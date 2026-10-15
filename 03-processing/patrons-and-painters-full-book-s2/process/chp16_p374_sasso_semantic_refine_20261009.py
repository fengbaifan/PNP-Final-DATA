"""Hash-guarded S2 semantic refinement for chapter 16, printed p.374."""
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
BODY = "chp-16:16_CHP-16_intro:l16-22"
NOTES = "chp-16:16_CHP-16_intro:l69-89"
EXPECTED = {
    "book-statements.jsonl": "e70539f92d53062744bb6f914eca3bda2807479e9958cd8aff0c5dc2c034b8a9",
    "mentions.csv": "cb9210f54e6e011e2d3410d712297ba83ed93ff8fc0054acb26251355ca0e417",
    "entity-candidates.csv": "cf7e8c2890898302d5a062ee20f772431acb847c254a2cd6d81b34a45efb8ef3",
}
SOURCE_SHA = "ee8516e7868b0036a753da731e10a7e201faafa45314615b45ae024c6c7507ff"
PDF_SHA = "6bfb3e331f0ac2421d31279f97b08b17486f0e2c32451a10a6798cf31424af5f"
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply after reviewing the dry-run")
args = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(f.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(f.name)
    temp.replace(path)


def frag(line_no, start, end):
    line = lines[line_no - 1]
    i = line.find(start)
    if i < 0 or line.find(start, i + 1) >= 0:
        raise SystemExit(f"source start is missing or ambiguous at L{line_no}: {start}")
    j = line.find(end, i)
    if j < 0:
        raise SystemExit(f"source end is missing at L{line_no}: {end}")
    return line[i:j + len(end)]


def make(statement_id, segment, line_no, subject, obj, predicate, claim, speaker, layer,
         qualification, mentioned, quote, relation=False, **extra):
    q = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 374, "pdf_physical_page": 2, "claim": claim,
        "speaker": speaker, "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
    }
    if relation:
        q["relation_candidate"] = True
    q.update(extra)
    return {
        "statement_id": statement_id, "segment_id": segment,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": q, "original_quote": quote,
        "origin": "book", "source_file": "02-sources/02-Markdown/16_CHP-16_intro.md",
    }


for path in (SOURCE, PDF):
    expected = SOURCE_SHA if path == SOURCE else PDF_SHA
    if sha(path) != expected:
        raise SystemExit(f"source asset hash changed: {path.name}")
for name, expected in EXPECTED.items():
    if sha(TABLES / name) != expected:
        raise SystemExit(f"table baseline hash changed: {name}")

lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
checks = {17: "—less frequently—the moderns", 18: "citta di Venezia", 19: "truth",
          20: "hot just clear", 21: "G. A. Armanni", 22: "eighteenthcentury",
          72: "i960", 73: "1784,", 74: "G. M Sasso", 75: "i960"}
for no, text in checks.items():
    if text not in lines[no - 1]:
        raise SystemExit(f"required source text changed at L{no}: {text}")

statement_path = TABLES / "book-statements.jsonl"
mention_path = TABLES / "mentions.csv"
candidate_path = TABLES / "entity-candidates.csv"
statements = [json.loads(x) for x in statement_path.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
mention_fields, mentions = read_csv(mention_path)
candidate_fields, candidates = read_csv(candidate_path)
by_sid = {s["statement_id"]: s for s in statements}
by_cid = {c["candidate_id"]: c for c in candidates}
if len(by_sid) != len(statements):
    raise SystemExit("statement IDs are not unique")
if not all(x in by_sid for x in ("st-chp16-p373-strange-employed-sasso-to-buy-pictures",
                                  "st-chp16-p374-sasso-posthumous-collection-partial",
                                  "st-chp16-p375-sasso-collection-list-completion")):
    raise SystemExit("p.373/p.374 cross-page anchors changed")
if any(s["segment_id"] == BODY and s["statement_id"].startswith("st-chp16-p374-refine-") for s in statements):
    raise SystemExit("refinement statements already exist")

# These candidates keep generic residences, an unidentified group of Guardi works,
# and the 1803 auction distinct from named places and Sasso's collection.
new_candidates = [
    ("cand-11546", "John Strange’s unidentified country house near Treviso", "place",
     "Haskell says pictures stayed temporarily in Strange's country house near Treviso; identity with the villa at Paese (cand-11524) is not established.", BODY, 17),
    ("cand-11547", "John Strange’s unidentified London apartments", "place",
     "Haskell mentions Strange's apartments in London without an address or building name; keep distinct from London as a city.", BODY, 17),
    ("cand-11548", "Unidentified group of Guardi works owned by John Strange", "work",
     "Haskell reports that Strange owned a large number of Guardi's works but supplies no titles, count, or individual identities.", BODY, 20),
    ("cand-11549", "Auction of Sasso’s collection after his death in 1803", "event",
     "Haskell says the collection Sasso made for himself was auctioned after his death in 1803; the sale catalogue was not independently consulted.", BODY, 22),
]
for cid, name, kind, detail, segment, source_line in new_candidates:
    if cid in by_cid:
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
           "index_page_range": "", "suggested_type": kind, "status": "open",
           "index_source_file": "", "sub_entry": "", "detail": detail,
           "exclude_reason": "", "candidate_origin": "body-mention",
           "candidate_source_ref": f"{segment}#L{source_line}"}
    candidates.append(row)
    by_cid[cid] = row

