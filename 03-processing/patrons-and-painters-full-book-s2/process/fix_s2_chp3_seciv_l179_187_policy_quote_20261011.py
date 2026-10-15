from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
STATEMENT_ID = "st-chp3-seciv-l179-187-deliberate-policy-evidenced-by-commissions"
BEFORE_SHA = "3c74ee51b26e6091903ca6d69323547d7e4d9a17e3d25750c4b17e45fe3c1dfb"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-seciv-l179-187-policy-quote-20261011")
CORRECT_QUOTE = (
    "That this policy was now deliberate is shown by other commissions of the time— "
    "most notably the gruesome polychrome figure by Legros of St Stanislas Kostka on his deathbed"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    before = TABLE.read_bytes()
    if digest(before) != BEFORE_SHA:
        raise SystemExit("statement table changed since the reviewed p.93 writeback")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if CORRECT_QUOTE not in source_lines[180]:
        raise SystemExit("corrected quote is not an exact substring of source line L181")

    lines = before.splitlines(keepends=True)
    matches = 0
    out: list[bytes] = []
    for raw in lines:
        row = json.loads(raw)
        if row.get("statement_id") == STATEMENT_ID:
            matches += 1
            row["original_quote"] = CORRECT_QUOTE
            raw = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        out.append(raw)
    if matches != 1:
        raise SystemExit(f"expected one target statement, found {matches}")

    shutil.copy2(TABLE, BACKUP)
    TABLE.write_bytes(b"".join(out))
    after = TABLE.read_bytes()
    if digest(after) == digest(before):
        raise SystemExit("quote repair did not change the table")
    print(json.dumps({
        "statement_id": STATEMENT_ID,
        "quote_matches_source_line_181": True,
        "before_sha256": digest(before),
        "after_sha256": digest(after),
        "recovery_copy": str(BACKUP.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
