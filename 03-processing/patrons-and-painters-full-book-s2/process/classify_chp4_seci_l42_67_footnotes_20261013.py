from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
SEGMENT_ID = "chp-4:04_CHP-4_sec_i:l42-67"
EXPECTED_STATEMENTS_SHA256 = "6b1ead355011b5fb35c3d64f6eb530f2fcf90ef087cf1491dd2668a9066ff2e4"
EXPECTED_CANDIDATES_SHA256 = "00c7ebc8ed902d545128e996f2bdcdd3dd9327cdd443c847d0401dbf39bcce82"
EXPECTED_MENTIONS_SHA256 = "0644450cf12abbb2bc56f06996101c4e443b2ece528fc7349788b99b1b7f04cf"
SEGMENT_SHA256 = "d12bc7787254f570c78f5c7d2d051fe844e6b343b4b60ac33b4dae4d094960f9"
NEW_STATEMENT_ID = "st-chp4-sec-i-l42-67-claude-picture-recorded-in-liber-veritatis"
FALSE_NOTES = {
    "st-chp4-sec-i-l42-67-fn95-age-citations": "Nonrelation: these are bibliographic locators supporting the preceding succession and age account; the citation does not assert a separate entity relation.",
    "st-chp4-sec-i-l42-67-fn95-medici-court-citation": "Nonrelation: this records Haskell's source locator for the Medici-court passage, not a separate historical relation.",
    "st-chp4-sec-i-l42-67-fn96-leoni-citation": "Nonrelation: this is a bibliographic locator for Bartsch, not a separate relation involving the etching.",
    "st-chp4-sec-i-l42-67-fn96-monteverdi-citation": "Nonrelation: this is a bibliographic locator for Prunières, not a separate relation involving Monteverdi.",
    "st-chp4-sec-i-l42-67-fn96-poetry-publication": "Nonrelation: the statement records bibliographic identification and publication metadata for Paolo Giordano II's poetry volume, followed by citations; it adds no entity-to-entity relation.",
    "st-chp4-sec-i-l42-67-fn96-rosidra-citation": "Nonrelation: this is a bibliographic locator for Mandosio after the instrument is named; it does not independently assert a relation.",
    "st-chp4-sec-i-l42-67-fn97-bronze-note": "Nonrelation: this reports the bronze's loss and Haskell's literature-search result, a work-status and historiographic statement rather than an entity edge.",
    "st-chp4-sec-i-l42-67-fn97-bust-dating": "Nonrelation: this records attributed date assessments of the busts; the dates and disagreement remain scalar work claims.",
    "st-chp4-sec-i-l42-67-fn97-christina-correspondence-source": "Nonrelation: this records Haskell's de Bildt citation for the correspondence, not a separate historical relation.",
    "st-chp4-sec-i-l42-67-fn97-church-archive-citation": "Nonrelation: this is an archival locator for the church-decoration note; the cited folios were not independently inspected.",
    "st-chp4-sec-i-l42-67-fn97-claude-picture-record": "Nonrelation/parent statement: the painting's loss and probable date remain scalar claims; its explicit record in Liber Veritatis no. 33 is represented by a separate relation candidate below.",
    "st-chp4-sec-i-l42-67-fn97-isabella-portrait-date": "Nonrelation: this reports Wittkower's workshop and approximate-date assessment of a portrait; it is a work-level attribution, not an entity relation.",
    "st-chp4-sec-i-l42-67-fn97-medal-archive-citation": "Nonrelation: this is an archival locator for the medal-collecting note; the cited letters were not independently inspected.",
    "st-chp4-sec-i-l42-67-fn97-medal-citation": "Nonrelation: this records Haskell's citation to Dworschak; the possible maker attribution remains a separate qualified claim.",
    "st-chp4-sec-i-l42-67-fn97-podesta-citation": "Nonrelation: this directs the reader to Blunt's article and does not assert a separate relation involving Podestà.",
    "st-chp4-sec-i-l42-67-fn97-tacca-no-reference": "Nonrelation: this reports Haskell's literature-search result and publication of a letter, not a separate entity relation.",
    "st-chp4-sec-i-l42-67-fn98-christina-ceremonies-source": "Nonrelation: this is the bibliographic locator for the ceremonies and concert account.",
    "st-chp4-sec-i-l42-67-fn98-dilettante-source": "Nonrelation: this is the bibliographic locator for Baglione after Haskell's dilettante characterization.",
}
PREDICATES = {
    "st-chp4-sec-i-l42-67-fn95-age-citations": "cites_sources_for_reported_succession_and_age",
    "st-chp4-sec-i-l42-67-fn95-medici-court-citation": "cites_source_for_medici_court_life",
    "st-chp4-sec-i-l42-67-fn96-leoni-citation": "cites_source_for_leoni_etching",
    "st-chp4-sec-i-l42-67-fn96-monteverdi-citation": "cites_source_for_monteverdi_reference",
    "st-chp4-sec-i-l42-67-fn96-poetry-publication": "publication_identification_and_citations_reported",
    "st-chp4-sec-i-l42-67-fn96-rosidra-citation": "cites_source_for_rosidra",
    "st-chp4-sec-i-l42-67-fn97-bronze-note": "reported_absence_from_berniniana",
    "st-chp4-sec-i-l42-67-fn97-bust-dating": "bust_dating_attributed_to_faldi",
    "st-chp4-sec-i-l42-67-fn97-christina-correspondence-source": "cites_de_bildt_for_christina_correspondence",
    "st-chp4-sec-i-l42-67-fn97-church-archive-citation": "cited_archival_sources_for_church_decoration",
    "st-chp4-sec-i-l42-67-fn97-claude-picture-record": "lost_picture_record_and_probable_date_reported",
    "st-chp4-sec-i-l42-67-fn97-isabella-portrait-date": "portrait_assessment_and_date_attributed_to_wittkower",
    "st-chp4-sec-i-l42-67-fn97-medal-archive-citation": "cited_archival_sources_for_medal_collecting",
    "st-chp4-sec-i-l42-67-fn97-medal-citation": "cites_source_for_medal",
    "st-chp4-sec-i-l42-67-fn97-podesta-citation": "cites_blunt_for_podesta",
    "st-chp4-sec-i-l42-67-fn97-tacca-no-reference": "author_reports_no_reference_in_tacca_literature",
    "st-chp4-sec-i-l42-67-fn98-christina-ceremonies-source": "cites_gualdo_priorato_for_christina_visit",
    "st-chp4-sec-i-l42-67-fn98-dilettante-source": "cites_baglione_for_dilettante_status",
}
BACKUP = STATEMENTS.with_name("book-statements.jsonl.bak-s2-chp4-seci-l42-67-footnotes-20261013")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify chapter 4 footnote citations and isolate the Liber Veritatis record relation.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview checks")
    args = parser.parse_args()

    raw = STATEMENTS.read_bytes()
    if sha256(raw) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("protected statement table changed")
    if sha256(CANDIDATES.read_bytes()) != EXPECTED_CANDIDATES_SHA256:
        raise SystemExit("protected candidate table changed")
    mentions_raw = MENTIONS.read_bytes()
    if sha256(mentions_raw) != EXPECTED_MENTIONS_SHA256:
        raise SystemExit("protected mention table changed")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected S0 segment metadata changed")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(source_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected S0 source segment changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    unset = {
        row.get("statement_id") for row in rows
        if row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if unset != set(FALSE_NOTES):
        raise SystemExit(f"protected segment unset set changed: {sorted(unset)}")
    if NEW_STATEMENT_ID in by_id:
        raise SystemExit("new relation statement ID already exists")
    for statement_id, note in FALSE_NOTES.items():
        row = by_id[statement_id]
        if row.get("predicate") != PREDICATES[statement_id]:
            raise SystemExit(f"protected predicate changed: {statement_id}")
        row["qualifiers"]["relation_candidate"] = False
        row["qualifiers"]["relation_candidate_note"] = note

    parent = by_id["st-chp4-sec-i-l42-67-fn97-claude-picture-record"]
    parent["qualifiers"]["related_statement_ids"] = [NEW_STATEMENT_ID]
    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-5556",
        "object_candidate_id": "cand-5617",
        "predicate": "recorded_in",
        "qualifiers": {
            "source_line_start": 58,
            "source_line_end": 58,
            "claim": "Haskell reports that Röthlisberger records the lost Claude painting in Liber Veritatis no. 33.",
            "speaker": "Haskell reporting Röthlisberger's catalogue statement",
            "text_layer": "authorial footnote",
            "qualification": "The numbered entry itself has not been independently inspected; the source also presents the painting's 1638–39 date as probable.",
            "footnote_marker": "7",
            "mentioned_candidate_ids": ["cand-5556", "cand-3502", "cand-5617"],
            "relation_candidate": True,
            "relation_candidate_note": "S2 candidate: the source explicitly says the lost A Storm at Sea is recorded as Liber Veritatis no. 33; no formal S6 edge is created.",
        },
        "original_quote": "The picture has been lost, but it is recorded in the Liber Veritatis, No. 33.",
        "origin": "book",
        "source_file": segment["source_file"],
    }
    if not any(
        row.get("segment_id") == SEGMENT_ID
        and row.get("candidate_id") == "cand-5617"
        and row.get("surface_form") == "Liber Veritatis, No. 33"
        and row.get("start_char") == "1717"
        and row.get("end_char") == "1740"
        for row in csv.DictReader(io.StringIO(mentions_raw.decode("utf-8-sig"), newline=""))
    ):
        raise SystemExit("protected Liber Veritatis mention mapping changed")
    if not any(row.get("candidate_id") == "cand-5556" for row in csv.DictReader(io.StringIO(CANDIDATES.read_text(encoding="utf-8-sig"), newline=""))):
        raise SystemExit("Claude painting candidate missing")
    rows.append(new_statement)
    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered

    print(f"Chapter 4 section I L42-67 preview: {len(FALSE_NOTES)} citations/scalar/parent claims -> false")
    print(f"new relation candidate: {NEW_STATEMENT_ID} cand-5556 -> cand-5617 (recorded_in)")
    print(f"book-statements.jsonl: {sha256(raw)} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")
    shutil.copy2(STATEMENTS, BACKUP)
    temporary = STATEMENTS.with_name(STATEMENTS.name + ".tmp-s2-chp4-seci-l42-67-footnotes")
    temporary.write_bytes(rendered)
    temporary.replace(STATEMENTS)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
