from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path.cwd()
TABLE = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
EXPECTED = "311cf9ed9935f5c12c6f3b4d1a23571a01ff0d69208af2f488bee39d1c6ee687"
OLD = b"chp-5:05_CHP-5_sec_i:l115-123#L117-118"
NEW = b"chp-5:05_CHP-5_sec_i:l115-123#L117"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
    parser = argparse.ArgumentParser(description="Correct the p.131 candidate source locator; dry-run by default.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    current = TABLE.read_bytes()
    if digest(current) != EXPECTED:
        raise SystemExit("candidate table changed since review")
    if current.count(OLD) != 1:
        raise SystemExit("expected exactly one p.131 candidate source locator")
    updated = current.replace(OLD, NEW)
    print(f"{TABLE.relative_to(ROOT)}: {digest(current)} -> {digest(updated)}")
    if not args.apply:
        print("dry-run only; no table written")
        return
    backup = TABLE.with_name(TABLE.name + ".bak-s2-chp5-p131-source-ref-20261012")
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
    shutil.copy2(TABLE, backup)
    if digest(backup.read_bytes()) != EXPECTED:
        raise SystemExit("recovery copy hash mismatch")
    atomic_write(TABLE, updated)
    if digest(TABLE.read_bytes()) != digest(updated):
        raise SystemExit("post-write hash mismatch")
    print(f"applied; backup={backup.name}; sha256={digest(TABLE.read_bytes())}")


if __name__ == "__main__":
    main()