body17 = lines[16]
body18 = lines[17]
body19 = lines[18]
body20 = lines[19]
body21 = lines[20]
body22 = lines[21]
note72, note73, note74, note75 = lines[71:75]
note1 = "st-chp16-p374-note1-guardi-patronage-reference"
note2 = "st-chp16-p374-note2-strange-sasso-letter8"
note3_repo = "st-chp16-p374-note3-armanni-sasso-letters-and-poore"
note3_letter = "st-chp16-p374-note3-poore-letter-locator"
note3_auction = "st-chp16-p374-note3-poore-auction-sales"
note4 = "st-chp16-p374-note4-haskell-journal-276"
note3_ids = [note3_repo, note3_letter, note3_auction]

foot1 = {"footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L72-L72",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_body_line_range": "L19", "footnote_note_statement_ids": [note1],
         "footnote_link_note": "Footnote 1 directs readers to Haskell's fuller references on Guardi patronage."}
foot2 = {"footnote_marker": "2", "footnote_segment": NOTES, "footnote_line_range": "L73-L73",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_body_line_range": "L20", "footnote_note_statement_ids": [note2],
         "footnote_link_note": "Footnote 2 gives a dated letter locator for the Strange-Sasso correspondence."}
foot3 = {"footnote_marker": "3", "footnote_segment": NOTES, "footnote_line_range": "L74-L74",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_body_line_range": "L21-L22", "footnote_note_statement_ids": note3_ids,
         "footnote_link_note": "Footnote 3 gives Armanni-Sasso archival and Poore-sale source locators."}
foot4 = {"footnote_marker": "4", "footnote_segment": NOTES, "footnote_line_range": "L75-L75",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_body_line_range": "L22", "footnote_note_statement_ids": [note4],
         "footnote_link_note": "Footnote 4 supplies the Haskell journal citation locator."}

fix_l18 = [{"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 18,
            "ocr": "citta", "print": "città", "basis": "CHP-16.pdf physical page 2."}]
fix_l20 = [{"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 20,
            "ocr": "hot just clear", "print": "not just clear", "basis": "CHP-16.pdf physical page 2."}]
fix_l22 = [
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 22,
     "ocr": "with'whom", "print": "with whom", "basis": "CHP-16.pdf physical page 2."},
    {"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 22,
     "ocr": "eighteenthcentury", "print": "eighteenth-century", "basis": "CHP-16.pdf physical page 2."},
]
fix_l72 = [{"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 72,
            "ocr": "i960", "print": "1960", "basis": "CHP-16.pdf physical page 2."}]
fix_l73 = [{"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 73,
            "ocr": "1784,", "print": "1784.", "basis": "CHP-16.pdf physical page 2."}]
fix_l74 = [{"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 74,
            "ocr": "G. M Sasso", "print": "G. M. Sasso", "basis": "CHP-16.pdf physical page 2."}]
fix_l75 = [{"source_file": "02-sources/02-Markdown/16_CHP-16_intro.md", "source_line": 75,
            "ocr": "i960", "print": "1960", "basis": "CHP-16.pdf physical page 2."}]

new = []
def add(*args, **kwargs):
    row = make(*args, **kwargs)
    if row["statement_id"] in by_sid or any(x["statement_id"] == row["statement_id"] for x in new):
        raise SystemExit(f"duplicate statement ID: {row['statement_id']}")
    new.append(row)
    return row

