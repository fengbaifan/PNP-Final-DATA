"""Controlled S2 migration for the printed p.316 notes; dry-run by default."""

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
BODY = "chp-10:10_CHP-10_sec_ii:l108-117"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BACKUP_SUFFIX = ".bak-s2-chp10-p316-notes-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.316 note rows and links")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_notes = {
    294: "1 Streit’s notes on his Canalettos have been published by Zimmermann, pp. 197-224.",
    295: "2 Zimmermann, pp. 199-203, attributes one of these—the Sala del Maxtor Consiglio—to Gianantonio and Francesco Guardi.",
    296: "3 These were the years when Amigoni was in Venice after his visit to England and before that to Spain.",
    297: "4 I am grateful to Mr Hugh Honour for letting me see his photographs of these paintings.",
}
for line_no, prefix in expected_notes.items():
    if not source_lines[line_no - 1].startswith(prefix):
        raise SystemExit(f"canonical p.316 note boundary changed at L{line_no}")

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
if state != (9897, 9910, 21022, 9348):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (BODY, NOTES):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.316 body is not reviewed/partial")
if coverage[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated footnote segment is not partial")
if any(sid.startswith("st-chp10-p316-n0") for sid in statement_ids):
    raise SystemExit("p.316 note statements already exist")
if any(row["mention_id"].startswith("m-s2-ch10-p316-note-") for row in mentions):
    raise SystemExit("p.316 note mentions already exist")

body_markers = [
    ("st-chp10-p316-two-life-scenes-noted-about-streits-pictures", 1, 294),
    ("st-chp10-p316-follower-paintings-record-doge-processions", 2, 295),
    ("st-chp10-p316-amigoni-painted-streit-portrait-and-ten-other-pictures", 3, 296),
    ("st-chp10-p316-nogari-found-genre-more-congenial", 4, 297),
]
for sid, marker, line in body_markers:
    row = statement_by_id.get(sid)
    if not row or row["qualifiers"].get("footnote_marker") != marker or row["qualifiers"].get("pending_note_source_line") != line:
        raise SystemExit(f"expected pending body footnote not found: {sid}")
for required_id in ("cand-0099", "cand-0822", "cand-1241", "cand-1249", "cand-1743", "cand-2519", "cand-3471", "cand-8983", "cand-9423", "cand-9606", "cand-9633", "cand-9634", "cand-9636", "cand-9637", "cand-9656", "cand-9904", "cand-5120"):
    if required_id not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {required_id}")

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


add_candidate("cand-9911", "Zimmermann (author cited at p.316 notes; identity unresolved)", "person", "Surname-only author cited for Streit’s notes and portrait publication. No full identity or exact work title is inferred.", 294)
add_candidate("cand-9912", "Zimmermann, pages 197–224 (citation locator)", "archive", "Haskell cites these pages for Streit’s notes about his Canalettos and cites pages 199–203 for the Sala del Maggior Consiglio attribution. The cited pages were not independently consulted.", 294)
add_candidate("cand-9913", "W. G. Constable (author cited at p.316 note 1; identity unresolved)", "person", "The note gives initials W. G.; keep distinct from John Constable and defer identity alignment to S3.", 294)
add_candidate("cand-9914", "W. G. Constable, 1956, pages 81–93 (citation locator)", "archive", "Cited for discussion of the Streit Canalettos and rejection of an attribution to Moretti or another follower. The cited pages were not independently consulted.", 294)
add_candidate("cand-9915", "Moretti (painter named in rejected attribution; identity unresolved)", "person", "Named only in a prior attribution that W. G. Constable reportedly rejects; no identity or specific individual painting is inferred.", 294)
add_candidate("cand-9916", "Sala del Maggior Consiglio (painting named in p.316 note)", "work", "The printed title is visually read as Sala del Maggior Consiglio; OCR reads Maxtor. Zimmermann is reported as attributing the work to Gian Antonio and Francesco Guardi. No date, present location, or independent attribution is supplied.", 295)
add_candidate("cand-9917", "Hugh Honour (named in p.316 note 4)", "person", "Named by Haskell as showing him photographs; no further identity or role is inferred.", 297)
add_candidate("cand-9918", "Photographs of paintings shown to Haskell by Hugh Honour", "archive", "Haskell says Honour let him see photographs of ‘these paintings’; the exact referents are unresolved and no individual photograph or work is identified.", 297)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []
note_block = "\n".join(source_lines[272:349])


def add_mention(cid, line_no, needle, note=""):
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention candidate missing: {cid}")
    line = source_lines[line_no - 1]
    line_offset = sum(len(source_lines[index - 1]) + 1 for index in range(273, line_no))
    earlier_occurrences = [
        int(row["start_char"]) - line_offset
        for row in new_mentions
        if row["segment_id"] == NOTES and row["surface_form"] == needle
        and line_offset <= int(row["start_char"]) < line_offset + len(line)
    ]
    at = line.find(needle, max((start + len(needle) for start in earlier_occurrences), default=0))
    if at < 0:
        raise SystemExit(f"mention needle missing at L{line_no}: {needle!r}")
    start = line_offset + at
    if note_block[start:start + len(needle)] != needle:
        raise SystemExit(f"mention offset mismatch at L{line_no}: {needle!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p316-note-{len(new_mentions) + 1:04d}",
        "segment_id": NOTES,
        "candidate_id": cid,
        "surface_form": needle,
        "start_char": start,
        "end_char": start + len(needle),
        "note": note,
    })
    new_mentions.append(row)


