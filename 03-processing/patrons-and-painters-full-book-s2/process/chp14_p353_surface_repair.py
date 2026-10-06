"""Add two typed candidate mentions found by the p.353 surface audit."""
import argparse
import csv
import hashlib
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
SEGMENT = "chp-14:14_CHP-14_intro:l63-71"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp14-p353-surface-repair-20261003")
ADDITIONS = [
    ("m-chp14-p353-0073", "cand-3571", "canvas", 65,
     "Painting support named in the description of the columns reaching the canvas edge."),
    ("m-chp14-p353-0074", "cand-3462", "Europe", 66,
     "Geographic scope of the predicted spread of Greek vase forms in painting and decoration."),
]

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

with TABLE.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames
    rows = list(reader)
existing = {row["mention_id"] for row in rows}
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
offsets = {}
offset = 0
for line_number in range(63, 72):
    offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + (1 if line_number < 71 else 0)

for mention_id, candidate_id, surface, line_number, note in ADDITIONS:
    if mention_id in existing:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    line = source_lines[line_number - 1]
    pos = line.find(surface)
    if pos < 0 or line.find(surface, pos + 1) >= 0:
        raise SystemExit(f"expected one exact {surface!r} on L{line_number}")
    start, end = offsets[line_number] + pos, offsets[line_number] + pos + len(surface)
    for row in rows:
        if row["segment_id"] != SEGMENT:
            continue
        other_start, other_end = int(row["start_char"]), int(row["end_char"])
        if start < other_end and end > other_start:
            raise SystemExit(f"planned mention overlaps {row['mention_id']}")
    rows.append({"mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": candidate_id,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})
    existing.add(mention_id)

print(f"{{\"mode\": \"{'apply' if args.apply else 'dry-run'}\", \"added_mentions\": {len(ADDITIONS)}}}")
if args.apply:
    if BACKUP.exists():
        if hashlib.sha256(BACKUP.read_bytes()).digest() != hashlib.sha256(TABLE.read_bytes()).digest():
            raise SystemExit(f"existing backup differs from current table: {BACKUP.name}")
    else:
        shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(handle.name)
    temp_path.replace(TABLE)
