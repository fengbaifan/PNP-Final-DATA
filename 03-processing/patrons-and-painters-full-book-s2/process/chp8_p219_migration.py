"""Controlled S2 migration for Chapter 8 printed page 219 and its footnotes.

Default invocation is read-only. Source OCR is preserved; visual corrections
are recorded in qualifiers. Apply only after reviewing the dry-run summary.
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
BACKUP_SUFFIX = ".bak-s2-chp8-p219-20261001"

P217 = "chp-8:08_CHP-8_sec_ii:l69-76"
P218 = "chp-8:08_CHP-8_sec_ii:l78-84"
P219 = "chp-8:08_CHP-8_sec_ii:l86-98"
P220 = "chp-8:08_CHP-8_sec_ii:l100-110"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P217, P218, P219, P220, NOTES}


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
if len(segment_by_id) != len(segments):
    raise SystemExit("segments.jsonl contains duplicate segment IDs")
if not TARGET_IDS <= set(segment_by_id):
    raise SystemExit("one or more source segments are missing")

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
    P217: ("reviewed", "partial"),
    P218: ("reviewed", "partial"),
    P219: ("queued", "pending"),
}
for segment_id, expected in expected_coverage.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-376":
    raise SystemExit("notes coverage changed since p.215–218 processing; inspect before proceeding")
if any(row["segment_id"] == P219 for row in mention_rows + statement_rows):
    raise SystemExit("p.219 rows already exist; inspect before rerunning")
if any(row["segment_id"] == NOTES and row["qualifiers"].get("source_line_start", 0) >= 377
       for row in statement_rows):
    raise SystemExit("p.219 footnote rows already exist; inspect before rerunning")


def segment_text(segment_id: str) -> str:
    meta = segment_by_id[segment_id]
    lines = source_lines
    return "\n".join(lines[meta["line_start"] - 1:meta["line_end"]])


def lines_quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


new_candidates = [
    ["cand-7678", "", "The Sacrifice of Noah (competition painting for Santa Maria Maggiore, Bergamo)", "", "work", "open", "", "",
     "A specific painting identified by its subject and the 1677 competition context; it replaces an unnamed unsuccessful Ciro Ferri effort above the door of the Colleoni chapel. Distinct from Poussin's separate Sacrifice of Noah candidate cand-5761.",
     "", "body-mention", f"{P219}#L88"],
    ["cand-7679", "", "1677 competition for The Sacrifice of Noah at Santa Maria Maggiore, Bergamo", "", "event", "open", "", "",
     "Haskell reports that the committee organized the competition after a delay of some years; no competition document is identified.",
     "", "body-mention", f"{P219}#L88"],
    ["cand-7680", "", "Pietro Negri painting commemorating the cessation of the 1630 plague at Scuola di San Rocco", "", "work", "open", "", "",
     "An unnamed picture reported by Haskell as painted by Negri for Scuola di San Rocco; no title, date of execution, or current location is supplied.",
     "", "body-mention", f"{P219}#L89"],
    ["cand-7681", "", "Plague of 1630 referenced in Pietro Negri's Scuola di San Rocco picture", "", "event", "open", "", "",
     "The passage identifies the outbreak only by the phrase 'plague of 1630' and by the picture's commemorative context; exact geographic scope is not supplied.",
     "", "body-mention", f"{P219}#L89"],
    ["cand-7682", "", "Cavaliere Perugino (Turinese painter; identity unresolved)", "", "person", "open", "", "",
     "The source gives only the title/name Cavaliere Perugino and the descriptor Turinese. Do not merge with Pietro Perugino (cand-1883) without later identity evidence.",
     "", "body-mention", f"{P219}#L89"],
    ["cand-7683", "", "King of Savoy (patron referent in Haskell's 1677 account; identity unresolved)", "", "person", "open", "", "",
     "Title-only referent described as the Cavaliere Perugino's patron. Keep distinct from the separate title-only candidate cand-3586 until S3 resolves identity.",
     "", "body-mention", f"{P219}#L89"],
    ["cand-7684", "", "Hymn of Liberation after the Crossing (reported image subject)", "", "term", "open", "", "",
     "Alternative subject identification reported by Haskell from an anonymous 1947 Bergomum article; neither the article nor the painting has been independently checked.",
     "", "body-mention", f"{NOTES}#L377"],
    ["cand-7685", "", "Central nave of Santa Maria Maggiore, Bergamo", "", "place", "open", "", "",
     "Interior space named as the location of fourteen further paintings; distinguish it from the northern transept and its earlier decoration scheme.",
     "", "body-mention", f"{P219}#L94"],
    ["cand-7686", "", "Fourteen paintings planned for the central nave of Santa Maria Maggiore, Bergamo", "", "work", "open", "", "",
     "A later central-nave requirement, distinct from the sixteen-picture northern-transept/door scheme cand-7663. Giordano's proposed ten frescoes and four oils match this count; the source does not say they were executed.",
     "", "body-mention", f"{P219}#L94"],
    ["cand-7687", "", "Untitled modello submitted by Carlo Ceresa for the Santa Maria Maggiore central-nave project (1682)", "", "work", "open", "", "",
     "The subject and later fate are not stated. Haskell reports that the committee called it 'very beautiful and precious' while presenting that praise as flattery masking higher aims.",
     "", "body-mention", f"{P219}#L96"],
    ["cand-7688", "", "Contract reported for Luca Giordano's ten-fresco and four-oil Santa Maria Maggiore project", "", "archive", "open", "", "",
     "Haskell reports that a contract was signed and ignored by Giordano; the document, date, terms as written, and survival are not independently established.",
     "", "body-mention", f"{P219}#L96"],
    ["cand-7689", "", "Anonymous article in Bergomum (1947), pp. 60–61; title unreported", "", "archive", "open", "", "",
     "Cited in Haskell's note 1 for an alternative identification of the subject represented in the Giordano painting; the article was not independently consulted.",
     "", "body-mention", f"{NOTES}#L377"],
    ["cand-7690", "", "Tassi, volume I, page 265 (cited at p.219 n.2; work identity unresolved)", "", "archive", "open", "", "",
     "A short-form citation only. The cited work and page have not been identified or independently consulted; do not infer that it documents the reported contract.",
     "", "body-mention", f"{NOTES}#L378"],
    ["cand-7691", "", "Como (place named as Cristoforo Tencala's origin)", "", "place", "open", "", "",
     "The passage names Como as Tencala's point of origin; no further biographical or institutional claim is made.",
     "", "body-mention", f"{P219}#L94"],
]

candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_ids = set(candidate_by_id)
new_candidate_ids = [row[0] for row in new_candidates]
if len(set(new_candidate_ids)) != len(new_candidate_ids) or candidate_ids.intersection(new_candidate_ids):
    raise SystemExit("duplicate candidate IDs")
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 7677:
    raise SystemExit("candidate sequence changed; allocate IDs from the current table")
candidate_ids.update(new_candidate_ids)
candidate_natural_keys = {
    (row["canonical_name"], row["suggested_type"])
    for row in candidate_rows
    if not row["index_entry_id"]
}
for row in new_candidates:
    key = (row[2], row[4])
    if key in candidate_natural_keys:
        raise SystemExit(f"candidate natural-key collision: {key}")
    candidate_natural_keys.add(key)

candidate_7668 = candidate_by_id.get("cand-7668")
expected_7668 = "The intended subject of the large picture over a door in Ferri's commission. This passage does not unambiguously identify which contracted oil painting was completed."
if (not candidate_7668 or candidate_7668["detail"] != ""
        or candidate_7668["exclude_reason"] != expected_7668):
    raise SystemExit("cand-7668 changed; review before updating its p.219 context")
patched_7668 = dict(candidate_7668)
patched_7668["detail"] = (
    "Initially planned as the subject of Ciro Ferri's large overdoor picture. At p.219 Haskell calls it "
    "the third large oil painting and says the subject was entrusted to Luca Giordano in 1682; do not "
    "infer the external identity, completion history, or current location of a surviving canvas. "
    "Haskell's note 1 reports an alternative represented subject (cand-7684) from an unconsulted article."
)
patched_7668["exclude_reason"] = ""

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_mention_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


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
    if key in existing_mention_spans or any(
        (row["segment_id"], row["start_char"], row["end_char"]) == key for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
    })


# The source uses hard line breaks inside several proper names; preserve those
# exact spans instead of normalizing the OCR text in place.
mention(P219, "m-chp8-p219-zanchi-picture", "cand-7670", "coloured picture", "Continuation of Zanchi's painting description from p.218.")
mention(P219, "m-chp8-p219-noah-work", "cand-7678", "Sacrifice of Noah", "Specific Santa Maria Maggiore competition painting; distinct from Poussin's work.")
mention(P219, "m-chp8-p219-noah", "cand-5767", "Noah", "Biblical figure named as the subject of the competition painting.")
mention(P219, "m-chp8-p219-ferri-1", "cand-1027", "Ciro Ferri", "Painter whose unsuccessful overdoor effort was to be replaced.", occurrence=0)
mention(P219, "m-chp8-p219-colleoni-door", "cand-7673", "the door", "The location phrase for the unnamed Ferri effort; retain its identity as unspecified.")
mention(P219, "m-chp8-p219-colleoni-chapel", "cand-7671", "Colleoni chapel", "Chapel named as the adjoining landmark.")
mention(P219, "m-chp8-p219-committee-1", "cand-7641", "committee", "Committee organizing the competition.", occurrence=0)
mention(P219, "m-chp8-p219-competition", "cand-7679", "competition", "The 1677 competition for the Sacrifice of Noah.")
mention(P219, "m-chp8-p219-cervelli-1", "cand-0638", "Federico Cervelli", "First named competitor; index candidate specifically covers p.219.")
mention(P219, "m-chp8-p219-milan", "cand-3418", "Milan", "City used in the source's identification of Cervelli.")
mention(P219, "m-chp8-p219-negri", "cand-1731", "Pietro Negri", "Named competitor; identity remains for global S3 alignment.")
mention(P219, "m-chp8-p219-venice", "cand-3401", "Venice", "City used in the source's identification of Negri.")
mention(P219, "m-chp8-p219-zanchi", "cand-2834", "Zanchi", "Earlier painter in the San Rocco sequence.")
mention(P219, "m-chp8-p219-san-rocco", "cand-2351", "Scuola di San Rocco", "Reuse the indexed school candidate; its identity/type remains for S3.")
mention(P219, "m-chp8-p219-plague", "cand-7681", "plague of 1630", "Event cited as the subject of Negri's commemorative picture; location is not inferred.")
mention(P219, "m-chp8-p219-cavaliere-perugino", "cand-7682", "Turinese Cavaliere Perugino", "Title-only painter referent; do not conflate with Pietro Perugino.")
mention(P219, "m-chp8-p219-turinese", "cand-2662", "Turinese", "Geographic adjective linked to the Turin candidate, not a separate polity.")
mention(P219, "m-chp8-p219-king-savoy", "cand-7683", "King of Savoy", "Title-only protégé's patron; identity unresolved.")
mention(P219, "m-chp8-p219-cervelli-2", "cand-0638", "Cervelli", "Winner of the competition.", occurrence=1)
mention(P219, "m-chp8-p219-bergamo-1", "cand-6208", "Bergamo", "City visited by Cervelli to make alterations.")
mention(P219, "m-chp8-p219-ferri-2", "cand-1027", "Ciro Ferri", "The source links Ferri's earlier interest to the later Crossing subject.", occurrence=1)
mention(P219, "m-chp8-p219-third-oil", "cand-7663", "The third of the large oil paintings", "Part of the wider church decoration sequence; keep distinct from the central-nave group.")
mention(P219, "m-chp8-p219-crossing-1", "cand-7668", "The Crossing of the Red Sea", "Subject previously planned for Ferri and now entrusted to Giordano.")
mention(P219, "m-chp8-p219-bergamasque", "cand-6208", "Bcrgamasque", "OCR surface linked to Bergamo; page-image correction recorded in the statement.")
mention(P219, "m-chp8-p219-giordano-1", "cand-1172", "Luca Giordano", "Painter entrusted with the Crossing in 1682.")
mention(P219, "m-chp8-p219-committee-2", "cand-7641", "committee", "Committee able to employ Giordano for the venture.", occurrence=1)
mention(P219, "m-chp8-p219-naples", "cand-1722", "Naples", "City where Giordano was at the height of his career.")
mention(P219, "m-chp8-p219-picture-sent", "cand-7668", "the picture which he sent them", "Coreferential reference to Giordano's reported Crossing picture.")
mention(P219, "m-chp8-p219-church", "cand-7627", "the church", "Santa Maria Maggiore; context does not identify a specific remaining decoration contract.", occurrence=0)
mention(P219, "m-chp8-p219-fourteen", "cand-7686", "Fourteen more paintings", "Separate central-nave painting requirement.")
mention(P219, "m-chp8-p219-central-nave", "cand-7685", "central nave", "Interior space of Santa Maria Maggiore.")
mention(P219, "m-chp8-p219-como", "cand-7691", "Como", "Place named as Tencala's origin.")
mention(P219, "m-chp8-p219-tencala", "cand-2548", "Cristoforo\nTencala", "Name broken across source lines; candidate is the p.219 index entry.")
mention(P219, "m-chp8-p219-ceresa", "cand-0624", "Carlo\nCeresa", "Name broken across source lines; candidate is the p.219 index entry.")
mention(P219, "m-chp8-p219-modello", "cand-7687", "tnodello", "Source OCR form; print reads modello, recorded as an S2 correction.")
mention(P219, "m-chp8-p219-committee-3", "cand-7641", "committee", "Committee whose target was higher than Ceresa's proposal.", occurrence=2)
mention(P219, "m-chp8-p219-their-funds", "cand-7641", "their funds", "Anaphoric reference to the committee's financial capacity.")
mention(P219, "m-chp8-p219-cignani-1", "cand-0749", "Carlo Cignani", "Artist candidate with the p.219 S. Maria Maggiore index subentry.")
mention(P219, "m-chp8-p219-bologna", "cand-3398", "Bologna", "City associated with Cignani in this passage.")
mention(P219, "m-chp8-p219-italy-1", "cand-3461", "Italy", "Named region in Haskell's assessment of Giordano's court success.")
mention(P219, "m-chp8-p219-bergamo-2", "cand-6208", "Bergamo", "City Cignani visited to press his claims.", occurrence=1)
mention(P219, "m-chp8-p219-committee-4", "cand-7641", "The committee", "Committee that wavered and proposed a compromise.", occurrence=0)
mention(P219, "m-chp8-p219-cignani-2", "cand-0749", "Cignani", "Artist whose negotiating position led the plan to fail.", occurrence=1)
mention(P219, "m-chp8-p219-giordano-2", "cand-1172", "Luca Giordano", "Artist compared with Cignani in the later central-nave negotiations.", occurrence=1)
mention(P219, "m-chp8-p219-crossing-2", "cand-7668", "Crossing of the Red Sea", "Repeat reference to the Giordano painting.", occurrence=1)
mention(P219, "m-chp8-p219-fourteen-terms", "cand-7686", "the ten frescoes and four oils", "The proposed division of the fourteen central-nave paintings.")
mention(P219, "m-chp8-p219-contract", "cand-7688", "a contract", "The reported signed Giordano agreement; document identity is unresolved.")
mention(P219, "m-chp8-p219-bergamo-3", "cand-6208", "Bergamo", "Place where Giordano's assistant and servant would be housed.", occurrence=2)
mention(P219, "m-chp8-p219-giordano-3", "cand-1172", "Giordano", "Artist whose legendary speed initially attracted the committee.", occurrence=2)
mention(P219, "m-chp8-p219-committee-5", "cand-7641", "The committee", "Committee that could meet the reported conditions.", occurrence=1)
mention(P219, "m-chp8-p219-giordano-4", "cand-1172", "Giordano", "Artist whose success and evasive replies became a drawback.", occurrence=3)
mention(P219, "m-chp8-p219-italy-2", "cand-3461", "Italy", "Part of Haskell's broad court-success assessment.", occurrence=1)
mention(P219, "m-chp8-p219-europe", "cand-3462", "Europe", "Part of Haskell's broad court-success assessment.")
mention(P219, "m-chp8-p219-cignani-3", "cand-0749", "Cignani", "Name in the incomplete final sentence; continuation remains open to p.220.", occurrence=2)
mention(NOTES, "m-chp8-p219-bergomum-note", "cand-7689", "Bergomum, 1947, pp. 60-1", "Anonymous cited article; cited pages were not consulted.")
mention(NOTES, "m-chp8-p219-hymn-note", "cand-7684", "Hymn of Liberation after the Crossing", "Alternative subject reported in footnote 1, not independently verified.")
mention(NOTES, "m-chp8-p219-tassi-note", "cand-7690", "Tassi, I, p. 265", "Short-form citation; cited work and page were not consulted.")


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, page=219, physical=21, speaker="Haskell",
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


ocr = [
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 89,
     "ocr": "protege", "print": "protégé", "basis": "CHP-8.pdf physical page 21."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 91,
     "ocr": "Bcrgamasque", "print": "Bergamasque", "basis": "CHP-8.pdf physical page 21."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 93,
     "ocr": "setidi", "print": "scudi", "basis": "CHP-8.pdf physical page 21."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 96,
     "ocr": "tnodello", "print": "modello", "basis": "CHP-8.pdf physical page 21."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 96,
     "ocr": "\"should be required", "print": "should be required", "basis": "CHP-8.pdf physical page 21."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 97,
     "ocr": "Giordano’s.success", "print": "Giordano’s success", "basis": "CHP-8.pdf physical page 21 high-resolution crop."},
]

new_statements = [
    make_statement(
        "st-chp8-p219-zanchi-coloured-picture", P219, 87, 87, "cand-2834", "cand-7670",
        "painting_visual_description",
        "Haskell continues his description of Zanchi's accepted painting, emphasizing the colours of the women's costumes and the men's muscular backs against a tumultuous background.",
        "This closes the sentence ending in 'richly' on p.218; the description and praise remain Haskell's account, not an independent assessment.",
        ["cand-2834", "cand-7670"],
        extras={"continued_from_segment_id": P218, "continued_from_source_line": 84,
                "continued_from_statement_id": "st-chp8-p218-zanchi-canvas-accepted",
                "continuation_status": "closed"},
    ),
    make_statement(
        "st-chp8-p219-noah-competition", P219, 88, 88, "cand-7641", "cand-7678",
        "competition_for_replacement_painting",
        "After a delay of some years, the committee decided in 1677 to organize a competition for a Sacrifice of Noah painting to replace Ciro Ferri's unsuccessful effort above the door of the Colleoni chapel.",
        "The replacement picture is not identified with Ferri's separate planned Crossing of the Red Sea; the earlier unsuccessful effort remains unnamed.",
        ["cand-7641", "cand-7678", "cand-7679", "cand-1027", "cand-7669", "cand-7673", "cand-7671"],
        extras={"qualification_terms": ["after a delay of some years", "unsuccessful effort"]},
    ),
    make_statement(
        "st-chp8-p219-noah-competition-entrants", P219, 88, 89, "cand-7679", None,
        "competition_entries",
        "Three artists took part and submitted sketches: Federico Cervelli of Milan, Pietro Negri of Venice, and the Turinese Cavaliere Perugino.",
        "The source does not title or describe the individual sketches. Geographic descriptors are retained without external identity claims.",
        ["cand-7679", "cand-0638", "cand-3418", "cand-1731", "cand-3401", "cand-7682", "cand-2662"],
    ),
    make_statement(
        "st-chp8-p219-negri-san-rocco-picture", P219, 89, 89, "cand-1731", "cand-7680",
        "painting_for_institution",
        "Haskell says Pietro Negri had followed Zanchi in painting for the Scuola di San Rocco a picture commemorating the cessation of the plague of 1630.",
        "The painting has no supplied title or execution date; the plague's location is not specified. The indexed school candidate is retained for later identity/type alignment.",
        ["cand-1731", "cand-2834", "cand-7680", "cand-2351", "cand-7681"],
        extras={"qualification_terms": ["had followed", "to commemorate"]},
    ),
    make_statement(
        "st-chp8-p219-perugino-protege", P219, 89, 89, "cand-7683", "cand-7682",
        "patron_protege_relation",
        "Haskell identifies the Turinese Cavaliere Perugino as a protégé of the King of Savoy.",
        "Both referents are title-only in this passage; do not merge the painter with Pietro Perugino or the king with another title-only candidate until S3.",
        ["cand-7683", "cand-7682", "cand-1883", "cand-3586"],
        extras={"qualification_terms": ["Turinese", "Cavaliere", "protégé"]},
    ),
    make_statement(
        "st-chp8-p219-cervelli-wins-noah", P219, 90, 90, "cand-7641", "cand-7678",
        "competition_award_and_payment",
        "Cervelli won the competition; after visiting Bergamo to make certain alterations, he was paid 370 ducats.",
        "The account does not specify the alterations or provide a payment record.",
        ["cand-7641", "cand-0638", "cand-7678", "cand-6208"],
    ),
    make_statement(
        "st-chp8-p219-giordano-crossing-assigned", P219, 91, 92, "cand-7641", "cand-1172",
        "painting_entrusted_to_artist",
        "Haskell identifies the Crossing of the Red Sea as the third large oil painting and says that, in 1682, the subject that had fascinated Ciro Ferri was entrusted to Luca Giordano.",
        "The source connects the subject across the Ferri and Giordano passages but does not establish the external identity, completion history, or present location of a surviving canvas.",
        ["cand-7641", "cand-7663", "cand-7668", "cand-1027", "cand-1172"],
        extras={"footnote_markers": [1], "footnote_link_status": "linked",
                "footnote_segment": NOTES, "footnote_target_line": 377,
                "footnote_citation_statement_ids": ["st-chp8-p219-n1-citation"],
                "footnote_pending": False},
    ),
    make_statement(
        "st-chp8-p219-giordano-crossing-description", P219, 92, 93, "cand-1172", "cand-7668",
        "painting_sent_and_described",
        "Giordano was then at the height of his career in Naples; Haskell says the picture he sent glowed warmly around the faithful emerging from a dark-green, tempestuous sea and justified the committee's hopes.",
        "This is Haskell's reported description and evaluation. Footnote 1 gives a reported alternative identification of the represented subject; it is not independently verified.",
        ["cand-1172", "cand-7668", "cand-1722", "cand-7641", "cand-7684"],
        extras={"qualification_terms": ["at the height", "justified their great hopes"],
                "footnote_markers": [1], "footnote_link_status": "linked",
                "footnote_segment": NOTES, "footnote_target_line": 377,
                "footnote_citation_statement_ids": ["st-chp8-p219-n1-citation"],
                "footnote_pending": False,
                "ocr_corrections": [ocr[1]]},
    ),
    make_statement(
        "st-chp8-p219-giordano-gift-and-remainder", P219, 93, 93, "cand-1172", "cand-7627",
        "reported_payment_and_unrealized_remainder",
        "Haskell reports that Giordano received a present of 100 scudi in addition to the 700 previously promised and was unsuccessfully pressed to undertake all the remaining church decoration.",
        "The giver and terms of the original promise are not named; no reason is supplied for Giordano's failure to take on the remaining decoration.",
        ["cand-1172", "cand-7627"],
        extras={"ocr_corrections": [ocr[2]], "qualification_terms": ["in addition to", "unsuccessfully"]},
    ),
    make_statement(
        "st-chp8-p219-central-nave-requirement", P219, 94, 94, None, "cand-7686",
        "central_nave_painting_requirement",
        "Fourteen further paintings were required for the central nave, and difficult negotiations began.",
        "No exact date, subject list, or completed set of fourteen paintings is supplied here.",
        ["cand-7686", "cand-7685", "cand-7627"],
    ),
    make_statement(
        "st-chp8-p219-tencala-approached", P219, 94, 95, "cand-2548", "cand-7686",
        "artist_approached_for_project",
        "In 1681 the painter Cristoforo Tencala from Como was approached for the central-nave work, but nothing was arranged.",
        "The person who approached him is not named; no contract or reason for the failed arrangement is supplied.",
        ["cand-2548", "cand-7691", "cand-7686"],
    ),
    make_statement(
        "st-chp8-p219-ceresa-modello", P219, 95, 96, "cand-0624", "cand-7687",
        "modello_submitted_and_received",
        "In 1682 Carlo Ceresa submitted a modello that was called 'very beautiful and precious'; Haskell characterizes that praise as flattering language concealing the committee's higher target.",
        "The model's subject and later fate are not stated; the explanation of the praise is Haskell's account, not a quoted committee admission.",
        ["cand-0624", "cand-7687", "cand-7641", "cand-7686"],
        extras={"ocr_corrections": [ocr[3]], "qualification_terms": ["a year later", "very beautiful and precious", "designed to conceal"]},
    ),
    make_statement(
        "st-chp8-p219-project-funds-strained", P219, 96, 96, "cand-7641", "cand-7686",
        "project_funding_constraint",
        "Haskell says the committee's funds could not withstand the strain as it pursued the higher target.",
        "This is the source's general description of the project's finances; no budget, donor, or account is named.",
        ["cand-7641", "cand-7686"],
    ),
    make_statement(
        "st-chp8-p219-cignani-reputation", P219, 96, 96, "cand-0749", None,
        "qualified_reputation_assessment",
        "Haskell says Carlo Cignani of Bologna was probably the most famous painter in Italy at that time.",
        "The ranking is explicitly qualified as probable and attributed to Haskell.",
        ["cand-0749", "cand-3398", "cand-3461"],
        extras={"ocr_corrections": [ocr[3]], "qualification_terms": ["probably", "at this time"]},
    ),
    make_statement(
        "st-chp8-p219-cignani-negotiation-fails", P219, 96, 96, "cand-0749", "cand-7686",
        "commission_negotiation_failed",
        "Cignani asked for what Haskell calls exorbitant sums and expenses, arrived in Bergamo to press his claims, and after the committee wavered and proposed a compromise maintained his position, so the plan fell through.",
        "The sums and compromise terms are not given; Haskell's description of Cignani's eagerness is an interpretation.",
        ["cand-0749", "cand-3398", "cand-6208", "cand-7641", "cand-7686"],
        extras={"ocr_corrections": [ocr[3]], "qualification_terms": ["exorbitant", "obviously anxious", "sorely tempted"]},
    ),
    make_statement(
        "st-chp8-p219-giordano-project-terms", P219, 96, 96, "cand-1172", "cand-7686",
        "commission_terms_negotiated",
        "For ten frescoes and four oil paintings, Giordano first asked for 6,000 ducats and under pressure agreed to 5,000 on condition that he, an assistant, and a servant receive free board and lodging for as long as they were required to stay in Bergamo.",
        "The amounts and conditional terms are Haskell's report; the source does not name the negotiating party or provide the contract text. The opening quote before 'should' in S0 is not visible in the print.",
        ["cand-1172", "cand-7686", "cand-6208", "cand-7688"],
        extras={"footnote_markers": [2], "footnote_link_status": "linked",
                "footnote_segment": NOTES, "footnote_target_line": 378,
                "footnote_citation_statement_ids": ["st-chp8-p219-n2-citation"],
                "footnote_pending": False,
                "ocr_corrections": [ocr[4]],
                "qualification_terms": ["under pressure", "provided that", "as long as"]},
    ),
    make_statement(
        "st-chp8-p219-giordano-contract-not-performed", P219, 96, 96, "cand-1172", "cand-7688",
        "contract_signed_then_not_performed",
        "The committee could just manage Giordano's conditions and a contract was signed, only to be ignored by the artist.",
        "The document is not identified or independently checked; the source does not specify why Giordano ignored it or what obligations remained.",
        ["cand-7641", "cand-1172", "cand-7688", "cand-7686"],
        extras={"footnote_markers": [2], "footnote_link_status": "linked",
                "footnote_segment": NOTES, "footnote_target_line": 378,
                "footnote_citation_statement_ids": ["st-chp8-p219-n2-citation"],
                "footnote_pending": False,
                "ocr_corrections": [ocr[4]]},
    ),
    make_statement(
        "st-chp8-p219-giordano-speed-and-court-success", P219, 96, 97, "cand-1172", "cand-7686",
        "commission_delay_and_reputation",
        "Haskell says Giordano's legendary speed initially attracted the committee, but year after year and letter after letter brought conciliatory yet evasive replies; his success with the courts of Italy and Europe became a drawback.",
        "The timing and evaluation are Haskell's narrative; 'success' is corrected from the OCR join/punctuation error visible in S0.",
        ["cand-1172", "cand-7641", "cand-3461", "cand-3462", "cand-7686"],
        extras={"ocr_corrections": [ocr[5]], "qualification_terms": ["legendary", "conciliatory", "evasive", "real drawback"]},
    ),
    make_statement(
        "st-chp8-p219-terms-stiffen-cignani-open", P219, 98, 98, "cand-0749", "cand-1172",
        "possible_alternative_after_terms_change",
        "As Giordano's terms stiffened, Haskell began to suggest that Cignani might prove more satisfactory.",
        "The source segment ends mid-sentence at 'Perhaps Cignani would'; the thought continues on p.220 and remains open until that segment is read.",
        ["cand-0749", "cand-1172"],
        extras={"ocr_corrections": [ocr[3]],
                "continuation_to_segment_id": P220, "continuation_to_source_line": 101,
                "continuation_fragment": "Perhaps Cignani would",
                "continuation_status": "open"},
    ),
    make_statement(
        "st-chp8-p219-n1-citation", NOTES, 377, 377, None, "cand-7689",
        "footnote_citation",
        "Footnote 1 cites an anonymous article in Bergomum (1947), pages 60–61.",
        "The article title and author are not supplied; the article itself has not been consulted.",
        ["cand-7689"], speaker="Haskell", text_layer="bibliographic citation",
        extras={"printed_page_locator": "p.219 n.1", "footnote_marker": 1,
                "footnote_body_link_status": "linked",
                "linked_body_statement_ids": ["st-chp8-p219-giordano-crossing-assigned",
                                              "st-chp8-p219-giordano-crossing-description"]},
    ),
    make_statement(
        "st-chp8-p219-n1-alternative-subject", NOTES, 377, 377, "cand-7668", "cand-7684",
        "reported_subject_identification",
        "Haskell reports that the anonymous Bergomum article says the subject represented was in fact the Hymn of Liberation after the Crossing.",
        "This is a claim transmitted by Haskell from an unconsulted secondary article; it remains a reported alternative and does not independently verify the painting's identity or subject.",
        ["cand-7668", "cand-7684", "cand-7689"],
        speaker="Haskell reporting an anonymous article", text_layer="footnote report",
        extras={"printed_page_locator": "p.219 n.1", "footnote_marker": 1,
                "qualification_terms": ["anonymous", "has shown", "in fact"]},
    ),
    make_statement(
        "st-chp8-p219-n2-citation", NOTES, 378, 378, None, "cand-7690",
        "footnote_citation",
        "Footnote 2 cites Tassi, volume I, page 265.",
        "The cited work and page have not been identified or independently consulted; this citation does not itself verify the reported contract.",
        ["cand-7690"], speaker="Haskell", text_layer="bibliographic citation",
        extras={"printed_page_locator": "p.219 n.2", "footnote_marker": 2,
                "footnote_body_link_status": "linked",
                "linked_body_statement_ids": ["st-chp8-p219-giordano-project-terms",
                                              "st-chp8-p219-giordano-contract-not-performed"]},
    ),
]

existing_statement_ids = {row["statement_id"] for row in statement_rows}
new_statement_ids = [row["statement_id"] for row in new_statements]
if len(set(new_statement_ids)) != len(new_statement_ids) or existing_statement_ids.intersection(new_statement_ids):
    raise SystemExit("duplicate statement ID")
for row in new_statements:
    if row["segment_id"] not in segment_by_id:
        raise SystemExit(f"statement source segment missing: {row['statement_id']}")
    source_meta = segment_by_id[row["segment_id"]]
    q = row["qualifiers"]
    if not (source_meta["line_start"] <= q["source_line_start"] <= q["source_line_end"] <= source_meta["line_end"]):
        raise SystemExit(f"statement line range escapes its segment: {row['statement_id']}")
    text = segment_text(row["segment_id"])
    if row["original_quote"] not in text:
        raise SystemExit(f"statement quote is not an exact source span: {row['statement_id']}")
    for endpoint in (row["subject_candidate_id"], row["object_candidate_id"]):
        if endpoint is not None and endpoint not in candidate_ids:
            raise SystemExit(f"missing statement endpoint: {row['statement_id']} -> {endpoint}")
    for candidate_id in row["qualifiers"]["mentioned_candidate_ids"]:
        if candidate_id not in candidate_ids:
            raise SystemExit(f"missing statement candidate: {row['statement_id']} -> {candidate_id}")
for row in new_mentions:
    if row["segment_id"] not in {P219, NOTES}:
        raise SystemExit(f"unexpected mention segment: {row['mention_id']}")

statement_by_id = {row["statement_id"]: row for row in statement_rows}
prior217 = statement_by_id.get("st-chp8-p217-ferri-cannot-leave-open")
prior218 = statement_by_id.get("st-chp8-p218-zanchi-canvas-accepted")
if not prior217 or prior217["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.217 Ferri continuation is missing or changed")
if not prior218 or prior218["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.218 Zanchi continuation is missing or changed")
if prior217["qualifiers"].get("continuation_to_segment_id") != P218:
    raise SystemExit("p.217 continuation target differs; inspect before proceeding")
if prior217["qualifiers"].get("continuation_to_source_line") != 79:
    raise SystemExit("p.217 continuation line differs; inspect before proceeding")
if prior218["qualifiers"].get("continuation_to_segment_id") != "chp-8:08_CHP-8_sec_ii:l87-95":
    raise SystemExit("p.218 continuation target differs from the known stale segment ID")
if prior218["qualifiers"].get("continuation_to_source_line") != 87:
    raise SystemExit("p.218 continuation line differs; inspect before proceeding")
if prior218["qualifiers"].get("continuation_fragment") != "richly":
    raise SystemExit("p.218 continuation fragment changed")

patched217 = json.loads(json.dumps(prior217, ensure_ascii=False))
patched217["qualifiers"].update({
    "continuation_status": "closed",
    "continuation_resolved_by_segment": P218,
    "continuation_resolved_by_source_line": 79,
    "continuation_resolved_by_statement_id": "st-chp8-p218-ferri-invitation-response",
})
patched217["qualifiers"].pop("continuation_in", None)

patched218 = json.loads(json.dumps(prior218, ensure_ascii=False))
patched218["qualifiers"].update({
    "continuation_to_segment_id": P219,
    "continuation_status": "closed",
    "continuation_resolved_by_segment": P219,
    "continuation_resolved_by_source_line": 87,
    "continuation_resolved_by_statement_id": "st-chp8-p219-zanchi-coloured-picture",
})
patched218["qualifiers"].pop("continuation_in", None)

coverage_updates = {
    P217: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L69-76",
        "note": "Printed p.217 body and n.1 are covered. Its final Ferri invitation sentence closes at p.218 L79; the earlier p.216 count continuation closes at p.217 L70. See the linked continuation statements.",
    },
    P218: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L79-84",
        "note": "Printed p.218 body and n.1 are covered. The Zanchi painting description continues with p.219 L87; the visual description is recorded there. OCR corrections remain S2-only.",
    },
    P219: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L86-98",
        "note": "Printed p.219 body reviewed against CHP-8.pdf physical p.21. Records the 1677 Sacrifice of Noah competition, Cervelli's award, the 1682 Giordano Crossing, central-nave negotiations, and Giordano's failed terms/contract. The final sentence ends mid-thought at 'Perhaps Cignani would' and continues at p.220 L101.",
    },
    NOTES: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-378",
        "note": "Adds p.217–219 notes through p.219 n.2 and links them to body statements. The anonymous Bergomum article and Tassi citation are locators only; cited sources were not independently consulted. Later notes L379-461 remain pending.",
    },
}
updated_coverage = []
for segment in segments:
    sid = segment["segment_id"]
    if sid in coverage_updates:
        updated_coverage.append({"chapter": segment["chapter"], "segment_id": sid, **coverage_updates[sid]})
    elif sid in coverage_by_id:
        updated_coverage.append(dict(coverage_by_id[sid]))
    else:
        raise SystemExit(f"coverage row missing: {sid}")
if {row["segment_id"] for row in updated_coverage} != set(segment_by_id):
    raise SystemExit("coverage and source segment IDs do not match")

patched_statement_rows = [
    patched217 if row["statement_id"] == prior217["statement_id"] else
    patched218 if row["statement_id"] == prior218["statement_id"] else row
    for row in statement_rows
]

preview = {
    "mode": "dry-run",
    "candidate_additions": len(new_candidates),
    "candidate_updates": ["cand-7668.detail"],
    "mention_additions": len(new_mentions),
    "statement_additions": len(new_statements),
    "coverage_updates": {
        sid: {"disposition": val["disposition"], "migration_status": val["migration_status"],
              "source_line_ranges": val["source_line_ranges"]}
        for sid, val in coverage_updates.items()
    },
    "closed_continuations": [
        {"statement_id": prior217["statement_id"], "to": P218, "line": 79},
        {"statement_id": prior218["statement_id"], "to": P219, "line": 87},
    ],
    "open_continuation": {"segment_id": P219, "to": P220, "line": 101},
    "ocr_corrections": [item["ocr"] + " -> " + item["print"] for item in ocr],
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

candidate_rows = [patched_7668 if row["candidate_id"] == "cand-7668" else row for row in candidate_rows]
candidate_rows.extend(dict(zip(candidate_fields, row)) for row in new_candidates)
write_csv_atomic(CANDIDATE_PATH, candidate_fields, candidate_rows)
mention_rows.extend(new_mentions)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
patched_statement_rows.extend(new_statements)
write_jsonl_atomic(STATEMENT_PATH, patched_statement_rows)
write_csv_atomic(COVERAGE_PATH, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
