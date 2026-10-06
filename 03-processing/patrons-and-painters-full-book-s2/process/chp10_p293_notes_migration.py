"""Controlled S2 migration for p.293 note 1 and notes 2-4; dry-run unless --apply."""
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
BODY_SEG = "chp-10:10_CHP-10_intro:l279-290"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "5683d41377f001dbb8292be3560ce5ec8bc074a867280f22abfcfeb07a8d9b28"
BACKUP_SUFFIX = ".bak-s2-chp10-p293-notes-20261002"


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
if hashlib.sha256("\n".join(source_lines[557:560]).encode("utf-8")).hexdigest() != EXPECTED_NOTES_SHA:
    raise SystemExit("p.293 note lines L558-L560 changed")
if not source_lines[557].startswith("2 Letter from Tessin"):
    raise SystemExit("p.293 note 2 anchor changed")
if not source_lines[558].startswith("3 Letter from Francesco Algarotti"):
    raise SystemExit("p.293 note 3 anchor changed")
if not source_lines[559].startswith("4 Pellegrini went to Vienna"):
    raise SystemExit("p.293 note 4 anchor changed")
if not source_lines[560].startswith("1 Pellegrini’s drawing is reproduced"):
    raise SystemExit("p.294 note 1 begins at an unexpected line")

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
if maximum != 9445:
    raise SystemExit(f"candidate sequence changed: {maximum}")
note_cov = cov.get(NOTES_SEG)
if not note_cov or (note_cov["disposition"], note_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes coverage changed")
if note_cov["source_line_ranges"] != "L492-557":
    raise SystemExit(f"consolidated notes range changed: {note_cov['source_line_ranges']}")
if cov.get(BODY_SEG, {}).get("migration_status") != "complete":
    raise SystemExit("p.293 body is not complete")

BODY_LINKS = {
    1: ["st-chp10-p293-tessin-tiepolo-letter-evaluation", "st-chp10-p293-tessin-tiepolo-quoted-praise"],
    2: ["st-chp10-p293-tessin-gai-letter"],
    3: ["st-chp10-p293-berlin-opinion"],
    4: ["st-chp10-p293-hapsburg-schoenborn-reception"],
}
FOOTNOTE_LINES = {1: 290, 2: 558, 3: 559, 4: 560}
by_sid = {row["statement_id"]: row for row in statements}
if not set(sum(BODY_LINKS.values(), [])) <= by_sid.keys():
    raise SystemExit("p.293 body footnote targets changed")
for marker, ids in BODY_LINKS.items():
    for sid in ids:
        qualifiers = by_sid[sid].get("qualifiers", {})
        if qualifiers.get("footnote_marker") != marker or not qualifiers.get("footnote_text_pending"):
            raise SystemExit(f"p.293 body footnote state changed: {sid}")

E = {
    "tessin": "cand-2552", "zanetti": "cand-2838", "algarotti": "cand-0041", "bonomo": "cand-0040",
    "pellegrini": "cand-1868", "vienna": "cand-2772", "carriera": "cand-0581", "ricci": "cand-2154",
    "ricci_bacchus_ariadne": "cand-2158", "pommersfelden": "cand-1971", "england": "cand-8983",
    "la_pittura": "cand-7949", "johann_philip_franz": "cand-2398", "friedrich_karl_schoenborn": "cand-2397",
    "london": "cand-1422", "paris": "cand-4653", "duesseldorf": "cand-0955", "von_freeden_work": "cand-7253",
    "siren_locator": "cand-9066", "treviso": "cand-9209",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("siren_author", "O. Sirén (author cited as Sirén in p.293 note 1)", "person",
     "The book bibliography has one local O. Sirén entry for Dessins et tableaux italiens de la Renaissance dans les collections de Suède (Stockholm, 1902). The note-to-entry match is provisional; the cited pages and identity were not independently verified.", 290),
    ("tessin_letter", "Letter from Count Carl Gustaf Tessin to A. M. Zanetti the Elder, 12 March 1737 (Biblioteca Marciana, Cl. XI, Cod. CXVI, 7356)", "archive",
     "Specific letter locator printed in p.293 note 2. The manuscript was not consulted; the spelling of the repository and shelfmark is retained as printed after scan check.", 558),
    ("biblioteca_marciana", "Biblioteca Marciana (repository named in p.293 note 2)", "institution",
     "Repository named for the Tessin-Zanetti letter; this records Haskell's locator only and does not establish a current catalogue record.", 558),
    ("algarotti_letter", "Letter from Francesco Algarotti to his brother Bonomo, 5 September 1749 (Biblioteca Comunale, Treviso, MSS. 1256)", "archive",
     "Specific letter locator printed in p.293 note 3. The manuscript was not consulted; the institution name is preserved as printed.", 559),
    ("biblioteca_comunale_treviso", "Biblioteca Comunale, Treviso (repository named in p.293 note 3)", "institution",
     "Repository named for the Algarotti-Bonomo letter; the cited manuscript and current institutional catalogue were not consulted.", 559),
    ("franz_schoenborn_letter", "Letter from Johann Philip Franz to Friedrich Karl Schönborn, 12 July 1723 (cited in Von Freeden, 1955, p.848)", "archive",
     "Specific letter described by Haskell in p.293 note 4. The letter was not independently consulted; Von Freeden is a local bibliography match only.", 560),
    ("von_freeden_person", "Max H. von Freeden (author cited in p.293 note 4)", "person",
     "The bibliography identifies Max H. von Freeden as author of the 1955 source; personal identity alignment is deferred to S3.", 560),
]
new_candidates = []
C = {}
for index, (key, name, kind, detail, line_no) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{index:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES_SEG}#L{line_no}" if line_no != 290 else f"{BODY_SEG}#L{line_no}",
    })

