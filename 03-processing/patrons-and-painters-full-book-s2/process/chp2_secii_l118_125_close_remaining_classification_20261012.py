from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l118-125"
SEGMENT_SHA = "b45e5832e49f40c221c95f72d8e4be732de3b687fd4ac95821a1cfafe469b27f"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
STATEMENT_ID = "st-chp2-secii-l118-125-carlo-statue-assessment"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l118-125-final-unset-20261012"
EXPECTED = {
    "book-statements.jsonl": "12c91690ea0b5e2043442f674a0d9b5eb1dd1a673a45f7465279f3f99bd7d999",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "a724772d0a5576ee66c85d3a35c17b095682867286f82435df9c1c9b1bf6c1fc",
}
NOTE = (
    "Haskell's artistic and psychological judgment of the Carlo monument is an authorial assessment, "
    "not a relation claim; retain the monument as the assessed subject and do not infer a contemporary response."
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def serialize(name: str, rows: list[dict]) -> bytes:
    if name.endswith(".jsonl"):
        return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Close the final unset S2 classification in CHP-2 L118-125.")
    parser.add_argument("--apply", action="store_true", help="write after protected checks; default is preview")
    args = parser.parse_args()
    paths = {name: TABLES / name for name in EXPECTED}
    for name, expected in EXPECTED.items():
        actual = digest(paths[name])
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE) != SOURCE_SHA:
        raise SystemExit("protected section source asset changed")
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.41 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    row = statement_by_id.get(STATEMENT_ID)
    if not row or row.get("segment_id") != SEGMENT_ID:
        raise SystemExit("protected Carlo assessment statement is missing or moved")
    unset = {
        item["statement_id"] for item in statements
        if item.get("segment_id") == SEGMENT_ID and item.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != {STATEMENT_ID}:
        raise SystemExit(f"unexpected p.41 unset statement set: {sorted(unset)}")
    if row.get("subject_candidate_id") != "cand-4508" or row.get("object_candidate_id") is not None:
        raise SystemExit("protected subject/object mapping changed")
    if "cand-4508" not in candidate_ids:
        raise SystemExit("the Carlo monument candidate is missing")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[117:125])
    if row.get("original_quote") != "Artistically the result is somewhat incongruous; psychologically much more so.":
        raise SystemExit("protected original quote changed")
    if row["original_quote"] not in source_text:
        raise SystemExit("the statement quote no longer matches the protected source segment")
    if len([item for item in coverage if item.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one p.41 coverage row")

    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = False
    qualifiers["relation_candidate_note"] = NOTE
    qualifiers["mentioned_candidate_ids"] = ["cand-4508"]
    qualifiers.pop("open_endpoint_reason", None)
    coverage_row = next(item for item in coverage if item.get("segment_id") == SEGMENT_ID)
    coverage_note = " S2 follow-up classifies the Carlo monument's artistic and psychological judgment as a non-relational authorial assessment; p.41 print page 41 / PDF page 26 was visually checked, and the S0 source asset remains unchanged."
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    if any(
        item.get("segment_id") == SEGMENT_ID and item.get("qualifiers", {}).get("relation_candidate") is None
        for item in statements
    ):
        raise SystemExit("p.41 segment still has unset relation_candidate values")
    updated = {
        "book-statements.jsonl": statements,
        "s2-coverage.csv": coverage,
    }
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "classified_unset_ids": [STATEMENT_ID],
        "classification": "false",
        "reason": NOTE,
        "new_candidates": 0,
        "new_mentions": 0,
        "remaining_unset_in_segment": [],
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temps: dict[str, Path] = {}
    try:
        for name, payload in payloads.items():
            path = paths[name]
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + ".s2tmp-", delete=False) as handle:
                temp = Path(handle.name)
                handle.write(payload)
            temps[name] = temp
        for name, temp in temps.items():
            os.replace(temp, paths[name])
        written = read_jsonl(paths["book-statements.jsonl"])
        written_row = next(item for item in written if item["statement_id"] == STATEMENT_ID)
        if written_row.get("qualifiers", {}).get("relation_candidate") is not False:
            raise SystemExit("the Carlo assessment classification was not persisted")
        if digest(SOURCE) != SOURCE_SHA:
            raise SystemExit("source asset changed during write")
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for name, backup in backups.items():
            shutil.copy2(backup, paths[name])
        raise
    print(json.dumps({
        "result": "applied",
        "backups": {name: backup.name for name, backup in backups.items()},
        "written_hashes": {name: digest(path) for name, path in paths.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
