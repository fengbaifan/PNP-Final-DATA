"""Controlled S2 migration for p.278 footnotes 1-6; dry-run unless --apply."""
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
BODY = "chp-10:10_CHP-10_intro:l26-41"
NOTES = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "c2dedba0f20f5a1958721cb8ffbdb044bddb69c7ef6c95967058e84f050b8fa9"
BACKUP = ".bak-s2-chp10-p278-notes1-6-20261002"


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
if hashlib.sha256("\n".join(src[499:505]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.278 notes 1-6 changed")
if not src[501].startswith("3 Donzelli") or "Amigonis in Nymphenburg date from 1716" not in src[502]:
    raise SystemExit("p.278 note text mismatch")

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
if maximum != 9295:
    raise SystemExit(f"candidate sequence changed: {maximum}")
for seg, expected in ((BODY, ("reviewed", "complete")), (NOTES, ("reviewed", "partial"))):
    row = cov.get(seg)
    if not row or (row["disposition"], row["migration_status"]) != expected:
        raise SystemExit(f"coverage changed: {seg}: {row}")
if cov[NOTES]["source_line_ranges"] != "L492-499":
    raise SystemExit("notes coverage pre-state changed")

body_targets = [row for row in statements if row["segment_id"] == BODY
                and row.get("qualifiers", {}).get("footnote_marker") in (1, 2, 3, 4, 5, 6)]
if len(body_targets) != 6 or {row["qualifiers"]["footnote_marker"] for row in body_targets} != {1, 2, 3, 4, 5, 6}:
    raise SystemExit("p.278 footnote body links changed")
if any(not row["qualifiers"].get("footnote_text_pending") for row in body_targets):
    raise SystemExit("one or more p.278 footnotes are already resolved")

NEW_CANDIDATES = [
    ("cand-9296", "Pallucchini, 1933-4, pp.1491-1511 (citation locator; title unresolved)", "archive",
     "Citation in Haskell's p.278 note 2 for German court purchases of Italian late-Baroque works. Cited pages not independently consulted."),
    ("cand-9297", "Donzelli, p.82 (citation locator; title and edition unresolved)", "archive",
     "Citation in Haskell's p.278 note 3 for Gaspare Diziani's Dresden service; cited page not independently consulted."),
    ("cand-9298", "Powell, pp.68-70, 110, 147 (citation locator; title and edition unresolved)", "archive",
     "Citation in Haskell's p.278 note 4 about Amigoni's Nymphenburg works; cited pages not independently consulted."),
    ("cand-9299", "Duke of Manchester, vol. II (citation locator; work and edition unresolved)", "archive",
     "Cited by Haskell's p.278 notes 5-6 as 'II, passim' and 'ibid., p.140'; exact publication not identified or independently consulted."),
    ("cand-9300", "Unidentified Amigoni works at Nymphenburg (Haskell p.278)", "work",
     "Haskell's note dates the Amigonis at Nymphenburg from 1716. No individual title, medium, or structure is identified; do not equate the works with the pavilions."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
newc = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES}#L{501 if cid == 'cand-9296' else 502 if cid == 'cand-9297' else 503 if cid in ('cand-9298','cand-9300') else 504}",
} for cid, name, kind, detail in NEW_CANDIDATES]

first, last = 491, 634
offsets, offset = {}, 0
for line_no in range(first, last + 1):
    offsets[line_no] = offset
    offset += len(src[line_no - 1]) + 1
newm = []


def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p278notes-{local}"
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


add_mention("lavagnino-general", 500, "Lavagnino", "cand-7251", "Citation only; Chapter 7 is an internal cross-reference.")
add_mention("pallucchini", 501, "Pallucchini, 1933-4, PP1491-1511.", "cand-9296", "S0 OCR page string retained in the anchor; scan confirms pp.1491-1511.")
add_mention("donzelli", 502, "Donzelli, p. 82.", "cand-9297")
add_mention("amigoni-works", 503, "The Amigonis in Nymphenburg", "cand-9300", "S2 print reading; no individual work identified.")
add_mention("amigoni-person", 503, "Amigonis", "cand-8857")
add_mention("nymphenburg", 503, "Nymphenburg", "cand-8859")
add_mention("lavagnino-p121", 503, "Lavagnino", "cand-7251")
add_mention("powell", 503, "Powell, pp. 68-70, Iio and 147.", "cand-9298", "S0 OCR reads Iio; scan reads 110.")
add_mention("manchester-vol2", 504, "Duke of Manchester, II, passim.", "cand-9299", "Printed note 5; S0 OCR misnumbers its marker as 6.")
add_mention("manchester-p140", 505, "ibid., p. 140.", "cand-9299", "Printed note 6; S0 OCR misnumbers its marker as 8.")

statement_id = "st-chp10-notes-p278n4-amigoni-nymphenburg-date"
if statement_id in sids:
    raise SystemExit(f"duplicate statement ID: {statement_id}")
quote = "The Amigonis in Nymphenburg date from 1716"
if quote not in src[502]:
    raise SystemExit("note 4 statement quote is not anchored")
newstatement = {
    "statement_id": statement_id, "segment_id": NOTES,
    "subject_candidate_id": "cand-9300", "object_candidate_id": "",
    "predicate": "haskell_note_dates_amigoni_works_at_nymphenburg_from_1716",
    "qualifiers": {
        "source_line_start": 503, "source_line_end": 503, "printed_page": 278, "pdf_physical_page": 3,
        "claim": "Haskell's note dates the Amigoni works at Nymphenburg from 1716.",
        "speaker": "Haskell, footnote", "text_layer": "authorial note",
        "qualification": "The note identifies no individual work, medium, or pavilion. Lavagnino p.121 and Powell pp.68-70, 110, 147 are cited but were not independently consulted; S0 OCR reads 'Iio' where the scan shows '110'.",
        "mentioned_candidate_ids": ["cand-9300", "cand-8857", "cand-8859", "cand-7251", "cand-9298"],
        "footnote_number": 4, "related_body_statement_ids": [
            row["statement_id"] for row in body_targets if row["qualifiers"]["footnote_marker"] == 4
        ],
        "cited_material_not_independently_consulted": True, "relation_candidate": False,
    },
    "original_quote": quote, "origin": "book", "source_file": SOURCE_FILE,
}

for row in body_targets:
    marker = row["qualifiers"]["footnote_marker"]
    q = row["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES
    q["footnote_source_line"] = {1: 500, 2: 501, 3: 502, 4: 503, 5: 504, 6: 505}[marker]
    q["footnote_note_statement_ids"] = [statement_id] if marker == 4 else []
    if marker == 5:
        q["qualification"] = (q.get("qualification", "") + " Printed p.278 note marker is 5; S0 OCR misreads it as 6. The cited volume is not independently consulted.").strip()
    if marker == 6:
        q["qualification"] = (q.get("qualification", "") + " Printed p.278 note marker is 6; S0 OCR misreads it as 8. The cited volume is not independently consulted.").strip()

notes_cov = cov[NOTES]
notes_cov["source_line_ranges"] = "L492-505"
notes_cov["note"] = (notes_cov.get("note", "") +
    " Processed p.278 notes 1-6 at L500-L505: notes 1-3 and 5-6 are citation pointers; note 4 dates unidentified Amigoni works at Nymphenburg from 1716. Printed note markers 5 and 6 are OCRed as 6 and 8; source remains unchanged. L506 onward remains pending.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p278 notes 1-6 hashes verified; planned new candidates=5, mentions=10, statements=1")
print("printed note numbering and OCR marker mismatches recorded in S2; citation locators remain unverified")
print("Amigoni work group remains unidentified; no individual work or pavilion is inferred")
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
statements.append(newstatement)
write_csv(cp, cf, candidates)
write_csv(mp, mf, mentions)
write_jsonl(sp, statements)
write_csv(vp, vf, coverage)
print(f"applied; recovery copies use suffix {BACKUP}")
