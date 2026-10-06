"""Controlled S2 migration for Chapter 8 printed page 221 and notes 1-2."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
BACKUP_SUFFIX = ".bak-s2-chp8-p221-20261001"

P220 = "chp-8:08_CHP-8_sec_ii:l100-110"
P221 = "chp-8:08_CHP-8_sec_ii:l112-124"
P222 = "chp-8:08_CHP-8_sec_ii:l126-138"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P220, P221, P222, NOTES}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or not TARGET_IDS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()


def segment_text(segment_id: str) -> str:
    meta = segment_by_id[segment_id]
    text = "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    return text


for sid in TARGET_IDS:
    segment_text(sid)

candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
mention_fields, mention_rows = read_csv(MENTION_PATH)
statement_rows = read_jsonl(STATEMENT_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

expected_coverage = {
    P220: ("reviewed", "partial", "L101-110"),
    P221: ("queued", "pending", ""),
}
for sid, expected in expected_coverage.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-379":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P221 for row in mention_rows + statement_rows):
    raise SystemExit("p.221 rows already exist; inspect before rerunning")
if any(row["segment_id"] == NOTES and row["qualifiers"].get("source_line_start") in {380, 381}
       for row in statement_rows):
    raise SystemExit("p.221 footnote rows already exist; inspect before rerunning")

new_candidates = [
    {
        "candidate_id": "cand-7694", "index_entry_id": "", "canonical_name": "Unspecified great southern family attributed to Cardinal Tommaso Ruffo and Don Antonio Ruffo",
        "index_page_range": "", "suggested_type": "family", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says Cardinal Tommaso Ruffo and Don Antonio came from the same great southern family. The source does not specify lineage, branch, or a more precise kinship; this candidate preserves that group claim without asserting descent.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P221}#L115",
    },
    {
        "candidate_id": "cand-7695", "index_entry_id": "", "canonical_name": "Di alcuni quadri settecenteschi di Bergamo e provincia tornati da Roma (Angelo Pinetti, Fiera di Bergamo, 1920)",
        "index_page_range": "", "suggested_type": "archive", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Cited in p.221 n.1; title, periodical, and year are identified from this book's bibliography. The article itself was not consulted and no page locator is given.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTES}#L380",
    },
    {
        "candidate_id": "cand-7696", "index_entry_id": "", "canonical_name": "Dizionario di erudizione stòrico-ecclesiastica da San Pietro sino ai nostri giorni (G. Moroni; cited vol. 69)",
        "index_page_range": "", "suggested_type": "archive", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Cited at p.221 n.2, pp.215–216. The title and author initial are identified from this book's bibliography; edition/year and the cited entry were not independently checked.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTES}#L381",
    },
    {
        "candidate_id": "cand-7697", "index_entry_id": "", "canonical_name": "Ravenna (place named in Cardinal Tommaso Ruffo's career)",
        "index_page_range": "", "suggested_type": "place", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "City named as the site of Ruffo's vice-legate appointment and later legation; identity and historical offices remain at the source-report level pending global alignment.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P221}#L116",
    },
    {
        "candidate_id": "cand-7698", "index_entry_id": "", "canonical_name": "Trevi Fountain in Rome",
        "index_page_range": "", "suggested_type": "place", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Landmark used to locate the palace where Cardinal Tommaso Ruffo later lived; exact spatial relation is as stated by Haskell.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P221}#L120",
    },
    {
        "candidate_id": "cand-7699", "index_entry_id": "", "canonical_name": "Cibo family (seller of Cardinal Tommaso Ruffo's Rome palace)",
        "index_page_range": "", "suggested_type": "family", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Family from whom Haskell says Ruffo bought the palace opposite the Trevi Fountain; no individual seller or precise branch is named.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P221}#L120",
    },
    {
        "candidate_id": "cand-7700", "index_entry_id": "", "canonical_name": "Unidentified Cathedral adjoining Cardinal Tommaso Ruffo's Archbishop's Palace in Ferrara",
        "index_page_range": "", "suggested_type": "place", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "The source calls it only 'the Cathedral' while describing the Ferrara palace; retain the local referent without supplying a formal name.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P221}#L124",
    },
    {
        "candidate_id": "cand-7701", "index_entry_id": "", "canonical_name": "Statue of Vigilance commissioned by Cardinal Tommaso Ruffo for the Archbishop's Palace staircase",
        "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "A statue on the palace balustrade attributed in Haskell's account to sculptor Andrea Ferrerio; its description continues onto p.222.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P221}#L124",
    },
    {
        "candidate_id": "cand-7702", "index_entry_id": "", "canonical_name": "Additional unidentified pictures given to Niccolò Melanconici at Santa Maria Maggiore after the central-nave commission",
        "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says Melanconici was later given a certain number of other pictures to paint in the church. Their number, subjects, and completion are not stated; keep them distinct from the fourteen-picture central-nave commission.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P221}#L113",
    },
    {
        "candidate_id": "cand-7703", "index_entry_id": "", "canonical_name": "Completion of the Santa Maria Maggiore, Bergamo decoration by 1695",
        "index_page_range": "", "suggested_type": "event", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell dates completion of the decoration to 1695, roughly forty years after the original proposals; this is distinct from the 1653 programme candidate cand-7639.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P221}#L113",
    },
]

candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_ids = set(candidate_by_id)
new_candidate_ids = [row["candidate_id"] for row in new_candidates]
if len(set(new_candidate_ids)) != len(new_candidate_ids) or candidate_ids.intersection(new_candidate_ids):
    raise SystemExit("duplicate candidate IDs")
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 7693:
    raise SystemExit("candidate sequence changed; allocate IDs from current table")
candidate_ids.update(new_candidate_ids)
natural_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows if not row["index_entry_id"]}
for row in new_candidates:
    key = (row["canonical_name"], row["suggested_type"])
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {key}")
    natural_keys.add(key)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, mention_id, candidate_id, surface, note, occurrence=0):
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    text = segment_text(segment_id)
    starts = []
    at = 0
    while True:
        found = text.find(surface, at)
        if found < 0:
            break
        starts.append(found)
        at = found + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention surface not found: {segment_id} {surface!r} #{occurrence}; count={len(starts)}")
    start = starts[occurrence]
    key = (segment_id, str(start), str(start + len(surface)))
    if key in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == key for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
    })


mention(P221, "m-chp8-p221-melanconici-1", "cand-1636", "Melanconici", "The experimental painter whose approval closes p.220.", occurrence=0)
mention(P221, "m-chp8-p221-entire-commission", "cand-7686", "entire commission", "The fourteen-picture central-nave commission described on p.219.")
mention(P221, "m-chp8-p221-naples-oils", "cand-1722", "Naples", "Place where the oil paintings were painted.", occurrence=0)
mention(P221, "m-chp8-p221-bergamo-arrival", "cand-6208", "Bergamo", "Place where Melanconici arrived to undertake the frescoes.", occurrence=0)
mention(P221, "m-chp8-p221-committee-criticism", "cand-7641", "committee", "The committee's reported response to criticism.")
mention(P221, "m-chp8-p221-melanconici-2", "cand-1636", "Melanconici", "The artist later given additional pictures.", occurrence=1)
mention(P221, "m-chp8-p221-church", "cand-7627", "the church", "Santa Maria Maggiore in Bergamo.")
mention(P221, "m-chp8-p221-additional-pictures", "cand-7702", "other pictures", "Additional works beyond the central-nave commission; number and subjects unspecified.")
mention(P221, "m-chp8-p221-david-goliath", "cand-1638", "David with the Head of Goliath", "The painting beneath which Melanconici was allowed to sign.")
mention(P221, "m-chp8-p221-completion-date", "cand-7703", "1695", "Date by which Haskell says the church decoration was complete.")
mention(P221, "m-chp8-p221-governors", "cand-7640", "Governors of S. Maria\nMaggiore", "The governing body whose commissioning activity Haskell assesses.")
mention(P221, "m-chp8-p221-smm-place", "cand-7627", "S. Maria\nMaggiore", "Santa Maria Maggiore in Bergamo; place nested in the governors' name.")
mention(P221, "m-chp8-p221-italy", "cand-3461", "Italy", "Artists were drawn from schools across Italy.")
mention(P221, "m-chp8-p221-ruffo-name-ocr", "cand-2304", "Cardinal Tommaso Russo", "OCR spelling; the page image reads Cardinal Tommaso Ruffo.")
mention(P221, "m-chp8-p221-naples-birth", "cand-1722", "Naples", "Birthplace reported for Cardinal Tommaso Ruffo.", occurrence=1)
mention(P221, "m-chp8-p221-southern-family", "cand-7694", "same great southern family", "Family group asserted by Haskell; no specific lineage is named.")
mention(P221, "m-chp8-p221-don-antonio", "cand-2297", "Don\nAntonio", "Don Antonio Ruffo, with surname supplied by the book's local context and index.")
mention(P221, "m-chp8-p221-messina", "cand-1655", "Messina", "Place linked to Don Antonio in Haskell's family statement.")
mention(P221, "m-chp8-p221-church-institution", "cand-3400", "the Church", "Institutional reference to the Catholic Church.")
mention(P221, "m-chp8-p221-innocent-xii", "cand-1929", "Pope Innocent XII", "Pope who appointed Ruffo Vice-Legate in Ravenna according to Haskell.")
mention(P221, "m-chp8-p221-ravenna-1", "cand-7697", "Ravenna", "Place of the vice-legate appointment.", occurrence=0)
mention(P221, "m-chp8-p221-malta", "cand-6938", "Malta", "Place of Ruffo's reported inquisitorial service.")
mention(P221, "m-chp8-p221-tuscany", "cand-6232", "Tuscany", "Place of Ruffo's reported nunciature.")
mention(P221, "m-chp8-p221-ravenna-2", "cand-7697", "Ravenna", "Place to which Ruffo later returned as Legate.", occurrence=1)
mention(P221, "m-chp8-p221-ferrara-career", "cand-1017", "Ferrara", "City where Ruffo served and assembled his collection.", occurrence=0)
mention(P221, "m-chp8-p221-bologna-career", "cand-3398", "Bologna", "Place of Ruffo's six-year exception from his Ferrara residence.")
mention(P221, "m-chp8-p221-rome-career", "cand-4490", "Rome", "City where Ruffo later lived and died.")
mention(P221, "m-chp8-p221-cibo-palace", "cand-0746", "a palace", "The Cibo palace index candidate, identified here by its location opposite the Trevi Fountain.")
mention(P221, "m-chp8-p221-trevi", "cand-7698", "Trevi\nFountain", "Landmark opposite Ruffo's Rome residence; the printed line break is retained in the source span.")
mention(P221, "m-chp8-p221-cibo-family", "cand-7699", "Cibo family", "Family from whom Ruffo is said to have bought the Rome palace.")
mention(P221, "m-chp8-p221-ruffo-gallery-1", "cand-2304", "Ruffo", "Cardinal Tommaso Ruffo as patron and collector.", occurrence=0)
mention(P221, "m-chp8-p221-venice", "cand-3401", "Venice", "Notable exception to Ruffo's commissions among leading Italian artists.")
mention(P221, "m-chp8-p221-gallery", "cand-2307", "his gallery", "Cardinal Ruffo's collection in Haskell's account.")
mention(P221, "m-chp8-p221-ferrara-collection", "cand-1017", "Ferrara", "City where Ruffo assembled the collection.", occurrence=1)
mention(P221, "m-chp8-p221-palace", "cand-2306", "Archbishop’s Palace", "Ruffo's palace in Ferrara, distinguished from his Rome residence.")
mention(P221, "m-chp8-p221-mattei", "cand-1580", "Tommaso Mattei", "Roman architect named as builder of the Archbishop's Palace.")
mention(P221, "m-chp8-p221-cathedral", "cand-7700", "the Cathedral", "Unidentified cathedral adjoining the Archbishop's Palace in Ferrara.")
mention(P221, "m-chp8-p221-statue", "cand-7701", "statue of Vigilance", "Sculptural work on the palace staircase; its account continues on p.222.")
mention(P221, "m-chp8-p221-ruffo-statue", "cand-2304", "Ruffo", "Cardinal Ruffo as commissioner of the statue.", occurrence=1)
mention(P221, "m-chp8-p221-ferrerio", "cand-1024", "Andrea Ferrerio", "Sculptor identified in the index entry for Vigilance.")

mention(NOTES, "m-chp8-p221-paolo", "cand-0681", "S. Paolo d’Argan", "Church/building in Bergamo; the existing index candidate identifies it on p.221 n.1.")
mention(NOTES, "m-chp8-p221-note1-bergamo", "cand-6208", "Bergamo", "City location of S. Paolo d’Argan in note 1.", occurrence=1)
mention(NOTES, "m-chp8-p221-crespi", "cand-0871", "G. M. Crespi", "Painter named in note 1; candidate is the indexed Giuseppe Maria Crespi.")
mention(NOTES, "m-chp8-p221-note1-bologna", "cand-3398", "Bologna", "City where Crespi worked for the church.")
mention(NOTES, "m-chp8-p221-lazzarini", "cand-1374", "Lazzarini", "Indexed Gregorio Lazzarini; note does not give his forename.")
mention(NOTES, "m-chp8-p221-ricci", "cand-2182", "Ricci", "The p.221n index subentry connects this name to Sebastiano Ricci's work for S. Paolo d'Argan.")
mention(NOTES, "m-chp8-p221-balestra", "cand-0168", "Balestra", "Indexed as Antonio Balestra on p.221 n.")
mention(NOTES, "m-chp8-p221-note1-venice", "cand-3401", "Venice", "City where the named painters worked for the church.")
mention(NOTES, "m-chp8-p221-pinetti-author", "cand-7656", "Pinetti", "Surname of the author credited at the end of p.221 note 1; full author-year citation is separately anchored to the article candidate.", occurrence=1)
mention(NOTES, "m-chp8-p221-pinetti-1920", "cand-7695", "Angelo Pinetti, 1920", "Full author-year citation for the 1920 article identified from the book bibliography; the author surname is nested as a separate mention.")
mention(NOTES, "m-chp8-p221-moroni-author", "cand-5954", "Moroni", "Surname-only author reference; do not align with painter Giovanni Battista Moroni.")
mention(NOTES, "m-chp8-p221-moroni-work", "cand-7696", "Moroni, Vol. 69, pp. 215-16", "Short citation linked to the dictionary entry identified from the book bibliography.")


def lines_quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


ocr = [
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 115,
     "ocr": "Russo", "print": "Ruffo", "basis": "CHP-8.pdf physical page 23."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 115,
     "ocr": "bom", "print": "born", "basis": "CHP-8.pdf physical page 23."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 124,
     "ocr": "1710'by", "print": "1710 by", "basis": "CHP-8.pdf physical page 23."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 124,
     "ocr": "the' piano", "print": "the piano", "basis": "CHP-8.pdf physical page 23."},
]


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, page=221, physical=23, speaker="Haskell",
                   text_layer="body", extras=None):
    qualifiers = {
        "source_line_start": first_line, "source_line_end": last_line,
        "printed_page": page, "pdf_physical_page": physical,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": lines_quote(segment_id, first_line, last_line),
        "origin": "book", "source_file": segment_by_id[segment_id]["source_file"],
    }


new_statements = [
    make_statement(
        "st-chp8-p221-melanconici-commission", P221, 113, 113, "cand-7641", "cand-7686",
        "experimental_painting_approved_and_commission_awarded",
        "The experimental picture met with approval, and the committee arranged for Melanconici to receive the entire fourteen-picture commission for 4,000 ducats, including travel, board, and lodging expenses.",
        "This continues the p.220 statement that the picture arrived quickly. Approval and the subsequent award are separate; the quoted committee evaluation is mediated by Haskell.",
        ["cand-1636", "cand-1637", "cand-7641", "cand-7686"],
        extras={"continued_from_segment_id": P220, "continued_from_source_line": 110,
                "continued_from_statement_id": "st-chp8-p220-melanconici-abraham-open",
                "continuation_status": "closed", "continuation_fragment": "and met with approval"},
    ),
    make_statement(
        "st-chp8-p221-melanconici-oils-and-frescoes", P221, 113, 113, "cand-1636", "cand-7686",
        "painting_locations_and_arrival_for_frescoes",
        "The oil paintings were painted in Naples; in June 1693 Melanconici arrived in Bergamo to undertake the frescoes.",
        "Haskell distinguishes the oil work from the frescoes; the passage does not give exact completion dates for each painting.",
        ["cand-1636", "cand-1722", "cand-6208", "cand-7686"],
        extras={"qualification_terms": ["oils", "in Naples", "June 1693", "frescoes"]},
    ),
    make_statement(
        "st-chp8-p221-melanconici-results-and-additional-pictures", P221, 113, 113, "cand-7641", "cand-1636",
        "reported_controversy_additional_pictures_and_signature",
        "Haskell says the results were controversial and the committee called criticism unavoidable; because a willing artist at a reasonable fee was rare, Melanconici received a certain number of additional pictures to paint in the church and permission to add a very large signature beneath David with the Head of Goliath.",
        "The committee's words and Haskell's evaluation are kept distinct. The number and subjects of the additional paintings are unspecified; the signature is described as visible to the naked eye.",
        ["cand-7641", "cand-1636", "cand-7627", "cand-7702", "cand-1638"],
        extras={"qualification_terms": ["controversial", "as the committee pointed out", "a certain number", "if slightly academic"]},
    ),
    make_statement(
        "st-chp8-p221-decoration-completed-1695", P221, 113, 113, "cand-7703", "cand-7639",
        "decoration_completion_date",
        "Haskell says the church decoration was complete by 1695, roughly forty years after the original proposals.",
        "The approximate interval and completion date are Haskell's account; the 1695 completion event is distinct from the 1653 programme record.",
        ["cand-7703", "cand-7639", "cand-7627"],
        extras={"qualification_terms": ["by 1695", "some forty years"]},
    ),
    make_statement(
        "st-chp8-p221-governors-ambition", P221, 114, 115, "cand-7640", "cand-7627",
        "historical_assessment_of_commissioning_campaign",
        "Haskell calls the Governors' long and complicated effort to commission artists from all Italian schools for Santa Maria Maggiore one of the most ambitious and best-documented such ventures of the seventeenth and eighteenth centuries.",
        "The superlative is Haskell's assessment, not an independently measured comparison.",
        ["cand-7640", "cand-7627", "cand-3461"],
        extras={"qualification_terms": ["by far the most ambitious", "best documented"]},
    ),
    make_statement(
        "st-chp8-p221-provincial-patronage-context", P221, 115, 115, None, "cand-2304",
        "provincial_patron_as_example",
        "Haskell says no private patron had the Governors' resources or available time, and that men in other small towns helped break provincial cultural isolation; he presents Cardinal Tommaso Ruffo as one example.",
        "This is Haskell's framing of Ruffo as an example; it does not assert a specific institutional role or quantify the broader trend.",
        ["cand-7640", "cand-2304"],
        extras={"qualification_terms": ["no private patron", "on however modest a scale", "one such"]},
    ),
    make_statement(
        "st-chp8-p221-ruffo-origin-and-family", P221, 115, 116, "cand-2304", "cand-7694",
        "reported_birth_and_shared_family",
        "Haskell reports that Cardinal Tommaso Ruffo was born in Naples in 1663 and came from the same great southern family as Don Antonio, whom the passage places in Messina.",
        "The family identity is not named beyond this description, and no parent-child or other specific kinship is asserted. The OCR spelling Russo and bom are corrected against the page image.",
        ["cand-2304", "cand-1722", "cand-7694", "cand-2297", "cand-1655"],
        extras={"ocr_corrections": ocr[:2], "qualification_terms": ["same great southern family"]},
    ),
    make_statement(
        "st-chp8-p221-ruffo-early-ecclesiastical-career", P221, 116, 118, "cand-2304", "cand-1929",
        "reported_ecclesiastical_offices_and_service",
        "Haskell reports that Ruffo entered the Church, was made Vice-Legate in Ravenna by Pope Innocent XII in 1692, served as Inquisitor in Malta and Nunzio in Tuscany, and then became maestro de camera to the Pope.",
        "The offices and dates are reported in Haskell's narrative; the unnamed Pope after Innocent XII is not identified.",
        ["cand-2304", "cand-3400", "cand-7697", "cand-1929", "cand-6938", "cand-6232"],
        extras={"qualification_terms": ["in 1692", "He then served", "before becoming"]},
    ),
    make_statement(
        "st-chp8-p221-ruffo-cardinal-and-legate-appointments", P221, 118, 120, "cand-2304", "cand-1017",
        "reported_cardinalate_and_legate_archbishop_tenure",
        "Ruffo became a Cardinal in 1706, returned briefly to Ravenna as Legate, then went to Ferrara; Haskell says he was Legate there from 1710 and Archbishop from 1717 until 1738, apart from six years in Bologna from 1721 to 1727.",
        "The source reports office dates and a temporary Bologna interval; it does not supply a separate end date for the Ferrara legateship.",
        ["cand-2304", "cand-7697", "cand-1017", "cand-3398"],
        extras={"qualification_terms": ["for a short time", "from 1710", "from 1717", "except for six years"]},
    ),
    make_statement(
        "st-chp8-p221-ruffo-rome-palace-and-death", P221, 120, 121, "cand-2304", "cand-0746",
        "reported_residence_purchase_and_death",
        "Haskell says Ruffo later lived in Rome in a palace opposite the Trevi Fountain that he bought from the Cibo family, and died there in 1753 aged 90.",
        "The palace is indexed as the Cibo palace; the seller is not individually named. Age and date remain as reported by Haskell.",
        ["cand-2304", "cand-4490", "cand-0746", "cand-7698", "cand-7699"],
        extras={"qualification_terms": ["as an old man", "which he bought", "aged 90", "in 1753"]},
    ),
    make_statement(
        "st-chp8-p221-ruffo-gallery-taste", P221, 122, 123, "cand-2304", "cand-2307",
        "gallery_scope_taste_and_assembly",
        "Haskell says Ruffo had opportunities to seek works by leading Italian artists except those in Venice; the varied gallery contents testify, in Haskell's view, to broad tastes and enthusiasm, and he assembled the collection in Ferrara.",
        "The characterization of the collection as evidence of taste and enthusiasm is Haskell's interpretation; it does not establish a complete inventory.",
        ["cand-2304", "cand-3401", "cand-2307", "cand-1017"],
        extras={"qualification_terms": ["most of the leading Italian artists", "notable exception", "testify", "width of his tastes"]},
    ),
    make_statement(
        "st-chp8-p221-ruffo-commissioning-in-resident-towns", P221, 122, 123, "cand-2304", "cand-2307",
        "reported_commissions_across_residences",
        "Haskell says Ruffo commissioned paintings in most of the towns where he resided.",
        "This is Haskell's summarized account; the passage does not enumerate the towns or individual commissions.",
        ["cand-2304", "cand-1017"],
        extras={"qualification_terms": ["we know", "would commission", "most of the towns"]},
    ),
    make_statement(
        "st-chp8-p221-archbishop-palace-and-vigilance-statue-open", P221, 123, 124, "cand-2304", "cand-7701",
        "palace_gallery_and_commissioned_staircase_statue",
        "Haskell places Ruffo's gallery in a new Archbishop's Palace built for him in 1710 by the Roman architect Tommaso Mattei; the palace adjoined the Cathedral, and its staircase included a statue of Vigilance commissioned by Ruffo from Andrea Ferrerio.",
        "The Cathedral is unnamed in the text. The final phrase about Ferrerio continues onto p.222, so the artist's further description is not yet complete. Page-image corrections remove OCR artifacts in the printed date and piano nobile passage.",
        ["cand-2304", "cand-2307", "cand-2306", "cand-1580", "cand-7700", "cand-7701", "cand-1024"],
        extras={"continuation_to_segment_id": P222, "continuation_to_source_line": 127,
                "continuation_fragment": "from the sculptor Andrea Ferrerio,",
                "continuation_status": "open", "ocr_corrections": ocr[2:]},
    ),
    make_statement(
        "st-chp8-p221-n1-s-paolo-painters", NOTES, 380, 380, "cand-0681", None,
        "reported_painter_employment_at_bergamo_church",
        "Haskell's note says S. Paolo d'Argan in Bergamo employed painters from several Italian towns in the early eighteenth century, naming G. M. Crespi in Bologna and Lazzarini, Ricci, Balestra and others in Venice, as well as local Bergamo artists.",
        "This is a footnote report attributed to Angelo Pinetti's 1920 article, identified by title from the book bibliography but not independently read. The unnamed artists and the exact works are not supplied.",
        ["cand-0681", "cand-6208", "cand-0871", "cand-3398", "cand-1374", "cand-2182", "cand-0168", "cand-3401", "cand-7656", "cand-7695"],
        text_layer="footnote report", speaker="Haskell citing Pinetti",
        extras={"footnote_marker": 1, "printed_page_locator": "p.221 n.1",
                "footnote_citation_statement_ids": ["st-chp8-p221-n1-pinetti-citation"],
                "qualification_terms": ["early in the eighteenth century", "among those", "and others", "some local artists"]},
    ),
    make_statement(
        "st-chp8-p221-n1-pinetti-citation", NOTES, 380, 380, None, "cand-7695",
        "footnote_citation",
        "Footnote 1 credits Angelo Pinetti's 1920 article, identified in the bibliography as Di alcuni quadri settecenteschi di Bergamo e provincia tornati da Roma in Fiera di Bergamo.",
        "The article is cited as the report's source but was not independently consulted; no page number is supplied in the note.",
        ["cand-7656", "cand-7695"],
        text_layer="bibliographic citation", speaker="Haskell",
        extras={"footnote_marker": 1, "printed_page_locator": "p.221 n.1",
                "bibliography_locator": "21_CHP-21Bibliography.md:L963-965",
                "citation_year": "1920", "citation_pages": "not supplied"},
    ),
    make_statement(
        "st-chp8-p221-n2-moroni-citation", NOTES, 381, 381, None, "cand-7696",
        "footnote_citation",
        "Footnote 2 directs readers to Moroni, volume 69, pages 215–216, for the outline of Ruffo's career.",
        "The cited volume and pages were not independently consulted. The book bibliography identifies Moroni's dictionary title and initial G.; this does not verify the biographical claims in Haskell's main text.",
        ["cand-5954", "cand-7696", "cand-2304"],
        text_layer="bibliographic citation", speaker="Haskell",
        extras={"footnote_marker": 2, "printed_page_locator": "p.221 n.2",
                "bibliography_locator": "21_CHP-21Bibliography.md:L847",
                "citation_pages": "vol. 69, pp. 215-216",
                "linked_body_statement_ids": ["st-chp8-p221-ruffo-origin-and-family", "st-chp8-p221-ruffo-early-ecclesiastical-career", "st-chp8-p221-ruffo-cardinal-and-legate-appointments", "st-chp8-p221-ruffo-rome-palace-and-death"]},
    ),
]

# Update the p.220 open sentence only after reading the printed continuation.
statement_by_id = {row["statement_id"]: row for row in statement_rows}
prior_id = "st-chp8-p220-melanconici-abraham-open"
prior = statement_by_id.get(prior_id)
if not prior or prior["qualifiers"].get("continuation_status") != "open" or prior["qualifiers"].get("continuation_to_segment_id") != P221:
    raise SystemExit("p.220 open continuation changed; inspect before closing")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continued_to_segment_id": P221,
    "continued_to_source_line": 113,
    "continued_to_statement_id": "st-chp8-p221-melanconici-commission",
    "continuation_fragment": "and met with approval",
    "qualification": "Arrival at p.220 is followed by approval on p.221; approval and the subsequent award are separate, and the committee's evaluation is mediated by Haskell.",
    "claim": "In Naples, Luca Giordano's pupil Niccolò Melanconici agreed to paint an Abraham at his own expense as an experiment; Haskell says the picture arrived quickly and met with approval.",
})

new_statement_ids = [row["statement_id"] for row in new_statements]
all_statement_ids = {row["statement_id"] for row in statement_rows}
if len(set(new_statement_ids)) != len(new_statement_ids) or all_statement_ids.intersection(new_statement_ids):
    raise SystemExit("duplicate statement IDs")
for row in new_statements:
    q = row["qualifiers"]
    if q["source_line_start"] > q["source_line_end"] or not set(q["mentioned_candidate_ids"]) <= candidate_ids:
        raise SystemExit(f"invalid statement anchors or candidate references: {row['statement_id']}")
    if row["segment_id"] == P221 and not (113 <= q["source_line_start"] <= 124 and 113 <= q["source_line_end"] <= 124):
        raise SystemExit(f"statement outside p.221 body: {row['statement_id']}")
    if row["segment_id"] == NOTES and q["source_line_start"] not in {380, 381}:
        raise SystemExit(f"statement outside p.221 notes: {row['statement_id']}")

new_coverage = []
for segment in segments:
    sid = segment["segment_id"]
    row = dict(coverage_by_id[sid])
    if sid == P220:
        row.update({"disposition": "reviewed", "migration_status": "complete",
                    "source_line_ranges": "L101-110", "note": "p.220 body complete; the Melanconici picture's arrival clause closes with approval at p.221 L113."})
    elif sid == P221:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L113-124", "note": "p.221 body read against CHP-8.pdf physical page 23. The Ferrerio statue sentence continues at p.222 L127."})
    elif sid == NOTES:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L373-381", "note": "Adds p.221 n.1-2, their factual/citation records, and links; Pinetti 1920 and Moroni vol.69 pages are bibliography-located but not independently read. Notes L382-461 remain pending."})
    new_coverage.append(row)
if {row["segment_id"] for row in new_coverage} != set(segment_by_id):
    raise SystemExit("coverage and source segment IDs do not match")

patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
preview = {
    "mode": "dry-run", "candidate_additions": len(new_candidates),
    "mention_additions": len(new_mentions), "statement_additions": len(new_statements),
    "continuations": [
        {"statement_id": prior_id, "status": "closed", "to": P221, "line": 113},
        {"statement_id": "st-chp8-p221-archbishop-palace-and-vigilance-statue-open", "status": "open", "to": P222, "line": 127},
    ],
    "coverage_updates": {
        P220: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L101-110"},
        P221: {"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L113-124"},
        NOTES: {"source_line_ranges": "L373-381", "migration_status": "partial"},
    },
    "ocr_corrections": [f"{item['ocr']} -> {item['print']}" for item in ocr],
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (CANDIDATE_PATH, MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
patched_statements.extend(new_statements)
write_csv_atomic(CANDIDATE_PATH, candidate_fields, candidate_rows)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
write_jsonl_atomic(STATEMENT_PATH, patched_statements)
write_csv_atomic(COVERAGE_PATH, coverage_fields, new_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
