"""Reconcile p.275 S2 mentions, entity granularity, and footnote relations.

Dry-run by default. Apply only after source/table hashes and exact spans pass.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-9.pdf"
TABLES = ROOT / "04-knowledge/tables"
PROCESS = ROOT / "03-processing/patrons-and-painters-full-book-s2/process"
BODY = "chp-9:09_CHP-9_sec_ii:l80-83"
NOTES = "chp-9:09_CHP-9_sec_ii:l85-127"
BACKUP_SUFFIX = ".bak-s2-chp9-p275-reconciliation-20261014"

EXPECTED_SHA256 = {
    SOURCE: "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    PDF: "8d0adc954f824fa5c6f202571e03a6eb8475dd4125c91c41f79204a445b961ec",
    TABLES / "entity-candidates.csv": "dcd538f63b57d3b52554eaa548248ef363b13ccb57d8c44d38dfdeb47613ccd4",
    TABLES / "mentions.csv": "3aae1e4f7f622e727faabefc6b306ff10f660a4e24d71e9f42439b9b5fdfbb95",
    TABLES / "book-statements.jsonl": "6c130072bbc56bd237f74ea815d74e9a23983beed5bf2a1597c42d4d3b747289",
    TABLES / "s2-coverage.csv": "966cb4f1a5dc5a6c3cfbc81082c6ef3f8d08ccc2a9e359bba8d6f0b2049a533c",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(handle.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(handle.name)
    tmp.replace(path)


for path, expected in EXPECTED_SHA256.items():
    actual = sha256(path)
    if actual != expected:
        raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[79].strip() != "[Page 275]" or not source_lines[80].startswith("Comer was also interested"):
    raise SystemExit("p.275 source anchors changed")
if "1778/" not in source_lines[81] or "eesere" not in source_lines[82]:
    raise SystemExit("expected p.275 OCR readings changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)

candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
if max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates) != 12105:
    raise SystemExit("candidate sequence changed")
if (coverage_by_id.get(BODY, {}).get("disposition"), coverage_by_id.get(BODY, {}).get("migration_status")) != ("reviewed", "complete"):
    raise SystemExit("p.275 body coverage has changed")
if (coverage_by_id.get(NOTES, {}).get("disposition"), coverage_by_id.get(NOTES, {}).get("migration_status")) != ("reviewed", "partial"):
    raise SystemExit("p.275 consolidated notes coverage has changed")

EXPECTED_EXISTING_STATEMENTS = {
    "st-chp9-p275-corner-advised-carita-facade",
    "st-chp9-p275-corner-advised-srocco-facade",
    "st-chp9-p275-corner-architecture-interest",
    "st-chp9-p275-corner-harmony-creed",
    "st-chp9-p275-corner-marble-altar-preference",
    "st-chp9-p275-corner-rejected-theatrical-friezes",
    "st-chp9-p275-corner-uniform-altar-rules",
    "st-chp9-p275-gerardi-madonna-complaint-tail",
    "st-chp9-p275-n01",
    "st-chp9-p275-n01-probable-letterini-corner-commission",
    "st-chp9-p275-n02",
    "st-chp9-p275-n02-gherardi-church-decoration-complaint",
    "st-chp9-p275-n02-haskell-commentary-tail",
    "st-chp9-p275-priest-says-corner-built-altars",
    "st-chp9-p275-sanciano-austerity-comparison",
    "st-chp9-p275-sanciano-material-description",
    "st-chp9-p275-sanciano-surviving-style",
}
if {row_id for row_id in statement_by_id if row_id.startswith("st-chp9-p275-")} != EXPECTED_EXISTING_STATEMENTS:
    raise SystemExit("p.275 statement set changed")

required_candidates = {
    "cand-0844",  # Flaminio Corner
    "cand-1155",  # P. E. Gherardi
    "cand-1400",  # Bartolommeo Letterini
    "cand-1717",  # Muratori
    "cand-2719",  # Venice
    "cand-3416",  # Modena
    "cand-3427",  # Virgin Mary, in the continuation only
    "cand-3916",  # S. Rocco
    "cand-8198",  # Church of San Canciano
    "cand-8539",  # Biblioteca Estense
    "cand-8770",  # unresolved Carità site
    "cand-8771",  # Corner-associated S. Canciano altars
    "cand-8772",  # Corner's altar preference
    "cand-8821",  # Brustoloni citation locator
    "cand-8822",  # Letterini altar paintings
    "cand-8823",  # Gherardi letter
}
missing = required_candidates - candidate_by_id.keys()
if missing:
    raise SystemExit(f"required candidate is missing: {sorted(missing)}")

next_id = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates) + 1
facade_srocco_id = f"cand-{next_id:04d}"
facade_carita_id = f"cand-{next_id + 1:04d}"
new_candidates = [
    {
        "candidate_id": facade_srocco_id,
        "index_entry_id": "",
        "canonical_name": "Great marble façade of S. Rocco reported by Haskell on p.275",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Architectural work distinct from the Church of S. Rocco. Haskell reports that Corner encouraged its construction with advice, possibly without money; completion and direct funding by Corner are not established.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L81",
    },
    {
        "candidate_id": facade_carita_id,
        "index_entry_id": "",
        "canonical_name": "Great marble façade at the Carità reported by Haskell on p.275",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Architectural work distinct from the unresolved Carità site candidate. Haskell reports that Corner encouraged its construction with advice, possibly without money; the site identity, completion, and any direct funding remain unresolved.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY}#L81",
    },
]
if any(row["candidate_id"] in candidate_by_id for row in new_candidates):
    raise SystemExit("planned façade candidate ID already exists")

candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
source_segments = {
    BODY: (80, 83),
    NOTES: (85, 127),
}
segment_texts = {
    segment_id: "\n".join(source_lines[first - 1:last])
    for segment_id, (first, last) in source_segments.items()
}
line_offsets = {}
for segment_id, (first, last) in source_segments.items():
    offset = 0
    for line_no in range(first, last + 1):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(source_lines[line_no - 1]) + 1

mention_ids = {row["mention_id"] for row in mentions}
planned_mentions = []


def add_mention(mention_id, segment_id, line_no, candidate_id, surface, note, occurrence=0):
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in planned_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown mention candidate: {candidate_id}")
    line = source_lines[line_no - 1]
    matches, cursor = [], 0
    while True:
        pos = line.find(surface, cursor)
        if pos < 0:
            break
        matches.append(pos)
        cursor = pos + 1
    if occurrence >= len(matches):
        raise SystemExit(f"surface absent on L{line_no}: {surface!r}")
    start = line_offsets[(segment_id, line_no)] + matches[occurrence]
    end = start + len(surface)
    if segment_texts[segment_id][start:end] != surface:
        raise SystemExit(f"bad source span: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })


BODY_MENTIONS = [
    ("corner", 81, "cand-0844", "Comer", "S0 OCR reads Comer; the p.275 scan reads Corner.", 0),
    ("srocco", 81, "cand-3916", "S. Rocco", "Church site; distinct from its marble façade work.", 0),
    ("carita", 81, "cand-8770", "Carita", "S0 OCR omits the accent visible in the scan; exact site identity remains unresolved.", 0),
    ("facade-srocco", 81, facade_srocco_id, "façades of S. Rocco", "The marble façade is a work distinct from the Church of S. Rocco.", 0),
    ("facade-carita", 81, facade_carita_id, "the Carita", "The second façade in the coordinated phrase; site identity remains unresolved.", 0),
    ("corner-marble", 82, "cand-8772", "marble", "Material in Corner's reported preference for church altars.", 0),
    ("venetian-churches-1", 82, "cand-2719", "Venetian", "Regional modifier in the reported altar preference.", 0),
    ("altars", 82, "cand-8771", "All the altars", "General altar rule reported by Haskell; not an individually named set.", 0),
    ("same-marble", 82, "cand-8772", "identical marble", "Part of the reported altar-design preference.", 0),
    ("harmony-creed", 82, "cand-8772", "‘Harmony is delightful in everything’", "Quoted as Corner's creed by Haskell.", 0),
    ("corner-patronage", 82, "cand-0844", "his patronage", "Anaphoric reference to Flaminio Corner.", 0),
    ("sanciano", 82, "cand-8198", "S. Canciano", "Church site, mapped to the specific existing S. Canciano candidate rather than the generic Churches index candidate.", 0),
    ("corner-style", 82, "cand-8772", "the style he encouraged", "Haskell's reference to the altar-design preference associated with Corner.", 0),
    ("corner-altar-group", 82, "cand-8771", "These very altars", "The S. Canciano altar group; distinct from the p.274 Angeli altarpieces.", 0),
    ("corner-built", 82, "cand-0844", "him", "Anaphoric reference in the priest's reported funeral speech.", 0),
    ("corner-columns", 82, "cand-8771", "black and blue-veined marble columns", "Architectural detail in Haskell's S. Canciano description.", 0),
    ("corner-capitals", 82, "cand-8771", "gold Corinthian capitals", "Architectural detail in Haskell's S. Canciano description.", 0),
    ("venetian-churches-2", 82, "cand-2719", "Venetian", "Regional modifier in Haskell's comparison with contemporary Venetian church style.", 1),
    ("madonna", 83, "cand-3427", "Madonna", "Generic Marian image in the continuation of Gherardi's quoted letter.", 0),
]
for key, line_no, candidate_id, surface, note, occurrence in BODY_MENTIONS:
    add_mention(f"m-chp9-p275-{key}", BODY, line_no, candidate_id, surface, note, occurrence)

NOTE_MENTIONS = [
    ("n01-brustoloni", 126, "cand-8821", "Don Giovanni Domenico Brustoloni, 1779", "P.275 note 1 citation/source locator; the publication was not independently consulted."),
    ("n01-letterini-paintings", 126, "cand-8822", "altar paintings by Bartolommeo Letterini", "Haskell says it is probable Corner commissioned these paintings; titles, dates, and locations are not supplied."),
    ("n01-corner", 126, "cand-0844", "Corner", "Named as the probable commissioner in Haskell's attribution."),
    ("n01-letterini-person", 126, "cand-1400", "Bartolommeo Letterini", "Painter named in Haskell's probable attribution; reuse the existing person candidate."),
    ("n02-date", 127, "cand-8823", "20 February 1746", "Date of the cited letter; the letter itself was not independently consulted."),
    ("n02-gherardi", 127, "cand-1155", "P. E. Gherardi", "Named letter writer in Haskell's footnote; identity alignment remains for S3."),
    ("n02-muratori", 127, "cand-1717", "Muratori", "Named addressee; preserve the shortened form used by Haskell."),
    ("n02-biblioteca-estense", 127, "cand-8539", "Biblioteca Estense", "Repository named in the letter locator; reuse the existing institution candidate."),
    ("n02-modena", 127, "cand-3416", "Modena", "Location in the letter locator; reuse the existing place candidate."),
    ("n02-venetian-churches", 127, "cand-2719", "Venetian churches", "The setting in Haskell's statement that other people protested church decoration."),
]
for key, line_no, candidate_id, surface, note in NOTE_MENTIONS:
    add_mention(f"m-chp9-p275-{key}", NOTES, line_no, candidate_id, surface, note)

new_statement_ids = {
    "st-chp9-p275-n02-other-protests-context",
    "st-chp9-p275-n02-letter-authored-by",
    "st-chp9-p275-n02-letter-addressed-to",
    "st-chp9-p275-n02-letter-held-at",
}
if new_statement_ids & statement_by_id.keys():
    raise SystemExit("planned p.275 statement ID already exists")

CLASSIFICATIONS = {
    "st-chp9-p275-corner-advised-carita-facade": True,
    "st-chp9-p275-corner-advised-srocco-facade": True,
    "st-chp9-p275-corner-architecture-interest": False,
    "st-chp9-p275-corner-harmony-creed": True,
    "st-chp9-p275-corner-marble-altar-preference": True,
    "st-chp9-p275-corner-rejected-theatrical-friezes": False,
    "st-chp9-p275-corner-uniform-altar-rules": True,
    "st-chp9-p275-gerardi-madonna-complaint-tail": False,
    "st-chp9-p275-n01": False,
    "st-chp9-p275-n01-probable-letterini-corner-commission": True,
    "st-chp9-p275-n02": False,
    "st-chp9-p275-n02-gherardi-church-decoration-complaint": False,
    "st-chp9-p275-n02-haskell-commentary-tail": False,
    "st-chp9-p275-priest-says-corner-built-altars": True,
    "st-chp9-p275-sanciano-austerity-comparison": False,
    "st-chp9-p275-sanciano-material-description": False,
    "st-chp9-p275-sanciano-surviving-style": True,
}
if set(CLASSIFICATIONS) != EXPECTED_EXISTING_STATEMENTS:
    raise SystemExit("classification list does not cover the exact p.275 statement set")

for statement_id, relation_candidate in CLASSIFICATIONS.items():
    statement_by_id[statement_id]["qualifiers"]["relation_candidate"] = relation_candidate

def set_refs(statement_id, candidate_ids):
    statement_by_id[statement_id]["qualifiers"]["mentioned_candidate_ids"] = sorted(set(candidate_ids))


srocco_row = statement_by_id["st-chp9-p275-corner-advised-srocco-facade"]
srocco_row["object_candidate_id"] = facade_srocco_id
srocco_row["predicate"] = "corner_reportedly_encouraged_construction_of_marble_facade_at_s_rocco"
srocco_row["qualifiers"]["claim"] = "Haskell reports that Corner encouraged, with advice, construction of the great marble façade at S. Rocco."
srocco_row["qualifiers"]["qualification"] = "Haskell says 'if not with money'; this does not establish that Corner funded the work or that the façade was completed."
set_refs(srocco_row["statement_id"], ["cand-0844", "cand-3916", facade_srocco_id, "cand-8770"])

carita_row = statement_by_id["st-chp9-p275-corner-advised-carita-facade"]
carita_row["object_candidate_id"] = facade_carita_id
carita_row["predicate"] = "corner_reportedly_encouraged_construction_of_marble_facade_at_carita"
carita_row["qualifiers"]["claim"] = "Haskell reports that Corner encouraged, with advice, construction of the great marble façade at the Carità."
carita_row["qualifiers"]["qualification"] = "Haskell says 'if not with money'; the exact Carità site identity, direct funding by Corner, and completion of the façade remain unresolved."
set_refs(carita_row["statement_id"], ["cand-0844", "cand-3916", "cand-8770", facade_carita_id])

surviving_row = statement_by_id["st-chp9-p275-sanciano-surviving-style"]
surviving_row["subject_candidate_id"] = "cand-8198"
set_refs(surviving_row["statement_id"], ["cand-8198", "cand-0844", "cand-8771", "cand-8772"])

priest_row = statement_by_id["st-chp9-p275-priest-says-corner-built-altars"]
set_refs(priest_row["statement_id"], ["cand-0844", "cand-8198", "cand-8771"])
priest_row["qualifiers"]["qualification"] = "Nested quotation reported by Haskell. Printed note 1 is now transcribed and linked in the consolidated p.268-275 notes segment; Brustoloni's cited publication was not independently consulted."

comparison_row = statement_by_id["st-chp9-p275-sanciano-austerity-comparison"]
comparison_row["qualifiers"]["qualification"] = "Comparative aesthetic judgement by Haskell. Printed note 2's citation, quoted letter, and Haskell continuation are recorded and linked in the consolidated p.268-275 notes segment; the cited letter was not independently consulted."
note2_ids = sorted({
    "st-chp9-p275-n02",
    "st-chp9-p275-n02-gherardi-church-decoration-complaint",
    "st-chp9-p275-n02-haskell-commentary-tail",
    *new_statement_ids,
})
comparison_row["qualifiers"]["footnote_statement_ids"] = note2_ids

complaint_row = statement_by_id["st-chp9-p275-n02-gherardi-church-decoration-complaint"]
complaint_row["subject_candidate_id"] = "cand-1155"
complaint_row["object_candidate_id"] = None
set_refs(complaint_row["statement_id"], ["cand-1155", "cand-8823"])
complaint_row["qualifiers"]["qualification"] = "This is Gherardi's reported complaint, not an independent assessment of Venetian churches; the quotation continues at p.275 L83. Haskell cites but the underlying letter was not independently consulted."

tail_row = statement_by_id["st-chp9-p275-gerardi-madonna-complaint-tail"]
tail_row["subject_candidate_id"] = "cand-1155"
tail_row["object_candidate_id"] = None
set_refs(tail_row["statement_id"], ["cand-1155", "cand-3427", "cand-8823"])
tail_row["qualifiers"]["qualification"] = "Continuation of Gherardi's 20 February 1746 letter quoted by Haskell; it describes Madonna images in churches and is not a separate Corner altar-preference claim. The Italian text is transcribed by Haskell, not independently checked against the letter."

new_statements = []


def add_statement(statement_id, subject, obj, predicate, line_quote, claim, qualification, refs, relation_candidate, text_layer):
    line_no = 127
    if line_quote not in source_lines[line_no - 1]:
        raise SystemExit(f"unanchored new statement quote: {statement_id}")
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": NOTES,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_no,
            "source_line_end": line_no,
            "printed_page": 275,
            "pdf_physical_page": 41,
            "claim": claim,
            "speaker": "Haskell's footnote",
            "text_layer": text_layer,
            "qualification": qualification,
            "mentioned_candidate_ids": sorted(set(refs)),
            "relation_candidate": relation_candidate,
            "footnote_marker": 2,
            "footnote_segment": NOTES,
            "footnote_body_link_status": "linked",
            "linked_body_statement_ids": ["st-chp9-p275-sanciano-austerity-comparison"],
            "footnote_refs": [{"marker": 2, "segment_id": BODY, "source_line": 82}],
            "cross_reference_segments": [{"segment_id": BODY, "source_line_start": 82, "source_line_end": 82}],
        },
        "original_quote": line_quote,
        "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "origin": "book",
    })


add_statement(
    "st-chp9-p275-n02-other-protests-context", None, None,
    "haskell_reports_other_protests_against_excessive_venetian_church_decoration",
    "Other people too protested about the excessive decoration of Venetian churches.",
    "Haskell says other people also protested excessive decoration in Venetian churches, introducing Gherardi's letter as one cited example.",
    "The other protestors remain unidentified; do not infer their membership or count from this phrase.",
    ["cand-2719"], False, "footnote contextual statement",
)
add_statement(
    "st-chp9-p275-n02-letter-authored-by", "cand-8823", "cand-1155",
    "letter_authored_by_gherardi",
    "P. E. Gherardi wrote",
    "Haskell identifies P. E. Gherardi as the author of the letter dated 20 February 1746.",
    "Source-reported authorship; the underlying letter was not independently consulted.",
    ["cand-8823", "cand-1155"], True, "footnote source attribution",
)
add_statement(
    "st-chp9-p275-n02-letter-addressed-to", "cand-8823", "cand-1717",
    "letter_addressed_to_muratori",
    "P. E. Gherardi wrote to Muratori",
    "Haskell identifies Muratori as the addressee of Gherardi's letter dated 20 February 1746.",
    "Source-reported addressee; preserve Haskell's abbreviated name and do not infer a fuller identity here.",
    ["cand-8823", "cand-1717", "cand-1155"], True, "footnote source attribution",
)
add_statement(
    "st-chp9-p275-n02-letter-held-at", "cand-8823", "cand-8539",
    "letter_located_at_biblioteca_estense",
    "letter in Biblioteca Estense, Modena",
    "Haskell locates the cited Gherardi letter at Biblioteca Estense in Modena.",
    "Repository locator as reported in Haskell's footnote; the manuscript was not independently consulted.",
    ["cand-8823", "cand-8539", "cand-3416"], True, "footnote source locator",
)

existing_mention_spans = {
    (row["segment_id"], row["start_char"], row["end_char"], row["surface_form"])
    for row in mentions
}
new_mention_spans = [(row["segment_id"], row["start_char"], row["end_char"], row["surface_form"]) for row in planned_mentions]
if len(new_mention_spans) != len(set(new_mention_spans)) or existing_mention_spans.intersection(new_mention_spans):
    raise SystemExit("duplicate mention span in reconciliation plan")

statement_rows = []
for row in statements:
    if row["statement_id"] == "st-chp9-p275-n02":
        row["qualifiers"]["continued_by_statement_ids"] = sorted(set(row["qualifiers"].get("continued_by_statement_ids", [])))
    statement_rows.append(row)

notes_cov = coverage_by_id[NOTES]
old_coverage_note = notes_cov.get("note", "")
if "p.275 remains to be reconciled" not in old_coverage_note:
    raise SystemExit("expected p.275 partial-coverage rationale changed")
notes_cov["migration_status"] = "complete"
notes_cov["note"] = old_coverage_note.replace(
    "p.275 remains to be reconciled, so coverage stays partial.",
    "P.275 was reconciled against the printed scan on 2026-10-14: restored 10 note mentions; classified the existing citation and complaint statements; added the missing contextual protest claim and atomic letter author, addressee, and repository relation candidates. All quoted continuations and body links were checked; the cited manuscript was not independently consulted. Coverage is now complete.",
)
if notes_cov["note"] == old_coverage_note:
    raise SystemExit("failed to close the p.275 coverage rationale")

body_cov = coverage_by_id[BODY]
body_cov["note"] = (
    "Printed p.275 body (PDF physical page 41) reviewed against the scan saved as p275_page_review_20261014.png; source SHA-256 "
    + EXPECTED_SHA256[SOURCE]
    + ". Restored 19 precise mentions and reviewed/classified all 13 existing body/continuation statements. Split the two façade targets from their church sites, mapping S. Canciano to the specific existing Church of San Canciano candidate and keeping its altar group separate from the p.274 Angeli works. S2 visual readings only: L81 Comer→Corner and Carita→Carità; L82 os→of, exfended→extended, 1778/→printed note marker 1; L83 eesere→essere. The source Markdown remains unchanged. Printed notes 1–2 are transcribed and linked in the consolidated notes segment; the cited works and letter were not independently consulted."
)

for row in new_statements:
    all_refs = {row.get("subject_candidate_id"), row.get("object_candidate_id"), *row["qualifiers"]["mentioned_candidate_ids"]} - {None}
    if not all_refs <= candidate_ids:
        raise SystemExit(f"unknown candidate FK in {row['statement_id']}: {sorted(all_refs - candidate_ids)}")
    if not row.get("original_quote") or not row.get("predicate"):
        raise SystemExit(f"incomplete new statement: {row['statement_id']}")

result = {
    "source": "p.275; PDF physical page 41",
    "mode": "planned; use --apply to write",
    "existing_statements_reviewed": len(EXPECTED_EXISTING_STATEMENTS),
    "new_statements": len(new_statements),
    "new_candidates": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(planned_mentions),
    "relation_candidate": {"true": sum(CLASSIFICATIONS.values()) + sum(row["qualifiers"]["relation_candidate"] for row in new_statements), "false": len(CLASSIFICATIONS) - sum(CLASSIFICATIONS.values()) + sum(not row["qualifiers"]["relation_candidate"] for row in new_statements), "unset": 0},
    "coverage": {"body": "reviewed/complete", "consolidated_notes": "reviewed/complete"},
    "planned_counts": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(planned_mentions),
        "statements": len(statements) + len(new_statements),
    },
    "table_sha256_before": {str(path.relative_to(ROOT)): expected for path, expected in EXPECTED_SHA256.items() if path.parent == TABLES},
}
print(json.dumps(result, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for src, dst in zip(paths, backups):
        shutil.copy2(src, dst)
    try:
        write_csv(candidate_path, candidate_fields, candidates + new_candidates)
        write_csv(mention_path, mention_fields, mentions + planned_mentions)
        write_jsonl(statement_path, statement_rows + new_statements)
        write_csv(coverage_path, coverage_fields, coverage)
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; backups=" + ", ".join(str(path.relative_to(ROOT)) for path in backups))
