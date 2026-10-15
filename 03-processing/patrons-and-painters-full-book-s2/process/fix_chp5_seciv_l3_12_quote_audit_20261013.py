from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_iv.md"
PREVIOUS_BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp5-seciv-l3-12-20261013")
EXPECTED_TABLE_SHA = "b2a93b38346c8023096a2ecc233850fba5475cd0c441510af10b4f62db8398ab"
EXPECTED_SOURCE_SHA = "805df7b2bdc296cf987069cb0cea829bc07ec8932e28b075e9575f0c2ac67c4f"
STATEMENT_ID = "st-chp5-p142-simonelli-early-patron-and-vanlaer-interest"
BACKUP_SUFFIX = ".bak-s2-chp5-seciv-l3-12-quote-auditfix-20261013"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if digest(TABLE) != EXPECTED_TABLE_SHA or digest(SOURCE) != EXPECTED_SOURCE_SHA:
        raise SystemExit("guard failed: source or statement table changed")
    current = load(TABLE)
    previous = load(PREVIOUS_BACKUP)
    row = next((item for item in current if item.get("statement_id") == STATEMENT_ID), None)
    old = next((item for item in previous if item.get("statement_id") == STATEMENT_ID), None)
    if row is None or old is None:
        raise SystemExit("guard failed: target statement or pre-write source quote is missing")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    cited = " ".join("\n".join(source_lines[3:5]).split())
    old_quote = old.get("original_quote", "")
    if " ".join(old_quote.split()) not in cited:
        raise SystemExit("guard failed: recovery quote does not match S0 lines 4-5")
    if row.get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("guard failed: statement classification changed")
    row["original_quote"] = old_quote
    if not args.apply:
        print("PREVIEW only; no table writes")
        print(f"will restore exact original_quote from pre-write backup ({len(old_quote)} characters)")
        return
    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"guard failed: backup already exists: {backup.name}")
    shutil.copy2(TABLE, backup)
    with TABLE.open("w", encoding="utf-8", newline="") as f:
        f.write("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in current))
    print(f"restored exact source-matching quote; backup: {backup.name}")


if __name__ == "__main__":
    main()
