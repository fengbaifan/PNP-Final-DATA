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
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l124-157"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
SOURCE_SHA = "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6"
SEGMENT_SHA = "ff068d6951eb10bf2a5a8e4f895c0d6f1cb1ccc2ea00c6d8de0d58fe11dd3862"
BACKUP_SUFFIX = ".bak-s2-chp2-seci-l124-157-20261012"
EXPECTED = {
    "book-statements.jsonl": "6e3ca5f2ca6292342d80b8991f2f9249e8c8078349cf824067bfeb960ac218b4",
    "entity-candidates.csv": "5ec5a3c6b47230063fa994f5220ed53a05f2ba9a1287e63aa0e3dfb7b6e80153",
    "mentions.csv": "9b1b0b6cf70fe0c110749ad60baef0f8e6ada0b44077cfde9fece28a60cb2cfa",
    "s2-coverage.csv": "c4223ae83a75f610093e7b406b6465c58b53db86107df5245b3d8a2ba44170ba",
}
CITATIONS = {
    "st-chp2-seci-l124-157-cite-avviso-1624": "Footnote 1 explicitly cites the 1624 avviso through Roma, XVII (1939), p. 270; this records Haskell’s citation, not independent verification of the notice.",
    "st-chp2-seci-l124-157-cite-barozzi-p162": "Footnote 1 explicitly cites Barozzi e Berchet, I, p. 162; the cited passage has not been independently examined.",
    "st-chp2-seci-l124-157-cite-bellori-1976": "Footnote 4 explicitly cites Bellori (1976), p. 541; title and edition remain unspecified.",
    "st-chp2-seci-l124-157-cite-orbaan": "Footnote 1 points readers to Orbaan (1920) for additional references; the individual cited passages are unspecified.",
    "st-chp2-seci-l124-157-cite-rinaldis-archivi": "Footnote 3 explicitly includes the 1936 de Rinaldis article in Archivi, pp. 110–118; the article’s contents are not independently verified.",
    "st-chp2-seci-l124-157-cite-rinaldis-bollettino": "Footnote 3 explicitly cites de Rinaldis in Bollettino d’Arte, XXIX (1936), pp. 577–580; the article’s contents are not independently verified.",
    "st-chp2-seci-l124-157-cite-rosi": "Footnote 2 explicitly cites Rosi, pp. 347–370, for the witchcraft discussion; the full bibliographic record remains incomplete.",
    "st-chp2-seci-l124-157-cite-venturi": "Footnote 3 directs readers to A. Venturi, pp. 113–131, for the preceding discussion; this records the citation pointer without resolving its scope.",
}
CHAPEL_RELATIONS = {
    "st-chp2-seci-l124-157-strozzi-chapels": "cand-4360",
    "st-chp2-seci-l124-157-rucellai-chapels": "cand-4361",
}
UNSET = set(CITATIONS) | set(CHAPEL_RELATIONS)


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
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected CHP-2 section source changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected footnote segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None
    }
    if unset != UNSET:
        raise SystemExit(f"unexpected footnote unset statement set: {sorted(unset)}")
    if "cand-2962" not in candidate_ids:
        raise SystemExit("Haskell book candidate cand-2962 is missing")

    for statement_id, note in CITATIONS.items():
        row = statement_by_id[statement_id]
        if not row.get("object_candidate_id") or row["object_candidate_id"] not in candidate_ids:
            raise SystemExit(f"citation object candidate missing: {statement_id}")
        row.update({"subject_candidate_id": "cand-2962", "predicate": "cites"})
        row["qualifiers"].update({
            "relation_candidate": True,
            "relation_candidate_note": note,
            "mentioned_candidate_ids": ["cand-2962", row["object_candidate_id"]],
        })

    for statement_id, family_id in CHAPEL_RELATIONS.items():
        if family_id not in candidate_ids:
            raise SystemExit(f"chapel family candidate missing: {family_id}")
        row = statement_by_id[statement_id]
        row.update({"subject_candidate_id": None, "object_candidate_id": family_id, "predicate": "belonged_to_family_reported"})
        row["qualifiers"].update({
            "relation_candidate": True,
            "relation_candidate_note": "Footnote 6 states that other chapels belonged to this family; preserve the reported relation without assigning a chapel identity.",
            "open_endpoint_reason": "The chapels are unnamed and no number, location, or individual identity is supplied.",
            "mentioned_candidate_ids": [family_id],
        })

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
        raise SystemExit(f"missing footnote candidate foreign keys: {missing}")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"footnote segment still has unset values: {remaining}")
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one footnote coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up closed ten unset relation_candidate fields: eight explicit citation links now point from the book candidate to the cited sources, "
        "without treating the cited works as independently verified; the two chapel-family statements remain open relation candidates because the chapels are unnamed."
    )

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2.pdf footnotes / normalized S0 L124-157; print pp.25-31",
        "classified_unset_ids": sorted(UNSET),
        "citation_links": len(CITATIONS),
        "open_chapel_relations": sorted(CHAPEL_RELATIONS),
        "segment_unset_count": 0,
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
            temp = path.with_name(path.name + ".tmp-s2-chp2-notes")
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
