from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE_REL = Path("04-knowledge/tables/mentions.csv")
TABLE = ROOT / TABLE_REL
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
RESULTS = ROOT / "03-processing/patrons-and-painters-full-book-s2/results"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-accepted-surface-mentions-20261015")
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    TABLE: "87fbbc8644a2680ce6ecf4098ab948a6ac49ccece6646da3c9370b07491f263b",
    CANDIDATES: "287cb3b73ce8d113e6d82d1fb28fc9630145b1277ce010858b731d16c1e1f8f2",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    COVERAGE: "1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d",
}
EXPECTED_RESULTS_HASHES = {
    "chp-10.md": "7a3d36bf4b5f1e55585af4258a2fdb599e3db70996f1d6947be181c36c6278da",
    "chp-13.md": "4869e65b80af81fe702d8da35925e139694837f1e723fa41e750ca48f30f5ebb",
    "chp-14.md": "a26122586c9a1545b4034f34a0b85760ea4a2206d54ff0075358021999efe7c6",
    "chp-15.md": "6ce63afdf92b3491f0eff31dd4478640705d5d220c59597c7ea77179125f80e8",
}
EXPECTED_MAPPINGS_BY_CHAPTER = {"10": 60, "13": 18, "14": 10, "15": 9}
EXPECTED_RECONCILIATION = {"already_exact": 4, "covered_by_wider_same_candidate": 2, "restore": 91}
EXPECTED_COVERED = {
    ("13_CHP-13_intro.md", 240, "cand-11495", 7932, 7942, "collection"),
    ("14_CHP-14_intro.md", 6, "cand-4129", 95, 106, "art patrons"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    return list(reader.fieldnames or []), list(reader)


def accepted_mappings() -> list[dict[str, object]]:
    mappings: list[dict[str, object]] = []
    per_chapter: Counter[str] = Counter()
    for chapter in EXPECTED_MAPPINGS_BY_CHAPTER:
        result_path = RESULTS / f"chp-{chapter}.md"
        actual = sha256(result_path.read_bytes())
        expected = EXPECTED_RESULTS_HASHES[result_path.name]
        if actual != expected:
            raise SystemExit(f"{result_path.name} changed: expected {expected}, got {actual}")
        for line_number, line in enumerate(result_path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if "映射 cand-" not in line:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 6:
                raise SystemExit(f"{result_path.name}:{line_number}: malformed accepted mapping row")
            ref = re.fullmatch(r"(.+)#L(\d+)", cells[1])
            offsets = re.fullmatch(r"(\d+):(\d+)", cells[2])
            candidate = re.search(r"映射 (cand-\d+)", cells[4])
            if not ref or not offsets or not candidate:
                raise SystemExit(f"{result_path.name}:{line_number}: cannot parse accepted mapping")
            source_name, source_line = ref.group(1), int(ref.group(2))
            start, end = int(offsets.group(1)), int(offsets.group(2))
            if end <= start or not cells[3].strip():
                raise SystemExit(f"{result_path.name}:{line_number}: invalid accepted span")
            mappings.append({
                "chapter": chapter,
                "result": result_path.name,
                "result_line": line_number,
                "source_name": Path(source_name).name,
                "source_line": source_line,
                "source_ref": cells[1],
                "start": start,
                "end": end,
                "surface": cells[3],
                "candidate_id": candidate.group(1),
            })
            per_chapter[chapter] += 1
    if dict(per_chapter) != EXPECTED_MAPPINGS_BY_CHAPTER:
        raise SystemExit(f"accepted mapping counts changed: {dict(per_chapter)}")
    return mappings


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
    head_bytes = subprocess.check_output(["git", "show", f"HEAD:{TABLE_REL.as_posix()}"], cwd=ROOT)
    head_headers, head_rows = read_csv(head_bytes)
    if headers != head_headers:
        raise SystemExit("current and HEAD mentions.csv headers differ")
    if len(current_rows) != 25_964 or len(head_rows) != 27_697:
        raise SystemExit(f"unexpected table sizes: current={len(current_rows)}, HEAD={len(head_rows)}")
    current_ids = [row.get("mention_id", "") for row in current_rows]
    head_ids = [row.get("mention_id", "") for row in head_rows]
    if not all(current_ids) or len(current_ids) != len(set(current_ids)):
        raise SystemExit("current mention IDs are empty or duplicated")
    if not all(head_ids) or len(head_ids) != len(set(head_ids)):
        raise SystemExit("HEAD mention IDs are empty or duplicated")

    candidates = set()
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidates = {row["candidate_id"] for row in csv.DictReader(stream)}
    segments: list[dict] = []
    for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            segments.append(json.loads(line))
    coverage = {}
    with COVERAGE.open(encoding="utf-8-sig", newline="") as stream:
        coverage = {row["segment_id"]: row for row in csv.DictReader(stream)}

    segment_for_mapping: dict[tuple[str, int], dict] = {}
    for segment in segments:
        key = (Path(segment.get("source_file", "")).name, int(segment["line_start"]))
        # Indexing by start alone is insufficient; candidate lookup below uses the full interval.
        segment_for_mapping.setdefault(key, segment)
    segments_by_source: dict[str, list[dict]] = defaultdict(list)
    for segment in segments:
        segments_by_source[Path(segment.get("source_file", "")).name].append(segment)

    mappings = accepted_mappings()
    head_by_key: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    current_by_key: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    current_by_segment: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in head_rows:
        head_by_key[(row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"], row["surface_form"])].append(row)
    for row in current_rows:
        current_by_key[(row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"], row["surface_form"])].append(row)
        current_by_segment[row["segment_id"]].append(row)

    source_cache: dict[str, tuple[str, list[str], str]] = {}
    segment_texts: dict[str, str] = {}
    classes: Counter[str] = Counter()
    restored: list[dict[str, str]] = []
    covered_cases = set()
    restored_intervals: dict[str, list[tuple[int, int, str]]] = defaultdict(list)

    for mapping in mappings:
        possible = [
            segment for segment in segments_by_source.get(str(mapping["source_name"]), [])
            if int(segment["line_start"]) <= int(mapping["source_line"]) <= int(segment["line_end"])
        ]
        if len(possible) != 1:
            raise SystemExit(f"{mapping['source_ref']}: expected one S0 segment, found {len(possible)}")
        segment = possible[0]
        segment_id = segment["segment_id"]
        candidate_id = str(mapping["candidate_id"])
        start, end = int(mapping["start"]), int(mapping["end"])
        surface = str(mapping["surface"])
        if candidate_id not in candidates:
            raise SystemExit(f"{mapping['source_ref']}: unknown candidate {candidate_id}")
        coverage_row = coverage.get(segment_id)
        if not coverage_row or coverage_row.get("migration_status") != "complete" or coverage_row.get("disposition") not in {"reviewed", "excluded"}:
            raise SystemExit(f"{mapping['source_ref']}: segment is not recorded as processed: {segment_id}")
        source_file = segment["source_file"]
        if source_file not in source_cache:
            source_path = ROOT / source_file
            data = source_path.read_bytes()
            actual_asset_hash = sha256(data)
            if actual_asset_hash != segment.get("asset_sha256"):
                raise SystemExit(f"{segment_id}: source asset hash mismatch")
            source_cache[source_file] = (actual_asset_hash, source_path.read_text(encoding="utf-8-sig").splitlines(), source_file)
        _, source_lines, _ = source_cache[source_file]
        if segment_id not in segment_texts:
            text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
            if sha256(text.encode("utf-8")) != segment.get("sha256"):
                raise SystemExit(f"{segment_id}: source segment hash mismatch")
            segment_texts[segment_id] = text
        segment_text = segment_texts[segment_id]
        if start < 0 or end <= start or end > len(segment_text) or segment_text[start:end] != surface:
            raise SystemExit(f"{mapping['source_ref']}: accepted span does not match exact S0 source text")

        key = (segment_id, candidate_id, str(start), str(end), surface)
        historical = head_by_key.get(key, [])
        if len(historical) != 1:
            raise SystemExit(f"{mapping['source_ref']}: expected exactly one matching HEAD row, found {len(historical)}")
        old_row = historical[0]
        if current_by_key.get(key):
            classes["already_exact"] += 1
            continue

        wider = [
            row for row in current_by_segment.get(segment_id, [])
            if row["candidate_id"] == candidate_id
            and int(row["start_char"]) <= start
            and int(row["end_char"]) >= end
        ]
        if wider:
            descriptor = (
                str(mapping["source_name"]), int(mapping["source_line"]), candidate_id,
                start, end, surface,
            )
            covered_cases.add(descriptor)
            classes["covered_by_wider_same_candidate"] += 1
            continue

        collisions = [
            row for row in current_by_segment.get(segment_id, [])
            if max(start, int(row["start_char"])) < min(end, int(row["end_char"]))
        ]
        if collisions:
            raise SystemExit(f"{mapping['source_ref']}: accepted span overlaps current mention(s): {[r['mention_id'] for r in collisions]}")
        if old_row["mention_id"] in current_ids:
            raise SystemExit(f"{mapping['source_ref']}: historical mention ID already exists in current table")
        restored.append(old_row)
        restored_intervals[segment_id].append((start, end, old_row["mention_id"]))
        classes["restore"] += 1

    if classes != Counter(EXPECTED_RECONCILIATION):
        raise SystemExit(f"accepted mention reconciliation changed: {dict(classes)}")
    if covered_cases != EXPECTED_COVERED:
        raise SystemExit(f"wider-coverage cases changed: {covered_cases}")
    ids = [row["mention_id"] for row in restored]
    if len(ids) != len(set(ids)):
        raise SystemExit("selected restored mention IDs are duplicated")
    for segment_id, spans in restored_intervals.items():
        spans.sort()
        for left, right in zip(spans, spans[1:]):
            if right[0] < left[1]:
                raise SystemExit(f"restored accepted spans overlap in {segment_id}: {left}, {right}")
    # Preserve the historical row order for the appended subset.
    head_order = {row["mention_id"]: i for i, row in enumerate(head_rows)}
    restored.sort(key=lambda row: head_order[row["mention_id"]])
    return current_bytes, headers, current_rows, restored


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore only accepted, source-anchored S2 mention rows missing from the current table.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    current_bytes, headers, current_rows, restored = validate()
    print(f"accepted_rows_restored={len(restored)} current_rows={len(current_rows)} projected_total={len(current_rows) + len(restored)}")
    print(f"restored_by_chapter={dict(Counter(row['segment_id'].split(':', 1)[0] for row in restored))}")
    print("source spans, candidate IDs, completed coverage, and current-table overlaps validated")
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
    print(f"restored={len(restored)} accepted S2 mentions")


if __name__ == "__main__":
    main()