for cid, line, needle, note in [
    ("cand-9637", 294, "Streit’s notes", "The archive object identified in the note."),
    ("cand-9633", 294, "Canalettos", "First mention of the group of four Canaletto paintings owned by Streit."),
    ("cand-9911", 294, "Zimmermann", "Surname of the cited author."),
    ("cand-9912", 294, "pp. 197-224", "Pages cited for Streit’s notes about his Canalettos."),
    ("cand-9633", 294, "Canalettos", "Second mention of the Streit Canaletto group."),
    ("cand-9913", 294, "W. G. Constable", "Named author; do not merge with John Constable."),
    ("cand-9914", 294, "1956, pp. 81-93", "Publication locator cited by Haskell."),
    ("cand-9915", 294, "Moretti", "Artist named in an attribution reported as rejected."),
    ("cand-9656", 294, "some other follower", "Unnamed alternative follower; identity and membership unspecified."),
    ("cand-9911", 295, "Zimmermann", "Surname of the cited author."),
    ("cand-9912", 295, "pp. 199-203", "Specific pages within the cited Zimmermann locator."),
    ("cand-9916", 295, "Sala del Maxtor Consiglio", "OCR wording; print was visually read as Sala del Maggior Consiglio."),
    ("cand-1249", 295, "Gianantonio", "Printed artist name; identity candidate is Gian Antonio Guardi."),
    ("cand-1241", 295, "Francesco Guardi", "Printed artist name; identity candidate is Francesco Guardi."),
    ("cand-0099", 296, "Amigoni", "Existing Amigoni index candidate reused."),
    ("cand-9904", 296, "Venice", "Existing Venice candidate reused."),
    ("cand-8983", 296, "England", "Existing geographic candidate reused."),
    ("cand-5120", 296, "Spain", "Existing geographic candidate reused."),
    ("cand-9636", 296, "portrait of Streit", "Existing Amigoni portrait candidate; note gives its reported date."),
    ("cand-9911", 296, "Zimmermann", "Surname of the cited author who published the portrait."),
    ("cand-2519", 296, "the sitter", "The sitter is Sigismund Streit."),
    ("cand-9917", 297, "Mr Hugh Honour", "Person named in Haskell’s acknowledgement."),
    ("cand-9918", 297, "his photographs", "Photographs shown to Haskell; the referent set is not specified."),
    ("cand-9918", 297, "these paintings", "Anaphoric referent remains unresolved."),
]:
    add_mention(cid, line, needle, note)

new_statements = []