# p.374 continuation of the p.373 purchase list; keep this ID as the stable link.
s = by_sid["st-chp16-p374-strange-pictures-list-and-custody"]
s["predicate"] = "purchased_picture_list_continues_with_less_frequent_modern_painters"
s["qualifiers"].update({"claim": "Haskell continues the p.373 account of pictures Sasso bought for Strange, naming Rosalba, Canaletto, and Tiepolo as less-frequent moderns.",
                        "qualification": "This row records the painter list only; temporary storage and possible later sales are separate claims.",
                        "mentioned_candidate_ids": ["cand-2517", "cand-2367", "cand-0581", "cand-0498", "cand-10608"],
                        "relation_candidate": True})
s["original_quote"] = frag(17, "—less frequently—the moderns", "especially.")
add("st-chp16-p374-refine-picture-storage", BODY, 17, None, None, "pictures_temporarily_stored_at_strange_residences",
    "Haskell says the pictures found temporary resting places in Strange's country house near Treviso or his London apartments.",
    "Haskell", "authorial report", "The two residences are not individually identified; the country house is not equated here with the villa named in the Plate 64 caption.",
    ["cand-2517", "cand-11546", "cand-11547", "cand-9209", "cand-1422"],
    frag(17, "These pictures found a temporary resting-place", "his apartments in London,"))
add("st-chp16-p374-refine-picture-sale-qualification", BODY, 17, None, None, "pictures_sold_or_would_have_been_sold_to_rich_amateurs",
    "Haskell says the pictures were then sold to rich amateurs, or would have been sold had buyers not preferred modern pictures.",
    "Haskell", "authorial report with counterfactual qualification", "The counterfactual leaves actual completion uncertain and does not identify who completed any sale.",
    ["cand-2367"], frag(17, "and were then sold", "modern trash’.") )

# Split the general trade conditions into independently attributable clauses.
trade = by_sid["st-chp16-p374-dealer-trade-secrecy-transport-customs"]
trade.update(make(trade["statement_id"], BODY, 18, None, None, "prospective_collections_examined_in_secrecy",
    "Haskell says collections likely to be dispersed had to be examined in absolute secrecy.", "Haskell",
    "authorial report", "A general account of the trade process, not a claim about a named shipment.", [],
    frag(18, "Collections likely to be dispersed", "absolute secrecy;")))
add("st-chp16-p374-refine-transport-cost", BODY, 18, None, None, "transport_was_enormously_expensive",
    "Haskell says transport was enormously expensive.", "Haskell", "authorial report",
    "A general account of the trade process.", [], frag(18, "transport was enormously expensive", "expensive;"))
add("st-chp16-p374-refine-customs-evasion", BODY, 18, None, None, "customs_troublesome_and_evasion_conditional",
    "Haskell says customs were troublesome and had to be evaded if possible.", "Haskell", "authorial report",
    "The source says evasion was conditional ('if possible').", [],
    frag(18, "the customs were troublesome", "if possible."))

for sid, pred, start, end, claim, subject, obj, cited, relation, extra in [
    ("st-chp16-p374-strange-modern-art-commissions", "occasionally_commissioned_modern_works_for_himself_or_client",
     "Strange occasionally commissioned", "for a client.", "Haskell says Strange occasionally commissioned a modern work for himself or a client; the work and client are unnamed.",
     "cand-2517", None, ["cand-2517"], False, {}),
    ("st-chp16-p374-strange-zompini-publication-plan", "planned_to_publish_an_edition_of_zompini_le_arti",
     "He planned to bring out", "Venezia;", "Haskell says Strange planned to bring out an edition of Zompini's Le Arti che vanno per le vie nella citta di Venezia.",
     "cand-2517", "cand-2876", ["cand-2517", "cand-2874", "cand-2876"], True, {"ocr_corrections": fix_l18}),
    ("st-chp16-p374-strange-employs-guardi", "employed_the_little_known_francesco_guardi",
     "he employed the little-known Francesco Guardi", "(Plate 64).", "Haskell says Strange employed the then little-known Francesco Guardi.",
     "cand-2517", "cand-1239", ["cand-2517", "cand-1239"], True, {}),
]:
    old = by_sid[sid]
    old.update(make(sid, BODY, 18, subject, obj, pred, claim, "Haskell", "authorial report",
                    "The claim is limited to the plan or action stated; it does not establish an outcome.",
                    cited, frag(18, start, end), relation, **extra))

