"""Controlled S2 migration for Chapter 8 printed page 234 and notes 1-6.

The default invocation is a read-only dry run. Source OCR is preserved; print
corrections are recorded as statement qualifiers after comparison with the PDF.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
P233 = "chp-8:08_CHP-8_sec_ii:l271-279"
P234 = "chp-8:08_CHP-8_sec_ii:l281-289"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P233, P234, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p234-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or not TARGET_IDS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line_offsets = {}
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    lines = source_lines[meta["line_start"] - 1:meta["line_end"]]
    if hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), lines):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(line) + 1

candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
mention_fields, mention_rows = read_csv(TABLES / "mentions.csv")
statement_rows = read_jsonl(TABLES / "book-statements.jsonl")
coverage_fields, coverage_rows = read_csv(TABLES / "s2-coverage.csv")
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("duplicate S2 coverage segment IDs")
expected = {
    P233: ("reviewed", "partial", "L272-279"),
    P234: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-423":
    raise SystemExit("post-text note coverage changed; inspect before proceeding")

new_candidates = [
    ("cand-7939", "The Stoning of Zechariah (painting attributed to Fumiani, Plate 40b)", "work", 284,
     "Haskell's probable identification of the subject; the lost instructions prevent certainty."),
    ("cand-7940", "Portrait of a Cook (painting by Niccolò Cassana, 1707)", "work", 286,
     "The source names the portrait but does not identify the sitter or establish its present location."),
    ("cand-7941", "Unidentified Bacchanal painted by Niccolò Cassana for Ferdinand", "work", 287,
     "One of several history pictures named by Haskell; no title, date, or present location is supplied."),
    ("cand-7942", "Unidentified Venus playing with Cupid painted by Niccolò Cassana for Ferdinand", "work", 287,
     "One of several history pictures named by Haskell; no title, date, or present location is supplied."),
    ("cand-7943", "Conspiracy of Catiline by Niccolò Cassana (Pitti no. 111)", "work", 287,
     "The attribution and location are reported by Haskell; footnote 5 qualifies it as probably a copy after Rosa."),
    ("cand-7944", "Unidentified painting by Domenichino used as model for Fumiani's composition", "work", 283,
     "The painting is not titled or otherwise identified in the passage."),
    ("cand-7945", "Uffizi (repository named for the Stoning of Zechariah)", "", 284,
     "Type unresolved: Haskell's wording does not distinguish the holding institution from the physical gallery."),
    ("cand-7946", "Unidentified portrait by Giovanni Battista Langetti reported in the Medici collection", "work", 288,
     "Ratti's report is indirect; the portrait is not identified."),
    ("cand-7947", "Unidentified card-players picture by Giovanni Battista Langetti reported in the Medici collection", "work", 288,
     "Ratti's report is indirect; the picture is not identified."),
    ("cand-7948", "Medici collection of pictures (repository referred to by Ratti)", "", 288,
     "Type and location unresolved; the source does not specify an institutional or physical repository."),
    ("cand-7949", "La Pittura del Seicento a Venezia (1959 catalogue cited by Haskell)", "archive", 426,
     "Cited as the source of a misidentification; the catalogue was not independently consulted."),
    ("cand-7950", "Fogolari (1937), Letter 120 (1707-09-03)", "archive", 427,
     "A letter locator cited through Haskell; the letter was not independently consulted."),
    ("cand-7951", "Fogolari (1937), Letter 92 (1704-01-25)", "archive", 429,
     "A letter locator cited through Haskell; the letter was not independently consulted."),
    ("cand-7952", "Unidentified self-portrait by Niccolò Cassana", "work", 427,
     "Ratti's cited account reports a self-portrait but does not identify the object."),
    ("cand-7953", "Rosa (painter named by surname only in Jahn-Rusconi's attribution)", "person", 428,
     "The source gives only the surname; identity is not resolved to a specific painter."),
    ("cand-7954", "II Samuel 24:12 (biblical locator cited in Haskell's footnote)", "archive", 425,
     "Scriptural reference cited by Haskell; the passage was not independently consulted."),
    ("cand-7955", "II Chronicles 24:21 (biblical locator cited in Haskell's footnote)", "archive", 426,
     "Scriptural reference cited by Haskell; the passage was not independently consulted."),
]

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 372 else P234
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"])
                  for row in mention_rows}
new_mentions = []


def mention(segment_id, source_line, suffix, candidate_id, surface, note, occurrence=0):
    mention_id = f"m-chp8-p234-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[source_line - 1]
    search_at = 0
    found_at = -1
    for _ in range(occurrence + 1):
        found_at = line.find(surface, search_at)
        if found_at < 0:
            raise SystemExit(f"surface not found at L{source_line}: {surface!r} #{occurrence}")
        search_at = found_at + 1
    start = line_offsets[(segment_id, source_line)] + found_at
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span
                                     for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id,
                         "candidate_id": candidate_id, "surface_form": surface,
                         "start_char": str(start), "end_char": str(end), "note": note})


mention_specs = [
    (P234, 282, "fumiani-name", "cand-1087", "Giannaritonio Fumiani", "The page image prints Giannantonio; the source transcription is retained and correction recorded on the statement."),
    (P234, 282, "grand-prince", "cand-1609", "the Grand Prince", "The patron discussed in this section."),
    (P234, 282, "he", "cand-1609", "he", "Coreference to the Grand Prince."),
    (P234, 283, "he-programme", "cand-1609", "He", "Coreference to the Grand Prince."),
    (P234, 283, "domenichino", "cand-0932", "Domenichino", "Reuse the indexed painter candidate."),
    (P234, 283, "fumiani-1", "cand-1087", "Fumiani", "Reuse the same artist candidate as the p.233 lead-in."),
    (P234, 283, "fumiani-picture", "cand-7893", "picture", "The unidentified composition requested by Ferdinand; reuse the p.232 candidate."),
    (P234, 283, "domenichino-picture", "cand-7944", "one by Domenichino", "Unidentified work used as the model."),
    (P234, 284, "cassana-agent", "cand-0593", "Cassana", "The agent is Niccolò Cassana."),
    (P234, 284, "david-1", "cand-4268", "David", "Biblical figure; footnote 2 gives II Samuel xxiv,12."),
    (P234, 284, "david-2", "cand-4268", "David", "The proposed figure to be painted by Cassana or Fumiani.", 1),
    (P234, 284, "fumiani-3", "cand-1087", "Fumiani", "Reuse the same artist candidate."),
    (P234, 284, "david-3", "cand-4268", "David", "The figure in the composition.", 2),
    (P234, 284, "modello", "cand-1674", "modello", "The preparatory model sent to Ferdinand for review."),
    (P234, 284, "ferdinand-review", "cand-1609", "Ferdinand", "The patron who reviewed the modello."),
    (P234, 284, "david-4", "cand-4268", "David", "The figure whose movement Ferdinand wanted to increase.", 3),
    (P234, 284, "prince", "cand-1609", "the Prince", "Coreference to Grand Prince Ferdinand."),
    (P234, 284, "king", "cand-4268", "the king", "David, as indicated by the explicit reference to David and footnote 2."),
    (P234, 284, "ferdinand-change", "cand-1609", "Ferdinand", "The patron who changed the requested subject.", 1),
    (P234, 284, "stoning-zechariah", "cand-7939", "The Stoning of Zechariah", "Haskell's probable identification of the alternative subject."),
    (P234, 284, "zechariah", "cand-4173", "Zechariah", "Reuse the religious-figure candidate from the plate list."),
    (P234, 284, "ferdinand-inventory", "cand-1609", "Ferdinand’s inventory", "The cited 1716 inventory; see note 3."),
    (P234, 284, "uffizi", "cand-7945", "the Uffizi", "Repository/building distinction remains unresolved for S3."),
    (P234, 285, "cassana-name", "cand-0593", "Niccolo Cassana", "Reuse the indexed artist candidate; printed accent is recorded in the statement correction."),
    (P234, 285, "ferdinand-cassana", "cand-1609", "Ferdinand", "The Grand Prince who employed Cassana."),
    (P234, 285, "florence", "cand-3397", "Florence", "City where Cassana painted portraits for the Prince and household."),
    (P234, 285, "prince-household", "cand-1609", "the Prince", "Coreference to Ferdinand."),
    (P234, 286, "venice", "cand-3401", "Venice", "Place from which Cassana sent pictures."),
    (P234, 286, "portrait-cook", "cand-7940", "his Portrait os a Cook", "The title is corrected to Portrait of a Cook against the print."),
    (P234, 286, "florence-arrival", "cand-3397", "Florence", "Destination of the portrait."),
    (P234, 287, "prince-reception", "cand-1609", "Prince", "Coreference to Ferdinand."),
    (P234, 287, "grand-prince-history", "cand-1609", "Grand Prince", "Coreference to Ferdinand."),
    (P234, 287, "venetian-quality", "cand-5756", "Venetian", "Describes the painting style as reported by Haskell."),
    (P234, 287, "florentine-artists", "cand-3397", "native Florentine artists", "Florentine is a place-derived adjective; no unnamed artist group candidate is created."),
    (P234, 287, "cassana-history", "cand-0593", "Cassana", "Reuse the indexed artist candidate."),
    (P234, 287, "bacchanal", "cand-7941", "a Bacchanal", "An unnamed Cassana history picture; not assigned a date or location."),
    (P234, 287, "venus-cupid", "cand-7942", "a Venus playing with Cupid", "An unnamed Cassana history picture; not assigned a date or location."),
    (P234, 287, "catiline", "cand-7943", "a Conspiracy of Catiline", "The named Cassana history picture; note 5 qualifies the attribution."),
    (P234, 288, "langetti-full-name", "cand-1363", "Giovanni Battista Langetti", "Reuse the indexed painter candidate; this material appears in the page-end note area."),
    (P234, 288, "venice-langetti", "cand-3401", "Venice", "City where Langetti worked according to Haskell."),
    (P234, 289, "ratti-edition", "cand-5160", "Ratti (Soprani/Ratti, H, 26)", "Citation to the Soprani/Ratti edition; the page reference is preserved as transcribed."),
    (P234, 289, "langetti-portrait", "cand-7946", "a portrait", "Unidentified Langetti painting reported by Ratti."),
    (P234, 289, "langetti-card-players", "cand-7947", "a picture of card players", "Unidentified Langetti painting reported by Ratti."),
    (P234, 289, "medici-collection", "cand-7948", "the Medici collection", "Repository type and location unresolved."),
    (P234, 289, "ferdinand-employment", "cand-1609", "Ferdinand", "The patron named in the report."),
    (P234, 289, "langetti-again", "cand-1363", "Langetti", "The artist whose employment claim Haskell rejects."),
    (P234, 289, "florence-employment", "cand-3397", "Florence", "The alleged place of employment."),
    (P234, 289, "langetti-death", "cand-1363", "Langetti", "Haskell's chronological objection refers to the same painter.", 1),
    (P234, 289, "prince-age", "cand-1609", "the Prince", "Ferdinand, aged eleven in 1676 according to Haskell."),
    (P234, 289, "ferdinand-chronology", "cand-1609", "Ferdinand", "The named prince whose age is given as eleven in 1676.", 1),
    (P234, 289, "fogolari-ref", "cand-7894", "Fogolari", "Cited publication; the specific letter locator continues in the notes segment."),
    (NOTES, 424, "note1-fogolari", "cand-7894", "Fogolari", "Citation list supporting Haskell's account of correspondence with Fumiani."),
    (NOTES, 425, "note2-samuel", "cand-7954", "II Samuel xxiv, 12", "Biblical locator for the proposed David subject."),
    (NOTES, 426, "note3-inventory", "cand-7936", "1716 inventory", "Reuse the existing inventory candidate."),
    (NOTES, 426, "note3-chronicles", "cand-7955", "IT Chronicles xxiv, 21", "The print reads II Chronicles; the OCR source is retained."),
    (NOTES, 426, "note3-anaias-title", "cand-7939", "The Punishment of the Prophet Ananias", "Misdescription reported for the same painting; do not create a separate work."),
    (NOTES, 426, "note3-catalogue", "cand-7949", "La Pittura del Seicento a Venezia", "Cited 1959 catalogue; not independently consulted."),
    (NOTES, 426, "note3-fumiani", "cand-1087", "Ferdinand’s patronage of Fumiani", "Named as context for a further letter in Fogolari note 34."),
    (NOTES, 426, "note3-fogolari", "cand-7894", "Fogolari", "Cited publication; the letter was not independently consulted."),
    (NOTES, 427, "note4-ratti", "cand-5160", "Ratti", "Surname in the Soprani/Ratti cited edition."),
    (NOTES, 427, "note4-cassana", "cand-0593", "Cassana", "Reuse the indexed painter candidate."),
    (NOTES, 427, "note4-prince", "cand-1609", "the Grand Prince", "The sitter and patron in Ratti's report."),
    (NOTES, 427, "note4-selfportrait", "cand-7952", "his self-portrait", "Unidentified Cassana self-portrait reported by Ratti."),
    (NOTES, 427, "note4-fogolari", "cand-7894", "Fogolari", "Cited publication."),
    (NOTES, 427, "note4-letter120", "cand-7950", "Letter 120", "Letter locator dated 3 September 1707."),
    (NOTES, 428, "note5-catiline", "cand-7943", "The Conspiracy of Catiline", "The work is tentatively attributed as a copy after Rosa."),
    (NOTES, 428, "note5-rosa", "cand-7953", "Rosa", "Surname-only reference; identity unresolved."),
    (NOTES, 428, "note5-pitti", "cand-7662", "the Pitti", "Haskell's repository wording; building and holding-collection roles are not distinguished."),
    (NOTES, 428, "note5-jahn-rusconi", "cand-7870", "Jahn-Rusconi", "Cited catalogue; not independently consulted."),
    (NOTES, 429, "note6-letter92", "cand-7951", "92", "Continuation of the Fogolari letter locator in the page-end report at P234 L288-289."),
]
for spec in mention_specs:
    mention(*spec)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 234,
        "pdf_physical_page": 40, "claim": claim, "speaker": "Haskell",
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote(segment_id, first, last), "origin": "book",
            "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p234-fumiani-relations", P234, 282, 282, "cand-1609", "cand-1087",
                   "described_fumiani_relationship_as_vehicle_for_fanciful_composition",
                   "Haskell says the relations between Giannantonio Fumiani and the Grand Prince reveal Ferdinand's eagerness to have artists express his fantasies.",
                   "This is Haskell's interpretive account, not independently verified evidence of Ferdinand's psychology. The sentence begins with 'The' at p.233 L279; page 234 prints Giannantonio and 'us' where the source transcription has OCR variants.",
                   ["cand-1609", "cand-1087"],
                   extras={"relation_candidate": True,
                           "continued_from_segment_id": P233,
                           "continued_from_source_line": 279,
                           "cross_reference_segments": [{"segment_id": P233, "source_line_start": 279, "source_line_end": 279}],
                           "ocr_corrections": [{"source_line": 282, "ocr": "Giannaritonio", "print": "Giannantonio", "basis": "CHP-8.pdf physical page 40"},
                                               {"source_line": 282, "ocr": "ns", "print": "us", "basis": "CHP-8.pdf physical page 40"}]}),
    make_statement("st-chp8-p234-fumiani-programme", P234, 283, 284, "cand-1609", "cand-7893",
                   "specified_programme_for_fumiani_composition",
                   "Ferdinand wanted Fumiani to make a picture matching an unidentified work by Domenichino and gave agent Niccolò Cassana its dimensions and a detailed programme: an architectural background, guards, and David at prayer; Cassana was to paint David unless Fumiani insisted on doing so.",
                   "The instructions are reported through Haskell; neither the original correspondence nor the unidentified Domenichino painting was independently consulted. The passage does not establish that this programme was fully executed.",
                   ["cand-1609", "cand-7893", "cand-7944", "cand-0932", "cand-1087", "cand-0593", "cand-4268"],
                   extras={"relation_candidate": True,
                           "ocr_corrections": [{"source_line": 284, "ocr": "lais sceptre", "print": "his sceptre", "basis": "CHP-8.pdf physical page 40"}]}),
    make_statement("st-chp8-p234-fumiani-model-review", P234, 284, 284, "cand-1609", "cand-7893",
                   "reviewed_modello_and_requested_compositional_changes",
                   "Fumiani's modello reached Ferdinand and was satisfactory to him, but Ferdinand wanted more movement, suggesting a flying angel with a flaming sword and the choice of three punishments; David was to show surprise and could be accompanied by his harp, sceptre, and diadem.",
                   "The Prince's response is reported through Haskell. The proposed angel, attributes, and revised composition are instructions, not evidence that the changes were made or the painting completed.",
                   ["cand-1609", "cand-7893", "cand-1087", "cand-1674", "cand-4268"],
                   extras={"relation_candidate": True,
                           "linked_note_statement_ids": ["st-chp8-p234-note2-samuel"]}),
    make_statement("st-chp8-p234-subject-change", P234, 284, 284, "cand-1609", "cand-7939",
                   "changed_requested_subject_to_stoning_of_zechariah",
                   "After the initial David programme, Ferdinand changed his mind and wanted an unusual Old Testament subject; Haskell says the lost instructions were evidently for The Stoning of Zechariah and interprets these subjects as pretexts for fanciful composition rather than evidence of special significance.",
                   "Haskell marks the identification as inferential ('evidently'); the instructions are lost. The work's present location and inventory record are reported in footnote 3, not independently verified.",
                   ["cand-1609", "cand-7939", "cand-4173", "cand-4268"],
                   extras={"relation_candidate": True,
                           "linked_note_statement_ids": ["st-chp8-p234-note3-stoning-record"]}),
    make_statement("st-chp8-p234-cassana-role", P234, 285, 286, "cand-0593", "cand-1609",
                   "worked_as_painter_and_adviser_for_grand_prince",
                   "Haskell says Niccolò Cassana worked for Ferdinand as painter and artistic adviser, visited Florence chiefly to paint portraits of the Prince and household, and sent pictures from Venice.",
                   "The account is Haskell's report; the source does not name the sitters in the household portraits or identify the pictures sent from Venice.",
                   ["cand-0593", "cand-1609", "cand-3397", "cand-3401"],
                   extras={"relation_candidate": True,
                           "ocr_corrections": [{"source_line": 285, "ocr": "Niccolo", "print": "Niccolò", "basis": "CHP-8.pdf physical page 40"}]}),
    make_statement("st-chp8-p234-cook-arrival", P234, 286, 286, "cand-7940", "cand-3397",
                   "reached_florence_in_september_1707",
                   "In September 1707, Niccolò Cassana's Portrait of a Cook reached Florence.",
                   "The sitter is not identified and no present location is given. The title's OCR error is corrected against the print.",
                   ["cand-0593", "cand-7940", "cand-3397"],
                   extras={"date": "1707-09", "relation_candidate": True,
                           "ocr_corrections": [{"source_line": 286, "ocr": "Portrait os a Cook", "print": "Portrait of a Cook", "basis": "CHP-8.pdf physical page 40"}]}),
    make_statement("st-chp8-p234-cook-reception", P234, 286, 287, "cand-1609", "cand-7940",
                   "praised_cooks_portrait_for_realism_and_venetian_painterly_quality",
                   "Ferdinand delighted in the portrait's realistic details, wanted to know who the sitter was, and praised its bold Venetian painterly quality in contrast with what he called the timid efforts of native Florentine artists.",
                   "The sitter remains unidentified. The judgement and contrast are reported by Haskell as Ferdinand's comments; they are not independent quality assessments.",
                   ["cand-1609", "cand-7940", "cand-0593", "cand-5756", "cand-3397"],
                   extras={"speaker": "Ferdinand as reported by Haskell"}),
    make_statement("st-chp8-p234-cassana-history-pictures", P234, 287, 287, "cand-0593", "cand-1609",
                   "painted_history_pictures_for_grand_prince",
                   "Cassana also painted history pictures for Ferdinand, mostly in a light vein: an unidentified Bacchanal, an unidentified Venus playing with Cupid, and a Conspiracy of Catiline.",
                   "The book does not supply dates or present locations for the first two pictures. Footnote 5 qualifies the Conspiracy of Catiline as probably a copy after Rosa and reports it in the Pitti; neither attribution nor location was independently checked.",
                   ["cand-0593", "cand-1609", "cand-7941", "cand-7942", "cand-7943"],
                   extras={"relation_candidate": True}),
    make_statement("st-chp8-p234-langetti-report", P234, 288, 289, "cand-1363", "cand-1609",
                   "reported_as_employed_by_ferdinand_but_chronologically_impossible",
                   "The page-end note says Ratti reports Langetti's portrait and card-players picture in the Medici collection and says he was employed by Ferdinand in Florence; Haskell rejects the employment claim because Langetti died in 1676, when Ferdinand was eleven.",
                   "This text is printed in the page-end note area but its note number is absent from the transcription. Ratti's report is indirect; Haskell's chronological objection is recorded as the author's claim, not independently verified here. The citation to Fogolari continues at note line 429.",
                   ["cand-1363", "cand-1609", "cand-5160", "cand-7946", "cand-7947", "cand-7948", "cand-3397", "cand-7894", "cand-7951"],
                   text_layer="page-end note/report; marker number absent in transcription",
                   extras={"relation_candidate": True,
                           "linked_note_statement_ids": ["st-chp8-p234-note6-letter92"],
                           "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 429, "source_line_end": 429}]}),
]

new_statements.extend([
    make_statement("st-chp8-p234-note1-fogolari-letters", NOTES, 424, 424, None, "cand-7894",
                   "footnote_cites_fogolari_letters_45_63_between_may_and_november_1699",
                   "Footnote 1 cites Fogolari (1937), Letters 45, 47, 48, 49, 50, 53, 54, 55, 56, 57, 59, 61, and 63, dated between May and November 1699.",
                   "This is a citation list in Haskell, not independent consultation of Fogolari or the letters.",
                   ["cand-7894", "cand-1087", "cand-1609"], text_layer="footnote citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p234-fumiani-relations", "st-chp8-p234-fumiani-model-review"],
                           "ocr_corrections": [{"source_line": 424, "ocr": "1699..", "print": "1699.", "basis": "CHP-8.pdf physical page 40"}]}),
    make_statement("st-chp8-p234-note2-samuel", NOTES, 425, 425, "cand-7954", "cand-4268",
                   "footnote_locates_david_scene_in_ii_samuel_xxiv_12",
                   "Footnote 2 says the unusual proposed subject involving the three punishments is taken from II Samuel xxiv, 12.",
                   "This is Haskell's scriptural locator; the Biblical passage was not independently consulted in this migration.",
                   ["cand-7954", "cand-4268"], text_layer="footnote citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p234-fumiani-programme", "st-chp8-p234-fumiani-model-review"]}),
    make_statement("st-chp8-p234-note3-stoning-record", NOTES, 426, 426, "cand-7939", "cand-7949",
                   "footnote_reports_inventory_record_and_catalogue_misdescription",
                   "Footnote 3 says the picture is recorded in the 1716 inventory, identifies its subject with II Chronicles xxiv, 21, reports a catalogue misdescription as The Punishment of the Prophet Ananias, and cites another letter from Ferdinand to Fumiani in Fogolari note 34.",
                   "All details are Haskell's footnote report. The inventory, scripture, catalogue, and Fogolari letter were not independently consulted; the alternative catalogue title is a misdescription, not a separate work.",
                   ["cand-7939", "cand-7936", "cand-7949", "cand-7955", "cand-1087", "cand-1609", "cand-7894"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p234-subject-change"],
                           "ocr_corrections": [{"source_line": 426, "ocr": "IT Chronicles", "print": "II Chronicles", "basis": "CHP-8.pdf physical page 40"},
                                               {"source_line": 426, "ocr": "catalogue ' ' of", "print": "catalogue of", "basis": "CHP-8.pdf physical page 40"}]}),
    make_statement("st-chp8-p234-note4-cassana-references", NOTES, 427, 427, "cand-0593", "cand-5160",
                   "footnote_cites_ratti_and_fogolari_on_cassanas_work_for_ferdinand",
                   "Footnote 4 cites Soprani/Ratti, volume II, page 14, for Cassana portraits of the Grand Prince, his wife, his gentiluomo di camera, other courtiers including jesters, a self-portrait, and history pictures; it also cites Fogolari Letter 120 dated 3 September 1707.",
                   "These are Haskell's bibliographic reports; the cited edition and letter were not independently consulted. Unnamed sitters remain unidentified.",
                   ["cand-0593", "cand-1609", "cand-5160", "cand-7950", "cand-7952", "cand-7894"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p234-cassana-role", "st-chp8-p234-cook-arrival"]}),
    make_statement("st-chp8-p234-note5-catiline", NOTES, 428, 428, "cand-7943", "cand-7662",
                   "footnote_reports_probable_copy_after_rosa_in_pitti_no_111",
                   "Footnote 5 says the Conspiracy of Catiline is probably a copy after Rosa and is now in the Pitti, catalogue number 111, citing Jahn-Rusconi page 238.",
                   "The copy attribution is explicitly probable; Rosa is given by surname only. The catalogue and holding location were not independently checked, and the Pitti building/collection role remains unresolved.",
                   ["cand-7943", "cand-7953", "cand-7662", "cand-7870"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p234-cassana-history-pictures"],
                           "ocr_corrections": [{"source_line": 428, "ocr": "No. in", "print": "No. 111", "basis": "CHP-8.pdf physical page 40"}]}),
    make_statement("st-chp8-p234-note6-letter92", NOTES, 429, 429, None, "cand-7951",
                   "footnote_locator_continues_fogolari_letter_92",
                   "The final note line completes the page-end Langetti report's citation as Fogolari (1937), Letter 92 of 25 January 1704.",
                   "The citation supports the note's reported source only; Fogolari's text and the letter were not independently consulted.",
                   ["cand-7894", "cand-7951", "cand-1363"], text_layer="footnote citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p234-langetti-report"],
                           "continued_from_segment_id": P234,
                           "continued_from_source_line": 289,
                           "cross_reference_segments": [{"segment_id": P234, "source_line_start": 288, "source_line_end": 289}]})
])

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p233-loth-employment"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["segment_id"] != P233 or prior["qualifiers"].get("continuation_status"):
    raise SystemExit("expected unclosed p.233 final statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continuation_to_segment_id": P234,
    "continuation_to_source_line": 282, "continued_to_segment_id": P234,
    "continued_to_source_line": 282,
    "continuation_closed_by_statement_id": "st-chp8-p234-fumiani-relations",
})

for row in coverage_rows:
    if row["segment_id"] == P233:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L272-279",
                    "note": "p.233 body and notes 1-5 at L419-423 reviewed against CHP-8.pdf physical page 39. The final sentence's opening article at L279 continues to p.234 L282 and is closed by st-chp8-p234-fumiani-relations."})
    elif row["segment_id"] == P234:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L282-289",
                    "note": "p.234 printed body, page-end Langetti report, and notes 1-6 at L424-429 reviewed against CHP-8.pdf physical page 40. The Langetti text at L288-289 is page-end note text with no marker in the transcription; its citation continues at L429. L430-461 remain."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-429",
                    "note": "Post-text notes through p.234 note 6 at L429 migrated and linked to cited body/page-end claims; consolidated notes L430-461 remain."})

preview = {
    "mode": "dry-run", "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "closed_continuation": {"statement_id": prior_id, "segment_id": P234, "line": 282},
    "coverage_updates": {P233: "complete", P234: "complete", NOTES: "L373-429 partial"},
    "ocr_corrections": [
        "L282 Giannaritonio -> Giannantonio; ns -> us",
        "L284 lais sceptre -> his sceptre",
        "L285 Niccolo -> Niccolò",
        "L286 Portrait os a Cook -> Portrait of a Cook",
        "L424 1699.. -> 1699.",
        "L426 IT Chronicles -> II Chronicles; catalogue ' ' of -> catalogue of",
        "L428 No. in -> No. 111",
    ],
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=True, indent=2))
    raise SystemExit(0)

paths = (TABLES / "entity-candidates.csv", TABLES / "mentions.csv",
         TABLES / "book-statements.jsonl", TABLES / "s2-coverage.csv")
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
patched_statements = [patched_prior if row["statement_id"] == prior_id else row
                      for row in statement_rows]
patched_statements.extend(new_statements)
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", patched_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, coverage_rows)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=True, indent=2))
