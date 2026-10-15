from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md"
BACKUP = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl.bak-s2-chp3-sec-ii-l33-38-quote-anchor-fix-20261010"
STATEMENT_ID = "st-chp3-secii-l33-38-philip-attracted-cultivated-people-and-decorated-church"
EXPECTED_SHA = "26a944ae926fd450683033f8afae2eab9542057a963e20836f17c6aa913908c8"
OLD_QUOTE = "He naturally attracted to himself many of the most cultivated spirits of the time."
NEW_QUOTE = OLD_QUOTE[:-1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(raw: bytes):
    rows = []
    offset = 0
    for line in raw.splitlines(keepends=True):
        if line.strip():
            rows.append((json.loads(line), offset, offset + len(line)))
        offset += len(line)
    return rows


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    actual = sha256(TABLE)
    if actual != EXPECTED_SHA:
        raise SystemExit(f"statement table SHA mismatch: {actual}")
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP}")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if NEW_QUOTE not in " ".join(source_lines[36:37]):
        raise SystemExit("corrected quotation is not an exact substring of source line 37")

    raw = TABLE.read_bytes()
    parsed = parse(raw)
    matches = [(row, start, end) for row, start, end in parsed if row.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"unexpected statement matches: {len(matches)}")
    row, start, end = matches[0]
    if row.get("original_quote") != OLD_QUOTE:
        raise SystemExit("original quote differs from expected text")
    q = row.get("qualifiers", {})
    if (q.get("source_line_start"), q.get("source_line_end"), q.get("relation_candidate")) != (37, 37, True):
        raise SystemExit("statement locator or classification changed")

    updated = dict(row)
    updated["original_quote"] = NEW_QUOTE
    replacement = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    newline = b"\r\n" if raw[start:end].endswith(b"\r\n") else b"\n"
    projected = raw[:start] + replacement + newline + raw[end:]
    print(json.dumps({
        "mode": "dry-run" if args.dry_run else "apply",
        "statement_id": STATEMENT_ID,
        "old_quote": OLD_QUOTE,
        "new_quote": NEW_QUOTE,
        "table_sha_before": actual,
        "backup": str(BACKUP.relative_to(ROOT)) if args.apply else None,
    }, ensure_ascii=False, indent=2))
    if args.dry_run:
        return

    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix="book-statements.quote-anchor-fix.", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(projected)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise

    written = [r for r, _, _ in parse(TABLE.read_bytes()) if r.get("statement_id") == STATEMENT_ID]
    if len(written) != 1 or written[0].get("original_quote") != NEW_QUOTE:
        raise SystemExit("post-write quotation check failed; recovery backup retained")
    print(f"post_write_sha256={sha256(TABLE)}")


if __name__ == "__main__":
    main()
