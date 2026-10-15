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
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l108-119"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
SOURCE_SHA = "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6"
SEGMENT_SHA = "eb79505a43436aa4d7a141a2314a8bf34fd450b0ac108511cda8880d292f65f3"
BACKUP_SUFFIX = ".bak-s2-chp2-seci-l108-119-20261012"
EXPECTED = {
    "book-statements.jsonl": "3173e19b299f2b977aa3156c9f6d47ba03d4412319cc95f94748fca83aedcb4c",
    "entity-candidates.csv": "fd67cc44fa25b9a12f652e384afe37d263c830dc005b21d83a2a3ff0fd211929",
    "mentions.csv": "ff30b863260bf4b8418473e8193707659e40664347f9d64deb112ce7e58a7865",
    "s2-coverage.csv": "cd14f3680a0fc6ad9f08f223f1f8c4cbd8549f86b7be3e0cc34c216c340f3bf5",
}
UNSET = {
    "st-chp2-seci-l108-119-bernini-employed-by-powerful-families",
    "st-chp2-seci-l108-119-maffeo-lived-splendidly",
    "st-chp2-seci-l108-119-recognised-artistic-revolution",
    "st-chp2-seci-l108-119-taste-more-defined-than-writings",
}
NEW_CANDIDATE_ID = "cand-11875"
NEW_MENTION_ID = "m-chp2-seci-l108-119-0073"
BAD_MENTION_ID = "m-chp2-seci-l108-119-0003"


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

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[107:119])
    segment = next((row for row in read_jsonl(TABLES / "segments.jsonl") if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected p.30 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None
    }
    if unset != UNSET:
        raise SystemExit(f"unexpected p.30 unset statement set: {sorted(unset)}")
    if NEW_CANDIDATE_ID in candidate_by_id or NEW_MENTION_ID in mention_by_id:
        raise SystemExit("planned candidate or mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 11874:
        raise SystemExit("candidate ID sequence changed; refusing to allocate cand-11875")

    new_candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Artistic revolution at the end of the sixteenth century",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell’s retrospective description of artistic change at the end of the sixteenth century; scope and identity remain unresolved. Do not merge with other revolution candidates by wording alone.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L109",
    }
    candidates.append(new_candidate)

    new_mention = {
        "mention_id": NEW_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": NEW_CANDIDATE_ID,
        "surface_form": "the artistic revolution",
        "start_char": "220",
        "end_char": "243",
        "note": "Haskell’s periodizing phrase for the artistic change said to have occurred at the end of the sixteenth century; candidate scope remains open.",
    }
    if segment_text[220:243] != new_mention["surface_form"]:
        raise SystemExit("new artistic-revolution mention does not match the protected source span")
    mentions.append(new_mention)

    bad_mention = mention_by_id.get(BAD_MENTION_ID)
    if not bad_mention or bad_mention.get("segment_id") != SEGMENT_ID or bad_mention.get("surface_form") != "he":
        raise SystemExit("expected incorrect ‘he’ mention was not found")
    if segment_text[int(bad_mention["start_char"]):int(bad_mention["end_char"])] != "he":
        raise SystemExit("protected ‘he’ mention span changed")
    bad_start, bad_end = int(bad_mention["start_char"]), int(bad_mention["end_char"])
    if not (segment_text[bad_start:bad_end] == "he" and segment_text[bad_start - 1].isalnum() and segment_text[bad_end].isalnum()):
        raise SystemExit("the ‘he’ mention no longer points inside ‘rather’")
    bad_mention["start_char"] = "183"
    bad_mention["end_char"] = "185"
    bad_mention["note"] = "Corrected to the standalone pronoun in ‘he realised’; the former offset matched the letters ‘he’ inside ‘rather’ and did not identify an entity mention."
    if segment_text[183:185] != "he" or segment_text[182].isalnum() or segment_text[185].isalnum():
        raise SystemExit("corrected standalone pronoun anchor failed validation")

    false_decisions = {
        "st-chp2-seci-l108-119-maffeo-lived-splendidly": "This is Haskell’s evaluative description of Maffeo’s lifestyle, not a relation claim.",
        "st-chp2-seci-l108-119-taste-more-defined-than-writings": "This is Haskell’s comparative assessment of Vincenzo’s taste and writings, not a relation between entities.",
    }
    for statement_id, note in false_decisions.items():
        statement_by_id[statement_id]["qualifiers"].update({
            "relation_candidate": False,
            "relation_candidate_note": note,
        })

    families = statement_by_id["st-chp2-seci-l108-119-bernini-employed-by-powerful-families"]
    families.update({"subject_candidate_id": "cand-0295", "object_candidate_id": None, "predicate": "could_be_employed_by_reported"})
    families["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell explicitly states that only Rome’s most powerful families could employ a sculptor of Bernini’s ability; preserve the broad employment claim without inventing the family identities.",
        "open_endpoint_reason": "The powerful families are described as an unnamed group and are not individually identified.",
        "mentioned_candidate_ids": ["cand-0295"],
    })

    revolution = statement_by_id["st-chp2-seci-l108-119-recognised-artistic-revolution"]
    revolution["object_candidate_id"] = NEW_CANDIDATE_ID
    revolution["predicate"] = "realised_implications_of_reported"
    revolution["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": "Haskell credits Giustiniani with recognising the implications of the artistic revolution; retain this as the author’s retrospective interpretation, not independent verification.",
        "mentioned_candidate_ids": ["cand-1200", NEW_CANDIDATE_ID],
    })

    referenced = set()
    for row in statements:
        if row["segment_id"] != SEGMENT_ID:
            continue
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced.add(row[key])
        referenced.update(row["qualifiers"].get("mentioned_candidate_ids", []))
    missing = sorted(referenced - {row["candidate_id"] for row in candidates})
    if missing:
        raise SystemExit(f"missing p.30 candidate foreign keys: {missing}")
    remaining = [
        row["statement_id"] for row in statements
        if row["segment_id"] == SEGMENT_ID and row["qualifiers"].get("relation_candidate") is None
    ]
    if remaining:
        raise SystemExit(f"p.30 segment still has unset values: {remaining}")
    coverage_rows = [row for row in coverage if row["segment_id"] == SEGMENT_ID]
    if len(coverage_rows) != 1:
        raise SystemExit("expected one p.30 coverage row")
    coverage_rows[0]["note"] = coverage_rows[0]["note"].rstrip() + (
        " S2 follow-up closed four unset relation_candidate fields. Bernini’s employment by powerful Roman families remains an open relation candidate; the unnamed families are not inferred. "
        "Giustiniani’s recognition of the late-sixteenth-century artistic revolution remains an authorial interpretation and now points to a source-bounded body-mention candidate. "
        "Maffeo’s splendour and Vincenzo’s comparative taste assessment are non-relational. One Giustiniani pronoun mention was corrected from the substring ‘he’ inside ‘rather’ to the standalone ‘he realised’ in L109."
    )

    updated = {
        "book-statements.jsonl": statements,
        "entity-candidates.csv": candidates,
        "mentions.csv": mentions,
        "s2-coverage.csv": coverage,
    }
    result = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-2.pdf print p.30 / normalized S0 L108-119",
        "classified_unset_ids": sorted(UNSET),
        "new_candidate": NEW_CANDIDATE_ID,
        "new_mention": {"mention_id": NEW_MENTION_ID, "span": [220, 243]},
        "corrected_mention": {"mention_id": BAD_MENTION_ID, "old_span": [13, 15], "new_span": [183, 185]},
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
            temp = path.with_name(path.name + ".tmp-s2-chp2-p30")
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
