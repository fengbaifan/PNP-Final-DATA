"""Migrate printed p.397 notes 1-12; dry-run by default."""
import argparse
import csv
import hashlib
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
BACKUP_SUFFIX = ".bak-s2-chp20-notes-p397-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply p.397 note migration")
args = parser.parse_args()


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical postscript Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered postscript PDF changed")

mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

if (len(mentions), len(statements), len(coverage_rows)) != (25719, 11103, 832):
    raise SystemExit("unexpected S2 table pre-state")
if NOTES not in coverage_by_id:
    raise SystemExit("postscript notes coverage row missing")
coverage = coverage_by_id[NOTES]
if (coverage["disposition"], coverage["migration_status"], coverage["source_line_ranges"]) != (
    "reviewed", "partial", "L212-214"
):
    raise SystemExit(f"unexpected postscript notes coverage state: {coverage}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_text = "\n".join(source_lines[210:280])
line_offsets = {}
offset = 0
for line_number in range(211, 281):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

# printed quote, source line, author span, person candidate, citation span, archive candidate, body statement
note_specs = [
    (1, 215, "1 Lavin, L, 1968.", "Lavin", "cand-10859", "Lavin, L, 1968", "cand-10860", "st-chp20-p397-lavin-quote-closure"),
    (2, 215, "2 Hibbard, 1973.", "Hibbard", "cand-4872", "Hibbard, 1973", "cand-10885", "st-chp20-p397-hibbard-qualifies-baldacchino-attribution"),
    (3, 216, "3 Dubon.", "Dubon", "cand-10865", "Dubon", "cand-10866", "st-chp20-p397-french-tapestries-dubon"),
    (4, 216, "4 Barberini, 1968.", "Barberini", "cand-10867", "Barberini, 1968", "cand-10868", "st-chp20-p397-urban-viii-tapestries-don-urbano"),
    (5, 217, "5 Harris, A. S.", "Harris", "cand-10869", "Harris, A. S.", "cand-10870", "st-chp20-p397-harris-sacchi-palazzo-ceiling"),
    (6, 217, "6 Poirier.", "Poirier", "cand-10871", "Poirier", "cand-10872", "st-chp20-p397-classical-baroque-debate-poirier"),
    (7, 218, "7 Garas, 1967.", "Garas", "cand-9342", "Garas, 1967", "cand-10873", "st-chp20-p397-ludovisi-garas-inventory"),
    (8, 218, "8 Heikamp.", "Heikamp", "cand-10874", "Heikamp", "cand-10875", "st-chp20-p397-heikamp-del-monte-tuscan-court"),
    (9, 219, "9 Frommel.", "Frommel", "cand-10877", "Frommel", "cand-10878", "st-chp20-p397-frommel-del-monte-inventories"),
    (10, 219, "10 Kirwin.", "Kirwin", "cand-10879", "Kirwin", "cand-10880", "st-chp20-p397-kirwin-del-monte-inventories"),
    (11, 220, "11 Spezzaferro.", "Spezzaferro", "cand-10881", "Spezzaferro", "cand-10882", "st-chp20-p397-spezzaferro-del-monte-caravaggio"),
    (12, 220, "12 Posner, 1971.", "Posner", "cand-10883", "Posner, 1971", "cand-10884", "st-chp20-p397-posner-caravaggio-early-works"),
]

candidate_path = TABLES / "entity-candidates.csv"
_, candidates = read_csv(candidate_path)
candidate_ids = {row["candidate_id"] for row in candidates}
for marker, line_number, quote, author_surface, person_id, citation_surface, archive_id, body_id in note_specs:
    if person_id not in candidate_ids or archive_id not in candidate_ids:
        raise SystemExit(f"candidate FK missing for p.397 note {marker}")
    if quote not in source_lines[line_number - 1]:
        raise SystemExit(f"note quote mismatch at L{line_number}: {quote!r}")
    if body_id not in statement_by_id:
        raise SystemExit(f"body statement missing for p.397 note {marker}: {body_id}")
    refs = statement_by_id[body_id].get("qualifiers", {}).get("footnote_refs", [])
    matching = [ref for ref in refs if ref.get("marker") == marker and ref.get("segment_id") == NOTES]
    if len(matching) != 1 or matching[0].get("source_line") != line_number:
        raise SystemExit(f"body footnote link changed for note {marker}: {matching}")
    if statement_by_id[body_id]["qualifiers"].get("footnote_text_pending") is not True:
        raise SystemExit(f"body note {marker} is not pending")

existing_statement_ids = set(statement_by_id)
existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
new_statements = []
note_ids_by_marker = {}


def add_mention(line_number, surface, candidate_id, marker, role):
    if candidate_id not in candidate_ids:
        raise SystemExit(f"candidate FK missing for p.397 note {marker}: {candidate_id}")
    line = source_lines[line_number - 1]
    start_in_line = line.find(surface)
    if start_in_line < 0 or line.find(surface, start_in_line + 1) >= 0:
        raise SystemExit(f"mention surface absent or ambiguous at L{line_number}: {surface!r}")
    start = line_offsets[line_number] + start_in_line
    end = start + len(surface)
    if notes_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    key = (NOTES, candidate_id, str(start), str(end))
    if key in existing_mention_keys or any(
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"])) == key
        for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention at L{line_number}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-chp20-notes-p397-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": f"Printed p.397 footnote {marker} {role}; citation is not an independent consultation of the cited work.",
    })
    new_mentions.append(row)


