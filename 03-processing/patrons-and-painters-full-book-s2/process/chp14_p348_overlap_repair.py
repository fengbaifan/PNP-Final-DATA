"""Repair duplicate p.348 pronoun spans assigned to two Algarotti index candidates."""
import argparse
import csv
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
EXPECTED = {
    "m-chp14-p348-0065": ("cand-0061", "he", 879, 881),
    "m-chp14-p348-0066": ("cand-0061", "he", 1015, 1017),
    "m-chp14-p348-0067": ("cand-0061", "he", 1098, 1100),
    "m-chp14-p348-0068": ("cand-0061", "he", 1125, 1127),
}
KEEP = {
    "m-chp14-p348-0071": ("cand-0050", "he", 879, 881),
    "m-chp14-p348-0072": ("cand-0050", "he", 1015, 1017),
    "m-chp14-p348-0073": ("cand-0050", "he", 1098, 1100),
    "m-chp14-p348-0074": ("cand-0050", "he", 1125, 1127),
}
BACKUP_SUFFIX = ".bak-s2-chp14-p348-overlap-fix-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

with TABLE.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
by_id = {r["mention_id"]: r for r in rows}
for mention_id, expected in {**EXPECTED, **KEEP}.items():
    if mention_id not in by_id:
        raise SystemExit(f"expected p.348 mention missing: {mention_id}")
    row = by_id[mention_id]
    actual = (row["candidate_id"], row["surface_form"], int(row["start_char"]), int(row["end_char"]))
    if actual != expected:
        raise SystemExit(f"unexpected mention state for {mention_id}: {actual}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment = "\n".join(source_lines[13:21])
for mention_id, (_, surface, start, end) in {**EXPECTED, **KEEP}.items():
    if segment[start:end] != surface:
        raise SystemExit(f"source span changed for {mention_id}")

print(f"mode={'apply' if args.apply else 'dry-run'} remove={len(EXPECTED)} keep={len(KEEP)}")
if args.apply:
    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
    shutil.copy2(TABLE, backup)
    new_rows = [r for r in rows if r["mention_id"] not in EXPECTED]
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(new_rows)
        tmp = Path(f.name)
    tmp.replace(TABLE)
