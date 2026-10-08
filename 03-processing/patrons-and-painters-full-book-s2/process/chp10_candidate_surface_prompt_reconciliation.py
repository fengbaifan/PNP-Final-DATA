#!/usr/bin/env python3
"""Adjudicate Chapter 10 candidate-surface prompts against their source context.

The scanner is a locator only. This controlled writer verifies the complete
prompt partition, source spans, candidate keys, mention overlap, statement
targets, and locked inputs before it writes S2 decisions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
RESULT = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "results" / "chp-10.md"
SCRIPT_REL = "03-processing/patrons-and-painters-full-book-s2/process/chp10_candidate_surface_prompt_reconciliation.py"

sys.path.insert(0, str(ROOT / "scripts"))
import audit_s2_candidate_surfaces as surface_audit

EXPECTED_HASHES = {
    "04-knowledge/tables/entity-candidates.csv": "ad016f18b25aa2e9d0ce75be7399ac5a62b3ccd51b882100c9b60bb14cad1ffd",
    "04-knowledge/tables/mentions.csv": "1569933c8d788796fb56d3fbe690753dae3d9eeadbe7695fff7f96550ab728a6",
    "04-knowledge/tables/book-statements.jsonl": "9a01c3ec987dd20a19773f711bfde74ed5d52d679ce83bc5d004e4124dc15280",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "04-knowledge/tables/s2-coverage.csv": "84f8497a7ce0100f4785acd8bf8ed88bb4c69fe5254cd89d172577b0400eb6c1",
    "scripts/audit_s2_candidate_surfaces.py": "130b53da86d940daad454079960415ac5e7043e0b71239370b66226158cd1ee2",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "01-domain/stage-artifact-schema.md": "929b8a55f92103de962e8bd509d02d883683b0eea3a9ffe307e5de8229a86abe",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/10_CHP-10_intro_notes_p289_visual-transcription.md": "8cf5ec82dbf1d8040a860f7e386ec5b45d83059da643d5d12c0d0ef3d415a3d2",
    "02-sources/02-Markdown/10_CHP-10_intro_p302_note4_visual-transcription.md": "459a405191b15071dadf62a6f984f543a81226599f71ba5cd91cd68239c44da0",
    "02-sources/02-Markdown/10_CHP-10_intro_plates_visual-transcription.md": "163e94e2ebaad7cdd6a5bc2e57842103749ddb37f410af0fabfad3a4ea5e2e65",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
}


def accepted(index: int, candidate_id: str, statement_id: str, note: str, mention_surface: str | None = None) -> dict[str, object]:
    return {
        "prompt_index": index,
        "candidate_id": candidate_id,
        "statement_id": statement_id,
        "note": note,
        "mention_surface": mention_surface,
    }


ACCEPTED = [
    accepted(4, "cand-1325", "st-chp10-p283-pollnitz-praise", "The quoted French honorific Prince magnifique refers back to Johann Wilhelm, whose death and achievements frame Pöllnitz's praise; it is not Machiavelli's book The Prince, the false index hit."),
    accepted(6, "cand-4288", "st-chp10-p283-five-room-gallery", "Old masters names the art-historical category contrasted with the gallery's room-by-room holdings."),
    accepted(7, "cand-3401", "st-chp10-p283-pellegrini-gallery-influence-and-style", "Venice is the city in the Pellegrini gallery discussion; use the body-local place candidate and leave cross-source identity alignment to S3."),
    accepted(8, "cand-11494", "st-chp10-p284-crozat-mansion-collection", "The paintings collection in Crozat's Rue Richelieu mansion is a source-described collection with no itemized inventory; retain its type and boundary as unresolved."),
    accepted(10, "cand-11494", "st-chp10-p284-crozat-collection-made-available", "His collection refers to the same Crozat collection on p.284; the statement records reported access to artists without inventing named borrowers."),
    accepted(11, "cand-4131", "st-chp10-p284-peak-venetian-influence-france", "Italian art is the broad art-historical category in Haskell's assessment of the last serious impact in France."),
    accepted(12, "cand-8970", "st-chp10-p285-carriera-painted-sitters", "The phrase identifies the informal Paris portrait group Haskell attributes to Carriera and names by sitter; no title, exact date, or location is inferred."),
    accepted(20, "cand-0528", "st-chp10-p292-canaletto-market", "Canaletto is the painter in the p.292 account of English-client demand and the Grand Tour market; use the index candidate scoped to his English work."),
    accepted(22, "cand-4131", "st-chp10-p292-french-collectors", "Contemporary Italian art is the broad art-historical category in Haskell's account of French collecting."),
    accepted(28, "cand-2719", "st-chp10-p276-manchester-carlevarijs-entry", "Venice is the city in Lord Manchester's return and official-visit account."),
    accepted(30, "cand-2719", "st-chp10-p296-tiepolo-scene-venice-quote", "Venice is the city Tiepolo names as the historical setting of the Kaisersaal scene."),
    accepted(31, "cand-2822", "st-chp10-p296-staircase-ceiling-commission", "The palace is the Würzburg Residenz at which Tiepolo received the staircase-ceiling commission, not the fresco itself."),
    accepted(32, "cand-2719", "st-chp10-p296-ancien-regime-vision", "Venice is the city invoked in Haskell's description of the ancien-régime vision."),
    accepted(36, "cand-3401", "st-chp10-p300-smith-patron-and-painters", "Venice is the city where Smith was known as an arts patron and was in close contact with painters."),
    accepted(38, "cand-3401", "st-chp10-p300-palace-meeting-place-and-publishing", "Venice is the setting for Smith's palace as a meeting place and for his publishing activity."),
    accepted(39, "cand-3401", "st-chp10-p300-lodoli-memmo-and-smith-meetings", "Venice is the city whose cultural life is discussed through Lodoli, Memmo, and Smith."),
    accepted(40, "cand-3401", "st-chp10-p300-lodoli-memmo-wynne-rivalry", "Venice is the setting for the Lodoli-Memmo rivalry and its social circle."),
    accepted(41, "cand-2719", "st-chp10-p300-note1-esposizione-register", "Venice identifies the Archivio di Stato in the p.300 note citation; use the place candidate, not a topical index subentry."),
    accepted(42, "cand-2719", "st-chp10-p301-goldoni-and-smith-will", "Venice is the city context for Goldoni's dedication and Smith's will."),
    accepted(43, "cand-2719", "st-chp10-p301-smith-official-visitors", "Venice is the city to which Smith's official visitors came."),
    accepted(44, "cand-3401", "st-chp10-p302-ricci-employment-venice-turin", "Venice is one of the locations in the comparison of Ricci's employment, distinguished from the Turin court."),
    accepted(45, "cand-3401", "st-chp10-p302-seven-ricci-pictures-and-cignani-cartoons", "Venice is the artistic context in which Cignani was admired; retain the source's comparison and wording."),
    accepted(46, "cand-9200", "st-chp10-p303-marco-collection", "The nearly 150 drawings are the bounded Marco Ricci group already described in Smith's collection; retain the source's approximate count."),
    accepted(51, "cand-0514", "st-chp10-p305-canaletto-gap-and-english-commissions", "Canaletto is the painter in the account of the gap in Smith commissions and subsequent English work."),
    accepted(52, "cand-0514", "st-chp10-p307-claimed-vermeer-influence", "Canaletto is the painter whose development was said to be influenced by Vermeer; preserve that attribution as reported, not settled."),
    accepted(54, "cand-9210", "st-chp10-p307-roman-views-largest-for-smith", "His collection means Smith's type-unresolved Venetian collection; Haskell's claim about the six Roman views' impact remains explicitly inferential."),
    accepted(55, "cand-4131", "st-chp10-p307-smith-antique-rome-and-neoclassic", "Italian art is the broad historical field in Haskell's account of Rome and Roman values."),
    accepted(56, "cand-0514", "st-chp10-p307-next-commissioned-series-aim", "Canaletto is the painter of the next commissioned series; preserve Haskell's account of its architectural purpose."),
    accepted(57, "cand-0514", "st-chp10-p308-etchings-dedicated-to-smith", "Canaletto is the artist who dedicated the thirty-one-etching series to Smith."),
    accepted(59, "cand-0514", "st-chp10-p308-poetic-etching-vision", "Canaletto is the artist whose etching vision Haskell characterizes; do not turn the stylistic evaluation into an independent work."),
    accepted(60, "cand-0514", "st-chp10-p308-smith-continued-overdoor-series", "Canaletto is the artist whose departure preceded Smith's continuation of the overdoor series."),
    accepted(72, "cand-9497", "st-chp10-p300-note2-operatic-caricature-collection", "The large collection is the identified group of operatic caricatures attributed to Marco Ricci, A. M. Zanetti, and others."),
    accepted(74, "cand-3397", "st-chp10-p306-note3-gori-letter", "Florence is the location in the Biblioteca Marucelliana citation; the city's source-local place candidate is appropriate."),
    accepted(75, "cand-3397", "st-chp10-p306-note5-zanetti-letter-citation", "Florence is the location in the second Biblioteca Marucelliana letter citation."),
    accepted(76, "cand-3397", "st-chp10-p306-note6-smith-gori-letter", "Florence is the location of the Biblioteca Marucelliana cited for Smith's letter to Gori."),
    accepted(77, "cand-9210", "st-chp10-p310-note1-adam-visit-citations", "The collection of pictures refers to Smith's type-unresolved collection described at Mogliano; it is not a new set of individual works."),
    accepted(78, "cand-8919", "st-chp10-p280-burlington-grand-tour-and-mansion", "The palace is Burlington House, his Piccadilly mansion, as identified in the p.280 account."),
    accepted(82, "cand-9663", "st-chp10-p316-streit-displayed-family-portraits", "The exact group is the portraits of Streit’s father, mother, and sister; no artists or dates are added."),
    accepted(83, "cand-3570", "st-chp10-p319-conti-described-as-amateur-scientist", "Amateur is Haskell's characterization of Conti; this records the term without asserting an independently verified professional status."),
    accepted(85, "cand-2719", "st-chp10-p320-lodoli-in-touch-with-montesquieu", "Outside Venice is a geographic reference to the city from which Haskell distinguishes Lodoli's contacts with Montesquieu and Maffei."),
    accepted(87, "cand-9622", "st-chp10-p312-n02-corfu-and-collection-sources", "Schulenburg’s collection is the same type-unresolved picture collection that Haskell calls his gallery; note 2 discusses its contents and citations."),
    accepted(88, "cand-0525", "st-chp10-p312-n02-corfu-and-collection-sources", "Canaletto’s Corfu view is the specific work described in Schulenburg's inventory transcription; the statement preserves the source's uncertain reading."),
    accepted(89, "cand-2410", "st-chp10-p312-n02-corfu-and-collection-sources", "Schulenburg’s portraits is the indexed portrait material to which Haskell directs readers; keep it distinct from the specific portrait works by Guardi."),
    accepted(90, "cand-1421", "st-chp10-p322-lodoli-views-on-painting-exceptional", "Views on painting is the indexed conceptual subentry matching Haskell's statement that Lodoli's views were exceptional."),
    accepted(96, "cand-2719", "st-chp10-p325-jibe-and-pictures-anticipate-millet", "Venice is the contemporary artistic context in the comparison with Millet."),
    accepted(98, "cand-2719", "st-chp10-p326-n01-marciana-set", "Venice is the location of the Biblioteca Marciana holding the pamphlets."),
    accepted(99, "cand-2719", "st-chp10-p326-n03-dating-and-exhibition", "Venice is the location of the Biblioteca Correr named in the note continuation."),
    accepted(100, "cand-2719", "st-chp10-p328-zuccarelli-arrived-in-venice-from-tuscany", "Venice is the destination in the source's account of Zuccarelli's arrival from Tuscany; the source gives only an approximate date."),
    accepted(101, "cand-3575", "st-chp10-p328-english-landscape-market", "Landscape painting is the broad artistic category used to explain Zuccarelli's reception among English patrons."),
    accepted(102, "cand-2719", "st-chp10-p328-baretti-wrote-enthusiastically-of-zuccarelli", "Venice is the city used metonymically for the culture Baretti criticized; it is not a claim about every resident."),
    accepted(104, "cand-0005", "st-chp10-p330-memmo-vasari-academy-queries", "The Venetian Academy is the institution Memmo asks about; the statement retains his question rather than presuming a reform."),
    accepted(106, "cand-2719", "st-chp10-p311-n03-funeral-drawing-and-itinerary", "Venice is one of the cities in the footnote itinerary for Schulenburg."),
    accepted(107, "cand-2719", "st-chp10-p312-n01-marciana-shelfmark", "Venice is the location in the Biblioteca Marciana shelfmark citation."),
    accepted(108, "cand-9622", "st-chp10-p312-n04-inventories-and-wright", "Schulenburg’s collection is the same picture collection whose inventories are cited for 1724–1737."),
    accepted(110, "cand-2719", "st-chp10-p320-323-n02-correr-manuscript-sonnet-citation", "Venice is the location in the Biblioteca Correr manuscript citation."),
    accepted(111, "cand-2719", "st-chp10-p325-n1-magggiotto-source-citations", "Venice is the location in the Biblioteca Correr citation for Maggiotto's treatise."),
    accepted(112, "cand-2719", "st-chp10-p327-n01-grimaldo-balbi-citation", "Venice is the location in the Biblioteca Correr citation for the Grimaldo and Balbi materials."),
    accepted(113, "cand-9580", "st-chp10-p311-dynastic-portraits-at-palazzo-loredan", "The portraits form the specifically described dynastic group at Palazzo Loredan; do not infer individual makers or dates."),
    accepted(114, "cand-2719", "st-chp10-p313-pittoni-schulenburg-commission-and-reputation", "Venice is the city context for Pittoni's reputation as one of its leading history painters."),
    accepted(116, "cand-9622", "st-chp10-p314-ceruti-works-would-make-collection-unique", "The collection is Schulenburg's established type-unresolved picture collection; the claim that it was unique remains attributed to Haskell."),
]


NO_WRITE_REASONS = {
    1: "This is a duplicate OCR caption already captured in the plate-list and visual-transcription records; adding a second mention would duplicate the same caption.",
    2: "Fortune means the Duke of Chandos's accumulated wealth, not a named personified figure, work, or bounded financial record.",
    3: "Art patrons is a broad unnamed social category; no bounded group is identified in this passage.",
    5: "Dutch artists is an unbounded group descriptor inside the gallery inventory; the statement already preserves the room's artists and holdings without creating an extra group entity.",
    9: "Drawings is one medium in Crozat's described collection; the source identifies no distinct drawing set or inventory.",
    13: "Their portraits describes general demand from aristocrats and ambassadors, not a bounded group of works beyond Carriera's separately identified portraits.",
    14: "Fortune is generic wealth acquired through the South Sea Bubble, not a named or independently bounded object.",
    15: "Portraits is a general category of English commissions, not an identified set of works.",
    16: "The Van Dyck portraits are an unrealized engraving plan described generically; no completed or bounded work group is identified here.",
    17: "Modern Italian painting is descriptive context for the project's prospects, not an independently defined term in this passage; the Ch.20 Italian-painting candidate refers to a different catalog subject.",
    18: "Histories contrasts a generic subject genre with fables; it does not identify a specific history painting or archive.",
    19: "The Duke of Richmond's collection is a generic provenance phrase for prints; the source does not define a bounded collection object here.",
    21: "Prices refers to a general market response to steady demand, not a named price, transaction, or record.",
    23: "Prices is a generic comparative market term in the Swedish-patron discussion; no specific transaction is named.",
    24: "Portraits is an unbounded work category among Tessin's purchases; the source does not identify a particular set.",
    25: "Drawings is a generic medium in the Würzburg collection list; no bounded group is identified by this span.",
    26: "The theatre is the general sphere of stage scenery and festivals, not a named venue or institution.",
    27: "Pastel portraits describes Carriera's general practice; this span does not name a bounded work group.",
    29: "Churches is a general class of sites under Clemens August's patronage; no specific church or bounded group is named here.",
    33: "Churches is a generic class in the report of Ricci's work for the royal palace and other sites; no building is identified by this word.",
    34: "Venetian artists in the most distant outposts is a generic narrative group, not a named or bounded collective entity.",
    35: "Portraits is one generic subject category among Rotari's hundreds of pictures; the source identifies no separate portrait group.",
    37: "Theatre describes Smith's general leisure activity, not a named theatre or performance institution.",
    47: "Payments summarizes recurring remuneration over several years; no individual payment record or bounded payment series is identified.",
    48: "Drawings is a medium in the already described Smith holdings; this span does not identify a distinct drawing group.",
    49: "Portraits is a general category in the contrast of Smith's collecting preferences, not a bounded work entity.",
    50: "Churches is a generic architectural category in the description of Canaletto's views, not an identified group of buildings.",
    53: "Subject means the generic subject matter of Canaletto's pictures, not an independently identified entity.",
    58: "Drawings is a generic medium used to compare Canaletto's etchings with his painted work; no bounded drawing set is named.",
    61: "Attacks on Baroque architecture describes the content of Visentini's already registered updated book; the phrase is not a separate work or named concept.",
    62: "This Canaletto occurrence is part of the p.289 printed table already transcribed and represented in the dedicated visual-transcription source.",
    63: "This repeated Canaletto occurrence is the same p.289 table row already represented in the dedicated visual-transcription source; do not duplicate its mentions.",
    64: "Private collection is an anonymous parenthetical location label in the duplicated p.289 table, not an identifiable collection entity.",
    65: "Collection is a generic table-cell label in a duplicate OCR table; the curated transcription already preserves the row and its references.",
    66: "Private collection is an anonymous parenthetical label in the duplicated p.289 table, not a separately identifiable object.",
    67: "Collection is a generic table-cell label in the duplicated p.289 table; the visual transcription already records the row.",
    68: "This Canaletto occurrence is part of the p.289 printed table already represented in the dedicated visual-transcription source.",
    69: "Collection is an anonymous parenthetical table-cell label in the duplicate OCR, not a bounded collection candidate.",
    70: "The citation describes secondary literature about Clemens August's patronage; the phrase is a topical summary, not an additional named entity.",
    71: "Of Venetian artists is a generic descriptor in the same bibliography note, not a separate group or work.",
    73: "Drawings is a broad subject category in a secondary-literature citation about the Riccis, not a bounded set of drawings.",
    79: "Subject is a column heading in the curated p.289 table, not a subject entity.",
    80: "Venetian artists in Germany and England is a plate-section heading, not a named group; the individual captioned works are handled separately.",
    81: "Venetian artists in the middle of the eighteenth century is a plate-section heading, not an entity or bounded collective.",
    84: "Subject-matter means the generic topic of a grammatical exercise, not a separate entity.",
    86: "The index subentry points to Schulenburg's interest, and the S2 statement already captures it; contemporary Venetian sculpture is a descriptive field here, not a distinct named concept.",
    91: "Portraits is a generic plural already resolved into the two artist-specific portrait statements and their separate work candidates; it is not an additional group object.",
    92: "Theatre is the general art form being reformed by Goldoni, not a named venue, institution, or specific play.",
    93: "Subject means the topic of Longhi's poetry and paintings, not an independent object.",
    94: "Canvas is a generic artistic medium in Goldoni's quotation, not a particular painting or a separately discussed support concept.",
    95: "Poetry is a generic literary category in the accusation against Goldoni, not an identified poem.",
    97: "Subject means the subject matter of Maggiotto's treatise, not a separate entity.",
    103: "Canvas is a generic support in Baretti's description of Zuccarelli's work, not an individually identified painting.",
    105: "Aristocracy is a broad social class contrasted with the State; no bounded institution or source-specific group is identified.",
    109: "The Duke of Mantua's collection is mentioned generically as provenance for items; the passage does not identify a bounded collection object distinct from those works.",
    115: "Canvas means an unspecified commissioned painting; no title, maker, or bounded work is identified by this singular category.",
    117: "Fortune is generic wealth gained through commerce, not the personified figure or the unrelated work candidate Fortune.",
}


NEW_CANDIDATES = [
    {
        "candidate_id": "cand-11494",
        "index_entry_id": "",
        "canonical_name": "Pierre Crozat's collection of paintings and drawings (inventory and boundary unresolved)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes a superb painting collection and many thousands of drawings in Crozat's Rue Richelieu mansion, and says Crozat made his collection available to artists. No inventory, complete contents, or boundary with other Crozat holdings is supplied. Keep type unresolved and distinguish the collection from the mansion, its address, and its meeting participants.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": "chp-10:10_CHP-10_intro:l167-176#L171",
    },
]

NEW_STATEMENT_IDS = {
    "st-chp10-p284-crozat-had-mansion-rue-richelieu",
    "st-chp10-p284-crozat-hospitality-to-artists",
    "st-chp10-p284-crozat-collection-made-available",
    "st-chp10-p328-zuccarelli-arrived-in-venice-from-tuscany",
}

CROZAT_MANSION_STATEMENT = "st-chp10-p284-crozat-mansion-collection"
CROZAT_MEETINGS_STATEMENT = "st-chp10-p284-crozat-weekly-meetings"
CROZAT_MANSION_OLD_PREDICATE = "crozat_mansion_on_rue_richelieu_housed_collection"
CROZAT_MEETING_OLD_PREDICATE = "crozat_hosted_weekly_gatherings_and_opened_collection_to_artists"
CROZAT_MANSION_OLD_QUOTE = "He was at once brought into touch with Pierre Crozat, then aged 51, whose fine mansion in the Rue Richelieu contained a superb collection of paintings and, above all, many thousands of drawings by all the greatest Italian and Flemish masters."
CROZAT_MEETINGS_OLD_QUOTE = "Crozat used to arrange weekly meetings of an exceptionally alert group of art-lovers, painters and writers, and he was generous in giving hospitality to artists and making his collection easily available to them."


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_hashes() -> dict[str, str]:
    actual = {relative: sha256_bytes((ROOT / relative).read_bytes()) for relative in EXPECTED_HASHES}
    mismatches = {
        key: {"expected": EXPECTED_HASHES[key], "actual": actual[key]}
        for key in EXPECTED_HASHES if actual[key] != EXPECTED_HASHES[key]
    }
    if mismatches:
        raise RuntimeError(f"Locked inputs changed; re-review before writing: {json.dumps(mismatches, ensure_ascii=False)}")
    return actual


def read_csv_rows(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    return raw, list(reader.fieldnames or []), list(reader)


def append_csv_rows(raw: bytes, columns: list[str], rows: list[dict[str, str]]) -> bytes:
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator=eol.decode("ascii"))
    writer.writerows(rows)
    separator = b"" if raw.endswith((b"\n", b"\r")) else eol
    return raw + separator + buffer.getvalue().encode("utf-8")


def read_jsonl(raw: bytes) -> tuple[list[str], list[dict[str, object]], str, bool]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    if len(records) != len(lines):
        raise ValueError("Unexpected blank JSONL line; refusing to rewrite the table.")
    return lines, records, eol, bom


def mention_id(row: dict[str, object]) -> str:
    key = "|".join(str(row[field]) for field in ("segment_id", "start_char", "end_char", "candidate_id"))
    return "m-s2-chp10-surface-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def add_candidate_ids(record: dict[str, object], candidate_ids: list[str]) -> None:
    qualifiers = record.setdefault("qualifiers", {})
    if not isinstance(qualifiers, dict):
        raise ValueError(f"Statement qualifiers are not an object: {record.get('statement_id')}")
    current = qualifiers.setdefault("mentioned_candidate_ids", [])
    if not isinstance(current, list):
        raise ValueError(f"mentioned_candidate_ids is not a list: {record.get('statement_id')}")
    for candidate_id in candidate_ids:
        if candidate_id not in current:
            current.append(candidate_id)


def new_statement(
    statement_id: str,
    segment_id: str,
    source_file: str,
    subject_id: str,
    object_id: str | None,
    predicate: str,
    quote: str,
    claim: str,
    qualification: str,
    line_start: int,
    line_end: int,
    page: int,
    physical_page: int,
    mentioned_candidate_ids: list[str],
    relation_candidate: bool,
) -> dict[str, object]:
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject_id,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "printed_page": page,
            "pdf_physical_page": physical_page,
            "claim": claim,
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned_candidate_ids,
            "relation_candidate": relation_candidate,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": source_file,
    }


def make_new_statements() -> dict[str, dict[str, object]]:
    intro_segment = "chp-10:10_CHP-10_intro:l167-176"
    intro_source = "02-sources/02-Markdown/10_CHP-10_intro.md"
    sec_segment = "chp-10:10_CHP-10_sec_ii:l241-246"
    sec_source = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
    crozat_context = "He was at once brought into touch with Pierre Crozat, then aged 51, whose fine mansion in the Rue Richelieu contained a superb collection of paintings and, above all, many thousands of drawings by all the greatest Italian and Flemish masters."
    return {
        "st-chp10-p284-crozat-had-mansion-rue-richelieu": new_statement(
            "st-chp10-p284-crozat-had-mansion-rue-richelieu", intro_segment, intro_source,
            "cand-0894", "cand-8846", "crozat_described_as_having_mansion_on_rue_richelieu",
            crozat_context,
            "Haskell identifies the Rue Richelieu mansion as Crozat's and says he was then aged 51.",
            "The wording establishes the source's association of Crozat with the house, not legal title or an independently verified address.",
            171, 171, 284, 13, ["cand-0894", "cand-8846", "cand-8961"], False,
        ),
        "st-chp10-p284-crozat-hospitality-to-artists": new_statement(
            "st-chp10-p284-crozat-hospitality-to-artists", intro_segment, intro_source,
            "cand-0894", None, "crozat_extended_hospitality_to_artists",
            "he was generous in giving hospitality to artists",
            "Haskell says Crozat gave hospitality to artists.",
            "The artists are unnamed; this assertion does not create a collective identity or a person-to-person relation.",
            171, 171, 284, 13, ["cand-0894"], False,
        ),
        "st-chp10-p284-crozat-collection-made-available": new_statement(
            "st-chp10-p284-crozat-collection-made-available", intro_segment, intro_source,
            "cand-0894", "cand-11494", "crozat_made_collection_available_to_artists",
            "making his collection easily available to them.",
            "Haskell says Crozat made his collection easily available to artists.",
            "His refers to Crozat and them to the artists he welcomed. The passage gives no itemized loan list or formal lending terms.",
            171, 171, 284, 13, ["cand-0894", "cand-11494"], False,
        ),
        "st-chp10-p328-zuccarelli-arrived-in-venice-from-tuscany": new_statement(
            "st-chp10-p328-zuccarelli-arrived-in-venice-from-tuscany", sec_segment, sec_source,
            "cand-2879", "cand-2719", "zuccarelli_arrived_in_venice_from_tuscany_a_few_years_before_1738",
            "a few years after his arrival in Venice from his native Tuscany",
            "Haskell says Zuccarelli had arrived in Venice from his native Tuscany a few years before Zanetti praised him in 1738.",
            "The source gives no exact arrival year. This records the reported movement as an S2 assertion, not a formal relation type or independently verified chronology.",
            242, 242, 328, 61, ["cand-2879", "cand-2719"], False,
        ),
    }


def build_plan() -> dict[str, object]:
    summary, prompts = surface_audit.audit("chp-10", 6)
    if summary["reviewed_segments_scanned"] != 73 or summary["uncovered_candidate_surface_spans"] != 117:
        raise ValueError(f"Unexpected scanner scope: {summary}")
    accepted_indices = {int(row["prompt_index"]) for row in ACCEPTED}
    no_write_indices = set(NO_WRITE_REASONS)
    if len(accepted_indices) != len(ACCEPTED) or accepted_indices & no_write_indices:
        raise ValueError("Prompt decisions contain duplicate indices or overlap.")
    if accepted_indices | no_write_indices != set(range(1, 118)):
        raise ValueError(f"Prompt decisions do not partition 1..117: missing={sorted(set(range(1,118))-(accepted_indices|no_write_indices))}, extra={sorted((accepted_indices|no_write_indices)-set(range(1,118)))}")
    if len(ACCEPTED) != 60 or len(NO_WRITE_REASONS) != 57:
        raise ValueError(f"Malformed prompt partition: accepted={len(ACCEPTED)}, no_write={len(NO_WRITE_REASONS)}")
    prompts_by_index = {index: row for index, row in enumerate(prompts, 1)}

    segment_rows = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    segment_by_id = {str(row["segment_id"]): row for row in segment_rows}
    segment_text: dict[str, str] = {}
    for segment in segment_rows:
        if segment.get("chapter") != "chp-10":
            continue
        lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8-sig").splitlines()
        segment_text[str(segment["segment_id"])] = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])

    candidate_raw, candidate_columns, existing_candidates = read_csv_rows(CANDIDATES)
    mention_raw, mention_columns, existing_mentions = read_csv_rows(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    statement_lines, statement_rows, statement_eol, statement_bom = read_jsonl(statement_raw)
    candidate_ids = {row["candidate_id"] for row in existing_candidates}
    numeric_ids = [int(value.split("-", 1)[1]) for value in candidate_ids if value.startswith("cand-") and value.split("-", 1)[1].isdigit()]
    if max(numeric_ids, default=0) != 11493:
        raise ValueError(f"Candidate sequence changed; expected cand-11493, got {max(numeric_ids, default=0)}")
    if [row["candidate_id"] for row in NEW_CANDIDATES] != ["cand-11494"] or "cand-11494" in candidate_ids:
        raise ValueError("Unexpected or already allocated candidate ID.")

    mention_ids = {row["mention_id"] for row in existing_mentions}
    occupied: dict[str, list[tuple[int, int]]] = {}
    for row in existing_mentions:
        occupied.setdefault(row["segment_id"], []).append((int(row["start_char"]), int(row["end_char"])))

    planned_mentions: list[dict[str, str]] = []
    for item in ACCEPTED:
        prompt = prompts_by_index[int(item["prompt_index"])]
        segment_id = str(prompt["segment_id"])
        text = segment_text[segment_id]
        requested_surface = item["mention_surface"]
        surface = str(requested_surface or prompt["surface_form"])
        prompt_start, prompt_end = int(prompt["start_char"]), int(prompt["end_char"])
        if requested_surface:
            positions = [pos for pos in range(len(text)) if text.startswith(surface, pos)]
            covering = [pos for pos in positions if pos < prompt_end and pos + len(surface) > prompt_start]
            if not covering:
                raise ValueError(f"Custom mention does not cover prompt span: {item}; prompt={prompt}")
            start = min(covering, key=lambda pos: abs(pos - prompt_start))
        else:
            start = prompt_start
        end = start + len(surface)
        if start < 0 or text[start:end] != surface or start >= prompt_end or end <= prompt_start:
            raise ValueError(f"Accepted mention does not match source text: {item}; got={text[max(0,start):max(0,end)]!r}")
        row = {
            "segment_id": segment_id,
            "candidate_id": str(item["candidate_id"]),
            "surface_form": surface,
            "start_char": str(start),
            "end_char": str(end),
            "note": str(item["note"]),
        }
        row["mention_id"] = mention_id({**row, "start_char": start, "end_char": end})
        planned_mentions.append(row)

    new_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    all_candidate_ids = candidate_ids | new_candidate_ids
    planned_ids: set[str] = set()
    for row in planned_mentions:
        if row["mention_id"] in mention_ids or row["mention_id"] in planned_ids:
            raise ValueError(f"Duplicate mention ID: {row['mention_id']}")
        planned_ids.add(row["mention_id"])
        if row["candidate_id"] not in all_candidate_ids:
            raise ValueError(f"Mention refers to a missing candidate: {row}")
        a, b = int(row["start_char"]), int(row["end_char"])
        if any(a < old_end and b > old_start for old_start, old_end in occupied.get(row["segment_id"], [])):
            raise ValueError(f"Mention overlaps an existing mention: {row}")
        for other in planned_mentions:
            if other is row or other["segment_id"] != row["segment_id"]:
                continue
            if a < int(other["end_char"]) and b > int(other["start_char"]):
                raise ValueError(f"Planned mentions overlap: {row} / {other}")

    statement_map = {str(row["statement_id"]): row for row in statement_rows}
    if len(statement_map) != len(statement_rows):
        raise ValueError("Statement IDs are not unique.")
    required_targets = {str(row["statement_id"]) for row in ACCEPTED if str(row["statement_id"]) not in NEW_STATEMENT_IDS} | {CROZAT_MANSION_STATEMENT, CROZAT_MEETINGS_STATEMENT}
    if not required_targets <= statement_map.keys():
        raise ValueError(f"Missing statement update targets: {sorted(required_targets-statement_map.keys())}")
    if NEW_STATEMENT_IDS & statement_map.keys():
        raise ValueError(f"New statement ID already exists: {sorted(NEW_STATEMENT_IDS & statement_map.keys())}")

    old_mansion = statement_map[CROZAT_MANSION_STATEMENT]
    if old_mansion.get("predicate") != CROZAT_MANSION_OLD_PREDICATE or old_mansion.get("subject_candidate_id") != "cand-0894" or old_mansion.get("object_candidate_id") != "cand-8846" or old_mansion.get("original_quote") != CROZAT_MANSION_OLD_QUOTE:
        raise ValueError("The Crozat mansion/collection statement changed; re-review before splitting it.")
    old_meetings = statement_map[CROZAT_MEETINGS_STATEMENT]
    if old_meetings.get("predicate") != CROZAT_MEETING_OLD_PREDICATE or old_meetings.get("subject_candidate_id") != "cand-0894" or old_meetings.get("original_quote") != CROZAT_MEETINGS_OLD_QUOTE:
        raise ValueError("The Crozat meetings statement changed; re-review before splitting it.")

    updates: dict[str, dict[str, object]] = {}
    new_statements = make_new_statements()
    for statement_id, candidate_id in ((str(item["statement_id"]), str(item["candidate_id"])) for item in ACCEPTED):
        record = statement_map.get(statement_id, new_statements.get(statement_id))
        if record is None:
            raise ValueError(f"Missing statement target: {statement_id}")
        add_candidate_ids(record, [candidate_id])
        if statement_id in statement_map:
            updates[statement_id] = record

    mansion = json.loads(json.dumps(old_mansion, ensure_ascii=False))
    mansion["subject_candidate_id"] = "cand-8846"
    mansion["object_candidate_id"] = "cand-11494"
    mansion["predicate"] = "crozat_mansion_contained_paintings_and_drawings_collection"
    mansion["qualifiers"]["claim"] = "Haskell says Crozat's fine Rue Richelieu mansion contained a superb painting collection and many thousands of drawings by Italian and Flemish masters."
    mansion["qualifiers"]["qualification"] = "The collection has no itemized inventory or settled boundary in this passage. The opening of the quote identifies Crozat and the house; note 3 remains a short-form locator whose cited material was not independently consulted."
    mansion["qualifiers"]["mentioned_candidate_ids"] = ["cand-0894", "cand-8846", "cand-8961", "cand-11494"]
    mansion["qualifiers"]["relation_candidate"] = True
    updates[CROZAT_MANSION_STATEMENT] = mansion

    meetings = json.loads(json.dumps(old_meetings, ensure_ascii=False))
    meetings["object_candidate_id"] = None
    meetings["predicate"] = "crozat_arranged_weekly_meetings_of_art_lovers_painters_and_writers"
    meetings["original_quote"] = "Crozat used to arrange weekly meetings of an exceptionally alert group of art-lovers, painters and writers"
    meetings["qualifiers"]["claim"] = "Haskell says Crozat arranged weekly meetings of an unusually alert group of art-lovers, painters, and writers."
    meetings["qualifiers"]["qualification"] = "Participants are described collectively but not individually named. The following hospitality and collection-access claims are separated into distinct statements."
    meetings["qualifiers"]["mentioned_candidate_ids"] = ["cand-0894"]
    meetings["qualifiers"]["relation_candidate"] = False
    updates[CROZAT_MEETINGS_STATEMENT] = meetings

    extras = make_new_statements()
    add_candidate_ids(extras["st-chp10-p284-crozat-had-mansion-rue-richelieu"], ["cand-0894", "cand-8846", "cand-8961"])
    add_candidate_ids(extras["st-chp10-p284-crozat-hospitality-to-artists"], ["cand-0894"])
    add_candidate_ids(extras["st-chp10-p284-crozat-collection-made-available"], ["cand-0894", "cand-11494"])
    add_candidate_ids(extras["st-chp10-p328-zuccarelli-arrived-in-venice-from-tuscany"], ["cand-2879", "cand-2719"])
    extras_after = {
        CROZAT_MANSION_STATEMENT: [extras["st-chp10-p284-crozat-had-mansion-rue-richelieu"]],
        CROZAT_MEETINGS_STATEMENT: [extras["st-chp10-p284-crozat-hospitality-to-artists"], extras["st-chp10-p284-crozat-collection-made-available"]],
        "st-chp10-p328-english-landscape-market": [extras["st-chp10-p328-zuccarelli-arrived-in-venice-from-tuscany"]],
    }

    candidate_output = append_csv_rows(candidate_raw, candidate_columns, NEW_CANDIDATES)
    mention_output = append_csv_rows(mention_raw, mention_columns, planned_mentions)
    output_lines: list[str] = []
    inserted: set[str] = set()
    for line in statement_lines:
        row = json.loads(line)
        statement_id = str(row["statement_id"])
        if statement_id in updates:
            row = updates[statement_id]
            output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
        else:
            output_lines.append(line)
        for extra in extras_after.get(statement_id, []):
            output_lines.append(json.dumps(extra, ensure_ascii=False, separators=(",", ":")))
            inserted.add(str(extra["statement_id"]))
    if inserted != NEW_STATEMENT_IDS:
        raise ValueError(f"Could not place every new statement: inserted={sorted(inserted)}")
    statement_text = statement_eol.join(output_lines) + statement_eol
    if statement_bom:
        statement_text = "\ufeff" + statement_text
    statement_output = statement_text.encode("utf-8")

    plan_content = {
        "accepted": ACCEPTED,
        "no_write": NO_WRITE_REASONS,
        "new_candidates": NEW_CANDIDATES,
        "new_statements": extras,
        "statement_updates": {key: value for key, value in updates.items()},
    }
    plan_sha = hashlib.sha256(json.dumps(plan_content, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "scanner_summary": summary,
        "prompts": prompts,
        "segment_by_id": segment_by_id,
        "segment_text": segment_text,
        "candidates": {row["candidate_id"]: row for row in existing_candidates} | {row["candidate_id"]: row for row in NEW_CANDIDATES},
        "accepted": ACCEPTED,
        "no_write": NO_WRITE_REASONS,
        "planned_mentions": planned_mentions,
        "new_candidates": NEW_CANDIDATES,
        "new_statements": extras,
        "statement_updates": updates,
        "plan_sha256": plan_sha,
        "outputs": {CANDIDATES: candidate_output, MENTIONS: mention_output, STATEMENTS: statement_output},
        "before_hashes": {path.name: sha256_bytes(path.read_bytes()) for path in (CANDIDATES, MENTIONS, STATEMENTS)},
    }


def render_report(plan: dict[str, object], after_hashes: dict[str, str], recovery: Path, audit_summary: dict[str, object]) -> bytes:
    prompts = plan["prompts"]
    accepted_map = {int(row["prompt_index"]): row for row in plan["accepted"]}
    no_write = plan["no_write"]
    segment_by_id = plan["segment_by_id"]
    segment_text = plan["segment_text"]
    candidates = plan["candidates"]
    lines = [
        "# 第十章候选表面提示裁决（2026-10-08）",
        "",
        "候选表面定位器在73个reviewed/complete段中给出117条提示。定位器只覆盖当前候选名称，不代表实体召回率或语义验收。逐条回到对应来源和现有statement裁决后，60条映射、57条不写。新增1个类型待定的Crozat收藏候选、60条mentions；为既有statement补齐候选提及，并拆分Crozat的住宅、收藏内容、每周聚会、艺术家接待与收藏开放陈列等断言。补记Zuccarelli从Tuscany抵达Venice的来源断言；不新增正式S6关系。",
        "",
        "字符跨度为拼接段文本中的零起点、右开区间；行号用于回到规范S0来源。对专名、人物、作品、地点及概念均按当前语境选择候选；重复OCR及无界泛称不另造对象。",
        "",
        "| 序号 | 来源定位 | 字符跨度 | 提示原文 | 裁决/候选 | 判断依据 |",
        "|---:|---|---:|---|---|---|",
    ]
    for index, prompt in enumerate(prompts, 1):
        segment_id = str(prompt["segment_id"])
        segment = segment_by_id[segment_id]
        text = segment_text[segment_id]
        start, end = int(prompt["start_char"]), int(prompt["end_char"])
        source_line = int(segment["line_start"]) + text[:start].count("\n")
        source_name = Path(str(segment["source_file"])).name
        decision = accepted_map.get(index)
        if decision:
            candidate_id = str(decision["candidate_id"])
            candidate_name = str(candidates[candidate_id]["canonical_name"])
            outcome = f"映射 {candidate_id} ({candidate_name})"
            reason = str(decision["note"])
        else:
            outcome = "不写入"
            reason = str(no_write[index])
        surface = str(prompt["surface_form"]).replace("|", "\\|").replace("\n", " ")
        reason = reason.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {index} | {source_name}#L{source_line} | {start}:{end} | {surface} | {outcome} | {reason} |")
    lines.extend([
        "",
        "## 写回与核验",
        "",
        f"- 候选数量：{len(plan['candidates']) - len(plan['new_candidates'])} → {len(plan['candidates'])}；新候选：cand-11494，类型待定。",
        f"- mentions新增：{len(plan['planned_mentions'])}；statement新增：{len(plan['new_statements'])}。Crozat原有复合statement已拆为可核对的命题；收藏仍不扩写为逐件清单。",
        f"- 写后候选表面提示：{audit_summary['uncovered_candidate_surface_spans']}条；与裁决后的no-write残余逐跨度一致。扫描结果仍不证明候选召回完整。",
        f"- 严格S2检查：{audit_summary.get('strict_audit', '见全书当前结果更新')}",
        f"- 决策计划SHA-256：{plan['plan_sha256']}；脚本SHA-256：{sha256_bytes((ROOT / SCRIPT_REL).read_bytes())}。",
        f"- 写前表SHA-256：candidates {plan['before_hashes']['entity-candidates.csv']}；mentions {plan['before_hashes']['mentions.csv']}；statements {plan['before_hashes']['book-statements.jsonl']}。",
        f"- 写后表SHA-256：candidates {after_hashes['entity-candidates.csv']}；mentions {after_hashes['mentions.csv']}；statements {after_hashes['book-statements.jsonl']}。",
        f"- 恢复副本：{recovery}。",
        "",
        "候选提示裁决不取代对S2语义陈述、跨章身份、脚注、遗漏来源及关系候选的全书交接审计。",
        "",
    ])
    return "\n".join(lines).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def apply_plan(plan: dict[str, object]) -> tuple[Path, dict[str, str], dict[str, object]]:
    recovery = Path(tempfile.gettempdir()) / f"pnp-s2-chp10-surface-prompts-{datetime.now():%Y%m%d-%H%M%S}"
    recovery.mkdir(parents=True, exist_ok=False)
    paths = list(plan["outputs"].keys())
    for path in paths:
        shutil.copy2(path, recovery / path.name)
    old_result = RESULT.read_bytes() if RESULT.exists() else None
    try:
        for path, data in plan["outputs"].items():
            atomic_write(path, data)
        expected_after = {
            (str(plan["prompts"][index - 1]["segment_id"]), int(plan["prompts"][index - 1]["start_char"]), int(plan["prompts"][index - 1]["end_char"]), str(plan["prompts"][index - 1]["surface_form"]))
            for index in plan["no_write"]
        }
        planned_spans = [(str(row["segment_id"]), int(row["start_char"]), int(row["end_char"])) for row in plan["planned_mentions"]]
        expected_after = {
            signature for signature in expected_after
            if not any(signature[0] == segment_id and signature[1] < end and signature[2] > start for segment_id, start, end in planned_spans)
        }
        after_summary, remaining = surface_audit.audit("chp-10", 6)
        actual_after = {
            (str(hit["segment_id"]), int(hit["start_char"]), int(hit["end_char"]), str(hit["surface_form"]))
            for hit in remaining
        }
        if actual_after != expected_after:
            raise RuntimeError(f"Post-write prompts differ from no-write residue: missing={sorted(expected_after-actual_after)}; extra={sorted(actual_after-expected_after)}; scanner={after_summary}")
        after_hashes = {path.name: sha256_bytes(data) for path, data in plan["outputs"].items()}
        audit_run = subprocess.run(
            [sys.executable, "-X", "utf8", "scripts/audit_tables.py", "--strict-stage"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        strict_audit = json.loads(audit_run.stdout)
        after_summary["strict_audit"] = (
            f"errors={strict_audit.get('errors')}; s2_missing={strict_audit.get('s2_missing')}; "
            f"candidates={strict_audit.get('candidates')}; mentions={strict_audit.get('mentions')}; "
            f"statements={strict_audit.get('book_statements')}"
        )
        report = render_report(plan, after_hashes, recovery, after_summary)
        atomic_write(RESULT, report)
    except Exception:
        for path in paths:
            shutil.copy2(recovery / path.name, path)
        if old_result is None:
            RESULT.unlink(missing_ok=True)
        else:
            atomic_write(RESULT, old_result)
        raise
    return recovery, after_hashes, after_summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the locked, preflighted decisions")
    args = parser.parse_args()
    verify_hashes()
    plan = build_plan()
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "scanner": plan["scanner_summary"],
        "accepted_mentions": len(plan["planned_mentions"]),
        "no_write_prompts": len(plan["no_write"]),
        "new_candidates": len(plan["new_candidates"]),
        "new_statements": len(plan["new_statements"]),
        "updated_statements": len(plan["statement_updates"]),
        "plan_sha256": plan["plan_sha256"],
        "before_hashes": plan["before_hashes"],
    }, ensure_ascii=False))
    if not args.apply:
        return 0
    recovery, after_hashes, after_summary = apply_plan(plan)
    print(json.dumps({
        "post_write_scanner": after_summary,
        "remaining_prompts_match_no_write_residue": True,
        "after_hashes": after_hashes,
        "recovery_directory": str(recovery),
        "chapter_result": str(RESULT),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
