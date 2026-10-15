#!/usr/bin/env python3
"""Classify p.105 footnotes after checking the scan and source transcript.

Default mode is a guarded dry-run. --apply changes only book-statements.jsonl
and creates an exact recovery copy before atomic replacement.
"""
from __future__ import annotations

import argparse
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
NOTES_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
PDF_SHA256 = "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303"
SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
TABLE_SHA256 = {
    "book-statements.jsonl": "655b5e7bcce74755abce403358eb324c98f9009887f3f12a52b34dd04787a1e0",
    "entity-candidates.csv": "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
}
BACKUP_SUFFIX = "bak-s2-chp4-p105-notes-20261011"
NEW_CITATION_ID = "st-chp4-sec-ii-p105-footnote1-cites-rinehart"

FN255 = "st-chp4-sec-ii-notes-l255-259-fn255-galli-letter"
FN256 = "st-chp4-sec-ii-notes-l255-259-fn256-inventory-citation"
FN257 = "st-chp4-sec-ii-notes-l255-259-fn257-brienne-report-chain"
EXPECTED_UNCLASSIFIED = {FN255, FN256, FN257}


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
    segment = segments.get(NOTES_ID)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("preflight failed: source segment manifest changed")

    paths = {name: TABLES / name for name in TABLE_SHA256}
    for name, expected in TABLE_SHA256.items():
        if sha256(paths[name]) != expected:
            raise SystemExit(f"preflight failed: table changed: {name}")

    statement_path = paths["book-statements.jsonl"]
    statements = read_jsonl(statement_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or len(statements) != 13137:
        raise SystemExit("preflight failed: statement IDs or table total changed")
    note_rows = [row for row in statements if row.get("segment_id") == NOTES_ID
                 and row.get("qualifiers", {}).get("printed_page_locator") == "p.105"
                 and 255 <= row.get("qualifiers", {}).get("source_line_start", 0) <= 257]
    if {row["statement_id"] for row in note_rows} != EXPECTED_UNCLASSIFIED or len(note_rows) != 3:
        raise SystemExit("preflight failed: p.105 unclassified statements changed")
    if any("relation_candidate" in row.get("qualifiers", {}) for row in note_rows):
        raise SystemExit("preflight failed: a p.105 target has already been classified")
    if NEW_CITATION_ID in by_id:
        raise SystemExit("preflight failed: planned citation statement already exists")

    candidates = {row["candidate_id"]: row for row in
                  __import__("csv").DictReader(paths["entity-candidates.csv"].open(encoding="utf-8-sig", newline=""))}
    expected_candidates = {
        "cand-0452": "person", "cand-1111": "person", "cand-1984": "person",
        "cand-2036": "person", "cand-2962": "archive", "cand-5658": "archive",
        "cand-5791": "archive", "cand-5792": "archive", "cand-5793": "person",
        "cand-5804": "person", "cand-5805": "archive",
    }
    for candidate_id, expected_type in expected_candidates.items():
        row = candidates.get(candidate_id)
        if not row or row.get("suggested_type") != expected_type:
            raise SystemExit(f"preflight failed: candidate endpoint changed: {candidate_id}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    note_text = "\n".join(source_lines[254:257])
    for row in note_rows:
        quote = row.get("original_quote", "")
        if not quote or quote not in note_text:
            raise SystemExit(f"preflight failed: source quote changed for {row['statement_id']}")
    if not any(row.get("qualifiers", {}).get("footnote_statement_id") == FN255
               for row in statements if row.get("segment_id") == "chp-4:04_CHP-4_sec_ii:l80-89"):
        raise SystemExit("preflight failed: p.105 body-to-footnote link changed")

    # Footnote 1 reports Cassiano buying pictures for Galli through a cited letter.
    row = by_id[FN255]
    row["subject_candidate_id"] = "cand-2036"
    row["object_candidate_id"] = "cand-1111"
    row["predicate"] = "buying_pictures_for"
    q = row["qualifiers"]
    q["claim"] = ("Haskell's footnote identifies Cassiano's letter to Agnolo Galli, dated "
                  "3 November 1629, and says Cassiano was buying pictures for Galli.")
    q["speaker"] = "Haskell's footnote, citing Rinehart"
    q["text_layer"] = "secondary report of correspondence"
    q["document_candidate_id"] = "cand-5791"
    q["citation_candidate_id"] = "cand-5793"
    q["citation_publication_candidate_id"] = "cand-5792"
    q["citation_locator"] = "Rinehart, 1961, p. 52"
    q["cited_material_not_independently_consulted"] = True
    q["qualification"] = ("The letter and buying arrangement are reported through Haskell's note and "
                          "Rinehart, page 52; neither the letter nor the cited page was independently consulted.")
    q["mentioned_candidate_ids"] = list(dict.fromkeys(
        ["cand-2036", "cand-1111", "cand-5791", "cand-5793", "cand-5792"]
        + q.get("mentioned_candidate_ids", [])))
    q["relation_candidate"] = True
    q["relation_candidate_note"] = ("Haskell reports through Rinehart that Cassiano was buying pictures for "
                                    "Galli; retain the source attribution and do not infer completed purchases.")

    # Footnote 2 is a citation plus an internal cross-reference, not independent validation.
    row = by_id[FN256]
    row["subject_candidate_id"] = "cand-2962"
    row["object_candidate_id"] = "cand-5658"
    row["predicate"] = "cites"
    q = row["qualifiers"]
    q["claim"] = "Haskell's book cites the Haskell and Rinehart 1960 inventory and cross-refers to p. 100, note 2."
    q["speaker"] = "Haskell's footnote"
    q["text_layer"] = "bibliographic citation to publication"
    q["citation_publication_candidate_id"] = "cand-5658"
    q["citation_locator"] = "Haskell and Rinehart, 1960; see also p. 100, note 2"
    q["citations"] = [{"publication_candidate_id": "cand-5658",
                        "locator": "Haskell and Rinehart, 1960; see also p. 100, note 2"}]
    q["cited_material_not_independently_consulted"] = True
    q["qualification"] = "Citation and internal cross-reference only; the inventory was not independently checked."
    q["mentioned_candidate_ids"] = list(dict.fromkeys(["cand-2962", "cand-5658"]
                                                       + q.get("mentioned_candidate_ids", [])))
    q["relation_candidate"] = True
    q["relation_candidate_note"] = "The footnote explicitly cites the inventory; preserve its cross-reference and do not infer independent verification."

    # Footnote 3 gives the secondary citation chain for the reported advice.
    row = by_id[FN257]
    row["subject_candidate_id"] = "cand-2962"
    row["object_candidate_id"] = "cand-5805"
    row["predicate"] = "cites"
    q = row["qualifiers"]
    q["claim"] = ("Haskell cites Thuillier's 1960 publication, volume II, page 210, for the report "
                  "that Brienne recorded the advice in 1693-1695.")
    q["speaker"] = "Haskell's footnote"
    q["text_layer"] = "bibliographic citation to a secondary report"
    q["citation_candidate_id"] = "cand-5804"
    q["citation_publication_candidate_id"] = "cand-5805"
    q["citation_locator"] = "Thuillier, 1960, Actes du Colloque Poussin, II, p. 210"
    q["citations"] = [{"source_candidate_id": "cand-5804", "publication_candidate_id": "cand-5805",
                        "locator": "Thuillier, 1960, Actes du Colloque Poussin, II, p. 210"}]
    q["cited_material_not_independently_consulted"] = True
    q["qualification"] = ("This is a second-hand citation chain: Haskell attributes the report to Brienne "
                          "and cites Thuillier; neither source was independently consulted here.")
    q["ocr_corrections"] = [{"source_line": 257, "source_form": "i960", "print_form": "1960"}]
    q["mentioned_candidate_ids"] = list(dict.fromkeys(
        ["cand-2962", "cand-0452", "cand-1984", "cand-5804", "cand-5805"]
        + q.get("mentioned_candidate_ids", [])))
    q["relation_candidate"] = True
    q["relation_candidate_note"] = "This records Haskell's citation to the secondary report; it does not independently verify Brienne's report or the advice."

    # Footnote 1 has two claims: the reported Cassiano-Galli transaction context above,
    # and Haskell's bibliographic citation to the Rinehart publication here.
    new_statement = {
        "statement_id": NEW_CITATION_ID,
        "segment_id": NOTES_ID,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": "cand-5792",
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 255, "source_line_end": 255,
            "claim": "Haskell's footnote cites S. Rinehart's 1961 article, page 52, for the letter to Agnolo Galli.",
            "speaker": "Haskell's footnote", "text_layer": "bibliographic citation to publication",
            "pdf_physical_page": 16, "printed_page_locator": "p.105", "footnote_marker": 1,
            "mentioned_candidate_ids": ["cand-2962", "cand-5791", "cand-5792", "cand-5793", "cand-2036", "cand-1111"],
            "citation_candidate_id": "cand-5793", "citation_publication_candidate_id": "cand-5792",
            "citation_locator": "Rinehart, 1961, p. 52",
            "citations": [{"source_candidate_id": "cand-5793", "publication_candidate_id": "cand-5792",
                           "locator": "Rinehart, 1961, p. 52"}],
            "cited_material_not_independently_consulted": True,
            "qualification": "The cited page and letter were not independently consulted; this citation does not verify the reported transaction.",
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly cites Rinehart, page 52; retain it as a bibliographic link, not independent verification.",
        },
        "original_quote": "see Rinehart, 1961, p. 52.",
        "origin": "book", "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }
    if new_statement["original_quote"] not in source_lines[254]:
        raise SystemExit("preflight failed: p.105 footnote 1 citation anchor changed")
    statements.append(new_statement)
    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("preflight failed: duplicate statement ID after update")

    note_after = [row for row in statements if row.get("segment_id") == NOTES_ID
                  and row.get("qualifiers", {}).get("printed_page_locator") == "p.105"
                  and row.get("qualifiers", {}).get("source_line_start") in {255, 256, 257}]
    totals = {value: sum(row.get("qualifiers", {}).get("relation_candidate") is value for row in note_after)
              for value in (True, False)}
    if totals != {True: 4, False: 0} or len(note_after) != 4:
        raise SystemExit(f"preflight failed: unexpected p.105 outcome {totals}, rows={len(note_after)}")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "source_page": "p.105 footnotes 1-3, physical PDF page 16",
        "unclassified_resolved": len(EXPECTED_UNCLASSIFIED),
        "classification": {"relation_candidates": 4, "non_relations": 0},
        "citation_added": NEW_CITATION_ID,
        "statements_after": len(statements),
        "table_sha256_before": TABLE_SHA256["book-statements.jsonl"],
        "source_sha256": SOURCE_SHA256, "pdf_sha256": PDF_SHA256,
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backup = statement_path.with_name(statement_path.name + "." + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit("apply failed: recovery backup already exists")
    if sha256(statement_path) != TABLE_SHA256["book-statements.jsonl"]:
        raise SystemExit("apply failed: statement table changed after preflight")
    shutil.copy2(statement_path, backup)
    try:
        write_jsonl_atomic(statement_path, statements)
    except Exception:
        shutil.copy2(backup, statement_path)
        raise
    print("APPLY_OK")
    print("statements_sha256_after", sha256(statement_path))
    print("recovery_copy", backup.name)


if __name__ == "__main__":
    main()
