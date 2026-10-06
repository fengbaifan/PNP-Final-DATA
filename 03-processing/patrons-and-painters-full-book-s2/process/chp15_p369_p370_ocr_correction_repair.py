"""Place p.369-p.370 print corrections on only the statements they affect."""
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
EXPECTED_SHA = "e46c45bc25314c65321308aedead66747ee875d68343a6ba698ee17090e1bc8f"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp15-p369-p370-ocr-repair-20261004")
SOURCE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"

if hashlib.sha256(TABLE.read_bytes()).hexdigest() != EXPECTED_SHA:
    raise SystemExit("book-statements table changed since the p.370 audit; inspect before repairing")
if BACKUP.exists():
    raise SystemExit(f"repair backup already exists: {BACKUP.name}")

rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
p369_id = "st-chp15-p369-querini-beccaria-authorship-rumour"
targets = {
    "st-chp15-p370-querini-study-daphnis-chloe-print-series": [
        {"source_file": SOURCE, "source_line": 62, "ocr": "R��gent Philippe d��Orl��ans", "print": "Régent Philippe d’Orléans", "basis": "CHP-15.pdf physical page 10."}],
    "st-chp15-p370-youngs-wood-landscape-arrangement": [
        {"source_file": SOURCE, "source_line": 63, "ocr": "wildarea", "print": "wild area", "basis": "CHP-15.pdf physical page 10."}],
    "st-chp15-p370-phocion-described-as-querini-hero": [
        {"source_file": SOURCE, "source_line": 65, "ocr": 'who "was Querini', "print": "who was Querini", "basis": "CHP-15.pdf physical page 10."}],
    "st-chp15-p370-querini-aristocratic-cast-and-1761-downfall": [
        {"source_file": SOURCE, "source_line": 65, "ocr": 'who "was Querini', "print": "who was Querini", "basis": "CHP-15.pdf physical page 10."}],
    "st-chp15-p370-cabane-de-la-folie-and-montaigne-inscription": [
        {"source_file": SOURCE, "source_line": 67, "ocr": "Montaigne's", "print": "Montaigne’s", "basis": "CHP-15.pdf physical page 10."}],
    "st-chp15-p370-note2-moschini-citation": [
        {"source_file": SOURCE, "source_line": 110, "ocr": "1806, H, p. 116", "print": "1806, II, p. 116", "basis": "CHP-15.pdf physical page 10."}],
}
if p369_id not in by_id or any(statement_id not in by_id for statement_id in targets):
    raise SystemExit("expected p.369-p.370 statement is missing")
if len([row for row in rows if row["statement_id"].startswith("st-chp15-p370-")]) != 24:
    raise SystemExit("p.370 statement count changed")

for correction in by_id[p369_id]["qualifiers"].get("ocr_corrections", []):
    if correction.get("source_line") == 50:
        by_id[p369_id]["qualifiers"]["ocr_corrections"].remove(correction)
        break
for row in rows:
    if row["statement_id"].startswith("st-chp15-p370-"):
        row["qualifiers"].pop("ocr_corrections", None)
for statement_id, corrections in targets.items():
    by_id[statement_id]["qualifiers"]["ocr_corrections"] = corrections

shutil.copy2(TABLE, BACKUP)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
    for row in rows:
        handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temp = Path(handle.name)
temp.replace(TABLE)
print(f"repaired p.369/p.370 OCR correction placement; backup={BACKUP.name}")
