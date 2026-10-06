"""Migrate printed p.400 notes 1-8 and the discovery claim in note 8."""
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
P400_BODY = "chp-20:20_CHP-20Postscript:l46-57"
BACKUP_SUFFIX = ".bak-s2-chp20-notes-p400-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply p.400 note migration")
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

if (len(candidates), len(mentions), len(statements), len(coverage_rows)) != (11138, 25754, 11125, 832):
    raise SystemExit("unexpected S2 table pre-state")
coverage = coverage_by_id.get(NOTES)
if coverage is None or (coverage["disposition"], coverage["migration_status"], coverage["source_line_ranges"]) != (
    "reviewed", "partial", "L212-225"
):
    raise SystemExit(f"unexpected postscript notes coverage state: {coverage}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_text = "\n".join(source_lines[210:280])
line_offsets = {}
offset = 0
for line_number in range(211, 281):
    line_offsets[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1

candidate_specs = [
    ("cand-11160", "Vittorio Casale publication cited for censor’s comments on the Ottonelli–Berrettini treatise (title and date unspecified)", "archive", 227,
     "P.400 note 4 cites Casale in the context of his discovery of censor's comments. The cited publication is not identified by title or date and was not independently consulted."),
    ("cand-11161", "Jacob Hess, 1963 publication on the early building history of Chiesa Nuova (title unspecified)", "archive", 228,
     "P.400 note 5 gives Hess and 1963 but no title or edition; cited scholarship was not independently consulted."),
    ("cand-11162", "Bonadonna Russo, 1968 publication cited at p.135 (title unspecified)", "archive", 228,
     "P.400 note 6 gives Bonadonna Russo, 1968, p.135; full publication identity awaits bibliography review and the work was not independently consulted."),
    ("cand-11163", "Bonadonna Russo, 1967 and 1968 publications (citation group; titles unspecified)", "archive", 229,
     "P.400 note 7 cites publications from 1967 and 1968 without titles. Preserve this as a citation group until bibliography review identifies whether and how the entries divide."),
    ("cand-11164", "Marcello del Piazzo (document finder named in p.400 note 8; identity unresolved)", "person", 230,
     "The p.400 footnote attributes finding the referenced documents in 1969 to Marcello del Piazzo. No further identity details are supplied here."),
]
existing_natural_keys = {(row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold()) for row in candidates}
new_candidates = []
for candidate_id, name, kind, line_number, detail in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    natural_key = (name.strip().casefold(), kind.casefold())
    if natural_key in existing_natural_keys:
        raise SystemExit(f"candidate natural key already exists: {name}")
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
    candidate_by_id[candidate_id] = row
    existing_natural_keys.add(natural_key)
candidate_ids = set(candidate_by_id)

# marker, source line, quote, citation span, archive candidate, author spans/persons, body statement IDs, corrections
note_specs = [
    (1, 226, "1 LnAALSS, 1974.", "LnAALSS, 1974", "cand-10934", [("Enggass", "cand-10928")], ["st-chp20-p400-enggass-jesuit-altar-article"],
     [{"source_reading": "LnAALSS, 1974", "print_reading": "Enggass, 1974", "basis": "CHP-20Postscript.pdf physical page 5"}]),
    (2, 226, "2 Enggass, 1976.", "Enggass, 1976", "cand-10935", [("Enggass", "cand-10928")], ["st-chp20-p400-enggass-rome-sculpture-book"], []),
    (3, 227, "3 Ottonelli and Berrettini.", "Ottonelli and Berrettini", "cand-4979", [("Ottonelli", "cand-1800"), ("Berrettini", "cand-0342")], ["st-chp20-p400-casale-ottonelli-treatise-and-censor"], []),
    (4, 227, "4 Casale.", "Casale", "cand-11160", [("Casale", "cand-10937")], ["st-chp20-p400-casale-ottonelli-treatise-and-censor"], []),
    (5, 228, "5 Hess, 1963.", "Hess, 1963", "cand-11161", [("Hess", "cand-10940")], ["st-chp20-p400-oratorian-building-history-and-chapel-autonomy"], []),
    (6, 228, "6 Bonadonna Russo, 1968, p. 13 5.", "Bonadonna Russo, 1968, p. 13 5", "cand-11162", [("Bonadonna Russo", "cand-10943")], ["st-chp20-p400-cesi-self-restraint-and-1581-letter"],
     [{"source_reading": "p. 13 5", "print_reading": "p. 135", "basis": "CHP-20Postscript.pdf physical page 5"}]),
    (7, 229, "7 Bonadonna Russo, 1967 and 1968.", "Bonadonna Russo, 1967 and 1968", "cand-11163", [("Bonadonna Russo", "cand-10943")], ["st-chp20-p400-bonadonna-russo-longhi-and-angelo-cesi"], []),
    (8, 230, "8 Brejon, p. 94, note 21—the documents were found in 1969 by Marcello del Piazzo.", "Brejon, p. 94, note 21", "cand-10954", [("Brejon", "cand-10955")], ["st-chp20-p400-cassiano-family-inventory-discovery"], []),
]

for marker, line_number, quote, citation_surface, archive_id, authors, body_ids, corrections in note_specs:
    if archive_id not in candidate_ids:
        raise SystemExit(f"archive candidate missing for p.400 note {marker}: {archive_id}")
    if quote not in source_lines[line_number - 1]:
        raise SystemExit(f"note quote mismatch at L{line_number}: {quote!r}")
    for surface, person_id in authors:
        if person_id not in candidate_ids:
            raise SystemExit(f"author candidate missing for note {marker}: {person_id}")
    for body_id in body_ids:
        if body_id not in statement_by_id:
            raise SystemExit(f"body statement missing for note {marker}: {body_id}")
        refs = statement_by_id[body_id].get("qualifiers", {}).get("footnote_refs", [])
        matching = [ref for ref in refs if ref.get("marker") == marker and ref.get("segment_id") == NOTES]
        if len(matching) != 1 or matching[0].get("source_line") != line_number:
            raise SystemExit(f"body footnote link changed for note {marker}: {matching}")
        if statement_by_id[body_id]["qualifiers"].get("footnote_text_pending") is not True:
            raise SystemExit(f"body note {marker} is not pending")

discovery_id = "st-chp20-p400-n08-document-discovery"
if discovery_id in statement_by_id:
    raise SystemExit(f"statement already exists: {discovery_id}")
for candidate_id in ("cand-10946", "cand-11164"):
    if candidate_id not in candidate_ids:
        raise SystemExit(f"discovery endpoint candidate missing: {candidate_id}")

existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
existing_statement_ids = set(statement_by_id)
new_mentions = []
new_statements = []


def add_mention(line_number, surface, candidate_id, marker, role, within=None):
    if candidate_id not in candidate_ids:
        raise SystemExit(f"candidate FK missing for p.400 note {marker}: {candidate_id}")
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
    start = line_offsets[line_number] + container_start + local_start
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
        "mention_id": f"m-s2-chp20-notes-p400-{len(new_mentions) + 1:03d}",
        "segment_id": NOTES,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": f"Printed p.400 footnote {marker} {role}; citation is not an independent consultation of the cited work.",
    })
    new_mentions.append(row)


