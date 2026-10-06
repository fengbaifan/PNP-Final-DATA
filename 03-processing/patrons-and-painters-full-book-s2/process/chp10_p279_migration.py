"""Controlled S2 migration for printed p.279; dry-run by default."""
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
SEGMENT = "chp-10:10_CHP-10_intro:l43-49"
PREVIOUS = "chp-10:10_CHP-10_intro:l26-41"
NEXT = "chp-10:10_CHP-10_intro:l51-61"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
MAX_CANDIDATE = 8883
BACKUP_SUFFIX = ".bak-s2-chp10-p279-20261002"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREVIOUS_OPEN_ID = "st-chp10-p278-manchester-sets-pellegrini-opera-scenes"


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


def backup(path: Path):
    target = Path(str(path) + BACKUP_SUFFIX)
    if target.exists():
        raise SystemExit(f"backup already exists: {target}")
    shutil.copy2(path, target)
    return target


source_bytes = SOURCE.read_bytes()
if hashlib.sha256(source_bytes).hexdigest() != ASSET_SHA:
    raise SystemExit("Chapter 10 intro source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[42].strip() != "[Page 279]" or not source_lines[43].startswith("decorate his mansions"):
    raise SystemExit("expected p.279 source text changed")
if "the two Venetian artists" not in source_lines[43] or "Sir Andrew" not in source_lines[44]:
    raise SystemExit("expected p.279 artist/collector text changed")
if not source_lines[48].startswith("In 1712 Pellegrini and Marco Ricci quarrelled"):
    raise SystemExit("expected p.279 closing paragraph changed")

segment_rows = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segment_rows}
segment_meta = segment_by_id.get(SEGMENT)
previous_meta = segment_by_id.get(PREVIOUS)
next_meta = segment_by_id.get(NEXT)
if not segment_meta or not previous_meta or not next_meta:
    raise SystemExit("expected p.278/p.279/p.280 source segments missing")
if segment_meta.get("asset_sha256") != ASSET_SHA:
    raise SystemExit("p.279 segment asset hash mismatch")
segment_text = "\n".join(source_lines[segment_meta["line_start"] - 1 : segment_meta["line_end"]])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment_meta.get("sha256"):
    raise SystemExit("p.279 source segment content hash mismatch")

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
for segment_id, expected in {
    PREVIOUS: ("reviewed", "partial"),
    SEGMENT: ("queued", "pending"),
    NEXT: ("queued", "pending"),
}.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")
if PREVIOUS_OPEN_ID not in statement_ids:
    raise SystemExit("p.278 open Manchester commission statement missing")

