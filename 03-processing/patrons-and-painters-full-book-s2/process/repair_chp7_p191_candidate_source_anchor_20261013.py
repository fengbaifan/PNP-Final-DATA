from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
COVERAGE = ROOT / "04-knowledge" / "tables" / "s2-coverage.csv"
BACKUP = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv.bak-s2-chp7-seci-p191-candidate-source-ref-20261013"
EXPECTED_HASH = "783a9f8a549e9adf0a4cbbc78d42b985570772261cfb950d45bc179f1ca28501"
CANDIDATE_ID = "cand-12002"
OLD_REF = "chp-7:07_CHP-7_sec_i:l268-280#L270-L271"
NEW_REF = "chp-7:07_CHP-7_sec_i:l268-280#L270"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Use the audit schema's single-line source locator for cand-12002")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if sha(raw) != EXPECTED_HASH:
        raise SystemExit(f"candidate table hash changed: {sha(raw)}")
    encoding = "utf-8-sig"
    reader = csv.DictReader(io.StringIO(raw.decode(encoding), newline=""))
    fields = reader.fieldnames
    if not fields:
        raise SystemExit("candidate table header missing")
    rows = list(reader)
    by_id = {row["candidate_id"]: row for row in rows}
    candidate = by_id.get(CANDIDATE_ID)
    if not candidate or candidate.get("candidate_origin") != "body-mention" or candidate.get("candidate_source_ref") != OLD_REF:
        raise SystemExit("cand-12002 no longer has the expected source reference")

    coverage_rows = list(csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")))
    coverage = next((row for row in coverage_rows if row.get("segment_id") == NEW_REF.split("#", 1)[0]), None)
    if not coverage or coverage.get("disposition") != "reviewed" or "L268-280" not in coverage.get("source_line_ranges", ""):
        raise SystemExit("candidate source line is not within reviewed coverage")

    candidate["candidate_source_ref"] = NEW_REF
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fields} for row in rows)
    out = buffer.getvalue()
    if raw.startswith(b"\xef\xbb\xbf"):
        out = "\ufeff" + out
    output = out.encode("utf-8")
    print(f"mode={'apply' if args.apply else 'dry_run'} candidate={CANDIDATE_ID} source_ref={NEW_REF} before={sha(raw)} after={sha(output)}")
    if not args.apply:
        return
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    atomic_write(TABLE, output)
    print(f"APPLIED; recovery copy: {BACKUP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