def offsets_for(segment_id):
    if segment_id == NOTES_SEG:
        first, last = 491, 634
    elif segment_id == BODY_SEG:
        first, last = 279, 290
    else:
        raise SystemExit(f"unexpected source segment: {segment_id}")
    text = "\n".join(source_lines[first - 1:last])
    offsets, offset = {}, 0
    for line_no in range(first, last + 1):
        offsets[line_no] = offset
        offset += len(source_lines[line_no - 1]) + 1
    return text, offsets

segment_texts = {segment: offsets_for(segment) for segment in (NOTES_SEG, BODY_SEG)}
new_mentions = []
new_mids = set()


def add_mention(local_id, segment_id, line_no, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p293-{local_id}"
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
    text, offsets = segment_texts[segment_id]
    start = offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})
    new_mids.add(mention_id)


# The p.293 note 1 text is already in the body OCR segment at L290; split the
# existing locator mention into its cited author and page locator without double-counting the excerpt.
siren_mention = next((r for r in mentions if r["mention_id"] == "m-chp10-p293-siren-note"), None)
if not siren_mention or siren_mention["candidate_id"] != E["siren_locator"] or siren_mention["surface_form"] != "Siren, pp. 103 ff.":
    raise SystemExit("p.293 Siren mention changed")
body_text, body_offsets = segment_texts[BODY_SEG]
body_line = source_lines[289]
siren_start = body_offsets[290] + body_line.index("Siren")
siren_end = siren_start + len("Siren")
siren_mention.update({"candidate_id": C["siren_author"], "surface_form": "Siren",
                      "start_char": str(siren_start), "end_char": str(siren_end),
                      "note": "Author surname in S0 OCR; the physical p.293 scan reads Sirén. The full footer excerpt is not duplicated in the merged-note mentions."})
add_mention("siren-page-locator", BODY_SEG, 290, "pp. 103 ff.", E["siren_locator"],
            "Citation locator in p.293 note 1; print reads pp. 103 ff.; the cited pages were not consulted.")

add_mention("n2-letter-object", NOTES_SEG, 558, "Letter from", C["tessin_letter"], "The specific letter cited in note 2.")
add_mention("n2-tessin", NOTES_SEG, 558, "Tessin", E["tessin"], "Existing index candidate reused.")
add_mention("n2-zanetti", NOTES_SEG, 558, "A. M. Zanetti the Elder", E["zanetti"], "Existing index candidate reused.")
add_mention("n2-repository", NOTES_SEG, 558, "Bibiioteca Marciana", C["biblioteca_marciana"], "S0 OCR spelling; the scan reads Biblioteca Marciana.")
add_mention("n2-shelfmark", NOTES_SEG, 558, "Cl.XI, Cod. CXVI, 7356", C["tessin_letter"], "Call number as printed; manuscript not consulted.")

add_mention("n3-letter-object", NOTES_SEG, 559, "Letter from", C["algarotti_letter"], "The specific letter cited in note 3.")
add_mention("n3-algarotti", NOTES_SEG, 559, "Francesco Algarotti", E["algarotti"], "Existing index candidate reused.")
add_mention("n3-bonomo", NOTES_SEG, 559, "Bonomo", E["bonomo"], "Existing index candidate reused.")
add_mention("n3-repository", NOTES_SEG, 559, "Bibiioteca Comunale", C["biblioteca_comunale_treviso"], "S0 OCR spelling; the scan reads Biblioteca Comunale.")
add_mention("n3-treviso", NOTES_SEG, 559, "Treviso", E["treviso"], "Existing place candidate reused.")
add_mention("n3-shelfmark", NOTES_SEG, 559, "MSS. 1256", C["algarotti_letter"], "Manuscript locator as printed; manuscript not consulted.")

