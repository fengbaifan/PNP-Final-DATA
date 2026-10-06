"""Controlled S2 migration of p.269, including closure of the p.268 quotation."""
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
SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l18-25"
PREVIOUS_SEGMENT_ID = "chp-9:09_CHP-9_sec_ii:l6-16"
PREVIOUS_QUOTE_STATEMENT_ID = "st-chp9-p268-observer-complaint-partial"
EXPECTED_SEGMENT_SHA = "908c9e9ac8a5a25f91200eec9d2680beb6b8345dceb66b88392c96b51bd7530d"
EXPECTED_ASSET_SHA = "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923"
EXPECTED_MAX_CANDIDATE = 8681
BACKUP_SUFFIX = ".bak-s2-chp9-p269-retry-20261001"


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
    raise SystemExit("p.269 segment is missing or changed")
if segments[SEGMENT_ID].get("asset_sha256") != EXPECTED_ASSET_SHA:
    raise SystemExit("p.269 source asset fingerprint mismatch")
if not source_lines[18].startswith("sums to build their magnificent and splendid churches"):
    raise SystemExit("expected p.269 quotation continuation has changed")
if not source_lines[20].startswith("The Scalzi, for instance, a particularly strict off-shoot"):
    raise SystemExit("expected p.269 Scalzi passage has changed")
