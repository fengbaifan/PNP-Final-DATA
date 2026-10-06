"""Remove a repeated candidate ID from one p.312 statement list; dry-run by default."""
import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
STATEMENT_ID = "st-chp10-p312-works-from-gonzaga-gallery"
EXPECTED = ["cand-2401", "cand-2411", "cand-1524", "cand-1524"]
BACKUP_SUFFIX = ".bak-s2-chp10-p312-statement-dedupe-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
rows = [json.loads(line) for line in PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
matches = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
if len(matches) != 1 or matches[0].get("qualifiers", {}).get("mentioned_candidate_ids") != EXPECTED:
    raise SystemExit("statement changed; review current row before repair")
matches[0]["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(EXPECTED))
print("p.312 statement repair preview: duplicate Ferdinando Carlo Gonzaga candidate reference removed")
if not args.apply:
    raise SystemExit(0)
backup = PATH.with_name(PATH.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"backup already exists: {backup.name}")
shutil.copy2(PATH, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=PATH.parent, delete=False) as stream:
    for row in rows:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(PATH)
print(f"applied; recovery copy created as {backup.name}")
