"""Controlled S2 migration for p.290 footnotes L545-L550; dry-run unless --apply."""
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
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
BODY_SEG = "chp-10:10_CHP-10_intro:l240-251"
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_LINES_SHA = "8ca4d9669a823989543f90f31dc1e65039767c4e9ef5341dc5c7c1217fdebc47"
BACKUP_SUFFIX = ".bak-s2-chp10-p290-notes-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256("\n".join(source_lines[544:550]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.290 note lines L545-L550 changed")
if not source_lines[544].startswith("1 Letter from John Conduitt to McSwiny"):
    raise SystemExit("p.290 note 1 anchor changed")
if not source_lines[548].startswith("6 See letter from Joseph Smith to Samuel Hill"):
    raise SystemExit("p.290 OCR footnote marker precondition changed")
if not source_lines[549].startswith("6 Zanotti, U, p. 313"):
    raise SystemExit("p.290 OCR volume precondition changed")

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
if maximum != 9419:
    raise SystemExit(f"candidate sequence changed: {maximum}")
if cov.get(BODY_SEG, {}).get("migration_status") != "complete":
    raise SystemExit("p.290 body is not complete")
note_cov = cov.get(NOTES_SEG)
if not note_cov or (note_cov["disposition"], note_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes coverage changed")
if note_cov["source_line_ranges"] != "L492-544":
    raise SystemExit(f"consolidated notes range changed: {note_cov['source_line_ranges']}")

BODY_TARGETS = {
    "st-chp10-p290-client-letter-addressed": 1,
    "st-chp10-p290-client-critique": 1,
    "st-chp10-p290-devonshire-version-subject": 2,
    "st-chp10-p290-devonshire-version-brutus": 2,
    "st-chp10-p290-shovel-version-subject": 2,
    "st-chp10-p290-shovel-version-admiral": 2,
    "st-chp10-p290-devonshire-version-held-bingley": 2,
    "st-chp10-p290-shovel-version-held-bingley": 2,
    "st-chp10-p290-richmond-dining-room": 3,
    "st-chp10-p290-written-description": 3,
    "st-chp10-p290-mcswiny-reply-letter": 4,
    "st-chp10-p290-single-story-constraint": 4,
    "st-chp10-p290-marlborough-monument-example": 4,
    "st-chp10-p290-marlborough-iconographic-limits": 4,
    "st-chp10-p290-morice-purchase": 5,
    "st-chp10-p290-fratta-drawings": 6,
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(BODY_TARGETS) <= by_sid.keys():
    raise SystemExit("p.290 body footnote targets changed")
for sid, marker in BODY_TARGETS.items():
    qualifiers = by_sid[sid].get("qualifiers", {})
    if qualifiers.get("footnote_marker") != marker or not qualifiers.get("footnote_text_pending"):
        raise SystemExit(f"p.290 body footnote state changed: {sid}")

E = {
    "john_conduitt": "cand-0820", "munby": "cand-3708", "mcswiny": "cand-1466",
    "devonshire_person": "cand-0918",
    "devonshire_work": "cand-9016", "devonshire_altered_version": "cand-9020",
    "shovel_person": "cand-9021", "shovel_altered_version": "cand-9022",
    "richmond": "cand-2194", "barber_institute": "cand-9386", "shovel_table_work": "cand-9394",
    "vertue": "cand-8933", "vertue_notebooks": "cand-7255", "joseph_smith": "cand-2440",
    "samuel_hill": "cand-1300", "zanotti_book": "cand-7115", "fratta": "cand-1076",
    "scheme": "cand-9007", "goodwood": "cand-9025", "bingley": "cand-0376",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("conduitt_1729_letter", "Letter from John Conduitt to McSwiny, 4 June 1729 (reported in p.290 note 1)", "archive", "Haskell reports this letter among the Conduitt papers at the Library of King's College, Cambridge. The letter was not independently consulted.", 545),
    ("conduitt_papers", "Conduitt Papers (collection named in p.290 note 1)", "archive", "Archival collection reported by Haskell as holding the 4 June 1729 Conduitt-to-McSwiny letter; exact archival arrangement not independently checked.", 545),
    ("kings_college", "King's College, Cambridge (library named in p.290 note 1)", "institution", "Repository named by Haskell for the Conduitt papers; present custody and institutional record not independently checked.", 545),
    ("haskell_person", "Francis Haskell (author named in p.290 note 1)", "person", "Surname citation in p.290 note 1; bibliography contains more than one Haskell item dated 1967, so the exact cited work is not assigned here.", 545),
    ("haskell_1967_locator", "Haskell, 1967 (citation in p.290 note 1; exact work unresolved)", "archive", "The citation may correspond to more than one Haskell 1967 bibliography entry. Preserve the shorthand and do not choose a title before full bibliography reconciliation.", 545),
    ("mcswiny_conduitt_1730_letter", "Letter from McSwiny to John Conduitt, 27 September 1730 (p.290 note 4)", "archive", "Footnote 4 identifies the date and correspondent and cross-refers to note 1. Do not merge with the separate 4 June 1729 letter or the matching date citation in p.291 note 3 before S3 comparison.", 548),
    ("smith_hill_1729_letter", "Letter from Joseph Smith to Samuel Hill, 26 November 1729 (p.290 note 5)", "archive", "Cited by Haskell as published by W. H. Chaloner in connection with Morice's purchase; neither the letter nor its publication was independently consulted.", 549),
    ("chaloner_person", "W. H. Chaloner (author cited in p.290 note 5)", "person", "The note gives surname only. The book bibliography contains a W. H. Chaloner entry; the publication-to-note link is recorded as a local bibliographic match, not independent consultation.", 549),
    ("chaloner_article", "The Egertons in Italy and the Netherlands, 1729–1734 (W. H. Chaloner)", "archive", "Bibliography entry at 21_CHP-21Bibliography.md L328–329; p.290 note 5 says the Smith-to-Hill letter was published by Chaloner. The article was not independently consulted.", 549),
]
new_candidates = []
C = {}
for index, (key, name, kind, detail, line) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{index:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES_SEG}#L{line}",
    })

