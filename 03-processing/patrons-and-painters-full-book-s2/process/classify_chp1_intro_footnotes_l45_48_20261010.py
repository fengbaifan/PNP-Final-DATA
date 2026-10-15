from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
BACKUP = TABLES / "book-statements.jsonl.bak-s2-chp1-intro-footnotes-l45-48-20261010"
TARGET_SEGMENT = "chp-1:01_CHP-1_intro:l11-13"

EXPECTED_HASHES = {
    "04-knowledge/tables/book-statements.jsonl": "79914f790b12f0e8cdf15d9aa681cb09d6e844d781a645b9281e00e57b5831b8",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "04-knowledge/tables/mentions.csv": "10eb1687c3af1f4515cae4c68273a263f530dd3c8bb3613a3d2b26ddd9a54647",
    "04-knowledge/tables/s2-coverage.csv": "25ed4a10793e783a53989c3df50ddc66f688b7148454775f0111c30f2cffe621",
    "02-sources/02-Markdown/01_CHP-1_intro.md": "93c891b83017cd46962aafe0ee80e2d49c6858446647e42daad0ac034d95cfd6",
    "02-sources/02-Markdown/01_CHP-1.md": "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb",
}

EXPECTED_IDS = {
    "st-chp1-l45-46-lhoggidi-context",
    "st-chp1-l45-passeri-citation",
    "st-chp1-l46-47-lhoggidi-publication",
    "st-chp1-l48-coke-letter-citation",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def relation_counts(rows: list[dict]) -> dict[str, int]:
    flag = lambda row: row.get("qualifiers", {}).get("relation_candidate")
    bilateral = lambda row: bool(row.get("subject_candidate_id") and row.get("object_candidate_id"))
    return {
        "statements": len(rows),
        "true": sum(flag(row) is True for row in rows),
        "true_bilateral": sum(flag(row) is True and bilateral(row) for row in rows),
        "true_open": sum(flag(row) is True and not bilateral(row) for row in rows),
        "false": sum(flag(row) is False for row in rows),
        "unclassified_bilateral": sum(bilateral(row) and flag(row) is None for row in rows),
    }


def preflight() -> list[dict]:
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.exists(), f"missing input {relative}")
        require(sha256(path) == expected, f"SHA-256 changed for {relative}")

    candidates = {
        row["candidate_id"]: row
        for row in csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline=""))
    }
    expected_types = {
        "cand-0198": "family",
        "cand-1856": "person",
        "cand-2962": "archive",
        "cand-3085": "person",
        "cand-3401": "place",
        "cand-3420": "archive",
        "cand-3421": "archive",
        "cand-3422": "person",
        "cand-4376": "archive",
        "cand-5615": "archive",
    }
    for candidate_id, expected_type in expected_types.items():
        require(candidate_id in candidates, f"missing candidate {candidate_id}")
        require(candidates[candidate_id]["suggested_type"] == expected_type,
                f"unexpected type for {candidate_id}: {candidates[candidate_id]['suggested_type']}")

    coverage = list(csv.DictReader((TABLES / "s2-coverage.csv").open(encoding="utf-8-sig", newline="")))
    covered = [row for row in coverage if row.get("segment_id") == TARGET_SEGMENT]
    require(len(covered) == 1, "target segment coverage must be unique")
    require(covered[0].get("disposition") == "reviewed" and covered[0].get("migration_status") == "complete",
            "target segment must be reviewed/complete")

    mentions = list(csv.DictReader((TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="")))
    segment_mentions = {row["mention_id"]: row for row in mentions if row.get("segment_id") == TARGET_SEGMENT}
    expected_mentions = {
        "m-chp1-intro-0109": "cand-1856",
        "m-chp1-intro-0110": "cand-0198",
        "m-chp1-intro-0112": "cand-3420",
        "m-chp1-intro-0113": "cand-3401",
        "m-chp1-intro-0114": "cand-3421",
        "m-chp1-intro-0115": "cand-3085",
        "m-chp1-intro-0116": "cand-3422",
    }
    for mention_id, candidate_id in expected_mentions.items():
        require(mention_id in segment_mentions and segment_mentions[mention_id]["candidate_id"] == candidate_id,
                f"mention mapping changed for {mention_id}")

    intro_lines = (ROOT / "02-sources/02-Markdown/01_CHP-1_intro.md").read_text(encoding="utf-8").splitlines()
    master_lines = (ROOT / "02-sources/02-Markdown/01_CHP-1.md").read_text(encoding="utf-8").splitlines()
    require("Passeri, p. 293." in intro_lines[11], "split-source footnote 1 anchor changed")
    require("Hervey, p. 183." in intro_lines[12], "split-source footnote 2 anchor changed")
    require("Passed, p. 293." in master_lines[44], "master OCR footnote 1 anchor changed")
    require("Hervey, p. 183." in master_lines[47], "master OCR footnote 2 anchor changed")

    rows = load_jsonl(STATEMENTS)
    by_id = {row.get("statement_id"): row for row in rows}
    require(len(by_id) == len(rows), "statement IDs are not unique")
    require(EXPECTED_IDS <= set(by_id), "one or more target statement IDs are missing")
    require(len([row for row in rows if row.get("segment_id") == TARGET_SEGMENT]) == 4,
            "target segment statement count changed")
    require(relation_counts(rows) == {
        "statements": 12690,
        "true": 3865,
        "true_bilateral": 3838,
        "true_open": 27,
        "false": 1791,
        "unclassified_bilateral": 4222,
    }, "current statement classification totals changed")

    expected_rows = {
        "st-chp1-l45-46-lhoggidi-context": ("cand-3420", "cand-0198", "contemporary_account_context", 45, 46),
        "st-chp1-l45-passeri-citation": ("cand-1856", None, "citation_source", 45, 45),
        "st-chp1-l46-47-lhoggidi-publication": ("cand-3420", "cand-3401", "publication_history", 46, 47),
        "st-chp1-l48-coke-letter-citation": ("cand-3421", "cand-3085", "letter_attribution", 48, 48),
    }
    selected = []
    for statement_id, (subject, object_, predicate, line_start, line_end) in expected_rows.items():
        row = by_id[statement_id]
        qualifiers = row.get("qualifiers", {})
        require(row.get("segment_id") == TARGET_SEGMENT, f"segment changed for {statement_id}")
        require(row.get("subject_candidate_id") == subject and row.get("object_candidate_id") == object_,
                f"endpoints changed for {statement_id}")
        require(row.get("predicate") == predicate, f"predicate changed for {statement_id}")
        require(qualifiers.get("source_line_start") == line_start and qualifiers.get("source_line_end") == line_end,
                f"source line anchor changed for {statement_id}")
        require("relation_candidate" not in qualifiers, f"already classified: {statement_id}")
        selected.append(row)

    return selected


