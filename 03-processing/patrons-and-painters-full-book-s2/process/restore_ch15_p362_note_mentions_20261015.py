import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
BACKUP_TAG = ".bak-s2-recover-ch15-p362-notes-20261015"
EXPECTED_SHA = "96da0785f4117d4115cd969cb320287751d5f541378b299d54adc92b37cd1719"
REMOVE_IDS = {f"m-chp15-p362-{i:04d}" for i in range(97, 101)}
SEGMENT_ID = "chp-15:15_CHP-15_sec_i:l43-56"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

before = MENTIONS.read_bytes()
if hashlib.sha256(before).hexdigest() != EXPECTED_SHA:
    raise SystemExit("unexpected mentions pre-write hash")

head = subprocess.run(
    ["git", "show", "HEAD:04-knowledge/tables/mentions.csv"],
    cwd=ROOT, capture_output=True, check=True,
).stdout.decode("utf-8-sig")
historical = list(csv.DictReader(io.StringIO(head, newline="")))
recovered = [row for row in historical if row["segment_id"] == SEGMENT_ID and row["mention_id"].startswith("m-chp15-p362-")]
if len(recovered) != 14 or {row["mention_id"] for row in recovered} != {
    f"m-chp15-p362-{i:04d}" for i in range(73, 87)
}:
    raise SystemExit("historical p362 note mention set changed")

with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, current = reader.fieldnames, list(reader)
if {row["mention_id"] for row in current if row["segment_id"] == SEGMENT_ID and row["mention_id"].startswith("m-chp15-p362-")} != REMOVE_IDS:
    raise SystemExit("unexpected current p362 note mention set")
current_ids = {row["mention_id"] for row in current}
if current_ids.intersection(row["mention_id"] for row in recovered):
    raise SystemExit("historical note mention already exists")

segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment = next(row for row in segments if row["segment_id"] == SEGMENT_ID)
source = ROOT / segment["source_file"]
source_lines = source.read_text(encoding="utf-8-sig").splitlines()
source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
candidate_ids = {
    row["candidate_id"]
    for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
}
for row in recovered:
    start, end = int(row["start_char"]), int(row["end_char"])
    if row["candidate_id"] not in candidate_ids or source_text[start:end] != row["surface_form"]:
        raise SystemExit(f"historical mention no longer matches current evidence: {row['mention_id']}")

combined = [row for row in current if row["mention_id"] not in REMOVE_IDS] + recovered
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
               for row in combined if row["segment_id"] == SEGMENT_ID)
for first, second in zip(spans, spans[1:]):
    if second[0] < first[1]:
        raise SystemExit(f"overlap after recovery: {first[2]} / {second[2]}")

buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
writer.writeheader()
writer.writerows(combined)
output = buffer.getvalue().encode("utf-8")
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "restored_historical_mentions": len(recovered),
    "removed_provisional_mentions": sorted(REMOVE_IDS),
    "source_spans_verified": len(recovered),
    "after_sha256": hashlib.sha256(output).hexdigest(),
}, ensure_ascii=False, indent=2))

if args.apply:
    backup = MENTIONS.with_name(MENTIONS.name + BACKUP_TAG)
    if backup.exists() and hashlib.sha256(backup.read_bytes()).hexdigest() != EXPECTED_SHA:
        raise SystemExit(f"backup differs: {backup.name}")
    if not backup.exists():
        shutil.copy2(MENTIONS, backup)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=MENTIONS.parent) as handle:
        handle.write(output)
        temp = Path(handle.name)
    temp.replace(MENTIONS)
    print(json.dumps({"written_sha256": hashlib.sha256(MENTIONS.read_bytes()).hexdigest()}, indent=2))
