"""Controlled S2 migration for printed p.309; dry-run unless --apply."""
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
P308 = "chp-10:10_CHP-10_intro:l456-466"
P309 = "chp-10:10_CHP-10_intro:l468-479"
P310 = "chp-10:10_CHP-10_intro:l481-489"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "f94d7f83181d838df32049848707d735907115f01dde74e89dac6de11d635dac"
BACKUP = ".bak-s2-chp10-p309-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
first, last, PAGE, PHYSICAL = 468, 479, 309, 38
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[467].strip() != "[Page 309]" or "Vitruvius Britannicus" not in body:
    raise SystemExit(f"p.309 source segment mismatch: {digest}")
line_offsets, offset = {}, 0
for line_no in range(first, last + 1):
    line_offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9252:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P308, ("reviewed", "partial")), (P309, ("queued", "pending")),
                      (P310, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P309 for row in mentions) or any(row["segment_id"] == P309 for row in statements):
    raise SystemExit("p.309 already has mention or statement rows")

E = {
    "jones": "cand-1335", "burlington": "cand-0470", "campbell": "cand-0493",
    "morris": "cand-1707", "vanbrugh": "cand-2690", "canaletto": "cand-0514",
    "smith": "cand-2440", "nogari": "cand-1743", "vandyke": "cand-8909",
    "palladio": "cand-1807", "gallacini": "cand-1110", "visentini": "cand-2783",
    "piranesi": "cand-1938", "memmo": "cand-1642", "tiepolo": "cand-2569",
    "algarotti": "cand-0041", "dresden_court": "cand-9075", "zuccarelli": "cand-2883",
    "zais": "cand-2830", "george_iii": "cand-1141", "castiglione": "cand-0602",
    "carracci_collective": "cand-4318", "sagredo": "cand-2329", "england": "cand-8983",
    "smith_palace": "cand-9171", "english_taste": "cand-9187", "smith_sale": "cand-9178",
    "smith_shift": "cand-9211", "baroque": "cand-4500", "horses_caprice": "cand-9245",
    "overdoors": "cand-9251", "smith_library": "cand-9177", "venice": "cand-2719",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("vitruvius_britannicus", "Colen Campbell’s Vitruvius Britannicus (architectural book and engravings)", "archive",
     "Haskell identifies this work as the principal source of engravings for the English architectural pictures; edition and plate references are not specified here.", 471),
    ("nogari_jones_portrait", "Giuseppe Nogari’s commissioned portrait of Inigo Jones", "work",
     "A portrait commissioned for Joseph Smith; Haskell says its model was described as ‘Vandyke, with the plan of the Banquetting House in his hands’. Do not treat that quoted label as independent attribution evidence.", 471),
    ("banquetting_house", "Banquetting House named in the Inigo Jones portrait description", "place",
     "Named through the plan held in the portrait description; this passage does not independently specify the building’s location or exact identity.", 471),
    ("jones_palladio_editions", "Editions of architectural works by Inigo Jones and Palladio brought out by Joseph Smith", "archive",
     "A plural publication group; Haskell gives no titles or edition dates in this passage.", 472),
    ("gallacini_treatise", "Teofilo Gallacini’s Trattato sopra gli errori degli architetti (manuscript and 1767 publication)", "archive",
     "Smith published one manuscript from his collection in 1767; the title is normalized from the page image while the S0 OCR joins ‘sopra gli’ as ‘sopragli’.", 473),
    ("visentini_gallacini_update", "Antonio Visentini’s updated version of Gallacini’s Trattato sopra gli errori degli architetti", "archive",
     "Haskell says the book was soon brought up to date by Visentini with attacks on Baroque architects and successors down to Piranesi; exact edition and title-page details are not supplied.", 474),
    ("tiepolo_unrealized_commission", "Unidentified important work from Giambattista Tiepolo diverted to the Dresden court", "work",
     "Haskell says the commission came to nothing because Algarotti expropriated the work for Dresden; the original commissioner, title, execution status and version remain unspecified.", 477),
    ("visentini_marble_facade", "Antonio Visentini’s new classicising marble façade built in the first year of the 1750s", "work",
     "An architectural component mentioned without a fully resolved palace referent; the source’s ‘his palace’ pronoun is preserved as ambiguous.", 478),
    ("facade_palace_unresolved", "Unidentified palace for which Visentini built a new marble façade", "place",
     "The source says ‘his palace’; the pronoun’s referent is not resolved here and is not merged with Joseph Smith’s palace.", 478),
    ("smith_castiglione_carracci_drawings", "Drawings by Castiglione and the Carracci acquired by Joseph Smith in 1752", "work",
     "A grouped acquisition described as including many drawings by Castiglione and the Carracci; individual sheets and exact count are not supplied.", 479),
    ("smith_sagredo_old_masters", "Old-master paintings acquired by Joseph Smith from Zaccaria Sagredo’s heirs", "work",
     "The passage dates this acquisition to the same year as the preceding 1752 reference; the heirs are unnamed and no individual paintings are identified.", 479),
    ("smith_canaletto_return_pictures", "Additional pictures acquired by Joseph Smith from Canaletto on the artist’s return", "work",
     "Includes an unspecified number of English views; the sentence continues on p.310 and does not yet state the destination of Canaletto’s return.", 479),
    ("neo_palladianism", "Strict neo-Palladianism in Joseph Smith’s architectural taste", "term",
     "Haskell’s p.309 formulation of the strict Palladian canon associated with Smith’s taste in 1746; compare against other Palladianism candidates at S3.", 477),
    ("venetian_classicism", "Move towards classicism across Venetian art in the 1740s", "term",
     "Haskell’s description of a broad tendency across Venetian art, which he says Smith’s patronage helped promote.", 477),
    ("zais_landscapes_smith", "Unspecified landscapes by Giuseppe Zais excluded from Joseph Smith’s later picture sale", "work",
     "Haskell says Smith did not think them worth including in the batch later sold to George III; individual landscapes are unidentified.", 478),
]
newc, C = [], {}
for i, (key, name, kind, detail, line) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{i:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    newc.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name,
                 "index_page_range": "", "suggested_type": kind, "status": "open",
                 "index_source_file": "", "sub_entry": "", "detail": detail,
                 "exclude_reason": "", "candidate_origin": "body-mention",
                 "candidate_source_ref": f"{P309}#L{line}"})

newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p309-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    line_start = line_offsets[line]
    line_end = line_start + len(src[line - 1])
    positions, at = [], line_start
    while True:
        at = body.find(surface, at)
        if at < 0 or at + len(surface) > line_end:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": P309, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    ("palladian-taste-close", 469, "taste—the Palladian", C["neo_palladianism"], "Completes p.308 L465 ‘dogmatic canon of’; the full phrase is preserved across the page boundary."),
    ("eleven-overdoor-pictures", 469, "the eleven pictures", E["overdoors"]),
    ("jones-five-pictures", 469, "Inigo Jones", E["jones"]),
    ("burlington-two-pictures", 470, "Lord Burlington", E["burlington"]),
    ("campbell-two-pictures", 470, "Colen Campbell", E["campbell"]),
    ("morris-one-picture", 470, "Roger Morris", E["morris"]),
    ("vanbrugh-one-picture", 470, "Vanbrugh", E["vanbrugh"]),
    ("vanbrugh-coreference", 470, "him", E["vanbrugh"], "Corefers to Vanbrugh."),
    ("overdoor-capricci", 471, "these capricci", E["overdoors"]),
    ("canaletto-horses-distortions", 471, "Canaletto’s Horses of St Mark’s", E["horses_caprice"]),
    ("smith-capriccio-genre", 471, "Smith", E["smith"]),
    ("overdoor-pictures-based", 471, "The pictures", E["overdoors"]),
    ("campbell-vitruvius-author", 471, "Colen Campbell", E["campbell"], "Identifies the author of Vitruvius Britannicus."),
    ("vitruvius-britannicus", 471, "Vitruvius Britannicus", C["vitruvius_britannicus"]),
    ("nogari-portrait", 471, "the portrait", C["nogari_jones_portrait"]),
    ("nogari-portrait-artist", 471, "Nogari", E["nogari"]),
    ("smith-portrait-patron-coreference", 471, "him", E["smith"], "Corefers to Smith, for whom Nogari was commissioned to paint."),
    ("portrait-subject-jones", 471, "Inigo Jones", E["jones"], "Second Jones mention in this passage; portrait subject."),
    ("vandyke-model-reference", 471, "Vandyke", E["vandyke"], "The quoted portrait label is not independent evidence for a Van Dyck work or attribution."),
    ("banquetting-house-name-start", 471, "Banquetting", C["banquetting_house"], "The printed name breaks across L471–472."),
    ("smith-publication", 472, "Smith", E["smith"]),
    ("banquetting-house-name-end", 472, "House", C["banquetting_house"], "Completes the L471–472 building name."),
    ("jones-editions", 472, "Jones", E["jones"]),
    ("palladio-editions", 473, "Palladio", E["palladio"]),
    ("editions-group", 472, "many editions", C["jones_palladio_editions"]),
    ("smith-manuscript-publication-coreference", 473, "he", E["smith"], "Corefers to Joseph Smith as publisher."),
    ("smith-library-coreference", 473, "his collection", E["smith_library"], "Smith’s manuscript/library collection; do not identify a specific shelfmark."),
    ("gallacini-manuscript", 473, "one of the manuscripts", C["gallacini_treatise"]),
    ("gallacini", 473, "TeoFilo Gallacini", E["gallacini"], "S0 OCR capitalizes the internal F; the page image reads Teofilo."),
    ("gallacini-treatise-title", 473, "Trattato sopragli errori degli architetti", C["gallacini_treatise"], "S0 joins ‘sopra gli’; the printed title has a space."),
    ("visentini-book-update", 473, "the book", C["visentini_gallacini_update"], "Corefers to the Gallacini treatise as updated by Visentini."),
    ("visentini-update-author", 474, "Antonio Visentini", E["visentini"]),
    ("baroque-architects-critique", 474, "the Baroque architects", E["baroque"]),
    ("piranesi", 474, "Piranesi", E["piranesi"]),
    ("smith-palace-books", 475, "Smith’s palace", E["smith_palace"]),
    ("memmo-quote-author", 475, "Andrea Memmo", E["memmo"]),
    ("visentini-in-memmo-quote-start", 475, "Signor Antonio", E["visentini"], "The personal name crosses the OCR line break; completed by ‘Visentini’ on p.309 L476."),
    ("visentini-in-memmo-quote-end", 476, "Visentini", E["visentini"], "Completes the p.309 L475 name ‘Signor Antonio’."),
    ("memmo-pure-simple-style", 476, "pure and simple", C["neo_palladianism"], "Memmo’s quoted characterization; retain his voice rather than Haskell’s."),
    ("neo-palladianism", 477, "neo-Palladianism", C["neo_palladianism"]),
    ("smith-1746-taste", 477, "Smith", E["smith"]),
    ("english-taste", 477, "English taste", E["english_taste"]),
    ("english-homeland", 477, "his own homeland", E["england"], "Refers to the English homeland in Haskell’s comparison."),
    ("venetian-art", 477, "Venetian art", E["venice"]),
    ("classicist-movement", 477, "classicism", C["venetian_classicism"]),
    ("smith-patronage-promotion", 477, "Smith’s patronage", E["smith"]),
    ("tiepolo-commission", 478, "Tiepolo", E["tiepolo"]),
    ("important-work", 477, "an important work", C["tiepolo_unrealized_commission"]),
    ("algarotti-diversion", 478, "Algarotti", E["algarotti"]),
    ("dresden-court", 478, "the court of Dresden", E["dresden_court"]),
    ("smith-shift-away-from-history", 478, "history painting and fantasy", E["smith_shift"]),
    ("smith-shift-to-landscapes", 478, "landscapes and architectural paintings", E["smith_shift"]),
    ("visentini-facade-builder", 478, "Visentini", E["visentini"]),
    ("new-marble-facade", 478, "a new classicising marble façade", C["visentini_marble_facade"]),
    ("palace-pronoun-unresolved", 478, "his palace", C["facade_palace_unresolved"], "The possessive’s antecedent is not resolved by this passage."),
    ("smith-patronage-diminished", 478, "his patronage", E["smith"], "Likely refers to Smith in the paragraph context; preserve the pronoun rather than treating identity as independently explicit."),
    ("zuccarelli-england", 478, "Zuccarelli", E["zuccarelli"]),
    ("england-destination", 478, "England", E["england"]),
    ("smith-zais-employment", 478, "Smith", E["smith"]),
    ("zais", 478, "Zais", E["zais"]),
    ("zais-landscapes", 478, "whose landscapes", C["zais_landscapes_smith"]),
    ("picture-batch-sold", 478, "the batch of pictures", E["smith_sale"]),
    ("george-iii", 479, "George III", E["george_iii"]),
    ("smith-drawings-acquired-coreference", 479, "he acquired", E["smith"], "Corefers to Smith; the year is carried forward from the preceding 1752 clause."),
    ("smith-castiglione-carracci-drawings", 479, "some of his most magnificent drawings", C["smith_castiglione_carracci_drawings"]),
    ("castiglione-drawings", 479, "Castiglione", E["castiglione"]),
    ("carracci-drawings", 479, "the Carracci", E["carracci_collective"]),
    ("sagredo-heirs-source", 479, "Zaccaria Sagredo", E["sagredo"], "The heirs are unnamed; this mention identifies only the deceased collection owner."),
    ("sagredo-old-master-pictures", 479, "some old master paintings", C["smith_sagredo_old_masters"]),
    ("smith-canaletto-purchases", 479, "some more pictures", C["smith_canaletto_return_pictures"]),
    ("canaletto-return-pictures-artist", 479, "Canaletto", E["canaletto"]),
    ("english-views", 479, "English views", C["smith_canaletto_return_pictures"]),
    ("canaletto-return-coreference", 479, "that artist’s return", E["canaletto"], "The destination and full syntax continue on p.310."),
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, lo, hi, subject, obj, predicate, claim, qualification, relation=False,
          footnote=None, cross=None, layer="authorial narrative", speaker="Haskell"):
    sid = f"st-chp10-p309-{local}"
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    mentioned = []
    for mention in newm:
        start = int(mention["start_char"])
        line_no = max((n for n, off in line_offsets.items() if off <= start), default=first)
        if lo <= line_no <= hi and mention["candidate_id"] not in mentioned:
            mentioned.append(mention["candidate_id"])
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": PAGE,
                  "pdf_physical_page": PHYSICAL, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
        qualifiers["cross_reference_segments"] = [NOTES]
    if cross:
        qualifiers["cross_reference_segments"] = list(dict.fromkeys(qualifiers.get("cross_reference_segments", []) + cross))
        pages = [310 for item in cross if item == P310]
        if pages:
            qualifiers["cross_reference_printed_pages"] = pages
            qualifiers["cross_reference_source_line_ranges"] = [{"segment_id": P310, "line_start": 481, "line_end": 489}]
    if not mentioned:
        raise SystemExit(f"statement has no anchored mention: {sid}")
    new_s.append({"statement_id": sid, "segment_id": P309, "subject_candidate_id": subject,
                  "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": "\n".join(src[lo - 1:hi]), "source_file": SOURCE_FILE, "origin": "book"})


