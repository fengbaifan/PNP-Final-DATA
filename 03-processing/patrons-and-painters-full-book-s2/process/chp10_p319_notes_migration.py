"""Controlled S2 migration for the printed p.319 notes; dry-run by default."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
BODY = "chp-10:10_CHP-10_sec_ii:l144-149"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BACKUP_SUFFIX = ".bak-s2-chp10-p319-notes-20261003"


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


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write reviewed p.319 note rows and links")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected = {
    304: "1 Apart from the above see Manuel, pp. 86 and 94.",
    305: "2 Conti, II, p. cxlviii:",
    306: "3 ibid., p. 250:",
    307: "4 ibid., p. 278:",
}
for line_no, prefix in expected.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f"canonical p.319 note boundary changed at L{line_no}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
candidate_ids = set(candidate_by_id)
statement_by_id = {row["statement_id"]: row for row in statements}
statement_ids = set(statement_by_id)
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates), len(mentions), len(statements))
if state != (9921, 9934, 21062, 9363):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (BODY, NOTES):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.319 body is not reviewed/partial")
if coverage[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated footnote segment is not partial")
if any(sid.startswith("st-chp10-p319-n0") for sid in statement_ids):
    raise SystemExit("p.319 note statements already exist")
if any(row["mention_id"].startswith("m-s2-ch10-p319-note-") for row in mentions):
    raise SystemExit("p.319 note mentions already exist")
body_markers = [
    ("st-chp10-p319-newton-showed-conti-confidential-notes", 1, 304),
    ("st-chp10-p319-contis-vague-ideas-about-newton-optics-had-no-impact", 2, 305),
    ("st-chp10-p319-conti-praised-canaletto-camera-ottica-views", 3, 306),
    ("st-chp10-p319-conti-painters-fantasy-quoted-principles", 4, 307),
]
for sid, marker, line in body_markers:
    row = statement_by_id.get(sid)
    if not row or row["qualifiers"].get("footnote_marker") != marker or row["qualifiers"].get("pending_note_source_line") != line:
        raise SystemExit(f"expected pending body footnote not found: {sid}")
for cid in ("cand-0498", "cand-0826", "cand-0829", "cand-0992", "cand-1390", "cand-1422", "cand-1739", "cand-2719", "cand-3418", "cand-8178", "cand-8959", "cand-9725", "cand-9729", "cand-9934"):
    if cid not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {cid}")
if candidate_by_id["cand-9934"]["canonical_name"] != "Conti, Prose e Poesie, volume II, 1756 (citation locator)":
    raise SystemExit("expected Conti volume-II citation candidate changed")

new_candidates = []


def add_candidate(cid, name, kind, detail, line):
    if cid in candidate_ids or any(row["candidate_id"] == cid for row in new_candidates):
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line}",
    })
    new_candidates.append(row)


add_candidate("cand-9935", "Manuel (author cited at p.319 note 1; identity unresolved)", "person", "Surname-only author reference for the preceding account of Conti and Newton; full name and work are not given here.", 304)
add_candidate("cand-9936", "Manuel, pages 86 and 94 (citation locator)", "archive", "Haskell refers readers to these pages; publication title and edition are not specified in this note and were not independently consulted.", 304)
add_candidate("cand-9937", "Leonardo da Vinci manuscript on harmony of colors in painting (title unspecified)", "archive", "Conti reports that Leonardo cites a manuscript of his own discussing color harmony in painting and locates it at a library in Milan. Do not equate it with Leonardo’s Trattato della pittura without evidence.", 305)
add_candidate("cand-9938", "Library in Milan named in Conti’s quotation (institution unresolved)", "institution", "The quotation says Biblioteca di Milano but gives no exact institutional name, shelfmark, or current repository identity.", 305)
add_candidate("cand-9939", "Harmony of colors in painting (as discussed in Conti’s quotation)", "term", "Aesthetic and optical concept in the quoted passage; Conti’s report links it to Newtonian optics and color application, without validating the theory.", 305)
add_candidate("cand-9940", "Newtonian theory of colors (as described in Conti’s quotation)", "term", "The source reports this theory as a context for mechanical determination of color composition; specific scientific works are not identified.", 305)
add_candidate("cand-9941", "Mechanical rule of centers of gravity for determining color composition", "term", "Conti’s quoted description of a method used by many to determine color composition; the underlying method is not independently verified.", 305)
add_candidate("cand-9942", "Unnamed German painter who produced printed pictures (Conti quotation)", "person", "Conti describes an unidentified German painter who prints pictures, showed examples in London, and was seen by Conti at The Hague. No identity or exact medium is supplied.", 305)
add_candidate("cand-9943", "Unidentified printed-painting examples by the German painter in Conti’s quotation", "work", "An unspecified group of printed pictures: Conti says various examples were shown in London and one was kept in Venice by Antonio Zanetti. Titles, subjects, dates, and technique are not given.", 305)
add_candidate("cand-9944", "Antonio Zanetti (named in Conti quotation; identity alignment unresolved)", "person", "The note gives ‘Signor Antonio Zanetti’. Keep this source-derived mention distinct until S3 compares it with indexed Zanetti candidates.", 305)
add_candidate("cand-9945", "Apelles (named in Conti quotation)", "person", "Classical painter invoked in Conti’s conditional speculation about representing color harmony and impossible phenomena; no identity or historical claim is added here.", 305)
add_candidate("cand-9946", "Newtonian principles of light immutability, refrangibility, and reflexibility", "term", "The quotation attributes these principles to Newton and reports their use by an unnamed painter to set color vividness and attenuation; no scientific source is independently consulted.", 305)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []
note_block = "\n".join(source_lines[272:349])


def add_mention(cid, line_no, needle, note=""):
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention candidate missing: {cid}")
    line = source_lines[line_no - 1]
    line_offset = sum(len(source_lines[index - 1]) + 1 for index in range(273, line_no))
    earlier = [
        int(row["start_char"]) - line_offset
        for row in new_mentions
        if row["surface_form"] == needle and line_offset <= int(row["start_char"]) < line_offset + len(line)
    ]
    at = line.find(needle, max((start + len(needle) for start in earlier), default=0))
    if at < 0:
        raise SystemExit(f"mention needle missing at L{line_no}: {needle!r}")
    offset = line_offset + at
    if note_block[offset:offset + len(needle)] != needle:
        raise SystemExit(f"mention offset mismatch at L{line_no}: {needle!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p319-note-{len(new_mentions) + 1:04d}",
        "segment_id": NOTES,
        "candidate_id": cid,
        "surface_form": needle,
        "start_char": offset,
        "end_char": offset + len(needle),
        "note": note,
    })
    new_mentions.append(row)


for cid, line, needle, note in [
    ("cand-9935", 304, "Manuel", "Surname-only cited author."),
    ("cand-9936", 304, "pp. 86 and 94", "Page locator supplied by Haskell."),
    ("cand-0826", 305, "Conti", "Existing Antonio Conti candidate used in the adjacent body statements."),
    ("cand-1390", 305, "Leonardo da Vinci", "Existing broad Leonardo index candidate reused; S3 resolves repeated index entries."),
    ("cand-9937", 305, "un suo manoscritto", "Unidentified manuscript reported in Conti’s quotation."),
    ("cand-9939", 305, "armonia de’ colori", "First occurrence: harmony of colors in painting."),
    ("cand-9938", 305, "Biblioteca di Milano", "Repository wording as printed; exact institution unresolved."),
    ("cand-9940", 305, "teoria Newtoniana de’ colori", "Newtonian color theory as named in the quotation."),
    ("cand-9941", 305, "regola meccanica de centri di gravità", "Mechanical rule named in the OCR transcription; the printed apostrophe is not represented in S0."),
    ("cand-9942", 305, "Pittor Tedesco", "Unnamed German painter, not identified with a named printmaker."),
    ("cand-9943", 305, "stampa le pitture", "Printed-picture activity described in the source; process is not classified further."),
    ("cand-9943", 305, "varj saggj", "Various examples of the painter’s printed pictures."),
    ("cand-1422", 305, "Londra", "Existing London candidate reused; source uses the Italian name."),
    ("cand-9944", 305, "Signor Antonio Zanetti", "Name as printed; alignment with indexed Zanetti candidates deferred to S3."),
    ("cand-8959", 305, "Haja", "Italian rendering for The Hague in the quotation; the print form is retained."),
    ("cand-1739", 305, "Newtono", "Printed inflected form referring to Newton in the quoted Italian."),
    ("cand-9946", 305, "immutabilità", "First named optical principle in the quotation."),
    ("cand-9946", 305, "varia ri frangibilità e reflessibilità", "OCR splits ‘rifrangibilità’; print reading is recorded in S2, S0 unchanged."),
    ("cand-9939", 305, "armonizarli", "The painter’s reported purpose is to harmonize colors."),
    ("cand-9939", 305, "armonia de’ colori", "Second occurrence: conditional application to the human body in shadow."),
    ("cand-9945", 305, "Apelle", "Italian form of Apelles as printed in Conti’s quotation."),
    ("cand-9729", 306, "camera ottica", "Existing apparatus candidate reused; no particular device is identified."),
    ("cand-2719", 306, "Venezia", "Existing Venice candidate reused from this chapter’s body passage."),
    ("cand-0498", 306, "Canaletto", "Existing Canaletto candidate used in the adjacent body statement."),
    ("cand-9934", 307, "ibid.", "Cross-reference resolves to Conti, volume II, from p.319 note 2."),
    ("cand-0992", 307, "fantasia pittoresca", "Painterly fantasy in the source quotation; linked to the existing fantasy-in-art concept candidate."),
]:
    add_mention(cid, line, needle, note)

# The existing volume-II citation is reused; these page locators belong to the same source volume.
conti_volume = candidate_by_id["cand-9934"]
if "pp. cxlviii, 250, 278" not in conti_volume["detail"]:
    conti_volume["detail"] += " P.319 notes 2–4 cite the same volume at pp. cxlviii, 250, and 278; these pages are recorded from Haskell’s notes and were not independently consulted."

new_statements = []


def add_statement(sid, subject, object_id, predicate, line, claim, qualification, mentioned,
                  speaker, layer, body_ids, marker, relation_candidate=False, extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement ID already exists: {sid}")
    quote = source_lines[line - 1]
    if not quote.startswith(f"{line - 303} "):
        raise SystemExit(f"note quote boundary changed: {sid}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing statement subject: {sid}")
    if object_id and object_id not in all_candidate_ids:
        raise SystemExit(f"missing statement object: {sid}")
    mentioned = list(dict.fromkeys(mentioned))
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing statement mention candidate: {sid}")
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": 319,
        "pdf_physical_page": 52,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
        "footnote_number": line - 303,
        "linked_body_statement_ids": body_ids,
    }
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": sid,
        "segment_id": NOTES,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


add_statement("st-chp10-p319-n01-manuel-citation", "cand-9725", "cand-9936", "cites_manuel_for_conti_newton_exchange",
              304, "Haskell directs readers to Manuel, pages 86 and 94, in connection with the preceding account of Conti and Newton’s confidential notes.",
              "The phrase ‘Apart from the above’ is kept broad; Manuel’s identity, work, and cited pages were not independently checked.",
              ["cand-9725", "cand-0826", "cand-1739", "cand-9935", "cand-9936"], "Haskell footnote", "bibliographic citation",
              ["st-chp10-p319-newton-showed-conti-confidential-notes"], 1,
              extra={"citations": [{"source_candidate_id": "cand-9936", "author_candidate_id": "cand-9935", "pages": ["86", "94"]}]})
add_statement("st-chp10-p319-n02-leonardo-manuscript-color-harmony", "cand-1390", "cand-9937", "reported_manuscript_on_color_harmony_in_milan_library",
              305, "In Conti’s quotation, Leonardo da Vinci is said to cite a manuscript of his own on color harmony in painting, reportedly held at a library in Milan.",
              "This is Conti’s statement as quoted by Haskell; the manuscript and library were not consulted. The manuscript is not identified with the Trattato della pittura.",
              ["cand-1390", "cand-9937", "cand-9938", "cand-3418", "cand-9939", "cand-0826", "cand-9934"],
              "Antonio Conti (quoted by Haskell)", "quotation in authorial note", ["st-chp10-p319-contis-vague-ideas-about-newton-optics-had-no-impact"], 2,
              extra={"citation_source_candidate_id": "cand-9934", "cited_volume": "II", "cited_page": "cxlviii", "repository_identity": "unresolved"})
add_statement("st-chp10-p319-n02-newtonian-color-theory-centers-of-gravity", "cand-9940", "cand-9941", "used_to_determine_color_composition_mechanically",
              305, "Conti’s quotation says Newtonian color theory had prompted many to determine color composition by a mechanical rule of centers of gravity.",
              "The quotation reports a contemporary understanding; no named practitioners, scientific text, or validated method is identified.",
              ["cand-9940", "cand-9941", "cand-9939", "cand-0826", "cand-9934"],
              "Antonio Conti (quoted by Haskell)", "quotation in authorial note", ["st-chp10-p319-contis-vague-ideas-about-newton-optics-had-no-impact"], 2,
              extra={"citation_source_candidate_id": "cand-9934", "cited_volume": "II", "cited_page": "cxlviii"})
add_statement("st-chp10-p319-n02-german-painter-and-printed-examples", "cand-9942", "cand-9943", "reported_printed_paintings_and_examples_in_london_and_venice",
              305, "Conti’s quotation describes an unnamed German painter who prints pictures, derived a color-related ‘secret’ from the preceding theory, showed various examples in London, and had one example kept in Venice by Antonio Zanetti.",
              "The demonstrative ‘questa’ is read contextually as referring to the Newtonian color theory. The painter, pictures, printing process, and Zanetti identity are not independently identified.",
              ["cand-9942", "cand-9943", "cand-9940", "cand-1422", "cand-2719", "cand-9944", "cand-0826", "cand-9934"],
              "Antonio Conti (quoted by Haskell)", "quotation in authorial note", ["st-chp10-p319-contis-vague-ideas-about-newton-optics-had-no-impact"], 2,
              extra={"citation_source_candidate_id": "cand-9934", "cited_volume": "II", "cited_page": "cxlviii", "deictic_resolution": "questa -> preceding Newtonian color theory; contextual reading"})
add_statement("st-chp10-p319-n02-painter-reported-newtonian-harmonizing-method", "cand-0826", "cand-9942", "reports_encounter_and_painters_claimed_color_method",
              305, "Conti says he saw the unnamed painter at The Hague and was told that the painter followed Newtonian principles of light and established degrees of color vividness and attenuation to harmonize colors.",
              "The method is reported speech (‘he assured me’) within Conti’s quotation, relayed by Haskell. The principles and painter’s practice are not independently verified.",
              ["cand-0826", "cand-9942", "cand-8959", "cand-1739", "cand-9946", "cand-9939", "cand-9934"],
              "Antonio Conti (quoted by Haskell)", "reported speech in authorial note", ["st-chp10-p319-contis-vague-ideas-about-newton-optics-had-no-impact"], 2,
              extra={"citation_source_candidate_id": "cand-9934", "cited_volume": "II", "cited_page": "cxlviii", "reported_speech": True})
add_statement("st-chp10-p319-n02-conditional-human-color-harmony-and-apelles", "cand-0826", "cand-9939", "conditionally_speculated_on_color_harmony_in_human_shadow",
              305, "Conti speculates that, if the reported method is true, color harmony in the human body in shadow might be determinable, perhaps as Apelles had fixed it.",
              "Both ‘if this is true’ and ‘perhaps’ are retained as explicit uncertainty; Apelles is invoked in Conti’s classical comparison, not independently evidenced.",
              ["cand-0826", "cand-9939", "cand-9945", "cand-9942", "cand-9934"],
              "Antonio Conti (quoted by Haskell)", "conditional speculation in authorial note", ["st-chp10-p319-contis-vague-ideas-about-newton-optics-had-no-impact"], 2,
              extra={"citation_source_candidate_id": "cand-9934", "cited_volume": "II", "cited_page": "cxlviii", "modality": "conditional and conjectural"})
add_statement("st-chp10-p319-n03-camera-ottica-and-canaletto-point-transfer", "cand-0826", "cand-0498", "camera_ottica_perspective_and_partial_point_transfer",
              306, "Conti’s quotation says camera ottica may be used to construct the perspective of a Venetian canal and its buildings, and that Canaletto can transfer more points than another painter but cannot transfer all of them.",
              "This records Conti’s stated possibility and comparison; it does not establish that a particular Canaletto painting or apparatus has been identified.",
              ["cand-0826", "cand-9729", "cand-0498", "cand-2719", "cand-8178", "cand-9934"],
              "Antonio Conti (quoted by Haskell)", "quotation in authorial note", ["st-chp10-p319-conti-praised-canaletto-camera-ottica-views"], 3,
              extra={"citation_source_candidate_id": "cand-9934", "cited_volume": "II", "cited_page": "250", "ocr_corrections": [{"source_line": 306, "ocr": "tutti fi trasferisca", "print_reading": "tutti li trasferisca"}]})
add_statement("st-chp10-p319-n03-transferred-points-create-vivid-optical-impression", "cand-0498", "cand-8178", "transferred_points_make_view_seem_like_object",
              306, "Conti says the points transferred by Canaletto would make such a vivid impression on the eye that, at first sight, the viewer would be persuaded of seeing the object itself.",
              "This is an aesthetic claim in Conti’s quotation, not a measured or independently tested optical result.",
              ["cand-0498", "cand-8178", "cand-9729", "cand-0826", "cand-9934"],
              "Antonio Conti (quoted by Haskell)", "quotation in authorial note", ["st-chp10-p319-conti-praised-canaletto-camera-ottica-views"], 3,
              extra={"citation_source_candidate_id": "cand-9934", "cited_volume": "II", "cited_page": "250"})
add_statement("st-chp10-p319-n04-conti-volume-ii-p278-source-for-fantasy-quote", "cand-0829", "cand-9934", "cites_conti_volume_ii_p278_for_painterly_fantasy_quote",
              307, "Haskell identifies Conti, volume II, page 278, as the source of the preceding Italian quotation on painterly fantasy.",
              "The Italian wording is reproduced in Haskell’s note and corresponds to the translated quotation begun in the body; Conti’s volume was not independently consulted.",
              ["cand-0829", "cand-0992", "cand-9934"], "Haskell footnote", "bibliographic citation",
              ["st-chp10-p319-conti-painters-fantasy-quoted-principles"], 4,
              extra={"citations": [{"source_candidate_id": "cand-9934", "author_candidate_id": "cand-0829", "volume": "II", "page": "278"}],
                     "translation_source_for_statement_id": "st-chp10-p319-conti-painters-fantasy-quoted-principles"})

all_statements = statements + new_statements
statement_by_id = {row["statement_id"]: row for row in all_statements}


def add_footnote_ref(body_statement_id, marker, line, note_ids):
    row = statement_by_id.get(body_statement_id)
    if not row:
        raise SystemExit(f"body statement missing: {body_statement_id}")
    q = row["qualifiers"]
    if q.get("footnote_marker") != marker or q.get("pending_note_source_line") != line:
        raise SystemExit(f"unexpected footnote marker/line: {body_statement_id}")
    q["footnote_text_pending"] = False
    q["footnote_segment"] = NOTES
    ref = {"marker": marker, "segment_id": NOTES, "source_line": line}
    refs = q.setdefault("footnote_refs", [])
    if ref not in refs:
        refs.append(ref)
    ids = q.setdefault("footnote_statement_ids", [])
    for sid in note_ids:
        if sid not in statement_by_id:
            raise SystemExit(f"note statement missing: {sid}")
        if sid not in ids:
            ids.append(sid)
    q["footnote_body_link_status"] = "linked"


add_footnote_ref("st-chp10-p319-newton-showed-conti-confidential-notes", 1, 304,
                 ["st-chp10-p319-n01-manuel-citation"])
add_footnote_ref("st-chp10-p319-contis-vague-ideas-about-newton-optics-had-no-impact", 2, 305,
                 ["st-chp10-p319-n02-leonardo-manuscript-color-harmony", "st-chp10-p319-n02-newtonian-color-theory-centers-of-gravity",
                  "st-chp10-p319-n02-german-painter-and-printed-examples", "st-chp10-p319-n02-painter-reported-newtonian-harmonizing-method",
                  "st-chp10-p319-n02-conditional-human-color-harmony-and-apelles"])
add_footnote_ref("st-chp10-p319-conti-praised-canaletto-camera-ottica-views", 3, 306,
                 ["st-chp10-p319-n03-camera-ottica-and-canaletto-point-transfer", "st-chp10-p319-n03-transferred-points-create-vivid-optical-impression"])
add_footnote_ref("st-chp10-p319-conti-painters-fantasy-quoted-principles", 4, 307,
                 ["st-chp10-p319-n04-conti-volume-ii-p278-source-for-fantasy-quote"])

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate ID")
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention ID")
if len({row["statement_id"] for row in all_statements}) != len(all_statements):
    raise SystemExit("duplicate statement ID")
candidate_id_set = {row["candidate_id"] for row in candidate_rows}
if any(row["candidate_id"] not in candidate_id_set for row in new_mentions):
    raise SystemExit("missing mention candidate foreign key")
for row in new_statements:
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing statement subject: {row['statement_id']}")
    if row["object_candidate_id"] and row["object_candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing statement object: {row['statement_id']}")
    if any(cid not in candidate_id_set for cid in row["qualifiers"]["mentioned_candidate_ids"]):
        raise SystemExit(f"missing statement mention foreign key: {row['statement_id']}")
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in new_mentions)
for left, right in zip(spans, spans[1:]):
    if left[1] > right[0]:
        raise SystemExit(f"overlapping p.319 note mention spans: {left[2]} and {right[2]}")

coverage[BODY].update({
    "migration_status": "complete",
    "source_line_ranges": "L145-149; notes L304-307",
    "note": (
        "Printed p.319 was checked against CHP-10.pdf physical p.52. Notes 1–4 at canonical L304–307 are reviewed and linked. "
        "Conti’s long Italian quotations are recorded as attributed reports, including the unnamed German painter’s account and the conditional ‘if true’ claim. "
        "The painter, Leonardo manuscript, Milan library, and Zanetti identity remain unresolved. The painterly-fantasy quotation continues into the next body segment and retains its existing continuation link."
    ),
})
coverage[NOTES].update({
    "source_line_ranges": "L274-307; L325-349",
    "note": "P.311–319 notes L274–307 are reviewed and linked; L325–349 was previously processed. The remaining gap is L308–324 (p.320–323 notes).",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
print(f"p.319 note preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.319 partial->complete; consolidated note coverage extends through L307")
print(f"totals: {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(all_statements)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
