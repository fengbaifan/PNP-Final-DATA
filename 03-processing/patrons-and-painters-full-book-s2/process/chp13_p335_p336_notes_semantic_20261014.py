#!/usr/bin/env python3
"""Classify and atomize CHP-13 printed p.335-336 footnote statements."""
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
BODY_SEGMENT = "chp-13:13_CHP-13_intro:l32-39"
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
BACKUP_SUFFIX = ".bak-s2-ch13-p335-p336-notes-semantic-review-20261014"
EXPECTED_STATEMENTS = "a8aa5d9ee6023ceea51cd7d4452f808983835965bd2a6da887ebb614e704dda1"
EXPECTED_SOURCE = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"

FALSE_DECISIONS = {
    "st-chp13-p336-note1-hofer-citation": "Bibliographic locator only; the cited page was not independently consulted and the reference does not establish that the proposed Orlando edition appeared.",
    "st-chp13-p336-note3-morazzoni-locator": "Abbreviated bibliographic pointer only; the cited work and its contents were not independently consulted.",
    "st-chp13-p336-note4-moschini-gradenigo-locators": "The note supplies two bibliographic locators; neither cited page was independently consulted, and no separate historical relation is asserted.",
    "st-chp13-p336-note5-albrizzi-memorie-locator": "This is a short citation locator. The bracketed author form, exact work identity, and cited contents remain unchecked; do not convert the citation into an authorship relation.",
    "st-chp13-p336-note6-print-collection-references": "These are bibliographic pointers to references about the print collection, not independently consulted evidence or a separate historical relation. Keep the collection type unresolved and distinct from Piazzetta's drawings and paintings.",
    "st-chp13-p336-note7-morazzoni-page117-locator": "Citation locator only; the cited page was not independently consulted.",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
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
    target_ids = set(FALSE_DECISIONS) | {
        "st-chp13-p335-note1-augustine-advertisement",
        "st-chp13-p335-note2-book-frontispiece",
        "st-chp13-p335-note3-drawings-owned-by-albrizzi",
        "st-chp13-p335-note3-drawings-formerly-in-england",
        "st-chp13-p335-note3-drawings-now-at-royal-library",
        "st-chp13-p336-note6-brandolese-catalogue-untraced",
        "st-chp13-p336-note8-letter-characterisation",
    }
    target_rows = [row for row in rows if row.get("segment_id") == SEGMENT and row.get("statement_id") in target_ids]
    if len(target_rows) != len(target_ids):
        raise SystemExit(f"expected {len(target_ids)} target statements, found {len(target_rows)}")
    for statement_id in target_ids:
        q = by_id[statement_id].get("qualifiers", {})
        if "relation_candidate" in q:
            raise SystemExit(f"classification already exists: {statement_id}")
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        quote = by_id[statement_id]["original_quote"]
        scoped = "\n".join(source_lines[start - 1 : end])
        if quote not in scoped:
            raise SystemExit(f"source quote mismatch for {statement_id} at L{start}-L{end}")

    def classify(statement_id: str, relation: bool, *, qualification: str | None = None,
                 subject: str | None = None, obj: str | None = None,
                 predicate: str | None = None, claim: str | None = None,
                 speaker: str | None = None, text_layer: str | None = None,
                 mentioned: list[str] | None = None, note: str | None = None) -> None:
        row = by_id[statement_id]
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = relation
        if qualification is not None:
            q["qualification"] = qualification
        if subject is not None:
            row["subject_candidate_id"] = subject
        if obj is not None:
            row["object_candidate_id"] = obj
        if predicate is not None:
            row["predicate"] = predicate
        if claim is not None:
            q["claim"] = claim
        if speaker is not None:
            q["speaker"] = speaker
        if text_layer is not None:
            q["text_layer"] = text_layer
        if mentioned is not None:
            q["mentioned_candidate_ids"] = mentioned
        if note is not None:
            q["relation_candidate_note"] = note

    classify(
        "st-chp13-p335-note1-augustine-advertisement", True,
        qualification="The note reports an advertisement in Novelle for a proposed edition, not a publication known to have appeared.",
        note="The periodical's advertisement and the proposed edition are explicit endpoints; keep the proposal status and do not infer publication.")

    book_row = by_id["st-chp13-p335-note2-book-frontispiece"]
    original_note2 = book_row["original_quote"]
    note2_ids = [
        "st-chp13-p335-note2-book-frontispiece",
        "st-chp13-p335-note2-piazzetta-drew-design",
        "st-chp13-p335-note2-pitteri-engraved-design",
    ]
    classify(
        "st-chp13-p335-note2-book-frontispiece", True,
        subject="cand-10149", obj="cand-9993", predicate="frontispiece_for_devotional_book",
        claim="Haskell's note identifies Religion trampling on Heresy as the design Piazzetta drew for the devotional book La Chiesa di Gesù Cristo vendicata ne' suoi contrasegni e ne' suoi dogmi.",
        qualification="The footnote adds the exact work and book title to the p.335 body statement that Piazzetta made a frontispiece for Recurti's devotional book. The cited Gallo passage and book were not independently consulted.",
        mentioned=["cand-10148", "cand-9993", "cand-1907", "cand-10149"],
        note="The note directly links the named frontispiece design to the devotional book; preserve the work-to-book direction and the cited-source limitation.")

    for statement_id, subject, predicate, claim, mentioned in [
        ("st-chp13-p335-note2-piazzetta-drew-design", "cand-1907", "drew", "Haskell's note says Piazzetta drew Religion trampling on Heresy.", ["cand-1907", "cand-10149", "cand-9993"]),
        ("st-chp13-p335-note2-pitteri-engraved-design", "cand-1948", "engraved", "Haskell's note says Pitteri engraved Religion trampling on Heresy.", ["cand-1948", "cand-10149", "cand-9993"]),
    ]:
        if statement_id in by_id:
            raise SystemExit(f"planned statement already exists: {statement_id}")
        new = copy.deepcopy(book_row)
        new["statement_id"] = statement_id
        new["subject_candidate_id"] = subject
        new["object_candidate_id"] = "cand-10149"
        new["predicate"] = predicate
        q = new["qualifiers"]
        q["claim"] = claim
        q["relation_candidate"] = True
        q["mentioned_candidate_ids"] = mentioned
        q["qualification"] = "Haskell reports this attribution in a footnote citing Gallo, 1948, p.176 n.4; neither the cited passage nor the exact edition was independently checked."
        q["relation_candidate_note"] = "The printed note directly names the person as the maker of the identified work; keep the attribution source-bound pending later verification."
        by_id[statement_id] = new
        rows.append(new)

    for statement_id in [
        "st-chp13-p335-note3-drawings-owned-by-albrizzi",
        "st-chp13-p335-note3-drawings-formerly-in-england",
        "st-chp13-p335-note3-drawings-now-at-royal-library",
    ]:
        classify(statement_id, True, note="The note explicitly states this ownership or location relation for the drawing group; retain the source's undated custody sequence and defer exact institutional identity to alignment.")

    for statement_id, qualification in FALSE_DECISIONS.items():
        classify(statement_id, False, qualification=qualification)

    classify(
        "st-chp13-p336-note6-brandolese-catalogue-untraced", True,
        note="Haskell directly attributes making the catalogue to Pietro Brandolese. Its untraced status, unknown title, date, and location remain qualifiers; do not infer that the catalogue survives.")
    classify(
        "st-chp13-p336-note8-letter-characterisation", True,
        subject="cand-1844", obj="cand-0025", predicate="described_as_complete_opposites_by_gherardi",
        claim="As quoted by Haskell, Gherardi's letter calls Pasquali the opposite of Albrizzi and contrasts their caution, support, and prospects in their affairs.",
        speaker="P. E. Gherardi, letter to L. A. Muratori, 12 July 1749 (quoted by Haskell)",
        text_layer="archival quotation reproduced in footnote",
        qualification="This Italian quotation supports the p.336 body statement that Gherardi described the two publishers as opposites. Its characterizations remain attributed to Gherardi, not verified biography; the letter was not independently consulted.",
        mentioned=["cand-1155", "cand-1844", "cand-0025", "cand-1717", "cand-10008"],
        note="The quotation explicitly contrasts Pasquali with Albrizzi. Keep the comparison directed between the two named publishers and retain Gherardi as speaker; the trait judgments remain attributed.")

    # Keep the already-linked p.335 body statements connected to all three note-2 assertions.
    for statement_id in ["st-chp13-p335-piazzetta-frontispiece-before-albrizzi-enterprise", "st-chp13-p335-recurti-published-devotional-book"]:
        body = by_id[statement_id]
        q = body["qualifiers"]
        q["footnote_note_statement_ids"] = note2_ids
        for ref in q.get("footnote_refs", []):
            if ref.get("footnote_line_range") == "L193":
                ref["footnote_note_statement_ids"] = note2_ids

    if len({row["statement_id"] for row in rows}) != len(rows):
        raise SystemExit("statement_id collision after planned additions")
    payload = dump_jsonl(rows)
    print("dry-run preview:")
    print(f"classifications: {len(target_ids)} existing statements; new atomized relation rows: 2")
    for statement_id in sorted(target_ids):
        row = by_id[statement_id]
        q = row["qualifiers"]
        print(f"{statement_id}: relation_candidate={str(q['relation_candidate']).lower()}, subject={row.get('subject_candidate_id')}, object={row.get('object_candidate_id')}")
    print(f"p.335 note 2 split into work/book, Piazzetta/work, and Pitteri/work relations; body links updated")
    print(f"validated exact S0 anchors; statements={len(rows)}; new sha256={hashlib.sha256(payload).hexdigest()}")
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
