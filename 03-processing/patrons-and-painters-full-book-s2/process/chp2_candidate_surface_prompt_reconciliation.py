"""Adjudicate all 75 current chapter 2 candidate-surface prompts.

The locator is heuristic only. This source-locked plan records accepted spans,
no-write decisions, source-derived collection candidates, and two statement
endpoint corrections. Default mode is a read-only dry-run. --apply writes the
three tables with recovery copies and checks the exact post-write prompt set.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "b45c5ad6c5be4f2e16ea51ed2c782aa06745d7b80af993066df42255395f570f",
    "04-knowledge/tables/mentions.csv": "ffa49a2e539ff17ddd2fa27e3cc286ac67a89930515f0ddaafa9f66cdc380b26",
    "04-knowledge/tables/book-statements.jsonl": "c9f22335876d9e609022a0f5f7ece618277b5aa2e3798c13ffeefebb863268ad",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "scripts/audit_s2_candidate_surfaces.py": "44874e88e4940af624ad7b91b6f3e7d016f8c4083c203114e354b6e6622901ba",
    "02-sources/02-Markdown/02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
    "02-sources/02-Markdown/02_CHP-2_sec_iv.md": "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf",
    "02-sources/02-Markdown/02_CHP-2_sec_vii.md": "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c",
}


def accepted(
    segment_id: str,
    prompt_start: int,
    prompt_end: int,
    prompt_surface: str,
    candidate_id: str,
    surface_form: str,
    start_char: int,
    note: str,
) -> dict[str, object]:
    return {
        "segment_id": segment_id,
        "prompt_start": prompt_start,
        "prompt_end": prompt_end,
        "prompt_surface": prompt_surface,
        "candidate_id": candidate_id,
        "surface_form": surface_form,
        "start_char": start_char,
        "end_char": start_char + len(surface_form),
        "note": note,
    }


def prompt(segment_id: str, start: int, end: int, surface: str, reason: str) -> dict[str, object]:
    return {
        "segment_id": segment_id,
        "start_char": start,
        "end_char": end,
        "surface_form": surface,
        "reason": reason,
    }


SI108 = "chp-2:02_CHP-2_sec_i:l108-119"
SI124 = "chp-2:02_CHP-2_sec_i:l124-157"
SI3 = "chp-2:02_CHP-2_sec_i:l3-7"
SI44 = "chp-2:02_CHP-2_sec_i:l44-53"
SI55 = "chp-2:02_CHP-2_sec_i:l55-69"
SI71 = "chp-2:02_CHP-2_sec_i:l71-80"
SII118 = "chp-2:02_CHP-2_sec_ii:l118-125"
SII127 = "chp-2:02_CHP-2_sec_ii:l127-139"
SII147 = "chp-2:02_CHP-2_sec_ii:l147-193"
SII30 = "chp-2:02_CHP-2_sec_ii:l30-40"
SII42 = "chp-2:02_CHP-2_sec_ii:l42-50"
SII52 = "chp-2:02_CHP-2_sec_ii:l52-60"
SII71 = "chp-2:02_CHP-2_sec_ii:l71-78"
SII80 = "chp-2:02_CHP-2_sec_ii:l80-89"
SII91 = "chp-2:02_CHP-2_sec_ii:l91-104"
SIV106 = "chp-2:02_CHP-2_sec_iv:l106-112"
SIV114 = "chp-2:02_CHP-2_sec_iv:l114-125"
SIV127 = "chp-2:02_CHP-2_sec_iv:l127-137"
SIV139 = "chp-2:02_CHP-2_sec_iv:l139-152"
SIV171 = "chp-2:02_CHP-2_sec_iv:l171-179"
SIV181 = "chp-2:02_CHP-2_sec_iv:l181-188"
SIV19 = "chp-2:02_CHP-2_sec_iv:l19-29"
SIV190 = "chp-2:02_CHP-2_sec_iv:l190-245"
SIV3 = "chp-2:02_CHP-2_sec_iv:l3-4"
SIV45 = "chp-2:02_CHP-2_sec_iv:l45-52"
SIV54 = "chp-2:02_CHP-2_sec_iv:l54-63"
SIV6 = "chp-2:02_CHP-2_sec_iv:l6-17"
SIV65 = "chp-2:02_CHP-2_sec_iv:l65-77"
SIV79 = "chp-2:02_CHP-2_sec_iv:l79-89"
SIV91 = "chp-2:02_CHP-2_sec_iv:l91-94"
SVII21 = "chp-2:02_CHP-2_sec_vii:l21-30"
SVII38 = "chp-2:02_CHP-2_sec_vii:l38-54"
SVII5 = "chp-2:02_CHP-2_sec_vii:l5-19"


ACCEPTED = [
    accepted(SI108, 1500, 1511, "old masters", "cand-4288", "old masters", 1500,
             "Historical art-historical category, not a single work."),
    accepted(SI108, 2318, 2325, "in Rome", "cand-3126", "Rome", 2321,
             "Exact city substring; the locator's longer phrase collides with unrelated index subentries."),
    accepted(SI44, 797, 804, "subject", "cand-0840", "subject", 797,
             "Commissioned subject discussed as a term of patronal choice."),
    accepted(SI55, 920, 927, "subject", "cand-0840", "subject", 920,
             "The quoted commission leaves subject choice open to the patron."),
    accepted(SI71, 2815, 2825, "collection", "cand-11474", "his collection", 2811,
             "The possessive collection is identified by the next segment as Scipione's collection of paintings; type and broader identity remain open."),
    accepted(SII127, 2557, 2564, "In Rome", "cand-3126", "Rome", 2560,
             "Exact city substring; the locator's longer phrase collides with unrelated index subentries."),
    accepted(SII147, 559, 565, "palace", "cand-0240", "palace", 559,
             "The footnote refers back to the Barberini palace named in this passage."),
    accepted(SII147, 2559, 2569, "collection", "cand-11475", "Sacchetti collection", 2549,
             "The footnote names the collection through its inventories; the repository is not the collection itself."),
    accepted(SII42, 1719, 1725, "botany", "cand-5634", "botany", 1719,
             "Named disciplinary term in the botanical observation."),
    accepted(SII52, 1138, 1146, "St Peter", "cand-4231", "St Peter", 1138,
             "The apostle Peter, not Guercino's indexed work titled St Peter."),
    accepted(SII80, 248, 255, "Raphael", "cand-2098", "Raphael", 248,
             "Person reference in the comparison of artistic qualities."),
    accepted(SII80, 295, 301, "Titian", "cand-2630", "Titian", 295,
             "Person reference in the same comparison."),
    accepted(SIV139, 1678, 1684, "botany", "cand-5634", "botany", 1678,
             "Named disciplinary term in the description of the Barberini palace library."),
    accepted(SIV139, 1769, 1775, "palace", "cand-0240", "palace", 1769,
             "Definite reference to the Barberini palace named earlier in the passage."),
    accepted(SIV139, 1898, 1905, "theatre", "cand-0241", "theatre", 1898,
             "The theatre subentry of the Barberini palace, not an unrelated theatre candidate."),
    accepted(SIV19, 2470, 2488, "private collection", "cand-11476", "private collection", 2470,
             "Francesco's own Poussin collection; a collection grouping, not a single work or repository. The nested 'collection' prompt maps to this same mention."),
    accepted(SIV19, 2478, 2488, "collection", "cand-11476", "private collection", 2470,
             "Francesco's own Poussin collection; a collection grouping, not a single work or repository. The nested 'collection' prompt maps to this same mention."),
    accepted(SIV190, 2044, 2050, "palace", "cand-0398", "palace", 2044,
             "The note identifies the building as the Borghese Palace through its 1619 purchase history."),
    accepted(SIV190, 2625, 2631, "palace", "cand-0398", "palace", 2625,
             "Same Borghese Palace, identified in the preceding note."),
    accepted(SIV190, 2894, 2900, "palace", "cand-0398", "palace", 2894,
             "Same Borghese Palace in the Aurora anecdote."),
    accepted(SIV190, 3034, 3041, "in Rome", "cand-3126", "Rome", 3037,
             "Exact city substring; the locator's longer phrase collides with unrelated index subentries."),
    accepted(SIV190, 3340, 3346, "palace", "cand-0398", "palace", 3340,
             "The note explicitly says the palace then belonged to Scipione Borghese."),
    accepted(SIV190, 4232, 4249, "and the Barberini", "cand-0198", "the Barberini", 4236,
             "Exact family span inside the locator's longer phrase; specific family/subgroup alignment remains for S3."),
    accepted(SIV190, 4627, 4633, "Louvre", "cand-1450", "Louvre", 4627,
             "Repository/place, not a Louvre collection object."),
    accepted(SIV190, 4642, 4656, "Palazzo Ducale", "cand-1806", "Palazzo Ducale", 4642,
             "The Ducal Palace in Urbino, not a generic palace."),
    accepted(SIV190, 5630, 5636, "Louvre", "cand-1450", "Louvre", 5630,
             "Repository/place for the Poussin version."),
    accepted(SIV190, 6055, 6061, "Aurora", "cand-2128", "Aurora", 6055,
             "Guido Reni's indexed Aurora, not Guercino's distinct Aurora work."),
    accepted(SIV190, 6076, 6082, "palace", "cand-4291", "family palace", 6069,
             "The footnote's family palace is locally identified as Casino Rospigliosi in the same Reni Aurora context."),
    accepted(SIV190, 6338, 6356, "Arcadian Shepherds", "cand-1995", "Arcadian Shepherds", 6338,
             "The Louvre location identifies the indexed second version."),
    accepted(SIV190, 6510, 6516, "Madrid", "cand-1481", "Madrid", 6510,
             "City reference; use the main Madrid place candidate, not its indexed subentries."),
    accepted(SIV6, 424, 435, "art patrons", "cand-4129", "art patrons", 424,
             "The exact social-role concept; the overlapping 'Italian art' phrase is a modifier."),
    accepted(SIV65, 298, 308, "collection", "cand-11477", "notable collection", 290,
             "Guido Bentivoglio's collection grouping, described with a Van Dyck Crucifixion and a portrait."),
    accepted(SIV65, 1720, 1731, "old masters", "cand-4288", "old masters", 1720,
             "Historical art-historical category, not a single work."),
    accepted(SIV65, 2011, 2021, "collection", "cand-11478", "Ducal collection", 2005,
             "Unidentified ducal collection from which Enzo procured Dosso works; keep distinct from the Urbino collection candidate pending S3."),
    accepted(SIV79, 633, 639, "palace", "cand-0240", "palace", 633,
             "The new Barberini palace recommended for decoration."),
    accepted(SIV79, 1838, 1844, "palace", "cand-0240", "palace", 1838,
             "Definite reference to the Barberini palace in the ongoing decoration account."),
    accepted(SIV79, 2159, 2166, "subject", "cand-0840", "subject", 2159,
             "An explicitly named proposed subject in the patronal art discussion."),
    accepted(SVII21, 1836, 1845, "Velasquez", "cand-2709", "Velasquez", 1836,
             "The Spanish painter, not same-name work or event index subentries."),
    accepted(SVII38, 840, 847, "in Rome", "cand-3126", "Rome", 843,
             "Exact city substring; the locator's longer phrase collides with unrelated index subentries."),
    accepted(SVII5, 2770, 2777, "subject", "cand-0840", "subject", 2770,
             "The commemorative subject selected by the cardinals from the Anabasis."),
]


NO_WRITE = [
    prompt(SI108, 907, 915, "churches", "generic_place_class"),
    prompt(SI3, 420, 426, "poetry", "ordinary_poetry_reference"),
    prompt(SI3, 1714, 1722, "churches", "generic_place_class"),
    prompt(SI44, 140, 146, "poetry", "ordinary_poetry_reference"),
    prompt(SI44, 1843, 1850, "fortune", "ordinary_fortune_reference"),
    prompt(SI55, 2564, 2570, "poetry", "ordinary_poetry_reference"),
    prompt(SI71, 617, 625, "churches", "generic_place_class"),
    prompt(SI82 := "chp-2:02_CHP-2_sec_i:l82-93", 1257, 1264, "fortune", "ordinary_fortune_reference"),
    prompt(SI82, 2161, 2172, "temperament", "ordinary_temperament"),
    prompt(SI124, 2629, 2636, "subject", "ordinary_study_subject"),
    prompt(SII118, 298, 310, "monuments to", "generic_monuments"),
    prompt(SII127, 2874, 2882, "churches", "generic_place_class"),
    prompt("chp-2:02_CHP-2_sec_ii:l3-8", 1198, 1205, "fortune", "ordinary_fortune_reference"),
    prompt(SII30, 2778, 2784, "palace", "generic_or_narrative_palace"),
    prompt(SII71, 1534, 1540, "poetry", "ordinary_poetry_reference"),
    prompt(SII80, 88, 105, "views on painting", "ordinary_views"),
    prompt(SII91, 365, 371, "poetry", "ordinary_poetry_reference"),
    prompt(SII91, 1570, 1579, "character", "ordinary_character_quality"),
    prompt(SIV106, 1666, 1672, "prince", "generic_title_or_role"),
    prompt(SIV106, 2149, 2157, "churches", "generic_place_class"),
    prompt(SIV114, 37, 48, "temperament", "ordinary_temperament"),
    prompt(SIV127, 1371, 1379, "churches", "generic_place_class"),
    prompt(SIV139, 1605, 1611, "poetry", "ordinary_poetry_reference"),
    prompt(SIV171, 495, 501, "palace", "generic_or_narrative_palace"),
    prompt(SIV171, 1977, 1983, "poetry", "ordinary_poetry_reference"),
    prompt(SIV171, 1977, 1986, "poetry of", "ordinary_poetry_reference"),
    prompt(SIV181, 1470, 1478, "drawings", "generic_medium"),
    prompt(SIV19, 1377, 1385, "payments", "generic_payment"),
    prompt(SIV3, 460, 469, "character", "ordinary_character_quality"),
    prompt(SIV45, 758, 767, "character", "ordinary_character_quality"),
    prompt(SIV54, 51, 57, "palace", "generic_or_narrative_palace"),
    prompt(SIV6, 416, 427, "Italian art", "ordinary_modifier"),
    prompt(SIV79, 2425, 2438, "divine wisdom", "abstract_phrase_not_work"),
    prompt(SIV91, 3100, 3109, "character", "ordinary_character_quality"),
    prompt(SVII5, 2384, 2391, "fortune", "ordinary_fortune_reference"),
]

NO_WRITE_TEXT = {
    "generic_place_class": "Plural generic reference; no individually identified site is meant.",
    "ordinary_poetry_reference": "Ordinary literary activity or quality, not the indexed conceptual work or a distinct entity.",
    "ordinary_fortune_reference": "Ordinary reference to wealth, luck, or reversal of fortune, not the indexed work Fortune.",
    "ordinary_temperament": "Ordinary personal disposition, not the indexed concept-history usage of artistic temperament.",
    "ordinary_study_subject": "Generic object of a modern study; it does not refer to a distinct entity or the indexed patronal subject concept.",
    "generic_monuments": "Generic class of public monuments, with no particular monument identified.",
    "generic_or_narrative_palace": "Generic architectural description, or a palace in a literary anecdote; no indexed building is identified.",
    "ordinary_views": "Ordinary phrase for Marcello's opinions about painting, not a distinct conceptual entity.",
    "ordinary_character_quality": "Ordinary use of character as a personal quality, not a distinct person or work.",
    "generic_title_or_role": "Generic secular title or role, not the indexed work The Prince or a named person.",
    "generic_medium": "Generic reference to drawings as a medium; no distinct drawing is identified.",
    "generic_payment": "Ordinary advance payments, not a distinct document or entity.",
    "ordinary_modifier": "Italian art modifies the social-role phrase; the overlapping exact concept is Art patrons.",
    "abstract_phrase_not_work": "Lowercase abstract phrase in a quotation, not the indexed work Divine Wisdom.",
}

EXPECTED_NO_WRITE_COUNTS = {
    "generic_place_class": 6,
    "ordinary_poetry_reference": 8,
    "ordinary_fortune_reference": 4,
    "ordinary_temperament": 2,
    "ordinary_study_subject": 1,
    "generic_monuments": 1,
    "generic_or_narrative_palace": 3,
    "ordinary_views": 1,
    "ordinary_character_quality": 4,
    "generic_title_or_role": 1,
    "generic_medium": 1,
    "generic_payment": 1,
    "ordinary_modifier": 1,
    "abstract_phrase_not_work": 1,
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11474", "index_entry_id": "", "canonical_name": "Scipione Borghese’s collection of paintings",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell describes a collection of paintings and later calls them Scipione's collections. The extent and formal identity of this collection are unresolved; keep distinct from other Borghese collections pending S3.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-2:02_CHP-2_sec_i:l82-93#L82",
    },
    {
        "candidate_id": "cand-11475", "index_entry_id": "", "canonical_name": "Sacchetti collection",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "The footnote cites inventories of the Sacchetti collection and reports that most of it is now in the Pinacoteca Capitolina. Do not equate the historical collection with the present repository.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-2:02_CHP-2_sec_ii:l147-193#L179",
    },
    {
        "candidate_id": "cand-11476", "index_entry_id": "", "canonical_name": "Francesco Barberini’s private collection of Poussin works",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says Francesco bought one or two other Poussin works for his private collection. This is a source-described collection grouping, not a single work; the collection's broader identity remains open.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-2:02_CHP-2_sec_iv:l19-29#L28",
    },
    {
        "candidate_id": "cand-11477", "index_entry_id": "", "canonical_name": "Guido Bentivoglio’s art collection",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell describes a notable collection assembled by Cardinal Guido Bentivoglio, including a Van Dyck Crucifixion and a portrait. Keep the collection grouping distinct from its component works.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-2:02_CHP-2_sec_iv:l65-77#L68",
    },
    {
        "candidate_id": "cand-11478", "index_entry_id": "", "canonical_name": "Unidentified Ducal collection of Dosso Dossi works",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell says Enzo procured Dosso works from the Ducal collection for a cardinal's gallery. The owner and location are not specified here; keep distinct from cand-4743, the source-described Urbino collection, pending S3.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-2:02_CHP-2_sec_iv:l65-77#L74",
    },
]

EXTRA_MENTIONS = [
    {
        "segment_id": SIV190, "candidate_id": "cand-4291", "surface_form": "Casino Rospigliosi",
        "start_char": 6105, "end_char": 6123,
        "note": "Proper place name in Haskell's p.57 footnote; locally identifies the family palace in the same Guido Reni Aurora discussion. Cross-chapter identity alignment remains open for S3.",
    },
]

REMAP_MENTIONS = {
    "m-chp2-seci-l82-93-0001": {
        "old_candidate_id": "cand-0396", "new_candidate_id": "cand-11474",
        "note": "Scipione's collection of paintings; source-derived collection candidate, with formal identity and type left open.",
    },
    "m-chp2-seci-l82-93-0007": {
        "old_candidate_id": "cand-0396", "new_candidate_id": "cand-11474",
        "note": "Scipione's collections; source-derived collection candidate, not the person-index subentry.",
    },
}

NEW_STATEMENT = {
    "statement_id": "st-chp2-seciv-l190-245-casino-rospigliosi-belonged-to-bentivoglio",
    "segment_id": SIV190,
    "subject_candidate_id": "cand-4291",
    "object_candidate_id": "cand-0291",
    "predicate": "casino_rospigliosi_belonged_to_cardinal_bentivoglio_in_1621_1623",
    "qualifiers": {
        "source_line_start": 242,
        "source_line_end": 242,
        "printed_page": 57,
        "pdf_physical_page": 46,
        "claim": "Haskell states that the Casino Rospigliosi belonged to Cardinal Guido Bentivoglio during 1621–1623.",
        "speaker": "Haskell, footnote",
        "text_layer": "substantive footnote",
        "qualification": "This is Haskell's reported ownership context, not an independently verified property record and not proof that Rospigliosi and Guercino had no contact by any route. The OCR spelling is Bentivoglia; the print reads Bentivoglio.",
        "mentioned_candidate_ids": ["cand-4291", "cand-0291"],
        "footnote_number": 3,
        "relation_candidate": True,
        "relation_candidate_note": "Book-reported ownership for 1621–1623; retain as an S2 candidate pending independent source verification.",
        "date": "1621-1623",
        "ocr_corrections": [{
            "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
            "source_line": 242,
            "ocr": "Bentivoglia",
            "print": "Bentivoglio",
            "basis": "CHP-2.pdf physical page 46",
        }],
    },
    "original_quote": "for at that time the Casino Rospigliosi belonged to Cardinal Bentivoglia",
    "origin": "book",
    "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
}

STATEMENT_UPDATES = {
    "st-chp2-seci-l71-80-collection-fragment": {
        "expected_object": None,
        "object_candidate_id": "cand-11474",
        "qualification": "The source segment ends after “a wonderful”; the immediately following segment continues with “collection of paintings”. The collection candidate is linked from that continuation; its broader identity and formal type remain open.",
    },
    "st-chp2-seci-l71-80-deposition-removal": {
        "expected_object": "cand-0394",
        "object_candidate_id": "cand-11474",
    },
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 table changes")
ARGS = parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def sig(value: dict[str, object]) -> tuple[str, int, int]:
    return str(value["segment_id"]), int(value["start_char"]), int(value["end_char"])


def encode_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    raw = path.read_bytes()
    line_ending = "\r\n" if b"\r\n" in raw else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + payload if raw.startswith(b"\xef\xbb\xbf") else payload


def atomic_write(path: Path, payload: bytes) -> None:
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as stream:
        stream.write(payload)
        temporary = Path(stream.name)
    temporary.replace(path)


for relative_path, expected_hash in EXPECTED_HASHES.items():
    actual_hash = sha256(ROOT / relative_path)
    if actual_hash != expected_hash:
        raise SystemExit(f"input hash mismatch: {relative_path}: {actual_hash}")

candidate_fields, candidate_rows = read_csv(CANDIDATES)
mention_fields, mention_rows = read_csv(MENTIONS)
expected_candidate_fields = [
    "candidate_id", "index_entry_id", "canonical_name", "index_page_range", "suggested_type",
    "status", "index_source_file", "sub_entry", "detail", "exclude_reason", "candidate_origin",
    "candidate_source_ref",
]
expected_mention_fields = [
    "mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note",
]
if candidate_fields != expected_candidate_fields or mention_fields != expected_mention_fields:
    raise SystemExit("unexpected candidate or mention CSV schema")

candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
if len(candidate_by_id) != len(candidate_rows):
    raise SystemExit("duplicate candidate IDs")
if max(int(value.split("-")[1]) for value in candidate_by_id) != 11473:
    raise SystemExit("candidate ID sequence changed; do not apply this fixed plan")
if any(row["candidate_id"] in candidate_by_id for row in NEW_CANDIDATES):
    raise SystemExit("one or more planned collection candidate IDs already exist")
if candidate_by_id["cand-4291"]["canonical_name"] != "Borghese casino for Reni’s Aurora fresco (unidentified)":
    raise SystemExit("cand-4291 changed since this plan was reviewed")

segments = {
    row["segment_id"]: row
    for row in (
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    )
}
summary, hits = surface_audit.audit("chp-2", 6)
if int(summary["uncovered_candidate_surface_spans"]) != 75:
    raise SystemExit(f"expected 75 prompts, found {summary['uncovered_candidate_surface_spans']}")
hit_by_sig = {sig(hit): hit for hit in hits}
if len(hit_by_sig) != len(hits):
    raise SystemExit("duplicate locator prompt signatures")

accepted_by_sig: dict[tuple[str, int, int], dict[str, object]] = {}
for entry in ACCEPTED:
    key = (str(entry["segment_id"]), int(entry["prompt_start"]), int(entry["prompt_end"]))
    if key in accepted_by_sig:
        raise SystemExit(f"duplicate accepted prompt in plan: {key}")
    accepted_by_sig[key] = entry
no_write_by_sig: dict[tuple[str, int, int], dict[str, object]] = {}
for entry in NO_WRITE:
    key = sig(entry)
    if key in no_write_by_sig:
        raise SystemExit(f"duplicate no-write prompt in plan: {key}")
    no_write_by_sig[key] = entry
if set(accepted_by_sig).intersection(no_write_by_sig):
    raise SystemExit("accepted and no-write prompt plans overlap")
if set(accepted_by_sig) | set(no_write_by_sig) != set(hit_by_sig):
    missing = sorted(set(hit_by_sig) - set(accepted_by_sig) - set(no_write_by_sig))
    extra = sorted((set(accepted_by_sig) | set(no_write_by_sig)) - set(hit_by_sig))
    raise SystemExit(f"prompt partition mismatch; unadjudicated={missing}; stale={extra}")

no_write_counts = Counter(str(row["reason"]) for row in NO_WRITE)
if len(ACCEPTED) != 40 or len(NO_WRITE) != 35 or dict(no_write_counts) != EXPECTED_NO_WRITE_COUNTS:
    raise SystemExit(f"adjudication count mismatch: accepted={len(ACCEPTED)}, no_write={dict(no_write_counts)}")

all_candidate_rows = candidate_rows + NEW_CANDIDATES
all_candidates = {row["candidate_id"]: row for row in all_candidate_rows}
source_text_cache: dict[str, str] = {}
planned_by_natural_key: dict[tuple[str, int, int], dict[str, str]] = {}
for entry in ACCEPTED:
    key = (str(entry["segment_id"]), int(entry["prompt_start"]), int(entry["prompt_end"]))
    hit = hit_by_sig[key]
    if hit["surface_form"] != entry["prompt_surface"]:
        raise SystemExit(f"prompt text mismatch: {key}")
    segment_id = str(entry["segment_id"])
    candidate_id = str(entry["candidate_id"])
    if candidate_id not in all_candidates:
        raise SystemExit(f"unknown planned candidate: {candidate_id}")
    candidate_type = all_candidates[candidate_id]["suggested_type"]
    if not candidate_type and candidate_id not in {row["candidate_id"] for row in NEW_CANDIDATES}:
        raise SystemExit(f"untyped candidate cannot receive this planned mention: {candidate_id}")
    segment = segments.get(segment_id)
    if not segment:
        raise SystemExit(f"unknown segment: {segment_id}")
    if segment_id not in source_text_cache:
        source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
        source_text_cache[segment_id] = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    start, end = int(entry["start_char"]), int(entry["end_char"])
    surface = str(entry["surface_form"])
    source_text = source_text_cache[segment_id]
    if source_text[start:end] != surface:
        raise SystemExit(f"source span mismatch: {segment_id} {start}:{end} {surface!r}")
    if start >= int(entry["prompt_end"]) or end <= int(entry["prompt_start"]):
        raise SystemExit(f"chosen mention does not overlap prompt: {key}")
    natural_key = (segment_id, start, end)
    planned_row = {
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": str(entry["note"]),
    }
    existing_plan = planned_by_natural_key.get(natural_key)
    if existing_plan and existing_plan != planned_row:
        raise SystemExit(f"conflicting accepted prompts share one mention span: {natural_key}")
    planned_by_natural_key[natural_key] = planned_row

existing_keys = {
    (row["segment_id"], int(row["start_char"]), int(row["end_char"])) for row in mention_rows
}
existing_ids = {row["mention_id"] for row in mention_rows}
for item in EXTRA_MENTIONS:
    segment_id = str(item["segment_id"])
    if segment_id not in segments:
        raise SystemExit(f"unknown extra-mention segment: {segment_id}")
    if segment_id not in source_text_cache:
        seg = segments[segment_id]
        lines = (ROOT / seg["source_file"]).read_text(encoding="utf-8-sig").splitlines()
        source_text_cache[segment_id] = "\n".join(lines[seg["line_start"] - 1:seg["line_end"]])
    start, end = int(item["start_char"]), int(item["end_char"])
    if source_text_cache[segment_id][start:end] != item["surface_form"]:
        raise SystemExit(f"extra mention span mismatch: {segment_id} {start}:{end}")
    natural_key = (segment_id, start, end)
    if natural_key in planned_by_natural_key or natural_key in existing_keys:
        raise SystemExit(f"extra mention key already planned or present: {natural_key}")
    planned_by_natural_key[natural_key] = {**item, "start_char": str(start), "end_char": str(end)}

for row in planned_by_natural_key.values():
    segment_id = str(row["segment_id"])
    start, end = int(row["start_char"]), int(row["end_char"])
    if (segment_id, start, end) in existing_keys:
        raise SystemExit(f"mention natural key already exists: {(segment_id, start, end)}")
    for old in mention_rows:
        old_start, old_end = int(old["start_char"]), int(old["end_char"])
        if old["segment_id"] == segment_id and start < old_end and end > old_start:
            raise SystemExit(f"planned mention overlaps an existing mention: {(segment_id, start, end)}")

remapped_mentions = {row["mention_id"]: row for row in mention_rows}
for mention_id, update in REMAP_MENTIONS.items():
    row = remapped_mentions.get(mention_id)
    if not row or row["candidate_id"] != update["old_candidate_id"]:
        raise SystemExit(f"mention remap precondition failed: {mention_id}")
    row["candidate_id"] = update["new_candidate_id"]
    row["note"] = update["note"]

for row in NEW_CANDIDATES:
    if row["suggested_type"] or row["candidate_origin"] != "body-mention" or row["status"] != "open":
        raise SystemExit(f"collection candidate must remain type-pending and source-derived: {row['candidate_id']}")

new_mention_rows = []
for natural_key, planned in planned_by_natural_key.items():
    digest = hashlib.sha256(
        f"{natural_key[0]}|{natural_key[1]}|{natural_key[2]}|{planned['candidate_id']}".encode("utf-8")
    ).hexdigest()[:16]
    mention_id = f"m-s2-chp2-surface-{digest}"
    if mention_id in existing_ids:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    new_mention_rows.append({
        "mention_id": mention_id,
        "segment_id": str(planned["segment_id"]),
        "candidate_id": str(planned["candidate_id"]),
        "surface_form": str(planned["surface_form"]),
        "start_char": str(planned["start_char"]),
        "end_char": str(planned["end_char"]),
        "note": str(planned["note"]),
    })
    existing_ids.add(mention_id)

statement_lines = STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
statement_rows = [json.loads(line) for line in statement_lines if line.strip()]
statement_by_id = {row["statement_id"]: row for row in statement_rows}
if len(statement_by_id) != len(statement_rows):
    raise SystemExit("duplicate statement IDs")
if NEW_STATEMENT["statement_id"] in statement_by_id:
    raise SystemExit("planned ownership statement already exists")
for statement_id, update in STATEMENT_UPDATES.items():
    row = statement_by_id.get(statement_id)
    if not row or row.get("object_candidate_id") != update["expected_object"]:
        raise SystemExit(f"statement endpoint precondition failed: {statement_id}")
    row["object_candidate_id"] = update["object_candidate_id"]
    if "qualification" in update:
        row["qualifiers"]["qualification"] = update["qualification"]
statement_by_id[NEW_STATEMENT["statement_id"]] = NEW_STATEMENT

written_spans = [
    (str(row["segment_id"]), int(row["start_char"]), int(row["end_char"]))
    for row in planned_by_natural_key.values()
]
expected_residual = {
    key for key in no_write_by_sig
    if not any(
        segment_id == key[0] and start < key[2] and end > key[1]
        for segment_id, start, end in written_spans
    )
}
if len(expected_residual) != 34:
    raise SystemExit(f"unexpected expected residual prompt count: {len(expected_residual)}")

plan_sha = hashlib.sha256(json.dumps({
    "accepted": ACCEPTED,
    "no_write": NO_WRITE,
    "no_write_reasons": NO_WRITE_TEXT,
    "new_candidates": NEW_CANDIDATES,
    "extra_mentions": EXTRA_MENTIONS,
    "remap_mentions": REMAP_MENTIONS,
    "statement_updates": STATEMENT_UPDATES,
    "new_statement": NEW_STATEMENT,
}, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

print(f"chapter={summary['chapter']}")
print(f"reviewed_segments_scanned={summary['reviewed_segments_scanned']}")
print(f"candidate_surface_prompts={len(hits)}")
print(f"accepted_prompt_signatures={len(ACCEPTED)}")
print(f"new_mentions={len(new_mention_rows)}")
print(f"no_write_prompt_signatures={len(NO_WRITE)}")
for reason, count in sorted(no_write_counts.items()):
    print(f"no_write[{reason}]={count}: {NO_WRITE_TEXT[reason]}")
print(f"new_type_pending_candidates={len(NEW_CANDIDATES)}")
print(f"remapped_mentions={len(REMAP_MENTIONS)}")
print(f"statement_rows_added=1 statement_rows_updated={len(STATEMENT_UPDATES)}")
print(f"mentions_before={len(mention_rows)} mentions_after={len(mention_rows) + len(new_mention_rows)}")
print(f"candidates_before={len(candidate_rows)} candidates_after={len(candidate_rows) + len(NEW_CANDIDATES)}")
print(f"statements_before={len(statement_rows)} statements_after={len(statement_rows) + 1}")
print(f"expected_post_write_prompts={len(expected_residual)}")
print(f"plan_sha256={plan_sha}")
if not ARGS.apply:
    print("mode=dry-run; no files written")
    raise SystemExit(0)

recovery = Path(tempfile.gettempdir()) / (
    "pnp-s2-chp2-surface-prompts-" + datetime.now().strftime("%Y%m%d-%H%M%S")
)
recovery.mkdir(parents=True, exist_ok=False)
paths = [CANDIDATES, MENTIONS, STATEMENTS]
backups = {}
for path in paths:
    backup = recovery / path.name
    shutil.copy2(path, backup)
    backups[path] = backup
    print(f"recovery_copy[{path.name}]={backup}")

candidate_after = candidate_rows + NEW_CANDIDATES
mentions_after = mention_rows + new_mention_rows
candidate_payload = encode_csv(CANDIDATES, candidate_fields, candidate_after)
mention_payload = encode_csv(MENTIONS, mention_fields, mentions_after)

raw_statement_bytes = STATEMENTS.read_bytes()
line_ending = "\r\n" if b"\r\n" in raw_statement_bytes else "\n"
bom = raw_statement_bytes.startswith(b"\xef\xbb\xbf")
output_statement_lines = []
changed_ids = set(STATEMENT_UPDATES)
for line in statement_lines:
    if not line.strip():
        output_statement_lines.append(line)
        continue
    parsed = json.loads(line)
    statement_id = parsed["statement_id"]
    if statement_id in changed_ids:
        output_statement_lines.append(json.dumps(statement_by_id[statement_id], ensure_ascii=False, separators=(",", ":")))
    else:
        output_statement_lines.append(line)
output_statement_lines.append(json.dumps(NEW_STATEMENT, ensure_ascii=False, separators=(",", ":")))
statement_text = line_ending.join(output_statement_lines)
if raw_statement_bytes.endswith((b"\n", b"\r")):
    statement_text += line_ending
statement_payload = statement_text.encode("utf-8")
if bom:
    statement_payload = b"\xef\xbb\xbf" + statement_payload

try:
    atomic_write(CANDIDATES, candidate_payload)
    atomic_write(MENTIONS, mention_payload)
    atomic_write(STATEMENTS, statement_payload)
    post_summary, post_hits = surface_audit.audit("chp-2", 6)
    post_residual = {sig(hit) for hit in post_hits}
    if int(post_summary["uncovered_candidate_surface_spans"]) != len(expected_residual) or post_residual != expected_residual:
        raise RuntimeError(f"post-write prompt set mismatch: expected={sorted(expected_residual)} actual={sorted(post_residual)}")
    written_candidates = {row["candidate_id"] for row in read_csv(CANDIDATES)[1]}
    written_mentions = read_csv(MENTIONS)[1]
    if any(row["candidate_id"] not in written_candidates for row in written_mentions):
        raise RuntimeError("post-write mention has an unknown candidate FK")
    written_statements = [json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_index = {row["statement_id"]: row for row in written_statements}
    if statement_index["st-chp2-seci-l71-80-collection-fragment"]["object_candidate_id"] != "cand-11474":
        raise RuntimeError("collection continuation endpoint did not persist")
    if statement_index["st-chp2-seci-l71-80-deposition-removal"]["object_candidate_id"] != "cand-11474":
        raise RuntimeError("Deposition collection endpoint did not persist")
    if statement_index[NEW_STATEMENT["statement_id"]]["qualifiers"].get("relation_candidate") is not True:
        raise RuntimeError("Casino Rospigliosi ownership relation candidate did not persist")
except Exception:
    for path, backup in backups.items():
        shutil.copy2(backup, path)
    restored = all(sha256(path) == sha256(backup) for path, backup in backups.items())
    if not restored:
        raise RuntimeError("post-write validation failed and a table did not restore exactly")
    raise SystemExit("post-write validation failed; all three tables restored from recovery copies")

print(f"post_write_prompts={post_summary['uncovered_candidate_surface_spans']}")
print(f"written_mentions={len(new_mention_rows)}")
for path in paths:
    print(f"sha256_after[{path.name}]={sha256(path)}")
print("mode=applied; postconditions passed")
