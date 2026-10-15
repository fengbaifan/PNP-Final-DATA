#!/usr/bin/env python3
"""Classify p.337 notes and align source-only citation treatment with p.332-336."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
SEGMENT = "chp-13:13_CHP-13_intro:l179-251"
BACKUP_SUFFIX = ".bak-s2-ch13-p337-notes-semantic-review-20261014"
EXPECTED_STATEMENTS = "ff799ccd14628ec06e4600d334c6a93089d4a15586235d8994d7801e26830edf"
EXPECTED_SOURCE = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"

DECISIONS = {
    "st-chp13-p337-note1-memmo-1786-p45-citation": "Citation locator for the Lodoli discussion; Memmo's cited page was not independently consulted. Preserve the source pointer without creating a separate historical relation.",
    "st-chp13-p337-note3-inquisitori-record-locator": "This is a precise archival locator for the 1764 incident, but the register was not independently consulted. The note records Haskell's source pointer; the event claims remain in the linked body statements.",
    "st-chp13-p337-note4-novelle-1736-issue-citation": "The issue is cited as a locator for the preceding English-grammar claim; the issue was not independently consulted and no relation to the unidentified grammar is established here.",
    "st-chp13-p337-note5-morazzoni-p116-citation": "Bibliographic locator only; the author is surname-only and the cited page was not independently consulted.",
    "st-chp13-p337-note6-goldoni-author-preface-citation": "The note identifies the cited volume and author-preface pages for Goldoni's preceding comments, but the book and pages were not independently consulted. Retain this source attribution as citation metadata rather than a separate historical relation.",
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
    for statement_id, qualification in DECISIONS.items():
        row = by_id[statement_id]
        q = row["qualifiers"]
        if row.get("segment_id") != SEGMENT or "relation_candidate" in q:
            raise SystemExit(f"unexpected status or source segment: {statement_id}")
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        scoped = "\n".join(source_lines[start - 1 : end])
        if row["original_quote"] not in scoped:
            raise SystemExit(f"source quote mismatch for {statement_id} at L{start}-L{end}")
        q["relation_candidate"] = False
        q["qualification"] = qualification

    # A direct identification of the source of a quotation remains source metadata,
    # consistent with the p.332 source-pointer decisions, rather than a historical edge.
    bettinelli = by_id["st-chp13-p334-n1-bettinelli-letter-citation"]
    bq = bettinelli["qualifiers"]
    if bq.get("relation_candidate") is not True or bettinelli.get("subject_candidate_id") != "cand-2962":
        raise SystemExit("unexpected p.334 note 1 state before citation-policy correction")
    bq["relation_candidate"] = False
    bq["qualification"] = "The note identifies the source of the preceding quotation, but this is an editorial source attribution, not a separate historical relation. Preserve the exact source text and candidate; the edition and quoted passage were not independently checked."
    bq.pop("relation_candidate_note", None)
    bettinelli["subject_candidate_id"] = None

    payload = dump_jsonl(rows)
    print("dry-run preview:")
    for statement_id in DECISIONS:
        print(f"{statement_id}: relation_candidate=false")
    print("st-chp13-p334-n1-bettinelli-letter-citation: relation_candidate=false; source metadata retained without citing-work endpoint")
    print(f"validated 6 exact S0 anchors; statements={len(rows)}; new sha256={hashlib.sha256(payload).hexdigest()}")
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
