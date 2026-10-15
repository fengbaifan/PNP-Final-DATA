#!/usr/bin/env python3
"""Repair the p.107 candidate source reference to use the S2 segment ID contract."""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l101-107"
CANDIDATE_ID = "cand-11648"
EXPECTED_SHA256 = "b9db2d2d0a03e0d05d20c7f25134bac0962f45d5bac3ca2c48f35669c8f38b6d"
EXPECTED_OLD_REF = "02-sources/02-Markdown/04_CHP-4_sec_ii.md#L102"
EXPECTED_NEW_REF = SEGMENT_ID + "#L102"
BACKUP_SUFFIX = "bak-s2-chp4-p107-candidate-source-ref-20261011"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    path = TABLES / "entity-candidates.csv"
    before = path.read_bytes()
    if sha(before) != EXPECTED_SHA256:
        raise SystemExit("preflight failed: candidate table hash changed")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    matches = [row for row in rows if row["candidate_id"] == CANDIDATE_ID]
    if len(matches) != 1:
        raise SystemExit("preflight failed: expected one p.107 candidate")
    row = matches[0]
    if row.get("candidate_origin") != "body-mention" or row.get("candidate_source_ref") != EXPECTED_OLD_REF:
        raise SystemExit("preflight failed: candidate origin or source reference changed")

    coverage_path = TABLES / "s2-coverage.csv"
    with coverage_path.open(encoding="utf-8-sig", newline="") as handle:
        coverage = list(csv.DictReader(handle))
    source_segments = [item for item in coverage if item.get("segment_id") == SEGMENT_ID]
    if len(source_segments) != 1:
        raise SystemExit("preflight failed: S2 segment does not resolve uniquely")
    item = source_segments[0]
    if item.get("disposition") != "reviewed" or "L101-107" not in item.get("source_line_ranges", ""):
        raise SystemExit("preflight failed: candidate source line is not covered")

    row["candidate_source_ref"] = EXPECTED_NEW_REF
    plan = {
        "mode": "apply" if args.apply else "dry-run",
        "candidate_id": CANDIDATE_ID,
        "old_ref": EXPECTED_OLD_REF,
        "new_ref": EXPECTED_NEW_REF,
        "table_sha256_before": sha(before),
        "backup": path.name + "." + BACKUP_SUFFIX,
    }
    print(plan)
    if not args.apply:
        return

    backup = path.with_name(path.name + "." + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("apply refused: recovery backup already exists")
    shutil.copy2(path, backup)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        written = list(csv.DictReader(handle))
    final = next((item for item in written if item["candidate_id"] == CANDIDATE_ID), None)
    if not final or final.get("candidate_source_ref") != EXPECTED_NEW_REF:
        raise SystemExit("post-write verification failed; recovery backup retained")
    print("apply complete")
    print("candidate_sha256=" + sha(path.read_bytes()))
    print("backup=" + backup.name)


if __name__ == "__main__":
    main()
