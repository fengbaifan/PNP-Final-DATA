"""Restore p.311 coverage evidence and record the p.312 continuation; dry-run by default."""
import argparse
import csv
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "04-knowledge" / "tables" / "s2-coverage.csv"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l7-15"
BACKUP_SUFFIX = ".bak-s2-chp10-p312-coverage-note-fix-20261003"
CURRENT_NOTE = (
    "Printed p.311 sentence now closes at p.312 L18; p.311 footnotes 1-5 remain pending in canonical note block L274-278. "
    "The page-level note numbering is checked against print."
)
RESTORED_NOTE = (
    "Printed p.311 body checked against CHP-10.pdf physical page 40. The source marker [Page 1661] is inconsistent with "
    "the printed page; scan confirms p.311. S2 records OCR corrections 'scries'→'series', 'I747?'→1747 with marker 3, "
    "and 'claps'→'clapt' without altering S0. Sentence at L15 continues at L18 on p.312; body footnote markers 1–6 "
    "point to the later notes block and remain pending. Printed p.311 sentence now closes at p.312 L18. Footnotes 1–6 "
    "remain pending in canonical note block L274-278; print confirms a note 6 marker after 'clapt', and the OCR joins "
    "footnotes 5 and 6 on L278."
)

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
with PATH.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
matches = [row for row in rows if row["segment_id"] == SEGMENT]
if len(matches) != 1 or matches[0]["note"] != CURRENT_NOTE:
    raise SystemExit("p.311 coverage row changed; review current state before repairing")
if (matches[0]["disposition"], matches[0]["migration_status"], matches[0]["source_line_ranges"]) != ("reviewed", "partial", "L7-15"):
    raise SystemExit("p.311 coverage status changed")
matches[0]["note"] = RESTORED_NOTE
print("p.311 coverage note repair preview: original scan corrections preserved; continuation and notes 1-6 pending accurately recorded")
if not args.apply:
    raise SystemExit(0)
backup = PATH.with_name(PATH.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"backup already exists: {backup.name}")
shutil.copy2(PATH, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=PATH.parent, delete=False) as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    temporary = Path(stream.name)
temporary.replace(PATH)
print(f"applied; recovery copy created as {backup.name}")