E = {
    "pellegrini": "cand-1870",
    "marco_ricci": "cand-2149",
    "sebastiano_ricci": "cand-2154",
    "vanbrugh": "cand-2690",
    "carlisle": "cand-0559",
    "fountaine": "cand-1060",
    "motteux": "cand-1711",
    "hogarth": "cand-1301",
    "tiepolo": "cand-2569",
    "veronese": "cand-2755",
    "manchester": "cand-1504",
    "portland": "cand-1979",
    "venetian_artists": "cand-8104",
    "english_patrons": "cand-8863",
    "england": "cand-4439",
    "italy": "cand-3461",
    "europe": "cand-3462",
    "versailles_model": "cand-7162",
}
for key, candidate_id in E.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("arlington_street", "Arlington Street residence of Lord Manchester (p.279)", "place", "One of Manchester's mansions that Pellegrini and Marco Ricci were set to decorate; precise building name and extent are not supplied.", 44),
    ("kimbolton", "Kimbolton residence of Lord Manchester, rebuilt by Vanbrugh (p.279)", "place", "One of Manchester's mansions; distinguish the named residence from the town and from the wider group of country houses.", 44),
    ("huntingdonshire", "Huntingdonshire named for Lord Manchester's Kimbolton residence (p.279)", "place", "County locator in the source; this is not an independently verified modern administrative boundary claim.", 44),
    ("yorkshire", "Yorkshire, location of Lord Carlisle's country house (p.279)", "place", "Regional location supplied in Haskell's account of Vanbrugh's country-house project.", 44),
    ("castle_howard", "Castle Howard, country house for Lord Carlisle (p.279)", "place", "The passage first describes Vanbrugh's house for Carlisle and then names Castle Howard as the artists' point of departure; preserve that local identification for later S3 review.", 44),
    ("norfolk", "Norfolk, location of Narford Hall (p.279)", "place", "County named after the Narford Hall reference.", 45),
    ("narford_hall", "Narford Hall, country seat of Sir Andrew Fountaine (p.279)", "place", "Named country seat and destination of the two Venetian artists in Haskell's account.", 45),
    ("manchester_mansions", "Lord Manchester's mansions at Arlington Street and Kimbolton (p.279)", "place", "A collective reference to two residences in the p.278–279 sentence; do not treat as a single building.", 44),
    ("pellegrini_motteux_drawing", "Pellegrini's lively informal drawing of Pierre Motteux (p.279)", "work", "Drawing described by Haskell; no collection, date, or surviving-work identity is supplied here.", 48),
    ("pellegrini_work_group", "Pellegrini's mythologies, histories, capricci and portraits described on p.279", "work", "Unspecified group of works in named genres; the passage describes a body of production rather than identifying individual paintings.", 47),
    ("seventeenth_century_stolidity", "Seventeenth-century stolidity said to inhibit Pellegrini's achievement (p.279)", "term", "Haskell's metaphorical characterization; retain as an interpretation, not a measured property of seventeenth-century painting.", 47),
    ("pellegrini_new_style", "New style of Pellegrini's English-period painting (p.279)", "term", "Haskell's stylistic characterization, described as weightless and sensual yet sometimes clumsy or melodramatic.", 47),
    ("english_society", "Nature of English society as interpreted through Pellegrini's drawing of Motteux (p.279)", "term", "A social interpretation attributed to Haskell's account of the drawing and Van Dyck's portraits.", 48),
    ("english_atmosphere", "Comparatively uninhibited atmosphere of England credited with supporting Pellegrini's innovations (p.279)", "term", "Haskell's cultural explanation; distinguish this social atmosphere from England as a polity.", 48),
    ("venetian_senators", "Venetian Senators as a contrasting portrait subject group (p.279)", "term", "Collective social/political subject category in Haskell's comparison; not a named formal organization.", 48),
    ("english_theatrical_group", "Theatrical group circulating around Lord Manchester (unnamed, p.279)", "term", "Unnamed social circle in which Pierre Motteux moved; keep distinct from Manchester's wider circle and Whig noblemen.", 48),
    ("conversation_pieces", "English conversation-piece painting tradition referenced on p.279", "term", "Genre Haskell says the drawing anticipates; no specific work is identified by this phrase.", 48),
    ("marco_musical_groups", "Marco Ricci's half-caricatured musical groups mentioned on p.279", "work", "Unnamed group of works; the passage does not identify individual compositions or surviving objects.", 48),
    ("pellegrini_marco_duo", "Pellegrini and Marco Ricci as the two Venetian artists moving between English patrons (p.278–279)", "term", "A source-local collective with identifiable members, used where the passage says 'the two Venetian artists' or 'both'.", 44),
    ("marco_sebastiano_duo", "Marco and Sebastiano Ricci as the two men returning to work in England (p.279)", "term", "A source-local collective distinct from Pellegrini and Marco Ricci; preserve the kinship and group boundary stated in the text.", 49),
    ("italian_autocratic_rulers", "Powerful autocratic rulers of northern and central Italy described as Sebastiano Ricci's early patrons (p.279)", "term", "Unspecified patron group. Distinct from the South German/Austrian princes on p.278.", 49),
    ("sebastiano_absorbed_styles", "Varied artistic styles absorbed by Sebastiano Ricci through travel (p.279)", "term", "A source-level description of the styles Sebastiano encountered and displayed; distinct from Pellegrini's later English-period style.", 49),
    ("pellegrini_ricci_quarrel", "Pellegrini and Marco Ricci's quarrel in 1712 (p.279)", "event", "Event as dated by Haskell; cause and details are not supplied in this passage.", 49),
    ("rabelais", "Rabelais (surname only), named as a subject translated by Pierre Motteux (p.279)", "person", "The passage supplies only the surname; do not infer a full name at S2.", 48),
    ("cervantes", "Cervantes (surname only), named as a subject translated by Pierre Motteux (p.279)", "person", "The passage supplies only the surname; do not infer a full name at S2.", 48),
    ("van_dyck", "Van Dyck (name as printed), invoked through his portraits on p.279", "person", "Artist named through his portraits; full identity and alignment remain for S3.", 48),
]
new_candidates = []
C = {}
for offset, (key, name, kind, detail, source_line) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids or any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate ID/natural key exists: {candidate_id} {name}")
    C[key] = candidate_id
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

line_offsets = {}
offset = 0
for line_no in range(segment_meta["line_start"], segment_meta["line_end"] + 1):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1
new_mentions = []


