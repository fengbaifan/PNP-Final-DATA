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
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RELATIVE_TABLE = Path("04-knowledge/tables/mentions.csv")
TABLE = ROOT / RELATIVE_TABLE
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-reviewed-surface-mentions-20261015")
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HEAD_TABLE_SHA256 = "6daa57037f79fb3eca85207b04091c710928d183f68dfc63afd4fb3fefd4b899"
EXPECTED_HASHES = {
    TABLE: "178885264bc55e8fe1acda43aa078c03dde9a45de54d51bec7f610e82b37dfa8",
    CANDIDATES: "287cb3b73ce8d113e6d82d1fb28fc9630145b1277ce010858b731d16c1e1f8f2",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    COVERAGE: "1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d",
}
EXPECTED_CURRENT_ROWS = 26_102
EXPECTED_HISTORICAL_MISSING = 345

# These four historically accepted place mentions are valid nested entities
# inside a group, exhibition, or institution mention currently in the table.
NESTED_CURRENT_RESTORE = {
    "m-s2-surface-a8a6c5978b050e4a": ("m-s2-ch13-p335-039", "cand-12140"),
    "m-s2-surface-0e88d39238b6475e": ("m-s2-ch10-p331-0012", "cand-9870"),
    "m-s2-surface-0d95650b5b027951": ("m-chp2-seciv-l190-245-0060", "cand-4892"),
}

# These historical rows are superseded by current, more specific mappings.
# Keep the current institution/place decomposition and current Zanetti mapping.
CONFLICT_SKIP = {
    "m-s2-surface-7f58514b473075ba": {
        "m-chp9-p270-n06-library",
        "m-chp9-p270-n06-lucca",
    },
    "m-s2-surface-4ac6a6ef9edf9885": {"m-chp9-p270-n07-zanetti"},
    "m-s2-surface-1397a86ca6cdcd1b": {
        "m-chp9-p271-n01-library",
        "m-chp9-p271-n01-modena",
    },
    "m-s2-surface-5f35ed8736c82486": {"m-chp9-p274-n01-zanetti"},
    "m-s2-surface-0cb4eecce65bf077": {
        "m-chp9-p275-n02-biblioteca-estense",
        "m-chp9-p275-n02-modena",
    },
}

# "Europe" is a substring of the accepted place name "Central Europe". It is
# not a separate place reference in this sentence, so retain the full region
# mention and skip the compositional subspan.
COMPOSITIONAL_SKIP = {
    "m-s2-surface-4d75f7e1171ffb8b": "m-s2-surface-a8a6c5978b050e4a",
}

# Two additional pairs are intentionally nested within the restored historical
# set: a place inside an epithet and a place inside an institution name.
HISTORICAL_NESTED_PAIRS = {
    frozenset({"m-s2-surface-04e85eab372f9bf9", "m-s2-surface-60dbacda9c23ce0a"}),
    frozenset({"m-s2-surface-24f51761f185a313", "m-s2-surface-755420be90842e1e"}),
}

