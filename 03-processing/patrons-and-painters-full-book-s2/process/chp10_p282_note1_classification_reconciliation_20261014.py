"""Classify p.282 note 1 against the printed footnote on physical page 11."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PDF = ROOT / "02-sources/01-book/CHP-10.pdf"
TABLES = ROOT / "04-knowledge/tables"
SEGMENT = "chp-10:10_CHP-10_intro:l491-634"
TARGET = "st-chp10-notes-p282n1-portrait-patronage-account"
SUFFIX = ".bak-s2-chp10-p282-note1-classification-20261014"
EXPECTED = {
    PDF: "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb",
    TABLES / "book-statements.jsonl": "c8ef2ca67b4222ccde3000e54ee2606028d24755c0da7256d00ea6ec5dd5c68e",
    TABLES / "s2-coverage.csv": "0c62665ac3580a48fb5b1ec95fed0d2f29b1b46a9e0ca15acde0392b10c6c022",
}

def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)

def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)

for path, expected in EXPECTED.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"input changed: {path.relative_to(ROOT)} sha256={actual}")

statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
with coverage_path.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    coverage_fields, coverage = list(reader.fieldnames), list(reader)
row_by_id = {r["statement_id"]: r for r in statements}
cov_by_id = {r["segment_id"]: r for r in coverage}
row = row_by_id.get(TARGET)
if not row or row.get("segment_id") != SEGMENT or row.get("qualifiers", {}).get("relation_candidate") is not None:
    raise SystemExit("p.282 note 1 target changed or is already classified")
q = row["qualifiers"]
q["claim"] = "Haskell says the Rapparini eulogy gives a fairly full account of Johann Wilhelm's patronage, but because it was written in 1709 it naturally contains no references to Pellegrini."
q["qualification"] = "This is Haskell's description of the eulogy's scope, not an independent assessment of the source. The scan reads 'full' where the OCR has 'hill'; the eulogy itself was not independently consulted."
row["original_quote"] = "Le Portrait du Vrai Mérité dans la personne serenissime de Monseigneur l’Electeur Palatin gives a fairly full account of Johann Wilhelm’s patronage"
q["relation_candidate"] = False
cov = cov_by_id.get(SEGMENT)
if not cov or (cov["disposition"], cov["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("consolidated note coverage state changed")
cov["note"] += " 2026-10-14 reviewed p.282 note 1 against CHP-10.pdf physical p.11; classified its Rapparini eulogy description as a source-scope locator rather than a formal relation candidate, and retained Haskell's 1709 cutoff and no-Pellegrini limitation. Corrected the quoted OCR 'hill' to printed 'full'."

print(json.dumps({"source": "p.282 note 1, CHP-10.pdf physical page 11", "classification": False, "statement": TARGET, "quote_correction": "hill -> full"}, ensure_ascii=False, indent=2))
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
if args.apply:
    paths = [statement_path, coverage_path]
    backups = [p.with_name(p.name + SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("recovery backup already exists; inspect before retrying")
    for p, b in zip(paths, backups):
        shutil.copy2(p, b)
    try:
        write_jsonl(statement_path, statements)
        write_csv(coverage_path, coverage_fields, coverage)
    except Exception:
        for p, b in zip(paths, backups):
            shutil.copy2(b, p)
        raise
    print("APPLIED; backups=" + ", ".join(str(p.relative_to(ROOT)) for p in backups))
