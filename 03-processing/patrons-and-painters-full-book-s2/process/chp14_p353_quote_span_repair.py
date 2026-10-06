"""Correct the two-line source locator for the p.353 Maecenas commission statement."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
STATEMENT_ID = "st-chp14-p353-commissioned-maecenas-picture-for-bruhl"
EXPECTED_QUOTE = (
    "‘les Beaux Arts amenez par Mecène au Trône d’Auguste ... et l’empire de\n"
    "Flore qui change en endroits délicieux les lieux les plus sauvages’"
)
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp14-p353-quote-repair-20261003")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
matches = [row for row in rows if row["statement_id"] == STATEMENT_ID]
if len(matches) != 1:
    raise SystemExit(f"expected one statement, found {len(matches)}")
row = matches[0]
if row["original_quote"] != EXPECTED_QUOTE:
    raise SystemExit("statement quote differs from the reviewed source phrase")
start = row["qualifiers"]["source_line_start"]
end = row["qualifiers"]["source_line_end"]
if (start, end) not in ((69, 69), (69, 70)):
    raise SystemExit(f"unexpected source line range: {start}-{end}")
if row["segment_id"] != "chp-14:14_CHP-14_intro:l63-71":
    raise SystemExit("statement segment changed")
source = (ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md").read_text(encoding="utf-8-sig").splitlines()
if EXPECTED_QUOTE not in "\n".join(source[68:70]):
    raise SystemExit("reviewed quote is not present in the registered source lines")

row["qualifiers"]["source_line_end"] = 70
print(json.dumps({"mode": "apply" if args.apply else "dry-run", "statement_id": STATEMENT_ID,
                  "source_line_start": 69, "source_line_end": 70}, ensure_ascii=False))

if args.apply:
    if BACKUP.exists():
        if hashlib.sha256(BACKUP.read_bytes()).digest() != hashlib.sha256(TABLE.read_bytes()).digest():
            raise SystemExit(f"existing backup differs from current table: {BACKUP.name}")
    else:
        shutil.copy2(TABLE, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
        for item in rows:
            handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(TABLE)
