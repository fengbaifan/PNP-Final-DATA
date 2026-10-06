"""Correct p.324-325 note mention offsets to the full consolidated segment frame."""
import argparse
import csv
import hashlib
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
BACKUP_SUFFIX = ".bak-s2-chp10-p324-325-note-offset-fix-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="repair the 21 note mention offsets after saving a recovery copy")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical source markdown changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
full_note_text = "\n".join(source_lines[272:349])
offset = sum(len(source_lines[index]) + 1 for index in range(272, 324))

path = TABLES / "mentions.csv"
with path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
if len(rows) != 20725:
    raise SystemExit(f"unexpected mention table size: {len(rows)}")
targets = [row for row in rows if row["segment_id"] == NOTES and row["mention_id"].startswith("m-s2-ch10-p325-")]
if len(targets) != 21:
    raise SystemExit(f"expected 21 p.324-325 note mentions; found {len(targets)}")
for row in targets:
    old_start = int(row["start_char"])
    old_end = int(row["end_char"])
    surface = row["surface_form"]
    if full_note_text[old_start:old_end] == surface:
        raise SystemExit(f"mention already has full-segment offsets: {row['mention_id']}")
    new_start = old_start + offset
    new_end = old_end + offset
    if full_note_text[new_start:new_end] != surface:
        raise SystemExit(f"corrected span does not match source: {row['mention_id']}")

print(f"preview: {len(targets)} offsets shifted by {offset} characters; all surfaces match full note segment")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup = path.with_name(path.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"backup already exists: {backup.name}")
shutil.copy2(path, backup)
for row in targets:
    row["start_char"] = str(int(row["start_char"]) + offset)
    row["end_char"] = str(int(row["end_char"]) + offset)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    temporary = Path(stream.name)
temporary.replace(path)
print(f"applied; recovery copy: {backup.name}")
