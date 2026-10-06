"""Controlled S2 migration for p.296 notes 1-3; dry-run unless --apply."""
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
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
BODY_SEGMENTS = (
    "chp-10:10_CHP-10_intro:l304-316",
    "chp-10:10_CHP-10_intro:l318-330",
)
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
NOTES_SHA = "c7b5277c5d3fd7dd01af6be308c8f82a9342384fd3802dd8ef25454017ae249b"
BACKUP_SUFFIX = ".bak-s2-chp10-p296-notes-20261002"


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
        temp_path = Path(stream.name)
    temp_path.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(stream.name)
    temp_path.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256("\n".join(source_lines[566:569]).encode("utf-8")).hexdigest() != NOTES_SHA:
    raise SystemExit("p.296 note lines L567-L569 changed")
if not source_lines[566].startswith("1 Von Freeden, 1956."):
    raise SystemExit("p.296 note 1 anchor changed")
if not source_lines[567].startswith("2 Levey, 1959, p. 192."):
    raise SystemExit("p.296 note 2 anchor changed")
if not source_lines[568].startswith("3 See Chapter 7;"):
    raise SystemExit("p.296 note 3 anchor changed")

cp, mp, sp, vp = [TABLES / name for name in ("entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv")]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
by_cid = {row["candidate_id"]: row for row in candidates}
maximum = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if maximum != 9464:
    raise SystemExit(f"candidate sequence changed: {maximum}")
note_cov = cov.get(NOTES_SEG)
if not note_cov or (note_cov["disposition"], note_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes coverage changed")
if note_cov["source_line_ranges"] != "L492-566":
    raise SystemExit(f"consolidated notes range changed: {note_cov['source_line_ranges']}")
for segment_id in BODY_SEGMENTS:
    if cov.get(segment_id, {}).get("migration_status") != "complete":
        raise SystemExit(f"p.296 body segment is not complete: {segment_id}")

BODY_LINKS = {
    1: ["st-chp10-p296-german-patronage-residenz-1750"],
    2: ["st-chp10-p296-tiepolo-scene-venice-quote"],
    3: ["st-chp10-p296-turin-rise"],
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(sum(BODY_LINKS.values(), [])) <= by_sid.keys():
    raise SystemExit("p.296 body footnote targets changed")
for marker, ids in BODY_LINKS.items():
    for sid in ids:
        qualifiers = by_sid[sid].get("qualifiers", {})
        if qualifiers.get("footnote_marker") != marker or not qualifiers.get("footnote_text_pending"):
            raise SystemExit(f"p.296 body footnote state changed: {sid}")

E = {
    "levey_person": "cand-9442",
    "levey_book": "cand-8436",
    "claretta_person": "cand-3508",
    "claretta_article": "cand-4995",
    "griseri_person": "cand-7142",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")
if by_cid[E["levey_book"]]["canonical_name"] != "Levey, 1959, relevant chapter (citation locator)":
    raise SystemExit("Levey 1959 candidate changed")
by_cid[E["levey_book"]]["canonical_name"] = "Michael Levey, Painting in 18th century Venice (London, 1959; citation locator)"
by_cid[E["levey_book"]]["detail"] = (
    "Short-form citation in p.296 note 2, page 192; matched by year and author to the local bibliography entry. "
    "The cited page and book were not independently consulted."
)

NEW_SPECS = [
    ("von_freeden_person", "Von Freeden (author cited in p.296 note 1; identity unresolved)", "person",
     "The note supplies only the surname and year 1956. Do not merge with the p.293 Von Freeden 1955 candidate before S3.", 567),
    ("von_freeden_1956", "Von Freeden, 1956 (p.296 note 1 citation locator; title/page unspecified)", "archive",
     "Short-form reference in p.296 note 1 for the Würzburg Residenz account. No matching title/page has been established from the local bibliography; work not consulted.", 567),
    ("griseri_palazzo_reale_1957", "A. Griseri, ‘The Palazzo Reale at Turin’ (Connoisseur, 1957, vol.140, pp.145-150; citation locator)", "archive",
     "Matched to the local bibliography entry. The article and cited pages were not independently consulted.", 569),
]
new_candidates = []
C = {}
for index, (key, name, kind, detail, line_no) in enumerate(NEW_SPECS, maximum + 1):
    cid = f"cand-{index:04d}"
    if cid in cids:
        raise SystemExit(f"candidate id already exists: {cid}")
    C[key] = cid
    new_candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES_SEG}#L{line_no}",
    })

