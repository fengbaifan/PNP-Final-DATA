"""Resolve duplicate natural-key claims found by the p.389 S2 audit."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
BACKUP = PATH.with_name(PATH.name + ".bak-s2-chp19-p389-claim-repair-20261004")
TARGETS = {
    "st-chp19-p389-appendix3-conti-franceschini": "The Appendix 3 heading names Marcantonio Franceschini as one of the painters whose commission documents are presented for Stefano Conti at Biblioteca Governativa, Lucca, MS 3299.",
    "st-chp19-p389-appendix3-conti-felice-torelli": "The Appendix 3 heading names Felice Torelli as one of the painters whose commission documents are presented for Stefano Conti at Biblioteca Governativa, Lucca, MS 3299.",
}
EXPECTED_SHARED = "The Appendix 3 heading describes the following documents as relating to Stefano Conti's commissions to Marcantonio Franceschini and Felice Torelli, held at Biblioteca Governativa, Lucca, MS 3299."

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

rows = [json.loads(line) for line in PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
by_id = {row["statement_id"]: row for row in rows}
if len(by_id) != len(rows):
    raise SystemExit("duplicate statement IDs already exist")
for sid in TARGETS:
    row = by_id.get(sid)
    if not row or row.get("qualifiers", {}).get("claim") != EXPECTED_SHARED:
        raise SystemExit(f"repair precondition changed for {sid}")

for sid, claim in TARGETS.items():
    by_id[sid]["qualifiers"]["claim"] = claim

natural_keys = defaultdict(list)
for row in rows:
    claim = row.get("qualifiers", {}).get("claim", "")
    key = (row.get("segment_id"), re.sub(r"\s+", " ", claim).strip().casefold())
    if key[1]:
        natural_keys[key].append(row["statement_id"])
duplicates = {key: ids for key, ids in natural_keys.items() if len(ids) > 1}
if duplicates:
    raise SystemExit(f"duplicate statement natural keys remain: {duplicates}")

if args.apply:
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP.name}")
    shutil.copy2(PATH, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=PATH.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(PATH)
    print(f"applied unique claim repair; backup: {BACKUP.name}")
else:
    print("DRY RUN: no files written")
    for sid, claim in TARGETS.items():
        print(f"{sid}: {claim}")
    print("all statement segment/normalized-claim natural keys are unique after repair")
