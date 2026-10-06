"""Controlled S2 migration for printed p.280; dry-run by default."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SEGMENT = "chp-10:10_CHP-10_intro:l51-61"
PREVIOUS = "chp-10:10_CHP-10_intro:l43-49"
NEXT = "chp-10:10_CHP-10_intro:l63-89"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEGMENT_SHA = "877f9ed4cdae9e0e1bc219c8e90b31521e82843d62c83877f5d7a6c2420722c6"
MAX_CANDIDATE = 8909
BACKUP_SUFFIX = ".bak-s2-chp10-p280-20261002"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREVIOUS_OPEN_ID = "st-chp10-p279-portland-early-employer-open"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("Chapter 10 intro source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[50].strip() != "[Page 280]" or not source_lines[51].startswith("had already commissioned paintings from Pellegrini"):
    raise SystemExit("expected p.280 source text changed")
if "Cathode church" not in source_lines[54] or "some'of which" not in source_lines[59]:
    raise SystemExit("expected p.280 OCR text changed")
if not source_lines[60].endswith("Prince Eugene in"):
    raise SystemExit("expected p.280 open Prince Eugene clause changed")

segment_rows = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segment_rows}
segment_meta = segment_by_id.get(SEGMENT)
previous_meta = segment_by_id.get(PREVIOUS)
next_meta = segment_by_id.get(NEXT)
if not segment_meta or not previous_meta or not next_meta:
    raise SystemExit("expected p.279/p.280/p.281 source segments missing")
if segment_meta.get("sha256") != SEGMENT_SHA or segment_meta.get("asset_sha256") != ASSET_SHA:
    raise SystemExit("p.280 source segment hash mismatch")
segment_text = "\n".join(source_lines[segment_meta["line_start"] - 1 : segment_meta["line_end"]])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
    raise SystemExit("p.280 source segment content hash mismatch")

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
    raise SystemExit("p.279 Lord Portland open statement missing")

E = {
    "portland": "cand-1979",
    "pellegrini": "cand-1870",
    "william_iii": "cand-2814",
    "bentinck": "cand-0289",
    "rigaud": "cand-2199",
    "sebastiano_ricci": "cand-2154",
    "burlington": "cand-0470",
    "burlington_chiswick_house": "cand-0471",
    "gay": "cand-1125",
    "bellucci": "cand-0282",
    "sheffield": "cand-0465",
    "james_ii": "cand-1317",
    "england": "cand-4439",
    "italy": "cand-3461",
    "london": "cand-1422",
    "bulstrode_park": "cand-1981",
    "whig_nobility_prev": "cand-8865",
}
for key, candidate_id in E.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("portland_townhouse", "Unidentified London town house of Henry, Duke of Portland (p.280)", "place", "Sebastiano Ricci is said to have painted for this town house; its name and exact location are not supplied.", 53),
    ("portland_portrait", "Portrait of Henry, Duke of Portland by Hyacinthe Rigaud (1699; p.280)", "work", "Portrait mentioned by Haskell; no collection or present location is identified in this segment.", 53),
    ("ascension", "The Ascension (Sebastiano Ricci's Bulstrode Park chapel commission; p.280)", "work", "Named in a group of four works commissioned for Portland's chapel; keep distinct from other works with the same title.", 54),
    ("last_supper", "The Last Supper (Sebastiano Ricci's Bulstrode Park chapel commission; p.280)", "work", "Named in the chapel programme; footnote 3 gives a source trail to an NGA sketch and a Sotheby's sale, neither independently read here.", 54),
    ("baptism", "The Baptism of Christ (Sebastiano Ricci's Bulstrode Park chapel commission; p.280)", "work", "Named across the source line break; footnote 3 reports a 1960 Sotheby's sale, not independent verification.", 54),
    ("visitation", "The Visitation (Sebastiano Ricci's Bulstrode Park chapel commission; p.280)", "work", "Named as one of four paintings commissioned for the chapel; do not merge with other works titled The Visitation.", 55),
    ("bulstrode_program", "Four-painting programme commissioned by Portland for Bulstrode Park chapel (p.280)", "work", "Collective commission comprising The Ascension, The Last Supper, The Baptism of Christ, and The Visitation.", 54),
    ("catholic_church_type", "Catholic church as the general comparison class for Portland's chapel programme (p.280)", "term", "A generic type of religious building in the author's comparison, not the Catholic Church as an institution.", 55),
    ("piccadilly", "Piccadilly, site of Burlington's great mansion (p.280)", "place", "Local address in the source; do not infer a modern exact parcel or building footprint.", 59),
    ("burlington_house", "Burlington House, Lord Burlington's Piccadilly mansion (p.280)", "place", "Local identification of the mansion rebuilt and redecorated by Burlington and named in John Gay's 1715 quotation.", 60),
    ("grand_tour", "Lord Burlington's conventional Grand Tour to Italy before May 1715 (p.280)", "event", "Travel event as described by Haskell; exact itinerary is not supplied in this passage.", 59),
    ("palladianism", "Austere Palladianism that later preoccupied Lord Burlington (p.280)", "term", "Architectural tendency named by Haskell; this passage says Burlington had not yet developed a special interest in it.", 60),
    ("large_italian_paintings", "Large colourful Italian paintings used for interior decoration (p.280)", "term", "Haskell's description of Burlington's decorative preference at this date; not an individual work or national entity.", 60),
    ("ricci_burlington_painting_group", "Sebastiano Ricci's mythological and history paintings installed at Burlington House (p.280)", "work", "Unspecified group of paintings let into walls and ceilings; note 7 qualifies the later transfer to Chiswick as probable.", 60),
    ("chelsea_hospital", "Chelsea Hospital, where Sebastiano Ricci painted a Resurrection fresco (p.280)", "institution", "Named institution described by Haskell as one of England's most national institutions.", 61),
    ("resurrection_fresco", "The Resurrection fresco by Sebastiano Ricci at Chelsea Hospital (p.280)", "work", "Fresco named by Haskell; no individual chapel or surviving state is specified here.", 61),
    ("whig_nobility", "Whig nobility among Sebastiano Ricci's English patrons (p.280)", "term", "Collective patron group in this passage; keep distinct from other Whig groups until S3.", 61),
    ("important_officials", "Important officials among Sebastiano Ricci's English patrons (unnamed group, p.280)", "term", "Unnamed collective patron group; the source does not enumerate members.", 61),
    ("buckingham_house", "Unidentified great London house begun for John Sheffield, Duke of Buckingham, in 1703 (p.280)", "place", "The building is not given a proper name in this passage.", 61),
    ("constitutional_monarchy", "New constitutional monarchy acknowledged by John Sheffield (p.280)", "term", "Political arrangement as characterized by Haskell; retain the source's wording and do not infer a formal constitutional document.", 61),
    ("james_daughter", "Unidentified illegitimate daughter of James II chosen by John Sheffield as his third wife (p.280)", "person", "Daughter is unnamed in this segment; preserve the stated kinship and marital relation without adding identity.", 61),
    ("orange_cause", "Orange cause to which William Bentinck's loyalty was directed (p.280)", "term", "Political cause as named in the source; no further institutional identity is inferred here.", 53),
    ("prince_eugene", "Prince Eugene named as the source of a description of John Sheffield (p.280)", "person", "Body-only candidate; the quoted description continues at p.281 and identity alignment remains for S3.", 61),
    ("george_vertue", "George Vertue, witness to and critic of Portland's chapel paintings (p.280)", "person", "Named as the observer who saw and praised the paintings; the cited Vertue volume remains pending.", 55),
    ("bentinck_estates", "Vast estates granted to William Bentinck for loyalty to the Orange cause (p.280)", "place", "Collective property reward; no estate is individually identified.", 53),
    ("unnamed_contemporary", "Unidentified contemporary whose opinion of Portland is quoted by Haskell (p.280)", "person", "Speaker is unnamed; preserve the quoted appraisal without assigning an identity.", 53),
    ("bulstrode_chapel", "Chapel in Portland's country house at Bulstrode Park (p.280)", "place", "Architectural interior designated for the four Ricci paintings; distinct from Bulstrode Park as the larger estate.", 53),
    ("buckinghamshire", "Buckinghamshire, county location of Bulstrode Park (p.280)", "place", "Geographic locator supplied in the source; not independently checked here.", 54),
    ("chiswick_place", "Chiswick, location of Lord Burlington's villa (p.280)", "place", "Geographic place named separately from the villa building.", 60),
    ("patron_circles", "Political and patronage circles previously considered by Haskell (p.280)", "term", "Contextual collective referenced by John Sheffield's political position; membership is not enumerated here.", 61),
]
new_candidates = []
C = {}
for offset, (key, name, kind, detail, source_line) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids or any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate ID/natural key exists: {candidate_id} {name}")
    C[key] = candidate_id
    new_candidates.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
        "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT}#L{source_line}",
    })

line_offsets = {}
offset = 0
for line_no in range(segment_meta["line_start"], segment_meta["line_end"] + 1):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1
new_mentions = []


def add_mention(local_id, line_no, surface, candidate_id, note, occurrence=0):
    mention_id = f"m-chp10-p280-{local_id}"
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
        "mention_id": mention_id, "segment_id": SEGMENT, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start_char), "end_char": str(end_char), "note": note,
    })


MENTION_SPECS = [
    ("pellegrini", 52, "Pellegrini", "portland", "Recipient of Portland's earlier commission; linked back to p.279 L49."),
    ("young_man", 52, "This young man", "portland", "Refers to Henry, Duke of Portland, named in the preceding segment."),
    ("william_iii", 53, "William Ill", "william_iii", "S0 OCR reads Ill; the p.280 print scan confirms III."),
    ("bentinck", 53, "William Bentinck", "bentinck", "Reuse the indexed candidate."),
    ("orange_cause", 53, "the Orange cause", "orange_cause", "Political cause named in the source."),
    ("estates", 53, "vast estates", "bentinck_estates", "Collective reward described in the source; no individual estate is identified."),
    ("henry", 53, "Henry", "portland", "Refers to the young man, Henry, Duke of Portland."),
    ("portland_title", 53, "the Portland title", "portland", "Title succession stated for 1709."),
    ("first_duke", 53, "first Duke", "portland", "Portland was created first Duke in 1716."),
    ("his_portrait", 53, "his portrait", "portland_portrait", "Portrait of Portland referred to before the painter is named."),
    ("rigaud", 53, "Rigaud", "rigaud", "Reuse indexed Hyacinthe Rigaud candidate."),
    ("work_portrait", 53, "a work", "portland_portrait", "Refers to Rigaud's portrait of Portland."),
    ("contemporary_opinion", 53, "a contemporary", "unnamed_contemporary", "Unnamed contemporary whose opinion Haskell quotes."),
    ("he_contemporary", 53, "he", "portland", "Pronoun inside the quoted contemporary opinion refers to Portland."),
    ("he_commissioned", 53, "He", "portland", "Refers to Henry, Duke of Portland."),
    ("ricci_commission", 53, "Ricci", "sebastiano_ricci", "The artist named by surname; local context and index distinguish Sebastiano."),
    ("town_house", 53, "his town house", "portland_townhouse", "Portland's unnamed town house."),
    ("chapel", 53, "the chapel", "bulstrode_chapel", "Refers to the chapel in Portland's country house."),
    ("country_house", 53, "his country house", "bulstrode_park", "Portland's country house, named on the following source line."),
    ("bulstrode_park", 54, "Bulstrode Park", "bulstrode_park", "Reuse the indexed Portland sub-entry."),
    ("buckinghamshire", 54, "Buckinghamshire", "buckinghamshire", "County locator for Bulstrode Park."),
    ("ascension", 54, "The Ascension", "ascension", "First of four paintings in the chapel programme."),
    ("last_supper", 54, "The Last Supper", "last_supper", "Second named painting in the chapel programme."),
    ("baptism", 54, "The Baptism of", "baptism", "Title continues as 'Christ' at p.280 L55."),
    ("baptism_christ", 55, "Christ", "baptism", "Completes The Baptism of Christ across the OCR line break."),
    ("visitation", 55, "The Visitation", "visitation", "Fourth named painting in the chapel programme."),
    ("programme", 55, "a programme", "bulstrode_program", "Collective group of the four named chapel paintings."),
    ("cathode", 55, "Cathode", "catholic_church_type", "OCR reads Cathode; the print scan confirms Catholic."),
    ("vertue", 55, "Vertue", "george_vertue", "Witness who saw and praised the paintings; the book citation remains pending."),
    ("the_paintings", 55, "the paintings", "bulstrode_program", "Refers to the named Bulstrode Park chapel programme."),
    ("england_ricci", 56, "England", "england", "Setting for Ricci's employment."),
    ("ricci_again", 56, "Ricci", "sebastiano_ricci", "Refers to Sebastiano Ricci."),
    ("lord_burlington", 56, "Lord", "burlington", "Title begins at L56; Burlington completes it on L57."),
    ("burlington", 57, "Burlington", "burlington", "Completes Lord Burlington."),
    ("patron", 57, "the most influential patron", "burlington", "Haskell's assessment of Burlington's later influence."),
    ("peer", 58, "the young peer", "burlington", "Refers to Lord Burlington."),
    ("grand_tour", 59, "Grand Tour", "grand_tour", "Burlington's trip to Italy, described as conventional."),
    ("italy", 59, "Italy", "italy", "Destination of Burlington's Grand Tour."),
    ("great_mansion", 59, "his great mansion", "burlington_house", "Refers to Burlington House, named later in the same source line."),
    ("piccadilly", 60, "Piccadilly", "piccadilly", "Location of Burlington's mansion."),
    ("ricci_venetian", 60, "the Venetian artist", "sebastiano_ricci", "Refers to Sebastiano Ricci."),
    ("palladianism", 60, "Palladianism", "palladianism", "Architectural tendency Burlington was not yet especially interested in."),
    ("him_burlington", 60, "him", "burlington", "Pronoun refers to Lord Burlington."),
    ("nobleman", 60, "any other nobleman of the age", "burlington", "Comparison class for Burlington's decorative preference."),
    ("italian_paintings", 60, "large and colourful Italian paintings", "large_italian_paintings", "Decorative type preferred for interior walls."),
    ("gay_quote", 60, "The wall with animated pictures lives", "burlington_house", "Quoted observation about Burlington House in 1715."),
    ("gay", 60, "Gay", "gay", "Reuse indexed John Gay candidate; quoted source work is unidentified here."),
    ("burlington_house", 60, "Burlington House", "burlington_house", "Named Piccadilly mansion in Gay's 1715 quotation."),
    ("mythological_history_paintings", 60, "mythological-and history paintings", "ricci_burlington_painting_group", "OCR's compound phrase; a group of paintings by Sebastiano Ricci."),
    ("ricci_walls", 60, "Sebastiano Ricci", "sebastiano_ricci", "Artist identified in full."),
    ("burlington_villa", 60, "Burlington’s villa", "burlington_chiswick_house", "Reuse the indexed Burlington sub-entry for the house at Chiswick."),
    ("chiswick", 60, "Chiswick", "chiswick_place", "Place named as the location of Burlington's villa."),
    ("ricci_patrons", 61, "Ricci", "sebastiano_ricci", "Sebastiano Ricci as the subject of the patronage statement."),
    ("whig_nobility", 61, "the Whig nobility", "whig_nobility", "Collective patron group in this passage."),
    ("officials", 61, "important officials", "important_officials", "Unnamed collective patron group."),
    ("leaving", 61, "leaving", "sebastiano_ricci", "Ricci left England in 1716; departure is temporally qualified."),
    ("resurrection", 61, "The Resurrection", "resurrection_fresco", "Fresco title at Chelsea Hospital."),
    ("national_institution", 61, "that most national of institutions", "chelsea_hospital", "Authorial description of Chelsea Hospital."),
    ("chelsea_hospital", 61, "the Chelsea Hospital", "chelsea_hospital", "Named institution and site of the fresco."),
    ("departure", 61, "his departure", "sebastiano_ricci", "His refers to Ricci's departure from England in 1716."),
    ("bellucci", 61, "Antonio Bellucci", "bellucci", "Reuse the indexed person candidate."),
    ("england_bellucci", 61, "England", "england", "Destination of Bellucci's arrival."),
    ("first_patron", 61, "his first patrons", "bellucci", "His refers to Bellucci."),
    ("a_man", 61, "a man", "sheffield", "The man is identified immediately afterwards as John Sheffield."),
    ("ricci_employment", 61, "Sebastiano Ricci", "sebastiano_ricci", "The employment Bellucci's patron had previously given to Ricci."),
    ("sheffield", 61, "John Sheffield", "sheffield", "Reuse indexed Duke of Buckingham candidate."),
    ("duke_buckingham", 61, "Duke of Buckingham", "sheffield", "Title held since 1703."),
    ("year_1703", 61, "1703", "sheffield", "Year Sheffield became Duke and began his London house."),
    ("great_london_house", 61, "his great London house", "buckingham_house", "Unidentified building begun in 1703."),
    ("london", 61, "London", "london", "City locator for Sheffield's unnamed house."),
    ("circles", 61, "the circles", "patron_circles", "Refers to the patronage and political circles previously considered; membership is not repeated here."),
    ("acknowledged", 61, "he acknowledged", "sheffield", "Pronoun refers to John Sheffield."),
    ("constitutional_monarchy", 61, "the new constitutional monarchy", "constitutional_monarchy", "Political system acknowledged by Sheffield."),
    ("supporter", 61, "he had been a staunch supporter", "sheffield", "Pronoun refers to John Sheffield."),
    ("james_ii", 61, "James II", "james_ii", "Reuse indexed person candidate."),
    ("daughter", 61, "one of whose illegitimate daughters", "james_daughter", "Unnamed daughter of James II."),
    ("chosen", 61, "he had chosen", "sheffield", "Pronoun refers to John Sheffield."),
    ("third_wife", 61, "his third wife", "james_daughter", "The unnamed daughter was chosen as Sheffield's third wife."),
    ("prince_eugene", 61, "Prince Eugene", "prince_eugene", "Person who begins a description of Sheffield; the source continues at p.281."),
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
                  refs=(), relation=False, footnote=None, cross=(), previous_cross=(),
                  continuation_of=None, speaker="Haskell", text_layer="authorial narrative", ocr=()):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    if quote not in segment_text:
        raise SystemExit(f"quote not anchored in p.280 source segment: {sid}")
    linked = set(refs) | {value for value in (subject, obj) if value}
    known = candidate_ids | {row["candidate_id"] for row in new_candidates}
    if not linked <= known:
        raise SystemExit(f"unknown candidate in {sid}: {sorted(linked - known)}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "printed_page": 280, "pdf_physical_page": 5, "claim": claim,
        "speaker": speaker, "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": sorted(linked),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if footnote is not None:
        qualifiers.update({"footnote_marker": footnote, "footnote_text_pending": True, "footnote_link_status": "pending_source_migration"})
    refs_out = []
    refs_out.extend({"segment_id": NEXT, "source_line_start": start, "source_line_end": end} for start, end in cross)
    refs_out.extend({"segment_id": PREVIOUS, "source_line_start": start, "source_line_end": end} for start, end in previous_cross)
    if refs_out:
        qualifiers["cross_reference_segments"] = refs_out
    if continuation_of:
        qualifiers["continuation_of_statement_id"] = continuation_of
    if ocr:
        qualifiers["ocr_corrections"] = [
            {"source_file": SOURCE_FILE, "source_line": line_no, "ocr": raw, "print": printed, "basis": "CHP-10.pdf physical page 5."}
            for line_no, raw, printed in ocr
        ]
    new_statements.append({
        "statement_id": sid, "segment_id": SEGMENT, "subject_candidate_id": subject,
        "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "source_file": SOURCE_FILE, "origin": "book",
    })


add_statement(
    "st-chp10-p280-portland-commissioned-pellegrini", 52, 52, E["portland"], E["pellegrini"],
    "portland_had_already_commissioned_paintings_from_pellegrini",
    quote_between("had already commissioned paintings", "Pellegrini.1"),
    "Haskell says Lord Portland had already commissioned paintings from Pellegrini.",
    "This clause closes the p.279 statement that Portland was an early English employer of Sebastiano Ricci; it is a separate commission fact. Footnote 1 remains pending the later consolidated notes segment.",
    [E["sebastiano_ricci"]], True, 1, previous_cross=[(49, 49)],
)
add_statement(
    "st-chp10-p280-portland-son-of-bentinck", 52, 53, E["portland"], E["bentinck"],
    "henry_portland_was_son_of_william_bentinck",
    quote_between("This young man was the son", "William Bentinck"),
    "Haskell identifies the young Henry, Duke of Portland, as the son of Dutch William Bentinck.",
    "'This young man' refers to Henry, Duke of Portland from p.279; retain the source's identification and leave global alignment to S3.",
    [E["william_iii"]], True,
)
add_statement(
    "st-chp10-p280-williamiii-favourite-bentinck", 53, 53, E["william_iii"], E["bentinck"],
    "william_iii_regarded_bentinck_as_great_favourite",
    quote_between("William Ill’s great favourite", "William Bentinck"),
    "Haskell calls William Bentinck a great favourite of William III.",
    "The source gives this as a biographical characterization, without specifying when or in what office the favour operated.",
    relation=True, ocr=[(53, "William Ill’s", "William III’s")],
)
add_statement(
    "st-chp10-p280-bentinck-orange-loyalty-reward", 53, 53, E["bentinck"], C["orange_cause"],
    "bentinck_loyalty_to_orange_cause_rewarded_with_vast_estates",
    quote_between("whose loyalty to the Orange cause", "vast estates.2"),
    "Haskell says Bentinck's loyalty to the Orange cause was rewarded with vast estates.",
    "The estates are not individually identified. Footnote 2 remains pending the later notes segment.",
    [C["bentinck_estates"]], relation=True, footnote=2,
)
add_statement(
    "st-chp10-p280-portland-title-and-biography", 53, 53, E["portland"], None,
    "henry_succeeded_to_portland_title_1709_created_first_duke_1716_and_lived_abroad",
    quote_between("Henry, who succeeded", "abroad"),
    "Haskell says Henry succeeded to the Portland title in 1709, became first Duke in 1716, and had lived a great deal abroad.",
    "Dates and characterization are reported from Haskell's text; the following portrait and contemporary opinion are separate claims.",
)
add_statement(
    "st-chp10-p280-portland-portrait-by-rigaud", 53, 53, E["rigaud"], C["portland_portrait"],
    "rigaud_painted_portlands_portrait_in_1699",
    quote_between("had had his portrait painted by Rigaud in 1699", "1699"),
    "Haskell says Rigaud painted Portland's portrait in 1699.",
    "No collection or present location is supplied; do not conflate with other Rigaud portraits.",
    [E["portland"]], True,
)
add_statement(
    "st-chp10-p280-portland-contemporary-opinion", 53, 53, E["portland"], C["portland_portrait"],
    "portrait_seemed_to_endorse_an_unnamed_contemporarys_opinion_of_portland",
    quote_between("a work that seems", "very affected’"),
    "Haskell says the portrait seems to endorse an unnamed contemporary's opinion that Portland was 'a fine fellow, but very affected'.",
    "The portrait-to-opinion link is explicitly modal ('seems'); the contemporary speaker is unidentified and the appraisal remains quoted opinion.",
    [C["portland_portrait"], C["unnamed_contemporary"]], speaker="unnamed contemporary quoted by Haskell", text_layer="nested quotation with Haskell's framing",
)
add_statement(
    "st-chp10-p280-portland-ricci-townhouse", 53, 53, E["portland"], C["portland_townhouse"],
    "portland_commissioned_ricci_paintings_for_his_town_house",
    quote_between("He commissioned paintings from Ricci", "his town house"),
    "Haskell says Portland commissioned paintings from Sebastiano Ricci for his unnamed town house.",
    "The painter is identified as Sebastiano by the page context and index. The town house is not named.",
    [E["sebastiano_ricci"]], True,
)
add_statement(
    "st-chp10-p280-portland-bulstrode-chapel-programme", 53, 55, E["portland"], C["bulstrode_program"],
    "portland_commissioned_four_ricci_paintings_for_bulstrode_park_chapel",
    quote_between("above all for the chapel", "The Visitation.3"),
    "Haskell says Portland especially commissioned The Ascension, The Last Supper, The Baptism of Christ and The Visitation for the chapel at Bulstrode Park.",
    "The OCR splits The Baptism of Christ across L54–55. Footnote 3 supplies locations for two named works but has not yet been independently read.",
    [E["sebastiano_ricci"], E["bulstrode_park"], C["bulstrode_chapel"], C["buckinghamshire"], C["ascension"], C["last_supper"], C["baptism"], C["visitation"]],
    True, 3,
)
add_statement(
    "st-chp10-p280-portland-programme-catholic-comparison", 55, 55, C["bulstrode_program"], C["catholic_church_type"],
    "bulstrode_chapel_programme_would_not_be_out_of_place_in_any_catholic_church",
    quote_between("Strangely enough this was a programme", "Cathode church."),
    "Haskell says the programme would not have been out of place in a Catholic church.",
    "The print scan confirms Catholic; the source makes a comparison about the programme, not an identity or institutional relation.",
    [E["sebastiano_ricci"]], ocr=[(55, "Cathode", "Catholic")],
)
add_statement(
    "st-chp10-p280-vertue-praises-portland-paintings", 55, 55, E["portland"], C["bulstrode_program"],
    "vertue_saw_paintings_about_twenty_years_later_and_praised_their_invention_and_composition",
    quote_between("When Vertue saw the paintings", "composition of the parts’.4"),
    "Haskell says Vertue saw the paintings about twenty years later and praised their free invention, force of light and shade, and variety and freedom in composition.",
    "The praise is Vertue's quoted response, mediated by Haskell. Footnote 4 is pending the notes segment.",
    [E["bulstrode_park"], C["george_vertue"]], footnote=4, speaker="George Vertue as quoted by Haskell", text_layer="nested quotation",
)
add_statement(
    "st-chp10-p280-ricci-early-burlington-employment", 56, 57, E["sebastiano_ricci"], E["burlington"],
    "ricci_worked_for_lord_burlington_within_months_of_arriving_in_england",
    quote_between("Within a few months", "first half of the century.5"),
    "Haskell says Ricci was working for Lord Burlington within a few months of arriving in England and describes Burlington as destined to become the most influential patron of the first half of the century.",
    "The employment timing and the author's evaluative prediction are retained together; footnote 5 remains pending the consolidated notes segment.",
    [E["england"]], True, 5,
)
add_statement(
    "st-chp10-p280-burlington-grand-tour-and-mansion", 58, 60, E["burlington"], C["burlington_house"],
    "after_returning_from_grand_tour_in_may_1715_burlington_rebuilt_mansion_and_extensively_employed_ricci",
    quote_between("But it was not until May 1715", "extensive scale.8"),
    "Haskell says Burlington returned from his Grand Tour to Italy and began rebuilding and redecorating his Piccadilly mansion; only then, in May 1715, did he employ Ricci extensively.",
    "The prose date and sequence are preserved as printed. The OCR reads footnote 8 after 'scale'; the scan and note list show marker 6. Footnote 6 remains pending.",
    [E["sebastiano_ricci"], E["italy"], C["grand_tour"], C["piccadilly"]], True, 6,
    ocr=[(60, "extensive scale.8", "extensive scale.6")],
)
add_statement(
    "st-chp10-p280-burlington-decorative-preference", 60, 60, E["burlington"], C["large_italian_paintings"],
    "burlington_not_yet_interested_in_palladianism_and_preferred_large_colourful_italian_interior_paintings",
    quote_between("As yet he had no special interest", "Italian paintings."),
    "Haskell says Burlington had not yet taken a special interest in austere Palladianism and was as keen as other noblemen to decorate his palace interiors with large, colourful Italian paintings.",
    "'Not yet' and 'later to preoccupy him' preserve the change over time; the passage describes a preference, not the exact decoration of every room.",
    [C["palladianism"], E["sebastiano_ricci"]],
)
add_statement(
    "st-chp10-p280-gay-burlington-house-quotation", 60, 60, E["gay"], C["burlington_house"],
    "john_gay_wrote_wall_with_animated_pictures_lives_about_burlington_house_in_1715",
    quote_between("‘The wall with animated pictures lives’", "Burlington House in 1715"),
    "Haskell quotes John Gay's line 'The wall with animated pictures lives' about Burlington House in 1715.",
    "Haskell calls Gay's wording rather clumsy. No poem or publication title is identified in this segment.",
    [C["large_italian_paintings"]], speaker="John Gay as quoted by Haskell", text_layer="nested quotation",
)
add_statement(
    "st-chp10-p280-ricci-paintings-burlington-house-chiswick", 60, 60, E["sebastiano_ricci"], C["ricci_burlington_painting_group"],
    "ricci_mythological_and_history_paintings_installed_at_burlington_house_some_later_transferred_to_chiswick",
    quote_between("a great number of mythological-and history paintings", "Burlington’s villa at Chiswick.7"),
    "Haskell says many mythological and history paintings by Ricci were let into Burlington House walls and ceilings, and that some were later transferred to Burlington's villa at Chiswick.",
    "The quantifier 'some' is preserved. Footnote 7 later qualifies the transfer as probable; the note is pending and the transfer is not independently verified.",
    [C["burlington_house"], E["burlington_chiswick_house"]], True, 7,
    ocr=[(60, "some'of which", "some of which")],
)
add_statement(
    "st-chp10-p280-ricci-patrons-whig-and-officials", 61, 61, E["sebastiano_ricci"], C["whig_nobility"],
    "ricci_had_many_enthusiastic_patrons_among_whig_nobility_and_important_officials",
    quote_between("Ricci had many enthusiastic patrons", "important officials"),
    "Haskell says Ricci had many enthusiastic patrons among the Whig nobility and important officials.",
    "Both patron groups are unnamed here; avoid treating them as a formal organization.",
    [C["important_officials"]],
)
add_statement(
    "st-chp10-p280-ricci-chelsea-resurrection", 61, 61, E["sebastiano_ricci"], C["resurrection_fresco"],
    "ricci_painted_resurrection_fresco_at_chelsea_hospital_before_leaving_england_in_1716",
    quote_between("before leaving in 1716 he painted a fresco", "the Chelsea Hospital"),
    "Haskell says Ricci painted a Resurrection fresco at Chelsea Hospital before leaving England in 1716.",
    "The hospital is described as one of England's most national institutions; the specific site or present state of the fresco is not given.",
    [C["chelsea_hospital"], E["england"]], True,
)
add_statement(
    "st-chp10-p280-bellucci-arrives-after-ricci", 61, 61, E["bellucci"], E["england"],
    "bellucci_arrived_in_england_a_few_months_after_riccis_departure_and_was_well_received",
    quote_between("a few months after his departure", "equally well received."),
    "Haskell says Antonio Bellucci arrived in England a few months after Ricci's departure and was equally well received.",
    "'His departure' refers to Ricci leaving England in 1716; the source does not provide a more exact date.",
    [E["sebastiano_ricci"]], True,
)
add_statement(
    "st-chp10-p280-bellucci-patron-sheffield-also-employed-ricci", 61, 61, E["sheffield"], E["bellucci"],
    "john_sheffield_was_one_of_bellucci_first_patrons_and_had_employed_ricci",
    quote_between("one of his first patrons was a man", "Sebastiano Ricci."),
    "Haskell says one of Bellucci's first patrons had already employed Sebastiano Ricci; he identifies the patron as John Sheffield, Duke of Buckingham.",
    "'His' refers to Bellucci. The sentence connects Sheffield to both painters but does not specify the form or date of either commission.",
    [E["sebastiano_ricci"]], True,
)
add_statement(
    "st-chp10-p280-sheffield-title-house-politics", 61, 61, E["sheffield"], C["buckingham_house"],
    "sheffield_duke_since_1703_began_london_house_and_stood_outside_prior_patron_circles",
    quote_between("John Sheffield, Duke of Buckingham", "considered.8"),
    "Haskell says Sheffield had been Duke of Buckingham since 1703, began building his great London house that year, and stood politically rather outside the circles already discussed.",
    "'Circles' refers to the patron groups in the preceding discussion. The source's note 8 remains pending; it is a source trail, not independent corroboration.",
    [C["whig_nobility"], C["important_officials"]], True, 8,
    ocr=[(61, "biave so far", "have so far")],
)
add_statement(
    "st-chp10-p280-sheffield-acknowledged-monarchy", 61, 61, E["sheffield"], C["constitutional_monarchy"],
    "sheffield_acknowledged_new_constitutional_monarchy",
    quote_between("Though he acknowledged the new", "constitutional monarchy"),
    "Haskell says Sheffield acknowledged the new constitutional monarchy.",
    "Political characterization is kept distinct from his support for James II and his marriage.",
)
add_statement(
    "st-chp10-p280-sheffield-supported-jamesii", 61, 61, E["sheffield"], E["james_ii"],
    "sheffield_had_been_staunch_supporter_of_jamesii",
    quote_between("he had been a staunch supporter", "James II"),
    "Haskell says Sheffield had been a staunch supporter of James II.",
    "This is the author's political characterization; the source does not specify a particular act of support.",
    relation=True,
)
add_statement(
    "st-chp10-p280-sheffield-third-wife-jamesii-daughter", 61, 61, E["sheffield"], C["james_daughter"],
    "sheffield_chose_jamesii_unnamed_illegitimate_daughter_as_third_wife",
    quote_between("one of whose illegitimate daughters", "his third wife."),
    "Haskell says Sheffield chose one of James II's illegitimate daughters as his third wife.",
    "The daughter is unnamed in the source; do not add an identity at S2.",
    [E["james_ii"]], relation=True,
)
add_statement(
    "st-chp10-p280-sheffield-description-open", 61, 61, E["sheffield"], C["prince_eugene"],
    "prince_eugene_description_of_sheffield_begins_and_continues_on_p281",
    quote_between("He was described by Prince Eugene", "Prince Eugene in"),
    "Haskell begins to report a description of Sheffield by Prince Eugene, but the sentence is unfinished at the page break.",
    "No wording or evaluation from Prince Eugene is inferred before p.281 is read.",
    [], True, cross=[(63, 89)], speaker="Haskell reporting Prince Eugene", text_layer="nested report, incomplete",
)

if len({row["candidate_id"] for row in new_candidates}) != len(new_candidates):
    raise SystemExit("duplicate candidate IDs")
if len({row["mention_id"] for row in new_mentions}) != len(new_mentions):
    raise SystemExit("duplicate mention IDs")
if len({row["statement_id"] for row in new_statements}) != len(new_statements):
    raise SystemExit("duplicate statement IDs")

coverage_by_id[PREVIOUS]["migration_status"] = "complete"
coverage_by_id[PREVIOUS]["note"] += " Closed its final Portland clause at p.280 L52; the commission to Pellegrini is recorded in the p.280 segment."
coverage_by_id[SEGMENT]["disposition"] = "reviewed"
coverage_by_id[SEGMENT]["migration_status"] = "partial"
coverage_by_id[SEGMENT]["source_line_ranges"] = "L51-61"
coverage_by_id[SEGMENT]["note"] = (
    "Printed p.280 body read against CHP-10.pdf physical page 5. Closed p.279 L49's Lord Portland sentence at L52 and "
    "recorded Portland's prior Pellegrini commission; Bentinck/William III and Orange-cause context; Portland's title, "
    "Rigaud portrait and attributed contemporary opinion; Ricci's town-house and Bulstrode chapel commissions with four "
    "named works; the Catholic-church comparison and Vertue's praise; Ricci/Burlington employment and the 1715 Piccadilly "
    "redecoration; Palladianism and Italian-painting preference; Gay's quotation and Ricci's Burlington House paintings/"
    "possible later transfer to Chiswick; Ricci's Whig/official patrons, Chelsea Hospital Resurrection fresco, and Bellucci's "
    "arrival/patronage; and John Sheffield's Buckingham title, politics, London house and marriage. OCR corrections are "
    "recorded in S2 only: William Ill→III, Cathode→Catholic, some'of→some of, footnote marker 8→6 after 'scale', and "
    "biave→have; S0 is unchanged. Notes 1-8 remain pending the consolidated notes source segment. The Prince Eugene "
    "description begins at L61 and continues at p.281 L63, so p.280 remains partial."
)
coverage_by_id[NEXT]["note"] = "Next source-order body segment; expected to close the Prince Eugene description begun at p.280 L61 and to supply its wording."

new_candidates_final = candidates + new_candidates
new_mentions_final = mentions + new_mentions
new_statements_final = statements + new_statements
new_coverage_final = [coverage_by_id[row["segment_id"]] for row in coverage]

print(json.dumps({
    "mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
    "segment": SEGMENT,
    "new_candidates": len(new_candidates), "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "candidate_range": [new_candidates[0]["candidate_id"], new_candidates[-1]["candidate_id"]],
    "coverage_updates": {
        PREVIOUS: [coverage_by_id[PREVIOUS]["disposition"], coverage_by_id[PREVIOUS]["migration_status"]],
        SEGMENT: [coverage_by_id[SEGMENT]["disposition"], coverage_by_id[SEGMENT]["migration_status"]],
        NEXT: [coverage_by_id[NEXT]["disposition"], coverage_by_id[NEXT]["migration_status"]],
    },
}, ensure_ascii=False, indent=2))

if sys.argv[-1:] != ["--apply"]:
    raise SystemExit(0)
for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup(path)
write_csv_atomic(candidate_path, candidate_fields, new_candidates_final)
write_csv_atomic(mention_path, mention_fields, new_mentions_final)
write_jsonl_atomic(statement_path, new_statements_final)
write_csv_atomic(coverage_path, coverage_fields, new_coverage_final)
print("Applied p.280 S2 migration; backups retained.")
