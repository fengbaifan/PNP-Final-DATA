"""Controlled S2 migration for p.205 notes 1-4 in the composite note segment.

Default invocation validates and previews only. --apply writes the S2 tables
with recoverable backups after checking source fingerprints and current coverage.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
P205_BODY_ID = "chp-8:08_CHP-8_sec_i:l23-28"
EXPECTED_MAX_CANDIDATE = 7582
BACKUP_SUFFIX = ".bak-s2-chp8-p205-notes-20260930"

BODY_NOTE1_IDS = [
    "st-chp8-p205-roomer-most-influential-patron",
    "st-chp8-p205-roomer-survived-masaniello-revolt",
    "st-chp8-p205-roomer-lifespan-recovery-death",
    "st-chp8-p205-roomer-estate-and-collection-dispersal",
    "st-chp8-p205-roomer-proverb",
    "st-chp8-p205-roomer-taste-for-grotesque-subjects",
    "st-chp8-p205-roomer-favoured-caravaggists",
    "st-chp8-p205-roomer-owned-seven-ribera-paintings",
    "st-chp8-p205-roomer-owned-three-caracciolo-paintings",
    "st-chp8-p205-roomer-owned-three-stanzione-paintings",
    "st-chp8-p205-roomer-owned-three-saraceni-paintings-open",
]
BODY_NOTE2_ID = "st-chp8-p205-roomer-collected-drunk-silenus"
BODY_NOTE3_ID = "st-chp8-p205-roomer-collected-flaying-marsyas"
BODY_NOTE4_ID = "st-chp8-p205-sandrart-recalled-cato"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)

segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}

segment = segments.get(SEGMENT_ID)
if not segment or segment["source_file"] != SOURCE_REL:
    raise SystemExit(f"source segment metadata missing or changed: {SEGMENT_ID}")
if (int(segment["line_start"]), int(segment["line_end"])) != (126, 157):
    raise SystemExit(f"source segment line range changed: {SEGMENT_ID}")

source_path = ROOT / SOURCE_REL
source_bytes = source_path.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != segment["asset_sha256"]:
    raise SystemExit(f"source asset fingerprint changed: {SOURCE_REL}")
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[125:157]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit(f"source line-slice hash changed: {SEGMENT_ID}")
if segment_lines[4:8] != [
    "1 Except where specifically mentioned, all the information given here about Gaspar Roomer comes from the two excellent articles by Ceci and de Vaes (1925). These include quotations from and references to all the available first-hand sources—Sandrart, Capaccio, Celano, de Dominici, etc.",
    "2 Although this painting now at Capodimonte is dated 1626 it is not referred to in Capaccio’s list of the pictures in Roomer’s house in 1634; but Palomino (III, p. 311) describes it and says that it was painted for him. SeeTrapier, p. 36.",
    "3 The picture of this subject now in the Museo di S. Martino, on which this description is based, cannot be the actual one owned by Roomer as it is dated 1637 and Capaccio refers to a painting of the subject as being in his house in 1634—Trapier, p. 133, and Ville sur-Yllon, p. 147.",
    "4 Trapier, p. 230. There is also a print by Sebastiano Marcotti of St Januatius by Ribera, dated 1665 and dedicated to Roomer . . . affetti:mo della pittura e divot:o del Santo . ..'",
]:
    raise SystemExit("p.205 note source text changed; re-review before migration")

note_coverage = coverage_by_id.get(SEGMENT_ID)
if not note_coverage or (
    note_coverage["disposition"],
    note_coverage["migration_status"],
    note_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L127-129"):
    raise SystemExit(f"unexpected composite-note coverage state: {note_coverage}")
body_coverage = coverage_by_id.get(P205_BODY_ID)
if not body_coverage or (
    body_coverage["disposition"],
    body_coverage["migration_status"],
    body_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L24-28"):
    raise SystemExit(f"unexpected p.205 body coverage state: {body_coverage}")

body_statement_ids = {row["statement_id"] for row in statement_rows if row["segment_id"] == P205_BODY_ID}
required_body_statements = set(BODY_NOTE1_IDS + [BODY_NOTE2_ID, BODY_NOTE3_ID, BODY_NOTE4_ID])
if not required_body_statements <= body_statement_ids:
    raise SystemExit(f"p.205 body statements missing: {sorted(required_body_statements - body_statement_ids)}")
marker_ids = {
    row["statement_id"]
    for row in statement_rows
    if row.get("segment_id") == P205_BODY_ID and row.get("qualifiers", {}).get("footnote_marker") == 1
}
if marker_ids != set(BODY_NOTE1_IDS):
    raise SystemExit(f"p.205 note 1 body-link set changed: {sorted(marker_ids)}")

current_max = max(
    int(row["candidate_id"].split("-")[1])
    for row in candidate_rows
    if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()
)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")

EXISTING = {
    "roomer": "cand-2223",
    "sandrart": "cand-2353",
    "de_dominici": "cand-4835",
    "capodimonte": "cand-3662",
    "drunk_silenus": "cand-4089",
    "roomer_flaying": "cand-7412",
    "museum_san_martino": "cand-6201",
    "trapier": "cand-7002",
    "marcotti_person": "cand-1542",
    "ribera": "cand-2140",
}
if not set(EXISTING.values()) <= candidate_ids:
    raise SystemExit("one or more planned existing candidate IDs are absent")

CANDIDATE_SPECS = [
    (
        "ceci_roomer_article",
        "Giuseppe Ceci, Un mercante mecenate del secolo XVII: Gaspare Roomer (Napoli Nobilissima, 1920)",
        "archive",
        "Bibliography entry at 21_CHP-21Bibliography.md identifies this Roomer article as 1920, pp.160-164. Haskell's p.205 note calls it one of two articles by Ceci and de Vaes followed by '(1925)'; preserve the year-scope ambiguity rather than changing the bibliography record. Cited broadly, not independently read.",
        130,
    ),
    (
        "vaes_de_wael_article",
        "M. Vaes, Corneille de Wael (1592-1667) (Bulletin de l'Institut Belge de Rome, 1925)",
        "archive",
        "Bibliography entry at 21_CHP-21Bibliography.md identifies the 1925 article, pp.137-247. It is a plausible match for Haskell's short citation to de Vaes in p.205 note 1; retain the source's abbreviated author-year wording and do not claim the article was read.",
        130,
    ),
    (
        "celano_source_author",
        "Celano (author named among first-hand sources in p.205 n.1; identity unresolved)",
        "person",
        "Haskell names Celano among the first-hand sources quoted or referenced by the articles on Roomer but gives no first name, title, or locator here.",
        130,
    ),
    (
        "capaccio_roomer_list",
        "Capaccio's 1634 list of pictures in Gaspar Roomer's house (title and edition unresolved)",
        "archive",
        "Haskell says the list records pictures in Roomer's house in 1634. The note supplies no title, edition, or archival locator; both its absence claim for The Drunken Silenus and its subject reference for the Flaying of Marsyas are retained as second-hand reports.",
        131,
    ),
    (
        "palomino_vol3_p311",
        "Palomino, volume III, p. 311 (p.205 n.2 citation; identity alignment open)",
        "archive",
        "Haskell cites Palomino, volume III, p.311 for a description and attribution of The Drunken Silenus. The bibliography lists El Museo Pictorico y Escala Optica; do not merge this local locator candidate with the existing p.336 Palomino candidate cand-4955 before S3.",
        131,
    ),
    (
        "ville_sur_yllon_article",
        "Ludovico de la Ville sur-Yllon, Il palazzo dei duchi di Maddaloni alla Stella (Napoli Nobilissima, 1904)",
        "archive",
        "The bibliography identifies the article, pp.145-147; Haskell cites p.147 for the p.205 note 3 comparison. Cited page not independently read.",
        132,
    ),
    (
        "san_martino_flaying_1637",
        "Flaying of Marsyas picture at Museo di San Martino (dated 1637; not Roomer's 1634 picture)",
        "work",
        "Haskell says the picture at Museo di San Martino on which his description is based is dated 1637 and cannot be the actual picture listed in Roomer's house in 1634. Keep separate from the source-specific Roomer collection candidate cand-7412; exact object identity and maker are not independently established here.",
        132,
    ),
    (
        "marcotti_st_januarius_print",
        "Sebastiano Marcotti print of St Januarius by Ribera (1665; dedicated to Roomer)",
        "work",
        "Haskell reports a print by Marcotti of St Januarius by Ribera, dated 1665 and dedicated to Roomer. The source gives no title, surviving impression, or catalogue identifier; do not treat the print and any Ribera painting as the same object.",
        133,
    ),
    (
        "saint_januarius",
        "Saint Januarius (figure named in p.205 n.4)",
        "person",
        "The saint is named as the subject of a Marcotti print associated with Ribera; S0 OCR spells the name Januatius, while the p.205 print reads Januarius. Keep this subject separate from Ribera and from the print object.",
        133,
    ),
]

candidate_by_key = {}
new_candidates = []
next_number = current_max + 1
for key, name, suggested_type, detail, line_number in CANDIDATE_SPECS:
    candidate_id = f"cand-{next_number:04d}"
    next_number += 1
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID collision: {candidate_id}")
    if any(row.get("canonical_name") == name for row in candidate_rows):
        raise SystemExit(f"candidate natural key already exists; reuse or reconcile: {name}")
    candidate_by_key[key] = candidate_id
    new_candidates.append(
        {
            "candidate_id": candidate_id,
            "index_entry_id": "",
            "canonical_name": name,
            "index_page_range": "",
            "suggested_type": suggested_type,
            "status": "open",
            "index_source_file": "",
            "sub_entry": "",
            "detail": detail,
            "exclude_reason": "",
            "candidate_origin": "body-mention",
            "candidate_source_ref": f"{SEGMENT_ID}#L{line_number}",
        }
    )


def cid(key: str) -> str:
    return candidate_by_key[key] if key in candidate_by_key else EXISTING[key]


MENTION_SPECS = [
    (130, "Gaspar Roomer", "roomer", 0, "The named subject of the p.205 collection account."),
    (130, "Ceci", "ceci_roomer_article", 0, "Short citation mapped to the bibliography's 1920 Roomer article; the footnote's year placement remains ambiguous."),
    (130, "de Vaes", "vaes_de_wael_article", 0, "Short citation mapped provisionally to the bibliography's 1925 de Wael article; cited article not read."),
    (130, "Sandrart", "sandrart", 0, "Named as a first-hand source used by the two Roomer articles."),
    (130, "Capaccio", "capaccio_roomer_list", 0, "Named as a first-hand source; the specific 1634 Roomer picture list is separately cited in notes 2-3."),
    (130, "Celano", "celano_source_author", 0, "Named as a first-hand source; the note gives no title or full identity."),
    (130, "de Dominici", "de_dominici", 0, "Named among first-hand sources referenced by the cited articles."),
    (131, "this painting", "drunk_silenus", 0, "Anaphoric reference to Ribera's The Drunken Silenus in the p.205 body."),
    (131, "Capodimonte", "capodimonte", 0, "Reported current location of the painting; reuse the existing museum candidate."),
    (131, "Capaccio’s list", "capaccio_roomer_list", 0, "The cited 1634 list of pictures in Roomer's house."),
    (131, "Roomer", "roomer", 0, "Gaspar Roomer, named in the list's collection context."),
    (131, "Palomino", "palomino_vol3_p311", 0, "Short citation to volume III p.311; bibliography-to-candidate alignment remains for S3."),
    (131, "Trapier", "trapier", 0, "E. du Gué Trapier, Ribera (1952), cited at p.36."),
    (132, "The picture of this subject", "san_martino_flaying_1637", 0, "Distinct 1637 picture at Museo di San Martino, not the picture listed in Roomer's 1634 house inventory."),
    (132, "this subject", "roomer_flaying", 0, "Anaphoric reference to The Flaying of Marsyas candidate in the p.205 body."),
    (132, "Museo di S. Martino", "museum_san_martino", 0, "Museum named as the location of the distinct 1637 picture."),
    (132, "Roomer", "roomer", 0, "Gaspar Roomer, whose 1634 house list is the basis of the comparison."),
    (132, "Capaccio", "capaccio_roomer_list", 0, "Named as the source of the 1634 picture-list reference."),
    (132, "Trapier", "trapier", 0, "E. du Gué Trapier, Ribera (1952), cited at p.133."),
    (132, "Ville sur-Yllon", "ville_sur_yllon_article", 0, "Short citation to the bibliography-identified article, p.147."),
    (133, "Trapier", "trapier", 0, "E. du Gué Trapier, Ribera (1952), cited at p.230."),
    (133, "a print by Sebastiano Marcotti", "marcotti_st_januarius_print", 0, "The 1665 print; distinct from a Ribera painting."),
    (133, "Sebastiano Marcotti", "marcotti_person", 0, "Printmaker named in the note; reuse the index candidate."),
    (133, "St Januatius", "saint_januarius", 0, "S0 OCR form; the printed page reads St Januarius."),
    (133, "Ribera", "ribera", 0, "Painter named as associated with the image reproduced in the print."),
    (133, "Roomer", "roomer", 0, "Gaspar Roomer, to whom the print is reported as dedicated."),
    (133, "Santo", "saint_januarius", 0, "Italian dedication refers to the saint named as St Januarius earlier in the note."),
]

line_offsets = {}
offset = 0
for number in range(126, 158):
    line_offsets[number] = offset
    offset += len(source_lines[number - 1]) + 1

new_mentions = []
for index, (line_number, surface, key, occurrence, note) in enumerate(MENTION_SPECS, 1):
    line = source_lines[line_number - 1]
    spans = [match.span() for match in re.finditer(re.escape(surface), line)]
    if occurrence >= len(spans):
        raise SystemExit(f"mention not found: L{line_number} {surface!r}; found {len(spans)}")
    local_start, local_end = spans[occurrence]
    start_char = line_offsets[line_number] + local_start
    end_char = line_offsets[line_number] + local_end
    if segment_text[start_char:end_char] != surface:
        raise SystemExit(f"mention offset mismatch: L{line_number} {surface!r}")
    new_mentions.append(
        {
            "mention_id": f"m-chp8-p205-note-{index:03d}",
            "segment_id": SEGMENT_ID,
            "candidate_id": cid(key),
            "surface_form": surface,
            "start_char": str(start_char),
            "end_char": str(end_char),
            "note": note,
        }
    )


def make_statement(
    statement_id,
    subject_candidate_id,
    object_candidate_id,
    predicate,
    line_start,
    line_end,
    claim,
    qualification,
    original_quote,
    mentioned_candidate_ids,
    footnote_number,
    *,
    text_layer="footnote",
    speaker="Haskell",
    linked_body_statement_ids=None,
    citations=None,
    relation_candidate=False,
    ocr_corrections=None,
    extra_qualifiers=None,
):
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 205,
        "pdf_physical_page": 3,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned_candidate_ids,
        "footnote_number": footnote_number,
    }
    if linked_body_statement_ids:
        qualifiers["linked_body_statement_ids"] = linked_body_statement_ids
    if citations is not None:
        qualifiers["citations"] = citations
    if relation_candidate:
        qualifiers["relation_candidate"] = True
    if ocr_corrections:
        qualifiers["ocr_corrections"] = ocr_corrections
    if extra_qualifiers:
        qualifiers.update(extra_qualifiers)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject_candidate_id,
        "object_candidate_id": object_candidate_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": original_quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


new_statements = [
    make_statement(
        "st-chp8-p205-n1-roomer-source-citations",
        None,
        cid("ceci_roomer_article"),
        "footnote_citation",
        130,
        130,
        "Haskell says that, except where noted, his information about Gaspar Roomer comes from articles by Ceci and de Vaes (1925).",
        "The bibliography identifies Ceci's Roomer article as 1920 and M. Vaes's Corneille de Wael article as 1925; the note's parenthetical year is not clearly scoped, so keep both source wording and bibliography dates. Neither article is independently read.",
        "Except where specifically mentioned, all the information given here about Gaspar Roomer comes from the two excellent articles by Ceci and de Vaes (1925).",
        [cid("roomer"), cid("ceci_roomer_article"), cid("vaes_de_wael_article")],
        1,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=BODY_NOTE1_IDS,
        citations=[
            {"source_candidate_id": cid("ceci_roomer_article"), "locator": "passim"},
            {"source_candidate_id": cid("vaes_de_wael_article"), "locator": "passim"},
        ],
    ),
    make_statement(
        "st-chp8-p205-n1-articles-reference-firsthand-sources",
        cid("ceci_roomer_article"),
        cid("vaes_de_wael_article"),
        "roomer_articles_said_to_quote_and_reference_available_firsthand_sources",
        130,
        130,
        "Haskell says the two articles include quotations from and references to the available first-hand sources, naming Sandrart, Capaccio, Celano and de Dominici among others.",
        "This records Haskell's description of the articles' source apparatus. The named sources and the cited articles are not independently consulted here.",
        "These include quotations from and references to all the available first-hand sources—Sandrart, Capaccio, Celano, de Dominici, etc.",
        [
            cid("ceci_roomer_article"),
            cid("vaes_de_wael_article"),
            cid("sandrart"),
            cid("capaccio_roomer_list"),
            cid("celano_source_author"),
            cid("de_dominici"),
        ],
        1,
        linked_body_statement_ids=BODY_NOTE1_IDS,
    ),
    make_statement(
        "st-chp8-p205-n2-palomino-capaccio-trapier-citations",
        None,
        cid("capaccio_roomer_list"),
        "footnote_citation",
        131,
        131,
        "P.205 note 2 cites Capaccio's 1634 list, Palomino volume III page 311, and Trapier page 36 in discussing the Ribera painting.",
        "These are citation locators as reported by Haskell; the listed sources and cited pages are not independently read. The Palomino locator remains separate from the existing p.336 candidate pending S3 alignment.",
        "Although this painting now at Capodimonte is dated 1626 it is not referred to in Capaccio’s list of the pictures in Roomer’s house in 1634; but Palomino (III, p. 311) describes it and says that it was painted for him. SeeTrapier, p. 36.",
        [cid("capaccio_roomer_list"), cid("palomino_vol3_p311"), cid("trapier"), cid("drunk_silenus")],
        2,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=[BODY_NOTE2_ID],
        citations=[
            {"source_candidate_id": cid("capaccio_roomer_list"), "locator": "Roomer house picture list, 1634"},
            {"source_candidate_id": cid("palomino_vol3_p311"), "volume": "III", "page": "311"},
            {"source_candidate_id": cid("trapier"), "page": "36"},
        ],
        ocr_corrections=[
            {
                "source_file": SOURCE_REL,
                "source_line": 131,
                "ocr": "SeeTrapier",
                "print": "See Trapier",
                "basis": "CHP-8.pdf physical page 3.",
            }
        ],
    ),
    make_statement(
        "st-chp8-p205-drunk-silenus-capaccio-1634-list",
        cid("drunk_silenus"),
        cid("capaccio_roomer_list"),
        "dated_1626_at_capodimonte_not_listed_in_roomer_house_picture_list_1634",
        131,
        131,
        "Haskell says the painting at Capodimonte is dated 1626 and is not referred to in Capaccio's list of pictures in Roomer's house in 1634.",
        "The claim concerns The Drunken Silenus through the preceding body reference; the list itself is not independently checked, and its omission does not establish when the painting entered or left Roomer's collection.",
        "Although this painting now at Capodimonte is dated 1626 it is not referred to in Capaccio’s list of the pictures in Roomer’s house in 1634",
        [cid("drunk_silenus"), cid("capodimonte"), cid("capaccio_roomer_list"), cid("roomer")],
        2,
        linked_body_statement_ids=[BODY_NOTE2_ID],
        extra_qualifiers={"reported_date": "1626", "reported_current_location_candidate_id": cid("capodimonte")},
    ),
    make_statement(
        "st-chp8-p205-palomino-says-drunken-silenus-painted-for-roomer",
        cid("drunk_silenus"),
        cid("roomer"),
        "palomino_reported_to_say_painting_was_painted_for_roomer",
        131,
        131,
        "Haskell reports that Palomino describes the painting and says it was painted for Roomer.",
        "This attribution is reported by Haskell through Palomino volume III page 311; neither that page nor the cited edition is independently read. Retain it alongside the separate report that Capaccio's 1634 list omits the picture.",
        "Palomino (III, p. 311) describes it and says that it was painted for him.",
        [cid("drunk_silenus"), cid("palomino_vol3_p311"), cid("roomer")],
        2,
        linked_body_statement_ids=[BODY_NOTE2_ID],
        relation_candidate=True,
    ),
    make_statement(
        "st-chp8-p205-n3-capaccio-trapier-ville-citations",
        None,
        cid("capaccio_roomer_list"),
        "footnote_citation",
        132,
        132,
        "P.205 note 3 cites Capaccio, Trapier page 133, and Ville sur-Yllon page 147 in distinguishing the 1637 Museo di San Martino picture from the subject recorded at Roomer's house in 1634.",
        "Citation locations only; the listed source and cited pages are not independently read.",
        "The picture of this subject now in the Museo di S. Martino, on which this description is based, cannot be the actual one owned by Roomer as it is dated 1637 and Capaccio refers to a painting of the subject as being in his house in 1634—Trapier, p. 133, and Ville sur-Yllon, p. 147.",
        [cid("capaccio_roomer_list"), cid("trapier"), cid("ville_sur_yllon_article")],
        3,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=[BODY_NOTE3_ID],
        citations=[
            {"source_candidate_id": cid("capaccio_roomer_list"), "locator": "Roomer house picture list, 1634"},
            {"source_candidate_id": cid("trapier"), "page": "133"},
            {"source_candidate_id": cid("ville_sur_yllon_article"), "page": "147"},
        ],
    ),
    make_statement(
        "st-chp8-p205-san-martino-flaying-not-roomer-1634-picture",
        cid("san_martino_flaying_1637"),
        cid("roomer_flaying"),
        "1637_san_martino_picture_not_the_flaying_of_marsyas_listed_at_roomer_in_1634",
        132,
        132,
        "Haskell says the 1637 picture of this subject at Museo di San Martino, on which his description is based, cannot be the actual painting listed at Roomer's house in 1634.",
        "This is Haskell's explicit version distinction, supported in the note by Capaccio, Trapier and Ville sur-Yllon locators. Preserve the museum picture and the Roomer-listed picture as separate candidates; neither source object is independently examined.",
        "The picture of this subject now in the Museo di S. Martino, on which this description is based, cannot be the actual one owned by Roomer as it is dated 1637 and Capaccio refers to a painting of the subject as being in his house in 1634",
        [
            cid("san_martino_flaying_1637"),
            cid("roomer_flaying"),
            cid("museum_san_martino"),
            cid("roomer"),
            cid("capaccio_roomer_list"),
        ],
        3,
        linked_body_statement_ids=[BODY_NOTE3_ID],
        extra_qualifiers={"reported_date": "1637", "reported_location_candidate_id": cid("museum_san_martino")},
    ),
    make_statement(
        "st-chp8-p205-n4-trapier-citation",
        None,
        cid("trapier"),
        "footnote_citation",
        133,
        133,
        "P.205 note 4 cites Trapier page 230 for the Sandrart-recalled Cato image.",
        "Trapier page 230 is a bibliographic locator only; the cited page is not independently read.",
        "Trapier, p. 230.",
        [cid("trapier")],
        4,
        text_layer="bibliographic citation",
        speaker="Haskell footnote",
        linked_body_statement_ids=[BODY_NOTE4_ID],
        citations=[{"source_candidate_id": cid("trapier"), "page": "230"}],
    ),
    make_statement(
        "st-chp8-p205-marcotti-januarius-print-dedicated-to-roomer",
        cid("marcotti_st_januarius_print"),
        cid("roomer"),
        "marcotti_print_of_ribera_januarius_dated_1665_and_dedicated_to_roomer",
        133,
        133,
        "Haskell reports a 1665 print by Sebastiano Marcotti of St Januarius by Ribera, dedicated to Roomer, with an abbreviated Italian dedication.",
        "The note gives no title, surviving impression, or catalogue identifier. Treat the print as a distinct work candidate; do not identify it with a Ribera painting. The source's Januatius spelling is an OCR error for the printed Januarius.",
        "There is also a print by Sebastiano Marcotti of St Januatius by Ribera, dated 1665 and dedicated to Roomer . . . affetti:mo della pittura e divot:o del Santo . ..'",
        [
            cid("marcotti_st_januarius_print"),
            cid("marcotti_person"),
            cid("saint_januarius"),
            cid("ribera"),
            cid("roomer"),
        ],
        4,
        linked_body_statement_ids=[BODY_NOTE4_ID],
        relation_candidate=True,
        ocr_corrections=[
            {
                "source_file": SOURCE_REL,
                "source_line": 133,
                "ocr": "St Januatius",
                "print": "St Januarius",
                "basis": "CHP-8.pdf physical page 3.",
            }
        ],
        extra_qualifiers={"reported_date": "1665", "dedication_text_as_transcribed": "affetti:mo della pittura e divot:o del Santo"},
    ),
]

planned_candidate_ids = {row["candidate_id"] for row in new_candidates}
planned_mention_ids = {row["mention_id"] for row in new_mentions}
planned_statement_ids = {row["statement_id"] for row in new_statements}
if len(planned_candidate_ids) != len(new_candidates) or candidate_ids & planned_candidate_ids:
    raise SystemExit("planned candidate IDs collide")
if len(planned_mention_ids) != len(new_mentions) or mention_ids & planned_mention_ids:
    raise SystemExit("planned mention IDs collide")
if len(planned_statement_ids) != len(new_statements) or statement_ids & planned_statement_ids:
    raise SystemExit("planned statement IDs collide")

all_candidate_ids = candidate_ids | planned_candidate_ids
for row in new_mentions:
    if row["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']}")
for row in new_statements:
    for candidate_id in [row["subject_candidate_id"], row["object_candidate_id"], *row["qualifiers"]["mentioned_candidate_ids"]]:
        if candidate_id is not None and candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement has unknown candidate: {row['statement_id']} -> {candidate_id}")

candidate_new = candidate_rows + new_candidates
mention_new = mention_rows + new_mentions
statement_new = statement_rows + new_statements
coverage_new = []
for row in coverage_rows:
    copied = dict(row)
    if copied["segment_id"] == SEGMENT_ID:
        copied["source_line_ranges"] = "L127-133"
        copied["note"] = (
            "P.204 notes 1-3 (L127-129) and p.205 notes 1-4 (L130-133) read against CHP-8.pdf physical pp.2-3 and migrated. "
            "Ceci and Vaes article identities are mapped to bibliography entries while the note's year scope remains ambiguous. "
            "Capaccio, Palomino, Trapier and Ville sur-Yllon references are locators only; cited pages are not independently read. "
            "The 1637 Museo di San Martino Flaying of Marsyas is kept distinct from the Roomer-listed 1634 picture; "
            "the Marcotti print is separate from any Ribera painting. OCR corrections are recorded in S2 only. L134-L157 remain pending."
        )
    elif copied["segment_id"] == P205_BODY_ID:
        copied["migration_status"] = "complete"
        copied["note"] = (
            "P.205 body read against CHP-8.pdf physical p.3. Footnotes 1-4 have now been migrated from the composite "
            "source segment L130-L133 and linked to their body statements. The 1637 Museo di San Martino painting is "
            "kept distinct from the painting reported in Roomer's 1634 house list. Citations are locators, not independent verification."
        )
    coverage_new.append(copied)


def preview():
    print(f"validated segment: {SEGMENT_ID} lines 126-157")
    print("processed source range: L130-133 (p.205 notes 1-4)")
    print(f"new candidates: {len(new_candidates)}; IDs {new_candidates[0]['candidate_id']}..{new_candidates[-1]['candidate_id']}")
    print(f"new mentions: {len(new_mentions)}")
    print(f"new statements: {len(new_statements)}")
    print("p.205 body coverage: reviewed/complete")
    print("composite note coverage: reviewed/partial, L127-133; L134-157 pending")


def apply():
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    write_csv_atomic(candidate_path, candidate_fields, candidate_new)
    write_csv_atomic(mention_path, mention_fields, mention_new)
    write_jsonl_atomic(statement_path, statement_new)
    write_csv_atomic(coverage_path, coverage_fields, coverage_new)
    print("APPLIED; recovery backups retained pending audits:")
    for backup in backups:
        print(backup.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after all preflight checks pass")
    args = parser.parse_args()
    preview()
    if args.apply:
        apply()
    else:
        print("DRY RUN: no files written")


if __name__ == "__main__":
    main()
