"""Controlled S2 migration for chapter 8 printed p.205 body text.

Default invocation is a read-only dry run. Print readings are documented in S2;
the immutable S0 transcription is never edited by this script.
"""
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
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SOURCE_PATH = ROOT / SOURCE_REL
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l23-28"
NEXT_SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l30-41"
BACKUP_SUFFIX = ".bak-s2-chp8-p205-body-20260930"
EXPECTED_MAX_CANDIDATE = 7400


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)
segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

meta = segments.get(SEGMENT_ID)
if not meta or meta["source_file"] != SOURCE_REL or (int(meta["line_start"]), int(meta["line_end"])) != (23, 28):
    raise SystemExit("p.205 segment metadata changed; review before migration")
raw_source = SOURCE_PATH.read_bytes()
if hashlib.sha256(raw_source).hexdigest() != meta["asset_sha256"]:
    raise SystemExit("source file fingerprint changed; rebuild segments and review")
source_lines = SOURCE_PATH.read_text(encoding="utf-8-sig").splitlines()
segment_text = "\n".join(source_lines[22:28])
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != meta["sha256"]:
    raise SystemExit("p.205 segment text hash changed; review before migration")
if coverage_by_id.get(SEGMENT_ID, {}).get("disposition") != "queued":
    raise SystemExit("expected queued p.205 coverage; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in mention_rows):
    raise SystemExit("mentions already exist for p.205; inspect before rerunning")
if any(row["segment_id"] == SEGMENT_ID for row in statement_rows):
    raise SystemExit("statements already exist for p.205; inspect before rerunning")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")


def candidate(cid, name, typ, detail, line):
    return {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": typ,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line}",
    }


new_candidates = [
    candidate("cand-7401", "Unnamed King of Spain to whom Gaspar Roomer lent money", "person", "The text supplies only the royal title. Do not identify the ruler from chronology alone.", 25),
    candidate("cand-7402", "Via Monteoliveto (location of Roomer's earlier Naples palace)", "place", "Named street used to locate Roomer's earlier palace; building identity and address are not further specified.", 25),
    candidate("cand-7403", "Palazzo della Stella (later residence of Gaspar Roomer)", "place", "Named Naples palace among Roomer's residences; no independent modern identification is established here.", 25),
    candidate("cand-7404", "Unnamed only daughter of Gaspar Roomer", "person", "The source identifies her only as Roomer's only daughter and says she entered a Carmelite convent; her name is not supplied.", 25),
    candidate("cand-7405", "Unidentified Carmelite convent entered by Roomer's daughter", "place", "The convent is not named; retain it as a distinct religious building candidate without inferring its location.", 25),
    candidate("cand-7406", "Plague in 1656 from which Roomer is reported to have recovered", "event", "Haskell gives the year and reports recovery but does not specify the epidemic's location in this clause.", 25),
    candidate("cand-7407", "Gaspar Roomer's picture gallery and collection described on p.205", "", "A named collection as a source-specific object: outstanding by 1634 and reported to comprise over 1,500 paintings at Roomer's death. The taxonomy has no collection type.", 24),
    candidate("cand-7408", "Unidentified viceroys to whom Roomer lent money", "term", "Collective office-holder reference; no individual viceroy or precise office is identified in this passage.", 25),
    candidate("cand-7409", "Working men living near Roomer's palace", "term", "Unnamed group whose earlier generosity is said to have helped Roomer during the 1647 revolt; exact membership is absent.", 25),
    candidate("cand-7410", "Unidentified leaders bribed during the revolt of Masaniello", "term", "The passage calls them the workers' present leaders in the revolt context but names none and does not specify their organization.", 25),
    candidate("cand-7411", "Unidentified Carmelite churches receiving Roomer's donations", "place", "Plural religious buildings are described collectively; none is named or independently identified.", 25),
    candidate("cand-7412", "Unidentified painting of the Flaying of Marsyas reported among Roomer's collection", "work", "The p.205 text places a work of this subject in the Ribera series associated with Roomer; note 3 later distinguishes the extant 1637 painting from the work listed at Roomer's house in 1634.", 27),
    candidate("cand-7413", "Marsyas represented in the p.205 Flaying painting", "person", "Mythological figure named as the subject of the painting; preserve as image content, not as evidence for the mythic event.", 27),
    candidate("cand-7414", "Unidentified Cato painting recalled by Sandrart", "work", "Haskell reports Sandrart's recollection of an image described by its subject; maker, title, medium, and version are not specified.", 27),
    candidate("cand-7415", "Cato represented in Sandrart's recollection, identity unspecified", "person", "The source names only Cato; do not choose a specific Roman Cato from this passage.", 27),
    candidate("cand-7416", "Caravaggist painters collectively described as Roomer's favourites", "term", "The source names a group/style category but gives no membership list in this clause.", 28),
    candidate("cand-7417", "Fauns in Haskell's description of The Drunken Silenus", "", "Collective mythological image content described as goat-like companions; the taxonomy does not provide a clear group type, so preserve this as an untyped source candidate pending S3.", 27),
    candidate("cand-7418", "Proverb 'Do you take me for a Roomer?'", "term", "The passage reports a saying associated with persistent borrowers; preserve the wording and its attribution to the Roomer account.", 25),
    candidate("cand-7419", "Satyrs in the p.205 Flaying of Marsyas description", "", "Collective mythological image content described as watching the torment; the taxonomy does not provide a clear group type, so preserve this as an untyped source candidate pending S3.", 27),
    candidate("cand-7420", "Egypt", "place", "Named as an extent of Roomer's shipping routes; the passage gives no port or itinerary.", 24),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate IDs collide")

mention_specs = []


def add_mention(surface, cid, note, occurrence=1):
    mention_specs.append((surface, cid, note, occurrence))


add_mention("Gaspar Roomer", "cand-2223", "Main index candidate for Roomer, indexed on p.205.")
add_mention("Antwerp", "cand-4983", "Birthplace named by Haskell.")
add_mention("Naples", "cand-1722", "City where Roomer had settled by 1634; p.205 later refers back to this city.")
add_mention("picture gallery", "cand-7407", "Roomer's gallery, which the text calls outstanding by 1634.")
add_mention("Scandinavia", "cand-5521", "Region named as the far reach of Roomer's shipping; the OCR has an uncertain small mark after the word, left unresolved.")
add_mention("Egypt", "cand-7420", "Second named extent of Roomer's ships.")
add_mention("Low Countries", "cand-4342", "Region identified as the main area of Roomer's business and his native region.")
add_mention("viceroys", "cand-7408", "Unspecified office-holders to whom Roomer lent money.")
add_mention("King of Spain", "cand-7401", "Title-only person reference; ruler identity deferred.")
add_mention("Spain", "cand-4591", "Polity named within the nested royal title.")
add_mention("Italy", "cand-3461", "Country in Haskell's comparative description of local titles and feudal virtues.")
add_mention("Via Monteoliveto", "cand-7402", "Street locating Roomer's earlier palace.")
add_mention("Palazzo della Stella", "cand-7403", "Later named residence of Roomer.")
add_mention("Carmelites", "cand-0563", "Religious order to which Roomer was devoted and whose churches received donations.")
add_mention("their churches", "cand-7411", "Unidentified churches of the Carmelites, mentioned anaphorically.")
add_mention("his only daughter", "cand-7404", "Unnamed daughter identified as his only child.")
add_mention("one of their convents", "cand-7405", "Unidentified Carmelite convent entered by the daughter.")
add_mention("revolt of Masaniello", "cand-1559", "The 1647 revolt named as the context of Roomer's danger.")
add_mention("Masaniello", "cand-4150", "Person named within the revolt title; image-title candidate remains distinct from the event.")
add_mention("Roomer", "cand-2229", "Index subentry for Roomer's escape during the Masaniello revolt.", 2)
add_mention("some working men living near his palace", "cand-7409", "Unnamed group whose prior generosity is described as protecting Roomer.")
add_mention("their present leaders", "cand-7410", "Unidentified leaders whom Roomer was ready to bribe during the revolt.")
add_mention("plague in 1656", "cand-7406", "Epidemic episode from which the source says Roomer recovered.")
add_mention("over 1500 paintings", "cand-7407", "Quantity reported for the paintings left at Roomer's death; the items are not individually identified.")
add_mention("Do you take me for a Roomer?", "cand-7418", "Proverb reported in Haskell's account.")
add_mention("Roomer", "cand-2223", "Surname used within the reported proverb; lexical use, not a separate biographical assertion.", 3)
add_mention("Roomer", "cand-2231", "Index subentry for Roomer's taste for grotesque and dark subject matter.", 4)
add_mention("Ribera", "cand-2142", "Index subentry for Ribera's Drunken Silenus on p.205.")
add_mention("The Drunken Silenus", "cand-4089", "Artwork identified in the front-matter plate caption and named again in the body.")
add_mention("Silenus", "cand-4161", "Mythological figure represented in the work; source description is not treated as an independent mythic fact.")
add_mention("goat-like fauns", "cand-7417", "Collective figures described within the work.")
add_mention("The Flaying of Marsyas", "cand-7412", "Work identified by subject in the Ribera series associated with Roomer; object/version is unresolved.")
add_mention("Marsyas", "cand-7413", "Mythological figure represented in the work.")
add_mention("Apollo", "cand-4667", "Mythological figure in the described scene; mapped to the existing source candidate pending S3 identity alignment.")
add_mention("St Peter", "cand-4231", "Saint used as a visual comparison in Haskell's description.")
add_mention("satyrs", "cand-7419", "Collective figures in Haskell's description of the image.")
add_mention("Sandrart", "cand-2353", "Joachim von Sandrart, named as the source of the recollection.")
add_mention("a Cato", "cand-7414", "Painting/image referred to by subject in Sandrart's recollection.")
add_mention("Cato", "cand-7415", "Unspecified person represented by the painting; nested in the work mention.")
add_mention("Roomer", "cand-2230", "Index subentry for Roomer's preference for Caravaggists.", 5)
add_mention("Caravaggists", "cand-7416", "Unnamed painter group described as Roomer's particular preference.")
add_mention("Riberas", "cand-2140", "Plural metonymic reference to works by Ribera; the passage reports seven paintings.")
add_mention("Caracciolo", "cand-0541", "Giovanni Battista Caracciolo, indexed on p.205.")
add_mention("Massimo Stanzione", "cand-2506", "Massimo Stanzione, indexed on p.205.")
add_mention("Carlo", "cand-2358", "The p.205 line breaks after the first name; p.206 continues with Saraceni. Keep this mention anchored to the partial printed span.")

new_mentions = []
for index, (surface, cid, note, occurrence) in enumerate(mention_specs, 1):
    if cid not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {cid}")
    starts = []
    cursor = 0
    while True:
        found = segment_text.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + 1
    if occurrence > len(starts):
        raise SystemExit(f"surface occurrence {occurrence} missing for {surface!r}; found {len(starts)}")
    start = starts[occurrence - 1]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch for {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp8-p205-{index:03d}",
        "segment_id": SEGMENT_ID,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })

new_mentions.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for i, first in enumerate(new_mentions):
    if first["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {first['mention_id']}")
    for second in new_mentions[i + 1:]:
        a, b = int(first["start_char"]), int(first["end_char"])
        c, d = int(second["start_char"]), int(second["end_char"])
        if a < d and c < b:
            nested = (a <= c and d <= b and (a, b) != (c, d)) or (c <= a and b <= d and (a, b) != (c, d))
            if not nested:
                raise SystemExit(f"overlapping non-nested mentions: {first!r} / {second!r}")


def quote_between(start_token, end_token):
    start = segment_text.find(start_token)
    if start < 0:
        raise SystemExit(f"quote start token missing: {start_token!r}")
    stop = segment_text.find(end_token, start + len(start_token))
    if stop < 0:
        raise SystemExit(f"quote end token missing: {end_token!r}")
    return segment_text[start:stop + len(end_token)]


def statement(sid, start, end, predicate, claim, qualification, *, subject=None, obj=None,
              mentioned=(), quote=None, extra=None):
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 205,
        "pdf_physical_page": 3,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": sid,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote or "\n".join(source_lines[start - 1:end]),
        "origin": "book",
        "source_file": SOURCE_REL,
    }


