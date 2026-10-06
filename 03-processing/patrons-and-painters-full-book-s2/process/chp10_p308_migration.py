"""Controlled S2 migration for printed p.308; dry-run unless --apply."""
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
P307 = "chp-10:10_CHP-10_intro:l445-454"
P308 = "chp-10:10_CHP-10_intro:l456-466"
P309 = "chp-10:10_CHP-10_intro:l468-479"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "64cd99d39303a5fd6feebb08c5dd19b6bdbe48df72d80357b3c5995c30494964"
BACKUP = ".bak-s2-chp10-p308-20261002"


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
first, last, PAGE, PHYSICAL = 456, 466, 308, 37
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[455].strip() != "[Page 308]" or "thirty-one etchings" not in body:
    raise SystemExit(f"p.308 source segment mismatch: {digest}")
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
if maximum != 9242:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P307, ("reviewed", "partial")), (P308, ("queued", "pending")),
                      (P309, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P308 for row in mentions) or any(row["segment_id"] == P308 for row in statements):
    raise SystemExit("p.308 already has mention or statement rows")

E = {
    "canaletto": "cand-0514", "smith": "cand-2440", "palladio": "cand-1807",
    "venice": "cand-2719", "rome": "cand-4490", "algarotti": "cand-0041",
    "pannini": "cand-1827", "visentini": "cand-2785", "zuccarelli": "cand-2883",
    "zuccarelli_landscapes_index": "cand-2882", "lord_burlington": "cand-0470",
    "horses_index": "cand-0506", "rialto": "cand-9206", "anthony_blunt": "cand-0379",
    "england": "cand-8983", "padua": "cand-3944",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("canaletto_rialto_view", "Canaletto’s view of the Rialto as planned by Palladio", "work",
     "Haskell contrasts this almost mathematically precise view with the imaginary scenes in the architectural series; no individual title is supplied.", 459),
    ("carita_courtyard", "Courtyard of the Carità (site identity unresolved)", "place",
     "Named as the subject of a Canaletto view; retain the OCR accent correction and do not conflate it with another Carità reference without S3 evidence.", 460),
    ("canaletto_horses_caprice", "Canaletto’s imagined scene of the Horses of St Mark detached from the church and placed in the piazza", "work",
     "A caprice described by Haskell; keep it distinct from the physical Horses and from other Canaletto works until aligned.", 460),
    ("scala_giganti", "Scala dei Giganti (architectural referent named by Haskell)", "place",
     "Haskell refers to a fantastic interpretation of this structure; its specific site identity is not resolved in this passage.", 461),
    ("canaletto_scala_caprice", "Canaletto’s fantastic interpretation of the Scala dei Giganti", "work",
     "One of the imaginary Venetian scenes described among Canaletto’s early caprices; no catalogue title or inventory is provided.", 461),
    ("canaletto_early_caprices", "Canaletto’s early caprices in the p.308 architectural series", "term",
     "Haskell calls the imagined Horses of St Mark and Scala dei Giganti scenes among Canaletto’s first caprices; proposed influences remain competing hypotheses.", 461),
    ("canaletto_roman_capricci", "Two capricci with Roman ruins painted by Canaletto for Joseph Smith", "work",
     "Haskell says they were painted about this time in a ‘bold frank manner’; footnote 2 says their imaginary settings appear inspired by Padua, pending the consolidated notes read.", 461),
    ("canaletto_31_etchings", "Canaletto’s series of thirty-one etchings ‘altre prese da i Luoghi altre ideate’ (Plate 55a)", "work",
     "A distinct etching series dedicated to Smith, separate from the paintings; the Italian phrase is retained as printed.", 462),
    ("smith_palladian_overdoors", "Joseph Smith’s series of overdoors illustrating Palladian architecture, continued after Canaletto’s departure", "work",
     "The larger series includes Canaletto’s 13 Door Pieces and later work by Visentini and Zuccarelli; keep those contributions and their dates distinct.", 464),
    ("zuccarelli_rebecca_landscapes", "Zuccarelli’s six landscapes representing Rebecca, Jacob and Esau", "work",
     "Haskell says it is unclear whether they were painted before 1746 or whether that year’s commission brought the first contact with Smith.", 464),
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
                 "candidate_source_ref": f"{P308}#L{line}"})

newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p308-{local}"
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
    newm.append({"mention_id": mid, "segment_id": P308, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    ("palladio-title-close", 457, "Palladio", E["palladio"]),
    ("smith-catalogue-note", 457, "Smith", E["smith"]),
    ("canaletto-series-reference", 457, "the pictures in the series", "cand-9239"),
    ("palladio-architect-coreference", 457, "that architect", E["palladio"], "Corefers to Palladio."),
    ("canaletto-series-aim", 457, "the aim of the group", "cand-9239"),
    ("most-admired-buildings", 458, "most admired Buildings at Venice", "cand-9239"),
    ("canaletto-rialto-view", 459, "views of the Rialto", C["canaletto_rialto_view"]),
    ("palladio-rialto-plan", 460, "Palladio", E["palladio"]),
    ("carita-courtyard", 460, "the Courtyard of the Carita", C["carita_courtyard"], "S0 OCR omits the accent; the printed page reads Carità."),
    ("horses-caprice-start", 460, "Horses of", C["canaletto_horses_caprice"], "The page break in the source OCR divides this phrase from ‘St Mark’s’ on the next line."),
    ("horses-caprice-end", 461, "St Mark’s", C["canaletto_horses_caprice"], "Completes the p.460 phrase ‘Horses of’."),
    ("scala-place", 461, "Scala dei Giganti", C["scala_giganti"]),
    ("scala-caprice", 461, "fantastic interpretation", C["canaletto_scala_caprice"]),
    ("early-caprices", 461, "the first ‘caprices’", C["canaletto_early_caprices"]),
    ("canaletto-caprice-author", 461, "Canaletto", E["canaletto"]),
    ("venice-algarotti-arrival", 461, "Venice in 1743", E["venice"]),
    ("algarotti-arrival", 461, "Francesco Algarotti", E["algarotti"]),
    ("smith-contact-algarotti", 461, "with Smith", E["smith"]),
    ("canaletto-pannini-idea", 461, "Canaletto", E["canaletto"], "Second Canaletto mention in this line.", 1),
    ("pannini", 461, "Pannini", E["pannini"]),
    ("pannini-rome-visit", 461, "Rome", E["rome"]),
    ("two-roman-capricci", 461, "two capricci with Roman ruins", C["canaletto_roman_capricci"]),
    ("smith-roman-capricci", 461, "for Smith", E["smith"]),
    ("algarotti-fanciful", 461, "the fanciful Algarotti", E["algarotti"]),
    ("smith-phlegmatic", 461, "temperament of Smith", E["smith"]),
    ("smith-english-patron", 461, "his English patron", E["smith"]),
    ("canaletto-etching-series", 462, "Canaletto", E["canaletto"]),
    ("thirty-one-etchings", 462, "the series of thirty-one etchings", C["canaletto_31_etchings"]),
    ("etchings-italian-title", 462, "altre prese da i Luoghi altre ideate", C["canaletto_31_etchings"]),
    ("smith-consul-paintings", 462, "for the Consul", E["smith"]),
    ("canaletto-departure", 462, "he left for", E["canaletto"], "Corefers to Canaletto; the phrase begins on this line and continues on p.308 line 463."),
    ("england-destination", 463, "England", E["england"]),
    ("smith-recommendation", 463, "Smith’s recommendation", E["smith"]),
    ("canaletto-departure-context", 464, "Canaletto’s departure in 1746", E["canaletto"]),
    ("smith-overdoors", 464, "Smith turned", E["smith"]),
    ("overdoor-series", 464, "the series of overdoors illustrating Palladian architecture", C["smith_palladian_overdoors"]),
    ("visentini", 464, "Antonio Visentini", E["visentini"]),
    ("smith-employed-visentini", 464, "employed by him", E["smith"], "Corefers to Joseph Smith."),
    ("zuccarelli", 464, "Francesco Zuccarelli", E["zuccarelli"]),
    ("rebecca-landscapes", 464, "6 Landscapes representing the story of Rebecca with Jacob and Esau", C["zuccarelli_rebecca_landscapes"]),
    ("zuccarelli-worked-for-smith", 464, "for Smith", E["smith"]),
    ("zuccarelli-enterprise", 464, "Zuccarelli", E["zuccarelli"], "Repeated surname; identifies Zuccarelli’s minor part in the enterprise.", 1),
    ("visentini-architecture", 465, "Visentini", E["visentini"]),
    ("english-country-houses", 465, "exclusively English", E["england"]),
    ("burlington", 465, "Lord Burlington", E["lord_burlington"]),
    ("burlington-followers", 465, "his followers", E["lord_burlington"], "Corefers to Lord Burlington."),
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, lo, hi, subject, obj, predicate, claim, qualification, relation=False,
          footnote=None, cross=None, layer="authorial narrative", speaker="Haskell"):
    sid = f"st-chp10-p308-{local}"
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
        page_map = {P307: 307, P309: 309}
        pages = [page_map[item] for item in cross if item in page_map]
        if pages:
            qualifiers["cross_reference_printed_pages"] = pages
    new_s.append({"statement_id": sid, "segment_id": P308, "subject_candidate_id": subject,
                  "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": "\n".join(src[lo - 1:hi]), "source_file": SOURCE_FILE, "origin": "book"})


add_s("door-series-aim-and-membership", 457, 458, E["smith"], "cand-9239",
      "aimed_to_show_most_admired_venetian_buildings_but_not_all_were_palladios",
      "Smith’s catalogue note acknowledges that not all pictures in the Canaletto series represent Palladio’s works; Haskell says its stated aim was to show the most admired buildings at Venice, most of which were by sixteenth-century Palladian architects.",
      "Preserve the distinction between the series’ aim and the attribution of every building; ‘vast majority’ does not mean all.",
      layer="authorial narrative")
add_s("door-series-contrasting-scenes", 458, 461, "cand-9239", C["canaletto_early_caprices"],
      "series_combined_precise_palladian_views_and_imaginary_scenes",
      "Haskell contrasts almost mathematically precise Rialto and Carità courtyard views with imaginary scenes of the Horses of St Mark detached into the piazza and the Scala dei Giganti interpreted fantastically; he says the series is not altogether consistent.",
      "The named buildings and scenes are retained as distinct referents and the descriptions remain Haskell’s characterization.",
      relation=False, layer="authorial interpretation")
add_s("possible-algarotti-link", 461, 461, C["canaletto_early_caprices"], E["algarotti"],
      "tempting_but_unproven_link_to_algarottis_1743_arrival",
      "Haskell says it is tempting to link the early caprices with Francesco Algarotti’s arrival in Venice in 1743, given his later enthusiasm for this picture type and his contact with Smith at the time.",
      "This is a proposed connection, not a demonstrated source of Canaletto’s idea; Haskell immediately gives an alternative explanation.",
      relation=True, layer="authorial hypothesis")
add_s("possible-pannini-source", 461, 461, C["canaletto_early_caprices"], E["pannini"],
      "equally_possible_derivation_from_pannini_after_rome_visit",
      "Haskell says it is equally possible that Canaletto derived the caprice idea from Pannini during a Rome visit a year or two earlier.",
      "Competing with the possible Algarotti link; neither source is resolved here.",
      relation=True, layer="authorial hypothesis")
add_s("two-roman-capricci-for-smith", 461, 461, E["canaletto"], C["canaletto_roman_capricci"],
      "painted_two_roman_ruin_capricci_for_smith_about_this_time",
      "Haskell says Canaletto certainly painted two capricci with Roman ruins for Smith about this time, in a ‘bold frank manner’.",
      "The timing is approximate (‘about now’); footnote 2 remains pending in the consolidated notes segment.",
      relation=True, footnote=2)
add_s("algarotti-smith-comparison", 461, 461, E["algarotti"], E["smith"],
      "caprices_more_readily_associated_with_algarotti_than_smith",
      "Haskell says the capricci are more readily associated with Algarotti’s fanciful temperament than Smith’s more phlegmatic one, while stating that Canaletto dedicated his poetic imaginative excursions to his English patron.",
      "This is Haskell’s comparison of temperaments and patronage context, not proof Algarotti commissioned the Roman capricci.",
      relation=False, layer="authorial interpretation")
add_s("etchings-dedicated-to-smith", 462, 462, E["canaletto"], C["canaletto_31_etchings"],
      "dedicated_thirty_one_etchings_to_smith",
      "Canaletto dedicated to Smith a series of thirty-one etchings titled ‘altre prese da i Luoghi altre ideate’ (Plate 55a).",
      "Keep this etching series distinct from the paintings made for Smith.", relation=True)
add_s("etchings-show-absent-artistic-side", 462, 462, E["canaletto"], C["canaletto_31_etchings"],
      "etchings_presented_imaginative_side_absent_from_smith_paintings",
      "Haskell says the etchings show a side of Canaletto’s art absent from his paintings for Smith but occasionally hinted at in drawings: distances, plant-covered worn columns, a solitary black bird, arches and mountains.",
      "The descriptive features and absence/presence comparison are Haskell’s interpretive reading.",
      relation=False, layer="authorial interpretation")
add_s("poetic-etching-vision", 462, 462, E["canaletto"], C["canaletto_31_etchings"],
      "described_as_deep_informal_and_often_poignant_vision",
      "Haskell describes this etching vision as deeply felt, informal and often poignant, and says Canaletto’s genius blazes at full power almost for the last time.",
      "These are the author’s aesthetic judgments.", relation=False, layer="authorial interpretation")
add_s("canaletto-left-for-england", 463, 463, E["canaletto"], E["england"],
      "apparently_left_for_england_on_smiths_recommendation",
      "Very soon afterwards Canaletto left for England, apparently on Smith’s recommendation; Haskell says there was little contact between the two for nearly ten years.",
      "The recommendation is explicitly qualified as apparent; the length of reduced contact is approximate.",
      relation=True, layer="authorial narrative")
add_s("smith-continued-overdoor-series", 464, 464, E["smith"], C["smith_palladian_overdoors"],
      "after_1746_turn_to_visentini_and_zuccarelli_to_continue_overdoors",
      "After Canaletto’s departure in 1746, Smith turned to Visentini and Zuccarelli to continue the series of overdoors illustrating Palladian architecture.",
      "The larger series includes but is not identical to Canaletto’s thirteen Door Pieces; preserve the different artists’ contributions.",
      relation=True, footnote=3)
add_s("visentini-long-employment", 464, 464, E["smith"], E["visentini"],
      "employed_visentini_for_more_than_fifteen_years_as_architect_and_book_illustrator",
      "Haskell says Smith had employed Antonio Visentini for more than fifteen years as an architect and book illustrator by this point.",
      "The duration is the book’s rounded account.", relation=True)
add_s("zuccarelli-employment-and-landscape-series", 464, 464, E["zuccarelli"], E["smith"],
      "established_landscape_painter_worked_often_for_smith_but_six_landscape_dates_uncertain",
      "Francesco Zuccarelli was an established landscape painter who worked greatly for Smith; Haskell is unsure whether his six Rebecca/Jacob/Esau landscapes and other pictures predated 1746 or whether that commission initiated contact.",
      "Do not date the six-landscape series or assert first contact; either sequence remains possible.",
      relation=True)
add_s("zuccarelli-role-in-overdoors", 464, 465, E["zuccarelli"], E["visentini"],
      "added_decorative_venetian_landscapes_to_visentinis_architectural_views",
      "Haskell says Zuccarelli’s part in the overdoor enterprise was minor despite its greater artistic quality: he added decorative Venetian landscapes to Visentini’s architectural views.",
      "The relative artistic-quality judgment belongs to Haskell; do not transfer Visentini’s architecture to Zuccarelli.",
      relation=True, layer="authorial interpretation")
add_s("english-overdoor-architecture", 465, 465, C["smith_palladian_overdoors"], E["lord_burlington"],
      "english_country_houses_in_style_burlington_followers_made_palladian_canon",
      "Haskell says the architecture was exclusively English, showing country houses and surroundings neither Visentini nor Smith had seen, in the style Lord Burlington and his followers had raised into a dogmatic canon.",
      "The sentence continues on p.309 with the word ‘taste’; preserve that continuation before finalizing its full syntax.",
      relation=False, cross=[P309], layer="authorial interpretation")
all_ids = cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < first or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside p.308: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if not q["mentioned_candidate_ids"]:
        raise SystemExit(f"statement has no anchored mention: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

# Close the sentence begun on p.307; footnotes remain for the consolidated notes pass.
p307_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p307-next-commissioned-series-aim"), None)
p307_candidate = next((row for row in candidates if row["candidate_id"] == "cand-9239"), None)
p307_mention = next((row for row in mentions if row["mention_id"] == "m-chp10-p307-thirteen-door-pieces"), None)
if not p307_statement or not p307_candidate or not p307_mention:
    raise SystemExit("p.307 Door Pieces rows changed; cannot close cross-page reference")
p307_statement["qualifiers"]["qualification"] = (
    "The p.308 continuation completes the phrase as principal Buildings of Palladio. "
    "The associated footnotes remain pending for the consolidated notes pass."
)
p307_candidate["canonical_name"] = "Canaletto’s 1744 series of 13 Door Pieces of the principal Buildings of Palladio"
p307_candidate["detail"] = (
    "The p.307–308 text names Canaletto’s 1744 13 Door Pieces of the principal Buildings of Palladio; "
    "Haskell says the larger series aimed to show Venice’s most admired buildings and that not all represented Palladio. "
    "The page footnotes remain to be processed from the consolidated notes source."
)
p307_mention["note"] = "p.308 L457 completes the phrase as ‘of Palladio’; associated page footnotes remain pending in the consolidated notes source."
cov[P307]["note"] = cov[P307]["note"].replace(
    "The last sentence continues on p.308, so this page remains partial.",
    "The final sentence is closed by p.308 L457 as ‘of Palladio’; p.307 remains partial because its footnotes 1–4 await the consolidated notes segment."
)
cov[P308].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L457-465",
    "note": "Printed p.308 body checked against CHP-10.pdf physical page 37. Closed p.307’s 1744 13 Door Pieces sentence and recorded Smith’s catalogue qualification that not all represented Palladio, the aim of showing Venice’s most admired buildings, and the majority’s sixteenth-century Palladian designers; contrasted precise Rialto/Carità views with the imaginary Horses of St Mark and Scala dei Giganti scenes; preserved competing possible links to Algarotti’s 1743 arrival or Pannini’s Rome visit; recorded two Roman-ruin capricci for Smith, the separate thirty-one-etching series dedicated to him, Canaletto’s qualified departure for England on Smith’s recommendation, their nearly ten-year lapse in contact, and Smith’s post-1746 continuation of the overdoor series through Visentini and Zuccarelli. The six Rebecca/Jacob/Esau landscapes remain uncertain in date and first-contact status; Zuccarelli’s role and the English architectural series are preserved with Haskell’s qualifications. Footnotes 1–3 remain pending in the consolidated notes segment, including the p.308 line 466 continuation of note 1. Page-image checks correct S0 OCR ‘Carita’ to printed ‘Carità’ and ‘Canaletto’s’work’ to ‘Canaletto’s work’, without changing S0. The next sentence continues on p.309, so p.308 remains partial."})

summary = {"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": P308, "segment_sha256": digest, "new_candidates": len(newc),
           "candidate_ids": [row["candidate_id"] for row in newc],
           "new_mentions": len(newm), "new_statements": len(new_s),
           "closed_cross_page_segment": P307,
           "coverage": {"p307": cov[P307]["migration_status"], "p308": cov[P308]["migration_status"],
                        "p309": cov[P309]["migration_status"]}}
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
    print("Applied p.308 S2 body migration; footnotes 1–3 remain with the consolidated notes segment.")