add_mention("n4-pellegrini-trip", NOTES_SEG, 560, "Pellegrini", E["pellegrini"], "Existing index candidate reused.")
add_mention("n4-vienna", NOTES_SEG, 560, "Vienna", E["vienna"], "Existing place candidate reused.")
add_mention("n4-carriera", NOTES_SEG, 560, "Rosalba Camera", E["carriera"], "S0 OCR form; the p.293 scan reads Rosalba Carriera.")
add_mention("n4-ricci", NOTES_SEG, 560, "Ricci’s", E["ricci"], "Existing index candidate reused.")
add_mention("n4-bacchus-ariadne", NOTES_SEG, 560, "Bacchus and Ariadne", E["ricci_bacchus_ariadne"], "Existing index sub-entry candidate reused; exact work identity is not resolved here.")
add_mention("n4-pommersfelden", NOTES_SEG, 560, "Pommersfelden", E["pommersfelden"], "Existing place candidate reused.")
add_mention("n4-england", NOTES_SEG, 560, "England", E["england"], "Existing place candidate reused.")
add_mention("n4-catalogue", NOTES_SEG, 560, "La Pittura del Seicento a Venezia", E["la_pittura"], "Existing catalogue candidate reused; bibliography match and p.151 locator are not independent verification.")
add_mention("n4-letter-object", NOTES_SEG, 560, "A letter", C["franz_schoenborn_letter"], "Specific 12 July 1723 letter reported by Haskell.")
add_mention("n4-johann-philip", NOTES_SEG, 560, "Johann Philip Franz", E["johann_philip_franz"], "Existing index candidate reused.")
add_mention("n4-friedrich-karl", NOTES_SEG, 560, "Friedrich Karl Schönborn", E["friedrich_karl_schoenborn"], "Existing index candidate reused.")
add_mention("n4-pellegrini-letter", NOTES_SEG, 560, "Pellegrini", E["pellegrini"], "Second occurrence, in the letter's reported subject; existing index candidate reused.", occurrence=1)
add_mention("n4-london", NOTES_SEG, 560, "London", E["london"], "Existing index context candidate reused.")
add_mention("n4-paris", NOTES_SEG, 560, "Paris", E["paris"], "Existing place candidate reused.")
add_mention("n4-duesseldorf", NOTES_SEG, 560, "Diisseldorf", E["duesseldorf"], "S0 OCR form; the scan reads Düsseldorf.")
add_mention("n4-von-freeden", NOTES_SEG, 560, "Von Freeden", C["von_freeden_person"], "Surname-only in the note; the bibliography gives Max H. von Freeden.")
add_mention("n4-von-freeden-locator", NOTES_SEG, 560, "1955, p. 848", E["von_freeden_work"], "Existing book candidate reused; p.848 was not consulted.")

existing_candidate = next(r for r in candidates if r["candidate_id"] == E["siren_locator"])
existing_candidate["detail"] = "The p.293 note 1 locator is printed as Sirén, pp. 103 ff. The book bibliography lists one local O. Sirén entry (1902), but the exact work match remains provisional; cited pages were not consulted."

new_statements = []
new_sids = set()


def add_statement(local_id, segment_id, line_no, marker, obj, predicate, claim, qualification,
                  mentioned, citations, text_layer="bibliographic pointer", relation_candidate=False, corrections=None):
    statement_id = f"st-chp10-p293-note{marker}-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement: {statement_id}")
    quote = source_lines[line_no - 1]
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 293, "pdf_physical_page": 22,
        "claim": claim, "speaker": "Haskell, footnote",
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation_candidate,
        "footnote_marker": marker,
        "related_body_statement_ids": BODY_LINKS[marker],
        "citations": citations,
        "cited_material_not_independently_consulted": True,
    }
    if corrections:
        qualifiers["ocr_corrections"] = corrections
    statement = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": None, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
    }
    new_statements.append(statement)
    new_sids.add(statement_id)
    return statement_id