def add_statement(sid, subject, object_id, predicate, line, claim, qualification, mentioned,
                  speaker="Haskell footnote", layer="authorial note", relation_candidate=False, extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement ID already exists: {sid}")
    quote = source_lines[line - 1]
    if not quote.startswith(f"{line - 293} "):
        raise SystemExit(f"note quote boundary changed: {sid}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing subject candidate for {sid}: {subject}")
    if object_id and object_id not in all_candidate_ids:
        raise SystemExit(f"missing object candidate for {sid}: {object_id}")
    mentioned = list(dict.fromkeys(mentioned))
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing statement mention foreign key: {sid}")
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": 316,
        "pdf_physical_page": 49,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": relation_candidate,
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


add_statement("st-chp10-p316-n01-streit-notes-published-by-zimmermann", "cand-9637", "cand-9912", "notes_published_in_cited_source",
              294, "Haskell says Streit’s notes on his Canalettos were published by Zimmermann, pages 197–224.",
              "This records Haskell’s citation only; the cited pages were not independently consulted.",
              ["cand-9637", "cand-9633", "cand-9911", "cand-9912"], layer="bibliographic citation",
              extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p316-two-life-scenes-noted-about-streits-pictures"],
                     "citations": [{"source_candidate_id": "cand-9912", "author_candidate_id": "cand-9911", "pages": ["197", "224"]}]})
add_statement("st-chp10-p316-n01-constable-rejected-moretti-attribution", "cand-9633", "cand-9915", "attribution_reported_as_rejected",
              294, "Haskell says W. G. Constable discussed the Streit Canalettos in 1956 and rejected attribution to Moretti or another follower.",
              "The rejection is reported by Haskell from the cited pages, which were not independently consulted. Moretti and the alternative follower remain unidentified beyond the wording here.",
              ["cand-9633", "cand-9913", "cand-9914", "cand-9915", "cand-9656"], layer="bibliographic citation",
              relation_candidate=True,
              extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p316-two-life-scenes-noted-about-streits-pictures"],
                     "attribution_status": "reported as rejected by Constable", "cited_author_candidate_id": "cand-9913",
                     "citations": [{"source_candidate_id": "cand-9914", "author_candidate_id": "cand-9913", "year": "1956", "pages": ["81", "93"]}]})
add_statement("st-chp10-p316-n02-sala-attributed-to-gianantonio-guardi", "cand-9916", "cand-1249", "attributed_to",
              295, "Haskell reports Zimmermann’s attribution of the Sala del Maggior Consiglio to Gianantonio Guardi.",
              "The print title is Sala del Maggior Consiglio; OCR reads Maxtor. This is an attribution reported through Haskell’s note, not independent verification.",
              ["cand-9916", "cand-9911", "cand-9912", "cand-1249"], layer="attribution reported in authorial note",
              relation_candidate=True,
              extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p316-follower-paintings-record-doge-processions"],
                     "attribution_source": "Zimmermann, pages 199–203, as cited by Haskell", "ocr_corrections": [{"source_line": 295, "ocr": "Maxtor", "print_reading": "Maggior"}]})
add_statement("st-chp10-p316-n02-sala-attributed-to-francesco-guardi", "cand-9916", "cand-1241", "attributed_to",
              295, "Haskell reports Zimmermann’s attribution of the Sala del Maggior Consiglio to Francesco Guardi.",
              "The print title is Sala del Maggior Consiglio; OCR reads Maxtor. This is an attribution reported through Haskell’s note, not independent verification.",
              ["cand-9916", "cand-9911", "cand-9912", "cand-1241"], layer="attribution reported in authorial note",
              relation_candidate=True,
              extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p316-follower-paintings-record-doge-processions"],
                     "attribution_source": "Zimmermann, pages 199–203, as cited by Haskell", "ocr_corrections": [{"source_line": 295, "ocr": "Maxtor", "print_reading": "Maggior"}]})
add_statement("st-chp10-p316-n03-amigoni-in-venice-between-england-and-spain", "cand-0099", "cand-9904", "in_venice_during_1739_1746_interval",
              296, "Haskell says Amigoni was in Venice during the years 1739–1746, after his visit to England and before his visit to Spain.",
              "The note attaches this chronology to the period named in the preceding sentence; the travel chronology is not independently verified.",
              ["cand-0099", "cand-9904", "cand-8983", "cand-5120"],
              extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p316-amigoni-painted-streit-portrait-and-ten-other-pictures"],
                     "date_range": ["1739", "1746"], "sequence": ["after England visit", "before Spain visit"]})
