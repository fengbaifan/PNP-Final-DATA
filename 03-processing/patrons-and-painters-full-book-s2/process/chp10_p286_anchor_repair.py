"""Repair p.286 mention offsets and line spans found by the table audit."""
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "4690eee7aca37d3bf859d70d2adcd571b736e7b9b7c1a29611a334a7e23648a9"
SEG = "chp-10:10_CHP-10_intro:l190-204"
BACKUP = ".bak-s2-chp10-p286-anchorfix-20261002"

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[189:204])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEG_SHA:
    raise SystemExit("p.286 segment changed")

mentions_path = TABLES / "mentions.csv"
statements_path = TABLES / "book-statements.jsonl"
with mentions_path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    mention_fields = reader.fieldnames
    mentions = list(reader)
statements = [json.loads(line) for line in statements_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]

by_id = {row["mention_id"]: row for row in mentions}
duplicate_ids = ("m-chp10-p286-powis_house_2", "m-chp10-p286-powis_house_3")
if any(mid not in by_id for mid in duplicate_ids):
    raise SystemExit("expected duplicate Powis House mentions are missing")
if (by_id[duplicate_ids[0]]["candidate_id"], by_id[duplicate_ids[0]]["start_char"], by_id[duplicate_ids[0]]["end_char"]) != (
        by_id[duplicate_ids[1]]["candidate_id"], by_id[duplicate_ids[1]]["start_char"], by_id[duplicate_ids[1]]["end_char"]):
    raise SystemExit("Powis House mentions are not the exact duplicate found by audit")

style = by_id.get("m-chp10-p286-styles_spite")
if not style:
    raise SystemExit("Styles second mention is missing")
segment_offset = sum(len(source_lines[line - 1]) + 1 for line in range(190, 204))
second_styles = source_lines[203].find("Styles", source_lines[203].find("Styles") + 1)
if second_styles < 0:
    raise SystemExit("second Styles occurrence is missing from p.286 L204")
correct_style_span = (str(segment_offset + second_styles), str(segment_offset + second_styles + len("Styles")))

expected = {
    "st-chp10-p286-amigoni-arrival": (197, 197, 196, 197),
    "st-chp10-p286-powis-restoration-lords": (201, 201, 200, 201),
    "st-chp10-p286-styles-south-sea-fortune": (202, 202, 201, 202),
}
by_statement = {row["statement_id"]: row for row in statements}
for sid, (old_start, old_end, new_start, new_end) in expected.items():
    row = by_statement.get(sid)
    if not row:
        raise SystemExit(f"missing statement {sid}")
    qualifiers = row["qualifiers"]
    if (qualifiers["source_line_start"], qualifiers["source_line_end"]) != (old_start, old_end):
        raise SystemExit(f"unexpected current line range for {sid}: {qualifiers}")

fixed_mentions = [row for row in mentions if row["mention_id"] not in {duplicate_ids[0]}]
for row in fixed_mentions:
    if row["mention_id"] == "m-chp10-p286-styles_spite":
        row["start_char"], row["end_char"] = correct_style_span
for sid, (_, _, new_start, new_end) in expected.items():
    by_statement[sid]["qualifiers"]["source_line_start"] = new_start
    by_statement[sid]["qualifiers"]["source_line_end"] = new_end

print(json.dumps({"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "removed_duplicate_mention": duplicate_ids[0],
                  "moved_styles_mention_to_second_occurrence": correct_style_span,
                  "fixed_statement_line_ranges": {sid: [new[2], new[3]] for sid, new in expected.items()}},
                 ensure_ascii=False, indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (mentions_path, statements_path):
        backup_path = Path(str(path) + BACKUP)
        if backup_path.exists():
            raise SystemExit(f"backup already exists: {backup_path}")
        shutil.copy2(path, backup_path)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=mentions_path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(fixed_mentions)
        temporary = Path(stream.name)
    temporary.replace(mentions_path)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=statements_path.parent, delete=False) as stream:
        for row in statements:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(statements_path)
    print("Applied p.286 anchor repairs; source records and recovery copies retained.")
