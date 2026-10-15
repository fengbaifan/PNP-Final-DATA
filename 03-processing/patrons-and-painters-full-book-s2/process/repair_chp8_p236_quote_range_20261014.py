"""Correct the p.236 Ricci picture-group statement's cited source line."""
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
EXPECTED_TABLE_SHA256 = "a88061a75c65d011f680dc34b201729066dd6db95a73e97d7ecab2dd6ede7d5a"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp8-p236-quote-range-repair-20261014")
STATEMENT_ID = "st-chp8-p236-ricci-small-figure-pictures"
EXPECTED_QUOTE = "Ricci also painted various pictures for him at this time, particularly of little figures disporting themselves against architectural backgrounds"


def write_atomic(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temp_path = Path(stream.name)
        stream.write(data)
    temp_path.replace(path)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
table_bytes = TABLE.read_bytes()
if hashlib.sha256(table_bytes).hexdigest() != EXPECTED_TABLE_SHA256:
    raise SystemExit("statement table changed since the failed audit; refusing repair")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if EXPECTED_QUOTE not in source_lines[308]:
    raise SystemExit("expected quote is absent from source L309")
rows = [json.loads(line) for line in table_bytes.decode("utf-8-sig").splitlines() if line.strip()]
row = next((item for item in rows if item.get("statement_id") == STATEMENT_ID), None)
if not row or row.get("original_quote") != EXPECTED_QUOTE:
    raise SystemExit("statement or quote changed; refusing repair")
q = row.get("qualifiers", {})
if (q.get("source_line_start"), q.get("source_line_end")) != (304, 304):
    raise SystemExit("unexpected source range; refusing repair")
q["source_line_start"] = 309
q["source_line_end"] = 309

preview = {"mode": "dry-run", "statement_id": STATEMENT_ID, "source_lines": [309, 309]}
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
if BACKUP.exists():
    raise SystemExit(f"backup already exists: {BACKUP}")
shutil.copy2(TABLE, BACKUP)
new_bytes = ("\n".join(json.dumps(item, ensure_ascii=False) for item in rows) + "\n").encode("utf-8")
write_atomic(TABLE, new_bytes)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
