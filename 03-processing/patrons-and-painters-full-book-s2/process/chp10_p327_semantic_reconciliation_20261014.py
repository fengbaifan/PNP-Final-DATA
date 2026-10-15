from __future__ import annotations

import argparse
import csv
import copy
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
STATEMENTS = TABLES / "book-statements.jsonl"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l224-239"
NOTE_SEGMENT = "chp-10:10_CHP-10_sec_ii:l273-349"
BACKUP_SUFFIX = ".bak-s2-chp10-p327-semantic-reconciliation-20261014"

EXPECTED = {
    STATEMENTS.name: "0763bc7be66f556b7220b070b7fca43f9175e4b1f531e584f3fa671d2c6aaf65",
    MENTIONS.name: "e73acdaaa30e46916a9120094f58c33ee6d15afed01807cfd45557b5e7f348ce",
    COVERAGE.name: "7765342aacbe38fc99cee0bebd0a3734cfd1e9b477faa672d0e61251b62b5533",
    SOURCE.name: "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def dump_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def dump_csv(fields: list[str], rows: list[dict]) -> bytes:
    from io import StringIO

    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def line_quote(lines: list[str], first: int, last: int, start: str, end: str) -> str:
    block = "\n".join(lines[first - 1 : last])
    start_at = block.find(start)
    if start_at < 0:
        raise ValueError(f"quote start not found on lines {first}-{last}: {start!r}")
    end_at = block.find(end, start_at + len(start))
    if end_at < 0 and start.endswith(end):
        end_at = start_at + len(start) - len(end)
    if end_at < 0:
        raise ValueError(f"quote end not found on lines {first}-{last}: {end!r}")
    return block[start_at : end_at + len(end)]


def make_qualifiers(
    start: int,
    end: int,
    claim: str,
    qualification: str,
    mentioned: list[str],
    relation: bool,
    *,
    speaker: str = "Haskell",
    text_layer: str = "authorial narrative",
    relation_note: str | None = None,
    footnote: bool = False,
    extra: dict | None = None,
) -> dict:
    result = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 327,
        "pdf_physical_page": 60,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
    }
    if relation_note:
        result["relation_candidate_note"] = relation_note
    if footnote:
        result.update(
            {
                "footnote_marker": 3,
                "footnote_segment": NOTE_SEGMENT,
                "footnote_refs": [
                    {"marker": 3, "segment_id": NOTE_SEGMENT, "source_line": 335},
                    {"marker": 3, "segment_id": SEGMENT, "source_line": 237},
                ],
                "cited_source_independently_consulted": False,
            }
        )
    if extra:
        result.update(extra)
    return result


def statement(
    statement_id: str,
    subject: str | None,
    obj: str | None,
    predicate: str,
    quote: str,
    qualifiers: dict,
    source_file: str,
    *,
    segment: str = SEGMENT,
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": segment,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": source_file,
    }


def occurrence(text: str, needle: str, which: int = 0) -> int:
    found = []
    cursor = 0
    while True:
        index = text.find(needle, cursor)
        if index < 0:
            break
        found.append(index)
        cursor = index + 1
    if which >= len(found):
        raise ValueError(f"mention span not found: {needle!r}, occurrence={which}")
    return found[which]