def classify(rows: list[dict]) -> list[dict]:
    updated = [dict(row) for row in rows]
    by_id = {row["statement_id"]: row for row in updated}

    context = by_id["st-chp1-l45-46-lhoggidi-context"]
    context["qualifiers"] = dict(context["qualifiers"])
    context["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": (
            "Haskell presents L’Hoggidi as a contemporary account of art patronage and life under the Barberini. "
            "The characterization, including ‘enthusiastic’, remains attributed to Haskell."
        ),
    })

    passeri = by_id["st-chp1-l45-passeri-citation"]
    passeri["subject_candidate_id"] = "cand-2962"
    passeri["object_candidate_id"] = "cand-4376"
    passeri["predicate"] = "cites"
    passeri["qualifiers"] = dict(passeri["qualifiers"])
    passeri["qualifiers"].update({
        "claim": "Haskell’s book cites Giambattista Passeri’s Vite de’ Pittori Scultori et Architetti, p. 293.",
        "speaker": "Haskell footnote",
        "text_layer": "bibliographic citation to publication",
        "citation_candidate_id": "cand-1856",
        "citation_publication_candidate_id": "cand-4376",
        "citation_locator": "Passeri, p. 293",
        "citations": [{
            "source_candidate_id": "cand-4376",
            "publication_candidate_id": "cand-4376",
            "locator": "Passeri, p. 293",
        }],
        "mentioned_candidate_ids": ["cand-1856", "cand-4376"],
        "cited_material_not_independently_consulted": True,
        "relation_candidate": True,
        "relation_candidate_note": (
            "The footnote explicitly cites Passeri, p. 293; the bibliography resolves this shorthand to the existing "
            "publication candidate. The cited page was not independently consulted."
        ),
    })

    publication = by_id["st-chp1-l46-47-lhoggidi-publication"]
    publication["qualifiers"] = dict(publication["qualifiers"])
    publication["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": (
            "Haskell reports that L’Hoggidi was first published in Venice in 1627 and often reprinted. "
            "These publication details remain source-attributed and were not independently verified."
        ),
    })

    letter = by_id["st-chp1-l48-coke-letter-citation"]
    letter["qualifiers"] = dict(letter["qualifiers"])
    letter["qualifiers"].update({
        "relation_candidate": True,
        "relation_candidate_note": (
            "The footnote explicitly attributes the dated letter to Mr Coke. The letter remains the subject and "
            "the correspondent the attributed author; the cited Hervey passage was not independently consulted."
        ),
    })

    citation_id = "st-chp1-l48-hervey-citation"
    require(citation_id not in by_id, f"new statement ID already exists: {citation_id}")
    hervey_citation = {
        "statement_id": citation_id,
        "segment_id": TARGET_SEGMENT,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-5615",
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 48,
            "source_line_end": 48,
            "claim": "Haskell’s footnote cites M. F. S. Hervey, p. 183, for the dated Mr Coke letter; the bibliography identifies Hervey’s 1921 book.",
            "speaker": "Haskell footnote",
            "text_layer": "bibliographic citation to publication",
            "footnote_marker": 2,
            "citation_candidate_id": "cand-3422",
            "citation_publication_candidate_id": "cand-5615",
            "citation_locator": "Hervey, p. 183",
            "mentioned_candidate_ids": ["cand-3422", "cand-5615"],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": (
                "The note explicitly cites Hervey, p. 183; the bibliography identifies the existing 1921 publication candidate. "
                "This records a citation pointer only and does not verify the cited page or the letter."
            ),
        },
        "original_quote": "2 Letter from Mr Coke of 8 October 1620—Hervey, p. 183.",
        "origin": "book",
        "source_file": "02-sources/02-Markdown/01_CHP-1.md",
    }
    position = next(i for i, row in enumerate(updated) if row["statement_id"] == "st-chp1-l48-coke-letter-citation")
    updated.insert(position + 1, hervey_citation)
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify first-chapter introduction footnote statements with source-hash preflight.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted statement changes")
    args = parser.parse_args()

    selected = preflight()
    before_rows = load_jsonl(STATEMENTS)
    updated = classify(before_rows)
    print("PREVIEW: chapter 1 introduction footnotes L45–48")
    for row in selected:
        print(f"  existing {row['statement_id']}: {row['predicate']} -> relation_candidate=true")
    print("  existing st-chp1-l45-passeri-citation: citation_source -> cand-2962 cites cand-4376")
    print("  add st-chp1-l48-hervey-citation: cand-2962 cites cand-5615 (Hervey p. 183)")
    print("  no candidate or mention rows change")
    print("  counts before:", json.dumps(relation_counts(before_rows), sort_keys=True))
    print("  counts after: ", json.dumps(relation_counts(updated), sort_keys=True))
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply after reviewing the preview.")
        return

    require(not BACKUP.exists(), f"backup already exists: {BACKUP.relative_to(ROOT)}")
    shutil.copy2(STATEMENTS, BACKUP)
    payload = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in updated) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=STATEMENTS.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, STATEMENTS)
    print(f"APPLIED; backup: {BACKUP.relative_to(ROOT)}")
    print(f"new SHA-256: {sha256(STATEMENTS)}")


if __name__ == "__main__":
    main()
