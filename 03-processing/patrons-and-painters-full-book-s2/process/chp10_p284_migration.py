"""Controlled S2 migration for p.284; dry-run unless --apply is passed."""
import csv, hashlib, json, re, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
PREV = "chp-10:10_CHP-10_intro:l151-165"
SEG = "chp-10:10_CHP-10_intro:l167-176"
NEXT = "chp-10:10_CHP-10_intro:l178-188"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "04334ccfd7b76b83960b6ab5f8d96f1400b0482c11f2d7719a3c3185ad3eda21"
MAX_CAND = 8956
BACKUP = ".bak-s2-chp10-p284-20261002"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(src[166:176])
if hashlib.sha256(body.encode()).hexdigest() != SEG_SHA or src[166].strip() != "[Page 284]":
    raise SystemExit("p.284 source segment hash/page mismatch")
if "when the Elector died in 1716? He worked in Antwerp" not in src[168]:
    raise SystemExit("expected OCR footnote marker in p.284 text changed")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {r["candidate_id"] for r in candidates}
mids = {r["mention_id"] for r in mentions}
sids = {r["statement_id"] for r in statements}
cov = {r["segment_id"]: r for r in coverage}
maximum = max(int(re.search(r"\d+", r["candidate_id"]).group()) for r in candidates)
if maximum != MAX_CAND:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")), (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "bellucci": "cand-0282", "bellucci_group": "cand-8955", "johann": "cand-1325",
    "veronese": "cand-2755", "pellegrini": "cand-1862", "dusseldorf": "cand-0955",
    "low_countries": "cand-4342", "holland": "cand-6084", "antwerp": "cand-4983",
    "amsterdam": "cand-6617", "cadogan": "cand-0477", "marlborough": "cand-8869",
    "flanders": "cand-4652", "paris": "cand-4653", "ricci": "cand-2154",
    "london": "cand-1422", "crozat": "cand-0894", "crozat_house": "cand-8846",
    "la_fosse": "cand-1343", "watteau": "cand-2804", "carriera": "cand-0581",
    "zanetti": "cand-2838", "louis_xiv": "cand-1447", "john_law": "cand-1367",
    "france": "cand-5317", "england": "cand-7200", "versailles": "cand-3985",
}
for k, v in E.items():
    if v not in cids:
        raise SystemExit(f"missing candidate {k}={v}")

NEW_SPECS = [
    ("amsterdam_hall", "Amsterdam City Hall (building Pellegrini was commissioned to decorate)", "place",
     "The source calls it the city hall in Amsterdam; it supplies no formal building name.", 169),
    ("amsterdam_frescoes", "Unidentified frescoes commissioned from Giovanni Antonio Pellegrini for Amsterdam City Hall", "work",
     "A group commission reported by Haskell; no titles, count, or completion status are supplied.", 169),
    ("hague", "The Hague", "place",
     "City named as Lord Cadogan's diplomatic post; no building or country-house location is asserted there.", 169),
    ("cadogan_house", "Unidentified country house of Lord Cadogan that Pellegrini was to decorate (summer 1719)", "place",
     "Haskell reports Pellegrini's purpose in returning to England; the house is unnamed and its precise location is not given.", 169),
    ("rue_richelieu", "Rue Richelieu, Paris", "place",
     "Street location of Pierre Crozat's mansion as described by Haskell.", 171),
    ("watteau_sheet", "Unidentified sheet of Antoine Watteau drawings copied by Sebastiano Ricci", "work",
     "Haskell reports Ricci copied a sheet; neither its title nor present location is supplied.", 172),
    ("mississippi_gallery", "Mississippi Gallery at the Banque Royale", "place",
     "Named gallery space identified by Haskell as the decorative commission given to Pellegrini.", 174),
    ("mississippi_programme", "Pellegrini's decorative programme for the Mississippi Gallery", "work",
     "The programme combined royal glorification and allegorical tributes to commerce; p.284 sentence continues on p.285.", 174),
    ("banque_royale", "Banque Royale, John Law's Paris bank", "institution",
     "Haskell identifies it as the headquarters of John Law's financial scheme; the account is not independently verified here.", 174),
    ("law_system", "John Law's Système financial scheme", "term",
     "Haskell calls it reckless but still successful at the time; preserve that temporal and evaluative framing.", 175),
]
newc, C = [], {}
for i, (key, name, kind, detail, line) in enumerate(NEW_SPECS, MAX_CAND + 1):
    cid = f"cand-{i:04d}"
    if cid in cids or any(r["canonical_name"] == name and r["suggested_type"] == kind for r in candidates):
        raise SystemExit(f"candidate already exists: {cid} {name}")
    C[key] = cid
    newc.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
                 "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
                 "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
                 "candidate_source_ref": f"{SEG}#L{line}"})

