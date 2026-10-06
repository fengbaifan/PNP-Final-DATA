"""Repair p.369 S2 candidate_origin values to the repository's accepted enum."""
import csv
import hashlib
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
EXPECTED_SHA = "cbbeaa1603201a9d1e6c758b889ebb7dd7a2aeaca4015366e87ab16b363dbb23"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp15-p369-origin-repair-20261004")
IDS = {f"cand-{number}" for number in range(10527, 10545)}

if hashlib.sha256(TABLE.read_bytes()).hexdigest() != EXPECTED_SHA:
    raise SystemExit("candidate table changed since the p.369 audit; inspect before repairing")
if BACKUP.exists():
    raise SystemExit(f"repair backup already exists: {BACKUP.name}")

with TABLE.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, rows = reader.fieldnames, list(reader)
selected = [row for row in rows if row["candidate_id"] in IDS]
if {row["candidate_id"] for row in selected} != IDS:
    raise SystemExit("p.369 candidate set is incomplete")
invalid = [row["candidate_id"] for row in selected if row["candidate_origin"] not in {"body-mention", "footnote-mention"}]
if invalid or any(not re.search(r"#L(?:51|52|57|59|105|107|108)$", row["candidate_source_ref"]) for row in selected):
    raise SystemExit("p.369 candidate preconditions changed")

shutil.copy2(TABLE, BACKUP)
for row in selected:
    row["candidate_origin"] = "body-mention"
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=TABLE.parent, delete=False) as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    temp = Path(handle.name)
temp.replace(TABLE)
print(f"repaired {len(selected)} p.369 candidates; backup={BACKUP.name}")
