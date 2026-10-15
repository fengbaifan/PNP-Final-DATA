#!/usr/bin/env python3
"""Atomize and link printed p.13 notes after protected S0/table checks.

Default mode is a read-only preview. Pass --apply to write the four S2 tables.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
NOTE_SEG = "chp-1:01_CHP-1_sec_ii:l168-239"
BODY_SEG = "chp-1:01_CHP-1_sec_ii:l73-77"
SOURCE_FULL = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md"
SOURCE_SEGMENT = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
OLD_IDS = {
    "st-chp1-secii-notes-advance-payment-cases",
    "st-chp1-secii-notes-payment-letters",
    "st-chp1-secii-notes-material-cost-allocation",
}
BACKUP_SUFFIX = ".bak-s2-chp1-secii-p13-notes-20261012"
EXPECTED = {
    "book-statements.jsonl": "4ce166c9e552322c87a38ceb564dc2985a674489867ae6874a1644c5b4947d35",
    "entity-candidates.csv": "fa6e12e7595b6e4e4f1fef8762aa3bcd99ac77c5202fe5dd3406c42555bc21ec",
    "mentions.csv": "50c674a26e83ac8b80b4ed8eaf5822a1d9420730d039e5610ab441b94e3f0722",
    "s2-coverage.csv": "da36ec28d0741274e8f4bd2536c32e0bd66446f0bad411c480c5de4eef36bc4e",
}
SOURCE_SHA = "2c99c1b372f756b1482d746f5714fe930b538118792b52a3de0834f585d4f3fb"
SEGMENT_ASSET_SHA = "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268"
SEGMENT_SHA = "b5560e20ceb3b9b531266ac26966dd0a7f76c6ce8bbc82f6664a9a95d68af258"
PRINT_PAGE = 13
PDF_PAGE = 12
MARKER_LINES = {1: 485, 2: 489, 3: 490, 4: 492, 5: 497, 6: 502}
BODY_IDS = {
    1: ["st-chp1-secii-l73-77-01"],
    2: ["st-chp1-secii-l73-77-02"],
    3: ["st-chp1-secii-l73-77-02"],
    4: ["st-chp1-secii-l73-77-02"],
    5: ["st-chp1-secii-l73-77-03"],
    6: ["st-chp1-secii-l73-77-06"],
}
P10_CAMASSEI_ID = "st-chp1-secii-p10-n1-camassei-artist-of-altarpiece"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_with_offsets(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    offsets: list[int] = []
    previous_space = False
    for index, char in enumerate(text):
        if char.isspace():
            if not previous_space:
                chars.append(" ")
                offsets.append(index)
            previous_space = True
        else:
            chars.append(char)
            offsets.append(index)
            previous_space = False
    return "".join(chars), offsets


def excerpt(lines: list[str], start: int, end: int, phrase: str) -> str:
    raw = "\n".join(lines[start - 1 : end])
    normalized, positions = normalize_with_offsets(raw)
    target = " ".join(phrase.split())
    offset = normalized.find(target)
    if offset < 0:
        raise ValueError(f"quote missing from S0 L{start}-{end}: {phrase}")
    return raw[positions[offset] : positions[offset + len(target) - 1] + 1]


def normalized_span(text: str, phrase: str, occurrence: int = 0) -> tuple[int, int, str]:
    normalized, positions = normalize_with_offsets(text)
    target = " ".join(phrase.split())
    cursor = 0
    offset = -1
    for _ in range(occurrence + 1):
        offset = normalized.find(target, cursor)
        if offset < 0:
            raise ValueError(f"mention phrase missing from flattened source segment: {phrase}")
        cursor = offset + len(target)
    start = positions[offset]
    end = positions[offset + len(target) - 1] + 1
    surface = text[start:end]
    if "\n" in surface or "\r" in surface:
        raise ValueError(f"mention surface crosses a source line: {phrase}")
    return start, end, surface


def append_unique(target: list, values: list) -> list:
    for value in values:
        if value not in target:
            target.append(value)
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all protected checks pass; default is preview")
    args = parser.parse_args()

    for name, expected in EXPECTED.items():
        path = TABLES / name
        actual = digest(path)
        if actual != expected:
            raise SystemExit(f"protected table changed: {name}: expected {expected}, found {actual}")
    if digest(SOURCE_FULL) != SOURCE_SHA:
        raise SystemExit("protected full S0 source file changed")
    if digest(SOURCE_SEGMENT) != SEGMENT_ASSET_SHA:
        raise SystemExit("protected S0 section file changed")

    tables = {name: TABLES / name for name in EXPECTED}
    statements = read_jsonl(tables["book-statements.jsonl"])
    candidates = read_csv(tables["entity-candidates.csv"])
    mentions = read_csv(tables["mentions.csv"])
    coverage = read_csv(tables["s2-coverage.csv"])
    full_lines = SOURCE_FULL.read_text(encoding="utf-8-sig").splitlines()
    section_lines = SOURCE_SEGMENT.read_text(encoding="utf-8-sig").splitlines()
    flat_note = " ".join(" ".join(section_lines[167:239]).split())

    segments = read_jsonl(TABLES / "segments.jsonl")
    segment = next((row for row in segments if row.get("segment_id") == NOTE_SEG), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SEGMENT_ASSET_SHA:
        raise SystemExit("protected note segment fingerprint changed")
    if len(full_lines) < 523 or len(section_lines) < 239:
        raise SystemExit("protected source range is incomplete")

    statement_by_id = {row["statement_id"]: row for row in statements}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    if len(statement_by_id) != len(statements) or len(candidate_by_id) != len(candidates):
        raise SystemExit("duplicate statement or candidate IDs in protected tables")
    if not OLD_IDS.issubset(statement_by_id):
        raise SystemExit("one or more expected p.13 broad statement rows are missing")
    if any(row["segment_id"] != NOTE_SEG for row in (statement_by_id[sid] for sid in OLD_IDS)):
        raise SystemExit("a broad statement row no longer belongs to the protected note segment")

    # Source passages are kept verbatim from S0; print corrections are only S2 qualifiers.
    corrections = {
        "albani": [{"source_line": 503, "ocr": "bere", "print": "here", "basis": "CHP-1.pdf physical page 12"}],
        "mola_payment": [
            {"source_line": 506, "ocr": "3 00", "print": "300", "basis": "CHP-1.pdf physical page 12"},
            {"source_line": 506, "ocr": "p. 2 8 7", "print": "p. 287", "basis": "CHP-1.pdf physical page 12"},
        ],
        "ferri_payment": [{"source_line": 508, "ocr": "Laparclli", "print": "Laparelli", "basis": "CHP-1.pdf physical page 12"}],
        "gessi": [{"source_line": 510, "ocr": "io July", "print": "10 July", "basis": "CHP-1.pdf physical page 12"}],
        "quarismini": [{"source_line": 512, "ocr": "Quarisinini", "print": "Quarismini", "basis": "CHP-1.pdf physical page 12"}],
        "camassei": [
            {"source_line": 514, "ocr": "Urban Vili", "print": "Urban VIII", "basis": "CHP-1.pdf physical page 12"},
            {"source_line": 514, "ocr": "sor", "print": "for", "basis": "CHP-1.pdf physical page 12"},
        ],
        "gavasetti": [{"source_line": 520, "ocr": "Iris frescoes", "print": "his frescoes", "basis": "CHP-1.pdf physical page 12"}],
        "cross_ref": [{"source_line": 514, "ocr": "p. io, note 1", "print": "p. 10, note 1", "basis": "CHP-1.pdf physical page 12"}],
    }

    def mk_statement(
        suffix: str,
        predicate: str,
        claim: str,
        start: int,
        end: int,
        phrase: str,
        marker: int,
        mentioned: list[str],
        *,
        subject: str | None = None,
        obj: str | None = None,
        relation: bool = True,
        relation_note: str = "S2 source-defined candidate only; this migration creates no S6 formal relation.",
        speaker: str | None = None,
        text_layer: str = "Haskell footnote / source-mediated claim",
        qualification: str = "The cited primary document/publication was not independently consulted.",
        extra: dict | None = None,
        correction_key: str | None = None,
    ) -> dict:
        body_ids = BODY_IDS[marker]
        line_refs = [MARKER_LINES[marker]]
        qualifiers = {
            "source_line_start": start,
            "source_line_end": end,
            "printed_page": PRINT_PAGE,
            "pdf_physical_page": PDF_PAGE,
            "claim": claim,
            "speaker": speaker or f"Haskell footnote {marker}",
            "text_layer": text_layer,
            "qualification": qualification,
            "relation_candidate": relation,
            "mentioned_candidate_ids": mentioned,
            "footnote_marker": marker,
            "footnote_number": marker,
            "footnote_segment": NOTE_SEG,
            "footnote_refs": [{"marker": marker, "segment_id": NOTE_SEG, "source_line": line_refs[0]}],
            "related_segment": BODY_SEG,
            "related_body_statement_ids": body_ids,
            "linked_body_statement_ids": body_ids,
            "related_source_lines": line_refs,
            "footnote_link_status": "linked",
            "footnote_text_pending": False,
        }
        if relation:
            qualifiers["relation_candidate_note"] = relation_note
        if correction_key:
            qualifiers["ocr_corrections"] = corrections[correction_key]
        if extra:
            qualifiers.update(extra)
        return {
            "statement_id": f"st-chp1-secii-p13-n{marker}-{suffix}",
            "segment_id": NOTE_SEG,
            "subject_candidate_id": subject,
            "object_candidate_id": obj,
            "predicate": predicate,
            "qualifiers": qualifiers,
            "original_quote": excerpt(full_lines, start, end, phrase),
            "origin": "book",
            "source_file": "02-sources/02-Markdown/01_CHP-1.md",
        }

    def mk_citation(
        suffix: str,
        marker: int,
        start: int,
        end: int,
        quote_phrase: str,
        claim: str,
        citation_candidate: str,
        publication_candidate: str,
        locator: str,
        mention_id: str,
        body_context: list[str],
        *,
        cited_document: str | None = None,
        corrections_key: str | None = None,
        cited_material_not_independently_consulted: bool = True,
    ) -> dict:
        source_author = citation_candidate
        citations = [{
            "source_candidate_id": source_author,
            "publication_candidate_id": publication_candidate,
            "locator": locator,
        }]
        row = mk_statement(
            suffix,
            "cites",
            claim,
            start,
            end,
            quote_phrase,
            marker,
            ["cand-2962", citation_candidate, publication_candidate] + ([cited_document] if cited_document else []),
            subject="cand-2962",
            obj=publication_candidate,
            relation_note="This records Haskell's citation path and locator; it does not independently verify the cited contents.",
            speaker=f"Haskell footnote {marker}",
            text_layer="bibliographic citation locator",
            qualification="The cited pages/publication were not independently consulted; this row records the source path only.",
            extra={
                "citation_candidate_id": citation_candidate,
                "citation_publication_candidate_id": publication_candidate,
                "citation_locator": locator,
                "citations": citations,
                "citation_mention_ids": [mention_id],
                "cited_material_not_independently_consulted": cited_material_not_independently_consulted,
                "relation_candidate": True,
                "cited_document_candidate_id": cited_document,
                "linked_statement_ids": body_context,
                "related_note_statement_ids": body_context,
            },
            correction_key=corrections_key,
        )
        if cited_document is None:
            row["qualifiers"].pop("cited_document_candidate_id", None)
        return row

    # Footnote 1: three distinct contracts and three independent citation locators.
    new_statements = [
        mk_statement(
            "albani-1639-advance", "advance_payment_to_artist",
            "Haskell’s note says that in 1639 Francesco Albani received an exceptionally high contract deposit: 450 of a total 1,000 lire. The named commission is not identified here.",
            503, 505,
            "In 1639 Francesco Albani was given an exceptionally high proportion of the total sum as caparra—450 out of a 1000 lire",
            1, ["cand-0021"], subject="cand-0021", obj=None,
            relation_note="This is a source-defined payment relation. The particular commission/work is unnamed, so no work candidate is inferred.",
            speaker="Haskell footnote 1 summarizing a 1639 payment example",
            text_layer="authorial footnote summary",
            qualification="The deposit is 450 of 1,000 lire; do not merge this unnamed commission with Albani’s separately named Chiesa de’ Servi altarpiece in note 3.",
            correction_key="albani",
        ),
        mk_statement(
            "mola-1639-payment-schedule", "advance_and_installment_payment_for_work",
            "For Pier Francesco Mola’s Valmontone frescoes, Haskell’s note gives 300 scudi immediately and a further 1,000 in installments as work progressed.",
            505, 506,
            "Pier Francesco Mola who for his frescoes at Valmontone was to be given 3 00 scudi immediately and the remaining 1000 in stages as he worked",
            1, ["cand-1676", "cand-3199", "cand-3431"], subject="cand-1676", obj="cand-3199",
            relation_note="The payment schedule is attributed to Mola’s source-defined Valmontone fresco project; no patron is added from the footnote.",
            speaker="Haskell footnote 1 summarizing Montalto",
            text_layer="secondary-source summary of a payment record",
            qualification="The note calls this case more typical than Albani’s large deposit; the cited Montalto page was not independently consulted. The existing Mola Four Elements work candidate is reused.",
            correction_key="mola_payment",
        ),
        mk_statement(
            "ferri-laparelli-altarpiece-payment", "advance_and_completion_payment_for_work",
            "Ciro Ferri received 50 scudi as a deposit and was promised another 180 on completion of an altarpiece in Cortona for Annibale Laparelli.",
            506, 508,
            "Ciro Ferri who was given 50 scudi as caparra and promised 180 more on completion of an altarpiece in Cortona for Annibale Laparclli",
            1, ["cand-3021", "cand-3190", "cand-3111", "cand-1364"], subject="cand-3021", obj="cand-3190",
            relation_note="The source names Ferri, Laparelli and Cortona; the already registered Ferri/Laparelli altarpiece candidate is reused.",
            speaker="Haskell footnote 1 summarizing Gualandi",
            text_layer="secondary-source summary of a payment record",
            qualification="The footnote identifies the altar picture but not its title or specific church. The cited Gualandi page was not independently consulted.",
            correction_key="ferri_payment",
        ),
        mk_citation(
            "cites-gualandi-i-p19", 1, 504, 505, "Gualandi, I, p. 19",
            "Haskell cites Gualandi, volume I, page 19, for the 1639 Albani deposit example.",
            "cand-3477", "cand-6608", "Gualandi, I, p. 19", "m-chp1-secii-p13-n1-gualandi-i-p19",
            ["st-chp1-secii-p13-n1-albani-1639-advance"],
        ),
        mk_citation(
            "cites-montalto-p287-mola-payment", 1, 506, 506, "Montalto, p. 2 8 7",
            "Haskell cites Montalto, page 287, for Mola’s Valmontone payment schedule.",
            "cand-3413", "cand-6355", "Montalto, p. 287", "m-chp1-secii-p13-n1-montalto-p287",
            ["st-chp1-secii-p13-n1-mola-1639-payment-schedule"], corrections_key="mola_payment",
        ),
        mk_citation(
            "cites-gualandi-iv-p117", 1, 508, 508, "Gualandi, IV, p. 117",
            "Haskell cites Gualandi, volume IV, page 117, for Ferri’s Cortona altarpiece payment example.",
            "cand-3477", "cand-11348", "Gualandi, IV, p. 117", "m-chp1-secii-p13-n1-gualandi-iv-p117",
            ["st-chp1-secii-p13-n1-ferri-laparelli-altarpiece-payment"],
            corrections_key="ferri_payment",
        ),
        # Footnote 2 records two separately dated letters and their distinct publication locators.
        mk_statement(
            "gessi-letter-authored-by", "letter_authored_by",
            "The quoted 10 July 1647 letter is attributed to Berlingero Gessi.",
            509, 510,
            "letter from Berlingete Gessi",
            2, ["cand-3545", "cand-3496"], subject="cand-3545", obj="cand-3496",
            relation_note="The footnote explicitly names the letter and writer; the print reads Berlingero where S0 OCR reads Berlingete.",
            speaker="Haskell footnote 2",
            text_layer="letter attribution mediated by Haskell",
            qualification="The original letter was not independently consulted; its author/date are recorded as Haskell prints them.",
            correction_key="gessi",
        ),
        mk_statement(
            "gessi-letter-addressed-to", "letter_addressed_to",
            "Haskell identifies Don Cesare Leopardi d’Osimo as the addressee of Gessi’s 10 July 1647 letter.",
            509, 510,
            "to Don Cesare Leopardi d’Osimo",
            2, ["cand-3545", "cand-1790"], subject="cand-3545", obj="cand-1790",
            relation_note="The named recipient is explicit in the footnote; no letter location is inferred from “d’Osimo”.",
            speaker="Haskell footnote 2",
            text_layer="letter metadata mediated by Haskell",
            qualification="The original letter was not independently consulted.",
            correction_key="gessi",
        ),
        mk_statement(
            "gessi-letter-reports-material-payment-practice", "letter_reports_material_payment_practice",
            "As quoted by Haskell, Gessi’s letter describes it as usual for painters to be paid for the canvas/stretcher, priming and ultramarine.",
            509, 510,
            "‘è solito che si paghi a tutti i pittori il telato, imprimitura, et oltremare ...’",
            2, ["cand-3545", "cand-3496", "cand-3458", "cand-3459", "cand-3460"], subject="cand-3545", obj=None,
            relation=False,
            speaker="Berlingero Gessi, as quoted by Haskell",
            text_layer="quoted letter content mediated by Haskell",
            qualification="This is Haskell’s rendering of a cited letter, not an independently read document; the passage presents a customary practice rather than a rule for every contract.",
            correction_key="gessi",
        ),
        mk_citation(
            "cites-gualandi-i-p40-gessi-letter", 2, 510, 510, "published by Gualandi, I, p. 40",
            "Haskell says Gessi’s letter was published by Gualandi, volume I, page 40.",
            "cand-3477", "cand-6608", "Gualandi, I, p. 40", "m-chp1-secii-p13-n2-gualandi-i-p40",
            ["st-chp1-secii-p13-n2-gessi-letter-authored-by", "st-chp1-secii-p13-n2-gessi-letter-reports-material-payment-practice"],
            cited_document="cand-3545", corrections_key="gessi",
        ),
        mk_statement(
            "quarismini-letter-authored-by", "letter_authored_by",
            "Haskell attributes the 11 July 1696 letter to Carlo Quarismini; the print reads Quarismini where S0 OCR reads Quarisinini.",
            511, 513,
            "letter from Carlo Quarisinini",
            2, ["cand-3546", "cand-3016"], subject="cand-3546", obj="cand-3016",
            relation_note="The source names the correspondent and date; the print confirms the corrected spelling.",
            speaker="Haskell footnote 2",
            text_layer="letter attribution mediated by Haskell",
            qualification="The original letter was not independently consulted.",
            correction_key="quarismini",
        ),
        mk_statement(
            "quarismini-letter-addressed-to", "letter_addressed_to",
            "Haskell identifies Conte Ventura Carrara as the addressee of Quarismini’s 11 July 1696 letter.",
            511, 513,
            "to Conte Ventura Carrara",
            2, ["cand-3546", "cand-3497"], subject="cand-3546", obj="cand-3497",
            relation_note="The recipient is explicit; the source does not provide additional identity details here.",
            speaker="Haskell footnote 2",
            text_layer="letter metadata mediated by Haskell",
            qualification="The original letter was not independently consulted.",
            correction_key="quarismini",
        ),
        mk_statement(
            "quarismini-letter-reports-advance-practice", "letter_reports_canvas_and_advance_practice",
            "Haskell quotes Quarismini’s letter as describing prepared canvas and some advance money as a practice applied even to the least painter.",
            511, 513,
            "‘. . . Sappia che questo è lo stile che si pratica con ogni minimo pittore, cioè consegnarli la tela impresa, e qualche denaro anticipato . . .'",
            2, ["cand-3546", "cand-3016", "cand-3571"], subject="cand-3546", obj=None,
            relation=False,
            speaker="Carlo Quarismini, as quoted by Haskell",
            text_layer="quoted letter content mediated by Haskell",
            qualification="This is a cited letter quotation, not an independently read document; the phrase is retained as a reported practice.",
            correction_key="quarismini",
        ),
        mk_citation(
            "cites-bottari-v-p186-quarismini-letter", 2, 512, 513, "Bottari, V, p. 186",
            "Haskell cites Bottari, volume V, page 186, for Quarismini’s letter.",
            "cand-3507", "cand-9458", "Bottari, V, p. 186", "m-chp1-secii-p13-n2-bottari-v-p186",
            ["st-chp1-secii-p13-n2-quarismini-letter-authored-by", "st-chp1-secii-p13-n2-quarismini-letter-reports-advance-practice"],
            cited_document="cand-3546", corrections_key="quarismini",
        ),
        # Footnote 3 separates the two artists' obligations and preserves the print's internal reference.
        mk_statement(
            "camassei-contract-material-costs", "contract_assigns_material_costs_to_artist",
            "In 1633 Camassei agreed in his contract with Urban VIII to pay for the canvas, colours and blues himself.",
            514, 515,
            "In 1633 Camassei agreed in his contract with Urban Vili (see p. io, note 1) to pay himself sor ‘tela colore e azzurri’",
            3, ["cand-3547", "cand-0484", "cand-3104"], subject="cand-3547", obj="cand-0484",
            relation_note="The contract note explicitly assigns the listed materials to Camassei; Urban VIII is the named contractual counterpart.",
            speaker="Haskell footnote 3",
            text_layer="contract summary mediated by Haskell",
            qualification="The Italian material terms remain as printed in the source transcription; do not normalize them to modern pigment names. The referenced p.10 note is linked separately.",
            correction_key="camassei",
            extra={"contract_counterparty_candidate_id": "cand-3104"},
        ),
        mk_statement(
            "camassei-internal-reference-p10-n1", "internal_cross_reference",
            "The note directs readers to printed page 10, note 1, for the Camassei altarpiece reference.",
            514, 514,
            "see p. io, note 1",
            3, [], relation=False,
            speaker="Haskell footnote 3",
            text_layer="internal navigation",
            qualification="This is a cross-reference, not independent evidence for the contract terms.",
            correction_key="cross_ref",
            extra={
                "cross_reference_chapter": 1,
                "cross_reference_printed_page": 10,
                "cross_reference_note": 1,
                "cross_reference_statement_ids": [P10_CAMASSEI_ID],
                "linked_statement_ids": [P10_CAMASSEI_ID],
            },
        ),
        mk_statement(
            "gozadini-supplies-albani-altarpiece", "promised_material_supply_for_work",
            "In 1639 Bonifazio Gozadini promised to supply Francesco Albani with canvas and the necessary ultramarine for his altarpiece at the Chiesa de’ Servi in Bologna.",
            515, 516,
            "in 1639 Bonifazio Gozadini promised to supply Albani with the canvas and necessary ultramarine for his altarpiece in the Chiesa de’ Servi in Bologna",
            3, ["cand-1217", "cand-0021", "cand-3178", "cand-3571", "cand-3460", "cand-3536", "cand-3398"],
            subject="cand-1217", obj="cand-3178",
            relation_note="The note explicitly connects Gozadini’s promised material supply to Albani’s named altarpiece and site; this is not recast as general patronage.",
            speaker="Haskell footnote 3",
            text_layer="historical agreement summary mediated by Haskell",
            qualification="The existing accepted Albani/Servi altarpiece candidate is reused. The page does not connect this work to the separate Albani deposit example in note 1.",
        ),
        mk_citation(
            "cites-luzio-p48-gozadini", 3, 516, 516, "Luzio, p. 48",
            "Haskell cites Luzio, page 48, for Gozadini’s promised supply of canvas and ultramarine.",
            "cand-3515", "cand-7052", "Luzio, p. 48", "m-chp1-secii-p13-n3-luzio-p48",
            ["st-chp1-secii-p13-n3-gozadini-supplies-albani-altarpiece"], corrections_key=None,
        ),
        mk_statement(
            "pamfili-pays-mola-material-list", "patron_pays_material_costs_for_work",
            "In 1657 Prince Pamfili agreed to pay for the listed white ground, brushes, coccioli smaltirli, green earth, verdetti, fine lakes, pavonazzo di sole and ultramarine for Pier Francesco Mola’s Valmontone frescoes.",
            516, 519,
            "in 1657 Prince Pamfili agreed to pay for ‘il bianco macinato, pennelli, e coccioli smaltirli, terra verde, verdetti, lacche fine, e pavonazzo di sole et azzurro oltramare’ to be used by Pier Francesco Mola in his frescoes at Valmontone",
            3, ["cand-1814", "cand-1676", "cand-3199", "cand-3431", "cand-3458", "cand-3459", "cand-3460", "cand-3571"],
            subject="cand-1814", obj="cand-3199",
            relation_note="The 1657 cost agreement is explicitly for Mola’s Valmontone fresco project; the already registered Four Elements work candidate is reused.",
            speaker="Haskell footnote 3",
            text_layer="contract summary mediated by Haskell",
            qualification="The named pigment/material terms are retained as quoted; no modern material identifications are inferred. The source does not give a first name for Prince Pamfili in this note.",
        ),
        mk_statement(
            "mola-pays-remaining-materials", "artist_pays_remaining_material_costs_for_work",
            "The note says Mola was to pay for the remaining colours, paper and other materials for the Valmontone frescoes.",
            518, 519,
            "while the artist was to pay for the remaining colours, paper, etc.",
            3, ["cand-1676", "cand-3199", "cand-1814"], subject="cand-1676", obj="cand-3199",
            relation_note="This is the artist’s separate share of the same material-cost arrangement; it is not merged with the patron’s listed supplies.",
            speaker="Haskell footnote 3",
            text_layer="contract summary mediated by Haskell",
            qualification="The cited Montalto page was not independently consulted; “etc.” remains open-ended.",
        ),
        mk_citation(
            "cites-montalto-p287-mola-materials", 3, 519, 519, "Montalto, p. 287",
            "Haskell cites Montalto, page 287, for the 1657 allocation of material costs between Prince Pamfili and Mola.",
            "cand-3413", "cand-6355", "Montalto, p. 287", "m-chp1-secii-p13-n3-montalto-p287",
            ["st-chp1-secii-p13-n3-pamfili-pays-mola-material-list", "st-chp1-secii-p13-n3-mola-pays-remaining-materials"],
        ),
        # Notes 4–6 are locators/examples linked to the corresponding body claims.
        mk_statement(
            "gavasetti-uses-finest-colours", "agrees_to_use_specified_material_quality",
            "Camillo Gavasetti agreed in 1624 to use colours ‘of the finest’ for his frescoes in Piacenza.",
            520, 521,
            "Camillo Gavasetti agreed in 1624 to use ‘colori de’ più fini’ for Iris frescoes in Piacenza",
            4, ["cand-1124", "cand-3194", "cand-3483"], subject="cand-1124", obj="cand-3194",
            relation_note="The note ties the quality requirement to Gavasetti’s existing Piacenza/S. Antonino fresco work candidate.",
            speaker="Haskell footnote 4",
            text_layer="contract example mediated by Haskell",
            qualification="The Italian phrase is retained without further material identification; the print reads “his” where S0 OCR reads “Iris”.",
            correction_key="gavasetti",
        ),
        mk_citation(
            "cites-gualandi-i-p91-gavasetti", 4, 521, 521, "Gualandi, I, p. 91",
            "Haskell cites Gualandi, volume I, page 91, for the Gavasetti colour-quality example.",
            "cand-3477", "cand-6608", "Gualandi, I, p. 91", "m-chp1-secii-p13-n4-gualandi-i-p91",
            ["st-chp1-secii-p13-n4-gavasetti-uses-finest-colours"], corrections_key="gavasetti",
        ),
        mk_citation(
            "cites-montalto-pp287-289-mola-treatment", 5, 522, 522, "Montalto, pp. 287 and 289",
            "Haskell cites Montalto, pages 287 and 289, for the preceding report that Prince Pamfili treated Mola as one of his retinue and supplied delicacies.",
            "cand-3413", "cand-6355", "Montalto, pp. 287 and 289", "m-chp1-secii-p13-n5-montalto-pp287-289",
            ["st-chp1-secii-l73-77-03"],
        ),
        mk_statement(
            "preti-gentileschi-letters-mentioned", "letters_cited_as_examples",
            "Haskell points to letters by Mattia Preti and Artemisia Gentileschi as examples; this note gives no individual dates, letter contents, or recipients.",
            523, 523,
            "letters from Mattia Preti and Artemisia Gentileschi",
            6, ["cand-3548", "cand-2061", "cand-1134"], subject="cand-3548", obj=None,
            relation=False,
            speaker="Haskell footnote 6",
            text_layer="bibliographic note identifying cited correspondence",
            qualification="The letters are named only as examples in this note; do not infer their content, dates, or addressee here.",
        ),
        mk_citation(
            "cites-ruffo-pp239-48-preti-gentileschi-letters", 6, 523, 523, "Ruffo, pp. 239 and 48",
            "Haskell cites the Preti and Gentileschi letters through a publication abbreviated as Ruffo, pages 239 and 48.",
            "cand-3555", "cand-3555", "Ruffo, pp. 239 and 48", "m-chp1-secii-p13-n6-ruffo-pp239-48",
            ["st-chp1-secii-p13-n6-preti-gentileschi-letters-mentioned"], cited_document="cand-3548",
        ),
    ]

    citation_rows = {row["statement_id"]: row for row in new_statements if row["predicate"] == "cites"}
    mention_specs = [
        ("m-chp1-secii-p13-n1-ferri-altarpiece", "cand-3190", "altarpiece", "Ciro Ferri’s unidentified-in-note altarpiece for Annibale Laparelli; existing accepted work candidate reused.", 0),
        ("m-chp1-secii-p13-n1-mola-frescoes", "cand-3199", "frescoes at Valmontone", "Pier Francesco Mola’s existing Valmontone Four Elements work candidate, as named in the payment example.", 0),
        ("m-chp1-secii-p13-n1-gualandi-i-p19", "cand-6608", "Gualandi, I, p. 19", "Exact Gualandi volume I citation locator; the cited page was not independently consulted.", 0),
        ("m-chp1-secii-p13-n1-montalto-p287", "cand-6355", "Montalto, p. 2 8 7", "Exact p.13 note 1 locator; print confirms p.287; cited page was not independently consulted.", 0),
        ("m-chp1-secii-p13-n1-gualandi-iv-p117", "cand-11348", "Gualandi, IV, p. 117", "Exact volume IV locator mapped to the bibliography-identified Gualandi set; cited page was not independently consulted.", 0),
        ("m-chp1-secii-p13-n2-gessi-telato", "cand-3458", "il telato", "Original Italian term for the canvas/stretcher expense in Gessi’s quoted letter.", 0),
        ("m-chp1-secii-p13-n2-gessi-imprimitura", "cand-3459", "imprimitura", "Original Italian term for priming in Gessi’s quoted letter.", 0),
        ("m-chp1-secii-p13-n2-gessi-oltremare", "cand-3460", "oltremare", "Original Italian term for ultramarine in Gessi’s quoted letter.", 0),
        ("m-chp1-secii-p13-n2-gualandi-i-p40", "cand-6608", "Gualandi, I, p. 40", "Exact publication locator for the 1647 Gessi letter; the cited page was not independently consulted.", 0),
        ("m-chp1-secii-p13-n2-quarismini-prepared-canvas", "cand-3571", "la tela impresa", "Prepared canvas mentioned in Quarismini’s quoted letter; mapped to the existing canvas material term.", 0),
        ("m-chp1-secii-p13-n2-bottari-v-p186", "cand-9458", "Bottari, V, p. 186", "Exact Bottari volume V locator for the Quarismini letter; the cited page was not independently consulted.", 0),
        ("m-chp1-secii-p13-n3-albani-altarpiece", "cand-3178", "his altarpiece", "Albani altarpiece supplied by Gozadini; existing accepted work candidate reused.", 0),
        ("m-chp1-secii-p13-n3-luzio-p48", "cand-7052", "Luzio, p. 48", "Exact Luzio locator for Gozadini’s material-supply promise; the cited page was not independently consulted.", 0),
        ("m-chp1-secii-p13-n3-mola-frescoes", "cand-3199", "frescoes at Valmontone", "The same Mola Four Elements work candidate as the p.13 note 1 payment example.", 1),
        ("m-chp1-secii-p13-n3-montalto-p287", "cand-6355", "Montalto, p. 287", "Exact p.13 note 3 locator for the 1657 material-cost allocation; cited page not independently consulted.", 0),
        ("m-chp1-secii-p13-n4-gavasetti-frescoes", "cand-3194", "his frescoes in Piacenza", "Gavasetti’s existing Piacenza/S. Antonino fresco-work candidate; print reads “his” where S0 has “Iris”.", 0),
        ("m-chp1-secii-p13-n4-gualandi-i-p91", "cand-6608", "Gualandi, I, p. 91", "Exact p.13 note 4 locator; cited page was not independently consulted.", 1),
        ("m-chp1-secii-p13-n5-montalto-pp287-289", "cand-6355", "Montalto, pp. 287 and 289", "Exact note 5 citation locator; the cited pages were not independently consulted.", 0),
        ("m-chp1-secii-p13-n6-ruffo-pp239-48", "cand-3555", "Ruffo, pp. 239 and 48", "Exact locator to the unresolved Ruffo publication; do not identify it as Antonio Ruffo or the 1916 V. Ruffo article.", 0),
    ]
    new_mentions: list[dict[str, str]] = []
    for mention_id, candidate_id, phrase, note, occurrence in mention_specs:
        start, end, surface = normalized_span(flat_note, phrase, occurrence)
        new_mentions.append({
            "mention_id": mention_id,
            "segment_id": NOTE_SEG,
            "candidate_id": candidate_id,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        })

    # Add the exact locator-mention IDs to their statement rows.
    mention_ids_by_statement = {
        "st-chp1-secii-p13-n1-cites-gualandi-i-p19": "m-chp1-secii-p13-n1-gualandi-i-p19",
        "st-chp1-secii-p13-n1-cites-montalto-p287-mola-payment": "m-chp1-secii-p13-n1-montalto-p287",
        "st-chp1-secii-p13-n1-cites-gualandi-iv-p117": "m-chp1-secii-p13-n1-gualandi-iv-p117",
        "st-chp1-secii-p13-n2-cites-gualandi-i-p40-gessi-letter": "m-chp1-secii-p13-n2-gualandi-i-p40",
        "st-chp1-secii-p13-n2-cites-bottari-v-p186-quarismini-letter": "m-chp1-secii-p13-n2-bottari-v-p186",
        "st-chp1-secii-p13-n3-cites-luzio-p48-gozadini": "m-chp1-secii-p13-n3-luzio-p48",
        "st-chp1-secii-p13-n3-cites-montalto-p287-mola-materials": "m-chp1-secii-p13-n3-montalto-p287",
        "st-chp1-secii-p13-n4-cites-gualandi-i-p91-gavasetti": "m-chp1-secii-p13-n4-gualandi-i-p91",
        "st-chp1-secii-p13-n5-cites-montalto-pp287-289-mola-treatment": "m-chp1-secii-p13-n5-montalto-pp287-289",
        "st-chp1-secii-p13-n6-cites-ruffo-pp239-48-preti-gentileschi-letters": "m-chp1-secii-p13-n6-ruffo-pp239-48",
    }
    for statement_id, mention_id in mention_ids_by_statement.items():
        citation_rows[statement_id]["qualifiers"]["citation_mention_ids"] = [mention_id]

    # Extend material-term mention mappings in the statement claims themselves.
    statement_by_new_id = {row["statement_id"]: row for row in new_statements}
    for sid, ids in {
        "st-chp1-secii-p13-n2-gessi-letter-reports-material-payment-practice": ["cand-3458", "cand-3459", "cand-3460"],
        "st-chp1-secii-p13-n2-quarismini-letter-reports-advance-practice": ["cand-3571"],
    }.items():
        append_unique(statement_by_new_id[sid]["qualifiers"]["mentioned_candidate_ids"], ids)

    # Natural-key and foreign-key checks before any write.
    new_ids = [row["statement_id"] for row in new_statements]
    if len(new_ids) != len(set(new_ids)) or set(new_ids) & set(statement_by_id):
        raise SystemExit("new p.13 statement IDs collide with the protected table")
    referenced_candidates = set()
    for row in new_statements:
        for key in ("subject_candidate_id", "object_candidate_id"):
            if row.get(key):
                referenced_candidates.add(row[key])
        referenced_candidates.update(row["qualifiers"].get("mentioned_candidate_ids", []))
    referenced_candidates.update(row["candidate_id"] for row in new_mentions)
    missing_candidates = sorted(referenced_candidates - set(candidate_by_id))
    if missing_candidates:
        raise SystemExit(f"missing candidate foreign keys: {missing_candidates}")
    existing_mention_ids = {row["mention_id"] for row in mentions}
    if len(existing_mention_ids) != len(mentions):
        raise SystemExit("duplicate mention IDs in protected table")
    if any(row["mention_id"] in existing_mention_ids for row in new_mentions):
        raise SystemExit("new p.13 mention ID already exists")
    natural_keys = {(row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"]) for row in mentions}
    for row in new_mentions:
        key = (row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"])
        if key in natural_keys:
            raise SystemExit(f"duplicate mention natural key: {key}")
        natural_keys.add(key)
        a, b = int(row["start_char"]), int(row["end_char"])
        if flat_note[a:b] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']}")
    for row in new_statements:
        start = row["qualifiers"]["source_line_start"]
        end = row["qualifiers"]["source_line_end"]
        if row["original_quote"] not in "\n".join(full_lines[start - 1 : end]):
            raise SystemExit(f"quote is outside source lines for {row['statement_id']}")
        if row["qualifiers"]["footnote_marker"] not in BODY_IDS:
            raise SystemExit(f"missing body marker map for {row['statement_id']}")
    if len(new_statements) != 26 or len(new_mentions) != len(mention_specs):
        raise SystemExit(f"unexpected migration size: {len(new_statements)} statements / {len(new_mentions)} mentions")

    # Verify exact reciprocal marker links and the printed p.10 note cross-reference.
    for marker, body_ids in BODY_IDS.items():
        expected_marker = MARKER_LINES[marker]
        matches = [row for row in new_statements if row["qualifiers"]["footnote_marker"] == marker]
        if not matches or any(row["qualifiers"]["footnote_refs"] != [{"marker": marker, "segment_id": NOTE_SEG, "source_line": expected_marker}] for row in matches):
            raise SystemExit(f"incomplete p.13 marker {marker} linkage")
        for body_id in body_ids:
            if body_id not in statement_by_id:
                raise SystemExit(f"missing p.13 body statement: {body_id}")
    if P10_CAMASSEI_ID not in statement_by_id:
        raise SystemExit("p.10 note 1 target statement is missing")

    # Correct only S2 candidate/mention labels; preserve every S0 surface string.
    candidate_updates = {
        "cand-3496": {
            "canonical_name": "Berlingero Gessi",
            "detail": "Author of the cited 10 July 1647 letter about material payments; S0 OCR reads Berlingete, while printed p.13 reads Berlingero.",
        },
        "cand-3545": {
            "canonical_name": "Letter from Berlingero Gessi to Don Cesare Leopardi d’Osimo (1647-07-10)",
            "detail": "Dated correspondence cited for payment conventions; printed p.13 corrects S0 OCR Berlingete/io to Berlingero/10.",
        },
        "cand-3546": {
            "canonical_name": "Letter from Carlo Quarismini to Conte Ventura Carrara (1696-07-11)",
            "detail": "Dated correspondence cited for payment conventions; printed p.13 corrects S0 OCR Quarisinini to Quarismini.",
        },
        "cand-3548": {
            "canonical_name": "Letters from Mattia Preti and Artemisia Gentileschi (cited examples; addressee unspecified)",
            "candidate_source_ref": f"{NOTE_SEG}#L523",
            "detail": "Two letters are cited as examples on printed p.13 note 6. That note supplies no dates, contents or recipients; their addressee is not inferred from the abbreviated Ruffo citation.",
        },
        "cand-6608": {
            "canonical_name": "Gualandi, volume I, cited publication (title and edition unspecified)",
            "detail": "Volume-I citation candidate. The book includes p.38 (chapter 7) and p.13 locators at pp.19, 40 and 91; cited pages were not independently consulted. The six-volume bibliography record is cand-11348.",
        },
        "cand-9458": {
            "canonical_name": "Bottari, volume V, cited publication (1822 Raccolta; volume-level locator)",
            "detail": "Volume-V citation candidate used for the p.294 note 3 pages 27–28 and p.13 note 2 page 186. The full collection record is cand-11261; cited pages were not independently consulted.",
        },
        "cand-6355": {
            "detail": "L. Montalto, ‘Gli affreschi del Palazzo Pamphilj in Valmontone’ (Commentari, 1955, pp. 267–302), identified from the book bibliography. Printed p.13 notes cite pp.287, 287 and 289; those pages were not independently consulted. Keep separate from surname-only person candidate cand-3413 pending S3.",
        },
        "cand-3555": {
            "detail": "Bare Ruffo references denote a cited correspondence publication, distinct from Antonio Ruffo and from the identified 1916 V. Ruffo article. Printed p.13 note 6 cites pp.239 and 48; the exact title/edition and contents remain unresolved and unconsulted.",
        },
    }
    for candidate_id, updates in candidate_updates.items():
        if candidate_id not in candidate_by_id:
            raise SystemExit(f"candidate update target missing: {candidate_id}")
        candidate_by_id[candidate_id].update(updates)

    mention_updates = {
        "m-chp1-secii-0448": "Named recipient; S0 OCR Laparclli is corrected to Annibale Laparelli by printed p.13.",
        "m-chp1-secii-0558": "Nested surname span within the full-name mention of Francesco Albani in the 1639 advance example; it is not a second material-supply occurrence.",
        "m-chp1-secii-0573": "Letter from Berlingero Gessi to Don Cesare Leopardi d’Osimo, dated 10 July 1647; S0 OCR Berlingete/io is preserved in surface_form and corrected only in S2.",
        "m-chp1-secii-0449": "Author of the cited 10 July 1647 letter; printed p.13 reads Berlingero Gessi while S0 OCR reads Berlingete Gessi.",
        "m-chp1-secii-0450": "Recipient named in Haskell’s cited 1647 letter; the surname d’Osimo is not treated as the letter’s location.",
        "m-chp1-secii-0484": "Gualandi volume-I author/editor mention in the citation to the 1696 Quarismini letter.",
        "m-chp1-secii-0574": "Letter from Carlo Quarismini to Conte Ventura Carrara, dated 11 July 1696; S0 OCR Quarisinini is preserved in surface_form and corrected only in S2.",
        "m-chp1-secii-0451": "Author of the cited 1696 letter; printed p.13 reads Carlo Quarismini while S0 OCR reads Quarisinini.",
        "m-chp1-secii-0452": "Recipient of Quarismini’s 11 July 1696 letter.",
        "m-chp1-secii-0497": "Bottari is cited as the publication source for the 1696 letter at volume V, page 186; personal identity remains unresolved.",
        "m-chp1-secii-0435": "Camassei is named in the 1633 Urban VIII contract example; this note gives no first name.",
        "m-chp1-secii-0575": "Contract with Urban VIII, 1633; named as the source of Camassei’s material-cost agreement.",
        "m-chp1-secii-0454": "Urban VIII, named contractual counterpart in the 1633 Camassei example; S0 OCR Vili is corrected in S2.",
        "m-chp1-secii-0453": "Bonifazio Gozadini promised to supply canvas and ultramarine for Albani’s Chiesa de’ Servi altarpiece; he is not identified as a painter here.",
        "m-chp1-secii-0559": "Surname-only reference to Francesco Albani in Gozadini’s 1639 material-supply example.",
        "m-chp1-secii-0560": "Church named as the intended site of Albani’s altarpiece; the statement also identifies Bologna.",
        "m-chp1-secii-0418": "City of the Chiesa de’ Servi altarpiece named in this note; previous mention note incorrectly described Ricci’s commission.",
        "m-chp1-secii-0510": "Luzio citation at page 48 for Gozadini’s promised canvas and ultramarine supply; identity remains unresolved.",
        "m-chp1-secii-0400": "Prince Pamfili is named in the 1657 agreement for Mola’s Valmontone frescoes; this note does not supply his first name.",
        "m-chp1-secii-0490": "Montalto citation at page 287 for the 1657 allocation of material costs; author/work identity maps to the bibliography-identified article candidate cand-6355 for this locator.",
        "m-chp1-secii-0410": "Camillo Gavasetti, whose 1624 Piacenza frescoes had a ‘finest colours’ requirement.",
        "m-chp1-secii-0413": "City where Gavasetti’s frescoes were to use the finest colours.",
        "m-chp1-secii-0485": "Gualandi volume-I citation locator at page 91 for Gavasetti’s 1624 agreement.",
        "m-chp1-secii-0491": "Montalto citation for the preceding Haskell report about Mola’s treatment; article candidate cand-6355 is distinct from the unresolved person candidate.",
        "m-chp1-secii-0576": "Haskell cites letters by Mattia Preti and Artemisia Gentileschi as examples; the note gives no individual dates, contents or addressee.",
        "m-chp1-secii-0455": "Mattia Preti, whose letter is cited as an example; no letter content or recipient is supplied in this note.",
        "m-chp1-secii-0456": "Artemisia Gentileschi, whose letter is cited as an example; no letter content or recipient is supplied in this note.",
    }
    mention_by_id = {row["mention_id"]: row for row in mentions}
    if not set(mention_updates).issubset(mention_by_id):
        raise SystemExit(f"expected existing p.13 mentions missing: {sorted(set(mention_updates) - set(mention_by_id))}")
    for mention_id, note in mention_updates.items():
        mention_by_id[mention_id]["note"] = note

    # Atomize the note rows in place and preserve unrelated notes in the same merged segment.
    rebuilt_statements: list[dict] = []
    inserted = False
    for row in statements:
        if row["statement_id"] in OLD_IDS:
            if not inserted:
                rebuilt_statements.extend(new_statements)
                inserted = True
            continue
        rebuilt_statements.append(row)
    if not inserted:
        raise SystemExit("failed to replace the three protected p.13 note rows")

    # Replace the old broad links with precise body-to-note links, preserving unrelated links.
    broad_to_precise = {
        "st-chp1-secii-notes-advance-payment-cases": [
            "st-chp1-secii-p13-n1-albani-1639-advance",
            "st-chp1-secii-p13-n1-mola-1639-payment-schedule",
            "st-chp1-secii-p13-n1-ferri-laparelli-altarpiece-payment",
            "st-chp1-secii-p13-n1-cites-gualandi-i-p19",
            "st-chp1-secii-p13-n1-cites-montalto-p287-mola-payment",
            "st-chp1-secii-p13-n1-cites-gualandi-iv-p117",
        ],
        "st-chp1-secii-notes-payment-letters": [
            "st-chp1-secii-p13-n2-gessi-letter-authored-by",
            "st-chp1-secii-p13-n2-gessi-letter-addressed-to",
            "st-chp1-secii-p13-n2-gessi-letter-reports-material-payment-practice",
            "st-chp1-secii-p13-n2-cites-gualandi-i-p40-gessi-letter",
            "st-chp1-secii-p13-n2-quarismini-letter-authored-by",
            "st-chp1-secii-p13-n2-quarismini-letter-addressed-to",
            "st-chp1-secii-p13-n2-quarismini-letter-reports-advance-practice",
            "st-chp1-secii-p13-n2-cites-bottari-v-p186-quarismini-letter",
        ],
        "st-chp1-secii-notes-material-cost-allocation": [
            "st-chp1-secii-p13-n3-camassei-contract-material-costs",
            "st-chp1-secii-p13-n3-camassei-internal-reference-p10-n1",
            "st-chp1-secii-p13-n3-gozadini-supplies-albani-altarpiece",
            "st-chp1-secii-p13-n3-cites-luzio-p48-gozadini",
            "st-chp1-secii-p13-n3-pamfili-pays-mola-material-list",
            "st-chp1-secii-p13-n3-mola-pays-remaining-materials",
            "st-chp1-secii-p13-n3-cites-montalto-p287-mola-materials",
            "st-chp1-secii-p13-n4-gavasetti-uses-finest-colours",
            "st-chp1-secii-p13-n4-cites-gualandi-i-p91-gavasetti",
            "st-chp1-secii-p13-n5-cites-montalto-pp287-289-mola-treatment",
            "st-chp1-secii-p13-n6-preti-gentileschi-letters-mentioned",
            "st-chp1-secii-p13-n6-cites-ruffo-pp239-48-preti-gentileschi-letters",
        ],
    }
    old_refs = set(broad_to_precise)
    for row in rebuilt_statements:
        q = row.get("qualifiers", {})
        if "linked_statement_ids" in q:
            q["linked_statement_ids"] = [sid for sid in q["linked_statement_ids"] if sid not in old_refs]
        for field in ("related_body_statement_ids", "linked_body_statement_ids", "footnote_statement_ids"):
            if field in q:
                q[field] = [sid for sid in q[field] if sid not in old_refs]
    body_by_id = {row["statement_id"]: row for row in rebuilt_statements}
    for old_id, precise_ids in broad_to_precise.items():
        old = statement_by_id[old_id]
        related_body_ids = old["qualifiers"].get("linked_body_statement_ids", old["qualifiers"].get("related_body_statement_ids", []))
        # The p.13 body statement links are explicitly grounded by the note markers.
        if old_id == "st-chp1-secii-notes-advance-payment-cases":
            related_body_ids = BODY_IDS[1]
        elif old_id == "st-chp1-secii-notes-payment-letters":
            related_body_ids = BODY_IDS[2]
        elif old_id == "st-chp1-secii-notes-material-cost-allocation":
            related_body_ids = list(dict.fromkeys(BODY_IDS[3] + BODY_IDS[4] + BODY_IDS[5] + BODY_IDS[6]))
        for body_id in related_body_ids:
            if body_id not in body_by_id:
                raise SystemExit(f"old note row references missing body statement: {body_id}")
            q = body_by_id[body_id].setdefault("qualifiers", {})
            links = q.setdefault("linked_statement_ids", [])
            q["linked_statement_ids"] = [sid for sid in links if sid != old_id]
            # Add only the rows whose body marker belongs to this statement.
            marker_for_body = {
                "st-chp1-secii-l73-77-01": [1],
                "st-chp1-secii-l73-77-02": [2, 3, 4],
                "st-chp1-secii-l73-77-03": [5],
                "st-chp1-secii-l73-77-06": [6],
            }.get(body_id, [])
            marker_rows = [r["statement_id"] for r in new_statements if r["qualifiers"]["footnote_marker"] in marker_for_body]
            append_unique(q["linked_statement_ids"], marker_rows)

    # Reciprocal link for the printed p.10 note 1 cross-reference.
    cross_id = "st-chp1-secii-p13-n3-camassei-internal-reference-p10-n1"
    p10 = body_by_id[P10_CAMASSEI_ID]
    p10q = p10.setdefault("qualifiers", {})
    append_unique(p10q.setdefault("linked_statement_ids", []), [cross_id])
    append_unique(p10q.setdefault("referenced_by_statement_ids", []), [cross_id])

    # Update coverage note without changing its reviewed/complete disposition.
    coverage_rows = [row for row in coverage if row["segment_id"] == NOTE_SEG]
    if len(coverage_rows) != 1:
        raise SystemExit("expected exactly one merged-note coverage row")
    coverage_note = coverage_rows[0]["note"]
    coverage_rows[0]["note"] = coverage_note.rstrip() + (
        " Printed p.13 (PDF physical p.12) notes 1–6 were checked against the page image. "
        "The three broad note rows for L503–523 were replaced by 26 source-specific claims and citation rows. "
        "The Albani 1639 deposit remains separate from the Chiesa de’ Servi altarpiece; the Mola Valmontone project, "
        "Ferri/Laparelli altarpiece, Gozadini material promise, Camassei contract, and Gavasetti colour clause reuse existing candidates. "
        "Berlingero and Quarismini print spellings, payment amounts, dates, Urban VIII, and “his frescoes” are recorded as S2 OCR corrections; S0 is unchanged. "
        "Exact citation locators were linked; cited pages and letters were not independently consulted. "
        "The p.13 note 3 cross-reference now points to p.10 note 1. No KU or formal relation was added."
    )

    # Confirm statement/body reciprocity, exact candidate refs, and citation-to-mention consistency.
    rebuilt_by_id = {row["statement_id"]: row for row in rebuilt_statements}
    for row in new_statements:
        for body_id in row["qualifiers"]["linked_body_statement_ids"]:
            if row["statement_id"] not in rebuilt_by_id[body_id]["qualifiers"].get("linked_statement_ids", []):
                raise SystemExit(f"body/note link is not reciprocal: {row['statement_id']} / {body_id}")
        if row["predicate"] == "cites":
            citation_mention = row["qualifiers"]["citation_mention_ids"][0]
            if not any(m["mention_id"] == citation_mention for m in new_mentions):
                raise SystemExit(f"citation mention missing: {row['statement_id']}")
    if cross_id not in rebuilt_by_id[P10_CAMASSEI_ID]["qualifiers"].get("linked_statement_ids", []):
        raise SystemExit("p.10/p.13 internal cross-reference is not reciprocal")
    all_statement_ids = set(rebuilt_by_id)
    for row in new_statements:
        q = row["qualifiers"]
        for sid in q.get("linked_statement_ids", []) + q.get("related_body_statement_ids", []) + q.get("cross_reference_statement_ids", []):
            if sid not in all_statement_ids:
                raise SystemExit(f"statement link target missing: {row['statement_id']} -> {sid}")

    candidate_rows = candidates
    mention_rows = mentions + new_mentions
    updated_tables = {
        "book-statements.jsonl": rebuilt_statements,
        "entity-candidates.csv": candidate_rows,
        "mentions.csv": mention_rows,
        "s2-coverage.csv": coverage,
    }
    summary = {
        "mode": "apply" if args.apply else "preview",
        "source": "CHP-1.pdf print p.13 / S0 L503-523",
        "replaced_statement_ids": sorted(OLD_IDS),
        "new_statement_count": len(new_statements),
        "new_statement_ids": [row["statement_id"] for row in new_statements],
        "new_mention_count": len(new_mentions),
        "new_mention_ids": [row["mention_id"] for row in new_mentions],
        "updated_candidate_ids": sorted(candidate_updates),
        "updated_existing_mention_count": len(mention_updates),
        "source_unchanged": True,
        "coverage_disposition": coverage_rows[0]["disposition"],
        "coverage_migration_status": coverage_rows[0]["migration_status"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups: dict[str, Path] = {}
    temp_paths: dict[str, Path] = {}
    try:
        for name, path in tables.items():
            backup = path.with_name(path.name + BACKUP_SUFFIX)
            if backup.exists():
                raise SystemExit(f"recovery copy already exists; refusing overwrite: {backup.name}")
            shutil.copy2(path, backup)
            backups[name] = backup
        for name, rows in updated_tables.items():
            path = tables[name]
            temp = path.with_name(path.name + ".tmp-s2-p13")
            if temp.exists():
                raise SystemExit(f"stale temp file exists; refusing overwrite: {temp.name}")
            if name.endswith(".jsonl"):
                write_jsonl(temp, rows)  # type: ignore[arg-type]
            else:
                write_csv(temp, rows)  # type: ignore[arg-type]
            temp_paths[name] = temp
        for name, temp in temp_paths.items():
            os.replace(temp, tables[name])
    except Exception:
        for name, backup in backups.items():
            shutil.copy2(backup, tables[name])
        for temp in temp_paths.values():
            if temp.exists():
                temp.unlink()
        raise
    summary["backups"] = {name: path.name for name, path in backups.items()}
    summary["post_hashes"] = {name: digest(tables[name]) for name in EXPECTED}
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
