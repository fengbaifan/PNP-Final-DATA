from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RELATIVE_TABLE = Path("04-knowledge/tables/mentions.csv")
TABLE = ROOT / RELATIVE_TABLE
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-restore-dropped-frontmatter-ch16-21-20261015")
EXPECTED_CURRENT_SHA256 = "5005de8f9e02346308ba1be120e4cd88609546b6b9263f3e0281fb32dc9b7b2d"
EXPECTED_CANDIDATES_SHA256 = "748e71911a51e1cd8ed28e2099c6c67007b2b424566706f46780a0ac4d81c407"
EXPECTED_SEGMENTS_SHA256 = "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036"
EXPECTED_COVERAGE_SHA256 = "1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d"
EXPECTED_COUNTS = {
    "front-matter": 735,
    "chp-16": 297,
    "chp-17": 271,
    "chp-18": 77,
    "chp-19": 451,
    "chp-20": 987,
    "chp-21": 917,
}
HEAD = "HEAD"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_csv_bytes(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader)


def restore_chapter(segment_id: str) -> str | None:
    prefix = segment_id.split(":", 1)[0]
    return prefix if prefix in EXPECTED_COUNTS else None


def validate() -> tuple[bytes, bytes, list[dict[str, str]], list[dict[str, str]], dict[str, dict], dict[str, dict]]:
    current_bytes = TABLE.read_bytes()
    current_hash = sha256_bytes(current_bytes)
    if current_hash != EXPECTED_CURRENT_SHA256:
        raise SystemExit(f"current mentions hash mismatch: expected {EXPECTED_CURRENT_SHA256}, got {current_hash}")
    for path, expected in (
        (CANDIDATES, EXPECTED_CANDIDATES_SHA256),
        (SEGMENTS, EXPECTED_SEGMENTS_SHA256),
        (COVERAGE, EXPECTED_COVERAGE_SHA256),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise SystemExit(f"{path.name} hash mismatch: expected {expected}, got {actual}")

    head_bytes = subprocess.check_output(["git", "show", f"{HEAD}:{RELATIVE_TABLE.as_posix()}"], cwd=ROOT)
    current_headers, current_rows = read_csv_bytes(current_bytes)
    old_headers, old_rows = read_csv_bytes(head_bytes)
    if current_headers != old_headers:
        raise SystemExit("current and HEAD mentions.csv headers differ")
    if len(current_rows) != 22_218:
        raise SystemExit(f"unexpected current mention count: {len(current_rows)}")

    current_ids = [row.get("mention_id", "") for row in current_rows]
    if not all(current_ids) or len(current_ids) != len(set(current_ids)):
        raise SystemExit("current mention IDs are empty or duplicated")
    current_segments = {row.get("segment_id", "") for row in current_rows}
    selected = [row for row in old_rows if restore_chapter(row.get("segment_id", ""))]
    counts = Counter(restore_chapter(row["segment_id"]) for row in selected)
    if dict(counts) != EXPECTED_COUNTS:
        raise SystemExit(f"historical scope count mismatch: expected {EXPECTED_COUNTS}, got {dict(counts)}")
    if current_segments.intersection(row["segment_id"] for row in selected):
        overlap = sorted(current_segments.intersection(row["segment_id"] for row in selected))
        raise SystemExit(f"current mentions already occupy target segments: {overlap[:10]}")
    selected_ids = [row.get("mention_id", "") for row in selected]
    if not all(selected_ids) or len(selected_ids) != len(set(selected_ids)):
        raise SystemExit("historical target rows contain empty or duplicate IDs")
    collisions = set(current_ids).intersection(selected_ids)
    if collisions:
        raise SystemExit(f"historical IDs collide with current rows: {sorted(collisions)[:10]}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(stream)}
    segment_map: dict[str, dict] = {}
    for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            row = json.loads(line)
            segment_map[row["segment_id"]] = row
    with COVERAGE.open(encoding="utf-8-sig", newline="") as stream:
        coverage_map = {row["segment_id"]: row for row in csv.DictReader(stream)}

    source_lines: dict[str, list[str]] = {}
    segment_texts: dict[str, str] = {}
    intervals: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    source_hashes: dict[str, str] = {}
    for row in selected:
        mention_id = row["mention_id"]
        segment_id = row["segment_id"]
        segment = segment_map.get(segment_id)
        if not segment:
            raise SystemExit(f"{mention_id}: unknown segment {segment_id}")
        if row.get("candidate_id") not in candidate_ids:
            raise SystemExit(f"{mention_id}: unknown candidate {row.get('candidate_id')}")
        coverage = coverage_map.get(segment_id)
        if not coverage or coverage.get("migration_status") != "complete" or coverage.get("disposition") not in {"reviewed", "excluded"}:
            raise SystemExit(f"{mention_id}: segment is not recorded as fully processed: {segment_id}")
        source_file = segment["source_file"]
        if source_file not in source_lines:
            source_path = ROOT / source_file
            data = source_path.read_bytes()
            actual_asset_hash = sha256_bytes(data)
            if actual_asset_hash != segment.get("asset_sha256"):
                raise SystemExit(f"{segment_id}: source asset hash mismatch")
            source_hashes[source_file] = actual_asset_hash
            source_lines[source_file] = source_path.read_text(encoding="utf-8-sig").splitlines()
        if segment_id not in segment_texts:
            segment_text = "\n".join(source_lines[source_file][int(segment["line_start"]) - 1 : int(segment["line_end"])])
            if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment.get("sha256"):
                raise SystemExit(f"{segment_id}: source segment hash mismatch")
            segment_texts[segment_id] = segment_text
        start, end = int(row["start_char"]), int(row["end_char"])
        text = segment_texts[segment_id]
        if start < 0 or end <= start or end > len(text):
            raise SystemExit(f"{mention_id}: invalid character range {start}:{end}")
        if text[start:end] != row.get("surface_form"):
            raise SystemExit(f"{mention_id}: surface does not match source segment slice")
        if not row.get("surface_form", "").strip():
            raise SystemExit(f"{mention_id}: empty surface form")
        intervals[segment_id].append((start, end, mention_id))

    overlap_errors = []
    for segment_id, items in intervals.items():
        items.sort()
        for index, left in enumerate(items):
            for right in items[index + 1 :]:
                if right[0] >= left[1]:
                    break
                exact = left[:2] == right[:2]
                nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
                if exact or not nested:
                    overlap_errors.append((segment_id, left[2], right[2]))
    if overlap_errors:
        raise SystemExit(f"historical rows contain overlapping mention spans: {overlap_errors[:10]}")

    return current_bytes, head_bytes, current_rows, selected, segment_map, coverage_map


def main() -> None:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    current_bytes, _, current_rows, selected, _, _ = validate()
    counts = Counter(restore_chapter(row["segment_id"]) for row in selected)
    print(f"restore_rows={len(selected)} current_rows={len(current_rows)} projected_total={len(current_rows)+len(selected)}")
    print(f"per_scope={dict(counts)}")
    print("all restored rows match current S0 segment slices, candidate IDs, completed coverage, and non-crossing span rules")
    if args.preview:
        print("preview only; no table or backup written")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    head_bytes = subprocess.check_output(["git", "show", f"{HEAD}:{RELATIVE_TABLE.as_posix()}"], cwd=ROOT)
    headers, old_rows = read_csv_bytes(head_bytes)
    target_rows = [row for row in old_rows if restore_chapter(row.get("segment_id", ""))]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writerows(target_rows)
    additions = buffer.getvalue().encode("utf-8")
    separator = b"" if current_bytes.endswith((b"\n", b"\r")) else b"\n"
    updated = current_bytes + separator + additions

    final_headers, final_rows = read_csv_bytes(updated)
    final_ids = [row.get("mention_id", "") for row in final_rows]
    if final_headers != headers or len(final_rows) != len(current_rows) + len(selected) or len(final_ids) != len(set(final_ids)):
        raise SystemExit("merged table failed header, row-count, or mention-ID validation")
    if sha256_bytes(TABLE.read_bytes()) != EXPECTED_CURRENT_SHA256:
        raise SystemExit("mentions.csv changed after preview")

    shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False) as stream:
        temp_path = Path(stream.name)
        stream.write(updated)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp_path, TABLE)
    print(f"backup={BACKUP}")
    print(f"after_sha256={sha256_file(TABLE)}")
    print(f"restored={len(selected)} previously reviewed and source-validated mention rows")


if __name__ == "__main__":
    main()