offsets, offset = {}, 0
for n in range(167, 177):
    offsets[n] = offset
    offset += len(src[n - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p284-{local}"
    if mid in mids or any(r["mention_id"] == mid for r in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {r["candidate_id"] for r in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    positions, at = [], 0
    while True:
        at = src[line - 1].find(surface, at)
        if at < 0:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}")
    a = offsets[line] + positions[occurrence]
    b = a + len(surface)
    if body[a:b] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid, "surface_form": surface,
                 "start_char": str(a), "end_char": str(b), "note": note})


MENTIONS = [
    ("bellucci_which",168,"which",E["bellucci_group"],"Relative pronoun refers to Bellucci's allegories and group portraits."),
    ("bellucci_he",168,"he",E["bellucci"],"Continuation identifies Bellucci as the Venetian artist described."),
    ("veronese",168,"Veronese",E["veronese"],"Artist whose example Bellucci is said to have appreciated."),
    ("pellegrini",169,"Pellegrini",E["pellegrini"],"Artist discussed on p.284."),
    ("dusseldorf",169,"Düsseldorf",E["dusseldorf"],"Existing candidate; identity/alignment remains for S3."),
    ("low_countries",169,"Low Countries",E["low_countries"],"Geographic region in Haskell's account."),
    ("elector",169,"the Elector",E["johann"],"Title linked to the p.277 Palatine candidate for S3 review."),
    ("antwerp",169,"Antwerp",E["antwerp"],"City where Pellegrini worked."),
    ("amsterdam",169,"Amsterdam",E["amsterdam"],"City where Pellegrini worked and received the city-hall commission."),
    ("city_hall",169,"the city hall",C["amsterdam_hall"],"Unspecified Amsterdam city hall building."),
    ("frescoes",169,"frescoes",C["amsterdam_frescoes"],"Collective commission; completion is not claimed."),
    ("holland",169,"Holland",E["holland"],"Region as named by Haskell."),
    ("italian_artist",169,"an Italian artist",E["pellegrini"],"Refers to Pellegrini; Haskell's first-time claim is retained as his account."),
    ("england",169,"England",E["england"],"Destination named for the short return in summer 1719."),
    ("hague",169,"The Hague",C["hague"],"Lord Cadogan's diplomatic post."),
    ("cadogan",169,"Lord Cadogan",E["cadogan"],"The English Ambassador named by Haskell."),
    ("country_house",169,"country house",C["cadogan_house"],"Unidentified house Pellegrini was to decorate; exact location is not stated."),
    ("marlborough",169,"Marlborough",E["marlborough"],"Commander named without first name on this page; keep as title candidate pending S3."),
    ("flanders",169,"Flanders",E["flanders"],"Campaign region named by Haskell."),
    ("paris",170,"Paris",E["paris"],"City in Haskell's comparative framing."),
    ("ricci",170,"Sebastiano Ricci",E["ricci"],"Artist's move to Paris in 1716."),
    ("london",170,"London",E["london"],"Departure city as stated by Haskell."),
    ("crozat",171,"Pierre Crozat",E["crozat"],"Collector and host named by Haskell."),
    ("rue_richelieu",171,"Rue Richelieu",C["rue_richelieu"],"Street named as location of Crozat's mansion."),
    ("crozat_mansion",171,"mansion",E["crozat_house"],"Existing p.277 candidate for Crozat's Paris residence."),
    ("la_fosse",171,"Charles de la Fosse",E["la_fosse"],"Painter lodged at Crozat's house."),
    ("london_lafosse",171,"London",E["london"],"La Fosse had been in London; same city candidate reused."),
    ("ricci_in_crozat_house",171,"Ricci",E["ricci"],"Named as the artist La Fosse did not admire.",1),
    ("crozat_discovery",172,"Crozat’s latest discovery",E["crozat"],"Crozat is the referent."),
    ("watteau",172,"Antoine Watteau",E["watteau"],"Artist living at Crozat's house."),
    ("watteau_house",172,"his house",E["crozat_house"],"Possessive refers to Crozat's Paris residence."),
    ("elderly_venetian",172,"the elderly Venetian",E["ricci"],"Refers to Sebastiano Ricci in the preceding paragraph."),
    ("watteau_drawings",172,"his drawings",E["watteau"],"Drawings by Watteau; individual sheet remains unidentified."),
    ("copied_sheet",172,"a sheet",C["watteau_sheet"],"Unidentified sheet copied by Ricci."),
    ("pellegrini_visit",173,"Pellegrini",E["pellegrini"],"Visitor to France four years after Ricci."),
    ("carriera",173,"Rosalba",E["carriera"],"Rosalba Carriera, identified by continuation on L174."),
    ("carriera_continuation",174,"Carriera",E["carriera"],"Continuation of the line-break name Rosalba Carriera."),
    ("zanetti",174,"Antonio Maria Zanetti",E["zanetti"],"Engraver and connoisseur; candidate is the Elder index entry."),
    ("france",174,"France",E["france"],"Place of the reported impact of contemporary Italian art."),
    ("crozat_patronage",174,"patronage of Crozat",E["crozat"],"Crozat's patronage as the route of introduction to aristocratic society."),
    ("louis_xiv",174,"Louis XIV",E["louis_xiv"],"Named in Haskell's description of the period after his death."),
    ("mississippi_gallery",174,"Mississippi Gallery",C["mississippi_gallery"],"Named decorative space in the Banque Royale."),
    ("banque_royale_part1",174,"Banque",C["banque_royale"],"First word of the bank name split across the source line."),
    ("banque_royale_part2",175,"Royale",C["banque_royale"],"Line-wrapped continuation of Banque Royale."),
    ("john_law",175,"John Law",E["john_law"],"Financier associated with the Système."),
    ("systeme",176,"Système",C["law_system"],"Named financial scheme; OCR spelling confirmed against print."),
    ("gallery_programme",176,"The programme",C["mississippi_programme"],"Refers to Pellegrini's Mississippi Gallery decoration."),
    ("versailles",176,"Versailles",E["versailles"],"Place used as a comparison for royal glorification."),
]
for row in MENTIONS:
    add_m(*row)

new_s = []


def q(start, end):
    a = body.find(start)
    if a < 0:
        raise SystemExit(f"quote start absent: {start!r}")
    b = body.find(end, a)
    if b < 0:
        raise SystemExit(f"quote end absent: {end!r}")
    return body[a:b + len(end)]


def add_s(sid, lo, hi, subj, obj, pred, start, end, claim, qualification, mentioned,
          speaker="Haskell", layer="authorial narrative", relation=False, cross=None, footnote=None):
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    qualifiers = {"source_line_start":lo, "source_line_end":hi, "printed_page":284,
                  "pdf_physical_page":13, "claim":claim, "speaker":speaker,
                  "text_layer":layer, "qualification":qualification,
                  "mentioned_candidate_ids":mentioned, "relation_candidate":relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
    if cross:
        qualifiers["cross_reference_segments"] = cross
    new_s.append({"statement_id":sid,"segment_id":SEG,"subject_candidate_id":subj,
                  "object_candidate_id":obj,"predicate":pred,"qualifiers":qualifiers,
                  "original_quote":q(start,end),"source_file":SOURCE_FILE,"origin":"book"})


add_s("st-chp10-p284-bellucci-veronese-appreciation",168,168,E["bellucci"],E["veronese"],
      "bellucci_works_show_early_appreciation_of_veronese","which show that he was among the earliest",
      "appreciate the example of Veronese.",
      "Haskell says Bellucci's allegories and group portraits show that Bellucci was among the earliest eighteenth-century Venetian artists to appreciate Veronese.",
      "The pronoun refers to Bellucci; this is Haskell's art-historical assessment.",
      [E["bellucci_group"],E["veronese"]],cross=[{"segment_id":PREV,"source_line_start":163,"source_line_end":163}],footnote=1)
add_s("st-chp10-p284-pellegrini-low-countries",169,169,E["pellegrini"],E["low_countries"],
      "pellegrini_moved_to_low_countries_after_elector_died","Pellegrini’s connections with Düsseldorf",
      "He worked in Antwerp and Amsterdam,",
      "Haskell says Pellegrini's Düsseldorf connections made the move to the Low Countries logical after the Elector died in 1716 and reports work in Antwerp and Amsterdam.",
      "The opening is Haskell's inference rather than an independently evidenced motive; the footnote marker after 1716 is misread as a question mark in OCR.",
      [E["dusseldorf"],E["johann"],E["antwerp"],E["amsterdam"]],footnote=2)
add_s("st-chp10-p284-pellegrini-amsterdam-city-hall",169,169,E["pellegrini"],C["amsterdam_hall"],
      "pellegrini_commissioned_amsterdam_city_hall_frescoes","where he was actually commissioned",
      "decorate the city hall with frescoes",
      "Haskell says Pellegrini was commissioned to decorate Amsterdam's city hall with frescoes.",
      "The text reports a commission and does not independently establish completion.",
      [E["pellegrini"],E["amsterdam"],C["amsterdam_frescoes"]],relation=True)
add_s("st-chp10-p284-first-italian-artist-in-holland",169,169,E["pellegrini"],E["holland"],
      "haskell_calls_pellegrini_first_italian_artist_to_paint_in_holland",
      "the first time an Italian artist had ever painted in Holland",
      "a remarkable sign of the cosmopolitanism of early eighteenth-century culture.",
      "Haskell presents the commission as the first time an Italian artist had painted in Holland and calls it a sign of cosmopolitanism.",
      "Retain as Haskell's historical claim and interpretation; no external verification is supplied here.",
      [E["pellegrini"],E["holland"],E["amsterdam"]],layer="authorial claim and interpretation")
add_s("st-chp10-p284-cadogan-house-purpose",169,169,E["pellegrini"],C["cadogan_house"],
      "pellegrini_returned_to_decorate_cadogan_country_house","From Holland he was taken back to England",
      "had later been a Whig M.P.",
      "Haskell says Pellegrini was taken back to England for a short time in summer 1719 to decorate Lord Cadogan's country house; Cadogan is identified as the English Ambassador in The Hague.",
      "The property is unnamed; the text does not locate it in The Hague, and the commission's completion is not stated.",
      [E["holland"],E["england"],E["cadogan"],C["hague"],C["cadogan_house"]],relation=True)
add_s("st-chp10-p284-cadogan-career",169,169,E["cadogan"],E["marlborough"],
      "cadogan_served_with_marlborough_in_flanders_and_later_became_whig_mp",
      "had served as commander with Marlborough in Flanders","had later been a Whig M.P.",
      "Haskell describes Cadogan as having served as a commander with Marlborough in Flanders and later as a Whig member of Parliament.",
      "Marlborough is given by title only in this passage; personal identity is deferred to S3.",
      [E["marlborough"],E["flanders"]],relation=True)
add_s("st-chp10-p284-paris-venetian-painting",170,170,E["paris"],None,
      "paris_as_third_town_helped_free_venetian_painting","Paris was the third town",
      "the bondage of the past.",
      "Haskell calls Paris the third town that helped free Venetian painting from the past.",
      "This is an authorial art-historical framing, not a discrete event or quantified causal claim.",
      [E["paris"]],layer="authorial interpretation")
add_s("st-chp10-p284-ricci-to-paris-1716",170,170,E["ricci"],E["paris"],
      "sebastiano_ricci_went_to_paris_in_1716","Sebastiano Ricci went there in 1716",
      "on his departure from London.",
      "Haskell says Sebastiano Ricci went to Paris in 1716 when he left London.",
      "The source gives the year and departure context; no itinerary detail is added.",
      [E["london"]],relation=True)
add_s("st-chp10-p284-crozat-mansion-collection",171,171,E["crozat"],E["crozat_house"],
      "crozat_mansion_on_rue_richelieu_housed_collection","He was at once brought into touch with Pierre Crozat",
      "Italian and Flemish masters.",
      "Haskell says Crozat, aged 51, had a fine mansion on Rue Richelieu with a superb painting collection and thousands of drawings by major Italian and Flemish masters.",
      "The collection is described in Haskell's account; the passage does not provide an inventory. Note 3 remains pending.",
      [E["crozat"],C["rue_richelieu"]],footnote=3)
add_s("st-chp10-p284-crozat-weekly-meetings",171,171,E["crozat"],None,
      "crozat_hosted_weekly_gatherings_and_opened_collection_to_artists",
      "Crozat used to arrange weekly meetings","easily available to them.",
      "Haskell says Crozat hosted weekly meetings of art-lovers, painters, and writers, welcomed artists, and made his collection available to them.",
      "Participants are described collectively and are not expanded into named entities.",
      [E["crozat"],E["crozat_house"]],relation=True)
add_s("st-chp10-p284-la-fosse-lodged-and-aged",171,171,E["la_fosse"],E["crozat_house"],
      "la_fosse_lodged_at_crozat_house_in_final_year","When Ricci arrived, Charles de la Fosse",
      "his eightieth and last year,",
      "Haskell says Charles de la Fosse, who had been to London, was lodging at Crozat's house when Ricci arrived and was in his eightieth and final year.",
      "The age is reported by Haskell; no exact birth date is inferred.",
      [E["london"],E["ricci"]],relation=True,footnote=4)
add_s("st-chp10-p284-la-fosse-view-of-ricci",171,171,E["la_fosse"],E["ricci"],
      "la_fosse_not_impressed_by_ricci_despite_admiring_venetian_painting",
      "though an enthusiastic admirer of Venetian painting","he was not impressed by Ricci.",
      "Haskell reports that La Fosse admired Venetian painting but was not impressed by Ricci.",
      "This records Haskell's report of La Fosse's view; note 4's cited anecdote is pending.",
      [E["la_fosse"],E["ricci"]],speaker="Haskell reporting La Fosse's opinion",
      layer="authorial report of attributed opinion",footnote=4)
add_s("st-chp10-p284-watteau-at-crozat-house",172,172,E["watteau"],E["crozat_house"],
      "watteau_lived_in_crozats_house","Crozat’s latest discovery, the 32-year-old Antoine Watteau",
      "was living in his house,",
      "Haskell says the 32-year-old Antoine Watteau was living in Crozat's house.",
      "The age and residence are reported as Haskell's account; no external source is asserted.",
      [E["crozat"]],relation=True)
add_s("st-chp10-p284-ricci-copied-watteau-drawing",172,172,E["ricci"],C["watteau_sheet"],
      "ricci_copied_sheet_of_watteau_drawings","the elderly Venetian admired his work sufficiently to copy",
      "a sheet of his drawings.",
      "Haskell says Ricci admired Watteau's work enough to copy a sheet of Watteau's drawings.",
      "The specific sheet is unidentified; note 5 remains pending.",
      [E["watteau"]],relation=True,footnote=5)
add_s("st-chp10-p284-pellegrini-carriera-zanetti-visit",173,174,E["pellegrini"],E["france"],
      "pellegrini_carriera_zanetti_arrived_four_years_after_ricci","Four years after Ricci came his rival Pellegrini",
      "the engraver and connoisseur.",
      "Haskell says Pellegrini arrived four years after Ricci with his sister-in-law Rosalba Carriera and their common friend Antonio Maria Zanetti, described as an engraver and connoisseur.",
      "The interval is relative to Ricci's 1716 arrival; the source does not state an exact year in this sentence.",
      [E["ricci"],E["carriera"],E["zanetti"]],relation=True)
add_s("st-chp10-p284-peak-venetian-influence-france",174,174,E["pellegrini"],E["france"],
      "visit_marked_peak_of_venetian_influence_and_last_major_impact_in_france",
      "This visit, marked the peak of Venetian influence abroad","a serious impact on France.",
      "Haskell presents the visit as the peak of Venetian influence abroad and the last serious impact of contemporary Italian art in France.",
      "This is the author's periodizing assessment; the scan does not contain the OCR comma before 'marked'.",
      [E["pellegrini"],E["carriera"],E["zanetti"],E["france"]],layer="authorial interpretation")
add_s("st-chp10-p284-crozat-patronage-aristocratic-contact",174,174,E["crozat"],None,
      "crozat_patronage_connected_artists_to_aristocratic_society",
      "The aristocratic society, with which the three artists were at once brought into contact through the patronage of Crozat",
      "the apparently miraculous benefits that could be obtained from financial speculation.",
      "Haskell says Crozat's patronage brought the three artists into contact with aristocratic society amid post-Louis-XIV-death relaxation and financial speculation.",
      "The social and economic characterization is Haskell's account; period descriptions are not independently checked.",
      [E["pellegrini"],E["carriera"],E["zanetti"],E["louis_xiv"],E["crozat"]],
      layer="authorial interpretation with period description",relation=True)
add_s("st-chp10-p284-pellegrini-mississippi-commission",174,176,E["pellegrini"],C["mississippi_programme"],
      "pellegrini_assigned_mississippi_gallery_decoration",
      "Pellegrini was at once given the'task of decorating",
      "the headquarters of John Law’s reckless, but as yet successful,\nSystème.",
      "Haskell says Pellegrini was assigned the Mississippi Gallery decoration at the Banque Royale, headquarters of John Law's scheme, which he characterizes as reckless but still successful at the time.",
      "Assignment is not treated as proof the work was completed. Preserve Haskell's evaluation and temporal qualification.",
      [C["mississippi_gallery"],C["banque_royale"],E["john_law"],C["law_system"]],relation=True)
add_s("st-chp10-p284-mississippi-programme-open",175,176,E["pellegrini"],C["mississippi_programme"],
      "mississippi_gallery_programme_combined_royal_glorification_and_commerce_allegory",
      "The programme given to the artist represented a curious combination",
      "which were to become general only in the second half of the",
      "Haskell describes the programme as combining royal glorification in the Versailles manner with allegorical tributes to commerce, whose broader prevalence he dates only to the century's second half.",
      "The sentence is incomplete at p.284 and continues at p.285; retain as partial until the next segment is read.",
      [C["mississippi_programme"],E["louis_xiv"]],relation=True,
      cross=[{"segment_id":NEXT,"source_line_start":178,"source_line_end":188}])

# Close the p.283 Bellucci sentence with its p.284 continuation; keep the footnote for later.
previous_open = next((r for r in statements if r["statement_id"] == "st-chp10-p283-bellucci-celebrated-wilhelm-open"), None)
if not previous_open or previous_open["segment_id"] != PREV:
    raise SystemExit("expected open p.283 Bellucci statement missing")
previous_open["predicate"] = "bellucci_painted_allegories_and_group_portraits_for_wilhelm"
previous_open["qualifiers"]["claim"] = "Haskell says Bellucci celebrated Johann Wilhelm with allegories and group portraits, judged more clumsy than Pellegrini's; the p.284 continuation says they show Bellucci's early appreciation of Veronese."
previous_open["qualifiers"]["qualification"] = "Comparative and art-historical judgments are Haskell's; continuation is cross-referenced to p.284 L168."
previous_open["qualifiers"]["continuation_quote"] = "which show that he was among the earliest of the eighteenth-century Venetian artists to appreciate the example of Veronese."
previous_open["qualifiers"]["cross_reference_segments"] = [{"segment_id":SEG,"source_line_start":168,"source_line_end":168}]

if "p.284" not in cov[PREV]["note"]:
    raise SystemExit("p.283 coverage note no longer matches expected open continuation")
cov[PREV].update({"migration_status":"complete","source_line_ranges":"L151-165; p.284 L168",
 "note":"Printed p.283 body and footer read against CHP-10.pdf physical page 12. The Bellucci sentence ending 'but' is closed by p.284 L168 and cross-linked. The p.282 unnumbered footer fragment is also closed at p.283 L163-164. Notes 1-2 remain pending in the consolidated notes segment. S0 OCR is unchanged."})
cov[SEG].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L168-176",
 "note":"Printed p.284 read against CHP-10.pdf physical page 13. Closed the p.283 Bellucci comparison; recorded Pellegrini's Low Countries work, Amsterdam city-hall fresco commission and Haskell's first-Italian-artist claim; the 1719 Cadogan-house commission and Flanders service; Haskell's Paris framing, Ricci's 1716 move, Crozat's mansion/collection and hospitality, La Fosse's residence and view of Ricci, Watteau's residence and Ricci's copied drawing, and the later Pellegrini-Carriera-Zanetti visit and Mississippi Gallery commission/programme. Against print, S2 reads L169 '1716?' as the footnote marker after 1716; 'rime'->'time'; 'who -had'->'who had'; L172 'eopy'->'copy' and removes the stray OCR apostrophe after note 5; L174 removes the OCR comma in 'This visit, marked' and apostrophe in 'the'task'. S0 unchanged. Notes 1-5 at consolidated source L524-527 remain pending. L176 ends mid-sentence and continues at p.285 L178."})
cov[NEXT]["note"] = "Next source-order segment is printed p.285 at L178; close the p.284 Mississippi Gallery programme sentence before marking p.284 complete."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:]==["--apply"] else "DRY-RUN",
 "segment":SEG,"new_candidates":len(newc),"new_mentions":len(newm),"new_statements":len(new_s),
 "candidate_range":[newc[0]["candidate_id"],newc[-1]["candidate_id"]],
 "coverage":{"p283":cov[PREV]["migration_status"],"p284":cov[SEG]["migration_status"],"p285":cov[NEXT]["migration_status"]}},
 ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup = Path(str(path) + BACKUP)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[r["segment_id"]] for r in coverage])
    print("Applied p.284 S2 migration and closed p.283 Bellucci sentence; backups retained.")
