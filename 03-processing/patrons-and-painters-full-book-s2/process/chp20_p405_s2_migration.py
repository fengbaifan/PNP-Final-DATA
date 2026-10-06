#!/usr/bin/env python3
"""Controlled S2 migration for printed p.405 (PDF physical p.14)."""
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
P404 = "chp-20:20_CHP-20Postscript:l123-135"
P405 = "chp-20:20_CHP-20Postscript:l137-148"
P406 = "chp-20:20_CHP-20Postscript:l150-162"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
BACKUP = ".bak-s2-chp20-p405-20261004"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
P405_SHA = "5ada37a54a0e70ce7e257cfe9b31d233e650475e513dc0f5175ad8aa3810a011"

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
body = "\n".join(source_lines[136:148])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != P405_SHA:
    raise SystemExit("p.405 S0 segment hash mismatch")

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
for segment_id in (P404, P405, P406, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"missing segment: {segment_id}")
if segment_by_id[P405]["sha256"] != P405_SHA or segment_by_id[P405]["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("p.405 S0 registration changed")
if coverage_by_id[P404]["migration_status"] != "complete":
    raise SystemExit("p.404 must be complete before p.405")
if (coverage_by_id[P405]["disposition"], coverage_by_id[P405]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.405 is not queued/pending")
if (coverage_by_id[P406]["disposition"], coverage_by_id[P406]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.406 continuation segment is not queued/pending")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("postscript notes segment must remain queued")

candidate_specs = [
    ("cand-11059", "James C. Davis", "person", "Full name as printed; cross-chapter identity alignment remains for S3.", 141),
    ("cand-11060", "James C. Davis's study of the political and economic situation of the Venetian aristocracy", "archive", "A scholarly work described in the body; note 2 and bibliography details remain queued and the cited work was not independently consulted.", 141),
    ("cand-11061", "Venetian aristocracy in the last phase of its ascendancy (p.405 group reference)", "term", "Haskell describes diminishing numbers and wealth. Keep distinct from the older-aristocracy and newer-mercantile-group candidates cand-8137 and cand-8179 pending global alignment.", 140),
    ("cand-11062", "Pallucchini (editor cited by surname on p.405)", "person", "Surname-only person mention; do not align with the separate p.355-note candidate cand-10319 before S3. Note 3 remains queued.", 142),
    ("cand-11063", "Pallucchini-edited volume on country-villa decoration", "archive", "A volume described in the body as making recent investigations conveniently accessible. Note 3 and bibliography details remain queued; not independently consulted.", 142),
    ("cand-11064", "Study of Zenobio family patronage cited by Haskell on p.405", "archive", "The body says the family patronage was studied in some detail; note 4 remains queued, so author, title, and publication details are unresolved.", 142),
    ("cand-11065", "Puppi (scholar cited by surname on p.405)", "person", "Surname-only person mention in two closely related claims; full identity and relation to other Puppi candidates await S3. Notes 5-6 remain queued.", 142),
    ("cand-11066", "Puppi research on Valmarana and Cordellina patronage", "archive", "A scholarly source described in the body; notes 5-6 and bibliography reconciliation remain queued, and the cited material was not independently consulted.", 142),
    ("cand-11067", "Conte Giustino Valmarana", "person", "Named as the actual commissioner of the Valmarana frescoes in Haskell's retrospective correction; identity alignment remains for S3.", 143),
    ("cand-11068", "Local nobility in Haskell's p.405 comparison of Tiepolo's usual work", "term", "Unnamed patron group; do not assume it is identical to the broader Venetian-aristocracy referent on this page.", 143),
    ("cand-11069", "Palace in Vicenza begun by Carlo Cordellina in 1770", "place", "The passage does not give a formal name. It may correspond to the earlier unidentified Vicenza house candidate cand-8375, but keep separate pending source and identity review.", 143),
    ("cand-11070", "Croft-Murray's second volume of Decorative Painting in England", "archive", "Book identified descriptively in the body; note 7 and bibliography details remain queued. Possible relation to p.403 archive candidate cand-11002 is not resolved here.", 146),
    ("cand-11071", "The Riccis (collective artist reference on p.405)", "term", "Plural surname in a group list; do not resolve its members or equate it with Sebastiano Ricci alone.", 146),
    ("cand-11072", "Other Venetian artists attracted to Britain (group reference on p.405)", "term", "The passage gives a collective description without identifying all members.", 146),
    ("cand-11073", "Britain as destination in Haskell's p.405 account of Venetian artists", "place", "Geographic destination as phrased in the body; keep distinct from polity uses elsewhere pending global alignment.", 146),
    ("cand-11074", "Daniels (scholar cited by surname on p.405)", "person", "Surname-only author; identity alignment awaits S3. Note 8 remains queued.", 147),
    ("cand-11075", "Daniels's monograph on Sebastiano Ricci", "archive", "A monograph described in the body; note 8 and bibliography details remain queued and it was not independently consulted.", 147),
    ("cand-11076", "Shipley (writer cited by surname on p.405)", "person", "Surname-only author; identity alignment awaits S3. Note 9 remains queued.", 148),
    ("cand-11077", "Shipley's article on hostility toward Amigoni", "archive", "Article described in the body; note 9 and bibliographic details remain queued and it was not independently consulted.", 148),
    ("cand-11078", "Barbara Mazza", "person", "Full name as printed; identity alignment remains for S3.", 148),
    ("cand-11079", "Mazza's survey and catalogue of commemorative pictures for Owen McSwiny", "archive", "Scholarly survey/catalogue described across p.405-406; its footnote marker appears on p.406 and remains pending until that segment and notes are read.", 148),
    ("cand-11080", "Commemorative pictures painted for Owen McSwiny (group reference on p.405)", "work", "Group-level work reference; p.406 continues the catalogue description. Do not identify it with the British Worthies project candidate cand-9007 without evidence.", 148),
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
        "candidate_source_ref": f"{P405}#L{line_number}",
    }
    candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

# Candidate ID, exact S0 surface, first line, last line, occurrence, note.
mention_specs = [
    ("cand-0833", "Stefano Conti", 138, 138, 0, "Reuse the indexed Stefano Conti candidate; his commission is already described on p.228."),
    ("cand-0871", "Crespi", 138, 138, 0, "Reuse the indexed artist candidate; this is the same Jupiter/Corybantes painting discussed on p.228 and captioned on Plate 67."),
    ("cand-0879", "Jupiter among the Corybantes", 138, 138, 0, "Specific painting; reuse the index and Plate 67 candidate. Keep the separate p.222 same-title candidate cand-7720 unmerged pending S3."),
    ("cand-0879", "The Finding of Moses", 138, 138, 0, "Alternate title in Haskell's p.405 report; see the p.228 report and preserve the source's customs-duty explanation."),
    ("cand-0833", "him", 138, 138, 0, "Pronoun refers to Stefano Conti, who described the subject under the alternate title."),
    ("cand-0879", "Plate 67", 138, 138, 0, "Internal plate reference to the same work candidate; Plate 67 caption was processed separately."),
    ("cand-11061", "Venetian aristocracy", 140, 140, 0, "Group named in Haskell's summary of political and economic decline."),
    ("cand-11061", "its", 140, 140, 0, "Anaphoric reference to the Venetian aristocracy."),
    ("cand-11059", "James C. Davis", 141, 141, 0, "Full author name; identity alignment remains for S3."),
    ("cand-11061", "its", 141, 141, 0, "Anaphoric reference to the Venetian aristocracy and its artistic patronage."),
    ("cand-11063", "a volume edited by\nPallucchini", 141, 142, 0, "The edited volume is described but its title is not given in the body."),
    ("cand-11062", "Pallucchini", 142, 142, 0, "Surname-only editor mention; bibliography and cross-chapter identity remain unresolved."),
    ("cand-2870", "the Zenobio", 142, 142, 0, "Reuse the indexed Zenobio family candidate; the passage concerns its patronage."),
    ("cand-11065", "Puppi", 142, 142, 0, "Surname-only scholar mention; identity is not inferred from the notes."),
    ("cand-2689", "Leonardo Valmarana", 142, 142, 0, "Reuse the existing person candidate. P.405 corrects Haskell's earlier attribution of the commission; it does not claim Leonardo was not family head."),
    ("cand-2569", "Tiepolo", 142, 142, 0, "Reuse the indexed artist candidate."),
    ("cand-2594", "Tiepolo’s frescoes", 142, 142, 0, "Reuse the indexed Valmarana fresco-cycle candidate."),
    ("cand-2688", "the family", 142, 142, 0, "Anaphoric reference to the Valmarana family in the adjoining account."),
    ("cand-8444", "Villa near Vicenza", 143, 143, 0, "Reuse the existing Villa Valmarana place candidate; exact spatial complex remains as previously qualified."),
    ("cand-2769", "Vicenza", 143, 143, 0, "Reuse the indexed place candidate."),
    ("cand-8442", "Homer", 143, 143, 0, "Reuse the candidate for the named literary source of fresco subjects."),
    ("cand-2777", "Virgil", 143, 143, 0, "Reuse the indexed literary figure candidate."),
    ("cand-0116", "Ariosto", 143, 143, 0, "Reuse the indexed Ariosto candidate; the source names scenes, not a specific work title."),
    ("cand-2544", "Tasso", 143, 143, 0, "Reuse the indexed Tasso candidate; the source names scenes, not a specific work title."),
    ("cand-2594", "These beautiful works", 143, 143, 0, "Anaphoric reference to the Valmarana fresco cycle."),
    ("cand-2569", "Tiepolo", 143, 143, 0, "Second person-name mention in the p.405 discussion."),
    ("cand-11068", "local nobility", 143, 143, 0, "Unnamed patron group in Haskell's stylistic comparison."),
    ("cand-11067", "Conte Giustino Valmarana", 143, 143, 0, "Reuse is not available for this named individual; record as a new person candidate pending S3."),
    ("cand-11067", "who", 143, 143, 0, "Relative pronoun refers to Giustino Valmarana."),
    ("cand-11067", "whom", 143, 143, 0, "Anaphoric reference to Giustino Valmarana."),
    ("cand-11067", "he", 143, 143, 0, "Refers to Giustino Valmarana, described as rich, efficient, and retiring."),
    ("cand-11065", "Puppi", 143, 143, 0, "Second surname-only mention of the scholar."),
    ("cand-0842", "Carlo Cordellina", 143, 143, 0, "Reuse the indexed person candidate."),
    ("cand-2569", "Tiepolo", 143, 143, 1, "Tiepolo is described as another artist employed by Cordellina."),
    ("cand-11069", "palace in\nVicenza", 143, 144, 0, "Unnamed palace begun by Cordellina in 1770; possible link to cand-8375 is recorded but not resolved."),
    ("cand-2769", "Vicenza", 144, 144, 0, "Place named as the palace location."),
    ("cand-0842", "he", 144, 144, 0, "First Cordellina anaphor: he began building the Vicenza palace in 1770."),
    ("cand-0842", "he", 144, 144, 1, "Second Cordellina anaphor: Haskell says he died at the palace eighteen years later."),
    ("cand-11070", "The second volume of Croft-Murray’s book on Decorative Painting in England", 146, 146, 0, "Descriptive reference to Croft-Murray's book; bibliography reconciliation remains pending."),
    ("cand-11001", "Croft-Murray", 146, 146, 0, "Reuse p.403 surname-only author candidate within the same postscript; global identity alignment remains for S3."),
    ("cand-11071", "the Riccis", 146, 146, 0, "Collective plural reference; members remain unresolved."),
    ("cand-1870", "Pellegrini", 146, 146, 0, "Reuse the indexed entry for Pellegrini's work in England."),
    ("cand-0094", "Amigoni", 146, 146, 0, "Reuse the indexed artist candidate."),
    ("cand-0282", "Bellucci", 146, 146, 0, "Reuse the indexed artist candidate."),
    ("cand-11072", "other Venetians who were attracted to Britain", 146, 146, 0, "Collective group reference; membership is not enumerated."),
    ("cand-11073", "Britain", 146, 146, 0, "Geographic destination in the account of Venetian artists."),
    ("cand-2154", "Sebastiano Ricci", 147, 147, 0, "Reuse the indexed person candidate."),
    ("cand-11074", "Daniels", 147, 147, 0, "Surname-only monograph author; identity alignment remains for S3."),
    ("cand-11075", "monograph on him", 147, 147, 0, "The monograph is on Sebastiano Ricci; him refers to Ricci."),
    ("cand-2154", "him", 147, 147, 0, "Anaphoric reference to Sebastiano Ricci."),
    ("cand-0094", "Amigoni", 147, 147, 0, "Reuse the indexed artist candidate."),
    ("cand-11077", "article by Shipley", 148, 148, 0, "Article described in the body; its exact bibliographic identity awaits note 9."),
    ("cand-11076", "Shipley", 148, 148, 0, "Surname-only article author; identity alignment remains for S3."),
    ("cand-11078", "Barbara Mazza", 148, 148, 0, "Full author name."),
    ("cand-11079", "a full survey of all the literature relating to the commemorative pictures painted for Owen McSwiny", 148, 148, 0, "Mazza's described survey/catalogue; its page-end citation appears in the continuation."),
    ("cand-11080", "the commemorative pictures painted for Owen McSwiny", 148, 148, 0, "Group of works discussed; do not equate with cand-9007 without evidence."),
    ("cand-1466", "Owen McSwiny", 148, 148, 0, "Reuse the indexed person candidate."),
    ("cand-11080", "some of which", 148, 148, 0, "Anaphoric reference most likely to the pictures; the scope is left open for p.406 continuation review."),
    ("cand-11078", "Her", 148, 148, 0, "Anaphoric reference to Barbara Mazza."),
    ("cand-11079", "her detailed catalogue", 148, 148, 0, "Anaphoric reference to Mazza's survey/catalogue."),
    ("cand-11080", "all those at", 148, 148, 0, "Open phrase beginning the catalogue's enumeration; it continues on p.406."),
]

line_offsets = {}
cursor = 0
for line_number in range(137, 149):
    line_offsets[line_number] = cursor
    cursor += len(source_lines[line_number - 1]) + 1
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for index, (candidate_id, surface, first_line, last_line, occurrence, note) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p405-{index:03d}"
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
    new_mentions.append({"mention_id": mention_id, "segment_id": P405, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(position),
                         "end_char": str(position + len(surface)), "note": note})
    mention_ids.add(mention_id)

note_lines = {1: 254, 2: 254, 3: 255, 4: 255, 5: 256, 6: 256, 7: 257, 8: 257, 9: 258}


def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer, qualification, ids,
                   note_markers=(), relation=False, extra=None):
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 405,
                  "pdf_physical_page": 14, "claim": claim, "speaker": speaker, "text_layer": layer,
                  "qualification": qualification, "mentioned_candidate_ids": ids,
                  "relation_candidate": relation}
    if note_markers:
        qualifiers.update({"footnote_markers": list(note_markers), "footnote_text_pending": True,
                           "footnote_segment": NOTES,
                           "footnote_refs": [{"marker": n, "segment_id": NOTES, "source_line": note_lines[n]} for n in note_markers],
                           "footnote_statement_ids": [], "footnote_body_link_status": "pending"})
    if extra:
        qualifiers.update(extra)
    return {"statement_id": statement_id, "segment_id": P405, "subject_candidate_id": subject,
            "object_candidate_id": obj, "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": "\n".join(source_lines[first - 1:last]),
            "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "origin": "book"}


new_statements = [
    make_statement("st-chp20-p405-conti-crespi-jupiter-commission-found", 138, 138, "cand-0833", "cand-0879",
                   "commissioned_crespi_jupiter_corybantes_picture_later_found",
                   "Haskell says Stefano Conti's last commission was a Crespi picture of Jupiter among the Corybantes, deliberately described by Conti as The Finding of Moses because sacred subjects incurred lower customs duty; a picture previously known to Haskell only from documentary sources had now turned up.",
                   "Haskell", "authorial postscript report of documentary discovery",
                   "Retain Haskell's report and attributed motive; the cited footnote 1 remains queued and the picture's documentary source/current location has not been independently checked. Reuse p.228's specific Jupiter/Corybantes work candidate cand-0879 and keep p.222 candidate cand-7720 separate pending S3.",
                   ["cand-0833", "cand-0871", "cand-0879"], [1], True,
                   {"cited_material_not_independently_consulted": True,
                    "cross_reference_segments": [
                        {"segment_id": "chp-8:08_CHP-8_sec_ii:l206-214", "source_line_start": 206, "source_line_end": 211},
                        {"segment_id": "chp-20:20_CHP-20Postscript:l72-76", "source_line_start": 73, "source_line_end": 76}],
                    "cross_reference_statement_ids": ["st-chp8-p228-crespi-1728-commission", "st-chp8-p228-crespi-chosen-subject-sketch", "st-chp8-p228-crespi-retitles-finding-of-moses", "st-chp20-plate67-crespi-jupiter-cybele"],
                    "related_candidate_ids_pending_alignment": ["cand-7720"],
                    "ocr_corrections": []}),
    make_statement("st-chp20-p405-davis-venetian-aristocracy", 140, 141, "cand-11059", "cand-11061",
                   "discussed_political_and_economic_situation",
                   "Haskell says James C. Davis had discussed the political and economic situation of the Venetian aristocracy in the final phase of its ascendancy, when its numbers and wealth were diminishing.",
                   "Haskell", "authorial report of scholarship",
                   "The interpretation and demographic/economic characterization are attributed to Haskell's summary of Davis; footnote 2 remains queued and the cited work was not independently consulted.",
                   ["cand-11059", "cand-11060", "cand-11061"], [2], True,
                   {"cited_material_not_independently_consulted": True,
                    "ocr_corrections": [{"source_line": 140, "ocr": "lastjahase", "print": "last phase", "basis": "CHP-20Postscript.pdf physical page 14 image"}]}),
    make_statement("st-chp20-p405-country-villa-research-pallucchini-volume", 141, 142, None, "cand-11063",
                   "edited_volume_makes_country_villa_research_accessible",
                   "Haskell says incidental information about artistic patronage can be derived from artist monographs and recent investigations into country-villa decoration, much of which was made conveniently accessible in a volume edited by Pallucchini.",
                   "Haskell", "authorial synthesis of research literature",
                   "The work's title and exact contents are not stated in the body; footnote 3 remains queued and the volume was not independently consulted.",
                   ["cand-11062", "cand-11063"], [3], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p405-zenobio-patronage-study", 142, 142, "cand-11064", "cand-2870",
                   "studied_patronage_of_zenobio_family",
                   "Haskell says the patronage of the Zenobio family had been examined in some detail.",
                   "Haskell", "authorial report of scholarship",
                   "The study's author and bibliographic identity await note 4; neither its findings nor the family identity are independently verified here.",
                   ["cand-11064", "cand-2870"], [4], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p405-puppi-corrects-valmarana-fresco-commission", 142, 144, "cand-11067", "cand-2594",
                   "commissioned_valmarana_frescoes_not_leonardo_valmarana",
                   "Haskell says Puppi demonstrated that Haskell had been wrong to attribute the commissioning of Tiepolo's Valmarana frescoes to Leonardo Valmarana; the works were in fact commissioned by Conte Giustino Valmarana, who died in 1757 and is described as rich, efficient, and retiring.",
                   "Haskell reporting Puppi and correcting his earlier account", "authorial retrospective correction and report of scholarship",
                   "The strong wording is Haskell's assessment of Puppi's demonstration. Chapter 9 p.258 says Leonardo seems to have headed the family when the frescoes were painted; it does not itself state that he commissioned them. The cited note 5 remains queued; the fresco cycle is reused from its indexed p.258 candidate.",
                   ["cand-11065", "cand-11066", "cand-2689", "cand-2569", "cand-2594", "cand-2688", "cand-8444", "cand-11067", "cand-8442", "cand-2777", "cand-0116", "cand-2544"], [5], True,
                   {"cited_material_not_independently_consulted": True,
                    "cross_reference_segments": [{"segment_id": "chp-9:09_CHP-9_intro:l179-186", "source_line_start": 182, "source_line_end": 184}],
                    "cross_reference_statement_ids": ["st-chp9-p258-tiepolo-painted-valmarana-fresco-cycle", "st-chp9-p258-leonardo-valmarana-seems-family-head-in-1757"],
                    "ocr_corrections": [
                        {"source_line": 143, "ocr": "seeling", "print": "feeling", "basis": "CHP-20Postscript.pdf physical page 14 image"},
                        {"source_line": 143, "ocr": "Valmarana (who died in 1757)��about", "print": "Valmarana (who died in 1757)—about", "basis": "CHP-20Postscript.pdf physical page 14 image"}]}),
    make_statement("st-chp20-p405-cordellina-vicenza-palace", 143, 144, "cand-0842", "cand-11069",
                   "patronage_and_palace_construction_reported",
                   "Haskell says Puppi provided new information about Carlo Cordellina's patronage and especially the palace in Vicenza that Cordellina began having built in 1770 at age 73 and where he died eighteen years later.",
                   "Haskell reporting Puppi", "authorial report of scholarship and biographical detail",
                   "The palace has no formal name here; a possible match to the previously described Cordellina house candidate cand-8375 remains unresolved. Note 6 remains queued and the cited source was not independently consulted.",
                   ["cand-11065", "cand-11066", "cand-0842", "cand-2569", "cand-11069", "cand-2769"], [6], True,
                   {"cited_material_not_independently_consulted": True,
                    "cross_reference_segments": [{"segment_id": "chp-9:09_CHP-9_intro:l157-165", "source_line_start": 158, "source_line_end": 161}],
                    "cross_reference_statement_ids": ["st-chp9-p256-cordellina-built-vicenza-house"],
                    "related_candidate_ids_pending_alignment": ["cand-8375"]}),
    make_statement("st-chp20-p405-croft-murray-british-venetian-painters", 146, 146, "cand-11070", "cand-11072",
                   "volume_accounts_for_venetian_artists_attracted_to_britain",
                   "Haskell says the second volume of Croft-Murray's book on Decorative Painting in England gives the fullest account of the work of the Riccis, Pellegrini, Amigoni, Bellucci, and other Venetians attracted to Britain.",
                   "Haskell", "authorial assessment of later scholarship",
                   "The superlative is Haskell's assessment. The collective Riccis and unnamed other Venetians are not expanded to individuals; note 7 and bibliography reconciliation remain pending, including any link to p.403 candidate cand-11002.",
                   ["cand-11070", "cand-11001", "cand-11071", "cand-1870", "cand-0094", "cand-0282", "cand-11072", "cand-11073"], [7], True,
                   {"cited_material_not_independently_consulted": True,
                    "related_candidate_ids_pending_alignment": ["cand-11002"]}),
    make_statement("st-chp20-p405-daniels-monograph-sebastiano-ricci", 147, 147, "cand-11075", "cand-2154",
                   "monograph_adds_information_about_sebastiano_ricci",
                   "Haskell says additional information about Sebastiano Ricci can be found in Daniels's monograph on him.",
                   "Haskell", "authorial report of scholarship",
                   "Daniels is named by surname only; footnote 8 remains queued and the cited monograph was not independently consulted.",
                   ["cand-11074", "cand-11075", "cand-2154"], [8], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p405-shipley-amigoni-hostility", 147, 148, "cand-11077", "cand-0094",
                   "article_explores_hostility_toward_amigoni",
                   "Haskell says an article by Shipley explores the hostility to Amigoni felt and propagated in some quarters.",
                   "Haskell", "authorial report of scholarship",
                   "The source does not name those who held or propagated the hostility. Footnote 9 remains queued; the article was not independently consulted.",
                   ["cand-11076", "cand-11077", "cand-0094"], [9], True,
                   {"cited_material_not_independently_consulted": True}),
    make_statement("st-chp20-p405-mazza-mcswiny-pictures-catalogue-open", 148, 148, "cand-11078", "cand-11080",
                   "survey_and_catalogue_of_mcswiny_commemorative_pictures",
                   "Haskell says Barbara Mazza made a full survey of literature about commemorative pictures painted for Owen McSwiny; some of the pictures had emerged since Haskell's first edition, Mazza's conclusions confirmed his own, and her detailed catalogue replaced his 1963 summary list. The sentence continues with the catalogue's coverage.",
                   "Haskell reporting Barbara Mazza", "authorial report and comparison with earlier edition",
                   "The antecedent of 'some of which' is preserved as a group-level reference and is not resolved beyond the picture group. 'My own' refers to Haskell's conclusions. The catalogue description is open at the segment boundary and continues on p.406; no footnote marker appears before the boundary.",
                   ["cand-11078", "cand-11079", "cand-11080", "cand-1466"], [], True,
                   {"cited_material_not_independently_consulted": True,
                    "open_across_segment": True,
                    "continues_in_segment": P406,
                    "cross_reference_segments": [{"segment_id": P406, "source_line_start": 150, "source_line_end": 151}]})
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

all_mentions = mentions + new_mentions
spans = sorted((int(row["start_char"]), int(row["end_char"]), row["mention_id"])
               for row in all_mentions if row["segment_id"] == P405)
for index, left in enumerate(spans):
    for right in spans[index + 1:]:
        if right[0] >= left[1]:
            break
        nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
        if left[:2] == right[:2] or not nested:
            raise SystemExit(f"crossing/duplicate mention spans: {left[2]} / {right[2]}")

coverage_by_id[P405]["disposition"] = "reviewed"
coverage_by_id[P405]["migration_status"] = "partial"
coverage_by_id[P405]["source_line_ranges"] = "L137-148"
coverage_by_id[P405]["note"] = "Printed p.405 (PDF physical page 14) checked against page image. Ten S2 statements recorded; p.405 final catalogue clause continues on p.406 L150-162. Footnotes 1-9 point to queued notes L254-258."

paths = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP) for path in paths]
if ARGS.apply:
    if any(path.exists() for path in backups):
        raise SystemExit("p.405 recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied p.405 S2 migration; backup suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates={len(candidate_specs)}; new mentions={len(new_mentions)}; new statements={len(new_statements)}")
    print("p.405 source/PDF/S0 hashes, source spans, continuation, footnote links, candidate foreign keys, and mention overlaps validated")
