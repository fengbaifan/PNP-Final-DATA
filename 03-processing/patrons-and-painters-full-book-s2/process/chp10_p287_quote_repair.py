"""Correct the p.287 McSwiny quotation's source-line end after audit detection."""
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
path = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
backup = Path(str(path) + ".bak-s2-chp10-p287-quote-fix-20261002")
rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
matches = [row for row in rows if row["statement_id"] == "st-chp10-p287-mcswiny-stage-career"]
if len(matches) != 1:
    raise SystemExit(f"expected one McSwiny statement, found {len(matches)}")
statement = matches[0]
if statement["qualifiers"]["source_line_start"] != 211 or statement["qualifiers"]["source_line_end"] != 211:
    raise SystemExit(f"unexpected line span: {statement['qualifiers']}")
if backup.exists():
    raise SystemExit(f"backup already exists: {backup}")
shutil.copy2(path, backup)
statement["qualifiers"]["source_line_end"] = 212
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
    for row in rows:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(path)
print(json.dumps({"statement_id": statement["statement_id"], "source_line_start": 211,
                  "source_line_end": 212, "backup": str(backup)}, ensure_ascii=False, indent=2))
