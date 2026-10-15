import argparse
import csv
import hashlib
import shutil
import subprocess
import tempfile
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-15:15_CHP-15_sec_i:l16-25"
SOURCE_COMMIT = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_CURRENT = "aa83314dfe849236ddb333be1d87fc603b8d7b3d750833ccfb5eca783a33ca24"
EXPECTED_SNAPSHOT = "6daa57037f79fb3eca85207b04091c710928d183f68dfc63afd4fb3fefd4b899"
BACKUP = MENTIONS.with_name(MENTIONS.name + ".bak-s2-recover-ch15-p362-20261015")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()


def sha(data):
    return hashlib.sha256(data).hexdigest()


current_bytes = MENTIONS.read_bytes()
if sha(current_bytes) != EXPECTED_CURRENT:
    raise SystemExit("unexpected current mentions.csv hash")
snapshot_bytes = subprocess.check_output(
    ["git", "show", f"{SOURCE_COMMIT}:04-knowledge/tables/mentions.csv"], cwd=ROOT
)
if sha(snapshot_bytes) != EXPECTED_SNAPSHOT:
    raise SystemExit("unexpected historical mentions snapshot hash")

with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields = reader.fieldnames
    rows = list(reader)
with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
    candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}
snapshot_rows = [
    row for row in csv.DictReader(snapshot_bytes.decode("utf-8-sig").splitlines())
    if row["segment_id"] == SEGMENT_ID
]
if len(snapshot_rows) != 73:
    raise SystemExit(f"expected 73 historical anchors, found {len(snapshot_rows)}")
if any(row["segment_id"] == SEGMENT_ID for row in rows):
    raise SystemExit("target segment already contains mention rows")
existing_ids = {row["mention_id"] for row in rows}
if len(existing_ids) != len(rows) or any(row["mention_id"] in existing_ids for row in snapshot_rows):
    raise SystemExit("duplicate mention ID in current table or recovery set")

segments = [
    __import__("json").loads(line)
    for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
segment = next(row for row in segments if row["segment_id"] == SEGMENT_ID)
source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
for row in snapshot_rows:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"unknown candidate for {row['mention_id']}: {row['candidate_id']}")
    start, end = int(row["start_char"]), int(row["end_char"])
    if source_text[start:end] != row["surface_form"]:
        raise SystemExit(f"source span mismatch for {row['mention_id']}")

restored = rows + snapshot_rows
by_segment = {}
for row in restored:
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

buffer = StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
writer.writeheader()
writer.writerows(restored)
output = buffer.getvalue().encode("utf-8")
print({
    "mode": "apply" if args.apply else "dry-run",
    "source_commit": SOURCE_COMMIT,
    "restored_mentions": len(snapshot_rows),
    "candidates_valid": len(snapshot_rows),
    "source_spans_valid": len(snapshot_rows),
    "overlap_errors": 0,
    "after_sha256": sha(output),
})

if args.apply:
    if BACKUP.exists():
        if sha(BACKUP.read_bytes()) != EXPECTED_CURRENT:
            raise SystemExit(f"backup differs: {BACKUP.name}")
    else:
        shutil.copy2(MENTIONS, BACKUP)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=MENTIONS.parent) as handle:
        handle.write(output)
        temporary = Path(handle.name)
    temporary.replace(MENTIONS)
    print({"written_sha256": sha(MENTIONS.read_bytes())})
