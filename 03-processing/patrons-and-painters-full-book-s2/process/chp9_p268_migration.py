"""Controlled S2 migration of p.268; dry-run by default."""
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
SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l6-16"
NEXT_SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l18-25"
PREVIOUS_SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l3-4"
EXPECTED_SEGMENT_SHA = "011ed62e984b1e67c23bc2e36b88e9957fae9c3f97458a06918a4b75254853f8"
EXPECTED_ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
EXPECTED_MAX_CANDIDATE = 8671
BACKUP_SUFFIX = ".bak-s2-chp9-p268-20261001"


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


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(source_bytes).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("section-II source asset has changed")
segments = {row["segment_id"]: row for row in read_jsonl(segment_path)}
if segments.get(SEGMENT_ID, {}).get("sha256") != EXPECTED_SEGMENT_SHA:
    raise SystemExit("p.268 segment is missing or changed")
if segments[SEGMENT_ID].get("asset_sha256") != EXPECTED_ASSET_SHA:
    raise SystemExit("p.268 source asset fingerprint mismatch")
if not source_lines[6].startswith("it was expressed.1 Such lavishness was natural enough"):
    raise SystemExit("expected p.268 opening text has changed")
if not source_lines[15].startswith("Most of the religious Orders had very rich backers"):
    raise SystemExit("expected p.268 final paragraph has changed")
segment_text = "\n".join(source_lines[5:16])
line_offsets = {}
offset = 0
for line_no in range(6, 17):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

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
    raise SystemExit(f"unexpected p.268 coverage state: {segment_cov}")