segment_text = "\n".join(source_lines[17:25])
line_offsets = {}
offset = 0
for line_no in range(18, 26):
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
previous_cov = coverage_by_id.get(PREVIOUS_SEGMENT_ID)
segment_cov = coverage_by_id.get(SEGMENT_ID)
if not previous_cov or (previous_cov["disposition"], previous_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"unexpected p.268 coverage state: {previous_cov}")
if not segment_cov or (segment_cov["disposition"], segment_cov["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"unexpected p.269 coverage state: {segment_cov}")
previous_quote = next((row for row in statements if row["statement_id"] == PREVIOUS_QUOTE_STATEMENT_ID), None)
if not previous_quote or previous_quote["segment_id"] != PREVIOUS_SEGMENT_ID:
    raise SystemExit("p.268 quotation fragment statement is missing")

EXISTING = {
    "venetian_church": "cand-8672",
    "religious_orders": "cand-8675",
    "venetian_nobility": "cand-8677",
    "jesuits": "cand-1322",
    "dominicans": "cand-0941",
    "carmelites": "cand-0563",
    "oratorians": "cand-1783",
    "capuchins": "cand-0539",
    "scalzi_order": "cand-2389",
    "scalzi_church": "cand-0738",
    "carmelite_order": "cand-0563",
    "venice": "cand-2724",
    "peloponnese": "cand-8117",
    "longhena": "cand-1423",
    "sardi": "cand-2360",
    "cavazza": "cand-0614",
    "christ": "cand-4910",
    "mary_magdalene": "cand-5861",
    "st_peters_basilica": "cand-6960",
    "rome": "cand-4490",
}
for key, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {key}={candidate_id}")

CANDIDATE_SPECS = [
    ("parishes", "Venetian parish churches as a collective comparison group in Haskell's p.269 passage", "term", "Collective comparison group in the continuation of the observer's complaint; no individual parish church is identified by this phrase.", 19),
    ("s_toma", "S. Toma church in Venice (as named by Haskell at p.269)", "place", "Specific parish church named as rapidly rebuilt or richly decorated; S0 spelling is retained in the title pending authority control.", 19),
    ("s_vitale", "S. Vitale church in Venice (as named by Haskell at p.269)", "place", "Specific parish church named as rapidly rebuilt or richly decorated; keep distinct from the choir and fresco cycle candidates elsewhere.", 19),
    ("s_matteo", "S. Matteo di Rialto church in Venice (as named by Haskell at p.269)", "place", "Specific parish church used in Haskell's reported example of a 1735 renovation; the citation is not independently checked here.", 19),
    ("scalzi_original_church", "Unnamed original church of the Scalzi in Venice (p.269 account)", "place", "The church that Haskell says became too small before Longhena and Sardi were employed to build a new one; keep distinct from the later Scalzi church candidate.", 21),
    ("scalzi_monastery", "Scalzi monastery in Venice (the community's monastery in the 1732 pamphlet account)", "place", "The monastery discussed in the pamphleteer's defence; no further building identity is supplied in this passage.", 24),
    ("venetian_troops_peloponnese", "Venetian troops in the Peloponnese as a collective military referent", "term", "Unnamed troops in Haskell's account of the Scalzi's missionary context; no unit or campaign is identified.", 21),
    ("venetian_patriciate", "Venetian patriciate as a social and legal estate in Haskell's p.269 account", "term", "The social estate into which Haskell says Conte Cavazza was admitted in 1653; do not infer a named admission decree.", 22),
    ("st_marks_church", "St Mark's church in Venice as invoked by the 1732 pamphleteer", "place", "Church invoked as a comparison in the pamphlet's defence of magnificence; the passage uses 'St Mark's in Venice' without a separate formal title.", 24),
    ("venetian_public", "Venetian public as a collective source of alms in Haskell's account", "term", "Unspecified public said to be generous toward the monks; no individual donors or organized body are inferred.", 25),
    ("scalzi_arrival_1633", "Arrival of the Scalzi at Venice in 1633", "event", "Haskell reports the Scalzi came to Venice in 1633; retain as the source's date and wording, not an independently checked foundation date.", 21),
    ("matteo_renovation_1735", "Renovation of S. Matteo di Rialto after alms collection in 1735", "event", "Haskell reports that the priest collected alms in 1735 and that the church was renovated within months; preserve the nested report and its citation boundary.", 19),
    ("cavazza_admission_1653", "Admission of Conte Cavazza to the Venetian patriciate in 1653", "event", "Haskell reports Cavazza had been admitted to the patriciate in 1653; the admission record is not independently checked.", 23),
    ("scalzi_pamphlet_defence_1732", "Call for an anonymous pamphleteer to defend the Scalzi church expense in 1732", "event", "Haskell says an anonymous pamphleteer was called upon to justify the church expense in 1732; note 5 identifies a cited pamphlet whose publication date/source detail will be migrated later.", 23),
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


def m(key):
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


add_mention("m-chp9-p269-jesuits", 19, e("jesuits"), "the Jesuits", "Named religious order in the observer's nested quotation; index-candidate identity remains for S3.")
add_mention("m-chp9-p269-dominicans-quote", 19, e("dominicans"), "Dominicans", "Named religious order in the observer's nested quotation.")
add_mention("m-chp9-p269-parishes-quote", 19, m("parishes"), "the parishes", "Collective parish-church comparison in the observer's quotation.")
add_mention("m-chp9-p269-parish-churches", 19, m("parishes"), "Parish churches", "Haskell's own examples following the observer's complaint.")
add_mention("m-chp9-p269-s-toma", 19, m("s_toma"), "S. Toma", "S0 spelling retained; the scan reads S. Tomà. Specific building named by Haskell.")
add_mention("m-chp9-p269-s-vitale", 19, m("s_vitale"), "S. Vitale", "Specific parish church, distinct from the previously indexed choir and fresco cycle.")
add_mention("m-chp9-p269-s-matteo", 19, m("s_matteo"), "S. Matteo di Rialto", "Specific parish church in Haskell's reported renovation example.")
add_mention("m-chp9-p269-renovation-year", 19, m("matteo_renovation_1735"), "1735", "Year attached to the reported alms collection and renovation sequence.")
add_mention("m-chp9-p269-carmelites", 19, e("carmelites"), "Carmelites", "Named order in Haskell's account of church decoration.")
add_mention("m-chp9-p269-dominicans-patrons", 19, e("dominicans"), "Dominicans", "Second occurrence: named order in Haskell's account of church decoration.", 1)
add_mention("m-chp9-p269-oratorians", 20, e("oratorians"), "Oratorians", "Named order in Haskell's account of church decoration.")
add_mention("m-chp9-p269-capuchins", 20, e("capuchins"), "Capuchins", "Named order in Haskell's account of church decoration.")
add_mention("m-chp9-p269-scalzi-order", 21, e("scalzi_order"), "The Scalzi", "Here refers to the religious order, not its church building.")
add_mention("m-chp9-p269-carmelite-order", 21, e("carmelite_order"), "Carmelite Order", "Order affiliation stated explicitly in Haskell's description.")
add_mention("m-chp9-p269-venice-arrival", 21, e("venice"), "Venice", "City of arrival, not the Republic as political actor.")
add_mention("m-chp9-p269-peloponnese", 21, e("peloponnese"), "Peloponnese", "Place of the Scalzi's reported missionary work.")
add_mention("m-chp9-p269-venetian-troops", 21, m("venetian_troops_peloponnese"), "Venetian troops", "Unnamed collective military referent; no unit is inferred.")
add_mention("m-chp9-p269-original-church", 21, m("scalzi_original_church"), "their original church", "Unidentified earlier building, kept distinct from the replacement church.")
add_mention("m-chp9-p269-longhena", 21, e("longhena"), "Longhena", "Reuse the p.269 index candidate.")
add_mention("m-chp9-p269-sardi", 22, e("sardi"), "Sardi", "Reuse the p.269 index candidate.")
add_mention("m-chp9-p269-new-scalzi-church", 22, e("scalzi_church"), "a new one", "The replacement Scalzi church; use the existing index seed whose subentry identifies S. Maria di Nazareth, with identity reviewed at S3.")
add_mention("m-chp9-p269-nobles-altar", 22, e("venetian_nobility"), "Nobles", "Collective patrons competing for the High Altar privilege.")
add_mention("m-chp9-p269-cavazza-title", 22, e("cavazza"), "Conte", "Title is at the end of L22; the surname wraps to L23. Do not expand the identity beyond the index seed.")
add_mention("m-chp9-p269-cavazza-surname", 23, e("cavazza"), "Cavazza", "Surname continues the wrapped name from L22.")
add_mention("m-chp9-p269-patriciate", 23, m("venetian_patriciate"), "patriciate", "Social/legal estate into which Haskell says Cavazza was admitted.")
add_mention("m-chp9-p269-cavazza-admission-year", 23, m("cavazza_admission_1653"), "1653", "Year attached to the reported admission.")
add_mention("m-chp9-p269-order-praise", 23, e("scalzi_order"), "an austere Order", "The Scalzi Order, contrasted with its church's luxury.")
add_mention("m-chp9-p269-pamphlet-year", 23, m("scalzi_pamphlet_defence_1732"), "1732", "Year Haskell gives for the pamphleteer's intervention.")
add_mention("m-chp9-p269-christ", 23, e("christ"), "Christ", "Biblical figure used in the pamphleteer's rhetorical defence.")
add_mention("m-chp9-p269-mary-magdalene", 23, e("mary_magdalene"), "Mary Magdalene", "Biblical figure used in the pamphleteer's rhetorical defence.")
add_mention("m-chp9-p269-st-peters", 23, e("st_peters_basilica"), "St Peter’s", "Church building invoked in the pamphleteer's argument, not Peter as an acting person.")
add_mention("m-chp9-p269-rome", 23, e("rome"), "Rome", "City locating St Peter's church.")
add_mention("m-chp9-p269-st-marks-prefix", 23, m("st_marks_church"), "St", "The church name wraps across source lines L23–24; this is its first token.")
add_mention("m-chp9-p269-st-marks-surname", 24, m("st_marks_church"), "Mark’s", "Church name continues from L23; the passage does not supply a formal title.")
add_mention("m-chp9-p269-venice-st-marks", 24, e("venice"), "Venice", "City locating St Mark's church.")
add_mention("m-chp9-p269-monastery", 24, m("scalzi_monastery"), "the monastery", "The Scalzi monastery discussed in the anonymous pamphleteer's defence.")
add_mention("m-chp9-p269-monks-condition", 24, e("religious_orders"), "the monks", "Monastic community in the pamphleteer's reported account.")
add_mention("m-chp9-p269-order-poverty", 24, e("scalzi_order"), "the Order", "The Scalzi Order's poverty ideal, not the building.")
add_mention("m-chp9-p269-public-alms", 25, m("venetian_public"), "the Venetian public", "Unspecified collective described as generous to the monks.")
add_mention("m-chp9-p269-church-luxury", 25, e("scalzi_church"), "their church", "The replacement Scalzi church, whose luxury is the pamphleteer's topic.")

new_statements = []


def add_statement(statement_id, line_start, line_end, subject, object_, predicate, quote, claim, qualification, mentioned, *, relation=False, crossrefs=(), speaker="Haskell", text_layer="authorial narrative", footnote=None):
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote not anchored in p.269 segment: {statement_id}")
    refs = set(mentioned)
    refs.update(candidate for candidate in (subject, object_) if candidate)
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown statement candidate in {statement_id}: {sorted(refs - candidate_ids)}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 269,
        "pdf_physical_page": 35,
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


quote_continuation = source_lines[18].split(" The complaint was not wholly justified")[0]
haskell_rebuttal = source_lines[18].split(" The complaint was not wholly justified. ", 1)[1].split(" So too was S. Matteo")[0]
matteo_report = "So too was " + source_lines[18].split("So too was ", 1)[1].split(" But it is true")[0]
orders_painting = "But it is true that " + source_lines[18].split("But it is true that ", 1)[1] + "\n" + source_lines[19]
scalzi_arrival_quote = source_lines[20].split(" After some difficulties")[0]
scalzi_links_quote = "After some difficulties " + source_lines[20].split("After some difficulties ", 1)[1].split(" Such was their popularity")[0]
new_church_quote = "Such was their popularity " + source_lines[20].split("Such was their popularity ", 1)[1] + "\n" + source_lines[21].split(" Nobles quarrelled")[0]
frontage_praise_quote = source_lines[22][source_lines[22].index("Though it was widely praised"):source_lines[22].index(" such luxury became")]
scalzi_luxury_quote = source_lines[22][source_lines[22].index("such luxury became"):].split(" It was not true")[0]
pamphleteer_poverty_quote = source_lines[23][source_lines[23].index("It was not true that such a rich church"):source_lines[23].index(" It was not true that the monastery")]
pamphleteer_monastery_quote = source_lines[23][source_lines[23].index("It was not true that the monastery"):]
pamphlet_taste_quote = source_lines[24][source_lines[24].index("But the most interesting"):]

add_statement("st-chp9-p269-1743-observer-complaint-continuation", 19, 19, e("religious_orders"), c("parishes"), "observer_contrasted_monastic_church_funds_with_small_parish_support_and_long_waits", quote_continuation, "The 1743 observer's quotation continues that monks found vast sums for magnificent churches, including those of the Jesuits and Dominicans, while parishes received little help and waited years for their churches.", "Nested quotation begun on p.268 L16; cross-reference that opening fragment. Haskell immediately qualifies the complaint. Footnote 6's cited source will be migrated with the endnote block.", [e("jesuits"), e("dominicans"), c("parishes"), e("venetian_church")], crossrefs=[{"segment_id": PREVIOUS_SEGMENT_ID, "source_line_start": 16, "source_line_end": 16}], speaker="unnamed observer quoted by Haskell", text_layer="nested quotation", footnote=6)
add_statement("st-chp9-p269-parish-rebuilds-rebuttal", 19, 19, c("parishes"), None, "haskell_says_some_parish_churches_were_rebuilt_or_decorated_rapidly", haskell_rebuttal, "Haskell says the complaint was not wholly justified and gives S. Toma and S. Vitale as parish churches rebuilt or richly decorated with remarkable speed.", "This is Haskell's qualification of the observer's complaint; do not infer that all parish churches received equal support.", [c("parishes"), c("s_toma"), c("s_vitale")])
add_statement("st-chp9-p269-matteo-renovation-1735", 19, 19, m("matteo_renovation_1735"), m("s_matteo"), "s_matteo_di_rialto_renovated_within_months_after_1735_alms_collection", matteo_report, "Haskell reports that after the priest collected alms from parishioners and other pious people in 1735, S. Matteo di Rialto was renovated within a few months.", "The quoted report is nested and the cited note 1 source has not been independently read. The scan restores the printed note marker 1 and S. Tomà accent elsewhere on the page.", [m("matteo_renovation_1735"), m("s_matteo"), c("parishes")], relation=True, footnote=1)
add_statement("st-chp9-p269-orders-churches-filled-with-art", 19, 20, e("religious_orders"), None, "churches_of_four_orders_filled_with_striking_paintings_and_frescoes_after_1720", orders_painting, "Haskell says that for about a quarter century after 1720 churches of the Carmelites, Dominicans, Oratorians and Capuchins were filled with many striking paintings and frescoes.", "Retain 'about' and the author's assessment 'many of the most striking'; the scan reads 'striking paintings' without the OCR apostrophe.", [e("carmelites"), e("dominicans"), e("oratorians"), e("capuchins"), e("religious_orders")], relation=True)
add_statement("st-chp9-p269-scalzi-arrival-1633", 21, 21, m("scalzi_arrival_1633"), e("scalzi_order"), "scalzi_came_to_venice_in_1633_as_a_strict_carmelite_offshoot", scalzi_arrival_quote, "Haskell describes the Scalzi as a particularly strict offshoot of the Carmelite Order and says they came to Venice in 1633.", "Keep the order affiliation and the reported arrival distinct from the identity of its churches; note 2 is a citation, not independent verification.", [m("scalzi_arrival_1633"), e("scalzi_order"), e("carmelite_order"), e("venice")], footnote=2)
add_statement("st-chp9-p269-scalzi-noble-links-missions", 21, 21, e("scalzi_order"), e("venetian_nobility"), "scalzi_became_linked_with_leading_nobles_and_gained_sympathy_through_missions_and_troop_associations", scalzi_links_quote, "Haskell says the Scalzi became closely linked with leading nobles and gained special sympathy through missionary work in the Peloponnese and association with Venetian troops there.", "This is Haskell's account of the order's social and missionary context; no specific troop unit or noble patron is named.", [e("scalzi_order"), e("venetian_nobility"), e("peloponnese"), m("venetian_troops_peloponnese")], relation=True)
add_statement("st-chp9-p269-scalzi-original-church-too-small", 21, 22, e("scalzi_order"), m("scalzi_original_church"), "scalzi_popularity_made_original_church_too_small_and_longhena_sardi_hired_for_replacement", new_church_quote, "Haskell says the Scalzi's popularity made their original church too small and that Longhena and Sardi were employed to build a new one.", "The unnamed original church and replacement building remain distinct; do not infer the new church's name from the index subentry alone.", [e("scalzi_order"), m("scalzi_original_church"), e("longhena"), e("sardi"), e("scalzi_church")], relation=True)
add_statement("st-chp9-p269-nobles-competed-for-high-altar", 22, 22, e("venetian_nobility"), e("scalzi_church"), "nobles_quarrelled_for_privilege_to_erect_scalzi_church_high_altar", source_lines[21], "Haskell says nobles quarrelled for the privilege of erecting the High Altar in the replacement Scalzi church.", "A competition for a privilege is not evidence that every competitor completed work.", [e("venetian_nobility"), e("scalzi_church"), e("scalzi_order")], relation=True)
facade_cavazza_quote = source_lines[21] + "\n" + source_lines[22].split("3. Though it was widely praised", 1)[0]
cavazza_admission_quote = source_lines[22].split("3. Though it was widely praised", 1)[0]
add_statement("st-chp9-p269-cavazza-paid-facade", 22, 23, e("cavazza"), e("scalzi_church"), "conte_cavazza_paid_74000_ducats_for_scalzi_church_facade", facade_cavazza_quote, "Haskell says the façade cost 74,000 ducats and was paid for by a Conte Cavazza.", "The title and surname are split across source lines L22–23; preserve the amount as reported and do not identify the patron beyond the indexed candidate.", [e("cavazza"), e("scalzi_church")], relation=True, footnote=3)
add_statement("st-chp9-p269-cavazza-admission-patriciate", 23, 23, m("cavazza_admission_1653"), e("cavazza"), "conte_cavazza_admitted_to_venetian_patriciate_in_1653", cavazza_admission_quote, "Haskell says Conte Cavazza had been admitted to the patriciate in 1653.", "Admission date and status are reported by Haskell; no register or decree is independently checked.", [m("cavazza_admission_1653"), e("cavazza"), m("venetian_patriciate")], footnote=3)
add_statement("st-chp9-p269-frontage-praise", 23, 23, e("scalzi_church"), None, "scalzi_church_facade_reportedly_praised_as_europes_most_magnificent", frontage_praise_quote, "Haskell reports that the façade was widely praised as the most magnificent not just in Venice but possibly in all Europe.", "Preserve 'widely praised' and 'possibly'; this is reported reception, not a measured ranking.", [e("scalzi_church"), e("venice")], footnote=4)
add_statement("st-chp9-p269-scalzi-luxury-pamphlet", 23, 23, m("scalzi_pamphlet_defence_1732"), e("scalzi_order"), "luxury_embarrassed_austere_scalzi_order_and_anonymous_pamphleteer_called_to_justify_expense_in_1732", scalzi_luxury_quote, "Haskell says the church's luxury embarrassed the austere Order and that an anonymous pamphleteer was called upon in 1732 to justify the expense.", "The anonymous speaker remains unnamed; note 5 identifies the cited pamphlet but is processed later with the endnote segment.", [m("scalzi_pamphlet_defence_1732"), e("scalzi_order"), e("scalzi_church")], footnote=5)
poverty_relief_quote = source_lines[22][source_lines[22].index("It was not true, he commented"):] + "\n" + source_lines[23].split(" Worship of God", 1)[0]
add_statement("st-chp9-p269-pamphleteer-poor-relief-argument", 23, 24, m("scalzi_pamphlet_defence_1732"), None, "pamphleteer_rejected_claim_that_church_funds_better_spent_on_poverty_relief", poverty_relief_quote, "The pamphleteer rejects the claim that the money would have been better spent relieving poverty and invokes Christ, Mary Magdalene, St Peter's in Rome and St Mark's in Venice.", "Nested argument attributed to the anonymous pamphleteer, not to Haskell as a direct factual claim; preserve the biblical and church analogies as rhetoric.", [m("scalzi_pamphlet_defence_1732"), e("christ"), e("mary_magdalene"), e("st_peters_basilica"), e("rome"), m("st_marks_church"), e("venice")], speaker="anonymous pamphleteer quoted by Haskell", text_layer="nested pamphlet argument", footnote=5)
add_statement("st-chp9-p269-pamphleteer-worship-priority", 24, 24, m("scalzi_pamphlet_defence_1732"), None, "pamphleteer_said_worship_of_god_as_important_as_care_for_poor", source_lines[23].split(" Worship of God")[1].split(" It was not true")[0], "The pamphleteer argues that worship of God was fully as important as looking after the poor.", "Retain as the pamphleteer's normative argument.", [m("scalzi_pamphlet_defence_1732"), e("scalzi_order")], speaker="anonymous pamphleteer quoted by Haskell", text_layer="nested pamphlet argument", footnote=5)
add_statement("st-chp9-p269-pamphleteer-poverty-spirit", 24, 24, m("scalzi_pamphlet_defence_1732"), e("scalzi_order"), "pamphleteer_said_rich_church_consistent_with_order_poverty_if_living_quarters_austere", pamphleteer_poverty_quote, "The pamphleteer says a rich church did not conflict with the Order's poverty when living quarters remained austere, while the Tabernacle of God was to be built magnificently.", "Nested defence of the Order's practice; do not read the architectural distinction as proof of actual expenditure beyond Haskell's report.", [m("scalzi_pamphlet_defence_1732"), e("scalzi_order"), e("scalzi_church")], speaker="anonymous pamphleteer quoted by Haskell", text_layer="nested pamphlet argument", footnote=5)
add_statement("st-chp9-p269-pamphleteer-monastery-finances", 24, 24, m("scalzi_pamphlet_defence_1732"), m("scalzi_monastery"), "pamphleteer_denied_monastery_despoiled_and_said_monks_condition_unchanged_no_capital_or_debts", pamphleteer_monastery_quote, "The pamphleteer denies that the monastery was despoiled for the church, says the monks' condition had not changed, and says the monastery had no capital and no debts.", "Nested claims from the pamphlet as reported by Haskell; no independent financial record is cited in this segment.", [m("scalzi_pamphlet_defence_1732"), m("scalzi_monastery"), e("scalzi_order")], speaker="anonymous pamphleteer quoted by Haskell", text_layer="nested pamphlet argument", footnote=5)
add_statement("st-chp9-p269-benefactions-and-public-alms", 25, 25, m("venetian_public"), e("scalzi_order"), "benefactions_considerable_and_venetian_public_generous_to_monks_despite_church_luxury", source_lines[24], "Haskell says benefactions had been considerable and the Venetian public was too generous to withhold alms from the monks because of the church's luxury.", "Broad authorial summary; the particular donors and sums are not specified here.", [m("venetian_public"), e("scalzi_order"), e("scalzi_church")])
add_statement("st-chp9-p269-pamphlet-taste-objection", 25, 25, m("scalzi_pamphlet_defence_1732"), None, "pamphleteers_most_interesting_objection_concerned_taste_not_morals", pamphlet_taste_quote, "Haskell says the pamphleteer's most interesting complaint concerned taste rather than morals.", "This sentence previews the next page's continuation; retain the contrast as Haskell's assessment of the pamphlet's argument.", [m("scalzi_pamphlet_defence_1732")], speaker="Haskell describing pamphleteer", text_layer="authorial narrative")

if len({row["mention_id"] for row in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention ID within migration")
if len({row["statement_id"] for row in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement ID within migration")

previous_quote["qualifiers"]["qualification"] = "The p.268 quotation fragment is closed by its continuation at p.269 L19, which is linked from this row and recorded as a separate continuation statement. Footnote 6's cited source will be processed with the section's endnote block."
previous_quote["qualifiers"]["cross_reference_segments"] = [{"segment_id": SEGMENT_ID, "source_line_start": 19, "source_line_end": 19}]
previous_cov.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L7-16",
    "note": "Printed p.268 body has been read and its observer quotation fragment at L16 is now closed by p.269 L19. The p.268 segment remains anchored to its own lines; p.269 records the quote continuation and Haskell's qualification. OCR 'of-contemporary' was corrected against the scan in S2 only; S0 is unchanged.",
})
segment_cov.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L19-25",
    "note": "Printed p.269 (CHP-9.pdf physical p.35) read against the scan. Closes the 1743 observer quotation from p.268; Haskell qualifies it with parish-church examples. Distinguishes parish buildings, the Scalzi Order, its original church, replacement church and monastery. The 1732 pamphleteer's claims remain nested and are not independently verified. S2 scan corrections: S0 'S. Toma' reads 'S. Tomà'; OCR 'A1' is footnote 1; 'striking'paintings' reads 'striking paintings'. Footnote citations are scheduled in the section endnote segment; S0 unchanged.",
})

summary = {
    "segment": SEGMENT_ID,
    "previous_segment_closed": PREVIOUS_SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "new_candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "scan_corrections": ["S. Toma -> S. Tomà", "A1 -> printed note 1", "striking'paintings -> striking paintings"],
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