# The pronoun is kept qualified; the aesthetic judgement belongs to Haskell's narration.
old = by_sid["st-chp16-p374-strange-view-of-guardi-truth"]
old.update(make(old["statement_id"], BODY, 19, "cand-2517", None, "was_somewhat_diffident_about_unspecified_context",
    "Haskell says he was somewhat diffident about 'this'; the sentence does not specify the exact referent of 'this'.",
    "Haskell", "authorial interpretation", "The pronoun 'he' follows the discussion of Strange; do not convert the next clause into Strange's direct judgement.",
    ["cand-2517"], frag(19, "He was somewhat diffident", "about this,"), False))
add("st-chp16-p374-refine-haskell-guardi-truth-judgement", BODY, 19, None, "cand-1239",
    "haskell_describes_guardi_as_apt_to_miss_truth_in_painted_views",
    "Haskell describes the artist as spirited but apt to miss the truth of the views he painted.",
    "Haskell", "authorial aesthetic judgement", "This is Haskell's characterization, not an explicit opinion attributed to Strange.",
    ["cand-1239"], frag(19, "for the artist", "that he painted."), **foot1)

# Split the letter request, collecting, residence, taste, and Tiepolo detail.
draw = by_sid["st-chp16-p374-strange-drawing-instructions-via-sasso"]
draw.update(make(draw["statement_id"], BODY, 20, "cand-2517", "cand-2364", "asked_sasso_to_convey_guardi_drawing_specifications",
    "Haskell says Strange asked Sasso to tell Guardi that his drawings should be not just clear, well finished, paired, and accurately coloured.",
    "Haskell reporting Strange", "authorial report with quoted specifications",
    "The request identifies no particular drawings and does not confirm completion.",
    ["cand-2517", "cand-2364", "cand-1239", "cand-10611"],
    frag(20, "Sasso to tell Guardi", "coloured exactly’"), True, ocr_corrections=fix_l20))

add("st-chp16-p374-refine-strange-admires-guardi", BODY, 20, "cand-2517", "cand-1239",
    "strange_admired_guardi", "Haskell says Strange admired Guardi.", "Haskell", "authorial report",
    "The statement records admiration only.", ["cand-2517", "cand-1239"], frag(20, "Yet Strange admired Guardi", "Guardi,"), False)
add("st-chp16-p374-refine-strange-owns-guardi-works", BODY, 20, "cand-2517", "cand-11548",
    "strange_owned_many_works_by_guardi", "Haskell says Strange owned a large number of Guardi's works.",
    "Haskell", "authorial report", "The source gives no titles, exact count, or individual work identities.",
    ["cand-2517", "cand-1239", "cand-11548"], frag(20, "at one time or another he owned", "his works;"), True)
add("st-chp16-p374-refine-strange-venice-residence", BODY, 20, "cand-2517", "cand-2719",
    "strange_was_settled_in_venice", "Haskell places Strange among people settled in Venice, away from the newer currents of London, Paris, and Rome.",
    "Haskell", "authorial interpretation", "The comparison is Haskell's framing; it does not specify an exact address or duration.",
    ["cand-2517", "cand-2719", "cand-1422", "cand-4653", "cand-4490"],
    frag(20, "for like many others who were settled in Venice", "London, Paris or Rome,"), True)
add("st-chp16-p374-refine-strange-venetian-colour-preference", BODY, 20, "cand-2517", "cand-11543",
    "strange_loved_brio_and_rich_colour_of_venetian_painting", "Haskell says Strange loved the brio and rich colour of Venetian painting.",
    "Haskell", "authorial interpretation", "This is Haskell's account of Strange's taste.",
    ["cand-2517", "cand-11543"], frag(20, "he loved the brio", "Venetian painting,"))
add("st-chp16-p374-refine-strange-dislikes-neoclassical-works", BODY, 20, "cand-2517", "cand-8837",
    "strange_was_out_of_sympathy_with_new_dry_neoclassical_works",
    "Haskell says Strange was out of sympathy with the new, dry, neo-classical works then fashionable in London, Paris, and Rome.",
    "Haskell", "authorial interpretation", "The source presents this as Haskell's account of Strange's taste.",
    ["cand-2517", "cand-8837", "cand-1422", "cand-4653", "cand-4490"],
    frag(20, "and was out of sympathy", "in those towns."))

