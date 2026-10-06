"""Controlled S2 migration for p.283 notes 1-2 (merged source L523)."""
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
BODY = "chp-10:10_CHP-10_intro:l151-165"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINE_SHA = "b22a6b89cd8492f611a109c79208c7f724a2b3d139cc0d4e359628f0f01bb163"
BACKUP = ".bak-s2-chp10-p283-notes1-2-20261002"


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
if hashlib.sha256(src[522].encode("utf-8")).hexdigest() != EXPECTED_LINE_SHA:
    raise SystemExit("p.283 note line 523 changed")
if src[522] != "1 Pöllnitz, III, p. 274. 2 Lavagnino, p. 120, and M. Goering, 1937, pp. 233-50.":
    raise SystemExit("p.283 note 1-2 text changed")

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
if maximum != 9329:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-522":
    raise SystemExit("notes coverage pre-state changed")

body_targets = [row for row in statements if row["segment_id"] == BODY
                and row.get("qualifiers", {}).get("footnote_marker") in (1, 2)]
if len(body_targets) != 2 or {row["qualifiers"]["footnote_marker"] for row in body_targets} != {1, 2}:
    raise SystemExit("p.283 footnote body links changed")
if any(not row["qualifiers"].get("footnote_text_pending") for row in body_targets):
    raise SystemExit("one or more p.283 footnotes are already resolved")
required = {"cand-1969", "cand-7251"}
if not required <= cids:
    raise SystemExit(f"existing S2 candidates missing: {required-cids}")

NEW_CANDIDATES = [
    ("cand-9330", "Pöllnitz, vol. III, p.274 (citation locator in p.283 note 1)", "archive",
     "Haskell cites volume III, p.274 for the quoted account. The exact work is not resolved from this note alone; cited page not independently consulted."),
    ("cand-9331", "M. Goering, 1937, pp.233-250 (citation locator in p.283 note 2)", "archive",
     "Haskell gives author, year, and pages; the short note does not itself supply the article title or journal. Cited pages not independently consulted; bibliography alignment remains for its source-order review."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L523",
} for cid, name, kind, detail in NEW_CANDIDATES]

offset = sum(len(line) + 1 for line in src[490:522])
newm = []


def add_mention(local, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p283notes-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[522]
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"surface absent at L523: {surface!r}")
    start = offset + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("pollnitz-person", "Pöllnitz", "cand-1969")
add_mention("pollnitz-volume", "Pöllnitz, III, p. 274", "cand-9330", "Citation locator only; no additional claim from the cited text.")
add_mention("lavagnino", "Lavagnino, p. 120", "cand-7251", "Citation locator only; cited page not independently consulted.")
add_mention("goering", "M. Goering, 1937, pp. 233-50", "cand-9331", "Citation locator only; full bibliography alignment remains for later source-order review.")

for row in body_targets:
    q = row["qualifiers"]
    marker = q["footnote_marker"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES
    q["footnote_source_line"] = 523
    q["footnote_note_statement_ids"] = []
    q["qualification"] = (q.get("qualification", "") +
        (" P.283 note 1 is a Pöllnitz volume/page locator only; cited material was not consulted."
         if marker == 1 else
         " P.283 note 2 is a Lavagnino and M. Goering citation locator; cited pages were not consulted.")).strip()

cand_by_id = {row["candidate_id"]: row for row in candidates}
cand_by_id["cand-7251"]["detail"] += " P.283 note 2 cites p.120 without repeating a volume number; the cited page was not independently consulted."
notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-523"
notes_cov["note"] = (notes_cov.get("note", "") +
    " P.283 notes 1-2 at L523 are citation locators: Pöllnitz, vol. III, p.274; Lavagnino, p.120; M. Goering, 1937, pp.233-250. No cited pages were independently consulted; Goering bibliography alignment is deferred to the bibliography's source-order S2 pass. L524 onward remains pending.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p283 source L523 hash verified; planned new candidates=2, mentions=4, statements=0")
print("both printed footnote markers link to citation pointers; no cited text is treated as verified")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
candidates.extend(newc)
mentions.extend(newm)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
