from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch13-p333-source-path-fix-20261014")
EXPECTED_SHA = "92994c1646502707669bf0fe5ae7206b84d710c875101cf8d01bcf8b45612d51"
IDS = {
    "st-chp13-p333-publishers-employed-printmakers",
    "st-chp13-p333-publishers-commissioned-suitable-artists",
    "st-chp13-p333-publishers-patronized-printmakers",
    "st-chp13-p333-poem-collections-required-contributions-from-venetian-poets",
    "st-chp13-p333-poem-collections-supported-fine-artists",
    "st-chp13-p333-publishers-depended-on-patronage-for-expensive-ventures",
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

if sha(TABLE) != EXPECTED_SHA:
    raise SystemExit("statement table changed since the p.333 apply; no write made")
if BACKUP.exists():
    raise SystemExit(f"backup exists; refusing overwrite: {BACKUP.name}")
rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
if not IDS <= set(by_id):
    raise SystemExit("one or more p.333 statement rows are missing")
if any(by_id[sid].get("source_file") != "13_CHP-13_intro.md" for sid in IDS):
    raise SystemExit("new-row source_file values differ from expected repair baseline")
for sid in IDS:
    by_id[sid]["source_file"] = "02-sources/02-Markdown/13_CHP-13_intro.md"
output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
shutil.copy2(TABLE, BACKUP)
TABLE.write_bytes(output)
print("repaired", len(IDS), "source_file paths; backup:", BACKUP.name)
print("written sha256:", sha(TABLE))
