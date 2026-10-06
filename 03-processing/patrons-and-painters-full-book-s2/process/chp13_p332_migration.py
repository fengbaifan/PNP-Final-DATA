"""Controlled S2 migration for the opening printed page of chapter 13.

The default is a dry run. Apply only after reviewing the candidate mappings,
mentions, claims, and OCR corrections below.
"""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
HEADER_SEGMENT = "chp-13:13_CHP-13_intro:l1-1"
BODY_SEGMENT = "chp-13:13_CHP-13_intro:l3-12"
NOTES_SEGMENT = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p332-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the reviewed p.332 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[0] != "# 13 CHP-13 intro":
    raise SystemExit("generated Markdown heading changed")
expected_prefixes = {
    3: "[Page 2]",
    4: "Chapter 13",
    5: "PUBLISHERS AND CONNOISSEURS",
    6: "HERE was in Venice during the eighteenth century",
    7: "Tcontacts with the rest of Europe",
    8: "We know from many travellers",
    9: "Many publishers therefore wished",
    10: "In the long run these laws",
    11: "Venice,’ not all of whom",
    12: "’forties,are books like Carlevarijs’Le Fabriche",
}
for line_no, prefix in expected_prefixes.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f"canonical source changed at L{line_no}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
candidate_ids = set(candidate_by_id)
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (9963, 9976, 21145, 9391):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (HEADER_SEGMENT, BODY_SEGMENT, NOTES_SEGMENT):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
if (coverage[HEADER_SEGMENT]["disposition"], coverage[HEADER_SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("generated heading segment is not queued/pending")
if (coverage[BODY_SEGMENT]["disposition"], coverage[BODY_SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.332 body segment is not queued/pending")
if any(row["segment_id"] in {HEADER_SEGMENT, BODY_SEGMENT} for row in mentions):
    raise SystemExit("mentions already exist for p.332 segments")
if any(row["segment_id"] in {HEADER_SEGMENT, BODY_SEGMENT} for row in statements):
    raise SystemExit("statements already exist for p.332 segments")
if "cand-9977" in candidate_ids or "cand-9978" in candidate_ids:
    raise SystemExit("planned source-derived candidate ID already exists")
if any(row["mention_id"].startswith("m-s2-ch13-p332-") for row in mentions):
    raise SystemExit("p.332 mention IDs already exist")
if any(row["statement_id"].startswith("st-chp13-p332-") for row in statements):
    raise SystemExit("p.332 statement IDs already exist")

required_candidates = {
    "cand-0025", "cand-0554", "cand-0555", "cand-1063", "cand-1235",
    "cand-1452", "cand-1453", "cand-1546", "cand-2569", "cand-2719",
    "cand-2723", "cand-3462", "cand-4653", "cand-5317", "cand-5529",
    "cand-8105", "cand-8983", "cand-2068",
}
missing_candidates = required_candidates - candidate_ids
if missing_candidates:
    raise SystemExit(f"expected S1/body candidates missing: {sorted(missing_candidates)}")
if candidate_by_id["cand-0555"].get("sub_entry") != "Le Fabriche e Vedute di Venetia":
    raise SystemExit("Carlevarijs index subentry changed")
if candidate_by_id["cand-1453"].get("sub_entry") != "Il Gran Teatro delle Pitture e Prospettive di Venezia":
    raise SystemExit("Lovisa index subentry changed")

body_lines = {line_no: source_lines[line_no - 1] for line_no in range(3, 13)}
segment_text = "\n".join(body_lines[line_no] for line_no in range(3, 13))

new_candidates = []


def add_candidate(cid, name, kind, detail, line_no):
    if cid in candidate_ids or any(row["candidate_id"] == cid for row in new_candidates):
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{BODY_SEGMENT}#L{line_no}",
    })
    new_candidates.append(row)


add_candidate(
    "cand-9977",
    "Michele Marieschi’s views of Venice (1741; title unspecified)",
    "work",
    "Source-derived work-group candidate: Haskell says views by Marieschi dated 1741 appealed to Fragonard during a later visit to Venice. The passage gives no title, number, or individual view; preserve this as an unidentified group and do not merge it with other Marieschi works.",
    12,
)
add_candidate(
    "cand-9978",
    "Venetian book-publishing copyright monopoly mechanism (twenty-year term as described at p.332)",
    "procedure",
    "Source-derived legal mechanism: Haskell describes advantageous copyright laws granting twenty-year monopolies, used to encourage illustrated-book exports and affecting the quality of books aimed at the local market. No law title, enactment date, or precise scope is supplied.",
    9,
)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(line_no, surface, cid, note="", occurrence=0):
    if cid not in all_candidate_ids:
        raise SystemExit(f"unknown candidate for mention: {surface!r} {cid}")
    line = body_lines[line_no]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text missing at L{line_no}: {surface!r} occurrence {occurrence}")
    start = sum(len(body_lines[n]) + 1 for n in range(3, line_no)) + starts[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch at L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p332-{len(new_mentions) + 1:03d}",
        "segment_id": BODY_SEGMENT,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": note,
    })
    new_mentions.append(row)


add_mention(7, "Europe", "cand-3462")
add_mention(6, "Venice", "cand-2719", "The city as the setting of Venetian publishing.")
add_mention(7, "book publishers", "cand-2068")
add_mention(7, "Venetian", "cand-2719", "Adjectival reference to Venice and its publishing economy.", 0)
add_mention(7, "Republic’s", "cand-8105", "The Venetian political entity; not the city as a place.")
add_mention(7, "Venetian", "cand-2719", "Adjectival reference to the city's publishing pre-eminence.", 1)
add_mention(7, "aristocratic regime", "cand-8105", "Political regime whose criticism is the condition in Haskell's censorship account.")
add_mention(7, "censorship", "cand-2723")
add_mention(7, "Grosley", "cand-1235", "Traveller quoted by Haskell; the source is not independently consulted.")
add_mention(7, "françois", "cand-5317", "French works in the quoted French passage; surface form follows S0 OCR.")
add_mention(7, "Paris", "cand-4653")
add_mention(7, "Venetian", "cand-2719", "Adjectival reference to books issued from Venice.", 2)
add_mention(8, "Venetians", "cand-2719", "Demonym for residents, linked to the city as context; not an individual person or organization.")
add_mention(9, "publishers", "cand-2068")
add_mention(9, "government", "cand-8105", "The governing entity acting through copyright law, distinct from Venice as a place.")
add_mention(9, "copyright laws", "cand-9978")
add_mention(10, "these laws", "cand-9978", "Anaphora to the copyright laws named at L9.")
add_mention(10, "twenty-year monopolies", "cand-9978")
add_mention(10, "Venetian", "cand-2719", "Adjectival reference to the local book market.")
add_mention(10, "English", "cand-8983", "National audience named as a target market; not a claim about all English readers.")
add_mention(10, "French", "cand-5317", "National audience named as a target market.")
add_mention(10, "German", "cand-5529", "National audience named as a target market.")
add_mention(11, "Venice", "cand-2719")
add_mention(11, "the city", "cand-2719", "Anaphoric reference to Venice.")
add_mention(12, "Carlevarijs", "cand-0554")
add_mention(12, "Le Fabriche e Vedute di Venetia", "cand-0555", "Title as printed/OCRed; the index subentry ties it to Carlevarijs.")
add_mention(12, "Venetia", "cand-2719", "City named within the title; nested inside the work-title mention.")
add_mention(12, "II Gran Teatro delle Pitture e Prospettive di Venezia", "cand-1453", "S0 OCR reads ‘II’; CHP-13.pdf physical page 1 reads ‘Il’. The index supplies this work subentry under Lovisa.")
add_mention(12, "Venezia", "cand-2719", "City named within the work title; nested inside the title mention.")
add_mention(12, "Domenico Lovisa", "cand-1452")
add_mention(12, "Tiepolo", "cand-2569", "The passage says ‘young Tiepolo’; retain the source's age qualifier without a date or identity alignment.")
add_mention(12, "Marieschi", "cand-1546", "Artist named as creator of a set of views; nested in the work-group mention.")
add_mention(12, "Marieschi’s views of 1741", "cand-9977", "Unspecified views as a group, not an individually titled or counted work.")
add_mention(12, "Fragonard", "cand-1063")
add_mention(12, "Venice", "cand-2719", "Destination of Fragonard's later visit; no exact visit date is supplied.")

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for i, left in enumerate(new_mentions):
    left_start, left_end = int(left["start_char"]), int(left["end_char"])
    for right in new_mentions[i + 1:]:
        right_start, right_end = int(right["start_char"]), int(right["end_char"])
        if right_start >= left_end:
            break
        strict_nested = (
            (left_start <= right_start and right_end <= left_end and (left_start, left_end) != (right_start, right_end))
            or (right_start <= left_start and left_end <= right_end and (left_start, left_end) != (right_start, right_end))
        )
        if not strict_nested:
            raise SystemExit(f"crossing or duplicate mention spans: {left['mention_id']} / {right['mention_id']}")
if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention ID already exists")

new_statements = []


def excerpt(line_no, start_text, end_text):
    line = body_lines[line_no]
    start = line.find(start_text)
    if start < 0:
        raise SystemExit(f"quote start missing at L{line_no}: {start_text!r}")
    end = line.find(end_text, start)
    if end < 0:
        raise SystemExit(f"quote end missing at L{line_no}: {end_text!r}")
    return line[start:end + len(end_text)]


def cross_line_excerpt(first_line, last_line, start_text, end_text):
    text = "\n".join(body_lines[n] for n in range(first_line, last_line + 1))
    start = text.find(start_text)
    end = text.find(end_text, start)
    if start < 0 or end < 0:
        raise SystemExit(f"cross-line quote boundary missing: {start_text!r} / {end_text!r}")
    return text[start:end + len(end_text)]


OCR_CORRECTIONS = [
    {"source_line": 6, "ocr": "HERE was", "print": "THERE was", "basis": "CHP-13.pdf physical page 1; initial drop capital T is split from the OCR line."},
    {"source_line": 7, "ocr": "Tcontacts", "print": "contacts", "basis": "CHP-13.pdf physical page 1; the drop capital belongs before HERE at L6."},
    {"source_line": 11, "ocr": "Venice,’", "print": "Venice;", "basis": "CHP-13.pdf physical page 1."},
    {"source_line": 12, "ocr": "’forties,are", "print": "’forties, are", "basis": "CHP-13.pdf physical page 1."},
    {"source_line": 12, "ocr": "Carlevarijs’Le", "print": "Carlevarijs’ Le", "basis": "CHP-13.pdf physical page 1."},
    {"source_line": 12, "ocr": "II Gran Teatro", "print": "Il Gran Teatro", "basis": "CHP-13.pdf physical page 1."},
    {"source_line": 12, "ocr": "the’limitations", "print": "the limitations", "basis": "CHP-13.pdf physical page 1."},
]


def add_statement(suffix, subject, obj, predicate, line_start, line_end, claim, quote, qualification, mentioned,
                  *, speaker="Haskell", layer="authorial narrative", extra=None):
    statement_id = f"st-chp13-p332-{suffix}"
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"statement ID already exists: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"statement quote is not anchored in S0: {statement_id}")
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned-candidate FK: {statement_id}")
    for cid in (subject, obj):
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"missing statement endpoint FK: {statement_id}: {cid}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 332,
        "pdf_physical_page": 1,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
    }
    if line_start <= 7 <= line_end or line_start <= 11 <= line_end or line_start <= 12 <= line_end:
        qualifiers["ocr_corrections"] = [correction for correction in OCR_CORRECTIONS if line_start <= correction["source_line"] <= line_end]
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": BODY_SEGMENT,
        "subject_candidate_id": subject or None,
        "object_candidate_id": obj or None,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })


def footnote(marker):
    return {
        "footnote_marker": marker,
        "footnote_text_pending": True,
        "footnote_segment": NOTES_SEGMENT,
        "footnote_body_link_status": "pending",
        "cross_reference_segments": [NOTES_SEGMENT],
    }


first_sentence = cross_line_excerpt(6, 7, "HERE was", "international taste.")
publishing_history = excerpt(7, "Ever since the sixteenth century", "field.1")
republic_effort = excerpt(7, "in the last hundred years", "field.1")
censorship_quote = excerpt(7, "As long as criticism", "fairly lax:")
grosley_quote = excerpt(7, "the traveller Grosley noted that", "permission tacite’,2")
market_quote = excerpt(7, "and this helped to create", "Venetian books.")
bookshop_quote = body_lines[8]
export_aim_quote = body_lines[9]
law_effect_quote = cross_line_excerpt(10, 11, "In the long run these laws", "greatly gained.")
travel_demand_quote = cross_line_excerpt(10, 11, "Moreover, the increasing number of travellers", "good engraving.")
early_books_quote = cross_line_excerpt(11, 12, "The best works of the early years", "young Tiepolo.")
lovisa_book_quote = excerpt(12, "II Gran Teatro", "young Tiepolo.")
traveller_design_quote = excerpt(12, "Both of these publications", "travellers")
marieschi_traveller_design_quote = excerpt(12, "as were Marieschi’s views of 1741", "many years later.")
marieschi_quote = excerpt(12, "as were Marieschi’s views", "many years later.5")
illustration_quote = excerpt(12, "In fact, for the first time", "book illustrating.")
format_quote = excerpt(12, "And because of the very different market", "large-scale painting.")

