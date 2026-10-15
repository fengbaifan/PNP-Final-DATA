#!/usr/bin/env python3
"""Repair one p.338 split-claim quotation to match the immutable S0 source exactly."""

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
STATEMENTS_SHA256 = "3f0a4eeabe13e2c81021d65b8057a2ac71233d6f341ac448e7383eeccd4641ef"
STATEMENT_ID = "st-chp13-p338-pasquali-books-aimed-at-public-of-novelli-drawings"
OLD_QUOTE = "which were aimed at the very same sort of public as that illustrated in Novelli's drawings"
BACKUP_SUFFIX = ".bak-s2-ch13-p338-source-quote-fix-20261014"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    actual = hashlib.sha256(STATEMENTS.read_bytes()).hexdigest()
    if actual != STATEMENTS_SHA256:
        raise SystemExit(f"preflight failed: book-statements.jsonl SHA-256 {actual} != {STATEMENTS_SHA256}")

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    source_line = lines[64]
    start = source_line.find("which were aimed at the very same sort of public")
    end = source_line.find(", there is a complete lack", start)
    if start < 0 or end < 0:
        raise SystemExit("preflight failed: source quote boundaries not found on p.338 L65")
    corrected_quote = source_line[start:end]

    rows = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line]
    matches = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1 or matches[0].get("original_quote") != OLD_QUOTE:
        raise SystemExit("preflight failed: target statement or pre-repair quote changed")
    if "Novelli\u2019s drawings" not in corrected_quote:
        raise SystemExit("preflight failed: extracted source quote does not preserve S0 apostrophe")
    matches[0]["original_quote"] = corrected_quote
    print(f"statement={STATEMENT_ID}")
    print(f"corrected quotation={corrected_quote!r}")
    if not args.apply:
        print("DRY RUN only; pass --apply to save.")
        return

    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
    shutil.copy2(STATEMENTS, backup)
    data = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    fd, temp_name = tempfile.mkstemp(prefix=STATEMENTS.name + ".", suffix=".tmp", dir=STATEMENTS.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, STATEMENTS)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(f"APPLIED; backup={backup.name}; SHA-256={hashlib.sha256(STATEMENTS.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
