"""Repair verified postscript body-to-footnote anchors; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP_SUFFIX = ".bak-s2-chp20-footnote-link-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply verified footnote-link repairs")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical postscript Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered postscript PDF changed")

statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
statements = read_jsonl(statement_path)
_, coverage_rows = read_csv(coverage_path)
statement_by_id = {row["statement_id"]: row for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

if len(statements) != 11096:
    raise SystemExit(f"unexpected statement count: {len(statements)}")
if NOTES not in coverage or (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("postscript notes segment is not still queued/pending")

# Printed pages 396-397: refs read from the scanned footers and their body markers.
new_refs = {
    "st-chp20-p396-fagiolo-carandini-study": (1, 212),
    "st-chp20-p396-lavin-barberini-inventory-publication": (2, 212),
    "st-chp20-p396-donofrio-documents-on-maffeo": (3, 213),
    "st-chp20-p396-bellori-mancini-caravaggio-portrait-claim": (4, 213),
    "st-chp20-p396-longhi-alternative-portrait": (5, 214),
    "st-chp20-p396-hibbard-maderno-monograph": (6, 214),
    "st-chp20-p397-lavin-quote-closure": (1, 215),
    "st-chp20-p397-hibbard-qualifies-baldacchino-attribution": (2, 215),
    "st-chp20-p397-french-tapestries-dubon": (3, 216),
    "st-chp20-p397-urban-viii-tapestries-don-urbano": (4, 216),
    "st-chp20-p397-harris-sacchi-palazzo-ceiling": (5, 217),
    "st-chp20-p397-classical-baroque-debate-poirier": (6, 217),
    "st-chp20-p397-ludovisi-garas-inventory": (7, 218),
    "st-chp20-p397-heikamp-del-monte-tuscan-court": (8, 218),
    "st-chp20-p397-frommel-del-monte-inventories": (9, 219),
    "st-chp20-p397-kirwin-del-monte-inventories": (10, 219),
    "st-chp20-p397-spezzaferro-del-monte-caravaggio": (11, 220),
    "st-chp20-p397-posner-caravaggio-early-works": (12, 220),
}

for statement_id, (marker, source_line) in new_refs.items():
    if statement_id not in statement_by_id:
        raise SystemExit(f"required statement missing: {statement_id}")
    qualifiers = statement_by_id[statement_id].setdefault("qualifiers", {})
    if qualifiers.get("footnote_refs") or qualifiers.get("footnote_marker") is not None:
        raise SystemExit(f"unexpected pre-existing footnote link: {statement_id}")
    qualifiers.update({
        "footnote_marker": marker,
        "footnote_text_pending": True,
        "footnote_segment": NOTES,
        "footnote_refs": [{"marker": marker, "segment_id": NOTES, "source_line": source_line}],
        "footnote_statement_ids": [],
        "footnote_body_link_status": "pending",
    })

# On printed p.409, note 3 (Da Pozzo) begins on L272; OCR merged it into L271.
corrected_refs = {
    "st-chp20-p409-da-pozzo-edition-and-will-publication": {2: 271, 3: 272},
    "st-chp20-p409-tesi-painted-pitt-bequests": {3: 272},
    "st-chp20-p409-tiepolo-pictures-bequeathed-to-cosimo-mari": {3: 272},
}
for statement_id, expected in corrected_refs.items():
    if statement_id not in statement_by_id:
        raise SystemExit(f"required statement missing: {statement_id}")
    qualifiers = statement_by_id[statement_id]["qualifiers"]
    refs = qualifiers.get("footnote_refs", [])
    actual = {ref.get("marker"): ref.get("source_line") for ref in refs}
    if actual != {marker: 271 for marker in expected}:
        raise SystemExit(f"unexpected p.409 footnote refs for {statement_id}: {actual}")
    for ref in refs:
        if ref.get("marker") in expected:
            ref["source_line"] = expected[ref["marker"]]

print(f"verified repair: add {len(new_refs)} p.396-397 links; correct {len(corrected_refs)} p.409 statement mappings")
print("postscript notes coverage remains queued/pending until semantic migration is complete")
if not args.apply:
    print("dry-run only; pass --apply to write")
else:
    backup = statement_path.with_name(statement_path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(statement_path, backup)
    write_jsonl(statement_path, statements)
    reread = read_jsonl(statement_path)
    if len(reread) != len(statements):
        raise SystemExit("statement count changed after write")
    print(f"applied; backup={backup.name}")
