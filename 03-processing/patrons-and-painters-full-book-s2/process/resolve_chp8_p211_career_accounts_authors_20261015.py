from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
TARGET_ID = "st-chp8-p211-manini-salvini-career-accounts"
NEW_STATEMENT_ID = "st-chp8-p211-salvini-career-accounts"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l84-96"
EXPECTED_SEGMENT_HASH = "c4febe69e396257dee157d52e90f34ab1fdcc4c09162e8f81db5b744d70901ff"
BACKUP_SUFFIX = "bak-s2-chp8-p211-career-authors-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "bf6ac1f8a45a04995907a614d875e5ff2e1611941fc46e332091a7cf086bb81d",
    "mentions.csv": "8aa6d919cc6ffdc9af1fed84e91548298976003494cadb0cd5636092ea4b9e9b",
    "book-statements.jsonl": "d9fe999dfc78f759a3588121032974f3974743c30304ef7a9dff1fd803e06d08",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_open_true(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, _, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    actual = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(actual[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    candidate_ids = {row["candidate_id"] for row in candidates}
    if not {"cand-7505", "cand-7506"} <= candidate_ids:
        raise ValueError("One or both named author candidates are missing")
    segment = next(
        json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Source segment hash changed")
    author_mentions = {
        row["candidate_id"]: row for row in mentions
        if row["segment_id"] == SEGMENT_ID
        and row["candidate_id"] in {"cand-7505", "cand-7506"}
    }
    if set(author_mentions) != {"cand-7505", "cand-7506"}:
        raise ValueError("The named authors are not both mentioned in the source segment")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    index = {row["statement_id"]: pos for pos, row in enumerate(rows)}
    if TARGET_ID not in index or NEW_STATEMENT_ID in index:
        raise ValueError("Target statement missing or planned statement ID already exists")
    target = rows[index[TARGET_ID]]
    target_q = target.get("qualifiers") or {}
    if (
        target.get("segment_id") != SEGMENT_ID
        or target.get("subject_candidate_id") != "cand-12050"
        or target.get("object_candidate_id") is not None
        or not is_open_true(target)
        or not {"cand-7505", "cand-7506"} <= set(target_q.get("mentioned_candidate_ids") or [])
    ):
        raise ValueError("Target statement identity or open endpoint changed")
    before_open = sum(is_open_true(row) for row in rows)
    if before_open != 459:
        raise ValueError(f"Open endpoint count changed: {before_open}")

    target["predicate"] = "brief_career_accounts_attributed_to"
    target["object_candidate_id"] = "cand-7505"
    target_q["claim"] = "Haskell says the brief career accounts of Andrea and Ottavio are attributed to Giuseppe Manini."
    target_q["qualification"] = "The note names Manini and Salvini as providers; this atomic row isolates Manini's attribution without identifying a title, date, individual account-to-career mapping, or coauthored work."
    target_q["relation_candidate_note"] = "The source names Manini and Salvini as providers of brief career accounts. This row records the Manini attribution and preserves the unresolved bibliographic details."
    target_q["related_statement_ids"] = [NEW_STATEMENT_ID]
    target["qualifiers"] = target_q

    second = copy.deepcopy(target)
    second["statement_id"] = NEW_STATEMENT_ID
    second["object_candidate_id"] = "cand-7506"
    second_q = second["qualifiers"]
    second_q["claim"] = "Haskell says the brief career accounts of Andrea and Ottavio are attributed to Salvino Salvini."
    second_q["qualification"] = "The note names Manini and Salvini as providers; this atomic row isolates Salvini's attribution without identifying a title, date, individual account-to-career mapping, or coauthored work."
    second_q["relation_candidate_note"] = "The source names Manini and Salvini as providers of brief career accounts. This row records the Salvini attribution and preserves the unresolved bibliographic details."
    second_q["related_statement_ids"] = [TARGET_ID]
    second["qualifiers"] = second_q

    statement_after = ("".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in rows + [second]
    )).encode("utf-8")
    after_rows = [json.loads(line) for line in statement_after.decode("utf-8").splitlines()]
    after_open = sum(is_open_true(row) for row in after_rows)
    segment_open = [
        row["statement_id"] for row in after_rows
        if row.get("segment_id") == SEGMENT_ID and is_open_true(row)
    ]
    relation_true = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in after_rows)
    if after_open != 458 or segment_open or relation_true != 10390:
        raise ValueError(f"Unexpected post-update state: {after_open}, {segment_open}, {relation_true}")

    print(f"candidate_rows={len(candidates)}->{len(candidates)}")
    print(f"mention_rows={len(mentions)}->{len(mentions)}")
    print(f"statement_rows={len(rows)}->{len(rows) + 1}")
    print(f"planned_endpoint={TARGET_ID}|cand-12050->cand-7505")
    print(f"planned_statement={NEW_STATEMENT_ID}|cand-12050->cand-7506")
    print(f"open_endpoints={before_open}->{after_open}; relation_candidate_true={relation_true}")
    print(f"segment_open={segment_open}")
    print(f"{MENTIONS.relative_to(ROOT)} unchanged {digest(mention_raw)}")
    print(f"{STATEMENTS.relative_to(ROOT)} {digest(statement_raw)}->{digest(statement_after)}")
    if args.preview:
        return 0

    paths = ((STATEMENTS, statement_after),)
    pairs: list[tuple[Path, Path, bytes]] = []
    for path, data in paths:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        pairs.append((backup, temp, data))
    for path, (backup, _, _) in zip((STATEMENTS,), pairs, strict=True):
        shutil.copy2(path, backup)
    try:
        for (path, (_, temp, data)) in zip((STATEMENTS,), pairs, strict=True):
            temp.write_bytes(data)
        for path, (_, temp, _) in zip((STATEMENTS,), pairs, strict=True):
            temp.replace(path)
    except Exception:
        for _, temp, _ in pairs:
            if temp.exists():
                temp.unlink()
        raise
    for path, (backup, _, _) in zip((STATEMENTS,), pairs, strict=True):
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