SEGMENT_START, SEGMENT_END = 491, 634
segment_text = "\n".join(source_lines[SEGMENT_START - 1:SEGMENT_END])
segment_offsets = {}
offset = 0
for line_no in range(SEGMENT_START, SEGMENT_END + 1):
    segment_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

new_mentions = []
new_mids = set()


def add_mention(local_id, line_no, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p290-notes-{local_id}"
    if mention_id in mids or mention_id in new_mids:
        raise SystemExit(f"duplicate mention: {mention_id}")
    if candidate_id not in cids | {row["candidate_id"] for row in new_candidates}:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    source_line = source_lines[line_no - 1]
    positions, start_at = [], 0
    while True:
        found = source_line.find(surface, start_at)
        if found < 0:
            break
        positions.append(found)
        start_at = found + max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = segment_offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEG, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mids.add(mention_id)


add_mention("n1-letter-date", 545, "4 June 1729", C["conduitt_1729_letter"], "Date of Haskell's reported archival letter; not independently consulted.")
add_mention("n1-conduitt", 545, "John Conduitt", E["john_conduitt"], "Sender named in Haskell's report.")
add_mention("n1-mcswiny", 545, "McSwiny", E["mcswiny"], "Recipient named in Haskell's report.")
add_mention("n1-papers", 545, "Conduitt papers", C["conduitt_papers"], "Collection label reproduced from Haskell; not independently checked.")
add_mention("n1-library", 545, "Library of King’s College, Cambridge", C["kings_college"], "Repository wording as OCR-transcribed; p.290 scan checked.")
add_mention("n1-munby", 545, "A. N. L. Munby", E["munby"], "Existing accepted-person candidate reused; retain printed initials.")
add_mention("n1-haskell", 545, "Haskell", C["haskell_person"], "Author named in the source citation.")
add_mention("n1-haskell-year", 545, "1967", C["haskell_1967_locator"], "Year in the printed citation; exact Haskell work remains unresolved because the bibliography has multiple entries for that year.")

add_mention("n2-devonshire-version", 546, "The Duke of Devonshire thus altered", E["devonshire_altered_version"], "Anaphoric work description for the altered Bingley-held version discussed in the body.")
add_mention("n2-devonshire-richmond-version", 546, "another version of the one", E["devonshire_work"], "Haskell's inferred alternate version of the Ricci-collaborated Devonshire monument; object identity is not settled.")
add_mention("n2-richmond", 546, "Duke of Richmond", E["richmond"], "Owner named in Haskell's source-time report.")
add_mention("n2-barber", 546, "Barber Institute", E["barber_institute"], "Source-time location wording, not current-holding verification.")
add_mention("n2-shovel-version", 546, "The one of Sir Cloudesly Shovel", E["shovel_altered_version"], "Anaphoric work description for the untraced altered version.")
add_mention("n2-shovel-richmond-version", 546, "a second version of the one belonging to the Duke of Richmond", E["shovel_table_work"], "Haskell's qualified inferred version link; the physical work was not traced.")

add_mention("n3-vertue", 547, "Vertue", E["vertue"], "Bibliographic source named in the footnote.")
add_mention("n3-locator", 547, "V, p. 149", E["vertue_notebooks"], "Volume/page locator; the cited page was not independently read.")
add_mention("n4-mcswiny", 548, "McSwiny", E["mcswiny"], "Sender named by the footnote.")
add_mention("n4-conduitt", 548, "John Conduitt", E["john_conduitt"], "Recipient named by the footnote.")
add_mention("n4-date", 548, "27 September 1730", C["mcswiny_conduitt_1730_letter"], "Date of the reported letter; do not merge with p.291 note 3 before S3.")

add_mention("n5-smith", 549, "Joseph Smith", E["joseph_smith"], "Sender named in the cited letter.")
add_mention("n5-hill", 549, "Samuel Hill", E["samuel_hill"], "Recipient named in the cited letter.")
add_mention("n5-date", 549, "26 November 1729", C["smith_hill_1729_letter"], "Date of the letter; print footnote number is 5 although S0 OCR reads 6.")
add_mention("n5-chaloner", 549, "Chaloner", C["chaloner_person"], "Surname as printed; W. H. initials are supplied by the book bibliography.")

add_mention("n6-zanotti", 550, "Zanotti", E["zanotti_book"], "The book bibliography's Zanotti work; the OCR volume reads U but the scan reads II.")

by_candidate = {row["candidate_id"]: row for row in candidates}
candidate_detail_additions = {
    "cand-9034": " P.290 note 4 also cites a McSwiny-to-Conduitt letter dated 27 September 1730 for the monument-scheme reply. Its exact relationship to this note-3 Canaletto correspondence candidate is deferred to S3; do not infer identity from matching sender/date alone.",
}
for cid, addition in candidate_detail_additions.items():
    if cid not in by_candidate:
        raise SystemExit(f"candidate update target missing: {cid}")
    if addition.strip() not in by_candidate[cid].get("detail", ""):
        by_candidate[cid]["detail"] = (by_candidate[cid].get("detail", "").rstrip() + addition).strip()

BODY_LINKS = {
    1: ["st-chp10-p290-client-letter-addressed", "st-chp10-p290-client-critique"],
    2: ["st-chp10-p290-devonshire-version-subject", "st-chp10-p290-devonshire-version-brutus", "st-chp10-p290-shovel-version-subject", "st-chp10-p290-shovel-version-admiral", "st-chp10-p290-devonshire-version-held-bingley", "st-chp10-p290-shovel-version-held-bingley"],
    3: ["st-chp10-p290-richmond-dining-room", "st-chp10-p290-written-description"],
    4: ["st-chp10-p290-mcswiny-reply-letter", "st-chp10-p290-single-story-constraint", "st-chp10-p290-marlborough-monument-example", "st-chp10-p290-marlborough-iconographic-limits"],
    5: ["st-chp10-p290-morice-purchase"],
    6: ["st-chp10-p290-fratta-drawings"],
}

new_statements = []
new_sids = set()


def add_statement(local_id, line_no, subject, obj, predicate, claim, qualification,
                  mentioned, speaker, layer, marker, relation=False, citations=None,
                  corrections=None, cited_not_consulted=False, cross_reference=None):
    statement_id = f"st-chp10-p290-note{marker}-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement: {statement_id}")
    quote = source_lines[line_no - 1]
    if quote not in segment_text:
        raise SystemExit(f"source quote missing: {statement_id}")
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 290, "pdf_physical_page": 19, "claim": claim,
        "speaker": speaker, "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation, "footnote_marker": marker,
        "related_body_statement_ids": BODY_LINKS[marker],
    }
    if citations:
        qualifiers["citations"] = citations
    if corrections:
        qualifiers["ocr_corrections"] = corrections
    if cross_reference:
        qualifiers["cross_reference"] = cross_reference
    if cited_not_consulted:
        qualifiers["cited_material_not_independently_consulted"] = True
    new_statements.append({
        "statement_id": statement_id, "segment_id": NOTES_SEG,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
    })
    new_sids.add(statement_id)
    return statement_id


