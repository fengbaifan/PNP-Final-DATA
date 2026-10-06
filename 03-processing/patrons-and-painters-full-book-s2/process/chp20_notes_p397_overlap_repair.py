"""Remove duplicate exact-span person mentions from p.397 short citations."""
import argparse
import csv
import hashlib
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
REMOVE = {
    "m-s2-chp20-notes-p397-006",
    "m-s2-chp20-notes-p397-012",
    "m-s2-chp20-notes-p397-016",
    "m-s2-chp20-notes-p397-018",
    "m-s2-chp20-notes-p397-020",
    "m-s2-chp20-notes-p397-022",
}
BACKUP_SUFFIX = ".bak-s2-chp20-p397-overlap-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the exact-span overlap repair")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical postscript Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered postscript PDF changed")

path = TABLES / "mentions.csv"
with path.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
if len(rows) != 25743:
    raise SystemExit("unexpected mentions.csv pre-state")
by_id = {row["mention_id"]: row for row in rows}
if not REMOVE <= by_id.keys():
    raise SystemExit("expected duplicate person mentions are not all present")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_text = "\n".join(source_lines[210:280])
offset_by_line = {}
offset = 0
for number in range(211, 281):
    offset_by_line[number] = offset
    offset += len(source_lines[number - 1]) + 1

for mention_id in sorted(REMOVE):
    row = by_id[mention_id]
    if row["segment_id"] != NOTES:
        raise SystemExit(f"unexpected segment for {mention_id}")
    start, end = int(row["start_char"]), int(row["end_char"])
    if notes_text[start:end] != row["surface_form"]:
        raise SystemExit(f"source span mismatch for {mention_id}")
    same_span = [
        other for other in rows
        if other["segment_id"] == NOTES
        and other["mention_id"] != mention_id
        and int(other["start_char"]) == start
        and int(other["end_char"]) == end
    ]
    if len(same_span) != 1:
        raise SystemExit(f"expected one publication mention at identical span for {mention_id}: {same_span}")
    if same_span[0]["candidate_id"] == row["candidate_id"]:
        raise SystemExit(f"person and publication mentions are not distinct for {mention_id}")

out = [row for row in rows if row["mention_id"] not in REMOVE]
if len(out) != 25737:
    raise SystemExit("repair row count mismatch")
print("verified 6 exact-span author/citation overlaps; publication mentions and statement author links remain")
if not args.apply:
    print("dry-run only; pass --apply to write")
    raise SystemExit(0)

backup = path.with_name(path.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
backup.write_bytes(path.read_bytes())
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(out)
    temp = Path(stream.name)
temp.replace(path)
print(f"applied; removed 6 redundant exact-span mentions; backup={backup.name}")
