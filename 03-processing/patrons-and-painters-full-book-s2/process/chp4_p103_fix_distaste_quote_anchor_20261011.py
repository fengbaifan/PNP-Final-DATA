#!/usr/bin/env python3
"""Correct the source-exact quote anchor for the p.103 distaste statement."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
STATEMENT_ID = "st-chp4-sec-ii-l46-51-cassiano-distaste-pietro-friendship"
OLD_QUOTE = "To Cassiano dal Pozzo all this was clearly most distasteful"
NEW_QUOTE = "Cassiano dal Pozzo all this was clearly most distasteful"
EXPECTED_SHA256 = "f4c30d07fef5db6db6514356130cfdc31bbf757d36dbacfce90586e0d4f2232a"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp4-p103-distaste-quote-anchor-20261011")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if sha256(raw) != EXPECTED_SHA256:
        raise SystemExit("preflight failed: statement table hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if len(source_lines) < 50 or NEW_QUOTE not in source_lines[49]:
        raise SystemExit("preflight failed: exact replacement is absent from source line 50")

    lines = raw.decode("utf-8-sig").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    matches = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1 or matches[0].get("original_quote") != OLD_QUOTE:
        raise SystemExit("preflight failed: target statement or old quote differs")
    matches[0]["original_quote"] = NEW_QUOTE
    rendered = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    rendered_bytes = rendered.encode("utf-8")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "statement_id": STATEMENT_ID,
        "source_line": 50,
        "old_quote": OLD_QUOTE,
        "new_quote": NEW_QUOTE,
        "table_sha256_before": sha256(raw),
        "table_sha256_after": sha256(rendered_bytes),
        "backup": BACKUP.name if args.apply else None,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"apply failed: backup already exists: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    temp = TABLE.with_name(TABLE.name + ".tmp-s2-distaste-quote-anchor")
    try:
        temp.write_bytes(rendered_bytes)
        temp.replace(TABLE)
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise
    print("APPLY_OK SHA256 " + sha256(TABLE.read_bytes()))


if __name__ == "__main__":
    main()
