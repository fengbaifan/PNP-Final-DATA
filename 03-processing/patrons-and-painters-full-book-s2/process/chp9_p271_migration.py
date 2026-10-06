"""Controlled S2 migration for printed p.271 body; defaults to dry-run."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_sec_ii.md"
SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l38-51"
PREVIOUS_SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l27-36"
NEXT_SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l53-60"
PREVIOUS_VISITOR_STATEMENT_ID = "st-chp9-p270-1742-visitor-description-partial"
EXPECTED_SEGMENT_SHA = "578273f40983a11f02023c2753bbb564ecf08eae523a74fccd1576ab212c487f"
EXPECTED_ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
EXPECTED_MAX_CANDIDATE = 8708
BACKUP_SUFFIX = ".bak-s2-chp9-p271-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(source_bytes).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("section-II source asset has changed")
segments = {row["segment_id"]: row for row in read_jsonl(TABLES / "segments.jsonl")}
for sid, expected in [(SEGMENT_ID, EXPECTED_SEGMENT_SHA)]:
    if segments.get(sid, {}).get("sha256") != expected or segments[sid].get("asset_sha256") != EXPECTED_ASSET_SHA:
        raise SystemExit(f"p.271 source segment missing or changed: {sid}")
if NEXT_SEGMENT_ID not in segments:
    raise SystemExit("p.272 continuation segment is missing")
if not source_lines[38].startswith("sumptuous altars of marble"):
    raise SystemExit("expected p.271 continuation text has changed")
if not source_lines[50].startswith("1657 after some fifty years of exile"):
    raise SystemExit("expected p.271 closing paragraph has changed")

segment_text = "\n".join(source_lines[37:51])
line_offsets = {}
offset = 0
for line_no in range(38, 52):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
max_candidate = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if max_candidate != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {max_candidate}")
previous_cov = coverage_by_id.get(PREVIOUS_SEGMENT_ID)
segment_cov = coverage_by_id.get(SEGMENT_ID)
if not previous_cov or (previous_cov["disposition"], previous_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"unexpected p.270 coverage state: {previous_cov}")
if not segment_cov or (segment_cov["disposition"], segment_cov["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"unexpected p.271 coverage state: {segment_cov}")
previous_visitor = next((row for row in statements if row["statement_id"] == PREVIOUS_VISITOR_STATEMENT_ID), None)
if not previous_visitor or previous_visitor["segment_id"] != PREVIOUS_SEGMENT_ID:
    raise SystemExit("p.270 visitor quotation fragment is missing")

EXISTING = {
    "venice": "cand-2724",
    "gesuati": "cand-1150",
    "gesuati_church": "cand-0737",
    "visitor": "cand-8708",
    "dominicans": "cand-0941",
    "tiepolo": "cand-2569",
    "tiepolo_dominic_fresco": "cand-2605",
    "piazzetta": "cand-1901",
    "piazzetta_dominican_altarpiece": "cand-1924",
    "tiepolo_agnes_altarpiece": "cand-2607",
    "ricci": "cand-2154",
    "ricci_dominican_altarpiece": "cand-2174",
    "carmelites": "cand-0563",
    "jesuits": "cand-1322",
    "oratorians": "cand-1783",
    "balestra": "cand-0168",
    "amigoni": "cand-0094",
    "cignaroli": "cand-0754",
    "capuchins": "cand-0539",
    "correr": "cand-0856",
    "capuchin_helen_canvas": "cand-2606",
    "counter_reformation": "cand-3396",
    "religious_orders": "cand-8675",
    "manin_family": "cand-1519",
    "jesuit_church": "cand-0734",
    "concina": "cand-0819",
    "benedictines": "cand-0287",
}
for key, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("fava_church", "Church of the Fava in Venice (as named by Haskell at p.271)", "place", "Oratorian church for which Haskell reports commissions in 1724 and 1732; no formal dedication is supplied here.", 47),
    ("capuchin_church_castello", "Unnamed Capuchin church at Castello in Venice (p.271 account)", "place", "Church whose ceiling held Tiepolo's St Helen canvas; a more specific dedication is not supplied in this segment.", 48),
    ("oratorian_altarpieces", "Altarpieces commissioned by the Oratorians from Piazzetta and Tiepolo for the Fava (1724 and 1732)", "work", "Two commissions dated 1724 and 1732; no titles or individual artist-to-date mapping are supplied in this sentence.", 47),
    ("gesuati_monastery", "Monastery adjoining the Gesuati in Venice (as described by Haskell at p.271)", "place", "Unspecified monastery named as a source of Padre Daniele Concina's anti-Jesuit invective; retain the source's spatial wording.", 46),
    ("saint_dominic", "Saint Dominic (religious figure named in Tiepolo's p.271 fresco subject)", "person", "Figure represented in the fresco of St Dominic instituting the Rosary; identity is not independently aligned here.", 40),
    ("saint_vincent_dominican_altarpiece", "Vincent (one of the Three Dominican Saints in Piazzetta's p.271 altarpiece)", "person", "The text supplies only the name Vincent in this work title; do not assume this is Vincent Ferrer without alignment evidence.", 41),
    ("saint_hyacinth", "Hyacinth (one of the Three Dominican Saints in Piazzetta's p.271 altarpiece)", "person", "Named as a subject of Piazzetta's altarpiece; identity remains to be aligned.", 41),
    ("saint_lawrence", "Lawrence (one of the Three Dominican Saints in Piazzetta's p.271 altarpiece)", "person", "Named as a subject of Piazzetta's altarpiece; identity remains to be aligned.", 41),
    ("pope_pius_v", "Pope Pius V (named as a subject of Sebastiano Ricci's p.271 altarpiece)", "person", "Named as one of three Dominican saints in the altarpiece indexed on p.271.", 43),
    ("thomas_aquinas", "Thomas Aquinas (named as a subject of Sebastiano Ricci's p.271 altarpiece)", "person", "Named as one of three Dominican saints in the altarpiece indexed on p.271.", 44),
    ("vincent_ferrer", "Vincent Ferrer (named as a subject of Sebastiano Ricci's p.271 altarpiece)", "person", "Named as one of three Dominican saints in the altarpiece indexed on p.271; keep distinct from the short-form Vincent in Piazzetta's other altarpiece pending S3.", 44),
    ("saint_helen", "Saint Helen (named in Tiepolo's p.271 Capuchin church canvas)", "person", "Religious figure in the title of Tiepolo's canvas; no further biographical claim is made here.", 48),
    ("papacy", "Papacy as the authority to which the Jesuits were subject in Haskell's p.271 account", "institution", "Institutional authority named in Haskell's explanation of the Society's unpopularity in Venice.", 50),
]
candidate_by_key = {}
new_candidates = []
for index, (key, name, kind, detail, line_no) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{EXPECTED_MAX_CANDIDATE + index:04d}"
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate natural key already exists: {name}")
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
        "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
    })
candidate_ids |= {row["candidate_id"] for row in new_candidates}

new_mentions = []


def c(key):
    return candidate_by_key[key]


def e(key):
    return EXISTING[key]


def add_mention(mention_id, line_no, candidate_id, surface, note, occurrence=0):
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    line = source_lines[line_no - 1]
    positions = []
    cursor = 0
    while True:
        found = line.find(surface, cursor)
        if found < 0:
            break
        positions.append(found)
        cursor = found + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface missing on L{line_no}: {surface!r}")
    start = line_offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"invalid exact mention span: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown mention candidate: {candidate_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })


add_mention("m-chp9-p271-visitor-marble-altars", 39, e("gesuati_church"), "sumptuous altars of marble", "Continuation of the 1742 visitor's nested description begun on p.270.")
add_mention("m-chp9-p271-visitor-120000", 39, e("gesuati_church"), "120,000 ducats", "Reported expenditure as stated by the visitor; no conversion or independent verification.")
add_mention("m-chp9-p271-tiepolo", 40, e("tiepolo"), "Tiepolo", "Painter of the Dominican ceiling fresco according to Haskell.")
add_mention("m-chp9-p271-dominic-fresco", 40, e("tiepolo_dominic_fresco"), "The ceiling fresco of St Dominic instituting the Rosary", "Reuse p.271 indexed work candidate.")
add_mention("m-chp9-p271-saint-dominic", 40, c("saint_dominic"), "St Dominic", "Person represented in the indexed fresco subject.")
add_mention("m-chp9-p271-piazzetta", 41, e("piazzetta"), "Piazzetta", "Painter named in the Dominican commissions passage.")
add_mention("m-chp9-p271-three-saints-work", 41, e("piazzetta_dominican_altarpiece"), "an altarpiece of Three Dominican Saints: Vincent, Hyacinth and Lawrence", "Reuse p.271 indexed work candidate.")
add_mention("m-chp9-p271-vincent", 41, c("saint_vincent_dominican_altarpiece"), "Vincent", "Short form in Piazzetta's altarpiece title; keep separate from Vincent Ferrer pending S3.")
add_mention("m-chp9-p271-hyacinth", 41, c("saint_hyacinth"), "Hyacinth", "Named as an altarpiece subject.")
add_mention("m-chp9-p271-lawrence", 41, c("saint_lawrence"), "Lawrence", "Named as an altarpiece subject.")
add_mention("m-chp9-p271-tiepolo-1748", 41, e("tiepolo"), "Tiepolo", "Artist named in the 1748 altarpiece account.")
add_mention("m-chp9-p271-agnes-work-part1", 41, e("tiepolo_agnes_altarpiece"), "his own altarpiece of Saints Agnes", "Work title wraps across source lines L41–42.")
add_mention("m-chp9-p271-agnes-work-part2", 42, e("tiepolo_agnes_altarpiece"), "Rosa and Catherine", "Continuation of the wrapped work title from L41.")
add_mention("m-chp9-p271-ricci", 43, e("ricci"), "Sebastiano Ricci", "Painter of the earlier Dominican altarpiece according to Haskell.")
add_mention("m-chp9-p271-ricci-altarpiece", 43, e("ricci_dominican_altarpiece"), "Pope Pius V,", "Named work title and figures continue through L44.")
add_mention("m-chp9-p271-pope-pius-v", 43, c("pope_pius_v"), "Pope Pius V", "Named subject of Ricci's altarpiece.")
add_mention("m-chp9-p271-thomas-aquinas", 44, c("thomas_aquinas"), "Thomas Aquinas", "Named subject of Ricci's altarpiece.")
add_mention("m-chp9-p271-vincent-ferrer", 44, c("vincent_ferrer"), "Vincent Ferrer", "Named subject of Ricci's altarpiece; do not equate with Piazzetta's short-form Vincent without S3 evidence.")
add_mention("m-chp9-p271-venice-dominican", 45, e("venice"), "Venice", "City in Haskell's description of the Dominican religious organization.")
add_mention("m-chp9-p271-gesuati", 46, e("gesuati"), "the Gesuati", "Order named as a source of Concina's anti-Jesuit polemic.")
add_mention("m-chp9-p271-monastery", 46, c("gesuati_monastery"), "the adjoining monastery", "Building adjacent to the Gesuati, kept distinct from the order itself.")
add_mention("m-chp9-p271-concina", 46, e("concina"), "Padre Daniele Concina", "Reuse p.271 index person seed.")
add_mention("m-chp9-p271-jesuits-invective", 46, e("jesuits"), "the Jesuits", "Target of Concina's reported invective.")
add_mention("m-chp9-p271-society", 46, e("jesuits"), "the Society", "Explicit antecedent is the Jesuits; Haskell says Concina suggested suppression.")
add_mention("m-chp9-p271-oratorians", 47, e("oratorians"), "The Oratorians", "Order commissioning altarpieces and employing other painters.")
add_mention("m-chp9-p271-altarpieces", 47, c("oratorian_altarpieces"), "altarpieces in 1724 and 1732", "Two commissions; text does not map dates individually to artists.")
add_mention("m-chp9-p271-piazzetta-oratorian", 47, e("piazzetta"), "Piazzetta", "Artist named in the Oratorian commission sentence.")
add_mention("m-chp9-p271-tiepolo-oratorian", 47, e("tiepolo"), "Tiepolo", "Artist named in the Oratorian commission sentence.")
add_mention("m-chp9-p271-fava", 47, c("fava_church"), "the Fava", "Short source form for the Oratorians' new church.")
add_mention("m-chp9-p271-balestra", 47, e("balestra"), "Balestra", "One of the additional artists named in the middle-century account.")
add_mention("m-chp9-p271-amigoni", 47, e("amigoni"), "Amigoni", "One of the additional artists named in the middle-century account.")
add_mention("m-chp9-p271-cignaroli", 47, e("cignaroli"), "Cignaroli", "One of the additional artists named in the middle-century account.")
add_mention("m-chp9-p271-capuchins", 48, e("capuchins"), "the Capuchins", "Religious Order in Haskell's account.")
add_mention("m-chp9-p271-correr", 48, e("correr"), "Fra Francesco Antonio Correr", "Reuse p.271 indexed person seed.")
add_mention("m-chp9-p271-venice-patriarch", 48, e("venice"), "Venice", "Location of the Patriarchate in Haskell's account.")
add_mention("m-chp9-p271-tiepolo-helen", 48, e("tiepolo"), "Tiepolo", "Painter of the St Helen canvas.")
add_mention("m-chp9-p271-helen-work", 48, e("capuchin_helen_canvas"), "a canvas of St Helen finding the True Cross", "Reuse p.271 indexed work candidate.")
add_mention("m-chp9-p271-helen", 48, c("saint_helen"), "St Helen", "Named figure in the canvas subject.")
add_mention("m-chp9-p271-capuchin-church", 48, c("capuchin_church_castello"), "their church at Castello", "Capuchin church; no more specific dedication supplied in this segment.")
add_mention("m-chp9-p271-counter-reformation", 49, e("counter_reformation"), "Counter Reformation", "Historical-religious movement described by Haskell.")
add_mention("m-chp9-p271-religious-communities", 49, e("religious_orders"), "the religious communities", "Collective patrons competing in the reported commission context.")
add_mention("m-chp9-p271-jesuits-absence", 49, e("jesuits"), "the Jesuits", "Order whose absence Haskell marks in the preceding competition.")
add_mention("m-chp9-p271-society-unpopular", 50, e("jesuits"), "the Society", "Society of Jesus, explicit antecedent from L49.")
add_mention("m-chp9-p271-papacy", 50, c("papacy"), "the papacy", "Authority named as the reason for the Society's subjection and unpopularity.")
add_mention("m-chp9-p271-venice-jesuit", 50, e("venice"), "Venice", "City in which Haskell says the Society was unpopular.")
add_mention("m-chp9-p271-jesuits-readmitted", 51, e("jesuits"), "the Jesuits", "Order readmitted after exile in 1657, as previously reported on p.267–268.")
add_mention("m-chp9-p271-manin-family", 51, e("manin_family"), "Manin family", "Family said to provide most resources for the new Jesuit church; keep newly ennobled qualification.")
add_mention("m-chp9-p271-jesuit-church", 51, e("jesuit_church"), "a vast new church", "Reuse index candidate for S. Maria Assunta; the account continues onto p.272.")
add_mention("m-chp9-p271-venice-hostile-pamphlet", 51, e("venice"), "Venice", "City in the unfinished hostile-pamphlet sentence.")
add_mention("m-chp9-p271-jesuits-hostile-pamphlet", 51, e("jesuits"), "the Jesuits", "Target of the hostile pamphlet mentioned in the sentence continued at p.272.", 1)

new_statements = []


def add_statement(statement_id, line_start, line_end, subject, object_, predicate, quote, claim, qualification, mentioned, *, relation=False, crossrefs=(), speaker="Haskell", text_layer="authorial narrative", footnote=None):
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote not anchored in p.271 segment: {statement_id}")
    refs = set(mentioned)
    refs.update(candidate for candidate in (subject, object_) if candidate)
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown statement candidate in {statement_id}: {sorted(refs - candidate_ids)}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 271,
        "pdf_physical_page": 37,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": sorted(refs),
    }
    if crossrefs:
        qualifiers["cross_reference_segments"] = list(crossrefs)
    if relation:
        qualifiers["relation_candidate"] = True
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
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


def c(key):
    return candidate_by_key[key]


def e(key):
    return EXISTING[key]


visitor_description = source_lines[38] + "\n" + source_lines[39].split("1 The ceiling fresco", 1)[0]
tiepolo_and_piazzetta = "The ceiling fresco" + source_lines[39].split("1 The ceiling fresco", 1)[1] + "\n" + source_lines[40].split(" It was not until", 1)[0]
visitor_alms = source_lines[39].split("1 The ceiling fresco", 1)[0]
tiepolo_1748 = source_lines[40][source_lines[40].index("It was'not until"):] + "\n" + source_lines[41].split("A few years earlier", 1)[0]
ricci_altarpiece = source_lines[41][source_lines[41].index("A few years earlier"):] + "\n" + source_lines[42] + "\n" + source_lines[43]
dominic_church_context = source_lines[44]
concina_jesuits = source_lines[45]
oratorian_commissions = source_lines[46]
capuchin_correr = source_lines[47].split(" A few years later", 1)[0]
capuchin_helen = "A few years later" + source_lines[47].split(" A few years later", 1)[1]
counter_reformation = source_lines[48]
jesuit_subjection = source_lines[49]
jesuit_readmission_resources = source_lines[49][source_lines[49].index("Reluctantly readmitted in"):] + "\n" + source_lines[50].split(" When, years later", 1)[0]
hostile_pamphlet_partial = "When, years later" + source_lines[50].split(" When, years later", 1)[1]

add_statement("st-chp9-p271-visitor-church-description-continuation", 39, 40, e("visitor"), e("gesuati_church"), "1742_visitor_described_marble_altars_seats_floor_architecture_facade_and_120000_ducats_spent", visitor_description, "The 1742 visitor describes marble altars in seven chapels, new choir seats, a marble floor, the interior's architecture and proportions, a fine façade and 120,000 ducats spent so far.", "Continuation of the nested visitor quotation begun on p.270 L35; the report remains attributed to an unnamed visitor. Note 1 is pending migration.", [e("visitor"), e("gesuati_church")], crossrefs=[{"segment_id":PREVIOUS_SEGMENT_ID,"source_line_start":35,"source_line_end":35}], speaker="unnamed visitor quoted by Haskell", text_layer="nested quotation", footnote=1)
add_statement("st-chp9-p271-visitor-alms-funding", 40, 40, e("visitor"), e("gesuati_church"), "visitor_said_the_120000_ducats_spent_on_gesuati_church_came_entirely_from_alms", visitor_alms, "The visitor says the church's vast expenditure had come entirely from alms.", "Nested testimony, not independently verified; the footnote marker follows the statement and its cited 1742 letter remains to be migrated.", [e("visitor"), e("gesuati_church")], speaker="unnamed visitor quoted by Haskell", text_layer="nested quotation", footnote=1)
add_statement("st-chp9-p271-tiepolo-dominican-fresco-and-piazzetta-altarpiece", 40, 41, e("tiepolo"), e("tiepolo_dominic_fresco"), "tiepolo_painted_dominic_rosary_fresco_1737_to_1739_while_piazzetta_painted_three_dominican_saints", tiepolo_and_piazzetta, "Haskell dates Tiepolo's ceiling fresco of St Dominic instituting the Rosary to 1737–1739 and says that during those years Piazzetta produced an altarpiece of Three Dominican Saints: Vincent, Hyacinth and Lawrence.", "Keep the two works, their artists and date range distinct; note 1's visitor letter remains pending.", [e("tiepolo"), e("tiepolo_dominic_fresco"), c("saint_dominic"), e("piazzetta"), e("piazzetta_dominican_altarpiece"), c("saint_vincent_dominican_altarpiece"), c("saint_hyacinth"), c("saint_lawrence"), e("dominicans")], relation=True)
add_statement("st-chp9-p271-tiepolo-agnes-altarpiece", 41, 42, e("tiepolo"), e("tiepolo_agnes_altarpiece"), "tiepolo_produced_saints_agnes_rose_catherine_altarpiece_in_1748_under_contract_signed_1740", tiepolo_1748, "Haskell says Tiepolo produced the altarpiece of Saints Agnes, Rosa and Catherine in 1748, under a contract signed in 1740.", "The title wraps across source lines; retain the distinction between contract date and completion date. The source OCR punctuation around 'not' and 'A few years earlier' is checked against the scan.", [e("tiepolo"), e("tiepolo_agnes_altarpiece"), c("saint_helen")], relation=True)
add_statement("st-chp9-p271-ricci-dominican-saints-altarpiece", 42, 44, e("ricci"), e("ricci_dominican_altarpiece"), "ricci_painted_earlier_altarpiece_of_pope_pius_v_thomas_aquinas_and_vincent_ferrer", ricci_altarpiece, "A few years before Tiepolo's 1748 altarpiece, Sebastiano Ricci had painted an earlier altarpiece of Pope Pius V, Thomas Aquinas and Vincent Ferrer, described by Haskell as one of Ricci's last and most magnificent works.", "Haskell's evaluative phrase is retained as his judgment; do not equate Vincent Ferrer with the short-form Vincent in Piazzetta's altarpiece without S3 evidence. Note 2 is pending migration.", [e("ricci"), e("ricci_dominican_altarpiece"), c("pope_pius_v"), c("thomas_aquinas"), c("vincent_ferrer"), e("dominicans")], relation=True, footnote=2)
add_statement("st-chp9-p271-dominican-church-exaltation", 45, 45, e("dominicans"), None, "haskell_says_exaltation_and_triumph_suited_dominican_church_at_centre_of_venetian_religious_organization", dominic_church_context, "Haskell says the note of exaltation and triumph suited a church at the centre of the most combative religious organization in eighteenth-century Venice.", "Authorial characterization; in context the church is the Dominican church of SS. Giovanni e Paolo, but this sentence does not repeat its name.", [e("dominicans"), e("venice")])
add_statement("st-chp9-p271-concina-anti-jesuit-invective", 46, 46, e("concina"), e("jesuits"), "concina_from_gesuati_and_adjoining_monastery_poured_invective_against_jesuits_and_was_among_first_to_suggest_suppression", concina_jesuits, "Haskell says Padre Daniele Concina, from the Gesuati and adjoining monastery, poured out invective against the Jesuits that intensified rivalry and was among the first to suggest suppressing the Society.", "The monastery is not individually named; retain Haskell's causal and priority wording without strengthening it. Note 3 is pending migration.", [e("concina"), e("gesuati"), c("gesuati_monastery"), e("jesuits")], relation=True, footnote=3)
add_statement("st-chp9-p271-oratorian-fava-commissions", 47, 47, e("oratorians"), c("oratorian_altarpieces"), "oratorians_commissioned_altarpieces_from_piazzetta_and_tiepolo_for_fava_in_1724_and_1732", oratorian_commissions, "Haskell says the Oratorians commissioned altarpieces in 1724 and 1732 from Piazzetta and Tiepolo for their new church of the Fava, and employed Balestra, Amigoni and Cignaroli during the middle years of the century.", "The sentence does not assign each date to an individual painter or the three later painters to named works.", [e("oratorians"), c("oratorian_altarpieces"), e("piazzetta"), e("tiepolo"), c("fava_church"), e("balestra"), e("amigoni"), e("cignaroli")], relation=True)
add_statement("st-chp9-p271-correr-patriarch-1734", 48, 48, e("capuchins"), e("correr"), "fra_francesco_antonio_correr_made_patriarch_of_venice_in_1734", capuchin_correr, "Haskell says the Capuchins reached the peak of their glory in 1734 when Fra Francesco Antonio Correr, one of their number, was made Patriarch of Venice.", "Keep the source's evaluative framing as Haskell's assessment. Note 4 is pending migration.", [e("capuchins"), e("correr"), e("venice")], relation=True, footnote=4)
add_statement("st-chp9-p271-tiepolo-st-helen-capuchin-church", 48, 48, e("tiepolo"), e("capuchin_helen_canvas"), "tiepolo_later_painted_st_helen_finding_true_cross_for_capuchin_church_at_castello", capuchin_helen, "A few years later, Haskell says Tiepolo painted a canvas of St Helen finding the True Cross for the ceiling of the Capuchin church at Castello.", "The exact year and church dedication are not supplied; note 4 is pending migration.", [e("tiepolo"), e("capuchin_helen_canvas"), c("saint_helen"), e("capuchins"), c("capuchin_church_castello")], relation=True, footnote=4)
add_statement("st-chp9-p271-counter-reformation-competition", 49, 49, e("counter_reformation"), e("jesuits"), "counter_reformation_extended_into_eighteenth_century_and_orders_competed_in_commissions_while_jesuits_were_absent", counter_reformation, "Haskell calls the continuation of the Counter Reformation into the eighteenth century extraordinary and notes religious communities rivalled one another through splendid commissions while the Jesuits were absent.", "This is Haskell's broad historical interpretation, not a quantitative account of all commissions. Note 5 is pending migration.", [e("counter_reformation"), e("religious_orders"), e("jesuits")], relation=True, footnote=5)
add_statement("st-chp9-p271-jesuit-unpopularity-and-papal-subjection", 50, 50, e("jesuits"), c("papacy"), "jesuits_never_popular_in_venice_because_of_absolute_subjection_to_papacy", jesuit_subjection, "Haskell says the Society of Jesus had never been popular in Venice because of its absolute subjection to the papacy.", "This is the author's explanation; do not generalize beyond the stated Venetian context. Note 6 is pending migration.", [e("jesuits"), c("papacy"), e("venice")], relation=True, footnote=6)
add_statement("st-chp9-p271-jesuit-readmission-and-manin-resources", 50, 51, e("jesuits"), e("jesuit_church"), "jesuits_readmitted_1657_then_about_fifty_years_later_built_new_church_resourced_mostly_by_recently_ennobled_manin_family", jesuit_readmission_resources, "Haskell says the Jesuits were readmitted in 1657 after about fifty years in exile, began building a large new church only after another half-century, and drew most resources from the newly ennobled but wealthy Manin family.", "Preserve 'about', 'mostly' and the source's temporal phrasing; this repeats and extends the earlier readmission statement. The hostile-pamphlet sentence continues on p.272.", [e("jesuits"), e("jesuit_church"), e("manin_family")], relation=True)
add_statement("st-chp9-p271-hostile-pamphlet-introduction-partial", 51, 51, e("jesuits"), None, "haskell_begins_report_of_hostile_pamphlet_against_jesuits_in_venice", hostile_pamphlet_partial, "Haskell begins to report what a hostile pamphlet in Venice said about the Jesuits' church funding.", "The sentence ends at 'mentioned in' and continues at p.272; no pamphlet content is inferred here.", [e("jesuits"), e("venice"), e("jesuit_church")], crossrefs=[{"segment_id":NEXT_SEGMENT_ID,"source_line_start":54,"source_line_end":54}], text_layer="authorial narrative")

if len({row["mention_id"] for row in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID within migration")
if len({row["statement_id"] for row in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID within migration")

previous_visitor["qualifiers"]["qualification"] = "The quotation fragment from p.270 L35 is closed by its continuation at p.271 L39-40, recorded in a linked continuation statement. Its closing footnote marker 1 appears on p.271; note text remains queued in the section notes segment. The p.270 source segment remains partial only because S0 line L36 carries the continuation of printed footnote 7."
previous_visitor["qualifiers"]["cross_reference_segments"] = [{"segment_id": SEGMENT_ID, "source_line_start": 39, "source_line_end": 40}]
previous_visitor["qualifiers"]["footnote_marker"] = 1
previous_visitor["qualifiers"]["footnote_text_pending"] = True
previous_cov.update({
    "source_line_ranges": "L28-35",
    "note": "Printed p.270 body L28-35 is semantically migrated. Its 1742 visitor quotation is now closed by p.271 L39-40 and linked to the continuation statement. S0 L36 remains pending as the continuation of printed footnote 7; that note text is in the section notes segment and its marker/text mismatch with the preceding Gesuati sentence remains under review.",
})
segment_cov.update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L39-51",
    "note": "Printed p.271 (CHP-9.pdf physical p.37) body read against scan. Closes the 1742 visitor's p.270 quotation; records Dominican commissions, Gesuati/Jesuit rivalry, Oratorian and Capuchin patronage, and Jesuit church history. L38 is page navigation. Final sentence at L51 ('mentioned in') continues to p.272 L54. Footnotes 1-6 are cited but their text remains in the consolidated notes segment. OCR punctuation correction around 'was not' is recorded in S2 only; S0 unchanged.",
})

summary = {
    "segment": SEGMENT_ID,
    "closed_previous_quote": PREVIOUS_VISITOR_STATEMENT_ID,
    "next_segment": NEXT_SEGMENT_ID,
    "status": "reviewed/partial",
    "new_candidates": len(new_candidates),
    "new_candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "scan_corrections": ["It was'not -> It was not", "1740.-A few -> 1740. A few"],
    "counts_after": {
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
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source_path, backup_path in zip(paths, backups):
        shutil.copy2(source_path, backup_path)
    try:
        write_csv(candidate_path, candidate_fields, candidates + new_candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(path.name for path in backups))
else:
    print("DRY RUN: no S2 table rows written")
