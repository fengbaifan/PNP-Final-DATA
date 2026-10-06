"""Controlled S2 migration for printed p.286; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l178-188"
SEG = "chp-10:10_CHP-10_intro:l190-204"
NEXT = "chp-10:10_CHP-10_intro:l206-216"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "4690eee7aca37d3bf859d70d2adcd571b736e7b9b7c1a29611a334a7e23648a9"
BACKUP = ".bak-s2-chp10-p286-20261002"


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
body = "\n".join(src[189:204])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != SEG_SHA or src[189].strip() != "[Page 286]":
    raise SystemExit("p.286 source segment hash/page mismatch")

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
if maximum != 8982:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")), (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "galilei": "cand-1104", "hampton_court": "cand-7212", "halifax": "cand-1286",
    "ricci": "cand-2154", "burlington": "cand-0470", "vicenza": "cand-2769",
    "amigoni": "cand-0094", "belleucci": "cand-0282", "tankerville": "cand-2540",
    "james_ii": "cand-1317", "powis": "cand-2031", "styles": "cand-2531",
    "thornhill": "cand-2568", "leoni": "cand-1394",
    "london": "cand-1422", "europe": "cand-3462", "italy": "cand-3461",
    "old_masters": "cand-4288", "history_painting": "cand-4630",
    "venetian_artists": "cand-8104",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("england", "England", "place", "Geographic setting of the national taste discussed in this passage.", 191),
    ("st_pauls_dome", "Dome of St Paul's named as a site for Thornhill's painting", "place", "The spatial dome is distinguished from the painting applied to it.", 194),
    ("st_pauls_dome_work", "Thornhill's painting of the dome of St Paul's", "work", "An unnamed dome-painting commission; no title or completion date is supplied here.", 194),
    ("queens_bed_chamber", "Queen's Bed Chamber at Hampton Court", "place", "Room named as the site of a ceiling commission.", 194),
    ("queens_ceiling", "Ceiling decoration of the Queen's Bed Chamber at Hampton Court", "work", "The ceiling commission was intended for Ricci but assigned to Thornhill after Halifax's objection; no title is given.", 195),
    ("grand_tour_practice", "Grand Tour as a habitual English travel practice", "procedure", "Haskell presents the Grand Tour as customary and links it to changing English taste; no individual itinerary is implied.", 196),
    ("english_treasury", "Treasury responsible for the Hampton Court commission (identity pending)", "institution", "The Treasury is said to have threatened non-payment; its precise institutional identity is not specified.", 195),
    ("tankerville_staircase", "Amigoni's staircase decoration for Lord Tankerville", "work", "An unnamed staircase painting later pulled down; the residence is not identified in this passage.", 198),
    ("prince_of_wales", "Prince of Wales served by Lord Tankerville (identity pending)", "person", "Title-only reference; the individual is not identified in this passage.", 198),
    ("whig_group", "Whig political group in England", "institution", "Political affiliation named for Tankerville; do not infer a specific organization or membership list.", 197),
    ("powis_house", "Powis House in Great Ormond Street", "place", "The named house is treated as a building, distinct from its decoration and later tenancy.", 199),
    ("great_ormond_street", "Great Ormond Street", "place", "Named street locating Powis House; no further address is supplied.", 199),
    ("powis_decoration", "Amigoni's Seasons and Judith and Holofernes decoration at Powis House", "work", "Haskell describes a ceiling, walls and staircase with these subjects; whether Lord Powis was the patron remains explicitly uncertain.", 200),
    ("house_of_lords", "House of Lords", "institution", "Parliamentary institution in which Lord Powis was summoned to take his seat.", 201),
    ("tory_group", "Tory political group in England", "institution", "Political group with which Lord Powis sat; no specific organization is identified.", 201),
    ("jacobite_alarm", "Jacobite alarm of 1715", "event", "The event is named as the occasion of Lord Powis's last arrest in Haskell's account.", 200),
    ("french_ambassador", "Unidentified French ambassador who occupied Powis House", "person", "Role-only occupant during the tenancy preceding the fire; personal identity is not stated.", 200),
    ("powis_french_king", "King of France associated with rebuilding Powis House (identity pending)", "person", "The king is unnamed in Haskell's account of the house rebuilding around 1720; keep distinct from other unnamed French kings in different periods.", 200),
    ("south_sea_bubble", "South Sea Bubble", "event", "Named financial event from which Styles is said to have made his fortune.", 202),
    ("moor_park", "Moor Park country house", "place", "Styles's country house, distinct from its decoration.", 203),
    ("moor_park_decoration", "Unidentified decoration commission for Styles's Moor Park house", "work", "The job intended for Thornhill and later assigned elsewhere; the next page identifies the recipients and canvases.", 204),
]
newc, C = [], {}
next_candidate_number = maximum + 1
for key, name, kind, detail, line in NEW_SPECS:
    if next_candidate_number == maximum + 2:
        next_candidate_number += 1  # cand-8984 is reused from the existing Venetian artists category.
    number = next_candidate_number
    next_candidate_number += 1
    cid = f"cand-{number:04d}"
    if cid in cids or any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate already exists: {cid} {name}")
    C[key] = cid
    newc.append({"candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
                 "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
                 "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
                 "candidate_source_ref": f"{SEG}#L{line}"})

line_offsets = {}
offset = 0
for line in range(190, 205):
    line_offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, candidate, note="", occurrence=0):
    mid = f"m-chp10-p286-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention {mid}")
    text = src[line - 1]
    start_at = -1
    for _ in range(occurrence + 1):
        start_at = text.find(surface, start_at + 1)
        if start_at < 0:
            raise SystemExit(f"mention text not found at L{line}: {surface!r}")
    cid = C[candidate] if candidate in C else E[candidate] if candidate in E else candidate
    if cid not in cids and cid not in {row["candidate_id"] for row in newc}:
        raise SystemExit(f"mention references missing candidate: {local}={cid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid, "surface_form": surface,
                 "start_char": str(line_offsets[line] + start_at),
                 "end_char": str(line_offsets[line] + start_at + len(surface)), "note": note})


MENTIONS = [
    ("europe",191,"Europe","europe","Geographic frame of Haskell's generalization."),
    ("galilei",191,"Alessandro Galilei","galilei","Named speaker in Haskell's report."),
    ("england_1",191,"England","england","Geographic setting, not a claim by the English state."),
    ("italy",192,"Italy","italy","Geographic comparison in Galilei's reported remark."),
    ("st_pauls",194,"St Paul","st_pauls_dome","The dome is the painting site; not the painting itself."),
    ("thornhill_1",194,"Thornhill","thornhill","Painter assigned the dome work."),
    ("venetian_artists",194,"Venetian artists","venetian_artists","Collective category, not a formal institution."),
    ("queens_room",194,"Queen","queens_bed_chamber","Title within the room name; identity of the queen is not needed here."),
    ("hampton",195,"Hampton Court","hampton_court","Named site of the chamber."),
    ("halifax",195,"Earl of Halifax","halifax","Named speaker in the funding dispute."),
    ("treasury",195,"Treasury","english_treasury","English institution inferred from immediate context; precise institutional identity remains pending."),
    ("ricci",195,"Sebastiano Ricci","ricci","Artist initially intended for the commission."),
    ("burlington",195,"Lord Burlington","burlington","Promoter of the architectural style described."),
    ("vicenza",196,"Vicenza","vicenza","City named as Burlington's return point."),
    ("grand_tour",196,"Grand Tour","grand_tour_practice","Customary practice, not Burlington's earlier individual tour."),
    ("history_painting",196,"history painting","history_painting","Genre in Haskell's account of English taste."),
    ("old_master",196,"Old Master","old_masters","Category contrasted with contemporary large-scale history painters."),
    ("amigoni_arrival",197,"Amigoni","amigoni","Artist whose career is used as evidence of changing taste."),
    ("belleucci",197,"Bellucci","belleucci","His departure provides the approximate comparison date."),
    ("tankerville_title",197,"Lord","tankerville","Title begins the patron's name across the page line break."),
    ("whig",198,"Whig","whig_group","Political affiliation, not a formal patronage relation."),
    ("tankerville_surname",198,"Tankerville","tankerville","Surname continues the split name from p.286 L197."),
    ("amigoni_tankerville",198,"Amigoni","amigoni","Artist welcomed by Tankerville."),
    ("prince_wales",198,"Prince of Wales","prince_of_wales","Title-only office; individual identity left pending."),
    ("tankerville_staircase",198,"staircase","tankerville_staircase","Unidentified staircase decoration commissioned from Amigoni."),
    ("powis_house_1",199,"Powis House","powis_house","Building named as the location of Amigoni's decoration."),
    ("great_ormond",199,"Great Ormond","great_ormond_street","Street name begins here; candidate records the full named street."),
    ("great_ormond_street_cont",200,"Street","great_ormond_street","Street name continues across the source line break."),
    ("seasons",200,"the Seasons","powis_decoration","Iconographic subject within the Powis House programme, not the generic Four Seasons term."),
    ("judith_holofernes",200,"Judith and Holofernes","powis_decoration","Narrative subject within the same described decoration programme."),
    ("lord_powis_1",200,"Lord Powis","powis","Named owner and possible, not confirmed, patron."),
    ("james_ii",200,"James H","james_ii","OCR reads H; print scan confirms James II."),
    ("jacobite_alarm",200,"Jacobite alarm of 1715","jacobite_alarm","Named occasion of the last arrest described."),
    ("powis_house_great_house",200,"great house","powis_house","Anaphoric reference to Powis House during the ambassador's tenancy."),
    ("french_ambassador",200,"French Ambassador","french_ambassador","Role-only occupant; individual identity is not stated."),
    ("king_france",200,"King-of France","powis_french_king","Print reads 'King of France'; OCR includes a stray hyphen, and the monarch's identity remains pending."),
    ("house_lords",200,"House of","house_of_lords","Phrase continues as House of Lords on the next line."),
    ("house_lords_cont",201,"Lords","house_of_lords","Institution name continues after 'House of'."),
    ("tories",201,"Tories","tory_group","Political group among whom Powis sat."),
    ("amigoni_conditional",201,"Amigoni","amigoni","In the explicitly conditional patronage claim."),
    ("lord_powis_2",201,"he","powis","The pronoun in 'If he was the patron' refers to Lord Powis."),
    ("amigoni_patron",201,"Amigoni","amigoni","Begins the next sentence's statement about Styles; second occurrence on this line.",1),
    ("styles",202,"Mr Styles","styles","Index candidate gives Benjamin Styles; identity alignment remains an S3 task."),
    ("south_sea_bubble",202,"South Sea Bubble","south_sea_bubble","Named source of Styles's fortune in Haskell's account."),
    ("styles_house",203,"His country house","moor_park","Possessive refers to Styles's Moor Park country house."),
    ("moor_park",203,"Moor Park","moor_park","Named country house."),
    ("styles_decoration",204,"Styles","styles","Owner who intended to commission the decoration."),
    ("thornhill_2",204,"Thornhill","thornhill","Artist initially intended for the Moor Park decoration."),
    ("moor_park_job",204,"the decoration","moor_park_decoration","Unidentified job; sentence continues at p.287 with the replacement artists."),
    ("styles_spite",204,"Styles","styles","Subject of the open assignment sentence.",1),
]
for row in MENTIONS:
    add_m(*row)


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
          cross=None, footnote=None):
    if sid in sids or any(row["statement_id"] == sid for row in new_s):
        raise SystemExit(f"duplicate statement {sid}")
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 286,
                  "pdf_physical_page": 15, "claim": claim, "speaker": speaker,
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
                  "original_quote": quote(start, end), "source_file": SOURCE_FILE,
                  "origin": "book"})


opening = next((row for row in statements if row["statement_id"] == "st-chp10-p285-next-section-opening"), None)
if not opening or opening["segment_id"] != PREV:
    raise SystemExit("expected p.285 opening statement missing")
opening["qualifiers"]["claim"] = "Haskell calls London, Dusseldorf and Paris the most exciting centres of Venetian painting until early in the 1720s; he says the situation then began to change across Europe."
opening["qualifiers"]["qualification"] = "The sentence opened at p.285 L188 and closes at p.286 L191; preserve it as Haskell's periodizing assessment."
opening["qualifiers"]["continuation_quote"] = "Venetian painting until early in the 1720s."
opening["qualifiers"]["cross_reference_segments"] = [{"segment_id": SEG, "source_line_start": 191, "source_line_end": 191}]

add_s("st-chp10-p286-galilei-national-taste",191,193,E["galilei"],None,
      "galilei_complained_about_english_preference_for_native_artists",
      "In England there had been ominous signs", "an element of truth.",
      "Haskell says English national feeling had long resented foreign artists' success and reports Galilei's complaint that English patrons favored native artists; Haskell calls Galilei disgruntled but concedes the remark contains an element of truth.",
      "Nested quotation attributed to Galilei through Haskell; preserve the author's qualification and do not treat the quotation as an unqualified population-wide fact.",
      [E["galilei"]], speaker="Haskell reporting Alessandro Galilei", layer="authorial narration with nested quotation", footnote=1)
add_s("st-chp10-p286-thornhill-st-pauls-dome",194,194,E["thornhill"],C["st_pauls_dome_work"],
      "thornhill_given_st_pauls_dome_painting", "The dome of St Paul", "Thornhill to paint.",
      "Haskell says the dome of St Paul's, a major attraction for Venetian artists, was given to Thornhill to paint.",
      "The dome as a space and the painting as a work are separate candidates; the painting has no title here.",
      [C["st_pauls_dome"],E["thornhill"]], relation=True)
add_s("st-chp10-p286-queens-bedchamber-commission",194,195,E["halifax"],C["queens_ceiling"],
      "halifax_threatened_to_block_payment_for_ricci_commission",
      "So too was the ceiling", "Sebastiano Ricci.",
      "Haskell says Thornhill also received the Queen's Bed Chamber ceiling at Hampton Court after Halifax said the Treasury would refuse payment if the intended commission went to Sebastiano Ricci.",
      "The threatened refusal is Halifax's reported position; do not infer that the Treasury actually withheld payment. The room, ceiling work and institution remain distinct.",
      [C["queens_bed_chamber"],E["hampton_court"],E["halifax"],C["english_treasury"],E["ricci"],E["thornhill"]], relation=True)
add_s("st-chp10-p286-burlington-architecture",195,196,E["burlington"],None,
      "burlington_promoted_architecture_with_limited_scope_for_large_ceiling_decoration",
      "Moreover, the new style of architecture", "figures of gods and goddesses",
      "Haskell says the architectural style promoted by Burlington after returning from Vicenza in 1719 left little scope for large ceiling decorations filled with mythological figures.",
      "This is Haskell's interpretation of architectural taste and decorative opportunity, not a claim that Burlington prohibited such decoration.",
      [E["burlington"],E["vicenza"]], relation=True)
add_s("st-chp10-p286-grand-tour-changing-taste",196,196,C["grand_tour_practice"],None,
      "habitual_grand_tour_and_growing_english_confidence_changed_taste",
      "and, as the Grand Tour became habitual", "died long ago.",
      "Haskell links the Grand Tour becoming habitual and English patrons growing more confident in their taste to a dislike of large-scale history painting unless it was by a long-dead Old Master.",
      "Keep this as a broad, qualified historical interpretation; the Grand Tour practice is distinct from Burlington's earlier individual journey.",
      [C["grand_tour_practice"],E["history_painting"],E["old_masters"]], layer="authorial interpretation")
add_s("st-chp10-p286-amigoni-arrival",196,197,E["amigoni"],None,
      "amigoni_arrived_in_england_1730_after_bellucci_departure",
      "The career of", "symptomatic of the change.",
      "Haskell says Amigoni arrived in England in 1730, about eight years after Bellucci's departure, and treats his career as symptomatic of changing taste.",
      "The interval is approximate and the final clause is Haskell's interpretation.",
      [E["amigoni"],E["belleucci"]])
add_s("st-chp10-p286-tankerville-welcomed-amigoni",197,198,E["tankerville"],E["amigoni"],
      "tankerville_welcomed_amigoni", "He was first greeted", "Prince of Wales.",
      "Haskell says Lord Tankerville welcomed Amigoni enthusiastically and describes Tankerville as a prominent Whig and then Lord of the Bedchamber to the Prince of Wales.",
      "The Prince is identified by title only; do not infer a personal identity from the passage.",
      [E["tankerville"],C["whig_group"],C["prince_of_wales"]], relation=True)
add_s("st-chp10-p286-tankerville-staircase",198,198,E["amigoni"],C["tankerville_staircase"],
      "amigoni_painted_tankerville_staircase_later_pulled_down",
      "Amigoni painted his staircase", "eight years later.",
      "Haskell says Amigoni painted Tankerville's staircase and that it was pulled down eight years later.",
      "The residence and exact demolition date are not supplied.",
      [E["amigoni"],E["tankerville"]], relation=True)
add_s("st-chp10-p286-powis-house-decoration",199,200,E["amigoni"],C["powis_decoration"],
      "amigoni_decorated_powis_house_with_seasons_and_judith_holofernes",
      "He also painted a ceiling", "Judith and Holofernes.",
      "Haskell says Amigoni painted a ceiling, walls and staircase at Powis House in Great Ormond Street with the Seasons and the story of Judith and Holofernes.",
      "The programme is recorded as one described decoration; the text does not name separate canvases or establish Lord Powis as patron.",
      [E["amigoni"],C["powis_house"],C["great_ormond_street"],C["powis_decoration"]], relation=True, footnote=2)
add_s("st-chp10-p286-powis-patron-uncertain",200,201,E["powis"],C["powis_decoration"],
      "lord_powis_possible_patronage_of_amigoni_decoration_uncertain",
      "It is impossible to be quite certain", "a generation earlier.",
      "Haskell says it is impossible to be certain who patronized Amigoni's Powis House decoration; if Lord Powis was the patron, Amigoni was moving in less fashionable circles than his predecessors.",
      "The patronage is explicitly conditional and remains a relation candidate, not a formal relation.",
      [E["powis"],E["amigoni"]], relation=True)
add_s("st-chp10-p286-powis-age",200,200,E["powis"],None,
      "haskell_describes_powis_as_about_seventy_years_old",
      "Lord Powis himself was an elderly man", "about 70.",
      "Haskell describes Lord Powis as an elderly man of about seventy.",
      "Approximate age as stated by Haskell; the cited biographical references in note 3 remain pending review.",
      [E["powis"]], footnote=3)
add_s("st-chp10-p286-powis-political-history",200,200,E["powis"],E["james_ii"],
      "powis_was_james_ii_loyalist_and_arrested_multiple_times",
      "He had been one of", "of 1715.",
      "Haskell describes Lord Powis as one of James II's most loyal followers who was arrested more than once, most recently during the 1715 Jacobite alarm.",
      "The source's summary is retained without inferring additional political activity or causes for each arrest.",
      [E["powis"],E["james_ii"],C["jacobite_alarm"]], relation=True)
add_s("st-chp10-p286-powis-house-fire-rebuild",200,201,C["powis_house"],C["powis_french_king"],
      "powis_house_burned_during_ambassador_tenancy_and_rebuilt_at_french_crown_expense",
      "Two years earlier", "King-of France.",
      "Haskell says that, two years before Powis's 1722 restoration, Powis House was occupied by the French Ambassador, burned during that tenancy and was rebuilt at the expense of the King of France.",
      "The ambassador and French king are unnamed; the relative date is tied to the 1722 context and no specific fire date is added.",
      [E["powis"],C["powis_house"],C["french_ambassador"],C["powis_french_king"]], relation=True)
add_s("st-chp10-p286-powis-restoration-lords",200,201,E["powis"],C["house_of_lords"],
      "powis_estates_restored_and_summoned_to_house_of_lords_1722",
      "In 1722 Lord", "sat with the Tories.",
      "Haskell says Powis's forfeited estates were restored in 1722 and he was summoned to take his seat in the House of Lords, where he sat with the Tories.",
      "The political affiliations are preserved as the author's account; no formal party membership record is inferred.",
      [E["powis"],C["house_of_lords"],C["tory_group"]], relation=True)
add_s("st-chp10-p286-styles-south-sea-fortune",201,202,E["amigoni"],E["styles"],
      "styles_was_amigoni_third_and_most_important_english_patron",
      "third and most important", "South Sea Bubble.",
      "Haskell calls Mr Styles Amigoni's third and most important English patron and says Styles made a fortune from the South Sea Bubble.",
      "The index candidate names Benjamin Styles; identity is still an S3 alignment question.",
      [E["amigoni"],E["styles"],C["south_sea_bubble"]], relation=True)
add_s("st-chp10-p286-moor-park-built",203,204,E["styles"],C["moor_park"],
      "moor_park_built_for_styles_by_thornhill_and_later_leoni",
      "His country house at Moor Park", "Giacomo Leoni.",
      "Haskell says Styles's country house at Moor Park was built for him in modified Baroque by Sir James Thornhill and later Giacomo Leoni.",
      "The source does not specify which construction phases or design decisions belong to each architect.",
      [E["styles"],C["moor_park"],E["thornhill"],E["leoni"]], relation=True)
add_s("st-chp10-p286-moor-park-decoration-open",204,204,E["styles"],C["moor_park_decoration"],
      "styles_intended_thornhill_then_reassigned_moor_park_decoration_after_quarrel",
      "Styles had intended to entrust Thornhill", "gave the job to",
      "Haskell says Styles intended to entrust Thornhill with the Moor Park decoration, but after the two quarrelled Styles gave the job to someone else; the recipients are named on p.287.",
      "The sentence is unfinished at p.286 L204; the assignment outcome remains open until the next segment.",
      [E["styles"],E["thornhill"]], relation=True,
      cross=[{"segment_id": NEXT, "source_line_start": 207, "source_line_end": 207}])

opening_cov_note = cov[PREV]["note"]
if "p.286" not in opening_cov_note and "p.285" not in opening_cov_note:
    raise SystemExit("p.285 coverage note does not identify the open continuation")
cov[PREV].update({"migration_status": "complete", "source_line_ranges": "L179-188; p.286 L191",
                  "note": "Printed p.285 was read against physical page 14. Its subsection-opening sentence closes at p.286 L191; the continuation is cross-linked. Notes 1-4 in the consolidated notes segment remain pending."})
cov[SEG].update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L191-204",
                 "note": "Printed p.286 was read against CHP-10.pdf physical page 15. Closed p.285's sentence about London, Dusseldorf and Paris; recorded Galilei's nested complaint with Haskell's qualification; Thornhill's St Paul's dome and Queen's Bed Chamber commissions, Halifax's payment objection, Burlington's architecture and the change in English taste; Amigoni's arrival, Tankerville patronage/staircase and the uncertain Powis House patronage; Powis's political history and house fire/rebuilding; Styles, the South Sea Bubble, Moor Park and the open decoration assignment. Buildings/spaces are distinct from works; the Powis patron remains explicitly uncertain. Scan-only corrections: p.200 'James H' -> 'James II'; 'King-of France' -> 'King of France'; p.201 'house of Lords' -> 'House of Lords'. S0 unchanged. Notes 1-3 are retained as pending in the consolidated notes segment. The final sentence continues at p.287 L207, so coverage remains partial."})
cov[NEXT]["note"] = "Next source-order segment is printed p.287 at L206-216; close p.286's open Styles/Thornhill decoration sentence beginning at L204 before marking p.286 complete."

print(json.dumps({"mode": "APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment": SEG, "new_candidates": len(newc), "new_mentions": len(newm),
                  "new_statements": len(new_s), "new_candidate_ids": [row["candidate_id"] for row in newc],
                  "coverage": {"p285": cov[PREV]["migration_status"], "p286": cov[SEG]["migration_status"],
                               "p287": cov[NEXT]["migration_status"]}}, ensure_ascii=False, indent=2))

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
    print("Applied p.286 S2 migration; p.285 is closed, p.286 remains partial, backups retained.")
