#!/usr/bin/env python3
"""Controlled S2 migration for printed page 404 and p.403 continuation."""
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
P403 = "chp-20:20_CHP-20Postscript:l110-121"
P404 = "chp-20:20_CHP-20Postscript:l123-135"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
BACKUP = ".bak-s2-chp20-p404-20261004"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
P403_SHA = "7bc5e518a943cfa45d60c928cbff4ae1a8be817201c0d88fb9d8c4d00c5fe81b"
P404_SHA = "19d1d03fcc1da1f57c2bc8445fecd64f437467c74517fa53f840de5c774d8650"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
ARGS = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


if sha(SOURCE) != SOURCE_SHA or sha(PDF) != PDF_SHA:
    raise SystemExit("source or PDF changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(source_lines[122:135])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != P404_SHA:
    raise SystemExit("p.404 S0 segment hash mismatch")
if hashlib.sha256("\n".join(source_lines[109:121]).encode("utf-8")).hexdigest() != P403_SHA:
    raise SystemExit("p.403 S0 segment hash mismatch")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
for segment_id in (P403, P404, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"missing segment: {segment_id}")
if segment_by_id[P404]["sha256"] != P404_SHA or segment_by_id[P404]["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("p.404 S0 registration changed")
if coverage_by_id[P403]["migration_status"] != "partial":
    raise SystemExit("p.403 must be partial before continuation")
if (coverage_by_id[P404]["disposition"], coverage_by_id[P404]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.404 is not queued/pending")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("notes segment must remain queued")

open_id = "st-chp20-p403-borea-don-lorenzo-ferdinand-leopoldo-open"
open_statement = next((row for row in statements if row["statement_id"] == open_id), None)
if not open_statement or not open_statement["qualifiers"].get("open_across_segment") or open_statement["qualifiers"].get("continues_in_segment") != P404:
    raise SystemExit("p.403 Borea continuation statement changed")

candidate_specs = [
    ("cand-11023", "Exhibition on Cardinal Leopoldo's taste (p.404 title/date not stated in body)", "event", "The source continues the p.403 phrase 'an exhibition'; descriptive label only, with footnote 1 pending."),
    ("cand-11024", "Articles on Cardinal Leopoldo's taste cited by Haskell on p.404", "archive", "A source-described article series; individual titles and bibliographic details await the notes/bibliography pass."),
    ("cand-11025", "Procaccis (plural author reference on p.404; identities unresolved)", "", "The body gives only a plural surname. Footnote 2 remains queued; do not infer a family or individual identities here."),
    ("cand-11026", "Muraro (scholar cited by surname on p.404)", "person", "Surname only in the body; bibliographic and identity resolution deferred."),
    ("cand-11027", "Silvia Meloni", "person", "Named in the body; the earlier surname-only Meloni reference may be related, but footnote and S3 identity resolution remain pending."),
    ("cand-11028", "Chiarini de Anna (scholar cited on p.404)", "person", "Name as printed in the body; keep distinct from Marco Chiarini and other Chiarini candidates pending S3."),
    ("cand-11029", "Bandera (scholar cited by surname on p.404)", "person", "Surname only in the body; identity deferred."),
    ("cand-11030", "Prinz (scholar cited by surname on p.404)", "person", "Surname only in the body; identity deferred."),
    ("cand-11031", "Prinz's analysis of the formation of the Uffizi self-portrait gallery", "archive", "A scholarly analysis cited by footnote 7; publication details await notes/bibliography review."),
    ("cand-11032", "Uffizi gallery of self-portraits (collection/gallery referent; type unresolved)", "", "The passage discusses its formation, but the term 'gallery' does not settle whether the referent is a collection or physical space."),
    ("cand-11033", "Late Baroque art exhibition mounted in Florence and Detroit (1974)", "event", "Descriptive event label; the source supplies subject, date, and venues but no formal title in the body."),
    ("cand-11034", "Late Baroque art in Florence", "term", "Subject of the 1974 exhibition; the source does not supply a separate formal period label."),
    ("cand-11035", "Stella Rudolph", "person", "Named scholar; identity alignment deferred to S3."),
    ("cand-11036", "Stella Rudolph's articles on Cosimo III and Florentine provincial culture", "archive", "Two articles are mentioned, one on 'stile Cosimo III'; titles and citation details await notes."),
    ("cand-11037", "Italian provincial culture in Florence at the end of the seventeenth century", "term", "Rudolph's attributed interpretation; preserve its connection to the reported decline of Rome."),
    ("cand-11038", "Aristocratic families' patronage in Florence", "term", "A general group description, not a named family or institution."),
    ("cand-11039", "Chiarini's 1975 inventories of Grand Prince Ferdinand", "archive", "Inventories published by Chiarini; exact titles and identity await notes/bibliography review."),
    ("cand-11040", "Chiarini (author cited for 1975 and 1976 studies on p.404)", "person", "Surname only; keep distinct from Marco Chiarini and Chiarini de Anna pending S3."),
    ("cand-11041", "Strocchi (scholar cited by surname on p.404)", "person", "Surname only in the body; identity deferred."),
    ("cand-11043", "Guelfi (scholar cited by surname on p.404)", "person", "The body uses 'her' but gives no first name; identity deferred."),
    ("cand-11044", "Guelfi's monograph on Alessandro Magnasco", "archive", "Monograph cited in the passage; not independently consulted here."),
    ("cand-11045", "Account of seventeenth- and eighteenth-century art exhibitions in Florence", "archive", "A very full account is mentioned; author and bibliographic identity await footnote 14 review."),
    ("cand-11046", "Florentine art exhibition organized in 1706", "event", "The source says the Prince had a part in organizing it; do not infer the exact role or title."),
    ("cand-11047", "Florentine art exhibition catalogued in 1705", "event", "A catalogue is reported as evidence of a separate 1705 exhibition; no formal title is supplied."),
    ("cand-11048", "Catalogue for a Florentine art exhibition in 1705", "archive", "The discovery is said to revise Haskell's account; bibliographic details await footnote 15 review."),
    ("cand-11049", "Cleaning of paintings by Antonio Domenico Gabbiani at the Pitti", "event", "Undated conservation activity reported by Haskell; no individual paintings are identified."),
    ("cand-11050", "Chiarini's 1976 articles on Antonio Domenico Gabbiani", "archive", "Research cited in footnote 16; exact title and identity of Chiarini await notes/S3."),
    ("cand-11051", "Ewald (scholar cited on p.404)", "person", "Surname only in this passage; keep separate from the existing Ewald 1965 candidate pending S3."),
    ("cand-11052", "Ewald's 1976 articles on Antonio Domenico Gabbiani", "archive", "Research cited in footnote 17; not independently consulted here."),
    ("cand-11053", "Unidentified pictures owned by the Del Rosso brothers and identified by Silvia Meloni", "work", "The passage does not title or enumerate the pictures and does not say all are by Luca Giordano."),
    ("cand-11054", "Gallery of the Aeneid associated with Raimondo Buonaccorsi", "work", "The passage treats it as an identifiable ensemble that survived and was acquired; whether this denotes the picture cycle, collection, or gallery setting remains to be checked."),
    ("cand-11055", "Comune of Macerata", "institution", "Municipal body said to have acquired the Gallery of the Aeneid in 1967; keep distinct from the city of Macerata."),
    ("cand-11056", "Unidentified finest pictures dispersed from the Gallery of the Aeneid", "work", "A source-described subset; no individual titles or number are supplied."),
    ("cand-11057", "Detroit", "place", "Venue of the 1974 exhibition, as named in the source."),
    ("cand-11058", "Stile Cosimo III", "term", "A style label named as the subject of one of Rudolph's articles; preserve the source wording."),
]
candidate_source_lines = {
    "cand-11023": 124, "cand-11024": 124, "cand-11025": 124, "cand-11026": 124,
    "cand-11027": 124, "cand-11028": 124, "cand-11029": 125, "cand-11030": 125,
    "cand-11031": 125, "cand-11032": 125, "cand-11033": 126, "cand-11034": 126,
    "cand-11035": 126, "cand-11036": 126, "cand-11037": 126, "cand-11038": 126,
    "cand-11039": 128, "cand-11040": 128, "cand-11041": 129,
    "cand-11043": 131, "cand-11044": 131, "cand-11045": 131, "cand-11046": 131,
    "cand-11047": 131, "cand-11048": 131, "cand-11049": 131, "cand-11050": 131,
    "cand-11051": 131, "cand-11052": 131, "cand-11053": 133, "cand-11054": 134,
    "cand-11055": 135, "cand-11056": 135, "cand-11057": 126, "cand-11058": 126,
}
natural_keys = {(row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold()) for row in candidates}
for candidate_id, name, kind, detail in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID exists: {candidate_id}")
    key = (name.strip().casefold(), kind.casefold())
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {name}")
    row = {
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P404}#L{candidate_source_lines[candidate_id]}",
    }
    candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

# candidate, exact OCR surface, first/last source line, occurrence, note
mention_specs = [
    ("cand-11023", "exhibition", 124, 124, 0, "First word completes p.403's 'an exhibition'; marker 1 points to the queued notes segment."),
    ("cand-11024", "series of articles", 124, 124, 0, "Group of cited articles; individual titles are not supplied in the body."),
    ("cand-11025", "Procaccis", 124, 124, 0, "Plural surname reference; footnote details remain queued."),
    ("cand-11026", "Muraro", 124, 124, 0, "Surname-only scholar; footnote 3 remains queued."),
    ("cand-11027", "Meloni", 124, 124, 0, "Surname-only mention; full name appears later on this page, but footnote identity is not yet resolved."),
    ("cand-11028", "Chiarini de\nAnna", 124, 125, 0, "Name crosses a source line break; do not merge with other Chiarini candidates."),
    ("cand-11029", "Bandera", 125, 125, 0, "Surname-only scholar; footnote 6 remains queued."),
    ("cand-1629", "the Cardinal’s taste", 125, 125, 0, "The preceding p.403 context identifies the Cardinal as Leopoldo; retain that local reference."),
    ("cand-11032", "formation of the Uffizi gallery of self-portraits", 125, 125, 0, "Collection/gallery referent; the wording does not establish whether this is a physical room or collection."),
    ("cand-7945", "Uffizi", 125, 125, 0, "Reuse the existing Uffizi candidate as the named repository/institutional context."),
    ("cand-3589", "self-portraits", 125, 125, 0, "Reuse the existing self-portraiture term candidate."),
    ("cand-11030", "Prinz", 125, 125, 0, "Surname-only scholar; footnote 7 remains queued."),
    ("cand-11031", "analysed by Prinz", 125, 125, 0, "Prinz's cited analysis of the gallery's formation."),
    ("cand-10997", "Klaus Lankheit", 126, 126, 0, "The full given name appears here; reuse p.403 surname candidate for the contiguous postscript, with broader identity alignment deferred to S3."),
    ("cand-1607", "Cosimo III", 126, 126, 0, "Reuse the indexed Medici candidate."),
    ("cand-11033", "important exhibition devoted to late Baroque Art in Florence", 126, 126, 0, "Descriptive 1974 event label; no official title is supplied in the body."),
    ("cand-11034", "late Baroque Art", 126, 126, 0, "Art-field phrase in the exhibition description."),
    ("cand-3397", "Florence", 126, 126, 0, "Place in the exhibition description."),
    ("cand-11057", "Detroit", 126, 126, 0, "Second venue of the same exhibition mounted successively in 1974."),
    ("cand-11035", "Stella Rudolph", 126, 126, 0, "Named scholar."),
    ("cand-11036", "two interesting articles", 126, 126, 0, "Group of Rudolph's cited articles; one is on 'stile Cosimo III'."),
    ("cand-11058", "‘stile Cosimo III’", 126, 126, 0, "Style label named as the subject of an article."),
    ("cand-3397", "Florence", 126, 126, 1, "Florence in Rudolph's discussion of provincial culture."),
    ("cand-3397", "Florence", 126, 126, 2, "Third Florence mention, in Rudolph's discussion."),
    ("cand-11037", "Italian provincial culture", 126, 126, 0, "Rudolph's attributed subject and interpretation."),
    ("cand-4490", "Rome", 126, 126, 0, "Place named in the reported decline of Rome."),
    ("cand-11038", "aristocratic families in the city", 126, 126, 0, "General family-group description, not a named family."),
    ("cand-1609", "Grand Prince Ferdinand", 127, 128, 0, "Reuse the Medici Grand Prince candidate; the phrase crosses a line break."),
    ("cand-11039", "inventories published by\nChiarini", 128, 129, 0, "Source-group mention; publication details await notes."),
    ("cand-11040", "Chiarini", 129, 129, 0, "Surname-only author; keep separate from Marco Chiarini pending S3."),
    ("cand-11041", "Strocchi", 129, 129, 0, "Surname-only scholar; footnote 12 remains queued."),
    ("cand-1609", "the Prince himself", 128, 128, 0, "Anaphoric reference to Grand Prince Ferdinand."),
    ("cand-1609", "Ferdinand", 130, 130, 0, "Reuse the Grand Prince candidate."),
    ("cand-1492", "Magnasco", 131, 131, 0, "Reuse Alessandro Magnasco candidate."),
    ("cand-1492", "the artist", 131, 131, 0, "Anaphoric reference to Magnasco."),
    ("cand-11043", "Guelfi", 131, 131, 0, "Surname-only scholar; 'her' is not used to infer a first name."),
    ("cand-11044", "monograph on the artist", 131, 131, 0, "Guelfi's cited monograph; bibliographic details await footnote 13."),
    ("cand-11045", "very full account of seventeenthand eighteenthcentury art exhibitions in Florence", 131, 131, 0, "OCR spacing is retained in the mention; page-image hyphenation is recorded in the statement."),
    ("cand-1609", "the Prince’s part", 131, 131, 0, "Anaphoric reference to Grand Prince Ferdinand."),
    ("cand-11046", "one held in 1706", 131, 131, 0, "Descriptive reference to the exhibition the Prince helped organize."),
    ("cand-11048", "catalogue for the exhibition of 1705", 131, 131, 0, "Newly discovered catalogue; footnote 15 remains pending."),
    ("cand-11047", "exhibition of 1705", 131, 131, 0, "Distinct event identified through the discovered catalogue."),
    ("cand-11049", "cleaning of a number of paintings by Antonio Domenico Gabbiani in the Pitti", 131, 131, 0, "Undated conservation activity; the individual paintings are not identified."),
    ("cand-1093", "Antonio Domenico Gabbiani", 131, 131, 0, "Reuse the indexed artist candidate."),
    ("cand-7662", "the Pitti", 131, 131, 0, "Reuse Palazzo Pitti as the place; the passage does not mean the museum institution."),
    ("cand-11050", "articles on him by Chiarini16", 131, 131, 0, "Cited research on Gabbiani; author identity and details await footnote 16."),
    ("cand-11040", "Chiarini", 131, 131, 0, "Second surname-only occurrence; keep separate from Marco Chiarini pending S3."),
    ("cand-11051", "Ewald", 131, 131, 0, "Surname-only scholar; keep separate from the existing Ewald candidate pending S3."),
    ("cand-11052", "Ewald17", 131, 131, 0, "Cited article group; marker 17 applies to Ewald."),
    ("cand-1609", "the Grand Prince", 131, 131, 0, "Anaphoric reference to Ferdinand de' Medici."),
    ("cand-1093", "him", 131, 131, 0, "Anaphoric reference to Antonio Domenico Gabbiani."),
    ("cand-8078", "Del Rosso brothers", 132, 132, 0, "Reuse the collective candidate from p.403; do not split individuals."),
    ("cand-11027", "Silvia Meloni", 132, 132, 0, "Full name in the body; relation to the earlier p.404 surname mention awaits footnote/S3 review."),
    ("cand-1172", "Luca\nGiordano", 132, 133, 0, "Reuse the broad indexed artist candidate; the name crosses a source line break."),
    ("cand-3397", "the city", 133, 133, 0, "Anaphoric place reference to Florence."),
    ("cand-11053", "many of the pictures they owned", 133, 133, 0, "Unidentified group of pictures attributed to the Del Rosso brothers' holdings; not asserted to all be Giordano works."),
    ("cand-0467", "Raimondo Buonaccorsi", 134, 134, 0, "Reuse the indexed patron candidate."),
    ("cand-11054", "‘Gallery of the Aeneid’", 134, 134, 0, "Named ensemble/collection; its physical and object boundary remains to be verified."),
    ("cand-11055", "Comune of Macerara", 135, 135, 0, "Municipal institution; OCR has Macerara, page image reads Macerata."),
    ("cand-1475", "Macerara", 135, 135, 0, "City-place mention nested in Comune of Macerara; visual correction to Macerata is recorded in the statement."),
    ("cand-11054", "it", 135, 135, 0, "Anaphoric reference to the Gallery of the Aeneid ensemble."),
    ("cand-11056", "many of the finest pictures in it", 135, 135, 0, "Unidentified subset of pictures in the ensemble, dispersed before acquisition."),
]

line_offsets = {}
cursor = 0
for line_number in range(123, 136):
    line_offsets[line_number] = cursor
    cursor += len(source_lines[line_number - 1]) + 1
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for index, (candidate_id, surface, first_line, last_line, occurrence, note) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p404-{index:03d}"
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
    new_mentions.append({"mention_id": mention_id, "segment_id": P404, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(position),
                         "end_char": str(position + len(surface)), "note": note})
    mention_ids.add(mention_id)

note_lines = {1: 244, 2: 244, 3: 245, 4: 245, 5: 246, 6: 246, 7: 247, 8: 247,
              9: 248, 10: 248, 11: 249, 12: 249, 13: 250, 14: 250, 15: 251,
              16: 251, 17: 252, 18: 252, 19: 253}


def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer, qualification, ids, note_markers=(), relation=False, extra=None):
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 404,
                  "pdf_physical_page": 13, "claim": claim, "speaker": speaker, "text_layer": layer,
                  "qualification": qualification, "mentioned_candidate_ids": ids,
                  "relation_candidate": relation}
    if note_markers:
        qualifiers.update({"footnote_markers": list(note_markers), "footnote_text_pending": True,
                           "footnote_segment": NOTES,
                           "footnote_refs": [{"marker": n, "segment_id": NOTES, "source_line": note_lines[n]} for n in note_markers],
                           "footnote_statement_ids": [], "footnote_body_link_status": "pending"})
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": P404, "subject_candidate_id": subject,
            "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": "\n".join(source_lines[first - 1:last]),
            "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "origin": "book"}


