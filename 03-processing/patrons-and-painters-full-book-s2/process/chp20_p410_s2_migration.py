#!/usr/bin/env python3
"""Controlled S2 migration for printed p.410 (PDF physical p.19)."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
P409 = "chp-20:20_CHP-20Postscript:l187-199"
P410 = "chp-20:20_CHP-20Postscript:l201-209"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
BACKUP = ".bak-s2-chp20-p410-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
ARGS = parser.parse_args()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)

def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)

def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)

if sha(SOURCE.read_bytes()) != SOURCE_SHA or sha(PDF.read_bytes()) != PDF_SHA:
    raise SystemExit("source or PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(source_lines[200:209])
segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
if P410 not in segment_by_id or sha(body.encode("utf-8")) != segment_by_id[P410]["sha256"]:
    raise SystemExit("p.410 S0 segment hash mismatch")
if segment_by_id[P410]["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("p.410 source registration changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
for segment_id in (P409, P410, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"missing segment: {segment_id}")
if (coverage_by_id[P409]["disposition"], coverage_by_id[P409]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.409 must remain partial until p.410 closes its sentence")
if (coverage_by_id[P410]["disposition"], coverage_by_id[P410]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.410 is not queued/pending")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("postscript notes must remain queued")

candidate_specs = [
    ("cand-11147", "Marianne Roland-Michel", "person", "Named as a scholar who studied the Algarotti tomb painting; align identity during S3.", 202),
    ("cand-11148", "Christopher Lloyd", "person", "Named as the author who discussed his projected but uncompleted Venezia Pittrice; align identity during S3.", 205),
    ("cand-11149", "Christopher Lloyd's projected but uncompleted Venezia Pittrice", "archive", "The source explicitly says the publication was projected but never completed; note 2 and bibliography reconciliation remain pending.", 205),
    ("cand-11150", "Art and its Images exhibition catalogue on reproducing Italian art before photography", "archive", "The body describes an important exhibition catalogue; note 2 cites Art and its Images, pp. 75-76. Exact catalogue identity awaits the bibliography and note review.", 205),
    ("cand-11151", "Loredana Olivato's 1974 article on Giuseppe Maria Sasso", "archive", "The article is described but untitled in the body; note 3 gives Olivato, 1974. The article and cited letters have not been independently consulted.", 206),
    ("cand-11152", "Abate Della Lena", "person", "The source names the abbot as author of a treatise; do not merge automatically with the Giacomo della Lena references elsewhere until S3.", 207),
    ("cand-11153", "Vivarini (surname reference in Della Lena's account)", "person", "Surname-only painter reference; the individual or possible family scope is unresolved.", 207),
    ("cand-11154", "Vincenzo Fontana", "person", "Named as author of an article about Girolamo Manfrin's tobacco manufacture; align identity during S3.", 209),
    ("cand-11155", "Vincenzo Fontana's article on Girolamo Manfrin's tobacco manufacture", "archive", "The article is not titled in the source; footnote 5 appears as Fontana. The work has not been independently consulted.", 209),
    ("cand-11156", "Northern Italy", "place", "Geographical region named as the area whose early painters were being rediscovered.", 205),
]
natural_keys = {(r["canonical_name"].strip().casefold(), r["suggested_type"].strip().casefold()) for r in candidates}
for candidate_id, name, kind, detail, line_number in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID exists: {candidate_id}")
    key = (name.strip().casefold(), kind.casefold())
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {name}")
    row = {"candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
           "index_page_range": "", "suggested_type": kind, "status": "open", "index_source_file": "",
           "sub_entry": "", "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
           "candidate_source_ref": f"{P410}#L{line_number}"}
    candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

# candidate, exact S0 surface, first line, last line, occurrence, note.
mention_specs = [
    ("cand-2207", "Bernhard Rode", 202, 202, 0, "Reuse the indexed artist candidate; attribution is contested in this passage."),
    ("cand-11147", "Marianne Roland-Michel", 202, 202, 0, "Reuse candidate after this page's first mention."),
    ("cand-11141", "this picture", 203, 203, 0, "Refers to the Algarotti tomb painting described on p.409."),
    ("cand-2364", "Sasso", 205, 205, 0, "Reuse the indexed Giuseppe Maria Sasso candidate covering p.410 and chapters 16-17."),
    ("cand-11156", "Northern Italy", 205, 205, 0, "Geographical region in the account of rediscovery of early painters."),
    ("cand-3401", "Venice", 205, 205, 0, "Reuse the Venice place candidate."),
    ("cand-4131", "Italian art", 205, 205, 0, "Reuse the general term candidate."),
    ("cand-11148", "Christopher Lloyd", 205, 205, 0, "Person named in the exhibition catalogue discussion."),
    ("cand-11150", "catalogue of an important exhibition", 205, 205, 0, "Descriptive reference to the catalogue cited in footnote 2."),
    ("cand-11149", "Venezia\nPittrice", 205, 206, 0, "The title is split across the printed page's OCR lines; work remained projected and uncompleted."),
    ("cand-2364", "Sasso", 206, 206, 0, "Second p.410 mention of Giuseppe Maria Sasso."),
    ("cand-11118", "Loredana Olivato", 206, 206, 0, "Reuse the existing person candidate."),
    ("cand-11151", "article by Loredana Olivato", 206, 206, 0, "Untitled 1974 article described in the text; note 3 remains pending."),
    ("cand-11152", "Abate Della Lena", 207, 207, 0, "Retain the source's abbatial form without equating him with Giacomo della Lena."),
    ("cand-10622", "Spoliation of Pictures from Venice", 207, 207, 0, "Reuse the existing archive candidate for Della Lena's treatise."),
    ("cand-11152", "Della Lena", 207, 207, 1, "Second mention in 'aided by Della Lena himself'."),
    ("cand-3401", "Venice", 207, 207, 1, "Reuse Venice for the removal of paintings from the city."),
    ("cand-1239", "Guardi", 207, 207, 0, "Reuse the Francesco Guardi candidate; do not infer a specific painting."),
    ("cand-11153", "Vivarini", 207, 207, 0, "Surname-only painter reference; identity and scope remain unresolved."),
    ("cand-0565", "Carpaccio", 207, 207, 0, "Reuse the indexed Vittore Carpaccio candidate covering p.410."),
    ("cand-0270", "Bellini", 207, 207, 0, "Reuse the indexed Giovanni Bellini candidate covering p.410."),
    ("cand-1512", "Manfrin", 208, 208, 0, "Reuse the Girolamo Manfrin candidate covering p.410; the text refers to his collection."),
    ("cand-1189", "Giorgione", 208, 208, 0, "Reuse the indexed Giorgione candidate covering p.410."),
    ("cand-10695", "Tempesta", 209, 209, 0, "Reuse the existing work candidate Giorgione's Tempesta."),
    ("cand-11154", "Vincenzo Fontana", 209, 209, 0, "Person named as the author of the cited article."),
    ("cand-11155", "article by Vincenzo Fontana", 209, 209, 0, "The untitled article cited in footnote 5; exact bibliographic record remains pending."),
]

line_offsets = {}
cursor = 0
for line_number in range(201, 210):
    line_offsets[line_number] = cursor
    cursor += len(source_lines[line_number - 1]) + 1
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for index, (candidate_id, surface, first_line, last_line, occurrence, note) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p410-{index:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"mention ID exists: {mention_id}")
    if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["status"] != "open":
        raise SystemExit(f"unavailable mention candidate: {candidate_id}")
    start = line_offsets[first_line]
    end = line_offsets[last_line] + len(source_lines[last_line - 1])
    position = start
    for _ in range(occurrence + 1):
        position = body.find(surface, position, end)
        if position < 0:
            raise SystemExit(f"exact source surface not found L{first_line}-{last_line}: {surface!r}")
        position += len(surface)
    position -= len(surface)
    new_mentions.append({"mention_id": mention_id, "segment_id": P410, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(position),
                         "end_char": str(position + len(surface)), "note": note})
    mention_ids.add(mention_id)

note_lines = {1: 276, 2: 277, 3: 278, 4: 279, 5: 280}
source_file = "02-sources/02-Markdown/20_CHP-20Postscript.md"
statement_ids = {row["statement_id"] for row in statements}

def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer,
                   qualification, mentioned, markers=(), relation=False, extra=None):
    if statement_id in statement_ids:
        raise SystemExit(f"statement ID exists: {statement_id}")
    statement_ids.add(statement_id)
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 410,
                  "pdf_physical_page": 19, "claim": claim, "speaker": speaker,
                  "text_layer": layer, "qualification": qualification,
                  "mentioned_candidate_ids": list(mentioned)}
    if relation:
        qualifiers["relation_candidate"] = True
    if markers:
        qualifiers.update({"footnote_markers": list(markers), "footnote_text_pending": True,
                           "footnote_segment": NOTES,
                           "footnote_refs": [{"marker": n, "segment_id": NOTES, "source_line": note_lines[n]} for n in markers],
                           "footnote_statement_ids": [], "footnote_body_link_status": "pending"})
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": P410,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": "\n".join(source_lines[first - 1:last]),
            "source_file": source_file, "origin": "book"}

new_statements = [
    make_statement("st-chp20-p410-tomb-painting-attribution-dispute", 202, 202, "cand-11141", "cand-2207",
                   "reports_contested_attribution",
                   "Haskell reports that earlier writers, followed by Santifaller, attributed the Algarotti tomb painting to Bernhard Rode, while Marianne Roland-Michel considers an Italian artist more likely.",
                   "Haskell reporting earlier writers, Santifaller, and Marianne Roland-Michel",
                   "authorial account of conflicting scholarly attributions",
                   "The attribution remains unresolved. Roland-Michel's proposed Italian artist is unnamed; do not infer a specific painter or treat either attribution as accepted fact.",
                   ["cand-11141", "cand-11146", "cand-2207", "cand-11147"], relation=True,
                   extra={"cross_reference_segments": [{"segment_id": P409, "source_line_start": 199, "source_line_end": 199}],
                          "cross_reference_statement_ids": ["st-chp20-p409-santifaller-algarotti-tomb-painting-partial"]}),
    make_statement("st-chp20-p410-tomb-detail-dust-jacket", 203, 203, "cand-11141", None,
                   "reports_detail_reproduced_on_dust_jacket",
                   "Haskell says a detail from the Algarotti tomb painting is reproduced on the book's dust jacket.",
                   "Haskell", "authorial note about an illustration",
                   "The dust jacket is not separately identified as a dataset object.", ["cand-11141"]),
    make_statement("st-chp20-p410-sasso-scholarly-associations", 205, 205, "cand-2364", None,
                   "reports_recent_attention_to_sasso_and_his_venetian_associations",
                   "Haskell says Sasso attracted recent attention because of close associations with cultivated scholars and artists around Venice who were rediscovering early Italian painters of Northern Italy.",
                   "Haskell reporting recent scholarship", "authorial summary of scholarship",
                   "The scholars and artists are not named in this sentence. The footnote 1 reference remains pending note review.",
                   ["cand-2364", "cand-11156", "cand-3401"], markers=[1],
                   extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p410-lloyd-venezia-pittrice-project", 205, 206, "cand-11148", "cand-11149",
                   "discusses_projected_uncompleted_venezia_pittrice_in_exhibition_catalogue",
                   "Haskell says Christopher Lloyd placed his projected but uncompleted Venezia Pittrice in the context of similar publications in a catalogue for an exhibition on reproducing Italian art before photography.",
                   "Haskell reporting Christopher Lloyd", "authorial report of a publication project",
                   "The project was not completed. Footnote 2 cites Art and its Images, pp. 75-76; the precise catalogue record remains to be checked against the bibliography.",
                   ["cand-11148", "cand-11149", "cand-11150", "cand-4131"], markers=[2],
                   extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p410-olivato-sasso-article", 206, 206, "cand-2364", "cand-11151",
                   "discusses_sasso_as_dealer_and_reports_corrective_correspondence",
                   "Haskell describes Loredana Olivato's article as correcting some of his errors about Sasso and including letters that link Sasso with other figures in these chapters.",
                   "Haskell reporting Loredana Olivato", "authorial report of scholarship",
                   "The article and cited letters have not been independently consulted; its title and exact documentary scope remain pending.",
                   ["cand-2364", "cand-11118", "cand-11151"], markers=[3],
                   extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p410-della-lena-treatise-authorship", 207, 207, "cand-11152", "cand-10622",
                   "authored_treatise_on_spoliation_of_pictures_from_venice",
                   "Haskell identifies the Spoliation of Pictures from Venice as a treatise by Abate Della Lena and says he published it after this book first appeared.",
                   "Haskell", "authorial report of a later publication", "The publication is cited in footnote 4; its text has not been independently consulted.",
                   ["cand-11152", "cand-10622"], markers=[4], relation=True,
                   extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p410-della-lena-treatise-content", 207, 207, "cand-10622", None,
                   "describes_foreign_removal_of_art_from_venice_with_local_assistance",
                   "Haskell says the treatise vividly describes foreigners removing artworks from Venice in the Republic's final years, assisted by Della Lena and his friends.",
                   "Haskell reporting the treatise", "authorial summary of a cited source",
                   "The original treatise has not been independently consulted; the cited-source relation is pending note review.",
                   ["cand-10622", "cand-11152", "cand-3401"], markers=[4],
                   extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p410-della-lena-painter-appreciations", 207, 207, "cand-11152", "cand-1239",
                   "reports_appreciation_for_guardi_and_earlier_venetian_painters",
                   "Haskell says Della Lena's enthusiasm for Guardi did not prevent admiration for the simplicity of Vivarini, Carpaccio, and Bellini.",
                   "Haskell reporting the treatise", "authorial summary of a cited source",
                   "The passage names painters but does not identify particular works; Vivarini's individual or family scope remains unresolved.",
                   ["cand-11152", "cand-1239", "cand-11153", "cand-0565", "cand-0270"], markers=[4],
                   extra={"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p410-manfrin-tempesta-collection", 208, 209, "cand-1512", "cand-10695",
                   "reports_tempesta_once_in_manfrin_collection",
                   "Haskell says the dispersed Manfrin collection once included Giorgione's Tempesta and places its dispersal within nineteenth-century Venetian history.",
                   "Haskell", "authorial historical summary",
                   "The collection is not assigned a separate type or KU here. Do not infer a specific acquisition date or treat the collection reference as proof of a direct personal ownership transfer.",
                   ["cand-1512", "cand-1189", "cand-10695"], relation=True),
    make_statement("st-chp20-p410-manfrin-acquisition-sources-uncertain", 208, 209, "cand-1512", None,
                   "says_sources_of_manfrin_collection_pictures_remain_poorly_documented",
                   "Haskell says the sources from which Manfrin obtained the pictures remain poorly documented.",
                   "Haskell", "authorial statement of a research gap",
                   "This records the author's stated knowledge limit, not proof that no acquisition records exist.", ["cand-1512"]),
    make_statement("st-chp20-p410-fontana-manfrin-tobacco-article", 209, 209, "cand-1512", "cand-11155",
                   "reports_article_emphasizing_tobacco_manufacture_as_collection_wealth_source",
                   "Haskell says Vincenzo Fontana's article emphasizes Manfrin's tobacco manufacturing as the source of the fortune used to build his collection.",
                   "Haskell reporting Vincenzo Fontana", "authorial report of scholarship",
                   "The article is cited in footnote 5 and has not been independently consulted. The OCR reads the printed note number as 6; the page image shows note 5.",
                   ["cand-1512", "cand-11154", "cand-11155"], markers=[5],
                   extra={"cited_material_not_independently_consulted": True,
                          "ocr_corrections": [{"source_line": 280, "ocr": "6 Fontana", "print": "5 Fontana", "basis": "CHP-20Postscript.pdf physical page 19 image"}]})
]

for statement in new_statements:
    for cid in statement["qualifiers"]["mentioned_candidate_ids"]:
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate: {cid}")
    if statement["original_quote"] != "\n".join(source_lines[statement["qualifiers"]["source_line_start"]-1:statement["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"statement source quote mismatch: {statement['statement_id']}")

# Close the p.409 Santifaller sentence with its p.410 continuation.
continued = next((row for row in statements if row["statement_id"] == "st-chp20-p409-santifaller-algarotti-tomb-painting-partial"), None)
if continued is None:
    raise SystemExit("p.409 Santifaller statement is missing")
q = continued["qualifiers"]
if (q.get("source_line_start"), q.get("source_line_end")) != (199, 199):
    raise SystemExit("p.409 continuation statement has unexpected source span")
if not any(item.get("segment_id") == P410 for item in q.get("cross_reference_segments", [])):
    raise SystemExit("p.410 continuation link is missing")
q["cross_reference_segments"] = [
    {"segment_id": item["segment_id"], "source_line_start": 202, "source_line_end": 202}
    if item.get("segment_id") == P410 else item
    for item in q["cross_reference_segments"]
]
q["qualification"] = "P.410 completes the sentence: Santifaller followed earlier writers in attributing the tomb painting to Bernhard Rode, while Marianne Roland-Michel considers an Italian artist more likely. Keep the attribution contested and unresolved; note 9 remains pending."

coverage_by_id[P409]["disposition"] = "reviewed"
coverage_by_id[P409]["migration_status"] = "complete"
coverage_by_id[P409]["note"] = "Printed p.409 (PDF physical page 18) checked against page image. P.410 L202 completes the Santifaller attribution sentence; footnotes 1-9 map to queued notes L271-275."
coverage_by_id[P410]["disposition"] = "reviewed"
coverage_by_id[P410]["migration_status"] = "complete"
coverage_by_id[P410]["source_line_ranges"] = "L201-209"
coverage_by_id[P410]["note"] = "Printed p.410 (PDF physical page 19) checked against page image. Footnotes 1-5 map to queued notes L276-280; printed note 5 is OCR'd as 6 in L280. Page opens Chapters 16 and 17; Sasso and Manfrin references reuse existing candidates where available."

all_mentions = mentions + new_mentions
spans = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"])
               for r in all_mentions if r["segment_id"] == P410)
for i, left in enumerate(spans):
    for right in spans[i+1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"crossing/duplicate mention spans: {left[2]} / {right[2]}")

paths = [candidate_path, mention_path, statement_path, coverage_path]
if ARGS.apply:
    backups = [path.with_name(path.name + BACKUP) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("p.410 recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"APPLIED p.410: candidates+={len(candidate_specs)}, mentions+={len(new_mentions)}, statements+={len(new_statements)}; p.409 and p.410 complete; backup={BACKUP}")
else:
    print(f"DRY RUN p.410: candidates+={len(candidate_specs)}, mentions+={len(new_mentions)}, statements+={len(new_statements)}; closes p.409 and marks p.410 complete")
