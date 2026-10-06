"""Migrate printed p.396 notes 1-6; dry-run by default."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
BACKUP_SUFFIX = ".bak-s2-chp20-notes-p396-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply p.396 note migration")
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
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

if (len(candidates), len(mentions), len(statements), len(coverage_rows)) != (11135, 25704, 11096, 832):
    raise SystemExit("unexpected S2 table pre-state")
if NOTES not in coverage_by_id:
    raise SystemExit("postscript notes coverage row missing")
coverage = coverage_by_id[NOTES]
if (coverage["disposition"], coverage["migration_status"], coverage["source_line_ranges"]) != ("queued", "pending", ""):
    raise SystemExit(f"unexpected postscript notes coverage state: {coverage}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_text = "\n".join(source_lines[210:280])
line_offsets = {}
offset = 0
for line_number in range(211, 281):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

candidate_specs = [
    ("cand-11157", "Bellori, 1976, p. 224 (citation locator; title and edition unspecified)",
     "archive", "Short-form citation printed in p.396 note 4. The note supplies Bellori, year and page but no title or edition; cited work not independently consulted.", 213),
    ("cand-11158", "Mancini, volume I, p. 227 (citation locator; title and edition unspecified)",
     "archive", "Short-form citation printed in p.396 note 4. The note supplies Mancini, volume and page but no title or edition; cited work not independently consulted.", 213),
]
new_candidates = []
for candidate_id, name, kind, detail, line_number in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"].casefold() == name.casefold() for row in candidates):
        raise SystemExit(f"candidate natural-key collision: {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
    })
    new_candidates.append(row)

all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
for candidate_id in ("cand-10850", "cand-10851", "cand-10852", "cand-4787", "cand-10853", "cand-10854", "cand-10855", "cand-0272", "cand-1507", "cand-5505", "cand-10856", "cand-4872", "cand-5163"):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"required candidate missing: {candidate_id}")

new_mentions = []
existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}


def add_mention(line_number, surface, candidate_id):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for mention {surface!r}: {candidate_id}")
    line = source_lines[line_number - 1]
    start_in_line = line.find(surface)
    if start_in_line < 0 or line.find(surface, start_in_line + 1) >= 0:
        raise SystemExit(f"mention surface is absent or ambiguous at L{line_number}: {surface!r}")
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
        "mention_id": f"m-s2-chp20-notes-p396-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": "Printed p.396 footnote citation; bibliographic work is not independently consulted.",
    })
    new_mentions.append(row)


# Each archive mention spans the citation; the author mention is nested inside it.
mention_specs = [
    (212, "Fagiolo dell’Arca and Carandini", "cand-10852"),
    (212, "Fagiolo dell’Arca", "cand-10850"),
    (212, "Carandini", "cand-10851"),
    (212, "Lavin, M. A.", "cand-10853"),
    (212, "Lavin", "cand-4787"),
    (213, "d’Onofrio, 1967", "cand-10855"),
    (213, "d’Onofrio", "cand-10854"),
    (213, "Bellori, 1976, p. 224", "cand-11157"),
    (213, "Bellori", "cand-0272"),
    (213, "Mancini, I, p. 227", "cand-11158"),
    (213, "Mancini", "cand-1507"),
    (214, "Longhi, 1963", "cand-10856"),
    (214, "Longhi", "cand-5505"),
    (214, "Hibbard, 1971", "cand-5163"),
    (214, "Hibbard", "cand-4872"),
]
for spec in mention_specs:
    add_mention(*spec)

note_specs = [
    ("st-chp20-p396-n01-study-citation", 1, 212, "1 Fagiolo dell’Arca and Carandini.", "cand-10852",
     "Printed p.396 note 1 names Fagiolo dell’Arca and Carandini as the cited authors; it does not supply the study title.", ["cand-10852", "cand-10850", "cand-10851"]),
    ("st-chp20-p396-n02-lavin-citation", 2, 212, "2 Lavin, M. A.", "cand-10853",
     "Printed p.396 note 2 gives an abbreviated citation to Lavin; it does not supply the publication title.", ["cand-10853", "cand-4787"]),
    ("st-chp20-p396-n03-donofrio-citation", 3, 213, "3 d’Onofrio, 1967.", "cand-10855",
     "Printed p.396 note 3 cites d’Onofrio (1967); the short note supplies no title or page locator.", ["cand-10855", "cand-10854"]),
    ("st-chp20-p396-n04-bellori-citation", 4, 213, "Bellori, 1976, p. 224", "cand-11157",
     "Printed p.396 note 4 cites Bellori (1976), page 224; title and edition are unspecified in the note.", ["cand-11157", "cand-0272"]),
    ("st-chp20-p396-n04-mancini-citation", 4, 213, "Mancini, I, p. 227", "cand-11158",
     "Printed p.396 note 4 cites Mancini, volume I, page 227; title and edition are unspecified in the note.", ["cand-11158", "cand-1507"]),
    ("st-chp20-p396-n05-longhi-citation", 5, 214, "5 Longhi, 1963.", "cand-10856",
     "Printed p.396 note 5 cites Longhi (1963); the short note supplies no title or page locator.", ["cand-10856", "cand-5505"]),
    ("st-chp20-p396-n06-hibbard-citation", 6, 214, "6 Hibbard, 1971.", "cand-5163",
     "Printed p.396 note 6 cites Hibbard (1971); the short note supplies no title or page locator.", ["cand-5163", "cand-4872"]),
]
new_statements = []
note_ids_by_marker = {}
for statement_id, marker, line_number, quote, archive_id, claim, mentioned in note_specs:
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    if quote not in source_lines[line_number - 1]:
        raise SystemExit(f"note quote not found at L{line_number}: {quote!r}")
    statement = {
        "statement_id": statement_id,
        "segment_id": NOTES,
        "subject_candidate_id": None,
        "object_candidate_id": archive_id,
        "predicate": "footnote_cites_publication",
        "qualifiers": {
            "source_line_start": line_number,
            "source_line_end": line_number,
            "printed_page": 396,
            "pdf_physical_page": 1,
            "footnote_marker": marker,
            "claim": claim,
            "speaker": "Haskell’s footnote apparatus",
            "text_layer": "bibliographic citation",
            "qualification": "Citation transcribed from the printed note. Cited work has not been independently consulted; do not infer omitted title or edition details.",
            "mentioned_candidate_ids": mentioned,
            "relation_candidate": False,
            "cited_material_not_independently_consulted": True,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
    }
    new_statements.append(statement)
    note_ids_by_marker.setdefault(marker, []).append(statement_id)

body_links = {
    "st-chp20-p396-fagiolo-carandini-study": 1,
    "st-chp20-p396-lavin-barberini-inventory-publication": 2,
    "st-chp20-p396-donofrio-documents-on-maffeo": 3,
    "st-chp20-p396-bellori-mancini-caravaggio-portrait-claim": 4,
    "st-chp20-p396-longhi-alternative-portrait": 5,
    "st-chp20-p396-hibbard-maderno-monograph": 6,
}
for statement_id, marker in body_links.items():
    if statement_id not in statement_by_id:
        raise SystemExit(f"body statement missing: {statement_id}")
    qualifiers = statement_by_id[statement_id]["qualifiers"]
    refs = qualifiers.get("footnote_refs", [])
    matching = [ref for ref in refs if ref.get("marker") == marker and ref.get("segment_id") == NOTES]
    if len(matching) != 1 or matching[0].get("source_line") != ({1: 212, 2: 212, 3: 213, 4: 213, 5: 214, 6: 214}[marker]):
        raise SystemExit(f"p.396 note {marker} link changed for {statement_id}: {matching}")
    if qualifiers.get("footnote_text_pending") is not True:
        raise SystemExit(f"p.396 note {marker} is not pending for {statement_id}")
    qualifiers["footnote_text_pending"] = False
    qualifiers["footnote_body_link_status"] = "linked"
    qualifiers["footnote_statement_ids"] = note_ids_by_marker[marker]

coverage["disposition"] = "reviewed"
coverage["migration_status"] = "partial"
coverage["source_line_ranges"] = "L212-214"
coverage["note"] = "Printed p.396 footnotes 1-6 at L212-L214 are transcribed, represented as citation candidates/statements, and linked to their body statements. The cited works are not independently consulted. P.397 onward (L215-L280) remains unprocessed."

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = statements + new_statements
if len({row["candidate_id"] for row in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique")
if len({row["mention_id"] for row in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique")
if len({row["statement_id"] for row in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique")
candidate_ids_out = {row["candidate_id"] for row in candidate_out}
for row in new_mentions:
    if row["candidate_id"] not in candidate_ids_out:
        raise SystemExit(f"mention FK missing: {row['mention_id']}")
    if notes_text[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"mention exact span failed: {row['mention_id']}")
for row in new_statements:
    if row["original_quote"] not in notes_text:
        raise SystemExit(f"statement quote not anchored: {row['statement_id']}")

print(f"verified p.396 notes 1-6: +{len(new_candidates)} citation candidates, +{len(new_mentions)} exact mentions, +{len(new_statements)} note statements")
print("coverage advances to L212-214 and remains reviewed/partial")
if not args.apply:
    print("dry-run only; pass --apply to write")
else:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidate_out)
    write_csv(mention_path, mention_fields, mention_out)
    write_jsonl(statement_path, statement_out)
    write_csv(coverage_path, coverage_fields, coverage_rows)
    if len(read_csv(candidate_path)[1]) != len(candidate_out):
        raise SystemExit("candidate readback count mismatch")
    if len(read_csv(mention_path)[1]) != len(mention_out):
        raise SystemExit("mention readback count mismatch")
    if len(read_jsonl(statement_path)) != len(statement_out):
        raise SystemExit("statement readback count mismatch")
    print("applied; backups=" + ", ".join(backup.name for _, backup in backups))