new_statements = [
    make_statement("st-chp20-p404-leopoldo-exhibition-articles-taste", 124, 125, "cand-11024", "cand-1629",
                   "later_research_added_to_knowledge_of_cardinal_taste",
                   "Haskell says an exhibition and articles by the Procaccis, Muraro, Meloni, Chiarini de Anna, and Bandera greatly added to knowledge of Cardinal Leopoldo's taste.",
                   "Haskell", "authorial report of later scholarship",
                   "This continues the p.403 clause beginning 'an exhibition'. Scholar identities and publication contents are not independently verified; body footnotes 1-6 remain queued.",
                   ["cand-11023", "cand-11024", "cand-11025", "cand-11026", "cand-11027", "cand-11028", "cand-11029", "cand-1629"],
                   [1, 2, 3, 4, 5, 6], True,
                   {"cited_material_not_independently_consulted": True,
                    "cross_reference_segments": [{"segment_id": P403, "source_line_start": 120, "source_line_end": 121}]}
    ),
    make_statement("st-chp20-p404-prinz-uffizi-self-portrait-gallery-analysis", 125, 125, "cand-11030", "cand-11032",
                   "analysed_formation_of_self_portrait_gallery",
                   "Haskell says the formation of the Uffizi gallery of self-portraits had been analysed by Prinz.",
                   "Haskell", "authorial report of scholarship",
                   "Prinz is cited by surname only, and the gallery phrase does not settle whether it denotes a collection or physical space. Footnote 7 remains queued.",
                   ["cand-11030", "cand-11031", "cand-11032", "cand-7945", "cand-3589"], [7], True,
                   {"cited_material_not_independently_consulted": True}
    ),
    make_statement("st-chp20-p404-lankheit-reassesses-cosimo-iii", 126, 126, "cand-10997", "cand-1607",
                   "research_reassesses_role_of_cosimo_iii",
                   "Haskell says Klaus Lankheit showed that Cosimo III's role, which Haskell and many previous writers had treated as that of a blinkered villain, was more positive—especially regarding sculpture—than Haskell had suggested in 1963.",
                   "Haskell reporting Klaus Lankheit", "authorial report and retrospective self-correction",
                   "The judgment is attributed to Lankheit and Haskell's own earlier assessment; footnote 8 remains queued. The full given name is present here, but cross-chapter identity matching awaits S3.",
                   ["cand-10997", "cand-1607"], [8], True,
                   {"cited_material_not_independently_consulted": True}
    ),
    make_statement("st-chp20-p404-late-baroque-florence-detroit-exhibition", 126, 126, "cand-11033", "cand-1607",
                   "exhibition_clarified_cosimo_iii_assessment",
                   "Haskell says Cosimo III's more positive role became clear beyond all doubt in 1974 when an exhibition devoted to late Baroque art in Florence was mounted successively in Florence and Detroit.",
                   "Haskell", "authorial retrospective assessment",
                   "The event title is not supplied in the body; the candidate uses a descriptive label. Footnote 9 remains queued.",
                   ["cand-11033", "cand-11034", "cand-3397", "cand-11057", "cand-1607"], [9], True,
                   {"cited_material_not_independently_consulted": True}
    ),
    make_statement("st-chp20-p404-rudolph-florentine-provincial-culture", 126, 126, "cand-11035", "cand-11037",
                   "articles_interpret_florentine_provincial_culture_and_patronage",
                   "Haskell says Stella Rudolph's articles, one on 'stile Cosimo III', discuss Florence amid a broader revival of Italian provincial culture at the end of the seventeenth century, alongside Rome's decline, and emphasize lavish patronage by many aristocratic families in the city.",
                   "Haskell reporting Stella Rudolph", "authorial report of scholarship",
                   "The cultural interpretation and account of patronage are attributed to Rudolph; footnote 10 remains queued. The unnamed families are not turned into individual candidates.",
                   ["cand-11035", "cand-11036", "cand-11058", "cand-11037", "cand-3397", "cand-4490", "cand-11038"], [10], True,
                   {"cited_material_not_independently_consulted": True}
    ),
    make_statement("st-chp20-p404-inventories-magnasco-limited-patronage", 127, 131, "cand-1609", "cand-1492",
                   "inventories_support_employment_of_magnasco_and_later_assessment",
                   "Haskell says new inventories published by Chiarini and Strocchi disclosed that Grand Prince Ferdinand employed Magnasco; he says the painter's talents must surely have been congenial to the Prince, while Guelfi stressed the significance of this admittedly limited patronage in her monograph.",
                   "Haskell reporting inventories and Guelfi", "authorial report with explicit inference",
                   "Employment is reported from inventories; 'must surely have been congenial' is Haskell's inference, and the patronage is expressly limited. Footnotes 11-13 remain queued; cited sources were not independently consulted.",
                   ["cand-1609", "cand-11039", "cand-11040", "cand-11041", "cand-1492", "cand-11043", "cand-11044"],
                   [11, 12, 13], True,
                   {"cited_material_not_independently_consulted": True,
                    "cross_reference_segments": [{"segment_id": "chp-8:08_CHP-8_sec_i:l126-157", "source_line_start": 126, "source_line_end": 157}]}
    ),
    make_statement("st-chp20-p404-1706-role-corrected-by-1705-catalogue", 131, 131, "cand-1609", "cand-11046",
                   "1705_catalogue_revises_prince_role_in_exhibition_history",
                   "Haskell says a full account of Florentine art exhibitions clarified the Prince's part in organizing the 1706 exhibition; discovery of a catalogue for the 1705 exhibition showed that he had somewhat exaggerated the Prince's role in inaugurating this aspect of exhibition activity.",
                   "Haskell", "authorial report and correction of prior interpretation",
                   "The 1706 and 1705 exhibitions are distinct events. Haskell qualifies the Prince's role and explicitly revises his earlier claim. Footnotes 14-15 remain queued.",
                   ["cand-11045", "cand-1609", "cand-11046", "cand-11047", "cand-11048"], [14, 15], True,
                   {"cited_material_not_independently_consulted": True,
                    "ocr_corrections": [{"source_line": 131, "ocr": "seventeenthand eighteenthcentury", "print": "seventeenth- and eighteenth-century", "basis": "CHP-20Postscript.pdf physical page 13 image"}]}
    ),
    make_statement("st-chp20-p404-gabbiani-cleaning-and-scholarship", 131, 131, "cand-11049", "cand-1093",
                   "cleaning_and_studies_change_assessment_of_gabbiani_and_ferdinand",
                   "Haskell says the cleaning of a number of Gabbiani paintings at the Pitti and articles by Chiarini and Ewald convinced him that he had underrated the artist's merits, and consequently the perception of the Grand Prince who admired him.",
                   "Haskell", "authorial retrospective assessment based on conservation and scholarship",
                   "No individual paintings or cleaning date are identified. The source attributes Haskell's changed assessment to the cleaning and cited articles; footnotes 16-17 remain queued.",
                   ["cand-11049", "cand-1093", "cand-7662", "cand-11050", "cand-11040", "cand-11051", "cand-11052", "cand-1609"],
                   [16, 17], True,
                   {"cited_material_not_independently_consulted": True}
    ),
    make_statement("st-chp20-p404-meloni-del-rosso-giordano-context", 132, 133, "cand-11027", "cand-8078",
                   "meloni_contextualizes_del_rosso_collection_and_identifies_pictures",
                   "Haskell says Silvia Meloni placed the Del Rosso brothers in a wider context by discussing Luca Giordano's work in Florence and identifying many pictures owned by the brothers.",
                   "Haskell reporting Silvia Meloni", "authorial report of scholarship",
                   "The passage does not state that all pictures identified were by Giordano or name them individually. Footnote 18 remains queued; the earlier surname-only Meloni reference is not yet aligned.",
                   ["cand-11027", "cand-8078", "cand-1172", "cand-3397", "cand-11053"], [18], True,
                   {"cited_material_not_independently_consulted": True}
    ),
    make_statement("st-chp20-p404-buonaccorsi-gallery-acquisition-dispersal", 134, 135, "cand-0467", "cand-11054",
                   "gallery_acquired_by_macerata_after_partial_dispersal",
                   "Haskell says Raimondo Buonaccorsi's patronage had suffered grievously: the Gallery of the Aeneid survived virtually intact until the early 1960s and was acquired by the Comune of Macerata in 1967, but many of its finest pictures had already been dispersed.",
                   "Haskell", "authorial report of collection history",
                   "The Gallery of the Aeneid is treated as an identifiable ensemble, while its boundary between picture cycle, collection, and physical gallery remains to be verified. The Comune is an institution, distinct from Macerata as a place. OCR 'Macerara' is corrected from the page image. Footnote 19 remains queued.",
                   ["cand-0467", "cand-11054", "cand-11055", "cand-1475", "cand-11056"], [19], True,
                   {"cited_material_not_independently_consulted": True,
                    "ocr_corrections": [{"source_line": 135, "ocr": "Macerara", "print": "Macerata", "basis": "CHP-20Postscript.pdf physical page 13 image"}]}
    ),
]

