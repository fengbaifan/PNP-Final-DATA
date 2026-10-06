"""Controlled S2 migration for printed p.288; dry-run unless --apply is passed."""
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
PREV = "chp-10:10_CHP-10_intro:l206-216"
SEG = "chp-10:10_CHP-10_intro:l218-227"
NEXT = "chp-10:10_CHP-10_intro:l229-238"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
SEG_SHA = "c2ffb92b100d5ef3f58561ec76ceed777de410755c5d840f15eec99c100cbd76"
BACKUP = ".bak-s2-chp10-p288-20261002"


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
body = "\n".join(src[217:227])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != SEG_SHA or src[217].strip() != "[Page 288]":
    raise SystemExit("p.288 source segment hash/page mismatch")

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
if maximum != 9011:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for sid, expected in ((PREV, ("reviewed", "partial")), (SEG, ("queued", "pending")), (NEXT, ("queued", "pending"))):
    row = cov.get(sid)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {sid}: {row}")

E = {
    "mcswiny": "cand-1466", "england": "cand-8983", "europe": "cand-3462", "italy": "cand-3461",
    "whigs": "cand-8993", "robert_harley": "cand-1801", "marlborough": "cand-8869",
    "counter_reformation": "cand-6729", "history_painting": "cand-4630", "enlightenment": "cand-0974",
    "locke": "cand-1410", "newton": "cand-1739", "shaftesbury": "cand-2426",
    "creti": "cand-0889", "monti": "cand-1698", "piazzetta": "cand-1901",
    "pittoni": "cand-1950", "canaletto": "cand-0498", "cimaroli": "cand-0758",
    "bologna": "cand-0381", "venice": "cand-2719", "scheme": "cand-9007",
    "italian_artist_group": "cand-9009",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("english_noblemen", "English noblemen described as visiting the Continent for Italian art (unnamed group)", "term",
     "An unnamed group in Haskell's account of art tourism; no individual itinerary or membership is implied.", 219),
    ("british_worthies", "British monarchs, commanders and other illustrious people proposed for McSwiny's monuments (unnamed group)", "term",
     "The source quotes these as intended subjects but says no definite list was drawn up at the start.", 220),
    ("harley_monument", "Proposed McSwiny monument to Robert Harley, Earl of Oxford", "work",
     "A subject included in the proposed series; this passage describes it as represented but gives no individual title or location.", 220),
    ("marlborough_monument", "McSwiny series monument to the Duke of Marlborough", "work",
     "A monument in the proposed series; this passage says Marlborough was represented but gives no individual title or location.", 222),
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

scheme = next(row for row in candidates if row["candidate_id"] == E["scheme"])
if scheme["canonical_name"] != "McSwiny's proposed allegorical tomb series for England's recent great men":
    raise SystemExit("unexpected McSwiny tomb-scheme candidate")
old_scheme_detail = "A proposed commission on behalf of Lord March; the passage does not say that the paintings were executed."
if scheme["detail"] != old_scheme_detail:
    raise SystemExit("McSwiny tomb-scheme candidate detail changed")
scheme["detail"] = "Proposed commission on behalf of Lord March; p.288 describes intended subjects, political scope, format and division of roles. Proposals and intended designs are not all proof of execution."
artist_group = next(row for row in candidates if row["candidate_id"] == E["italian_artist_group"])
old_artist_group_detail = "Collective group in a proposal; no individual artists or completed commissions are identified."
if artist_group["detail"] != old_artist_group_detail:
    raise SystemExit("Italian artist group candidate detail changed")
artist_group["detail"] = "Collective artists proposed for McSwiny's scheme. Haskell names painters from Bologna and Venice, but this passage does not assign every individual role or identify which artists were the one or two exceptions; note 2 remains pending."

offsets, offset = {}, 0
for line in range(218, 228):
    offsets[line] = offset
    offset += len(src[line - 1]) + 1
newm = []


def add_m(local, line, surface, cid, note="", occurrence=0):
    mid = f"m-chp10-p288-{local}"
    if mid in mids or any(row["mention_id"] == mid for row in newm):
        raise SystemExit(f"duplicate mention: {mid}")
    if cid not in cids | {row["candidate_id"] for row in newc}:
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
    start = offsets[line] + positions[occurrence]
    end = start + len(surface)
    if body[start:end] != surface:
        raise SystemExit(f"span mismatch: {mid}")
    newm.append({"mention_id": mid, "segment_id": SEG, "candidate_id": cid,
                 "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTIONS = [
    ("noblemen",219,"thousands of English noblemen",C["english_noblemen"],"Unspecified collective in Haskell's prospective art-tourism explanation."),
    ("continent",219,"the Continent",E["europe"],"Broad destination wording; no specific country is inferred."),
    ("italian_art",219,"Italian art",E["italy"],"Artistic destination/field rather than a named work."),
    ("england_past",219,"England’s recent past",E["england"],"Subject of the proposed memorial scheme's patriotic framing."),
    ("mcswiny_quotation",220,"McSwiny",E["mcswiny"],"Haskell attributes the quoted statement to McSwiny; note 1 source remains pending."),
    ("monuments",220,"the monuments",E["scheme"],"Plural monuments are described as the proposed series."),
    ("british_worthies",220,"the British Monarchs, the valiant Commanders, and other illustrious Personages",C["british_worthies"],"Quoted intended subject classes; not an enumerated final list."),
    ("england_subjects",220,"England",E["england"],"Country in the quoted period description."),
    ("no_list_characters",220,"the characters",C["british_worthies"],"Refers to subjects later represented; list is explicitly said not to have been definite at the start."),
    ("whigs",220,"Whigs",E["whigs"],"Political affiliation attributed to most, not all, commemorated subjects."),
    ("robert_harley",220,"Robert Harley, Earl of",E["robert_harley"],"Name is split across L220-221; continuation is Oxford."),
    ("oxford",221,"Oxford",E["robert_harley"],"Completes Robert Harley's title across the line break."),
    ("marlborough",222,"Marlborough",E["marlborough"],"Named in connection with wars and explicitly said to be represented in the monument scheme; cross-chapter identity remains for S3."),
    ("pictures_format",222,"The pictures",E["scheme"],"Refers to the planned monument pictures."),
    ("scheme",222,"the scheme",E["scheme"],"McSwiny's proposed monument series."),
    ("counter_reformation",222,"Counter",E["counter_reformation"],"OCR line break divides Counter-Reformation across L222-223; scan confirms the compound."),
    ("counter_reformation_cont",223,"Reformation",E["counter_reformation"],"Second part of Counter-Reformation across the line break."),
    ("history_painting",223,"history painting",E["history_painting"],"A genre/category in Haskell's comparison."),
    ("continent_history",223,"the Continent",E["europe"],"European comparison, not a specific polity."),
    ("enlightenment",223,"the Enlightenment",E["enlightenment"],"The quoted 'Saints' language is metaphorical, not a religious classification."),
    ("locke",223,"Locke",E["locke"],"Named among Enlightenment figures commemorated."),
    ("newton",223,"Newton",E["newton"],"Named among Enlightenment figures commemorated."),
    ("each_picture",223,"Each picture",E["scheme"],"The iconographic instructions apply to the planned monuments."),
    ("mcswiny_subjects",225,"McSwiny",E["mcswiny"],"Subject of the reported invention and execution."),
    ("own_invention",225,"his own Invention",E["mcswiny"],"Possessive refers to McSwiny's claimed design authorship."),
    ("painters_italy",226,"Painters in Italy",E["italian_artist_group"],"Collective execution group; individual painters are separately named below."),
    ("exceptions",226,"one or two exceptions",E["italian_artist_group"],"The exceptions are not named in this sentence; note 2 remains pending."),
    ("bologna_selection",226,"Bologna",E["bologna"],"City from which McSwiny chose artists."),
    ("venice_selection",226,"Venice",E["venice"],"City from which McSwiny chose artists."),
    ("three_artists",226,"three artists",E["italian_artist_group"],"Three distinct roles were assigned for each picture; this does not name individual artists."),
    ("painters_puzzled",226,"the painters concerned",E["italian_artist_group"],"Painters were not told the purpose and are described through Haskell's nested quotation."),
    ("mcswiny_amateur",226,"this ‘amateur",E["mcswiny"],"Nested quotation characterizes McSwiny, not an independent unknown person."),
    ("shaftesbury",226,"Shaftesbury’s",E["shaftesbury"],"Surname reference; precise cross-chapter identity remains for S3."),
    ("bologna_figures",227,"Bologna",E["bologna"],"City where McSwiny selected figure painters."),
    ("creti_ocr",227,"Donato Cred",E["creti"],"OCR reads Cred; physical page reads Creti. Keep source text unchanged and log scan correction in S2."),
    ("monti",227,"Francesco Monti",E["monti"],"Named figure painter."),
    ("venice_figures",227,"Venice",E["venice"],"City where McSwiny selected figure painters."),
    ("piazzetta",227,"Piazzetta",E["piazzetta"],"Named figure painter."),
    ("pittoni",227,"Pittoni",E["pittoni"],"Named figure painter."),
    ("canaletto",227,"Canaletto",E["canaletto"],"Named landscape painter."),
    ("cimaroli",227,"Cimaroli",E["cimaroli"],"Named landscape painter."),
    ("venetian_group",227,"All four Venetian artists",E["italian_artist_group"],"Collective reference to the named Venetian participants; their career sentence continues on p.289."),
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
    qualifiers = {"source_line_start": lo, "source_line_end": hi, "printed_page": 288,
                  "pdf_physical_page": 17, "claim": claim, "speaker": speaker,
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


open_st = next((row for row in statements if row["statement_id"] == "st-chp10-p287-wealth-peace-open"), None)
if not open_st or open_st["segment_id"] != PREV:
    raise SystemExit("expected p.287 wealth-and-peace open statement missing")
open_st["qualifiers"]["claim"] = "Haskell says that wealth at home and peace in Europe encouraged thousands of English noblemen to visit the Continent and enjoy Italian art."
open_st["qualifiers"]["qualification"] = "The unfinished p.287 sentence closes at p.288 L219; the following sentence gives Haskell's inference about why McSwiny's project should prosper."
open_st["qualifiers"]["continuation_quote"] = "thousands of English noblemen to visit the Continent and enjoy the pleasures of Italian art."
open_st["qualifiers"]["cross_reference_segments"] = [{"segment_id": SEG, "source_line_start": 219, "source_line_end": 219}]
open_st["qualifiers"]["mentioned_candidate_ids"] = list(dict.fromkeys(open_st["qualifiers"].get("mentioned_candidate_ids", []) + [C["english_noblemen"],E["italy"]]))

add_s("st-chp10-p288-project-prospects",219,219,E["scheme"],None,
      "haskell_says_reverence_for_englands_past_and_modern_italian_painting_gave_project_good_prospects",
      "There was thus every reason", "should do well.",
      "Haskell infers that a project combining reverence for England's recent past with the prestige of modern Italian painting had good prospects.",
      "This is the author's expectation, not evidence that all patrons supported the project or that it ultimately succeeded.",
      [E["scheme"],E["england"],E["italy"]],layer="authorial inference")
add_s("st-chp10-p288-proposed-subjects",220,220,E["mcswiny"],C["british_worthies"],
      "mcswiny_proposed_monuments_to_british_monarchs_commanders_and_illustrious_personages",
      "McSwiny wrote1 that the monuments were to glorify", "Beginning of the eighteenth Centuries’.",
      "Haskell quotes McSwiny as saying the monuments were to glorify British monarchs, valiant commanders and other illustrious people who flourished in England around the end of the seventeenth and beginning of the eighteenth centuries.",
      "This is a reported quotation attributed to McSwiny; note 1's pamphlet source is pending in the consolidated notes segment. The quoted subject categories do not amount to a complete named list.",
      [E["mcswiny"],E["scheme"],C["british_worthies"],E["england"]],
      speaker="Haskell quoting McSwiny",layer="reported quotation",relation=True,footnote=1)
add_s("st-chp10-p288-no-definite-list",220,220,E["scheme"],C["british_worthies"],
      "haskell_says_no_definite_subject_list_was_likely_drawn_up_at_start",
      "It is almost certain that no definite list", "when the scheme was already under way.",
      "Haskell says it is almost certain no definite list of subjects was drawn up at the start, because some people eventually represented died only after the scheme was under way.",
      "The claim is expressly Haskell's inference and is time-bounded to the start of the project.",
      [E["scheme"],C["british_worthies"]],layer="authorial inference")
add_s("st-chp10-p288-whigs-no-strict-programme",220,221,E["scheme"],E["whigs"],
      "most_commemorated_were_whigs_but_no_strict_political_programme",
      "Most of those commemorated were, naturally, Whigs", "Oxford,",
      "Haskell says most people commemorated were Whigs but there was no strict political programme, and identifies Robert Harley, Earl of Oxford as an included figure.",
      "The title continues across the source line break from L220 to L221; it is not a page break.",
      [E["scheme"],E["whigs"],E["robert_harley"],C["british_worthies"]],relation=True)
add_s("st-chp10-p288-harley-included",220,222,E["scheme"],C["harley_monument"],
      "robert_harley_included_in_scheme_and_had_role_in_ending_marlborough_wars_then_imprisoned_1715",
      "for it was found possible to include Robert Harley", "imprisoned for two years in 1715.",
      "Haskell says Robert Harley, Earl of Oxford, was included among the commemorated figures, had played a major part in ending the wars waged by Marlborough and was imprisoned for two years in 1715.",
      "This passage supplies a subject for a monument but no individual title or location; Harley's stated political role is Haskell's summary.",
      [E["scheme"],C["harley_monument"],E["robert_harley"],E["marlborough"]],relation=True)
add_s("st-chp10-p288-marlborough-included",222,222,E["scheme"],C["marlborough_monument"],
      "marlborough_also_represented_in_the_scheme",
      "Marlborough (also, of course, represented)", "Marlborough (also, of course, represented)",
      "Haskell says Marlborough was also represented in the proposed monument series.",
      "The passage gives no individual monument title or location; the Duke's personal identity remains for global S3 alignment.",
      [E["scheme"],C["marlborough_monument"],E["marlborough"]],relation=True)
add_s("st-chp10-p288-picture-format",222,222,E["scheme"],None,
      "pictures_uniform_in_size_and_shaped_like_altarpieces",
      "The pictures were all to be the same size", "like altar paintings.",
      "Haskell says the pictures were to share a size and be vertically oriented with semicircular tops like altar paintings.",
      "This describes intended format; it does not establish that every proposed picture was completed in that form.",
      [E["scheme"]])
add_s("st-chp10-p288-secular-patriotic-counterpart",222,223,E["scheme"],None,
      "scheme_as_early_secular_patriotic_counterpart_to_religious_history_painting",
      "In fact, the scheme represented one of the first attempts", "of the Continent—",
      "Haskell characterizes the scheme as one of the first attempts to create a secular and patriotic counterpart to Counter-Reformation religious iconography and the more generalized history painting of continental Europe.",
      "This is Haskell's art-historical interpretation and comparison, not an independently established first occurrence.",
      [E["scheme"],E["counter_reformation"],E["history_painting"],E["europe"]],layer="authorial interpretation")
add_s("st-chp10-p288-enlightenment-figures",223,223,E["scheme"],None,
      "many_commemorated_figures_were_saints_of_the_enlightenment_including_locke_and_newton",
      "among the figures commemorated were many", "such as Locke and Newton.",
      "Haskell says many of the figures commemorated were among the 'Saints' of the Enlightenment, naming Locke and Newton.",
      "'Saints' is a metaphor in Haskell's comparison, not a religious status. No specific portrait or tomb title is supplied here.",
      [E["scheme"],E["enlightenment"],E["locke"],E["newton"]],layer="authorial interpretation")
add_s("st-chp10-p288-iconographic-instructions",223,224,E["scheme"],None,
      "each_picture_was_to_include_urn_family_heraldry_and_emblems_of_deceased_hero",
      "Each picture was to contain an urn", "of the Departed.’",
      "Haskell quotes the planned iconography: an urn supposed to hold the deceased hero's remains; family supporters and arms; and funerary ceremonies, statues and reliefs alluding to the deceased's virtues, occupations, learning and sciences.",
      "These are intended depictions and symbolic allusions, not evidence that remains were actually deposited or every feature was completed.",
      [E["scheme"],C["british_worthies"]],speaker="Haskell quoting McSwiny's descriptive instructions",layer="reported iconographic quotation")
add_s("st-chp10-p288-invention-execution",225,226,E["mcswiny"],E["italian_artist_group"],
      "mcswiny_claimed_subjects_as_his_invention_and_named_painters_executed_them",
      "McSwiny wrote that these subjects", "Painters in Italy’. ",
      "Haskell reports that McSwiny called the subjects his own invention and quoted them as elegantly executed by leading Italian painters.",
      "This preserves Haskell's report of McSwiny's claims; note 1's cited pamphlet is still pending and was not independently consulted.",
      [E["mcswiny"],E["scheme"],E["italian_artist_group"]],speaker="Haskell reporting and quoting McSwiny",layer="reported quotation",footnote=1,relation=True)
add_s("st-chp10-p288-artist-selection-geography",226,226,E["mcswiny"],E["italian_artist_group"],
      "mcswiny_selected_artists_mostly_from_bologna_and_venice",
      "With one or two exceptions", "from Bologna and Venice,",
      "Haskell says McSwiny chose the painters from Bologna and Venice with one or two exceptions.",
      "The exceptions are not named in this clause; note 2 is present in the consolidated notes segment and remains pending.",
      [E["mcswiny"],E["italian_artist_group"],E["bologna"],E["venice"]],relation=True,footnote=2)
add_s("st-chp10-p288-three-painter-rule",226,226,E["mcswiny"],E["scheme"],
      "every_picture_to_be_painted_by_three_artists_with_distinct_roles",
      "and he insisted that every picture", "buildings and other ornaments.",
      "Haskell says McSwiny required three artists for each picture: one for figures, one for landscape and one for buildings and other ornaments.",
      "The role allocation is an instruction; it does not identify which named artist performed each role in a particular picture. Printed page reads 'the figures'; OCR 'die' is corrected in S2 only.",
      [E["mcswiny"],E["scheme"],E["italian_artist_group"]],relation=True)
add_s("st-chp10-p288-painters-puzzled",226,226,E["italian_artist_group"],E["mcswiny"],
      "painters_puzzled_by_scheme_when_purpose_was_withheld",
      "Not surprisingly the painters concerned", "neither histories nor fables’.",
      "Haskell says the painters were not told the scheme's purpose and were puzzled by McSwiny's unusual ideas; he quotes an observer describing McSwiny as an amateur with unusually sound knowledge who commissioned ideas that were neither histories nor fables.",
      "The quoted observer is not named here; preserve nested quotation and do not treat 'amateur' as a formal role. Note 3 remains pending in the consolidated notes segment.",
      [E["italian_artist_group"],E["mcswiny"]],layer="authorial narration with nested quotation",footnote=3)
add_s("st-chp10-p288-instructions-rival-shaftesbury",226,226,E["mcswiny"],E["shaftesbury"],
      "mcswiny_instructions_must_have_rivalled_shaftesburys_in_detail",
      "In fact, McSwiny’s instructions", "minuteness of detail.",
      "Haskell judges that McSwiny's instructions must have rivalled Shaftesbury's in their minute detail.",
      "This is explicitly Haskell's comparative assessment; the named instructions are not reproduced here.",
      [E["mcswiny"],E["shaftesbury"]],layer="authorial interpretation")
add_s("st-chp10-p288-artist-allocation",227,227,E["mcswiny"],E["scheme"],
      "mcswiny_assigned_named_bologna_and_venice_figure_and_landscape_painters",
      "In Bologna he relied mostly", "painted some of the landscapes (Plate 52b).",
      "Haskell says McSwiny relied mainly on Donato Creti and Francesco Monti as figure painters in Bologna, and on Piazzetta and Pittoni in Venice; Canaletto and Cimaroli painted some landscapes.",
      "The OCR form 'Donato Cred' is corrected to Creti from the scan; assignments are preserved as stated without inferring which named person painted each specific monument. Plate 52b is a cross-reference, not a separate entity.",
      [E["mcswiny"],E["scheme"],E["creti"],E["monti"],E["piazzetta"],E["pittoni"],E["canaletto"],E["cimaroli"],E["bologna"],E["venice"]],relation=True)
add_s("st-chp10-p288-venetian-careers-open",227,227,E["italian_artist_group"],None,
      "four_venetian_participants_were_beginning_their_careers_open",
      "All four Venetian artists were beginning their", "All four Venetian artists were beginning their",
      "Haskell begins to say that the four Venetian artists were at the start of their careers; the sentence continues on p.289.",
      "Partial statement: retain only the completed source fragment and wait for p.289 before specifying what their careers were doing.",
      [E["italian_artist_group"],E["piazzetta"],E["pittoni"],E["canaletto"],E["cimaroli"]],
      cross=[{"segment_id":NEXT,"source_line_start":230,"source_line_end":230}])

open_note = cov[PREV]["note"]
if "p.288" not in open_note:
    raise SystemExit("p.287 coverage note does not identify its p.288 continuation")
cov[PREV].update({"migration_status":"complete","source_line_ranges":"L207-216; p.288 L219",
                  "note":"Printed p.287 was read against physical page 16. Its final wealth-and-peace sentence closes at p.288 L219; continuation is cross-linked. Inline note 2 was migrated with its cited sources retained as unresolved."})
cov[SEG].update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L219-227",
                 "note":"Printed p.288 was read against CHP-10.pdf physical page 17. Closed p.287's wealth-and-peace sentence; recorded Haskell's expectation for McSwiny's scheme, the proposed British subjects, lack of an initial definite list, Whig composition without strict political programme, named Harley/Marlborough subjects, intended picture format, secular-patriotic comparison, Enlightenment figures, quoted iconographic instructions, artist selection by city and role, painters' confusion and named artist assignments. Preserve Haskell's inference, reported quotations and project intentions. L223 OCR 'die figures' is corrected to printed 'the figures'; L227 'Donato Cred' to printed 'Donato Creti'; corrections are S2-only, S0 unchanged. Notes 1-3 (consolidated source L540-542) remain pending. L227's final career sentence continues at p.289 L230, so coverage remains partial."})
cov[NEXT]["note"] = "Next source-order segment is printed p.289 at L229-238; close p.288 L227's unfinished sentence about all four Venetian artists beginning their careers."

print(json.dumps({"mode":"APPLY" if sys.argv[-1:] == ["--apply"] else "DRY-RUN",
                  "segment":SEG,"new_candidates":len(newc),"updated_candidates":[E["scheme"],E["italian_artist_group"]],
                  "new_mentions":len(newm),"new_statements":len(new_s),
                  "new_candidate_ids":[row["candidate_id"] for row in newc],
                  "coverage":{"p287":cov[PREV]["migration_status"],"p288":cov[SEG]["migration_status"],"p289":cov[NEXT]["migration_status"]}},ensure_ascii=False,indent=2))

if sys.argv[-1:] == ["--apply"]:
    for path in (cp,mp,sp,vp):
        backup=Path(str(path)+BACKUP)
        if backup.exists(): raise SystemExit(f"backup already exists: {backup}")
        shutil.copy2(path,backup)
    write_csv(cp,cf,candidates+newc)
    write_csv(mp,mf,mentions+newm)
    write_jsonl(sp,statements+new_s)
    write_csv(vp,vf,[cov[row["segment_id"]] for row in coverage])
    print("Applied p.288 S2 migration; p.287 is complete, p.288 remains partial, backups retained.")
