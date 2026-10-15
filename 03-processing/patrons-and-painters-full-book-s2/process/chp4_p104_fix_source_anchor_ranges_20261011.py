#!/usr/bin/env python3
"""Correct four source-line spans in the p.104 S2 relation batch."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
EXPECTED_TABLE_SHA256 = "0336389ad8bb723068a2bfb41e5f1067b26ea14bd15c66fd1599c44423713ecf"
EXPECTED_SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp4-p104-source-anchor-fix-20261011")
RANGES = {
    "st-chp4-sec-ii-l53-63-mannerism-opposed-classical-path": (59, 60),
    "st-chp4-sec-ii-l53-63-naturalism-opposed-classical-path": (59, 60),
    "st-chp4-sec-ii-l53-63-guglielmo-created-paul-tomb": (54, 56),
    "st-chp4-sec-ii-l53-63-duquesnoy-created-modelli": (56, 58),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    table_bytes = TABLE.read_bytes()
    source_bytes = SOURCE.read_bytes()
    if sha(table_bytes) != EXPECTED_TABLE_SHA256:
        raise SystemExit("preflight failed: statement table hash changed")
    if sha(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("preflight failed: source hash changed")

    rows = [json.loads(line) for line in table_bytes.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("preflight failed: duplicate statement id")
    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    for statement_id, (start, end) in RANGES.items():
        row = by_id.get(statement_id)
        if row is None:
            raise SystemExit(f"preflight failed: missing {statement_id}")
        q = row.get("qualifiers", {})
        if (q.get("source_line_start"), q.get("source_line_end")) == (start, end):
            raise SystemExit(f"preflight failed: {statement_id} already has target range")
        if not (start <= end <= len(source_lines)):
            raise SystemExit(f"preflight failed: invalid target range for {statement_id}")
        quote = row.get("original_quote", "")
        source_span = "\n".join(source_lines[start - 1 : end])
        if not quote or quote not in source_span:
            raise SystemExit(f"preflight failed: quote is not contained by source span for {statement_id}")

    print(f"mode={'apply' if args.apply else 'dry-run'}; rows={len(RANGES)}; table_sha256={sha(table_bytes)}")
    for statement_id, span in RANGES.items():
        print(f"{statement_id}: {span[0]}-{span[1]}")
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"preflight failed: backup already exists: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    for statement_id, (start, end) in RANGES.items():
        by_id[statement_id]["qualifiers"]["source_line_start"] = start
        by_id[statement_id]["qualifiers"]["source_line_end"] = end
    TABLE.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
        newline="",
    )
    print(f"backup={BACKUP.name}; new_table_sha256={sha(TABLE.read_bytes())}")


if __name__ == "__main__":
    main()
