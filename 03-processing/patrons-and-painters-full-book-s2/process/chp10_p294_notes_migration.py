"""Controlled S2 migration for p.294 notes 1-3; dry-run unless --apply."""
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
BODY_SEG = "chp-10:10_CHP-10_intro:l292-302"
EXPECTED_ASSET_SHA = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
EXPECTED_NOTES_SHA = "4a9adb883e279a906e8f84db9ed2cb29f44fd74d347943ca7bdd28e08fc60120"
BACKUP_SUFFIX = ".bak-s2-chp10-p294-notes-20261002"


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("source asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256("\n".join(source_lines[560:563]).encode("utf-8")).hexdigest() != EXPECTED_NOTES_SHA:
    raise SystemExit("p.294 note lines L561-L563 changed")
if not source_lines[560].startswith("1 Pellegrini’s drawing is reproduced"):
    raise SystemExit("p.294 note 1 anchor changed")
if not source_lines[561].startswith("2 Lavagnino, p. 115."):
    raise SystemExit("p.294 note 2 anchor changed")
if not source_lines[562].startswith("3 Bottari, V, pp. 27-8."):
    raise SystemExit("p.294 note 3 anchor changed")

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
if maximum != 9452:
    raise SystemExit(f"candidate sequence changed: {maximum}")
note_cov = cov.get(NOTES_SEG)
if not note_cov or (note_cov["disposition"], note_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes coverage changed")
if note_cov["source_line_ranges"] != "L492-560":
    raise SystemExit(f"consolidated notes range changed: {note_cov['source_line_ranges']}")
if cov.get(BODY_SEG, {}).get("migration_status") != "complete":
    raise SystemExit("p.294 body is not complete")

BODY_LINKS = {
    1: ["st-chp10-p294-pellegrini-church-pictures", "st-chp10-p294-ricci-ascension"],
    2: ["st-chp10-p294-zucchi-print-cabinet"],
    3: ["st-chp10-p294-benefial-third-version-given-away"],
}
by_sid = {row["statement_id"]: row for row in statements}
if not set(sum(BODY_LINKS.values(), [])) <= by_sid.keys():
    raise SystemExit("p.294 body footnote targets changed")
for marker, ids in BODY_LINKS.items():
    for sid in ids:
        qualifiers = by_sid[sid].get("qualifiers", {})
        if qualifiers.get("footnote_marker") != marker or not qualifiers.get("footnote_text_pending"):
            raise SystemExit(f"p.294 body footnote state changed: {sid}")

E = {"pellegrini": "cand-1868", "ricci": "cand-2154", "dresden": "cand-0947",
     "garas": "cand-9342", "lavagnino_work": "cand-7251", "bottari": "cand-0417"}
for key, cid in E.items():
    if cid not in cids:
        raise SystemExit(f"missing existing candidate {key}={cid}")

NEW_SPECS = [
    ("mostra_pellegrini_plate92", "Mostra di Pellegrini (1959), Plate 92 (citation locator)", "archive",
     "P.294 note 1 says Pellegrini's drawing is reproduced here. The catalogue plate was not consulted; the note's reference is retained as printed.", 561),
    ("posse_person", "H. Posse (author cited in p.294 note 1)", "person",
     "The local bibliography has H. Posse as author of the 1929 Dresden gallery catalogue; identity alignment is deferred to S3.", 561),
    ("posse_dresden_catalogue", "H. Posse, Die Staatliche Gemäldegalerie zu Dresden, first section (Dresden and Berlin, 1929; citation locator)", "archive",
     "Locally matched to the bibliography entry cited as Posse, 1929. The book and relevant pages were not independently consulted.", 561),
    ("garas_pellegrini_article", "Clara Garas, 'Giovanni Antonio Pellegrini in Deutschland' (Arte Veneta, 1971; citation locator)", "archive",
     "Locally matched to the bibliography entry cited as Garas, 1971; article and cited pages were not independently consulted. Surname-only candidate identity remains for S3.", 561),
    ("lavagnino_person", "E. Lavagnino (author cited in p.294 note 2)", "person",
     "The book bibliography identifies E. Lavagnino as author of Gli artisti italiani in Germania. Identity alignment is deferred to S3.", 562),
    ("bottari_v_locator", "Bottari, volume V, pages 27-28 (citation locator)", "archive",
     "P.294 note 3 short citation. The local bibliography identifies Bottari's Raccolta di lettere, Milano 1822; the cited volume/pages and edition were not checked.", 563),
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
    mention_id = f"m-chp10-p294-{local_id}"
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


add_mention("n1-pellegrini-drawing", 561, "Pellegrini’s", E["pellegrini"], "Existing index candidate reused.")
add_mention("n1-mostra", 561, "Mostra di Pellegrini, 1959, Plate 92", C["mostra_pellegrini_plate92"], "Citation locator; plate not consulted.")
add_mention("n1-pellegrini-work", 561, "Pellegrini’s", E["pellegrini"], "Second occurrence in the Dresden-work reference.", occurrence=1)
add_mention("n1-ricci-work", 561, "Ricci’s", E["ricci"], "Existing index candidate reused.")
add_mention("n1-dresden", 561, "Dresden", E["dresden"], "Existing place candidate reused.")
add_mention("n1-posse", 561, "Posse", C["posse_person"], "Author surname in the citation.")
add_mention("n1-posse-year", 561, "1929", C["posse_dresden_catalogue"], "Local bibliography match; cited work not independently consulted.")
add_mention("n1-garas", 561, "Garas", E["garas"], "Existing surname-only person candidate reused; identity remains for S3.")
add_mention("n1-garas-year", 561, "1971", C["garas_pellegrini_article"], "Local bibliography match; article not independently consulted.")
add_mention("n2-lavagnino", 562, "Lavagnino", C["lavagnino_person"], "Author as named in the note; full identity alignment deferred to S3.")
add_mention("n2-page", 562, "p. 115", E["lavagnino_work"], "Citation locator locally associated with the bibliography's 1943 work; page not consulted.")
add_mention("n3-bottari", 563, "Bottari", E["bottari"], "Existing index candidate reused.")
add_mention("n3-volume-locator", 563, "V, pp. 27-8", C["bottari_v_locator"], "Volume/page locator; cited text not consulted.")

new_statements = []
new_sids = set()


def add_statement(local_id, line_no, marker, obj, predicate, claim, qualification,
                  mentioned, citations):
    statement_id = f"st-chp10-p294-note{marker}-{local_id}"
    if statement_id in sids or statement_id in new_sids:
        raise SystemExit(f"duplicate statement: {statement_id}")
    qualifiers = {
        "source_line_start": line_no, "source_line_end": line_no,
        "printed_page": 294, "pdf_physical_page": 23,
        "claim": claim, "speaker": "Haskell, footnote",
        "text_layer": "bibliographic pointer",
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
        "relation_candidate": False,
        "footnote_marker": marker,
        "related_body_statement_ids": BODY_LINKS[marker],
        "citations": citations,
        "cited_material_not_independently_consulted": True,
    }
    row = {"statement_id": statement_id, "segment_id": NOTES_SEG,
           "subject_candidate_id": None, "object_candidate_id": obj,
           "predicate": predicate, "qualifiers": qualifiers,
           "original_quote": source_lines[line_no - 1], "origin": "book", "source_file": SOURCE_FILE}
    new_statements.append(row)
    new_sids.add(statement_id)
    return statement_id


S = {}
S[1] = add_statement(
    "pellegrini-dresden-citations", 561, 1, C["mostra_pellegrini_plate92"], "footnote_citations_for_pellegrini_and_ricci_in_dresden",
    "P.294 note 1 says a drawing by Pellegrini is reproduced in Mostra di Pellegrini (1959), Plate 92, and directs readers to Posse (1929) and Garas (1971) for Pellegrini and Ricci's work in Dresden and other gallery information.",
    "These are source pointers only. The catalogue plate, Posse volume and Garas article were not consulted; local bibliography matches remain provisional.",
    [E["pellegrini"], C["mostra_pellegrini_plate92"], E["ricci"], E["dresden"], C["posse_person"], C["posse_dresden_catalogue"], E["garas"], C["garas_pellegrini_article"]],
    [{"source_candidate_id": C["mostra_pellegrini_plate92"], "year": "1959", "plate": "92"},
     {"source_candidate_id": C["posse_dresden_catalogue"], "year": "1929", "bibliography_match": "local"},
     {"source_candidate_id": C["garas_pellegrini_article"], "year": "1971", "bibliography_match": "local"}],
)
S[2] = add_statement(
    "lavagnino-citation", 562, 2, E["lavagnino_work"], "footnote_citation",
    "P.294 note 2 cites Lavagnino, page 115, for Antonio Zucchi's Dresden print-cabinet employment.",
    "The book bibliography locally identifies E. Lavagnino's Gli artisti italiani in Germania (1943); volume and cited page were not independently checked.",
    [C["lavagnino_person"], E["lavagnino_work"]],
    [{"source_candidate_id": E["lavagnino_work"], "page": "115", "bibliography_match": "provisional"}],
)
S[3] = add_statement(
    "bottari-citation", 563, 3, C["bottari_v_locator"], "footnote_citation",
    "P.294 note 3 cites Bottari, volume V, pages 27-28, for the Benefial painting reported as arriving in Dresden and being given away.",
    "The local bibliography lists Bottari's Raccolta di lettere (Milano, 1822); the cited volume, pages and edition were not checked.",
    [E["bottari"], C["bottari_v_locator"]],
    [{"source_candidate_id": C["bottari_v_locator"], "volume": "V", "pages": "27-28", "bibliography_match": "local"}],
)

for marker, body_ids in BODY_LINKS.items():
    linked_note_ids = [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_marker"] == marker]
    for sid in body_ids:
        qualifiers = by_sid[sid]["qualifiers"]
        qualifiers["footnote_text_pending"] = False
        qualifiers["footnote_body_link_status"] = "linked"
        qualifiers["footnote_segment"] = NOTES_SEG
        qualifiers["footnote_source_line"] = {1: 561, 2: 562, 3: 563}[marker]
        qualifiers["footnote_note_statement_ids"] = linked_note_ids

for segment_id, rows in ((NOTES_SEG, new_mentions),):
    rows = sorted(rows, key=lambda row: (int(row["start_char"]), int(row["end_char"])))
    for left, right in zip(rows, rows[1:]):
        if int(right["start_char"]) < int(left["end_char"]):
            raise SystemExit(f"overlapping new mention anchors: {left['mention_id']} / {right['mention_id']}")
for row in new_statements:
    ids = cids | {item["candidate_id"] for item in new_candidates}
    if row["object_candidate_id"] and row["object_candidate_id"] not in ids:
        raise SystemExit(f"unknown statement object: {row['statement_id']}")
    for cid in row["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in ids:
            raise SystemExit(f"unknown statement mention candidate: {row['statement_id']} {cid}")
    for citation in row["qualifiers"]["citations"]:
        if citation["source_candidate_id"] not in ids:
            raise SystemExit(f"unknown citation candidate: {row['statement_id']}")

body_cov = cov[BODY_SEG]
pending = "The p.294 body is complete; notes 1-3 remain pending in the consolidated notes segment."
if pending not in body_cov.get("note", ""):
    raise SystemExit("p.294 body coverage note changed")
body_cov["note"] = body_cov["note"].replace(
    pending,
    "The p.294 body is complete; notes 1-3 at L561-L563 are migrated and linked to the corresponding body statements.",
)
if "L561 onward remains pending." not in note_cov.get("note", ""):
    raise SystemExit("consolidated-notes cursor changed")
note_cov["source_line_ranges"] = "L492-563"
note_cov["note"] = note_cov["note"].replace("L561 onward remains pending.", "L564 onward remains pending.")
note_cov["note"] += (
    " P.294 notes 1-3 at L561-L563 are migrated and linked to the body markers. "
    "The cited catalogue plate, Posse/Garas publications, Lavagnino page and Bottari volume/pages were not independently consulted; any bibliography matches are locators, not fact verification. "
    "The next line L564 begins p.295 notes and remains pending."
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the validated p.294 footnote migration")
args = parser.parse_args()
print(json.dumps({
    "mode": "APPLY" if args.apply else "DRY-RUN",
    "source_segments": [BODY_SEG, NOTES_SEG],
    "new_candidates": [row["candidate_id"] for row in new_candidates],
    "new_candidate_count": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "body_markers_linked": {str(marker): len(ids) for marker, ids in BODY_LINKS.items()},
    "coverage": {"notes_ranges": note_cov["source_line_ranges"], "next": "L564", "notes_status": note_cov["migration_status"]},
}, ensure_ascii=True, indent=2))
if not args.apply:
    raise SystemExit(0)

for path in (cp, mp, sp, vp):
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(cp, cf, candidates + new_candidates)
write_csv(mp, mf, mentions + new_mentions)
write_jsonl(sp, statements + new_statements)
write_csv(vp, vf, coverage)
print("Applied validated p.294 footnote migration; four table backups created.")