old = by_sid["st-chp16-p374-strange-tiepolo-pigeon-detail"]
old.update(make(old["statement_id"], BODY, 20, "cand-2517", "cand-10609", "wanted_tiepolo_picture_detail_cut_out_for_him",
    "Haskell says Strange spoke enthusiastically of Tiepolo and wanted a pigeon-on-a-twig detail from one of his pictures cut out for himself.",
    "Haskell", "authorial report", "The painting is unnamed and the request is not evidence that the detail was actually removed.",
    ["cand-2517", "cand-10608", "cand-10609"], frag(20, "And so we find him speaking enthusiastically", "for himself."),
    True, **foot2))

# Keep the clients' differing responses, Armanni's roles, travel, and remark distinct.
add("st-chp16-p374-refine-not-all-clients", BODY, 21, None, None, "not_all_sasso_clients_equally_keen",
    "Haskell says not all of Sasso's clients were as keen as Strange.", "Haskell", "authorial interpretation",
    "The sentence does not identify the other clients.", ["cand-2364"], frag(21, "Not all Sasso’s clients", "so keen."))
add("st-chp16-p374-refine-armanni-occupation", BODY, 21, "cand-0119", None, "armanni_was_painter_and_dealer",
    "Haskell identifies G. A. Armanni as a painter and dealer.", "Haskell", "authorial report",
    "No independent occupational source is cited here.", ["cand-0119"], frag(21, "The painter and dealer", "G. A. Armanni,"))
add("st-chp16-p374-refine-armanni-travel", BODY, 21, "cand-0119", None, "armanni_travelled_between_bologna_and_rome",
    "Haskell says Armanni travelled between Bologna and Rome.", "Haskell", "authorial report",
    "This identifies a travel pattern, not a permanent residence.", ["cand-0119", "cand-0381", "cand-4490"],
    frag(21, "travelling between Bologna", "Rome,"))
old = by_sid["st-chp16-p374-armanni-introduces-poore"]
old.update(make(old["statement_id"], BODY, 21, "cand-0119", "cand-1973", "armanni_wrote_derisively_of_english_visitor_mr_poore",
    "Haskell says Armanni wrote derisively of an English visitor, Mr Poore.", "Haskell", "authorial report",
    "The note later identifies him as Edward Poore; this identity is recorded as Haskell presents it, without external verification.",
    ["cand-0119", "cand-1973"], frag(21, "wrote derisively", "Mr Poore:"), True, **foot3))
old = by_sid["st-chp16-p374-armanni-quote-on-poore"]
old.update(make(old["statement_id"], BODY, 22, "cand-0119", "cand-1973", "armanni_quote_mocks_taste_for_tiepolo_celesti_and_lesser_painters",
    "Haskell quotes Armanni asking how someone who loves Greek subtlety could patiently look at Tiepolo's stranezze, Celesti's caricatures, and lesser painters' schiribizzi.",
    "Armanni, as quoted by Haskell", "embedded quotation",
    "Haskell links the remark to Mr Poore; the archival letter itself was not consulted.",
    ["cand-0119", "cand-1973", "cand-10608", "cand-0618"],
    frag(22, "‘How strange", "lesser painters!’3"), False, **foot3))

old = by_sid["st-chp16-p374-venetian-dealers-retain-painting-heritage"]
old.update(make(old["statement_id"], BODY, 22, None, "cand-11543", "venice_social_world_need_not_reject_recent_venetian_painting",
    "Haskell says that among Venice's agents, dealers, minor clerics, and doctors there was not yet a need to reject the heritage of recent Venetian painting.",
    "Haskell", "authorial interpretation", "This is Haskell's generalization about the city's art world, not a claim about every individual in it.",
    ["cand-2719", "cand-11543"], frag(22, "while in the enclosed world of Venice itself", "recent Venetian painting."),
    ocr_corrections=fix_l22))
add("st-chp16-p374-refine-armanni-new-fashions", BODY, 22, "cand-0119", None, "armanni_was_in_touch_with_new_fashions",
    "Haskell says Armanni was in touch with all the new fashions.", "Haskell", "authorial report",
    "The passage does not name specific fashions in this clause.", ["cand-0119"],
    frag(22, "But Armanni was in touch", "new fashions,"))
add("st-chp16-p374-refine-sasso-earlier-painter-virtuosity", BODY, 22, "cand-2364", "cand-11543",
    "sasso_seems_to_share_previous_generation_admiration_for_earlier_painters",
    "Haskell says Sasso seems to have felt the admiration of a previous generation for the rich, bold virtuosity of earlier eighteenth-century painters.",
    "Haskell", "authorial interpretation", "Retain Haskell's 'seems' qualification; the source does not name a particular admired work.",
    ["cand-2364", "cand-11543"], frag(22, "Certainly Sasso seems", "painters."), ocr_corrections=fix_l22)

