#!/usr/bin/env python3
"""Classify p.101–102 carryover statements with guarded S2 table writes."""

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
BACKUP = ROOT / "04-knowledge/tables/book-statements.jsonl.bak-s2-chp4-p102-relations-20261011"

EXPECTED = {
    SOURCE: "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575",
    PDF: "2a737df590be91a661dbb2dd5c75b7d9df3d882487183f58430e51fb43b26303",
    STATEMENTS: "fd3a88644900fffe37df525a9f38905db0df125e4246228eaad176208e47d351",
    CANDIDATES: "008176568d37d51db72fcc7393bb72711d8c0c7e9dcd1b4cccd1c018ac29a85d",
}
SEGMENT_HASHES = {
    "chp-4:04_CHP-4_sec_ii:l24-31": "bb7074a81019378f57e08bb514671a9f4869443a7d5a5d9e20f4c953442b36aa",
    "chp-4:04_CHP-4_sec_ii:l33-44": "b58e75c02a220218d26467325369277c99d76b05ff11d3ce57af8b100d0038bf",
    "chp-4:04_CHP-4_sec_ii:l232-308": "792d95e61aab35b3bfb639af2364220365d26076eeafb93e545526ccf302ca7e",
}
TARGET_IDS = {
    "st-chp4-sec-ii-l24-31-veneration-fragment",
    "st-chp4-sec-ii-l33-44-different-artistic-preference",
    "st-chp4-sec-ii-l33-44-early-taste-contrast",
    "st-chp4-sec-ii-l33-44-fifth-volume-image-sources",
    "st-chp4-sec-ii-l33-44-galileo-scientific-attitude-and-taste",
    "st-chp4-sec-ii-l33-44-interest-in-contemporary-painting",
    "st-chp4-sec-ii-l33-44-veneration-closure",
    "st-chp4-sec-ii-l33-44-wide-tastes",
    "st-chp4-sec-ii-p102-footnote1-baldinucci",
    "st-chp4-sec-ii-p102-footnote2-vouet-letters",
    "st-chp4-sec-ii-p102-footnote3-panofsky",
    "st-chp4-sec-ii-p102-footnote4-cigoli-galilei",
    "st-chp4-sec-ii-p102-footnote4-matteoli-edited-carteggio",
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


def citation_row(statement_id: str, object_id: str, author_id: str, locator: str,
                 quote: str, line: int, note: str) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": "chp-4:04_CHP-4_sec_ii:l232-308",
        "subject_candidate_id": "cand-2962",
        "object_candidate_id": object_id,
        "predicate": "cites",
        "qualifiers": {
            "source_line_start": line,
            "source_line_end": line,
            "claim": f"Haskell's book cites {locator}.",
            "speaker": "Haskell footnote",
            "text_layer": "bibliographic citation to publication",
            "pdf_physical_page": 9,
            "printed_page_locator": "p.102",
            "footnote_marker": 2,
            "citation_candidate_id": author_id,
            "citation_publication_candidate_id": object_id,
            "citation_locator": locator,
            "citations": [{"source_candidate_id": author_id, "publication_candidate_id": object_id, "locator": locator}],
            "mentioned_candidate_ids": ["cand-2962", author_id, object_id],
            "cited_material_not_independently_consulted": True,
            "qualification": note,
            "relation_candidate": True,
            "relation_candidate_note": "The footnote explicitly cites this publication locator; it does not independently verify the cited text or adjacent claims.",
        },
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
    rows, raw, newline = read_jsonl(ROOT / STATEMENTS)
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("Duplicate statement_id found")
    unresolved = {
        row["statement_id"] for row in rows
        if row.get("statement_id") in TARGET_IDS
        and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unresolved != TARGET_IDS:
        raise SystemExit(f"Target set changed: expected {sorted(TARGET_IDS)}, found {sorted(unresolved)}")
    with (ROOT / CANDIDATES).open(encoding="utf-8-sig", newline="") as stream:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(stream)}
    required_candidates = {"cand-2962", "cand-0166", "cand-4846", "cand-5718", "cand-2792", "cand-2036",
                           "cand-4830", "cand-5553", "cand-0417", "cand-4841", "cand-5712", "cand-5714",
                           "cand-5711", "cand-5713", "cand-5666", "cand-5699", "cand-5703"}
    if not required_candidates.issubset(candidate_ids):
        raise SystemExit(f"Missing candidate IDs: {sorted(required_candidates - candidate_ids)}")

    # Resolve the p.101 sentence fragment with its p.102 continuation.
    p101 = by_id["st-chp4-sec-ii-l24-31-veneration-fragment"]
    classify(p101, False, "The cross-page sentence is Haskell's scalar interpretation of Cassiano's antiquarian outlook; p.102 completes it with 'and historical interest.'")

    scalar_notes = {
        "st-chp4-sec-ii-l33-44-different-artistic-preference": "Haskell's scalar characterization of Cassiano's artistic preference; no bounded artist or group is identified.",
        "st-chp4-sec-ii-l33-44-early-taste-contrast": "Haskell's authorial comparison of taste over time; it does not assert a relation between two bounded entities.",
        "st-chp4-sec-ii-l33-44-galileo-scientific-attitude-and-taste": "Haskell's interpretation of Galileo's influence on aesthetic taste; the cited Panofsky passage has not been independently consulted.",
        "st-chp4-sec-ii-l33-44-interest-in-contemporary-painting": "Haskell's qualified scalar description ('almost as enthusiastic'), not a relation to a bounded entity.",
        "st-chp4-sec-ii-l33-44-wide-tastes": "Haskell's authorial interpretation of Cassiano's tastes; Vouet is contextual evidence, not the object of a relation in this sentence.",
    }
    for sid, note in scalar_notes.items():
        classify(by_id[sid], False, note)

    closure = by_id["st-chp4-sec-ii-l33-44-veneration-closure"]
    closure["original_quote"] = "and historical interest."
    closure["qualifiers"]["claim"] = "Haskell completes his previous-page characterization by saying Cassiano gave veneration of antiquity new precision and historical interest."
    closure["qualifiers"]["qualification"] = "This closes the p.101 sentence; the following sentence about organizing drawings is recorded separately. It remains Haskell's interpretation."
    classify(closure, False, "The cross-page sentence is Haskell's scalar interpretation of Cassiano's antiquarian outlook, not an entity relation.")

    # Atomize the Baldinucci list: source materials are not treated as objects owned by Cassiano.
    source_row = by_id["st-chp4-sec-ii-l33-44-fifth-volume-image-sources"]
    source_row["subject_candidate_id"] = "cand-5666"
    source_row["object_candidate_id"] = "cand-5699"
    source_row["predicate"] = "contains_figures_derived_from_source"
    source_row["original_quote"] = "figures taken from the ancient manuscripts of Virgil and Terence in the Vatican"
    source_row["qualifiers"].update({
        "claim": "Haskell, quoting Baldinucci, reports that figures in the fifth volume of Cassiano's paper-museum corpus were derived from an unidentified group of ancient Vatican manuscripts of Virgil and Terence.",
        "qualification": "The manuscripts are reported as image sources; the text does not say Cassiano owned or held them. Their individual identities are unknown; Baldinucci's cited page was not independently consulted.",
        "mentioned_candidate_ids": ["cand-5666", "cand-5699", "cand-2777", "cand-5700", "cand-3399"],
        "relation_candidate": True,
        "relation_candidate_note": "A source-bounded relation between the paper-museum volume's figures and their manuscript source; it does not place the manuscripts in Cassiano's collection.",
    })
    new_rows = [{
        "statement_id": "st-chp4-sec-ii-l33-44-fifth-volume-mosaic-source",
        "segment_id": "chp-4:04_CHP-4_sec_ii:l33-44",
        "subject_candidate_id": "cand-5666",
        "object_candidate_id": "cand-5703",
        "predicate": "contains_figures_derived_from_source",
        "qualifiers": {
            "source_line_start": 35, "source_line_end": 35, "claim": "Haskell, quoting Baldinucci, reports that figures in the fifth volume of Cassiano's paper-museum corpus were derived from a mosaic from the Temple of Fortune at Preneste.",
            "speaker": "Haskell quoting Filippo Baldinucci", "text_layer": "nested quotation", "pdf_physical_page": 9,
            "printed_page_locator": "p.102", "mentioned_candidate_ids": ["cand-5666", "cand-5703", "cand-5701", "cand-5702"],
            "qualification": "The mosaic is identified only as a source for figures; the text does not say Cassiano owned or held it. No present location is supplied, and Baldinucci's cited page was not independently consulted.",
            "relation_candidate": True,
            "relation_candidate_note": "A source-bounded relation between the fifth volume's figures and their mosaic source; it does not place the mosaic in Cassiano's collection.",
        },
        "original_quote": "the mosaic from the Temple of Fortune at Preneste, known today as Palestrina",
        "origin": "book", "source_file": SOURCE.as_posix(),
    }, {
        "statement_id": "st-chp4-sec-ii-l33-44-fifth-volume-other-coloured-items",
        "segment_id": "chp-4:04_CHP-4_sec_ii:l33-44",
        "subject_candidate_id": "cand-5666", "object_candidate_id": None,
        "predicate": "other_coloured_items_in_fifth_volume",
        "qualifiers": {
            "source_line_start": 35, "source_line_end": 35,
            "claim": "Baldinucci's quoted description adds other unspecified coloured items to the fifth volume's contents.",
            "speaker": "Haskell quoting Filippo Baldinucci", "text_layer": "nested quotation", "pdf_physical_page": 9,
            "printed_page_locator": "p.102", "mentioned_candidate_ids": ["cand-5666"],
            "qualification": "The additional items are not identified; the cited page was not independently consulted.",
            "relation_candidate": False,
            "relation_candidate_note": "This is a scalar contents statement with no bounded second entity.",
        },
        "original_quote": "and other things in colour.", "origin": "book", "source_file": SOURCE.as_posix(),
    }]

    # Classify and normalize the four p.102 footnote references.
    f1 = by_id["st-chp4-sec-ii-p102-footnote1-baldinucci"]
    f1["subject_candidate_id"] = "cand-2962"
    f1["predicate"] = "cites"
    f1["qualifiers"].update({"citation_candidate_id": "cand-0166", "citation_publication_candidate_id": "cand-4846",
                             "citation_locator": "Baldinucci, VI, 1728, p. 479", "cited_material_not_independently_consulted": True})
    classify(f1, True, "The book explicitly cites Baldinucci, volume VI, page 479; this is a citation pointer, not independent verification.")

    f2 = by_id["st-chp4-sec-ii-p102-footnote2-vouet-letters"]
    f2["subject_candidate_id"] = "cand-2962"
    f2["predicate"] = "cites"
    f2["qualifiers"].update({"citation_candidate_id": "cand-5718", "citation_locator": "letters from Vouet to Cassiano, 1621",
                             "cited_material_not_independently_consulted": True})
    classify(f2, True, "The footnote directs readers to the cited 1621 correspondence; neither the original letters nor their editions were independently consulted.")
    new_rows.append(citation_row("st-chp4-sec-ii-p102-footnote2-cites-bottari", "cand-4830", "cand-0417",
                                 "Bottari, I, pp. 331–333", f2["original_quote"], 247,
                                 "The locator is retained as printed; the cited pages were not independently consulted."))
    new_rows.append(citation_row("st-chp4-sec-ii-p102-footnote2-cites-demonts", "cand-5553", "cand-4841",
                                 "Demonts, p. 322", f2["original_quote"], 247,
                                 "The p.322 locator remains provisionally linked to the existing Demonts publication candidate used at p.314; identity and cited page are not independently verified."))

    f3 = by_id["st-chp4-sec-ii-p102-footnote3-panofsky"]
    f3["subject_candidate_id"] = "cand-2962"
    f3["predicate"] = "cites"
    f3["qualifiers"].update({"citation_candidate_id": "cand-5714", "citation_publication_candidate_id": "cand-5712",
                             "citation_locator": "Panofsky, 1954", "cited_material_not_independently_consulted": True})
    classify(f3, True, "The book explicitly directs readers to Panofsky (1954); the publication is a locator, not independent verification of the paragraph.")

    f4 = by_id["st-chp4-sec-ii-p102-footnote4-cigoli-galilei"]
    f4["subject_candidate_id"] = "cand-2962"
    f4["predicate"] = "cites"
    f4["qualifiers"].update({"citation_candidate_id": "cand-5711", "citation_locator": "Cigoli-Galilei Carteggio",
                             "cited_material_not_independently_consulted": True})
    classify(f4, True, "The footnote cites the Cigoli-Galilei correspondence edition; the edition was not independently consulted.")

    matteoli = by_id["st-chp4-sec-ii-p102-footnote4-matteoli-edited-carteggio"]
    classify(matteoli, True, "The note identifies Matteoli as editor of the correspondence edition; the name is supplied only by initial and surname and is not independently verified.")

    new_ids = {row["statement_id"] for row in new_rows}
    if new_ids & set(by_id):
        raise SystemExit(f"New statement IDs already exist: {sorted(new_ids & set(by_id))}")
    if "the mosaic from the Temple of Fortune at Preneste" not in source_text or "and other things in colour" not in source_text:
        raise SystemExit("Expected p.102 source phrases are missing")
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
