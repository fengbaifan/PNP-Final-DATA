"""Controlled S2 migration for the p.335 notes and their body links."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
NOTE_SEGMENT = "chp-13:13_CHP-13_intro:l179-251"
BODY_SEGMENT = "chp-13:13_CHP-13_intro:l32-39"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p335-notes-20261003"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the reviewed notes migration")
args = parser.parse_args()


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
note_text = "\n".join(source_lines[178:251])
body_text = "\n".join(source_lines[31:39])

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
segments = read_jsonl(segment_path)
state = (len(candidates), len(mentions), len(statements), len(coverage))
if state != (10132, 21900, 9793, 830):
    raise SystemExit(f"unexpected pre-state {state}")
candidate_by_id = {row["candidate_id"]: row for row in candidates}
if max(int(row["candidate_id"].split("-")[1]) for row in candidates) != 10145:
    raise SystemExit("candidate sequence changed")
if not {"cand-0025", "cand-1907", "cand-1948", "cand-2111", "cand-2188", "cand-2662", "cand-8514", "cand-9988", "cand-9991", "cand-9993", "cand-9996", "cand-10129"}.issubset(candidate_by_id):
    raise SystemExit("required existing candidates missing")
segment_by_id = {row["segment_id"]: row for row in segments}
for segment_id in [NOTE_SEGMENT, BODY_SEGMENT]:
    row = segment_by_id.get(segment_id)
    if not row:
        raise SystemExit(f"source segment missing: {segment_id}")
    lines = source_lines[row["line_start"] - 1:row["line_end"]]
    exact = "\n".join(lines)
    if hashlib.sha256(exact.encode("utf-8")).hexdigest() != row["sha256"]:
        raise SystemExit(f"segment hash mismatch: {segment_id}")
coverage_by_id = {row["segment_id"]: row for row in coverage}
if coverage_by_id[BODY_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("p.335 body is not in partial state")
if coverage_by_id[NOTE_SEGMENT]["migration_status"] != "partial":
    raise SystemExit("composite note segment is not in partial state")

candidate_specs = [
    ("Augustine, Saint (named in the p.335 proposed-edition notice)", "person", "Saint Augustine is named as the subject of a proposed edition; identity is left for S3 alignment.", 192),
    ("Proposed edition of Saint Augustine's works advertised in the Novelle, 19 March 1730", "archive", "The footnote identifies an advertisement for a proposed edition, not evidence that the edition appeared.", 192),
    ("Antonio da Venezia (author form in the p.335 devotional-book title)", "person", "Named as Padre Antonio da Venezia in the cited title; no identity expansion is made at S2.", 193),
    ("Religion trampling on Heresy (Piazzetta drawing for the devotional book)", "work", "Image named in p.335 note 2 as drawn by Piazzetta and engraved by Pitteri; edition-level identity awaits alignment.", 193),
    ("Gallo, 1948, p.176, note 4 (citation locator)", "archive", "Short citation in p.335 note 2; title, edition, and cited passage were not independently consulted.", 193),
    ("England (former location in the p.335 drawings provenance note)", "place", "Country named only as an earlier location of the Piazzetta drawings; timing and transfer route are unspecified.", 194),
    ("Royal Library, Turin (repository named in the p.335 drawings provenance note)", "institution", "Repository as named by Haskell; exact institutional identity is left for S3 alignment.", 194),
]
new_candidates = []
for number, (name, kind, detail, line) in enumerate(candidate_specs, 10146):
    candidate_id = f"cand-{number}"
    if candidate_id in candidate_by_id or any(row["canonical_name"] == name for row in candidates):
        raise SystemExit(f"candidate collision: {candidate_id} / {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTE_SEGMENT}#L{line}",
    })
    new_candidates.append(row)

CID = {
    "augustine": "cand-10146", "proposed_edition": "cand-10147",
    "antonio_da_venezia": "cand-10148", "religion_image": "cand-10149",
    "gallo_1948": "cand-10150", "england": "cand-10151", "royal_library": "cand-10152",
}
BODY_IDS = {
    "p334_advertisement": "st-chp13-p334-albrizzi-plan-revive-venetian-prints-open",
    "p335_relations": "st-chp13-p335-albrizzi-close-relations-with-recurti",
    "p335_frontispiece": "st-chp13-p335-piazzetta-frontispiece-before-albrizzi-enterprise",
    "p335_devotional_book": "st-chp13-p335-recurti-published-devotional-book",
    "p335_drawings": "st-chp13-p335-piazzetta-seventy-drawings-for-gerusalemme",
    "p335_richard": "st-chp13-p335-gerusalemme-admired-by-richard",
}
mention_specs = [
    (NOTE_SEGMENT, 192, "cand-9988", "Novelle", "Weekly bulletin named as the source of the advertisement."),
    (NOTE_SEGMENT, 192, CID["augustine"], "St Augustine", "Person named as the subject of the proposed edition."),
    (NOTE_SEGMENT, 192, CID["proposed_edition"], "proposed edition of the works of St Augustine", "The note describes a project, not a confirmed publication."),
    (NOTE_SEGMENT, 193, CID["antonio_da_venezia"], "Padre Antonio da Venezia", "Author form retained as printed."),
    (NOTE_SEGMENT, 193, "cand-9993", "La Chiesa di Gesù Cristo vendicata ne' suoi contrasegni e ne' suoi dogmi", "Title supplied by the footnote; no independent edition check."),
    (NOTE_SEGMENT, 193, "cand-1907", "Piazzetta", "Artist named in the citation."),
    (NOTE_SEGMENT, 193, CID["religion_image"], "Religion trampling on Heresy", "Named image drawn for the book."),
    (NOTE_SEGMENT, 193, "cand-1948", "Pitteri", "Engraver named in the citation."),
    (NOTE_SEGMENT, 193, "cand-8514", "Gallo", "Surname-only cited author; identity remains unresolved."),
    (NOTE_SEGMENT, 193, CID["gallo_1948"], "Gallo, 1948, p. 176, note 4", "Citation locator only."),
    (NOTE_SEGMENT, 194, "cand-9991", "The drawings", "Refers to the approximately seventy drawings named in the body."),
    (NOTE_SEGMENT, 194, "cand-0025", "Albrizzi", "Original owner named in the note."),
    (NOTE_SEGMENT, 194, CID["england"], "England", "Earlier location named without dates."),
    (NOTE_SEGMENT, 194, CID["royal_library"], "Royal Library", "Repository named in the note."),
    (NOTE_SEGMENT, 194, "cand-2662", "Turin", "City named as repository location; index candidate retained pending S3."),
    (BODY_SEGMENT, 38, "cand-0025", "Albrizzi", "Publisher named in the bibliographic note continuation."),
    (BODY_SEGMENT, 38, "cand-2111", "Recurti", "Publisher named in the bibliographic note continuation."),
    (BODY_SEGMENT, 38, "cand-9988", "Novelle", "Publication cited for Albrizzi and Recurti's relations."),
    (BODY_SEGMENT, 39, "cand-10129", "Morazzoni", "Citing author named within the Richard citation; identity remains unresolved."),
]
existing_mention_keys = set()
for row in mentions:
    existing_mention_keys.add((row["segment_id"], row["candidate_id"], row["start_char"], row["end_char"]))
new_mentions = []
occurrence_counts = {}
for index, (segment_id, line_number, candidate_id, surface, note) in enumerate(mention_specs, 1):
    segment = segment_by_id[segment_id]
    lines = source_lines[segment["line_start"] - 1:segment["line_end"]]
    local_line = line_number - segment["line_start"]
    if local_line < 0 or local_line >= len(lines) or surface not in lines[local_line]:
        raise SystemExit(f"mention surface absent on source line {line_number}: {surface!r}")
    start = sum(len(text) + 1 for text in lines[:local_line]) + lines[local_line].index(surface)
    end = start + len(surface)
    key = (segment_id, candidate_id, str(start), str(end))
    if key in existing_mention_keys:
        print(f"reuse existing mention: {segment_id} line {line_number} {surface!r}")
        continue
    mention_id = f"m-s2-ch13-p335-notes-{index:03d}"
    row = {field: "" for field in mention_fields}
    row.update({"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})
    new_mentions.append(row)
    existing_mention_keys.add(key)

statement_specs = [
    ("st-chp13-p335-note1-augustine-advertisement", NOTE_SEGMENT, 192, 335, 4,
     "cand-9988", CID["proposed_edition"], "advertised_proposed_edition",
     "An advertisement in the Novelle dated 19 March 1730 concerned a proposed edition of Saint Augustine's works.",
     "The note describes a proposal, not a publication known to have appeared.",
     ["cand-9988", CID["augustine"], CID["proposed_edition"]], [BODY_IDS["p334_advertisement"]],
     [{"source_candidate_id": "cand-9988", "date": "1730-03-19", "item": "advertisement"}], None),
    ("st-chp13-p335-note2-book-frontispiece", NOTE_SEGMENT, 193, 335, 4,
     "cand-9993", CID["religion_image"], "frontispiece_drawn_for_devotional_book",
     "The footnote identifies the devotional book as La Chiesa di Gesù Cristo vendicata ne' suoi contrasegni e ne' suoi dogmi and says Piazzetta drew Religion trampling on Heresy, engraved by Pitteri.",
     "The bibliographic details are reported by Haskell's note; neither the book nor the cited Gallo passage was independently consulted.",
     [CID["antonio_da_venezia"], "cand-9993", "cand-1907", CID["religion_image"], "cand-1948", "cand-8514", CID["gallo_1948"]],
     [BODY_IDS["p335_frontispiece"], BODY_IDS["p335_devotional_book"]],
     [{"source_candidate_id": CID["gallo_1948"], "author_candidate_id": "cand-8514", "year": "1948", "page": "176", "note": "4"}],
     [{"source_line": 193, "ocr": "Ges�� Cristo", "print": "Gesù Cristo", "basis": "CHP-13.pdf physical page 4."}]),
    ("st-chp13-p335-note2-recurti-citation", BODY_SEGMENT, 38, 335, 4,
     "cand-9988", "cand-2111", "footnote_citation_for_publisher_relations",
     "Haskell directs readers to the Novelle for information about Albrizzi's relations with Recurti.",
     "This is a bibliographic pointer only; it does not independently verify the nature or details of the relationship.",
     ["cand-0025", "cand-2111", "cand-9988"], [BODY_IDS["p335_relations"]],
     [{"source_candidate_id": "cand-9988", "reference_text": "passim"}], None),
    ("st-chp13-p335-note3-drawings-owned-by-albrizzi", NOTE_SEGMENT, 194, 335, 4,
     "cand-9991", "cand-0025", "originally_belonged_to",
     "The note says the approximately seventy drawings originally belonged to Albrizzi.",
     "The note gives no dates for ownership or transfer.", ["cand-9991", "cand-0025"], [BODY_IDS["p335_drawings"]], [], None),
    ("st-chp13-p335-note3-drawings-formerly-in-england", NOTE_SEGMENT, 194, 335, 4,
     "cand-9991", CID["england"], "formerly_located_in",
     "The note says the drawings were at one time in England.",
     "No date, custodian, or route of transfer is given.", ["cand-9991", CID["england"]], [BODY_IDS["p335_drawings"]], [], None),
    ("st-chp13-p335-note3-drawings-now-at-royal-library", NOTE_SEGMENT, 194, 335, 4,
     "cand-9991", CID["royal_library"], "currently_held_at",
     "The note says the drawings are now in the Royal Library, Turin.",
     "The institution is recorded as named by Haskell; exact identity remains for S3 alignment.", ["cand-9991", CID["royal_library"], "cand-2662"], [BODY_IDS["p335_drawings"]], [], None),
    ("st-chp13-p335-note4-richard-citation", BODY_SEGMENT, 39, 335, 4,
     "cand-9996", "cand-2188", "citation_for_reported_admiration",
     "The note cites Richard, volume II, page 492, as quoted through Morazzoni, page 125, for the report that the 1745 Gerusalemme Liberata was admired by Abbé Richard.",
     "Citation locator only; neither Richard nor Morazzoni was independently consulted. The print reads volume II; the OCR reads H.",
     ["cand-9990", "cand-9996", "cand-2188", "cand-10129"], [BODY_IDS["p335_richard"]],
     [{"source_candidate_id": "cand-9996", "author_candidate_id": "cand-10129", "volume": "II", "page": "492", "quoted_through_page": "125"}],
     [{"source_line": 39, "ocr": "Richard, H, p. 492", "print": "Richard, II, p. 492", "basis": "CHP-13.pdf physical page 4."}]),
]
statement_by_id = {row["statement_id"]: row for row in statements}
candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
new_statements = []
links_by_body = {}
for sid, segment_id, line, page, physical, subject, obj, predicate, claim, qualification, mentioned, linked, citations, corrections in statement_specs:
    if sid in statement_by_id:
        raise SystemExit(f"statement already exists: {sid}")
    for body_id in linked:
        if body_id not in statement_by_id:
            raise SystemExit(f"linked body statement missing: {body_id}")
        links_by_body.setdefault(body_id, []).append((sid, line, NOTE_SEGMENT if line in [192, 193, 194] else BODY_SEGMENT, page))
    for candidate_id in [subject, obj, *mentioned]:
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"candidate missing for {sid}: {candidate_id}")
    if segment_id == NOTE_SEGMENT:
        quote = source_lines[line - 1]
    else:
        quote = source_lines[line - 1]
    qualifiers = {
        "source_line_start": line, "source_line_end": line, "printed_page": page,
        "pdf_physical_page": physical, "claim": claim, "speaker": "Haskell, printed footnote",
        "text_layer": "bibliographic citation locator" if predicate.startswith("footnote_citation") or predicate.startswith("citation_for_") else "footnote",
        "qualification": qualification, "mentioned_candidate_ids": mentioned,
        "footnote_number": 2 if "note2-recurti" in sid else (3 if "note3" in sid else (1 if "note1" in sid else (4 if "note4" in sid else 2))),
        "linked_body_statement_ids": linked,
    }
    if citations:
        qualifiers["citations"] = citations
    if corrections:
        qualifiers["ocr_corrections"] = corrections
    new_statements.append({"statement_id": sid, "segment_id": segment_id,
                           "subject_candidate_id": subject, "object_candidate_id": obj,
                           "predicate": predicate, "qualifiers": qualifiers,
                           "original_quote": quote, "origin": "book",
                           "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md"})

candidate_new = candidates + new_candidates
candidate_by_id["cand-9993"]["canonical_name"] = "Padre Antonio da Venezia, La Chiesa di Gesù Cristo vendicata ne' suoi contrasegni e ne' suoi dogmi"
candidate_by_id["cand-9993"]["detail"] = "Piazzetta drew Religion trampling on Heresy for this devotional book, engraved by Pitteri, according to p.335 note 2. Exact edition and cited Gallo passage have not been independently checked."
for body_id, link_rows in links_by_body.items():
    body = statement_by_id[body_id]
    q = body.setdefault("qualifiers", {})
    refs = q.setdefault("footnote_refs", [])
    ids = []
    for sid, line, segment_id, page in link_rows:
        ids.append(sid)
        marker = 2 if "note2" in sid else (3 if "note3" in sid else (4 if "note4" in sid else 1))
        entry = {"footnote_marker": str(marker), "footnote_printed_page": page,
                 "footnote_text_pending": False, "footnote_segment": segment_id,
                 "footnote_line_range": f"L{line}", "footnote_body_link_status": "linked",
                 "footnote_note_statement_ids": [sid]}
        if not any(x.get("footnote_marker") == entry["footnote_marker"] and x.get("footnote_segment") == segment_id and x.get("footnote_line_range") == entry["footnote_line_range"] for x in refs):
            refs.append(entry)
    q["footnote_text_pending"] = False
    q["footnote_body_link_status"] = "linked"
    q["footnote_note_statement_ids"] = sorted(set(q.get("footnote_note_statement_ids", [])) | set(ids))

coverage_by_id[BODY_SEGMENT]["migration_status"] = "complete"
coverage_by_id[BODY_SEGMENT]["source_line_ranges"] = "L32-39"
coverage_by_id[BODY_SEGMENT]["note"] = "Printed p.335 body and its notes were checked against CHP-13.pdf physical page 4. Consolidated notes L192-194 and the Richard citation at OCR L39 are mapped to body claims; L38 is retained as the Recurti/Novelle citation continuation. OCR is unchanged; print corrections remain in S2 qualifiers."
coverage_by_id[NOTE_SEGMENT]["source_line_ranges"] = "L180-194"
coverage_by_id[NOTE_SEGMENT]["note"] = "Notes L180-191 (pp.332-334) and p.335 notes L192-194 are migrated. L195-238 and mirrored caption lines L247-248 remain to process or map; the composite segment remains partial."

new_candidate_count = len(new_candidates)
new_mention_count = len(new_mentions)
new_statement_count = len(new_statements)
print(f"preview candidates=+{new_candidate_count} mentions=+{new_mention_count} statements=+{new_statement_count}; p335 body complete; notes coverage L180-194")
if not args.apply:
    print("preview only; pass --apply to write")
    raise SystemExit(0)

for path in [candidate_path, mention_path, statement_path, coverage_path]:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_new)
write_csv(mention_path, mention_fields, mentions + new_mentions)
write_jsonl(statement_path, statements + new_statements)
write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
print(f"applied candidates={len(candidate_new)} mentions={len(mentions)+new_mention_count} statements={len(statements)+new_statement_count} coverage={len(coverage)}")