S = {}
S["n1-letter-direction"] = add_statement(
    "letter-direction", 545, C["conduitt_1729_letter"], E["john_conduitt"],
    "haskell_reports_conduitt_letter_to_mcswiny",
    "Haskell identifies a letter from John Conduitt to McSwiny dated 4 June 1729.",
    "The letter is reported through Haskell and was not independently consulted; the note's repository and source claims remain attributed.",
    [C["conduitt_1729_letter"], E["john_conduitt"], E["mcswiny"]],
    "Haskell, footnote", "authorial footnote reporting correspondence", 1, relation=True,
    cited_not_consulted=True,
)
S["n1-letter-location"] = add_statement(
    "letter-location", 545, C["conduitt_1729_letter"], C["conduitt_papers"],
    "haskell_reports_letter_kept_in_collection_at_institution",
    "Haskell reports the letter among the Conduitt papers in the Library of King's College, Cambridge.",
    "Repository description is Haskell's report, not an independently checked archival record or statement of present custody.",
    [C["conduitt_1729_letter"], C["conduitt_papers"], C["kings_college"]],
    "Haskell, footnote", "authorial footnote reporting archival location", 1,
    cited_not_consulted=True,
)
S["n1-munby-credit"] = add_statement(
    "munby-credit", 545, C["haskell_person"], E["munby"],
    "haskell_credits_munby_with_pointing_out_correspondence",
    "Haskell says A. N. L. Munby pointed this correspondence out to him.",
    "This records Haskell's acknowledgment; it does not establish who first discovered the letter or an independent provenance history.",
    [C["haskell_person"], E["munby"], C["conduitt_1729_letter"]],
    "Haskell, footnote", "authorial acknowledgment in footnote", 1, relation=True,
)
S["n1-haskell-citation"] = add_statement(
    "haskell-1967-citation", 545, None, C["haskell_1967_locator"], "footnote_citation",
    "P.290 note 1 cites 'Haskell, 1967'; the exact Haskell 1967 work is unresolved.",
    "The bibliography contains multiple Haskell entries dated 1967. Preserve the citation as printed and do not assign a title or read the cited work into evidence.",
    [C["haskell_person"], C["haskell_1967_locator"]],
    "Haskell, footnote", "bibliographic pointer", 1,
    citations=[{"source_candidate_id": C["haskell_1967_locator"], "locator": "Haskell, 1967"}],
    cited_not_consulted=True,
)
S["n2-devonshire-version"] = add_statement(
    "devonshire-alternate-version", 546, E["devonshire_altered_version"], E["devonshire_work"],
    "haskell_infers_alternate_version_of",
    "Haskell says the altered Duke of Devonshire painting must be another version of the monument formerly owned by the Duke of Richmond and described as then at the Barber Institute.",
    "Retain 'must be' as Haskell's inference. The source-time 'now' is not a current-holding verification; the two version candidates are not merged.",
    [E["devonshire_altered_version"], E["devonshire_work"], E["richmond"], E["barber_institute"]],
    "Haskell, footnote", "authorial footnote with qualified version inference", 2, relation=True,
)
S["n2-shovel-version"] = add_statement(
    "shovel-alternate-version", 546, E["shovel_altered_version"], E["shovel_table_work"],
    "haskell_infers_second_version_of",
    "Haskell says the untraced Sir Cloudesly Shovel painting must have been a second version of the one belonging to the Duke of Richmond.",
    "The work had not been traced; retain 'must have been' as Haskell's inference and do not merge it with the table/list candidate.",
    [E["shovel_altered_version"], E["shovel_table_work"], E["shovel_person"], E["richmond"]],
    "Haskell, footnote", "authorial footnote with qualified version inference", 2, relation=True,
)
S["n3-vertue-citation"] = add_statement(
    "vertue-citation", 547, None, E["vertue_notebooks"], "footnote_citation",
    "P.290 note 3 cites Vertue, volume V, page 149, for the preceding account of display at Goodwood.",
    "The cited page was not independently consulted; this repeats the same locator already cited for the p.289 Goodwood list without treating that list as identity proof.",
    [E["vertue"], E["vertue_notebooks"], E["goodwood"]],
    "Haskell, footnote", "bibliographic pointer", 3,
    citations=[{"source_candidate_id": E["vertue_notebooks"], "volume": "V", "page": "149"}],
    cited_not_consulted=True,
)
S["n4-letter-citation"] = add_statement(
    "mcswiny-conduitt-letter", 548, None, C["mcswiny_conduitt_1730_letter"], "footnote_citation",
    "P.290 note 4 identifies a McSwiny-to-John Conduitt letter dated 27 September 1730 and cross-refers to note 1 for source context.",
    "The letter was not independently consulted. Do not merge it with the separately described 4 June 1729 letter or the same-date p.291 note 3 citation before S3 comparison.",
    [C["mcswiny_conduitt_1730_letter"], E["mcswiny"], E["john_conduitt"]],
    "Haskell, footnote", "bibliographic pointer to correspondence", 4,
    cited_not_consulted=True, cross_reference={"printed_note": 1, "target": "p.290 note 1"},
)
S["n5-smith-hill-citation"] = add_statement(
    "smith-hill-letter-citation", 549, C["smith_hill_1729_letter"], C["chaloner_article"],
    "haskell_cites_letter_published_by_chaloner",
    "Haskell cites a letter from Joseph Smith to Samuel Hill dated 26 November 1729, published by W. H. Chaloner, in support of the Morice purchase account.",
    "Neither the letter nor Chaloner's publication was independently consulted. The printed marker is 5; S0 OCR misreads it as 6, corrected only in this S2 record.",
    [C["smith_hill_1729_letter"], E["joseph_smith"], E["samuel_hill"], C["chaloner_person"], C["chaloner_article"]],
    "Haskell, footnote", "authorial footnote citing a published letter", 5,
    relation=False,
    citations=[{"source_candidate_id": C["chaloner_article"], "reference_as_printed": "published by Chaloner"}],
    corrections=[{"source_line": 549, "ocr": "6", "print": "5", "basis": "CHP-10.pdf physical page 19"}],
    cited_not_consulted=True,
)
S["n6-zanotti-citation"] = add_statement(
    "zanotti-citation", 550, None, E["zanotti_book"], "footnote_citation",
    "P.290 note 6 cites Zanotti, volume II, page 313, for the preceding statement about Fratta's drawings.",
    "The bibliography identifies the cited work, but page 313 was not independently consulted. S0 OCR reads the volume as U; the scan reads II.",
    [E["zanotti_book"], E["fratta"]],
    "Haskell, footnote", "bibliographic pointer", 6,
    citations=[{"source_candidate_id": E["zanotti_book"], "volume": "II", "page": "313"}],
    corrections=[{"source_line": 550, "ocr": "U", "print": "II", "basis": "CHP-10.pdf physical page 19"}],
    cited_not_consulted=True,
)

