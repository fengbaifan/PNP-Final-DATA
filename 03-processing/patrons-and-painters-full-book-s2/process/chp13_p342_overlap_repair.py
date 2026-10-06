"""Remove duplicate same-span S2 mentions detected by the p.342 table audit."""
import argparse
import csv
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
BODY = "chp-13:13_CHP-13_intro:l98-105"
REMOVE_IDS = {"m-s2-ch13-p342-049", "m-s2-ch13-p342-050"}
BACKUP_SUFFIX = ".bak-s2-chp13-p342-overlap-fix-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the exact duplicate-span repair")
args = parser.parse_args()

with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
matches = [row for row in rows if row["mention_id"] in REMOVE_IDS]
if {row["mention_id"] for row in matches} != REMOVE_IDS:
    raise SystemExit("expected p.342 duplicate mentions were not found exactly")
if any(row["segment_id"] != BODY or row["surface_form"] != "those countries" for row in matches):
    raise SystemExit("duplicate mention identity differs from the reviewed repair target")
if len({(row["start_char"], row["end_char"]) for row in matches}) != 1:
    raise SystemExit("target mentions do not share the same span")
remaining = [row for row in rows if row["mention_id"] not in REMOVE_IDS]
print("repair dry-run: remove duplicate same-span anaphoric rows")
for row in matches:
    print(f"  {row['mention_id']} {row['candidate_id']} {row['surface_form']} [{row['start_char']}:{row['end_char']}]")
print(f"mentions: {len(rows)} -> {len(remaining)}")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"recovery copy already exists: {backup.name}")
shutil.copy2(MENTIONS, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=MENTIONS.parent, delete=False) as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(remaining)
    tmp = Path(f.name)
tmp.replace(MENTIONS)
print(f"applied; recovery copy created as {backup.name}")
