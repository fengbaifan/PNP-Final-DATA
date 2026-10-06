"""Controlled S2 migration for Chapter 8 printed page 220 and its note.

The default run is read-only. OCR is preserved; visual corrections are logged
in S2 qualifiers. Use --apply only after reviewing the dry-run summary.
"""
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
BACKUP_SUFFIX = ".bak-s2-chp8-p220-20261001"

P219 = "chp-8:08_CHP-8_sec_ii:l86-98"
P220 = "chp-8:08_CHP-8_sec_ii:l100-110"
P221 = "chp-8:08_CHP-8_sec_ii:l112-124"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P219, P220, P221, NOTES}


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
candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
mention_fields, mention_rows = read_csv(MENTION_PATH)
statement_rows = read_jsonl(STATEMENT_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

expected_coverage = {
    P219: ("reviewed", "partial"),
    P220: ("queued", "pending"),
}
for segment_id, expected in expected_coverage.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-378":
    raise SystemExit("footnote coverage changed; review before proceeding")
if any(row["segment_id"] == P220 for row in mention_rows + statement_rows):
    raise SystemExit("p.220 rows already exist; inspect before rerunning")
if any(row["segment_id"] == NOTES and row["qualifiers"].get("source_line_start") == 379
       for row in statement_rows):
    raise SystemExit("p.220 footnote row already exists; inspect before rerunning")


def segment_text(segment_id: str) -> str:
    meta = segment_by_id[segment_id]
    return "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])


def lines_quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


new_candidates = [
    {
        "candidate_id": "cand-7692", "index_entry_id": "", "canonical_name": "Forlì Cathedral",
        "index_page_range": "", "suggested_type": "place", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "Cathedral whose cupola Carlo Cignani was painting in 1692; distinguish the building from the cupola work and from the city.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P220}#L102",
    },
    {
        "candidate_id": "cand-7693", "index_entry_id": "", "canonical_name": "Painters’ guilds of Florence, Bologna, and Venice (unidentified bodies in David’s proposal)",
        "index_page_range": "", "suggested_type": "institution", "status": "open",
        "index_source_file": "", "sub_entry": "",
        "detail": "The passage treats these as separate local guilds but supplies no formal names and does not say whether David’s proposed review was carried out. This collective candidate records the grouped reference without asserting one institution across the cities.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P220}#L107",
    },
]

candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_ids = set(candidate_by_id)
new_candidate_ids = [row["candidate_id"] for row in new_candidates]
if len(set(new_candidate_ids)) != len(new_candidate_ids) or candidate_ids.intersection(new_candidate_ids):
    raise SystemExit("duplicate candidate IDs")
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 7691:
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


# Map book names and independently meaningful referents to existing S1/S2 candidates.
mention(P220, "m-chp8-p220-cignani-close", "cand-0749", "Cignani", "Closes the p.219 sentence naming him as a possible alternative.")
mention(P220, "m-chp8-p220-giordano-spain", "cand-1172", "Giordano", "Luca Giordano; departure to Spain is reported by Haskell.")
mention(P220, "m-chp8-p220-spain", "cand-5120", "Spain", "Geographic destination in the p.220 account.")
mention(P220, "m-chp8-p220-committee-1", "cand-7641", "committee", "The Santa Maria Maggiore commission committee.")
mention(P220, "m-chp8-p220-cignani-again", "cand-0749", "Cignani", "Artist approached again in 1692.", occurrence=1)
mention(P220, "m-chp8-p220-cupola", "cand-0751", "cupola", "Cignani index subentry for the Forlì Cathedral cupola work.")
mention(P220, "m-chp8-p220-forli-cathedral", "cand-7692", "Forlì\nCathedral", "Building named as the site of Cignani’s cupola painting.")
mention(P220, "m-chp8-p220-correggio", "cand-0852", "Correggio", "Painter whose Parma cupola work Cignani intended to rival.")
mention(P220, "m-chp8-p220-parma", "cand-3417", "Parma", "Place associated with Correggio’s comparable cupola.")
mention(P220, "m-chp8-p220-ferri", "cand-1027", "Ciro Ferri", "Earlier artist whom the restricted space had disconcerted.")
mention(P220, "m-chp8-p220-committee-2", "cand-7641", "committee", "Committee hearing David’s proposed terms.", occurrence=1)
mention(P220, "m-chp8-p220-rome-1", "cand-4490", "Rome", "Location where David was when approached by a colleague.")
mention(P220, "m-chp8-p220-david-full", "cand-0911", "Ludovico David", "Swiss painter named in the index subentry for this Bergamo commission.")
mention(P220, "m-chp8-p220-fourteen-pictures", "cand-7686", "fourteen pictures", "The central-nave commission requirements.")
mention(P220, "m-chp8-p220-italy-1", "cand-3461", "Italy", "Painters were to be invited from across Italy.")
mention(P220, "m-chp8-p220-committee-3", "cand-7641", "committee", "Committee that found David’s review scheme too complicated.", occurrence=2)
mention(P220, "m-chp8-p220-david-indignant", "cand-0911", "David", "Surname refers to Ludovico David; he objects to the committee’s terms.", occurrence=1)
mention(P220, "m-chp8-p220-david-himself", "cand-0911", "David", "David included himself among the three painters in his proposed scheme.", occurrence=2)
mention(P220, "m-chp8-p220-subjects-required", "cand-7686", "the subjects required", "Subjects belong to the fourteen-picture commission; individual subjects are not identified.")
mention(P220, "m-chp8-p220-rome-2", "cand-4490", "Rome", "Proposed public exhibition location.", occurrence=1)
mention(P220, "m-chp8-p220-guilds", "cand-7693", "guilds", "Three separate local painters’ guilds are grouped in David’s proposal; none is formally named.")
mention(P220, "m-chp8-p220-florence", "cand-3397", "Florence", "City named as a proposed review venue.")
mention(P220, "m-chp8-p220-bologna", "cand-3398", "Bologna", "City named as a proposed review venue.")
mention(P220, "m-chp8-p220-venice", "cand-3401", "Venice", "City named as a proposed review venue.")
mention(P220, "m-chp8-p220-rome-3", "cand-4490", "Rome", "Excluded as a review venue because of possible favouritism.", occurrence=2)
mention(P220, "m-chp8-p220-committee-4", "cand-7641", "committee", "Committee that had already turned elsewhere.", occurrence=3)
mention(P220, "m-chp8-p220-franceschini", "cand-1069", "Marcantonio Franceschini", "Bolognese pupil of Cignani approached by the committee.")
mention(P220, "m-chp8-p220-giordano-franceschini-compare", "cand-1172", "Luca Giordano", "Comparator for Franceschini’s proposed price.")
mention(P220, "m-chp8-p220-naples", "cand-1722", "Naples", "Location from which the next artist was approached.")
mention(P220, "m-chp8-p220-giordano-pupil", "cand-1172", "Luca Giordano", "Melanconici is identified as Giordano’s pupil.", occurrence=1)
mention(P220, "m-chp8-p220-melanconici", "cand-1636", "Niccolò Melanconici", "Painter who agreed to the experimental Abraham painting.")
mention(P220, "m-chp8-p220-abraham", "cand-1637", "Abraham", "The subject/title of Melanconici’s experimental painting; no fuller title is supplied.")
mention(P220, "m-chp8-p220-picture", "cand-1637", "The picture", "Coreferential reference to Melanconici’s Abraham painting; arrival sentence continues on p.221.")


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, page=220, physical=22, speaker="Haskell",
                   text_layer="body", extras=None, original_quote=None):
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
        "original_quote": original_quote if original_quote is not None else lines_quote(segment_id, first_line, last_line),
        "origin": "book", "source_file": segment_by_id[segment_id]["source_file"],
    }


