"""Controlled S2 migration for Chapter 8 printed page 228 and note 1."""
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
P227 = "chp-8:08_CHP-8_sec_ii:l190-204"
P228 = "chp-8:08_CHP-8_sec_ii:l206-214"
P229 = "chp-8:08_CHP-8_sec_ii:l216-225"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P227, P228, P229, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p228-20261001"


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
    P227: ("reviewed", "partial", "L190-204"),
    P228: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-402":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P228 for row in mention_rows + statement_rows):
    raise SystemExit("p.228 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7824", "Four paintings commissioned by Stefano Conti from Canaletto in two pairs", "work", 207,
     "The first two paintings and another two after Conti approved the first result; titles are not supplied."),
    ("cand-7825", "Five small landscapes with ruins and figures by Marco Ricci for Stefano Conti", "work", 207,
     "A group of five paintings; Sebastiano Ricci is reported to have inserted the figures."),
    ("cand-7826", "Two proposed history pictures by Sebastiano Ricci for Stefano Conti", "work", 207,
     "Proposal for two large full-length figure paintings featuring Alexander the Great; the proposal came to nothing."),
    ("cand-7827", "Emmanuela Conti", "person", 208,
     "Named as Stefano Conti's daughter-in-law and subject of a portrait by Rosalba Carriera; no further identity inferred."),
    ("cand-7828", "Unidentified record in Biblioteca Governativa, Lucca, MS 3299 cited for Crespi's commission", "archive", 403,
     "Note 1 cites this manuscript call number together with Zanotti II, p.62; the specific item and its text are not identified or independently consulted."),
    ("cand-7829", "Unidentified late Pope cited by Giuseppe Maria Crespi as a source of prior contracts", "person", 209,
     "Unnamed Pope in Crespi's reported comparison of previous written contracts; do not infer which pontiff."),
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
    anchor_segment = NOTES if source_line >= 403 else P228
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
    mention_id = f"m-chp8-p228-{suffix}"
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
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


