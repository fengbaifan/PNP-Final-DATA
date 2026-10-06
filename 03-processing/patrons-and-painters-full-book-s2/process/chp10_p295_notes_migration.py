"""Controlled S2 migration for p.295 notes 1-5; dry-run unless --apply."""
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
    "chp-10:10_CHP-10_intro:l292-302",
    "chp-10:10_CHP-10_intro:l304-316",
)
ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
NOTES_SHA = "ffa89cedf7567bc9ed68e48c488a751a696089a756424d0de701dbd18eb29bba"
BACKUP_SUFFIX = ".bak-s2-chp10-p295-notes-20261002"


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
if hashlib.sha256("\n".join(source_lines[563:566]).encode("utf-8")).hexdigest() != NOTES_SHA:
    raise SystemExit("p.295 note lines L564-L566 changed")
if not source_lines[563].startswith("1 Chapter 14. See also L. Ferrari"):
    raise SystemExit("p.295 note 1 anchor changed")
if not source_lines[564].startswith("3 See catalogue of Mostra di Bernardo Bellotto"):
    raise SystemExit("p.295 note 3 anchor changed")
if not source_lines[565].startswith("6 For a summary of Clemens August"):
    raise SystemExit("p.295 note 5 OCR anchor changed")

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
if maximum != 9458:
    raise SystemExit(f"candidate sequence changed: {maximum}")
note_cov = cov.get(NOTES_SEG)
if not note_cov or (note_cov["disposition"], note_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes coverage changed")
if note_cov["source_line_ranges"] != "L492-563":
    raise SystemExit(f"consolidated notes range changed: {note_cov['source_line_ranges']}")
for segment_id in BODY_SEGMENTS:
    if cov.get(segment_id, {}).get("migration_status") != "complete":
        raise SystemExit(f"p.295 body segment is not complete: {segment_id}")

BODY_LINKS = {
    1: [
        "st-chp10-p295-algarotti-commission-tiepolo",
        "st-chp10-p295-algarotti-commission-piazzetta",
        "st-chp10-p295-algarotti-commission-amigoni",
        "st-chp10-p295-algarotti-commission-pittoni",
        "st-chp10-p295-algarotti-commission-zuccarelli",
    ],
    2: ["st-chp10-p295-sartori-dresden-work"],
    3: ["st-chp10-p295-bellotto-arrival-and-court-post", "st-chp10-p295-bellotto-court-service"],
    4: ["st-chp10-p295-bellotto-return-1765", "st-chp10-p295-cross-church-painting"],
    5: ["st-chp10-p295-clemens-venice-visits"],
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(sum(BODY_LINKS.values(), [])) <= by_sid.keys():
    raise SystemExit("p.295 body footnote targets changed")
for marker, ids in BODY_LINKS.items():
    for sid in ids:
        qualifiers = by_sid[sid].get("qualifiers", {})
        if qualifiers.get("footnote_marker") != marker or not qualifiers.get("footnote_text_pending"):
            raise SystemExit(f"p.295 body footnote state changed: {sid}")

E = {
    "malamani": "cand-9433",
    "posse_person": "cand-9454",
    "posse_work": "cand-9455",
    "levey": "cand-9442",
    "clemens": "cand-0788",
    "rotari": "cand-2288",
    "dresden": "cand-0947",
    "verona": "cand-8681",
}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("luigi_ferrari_person", "Luigi Ferrari (bibliographic author cited at p.295 note 1)", "person",
     "The local bibliography expands L. Ferrari to Luigi Ferrari for the 1900 article; person identity alignment remains for S3.", 564),
    ("ferrari_algarotti_article", "Luigi Ferrari, ‘Gli acquisti dell’Algarotti pel Regio Museo di Dresda’ (L’Arte, 1900, pp.150-154; citation locator)", "archive",
     "Matched to the local bibliography entry. P.295 note 1 points to pp.150-154; article and cited pages were not independently consulted.", 564),
    ("malamani_1899_p77", "Malamani, ‘Rosalba Carriera’ (1899), p.77 (citation locator)", "archive",
     "Locally matched to the bibliography entry ‘Rosalba Carriera’, 1899, pp.27-149. The cited page and article were not independently consulted; align with other Malamani locators at S3.", 564),
    ("mostra_bellotto_1955", "Mostra di Bernardo Bellotto—opere provenienti dalla Polonia (Venezia, 1955; citation locator)", "archive",
     "Matched by title and year to the local bibliography. Catalogue and cited content were not independently consulted.", 565),
    ("levey_nymphenburg_1957", "Michael Levey, ‘The modello for Tiepolo’s altarpiece at Nymphenburg’ (Burlington Magazine, 1957, pp.256-261; citation locator)", "archive",
     "Matched to the local bibliography entry cited in p.295 note 5. The article and cited pages were not independently consulted; author identity remains for S3.", 566),
    ("clemens_catalogue_1961", "Clemens August, Kurfürst—Ausstellung in Schloss Augustusburg zu Brühl (Köln, 1961; citation locator)", "archive",
     "The p.295 OCR reads ‘Kutfurst Clemens August, Koln 1961’; the print and local bibliography identify the exhibition catalogue. It was not independently consulted.", 566),
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
    mention_id = f"m-chp10-p295-{local_id}"
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


add_mention("n1-ferrari-author", 564, "L. Ferrari", C["luigi_ferrari_person"], "Author expanded only from the local bibliography.")
add_mention("n1-ferrari-work", 564, "1900, pp. 150-4", C["ferrari_algarotti_article"], "Citation locator; article and pages unread.")
add_mention("n2-malamani-author", 564, "Malamani", E["malamani"], "Same surname candidate as p.291; no identity merge beyond reuse of this existing citation author.")
add_mention("n2-malamani-work", 564, "1899, p. 77", C["malamani_1899_p77"], "Citation locator; local bibliography match only.")
add_mention("n3-bellotto-catalogue", 565, "Mostra di Bernardo Bellotto, 1955", C["mostra_bellotto_1955"], "Citation locator; catalogue unread.")
add_mention("n3-rotari", 565, "Pietro Rotari", E["rotari"], "Reuse the index candidate spanning p.295 note and p.297 body.")
add_mention("n3-dresden", 565, "Dresden", E["dresden"], "Existing place candidate reused.")
add_mention("n3-verona", 565, "Verona", E["verona"], "Existing place candidate reused.")
add_mention("n4-posse-author", 565, "Posse", E["posse_person"], "Existing author candidate reused.")
add_mention("n4-posse-work", 565, "1929, p. 300", E["posse_work"], "Same local bibliography work as p.294 note 1; cited page unread.")
add_mention("n5-clemens", 566, "Clemens August", E["clemens"], "Existing index candidate reused.")
add_mention("n5-levey-author", 566, "Levey", E["levey"], "Existing surname author candidate reused; S3 retains global identity decision.")
add_mention("n5-levey-work", 566, "Burlington Magazine, 1957, PP256-61", C["levey_nymphenburg_1957"], "Citation locator matched to local bibliography; article unread.")
add_mention("n5-catalogue-work", 566, "Koln 1961", C["clemens_catalogue_1961"], "OCR spelling; print reads Köln and title begins Kurfürst Clemens August.")

new_statements = []
new_sids = set()


def add_statement(local_id, line_no, marker, obj, predicate, claim, qualification, mentioned, citations,
                  *, subject=None, relation_candidate=False, text_layer="bibliographic pointer"):
    statement_id = f"st-chp10-p295-note{marker}-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement: {statement_id}")
    body_ids = BODY_LINKS[marker]
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 295, "pdf_physical_page": 24,
        "claim": claim, "speaker": "Haskell, footnote",
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": relation_candidate,
        "footnote_marker": marker,
        "related_body_statement_ids": body_ids,
        "citations": citations,
        "cited_material_not_independently_consulted": True,
    }
    row = {"statement_id": statement_id, "segment_id": NOTES_SEG,
           "subject_candidate_id": subject, "object_candidate_id": obj,
           "predicate": predicate, "qualifiers": qualifiers,
           "original_quote": source_lines[line_no - 1], "origin": "book", "source_file": SOURCE_FILE}
    new_statements.append(row)
    new_sids.add(statement_id)
    return statement_id


