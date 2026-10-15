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
EXPECTED_TABLE_SHA256 = "55d50516686ebed39fa78c55874e430fa9757466c96d4b72d7b2a21ce24d8c7f"
EXPECTED_SOURCE_SHA256 = "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83"
SEGMENT = "front-matter:00_05_List_of_Plates:l123-138"
SOURCE_RELATIVE = "02-sources/02-Markdown/00_05_List_of_Plates.md"
STATEMENT_ID = "st-fm-pl-p55a-carrier"
BACKUP = TABLE.with_name(
    "book-statements.jsonl.bak-s2-front-matter-plate-list-p55a-carrier-20261010"
)


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
        description="Classify one plate-list S2 relation candidate; default is dry-run."
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
    if 133 > len(source_lines) or "Dedicatory frontispiece to Etchings" not in source_lines[132]:
        raise SystemExit("source line 133 anchor mismatch")

    segment_row = next(
        (row for row in read_jsonl(SEGMENTS) if row.get("segment_id") == SEGMENT), None
    )
    if (
        segment_row is None
        or segment_row.get("source_file") != SOURCE_RELATIVE
        or segment_row.get("line_start") != 123
        or segment_row.get("line_end") != 138
        or segment_row.get("asset_sha256") != EXPECTED_SOURCE_SHA256
    ):
        raise SystemExit("S0 segment/source mapping mismatch")
    coverage_row = next(
        (row for row in read_csv(COVERAGE) if row.get("segment_id") == SEGMENT), None
    )
    if not coverage_row or (
        coverage_row.get("disposition"), coverage_row.get("migration_status")
    ) != ("reviewed", "complete"):
        raise SystemExit("S2 segment coverage is not reviewed/complete")

    candidates = {row["candidate_id"]: row for row in read_csv(CANDIDATES)}
    for candidate_id, expected_type in {"cand-4013": "work", "cand-4181": "archive"}.items():
        candidate = candidates.get(candidate_id)
        if candidate is None or candidate.get("suggested_type") != expected_type:
            raise SystemExit(f"candidate/type mismatch: {candidate_id}")

    mentions = {row["mention_id"]: row for row in read_csv(MENTIONS)}
    expected_mentions = {
        "m-fm-pl-p55a-work": ("cand-4013", "Canaletto: Dedicatory frontispiece to Etchings", 1199, 1245),
        "m-fm-pl-p55a-carrier": ("cand-4181", "Etchings", 1237, 1245),
    }
    for mention_id, expected in expected_mentions.items():
        row = mentions.get(mention_id)
        actual = (
            row.get("candidate_id"),
            row.get("surface_form"),
            int(row.get("start_char", -1)),
            int(row.get("end_char", -1)),
            row.get("segment_id"),
        ) if row else None
        if actual != (*expected, SEGMENT):
            raise SystemExit(f"mention preflight mismatch: {mention_id}")

    rows = read_jsonl(TABLE)
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    row = by_id.get(STATEMENT_ID)
    if row is None:
        raise SystemExit(f"missing statement: {STATEMENT_ID}")
    q = row.get("qualifiers") or {}
    if (
        row.get("segment_id") != SEGMENT
        or row.get("source_file") != SOURCE_RELATIVE
        or row.get("origin") != "book"
        or row.get("predicate") != "frontispiece_of"
        or row.get("subject_candidate_id") != "cand-4013"
        or row.get("object_candidate_id") != "cand-4181"
        or q.get("source_line_start") != 133
        or q.get("source_line_end") != 133
        or q.get("claim")
        != "The caption identifies the Canaletto frontispiece as belonging to a set called Etchings."
        or row.get("original_quote") != "55 a Canaletto: Dedicatory frontispiece to Etchings "
        or q.get("speaker") != "plate caption"
        or q.get("text_layer") != "plate-list caption"
        or "relation_candidate" in q
    ):
        raise SystemExit(f"statement preflight mismatch: {STATEMENT_ID}")

    note = (
        "The plate list calls this Canaletto work a dedicatory frontispiece to a set "
        "called Etchings. This supports the work-to-carrier relation, while the set's "
        "formal title, edition, and publication identity remain unresolved."
    )
    updated = deepcopy(row)
    updated["qualifiers"]["relation_candidate"] = True
    updated["qualifiers"]["relation_candidate_note"] = note

    output: list[str] = []
    seen = False
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output.append(line)
            continue
        current = json.loads(line)
        if current.get("statement_id") == STATEMENT_ID:
            output.append(json.dumps(updated, ensure_ascii=False, separators=(",", ":")))
            seen = True
        else:
            output.append(line)
    if not seen:
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output) + "\n").encode("utf-8")

    print(
        "preflight passed: statement/source SHA, segment, reviewed coverage, "
        "candidate types, exact mentions and source anchor verified"
    )
    print(f"review {STATEMENT_ID}: relation_candidate absent -> true; cand-4013 -> cand-4181")
    print(f"rationale: {note}")
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