add("st-chp16-p374-refine-canova-requests-modello", BODY, 22, "cand-0532", "cand-10610",
    "canova_wrote_from_rome_to_request_a_tiepolo_modello",
    "Haskell says Canova wrote from Rome to ask for a Tiepolo modello.", "Haskell", "authorial report",
    "The requested modello is not titled or otherwise individually identified.",
    ["cand-0532", "cand-4490", "cand-10608", "cand-10610"],
    frag(22, "When Canova wrote from Rome", "by Tiepolo,"), True)
old = by_sid["st-chp16-p374-canova-tiepolo-modello-rumour"]
old.update(make(old["statement_id"], BODY, 22, None, "cand-2364", "report_that_sasso_had_bought_all_tiepolo_modelli",
    "Haskell reports that Canova was told Sasso had bought all the Tiepolo modelli.", "Haskell", "reported claim",
    "The speaker who told Canova is unnamed; Haskell immediately rejects the reported purchase. Do not represent it as an acquisition.",
    ["cand-0532", "cand-2364", "cand-10608", "cand-10610"],
    frag(22, "he was told that Sasso", "bought them all.4"), False, **foot4))
add("st-chp16-p374-refine-haskell-rejects-modello-rumour", BODY, 22, None, None,
    "haskell_says_reported_purchase_was_not_true",
    "Haskell says the report that Sasso had bought all such modelli was not true.", "Haskell", "explicit correction",
    "The statement rejects the reported purchase; it does not determine which individual works Sasso owned.",
    ["cand-2364", "cand-10610"], frag(22, "In fact this was not true", "not true,"))
add("st-chp16-p374-refine-haskell-interprets-modello-rumour", BODY, 22, "cand-2364", "cand-11543",
    "haskell_probably_reads_rumour_as_reflecting_sassos_painting_taste",
    "Haskell says the rumour probably reflects Sasso's known love of this kind of painting.", "Haskell", "authorial interpretation",
    "Retain 'probably'; this is Haskell's interpretation, not evidence that Sasso bought all the modelli.",
    ["cand-2364", "cand-11543"], frag(22, "but the rumour probably reflects", "painting."))

old = by_sid["st-chp16-p374-sasso-posthumous-collection-partial"]
cross = {k: old["qualifiers"][k] for k in ("predicate_status", "cross_reference_segments", "cross_reference_text", "cross_reference_text_pending") if k in old["qualifiers"]}
old.update(make(old["statement_id"], BODY, 22, "cand-10598", None, "sasso_collection_inventory_partial_continues_on_p375",
    "Haskell lists Tiepolo pictures, one Sasso copy, 100 drawings, and modelli by Ricci and Pittoni among the collection's contents; the list continues on p.375.",
    "Haskell", "authorial report", "The list is partial; the named works and copied picture are not individually identified.",
    ["cand-2364", "cand-10598", "cand-2569", "cand-2624", "cand-10612", "cand-11500", "cand-1674", "cand-2154", "cand-1950"],
    frag(22, "there were a number of such pictures", "Ricci, Pittoni"), False,
    predicate_status="partial", cross_reference_segments=["chp-16:16_CHP-16_intro:l24-36"],
    cross_reference_text="P.374 L22 ends the partial inventory with modelli by Pittoni; p.375 L25 continues 'and Piazzetta' and adds drawings and sketches.",
    cross_reference_text_pending=True))
# The original pointer from p.375 remains on this stable statement ID.
auction_quote = frag(22, "In the collection he made for himself", "after his death in 1803")
add("st-chp16-p374-refine-sasso-collection-auction", BODY, 22, "cand-10598", "cand-11549",
    "sasso_collection_auctioned_after_his_death_in_1803",
    "Haskell says Sasso's self-made collection was auctioned after his death in 1803.", "Haskell", "authorial report",
    "The sale catalogue was not independently consulted.", ["cand-2364", "cand-10598", "cand-11549"], auction_quote, True)

# Split note 3's archival locator from its separate dated-letter reference.
old = by_sid[note3_repo]
old.update(make(note3_repo, NOTES, 74, "cand-10614", "cand-6589", "note_locates_armanni_sasso_letter_volumes",
    "Haskell's note locates two volumes of Armanni-Sasso letters in the Archivio of the Seminario Patriarcale, Venice, MSS. 565 and 566.",
    "Haskell's note", "archival locator", "The manuscripts were not consulted.",
    ["cand-10614", "cand-6589", "cand-2719"], frag(74, "3 Two volumes", "MSS. 565 and 566."), False,
    cited_source_independently_consulted=False, **foot3, ocr_corrections=fix_l74))