ocr = [
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 379,
     "ocr": "Bonari", "print": "Bottari", "basis": "CHP-8.pdf physical page 22; footnote 1."},
]

new_statements = [
    make_statement(
        "st-chp8-p220-cignani-satisfactory", P220, 101, 101, "cand-0749", "cand-1172",
        "alternative_assessment_continuation",
        "Haskell completes the preceding thought: Cignani might prove more satisfactory after all.",
        "This completes the open p.219 sentence; it is Haskell’s assessment, not Cignani’s acceptance of the commission.",
        ["cand-0749", "cand-1172"],
        extras={"continued_from_segment_id": P219, "continued_from_source_line": 98,
                "continued_from_statement_id": "st-chp8-p219-terms-stiffen-cignani-open",
                "continuation_status": "closed"},
        original_quote="prove more satisfactory after all.",
    ),
    make_statement(
        "st-chp8-p220-giordano-spain-cignani-reapproached", P220, 101, 101, "cand-7641", "cand-0749",
        "commissioner_reapproached_after_departure",
        "Haskell says Giordano went to Spain in 1692, ten years after the original approach, and the committee turned to Cignani again.",
        "The ten-year interval is Haskell’s account; this does not say Giordano completed the earlier commission or that Cignani accepted this later approach.",
        ["cand-1172", "cand-5120", "cand-7641", "cand-0749"],
        extras={"qualification_terms": ["finally", "in 1692", "ten years after", "once again"]},
    ),
    make_statement(
        "st-chp8-p220-cignani-forli-cupola", P220, 102, 103, "cand-0749", "cand-0751",
        "painting_cupola_with_comparative_aim",
        "Cignani was painting the cupola of Forlì Cathedral and intended the work to rival Correggio’s at Parma; the vast scale of his work made him reluctant to paint in a reduced space, whose limitations had earlier disconcerted Ciro Ferri.",
        "Haskell reports Cignani’s intention and reluctance; the precise identity and state of the Parma comparison work are not specified here.",
        ["cand-0749", "cand-0751", "cand-7692", "cand-0852", "cand-3417", "cand-1027"],
        extras={"qualification_terms": ["intended", "reluctant", "earlier", "a quarter of a century"]},
    ),
    make_statement(
        "st-chp8-p220-cignani-letter-perspective-objection", P220, 104, 105, "cand-0749", "cand-7686",
        "reported_letter_rejecting_pictorial_conditions",
        "In August 1692 Cignani wrote that the small available area, high bays, crowded scenes, and narrow church would prevent naturally scaled figures and make the required foreshortening impossible to correct.",
        "The wording is quoted by Haskell from a letter; the letter has not been independently consulted. The objection concerns the proposed commission and its architectural conditions.",
        ["cand-0749", "cand-7686"],
        speaker="Cignani as quoted by Haskell", text_layer="quoted correspondence",
        extras={"qualification_terms": ["would", "impossible", "August 1692"]},
    ),
    make_statement(
        "st-chp8-p220-david-offer", P220, 106, 106, "cand-0911", "cand-7686",
        "reported_commission_offer",
        "While in Rome, Ludovico David heard from an unnamed colleague and friend about the fourteen required pictures and offered to paint them all within two and a half years for 3,500 scudi, or to take a share of the scheme at a price to be agreed with other artists.",
        "Haskell reports David’s offer; the colleague and any agreement with other artists are unnamed, and no proposal document is independently consulted.",
        ["cand-0911", "cand-4490", "cand-7686"],
        extras={"qualification_terms": ["heard from", "offered", "within two and a half years", "or alternatively", "to be agreed"]},
    ),
    make_statement(
        "st-chp8-p220-committee-self-funded-alternative", P220, 106, 106, "cand-7641", "cand-7686",
        "proposed_self_funded_painter_allocation",
        "The committee instead proposed that painters across Italy each paint three pictures at their own expense, with no payment if the results proved unsatisfactory.",
        "This is a proposal by the committee; the passage does not say that the arrangement was implemented.",
        ["cand-7641", "cand-3461", "cand-7686"],
        extras={"qualification_terms": ["proposed instead", "entirely at their own expense", "if these proved unsatisfactory"]},
    ),
    make_statement(
        "st-chp8-p220-david-payment-terms-objection", P220, 106, 106, "cand-0911", "cand-7686",
        "reported_payment_practice_and_objection",
        "David said he had always received at least one quarter of the agreed price in advance and the remainder immediately on completion, and that accepting the committee’s arrangement would shame him and degrade his profession.",
        "The account and embedded quotation are mediated by Haskell; this is David’s stated position, not independent evidence of all his prior contracts.",
        ["cand-0911", "cand-7641", "cand-7686"],
        speaker="David as quoted by Haskell", text_layer="quoted correspondence",
        extras={"qualification_terms": ["always", "at least", "I could not", "shaming myself"]},
    ),
    make_statement(
        "st-chp8-p220-david-competitive-scheme", P220, 106, 107, "cand-0911", "cand-7686",
        "proposed_competitive_selection_scheme",
        "David proposed selecting three subjects, offering 500 scudi for each, and having himself and two other painters complete canvases within a year after one quarter was paid in advance; the canvases would be publicly exhibited in Rome for comparison and criticism.",
        "This is David’s elaborate counterproposal as reported by Haskell; the passage does not state that the trial canvases were produced or exhibited.",
        ["cand-0911", "cand-7686", "cand-4490"],
        speaker="David as reported by Haskell", text_layer="reported proposal",
        extras={"qualification_terms": ["proposed", "should be chosen", "should begin", "should submit"]},
    ),
    make_statement(
        "st-chp8-p220-david-guild-review", P220, 107, 107, "cand-0911", "cand-7686",
        "proposed_guild_review_and_final_award",
        "David proposed sending the canvases to painters’ guilds in Florence, Bologna, and Venice for review, excluding Rome because of possible favouritism; the painter judged best would receive the remainder of the commission.",
        "The guilds are not named and the proposed review is not reported as having occurred. Haskell’s description that these cities were thought the best after Rome is retained as the source’s characterization.",
        ["cand-0911", "cand-7686", "cand-7693", "cand-3397", "cand-3398", "cand-3401", "cand-4490"],
        speaker="David as quoted by Haskell", text_layer="quoted proposal",
        extras={"qualification_terms": ["should then be sent", "thought to be the best", "must be excluded", "risk of favouritism", "should then be given"]},
    ),
    make_statement(
        "st-chp8-p220-franceschini-approached", P220, 108, 109, "cand-7641", "cand-1069",
        "alternative_painter_terms_and_missed_timing",
        "Finding David’s scheme too complicated, the committee approached Cignani’s Bolognese pupil Marcantonio Franceschini; his terms were more expensive than Cignani’s or Giordano’s, and although he lowered them after hearing of a potential rival, the committee had already turned elsewhere.",
        "The potential rival is unnamed. Haskell does not specify Franceschini’s final reduced terms or identify the artist to whom the committee turned.",
        ["cand-7641", "cand-1069", "cand-0749", "cand-1172"],
        extras={"qualification_terms": ["pupil", "more expensive", "potential rival", "already turned elsewhere"]},
    ),
    make_statement(
        "st-chp8-p220-melanconici-abraham-open", P220, 110, 110, "cand-1636", "cand-1637",
        "experimental_painting_agreement_and_arrival",
        "In Naples, Luca Giordano’s pupil Niccolò Melanconici agreed to paint an Abraham at his own expense as an experiment; Haskell says the picture arrived quickly.",
        "The final clause continues on p.221 with the committee’s approval; keep arrival distinct from acceptance and from the later full commission.",
        ["cand-1722", "cand-1172", "cand-1636", "cand-1637"],
        extras={"continuation_to_segment_id": P221, "continuation_to_source_line": 113,
                "continuation_fragment": "The picture arrived quickly", "continuation_status": "open",
                "qualification_terms": ["agreed", "at his own expense", "as an experiment", "arrived quickly"]},
    ),
    make_statement(
        "st-chp8-p220-n1-bottari-citation", NOTES, 379, 379, None, "cand-5461",
        "footnote_citation",
        "Footnote 1 cites Bottari, volume III, pages 361–369.",
        "The citation is used as a locator for the source report; the cited pages were not independently consulted. The OCR reads Bonari; the printed page reads Bottari.",
        ["cand-5461"],
        speaker="Haskell", text_layer="bibliographic citation",
        extras={"ocr_corrections": ocr, "printed_page_locator": "p.220 n.1", "footnote_marker": 1,
                "citation_pages": "vol. III, pp. 361–369", "pdf_physical_page": 22},
    ),
]

