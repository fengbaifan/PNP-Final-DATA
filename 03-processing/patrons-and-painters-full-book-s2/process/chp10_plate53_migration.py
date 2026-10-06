"""Controlled S2 migration for the Plate 53 caption page; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_sec_ii.md"
SEGMENT = "chp-10:10_CHP-10_sec_ii:l34-53"
EXPECTED_ASSET_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
EXPECTED_SEGMENT_SHA = "6e02d7f8f1f4d7611a368f7140091d4eb9f7acdf3c5b429b5771370b9a573740"
BACKUP_SUFFIX = ".bak-s2-chp10-plate53-20261003"


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
parser.add_argument("--apply", action="store_true", help="write the reviewed caption rows after making backups")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segment_lines = source_lines[33:53]
segment_text = "\n".join(segment_lines)
if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != EXPECTED_SEGMENT_SHA:
    raise SystemExit("S2 source segment changed")
if not segment_lines or segment_lines[0] != "[Page 53]" or "grubneluhcS" not in segment_text:
    raise SystemExit("caption OCR segment does not match the reviewed source")

candidate_path, mention_path, statement_path, coverage_path = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if (len(candidates), maximum, len(mentions), len(statements)) != (9576, 9589, 20002, 8867):
    raise SystemExit(f"table state changed: candidates={len(candidates)}/{maximum}, mentions={len(mentions)}, statements={len(statements)}")
if (coverage[SEGMENT]["disposition"], coverage[SEGMENT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"Plate 53 coverage state changed: {coverage[SEGMENT]}")
if any(row["segment_id"] == SEGMENT for row in mentions) or any(row["segment_id"] == SEGMENT for row in statements):
    raise SystemExit("Plate 53 already has S2 mention or statement rows")

EXISTING = {
    "schulenburg": "cand-2401", "piazzetta": "cand-1901", "amigoni": "cand-0094",
    "sigismund_streit": "cand-2519", "amigoni_portrait_of_streit": "cand-0099",
}
for key, cid in EXISTING.items():
    if cid not in candidate_ids:
        raise SystemExit(f"required candidate missing: {key}={cid}")

new_candidate = {field: "" for field in candidate_fields}
new_candidate.update({
    "candidate_id": "cand-9590",
    "canonical_name": "Piazzetta portrait of Marshal Johann Matthias Schulenburg (Plate 53a)",
    "suggested_type": "work", "status": "open",
    "detail": "Plate 53a caption identifies Piazzetta as painter and Marshal Schulenburg as sitter. The work has no separate title, date, or location in this caption.",
    "candidate_origin": "body-mention", "candidate_source_ref": f"{SEGMENT}#L51",
})
if new_candidate["candidate_id"] in candidate_ids:
    raise SystemExit("Plate 53 work candidate id already exists")
candidate_ids.add(new_candidate["candidate_id"])

new_mentions = []
counter = 0


def add_mention(line_no, surface, cid, note=""):
    global counter
    line = source_lines[line_no - 1]
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"mention text not found on L{line_no}: {surface!r}")
    offset = sum(len(source_lines[i]) + 1 for i in range(33, line_no - 1)) + at
    counter += 1
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-plate53-{counter:04d}", "segment_id": SEGMENT,
        "candidate_id": cid, "surface_form": surface, "start_char": offset,
        "end_char": offset + len(surface), "note": note,
    })
    new_mentions.append(row)


# OCR read the rotated plate page in reverse/interleaved order; exact raw spans are
# retained, with the printed caption reading recorded in mention notes and claims.
add_mention(51, "grubneluhcS lahsraM", "cand-9590", "OCR raw span; CHP-10.pdf physical page 42 reads 'Piazzetta: Marshal Schulenburg' for Plate 53a")
add_mention(51, "grubneluhcS", EXISTING["schulenburg"], "OCR reversed surname; print caption reads Schulenburg")
add_mention(52, "attezzai", EXISTING["piazzetta"], "OCR reversed surname; print caption reads Piazzetta")
add_mention(49, "tiertS dnumsigiS", EXISTING["amigoni_portrait_of_streit"], "OCR reversed sitter name; Plate 53b print caption reads Amigoni: Sigismund Streit")
add_mention(49, "tiertS", EXISTING["sigismund_streit"], "OCR reversed surname; print caption reads Streit")
add_mention(51, "inocimA", EXISTING["amigoni"], "OCR reversed surname; print caption reads Amigoni")

new_statements = [
    {
        "statement_id": "st-chp10-plate53a-piazzetta-schulenburg-portrait",
        "segment_id": SEGMENT, "subject_candidate_id": "cand-2401", "object_candidate_id": "cand-9590",
        "predicate": "plate_caption_identifies_piazzetta_portrait_of_schulenburg",
        "qualifiers": {
            "source_line_start": 51, "source_line_end": 53, "pdf_physical_page": 42, "plate_number": 53,
            "claim": "On Plate 53a, the printed caption reads 'Piazzetta: Marshal Schulenburg.'",
            "speaker": "printed caption", "text_layer": "figure caption checked against PDF",
            "qualification": "The OCR reverses/interleaves the caption fragments. No title, date, or location is supplied.",
            "mentioned_candidate_ids": ["cand-1901", "cand-2401", "cand-9590"], "relation_candidate": False,
            "printed_caption": "a. Piazzetta: Marshal Schulenburg",
        },
        "original_quote": "\n".join(source_lines[50:53]), "origin": "book", "source_file": SOURCE_FILE,
    },
    {
        "statement_id": "st-chp10-plate53b-amigoni-sigismund-streit-portrait",
        "segment_id": SEGMENT, "subject_candidate_id": "cand-2519", "object_candidate_id": "cand-0099",
        "predicate": "plate_caption_identifies_amigoni_portrait_of_sigismund_streit",
        "qualifiers": {
            "source_line_start": 49, "source_line_end": 51, "pdf_physical_page": 42, "plate_number": 53,
            "claim": "On Plate 53b, the printed caption reads 'Amigoni: Sigismund Streit.'",
            "speaker": "printed caption", "text_layer": "figure caption checked against PDF",
            "qualification": "The OCR reverses/interleaves the caption fragments. The existing index candidate for Amigoni's portrait of Streit is reused.",
            "mentioned_candidate_ids": ["cand-0094", "cand-0099", "cand-2519"], "relation_candidate": False,
            "printed_caption": "b. Amigoni: Sigismund Streit",
        },
        "original_quote": "\n".join(source_lines[48:51]), "origin": "book", "source_file": SOURCE_FILE,
    },
]

for row in new_mentions:
    if row["candidate_id"] not in candidate_ids:
        raise SystemExit(f"mention points to missing candidate: {row['mention_id']}")
    start, end = int(row["start_char"]), int(row["end_char"])
    if segment_text[start:end] != row["surface_form"]:
        raise SystemExit(f"mention span mismatch: {row['mention_id']}")
intervals = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in new_mentions)
for index, left in enumerate(intervals):
    for right in intervals[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = ((left[0] <= right[0] and right[1] <= left[1]) or
                  (right[0] <= left[0] and left[1] <= right[1]))
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"duplicate or crossing mention spans: {left[2]} and {right[2]}")
for row in new_statements:
    cited = "\n".join(source_lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]])
    if " ".join(row["original_quote"].split()) not in " ".join(cited.split()):
        raise SystemExit(f"statement quote mismatch: {row['statement_id']}")
    if any(cid not in candidate_ids for cid in row["qualifiers"]["mentioned_candidate_ids"]):
        raise SystemExit(f"statement candidate missing: {row['statement_id']}")
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("Plate 53 statement id already exists")

coverage[SEGMENT].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L34-53",
    "note": (
        "OCR segment '[Page 53]' is a plate number, not printed text page 53. Compared with CHP-10.pdf physical page 42, "
        "which shows Plate 53 under the heading 'German Patrons in Eighteenth-Century Venice'. Printed captions are "
        "53a 'Piazzetta: Marshal Schulenburg' and 53b 'Amigoni: Sigismund Streit'; the OCR reverses and interleaves "
        "caption fragments, so raw offsets are retained and corrected readings recorded in S2. The Streit portrait index "
        "candidate is reused; a distinct work candidate is added for the otherwise unitemized Piazzetta portrait."
    ),
})

candidate_rows = candidates + [new_candidate]
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate id")
if len({row["mention_id"] for row in mention_rows}) != len(mention_rows):
    raise SystemExit("duplicate mention id")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement id")

print(f"Plate 53 preview: +1 candidate, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print(f"coverage: {SEGMENT} reviewed/complete; resulting totals {len(candidate_rows)} candidates, {len(mention_rows)} mentions, {len(statement_rows)} statements")
if not args.apply:
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
