"""Controlled S2 migration for p.315 notes; dry-run by default."""

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
BODY = "chp-10:10_CHP-10_sec_ii:l95-106"
BODY_NEXT = "chp-10:10_CHP-10_sec_ii:l108-117"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BACKUP_SUFFIX = ".bak-s2-chp10-p315-notes-20261003"


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
parser.add_argument("--apply", action="store_true", help="write p.315 note rows and links")
args = parser.parse_args()

source_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
if source_sha != SOURCE_SHA:
    raise SystemExit(f"canonical source markdown changed or script hash is stale: {source_sha}")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if not source_lines[291].startswith("1 On 28 July 1743 Schulenburg wrote to Rosalba Carriera"):
    raise SystemExit("canonical p.315 note 1 boundary changed")
if not source_lines[292].startswith("2 For a brief outline of Streit’s career"):
    raise SystemExit("canonical p.315 note 2 boundary changed")

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
if state != (9891, 9904, 21011, 9344):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (BODY, BODY_NEXT, NOTES):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.315 coverage is not reviewed/partial")
if coverage[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated footnote segment is not partial")
if any(sid.startswith("st-chp10-p315-n0") for sid in statement_ids):
    raise SystemExit("p.315 note statements already exist")
if any(row["mention_id"].startswith("m-s2-ch10-p315-note-") for row in mentions):
    raise SystemExit("p.315 note mentions already exist")
for sid, marker, line in [
    ("st-chp10-p315-schulenburg-good-terms-with-carriera", 1, 292),
    ("st-chp10-p315-streit-pictures-reflect-similarities-and-differences", 2, 293),
]:
    row = statement_by_id.get(sid)
    if not row or row["qualifiers"].get("footnote_marker") != marker or row["qualifiers"].get("pending_note_source_line") != line:
        raise SystemExit(f"expected pending body footnote not found: {sid}")
fragment = statement_by_id.get("st-chp10-p315-four-canalettos-two-scenes-linked-to-streits-life-fragment")
if not fragment or fragment["qualifiers"].get("continuation_closed_by_statement_id") != "st-chp10-p316-two-life-scenes-noted-about-streits-pictures":
    raise SystemExit("p.315-p.316 continuation is not closed")
if "cand-9531" not in candidate_ids or "cand-9904" not in candidate_ids:
    raise SystemExit("required Laurenziana or Venice candidate missing")

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


add_candidate("cand-9905", "Angelica Griè (young woman painter named in p.315 note; identity unresolved)", "person", "The print is visually read as Griè while OCR gives GriS. No fuller identity or career is inferred.", 292)
add_candidate("cand-9906", "Letter from Schulenburg to Rosalba Carriera, 28 July 1743 (Biblioteca Laurenziana, Cod. Ashburn. 1781, vol. IV, p.266)", "archive", "Letter locator as cited by Haskell. The manuscript and current catalogue were not consulted.", 292)
add_candidate("cand-9907", "Rohrlach (author cited at p.315 note 2; identity unresolved)", "person", "Surname-only author reference; no identity beyond Haskell's citation is assumed.", 293)
add_candidate("cand-9908", "Rohrlach, 1951, pages 198-200 (citation locator)", "archive", "Cited for a career outline and list of Streit pictures and their subsequent fate. The cited pages were not independently consulted.", 293)
add_candidate("cand-9909", "Denina (author cited at p.315 note 2; identity unresolved)", "person", "Surname-only author reference; no identity beyond Haskell's citation is assumed.", 293)
add_candidate("cand-9910", "Denina, page 196 (citation locator)", "archive", "Cited for Streit’s position in Venice. The cited passage was not independently consulted.", 293)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(cid, line_no, needle, note=""):
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention candidate missing: {cid}")
    line = source_lines[line_no - 1]
    at = line.find(needle)
    if at < 0:
        raise SystemExit(f"mention needle missing at L{line_no}: {needle!r}")
    segment_text = "\n".join(source_lines[272:349])
    start = sum(len(source_lines[index - 1]) + 1 for index in range(273, line_no)) + at
    if segment_text[start:start + len(needle)] != needle:
        raise SystemExit(f"mention offset mismatch at L{line_no}: {needle!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p315-note-{len(new_mentions) + 1:04d}",
        "segment_id": NOTES,
        "candidate_id": cid,
        "surface_form": needle,
        "start_char": start,
        "end_char": start + len(needle),
        "note": note,
    })
    new_mentions.append(row)


for cid, line, needle, note in [
    ("cand-2401", 292, "Schulenburg", "Author named as letter writer in Haskell's note."),
    ("cand-0581", 292, "Rosalba Carriera", "Named as letter recipient in Haskell's note."),
    ("cand-9905", 292, "Angelica GriS", "OCR span; printed reading is recorded as Griè in the linked statement."),
    ("cand-9531", 292, "Biblioteca Laurenziana", "Existing repository candidate reused."),
    ("cand-9906", 292, "MSS. Cod. Ashburn. 1781, Vol. IV, p. 266", "Specific manuscript locator cited by Haskell."),
    ("cand-2519", 293, "Streit’s career", "Contextual mention for cited career source."),
    ("cand-9907", 293, "Rohrlach", "Author surname in Haskell's citation."),
    ("cand-9908", 293, "Rohrlach, 1951, pp. 198-200", "Citation locator for career and picture list."),
    ("cand-9909", 293, "Denina", "Author surname in Haskell's citation."),
    ("cand-9910", 293, "Denina, p. 196", "Citation locator for Streit’s position in Venice."),
    ("cand-9904", 293, "Venice", "Existing p.313 place candidate reused for the same named city."),
]:
    add_mention(cid, line, needle, note)


