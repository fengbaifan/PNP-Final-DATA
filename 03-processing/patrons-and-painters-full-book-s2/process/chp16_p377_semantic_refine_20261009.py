"""Controlled semantic refinement for chapter 16 p.377 and its p.376 continuation."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "16_CHP-16_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-16.pdf"
STATEMENTS = TABLES / "book-statements.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
BODY = "chp-16:16_CHP-16_intro:l48-64"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
P376 = "chp-16:16_CHP-16_intro:l38-46"
P378 = "chp-16:16_CHP-16_intro:l66-67"
SOURCE_FILE = "02-sources/02-Markdown/16_CHP-16_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp16-p377-semantic-review-20261009"
UNSET = object()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write after all guards and checks pass")
args = parser.parse_args()

EXPECTED = {
    SOURCE: "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff",
    PDF: "6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f",
    STATEMENTS: "25ab0c979e651c100b69d3b0ce8b6a194382887ff9695db92b6ae82b624345dc",
    CANDIDATES: "b7d2071809f6174391a18e2b7e14489d8268a5cacc94ea3911ebac4968a42993",
    MENTIONS: "b6c722d4f1e3849e05bdd63c276b3eeb846bdae68ecc681fafc29ab18ac123b0",
}
for path, expected in EXPECTED.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"baseline changed for {path.relative_to(ROOT)}: {actual}")

lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_text = "\n".join(lines[47:64])
note_text = "\n".join(lines[68:89])
for n, text in {
    49: "ones caused, some anxiety to the Inquisitors of State",
    52: "Luigi Celotti, who survived the downfall of the Republic",
    55: "he owned—and, of course, sold—old masters of all sorts",
    56: "Of his eight Canalettos",
    57: "His Sebastiano Ricci pastoral scene",
    58: "composition fougueuse",
    59: "In all these men, so similar in their status and their place in society",
    64: "His papers and manuscripts are mentioned in the Archivio di Stato",
    87: "The miniatures are described by William Young Ottley.",
    88: "Noticele Tableaux",
    89: "In 1814 he sold some more Tiepolos and also Piazzettas",
}.items():
    if text not in lines[n - 1]:
        raise SystemExit(f"source line {n} changed: {text}")

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)

def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)

def norm(text):
    return " ".join(text.split())

def check_quote(segment, quote):
    haystack = body_text if segment == BODY else note_text
    if norm(quote) not in norm(haystack):
        raise SystemExit(f"quote not found in {segment}: {quote!r}")

with STATEMENTS.open(encoding="utf-8-sig") as f:
    statements = [json.loads(line) for line in f if line.strip()]
cand_fields, candidates = read_csv(CANDIDATES)
mention_fields, mentions = read_csv(MENTIONS)
S = {r["statement_id"]: r for r in statements}
C = {r["candidate_id"]: r for r in candidates}
if len(S) != len(statements) or len(C) != len(candidates):
    raise SystemExit("duplicate IDs in current table")
if sum(r.get("segment_id") == BODY for r in statements) != 29:
    raise SystemExit("p.377 first-pass statement count changed")

required = [
    "st-chp16-p377-swajer-inquisitors-conclusion",
    "st-chp16-p377-swajer-in-contact-with-giambattista-tiepolo",
    "st-chp16-p377-swajer-negotiated-gian-domenico-commissions",
    "st-chp16-p377-celotti-dealer-characterization",
    "st-chp16-p377-celotti-survived-republic-fall",
    "st-chp16-p377-celotti-at-home-in-all-regimes",
    "st-chp16-p377-celotti-assembled-and-dispersed-collections",
    "st-chp16-p377-celotti-miniatures-from-papal-choral-books",
    "st-chp16-p377-celotti-owned-and-sold-old-masters",
    "st-chp16-p377-celotti-owned-eighteenth-century-venetian-paintings",
    "st-chp16-p377-haskell-infers-celotti-salesmanship-and-taste",
    "st-chp16-p377-celotti-eight-canaletto-paintings",
    "st-chp16-p377-celotti-four-canalettos-with-tiepolo-figures",
    "st-chp16-p377-celotti-tiepolo-friendship-as-catalogue-wording",
    "st-chp16-p377-celotti-sebastiano-ricci-pastoral",
    "st-chp16-p377-celotti-tiepolo-rape-of-ganymede-sketch",
    "st-chp16-p377-celotti-tiepolo-allegorical-sketch",
    "st-chp16-p377-haskell-generalizes-dealers-collections-and-patronage",
    "st-chp16-p377-note3-christies-miniatures",
    "st-chp16-p377-note3-state-archive-locator",
    "st-chp16-p377-note4-celotti-1807-catalogue",
    "st-chp16-p377-note5-celotti-1814-sale",
    "st-chp16-p376-swajer-secret-manuscripts-partial",
    "st-chp16-p377-note1-levi-celotti-date",
    "st-chp16-p378-group-livelihood-and-old-masters-demand",
    "st-chp16-p378-group-collected-artists-affected-by-taste-change",
    "st-chp16-p378-group-retrospective-venetian-tradition",
]
if any(i not in S for i in required):
    raise SystemExit(f"required statement missing: {[i for i in required if i not in S]}")

def revise(sid, quote, start, end, *, claim, qualification, predicate=UNSET,
           subject=UNSET, obj=UNSET, mentioned=None, relation=UNSET, qset=None,
           speaker=None, text_layer=None):
    row = S[sid]
    check_quote(row["segment_id"], quote)
    row["original_quote"] = quote
    q = row.setdefault("qualifiers", {})
    q.update({"source_line_start": start, "source_line_end": end,
              "claim": claim, "qualification": qualification})
    if predicate is not UNSET: row["predicate"] = predicate
    if subject is not UNSET: row["subject_candidate_id"] = subject
    if obj is not UNSET: row["object_candidate_id"] = obj
    if mentioned is not None: q["mentioned_candidate_ids"] = mentioned
    if relation is not UNSET: q["relation_candidate"] = relation
    if speaker is not None: q["speaker"] = speaker
    if text_layer is not None: q["text_layer"] = text_layer
    if qset: q.update(qset)

def correction(sid, line, ocr, printed):
    q = S[sid]["qualifiers"]
    corr = q.setdefault("ocr_corrections", [])
    item = {"source_file": SOURCE_FILE, "source_line": line, "ocr": ocr,
            "print": printed, "basis": "CHP-16.pdf physical page 5."}
    if item not in corr: corr.append(item)

def add_statement(sid, segment, start, end, subject, predicate, obj, quote,
                  claim, qualification, mentioned, *, speaker="Haskell",
                  text_layer="authorial report", relation=False, extra=None):
    if sid in S: raise SystemExit(f"statement ID already exists: {sid}")
    check_quote(segment, quote)
    q = {"source_line_start": start, "source_line_end": end,
         "printed_page": 377, "pdf_physical_page": 5,
         "claim": claim, "speaker": speaker, "text_layer": text_layer,
         "qualification": qualification, "mentioned_candidate_ids": mentioned,
         "relation_candidate": relation}
    if extra: q.update(extra)
    row = {"statement_id": sid, "segment_id": segment,
           "subject_candidate_id": subject, "object_candidate_id": obj,
           "predicate": predicate, "qualifiers": q, "original_quote": quote,
           "origin": "book", "source_file": SOURCE_FILE}
    statements.append(row)
    S[sid] = row
    return row

# Swajer's p.376 sentence continuation: separate the reported anxiety from acquisition.
revise("st-chp16-p377-swajer-inquisitors-conclusion",
       "ones caused, some anxiety to the Inquisitors of State",49,49,
       predicate="possible_dispersal_of_swajers_secret_manuscripts_reported_to_have_caused_anxiety",
       subject="cand-2534",obj=None,
       claim="Haskell reports that possible dispersal of Swajer's secret manuscripts caused anxiety to the Inquisitors of State.",
       qualification="The report concerns possible dispersal and the Inquisitors' reaction; it does not by itself establish acquisition.",
       mentioned=["cand-2534","cand-10643","cand-10524"],relation=False)
revise("st-chp16-p377-swajer-in-contact-with-giambattista-tiepolo",
       "in touch with a number of artists, notably Giambattista Tiepolo",49,49,
       claim="Haskell says Swajer was in touch with Giambattista Tiepolo.",
       qualification="This records contact only; the passage does not specify friendship or a commission with Giambattista Tiepolo.",
       mentioned=["cand-2534","cand-2569"])
revise("st-chp16-p377-swajer-negotiated-gian-domenico-commissions",
       "Domenico on whose behalf he negotiated a few commissions",49,50,
       claim="Haskell says Swajer negotiated a few commissions on behalf of Gian Domenico Tiepolo.",
       qualification="The nearest antecedent is Gian Domenico; neither the commissions nor their patrons are identified.",
       mentioned=["cand-2534","cand-2624"])
acquired_id="st-chp16-p377-swajer-inquisitors-acquired-secret-manuscripts"
add_statement(acquired_id,BODY,49,49,"cand-10524","acquired_swajers_secret_manuscripts","cand-10643",
              "who acquired them all.",
              "Haskell says the Inquisitors of State acquired all of Swajer's secret manuscripts.",
              "This is Haskell's reported account; the officials and manuscripts are not individually identified.",
              ["cand-10524","cand-10643"],relation=True,extra={
                  "cross_reference_segments":[P376],
                  "cross_reference_statement_ids":["st-chp16-p376-swajer-secret-manuscripts-partial"],
                  "cross_reference_text":"Completes p.376 L46: p.377 identifies the Inquisitors' reaction and says they acquired all the manuscripts.",
                  "cross_reference_text_pending":False,"predicate_status":"complete"})
add_statement("st-chp16-p377-swajer-in-touch-with-gian-domenico-tiepolo",BODY,49,50,
              "cand-2534","was_in_touch_with_gian_domenico_tiepolo","cand-2624",
              "in touch with a number of artists, notably Giambattista Tiepolo and his son Gian\nDomenico",
              "Haskell says Swajer was in touch with Gian Domenico Tiepolo as well as Giambattista Tiepolo.",
              "The passage states contact, not friendship; the commissions mentioned next were negotiated on Gian Domenico's behalf.",
              ["cand-2534","cand-2569","cand-2624"],relation=True)

revise("st-chp16-p377-celotti-dealer-characterization",
       "A much more adventurous and successful dealer than any of these was the Abate\nLuigi Celotti,",51,52,
       claim="Haskell characterizes Celotti as a more adventurous and successful dealer than those previously discussed.",
       qualification="This is Haskell's comparative evaluation, not an independently measured ranking.",mentioned=["cand-0622","cand-0126"],relation=False)
revise("st-chp16-p377-celotti-survived-republic-fall",
       "Luigi Celotti, who survived the downfall of the Republic by half a century.1",52,52,
       claim="Haskell says Celotti survived the fall of the Republic by half a century.",
       qualification="No exact death date is inferred here; note 1 separately reports about 1846.",
       mentioned=["cand-0622","cand-8838"],qset={
           "footnote_marker":"1","footnote_segment":NOTES,"footnote_line_range":"L85-L85",
           "footnote_text_pending":False,"footnote_body_link_status":"linked",
           "footnote_body_line_range":"L52","footnote_note_statement_ids":["st-chp16-p377-note1-levi-celotti-date"],
           "footnote_link_note":"Printed note 1 after the half-century statement cites Levi for Celotti's approximate death date."})
revise("st-chp16-p377-celotti-at-home-in-all-regimes",
       "But hewas at home in all regimes—as long as there were clients to buy his pictures.",52,52,
       claim="Haskell characterizes Celotti as at home in any regime so long as clients bought his pictures.",
       qualification="This is Haskell's account of adaptability, not a specific political office.",mentioned=["cand-0622"])
correction("st-chp16-p377-celotti-at-home-in-all-regimes",52,"hewas","he was")
revise("st-chp16-p377-celotti-assembled-and-dispersed-collections",
       "Constantly building up collections and then dispersing them",52,52,
       predicate="constantly_built_up_and_dispersed_collections",
       claim="Haskell says Celotti constantly built up collections and then dispersed them.",
       qualification="The passage does not identify individual collections or a particular sale.",mentioned=["cand-0622"],relation=False)
for city, cid, quote in [
    ("london","cand-1422","turns up again and again in London"),
    ("paris","cand-4653","turns up again and again in London,\nParis"),
    ("venice","cand-2719","turns up again and again in London,\nParis and his native Venice"),
]:
    add_statement(f"st-chp16-p377-celotti-repeatedly-appeared-{city}",BODY,52,53,
                  "cand-0622",f"repeatedly_appeared_in_{city}_in_haskells_account",cid,quote,
                  f"Haskell says Celotti appeared repeatedly in {city.title()} in his account of the dealer's activity.",
                  "Repeated appearances do not establish residence, an office, or a travel itinerary.",
                  ["cand-0622",cid],relation=True)
revise("st-chp16-p377-celotti-miniatures-from-papal-choral-books",
       "These were of all kinds and included ‘illumined miniature paintings taken from the\nChoral Books of the Papal Chapel in the Vatican during the French Revolution’.3",54,55,
       claim="Haskell says Celotti's advertised works included illuminated miniatures taken from the Papal Chapel's Choral Books during the French Revolution.",
       qualification="The passage identifies a group of miniatures but no individual image or present location.",
       mentioned=["cand-0622","cand-10651","cand-10650","cand-10649","cand-3399","cand-9828"])
revise("st-chp16-p377-celotti-owned-and-sold-old-masters",
       "he owned—and, of course, sold—old masters of all sorts",55,55,
       predicate="owned_unidentified_old_masters",claim="Haskell says Celotti owned old masters of all sorts.",
       qualification="The paintings are unidentified; the sale activity is recorded separately.",
       mentioned=["cand-0622","cand-10652","cand-4288"],relation=True)
add_statement("st-chp16-p377-celotti-sold-old-masters",BODY,55,55,"cand-0622",
              "sold_unidentified_old_masters","cand-10652",
              "he owned—and, of course, sold—old masters of all sorts",
              "Haskell says Celotti sold old masters of all sorts.",
              "No individual painting, sale date, or buyer is identified.",
              ["cand-0622","cand-10652","cand-4288"],relation=True)
revise("st-chp16-p377-celotti-owned-eighteenth-century-venetian-paintings",
       "many eighteenth-century Venetian paintings",55,55,
       claim="Haskell says Celotti owned many eighteenth-century Venetian paintings.",
       qualification="No number, title, or location is supplied; the sentence also says these works were sold.",
       mentioned=["cand-0622","cand-10653"])
add_statement("st-chp16-p377-celotti-sold-eighteenth-century-venetian-paintings",BODY,55,55,
              "cand-0622","sold_many_eighteenth_century_venetian_paintings","cand-10653",
              "he owned—and, of course, sold—old masters of all sorts and many eighteenth-century Venetian paintings",
              "Haskell's sentence says Celotti also sold many eighteenth-century Venetian paintings.",
              "The sentence does not identify individual works, a date, or a buyer.",
              ["cand-0622","cand-10653"],relation=True)
C["cand-10653"]["canonical_name"]="Unidentified eighteenth-century Venetian paintings owned and sold by Luigi Celotti"
C["cand-10653"]["detail"]="Haskell says Celotti owned and sold many eighteenth-century Venetian paintings; individual titles, number, and locations are not supplied."
revise("st-chp16-p377-haskell-infers-celotti-salesmanship-and-taste",
       "It is legitimate to infer from his rhapsodic accounts of these not only a considerable gift for salesmanship but also a genuine and individual taste which is similar to that of some of the humbler dealers so far recorded.4",56,56,
       claim="Haskell infers from Celotti's rhapsodic accounts both salesmanship and individual taste similar to that of some humbler dealers.",
       qualification="The sentence explicitly frames both conclusions as Haskell's inference.",mentioned=["cand-0622","cand-0126"])
revise("st-chp16-p377-celotti-eight-canaletto-paintings","Of his eight Canalettos,",56,56,
       predicate="owned_eight_canaletto_paintings",claim="Haskell says Celotti had eight Canalettos in his collection.",
       qualification="The eight works are unnamed; the four paintings with Tiepolo figures are treated separately.",
       mentioned=["cand-0622","cand-10654","cand-0498"])
revise("st-chp16-p377-celotti-four-canalettos-with-tiepolo-figures",
       "four ‘joignent à la richesse de leur composition, à l’imitation exacte et spirituelle dans tous leurs détails, et à la manière vague et légère que l’on admire ordinairement dans les Productions de cet habile Peintre, le précieux avantage d’etre enrichis de Figures de la main du célèbre\nTiepolo",56,57,
       claim="The quoted catalogue says four of Celotti's Canalettos were enriched with figures by Tiepolo and praises their composition and execution.",
       qualification="The paintings and figures are not individually identified; this is catalogue wording quoted by Haskell.",
       mentioned=["cand-10655","cand-0498","cand-2569"])
revise("st-chp16-p377-celotti-tiepolo-friendship-as-catalogue-wording",
       "Tiepolo, son ami’",57,57,
       claim="The quoted 1807 catalogue calls Tiepolo 'son ami' in its recommendation of the Canaletto paintings.",
       qualification="This records the catalogue's wording, not independent proof of a personal friendship.",mentioned=["cand-0622","cand-2569"])
revise("st-chp16-p377-celotti-sebastiano-ricci-pastoral","His Sebastiano Ricci pastoral scene",57,57,
       predicate="owned_sebastiano_ricci_pastoral_scene",
       claim="Haskell identifies a Sebastiano Ricci pastoral scene as belonging to Celotti.",
       qualification="The work is unidentified; its quoted appraisal is recorded separately.",
       mentioned=["cand-0622","cand-10656","cand-2154"])
add_statement("st-chp16-p377-celotti-ricci-pastoral-appraisal",BODY,57,57,
              "cand-10656","described_as_fresh_in_colour_and_light_in_brushwork",None,
              "‘d’un coloris frais et d’un pinceau léger’",
              "Haskell quotes a description of the Ricci pastoral scene as fresh in colour and light in brushwork.",
              "This is the cited appraisal, not an independent visual examination of the work.",
              ["cand-10656","cand-2154"],speaker="Haskell quoting a sale description",
              text_layer="bibliographic quotation")
revise("st-chp16-p377-celotti-tiepolo-rape-of-ganymede-sketch",
       "His Tiepolo sketches—of the Rape of\nGanymede",57,58,
       claim="Haskell says the Tiepolo sketches in Celotti's collection included one depicting the Rape of Ganymede.",
       qualification="The individual sketch is not identified; the index has a matching Tiepolo subentry for S3 to assess.",
       mentioned=["cand-0622","cand-10657","cand-2569","cand-3436","cand-2608"])
revise("st-chp16-p377-celotti-tiepolo-allegorical-sketch","and an allegorical subject",58,58,
       claim="Haskell says the Tiepolo sketches in Celotti's collection also included one with an allegorical subject.",
       qualification="The allegorical subject and sketch are unidentified.",mentioned=["cand-0622","cand-10658","cand-2569"])

# Make the two-sketch group explicit and keep the mismatched printed marker 6 visible.
new_candidates=[
    {"candidate_id":"cand-11550","index_entry_id":"","canonical_name":"Unidentified Tiepolo paintings in Luigi Celotti's 1814 sale","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell reports that Celotti sold 'some more Tiepolos' in 1814; individual paintings and lots are unidentified. The source does not identify these works with the two sketches discussed on p.377.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{NOTES}#L89"},
    {"candidate_id":"cand-11551","index_entry_id":"","canonical_name":"Unidentified Piazzetta paintings in Luigi Celotti's 1814 sale","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell reports that Celotti sold Piazzetta works in 1814; individual paintings and lots are unidentified.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{NOTES}#L89"},
    {"candidate_id":"cand-11552","index_entry_id":"","canonical_name":"Two Tiepolo sketches in Luigi Celotti's collection (Rape of Ganymede and an allegorical subject)","index_page_range":"","suggested_type":"work","status":"open","index_source_file":"","sub_entry":"","detail":"Haskell groups two Tiepolo sketches in Celotti's collection and appraises them together; one subject is the Rape of Ganymede and the other is described only as allegorical. Neither sketch is individually identified.","exclude_reason":"","candidate_origin":"body-mention","candidate_source_ref":f"{BODY}#L57"},
]
for c in new_candidates:
    if c["candidate_id"] in C: raise SystemExit(f"candidate exists: {c['candidate_id']}")
    candidates.append(c); C[c["candidate_id"]]=c
new_group_id="st-chp16-p377-celotti-tiepolo-sketches-collective-appraisal"
MISMATCH="The body prints marker 6 after the p.377 sketch appraisal, while the footer prints note 5 for an 1814 sale; the page image shows no matching note 6, so they are not linked."
add_statement(new_group_id,BODY,57,58,"cand-11552",
              "described_as_easy_in_touch_and_impetuous_in_composition",None,
              "are ‘d’une grande facilité de touche, et d’une composition fougueuse . . ..6",
              "The quoted catalogue appraises the two Tiepolo sketches as having great ease of touch and an impetuous composition.",
              "The appraisal applies to the pair as Haskell presents it; the printed body marker 6 has no matching note 6 on this page.",
              ["cand-11552","cand-2569"],speaker="1807 catalogue as quoted by Haskell",
              text_layer="bibliographic quotation",extra={
                  "footnote_marker":"6","footnote_segment":NOTES,"footnote_line_range":None,
                  "footnote_text_pending":False,"footnote_body_link_status":"mismatched",
                  "footnote_body_line_range":"L58","footnote_note_statement_ids":[],"footnote_link_note":MISMATCH})

# Split Haskell's social synthesis while preserving its existing ID for collection/patronage.
group_ids=["st-chp16-p377-haskell-groups-dealers-by-status-and-social-place",
           "st-chp16-p377-haskell-generalizes-dealers-collections-and-patronage",
           "st-chp16-p377-haskell-dealers-outside-venetian-intellectual-currents"]
p378_ids=["st-chp16-p378-group-livelihood-and-old-masters-demand",
          "st-chp16-p378-group-collected-artists-affected-by-taste-change",
          "st-chp16-p378-group-retrospective-venetian-tradition"]
cross={"cross_reference_segments":[P378],"cross_reference_statement_ids":p378_ids,
       "cross_reference_text":"P.378 L67 continues Haskell's group-level synthesis about the same men, their collections and trade, and his retrospective assessment.",
       "cross_reference_text_pending":False}
revise("st-chp16-p377-haskell-generalizes-dealers-collections-and-patronage",
       "we can see a strikingly similar type of collection and patronage.",59,59,
       predicate="haskell_generalizes_similar_collection_and_patronage_across_the_dealers",
       claim="Haskell identifies a strikingly similar type of collection and patronage among the men discussed.",
       qualification="This is a group-level authorial synthesis, not an individual fact about Celotti alone.",
       mentioned=["cand-2534","cand-0622","cand-0126"],relation=False,qset=cross)
add_statement(group_ids[0],BODY,59,59,None,"haskell_groups_dealers_as_similar_in_status_and_social_place",None,
              "In all these men, so similar in their status and their place in society,",
              "Haskell says the men discussed shared similar social status and place in society.",
              "This is a group-level comparison; no precise rank is assigned to each person.",
              ["cand-2534","cand-0622","cand-0126"],relation=False,extra=cross)
add_statement(group_ids[2],BODY,59,59,None,"group_stood_outside_main_venetian_intellectual_currents",None,
              "They were outside the main currents of the intellectual life of Venice which have been examined in the last few chapters.",
              "Haskell says the men discussed stood outside the main currents of Venice's intellectual life examined in earlier chapters.",
              "This is Haskell's group-level interpretation and does not imply that each person lacked intellectual contacts.",
              ["cand-2534","cand-0622","cand-0126","cand-2719"],relation=False,extra=cross)

# Refine p.376's cross-page completion and p.378's reciprocal group references.
p376=S["st-chp16-p376-swajer-secret-manuscripts-partial"]["qualifiers"]
targets=p376.setdefault("cross_reference_statement_ids",[])
if acquired_id not in targets: targets.append(acquired_id)
for sid in p378_ids:
    S[sid]["qualifiers"]["referent_statement_ids"]=group_ids

# Narrow the continued note-3 archive locator and record the page-image OCR correction.
revise("st-chp16-p377-note3-state-archive-locator",
       "His papers and manuscripts are mentioned in the Archivio di Stato, Venice—Inquisitori, 540, p. 164—30 Maggio 1792. ‘",64,64,
       claim="Haskell's note locates a mention of Swajer's papers and manuscripts in Archivio di Stato, Venice, Inquisitori 540, page 164, dated 30 May 1792.",
       qualification="The archival record was not consulted; this locator is recorded as cited by Haskell.",
       mentioned=["cand-2534","cand-10172","cand-10462"])
correction("st-chp16-p377-note3-state-archive-locator",64,"1792. ‘","1792.")

# Split the Christie's locator from the reported description by William Young Ottley.
revise("st-chp16-p377-note3-christies-miniatures","Christies’, 26 May 1825.",87,87,
       predicate="note_cites_christies_sale_on_26_may_1825",
       claim="Haskell's note cites Christie's, 26 May 1825, as a sale locator.",
       qualification="No lot number or catalogue title is supplied; the sale record was not independently consulted.",
       mentioned=["cand-10661","cand-9400"])
ottley_id="st-chp16-p377-note3-miniatures-described-by-ottley"
add_statement(ottley_id,NOTES,87,87,"cand-10651","described_by_william_young_ottley","cand-1793",
              "The miniatures are described by William Young Ottley.",
              "Haskell's note identifies William Young Ottley as the person who described the miniatures.",
              "The cited description was not independently consulted.",["cand-10651","cand-1793"],
              speaker="Haskell's note",text_layer="attributed description",relation=True,
              extra={"cited_source_independently_consulted":False,"footnote_marker":"3",
                     "footnote_segment":NOTES,"footnote_line_range":"L87-L87","footnote_text_pending":False,
                     "footnote_body_link_status":"linked","footnote_body_line_range":"L54-L55",
                     "footnote_note_statement_ids":["st-chp16-p377-note3-christies-miniatures",ottley_id],
                     "footnote_link_note":"P.377 note 3 gives the sale locator and attributes the miniatures' description to William Young Ottley."})
S["st-chp16-p377-celotti-miniatures-from-papal-choral-books"]["qualifiers"]["footnote_note_statement_ids"]=["st-chp16-p377-note3-christies-miniatures",ottley_id]

# The printed title preserves historic spelling "maistres"; do not modernize it to "maîtres".
note4=S["st-chp16-p377-note4-celotti-1807-catalogue"]
for c in note4["qualifiers"].get("ocr_corrections",[]):
    if c.get("source_line")==88 and c.get("ocr")=="maitres":
        c["print"]="maistres"
        c["basis"]="CHP-16.pdf physical page 5; the printed title retains the historical spelling."
C["cand-10662"]["canonical_name"]="Notice de Tableaux, par les plus grands maistres d’Italie, composant le cabinet de M. Celotti de Venise, Paris 1807"

# Notes 5 and the body marker 6 visibly disagree on the page; do not force a link.
note5_id="st-chp16-p377-note5-celotti-1814-sale"
revise(note5_id,
       "Notice d’une collection de tableaux [appartenant à M.r Celotti] doni la vente aura lieu le luridi 14 Novembre 1814.",89,89,
       predicate="note_cites_celotti_sale_catalogue_for_14_november_1814",
       claim="Haskell's note cites the Notice d'une collection de tableaux for a sale dated 14 November 1814.",
       qualification="The catalogue and annotated copy were not consulted; works sold and Haskell's copy-specific observation are recorded separately.",
       mentioned=["cand-10663","cand-0622"],relation=True,
       qset={"footnote_body_link_status":"mismatched","footnote_body_line_range":None,
             "footnote_link_note":MISMATCH})
S[note5_id]["qualifiers"]["footnote_note_statement_ids"]=[note5_id]

def note5_extra(sid):
    return {"cited_source_independently_consulted":False,"footnote_marker":"5",
            "footnote_segment":NOTES,"footnote_line_range":"L89-L89","footnote_text_pending":False,
            "footnote_body_link_status":"mismatched","footnote_body_line_range":None,
            "footnote_note_statement_ids":[sid],"footnote_link_note":MISMATCH}

for sid, obj, pred, quote, claim, mentioned in [
    ("st-chp16-p377-note5-celotti-sold-tiepolo-works-1814","cand-11550","sold_unidentified_tiepolo_paintings_in_1814",
     "In 1814 he sold some more Tiepolos","Haskell's note reports that Celotti sold further Tiepolo paintings in 1814.",["cand-0622","cand-11550","cand-2569"]),
    ("st-chp16-p377-note5-celotti-sold-piazzetta-works-1814","cand-11551","sold_unidentified_piazzetta_paintings_in_1814",
     "and also Piazzettas","Haskell's note reports that Celotti also sold Piazzetta paintings in 1814.",["cand-0622","cand-11551","cand-1901"]),
]:
    add_statement(sid,NOTES,89,89,"cand-0622",pred,obj,quote,claim,
                  "The note names artist groups but no individual works, lots, or buyers; the sale catalogue was not consulted.",
                  mentioned,speaker="Haskell's note",text_layer="secondary sale report",relation=True,
                  extra=note5_extra(sid))
ink_id="st-chp16-p377-note5-bracketed-celotti-wording-added-in-ink"
add_statement(ink_id,NOTES,89,89,"cand-10663","bracketed_celotti_wording_reported_as_added_in_ink",None,
              "The words in brackets are added in ink to the printed catalogue in the copy which I have seen.",
              "Haskell says the bracketed Celotti wording was handwritten in ink in the catalogue copy he saw.",
              "This is Haskell's copy-specific observation; neither that copy nor the catalogue was examined here.",
              ["cand-10663","cand-0622"],speaker="Haskell's note",text_layer="copy-specific observation",
              extra=note5_extra(ink_id))

# All p.377 note-5 rows are mismatched with the body; the unmatched marker is 6 at L58.
for row in statements:
    q=row.get("qualifiers") or {}
    if row.get("segment_id")==NOTES and q.get("printed_page")==377 and q.get("footnote_marker")=="5":
        q.update({"footnote_body_link_status":"mismatched","footnote_body_line_range":None,
                  "footnote_text_pending":False,"footnote_link_note":MISMATCH})
        if row["statement_id"]!=note5_id and row["statement_id"] not in [
            "st-chp16-p377-note5-celotti-sold-tiepolo-works-1814",
            "st-chp16-p377-note5-celotti-sold-piazzetta-works-1814",ink_id]:
            q["footnote_note_statement_ids"]=[row["statement_id"]]

# Add explicit group mentions while retaining the existing artist mentions.
def add_mention(mid, seg, cid, surface):
    if any(m["mention_id"]==mid for m in mentions): raise SystemExit(f"mention exists: {mid}")
    text=body_text if seg==BODY else note_text
    starts=[i for i in range(len(text)) if text.startswith(surface,i)]
    if len(starts)!=1: raise SystemExit(f"expected one {surface!r} in {seg}; found {len(starts)}")
    start=starts[0]
    mentions.append({"mention_id":mid,"segment_id":seg,"candidate_id":cid,"surface_form":surface,
                     "start_char":str(start),"end_char":str(start+len(surface)),
                     "note":"S2 semantic refinement: explicit group-level work reference."})
add_mention("m-chp16-p377-celotti-0066",BODY,"cand-11552","Tiepolo sketches")
add_mention("m-chp16-p377-celotti-0067",NOTES,"cand-11550","some more Tiepolos")
add_mention("m-chp16-p377-celotti-0068",NOTES,"cand-11551","also Piazzettas")

# Synchronize the completed p.376 sentence and group synthesis across the page break.
p376q=S["st-chp16-p376-swajer-secret-manuscripts-partial"]["qualifiers"]
refs=p376q.setdefault("cross_reference_statement_ids",[])
if acquired_id not in refs: refs.append(acquired_id)
for sid in p378_ids:
    S[sid]["qualifiers"]["referent_statement_ids"]=group_ids

# Preserve source OCR but record that the page image has no apostrophe after the archive date.
locator="st-chp16-p377-note3-state-archive-locator"
correction(locator,64,"1792. ‘","1792.")

# Validate every p.377 statement quote and every existing/new mention span before any write.
for row in statements:
    if row.get("segment_id") in (BODY,NOTES): check_quote(row["segment_id"],row["original_quote"])
for m in mentions:
    if m.get("segment_id") not in (BODY,NOTES): continue
    text=body_text if m["segment_id"]==BODY else note_text
    a,b=int(m["start_char"]),int(m["end_char"])
    if text[a:b]!=m["surface_form"]: raise SystemExit(f"mention span mismatch: {m['mention_id']}")
if any(cid not in C for row in statements for cid in ([row.get("subject_candidate_id"),row.get("object_candidate_id")]+(row.get("qualifiers",{}).get("mentioned_candidate_ids") or [])) if cid):
    raise SystemExit("candidate reference missing after refinement")
for sid in [note5_id,"st-chp16-p377-note5-celotti-sold-tiepolo-works-1814",
            "st-chp16-p377-note5-celotti-sold-piazzetta-works-1814",ink_id]:
    if S[sid]["qualifiers"].get("footnote_body_link_status")!="mismatched":
        raise SystemExit(f"note 5 mismatch not recorded: {sid}")
if S[new_group_id]["qualifiers"].get("footnote_body_link_status")!="mismatched":
    raise SystemExit("printed marker 6 mismatch not recorded")

print("plan: +15 statements, +3 candidates, +3 mentions; existing statements/links refined")
print("validation: source/PDF/table SHA guards, quote anchors, mention spans, candidate references passed")
print("footnote: bottom note 5 and body marker 6 remain explicitly mismatched; no inferred link")
if args.apply:
    backups=[]
    for path in (STATEMENTS,CANDIDATES,MENTIONS):
        backup=path.with_name(path.name+BACKUP_SUFFIX)
        if backup.exists(): raise SystemExit(f"refusing to overwrite backup {backup}")
        shutil.copy2(path,backup); backups.append(backup)
    write_jsonl(STATEMENTS,statements)
    write_csv(CANDIDATES,cand_fields,candidates)
    write_csv(MENTIONS,mention_fields,mentions)
    print("applied; backups:")
    for backup in backups: print(backup.relative_to(ROOT))
else:
    print("dry-run only; pass --apply to write")
