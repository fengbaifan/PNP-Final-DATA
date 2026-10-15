"""Correct two p.235 statement ranges whose exact quotes cross a printed-text line."""
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
EXPECTED_TABLE_SHA256 = "9552aee b27a99b0ac47f5e685f088b4c5c171859549c706a12dc242fe71adbf9".replace(" ", "")
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp8-p235-quote-range-repair-20261014")
TARGETS = {
    "st-chp8-p235-allegory-destroyed": "This work has unfortunately been destroyed,",
    "st-chp8-p235-allegory-arrival": "However, shortly afterwards the situation improved and Ricci arrived to paint an\nAllegory of the Arts in Ferdinand’s favourite gallery in his favourite villa.",
}


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
source_text = "\n".join(source_lines[298:300])
rows = [json.loads(line) for line in table_bytes.decode("utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
for statement_id, quote in TARGETS.items():
    row = by_id.get(statement_id)
    if row is None or row.get("original_quote") != quote or quote not in source_text:
        raise SystemExit(f"unexpected quote or missing row: {statement_id}")
    q = row.get("qualifiers", {})
    if (q.get("source_line_start"), q.get("source_line_end")) != (299, 299):
        raise SystemExit(f"unexpected source line range: {statement_id}")
    q["source_line_end"] = 300

preview = {"mode": "dry-run", "updated_statement_ids": sorted(TARGETS), "line_range": [299, 300]}
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)
if BACKUP.exists():
    raise SystemExit(f"backup already exists: {BACKUP}")
shutil.copy2(TABLE, BACKUP)
new_bytes = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
write_atomic(TABLE, new_bytes)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
