from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STATEMENTS = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_v.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-7.pdf"
SEGMENT = "chp-7:07_CHP-7_sec_v:l62-76"
PETERBOROUGH_RETURN = "st-chp7-p200-n1-peterborough-return-italy"
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp7-notes-l62-76-20261014")

EXPECTED_HASHES = {
    STATEMENTS.name: "c1cd1b23aa233adfccbe57279e1065830f7e0e8ca12134347c8beb761368272a",
    CANDIDATES.name: "ed1a698cad783887d9f511972c329cd1a649b1d1ab924255ad996893675020c3",
    MENTIONS.name: "8976f979a97de735298020f8438d40eeba2e37b02e54901d308322393a21ccea",
    SEGMENTS.name: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE.name: "956054d03a849749a1f7a0dbf0eade81c5cb1252a284cc26d024a7f9f134b432",
    PDF.name: "eebc3db682bd604e3f346f9908aa73977595daf925ac79ab2b3a92e437410212",
}
EXPECTED_SEGMENT_SHA = "c12f66ed101e3e1242ee863be622eb0d3c0e46f006a80aae42f777a419dad832"

CITATIONS = {
    "st-chp7-p200-n1-cite-soprani": {
        "publication": "cand-5160", "locator": "vol. II, p. 120",
        "claim": "Haskell's p.200 footnote 1 cites Soprani, vol. II, p.120, in connection with the possible Peterborough identification.",
        "qualification": "The printed volume numeral is II, confirmed on CHP-7.pdf physical p.38; the cited page was not independently read.",
    },
    "st-chp7-p200-n1-cite-zanotti": {
        "publication": "cand-7115", "locator": "vol. I, p. 309",
        "claim": "Haskell's p.200 footnote 1 cites Zanotti, vol. I, p.309, after the statement about Peterborough commissioning pictures from dal Sole.",
        "qualification": "Bibliographic pointer only; the cited page was not independently read.",
    },
    "st-chp7-p200-n2-cite-soprani": {
        "publication": "cand-5160", "locator": "vol. II, p. 115",
        "claim": "Haskell's p.200 footnote 2 cites Soprani, vol. II, p.115, for the de Ferrari and Noailles passage.",
        "qualification": "The printed volume numeral is II, confirmed on CHP-7.pdf physical p.38; the cited page was not independently read.",
    },
    "st-chp7-p200-n3-cite-de-dominici": {
        "publication": "cand-4835", "locator": "vol. IV, p. 321",
        "claim": "Haskell's p.200 footnote 3 cites de Dominici, vol. IV, p.321, for d'Estrées's arrival in Naples.",
        "qualification": "Bibliographic pointer only; the cited page was not independently read.",
    },
    "st-chp7-p200-n3-cite-loret": {
        "publication": "cand-6583", "locator": "p. 543",
        "claim": "Haskell's p.200 footnote 3 cites Loret, p.543, for de Matteis's work for Crozat in Paris.",
        "qualification": "Bibliographic pointer only; the cited page was not independently read.",
    },
    "st-chp7-p200-n4-cite-bologna": {
        "publication": "cand-7348", "locator": "p. 191",
        "claim": "Haskell's p.200 footnote 4 cites Bologna, p.191, for the 1715 invitation to Solimena.",
        "qualification": "Bibliographic pointer only; the cited page was not independently read.",
    },
    "st-chp7-p200-n5-cite-archivio": {
        "publication": "cand-7347", "locator": "1906, p. 453",
        "claim": "Haskell's p.200 footnote 5 cites the Archivio Storico per le Province Napoletane (1906), p.453, for the report that 'Binchs' was back in Naples in 1719.",
        "qualification": "The article title and author are unspecified in this note; the cited page was not independently read.",
    },
    "st-chp7-p200-n5-cite-de-dominici": {
        "publication": "cand-4835", "locator": "vol. IV, pp. 258 and 336",
        "claim": "Haskell's p.200 footnote 5 cites de Dominici, vol. IV, pp.258 and 336.",
        "qualification": "Bibliographic pointer only; the cited pages were not independently read.",
    },
    "st-chp7-p200-n7-cite-de-dominici": {
        "publication": "cand-4835", "locator": "vol. IV, pp. 46, 439, 441, 444, 571",
        "claim": "Haskell's p.200 footnote 7 cites de Dominici, vol. IV, pp.46, 439, 441, 444, and 571, for Harrach's patronage and collection.",
        "qualification": "Bibliographic pointer only; the cited pages were not independently read.",
    },
    "st-chp7-p200-n7-cite-ritschl": {
        "publication": "cand-7352", "locator": "passim",
        "claim": "Haskell's p.200 footnote 7 cites Ritschl, passim, on Harrach's surviving picture collection.",
        "qualification": "The catalogue and its entries were not independently consulted.",
    },
    "st-chp7-p201-n1-cite-zanotti-i": {
        "publication": "cand-7115", "locator": "vol. I, p. 302",
        "claim": "Haskell's p.201 footnote 1 cites Zanotti, vol. I, p.302, for the Bologna pictures associated with Crespi and dal Sole.",
        "qualification": "Bibliographic pointer only; the cited page was not independently read.",
    },
    "st-chp7-p201-n1-cite-zanotti-ii": {
        "publication": "cand-7115", "locator": "vol. II, p. 45",
        "claim": "Haskell's p.201 footnote 1 also cites Zanotti, vol. II, p.45.",
        "qualification": "The printed volume and page are II and 45, confirmed on CHP-7.pdf physical p.43; the cited page was not independently read.",
    },
    "st-chp7-p201-n2-cite-baudi": {
        "publication": "cand-7351", "locator": "1886, pp. 161–256",
        "claim": "Haskell's p.201 footnote 2 cites Baudi di Vesme (1886), pp.161–256, for the fate of Eugene's picture collection.",
        "qualification": "The cited study was not independently read.",
    },
    "st-chp7-p201-n2-cite-ilg": {
        "publication": "cand-7349", "locator": "passim",
        "claim": "Haskell's p.201 footnote 2 cites Ilg, passim.",
        "qualification": "The printed author name is Ilg, confirmed on CHP-7.pdf physical p.43; the cited work was not independently read.",
    },
    "st-chp7-p201-n2-cite-tietze": {
        "publication": "cand-7350", "locator": "pp. 891–907",
        "claim": "Haskell's p.201 footnote 2 cites Tietze, pp.891–907.",
        "qualification": "The cited pages were not independently read.",
    },
    "st-chp7-p201-n3-cite-zanotti": {
        "publication": "cand-7115", "locator": "vol. I, p. 275",
        "claim": "Haskell's p.201 footnote 3 cites Zanotti, vol. I, p.275, for Eugene's contemporary reputation as a protector of the fine arts.",
        "qualification": "Bibliographic pointer only; the cited page was not independently read.",
    },
    "st-chp7-p201-n4-cite-zanotti": {
        "publication": "cand-7115", "locator": "vol. I, p. 302; vol. II, p. 43",
        "claim": "Haskell's p.201 footnote 4 continues the Zanotti citation, vol. I, p.302 and vol. II, p.43.",
        "qualification": "Ibid. resolves to Zanotti as cited in footnote 3; the cited pages were not independently read.",
    },
    "st-chp7-p201-n5-cite-de-dominici": {
        "publication": "cand-4835", "locator": "vol. IV, pp. 432–433, 439",
        "claim": "Haskell's p.201 footnote 5 cites de Dominici, vol. IV, pp.432–433 and 439.",
        "qualification": "Bibliographic pointer only; the cited pages were not independently read.",
    },
    "st-chp7-p201-n6-cite-zanotti": {
        "publication": "cand-7115", "locator": "vol. II, p. 234",
        "claim": "Haskell's p.201 footnote 6 cites Zanotti, vol. II, p.234, for the Boni commission.",
        "qualification": "Bibliographic pointer only; the cited page was not independently read.",
    },
    "st-chp7-p202-n1-cite-claretta": {
        "publication": "cand-4995", "locator": "1893, pp. 1–309",
        "claim": "Haskell's p.202 footnote 1 cites Claretta (1893), pp.1–309, in the discussion of Savoy's transformation and artistic flowering.",
        "qualification": "The printed year is 1893, confirmed on CHP-7.pdf physical p.44; the cited pages were not independently read. The publication title remains unspecified pending bibliography review.",
    },
}

