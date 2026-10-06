"""Controlled S2 migration for printed p.270 body; defaults to dry-run."""
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
SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l27-36"
NEXT_SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l38-51"
EXPECTED_SEGMENT_SHA = "93efb8db0766c4e0f568e4c49f04cfa8f41c4ae584666445c0682d070e260026"
EXPECTED_ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
EXPECTED_MAX_CANDIDATE = 8695
BACKUP_SUFFIX = ".bak-s2-chp9-p270-20261001"


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
if segments.get(SEGMENT_ID, {}).get("sha256") != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.270 segment is missing or changed")
if segments[SEGMENT_ID].get("asset_sha256") != EXPECTED_ASSET_SHA:
    raise SystemExit("p.270 source asset fingerprint mismatch")
if segments.get(NEXT_SEGMENT_ID, {}).get("segment_id") != NEXT_SEGMENT_ID:
    raise SystemExit("p.271 continuation segment is missing")
if not source_lines[27].startswith("So much richness, it was protested"):
    raise SystemExit("expected p.270 body has changed")
if not source_lines[34].startswith("Scarcely less imposing as patrons were the Dominicans"):
    raise SystemExit("expected p.270 final body paragraph has changed")

segment_text = "\n".join(source_lines[26:36])
line_offsets = {}
offset = 0
for line_no in range(27, 37):
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
segment_cov = coverage_by_id.get(SEGMENT_ID)
if not segment_cov or (segment_cov["disposition"], segment_cov["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"unexpected p.270 coverage state: {segment_cov}")

EXISTING = {
    "tuscany": "cand-6232",
    "rome": "cand-4490",
    "bologna": "cand-3398",
    "venice": "cand-2724",
    "scalzi_order": "cand-2389",
    "scalzi_church": "cand-0738",
    "carmelites": "cand-0563",
    "lazzarini": "cand-1368",
    "bambini": "cand-0171",
    "dorigny": "cand-0944",
    "tiepolo": "cand-2569",
    "holy_house": "cand-6056",
    "loreto": "cand-6057",
    "ricci": "cand-2154",
    "carmini_church": "cand-8458",
    "diziani": "cand-0922",
    "s_apponal": "cand-0729",
    "carmelites_index_church": "cand-0735",
    "scuola_carmini": "cand-2416",
    "piazzetta": "cand-1901",
    "judith_work": "cand-1914",
    "pedozzi": "cand-1860",
    "venetian_nobility": "cand-8677",
    "canaletto": "cand-0498",
    "dominicans": "cand-0941",
    "glory_st_dominic": "cand-1912",
    "giovanni_paolo": "cand-0733",
    "gesuati": "cand-1150",
    "massari": "cand-1562",
    "gesuati_church": "cand-0737",
}
for key, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("temple_jerusalem", "Temple of Jerusalem (invoked in the p.270 architectural defence)", "place", "Place used by the anonymous pamphleteer as an architectural comparison; source wording is retained.", 28),
    ("good_architecture", "Rules of good architecture as invoked by the p.270 critic", "term", "Evaluative architectural principle attributed to an unnamed critic in Haskell's account.", 28),
    ("roman_baroque", "Full Baroque style of Roman grandeur in the Scalzi church (p.270 account)", "term", "Style characterization reported by Haskell; not a catalogued decorative programme.", 28),
    ("palladian_tradition", "Palladian tradition in Venetian ecclesiastical architecture (p.270 account)", "term", "Architectural tradition described by Haskell as formerly dominant and soon dominant again.", 28),
    ("nazareth_island", "Island of S. Maria di Nazareth (as named in Haskell's p.270 account)", "place", "Source location from which Haskell says the Madonna painting was brought; keep distinct from the Scalzi church bearing the same dedication.", 28),
    ("madonna_painting", "Unidentified painting of the Madonna from S. Maria di Nazareth given to the Scalzi", "work", "Unnamed image said by Haskell to have been given to the Scalzi on their arrival in Venice; distinct from the 1745 ceiling fresco that celebrates it.", 28),
    ("holy_house_fresco", "Tiepolo ceiling fresco of the Holy House carried to Loreto at the Scalzi church (1745)", "work", "Fresco described by Haskell as the culmination of Tiepolo's decoration work; retain its date and reported subject without claiming an external catalogue match.", 28),
    ("ricci_carmini_fresco", "Unidentified 1708 fresco by Sebastiano Ricci in a chapel of the Carmini", "work", "Single chapel fresco described by Haskell; no title or precise chapel is supplied.", 30),
    ("diziani_carmini_pictures", "Four large pictures by Gaspare Diziani for the church of the Carmini", "work", "Unnamed group of four pictures described as painted nearly half a century after Ricci's 1708 fresco; no exact year is inferred.", 30),
    ("carmini_scuola_frescoes", "Tiepolo's ceiling frescoes in the principal room of the Scuola Grande dei Carmini", "work", "Group of frescoes described by Haskell as produced about twenty years after the Madonna del Carmelo; no exact date is supplied.", 31),
    ("carmini_association", "Association of non-noble laymen and religious headquartered at the Scuola Grande dei Carmini", "institution", "Group described by Haskell as under the general inspiration of the Carmelites; do not infer membership names or a narrower formal title.", 31),
    ("zattere", "Zattere waterfront in Venice (p.270 account)", "place", "Venetian area named as the site of the new Gesuati church.", 35),
    ("visitor_1742", "Unnamed visitor taken around the Gesuati church in 1742", "person", "Unidentified visitor whose nested testimony begins on p.270 and continues onto p.271; retain anonymity.", 35),
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


add_mention("m-chp9-p270-temple", 28, c("temple_jerusalem"), "Temple ofjerusalem", "S2 scan correction: print reads 'Temple of Jerusalem'; S0 OCR spacing is unchanged.")
add_mention("m-chp9-p270-tuscany", 28, e("tuscany"), "Tuscany", "Regional architectural comparison in the pamphleteer's reported defence.")
add_mention("m-chp9-p270-rome", 28, e("rome"), "Rome", "City named in the pamphleteer's architectural comparison.")
add_mention("m-chp9-p270-bologna", 28, e("bologna"), "Bologna", "City named in the pamphleteer's architectural comparison.")
add_mention("m-chp9-p270-good-architecture", 28, c("good_architecture"), "rules of good architecture", "Norm invoked by the unnamed critic in Haskell's report.")
add_mention("m-chp9-p270-baroque", 28, c("roman_baroque"), "full Baroque style of Roman grandeur", "Haskell's stylistic characterization of the church.")
add_mention("m-chp9-p270-palladian", 28, c("palladian_tradition"), "Palladian tradition", "Architectural tradition named by Haskell.")
add_mention("m-chp9-p270-venice-architecture", 28, e("venice"), "Venice", "City named as the setting of the ecclesiastical architectural tradition.")
add_mention("m-chp9-p270-lazzarini", 28, e("lazzarini"), "Lazzarini", "Reuse p.270 index candidate.")
add_mention("m-chp9-p270-bambini", 28, e("bambini"), "Bambini", "Reuse p.270 index candidate.")
add_mention("m-chp9-p270-dorigny", 28, e("dorigny"), "Dorigny", "Reuse p.270 index candidate.")
add_mention("m-chp9-p270-tiepolo-1", 28, e("tiepolo"), "Tiepolo", "Artist named in the Scalzi decoration account.")
add_mention("m-chp9-p270-holy-house", 28, e("holy_house"), "Holy House of Nazareth", "Subject represented in the reported ceiling fresco.")
add_mention("m-chp9-p270-loreto", 28, e("loreto"), "Loreto", "Destination in the reported image of the Holy House.")
add_mention("m-chp9-p270-madonna-painting", 28, c("madonna_painting"), "a painting of the Madonna", "Unnamed devotional painting said to have been given to the Scalzi.")
add_mention("m-chp9-p270-nazareth-island", 28, c("nazareth_island"), "the island of S. Maria di Nazareth", "Source location for the Madonna painting; distinct from the Scalzi church.")
add_mention("m-chp9-p270-scalzi-church", 28, e("scalzi_church"), "the Scalzi", "Here the Scalzi refers to the order as recipient of the painting.")
add_mention("m-chp9-p270-venice-arrival", 28, e("venice"), "Venice", "City of the Scalzi's arrival; second occurrence on this line.", 1)
add_mention("m-chp9-p270-carmelites-1", 29, e("carmelites"), "Carmelites", "The mother Order of the Scalzi, as explicitly described by Haskell.")
add_mention("m-chp9-p270-ricci", 30, e("ricci"), "Sebastiano Ricci", "Reuse the p.270 index candidate.")
add_mention("m-chp9-p270-carmini-church", 30, e("carmini_church"), "the church of the Carmini", "Use the existing source-level church candidate; keep separate from the Scuola Grande.")
add_mention("m-chp9-p270-diziani", 30, e("diziani"), "Gaspare Diziani", "Reuse the p.270 index candidate.")
add_mention("m-chp9-p270-tiepolo-2", 31, e("tiepolo"), "Tiepolo", "Reuse the p.270 index candidate.")
add_mention("m-chp9-p270-madonna-del-carmelo", 31, "cand-2596", "the Madonna del Carmelo", "Reuse the p.270 artwork index candidate; title and attribution are not externally checked here.")
add_mention("m-chp9-p270-order-chapel", 31, e("carmelites"), "the Order", "Carmelite Order, explicit antecedent in the sentence.")
add_mention("m-chp9-p270-s-apponal", 31, e("s_apponal"), "S. Aponal", "Church identified by the p.270 index seed.")
add_mention("m-chp9-p270-carmini-frescoes", 31, c("carmini_scuola_frescoes"), "the frescoes on the ceiling of the principal room in the Scuola Grande dei Carmini", "Work group described by Haskell; no separate title is supplied.")
add_mention("m-chp9-p270-scuola", 31, e("scuola_carmini"), "Scuola Grande dei Carmini", "Place/institution named by Haskell; role as headquarters is stated separately.")
add_mention("m-chp9-p270-association", 31, c("carmini_association"), "an association of non-noble laymen and religious", "Group headquartered at the Scuola Grande; no formal name is supplied.")
add_mention("m-chp9-p270-carmelites-2", 31, e("carmelites"), "the Carmelites", "General inspiration for the association, not a claim that the association was a formal Carmelite branch.")
add_mention("m-chp9-p270-piazzetta-1", 32, e("piazzetta"), "Piazzetta", "Reuse p.270 index candidate.")
add_mention("m-chp9-p270-judith", 32, e("judith_work"), "Judith with the Head of Holofernes", "Named work in the p.270 index.")
add_mention("m-chp9-p270-carmelite", 32, e("carmelites"), "Carmelite", "Order affiliation of Padre Jacopo Pedozzi.")
add_mention("m-chp9-p270-pedozzi", 33, e("pedozzi"), "Padre Jacopo Pedozzi", "Reuse the p.270 index person seed.")
add_mention("m-chp9-p270-order-secretary", 33, e("carmelites"), "the Order", "The Carmelite Order; Pedozzi's Secretary General role is reported by Haskell.")
add_mention("m-chp9-p270-venetian-nobility", 33, e("venetian_nobility"), "the Venetian nobikty", "S2 scan correction: the print reads 'nobility'; S0 OCR typo is unchanged.")
add_mention("m-chp9-p270-canaletto", 34, e("canaletto"), "Canaletto", "Reuse the p.270 index person seed.")
add_mention("m-chp9-p270-dominicans", 35, e("dominicans"), "the Dominicans", "Religious Order described as major patrons.")
add_mention("m-chp9-p270-piazzetta-2", 35, e("piazzetta"), "Piazzetta", "Reuse p.270 artist candidate.")
add_mention("m-chp9-p270-glory", 35, e("glory_st_dominic"), "The Glory of St Dominic", "Named frescoes/work as indexed on p.270.")
add_mention("m-chp9-p270-giovanni-paolo", 35, e("giovanni_paolo"), "SS. Giovanni e Paolo", "Church that contains the chapel named as the work's setting.")
add_mention("m-chp9-p270-gesuati", 35, e("gesuati"), "the Gesuati", "Another branch of the Order; retain the source's designation pending identity review.")
add_mention("m-chp9-p270-massari", 35, e("massari"), "Giorgio Massari", "Reuse the p.270 index candidate.")
add_mention("m-chp9-p270-gesuati-church", 35, e("gesuati_church"), "a complete new church", "Use the p.270–272 index seed for S. Maria del Rosario; identity alignment remains an S3 task.")
add_mention("m-chp9-p270-zattere", 35, c("zattere"), "the Zattere", "Site of the new Gesuati church.")
add_mention("m-chp9-p270-scalzi-analogy", 35, e("scalzi_order"), "the Scalzi", "Order used as a comparison for public-funding advocacy.")
add_mention("m-chp9-p270-visitor", 35, c("visitor_1742"), "one visitor", "Unnamed witness taken around the church in 1742; the report continues on p.271.")
add_mention("m-chp9-p270-gesuati-father", 35, e("gesuati"), "one of the Gesuati fathers", "Unnamed guide belonging to the order.")
add_mention("m-chp9-p270-new-church-interior", 35, e("gesuati_church"), "the new church", "Same new church; the visitor's description continues at p.271.")

new_statements = []


def add_statement(statement_id, line_start, line_end, subject, object_, predicate, quote, claim, qualification, mentioned, *, relation=False, crossrefs=(), speaker="Haskell", text_layer="authorial narrative", footnote=None):
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote not anchored in p.270 segment: {statement_id}")
    refs = set(mentioned)
    refs.update(candidate for candidate in (subject, object_) if candidate)
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown statement candidate in {statement_id}: {sorted(refs - candidate_ids)}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 270,
        "pdf_physical_page": 36,
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


architectural_protest = source_lines[27].split(" And here he could do no more", 1)[0]
pamphlet_comparison = "And here he could do no more" + source_lines[27].split(" And here he could do no more", 1)[1].split(" The complaint certainly", 1)[0]
complaint_and_style = "The complaint certainly" + source_lines[27].split(" The complaint certainly", 1)[1].split(" Rich families", 1)[0]
rich_families_patronage = source_lines[27].split(" Rich families", 1)[1]
rich_families_patronage = "Rich families" + rich_families_patronage.split(" Above all Tiepolo", 1)[0]
tiepolo_decoration = "Above all Tiepolo" + source_lines[27].split(" Above all Tiepolo", 1)[1]
carmeli_patronage = source_lines[28]
ricci_diziani = source_lines[29]
tiepolo_carmelo = source_lines[30].split("; while", 1)[0]
tiepolo_carmini = "while" + source_lines[30].split("; while", 1)[1]
piazzetta_judith = source_lines[31].split(" It was, incidentally", 1)[0]
pedozzi_canale = "It was, incidentally" + source_lines[31].split(" It was, incidentally", 1)[1] + "\n" + source_lines[32] + "\n" + source_lines[33]
dominican_commission = source_lines[34].split(" At much the same time", 1)[0]
gesuati_church = "At much the same time" + source_lines[34].split(" At much the same time", 1)[1].split(" When one visitor", 1)[0]
visitor_partial = "When one visitor" + source_lines[34].split(" When one visitor", 1)[1]

add_statement("st-chp9-p270-critic-architectural-objection", 28, 28, e("scalzi_church"), c("good_architecture"), "critic_objected_that_richness_and_gold_conflicted_with_good_architecture", architectural_protest, "Haskell reports a protest that the church's degree of richness, especially its gold, violated good architectural rules.", "The critic is unnamed and the objection is reported rather than quoted directly; note 7's attachment and content will be reviewed with the note segment.", [e("scalzi_church"), c("good_architecture")], speaker="unnamed critic described by Haskell", text_layer="reported objection", footnote=7)
add_statement("st-chp9-p270-pamphlet-architectural-comparison", 28, 28, e("scalzi_church"), c("temple_jerusalem"), "anonymous_pamphleteer_countered_architectural_objection_with_ancient_and_italian_examples", pamphlet_comparison, "In answer to the criticism, Haskell says the anonymous pamphleteer invoked the Temple of Jerusalem and churches and palaces of Tuscany, Rome and Bologna.", "Continuation of the anonymous pamphleteer's defence on p.269; the examples are rhetorical comparisons, not claims of direct architectural influence.", [e("scalzi_church"), c("temple_jerusalem"), e("tuscany"), e("rome"), e("bologna")], crossrefs=[{"segment_id":"chp-9:09_CHP-9_sec_ii:l18-25","source_line_start":23,"source_line_end":24}], speaker="anonymous pamphleteer as described by Haskell", text_layer="nested pamphlet argument")
add_statement("st-chp9-p270-complaint-had-force-and-church-style", 28, 28, e("scalzi_church"), c("roman_baroque"), "haskell_says_architectural_complaint_had_force_but_church_marked_roman_baroque_break_with_palladian_tradition", complaint_and_style, "Haskell says the complaint had force, though it was not pressed, because the church's Roman Baroque grandeur broke with the Palladian tradition that had dominated Venetian ecclesiastical architecture and would soon do so again.", "Keep the author's qualification and sequence; the scan confirms the OCR phrase 'Temple ofjerusalem' should read 'Temple of Jerusalem'.", [e("scalzi_church"), c("roman_baroque"), c("palladian_tradition"), e("venice")])
add_statement("st-chp9-p270-rich-families-employed-painters", 28, 28, None, None, "rich_families_old_and_new_employed_lazzarini_bambini_and_dorigny_for_pictures_and_frescoes", rich_families_patronage, "Haskell says rich families, both old and new, employed Lazzarini, Bambini and Dorigny to provide pictures and frescoes.", "The families are not named or enumerated; do not distribute the commissions among the three artists.", [e("lazzarini"), e("bambini"), e("dorigny")], relation=True)
add_statement("st-chp9-p270-tiepolo-scalzi-decoration-1745", 28, 28, e("tiepolo"), c("holy_house_fresco"), "tiepolo_called_to_help_decorate_scalzi_church_culminating_in_1745_ceiling_fresco", tiepolo_decoration, "Haskell says Tiepolo was called in on several occasions to help decorate the Scalzi church, culminating in a 1745 ceiling fresco.", "The relation is inferred from the sentence's grammar but remains a source-level candidate; note 1 is pending migration.", [e("tiepolo"), c("holy_house_fresco"), e("scalzi_church"), e("holy_house"), e("loreto")], relation=True, footnote=1)
add_statement("st-chp9-p270-fresco-subject-and-madonna-donation", 28, 28, c("holy_house_fresco"), c("madonna_painting"), "1745_fresco_showed_holy_house_carried_by_angels_to_loreto_and_was_designed_to_celebrate_scalzi_madonna_image", tiepolo_decoration, "The fresco showed the Holy House of Nazareth being carried by angels to Loreto; Haskell says the theme celebrated a Madonna painting from S. Maria di Nazareth that had been given to the Scalzi on their arrival in Venice.", "The source distinguishes this 1745 fresco from the earlier unnamed Madonna painting; donor, exact date of transfer and external identities are not supplied.", [c("holy_house_fresco"), e("holy_house"), e("loreto"), c("madonna_painting"), c("nazareth_island"), e("scalzi_order"), e("venice")], relation=True, footnote=1)
add_statement("st-chp9-p270-carmelite-patronage-comparison", 29, 29, e("carmelites"), None, "haskell_describes_mother_carmelite_orders_patronage_as_splendid", carmeli_patronage, "Haskell says the patronage of the Scalzi's mother Order, the Carmelites, was equally splendid.", "Comparative authorial assessment; it does not identify a specific commission.", [e("carmelites"), e("scalzi_order")])
add_statement("st-chp9-p270-ricci-and-diziani-carmini-works", 30, 30, e("ricci"), c("ricci_carmini_fresco"), "ricci_frescoed_one_carmini_chapel_in_1708_and_pupil_diziani_later_painted_four_large_pictures_for_same_church", ricci_diziani, "Haskell says Sebastiano Ricci frescoed one chapel in the church of the Carmini in 1708; nearly half a century later his pupil Gaspare Diziani painted four large pictures for the same church.", "The exact chapel and picture titles are not supplied; retain 'nearly half a century' without inferring a year. Note 2 is pending migration.", [e("ricci"), c("ricci_carmini_fresco"), e("diziani"), c("diziani_carmini_pictures"), e("carmini_church")], relation=True, footnote=2)
add_statement("st-chp9-p270-tiepolo-madonna-del-carmelo", 31, 31, e("tiepolo"), "cand-2596", "tiepolo_painted_madonna_del_carmelo_about_1720_for_carmelite_chapel_at_s_apponal", tiepolo_carmelo, "Haskell says Tiepolo painted the Madonna del Carmelo, one of his earliest works, about 1720 for a chapel belonging to the Carmelites in S. Aponal.", "Retain 'about 1720'; the exact chapel is unnamed. The p.270 index supplies the work seed; note 3 is pending migration.", [e("tiepolo"), "cand-2596", e("carmelites"), e("s_apponal")], relation=True, footnote=3)
add_statement("st-chp9-p270-tiepolo-carmini-frescoes", 31, 31, e("tiepolo"), c("carmini_scuola_frescoes"), "tiepolo_later_produced_ceiling_frescoes_for_carmelite_scuola_grande_carmini", tiepolo_carmini, "About twenty years after the Madonna del Carmelo, Haskell says Tiepolo produced frescoes on the ceiling of the principal room in the Scuola Grande dei Carmini for the Carmelites.", "Haskell calls these among Tiepolo's greatest masterpieces; this is authorial evaluation, not an independent ranking. Note 4 is pending migration.", [e("tiepolo"), c("carmini_scuola_frescoes"), e("carmelites"), e("scuola_carmini"), c("carmini_association")], relation=True, footnote=4)
add_statement("st-chp9-p270-scuola-carmini-association", 31, 31, e("scuola_carmini"), c("carmini_association"), "scuola_grande_dei_carmini_was_headquarters_of_non_noble_lay_religious_association_under_carmelite_inspiration", tiepolo_carmini, "Haskell describes the Scuola Grande dei Carmini as the headquarters of an association of non-noble laymen and religious under the Carmelites' general inspiration.", "The association's formal name and legal relation to the building are not supplied; do not identify it beyond Haskell's wording.", [e("scuola_carmini"), c("carmini_association"), e("carmelites")])
add_statement("st-chp9-p270-piazzetta-judith-carmini-group", 32, 32, e("piazzetta"), e("judith_work"), "piazzetta_painted_judith_with_head_of_holofernes_for_same_carmelite_inspired_group", piazzetta_judith, "Haskell says Piazzetta painted Judith with the Head of Holofernes for the same group and that other leading painters were also employed.", "The group refers back to the Scuola Grande association; note 5 is pending migration.", [e("piazzetta"), e("judith_work"), c("carmini_association"), e("carmelites")], relation=True, footnote=5)
add_statement("st-chp9-p270-pedozzi-reputation-and-canaletto-patron", 32, 34, e("pedozzi"), e("canaletto"), "carmelite_secretary_general_pedozzi_held_in_high_regard_by_venetian_nobility_was_among_canalettos_earliest_patrons", pedozzi_canale, "Haskell identifies Padre Jacopo Pedozzi as Secretary General of the Carmelite Order, says he was highly regarded by Venetian nobility, and calls him one of Canaletto's very first patrons.", "The precise patronage act and date are not given; note 6 is pending migration and will be linked to the cited Marchesini letter and Zarzabini locator.", [e("pedozzi"), e("carmelites"), e("venetian_nobility"), e("canaletto")], relation=True, footnote=6)
add_statement("st-chp9-p270-dominican-commission", 35, 35, e("dominicans"), e("glory_st_dominic"), "piazzetta_painted_only_frescoes_for_dominicans_between_1725_and_1727_at_ss_giovanni_e_paolo", dominican_commission, "Haskell says the Dominicans were imposing patrons and that Piazzetta painted his only frescoes for them between 1725 and 1727: The Glory of St Dominic in a chapel at SS. Giovanni e Paolo.", "The exact chapel is not named; the note 7 text later in the page specifically discusses the Dominican church, although its printed marker appears after the following Gesuati sentence.", [e("dominicans"), e("piazzetta"), e("glory_st_dominic"), e("giovanni_paolo")])
add_statement("st-chp9-p270-gesuati-new-church-public-funding", 35, 35, e("gesuati"), e("gesuati_church"), "gesuati_employed_massari_to_build_new_zattere_church_with_most_funding_from_public_support", gesuati_church, "Haskell says the Gesuati were beginning to employ Giorgio Massari to build a new church on the Zattere, financed largely by public support.", "The support is not attributed to a named body or donor; retain the source's collective formulation. Printed note 7 follows this sentence, but its content concerns the Dominicans; do not force the note onto this claim.", [e("gesuati"), e("massari"), e("gesuati_church"), c("zattere")], relation=True, footnote=7)
add_statement("st-chp9-p270-gesuati-emphasized-public-support", 35, 35, e("gesuati"), e("gesuati_church"), "gesuati_were_keen_to_emphasize_public_support_for_new_church_as_scalzi_had_done", gesuati_church, "Haskell says the Gesuati, like the Scalzi, were keen to emphasize the public support for their new church.", "This repeats the preceding source-level claim; the note 7 attachment/content mismatch is preserved for later review.", [e("gesuati"), e("gesuati_church"), e("scalzi_order")], relation=True, footnote=7)
add_statement("st-chp9-p270-1742-visitor-description-partial", 35, 35, c("visitor_1742"), e("gesuati_church"), "unnamed_visitor_began_describing_gesuati_church_interior_in_1742", visitor_partial, "Haskell begins an unnamed visitor's 1742 description of the new Gesuati church's interior, paintings and chiaroscuri on its brilliantly lit vault.", "The quotation cuts off at 'with' and continues on p.271; keep this statement partial until the continuation is read. S2 scan correction: OCR 'sine interior' reads 'fine interior' in print. The closing footnote marker appears on p.271, not in this fragment.", [c("visitor_1742"), e("gesuati_church"), e("gesuati")], crossrefs=[{"segment_id":NEXT_SEGMENT_ID,"source_line_start":39,"source_line_end":40}], speaker="unnamed visitor quoted by Haskell", text_layer="nested quotation")

if len({row["mention_id"] for row in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID within migration")
if len({row["statement_id"] for row in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID within migration")

segment_cov.update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L28-35",
    "note": "Printed p.270 (CHP-9.pdf physical p.36) body L28-35 read against scan. L27 page heading is navigation. The anonymous architectural objection and reply, style comparison, commissions by Carmelites/Dominicans/Gesuati and the 1742 visitor quotation are recorded. Visitor quotation continues at p.271 L39-40; source line L36 is a continuation of note 7 and remains for the notes pass. Note 7's printed marker follows the Gesuati funding sentence, while its text concerns the Dominican church; discrepancy retained without forcing attribution. OCR corrections are recorded in S2 only; S0 unchanged."
})

summary = {
    "segment": SEGMENT_ID,
    "status": "reviewed/partial",
    "next_segment": NEXT_SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "new_candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "scan_corrections": ["Temple ofjerusalem -> Temple of Jerusalem", "nobikty -> nobility", "Gcsuati -> Gesuati", "sine interior -> fine interior"],
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