add_s("five-pictures-after-jones", 469, 470, E["overdoors"], E["jones"],
      "five_of_eleven_pictures_portray_works_by_inigo_jones",
      "Haskell says five of the eleven pictures portray works by Inigo Jones.",
      "The count describes the series of English architectural pictures; do not conflate it with Canaletto’s separate thirteen Door Pieces.",
      relation=True)
add_s("two-pictures-after-burlington", 470, 470, E["overdoors"], E["burlington"],
      "two_of_eleven_pictures_portray_works_by_lord_burlington",
      "Haskell says two pictures portray works by Lord Burlington.",
      "The count is part of the eleven-picture breakdown, not a claim that Burlington painted the pictures.", relation=True)
add_s("two-pictures-after-campbell", 470, 470, E["overdoors"], E["campbell"],
      "two_of_eleven_pictures_portray_works_by_colen_campbell",
      "Haskell says two pictures portray works by Colen Campbell.",
      "The count is part of the eleven-picture breakdown, not a claim that Campbell painted the pictures.", relation=True)
add_s("one-picture-after-morris", 470, 470, E["overdoors"], E["morris"],
      "one_of_eleven_pictures_portrays_a_work_by_roger_morris",
      "Haskell says one picture portrays a work by Roger Morris.",
      "The count is part of the eleven-picture breakdown, not a claim that Morris painted the picture.", relation=True)
