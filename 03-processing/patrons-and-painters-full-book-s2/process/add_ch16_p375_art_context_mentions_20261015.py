from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/mentions.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/16_CHP-16_intro.md"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch16-p375-art-context-mentions-20261015")
EXPECTED_MENTIONS_SHA256 = "cfe5cdd7ac5a7e541741f915571ea1fcae0620308b404003b59d790e2d93a4f5"
SEGMENT_ID = "chp-16:16_CHP-16_intro:l24-36"
CANDIDATE_ID = "cand-11543"
NEW_ROWS = [
    {
        "mention_id": "m-s2-ch16-p375-venetian-art-tradition-001",
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": "Venetian art",
        "start_char": "876",
        "end_char": "888",
        "note": "Explicit reference to the source-defined Venetian art tradition cand-11543, not to Venice as a place.",
    },
    {
        "mention_id": "m-s2-ch16-p375-artistic-atmosphere-anaphor-001",
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": "such an atmosphere",
        "start_char": "2491",
        "end_char": "2509",
        "note": "Anaphoric to the preceding account of dealer tastes and colour/fantasy in Venetian art; Haskell uses it as the context in which Guardi could flourish.",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate() -> tuple[bytes, list[str], list[dict[str, str]], list[str]]:
    current = TABLE.read_bytes()
    current_hash = sha256(current)
    if current_hash != EXPECTED_MENTIONS_SHA256:
        raise SystemExit(f"mentions hash mismatch: expected {EXPECTED_MENTIONS_SHA256}, got {current_hash}")
    text = current.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    headers = list(reader.fieldnames or [])
    rows = list(reader)
    required = {"mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note"}
    if not required.issubset(headers):
        raise SystemExit(f"mentions.csv lacks columns: {sorted(required-set(headers))}")
    ids = [row["mention_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("current mentions.csv has duplicate IDs")
    if any(row["mention_id"] in set(ids) for row in NEW_ROWS):
        raise SystemExit("one or more new mention IDs already exist")
    if any(row["segment_id"] != SEGMENT_ID or row["candidate_id"] != CANDIDATE_ID for row in NEW_ROWS):
        raise SystemExit("new mention segment or candidate differs from the fixed decision")

    candidate_ids = {row["candidate_id"] for row in csv.DictReader(CANDIDATES.open(encoding="utf-8-sig", newline=""))}
    if CANDIDATE_ID not in candidate_ids:
        raise SystemExit(f"candidate does not exist: {CANDIDATE_ID}")
    segment_map = {
        row["segment_id"]: row
        for row in (json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    segment = segment_map.get(SEGMENT_ID)
    if not segment:
        raise SystemExit(f"segment does not exist: {SEGMENT_ID}")
    coverage = {row["segment_id"]: row for row in csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline=""))}
    coverage_row = coverage.get(SEGMENT_ID)
    if not coverage_row or coverage_row.get("migration_status") != "complete":
        raise SystemExit(f"segment is not fully migrated: {SEGMENT_ID}")
    source_text = SOURCE.read_text(encoding="utf-8-sig")
    if sha256(SOURCE.read_bytes()) != segment.get("asset_sha256"):
        raise SystemExit("source asset hash mismatch")
    source_lines = source_text.splitlines()
    segment_text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    if sha256(segment_text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("source segment hash mismatch")
    occupied = []
    for row in rows:
        if row.get("segment_id") == SEGMENT_ID:
            occupied.append((int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
    for row in NEW_ROWS:
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment_text[start:end] != row["surface_form"]:
            raise SystemExit(f"source slice mismatch for {row['mention_id']}: {segment_text[start:end]!r}")
        for old_start, old_end, old_id in occupied:
            if start < old_end and old_start < end:
                raise SystemExit(f"new span overlaps {old_id}: {row['mention_id']}")
        occupied.append((start, end, row["mention_id"]))
    occupied.sort()
    for left, right in zip(occupied, occupied[1:]):
        if right[0] < left[1]:
            nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
            if not nested or left[:2] == right[:2]:
                raise SystemExit(f"crossing or duplicate spans: {left[2]} and {right[2]}")
    return current, headers, rows, occupied


def main() -> None:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    current, headers, rows, _ = validate()
    print(f"segment={SEGMENT_ID} add_mentions={len(NEW_ROWS)} current_rows={len(rows)}")
    for row in NEW_ROWS:
        print(f"{row['mention_id']}: {row['surface_form']} [{row['start_char']}:{row['end_char']}] -> {row['candidate_id']}")
    print(f"before_sha256={sha256(current)}")
    if args.preview:
        print("preview only; no table or backup written")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writerows(NEW_ROWS)
    separator = b"" if current.endswith((b"\n", b"\r")) else b"\n"
    updated = current + separator + buffer.getvalue().encode("utf-8")
    final_rows = list(csv.DictReader(io.StringIO(updated.decode("utf-8-sig"), newline="")))
    final_ids = [row["mention_id"] for row in final_rows]
    if len(final_rows) != len(rows) + len(NEW_ROWS) or len(final_ids) != len(set(final_ids)):
        raise SystemExit("post-merge row count or ID uniqueness failed")
    if sha256(TABLE.read_bytes()) != EXPECTED_MENTIONS_SHA256:
        raise SystemExit("mentions.csv changed after preview")

    shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False) as stream:
        temp_path = Path(stream.name)
        stream.write(updated)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp_path, TABLE)
    print(f"backup={BACKUP}")
    print(f"after_sha256={sha256(TABLE.read_bytes())}")
    print(f"applied={len(NEW_ROWS)} mention rows")


if __name__ == "__main__":
    main()
