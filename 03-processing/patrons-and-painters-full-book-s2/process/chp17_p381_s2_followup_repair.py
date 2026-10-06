"""Small controlled S2 repair for p.381 mentions and OCR qualifiers."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE_I = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
SOURCE_II = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_ii.md"
SOURCE_HASHES = {
    SOURCE_I: "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4",
    SOURCE_II: "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3",
}
BODY_I = "chp-17:17_CHP-17_sec_i:l22-24"
BODY_II = "chp-17:17_CHP-17_sec_ii:l3-5"
BACKUP_SUFFIX = ".bak-s2-chp17-p381-followup-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()


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


for path, expected_hash in SOURCE_HASHES.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
        raise SystemExit(f"registered p.381 source changed: {path.name}")
source_i_lines = SOURCE_I.read_text(encoding="utf-8-sig").splitlines()
source_ii_lines = SOURCE_II.read_text(encoding="utf-8-sig").splitlines()
if "his Use" not in source_ii_lines[2] or "erotic themes" not in source_i_lines[23]:
    raise SystemExit("expected source phrases changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
candidate_rows = read_csv(candidate_path)[1]
mention_fields, mentions = read_csv(mention_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
required_candidates = {"cand-0857", "cand-0817", "cand-1313"}
if not required_candidates.issubset(candidate_ids):
    raise SystemExit("one or more index candidates for the p.381 repair are missing")
statement_by_id = {row["statement_id"]: row for row in statements}
needed = {
    "st-chp17-p381-manfrin-competitions",
    "st-chp17-p381-correr-meeting-poems",
    "st-chp17-p381-note2-catalogue-references",
}
if not needed.issubset(statement_by_id):
    raise SystemExit("p.381 statements expected by the repair are missing")
if "st-chp17-p381-correr-love-of-learning" in statement_by_id:
    raise SystemExit("love-of-learning statement is already present")

competition_mention = next((row for row in mentions if row["mention_id"] == "m-chp17-p381-0012"), None)
if not competition_mention or competition_mention["surface_form"] != "competitions" or competition_mention["candidate_id"] != "cand-1514":
    raise SystemExit("competition mention no longer matches the reviewed row")

planned = []
for cid, surface, note, mention_id, segment_id, source_lines, line_number, first_line, last_line in [
    ("cand-0857", "his Use", "Exact OCR span for Correr’s life; the page image reads ‘his life’.", "m-chp17-p381-followup-correr-learning", BODY_II, source_ii_lines, 3, 3, 5),
    ("cand-1313", "erotic themes", "Matches the p.381 topical index entry ‘Indecency and the erotic’; the four named narratives remain contest topics, not identified painting objects.", "m-chp17-p381-followup-erotic-themes", BODY_I, source_i_lines, 24, 22, 24),
]:
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention already exists: {mention_id}")
    body_line = source_lines[line_number - 1]
    position = body_line.find(surface)
    if position < 0:
        raise SystemExit(f"source span not found: {surface}")
    start = sum(len(source_lines[number - 1]) + 1 for number in range(first_line, line_number)) + position
    segment_text = "\n".join(source_lines[first_line - 1:last_line])
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset does not reproduce exact source span: {surface}")
    for row in mentions:
        if row["segment_id"] != segment_id:
            continue
        other_start, other_end = int(row["start_char"]), int(row["end_char"])
        if start < other_end and other_start < end:
            nested = (start <= other_start and other_end <= end) or (other_start <= start and end <= other_end)
            if not nested or (start, end) == (other_start, other_end):
                raise SystemExit(f"new mention overlaps an existing mention: {surface}")
    planned.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })

competition_mention["candidate_id"] = "cand-0817"
competition_mention["note"] = "Topical index candidate ‘Competitions’ includes p.381; the person entry cand-1514 remains a separate Manfrin subentry and is not used as the activity entity."
competition_statement = statement_by_id["st-chp17-p381-manfrin-competitions"]
competition_statement["object_candidate_id"] = "cand-0817"
competition_statement["qualifiers"]["mentioned_candidate_ids"] = ["cand-1512", "cand-0817", "cand-1313"]
competition_statement["qualifiers"]["competition_subjects"] = [
    "Joseph and Potiphar’s Wife", "Bathsheba bathing", "Lot and his Daughters", "Susanna and the Elders"
]
competition_statement["qualifiers"]["qualification"] = (
    "The four named narratives are topics for the proposed competitions, not identified competition outputs. "
    "Same-titled work candidates elsewhere concern different passages/paintings and are not linked here."
)
competition_statement["qualifiers"]["ocr_corrections"] = [{
    "source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 24,
    "ocr": "Potiphars Wife", "print": "Potiphar’s Wife",
    "basis": "CHP-17.pdf physical page 3, printed page 381."
}]

note2_statement = statement_by_id["st-chp17-p381-note2-catalogue-references"]
note2_statement["qualifiers"]["qualification"] = (
    "The note gives citation leads only; none of the cited works was independently consulted. "
    "The page image reads 1960 where S0 OCR has i960; the printed ‘of-the’ is retained."
)
note2_statement["qualifiers"]["ocr_corrections"] = [{
    "source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_line": 33,
    "ocr": "i960", "print": "1960",
    "basis": "CHP-17.pdf physical page 3, printed page 381."
}]

statements.append({
    "statement_id": "st-chp17-p381-correr-love-of-learning",
    "segment_id": BODY_II, "subject_candidate_id": "cand-0857", "object_candidate_id": None,
    "predicate": "showed_love_of_learning_as_young_man",
    "qualifiers": {
        "source_line_start": 3, "source_line_end": 3,
        "printed_page": 381, "pdf_physical_page": 3,
        "claim": "Haskell says Correr began to show a love of learning as a young man.",
        "speaker": "Haskell", "text_layer": "authorial report",
        "qualification": "The printed reading is ‘his life’; S0 OCR gives ‘his Use’. The correction is restricted to S2.",
        "mentioned_candidate_ids": ["cand-0857"],
        "ocr_corrections": [{
            "source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md", "source_line": 3,
            "ocr": "his Use", "print": "his life",
            "basis": "CHP-17.pdf physical page 3, printed page 381."
        }]
    },
    "original_quote": source_ii_lines[2],
    "origin": "book", "source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md"
})

if not args.apply:
    print(json.dumps({"mode": "dry-run", "new_mentions": len(planned), "new_statements": 1,
                      "reassigned_competition_candidate": "cand-0817",
                      "statement_updates": sorted(needed)}, ensure_ascii=False))
    raise SystemExit(0)

for path in (mention_path, statement_path):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing to overwrite: {backup.name}")
    shutil.copy2(path, backup)
write_csv(mention_path, mention_fields, mentions + planned)
write_jsonl(statement_path, statements)
print(json.dumps({"mode": "applied", "new_mentions": len(planned), "new_statements": 1,
                  "backups": [mention_path.name + BACKUP_SUFFIX, statement_path.name + BACKUP_SUFFIX]}, ensure_ascii=False))
