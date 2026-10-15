#!/usr/bin/env python3
"""Close remaining S2 relation-candidate classifications for CHP-2 p.25."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l44-53"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
BACKUP_SUFFIX = ".bak-s2-chp2-seci-l44-53-20261012"
EXPECTED = {
    "book-statements.jsonl": "423770c56de085770d4325076b0d1908b1993f2bd1b4c15e4f3ac656a095cb3b",
    "entity-candidates.csv": "fd67cc44fa25b9a12f652e384afe37d263c830dc005b21d83a2a3ff0fd211929",
    "mentions.csv": "ff30b863260bf4b8418473e8193707659e40664347f9d64deb112ce7e58a7865",
    "s2-coverage.csv": "1b8146b9a2f5e99768d8ee40f9f8b67ae1746b20a5a5abae507a26148c8f0399",
}
SOURCE_SHA = "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6"
SEGMENT_SHA = "9fbce3f3d95519a7927373e6fff8f82bfe3b09ead9133b0ba3bcec85e91deac4"
DECISIONS = {
    "st-chp2-seci-l44-53-artistic-interest": "Maffeo’s poetry and interest in the arts are personal interests, with no distinct entity endpoint asserted.",
    "st-chp2-seci-l44-53-bellori-description": "This is a quoted description of the subject depicted in a work, not a relation between the work and another historical entity.",
    "st-chp2-seci-l44-53-castelli-assessment": "Haskell’s qualitative comparison of Matteo Castelli is an authorial assessment, not a relation claim.",
    "st-chp2-seci-l44-53-marble-style": "Popularity and effectiveness of the architectural style are aesthetic characterizations; the specific Sixtus V and Paul V examples are separately recorded as relation candidates.",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    for name, expected in EXPECTED.items():
        actual = digest(TABLES / name)
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected CHP-2 section source changed")

    paths = {name: TABLES / name for name in EXPECTED}
    statements = read_jsonl(paths["book-statements.jsonl"])
    coverage = read_csv(paths["s2-coverage.csv"])
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.25 source segment fingerprint changed")
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {row["statement_id"] for row in statements if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None}
    if unset != set(DECISIONS):
        raise SystemExit(f"unexpected p.25 unset statement set: {sorted(unset)}")
    for statement_id, note in DECISIONS.items():
        q = statement_by_id[statement_id]["qualifiers"]
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.25 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up on printed p.25 closed four unset relation_candidate fields. "
        "Maffeo’s artistic interests, Bellori’s description of a depicted scene, Castelli’s qualitative assessment, "
        "and the generalized marble-style evaluation remain non-relational; specific patronage, commission, site, and style-attribution statements remain separately recorded."
    )
    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    summary = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2.pdf print p.25 / normalized S0 L44-53",
        "classified_as_non_relational": sorted(DECISIONS),
        "segment_unset_count": sum(row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None for row in statements),
        "source_unchanged": True,
        "coverage_disposition": coverage_rows[0]["disposition"],
        "coverage_migration_status": coverage_rows[0]["migration_status"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temp_paths: dict[str, Path] = {}
    try:
        for name in updated:
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
        for name, rows in updated.items():
            path = paths[name]
            temp = path.with_name(path.name + ".tmp-s2-chp2-p25")
            if temp.exists():
                raise SystemExit(f"stale temp file exists; refusing overwrite: {temp.name}")
            if name.endswith(".jsonl"):
                write_jsonl(temp, rows)
            else:
                write_csv(temp, rows)
            temp_paths[name] = temp
        for name, temp in temp_paths.items():
            os.replace(temp, paths[name])
    except Exception:
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        for temp in temp_paths.values():
            if temp.exists():
                temp.unlink()
        raise
    summary["backups"] = {name: path.name for name, path in backups.items()}
    summary["post_hashes"] = {name: digest(paths[name]) for name in updated}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