S = {}
S[1] = add_statement(
    "algarotti-commission-citations", 564, 1, C["ferrari_algarotti_article"], "footnote_citation",
    "P.295 note 1 directs the reader to Chapter 14 and cites Luigi Ferrari's 1900 article, pages 150-154, for the preceding statement about Algarotti's commissions.",
    "The chapter reference is internal. The Ferrari article is locally matched to the bibliography; neither article nor cited pages were independently consulted.",
    [C["luigi_ferrari_person"], C["ferrari_algarotti_article"]],
    [{"source_candidate_id": C["ferrari_algarotti_article"], "year": "1900", "pages": "150-154", "bibliography_match": "local"}],
)
S[2] = add_statement(
    "sartori-dresden-citation", 564, 2, C["malamani_1899_p77"], "footnote_citation",
    "P.295 note 2 cites Malamani (1899), page 77, for the statement that Felicita Sartori came to Dresden in 1741 and worked extensively for Augustus III.",
    "The source is locally matched to the bibliography's 1899 Rosalba Carriera article; the cited page and article were not independently consulted.",
    [E["malamani"], C["malamani_1899_p77"]],
    [{"source_candidate_id": C["malamani_1899_p77"], "year": "1899", "page": "77", "bibliography_match": "local"}],
)
S[3] = add_statement(
    "bellotto-catalogue-citation", 565, 3, C["mostra_bellotto_1955"], "footnote_citation",
    "P.295 note 3 cites the 1955 Mostra di Bernardo Bellotto catalogue in connection with the preceding Bellotto account.",
    "The catalogue is matched by title and year to the local bibliography; it was not consulted.",
    [C["mostra_bellotto_1955"]],
    [{"source_candidate_id": C["mostra_bellotto_1955"], "year": "1955", "bibliography_match": "local"}],
)
S[4] = add_statement(
    "rotari-dresden-departure", 565, 3, E["dresden"], "reported_dresden_activity_and_departure",
    "Haskell's p.295 note 3 describes Pietro Rotari as another Venetian artist working at Dresden who left 'at this time', and says he had arrived in 1750.",
    "The phrase 'at this time' is left unresolved. P.297 separately reports Rotari's move to St Petersburg by 1756; the timeline is not reconciled here. The note's Bellotto catalogue citation was not consulted.",
    [E["rotari"], E["dresden"], E["verona"]],
    [{"source_candidate_id": C["mostra_bellotto_1955"], "year": "1955", "bibliography_match": "local"}],
    subject=E["rotari"], relation_candidate=True, text_layer="source-reported biographical detail",
)
S[5] = add_statement(
    "bellotto-dresden-citation", 565, 4, E["posse_work"], "footnote_citation",
    "P.295 note 4 cites Posse (1929), page 300, for the p.295 account of Bellotto's Dresden work.",
    "The publication matches the local bibliography and p.294 note 1 candidate; page 300 and the work were not independently consulted.",
    [E["posse_person"], E["posse_work"]],
    [{"source_candidate_id": E["posse_work"], "year": "1929", "page": "300", "bibliography_match": "local"}],
)
S[6] = add_statement(
    "clemens-patronage-citations", 566, 5, C["clemens_catalogue_1961"], "footnote_citations",
    "P.295 note 5 recommends Michael Levey's 1957 Burlington Magazine article, pages 256-261, and the 1961 Clemens August exhibition catalogue as summaries of Clemens August's patronage of Venetian artists.",
    "Both references match local bibliography entries. The print reads note 5, Kurfürst, Köln, and pp.256-261; S0 OCR reads note 6, Kutfurst, Koln, and PP256-61. Neither cited work was independently consulted.",
    [E["clemens"], E["levey"], C["levey_nymphenburg_1957"], C["clemens_catalogue_1961"]],
    [{"source_candidate_id": C["levey_nymphenburg_1957"], "year": "1957", "pages": "256-261", "bibliography_match": "local"},
     {"source_candidate_id": C["clemens_catalogue_1961"], "year": "1961", "bibliography_match": "local"}],
)