note_statement_ids = {marker: [] for marker in range(1, 7)}
for statement_id, row in S.items():
    marker = next(item["qualifiers"]["footnote_marker"] for item in new_statements if item["statement_id"] == row)
    note_statement_ids[marker].append(row)
for marker, body_ids in BODY_LINKS.items():
    if not set(body_ids) <= by_sid.keys():
        raise SystemExit(f"missing p.290 body statements for note {marker}")
    note_line = 544 + marker
    for sid in body_ids:
        qualifiers = by_sid[sid]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_segment"] = NOTES_SEG
        qualifiers["footnote_source_line"] = note_line
        qualifiers["footnote_note_statement_ids"] = note_statement_ids[marker]
        qualifiers["cited_material_not_independently_consulted"] = True

# Keep current coverage notes current without rewriting immutable S0 source text.
old_body_note = {row["segment_id"]: row for row in coverage}[BODY_SEG]["note"]
pending_clause = "Notes 1-6 remain in the separate consolidated notes segment and are not duplicated in this body segment."
if pending_clause not in old_body_note:
    raise SystemExit("p.290 coverage note no longer has the expected pending clause")
cov[BODY_SEG]["note"] = old_body_note.replace(
    pending_clause,
    "Notes 1-6 are in the separate consolidated notes segment and are linked to their body statements; they are not duplicated in this body segment.",
)
notes = cov[NOTES_SEG]
if "L545 onward remains pending." not in notes.get("note", ""):
    raise SystemExit("p.290 consolidated-notes coverage note changed")