def mention_position(text: str, surface: str, context: str | None = None, which: int = 0) -> tuple[int, int]:
    if context is None:
        start = occurrence(text, surface, which)
    else:
        context_start = occurrence(text, context, which)
        within = context.find(surface)
        if within < 0:
            raise ValueError(f"{surface!r} not contained in context {context!r}")
        start = context_start + within
    return start, start + len(surface)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes after exact-hash preflight")
    args = parser.parse_args()

    paths = [STATEMENTS, MENTIONS, COVERAGE, SOURCE]
    current_hashes = {path.name: sha256(path) for path in paths}
    if current_hashes != EXPECTED:
        raise SystemExit(f"preflight hash mismatch; no writes made: {current_hashes}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    full_source = "\n".join(source_lines)
    segment_text = "\n".join(source_lines[223:239])
    statements = load_jsonl(STATEMENTS)
    statement_by_id = {row["statement_id"]: row for row in statements}
    if len(statement_by_id) != len(statements):
        raise SystemExit("duplicate statement_id in current table")

    active_ids = {
        "st-chp10-p326-n03-dating-and-exhibition",
        "st-chp10-p327-dallacqua-not-involved-report",
        "st-chp10-p327-giampiccoli-print-commission",
        "st-chp10-p327-inquisitors-act-four-days-later",
        "st-chp10-p327-less-offensive-poem-open",
        "st-chp10-p327-menu-verse-and-circulating-saying",
        "st-chp10-p327-palace-celebration-surveillance",
        "st-chp10-p327-pisani-arrest-boscarati-trouble",
        "st-chp10-p327-political-pictures-procuratie",
        "st-chp10-p327-politics-and-art-separation",
        "st-chp10-p327-print-inscription-and-withdrawal",
    }
    if not active_ids.issubset(statement_by_id):
        raise SystemExit(f"missing expected segment statements: {sorted(active_ids - statement_by_id.keys())}")
    if sum(row.get("segment_id") == SEGMENT for row in statements) != len(active_ids):
        raise SystemExit("unexpected statement set in the p.327 segment; no writes made")

    source_file = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
    note_refs_extra = {
        "footnote_statement_ids": ["st-chp10-p327-n03-moschini-citation"],
        "footnote_body_link_status": "linked",
    }

    def q(first: int, last: int, start: str, end: str) -> str:
        quote = line_quote(source_lines, first, last, start, end)
        if quote not in full_source:
            raise ValueError(f"quote not found in OCR source: {quote!r}")
        return quote

    rows_to_add = [
        statement(
            "st-chp10-p327-political-pictures-iconography",
            "cand-9807",
            "cand-8449",
            "pictures_show_procurator_rebuilding_public_buildings",
            q(225, 226, "showing ‘the sleeping lion", "copy him’."),
            make_qualifiers(
                225,
                226,
                "Haskell describes the political pictures as showing a sleeping lion, unbalanced scales, a liberty cap, collapsing public buildings, and a Procurator rebuilding them while encouraging his sons to follow.",
                "The description continues from p.326. It identifies the office of Procurator but does not name the sons or establish the maker's intended meaning.",
                ["cand-9807", "cand-8449"],
                True,
                relation_note="The source describes the image's representation of the Procurator; this remains an S2 candidate, not a formal edge.",
                extra={
                    "continuation_from_segment_id": "chp-10:10_CHP-10_sec_ii:l210-222",
                    "continuation_prefix": "for other pictures, much more obviously",
                    "footnote_marker": 1,
                    "footnote_segment": NOTE_SEGMENT,
                    "footnote_refs": [{"marker": 1, "segment_id": NOTE_SEGMENT, "source_line": 336}],
                    "footnote_statement_ids": ["st-chp10-p327-n01-grimaldo-balbi-citation"],
                    "footnote_body_link_status": "linked",
                },
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-celebration-time",
            "cand-9812",
            "cand-9792",
            "celebration_held_on_evening_of_pisani_procession",
            q(229, 229, "on the evening of the procession", "when a huge celebration"),
            make_qualifiers(
                229,
                229,
                "Haskell dates the palace celebration to the evening of Pisani's procession.",
                "The source supplies a relative event date, not a calendar date.",
                ["cand-9812", "cand-9792"],
                True,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-celebration-location",
            "cand-9812",
            "cand-9811",
            "celebration_held_at_pisani_palace",
            q(229, 229, "a huge celebration was held", "in the palace"),
            make_qualifiers(
                229,
                229,
                "Haskell says the large celebration was held in Pisani's palace.",
                "The palace is not independently identified beyond the source-local candidate at Campo di S. Maria Formosa.",
                ["cand-9812", "cand-9811"],
                True,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-spies-picture-report",
            "cand-9790",
            "cand-9813",
            "spies_noted_picture_in_celebration_reception_room",
            q(229, 229, "Spies moved among the guests", "a picture"),
            make_qualifiers(
                229,
                229,
                "Haskell says the unidentified spies moved among the guests and noted a picture in the main reception room.",
                "The OCR reads 'nosed'; the scan reads 'noted'. The agents and painting remain unidentified.",
                ["cand-9790", "cand-9812", "cand-9813"],
                True,
                extra={"ocr_corrections": [{"source_line": 229, "ocr": "nosed", "print": "noted"}]},
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-picture-depicts-pisani",
            "cand-9813",
            "cand-1942",
            "picture_depicted_pisani_with_political_emblems",
            q(229, 230, "a picture showing Pisani", "completely new system’."),
            make_qualifiers(
                229,
                230,
                "The picture was reported as showing Pisani with emblems of Freedom, Power, Sovereignty, governmental collapse, and adoption of a new system.",
                "This is the spies' reported observation as retold by Haskell; the painter, individual object, and intended political meaning are not independently established.",
                ["cand-9813", "cand-1942"],
                True,
                extra={"reported_observation": "unnamed spies as quoted by Haskell"},
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-atmosphere-suspicion",
            "cand-9812",
            None,
            "celebration_atmosphere_described_as_suspicious",
            q(230, 230, "The atmosphere was fraught with suspicion", "suspicion"),
            make_qualifiers(
                230,
                230,
                "Haskell characterizes the atmosphere at the celebration as fraught with suspicion.",
                "This is Haskell's narrative characterization, not a separately attested relation.",
                ["cand-9812"],
                False,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-menus-at-celebration",
            "cand-9814",
            "cand-9812",
            "celebration_menus_were_carefully_noted",
            q(230, 230, "even the menus were carefully noted", "noted"),
            make_qualifiers(
                230,
                230,
                "Haskell says the menus at the celebration were carefully noted.",
                "The passive sentence does not name who noted the menus; the preceding spies are not asserted as the agents here.",
                ["cand-9814", "cand-9812"],
                True,
                relation_note="The event link is explicit in the paragraph context; the observer remains unnamed.",
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-saying-circulated",
            "cand-9815",
            "cand-9792",
            "saying_circulated_during_pisani_entry",
            q(233, 233, "and the saying went around:", "Dio ti guardi.’"),
            make_qualifiers(
                233,
                233,
                "Haskell reports a saying circulating during Pisani's entry, warning that the entry would be followed by a trial.",
                "The Italian saying is transcribed from the OCR. The scan reads 'l’Ingresso' and 'il Processo' where the OCR has '1’Ingresso' and 'ii Processo'.",
                ["cand-9815", "cand-9792"],
                True,
                extra={
                    "ocr_corrections": [
                        {"source_line": 233, "ocr": "1’Ingresso", "print": "l’Ingresso"},
                        {"source_line": 233, "ocr": "ii Processo", "print": "il Processo"},
                    ]
                },
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-boscarati-trouble-after-patron-disgrace",
            "cand-0411",
            "cand-1942",
            "boscarati_had_trouble_after_pisani_disgrace",
            q(235, 235, "also had trouble after the disgrace", "his patron."),
            make_qualifiers(
                235,
                235,
                "Haskell says Boscarati also had trouble after the disgrace of his patron, Pisani.",
                "The passage does not specify a charge, sentence, or the nature of Boscarati's trouble; it does not state causation.",
                ["cand-0411", "cand-1942"],
                True,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-guests-uneasy",
            "cand-9812",
            None,
            "guests_inferred_to_have_felt_uneasy",
            q(233, 233, "The guests must have felt uneasy", "uneasy"),
            make_qualifiers(
                233,
                233,
                "Haskell infers that the guests must have felt uneasy.",
                "The modal wording marks this as Haskell's inference, not a quoted guest report.",
                ["cand-9812"],
                False,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-prophecy-assessment",
            "cand-9815",
            None,
            "haskell_assessed_saying_as_apt",
            q(234, 234, "The prophecy was apt enough.", "apt enough."),
            make_qualifiers(
                234,
                234,
                "Haskell judges the circulating saying to have been apt.",
                "This is Haskell's retrospective assessment of the saying.",
                ["cand-9815"],
                False,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-boscarati-satire-assessment",
            "cand-0411",
            None,
            "haskell_characterized_boscarati_as_fond_of_satire",
            q(235, 235, "who was dangerously fond of satire", "satire"),
            make_qualifiers(
                235,
                235,
                "Haskell characterizes Felice Boscarati as dangerously fond of satire.",
                "This is Haskell's characterization, not a separately sourced assessment.",
                ["cand-0411"],
                False,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-prints-predate-election",
            "cand-9826",
            "cand-9792",
            "dallacqua_prints_predated_pisani_election",
            q(237, 237, "Not only are the prints by Cristoforo dall’Acqua", "Pisani’s election,"),
            make_qualifiers(
                237,
                237,
                "Haskell says the cited Dall'Acqua prints were dated before 1780, when Pisani's election was not yet in view.",
                "The print dates and the implication for commission chronology are reported in Haskell's note; the cited collection was not consulted.",
                ["cand-9826", "cand-0010", "cand-9792", "cand-1942", "cand-8262", "cand-9825"],
                True,
                speaker="Haskell's note",
                text_layer="authorial note",
                footnote=True,
                extra={
                    "continuation_from_statement_id": "st-chp10-p326-n03-haskell-explanation",
                    **note_refs_extra,
                },
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-riviera-pamphlets-attributed",
            "cand-2204",
            "cand-9806",
            "riviera_attributed_with_explanatory_pamphlets",
            q(237, 237, "Riviera’s own explanatory pamphlets", "one in French and one in Italian"),
            make_qualifiers(
                237,
                237,
                "Haskell attributes the explanatory La Educazione Virile pamphlets, in French and Italian, to Riviera.",
                "This preserves Haskell's attribution; the pamphlets were not independently consulted.",
                ["cand-2204", "cand-9806"],
                True,
                speaker="Haskell's note",
                text_layer="authorial note",
                footnote=True,
                extra=note_refs_extra,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-pamphlets-published-verona",
            "cand-9806",
            "cand-8681",
            "la_educazione_virile_pamphlets_published_in_verona_1773",
            q(237, 237, "were published in Verona", "1773."),
            make_qualifiers(
                237,
                237,
                "Haskell says the French and Italian pamphlet versions were published in Verona in 1773.",
                "The printed pamphlets were not independently consulted.",
                ["cand-9806", "cand-8681"],
                True,
                speaker="Haskell's note",
                text_layer="authorial note",
                footnote=True,
                extra=note_refs_extra,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-pamphlet-copies-correr",
            "cand-9806",
            "cand-8262",
            "pamphlet_versions_held_at_biblioteca_correr",
            q(237, 237, "Copies of both versions of this rare pamphlet", "Op.P.D. 3577-8.]"),
            make_qualifiers(
                237,
                237,
                "Haskell says copies of both pamphlet versions are held at Biblioteca Correr under shelfmark Op.P.D. 3577-8.",
                "This is a shelfmark locator reported in Haskell's note; the copies and catalogue were not consulted.",
                ["cand-9806", "cand-8262"],
                True,
                speaker="Haskell's note",
                text_layer="bibliographic note",
                footnote=True,
                extra={**note_refs_extra, "shelfmark": "Op.P.D. 3577-8"},
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-pictures-or-prints-exhibited",
            None,
            "cand-9792",
            "pictures_or_prints_possibly_exhibited_at_pisani_entry",
            q(237, 237, "On the other hand there is good reason to believe", "exhibited in 1780"),
            make_qualifiers(
                237,
                237,
                "Haskell says there is good reason to believe that the pictures or prints were exhibited in 1780.",
                "The source explicitly leaves the object as pictures or prints; it does not identify which form was exhibited. This is Haskell's qualified belief, not an independently verified event.",
                ["cand-9803", "cand-9826", "cand-9792", "cand-8359", "cand-9820", "cand-9821"],
                True,
                speaker="Haskell's note",
                text_layer="authorial note",
                relation_note="Open work endpoint: the source gives 'pictures or prints' as alternatives. The cited candidates are retained in mentions but neither is asserted as the sole object.",
                footnote=True,
                extra={
                    **note_refs_extra,
                    "citations": [
                        {"source_candidate_id": "cand-8359", "reported_by_haskell": "Zannandreis states the exhibition claim"},
                        {"source_candidate_id": "cand-9821", "author_candidate_id": "cand-9820", "year": "1924", "page": "145", "reported_by_haskell": "Moschini implies the prints were at Pisani's entry"},
                    ],
                },
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-moschini-prints-at-entry",
            "cand-9826",
            "cand-9792",
            "haskell_reports_moschini_reference_to_prints_at_pisani_entry",
            q(237, 237, "who refers to Dall’Acqua’s prints", "Pisani’"),
            make_qualifiers(
                237,
                237,
                "Haskell says Moschini's p.145 refers to Dall'Acqua's prints in the entry of Procurator Giorgio Pisani.",
                "This records Haskell's report of Moschini's wording; Moschini's cited page was not independently consulted.",
                ["cand-9826", "cand-0010", "cand-9792", "cand-1942", "cand-9820", "cand-9821"],
                True,
                speaker="Haskell's note",
                text_layer="reported bibliographic content",
                footnote=True,
                extra={
                    **note_refs_extra,
                    "citation_source_candidate_id": "cand-9821",
                    "citation_author_candidate_id": "cand-9820",
                    "cited_page": "145",
                },
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-pisani-boscarati-close-relations",
            "cand-1942",
            "cand-0411",
            "haskell_reported_close_relations_between_pisani_and_boscarati",
            q(237, 237, "we also know of the very close relations", "Pisani and Boscarati."),
            make_qualifiers(
                237,
                237,
                "Haskell says Pisani and Boscarati had very close relations.",
                "The nature, duration, and independent basis of the relationship are not specified here.",
                ["cand-1942", "cand-0411"],
                True,
                speaker="Haskell's note",
                text_layer="authorial note",
                relation_note="The source explicitly states a close relation but does not define its type.",
                footnote=True,
                extra=note_refs_extra,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-saleroom-version",
            "cand-9803",
            "cand-9827",
            "version_of_one_picture_reported_in_london_saleroom_1957",
            q(238, 239, "A version of one of the pictures", "February-March, 1957)"),
            make_qualifiers(
                238,
                239,
                "Haskell reports that a version of one of the pictures appeared in a London saleroom associated with Settecento Paintings—Arcade Gallery in February–March 1957.",
                "The specific picture, sale record, and version are not identified beyond this note; the gallery record was not independently consulted.",
                ["cand-9803", "cand-9827"],
                True,
                speaker="Haskell's note",
                text_layer="reported sale appearance",
                relation_note="The work-to-sale appearance is reported by Haskell; exact object identity remains unresolved.",
                footnote=True,
                extra=note_refs_extra,
            ),
            source_file,
        ),
        statement(
            "st-chp10-p327-n03-saleroom-original-assessment",
            "cand-9827",
            "cand-9803",
            "haskell_doubted_saleroom_version_was_an_original",
            q(239, 239, "but this is unlikely to be one of the originals", "large."),
            make_qualifiers(
                239,
                239,
                "Haskell considers the saleroom version unlikely to be one of the originals, which Zannandreis describes as large.",
                "This is Haskell's qualified authenticity assessment, not an independently verified object identification.",
                ["cand-9827", "cand-9803", "cand-8359"],
                False,
                speaker="Haskell's note",
                text_layer="authorial note",
                footnote=True,
                extra={**note_refs_extra, "citation_source_candidate_id": "cand-8359"},
            ),
            source_file,
        ),
    ]

    # Update existing p.327 statements in place, preserving their stable IDs.
    existing_updates = {
        "st-chp10-p327-political-pictures-procuratie": statement(
            "st-chp10-p327-political-pictures-procuratie",
            "cand-9807",
            "cand-9808",
            "political_pictures_exhibited_outside_procuratie_nuove",
            q(225, 225, "political, were exhibited outside", "Procuratie Nuove"),
            make_qualifiers(
                225,
                225,
                "Haskell says the more obviously political pictures were exhibited outside the Procuratie Nuove.",
                "The sentence begins on p.326; this quote preserves only the p.327 continuation. The individual pictures and their maker are not identified.",
                ["cand-9807", "cand-9808"],
                True,
                extra={
                    "continuation_from_segment_id": "chp-10:10_CHP-10_sec_ii:l210-222",
                    "continuation_prefix": "for other pictures, much more obviously",
                    "footnote_marker": 1,
                    "footnote_segment": NOTE_SEGMENT,
                    "footnote_refs": [{"marker": 1, "segment_id": NOTE_SEGMENT, "source_line": 336}],
                    "footnote_statement_ids": ["st-chp10-p327-n01-grimaldo-balbi-citation"],
                    "footnote_body_link_status": "linked",
                },
            ),
            source_file,
        ),
        "st-chp10-p327-palace-celebration-surveillance": statement(
            "st-chp10-p327-palace-celebration-surveillance",
            "cand-9790",
            "cand-9812",
            "spies_moved_among_guests_at_celebration",
            q(229, 229, "Spies moved among the guests", "guests"),
            make_qualifiers(
                229,
                229,
                "Haskell says unnamed spies moved among the guests at the celebration.",
                "The agents are not named or individually identified.",
                ["cand-9790", "cand-9812"],
                True,
            ),
            source_file,
        ),
        "st-chp10-p327-menu-verse-and-circulating-saying": statement(
            "st-chp10-p327-menu-verse-and-circulating-saying",
            "cand-9814",
            None,
            "menus_carried_two_french_lines",
            q(230, 232, "on them were printed two lines in French:", "Sont-ils les fondements de la République."),
            make_qualifiers(
                230,
                232,
                "Haskell transcribes two French lines printed on the celebration menus.",
                "The short couplet is preserved as text on the menus; no separate titled work or author is identified.",
                ["cand-9814"],
                False,
            ),
            source_file,
        ),
        "st-chp10-p327-inquisitors-act-four-days-later": statement(
            "st-chp10-p327-inquisitors-act-four-days-later",
            "cand-9739",
            "cand-9792",
            "inquisitors_moved_into_action_four_days_after_procession",
            q(234, 234, "Four days later", "action."),
            make_qualifiers(
                234,
                234,
                "Haskell says the Inquisitors moved into action four days after the procession.",
                "No calendar date or specific action is supplied; do not equate this phrase by itself with Pisani's arrest.",
                ["cand-9739", "cand-9792"],
                True,
            ),
            source_file,
        ),
        "st-chp10-p327-pisani-arrest-boscarati-trouble": statement(
            "st-chp10-p327-pisani-arrest-boscarati-trouble",
            "cand-1942",
            "cand-9816",
            "pisani_was_arrested",
            q(235, 235, "Pisani was arrested", "arrested"),
            make_qualifiers(
                235,
                235,
                "Haskell says Giorgio Pisani was arrested.",
                "No arrest date, charge, or procedure is given in this sentence.",
                ["cand-1942", "cand-9816"],
                True,
            ),
            source_file,
        ),
        "st-chp10-p327-dallacqua-not-involved-report": statement(
            "st-chp10-p327-dallacqua-not-involved-report",
            "cand-0010",
            "cand-1942",
            "later_writer_noted_dallacqua_not_involved_in_downfall",
            q(235, 236, "a later writer thought it worth recording", "Pisani’s downfall.3"),
            make_qualifiers(
                235,
                236,
                "Haskell reports that an unnamed later writer considered it significant that Cristoforo dall'Acqua was not involved in Pisani's downfall.",
                "This is a reported negative claim; it is not evidence that dall'Acqua was investigated or accused.",
                ["cand-0010", "cand-1942"],
                False,
                extra={
                    "footnote_marker": 3,
                    "footnote_segment": NOTE_SEGMENT,
                    "footnote_refs": [{"marker": 3, "segment_id": NOTE_SEGMENT, "source_line": 337}],
                    **note_refs_extra,
                },
            ),
            source_file,
        ),
        "st-chp10-p327-politics-and-art-separation": statement(
            "st-chp10-p327-politics-and-art-separation",
            "cand-9789",
            "cand-3678",
            "politics_and_art_separated_until_revolution_and_republic_collapse",
            q(236, 236, "Thereafter politics and art separated", "Venetian Republic."),
            make_qualifiers(
                236,
                236,
                "Haskell makes the broad periodizing claim that politics and art separated until the French Revolution and the collapse of the Venetian Republic.",
                "This is Haskell's generalization, not a claim that political art entirely ceased or that the two endpoints were simultaneous.",
                ["cand-9789", "cand-9828", "cand-3678"],
                False,
            ),
            source_file,
        ),
        "st-chp10-p327-less-offensive-poem-open": statement(
            "st-chp10-p327-less-offensive-poem-open",
            "cand-9829",
            "cand-9792",
            "poem_published_to_celebrate_pisani_entry",
            q(237, 237, "Among the less offensive poems", "Pisani’s"),
            make_qualifiers(
                237,
                237,
                "Haskell begins identifying a poem among those published to celebrate Pisani's election; p.328 identifies it as Il Filosofo dell'Alpi.",
                "The main-text sentence continues after the footnote on p.328 and is linked to its completing statement.",
                ["cand-9829", "cand-9792"],
                True,
                extra={
                    "continuation_to_segment_id": "chp-10:10_CHP-10_sec_ii:l241-246",
                    "continuation_status": "closed",
                    "continuation_closed_by_segment_id": "chp-10:10_CHP-10_sec_ii:l241-246",
                    "continuation_to_statement_id": "st-chp10-p328-filosofo-poem-identified",
                },
            ),
            source_file,
        ),
        "st-chp10-p326-n03-dating-and-exhibition": statement(
            "st-chp10-p326-n03-dating-and-exhibition",
            "cand-9803",
            "cand-9792",
            "haskell_rejected_claim_pictures_commissioned_for_pisani_entry",
            q(237, 237, "were especially commissioned", "Pisani’s entry."),
            make_qualifiers(
                237,
                237,
                "Continuing the p.326 note, Haskell says Zannandreis was wrong to say the pictures had been specially commissioned for Pisani's entry.",
                "This is a disputed commission claim: Haskell rejects it. The p.326 note statement supplies the antecedent, and no positive commission edge follows.",
                ["cand-9803", "cand-9792", "cand-8359"],
                True,
                speaker="Haskell's note",
                text_layer="authorial note",
                relation_note="Explicitly disputed commission relationship, retained as an S2 candidate with the rejection and source attribution preserved.",
                footnote=True,
                extra={
                    "continuation_from_statement_id": "st-chp10-p326-n03-haskell-explanation",
                    **note_refs_extra,
                },
            ),
            source_file,
        ),
    }

    for statement_id, replacement in existing_updates.items():
        statement_by_id[statement_id].update(replacement)

    # Complete the note and poem continuation links already present in adjacent segments.
    prior_note = statement_by_id["st-chp10-p326-n03-haskell-explanation"]
    prior_note["qualifiers"]["relation_candidate"] = False
    prior_note["qualifiers"]["continuation_to_statement_id"] = "st-chp10-p326-n03-dating-and-exhibition"
    citation = statement_by_id["st-chp10-p327-n03-moschini-citation"]
    citation["qualifiers"]["relation_candidate"] = False
    citation["qualifiers"]["qualification"] = (
        "Citation locator only; the cited page was not independently consulted. "
        "Haskell's claim about the page's content is separately recorded in the p.327 footnote continuation."
    )
    poem_completion = statement_by_id["st-chp10-p328-filosofo-poem-identified"]
    poem_completion["qualifiers"]["relation_candidate"] = True
    poem_completion["qualifiers"]["relation_candidate_note"] = "The source identifies the poem as published to celebrate Pisani's election."

    existing_ids = set(statement_by_id)
    if any(row["statement_id"] in existing_ids for row in rows_to_add):
        raise SystemExit("new statement ID collision; no writes made")
    for row in rows_to_add:
        if row["original_quote"] not in full_source:
            raise SystemExit(f"quote not anchored to OCR source: {row['statement_id']}")
        row["qualifiers"].setdefault("footnote_refs", [])
        statements.append(row)

    # Correct the existing venue mention and add source-local mentions for newly resolved endpoints.
    mention_fields, mentions = load_csv(MENTIONS)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    venue_mention = mention_by_id.get("m-s2-ch10-p326-327-0044")
    if not venue_mention or venue_mention["candidate_id"] != "cand-9812" or venue_mention["surface_form"] != "the palace":
        raise SystemExit("expected mis-mapped p.327 palace mention changed; no writes made")
    venue_mention["candidate_id"] = "cand-9811"
    venue_mention["note"] = "The palace is the celebration venue; cand-9812 is the event, not the place."

    prefix = "m-s2-ch10-p326-327-"
    suffixes = [int(row["mention_id"][len(prefix):]) for row in mentions if row["mention_id"].startswith(prefix)]
    next_mention = max(suffixes) + 1

    def add_mention(candidate: str, surface: str, context: str | None = None, which: int = 0, note: str = "") -> None:
        nonlocal next_mention
        start, end = mention_position(segment_text, surface, context, which)
        mention_id = f"{prefix}{next_mention:04d}"
        if mention_id in mention_by_id:
            raise SystemExit(f"mention ID collision: {mention_id}")
        row = {
            "mention_id": mention_id,
            "segment_id": SEGMENT,
            "candidate_id": candidate,
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": note,
        }
        mentions.append(row)
        mention_by_id[mention_id] = row
        next_mention += 1

    add_mention("cand-9812", "a huge celebration")
    add_mention("cand-1942", "Pisani", "a picture showing Pisani with various")
    add_mention("cand-9816", "was arrested", "Pisani was arrested")
    add_mention("cand-9826", "prints by Cristoforo dall’Acqua")
    add_mention("cand-9826", "Dall’Acqua’s prints")
    add_mention("cand-9821", "Moschini (1924, p. 145)")
    add_mention("cand-8262", "Biblioteca Correr", which=1)
    add_mention("cand-1942", "Pisani", "we also know of the very close relations between Pisani and Boscarati.")
    add_mention("cand-9803", "the pictures", "the pictures or the prints")
    add_mention("cand-9826", "the prints", "the pictures or the prints")
    add_mention("cand-9803", "one of the pictures")

    coverage_fields, coverage = load_csv(COVERAGE)
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or coverage_row["migration_status"] != "complete":
        raise SystemExit("expected completed p.327 coverage row missing; no writes made")
    coverage_row["note"] = (
        "p.327 main text reviewed against scan; p.326 note 3 continuation split from page text; "
        "OCR corrections recorded; p.327 poem continuation confirmed at p.328."
    )

    new_statement_ids = [row["statement_id"] for row in rows_to_add]
    unset_active = [
        row["statement_id"]
        for row in statements
        if row.get("segment_id") == SEGMENT and "relation_candidate" not in row.get("qualifiers", {})
    ]
    if unset_active:
        raise SystemExit(f"unclassified statement remains in p.327 segment: {unset_active}")

    print(json.dumps(
        {
            "mode": "apply" if args.apply else "preview",
            "input_hashes": current_hashes,
            "segment_statements_before": len(active_ids),
            "new_statement_count": len(rows_to_add),
            "new_statement_ids": new_statement_ids,
            "mentions_added": next_mention - max(suffixes) - 1,
            "coverage_updated": SEGMENT,
            "post_statement_count": len(statements),
            "post_mention_count": len(mentions),
        },
        ensure_ascii=False,
        indent=2,
    ))
    if not args.apply:
        return 0

    outputs = {
        STATEMENTS: dump_jsonl(statements),
        MENTIONS: dump_csv(mention_fields, mentions),
        COVERAGE: dump_csv(coverage_fields, coverage),
    }
    for path in outputs:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; no writes made: {backup}")
    for path in outputs:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    for path, payload in outputs.items():
        temp = path.with_name(path.name + ".tmp-p327-semantic-20261014")
        if temp.exists():
            raise SystemExit(f"staging file already exists; no writes made: {temp}")
        temp.write_bytes(payload)
    replaced = []
    try:
        for path in outputs:
            temp = path.with_name(path.name + ".tmp-p327-semantic-20261014")
            os.replace(temp, path)
            replaced.append(path.name)
    except OSError as exc:
        print(f"partial apply after {replaced}; backups and remaining staging files retained: {exc}", file=sys.stderr)
        raise
    print("APPLIED", {path.name: sha256(path) for path in outputs})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
