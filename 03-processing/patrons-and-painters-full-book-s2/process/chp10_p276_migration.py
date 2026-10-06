"""Controlled S2 migration for Chapter 10 p.276; dry-run by default."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
HEADER = "chp-10:10_CHP-10_intro:l1-1"
SEGMENT = "chp-10:10_CHP-10_intro:l3-13"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
HEADER_SHA = "2929e867e881835dcc10b3c28ccf398f462fb401b03fcf13684c77873921f218"
SEGMENT_SHA = "2b86f1b920d1aa7de55b2ba8f511e3c8ec71b8c546387f71da2113d40e197e92"
MAX_CANDIDATE = 8830
BACKUP_SUFFIX = ".bak-s2-chp10-p276-20261002"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(source_bytes).hexdigest() != ASSET_SHA:
    raise SystemExit("Chapter 10 intro source asset changed")

segment_rows = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segment_rows}
expected_segments = {HEADER: HEADER_SHA, SEGMENT: SEGMENT_SHA}
for segment_id, expected_sha in expected_segments.items():
    meta = segment_by_id.get(segment_id)
    if not meta or meta.get("sha256") != expected_sha or meta.get("asset_sha256") != ASSET_SHA:
        raise SystemExit(f"source segment missing or changed: {segment_id}")
    exact = "\n".join(source_lines[meta["line_start"] - 1 : meta["line_end"]])
    if hashlib.sha256(exact.encode("utf-8")).hexdigest() != expected_sha:
        raise SystemExit(f"source segment content hash mismatch: {segment_id}")
if source_lines[0].strip() != "# 10 CHP-10 intro" or source_lines[2].strip() != "[Page 2]":
    raise SystemExit("expected generated heading/page marker changed")
if "FOREIGN INFLUENCES" not in source_lines[4] or "Christian Cole" not in source_lines[8]:
    raise SystemExit("expected p.276 text changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {MAX_CANDIDATE}, found {maximum}")
for segment_id in (HEADER, SEGMENT):
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != ("queued", "pending"):
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")

EXISTING = {
    "venice_city": "cand-2725",
    "venice_nobility": "cand-8677",
    "catholic_church": "cand-8672",
    "europe": "cand-3462",
    "cole": "cand-0801",
    "carriera": "cand-0581",
    "reni": "cand-2124",
    "manchester": "cand-1504",
    "carlevarijs": "cand-0554",
    "pellegrini": "cand-1862",
    "marco_ricci": "cand-2149",
    "sebastiano_ricci": "cand-2154",
    "cassana": "cand-0593",
    "dartmouth": "cand-0904",
    "england": "cand-7200",
    "tiepolo": "cand-2569",
    "piazzetta": "cand-1901",
}
for key, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("venetian_state_patron", "State as a traditional patronage source in Haskell's p.276 account", "institution", "The printed page names the State among traditional patronage sources. Given the chapter context it may refer to Venice's political authority; keep its relation to the explicit Republic candidate for later S3 alignment.", 6),
    ("southern_germany", "Southern Germany in Haskell's p.276 comparison with Venetian patronage", "place", "Named as a region with regimes Haskell compares to Venice; no specific court, ruler, or commission is supplied.", 7),
    ("spain_regime", "Spain as a similar-regime patronage context in Haskell's p.276 account", "institution", "Spain is grouped with regimes said to appreciate this art; no specific monarch, court, or commission is named.", 7),
    ("counter_reformation_painting", "Conservative Counter-Reformation elements in Italian painting (p.276 account)", "term", "Haskell's characterization of tendencies promoted by the three traditional patron groups; preserve it as the author's interpretation.", 7),
    ("italian_painting", "Italian painting as the field discussed in Haskell's p.276 account", "term", "The field in which Haskell locates the patronage tendencies; do not infer a bounded movement or school.", 7),
    ("rococo", "Rococo as a European artistic fashion in Haskell's p.276 contrast", "term", "One of the fashions Haskell says the new art could follow; the passage does not identify a particular work.", 8),
    ("neoclassical", "Neo-classical art as a European fashion in Haskell's p.276 contrast", "term", "One of the fashions Haskell says the new art could follow; retain the source's hyphenated wording in the mention.", 8),
    ("venetian_republic", "Republic of Venice as the political entity in Haskell's p.276 account", "institution", "The political entity with which Lord Manchester is said to have quarrelled; distinguish it from Venice as a city and leave wider identity alignment to S3.", 12),
    ("manchester_entry_work", "Unidentified painting of Lord Manchester's entry into Venice (commission attributed to Luca Carlevarijs, 1707)", "work", "The source supplies no title. The p.276 footnote locator and any later identification remain to be processed from the canonical footnote block.", 12),
    ("osti_locator", "Osti, 1951, p. 119 (bibliographic locator cited by Haskell at p.276)", "archive", "Short-form citation only; full bibliographic identity is deferred to the canonical bibliography segment. The cited page has not been independently consulted.", 13),
]

new_candidates = []
candidate_by_key = {}
for offset, (key, name, kind, detail, source_line) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids or any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate ID/natural key exists: {candidate_id} {name}")
    candidate_by_key[key] = candidate_id
    new_candidates.append({
        "candidate_id": candidate_id,
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
        "candidate_source_ref": f"{SEGMENT}#L{source_line}",
    })
candidate_ids |= {row["candidate_id"] for row in new_candidates}


def candidate(key):
    return candidate_by_key[key] if key in candidate_by_key else EXISTING[key]


segment_meta = segment_by_id[SEGMENT]
segment_text = "\n".join(source_lines[segment_meta["line_start"] - 1 : segment_meta["line_end"]])
line_offsets = {}
cursor = 0
for line_no in range(segment_meta["line_start"], segment_meta["line_end"] + 1):
    line_offsets[line_no] = cursor
    cursor += len(source_lines[line_no - 1]) + 1

new_mentions = []


def mention(local_id, surface, candidate_key, note="", occurrence=0):
    mention_id = f"m-chp10-p276-{local_id}"
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    found = []
    start = 0
    while True:
        position = segment_text.find(surface, start)
        if position < 0:
            break
        found.append(position)
        start = position + 1
    if occurrence >= len(found):
        raise SystemExit(f"source surface absent: {surface!r} occurrence={occurrence}")
    start_char = found[occurrence]
    end_char = start_char + len(surface)
    if segment_text[start_char:end_char] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    candidate_id = candidate(candidate_key)
    if candidate_id not in candidate_ids:
        raise SystemExit(f"mention references absent candidate: {mention_id} -> {candidate_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start_char),
        "end_char": str(end_char),
        "note": note,
    })


MENTION_SPECS = [
    ("state", "iTATE", "venetian_state_patron", "OCR fragment for printed 'STATE'; preserve raw source span and S2 correction.", 0),
    ("nobles", "nobles", "venice_nobility", "Unnamed Venetian noble group as one of the three traditional patron categories.", 0),
    ("church", "Church", "catholic_church", "The Church is named as a broad patronage institution, not a specific church building.", 0),
    ("counter_reformation", "Counter Reformation", "counter_reformation_painting", "Source prints the two words without a hyphen.", 0),
    ("italian_painting", "Italian painting", "italian_painting", "Field named in Haskell's account.", 0),
    ("southern_germany", "Southern Germany", "southern_germany", "Region in the source's regime comparison.", 0),
    ("spain", "Spain", "spain_regime", "Country named as a later similar-regime context.", 0),
    ("venetian_adjective", "Venetian", "venice_city", "Adjectival reference to Venice in the author's description of isolation.", 0),
    ("venice_city", "Venice", "venice_city", "The cosmopolitan city of pleasure in the contrast.", 0),
    ("europe_fashion", "Europe", "europe", "European context for contemporary artistic fashion.", 0),
    ("rococo", "rococo", "rococo", "Named artistic fashion; no specific work is identified.", 0),
    ("neoclassical", "neo-classical", "neoclassical", "Named artistic fashion; preserve the source's hyphenation.", 0),
    ("tiepolo_regimes", "Tiepolo", "tiepolo", "Painter named in the regime comparison.", 0),
    ("piazzetta", "Piazzetta", "piazzetta", "Painter named among the contrasting history painters.", 0),
    ("tiepolo_visions", "Tiepolo", "tiepolo", "Painter named in the closing contrast with the new art.", 1),
    ("europe_war", "Europe", "europe", "Geopolitical frame of the author's account.", 1),
    ("venice_neutral", "Venice", "venetian_republic", "Venice as a neutral political actor, distinct from the city candidate above.", 1),
    ("cole_full", "Christian Cole", "cole", "British Ambassador's first secretary in Haskell's account.", 0),
    ("carriera", "Rosalba Carriera", "carriera", "Artist introduced in the 1703 encounter.", 0),
    ("reni", "Guido Reni", "reni", "Artist used as a comparison for Carriera's work.", 0),
    ("manchester_crossline", "Lord.\nManchester", "manchester", "OCR punctuation/line break splits the name; the printed text reads Lord Manchester.", 0),
    ("carlevarijs_crossline", "Luca\nCarlevarijs", "carlevarijs", "Name is split across OCR lines; retain the source line break in this exact span.", 0),
    ("entry_work", "his entry", "manchester_entry_work", "Unidentified painting subject commissioned from Carlevarijs.", 0),
    ("republic", "the Republic", "venetian_republic", "Political entity in the account of Manchester's quarrel and departure.", 0),
    ("england", "England", "england", "Destination to which Manchester took the two named artists.", 0),
    ("pellegrini_full", "Giovanni Antonio Pellegrini", "pellegrini", "Full artist name at first occurrence in the passage.", 0),
    ("marco_ricci", "Marco Ricci", "marco_ricci", "Young landscape painter named by Haskell.", 0),
    ("cole_short", "Cole", "cole", "Christian Cole named again in the authorial assessment.", 1),
    ("pellegrini_short", "Pellegrini", "pellegrini", "Short form in Cole's recommendation; the candidate remains an S2 source candidate.", 1),
    ("dartmouth", "Lord Dartmouth", "dartmouth", "Recipient named in the account of Cole's letters.", 0),
    ("sebastiano_ricci", "Sebastiano Ricci", "sebastiano_ricci", "Artist whose signed picture estimates Cole enclosed.", 0),
    ("cassana", "Niccolo Cassana", "cassana", "Artist named in the OCR; no accent correction is made without a clear print basis.", 0),
    ("osti", "Osti, 1951, p. 119", "osti_locator", "Inline bibliographic locator; full item identity deferred to the bibliography segment.", 0),
]
for spec in MENTION_SPECS:
    mention(*spec)

new_statements = []


def quote_between(first: str, last: str):
    start = segment_text.find(first)
    if start < 0:
        raise SystemExit(f"quote start absent: {first!r}")
    end_start = segment_text.find(last, start)
    if end_start < 0:
        raise SystemExit(f"quote end absent after {first!r}: {last!r}")
    return segment_text[start : end_start + len(last)], start, end_start + len(last)


def source_line_at(offset: int):
    for line_no in sorted(line_offsets, reverse=True):
        if offset >= line_offsets[line_no]:
            return line_no
    return segment_meta["line_start"]


OCR_CORRECTIONS = {
    "state_opening": [
        {"source_file": SOURCE_FILE, "source_line": 6, "ocr": "- iTATE", "print": "STATE", "basis": "CHP-10.pdf physical page 1."},
        {"source_file": SOURCE_FILE, "source_line": 6, "ocr": "of-patronage", "print": "of patronage", "basis": "CHP-10.pdf physical page 1."},
        {"source_file": SOURCE_FILE, "source_line": 7, "ocr": "Shave", "print": "have", "basis": "CHP-10.pdf physical page 1."},
    ],
    "manchester": [
        {"source_file": SOURCE_FILE, "source_line": 10, "ocr": "Lord.\\nManchester", "print": "Lord Manchester", "basis": "CHP-10.pdf physical page 1."},
    ],
    "departure": [
        {"source_file": SOURCE_FILE, "source_line": 12, "ocr": "left’ taking", "print": "left, taking", "basis": "CHP-10.pdf physical page 1."},
    ],
    "cole_part": [
        {"source_file": SOURCE_FILE, "source_line": 13, "ocr": "pan", "print": "part", "basis": "CHP-10.pdf physical page 1."},
    ],
}


def add_statement(local_id, first, last, predicate, claim, qualification, refs=(), subject=None,
                  obj=None, relation=False, footnote=None, corrections=None,
                  text_layer="authorial narrative"):
    statement_id = f"st-chp10-p276-{local_id}"
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    original_quote, start, end = quote_between(first, last)
    references = set(refs) | {key for key in (subject, obj) if key}
    candidate_refs = {candidate(key) for key in references}
    if not candidate_refs <= candidate_ids:
        raise SystemExit(f"statement references missing candidates: {statement_id}")
    qualifiers = {
        "source_line_start": source_line_at(start),
        "source_line_end": source_line_at(end - 1),
        "printed_page": 276,
        "pdf_physical_page": 1,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": sorted(candidate_refs),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["footnote_link_status"] = "pending_source_migration"
    if corrections:
        qualifiers["ocr_corrections"] = OCR_CORRECTIONS[corrections]
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT,
        "subject_candidate_id": None if subject is None else candidate(subject),
        "object_candidate_id": None if obj is None else candidate(obj),
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": original_quote,
        "source_file": SOURCE_FILE,
        "origin": "book",
    })


add_statement(
    "traditional-patronage-sources", "- iTATE", "eighteenth century.",
    "state_nobility_and_church_named_as_traditional_patronage_sources",
    "Haskell names the State, nobles, and Church as traditional sources of patronage and says they had operated during the first part of the eighteenth century.",
    "Authorial framing in the Venice chapter. The OCR's initial 'iTATE' is corrected from the scan; the State's exact institutional referent remains source-local.",
    refs=("venetian_state_patron", "venice_nobility", "catholic_church"), corrections="state_opening")
add_statement(
    "counter-reformation-painting", "All three tended", "Italian painting",
    "traditional_patronage_promoted_conservative_counter_reformation_elements_in_italian_painting",
    "Haskell says the three patron groups tended to promote conservative Counter-Reformation elements in Italian painting.",
    "This is Haskell's characterization of a tendency, not a claim that every commission or painting shared the same programme.",
    refs=("venetian_state_patron", "venice_nobility", "catholic_church", "counter_reformation_painting", "italian_painting"))
add_statement(
    "similar-regimes-and-tiepolo", "and this led", "European politics.",
    "similar_regimes_in_southern_germany_and_later_spain_appreciated_the_art_and_tiepolo_was_called_in_for_grandeur",
    "Haskell says the resulting art was most fully appreciated in regimes similar to Venice, notably Southern Germany and later Spain. He adds that Tiepolo was called in to satisfy grandeur ambitions.",
    "The phrase 'illusions of grandeur' is Haskell's evaluative interpretation. The relative 'where' most immediately follows Spain, but do not assign a Tiepolo commission to both regions; no particular ruler, commission, or work is identified.",
    refs=("italian_painting", "southern_germany", "spain_regime", "tiepolo", "europe"), relation=True)
add_statement(
    "venetian-isolation", "Essentially,", "foreign ambassadors and visitors.",
    "venetian_patron_paintings_reflected_desire_for_isolation_expressed_through_censorship",
    "Haskell says paintings for the three patron types reflected a Venetian desire to isolate from the contemporary world, also manifested in censorship and restrictions on foreign ambassadors and visitors.",
    "Authorial interpretation; 'Venetian' is retained as a political-cultural characterization and is not generalized beyond the passage.",
    refs=("venice_city", "venetian_state_patron"))
add_statement(
    "cosmopolitan-venice-and-new-art", "But there was another Venice", "history painters.",
    "cosmopolitan_venice_supported_new_art_responsive_to_rococo_and_neoclassical_fashion",
    "Haskell contrasts a cosmopolitan Venice of tourists and dilettantes with a new kind of art more attuned to European fashion, from rococo to neo-classical, than the visions of Tiepolo, Piazzetta, and other history painters.",
    "This is the author's contrast between patronage audiences and art; it does not identify individual works or establish a formal movement boundary.",
    refs=("venice_city", "europe", "rococo", "neoclassical", "tiepolo", "piazzetta"))
add_statement(
    "war-neutrality-and-visitors", "Europe was at war", "military campaigns.",
    "venice_remained_neutral_while_foreign_embassies_and_kings_sought_alliance_or_relief",
    "Haskell says Venice remained neutral while foreign embassies intrigued and foreign kings visited seeking alliance or respite from military campaigns.",
    "The unnamed embassies and kings remain collective actors; no specific diplomatic mission or ruler is inferred.",
    refs=("europe", "venetian_republic"))
add_statement(
    "cole-carriera-pastel-portraits", "In 1703", "Guido Reni.1",
    "cole_encountered_carriera_and_encouraged_pastel_portraiture",
    "Haskell says Christian Cole encountered Rosalba Carriera painting snuff-boxes and ivory miniatures in 1703, persuaded her to turn to pastel portraits, and her work was soon compared with Guido Reni.",
    "Retain Haskell's chronology and comparison; footnote 1 is a source trail and remains pending migration. The cited works have not been independently consulted.",
    refs=("cole", "carriera", "reni"), relation=True, footnote=1)
add_statement(
    "manchester-carlevarijs-entry", "In 1707", "record his entry.2",
    "manchester_commissioned_carlevarijs_to_record_his_venice_entry",
    "Haskell says Lord Manchester returned to Venice on a second official visit in 1707 and commissioned Luca Carlevarijs to record his entry.",
    "The painting has no title in this passage. Footnote 2 is pending; do not identify the work from a later locator before that segment is processed.",
    refs=("manchester", "carlevarijs", "venice_city", "manchester_entry_work"), relation=True, footnote=2,
    corrections="manchester")
add_statement(
    "manchester-departure-with-artists", "A year later", "Marco Ricci.3",
    "manchester_left_venice_with_pellegrini_and_marco_ricci_for_england",
    "Haskell says that a year after the 1707 visit Manchester quarrelled with the Republic and left, taking Giovanni Antonio Pellegrini and Marco Ricci to England.",
    "The text gives a relative date ('a year later'); do not replace it with a separately asserted year. Footnote 3 remains pending migration.",
    refs=("manchester", "venetian_republic", "pellegrini", "marco_ricci", "england"), relation=True,
    footnote=3, corrections="departure")
add_statement(
    "cole-recommended-pellegrini", "Cole played", "in 1707,",
    "cole_almost_certainly_advised_manchester_to_choose_pellegrini",
    "Haskell says Cole played an important role in Anglo-Venetian artistic relations and almost certainly advised the Duke of Manchester to choose Pellegrini to take to England in 1707.",
    "Preserve 'almost certainly'; Haskell's use of 'Duke' follows the earlier 'Lord Manchester' reference, but title identity is not made a separate finding here.",
    refs=("cole", "manchester", "pellegrini", "england"), relation=True)
add_statement(
    "cole-dartmouth-estimates", "and in 1710", "Osti, 1951, p. 119.",
    "cole_wrote_dartmouth_in_1710_and_1711_with_estimates_for_ricci_and_cassana_pictures",
    "Haskell says Cole wrote to Lord Dartmouth in 1710 and 1711 enclosing estimates for pictures signed by Sebastiano Ricci and Niccolo Cassana.",
    "Osti, 1951, p. 119 is an inline locator only; its full identity is deferred to the bibliography segment and the cited page has not been consulted.",
    refs=("cole", "dartmouth", "sebastiano_ricci", "cassana", "osti_locator"), relation=True,
    text_layer="authorial narrative with bibliographic locator", corrections="cole_part")

if len(new_mentions) != len(MENTION_SPECS) or len(new_statements) != 11:
    raise SystemExit("unexpected draft row count")
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("statement natural key already exists")

header_coverage = coverage_by_id[HEADER]
header_coverage.update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L1-1",
    "note": "Generated Markdown filename heading only; not printed book content and contains no claim or entity mention.",
})
body_coverage = coverage_by_id[SEGMENT]
body_coverage.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L3-13",
    "note": "Printed p.276 opening body read against CHP-10.pdf physical p.1. L3-L5 are page/title/section navigation; narrative is L6-L13. The p.276 footnotes are consolidated at L492-L494 in this canonical file and remain assigned to their later source segment; the full-chapter OCR is comparison only.",
})

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 rows and coverage updates")
args = parser.parse_args()
print(f"segment={SEGMENT}; new_candidates={len(new_candidates)}; mentions={len(new_mentions)}; statements={len(new_statements)}")
print(f"excluded_header={HEADER}; OCR_corrections={sum(len(v) for v in OCR_CORRECTIONS.values())}")
print(f"source_sha256={ASSET_SHA}; segment_sha256={SEGMENT_SHA}; next_candidate=cand-{MAX_CANDIDATE + 1:04d}")
if not args.apply:
    print("DRY RUN: no files changed")
else:
    table_paths = [candidate_path, mention_path, statement_path, coverage_path]
    backup_paths = [path.with_name(path.name + BACKUP_SUFFIX) for path in table_paths]
    existing_backups = [path.name for path in backup_paths if path.exists()]
    if existing_backups:
        raise SystemExit(f"refusing to overwrite existing backups: {existing_backups}")
    for path, backup in zip(table_paths, backup_paths):
        shutil.copy2(path, backup)
    write_csv_atomic(candidate_path, candidate_fields, candidates + new_candidates)
    write_csv_atomic(mention_path, mention_fields, mentions + new_mentions)
    write_jsonl_atomic(statement_path, statements + new_statements)
    write_csv_atomic(coverage_path, coverage_fields, coverage)
    print("applied; backups=" + ",".join(path.name for path in backup_paths))
