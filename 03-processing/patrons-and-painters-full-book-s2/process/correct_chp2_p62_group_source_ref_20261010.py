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
TABLE = ROOT / "04-knowledge/tables/entity-candidates.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
EXPECTED_SHA = "8df259e87cc38c00e41386893f23851b5cb69e581e9e8f01d5285ba376b9494f"
OLD_REF = "chp-2:02_CHP-2_sec_viii:l3-7#L3-L4"
NEW_REF = "chp-2:02_CHP-2_sec_viii:l3-7#L3"
BACKUP_SUFFIX = ".bak-s2-handoff-chp2-p62-group-source-ref-fix-20261010"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    require(sha(TABLE) == EXPECTED_SHA, "candidate table changed since the inspected batch")
    raw = TABLE.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    with TABLE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    matches = [r for r in rows if r.get("candidate_id") == "cand-11577"]
    require(len(matches) == 1 and matches[0].get("candidate_source_ref") == OLD_REF,
            "expected exact source-ref defect is not present")
    with COVERAGE.open("r", encoding="utf-8-sig", newline="") as f:
        cov = {r["segment_id"]: r for r in csv.DictReader(f)}
    segment_id = NEW_REF.split("#", 1)[0]
    require(segment_id in cov and cov[segment_id].get("disposition") == "reviewed"
            and "L3-7" in cov[segment_id].get("source_line_ranges", ""),
            "candidate source line is not covered as reviewed")
    matches[0]["candidate_source_ref"] = NEW_REF
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    payload = buf.getvalue().encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    print({"action": "apply" if args.apply else "dry-run", "candidate": "cand-11577",
           "old_ref": OLD_REF, "new_ref": NEW_REF, "table_sha_before": EXPECTED_SHA})
    if not args.apply:
        return
    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    require(not backup.exists(), "recovery backup already exists")
    shutil.copy2(TABLE, backup)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=TABLE.parent, prefix=TABLE.name + ".tmp-", delete=False) as f:
            f.write(payload)
            temp = Path(f.name)
        os.replace(temp, TABLE)
        with TABLE.open("r", encoding="utf-8-sig", newline="") as f:
            check = {r["candidate_id"]: r for r in csv.DictReader(f)}
        require(check["cand-11577"]["candidate_source_ref"] == NEW_REF,
                "post-write source-ref check failed")
        print({"result": "applied", "table_sha_after": sha(TABLE),
               "backup": str(backup.relative_to(ROOT))})
    except Exception:
        shutil.copy2(backup, TABLE)
        raise
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


if __name__ == "__main__":
    main()