SEGMENT_START, SEGMENT_END = 491, 634
segment_text = "\n".join(source_lines[SEGMENT_START - 1:SEGMENT_END])
segment_offsets, offset = {}, 0
for line_no in range(SEGMENT_START, SEGMENT_END + 1):
    segment_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

new_mentions = []
new_mids = set()


def add_mention(local_id, line_no, surface, candidate_id, note="", occurrence=0):
    mention_id = f"m-chp10-p296-{local_id}"
    if mention_id in mids or mention_id in new_mids:
        raise SystemExit(f"duplicate mention: {mention_id}")
    if candidate_id not in cids | {row["candidate_id"] for row in new_candidates}:
        raise SystemExit(f"missing candidate for {mention_id}: {candidate_id}")
    source_line = source_lines[line_no - 1]
    positions, start_at = [], 0
    while True:
        found = source_line.find(surface, start_at)
        if found < 0:
            break
        positions.append(found)
        start_at = found + max(1, len(surface))
    if occurrence >= len(positions):
        raise SystemExit(f"surface absent at L{line_no}: {surface!r}")
    start = segment_offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({"mention_id": mention_id, "segment_id": NOTES_SEG, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})
    new_mids.add(mention_id)


add_mention("n1-von-freeden-author", 567, "Von Freeden", C["von_freeden_person"], "Surname-only author candidate; identity deferred to S3.")
add_mention("n1-von-freeden-work", 567, "1956", C["von_freeden_1956"], "Citation locator only; title/page unresolved.")
add_mention("n2-levey-author", 568, "Levey", E["levey_person"], "Existing Levey author candidate reused; global identity remains for S3.")
add_mention("n2-levey-work", 568, "1959, p. 192", E["levey_book"], "Local bibliography identifies Painting in 18th century Venice (1959); p.192 was not consulted.")
add_mention("n3-claretta-author", 569, "Claretta", E["claretta_person"], "Existing surname-only author candidate reused; identity is not expanded here.")
add_mention("n3-claretta-work", 569, "1893, pp. 1-309", E["claretta_article"], "Citation locator matches the local bibliography's 1893 article; cited text unread.")
add_mention("n3-griseri-author", 569, "Griseri", E["griseri_person"], "Existing A. Griseri author candidate reused.")
add_mention("n3-griseri-work", 569, "1957, pp. 145-50", C["griseri_palazzo_reale_1957"], "Citation locator matched to local bibliography; article unread.")

new_statements = []
new_sids = set()


def add_statement(local_id, line_no, marker, obj, claim, mentioned, citations):
    statement_id = f"st-chp10-p296-note{marker}-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement: {statement_id}")
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 296, "pdf_physical_page": 25,
        "claim": claim, "speaker": "Haskell, footnote",
        "text_layer": "bibliographic pointer",
        "qualification": "Citation locator only; the cited publication or pages were not independently consulted.",
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": False,
        "footnote_marker": marker,
        "related_body_statement_ids": BODY_LINKS[marker],
        "citations": citations,
        "cited_material_not_independently_consulted": True,
    }
    row = {"statement_id": statement_id, "segment_id": NOTES_SEG,
           "subject_candidate_id": None, "object_candidate_id": obj,
           "predicate": "footnote_citation", "qualifiers": qualifiers,
           "original_quote": source_lines[line_no - 1], "origin": "book", "source_file": SOURCE_FILE}
    new_statements.append(row)
    new_sids.add(statement_id)
    return statement_id


