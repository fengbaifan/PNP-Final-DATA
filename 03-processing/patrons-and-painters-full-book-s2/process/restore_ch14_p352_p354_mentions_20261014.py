"""Restore the previously reviewed p.352-p.354 S2 mention anchors."""
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
MENTION_PATH = TABLES / "mentions.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
SEGMENT_PATH = TABLES / "segments.jsonl"
SOURCE_COMMIT = "c65900801de1cb3af9089345250774161d67f5c9"
SOURCE_SHA256 = "6daa57037f79fb3eca85207b04091c710928d183f68dfc63afd4fb3fefd4b899"
EXPECTED_CURRENT_SHA256 = "612483ed71f06c1e4cd8a1b788401423cf9f1a4a9454f6235b43c9c2e1585add"
BACKUP_SUFFIX = ".bak-s2-recover-ch14-p352-p354-20261014"
TARGET_COUNTS = {
    "m-chp14-p352-": 76,
    "m-chp14-p353-": 74,
    "m-chp14-p354-": 71,
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="restore reviewed mention rows")
args = parser.parse_args()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


current_bytes = MENTION_PATH.read_bytes()
if sha256(current_bytes) != EXPECTED_CURRENT_SHA256:
    raise SystemExit("mentions.csv changed since this recovery was prepared")

source_bytes = subprocess.check_output(
    ["git", "show", f"{SOURCE_COMMIT}:04-knowledge/tables/mentions.csv"], cwd=ROOT
)
if sha256(source_bytes) != SOURCE_SHA256:
    raise SystemExit("the committed mention snapshot does not match the recovery evidence")

source_rows = list(csv.DictReader(io.StringIO(source_bytes.decode("utf-8-sig"), newline="")))
prefixes = tuple(TARGET_COUNTS)
recovered = [row for row in source_rows if row["mention_id"].startswith(prefixes)]
counts = {
    prefix: sum(row["mention_id"].startswith(prefix) for row in recovered)
    for prefix in TARGET_COUNTS
}
if counts != TARGET_COUNTS:
    raise SystemExit(f"recovery source counts changed: {counts}")

with MENTION_PATH.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    mention_fields = reader.fieldnames
    current = list(reader)
with CANDIDATE_PATH.open(encoding="utf-8-sig", newline="") as handle:
    candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
segment_rows = [
    json.loads(line)
    for line in SEGMENT_PATH.read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
segment_by_id = {row["segment_id"]: row for row in segment_rows}
current_ids = {row["mention_id"] for row in current}
if len(current_ids) != len(current):
    raise SystemExit("current mentions.csv already has duplicate mention IDs")
if current_ids.intersection(row["mention_id"] for row in recovered):
    raise SystemExit("one or more recovery mention IDs already exist in the current table")

segment_texts = {}
for row in recovered:
    segment_id = row["segment_id"]
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"missing candidate: {row['mention_id']} -> {row['candidate_id']}")
    segment = segment_by_id.get(segment_id)
    if segment is None:
        raise SystemExit(f"missing source segment: {row['mention_id']} -> {segment_id}")
    if segment_id not in segment_texts:
        source_path = ROOT / segment["source_file"]
        source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
        first, last = int(segment["line_start"]), int(segment["line_end"])
        if first < 1 or last < first or last > len(source_lines):
            raise SystemExit(f"invalid source line interval for {segment_id}")
        segment_texts[segment_id] = "\n".join(source_lines[first - 1:last])
    start, end = int(row["start_char"]), int(row["end_char"])
    if start < 0 or end <= start or segment_texts[segment_id][start:end] != row["surface_form"]:
        raise SystemExit(f"source span mismatch: {row['mention_id']}")

# Preserve existing rows and reject duplicates or crossing spans. Strict
# containment is allowed by audit_tables.py.
intervals = {}
for row in current + recovered:
    intervals.setdefault(row["segment_id"], []).append(
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
    )
crossings = []
for segment_id, spans in intervals.items():
    spans.sort()
    for index, left in enumerate(spans):
        for right in spans[index + 1 :]:
            if right[0] >= left[1]:
                break
            exact_duplicate = left[:2] == right[:2]
            nested = (left[0] <= right[0] and right[1] <= left[1]) or (
                right[0] <= left[0] and left[1] <= right[1]
            )
            if exact_duplicate or not nested:
                crossings.append((segment_id, left[2], right[2]))
if crossings:
    raise SystemExit(f"recovery introduces duplicate/crossing spans: {crossings[:10]}")

print(
    json.dumps(
        {
            "mode": "apply" if args.apply else "dry-run",
            "source_commit": SOURCE_COMMIT,
            "source_mentions_sha256": SOURCE_SHA256,
            "current_mentions_sha256": EXPECTED_CURRENT_SHA256,
            "recovered_rows": len(recovered),
            "counts": counts,
            "validated_spans": len(recovered),
            "validated_candidates": len(recovered),
            "crossing_spans": 0,
        },
        ensure_ascii=False,
        indent=2,
    )
)

if args.apply:
    backup = MENTION_PATH.with_name(MENTION_PATH.name + BACKUP_SUFFIX)
    if backup.exists():
        if sha256(backup.read_bytes()) != EXPECTED_CURRENT_SHA256:
            raise SystemExit(f"existing backup differs from pre-write table: {backup.name}")
    else:
        shutil.copy2(MENTION_PATH, backup)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=MENTION_PATH.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=mention_fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(current + recovered)
        temp_path = Path(handle.name)
    temp_path.replace(MENTION_PATH)
    print(json.dumps({"written_sha256": sha256(MENTION_PATH.read_bytes()), "backup": backup.name}))
