from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
IMAGE = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "p332_page_review_20261014.png"
SEGMENT = "chp-13:13_CHP-13_intro:l179-251"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-ch13-p332-notes-semantics-20261014")
EXPECTED = {
    TABLE.name: "759f4ea105ebc036d2ca2130d85511cf95615bb3be27e224afcef65df78bdee3",
    SOURCE.name: "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8",
    PDF.name: "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc",
    IMAGE.name: "9a28de10454d9ef07041bd00c9c49ebf55355803787c193b0295f3f81b812dbf",
}

TARGETS = {
    "st-chp13-p332-n1-brown-survey-citation": False,
    "st-chp13-p332-n2-berengo-citation": False,
    "st-chp13-p332-n3-goethe-citation": False,
    "st-chp13-p332-n4-berengo-citation": False,
    "st-chp13-p332-n4-morazzoni-citation": False,
    "st-chp13-p332-n4-gallo-citation": False,
    "st-chp13-p332-n4-marin-counterview": True,
    "st-chp13-p332-n5-morazzoni-citation": False,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify p.332 footnotes and preserve Marin's open claim challenge")
    parser.add_argument("--apply", action="store_true", help="write after exact source, row-set, and quote checks")
    args = parser.parse_args()

    actual = {p.name: sha(p) for p in (TABLE, SOURCE, PDF, IMAGE)}
    if actual != EXPECTED:
        raise SystemExit(f"preflight hash mismatch; no writes made: {actual}")

    rows = [json.loads(line) for line in TABLE.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement_id in table")
    target = [
        row for row in rows
        if row.get("segment_id") == SEGMENT and row.get("qualifiers", {}).get("printed_page") == 332
    ]
    if {row["statement_id"] for row in target} != set(TARGETS):
        raise SystemExit("p.332 footnote statement set changed")
    if {row["statement_id"] for row in target if "relation_candidate" in row.get("qualifiers", {})}:
        raise SystemExit("one or more p.332 footnotes already classified")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    for row in target:
        q = row["qualifiers"]
        start, end = q["source_line_start"], q["source_line_end"]
        block = "\n".join(source_lines[start - 1:end])
        if not row.get("original_quote") or row["original_quote"] not in block:
            raise SystemExit(f"source quote mismatch: {row['statement_id']}")

    marin = by_id["st-chp13-p332-n4-marin-counterview"]
    q = marin["qualifiers"]
    if marin.get("subject_candidate_id") is not None or marin.get("object_candidate_id") != "cand-10139":
        raise SystemExit("Marin counterview endpoints changed")
    if q.get("linked_body_statement_ids") != ["st-chp13-p332-government-copyright-encouragement"]:
        raise SystemExit("Marin footnote body link changed")

    for sid, is_relation in TARGETS.items():
        row = by_id[sid]
        row["qualifiers"]["relation_candidate"] = is_relation
        if is_relation:
            row["qualifiers"]["qualification"] = (
                "Haskell reports that the cited Marin volume challenges the generally optimistic view of eighteenth-century Venetian engraving. "
                "The challenged view is not tied to a specific author or claim in this note, so the claim endpoint remains open."
            )
        else:
            row["qualifiers"]["qualification"] = (
                "This is a bibliographic locator or source pointer, not a separate historical relation. "
                "The cited work/page was not independently consulted."
            )

    marin["subject_candidate_id"] = "cand-10139"
    marin["predicate"] = "challenges_claim"
    marin["object_candidate_id"] = None
    marin["qualifiers"].pop("linked_body_statement_ids", None)

    counts = {
        "true": sum(r["qualifiers"].get("relation_candidate") is True for r in target),
        "false": sum(r["qualifiers"].get("relation_candidate") is False for r in target),
        "unset": sum("relation_candidate" not in r["qualifiers"] for r in target),
    }
    if counts != {"true": 1, "false": 7, "unset": 0}:
        raise SystemExit(f"unexpected p.332 note classification: {counts}")

    output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
    print("p.332 footnotes 1-5: 8 statements, 1 claim-level relation candidate, 7 citation locators, 0 unset.")
    print("Marin: archive locator -> challenges_claim; target claim stays open; removed unsupported link to the copyright-law statement.")
    print("planned table sha256:", hashlib.sha256(output).hexdigest())
    if not args.apply:
        print("preview only; no files written")
        return 0
    if BACKUP.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    TABLE.write_bytes(output)
    print("applied; backup:", BACKUP.name)
    print("written table sha256:", sha(TABLE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
