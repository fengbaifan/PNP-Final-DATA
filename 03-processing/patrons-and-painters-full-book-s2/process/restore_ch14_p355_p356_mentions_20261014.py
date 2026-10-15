"""Restore p.355-p.356 mention anchors preserved in the repository snapshot."""
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
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE_COMMIT = "c65900801de1cb3af9089345250774161d67f5c9"
SOURCE_SHA = "6daa57037f79fb3eca85207b04091c710928d183f68dfc63afd4fb3fefd4b899"
CURRENT_SHA = "25e9e47dbcae5d111a2f6e57483dc636684e47bc29239615f64c7717033e2d77"
BACKUP_SUFFIX = ".bak-s2-recover-ch14-p355-p356-20261014"
COUNTS = {"m-chp14-p355-": 87, "m-chp14-p356-": 72}
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

before = MENTIONS.read_bytes()
if sha(before) != CURRENT_SHA:
    raise SystemExit("mentions.csv changed since this recovery was prepared")
snapshot = subprocess.check_output(
    ["git", "show", f"{SOURCE_COMMIT}:04-knowledge/tables/mentions.csv"], cwd=ROOT
)
if sha(snapshot) != SOURCE_SHA:
    raise SystemExit("repository mention snapshot changed")
historical = list(csv.DictReader(io.StringIO(snapshot.decode("utf-8-sig"), newline="")))
prefixes = tuple(COUNTS)
recovered = [row for row in historical if row["mention_id"].startswith(prefixes)]
found = {prefix: sum(row["mention_id"].startswith(prefix) for row in recovered) for prefix in COUNTS}
if found != COUNTS:
    raise SystemExit(f"unexpected source counts: {found}")
with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, current = reader.fieldnames, list(reader)
candidate_ids = {row["candidate_id"] for row in csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
segment_by_id = {
    row["segment_id"]: row
    for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())
}
ids = {row["mention_id"] for row in current}
if len(ids) != len(current) or ids.intersection(row["mention_id"] for row in recovered):
    raise SystemExit("duplicate or already-restored mention IDs")
texts = {}
for row in recovered:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"missing candidate: {row['mention_id']}")
    seg_id = row["segment_id"]
    seg = segment_by_id.get(seg_id)
    if seg is None:
        raise SystemExit(f"missing segment: {seg_id}")
    if seg_id not in texts:
        lines = (ROOT / seg["source_file"]).read_text(encoding="utf-8-sig").splitlines()
        texts[seg_id] = "\n".join(lines[int(seg["line_start"]) - 1 : int(seg["line_end"])])
    start, end = int(row["start_char"]), int(row["end_char"])
    if texts[seg_id][start:end] != row["surface_form"]:
        raise SystemExit(f"source span mismatch: {row['mention_id']}")
intervals = {}
for row in current + recovered:
    intervals.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for seg_id, spans in intervals.items():
    spans.sort()
    for i, left in enumerate(spans):
        for right in spans[i + 1 :]:
            if right[0] >= left[1]:
                break
            nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
            if left[:2] == right[:2] or not nested:
                raise SystemExit(f"crossing source spans: {seg_id} {left[2]} / {right[2]}")
from io import StringIO
buffer = StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
writer.writeheader()
writer.writerows(current + recovered)
after = buffer.getvalue().encode("utf-8")
print(json.dumps({"mode": "apply" if args.apply else "dry-run", "source_commit": SOURCE_COMMIT, "recovered": len(recovered), "counts": found, "validated_spans": len(recovered), "crossings": 0, "after_sha256": sha(after)}, ensure_ascii=False, indent=2))
if args.apply:
    backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
    if backup.exists():
        if sha(backup.read_bytes()) != CURRENT_SHA:
            raise SystemExit("existing backup differs from pre-write mentions.csv")
    else:
        shutil.copy2(MENTIONS, backup)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=MENTIONS.parent) as handle:
        handle.write(after)
        temp = Path(handle.name)
    temp.replace(MENTIONS)
    print(json.dumps({"written_sha256": sha(MENTIONS.read_bytes()), "backup": backup.name}))
