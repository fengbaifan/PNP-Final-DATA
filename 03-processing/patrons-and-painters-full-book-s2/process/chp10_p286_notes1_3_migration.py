"""Controlled S2 migration for p.286 notes 1-3 at merged source L532-L534."""
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
NOTES_SEGMENT = "chp-10:10_CHP-10_intro:l491-634"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "33d2557d3e681434a9c964316a7a24fe2c00faa934add1381c12fc4d8a7c7f76"
EXPECTED_LINES_SHA = "7efb84cf8591c3d6cf3942060b588aeadea90348adb6e8856493ad567efdf55e"
BACKUP = ".bak-s2-chp10-p286-notes1-3-20261002"


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
if hashlib.sha256("\n".join(src[531:534]).encode("utf-8")).hexdigest() != EXPECTED_LINES_SHA:
    raise SystemExit("p.286 notes 1-3 changed")
if not src[531].startswith("1 Quoted by Ilaria Toesca") or not src[532].startswith("3 For these events see Vertue") or not src[533].startswith("3 Dictionary"):
    raise SystemExit("p.286 footnote markers or wording changed")

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
if maximum != 9344:
    raise SystemExit(f"candidate sequence changed: {maximum}")
notes_cov = cov.get(NOTES_SEGMENT)
if not notes_cov or (notes_cov["disposition"], notes_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("merged note coverage status changed")
if notes_cov["source_line_ranges"] != "L492-531":
    raise SystemExit(f"merged note coverage range changed: {notes_cov['source_line_ranges']}")

TARGETS = {
    "st-chp10-p286-galilei-national-taste": (1, 532),
    "st-chp10-p286-powis-house-decoration": (2, 533),
    "st-chp10-p286-powis-age": (3, 534),
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(TARGETS) <= by_sid.keys():
    raise SystemExit(f"p.286 body note targets missing: {set(TARGETS)-by_sid.keys()}")
for sid, (marker, source_line) in TARGETS.items():
    q = by_sid[sid].get("qualifiers", {})
    if q.get("footnote_marker") != marker or not q.get("footnote_text_pending"):
        raise SystemExit(f"p.286 marker {marker} state changed on {sid}")

REQUIRED = {"cand-7255", "cand-8933"}
if not REQUIRED <= cids:
    raise SystemExit(f"required existing candidates missing: {REQUIRED-cids}")
NEW_CANDIDATES = [
    ("cand-9345", "Ilaria Toesca (full name in p.286 note 1; possible identity with I. Toesca unresolved)", "person",
     "Haskell credits Ilaria Toesca as the intermediary source for Alessandro Galilei's quotation. A separate chapter-2 candidate records I. Toesca; possible identity is deferred to S3."),
    ("cand-9346", "Ilaria Toesca, 1952, p.208 (citation locator in p.286 note 1; work unresolved)", "archive",
     "Haskell cites Toesca, 1952, p.208 for the Galilei quotation. No title or further bibliographic data is given here, and the cited page was not consulted."),
    ("cand-9347", "Dictionary of National Biography (citation locator in p.286 note 3)", "archive",
     "Short-form bibliographic reference in Haskell's p.286 note 3. Edition/volume/page and cited content are not supplied or independently consulted."),
    ("cand-9348", "Wheatley (surname-only author in p.286 note 3; identity unresolved)", "person",
     "Haskell gives the surname Wheatley with volume and page only. No full identity is inferred before bibliography review and S3."),
    ("cand-9349", "Wheatley, vol. III, p.18 (citation locator in p.286 note 3; work unresolved)", "archive",
     "Short-form citation in Haskell's p.286 note 3. The title, edition and cited page content were not independently checked."),
]
new_ids = {row[0] for row in NEW_CANDIDATES}
if new_ids & cids:
    raise SystemExit("one or more planned candidate IDs already exist")
new_candidates = [{
    "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
    "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
    "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
    "candidate_source_ref": f"{NOTES_SEGMENT}#L{532 if cid in {'cand-9345','cand-9346'} else 534}",
} for cid, name, kind, detail in NEW_CANDIDATES]

new_mentions = []
notes_start = sum(len(src[n - 1]) + 1 for n in range(491, 532))


def add_mention(local, line_no, surface, candidate_id, note=""):
    mention_id = f"m-chp10-p286notes-{local}"
    if mention_id in mids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in cids | new_ids:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    line = src[line_no - 1]
    at = line.find(surface)
    if at < 0:
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = notes_start + sum(len(src[n - 1]) + 1 for n in range(532, line_no)) + at
    end = start + len(surface)
    if notes_body[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEGMENT, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention("n1-toesca-person", 532, "Ilaria Toesca", "cand-9345", "Full name stated; possible identity with chapter-2 I. Toesca candidate is deferred to S3.")
add_mention("n1-toesca-source", 532, "Ilaria Toesca, 1952, p. 208", "cand-9346", "Citation locator only; cited page and intermediary source were not consulted.")
add_mention("n2-vertue-person", 533, "Vertue", "cand-8933", "Author named in the citation; identity candidate reused, not re-resolved here.")
add_mention("n2-vertue-vol1", 533, "Vertue, I, p. 45", "cand-7255", "Citation locator in Vertue's Notebooks; cited page not consulted.")
add_mention("n2-vertue-vol3", 533, "III, pp. 45, 49, 51, 67", "cand-7255", "Second volume/pages locator continuing the Vertue, Notebooks citation; cited pages not consulted.")
add_mention("n3-dnb", 534, "Dictionary os National Biography", "cand-9347", "OCR reads 'os'; print reads 'of'. Citation locator only; content not consulted.")
add_mention("n3-wheatley-person", 534, "Wheatley", "cand-9348", "Surname-only author; identity unresolved.")
add_mention("n3-wheatley-source", 534, "Wheatley, III, p. 18", "cand-9349", "Citation locator only; cited page not consulted.")

if len(new_mentions) != 8:
    raise SystemExit("planned p.286 notes 1-3 mention count changed")

target_qualifications = {
    1: "P.286 note 1 credits Ilaria Toesca, 1952, p.208 as the intermediary source for Galilei's quotation. The page was not consulted; the separate I. Toesca candidate remains for S3 identity review.",
    2: "P.286 note 2 points to Vertue, Notebooks, vol.I p.45 and vol.III pp.45, 49, 51, 67 for these events; cited pages were not consulted.",
    3: "P.286 note 3 cites the Dictionary of National Biography and Wheatley, vol.III p.18 for context on Lord Powis. The cited material was not consulted and Wheatley's identity remains unresolved.",
}
for sid, (marker, source_line) in TARGETS.items():
    q = by_sid[sid]["qualifiers"]
    q["footnote_text_pending"] = False
    q["footnote_link_status"] = "resolved_source_migration"
    q["footnote_segment"] = NOTES_SEGMENT
    q["footnote_source_line"] = source_line
    q["footnote_note_statement_ids"] = []
    q["qualification"] = (q.get("qualification", "") + " " + target_qualifications[marker]).strip()
    q["cited_material_not_independently_consulted"] = True

notes_cov["source_line_ranges"] = "L492-534"
notes_cov["note"] = (notes_cov.get("note", "") +
    " P.286 notes 1-3 at L532-L534 are migrated. Note 1 cites Ilaria Toesca (1952, p.208) for the Galilei quotation; the possible identity with the existing I. Toesca candidate is deferred to S3. Note 2 cites Vertue, Notebooks, vols.I/III for Powis House events. Note 3 cites the Dictionary of National Biography and Wheatley, vol.III, p.18 for Lord Powis. No cited source was consulted; OCR 'os' in Dictionary of National Biography is corrected to print 'of' in S2 only. L535 onward remains pending.").strip()

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated changes")
args = parser.parse_args()
print("p286 notes L532-L534 verified against CHP-10.pdf physical page 15")
print("planned new candidates=5, mentions=8, statements=0; closes body footnote markers 1-3")
print("all cited pages remain unread; Ilaria Toesca / I. Toesca identity and Wheatley identity remain unresolved")
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
