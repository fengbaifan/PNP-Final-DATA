from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
EXPECTED_SHA256 = "90a661b96e9f7a3c974dcfd138f1eb761217e10702cf0a7841f76af27270efc5"
BAD_REF = b"chp-2:02_CHP-2_sec_i:l82-93#L86-L87"
GOOD_REF = b"chp-2:02_CHP-2_sec_i:l82-93#L86"
BACKUP = TABLE.with_name("entity-candidates.csv.bak-s2-chp2-sec-i-l82-93-source-ref-fix-20261010")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def atomic_write(path: Path, payload: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Correct the candidate source locator to the audit contract.")
    parser.add_argument("--apply", action="store_true", help="apply the preflighted locator correction")
    args = parser.parse_args()
    current = TABLE.read_bytes()
    if sha256(current) != EXPECTED_SHA256:
        raise SystemExit("PRECONDITION FAILED: candidate table hash changed")
    if BAD_REF not in current or current.count(BAD_REF) != 1:
        raise SystemExit("PRECONDITION FAILED: expected single cross-line locator not found")
    if b"cand-11578" not in current:
        raise SystemExit("PRECONDITION FAILED: candidate cand-11578 is missing")
    if BACKUP.exists():
        raise SystemExit(f"PRECONDITION FAILED: backup already exists: {BACKUP.name}")

    updated = current.replace(BAD_REF, GOOD_REF, 1)
    print("PREVIEW: cand-11578 candidate_source_ref")
    print("  before:", BAD_REF.decode())
    print("  after: ", GOOD_REF.decode())
    print("  line 86 is within the reviewed source segment; mention span remains exact across lines 86–87")
    print("  before sha256:", sha256(current))
    print("  after sha256: ", sha256(updated))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to apply the correction.")
        return

    shutil.copy2(TABLE, BACKUP)
    atomic_write(TABLE, updated)
    print("APPLIED")
    print("table sha256:", sha256(TABLE.read_bytes()))
    print("backup:", BACKUP.relative_to(ROOT))


if __name__ == "__main__":
    main()
