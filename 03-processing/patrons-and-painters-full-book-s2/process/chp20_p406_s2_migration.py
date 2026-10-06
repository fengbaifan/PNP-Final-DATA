#!/usr/bin/env python3
"""Controlled S2 migration for printed p.406 (PDF physical p.15)."""
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
P405 = "chp-20:20_CHP-20Postscript:l137-148"
P406 = "chp-20:20_CHP-20Postscript:l150-162"
P407 = "chp-20:20_CHP-20Postscript:l164-172"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
BACKUP = ".bak-s2-chp20-p406-20261004"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
P406_SHA = "ad90c7c7021c0738b90d7b59ee01312bf7c58d6618d6d7981db8e7fc3c4f54ff"

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
body = "\n".join(source_lines[149:162])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != P406_SHA:
    raise SystemExit("p.406 S0 segment hash mismatch")

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
for segment_id in (P405, P406, P407, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"missing segment: {segment_id}")
if segment_by_id[P406]["sha256"] != P406_SHA or segment_by_id[P406]["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("p.406 S0 registration changed")
if (coverage_by_id[P405]["disposition"], coverage_by_id[P405]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.405 must be reviewed/partial before its continuation is closed")
if (coverage_by_id[P406]["disposition"], coverage_by_id[P406]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.406 is not queued/pending")
if (coverage_by_id[P407]["disposition"], coverage_by_id[P407]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.407 must remain queued/pending")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("postscript notes segment must remain queued")

# New S2 candidates are only for distinct, semantically necessary objects not
# safely represented by a current candidate. Suspected matches remain linked
# as unresolved references for S3 instead of being merged here.
candidate_specs = [
    ("cand-11081", "Ivanov (author of the p.406 survey; identity unresolved)", "person", "Surname-only author in the body. Keep distinct from N. Ivanov candidate cand-8264 pending note/bibliography review and S3.", 153),
    ("cand-11082", "Ivanov's survey of contemporary French interest in eighteenth-century Venetian art", "archive", "Survey described in the body; footnote 2 and bibliography remain queued, and the cited work was not independently consulted.", 153),
    ("cand-11083", "French interest in eighteenth-century Venetian art", "term", "The subject as described by Haskell; do not infer a specific exhibition, institution, or individual French patron.", 153),
    ("cand-11084", "Giovanni Antonio Pellegrini's frescoes in the Zwinger at Dresden", "work", "Haskell's p.406 retrospective says Pellegrini did paint the frescoes for which he had been proposed. Keep related to, but distinct from, the earlier unidentified proposed room-decoration candidate cand-9077 pending S3/source review.", 155),
    ("cand-11085", "Article on Antonio Bellucci in Vienna and the Liechtenstein palace decorations", "archive", "Descriptive article reference in the body; the author and exact bibliographic identity await footnote 5 and bibliography review.", 155),
    ("cand-11086", "Tessin (surname-only in the p.406 discussion; identity unresolved)", "person", "The index includes Nicodemus Tessin the Younger at p.406 while the cited Bjurström article concerns Carl Gustaf Tessin. Do not choose or merge either identity until source and bibliography review/S3.", 156),
    ("cand-11087", "Eighteenth-century Russian court", "institution", "Collective court named as an organized patronage context; keep distinct from a modern Russian state entity.", 157),
    ("cand-11088", "1948 book about Giuseppe Valeriani and the Venetian artists attracted by the Russian court", "archive", "Book described in the body; author, title, and bibliographic identity await footnote 7 and bibliography review.", 157),
    ("cand-11089", "Two later articles on the Russian court's interest in Venetian artists", "archive", "The body describes two further articles collectively without titles or authors; keep them grouped only as a source description until notes/bibliography permit separation.", 157),
    ("cand-11090", "Giambattista Tiepolo's Banquet of Cleopatra (Plate 61b)", "work", "Work identified by title and plate reference. Keep distinct from cand-9162, whose candidate label folds in the earlier Catherine-purchase claim that Haskell now calls over-confident.", 158),
    ("cand-11091", "Joseph Smith's 'second collection' problem", "term", "Haskell's label for the unresolved discrepancy involving several hundred paintings recorded in Smith's palace in 1770. This is a historiographic problem/group reference, not a uniquely identified collection object.", 161),
    ("cand-11092", "Frances Vivian's scholarship on Consul Joseph Smith as merchant and collector", "archive", "The body refers collectively to articles and a book, without naming them here; footnote 9 and bibliography reconciliation remain pending.", 160),
    ("cand-11093", "Jeffrey Daniels", "person", "Full name opening the next discussion at p.406 L162; keep distinct from surname-only p.405 Daniels candidate cand-11074 pending S3.", 162),
]

natural_keys = {(row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold()) for row in candidates}
for candidate_id, name, kind, detail, line_number in candidate_specs:
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
        "candidate_source_ref": f"{P406}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

# Candidate ID, exact S0 surface, first line, last line, occurrence, note.
mention_specs = [
    ("cand-11080", "four more possibly still to be discovered", 151, 151, 0, "Continuation of the p.405 group-level catalogue claim; four additional possible pictures are not individually identified."),
    ("cand-11078", "Mazza", 152, 152, 0, "Reuse Barbara Mazza candidate from the p.405 sentence being closed."),
    ("cand-1466", "McSwiny", 152, 152, 0, "Possessive reference to Owen McSwiny in the p.405/p.406 commemorative-picture discussion."),
    ("cand-11081", "Ivanov", 153, 153, 0, "Surname-only author; do not align automatically with cand-8264."),
    ("cand-11083", "contemporary French interest in eighteenthcentury Venetian art", 153, 153, 0, "Subject of the survey; preserve S0 OCR surface here and record the hyphen correction on the statement."),
    ("cand-2719", "Venetian", 153, 153, 0, "Adjectival reference to Venetian art; reuse the broad indexed Venice candidate provisionally pending S3."),
    ("cand-9343", "authoritative account by", 153, 153, 0, "The described Garas account; note 3 remains queued and its exact bibliography identity remains pending."),
    ("cand-9342", "Garas", 154, 154, 0, "Surname-only scholar reference; identity remains unresolved."),
    ("cand-1862", "Pellegrini", 154, 154, 0, "Reuse the Giovanni Antonio Pellegrini candidate."),
    ("cand-9054", "destroyed decoration of the Banque Royale", 154, 154, 0, "Related to the indexed ceiling candidate; p.406 says decoration generally, so exact architectural scope remains unresolved."),
    ("cand-8965", "Banque Royale", 154, 154, 0, "Reuse the institution candidate for the Paris bank."),
    ("cand-4653", "Paris", 154, 154, 0, "Place of the Banque Royale."),
    ("cand-9343", "same article", 155, 155, 0, "Anaphoric reference to the Garas 1962 article cited immediately before; bibliography reconciliation remains pending."),
    ("cand-9342", "Garas", 155, 155, 0, "Surname-only scholar reference."),
    ("cand-1862", "Pellegrini", 155, 155, 0, "Reuse the indexed artist candidate."),
    ("cand-2772", "Vienna", 155, 155, 0, "Place in which Garas's same article discusses Pellegrini's employment."),
    ("cand-9456", "another article on him in Germany", 155, 155, 0, "Reuse the locally matched 1971 Garas article candidate; 'him' refers to Pellegrini."),
    ("cand-1862", "him", 155, 155, 0, "Anaphoric reference to Pellegrini."),
    ("cand-5529", "Germany", 155, 155, 0, "Place context for the second article."),
    ("cand-11084", "frescoes in the Zwinger", 155, 155, 0, "Executed frescoes as reported on p.406; possible match to earlier proposal cand-9077 remains unresolved."),
    ("cand-9076", "Zwinger", 155, 155, 0, "Reuse the place candidate for the Dresden pavilion."),
    ("cand-0947", "Dresden", 155, 155, 0, "Reuse the indexed place candidate."),
    ("cand-9054", "work in Paris", 155, 155, 0, "Anaphoric reference to Pellegrini's Banque Royale decoration; exact scope remains unresolved."),
    ("cand-0282", "Bellucci", 155, 155, 0, "Reuse Antonio Bellucci candidate."),
    ("cand-2772", "Vienna", 155, 155, 1, "Place of the Bellucci article and palace decorations."),
    ("cand-6604", "Liechtenstein palace", 155, 155, 0, "Reuse the unidentified Vienna palace candidate; do not merge with the Liechtenstein family candidate cand-1407."),
    ("cand-0282", "the artist", 155, 155, 0, "Anaphoric reference to Bellucci, not Pellegrini."),
    ("cand-11086", "Tessin", 156, 156, 0, "Surname-only referent; index and bibliographic evidence conflict over which Tessin is meant."),
    ("cand-7076", "Bjurstrom", 156, 156, 0, "Reuse Per Bjurström person candidate; the printed name has an umlaut, recorded as an OCR correction below."),
    ("cand-11086", "him", 156, 156, 0, "Anaphoric reference to the unresolved Tessin referent."),
    ("cand-11087", "eighteenth-century Russian court", 157, 157, 0, "Collective patronage institution/context described in the body."),
    ("cand-2719", "Venice", 157, 157, 0, "Origin named for the artists attracted to the court; use the existing indexed city candidate pending global alignment."),
    ("cand-9382", "Giuseppe Valeriani", 157, 157, 0, "Reuse the individual Giuseppe Valeriani candidate; keep separate from combined index candidate cand-2679 pending S3."),
    ("cand-11088", "fully documented book about Giuseppe Valeriani in 1948", 157, 157, 0, "Descriptive publication reference; the cited book has not been independently consulted."),
    ("cand-11089", "two further articles", 157, 157, 0, "Collective reference to two later articles; the body does not name them."),
    ("cand-0609", "Catherine the Great", 157, 157, 0, "Reuse the indexed historical person candidate."),
    ("cand-2569", "Tiepolo", 158, 158, 0, "Reuse the indexed artist candidate."),
    ("cand-11090", "Banquet of Cleopatra", 158, 158, 0, "Specific painting title; keep distinct from cand-9162's purchase-claim candidate until S3 reconciliation."),
    ("cand-11090", "Plate 61b", 158, 158, 0, "Internal plate reference to the same painting."),
    ("cand-11092", "In some articles and a book", 160, 160, 0, "Collective description of Frances Vivian's scholarship; publication identities await footnote 9 and bibliography review."),
    ("cand-9553", "Frances Vivian", 160, 160, 0, "Reuse Frances Vivian candidate."),
    ("cand-2440", "Consul Smith", 161, 161, 0, "Reuse the Joseph Smith candidate whose index entry covers p.406."),
    ("cand-2440", "Smith", 161, 161, 0, "Reuse Joseph Smith candidate in the second-collection reference."),
    ("cand-11091", "second collection", 161, 161, 0, "The unresolved problem label, not a claim that a formally identified collection existed."),
    ("cand-11091", "several hundred paintings", 162, 162, 0, "Description of the paintings recorded in the palace in 1770; exact inventory and object identities remain unresolved."),
    ("cand-11091", "Appendix 5", 162, 162, 0, "Internal cross-reference to the book's appendix, already processed in S2; see the linked p.391-p.394 segments."),
    ("cand-2440", "his palace", 162, 162, 0, "Possessive reference to Joseph Smith."),
    ("cand-1141", "George III", 162, 162, 0, "Reuse the indexed king candidate."),
    ("cand-9178", "sold all his pictures", 162, 162, 0, "The phrase reports what Smith was believed to have sold; Vivian and Haskell question whether that sale included all pictures."),
    ("cand-9553", "she", 162, 162, 1, "Anaphoric reference to Frances Vivian in her attributed interpretation."),
    ("cand-9553", "she~argues", 162, 162, 0, "S0 OCR inserts a tilde at the line-level word break; printed reading is 'she argues'. The pronoun refers to Frances Vivian and the argument remains attributed."),
    ("cand-11093", "Jeffrey Daniels", 162, 162, 0, "Name opens the next sentence/discussion, which continues on p.407; distinct from p.405 surname-only Daniels pending S3."),
]

line_offsets = {}
cursor = 0
for line_number in range(150, 163):
    line_offsets[line_number] = cursor
    cursor += len(source_lines[line_number - 1]) + 1
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for index, (candidate_id, surface, first_line, last_line, occurrence, note) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p406-{index:03d}"
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
    new_mentions.append({"mention_id": mention_id, "segment_id": P406, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(position),
                         "end_char": str(position + len(surface)), "note": note})
    mention_ids.add(mention_id)

note_lines = {1: 259, 2: 259, 3: 260, 4: 260, 5: 261, 6: 261, 7: 262, 8: 262, 9: 263}


def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer, qualification, ids,
                   note_markers=(), relation=True, extra=None):
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 406,
                  "pdf_physical_page": 15, "claim": claim, "speaker": speaker, "text_layer": layer,
                  "qualification": qualification, "mentioned_candidate_ids": ids,
                  "relation_candidate": relation}
    if note_markers:
        qualifiers.update({"footnote_markers": list(note_markers), "footnote_text_pending": True,
                           "footnote_segment": NOTES,
                           "footnote_refs": [{"marker": n, "segment_id": NOTES, "source_line": note_lines[n]} for n in note_markers],
                           "footnote_statement_ids": [], "footnote_body_link_status": "pending"})
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": P406, "subject_candidate_id": subject,
            "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": "\n".join(source_lines[first - 1:last]),
            "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "origin": "book"}


new_statements = [
    make_statement("st-chp20-p406-mazza-mcswiny-catalogue-coverage", 151, 152, "cand-11078", "cand-11080",
                   "catalogued_identified_originals_and_copies_of_mcswiny_pictures",
                   "Haskell says Mazza's detailed catalogue covers all commemorative pictures then identified, whether originals or copies, with four more possibly still to be discovered; it replaces Haskell's 1963 summary list. Haskell says Mazza was as baffled as he and McSwiny's contemporaries by the pictures' meaning.",
                   "Haskell reporting Barbara Mazza and comparing his earlier edition", "authorial report and retrospective comparison",
                   "The source does not identify the four possible pictures individually or settle the meaning of the group. Footnote 1 remains queued; Mazza's catalogue was not independently consulted.",
                   ["cand-11078", "cand-11079", "cand-11080", "cand-1466"], [1], True,
                   {"cited_material_not_independently_consulted": True,
                    "cross_reference_segments": [{"segment_id": P405, "source_line_start": 148, "source_line_end": 148}],
                    "cross_reference_statement_ids": ["st-chp20-p405-mazza-mcswiny-pictures-catalogue-open"]}),
    make_statement("st-chp20-p406-ivanov-french-interest-survey", 153, 153, "cand-11082", "cand-11083",
                   "surveyed_contemporary_french_interest_in_venetian_art",
                   "Haskell describes Ivanov's survey of contemporary French interest in eighteenth-century Venetian art as useful.",
                   "Haskell", "authorial assessment of later scholarship",
                   "The assessment is Haskell's; the survey's author identity, exact title, and scope await footnote 2 and bibliography review. The source was not independently consulted.",
                   ["cand-11081", "cand-11082", "cand-11083", "cand-2719"], [2], True,
                   {"cited_material_not_independently_consulted": True,
                    "related_candidate_ids_pending_alignment": ["cand-8264"],
                    "ocr_corrections": [{"source_line": 153, "ocr": "eighteenthcentury", "print": "eighteenth-century", "basis": "CHP-20Postscript.pdf physical page 15 image"}]}),
    make_statement("st-chp20-p406-garas-banque-royale-account", 153, 154, "cand-9343", "cand-9054",
                   "account_of_destroyed_banque_royale_decoration",
                   "Haskell calls Garas's account the most important contribution accessible since his book appeared and says it documents what can now be ascertained about Pellegrini's destroyed Banque Royale decoration; Garas considers its influence overestimated.",
                   "Haskell reporting Garas", "authorial assessment and report of scholarship",
                   "The body says 'decoration' and does not resolve its exact architectural scope; do not equate it automatically with the separately described Mississippi Gallery. Footnote 3 and bibliographic reconciliation remain pending; the cited article was not independently consulted.",
                   ["cand-9342", "cand-9343", "cand-1862", "cand-9054", "cand-8965", "cand-4653"], [3], True,
                   {"cited_material_not_independently_consulted": True,
                    "related_candidate_ids_pending_alignment": ["cand-8963"],
                    "ocr_corrections": [{"source_line": 154, "ocr": "Pellegrini��s", "print": "Pellegrini’s", "basis": "CHP-20Postscript.pdf physical page 15 image"}]}),
    make_statement("st-chp20-p406-garas-vienna-employment", 155, 155, "cand-9343", "cand-1862",
                   "article_discusses_pellegrini_employment_in_vienna",
                   "Haskell says Garas discusses Pellegrini's employment in Vienna in the same article cited for the Banque Royale account.",
                   "Haskell reporting Garas", "authorial report of scholarship",
                   "This is Haskell's description of the article, not an independently verified employment record. Footnote 3 remains queued.",
                   ["cand-9342", "cand-9343", "cand-1862", "cand-2772"], [3], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p406-garas-zwinger-frescoes", 155, 155, "cand-1862", "cand-11084",
                   "painted_frescoes_at_zwinger_confirmed_in_later_research",
                   "Haskell reports that in another article on Pellegrini in Germany Garas corrected Haskell's first-edition proposal: Pellegrini did paint the Zwinger frescoes in Dresden. Haskell says they survived longer than the Paris work but were destroyed long before Dresden itself was destroyed in 1945.",
                   "Haskell reporting Garas and correcting his first edition", "authorial retrospective correction and report of scholarship",
                   "The p.406 passage links the frescoes to the earlier proposal but does not identify the decorated room; keep the executed frescoes candidate separate from candidate cand-9077 until global identity review. Footnote 4 and the cited article remain unreviewed.",
                   ["cand-1862", "cand-11084", "cand-9076", "cand-0947", "cand-5529", "cand-9054", "cand-9456"], [4], True,
                   {"cited_material_not_independently_consulted": True,
                    "related_candidate_ids_pending_alignment": ["cand-9077"],
                    "ocr_corrections": [{"source_line": 155, "ocr": "Pellegrini��s", "print": "Pellegrini’s", "basis": "CHP-20Postscript.pdf physical page 15 image"}]}),
    make_statement("st-chp20-p406-bellucci-vienna-dates", 155, 155, "cand-11085", "cand-0282",
                   "article_makes_bellucci_vienna_presence_likely_1692_1704",
                   "Haskell says an article on Bellucci in Vienna, especially his Liechtenstein-palace decorations, makes it likely that Bellucci was in the city from 1692 to 1704, earlier than Haskell had suggested.",
                   "Haskell reporting and assessing later scholarship", "authorial report of scholarship",
                   "The date range is presented as likely in the article as summarized by Haskell; the body does not name the article's author or the palace. Footnote 5 and the cited work remain pending.",
                   ["cand-11085", "cand-0282", "cand-2772", "cand-6604"], [5], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p406-bjurstrom-tessin-drawings", 156, 156, "cand-9445", "cand-11086",
                   "discusses_tessin_taste_and_drawing_collecting",
                   "Haskell says Bjurström discussed Tessin's taste in the arts and his standing as a collector of drawings, and supplied bibliographical references to Swedish literature on him.",
                   "Haskell reporting Bjurström", "authorial report of scholarship",
                   "The body gives only the surname Tessin. The p.406 index candidate names Nicodemus Tessin the Younger, while the matched Bjurström article candidate names Carl Gustaf Tessin; retain the identity conflict pending the note and bibliography review/S3. Footnote 6 is queued.",
                   ["cand-7076", "cand-9445", "cand-11086", "cand-2555", "cand-2552"], [6], True,
                   {"cited_material_not_independently_consulted": True,
                    "related_candidate_ids_pending_alignment": ["cand-2553", "cand-2554"],
                    "ocr_corrections": [{"source_line": 156, "ocr": "Bjurstrom", "print": "Bjurström", "basis": "CHP-20Postscript.pdf physical page 15 image"}]}),
    make_statement("st-chp20-p406-russian-court-valeriani-book", 157, 157, "cand-11088", "cand-9382",
                   "book_documents_russian_court_interest_in_venetian_artists",
                   "Haskell says the eighteenth-century Russian court's interest in attracting artists from Venice was investigated in a fully documented 1948 book about Giuseppe Valeriani.",
                   "Haskell", "authorial report of scholarship",
                   "The book's title and authorship await footnote 7 and bibliography review; the combined index candidate cand-2679 is not merged with the individual Giuseppe Valeriani candidate here.",
                   ["cand-11087", "cand-11088", "cand-9382", "cand-2719"], [7], True,
                   {"cited_material_not_independently_consulted": True,
                    "related_candidate_ids_pending_alignment": ["cand-2679"]}),
    make_statement("st-chp20-p406-russian-court-later-articles", 157, 157, "cand-11089", "cand-11087",
                   "later_articles_address_russian_court_interest_in_venetian_artists",
                   "Haskell says two further articles have addressed the eighteenth-century Russian court's interest in attracting Venetian artists in recent years.",
                   "Haskell", "authorial report of scholarship",
                   "The two articles are not named or separated in the body; note 8 and bibliography reconciliation remain pending.",
                   ["cand-11089", "cand-11087", "cand-2719"], [8], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p406-catherine-tiepolo-purchase-reassessment", 157, 158, "cand-0609", "cand-11090",
                   "haskell_reassesses_catherine_purchase_as_overconfident",
                   "Haskell now judges his earlier assumption that Catherine the Great herself purchased Tiepolo's Banquet of Cleopatra (Plate 61b) to have been over-confident.",
                   "Haskell", "authorial retrospective qualification of an earlier claim",
                   "This is a retreat from confidence, not a claim that Catherine did not purchase the painting. The earlier p.298 statement and the claim-bearing candidate cand-9162 must remain visible for later reconciliation; the work title itself is recorded separately from the purchase claim.",
                   ["cand-0609", "cand-2569", "cand-11090", "cand-9162"], (), True,
                   {"cross_reference_segments": [{"segment_id": "chp-10:10_CHP-10_intro:l345-352", "source_line_start": 345, "source_line_end": 352}],
                    "cross_reference_statement_ids": ["st-chp10-p298-catherine-tiepolo-purchase", "st-chp10-p298-banquet-transferred-and-power-balance"],
                    "related_candidate_ids_pending_alignment": ["cand-9162"]}),
    make_statement("st-chp20-p406-vivian-scholarship-and-open-question", 160, 162, "cand-11092", "cand-11091",
                   "vivian_studies_smith_but_does_not_resolve_second_collection_problem",
                   "Haskell says Frances Vivian's articles and book add to knowledge of Consul Smith as merchant and collector but do not solve the 'second collection' problem. He describes several hundred paintings recorded in Smith's palace at his death in 1770, eight years after he was believed to have sold all his pictures to George III.",
                   "Haskell reporting Frances Vivian and the historical record as he understands it", "authorial summary of scholarship and unresolved historical problem",
                   "The existence, contents, and relation of the recorded paintings to the 1762 sale are discussed at length in Appendix 5; this passage summarizes the problem and does not independently establish a complete inventory. Footnote 9 remains queued.",
                   ["cand-11092", "cand-9553", "cand-2440", "cand-11091", "cand-1141", "cand-9178"], [9], True,
                   {"cited_material_not_independently_consulted": True,
                    "cross_reference_segments": [
                        {"segment_id": "chp-19:19_CHP-19Appendix:l109-124", "source_line_start": 109, "source_line_end": 124},
                        {"segment_id": "chp-19:19_CHP-19Appendix:l126-138", "source_line_start": 126, "source_line_end": 138},
                        {"segment_id": "chp-19:19_CHP-19Appendix:l140-155", "source_line_start": 140, "source_line_end": 155},
                        {"segment_id": "chp-19:19_CHP-19Appendix:l157-183", "source_line_start": 157, "source_line_end": 183}],
                    "cross_reference_statement_ids": ["st-chp19-p392-moschini-conflicting-widow-account", "st-chp19-p393-zais-and-1762-sale-uncertainty", "st-chp19-p394-smith-books-history-closure"],
                    "related_candidate_ids_pending_alignment": ["cand-2447", "cand-9278"]}),
    make_statement("st-chp20-p406-vivian-partial-sale-hypothesis", 162, 162, "cand-9553", "cand-11091",
                   "vivian_and_haskell_consider_1762_sale_only_partial",
                   "Haskell says Vivian, like him, is inclined to believe Smith sold only a portion of what he owned in 1762; she therefore argues that the paintings later in his possession had probably been acquired earlier.",
                   "Haskell reporting Vivian and aligning his own view", "authorial report of a scholar's qualified interpretation",
                   "Both the partial-sale interpretation and the earlier-acquisition explanation are presented as probability, not settled fact. Preserve Vivian's argument, Haskell's agreement, and the unresolved Appendix 5 evidence chain.",
                   ["cand-9553", "cand-2440", "cand-11091", "cand-9178", "cand-1141"], [9], True,
                   {"cited_material_not_independently_consulted": True,
                    "cross_reference_segments": [{"segment_id": "chp-19:19_CHP-19Appendix:l109-124", "source_line_start": 109, "source_line_end": 124},
                                                  {"segment_id": "chp-19:19_CHP-19Appendix:l126-138", "source_line_start": 126, "source_line_end": 138}],
                    "cross_reference_statement_ids": ["st-chp19-p392-moschini-conflicting-widow-account", "st-chp19-p393-zais-and-1762-sale-uncertainty"],
                    "ocr_corrections": [{"source_line": 162, "ocr": ", - Appendix 5)��i.e.", "print": "Appendix 5)—i.e.", "basis": "CHP-20Postscript.pdf physical page 15 image"}]}),
]

# Close the p.405 catalogue statement with the continuation on p.406.
prior_statement_id = "st-chp20-p405-mazza-mcswiny-pictures-catalogue-open"
prior_statement = next((row for row in statements if row["statement_id"] == prior_statement_id), None)
if prior_statement is None:
    raise SystemExit("p.405 open catalogue statement is missing")
prior_q = prior_statement["qualifiers"]
prior_q["claim"] = "Haskell says Barbara Mazza made a full survey of literature about commemorative pictures painted for Owen McSwiny; some had emerged since his first edition, Mazza's conclusions confirmed his own, and her detailed catalogue covered all then-identified examples as originals or copies, with four more possibly still to be discovered, replacing his 1963 summary list. Haskell says Mazza was as baffled as he and McSwiny's contemporaries by the pictures' meaning."
prior_q["qualification"] = "The picture group and the four possible additional works remain unidentified individually. The continuation on p.406 L151-152 closes the sentence; footnote 1 is in the queued notes segment. The cited catalogue was not independently consulted."
prior_q.pop("open_across_segment", None)
prior_q.pop("continues_in_segment", None)
prior_q["cross_reference_segments"] = [{"segment_id": P406, "source_line_start": 151, "source_line_end": 152}]
prior_q["footnote_markers"] = [1]
prior_q["footnote_text_pending"] = True
prior_q["footnote_segment"] = NOTES
prior_q["footnote_refs"] = [{"marker": 1, "segment_id": NOTES, "source_line": 259}]
prior_q["footnote_statement_ids"] = []
prior_q["footnote_body_link_status"] = "pending"

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

all_mentions = mentions + new_mentions
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
               for row in all_mentions if row["segment_id"] == P406)
for index, left in enumerate(spans):
    for right in spans[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"crossing/duplicate mention spans: {left[2]} / {right[2]}")

coverage_by_id[P405]["disposition"] = "reviewed"
coverage_by_id[P405]["migration_status"] = "complete"
coverage_by_id[P405]["note"] = "Printed p.405 (PDF physical page 14) checked against page image; its final Mazza catalogue sentence is closed by p.406 L151-152. Footnote 1 remains linked to queued notes L259."
coverage_by_id[P406]["disposition"] = "reviewed"
coverage_by_id[P406]["migration_status"] = "partial"
coverage_by_id[P406]["source_line_ranges"] = "L150-162"
coverage_by_id[P406]["note"] = "Printed p.406 (PDF physical page 15) checked against page image. The p.405 Mazza sentence closes at L152; notes 1-9 map to queued notes L259-263. L162 names Jeffrey Daniels at the start of a discussion continuing on p.407, so this segment remains partial."

paths = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP) for path in paths]
if ARGS.apply:
    if any(path.exists() for path in backups):
        raise SystemExit("p.406 recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied p.406 S2 migration; backup suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates={len(candidate_specs)}; new mentions={len(new_mentions)}; new statements={len(new_statements)}")
    print("p.405 continuation, p.406 source/PDF/S0 hashes, source spans, note links, candidate foreign keys, and mention overlaps validated")
