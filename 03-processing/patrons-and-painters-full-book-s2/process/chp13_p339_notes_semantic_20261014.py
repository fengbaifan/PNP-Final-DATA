#!/usr/bin/env python3
"""Classify the remaining source-locator statements in CHP-13 p.339 notes."""
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
BACKUP_SUFFIX = ".bak-s2-ch13-p339-notes-semantic-review-20261014"
EXPECTED_STATEMENTS = "05290b545c790bb5bf9fa84fb3727a5ad16d188efaa4ada0bfffa50f1d85df10"
EXPECTED_SOURCE = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"

DECISIONS = {
    "st-chp13-p339-note1-inquisitori-records": "The two dated Inquisitori di Stato entries are precise archival locators, but neither record was consulted. Preserve them as source pointers; the body statements record Haskell's account of Zatta's episodes.",
    "st-chp13-p339-note3-zatta-letter-page23": "This is a page locator in the 1761 Zatta letter identified at p.338 note 2. The letter was not consulted and the note adds no separately verified historical relation.",
    "st-chp13-p339-note4-zatta-1790-catalogue": "The note cites a 1790 catalogue but does not independently establish its contents or the business practices described in its title. Preserve the catalogue and imprint as source metadata; the cited item was not consulted.",
    "st-chp13-p339-note5-da-venezia-1934": "Bibliographic locator only; the cited pages were not independently consulted and the author is not expanded beyond the printed citation.",
    "st-chp13-p339-note6-pinelli-catalogues": "These are bibliographic pointers printed after Haskell's approximate picture-count statement. Neither source was independently consulted; preserve the references without treating them as confirmation of ownership or count.",
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
        if row["original_quote"] not in "\n".join(source_lines[start - 1 : end]):
            raise SystemExit(f"source quote mismatch for {statement_id} at L{start}-L{end}")
        q["relation_candidate"] = False
        q["qualification"] = qualification

    payload = dump_jsonl(rows)
    print("dry-run preview:")
    for statement_id in DECISIONS:
        print(f"{statement_id}: relation_candidate=false")
    print(f"validated {len(DECISIONS)} exact S0 anchors; statements={len(rows)}; new sha256={hashlib.sha256(payload).hexdigest()}")
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