add_statement("st-chp10-p316-n03-amigoni-portrait-painted-1739-sitter-age-52", "cand-0099", "cand-9636", "painted_in_1739_when_sitter_was_52",
              296, "Haskell says Amigoni’s portrait of Streit was published by Zimmermann and was painted in 1739, when Streit was 52.",
              "The publication and date are reported in Haskell’s note; Zimmermann’s cited publication and the portrait were not independently consulted.",
              ["cand-0099", "cand-9636", "cand-2519", "cand-9911", "cand-9912"],
              layer="portrait date and citation reported in authorial note", relation_candidate=True,
              extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p316-amigoni-painted-streit-portrait-and-ten-other-pictures"],
                     "date": "1739", "sitter_age": 52, "citations": [{"source_candidate_id": "cand-9912", "author_candidate_id": "cand-9911", "scope": "portrait published"}]})
add_statement("st-chp10-p316-n04-honour-showed-haskell-painting-photographs", "cand-9917", "cand-9918", "showed_photographs_to_haskell",
              297, "Haskell thanks Hugh Honour for letting him see photographs of paintings discussed in the surrounding passage.",
              "‘These paintings’ is an unresolved reference; no individual photographs or works are identified.",
              ["cand-9917", "cand-9918", "cand-9423"], layer="authorial acknowledgement",
              extra={"footnote_number": 4, "linked_body_statement_ids": ["st-chp10-p316-nogari-found-genre-more-congenial"],
                     "recipient_candidate_id": "cand-9423", "referent_status": "unresolved"})

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


add_footnote_ref("st-chp10-p316-two-life-scenes-noted-about-streits-pictures", 1, 294,
                 ["st-chp10-p316-n01-streit-notes-published-by-zimmermann", "st-chp10-p316-n01-constable-rejected-moretti-attribution"])
add_footnote_ref("st-chp10-p316-follower-paintings-record-doge-processions", 2, 295,
                 ["st-chp10-p316-n02-sala-attributed-to-gianantonio-guardi", "st-chp10-p316-n02-sala-attributed-to-francesco-guardi"])
add_footnote_ref("st-chp10-p316-amigoni-painted-streit-portrait-and-ten-other-pictures", 3, 296,
                 ["st-chp10-p316-n03-amigoni-in-venice-between-england-and-spain", "st-chp10-p316-n03-amigoni-portrait-painted-1739-sitter-age-52"])
add_footnote_ref("st-chp10-p316-nogari-found-genre-more-congenial", 4, 297,
                 ["st-chp10-p316-n04-honour-showed-haskell-painting-photographs"])

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
        raise SystemExit(f"overlapping p.316 note mention spans: {left[2]} and {right[2]}")

coverage[BODY].update({
    "migration_status": "complete",
    "source_line_ranges": "L109-117; notes L294-297",
    "note": (
        "Read printed p.316 against CHP-10.pdf physical p.49. Body L109–117 and notes 1–4 at canonical L294–297 "
        "are reviewed and linked. The two life-related Canaletto scenes and the further Vigilie scenes remain distinct; "
        "Zimmermann’s attribution of the Sala del Maggior Consiglio is recorded as reported, not verified. Amigoni’s "
        "Venice chronology and the 1739 portrait date remain Haskell’s claims. Hugh Honour’s photographs are recorded "
        "with the referent ‘these paintings’ unresolved."
    ),
})
coverage[NOTES].update({
    "source_line_ranges": "L274-297; L325-349",
    "note": "P.311–316 notes L274–297 are reviewed and linked; L325–349 was previously processed. The remaining gap is L298–324 (p.317–323 notes).",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
print(f"p.316 note preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.316 partial->complete; consolidated note coverage extends through L297")
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
print(f"applied; recovery copies created with suffix {BACKUP_SUFFIX}")
