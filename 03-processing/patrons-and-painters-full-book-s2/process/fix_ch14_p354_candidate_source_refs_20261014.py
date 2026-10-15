"""Normalize the three p.354 candidate locators to audit-supported single lines."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
EXPECTED = "ae4b04794840e521a75c8286688faf53367b5a90db7110d2c5d128a01a2bcbc5"
BACKUP = PATH.with_name(PATH.name + ".bak-s2-ch14-p354-source-ref-format-20261014")
UPDATES = {
    "cand-12195": ("chp-14:14_CHP-14_intro:l73-83#L75-76", "chp-14:14_CHP-14_intro:l73-83#L75"),
    "cand-12196": ("chp-14:14_CHP-14_intro:l73-83#L79-80", "chp-14:14_CHP-14_intro:l73-83#L79"),
    "cand-12197": ("chp-14:14_CHP-14_intro:l73-83#L79-80", "chp-14:14_CHP-14_intro:l73-83#L79"),
}
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

before = PATH.read_bytes()
digest = lambda b: hashlib.sha256(b).hexdigest()
if digest(before) != EXPECTED:
    raise SystemExit("entity-candidates.csv changed since the locator repair was prepared")
with PATH.open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    fields, rows = reader.fieldnames, list(reader)
found = {row["candidate_id"]: row for row in rows}
for candidate_id, (old, new) in UPDATES.items():
    row = found.get(candidate_id)
    if row is None or row["candidate_source_ref"] != old:
        raise SystemExit(f"unexpected source ref for {candidate_id}")
    row["candidate_source_ref"] = new
from io import StringIO
buffer = StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
writer.writeheader()
writer.writerows(rows)
after = buffer.getvalue().encode("utf-8")
print(json.dumps({"mode": "apply" if args.apply else "dry-run", "updated": UPDATES, "before_sha256": digest(before), "after_sha256": digest(after)}, ensure_ascii=False, indent=2))
if args.apply:
    if BACKUP.exists():
        if digest(BACKUP.read_bytes()) != EXPECTED:
            raise SystemExit("existing backup does not match pre-write file")
    else:
        shutil.copy2(PATH, BACKUP)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=PATH.parent) as handle:
        handle.write(after)
        temp = Path(handle.name)
    temp.replace(PATH)
    print(json.dumps({"written_sha256": digest(PATH.read_bytes()), "backup": BACKUP.name}))
