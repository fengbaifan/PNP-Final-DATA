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
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l95-106"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
SOURCE_SHA = "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6"
SEGMENT_SHA = "165eaffa3127c4d1978a6d3bddf30c96e2b139803117cdefc6d8c02d0c04df8a"
BACKUP_SUFFIX = ".bak-s2-chp2-seci-l95-106-20261012"
EXPECTED = {
    "book-statements.jsonl": "9bbb9285f282b37abf17933618aad061eb41b63ef1741c58845cbfd82e300e39",
    "entity-candidates.csv": "fd67cc44fa25b9a12f652e384afe37d263c830dc005b21d83a2a3ff0fd211929",
    "mentions.csv": "ff30b863260bf4b8418473e8193707659e40664347f9d64deb112ce7e58a7865",
    "s2-coverage.csv": "8f05e1179a102fc4dd352151245e9c00f3c2556c02557ae49274f5c31eac5da2",
}
UNSET = {
    "st-chp2-seci-l95-106-continued-search",
    "st-chp2-seci-l95-106-cupid-eroticism",
    "st-chp2-seci-l95-106-largest-group-assessment",
    "st-chp2-seci-l95-106-party-description",
    "st-chp2-seci-l95-106-pleasure-lifestyle",
    "st-chp2-seci-l95-106-quote-continuation",
    "st-chp2-seci-l95-106-religious-majority",
    "st-chp2-seci-l95-106-sacchi-unknown",
    "st-chp2-seci-l95-106-vincenzo-wealth",
    "st-chp2-seci-l95-106-wide-catholic-taste",
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
    candidates = read_csv(paths["entity-candidates.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.29 source segment fingerprint changed")

    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None
    }
    if unset != UNSET:
        raise SystemExit(f"unexpected p.29 unset statement set: {sorted(unset)}")
    for candidate_id in ("cand-1691", "cand-4313", "cand-4316"):
        if candidate_id not in candidate_ids:
            raise SystemExit(f"required existing candidate missing: {candidate_id}")

    false_decisions = {
        "st-chp2-seci-l95-106-cupid-eroticism": "This is Haskell’s evaluative description of the unidentified Cupid painting, not a relation between entities.",
        "st-chp2-seci-l95-106-largest-group-assessment": "This is Haskell’s comparative assessment of the thirteen-painting group; the comparison set is unspecified and creates no relation.",
        "st-chp2-seci-l95-106-party-description": "This is an embedded description of Del Monte’s parties and their entertainment, not a relation to an independently identified event or participant.",
        "st-chp2-seci-l95-106-pleasure-lifestyle": "This is a biographical description of Del Monte’s lifestyle, not a relation claim.",
        "st-chp2-seci-l95-106-quote-continuation": "This continues an unidentified later source’s biographical description of Del Monte; it does not assert a relation between entities.",
        "st-chp2-seci-l95-106-religious-majority": "This is a qualitative attribute of the collection’s contents; no distinct work or religious-art entity is identified, so it does not establish collection-item edges.",
        "st-chp2-seci-l95-106-sacchi-unknown": "This is Haskell’s time-bound characterization of Sacchi’s reputation at the commission, not a relation claim.",
        "st-chp2-seci-l95-106-vincenzo-wealth": "This is Haskell’s characterization of Vincenzo’s wealth, not a relation claim.",
        "st-chp2-seci-l95-106-wide-catholic-taste": "This is Haskell’s inference about Vincenzo’s breadth of taste from the collection; it is not a relation between entities.",
    }
    for statement_id, note in false_decisions.items():
        statement_by_id[statement_id]["qualifiers"].update({
            "relation_candidate": False,
            "relation_candidate_note": note,
        })

    search = statement_by_id["st-chp2-seci-l95-106-continued-search"]
    search["predicate"] = "searched_studios_for_artists_reported"
    search["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell directly reports that del Monte continued to explore studios in search of talented artists; preserve the activity without identifying particular studios or artists.",
        "open_endpoint_reason": "The studios and prospective artists are plural and unnamed in this passage.",
        "mentioned_candidate_ids": ["cand-1691"],
    })
    statement_by_id["st-chp2-seci-l95-106-largest-group-assessment"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-4316"]
    statement_by_id["st-chp2-seci-l95-106-religious-majority"]["qualifiers"]["mentioned_candidate_ids"] = ["cand-4313"]

    referenced = set()
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced.add(row[key])
        referenced.update(row["qualifiers"].get("mentioned_candidate_ids", []))
    missing = sorted(referenced - candidate_ids)
    if missing:
        raise SystemExit(f"missing p.29 candidate foreign keys: {missing}")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"p.29 segment still has unset values: {remaining}")
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.29 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up closed ten unset relation_candidate fields. Del Monte’s continued search through studios for talented artists remains an open relation candidate because neither the studios nor prospective artists are identified. "
        "The quote, lifestyle descriptions, comparative assessments, collection distribution, and authorial judgments are classified as non-relational; the existing candidate links to the collection and thirteen-painting group are retained."
    )

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2.pdf print p.29 / normalized S0 L95-106",
        "classified_unset_ids": sorted(UNSET),
        "open_relation_candidates": [search["statement_id"]],
        "segment_unset_count": 0,
        "source_unchanged": True,
        "coverage_disposition": coverage_rows[0]["disposition"],
        "coverage_migration_status": coverage_rows[0]["migration_status"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
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
            temp = path.with_name(path.name + ".tmp-s2-chp2-p29")
            if temp.exists():
                raise SystemExit(f"stale temp file exists; refusing overwrite: {temp.name}")
            if name.endswith(".jsonl"):
                write_jsonl(temp, rows)
            else:
                write_csv(temp, rows)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
    except Exception:
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        raise
    result["backups"] = {name: path.name for name, path in backups.items()}
    result["post_hashes"] = {name: digest(paths[name]) for name in updated}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
