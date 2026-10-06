"""Controlled S2 migration for p.285 note 1 at merged source L528."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
BODY_SEGMENT = "chp-10:10_CHP-10_intro:l167-176"
NOTES_SEGMENT = "chp-10:10_CHP-10_intro:l491-634"
TARGET_STATEMENT = "st-chp10-p284-mississippi-programme-open"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINE_SHA = "cb5412157d3fc098334a0e8e78887360151587518ee73bdbb4de86d1240b0943"
BACKUP = ".bak-s2-chp10-p285-note1-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
src = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_body = "\n".join(src[490:634])
if hashlib.sha256(notes_body.encode("utf-8")).hexdigest() != EXPECTED_NOTES_SHA:
    raise SystemExit("merged note segment changed")
if hashlib.sha256(src[527].encode("utf-8")).hexdigest() != EXPECTED_LINE_SHA:
    raise SystemExit("p.285 note 1 source line changed")
if not src[527].startswith("1 See the document published by Sensier"):
    raise SystemExit("p.285 note 1 marker or wording changed")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9340:
    raise SystemExit(f"candidate sequence changed: {maximum}")
notes_cov = cov.get(NOTES_SEGMENT)
if not notes_cov or (notes_cov["disposition"], notes_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("merged note coverage status changed")
if notes_cov["source_line_ranges"] != "L492-527":
    raise SystemExit(f"merged note coverage range changed: {notes_cov['source_line_ranges']}")
target = next((row for row in statements if row["statement_id"] == TARGET_STATEMENT), None)
if not target:
    raise SystemExit("p.284/p.285 continuation statement missing")
q = target.get("qualifiers", {})
if q.get("footnote_marker") != 1 or not q.get("footnote_text_pending"):
    raise SystemExit("p.285 note marker state changed")

NEW_CANDIDATES = [
    ("cand-9341", "Document published by Sensier (p.285 note 1, pp.97-102; title unresolved)", "archive",
     "Haskell directs readers to an unidentified document published by Sensier, cited at pp.97-102. The cited pages and publication were not independently consulted."),
    ("cand-9342", "Garas (surname-only name in p.285 note 1; identity unresolved)", "person",
     "The note gives only the surname Garas and year 1962; identity is not inferred before bibliography review and S3."),
    ("cand-9343", "Garas, 1962 (citation locator in p.285 note 1; work unresolved)", "archive",
     "Haskell's note cites Garas, 1962 without a title or further bibliographic details; the cited work was not consulted."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
new_candidates = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES_SEGMENT}#L528",
} for cid, name, kind, detail in NEW_CANDIDATES]

line = src[527]
notes_start = 0
for n in range(491, 528):
    notes_start += len(src[n - 1]) + 1
new_mentions = []


def add_mention(local, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p285note1-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"surface absent at L528: {surface!r}")
    start = notes_start + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEGMENT, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("sensier-author", "Sensier", "cand-9291", "Surname only; identity remains unresolved.")
add_mention("sensier-document", "the document published by Sensier, pp. 97-102", "cand-9341", "Citation locator only; cited material was not consulted.")
add_mention("garas-author", "Garas", "cand-9342", "Surname only; identity remains unresolved.")
add_mention("garas-source", "Garas, 1962", "cand-9343", "Citation locator only; title and cited material were not consulted.")

if len(new_mentions) != 4:
    raise SystemExit("planned p.285 note 1 mention count changed")
q["footnote_text_pending"] = False
q["footnote_link_status"] = "resolved_source_migration"
q["footnote_segment"] = NOTES_SEGMENT
q["footnote_source_line"] = 528
q["footnote_note_statement_ids"] = []
q["qualification"] = (q.get("qualification", "") +
    " P.285 note 1 supplies citation locators only: an unidentified Sensier-published document at pp.97-102 and Garas (1962). Neither cited work was consulted; Garas's identity and publication remain unresolved.").strip()

notes_cov["source_line_ranges"] = "L492-528"
notes_cov["note"] = (notes_cov.get("note", "") +
    " P.285 note 1 at L528 is citation-only: an unidentified document published by Sensier (pp.97-102) and Garas (1962); neither source was consulted. The p.285 continuation marker 1 is now linked to its own note, distinct from p.284 note 1.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p285 source L528 verified against CHP-10.pdf physical page 14")
print("planned new candidates=3, mentions=4, statements=0; closes only the p285 continuation marker 1")
print("Sensier's document identity and Garas's identity/work remain unresolved; no cited content is inferred")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
candidates.extend(new_candidates)
mentions.extend(new_mentions)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
