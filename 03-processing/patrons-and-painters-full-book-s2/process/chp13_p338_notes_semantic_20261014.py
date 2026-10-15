#!/usr/bin/env python3
"""Classify p.338 notes and atomize Zatta's cited letter endpoints."""
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
BACKUP_SUFFIX = ".bak-s2-ch13-p338-notes-semantic-review-20261014"
EXPECTED_STATEMENTS = "924f6c033d0552a75b07ad58c699cefa45984518d023a884799ebb1c94eabadb"
EXPECTED_SOURCE = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"


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
    target_ids = [
        "st-chp13-p338-note1-goldoni-volume2-page1-citation",
        "st-chp13-p338-note2-zatta-letter-to-unnamed-duke",
        "st-chp13-p338-note2-zatta-justificatory-letter",
    ]
    for statement_id in target_ids:
        row = by_id[statement_id]
        q = row["qualifiers"]
        if row.get("segment_id") != SEGMENT or "relation_candidate" in q:
            raise SystemExit(f"unexpected status or source segment: {statement_id}")
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        if row["original_quote"] not in "\n".join(source_lines[start - 1 : end]):
            raise SystemExit(f"source quote mismatch for {statement_id} at L{start}-L{end}")

    note1 = by_id[target_ids[0]]
    note1["qualifiers"]["relation_candidate"] = False
    note1["qualifiers"]["qualification"] = "This is a bibliographic locator for Goldoni's frontispiece proposal. The cited volume and page were not independently consulted; preserve it as source metadata rather than a separate historical relation. S0 reads 'Vol. H'; the scan reads 'Vol. II' and the existing S2 OCR correction records this."

    original_letter = copy.deepcopy(by_id[target_ids[1]])
    letter = by_id[target_ids[1]]
    lq = letter["qualifiers"]
    letter["subject_candidate_id"] = "cand-10178"
    letter["object_candidate_id"] = None
    letter["predicate"] = "addressed_to_unidentified_duke"
    lq["claim"] = "Haskell's note gives the incomplete title of a 1761 letter addressed to an unnamed Duke and prints its imprint as Fiorenza, corrected in brackets to Venice."
    lq["speaker"] = "Haskell, printed footnote"
    lq["text_layer"] = "source-title attribution"
    lq["relation_candidate"] = True
    lq["qualification"] = "The title ends with an ellipsis and identifies the recipient only as a Duke. Preserve Haskell's bracketed venue correction; the cited letter was not independently consulted."
    lq["open_endpoint_reason"] = "The recipient is unnamed in the title; no identity beyond 'Duke' is supplied."
    lq["relation_candidate_note"] = "The cited title explicitly presents the letter as addressed to a Duke; retain the letter as subject and leave the recipient endpoint open."
    lq["mentioned_candidate_ids"] = ["cand-10178", "cand-2865", "cand-3401"]

    author_id = "st-chp13-p338-note2-zatta-authored-letter"
    if author_id in by_id:
        raise SystemExit(f"planned statement already exists: {author_id}")
    author = copy.deepcopy(original_letter)
    author["statement_id"] = author_id
    author["subject_candidate_id"] = "cand-2865"
    author["object_candidate_id"] = "cand-10178"
    author["predicate"] = "authored_letter"
    aq = author["qualifiers"]
    aq["claim"] = "The incomplete title names Antonio Zatta as the author of the 1761 letter to an unnamed Duke."
    aq["speaker"] = "Haskell, printed footnote"
    aq["text_layer"] = "source-title attribution"
    aq["relation_candidate"] = True
    aq["qualification"] = "The title attributes the letter to Antonio Zatta. The recipient and exact publication details remain limited to Haskell's printed citation; the letter was not independently consulted."
    aq.pop("open_endpoint_reason", None)
    aq["relation_candidate_note"] = "The printed title explicitly attributes the letter to Zatta; preserve that attribution without expanding his identity or the recipient."
    aq["mentioned_candidate_ids"] = ["cand-2865", "cand-10178"]
    by_id[author_id] = author
    rows.append(author)

    justificatory_id = target_ids[2]
    justificatory = by_id[justificatory_id]
    jq = justificatory["qualifiers"]
    justificatory["predicate"] = "authored_justificatory_letter_published_venice_1761"
    jq["claim"] = "The title identifies Lettera Giustificativa as Antonio Zatta's letter, published in Venice in 1761."
    jq["speaker"] = "Haskell, printed footnote"
    jq["text_layer"] = "source-title and imprint attribution"
    jq["relation_candidate"] = True
    jq["qualification"] = "The author, title, place, and year are reported by Haskell's printed note; the work was not independently consulted."
    jq["relation_candidate_note"] = "The printed title attributes the justificatory letter to Zatta; preserve Venice and 1761 as cited imprint details."

    body_id = "st-chp13-p338-zatta-combatively-supported-jesuits"
    body = by_id[body_id]
    bq = body["qualifiers"]
    for field in ["footnote_note_statement_ids"]:
        refs = bq.get(field, [])
        if author_id not in refs:
            refs.append(author_id)
        bq[field] = refs
    for ref in bq.get("footnote_refs", []):
        if ref.get("footnote_marker") == "2":
            refs = ref.setdefault("footnote_note_statement_ids", [])
            if author_id not in refs:
                refs.append(author_id)

    if len({row["statement_id"] for row in rows}) != len(rows):
        raise SystemExit("statement_id collision after planned addition")
    payload = dump_jsonl(rows)
    print("dry-run preview:")
    print("p.338 note 1: relation_candidate=false (citation locator)")
    print("p.338 note 2: Zatta letter addressed-to relation=true with open recipient; Zatta-authorship relation=true")
    print("p.338 note 2: justificatory letter authored by Zatta relation=true")
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
