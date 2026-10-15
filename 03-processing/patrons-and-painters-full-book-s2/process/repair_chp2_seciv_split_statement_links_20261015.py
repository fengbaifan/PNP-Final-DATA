from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
EXPECTED_SHA256 = "c8c7f68e421e84c5b707d321051b333dadd3911bbf6d5b2e4d8d79a723c4d993"
BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp2-list-split-links-20261015")
OLD_ID = "st-chp2-seciv-l6-17-committee-correspondence-and-list-preparation"
NEW_ID = "st-chp2-seciv-l6-17-committee-selection-lists-drawn"
CONTINUATION_ID = "st-chp2-seciv-l19-29-committee-lists-amended"
CITATION_ID = "st-chp2-seciv-l190-245-citation-05"
DISCUSSION_ID = "st-chp2-seciv-l19-29-committee-discussion-frequency"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def statement_reference_count(rows: list[dict]) -> int:
    count = 0
    for row in rows:
        for key, value in row.get("qualifiers", {}).items():
            if key.endswith("_statement_ids") or key in {
                "linked_statement_id",
                "related_statement_id",
                "continued_from_statement_id",
            }:
                values = value if isinstance(value, list) else [value]
                count += sum(isinstance(item, str) and item.startswith("st-") for item in values)
    return count


def build() -> bytes:
    if sha(STATEMENTS.read_bytes()) != EXPECTED_SHA256:
        raise SystemExit("statement table hash changed")
    originals: list[dict] = []
    raw_lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    for raw in raw_lines:
        if raw.strip():
            originals.append(json.loads(raw))
    by_id = {row["statement_id"]: row for row in originals}
    if len(by_id) != len(originals):
        raise SystemExit("duplicate statement IDs")
    expected = {OLD_ID, NEW_ID, CONTINUATION_ID, CITATION_ID, DISCUSSION_ID}
    if not expected.issubset(by_id):
        raise SystemExit("one or more target statements are missing")

    old_q = by_id[OLD_ID]["qualifiers"]
    new_q = by_id[NEW_ID]["qualifiers"]
    cont_q = by_id[CONTINUATION_ID]["qualifiers"]
    if old_q.get("related_statement_ids") != [CONTINUATION_ID]:
        raise SystemExit("unexpected old composite-statement relation links")
    if new_q.get("related_statement_ids") != [CONTINUATION_ID] or new_q.get("linked_statement_ids") != [CONTINUATION_ID]:
        raise SystemExit("unexpected new list-statement continuation links")
    if cont_q.get("continuation_of_statement_id") != OLD_ID:
        raise SystemExit("unexpected singular continuation target")
    if OLD_ID not in (cont_q.get("related_statement_ids") or []):
        raise SystemExit("old statement link is missing from the continuation")
    if cont_q.get("continued_from_statement_ids") != [NEW_ID]:
        raise SystemExit("unexpected duplicate continuation-list field")

    before_refs = statement_reference_count(originals)
    old_q.pop("related_statement_ids")
    new_q.pop("linked_statement_ids")
    cont_q["continuation_of_statement_id"] = NEW_ID
    cont_q["related_statement_ids"] = list(
        dict.fromkeys(NEW_ID if item == OLD_ID else item for item in cont_q["related_statement_ids"])
    )
    cont_q.pop("continued_from_statement_ids")
    after_refs = statement_reference_count(originals)
    if before_refs != 8125 or after_refs != 8122:
        raise SystemExit(f"unexpected statement-reference count: {before_refs} -> {after_refs}")

    output = []
    for raw in raw_lines:
        if not raw.strip():
            output.append(raw)
            continue
        row = json.loads(raw)
        statement_id = row["statement_id"]
        if statement_id in {OLD_ID, NEW_ID, CONTINUATION_ID}:
            row = by_id[statement_id]
            ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            output.append(raw)
    return b"".join(output)


def apply(data: bytes) -> None:
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP.name}")
    if sha(STATEMENTS.read_bytes()) != EXPECTED_SHA256:
        raise SystemExit("statement table changed after preview")
    shutil.copy2(STATEMENTS, BACKUP)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=STATEMENTS.parent, delete=False) as handle:
            temp_path = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, STATEMENTS)
    except Exception:
        shutil.copy2(BACKUP, STATEMENTS)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updated = build()
    print(f"book-statements.jsonl: {EXPECTED_SHA256} -> {sha(updated)}")
    print("Move the list continuation links to the split list statement; remove duplicate cross-links.")
    print("Statement-reference pointers: 8,125 -> 8,122 under the script's array-field count.")
    if args.apply:
        apply(updated)
        print(f"Applied with recovery backup {BACKUP.name}.")


if __name__ == "__main__":
    main()
