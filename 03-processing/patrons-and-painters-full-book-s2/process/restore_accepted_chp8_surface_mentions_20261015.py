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
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RELATIVE_TABLE = Path("04-knowledge/tables/mentions.csv")
TABLE = ROOT / RELATIVE_TABLE
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
ADJUDICATION = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/chp8_candidate_surface_prompt_reconciliation.py"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp8-accepted-surface-restore-20261015")
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    TABLE: "2314deb9d8ab42e7222c69035993009f92e2a14948b03c78b04465b9d2e99cff",
    CANDIDATES: "287cb3b73ce8d113e6d82d1fb28fc9630145b1277ce010858b731d16c1e1f8f2",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    COVERAGE: "1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d",
    ADJUDICATION: "7ab3e8b6e50e63fe0dc099c03cb09a56787f9c736668ee27f129405697c723c1",
}
EXPECTED_CURRENT_ROWS = 26_055
EXPECTED_RESTORE_ROWS = 47
MENTION_PREFIX = "m-s2-chp8-surface-"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def validate() -> tuple[bytes, list[str], list[dict[str, str]], list[dict[str, str]]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit(f"HEAD changed: expected {EXPECTED_HEAD}, got {head}")
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"{path.relative_to(ROOT)} changed: expected {expected}, got {actual}")

    current_bytes = TABLE.read_bytes()
    headers, current_rows = read_csv(current_bytes)
    head_bytes = subprocess.check_output(["git", "show", f"HEAD:{RELATIVE_TABLE.as_posix()}"], cwd=ROOT)
    head_headers, head_rows = read_csv(head_bytes)
    if headers != head_headers:
        raise SystemExit("current and HEAD mentions.csv headers differ")
    if len(current_rows) != EXPECTED_CURRENT_ROWS:
        raise SystemExit(f"unexpected current mention count: {len(current_rows)}")
    current_ids = [row.get("mention_id", "") for row in current_rows]
    if not all(current_ids) or len(current_ids) != len(set(current_ids)):
        raise SystemExit("current mention IDs are empty or duplicated")

    restored = [row for row in head_rows if row.get("mention_id", "").startswith(MENTION_PREFIX)]
    if len(restored) != EXPECTED_RESTORE_ROWS:
        raise SystemExit(f"expected {EXPECTED_RESTORE_ROWS} accepted Chapter 8 rows in HEAD, found {len(restored)}")
    restored_ids = [row.get("mention_id", "") for row in restored]
    if not all(restored_ids) or len(restored_ids) != len(set(restored_ids)):
        raise SystemExit("historical accepted mention IDs are empty or duplicated")
    collisions = set(current_ids).intersection(restored_ids)
    if collisions:
        raise SystemExit(f"accepted Chapter 8 IDs already exist in current table: {sorted(collisions)[:10]}")

    candidate_ids: set[str] = set()
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
    existing_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in current_rows:
        existing_by_segment[row["segment_id"]].append(row)

    restored_intervals: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
    for row in restored:
        segment_id = row.get("segment_id", "")
        segment = segment_map.get(segment_id)
        if not segment:
            raise SystemExit(f"{row['mention_id']}: unknown source segment {segment_id}")
        if row.get("candidate_id") not in candidate_ids:
            raise SystemExit(f"{row['mention_id']}: candidate no longer exists: {row.get('candidate_id')}")
        state = coverage_map.get(segment_id)
        if not state or state.get("migration_status") != "complete" or state.get("disposition") not in {"reviewed", "excluded"}:
            raise SystemExit(f"{row['mention_id']}: segment is not recorded as processed: {segment_id}")

        source_file = segment["source_file"]
        if source_file not in source_lines:
            source_path = ROOT / source_file
            raw = source_path.read_bytes()
            if sha256(raw) != segment.get("asset_sha256"):
                raise SystemExit(f"{segment_id}: source asset hash mismatch")
            source_lines[source_file] = source_path.read_text(encoding="utf-8-sig").splitlines()
        if segment_id not in segment_texts:
            text = "\n".join(source_lines[source_file][int(segment["line_start"]) - 1:int(segment["line_end"])])
            if sha256(text.encode("utf-8")) != segment.get("sha256"):
                raise SystemExit(f"{segment_id}: source segment hash mismatch")
            segment_texts[segment_id] = text

        start, end = int(row["start_char"]), int(row["end_char"])
        text = segment_texts[segment_id]
        if start < 0 or end <= start or end > len(text) or text[start:end] != row.get("surface_form"):
            raise SystemExit(f"{row['mention_id']}: accepted span does not match exact source text")
        for current in existing_by_segment.get(segment_id, []):
            old_start, old_end = int(current["start_char"]), int(current["end_char"])
            if start < old_end and end > old_start:
                raise SystemExit(f"{row['mention_id']}: accepted span overlaps current mention {current['mention_id']}")
        restored_intervals[segment_id].append((start, end, row["mention_id"]))

    for segment_id, spans in restored_intervals.items():
        spans.sort()
        for left, right in zip(spans, spans[1:]):
            if right[0] < left[1]:
                raise SystemExit(f"historical accepted spans overlap in {segment_id}: {left}, {right}")
    return current_bytes, headers, current_rows, restored


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore only Chapter 8 mentions previously accepted by the locked S2 prompt review.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    current_bytes, headers, current_rows, restored = validate()
    print(f"accepted_rows_restored={len(restored)} current_rows={len(current_rows)} projected_total={len(current_rows) + len(restored)}")
    print("all 47 rows match HEAD IDs, live candidates, completed S2 segments, exact S0 spans, and non-overlapping mention ranges")
    if args.preview:
        print("preview only; no table or backup written")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writerows(restored)
    additions = buffer.getvalue().encode("utf-8")
    separator = b"" if current_bytes.endswith((b"\n", b"\r")) else b"\n"
    updated = current_bytes + separator + additions
    final_headers, final_rows = read_csv(updated)
    final_ids = [row.get("mention_id", "") for row in final_rows]
    if final_headers != headers or len(final_rows) != len(current_rows) + len(restored) or len(final_ids) != len(set(final_ids)):
        raise SystemExit("merged table failed header, row-count, or mention-ID validation")
    if sha256(TABLE.read_bytes()) != EXPECTED_HASHES[TABLE]:
        raise SystemExit("mentions.csv changed after preview")

    shutil.copy2(TABLE, BACKUP)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False) as stream:
            temp_path = Path(stream.name)
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, TABLE)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
    print(f"backup={BACKUP}")
    print(f"after_sha256={sha256(TABLE.read_bytes())}")
    print(f"restored={len(restored)} previously accepted Chapter 8 mentions")


if __name__ == "__main__":
    main()