add(note3_letter, NOTES, 74, "cand-10615", "cand-1973", "note_says_poore_discussed_in_letter_dated_7_july_1789",
    "Haskell's note says Mr Poore is discussed in a letter dated 7 July 1789.", "Haskell's note", "archival locator",
    "The manuscript was not consulted; the note does not establish that this was the exact source of Armanni's quoted remark.",
    ["cand-10615", "cand-1973"], frag(74, "Mr Poore is discussed", "7 July 1789."), False,
    cited_source_independently_consulted=False, **foot3)
old = by_sid[note3_auction]
old.update(make(note3_auction, NOTES, 74, "cand-10616", "cand-1973", "note_reports_poore_print_and_drawing_sales_without_tiepolo",
    "Haskell's note reports Richardson sales on 4 and 19 April 1805 of prints and drawings belonging to Edward Poore, with no Tiepolo reference among them.",
    "Haskell's note", "auction locator", "The sale catalogues were not independently consulted; 'Richardson' is retained as the source's abbreviated locator.",
    ["cand-10616", "cand-1973", "cand-10608"], frag(74, "In two auctions", "among them."), False,
    cited_source_independently_consulted=False, **foot3))

old = by_sid[note1]
old["original_quote"] = note72
old["qualifiers"]["ocr_corrections"] = fix_l72
old["qualifiers"]["claim"] = "Haskell's note directs readers to his fuller references on Guardi patronage in the Journal of the Warburg Institute, 1960, pages 256-276."
old["qualifiers"]["cited_source_independently_consulted"] = False
old = by_sid[note2]
old["original_quote"] = note73
old["qualifiers"]["ocr_corrections"] = fix_l73
old["qualifiers"]["claim"] = "Haskell's note identifies Letter 8 in the Strange-Sasso correspondence and dates it 22 December 1784."
old["qualifiers"]["qualification"] = "The note gives no repository or manuscript shelfmark; the letter was not consulted. The print ends with a period, while S0 has a comma."
old["qualifiers"]["cited_source_independently_consulted"] = False
old = by_sid[note4]
old["original_quote"] = note75
old["qualifiers"]["ocr_corrections"] = fix_l75
old["qualifiers"]["claim"] = "Haskell's note cites his Journal of Warburg Institute publication, 1960, page 276."
old["qualifiers"]["cited_source_independently_consulted"] = False

# Attach all three note-3 statements to both p.374 body statements using footnote 3.
for sid in ("st-chp16-p374-armanni-introduces-poore", "st-chp16-p374-armanni-quote-on-poore"):
    by_sid[sid]["qualifiers"].update(footnote_note_statement_ids=note3_ids)

# Existing note mention includes both institution and city; split it into non-overlapping spans.
inst = next(m for m in mentions if m["mention_id"] == "m-chp16-p374-sasso-0046")
inst["surface_form"] = "Seminario Patriarcale"
inst["end_char"] = str(int(inst["start_char"]) + len(inst["surface_form"]))

planned_mentions = []
segment_ranges = {BODY: range(16, 23), NOTES: range(69, 90)}
segment_offsets = {}
for segment, numbers in segment_ranges.items():
    off = 0
    segment_offsets[segment] = {}
    for n in numbers:
        segment_offsets[segment][n] = off
        off += len(lines[n - 1]) + 1

def mention(cid, surface, segment, line_no, note="", occurrence=0):
    line = lines[line_no - 1]
    positions, pos = [], 0
    while True:
        pos = line.find(surface, pos)
        if pos < 0:
            break
        positions.append(pos)
        pos += 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention surface missing at L{line_no}: {surface}")
    start = segment_offsets[segment][line_no] + positions[occurrence]
    end = start + len(surface)
    occupied = [(int(m["start_char"]), int(m["end_char"])) for m in mentions + planned_mentions if m["segment_id"] == segment]
    if any(start < b and a < end for a, b in occupied):
        raise SystemExit(f"mention overlaps existing span at L{line_no}: {surface}")
    n = len(planned_mentions) + 1
    planned_mentions.append({"mention_id": f"m-chp16-p374-refine-{n:04d}", "segment_id": segment,
                             "candidate_id": cid, "surface_form": surface,
                             "start_char": str(start), "end_char": str(end), "note": note})

