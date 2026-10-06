"""Controlled S2 migration for chapter 9 printed p.265; defaults to read-only dry run."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l291-301"
NOTE_SEGMENT_ID = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_SEGMENT_SHA = "3820d49b66ee86388bfe238d2257d81f282963238c24fbf01a771e396f41cc83"
EXPECTED_ASSET_SHA = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p265-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_by_id = {r["segment_id"]: r for r in read_jsonl(segment_path)}
segment_meta = segment_by_id.get(SEGMENT_ID)
if not segment_meta or segment_meta.get("sha256") != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.265 S0 segment is missing or has changed")
if segment_meta.get("asset_sha256") != EXPECTED_ASSET_SHA or hashlib.sha256(source_bytes).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("p.265 source asset is missing or has changed")
if "piastra.’6 himself) there are some religious canvases" not in source_lines[294]:
    raise SystemExit("p.265 body or p.264 note 8 continuation changed")
segment_text = "\n".join(source_lines[290:301])

candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_ids = {r["candidate_id"] for r in candidates}
mention_ids = {r["mention_id"] for r in mentions}
statement_ids = {r["statement_id"] for r in statements}
coverage_by_id = {r["segment_id"]: r for r in coverage}

page_cov = coverage_by_id.get(SEGMENT_ID)
if not page_cov or (page_cov["disposition"], page_cov["migration_status"], page_cov["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"unexpected p.265 coverage state: {page_cov}")
notes_cov = coverage_by_id.get(NOTE_SEGMENT_ID)
if not notes_cov or (notes_cov["disposition"], notes_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"unexpected consolidated-notes coverage state: {notes_cov}")

NEW_CANDIDATES = [
    ("cand-8606", "Unidentified ceiling by Giambattista Tiepolo recorded in 1743", "work", "Haskell says a ceiling by Tiepolo was recorded in 1743, but it may have been commissioned after Zaccaria's death; no surviving object or title is identified.", 292),
    ("cand-8607", "Several unidentified drawings by Giambattista Tiepolo recorded in 1743", "work", "Drawings attributed to Tiepolo were recorded in 1743; Haskell says they were almost certainly acquired by Zaccaria, without identifying individual sheets.", 292),
    ("cand-8608", "Tiepolo drawing of Antonio Corradini's Statue of Virginity prepared for Andrea Zucchi", "work", "Haskell says Tiepolo drew the statue for engraver Andrea Zucchi sometime after 1721; the referent of the dedication is kept at the image/print level pending S3.", 293),
    ("cand-8609", "Antonio Corradini's statue of Virginity at S. Maria del Carmelo", "work", "Sculptural work named and located by Haskell; no independent object or attribution verification has been performed.", 294),
    ("cand-8610", "Personification of Virginity represented by Corradini's statue", "term", "Iconographic subject of the statue; it is treated as a represented concept, not as a historical person.", 294),
    ("cand-8611", "Church of S. Maria del Carmelo", "place", "Church named as the location of Corradini's statue; exact modern institutional identity is not normalized at S2.", 294),
    ("cand-8612", "Unidentified Canaletto view owned by Zaccaria Sagredo before the end of 1725", "work", "Haskell reports at least one Canaletto view in Sagredo's possession but supplies no title, date of acquisition, or present location.", 294),
    ("cand-8613", "The Fall of the Giants fresco by Pietro Longhi at Palazzo Sagredo", "work", "Haskell reports the fresco and its 1734 date; the date may indicate completion, and the beginning/commission chronology remains tentative.", 295),
    ("cand-8614", "Palazzo Sagredo, staircase site of The Fall of the Giants", "place", "Building named as the location of Longhi's fresco; it may correspond to the unnamed Sagredo palace at S. Sofia in p.263, but identity is deferred to S3.", 295),
    ("cand-8615", "Unidentified religious canvases by Johann Karl Loth in the Sagredo inventories", "work", "The p.264 note 8 continuation names canvases by Loth among pictures that Haskell says are safe to regard as acquired by Zaccaria; individual objects are not identified.", 295),
    ("cand-8616", "Unidentified portraits by Niccolò Cassana in the Sagredo inventories", "work", "The p.264 note 8 continuation names Cassana portraits among pictures that Haskell says are safe to regard as acquired by Zaccaria; individual objects are not identified.", 295),
    ("cand-8617", "Unidentified old-master pictures acquired by Zaccaria Sagredo", "work", "Haskell says Sagredo bought many old masters that cannot be identified among the collection's hundreds of pictures; no titles or makers are supplied.", 296),
    ("cand-8618", "First inventory of Zaccaria Sagredo's collection (1743; exact record unidentified)", "archive", "Haskell calls the 1743 inventory the first inventory and says many pictures had already been disposed of by then; repository and item title are not supplied.", 296),
    ("cand-8619", "Bologna named as the place from which Giuseppe Maria Crespi wrote in July 1729", "place", "Haskell locates Crespi in Bologna when he wrote to Stefano Conti; keep as a local S2 candidate pending global place alignment.", 295),
    ("cand-8620", "Giuseppe Maria Crespi's letter to Stefano Conti (4 July 1729; Biblioteca Governativa, Lucca, MS 3299)", "archive", "Letter locator and Italian quotation reproduced by Haskell; the manuscript was not independently consulted.", 299),
    ("cand-8621", "Tiepolo and Piazzetta's estimate of the Sagredo collection (record unidentified)", "archive", "Haskell says both painters drew up an estimate and valued the Angelo Custode highly; no document title, date, repository, or surviving item is identified.", 292),
]
for cid, name, *_ in NEW_CANDIDATES:
    if cid in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {cid}")
    if any(c["canonical_name"] == name for c in candidates):
        raise SystemExit(f"candidate natural key already exists: {name}")

new_candidates = []
for cid, name, kind, detail, line_no in NEW_CANDIDATES:
    new_candidates.append({
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
    })

candidate_ids |= {r["candidate_id"] for r in new_candidates}
LINE_OFFSETS = {}
offset = 0
for line_no in range(291, 302):
    LINE_OFFSETS[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

new_mentions = []
def add_mention(mention_id, line_no, candidate_id, surface, note, occurrence=0):
    if mention_id in mention_ids:
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    line = source_lines[line_no - 1]
    starts = []
    cursor = 0
    while True:
        start = line.find(surface, cursor)
        if start < 0:
            break
        starts.append(start)
        cursor = start + 1
    if occurrence >= len(starts):
        raise SystemExit(f"surface occurrence not found on L{line_no}: {surface!r}")
    start = LINE_OFFSETS[line_no] + starts[occurrence]
    row = {
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    }
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"invalid exact-span anchor: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown candidate for mention {mention_id}: {candidate_id}")
    new_mentions.append(row)

def add_mention_span(mention_id, candidate_id, surface, note):
    if mention_id in mention_ids or any(r["mention_id"] == mention_id for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    start = segment_text.find(surface)
    if start < 0:
        raise SystemExit(f"surface span not found in segment: {surface!r}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown candidate for mention {mention_id}: {candidate_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })

add_mention("m-chp9-p265-srocco", 292, "cand-8588", "S. Rocco", "Place named as the site of one annual exhibition; identity of the exact venue is unresolved.")
add_mention("m-chp9-p265-piazzetta-angelo", 292, "cand-1904", "Piazzetta", "Use the index sub-entry for the Angelo Custode; global identity alignment remains deferred.")
add_mention("m-chp9-p265-angelo-custode", 292, "cand-8569", "Angelo Custode", "Work candidate also cited in p.262 and p.263 note 5; this is a second source passage, not a new object.")
add_mention("m-chp9-p265-tiepolo-valuation", 292, "cand-2569", "Tiepolo", "Artist named in the collection valuation account.", 0)
add_mention("m-chp9-p265-piazzetta-valuation", 292, "cand-1901", "Piazzetta", "Artist named in the valuation account; the candidate's broader index entry covers p.265.", 1)
add_mention("m-chp9-p265-zaccaria-contact", 292, "cand-2329", "Zaccaria Sagredo", "Named as the patron whose early contact with Tiepolo is hedged by 'may well'.")
add_mention("m-chp9-p265-tiepolo-contact", 292, "cand-2569", "Tiepolo", "Artist named in the possible early contact statement.", 1)
add_mention("m-chp9-p265-tiepolo-ceiling", 292, "cand-2569", "by him", "Pronoun refers to Tiepolo in the preceding clause and attributes the unidentified ceiling to him.")
add_mention("m-chp9-p265-ceiling-work", 292, "cand-8606", "ceiling", "Unidentified work recorded in 1743; not the separately described mysterious ceiling at L355.")
add_mention("m-chp9-p265-tiepolo-drawings", 293, "cand-2569", "Tiepolo", "Artist attribution reported for several drawings recorded in 1743.")
add_mention("m-chp9-p265-drawings-work", 293, "cand-8607", "drawings", "Unidentified group of several sheets; Haskell says they were almost certainly acquired by Zaccaria.")
add_mention("m-chp9-p265-zucchi", 293, "cand-2886", "Andrea Zucchi", "Engraver named as the recipient of Tiepolo's drawing.")
add_mention("m-chp9-p265-drawing-work", 293, "cand-8608", "Tiepolo drew for the engraver Andrea Zucchi", "Uncaptioned representational work identified by Tiepolo's drawing act for Zucchi; the depicted statue is anchored separately. Preserve the dedication ambiguity.")
add_mention_span("m-chp9-p265-corradini-statue", "cand-8609", "the statue of\nVirginity by the sculptor Antonio Corradini", "Cross-line phrase names Corradini's sculpture; the OCR break falls between 'statue of' and 'Virginity'. It is distinct from Tiepolo's drawing for Zucchi.")
add_mention("m-chp9-p265-virginity-term", 294, "cand-8610", "Virginity", "Represented concept nested in the named statue.")
add_mention("m-chp9-p265-corradini", 294, "cand-0851", "Antonio Corradini", "Use the index sub-entry for Virginity; external identity verification is deferred.")
add_mention("m-chp9-p265-carmelo", 294, "cand-8611", "S. Maria del Carmelo", "Church named as the statue's location; current institutional identity is not asserted.")
add_mention("m-chp9-p265-zaccaria-dedication", 294, "cand-2339", "Zaccaria Sagredo", "Use the index sub-entry for patronage of younger Venetian artists.")
add_mention("m-chp9-p265-sagredo-canaletto", 294, "cand-2330", "Sagredo", "Surname-only reference in the Canaletto patronage sub-entry.")
add_mention("m-chp9-p265-canaletto", 294, "cand-0522", "Canaletto", "Use the index sub-entry 'Z. Sagredo and'.")
add_mention("m-chp9-p265-canaletto-view", 294, "cand-8612", "at least one view by him", "Unidentified work; the pronoun refers to Canaletto in the immediately preceding clause.")
add_mention("m-chp9-p265-longhi", 295, "cand-1431", "Pietro Longhi", "Use the index sub-entry for The Fall of the Giants.")
add_mention("m-chp9-p265-fall-giants", 295, "cand-8613", "The Fall of the Giants", "Fresco named by Haskell; retain the reported date and uncertain commission chronology.")
add_mention("m-chp9-p265-palazzo", 295, "cand-8614", "Palazzo Sagredo", "Building named as fresco location; possible match to the S. Sofia palace remains open for S3.")
add_mention("m-chp9-p265-zaccaria-longhi", 295, "cand-2339", "Zaccaria", "Possible commissioner; the clause is explicitly tentative.")
add_mention("m-chp9-p265-crespi", 295, "cand-0871", "G. M. Crespi", "Indexed person candidate; the passage says he painted two religious works for Sagredo.")
add_mention("m-chp9-p265-crespi-works", 295, "cand-8591", "two religious works", "Group candidate from p.263 note 5; p.265 note 6 later specifies the titles.")
add_mention("m-chp9-p265-bologna", 295, "cand-8619", "Bologna", "Place from which Haskell says Crespi wrote in July 1729; local candidate pending S3.")
add_mention("m-chp9-p265-zaccaria-crespi", 295, "cand-2335", "his patron", "Anaphora to Zaccaria Sagredo; use his p.263 index sub-entry for commissions to Crespi.")
add_mention("m-chp9-p265-loth-canvases", 295, "cand-8615", "religious canvases", "Unidentified group in the p.264 note 8 continuation.")
add_mention("m-chp9-p265-loth", 295, "cand-1442", "Johann Karl Loth", "Use the p.265n index candidate; do not merge with the separate Carlo Loth candidate from chapter 7 at S2.")
add_mention("m-chp9-p265-cassana-portraits", 295, "cand-8616", "portraits", "Unidentified group in the p.264 note 8 continuation; the name continues at the next OCR line.")
add_mention("m-chp9-p265-cassana-first", 295, "cand-0593", "Niccolò", "Name is split by the OCR line break; map the following 'Cassana' token to the same indexed candidate.")
add_mention("m-chp9-p265-cassana-second", 296, "cand-0593", "Cassana", "Second half of the OCR-line-broken name Niccolò Cassana.")
add_mention("m-chp9-p265-zaccaria-note8", 296, "cand-2339", "Zaccaria", "Named in the p.264 note 8 continuation concerning directly acquired pictures.")
add_mention("m-chp9-p265-old-masters", 296, "cand-8617", "many old masters", "Unidentified works that Haskell says cannot be matched to objects among the collection's hundreds of pictures.")
add_mention("m-chp9-p265-first-inventory", 296, "cand-8618", "first inventory", "The 1743 inventory is named but its repository and exact archival identity are not supplied.")
add_mention("m-chp9-p265-detroit", 297, "cand-7072", "Detroit Institute of Arts", "Use the existing Detroit institution candidate; the footnote says only part of the picture is there.")
add_mention("m-chp9-p265-cochin", 297, "cand-0793", "Cochin", "Author of the cited 1758 account as reported by Haskell.")
add_mention("m-chp9-p265-crespi-letter-author", 299, "cand-0871", "Crespi", "Author of the 4 July 1729 letter cited in the footnote.")
add_mention("m-chp9-p265-conti-letter-recipient", 299, "cand-0833", "Stefano Conti", "Recipient named in the Crespi letter locator; use the index entry covering p.265n.")
add_mention("m-chp9-p265-library", 299, "cand-7803", "Biblioteca Governativa", "Repository name is preserved as printed; no present-day institutional name is inferred.")
add_mention("m-chp9-p265-lucca", 299, "cand-3934", "Lucca", "Place in the printed repository locator; reuse the existing accepted place candidate.")
add_mention("m-chp9-p265-letter-archive", 299, "cand-8620", "MSS. 3299", "Manuscript locator for Crespi's letter; the manuscript was not independently consulted.")
add_mention("m-chp9-p265-zachario", 300, "cand-2339", "Zachario Sagredo", "Variant spelling in Crespi's Italian quotation; preserve as a source form without normalizing the OCR/source text.")

def q(line_no, start_text, end_text=None):
    text = source_lines[line_no - 1]
    start = text.index(start_text)
    if end_text is None:
        return text[start:]
    end = text.index(end_text, start) + len(end_text)
    return text[start:end]

purchase_quote = q(292, "Thus at one", "elsewhere.1")
valuation_quote = q(292, "This picture", "aware of its fame.2")
contact_quote = q(292, "Zaccaria Sagredo may well", "recorded in 1743,")
inventory_quote = q(292, "an unidentified ceiling") + "\n" + q(293, "Zaccaria’s death", "Zaccaria’s death, the drawings were almost certainly acquired by him.")
drawing_quote = q(293, "Furthermore, sometime after 1721") + "\n" + q(294, "Virginity by the sculptor", "fine arts’.3")
canaletto_quote = q(294, "Sagredo Was also among", "other clients.4")
longhi_quote = q(295, "It is finally just possible", "Zaccaria himself.5")
collection_quote = q(295, "Certainly the old man", "piastra.’6")
footnote2_quote = source_lines[296]
letter_locator_quote = source_lines[298]
letter_quote = source_lines[299] + "\n" + source_lines[300]
# Consolidated note 8 starts on p.264 L427 and continues as this suffix of p.265 L295 plus L296.
note8_start = source_lines[294].index("himself) there are some religious canvases")
note8_quote = source_lines[294][note8_start:] + "\n" + source_lines[295]

new_statements = []
def add_statement(statement_id, subject, object_, predicate, quote, line_start, line_end, claim, qualification, mentioned, *, speaker="Haskell", text_layer="authorial narrative", relation=False, crossrefs=None, footnote=None):
    if statement_id in statement_ids or any(s["statement_id"] == statement_id for s in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in this segment: {statement_id}")
    refs = set(mentioned)
    if subject:
        refs.add(subject)
    if object_:
        refs.add(object_)
    if not refs <= candidate_ids:
        raise SystemExit(f"statement has missing candidate keys: {statement_id}: {refs - candidate_ids}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 265,
        "pdf_physical_page": 31,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": sorted(refs),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if crossrefs:
        qualifiers["cross_reference_segments"] = crossrefs
    if footnote:
        qualifiers["footnote_marker"] = footnote
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
        "origin": "book",
    })

P263 = {"segment_id": "chp-9:09_CHP-9_intro:l231-238", "source_line_start": 233, "source_line_end": 236}
NOTES_P264 = {"segment_id": NOTE_SEGMENT_ID, "source_line_start": 427, "source_line_end": 427}
NOTES_P263_N5 = {"segment_id": NOTE_SEGMENT_ID, "source_line_start": 418, "source_line_end": 418}

add_statement(
    "st-chp9-p265-sagredo-bought-angelo-custode",
    "cand-2329", "cand-8569", "sagredo_bought_piazzetta_angelo_custode_at_s_rocco_exhibition",
    purchase_quote, 292, 292,
    "Haskell says Zaccaria Sagredo bought Piazzetta's Angelo Custode at one of the annual exhibitions at S. Rocco.",
    "The buyer is identified by continuation from p.263; no year or exact exhibition edition is supplied. This repeats the transaction stated in p.263 note 5 but is a distinct main-text passage.",
    ["cand-2329", "cand-1904", "cand-8569", "cand-8587", "cand-8588"],
    relation=True, crossrefs=[P263, NOTES_P263_N5], footnote=1,
)
add_statement(
    "st-chp9-p265-angelo-prior-disposal-difficulty",
    "cand-8569", "cand-1904", "painter_had_been_unable_to_dispose_of_angelo_custode_elsewhere",
    purchase_quote, 292, 292,
    "Haskell says the painter had been unable to dispose of the Angelo Custode elsewhere before Sagredo bought it.",
    "This preserves the reported sale difficulty and does not infer where, when, or how many prior sales were attempted.",
    ["cand-8569", "cand-1904"], relation=True, footnote=1,
)
add_statement(
    "st-chp9-p265-angelo-valuation-and-reputation",
    "cand-8569", "cand-8621", "tiepolo_and_piazzetta_valued_angelo_custode_highly_in_collection_estimate",
    valuation_quote, 292, 292,
    "Haskell says the picture was Sagredo's most important modern acquisition and that Tiepolo and Piazzetta valued it highly when drawing up an estimate of the collection; Venetian and foreign visitors knew its fame.",
    "The importance and fame are Haskell's characterization; no estimate document or valuation amount is supplied here.",
    ["cand-8569", "cand-2569", "cand-1901", "cand-8621"], relation=True, crossrefs=[NOTES_P263_N5], footnote=2,
)
add_statement(
    "st-chp9-p265-possible-sagredo-tiepolo-contact",
    "cand-2329", "cand-2569", "sagredo_may_have_been_in_touch_with_tiepolo_early_in_his_career",
    contact_quote, 292, 292,
    "Haskell says Zaccaria Sagredo may well have been in touch with Tiepolo early in the artist's career.",
    "Preserve 'may well'; the passage does not document a specific meeting or communication.",
    ["cand-2329", "cand-2569"], relation=True,
)
add_statement(
    "st-chp9-p265-tiepolo-works-recorded-in-1743",
    "cand-8618", None, "1743_sagredo_record_lists_tiepolo_ceiling_and_drawings",
    inventory_quote, 292, 293,
    "Haskell says an unidentified ceiling by Tiepolo and several drawings were recorded in 1743.",
    "The exact inventory record and repository are not identified; the ceiling and the drawings remain separate candidate objects.",
    ["cand-8618", "cand-2569", "cand-8606", "cand-8607"],
    crossrefs=[NOTES_P264],
)
add_statement(
    "st-chp9-p265-tiepolo-ceiling-possibly-posthumous",
    "cand-8606", "cand-2329", "tiepolo_ceiling_may_have_been_commissioned_after_sagredos_death",
    inventory_quote, 292, 293,
    "Haskell says the unidentified Tiepolo ceiling recorded in 1743 may have been commissioned after Zaccaria's death.",
    "This is expressly uncertain and does not establish Zaccaria as commissioner.",
    ["cand-8606", "cand-2569", "cand-2329", "cand-8618"], relation=True,
)
add_statement(
    "st-chp9-p265-tiepolo-drawings-probably-acquired-by-sagredo",
    "cand-8607", "cand-2329", "tiepolo_drawings_were_almost_certainly_acquired_by_sagredo",
    inventory_quote, 292, 293,
    "Haskell says the Tiepolo drawings recorded in 1743 were almost certainly acquired by Zaccaria Sagredo.",
    "The source's 'almost certainly' is retained; individual drawings and acquisition dates are not identified.",
    ["cand-8607", "cand-2569", "cand-2329", "cand-8618"], relation=True,
)
add_statement(
    "st-chp9-p265-tiepolo-drew-virginity-for-zucchi",
    "cand-8608", "cand-2886", "tiepolo_drew_corradini_virginity_image_for_zucchi_after_1721",
    drawing_quote, 293, 294,
    "Haskell says that sometime after 1721 Tiepolo drew the statue of Virginity by Antonio Corradini for engraver Andrea Zucchi.",
    "The passage describes Tiepolo's drawing for an engraver; it does not say that Tiepolo made the statue.",
    ["cand-8608", "cand-2569", "cand-2886", "cand-8609", "cand-8610", "cand-0851", "cand-8611"], relation=True, footnote=3,
)
add_statement(
    "st-chp9-p265-zucchi-dedication-to-sagredo",
    None, "cand-2339", "dedication_to_zaccaria_reported_after_tiepolo_zucchi_statue_image_passage",
    drawing_quote, 293, 294,
    "Haskell quotes a dedication praising Zaccaria Sagredo for promoting the fine arts immediately after the passage on Tiepolo drawing Corradini's statue for Zucchi.",
    "The antecedent of 'this' is ambiguous. Consolidated note 3 at L430 identifies print 428 in Raccolta Gherro, vol. 3, as dedicated to Zaccaria; its separate print candidate and exact relation will be captured with that note. Do not attach the dedication to Corradini's sculpture or Tiepolo's preparatory drawing.",
    ["cand-8608", "cand-2339", "cand-2886", "cand-2569"], relation=True,
    crossrefs=[{"segment_id": NOTE_SEGMENT_ID, "source_line_start": 430, "source_line_end": 430}], footnote=3,
)
add_statement(
    "st-chp9-p265-canalletto-patronage-and-view",
    "cand-2330", "cand-0522", "sagredo_was_among_canalettos_earliest_patrons_and_owned_a_view_by_1725",
    canaletto_quote, 294, 294,
    "Haskell says Sagredo was among Canaletto's very first patrons and owned at least one Canaletto view before the end of 1725.",
    "The view is not titled and the passage does not give an exact acquisition date.",
    ["cand-2330", "cand-0522", "cand-8612"], relation=True, crossrefs=[P263], footnote=4,
)
add_statement(
    "st-chp9-p265-sagredo-commented-on-canaletto-clients",
    "cand-2330", "cand-0522", "sagredo_commented_on_pictures_canaletto_painted_for_other_clients",
    canaletto_quote, 294, 294,
    "Haskell says Sagredo was interested enough in Canaletto's career to comment on pictures painted for other clients.",
    "No particular client, work, or recorded comment is identified in this passage.",
    ["cand-2330", "cand-0522"], relation=True, footnote=4,
)
add_statement(
    "st-chp9-p265-longhi-fall-of-giants-location-and-date",
    "cand-8613", "cand-8614", "longhi_fall_of_the_giants_fresco_at_palazzo_sagredo_dated_1734",
    longhi_quote, 295, 295,
    "Haskell says Pietro Longhi dated The Fall of the Giants fresco 1734 and located it on the staircase of Palazzo Sagredo.",
    "The source calls the fresco clumsy; that evaluation is Haskell's. The relation to the named palace is a reported location, not an independently verified present location.",
    ["cand-1431", "cand-8613", "cand-8614"], relation=True, footnote=5,
)
add_statement(
    "st-chp9-p265-longhi-date-may-mark-completion",
    "cand-8613", None, "longhi_1734_date_may_mark_completion_not_start",
    longhi_quote, 295, 295,
    "Haskell argues that 1734 must refer to completion of The Fall of the Giants rather than the start of the work.",
    "This is Haskell's interpretation of the inscription/date, not a separately documented completion record.",
    ["cand-8613", "cand-1431"],
)
add_statement(
    "st-chp9-p265-zaccaria-possible-longhi-commission",
    "cand-2329", "cand-8613", "fall_of_the_giants_may_have_been_commissioned_by_zaccaria",
    longhi_quote, 295, 295,
    "Haskell considers it possible that Longhi began The Fall of the Giants much earlier and that the commission came from Zaccaria Sagredo.",
    "The argument is inferential and expressly tentative; do not treat Sagredo's commission as certain.",
    ["cand-2329", "cand-1431", "cand-8613", "cand-8614"], relation=True, crossrefs=[P263], footnote=5,
)
add_statement(
    "st-chp9-p265-sagredo-collected-until-end-of-life",
    "cand-2329", None, "sagredo_continued_collecting_until_near_death",
    collection_quote, 295, 295,
    "Haskell says Zaccaria continued collecting until the very end of his life.",
    "Authorial summary; no final acquisition or exact date is given.",
    ["cand-2329"],
)
add_statement(
    "st-chp9-p265-crespi-painted-two-religious-works-for-sagredo",
    "cand-8591", "cand-2335", "crespi_painted_two_religious_works_for_sagredo",
    collection_quote, 295, 295,
    "Haskell says Giuseppe Maria Crespi painted two religious works for Zaccaria Sagredo.",
    "The works are not named in this sentence; p.265 note 6 supplies further identification, to be migrated from the consolidated notes segment.",
    ["cand-8591", "cand-0871", "cand-2335"], relation=True, crossrefs=[NOTES_P263_N5], footnote=6,
)
add_statement(
    "st-chp9-p265-crespi-reported-dealers-hastened-sagredo-death",
    "cand-2339", "cand-0871", "crespi_said_dealers_tricks_hastened_sagredos_death_and_reported_large_spending",
    collection_quote, 295, 295,
    "Haskell reports that Crespi, writing from Bologna in July 1729, said dealers' tricks had hastened Sagredo's death and quoted him describing seven to eight thousand zecchini spent on pictures and drawings, most of low value.",
    "This is Haskell's report of Crespi's letter, not a direct reading of the letter. Retain the approximate amount and the nested quotation attribution.",
    ["cand-2339", "cand-0871", "cand-8619", "cand-8591"], relation=True, footnote=6,
)
add_statement(
    "st-chp9-p265-angelo-part-now-detroit",
    "cand-8569", "cand-7072", "part_of_angelo_custode_now_at_detroit_institute_of_arts",
    footnote2_quote, 297, 297,
    "Haskell's p.265 note 2 says part of the Angelo Custode is now in the Detroit Institute of Arts.",
    "Only a part is located there; this does not establish that the complete work is at the museum. The note points to Haskell and Levey 1958, p.182, whose article is not independently consulted.",
    ["cand-8569", "cand-7072", "cand-0793", "cand-8580"], relation=True, crossrefs=[{"segment_id": NOTE_SEGMENT_ID, "source_line_start": 429, "source_line_end": 429}], footnote=2,
)
add_statement(
    "st-chp9-p265-cochin-called-angelo-tableau-fort-beau",
    "cand-8580", "cand-8569", "cochin_called_angelo_custode_tableau_fort_beau_in_1758_account",
    footnote2_quote, 297, 297,
    "Haskell says Cochin's 1758 account of pictures in the Sagredo palace described the Angelo Custode as a 'tableau fort beau'.",
    "A nested source report: Cochin's account is cited at vol. III, p.150 but was not independently consulted.",
    ["cand-0793", "cand-8580", "cand-8569", "cand-2329"], relation=True, footnote=2,
)
add_statement(
    "st-chp9-p265-note8-loth-and-cassana-in-directly-acquired-set",
    "cand-8615", "cand-2339", "some_loth_canvases_and_cassana_portraits_among_pictures_sagredo_directly_acquired",
    note8_quote, 295, 296,
    "Haskell's p.264 note 8 says the paintings must date from 1685-1729 and names religious canvases by Johann Karl Loth and portraits by Niccolò Cassana among the few pictures safe to assume Zaccaria acquired directly.",
    "The 1685-1729 range is Haskell's inference about date of painting, not an inventory date or independently verified chronology. Neither set is individually identified; do not merge Johann Karl Loth with the separate Carlo Loth candidate at S2.",
    ["cand-8615", "cand-8616", "cand-1442", "cand-0593", "cand-2339"], relation=True, crossrefs=[NOTES_P264], speaker="Haskell's footnote", text_layer="footnote continuation",
)
add_statement(
    "st-chp9-p265-note8-assessment-and-collection-dispersal",
    "cand-8617", "cand-2339", "sagredo_bought_unidentified_old_masters_and_many_were_disposed_by_1743",
    note8_quote, 295, 296,
    "Haskell says Sagredo bought many old masters that cannot be identified among the collection's hundreds of pictures, and that many pictures had already been disposed of by the first inventory in 1743.",
    "Haskell presents the purchases and dispersal as certain at collection level, but no item-level identity, disposal date, or recipient is named.",
    ["cand-8617", "cand-8618", "cand-2339"], relation=True, crossrefs=[NOTES_P264], speaker="Haskell's footnote", text_layer="footnote continuation",
)
add_statement(
    "st-chp9-p265-crespi-letter-locator",
    "cand-8620", "cand-7803", "crespi_letter_to_conti_dated_1729_07_04_in_lucca_ms3299",
    letter_locator_quote, 299, 299,
    "Haskell identifies a 4 July 1729 letter from Giuseppe Maria Crespi to Stefano Conti at Biblioteca Governativa, Lucca, MS 3299.",
    "The letter is cited as evidence for the p.265 report; repository and manuscript have not been independently checked.",
    ["cand-8620", "cand-0871", "cand-0833", "cand-7803", "cand-3934"], relation=True,
)
add_statement(
    "st-chp9-p265-crespi-letter-italian-quotation",
    "cand-8620", "cand-2339", "crespi_letter_says_dealers_accelerated_sagredo_death_and_reports_picture_spending",
    letter_quote, 300, 301,
    "In the Italian passage reproduced by Haskell, Crespi says that if Zaccaria had acted as repeatedly requested, the many deceptions would not have hastened his death; he reports that Sagredo died days earlier after spending between seven and eight thousand zecchini on pictures and drawings, most worth less than a piastra.",
    "This is a transcription of the quotation as printed in Haskell, not an independent reading of Biblioteca Governativa MS 3299. Preserve the source's spelling and monetary wording.",
    ["cand-8620", "cand-0871", "cand-0833", "cand-2339"], relation=True, speaker="Crespi, quoted in Haskell", text_layer="nested archival quotation",
)

for row in new_statements:
    qrow = row["qualifiers"]
    if qrow["source_line_start"] < 291 or qrow["source_line_end"] > 301:
        raise SystemExit(f"statement line anchor outside segment: {row['statement_id']}")

for mention in new_mentions:
    mention_ids.add(mention["mention_id"])
statements_ids_added = [r["statement_id"] for r in new_statements]

page_cov.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L291-301",
    "note": "Printed p.265 body, note 2, Crespi letter locator/quotation, and p.264 note 8 continuation at L295-296 reviewed against CHP-9.pdf physical p.31. The latter closes the p.264 note 8 partial. Note 3's dedication quote at L298 overlaps its locator/quotation in consolidated note L430; the dedication claim is recorded once, with the full citation pending note-segment migration. Other p.265 note references continue in L429-432. S0 OCR remains unchanged; page image corrections and attribution limits are recorded in S2.",
})
notes_cov.update({
    "source_line_ranges": "L349-427; p.255 L155 continuation; p.263 note 6 continues at p.264 L245-248; p.264 note 8 continuation at p.265 L295-296 complete",
    "note": "Consolidated notes through p.264 notes 1-8 migrated at L414-427. P.263 note 6 continues at p.264 OCR L245-248. P.264 note 8 continued at p.265 OCR L295-296 and is now closed. L428 repeats the Plate 46 heading; later p.265+ consolidated notes L429-445 remain pending.",
})

summary = {
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "segment": SEGMENT_ID,
    "closed_partial_note": "p.264 note 8 at p.265 L295-296",
    "duplicate_footnote_text": "p.265 L298 overlaps consolidated note 3 at L430; record the dedication claim once and migrate the full citation at L430",
    "next_segment": "chp-9:09_CHP-9_intro:l303-311 (printed p.266)",
    "counts": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements),
        "coverage_rows": len(coverage),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    try:
        write_csv(candidate_path, candidate_fields, candidates + new_candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
