"""Controlled migration of p.298 footnotes 1-3; dry-run unless --apply."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
BIB = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
BODY_SEG = "chp-10:10_CHP-10_intro:l345-352"
NOTES_SEG = "chp-10:10_CHP-10_intro:l491-634"
CH14_SEG = "chp-14:14_CHP-14_intro:l55-61"
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
NOTES_SHA = "067192b7d838f0518ea1b741f8ae378aa3bc52fc35076ba081c2336ead7c6fea"
BACKUP_SUFFIX = ".bak-s2-chp10-p298-notes-20261002"
EXPECTED_MAX_CANDIDATE = 9483


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


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the validated migration")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != ASSET_SHA:
    raise SystemExit("canonical source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
notes_text = "\n".join(source_lines[574:577])
if hashlib.sha256(notes_text.encode("utf-8")).hexdigest() != NOTES_SHA:
    raise SystemExit("p.298 composite-note lines L575-L577 changed")
if not source_lines[574].startswith("1 Mostra di Bernardo Bellotto, 1955."):
    raise SystemExit("p.298 note 1 changed")
if source_lines[575] != "2 Novelli.":
    raise SystemExit("p.298 note 2 changed")
if source_lines[576] != "3 See later. Chapter 14.":
    raise SystemExit("p.298 note 3 changed")

bib_text = BIB.read_text(encoding="utf-8-sig")
for fragment in (
    "Mostra di Bernardo Bellotto—opere provenienti dalla Polonia, Venezia 1955.",
    "Novelli, Pietro Antonio: Memorie della vita—per le auspicate nozze del Marchese Giovanni",
    "Padova 1834.",
):
    if fragment not in bib_text:
        raise SystemExit(f"local bibliography match changed: {fragment}")

cp, mp, sp, vp = [TABLES / name for name in (
    "entity-candidates.csv", "mentions.csv", "book-statements.jsonl", "s2-coverage.csv"
)]
cf, candidates = read_csv(cp)
mf, mentions = read_csv(mp)
vf, coverage = read_csv(vp)
statements = read_jsonl(sp)
cids = {row["candidate_id"] for row in candidates}
mids = {row["mention_id"] for row in mentions}
sids = {row["statement_id"] for row in statements}
cov = {row["segment_id"]: row for row in coverage}
by_cid = {row["candidate_id"]: row for row in candidates}
by_sid = {row["statement_id"]: row for row in statements}

maximum = max(int(row["candidate_id"].split("-")[-1]) for row in candidates if row["candidate_id"].startswith("cand-"))
if maximum != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: {maximum}")
expected_coverage = {
    BODY_SEG: ("reviewed", "complete", "L346-352"),
    NOTES_SEG: ("reviewed", "partial", "L492-574"),
    CH14_SEG: ("queued", "pending", ""),
}
for segment_id, expected in expected_coverage.items():
    row = cov.get(segment_id)
    actual = (row["disposition"], row["migration_status"], row["source_line_ranges"]) if row else None
    if actual != expected:
        raise SystemExit(f"coverage changed: {segment_id}: {actual}")

REUSED = {"bellotto_catalogue": "cand-9462", "novelli_memoirs": "cand-8363"}
if any(cid not in cids for cid in REUSED.values()):
    raise SystemExit("a reused citation candidate is missing")
if not by_cid[REUSED["bellotto_catalogue"]]["canonical_name"].startswith(
    "Mostra di Bernardo Bellotto—opere provenienti dalla Polonia"
):
    raise SystemExit("the Bellotto catalogue candidate no longer matches the local bibliography")
if not by_cid[REUSED["novelli_memoirs"]]["canonical_name"].startswith("Pietro Novelli's Memoirs"):
    raise SystemExit("the Novelli memoir candidate changed; review identity/source mapping")

BODY_LINKS = {
    1: ["st-chp10-p298-bellotto-warsaw-views"],
    2: ["st-chp10-p298-novelli-declined-russia-invitation"],
    3: ["st-chp10-p298-algarotti-acquired-banquet-for-augustus"],
}
for marker, target_ids in BODY_LINKS.items():
    for sid in target_ids:
        row = by_sid.get(sid)
        if not row or row.get("qualifiers", {}).get("footnote_marker") != marker:
            raise SystemExit(f"body target changed for footnote {marker}: {sid}")
        if not row["qualifiers"].get("footnote_text_pending"):
            raise SystemExit(f"body footnote was already resolved: {sid}")


def segment_text_and_offsets(start_line, end_line):
    text = "\n".join(source_lines[start_line - 1:end_line])
    offsets = {}
    offset = 0
    for line_no in range(start_line, end_line + 1):
        offsets[line_no] = offset
        offset += len(source_lines[line_no - 1]) + 1
    return text, offsets


note_segment_text, note_offsets = segment_text_and_offsets(491, 634)
new_mentions = []
new_statements = []
new_mids = set()
new_sids = set()


def add_mention(local_id, line_no, surface, candidate_id, note):
    mention_id = f"m-chp10-p298-{local_id}"
    if mention_id in mids or mention_id in new_mids:
        raise SystemExit(f"duplicate mention id: {mention_id}")
    if candidate_id not in cids:
        raise SystemExit(f"missing candidate for mention {mention_id}: {candidate_id}")
    start_in_line = source_lines[line_no - 1].find(surface)
    if start_in_line < 0 or source_lines[line_no - 1].find(surface, start_in_line + 1) >= 0:
        raise SystemExit(f"surface is absent or ambiguous at L{line_no}: {surface!r}")
    start = note_offsets[line_no] + start_in_line
    end = start + len(surface)
    if note_segment_text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {mention_id}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": NOTES_SEG, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    new_mids.add(mention_id)


add_mention("n1-bellotto-catalogue", 575, "Mostra di Bernardo Bellotto, 1955", REUSED["bellotto_catalogue"],
            "Bibliographic pointer reused from p.295 note 3; local catalogue entry matched, but catalogue and cited content unread.")
add_mention("n2-novelli-memoirs", 576, "Novelli", REUSED["novelli_memoirs"],
            "Surname-only short citation; the local Pietro Antonio Novelli memoir entry is a possible match, with no page supplied.")


def add_statement(local_id, line_no, marker, predicate, claim, obj=None, mentioned=(), text_layer="bibliographic pointer",
                  qualification="", citations=(), related_body_ids=(), cross_reference_segments=None):
    statement_id = f"st-chp10-p298-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement id: {statement_id}")
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 298, "pdf_physical_page": 27,
        "claim": claim, "speaker": "Haskell, footnote",
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": False, "footnote_marker": marker,
        "footnote_text_pending": False,
        "related_body_statement_ids": list(related_body_ids),
    }
    if citations:
        qualifiers["citations"] = list(citations)
        qualifiers["cited_material_not_independently_consulted"] = True
    if cross_reference_segments:
        qualifiers["cross_reference_segments"] = list(cross_reference_segments)
        qualifiers["cross_reference_content_read"] = False
    row = {
        "statement_id": statement_id, "segment_id": NOTES_SEG,
        "subject_candidate_id": None, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": source_lines[line_no - 1],
        "origin": "book", "source_file": SOURCE_FILE,
    }
    new_statements.append(row)
    new_sids.add(statement_id)
    return statement_id


add_statement(
    "note1-bellotto-catalogue-citation", 575, 1, "footnote_citation",
    "P.298 note 1 cites the 1955 Mostra di Bernardo Bellotto catalogue in connection with Haskell's account of Bellotto's Warsaw views.",
    obj=REUSED["bellotto_catalogue"], mentioned=[REUSED["bellotto_catalogue"]],
    qualification="Matched by title and year to the local bibliography and reused from p.295 note 3; the catalogue and cited content were not consulted.",
    citations=[{"source_candidate_id": REUSED["bellotto_catalogue"], "year": "1955",
                "title": "Mostra di Bernardo Bellotto—opere provenienti dalla Polonia", "place": "Venezia",
                "bibliography_match": "local"}],
    related_body_ids=BODY_LINKS[1],
)
add_statement(
    "note2-novelli-short-citation", 576, 2, "footnote_citation",
    "P.298 note 2 gives the surname-only citation 'Novelli.'; the local bibliography lists Pietro Antonio Novelli's 1834 Memorie della vita, which is a possible match.",
    obj=REUSED["novelli_memoirs"], mentioned=[REUSED["novelli_memoirs"]],
    qualification="The footnote supplies no title or page. The possible bibliography match is not confirmed by consulting the work.",
    citations=[{"source_candidate_id": REUSED["novelli_memoirs"], "year": "1834",
                "title": "Memorie della vita—per le auspicate nozze del Marchese Giovanni Selvatico colla contessa Laura Contarini",
                "place": "Padova", "bibliography_match": "possible_local"}],
    related_body_ids=BODY_LINKS[2],
)
add_statement(
    "note3-chapter14-cross-reference", 577, 3, "internal_chapter_cross_reference",
    "P.298 note 3 directs readers to the later discussion in Chapter 14 in connection with the preceding statement about Algarotti acquiring the painting for Augustus III.",
    text_layer="internal cross-reference",
    qualification="The referenced Chapter 14 segment is still queued and unread; this pointer does not independently support or verify the preceding claim.",
    related_body_ids=BODY_LINKS[3], cross_reference_segments=[CH14_SEG],
)

for row in new_statements:
    q = row["qualifiers"]
    if row["object_candidate_id"] and row["object_candidate_id"] not in cids:
        raise SystemExit(f"unknown object candidate: {row['statement_id']}")
    for cid in q["mentioned_candidate_ids"]:
        if cid not in cids:
            raise SystemExit(f"unknown mentioned candidate: {row['statement_id']} {cid}")
    for citation in q.get("citations", []):
        if citation["source_candidate_id"] not in cids:
            raise SystemExit(f"unknown citation candidate: {row['statement_id']}")
    for sid in q["related_body_statement_ids"]:
        if sid not in by_sid:
            raise SystemExit(f"unknown body statement: {row['statement_id']} {sid}")
    if not row["original_quote"]:
        raise SystemExit(f"empty source quote: {row['statement_id']}")

for row in mentions:
    if row["mention_id"] in {item["mention_id"] for item in new_mentions}:
        raise SystemExit(f"mention id already exists: {row['mention_id']}")
for item in new_mentions:
    if any(row["segment_id"] == item["segment_id"] and
           int(row["start_char"]) < int(item["end_char"]) and
           int(item["start_char"]) < int(row["end_char"]) for row in mentions):
        raise SystemExit(f"new mention overlaps an existing anchor: {item['mention_id']}")

for marker, target_ids in BODY_LINKS.items():
    for sid in target_ids:
        q = by_sid[sid]["qualifiers"]
        if q.get("footnote_marker") != marker or not q.get("footnote_text_pending"):
            raise SystemExit(f"body marker state changed: {sid}")
        q["footnote_text_pending"] = False
        if marker == 1:
            q["qualification"] = "The 1955 exhibition catalogue is cited as a source pointer only; it was not consulted. The source does not supply individual view titles."
        elif marker == 2:
            q["qualification"] = "The inviter and intended city are not named. Note 2 gives only the short citation 'Novelli.'; its precise page or intended passage is unspecified."
        else:
            q["qualification"] = "Note 3 is an internal pointer to Chapter 14. Its target segment is queued and unread, so it adds no independent evidence for the acquisition claim."

by_cov = cov[NOTES_SEG]
by_cov["source_line_ranges"] = "L492-577"
by_cov["note"] = (
    "Merged-note source processed in order through p.298 notes 1-3. Note 1 reuses the locally matched Bellotto "
    "exhibition catalogue candidate; note 2's surname-only Novelli pointer is a possible match to the local "
    "1834 memoir entry, with no page supplied; note 3 points to queued Chapter 14 content. Cited material was "
    "not independently consulted. Next source range: p.299 note 1 at L578."
)

new_mention_ids = {row["mention_id"] for row in new_mentions}
new_statement_ids = {row["statement_id"] for row in new_statements}
assert len(new_mention_ids) == 2 and len(new_statement_ids) == 3
assert all(row["segment_id"] == NOTES_SEG for row in new_mentions)

print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "reused_candidates": REUSED,
    "new_mentions": [row["mention_id"] for row in new_mentions],
    "new_statements": [row["statement_id"] for row in new_statements],
    "body_footnote_markers_resolved": [1, 2, 3],
    "notes_coverage": {"from": "L492-574", "to": "L492-577", "status": "partial"},
    "next_source_range": "p.299 note 1 (L578)",
}, ensure_ascii=False, indent=2))

if args.apply:
    paths = [mp, sp, vp]
    backups = [Path(str(path) + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("a migration backup already exists; inspect before applying")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    mentions.extend(new_mentions)
    statements.extend(new_statements)
    write_csv(mp, mf, mentions)
    write_jsonl(sp, statements)
    write_csv(vp, vf, coverage)
    print("applied; backups=" + ", ".join(path.name for path in backups))