next_cov = coverage_by_id.get(NEXT_SEGMENT_ID)
if not next_cov or (next_cov["disposition"], next_cov["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"unexpected p.269 coverage state: {next_cov}")

EXISTING = {
    "state": "cand-8572",
    "venice_city": "cand-2735",
    "cignaroli": "cand-0754",
    "barocci": "cand-0247",
    "carlo_dolci": "cand-0923",
    "piazzetta": "cand-1901",
    "tiepolo": "cand-2569",
    "manin_family": "cand-1519",
    "udine_city": "cand-2666",
    "udine_cathedral": "cand-8235",
    "scalzi_church_index": "cand-0738",
    "jesuit_church_index": "cand-0734",
    "jesuits": "cand-3403",
    "dorigny": "cand-0945",
    "passeriano": "cand-8217",
}
for key, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("venetian_church", "Catholic Church as institution and patron in Haskell's p.268 Venetian account", "institution", "Local S2 candidate for the institutional Church in this Venetian passage; keep separate from the Republic, the Papacy and individual church buildings until S3.", 9),
    ("venetian_piety", "Venetian piety as expressed through lavish church expenditure in Haskell's account", "term", "Concept in Haskell's p.267–268 account; the passage distinguishes doubts about inner piety from the visible lavishness of its expression.", 7),
    ("venetian_clergy", "Clergy as a social group in Haskell's p.268 Venetian account", "term", "Collective social group, not an organized institution; the reported population share and access to ecclesiastical office remain Haskell's claims.", 8),
    ("religious_orders", "Religious orders as collective patrons in Haskell's p.268 Venetian account", "term", "Collective category, not one institution; Haskell attributes wealth and patronage to unnamed orders generally.", 7),
    ("history_painters", "History painters in Venice as a collective group in Haskell's account", "term", "Unspecified group used for Haskell's aggregate claim about the proportion of work devoted to the Church.", 9),
    ("venetian_nobility", "Venetian nobility as a social group in Haskell's p.268 account", "term", "Collective social estate in Haskell's account of ecclesiastical offices, younger sons and patronage; no unnamed individual is inferred.", 11),
    ("property_transfer_ban_1767", "1767 prohibition on secular property passing into clerical ownership", "event", "Haskell reports a 1767 decision to forbid secular property passing into clerical ownership; the passage does not identify the statute or independently verify the measure.", 8),
    ("sacred_figures_in_painting", "The Virgin and Saints as subjects of Venetian religious painting in Haskell's p.268 account", "term", "Iconographic subject group in Haskell's interpretation of Piazzetta and Tiepolo; not a claim about historical agency by the depicted figures.", 12),
    ("aristocratic_principles_in_sacred_history", "Aristocratic principles projected into sacred history in Haskell's interpretation", "term", "Haskell's interpretive concept linking the depicted Virgin and Saints to aristocratic principles; retain as authorial interpretation.", 12),
    ("verona", "Verona (place mentioned in Haskell's p.268 Cignaroli comparison)", "place", "Place named as Cignaroli's context in this passage; no further location or institutional identity inferred.", 9),
]

candidate_by_key = {}
new_candidates = []
for offset, (key, name, kind, detail, line_no) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{EXPECTED_MAX_CANDIDATE + offset:04d}"
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


def m(key):
    return candidate_by_key[key]


add_mention("m-chp9-p268-piety-lavishness", 7, m("venetian_piety"), "Such lavishness", "Completes the p.267 sentence about the outward expression of Venetian piety; the cross-page link is recorded in its statement.")
add_mention("m-chp9-p268-church-wealth", 7, m("venetian_church"), "the Church", "Institutional Church, distinct from the Republic and the churches as buildings.")
add_mention("m-chp9-p268-religious-orders-line7", 7, m("religious_orders"), "religious", "First half of the line-broken phrase 'religious Orders'.")
add_mention("m-chp9-p268-religious-orders-line8", 8, m("religious_orders"), "Orders", "Completes the line-broken phrase 'religious Orders'.")
add_mention("m-chp9-p268-state-wealth", 8, EXISTING["state"], "the State", "Venetian political authority, not the city.")
add_mention("m-chp9-p268-property-ban-year", 8, m("property_transfer_ban_1767"), "1767", "Year attached to the reported prohibition.")
add_mention("m-chp9-p268-clergy-share", 8, m("venetian_clergy"), "the clergy", "Collective clergy population in Haskell's report.")
add_mention("m-chp9-p268-republic-income", 8, EXISTING["state"], "the Republic", "Venetian Republic as the comparison polity.")
add_mention("m-chp9-p268-church-leading-patron", 9, m("venetian_church"), "the Church", "Institutional patron, not a church building.")
add_mention("m-chp9-p268-venice-city-1", 9, EXISTING["venice_city"], "Venice", "City in which the history painters are discussed.")
add_mention("m-chp9-p268-history-painters", 9, m("history_painters"), "history painters", "Unspecified collective group; no individual membership is inferred.")
add_mention("m-chp9-p268-cignaroli", 9, EXISTING["cignaroli"], "Cignaroli", "Reuse the index candidate covering p.268; exact identity remains for S3.")
add_mention("m-chp9-p268-verona", 9, m("verona"), "Verona", "Place where the text locates Cignaroli in this comparison.")
add_mention("m-chp9-p268-barocci", 10, EXISTING["barocci"], "Barocci", "Reuse the index candidate whose range includes p.268.")
add_mention("m-chp9-p268-carlo-dolci", 10, EXISTING["carlo_dolci"], "Carlo Dolci", "Reuse the index candidate whose range includes p.268.")
add_mention("m-chp9-p268-church-market", 10, m("venetian_church"), "the Church", "Institutional Church as the provider of an altarpiece market.")
add_mention("m-chp9-p268-clerics", 11, m("venetian_clergy"), "Clerics", "Clergy as a social group, not a single organization.")
add_mention("m-chp9-p268-government", 11, EXISTING["state"], "the government", "Refers to the Venetian political authority in this passage.")
add_mention("m-chp9-p268-ecclesiastical-posts", 11, m("venetian_church"), "ecclesiastical posts", "Posts within the Church; the passage says they were held by members of the nobility.")
add_mention("m-chp9-p268-nobility-offices", 11, m("venetian_nobility"), "the nobility", "Collective estate in Haskell's account.")
add_mention("m-chp9-p268-traveller", 11, m("venetian_nobility"), "a traveller", "Unidentified traveller is retained as the attributed speaker in the statement, not treated as a named person candidate.")
add_mention("m-chp9-p268-patrician-ideals", 11, m("venetian_nobility"), "patrician ideals", "Haskell's social interpretation; not an independently verified general rule.")
add_mention("m-chp9-p268-sacred-subjects", 12, m("sacred_figures_in_painting"), "the Virgin and Saints", "Iconographic subjects in the passage's comparison of religious paintings.")
add_mention("m-chp9-p268-piazzetta", 12, EXISTING["piazzetta"], "Piazzetta", "Reuse p.268 index candidate.")
add_mention("m-chp9-p268-tiepolo", 12, EXISTING["tiepolo"], "Tiepolo", "Reuse p.268 index candidate.")
add_mention("m-chp9-p268-aristocratic-principles", 12, m("aristocratic_principles_in_sacred_history"), "aristocratic principles", "Haskell's interpretive concept of their projection into sacred history.")
add_mention("m-chp9-p268-nobles-commissions", 13, m("venetian_nobility"), "nobles", "Collective patrons in Haskell's account.")
add_mention("m-chp9-p268-manin-family", 14, EXISTING["manin_family"], "Manin", "Completes the line-broken phrase 'Thus the Manin'; reuse the p.268 index entry 'Manin family'. Individual brothers remain for the footnote/S3.")
add_mention("m-chp9-p268-udine-cathedral", 14, EXISTING["udine_cathedral"], "Cathedral at Udine", "The cathedral building is a place; choir, transept and altar are named as its decoration targets.")
add_mention("m-chp9-p268-udine-city", 14, EXISTING["udine_city"], "Udine", "City, distinct from the Cathedral as a building.")
add_mention("m-chp9-p268-scalzi-church", 14, EXISTING["scalzi_church_index"], "the church of the Scalzi in Venice", "Reuse the index candidate whose subentry identifies the Scalzi church; S3 must preserve the building/order distinction.")
add_mention("m-chp9-p268-venice-scalzi", 14, EXISTING["venice_city"], "Venice", "City location of the Scalzi church.")
add_mention("m-chp9-p268-jesuit-church", 15, EXISTING["jesuit_church_index"], "Jesuit church", "Use the p.268 Churches index candidate with the Jesuit-church subentry; distinguish the building from the Jesuit institution.")
add_mention("m-chp9-p268-jesuits-institution", 15, EXISTING["jesuits"], "Jesuit", "Religious institution named as the church's affiliation, not the church building itself.")
add_mention("m-chp9-p268-dorigny", 15, EXISTING["dorigny"], "Louis Dorigny", "Reuse the index candidate with the 'work for Manin' subentry at p.268.")
add_mention("m-chp9-p268-passeriano", 15, EXISTING["passeriano"], "Passeriano", "Place of the Manin villa decorated by Dorigny.")
add_mention("m-chp9-p268-orders-patrons", 16, m("religious_orders"), "religious Orders", "Collective category of religious institutions; no individual order is inferred.")
add_mention("m-chp9-p268-venice-city-2", 16, EXISTING["venice_city"], "Venice", "City context for early-eighteenth-century patronage.")
add_mention("m-chp9-p268-monks", 16, m("religious_orders"), "monks", "Monastic actors in the observer's incomplete quotation; the cited source will be processed with the note segment.")

new_statements = []


def add_statement(statement_id, line_start, line_end, subject, object_, predicate, quote, claim, qualification, mentioned, *, relation=False, crossrefs=(), speaker="Haskell", text_layer="authorial narrative", footnote=None):
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote not anchored in p.268 segment: {statement_id}")
    refs = set(mentioned)
    refs.update(candidate for candidate in (subject, object_) if candidate)
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown statement candidate in {statement_id}: {sorted(refs - candidate_ids)}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 268,
        "pdf_physical_page": 34,
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


crossref_267 = [{"segment_id": PREVIOUS_SEGMENT_ID, "source_line_start": 3, "source_line_end": 4}]
add_statement("st-chp9-p268-venetian-piety-lavishness", 7, 7, c("venetian_piety"), c("venetian_church"), "haskell_describes_venetian_piety_as_publicly_expressed_through_lavishness", source_lines[6], "Haskell distinguishes doubts about the depth of Venetian piety from confidence in its lavish outward expression.", "This completes the sentence begun on p.267 L3; 'it' refers to piety. The claim is Haskell's characterization, not an independent measure of religious belief.", [c("venetian_piety"), c("venetian_church")], crossrefs=crossref_267, footnote=1)
add_statement("st-chp9-p268-church-and-orders-wealth", 7, 8, None, None, "church_and_religious_orders_reported_as_growing_in_wealth", source_lines[6] + "\n" + source_lines[7].split(" When in 1767")[0], "Haskell says the Church, particularly the religious orders, grew wealthy through the seventeenth and first half of the eighteenth centuries despite frequent unsuccessful State efforts to stop the process.", "A broad authorial summary. Do not infer that every order or every attempt is individually identified.", [c("venetian_church"), c("religious_orders"), e("state")], relation=True)
add_statement("st-chp9-p268-property-transfer-ban-1767", 8, 8, c("property_transfer_ban_1767"), e("state"), "venetian_state_decided_to_forbid_secular_property_transfers_to_clerical_ownership_in_1767", source_lines[7], "Haskell reports that in 1767 a decision was made to forbid secular property from passing into clerical ownership.", "The text does not name the statute or its enforcement history; retain this as Haskell's report.", [c("property_transfer_ban_1767"), e("state"), c("venetian_clergy"), c("venetian_church")], footnote=2)
add_statement("st-chp9-p268-clergy-land-income-comparison", 8, 8, c("venetian_clergy"), e("state"), "clergy_two_percent_of_population_land_income_nearly_equalled_remainder_of_republic", source_lines[7], "Haskell reports that the clergy were two per cent of the population while the income from their land was almost equal to that of the rest of the Republic.", "Preserve 'almost' and the comparison; the cited Tabacco source has not been independently read in this task.", [c("venetian_clergy"), e("state"), c("property_transfer_ban_1767")], footnote=2)
church_patron_quote = source_lines[8].split(" Of the history painters")[0]
history_painters_quote = "Of the history painters" + source_lines[8].split(" Of the history painters", 1)[1].split(" Of Cignaroli")[0]
cignaroli_quote = source_lines[8][source_lines[8].index("Of Cignaroli"): ] + "\n" + source_lines[9].split(" With its constant")[0]
add_statement("st-chp9-p268-church-leading-patron", 9, 9, c("venetian_church"), e("venice_city"), "church_retained_or_increased_position_as_leading_patron_of_contemporary_art", church_patron_quote, "Haskell says the Church retained, or even increased, its position as Venice's leading patron of contemporary art.", "Retain 'or even increased' as Haskell's qualified phrasing; scan reading removes the spurious OCR hyphen in 'of-contemporary'.", [c("venetian_church"), e("venice_city")], relation=True)
add_statement("st-chp9-p268-history-painters-church-work", 9, 9, c("history_painters"), c("venetian_church"), "venetian_history_painters_devoted_over_half_their_work_to_church", history_painters_quote, "Haskell generalizes that virtually all history painters in Venice devoted well over half their work to the Church, often a higher proportion.", "Aggregate authorial estimate; no percentages, individual artists or commissions beyond the text are inferred.", [c("history_painters"), c("venetian_church"), e("venice_city")], relation=True)
add_statement("st-chp9-p268-cignaroli-saints-claim", 9, 10, e("cignaroli"), c("sacred_figures_in_painting"), "cignaroli_reportedly_painted_almost_only_saints_for_years", cignaroli_quote, "Haskell says it was claimed that Cignaroli in Verona, like Barocci and Carlo Dolci, painted almost nothing but saints for years; Haskell adds that many such pictures must have been private devotional works.", "Keep 'it was claimed' and 'must have' distinct from verified commission history. Barocci and Carlo Dolci are significant parallels in Haskell's wording, not proof of identical practice.", [e("cignaroli"), c("verona"), e("barocci"), e("carlo_dolci"), c("sacred_figures_in_painting")], footnote=3)
add_statement("st-chp9-p268-church-altarpiece-market", 10, 10, c("venetian_church"), None, "church_demand_for_altarpieces_provided_a_market_for_modern_painting", source_lines[9], "Haskell says the Church's constant demand for altarpieces provided a market for modern painting lacking elsewhere.", "This is Haskell's comparative market claim; 'elsewhere' is not expanded to a named location.", [c("venetian_church"), e("venice_city")])
add_statement("st-chp9-p268-clergy-government-nobility", 11, 11, c("venetian_clergy"), e("state"), "clerics_excluded_from_political_office_but_associated_with_government_through_noble_ecclesiastical_posts", source_lines[10], "Haskell says clerics were excluded from political office yet closely associated with government because the great ecclesiastical posts were held by the nobility.", "Preserve the stated institutional explanation as Haskell's account; it does not specify every office or identify its holders.", [c("venetian_clergy"), e("state"), c("venetian_nobility"), c("venetian_church")], relation=True)
add_statement("st-chp9-p268-traveller-younger-sons", 11, 11, None, c("venetian_nobility"), "traveller_said_noble_younger_sons_lacked_other_outlets_and_trade_was_dishonourable", source_lines[10], "A traveller cited by Haskell is said to have observed that the nobility had no other outlet for younger sons because trade was considered dishonourable.", "The traveller is unnamed here; keep the report nested and do not turn it into Haskell's independently verified social rule.", [c("venetian_nobility")], speaker="unnamed traveller cited by Haskell", text_layer="nested reported observation", footnote=4)
add_statement("st-chp9-p268-church-decoration-patrician-ideals", 11, 11, c("venetian_church"), c("venetian_nobility"), "church_decoration_reflected_patrician_ideals_as_much_as_palace_decoration", source_lines[10], "Haskell says church decoration reflected patrician ideals fully as much as palace decoration.", "This is an interpretive comparison by Haskell, not a directly measured causal relation.", [c("venetian_church"), c("venetian_nobility")], relation=True)
add_statement("st-chp9-p268-sacred-history-aristocratic-projection", 12, 12, c("sacred_figures_in_painting"), c("aristocratic_principles_in_sacred_history"), "piazzetta_and_tiepolo_imagery_projects_aristocratic_principles_into_sacred_history", source_lines[11], "Haskell interprets the haughtiness of the Virgin and Saints in works by Piazzetta and Tiepolo as projection of aristocratic principles into sacred history.", "Authorial visual interpretation; preserve the comparison with most seventeenth-century religious painting without treating it as an objective property of all such works.", [c("sacred_figures_in_painting"), e("piazzetta"), e("tiepolo"), c("aristocratic_principles_in_sacred_history")], relation=True)
add_statement("st-chp9-p268-noble-commissions", 13, 13, c("venetian_nobility"), c("venetian_church"), "venetian_nobles_responsible_for_church_and_palace_commissions_and_used_favourite_artists", source_lines[12], "Haskell says many nobles were directly responsible for commissions and employed favourite artists in palaces and churches.", "This is a broad generalization; no unnamed patron or artist is converted into an individual relation.", [c("venetian_nobility"), c("venetian_church")], relation=True)
add_statement("st-chp9-p268-manin-udine-offer-1706", 14, 14, e("manin_family"), e("udine_cathedral"), "manin_offered_to_decorate_udine_cathedral_choir_transept_and_high_altar_in_1706", source_lines[13], "Haskell says the Manin offered in 1706 to decorate the choir, transept and High Altar of Udine Cathedral.", "Retain as an offer, not a completed commission; the footnote's archival quotation is not independently verified here.", [e("manin_family"), e("udine_cathedral"), e("udine_city")], relation=True, footnote=5)
add_statement("st-chp9-p268-manin-scalzi-attempt", 14, 14, e("manin_family"), e("scalzi_church_index"), "manin_unsuccessfully_tried_to_build_scalzi_church_high_altar_amid_rivalry", source_lines[13], "Haskell says the Manin unsuccessfully tried, amid rivalry, to build the High Altar of the Scalzi church in Venice.", "The building attempt failed; do not record it as a completed commission. Building/order identity remains for S3.", [e("manin_family"), e("scalzi_church_index"), e("venice_city")], relation=True)
add_statement("st-chp9-p268-manin-scalzi-chapel", 14, 14, e("manin_family"), e("scalzi_church_index"), "manin_later_took_over_decoration_of_one_scalzi_chapel", source_lines[13], "Haskell says the Manin later took over decoration of one chapel in the Scalzi church.", "No chapel name or completion date is supplied.", [e("manin_family"), e("scalzi_church_index")], relation=True)
add_statement("st-chp9-p268-manin-jesuit-church", 14, 14, e("manin_family"), e("jesuit_church_index"), "manin_responsible_for_jesuit_church_facade_and_high_altar", source_lines[13], "Haskell says the Manin were responsible for building the façade and High Altar of the Jesuit church.", "Preserve 'responsible for building'; footnote 5 cites a manuscript account but it has not been independently checked. The church and Jesuit institution remain distinct.", [e("manin_family"), e("jesuit_church_index"), e("jesuits")], relation=True, footnote=5)
add_statement("st-chp9-p268-manin-dorigny", 15, 15, e("manin_family"), e("dorigny"), "manin_employed_louis_dorigny_when_possible", source_lines[14], "Haskell says the Manin used Louis Dorigny whenever they could.", "The wording supports a broad patronage claim but supplies no individual commission dates in this segment.", [e("manin_family"), e("dorigny")], relation=True)
add_statement("st-chp9-p268-dorigny-passeriano-villa", 15, 15, e("dorigny"), e("passeriano"), "louis_dorigny_decorated_manin_villa_at_passeriano", source_lines[14], "Haskell says Louis Dorigny also decorated the Manin villa at Passeriano.", "The villa's exact building identity is not specified in this sentence.", [e("dorigny"), e("passeriano"), e("manin_family")], relation=True)
add_statement("st-chp9-p268-orders-leading-patrons", 16, 16, c("religious_orders"), e("venice_city"), "wealthy_religious_orders_were_the_most_important_patrons_of_modern_painting_and_architecture_in_early_eighteenth_century_venice", source_lines[15], "Haskell says well-backed religious orders were by far the most important patrons of modern painting and architecture in early-eighteenth-century Venice.", "Keep as the author's broad, period-specific assessment; no individual order or donor is inferred.", [c("religious_orders"), e("venice_city")], relation=True)
add_statement("st-chp9-p268-observer-complaint-partial", 16, 16, c("religious_orders"), None, "1743_observer_begins_complaint_that_monks_found_vast_sums_for_church_building", source_lines[15], "A 1743 observer begins a complaint that monks found vast sums for magnificent churches.", "The quotation ends mid-sentence at p.268 'vast' and continues on p.269; do not add the comparison with parishes until that segment is read. The source and footnote 6 will be processed from the endnote block.", [c("religious_orders")], crossrefs=[{"segment_id": NEXT_SEGMENT_ID, "source_line_start": 18, "source_line_end": 25}], speaker="unnamed observer quoted by Haskell", text_layer="nested quotation", footnote=6)

if len({row["mention_id"] for row in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID within migration")
if len({row["statement_id"] for row in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID within migration")

segment_cov.update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L7-16",
    "note": "Printed p.268 (CHP-9.pdf physical p.34) read against the scan. The p.267 sentence on Venetian piety closes at L7; Church is institutional, Venice city, State/Republic polity, and Church buildings are distinct candidates. Haskell's wealth, patronage, clerical-office and aristocratic-ideals claims retain authorial qualification; Cignaroli's painting claim remains reported and private devotion remains 'must have'. Manin offers/failed attempt/later chapel and Jesuit-church building claims are separate. Observer quotation at L16 ends mid-sentence ('vast') and continues in p.269 L18-25, so coverage is partial. OCR 'of-contemporary' is corrected against the scan in S2 only; S0 is unchanged.",
})

summary = {
    "segment": SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "new_candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "scan_corrections": ["L9 of-contemporary -> of contemporary"],
    "cross_page": {"previous": PREVIOUS_SEGMENT_ID, "next": NEXT_SEGMENT_ID},
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