for marker, line_number, quote, author_surface, person_id, citation_surface, archive_id, body_id in note_specs:
    add_mention(line_number, citation_surface, archive_id, marker, "citation locator")
    # Where the short citation is only the author's surname, one exact source
    # span cannot be represented as two separate mentions; the person remains
    # linked in the statement's mentioned_candidate_ids.
    if author_surface != citation_surface:
        add_mention(line_number, author_surface, person_id, marker, "author mention")
    claim = f"Printed p.397 note {marker} cites the publication represented by {archive_id}; bibliographic detail is limited to the printed short citation."
    qualification = "Citation transcribed from the printed note. The note does not provide a full title or edition, and the cited work has not been independently consulted. Do not infer omitted bibliographic details."
    corrections = []
    if marker == 1:
        qualification += " The OCR source reads 'Lavin, L, 1968'; the p.397 scan reads 'Lavin, I., 1968'. The source transcription is not rewritten."
        corrections.append({"source_reading": "Lavin, L, 1968", "print_reading": "Lavin, I., 1968", "basis": "CHP-20Postscript.pdf physical page 2"})
    statement_id = f"st-chp20-p397-n{marker:02d}-citation"
    if statement_id in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    statement = {
        "statement_id": statement_id,
        "segment_id": NOTES,
        "subject_candidate_id": None,
        "object_candidate_id": archive_id,
        "predicate": "footnote_cites_publication",
        "qualifiers": {
            "source_line_start": line_number,
            "source_line_end": line_number,
            "printed_page": 397,
            "pdf_physical_page": 2,
            "footnote_marker": marker,
            "claim": claim,
            "speaker": "Haskell’s footnote apparatus",
            "text_layer": "bibliographic citation",
            "qualification": qualification,
            "mentioned_candidate_ids": [archive_id, person_id],
            "relation_candidate": False,
            "cited_material_not_independently_consulted": True,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
    }
    if corrections:
        statement["qualifiers"]["ocr_corrections"] = corrections
    new_statements.append(statement)
    note_ids_by_marker[marker] = [statement_id]
    body = statement_by_id[body_id]
    qualifiers = body["qualifiers"]
    qualifiers["footnote_text_pending"] = False
    qualifiers["footnote_body_link_status"] = "linked"
    qualifiers["footnote_statement_ids"] = note_ids_by_marker[marker]

mention_out = mentions + new_mentions
statement_out = statements + new_statements
if len({row["mention_id"] for row in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique")
if len({row["statement_id"] for row in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique")
for row in new_mentions:
    if notes_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"mention exact-span audit failed: {row['mention_id']}")
for row in new_statements:
    if row["original_quote"] not in notes_text:
        raise SystemExit(f"statement quote is not anchored: {row['statement_id']}")

coverage["disposition"] = "reviewed"
coverage["migration_status"] = "partial"
coverage["source_line_ranges"] = "L212-220"
coverage["note"] = "Printed p.396 notes 1-6 at L212-L214 and p.397 notes 1-12 at L215-L220 are transcribed, represented as citation statements, and linked to body statements. Cited works have not been independently consulted. P.398 onward (L221-L280) remains unprocessed."

print(f"verified p.397 notes 1-12: +{len(new_mentions)} exact mentions, +{len(new_statements)} note statements; no new candidates")
print("coverage advances to L212-220 and remains reviewed/partial")
if not args.apply:
    print("dry-run only; pass --apply to write")
    raise SystemExit(0)

for path in (mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
    backup.write_bytes(path.read_bytes())
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied; backups=" + ", ".join(path.name + BACKUP_SUFFIX for path in (mention_path, statement_path, coverage_path)))
