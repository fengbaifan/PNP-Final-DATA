"""Controlled S2 migration for printed p.310; dry-run unless --apply."""
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
P309 = "chp-10:10_CHP-10_intro:l468-479"
P310 = "chp-10:10_CHP-10_intro:l481-489"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEGMENT_SHA = "1b5b051796bbac3725681b091cb6e82a00f22381d0f651f934a9ccbd590f66b7"
BACKUP = ".bak-s2-chp10-p310-20261002"


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
first, last, PAGE, PHYSICAL = 481, 489, 310, 39
body = "\n".join(src[first - 1:last])
digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
if digest != EXPECTED_SEGMENT_SHA or src[first - 1].strip() != "[Page 310]" or "Bibliotheca Smithiana" not in body:
    raise SystemExit(f"p.310 source segment mismatch: {digest}")
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
if maximum != 9267:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((P309, ("reviewed", "partial")), (P310, ("queued", "pending")),
                      (NOTES, ("queued", "pending"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if any(row["segment_id"] == P310 for row in mentions) or any(row["segment_id"] == P310 for row in statements):
    raise SystemExit("p.310 already has mention or statement rows")

E = {
    "smith": "cand-2440", "canaletto": "cand-0502", "london": "cand-1422",
    "smith_palace": "cand-9171", "country_house": "cand-9207", "smith_collection": "cand-9210",
    "smith_library": "cand-9177", "smith_pictures": "cand-9178", "drawings": "cand-9224",
    "gems": "cand-9228", "george_iii": "cand-1141", "war": "cand-9090",
    "england": "cand-8983", "italy": "cand-3461", "venice": "cand-2719",
    "james_adam": "cand-0011", "canaletto_pictures": "cand-9264",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("ricci_palace_works", "Unspecified works by the Riccis among Joseph Smith's palace holdings", "work",
     "The plural surname is retained as the source's collective reference. Individual works are not named; do not equate this group with the previously described Marco or Sebastiano Ricci groups before S3.", 482),
    ("cignani_palace_works", "Unspecified works by the Cignanis among Joseph Smith's palace holdings", "work",
     "The source gives only the plural surname in a list of palace holdings. Individual works and the exact artist identity are not supplied here; compare with existing Cignani work groups at S3.", 482),
    ("larger_palace_works", "Most of Joseph Smith's larger works hung in his Venetian palace", "work",
     "A size-based group of collection works, not a complete inventory. The passage does not identify individual works or establish whether this group overlaps the named artist groups.", 482),
    ("dutch_flemish_country_works", "Dutch and Flemish paintings kept at Joseph Smith's country house", "work",
     "The source identifies a broad group by the artists' regional designation but no individual paintings. It may overlap the earlier candidate for pictures bought from Pellegrini's widow; the passage does not equate them.", 483),
    ("zuccarelli_country_works", "Unspecified Zuccarelli paintings kept at Joseph Smith's country house", "work",
     "A group described only as a number of Zuccarelli pictures. Do not assume it is identical to the six Rebecca, Jacob and Esau landscapes recorded elsewhere.", 483),
    ("old_master_country_works", "Unspecified old-master paintings kept at Joseph Smith's country house", "work",
     "The source says many old masters were kept there but identifies no individual paintings. Do not merge with separately described acquisition groups before S3.", 483),
    ("bibliotheca_smithiana", "Bibliotheca Smithiana (Joseph Smith's 1755 book inventory)", "archive",
     "Haskell describes a 1755 inventory of Smith's books, almost certainly designed as an elaborate sale catalogue. The qualification is the author's inference; edition and surviving copy are not identified here.", 484),
    ("english_royal_family", "English royal family in Joseph Smith's 1756 collection negotiations", "institution",
     "Collective negotiating party as named by Haskell. Do not replace it with George III or infer the family members involved; the sale to George III is separately described for 1762.", 484),
    ("smith_royal_negotiations", "Joseph Smith's 1756 negotiations to dispose of his library and collections", "event",
     "Haskell says the negotiations with the English royal family were interrupted almost at once by the outbreak of the Seven Years War. The passage does not establish uninterrupted negotiations through the 1762 sale.", 484),
    ("giovanni_crisostomo_theatre", "Theatre of S. Giovanni Crisostomo mentioned in Smith's 1756 account", "place",
     "Venue at which Smith gave up his box in 1756. Preserve the printed name; the passage does not resolve a modern institutional or building identity.", 486),
    ("smith_george_iii_sale", "Joseph Smith's 1762 sale of most of his best pictures, books, drawings and gems to George III", "event",
     "Haskell says difficult negotiations culminated in the sale of most of Smith's best items in these categories. Do not expand 'most' to the whole collection or assume the 1756 negotiations continued without interruption.", 488),
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
                 "candidate_source_ref": f"{P310}#L{line}"})

newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p310-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    positions, at = [], 0
    while True:
        at = body.find(surface, at)
        if at < 0:
            break
        start_line = first + body[:at].count("\n")
        if start_line == line:
            positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": P310, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


M = [
    ("return-from-london", 482, "from London", E["london"], "Closes p.309 L479: Canaletto returned from London in 1755."),
    ("canaletto-views-resumed", 482, "These", E["canaletto_pictures"], "Corefers to the additional Canaletto pictures introduced on p.309 L479."),
    ("ricci-palace-work-group", 482, "the Riccis", C["ricci_palace_works"]),
    ("cignani-palace-work-group", 482, "Cignanis", C["cignani_palace_works"]),
    ("larger-palace-works", 482, "most of his larger works", C["larger_palace_works"]),
    ("smith-palace", 482, "his palace", E["smith_palace"], "Smith's Venetian palace; the passage does not identify a different building."),
    ("smith-country-house", 482, "his country house", E["country_house"], "Corefers to Smith's country house at Mogliano identified earlier; p.310 itself gives no toponym."),
    ("dutch-flemish-pictures", 482, "the paintings by\nDutch and Flemish artists", C["dutch_flemish_country_works"]),
    ("zuccarelli-country-pictures", 483, "a number of Zuccarellis", C["zuccarelli_country_works"]),
    ("old-master-country-pictures", 483, "many of the old masters", C["old_master_country_works"]),
    ("smith-by-this-time", 484, "he was already nearly 80", E["smith"], "Corefers to Joseph Smith."),
    ("smith-library-plan", 484, "his library", E["smith_library"]),
    ("smith-collections-plan", 484, "collections", E["smith_collection"]),
    ("smith-1755-inventory-books", 484, "his books", E["smith_library"]),
    ("bibliotheca-title", 484, "Bibliotheca Smithiana", C["bibliotheca_smithiana"]),
    ("smith-published-inventory", 484, "he published", E["smith"], "Corefers to Smith as publisher."),
    ("english-royal-family", 484, "English royal family", C["english_royal_family"]),
    ("smith-negotiations-event", 484, "negotiations", C["smith_royal_negotiations"]),
    ("smith-began-negotiations", 484, "he began", E["smith"], "Corefers to Smith, who begins negotiations a year after 1755."),
    ("seven-years-war", 484, "Seven Years\nWar", E["war"]),
    ("smith-affected", 486, "him", E["smith"], "Corefers to Joseph Smith."),
    ("smith-withdrew", 486, "he began to withdraw", E["smith"], "Corefers to Joseph Smith."),
    ("smith-theatre-box", 486, "the theatre of S. Giovanni Crisostomo", C["giovanni_crisostomo_theatre"]),
    ("smith-gave-up-box", 486, "he gave up his box", E["smith"], "Corefers to Smith."),
    ("smith-resigned-consulship", 486, "he resigned the consulship", E["smith"], "Corefers to Smith; the text places this four years after 1756."),
    ("smith-wished-england", 486, "he wished to return", E["smith"], "Corefers to Smith and introduces his quoted travel plan."),
    ("england-return-plan", 486, "England", E["england"]),
    ("smith-art-collections-quote", 486, "considerable collections of tilings", E["smith_collection"], "S0 OCR reads 'tilings'; the printed page reads 'things'."),
    ("italian-towns-plan", 486, "Italy", E["italy"]),
    ("venice-known-only", 487, "Venice", E["venice"]),
    ("james-adam", 487, "James Adam", E["james_adam"]),
    ("james-met-smith", 487, "him and wrote", E["smith"], "Corefers to Smith, whom James Adam met."),
    ("james-quote-smith", 487, "he was ‘devilish poor", E["smith"], "Corefers to Smith inside James Adam's quoted assessment."),
    ("james-quote-continued", 488, "he has", E["smith"], "Corefers to Smith in the continued quotation."),
    ("james-quote-collection", 488, "a fine collection", E["smith_collection"]),
    ("smith-managed-sale", 488, "he at last managed", E["smith"], "Corefers to Smith, subject of the 1762 sale."),
    ("smith-pictures-sold", 488, "most of his best pictures", E["smith_pictures"]),
    ("smith-books-sold", 488, "books", E["smith_library"]),
    ("smith-drawings-sold", 488, "drawings", E["drawings"]),
    ("smith-gems-sold", 488, "gems", E["gems"]),
    ("george-iii-purchase", 488, "King George III", E["george_iii"]),
    ("smith-1762-sale-event", 488, "after difficult negotiations", C["smith_george_iii_sale"]),
    ("remaining-collection", 488, "enough remained", E["smith_collection"], "Haskell does not identify which residence's walls are meant."),
    ("smith-vitality", 488, "His vitality", E["smith"]),
    ("smith-active-business", 488, "he still actively engaged", E["smith"], "Corefers to Smith."),
    ("smith-consul-again", 488, "he again became Consul", E["smith"], "Corefers to Smith; the consulship resumes in 1766."),
    ("smith-retired-life", 488, "he seems to have lived", E["smith"], "Corefers to Smith; Haskell retains 'seems'."),
    ("smith-died", 488, "He finally died", E["smith"], "Corefers to Smith."),
    ("canaletto-after-death", 489, "Canaletto", E["canaletto"]),
    ("smith-associated-pronoun", 489, "he will always be associated", E["smith"], "Corefers to Smith."),
]
for row in M:
    add_m(*row)

new_s = []


def add_s(local, lo, hi, subject, obj, predicate, claim, qualification, relation=False,
          footnote=None, cross=None, cross_ranges=None, cross_pages=None,
          layer="authorial narrative", speaker="Haskell"):
    sid = f"st-chp10-p310-{local}"
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    mentioned = []
    for mention in newm:
        start = int(mention["start_char"])
        line_no = first + body[:start].count("\n")
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
    if cross_ranges:
        qualifiers["cross_reference_source_line_ranges"] = cross_ranges
    if cross_pages:
        qualifiers["cross_reference_printed_pages"] = cross_pages
    if not mentioned:
        raise SystemExit(f"statement has no anchored mention: {sid}")
    new_s.append({"statement_id": sid, "segment_id": P310, "subject_candidate_id": subject,
                  "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": "\n".join(src[lo - 1:hi]), "source_file": SOURCE_FILE, "origin": "book"})


add_s("canaletto-return-from-london", 482, 482, E["smith"], E["canaletto_pictures"],
      "smiths_additional_canaletto_pictures_include_english_views_after_return_from_london_in_1755",
      "Haskell's sentence begun on p.309 says Smith bought additional pictures from Canaletto, including English views; p.310 identifies Canaletto's return as from London in 1755.",
      "The individual views and their number are not supplied; the cross-page sentence closes here.", relation=True,
      cross=[P309], cross_ranges=[{"segment_id": P309, "line_start": 479, "line_end": 479}], cross_pages=[309])
add_s("palace-holdings", 482, 482, E["smith"], E["smith_palace"],
      "smith_hung_canaletto_views_ricci_and_cignani_works_and_most_larger_works_in_palace",
      "Haskell says the Canaletto views, works represented by the Riccis and Cignanis, and most of Smith's larger works were hung in his palace.",
      "The artist-group works and larger works are not itemized; 'most' is retained and the groups are kept distinct from earlier acquisition groups pending S3.", relation=True)
add_s("country-house-holdings", 482, 483, E["smith"], E["country_house"],
      "smith_kept_dutch_flemish_zuccarelli_and_old_master_pictures_at_country_house",
      "Haskell says Smith kept Dutch and Flemish pictures, a number of Zuccarelli pictures and many old masters at his country house.",
      "The source does not identify individual pictures or establish whether these groups equal earlier acquisitions. Footnote 1 remains pending in the consolidated notes segment.", relation=True, footnote=1)
add_s("plans-to-dispose-library-collection", 484, 484, E["smith"], E["smith_library"],
      "smith_nearly_80_made_plans_to_dispose_of_library_and_collections",
      "By this time, Haskell says Smith was already nearly 80 and making plans to dispose of his library and collections.",
      "The wording records plans, not a completed disposal; the text does not date when each plan began.", relation=False)
add_s("bibliotheca-inventory", 484, 484, E["smith"], C["bibliotheca_smithiana"],
      "smith_published_1755_inventory_of_books_called_bibliotheca_smithiana",
      "In 1755 Smith published an inventory of his books called Bibliotheca Smithiana.",
      "Haskell calls the title grand but slightly absurd and says it was 'almost certainly' designed as an elaborate sale catalogue; preserve that as an authorial inference, not a verified purpose.", relation=True)
add_s("1756-royal-negotiations-war", 484, 485, E["smith"], C["smith_royal_negotiations"],
      "smith_began_1756_collection_disposal_negotiations_with_english_royal_family_interrupted_by_war",
      "A year after the 1755 inventory, Smith began negotiations with the English royal family; the outbreak of the Seven Years War interrupted them almost at once.",
      "The passage does not say who in the royal family negotiated or establish that negotiations continued without interruption until the 1762 sale. Footnote 2 remains pending.", relation=True, footnote=2)
add_s("smith-social-withdrawal", 486, 486, E["smith"], None,
      "smith_withdrew_from_social_life_after_disappointment_age_and_trade_disruption",
      "Haskell says disappointment, old age and trade disruption deeply affected Smith, who began withdrawing more and more from social life.",
      "The cause and degree of withdrawal are Haskell's account. S0 OCR 'social Use' is corrected against the page image to 'social life'; S0 remains unchanged.",
      relation=False, layer="authorial interpretation")
add_s("smith-gave-up-theatre-box", 486, 486, E["smith"], C["giovanni_crisostomo_theatre"],
      "smith_gave_up_his_box_at_s_giovanni_crisostomo_theatre_in_1756",
      "In 1756 Smith gave up his box in the theatre of S. Giovanni Crisostomo.",
      "The text identifies the venue and date but not the box's ownership or contractual status. Footnote 3 remains pending.", relation=True, footnote=3)
add_s("smith-resigned-consulship", 486, 486, E["smith"], None,
      "smith_resigned_the_consulship_four_years_after_1756",
      "Four years after giving up his theatre box in 1756, Smith resigned the consulship, placing the resignation in 1760.",
      "The 1760 date is derived from the passage's relative chronology; the cited letter in footnote 4 is dated 29 October 1760, but its note text remains pending.", relation=False, footnote=4)
add_s("smith-return-and-italy-travel-plan", 486, 487, E["smith"], E["england"],
      "smith_wrote_of_returning_to_england_after_visiting_italian_towns_he_had_not_seen",
      "Haskell quotes Smith as wishing to return to England, but first visit the principal towns of Italy because he knew only Venice; Smith says he had spent spare time admiring fine arts and collecting related objects.",
      "This is Smith's quoted statement as relayed by Haskell, not proof that the proposed journey occurred. S0 OCR 'sine arts'/'tilings' is corrected from the page image to 'fine arts'/'things'; S0 remains unchanged. Footnote 4 remains pending.",
      relation=False, footnote=4, layer="nested quotation", speaker="Joseph Smith as quoted by Haskell")
add_s("james-adam-meeting-and-assessment", 487, 488, E["james_adam"], E["smith"],
      "james_adam_met_smith_and_described_him_as_devilish_poor_and_at_risk_of_bankruptcy",
      "At about this time James Adam met Smith and wrote that he was 'devilish poor', might die bankrupt if he lived a few more years, and ought to sell his collection although vanity prevented him.",
      "This is James Adam's contemporary assessment as quoted by Haskell, not independently verified financial evidence. Footnote 5's letter references remain pending.",
      relation=False, footnote=5, layer="nested quotation", speaker="James Adam as quoted by Haskell")
add_s("1762-sale-to-george-iii", 488, 488, E["smith"], C["smith_george_iii_sale"],
      "smith_sold_most_of_his_best_pictures_books_drawings_and_gems_to_george_iii_in_1762",
      "In 1762, after difficult negotiations, Smith managed to sell most of his best pictures, books, drawings and gems to King George III.",
      "Preserve 'most' and 'best'; this is not a claim that the entire collection was sold. Footnote 6 points to Appendix 5 and remains pending.", relation=True, footnote=6)
add_s("collection-remained-on-walls", 488, 488, E["smith"], E["smith_collection"],
      "some_of_smiths_collection_remained_enough_to_cover_his_walls",
      "Haskell says enough of Smith's collection remained after the sale to cover his walls.",
      "The passage does not specify which residence's walls are meant.", relation=False)
add_s("smith-business-and-picture-dealing", 488, 488, E["smith"], None,
      "smith_remained_active_in_business_including_picture_dealing",
      "Haskell says Smith remained actively engaged in business, including picture dealing.",
      "This is a general description; no individual transaction or counterpart is named.", relation=False)
add_s("smith-consul-return-1766", 488, 488, E["smith"], None,
      "smith_again_became_consul_for_a_few_months_in_1766",
      "Haskell says Smith again became Consul in 1766 for a few months.",
      "The passage does not state the exact dates or location of this short return to office.", relation=False)
add_s("smith-retired-life", 488, 488, E["smith"], None,
      "smith_seems_to_have_lived_a_retired_life_attracting_little_attention",
      "Apart from his business activity, Haskell says Smith seems to have lived a retired life and attracted little attention from native Venetians or tourists.",
      "Retain Haskell's 'seems'; this is not evidence that no one noticed him. S0 OCR 'retired fife' is corrected from the page image to 'retired life'; S0 remains unchanged.",
      relation=False, layer="authorial interpretation")
add_s("smith-death-1770-after-canaletto", 488, 489, E["smith"], E["canaletto"],
      "smith_died_in_1770_two_years_after_canaletto",
      "Haskell says Smith died in 1770, two years after Canaletto.",
      "The relative date is Haskell's statement; p.310 does not give Canaletto's exact death date.", relation=False)
add_s("smith-associated-with-canaletto", 489, 489, E["smith"], E["canaletto"],
      "haskell_says_smith_will_always_be_associated_with_canaletto",
      "Haskell concludes that Smith will always be associated with Canaletto.",
      "This is Haskell's retrospective characterization, not a separate formal relationship claim.", relation=False, layer="authorial interpretation")

all_ids = cids | {row["candidate_id"] for row in newc}
for row in new_s:
    q = row["qualifiers"]
    if q["source_line_start"] < first + 1 or q["source_line_end"] > last:
        raise SystemExit(f"statement range outside p.310 body: {row['statement_id']}")
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"missing statement FK {row['statement_id']} -> {cid}")
    if any(cid not in all_ids for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"missing mention candidate in {row['statement_id']}")

spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in newm)
for left, right in zip(spans, spans[1:]):
    if right[0] < left[1]:
        raise SystemExit(f"overlapping mentions: {left[2]} / {right[2]}")