mentions = [
    (P228,207,"carlevarijs-1","cand-0554","Carlevarijs","Closure of the p.227 quote reporting Marchesini's assessment."),
    (P228,207,"bassi-alias","cand-0259","il Cremonese","Francesco Bassi's alias; the previous sentence is completed on this page."),
    (P228,207,"canale-name","cand-0498","Sigr. Antonio Canale","Haskell's spelling for the artist referred to as Canaletto later in the paragraph."),
    (P228,207,"venice-1","cand-3401","this city","Coreference to Venice in Marchesini's reported letter."),
    (P228,207,"marchesini","cand-1540","Marchesini","Source of the quoted assessment, as reported by Haskell."),
    (P228,207,"ricci-quoted","cand-2149","Ricci","The following narrative names Marco Ricci; keep the painter identification tied to the local context."),
    (P228,207,"london","cand-1422","London","City named as one market for the painter's works."),
    (P228,207,"poussin","cand-1984","Poussin","Artist whose architectural landscape style is used for comparison."),
    (P228,207,"conti-commission","cand-0833","Conti","Collector commissioning the Canaletto paintings."),
    (P228,207,"canaletto-1","cand-0498","Canaletto","Artist of the first two commissioned paintings and the next two."),
    (P228,207,"marco-ricci","cand-2149","Marco Ricci","Artist of five small landscapes with ruins and figures."),
    (P228,207,"marco-coreference","cand-2149","Marco’s","Coreference to Marco Ricci before the uncle relationship."),
    (P228,207,"sebastiano-ricci","cand-2154","Sebastiano","Marco Ricci's uncle, who inserted figures in the landscapes."),
    (P228,207,"alexander","cand-3442","Alexander the Great","Subject specified for the proposed history pictures."),
    (P228,207,"ricci-history","cand-2154","Ricci","Sebastiano Ricci, asked to paint the two history pictures.",2),
    (P228,207,"conti-price","cand-0833","Conti","Collector who found Ricci's proposed price exorbitant.",1),
    (P228,208,"carriera-ocr","cand-0581","Rosalba Garriera","OCR spelling; page image reads Rosalba Carriera."),
    (P228,208,"daughter-in-law","cand-7827","his daughter-in-law Emmanuela","Stefano Conti's named daughter-in-law and portrait subject."),
    (P228,208,"carriera-portrait","cand-0585","a portrait by Rosalba Garriera","Reuse indexed portrait work; title and sitter match the entry."),
    (P228,208,"conti-1728","cand-0833","he","Coreference to Stefano Conti, who commissions the painting in 1728."),
    (P228,209,"crespi","cand-0871","Crespi","Painter selected for Conti's last commission."),
    (P228,209,"conti-negotiation","cand-0833","the two men","Coreference to Conti and Crespi negotiating directly."),
    (P228,209,"grand-prince","cand-1609","the late Grand Prince Ferdinand","One of Crespi's cited sources for prior correct written contracts."),
    (P228,209,"pope","cand-7829","the late Pope","Unidentified Pope named in Crespi's contract comparison."),
    (P228,209,"eugene","cand-2384","Prince Eugene of Savoy","Named as a prior employer whose contracts Crespi cites."),
    (P228,209,"infant-title-start","cand-0879","The Infant","Beginning of the painting's original title, continued on the next source line."),
    (P228,210,"jupiter","cand-4178","Jupiter","Mythological figure in Crespi's original title."),
    (P228,210,"cybele","cand-4187","Cybele","Mythological figure in Crespi's original title."),
    (P228,210,"corybantes","cand-4188","the Corybantes","Mythological group in Crespi's original title."),
    (P228,210,"infant-title-rest","cand-0879","handed over by Cybele to the Corybantes to be fed","Remainder of the original work title; the title spans source lines 209-210."),
    (P228,211,"finding-title","cand-0879","The Finding of Moses","New title for the same 1728 Conti commission; keep separate from the similarly titled p.222 painting until S3."),
    (P228,211,"moses","cand-4144","Moses","Biblical figure in the retitled work."),
    (P228,212,"crespi-group","cand-0871","Crespi","Member of the group of later pictures in Conti's collection."),
    (P228,212,"canaletto-2","cand-0498","Canaletto","Member of the group of later pictures in Conti's collection."),
    (P228,212,"marco-ricci-2","cand-2149","Marco","Marco Ricci, member of the later picture group."),
    (P228,212,"sebastiano-ricci-2","cand-2154","Sebastiano Ricci","Member of the later picture group."),
    (P228,212,"conti-gallery","cand-0833","Conti’s collection","Collection described by Haskell as essentially old-fashioned."),
    (P228,213,"lucca","cand-1454","Lucca","Destination where commissioned paintings reached Conti."),
    (P228,213,"bologna","cand-3398","Bologna","One source city for paintings in provincial collections."),
    (P228,213,"venice","cand-3401","Venice","One source city for paintings in provincial collections."),
    (P228,213,"naples","cand-3534","Naples","One source city for paintings in provincial collections."),
    (P228,213,"rome","cand-4490","Rome","One source city for paintings in provincial collections."),
    (P228,214,"medici","cand-1609","a Medici","Immediate continuation identifies the significant exception as Grand Prince Ferdinand on p.229."),
    (NOTES,403,"repository","cand-7803","Biblioteca Governativa, Lucca","Repository named in note 1."),
    (NOTES,403,"lucca-note","cand-1454","Lucca","City locating Biblioteca Governativa."),
    (NOTES,403,"ms3299","cand-7828","MS. 3299","Specific item is not identified in the note."),
    (NOTES,403,"zanotti","cand-7115","Zanotti, II, p. 62","Reuse the identified two-volume Storia dell’Accademia Clementina citation candidate."),
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
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 228,
                  "pdf_physical_page": 30, "claim": claim, "speaker": "Haskell",
                  "text_layer": text_layer, "qualification": qualification,
                  "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj, "predicate": predicate,
            "qualifiers": qualifiers, "original_quote": quote(segment_id, first, last),
            "origin": "book", "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p228-carlevarijs-bassi-age", P228, 207, 207, "cand-1540", "cand-0554",
                   "marchesini_says_carlevarijs_old_and_bassi_blind",
                   "Haskell reports Marchesini saying Carlevarijs was old and Francesco Bassi, il Cremonese, was blind.",
                   "This closes the p.227 quotation; the condition is attributed to Marchesini, not independently verified.",
                   ["cand-1540", "cand-0554", "cand-0259"], extras={"reported_speaker": "Alessandro Marchesini", "continued_from_segment_id": P227, "continued_from_statement_id": "st-chp8-p227-carlevarijs-transformed-scene-open", "continuation_status": "closed"}),
    make_statement("st-chp8-p228-canale-landscape-praise", P228, 207, 207, "cand-1540", "cand-0498",
                   "marchesini_praises_canales_landscape_views",
                   "Marchesini praises Antonio Canale's Venetian views, comparing them with Carlevarijs while noting their sunlit quality.",
                   "Haskell reports Marchesini's quoted judgment; Canale is connected to Canaletto by the page's later naming of Canaletto.",
                   ["cand-1540", "cand-0498", "cand-0554", "cand-3401"], extras={"reported_speaker": "Alessandro Marchesini", "speaker_judgment": True}),
    make_statement("st-chp8-p228-marco-ricci-landscape-praise", P228, 207, 207, "cand-1540", "cand-2149",
                   "marchesini_praises_ricci_landscapes_and_demand",
                   "Marchesini describes a landscape painter's works as in demand in Venice and London and praises Ricci's views, Poussin-like buildings, vivid colour and distinctive manner.",
                   "The quoted description is attributed by Haskell to Marchesini; its association with Marco Ricci follows the same paragraph's explicit naming of Marco Ricci.",
                   ["cand-1540", "cand-2149", "cand-1422", "cand-3401", "cand-1984"], extras={"reported_speaker": "Alessandro Marchesini", "speaker_judgment": True}),
    make_statement("st-chp8-p228-canaletto-four-pictures", P228, 207, 207, "cand-0833", "cand-7824",
                   "commissioned_four_canaletto_paintings_in_two_pairs",
                   "Under Marchesini's pressure, Conti commissioned two paintings by Canaletto and, pleased with the result, commissioned another two; the artist was difficult over money.",
                   "The four commissions are reported by Haskell; no titles, payment amounts or independent completion record are supplied.",
                   ["cand-0833", "cand-1540", "cand-0498", "cand-7824"], extras={"relation_candidate": True, "quantity": 4}),
    make_statement("st-chp8-p228-marco-ricci-five-landscapes", P228, 207, 207, "cand-0833", "cand-7825",
                   "acquired_five_ricci_landscapes_with_figures_added_by_sebastiano",
                   "Conti eventually acquired five small landscapes with ruins and figures by Marco Ricci; Marco's uncle Sebastiano inserted the figures.",
                   "The family relationship and division of work are reported in the source; formal relations await S6 review.",
                   ["cand-0833", "cand-2149", "cand-7825", "cand-2154"], extras={"relation_candidate": True, "quantity": 5}),
    make_statement("st-chp8-p228-sebastiano-proposal-failed", P228, 207, 207, "cand-2154", "cand-7826",
                   "proposed_two_history_pictures_not_commissioned_due_to_price",
                   "Sebastiano Ricci was asked to paint two large full-length history pictures featuring Alexander the Great opposite two works by Bolognese artists; he requested a price Conti found exorbitant and the proposal came to nothing.",
                   "These are proposed but unrealized works; do not record them as completed or acquired.",
                   ["cand-2154", "cand-0833", "cand-7826", "cand-3442"], extras={"relation_candidate": True, "quantity": 2, "outcome": "proposal came to nothing"}),
    make_statement("st-chp8-p228-carriera-emmanuela-portrait", P228, 208, 208, "cand-0833", "cand-0585",
                   "bought_carriera_portrait_of_daughter_in_law_emmanuela",
                   "Conti bought a portrait by Rosalba Carriera of his daughter-in-law Emmanuela.",
                   "The page image reads Carriera; source OCR says Garriera. The portrait is reused from its indexed subentry.",
                   ["cand-0833", "cand-0581", "cand-0585", "cand-7827"], extras={"relation_candidate": True, "ocr_corrections": [{"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 208, "ocr": "Rosalba Garriera", "print": "Rosalba Carriera", "basis": "CHP-8.pdf physical page 30."}]}),
    make_statement("st-chp8-p228-crespi-1728-commission", P228, 208, 209, "cand-0833", "cand-0871",
                   "commissioned_last_crespi_picture_in_1728_after_direct_negotiation",
                   "Three years after the portrait purchase, in 1728, Conti commissioned his last picture from Crespi; negotiations were direct between them and settled after initial difficulty.",
                   "The timing and successful settlement are reported by Haskell; the precise contract is not reproduced here.",
                   ["cand-0833", "cand-0871", "cand-0585", "cand-7827"], extras={"relation_candidate": True, "date": "1728"}),
    make_statement("st-chp8-p228-crespi-contract-comparators", P228, 209, 209, "cand-0871", "cand-1609",
                   "crespi_cites_prior_correct_written_contracts",
                   "Crespi explained that he had previously received correct written contracts from the late Grand Prince Ferdinand, an unnamed late Pope, and Prince Eugene of Savoy, in whose service he then was.",
                   "This is Crespi's reported statement; the Pope remains unidentified and the prior contracts were not independently examined.",
                   ["cand-0871", "cand-1609", "cand-7829", "cand-2384"], extras={"reported_speaker": "Giuseppe Maria Crespi", "text_layer": "reported direct speech", "relation_candidate": True}),
    make_statement("st-chp8-p228-crespi-chosen-subject-sketch", P228, 209, 210, "cand-0871", "cand-0879",
                   "chose_infant_jupiter_subject_and_enclosed_sketch",
                   "After the negotiations were settled, Crespi wrote at length about his chosen subject, The Infant Jupiter handed over by Cybele to the Corybantes to be fed, and enclosed a sketch to serve as an embryo.",
                   "The work is mapped to the page-228 index entry. Keep separate from the similarly titled p.222 work candidate until S3 resolves any identity issue.",
                   ["cand-0871", "cand-0879", "cand-4178", "cand-4187", "cand-4188"], extras={"relation_candidate": True, "title_as_reported": "The Infant Jupiter handed over by Cybele to the Corybantes to be fed", "potential_same_title_candidate_id": "cand-7720", "identity_review": "defer_to_S3"}),
    make_statement("st-chp8-p228-crespi-retitles-finding-of-moses", P228, 210, 211, "cand-0871", "cand-0879",
                   "changed_title_to_finding_of_moses_for_lower_customs_duty",
                   "When the painting was sent in April 1729, Crespi changed its title to The Finding of Moses because sacred pictures paid lower customs duty than profane ones.",
                   "Haskell's explanation is retained as reported motive; this title belongs to the p.228 Conti commission and is not merged with p.222's separate candidate.",
                   ["cand-0871", "cand-0879", "cand-4144"], extras={"relation_candidate": True, "date": "1729-04", "title_change": True}),
    make_statement("st-chp8-p228-four-artists-style-isolation", P228, 212, 212, "cand-0833", "cand-0871",
                   "later_picture_group_looked_isolated_in_old_fashioned_collection",
                   "Haskell says the pictures by Crespi, Canaletto, Marco Ricci and Sebastiano Ricci, with nervous brush strokes and dramatic light contrasts, must have looked isolated among Conti's essentially old-fashioned paintings.",
                   "The style and isolation are Haskell's art-historical judgment, not an objective classification of the works.",
                   ["cand-0833", "cand-0871", "cand-0498", "cand-2149", "cand-2154"], extras={"speaker_judgment": True}),
    make_statement("st-chp8-p228-conti-taste-accredited-works", P228, 212, 212, "cand-0833", "cand-7785",
                   "did_not_expand_picture_group_and_favoured_accredited_works",
                   "Conti did not increase the number of these pictures; Haskell characterizes his taste as unadventurous and says his main interest was filling the gallery with accredited works.",
                   "The evaluation of Conti's taste and interest belongs to Haskell.",
                   ["cand-0833", "cand-0871", "cand-0498", "cand-2149", "cand-2154", "cand-7785"], extras={"speaker_judgment": True}),
    make_statement("st-chp8-p228-provincial-collection-limitation", P228, 212, 213, None, None,
                   "provincial_patron_could_not_view_commissions_until_arrival",
                   "Haskell generalizes that patrons in small towns who ordered pictures from elsewhere could not see commissioned works until they reached them; he calls this a limitation of provincial collections.",
                   "This is Haskell's account of a common provincial collecting pattern, not a claim about every patron or every work.",
                   ["cand-0833", "cand-1454"], extras={"speaker_judgment": True, "scope": "generalization"}),
    make_statement("st-chp8-p228-provincial-artists-isolated", P228, 213, 213, None, None,
                   "imported_pictures_could_enrich_local_taste_but_isolate_artists",
                   "Haskell says pictures from Bologna, Venice, Naples and Rome could enrich local taste, while the artists remained isolated from one another and from guidance by a cultivated patron.",
                   "This is an authorial generalization about provincial collections.",
                   ["cand-3398", "cand-3401", "cand-3534", "cand-4490"], extras={"speaker_judgment": True, "scope": "generalization"}),
    make_statement("st-chp8-p228-medici-exception", P228, 213, 214, "cand-1609", None,
                   "medici_figure_was_exception_to_provincial_isolation",
                   "Haskell introduces one significant exception to provincial artistic isolation and identifies the most important figure in this interregnum as a Medici; the following page names Grand Prince Ferdinand.",
                   "The Medici reference is resolved from the immediate p.229 continuation; preserve Haskell's periodization and evaluation.",
                   ["cand-1609", "cand-3398", "cand-3401", "cand-3534", "cand-4490"], extras={"speaker_judgment": True, "continued_context_segment_id": P229, "continued_context_source_line": 217}),
    make_statement("st-chp8-p228-note1-ms3299-zanotti", NOTES, 403, 403, "cand-7828", "cand-7115",
                   "footnote_cites_lucca_ms3299_and_zanotti_volume_ii_page_62",
                   "Note 1 cites Biblioteca Governativa, Lucca, MS 3299 and Zanotti, volume II, page 62, for the Crespi commission passage.",
                   "This records Haskell's source locator only; the manuscript and cited page were not independently read.",
                   ["cand-7828", "cand-7803", "cand-1454", "cand-7115", "cand-0871", "cand-0879"], text_layer="footnote citation", extras={"relation_candidate": False, "linked_body_statement_ids": ["st-chp8-p228-crespi-1728-commission", "st-chp8-p228-crespi-chosen-subject-sketch", "st-chp8-p228-crespi-retitles-finding-of-moses"]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p227-carlevarijs-transformed-scene-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.227 Carlevarijs statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({"continuation_status": "closed", "continuation_to_segment_id": P228,
                                    "continuation_to_source_line": 207, "continued_to_segment_id": P228,
                                    "continued_to_source_line": 207,
                                    "continuation_closed_by_statement_id": "st-chp8-p228-carlevarijs-bassi-age"})

for row in coverage_rows:
    if row["segment_id"] == P227:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L190-204",
                    "note": "p.227 pricing statement closes at L191; Carlevarijs quotation closes at p.228 L207."})
    elif row["segment_id"] == P228:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L206-214",
                    "note": "p.228 read against CHP-8.pdf physical page 30; p.227 continuation closes at L207."})
    elif row["segment_id"] == NOTES:
        row.update({"source_line_ranges": "L373-403", "migration_status": "partial",
                    "note": "p.228 note 1 at L403 migrated; later consolidated notes remain queued by printed page."})

preview = {"mode": "dry-run", "candidate_additions": len(new_candidates), "mention_additions": len(new_mentions),
           "statement_additions": len(new_statements),
           "closed_continuation": {"statement_id": prior_id, "to": P228, "line": 207},
           "coverage": {P227: "complete", P228: "complete", NOTES: "L373-403 partial"},
           "ocr_corrections": ["L208 Rosalba Garriera -> Rosalba Carriera"]}

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
