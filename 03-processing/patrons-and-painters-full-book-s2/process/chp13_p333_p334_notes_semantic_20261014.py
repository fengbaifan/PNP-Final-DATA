#!/usr/bin/env python3
"""Classify the p.333-334 footnote statements in the merged CHP-13 notes segment."""
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
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
BACKUP_SUFFIX = ".bak-s2-ch13-p333-p334-notes-semantic-review-20261014"
EXPECTED_STATEMENTS = "84e6040f06c52b70e142d3496cef51e97e763e2d151270253846859d7d149b1d"
EXPECTED_SOURCE = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"

DECISIONS = {
    "st-chp13-p333-n1-roberti-citation": {
        "relation": False,
        "qualification": "This is a bibliographic locator for the preceding instructions attributed to Caterina Barbarigo, not a separate historical relation. The article is locally identified from the book bibliography but was not independently consulted.",
    },
    "st-chp13-p334-n1-bettinelli-letter-citation": {
        "relation": True,
        "subject": "cand-2962",
        "note": "The note explicitly identifies the preceding quotation as a specific source text, Lettere inglesi, lettera seconda. Record the source-book citation candidate while retaining that the edition and text were not independently checked.",
    },
    "st-chp13-p334-n2-morazzoni-citation": {
        "relation": False,
        "qualification": "Citation locator only; the cited page was not independently consulted and is kept distinct from other Morazzoni references.",
    },
    "st-chp13-p334-n3-bossuet-eighth-volume-1755": {
        "relation": True,
        "note": "The note directly reports a dedication of the eighth Bossuet volume in 1755, so the work-to-dedicatee link remains an S2 relation candidate. The recipient is unnamed here; preserve the open endpoint and do not promote the note's ambiguous inference about Albrizzi's son.",
        "open_endpoint_reason": "The dedication's recipient is not named in this note. The preceding 'This' is ambiguous, so the note does not independently establish the son's schooling or identify a dedicatee.",
    },
    "st-chp13-p334-n4-battagia-citation": {
        "relation": False,
        "qualification": "Citation locator only; the publication title, edition, author's full identity, and cited contents are unresolved.",
    },
    "st-chp13-p334-n5-novelle-publication-from-1729": {
        "relation": False,
        "qualification": "This is a publication-date statement about the periodical, not a relation between distinct entities. Retain the source's 'as from' wording; it does not establish an exact first issue date. The OCR footnote label 6 is corrected to printed note 5 in S2 only.",
    },
    "st-chp13-p334-n6-hazard-citation": {
        "relation": False,
        "qualification": "Citation locator only; the cited pages were not independently consulted and the reference is kept distinct from the other Bossuet-related source pointers.",
    },
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
    target_rows = [row for row in rows if row.get("segment_id") == SEGMENT and row.get("statement_id") in DECISIONS]
    if len(target_rows) != len(DECISIONS):
        raise SystemExit(f"expected {len(DECISIONS)} target statements, found {len(target_rows)}")

    for statement_id, decision in DECISIONS.items():
        row = by_id[statement_id]
        q = row.setdefault("qualifiers", {})
        if "relation_candidate" in q:
            raise SystemExit(f"classification already exists: {statement_id}")
        start = int(q["source_line_start"])
        end = int(q["source_line_end"])
        quote = row["original_quote"]
        scoped = "\n".join(source_lines[start - 1 : end])
        if quote not in scoped:
            raise SystemExit(f"source quote mismatch for {statement_id} at L{start}-L{end}: {quote!r}")
        q["relation_candidate"] = decision["relation"]
        if "qualification" in decision:
            q["qualification"] = decision["qualification"]
        if "subject" in decision:
            row["subject_candidate_id"] = decision["subject"]
        if "note" in decision:
            q["relation_candidate_note"] = decision["note"]
        if "open_endpoint_reason" in decision:
            q["open_endpoint_reason"] = decision["open_endpoint_reason"]

    payload = dump_jsonl(rows)
    print("dry-run preview:")
    for statement_id, decision in DECISIONS.items():
        print(f"{statement_id}: relation_candidate={str(decision['relation']).lower()}" +
              (f", subject={decision['subject']}" if "subject" in decision else "") +
              (", open dedicatee endpoint" if "open_endpoint_reason" in decision else ""))
    print(f"validated {len(DECISIONS)} exact S0 quotes; statements sha256 {hashlib.sha256(payload).hexdigest()}")
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