# Close the p.309 Canaletto-return sentence and retain the earlier page's pending notes.
p309_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p309-smith-bought-more-canaletto-views"), None)
if not p309_statement:
    raise SystemExit("p.309 Canaletto-return statement missing")
p309_statement["qualifiers"]["claim"] = (
    "Haskell says Smith bought more pictures from Canaletto, including a number of English views, on the artist's return; "
    "p.310 identifies the return as from London in 1755."
)
p309_statement["qualifiers"]["qualification"] = (
    "The sentence closes at p.310 L482. The individual English views remain unidentified; p.309 footnotes 1–6 "
    "remain pending in the consolidated notes segment."
)
p309_statement["qualifiers"]["cross_reference_source_line_ranges"] = [
    {"segment_id": P310, "line_start": 482, "line_end": 482}
]
p309_statement["qualifiers"]["cross_reference_printed_pages"] = [310]
canaletto_candidate = next(row for row in candidates if row["candidate_id"] == E["canaletto_pictures"])
canaletto_candidate["canonical_name"] = "Additional pictures acquired by Joseph Smith from Canaletto on his return from London in 1755"
canaletto_candidate["detail"] = (
    "Includes an unspecified number of English views. The cross-page sentence says Canaletto returned from London in 1755; "
    "individual views and their number are not supplied."
)
old_note = "The later Canaletto-purchase sentence continues on p.310."
if old_note not in cov[P309]["note"]:
    raise SystemExit("p.309 coverage note no longer has the expected open-sentence text")
