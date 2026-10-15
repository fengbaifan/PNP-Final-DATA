#!/usr/bin/env python3
"""Classify p.104 body and footnote statements after source review.

Default mode is a guarded dry-run. --apply writes only book-statements.jsonl
and preserves an exact recovery copy first.
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
BODY_ID = "chp-4:04_CHP-4_sec_ii:l53-63"
NOTES_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
PDF_SHA256 = "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303"
SEGMENT_SHA256 = {
    BODY_ID: "b4a5ba97f08464b967ccca06b55a628e8a56e6188fb15d92d4ded8319c50a04a",
    NOTES_ID: "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e",
}
TABLE_SHA256 = {
    "book-statements.jsonl": "c5c9ad57a73d7f7045ee6221d284e2cb068356d2fbe9e991a9a4d30ed698f7b7",
    "entity-candidates.csv": "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
    "mentions.csv": "056f1ec87a9271eaadf34bdf31cbed181455dafa8c6896f833d3a84dd1ff4020",
    "s2-coverage.csv": "1211ffbc9d99f39ee53b132b2585d316452384efa7577fc904e63b8e2775b260",
}
BACKUP_SUFFIX = "bak-s2-chp4-p104-body-notes-20261011"
NEW_STATEMENT_ID = "st-chp4-sec-ii-p104-footnote3-cites-olina-ucelleria"

FALSE_DECISIONS = {
    "st-chp4-sec-ii-l53-63-cassiano-architectural-critique-closure":
        "This closes the quoted architectural judgment from p.103; it is not a separate entity-to-entity claim.",
    "st-chp4-sec-ii-l53-63-critique-attacks-whole-age":
        "This records Haskell's reading of the scope of Cassiano's criticism, not a relation between the named people.",
    "st-chp4-sec-ii-l53-63-fountains-allow-fantasy":
        "This is Haskell's general comment about fountains and artistic fantasy, not a relation to the named Fountain of the Four Rivers.",
    "st-chp4-sec-ii-l53-63-sacchi-slow":
        "This is Haskell's evaluative characterization of Sacchi's pace, not an entity-to-entity claim.",
    "st-chp4-sec-ii-p104-footnote3-bird-paintings-unidentified":
        "This states that Haskell had not identified the individual paintings; it does not assert a relation between entities.",
    "st-chp4-sec-ii-p104-footnote3-bird-pictures-evaluated":
        "This is Haskell's scalar evaluation of the unidentified paintings, not an entity-to-entity claim.",
    "st-chp4-sec-ii-p104-footnote3-skippon-attribution-unrecorded":
        "This records that Skippon did not specify authorship; it leaves the Poussin attribution unresolved rather than asserting a relation.",
}
TRUE_DECISIONS = {
    "st-chp4-sec-ii-l53-63-borromini-usually-singled-out":
        "Haskell identifies Borromini as the likely target of Cassiano's quoted architectural outburst; preserve this as an attributed S2 candidate.",
    "st-chp4-sec-ii-p104-footnote3-old-french-painter-reported-alive":
        "Haskell reports a second-hand statement that Poussin was still living in Rome; this is not independent verification.",
    "st-chp4-sec-ii-p104-footnote3-olina-notes-carlo-antonio-interest":
        "Haskell's note says Olina's cited work mentions Carlo Antonio's interest in birds; the publication was not independently consulted.",
    "st-chp4-sec-ii-p104-footnote3-skippon-noted-bird-paintings":
        "Haskell reports that Skippon noted many bird paintings in Cassiano's collection; no individual work or Poussin authorship is inferred.",
    "st-chp4-sec-ii-p104-footnote3-skippon-shown-collection":
        "Haskell reports Skippon's 1663 visit to Cassiano's collection, shown by an unnamed nephew; the nephew remains unidentified.",
}
CITATIONS = {
    "st-chp4-sec-ii-p104-footnote1-lumbroso": {
        "author": "cand-5626", "publication": "cand-5748",
        "locator": "Lumbroso, pp. 190 and 194",
        "claim": "Haskell's book cites Lumbroso, pages 190 and 194.",
    },
    "st-chp4-sec-ii-p104-footnote2-passeri": {
        "author": "cand-1856", "publication": "cand-5749",
        "locator": "Passeri, p. 107",
        "claim": "Haskell's book cites Passeri, page 107, for the preceding Duquesnoy and St Susanna judgment.",
    },
}
EXPECTED_UNCLASSIFIED_BODY = set(FALSE_DECISIONS) & {
    "st-chp4-sec-ii-l53-63-cassiano-architectural-critique-closure",
    "st-chp4-sec-ii-l53-63-critique-attacks-whole-age",
    "st-chp4-sec-ii-l53-63-fountains-allow-fantasy",
    "st-chp4-sec-ii-l53-63-sacchi-slow",
} | {"st-chp4-sec-ii-l53-63-borromini-usually-singled-out"}
EXPECTED_UNCLASSIFIED_NOTES = {
    *CITATIONS.keys(),
    "st-chp4-sec-ii-p104-footnote3-bird-paintings-unidentified",
    "st-chp4-sec-ii-p104-footnote3-bird-pictures-evaluated",
    "st-chp4-sec-ii-p104-footnote3-old-french-painter-reported-alive",
    "st-chp4-sec-ii-p104-footnote3-olina-notes-carlo-antonio-interest",
    "st-chp4-sec-ii-p104-footnote3-skippon-attribution-unrecorded",
    "st-chp4-sec-ii-p104-footnote3-skippon-noted-bird-paintings",
    "st-chp4-sec-ii-p104-footnote3-skippon-shown-collection",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


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
        raise SystemExit("preflight failed: source or scanned PDF changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    for segment_id, expected in SEGMENT_SHA256.items():
        row = segments.get(segment_id)
        if not row or row.get("sha256") != expected or row.get("asset_sha256") != SOURCE_SHA256:
            raise SystemExit(f"preflight failed: segment manifest changed for {segment_id}")

    table_paths = {name: TABLES / name for name in TABLE_SHA256}
    for name, expected in TABLE_SHA256.items():
        if sha256(table_paths[name]) != expected:
            raise SystemExit(f"preflight failed: table changed: {name}")

    statements_path = table_paths["book-statements.jsonl"]
    statements = read_jsonl(statements_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or len(statements) != 13136:
        raise SystemExit("preflight failed: statement IDs or table total changed")
    body_rows = [row for row in statements if row.get("segment_id") == BODY_ID]
    note_rows = [row for row in statements if row.get("segment_id") == NOTES_ID
                 and row.get("qualifiers", {}).get("printed_page_locator") == "p.104"]
    if len(body_rows) != 43 or len(note_rows) != 10:
        raise SystemExit(f"preflight failed: p.104 statement counts changed ({len(body_rows)} body, {len(note_rows)} notes)")

    body_unclassified = {row["statement_id"] for row in body_rows
                         if "relation_candidate" not in row.get("qualifiers", {})}
    note_unclassified = {row["statement_id"] for row in note_rows
                         if "relation_candidate" not in row.get("qualifiers", {})}
    if body_unclassified != EXPECTED_UNCLASSIFIED_BODY:
        raise SystemExit("preflight failed: p.104 body unclassified IDs changed")
    if note_unclassified != EXPECTED_UNCLASSIFIED_NOTES:
        raise SystemExit("preflight failed: p.104 footnote unclassified IDs changed")
    if NEW_STATEMENT_ID in by_id:
        raise SystemExit("preflight failed: planned citation statement already exists")

    candidates, _ = read_csv(table_paths["entity-candidates.csv"])
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(candidate_by_id) != len(candidates):
        raise SystemExit("preflight failed: duplicate candidate IDs")
    required_candidates = {"cand-0404", "cand-2036", "cand-2962", "cand-5626", "cand-1856",
                           "cand-5748", "cand-5749", "cand-1770", "cand-5745"}
    if not required_candidates.issubset(candidate_by_id):
        raise SystemExit("preflight failed: expected p.104 candidate endpoint is missing")
    if candidate_by_id["cand-0404"].get("suggested_type") != "person" or candidate_by_id["cand-2036"].get("suggested_type") != "person":
        raise SystemExit("preflight failed: Borromini or Cassiano candidate type changed")

    body = "\n".join(source_lines[52:63])
    note_text = "\n".join(source_lines[231:308])
    def check_quote(row):
        quote = row.get("original_quote", "")
        source = body if row.get("segment_id") == BODY_ID else note_text
        if not quote or quote not in source:
            raise SystemExit(f"preflight failed: source quote changed for {row['statement_id']}")
    for statement_id in body_unclassified | note_unclassified:
        check_quote(by_id[statement_id])

    for statement_id, note in FALSE_DECISIONS.items():
        if statement_id not in body_unclassified | note_unclassified:
            raise SystemExit(f"preflight failed: unexpected false-decision row {statement_id}")
        by_id[statement_id]["qualifiers"]["relation_candidate"] = False
        by_id[statement_id]["qualifiers"]["relation_candidate_note"] = note
    for statement_id, note in TRUE_DECISIONS.items():
        if statement_id not in body_unclassified | note_unclassified:
            raise SystemExit(f"preflight failed: unexpected true-decision row {statement_id}")
        by_id[statement_id]["qualifiers"]["relation_candidate"] = True
        by_id[statement_id]["qualifiers"]["relation_candidate_note"] = note
    by_id["st-chp4-sec-ii-l53-63-borromini-usually-singled-out"]["object_candidate_id"] = "cand-2036"

    for statement_id, citation in CITATIONS.items():
        row = by_id[statement_id]
        row["subject_candidate_id"] = "cand-2962"
        row["object_candidate_id"] = citation["publication"]
        row["predicate"] = "cites"
        q = row["qualifiers"]
        q["claim"] = citation["claim"]
        q["text_layer"] = "bibliographic citation to publication"
        q["citation_candidate_id"] = citation["author"]
        q["citation_publication_candidate_id"] = citation["publication"]
        q["citation_locator"] = citation["locator"]
        q["citations"] = [{"source_candidate_id": citation["author"],
                            "publication_candidate_id": citation["publication"],
                            "locator": citation["locator"]}]
        q["cited_material_not_independently_consulted"] = True
        q["mentioned_candidate_ids"] = list(dict.fromkeys(
            ["cand-2962", citation["author"], citation["publication"]]
            + q.get("mentioned_candidate_ids", [])))
        q["relation_candidate"] = True
        q["relation_candidate_note"] = "The footnote explicitly cites this publication locator; cited material was not independently consulted."

    by_id["st-chp4-sec-ii-p104-footnote3-old-french-painter-reported-alive"]["qualifiers"]["relation_candidate_note"] = TRUE_DECISIONS[
        "st-chp4-sec-ii-p104-footnote3-old-french-painter-reported-alive"]
    for statement_id in ["st-chp4-sec-ii-p104-footnote3-olina-notes-carlo-antonio-interest",
                         "st-chp4-sec-ii-p104-footnote3-skippon-noted-bird-paintings",
                         "st-chp4-sec-ii-p104-footnote3-skippon-shown-collection"]:
        by_id[statement_id]["qualifiers"]["relation_candidate_note"] = TRUE_DECISIONS[statement_id]

    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": NOTES_ID,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-5745",
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 254, "source_line_end": 254,
            "claim": "Haskell's footnote identifies P. Olina's Uccelleria of 1622 as a cited source.",
            "speaker": "Haskell footnote", "text_layer": "bibliographic citation to publication",
            "pdf_physical_page": 11, "printed_page_locator": "p.104", "footnote_marker": 3,
            "mentioned_candidate_ids": ["cand-2962", "cand-1770", "cand-5745"],
            "citation_candidate_id": "cand-1770", "citation_publication_candidate_id": "cand-5745",
            "citation_locator": "P. Olina, Uccelleria (1622)",
            "citations": [{"source_candidate_id": "cand-1770", "publication_candidate_id": "cand-5745",
                           "locator": "P. Olina, Uccelleria (1622)"}],
            "cited_material_not_independently_consulted": True,
            "qualification": "The footnote names the work and year but gives no separate page locator; the publication was not independently consulted.",
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly identifies this publication as a source; it is a citation pointer, not independent verification of the adjacent claims.",
        },
        "original_quote": "3 P. Olina’s Uccelleria of 1622",
        "origin": "book", "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }
    if new_statement["original_quote"] not in source_lines[253]:
        raise SystemExit("preflight failed: Olina citation anchor changed")
    statements.append(new_statement)
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("preflight failed: duplicate statement ID after update")

    body_counts = {value: sum(row.get("qualifiers", {}).get("relation_candidate") is value for row in body_rows)
                   for value in (True, False)}
    note_rows_after = [row for row in statements if row.get("segment_id") == NOTES_ID
                       and row.get("qualifiers", {}).get("printed_page_locator") == "p.104"]
    note_counts = {value: sum(row.get("qualifiers", {}).get("relation_candidate") is value for row in note_rows_after)
                   for value in (True, False)}
    if body_counts != {True: 39, False: 4} or note_counts != {True: 8, False: 3}:
        raise SystemExit(f"preflight failed: unexpected p.104 classification totals {body_counts} / {note_counts}")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "body_segment": BODY_ID, "body_unclassified_resolved": len(body_unclassified),
        "body_classification": {"relation_candidates": 39, "non_relations": 4},
        "footnote_segment": NOTES_ID, "p104_footnote_unclassified_resolved": len(note_unclassified),
        "p104_footnote_classification": {"relation_candidates": 8, "non_relations": 3},
        "new_citation_statement": NEW_STATEMENT_ID,
        "normalized_citations": list(CITATIONS),
        "endpoint_added": {"Borromini": "cand-0404", "critic": "cand-2036"},
        "statements_after": len(statements),
        "source_sha256": SOURCE_SHA256, "pdf_sha256": PDF_SHA256,
        "table_sha256_before": TABLE_SHA256["book-statements.jsonl"],
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
