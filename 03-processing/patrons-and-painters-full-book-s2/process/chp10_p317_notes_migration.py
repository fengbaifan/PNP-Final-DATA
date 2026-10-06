"""Controlled S2 migration for the printed p.317 notes; dry-run by default."""

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
BODY = "chp-10:10_CHP-10_sec_ii:l119-131"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BACKUP_SUFFIX = ".bak-s2-chp10-p317-notes-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.317 note rows and links")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[297] != "1 Hazard, 1935." or source_lines[298] != "2 Maugain.":
    raise SystemExit("canonical p.317 note lines L298–299 changed")

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
if state != (9905, 9918, 21046, 9355):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (BODY, NOTES):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.317 body is not reviewed/partial")
if coverage[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated footnote segment is not partial")
if any(sid.startswith("st-chp10-p317-n0") for sid in statement_ids):
    raise SystemExit("p.317 note statements already exist")
if any(row["mention_id"].startswith("m-s2-ch10-p317-note-") for row in mentions):
    raise SystemExit("p.317 note mentions already exist")
for sid, marker, line in [
    ("st-chp10-p317-intellectual-revolution-in-england-and-france", 1, 298),
    ("st-chp10-p317-dialogo-publication-date-claim", 2, 299),
]:
    row = statement_by_id.get(sid)
    if not row or row["qualifiers"].get("footnote_marker") != marker or row["qualifiers"].get("pending_note_source_line") != line:
        raise SystemExit(f"expected pending body footnote not found: {sid}")
for cid in ("cand-9685", "cand-9704"):
    if cid not in candidate_ids:
        raise SystemExit(f"required existing candidate missing: {cid}")

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


add_candidate("cand-9919", "Hazard (author cited at p.317 note 1; identity unresolved)", "person", "Surname and publication year only; do not infer a full name or title from the abbreviated note.", 298)
add_candidate("cand-9920", "Hazard, 1935 (minimal citation locator)", "archive", "Haskell gives author surname and year only. Title, publisher, and pages are absent from this note; no external lookup has been made.", 298)
add_candidate("cand-9921", "Maugain (author cited at p.317 note 2; identity unresolved)", "person", "Surname-only reference in the printed note; identity remains unresolved pending the full bibliography context.", 299)
add_candidate("cand-9922", "Maugain (minimal citation locator)", "archive", "The printed note supplies only this surname. Title, date, and pages are not present in the note and are not inferred.", 299)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []
note_block = "\n".join(source_lines[272:349])


def add_mention(cid, line_no, needle, note):
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention candidate missing: {cid}")
    line = source_lines[line_no - 1]
    at = line.find(needle)
    if at < 0:
        raise SystemExit(f"mention needle missing at L{line_no}: {needle!r}")
    offset = sum(len(source_lines[index - 1]) + 1 for index in range(273, line_no)) + at
    if note_block[offset:offset + len(needle)] != needle:
        raise SystemExit(f"mention offset mismatch at L{line_no}: {needle!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p317-note-{len(new_mentions) + 1:04d}",
        "segment_id": NOTES,
        "candidate_id": cid,
        "surface_form": needle,
        "start_char": offset,
        "end_char": offset + len(needle),
        "note": note,
    })
    new_mentions.append(row)


add_mention("cand-9920", 298, "Hazard, 1935", "Minimal citation as printed; linked statement records Hazard separately as the unresolved author candidate.")
add_mention("cand-9922", 299, "Maugain", "Surname-only citation as printed; linked statement records Maugain separately as the unresolved author candidate.")

new_statements = []


def add_statement(sid, subject, object_id, predicate, line, claim, qualification, mentioned, body_id, marker, extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement ID already exists: {sid}")
    quote = source_lines[line - 1]
    if not quote.startswith(f"{line - 297} "):
        raise SystemExit(f"note quote boundary changed: {sid}")
    if subject not in all_candidate_ids or object_id not in all_candidate_ids:
        raise SystemExit(f"statement candidate missing: {sid}")
    mentioned = list(dict.fromkeys(mentioned))
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"statement mention candidate missing: {sid}")
    qualifiers = {
        "source_line_start": line,
        "source_line_end": line,
        "printed_page": 317,
        "pdf_physical_page": 50,
        "claim": claim,
        "speaker": "Haskell footnote",
        "text_layer": "bibliographic citation",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": False,
        "footnote_number": marker,
        "linked_body_statement_ids": [body_id],
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


add_statement("st-chp10-p317-n01-hazard-citation", "cand-9685", "cand-9920", "cites_hazard_1935_for_intellectual_revolution",
              298, "Haskell cites Hazard, 1935 in the note attached to his account of the late seventeenth-century intellectual revolution.",
              "The note gives only surname and year. It does not provide a title or pages, and the cited work was not independently consulted.",
              ["cand-9685", "cand-9919", "cand-9920"], "st-chp10-p317-intellectual-revolution-in-england-and-france", 1,
              {"citations": [{"source_candidate_id": "cand-9920", "author_candidate_id": "cand-9919", "year": "1935"}]})
add_statement("st-chp10-p317-n02-maugain-citation", "cand-9704", "cand-9922", "cites_maugain_for_dialogo_publication_date",
              299, "Haskell cites Maugain in the note attached to the claim that Galileo’s Dialogo could not be published until 1744.",
              "The note supplies only the surname; full bibliographic details and the source passage were not consulted, so this records the citation link without independent confirmation.",
              ["cand-9704", "cand-9921", "cand-9922"], "st-chp10-p317-dialogo-publication-date-claim", 2,
              {"citations": [{"source_candidate_id": "cand-9922", "author_candidate_id": "cand-9921", "title": "not given in note"}]})

all_statements = statements + new_statements
statement_by_id = {row["statement_id"]: row for row in all_statements}


def add_footnote_ref(body_statement_id, marker, line, note_id):
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
    if note_id not in ids:
        ids.append(note_id)
    q["footnote_body_link_status"] = "linked"


add_footnote_ref("st-chp10-p317-intellectual-revolution-in-england-and-france", 1, 298, "st-chp10-p317-n01-hazard-citation")
add_footnote_ref("st-chp10-p317-dialogo-publication-date-claim", 2, 299, "st-chp10-p317-n02-maugain-citation")

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
    if row["subject_candidate_id"] not in candidate_id_set or row["object_candidate_id"] not in candidate_id_set:
        raise SystemExit(f"missing statement endpoint: {row['statement_id']}")
    if any(cid not in candidate_id_set for cid in row["qualifiers"]["mentioned_candidate_ids"]):
        raise SystemExit(f"missing statement mention foreign key: {row['statement_id']}")

coverage[BODY].update({
    "migration_status": "complete",
    "source_line_ranges": "L121-131; notes L298-299",
    "note": "Printed p.317 was checked against CHP-10.pdf physical p.50. Body L121–131 and notes 1–2 at canonical L298–299 are reviewed and linked. Hazard (1935) and Maugain are retained as minimal citation locators; the note lacks full bibliographic details, and neither cited work was consulted.",
})
coverage[NOTES].update({
    "source_line_ranges": "L274-299; L325-349",
    "note": "P.311–317 notes L274–299 are reviewed and linked; L325–349 was previously processed. The remaining gap is L300–324 (p.318–323 notes).",
})

candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
all_statements.sort(key=lambda row: row["statement_id"])
print(f"p.317 note preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.317 partial->complete; consolidated note coverage extends through L299")
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