add_s("one-picture-after-vanbrugh", 470, 470, E["overdoors"], E["vanbrugh"],
      "one_of_eleven_pictures_portrays_a_work_by_vanbrugh",
      "Haskell says one picture portrays a work by Vanbrugh.",
      "The count is part of the eleven-picture breakdown, not a claim that Vanbrugh painted the picture.", relation=True)
add_s("vanbrugh-example-palladian", 470, 470, E["vanbrugh"], E["overdoors"],
      "chosen_vanbrugh_example_shows_him_at_his_most_palladian",
      "Haskell says the chosen Vanbrugh example shows him at his most Palladian.",
      "This is Haskell’s characterization of the selected example.", relation=False, layer="authorial interpretation")
add_s("capricci-and-smith-taste", 471, 471, E["overdoors"], E["horses_caprice"],
      "overdoor_capricci_omit_canaletto_playful_distortions_and_genre_not_sympathetic_to_smith",
      "Haskell says the overdoor capricci do not include Canaletto’s playful distortions of the Horses of St Mark and judges the genre not inherently sympathetic to Smith.",
      "The absence and aesthetic compatibility are Haskell’s interpretation, not a formal patronage fact.", relation=False, layer="authorial interpretation")
add_s("engravings-from-vitruvius-britannicus", 471, 471, E["overdoors"], C["vitruvius_britannicus"],
      "pictures_based_primarily_on_engravings_from_vitruvius_britannicus",
      "Haskell says the pictures were based primarily on engravings taken from Colen Campbell’s Vitruvius Britannicus, and that their architectural details were mostly highly accurate.",
      "‘Primarily’ and ‘mostly’ are retained; this is not an assertion that every image or detail derives from that book.",
      relation=True, layer="authorial interpretation")
