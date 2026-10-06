"""Uniquify artist-specific p.314 note claims after the first migration audit."""

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP_SUFFIX = ".bak-s2-chp10-p313-314-unique-count-claims-20261003"
EXPECTED_TOTAL = 9344
CLAIMS = {
    "st-chp10-p314-n04-marieschi-count": "Haskell's p.314 note reports ten pictures by Michele Marieschi in Schulenburg's collection.",
    "st-chp10-p314-n04-carlevarijs-count": "Haskell's p.314 note reports six pictures by Luca Carlevarijs in Schulenburg's collection.",
    "st-chp10-p314-n04-cimaroli-count": "Haskell's p.314 note reports four pictures by Giovan Battista Cimaroli in Schulenburg's collection.",
    "st-chp10-p314-n04-joli-count": "Haskell's p.314 note reports two pictures by Antonio Joli in Schulenburg's collection.",
    "st-chp10-p314-n04-marco-ricci-count": "Haskell's p.314 note reports six pictures by Marco Ricci in Schulenburg's collection.",
    "st-chp10-p314-n04-zuccarelli-count": "Haskell's p.314 note reports nine pictures by Francesco Zuccarelli in Schulenburg's collection.",
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write unique artist names into six count claims")
args = parser.parse_args()
rows = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
if len(rows) != EXPECTED_TOTAL:
    raise SystemExit(f"unexpected statement total: {len(rows)}")
by_id = {row["statement_id"]: row for row in rows}
if len(by_id) != len(rows):
    raise SystemExit("duplicate statement IDs")
for sid, claim in CLAIMS.items():
    row = by_id.get(sid)
    if not row:
        raise SystemExit(f"count statement missing: {sid}")
    if row["segment_id"] != "chp-10:10_CHP-10_sec_ii:l273-349" or row["qualifiers"].get("source_line_start") != 291:
        raise SystemExit(f"unexpected note anchor: {sid}")
    if row["qualifiers"].get("reported_count") is None:
        raise SystemExit(f"reported count missing: {sid}")
    row["qualifiers"]["claim"] = claim

print(f"unique claim preview: {len(CLAIMS)} count statements; statement total {len(rows)}")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)
backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
if backup.exists():
    raise SystemExit(f"recovery copy already exists: {backup.name}")
shutil.copy2(STATEMENTS, backup)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENTS.parent, delete=False) as stream:
    for row in rows:
        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary = Path(stream.name)
temporary.replace(STATEMENTS)
print(f"applied; recovery copy: {backup.name}")
