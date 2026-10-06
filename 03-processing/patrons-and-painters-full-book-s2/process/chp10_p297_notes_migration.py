"""Controlled migration of p.297 notes 1-6; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
BIB = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
BODY_SEG = "chp-10:10_CHP-10_intro:l332-343"
PREV_BODY_SEG = "chp-10:10_CHP-10_intro:l318-330"
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
BODY_LINE_SHA = "8758c0960f73f23eb15c805a293e9bf02d2d32ce69bf6a9f86016de3a35cb48b"
NOTES_SHA = "2130123c8de7c64d9b6fce17b5ea1a966760712749826e28a8bbb92349184b8e"
BACKUP_SUFFIX = ".bak-s2-chp10-p297-notes-20261002"
EXPECTED_MAX_CANDIDATE = 9467


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
        temp_path = Path(stream.name)
    temp_path.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(stream.name)
    temp_path.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("canonical source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_line = source_lines[342]
note_block = "\n".join(source_lines[569:574])
if hashlib.sha256(body_line.encode("utf-8")).hexdigest() != BODY_LINE_SHA:
    raise SystemExit("canonical p.297 note excerpt at L343 changed")
if hashlib.sha256(note_block.encode("utf-8")).hexdigest() != NOTES_SHA:
    raise SystemExit("p.297 composite note lines L570-L574 changed")
if not body_line.startswith("In 1723 Juvarra commissioned a painting from Marco Ricci"):
    raise SystemExit("L343 is no longer the complete p.297 note 1 continuation")
if not source_lines[569].startswith('1 "Gabrielli, 1950, pp. 204-11'):
    raise SystemExit("p.297 note 1 bibliography opening changed")
if not source_lines[570].startswith("2 Battisti, 1958"):
    raise SystemExit("p.297 note 2 anchor changed")
if not source_lines[571].startswith("3 It is true that Amigoni"):
    raise SystemExit("p.297 note 3 anchor changed")
if not source_lines[572].startswith("4 For the pressures put on Tiepolo"):
    raise SystemExit("p.297 note 4 anchor changed")
if not source_lines[573].startswith("5 Donzelli, pp. 209 and 90. 6 A. Longhi."):
    raise SystemExit("p.297 notes 5-6 anchor changed")

bib_text = BIB.read_text(encoding="utf-8-sig")
required_bib_fragments = (
    "Battisti, E.:",
    "Juvarra a Sant’Ildefonso",
    "1958, pp. 273-297.",
    "Per la storia del viaggio in Ispagna",
    "1914.",
    "Donzelli, Carlo: I pittori Veneti del Settecento, Firenze 1957.",
    "Longhi, Alessandro: Compendio delle vite",
    "Venezia 1762.",
    "Viale, V.:",
    "1950-1, pp. 161-169.",
)
if not all(fragment in bib_text for fragment in required_bib_fragments):
    raise SystemExit("one or more local bibliography matches changed")
if "Gabrielli, 1950" in bib_text:
    raise SystemExit("Gabrielli unexpectedly appears in the local bibliography; review before migration")

cp, mp, sp, vp = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
by_cid = {row["candidate_id"]: row for row in candidates}
by_sid = {row["statement_id"]: row for row in statements}

maximum = max(int(re.search(r"\d+", cid).group()) for cid in cids)
if maximum != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: {maximum}")
expected_coverage = {
    BODY_SEG: ("reviewed", "partial", "L333-342"),
    PREV_BODY_SEG: ("reviewed", "complete", "L319-330"),
    NOTES_SEG: ("reviewed", "partial", "L492-569"),
}
for segment_id, (disposition, migration_status, source_range) in expected_coverage.items():
    row = cov.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != (
        disposition, migration_status, source_range
    ):
        raise SystemExit(f"coverage changed: {segment_id}: {row}")
if by_cid["cand-9297"]["canonical_name"] != "Donzelli, p.82 (citation locator; title and edition unresolved)":
    raise SystemExit("existing Donzelli citation candidate changed")

BODY_LINKS = {
    1: ["st-chp10-p296-juvarra-artistic-director-and-commissions-open"],
    2: ["st-chp10-p297-madrid-decoration-plan", "st-chp10-p297-madrid-school-allocation"],
    3: ["st-chp10-p297-amigoni-madrid"],
    4: ["st-chp10-p297-tiepolo-spain-mission"],
    5: ["st-chp10-p297-fontebasso-winter-palace"],
    6: ["st-chp10-p297-guarana-iphigenia"],
}
for marker, target_ids in BODY_LINKS.items():
    for sid in target_ids:
        row = by_sid.get(sid)
        if not row or row.get("qualifiers", {}).get("footnote_marker") != marker:
            raise SystemExit(f"body target changed for footnote {marker}: {sid}")
        if not row["qualifiers"].get("footnote_text_pending"):
            raise SystemExit(f"body footnote was already resolved: {sid}")

NEW_SPECS = [
    ("gabrielli_person", "Gabrielli (author cited at p.297 note 1; identity unresolved)", "person",
     "P.297 note 1 gives surname only. Do not infer a given name or merge with another Gabrielli.", f"{NOTES_SEG}#L570"),
    ("gabrielli_locator", "Gabrielli, 1950, pp.204-211 (citation locator; title unresolved)", "archive",
     "Unmatched short-form reference in p.297 note 1 for an account of Ricci and the Turin court; title and cited pages are unresolved and unread.", f"{NOTES_SEG}#L570"),
    ("viale_person", "V. Viale (author of the p.297 note 1 cited article; identity unresolved)", "person",
     "The footnote gives initial and surname only; keep identity distinct until S3.", f"{BODY_SEG}#L343"),
    ("viale_article", "V. Viale, Un dipinto del Pannini con la veduta orientale del Castello di Rivoli (1950-1951; citation locator)", "archive",
     "Matched by author and year to the local bibliography. P.297 note 1 cites p.161; article and cited page were not consulted.", f"{BODY_SEG}#L343"),
    ("castello_rivoli", "Castello di Rivoli (place named in Juvarra’s 1723 proposal)", "place",
     "P.297 note 1 says the painting indicated Juvarra’s proposals for this site; the statement does not identify the proposal’s full contents.", f"{BODY_SEG}#L343"),
    ("ricci_1723_painting", "Unidentified painting commissioned from Marco Ricci for Juvarra’s Castello di Rivoli proposal (1723)", "work",
     "P.297 note 1 gives no title or location. Keep distinct from the grouped school allocations that follow; the note does not say whether it is included in their count.", f"{BODY_SEG}#L343"),
    ("juvarra_school_group", "Juvarra’s cited pictures from Roman, Venetian and Turinese artists (p.297 note 1)", "work",
     "The note counts four Roman pictures (two each by Pannini and Locatelli) and one each from a Venetian and a Turinese artist. Whether the earlier Marco Ricci painting is included is unresolved.", f"{BODY_SEG}#L343"),
    ("roman_painting", "Roman painting as a school in Juvarra’s p.297 note 1 comparison", "term",
     "Source-local art-historical category used for the four pictures ordered from Rome; compare and align with other Roman-painting candidates only at S3.", f"{BODY_SEG}#L343"),
    ("unnamed_venetian_artist", "Unnamed Venetian artist in Juvarra’s p.297 note 1 order", "person",
     "One artist is described only by regional association; do not infer an identity or equate the mention with Marco Ricci.", f"{BODY_SEG}#L343"),
    ("unnamed_turinese_artist", "Unnamed Turinese artist in Juvarra’s p.297 note 1 order", "person",
     "One artist is described only by regional association; no name or further identity evidence is supplied.", f"{BODY_SEG}#L343"),
    ("battisti_person", "E. Battisti (author cited at p.297 note 2; identity unresolved)", "person",
     "Local bibliography identifies the initial and surname. Keep separate from existing generic Battisti candidate cand-3499 until S3.", f"{NOTES_SEG}#L571"),
    ("battisti_article", "E. Battisti, Juvarra a Sant’Ildefonso (Commentari, 1958, pp.273-297; citation locator)", "archive",
     "Matched to the local bibliography; article and cited pages were not consulted.", f"{NOTES_SEG}#L571"),
    ("brunetti_person", "M. Brunetti (author cited at p.297 note 4; identity unresolved)", "person",
     "P.297 note 4 supplies initial and surname. Keep distinct from other Brunetti candidates until S3.", f"{NOTES_SEG}#L573"),
    ("brunetti_article", "M. Brunetti, Per la storia del viaggio in Ispagna di Gio. Batt. Tiepolo (1914; citation locator)", "archive",
     "Matched to the local bibliography by author, title and year; article was not consulted.", f"{NOTES_SEG}#L573"),
    ("donzelli_person", "Carlo Donzelli (author of I pittori Veneti del Settecento)", "person",
     "Author matched to the local bibliography; do not merge with candidates bearing only a surname until S3.", f"{NOTES_SEG}#L574"),
    ("longhi_book", "Alessandro Longhi, Compendio delle vite de’ pittori veneziani istorici più rinomati del presente secolo (Venezia, 1762; citation locator)", "archive",
     "P.297 note 6 gives A. Longhi only; the local bibliography supplies the matching title and year. The book and passage were not consulted.", f"{NOTES_SEG}#L574"),
]
new_candidates = []
C = {}
for offset, (key, name, kind, detail, source_ref) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{offset:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": source_ref,
    })

# Reuse chapter-wide/index candidates for named people and places; leave global identity for S3.
E = {
    "juvarra": "cand-1339", "marco_ricci": "cand-2149", "pannini": "cand-1827",
    "locatelli": "cand-1409", "amigoni": "cand-0094", "giaquinto": "cand-1165",
    "goya": "cand-1216", "madrid": "cand-1481", "naples": "cand-1722",
    "venice": "cand-2719", "sebastiano_ricci": "cand-2154", "turin": "cand-2662",
    "tiepolo": "cand-2569", "spain": "cand-5120", "longhi": "cand-1424",
    "donzelli_book": "cand-9297", "generic_battisti": "cand-3499",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing reused candidate {key}: {cid}")

# The p.82 locator already points to the same Carlo Donzelli book in the local bibliography.
by_cid[E["donzelli_book"]]["canonical_name"] = (
    "Carlo Donzelli, I pittori Veneti del Settecento (Firenze, 1957; citation locator)"
)
by_cid[E["donzelli_book"]]["detail"] = (
    "Matched to the local bibliography. Reused for the p.278 note 3 citation at p.82 and p.297 note 5 at "
    "pp.209 and 90. The book and cited pages were not independently consulted."
)

new_mentions = []
new_mids = set()


def segment_offsets(start_line, end_line):
    text = "\n".join(source_lines[start_line - 1:end_line])
    offsets = {}
    offset = 0
    for line_no in range(start_line, end_line + 1):
        offsets[line_no] = offset
        offset += len(source_lines[line_no - 1]) + 1
    return text, offsets


SEGMENT_TEXT = {
    BODY_SEG: segment_offsets(332, 343),
    NOTES_SEG: segment_offsets(491, 634),
}


def add_mention(local_id, segment_id, line_no, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p297-{local_id}"
    if mention_id in mids or mention_id in new_mids:
        raise SystemExit(f"duplicate mention id: {mention_id}")
    allowed_ids = cids | {row["candidate_id"] for row in new_candidates}
    if candidate_id not in allowed_ids:
        raise SystemExit(f"missing candidate for mention {mention_id}: {candidate_id}")
    positions = []
    search_from = 0
    source_line = source_lines[line_no - 1]
    while True:
        pos = source_line.find(surface, search_from)
        if pos < 0:
            break
        positions.append(pos)
        search_from = pos + max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    segment_text, offsets = SEGMENT_TEXT[segment_id]
    start = offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mids.add(mention_id)


add_mention("n1-gabrielli-author", NOTES_SEG, 570, "Gabrielli", C["gabrielli_person"],
            "Surname-only cited author; identity unresolved.")
add_mention("n1-gabrielli-locator", NOTES_SEG, 570, "1950, pp. 204-11", C["gabrielli_locator"],
            "Short citation; no local bibliography match and no pages consulted.")
add_mention("n1-context-ricci", NOTES_SEG, 570, "Ricci", E["sebastiano_ricci"],
            "Note 1 is attached to the preceding Sebastiano Ricci commission statement; retain S3 identity review.")
add_mention("n1-context-turin", NOTES_SEG, 570, "Turin", E["turin"],
            "Place named in the cited account; source-local index mapping remains for S3.")
add_mention("n1-juvarra", BODY_SEG, 343, "Juvarra", E["juvarra"])
add_mention("n1-marco-ricci", BODY_SEG, 343, "Marco Ricci", E["marco_ricci"])
add_mention("n1-castello-rivoli", BODY_SEG, 343, "Castello di Rivoli", C["castello_rivoli"])
add_mention("n1-ricci-painting", BODY_SEG, 343, "a painting", C["ricci_1723_painting"])
add_mention("n1-spain", BODY_SEG, 343, "Spain", E["spain"])
add_mention("n1-roman-painting", BODY_SEG, 343, "Roman painting", C["roman_painting"])
add_mention("n1-school-picture-group", BODY_SEG, 343, "four pictures", C["juvarra_school_group"])
add_mention("n1-pannini", BODY_SEG, 343, "Pannini", E["pannini"])
add_mention("n1-locatelli", BODY_SEG, 343, "Locatelli", E["locatelli"])
add_mention("n1-unnamed-venetian", BODY_SEG, 343, "a Venetian", C["unnamed_venetian_artist"])
add_mention("n1-unnamed-turinese", BODY_SEG, 343, "a Turinese artist", C["unnamed_turinese_artist"])
add_mention("n1-viale-author", BODY_SEG, 343, "Viale", C["viale_person"])
add_mention("n1-viale-locator", BODY_SEG, 343, "1950-1, p. 161", C["viale_article"],
            "Local bibliography match; cited page not consulted.")

add_mention("n2-battisti-author", NOTES_SEG, 571, "Battisti", C["battisti_person"],
            "Initial supplied by the local bibliography; keep distinct from cand-3499 until S3.")
add_mention("n2-battisti-locator", NOTES_SEG, 571, "1958, pp. 273-97", C["battisti_article"],
            "Local bibliography match; cited pages not consulted.")

add_mention("n3-amigoni-1", NOTES_SEG, 572, "Amigoni", E["amigoni"], occurrence=0)
add_mention("n3-naples", NOTES_SEG, 572, "Naples", E["naples"])
add_mention("n3-venice", NOTES_SEG, 572, "Venice", E["venice"])
add_mention("n3-amigoni-2", NOTES_SEG, 572, "Amigoni", E["amigoni"], occurrence=1)
add_mention("n3-madrid", NOTES_SEG, 572, "Madrid", E["madrid"])
add_mention("n3-giaquinto", NOTES_SEG, 572, "Corrado Giaquinto", E["giaquinto"])
add_mention("n3-goya", NOTES_SEG, 572, "Goya", E["goya"])

add_mention("n4-tiepolo", NOTES_SEG, 573, "Tiepolo", E["tiepolo"])
add_mention("n4-spain", NOTES_SEG, 573, "Spain", E["spain"])
add_mention("n4-brunetti-author", NOTES_SEG, 573, "M. Brunetti", C["brunetti_person"])
add_mention("n4-brunetti-year", NOTES_SEG, 573, "1914", C["brunetti_article"],
            "Local bibliography match; article not consulted.")
add_mention("n5-donzelli-author", NOTES_SEG, 574, "Donzelli", C["donzelli_person"])
add_mention("n5-donzelli-pages", NOTES_SEG, 574, "pp. 209 and 90", E["donzelli_book"],
            "Local bibliography identifies the book; cited pages not consulted.")
add_mention("n6-longhi-author", NOTES_SEG, 574, "A. Longhi", E["longhi"])

new_statements = []
new_sids = set()


def add_statement(local_id, segment_id, start_line, end_line, marker, predicate, claim,
                  subject=None, obj=None, mentioned=(), relation=False, text_layer="footnote narrative",
                  qualification="", citations=(), related_body_ids=()):
    statement_id = f"st-chp10-p297-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement id: {statement_id}")
    qualifiers = {
        "source_line_start": start_line, "source_line_end": end_line,
        "printed_page": 297, "pdf_physical_page": 26,
        "claim": claim, "speaker": "Haskell",
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation,
        "footnote_marker": marker,
        "footnote_text_pending": False,
        "related_body_statement_ids": list(related_body_ids),
        "cited_material_not_independently_consulted": True,
    }
    if citations:
        qualifiers["citations"] = list(citations)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[start_line - 1:end_line]),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    new_statements.append(row)
    new_sids.add(statement_id)
    return statement_id


S = {}
S["gabrielli"] = add_statement(
    "note1-gabrielli-citation", NOTES_SEG, 570, 570, 1, "footnote_citation",
    "P.297 note 1 directs readers to Gabrielli (1950, pp.204-211) for an account of Ricci’s relations with the Turin court.",
    obj=C["gabrielli_locator"],
    mentioned=[C["gabrielli_person"], C["gabrielli_locator"], E["sebastiano_ricci"], E["turin"]],
    text_layer="bibliographic pointer",
    qualification="The short reference does not identify a title in the local bibliography; the cited pages were not consulted.",
    citations=[{"source_candidate_id": C["gabrielli_locator"], "year": "1950", "pages": "204-211",
                "bibliography_match": "unresolved"}],
    related_body_ids=BODY_LINKS[1],
)
S["commission"] = add_statement(
    "note1-juvarra-marco-ricci-commission", BODY_SEG, 343, 343, 1,
    "juvarra_commissioned_marco_ricci_painting_for_castello_di_rivoli_proposal_in_1723",
    "In 1723 Juvarra commissioned a painting from Marco Ricci to indicate his proposals for the Castello di Rivoli.",
    subject=E["juvarra"], obj=E["marco_ricci"],
    mentioned=[E["juvarra"], E["marco_ricci"], C["castello_rivoli"], C["ricci_1723_painting"]],
    relation=True,
    qualification="The painting is unidentified. The note does not say whether it is included in the school-allocation count that follows.",
    citations=[{"source_candidate_id": C["gabrielli_locator"], "year": "1950", "pages": "204-211",
                "bibliography_match": "unresolved"}],
    related_body_ids=BODY_LINKS[1],
)
S["allocation"] = add_statement(
    "note1-juvarra-school-allocation", BODY_SEG, 343, 343, 1,
    "juvarra_ordered_four_roman_pictures_and_one_each_from_venetian_and_turinese_artists",
    "The note says Juvarra showed a preference for Roman painting by ordering four pictures from there—two each by Pannini and Locatelli—compared with one each from a Venetian and a Turinese artist.",
    subject=E["juvarra"], obj=C["juvarra_school_group"],
    mentioned=[E["juvarra"], C["juvarra_school_group"], C["roman_painting"], E["pannini"],
               E["locatelli"], C["unnamed_venetian_artist"], C["unnamed_turinese_artist"], E["spain"]],
    relation=True,
    qualification="The note uses a comparison with Juvarra’s later Spanish commissions. It does not resolve whether Marco Ricci’s painting in the preceding sentence is part of these counts.",
    citations=[{"source_candidate_id": C["viale_article"], "year": "1950-1951", "page": "161",
                "bibliography_match": "local"}],
    related_body_ids=BODY_LINKS[1],
)
S["battisti"] = add_statement(
    "note2-battisti-citation", NOTES_SEG, 571, 571, 2, "footnote_citation",
    "P.297 note 2 cites E. Battisti’s 1958 article, pages 273-297.",
    obj=C["battisti_article"],
    mentioned=[C["battisti_person"], C["battisti_article"]],
    text_layer="bibliographic pointer",
    qualification="Matched to the local bibliography; the article and cited pages were not consulted.",
    citations=[{"source_candidate_id": C["battisti_article"], "year": "1958", "pages": "273-297",
                "bibliography_match": "local"}],
    related_body_ids=BODY_LINKS[2],
)
S["amigoni-born"] = add_statement(
    "note3-amigoni-born-naples", NOTES_SEG, 572, 572, 3, "amigoni_was_born_in_naples",
    "Haskell states that Amigoni was born in Naples.",
    subject=E["amigoni"], obj=E["naples"],
    mentioned=[E["amigoni"], E["naples"]],
    qualification="This is stated in Haskell’s footnote; no external source was consulted.",
    related_body_ids=BODY_LINKS[3],
)
S["amigoni-venice"] = add_statement(
    "note3-amigoni-working-life-venice", NOTES_SEG, 572, 572, 3,
    "amigoni_spent_working_life_in_venice_when_not_abroad",
    "Haskell says Amigoni spent his working life in Venice when he was not abroad.",
    subject=E["amigoni"], obj=E["venice"],
    mentioned=[E["amigoni"], E["venice"]],
    qualification="Preserve the explicit exception for periods when he was abroad.",
    related_body_ids=BODY_LINKS[3],
)
S["giaquinto-madrid"] = add_statement(
    "note3-giaquinto-followed-amigoni-to-madrid", NOTES_SEG, 572, 572, 3,
    "giaquinto_followed_amigoni_to_madrid_in_1753",
    "Haskell says Corrado Giaquinto followed Amigoni to Madrid in 1753.",
    subject=E["giaquinto"], obj=E["amigoni"],
    mentioned=[E["giaquinto"], E["amigoni"], E["madrid"]],
    relation=True,
    qualification="The footnote does not say this was Amigoni’s first or only Madrid visit; keep distinct from the body’s 1739 statement.",
    related_body_ids=BODY_LINKS[3],
)
S["giaquinto-goya"] = add_statement(
    "note3-giaquinto-influence-on-young-goya", NOTES_SEG, 572, 572, 3,
    "haskell_compares_giaquintos_influence_on_young_goya_as_greater_than_other_italian_painters",
    "Haskell judges Giaquinto’s influence on the young Goya to have been far greater than that of any other Italian painter.",
    subject=E["giaquinto"], obj=E["goya"],
    mentioned=[E["giaquinto"], E["goya"]],
    relation=True,
    text_layer="authorial evaluation",
    qualification="This is Haskell’s comparative assessment, not an independently verified influence measure.",
    related_body_ids=BODY_LINKS[3],
)
S["brunetti"] = add_statement(
    "note4-brunetti-citation", NOTES_SEG, 573, 573, 4, "footnote_citation",
    "P.297 note 4 directs readers to M. Brunetti (1914) on the pressures for Tiepolo to go to Spain.",
    obj=C["brunetti_article"],
    mentioned=[C["brunetti_person"], C["brunetti_article"], E["tiepolo"], E["spain"]],
    text_layer="bibliographic pointer",
    qualification="Matched to the local bibliography; the article was not consulted.",
    citations=[{"source_candidate_id": C["brunetti_article"], "year": "1914",
                "bibliography_match": "local"}],
    related_body_ids=BODY_LINKS[4],
)
S["donzelli"] = add_statement(
    "note5-donzelli-citation", NOTES_SEG, 574, 574, 5, "footnote_citation",
    "P.297 note 5 cites Carlo Donzelli’s book at pages 209 and 90.",
    obj=E["donzelli_book"],
    mentioned=[C["donzelli_person"], E["donzelli_book"]],
    text_layer="bibliographic pointer",
    qualification="Matched to the local bibliography; the book and cited pages were not consulted.",
    citations=[{"source_candidate_id": E["donzelli_book"], "pages": ["209", "90"],
                "bibliography_match": "local"}],
    related_body_ids=BODY_LINKS[5],
)
S["longhi"] = add_statement(
    "note6-longhi-citation", NOTES_SEG, 574, 574, 6, "footnote_citation",
    "P.297 note 6 cites A. Longhi; the local bibliography identifies the reference as Alessandro Longhi’s 1762 Compendio.",
    obj=C["longhi_book"],
    mentioned=[E["longhi"], C["longhi_book"]],
    text_layer="bibliographic pointer",
    qualification="The match is based on the local bibliography. The book and relevant passage were not consulted.",
    citations=[{"source_candidate_id": C["longhi_book"], "year": "1762",
                "title": "Compendio delle vite de’ pittori veneziani istorici più rinomati del presente secolo",
                "bibliography_match": "local"}],
    related_body_ids=BODY_LINKS[6],
)

all_candidate_ids = cids | {row["candidate_id"] for row in new_candidates}
for row in new_statements:
    q = row["qualifiers"]
    if row["object_candidate_id"] and row["object_candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"unknown object candidate: {row['statement_id']}")
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"unknown subject candidate: {row['statement_id']}")
    for cid in q["mentioned_candidate_ids"]:
        if cid not in all_candidate_ids:
            raise SystemExit(f"unknown mentioned candidate: {row['statement_id']} {cid}")
    for citation in q.get("citations", []):
        if citation["source_candidate_id"] not in all_candidate_ids:
            raise SystemExit(f"unknown citation candidate: {row['statement_id']}")
    if not row["original_quote"]:
        raise SystemExit(f"empty source quote: {row['statement_id']}")

# Refuse crossing or duplicate spans; nested named-author/citation mentions are avoided by design.
by_segment = {}
for row in new_mentions:
    by_segment.setdefault(row["segment_id"], []).append(row)
for segment_id, rows in by_segment.items():
    rows.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
    for left, right in zip(rows, rows[1:]):
        if int(right["start_char"]) < int(left["end_char"]):
            raise SystemExit(f"overlapping mention anchors in {segment_id}: {left['mention_id']} / {right['mention_id']}")

note_statement_ids_by_marker = {}
for row in new_statements:
    marker = row["qualifiers"]["footnote_marker"]
    note_statement_ids_by_marker.setdefault(marker, []).append(row["statement_id"])
for marker, body_ids in BODY_LINKS.items():
    for sid in body_ids:
        q = by_sid[sid]["qualifiers"]
        q["footnote_text_pending"] = False
        q["footnote_body_link_status"] = "linked"
        q["footnote_segment"] = NOTES_SEG
        q["footnote_source_line"] = {1: 570, 2: 571, 3: 572, 4: 573, 5: 574, 6: 574}[marker]
        q["footnote_note_statement_ids"] = note_statement_ids_by_marker[marker]
        if marker == 1:
            q["footnote_full_content_anchor"] = f"{BODY_SEG}#L343"

body_cov = cov[BODY_SEG]
body_cov["source_line_ranges"] = "L333-343"
body_cov["migration_status"] = "complete"
body_cov["note"] = (
    "Printed p.297 body and footnotes 1-6 have been read against CHP-10.pdf physical page 26. "
    "L343 is the canonical OCR excerpt containing the full printed note 1 continuation; composite-note L570 repeats only its Gabrielli opening. "
    "The p.296 Juvarra/Ricci commission sentence is closed and its marker 1 linked; markers 2-6 also link to note statements. "
    "No duplicate claims were created from the parallel whole-chapter OCR. Haskell's 1739 Amigoni passage and note 3's 1753 Giaquinto follow-up remain distinct."
)
prev_cov = cov[PREV_BODY_SEG]
prev_cov["note"] = (
    "Printed p.296 body is complete after p.297 closes the Juvarra/Ricci commission sentence. "
    "P.296 notes 2-3 at L568-L569 and p.297 note 1 at L343/L570 are migrated and linked to the Juvarra/Ricci statement."
)
note_cov = cov[NOTES_SEG]
note_cov["source_line_ranges"] = "L492-574"
note_cov["note"] = (
    "Merged-note source processed in order through p.297 notes 1-6. Note 1's full substantive text is in canonical body-segment L343; "
    "L570 repeats only its Gabrielli citation opening and is linked without duplicate fact statements. Notes 2-6 at L571-L574 are migrated. "
    "Local bibliography matches: Viale 1950-1951, Battisti 1958, Brunetti 1914, Donzelli 1957, Longhi 1762; Gabrielli 1950 remains an unmatched short citation. "
    "Cited publications/pages were not independently consulted. Next source range: p.298 note 1 at L575."
)

new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates):
    raise SystemExit("new candidate ID collision")
if len({row["mention_id"] for row in new_mentions}) != len(new_mentions):
    raise SystemExit("new mention ID collision")
if len({row["statement_id"] for row in new_statements}) != len(new_statements):
    raise SystemExit("new statement ID collision")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the checked migration")
args = parser.parse_args()
summary = {
    "candidates_added": len(new_candidates),
    "candidate_ids": [row["candidate_id"] for row in new_candidates],
    "mentions_added": len(new_mentions),
    "statements_added": len(new_statements),
    "body_markers_linked": sorted(BODY_LINKS),
    "body_coverage": body_cov["migration_status"],
    "notes_source_range": note_cov["source_line_ranges"],
    "next": "p.298 note 1 at L575",
}
if not args.apply:
    print("DRY RUN OK: " + json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0)

paths = (cp, mp, sp, vp)
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(cp, cf, candidates + new_candidates)
write_csv(mp, mf, mentions + new_mentions)
write_jsonl(sp, statements + new_statements)
write_csv(vp, vf, coverage)
print("APPLIED: " + json.dumps(summary, ensure_ascii=False))
