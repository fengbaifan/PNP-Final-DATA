from __future__ import annotations

import csv
import hashlib
import shutil
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
EXPECTED_SHA = "9475149939cdf66fa423253ac077485cac9f1a22c2794ae1f16e7815307853c8"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch13-p334-duplicate-mentions-fix-20261014")
REMOVE = {
    "m-s2-ch13-p334-031": ("cand-0025", "Giambattista Albrizzi", "970", "991"),
    "m-s2-ch13-p334-032": ("cand-1844", "Giambattista Pasquali", "993", "1014"),
    "m-s2-ch13-p334-033": ("cand-2865", "Antonio Zatta", "1019", "1032"),
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

if sha(TABLE) != EXPECTED_SHA:
    raise SystemExit("mentions table changed since the p.334 write; no repair made")
if BACKUP.exists():
    raise SystemExit(f"backup exists; refusing overwrite: {BACKUP.name}")
with TABLE.open(encoding="utf-8-sig", newline="") as stream:
    reader = csv.DictReader(stream)
    fields = reader.fieldnames
    rows = list(reader)
if not fields:
    raise SystemExit("mentions table has no header")
by_id = {row["mention_id"]: row for row in rows}
if set(REMOVE) - set(by_id):
    raise SystemExit("one or more duplicate rows are missing")
for mention_id, expected in REMOVE.items():
    row = by_id[mention_id]
    actual = (row["candidate_id"], row["surface_form"], row["start_char"], row["end_char"])
    if actual != expected:
        raise SystemExit(f"duplicate row changed: {mention_id}: {actual}")
remaining = [row for row in rows if row["mention_id"] not in REMOVE]
buffer = StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
writer.writeheader()
writer.writerows(remaining)
output = buffer.getvalue().encode("utf-8")
shutil.copy2(TABLE, BACKUP)
TABLE.write_bytes(output)
print("removed", len(REMOVE), "duplicate p.334 name mentions; original exact rows retained")
print("backup:", BACKUP.name)
print("written sha256:", sha(TABLE))
