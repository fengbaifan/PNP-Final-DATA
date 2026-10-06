"""Restore the p.342 source-local quote after closing its p.343 continuation."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
STATEMENT_ID = "st-chp13-p342-zanetti_1752_rare_print_exception_fragment"
PREVIOUS_SEGMENT = "chp-13:13_CHP-13_intro:l98-105"
NEXT_SEGMENT = "chp-13:13_CHP-13_intro:l107-114"
BACKUP_SUFFIX = ".bak-s2-chp13-p343-quote-repair-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the source-local quote repair")
args = parser.parse_args()

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line = source_lines[104]
start = line.find("Indeed I can hope")
end_marker = "Annibale"
end = line.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit("expected p.342 quotation fragment was not found in source")
expected_quote = line[start:end + len(end_marker)]

rows = [json.loads(value) for value in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if value.strip()]
matches = [row for row in rows if row["statement_id"] == STATEMENT_ID]
if len(matches) != 1:
    raise SystemExit("expected exactly one p.342 quotation statement")
statement = matches[0]
if statement["segment_id"] != PREVIOUS_SEGMENT:
    raise SystemExit("statement segment changed; refusing to edit the quote")
if statement["qualifiers"].get("source_line_start") != 105 or statement["qualifiers"].get("source_line_end") != 105:
    raise SystemExit("statement source line range is not local to p.342")
if NEXT_SEGMENT not in statement["qualifiers"].get("cross_reference_segments", []):
    raise SystemExit("p.343 continuation link is missing")
if not statement["original_quote"].startswith(expected_quote):
    raise SystemExit("the current quote does not begin with the exact p.342 source fragment")
suffix = statement["original_quote"][len(expected_quote):]
if not suffix.startswith(" and the lascivious\nprints of Giulio Romano"):
    raise SystemExit("unexpected cross-page quote suffix")
statement["original_quote"] = expected_quote
print("quote repair dry-run: keep original_quote within the cited p.342 source segment")
print(f"  statement: {STATEMENT_ID}")
print(f"  p.342 quote: {expected_quote}")
print("  p.343 continuation remains in its own statement and cross-reference")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"recovery copy already exists: {backup.name}")
shutil.copy2(STATEMENTS, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENTS.parent, delete=False) as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp = Path(f.name)
tmp.replace(STATEMENTS)
print(f"applied; recovery copy created as {backup.name}")
