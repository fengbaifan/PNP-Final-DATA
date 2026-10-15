#!/usr/bin/env python3
"""Classify the p.106 body and notes after checking the scan and transcript.

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
BODY_ID = "chp-4:04_CHP-4_sec_ii:l91-99"
NOTES_ID = "chp-4:04_CHP-4_sec_ii:l232-308"
SOURCE_SHA256 = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
PDF_SHA256 = "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303"
BODY_SEGMENT_SHA256 = "fc37671caac8205d1d3e4273243bb67d7d1a8e93ecbec4f5c1f9c30c3dbe6230"
NOTES_SEGMENT_SHA256 = "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e"
TABLE_SHA256 = {
    "book-statements.jsonl": "f8f6a604b3213c46e51e58943c25590db8ce0a6a52a47bb924e0340ce9ca7a87",
    "entity-candidates.csv": "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
}
BACKUP_SUFFIX = "bak-s2-chp4-p106-body-notes-20261011"

TARGETS = {
    "st-chp4-sec-ii-l91-99-profound-pictures-later-for-other-patrons",
    "st-chp4-sec-ii-l91-99-two-exceptions-to-conservative-patronage",
    "st-chp4-sec-ii-notes-l255-259-fn258-letter-citation",
    "st-chp4-sec-ii-notes-l255-259-fn259-chantelou-copy-location",
    "st-chp4-sec-ii-notes-l255-259-fn259-cited-literature",
    "st-chp4-sec-ii-notes-l255-259-fn259-mazenta-letter-citation",
    "st-chp4-sec-ii-notes-l255-259-fn259-version-locations",
}
NEW_CITATIONS = {
    "st-chp4-sec-ii-p106-fn259-cites-bialostocki-1960",
    "st-chp4-sec-ii-p106-fn259-cites-trauman-steinitz-1953",
    "st-chp4-sec-ii-p106-fn259-cites-carusi-1929",
}


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


def add_citation_statement(*, statement_id: str, original_quote: str,
                           publication_id: str, author_id: str,
                           locator: str, claim: str) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": NOTES_ID,
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": publication_id,
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": 259, "source_line_end": 259,
            "pdf_physical_page": 17, "printed_page_locator": "p.106",
            "footnote_marker": 2,
            "claim": claim,
            "speaker": "Haskell's footnote",
            "text_layer": "bibliographic citation to publication",
            "mentioned_candidate_ids": ["cand-2962", author_id, publication_id],
            "citation_candidate_id": author_id,
            "citation_publication_candidate_id": publication_id,
            "citation_locator": locator,
            "citations": [{"source_candidate_id": author_id,
                           "publication_candidate_id": publication_id,
                           "locator": locator}],
            "cited_material_not_independently_consulted": True,
            "qualification": "This records Haskell's citation only; the cited publication was not independently consulted.",
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly cites this publication; citation is not independent verification of the adjacent claims.",
        },
        "original_quote": original_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after guarded preflight")
    args = parser.parse_args()

    if sha256(SOURCE) != SOURCE_SHA256 or sha256(PDF) != PDF_SHA256:
        raise SystemExit("preflight failed: source transcript or scanned PDF changed")
    segments = {row["segment_id"]: row for row in read_jsonl(SEGMENTS)}
    for segment_id, expected_hash in ((BODY_ID, BODY_SEGMENT_SHA256),
                                      (NOTES_ID, NOTES_SEGMENT_SHA256)):
        segment = segments.get(segment_id)
        if not segment or segment.get("sha256") != expected_hash or segment.get("asset_sha256") != SOURCE_SHA256:
            raise SystemExit(f"preflight failed: source segment manifest changed: {segment_id}")

    paths = {name: TABLES / name for name in TABLE_SHA256}
    for name, expected in TABLE_SHA256.items():
        if sha256(paths[name]) != expected:
            raise SystemExit(f"preflight failed: table changed: {name}")
    statements_path = paths["book-statements.jsonl"]
    statements = read_jsonl(statements_path)
    by_id = {row["statement_id"]: row for row in statements}
    if len(by_id) != len(statements) or len(statements) != 13138:
        raise SystemExit("preflight failed: statement IDs or table total changed")

    target_rows = {statement_id: by_id.get(statement_id) for statement_id in TARGETS}
    if any(row is None for row in target_rows.values()):
        raise SystemExit("preflight failed: one or more p.106 target statements are missing")
    unclassified = {statement_id for statement_id, row in target_rows.items()
                    if "relation_candidate" not in row.get("qualifiers", {})}
    if unclassified != TARGETS:
        raise SystemExit("preflight failed: p.106 target classification state changed")
    if any(statement_id in by_id for statement_id in NEW_CITATIONS):
        raise SystemExit("preflight failed: a planned citation statement already exists")

    candidates = {row["candidate_id"]: row for row in csv.DictReader(
        paths["entity-candidates.csv"].open(encoding="utf-8-sig", newline=""))}
    expected_types = {
        "cand-1984": "person", "cand-2036": "person", "cand-2962": "archive",
        "cand-4634": "archive", "cand-5790": "archive", "cand-5794": "institution",
        "cand-5795": "institution", "cand-5796": "place", "cand-5786": "archive",
        "cand-2045": "archive", "cand-5797": "archive", "cand-5798": "archive",
        "cand-5799": "person", "cand-5800": "person", "cand-5801": "archive",
        "cand-5802": "person", "cand-5803": "archive", "cand-1601": "person",
        "cand-5806": "archive", "cand-1390": "person",
    }
    for candidate_id, expected_type in expected_types.items():
        row = candidates.get(candidate_id)
        if not row or row.get("suggested_type") != expected_type:
            raise SystemExit(f"preflight failed: candidate endpoint changed: {candidate_id}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    body_text = "\n".join(source_lines[90:99])
    notes_text = "\n".join(source_lines[257:259])
    for statement_id, row in target_rows.items():
        expected_text = body_text if row["segment_id"] == BODY_ID else notes_text
        quote = row.get("original_quote", "")
        if not quote or quote not in expected_text:
            raise SystemExit(f"preflight failed: source quote changed for {statement_id}")

    # Broad assessment: keep the plural, unnamed patron group open instead of
    # selecting a single patron or creating a specific endpoint.
    row = by_id["st-chp4-sec-ii-l91-99-profound-pictures-later-for-other-patrons"]
    q = row["qualifiers"]
    q["relation_candidate"] = True
    q["relation_candidate_note"] = (
        "Haskell relates Poussin's later, nearly all profound pictures to work for different patrons. "
        "The plural patron group is unnamed, so no single patron is selected as the object endpoint."
    )
    q["open_endpoint_reason"] = (
        "The statement names only an unspecified plural group of different patrons; preserve the relation candidate open."
    )

    row = by_id["st-chp4-sec-ii-l91-99-two-exceptions-to-conservative-patronage"]
    q = row["qualifiers"]
    q["relation_candidate"] = False
    q["relation_candidate_note"] = (
        "This is Haskell's editorial transition announcing two exceptions; it does not itself assert an entity-to-entity relation."
    )

    # Footnote 258 is a citation by Haskell's book to the 1911 edition. The
    # separately represented letter remains as cited context, not as a new fact.
    row = by_id["st-chp4-sec-ii-notes-l255-259-fn258-letter-citation"]
    row["subject_candidate_id"] = "cand-2962"
    row["object_candidate_id"] = "cand-4634"
    row["predicate"] = "cites"
    q = row["qualifiers"]
    q.update({
        "claim": "Haskell's book cites the 1911 Correspondance edition, page 130, for Poussin's letter dated 4 April 1642.",
        "speaker": "Haskell's footnote", "text_layer": "bibliographic citation to edition",
        "citation_candidate_id": "cand-1984", "citation_publication_candidate_id": "cand-4634",
        "citation_locator": "Poussin, Correspondance, p. 130; letter dated 4 April 1642",
        "citations": [{"source_candidate_id": "cand-1984", "publication_candidate_id": "cand-4634",
                       "locator": "Poussin, Correspondance, p. 130; letter dated 4 April 1642"}],
        "cited_material_not_independently_consulted": True,
        "qualification": "The date and page locator are Haskell's citation; the letter and edition were not independently collated.",
        "relation_candidate": True,
        "relation_candidate_note": "The footnote explicitly cites the Correspondance edition; this does not independently verify the letter's text or date.",
    })
    q["mentioned_candidate_ids"] = list(dict.fromkeys(
        ["cand-2962", "cand-1984", "cand-4634", "cand-5790"] + q.get("mentioned_candidate_ids", [])))

    # Preserve each repository report as an attributed S2 relation candidate.
    row = by_id["st-chp4-sec-ii-notes-l255-259-fn259-chantelou-copy-location"]
    q = row["qualifiers"]
    q["relation_candidate"] = True
    q["relation_candidate_note"] = (
        "Haskell reports the Chantelou copy at the Hermitage; record this attributed version-to-repository claim without independent verification."
    )
    q["mentioned_candidate_ids"] = list(dict.fromkeys(
        ["cand-5786", "cand-5795", "cand-5796"] + q.get("mentioned_candidate_ids", [])))

    # Atomize the four references in footnote 259. The existing row becomes
    # the 1954 citation; three rows are added for the other publications.
    row = by_id["st-chp4-sec-ii-notes-l255-259-fn259-cited-literature"]
    row["subject_candidate_id"] = "cand-2962"
    row["object_candidate_id"] = "cand-5797"
    row["predicate"] = "cites"
    q = row["qualifiers"]
    q.update({
        "claim": "Haskell cites Jan Białostocki's 1954 article for Poussin's reactions to Leonardo.",
        "speaker": "Haskell's footnote", "text_layer": "bibliographic citation to publication",
        "citation_candidate_id": "cand-5799", "citation_publication_candidate_id": "cand-5797",
        "citation_locator": "Jan Białostocki, 1954",
        "citations": [{"source_candidate_id": "cand-5799", "publication_candidate_id": "cand-5797",
                       "locator": "Jan Białostocki, 1954"}],
        "cited_material_not_independently_consulted": True,
        "qualification": "This records the citation only; the article and its argument were not independently consulted.",
        "relation_candidate": True,
        "relation_candidate_note": "The footnote explicitly cites this publication; citation is not independent verification of the adjacent claims.",
    })
    q["mentioned_candidate_ids"] = list(dict.fromkeys(
        ["cand-2962", "cand-5799", "cand-5797"] + q.get("mentioned_candidate_ids", [])))

    additions = [
        add_citation_statement(
            statement_id="st-chp4-sec-ii-p106-fn259-cites-bialostocki-1960",
            original_quote="i960", publication_id="cand-5798", author_id="cand-5799",
            locator="Jan Białostocki, 1960",
            claim="Haskell cites Jan Białostocki's 1960 article for Poussin's reactions to Leonardo."),
        add_citation_statement(
            statement_id="st-chp4-sec-ii-p106-fn259-cites-trauman-steinitz-1953",
            original_quote="Kate Trauman-Steinitz, 1953", publication_id="cand-5801", author_id="cand-5800",
            locator="Kate Trauman-Steinitz, 1953",
            claim="Haskell cites Kate Trauman-Steinitz's 1953 article for Poussin's reactions to Leonardo."),
        add_citation_statement(
            statement_id="st-chp4-sec-ii-p106-fn259-cites-carusi-1929",
            original_quote="Enrico Carusi, 1929", publication_id="cand-5803", author_id="cand-5802",
            locator="Enrico Carusi, 1929",
            claim="Haskell cites Enrico Carusi's 1929 article concerning Cassiano's role in the Leonardo project."),
    ]
    for new_row in additions:
        if new_row["original_quote"] not in notes_text:
            raise SystemExit(f"preflight failed: citation anchor changed: {new_row['statement_id']}")
        statements.append(new_row)

    # Footnote 259's Mazenta/Lumbroso sentence is recorded as Haskell's
    # publication citation; the letter remains an attributed cited source.
    row = by_id["st-chp4-sec-ii-notes-l255-259-fn259-mazenta-letter-citation"]
    row["subject_candidate_id"] = "cand-2962"
    row["object_candidate_id"] = "cand-5806"
    row["predicate"] = "cites"
    q = row["qualifiers"]
    q.update({
        "claim": "Haskell cites Lumbroso, page 258, for a letter by Ambrogio Mazenta that refers to Leonardo manuscripts.",
        "speaker": "Haskell's footnote", "text_layer": "bibliographic citation to published letter",
        "citation_candidate_id": "cand-1601", "citation_publication_candidate_id": "cand-5806",
        "citation_locator": "Lumbroso, p. 258 (letter from Ambrogio Mazenta)",
        "citations": [{"source_candidate_id": "cand-1601", "publication_candidate_id": "cand-5806",
                       "locator": "Lumbroso, p. 258"}],
        "cited_material_not_independently_consulted": True,
        "qualification": "Haskell reports a reference in a Mazenta letter; neither the letter nor Lumbroso's cited page was independently checked.",
        "relation_candidate": True,
        "relation_candidate_note": "The footnote cites Lumbroso for the reported letter; preserve the citation chain without treating it as verified manuscript evidence.",
    })
    q["mentioned_candidate_ids"] = list(dict.fromkeys(
        ["cand-2962", "cand-1601", "cand-5806", "cand-5626"] + q.get("mentioned_candidate_ids", [])))

    row = by_id["st-chp4-sec-ii-notes-l255-259-fn259-version-locations"]
    q = row["qualifiers"]
    q["relation_candidate"] = True
    q["relation_candidate_note"] = (
        "Haskell reports the generally accepted identification of Cassiano's Trattato version at the Ambrosiana; "
        "retain 'generally accepted' and do not present the repository identification as independently verified."
    )
    q["mentioned_candidate_ids"] = list(dict.fromkeys(
        ["cand-2045", "cand-5794"] + q.get("mentioned_candidate_ids", [])))

    if len({row["statement_id"] for row in statements}) != len(statements):
        raise SystemExit("preflight failed: duplicate statement ID after update")
    p106_rows = [row for row in statements if row.get("qualifiers", {}).get("printed_page_locator") == "p.106"]
    unresolved = [row["statement_id"] for row in p106_rows
                  if "relation_candidate" not in row.get("qualifiers", {})]
    totals = {value: sum(row.get("qualifiers", {}).get("relation_candidate") is value for row in p106_rows)
              for value in (True, False)}
    if unresolved or len(p106_rows) != 44 or totals != {True: 40, False: 4}:
        raise SystemExit(f"preflight failed: unexpected p.106 result: rows={len(p106_rows)}, totals={totals}, unresolved={unresolved}")

    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "source_pages": "p.106 body and footnotes",
        "unclassified_resolved": len(TARGETS),
        "citation_statements_added": sorted(NEW_CITATIONS),
        "p106_statement_totals": {"relation_candidates": totals[True], "non_relations": totals[False], "unclassified": 0},
        "p106_open_endpoint": "st-chp4-sec-ii-l91-99-profound-pictures-later-for-other-patrons",
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