# The citation is on the combined notes segment; its mention is anchored to the OCR surface.
mention(NOTES, "m-chp8-p220-bottari-note", "cand-5461", "Bonari", "OCR form; printed footnote reads Bottari, volume III, pages 361–369.", occurrence=0)

statement_by_id = {row["statement_id"]: row for row in statement_rows}
prior_id = "st-chp8-p219-terms-stiffen-cignani-open"
prior = statement_by_id.get(prior_id)
if not prior or prior["qualifiers"].get("continuation_status") != "open" or prior["qualifiers"].get("continuation_to_segment_id") != P220:
    raise SystemExit("p.219 open continuation changed; inspect before closing")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continued_to_segment_id": P220,
    "continued_to_source_line": 101,
    "continued_to_statement_id": "st-chp8-p220-cignani-satisfactory",
    "continuation_fragment": "prove more satisfactory after all",
})

new_statement_ids = [row["statement_id"] for row in new_statements]
all_statement_ids = {row["statement_id"] for row in statement_rows}
if len(set(new_statement_ids)) != len(new_statement_ids) or all_statement_ids.intersection(new_statement_ids):
    raise SystemExit("duplicate statement IDs")
for row in new_statements:
    q = row["qualifiers"]
    if q["source_line_start"] > q["source_line_end"] or not set(q["mentioned_candidate_ids"]) <= candidate_ids:
        raise SystemExit(f"invalid statement anchors or candidate references: {row['statement_id']}")
    if row["segment_id"] == P220 and not (100 <= q["source_line_start"] <= 110 and 100 <= q["source_line_end"] <= 110):
        raise SystemExit(f"statement outside p.220 segment: {row['statement_id']}")
    if row["segment_id"] == NOTES and q["source_line_start"] != 379:
        raise SystemExit(f"footnote statement outside p.220 n.1: {row['statement_id']}")

