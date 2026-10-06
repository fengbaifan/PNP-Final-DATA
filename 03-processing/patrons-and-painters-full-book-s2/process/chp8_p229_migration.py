"""Controlled S2 migration for Chapter 8 printed page 229 and its citations."""
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
P228 = "chp-8:08_CHP-8_sec_ii:l206-214"
P229 = "chp-8:08_CHP-8_sec_ii:l216-225"
P230 = "chp-8:08_CHP-8_sec_ii:l227-236"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P228, P229, P230, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p229-20261001"


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
line_offsets = {}
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    lines = source_lines[meta["line_start"] - 1:meta["line_end"]]
    if hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), lines):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(line) + 1

candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
mention_fields, mention_rows = read_csv(TABLES / "mentions.csv")
statement_rows = read_jsonl(TABLES / "book-statements.jsonl")
coverage_fields, coverage_rows = read_csv(TABLES / "s2-coverage.csv")
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("duplicate S2 coverage segment IDs")
expected = {
    P228: ("reviewed", "complete", "L206-214"),
    P229: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-403":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P229 for row in mention_rows + statement_rows):
    raise SystemExit("p.229 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7830", "Marguerite d’Orléans", "person", 218,
     "Named as Cosimo III's wife and Grand Prince Ferdinand's mother; the source reports her 1675 departure for a convent at Montmartre."),
    ("cand-7831", "Violante of Bavaria", "person", 223,
     "Identified in the source only as a Bavarian princess called Violante, discovered and married to Grand Prince Ferdinand; no date or further identity is inferred."),
    ("cand-7832", "Montmartre", "place", 218,
     "Place of the convent to which Marguerite d’Orléans reportedly went in 1675; no individual convent is identified."),
    ("cand-7833", "Portugal (polity cited in failed marriage negotiations)", "institution", 222,
     "Named as a party to unsuccessful negotiations preceding Ferdinand's marriage; the other party and proposed match are not specified here."),
    ("cand-7834", "Istoria del Granducato di Toscana sotto il governo della Casa Medici (J. R. Galluzzi, Firenze 1781)", "archive", 224,
     "Bibliography identifies Galluzzi's cited history of Medici Tuscany; Haskell refers to it for the Medici family's history. The work was not independently read."),
    ("cand-7835", "La stirpe de’ Medici di Cafaggiolo (G. Pieraccini, 3 vols., Firenze 1925)", "archive", 225,
     "Bibliography identifies this three-volume Medici genealogy; Haskell recommends it for intimate family details. The cited work was not independently read."),
    ("cand-7836", "Firenze dai Medici ai Lorena (Giuseppe Conti, Firenze 1909)", "archive", 225,
     "Bibliography identifies Conti's history of Florence; Haskell recommends it for intimate family details. The cited work was not independently read."),
    ("cand-7837", "The Last Medici (Harold Acton, London 1958)", "archive", 225,
     "Bibliography identifies Acton's history of the last Medici; Haskell recommends it for intimate family details. The cited work was not independently read."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"])
                 for row in candidate_rows if not row["index_entry_id"]}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 404 else P229
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, source_line, suffix, candidate_id, surface, note, occurrence=0):
    mention_id = f"m-chp8-p229-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[source_line - 1]
    search_at = 0
    found_at = -1
    for _ in range(occurrence + 1):
        found_at = line.find(surface, search_at)
        if found_at < 0:
            raise SystemExit(f"surface not found at L{source_line}: {surface!r} #{occurrence}")
        search_at = found_at + 1
    start = line_offsets[(segment_id, source_line)] + found_at
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


