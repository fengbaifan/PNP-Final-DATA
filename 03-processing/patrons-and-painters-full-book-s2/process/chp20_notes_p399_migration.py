"""Migrate printed p.399 notes 1-3; dry-run by default."""
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
BACKUP_SUFFIX = ".bak-s2-chp20-notes-p399-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply p.399 note migration")
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

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

if (len(candidates), len(mentions), len(statements), len(coverage_rows)) != (11138, 25749, 11122, 832):
    raise SystemExit("unexpected S2 table pre-state")
if NOTES not in coverage_by_id:
    raise SystemExit("postscript notes coverage row missing")
coverage = coverage_by_id[NOTES]
if (coverage["disposition"], coverage["migration_status"], coverage["source_line_ranges"]) != (
    "reviewed", "partial", "L212-224"
):
    raise SystemExit(f"unexpected postscript notes coverage state: {coverage}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_text = "\n".join(source_lines[210:280])
line_offsets = {}
offset = 0
for line_number in range(211, 281):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

# marker, source line, quote, citation span, archive candidate, author surface/person candidate, linked body statements
note_specs = [
    (1, 225, "1 Buser.", "Buser", "cand-10921", "Buser", "cand-10920", [
        "st-chp20-p399-buser-challenges-jesuit-art-scepticism",
        "st-chp20-p399-nadal-engravings-commission-and-influence",
        "st-chp20-p399-buser-s-vitale-frescoes",
    ]),
    (2, 225, "2 Enggass, 1964.", "Enggass, 1964", "cand-10929", "Enggass", "cand-10928", [
        "st-chp20-p399-enggass-monograph-and-fresco-content",
        "st-chp20-p399-haskell-concedes-enggass-theological-relevance",
    ]),
    (3, 225, "3 Lavin, I., 1972, pp. 169-71.", "Lavin, I., 1972, pp. 169-71", "cand-10931", "Lavin", "cand-10859", [
        "st-chp20-p399-lavin-rejects-lanckoronska-dome-drawing-theory",
    ]),
]

for marker, line_number, quote, citation_surface, archive_id, author_surface, person_id, body_ids in note_specs:
    if archive_id not in candidate_ids or person_id not in candidate_ids:
        raise SystemExit(f"candidate FK missing for p.399 note {marker}")
    if quote not in source_lines[line_number - 1]:
        raise SystemExit(f"note quote mismatch at L{line_number}: {quote!r}")
    for body_id in body_ids:
        if body_id not in statement_by_id:
            raise SystemExit(f"body statement missing for p.399 note {marker}: {body_id}")
        refs = statement_by_id[body_id].get("qualifiers", {}).get("footnote_refs", [])
        matching = [ref for ref in refs if ref.get("marker") == marker and ref.get("segment_id") == NOTES]
        if len(matching) != 1 or matching[0].get("source_line") != line_number:
            raise SystemExit(f"body footnote link changed for note {marker}: {matching}")
        if statement_by_id[body_id]["qualifiers"].get("footnote_text_pending") is not True:
            raise SystemExit(f"body note {marker} is not pending")

existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
existing_statement_ids = set(statement_by_id)
new_mentions = []
new_statements = []


def add_mention(line_number, surface, candidate_id, marker, role, within=None):
    line = source_lines[line_number - 1]
    container_start = 0
    container = line
    if within is not None:
        container_start = line.find(within)
        if container_start < 0 or line.find(within, container_start + 1) >= 0:
            raise SystemExit(f"mention container absent or ambiguous at L{line_number}: {within!r}")
        container = within
    local_start = container.find(surface)
    if local_start < 0 or container.find(surface, local_start + 1) >= 0:
        raise SystemExit(f"mention surface absent or ambiguous at L{line_number}: {surface!r}")
    start = container_start + local_start
    end = start + len(surface)
    segment_start = line_offsets[line_number] + start
    segment_end = line_offsets[line_number] + end
    if notes_text[segment_start:segment_end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    key = (NOTES, candidate_id, str(segment_start), str(segment_end))
    if key in existing_mention_keys or any(
        (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"])) == key
        for row in new_mentions
    ):
        raise SystemExit(f"duplicate mention at L{line_number}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-chp20-notes-p399-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": segment_start,
        "end_char": segment_end,
        "note": f"Printed p.399 footnote {marker} {role}; citation is not an independent consultation of the cited work.",
    })
    new_mentions.append(row)


for marker, line_number, quote, citation_surface, archive_id, author_surface, person_id, body_ids in note_specs:
    add_mention(line_number, citation_surface, archive_id, marker, "citation locator")
    if author_surface != citation_surface:
        add_mention(line_number, author_surface, person_id, marker, "author mention", within=citation_surface)
    statement_id = f"st-chp20-p399-n{marker:02d}-citation"
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
            "printed_page": 399,
            "pdf_physical_page": 4,
            "footnote_marker": marker,
            "claim": f"Printed p.399 note {marker} cites the publication represented by {archive_id}; bibliographic detail is limited to the printed short citation.",
            "speaker": "Haskell’s footnote apparatus",
            "text_layer": "bibliographic citation",
            "qualification": "Citation transcribed from the printed note. The note does not provide a full title or edition, and the cited work has not been independently consulted. Do not infer omitted bibliographic details.",
            "mentioned_candidate_ids": [archive_id, person_id],
            "relation_candidate": False,
            "cited_material_not_independently_consulted": True,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
    }
    new_statements.append(statement)
    for body_id in body_ids:
        qualifiers = statement_by_id[body_id]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers.setdefault("footnote_statement_ids", []).append(statement_id)

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
coverage["source_line_ranges"] = "L212-225"
coverage["note"] = "Printed p.396 notes 1-6 at L212-L214, p.397 notes 1-12 at L215-L220, p.398 notes 1-7 at L221-L224, and p.399 notes 1-3 at L225 are transcribed, represented as citation statements, and linked to body statements. Cited works have not been independently consulted. P.400 onward (L226-L280) remains unprocessed."

print(f"verified p.399 notes 1-3: +{len(new_mentions)} exact mentions, +{len(new_statements)} note statements; no new candidates")
print("coverage advances to L212-225 and remains reviewed/partial")
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
print("applied; three tables backed up with suffix " + BACKUP_SUFFIX)