add_s("nogari-portrait-commission", 471, 472, E["smith"], C["nogari_jones_portrait"],
      "nogari_commissioned_to_paint_inigo_jones_portrait_for_smith",
      "Smith commissioned Nogari to paint a portrait of Inigo Jones for him.",
      "The source calls the portrait model ‘Vandyke, with the plan of the Banquetting House in his hands’; do not treat this wording as independently verified attribution.",
      relation=True, footnote=1)
add_s("portrait-model-description", 471, 472, C["nogari_jones_portrait"], E["vandyke"],
      "portrait_described_as_taken_from_vandyke_with_banquetting_house_plan",
      "Haskell says the Nogari portrait was taken from a Vandyke portrait description involving the Banquetting House plan.",
      "The quoted phrase may be a catalogue description; no separate Van Dyck painting is identified or verified here.",
      relation=False, layer="authorial interpretation")
add_s("smith-jones-palladio-editions", 472, 473, E["smith"], C["jones_palladio_editions"],
      "smith_brought_out_many_editions_of_jones_and_palladio_works",
      "Haskell says Smith also brought out many editions of the works of Jones and Palladio.",
      "No titles, precise edition count or dates are supplied in this passage.", relation=True)
add_s("smith-published-gallacini-manuscript", 473, 473, E["smith"], C["gallacini_treatise"],
      "smith_published_a_gallacini_manuscript_in_1767_under_trattato_title",
      "In 1767 Smith published one manuscript in his collection by the seventeenth-century theorist Teofilo Gallacini, titled Trattato sopra gli errori degli architetti.",
      "The OCR joins ‘sopra gli’; the page image separates the words. The cited manuscript and publication are not independently examined here.",
      relation=True)