mention("cand-11546", "country house", BODY, 17, "Residence near Treviso; do not assume identity with the villa at Paese.")
mention("cand-11547", "apartments", BODY, 17, "Unidentified residences in London.")
mention("cand-1239", "the artist", BODY, 19, "Haskell's description refers to Guardi in context.")
mention("cand-11548", "his works", BODY, 20, "Unidentified Guardi works reportedly owned by Strange.")
mention("cand-11543", "Venetian painting", BODY, 20)
mention("cand-8837", "neo-classical works", BODY, 20)
mention("cand-11543", "recent Venetian painting", BODY, 22)
mention("cand-11543", "earlier eighteenthcentury painters", BODY, 22,
        "S0 has a joined word; print reading is recorded in the statement's correction metadata.")
mention("cand-2719", "Venice", NOTES, 74, "Place in the manuscript repository locator.")

all_statements = list(statements)
if "st-chp16-p374-sasso-posthumous-collection-partial" not in by_sid["st-chp16-p375-sasso-collection-list-completion"]["qualifiers"].get("cross_reference_statement_ids", []):
    raise SystemExit("p.375 collection continuation no longer points to the p.374 inventory")
body_additions = [s for s in new if s["segment_id"] == BODY]
note_additions = [s for s in new if s["segment_id"] == NOTES]
collection_index = next(i for i, s in enumerate(all_statements) if s["statement_id"] == "st-chp16-p374-sasso-posthumous-collection-partial")
all_statements[collection_index + 1:collection_index + 1] = body_additions
note3_index = next(i for i, s in enumerate(all_statements) if s["statement_id"] == note3_repo)
all_statements[note3_index + 1:note3_index + 1] = note_additions
ids = [s["statement_id"] for s in all_statements]
if len(ids) != len(set(ids)):
    raise SystemExit("duplicate statement IDs after refinement")
if any(x not in {s["statement_id"] for s in all_statements} for x in note3_ids):
    raise SystemExit("note 3 link points to a missing statement")
for sid in ("st-chp16-p374-strange-pictures-list-and-custody", "st-chp16-p374-sasso-posthumous-collection-partial"):
    if sid not in {s["statement_id"] for s in all_statements}:
        raise SystemExit(f"stable cross-page anchor missing: {sid}")

# Validate new/revised quotes and offsets before any write.
segment_text = {BODY: "\n".join(lines[n - 1] for n in segment_ranges[BODY]),
                NOTES: "\n".join(lines[n - 1] for n in segment_ranges[NOTES])}
for s in all_statements:
    if s["segment_id"] in (BODY, NOTES):
        if s["original_quote"] not in segment_text[s["segment_id"]]:
            raise SystemExit(f"quote not anchored in source: {s['statement_id']}")
for m in mentions + planned_mentions:
    seg = m["segment_id"]
    if seg in segment_text:
        a, b = int(m["start_char"]), int(m["end_char"])
        if segment_text[seg][a:b] != m["surface_form"]:
            raise SystemExit(f"mention offset mismatch: {m['mention_id']}")

if not args.apply:
    print(json.dumps({"mode": "dry-run", "new_candidates": [x[0] for x in new_candidates],
                      "new_mentions": len(planned_mentions), "new_statements": len(new),
                      "p374_total_statements": sum(s["segment_id"] == BODY for s in all_statements),
                      "p374_note_total_statements": sum(s["segment_id"] == NOTES and s["statement_id"].startswith("st-chp16-p374-") for s in all_statements),
                      "checks": "hashes, quote anchors, mention offsets, unique IDs, and page cross-reference anchors pass"}, ensure_ascii=False))
    raise SystemExit(0)

backup_suffix = ".bak-s2-chp16-p374-semantic-refine-20261009"
for path in (statement_path, mention_path, candidate_path):
    backup = path.with_name(path.name + backup_suffix)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_jsonl(statement_path, all_statements)
mentions.extend(planned_mentions)
write_csv(mention_path, mention_fields, mentions)
write_csv(candidate_path, candidate_fields, candidates)
print(json.dumps({"mode": "applied", "new_candidates": len(new_candidates),
                  "new_mentions": len(planned_mentions), "new_statements": len(new),
                  "backups": [p.name + backup_suffix for p in (statement_path, mention_path, candidate_path)]}, ensure_ascii=False))
