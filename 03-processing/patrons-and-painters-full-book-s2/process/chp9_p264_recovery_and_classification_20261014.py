"""Reconcile p.264 source mentions and finish its unset S2 classifications.

Defaults to a read-only preflight. Printed p.264 and its footnotes were
reviewed against CHP-9.pdf physical page 26. Mention specifications from the
older p.263-p.264 migration are read as data only; this script does not run it.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
LEGACY_SPEC = PROCESS / "chp9_p263_p264_migration.py"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"

P263 = "chp-9:09_CHP-9_intro:l231-238"
P264 = "chp-9:09_CHP-9_intro:l240-249"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
SEGMENT_HASHES = {
    P264: "355313d4c69e00f29306b9e6a740b06e817202f3d37621ce1724718501862751",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
EXPECTED_HASHES = {
    MENTIONS: "924e91225b11dc341facb726de7b60b5f1966d9237cdb1f64edac39eea719691",
    STATEMENTS: "32e4f9728564a814c737a899a863cd186ce78d5396c5ca94b0a8ed444f4ee22e",
    COVERAGE: "3a34914051039732f229bebeffee2a4a9207b37bc97ff1f242a337e9c5ab870a",
    CANDIDATES: "80b34fbf58fe9f0436184452b52a1656f29b40faa3cd5fc6488779d5bd8c642b",
    SOURCE: "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    LEGACY_SPEC: "f917d572ed0ffbbc026d9f7f580d8ef64e023592b8a4e6a1522c6eecc3442eab",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p264-reconciliation-20261014"

CLASSIFICATIONS = {
    "st-chp9-p263264-baldinucci-borgognone-locator": False,
    "st-chp9-p263264-direct-acquisition-limit-partial": True,
    "st-chp9-p263264-gherardo-death-and-dispersal": True,
    "st-chp9-p263264-inventory-1738-locator": False,
    "st-chp9-p263264-posse-complete-sale-report": True,
    "st-chp9-p263264-udney-1762-list": True,
    "st-chp9-p263264-walpole-proposed-sale": False,
}
REASONS = {
    "st-chp9-p263264-baldinucci-borgognone-locator": (
        "S2: this is a bibliographic locator for Baldinucci; the cited text was not independently consulted."
    ),
    "st-chp9-p263264-direct-acquisition-limit-partial": (
        "S2: Haskell cautiously limits certain direct acquisitions to inventory pictures dated 1685-1729; "
        "retain this acquisition claim while keeping the works unidentified and linking the unfinished note "
        "to its p.265 continuation. The cited inventories were not independently consulted."
    ),
    "st-chp9-p263264-gherardo-death-and-dispersal": (
        "S2: this gives an explicit chronology and says plans to disperse the collection began after Gherardo's "
        "death; retain the reported age and year, and distinguish an initial plan from the later piecemeal sale."
    ),
    "st-chp9-p263264-inventory-1738-locator": (
        "S2: the note locates a 1738 inventory but does not identify the Procuratore Sagredo; do not equate it "
        "with Zaccaria's or Gherardo's personal collection."
    ),
    "st-chp9-p263264-posse-complete-sale-report": (
        "S2: Posse's letter reports an intended July 1743 sale of the pictures as a complete collection; "
        "retain it as a reported plan, not a completed transaction or identified buyer."
    ),
    "st-chp9-p263264-udney-1762-list": (
        "S2: the 1762 archival list describes pictures sought by the English consul; retain the attributed "
        "request relation, but do not infer that Udney completed a purchase."
    ),
    "st-chp9-p263264-walpole-proposed-sale": (
        "S2: this is a citation locator for Walpole's account; the cited text was not independently consulted "
        "and the note adds no separate relation."
    ),
}
EXPECTED_GLOBAL_BEFORE = {True: 9665, False: 3992, None: 1172}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(f.name)
    temp_path.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(f.name)
    temp_path.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"fingerprint changed; inspect before continuing: {path.relative_to(ROOT)}")

segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
for sid, expected in SEGMENT_HASHES.items():
    if sid not in segments or segments[sid]["sha256"] != expected:
        raise SystemExit(f"unexpected source segment: {sid}")
    if segments[sid]["asset_sha256"] != EXPECTED_HASHES[SOURCE]:
        raise SystemExit(f"unexpected source asset reference: {sid}")


class _ReplaceSegmentNames(ast.NodeTransformer):
    def visit_Name(self, node):
        values = {"P263": P263, "P264": P264, "NOTES": NOTES}
        if node.id in values:
            return ast.copy_location(ast.Constant(values[node.id]), node)
        return node


legacy_tree = ast.parse(LEGACY_SPEC.read_text(encoding="utf-8-sig"))
legacy_specs = None
for node in legacy_tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "M" for t in node.targets):
        legacy_specs = ast.literal_eval(_ReplaceSegmentNames().visit(node.value))
        break
if legacy_specs is None or len(legacy_specs) != 75:
    raise SystemExit("legacy mention specification changed; inspect before continuing")
legacy_specs = [
    spec for spec in legacy_specs
    if spec[0] == P264 or (spec[0] == NOTES and 420 <= spec[1] <= 427)
]
if len(legacy_specs) != 31:
    raise SystemExit(f"expected 31 p.264 base mentions, found {len(legacy_specs)}")
manual_specs = [
    (P264, 245, "will-tomaso", "cand-2357", "Tomaso de Santi",
     "Named testamentary custodian; the source spelling is retained."),
    (P264, 246, "will-girardo", "cand-2326", "Girardo P.O Sagredio",
     "Named nephew in the quoted will; spelling-to-index identity remains for S3 review."),
    (P264, 247, "will-rubens", "cand-2293", "Rubens",
     "Artist named in the reported bequest; no individual work title is supplied."),
    (P264, 247, "will-moron", "cand-1704", "Moron",
     "OCR spelling in the bequest; mapped to the existing Moroni candidate, pending S3 identity review."),
    (P264, 247, "will-varda", "cand-2700", "Salvator Varda",
     "Named recipient of the reported bequest; identity is not independently verified."),
    (NOTES, 427, "direct-acquisition-zaccaria", "cand-2329", "Zaccaria",
     "Named subject of p.264 note 8's partial direct-acquisition qualification."),
]
mention_specs = legacy_specs + manual_specs
if len(mention_specs) != 37:
    raise SystemExit(f"expected 37 p.264 mentions including the will continuation, found {len(mention_specs)}")

_, candidate_rows = read_csv(CANDIDATES)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, current_mentions = read_csv(MENTIONS)
coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
statement_rows = read_jsonl(STATEMENTS)
statement_by_id = {row["statement_id"]: row for row in statement_rows}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()

existing_ids = {row["mention_id"] for row in current_mentions}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in current_mentions}
new_mentions = []
for segment_id, line, suffix, candidate_id, surface, note, *optional in mention_specs:
    if segment_id not in (P264, NOTES) or candidate_id not in candidate_ids:
        raise SystemExit(f"missing segment or candidate in mention spec: {suffix}")
    line_text = source_lines[line - 1]
    pos, actual_surface = line_text.find(surface), surface
    if pos < 0 and "\ufffd" in surface:
        parts = re.split("\ufffd+", surface)
        pattern = "".join(re.escape(part) + (r"\S" if i < len(parts) - 1 else "")
                          for i, part in enumerate(parts))
        match = re.search(pattern, line_text)
        if match:
            pos, actual_surface = match.start(), match.group(0)
    if pos < 0:
        raise SystemExit(f"source text does not contain mention spec: line {line}, {surface!r}")
    meta = segments[segment_id]
    segment_offset = sum(len(source_lines[n - 1]) + 1 for n in range(meta["line_start"], line))
    start, end = segment_offset + pos, segment_offset + pos + len(actual_surface)
    mention_id = f"m-chp9-p263264-{suffix}"
    span = (segment_id, str(start), str(end))
    if mention_id in existing_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention id: {mention_id}")
    if span in existing_spans or any(
        (row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention span: {mention_id}")
    segment_text = "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])
    if segment_text[start:end] != actual_surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": actual_surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

unset_ids = {
    row["statement_id"] for row in statement_rows
    if row["statement_id"].startswith("st-chp9-p263264-")
    and row.get("qualifiers", {}).get("printed_page") == 264
    and row.get("qualifiers", {}).get("relation_candidate") is None
}
if unset_ids != set(CLASSIFICATIONS):
    raise SystemExit(f"unexpected p.264 unset classifications: {sorted(unset_ids)}")
if set(CLASSIFICATIONS) != set(REASONS):
    raise SystemExit("classification reasons do not match the decision set")
for statement_id, value in CLASSIFICATIONS.items():
    qualifiers = statement_by_id[statement_id]["qualifiers"]
    if qualifiers.get("relation_candidate") is not None:
        raise SystemExit(f"statement is no longer unset: {statement_id}")
    qualifiers["relation_candidate"] = value
    reason = REASONS[statement_id]
    qualification = qualifiers.get("qualification", "").strip()
    if reason not in qualification:
        qualifiers["qualification"] = (qualification + " " + reason).strip()

before = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in read_jsonl(STATEMENTS))
after = Counter(row.get("qualifiers", {}).get("relation_candidate") for row in statement_rows)
if dict(before) != EXPECTED_GLOBAL_BEFORE:
    raise SystemExit(f"unexpected global classification baseline: {dict(before)}")
if after[True] != before[True] + 4 or after[False] != before[False] + 3 or after[None] != before[None] - 7:
    raise SystemExit(f"unexpected classification delta: before={dict(before)}, after={dict(after)}")

for sid in (P264, NOTES):
    if sid not in coverage_by_id or coverage_by_id[sid]["migration_status"] != "complete":
        raise SystemExit(f"unexpected S2 coverage state for {sid}")
coverage_by_id[P264]["note"] += (
    " 2026-10-14 reconciliation restored 17 body mentions, 15 p.264 note mentions and 5 mentions in the "
    "p.263 note 6 continuation; seven previously unset relation_candidate fields were reviewed (4 true, 3 false)."
)
coverage_by_id[NOTES]["note"] += (
    " 2026-10-14 reconciliation restored 15 p.264 note mentions and verified the p.263 note 6 continuation "
    "spans against p.264 OCR."
)

summary = {
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "printed_page": 264,
    "pdf_physical_page": 26,
    "recovered_mentions": len(new_mentions),
    "mention_distribution": dict(Counter(row["segment_id"] for row in new_mentions)),
    "mention_line_distribution": dict(Counter(str(spec[1]) for spec in mention_specs)),
    "classified_statements": {"true": 4, "false": 3, "unset_closed": 7},
    "global_statements": len(statement_rows),
    "global_classifications_after": {"true": after[True], "false": after[False], "unset": after[None]},
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write verified p.264 mention and classification updates")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, STATEMENTS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more p.264 reconciliation backups already exist")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    try:
        write_csv(MENTIONS, mention_fields, current_mentions + new_mentions)
        write_jsonl(STATEMENTS, statement_rows)
        write_csv(COVERAGE, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; recovery backups: " + ", ".join(path.name for path in backups))