add_s("visentini-updated-gallacini-book", 473, 474, E["visentini"], C["visentini_gallacini_update"],
      "visentini_soon_updated_gallacini_book_with_attacks_on_baroque_architects_and_successors",
      "Haskell says Visentini soon brought the book up to date with a series of attacks on Baroque architects and their successors down to Piranesi.",
      "The precise date and edition relation to the 1767 publication remain unspecified; retain the polemical description as Haskell’s account.",
      relation=True, layer="authorial interpretation")
add_s("memmo-on-books-and-visentini", 475, 476, E["memmo"], C["neo_palladianism"],
      "memmo_says_architecture_books_and_visentini_guidance_shaped_his_preference_for_pure_simple_style",
      "Haskell quotes Andrea Memmo saying that architecture books he saw in Smith’s palace and Signor Antonio Visentini’s guidance led him to prefer the style called pure and simple.",
      "This is Memmo’s retrospective testimony as quoted by Haskell; do not generalize it to all Venetians.",
      relation=True, footnote=2, layer="nested quotation", speaker="Andrea Memmo as quoted by Haskell")
add_s("smith-neo-palladian-english-taste", 477, 477, E["smith"], C["neo_palladianism"],
      "smiths_1746_strict_neo_palladianism_conformed_to_english_taste_while_fading_in_england",
      "Haskell says Smith’s devotion to strict neo-Palladian canons in 1746 showed close conformity with English taste just as it was weakening in England.",
      "This is Haskell’s interpretive comparison; the style and its reception are not treated as one settled movement.",
      relation=False, layer="authorial interpretation")
add_s("venetian-classicism-and-smith-patronage", 477, 477, E["smith"], C["venetian_classicism"],
      "venetian_classicism_grew_across_artistic_branches_in_1740s_and_smith_patronage_promoted_it",
      "Haskell says a move towards classicism was felt across Venetian art in the 1740s and Smith’s patronage during the decade did much to promote it.",
      "The reach and causal weight are Haskell’s interpretation; retain his broad wording without assigning individual works to the movement.",
      relation=True, layer="authorial interpretation")
add_s("tiepolo-commission-came-to-nothing", 477, 478, E["tiepolo"], C["tiepolo_unrealized_commission"],
      "important_tiepolo_commission_came_to_nothing_after_diversion_to_dresden",
      "Haskell says an important work from Tiepolo came to nothing because Algarotti diverted it for the court of Dresden.",
      "The original commissioner, exact destination inside the court and execution status are not resolved by this passage.",
      relation=False, footnote=3)
add_s("algarotti-diverted-tiepolo-work", 477, 478, E["algarotti"], C["tiepolo_unrealized_commission"],
      "algarotti_expropriated_tiepolo_work_for_dresden_court",
      "Haskell describes Algarotti as expropriating the important Tiepolo work for the court of Dresden.",
      "Preserve Haskell’s strong verb as his account; do not add a commission contract or named work.",
      relation=True, layer="authorial narrative")