new_coverage = []
for segment in segments:
    sid = segment["segment_id"]
    row = dict(coverage_by_id[sid])
    if sid == P219:
        row.update({"disposition": "reviewed", "migration_status": "complete",
                    "source_line_ranges": "L87-98", "note": "p.219 body complete; final Cignani sentence closed by p.220 L101."})
    elif sid == P220:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L101-110", "note": "p.220 body semantically migrated; final Melanconici arrival clause continues at p.221 L113."})
    elif sid == NOTES:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L373-379",
                    "note": "Adds p.220 n.1 Bottari citation and links it to David’s reported proposal; citation pages not independently consulted. Later notes L380-461 remain pending."})
    new_coverage.append(row)
if {row["segment_id"] for row in new_coverage} != set(segment_by_id):
    raise SystemExit("coverage and source segment IDs do not match")

patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
preview = {
    "mode": "dry-run", "candidate_additions": len(new_candidates),
    "mention_additions": len(new_mentions), "statement_additions": len(new_statements),
    "candidate_refs_checked": True,
    "continuations": [
        {"statement_id": prior_id, "status": "closed", "to": P220, "line": 101},
        {"statement_id": "st-chp8-p220-melanconici-abraham-open", "status": "open", "to": P221, "line": 113},
    ],
    "coverage_updates": {
        P219: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L87-98"},
        P220: {"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L101-110"},
        NOTES: {"source_line_ranges": "L373-379", "migration_status": "partial"},
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