def add_mention(local_id, line_no, surface, candidate_id, note, occurrence=0):
    mention_id = f"m-chp10-p279-{local_id}"
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    known = candidate_ids | {row["candidate_id"] for row in new_candidates}
    if candidate_id not in known:
        raise SystemExit(f"mention references missing candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
    positions, start = [], 0
    while True:
        at = line.find(surface, start)
        if at < 0:
            break
        positions.append(at)
        start = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}; line={line!r}")
    start_char = line_offsets[line_no] + positions[occurrence]
    end_char = start_char + len(surface)
    if segment_text[start_char:end_char] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
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
    ("mansions", 44, "mansions", "manchester_mansions", "Continuation of the p.278 sentence; 'his' refers to Lord Manchester."),
    ("arlington", 44, "Arlington Street", "arlington_street", "Named Manchester residence."),
    ("kimbolton", 44, "Kimbolton", "kimbolton", "Named Manchester residence."),
    ("huntingdonshire", 44, "Huntingdonshire", "huntingdonshire", "County locator for Kimbolton."),
    ("vanbrugh", 44, "Vanbrugh", "vanbrugh", "Reuse the indexed architect candidate."),
    ("same_architect", 44, "The same architect", "vanbrugh", "Refers to Vanbrugh in the preceding clause."),
    ("yorkshire", 44, "Yorkshire", "yorkshire", "Regional location of the country house."),
    ("country_house", 44, "a country house", "castle_howard", "Unnamed building described before it is later named Castle Howard."),
    ("versailles", 44, "Versailles", "versailles_model", "Architectural model named in comparison; do not treat it as the site of Lord Carlisle's country house."),
    ("carlisle", 44, "Lord Carlisle", "carlisle", "Reuse the p.278 index candidate."),
    ("he_carlisle", 44, "He", "carlisle", "Pronoun refers to Lord Carlisle."),
    ("venetian_artists", 44, "the two Venetian artists", "pellegrini_marco_duo", "The local antecedents are Pellegrini and Marco Ricci from p.278."),
    ("castle_howard", 44, "Castle Howard", "castle_howard", "Named point of departure for the artists."),
    ("narford_hall", 44, "Narford Hall", "narford_hall", "Destination of the artists' move."),
    ("norfolk", 45, "Norfolk", "norfolk", "County location for Narford Hall."),
    ("english_patrons", 45, "their English patrons", "english_patrons", "Their refers to the two Venetian artists; group label reused from p.278."),
    ("sir_andrew", 45, "Sir Andrew", "fountaine", "Begins the indexed name completed on the next source line."),
    ("fountaine", 46, "Fountaine", "fountaine", "Completes Sir Andrew Fountaine."),
    ("europe", 46, "Europe", "europe", "Destination region in the account of his travels."),
    ("england_47", 47, "England", "england", "Named setting of Pellegrini's stylistic change."),
    ("pellegrini_47", 47, "Pellegrini", "pellegrini", "Reuse the indexed person candidate."),
    ("stolidity", 47, "seventeenth-century stolidity", "seventeenth_century_stolidity", "Haskell's metaphorical characterization of what had inhibited Pellegrini."),
    ("achievement", 47, "his already adventurous achievement", "pellegrini", "His refers to Pellegrini; this is authorial evaluation, not a separate work."),
    ("work_genres", 47, "mythologies, histories, capricci and portraits", "pellegrini_work_group", "Genres for an unnamed group of Pellegrini works."),
    ("new_style", 47, "a new style", "pellegrini_new_style", "Haskell's description of the English-period work."),
    ("sebastiano_47", 47, "Sebastiano Ricci", "sebastiano_ricci", "Reuse the indexed person candidate."),
    ("tiepolo", 47, "Tiepolo", "tiepolo", "Named as a later comparison."),
    ("veronese", 47, "Veronese", "veronese", "Named as a model in the description of the musicians."),
    ("england_48", 48, "England", "england", "Setting in Haskell's account of Pellegrini's new style."),
    ("uninhibited_atmosphere", 48, "uninhibited atmosphere of England", "english_atmosphere", "Haskell's social-cultural explanation, not England as a polity."),
    ("van_dyck", 48, "Van Dyck", "van_dyck", "Artist named through his portraits."),
    ("portraits", 48, "portraits", "van_dyck", "Portraits by Van Dyck; not an individual work candidate."),
    ("venetian_senators", 48, "Venetian Senators", "venetian_senators", "Collective portrait subjects contrasted with Van Dyck's portraits."),
    ("him_pellegrini", 48, "him", "pellegrini", "Pronoun refers to Pellegrini."),
    ("he_pellegrini", 48, "He", "pellegrini", "Pronoun refers to Pellegrini."),
    ("motteux", 48, "Pierre Motteux", "motteux", "Reuse the indexed person candidate."),
    ("rabelais", 48, "Rabelais", "rabelais", "Translator's named subject; full identity remains a provisional candidate."),
    ("cervantes", 48, "Cervantes", "cervantes", "Translator's named subject; full identity remains a provisional candidate."),
    ("theatrical_group", 48, "the theatrical group", "english_theatrical_group", "Unnamed social circle around Lord Manchester."),
    ("manchester", 48, "Lord Manchester", "manchester", "Reuse the indexed person candidate."),
    ("conversation_pieces", 48, "conversation pieces", "conversation_pieces", "Named English painting genre/tradition."),
    ("marco_ricci_48", 48, "Marco Ricci", "marco_ricci", "Reuse the indexed person candidate."),
    ("musical_groups", 48, "musical groups", "marco_musical_groups", "Unnamed group of works attributed to Marco Ricci."),
    ("hogarth", 48, "Hogarth", "hogarth", "Reuse the indexed person candidate."),
    ("pellegrini_49", 49, "Pellegrini", "pellegrini", "Reuse the indexed person candidate."),
    ("marco_ricci_49", 49, "Marco Ricci", "marco_ricci", "Reuse the indexed person candidate."),
    ("quarrel", 49, "quarrelled", "pellegrini_ricci_quarrel", "Verbal event reference; the cause is not specified."),
    ("both", 49, "Both", "pellegrini_marco_duo", "Pronoun refers to Pellegrini and Marco Ricci."),
    ("england_49", 49, "England", "england", "Destination left by both artists in 1712."),
    ("marco_return", 49, "Marco", "marco_ricci", "Short form refers to Marco Ricci."),
    ("sebastiano_uncle", 49, "Sebastiano", "sebastiano_ricci", "Named as Marco Ricci's uncle; relationship claim retained as reported by Haskell."),
    ("two_men", 49, "the two men", "marco_sebastiano_duo", "Refers to Marco Ricci and Sebastiano Ricci, not to Pellegrini and Marco Ricci."),
    ("sebastiano_old", 49, "Sebastiano", "sebastiano_ricci", "Second occurrence; refers to Sebastiano Ricci." , 1),
    ("early_patrons", 49, "His early patrons", "italian_autocratic_rulers", "His refers to Sebastiano Ricci."),
    ("northern_central_italy", 49, "northern and central Italy", "italy", "Source region within Italy; no separate regional candidates introduced here."),
    ("his_travels", 49, "his extensive travels", "sebastiano_ricci", "His refers to Sebastiano Ricci."),
    ("his_styles", 49, "a wide variety of styles", "sebastiano_absorbed_styles", "Styles absorbed by Sebastiano Ricci through travel."),
    ("he_innovator", 49, "he too", "sebastiano_ricci", "Pronoun refers to Sebastiano Ricci."),
    ("pellegrini_contrast", 49, "Pellegrini’s", "pellegrini", "Comparison point in Haskell's contrast of artistic manners."),
    ("his_manner", 49, "his manner", "sebastiano_ricci", "His refers to Sebastiano Ricci."),
    ("portland", 49, "Lord Portland", "portland", "Reuse the index candidate; statement remains open across the page break."),
]
for spec in MENTION_SPECS:
    local_id, line_no, surface, key, note, *occurrence = spec
    add_mention(local_id, line_no, surface, C[key] if key in C else E[key], note, occurrence[0] if occurrence else 0)

