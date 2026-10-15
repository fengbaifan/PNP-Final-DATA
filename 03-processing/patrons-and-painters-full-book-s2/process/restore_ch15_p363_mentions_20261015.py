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
BACKUP_TAG = ".bak-s2-recover-ch15-p363-20261015"
EXPECTED_SHA = "fc56264d9bca1f7ab2add2963e81682d1de4754c4c4493025e6e382f1c7ed155"
PREFIX = "m-chp15-p363-"
SEGMENT_IDS = {
    "chp-15:15_CHP-15_sec_i:l27-36",
    "chp-15:15_CHP-15_sec_i:l43-56",
}

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
recovered = [row for row in historical if row["mention_id"].startswith(PREFIX)]
if len(recovered) != 89 or {row["segment_id"] for row in recovered} != SEGMENT_IDS:
    raise SystemExit("historical p363 mention set changed")

with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, current = reader.fieldnames, list(reader)
if any(row["mention_id"].startswith(PREFIX) for row in current):
    raise SystemExit("p363 mention rows already exist")
candidate_ids = {
    row["candidate_id"]
    for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
}
segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segments_by_id = {row["segment_id"]: row for row in segments}
source_texts = {}
for segment_id in SEGMENT_IDS:
    segment = segments_by_id[segment_id]
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_texts[segment_id] = "\n".join(lines[segment["line_start"] - 1:segment["line_end"]])

for row in recovered:
    start, end = int(row["start_char"]), int(row["end_char"])
    if row["segment_id"] not in SEGMENT_IDS or row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"invalid historical row: {row['mention_id']}")
    if source_texts[row["segment_id"]][start:end] != row["surface_form"]:
        raise SystemExit(f"current source span differs: {row['mention_id']}")

combined = current + recovered
by_segment = {}
for row in combined:
    by_segment.setdefault(row["segment_id"], []).append(
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
    )
for segment_id, spans in by_segment.items():
    spans.sort()
    for i, first in enumerate(spans):
        for second in spans[i + 1:]:
            if second[0] >= first[1]:
                break
            nested = (first[0] <= second[0] and second[1] <= first[1]) or (second[0] <= first[0] and first[1] <= second[1])
            if first[:2] == second[:2] or not nested:
                raise SystemExit(f"crossing or duplicate spans: {first[2]} / {second[2]}")

buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
writer.writeheader()
writer.writerows(combined)
output = buffer.getvalue().encode("utf-8")
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "restored_historical_mentions": len(recovered),
    "by_segment": {segment_id: sum(row["segment_id"] == segment_id for row in recovered) for segment_id in sorted(SEGMENT_IDS)},
    "candidate_foreign_keys_verified": len(recovered),
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
