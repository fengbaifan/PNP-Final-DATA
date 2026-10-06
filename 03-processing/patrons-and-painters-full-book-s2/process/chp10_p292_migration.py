"""Controlled S2 migration for printed p.292; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l253-266"
SEG = "chp-10:10_CHP-10_intro:l268-277"
NEXT = "chp-10:10_CHP-10_intro:l279-290"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_SEG_SHA = "150905f8241e7adef0c58caaf16563464aff6e2aadee80629d184b574bff1aa4"
BACKUP = ".bak-s2-chp10-p292-reapply-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(src[267:277])
SEG_SHA = hashlib.sha256(body.encode("utf-8")).hexdigest()
if SEG_SHA != EXPECTED_SEG_SHA or src[267].strip() != "[Page 292]" or "Canaletti’s view all of one colour" not in body or "Royal\nAcademy" not in body:
    raise SystemExit("p.292 source segment/page mismatch")

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
if maximum != 9038:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")),
                      (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "amigoni": "cand-0102", "canaletto_mcswiny": "cand-0501", "canaletto_england": "cand-0528",
    "rosalba": "cand-0581", "george_iii": "cand-1141", "pellegrini": "cand-1865",
    "rowlandson": "cand-2291", "tessin": "cand-2552", "venice": "cand-2719",
    "watteau": "cand-2804", "zuccarelli": "cand-2879", "england": "cand-8983",
    "grand_tour": "cand-8989", "mcswiny": "cand-1466", "royal_bank": "cand-8965",
    "stockholm": "cand-4790", "europe": "cand-3462",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
for key, cid, page, sub in (
    ("amigoni", E["amigoni"], "286, 287, 292", "work in England"),
    ("canaletto_england", E["canaletto_england"], "292", "work in England"),
    ("george_iii", E["george_iii"], "292, 300, 303, 309, 361, 393, 406", ""),
    ("pellegrini", E["pellegrini"], "284, 285, 292", "Mississippi Gallery of Banque Royale"),
):
    row = next(row for row in candidates if row["candidate_id"] == cid)
    if row["index_page_range"] != page or row["sub_entry"] != sub:
        raise SystemExit(f"unexpected page-specific index candidate {key}={cid}")

NEW_SPECS = [
    ("burney", "Dr Burney (musicologist quoted about Venice in 1770; identity pending)", "person",
     "Haskell identifies the quoted observer as Dr Burney, a musicologist, but this passage gives no first name. Resolve identity in S3; keep his 1770 Venice observation as reported testimony.", 270),
    ("beckford", "William Beckford (writer quoted about Venice; identity pending)", "person",
     "Named as a later observer who wrote rhapsodically about Venice's mystery and decay and nevertheless praised its depiction by Canaletto. The passage supplies no dates or work title.", 270),
    ("war_1740", "Unnamed war in Europe in 1740 that reduced English travel", "event",
     "Haskell says a war in Europe in 1740 greatly reduced English travellers to the Continent; the passage does not name the war, so do not identify it by inference.", 271),
    ("english_travellers", "English travellers to the Continent in 1740 (unnamed group)", "term",
     "Collective travellers whose numbers Haskell says were reduced by an unnamed war in 1740. Do not collapse this broader group into the noblemen described in the Grand Tour passage.", 271),
    ("canaletto_pupils", "Canaletto's unnamed pupils who produced views for Grand Tour visitors", "term",
     "Collective reference to unnamed pupils whose views, alongside the master's, were brought home by Grand Tour noblemen; no pupil or individual work is identified.", 269),
    ("tour_noblemen", "Noblemen who brought home Canaletto or pupils' views from the Grand Tour", "term",
     "Unnamed group in Haskell's account of the Grand Tour market for Venetian views; the passage does not identify individual travellers or itineraries.", 269),
    ("grand_tour_views", "Sets of Venetian views by Canaletto or his pupils brought back on the Grand Tour", "work",
     "Unspecified group of views brought back by Grand Tour noblemen. Haskell allows that they were by Canaletto or his pupils; no titles, number, or individual attribution is supplied.", 269),
    ("english_viewers", "English generations who saw Venice through Canaletto's views", "term",
     "Collective audience described by Haskell across several generations. Burney and Beckford are presented as different responses; do not treat the group as a named organization.", 269),
    ("burney_view", "Unidentified Canaletto view of Venice described by Burney as all one colour", "work",
     "An unnamed view that Burney says shaped his expectations of Venice. The passage gives no title, date, or present location; the quoted spelling 'Canaletti' is retained in the source layer.", 270),
    ("canaletto_english_series", "Canaletto's series of London views and English country-house paintings", "work",
     "Collective body of views and country-house paintings made during Canaletto's English stay. No individual titles or houses are identified in this passage; Plate 51 is a cross-reference, not a complete inventory.", 272),
    ("canaletto_english_clients", "English dukes and enthusiastic amateurs who patronized Canaletto", "term",
     "Unnamed client group for Canaletto's English views and country-house paintings. The passage identifies George III separately in its account of Zuccarelli's clients.", 272),
    ("royal_academy", "Royal Academy (London; institutional identity pending)", "institution",
     "The passage says Zuccarelli became a founder member of the Royal Academy but does not state the full formal name; align the institution in S3.", 275),
    ("french_collectors", "French collectors of contemporary Italian art (unnamed group)", "term",
     "Collective audience in Haskell's claim about French interest after 1724, with Rosalba Carriera as the stated exception. No individual collectors are named.", 277),
    ("french_artists", "French artists in Haskell's account of Italian artistic influence (unnamed group)", "term",
     "Collective artists whom Haskell says received an impulse from Italian art. Do not assume they are identical to the unnamed French collectors.", 277),
    ("italian_artists", "Italian artists whose art supplied an impulse to French artists (unnamed group)", "term",
     "Collective Italian artists in Haskell's account of cross-national influence; no individual artist or work is specified in this claim.", 277),
    ("pellegrini_ceiling", "Giovanni Antonio Pellegrini's ceiling for the Banque Royale (destroyed 1724)", "work",
     "A ceiling work reported destroyed in 1724. The passage gives no title, image program, or room name; keep it distinct from Pellegrini's Mississippi Gallery commission.", 277),
    ("tessin_father", "Unnamed architect, father of Count Tessin, who built the Royal Palace in Stockholm", "person",
     "The passage identifies this person only by his architectural role and relationship to Count Tessin; do not supply a name without S3 evidence.", 277),
    ("stockholm_palace", "Royal Palace in Stockholm (building named in the Tessin passage)", "place",
     "Building said by Haskell to have been built by Count Tessin's father. It is distinct from Stockholm as a city and from institutions located there.", 277),
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
                 "candidate_source_ref": f"{SEG}#L{line}"})

offsets, offset = {}, 0
for line in range(268, 278):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p292-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
        raise SystemExit(f"missing candidate for {mid}: {cid}")
    line_start, line_end = offsets[line], offsets[line] + len(src[line - 1])
    positions, at = [], line_start
    while True:
        at = body.find(surface, at)
        if at < 0 or at >= line_end:
            break
        positions.append(at)
        at += max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent L{line}: {surface!r}; occurrences={len(positions)}")
    start = positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTIONS = [
    ("commission-canaletto",269,"pictures by Canaletto",E["canaletto_england"],"Closes the p.291 sentence about McSwiny's commission; map to the page-specific index entry for Canaletto's English work."),
    ("mcswiny-coreference",269,"he was for once fully in touch",E["mcswiny"],"Pronoun continues the subject McSwiny from p.291; this segment closes the cross-page sentence."),
    ("english-clients",269,"English clients",C["canaletto_english_clients"],"Group left unnamed by the source."),
    ("grand-tour",269,"Grand Tour",E["grand_tour"],"The already registered travel practice."),
    ("tour-noblemen",269,"noblemen",C["tour_noblemen"],"Unnamed travellers; no individuals or itineraries inferred."),
    ("tour-views",269,"their sets of views",C["grand_tour_views"],"Collective views brought home; the passage allows works by the master or pupils."),
    ("tour-master",269,"the master",E["canaletto_england"],"Corefers to Canaletto."),
    ("tour-pupils",269,"his pupils",C["canaletto_pupils"],"Unnamed collective; no individuals inferred."),
    ("market-canaletto",269,"Canaletto",E["canaletto_england"],"Subject of the market and price account."),
    ("englishmen-generations",269,"Several generations of Englishmen",C["english_viewers"],"Collective reception group, not a named organization."),
    ("venice",269,"Venice",E["venice"],"City viewed through Canaletto's paintings."),
    ("his-eyes",269,"his eyes",E["canaletto_england"],"Metaphor for Canaletto's views; corefers to the artist."),
    ("burney",270,"Burney",C["burney"],"The quoted observer is identified only as Dr Burney here."),
    ("burney-city",270,"there",E["venice"],"Corefers to Venice."),
    ("burney-city-description",270,"this city",E["venice"],"Corefers to Venice in Burney's quotation."),
    ("burney-view",270,"Canaletti’s view all of one colour",C["burney_view"],"Exact source spelling is retained; work identity and title are unspecified."),
    ("burney-canaletto",270,"Canaletti’s",E["canaletto_england"],"Source spelling inside the quotation; aligned to the Canaletto candidate without correcting the quote."),
    ("beckford",270,"William Beckford",C["beckford"],"Named later observer; identity alignment remains S3."),
    ("beckford-venice",270,"the city",E["venice"],"Corefers to Venice."),
    ("beckford-canaletto",270,"Canaletti",E["canaletto_england"],"Printed form inside Beckford's quoted phrase."),
    ("war",271,"war in Europe",C["war_1740"],"Unnamed event; no named war inferred."),
    ("english-travelers",271,"English travellers to the Continent",C["english_travellers"],"Broad group in Haskell's account; individual travellers are not specified."),
    ("canaletto-to-england",271,"Canaletto",E["canaletto_england"],"Subject of the move to England."),
    ("this-country",271,"this country",E["england"],"Corefers to England."),
    ("amigoni",272,"Amigoni",E["amigoni"],"Mapped to the page-specific index entry for work in England."),
    ("amigoni-english-taste",272,"gauging English taste",E["england"],"Context for Amigoni's encouragement of Canaletto."),
    ("canaletto-he-moved",272,"He moved",E["canaletto_england"],"Pronoun corefers to Canaletto."),
    ("series",272,"a series of London views and country houses",C["canaletto_english_series"],"Collective body of work; individual works and houses are not named."),
    ("english-patrons",272,"dukes and enthusiastic amateurs",C["canaletto_english_clients"],"Unnamed client group."),
    ("england-here",272,"here",E["england"],"Corefers to England."),
    ("rowlandson",272,"Thomas Rowlandson",E["rowlandson"],"Named satirist who later adapted Canaletto's shorthand."),
    ("zuccarelli",273,"Francesco Zuccarelli",E["zuccarelli"],"Named landscape painter."),
    ("zuccarelli-england",274,"England",E["england"],"Destination and residence in the career account."),
    ("george-iii-ocr",274,"George HI",E["george_iii"],"S0 OCR reads HI; the printed scan confirms George III. Preserve the OCR surface and record correction in S2 only."),
    ("royal-academy",274,"Royal\nAcademy",C["royal_academy"],"Line-break-spanning mention; full institutional identity deferred to S3."),
    ("canaletto-cultural-shift",276,"Canaletto",E["canaletto_england"],"First artist in the contrast."),
    ("zuccarelli-cultural-shift",276,"Zuccarelli",E["zuccarelli"],"Second artist in the contrast."),
    ("england-cultural-shift",276,"England",E["england"],"National context in the taste comparison."),
    ("europe",276,"Europe",E["europe"],"Broader European setting of the change in taste."),
    ("pellegrini-ceiling",277,"Pellegrini’s ceiling for the Banque Royale",C["pellegrini_ceiling"],"Distinct work from the Mississippi Gallery decoration."),
    ("banque-royale",277,"Banque Royale",E["royal_bank"],"The bank, distinguished from its Mississippi Gallery space."),
    ("rosalba",277,"Rosalba",E["rosalba"],"Index candidate identifies Rosalba Carriera; retain the short source form."),
    ("french-collectors",277,"French collectors",C["french_collectors"],"Unnamed collective group."),
    ("french-artists",277,"the French",C["french_artists"],"Collective artists in Haskell's account of artistic influence."),
    ("italian-artists",277,"the Italians",C["italian_artists"],"Collective source wording in the account of artistic influence; no individuals inferred."),
    ("french-native-artists",277,"their own native artists",C["french_artists"],"Corefers to French artists; distinct from the collectors."),
    ("tessin",277,"Count Tessin",E["tessin"],"Page-specific index candidate for Count Carl Gustav Tessin."),
    ("swede",277,"a Swede",E["tessin"],"Corefers to Count Tessin."),
    ("tessin-father",277,"the architect",C["tessin_father"],"Unnamed father; no identity inferred."),
    ("royal-palace",277,"the Royal Palace in Stockholm",C["stockholm_palace"],"Building distinguished from Stockholm city."),
    ("stockholm",277,"Stockholm",E["stockholm"],"City location; separate from the palace building."),
    ("tessin-birth",277,"He",E["tessin"],"Pronoun corefers to Count Tessin."),
    ("watteau",277,"Watteau",E["watteau"],"Antoine Watteau; page-specific index candidate."),
    ("tessin-political",277,"he",E["tessin"],"Pronoun corefers to Count Tessin; the clause remains open at the page end."),
]
for item in MENTIONS:
    add_m(*item)

new_s = []


def quote(start, end):
    first = body.find(start)
    if first < 0:
        raise SystemExit(f"quote start absent: {start!r}")
    last = body.find(end, first)
    if last < 0:
        raise SystemExit(f"quote end absent: {end!r}")
    return body[first:last + len(end)]


def add_s(sid, lo, hi, subject, obj, predicate, start, end, claim, qualification,
          mentioned, speaker="Haskell", layer="authorial narrative", relation=False,
          footnote=None, cross=None):
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement: {sid}")
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 292,
                  "pdf_physical_page": 21, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": mentioned, "relation_candidate": relation}
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
        qualifiers["footnote_text_pending"] = True
    if cross:
        qualifiers["cross_reference_segments"] = cross
    new_s.append({"statement_id": sid, "segment_id": SEG,
                  "subject_candidate_id": subject, "object_candidate_id": obj,
                  "predicate": predicate, "qualifiers": qualifiers,
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE, "origin": "book"})


add_s("st-chp10-p292-grand-tour-views",269,269,C["tour_noblemen"],C["grand_tour_views"],
      "grand_tour_noblemen_brought_home_sets_of_views_by_canaletto_or_his_pupils",
      "On the Grand Tour noblemen regularly", "his pupils.",
      "Haskell says Grand Tour noblemen regularly brought home sets of views by Canaletto or his pupils.",
      "The passage leaves the travellers, pupils, and individual views unnamed; it does not say that every view was painted by Canaletto.",
      [C["tour_noblemen"],C["grand_tour_views"],E["canaletto_england"],C["canaletto_pupils"],E["grand_tour"]],relation=True)
add_s("st-chp10-p292-mcswiny-canaletto-commission",269,269,E["mcswiny"],E["canaletto_england"],
      "mcswiny_commissioned_canaletto_pictures_for_english_clients",
      "pictures by Canaletto", "national taste.",
      "The sentence begun on p.291 says McSwiny commissioned Canaletto pictures for English clients and, in doing so, was fully in touch with national taste.",
      "The subject and commission context continue from p.291 L266; the quoted source span here remains within p.292 coverage.",
      [E["mcswiny"],E["canaletto_england"],C["canaletto_english_clients"]],relation=True,cross=[PREV])
add_s("st-chp10-p292-canaletto-market",269,269,E["canaletto_england"],C["english_viewers"],
      "canaletto_used_steady_english_demand_to_raise_prices_and_was_seen_as_spoilt_by_english_patronage",
      "Canaletto took full advantage", "spoilt by the English.",
      "Haskell says Canaletto took advantage of steady demand, raised his prices until he was inaccessible to others, and acquired a reputation for being spoiled by English clients.",
      "This is Haskell's characterization; the source's evaluative phrase is not an independently measured market finding.",
      [E["canaletto_england"],C["english_viewers"],C["canaletto_english_clients"]],layer="authorial report and evaluation",relation=True,footnote=1)
add_s("st-chp10-p292-english-reception",269,269,C["english_viewers"],E["venice"],
      "several_generations_of_englishmen_saw_venice_through_canalettos_views",
      "Several generations of Englishmen", "his eyes,",
      "Haskell says several generations of Englishmen saw Venice through Canaletto's eyes, sometimes with surprising results.",
      "The phrase describes the reach of the images, not exclusive or uniform English reception.",
      [C["english_viewers"],E["venice"],E["canaletto_england"]],layer="authorial interpretation")
add_s("st-chp10-p292-burney-testimony",269,270,C["burney"],C["burney_view"],
      "burney_says_a_canaletto_view_shaped_expectations_of_venice_that_did_not_match_its_architectural_variety",
      "When Dr\nBurney", "ages, and materials.",
      "Burney says romantic expectations of Venice did not match what he encountered, particularly after seeing a Canaletto view rendered in one colour; he found the city composed of varied buildings, architectural orders, ages, and materials.",
      "Reported first-person testimony quoted by Haskell; preserve Canaletti's spelling in the quotation. Note 2 remains to be migrated from the consolidated notes source.",
      [C["burney"],C["burney_view"],E["venice"],E["canaletto_england"]],speaker="Burney quoted by Haskell",layer="quoted testimony",footnote=2)
add_s("st-chp10-p292-beckford-testimony",270,270,C["beckford"],E["canaletto_england"],
      "beckford_found_venice_perfectly_depicted_by_canaletto_despite_its_mystery_and_decay",
      "Many years later William Beckford", "‘the pencil of Canaletti’.3",
      "Haskell says that William Beckford, despite rhapsodizing about Venice's mystery and decay, found it perfectly depicted by Canaletto.",
      "This is Haskell's report of Beckford's response; the cited text remains pending note migration and is not independently checked.",
      [C["beckford"],E["venice"],E["canaletto_england"]],speaker="Haskell reporting Beckford",layer="reported response",footnote=3)
add_s("st-chp10-p292-war-and-canaletto-move",271,272,C["war_1740"],E["canaletto_england"],
      "war_in_europe_reduced_english_travel_and_canaletto_came_to_england_encouraged_by_amigoni",
      "When in 1740 war in Europe", "English taste.",
      "Haskell says a war in Europe in 1740 greatly reduced English travel to the Continent, after which Canaletto found it necessary to come to England, encouraged by Amigoni.",
      "The war is unnamed; do not identify it as a specific conflict. The source gives a causal narrative but no additional evidence here.",
      [C["war_1740"],C["english_travellers"],E["canaletto_england"],E["england"],E["amigoni"]],speaker="Haskell",layer="authorial report",relation=True)
add_s("st-chp10-p292-amigoni-english-taste",272,272,E["amigoni"],E["england"],
      "amigoni_had_extensive_opportunity_to_gauge_english_taste",
      "Amigoni, who had had plenty", "English taste.",
      "Haskell says Amigoni had had plenty of opportunity to gauge English taste.",
      "The passage gives this as context for Amigoni's encouragement of Canaletto, without identifying specific works or clients.",
      [E["amigoni"],E["england"]],layer="authorial report")
add_s("st-chp10-p292-canaletto-english-commissions",272,272,E["canaletto_england"],C["canaletto_english_clients"],
      "canaletto_painted_london_views_and_country_houses_for_english_dukes_and_amateurs",
      "He moved throughout the land", "(Plate 51).4",
      "Haskell says Canaletto travelled through England painting London views and country houses for dukes and enthusiastic amateurs who welcomed him.",
      "The individual houses, works, and patrons are unnamed. Plate 51 is a cross-reference; footnote 4 remains pending migration.",
      [E["canaletto_england"],C["canaletto_english_series"],C["canaletto_english_clients"],E["england"]],relation=True,footnote=4)
add_s("st-chp10-p292-canaletto-reception",272,272,C["canaletto_english_clients"],E["canaletto_england"],
      "english_clients_welcomed_canaletto_despite_denigration_by_rivals_and_patriots",
      "who welcomed him", "boisterous patriots",
      "Haskell contrasts the welcome Canaletto received from dukes and enthusiastic amateurs with denigration by jealous rivals and boisterous patriots.",
      "The opposing groups are left unnamed; the phrasing is Haskell's characterization and is not a count of public opinion.",
      [C["canaletto_english_clients"],E["canaletto_england"]],layer="authorial report and evaluation")
add_s("st-chp10-p292-canaletto-late-manner",272,272,E["canaletto_england"],None,
      "canaletto_remained_in_england_nearly_ten_years_with_breaks_and_his_manner_grew_mechanical",
      "With short breaks he remained here", "increasingly mechanical,",
      "Haskell says Canaletto remained in England for nearly ten years with short breaks and that his manner became increasingly mechanical.",
      "The duration is approximate and the stylistic description is Haskell's assessment.",
      [E["canaletto_england"],E["england"]],layer="authorial report and evaluation")
add_s("st-chp10-p292-rowlandson-adaptation",272,272,E["canaletto_england"],E["rowlandson"],
      "rowlandson_later_adapted_canalettos_shorthand_figures_for_comic_purpose",
      "his shorthand of little blobs", "Thomas Rowlandson.",
      "Haskell says Thomas Rowlandson later adapted Canaletto's shorthand figures to brilliant comic purpose.",
      "The passage describes adaptation of a figure convention; it does not identify a particular Rowlandson work.",
      [E["canaletto_england"],E["rowlandson"]],relation=True)
add_s("st-chp10-p292-zuccarelli-career",273,274,E["zuccarelli"],E["england"],
      "zuccarelli_arrived_in_england_in_1752_and_stayed_over_fifteen_years_with_one_three_year_break",
      "The career of the landscape painter Francesco Zuccarelli", "one break of three.",
      "Haskell calls Zuccarelli's career even more successful, says he arrived in England in 1752, and reports that he remained for over fifteen years with one three-year break.",
      "The value judgment and approximate duration are attributed to Haskell. Note 5 remains pending migration from the consolidated notes.",
      [E["zuccarelli"],E["england"]],speaker="Haskell",layer="authorial report and evaluation",relation=True,footnote=5)
add_s("st-chp10-p292-zuccarelli-clients-academy",274,275,E["zuccarelli"],C["royal_academy"],
      "zuccarelli_had_george_iii_among_his_clients_and_became_a_founder_member_of_the_royal_academy",
      "His clients included George HI", "Academy.",
      "Haskell says Zuccarelli's clients included George III and that he became a founder member of the Royal Academy.",
      "The scan confirms George III where the OCR reads 'HI'; the institution's formal identity remains for S3.",
      [E["zuccarelli"],E["george_iii"],C["royal_academy"]],relation=True)
add_s("st-chp10-p292-taste-break",276,276,None,None,
      "canaletto_and_zuccarellis_triumphs_symbolize_a_break_in_taste_between_england_and_continent",
      "The triumphs of Canaletto and Zuccarelli", "the Continent.",
      "Haskell presents Canaletto's and Zuccarelli's successes as symbolic of a complete break in artistic taste between England and the Continent, while noting broader changes in Europe after the second decade of the eighteenth century.",
      "This is Haskell's historical interpretation, not a quantified measure of taste.",
      [E["canaletto_england"],E["zuccarelli"],E["england"],E["europe"]],layer="authorial interpretation")
add_s("st-chp10-p292-pellegrini-ceiling-destroyed",276,277,C["pellegrini_ceiling"],None,
      "pellegrinis_banque_royale_ceiling_was_destroyed_in_1724",
      "In 1724\nPellegrini’s ceiling", "was destroyed,",
      "Haskell reports that Pellegrini's ceiling for the Banque Royale was destroyed in 1724.",
      "No title, subject, or precise room is supplied; keep this work distinct from the Mississippi Gallery decoration.",
      [C["pellegrini_ceiling"],E["pellegrini"],E["royal_bank"]])
add_s("st-chp10-p292-french-collectors",277,277,C["french_collectors"],E["rosalba"],
      "contemporary_italian_art_had_little_interest_for_french_collectors_except_rosalba",
      "thereafter, with the exception of Rosalba", "French collectors.",
      "Haskell says that after the ceiling's destruction contemporary Italian art attracted little interest from French collectors, with Rosalba as the exception.",
      "This is a broad historical generalization by Haskell; it does not identify individual collectors or quantify interest.",
      [C["french_collectors"],E["rosalba"]],speaker="Haskell",layer="authorial interpretation")
add_s("st-chp10-p292-french-adoption",277,277,C["french_artists"],C["italian_artists"],
      "french_artists_took_enough_from_italian_art_to_stimulate_their_own_artists",
      "the French had taken just enough", "their own native artists.",
      "Haskell says the French had taken enough from Italian art to provide an impulse for their own artists.",
      "The comparison is Haskell's historical interpretation and does not identify particular French artists or works.",
      [C["french_artists"],C["italian_artists"]],layer="authorial interpretation")
add_s("st-chp10-p292-tessin-family-and-palace",277,277,C["tessin_father"],C["stockholm_palace"],
      "count_tessin_was_swedish_and_his_unnamed_architect_father_built_the_royal_palace_in_stockholm",
      "Count Tessin was a Swede", "Royal Palace in Stockholm.",
      "Haskell identifies Count Tessin as Swedish and as the son of the architect who built the Royal Palace in Stockholm.",
      "The architect is unnamed in this passage; building and city are recorded separately. Note 6 remains pending migration.",
      [E["tessin"],C["tessin_father"],C["stockholm_palace"],E["stockholm"]],relation=True,footnote=6)
add_s("st-chp10-p292-tessin-early-travel",277,277,E["tessin"],E["watteau"],
      "tessin_was_born_in_1695_travelled_between_1714_and_1719_and_first_met_watteau_during_those_travels",
      "He was born in 1695", "Watteau.",
      "Haskell says Tessin was born in 1695, travelled between 1714 and 1719, and first came into contact with Watteau during those travels.",
      "The source's OCR reads 'bis early travels'; the printed scan reads 'his'. The correction belongs in S2 and does not alter S0.",
      [E["tessin"],E["watteau"]],layer="authorial report",relation=True,footnote=6)
add_s("st-chp10-p292-tessin-political-importance-open",277,277,E["tessin"],None,
      "tessin_later_achieved_great_political_importance_clause_continues_on_p293",
      "A few years later he achieved", "in his",
      "Haskell begins a claim that Tessin achieved great political importance a few years later.",
      "The sentence ends mid-phrase at 'in his' and must be completed from p.293 before the claim's scope or setting is settled.",
      [E["tessin"]],layer="authorial narrative",footnote=6,cross=[NEXT])

cov[PREV].update({"migration_status":"complete", "source_line_ranges":"L254-266",
                  "note":"Printed p.291 was checked against CHP-10.pdf physical page 20. The final McSwiny commission sentence is now closed by p.292 L269 and recorded as a cross-segment statement; the p.292 continuation is linked. Footnotes 1-3 remain pending in the consolidated notes segment but do not duplicate into the body tables."})
cov[SEG].update({"disposition":"reviewed", "migration_status":"partial", "source_line_ranges":"L268-277",
                 "note":"Printed p.292 was checked against CHP-10.pdf physical page 21. Closed p.291's McSwiny commission sentence; recorded Grand Tour demand for Canaletto/pupils' Venetian views, the English reception and pricing narrative, Burney and Beckford as attributed testimony, the unnamed 1740 war and Amigoni's encouragement, Canaletto's English commissions and Rowlandson's adaptation, Zuccarelli's English career and Royal Academy membership, Haskell's taste-change interpretation, the 1724 destruction of Pellegrini's Banque Royale ceiling, French interest in contemporary Italian art, and Tessin's early biography. Unnamed people, groups, works, and building are retained without guessed identities; 'George HI', 'bis', and the OCR footnote marker 6 following Zuccarelli (printed 5) were checked against the scan and corrected only in S2. Footnotes 1-6 remain pending migration from the consolidated notes. Tessin's final sentence ends at 'in his' and continues on p.293, so this segment remains partial."})
cov[NEXT]["note"] = "Next source-order segment is printed p.293 at L279-290; it continues the open Tessin sentence at p.292 L277. Footnotes 1-6 printed on p.292 remain in the consolidated notes segment."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"segment_sha256":SEG_SHA,"new_candidates":len(newc),
                  "candidate_ids":[row["candidate_id"] for row in newc],"new_mentions":len(newm),
                  "new_statements":len(new_s),"coverage":{"p291":cov[PREV]["migration_status"],
                  "p292":cov[SEG]["migration_status"],"p293":cov[NEXT]["migration_status"]}},
                 ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.292 S2 migration; p.292 remains partial pending p.293 and consolidated notes.")