new_statements = []


def add_statement(sid, subject, object_id, predicate, line, claim, qualification, mentioned,
                  speaker="Haskell footnote", layer="authorial note", relation_candidate=False, extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement ID already exists: {sid}")
    quote = source_lines[line - 1]
    if not quote.startswith(str(1 if line == 292 else 2) + " "):
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
        "printed_page": 315,
        "pdf_physical_page": 48,
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


add_statement("st-chp10-p315-n01-letter-to-carriera", "cand-2401", "cand-0581", "wrote_to",
              292, "Haskell says Schulenburg wrote to Rosalba Carriera on 28 July 1743.",
              "The letter is known here only through Haskell's note and its cited shelfmark; the manuscript was not consulted.",
              ["cand-2401", "cand-0581", "cand-9906", "cand-9531"],
              layer="correspondence reported in authorial note", relation_candidate=True,
              extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p315-schulenburg-good-terms-with-carriera"],
                     "date": "1743-07-28", "archive_candidate_id": "cand-9906", "repository_candidate_id": "cand-9531",
                     "shelfmark": "MSS. Cod. Ashburn. 1781, Vol. IV, p. 266"})
add_statement("st-chp10-p315-n01-recommended-assistance-for-angelica", "cand-2401", "cand-9905", "recommended_young_painter_for_carriera_assistance",
              292, "Haskell says Schulenburg recommended the young painter Angelica Griè for Rosalba Carriera's assistance.",
              "The print is visually read as Griè and the OCR reads GriS. The exact relationship is limited to Haskell's wording around the Italian phrase; Angelica's identity and the requested assistance are not otherwise specified.",
              ["cand-2401", "cand-0581", "cand-9905", "cand-9906"],
              layer="recommendation reported in authorial note", relation_candidate=True,
              extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p315-schulenburg-good-terms-with-carriera"],
                     "recipient_candidate_id": "cand-0581", "archive_candidate_id": "cand-9906",
                     "quoted_italian_phrase": "di lei amorosa assistenza",
                     "ocr_corrections": [{"source_line": 292, "ocr": "GriS", "print_reading": "Griè"}]})
add_statement("st-chp10-p315-n02-rohrlach-citation", "cand-2519", "cand-9908", "cites_streit_career_and_picture_history_source",
              293, "Haskell directs readers to Rohrlach, 1951, pages 198-200, for an outline of Streit’s career and picture list with subsequent fates.",
              "The cited pages were not independently consulted; this records only Haskell's citation and its stated scope.",
              ["cand-2519", "cand-9907", "cand-9908"], layer="bibliographic citation",
              extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p315-streit-pictures-reflect-similarities-and-differences"],
                     "citations": [{"source_candidate_id": "cand-9908", "author_candidate_id": "cand-9907", "year": "1951", "pages": ["198", "200"]}]})
add_statement("st-chp10-p315-n02-denina-citation", "cand-2519", "cand-9910", "cites_streit_position_in_venice_source",
              293, "Haskell cites Denina, page 196, for Streit’s position in Venice.",
              "The cited passage was not independently consulted; no additional biographical claim is inferred from the locator.",
              ["cand-2519", "cand-9909", "cand-9910", "cand-9904"], layer="bibliographic citation",
              extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p315-streit-pictures-reflect-similarities-and-differences"],
                     "citations": [{"source_candidate_id": "cand-9910", "author_candidate_id": "cand-9909", "page": "196"}]})

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


add_footnote_ref("st-chp10-p315-schulenburg-good-terms-with-carriera", 1, 292,
                 ["st-chp10-p315-n01-letter-to-carriera", "st-chp10-p315-n01-recommended-assistance-for-angelica"])
add_footnote_ref("st-chp10-p315-streit-pictures-reflect-similarities-and-differences", 2, 293,
                 ["st-chp10-p315-n02-rohrlach-citation", "st-chp10-p315-n02-denina-citation"])

candidate_rows = candidates + new_candidates
all_mentions = mentions + new_mentions
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate ID")
if len({row["mention_id"] for row in all_mentions}) != len(all_mentions):
    raise SystemExit("duplicate mention ID")
if len({row["statement_id"] for row in all_statements}) != len(all_statements):
    raise SystemExit("duplicate statement ID")
candidate_id_set = {row["candidate_id"] for row in candidate_rows}
for row in all_mentions:
    if row["candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing mention foreign key: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    if row["subject_candidate_id"] and row["subject_candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing statement subject: {row['statement_id']}")
    if row["object_candidate_id"] and row["object_candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing statement object: {row['statement_id']}")
    if any(cid not in candidate_id_set for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"missing statement mention foreign key: {row['statement_id']}")

coverage[BODY].update({
    "migration_status": "complete",
    "source_line_ranges": "L96-106; notes L292-293",
    "note": "Printed p.315 notes 1-2 (canonical L292-293) are linked. The L106 sentence continues to p.316 L109 and is already closed by its continuation statement.",
})
coverage[NOTES].update({
    "migration_status": "partial",
    "source_line_ranges": "L274-293; L325-349",
    "note": "P.311-315 notes L274-293 are reviewed and linked; L325-349 was previously processed. The remaining gap is L294-324 (p.316-323 notes).",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
all_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
print(f"p.315 note preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.315 partial->complete; consolidated notes remain partial")
print(f"totals: {len(candidate_rows)} candidates, {len(all_mentions)} mentions, {len(all_statements)} statements")
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
write_csv(mention_path, mention_fields, all_mentions)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; recovery copies created with suffix {BACKUP_SUFFIX}")
