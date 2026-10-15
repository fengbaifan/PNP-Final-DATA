from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
STATEMENT_ID = "st-chp2-seciv-l91-94-fresco-covers-ceiling-without-illusionistic-scene"
OLD = "The whole ceiling is covered with the fresco."
NEW = "The whole ceiling is covered with the fresco"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-p51-ceiling-quote-punctuation-20261013")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()

    before = digest(TABLE)
    if args.expected_sha256 and before != args.expected_sha256:
        raise SystemExit(f"stale table hash: expected {args.expected_sha256}, got {before}")

    lines = TABLE.read_text(encoding="utf-8-sig").splitlines()
    matches = [i for i, line in enumerate(lines) if json.loads(line).get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one target row, found {len(matches)}")
    row_index = matches[0]
    row = json.loads(lines[row_index])
    if row.get("original_quote") != OLD:
        raise SystemExit(f"unexpected original_quote: {row.get('original_quote')!r}")
    updated = dict(row)
    updated["original_quote"] = NEW
    lines[row_index] = json.dumps(updated, ensure_ascii=False)
    rendered = "\n".join(lines) + "\n"

    print(f"target={STATEMENT_ID}")
    print(f"old_quote={OLD!r}")
    print(f"new_quote={NEW!r}")
    print(f"table_sha256={before}")
    if not args.apply:
        print("mode=preview; no files changed")
        return

    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    tmp = TABLE.with_suffix(TABLE.suffix + ".tmp-s2-p51-quote-fix")
    tmp.write_text(rendered, encoding="utf-8")
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}; new_sha256={digest(TABLE)}")


if __name__ == "__main__":
    main()
