"""Controlled follow-up for p.382 statement scope and coverage closure."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_ii.md"
EXPECTED_SOURCE = "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3"
BODY = "chp-17:17_CHP-17_sec_ii:l7-17"
P381 = "chp-17:17_CHP-17_sec_ii:l3-5"
BACKUP_SUFFIX = ".bak-s2-chp17-p382-repair-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_SOURCE:
    raise SystemExit("registered source changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if "the physical aspect of the city" not in source_lines[12] or "early Renaissance pictures" not in source_lines[10]:
    raise SystemExit("p.382 source precondition changed")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


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


mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage}
statement_by_id = {row["statement_id"]: row for row in statements}

if "cand-3578" not in {row["candidate_id"] for row in read_csv(TABLES / "entity-candidates.csv")[1]}:
    raise SystemExit("Renaissance term candidate is missing")
if any(row["mention_id"] == "m-chp17-p382-0060" for row in mentions):
    raise SystemExit("Renaissance mention already exists")
if "st-chp17-p382-correr-collecting-aim-and-palace" not in statement_by_id:
    raise SystemExit("combined p.382 statement is missing or already repaired")
if coverage_by_id[P381]["migration_status"] != "partial":
    raise SystemExit("p.381 continuation coverage is no longer partial")

old = statement_by_id["st-chp17-p382-correr-collecting-aim-and-palace"]
source_text = "\n".join(source_lines[6:17])
surface = "Renaissance"
line11 = source_lines[10]
line_offset = sum(len(source_lines[index]) + 1 for index in range(6, 10))
local_start = line11.find(surface)
if local_start < 0:
    raise SystemExit("Renaissance surface is missing from p.382")
start, end = line_offset + local_start, line_offset + local_start + len(surface)
mentions.append({
    "mention_id": "m-chp17-p382-0060", "segment_id": BODY,
    "candidate_id": "cand-3578", "surface_form": surface,
    "start_char": str(start), "end_char": str(end),
    "note": "Historical-period term in Haskell's phrase ‘early Renaissance pictures’; mapped to the existing term candidate, without an external period or style decision.",
})

if source_text[start:end] != surface:
    raise SystemExit("Renaissance mention offset failed source check")

aim = json.loads(json.dumps(old))
aim.update({
    "statement_id": "st-chp17-p382-correr-collecting-aim",
    "object_candidate_id": "cand-0858",
    "predicate": "collected_materials_illuminating_venices_history_and_culture",
})
aim["qualifiers"].update({
    "claim": "Haskell says Correr sought books, manuscripts, prints, coins, medals, bronzes and pictures that illuminated Venice's history and cultural achievements.",
    "qualification": "This records Haskell's description of Correr's collecting aim, without treating the listed classes as an exhaustive inventory.",
    "mentioned_candidate_ids": ["cand-0857", "cand-0858", "cand-2719"],
})
aim["qualifiers"].pop("ocr_corrections", None)
aim["qualifiers"].pop("relation_candidate", None)

palace = json.loads(json.dumps(old))
palace.update({
    "statement_id": "st-chp17-p382-correr-palace-as-museum",
    "object_candidate_id": "cand-10710",
    "predicate": "palace_near_s_giovanni_decollato_described_as_museum_before_death",
})
palace["qualifiers"].update({
    "claim": "Haskell says Correr's palace near S. Giovanni Decollato was already a museum before his death.",
    "qualification": "The palace is unnamed. ‘Already a museum’ is Haskell's retrospective description and does not establish a formal museum institution at that date.",
    "mentioned_candidate_ids": ["cand-0857", "cand-10710", "cand-10711"],
    "ocr_corrections": [{
        "source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 10,
        "ocr": "already-a museum", "print": "already a museum",
        "basis": "CHP-17.pdf physical page 4, printed page 382.",
    }],
})

position = statements.index(old)
statements[position:position + 1] = [aim, palace]
renaissance_statement = statement_by_id["st-chp17-p382-correr-owned-inferior-paintings"]
mentioned = renaissance_statement["qualifiers"]["mentioned_candidate_ids"]
if "cand-3578" not in mentioned:
    mentioned.append("cand-3578")

archive_paper_mentions = [row for row in mentions if row["segment_id"] == "chp-17:17_CHP-17_sec_ii:l24-33" and row["surface_form"] == "his archives"]
if len(archive_paper_mentions) != 1 or archive_paper_mentions[0]["candidate_id"] != "cand-10699":
    raise SystemExit("p.382 archive-papers mention precondition changed")
archive_paper_mentions[0]["candidate_id"] = "cand-10722"
archive_paper_mentions[0]["note"] = "Unspecified archival papers cited as corroboration; do not equate them with the separately cited 1468/10 unit."
note3 = statement_by_id["st-chp17-p382-note3-urbani-publication"]
note3_ids = note3["qualifiers"]["mentioned_candidate_ids"]
note3["qualifiers"]["mentioned_candidate_ids"] = ["cand-10722" if value == "cand-10699" else value for value in note3_ids]

coverage_by_id[P381].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-5",
    "note": "Printed p.381 Teodoro Correr section and note 5 checked against CHP-17.pdf physical page 3. The trailing ‘However, there’ is closed by p.382 L8; p.381 footnote marker 5 and shelfmark correction remain recorded in S2.",
})

if not args.apply:
    print(json.dumps({
        "mode": "dry-run", "new_mentions": 1,
        "statement_replacements": [aim["statement_id"], palace["statement_id"]],
        "removed_statement": old["statement_id"],
        "p381_coverage": "complete", "p382_body": "partial",
    }, ensure_ascii=False))
    raise SystemExit(0)

for path in (mention_path, statement_path, coverage_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup.name}")
    shutil.copy2(path, backup)

write_csv(mention_path, mention_fields, mentions)
write_jsonl(statement_path, statements)
write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps({"mode": "applied", "new_mentions": 1, "statements_added": 1, "p381_coverage": "complete"}, ensure_ascii=False))
