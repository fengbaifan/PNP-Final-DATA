"""Link p.285 note 1 to the French programme quotation split across the page segment."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
LINE_SHA = "68ba07cca0a62d47cc95c9a567affebe5670d2708b6fd19073d1d976a489dac5"
BACKUP_SUFFIX = ".bak-s2-chp10-p285-note1-link-fix-20261002"
P284_TARGET = "st-chp10-p284-mississippi-programme-open"
P285_TARGET = "st-chp10-p285-french-gallery-inscription"


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line = source_lines[178]
if hashlib.sha256(line.encode("utf-8")).hexdigest() != LINE_SHA:
    raise SystemExit("p.285 continuation line changed")
if "eighteenth century.1 He was to express" not in line:
    raise SystemExit("printed footnote marker position changed")

rows = [json.loads(item) for item in TABLE.read_text(encoding="utf-8-sig").splitlines() if item.strip()]
by_id = {row["statement_id"]: row for row in rows}
p284 = by_id.get(P284_TARGET)
p285 = by_id.get(P285_TARGET)
if not p284 or not p285:
    raise SystemExit("one or more cross-page statement rows are missing")
q284 = p284.get("qualifiers", {})
q285 = p285.get("qualifiers", {})
if q284.get("footnote_source_line") != 528 or q284.get("footnote_text_pending"):
    raise SystemExit("p.284 continuation note link is not in the expected state")
if q285.get("footnote_marker") != 1 or not q285.get("footnote_text_pending"):
    raise SystemExit("p.285 French quotation marker state changed")
if q285.get("source_line_start") != 179 or q285.get("source_line_end") != 179:
    raise SystemExit("p.285 French quotation source anchor changed")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated link correction")
args = parser.parse_args()
print("confirmed one printed p.285 marker 1 spans the cross-page programme statement and its French quotation")
print("only the p.285 quotation's existing pending note link will be closed; no claim text or counts change")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"backup already exists: {backup}")
shutil.copy2(TABLE, backup)
q285["footnote_text_pending"] = False
q285["footnote_link_status"] = "resolved_source_migration"
q285["footnote_segment"] = "chp-10:10_CHP-10_intro:l491-634"
q285["footnote_source_line"] = 528
q285["footnote_note_statement_ids"] = []
q285["qualification"] = (q285.get("qualification", "") +
    " The p.285 footnote marker appears after the cross-page programme sentence and its source document is also linked here to the immediately following French programme wording. Both rows represent the same single printed note 1; cited material remains unverified.").strip()

with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as stream:
    for row in rows:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(TABLE)
print(f"applied; recovery copy: {backup.name}")