mentions = [
    (P229,217,"florence-1","cand-3397","Florence","City evaluated as briefly regaining artistic prominence."),
    (P229,217,"italy-1","cand-3461","Italy","Country named in the same authorial comparison."),
    (P229,217,"ferdinand-1","cand-1609","Grand Prince Ferdinand","Index candidate for the Medici patron introduced on this page."),
    (P229,217,"plate36a","cand-4037","Plate 36a","Reference to the separately transcribed Plate 36a portrait."),
    (P229,217,"medici-1","cand-5179","Medici","Dynastic name; reuse the Medici family candidate."),
    (P229,217,"him-1","cand-1609","him","Coreference to Grand Prince Ferdinand."),
    (P229,217,"he-1","cand-1609","he","Coreference to Grand Prince Ferdinand."),
    (P229,217,"italy-2","cand-3461","Italy","Italy within the reported contemporary quotation.",1),
    (P229,218,"cosimo-iii","cand-1607","Cosimo III","Father of Grand Prince Ferdinand."),
    (P229,218,"marguerite","cand-7830","Marguerite d’Orléans","Named mother of Ferdinand; new body-mention candidate."),
    (P229,218,"florence-2","cand-3397","Florence","Place from which Marguerite reportedly left in 1675."),
    (P229,218,"montmartre","cand-7832","Montmartre","Place of the unnamed convent."),
    (P229,218,"cosimo-2","cand-1607","Cosimo himself","Second reference to Cosimo III."),
    (P229,218,"ferdinand-2","cand-1609","Ferdinand","Ferdinand, who died before ruling."),
    (P229,218,"gian-gastone-1","cand-1627","Gian Gastone","Grand Prince Ferdinand's brother."),
    (P229,218,"medici-princes","cand-5179","Medici princes","Dynastic identification; retain the family candidate."),
    (P229,218,"gian-gastone-2","cand-1627","Gian Gastone","Reference in the statement about later debauchery.",1),
    (P229,218,"europe","cand-3462","Europe","Intellectual Europe as named in Haskell's description."),
    (P229,218,"viviani","cand-2788","Viviani","Named educator; index form does not supply a forename here."),
    (P229,218,"lorenzini","cand-1440","Lorenzini","Named educator; preserve the indexed surname candidate."),
    (P229,218,"redi","cand-2112","Redi","Named educator; reuse the indexed Francesco Redi candidate."),
    (P229,220,"ferdinand-reaction","cand-1609","Ferdinand’s reaction","Coreference to Grand Prince Ferdinand."),
    (P229,220,"francesco-maria","cand-1626","Francesco Maria","The uncle named as Ferdinand's companion in the opposition."),
    (P229,220,"court","cand-5520","the court","Courtly milieu; candidate match to the Medici court remains for S3 alignment."),
    (P229,220,"marguerite-2","cand-7830","Marguerite d’Orléans","Comparison to her earlier conduct."),
    (P229,222,"venice-1","cand-3401","Venice","Destination proposed as a condition for agreeing to marriage."),
    (P229,222,"portugal","cand-7833","Portugal","Polity named in unsuccessful negotiations; details are not supplied."),
    (P229,223,"violante","cand-7831","Bavarian princess, Violante","The woman identified by Haskell as Ferdinand's eventual wife."),
    (P229,223,"court-2","cand-5520","the court","Florentine court context; candidate identity remains for S3 alignment."),
    (P229,223,"europe-2","cand-3462","Europe","Court and Europe awaiting a Medici heir."),
    (P229,223,"medici-line","cand-5179","Medici line","Dynastic succession reference."),
    (P229,223,"venice-2","cand-3401","Venice","Destination of the second, bachelor visit in 1696."),
    (P229,223,"grand-prince-coref","cand-1609","the Grand Prince","Coreference in the unfinished clause continued on p.230."),
    (P229,224,"galluzzi","cand-7834","Galluzzi","Cited publication as identified in the book bibliography."),
    (P229,225,"pieraccini","cand-7835","Pieraccini","Cited publication as identified in the book bibliography."),
    (P229,225,"conti-g","cand-7836","G. Conti","Cited publication by Giuseppe Conti as identified in the book bibliography."),
    (P229,225,"acton","cand-7837","Acton","Cited publication as identified in the book bibliography."),
    (NOTES,404,"zanotti","cand-7115","Zanotti, n, p. 50","Cited Zanotti work; OCR volume numeral is corrected from `n` to `II` in the S2 note."),
]
for row in mentions:
    mention(*row)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate, claim,
                   qualification, mentioned, text_layer="body", extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(candidate_id not in candidate_ids for candidate_id in [subject, obj, *mentioned] if candidate_id):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 229,
                  "pdf_physical_page": 31, "claim": claim, "speaker": "Haskell",
                  "text_layer": text_layer, "qualification": qualification,
                  "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj, "predicate": predicate,
            "qualifiers": qualifiers, "original_quote": quote(segment_id, first, last),
            "origin": "book", "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p229-florence-revival", P229,217,217,None,None,
                   "haskell_evaluates_florence_as_temporarily_regaining_prominence",
                   "Haskell says Florence again became Italy's most interesting city for a few years before returning to provincialism.",
                   "An authorial artistic-historical evaluation, not a measured ranking or a claim about every cultural activity.",
                   ["cand-3397","cand-3461"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p229-ferdinand-revival", P229,217,217,"cand-1609",None,
                   "presented_as_responsible_for_florentine_artistic_revival",
                   "Haskell credits Grand Prince Ferdinand with a short-lived but important artistic revival and presents him as embodying the shift from seventeenth- to eighteenth-century tastes.",
                   "The significance and period characterization are Haskell's assessment.",
                   ["cand-1609","cand-3397","cand-4037"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p229-ferdinand-patronage-quote", P229,217,217,"cand-1609",None,
                   "reported_as_munificent_patron_of_fine_arts",
                   "Haskell describes Ferdinand as a munificent patron and quotes an unidentified contemporary calling him the only support of the fine arts in Italy.",
                   "The quotation's contemporary author remains unnamed; page image confirms OCR `sine arts` reads `fine arts`. Do not turn the report into an independently verified appraisal.",
                   ["cand-1609","cand-3461"], extras={"speaker_judgment":True,"ocr_corrections":[{"source_line":217,"ocr":"sine arts","print":"fine arts","basis":"CHP-8.pdf physical page 31"}]}),
    make_statement("st-chp8-p229-taste-influenced-painting", P229,217,217,"cand-1609",None,
                   "individual_tastes_considered_important_for_painting",
                   "Haskell says Ferdinand's individual tastes were important for the development of painting.",
                   "Authorial assessment of historical importance.", ["cand-1609"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p229-birth-and-parentage", P229,218,218,"cand-1609","cand-1607",
                   "born_1663_son_of_cosimo_iii_and_marguerite_dorleans",
                   "Ferdinand was born in 1663 to Cosimo III and Marguerite d’Orléans.",
                   "Parentage and birth year are recorded as Haskell reports them; no external verification is added.",
                   ["cand-1609","cand-1607","cand-7830"], extras={"date":"1663","relation_candidate":True}),
    make_statement("st-chp8-p229-marguerite-departure", P229,218,218,"cand-7830","cand-7832",
                   "left_florence_for_montmartre_convent_in_1675",
                   "Haskell says Marguerite left Florence in 1675 for the freedom of a convent in Montmartre.",
                   "The convent is unnamed; the account's comments about its permissiveness and Marguerite's appetites are retained as Haskell's characterization.",
                   ["cand-7830","cand-3397","cand-7832"], extras={"date":"1675","relation_candidate":True}),
    make_statement("st-chp8-p229-parental-climate", P229,218,218,"cand-1607",None,
                   "parental_relationship_and_cosimos_rule_left_mark_on_sons",
                   "Haskell characterizes Cosimo and Marguerite's relationship as tempestuous and says Cosimo's pomposity and the family atmosphere left a mark on their two sons.",
                   "The psychological causal account and evaluative wording are Haskell's, not independently established facts.",
                   ["cand-1607","cand-7830","cand-1609","cand-1627"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p229-sons-status", P229,218,218,None,None,
                   "ferdinand_died_before_reigning_and_gian_gastone_was_last_medici_prince",
                   "Ferdinand died at 50 before ruling, while Gian Gastone was the last Medici prince.",
                   "The page reports both biographical claims; chronology and identity alignment remain for later review.",
                   ["cand-1609","cand-1627","cand-5179"], extras={"age_at_death":"50","relation_candidate":True}),
    make_statement("st-chp8-p229-brothers-personalities", P229,218,218,"cand-1609","cand-1627",
                   "both_brothers_described_as_intelligent_but_unstable",
                   "Haskell calls both brothers highly intelligent but unstable, and says Gian Gastone's instability eventually led to paralysing debauchery.",
                   "Psychological and moral judgments are attributed to Haskell.",
                   ["cand-1609","cand-1627"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p229-ferdinand-education", P229,218,218,"cand-1609",None,
                   "educated_by_viviani_lorenzini_and_redi",
                   "Haskell says Ferdinand was educated by Viviani, Lorenzini and Redi in Florence.",
                   "The source gives surnames only for Viviani and Lorenzini; do not expand their identities from this passage.",
                   ["cand-1609","cand-2788","cand-1440","cand-2112","cand-3397"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p229-ferdinand-character", P229,218,218,"cand-1609",None,
                   "described_as_cultivated_accomplished_and_hoped_for_change",
                   "Haskell characterizes Ferdinand as cultivated, accomplished, handsome, good-humoured and an excellent horseman, and as a hope for change from his father's rule.",
                   "These are biographical and evaluative descriptions in the source.", ["cand-1609","cand-1607"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p229-character-reconsidered", P229,219,220,"cand-1609",None,
                   "letters_and_memoirs_support_a_second_character_portrait",
                   "Haskell contrasts the public image seen by most contemporaries with a later interpretation based on letters, private memoirs and other records, describing Ferdinand as reacting against his father's 'Victorian' surroundings and drawn to equivocal pleasures.",
                   "This is Haskell's retrospective interpretation of evidence he says is available; the cited letters and memoirs are not individually identified or independently checked here. Page image corrects OCR `fife` to `life` and removes spurious punctuation after `surroundings`.",
                   ["cand-1609","cand-1607"], extras={"speaker_judgment":True,"ocr_corrections":[{"source_line":219,"ocr":"fife","print":"life","basis":"CHP-8.pdf physical page 31"},{"source_line":220,"ocr":"surroundings,. a","print":"surroundings, a","basis":"CHP-8.pdf physical page 31"},{"source_line":220,"ocr":"fife","print":"life","basis":"CHP-8.pdf physical page 31"}]}),
    make_statement("st-chp8-p229-ferdinand-francesco-opposition", P229,220,220,"cand-1609","cand-1626",
                   "led_opposition_to_cosimo_with_uncle_francesco_maria",
                   "Haskell says Ferdinand and his uncle Francesco Maria, three years older, led opposition to Cosimo; when political activity was impossible their opposition took the form of licence and wild behaviour that offended court decorum.",
                   "The age comparison, family relationship and behaviour are source claims; the moral characterization belongs to Haskell.",
                   ["cand-1609","cand-1626","cand-1607","cand-5520","cand-7830"], extras={"relation_candidate":True,"speaker_judgment":True}),
    make_statement("st-chp8-p229-marriage-and-venice-permission", P229,221,222,"cand-1609",None,
                   "marriage_agreed_with_permission_for_carnival_visit_to_venice",
                   "Haskell says marriage was insisted upon and agreed to in return for permission to visit Venice at carnival time.",
                   "The persons who insisted on and negotiated the arrangement are not named in these lines.",
                   ["cand-1609","cand-3401"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p229-portugal-negotiations", P229,222,223,"cand-1609","cand-7833",
                   "futile_marriage_negotiations_with_portugal_preceded_violante_match",
                   "After unsuccessful negotiations with Portugal, a Bavarian princess named Violante was found and married to Ferdinand.",
                   "The proposed Portuguese match and the date of Ferdinand's marriage are not supplied.",
                   ["cand-1609","cand-7833","cand-7831"], extras={"relation_candidate":True}),
    make_statement("st-chp8-p229-marriage-violante", P229,223,223,"cand-1609","cand-7831",
                   "married_violante_with_spectacular_ceremonies_but_little_love",
                   "Haskell says Violante was married to Ferdinand with spectacular ceremonies but little love.",
                   "The page supplies no marriage date; 'little love' is Haskell's characterization.",
                   ["cand-1609","cand-7831"], extras={"speaker_judgment":True,"relation_candidate":True}),
    make_statement("st-chp8-p229-heir-expectation", P229,223,223,"cand-5179",None,
                   "court_and_europe_waited_for_medici_heir",
                   "Haskell says the court and Europe waited year after year for an heir to ensure the Medici line's survival.",
                   "This is a broad authorial characterization; it does not identify individual claimants or a formal succession arrangement.",
                   ["cand-5520","cand-3462","cand-5179"], extras={"speaker_judgment":True}),
    make_statement("st-chp8-p229-second-bachelor-visit", P229,223,223,"cand-1609","cand-3401",
                   "made_bachelor_visit_to_venice_in_1696",
                   "Haskell describes a second visit to Venice in 1696 as reckless and made while Ferdinand remained a bachelor, saying it was scarcely calculated to promote the production of an heir.",
                   "The visit date is explicit; its motive and likely effect are Haskell's interpretation.",
                   ["cand-1609","cand-3401","cand-5179"], extras={"date":"1696","speaker_judgment":True}),
    make_statement("st-chp8-p229-family-called-to-provide-heir-open", P229,223,223,"cand-5179","cand-1609",
                   "other_medici_family_members_called_to_try_where_ferdinand_failed",
                   "Haskell says that in the early eighteenth century other family members were called upon to try where the Grand Prince had failed.",
                   "The sentence continues at p.230 L228 ('had failed'); the unnamed family members and outcomes remain unexpanded until that page is processed.",
                   ["cand-5179","cand-1609"], extras={"relation_candidate":True,"continuation_status":"open","continuation_expected_segment_id":P230,"continuation_expected_source_line":228}),
    make_statement("st-chp8-p229-note1-zanotti", NOTES,404,404,"cand-7115",None,
                   "footnote_cites_zanotti_volume_ii_page_50",
                   "Footnote 1 cites Zanotti, volume II, page 50, for the preceding contemporary quotation about Ferdinand's patronage.",
                   "The cited page was not independently read. The page image reads Roman numeral II; the source OCR's `n` is preserved as the raw quote and recorded as a correction.",
                   ["cand-7115","cand-1609"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p229-ferdinand-patronage-quote"],"ocr_corrections":[{"source_line":404,"ocr":"n","print":"II","basis":"CHP-8.pdf physical page 31"}]}),
    make_statement("st-chp8-p229-note2-family-bibliography", P229,224,225,None,None,
                   "footnote_recommends_four_medici_family_sources",
                   "Footnote 2 points readers to Galluzzi and recommends Pieraccini, Giuseppe Conti and Harold Acton for more intimate details about the last Medici family members.",
                   "The works are identified from the book bibliography; Haskell's cited works were not independently read. The footnote marker is 2 in the scan; the source's consolidated note text is in the body segment.",
                   ["cand-7834","cand-7835","cand-7836","cand-7837","cand-5179"], text_layer="footnote citation", extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p229-birth-and-parentage","st-chp8-p229-sons-status","st-chp8-p229-brothers-personalities"]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p228-medici-exception"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior:
    raise SystemExit("expected p.228 Medici-context statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({"continued_context_resolved_in_segment_id": P229,
                                   "continued_context_resolved_at_source_line": 217,
                                   "context_resolution_status": "resolved"})

for row in coverage_rows:
    if row["segment_id"] == P229:
        row.update({"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L216-225",
                    "note":"p.229 body and embedded n.2 reviewed against CHP-8.pdf physical page 31; closing sentence continues at p.230 L228."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L373-404",
                    "note":"p.228 n.1 at L403 and p.229 n.1 at L404 migrated; later consolidated notes remain queued by printed page."})

preview = {"mode":"dry-run","candidate_additions":len(new_candidates),"mention_additions":len(new_mentions),
           "statement_additions":len(new_statements),"context_resolved":{"statement_id":prior_id,"segment_id":P229,"line":217},
           "open_continuation":{"statement_id":"st-chp8-p229-family-called-to-provide-heir-open","segment_id":P230,"line":228},
           "coverage":{P229:"complete",NOTES:"L373-404 partial"},
           "ocr_corrections":["L217 sine arts -> fine arts","L219/L220 fife -> life","L220 remove spurious punctuation","L404 n -> II"]}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (TABLES / "entity-candidates.csv", TABLES / "mentions.csv", TABLES / "book-statements.jsonl", TABLES / "s2-coverage.csv"):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
patched_statements.extend(new_statements)
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", patched_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, coverage_rows)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
