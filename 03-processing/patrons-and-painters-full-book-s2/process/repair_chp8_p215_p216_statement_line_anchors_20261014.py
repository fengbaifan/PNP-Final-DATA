"""Correct five S2 source-line anchors against the unchanged p.215-216 S0 text."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
EXPECTED_TABLE_SHA = "e8253b1d1afd68b050dccdecd655d04ec4bc1490afad4cd595aa1e69cd27d3e0"
EXPECTED_SOURCE_SHA = "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6"
BACKUP_SUFFIX = ".bak-s2-chp8-p215-p216-line-anchor-repair-20261014"
UPDATES = {
    "st-chp8-p215-gothic-fresco-traces-remain": (13, 13),
    "st-chp8-p215-decoration-changed-and-altar-paintings-appeared": (13, 13),
    "st-chp8-p215-stucco-ornament-covers-dome-interior": (13, 13),
    "st-chp8-p215-ricchini-planned-dome-1612": (13, 14),
    "st-chp8-p216-milan-artists-commissioned-killing-of-sisera": (33, 34),
}
OLD_LINES = {
    "st-chp8-p215-gothic-fresco-traces-remain": (14, 14),
    "st-chp8-p215-decoration-changed-and-altar-paintings-appeared": (14, 14),
    "st-chp8-p215-stucco-ornament-covers-dome-interior": (14, 14),
    "st-chp8-p215-ricchini-planned-dome-1612": (14, 15),
    "st-chp8-p216-milan-artists-commissioned-killing-of-sisera": (33, 33),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    if sha(raw) != EXPECTED_TABLE_SHA:
        raise SystemExit("book-statements changed; recheck the affected rows before repair")
    source_raw = SOURCE.read_bytes()
    if sha(source_raw) != EXPECTED_SOURCE_SHA:
        raise SystemExit("S0 source changed; recheck source anchors before repair")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()

    raw_lines = raw.decode("utf-8-sig").splitlines()
    rows = [json.loads(line) for line in raw_lines if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows) or set(UPDATES) - set(by_id):
        raise SystemExit("statement IDs are missing or duplicated")
    changed = set(UPDATES)
    for statement_id, (new_start, new_end) in UPDATES.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers") or {}
        old = (qualifiers.get("source_line_start"), qualifiers.get("source_line_end"))
        if old != OLD_LINES[statement_id]:
            raise SystemExit(f"unexpected old source lines for {statement_id}: {old}")
        if row.get("source_file") != SOURCE_REL:
            raise SystemExit(f"unexpected source file for {statement_id}")
        quote = row.get("original_quote", "")
        source_span = "\n".join(lines[new_start - 1:new_end])
        if quote not in source_span:
            raise SystemExit(f"quote does not match corrected source lines for {statement_id}")
        qualifiers["source_line_start"] = new_start
        qualifiers["source_line_end"] = new_end
        row["qualifiers"] = qualifiers

    output_lines = [
        json.dumps(row, ensure_ascii=False) if row["statement_id"] in changed else raw_line
        for raw_line, row in zip(raw_lines, rows, strict=True)
    ]
    output = ("\n".join(output_lines) + "\n").encode("utf-8")
    checked = [json.loads(line) for line in output.decode("utf-8").splitlines()]
    for row in checked:
        if row["statement_id"] in UPDATES:
            q = row["qualifiers"]
            start, end = UPDATES[row["statement_id"]]
            if row["original_quote"] not in "\n".join(lines[start - 1:end]):
                raise SystemExit(f"serialized quote check failed for {row['statement_id']}")

    print("DRY RUN source-line anchor repair")
    for statement_id, (start, end) in UPDATES.items():
        print(f"{statement_id}: {OLD_LINES[statement_id]} -> {(start, end)}")
    print(f"book-statements before={EXPECTED_TABLE_SHA} after={sha(output)}")
    if not args.apply:
        print("No files written. Use --apply after reviewing the anchors.")
        return

    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("repair backup already exists")
    shutil.copy2(TABLE, backup)
    with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False, suffix=".tmp") as stream:
        stream.write(output)
        temporary = Path(stream.name)
    temporary.replace(TABLE)
    print(f"APPLIED; recovery copy: {backup.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
