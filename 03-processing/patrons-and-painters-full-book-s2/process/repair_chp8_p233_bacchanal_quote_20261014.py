"""Guarded repair for the p.233 Bacchanal statement quote span."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
SEGMENT = "chp-8:08_CHP-8_sec_ii:l271-279"
STATEMENT_ID = "st-chp8-p233-sacconi-bacchanal-order"
EXPECTED_SHA256 = "e3d32e7cb2c1665aa727e1060b0e4a6a5dd25bd2955867285bb224a0259ca83d"
OLD_QUOTE = "a Bacchanal. Ferdinand notes that his colour is improving under"
NEW_QUOTE = "a Bacchanal."
BACKUP_SUFFIX = ".bak-s2-chp8-p233-bacchanal-quote-repair-20261014"


def plan():
    if hashlib.sha256(STATEMENTS.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise SystemExit("book-statements.jsonl changed since the quote repair was prepared")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if "a Bacchanal." not in lines[275]:
        raise SystemExit("source does not contain the expected Bacchanal phrase")
    rows = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    matches = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"expected one {STATEMENT_ID}, found {len(matches)}")
    row = matches[0]
    if row.get("segment_id") != SEGMENT or row.get("original_quote") != OLD_QUOTE:
        raise SystemExit("target statement is not in the expected pre-repair state")
    row["original_quote"] = NEW_QUOTE
    data = ("\n".join(json.dumps(item, ensure_ascii=False) for item in rows) + "\n").encode("utf-8")
    return {"mode": "dry-run", "statement_id": STATEMENT_ID, "old_quote": OLD_QUOTE,
            "new_quote": NEW_QUOTE, "source_line": 276}, data


def atomic_write(data: bytes):
    with tempfile.NamedTemporaryFile(dir=STATEMENTS.parent, delete=False) as stream:
        temp = Path(stream.name)
        stream.write(data)
    temp.replace(STATEMENTS)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
preview, payload = plan()
if args.apply:
    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(STATEMENTS, backup)
    atomic_write(payload)
    preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
