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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l127-139"
SEGMENT_SHA = "4d2e65b99c5e5c8e49ecdc544ab6b88763a2ffa3ce1e5ca424eac5ca6d36da36"
SOURCE_SHA = "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9"
BACKUP_SUFFIX = ".bak-s2-chp2-secii-l127-139-close-unset-20261012"
EXPECTED = {
    "book-statements.jsonl": "35f413846ea735f1fad5e7a296dbd377413ee0389d1a0a9ad5bc105d5a64cdce",
    "entity-candidates.csv": "dcce40f3b1d7b1cd4c7c10e8962f79f7c588be418c9737af4fd2f69e8114fb74",
    "mentions.csv": "e8769d49402b02dac6800f06c3f16970ab58a8c66eb1f37ba1dfd2bf3a9ee856",
    "s2-coverage.csv": "c3a9f0546526a81246e5f1d78dbdae6ec043bbace40934fa0f16a71854afc85b",
}
UNSET_IDS = {
    "st-chp2-secii-l127-139-antonio-character-and-capuchin-life",
    "st-chp2-secii-l127-139-footnote1-author-tail",
    "st-chp2-secii-l127-139-urban-dynastic-motive-fragment",
    "st-chp2-secii-l127-139-urban-tomb-pause-and-1639-resumption",
    "st-chp2-secii-l127-139-urban-tomb-work-stopped-again",
    "st-chp2-secii-l127-139-antonio-cardinal-status-and-simple-life",
}
NEW_STATEMENT_ID = "st-chp2-secii-l127-139-antonio-simple-lifestyle"
FALSE_NOTES = {
    "st-chp2-secii-l127-139-antonio-character-and-capuchin-life": (
        "Haskell's judgments about Antonio's temperament and reluctance are authorial biographical characterization; "
        "his Capuchin membership is recorded separately, and the Barberini family is only the comparison group here."
    ),
    "st-chp2-secii-l127-139-footnote1-author-tail": (
        "This is the terminal name fragment of footnote 1; the complete note's study-to-author relation is recorded "
        "in the linked cross-segment authored_by statement, so the fragment is not a second relation claim."
    ),
    "st-chp2-secii-l127-139-urban-dynastic-motive-fragment": (
        "This is Haskell's incomplete interpretation of Urban VIII's motive. The completed, specifically bounded "
        "claim about other princes' arms is recorded in the linked continuation statement; this fragment supplies no separate endpoint."
    ),
    "st-chp2-secii-l127-139-urban-tomb-pause-and-1639-resumption": (
        "This preserves the tomb's internal construction chronology (an eight-year pause and 1639 resumption); "
        "it names no separate actor or event endpoint. Urban VIII's intervening commissions are recorded in their own relation statement."
    ),
    "st-chp2-secii-l127-139-urban-tomb-work-stopped-again": (
        "This preserves the tomb's construction-status chronology without a named stoppage event or actor; "
        "the subsequent Urban VIII completion attempt is recorded separately as a relation to the tomb."
    ),
    "st-chp2-secii-l127-139-antonio-cardinal-status-and-simple-life": (
        "The sentence supplies biographical title detail and is followed by a lifestyle characterization. "
        "Antonio's cardinalate appointment is already represented by the earlier L3-8 relation statement; no separate title entity is required here."
    ),
    NEW_STATEMENT_ID: (
        "This is Haskell's biographical characterization of Antonio's lifestyle, not a relation to an independent entity."
    ),
}


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


