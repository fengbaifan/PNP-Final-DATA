#!/usr/bin/env python3
"""Classify p.103 S2 claims and atomize its footnote citations with guards."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path("02-sources/02-Markdown/04_CHP-4_sec_ii.md")
PDF = Path("02-sources/01-book/CHP-4.pdf")
STATEMENTS = Path("04-knowledge/tables/book-statements.jsonl")
CANDIDATES = Path("04-knowledge/tables/entity-candidates.csv")
SEGMENTS = Path("04-knowledge/tables/segments.jsonl")
BACKUP = ROOT / "04-knowledge/tables/book-statements.jsonl.bak-s2-chp4-p103-relations-20261011"

EXPECTED = {
    SOURCE: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    PDF: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
    STATEMENTS: "d06c6aef7485cf8c990201e93f9385e23d10ab9f89642cc89979ed2cc340f0fc",
    CANDIDATES: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
}
SEGMENT_HASHES = {
    "chp-4:04_CHP-4_sec_ii:l33-44": "b58e75c02a220218d26467325369277c99d76b05ff11d3ce57af8b100d0038bf",
    "chp-4:04_CHP-4_sec_ii:l46-51": "5d759fc28c9dd1319dcd6f90f3fdf51004910ce09f4de69b80242712d4c95f4c",
    "chp-4:04_CHP-4_sec_ii:l232-308": "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e",
}
TARGET_IDS = {
    "st-chp4-sec-ii-l33-44-galileo-youth-fragment",
    "st-chp4-sec-ii-l46-51-barberini-grandiose-effects",
    "st-chp4-sec-ii-l46-51-bernini-breaks-medium-boundaries",
    "st-chp4-sec-ii-l46-51-cassiano-architectural-critique",
    "st-chp4-sec-ii-l46-51-cassiano-distaste-pietro-friendship",
    "st-chp4-sec-ii-l46-51-expense-beyond-cassiano-resources",
    "st-chp4-sec-ii-l46-51-galileo-tasso-ariosto-painting-analogy",
    "st-chp4-sec-ii-l46-51-galileo-youth-closure",
    "st-chp4-sec-ii-l46-51-haskell-reading-galileo",
    "st-chp4-sec-ii-l46-51-mannerists-no-longer-interest",
    "st-chp4-sec-ii-p103-footnote1-citations",
    "st-chp4-sec-ii-p103-footnote2-pietro-letters",
    "st-chp4-sec-ii-p103-footnote3-carlo-dati",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_jsonl(path: Path) -> tuple[list[dict], bytes, str]:
    raw = path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    return rows, raw, newline


def dump_jsonl(rows: list[dict], newline: str) -> bytes:
    return (newline.join(json.dumps(row, ensure_ascii=False) for row in rows) + newline).encode("utf-8")


def classify(row: dict, relation: bool, note: str) -> None:
    q = row.setdefault("qualifiers", {})
    q["relation_candidate"] = relation
    q["relation_candidate_note"] = note


def citation_row(statement_id: str, object_id: str, cited_id: str, locator: str,
                 quote: str, line: int, marker: int, qualification: str) -> dict:
    q = {
        "source_line_start": line,
        "source_line_end": line,
        "claim": f"Haskell's book cites {locator}.",
        "speaker": "Haskell footnote",
        "text_layer": "bibliographic citation to publication or source",
        "pdf_physical_page": 10,
        "printed_page_locator": "p.103",
        "footnote_marker": marker,
        "citation_locator": locator,
        "cited_material_not_independently_consulted": True,
        "mentioned_candidate_ids": list(dict.fromkeys(["cand-2962", cited_id, object_id])),
        "qualification": qualification,
        "relation_candidate": True,
        "relation_candidate_note": "The footnote explicitly cites this locator; the cited material is not treated as independent verification of the adjacent claim.",
    }
    if cited_id != object_id:
        q["citation_candidate_id"] = cited_id
    q["citation_publication_candidate_id"] = object_id
    return {
        "statement_id": statement_id,
        "segment_id": "chp-4:04_CHP-4_sec_ii:l232-308",
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": object_id,
        "predicate": "cites",
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE.as_posix(),
    }


def atomic_write(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preconditions pass; default is dry-run")
    args = parser.parse_args()
    if not (ROOT / ".agents/pipeline.md").exists():
        raise SystemExit(f"Repository root not found: {ROOT}")
    for rel, expected in EXPECTED.items():
        actual = sha256((ROOT / rel).read_bytes())
        if actual != expected:
            raise SystemExit(f"Hash mismatch for {rel}: expected {expected}, found {actual}")

    segments = [json.loads(line) for line in (ROOT / SEGMENTS).read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_map = {row["segment_id"]: row for row in segments}
    for segment_id, expected in SEGMENT_HASHES.items():
        actual = segment_map.get(segment_id, {}).get("sha256")
        if actual != expected:
            raise SystemExit(f"Segment hash mismatch for {segment_id}: {actual}")

    source_text = (ROOT / SOURCE).read_text(encoding="utf-8-sig")
    expected_phrases = ["Mancini, I, p. 263", "Haskell and Rinehart, i960", "published in Bottari, I, pp. 413-20", "Carlo Dari"]
    if not all(phrase in source_text for phrase in expected_phrases):
        raise SystemExit("One or more p.103 footnote locators differ from the expected S0 transcription")

    rows, raw, newline = read_jsonl(ROOT / STATEMENTS)
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("Duplicate statement_id found")
    unresolved = {
        row["statement_id"] for row in rows
        if (row.get("qualifiers") or {}).get("printed_page_locator") == "p.103"
        and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unresolved != TARGET_IDS:
        raise SystemExit(f"p.103 target set changed: expected {sorted(TARGET_IDS)}, found {sorted(unresolved)}")

    with (ROOT / CANDIDATES).open(encoding="utf-8-sig", newline="") as stream:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(stream)}
    required = {"cand-2962", "cand-1507", "cand-5726", "cand-5658", "cand-0342", "cand-5725", "cand-0417", "cand-4830", "cand-0905", "cand-5727"}
    if not required.issubset(candidate_ids):
        raise SystemExit(f"Missing candidate IDs: {sorted(required - candidate_ids)}")

    scalar_notes = {
        "st-chp4-sec-ii-l33-44-galileo-youth-fragment": "This is the p.102 fragment 'When still'; p.103 supplies the full scalar statement. It is not an entity relation.",
        "st-chp4-sec-ii-l46-51-barberini-grandiose-effects": "Haskell's scalar account of the Barberini family's desired effects and willingness to break rules; the desired effects are not a bounded entity.",
        "st-chp4-sec-ii-l46-51-bernini-breaks-medium-boundaries": "Haskell's description of Bernini's artistic techniques; no bounded second entity is asserted, so do not invent a technique group.",
        "st-chp4-sec-ii-l46-51-cassiano-architectural-critique": "Cassiano's quoted evaluation of artists who depart from antique architectural rules is a scalar viewpoint. The named restorers and their Roman-building proportions are recorded in the adjacent relation statement; the p.104 continuation remains linked.",
        "st-chp4-sec-ii-l46-51-cassiano-distaste-pietro-friendship": "Haskell's scalar description of Cassiano's reaction to the artistic effects; his separately stated friendship with Pietro remains a relation candidate.",
        "st-chp4-sec-ii-l46-51-expense-beyond-cassiano-resources": "Haskell's cost and affordability assessment has no bounded second entity; the two named pictures remain separately represented.",
        "st-chp4-sec-ii-l46-51-galileo-tasso-ariosto-painting-analogy": "A quoted literary and pictorial analogy attributed to Galileo, not a relation between the mentioned people; retain the source's comparison without inferring a specific artwork or authoring relation.",
        "st-chp4-sec-ii-l46-51-galileo-youth-closure": "Haskell's narrative characterization of young Galileo's discussion; the quoted comparison is separately recorded and is not an entity relation.",
        "st-chp4-sec-ii-l46-51-haskell-reading-galileo": "Haskell's interpretation of Galileo's aesthetic position, not a relation between Galileo and the named styles.",
        "st-chp4-sec-ii-l46-51-mannerists-no-longer-interest": "Haskell's broad periodizing statement about the older Mannerist generation; the sentence does not identify a specific person whose interest changed.",
    }
    for sid, note in scalar_notes.items():
        classify(by_id[sid], False, note)

    # Split the compound footnote into one citation row per locator.
    f1 = by_id["st-chp4-sec-ii-p103-footnote1-citations"]
    f1["subject_candidate_id"] = "cand-2962"
    f1["predicate"] = "cites"
    f1["original_quote"] = "1 Mancini, I, p. 263"
    f1["qualifiers"].update({
        "citation_candidate_id": "cand-1507", "citation_publication_candidate_id": "cand-5726",
        "citation_locator": "Mancini, I, p. 263", "cited_material_not_independently_consulted": True,
    })
    classify(f1, True, "The book explicitly cites Giulio Mancini, volume I, page 263; the page and publication were not independently consulted.")

    new_rows = [citation_row(
        "st-chp4-sec-ii-p103-footnote1-cites-haskell-rinehart", "cand-5658", "cand-5658",
        "Haskell and Rinehart, 1960", "and Haskell and Rinehart, i960.", 250, 1,
        "The scan reads 1960 while S0 OCR reads i960; record the printed reading in this qualifier only. The article was not independently consulted.",
    )]

    f2 = by_id["st-chp4-sec-ii-p103-footnote2-pietro-letters"]
    f2["subject_candidate_id"] = "cand-2962"
    f2["predicate"] = "cites"
    f2["qualifiers"].update({"citation_candidate_id": "cand-0342", "citation_locator": "Pietro's letters to Cassiano",
                             "cited_material_not_independently_consulted": True})
    classify(f2, True, "The footnote directs readers to the unspecified Pietro-to-Cassiano correspondence; no dates or individual letters are identified, and the cited material was not consulted.")
    new_rows.append(citation_row(
        "st-chp4-sec-ii-p103-footnote2-cites-bottari", "cand-4830", "cand-0417",
        "Bottari, I, pp. 413–420", "published in Bottari, I, pp. 413-20.", 251, 2,
        "Bottari's cited pages are recorded as printed and have not been independently consulted.",
    ))

    f3 = by_id["st-chp4-sec-ii-p103-footnote3-carlo-dati"]
    f3["subject_candidate_id"] = "cand-2962"
    f3["predicate"] = "cites"
    f3["qualifiers"].update({
        "citation_candidate_id": "cand-0905", "citation_publication_candidate_id": "cand-5727",
        "citation_locator": "Carlo Dati [no pagination]", "cited_material_not_independently_consulted": True,
        "ocr_note": "S0 OCR reads 'Carlo Dari'; the CHP-4 p.103 scan reads 'Carlo Dati'. Preserve S0 and record the print reading in S2 only.",
    })
    classify(f3, True, "The footnote attributes the preceding quotation to a Carlo Dati source without pagination; its work and cited text remain unresolved and unconsulted.")

    new_ids = {row["statement_id"] for row in new_rows}
    if new_ids & set(by_id):
        raise SystemExit(f"New statement IDs already exist: {sorted(new_ids & set(by_id))}")
    rows.extend(new_rows)
    result = dump_jsonl(rows, newline)
    if args.apply:
        if sha256(raw) != EXPECTED[STATEMENTS]:
            raise SystemExit("Statement table changed before apply")
        if BACKUP.exists():
            raise SystemExit(f"Recovery copy already exists: {BACKUP}")
        BACKUP.write_bytes(raw)
        atomic_write(ROOT / STATEMENTS, result)
        print(f"applied statements={len(rows)} backup={BACKUP.name} before={sha256(raw)} after={sha256(result)}")
    else:
        print(f"dry-run passed; targets={len(TARGET_IDS)} new_statements={len(new_rows)} rows_after={len(rows)}")
        print(f"statement_sha_before={sha256(raw)} statement_sha_after={sha256(result)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
