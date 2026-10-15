from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/entity-candidates.csv"
EXPECTED_SHA256 = "d1bce9baaf8287ad74cdad20f6630db42dfaaea321a696a4335340965c0646f1"
OLD = b"chp-17:17_CHP-17_sec_i:l8-20#L11-L12"
NEW = b"chp-17:17_CHP-17_sec_i:l8-20#L11"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp17-p380-source-ref-20261015")
TEMP = TABLE.with_name(TABLE.name + ".tmp-s2-chp17-p380-source-ref-20261015")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Use the candidate source-ref syntax accepted by the strict S2 audit.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if sha(raw) != EXPECTED_SHA256:
        raise ValueError("Candidate table changed since the guarded review batch.")
    if raw.count(OLD) != 1:
        raise ValueError("Expected exactly one p.380 range-style candidate source ref.")
    updated = raw.replace(OLD, NEW, 1)
    print({"before": sha(raw), "after": sha(updated), "candidate": "cand-12423", "source_ref": NEW.decode("ascii")})
    if args.preview:
        return 0

    if BACKUP.exists() or TEMP.exists():
        raise ValueError("A planned backup or temporary file already exists.")
    TEMP.write_bytes(updated)
    shutil.copy2(TABLE, BACKUP)
    TEMP.replace(TABLE)
    print("APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