add_s("smith-shift-to-sober-landscapes-and-architecture", 478, 478, E["smith"], E["smith_shift"],
      "smith_moved_from_history_painting_and_fantasy_toward_sober_landscapes_and_architecture",
      "Haskell says Smith tended to move away from history painting and fantasy towards landscapes and architectural paintings proclaiming sobriety.",
      "This is a tendency in Haskell’s account, not a claim that Smith ceased all other commissions.",
      relation=False, layer="authorial interpretation")
add_s("visentini-built-marble-facade", 478, 478, E["visentini"], C["visentini_marble_facade"],
      "visentini_built_classicising_marble_facade_in_first_year_of_1750s",
      "Haskell says Visentini built a new classicising marble façade for ‘his palace’ in the first year of the 1750s.",
      "The palace pronoun is unresolved; do not assign the building to Smith or Visentini without further evidence.",
      relation=True, footnote=4)
add_s("facade-palace-referent", 478, 478, C["visentini_marble_facade"], C["facade_palace_unresolved"],
      "marble_facade_belongs_to_unidentified_palace_referred_to_as_his",
      "The façade is described as built for ‘his palace’.",
      "The antecedent is ambiguous; this candidate remains unresolved and distinct from Smith’s named palace.",
      relation=False)
add_s("smith-contemporary-patronage-diminished", 478, 478, E["smith"], E["smith_shift"],
      "smiths_contemporary_artist_patronage_greatly_diminished_by_mid_1750s",
      "Haskell says Smith’s patronage of contemporary artists was greatly diminished by this period.",
      "The antecedent of ‘his’ is inferred from the paragraph’s Smith focus; keep this as a qualified authorial statement.",
      relation=False, layer="authorial interpretation")
add_s("possible-smith-employment-of-zais", 478, 478, E["smith"], E["zais"],
      "smith_may_have_begun_employing_zais_after_zuccarelli_went_to_england_in_1752",
      "After saying Zuccarelli went to England in 1752, Haskell says Smith may therefore have begun employing Zais at about this period.",
      "‘May therefore’ is a hypothesis; neither first contact nor exact start date is established.",
      relation=True, footnote=5, layer="authorial hypothesis")
add_s("zais-landscapes-excluded-from-george-iii-sale", 478, 479, E["smith"], C["zais_landscapes_smith"],
      "smith_did_not_value_zais_landscapes_for_later_george_iii_picture_sale",
      "Haskell says Smith did not think Zais’s landscapes worth including in the batch of pictures later sold to George III.",
      "This reports Haskell’s assessment of Smith’s selection; it does not establish the landscapes’ later whereabouts.",
      relation=False)
add_s("smith-acquired-castiglione-carracci-drawings", 479, 479, E["smith"], C["smith_castiglione_carracci_drawings"],
      "smith_acquired_drawings_including_many_by_castiglione_and_carracci_in_1752",
      "In the same year, Haskell says Smith acquired some of his most magnificent drawings, including many by Castiglione and the Carracci.",
      "‘The same year’ follows Zuccarelli’s 1752 departure; no drawing titles or exact count are given.",
      relation=True)
add_s("smith-acquired-sagredo-old-masters", 479, 479, E["smith"], C["smith_sagredo_old_masters"],
      "smith_acquired_old_master_paintings_from_sagredo_heirs_in_1752",
      "Haskell says Smith acquired old-master paintings from the heirs of Zaccaria Sagredo in the same year.",
      "The heirs are unnamed and the paintings are not identified; the year is carried from the preceding 1752 clause.",
      relation=True, footnote=6)
