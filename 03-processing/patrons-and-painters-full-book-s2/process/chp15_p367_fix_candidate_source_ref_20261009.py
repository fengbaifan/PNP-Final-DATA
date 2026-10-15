from __future__ import annotations

import argparse
import hashlib
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "04-knowledge/tables/entity-candidates.csv"
CANDIDATE_ID = "cand-11561"
OLD_REF = b"chp-15:15_CHP-15_sec_ii:l30-36#L33-L35"
NEW_REF = b"chp-15:15_CHP-15_sec_ii:l30-36#L34"
BACKUP_NAME = "entity-candidates.csv.bak-s2-handoff-chp15-p367-source-ref-fix-20261009"
TEMP_NAME = "entity-candidates.csv.tmp-s2-handoff-chp15-p367-source-ref-fix"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Correct the p.367 candidate source locator to its exact source line.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()

    raw = TARGET.read_bytes()
    text = raw.decode("utf-8-sig")
    rows = text.splitlines()
    matches = [line for line in rows if line.startswith(CANDIDATE_ID + ",")]
    if len(matches) != 1 or OLD_REF.decode() not in matches[0]:
        raise SystemExit(f"Expected one {CANDIDATE_ID} row with the reviewed old locator.")
    if raw.count(OLD_REF) != 1:
        raise SystemExit("Expected the old locator exactly once in the candidate table.")
    updated = raw.replace(OLD_REF, NEW_REF, 1)
    print(f"candidate={CANDIDATE_ID}")
    print(f"candidate_source_ref={OLD_REF.decode()} -> {NEW_REF.decode()}")
    print(f"old_sha256={sha256(raw)}")
    print(f"new_sha256={sha256(updated)}")
    if not args.apply:
        print("DRY-RUN: no files changed.")
        return

    if args.expected_sha256 != sha256(raw):
        raise SystemExit("--apply requires the exact SHA-256 printed by this dry run.")
    backup = TARGET.with_name(BACKUP_NAME)
    temp = TARGET.with_name(TEMP_NAME)
    if backup.exists() or temp.exists():
        raise SystemExit(f"Refusing to overwrite recovery or temp file: {backup if backup.exists() else temp}")
    shutil.copy2(TARGET, backup)
    try:
        temp.write_bytes(updated)
        os.replace(temp, TARGET)
    except Exception:
        if temp.exists():
            temp.unlink()
        if TARGET.exists() and TARGET.read_bytes() != raw:
            TARGET.write_bytes(raw)
        raise
    print(f"APPLIED: recovery_copy={backup} sha256={sha256(backup.read_bytes())}")
    print(f"new_file={TARGET} sha256={sha256(TARGET.read_bytes())}")


if __name__ == "__main__":
    main()
