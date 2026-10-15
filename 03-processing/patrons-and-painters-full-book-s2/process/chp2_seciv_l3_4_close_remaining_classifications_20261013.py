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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l3-4"
SEGMENT_SHA = "b6105d2699fd40909d7c847e55bd8b5e9c9b45d2c0919fe6373b1649305b9243"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
CARDINAL_ID = "st-chp2-seciv-l3-4-francesco-cardinalate"
CHARACTER_ID = "st-chp2-seciv-l3-4-francesco-characterization"
PRIOR_APPOINTMENT_ID = "st-chp2-sec-ii-l3-8-francesco-cardinal"
BACKUP_SUFFIX = ".bak-s2-chp2-seciv-l3-4-classifications-20261013"
EXPECTED = {
    "book-statements.jsonl": "920e525648a6f530d16c6d810f0d8354c5209a81765d7bf427c799c7c2292b47",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "c91a9d72fb9e056c343038f1f86f6098622f8469f92508296e897f6f9747b5c3",
}
CARDINAL_NOTE = (
    "The clause leaves the appointing agent implicit. The linked preceding-section statement explicitly says "
    "Urban VIII made Francesco a cardinal six weeks after his election; this row reuses that stated attribution "
    "and timing without inferring the agent from kinship alone."
)
CHARACTER_NOTE = (
    "This reports Francesco's personal traits and Haskell's characterization, not an entity relation. "
    "'Universally described' is an unbounded reception claim; footnote 2 points to Barozzi e Berchet, I, p. 214, "
    "but does not identify a bounded describer entity to model. Preserve the source attribution and qualification."
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
    parser = argparse.ArgumentParser(
        description="Classify the remaining S2 claims in CHP-2 section IV, L3-4."
    )
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
        raise SystemExit("protected CHP-2 p.43 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    cardinal = statement_by_id.get(CARDINAL_ID)
    character = statement_by_id.get(CHARACTER_ID)
    prior = statement_by_id.get(PRIOR_APPOINTMENT_ID)
    if not cardinal or not character or not prior:
        raise SystemExit("one or more protected statements are missing")
    if cardinal.get("segment_id") != SEGMENT_ID or character.get("segment_id") != SEGMENT_ID:
        raise SystemExit("protected statements moved to another segment")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != {CARDINAL_ID, CHARACTER_ID}:
        raise SystemExit(f"unexpected unset statement set: {sorted(unset)}")
    if cardinal.get("subject_candidate_id") is not None or cardinal.get("object_candidate_id") != "cand-3035":
        raise SystemExit("protected cardinalate endpoint mapping changed")
    if character.get("subject_candidate_id") != "cand-3035" or character.get("object_candidate_id") is not None:
        raise SystemExit("protected characterization endpoint mapping changed")
    if (
        prior.get("subject_candidate_id") != "cand-3104"
        or prior.get("object_candidate_id") != "cand-3035"
        or prior.get("predicate") != "appointed_to_cardinalate"
        or prior.get("qualifiers", {}).get("relation_candidate") is not True
    ):
        raise SystemExit("the explicit preceding-section appointment evidence changed")
    candidate_ids = {row["candidate_id"] for row in candidates}
    if not {"cand-3035", "cand-3104"}.issubset(candidate_ids):
        raise SystemExit("one or more referenced person candidates are missing")
    if not {"cand-3035", "cand-3104"}.issubset({row["candidate_id"] for row in mentions if row.get("segment_id") == SEGMENT_ID}):
        raise SystemExit("the segment lacks a mention for one or more referenced people")

    source_text = SOURCE.read_text(encoding="utf-8-sig")
    expected_quotes = {
        CARDINAL_ID: cardinal.get("original_quote"),
        CHARACTER_ID: character.get("original_quote"),
    }
    for statement_id, quote in expected_quotes.items():
        if not quote or quote not in source_text:
            raise SystemExit(f"statement quote no longer matches the protected source: {statement_id}")
    if len([row for row in coverage if row.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one section IV L3-4 coverage row")

    cardinal["subject_candidate_id"] = "cand-3104"
    cardinal["object_candidate_id"] = "cand-3035"
    cardinal["predicate"] = "appointed_to_cardinalate"
    cardinal_qualifiers = cardinal.setdefault("qualifiers", {})
    cardinal_qualifiers["claim"] = (
        "Haskell reports that Francesco was made a cardinal; the linked preceding section explicitly attributes "
        "the appointment to Urban VIII."
    )
    cardinal_qualifiers["relation_candidate"] = True
    cardinal_qualifiers["relation_candidate_note"] = CARDINAL_NOTE
    cardinal_qualifiers["mentioned_candidate_ids"] = ["cand-3104", "cand-3035"]
    cardinal_qualifiers["related_statement_ids"] = [PRIOR_APPOINTMENT_ID]
    cardinal_qualifiers["qualification"] = CARDINAL_NOTE
    cardinal_qualifiers.pop("open_endpoint_reason", None)

    character_qualifiers = character.setdefault("qualifiers", {})
    character_qualifiers["relation_candidate"] = False
    character_qualifiers["relation_candidate_note"] = CHARACTER_NOTE
    character_qualifiers["mentioned_candidate_ids"] = ["cand-3035"]
    character_qualifiers.pop("open_endpoint_reason", None)

    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_note = (
        " S2 classification closure: reused the explicitly attributed Urban VIII–Francesco cardinal appointment "
        "from section II; classified Francesco's reported personal characterization as non-relational. "
        "Print p.43 / PDF physical p.28; source asset unchanged."
    )
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    if any(
        row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
        for row in statements
    ):
        raise SystemExit("L3-4 still has unset relation_candidate values")
    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    result = {
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "classified_unset_ids": [CARDINAL_ID, CHARACTER_ID],
        "classifications": {CARDINAL_ID: True, CHARACTER_ID: False},
        "reused_explicit_appointment_evidence": PRIOR_APPOINTMENT_ID,
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
        written_by_id = {row["statement_id"]: row for row in written}
        if written_by_id[CARDINAL_ID].get("qualifiers", {}).get("relation_candidate") is not True:
            raise SystemExit("cardinal appointment classification was not persisted")
        if written_by_id[CHARACTER_ID].get("qualifiers", {}).get("relation_candidate") is not False:
            raise SystemExit("characterization classification was not persisted")
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
