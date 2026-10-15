#!/usr/bin/env python3
"""Repair p.340 candidate source references to exact source-line anchors."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
PRE_HASH = "b92c75208937f350ee6349bdc47717dd3a8d71d219aefb8a6071584840d6eb46"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch13-p340-source-ref-repair-20261014")
SEGMENT = "chp-13:13_CHP-13_intro:l79-88"
LINE_BY_ID = {
    "cand-12162": 82,
    "cand-12163": 82,
    "cand-12164": 86,
    "cand-12165": 86,
    "cand-12166": 86,
    "cand-12167": 84,
    "cand-12168": 85,
    "cand-12169": 85,
    "cand-12170": 80,
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    if digest(raw) != PRE_HASH:
        raise SystemExit(f"preflight failed: candidate table hash changed: {digest(raw)}")
    with TABLE.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    found = {row["candidate_id"]: row for row in rows if row["candidate_id"] in LINE_BY_ID}
    if set(found) != set(LINE_BY_ID):
        raise SystemExit("preflight failed: expected p.340 candidates are missing")
    for candidate_id, line in LINE_BY_ID.items():
        row = found[candidate_id]
        if row["candidate_source_ref"] != SEGMENT + "#L80-L86":
            raise SystemExit(f"preflight failed: unexpected source ref for {candidate_id}: {row['candidate_source_ref']}")
        row["candidate_source_ref"] = SEGMENT + f"#L{line}"
    with tempfile.SpooledTemporaryFile(mode="w+", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        stream.seek(0)
        updated = stream.read().encode("utf-8-sig")
    print(f"candidates repaired={len(LINE_BY_ID)}; before={digest(raw)}; after={digest(updated)}")
    if not args.apply:
        print("DRY RUN only; no files written. Pass --apply to write.")
        return
    if BACKUP.exists():
        raise SystemExit(f"refusing to overwrite existing backup: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    fd, temporary = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, TABLE)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"APPLIED; backup={BACKUP.name}; after={digest(TABLE.read_bytes())}")


if __name__ == "__main__":
    main()
