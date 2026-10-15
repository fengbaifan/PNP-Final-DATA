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
EXPECTED_TABLE_SHA256 = "25dc032469708f0aa806fe26831a0a4a0b7b8dd4e5f6854c0912757ae0e56098"
EXPECTED_SOURCE_SHA256 = "96aa11521c311c17676147c3ec99fb47d7cf9042a13bc58768c3742553ac5f83"
EXPECTED_CANDIDATES_SHA256 = "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae"
EXPECTED_MENTIONS_SHA256 = "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647"
SEGMENT = "front-matter:00_05_List_of_Plates:l198-198"
SOURCE_RELATIVE = "02-sources/02-Markdown/00_05_List_of_Plates.md"
BOOK_ID = "cand-2962"
BACKUP = TABLE.with_name(
    "book-statements.jsonl.bak-s2-front-matter-second-edition-intro-citations-l198-20261010"
)

DECISIONS = {
    "st-fm-2ed-l198-01-montaiglon": {
        "old_subject": "cand-3608",
        "old_object": "cand-3605",
        "source_line": 198,
        "quote": "1 Montaiglon, III, p. 240.",
        "page": 240,
        "volume": "III",
        "context": "Footnote 1 gives the source locator for the Poerson letter quoted in the introduction.",
        "author_key": "editor_or_author_candidate_id",
        "author_id": "cand-3706",
        "qualification": "The cited correspondence collection and page are identified in the book; the cited page was not independently consulted in this pass.",
    },
    "st-fm-2ed-l198-02-gilmartin": {
        "old_subject": "cand-3613",
        "old_object": "cand-3601",
        "source_line": 198,
        "quote": "2 Gilmartin.",
        "context": "Footnote 2 gives the source for Haskell's S. Clemente redecoration discussion.",
        "author_key": "author_candidate_id",
        "author_id": "cand-3814",
        "qualification": "The footnote gives only the surname; the existing bibliography-linked archive candidate identifies the cited item, which was not independently consulted in this pass.",
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
        description="Normalize the two bibliography pointers in the second-edition introduction; default is dry-run."
    )
    parser.add_argument("--apply", action="store_true", help="write after preflight")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    actual_table_hash = digest(raw)
    if actual_table_hash != EXPECTED_TABLE_SHA256:
        raise SystemExit(
            f"statement-table SHA mismatch: expected {EXPECTED_TABLE_SHA256}, got {actual_table_hash}"
        )
    source_raw = SOURCE.read_bytes()
    if digest(source_raw) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("S0 source SHA mismatch")
    if digest(CANDIDATES.read_bytes()) != EXPECTED_CANDIDATES_SHA256:
        raise SystemExit("candidate-table SHA mismatch")
    if digest(MENTIONS.read_bytes()) != EXPECTED_MENTIONS_SHA256:
        raise SystemExit("mention-table SHA mismatch")

    source_lines = source_raw.decode("utf-8-sig").splitlines()
    if len(source_lines) < 198 or "Montaiglon, III, p. 240." not in source_lines[197] or "Gilmartin." not in source_lines[197]:
        raise SystemExit("source line 198 citation anchor mismatch")
    segment = next(
        (r for r in read_jsonl(SEGMENTS) if r.get("segment_id") == SEGMENT), None
    )
    if (
        segment is None
        or segment.get("source_file") != SOURCE_RELATIVE
        or segment.get("line_start") != 198
        or segment.get("line_end") != 198
        or segment.get("asset_sha256") != EXPECTED_SOURCE_SHA256
    ):
        raise SystemExit("S0 segment/source mapping mismatch")
    coverage = next(
        (r for r in read_csv(COVERAGE) if r.get("segment_id") == SEGMENT), None
    )
    if not coverage or (coverage.get("disposition"), coverage.get("migration_status")) != (
        "reviewed",
        "complete",
    ):
        raise SystemExit("S2 segment coverage is not reviewed/complete")

    candidates = {r["candidate_id"]: r for r in read_csv(CANDIDATES)}
    expected_types = {
        BOOK_ID: "archive",
        "cand-3601": "archive",
        "cand-3605": "archive",
        "cand-3608": "archive",
        "cand-3706": "person",
        "cand-3814": "person",
    }
    for candidate_id, expected_type in expected_types.items():
        if candidate_id not in candidates or candidates[candidate_id].get("suggested_type") != expected_type:
            raise SystemExit(f"candidate/type mismatch: {candidate_id}")

    rows = read_jsonl(TABLE)
    by_id = {r.get("statement_id"): r for r in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    segment_rows = [r for r in rows if r.get("segment_id") == SEGMENT]
    if {r.get("statement_id") for r in segment_rows} != set(DECISIONS):
        raise SystemExit("segment statement coverage mismatch")

    updated_by_id: dict[str, dict] = {}
    for statement_id, decision in DECISIONS.items():
        row = by_id[statement_id]
        q = row.get("qualifiers") or {}
        if (
            row.get("source_file") != SOURCE_RELATIVE
            or row.get("origin") != "book"
            or row.get("predicate") != "footnote_citation_to_source"
            or row.get("subject_candidate_id") != decision["old_subject"]
            or row.get("object_candidate_id") != decision["old_object"]
            or q.get("source_line_start") != decision["source_line"]
            or q.get("source_line_end") != decision["source_line"]
            or row.get("original_quote") != decision["quote"]
            or "relation_candidate" in q
        ):
            raise SystemExit(f"statement preflight mismatch: {statement_id}")

        updated = deepcopy(row)
        updated["subject_candidate_id"] = BOOK_ID
        updated["predicate"] = "cites"
        updated["qualifiers"]["claim"] = (
            f"Haskell's book cites the existing archive candidate for the {decision['context']}"
        )
        updated["qualifiers"]["qualification"] = decision["qualification"]
        updated["qualifiers"][decision["author_key"]] = decision["author_id"]
        updated["qualifiers"]["cited_material_not_independently_consulted"] = True
        updated["qualifiers"]["relation_candidate"] = True
        updated["qualifiers"]["relation_candidate_note"] = (
            "S2 cites candidate: the footnote explicitly cites this archive from Haskell's book. "
            "The citation records a bibliographic link and does not independently validate the cited source's claims; no formal S6 edge is created."
        )
        updated_by_id[statement_id] = updated

    output_lines: list[str] = []
    seen: set[str] = set()
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output_lines.append(line)
            continue
        current = json.loads(line)
        statement_id = current.get("statement_id")
        if statement_id in updated_by_id:
            output_lines.append(
                json.dumps(updated_by_id[statement_id], ensure_ascii=False, separators=(",", ":"))
            )
            seen.add(statement_id)
        else:
            output_lines.append(line)
    if seen != set(DECISIONS):
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output_lines) + "\n").encode("utf-8")

    print(
        "preflight passed: source/segment/coverage, table SHA, candidate and mention SHA, "
        "archive/person types, exact footnote text and statement anchors verified"
    )
    print("normalization: two book-footnote source pointers -> cand-2962 cites archive; both retain page/context and remain S2 only")
    print(f"output_sha256={digest(result)}")
    if not args.apply:
        print(f"dry-run only; table unchanged; input_sha256={actual_table_hash}")
        return

    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
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