for marker, line_number, quote, citation_surface, archive_id, authors, body_ids, corrections in note_specs:
    add_mention(line_number, citation_surface, archive_id, marker, "citation locator")
    for surface, person_id in authors:
        if surface != citation_surface and surface in citation_surface:
            add_mention(line_number, surface, person_id, marker, "author mention", within=citation_surface)
    statement_id = f"st-chp20-p400-n{marker:02d}-citation"
    if statement_id in existing_statement_ids:
        raise SystemExit(f"statement already exists: {statement_id}")
    statement = {
        "statement_id": statement_id,
        "segment_id": NOTES,
        "subject_candidate_id": None,
        "object_candidate_id": archive_id,
        "predicate": "footnote_cites_publication",
        "qualifiers": {
            "source_line_start": line_number,
            "source_line_end": line_number,
            "printed_page": 400,
            "pdf_physical_page": 5,
            "footnote_marker": marker,
            "claim": f"Printed p.400 note {marker} cites the publication represented by {archive_id}; citation detail is limited to the note and body context.",
            "speaker": "Haskell’s footnote apparatus",
            "text_layer": "bibliographic citation",
            "qualification": "Short citation only; title/edition details not supplied here. The cited publication has not been independently consulted. Do not infer omitted bibliographic details.",
            "mentioned_candidate_ids": [archive_id] + [person_id for _, person_id in authors],
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
    for body_id in body_ids:
        qualifiers = statement_by_id[body_id]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers.setdefault("footnote_statement_ids", []).append(statement_id)

    if marker == 8:
        add_mention(230, "the documents", "cand-10946", marker, "subject of discovery statement")
        add_mention(230, "Marcello del Piazzo", "cand-11164", marker, "named document finder")
        new_statements.append({
            "statement_id": discovery_id,
            "segment_id": NOTES,
            "subject_candidate_id": "cand-10946",
            "object_candidate_id": "cand-11164",
            "predicate": "footnote_reports_documents_found_by",
            "qualifiers": {
                "source_line_start": 230,
                "source_line_end": 230,
                "printed_page": 400,
                "pdf_physical_page": 5,
                "footnote_marker": 8,
                "claim": "Haskell’s p.400 footnote says Marcello del Piazzo found the referenced documents in 1969.",
                "speaker": "Haskell’s footnote apparatus",
                "text_layer": "documentary discovery note",
                "qualification": "The footnote reports the discovery attribution; it is not independent confirmation of the documents or their discovery history.",
                "time": "1969",
                "mentioned_candidate_ids": ["cand-10946", "cand-11164"],
                "relation_candidate": True,
            },
            "original_quote": "the documents were found in 1969 by Marcello del Piazzo.",
            "origin": "book",
            "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        })
        statement_by_id[body_id]["qualifiers"]["footnote_statement_ids"].append(discovery_id)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = statements + new_statements
if len({row["candidate_id"] for row in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique")
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
coverage["source_line_ranges"] = "L212-230"
coverage["note"] = "Printed p.396 notes 1-6 at L212-L214, p.397 notes 1-12 at L215-L220, p.398 notes 1-7 at L221-L224, p.399 notes 1-3 at L225, and p.400 notes 1-8 at L226-L230 are transcribed, represented as citation statements, and linked to body statements. P.400 notes 9-10 are separately captured at body source L57. Cited works have not been independently consulted. P.401 onward (L231-L280) remains unprocessed."

print(f"verified p.400 notes 1-8: +{len(new_candidates)} candidates, +{len(new_mentions)} exact mentions, +{len(new_statements)} note statements")
print("p.400 notes 9-10 are already captured at body source L57; coverage advances to L212-230 and remains partial")
if not args.apply:
    print("dry-run only; pass --apply to write")
    raise SystemExit(0)

for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
    backup.write_bytes(path.read_bytes())
write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied; four tables backed up with suffix " + BACKUP_SUFFIX)
