"""Close p.374 collection-list pointer against its reviewed p.375 continuation."""
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
table = ROOT / "04-knowledge/tables/book-statements.jsonl"
expected_sha = "3a55117082ea2ce5ac90c6f80205837e1f16945663938df6119f78a01902a2f9"
if hashlib.sha256(table.read_bytes()).hexdigest() != expected_sha:
    raise SystemExit("statement table hash changed")
rows = [json.loads(line) for line in table.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
p374_id = "st-chp16-p374-sasso-posthumous-collection-partial"
p375_id = "st-chp16-p375-sasso-collection-list-completion"
p374, p375 = by_id[p374_id], by_id[p375_id]
if p374["qualifiers"].get("cross_reference_text_pending") is not True:
    raise SystemExit("p.374 pointer is no longer pending")
if (p374_id not in p375["qualifiers"].get("cross_reference_statement_ids", [])
        or p375["qualifiers"].get("cross_reference_text_pending") is not False
        or "and Piazzetta" not in p375["original_quote"]):
    raise SystemExit("reviewed p.375 continuation no longer supports this link")
p374["qualifiers"]["cross_reference_text_pending"] = False
backup = table.with_name(table.name + ".bak-s2-chp16-p374-close-cross-page-20261009")
if backup.exists():
    raise SystemExit(f"backup already exists: {backup.name}")
shutil.copy2(table, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=table.parent, delete=False) as f:
    for row in rows:
        f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temp = Path(f.name)
temp.replace(table)
print(json.dumps({"mode": "applied", "p374_statement": p374_id,
                  "p375_statement": p375_id, "cross_reference_text_pending": False,
                  "backup": backup.name}, ensure_ascii=False))