TRUE_NOTES = {
    "st-chp7-p200-n1-peterborough-travel": "This records the first Italy trip attributed to Peterborough in Haskell's footnote; it does not establish that the body figure 'Pekemburgh' was Peterborough.",
    "st-chp7-p200-n1-possible-peterborough": "This preserves Haskell's explicitly tentative identification of Admiral 'Pekemburgh' with the 3rd Earl of Peterborough; the two candidates remain distinct pending S3 alignment.",
    "st-chp7-p200-n3-destrees-arrival": "This records the footnote's report of d'Estrées's arrival in Naples in 1702; de Dominici's cited page was not independently read.",
    "st-chp7-p200-n3-matteis-crozat": "This records the source's report that de Matteis worked for Crozat in Paris among other patrons; no particular work or date is inferred.",
    "st-chp7-p200-n4-orleans-in-artlovers": "This records Haskell's identification of d'Orléans as one of the younger art lovers discussed in the preceding body passage; it does not imply membership in an organization.",
    "st-chp7-p200-n4-orleans-invites-solimena": "This records the reported 1715 invitation of Solimena to Paris by d'Orléans; the cited page was not independently read.",
    "st-chp7-p200-n4-orleans-patronage": "This records Haskell's description of d'Orléans as an important patron of contemporary Italian art; it does not infer commissions beyond the separately recorded invitation.",
    "st-chp7-p200-n5-binchs-identified-byng": "This preserves Haskell's inference that 'Binchs' must be Admiral Byng; the source-form and named candidates are not merged in S2.",
    "st-chp7-p200-n5-binchs-return-naples": "This records the footnote's report that the person called 'Binchs' was back in Naples in 1719; the possible Byng identity remains attributed and unresolved.",
    "st-chp7-p200-n5-byng-fleet-command": "This records Haskell's report that Admiral Byng commanded the British fleet in the Mediterranean from 1718; the relationship to the source-form 'Binchs' remains an attributed inference.",
    "st-chp7-p200-n7-harrach-patronage": "This preserves Haskell's superlative characterization of Harrach as an Austrian patron of Neapolitan art, with his surviving collection as the cited context.",
    "st-chp7-p201-n2-eugene-collection-acquired": "This records Haskell's report that much of Eugene's picture collection was bought by Carlo Emanuele III; preserve 'much of' and the second-hand citation status.",
}