S = {}
S["note1"] = add_statement(
    "siren-citation", BODY_SEG, 290, 1, E["siren_locator"], "footnote_citation",
    "P.293 note 1 cites Sirén, pages 103 ff., for Haskell's discussion of Tessin's assessment of Tiepolo.",
    "This is a citation pointer only. The bibliography's O. Sirén entry is a provisional local match; the cited pages were not consulted. The OCR excerpt occurs in the body segment at L290 and is not duplicated in the merged notes segment.",
    [C["siren_author"], E["siren_locator"]],
    [{"source_candidate_id": E["siren_locator"], "pages": "103 ff.", "bibliography_match": "provisional"}],
    corrections=[{"source_line": 290, "ocr": "Siren", "print": "Sirén", "basis": "CHP-10.pdf physical page 22"}],
)
S["note2"] = add_statement(
    "tessin-letter", NOTES_SEG, 558, 2, C["tessin_letter"], "cites_dated_tessin_to_zanetti_letter",
    "P.293 note 2 identifies a letter from Count Tessin to A. M. Zanetti the Elder, dated 12 March 1737, at Biblioteca Marciana, Cl. XI, Cod. CXVI, 7356.",
    "The manuscript was not consulted. Repository and shelfmark are recorded as Haskell's printed locator, not independently verified catalogue data.",
    [E["tessin"], E["zanetti"], C["tessin_letter"], C["biblioteca_marciana"]],
    [{"source_candidate_id": C["tessin_letter"], "date": "1737-03-12", "call_number": "Cl. XI, Cod. CXVI, 7356"}],
    text_layer="archival locator",
    corrections=[{"source_line": 558, "ocr": "Bibiioteca", "print": "Biblioteca", "basis": "CHP-10.pdf physical page 22"}],
)
S["note3"] = add_statement(
    "algarotti-letter", NOTES_SEG, 559, 3, C["algarotti_letter"], "cites_dated_algarotti_to_bonomo_letter",
    "P.293 note 3 identifies a letter from Francesco Algarotti to his brother Bonomo, dated 5 September 1749, at Biblioteca Comunale, Treviso, MSS. 1256.",
    "The manuscript and current repository catalogue were not consulted; this preserves Haskell's printed locator only.",
    [E["algarotti"], E["bonomo"], C["algarotti_letter"], C["biblioteca_comunale_treviso"], E["treviso"]],
    [{"source_candidate_id": C["algarotti_letter"], "date": "1749-09-05", "call_number": "MSS. 1256"}],
    text_layer="archival locator",
    corrections=[{"source_line": 559, "ocr": "Bibiioteca", "print": "Biblioteca", "basis": "CHP-10.pdf physical page 22"}],
)
S["note4-travel"] = add_statement(
    "travel-dates", NOTES_SEG, 560, 4, E["vienna"], "pellegrini_and_carriera_travel_to_vienna",
    "Haskell's note says Pellegrini went to Vienna in 1725–1727 and Rosalba Carriera in 1730.",
    "The note's abbreviated second clause is read as Carriera also going to Vienna; this is the source's syntax, not an independently checked itinerary.",
    [E["pellegrini"], E["vienna"], E["carriera"]], [],
    text_layer="authorial note report", relation_candidate=True,
    corrections=[{"source_line": 560, "ocr": "Camera", "print": "Carriera", "basis": "CHP-10.pdf physical page 22"}],
)
S["note4-ricci-work"] = add_statement(
    "ricci-work-date", NOTES_SEG, 560, 4, E["ricci_bacchus_ariadne"], "ricci_bacchus_ariadne_dates_after_england_visit",
    "Haskell's note says Sebastiano Ricci's Bacchus and Ariadne at Pommersfelden dates from after his visit to England, citing La Pittura del Seicento a Venezia, 1959, page 151.",
    "The artwork, the visit, and the relative dating are retained as separate source claims; the catalogue page was not consulted and no exact year is inferred.",
    [E["ricci"], E["ricci_bacchus_ariadne"], E["pommersfelden"], E["england"], E["la_pittura"]],
    [{"source_candidate_id": E["la_pittura"], "year": "1959", "page": "151", "bibliography_match": "local"}],
    text_layer="authorial note report",
    corrections=[{"source_line": 560, "ocr": "piZt A", "print": "p. 151", "basis": "CHP-10.pdf physical page 22"}],
)
S["note4-letter"] = add_statement(
    "franz-schoenborn-letter", NOTES_SEG, 560, 4, C["franz_schoenborn_letter"], "reports_1723_letter_introducing_pellegrini",
    "Haskell cites Johann Philip Franz's letter of 12 July 1723 to Friedrich Karl Schönborn introducing Pellegrini and reporting his success in London, Paris and Düsseldorf; the note cites Von Freeden, 1955, page 848.",
    "The letter was not consulted. The 1955 work matches a local bibliography entry; page 848 was not checked. The OCR form Diisseldorf is corrected only in S2.",
    [C["franz_schoenborn_letter"], E["johann_philip_franz"], E["friedrich_karl_schoenborn"], E["pellegrini"], E["london"], E["paris"], E["duesseldorf"], C["von_freeden_person"], E["von_freeden_work"]],
    [{"source_candidate_id": E["von_freeden_work"], "year": "1955", "page": "848", "bibliography_match": "local"}],
    text_layer="reported archival locator", relation_candidate=True,
    corrections=[{"source_line": 560, "ocr": "Diisseldorf", "print": "Düsseldorf", "basis": "CHP-10.pdf physical page 22"}],
)

