"""Remove three duplicate p.352 surface spans created by overlapping index candidates."""
import csv
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "04-knowledge" / "tables" / "mentions.csv"
BACKUP = PATH.with_name(PATH.name + ".bak-s2-chp14-p352-overlap-repair-20261003")
REMOVE = {
    "m-chp14-p352-0013": ("cand-0052", "Algarotti", "1502", "1511"),
    "m-chp14-p352-0014": ("cand-0045", "Algarotti", "877", "886"),
    "m-chp14-p352-0015": ("cand-0045", "Algarotti", "1273", "1282"),
}

with PATH.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)

by_id = {row["mention_id"]: row for row in rows}
for mention_id, expected in REMOVE.items():
    row = by_id.get(mention_id)
    if row is None or (row["candidate_id"], row["surface_form"], row["start_char"], row["end_char"]) != expected:
        raise SystemExit(f"unexpected overlap repair precondition: {mention_id}")
if not BACKUP.exists():
    shutil.copy2(PATH, BACKUP)

remaining = [row for row in rows if row["mention_id"] not in REMOVE]
with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", dir=PATH.parent, delete=False) as f:
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(remaining)
    tmp = Path(f.name)
tmp.replace(PATH)

print(json.dumps({"removed_duplicate_mentions": sorted(REMOVE), "mentions_before": len(rows),
                  "mentions_after": len(remaining), "backup": BACKUP.name}, ensure_ascii=False))