body_statements = [
    statement("st-chp8-p205-roomer-most-influential-patron", 24, 24, "ranked_as_most_influential_patron",
              "Haskell calls Gaspar Roomer by far the most important and influential of the patrons just discussed.",
              "This is Haskell's evaluative ranking; 'all such patrons' points back to the unnamed translocal patrons on p.204 and does not define a complete comparison set.",
              subject="cand-2223", obj="cand-7399", mentioned=["cand-2223", "cand-7399"],
              quote=quote_between("By far the most important", "Gaspar Roomer.1"),
              extra={"footnote_marker": 1, "footnote_scope_note": "P.205 note 1 says that, except where specified, the account's information about Roomer derives from Ceci and de Vaes (1925)."}),
    statement("st-chp8-p205-roomer-origin-residence-gallery", 24, 24, "born_in_and_settled_with_picture_gallery",
              "Haskell reports that Roomer came from a good family in Antwerp, was born near the end of the sixteenth century, had long been settled in Naples by 1634, and owned an outstanding picture gallery there.",
              "The dates, family description, and assessment of the gallery are reported by Haskell; no independent source is consulted here.",
              subject="cand-2223", obj="cand-7407", mentioned=["cand-2223", "cand-4983", "cand-1722", "cand-7407"],
              quote=quote_between("He was born of a good family", "outstanding picture gallery.")),
    statement("st-chp8-p205-roomer-shipping-trade", 24, 25, "shipowner_and_trader_with_cross_regional_routes",
              "Haskell reports that Roomer became a shipowner and trader, accumulated a fortune valued in the text at five million ducats, sent ships as far as Scandinavia and Egypt, and conducted most business with the Low Countries.",
              "Keep the amount as a reported valuation and the route as a stated extent; no currency conversion, exact itinerary, or trade ledger is supplied.",
              subject="cand-2223", mentioned=["cand-2223", "cand-5521", "cand-7420", "cand-4342"],
              quote=quote_between("Some years later his activities", "his native\nLow Countries.")),
    statement("st-chp8-p205-roomer-lent-to-viceroys", 25, 25, "lent_money_to_collective_officeholders",
              "Haskell says Roomer lent money to unnamed viceroys.",
              "No individual officeholder, jurisdiction, amount, or date is identified.",
              subject="cand-2223", obj="cand-7408", mentioned=["cand-2223", "cand-7408"],
              quote="He lent money to the viceroys"),
    statement("st-chp8-p205-roomer-lent-to-king-of-spain", 25, 25, "lent_money_to_king",
              "Haskell says Roomer also lent money to the King of Spain.",
              "The ruler is unnamed; do not identify him from the period alone.",
              subject="cand-2223", obj="cand-7401", mentioned=["cand-2223", "cand-7401", "cand-4591"],
              quote="even to the King of Spain"),
    statement("st-chp8-p205-roomer-hosted-neapolitan-nobility", 25, 25, "hosted_local_nobility_at_residences",
              "Haskell characterizes Naples as a place where titles and feudal virtues counted more than elsewhere in Italy and says Roomer entertained half the nobility at his palace on Via Monteoliveto, later at Palazzo della Stella or one of his country houses.",
              "'Half the nobility' and the comparative cultural judgment are Haskell's phrasing, not a measured count. The later residences are named but not independently identified.",
              subject="cand-2223", mentioned=["cand-2223", "cand-1722", "cand-3461", "cand-7402", "cand-7403"],
              quote=quote_between("and in a city where titles", "many country houses.")),
    statement("st-chp8-p205-roomer-devoted-to-carmelites", 25, 25, "religious_devotion_to_carmelites",
              "Haskell presents Roomer's religious convictions and particular devotion to the Carmelites as visible in donations to their churches.",
              "The churches are unnamed; the passage does not specify dates, amounts, or the receiving convents.",
              subject="cand-2223", obj="cand-0563", mentioned=["cand-2223", "cand-0563", "cand-7411"],
              quote=quote_between("The strength ofliis religious convictions", "donations to their churches"),
              extra={"ocr_corrections": [{"source_line": 25, "ocr": "strength ofliis", "print": "strength of his", "basis": "CHP-8.pdf physical page 3."}]}),
    statement("st-chp8-p205-roomer-daughter-entered-convent", 25, 25, "daughter_entered_carmelite_convent",
              "Haskell reports that Roomer's only daughter entered one of the Carmelites' convents.",
              "Neither the daughter nor convent is named; this is a reported action, not proof of a formal membership record.",
              subject="cand-7404", obj="cand-7405", mentioned=["cand-7404", "cand-7405", "cand-0563"],
              quote=quote_between("the entry of his only daughter", "one of their convents.")),
    statement("st-chp8-p205-roomer-survived-masaniello-revolt", 25, 25, "avoided_fate_during_revolt_through_generosity_and_bribery",
              "Haskell says Roomer faced danger during the 1647 revolt of Masaniello but was spared after the public remembered his earlier generosity to nearby working men and he was ready to bribe their present leaders.",
              "The causal account is Haskell's narrative; neither the workers nor leaders are named, and the passage does not specify the fate of the comparison group.",
              subject="cand-2229", obj="cand-1559", mentioned=["cand-2229", "cand-1559", "cand-4150", "cand-7409", "cand-7410"],
              quote=quote_between("During the revolt of Masaniello", "less cautious or less benevolent."),
              extra={"footnote_marker": 1}),
    statement("st-chp8-p205-roomer-lifespan-recovery-death", 25, 25, "recovered_from_plague_and_died_in_1674",
              "Haskell reports that Roomer recovered from the plague in 1656, lived for another twenty-six years, and died in 1674 at a very old age.",
              "'Very old' is the author's characterization; no birth year is specified beyond 'towards the end' of the sixteenth century.",
              subject="cand-2223", obj="cand-7406", mentioned=["cand-2223", "cand-7406"],
              quote=quote_between("He lived on, respected and successful", "in 1674."),
              extra={"footnote_marker": 1}),
    statement("st-chp8-p205-roomer-estate-and-collection-dispersal", 25, 25, "bequeathed_fortune_and_left_collection dispersed".replace(" ", "_"),
              "Haskell says Roomer left a vast fortune, most of it bequeathed to charity, and more than 1,500 paintings that were quickly dispersed.",
              "The source gives no named charitable recipient or item-level collection inventory; 'vast' and 'quickly' are Haskell's terms.",
              subject="cand-2223", obj="cand-7407", mentioned=["cand-2223", "cand-7407"],
              quote=quote_between("He left behind a vast fortune", "quickly dispersed,"),
              extra={"footnote_marker": 1}),
    statement("st-chp8-p205-roomer-proverb", 25, 25, "associated_with_proverb_about_persistent_borrowers",
              "Haskell reports the saying 'Do you take me for a Roomer?' as a means of countering persistent borrowers.",
              "The saying is attributed to the Roomer account; the passage does not establish its wider circulation or date.",
              subject="cand-7418", obj="cand-2223", mentioned=["cand-7418", "cand-2223"],
              quote=quote_between("the proverb", "persistent borrowers."),
              extra={"footnote_marker": 1}),
    statement("st-chp8-p205-roomer-taste-for-grotesque-subjects", 26, 26, "described_as_favouring_grotesque_dark_and_cruel_subjects",
              "Haskell generalizes that Roomer, like many Flemings devoted to life's pleasures, had a taste for grotesque, dark, and cruel subjects that Neapolitan painters could satisfy.",
              "This is the author's cultural characterization, not a self-description by Roomer.",
              subject="cand-2231", mentioned=["cand-2231", "cand-1722"],
              quote=quote_between("Like many a Fleming", "well able to satisfy."),
              extra={"footnote_marker": 1}),
    statement("st-chp8-p205-roomer-collected-drunk-silenus", 27, 27, "collected_work_attributed_to_ribera",
              "Haskell includes Ribera's The Drunken Silenus in the grim series Roomer collected and describes the figure and its attendants in grotesque terms.",
              "The description is Haskell's visual and evaluative account. Note 2 qualifies the work's documentation; the 1626 Capodimonte object must not be presumed identical to the picture in Roomer's 1634 list.",
              subject="cand-2223", obj="cand-4089", mentioned=["cand-2223", "cand-2142", "cand-4089", "cand-4161", "cand-7417"],
              quote=quote_between("Over the years he collected a grim series", "(Plate 32a)2;"),
              extra={"footnote_marker": 2, "relation_candidate": True, "relation_note": "Source reports Roomer collected a work attributed to Ribera; formal endpoints and object identity await later stages."}),
    statement("st-chp8-p205-roomer-collected-flaying-marsyas", 27, 27, "collected_work_of_marsyas_subject_attributed_to_ribera",
              "Haskell says a work representing the flaying of Marsyas also belonged to the Ribera series associated with Roomer, and describes its figures and composition.",
              "Note 3 explicitly says the extant 1637 San Martino picture cannot be the actual work in Roomer's house in 1634; the source-specific work candidate therefore remains unidentified.",
              subject="cand-2223", obj="cand-7412", mentioned=["cand-2223", "cand-2142", "cand-7412", "cand-7413", "cand-4667", "cand-4231", "cand-7419"],
              quote=quote_between("there was too The Flaying of Marsyas", "at his torments3;"),
              extra={"footnote_marker": 3, "relation_candidate": True, "relation_note": "The printed account reports a work in Roomer's collection; note 3 rejects identity with the surviving 1637 painting."}),
    statement("st-chp8-p205-sandrart-recalled-cato", 27, 27, "recalled_painting_described_as_cato",
              "Haskell reports that Sandrart recalled seeing an image of a Cato shown in the act of suicide.",
              "The recollection is attributed to Sandrart; Haskell does not name the artist, title, medium, collection, or which Cato is represented.",
              subject="cand-2353", obj="cand-7414", mentioned=["cand-2353", "cand-7414", "cand-7415"],
              quote=quote_between("and Sandrart recalled seeing a Cato", "with his hands’.4"),
              extra={"footnote_marker": 4}),
    statement("st-chp8-p205-roomer-favoured-caravaggists", 28, 28, "particularly_fond_of_caravaggist_painters",
              "Haskell says Roomer was especially fond of Caravaggist painters.",
              "The group is not enumerated as a whole in this sentence.",
              subject="cand-2230", obj="cand-7416", mentioned=["cand-2230", "cand-7416"],
              quote=quote_between("In fact, Roomer was especially fond", "Caravaggists:"),
              extra={"footnote_marker": 1}),
    statement("st-chp8-p205-roomer-owned-seven-ribera-paintings", 28, 28, "owned_seven_paintings_by_artist",
              "Haskell says Roomer owned seven paintings by Ribera.",
              "The count is explicit but the individual works are not all named here; this is a source claim, not a catalogue reconciliation.",
              subject="cand-2223", obj="cand-2140", mentioned=["cand-2223", "cand-2140"],
              quote="besides his seven Riberas",
              extra={"quantity": 7, "footnote_marker": 1, "relation_candidate": True}),
    statement("st-chp8-p205-roomer-owned-three-caracciolo-paintings", 28, 28, "owned_three_paintings_by_artist",
              "Haskell says Roomer owned three paintings by Caracciolo.",
              "No titles or dates are supplied.",
              subject="cand-2223", obj="cand-0541", mentioned=["cand-2223", "cand-0541"],
              quote="heowned three paintings each by Caracciolo",
              extra={"quantity": 3, "footnote_marker": 1, "relation_candidate": True, "ocr_corrections": [{"source_line": 28, "ocr": "heowned", "print": "he owned", "basis": "CHP-8.pdf physical page 3."}]}),
    statement("st-chp8-p205-roomer-owned-three-stanzione-paintings", 28, 28, "owned_three_paintings_by_artist",
              "Haskell says Roomer owned three paintings by the young Massimo Stanzione.",
              "No titles or dates are supplied; 'young' is retained as the author's description at the time of the account.",
              subject="cand-2223", obj="cand-2506", mentioned=["cand-2223", "cand-2506"],
              quote="heowned three paintings each by Caracciolo, the young Massimo Stanzione",
              extra={"quantity": 3, "footnote_marker": 1, "relation_candidate": True, "ocr_corrections": [{"source_line": 28, "ocr": "heowned", "print": "he owned", "basis": "CHP-8.pdf physical page 3."}]}),
    statement("st-chp8-p205-roomer-owned-three-saraceni-paintings-open", 28, 28, "owned_three_paintings_by_artist",
              "Haskell's sentence begins to say Roomer owned three paintings by Carlo [surname continued on p.206].",
              "The p.205 source segment ends after the first name. The identity and complete quote are carried forward to the next segment; do not mark this claim complete yet.",
              subject="cand-2223", obj="cand-2358", mentioned=["cand-2223", "cand-2358"],
              quote="heowned three paintings each by Caracciolo, the young Massimo Stanzione and Carlo",
              extra={"quantity": 3, "footnote_marker": 1, "continuation_status": "open", "continuation_expected_segment_id": NEXT_SEGMENT_ID, "continuation_note": "Printed p.206 begins 'Saraceni'; close the split painter's name and complete the claim while processing the next segment.", "relation_candidate": True, "ocr_corrections": [{"source_line": 28, "ocr": "heowned", "print": "he owned", "basis": "CHP-8.pdf physical page 3."}]}),
]