add_s("smith-bought-more-canaletto-views", 479, 479, E["smith"], C["smith_canaletto_return_pictures"],
      "smith_bought_more_canaletto_pictures_including_english_views_on_artist_return",
      "Haskell says Smith bought more pictures from Canaletto, including a number of English views, on the artist’s return.",
      "The sentence continues on p.310; do not yet specify the artist’s return destination or complete the temporal relation.",
      relation=True, cross=[P310])

all_ids = cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < first or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside p.309: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if any(cid not in all_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"missing mention candidate in {row['statement_id']}")

spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

# Close the p.308 sentence with p.309 L469 while keeping footnotes pending.
p308_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p308-english-overdoor-architecture"), None)
if not p308_statement:
    raise SystemExit("p.308 architectural-style statement missing")
p308_statement["qualifiers"]["claim"] = (
    "Haskell says the architecture was exclusively English, showing country houses and surroundings neither "
    "Visentini nor Smith had seen, in the style Lord Burlington and his followers had raised into a dogmatic "
    "canon of taste—the Palladian."
)
p308_statement["qualifiers"]["qualification"] = (
    "The sentence closes on p.309 L469 with ‘taste—the Palladian’; the full cross-page wording is recorded "
    "in the linked source line. The page’s footnotes remain pending in the consolidated notes segment."
)
p308_statement["qualifiers"]["cross_reference_source_line_ranges"] = [
    {"segment_id": P309, "line_start": 469, "line_end": 469}
]
neo_id = C["neo_palladianism"]
if neo_id not in p308_statement["qualifiers"]["mentioned_candidate_ids"]:
    p308_statement["qualifiers"]["mentioned_candidate_ids"].append(neo_id)
cov[P308]["note"] = cov[P308]["note"].replace(
    "The next sentence continues on p.309, so p.308 remains partial.",
    "The cross-page sentence is closed by p.309 L469; p.308 remains partial because footnotes 1–3 await the consolidated notes segment."
)

cov[P309].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L469-479",
    "note": "Printed p.309 body checked against CHP-10.pdf physical page 38. Closed p.308’s English architectural-style sentence at L469. Recorded the eleven-picture distribution among works by Inigo Jones, Burlington, Campbell, Morris and Vanbrugh; distinguished the Smith overdoor pictures from Canaletto’s playful Horses of St Mark caprice; recorded Campbell’s Vitruvius Britannicus as the principal engraving source, Nogari’s Inigo Jones portrait, Smith’s editions and Gallacini publication, Visentini’s update and Memmo’s quoted preference for the pure-and-simple style. Preserved Haskell’s interpretation of Smith’s neo-Palladian taste and Venetian classicism; kept the Tiepolo commission’s diversion, the 1751 façade and its ambiguous palace pronoun, Zais employment/value, and the 1752 Castiglione/Carracci drawings and Sagredo paintings at their stated certainty. The later Canaletto-purchase sentence continues on p.310. Footnotes 1–6 remain pending in the consolidated notes source. Page-image review records OCR ‘TeoFilo’ as printed ‘Teofilo’ and ‘sopragli’ as ‘sopra gli’; S0 is unchanged."})

summary = {"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": P309, "segment_sha256": digest, "new_candidates": len(newc),
           "candidate_ids": [row["candidate_id"] for row in newc],
           "new_mentions": len(newm), "new_statements": len(new_s),
           "closed_cross_page_segment": P308,
           "coverage": {"p308": cov[P308]["migration_status"], "p309": cov[P309]["migration_status"],
                        "p310": cov[P310]["migration_status"]}}
print(json.dumps(summary, ensure_ascii=True, indent=2))
if sys.argv[-1:] == ["--apply"]:
    for path in (cp, mp, sp, vp):
        backup = Path(str(path) + BACKUP)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path, backup)
    write_csv(cp, cf, candidates + newc)
    write_csv(mp, mf, mentions + newm)
    write_jsonl(sp, statements + new_s)
    write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
    print("Applied p.309 S2 body migration; notes 1–6 remain in the consolidated notes segment.")
