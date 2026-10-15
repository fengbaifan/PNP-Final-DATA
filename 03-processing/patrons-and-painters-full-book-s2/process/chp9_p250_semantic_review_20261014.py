"""Controlled semantic repair for printed p.250 in full-book S2.

Default invocation is a read-only preflight. Source OCR is never modified.
The script restores the pinned p.250 mention baseline, reviews statement
endpoints/classifications, atomizes compound claims, and adds the p.250 note's
missing inventory mention in the consolidated-notes segment.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l90-104"
NOTES_SEGMENT_ID = "chp-9:09_CHP-9_intro:l323-445"
BASELINE_REV = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_SEGMENT_HASH = "166b580e0d98274a4cef63638b625bce87aa307685138b9f311f4eba9d1f992d"
EXPECTED_NOTES_HASH = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p250-semantic-review-20261014"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
segment = segment_by_id.get(SEGMENT_ID)
notes_segment = segment_by_id.get(NOTES_SEGMENT_ID)
if not segment or not notes_segment:
    raise SystemExit("p.250 or consolidated-notes segment metadata is missing")
if segment["sha256"] != EXPECTED_SEGMENT_HASH or notes_segment["sha256"] != EXPECTED_NOTES_HASH:
    raise SystemExit("p.250 or notes segment hash changed; inspect before repair")
if segment["asset_sha256"] != EXPECTED_ASSET_HASH or notes_segment["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash in segment metadata changed")
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()


def source_segment_text(meta):
    selected = source_lines[meta["line_start"] - 1:meta["line_end"]]
    text = "\n".join(selected)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash mismatch: {meta['segment_id']}")
    line_offsets = {}
    offset = 0
    for line_number, line in zip(range(meta["line_start"], meta["line_end"] + 1), selected):
        line_offsets[line_number] = offset
        offset += len(line) + 1
    return text, line_offsets


segment_text, line_offsets = source_segment_text(segment)
notes_text, notes_line_offsets = source_segment_text(notes_segment)
candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
statement_rows = read_jsonl(statement_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}
statement_by_id = {row["statement_id"]: row for row in statement_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
coverage = coverage_by_id.get(SEGMENT_ID)
notes_coverage = coverage_by_id.get(NOTES_SEGMENT_ID)
if not coverage or (coverage["disposition"], coverage["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit(f"unexpected p.250 coverage: {coverage}")
if not notes_coverage or (notes_coverage["disposition"], notes_coverage["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit(f"unexpected notes coverage: {notes_coverage}")

expected_existing_ids = {
    "st-chp9-p250-carlevarijs-landscapes", "st-chp9-p250-cochin-inventory-references",
    "st-chp9-p250-frescoes-family-virtues", "st-chp9-p250-labia-employed-lazzarini",
    "st-chp9-p250-labia-giordano-collection", "st-chp9-p250-labia-inventory-title-list",
    "st-chp9-p250-labia-palace-and-wealth", "st-chp9-p250-lazzarini-ceres-bacchus",
    "st-chp9-p250-new-families-patronage", "st-chp9-p250-tiepolo-early-works",
    "st-chp9-p250-widmann-country-house-frescoes", "st-chp9-p250-widmann-palace-and-scipio-canvases",
    "st-chp9-p250-zenobio-fresco-cycle", "st-chp9-p250-zenobio-palace-transformation",
    "st-chp9-p250-zenobio-wealth-and-palace",
}
target_rows = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if {row["statement_id"] for row in target_rows} != expected_existing_ids:
    raise SystemExit("p.250 statement inventory changed; inspect before repair")
unset_ids = {
    "st-chp9-p250-cochin-inventory-references", "st-chp9-p250-frescoes-family-virtues",
    "st-chp9-p250-labia-inventory-title-list", "st-chp9-p250-new-families-patronage",
    "st-chp9-p250-zenobio-palace-transformation",
}
if any(statement_by_id[sid].get("qualifiers", {}).get("relation_candidate") is not None for sid in unset_ids):
    raise SystemExit("p.250 classification pre-state changed; inspect before repair")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("p.250 already has current mentions; inspect instead of duplicating")

baseline_text = subprocess.check_output(
    ["git", "show", f"{BASELINE_REV}:04-knowledge/tables/mentions.csv"],
    cwd=ROOT, text=True, encoding="utf-8",
)
baseline_mentions = list(csv.DictReader(io.StringIO(baseline_text)))
restored_mentions = [row.copy() for row in baseline_mentions if row["segment_id"] == SEGMENT_ID]
if len(restored_mentions) != 65:
    raise SystemExit(f"pinned baseline has {len(restored_mentions)} p.250 mentions, expected 65")
for row in restored_mentions:
    start, end = int(row["start_char"]), int(row["end_char"])
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"restored mention has missing candidate: {row['mention_id']}")
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"restored mention span differs from S0: {row['mention_id']}")
    if row["mention_id"] in mention_ids:
        raise SystemExit(f"mention ID already exists: {row['mention_id']}")

# The archive exists already; add the source-exact mention in p.250's consolidated note 8.
archive_candidate_id = "cand-8548"
note_surface = "An inventory of some of the Labia pictures in 1749"
note_line = source_lines[348 - 1]
note_column = note_line.index(note_surface)
note_start = notes_line_offsets[348] + note_column
note_end = note_start + len(note_surface)
archive_note_mention = {
    "mention_id": "m-chp9-notes-p250-labia-inventory-1749",
    "segment_id": NOTES_SEGMENT_ID,
    "candidate_id": archive_candidate_id,
    "surface_form": note_surface,
    "start_char": str(note_start),
    "end_char": str(note_end),
    "note": "Printed p.250 note 8 identifies the cited 1749 notarial inventory; the archival record itself was not independently consulted.",
}
if archive_candidate_id not in candidate_ids or notes_text[note_start:note_end] != note_surface:
    raise SystemExit("p.250 note 8 inventory mention does not match source/candidate")
if archive_note_mention["mention_id"] in mention_ids:
    raise SystemExit("p.250 inventory note mention ID already exists")
for row in mention_rows:
    if row["segment_id"] == NOTES_SEGMENT_ID and (row["start_char"], row["end_char"]) == (str(note_start), str(note_end)):
        raise SystemExit("p.250 inventory note span already exists in current mentions")


def quote_lines(first: int, last: int | None = None):
    last = first if last is None else last
    return "\n".join(source_lines[first - 1:last])


def update(statement_id: str, *, subject: str | None, object_: str | None, predicate: str,
           claim: str, qualification: str, mentioned: list[str], relation: bool,
           first: int, last: int | None = None, speaker: str = "Haskell",
           layer: str | None = None, quote: str | None = None, extras: dict | None = None):
    row = statement_by_id[statement_id]
    row["subject_candidate_id"] = subject
    row["object_candidate_id"] = object_
    row["predicate"] = predicate
    qualifiers = row.setdefault("qualifiers", {})
    qualifiers.update({
        "source_line_start": first,
        "source_line_end": first if last is None else last,
        "printed_page": 250,
        "pdf_physical_page": 12,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer or ("footnote" if first >= 97 else "body"),
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "semantic_review": "2026-10-14 source-order review; page image, span, endpoint, and attribution checked",
    })
    if extras:
        qualifiers.update(extras)
    row["original_quote"] = quote_lines(first, last) if quote is None else quote


def new_statement(statement_id: str, *, first: int, subject: str | None, object_: str | None,
                  predicate: str, claim: str, qualification: str, mentioned: list[str],
                  relation: bool, speaker: str = "Haskell", layer: str | None = None,
                  last: int | None = None, extras: dict | None = None):
    if statement_id in statement_ids:
        raise SystemExit(f"new statement ID already exists: {statement_id}")
    for candidate_id in [subject, object_, *mentioned]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"new statement has missing candidate: {statement_id} {candidate_id}")
    qualifiers = {
        "source_line_start": first,
        "source_line_end": first if last is None else last,
        "printed_page": 250,
        "pdf_physical_page": 12,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer or ("footnote" if first >= 97 else "body"),
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation,
        "semantic_review": "2026-10-14 source-order review; atomic statement",
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote_lines(first, last),
        "origin": "book",
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
    }


# Existing claims are revised to isolate one claim and use the appropriate endpoint.
update(
    "st-chp9-p250-carlevarijs-landscapes", subject="cand-0554", object_="cand-8191",
    predicate="carlevarijs_painted_romantic_landscapes_for_zenobio_palace",
    claim="Luca Carlevarijs painted a series of romantic landscapes for the Zenobio palace.",
    qualification="The source names a series but gives no number or individual titles. Its placement along the palace corridor is recorded separately.",
    mentioned=["cand-0554", "cand-2871", "cand-8191"], relation=True, first=93,
)
update(
    "st-chp9-p250-cochin-inventory-references", subject="cand-0793", object_="cand-1348",
    predicate="cochin_referred_to_labia_inventory_pictures_and_other_images",
    claim="Haskell says Cochin referred to several of the Labia pictures by inventory number and also mentioned a Sonates, a St Peter receiving the Keys, and a shepherds-and-sheep picture.",
    qualification="The parenthetical identification of inventory nos. 1, 2, 4, 5, 6, 7, 11 and 12 as Job and his Wife and Isaac blessing Jacob is expressly 'almost certain'. No exact mapping or authorship is inferred for the additional references. Cochin's presence in Venice is stated separately.",
    mentioned=["cand-0793", "cand-2719", "cand-1348", "cand-8548", "cand-8212", "cand-8213", "cand-8214", "cand-8215", "cand-4231", "cand-8216"],
    relation=False, first=104, layer="footnote",
    extras={
        "footnote_marker": 8,
        "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 348, "source_line_end": 348}],
        "continued_from_segment_id": NOTES_SEGMENT_ID,
        "continued_from_source_line": 348,
        "citation_locator": "Cochin, vol. III, pp. 138-139",
        "ocr_corrections": [{"source_line": 104, "ocr": "138139-", "print": "138-139.", "basis": "CHP-9.pdf physical page 12"}],
    },
)
update(
    "st-chp9-p250-frescoes-family-virtues", subject="cand-8186", object_="cand-2870",
    predicate="frescoes_designed_to_celebrate_zenobio_virtues_and_fine_arts_protection",
    claim="The Zenobio frescoes were designed to celebrate the family's virtues and its protection of the fine arts.",
    qualification="This records Haskell's account of the decorative programme, not a specific formal dedication or a verified historical motive.",
    mentioned=["cand-8186", "cand-2870", "cand-2720"], relation=False, first=92,
)
update(
    "st-chp9-p250-labia-employed-lazzarini", subject="cand-1349", object_="cand-1368",
    predicate="labia_employed_lazzarini_throughout_1680s",
    claim="The Labia employed Gregorio Lazzarini throughout the 1680s.",
    qualification="The OCR 'i68os' is corrected to printed '1680s'; retain the decade-level time range.",
    mentioned=["cand-1349", "cand-1368"], relation=True, first=95,
    extras={"footnote_marker": 7, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 347, "source_line_end": 347}],
            "ocr_corrections": [{"source_line": 95, "ocr": "i68os", "print": "1680s", "basis": "CHP-9.pdf physical page 12"}]},
)
update(
    "st-chp9-p250-labia-giordano-collection", subject="cand-1349", object_="cand-1348",
    predicate="labia_owned_largest_venetian_collection_of_giordano_pictures",
    claim="Haskell describes the Labia as owning Venice's largest collection of pictures by Luca Giordano.",
    qualification="The superlative is Haskell's account. His suggestion that the pictures were presumably painted for the Labia during Giordano's 1682 visit remains qualified, not independently verified.",
    mentioned=["cand-1349", "cand-1348", "cand-1182", "cand-2719"], relation=True, first=95, last=96,
    extras={"footnote_marker": 8, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 348, "source_line_end": 348}],
            "continuation_to_source_line": 96,
            "ocr_corrections": [{"source_line": 95, "ocr": "i68os", "print": "1680s", "basis": "CHP-9.pdf physical page 12"}]},
)
update(
    "st-chp9-p250-labia-inventory-title-list", subject=archive_candidate_id, object_="cand-1182",
    predicate="1749_labia_inventory_lists_giordano_picture_titles",
    claim="The continuation of note 8 lists nine further titles in the 1749 Labia inventory of pictures by Giordano.",
    qualification="The consolidated note identifies the archival source and attributes the listed pictures to Giordano. The titles are retained as inventory entries, not identified surviving objects; inventory nos. 6, 7 and 12 are not titled in this continuation.",
    mentioned=[archive_candidate_id, "cand-1348", "cand-1182", "cand-8203", "cand-8204", "cand-8205", "cand-8206", "cand-8207", "cand-8208", "cand-8209", "cand-8210", "cand-8211"],
    relation=True, first=97, last=103, layer="footnote",
    extras={
        "footnote_marker": 8,
        "continued_from_segment_id": NOTES_SEGMENT_ID,
        "continued_from_source_line": 348,
        "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 348, "source_line_end": 348}],
        "ocr_corrections": [{"source_line": 100, "ocr": "trionso", "print": "trionfo", "basis": "CHP-9.pdf physical page 12"}],
    },
)
update(
    "st-chp9-p250-labia-palace-and-wealth", subject="cand-1349", object_="cand-8201",
    predicate="labia_family_began_building_gigantic_palace",
    claim="The Labia had set about building a gigantic palace.",
    qualification="The palace's completion in the early eighteenth century and the family's ostentatious display of wealth are recorded separately.",
    mentioned=["cand-1349", "cand-8202", "cand-8201"], relation=True, first=95,
    extras={"footnote_marker": 6, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 347, "source_line_end": 347}]},
)
update(
    "st-chp9-p250-lazzarini-ceres-bacchus", subject="cand-1368", object_="cand-8194",
    predicate="lazzarini_decorated_zenobio_ceiling_with_ceres_and_bacchus",
    claim="Gregorio Lazzarini decorated a ceiling at the Zenobio palace with Ceres and Bacchus.",
    qualification="The source does not give a date or further iconographic description.",
    mentioned=["cand-1368", "cand-2871", "cand-8194", "cand-8195", "cand-7814"], relation=True, first=93,
)
update(
    "st-chp9-p250-new-families-patronage", subject="cand-8134", object_="cand-2720",
    predicate="recently_ennobled_families_led_early_18c_venetian_artistic_patronage",
    claim="Closing p.249's sentence, Haskell says four or five families ennobled about fifty years earlier were at the forefront of Venice's artistic patronage at the beginning of the eighteenth century.",
    qualification="Preserve the approximate family count, approximate interval and temporal wording; no family names or specific patronage relationships are supplied.",
    mentioned=["cand-8134", "cand-2720", "cand-2719"], relation=False, first=91,
    extras={"continued_from_segment_id": "chp-9:09_CHP-9_intro:l77-88", "continued_from_source_line": 86,
            "cross_reference_segments": [{"segment_id": "chp-9:09_CHP-9_intro:l77-88", "source_line_start": 86, "source_line_end": 86}]},
)
update(
    "st-chp9-p250-tiepolo-early-works", subject="cand-2569", object_="cand-2870",
    predicate="tiepolo_produced_early_works_for_zenobio_family",
    claim="The young Giambattista Tiepolo produced some of his earliest works for the Zenobio family.",
    qualification="Preserve 'some of his earliest'; the source does not identify the individual works or give a date.",
    mentioned=["cand-2569", "cand-2870"], relation=True, first=93,
    extras={"footnote_marker": 3, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 345, "source_line_end": 345}]},
)
update(
    "st-chp9-p250-widmann-country-house-frescoes", subject="cand-0944", object_="cand-8200",
    predicate="dorigny_painted_diana_actaeon_frescoes_for_widmann_country_house",
    claim="Louis Dorigny painted the Widmann country house with frescoes of Diana and Actaeon.",
    qualification="Keep this fresco group distinct from the similarly titled Diana-and-Actaeon wall scene in Ricci's Pitti decoration. The house's location is recorded separately.",
    mentioned=["cand-0944", "cand-2812", "cand-2811", "cand-8199", "cand-8200", "cand-4136", "cand-7995"],
    relation=True, first=94,
    extras={"footnote_marker": 5, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 346, "source_line_end": 346}]},
)
update(
    "st-chp9-p250-widmann-palace-and-scipio-canvases", subject="cand-2812", object_="cand-8197",
    predicate="widmann_family_decorated_palace_with_lazzarini_canvases",
    claim="The Widmann lavishly decorated their palace with large canvases by Gregorio Lazzarini.",
    qualification="The source gives no number or individual titles for the canvases. The palace's approximate location and the canvases' subject are represented separately.",
    mentioned=["cand-2812", "cand-2813", "cand-8197", "cand-1368"], relation=True, first=94,
    extras={"footnote_marker": 4, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 346, "source_line_end": 346}]},
)
update(
    "st-chp9-p250-zenobio-fresco-cycle", subject="cand-0944", object_="cand-8186",
    predicate="dorigny_called_to_paint_zenobio_mythological_fresco_cycle",
    claim="About fifteen years earlier, the French artist Dorigny had been called in to paint a spectacular mythological fresco series at the Zenobio palace.",
    qualification="Keep 'some fifteen years earlier' approximate. The framework's style and the frescoes' stated programme are recorded separately.",
    mentioned=["cand-0944", "cand-2871", "cand-8186"], relation=True, first=92,
)
update(
    "st-chp9-p250-zenobio-palace-transformation", subject="cand-2871", object_=None,
    predicate="zenobio_palace_transformed_and_nearing_completion_by_1703",
    claim="The Zenobio palace at the Carmini was completely transformed and nearing completion by 1703.",
    qualification="The source gives a terminus/status by 1703, not an exact completion date.",
    mentioned=["cand-2871", "cand-8184"], relation=False, first=92,
)
update(
    "st-chp9-p250-zenobio-wealth-and-palace", subject="cand-2870", object_="cand-2871",
    predicate="zenobio_family_bought_morosini_palace_at_carmini",
    claim="The Zenobio family had bought the palace at the Carmini from the Morosini, one of the twelve oldest families known as the Apostles.",
    qualification="The passage's statement that the Zenobio were said to be the richest family is recorded separately. Do not equate the Morosini family group with an individual.",
    mentioned=["cand-2870", "cand-2871", "cand-8184", "cand-1706", "cand-8185"], relation=True, first=92,
    extras={"footnote_marker": 1, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 344, "source_line_end": 344}],
            "ocr_corrections": [{"source_line": 92, "ocr": "socalled", "print": "so-called", "basis": "CHP-9.pdf physical page 12"}]},
)

new_statements = [
    new_statement("st-chp9-p250-zenobio-wealth-reputation", first=92,
        subject="cand-2870", object_="cand-2719", predicate="reported_as_richest_family_in_venice",
        claim="The Zenobio were said to be the richest family in Venice.",
        qualification="Retain the reported/hearsay phrasing 'were said to be'; this is Haskell's account, not independently verified.",
        mentioned=["cand-2870", "cand-2719"], relation=False),
    new_statement("st-chp9-p250-zenobio-framework-description", first=92,
        subject="cand-8187", object_="cand-8188", predicate="fresco_cycle_held_within_bolognese_type_painted_framework",
        claim="The mythological frescoes were contained within a heavy, elaborate painted architectural framework of the Bolognese type, with cartouches and Carraccesque nudes.",
        qualification="This records Haskell's visual and stylistic description; the influence claim about the nudes is separate.",
        mentioned=["cand-8186", "cand-8187", "cand-8188", "cand-8189"], relation=False),
    new_statement("st-chp9-p250-zenobio-nudes-derived-from-farnese", first=92,
        subject="cand-8189", object_="cand-0999", predicate="carraccesque_nudes_derived_from_palazzo_farnese",
        claim="Haskell says the Carraccesque nudes were derived from the Palazzo Farnese in Rome.",
        qualification="Preserve the source's 'derived from' art-historical claim; it does not assert that the entire framework was copied from the palace.",
        mentioned=["cand-8189", "cand-0999", "cand-4490"], relation=True),
    new_statement("st-chp9-p250-carlevarijs-lodged-at-palace", first=93,
        subject="cand-0554", object_="cand-2871", predicate="carlevarijs_lodged_at_zenobio_palace",
        claim="Luca Carlevarijs lodged in the Zenobio palace.",
        qualification="The source gives no dates or duration for his lodging.", mentioned=["cand-0554", "cand-2871"], relation=True),
    new_statement("st-chp9-p250-carlevarijs-landscape-placement", first=93,
        subject="cand-8191", object_="cand-8192", predicate="zenobio_landscape_series_inserted_along_corridor_to_salone",
        claim="Carlevarijs's landscape series was inserted into frames along the corridor leading to the Salone.",
        qualification="The source specifies placement in corridor frames but not the individual frame or work positions.",
        mentioned=["cand-8191", "cand-8192", "cand-8193", "cand-2871"], relation=True),
    new_statement("st-chp9-p250-widmann-origin", first=94,
        subject="cand-2812", object_="cand-8190", predicate="widmann_family_described_as_carinthian",
        claim="Haskell describes the Widmann as of Carinthian origin.",
        qualification="No more precise Carinthian place of origin is given.", mentioned=["cand-2812", "cand-8190"], relation=False),
    new_statement("st-chp9-p250-widmann-palace-location", first=94,
        subject="cand-2813", object_="cand-8198", predicate="widmann_palace_near_s_canciano",
        claim="The Widmann had a splendid palace near S. Canciano.",
        qualification="'Near' is preserved as approximate location; no exact site is inferred.",
        mentioned=["cand-2812", "cand-2813", "cand-8198"], relation=False),
    new_statement("st-chp9-p250-widmann-canvases-show-scipio", first=94,
        subject="cand-8197", object_="cand-8196", predicate="lazzarini_canvases_show_scenes_from_scipios_life",
        claim="The Lazzarini canvases showed scenes from the life of Scipio Africanus.",
        qualification="The source does not identify individual canvases or particular episodes.",
        mentioned=["cand-8197", "cand-1368", "cand-8196"], relation=True),
    new_statement("st-chp9-p250-widmann-country-house-location", first=94,
        subject="cand-2811", object_="cand-8199", predicate="widmann_country_house_located_at_bagnoli_di_sopra",
        claim="The Widmann country house was at Bagnoli di Sopra.",
        qualification="This identifies the house's stated location, not its exact surviving building or boundaries.",
        mentioned=["cand-2812", "cand-2811", "cand-8199"], relation=True),
    new_statement("st-chp9-p250-labia-origin-status", first=95,
        subject="cand-1349", object_="cand-8202", predicate="labia_described_as_rich_businessmen_of_catalan_origin",
        claim="Haskell describes the Labia as rich businessmen of Catalan origin.",
        qualification="Keep the broad regional origin as stated; the sentence does not name individual family members or a specific Catalan locality.",
        mentioned=["cand-1349", "cand-8202"], relation=False),
    new_statement("st-chp9-p250-labia-palace-completed", first=95,
        subject="cand-8201", object_=None, predicate="labia_palace_completed_in_early_18th_century",
        claim="The Labia palace was completed in the early eighteenth century.",
        qualification="The source gives only a broad period, not a precise year.", mentioned=["cand-1349", "cand-8201"], relation=False),
    new_statement("st-chp9-p250-labia-wealth-display", first=95,
        subject="cand-1349", object_=None, predicate="labia_displayed_wealth_ostentatiously",
        claim="Haskell says the Labia displayed their great wealth as ostentatiously as possible.",
        qualification="This is the author's characterization of the family's display, not an independent measurement of wealth.",
        mentioned=["cand-1349"], relation=False),
    new_statement("st-chp9-p250-cochin-in-venice", first=104,
        subject="cand-0793", object_="cand-2719", predicate="cochin_was_in_venice_in_1750",
        claim="Charles-Nicolas Cochin was in Venice in 1750.",
        qualification="The statement is reported by Haskell; the source does not supply exact arrival or departure dates.",
        mentioned=["cand-0793", "cand-2719"], relation=True, layer="footnote",
        extras={"footnote_marker": 8, "cross_reference_segments": [{"segment_id": NOTES_SEGMENT_ID, "source_line_start": 348, "source_line_end": 348}]}),
]

for row in new_statements:
    if row["statement_id"] in statement_ids:
        raise SystemExit(f"new statement ID already exists: {row['statement_id']}")
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"new statement has missing candidate: {row['statement_id']} {candidate_id}")
    if row["original_quote"] not in "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"new statement quote is not reproduced by source: {row['statement_id']}")

mention_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
for row in restored_mentions:
    span = (row["segment_id"], row["start_char"], row["end_char"])
    if span in mention_spans:
        raise SystemExit(f"p.250 mention span already exists: {row['mention_id']}")
    mention_spans.add(span)
mention_rows.extend(restored_mentions)
mention_rows.append(archive_note_mention)
statement_rows.extend(new_statements)

# Ensure a superseded OCR correction is attached to the statement containing it.
new_families = statement_by_id["st-chp9-p250-new-families-patronage"]["qualifiers"]
new_families.pop("ocr_corrections", None)

coverage["note"] = (
    "Printed p.250 reviewed against CHP-9.pdf physical p.12. Restored and span-checked all 65 p.250 baseline mentions; "
    "added the exact note-8 mention for the existing 1749 Labia inventory candidate in the consolidated-notes segment. "
    "Reviewed all 15 existing statements, corrected the inventory endpoint to the archive, split compound claims, "
    "and recorded OCR corrections only in S2. The 1749 inventory was not independently consulted; S0 is unchanged."
)

final_target = [row for row in statement_rows if row.get("segment_id") == SEGMENT_ID]
if len(final_target) != 28 or any(row.get("qualifiers", {}).get("relation_candidate") is None for row in final_target):
    raise SystemExit(f"post-plan p.250 statement/classification check failed ({len(final_target)} rows)")
if statement_by_id["st-chp9-p250-labia-inventory-title-list"]["subject_candidate_id"] != archive_candidate_id:
    raise SystemExit("inventory statement does not point to the archival candidate")
if statement_by_id["st-chp9-p250-zenobio-palace-transformation"]["subject_candidate_id"] != "cand-2871":
    raise SystemExit("palace transformation has the wrong subject candidate")
for row in final_target:
    q = row["qualifiers"]
    for candidate_id in [row.get("subject_candidate_id"), row.get("object_candidate_id"), *q.get("mentioned_candidate_ids", [])]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"final statement references missing candidate: {row['statement_id']} {candidate_id}")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted p.250 S2 repair")
args = parser.parse_args()
summary = {
    "segment_id": SEGMENT_ID,
    "baseline_revision": BASELINE_REV,
    "source_segment_sha256": segment["sha256"],
    "restored_p250_mentions": len(restored_mentions),
    "added_note_mentions": 1,
    "existing_statements_reviewed": len(expected_existing_ids),
    "new_atomic_statements": len(new_statements),
    "final_p250_statements": len(final_target),
    "classifications_complete": all(row["qualifiers"]["relation_candidate"] is not None for row in final_target),
    "inventory_statement_endpoint": archive_candidate_id,
    "apply": args.apply,
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
if not args.apply:
    print("Dry run only; no table files were written.")
    raise SystemExit(0)

paths = [mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, coverage_rows)
print("Applied. Backups saved with suffix " + BACKUP_SUFFIX)