for marker, body_ids in BODY_LINKS.items():
    linked_note_ids = [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_marker"] == marker]
    for sid in body_ids:
        qualifiers = by_sid[sid]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_segment"] = BODY_SEG if marker == 1 else NOTES_SEG
        qualifiers["footnote_source_line"] = FOOTNOTE_LINES[marker]
        qualifiers["footnote_note_statement_ids"] = linked_note_ids

# Check that anchors introduced or revised by this migration are exact and non-overlapping.
all_mentions = [siren_mention] + new_mentions
for segment_id in (NOTES_SEG, BODY_SEG):
    rows = [row for row in all_mentions if row["segment_id"] == segment_id]
    rows.sort(key=lambda row: (int(row["start_char"]), int(row["end_char"])))
    for left, right in zip(rows, rows[1:]):
        if int(right["start_char"]) < int(left["end_char"]):
            raise SystemExit(f"overlapping mention anchors: {left['mention_id']} / {right['mention_id']}")
for row in new_mentions:
    if row["candidate_id"] not in cids | {item["candidate_id"] for item in new_candidates}:
        raise SystemExit(f"unresolved mention candidate: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    if row["object_candidate_id"] and row["object_candidate_id"] not in cids | {item["candidate_id"] for item in new_candidates}:
        raise SystemExit(f"unknown statement object: {row['statement_id']}")
    for cid in q["mentioned_candidate_ids"]:
        if cid not in cids | {item["candidate_id"] for item in new_candidates}:
            raise SystemExit(f"unknown statement mention candidate: {row['statement_id']} {cid}")
    for citation in q.get("citations", []):
        if citation["source_candidate_id"] not in cids | {item["candidate_id"] for item in new_candidates}:
            raise SystemExit(f"unknown citation candidate: {row['statement_id']}")

body_cov = cov[BODY_SEG]
if "The final p.293 note locator was separately captured." not in body_cov.get("note", ""):
    raise SystemExit("p.293 body coverage note changed")
body_cov["note"] = body_cov["note"].replace(
    "The final p.293 note locator was separately captured. Consolidated notes remain pending.",
    "P.293 note 1's Sirén locator at L290 is now represented once and linked to its two body statements; notes 2-4 at L558-L560 are migrated from the consolidated notes segment.",
)
if "Consolidated notes remain pending." in body_cov["note"]:
    raise SystemExit("p.293 body coverage note was not fully synchronized")
note_cov["source_line_ranges"] = "L492-560"
if "L558 onward remains pending." not in note_cov.get("note", ""):
    raise SystemExit("consolidated-notes cursor changed")
note_cov["note"] = note_cov["note"].replace("L558 onward remains pending.", "L561 onward remains pending.")
note_cov["note"] += (
    " P.293 notes 2-4 at L558-L560 are migrated and linked to body markers 2-4. Note 1's Sirén citation is already present at body-segment L290 and is represented there once, avoiding duplication. "
    "The cited 1737 and 1749 letters, 1959 catalogue pages, and Von Freeden page were not independently consulted; bibliography matches are local pointers pending the bibliography S2 pass. "
    "The next line L561 begins p.294 note 1 and remains pending."
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the validated p.293 footnote migration")
args = parser.parse_args()
print(json.dumps({
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "source_segments": [BODY_SEG, NOTES_SEG],
    "new_candidates": [row["candidate_id"] for row in new_candidates],
    "new_candidate_count": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "body_markers_linked": {str(marker): len(ids) for marker, ids in BODY_LINKS.items()},
    "coverage": {"notes_ranges": note_cov["source_line_ranges"], "next": "L561", "notes_status": note_cov["migration_status"]},
    "cross_segment_duplicates": ["Sirén note 1 is captured at body-segment L290 and linked; it is not duplicated in the merged-note mentions."],
}, ensure_ascii=True, indent=2))
if not args.apply:
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(cp, cf, candidates + new_candidates)
write_csv(mp, mf, mentions + new_mentions)
write_jsonl(sp, statements + new_statements)
write_csv(vp, vf, coverage)
print("Applied validated p.293 footnote migration; four table backups created.")
