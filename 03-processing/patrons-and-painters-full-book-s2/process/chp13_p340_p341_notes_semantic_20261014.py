#!/usr/bin/env python3
"""Classify CHP-13 p.340-341 notes, separating source locators from reported relations."""
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
BACKUP_SUFFIX = ".bak-s2-ch13-p340-p341-notes-semantic-review-20261014"
EXPECTED_STATEMENTS = "56ede79d423554331ad95bf5c7bcdaadc92c8f9fb0a3c65d01de2d8feda35b7f"
EXPECTED_SOURCE = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"

DECISIONS = {
    "st-chp13-p340-note1-morelli-pinelli-dispersal": (False, "This is Haskell's citation locator after the reported dispersal of Pinelli's collections; Morelli's cited page was not independently consulted."),
    "st-chp13-p340-note2-remondini-sources": (False, "The note lists Berengo and an exhibition catalogue as citations for the Remondini discussion; neither source was independently consulted, so preserve them as bibliographic pointers."),
    "st-chp13-p340-note4-moschini-wagner-locator": (False, "Citation locator only; the cited page and publication title were not independently consulted."),
    "st-chp13-p340-note5-gallo-moschini-viero-locators": (False, "The note gives Gallo and Moschini page locators for the Viero discussion. The cited pages were not independently consulted; retain the reused Gallo candidate without converting the references into separate facts."),
    "st-chp13-p340-note6-gallo-furnaletto-locators": (False, "The two Gallo page locators are citations for the Furnaletto account, not independently consulted evidence. Preserve the existing shared Gallo reference candidate."),
    "st-chp13-p341-notes-note1-lorenzetti-borroni-references": (False, "The note supplies abbreviated references only; Borroni's title and date are absent and neither cited work was independently consulted."),
    "st-chp13-p341-notes-note3-mariette-abecedario-account-of-zanetti": (True, "The print reads Abecedario; S0 OCR reads Ahecedario. The work and cited page were not independently consulted. This statement records Mariette's account of Zanetti; the will's pastel bequest is handled separately."),
    "st-chp13-p341-notes-note4-volume-locator-at-biblioteca-marciana": (True, "Haskell's printed locator associates the cited manuscript volume with Biblioteca Marciana and gives its shelfmark. This is the book's reported repository association, not independently verified current custody."),
    "st-chp13-p341-notes-note4-zanetti-indexed-and-summarized-volume-letters": (True, "The note explicitly says Zanetti indexed and summarized the letters at the beginning of the described volume; the codex was not independently inspected."),
    "st-chp13-p341-notes-note4-memorie-mentions-castiglione-not-poussin": (True, "This preserves Haskell's comparison between the cited receipt and Zanetti's Memorie; it does not infer why the Poussin is absent, and neither document was independently consulted."),
    "st-chp13-p341-notes-note4-memorie-describes-copper-pastoral-by-epithet": (True, "The quotation attributes an untitled copper pastoral to 'lo Spagnolo di Bologna'. Do not equate that epithet with Crespi or identify the work with the body passage's pastoral."),
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
    for statement_id, (relation, qualification) in DECISIONS.items():
        row = by_id[statement_id]
        q = row["qualifiers"]
        if row.get("segment_id") != SEGMENT or "relation_candidate" in q:
            raise SystemExit(f"unexpected status or source segment: {statement_id}")
        start, end = int(q["source_line_start"]), int(q["source_line_end"])
        if row["original_quote"] not in "\n".join(source_lines[start - 1 : end]):
            raise SystemExit(f"source quote mismatch for {statement_id} at L{start}-L{end}")
        q["relation_candidate"] = relation
        q["qualification"] = qualification
        if relation:
            q["relation_candidate_note"] = qualification

    payload = dump_jsonl(rows)
    print("dry-run preview:")
    for statement_id, (relation, _) in DECISIONS.items():
        print(f"{statement_id}: relation_candidate={str(relation).lower()}")
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
