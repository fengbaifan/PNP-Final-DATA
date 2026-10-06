"""Include the page-bottom footnote line in p.363's reviewed source range; dry-run by default."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "04-knowledge" / "tables" / "s2-coverage.csv"
SEGMENT = "chp-15:15_CHP-15_sec_i:l27-36"
BACKUP_SUFFIX = ".bak-s2-chp15-p363-coverage-l36-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

with PATH.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, rows = reader.fieldnames, list(reader)
matches = [row for row in rows if row["segment_id"] == SEGMENT]
if len(matches) != 1:
    raise SystemExit(f"expected one p.363 body coverage row, got {len(matches)}")
row = matches[0]
if row["migration_status"] != "partial" or row["source_line_ranges"] != "L27-35; L36 (footnote 2)":
    raise SystemExit("unexpected p.363 coverage state")
row["source_line_ranges"] = "L27-36"
row["note"] = (
    "Printed p.363 checked against CHP-15.pdf physical p.3. Semantic body lines are L27-35; OCR line L36 is the page’s footnote 2, "
    "linked to the L28 quotation. Records Farsetti’s villa, gardens, patronage, Canova, illness and Daniele. OCR corrections are recorded only in S2. "
    "L35 ends ‘continued the’ and resumes at p.364 L39; this body segment remains partial."
)
result = {"mode": "apply" if args.apply else "dry-run", "segment_id": SEGMENT,
          "source_line_ranges": row["source_line_ranges"], "footnote2_line": 36}
if args.apply:
    backup = PATH.with_name(PATH.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(PATH, backup)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=PATH.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(PATH)
print(json.dumps(result, ensure_ascii=False, indent=2))