if len({row["statement_id"] for row in body_statements}) != len(body_statements):
    raise SystemExit("duplicate planned statement IDs")
new_statement_ids = {row["statement_id"] for row in body_statements}
if new_statement_ids & existing_statement_ids:
    raise SystemExit("planned statement ID collision")
for row in body_statements:
    q = row["qualifiers"]
    excerpt = "\n".join(source_lines[q["source_line_start"] - 1:q["source_line_end"]])
    if row["original_quote"] not in excerpt:
        raise SystemExit(f"quote is not reproducible in S0 source: {row['statement_id']}")
    if not (23 <= q["source_line_start"] <= q["source_line_end"] <= 28):
        raise SystemExit(f"statement line range outside segment: {row['statement_id']}")
    mentioned = set(q.get("mentioned_candidate_ids", []))
    if row.get("subject_candidate_id"):
        mentioned.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"):
        mentioned.add(row["object_candidate_id"])
    if not mentioned <= candidate_ids | new_candidate_ids:
        raise SystemExit(f"statement references missing candidate: {row['statement_id']}")

updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] == SEGMENT_ID:
        row.update({
            "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L24-28",
            "note": "P.205 body read against CHP-8.pdf physical p.3; page marker L23 is layout metadata. Footnotes 1-4 remain in composite source segment L130-133. The last name in L28 continues on p.206, so the Car(o) painting-count statement remains open until the next segment.",
        })
    updated_coverage.append(row)

preview = {
    "mode": "dry-run",
    "segment": SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(body_statements),
    "coverage": {SEGMENT_ID: "reviewed/partial"},
    "footnotes_pending": ["p.205 notes 1-4 at source lines 130-133"],
    "continuation_pending": {"statement_id": "st-chp8-p205-roomer-owned-three-saraceni-paintings-open", "next_segment_id": NEXT_SEGMENT_ID},
    "ocr_corrections": ["strength ofliis -> strength of his"],
    "unresolved_scan_reading": ["small mark after 'Scandinavia' not normalized"],
    "mention_preview": [{"candidate_id": row["candidate_id"], "surface": row["surface_form"], "start": int(row["start_char"]), "end": int(row["end_char"])} for row in new_mentions[:12]],
    "statement_ids": [row["statement_id"] for row in body_statements],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write validated tables and create recovery backups")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
statement_rows.extend(body_statements)
write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
write_csv_atomic(mention_path, mention_fields, mention_rows)
write_jsonl_atomic(statement_path, statement_rows)
write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