S = {}
S[1] = add_statement(
    "residenz-citation", 567, 1, C["von_freeden_1956"],
    "P.296 note 1 cites Von Freeden (1956) for the account of Tiepolo's Würzburg Residenz commission.",
    [C["von_freeden_person"], C["von_freeden_1956"]],
    [{"source_candidate_id": C["von_freeden_1956"], "year": "1956", "bibliography_match": "unresolved"}],
)
S[2] = add_statement(
    "tiepolo-venice-quote-citation", 568, 2, E["levey_book"],
    "P.296 note 2 cites Levey (1959), page 192, for Haskell's account of Tiepolo placing the Würzburg scene in sixteenth-century Venice.",
    [E["levey_person"], E["levey_book"]],
    [{"source_candidate_id": E["levey_book"], "year": "1959", "page": "192", "bibliography_match": "local"}],
)
S[3] = add_statement(
    "turin-rise-citations", 569, 3, E["claretta_article"],
    "P.296 note 3 directs readers to Chapter 7 and cites Claretta (1893), pages 1-309, and A. Griseri's 1957 article, pages 145-150, for the Turin discussion.",
    [E["claretta_person"], E["claretta_article"], E["griseri_person"], C["griseri_palazzo_reale_1957"]],
    [{"source_candidate_id": E["claretta_article"], "year": "1893", "pages": "1-309", "bibliography_match": "local"},
     {"source_candidate_id": C["griseri_palazzo_reale_1957"], "year": "1957", "pages": "145-150", "bibliography_match": "local"}],
)

for row in new_statements:
    ids = cids | {item["candidate_id"] for item in new_candidates}
    for cid in row["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in ids:
            raise SystemExit(f"unknown statement mention candidate: {row['statement_id']} {cid}")
    if row["object_candidate_id"] not in ids:
        raise SystemExit(f"unknown statement object: {row['statement_id']}")
    for citation in row["qualifiers"]["citations"]:
        if citation["source_candidate_id"] not in ids:
            raise SystemExit(f"unknown citation candidate: {row['statement_id']}")

for marker, body_ids in BODY_LINKS.items():
    linked_note_ids = [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_marker"] == marker]
    for sid in body_ids:
        qualifiers = by_sid[sid]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_segment"] = NOTES_SEG
        qualifiers["footnote_source_line"] = {1: 567, 2: 568, 3: 569}[marker]
        qualifiers["footnote_note_statement_ids"] = linked_note_ids

sorted_rows = sorted(new_mentions, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
for left, right in zip(sorted_rows, sorted_rows[1:]):
    if int(right["start_char"]) < int(left["end_char"]):
        raise SystemExit(f"overlapping new mention anchors: {left['mention_id']} / {right['mention_id']}")

note_cov["source_line_ranges"] = "L492-569"
note_cov["note"] = (
    "Merged-note source has been processed in order through p.296 printed notes 1-3 at L567-L569. "
    "All three printed footnote markers are linked to their body statements. The Levey, Claretta, and Griseri references "
    "match the local bibliography; Von Freeden 1956 remains an unresolved short-form citation. No cited pages were independently consulted. "
    "See process/stages.md for per-note decisions. Next source range: p.297 notes at L570-L574."
)
cov[BODY_SEGMENTS[0]]["note"] = (
    "Printed p.295 body and its notes 1-5 are complete. The p.296 Residenz claim's marker 1 is linked to note L567; "
    "continuation and remaining p.296 footnotes are recorded in adjacent coverage."
)
cov[BODY_SEGMENTS[1]]["note"] = (
    "Printed p.296 body is complete after p.297 closes the Juvarra/Ricci sentence. P.296 notes 2-3 at L568-L569 are migrated and linked. "
    "P.297 note 1 at L570 remains pending in the consolidated note segment."
)

if len(new_candidates) != 3 or len(new_mentions) != 8 or len(new_statements) != 3:
    raise SystemExit(f"unexpected migration size: candidates={len(new_candidates)}, mentions={len(new_mentions)}, statements={len(new_statements)}")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the validated p.296 note migration")
args = parser.parse_args()
if not args.apply:
    print("DRY RUN OK: p.296 notes 1-3; 3 candidates, 8 mentions, 3 statements; three marker groups will be linked.")
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        if hashlib.sha256(backup.read_bytes()).digest() != hashlib.sha256(path.read_bytes()).digest():
            raise SystemExit(f"existing backup is not the current pre-apply state: {backup.name}")
    else:
        shutil.copy2(path, backup)

write_csv(cp, cf, candidates + new_candidates)
write_csv(mp, mf, mentions + new_mentions)
write_jsonl(sp, statements + new_statements)
write_csv(vp, vf, coverage)
print("APPLIED: p.296 notes 1-3; backups saved for candidates, mentions, statements, and coverage.")
