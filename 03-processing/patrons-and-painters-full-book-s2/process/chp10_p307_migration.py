"""Controlled S2 migration for printed p.307; dry-run unless --apply."""
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
P306 = "chp-10:10_CHP-10_intro:l435-443"
P307 = "chp-10:10_CHP-10_intro:l445-454"
P308 = "chp-10:10_CHP-10_intro:l456-466"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "4941112223789a8e74bbf03bc5c027206d44d3f9ad78bbbd28c1f27666185f23"
BACKUP = ".bak-s2-chp10-p307-20261002"


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
first, last, PAGE, PHYSICAL = 445, 454, 307, 36
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[444].strip() != "[Page 307]" or "Priapus" not in body:
    raise SystemExit(f"p.307 source segment mismatch: {digest}")
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
if maximum != 9230:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P306, ("reviewed", "partial")), (P307, ("queued", "pending")),
                      (P308, ("queued", "pending")), (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P307 for row in mentions) or any(row["segment_id"] == P307 for row in statements):
    raise SystemExit("p.307 already has mention or statement rows")

E = {
    "smith": "cand-2440", "canaletto": "cand-0514", "pellegrini": "cand-1862",
    "elector": "cand-0148", "vermeer": "cand-2753", "mieris": "cand-1663",
    "breval": "cand-0451", "pannini": "cand-1827", "cignani_cartoons": "cand-9191",
    "rome": "cand-4490", "venice": "cand-2719", "neoclassicism": "cand-3995",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("elector_sale_paintings", "Unidentified group of paintings Joseph Smith sold to the Elector of Saxony in 1741", "work",
     "Haskell says Smith sold a number of paintings to the Elector of Saxony in 1741; the works are now impossible to identify.", 447),
    ("dutch_flemish_collection", "Joseph Smith’s collection of Dutch and Flemish pictures bought from Pellegrini’s widow", "",
     "An unnamed collection bought in 1741 or thereabouts; the individual pictures and the widow’s identity are not supplied here.", 447),
    ("pellegrini_widow", "Unnamed widow of the artist Pellegrini (personal identity unresolved)", "person",
     "Haskell identifies this woman only as the widow of the artist Pellegrini; do not infer her personal name or resolve the candidate identity here.", 447),
    ("vermeer_virginals", "Vermeer’s Lady at the Virginals", "work",
     "Haskell says the painting was then at Buckingham Palace and attributes it at that time to Frans van Mieris; its acquisition from Pellegrini’s widow is stated as almost certain, then treated conditionally.", 448),
    ("austrian_succession_war", "War of the Austrian Succession", "event",
     "The outbreak in 1740 is given as context for a reduction in English tourists and Canaletto’s renewed work for Smith.", 450),
    ("english_tourists_1740s", "English tourists whose numbers fell after the 1740 outbreak of war", "term",
     "An unnamed visitor group; Haskell says their numbers were cut down, without quantifying the decline.", 450),
    ("canaletto_early_venetian_views", "Canaletto’s earlier small-scale views of Venice", "work",
     "A broad body of earlier Venetian views associated with Canaletto’s international reputation; no fixed inventory is given.", 451),
    ("canaletto_roman_views", "Six views of ancient Roman monuments painted by Canaletto for Joseph Smith", "work",
     "Haskell links the group to a quite possible second visit to Rome, perhaps with Smith; titles are not supplied in this passage.", 452),
    ("canaletto_door_pieces", "Canaletto’s 1744 series of 13 Door Pieces (description continues on p.308)", "work",
     "The p.307 sentence begins the title and purpose of this commissioned group but breaks before completing the phrase ‘principal Buildings’; retain the continuation link to p.308.", 454),
    ("buckingham_palace", "Buckingham Palace", "place",
     "Named on p.307 as the painting’s then location; the sentence does not specify a room or collection inventory.", 448),
    ("breval_conventional_sculptures", "Unspecified conventional sculptures shown to John Breval in Joseph Smith’s collection", "work",
     "The sculptures are listed after the statuette but are not individually identified.", 446),
    ("smith_contemporary_artists", "Unnamed contemporary artists whose patronage Joseph Smith resumed in the early 1740s", "term",
     "The passage gives no names or number for the artists; retain them as an unnamed collective endpoint.", 447),
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
                 "candidate_source_ref": f"{P307}#L{line}"})

newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p307-{local}"
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
    newm.append({"mention_id": mid, "segment_id": P307, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    ("priapus", 446, "Priapus", "cand-9230", "Continuation of Breval’s p.306 statuette quotation; identity remains unresolved."),
    ("conventional-sculptures", 446, "more conventional sculptures", C["breval_conventional_sculptures"]),
    ("cignani-cartoons", 446, "the Cignani cartoons", E["cignani_cartoons"]),
    ("smith-resumed-patronage", 447, "he resumed the patronage", E["smith"], "Corefers to Joseph Smith."),
    ("contemporary-artists", 447, "contemporary artists", C["smith_contemporary_artists"]),
    ("smith-sold-paintings", 447, "he sold", E["smith"], "Corefers to Joseph Smith."),
    ("sale-painting-group", 447, "a number of paintings", C["elector_sale_paintings"]),
    ("elector-of-saxony", 447, "the Elector of Saxony", E["elector"], "Candidate mapping is suggested by the Augustus III index entry covering p.307; identity remains for S3."),
    ("smith-bought-collection", 447, "he bought", E["smith"], "Corefers to Joseph Smith."),
    ("dutch-flemish-pictures", 447, "a collection of Dutch and Flemish pictures", C["dutch_flemish_collection"]),
    ("pellegrini-widow", 447, "widow", C["pellegrini_widow"], "Unnamed woman; do not infer a personal name."),
    ("pellegrini", 447, "Pellegrini", E["pellegrini"], "S1 index candidate for Giovanni Antonio Pellegrini covers p.307; global identity mapping remains for S3."),
    ("widow-later-reference", 447, "her", C["pellegrini_widow"], "Corefers to Pellegrini’s unnamed widow."),
    ("smith-acquired-vermeer", 447, "he acquired", E["smith"], "Corefers to Joseph Smith."),
    ("vermeer-person", 447, "Vermeer", E["vermeer"], "S1 index entry with subentry ‘Lady at the Virginals’ covers p.307; person alignment remains for S3."),
    ("lady-at-virginals", 448, "Lady at the Virginals", C["vermeer_virginals"]),
    ("buckingham-palace", 448, "Buckingham Palace", C["buckingham_palace"]),
    ("vermeer-painting-ocr", 448, "Wermeer", C["vermeer_virginals"], "S0 reads ‘theWermeer’; the printed page reads ‘the Vermeer’. Preserve the S0 span and record the correction in S2."),
    ("canaletto-development", 448, "Canaletto", E["canaletto"]),
    ("canaletto-style-time", 448, "Canaletto", E["canaletto"], "", 1),
    ("van-mieris-attribution", 448, "Frans van Mieris", E["mieris"], "The painting was attributed to him at the time; this is not asserted as its true authorship."),
    ("vermeer-picture-reference", 448, "this picture", C["vermeer_virginals"], "Corefers to Lady at the Virginals."),
    ("war-austrian-succession", 450, "Austrian succession", C["austrian_succession_war"]),
    ("english-tourists", 450, "English tourists", C["english_tourists_1740s"]),
    ("canaletto-return-to-work", 450, "he once again began to work", E["canaletto"], "Corefers to Canaletto."),
    ("smith-persistent-patron", 450, "his most persistent patron", E["smith"], "Identified as Smith by the immediately following sentence on the same page."),
    ("canaletto-return", 451, "Canaletto", E["canaletto"]),
    ("smith-return", 451, "Smith", E["smith"]),
    ("small-venetian-views", 451, "the small-scale views of Venice", C["canaletto_early_venetian_views"]),
    ("rome-visit", 452, "Rome", E["rome"]),
    ("smith-possible-rome-visit", 452, "with Smith", E["smith"], "The text says ‘perhaps with Smith’; his participation is not certain."),
    ("six-roman-monument-views", 452, "six views of ancient Roman monuments", C["canaletto_roman_views"]),
    ("canaletto-roman-views-painted", 452, "Canaletto", E["canaletto"]),
    ("roman-views-for-smith", 452, "for Smith", E["smith"]),
    ("rome-values", 452, "Rome", E["rome"], "Reference to the city in Haskell’s Roman-values interpretation.", 1),
    ("venice-uniqueness", 452, "Venice", E["venice"]),
    ("venetian-views-style", 452, "Venetian views", C["canaletto_early_venetian_views"]),
    ("smith-antiquity-preference", 452, "Smith should have wished", E["smith"]),
    ("pannini", 452, "Pannini", E["pannini"]),
    ("neo-classic", 452, "neo-classic", E["neoclassicism"], "Haskell questions whether the pictures play more than a symbolic role; do not convert this into a settled influence claim."),
    ("smith-commission-context", 453, "Smith particularly liked", E["smith"]),
    ("next-commissioned-paintings", 453, "the next few paintings", C["canaletto_door_pieces"], "Series identification is provisional until p.308 completes the sentence."),
    ("thirteen-door-pieces", 454, "13 Door Pieces", C["canaletto_door_pieces"]),
    ("canaletto-door-pieces-author", 454, "Canaletto", E["canaletto"]),
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, lo, hi, subject, obj, predicate, claim, qualification, relation=False,
          footnote=None, cross=None, layer="authorial narrative", speaker="Haskell"):
    sid = f"st-chp10-p307-{local}"
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
        page_map = {P306: 306, P308: 308}
        pages = [page_map[item] for item in cross if item in page_map]
        if pages:
            qualifiers["cross_reference_printed_pages"] = pages
    new_s.append({"statement_id": sid, "segment_id": P307, "subject_candidate_id": subject,
                  "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": "\n".join(src[lo - 1:hi]), "source_file": SOURCE_FILE, "origin": "book"})


add_s("breval-statuette-continuation", 446, 446, E["breval"], "cand-9230",
      "reported_statuette_continues_as_priapus",
      "The continuation of John Breval’s reported visit says the statuette was a Priapus with a grotesquely large pudendum, then lists other sculptures, Cignani cartoons, books and antiquities.",
      "The p.306 quotation had called the same statuette seemingly an Aesculapius; the book’s differing labels are retained without resolving the object’s identity.",
      relation=True, footnote=1, cross=[P306], layer="reported observation")
add_s("smith-resumed-contemporary-patronage", 447, 447, E["smith"], C["smith_contemporary_artists"],
      "resumed_patronage_of_contemporary_artists_in_early_1740s",
      "Haskell says Smith resumed large-scale patronage of contemporary artists early in the 1740s.",
      "The passage gives a decade-level time phrase, not an exact year.", relation=True)
add_s("smith-sale-to-elector", 447, 447, E["smith"], C["elector_sale_paintings"],
      "sold_unidentified_paintings_to_elector_of_saxony_in_1741",
      "In 1741 Smith sold an unidentified number of paintings to the Elector of Saxony; Haskell says the paintings can no longer be identified.",
      "The Elector is mapped provisionally to the Augustus III index candidate whose page range includes p.307; identity is deferred to S3.",
      relation=True, footnote=2, layer="authorial narrative")
add_s("smith-bought-dutch-flemish-collection", 447, 447, E["smith"], C["dutch_flemish_collection"],
      "bought_dutch_and_flemish_picture_collection_from_pellegrinis_widow",
      "In the same year or thereabouts Smith bought a collection of Dutch and Flemish pictures from the widow of the artist Pellegrini.",
      "The date is approximate; the widow is unnamed and the pictures are not itemized.",
      relation=True, footnote=3)
add_s("pellegrini-widow-identity", 447, 447, C["pellegrini_widow"], E["pellegrini"],
      "identified_only_as_widow_of_pellegrini",
      "The seller is described only as the widow of the artist Pellegrini.",
      "Do not infer her name or additional biographical details from this passage.", relation=True, footnote=3)
add_s("smith-acquired-vermeer", 447, 449, E["smith"], C["vermeer_virginals"],
      "almost_certainly_acquired_vermeer_painting_from_pellegrinis_widow",
      "Haskell says Smith almost certainly acquired at least one Dutch-painting masterpiece, Vermeer’s Lady at the Virginals, from Pellegrini’s widow.",
      "The next sentence makes the provenance conditional (‘if this picture ... really came from Pellegrini’s widow’); retain the claim as strongly probable but not established.",
      relation=True, footnote=3, layer="authorial inference")
add_s("vermeer-attribution-to-mieris", 448, 448, C["vermeer_virginals"], E["mieris"],
      "attributed_to_frans_van_mieris_at_the_time",
      "At the time discussed, Lady at the Virginals was attributed to the secondary painter Frans van Mieris.",
      "This records a historical attribution, not the work’s accepted authorship.", relation=True)
add_s("claimed-vermeer-influence", 448, 448, C["vermeer_virginals"], E["canaletto"],
      "claimed_influence_on_canalettos_development",
      "It had been claimed that the Vermeer painting greatly influenced Canaletto’s development.",
      "Haskell calls the theory tempting but difficult to substantiate; the influence is not affirmed as fact.",
      relation=True, footnote=4, layer="reported scholarly claim")
add_s("war-reduced-tourists", 449, 450, C["austrian_succession_war"], C["english_tourists_1740s"],
      "outbreak_in_1740_cut_down_english_tourist_numbers",
      "Soon after the War of the Austrian Succession broke out in 1740, the number of English tourists was cut down.",
      "No number or exact scale of decline is given.", relation=True, layer="authorial narrative")
add_s("canaletto-returned-to-smith", 450, 450, E["canaletto"], E["smith"],
      "once_again_worked_for_his_most_persistent_patron",
      "In this period Canaletto once again began to work for his most persistent patron, Smith.",
      "The chronology is situated soon after the war outbreak and reduction in English tourists; the sentence does not give a precise restart date.",
      relation=True, layer="authorial narrative")
add_s("canaletto-style-and-subject-shift", 451, 451, E["canaletto"], C["canaletto_early_venetian_views"],
      "return_to_smith_marked_change_from_small_views_to_grandeur_and_fantasy",
      "Haskell says Canaletto’s return to Smith marked a striking stylistic and subject change: he gave up the small Venetian views behind his international reputation and turned to grandeur, fantasy and a wider range of subjects.",
      "This is Haskell’s characterization of the change; it does not claim that every earlier view ceased to be produced.",
      relation=True, layer="authorial interpretation")
add_s("possible-rome-visit-and-roman-series", 451, 452, E["canaletto"], C["canaletto_roman_views"],
      "quite_possibly_second_rome_visit_perhaps_with_smith_led_to_six_roman_views",
      "Haskell says there was quite possibly a second visit to Rome, perhaps with Smith, and that this led to six views of ancient Roman monuments.",
      "Both the second visit and Smith’s participation are qualified; keep the visit and resulting series provisional.",
      relation=True, layer="authorial hypothesis")
add_s("roman-views-largest-for-smith", 452, 452, C["canaletto_roman_views"], E["smith"],
      "largest_pictures_canaletto_painted_for_smith_and_likely_affected_his_collection",
      "The six Roman views were the largest pictures Canaletto ever painted for Smith and, Haskell says, must have made a great impact in the collection.",
      "The collection impact is Haskell’s inference, signaled by ‘must have’.", relation=True, layer="authorial inference")
add_s("roman-subjects-and-venetian-uniqueness", 452, 452, C["canaletto_roman_views"], E["venice"],
      "roman_monument_subjects_made_the_group_unique_in_venice",
      "Haskell says the subject matter made the Roman-view group unique in Venice.",
      "‘Unique’ is limited to Haskell’s comparison of the subjects in the Venetian context, not an independently verified census.",
      relation=True, layer="authorial interpretation")
add_s("rome-as-signal-and-outsider-view", 452, 453, C["canaletto_roman_views"], E["rome"],
      "interpreted_as_signal_of_roman_values_but_seen_from_outside",
      "Haskell reads the focus on grand ancient monuments as a signal that Rome and Roman values might resume a leading role in Italian art, while describing this as Rome seen by an outsider and unlike the matter-of-fact quality of Canaletto’s Venetian views.",
      "The return of Roman values is an analogy and prospective interpretation, not a factual political or artistic outcome.",
      relation=False, layer="authorial interpretation")
add_s("harsh-paint-and-dramatic-return", 452, 452, E["canaletto"], C["canaletto_roman_views"],
      "harsh_paint_with_return_to_early_dramatic_vision",
      "Haskell calls the paint harsh but sees in the Roman pictures a return to the dramatic vision of Canaletto’s earliest pictures.",
      "Both are Haskell’s stylistic judgments.", relation=False, layer="authorial interpretation")
add_s("smith-antique-rome-and-neoclassic", 452, 452, E["smith"], E["pannini"],
      "wanted_antique_rome_views_and_ignored_panninis_contemporary_rome",
      "Haskell says Smith wanted views of antiquity only and ignored Pannini’s contemporary Rome, but questions whether these pictures played more than a symbolic role in the rise of neo-classicism.",
      "The symbolic role is explicitly uncertain; do not report it as an established contribution to neo-classicism.",
      relation=False, layer="authorial interpretation")
add_s("next-commissioned-series-aim", 453, 454, E["canaletto"], C["canaletto_door_pieces"],
      "next_commissions_intended_to_portray_smiths_preferred_architectural_style",
      "Haskell says the next few paintings commissioned from Canaletto were clearly intended to portray the architectural style Smith particularly liked; he begins to identify a 1744 series of 13 Door Pieces.",
      "The title and sentence continue on p.308; do not finalize the series description before that segment is processed.",
      relation=True, cross=[P308], layer="authorial interpretation")

all_ids = cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < first or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside p.307: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if not q["mentioned_candidate_ids"]:
        raise SystemExit(f"statement has no anchored mention: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

# Close p.306's cross-page quotation while keeping the unresolved object identity explicit.
statuette_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p306-breval-statuette"), None)
statuette_candidate = next((row for row in candidates if row["candidate_id"] == "cand-9230"), None)
statuette_mention = next((row for row in mentions if row["mention_id"] == "m-chp10-p306-priapus" or
                          (row["segment_id"] == P306 and row["candidate_id"] == "cand-9230")), None)
if not statuette_statement or not statuette_candidate or not statuette_mention:
    raise SystemExit("p.306 statuette rows changed; cannot close cross-page reference")
statuette_statement["qualifiers"]["qualification"] = (
    "The p.307 continuation calls the same quoted object Priapus after p.306 called it seemingly an Aesculapius; "
    "the source’s differing labels are preserved and the statuette identity remains unresolved."
)
statuette_candidate["detail"] = (
    "John Breval’s p.306–307 reported description first calls it seemingly an Aesculapius, then says Priapus; "
    "the differing labels and proportions remain unresolved, with no object-level identification supplied."
)
statuette_mention["note"] = "The p.307 continuation calls the same statuette Priapus; preserve the discrepancy with p.306’s ‘seemingly an Aesculapius’ and do not resolve its identity."
cov[P306]["note"] = (
    "Printed p.306 body checked against CHP-10.pdf physical page 35. Closed p.305’s Canaletto style sentence; "
    "recorded Smith’s uncertain activity, old-master purchases, drawing collection, likely acquisition of much of "
    "Sebastiano Ricci’s studio after 1734, Pasquali’s illustrated editions and Visentini originals; Smith’s gems/cameos "
    "and 1737–38 letters to A. F. Gori; Smith’s qualified collector self-description and quoted preferences; praise and "
    "contrary dealer/antiquary judgments; and John Breval’s visit and statuette description. The p.307 continuation "
    "calls the same statuette Priapus after p.306’s ‘seemingly an Aesculapio’; retain both labels and leave its identity "
    "unresolved. Page-body footnote excerpts at L442–443 duplicate the consolidated notes source and are deferred; "
    "footnotes 1–6 remain pending. OCR source quote ‘charactèristic’ is visibly printed as ‘characteristic’; S2 records "
    "the correction without changing S0. The cross-page sentence is closed, but p.306 remains partial pending its notes."
)
cov[P307].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L446-454",
    "note": "Printed p.307 body checked against CHP-10.pdf physical page 36. Closed John Breval’s p.306 statuette quotation while preserving its conflicting Aesculapius/Priapus labels; recorded the sculptures, Cignani cartoons and collection objects shown; Smith’s early-1740s return to contemporary patronage, unidentified 1741 sale to the Elector of Saxony and approximate purchase of Dutch/Flemish pictures from Pellegrini’s unnamed widow; the probable but conditional provenance and then-current Frans van Mieris attribution of Vermeer’s Lady at the Virginals; the disputed Vermeer–Canaletto influence claim; the 1740 war/tourist context and Canaletto’s return to Smith; the qualified Rome visit and six Roman views; Haskell’s stylistic and neo-classical interpretations; and the beginning of the 1744 13 Door Pieces sentence. S0 OCR ‘theWermeer’ is visibly printed ‘the Vermeer’; correction recorded in S2 without changing S0. Printed footnotes 1–4 were checked and are deferred to the consolidated notes segment. The last sentence continues on p.308, so this page remains partial."})

summary = {"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": P307, "segment_sha256": digest, "new_candidates": len(newc),
           "candidate_ids": [row["candidate_id"] for row in newc],
           "new_mentions": len(newm), "new_statements": len(new_s),
           "closed_cross_page_segment": P306,
           "coverage": {"p306": cov[P306]["migration_status"], "p307": cov[P307]["migration_status"],
                        "p308": cov[P308]["migration_status"]}}
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
    print("Applied p.307 S2 body migration; printed footnotes remain with the consolidated notes segment.")
