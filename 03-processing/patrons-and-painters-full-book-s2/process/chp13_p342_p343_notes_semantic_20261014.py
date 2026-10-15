#!/usr/bin/env python3
"""Classify CHP-13 p.342-343 notes and atomize the Gori letter locator."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
SEGMENT = "chp-13:13_CHP-13_intro:l179-251"
BACKUP_SUFFIX = ".bak-s2-ch13-p342-p343-notes-semantic-review-20261014"
EXPECTED_STATEMENTS = "a898499d383f79ae2369ba3da387210fc70e40f438d236a9adbe5e2480d92333"
EXPECTED_SOURCE = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"

CLASSIFICATIONS = {
    "st-chp13-p342-notes-note1-tessin-seven-letter-dates": True,
    "st-chp13-p342-notes-note2-painter-unidentified": False,
    "st-chp13-p342-notes-note3-tessin-letter-about-tiepolo": True,
    "st-chp13-p342-notes-note4-third-letter-cross-reference": False,
    "st-chp13-p342-notes-note6-letter-to-gori-locator": True,
    "st-chp13-p342-notes-note7-zanetti-italian-exclusion-quote": True,
    "st-chp13-p343-notes-note1-lorenzetti-page122": False,
    "st-chp13-p343-notes-note2-varie-pitture-preface-source": False,
    "st-chp13-p343-notes-note4-lorenzetti-possible-1743-date": True,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def add_note_reference(row: dict, old_id: str, new_id: str) -> None:
    qualifiers = row["qualifiers"]
    note_ids = qualifiers.get("footnote_note_statement_ids", [])
    if old_id not in note_ids:
        raise SystemExit(f"body statement is missing old note reference: {row['statement_id']}")
    if new_id not in note_ids:
        note_ids.append(new_id)
    refs = qualifiers.get("footnote_refs", [])
    matched = False
    for ref in refs:
        ids = ref.get("footnote_note_statement_ids", [])
        if old_id in ids:
            matched = True
            if new_id not in ids:
                ids.append(new_id)
    if not matched:
        raise SystemExit(f"body statement has no matching nested footnote ref: {row['statement_id']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validation; default is dry-run")
    args = parser.parse_args()

    for path, expected in ((STATEMENTS, EXPECTED_STATEMENTS), (SOURCE, EXPECTED_SOURCE)):
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"precondition failed: {path.relative_to(ROOT)} sha256={actual}, expected={expected}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    rows = load_jsonl(STATEMENTS)
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("statement_id is not unique before apply")
    for statement_id in CLASSIFICATIONS:
        row = by_id.get(statement_id)
        if row is None or row.get("segment_id") != SEGMENT:
            raise SystemExit(f"missing statement or unexpected source segment: {statement_id}")
        qualifiers = row["qualifiers"]
        if "relation_candidate" in qualifiers:
            raise SystemExit(f"statement is already classified: {statement_id}")
        start, end = int(qualifiers["source_line_start"]), int(qualifiers["source_line_end"])
        if row["original_quote"] not in "\n".join(source_lines[start - 1 : end]):
            raise SystemExit(f"source quote mismatch for {statement_id} at L{start}-L{end}")

    # Add the nine S2 semantic classifications without promoting citations or
    # cross-references to historical relations.
    for statement_id, relation in CLASSIFICATIONS.items():
        by_id[statement_id]["qualifiers"]["relation_candidate"] = relation

    seven = by_id["st-chp13-p342-notes-note1-tessin-seven-letter-dates"]
    seven["qualifiers"]["relation_candidate_note"] = (
        "Haskell's cited Marciana volume is reported to contain this group of seven Tessin letters; "
        "retain the dates and place names as printed, including the 1743 (sic—but 1748) correction. "
        "The manuscript was not consulted."
    )

    unidentified = by_id["st-chp13-p342-notes-note2-painter-unidentified"]
    unidentified["qualifiers"]["qualification"] = (
        "This is a negative identity constraint, not a named historical relation. Keep the protégé's "
        "identity unresolved; do not infer it from the painter's later death or another passage."
    )

    offer = by_id["st-chp13-p342-notes-note3-tessin-letter-about-tiepolo"]
    offer.update({
        "subject_candidate_id": "cand-2554",
        "object_candidate_id": "cand-2569",
        "predicate": "offered_room_and_board_to_tiepolo_beyond_kings_pension",
    })
    offer_q = offer["qualifiers"]
    offer_q.update({
        "claim": "In the third letter, Tessin says that price is the remaining obstacle to Tiepolo's possible acceptance, expects Tiepolo would not regret accepting, and offers him room and board in Tessin's house in addition to the King's pension.",
        "speaker": "Count Carl Gustav Tessin, quoted by Haskell",
        "qualification": "French quotation transcribed by Haskell; preserve its wording and old spelling. This records an offer and anticipated terms, not Tiepolo's acceptance or payment of the King's pension. The letter was not independently consulted.",
        "relation_candidate_note": "The third letter reports Tessin's offer directly to Tiepolo; it does not establish acceptance. The letter was not independently consulted.",
    })

    crossref = by_id["st-chp13-p342-notes-note4-third-letter-cross-reference"]
    crossref["qualifiers"]["qualification"] = (
        "This preserves Haskell's source locator and chapter cross-reference; it is not a separate "
        "historical relation or independent evidence."
    )

    old_id = "st-chp13-p342-notes-note6-letter-to-gori-locator"
    new_id = "st-chp13-p342-notes-note6-letter-located-in-marucelliana"
    if new_id in by_id:
        raise SystemExit(f"new statement_id already exists: {new_id}")
    letter_note = by_id[old_id]
    linked_body_ids = list(letter_note["qualifiers"].get("linked_body_statement_ids", []))
    if len(linked_body_ids) != 6:
        raise SystemExit(f"unexpected body links on note 6: {len(linked_body_ids)}")
    letter_note.update({"object_candidate_id": "cand-1214", "predicate": "addressed_to"})
    letter_note["qualifiers"].update({
        "claim": "Haskell's p.342 note identifies the cited letter, dated 22 December 1752, as addressed to A. F. Gori.",
        "qualification": "The recipient and date are transcribed from Haskell's printed locator; the letter was not independently consulted.",
        "mentioned_candidate_ids": ["cand-10210", "cand-1214"],
        "relation_candidate_note": "The printed locator explicitly identifies A. F. Gori as the letter's recipient; the letter was not independently consulted.",
        "citations": [{"source_candidate_id": "cand-10210", "recipient_candidate_id": "cand-1214", "date": "1752-12-22"}],
    })
    repository_note = copy.deepcopy(letter_note)
    repository_note.update({
        "statement_id": new_id,
        "object_candidate_id": "cand-9493",
        "predicate": "cited_repository_and_shelfmark",
    })
    repository_note["qualifiers"].update({
        "claim": "Haskell's p.342 note locates the cited 22 December 1752 letter to A. F. Gori at Biblioteca Marucelliana, Florence, MSS. B. VIII, 13, page 400.",
        "qualification": "Repository, city, and shelfmark are transcribed from Haskell's printed note; the letter and catalogue were not independently consulted, so this is not a verified statement of current custody.",
        "mentioned_candidate_ids": ["cand-10210", "cand-9493", "cand-3397"],
        "relation_candidate_note": "Haskell's printed locator associates the cited letter with Biblioteca Marucelliana and gives its shelfmark; current custody was not independently verified.",
        "citations": [{"source_candidate_id": "cand-10210", "repository_candidate_id": "cand-9493", "shelfmark_as_printed": "MSS. B. VIII, 13, p. 400", "date": "1752-12-22"}],
    })
    for body_id in linked_body_ids:
        add_note_reference(by_id[body_id], old_id, new_id)
    insert_at = rows.index(letter_note) + 1
    rows.insert(insert_at, repository_note)
    by_id[new_id] = repository_note

    zanetti_quote = by_id["st-chp13-p342-notes-note7-zanetti-italian-exclusion-quote"]
    zanetti_quote.update({
        "subject_candidate_id": "cand-2838",
        "object_candidate_id": "cand-10090",
        "predicate": "described_annibale_cup_carved_in_underdish_as_bacchanal",
    })
    zanetti_quote["qualifiers"].update({
        "claim": "Zanetti's 1752 wording describes the cup of Annibale as carved in a sottocoppa and representing a Bacchanal.",
        "speaker": "A. M. Zanetti the elder, quoted by Haskell",
        "qualification": "Preserve the Italian quotation as printed. Haskell cites Kurz, 1955, pp. 282–287, but those pages were not consulted; do not extend this note's support to the Giulio Romano prints that follow in the open p.342 quotation.",
        "relation_candidate_note": "This is Zanetti's explicit description of the Annibale dish in the quoted 1752 statement; Kurz's cited pages were not independently consulted.",
    })

    for statement_id in (
        "st-chp13-p343-notes-note1-lorenzetti-page122",
        "st-chp13-p343-notes-note2-varie-pitture-preface-source",
    ):
        by_id[statement_id]["qualifiers"]["qualification"] += " This is a source locator, not a historical relation; the cited work was not independently consulted."

    possible_date = by_id["st-chp13-p343-notes-note4-lorenzetti-possible-1743-date"]
    possible_date.update({
        "subject_candidate_id": "cand-2838",
        "object_candidate_id": "cand-10103",
        "predicate": "may_have_published_tiepolo_etchings_as_early_as_1743",
    })
    possible_date["qualifiers"].update({
        "claim": "Haskell, citing Lorenzetti (1917, p. 55), says Zanetti may well have published the Tiepolo etchings as early as 1743.",
        "speaker": "Haskell, citing Lorenzetti",
        "qualification": "Preserve 'may well' and 'as early as': 1743 is a qualified possibility attributed to the cited source, not a verified publication date. Lorenzetti's page was not consulted.",
        "relation_candidate_note": "This is Haskell's expressly tentative statement about Zanetti and the Tiepolo etchings; it does not establish a verified publication date.",
    })

    if len({row["statement_id"] for row in rows}) != len(rows):
        raise SystemExit("statement_id is not unique after planned changes")
    payload = dump_jsonl(rows)
    print("dry-run preview:")
    for statement_id, relation in CLASSIFICATIONS.items():
        print(f"{statement_id}: relation_candidate={str(relation).lower()}")
    print(f"{old_id}: atomized into recipient and repository statements")
    print(f"validated 9 exact S0 anchors and 6 linked body statements; statements={len(rows)}; new sha256={hashlib.sha256(payload).hexdigest()}")
    if not args.apply:
        return

    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(STATEMENTS, backup)
    STATEMENTS.write_bytes(payload)
    print(f"applied; recovery copy: {backup.relative_to(ROOT)}; new sha256={sha(STATEMENTS)}")


if __name__ == "__main__":
    main()
