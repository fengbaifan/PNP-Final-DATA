"""Controlled S2 migration for p.292 footnotes L554-L557; dry-run unless --apply."""
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
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
BODY_SEG = "chp-10:10_CHP-10_intro:l268-277"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_LINES_SHA = "4becad5e2651d403bfc3b938388e23138aecbf1b4066f2922c6dd69cfa885405"
BACKUP_SUFFIX = ".bak-s2-chp10-p292-notes-20261002"


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
if hashlib.sha256("\n".join(source_lines[553:557]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.292 note lines L554-L557 changed")
if not source_lines[553].startswith("1 De Brosses, I, p. 282."):
    raise SystemExit("p.292 note 1 anchor changed")
if not source_lines[554].startswith("3 [William Beckford], I, p. 101."):
    raise SystemExit("p.292 note 3/4 anchor changed")
if not source_lines[555].startswith("8 Levey in Italian Studies"):
    raise SystemExit("p.292 note 5 OCR marker precondition changed")

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
if maximum != 9435:
    raise SystemExit(f"candidate sequence changed: {maximum}")
note_cov = cov.get(NOTES_SEG)
if not note_cov or (note_cov["disposition"], note_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes coverage changed")
if note_cov["source_line_ranges"] != "L492-553":
    raise SystemExit(f"consolidated notes range changed: {note_cov['source_line_ranges']}")
if cov.get(BODY_SEG, {}).get("migration_status") != "complete":
    raise SystemExit("p.292 body is not complete")

BODY_LINKS = {
    1: ["st-chp10-p292-canaletto-market"],
    2: ["st-chp10-p292-burney-testimony"],
    3: ["st-chp10-p292-beckford-testimony"],
    4: ["st-chp10-p292-canaletto-english-commissions"],
    5: ["st-chp10-p292-zuccarelli-career"],
    6: ["st-chp10-p292-tessin-family-and-palace", "st-chp10-p292-tessin-early-travel"],
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(sum(BODY_LINKS.values(), [])) <= by_sid.keys():
    raise SystemExit("p.292 body footnote targets changed")
for sid, marker in ((sid, marker) for marker, ids in BODY_LINKS.items() for sid in ids):
    qualifiers = by_sid[sid].get("qualifiers", {})
    if qualifiers.get("footnote_marker") != marker or not qualifiers.get("footnote_text_pending"):
        raise SystemExit(f"p.292 body footnote state changed: {sid}")

E = {
    "dr_burney": "cand-9039", "william_beckford": "cand-9040", "tessin": "cand-2552",
    "bjurstrom": "cand-7076",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("de_brosses_person", "Charles de Brosses (author named in p.292 note 1)", "person",
     "The p.292 note gives the surname; the book bibliography identifies Charles de Brosses. Identity and bibliographic matching remain subject to the full bibliography pass and S3.", 554),
    ("de_brosses_locator", "De Brosses, Lettres d'Italie, vol. I, p.282 (citation locator)", "archive",
     "P.292 note 1 locator. The book bibliography lists Charles de Brosses, Lettres d'Italie, 2 vols., Dijon 1927; the cited page was not independently consulted and the bibliography still awaits its source-order S2 review.", 554),
    ("burney_locator", "Burney, Musical Tours in Europe, vol. I, p.109 (citation locator)", "archive",
     "P.292 note 2 locator for the Burney testimony. The bibliography lists the two-volume edition edited by Percy Scholes, Oxford 1959; p.109 was not independently consulted.", 554),
    ("beckford_locator", "William Beckford, Italy, with sketches of Spain and Portugal, vol. I, p.101 (citation locator)", "archive",
     "P.292 note 3 locator for Beckford's reported response to Canaletto. The cited page was not independently consulted; bibliographic identification is local to the book bibliography.", 555),
    ("finberg_person", "Finberg (surname-only author cited at p.292 note 4)", "person",
     "The note cites Finberg, 1920-1; the book bibliography identifies Hilda Finberg. The cited work and author identity remain for the bibliography pass and S3 alignment.", 555),
    ("finberg_article", "Hilda Finberg, 'Canaletto in England' (Walpole Society, 1920-1; citation locator)", "archive",
     "The book bibliography lists the article in Walpole Society vols. IX and X; p.292 note 4 gives the short citation Finberg, 1920-1. The article was not independently consulted.", 555),
    ("levey_person", "M. Levey (author cited at p.292 note 5)", "person",
     "The note gives only Levey; the book bibliography lists M. Levey for the matching article. Possible identity with cand-8657, cand-9338, or the existing Levey KU candidate is deferred to S3.", 556),
    ("levey_article", "M. Levey, 'Francesco Zuccarelli in England' (Italian Studies, 1959, pp.1-20)", "archive",
     "Short citation in p.292 note 5, locally matched to the book bibliography entry. The cited article was not independently consulted; the OCR footnote marker is corrected from 8 to printed 5 in S2.", 556),
    ("dessin_catalogue", "Le Dessin Français dans les Collections du XVIIIe siècle (exhibition catalogue, Paris, 1935), p.43", "archive",
     "P.292 note 6 citation for Count Tessin's career and collecting activities; the book bibliography describes it as a Gazette des Beaux-Arts exhibition catalogue. The cited page was not consulted.", 557),
    ("bjurstrom_article", "Per Bjurström, 'Carl Gustaf Tessin as a collector of drawings' (1967; citation locator)", "archive",
     "P.292 note 6 short citation, locally matched to the book bibliography entry in Contributions to the History and Theory of Art. The article was not independently consulted.", 557),
]
new_candidates = []
C = {}
for index, (key, name, kind, detail, line_no) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{index:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES_SEG}#L{line_no}",
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
    mention_id = f"m-chp10-p292-notes-{local_id}"
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


add_mention("n1-de-brosses", 554, "De Brosses", C["de_brosses_person"], "Surname as printed; the bibliography identifies Charles de Brosses.")
add_mention("n1-locator", 554, "I, p. 282", C["de_brosses_locator"], "Volume/page locator; cited content was not independently consulted.")
add_mention("n2-burney", 554, "Burney", E["dr_burney"], "Existing p.292 person candidate reused.")
add_mention("n2-locator", 554, "I, p. 109", C["burney_locator"], "Volume/page locator; cited content was not independently consulted.")
add_mention("n3-beckford", 555, "[William Beckford]", E["william_beckford"], "Existing p.292 person candidate reused.")
add_mention("n3-locator", 555, "I, p. 101", C["beckford_locator"], "Volume/page locator; cited content was not independently consulted.")
add_mention("n4-finberg", 555, "Finberg", C["finberg_person"], "Surname-only citation; full bibliographic author form is not treated as S3 identity resolution.")
add_mention("n4-year", 555, "1920-1", C["finberg_article"], "Year locator locally matched to the Canaletto in England bibliography entry.")
add_mention("n5-levey", 556, "Levey", C["levey_person"], "Surname-only citation; possible matches remain for S3.")
add_mention("n5-article-locator", 556, "Italian Studies, 1959, pp. 1-20", C["levey_article"], "Article/journal locator matched locally to the bibliography; the footnote marker is OCRed as 8 but prints as 5.")
add_mention("n6-tessin", 557, "Tessin’s", E["tessin"], "Career and collecting activities are the subjects of the cited works.")
add_mention("n6-dessin-title", 557, "Le Dessin Français dans les Collections du XVIIIe siècle", C["dessin_catalogue"], "Exhibition catalogue named in the note.")
add_mention("n6-dessin-locator", 557, "193 5, p. 43", C["dessin_catalogue"], "S0 OCR spacing; the scan reads 1935, p. 43.")
add_mention("n6-bjurstrom", 557, "Bjurstrôm", E["bjurstrom"], "S0 OCR form; the print reads Bjurström. Existing author candidate reused; the specific 1967 work is recorded separately.")
add_mention("n6-bjurstrom-year", 557, "1967", C["bjurstrom_article"], "Short citation locally matched to the bibliography entry; article not independently consulted.")

new_statements = []
new_sids = set()


def add_statement(local_id, line_no, obj, predicate, claim, qualification,
                  mentioned, marker, citations, corrections=None):
    statement_id = f"st-chp10-p292-note{marker}-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement: {statement_id}")
    quote = source_lines[line_no - 1]
    if quote not in segment_text:
        raise SystemExit(f"source quote missing: {statement_id}")
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 292, "pdf_physical_page": 21,
        "claim": claim, "speaker": "Haskell, footnote",
        "text_layer": "bibliographic pointer",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": False, "footnote_marker": marker,
        "related_body_statement_ids": BODY_LINKS[marker],
        "citations": citations,
        "cited_material_not_independently_consulted": True,
    }
    if corrections:
        qualifiers["ocr_corrections"] = corrections
    statement = {
        "statement_id": statement_id, "segment_id": NOTES_SEG,
        "subject_candidate_id": None, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
    }
    new_statements.append(statement)
    new_sids.add(statement_id)
    return statement_id


S = {}
S["n1-brosses"] = add_statement(
    "brosses-citation", 554, C["de_brosses_locator"], "footnote_citation",
    "P.292 note 1 cites De Brosses, volume I, page 282, for the preceding account of Canaletto's market and prices.",
    "This is a source locator only. The cited page was not read; the book bibliography match is provisional until the bibliography's source-order S2 pass.",
    [C["de_brosses_person"], C["de_brosses_locator"]], 1,
    [{"source_candidate_id": C["de_brosses_locator"], "volume": "I", "page": "282"}],
)
S["n2-burney"] = add_statement(
    "burney-citation", 554, C["burney_locator"], "footnote_citation",
    "P.292 note 2 cites Burney, volume I, page 109, for the quoted account of Venice.",
    "The cited page was not independently consulted; the citation is a pointer, not confirmation of Burney's testimony.",
    [E["dr_burney"], C["burney_locator"]], 2,
    [{"source_candidate_id": C["burney_locator"], "volume": "I", "page": "109"}],
)
S["n3-beckford"] = add_statement(
    "beckford-citation", 555, C["beckford_locator"], "footnote_citation",
    "P.292 note 3 cites William Beckford, volume I, page 101, for the reported response to Canaletto.",
    "The cited page was not independently consulted; retain Haskell's report as the only current evidence.",
    [E["william_beckford"], C["beckford_locator"]], 3,
    [{"source_candidate_id": C["beckford_locator"], "volume": "I", "page": "101"}],
)
S["n4-finberg"] = add_statement(
    "finberg-citation", 555, C["finberg_article"], "footnote_citation",
    "P.292 note 4 cites Finberg, 1920-1, for the Canaletto-in-England account.",
    "The book bibliography locally identifies Hilda Finberg's Canaletto in England article; the article was not consulted and author identity remains for S3.",
    [C["finberg_person"], C["finberg_article"]], 4,
    [{"source_candidate_id": C["finberg_article"], "reference_as_printed": "Finberg, 1920-1"}],
)
S["n5-levey"] = add_statement(
    "levey-citation", 556, C["levey_article"], "footnote_citation",
    "P.292 note 5 cites Levey's article in Italian Studies, 1959, pages 1-20, for the Zuccarelli account.",
    "The book bibliography locally identifies 'Francesco Zuccarelli in England'; the article was not independently consulted. Print footnote number 5 is OCRed as 8 in S0; the correction is recorded only in S2.",
    [C["levey_person"], C["levey_article"]], 5,
    [{"source_candidate_id": C["levey_article"], "journal": "Italian Studies", "year": "1959", "pages": "1-20"}],
    corrections=[{"source_line": 556, "ocr": "8", "print": "5", "basis": "CHP-10.pdf physical page 21"}],
)
S["n6-tessin-references"] = add_statement(
    "tessin-references", 557, C["dessin_catalogue"], "footnote_citations_for_tessin_career_and_collecting",
    "Haskell directs readers to the 1935 exhibition catalogue Le Dessin Français dans les Collections du XVIIIe siècle, page 43, and to Bjurström, 1967, for a brief account of Tessin's career and collecting activities.",
    "These are source pointers only. Neither cited page nor article was consulted. Bibliographic matches are internal to the book and provisional until the bibliography's source-order S2 review; the OCR spacing '193 5' is corrected to printed 1935.",
    [E["tessin"], C["dessin_catalogue"], E["bjurstrom"], C["bjurstrom_article"]], 6,
    [
        {"source_candidate_id": C["dessin_catalogue"], "year": "1935", "page": "43"},
        {"source_candidate_id": C["bjurstrom_article"], "reference_as_printed": "Bjurström, 1967"},
    ],
    corrections=[
        {"source_line": 557, "ocr": "193 5", "print": "1935", "basis": "CHP-10.pdf physical page 21"},
        {"source_line": 557, "ocr": "Bjurstrôm", "print": "Bjurström", "basis": "CHP-10.pdf physical page 21"},
    ],
)

note_statement_ids = {marker: [] for marker in BODY_LINKS}
for statement in new_statements:
    note_statement_ids[statement["qualifiers"]["footnote_marker"]].append(statement["statement_id"])
note_lines = {1: 554, 2: 554, 3: 555, 4: 555, 5: 556, 6: 557}
for marker, body_ids in BODY_LINKS.items():
    for sid in body_ids:
        qualifiers = by_sid[sid]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_segment"] = NOTES_SEG
        qualifiers["footnote_source_line"] = note_lines[marker]
        qualifiers["footnote_note_statement_ids"] = note_statement_ids[marker]
        qualifiers["cited_material_not_independently_consulted"] = True

body_note = cov[BODY_SEG].get("note", "")
pending_clause = "Footnotes 1-6 remain pending in the consolidated notes segment."
if pending_clause not in body_note:
    raise SystemExit("p.292 body coverage note no longer has the expected pending clause")
cov[BODY_SEG]["note"] = body_note.replace(
    pending_clause,
    "Footnotes 1-6 at L554-L557 are migrated in the consolidated notes segment and linked to the body statements; their text is not duplicated into the body tables.",
)
notes = cov[NOTES_SEG]
if "L554 onward remains pending." not in notes.get("note", ""):
    raise SystemExit("consolidated-notes coverage note changed")
notes["source_line_ranges"] = "L492-557"
notes["note"] = notes["note"].replace("L554 onward remains pending.", "L558 onward remains pending.")
notes["note"] += (
    " P.292 notes 1-6 at L554-L557 are migrated and linked to all seven body statements carrying markers 1-6. Notes 1-5 are citation pointers for the preceding Canaletto, Burney, Beckford, Finberg, and Zuccarelli passages; "
    "note 6 points to a 1935 exhibition catalogue and Bjurström 1967 for Tessin. The cited works/pages were not independently consulted; local bibliography matches remain provisional pending the bibliography's own S2 pass. "
    "The print reads note marker 5 and year 1935 where S0 OCR reads 8 and '193 5'; corrections are recorded only in S2."
)

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
    for citation in statement["qualifiers"].get("citations", []):
        if citation["source_candidate_id"] not in all_candidate_ids:
            raise SystemExit(f"unknown citation candidate: {statement['statement_id']}")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the validated p.292 note migration")
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
    "ocr_corrections": [
        "L556 footnote marker 8 -> printed 5",
        "L557 year 193 5 -> printed 1935",
        "L557 Bjurstrôm -> printed Bjurström",
    ],
}, ensure_ascii=True, indent=2))
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
