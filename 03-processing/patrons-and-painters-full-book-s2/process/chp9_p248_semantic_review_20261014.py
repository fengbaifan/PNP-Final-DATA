"""Controlled semantic repair for printed p.248 in the full-book S2 pass.

Default invocation is a read-only preflight.  Source OCR is never modified.
This restores source-verified mentions from a pinned prior table and resolves
the six open statement classifications while refining three compound claims.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l38-46"
BASELINE_REV = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_SEGMENT_HASH = "353c3cfd37cc305ef624b371deb6b4e2a7cabf9c6a58bafa8e0269316329ba46"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p248-semantic-review-20261014"


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
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segment_rows = read_jsonl(TABLES / "segments.jsonl")
segment = next((row for row in segment_rows if row["segment_id"] == SEGMENT_ID), None)
if segment is None:
    raise SystemExit(f"missing segment metadata: {SEGMENT_ID}")
if segment["sha256"] != EXPECTED_SEGMENT_HASH or segment["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("p.248 source hashes changed; inspect before repair")
source_asset = ROOT / segment["source_file"]
if hashlib.sha256(source_asset.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
selected_lines = source_lines[segment["line_start"] - 1:segment["line_end"]]
if hashlib.sha256("\n".join(selected_lines).encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_HASH:
    raise SystemExit("p.248 segment content hash changed")
line_offsets = {}
offset = 0
for line_number, line in zip(range(segment["line_start"], segment["line_end"] + 1), selected_lines):
    line_offsets[line_number] = offset
    offset += len(line) + 1
segment_text = "\n".join(selected_lines)

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
_, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
statement_rows = read_jsonl(statement_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
coverage = coverage_by_id.get(SEGMENT_ID)
if not coverage or (coverage["disposition"], coverage["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit(f"unexpected p.248 coverage: {coverage}")

expected_existing_ids = {
    "st-chp9-p248-aristocratic-patronage-state", "st-chp9-p248-canvas-homage",
    "st-chp9-p248-collections-after-nobility", "st-chp9-p248-facade-design-and-building",
    "st-chp9-p248-facade-iconographic-program", "st-chp9-p248-facade-place-plans-and-ambassador",
    "st-chp9-p248-maffei-governor-canvases", "st-chp9-p248-palace-commemorations",
    "st-chp9-p248-patricians-praised-as-patrons", "st-chp9-p248-patronage-not-appreciation",
    "st-chp9-p248-shift-to-individual", "st-chp9-p248-veronese-tintoretto-venice",
    "st-chp9-p248-votive-pictures",
}
target_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if {row["statement_id"] for row in target_rows} != expected_existing_ids:
    raise SystemExit("p.248 statement inventory changed; inspect before repair")
unset_ids = {
    "st-chp9-p248-aristocratic-patronage-state", "st-chp9-p248-facade-iconographic-program",
    "st-chp9-p248-patricians-praised-as-patrons", "st-chp9-p248-patronage-not-appreciation",
    "st-chp9-p248-shift-to-individual", "st-chp9-p248-votive-pictures",
}
if any(statement_by_id[sid].get("qualifiers", {}).get("relation_candidate") is not None for sid in unset_ids):
    raise SystemExit("p.248 classification pre-state changed; inspect before repair")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("p.248 already has current mentions; inspect instead of duplicating")

baseline_text = subprocess.check_output(
    ["git", "show", f"{BASELINE_REV}:04-knowledge/tables/mentions.csv"],
    cwd=ROOT, text=True, encoding="utf-8",
)
baseline_mentions = list(csv.DictReader(io.StringIO(baseline_text)))
restored_mentions = [row for row in baseline_mentions if row["segment_id"] == SEGMENT_ID]
if len(restored_mentions) != 57:
    raise SystemExit(f"pinned baseline has {len(restored_mentions)} p.248 mentions, expected 57")
for row in restored_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"restored mention has missing candidate: {row['mention_id']}")
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"restored mention span differs from S0: {row['mention_id']}")
    if row["mention_id"] in mention_ids:
        raise SystemExit(f"mention ID already exists: {row['mention_id']}")


def quote_lines(first: int, last: int | None = None):
    last = first if last is None else last
    return "\n".join(source_lines[first - 1:last])


def update(statement_id: str, *, subject: str | None, object_: str | None, predicate: str,
           claim: str, qualification: str, mentioned: list[str], relation: bool,
           first: int, last: int | None = None, quote: str | None = None):
    row = statement_by_id[statement_id]
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers.update({
        "source_line_start": first,
        "source_line_end": first if last is None else last,
        "printed_page": 248,
        "pdf_physical_page": 6,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "semantic_review": "2026-10-14 source-order review; statement scope and endpoint mappings checked",
    })
    row["original_quote"] = quote_lines(first, last) if quote is None else quote


update(
    "st-chp9-p248-aristocratic-patronage-state", subject="cand-2720", object_="cand-2734",
    predicate="venetian_patronage_and_government_were_aristocratic_with_state_aristocracy_identification",
    claim="Haskell says Venetian patronage and government had long been aristocratic and that the identification of aristocracy and State was absolute.",
    qualification="This is Haskell's interpretive generalization, not a constitutional formula quoted from a statute.",
    mentioned=["cand-2720", "cand-8108", "cand-8105", "cand-2734"], relation=True, first=39,
)
update(
    "st-chp9-p248-facade-iconographic-program", subject="cand-8153", object_=None,
    predicate="façade_program_described_heraldic_figural_and_allegorical_elements",
    claim="Haskell describes the façade's Glory figure, Barbaro arms, cardinal virtues, central Antonio figure and funerary urn, statues of Honour and Virtue, Fame and Wisdom, and four brothers on the lower storey.",
    qualification="This is a descriptive inventory of the façade's iconographic program; preserve each named or independently scoped element as a mention without converting the whole inventory into one relation edge.",
    mentioned=["cand-8153", "cand-8162", "cand-8161", "cand-5174", "cand-0185", "cand-8166", "cand-8164", "cand-8165", "cand-8163"],
    relation=False, first=44, last=45,
)
line46_correction = {
    "source_line": 46,
    "ocr": "Antonio' Barbaro’s",
    "print": "Antonio Barbaro’s",
    "basis": "CHP-9.pdf physical page 6",
}
statement_by_id["st-chp9-p248-facade-iconographic-program"]["qualifiers"].pop("ocr_corrections", None)
cross_page_statement = statement_by_id.get("st-chp9-p249-tempio-comparison")
if not cross_page_statement or cross_page_statement.get("qualifiers", {}).get("continued_from_source_line") != 46:
    raise SystemExit("missing p.249 statement for p.248 L46 continuation")
corrections = cross_page_statement.setdefault("qualifiers", {}).setdefault("ocr_corrections", [])
if line46_correction not in corrections:
    corrections.append(line46_correction)
update(
    "st-chp9-p248-facade-design-and-building", subject="cand-8153", object_="cand-0185",
    predicate="designed_by_antonio_barbaro_as_apotheosis_of_himself_and_his_brothers",
    claim="Haskell says Antonio Barbaro designed the S. Maria del Giglio façade as an apotheosis of himself and his brothers.",
    qualification="The design attribution is Haskell's account; note 4 points to Barbaro's will but does not independently establish authorship. The separate builder and war facts are split into their own statements.",
    mentioned=["cand-8153", "cand-0736", "cand-0185", "cand-8163"], relation=True, first=42, last=43,
)
update(
    "st-chp9-p248-facade-place-plans-and-ambassador", subject="cand-8153", object_=None,
    predicate="pedestals_displayed_plans_of_candia_corfu_spalato_zara_padua_and_rome",
    claim="Haskell says the pedestals beneath the brothers displayed plans of Candia, Corfu, Spalato, Zara, Padua, and Rome.",
    qualification="The places are the subjects of displayed plans; the following clause separately identifies Rome as the place of Antonio's ambassadorial service.",
    mentioned=["cand-8153", "cand-8163", "cand-8155", "cand-8118", "cand-8159", "cand-8160", "cand-1803", "cand-4490"],
    relation=True, first=45,
    quote=source_lines[44][source_lines[44].find("on the pedestals"):source_lines[44].find("Rome", source_lines[44].find("on the pedestals")) + len("Rome")],
)
update(
    "st-chp9-p248-patricians-praised-as-patrons", subject="cand-8109", object_="cand-8149",
    predicate="publishers_and_printsellers_acclaimed_patricians_as_glorious_patrons",
    claim="Haskell says few patricians escaped being acclaimed as glorious patrons by obsequious publishers or printsellers, a tribute rarely paid to non-nobles.",
    qualification="This is a broad authorial comparison with a collective publisher group; no individual publisher, patrician, or commission is named.",
    mentioned=["cand-8109", "cand-8149", "cand-8167"], relation=True, first=39,
)
update(
    "st-chp9-p248-patronage-not-appreciation", subject="cand-2720", object_=None,
    predicate="patronage_could_have_little_to_do_with_appreciation_or_understanding",
    claim="Completing p.247 L31, Haskell says aristocratic patronage could often have little to do with appreciation or understanding.",
    qualification="This is a general authorial judgement about motive, not a relation to a named person or object; it remains linked to the p.247 sentence it completes.",
    mentioned=["cand-2720", "cand-8124"], relation=False, first=39,
)
update(
    "st-chp9-p248-shift-to-individual", subject="cand-2721", object_="cand-8105",
    predicate="seventeenth_century_attention_shifted_toward_individual_glorification_at_state_or_gods_expense",
    claim="Haskell describes a seventeenth-century shift of attention toward the individual at the expense of the State or God.",
    qualification="This is a broad interpretive periodization rather than a single dated commission; the source names no individual recipient.",
    mentioned=["cand-2721", "cand-8105", "cand-8108"], relation=True, first=41,
)
update(
    "st-chp9-p248-votive-pictures", subject="cand-8148", object_="cand-8168",
    predicate="votive_pictures_placed_noble_patrons_almost_equal_to_divine_protectors",
    claim="Haskell says large votive pictures that became prominent in the second half of the sixteenth century showed noble patrons on almost equal terms with their divine protectors.",
    qualification="The class of pictures is not an individual work; preserve the author's approximate chronology and comparison.",
    mentioned=["cand-8148", "cand-8108", "cand-8168"], relation=True, first=39,
)

line45 = source_lines[44]
rome_where = line45.find("Rome, where")
if rome_where < 0 or not source_lines[45].startswith("Antonio had served as ambassador"):
    raise SystemExit("could not isolate the Rome ambassador clause across p.248 lines 45-46")
ambassador_quote = line45[rome_where:] + "\n" + source_lines[45][:len("Antonio had served as ambassador.")]

new_statements = [
    {
        "statement_id": "st-chp9-p248-facade-erected-by-sardi",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-8153",
        "object_candidate_id": "cand-2360",
        "predicate": "erected_by_giuseppe_sardi_between_1675_and_1683",
        "qualifiers": {
            "source_line_start": 43, "source_line_end": 43, "printed_page": 248, "pdf_physical_page": 6,
            "claim": "Haskell says Giuseppe Sardi erected the façade between 1675 and 1683.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "The source gives an interval, not a single construction date.",
            "time": "between 1675 and 1683",
            "mentioned_candidate_ids": ["cand-8153", "cand-2360"],
            "relation_candidate": True,
            "semantic_review": "2026-10-14 source-order review; builder claim separated from designer attribution",
        },
        "original_quote": "which was erected by Giuseppe Sardi between 1675 and 1683",
        "origin": "book", "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    },
    {
        "statement_id": "st-chp9-p248-barbaro-fought-war-of-candia",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0185",
        "object_candidate_id": "cand-8154",
        "predicate": "fought_in_war_of_candia",
        "qualifiers": {
            "source_line_start": 43, "source_line_end": 43, "printed_page": 248, "pdf_physical_page": 6,
            "claim": "Haskell says Antonio Barbaro had fought in the War of Candia.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "The passage gives no campaign date or additional service detail.",
            "mentioned_candidate_ids": ["cand-0185", "cand-8154"],
            "relation_candidate": True,
            "semantic_review": "2026-10-14 source-order review; war participation separated from façade design",
        },
        "original_quote": "Antonio Barbaro, who had fought in the war of Candia",
        "origin": "book", "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    },
    {
        "statement_id": "st-chp9-p248-antonio-ambassador-in-rome",
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0185",
        "object_candidate_id": "cand-4490",
        "predicate": "served_as_ambassador_in_rome",
        "qualifiers": {
            "source_line_start": 45, "source_line_end": 46, "printed_page": 248, "pdf_physical_page": 6,
            "claim": "Haskell says Antonio Barbaro had served as ambassador in Rome.",
            "speaker": "Haskell", "text_layer": "body",
            "qualification": "The grammar links ambassadorial service to Rome only, not to all six places whose plans appeared on the façade.",
            "role": "ambassador", "mentioned_candidate_ids": ["cand-0185", "cand-4490"],
            "relation_candidate": True,
            "semantic_review": "2026-10-14 source-order review; role and place scope separated from façade plan list",
        },
        "original_quote": ambassador_quote,
        "origin": "book", "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    },
]

if len({row["statement_id"] for row in new_statements}) != len(new_statements):
    raise SystemExit("duplicate new statement IDs in plan")
for row in new_statements:
    if row["statement_id"] in statement_ids:
        raise SystemExit(f"new statement ID already exists: {row['statement_id']}")
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"new statement has missing candidate: {row['statement_id']} {candidate_id}")
    if row["original_quote"] not in "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"new statement quote is not reproduced by its source lines: {row['statement_id']}")

mention_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
for row in restored_mentions:
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in mention_spans:
        raise SystemExit(f"p.248 mention span already exists: {row['mention_id']}")
    mention_spans.add(span)
mention_rows.extend(restored_mentions)
statement_rows.extend(new_statements)
coverage["note"] = (
    "Printed p.248 reviewed against CHP-9.pdf physical p.6. The paragraph from p.247 L31 closes at L39; "
    "the façade description continues at p.249 L78, and the cross-page relation is preserved in book-statements. "
    "Page-note markers 1-4 link to consolidated notes L335-338. This repair restored and span-checked 57 baseline mentions, "
    "corrected the publisher endpoint, and split façade design, construction, War of Candia participation, and Rome ambassadorial service. "
    "The Antonio Barbaro OCR correction at L46 is attached to its p.249 continuation statement."
)

final_target = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if len(final_target) != 16 or any(row.get("qualifiers", {}).get("relation_candidate") is None for row in final_target):
    raise SystemExit("post-plan p.248 inventory/classification check failed")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.248 S2 repair")
args = parser.parse_args()
print(json.dumps({
    "segment_id": SEGMENT_ID,
    "baseline_revision": BASELINE_REV,
    "source_segment_sha256": segment["sha256"],
    "existing_statements_classified": len(expected_existing_ids),
    "new_atomic_statements": len(new_statements),
    "p248_statements_after": len(final_target),
    "restored_baseline_mentions": len(restored_mentions),
    "p248_mentions_after": len(restored_mentions),
    "no_new_candidates": True,
}, ensure_ascii=False, indent=2))
if not args.apply:
    print("DRY RUN: no files changed")
else:
    paths = [mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; inspect before applying: {backup}")
        shutil.copy2(path, backup)
        backups.append(backup)
    write_csv_atomic(mention_path, mention_fields, mention_rows)
    write_jsonl_atomic(statement_path, statement_rows)
    write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
    print("applied; backups=" + ", ".join(path.name for path in backups))