# The accepted historical surface omitted a line break present in S0. Store the
# exact source slice so the strict table audit can verify the character span.
SURFACE_FORM_REPAIRS = {
    "m-s2-surface-a8a6c5978b050e4a": "Central\nEurope",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def is_historical_surface_review(row: dict[str, str]) -> bool:
    mention_id = row.get("mention_id", "")
    return "surface" in mention_id and (
        mention_id.startswith("m-s2-") or mention_id.startswith("m-chp")
    )


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
    if sha256(head_bytes) != EXPECTED_HEAD_TABLE_SHA256:
        raise SystemExit("HEAD mentions.csv hash changed")
    head_headers, head_rows = read_csv(head_bytes)
    if headers != head_headers:
        raise SystemExit("current and HEAD mentions.csv headers differ")
    if len(current_rows) != EXPECTED_CURRENT_ROWS:
        raise SystemExit(f"unexpected current mention count: {len(current_rows)}")

    current_ids = [row.get("mention_id", "") for row in current_rows]
    if not all(current_ids) or len(current_ids) != len(set(current_ids)):
        raise SystemExit("current mention IDs are empty or duplicated")
    current_id_set = set(current_ids)
    historical_by_id = {row.get("mention_id", ""): row for row in head_rows if is_historical_surface_review(row)}
    if len(historical_by_id) != sum(is_historical_surface_review(row) for row in head_rows):
        raise SystemExit("historical surface review mention IDs are duplicated")
    missing = [row for mention_id, row in historical_by_id.items() if mention_id not in current_id_set]
    if len(missing) != EXPECTED_HISTORICAL_MISSING:
        raise SystemExit(f"expected {EXPECTED_HISTORICAL_MISSING} missing accepted rows, found {len(missing)}")

    candidate_ids: set[str] = set()
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as stream:
        candidate_rows = list(csv.DictReader(stream))
        candidate_ids = {row["candidate_id"] for row in candidate_rows}
    if len(candidate_ids) != len(candidate_rows):
        raise SystemExit("candidate IDs are duplicated")

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

    safe_rows: list[dict[str, str]] = []
    nested_rows: list[dict[str, str]] = []
    covered_ids: set[str] = set()
    conflict_ids: set[str] = set()
    compositional_ids: set[str] = set()
    restored_intervals: dict[str, list[tuple[int, int, str]]] = defaultdict(list)

    for historical in missing:
        mention_id = historical.get("mention_id", "")
        segment_id = historical.get("segment_id", "")
        segment = segment_map.get(segment_id)
        if not segment:
            raise SystemExit(f"{mention_id}: unknown source segment {segment_id}")
        if historical.get("candidate_id") not in candidate_ids:
            raise SystemExit(f"{mention_id}: candidate no longer exists: {historical.get('candidate_id')}")
        state = coverage_map.get(segment_id)
        if not state or state.get("migration_status") != "complete" or state.get("disposition") not in {"reviewed", "excluded"}:
            raise SystemExit(f"{mention_id}: segment is not recorded as processed: {segment_id}")

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

        start, end = int(historical["start_char"]), int(historical["end_char"])
        text = segment_texts[segment_id]
        if start < 0 or end <= start or end > len(text):
            raise SystemExit(f"{mention_id}: invalid source character span")
        source_slice = text[start:end]
        expected_surface = SURFACE_FORM_REPAIRS.get(mention_id, historical.get("surface_form", ""))
        if source_slice != expected_surface:
            raise SystemExit(
                f"{mention_id}: source slice mismatch; expected {expected_surface!r}, got {source_slice!r}"
            )

        overlaps: list[dict[str, str]] = []
        for current in existing_by_segment.get(segment_id, []):
            old_start, old_end = int(current["start_char"]), int(current["end_char"])
            if start < old_end and end > old_start:
                overlaps.append(current)

        if not overlaps:
            safe_rows.append(dict(historical, surface_form=source_slice))
            restored_intervals[segment_id].append((start, end, mention_id))
            continue

        covering_same_candidate = [
            current for current in overlaps
            if current["candidate_id"] == historical["candidate_id"]
            and int(current["start_char"]) <= start
            and int(current["end_char"]) >= end
        ]
        if covering_same_candidate:
            covered_ids.add(mention_id)
            continue

        if mention_id in COMPOSITIONAL_SKIP:
            parent_id = COMPOSITIONAL_SKIP[mention_id]
            parent = historical_by_id.get(parent_id)
            if not parent:
                raise SystemExit(f"{mention_id}: compositional parent row disappeared")
            if (
                parent["segment_id"] != segment_id
                or parent["candidate_id"] != "cand-6762"
                or int(parent["start_char"]) > start
                or int(parent["end_char"]) < end
            ):
                raise SystemExit(f"{mention_id}: compositional parent span changed")
            compositional_ids.add(mention_id)
            continue

        if mention_id in NESTED_CURRENT_RESTORE:
            expected_current_id, expected_candidate_id = NESTED_CURRENT_RESTORE[mention_id]
            if len(overlaps) != 1:
                raise SystemExit(f"{mention_id}: expected exactly one reviewed parent mention")
            parent = overlaps[0]
            if parent["mention_id"] != expected_current_id or parent["candidate_id"] != expected_candidate_id:
                raise SystemExit(f"{mention_id}: nested parent mapping changed")
            if not (int(parent["start_char"]) <= start and int(parent["end_char"]) >= end):
                raise SystemExit(f"{mention_id}: accepted nested place is not contained by the parent mention")
            nested_rows.append(dict(historical, surface_form=source_slice))
            restored_intervals[segment_id].append((start, end, mention_id))
            continue

        if mention_id in CONFLICT_SKIP:
            if {row["mention_id"] for row in overlaps} != CONFLICT_SKIP[mention_id]:
                raise SystemExit(f"{mention_id}: current conflict mapping changed")
            conflict_ids.add(mention_id)
            continue

        raise SystemExit(f"{mention_id}: unreviewed overlap with current table")

    if len(safe_rows) != 322 or len(nested_rows) != 3 or len(covered_ids) != 14 or len(conflict_ids) != 5 or len(compositional_ids) != 1:
        raise SystemExit(
            "classification changed: "
            f"safe={len(safe_rows)} nested={len(nested_rows)} covered={len(covered_ids)} "
            f"conflicts={len(conflict_ids)} compositional={len(compositional_ids)}"
        )
    if covered_ids & set(NESTED_CURRENT_RESTORE) or conflict_ids != set(CONFLICT_SKIP):
        raise SystemExit("accepted, covered, or conflict classification does not match the reviewed sets")

    allowed_internal_overlaps = HISTORICAL_NESTED_PAIRS
    actual_internal_overlaps: set[frozenset[str]] = set()
    for segment_id, spans in restored_intervals.items():
        for index, left in enumerate(spans):
            for right in spans[index + 1:]:
                if left[0] < right[1] and right[0] < left[1]:
                    actual_internal_overlaps.add(frozenset({left[2], right[2]}))
    if actual_internal_overlaps != allowed_internal_overlaps:
        raise SystemExit(f"historical nested mention pairs changed: {actual_internal_overlaps}")

    restored = sorted(safe_rows + nested_rows, key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
    return current_bytes, headers, current_rows, restored


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore only previously accepted S2 surface mentions that remain valid in the current table.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preview", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    current_bytes, headers, current_rows, restored = validate()
    counts_by_chapter: dict[str, int] = defaultdict(int)
    for row in restored:
        counts_by_chapter[row["segment_id"].split(":", 1)[0]] += 1
    print(
        f"restore_rows={len(restored)} current_rows={len(current_rows)} "
        f"projected_total={len(current_rows) + len(restored)}"
    )
    print("classification: 322 safe, 3 independent nested entities, 14 same-candidate covered, 5 superseded conflicts, 1 compositional subspan skipped")
    print("restored_by_chapter=" + json.dumps(dict(sorted(counts_by_chapter.items())), ensure_ascii=False))
    print("surface_form repair: m-s2-surface-a8a6c5978b050e4a now preserves the source line break in 'Central\\nEurope'")
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
    print(f"restored={len(restored)} previously accepted S2 surface mentions")


if __name__ == "__main__":
    main()