EXISTING_TRUE_NOTES = {
    "st-chp7-p200-n1-peterborough-commissions-dal-sole": "This records Haskell's statement that Peterborough certainly commissioned a number of pictures from dal Sole during the longer stay; the cited page was not independently read.",
}

EXPECTED_UNSET_IDS = {
    "st-chp7-p200-n1-cite-soprani", "st-chp7-p200-n1-cite-zanotti",
    "st-chp7-p200-n1-peterborough-travel", "st-chp7-p200-n1-possible-peterborough",
    "st-chp7-p200-n2-cite-soprani", "st-chp7-p200-n3-cite-de-dominici",
    "st-chp7-p200-n3-cite-loret", "st-chp7-p200-n3-destrees-arrival",
    "st-chp7-p200-n3-matteis-crozat", "st-chp7-p200-n4-cite-bologna",
    "st-chp7-p200-n4-orleans-in-artlovers", "st-chp7-p200-n4-orleans-invites-solimena",
    "st-chp7-p200-n4-orleans-patronage", "st-chp7-p200-n5-binchs-identified-byng",
    "st-chp7-p200-n5-binchs-return-naples", "st-chp7-p200-n5-byng-fleet-command",
    "st-chp7-p200-n5-cite-archivio", "st-chp7-p200-n5-cite-de-dominici",
    "st-chp7-p200-n7-cite-de-dominici", "st-chp7-p200-n7-cite-ritschl",
    "st-chp7-p200-n7-harrach-patronage", "st-chp7-p201-n1-cite-zanotti-i",
    "st-chp7-p201-n1-cite-zanotti-ii", "st-chp7-p201-n2-cite-baudi",
    "st-chp7-p201-n2-cite-ilg", "st-chp7-p201-n2-cite-tietze",
    "st-chp7-p201-n2-eugene-collection-acquired", "st-chp7-p201-n3-cite-zanotti",
    "st-chp7-p201-n4-cite-zanotti", "st-chp7-p201-n5-cite-de-dominici",
    "st-chp7-p201-n6-cite-zanotti", "st-chp7-p202-n1-cite-claretta",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after all guards pass")
    args = parser.parse_args()

    paths = [STATEMENTS, CANDIDATES, MENTIONS, SEGMENTS, SOURCE, PDF]
    raw = {path: path.read_bytes() for path in paths}
    hashes = {path.name: sha(data) for path, data in raw.items()}
    if hashes != EXPECTED_HASHES:
        raise SystemExit(f"input hashes changed: {hashes}")
    if BACKUP.exists():
        raise SystemExit(f"recovery copy already exists: {BACKUP}")

    with SEGMENTS.open("r", encoding="utf-8") as stream:
        segment_rows = [json.loads(line) for line in stream]
    segment = next(row for row in segment_rows if row["segment_id"] == SEGMENT)
    if segment.get("sha256") != EXPECTED_SEGMENT_SHA:
        raise SystemExit("footnote segment hash changed")
    source_text = raw[SOURCE].decode("utf-8")
    for excerpt in (
        "Soprani, H, p. 120", "Soprani, II, p. 115...", "and H, p. 4$",
        "Ug, passim", "Claretta, i893, pp. 1-309",
        "In Bergamo he commissioned his portrait from Vittore Gliislandi",
    ):
        if excerpt not in source_text:
            raise SystemExit(f"source excerpt not found: {excerpt!r}")

    rows = [json.loads(line) for line in raw[STATEMENTS].decode("utf-8").splitlines()]
    by_id = {row["statement_id"]: row for row in rows}
    segment_rows = [row for row in rows if row.get("segment_id") == SEGMENT]
    segment_ids = {row["statement_id"] for row in segment_rows}
    if len(segment_rows) != 33 or segment_ids != EXPECTED_UNSET_IDS | {"st-chp7-p200-n1-peterborough-commissions-dal-sole"}:
        raise SystemExit("footnote statement set changed")
    unset_ids = {row["statement_id"] for row in segment_rows if (row.get("qualifiers") or {}).get("relation_candidate") is None}
    if unset_ids != EXPECTED_UNSET_IDS:
        raise SystemExit(f"expected unset rows changed: {sorted(unset_ids ^ EXPECTED_UNSET_IDS)}")
    if set(CITATIONS) | set(TRUE_NOTES) != EXPECTED_UNSET_IDS:
        raise SystemExit("classification map does not cover the exact unset set")

    new_row_id = PETERBOROUGH_RETURN
    if new_row_id in by_id:
        raise SystemExit(f"new statement id already exists: {new_row_id}")
    if any(publication not in {row.get("object_candidate_id") for row in segment_rows} for publication in [info["publication"] for info in CITATIONS.values()]):
        raise SystemExit("citation publication endpoint mismatch in footnote segment")

    # Split the two separate trips to Italy; preserve Peterborough's possible relation to the body figure as unresolved.
    travel = by_id["st-chp7-p200-n1-peterborough-travel"]
    travel["object_candidate_id"] = "cand-3461"
    travel["predicate"] = "arrived_in_italy_from_spain_in_1707_for_a_few_months"
    travel["original_quote"] = "who arrived in Italy from Spain for a few months in 1707"
    tq = dict(travel.get("qualifiers") or {})
    tq.update({
        "claim": "The note says the 3rd Earl of Peterborough arrived in Italy from Spain for a few months in 1707.",
        "qualification": "This records only the first trip; a later, longer return is stored separately. These biographical details do not establish that the body figure 'Pekemburgh' was Peterborough.",
        "origin_place_candidate_id": "cand-5120", "year": 1707, "duration": "a few months",
    })
    travel["qualifiers"] = tq

    new_return = {
        "statement_id": new_row_id, "segment_id": SEGMENT,
        "subject_candidate_id": "cand-1891", "object_candidate_id": "cand-3461",
        "predicate": "returned_to_italy_for_a_longer_period_in_the_next_decade",
        "qualifiers": {
            "source_line_start": 63, "source_line_end": 63, "printed_page": 200, "pdf_physical_page": 38,
            "claim": "The note says Peterborough returned to Italy for a much longer period in the next decade.",
            "speaker": "Haskell footnote", "text_layer": "footnote",
            "qualification": "The source does not give exact dates; the passage remains within Haskell's possible identification of 'Pekemburgh' as Peterborough.",
            "footnote_marker": 1, "footnote_segment": SEGMENT,
            "related_segment": "chp-7:07_CHP-7_sec_v:l9-18", "related_source_lines": [11],
            "linked_body_statement_ids": list(tq.get("linked_body_statement_ids") or []),
            "mentioned_candidate_ids": ["cand-1891", "cand-5120", "cand-3461"],
            "relation_candidate": True,
            "relation_candidate_note": "This separates the later return to Italy from the earlier 1707 arrival and preserves the footnote's possible-identity context.",
        },
        "original_quote": "then returned for a much longer period in the next decade",
        "origin": "book", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
    }

    # The p.200 Soprani locator is volume II, not volume I; p.201 note 1's OCR corrections belong only to its second locator.
    soprani_1 = by_id["st-chp7-p200-n1-cite-soprani"]["qualifiers"]
    soprani_1["ocr_corrections"] = [{"source_line": 63, "ocr": "H", "reading": "II", "basis": "CHP-7.pdf physical p.38"}]
    soprani_2 = by_id["st-chp7-p200-n2-cite-soprani"]["qualifiers"]
    soprani_2["ocr_corrections"] = [
        {"source_line": 64, "ocr": "...", "reading": ".", "basis": "CHP-7.pdf physical p.38"},
    ]
    by_id["st-chp7-p201-n1-cite-zanotti-i"]["qualifiers"].pop("ocr_corrections", None)
    by_id["st-chp7-p201-n1-cite-zanotti-ii"]["qualifiers"]["ocr_corrections"] = [
        {"source_line": 70, "ocr": "H", "reading": "II", "basis": "CHP-7.pdf physical p.43"},
        {"source_line": 70, "ocr": "4$", "reading": "45", "basis": "CHP-7.pdf physical p.43"},
    ]

    # Repair S2-local endpoint details without resolving identities or consulting cited works.
    by_id["st-chp7-p200-n3-matteis-crozat"]["qualifiers"]["work_location_candidate_id"] = "cand-4653"
    by_id["st-chp7-p200-n4-orleans-invites-solimena"]["qualifiers"]["invitation_location_candidate_id"] = "cand-4653"
    by_id["st-chp7-p200-n5-byng-fleet-command"]["qualifiers"]["reported_start_year"] = 1718
    by_id["st-chp7-p200-n1-peterborough-commissions-dal-sole"]["qualifiers"]["relation_candidate_note"] = EXISTING_TRUE_NOTES["st-chp7-p200-n1-peterborough-commissions-dal-sole"]

    for sid, note in TRUE_NOTES.items():
        row = by_id[sid]
        q = dict(row.get("qualifiers") or {})
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note
        q["related_body_statement_ids"] = list(q.get("linked_body_statement_ids") or [])
        q["footnote_link_status"] = "linked"
        q["footnote_body_link_status"] = "linked"
        q["footnote_text_pending"] = False
        row["qualifiers"] = q
    for sid, note in EXISTING_TRUE_NOTES.items():
        q = dict(by_id[sid].get("qualifiers") or {})
        q["relation_candidate_note"] = note
        q["related_body_statement_ids"] = list(q.get("linked_body_statement_ids") or [])
        q["footnote_link_status"] = "linked"
        q["footnote_body_link_status"] = "linked"
        q["footnote_text_pending"] = False
        by_id[sid]["qualifiers"] = q

    for sid, info in CITATIONS.items():
        row = by_id[sid]
        q = dict(row.get("qualifiers") or {})
        publication = info["publication"]
        marker = q.get("footnote_marker")
        q.update({
            "claim": info["claim"],
            "speaker": "Haskell footnote",
            "text_layer": "bibliographic citation to publication",
            "qualification": info["qualification"],
            "mentioned_candidate_ids": list(dict.fromkeys([publication, "cand-2962", *(q.get("mentioned_candidate_ids") or [])])),
            "citations": [{"source_candidate_id": "cand-2962", "publication_candidate_id": publication, "locator": info["locator"]}],
            "citation_publication_candidate_id": publication,
            "citation_locator": info["locator"],
            "cited_material_not_independently_consulted": True,
            "relation_candidate": True,
            "relation_candidate_note": info["claim"] + " The cited material was not independently consulted.",
            "footnote_number": marker,
            "related_body_statement_ids": list(q.get("linked_body_statement_ids") or []),
            "footnote_link_status": "linked",
            "footnote_body_link_status": "linked",
            "footnote_text_pending": False,
        })
        row["subject_candidate_id"] = "cand-2962"
        row["object_candidate_id"] = publication
        row["predicate"] = "cites"
        row["qualifiers"] = q

    # The Soprani pointer covers both halves of the now-atomic trip history.
    soprani_cite = by_id["st-chp7-p200-n1-cite-soprani"]["qualifiers"]
    for field in ("linked_body_statement_ids", "related_body_statement_ids"):
        values = list(soprani_cite.get(field) or [])
        if new_row_id not in values:
            values.append(new_row_id)
        soprani_cite[field] = values

    rows.append(new_return)
    output = [by_id.get(row["statement_id"], row) for row in rows]
    # Existing rows were mutated in place; replace the appended row with its normalized object.
    output[-1] = new_return

    counts = {
        "statements": len(output),
        "true": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in output),
        "false": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in output),
        "unset": sum((row.get("qualifiers") or {}).get("relation_candidate") is None for row in output),
    }
    if counts != {"statements": 14202, "true": 8844, "false": 3439, "unset": 1919}:
        raise SystemExit(f"unexpected post-counts: {counts}")
    for sid, info in CITATIONS.items():
        row = by_id[sid]
        q = row["qualifiers"]
        if (row["subject_candidate_id"], row["object_candidate_id"], row["predicate"]) != ("cand-2962", info["publication"], "cites"):
            raise SystemExit(f"citation endpoints not normalized: {sid}")
        if q.get("citation_locator") != info["locator"] or not q.get("cited_material_not_independently_consulted"):
            raise SystemExit(f"citation locator/status error: {sid}")

    after = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in output) + "\n").encode("utf-8")
    report = {
        "mode": "apply" if args.apply else "dry_run", "segment": SEGMENT,
        "classified_unset_true": len(EXPECTED_UNSET_IDS), "existing_true_refined": 1,
        "normalized_citations": len(CITATIONS), "new_atomic_statements": 1,
        "corrections": {
            "p200_soprani_volume": "II confirmed on physical p.38",
            "p201_zanotti_second_locator": "II, p.45 confirmed on physical p.43",
            "p201_ilg_name": "Ilg confirmed on physical p.43",
            "p202_claretta_year": "1893 confirmed on physical p.44",
        },
        "post_counts": counts, "input_sha256": hashes,
        "after_statement_sha256": sha(after), "backup": str(BACKUP.relative_to(ROOT)),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files changed")
        return

    BACKUP.write_bytes(raw[STATEMENTS])
    atomic_write(STATEMENTS, after)
    if sha(STATEMENTS.read_bytes()) != report["after_statement_sha256"]:
        raise SystemExit("post-write statement hash mismatch")
    print("applied; recovery copy written; statement hash verified")


if __name__ == "__main__":
    main()
