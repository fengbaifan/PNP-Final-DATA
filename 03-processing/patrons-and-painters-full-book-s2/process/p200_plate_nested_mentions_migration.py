"""Add title-figure mentions omitted from the first Plate 32 migration."""
import argparse
import csv
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp7-p200-plate-nested-20260930")
TARGETS = [
    ("chp-7:07_CHP-7_sec_v:l39-40", "m-chp7-p200-plate32a-subject", "cand-4161", "Silenus",
     "Nested title-figure mention; the title is not treated as evidence for a historical event."),
    ("chp-7:07_CHP-7_sec_v_visual-transcription:l3-3", "m-chp7-p200-plate32b-subject", "cand-4162", "Hercules",
     "Nested title-figure mention; the title is not treated as evidence for a historical event."),
]


with TABLE.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
existing_ids = {row["mention_id"] for row in rows}
existing_keys = {(row["segment_id"], row["start_char"], row["end_char"]) for row in rows}
segment_records = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if line]
segments = {row["segment_id"]: row for row in segment_records}
payload = []

for segment_id, mention_id, candidate_id, surface, note in TARGETS:
    if mention_id in existing_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    record = segments.get(segment_id)
    if record is None:
        raise SystemExit(f"segment is missing: {segment_id}")
    text = (ROOT / record["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(text[record["line_start"] - 1:record["line_end"]])
    start = text.find(surface)
    if start < 0 or text.find(surface, start + 1) >= 0:
        raise SystemExit(f"surface is not unique in {segment_id}: {surface}")
    key = (segment_id, str(start), str(start + len(surface)))
    if key in existing_keys:
        raise SystemExit(f"mention span already exists: {key}")
    payload.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if not parser.parse_args().apply:
    print(json.dumps({"mode": "dry-run", "new_mentions": payload}, ensure_ascii=False, indent=2))
    raise SystemExit(0)

if BACKUP.exists():
    raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP}")
shutil.copy2(TABLE, BACKUP)
rows.extend(payload)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent,
                                 delete=False, suffix=".tmp") as stream:
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    temporary = Path(stream.name)
temporary.replace(TABLE)
print(json.dumps({"mode": "applied", "new_mentions": payload}, ensure_ascii=False, indent=2))
