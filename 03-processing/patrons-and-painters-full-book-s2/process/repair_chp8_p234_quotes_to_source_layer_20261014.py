"""Restore six p.234 original_quote values to the source transcription layer."""
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
EXPECTED_SHA256 = "6d83e37d066231bcba4625f10684e121dfde3cf87089ef1a74745f75e0531647"
BACKUP_SUFFIX = ".bak-s2-chp8-p234-quote-contract-repair-20261014"


def cut(text: str, start: str, end: str, *, include_end: bool = False) -> str:
    a = text.find(start)
    b = text.find(end, a + len(start))
    if a < 0 or b < 0:
        raise SystemExit(f"source span not found: {start!r} -> {end!r}")
    return text[a:b + len(end) if include_end else b].rstrip()


def plan():
    if hashlib.sha256(STATEMENTS.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise SystemExit("statement table changed since quote repair was prepared")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    raw = {
        "st-chp8-p234-cassana-role": cut(lines[284], "Niccolo Cassana also worked", "adviser.", include_end=True),
        "st-chp8-p234-cook-arrival": cut(lines[285], "In September 1707 his Portrait os a Cook reached Florence", " to the delight"),
        "st-chp8-p234-fumiani-relations": cut(lines[281], "relations between Giannaritonio", "by the artists who worked for him.1", include_end=True),
        "st-chp8-p234-david-attributes": cut(lines[283], "Besides, the composition could be enriched by", "diadem.", include_end=True),
        "st-chp8-p234-langetti-portrait-in-medici-collection": cut(lines[288], "Ratti (Soprani/Ratti, H, 26)", " says that Langetti was actually"),
        "st-chp8-p234-langetti-card-players-in-medici-collection": cut(lines[288], "Ratti (Soprani/Ratti, H, 26)", " says that Langetti was actually"),
    }
    rows = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    expected_print_quotes = {
        "st-chp8-p234-cassana-role": "Niccolò Cassana also worked a good deal for Ferdinand as painter as well as artistic adviser.",
        "st-chp8-p234-cook-arrival": "In September 1707 his Portrait of a Cook reached Florence",
        "st-chp8-p234-fumiani-relations": "relations between Giannantonio Fumiani and the Grand Prince can tell us much about the fantasies which he was so eager to have expressed by the artists who worked for him.1",
        "st-chp8-p234-david-attributes": "Besides, the composition could be enriched by placing at his side his harp, his sceptre and his diadem.",
        "st-chp8-p234-langetti-portrait-in-medici-collection": "Ratti (Soprani/Ratti, II, 26), who reports seeing a portrait and a picture of card players by him in the Medici collection,",
        "st-chp8-p234-langetti-card-players-in-medici-collection": "Ratti (Soprani/Ratti, II, 26), who reports seeing a portrait and a picture of card players by him in the Medici collection,",
    }
    for statement_id, new_quote in raw.items():
        row = by_id.get(statement_id)
        if not row or row.get("original_quote") != expected_print_quotes[statement_id]:
            raise SystemExit(f"unexpected current print-corrected quote: {statement_id}")
        if not new_quote or new_quote not in "\n".join(lines[281:289]):
            raise SystemExit(f"source-layer quote does not match p.234: {statement_id}")
        if not row.get("qualifiers", {}).get("ocr_corrections"):
            raise SystemExit(f"missing OCR correction record: {statement_id}")
        row["original_quote"] = new_quote
    payload = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    return {"mode": "dry-run", "updated_statements": list(raw),
            "reason": "original_quote follows Markdown OCR; print readings remain in ocr_corrections"}, payload


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
