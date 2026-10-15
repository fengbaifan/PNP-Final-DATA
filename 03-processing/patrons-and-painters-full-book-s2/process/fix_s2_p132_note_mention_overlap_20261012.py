from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path.cwd()
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
RESTORE = TABLE.with_name("mentions.csv.bak-s2-chp5-p132-notes-20261012")
CURRENT_SHA = "d4a0a2b98e4237973df879bf601554253e5a9fc2f01457b2020a6773defe2816"
RESTORE_SHA = "665ebc1635b2af8282feba756bffe34d609786bea45c3f2f937f90a3b235681a"
BAD_ID = "m-chp5-note-127-003"
KEEP_ID = "m-chp5-note-127-001"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_rows(data: bytes) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig")
    return list(csv.DictReader(text.splitlines()))


def atomic_write(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove only the overlapping S2-created p.132 note mention.")
    parser.add_argument("--apply", action="store_true", help="restore the exact pre-note mention table")
    args = parser.parse_args()

    current = TABLE.read_bytes()
    restore = RESTORE.read_bytes()
    need(digest(current) == CURRENT_SHA, "mentions table changed after the reviewed overlap finding")
    need(digest(restore) == RESTORE_SHA, "p.132 notes recovery copy does not match expected state")

    current_rows = read_rows(current)
    restore_rows = read_rows(restore)
    current_by_id = {r["mention_id"]: r for r in current_rows}
    restore_by_id = {r["mention_id"]: r for r in restore_rows}
    need(BAD_ID in current_by_id and BAD_ID not in restore_by_id,
         "overlapping mention row is not the expected added record")
    need(current_by_id.get(KEEP_ID, {}).get("candidate_id") == "cand-4376",
         "existing cited-archive mention changed")
    need(current_by_id[BAD_ID].get("candidate_id") == "cand-1856"
         and current_by_id[BAD_ID].get("start_char") == current_by_id[KEEP_ID].get("start_char")
         and current_by_id[BAD_ID].get("end_char") == current_by_id[KEEP_ID].get("end_char"),
         "added row no longer matches the reviewed overlap")
    need(len(current_rows) == len(restore_rows) + 1, "unexpected mention-table difference count")
    need({r["mention_id"] for r in current_rows} - {BAD_ID} == set(restore_by_id),
         "current table contains changes beyond the one overlapping row")

    print("S2 p.132 note mention correction dry-run")
    print(f"current sha256: {digest(current)}")
    print(f"desired sha256: {digest(restore)}; only row removed: {BAD_ID}")
    if not args.apply:
        print("dry-run only; no table written")
        return

    backup = TABLE.with_name("mentions.csv.bak-s2-fix-p132-note-overlap-20261012")
    need(not backup.exists(), f"recovery copy already exists: {backup.name}")
    shutil.copy2(TABLE, backup)
    need(digest(backup.read_bytes()) == CURRENT_SHA, "correction recovery copy hash mismatch")
    atomic_write(TABLE, restore)
    need(digest(TABLE.read_bytes()) == RESTORE_SHA, "corrected table hash mismatch")
    print(f"applied; recovery copy: {backup.name}; final sha256: {digest(TABLE.read_bytes())}")


if __name__ == "__main__":
    main()