cov[P309]["note"] = cov[P309]["note"].replace(
    old_note,
    "The Canaletto-purchase sentence closes at p.310 L482, which identifies the artist's return as from London in 1755."
)
cov[P310].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L482-489",
    "note": "Printed p.310 body checked against CHP-10.pdf physical page 39. Closed p.309 L479: Canaletto returned from London in 1755; the individual English views remain unnamed. Recorded the separate palace and country-house holdings, preserving distinct candidate groups for Ricci/Cignani works, most larger works, Dutch/Flemish pictures, Zuccarelli pictures and old masters pending S3 identity alignment. Recorded Smith's plans to dispose of his library and collections, the 1755 Bibliotheca Smithiana (only 'almost certainly' a sale catalogue), 1756 negotiations interrupted by the Seven Years War, his 1756 theatre box, the 1760 consulship resignation and quoted travel plan, James Adam's contemporary financial assessment, the 1762 sale of most selected collection categories to George III, the remaining collection, business/picture dealing, brief 1766 return as Consul, retired life and 1770 death. Footnotes 1–6 remain pending in the consolidated notes segment; footnote 6 points to Appendix 5. Page-image corrections are recorded only in S2: 'social Use'→'social life', 'sine arts'→'fine arts', 'tilings'→'things', 'retired fife'→'retired life'; S0 remains unchanged."})

summary = {"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
           "segment": P310, "segment_sha256": digest, "new_candidates": len(newc),
           "candidate_ids": [row["candidate_id"] for row in newc],
           "new_mentions": len(newm), "new_statements": len(new_s),
           "closed_cross_page_segment": P309,
           "coverage": {"p309": cov[P309]["migration_status"], "p310": cov[P310]["migration_status"],
                        "notes": cov[NOTES]["migration_status"]}}
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
    print("Applied p.310 S2 body migration; footnotes 1–6 remain in the consolidated notes segment.")