def classify(row: dict, note: str, candidate_ids: list[str]) -> None:
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = False
    qualifiers["relation_candidate_note"] = note
    qualifiers["mentioned_candidate_ids"] = candidate_ids
    qualifiers.pop("open_endpoint_reason", None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Close the remaining S2 classifications in CHP-2 L127-139.")
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
        raise SystemExit("protected printed p.42 source segment fingerprint changed")

    statements = read_jsonl(paths["book-statements.jsonl"])
    candidates = read_csv(paths["entity-candidates.csv"])
    mentions = read_csv(paths["mentions.csv"])
    coverage = read_csv(paths["s2-coverage.csv"])
    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row["statement_id"] for row in statements
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != UNSET_IDS:
        raise SystemExit(f"unexpected p.42 unset statement set: {sorted(unset)}")
    if NEW_STATEMENT_ID in statement_by_id:
        raise SystemExit(f"planned statement ID already exists: {NEW_STATEMENT_ID}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[126:139])
    status = statement_by_id["st-chp2-secii-l127-139-antonio-cardinal-status-and-simple-life"]
    if status.get("original_quote") != "Though made Cardinal di S. Onofrio, he continued to live as simply as his new circumstances would allow.":
        raise SystemExit("protected Antonio status/lifestyle quotation changed")
    if status["original_quote"] not in source_text:
        raise SystemExit("protected Antonio quote no longer matches p.42 source lines")
    if not {"cand-0186", "cand-0198", "cand-0213", "cand-0236", "cand-3405", "cand-4512", "cand-4536"}.issubset(candidate_ids):
        raise SystemExit("a required p.42 person, family, institution, or work candidate is missing")
    if "st-chp2-secii-l141-145-urban-dynastic-motive-continuation" not in statement_by_id:
        raise SystemExit("the next-page continuation of Urban VIII's motive is missing")
    continuation = statement_by_id["st-chp2-secii-l141-145-urban-dynastic-motive-continuation"]
    if continuation.get("qualifiers", {}).get("relation_candidate") is not True:
        raise SystemExit("the completed dynastic-motive relation is no longer classified")
    if len([row for row in coverage if row.get("segment_id") == SEGMENT_ID]) != 1:
        raise SystemExit("expected one p.42 coverage row")

    for statement_id, note in FALSE_NOTES.items():
        if statement_id == NEW_STATEMENT_ID:
            continue
        row = statement_by_id[statement_id]
        mentioned = [row["subject_candidate_id"]] if row.get("subject_candidate_id") else []
        if statement_id == "st-chp2-secii-l127-139-urban-tomb-pause-and-1639-resumption":
            mentioned = ["cand-4512", "cand-0236"]
        classify(row, note, mentioned)

    status["qualifiers"]["claim"] = "Haskell identifies Antonio Barberini as Cardinal di S. Onofrio."
    status["qualifiers"]["qualification"] = (
        "The source names Antonio's cardinal title but does not name an appointing actor in this sentence; "
        "the cardinalate appointment is separately represented in the earlier L3-8 relation statement."
    )
    status["qualifiers"].pop("subsequent_lifestyle", None)
    status["original_quote"] = "Though made Cardinal di S. Onofrio,"
    lifestyle = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0186",
        "object_candidate_id": None,
        "predicate": "authorial_lifestyle_characterization",
        "qualifiers": {
            "source_line_start": 132,
            "source_line_end": 132,
            "claim": "Haskell says Antonio Barberini continued to live as simply as his new circumstances would allow.",
            "speaker": "Haskell",
            "text_layer": "authorial biographical characterization",
            "qualification": "This is a characterization of Antonio's way of life, separate from the cardinal-title detail in the preceding clause.",
            "print_page": "42",
            "pdf_page": 27,
        },
        "original_quote": "he continued to live as simply as his new circumstances would allow.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    }
    classify(lifestyle, FALSE_NOTES[NEW_STATEMENT_ID], ["cand-0186"])
    if lifestyle["original_quote"] not in source_text:
        raise SystemExit("split lifestyle quote does not match p.42 source lines")
    status_at = statements.index(status)
    statements.insert(status_at + 1, lifestyle)
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("statement IDs are not unique after write preparation")
    if any(
        row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
        for row in statements
    ):
        raise SystemExit("p.42 segment still has unset relation_candidate values")

    coverage_row = next(row for row in coverage if row.get("segment_id") == SEGMENT_ID)
    coverage_note = (
        " S2 follow-up closes six remaining classifications: Antonio's evaluative biography, the footnote-author fragment, "
        "the incomplete Urban VIII motive fragment, and two tomb-work chronology claims remain non-relational; the motive's "
        "complete dynastic-arm relation is retained in L141-145. Antonio's Cardinal di S. Onofrio title and simple-lifestyle "
        "clause are separated as two biographical claims. Printed p.42 (PDF page 27) was checked; S0 remains unchanged."
    )
    if coverage_note.strip() not in coverage_row["note"]:
        coverage_row["note"] = coverage_row["note"].rstrip() + coverage_note

    updated = {"book-statements.jsonl": statements, "s2-coverage.csv": coverage}
    payloads = {name: serialize(name, data) for name, data in updated.items()}
    print(json.dumps({
        "mode": "apply" if args.apply else "preview",
        "segment": SEGMENT_ID,
        "classified_unset_ids": sorted(UNSET_IDS),
        "new_statement_ids": [NEW_STATEMENT_ID],
        "classification_of_new_statement": False,
        "new_candidates": 0,
        "new_mentions": 0,
        "remaining_unset_in_segment": [],
        "motive_continuation_relation_retained": continuation["qualifiers"]["relation_candidate"],
        "source_unchanged": True,
        "payload_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
    }, ensure_ascii=False, indent=2))
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
        if any(written_by_id[statement_id]["qualifiers"].get("relation_candidate") is not False for statement_id in FALSE_NOTES):
            raise SystemExit("a p.42 non-relational classification was not persisted")
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
        "statement_count": len(statements),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
