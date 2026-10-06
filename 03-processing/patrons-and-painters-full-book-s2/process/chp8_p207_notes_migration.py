"""Controlled S2 migration for p.207 notes 1-2 (composite lines L136-L137)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
P207_BODY_ID = "chp-8:08_CHP-8_sec_i:l43-51"
EXPECTED_MAX_CANDIDATE = 7592
BACKUP_SUFFIX = ".bak-s2-chp8-p207-notes-20260930"

BODY_NOTE1_ID = "st-chp8-p207-roomer-sought-castiglione-bamboccianti-and-battle-painter-works"
BODY_NOTE2_ID = "st-chp8-p207-de-dominici-said-picture-lovers-followed-roomer-advice"


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
if hashlib.sha256(source_path.read_bytes()).hexdigest() != segment["asset_sha256"]:
    raise SystemExit(f"source asset fingerprint changed: {SOURCE_REL}")
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[125:157]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit(f"source line-slice hash changed: {SEGMENT_ID}")
if segment_lines[10:12] != [
    "1 When Roomer died he left seventy of his pictures to Ferdinand van den Einden, the son of his business associate Jan. Van den Einden, who himself had a fine collection, imturn left a third of his pictures to each of his three daughters. One of these married Don Giuliano Colonna, and in 1688 the inventory of their collection was drawn up by Luca Giordano (Ferdinando Colonna, pp. 29-32). There are good—but not conclusive—grounds for believing that many of these paintings must have come from Van den Einden —and originally from Roomer. Indeed we know that the two pictures by Codazzi with figures by Micco Spadaro of The Pool of Bethesda and The Woman taken in Adultery did pass through the three collections in just this way (de Dominici, III, pp. 421-2). Unfortunately evidence as regards other pictures in the Colonna collection is lacking, and I cannot accept Vaes’s certainty about their provenance.",
    "2 De Dominici, IV, p. 47.",
]:
    raise SystemExit("p.207 note source text changed; re-review before migration")

note_coverage = coverage_by_id.get(SEGMENT_ID)
if not note_coverage or (
    note_coverage["disposition"],
    note_coverage["migration_status"],
    note_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L127-135"):
    raise SystemExit(f"unexpected composite-note coverage state: {note_coverage}")
body_coverage = coverage_by_id.get(P207_BODY_ID)
if not body_coverage or (
    body_coverage["disposition"],
    body_coverage["migration_status"],
    body_coverage.get("source_line_ranges"),
) != ("reviewed", "partial", "L44-51"):
    raise SystemExit(f"unexpected p.207 body coverage state: {body_coverage}")

body_statement_ids = {row["statement_id"] for row in statement_rows if row["segment_id"] == P207_BODY_ID}
if not {BODY_NOTE1_ID, BODY_NOTE2_ID} <= body_statement_ids:
    raise SystemExit("one or more p.207 body statements for notes 1-2 are missing")
for marker, expected_id in [(1, BODY_NOTE1_ID), (2, BODY_NOTE2_ID)]:
    marker_ids = {
        row["statement_id"]
        for row in statement_rows
        if row.get("segment_id") == P207_BODY_ID and row.get("qualifiers", {}).get("footnote_marker") == marker
    }
    if marker_ids != {expected_id}:
        raise SystemExit(f"unexpected p.207 body-link set for footnote {marker}: {sorted(marker_ids)}")

current_max = max(
    int(row["candidate_id"].split("-")[1])
    for row in candidate_rows
    if row["candidate_id"].startswith("cand-") and row["candidate_id"].split("-")[1].isdigit()
)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")

EXISTING = {
    "roomer": "cand-2223",
    "roomer_collection": "cand-7407",
    "ferdinand": "cand-0914",
    "jan": "cand-0915",
    "ferdinand_collection": "cand-7461",
    "giuliano_colonna": "cand-0810",
    "luca_giordano": "cand-1172",
    "codazzi": "cand-0794",
    "micco_spadaro": "cand-2495",
    "de_dominici_book": "cand-4835",
    "vaes_person": "cand-6386",
}
if not set(EXISTING.values()) <= candidate_ids:
    raise SystemExit("one or more planned existing candidate IDs are absent")

CANDIDATE_SPECS = [
    (
        "cand-7593",
        "The Pool of Bethesda (Codazzi painting with figures by Micco Spadaro; p.207 n.1)",
        "work",
        "Haskell names this picture as one of two works by Codazzi with figures by Micco Spadaro, reported to have passed through the Roomer, Van den Einden, and Colonna collections. Keep it distinct from the index subentry candidates for its makers; no date, current location, or catalogue identity is supplied here.",
        136,
    ),
    (
        "cand-7594",
        "The Woman taken in Adultery (Codazzi painting with figures by Micco Spadaro; p.207 n.1)",
        "work",
        "Haskell names this picture as one of two works by Codazzi with figures by Micco Spadaro, reported to have passed through the Roomer, Van den Einden, and Colonna collections. Keep it distinct from the index subentry candidates for its makers; no date, current location, or catalogue identity is supplied here.",
        136,
    ),
    (
        "cand-7595",
        "Unidentified 1688 collection of Don Giuliano Colonna and one of Van den Einden’s daughters",
        "",
        "Haskell refers to the collection of Don Giuliano Colonna and an unnamed daughter of Ferdinand van den Einden, whose inventory Luca Giordano drew up in 1688. This is distinct from other Colonna-family collections; the project taxonomy has no collection type.",
        136,
    ),
    (
        "cand-7596",
        "Ferdinando Colonna, pp. 29-32 (p.207 n.1 cited work; identity unresolved)",
        "archive",
        "Haskell cites ‘Ferdinando Colonna, pp. 29-32’ for the 1688 inventory of the Colonna collection. The note does not supply a title or edition, and the cited pages were not independently read. Keep this bibliographic pointer separate from the person candidate until S3 alignment.",
        136,
    ),
    (
        "cand-7597",
        "1688 inventory of the Colonna collection drawn up by Luca Giordano (p.207 n.1)",
        "archive",
        "The footnote reports an inventory of the collection of Don Giuliano Colonna and an unnamed wife, drawn up by Luca Giordano in 1688. Haskell cites an unidentified Ferdinando Colonna source, pp.29-32; the inventory itself is not independently consulted.",
        136,
    ),
    (
        "cand-7598",
        "Unidentified daughter of Ferdinand van den Einden who married Don Giuliano Colonna",
        "person",
        "Haskell identifies one of Ferdinand van den Einden’s three daughters as the wife of Don Giuliano Colonna but gives no personal name. Retain her as an unidentified person and do not infer identity from the Colonna surname.",
        136,
    ),
]
new_candidates = []
candidate_by_key = {}
for candidate_id, name, suggested_type, detail, source_line in CANDIDATE_SPECS:
    if candidate_id in candidate_ids:
        raise SystemExit(f"planned candidate ID already exists: {candidate_id}")
    if any(row.get("canonical_name") == name for row in candidate_rows):
        raise SystemExit(f"candidate natural key already exists; reuse or reconcile: {name}")
    key = candidate_id
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
            "candidate_source_ref": f"{SEGMENT_ID}#L{source_line}",
        }
    )


def offset_for_line(source_line: int) -> int:
    return sum(len(line) + 1 for line in segment_lines[: source_line - 126])


def make_mention(mention_id, source_line, surface, candidate_id, note, occurrence=0):
    source_text = segment_lines[source_line - 126]
    starts = []
    pos = 0
    while True:
        pos = source_text.find(surface, pos)
        if pos < 0:
            break
        starts.append(pos)
        pos += max(1, len(surface))
    if occurrence >= len(starts):
        raise SystemExit(f"mention surface occurrence is absent on L{source_line}: {surface!r} #{occurrence}")
    start = offset_for_line(source_line) + starts[occurrence]
    return {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }


new_mentions = [
    make_mention("m-chp8-p207-note-001", 136, "Roomer", EXISTING["roomer"], "Testator named in the note; the specific painting bequest is a reported claim.", 0),
    make_mention("m-chp8-p207-note-002", 136, "seventy of his pictures", EXISTING["roomer_collection"], "Quantity of pictures left to Ferdinand; the individual pictures are not identified."),
    make_mention("m-chp8-p207-note-003", 136, "Ferdinand van den Einden", EXISTING["ferdinand"], "Named heir and son of Roomer’s business associate Jan."),
    make_mention("m-chp8-p207-note-004", 136, "Jan", EXISTING["jan"], "Business associate of Roomer and father of Ferdinand, as stated by Haskell."),
    make_mention("m-chp8-p207-note-005", 136, "himself had a fine collection", EXISTING["ferdinand_collection"], "The collection is attributed to Ferdinand; it has no collection type in the current taxonomy."),
    make_mention("m-chp8-p207-note-006", 136, "a third of his pictures", EXISTING["ferdinand_collection"], "Share left by Ferdinand to each of his three daughters."),
    make_mention("m-chp8-p207-note-007", 136, "One of these", "cand-7598", "Anaphoric reference to one of Ferdinand’s three unnamed daughters."),
    make_mention("m-chp8-p207-note-008", 136, "Don Giuliano Colonna", EXISTING["giuliano_colonna"], "Named as the husband of one unidentified daughter."),
    make_mention("m-chp8-p207-note-009", 136, "their collection", "cand-7595", "The collection of Giuliano Colonna and the unnamed daughter, inventoried in 1688."),
    make_mention("m-chp8-p207-note-010", 136, "Luca Giordano", EXISTING["luca_giordano"], "Named as the person who drew up the 1688 inventory."),
    make_mention("m-chp8-p207-note-011", 136, "Ferdinando Colonna, pp. 29-32", "cand-7596", "Unresolved bibliographic pointer; cited pages not independently read."),
    make_mention("m-chp8-p207-note-012", 136, "many of these paintings", "cand-7595", "Unquantified subset of pictures in the Colonna collection; provenance is explicitly tentative."),
    make_mention("m-chp8-p207-note-013", 136, "Van den Einden", EXISTING["ferdinand"], "Intermediate provenance collection’s owner, named in Haskell’s tentative account.", 0),
    make_mention("m-chp8-p207-note-014", 136, "Van den Einden", EXISTING["ferdinand"], "Intermediate owner in the reported provenance sequence.", 1),
    make_mention("m-chp8-p207-note-015", 136, "Roomer", EXISTING["roomer"], "Original collection in the tentative provenance sequence.", 1),
    make_mention("m-chp8-p207-note-016", 136, "The Pool of Bethesda", "cand-7593", "Named painting; kept distinct from its makers and from index subentry candidates."),
    make_mention("m-chp8-p207-note-017", 136, "The Woman taken in Adultery", "cand-7594", "Named painting; kept distinct from its makers and from index subentry candidates."),
    make_mention("m-chp8-p207-note-018", 136, "Codazzi", EXISTING["codazzi"], "Painter named as maker of the architecture in both pictures."),
    make_mention("m-chp8-p207-note-019", 136, "Micco Spadaro", EXISTING["micco_spadaro"], "Painter named for the figures in the two Codazzi pictures."),
    make_mention("m-chp8-p207-note-020", 136, "de Dominici, III, pp. 421-2", EXISTING["de_dominici_book"], "Citation locator for Haskell’s report about the two pictures; cited pages not independently read."),
    make_mention("m-chp8-p207-note-021", 136, "the Colonna collection", "cand-7595", "Evidence is expressly said to be lacking for other pictures in this collection."),
    make_mention("m-chp8-p207-note-022", 136, "Vaes", EXISTING["vaes_person"], "Haskell refers to Vaes’s provenance certainty but does not supply a title or locator in this note."),
    make_mention("m-chp8-p207-note-023", 137, "De Dominici, IV, p. 47", EXISTING["de_dominici_book"], "Citation locator for the p.207 body quotation; cited page not independently read."),
]


def make_statement(statement_id, source_line, quote, subject, object_id, predicate, claim, qualification, mentions, body_id, marker, text_layer, extra=None):
    qualifiers = {
        "source_line_start": source_line,
        "source_line_end": source_line,
        "printed_page": 207,
        "pdf_physical_page": 5,
        "claim": claim,
        "speaker": "Haskell footnote",
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentions,
        "footnote_marker": marker,
        "linked_body_statement_ids": [body_id],
        "footnote_segment": SEGMENT_ID,
        "footnote_body_link_status": "linked",
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_REL,
    }


N1 = BODY_NOTE1_ID
N2 = BODY_NOTE2_ID
R = EXISTING["roomer"]
F = EXISTING["ferdinand"]
J = EXISTING["jan"]
ROOMER_COLLECTION = EXISTING["roomer_collection"]
FERDINAND_COLLECTION = EXISTING["ferdinand_collection"]
GIULIANO = EXISTING["giuliano_colonna"]
LUCA = EXISTING["luca_giordano"]
CODAZZI = EXISTING["codazzi"]
SPADARO = EXISTING["micco_spadaro"]
DE_DOMINICI = EXISTING["de_dominici_book"]
VAES = EXISTING["vaes_person"]
POOL = "cand-7593"
WOMAN = "cand-7594"
COLONNA_COLLECTION = "cand-7595"
COLONNA_REFERENCE = "cand-7596"
COLONNA_INVENTORY = "cand-7597"
DAUGHTER = "cand-7598"

new_statements = [
    make_statement(
        "st-chp8-p207-n1-cite-ferdinando-colonna", 136,
        "Ferdinando Colonna, pp. 29-32", None, COLONNA_REFERENCE, "footnote_citation",
        "Haskell cites an unidentified Ferdinando Colonna source, pp.29-32, for the 1688 inventory of the Colonna collection.",
        "Bibliographic locator only; the cited work and pages are not independently identified or read.",
        [COLONNA_REFERENCE, COLONNA_INVENTORY, COLONNA_COLLECTION, LUCA], N1, 1, "bibliographic pointer",
        {"citations": [{"source_candidate_id": COLONNA_REFERENCE, "page_start": "29", "page_end": "32"}]},
    ),
    make_statement(
        "st-chp8-p207-n1-cite-de-dominici", 136,
        "de Dominici, III, pp. 421-2", None, DE_DOMINICI, "footnote_citation",
        "Haskell cites De Dominici, volume III, pp.421-422, for the reported passage of two Codazzi pictures through three collections.",
        "Citation locator only; the cited volume and pages were not independently read.",
        [DE_DOMINICI, POOL, WOMAN, CODAZZI, SPADARO, ROOMER_COLLECTION, FERDINAND_COLLECTION, COLONNA_COLLECTION], N1, 1, "bibliographic pointer",
        {"citations": [{"source_candidate_id": DE_DOMINICI, "volume": "III", "page_start": "421", "page_end": "422"}]},
    ),
    make_statement(
        "st-chp8-p207-n1-roomer-bequeathed-seventy-pictures-to-ferdinand", 136,
        "When Roomer died he left seventy of his pictures to Ferdinand van den Einden, the son of his business associate Jan.",
        R, F, "bequeathed_seventy_pictures_to_heir",
        "Haskell says Roomer left seventy pictures to Ferdinand van den Einden, the son of his business associate Jan.",
        "This is Haskell’s report in a footnote; it does not identify the individual pictures or an estate document.",
        [R, F, J, ROOMER_COLLECTION], N1, 1, "footnote narrative claim",
        {"quantity": 70, "relation_candidate": True},
    ),
    make_statement(
        "st-chp8-p207-n1-ferdinand-left-thirds-to-daughters", 136,
        "Van den Einden, who himself had a fine collection, imturn left a third of his pictures to each of his three daughters.",
        F, None, "left_one_third_of_pictures_to_each_of_three_daughters",
        "Haskell says Ferdinand van den Einden had a collection and left one third of his pictures to each of his three daughters.",
        "The three daughters are unnamed as a group; the statement does not assign a particular third to the daughter who married Giuliano Colonna.",
        [F, FERDINAND_COLLECTION, DAUGHTER], N1, 1, "footnote narrative claim",
        {"share_text": "a third of his pictures", "recipient_count": 3, "relation_candidate": True,
         "ocr_corrections": [{"source_file": SOURCE_REL, "source_line": 136, "ocr": "imturn", "print": "in turn", "basis": "CHP-8.pdf physical page 5."}]},
    ),
    make_statement(
        "st-chp8-p207-n1-daughter-married-giuliano-colonna", 136,
        "One of these married Don Giuliano Colonna", DAUGHTER, GIULIANO, "married",
        "Haskell says one unidentified daughter of Ferdinand van den Einden married Don Giuliano Colonna.",
        "The daughter is not named; do not resolve her identity from the Colonna surname.",
        [DAUGHTER, F, GIULIANO], N1, 1, "footnote narrative claim",
        {"relation_candidate": True},
    ),
    make_statement(
        "st-chp8-p207-n1-colonna-collection-inventoried-in-1688", 136,
        "in 1688 the inventory of their collection was drawn up by Luca Giordano", COLONNA_INVENTORY, COLONNA_COLLECTION,
        "inventory_record_of_collection",
        "Haskell says Luca Giordano drew up an inventory of the couple’s collection in 1688.",
        "The statement reports the inventory described by Haskell and does not claim that the inventory itself was consulted.",
        [COLONNA_INVENTORY, COLONNA_COLLECTION, LUCA, GIULIANO, DAUGHTER], N1, 1, "footnote narrative claim",
        {"date_text": "1688", "agent_candidate_id": LUCA, "relation_candidate": True},
    ),
    make_statement(
        "st-chp8-p207-n1-tentative-colonna-picture-provenance", 136,
        "There are good—but not conclusive—grounds for believing that many of these paintings must have come from Van den Einden —and originally from Roomer.",
        COLONNA_COLLECTION, ROOMER_COLLECTION, "many_pictures_may_have_provenance_through_van_den_einden_from_roomer",
        "Haskell says there are good but inconclusive grounds to believe many pictures in the Colonna collection came from Van den Einden and originally from Roomer.",
        "This is explicitly tentative, applies to many but not all pictures, and does not establish item-level provenance. Keep the Van den Einden collection as an intermediate source.",
        [COLONNA_COLLECTION, FERDINAND_COLLECTION, ROOMER_COLLECTION, F, R], N1, 1, "footnote narrative claim",
        {"modality": "good but not conclusive grounds for believing", "intermediate_collection_candidate_id": FERDINAND_COLLECTION,
         "inference": True, "relation_candidate": True},
    ),
    make_statement(
        "st-chp8-p207-n1-pool-of-bethesda-passed-through-three-collections", 136,
        "Indeed we know that the two pictures by Codazzi with figures by Micco Spadaro of The Pool of Bethesda",
        POOL, COLONNA_COLLECTION, "painting_reported_to_have_passed_roomer_van_den_einden_colonna_collections",
        "Haskell says The Pool of Bethesda by Codazzi, with figures by Micco Spadaro, passed through the Roomer, Van den Einden, and Colonna collections.",
        "This is Haskell’s footnote report, supported there by a De Dominici locator; the cited pages and specific object histories were not independently checked.",
        [POOL, CODAZZI, SPADARO, ROOMER_COLLECTION, FERDINAND_COLLECTION, COLONNA_COLLECTION, DE_DOMINICI], N1, 1, "footnote narrative claim",
        {"reported_collection_sequence": [ROOMER_COLLECTION, FERDINAND_COLLECTION, COLONNA_COLLECTION], "relation_candidate": True,
         "citations": [{"source_candidate_id": DE_DOMINICI, "volume": "III", "page_start": "421", "page_end": "422"}]},
    ),
    make_statement(
        "st-chp8-p207-n1-woman-taken-in-adultery-passed-through-three-collections", 136,
        "and The Woman taken in Adultery did pass through the three collections in just this way",
        WOMAN, COLONNA_COLLECTION, "painting_reported_to_have_passed_roomer_van_den_einden_colonna_collections",
        "Haskell says The Woman taken in Adultery by Codazzi, with figures by Micco Spadaro, passed through the Roomer, Van den Einden, and Colonna collections.",
        "This is Haskell’s footnote report, supported there by a De Dominici locator; the cited pages and specific object histories were not independently checked.",
        [WOMAN, CODAZZI, SPADARO, ROOMER_COLLECTION, FERDINAND_COLLECTION, COLONNA_COLLECTION, DE_DOMINICI], N1, 1, "footnote narrative claim",
        {"reported_collection_sequence": [ROOMER_COLLECTION, FERDINAND_COLLECTION, COLONNA_COLLECTION], "relation_candidate": True,
         "citations": [{"source_candidate_id": DE_DOMINICI, "volume": "III", "page_start": "421", "page_end": "422"}]},
    ),
    make_statement(
        "st-chp8-p207-n1-limits-on-other-colonna-provenance", 136,
        "Unfortunately evidence as regards other pictures in the Colonna collection is lacking, and I cannot accept Vaes’s certainty about their provenance.",
        COLONNA_COLLECTION, VAES, "haskell_rejects_vaes_provenance_certainty_for_other_pictures",
        "Haskell says evidence is lacking for other pictures in the Colonna collection and that he cannot accept Vaes’s certainty about their provenance.",
        "Keep this qualification specific to the other pictures; it does not cancel Haskell’s separately qualified account of the two Codazzi works.",
        [COLONNA_COLLECTION, VAES], N1, 1, "footnote narrative claim",
        {"evidence_gap": True},
    ),
    make_statement(
        "st-chp8-p207-n2-cite-de-dominici", 137,
        "2 De Dominici, IV, p. 47.", None, DE_DOMINICI, "footnote_citation",
        "P.207 note 2 cites De Dominici, volume IV, p.47, for the preceding report about picture lovers following Roomer’s advice.",
        "Citation locator only; the cited page was not independently read.",
        [DE_DOMINICI], N2, 2, "bibliographic pointer",
        {"citations": [{"source_candidate_id": DE_DOMINICI, "volume": "IV", "page": "47"}]},
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
        raise SystemExit(f"mention has unknown candidate: {row['mention_id']} -> {row['candidate_id']}")
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
        copied["source_line_ranges"] = "L127-137"
        copied["note"] = (
            "P.204 notes 1-3 (L127-129), p.205 notes 1-4 (L130-133), p.206 notes 1-2 (L134-135), and p.207 notes 1-2 (L136-137) "
            "read against CHP-8.pdf physical pp.2-5 and migrated. The p.207 note reports a tentative provenance chain for many pictures, "
            "but identifies the Pool of Bethesda and Woman taken in Adultery as passing through three collections; keep these scopes distinct. "
            "Ferdinando Colonna pp.29-32 and De Dominici citations are locators only; cited pages were not independently read. "
            "The OCR correction imturn -> in turn is recorded in S2 only. L138-L157 remain pending."
        )
    elif copied["segment_id"] == P207_BODY_ID:
        copied["migration_status"] = "complete"
        copied["note"] = (
            "P.207 body was read against CHP-8.pdf physical p.5. Notes 1-2 in composite lines L136-L137 have been migrated and linked. "
            "The p.207 rhetorical question at L51 is closed by p.208 L54."
        )
    coverage_new.append(copied)


def preview():
    print(f"validated segment: {SEGMENT_ID} lines 126-157")
    print("processed source range: L136-137 (p.207 notes 1-2)")
    print(f"new candidates: {len(new_candidates)}; IDs cand-7593..cand-7598")
    print(f"new mentions: {len(new_mentions)}")
    print(f"new statements: {len(new_statements)}")
    print("p.207 body coverage: reviewed/complete")
    print("composite note coverage: reviewed/partial, L127-137; L138-157 pending")


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