existing_statement_ids = {row["statement_id"] for row in statements}
for statement in new_statements:
    if statement["statement_id"] in existing_statement_ids:
        raise SystemExit(f"statement ID exists: {statement['statement_id']}")
    existing_statement_ids.add(statement["statement_id"])
    first = statement["qualifiers"]["source_line_start"]
    last = statement["qualifiers"]["source_line_end"]
    if statement["original_quote"] != "\n".join(source_lines[first - 1:last]):
        raise SystemExit(f"statement quote mismatch: {statement['statement_id']}")
    for candidate_id in statement["qualifiers"]["mentioned_candidate_ids"]:
        if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate: {candidate_id}")

# Close the p.403 clause whose final word was 'an' on that page.
open_statement["qualifiers"]["qualification"] = "The clause continues on p.404 with an exhibition and cited articles; the resulting claim is now complete. The kinship and cultural-rescue relations remain S2 candidates, not formal edges. Footnote 10 remains queued."
open_statement["qualifiers"].pop("open_across_segment", None)
open_statement["qualifiers"].pop("continues_in_segment", None)
open_statement["qualifiers"]["cross_reference_segments"] = [{"segment_id": P404, "source_line_start": 124, "source_line_end": 125}]

all_mentions = mentions + new_mentions
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"]) for row in all_mentions if row["segment_id"] == P404)
for index, left in enumerate(spans):
    for right in spans[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"crossing/duplicate mention spans: {left[2]} / {right[2]}")

coverage_by_id[P403]["disposition"] = "reviewed"
coverage_by_id[P403]["migration_status"] = "complete"
coverage_by_id[P403]["source_line_ranges"] = "L110-121"
coverage_by_id[P403]["note"] = "Printed p.403 is complete with the continuation beginning p.404 L123-125; notes L239-243 remain queued."
coverage_by_id[P404]["disposition"] = "reviewed"
coverage_by_id[P404]["migration_status"] = "complete"
coverage_by_id[P404]["source_line_ranges"] = "L123-135"
coverage_by_id[P404]["note"] = "Printed p.404 (PDF physical page 13) checked against the page image. Closes p.403 continuation and records scholarship on Cosimo III, Grand Prince Ferdinand, and Florentine patronage, followed by Del Rosso and Buonaccorsi updates. Footnotes 1-19 link to queued notes L244-253."

paths = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP) for path in paths]
if ARGS.apply:
    if any(path.exists() for path in backups):
        raise SystemExit("p.404 recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied p.404 S2 migration; backup suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates={len(candidate_specs)}; new mentions={len(new_mentions)}; new statements={len(new_statements)}")
    print("p.403 statement closure, exact source spans, page/PDF/S0 hashes, notes links and candidate FKs validated")
