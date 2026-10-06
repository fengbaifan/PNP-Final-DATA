"""Close p.302-306 S2 coverage after the processed next-page passages resolve."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
BACKUP_SUFFIX = ".bak-s2-chp10-crosspage-close-20261002"

PAIRS = [
    ("chp-10:10_CHP-10_intro:l391-400", "st-chp10-p302-smith-ricci-acquisition-hypothesis",
     "st-chp10-p303-ricci-studio-acquisition", "chp-10:10_CHP-10_intro:l402-409",
     "L391-399", "P.302's final Ricci claim closes at p.303 L403; both statements cross-reference the adjacent source segment."),
    ("chp-10:10_CHP-10_intro:l402-409", "st-chp10-p303-smith-age-palazzo-balbi",
     "st-chp10-p304-smith-settled-palazzo", "chp-10:10_CHP-10_intro:l411-421",
     "L403-409", "P.303's final location clause closes at p.304 L412; both statements cross-reference the adjacent source segment. Notes excerpt at L409 is separately represented in the consolidated notes segment."),
    ("chp-10:10_CHP-10_intro:l411-421", "st-chp10-p304-smith-held-canalettos-versus-royal",
     "st-chp10-p305-tessin-observation-close", "chp-10:10_CHP-10_intro:l423-433",
     "L412-421", "P.304's final clause closes at p.305 L424; both statements cross-reference the adjacent source segment."),
    ("chp-10:10_CHP-10_intro:l423-433", "st-chp10-p305-later-groups-style-comparison",
     "st-chp10-p306-canaletto-spoilt-style", "chp-10:10_CHP-10_intro:l435-443",
     "L424-433", "P.305's final style comparison closes at p.306 L436; both statements cross-reference the adjacent source segment. Printed p.305 note 1 is linked to L611."),
    ("chp-10:10_CHP-10_intro:l435-443", "st-chp10-p306-breval-statuette",
     "st-chp10-p307-breval-statuette-continuation", "chp-10:10_CHP-10_intro:l445-454",
     "L436-443", "P.306's Breval statuette passage closes at p.307 L446; both statements cross-reference the adjacent source segment. P.306 notes are linked."),
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

coverage_path = TABLES / "s2-coverage.csv"
statements_path = TABLES / "book-statements.jsonl"
fields, rows = read_csv(coverage_path)
coverage = {row["segment_id"]: row for row in rows}
statements = [json.loads(line) for line in statements_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_sid = {row["statement_id"]: row for row in statements}

for segment_id, left_id, right_id, next_segment, ranges, note in PAIRS:
    row = coverage.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != ("reviewed", "partial", ranges):
        raise SystemExit(f"coverage precondition changed: {segment_id}: {row}")
    left = by_sid.get(left_id)
    right = by_sid.get(right_id)
    if not left or not right:
        raise SystemExit(f"missing cross-page statement pair: {left_id}, {right_id}")
    left_q = left.get("qualifiers", {})
    right_q = right.get("qualifiers", {})
    if next_segment not in left_q.get("cross_reference_segments", []):
        raise SystemExit(f"left statement no longer points forward: {left_id}")
    if segment_id not in right_q.get("cross_reference_segments", []):
        raise SystemExit(f"right statement no longer points back: {right_id}")
    if left["segment_id"] != segment_id or right["segment_id"] != next_segment:
        raise SystemExit(f"statement segment mapping changed: {left_id}, {right_id}")
    row.update({"disposition": "reviewed", "migration_status": "complete", "note": note})

print(json.dumps({"mode": "APPLY" if args.apply else "DRY-RUN",
                  "segments_closed": [entry[0] for entry in PAIRS],
                  "reason": "all adjacent continuation statements are present and cross-linked"},
                 ensure_ascii=True, indent=2))
if args.apply:
    backup = Path(str(coverage_path) + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(coverage_path, backup)
    write_csv(coverage_path, fields, [coverage[row["segment_id"]] for row in rows])
    print(f"Applied with recoverable backup: {backup.name}")