new_statements = []


def quote_between(first: str, last: str):
    start = segment_text.find(first)
    if start < 0:
        raise SystemExit(f"quote start absent: {first!r}")
    end_start = segment_text.find(last, start)
    if end_start < 0:
        raise SystemExit(f"quote end absent after {first!r}: {last!r}")
    return segment_text[start : end_start + len(last)]


def add_statement(sid, line_start, line_end, subject, obj, predicate, quote, claim, qualification,
                  refs=(), relation=False, footnote=None, cross=(), previous_cross=(), continuation_of=None,
                  speaker="Haskell", text_layer="authorial narrative", ocr=()):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    if quote not in segment_text:
        raise SystemExit(f"quote not anchored in p.279 source segment: {sid}")
    linked = set(refs) | {value for value in (subject, obj) if value}
    known = candidate_ids | {row["candidate_id"] for row in new_candidates}
    if not linked <= known:
        raise SystemExit(f"unknown candidate in {sid}: {sorted(linked - known)}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 279,
        "pdf_physical_page": 4,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": sorted(linked),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if footnote is not None:
        qualifiers.update({"footnote_marker": footnote, "footnote_text_pending": True, "footnote_link_status": "pending_source_migration"})
    references = []
    references.extend({"segment_id": NEXT, "source_line_start": start, "source_line_end": end} for start, end in cross)
    references.extend({"segment_id": PREVIOUS, "source_line_start": start, "source_line_end": end} for start, end in previous_cross)
    if references:
        qualifiers["cross_reference_segments"] = references
    if continuation_of:
        qualifiers["continuation_of_statement_id"] = continuation_of
    if ocr:
        qualifiers["ocr_corrections"] = [
            {"source_file": SOURCE_FILE, "source_line": line_no, "ocr": raw, "print": printed, "basis": "CHP-10.pdf physical page 4."}
            for line_no, raw, printed in ocr
        ]
    new_statements.append({
        "statement_id": sid,
        "segment_id": SEGMENT,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "source_file": SOURCE_FILE,
        "origin": "book",
    })


add_statement(
    "st-chp10-p279-pellegrini-manchester-decorate-mansions", 44, 44, E["pellegrini"], C["manchester_mansions"],
    "manchester_set_pellegrini_to_decorate_his_mansions_after_the_opera_scenes",
    quote_between("decorate his mansions", "Vanbrugh.1"),
    "Continuing the p.278 sentence, Haskell says Lord Manchester set Pellegrini to decorate his Arlington Street and Kimbolton mansions after the opera scenes.",
    "The artist and owner are resolved from p.278 L40–41; 'his' means Lord Manchester. The sentence reports an assignment, not proof of completion. Footnote 1 is pending the later notes segment.",
    [E["manchester"], E["marco_ricci"], E["vanbrugh"], C["arlington_street"], C["kimbolton"]], True, 1,
    previous_cross=[(40, 41)],
)
add_statement(
    "st-chp10-p279-marco-ricci-manchester-decorate-mansions", 44, 44, E["marco_ricci"], C["manchester_mansions"],
    "manchester_set_marco_ricci_to_decorate_his_mansions_after_the_opera_scenes",
    quote_between("decorate his mansions", "Vanbrugh.1"),
    "Continuing the p.278 sentence, Haskell says Lord Manchester set Marco Ricci to decorate his Arlington Street and Kimbolton mansions after the opera scenes.",
    "The artist and owner are resolved from p.278 L40–41; 'his' means Lord Manchester. The sentence reports an assignment, not proof of completion. Footnote 1 is pending the later notes segment.",
    [E["manchester"], E["pellegrini"], E["vanbrugh"], C["arlington_street"], C["kimbolton"]], True, 1,
    previous_cross=[(40, 41)],
)
add_statement(
    "st-chp10-p279-vanbrugh-carlisle-castle-howard", 44, 44, E["vanbrugh"], C["castle_howard"],
    "vanbrugh_erected_country_house_for_lord_carlisle_in_yorkshire",
    quote_between("The same architect", "Castle Howard"),
    "Haskell says Vanbrugh had for some years been erecting a country house in Yorkshire for Lord Carlisle, later named in the passage as Castle Howard.",
    "The house is described as palatial as a German imitation of Versailles; this is Haskell's comparison, not an independently measured architectural classification.",
    [E["carlisle"], C["yorkshire"], E["versailles_model"]], True,
)
add_statement(
    "st-chp10-p279-carlisle-employs-pellegrini", 44, 44, E["carlisle"], E["pellegrini"],
    "lord_carlisle_extensively_employed_pellegrini",
    quote_between("He, too, extensively employed", "Castle Howard"),
    "Haskell says Lord Carlisle extensively employed Pellegrini.",
    "'He' refers to Lord Carlisle; 'the two Venetian artists' are Pellegrini and Marco Ricci as established on p.278. The wording does not specify each commission.",
    [E["marco_ricci"], C["pellegrini_marco_duo"]], True,
)
add_statement(
    "st-chp10-p279-carlisle-employs-marco-ricci", 44, 44, E["carlisle"], E["marco_ricci"],
    "lord_carlisle_extensively_employed_marco_ricci",
    quote_between("He, too, extensively employed", "Castle Howard"),
    "Haskell says Lord Carlisle extensively employed Marco Ricci.",
    "'He' refers to Lord Carlisle; 'the two Venetian artists' are Pellegrini and Marco Ricci as established on p.278. The wording does not specify each commission.",
    [E["pellegrini"], C["pellegrini_marco_duo"]], True,
)
add_statement(
    "st-chp10-p279-venetian-artists-move-castle-howard-narford", 44, 45, C["pellegrini_marco_duo"], C["narford_hall"],
    "pellegrini_and_marco_ricci_moved_from_castle_howard_to_narford_hall",
    quote_between("the two Venetian artists who", "Norfolk"),
    "Haskell says the two Venetian artists moved from Castle Howard to Narford Hall in Norfolk.",
    "The local antecedent is Pellegrini and Marco Ricci; the group candidate preserves the plural wording. The move is reported by Haskell and is not independently checked here.",
    [E["pellegrini"], E["marco_ricci"], C["castle_howard"], C["norfolk"]], True,
)
add_statement(
    "st-chp10-p279-narford-seat-fountaine", 45, 46, C["narford_hall"], E["fountaine"],
    "narford_hall_was_fountaines_country_seat",
    quote_between("the country seat", "Europe.2"),
    "Haskell identifies Narford Hall as the country seat of Sir Andrew Fountaine.",
    "Local source statement; place/person identity remains subject to global S3 alignment. Footnote 2 is pending the later notes segment.",
    [C["norfolk"]], True, 2,
)
add_statement(
    "st-chp10-p279-fountaine-collector-traveller", 46, 46, E["fountaine"], None,
    "fountaine_was_a_rich_collector_connoisseur_and_wide_traveller",
    quote_between("a rich collector", "Europe.2"),
    "Haskell describes Fountaine as a rich collector and connoisseur who had travelled widely in Europe.",
    "This is the author's description; the cited note is a source trail and not external verification.",
    [E["europe"]], footnote=2,
)
add_statement(
    "st-chp10-p279-pellegrini-sheds-stolidity", 47, 47, E["pellegrini"], C["seventeenth_century_stolidity"],
    "pellegrini_shed_last_fragments_of_seventeenth_century_stolidity_in_england",
    quote_between("In England Pellegrini", "adventurous achievement."),
    "Haskell says Pellegrini shed the last fragments of seventeenth-century stolidity that had inhibited his already adventurous achievement in England.",
    "Metaphorical art-historical interpretation by Haskell; do not treat 'stolidity' as a separately verified period fact.",
    [E["england"]],
)
add_statement(
    "st-chp10-p279-pellegrini-new-style", 47, 47, E["pellegrini"], C["pellegrini_new_style"],
    "pellegrini_created_new_style_in_mythologies_histories_capricci_and_portraits",
    quote_between("In a series of mythologies", "free of tensions."),
    "Haskell says a new style emerged in Pellegrini's mythologies, histories, capricci and portraits, describing it as weightless and sensual, sometimes clumsy and melodramatic, and nearly always free of tensions.",
    "Retains Haskell's evaluative language and does not assign these traits to an individual painting.",
    [C["pellegrini_work_group"]],
)
add_statement(
    "st-chp10-p279-pellegrini-palette-and-motifs", 47, 47, E["pellegrini"], C["pellegrini_new_style"],
    "haskell_describes_pellegrini_painting_with_specific_colour_and_figure_motifs",
    quote_between("Rose-pink plumes", "painting."),
    "Haskell characterizes Pellegrini's painting through rose-pink plumes against blue and feathery-white skies, sparkling light on armour, golden hair, and transparent colour combinations of mauves, greens, reds and silvers.",
    "These are the author's visual descriptions of a generalized body of painting, not identifiers for a particular work.",
    [C["pellegrini_work_group"]],
)
add_statement(
    "st-chp10-p279-england-atmosphere-credit", 48, 48, C["english_atmosphere"], C["pellegrini_new_style"],
    "uninhibited_english_atmosphere_contributed_to_pellegrini_innovations",
    quote_between("Some of the credit", "the comparatively uninhibited atmosphere of England."),
    "Haskell attributes some credit for Pellegrini's innovations to England's comparatively uninhibited atmosphere.",
    "This is Haskell's causal interpretation, not a demonstrated exclusive cause.",
)
add_statement(
    "st-chp10-p279-van-dyck-portraits-influence-pellegrini", 48, 48, C["van_dyck"], E["pellegrini"],
    "van_dyck_portraits_gave_pellegrini_technical_hints_and_social_insight",
    quote_between("The easy elegance", "nature of English society."),
    "Haskell says Van Dyck's portraits gave Pellegrini technical hints and taught him something essential about English society.",
    "This preserves Haskell's account of influence and does not specify an individual Van Dyck portrait. Van Dyck is a body-only candidate pending S3.",
    [C["english_society"], C["venetian_senators"]],
)
add_statement(
    "st-chp10-p279-pellegrini-draws-motteux", 48, 48, E["pellegrini"], C["pellegrini_motteux_drawing"],
    "pellegrini_made_lively_informal_drawing_of_pierre_motteux",
    quote_between("a lively and informal drawing", "Lord Manchester (Plate 46).3"),
    "Haskell says Pellegrini made a lively, informal drawing of Pierre Motteux, who moved in the theatrical group around Lord Manchester.",
    "The drawing is not individually titled or located. Note 3 is pending the later notes segment; Plate 46 is a cross-reference, not a second work assertion.",
    [E["motteux"], C["english_theatrical_group"], E["manchester"]], True, 3,
)
add_statement(
    "st-chp10-p279-motteux-profile", 48, 48, E["motteux"], None,
    "motteux_translated_rabelais_and_cervantes_and_was_journalist_picture_dealer",
    quote_between("the enterprising translator", "Lord Manchester (Plate 46).3"),
    "Haskell describes Motteux as a translator of Rabelais and Cervantes, a journalist, and a picture dealer.",
    "The passage supplies surnames for the translated authors; their full identities in the candidate layer remain provisional until S3.",
    [C["rabelais"], C["cervantes"]],
)
add_statement(
    "st-chp10-p279-drawing-anticipates-conversation-pieces", 48, 48, C["pellegrini_motteux_drawing"], C["conversation_pieces"],
    "pellegrini_drawing_anticipates_english_conversation_piece_observation",
    quote_between("The engagingly", "dear to English society"),
    "Haskell says the drawing's engagingly private and witty observation anticipates the conversation pieces that became dear to English society.",
    "The print scan confirms the single quotation marks around 'private'. Genre-level comparison, not identity of the drawing as a conversation piece.",
    [E["pellegrini"], E["england"]],
)
add_statement(
    "st-chp10-p279-marco-musical-groups-hogarth", 48, 48, E["marco_ricci"], C["marco_musical_groups"],
    "marco_ricci_musical_groups_must_have_fascinated_hogarth",
    quote_between("a vein also exploited by Marco Ricci", "Hogarth (Plate"),
    "Haskell says Marco Ricci exploited this vein in half-caricatured musical groups that must certainly have fascinated Hogarth.",
    "'Must certainly have fascinated' is Haskell's inference, not a documented response by Hogarth. The scan closes the OCR-truncated plate reference as Plate 47; no plate entity is created here.",
    [E["hogarth"], C["conversation_pieces"]], relation=True,
    ocr=[(48, "Hogarth (Plate", "Hogarth (Plate 47).")],
)
add_statement(
    "st-chp10-p279-pellegrini-marco-quarrel-1712", 49, 49, E["pellegrini"], E["marco_ricci"],
    "pellegrini_and_marco_ricci_quarrelled_in_1712",
    quote_between("In 1712", "quarrelled."),
    "Haskell dates a quarrel between Pellegrini and Marco Ricci to 1712.",
    "The cause and details are not supplied. The source OCR inserts an apostrophe between the next sentence and Sebastiano; the print has a sentence break and no apostrophe.",
    [C["pellegrini_ricci_quarrel"]], True,
    ocr=[(49, "work.'Sebastiano", "work. Sebastiano")],
)
add_statement(
    "st-chp10-p279-both-artists-leave-england", 49, 49, C["pellegrini_marco_duo"], E["england"],
    "pellegrini_and_marco_ricci_left_england_after_quarrelling",
    quote_between("Both left England", "within a year"),
    "Haskell says both artists left England after the quarrel.",
    "'Both' refers to Pellegrini and Marco Ricci. The passage does not specify an exact departure date beyond the context of the 1712 quarrel.",
    [E["pellegrini"], E["marco_ricci"], C["pellegrini_ricci_quarrel"]], True,
)
add_statement(
    "st-chp10-p279-marco-returns-with-sebastiano", 49, 49, E["marco_ricci"], E["sebastiano_ricci"],
    "marco_ricci_returned_to_england_with_uncle_sebastiano_within_a_year",
    quote_between("within a year Marco returned", "with his uncle Sebastiano"),
    "Haskell says Marco Ricci returned within a year with his uncle Sebastiano.",
    "'Within a year' is relative to Marco's departure in the prior sentence; the source identifies Sebastiano as his uncle.",
    [E["england"], C["marco_sebastiano_duo"]], True,
)
add_statement(
    "st-chp10-p279-marco-and-sebastiano-back-at-work", 49, 49, C["marco_sebastiano_duo"], None,
    "marco_and_sebastiano_ricci_were_soon_busily_at_work",
    quote_between("the two men were soon", "busily at work."),
    "Haskell says Marco and Sebastiano Ricci were soon busily at work after Marco's return to England.",
    "The source does not specify the work in this clause; the immediate antecedent is Marco and Sebastiano, not Pellegrini and Marco.",
    [E["marco_ricci"], E["sebastiano_ricci"], E["england"]],
)
add_statement(
    "st-chp10-p279-sebastiano-patronage-and-travel", 49, 49, E["sebastiano_ricci"], C["italian_autocratic_rulers"],
    "sebastiano_ricci_early_patrons_were_autocratic_rulers_of_northern_and_central_italy",
    quote_between("Sebastiano belonged", "excessive facility."),
    "Haskell places Sebastiano Ricci in an older generation, says his early patrons were mostly powerful autocratic rulers of northern and central Italy, and says extensive travel exposed him to diverse styles that he could display with excessive facility.",
    "The patrons remain an unnamed collective. 'Excessive facility' is Haskell's evaluative phrasing; it is not converted into an objective assessment.",
    [E["italy"], C["sebastiano_absorbed_styles"]],
)
add_statement(
    "st-chp10-p279-sebastiano-contrasted-with-pellegrini", 49, 49, E["sebastiano_ricci"], E["pellegrini"],
    "sebastiano_was_innovative_but_more_past_tied_taut_solid_and_robust_than_pellegrini",
    quote_between("Though he too could be a bold innovator", "taut, solid and robust."),
    "Haskell says Sebastiano could be a bold innovator, but his manner was more tied to the past and more taut, solid and robust than Pellegrini's.",
    "This is a comparative art-historical judgment by Haskell, not a claim about a particular painting.",
    [C["pellegrini_new_style"]],
)
add_statement(
    "st-chp10-p279-portland-early-employer-open", 49, 49, E["sebastiano_ricci"], E["portland"],
    "lord_portland_was_one_of_sebastiano_riccis_earliest_english_employers",
    quote_between("One of his earliest employers", "Lord Portland, who"),
    "Haskell says Lord Portland was one of Sebastiano Ricci's earliest employers in England.",
    "The sentence continues at p.280 L52; the statement is intentionally open until that segment is processed.",
    [E["england"]], True, cross=[(52, 52)],
)

if set(row["candidate_id"] for row in new_candidates) & candidate_ids:
    raise SystemExit("candidate IDs are not unique")
if set(row["mention_id"] for row in new_mentions) & mention_ids:
    raise SystemExit("mention IDs are not unique")
if set(row["statement_id"] for row in new_statements) & statement_ids:
    raise SystemExit("statement IDs are not unique")

coverage_by_id[PREVIOUS]["migration_status"] = "complete"
coverage_by_id[PREVIOUS]["source_line_ranges"] = "L26-41"
coverage_by_id[PREVIOUS]["note"] = (
    "Printed p.278 body read against CHP-10.pdf physical page 3. Closed p.277 L24's taste-divergence contrast at L27. "
    "Recorded German-court purchases and artist recruitment; Hapsburg summons/employment; Bencovich's ambiguous 'them'; "
    "Diziani's Dresden work; Amigoni at Munich/Nymphenburg; the English/Whig comparison; Manchester's 1709 embassy, social "
    "circle and architect-patronage context; the Duchess's nested music letter; and the assignment of Pellegrini/Ricci to "
    "Scarlatti's Pyrrhus and Demetrius. The p.276 'a year later' departure chronology and p.278 1709 embassy chronology "
    "remain unreconciled. The OCR marker after 'poets' is 6, but the scan prints 5; correction is recorded in S2 only. "
    "Printed p.278 notes 1-6 remain pending at canonical L500-505. The sentence ending 'and then to' is closed by p.279 L44."
)
coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "partial"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L43-49"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.279 body read against CHP-10.pdf physical page 4. Closed p.278 L41's 'and then to' at L44 and recorded "
    "Manchester's continued decoration assignment, Vanbrugh's Castle Howard project for Carlisle, Carlisle's employment "
    "of Pellegrini/Marco Ricci, and the artists' move to Narford Hall, country seat of Andrew Fountaine. Also recorded "
    "Fountaine's profile, Haskell's account of Pellegrini's English-period style, Van Dyck's influence, the Motteux drawing "
    "and theatrical circle, the conversation-piece comparison, Marco Ricci's musical groups, the 1712 quarrel/departure, "
    "Marco's return with uncle Sebastiano, Sebastiano's patronage/style, and Lord Portland as an early employer. Notes 1-3 "
    "remain pending in the later consolidated notes segment. The OCR truncates Plate 47 and inserts punctuation artifacts; "
    "the p.279 scan confirms the reading recorded in S2. The Portland sentence continues at p.280 L52, so this segment is partial."
)
coverage_by_id[NEXT]["note"] = "Next source-order body segment; expected to close p.279's Lord Portland sentence at L52 and the remaining Plate 47 reference if needed."

new_candidates_final = candidates + new_candidates
new_mentions_final = mentions + new_mentions
new_statements_final = statements + new_statements
new_coverage_final = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "APPLY" if __import__("sys").argv[-1:] == ["--apply"] else "DRY-RUN",
    "segment": SEGMENT,
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "candidate_range": [new_candidates[0]["candidate_id"], new_candidates[-1]["candidate_id"]],
    "coverage_updates": {
        PREVIOUS: [coverage_by_id[PREVIOUS]["disposition"], coverage_by_id[PREVIOUS]["migration_status"]],
        SEGMENT: [coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]],
        NEXT: [coverage_by_id[NEXT]["disposition"], coverage_by_id[NEXT]["migration_status"]],
    },
}, ensure_ascii=False, indent=2))

if __import__("sys").argv[-1:] != ["--apply"]:
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup(path)
write_csv_atomic(candidate_path, candidate_fields, new_candidates_final)
write_csv_atomic(mention_path, mention_fields, new_mentions_final)
write_jsonl_atomic(statement_path, new_statements_final)
write_csv_atomic(coverage_path, coverage_fields, new_coverage_final)
print("Applied p.279 S2 migration; backups retained.")
