import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
BACKUP_TAG = ".bak-s2-recover-ch15-p364-p372-20261015"
EXPECTED_SHA = "5d8ddbf2e0928518e4c8e913a48ea9d65b02b1df9457edd594ccfe6cec98b853"
PREFIXES = tuple(f"m-chp15-p{page}-" for page in range(364, 373))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

before = MENTIONS.read_bytes()
if sha(before) != EXPECTED_SHA:
    raise SystemExit("unexpected mentions pre-write hash")
head = subprocess.run(
    ["git", "show", "HEAD:04-knowledge/tables/mentions.csv"],
    cwd=ROOT, capture_output=True, check=True,
).stdout.decode("utf-8-sig")
historical = list(csv.DictReader(io.StringIO(head, newline="")))
recovered = [row for row in historical if row["mention_id"].startswith(PREFIXES)]
expected_counts = {"p364": 70, "p365": 56, "p366": 87, "p367": 65, "p368": 51, "p369": 52, "p370": 57, "p371": 57, "p372": 17}
counts = Counter(row["mention_id"].split("-")[2] for row in recovered)
if len(recovered) != 512 or dict(counts) != expected_counts:
    raise SystemExit(f"historical mention set changed: {dict(counts)}")

with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, current = reader.fieldnames, list(reader)
if any(row["mention_id"].startswith(PREFIXES) for row in current):
    raise SystemExit("p364-p372 historical mention IDs unexpectedly already present")
candidate_ids = {
    row["candidate_id"]
    for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
}
segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segments_by_id = {row["segment_id"]: row for row in segments}
source_texts = {}
for segment_id in {row["segment_id"] for row in recovered}:
    if segment_id not in segments_by_id:
        raise SystemExit(f"missing source segment: {segment_id}")
    segment = segments_by_id[segment_id]
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_texts[segment_id] = "\n".join(lines[segment["line_start"] - 1:segment["line_end"]])

for row in recovered:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"missing candidate foreign key: {row['mention_id']}")
    start, end = int(row["start_char"]), int(row["end_char"])
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
    for index, first in enumerate(spans):
        for second in spans[index + 1:]:
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
    "by_page": dict(sorted(counts.items())),
    "candidate_foreign_keys_verified": len(recovered),
    "source_spans_verified": len(recovered),
    "after_sha256": sha(output),
}, ensure_ascii=False, indent=2))

if args.apply:
    backup = MENTIONS.with_name(MENTIONS.name + BACKUP_TAG)
    if backup.exists() and sha(backup.read_bytes()) != EXPECTED_SHA:
        raise SystemExit(f"backup differs: {backup.name}")
    if not backup.exists():
        shutil.copy2(MENTIONS, backup)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=MENTIONS.parent) as handle:
        handle.write(output)
        temp = Path(handle.name)
    temp.replace(MENTIONS)
    print(json.dumps({"written_sha256": sha(MENTIONS.read_bytes())}, indent=2))
