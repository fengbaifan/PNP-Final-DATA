from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/00_05_List_of_Plates.md"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
EXPECTED_TABLE_SHA256 = "65b74e8bb28082c7c792a4d75008f07de41c4531a0044727bfe2f614c9b4e125"
EXPECTED_SOURCE_SHA256 = "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83"
SEGMENT = "front-matter:00_05_List_of_Plates:l32-65"
SOURCE_RELATIVE = "02-sources/02-Markdown/00_05_List_of_Plates.md"
BACKUP = TABLE.with_name(
    "book-statements.jsonl.bak-s2-front-matter-plate-list-p09-relations-20261010"
)

ROWS = {
    "st-fm-pl-p09-frontispiece-of": {
        "predicate": "frontispiece_of",
        "subject": "cand-4050",
        "object": "cand-3595",
        "line_start": 49,
        "line_end": 50,
        "claim": "The frontispiece belongs to Girolamo Teti’s Aedes Barberinae ad Quirinalem.",
        "quote": (
            "9 Guido Abbatini: Frontispiece of Girolamo Teti: Aedes Barberinae ad\n"
            "Quirinalem, Rome 1642, with view of Palazzo Barberini 56"
        ),
        "anchors": [
            (49, "Frontispiece of Girolamo Teti: Aedes Barberinae ad"),
            (50, "Quirinalem, Rome 1642"),
        ],
        "mentions": {
            "m-fm-pl-p09-frontispiece": ("cand-4050", "Frontispiece", 782, 794),
            "m-fm-pl-p09-book": (
                "cand-3595",
                "Aedes Barberinae ad\nQuirinalem",
                813,
                843,
            ),
        },
        "note": (
            "The caption explicitly identifies this frontispiece as belonging to "
            "Girolamo Teti's Aedes Barberinae ad Quirinalem. This is a caption-level "
            "work-to-publication relation; the publication candidate's identity and "
            "type remain open for S3."
        ),
    },
    "st-fm-pl-p09-view": {
        "predicate": "frontispiece_depicts_view_of",
        "subject": "cand-4050",
        "object": "cand-3118",
        "line_start": 49,
        "line_end": 50,
        "claim": "The caption says the frontispiece includes a view of Palazzo Barberini.",
        "quote": (
            "9 Guido Abbatini: Frontispiece of Girolamo Teti: Aedes Barberinae ad\n"
            "Quirinalem, Rome 1642, with view of Palazzo Barberini 56"
        ),
        "anchors": [
            (50, "with view of Palazzo Barberini"),
        ],
        "mentions": {
            "m-fm-pl-p09-frontispiece": ("cand-4050", "Frontispiece", 782, 794),
            "m-fm-pl-p09-palace": (
                "cand-3118",
                "Palazzo Barberini",
                869,
                886,
            ),
        },
        "note": (
            "The caption explicitly says the frontispiece includes a view of Palazzo "
            "Barberini. This records the represented view only; it does not assert "
            "current custody, ownership, or a separately identified painting."
        ),
    },
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify two plate-list S2 relation candidates; default is dry-run."
    )
    parser.add_argument(
        "--apply", action="store_true", help="write after all preflight checks pass"
    )
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if digest(raw) != EXPECTED_TABLE_SHA256:
        raise SystemExit(
            f"statement-table SHA mismatch: expected {EXPECTED_TABLE_SHA256}, got {digest(raw)}"
        )
    source_raw = SOURCE.read_bytes()
    if digest(source_raw) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("S0 plate-list source SHA mismatch")

    source_lines = source_raw.decode("utf-8-sig").splitlines()
    segment_rows = read_jsonl(SEGMENTS)
    segment_row = next(
        (row for row in segment_rows if row.get("segment_id") == SEGMENT), None
    )
    if (
        segment_row is None
        or segment_row.get("source_file") != SOURCE_RELATIVE
        or segment_row.get("line_start") != 32
        or segment_row.get("line_end") != 65
        or segment_row.get("asset_sha256") != EXPECTED_SOURCE_SHA256
    ):
        raise SystemExit("S0 segment/source mapping mismatch")

    coverage = read_csv(COVERAGE)
    coverage_row = next(
        (row for row in coverage if row.get("segment_id") == SEGMENT), None
    )
    if not coverage_row or (
        coverage_row.get("disposition"), coverage_row.get("migration_status")
    ) != ("reviewed", "complete"):
        raise SystemExit("S2 segment coverage is not reviewed/complete")

    candidates = {
        row["candidate_id"]: row for row in read_csv(CANDIDATES)
    }
    expected_candidate_types = {
        "cand-4050": "work",
        "cand-3595": "archive",
        "cand-3118": "place",
    }
    for candidate_id, expected_type in expected_candidate_types.items():
        row = candidates.get(candidate_id)
        if row is None or row.get("suggested_type") != expected_type:
            raise SystemExit(f"candidate/type mismatch: {candidate_id}")

    mentions = {row["mention_id"]: row for row in read_csv(MENTIONS)}
    for statement_id, spec in ROWS.items():
        for line_number, anchor in spec["anchors"]:
            if line_number > len(source_lines) or anchor not in source_lines[line_number - 1]:
                raise SystemExit(f"source anchor mismatch: {statement_id} line {line_number}")
        for mention_id, expected in spec["mentions"].items():
            row = mentions.get(mention_id)
            actual = (
                row.get("candidate_id"),
                row.get("surface_form"),
                int(row.get("start_char", -1)),
                int(row.get("end_char", -1)),
                row.get("segment_id"),
            ) if row else None
            required = (*expected, SEGMENT)
            if actual != required:
                raise SystemExit(f"mention preflight mismatch: {mention_id}")

    rows = read_jsonl(TABLE)
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")

    updated: dict[str, dict] = {}
    for statement_id, spec in ROWS.items():
        row = by_id.get(statement_id)
        if row is None:
            raise SystemExit(f"missing statement: {statement_id}")
        q = row.get("qualifiers") or {}
        if (
            row.get("segment_id") != SEGMENT
            or row.get("source_file") != SOURCE_RELATIVE
            or row.get("origin") != "book"
            or row.get("predicate") != spec["predicate"]
            or row.get("subject_candidate_id") != spec["subject"]
            or row.get("object_candidate_id") != spec["object"]
            or q.get("source_line_start") != spec["line_start"]
            or q.get("source_line_end") != spec["line_end"]
            or q.get("claim") != spec["claim"]
            or row.get("original_quote") != spec["quote"]
            or q.get("speaker") != "plate caption"
            or q.get("text_layer") != "plate-list caption"
            or "relation_candidate" in q
        ):
            raise SystemExit(f"statement preflight mismatch: {statement_id}")
        revised = deepcopy(row)
        revised["qualifiers"]["relation_candidate"] = True
        revised["qualifiers"]["relation_candidate_note"] = spec["note"]
        updated[statement_id] = revised

    output: list[str] = []
    seen: set[str] = set()
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        statement_id = row["statement_id"]
        if statement_id in updated:
            output.append(
                json.dumps(updated[statement_id], ensure_ascii=False, separators=(",", ":"))
            )
            seen.add(statement_id)
        else:
            output.append(line)
    if seen != set(ROWS):
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output) + "\n").encode("utf-8")

    print(
        f"preflight passed: {len(seen)}/{len(ROWS)} statements; table/S0 SHA, "
        "segment, coverage, candidate types, endpoint mentions and exact source anchors verified"
    )
    for statement_id, spec in ROWS.items():
        print(
            f"review {statement_id}: relation_candidate absent -> true; "
            f"{spec['subject']} -> {spec['object']}"
        )
        print(f"  rationale: {spec['note']}")
    print(f"output_sha256={digest(result)}")
    if not args.apply:
        print(f"dry-run only; table unchanged; input_sha256={digest(raw)}")
        return

    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(
        prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent
    )
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={digest(result)}")


if __name__ == "__main__":
    main()