add_statement(
    "publishers-european-ties-and-patronage", "cand-2068", "cand-3462", "close_european_contacts_and_extensive_art_patronage",
    6, 7,
    "Haskell characterizes eighteenth-century Venetian publishers as a section of society with close contacts across Europe and extensive art patronage attuned to international taste.",
    first_sentence,
    "This is Haskell's broad characterization of the publisher group, not a claim about every publisher or a named patronage transaction.",
    ["cand-2068", "cand-3462", "cand-2719"],
)
add_statement(
    "publishing-role-in-venetian-economy", "cand-2068", "cand-2719", "book_publishing_important_to_venetian_economy_since_sixteenth_century",
    7, 7,
    "Haskell says book publishers had played an important role in the Venetian economy since the sixteenth century.",
    publishing_history,
    "A long-run characterization; the passage gives no economic measure or named publisher for the whole period.",
    ["cand-2068", "cand-2719"],
    extra=footnote(1),
)
add_statement(
    "republic-efforts-to-maintain-publishing-supremacy", None, None, "efforts_made_to_uphold_venetian_publishing_supremacy",
    7, 7,
    "Haskell says substantial, sometimes successful efforts were made to preserve Venetian supremacy in publishing during the Republic's last hundred years; the sentence does not identify who made them.",
    republic_effort,
    "The period is Haskell's approximate description of the Republic's final century; no specific law, official, or success measure is named.",
    ["cand-8105", "cand-2068", "cand-2719"],
    extra=footnote(1),
)
add_statement(
    "conditional-lax-censorship", "cand-2723", "cand-8105", "censorship_fairly_lax_when_regime_criticism_avoided",
    7, 7,
    "Haskell says censorship remained fairly lax on the condition that criticism of the aristocratic regime was avoided.",
    censorship_quote,
    "Conditional and comparative wording is retained; this does not mean censorship was absent or uniformly applied.",
    ["cand-2723", "cand-8105"],
)
add_statement(
    "grosley-venice-paris-publication-permission-report", "cand-1235", "cand-2719", "reported_publication_permission_comparison",
    7, 7,
    "Haskell quotes traveller Grosley contrasting daily permitted publication of French translations in Venice with Paris, where such works allegedly appeared only under tacit permission.",
    grosley_quote,
    "This is Grosley's quoted observation as mediated by Haskell, not an independently checked account of censorship law. The text specifically concerns translations of French works.",
    ["cand-1235", "cand-2719", "cand-4653", "cand-5317"],
    speaker="Pierre Jean Grosley as quoted by Haskell",
    layer="reported traveller observation and quotation",
    extra={**footnote(2), "quotation_language": "French"},
)
add_statement(
    "lax-censorship-and-international-book-market", "cand-2068", "cand-2719", "permissive_censorship_helped_create_international_market_for_venetian_books",
    7, 7,
    "Haskell connects the relatively permissive censorship context to the creation of an international market for Venetian books.",
    market_quote,
    "The causal link is Haskell's account; the passage does not quantify the market or isolate censorship as its only cause.",
    ["cand-2068", "cand-2719", "cand-2723", "cand-8105"],
    layer="authorial interpretation",
)
add_statement(
    "bookshops-cultural-contact", "cand-2719", None, "bookshops_as_centres_of_cultural_life_and_contact",
    8, 8,
    "Haskell summarizes travellers' descriptions of Venetian bookshops as cultural centres where contact with Venetians was especially possible.",
    bookshop_quote,
    "The individual travellers and shops are unnamed; the claim is attributed to Haskell's summary of traveller accounts.",
    ["cand-2719"],
    layer="authorial summary of traveller accounts",
    extra=footnote(3),
)
add_statement(
    "publishers-export-illustrated-books", "cand-2068", None, "sought_to_produce_lavishly_illustrated_books_for_export",
    9, 9,
    "Haskell says many Venetian publishers wished to produce lavishly illustrated books for export.",
    export_aim_quote,
    "This records publishers' stated aim as summarized by Haskell, not a claim that every intended book was completed or exported.",
    ["cand-2068"],
)
add_statement(
    "government-copyright-encouragement", "cand-8105", "cand-9978", "encouraged_export_illustrated_books_through_copyright_laws",
    9, 10,
    "Haskell says the government encouraged the export-book policy by enforcing advantageous copyright laws, which granted twenty-year monopolies.",
    export_aim_quote + "\n" + excerpt(10, "In the long run these laws", "twenty-year monopolies,"),
    "No law title, enactment date, legal text, or exact scope is supplied. The passage describes the policy's claimed mechanism.",
    ["cand-8105", "cand-9978", "cand-2068"],
    extra={**footnote(4), "relation_candidate": True},
)
add_statement(
    "copyright-effects-on-local-and-export-books", "cand-9978", "cand-2068", "twenty_year_monopolies_affected_local_and_export_book_markets",
    10, 11,
    "Haskell says the twenty-year copyright monopolies eventually lowered the quality of books aimed at the Venetian market, while luxury editions for English, French, and German amateurs gained.",
    cross_line_excerpt(10, 11, "In the long run these laws", "greatly gained."),
    "Preserve Haskell's contrast between local and export-oriented editions; no quantitative measure, named edition, or country-specific sales figure is given.",
    ["cand-9978", "cand-2068", "cand-2719", "cand-8983", "cand-5317", "cand-5529"],
    layer="authorial interpretation",
    extra=footnote(4),
)
add_statement(
    "travellers-created-demand-for-engraving", None, None, "growth_in_travel_and_limited_access_created_demand_for_engraving",
    10, 12,
    "Haskell links the increasing number of travellers to Venice, many lacking original city views or access to copyists, with new demand for good engraving.",
    travel_demand_quote,
    "The travellers are unnamed and their inability to acquire views or hire copyists is stated as a general tendency, not a universal condition.",
    ["cand-2068", "cand-2719"],
    layer="authorial interpretation",
)
add_statement(
    "carlevarijs-le-fabriche-1703-example", "cand-0555", "cand-0554", "listed_as_1703_example_of_early_illustrated_venetian_publication",
    11, 12,
    "Haskell names Luca Carlevarijs's Le Fabriche e Vedute di Venetia (1703) as an example of the early-century illustrated publications preceding the revival of the 1730s and 1740s.",
    early_books_quote,
    "The association is expressed through the possessive title attribution; the passage does not identify a printer, patron, or commissioning arrangement.",
    ["cand-0555", "cand-0554", "cand-2719"],
    layer="authorial characterization",
    extra={"relation_candidate": True},
)
add_statement(
    "lovisa-gran-teatro-publication-and-illustrations", "cand-1453", "cand-1452", "published_in_1720_with_drawings_and_pictures_by_artists",
    12, 12,
    "Haskell says Domenico Lovisa published Il Gran Teatro delle Pitture e Prospettive di Venezia in 1720, with drawings of monuments and pictures by several artists.",
    lovisa_book_quote,
    "The OCR title form ‘II’ is visually read as ‘Il’; the named book remains the indexed Lovisa subentry. No complete artist list is supplied.",
    ["cand-1453", "cand-1452", "cand-2719"],
    layer="authorial narrative",
    extra={"relation_candidate": True},
)
add_statement(
    "gran-teatro-includes-tiepolo-pictures", "cand-1453", "cand-2569", "included_pictures_by_young_tiepolo",
    12, 12,
    "Haskell says the 1720 Il Gran Teatro included pictures by several artists, among them the young Tiepolo.",
    lovisa_book_quote,
    "‘Young’ is retained as Haskell's relative age description; this passage gives no age or exact date for the pictures.",
    ["cand-1453", "cand-2569"],
    layer="authorial narrative",
    extra={"relation_candidate": True},
)
add_statement(
    "le-fabriche-designed-for-travellers", "cand-0555", None, "designed_for_travellers",
    12, 12,
    "Haskell says Le Fabriche e Vedute di Venetia was designed for travellers.",
    traveller_design_quote,
    "The demonstrative ‘these publications’ refers to Le Fabriche e Vedute di Venetia and Il Gran Teatro; travellers are an audience group, not an individually identified endpoint.",
    ["cand-0555", "cand-1453"],
)
add_statement(
    "gran-teatro-designed-for-travellers", "cand-1453", None, "designed_for_travellers",
    12, 12,
    "Haskell says Il Gran Teatro was designed for travellers.",
    traveller_design_quote,
    "The demonstrative ‘these publications’ refers to Il Gran Teatro and Le Fabriche e Vedute di Venetia; travellers are an audience group, not an individually identified endpoint.",
    ["cand-1453", "cand-0555"],
)
add_statement(
    "marieschi-views-designed-for-travellers", "cand-9977", None, "designed_for_travellers",
    12, 12,
    "Haskell's phrase ‘as were Marieschi's views’ also describes the 1741 views as designed for travellers.",
    marieschi_traveller_design_quote,
    "This continues the audience statement about the two named illustrated books; the views remain an unspecified work group.",
    ["cand-9977", "cand-1546"],
)
add_statement(
    "marieschi-views-appealed-to-fragonard", "cand-9977", "cand-1063", "views_appealed_to_fragonard_during_later_venice_visit",
    12, 12,
    "Haskell says Marieschi's views dated 1741 appealed to Fragonard on a visit to Venice many years later.",
    marieschi_quote,
    "No individual view, title, or Fragonard visit date is identified. The candidate is an unspecified group of views; no specific work or purchase is inferred.",
    ["cand-9977", "cand-1546", "cand-1063", "cand-2719"],
    layer="authorial narrative",
    extra={"relation_candidate": True, **footnote(5)},
)
add_statement(
    "artists-labour-on-book-illustration", None, None, "leading_artists_devoted_substantial_labour_to_book_illustration",
    12, 12,
    "Haskell says many leading artists devoted much of their labour and talent to book illustration for the first time in two or three hundred years.",
    illustration_quote,
    "This is a broad periodization by Haskell; the passage does not identify all artists or quantify the labour involved.",
    [],
    layer="authorial characterization",
)
add_statement(
    "book-illustration-market-format-limits", None, None, "market_size_and_technique_shaped_book_illustrations",
    12, 12,
    "Haskell says the different market, size, and technique of book illustration often produced work unlike artists' familiar large-scale paintings.",
    format_quote,
    "This is Haskell's comparative assessment, not a judgement about every illustrated work or every artist.",
    [],
    layer="authorial interpretation",
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
if len({row["candidate_id"] for row in all_candidates}) != len(all_candidates):
    raise SystemExit("duplicate candidate IDs")
if len({row["mention_id"] for row in all_mentions}) != len(all_mentions):
    raise SystemExit("duplicate mention IDs")
if len({row["statement_id"] for row in all_statements}) != len(all_statements):
    raise SystemExit("duplicate statement IDs")
for row in new_statements:
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"statement endpoint candidate missing: {row['statement_id']}")

coverage[HEADER_SEGMENT].update({
    "disposition": "excluded",
    "migration_status": "complete",
    "source_line_ranges": "L1-1",
    "note": "Excluded: generated Markdown filename heading only; it is not printed book content. The substantive chapter title and text begin in the next segment.",
})
coverage[BODY_SEGMENT].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L3-12",
    "note": "Printed p.332 body reviewed against CHP-13.pdf physical page 1 and migrated. The S0 split-drop-cap, punctuation, spacing, and Il/II title readings are recorded in statement qualifiers. Footnote markers 1–5 point to the later consolidated note segment L179–251 and remain pending; page body stays partial until those notes are processed and linked.",
})

candidate_rows = sorted(all_candidates, key=lambda row: row["candidate_id"])
mention_rows = sorted(all_mentions, key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
coverage_rows = [coverage[row["segment_id"]] for row in coverage_rows]

print(f"p.332 dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage: generated heading -> excluded/complete; printed p.332 body -> reviewed/partial pending notes 1–5")
print(f"totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(all_statements)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
