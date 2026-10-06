"""Controlled S2 migration for printed p.261; defaults to a read-only dry run."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
P259 = "chp-9:09_CHP-9_intro:l188-200"
P260 = "chp-9:09_CHP-9_intro:l202-210"
P261 = "chp-9:09_CHP-9_intro:l212-216"
P262 = "chp-9:09_CHP-9_intro:l218-229"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASHES = {
    P260: "ffbd53ac783c55a991bc4629b6bde3328e0708acce1819a1412f55607387ce6d",
    P261: "e94cea1632b183f4153ca8a3fef9cba2f227692c01e4c904a018c000303fa97b",
    P262: "19071349bda95267fa463da2c9c65c3af827a9e978d3585bdbb715e08831f9dc",
    NOTES: "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc",
}
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p261-20261001"
PHYSICAL_PAGE = 23


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {r["segment_id"]: r for r in segments}
for sid, expected_hash in EXPECTED_HASHES.items():
    if sid not in segment_by_id:
        raise SystemExit(f"missing source segment: {sid}")
    if segment_by_id[sid]["sha256"] != expected_hash:
        raise SystemExit(f"source segment fingerprint changed: {sid}")
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("S0 OCR asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
sources = {P261: source_lines, NOTES: source_lines}


def line_offsets(segment_id):
    meta = segment_by_id[segment_id]
    offsets, offset = {}, 0
    for n in range(meta["line_start"], meta["line_end"] + 1):
        offsets[n] = offset
        offset += len(source_lines[n - 1]) + 1
    return offsets


offsets = {sid: line_offsets(sid) for sid in sources}


def quote(segment_id, first, last):
    return "\n".join(source_lines[n - 1] for n in range(first, last + 1))


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {r["segment_id"]: r for r in coverage}
expected_coverage = {
    P259: ("reviewed", "complete", "L189-200"),
    P260: ("reviewed", "partial", "L202-210"),
    P261: ("queued", "pending", ""),
    P262: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L349-403; p.255 L155 continuation"),
}
for sid, expected in expected_coverage.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage for {sid}: {row}")

candidate_ids = {r["candidate_id"] for r in candidates}
if len(candidate_ids) != len(candidates) or max(int(x.split("-")[1]) for x in candidate_ids) != 8521:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")

C = {
    "travel_account": "cand-8522",
    "venetian_householders": "cand-8544",
    "late_artists": "cand-8523",
    "pisani_palace": "cand-8524",
    "santo_stefano": "cand-8525",
    "post_1720_pictures": "cand-8526",
    "stra_pictures": "cand-8527",
    "patronage_decline": "cand-8528",
    "decoration_fashions": "cand-8529",
    "wealth_concentration": "cand-8530",
    "inventory_corpus": "cand-8531",
    "levi": "cand-8532",
    "levi_collection": "cand-8533",
    "edwards_inventories": "cand-8534",
    "muraro": "cand-8535",
    "muraro_article": "cand-8536",
    "gallo_140": "cand-8537",
    "gherardi_letter": "cand-8538",
    "biblioteca_estense": "cand-8539",
    "beltrami": "cand-8540",
    "beltrami_reference": "cand-8541",
    "france": "cand-8542",
    "venetians_quote": "cand-8543",
}
candidate_specs = [
    (8522, "Letters from Italy ... in 1770 and 1771 to a friend in France (London, 1776)", "archive", NOTES, 404,
     "Haskell's note 1 citation for the travel quotation on p.261; the cited three-volume work is attributed only to an unnamed English woman and was not independently consulted."),
    (8523, "Last generation of artists adequately represented in Venetian collections (unnamed group)", "", P261, 214,
     "Unenumerated late-seventeenth-century artist group described by Haskell; no individuals are specified in this passage."),
    (8524, "Pisani palace at S. Stefano, Venice (as named on p.261)", "place", P261, 214,
     "Palace identified by Haskell as the Pisani residence at S. Stefano; keep distinct for now from the indexed Pisani palace and the country house at Stra pending S3 alignment."),
    (8525, "S. Stefano, Venice (location named for the Pisani palace)", "place", P261, 214,
     "Place-name as printed for the palace location; the passage does not specify whether it denotes a parish, campo, or another precise locality."),
    (8526, "Unidentified pictures painted after 1720 bought for the Pisani palace at S. Stefano", "work", P261, 214,
     "A small unnamed group described by Haskell; no titles, artists, or exact number are supplied."),
    (8527, "Unidentified contemporary paintings at the Pisani country house at Stra", "work", P261, 214,
     "An unnamed group of contemporary pictures described comparatively against the palace holdings and the previous century; no titles or exact number are supplied."),
    (8528, "Reported decline of Venetian art patronage during the eighteenth century", "term", P261, 215,
     "Subject of Haskell's discussion and a contemporary debate; this candidate records the reported topic, not a measured decline or causal conclusion."),
    (8529, "New interior-decoration fashions as a possible limit on wall space", "term", P261, 216,
     "One possible explanation Haskell considers for reduced display space; he says it cannot by itself explain the decline."),
    (8530, "Concentration of money in a small inner group of Venetian families", "term", P261, 216,
     "Haskell's qualified account of wealth becoming more restricted; the group is unnamed and no wealth measure is supplied here."),
    (8531, "Eighteenth-century Venetian inventories (unnamed archival corpus)", "archive", NOTES, 405,
     "Plural inventories cited by Haskell as evidence for collecting patterns; some are in C. A. Levi's 1900 collection and others remained unpublished in Venetian archives."),
    (8532, "C. A. Levi (collector named in Haskell's note)", "person", NOTES, 405,
     "Person identified only by initials and surname in the note; identity is not resolved here."),
    (8533, "C. A. Levi's 1900 collection of Venetian inventories", "archive", NOTES, 405,
     "Collection cited as containing some eighteenth-century Venetian inventories; its title and publication or custody details are not supplied."),
    (8534, "Pietro Edwards inventories in Seminario Patriarcale MS 788.13", "archive", NOTES, 405,
     "The manuscript locator named in Haskell's note for inventories drawn up by Pietro Edwards at the fall of the Venetian Republic; the manuscript was not independently consulted."),
    (8535, "Muraro (author cited in Emporium)", "person", NOTES, 406,
     "Surname-only author citation; first name and identity are unresolved."),
    (8536, "Muraro, Emporium, 1960, pages 195-218 (citation locator)", "archive", NOTES, 406,
     "Bibliographic locator in Haskell's note 3; title and cited pages were not independently consulted."),
    (8537, "Gallo, 1945, pages 140 ff. (citation locator)", "archive", NOTES, 407,
     "Bibliographic locator in Haskell's note 4; title and cited pages were not independently consulted. Keep separate from other Gallo locators pending S3."),
    (8538, "Letter from P. E. Gherardi to L. A. Muratori, 20 February 1745", "archive", NOTES, 408,
     "Letter cited by Haskell as the source for the p.261 contemporary observation; Biblioteca Estense, Modena is the stated repository. The letter was not independently consulted."),
    (8539, "Biblioteca Estense, Modena", "institution", NOTES, 408,
     "Repository named for the 1745 Gherardi-Muratori letter."),
    (8540, "Beltrami (author cited in Haskell's note)", "person", NOTES, 409,
     "Surname-only author citation; identity is unresolved."),
    (8541, "Beltrami, 1954 (citation locator)", "archive", NOTES, 409,
     "Bibliographic locator in Haskell's note 6; title and cited work were not supplied or independently consulted."),
    (8542, "France as the residence named in the title of Letters from Italy", "place", NOTES, 404,
     "Geographical country named as the residence of the book's unnamed recipient; no identity is inferred."),
    (8543, "Venetians in the unnamed traveler's generalization about picture display", "term", P261, 214,
     "Collective group as represented in the anonymous travel quotation; preserve its generalized scope and do not treat it as a representative survey."),
]
natural_keys = {(r["canonical_name"], r["suggested_type"]) for r in candidates}
for n, name, kind, source_segment, line_no, detail in candidate_specs:
    cid = f"cand-{n:04d}"
    if cid in candidate_ids or (name, kind) in natural_keys:
        raise SystemExit(f"candidate ID/natural-key collision: {cid} {name} / {kind}")
    candidates.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                       "index_page_range": "", "suggested_type": kind, "status": "open",
                       "index_source_file": "", "sub_entry": "", "detail": detail,
                       "exclude_reason": "", "candidate_origin": "body-mention",
                       "candidate_source_ref": f"{source_segment}#L{line_no}"})
    candidate_ids.add(cid)
    natural_keys.add((name, kind))

existing_mention_ids = {r["mention_id"] for r in mentions}
existing_spans = {(r["segment_id"], r["start_char"], r["end_char"]) for r in mentions}
new_mentions = []


def mention(segment_id, line, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p261-{suffix}"
    if mid in existing_mention_ids or any(r["mention_id"] == mid for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mid}")
    pos, start_at = -1, 0
    line_text = source_lines[line - 1]
    for _ in range(occurrence + 1):
        pos = line_text.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at L{line}: {surface!r}")
        start_at = pos + len(surface)
    start = offsets[segment_id][line] + pos
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((r["segment_id"], r["start_char"], r["end_char"]) == span for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": segment_id, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    (P261,214,"venetians-quote","cand-8543","The Venetians","Generalized collective in a nested anonymous travel quotation."),
    (P261,214,"older-patricians","cand-8137","older patrician families","Older Venetian aristocratic families; reuse the existing collective candidate."),
    (P261,214,"inventory-pattern","cand-8531","their inventories","Inventories of the older patrician families; note 2 describes the cited corpus."),
    (P261,214,"last-artists","cand-8523","last generation of artists","Unenumerated artist group described by Haskell."),
    (P261,214,"venetian-collections","cand-2719","Venetian collections","Venice as the location of collections, not the Republic."),
    (P261,214,"pisani-family","cand-8500","The Pisani","Reuse the family candidate introduced in the preceding p.260 passage."),
    (P261,214,"almoro","cand-1941","Almord","S0 OCR spelling; p.261 scan reads Almorò."),
    (P261,214,"zais","cand-2830","Giuseppe Zais","Existing index candidate reused."),
    (P261,214,"pisani-palace","cand-8524","their palace at S. Stefano","Building as named in the source; kept distinct from the Stra country house pending S3."),
    (P261,214,"santo-stefano","cand-8525","S. Stefano","Location name in the palace description; exact locality type remains unresolved."),
    (P261,214,"post1720-pictures","cand-8526","few pictures painted after 1720","Unnamed group; no titles or exact count are given."),
    (P261,214,"stra-country-house","cand-3990","country house at Stra","Existing place candidate for Villa Pisani at Stra; S3 will align identity."),
    (P261,214,"stra-site","cand-8317","Stra","Existing candidate for the locality named as the country-house site."),
    (P261,214,"stra-paintings","cand-8527","contemporary paintings","Unnamed works at the country house; no titles or count are supplied."),
    (P261,215,"decline-patronage","cand-8528","decline of art patronage","Reported subject of the passage, not an independently measured trend."),
    (P261,215,"observer-gherardi","cand-1155","one observer","Footnote 5 identifies the cited source as a letter by P. E. Gherardi; the letter itself was not read."),
    (P261,215,"these-nobles","cand-8124","these nobles","Collective Venetian patrician group; the source does not name families here."),
    (P261,216,"decorative-fashion","cand-8529","New fashions in interior decoration","One possible factor Haskell discusses, not a decisive cause."),
    (P261,216,"old-family-palaces","cand-8137","palaces of older families","Reuse the existing older Venetian aristocracy collective."),
    (P261,216,"wealthy-families","cand-8124","extremely important families","Unnamed Venetian family group in Haskell's economic assessment."),
    (P261,216,"small-inner-group","cand-8530","small inner group","Unnamed group to which money was increasingly restricted."),
    (P261,216,"foscarini-family","cand-1057","The Foscarini","Existing family candidate; do not substitute Marco Foscarini the person."),
    (P261,216,"carmini-church","cand-8458","the Carmini","Existing Church of the Carmini place candidate."),
    (P261,216,"venice-city","cand-2719","the city","Venice by chapter context; distinct from the Republic."),
    (NOTES,404,"travel-book","cand-8522","Letters from Italy","Book cited in note 1; author remains unnamed."),
    (NOTES,404,"english-woman","cand-8522","an English woman","Anonymous author description in the bibliographic citation; not an identified person."),
    (NOTES,404,"france","cand-8542","France","Residence stated for the unnamed recipient."),
    (NOTES,404,"london","cand-1422","London","Publication place; existing candidate reused."),
    (NOTES,404,"travel-volume","cand-8522","HI","S0 OCR; p.261 scan reads volume III."),
    (NOTES,405,"inventories-corpus","cand-8531","Venetian inventories","Plural source materials; no exact count or complete list is supplied."),
    (NOTES,405,"levi","cand-8532","C. A. Levi","Identity is limited to initials and surname in the note."),
    (NOTES,405,"levi-collection","cand-8533","C. A. Levi’s collection of 1900","Collection locator; title and form are not supplied."),
    (NOTES,405,"seminario","cand-6589","Seminario Patriarcale","Existing manuscript repository candidate reused."),
    (NOTES,405,"ms78813","cand-8534","MSS. 788.13","Manuscript locator as printed in the note."),
    (NOTES,405,"edwards","cand-0965","Pietro Edwards","Existing index candidate reused."),
    (NOTES,405,"venetian-republic","cand-6255","the Republic","Venetian Republic as political institution, not the city."),
    (NOTES,406,"muraro","cand-8535","Muraro","Surname-only author citation."),
    (NOTES,406,"emporium-article","cand-8536","Emporium, i960, pp. 195-218","Citation as OCRed; scan corrects i960 to 1960."),
    (NOTES,407,"gallo","cand-8514","Gallo","Existing surname-only author candidate reused."),
    (NOTES,407,"gallo-140","cand-8537","1945, pp. 140 ff.","Citation locator; distinct from the other Gallo page locators until aligned."),
    (NOTES,408,"gherardi","cand-1155","P. E. Gherardi","Existing index candidate for Abate Pietro Ercole Gherardi; retain S3 identity decision."),
    (NOTES,408,"muratori","cand-1717","L. A. Muratori","Existing index candidate reused."),
    (NOTES,408,"gherardi-letter","cand-8538","Letter from P. E. Gherardi to L. A. Muratori","Specific archive document named in the footnote."),
    (NOTES,408,"estense","cand-8539","Biblioteca Estense","Repository named for the letter."),
    (NOTES,408,"modena","cand-3416","Modena","Existing place candidate reused."),
    (NOTES,409,"beltrami","cand-8540","Beltrami","Surname-only author citation."),
    (NOTES,409,"beltrami-reference","cand-8541","Beltrami, 1954","Citation locator; title is not supplied."),
]
for row in M:
    mention(*row)

new_statements = []
existing_statement_ids = {r["statement_id"] for r in statements}


def statement(suffix, segment_id, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker=None, speaker="Haskell", text_layer="authorial narrative", extras=None):
    sid = f"st-chp9-p261-{suffix}"
    if sid in existing_statement_ids or any(r["statement_id"] == sid for r in new_statements):
        raise SystemExit(f"duplicate statement ID: {sid}")
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement span out of segment: {sid}")
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 261,
         "pdf_physical_page": PHYSICAL_PAGE, "claim": claim, "speaker": speaker,
         "text_layer": text_layer, "qualification": qualification,
         "mentioned_candidate_ids": list(dict.fromkeys(x for x in mentioned if x))}
    if marker is not None:
        q["footnote_marker"] = marker
    if extras:
        q.update(extras)
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": q,
                           "original_quote": quote(segment_id, first, last), "origin": "book",
                           "source_file": meta["source_file"]})


def body(suffix, first, last, subject, obj, predicate, claim, qualification, mentioned,
         marker=None, speaker="Haskell", text_layer="authorial narrative", extras=None):
    statement(suffix, P261, first, last, subject, obj, predicate, claim, qualification,
              mentioned, marker, speaker, text_layer, extras)


def note(suffix, line, subject, obj, predicate, claim, qualification, mentioned, marker,
         *, text_layer="footnote citation", speaker="Haskell's footnote", extras=None):
    statement(suffix, NOTES, line, line, subject, obj, predicate, claim, qualification,
              mentioned, marker, speaker, text_layer, extras)


body("decorative-hanging-report",213,213,None,None,
     "travellers_report_decorative_wall_hanging",
     "Haskell says travellers reported that pictures were hung on Venetian walls to fulfil a purely decorative function.",
     "The sentence begins on p.260 L210 and closes here; the general reference to travellers is broader than the specific quotation that follows.",
     [],extras={"cross_reference_segments":[{"segment_id":P260,"source_line_start":210,"source_line_end":210}],
     "ocr_corrections":[{"source_line":213,"ocr":"from travellers that pictures were hung on walls to fulfil a purely decorative function.","print":"We know too from travellers that pictures were hung on walls to fulfil a purely decorative function.","basis":"CHP-9.pdf physical page 23 plus p.260 L210."}]})
body("traveller-wall-display-quotation",214,214,None,"cand-8543",
     "venetian_picture_display_covered_walls",
     "The unnamed English woman quoted by Haskell says Venetians covered their walls with pictures to hide the hanging, often displaying more bad than good pictures and hanging works without regard to their suitability or light.",
     "Nested travel quotation, cited by Haskell's note 1; the publication and its quoted claims were not independently consulted. Preserve the speaker's broad generalization rather than treating it as a representative survey.",
     ["cand-8543","cand-8522"],marker=1,
     speaker="Unnamed English woman, as identified in Haskell's footnote",text_layer="nested travel quotation",
     extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":404,"source_line_end":404}],
             "ocr_corrections":[{"source_line":214,"ocr":"closej","print":"close,","basis":"CHP-9.pdf physical page 23."}]})
body("decorative-aim-achieved",214,214,"cand-8137",None,
     "decorative_wall_covering_aim_achieved_by_early_eighteenth_century",
     "Haskell says that by the early eighteenth century the decorative wall-covering aim had been achieved for most older patrician families.",
     "This is Haskell's historical interpretation, not a claim about every patrician family.",
     ["cand-8137"],extras={"ocr_corrections":[{"source_line":214,"ocr":"Almord","print":"Almorò","basis":"CHP-9.pdf physical page 23."}]})
body("inventories-contemporary-pictures-decline",214,214,"cand-8137","cand-8531",
     "commissioning_and_purchase_of_contemporary_pictures_declined",
     "Haskell says inventories repeatedly show a considerable decline in the commissioning or purchase of contemporary pictures after the early-eighteenth-century point just described.",
     "Retain Haskell's interpretation of inventories and the comparative wording; the cited inventory corpus is described in footnote 2 and was not independently inspected.",
     ["cand-8137","cand-8531"],marker=2,
     extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":405,"source_line_end":405}]})
body("last-represented-artists",214,214,"cand-8523","cand-2719",
     "last_generation_adequately_represented_in_venetian_collections",
     "Haskell identifies the last generation of artists adequately represented in Venetian collections as dating from the very end of the seventeenth century.",
     "The generation is unnamed and unenumerated; the statement does not identify individual artists or collections.",
     ["cand-8523","cand-2719"])
body("pisani-described-as-lavish",214,214,"cand-8500",None,
     "pisani_described_as_most_lavish_family_of_the_time",
     "Haskell describes the Pisani as by far the most lavish family of the time.",
     "Preserve this as Haskell's comparative description, not an independently measured ranking.",
     ["cand-8500"])
body("pisani-special-patrons-zais",214,214,"cand-8500","cand-2830",
     "pisani_special_patronage_of_landscape_painter_zais",
     "Haskell says the Pisani were, for some years during Almorò's youth (1740-66), special patrons of the landscape painter Giuseppe Zais.",
     "S2 relationship candidate only. The sentence assigns patronage to the Pisani collectively; it does not say Almorò personally commissioned works. Footnote 3 is a locator, not independently verified.",
     ["cand-8500","cand-1941","cand-2830"],marker=3,
     extras={"relation_candidate":True,"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":406,"source_line_end":406}],
             "ocr_corrections":[{"source_line":214,"ocr":"Almord","print":"Almorò","basis":"CHP-9.pdf physical page 23."}]})
body("pisani-post1720-palace-pictures",214,214,"cand-8500","cand-8526",
     "pisani_bought_few_post1720_pictures_for_santo_stefano_palace",
     "Haskell says the Pisani bought only a few pictures painted after 1720 for their palace at S. Stefano.",
     "The artworks are unnamed and uncounted; the palace remains distinct from the country house at Stra pending S3 identity alignment.",
     ["cand-8500","cand-8524","cand-8525","cand-8526"],extras={"relation_candidate":True})
body("stra-house-painting-comparison",214,214,"cand-3990","cand-8527",
     "stra_country_house_contemporary_paintings_compared_with_palace_and_previous_century",
     "Haskell says the Pisani country house at Stra, built in the 1740s, had many more contemporary paintings than their S. Stefano palace, though noticeably fewer than the previous century's holdings.",
     "The relative quantities are Haskell's comparison; neither the individual paintings nor an exact count is supplied. Footnote 4's source was not independently consulted.",
     ["cand-8500","cand-3990","cand-8317","cand-8524","cand-8527"],marker=4,
     extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":407,"source_line_end":407}]})
body("decline-debated",215,215,None,"cand-8528",
     "eighteenth_century_patronage_decline_discussed_contemporaneously",
     "Haskell says the decline of eighteenth-century art patronage was much discussed at the time.",
     "This reports the existence of contemporary discussion; it does not establish a uniform decline across all patrons or media.",
     ["cand-8528"])
body("gherardi-observer-quote",215,215,"cand-1155","cand-8124",
     "gherardi_observed_nobles_disliked_spending_on_pictures",
     "The observer cited by Haskell says that Venetian nobles did not like spending money on pictures.",
     "Nested quotation attributed by footnote 5 to P. E. Gherardi's letter to L. A. Muratori; the letter was not independently read. Preserve this as one observer's opinion, not a general fact about all nobles.",
     ["cand-1155","cand-8124","cand-8538"],marker=5,
     speaker="P. E. Gherardi, as identified in Haskell's footnote",text_layer="nested quotation",
     extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":408,"source_line_end":408}],
             "ocr_corrections":[{"source_line":215,"ocr":"T don’t find’","print":"‘I don’t find’","basis":"CHP-9.pdf physical page 23."}]})
body("corrupt-age-explanations",215,215,None,"cand-8528",
     "proposed_causes_often_reduced_to_corrupt_age_diatribes",
     "Haskell says various explanations for the decline often amounted to little more than worn-out denunciations of the age's corruption.",
     "This is Haskell's characterization of explanations given at the time, not his endorsement of corruption as the cause.",
     ["cand-8528"],extras={"ocr_corrections":[{"source_line":215,"ocr":"welkworn","print":"well-worn","basis":"CHP-9.pdf physical page 23."}]})
body("caution-corruption-explanation",216,216,None,"cand-8528",
     "corruption_and_fine_arts_can_coexist",
     "Haskell cautions that explanations based on corruption or decadence should be accepted only carefully, since corruption and fine arts can coexist.",
     "This is Haskell's methodological qualification of moral-decline explanations, not an externally tested causal conclusion.",
     ["cand-8528"],extras={"ocr_corrections":[{"source_line":216,"ocr":"sine arts","print":"fine arts","basis":"CHP-9.pdf physical page 23."}]})
body("concrete-causes-hard-to-find",216,216,None,"cand-8528",
     "concrete_reasons_for_patronage_decline_difficult_to_find",
     "Haskell says it is difficult to identify more concrete reasons for the decline.",
     "The claim describes the author's assessment of the evidence available in this discussion.",
     ["cand-8528"])
body("interior-fashions-limited-wall-space",216,216,"cand-8529",None,
     "new_interior_fashions_limited_wall_space",
     "Haskell says new interior-decoration fashions certainly played some part in limiting available wall space.",
     "Preserve the partial causal role; the author later says these factors cannot have been decisive.",
     ["cand-8529"])
body("old-palace-galleries-already-filled",216,216,"cand-8137",None,
     "older_family_palace_galleries_filled_with_centuries_of_art",
     "Haskell says the galleries in older families' palaces were already filled with accumulated art from centuries.",
     "General account of older family palaces; no individual gallery or work is named.",
     ["cand-8137"],extras={"ocr_corrections":[{"source_line":216,"ocr":"silled","print":"filled","basis":"CHP-9.pdf physical page 23."}]})
body("display-factors-not-decisive",216,216,None,"cand-8529",
     "wall_space_factors_not_decisive_explanation",
     "Haskell says the new fashions and already-filled galleries cannot have been decisive explanations of the patronage decline.",
     "This is the author's explicit qualification of the preceding proposed factors.",
     ["cand-8529","cand-8137","cand-8528"])
body("economic-assessment-difficult",216,216,None,"cand-8530",
     "economic_situation_difficult_to_assess",
     "Haskell says the economic situation is still more difficult to assess.",
     "This signals uncertainty in the author's account; it does not assert a verified economic measure.",
     ["cand-8530"])
body("important-families-lost-wealth",216,216,"cand-8124",None,
     "important_families_declined_in_wealth",
     "Haskell says many extremely important families drastically declined in wealth during the eighteenth century.",
     "The families are unnamed and no family-level figures are given here.",
     ["cand-8124","cand-8530"])
body("wealth-restricted-inner-group",216,216,"cand-8530",None,
     "money_increasingly_restricted_to_small_inner_group",
     "Haskell says money became increasingly restricted to a small inner group.",
     "The group is unnamed and the sentence continues into the following Foscarini example; note 6 is a citation locator only.",
     ["cand-8530","cand-8124"],marker=6,
     extras={"cross_reference_segments":[{"segment_id":NOTES,"source_line_start":409,"source_line_end":409}]})
body("foscarini-rumoured-richest",216,216,"cand-1057","cand-2719",
     "foscarini_family_rumoured_richest_in_venice",
     "Haskell reports that the Foscarini, who lived opposite the Carmini, were rumoured to be the richest family in the city.",
     "The source explicitly marks this as rumour; the sentence continues on p.262 with an income figure. Do not treat the report as verified wealth data.",
     ["cand-1057","cand-8458","cand-2719"],
     extras={"cross_reference_segments":[{"segment_id":P262,"source_line_start":218,"source_line_end":218}]})

note("note1-traveller-source",404,None,"cand-8522",
     "citation_locator_letters_from_italy_1776_volume_iii_page_274",
     "Haskell's note 1 cites Letters from Italy ... in the years 1770 and 1771 to a friend residing in France, by an English woman, London 1776, volume III, page 274.",
     "The author's identity is not supplied; the cited book and page were not independently consulted.",
     ["cand-8522","cand-8542","cand-1422"],1,
     extras={"ocr_corrections":[{"source_line":404,"ocr":"ia France","print":"in France","basis":"CHP-9.pdf physical page 23."},{"source_line":404,"ocr":"HI","print":"III","basis":"CHP-9.pdf physical page 23."}]})
note("note2-levi-inventory-collection",405,"cand-8532","cand-8533",
     "levi_collection_includes_venetian_inventories",
     "Haskell's note 2 says a number of eighteenth-century Venetian inventories are included in C. A. Levi's collection of 1900.",
     "The exact number, collection title, and inventory contents are not supplied; the collection was not independently consulted.",
     ["cand-8531","cand-8532","cand-8533"],2,
     text_layer="footnote claim",extras={"relation_candidate":True})
note("note2-seminario-edwards-inventories",405,"cand-6589","cand-8534",
     "seminario_ms78813_holds_edwards_inventories",
     "Haskell's note says other Venetian inventories remained unpublished in the archives, especially at the Seminario Patriarcale, where MSS. 788.13 contains inventories drawn up by Pietro Edwards at the downfall of the Republic.",
     "The repository and manuscript assertions are reported by Haskell; the manuscript was not independently consulted. Preserve the Republic of Venice as the institution meant by 'the Republic'.",
     ["cand-8531","cand-6589","cand-8534","cand-0965","cand-6255"],2,
     text_layer="footnote claim",extras={"relation_candidate":True})
note("note3-muraro-emporium",406,None,"cand-8536",
     "citation_locator_muraro_emporium_1960_pages_195_218",
     "Haskell's note 3 cites Muraro in Emporium, 1960, pages 195-218.",
     "Citation locator only; the article was not independently consulted.",
     ["cand-8535","cand-8536"],3,
     extras={"ocr_corrections":[{"source_line":406,"ocr":"i960","print":"1960","basis":"CHP-9.pdf physical page 23."}]})
note("note4-gallo-1945-pages_140ff",407,None,"cand-8537",
     "citation_locator_gallo_1945_pages_140_ff",
     "Haskell's note 4 cites Gallo, 1945, pages 140 and following.",
     "Citation locator only; title and cited pages were not independently consulted.",
     ["cand-8514","cand-8537"],4)
note("note5-gherardi-letter",408,"cand-1155","cand-8538",
     "gherardi_letter_to_muratori_1745",
     "Haskell's note 5 identifies a letter from P. E. Gherardi to L. A. Muratori dated 20 February 1745, held at Biblioteca Estense, Modena.",
     "The letter was not independently consulted; retain the source's initials, date, and repository locator.",
     ["cand-1155","cand-1717","cand-8538","cand-8539","cand-3416"],5,
     text_layer="footnote claim",extras={"relation_candidate":True,"ocr_corrections":[{"source_line":408,"ocr":"8 Letter","print":"5 Letter","basis":"CHP-9.pdf physical page 23."}]})
note("note6-beltrami-1954",409,"cand-8540","cand-8541",
     "citation_locator_beltrami_1954",
     "Haskell's note 6 cites Beltrami, 1954.",
     "Citation locator only; the author identity, title, and cited work remain unresolved.",
     ["cand-8540","cand-8541"],6,
     extras={"ocr_corrections":[{"source_line":409,"ocr":"8 Beltrami","print":"6 Beltrami","basis":"CHP-9.pdf physical page 23."}]})

all_candidate_ids = {r["candidate_id"] for r in candidates}
if len({r["mention_id"] for r in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("mention IDs are not unique")
if len({r["statement_id"] for r in statements + new_statements}) != len(statements) + len(new_statements):
    raise SystemExit("statement IDs are not unique")
for row in new_mentions:
    sid = row["segment_id"]
    start, end = int(row["start_char"]), int(row["end_char"])
    meta = segment_by_id[sid]
    segment_text = "\n".join(source_lines[n - 1] for n in range(meta["line_start"], meta["line_end"] + 1))
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    refs = set(q.get("mentioned_candidate_ids", []))
    refs.update(x for x in [row.get("subject_candidate_id"), row.get("object_candidate_id")] if x)
    if not refs <= all_candidate_ids:
        raise SystemExit(f"statement foreign key error {row['statement_id']}: {refs-all_candidate_ids}")
    if row["original_quote"] != quote(row["segment_id"], q["source_line_start"], q["source_line_end"]):
        raise SystemExit(f"quote mismatch: {row['statement_id']}")

coverage_by_id[P260].update({
    "disposition":"reviewed","migration_status":"complete","source_line_ranges":"L202-210",
    "note":"Printed p.260 (CHP-9.pdf physical p.22) reviewed against scan. L203 closes p.259 L200; L210 'We know too' is closed by p.261 L213. P.260 notes 1-9 are migrated at consolidated L395-403; note 8 has its own complete visual-transcription anchor."})
coverage_by_id[P261].update({
    "disposition":"reviewed","migration_status":"partial","source_line_ranges":"L213-216",
    "note":"Printed p.261 (CHP-9.pdf physical p.23) reviewed against scan. L213 closes p.260 L210; the Foscarini sentence at L216 continues at p.262 L218. Notes 1-6 are migrated at consolidated L404-409. Page-image OCR corrections are recorded in S2; source OCR is unchanged."})
coverage_by_id[NOTES].update({
    "disposition":"reviewed","migration_status":"partial","source_line_ranges":"L349-409; p.255 L155 continuation",
    "note":"Consolidated p.258-261 notes through p.261 notes 1-6 have been migrated at L387-409; p.255 note 1 continuation at L155 remains cross-linked to L370. Later notes from L410 remain queued. Citation locators are not independent verification."})

summary = {
    "new_candidates": len(candidate_specs), "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"], coverage_by_id[sid]["source_line_ranges"]]
                 for sid in (P260, P261, NOTES)},
    "cross_page_closure": "p.260 L210 -> p.261 L213; p.261 L216 -> p.262 L218",
    "next_body_segment": P262, "next_notes": "L410-461",
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for src, bak in zip(paths, backups):
        shutil.copy2(src, bak)
    try:
        write_csv(candidate_path, candidate_fields, candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for dst, bak in zip(paths, backups):
            shutil.copy2(bak, dst)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
