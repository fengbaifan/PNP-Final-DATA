"""Controlled S2 migration for Chapter 8 printed page 222 and notes 1-5."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
BACKUP_SUFFIX = ".bak-s2-chp8-p222-20261001"

P221 = "chp-8:08_CHP-8_sec_ii:l112-124"
P222 = "chp-8:08_CHP-8_sec_ii:l126-138"
P223 = "chp-8:08_CHP-8_sec_ii:l140-150"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P221, P222, P223, NOTES}


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
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or not TARGET_IDS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_texts = {}
line_offsets = {}
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    lines = source_lines[meta["line_start"] - 1:meta["line_end"]]
    text = "\n".join(lines)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    segment_texts[segment_id] = text
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), lines):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(line) + 1

candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
mention_fields, mention_rows = read_csv(MENTION_PATH)
statement_rows = read_jsonl(STATEMENT_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

expected_coverage = {
    P221: ("reviewed", "partial", "L113-124"),
    P222: ("queued", "pending", ""),
}
for sid, expected in expected_coverage.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-381":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P222 for row in mention_rows + statement_rows):
    raise SystemExit("p.222 rows already exist; inspect before rerunning")
if any(row["segment_id"] == NOTES and row["qualifiers"].get("source_line_start") in {382, 383, 384, 385}
       for row in statement_rows):
    raise SystemExit("p.222 footnote rows already exist; inspect before rerunning")

new_candidates = [
    {"candidate_id": "cand-7704", "index_entry_id": "", "canonical_name": "Rich stucco decoration with papal medallions on the Ferrara Archbishop's Palace staircase",
     "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Haskell reports that Andrea Ferrerio designed this staircase-wall decoration, including medallions of six popes. Keep it distinct from the staircase and from Vittorio Bigari's ceiling fresco.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P222}#L127-128"},
    {"candidate_id": "cand-7705", "index_entry_id": "", "canonical_name": "Four unidentified paintings by Giovanni Benedetto Castiglione in Cardinal Tommaso Ruffo's collection, as described by John Breval",
     "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Breval calls these four of the most capital Castigliones he remembered seeing. The individual titles, subjects, and exact attribution are not supplied.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P222}#L133"},
    {"candidate_id": "cand-7706", "index_entry_id": "", "canonical_name": "Unidentified original painting of the Neapolitan chief of the mutineers called Masanella [sic] by Breval",
     "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Breval's quoted description calls it a fine original of the chief of the mutineers and prints Masanella [sic]. Artist, medium, and exact object identity are not given; do not normalize the quoted spelling at S2.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P222}#L133"},
    {"candidate_id": "cand-7707", "index_entry_id": "", "canonical_name": "Four works by Giuseppe Maria Crespi in Cardinal Tommaso Ruffo's collection, two identified on p.222",
     "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Haskell says Crespi was represented by four works and names two commissioned during Ruffo's Ferrara legateship. This group preserves the reported count; do not merge the two named paintings with the separate index candidate cand-0879 without S3 review.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P222}#L134-135"},
    {"candidate_id": "cand-7708", "index_entry_id": "", "canonical_name": "Catholic Religion as an allegorical subject in Vittorio Bigari's Ferrara ceiling fresco",
     "index_page_range": "", "suggested_type": "term", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "The source says the Catholic Religion is represented by the Papacy in the fresco; retain the allegorical concept as a term, distinct from the Papacy as an institution.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P222}#L129"},
    {"candidate_id": "cand-7709", "index_entry_id": "", "canonical_name": "J. Agnelli (author associated with the 1734 Ruffo gallery publication)",
     "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "P.222 n.2 gives only the initial J.; the bibliography identifies a 1734 Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara. Do not expand the author's forename without evidence.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{NOTES}#L383"},
    {"candidate_id": "cand-7710", "index_entry_id": "", "canonical_name": "Girolamo Baruffaldi",
     "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Named in the title of the manuscript cited by Haskell as the description of Cardinal Ruffo's Ferrara palace and gallery.",
     "exclude_reason": "", "candidate_origin": "footnote-report", "candidate_source_ref": f"{NOTES}#L382"},
    {"candidate_id": "cand-7711", "index_entry_id": "", "canonical_name": "Collezione Antonelli MS. 610, Galleria di Pitture raccolte ed esposte nel Palazzo Vescovale di Ferrara (Girolamo Baruffaldi)",
     "index_page_range": "", "suggested_type": "archive", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Haskell identifies this manuscript in Biblioteca Ariostea, Ferrara, as the source for his account of Ruffo's palace. Its contents were not independently consulted; the title spelling is transcribed from the page image.",
     "exclude_reason": "", "candidate_origin": "footnote-report", "candidate_source_ref": f"{NOTES}#L382"},
    {"candidate_id": "cand-7712", "index_entry_id": "", "canonical_name": "Biblioteca Ariostea, Ferrara",
     "index_page_range": "", "suggested_type": "institution", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Named by Haskell as the repository of Collezione Antonelli MS. 610; this is a source-reported archival location, not a current catalogue check.",
     "exclude_reason": "", "candidate_origin": "footnote-report", "candidate_source_ref": f"{NOTES}#L382"},
    {"candidate_id": "cand-7713", "index_entry_id": "", "canonical_name": "Remarks on several parts of Europe relating chiefly to their antiquities and history (John Breval, 1738)",
     "index_page_range": "", "suggested_type": "archive", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Cited at p.222 n.3, volume I, p.193. The title and edition are identified from this book's bibliography; the cited page was not independently read.",
     "exclude_reason": "", "candidate_origin": "footnote-citation", "candidate_source_ref": f"{NOTES}#L384"},
    {"candidate_id": "cand-7714", "index_entry_id": "", "canonical_name": "Sir William Hamilton (collector named in the p.222 note about the Juan de Pareja portrait)",
     "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Haskell's note says the Juan de Pareja portrait was in Hamilton's collection in Naples by 1798. The note does not give further identifying detail.",
     "exclude_reason": "", "candidate_origin": "footnote-report", "candidate_source_ref": f"{P222}#L138"},
    {"candidate_id": "cand-7715", "index_entry_id": "", "canonical_name": "Museo di Palazzo Venezia, Rome",
     "index_page_range": "", "suggested_type": "institution", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "P.222 n.5 names this museum as the reported location of two Crespi paintings; do not conflate the collection institution with Palazzo Venezia as a building.",
     "exclude_reason": "", "candidate_origin": "footnote-report", "candidate_source_ref": f"{NOTES}#L385"},
    {"candidate_id": "cand-7716", "index_entry_id": "", "canonical_name": "Luigi Crespi (author cited as L. Crespi)",
     "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "The bibliography identifies the cited L. Crespi publication as Luigi Crespi's Vite de' Pittori bolognesi. Keep this author separate from painter Giuseppe Maria Crespi.",
     "exclude_reason": "", "candidate_origin": "footnote-citation", "candidate_source_ref": f"{NOTES}#L385"},
    {"candidate_id": "cand-7717", "index_entry_id": "", "canonical_name": "A. Santangelo (author of the Museo di Palazzo Venezia catalogue)",
     "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "The cited catalogue's author is given only as A. Santangelo; preserve the initial without expanding it.",
     "exclude_reason": "", "candidate_origin": "footnote-citation", "candidate_source_ref": f"{NOTES}#L385"},
    {"candidate_id": "cand-7718", "index_entry_id": "", "canonical_name": "Museo di Palazzo Venezia-Catalogo, 1—I dipinti (A. Santangelo, Rome, 1947)",
     "index_page_range": "", "suggested_type": "archive", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Cited at p.222 n.5, pp.2 and 23. Bibliographic identity is from this book's bibliography; neither the catalogue nor the cited pages were independently consulted.",
     "exclude_reason": "", "candidate_origin": "footnote-citation", "candidate_source_ref": f"{NOTES}#L385"},
    {"candidate_id": "cand-7719", "index_entry_id": "", "canonical_name": "Abigail giving Presents to David (painting by Giuseppe Maria Crespi cited on p.222)",
     "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Named by Haskell as one of two religious paintings commissioned by Cardinal Tommaso Ruffo during his Ferrara legateship. Keep distinct from other Crespi works unless S3 establishes identity.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P222}#L134-135"},
    {"candidate_id": "cand-7720", "index_entry_id": "", "canonical_name": "The Finding of Moses (painting by Giuseppe Maria Crespi cited on p.222)",
     "index_page_range": "", "suggested_type": "work", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "Named by Haskell as one of two religious paintings commissioned by Cardinal Tommaso Ruffo during his Ferrara legateship. Keep distinct from index candidate cand-0879 until S3 resolves whether the later Crespi index subentry is the same object.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P222}#L134-135"},
    {"candidate_id": "cand-7721", "index_entry_id": "", "canonical_name": "Abigail (person named in the title of Crespi's painting cited on p.222)",
     "index_page_range": "", "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
     "detail": "The source names Abigail as the figure receiving presents from David. Preserve the source-level identification without adding biographical details.",
     "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": f"{P222}#L135"},
]

candidate_source_lines = {
    "cand-7704": (P222, 127), "cand-7705": (P222, 133), "cand-7706": (P222, 133),
    "cand-7707": (P222, 134), "cand-7708": (P222, 129), "cand-7709": (NOTES, 383),
    "cand-7710": (NOTES, 382), "cand-7711": (NOTES, 382), "cand-7712": (NOTES, 382),
    "cand-7713": (NOTES, 384), "cand-7714": (P222, 138), "cand-7715": (NOTES, 385),
    "cand-7716": (NOTES, 385), "cand-7717": (NOTES, 385), "cand-7718": (NOTES, 385),
    "cand-7719": (P222, 135), "cand-7720": (P222, 135), "cand-7721": (P222, 135),
}
for row in new_candidates:
    segment_id, line_number = candidate_source_lines[row["candidate_id"]]
    row["candidate_origin"] = "body-mention"
    row["candidate_source_ref"] = f"{segment_id}#L{line_number}"

candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
candidate_ids = set(candidate_by_id)
new_candidate_ids = [row["candidate_id"] for row in new_candidates]
if len(set(new_candidate_ids)) != len(new_candidate_ids) or candidate_ids.intersection(new_candidate_ids):
    raise SystemExit("duplicate candidate IDs")
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 7703:
    raise SystemExit("candidate sequence changed; allocate IDs from current table")
candidate_ids.update(new_candidate_ids)
natural_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows if not row["index_entry_id"]}
for row in new_candidates:
    key = (row["canonical_name"], row["suggested_type"])
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {key}")
    natural_keys.add(key)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, source_line, mention_id, candidate_id, surface, note, occurrence=0):
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    text = segment_texts[segment_id]
    line_offset = line_offsets[(segment_id, source_line)]
    starts = []
    at = line_offset
    while True:
        found = text.find(surface, at)
        if found < 0:
            break
        starts.append(found)
        at = found + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention surface not found at/after L{source_line}: {surface!r} #{occurrence}; count={len(starts)}")
    start = starts[occurrence]
    key = (segment_id, str(start), str(start + len(surface)))
    if key in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == key for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
    })


# Page 222 body, lines 127-135.
mention(P222, 127, "m-chp8-p222-mazza", "cand-1602", "Giuseppe Mazza", "Bolognese sculptor identified in the index.")
mention(P222, 127, "m-chp8-p222-same-artist", "cand-1024", "The same artist", "Coreference to Andrea Ferrerio from p.221; he designed the stucco decoration.")
mention(P222, 127, "m-chp8-p222-staircase-stucco", "cand-7704", "rich stucco decoration", "Work on the staircase wall, distinct from the staircase space.")
mention(P222, 127, "m-chp8-p222-city-ferrara-1", "cand-1017", "City of Ferrara", "City whose legate is mentioned with the papal medallions.")
mention(P222, 127, "m-chp8-p222-legat-ruffo", "cand-2304", "her Legate", "Cardinal Ruffo in his legatine role; source does not name him in this phrase.")
mention(P222, 127, "m-chp8-p222-innocent-xii", "cand-1929", "Innocent\nXII", "Pope named as Ruffo's patron; printed name breaks across lines.")
mention(P222, 128, "m-chp8-p222-ruffo-patron", "cand-2304", "Russo", "OCR spelling; page image reads Ruffo.")
mention(P222, 128, "m-chp8-p222-clement-xi", "cand-0022", "Clement XL", "OCR spelling; page image reads Clement XI.")
mention(P222, 129, "m-chp8-p222-bigari", "cand-0374", "Vittorio Bigari", "Bolognese painter named in the page text and index.")
mention(P222, 129, "m-chp8-p222-catholic-religion", "cand-7708", "Catholic Religion", "Allegorical subject named in the fresco description.")
mention(P222, 129, "m-chp8-p222-papacy", "cand-4223", "the Papacy", "Institution represented in the allegory; distinct from the Catholic Religion concept.")
mention(P222, 129, "m-chp8-p222-ravenna", "cand-7697", "Ravenna", "City represented in the fresco and named as a place of Ruffo's service.")
mention(P222, 129, "m-chp8-p222-bologna-fresco", "cand-3398", "Bologna", "City represented in the fresco and named as a place of Ruffo's service.")
mention(P222, 129, "m-chp8-p222-ferrara-2", "cand-1017", "Ferrara", "City represented in the fresco and named as a place of Ruffo's service.")
mention(P222, 130, "m-chp8-p222-ruffo-1", "cand-2304", "Russo", "OCR spelling; page image reads Ruffo.", occurrence=0)
mention(P222, 130, "m-chp8-p222-ruffo-2", "cand-2304", "Russo", "OCR spelling; page image reads Ruffo.", occurrence=1)
mention(P222, 130, "m-chp8-p222-cardinal", "cand-2304", "the Cardinal", "Coreference to Cardinal Tommaso Ruffo.")
mention(P222, 130, "m-chp8-p222-architect", "cand-1580", "his architect", "Tommaso Mattei, the architect named on p.221.")
mention(P222, 130, "m-chp8-p222-sculptor", "cand-1024", "sculptor", "Andrea Ferrerio, the sculptor named on p.221.")
mention(P222, 130, "m-chp8-p222-collection", "cand-2307", "collection of paintings", "Cardinal Ruffo's Ferrara gallery collection.")
mention(P222, 131, "m-chp8-p222-ruffo-3", "cand-2304", "Russo", "OCR spelling; page image reads Ruffo.")
mention(P222, 131, "m-chp8-p222-giorgione", "cand-1188", "Giorgione", "Artist named among works attributed in Ruffo's collection.")
mention(P222, 131, "m-chp8-p222-titian", "cand-2630", "Titian", "Artist named among works attributed in Ruffo's collection.")
mention(P222, 131, "m-chp8-p222-bassano", "cand-0257", "Bassano", "Index candidate for Jacopo Bassano; source uses the surname only.")
mention(P222, 131, "m-chp8-p222-correggio", "cand-0852", "Correggio", "Artist named among works attributed in Ruffo's collection.")
mention(P222, 131, "m-chp8-p222-raphael", "cand-2098", "Raphael", "Artist named among works attributed in Ruffo's collection.")
mention(P222, 132, "m-chp8-p222-parmigianino", "cand-1839", "Parmigianino", "Artist named among works attributed in Ruffo's collection.")
mention(P222, 132, "m-chp8-p222-caravaggio", "cand-0544", "Caravaggio", "Artist named among works attributed in Ruffo's collection.")
mention(P222, 132, "m-chp8-p222-carracci-collective", "cand-4318", "the Carracci", "Collective reference; do not assign the group to Annibale alone.")
mention(P222, 132, "m-chp8-p222-guido-reni", "cand-2124", "Guido Reni", "Artist named among works attributed in Ruffo's collection.")
mention(P222, 132, "m-chp8-p222-guercino", "cand-1258", "Guercino", "Artist named among works attributed in Ruffo's collection.")
mention(P222, 132, "m-chp8-p222-rubens", "cand-2293", "Rubens", "Artist named among works in Ruffo's collection.")
mention(P222, 132, "m-chp8-p222-van-dyck", "cand-2155", "Van Dyck", "Artist named among works in Ruffo's collection.")
mention(P222, 132, "m-chp8-p222-breval", "cand-0451", "John Breval", "Visitor whose remarks are quoted by Haskell.")
mention(P222, 133, "m-chp8-p222-ferrara-visit", "cand-1017", "Ferrara", "City Breval visited according to Haskell.")
mention(P222, 133, "m-chp8-p222-castiglione-painter", "cand-0602", "Castigliones", "Artist surname in Breval's report of four paintings.")
mention(P222, 133, "m-chp8-p222-four-castigliones", "cand-7705", "four of the most capital Castigliones", "Group of four paintings in Breval's quoted assessment.")
mention(P222, 133, "m-chp8-p222-lucretia-work", "cand-0579", "Lucretia", "Work subentry under Annibale Carracci in the index.")
mention(P222, 133, "m-chp8-p222-annibale-carracci", "cand-0576", "Hannibal Carache", "Quoted English form for Annibale Carracci; retain the printed source form.")
mention(P222, 133, "m-chp8-p222-masanella-work", "cand-7706", "Original of the famous Neapolitan Chief of the Mutineers, Masanella", "Painting described by Breval; artist and object identity remain unspecified.")
mention(P222, 133, "m-chp8-p222-masanella-person", "cand-4150", "Masanella", "Quoted [sic] spelling for the Neapolitan chief; retain as a source form pending identity alignment.")
mention(P222, 133, "m-chp8-p222-ruffo-4", "cand-2304", "Russo", "OCR spelling; page image reads Ruffo.")
mention(P222, 133, "m-chp8-p222-velasquez", "cand-2709", "Velasquez", "Painter named in the portrait attribution.")
mention(P222, 133, "m-chp8-p222-juan-de-pareja", "cand-1834", "Juan de Pareja", "Sitter and Velasquez's servant named in the text.")
mention(P222, 133, "m-chp8-p222-rome", "cand-4490", "Rome", "City of the 1704 exhibition.")
mention(P222, 134, "m-chp8-p222-bologna-modern", "cand-3398", "Bologna", "City from which most of Ruffo's modern pictures came.")
mention(P222, 134, "m-chp8-p222-crespi", "cand-0871", "Crespi", "Index candidate Giuseppe Maria Crespi; full name is not supplied in the body here.")
mention(P222, 134, "m-chp8-p222-ruffo-5", "cand-2304", "Russo", "OCR spelling; page image reads Ruffo.")
mention(P222, 135, "m-chp8-p222-abigail-work", "cand-7719", "Abigail giving Presenti to David", "Named Crespi painting; OCR Presenti is corrected to Presents in the page image.")
mention(P222, 135, "m-chp8-p222-abigail-person", "cand-7721", "Abigail", "Person named in the title of the Crespi painting.")
mention(P222, 135, "m-chp8-p222-david-person", "cand-4268", "David", "Biblical figure named in the painting title.")
mention(P222, 135, "m-chp8-p222-finding-moses-work", "cand-7720", "The Finding of Moses", "Named Crespi painting; kept separate from index candidate cand-0879 pending S3.")
mention(P222, 135, "m-chp8-p222-moses-person", "cand-4144", "Moses", "Figure named in the painting title.")
mention(P222, 135, "m-chp8-p222-donato-creti", "cand-0889", "Donato Creti", "Artist compared with Crespi in Haskell's account.")
mention(P222, 135, "m-chp8-p222-ruffo-6", "cand-2304", "Russo", "OCR spelling; page image reads Ruffo.", occurrence=0)
mention(P222, 135, "m-chp8-p222-creti-reference", "cand-0889", "this painter", "Coreference to Donato Creti; the sentence continues on p.223.")

# Page 222 footnote 4 is transcribed in the source section lines 136-138.
mention(P222, 136, "m-chp8-p222-note4-portrait-title", "cand-2714", "11 Ritratto da tre palmi rappresentante un servo che Ri serv.re del S.r Diego Velasquez famoso pitt.re e cosa stupenda", "Inventory wording for the Juan de Pareja portrait; OCR 11 is corrected to printed Il in the page-image record.")
mention(P222, 136, "m-chp8-p222-note4-velasquez", "cand-2709", "Diego Velasquez", "Painter named in the quoted inventory wording.")
mention(P222, 136, "m-chp8-p222-note4-exhibition", "cand-6051", "exhibition in S. Salvatore in Lauro", "The 1704 exhibition identified by the note; recurring exhibition candidate from the index/body.")
mention(P222, 136, "m-chp8-p222-note4-salvatore", "cand-6052", "S. Salvatore in Lauro", "Church/building named as the exhibition venue.")
mention(P222, 137, "m-chp8-p222-note4-naples", "cand-1722", "Naples", "City attached to Hamilton's collection in the note.")
mention(P222, 137, "m-chp8-p222-note4-museum", "cand-7472", "Metropolitan Museum", "Museum identified as the reported present location in Haskell's source-time account.")
mention(P222, 137, "m-chp8-p222-note4-hamilton", "cand-7714", "Sir\nWilliam Hamilton", "Collector named in the note; name breaks across source lines.")

# Page 222 notes 1-3 and 5 in the consolidated footnote segment.
mention(NOTES, 382, "m-chp8-p222-n1-ariostea", "cand-7712", "Biblioteca Ariostea", "Repository of the manuscript as reported by Haskell.")
mention(NOTES, 382, "m-chp8-p222-n1-ferrara", "cand-1017", "Ferrara", "City where the manuscript is held and where the palace stands.", occurrence=0)
mention(NOTES, 382, "m-chp8-p222-n1-ms610", "cand-7711", "Collezione Antonelli MS. 610", "Manuscript identified by collection and shelfmark.")
mention(NOTES, 382, "m-chp8-p222-n1-gallery-title", "cand-7711", "Calleria di Pitture", "OCR spelling of the manuscript title; page image reads Galleria di Pitture.")
mention(NOTES, 382, "m-chp8-p222-n1-palace", "cand-2306", "Palazzo Vescovale di Ferrara", "Ferrara archbishop's palace described by the manuscript.")
mention(NOTES, 382, "m-chp8-p222-n1-baruffaldi", "cand-7710", "Girolamo Baruffaldi", "Author named in the manuscript title.")
mention(NOTES, 382, "m-chp8-p222-n1-ruffo", "cand-2304", "Tommaso Ruffo", "Cardinal whose palace and gallery the manuscript describes.")
mention(NOTES, 382, "m-chp8-p222-n1-bologna", "cand-3398", "Bologna", "City named in Ruffo's title and office description.")
mention(NOTES, 382, "m-chp8-p222-n1-gallery-collection", "cand-2307", "Pitture della sua Galleria", "Paintings Ruffo reportedly took with him to Rome.")
mention(NOTES, 382, "m-chp8-p222-n1-rome", "cand-4490", "Roma", "Destination named in the manuscript excerpt.")
mention(NOTES, 383, "m-chp8-p222-n2-ruffo", "cand-2304", "Russo", "OCR spelling; page image reads Ruffo.")
mention(NOTES, 383, "m-chp8-p222-n2-author", "cand-7709", "J. Agnelli", "Author cited with initial only in the note.")
mention(NOTES, 384, "m-chp8-p222-n3-breval-work", "cand-7713", "Breval, 1738,1, p. 193", "Citation to Breval's two-volume travel and antiquities work; OCR 1 is corrected to Roman I from the page image.")
mention(NOTES, 384, "m-chp8-p222-n3-breval-person", "cand-0451", "Breval", "Author of the cited 1738 work.")
mention(NOTES, 385, "m-chp8-p222-n5-group", "cand-7707", "Both of these", "Reference to the two Crespi works just named in the body.")
mention(NOTES, 385, "m-chp8-p222-n5-collection", "cand-2307", "Ruffo’s collection", "Collection from which the two paintings came.")
mention(NOTES, 385, "m-chp8-p222-n5-museum", "cand-7715", "Museo di Palazzo Venezia", "Institution reported as the location of the Crespi works.")
mention(NOTES, 385, "m-chp8-p222-n5-rome", "cand-4490", "Rome", "City named as the museum location.")
mention(NOTES, 385, "m-chp8-p222-n5-zanotti-work", "cand-7115", "Zanotti, II, p. 56", "Citation to the second volume of Storia dell’Accademia Clementina.")
mention(NOTES, 385, "m-chp8-p222-n5-zanotti-person", "cand-7114", "Zanotti", "Author of the cited work; source gives the surname only here.")
mention(NOTES, 385, "m-chp8-p222-n5-luigi-crespi-work", "cand-6591", "L. Crespi, p. 214", "Citation to Luigi Crespi's work identified from the book bibliography.")
mention(NOTES, 385, "m-chp8-p222-n5-luigi-crespi-person", "cand-7716", "L. Crespi", "Author identified as Luigi Crespi from the book bibliography.")
mention(NOTES, 385, "m-chp8-p222-n5-santangelo-work", "cand-7718", "Santangelo, pp. 2 and 23", "Citation to the Museo di Palazzo Venezia catalogue identified from the bibliography.")
mention(NOTES, 385, "m-chp8-p222-n5-santangelo-person", "cand-7717", "Santangelo", "Catalogue author given with initial A. in the bibliography.")


def lines_quote(segment_id: str, first: int, last: int) -> str:
    meta = segment_by_id[segment_id]
    return "\n".join(source_lines[first - 1:last])


ocr = [
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 127, "ocr": "os", "print": "of", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 127, "ocr": "in\" which", "print": "in which", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 128, "ocr": "XL", "print": "XI", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 130, "ocr": "rctrospect", "print": "retrospect", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 131, "ocr": "Italianjmasters", "print": "Italian masters", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 133, "ocr": "Masanella [sir]", "print": "Masanella [sic]", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 135, "ocr": "Presenti", "print": "Presents", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 135, "ocr": "sound so congenial", "print": "found so congenial", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 136, "ocr": "Ri serv.re", "print": "fu serv.re", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 382, "ocr": "Calleria", "print": "Galleria", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 383, "ocr": "Russo’s", "print": "Ruffo’s", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 384, "ocr": "1738,1", "print": "1738, I", "basis": "CHP-8.pdf physical page 24."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 385, "ocr": "6 Both of these", "print": "5 Both of these", "basis": "CHP-8.pdf physical page 24."},
]
for line in [128, 130, 131, 133, 134, 135]:
    ocr.append({"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": line,
                "ocr": "Russo", "print": "Ruffo", "basis": "CHP-8.pdf physical page 24."})
ocr.append({"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 130,
            "ocr": "Russo", "print": "Ruffo", "basis": "CHP-8.pdf physical page 24."})
ocr.append({"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 136,
            "ocr": "11 Ritratto", "print": "Il Ritratto", "basis": "CHP-8.pdf physical page 24."})


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", speaker="Haskell", extras=None):
    qualifiers = {
        "source_line_start": first_line, "source_line_end": last_line,
        "printed_page": 222, "pdf_physical_page": 24,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": lines_quote(segment_id, first_line, last_line),
        "origin": "book", "source_file": segment_by_id[segment_id]["source_file"],
    }


new_statements = [
    make_statement("st-chp8-p222-ferrerio-pupil", P222, 127, 127, "cand-1024", "cand-1602",
                   "reported_pupil_of",
                   "Haskell identifies Andrea Ferrerio as a pupil of the Bolognese Giuseppe Mazza.",
                   "This closes the p.221 statement about the Vigilance statue's sculptor; the source reports the pupil relation.",
                   ["cand-1024", "cand-1602"], extras={"continued_from_segment_id": P221,
                   "continued_from_statement_id": "st-chp8-p221-archbishop-palace-and-vigilance-statue-open",
                   "continuation_fragment": "a pupil of the Bolognese Giuseppe Mazza."}),
    make_statement("st-chp8-p222-staircase-stucco-medallions", P222, 127, 128, "cand-1024", "cand-7704",
                   "designed_staircase_stucco_and_papal_medallions",
                   "Haskell says Andrea Ferrerio also designed the rich stucco decoration of the staircase wall, including medallions of six popes; the series culminated in Innocent XII, Ruffo's own patron, and another medallion showed the reigning Pope Clement XI on the top floor.",
                   "The source does not name the other five popes. The OCR form Clement XL is corrected from the page image; all details remain Haskell's account.",
                   ["cand-1024", "cand-7704", "cand-1929", "cand-2304", "cand-0022"],
                   extras={"named_medallions": ["Innocent XII", "Clement XI"], "ocr_corrections": ocr[:3]}),
    make_statement("st-chp8-p222-bigari-ceiling-fresco", P222, 128, 130, "cand-0375", "cand-0374",
                   "painted_ceiling_fresco_of_allegorical_religion",
                   "Vittorio Bigari painted a ceiling fresco of the Catholic Religion, represented by the Papacy presiding over Ravenna, Bologna, and Ferrara; Haskell identifies those as the three cities where Ruffo principally served.",
                   "The allegorical subject, its representation, and Haskell's account of the cities are retained as written; this does not establish the fresco's current condition or location independently.",
                   ["cand-0375", "cand-0374", "cand-7708", "cand-4223", "cand-7697", "cand-3398", "cand-1017", "cand-2304"],
                   extras={"ocr_corrections": [ocr[3]] + [item for item in ocr if item["source_line"] == 130 and item["ocr"] == "Russo"]}),
    make_statement("st-chp8-p222-ruffo-setting-and-gallery", P222, 130, 130, "cand-2304", "cand-2307",
                   "designed_palace_setting_and_kept_collection",
                   "Haskell describes the staircase setting as grandiose and carefully designed by Ruffo in collaboration with his architect and sculptor, and says Ruffo kept there a varied collection of paintings that impressed contemporaries.",
                   "The contemporary enthusiasm and retrospective assessment are Haskell's characterizations; the collection is not a complete inventory.",
                   ["cand-2304", "cand-1580", "cand-1024", "cand-2307"],
                   extras={"qualification_terms": ["grandiose", "carefully designed", "aroused the enthusiasm", "still seems"],
                           "ocr_corrections": [item for item in ocr if item["source_line"] == 130]}),
    make_statement("st-chp8-p222-italian-masters-in-ruffo-collection", P222, 131, 132, "cand-2304", "cand-2307",
                   "reported_collection_attributions_to_italian_and_northern_masters",
                   "Haskell says Ruffo owned works attributed to Giorgione, Titian, Bassano, Correggio, Raphael, Parmigianino, Caravaggio, the Carracci, Guido Reni, and Guercino, as well as works by Rubens and Van Dyck that were less familiar in Italian collections.",
                   "The passage gives a broad reported list of attributions, not individual titles, provenances, or verified authorship. The collective Carracci reference is not assigned to Annibale alone.",
                   ["cand-2304", "cand-2307", "cand-1188", "cand-2630", "cand-0257", "cand-0852", "cand-2098", "cand-1839", "cand-0544", "cand-4318", "cand-2124", "cand-1258", "cand-2293", "cand-2155"],
                   extras={"ocr_corrections": [item for item in ocr if item["source_line"] == 131] + [item for item in ocr if item["source_line"] == 132]}) ,
    make_statement("st-chp8-p222-breval-castigliones", P222, 133, 133, "cand-0451", "cand-7705",
                   "visitor_described_four_castiglione_paintings",
                   "During a visit to Ferrara, John Breval wrote that he had seen four of the most capital Castiglione paintings.",
                   "This is Haskell's quotation of Breval; the four works are not individually identified.",
                   ["cand-0451", "cand-1017", "cand-0602", "cand-7705"],
                   extras={"quotation_attribution": "John Breval as quoted by Haskell", "qualification_terms": ["four", "I remember to have seen"]}),
    make_statement("st-chp8-p222-breval-lucretia", P222, 133, 133, "cand-0451", "cand-0579",
                   "described_lucretia_by_hannibal_carache",
                   "Breval called a Lucretia by Hannibal Carache an incomparable painting.",
                   "The quoted painter form is retained; the indexed Annibale Carracci candidate is an alignment lead, not an independent verification of attribution.",
                   ["cand-0451", "cand-0579", "cand-0576"],
                   extras={"quotation_attribution": "John Breval as quoted by Haskell", "qualification_terms": ["incomparable", "by Hannibal Carache"]}),
    make_statement("st-chp8-p222-breval-masanella", P222, 133, 133, "cand-0451", "cand-7706",
                   "described_original_of_neapolitan_mutineer_chief",
                   "Breval described a very fine original painting of the famous Neapolitan chief of the mutineers, named in the printed quotation as Masanella [sic].",
                   "The artist, medium, and exact identity of the painting are not stated. Preserve the quotation's [sic] spelling and do not add a portrait attribution.",
                   ["cand-0451", "cand-7706", "cand-4150"],
                   extras={"quotation_attribution": "John Breval as quoted by Haskell", "ocr_corrections": [ocr[5]]}),
    make_statement("st-chp8-p222-pareja-portrait-to-rome-exhibition", P222, 133, 133, "cand-2304", "cand-2714",
                   "reported_portrait_owned_and_sent_to_1704_rome_exhibition",
                   "Haskell says one of the most remarkable pictures in Ruffo's collection was Velasquez's portrait of his servant Juan de Pareja, described as cosa stupenda, which Ruffo sent to an exhibition in Rome in 1704.",
                   "The source-time attribution, sitter relationship, and exhibition report are preserved; the painting and loan history were not independently verified.",
                   ["cand-2304", "cand-2307", "cand-2714", "cand-2709", "cand-1834", "cand-4490", "cand-6051"],
                   extras={"qualification_terms": ["must have been", "cosa stupenda", "in 1704"], "relation_candidate": True,
                           "ocr_corrections": [item for item in ocr if item["source_line"] == 133]}),
    make_statement("st-chp8-p222-crespi-four-works", P222, 134, 135, "cand-0871", "cand-2307",
                   "represented_by_four_works_in_ruffo_collection",
                   "Haskell says most of Ruffo's modern pictures came from Bologna and Crespi was represented in his collection by four works.",
                   "The four works are not all named; the count and collection description are Haskell's report.",
                   ["cand-0871", "cand-2307", "cand-3398", "cand-7707"],
                   extras={"quantity": 4, "qualification_terms": ["bulk", "four works"]}),
    make_statement("st-chp8-p222-ruffo-commissioned-two-crespi-works", P222, 134, 135, "cand-2304", "cand-0871",
                   "commissioned_two_named_paintings_from_crespi_during_ferrara_legateship",
                   "Haskell says two of Crespi's four works, Abigail giving Presents to David and The Finding of Moses, were commissioned during Ruffo's Ferrara legateship.",
                   "The index's later Crespi subentry cand-0879 may overlap with The Finding of Moses but is not merged here. The source gives no dates or current locations in the body.",
                   ["cand-2304", "cand-0871", "cand-1017", "cand-7719", "cand-7720", "cand-7721", "cand-4268", "cand-4144"],
                   extras={"work_candidate_ids": ["cand-7719", "cand-7720"], "qualification_terms": ["two of which", "during Russo's legateship"]}),
    make_statement("st-chp8-p222-crespi-creti-style-comparison", P222, 135, 135, "cand-0871", "cand-0889",
                   "author_assesses_creti_as_more_aristocratic_counterpart_to_crespi",
                   "Haskell describes the two religious themes in Crespi's paintings as subdued and tenderly romantic, and suggests this quality may have appealed to Ruffo in Donato Creti, whom he calls Crespi's more aristocratic counterpart in depicting such subjects.",
                   "The aesthetic description and the suggested reason are Haskell's interpretation; 'perhaps' remains qualified.",
                   ["cand-0871", "cand-0889", "cand-2304"],
                   extras={"qualification_terms": ["subdued and tender romanticism", "perhaps", "so congenial"]}),
    make_statement("st-chp8-p222-ruffo-fondness-for-creti-open", P222, 135, 135, "cand-2304", "cand-0889",
                   "reported_patron_affinity_for_creti_open_continuation",
                   "Haskell says Ruffo was so fond of Donato Creti that he used to sit…",
                   "The sentence ends mid-thought at p.222; retain it as open until the p.223 continuation is read.",
                   ["cand-2304", "cand-0889"],
                   extras={"continuation_to_segment_id": P223, "continuation_to_source_line": 140,
                           "continuation_fragment": "He was so fond of this painter that he used to sit", "continuation_status": "open",
                           "qualification_terms": ["so fond"]}),
    make_statement("st-chp8-p222-n1-manuscript-source", NOTES, 382, 382, None, "cand-7711",
                   "footnote_identifies_manuscript_source_for_palace_description",
                   "Haskell says his account of the Archbishop's palace is taken from Collezione Antonelli MS. 610 in Biblioteca Ariostea, Ferrara, a manuscript titled as a gallery of paintings collected and displayed in the Ferrara episcopal palace and described by Girolamo Baruffaldi.",
                   "The manuscript is identified from Haskell's footnote and title; it was not independently consulted. Page-image reading corrects Calleria to Galleria.",
                   ["cand-7711", "cand-7712", "cand-1017", "cand-7710", "cand-2306"], text_layer="footnote citation",
                   extras={"footnote_marker": 1, "printed_page_locator": "p.222 n.1", "ocr_corrections": [ocr[9]]}),
    make_statement("st-chp8-p222-n1-ruffo-resigns-and-takes-gallery", NOTES, 382, 382, "cand-2304", "cand-2307",
                   "manuscript_reports_resignation_and_removal_of_gallery_paintings",
                   "Haskell quotes the manuscript as saying that Ruffo, bored and dissatisfied with the Ferrara archbishopric, resigned it to the Pope, left for Rome, and took his gallery paintings with him.",
                   "This is a nested manuscript report quoted by Haskell; neither the manuscript nor the quoted passage was independently checked, and the unnamed Pope is not identified.",
                   ["cand-2304", "cand-2307", "cand-7711", "cand-4490"], text_layer="footnote report",
                   extras={"footnote_marker": 1, "printed_page_locator": "p.222 n.1", "quotation_language": "Italian", "relation_candidate": True}),
    make_statement("st-chp8-p222-n1-manuscript-citation", NOTES, 382, 382, None, "cand-7711",
                   "footnote_citation",
                   "Footnote 1 identifies Collezione Antonelli MS. 610, described by Girolamo Baruffaldi, as the source of the palace and gallery account.",
                   "Citation and manuscript report are Haskell's; no catalogue record or manuscript image was consulted in this task.",
                   ["cand-7711", "cand-7712", "cand-7710"], text_layer="bibliographic citation",
                   extras={"footnote_marker": 1, "printed_page_locator": "p.222 n.1", "linked_body_statement_ids": ["st-chp8-p222-n1-ruffo-resigns-and-takes-gallery"]}),
    make_statement("st-chp8-p222-n2-agnelli-publication", NOTES, 383, 383, "cand-2307", "cand-7261",
                   "gallery_picture_list_published_with_verse_commentaries",
                   "Haskell says the list of Ruffo's pictures was published with verse commentaries by J. Agnelli.",
                   "The bibliography identifies Agnelli's 1734 Galleria di pitture del Card. Tomm. Ruffo vescovo di Ferrara; the publication itself was not independently read.",
                   ["cand-2307", "cand-7261", "cand-7709", "cand-2304"], text_layer="footnote report",
                   extras={"footnote_marker": 2, "printed_page_locator": "p.222 n.2", "bibliography_locator": "21_CHP-21Bibliography.md", "relation_candidate": True}),
    make_statement("st-chp8-p222-n2-agnelli-citation", NOTES, 383, 383, None, "cand-7261",
                   "footnote_citation",
                   "Footnote 2 points to the Agnelli publication associated in the bibliography with Ruffo's Ferrara gallery.",
                   "This is a bibliographic identification only; no contents beyond Haskell's statement were inspected.",
                   ["cand-7261", "cand-7709"], text_layer="bibliographic citation",
                   extras={"footnote_marker": 2, "printed_page_locator": "p.222 n.2", "linked_body_statement_ids": ["st-chp8-p222-italian-masters-in-ruffo-collection"]}),
    make_statement("st-chp8-p222-n3-breval-citation", NOTES, 384, 384, None, "cand-7713",
                   "footnote_citation",
                   "Footnote 3 cites Breval, 1738, volume I, page 193.",
                   "The work title and edition are resolved from the book bibliography; the cited page was not read independently. The OCR numeral 1 is corrected to Roman I from the page image.",
                   ["cand-0451", "cand-7713"], text_layer="bibliographic citation",
                   extras={"footnote_marker": 3, "printed_page_locator": "p.222 n.3", "volume": "I", "page_start": "193", "ocr_corrections": [ocr[11]],
                           "linked_body_statement_ids": ["st-chp8-p222-breval-castigliones", "st-chp8-p222-breval-lucretia", "st-chp8-p222-breval-masanella"]}),
    make_statement("st-chp8-p222-n4-pareja-exhibition", P222, 136, 137, "cand-2714", "cand-6051",
                   "inventory_identifies_pareja_portrait_lent_to_1704_exhibition",
                   "Haskell quotes an inventory description of the portrait as a three-palmi picture representing a servant of Diego Velasquez and says it was lent to the 1704 exhibition at S. Salvatore in Lauro.",
                   "The footnote cross-refers to p.125 n.1. The quote is an inventory locator reported by Haskell, not a newly inspected archival source; OCR Ri is corrected to fu from the page image.",
                   ["cand-2714", "cand-2709", "cand-6051", "cand-6052", "cand-4490", "cand-1834"], text_layer="footnote report",
                   extras={"footnote_marker": 4, "printed_page_locator": "p.222 n.4", "linked_body_statement_ids": ["st-chp8-p222-pareja-portrait-to-rome-exhibition"], "ocr_corrections": [ocr[8]]}),
    make_statement("st-chp8-p222-n4-pareja-museum-and-hamilton", P222, 137, 138, "cand-2714", "cand-7472",
                   "reported_later_location_and_hamilton_ownership",
                   "Haskell says the same portrait was then in the Metropolitan Museum and had been in Sir William Hamilton's collection in Naples by 1798.",
                   "'Now' is relative to Haskell's account. No current collection catalogue or Hamilton inventory was consulted.",
                   ["cand-2714", "cand-7472", "cand-7714", "cand-1722"], text_layer="footnote report",
                   extras={"footnote_marker": 4, "printed_page_locator": "p.222 n.4", "linked_body_statement_ids": ["st-chp8-p222-pareja-portrait-to-rome-exhibition"], "relation_candidate": True}),
    make_statement("st-chp8-p222-n5-crespi-works-at-museo-palazzo-venezia", NOTES, 385, 385, "cand-7707", "cand-7715",
                   "reported_location_of_two_ruffo_crespi_paintings",
                   "Haskell's note says both Crespi paintings just named, together with other pictures from Ruffo's collection, were then in the Museo di Palazzo Venezia in Rome.",
                   "The cross-reference points to the two paintings on p.222; the reported location and the cited catalogue references were not independently checked. The printed footnote marker is 5, not OCR 6.",
                   ["cand-7719", "cand-7720", "cand-7707", "cand-2307", "cand-7715", "cand-4490"], text_layer="footnote report",
                   extras={"footnote_marker": 5, "printed_page_locator": "p.222 n.5", "linked_body_statement_ids": ["st-chp8-p222-crespi-four-works", "st-chp8-p222-ruffo-commissioned-two-crespi-works"], "ocr_corrections": [ocr[12]], "relation_candidate": True}),
    make_statement("st-chp8-p222-n5-zanotti-citation", NOTES, 385, 385, None, "cand-7115",
                   "footnote_citation", "Footnote 5 cites Zanotti, volume II, page 56.",
                   "The book bibliography identifies Storia dell’Accademia Clementina; the cited page was not independently read.",
                   ["cand-7114", "cand-7115"], text_layer="bibliographic citation",
                   extras={"footnote_marker": 5, "printed_page_locator": "p.222 n.5", "volume": "II", "page_start": "56"}),
    make_statement("st-chp8-p222-n5-luigi-crespi-citation", NOTES, 385, 385, None, "cand-6591",
                   "footnote_citation", "Footnote 5 cites L. Crespi, page 214.",
                   "The book bibliography identifies Luigi Crespi's Vite de’ Pittori bolognesi; the cited page was not independently read.",
                   ["cand-7716", "cand-6591"], text_layer="bibliographic citation",
                   extras={"footnote_marker": 5, "printed_page_locator": "p.222 n.5", "page_start": "214"}),
    make_statement("st-chp8-p222-n5-santangelo-citation", NOTES, 385, 385, None, "cand-7718",
                   "footnote_citation", "Footnote 5 also cites Santangelo's Museo di Palazzo Venezia catalogue, pages 2 and 23.",
                   "The author initial, catalogue title, place, and year are identified from the book bibliography; neither cited page was independently read.",
                   ["cand-7717", "cand-7718"], text_layer="bibliographic citation",
                   extras={"footnote_marker": 5, "printed_page_locator": "p.222 n.5", "page_start": "2", "page_end": "23"}),
]

existing_statement_ids = {row["statement_id"] for row in statement_rows}
new_statement_ids = [row["statement_id"] for row in new_statements]
if len(set(new_statement_ids)) != len(new_statement_ids) or existing_statement_ids.intersection(new_statement_ids):
    raise SystemExit("duplicate statement IDs")
for row in new_statements:
    q = row["qualifiers"]
    if q["source_line_start"] > q["source_line_end"] or not set(q["mentioned_candidate_ids"]) <= candidate_ids:
        raise SystemExit(f"invalid statement anchors or candidate references: {row['statement_id']}")
    if row["segment_id"] == P222 and not (127 <= q["source_line_start"] <= 138 and 127 <= q["source_line_end"] <= 138):
        raise SystemExit(f"statement outside p.222 source range: {row['statement_id']}")
    if row["segment_id"] == NOTES and q["source_line_start"] not in {382, 383, 384, 385}:
        raise SystemExit(f"statement outside p.222 notes: {row['statement_id']}")
    if not row["original_quote"]:
        raise SystemExit(f"empty original quote: {row['statement_id']}")

prior_id = "st-chp8-p221-archbishop-palace-and-vigilance-statue-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open" or prior["qualifiers"].get("continuation_to_segment_id") != P222:
    raise SystemExit("p.221 open continuation changed; inspect before closing")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continued_to_segment_id": P222,
    "continued_to_source_line": 127, "continued_to_statement_id": "st-chp8-p222-ferrerio-pupil",
    "continuation_fragment": "a pupil of the Bolognese Giuseppe Mazza.",
})

new_coverage = []
for row in coverage_rows:
    sid = row["segment_id"]
    if sid == P221:
        row.update({"disposition": "reviewed", "migration_status": "complete",
                    "source_line_ranges": "L113-124", "note": "p.221 Ferrerio statue continuation closes at p.222 L127."})
    elif sid == P222:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L127-138", "note": "p.222 read against CHP-8.pdf physical page 24; final sentence about Ruffo and Creti continues on p.223 L140."})
    elif sid == NOTES:
        row.update({"source_line_ranges": "L373-385", "migration_status": "partial",
                    "note": "p.222 notes 1-3 and 5 migrated; remaining consolidated notes are queued by printed page."})
    new_coverage.append(row)

preview = {
    "mode": "dry-run", "candidate_additions": len(new_candidates),
    "mention_additions": len(new_mentions), "statement_additions": len(new_statements),
    "continuations": [
        {"statement_id": prior_id, "status": "closed", "to": P222, "line": 127},
        {"statement_id": "st-chp8-p222-ruffo-fondness-for-creti-open", "status": "open", "to": P223, "line": 140},
    ],
    "coverage_updates": {
        P221: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L113-124"},
        P222: {"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L127-138"},
        NOTES: {"source_line_ranges": "L373-385", "migration_status": "partial"},
    },
    "ocr_corrections": [f"L{x['source_line']} {x['ocr']} -> {x['print']}" for x in ocr],
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (CANDIDATE_PATH, MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
patched_statements.extend(new_statements)
write_csv_atomic(CANDIDATE_PATH, candidate_fields, candidate_rows)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
write_jsonl_atomic(STATEMENT_PATH, patched_statements)
write_csv_atomic(COVERAGE_PATH, coverage_fields, new_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
