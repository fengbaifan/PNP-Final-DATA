"""Remove the duplicate exact-span Sensier person mention from p.284 note 3."""
import argparse
import csv
import hashlib
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_LINE_SHA = "ca8e1a9485c4da58c1b161645bc2351ee69ff50e19248f679a300c9f4be1ab01"
REMOVE_ID = "m-chp10-p284notes-sensier-crozat-author"
KEEP_ID = "m-chp10-p284notes-sensier-crozat-source"
BACKUP = ".bak-s2-chp10-p284-mention-overlap-fix-20261002"

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256("\n".join(src[523:527]).encode("utf-8")).hexdigest() != EXPECTED_LINE_SHA:
    raise SystemExit("p.284 notes 1-5 changed")
if "Sensier" not in src[525]:
    raise SystemExit("expected citation author is absent")

with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
remove_rows = [row for row in rows if row["mention_id"] == REMOVE_ID]
keep_rows = [row for row in rows if row["mention_id"] == KEEP_ID]
if len(remove_rows) != 1 or len(keep_rows) != 1:
    raise SystemExit("expected duplicate/retained mention row count changed")
removed, kept = remove_rows[0], keep_rows[0]
for field in ("segment_id", "surface_form", "start_char", "end_char"):
    if removed[field] != kept[field]:
        raise SystemExit(f"mentions do not occupy the same source span: {field}")
if removed["surface_form"] != "Sensier" or removed["segment_id"] != "chp-10:10_CHP-10_intro:l491-634":
    raise SystemExit("duplicate mention no longer matches the expected source span")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="remove the duplicate exact-span row")
args = parser.parse_args()
print(f"confirmed exact-span duplicate: {REMOVE_ID} overlaps {KEEP_ID} at {removed['start_char']}:{removed['end_char']}")
print("keeping the archive citation mention; removing only the duplicate person-label span")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup = MENTIONS.with_name(MENTIONS.name + BACKUP)
if backup.exists():
    raise SystemExit(f"backup already exists: {backup}")
shutil.copy2(MENTIONS, backup)
remaining = [row for row in rows if row["mention_id"] != REMOVE_ID]
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=MENTIONS.parent, delete=False) as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(remaining)
    temporary = Path(stream.name)
temporary.replace(MENTIONS)
print(f"applied; recovery copy: {backup.name}")
