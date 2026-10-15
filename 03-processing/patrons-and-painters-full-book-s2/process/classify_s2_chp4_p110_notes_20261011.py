from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
PDF = ROOT / "02-sources/01-book/CHP-4.pdf"
PAGE = ROOT / "03-processing/patrons-and-painters-full-book-s2/process/p110_body_notes_page_review_20261011.png"
SEGMENTS = TABLES / "segments.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"

EXPECTED = {
    SOURCE: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    PDF: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
    PAGE: "b31c28d446373be682470241a1f31e1c4d4c6a1305056b7869c04e22b5c80542",
    STATEMENTS: "5243728dd94be3570cb59c18ab181ab9729a8be4a194934e5951c96c7c805de3",
    CANDIDATES: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    MENTIONS: "0251842ac93313725448baf44c7878ef71f74f5dfd31cdad8df19a5f84e3dca9",
    COVERAGE: "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
HASKELL_BOOK = "cand-2962"
OLD_IDS = {
    "st-chp4-sec-ii-notes-p110-fn1-bartsch": {
        "subject": "cand-5608", "object": "cand-5609",
        "predicate": "cites_bartsch_volume_twenty_page_216_for_testa_print",
        "author": "cand-5608", "publication": "cand-5609", "locator": "Bartsch, volume XX, p. 216",
        "claim": "Haskell cites Adam Bartsch, volume XX, page 216, for the preceding print discussion.",
        "expected_quote": "1 Bartsch, XX, p. 216.", "quote": "1 Bartsch, XX, p. 216.", "line": 275,
    },
    "st-chp4-sec-ii-notes-p110-fn2-zeri-mitchell-voss": {
        "subject": "cand-4878", "object": "cand-5871",
        "predicate": "cites_zeri_mitchell_and_voss_on_related_flight_into_egypt_representations",
        "author": "cand-4878", "publication": "cand-5871", "locator": "Zeri, 1954, p. 131",
        "claim": "Haskell cites Federico Zeri, 1954, page 131, for other representations of The Flight into Egypt.",
        "expected_quote": "2 Zeri, 1954, p. 131. For other representations of The Flight into Egypt in seventeenth-century art see articles by Mitchell, 1938, and Voss, 1957, pp. 25-61.",
        "quote": "2 Zeri, 1954, p. 131.", "line": 276,
    },
}
SPLITS = [
    {
        "statement_id": "st-chp4-sec-ii-notes-p110-fn2-mitchell-citation",
        "author": "cand-5872", "publication": "cand-5873", "locator": "Mitchell, 1938",
        "claim": "Haskell cites Mitchell's 1938 article for other representations of The Flight into Egypt.",
        "quote": "For other representations of The Flight into Egypt in seventeenth-century art see articles by Mitchell, 1938",
    },
    {
        "statement_id": "st-chp4-sec-ii-notes-p110-fn2-voss-citation",
        "author": "cand-5874", "publication": "cand-5875", "locator": "Voss, 1957, pp. 25-61",
        "claim": "Haskell cites Voss's 1957 article, pages 25-61, for other representations of The Flight into Egypt.",
        "quote": "For other representations of The Flight into Egypt in seventeenth-century art see articles by Mitchell, 1938, and Voss, 1957, pp. 25-61.",
    },
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_atomic(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def citation_fields(row: dict, author: str, publication: str, locator: str, claim: str) -> None:
    row["subject_candidate_id"] = HASKELL_BOOK
    row["object_candidate_id"] = publication
    row["predicate"] = "cites"
    q = row["qualifiers"]
    q["claim"] = claim
    q["relation_candidate"] = True
    q["relation_candidate_note"] = "Haskell's bibliographic citation; the cited source has not been independently consulted."
    q["mentioned_candidate_ids"] = [author, publication]
    q["citation_candidate_id"] = author
    q["citation_publication_candidate_id"] = publication
    q["citation_locator"] = locator
    q["citations"] = [{"source_candidate_id": author,
                        "publication_candidate_id": publication,
                        "locator": locator}]
    q["cited_material_not_independently_consulted"] = True


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and atomize citations in Chapter 4 p.110 notes.")
    parser.add_argument("--apply", action="store_true", help="write after all source, table, and row guards pass")
    args = parser.parse_args()

    for path, expected in EXPECTED.items():
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f"guard failed: {path.relative_to(ROOT)} SHA-256 {actual} != {expected}")
    segment = next((json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
                    if line.strip() and json.loads(line).get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("guard failed: p.110 source segment hash mismatch")

    candidate_types = {}
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            candidate_types[row["candidate_id"]] = row["suggested_type"]
    mention_candidates = set()
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["segment_id"] == SEGMENT_ID:
                mention_candidates.add(row["candidate_id"])

    before = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in before}
    if len(by_id) != len(before) or any(sid not in by_id for sid in OLD_IDS):
        raise SystemExit("guard failed: duplicate or missing target statement IDs")
    if any(item["statement_id"] in by_id for item in SPLITS):
        raise SystemExit("guard failed: split statement ID already exists")

    after = copy.deepcopy(before)
    after_by_id = {row["statement_id"]: row for row in after}
    updates = []
    for sid, item in OLD_IDS.items():
        row = after_by_id[sid]
        q = row.get("qualifiers", {})
        if (row.get("segment_id") != SEGMENT_ID or q.get("source_line_start") != item["line"]
                or q.get("source_line_end") != item["line"]):
            raise SystemExit(f"guard failed: source anchor changed for {sid}")
        if (row.get("subject_candidate_id") != item["subject"]
                or row.get("object_candidate_id") != item["object"]
                or row.get("predicate") != item["predicate"]
                or q.get("relation_candidate") is not None):
            raise SystemExit(f"guard failed: existing classification changed for {sid}")
        if row.get("original_quote") != item["expected_quote"]:
            raise SystemExit(f"guard failed: source quote changed for {sid}")
        source, publication = item["author"], item["publication"]
        for cid in (HASKELL_BOOK, source, publication):
            if cid not in candidate_types:
                raise SystemExit(f"guard failed: missing candidate {cid}")
        for cid in (source, publication):
            if cid not in mention_candidates:
                raise SystemExit(f"guard failed: missing candidate mention {cid} in source segment")
        if candidate_types[HASKELL_BOOK] != "archive" or candidate_types[publication] != "archive":
            raise SystemExit(f"guard failed: expected Haskell book and cited publication archives for {sid}")
        if candidate_types[source] != "person":
            raise SystemExit(f"guard failed: expected cited author to be a person for {sid}")
        citation_fields(row, source, publication, item["locator"], item["claim"])
        row["original_quote"] = item["quote"]
        updates.append({"statement_id": sid, "subject": HASKELL_BOOK, "object": publication,
                        "predicate": "cites", "relation_candidate": True, "locator": item["locator"]})

    template = after_by_id["st-chp4-sec-ii-notes-p110-fn2-zeri-mitchell-voss"]
    for item in SPLITS:
        source, publication = item["author"], item["publication"]
        for cid in (source, publication):
            if cid not in candidate_types or cid not in mention_candidates:
                raise SystemExit(f"guard failed: split citation candidate {cid} has no source mention")
        if candidate_types[publication] != "archive":
            raise SystemExit(f"guard failed: cited publication {publication} is not an archive candidate")
        if candidate_types[source] != "person":
            raise SystemExit(f"guard failed: cited author {source} is not a person candidate")
        row = copy.deepcopy(template)
        row["statement_id"] = item["statement_id"]
        citation_fields(row, source, publication, item["locator"], item["claim"])
        row["original_quote"] = item["quote"]
        after.append(row)
        updates.append({"statement_id": item["statement_id"], "subject": HASKELL_BOOK,
                        "object": publication, "predicate": "cites", "relation_candidate": True,
                        "locator": item["locator"]})

    output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in after) + "\n").encode("utf-8")
    print(json.dumps({"mode": "APPLY PREFLIGHT" if args.apply else "DRY-RUN",
                      "updates": updates, "statements_before": len(before),
                      "statements_after": len(after)}, ensure_ascii=False, indent=2))
    if not args.apply:
        return 0

    backup = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp4-p110-notes-20261011")
    if backup.exists():
        raise SystemExit(f"guard failed: recovery copy already exists: {backup.name}")
    backup.write_bytes(STATEMENTS.read_bytes())
    write_atomic(STATEMENTS, output)
    print(f"APPLIED {STATEMENTS.relative_to(ROOT)} sha256={digest(STATEMENTS)}")
    print(f"recovery copy {backup.relative_to(ROOT)} sha256={digest(backup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
