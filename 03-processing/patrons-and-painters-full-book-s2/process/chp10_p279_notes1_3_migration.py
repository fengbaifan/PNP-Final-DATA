"""Controlled S2 migration for p.279 notes 1-3 and detached Plate 47 fragment."""
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
BODY = "chp-10:10_CHP-10_intro:l43-49"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "4c6fe9d3b57e92b4782d9335823aeefefb6cad335a1b9ca08eebe556e7cefeb3"
BACKUP = ".bak-s2-chp10-p279-notes1-3-20261002"
PLATE_STATEMENT = "st-chp10-p279-marco-musical-groups-hogarth"


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
if hashlib.sha256("\n".join(src[505:509]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.279 source lines 506-509 changed")
if src[505].strip() != "47)." or not src[506].startswith("1 See above all"):
    raise SystemExit("p.279 footnote boundary changed")

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
if maximum != 9300:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-505":
    raise SystemExit("notes coverage pre-state changed")

body_targets = [row for row in statements if row["segment_id"] == BODY
                and row.get("qualifiers", {}).get("footnote_marker") in (1, 2, 3)]
if len(body_targets) != 5 or {row["qualifiers"]["footnote_marker"] for row in body_targets} != {1, 2, 3}:
    raise SystemExit("p.279 footnote body links changed")
if any(not row["qualifiers"].get("footnote_text_pending") for row in body_targets):
    raise SystemExit("one or more p.279 footnotes are already resolved")

plate_statement = next((row for row in statements if row["statement_id"] == PLATE_STATEMENT), None)
if not plate_statement or plate_statement["segment_id"] != BODY:
    raise SystemExit("existing Plate 47 body statement missing")
if "(Plate" not in plate_statement["original_quote"]:
    raise SystemExit("existing Plate 47 statement anchor changed")
if plate_statement.get("qualifiers", {}).get("source_fragment_reconciliations"):
    raise SystemExit("Plate 47 source fragment already reconciled")

needed = {"cand-2803", "cand-7255", "cand-9285"}
if not needed <= cids:
    raise SystemExit(f"existing citation candidates missing: {needed-cids}")
cand_by_id = {row["candidate_id"]: row for row in candidates}
if "volume III, p.94" in cand_by_id["cand-7255"].get("detail", ""):
    raise SystemExit("Vertue locator already recorded")

NEW_CANDIDATES = [
    ("cand-9301", "Watson, Journal of R.I.B.A., 1954, pp.171-177 (citation locator; article title unresolved)", "archive",
     "Citation in Haskell's p.279 note 1 for the section. The source OCR reads 'Journal os'; the print scan reads 'Journal of'. Cited pages not independently consulted."),
    ("cand-9302", "Mostra di Pellegrini, 1959, p.56 (citation locator)", "archive",
     "Citation in Haskell's p.279 note 3 for the Pierre Motteux drawing; cited page not independently consulted. Keep distinct from the same exhibition's p.15 locator pending S3."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L{507 if cid == 'cand-9301' else 509}",
} for cid, name, kind, detail in NEW_CANDIDATES]

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []


def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p279notes-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in newm):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = offsets[line_no] + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    newm.append({
        "mention_id": mention_id, "segment_id": NOTES, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("watson-source", 507, "Watson, in Journal os R.I.B.A., 1954, pp. 171-7.", "cand-9301",
            "S0 OCR retained in the mention anchor; print scan confirms 'of' and abbreviated pages 171-7.")
add_mention("watson-author", 507, "Watson", "cand-2803")
add_mention("vertue-notebooks", 508, "Vertue, HI, p. 94.", "cand-7255",
            "S0 OCR reads HI; print scan reads Roman III, p.94.")
add_mention("mostra-p56", 509, "Mostra di Pellegrini, 1959, p. 56.", "cand-9302")

cand_by_id["cand-7255"]["detail"] = (cand_by_id["cand-7255"].get("detail", "") +
    " Also cited at p.279 note 2 as vol. III, p.94; the cited passage was not independently consulted.").strip()

for row in body_targets:
    marker = row["qualifiers"]["footnote_marker"]
    q = row["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES
    q["footnote_source_line"] = {1: 507, 2: 508, 3: 509}[marker]
    q["footnote_note_statement_ids"] = []
    if marker == 1:
        q["qualification"] = (q.get("qualification", "") + " P.279 note 1 is a source pointer to Watson; the cited pages were not independently consulted.").strip()
    elif marker == 2:
        q["qualification"] = (q.get("qualification", "") + " P.279 note 2 points to Vertue, vol. III, p.94; the cited passage was not independently consulted.").strip()
    elif marker == 3:
        q["qualification"] = (q.get("qualification", "") + " P.279 note 3 points to Mostra di Pellegrini 1959, p.56; the cited page was not independently consulted.").strip()

plate_statement["qualifiers"].setdefault("source_fragment_reconciliations", []).append({
    "source_file": SOURCE_FILE, "source_line": 506, "source_text": "47).",
    "role": "detached continuation of the p.279 body plate reference, misplaced in the merged footnote source segment",
    "print_reading": "(Plate 47).", "target_statement_id": PLATE_STATEMENT,
    "basis": "CHP-10.pdf physical page 4",
})

notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-509"
notes_cov["note"] = (notes_cov.get("note", "") +
    " P.279 source L506 is a detached body-text continuation '47).' completing the Plate 47 reference in body segment l43-49; it is linked to the existing statement without a duplicate mention. P.279 notes 1-3 at L507-L509 are citation pointers to Watson, Vertue, and Mostra di Pellegrini; none was independently consulted. L510 onward remains pending.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p279 lines 506-509 verified; planned new candidates=2, mentions=4, statements=0")
print("detached Plate 47 fragment reconciles to an existing p279 body statement; not double counted")
print("three footnotes resolve five body links as citation trails only")
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