notes["source_line_ranges"] = "L492-550"
notes["note"] = notes["note"].replace("L545 onward remains pending.", "L551 onward remains pending.")
notes["note"] += " P.290 notes 1-6 at L545-L550 are now migrated and linked to body markers 1-6. The scan confirms printed note 5 where S0 OCR reads 6, and Zanotti volume II where S0 reads U; these corrections exist only in S2. The separately cited 27 September 1730 McSwiny-Conduitt letter remains a distinct candidate from the same-date p.291 note 3 citation until S3 comparison."

# Validate exact anchor non-overlap and all candidate/statement foreign keys.
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
all_candidate_ids = cids | new_candidate_ids
for mention in new_mentions:
    if mention["candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"unresolved mention candidate: {mention['mention_id']}")
by_segment = {}
for mention in new_mentions:
    by_segment.setdefault(mention["segment_id"], []).append(mention)
for segment_id, rows in by_segment.items():
    rows.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
    for left, right in zip(rows, rows[1:]):
        if int(right["start_char"]) < int(left["end_char"]):
            raise SystemExit(f"overlapping mention anchors: {left['mention_id']} / {right['mention_id']}")
for statement in new_statements:
    if statement["object_candidate_id"] and statement["object_candidate_id"] not in all_candidate_ids:
        raise SystemExit(f"unknown statement object: {statement['statement_id']}")
    for cid in statement["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in all_candidate_ids:
            raise SystemExit(f"unknown statement mention candidate: {statement['statement_id']} {cid}")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the validated p.290 note migration")
args = parser.parse_args()
print(json.dumps({
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "source_segment": NOTES_SEG,
    "new_candidates": [row["candidate_id"] for row in new_candidates],
    "new_candidate_count": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "body_markers_linked": {str(marker): len(ids) for marker, ids in BODY_LINKS.items()},
    "coverage": {"notes_ranges": notes["source_line_ranges"], "notes_status": notes["migration_status"]},
    "ocr_corrections": ["L549 footnote marker 6 -> printed 5", "L550 volume U -> printed II"],
}, ensure_ascii=False, indent=2))
if not args.apply:
    print("dry-run only; no tables written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
write_csv(cp, cf, candidates + new_candidates)
write_csv(mp, mf, mentions + new_mentions)
write_jsonl(sp, statements + new_statements)
write_csv(vp, vf, [cov[row["segment_id"]] for row in coverage])
print(f"applied; four recovery copies use suffix {BACKUP_SUFFIX}")
