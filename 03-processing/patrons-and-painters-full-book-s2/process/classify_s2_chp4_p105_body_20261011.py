#!/usr/bin/env python3
"""Classify unreviewed relation candidates in the p.105 body segment.

Default mode is a guarded dry-run. --apply changes only book-statements.jsonl
and creates an exact recovery copy before atomic replacement.
"""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-4.pdf"
SEGMENTS = TABLES / "segments.jsonl"
BODY_ID = "chp-4:04_CHP-4_sec_ii:l80-89"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
PDF_SHA256 = "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303"
SEGMENT_SHA256 = "18e5ceac63c431e5df905b26270ac6ef123624177a519b77b8b5c6fd25d234fa"
TABLE_SHA256 = {
    "book-statements.jsonl": "15aae231dbf7dd785868ebeaa883115e7d7c79b49977ed9246864cc3bfb5bb65",
    "entity-candidates.csv": "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
}
BACKUP_SUFFIX = "bak-s2-chp4-p105-body-20261011"

FALSE_DECISIONS = {
    "st-chp4-sec-ii-l80-89-bacchanals-rhetorical-query":
        "This is Haskell's rhetorical question; it identifies no particular painting and asserts neither authorship nor collection membership.",
    "st-chp4-sec-ii-l80-89-cassiano-modern-art-taste":
        "This is Haskell's scalar characterization of Cassiano's taste, not an entity-to-entity relation.",
    "st-chp4-sec-ii-l80-89-possible-recondite-subjects":
        "This is Haskell's qualified possibility about unidentified or unassociated pictures; no additional work or subject is asserted.",
    "st-chp4-sec-ii-l80-89-traveller-sacrifice-question":
        "This is Haskell's rhetorical question about an unidentified Sacrifice; it does not establish authorship or Cassiano's ownership.",
}
OPEN_RELATION_ID = "st-chp4-sec-ii-l80-89-identified-poussin-subjects-in-collection"
EXPECTED_UNCLASSIFIED = set(FALSE_DECISIONS) | {OPEN_RELATION_ID}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl_atomic(path: Path, rows) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after guarded preflight")
    args = parser.parse_args()

    if sha256(SOURCE) != SOURCE_SHA256 or sha256(PDF) != PDF_SHA256:
        raise SystemExit("preflight failed: source transcript or scanned PDF changed")
    segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    segment = segments.get(BODY_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("preflight failed: source segment manifest changed")

    paths = {name: TABLES / name for name in TABLE_SHA256}
    for name, expected in TABLE_SHA256.items():
        if sha256(paths[name]) != expected:
            raise SystemExit(f"preflight failed: table changed: {name}")
    statements_path = paths["book-statements.jsonl"]
    statements = read_jsonl(statements_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or len(statements) != 13138:
        raise SystemExit("preflight failed: statement IDs or table total changed")

    body_rows = [row for row in statements if row.get("segment_id") == BODY_ID
                 and row.get("qualifiers", {}).get("printed_page_locator") == "p.105"]
    unclassified = {row["statement_id"] for row in body_rows
                    if "relation_candidate" not in row.get("qualifiers", {})}
    if unclassified != EXPECTED_UNCLASSIFIED or len(body_rows) != 29:
        raise SystemExit("preflight failed: p.105 body target IDs or row count changed")

    candidates = {row["candidate_id"]: row for row in
                  csv.DictReader(paths["entity-candidates.csv"].open(encoding="utf-8-sig", newline=""))}
    required = {"cand-2036", "cand-1984", "cand-5758", "cand-5759", "cand-5760",
                "cand-5761", "cand-5762", "cand-5764", "cand-5765"}
    if not required.issubset(candidates):
        raise SystemExit("preflight failed: expected p.105 entity candidates changed")
    for candidate_id in ["cand-5758", "cand-5759", "cand-5760", "cand-5761", "cand-5762"]:
        if candidates[candidate_id].get("suggested_type") != "work":
            raise SystemExit(f"preflight failed: expected work candidate changed: {candidate_id}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    page_text = "\n".join(source_lines[80:89])
    for statement_id in unclassified:
        quote = by_id[statement_id].get("original_quote", "")
        if not quote or quote not in page_text:
            raise SystemExit(f"preflight failed: source quote changed for {statement_id}")

    for statement_id, note in FALSE_DECISIONS.items():
        q = by_id[statement_id]["qualifiers"]
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    # The sentence refers to several identified Poussin works in Cassiano's
    # collection. Keep the plural scope and all work mentions; do not nominate
    # one title as the sole object endpoint.
    row = by_id[OPEN_RELATION_ID]
    q = row["qualifiers"]
    q["relation_candidate"] = True
    q["relation_candidate_note"] = (
        "Haskell places several identified Poussin subjects within the paintings in Cassiano's collection. "
        "The sentence names a plural set, so no single work is selected as the object endpoint; retain the "
        "title-level work candidates in mentioned_candidate_ids for later atomized endpoint resolution."
    )
    q["open_endpoint_reason"] = (
        "Plural relation to several named work candidates; the single object_candidate_id field cannot represent the set."
    )

    counts = {value: sum(row.get("qualifiers", {}).get("relation_candidate") is value for row in body_rows)
              for value in (True, False)}
    if counts != {True: 25, False: 4}:
        raise SystemExit(f"preflight failed: unexpected p.105 body classification totals {counts}")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "segment": BODY_ID,
        "unclassified_resolved": len(unclassified),
        "p105_body_classification": {"relation_candidates": 25, "non_relations": 4},
        "plural_relation_open_endpoint": OPEN_RELATION_ID,
        "statements_after": len(statements),
        "table_sha256_before": TABLE_SHA256["book-statements.jsonl"],
        "source_sha256": SOURCE_SHA256, "pdf_sha256": PDF_SHA256,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backup = statements_path.with_name(statements_path.name + "." + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("apply failed: recovery backup already exists")
    if sha256(statements_path) != TABLE_SHA256["book-statements.jsonl"]:
        raise SystemExit("apply failed: statement table changed after preflight")
    shutil.copy2(statements_path, backup)
    try:
        write_jsonl_atomic(statements_path, statements)
    except Exception:
        shutil.copy2(backup, statements_path)
        raise
    print("APPLY_OK")
    print("statements_sha256_after", sha256(statements_path))
    print("recovery_copy", backup.name)


if __name__ == "__main__":
    main()