all_new_candidate_ids = {row["candidate_id"] for row in new_candidates}
all_ids = cids | all_new_candidate_ids
for row in new_statements:
    for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
        if cid is not None and cid not in all_ids:
            raise SystemExit(f"unknown statement endpoint: {row['statement_id']} {cid}")
    for cid in row["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in all_ids:
            raise SystemExit(f"unknown statement mention candidate: {row['statement_id']} {cid}")
    for citation in row["qualifiers"]["citations"]:
        if citation["source_candidate_id"] not in all_ids:
            raise SystemExit(f"unknown citation candidate: {row['statement_id']}")

for marker, body_ids in BODY_LINKS.items():
    linked_note_ids = [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_marker"] == marker]
    for sid in body_ids:
        qualifiers = by_sid[sid]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_segment"] = NOTES_SEG
        qualifiers["footnote_source_line"] = {1: 564, 2: 564, 3: 565, 4: 565, 5: 566}[marker]
        qualifiers["footnote_note_statement_ids"] = linked_note_ids

for segment_id, new_rows in ((NOTES_SEG, new_mentions),):
    sorted_rows = sorted(new_rows, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
    for left, right in zip(sorted_rows, sorted_rows[1:]):
        if int(right["start_char"]) < int(left["end_char"]):
            raise SystemExit(f"overlapping new mention anchors: {left['mention_id']} / {right['mention_id']}")

note_cov["source_line_ranges"] = "L492-566"
note_cov["note"] = (
    "Merged-note source has been processed in order through p.295 printed notes 1-5 at L564-L566. "
    "All five printed footnote markers are linked to their body statements. The scan corrects OCR note 6 to print note 5, "
    "Kutfurst to Kurfürst, Koln to Köln, and PP256-61 to pp.256-261; corrections are recorded in S2 only. "
    "Cited works were not independently consulted. See process/stages.md for the per-note decisions. Next source range: p.296 notes at L567-L569."
)
cov[BODY_SEGMENTS[0]]["note"] += " The p.295 marker 1 footnote at L564 is now migrated and linked."
cov[BODY_SEGMENTS[1]]["note"] = (
    "Printed p.295 body is complete after p.296 closes the final sentence. Notes 1-5 at L564-L566 are migrated "
    "and linked; citation sources remain locators unless explicitly described in the process record."
)

if len(new_candidates) != 6 or len(new_mentions) != 14 or len(new_statements) != 6:
    raise SystemExit(f"unexpected migration size: candidates={len(new_candidates)}, mentions={len(new_mentions)}, statements={len(new_statements)}")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the validated p.295 note migration")
args = parser.parse_args()
if not args.apply:
    print("DRY RUN OK: p.295 notes 1-5; 6 candidates, 14 mentions, 6 statements; five marker groups will be linked.")
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
print("APPLIED: p.295 notes 1-5; backups saved for candidates, mentions, statements, and coverage.")
