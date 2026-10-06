"""Add the required empty-segment rationale after the plate migration."""
from __future__ import annotations

import csv
import hashlib
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "s2-coverage.csv"
BACKUP = Path(str(TABLE) + ".bak-s2-chp10-plate50-no-semantic-20261002")
SEGMENT_ID = "chp-10:10_CHP-10_intro_plates_visual-transcription:l6-7"
PREFIX = "no_semantic_content: "

if not BACKUP.is_file() or hashlib.sha256(BACKUP.read_bytes()).digest() != hashlib.sha256(TABLE.read_bytes()).digest():
    raise SystemExit("the saved pre-correction table backup does not match the live table")
with TABLE.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
row = next((item for item in rows if item["segment_id"] == SEGMENT_ID), None)
if row is None or not row["note"].startswith("Printed Plate 50 grouping title"):
    raise SystemExit("expected Plate 50 coverage row not found")
row["note"] = PREFIX + row["note"]
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    temporary = Path(stream.name)
temporary.replace(TABLE)
print(f"Updated {SEGMENT_ID}; line_count={len(rows) + 1}; backup retained.")
