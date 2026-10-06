"""Controlled S2 migration for Chapter 8 printed page 233 and notes 1-5.

The default invocation is a read-only dry run. OCR corrections are recorded
in S2 qualifiers and process notes; canonical source text is not rewritten.
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
P232 = "chp-8:08_CHP-8_sec_ii:l251-257"
P233 = "chp-8:08_CHP-8_sec_ii:l271-279"
P234 = "chp-8:08_CHP-8_sec_ii:l281-289"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P232, P233, P234, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p233-20261001"


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
    P232: ("reviewed", "partial", "L251-257"),
    P233: ("queued", "pending", ""),
    P234: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-418":
    raise SystemExit("post-text note coverage changed; inspect before proceeding")
if any(row["segment_id"] == P233 for row in mention_rows + statement_rows):
    raise SystemExit("p.233 mentions/statements already exist; inspect before rerunning")

new_candidates = [
    ("cand-7915", "Modello for Francesco Trevisani's Banquet of Anthony and Cleopatra", "work", 419,
     "Haskell's note reports that Trevisani sent the modello to Ferdinand; the final painting was made for Cardinal Fabrizio Spada-Varallo. The modello's present identity and location are not given."),
    ("cand-7916", "Fabrizio Spada-Varallo, cardinal named as patron of Trevisani's Banquet", "person", 419,
     "The note gives this form and title only; identity alignment is deferred."),
    ("cand-7917", "Anthony named in Trevisani's Banquet of Anthony and Cleopatra title", "person", 419,
     "Retain the printed name form from the work title; do not normalize identity in S2."),
    ("cand-7918", "Unidentified father of Marco Sacconi", "person", 276,
     "The passage says Sacconi's father died but supplies no name or further identity."),
    ("cand-7919", "Unidentified St Sebastian painting ordered for Marco Sacconi", "work", 276,
     "A subject specified in Ferdinand's orders; the passage does not establish completion, title, or present location."),
    ("cand-7920", "Unidentified St Giustina painting ordered for Marco Sacconi", "work", 276,
     "A subject specified in Ferdinand's orders; the passage does not establish completion, title, or present location."),
    ("cand-7921", "Unidentified Bacchanal ordered for Marco Sacconi", "work", 276,
     "A subject specified in Ferdinand's orders; the passage does not establish completion, title, or present location."),
    ("cand-7922", "Anton Domenico Gabbiani's 1699 visit to Venice", "event", 275,
     "Haskell says Gabbiani visited Venice at age 47 to improve his colour for Ferdinand; no independent travel record is cited here."),
    ("cand-7923", "Unidentified half-length figures by Karl Loth sought by Ferdinand", "work", 279,
     "Haskell says Ferdinand made particular efforts to obtain some figures of this kind; acquisition is not confirmed."),
    ("cand-7924", "Archivio Mediceo, Guardaroba 1055 payment records", "archive", 420,
     "Haskell's note locates payments to painters and sculptors in this record group; the archive was not independently consulted."),
    ("cand-7925", "Abate Orazio Martini", "person", 420,
     "Named as a reference for other Tuscan artists; no further identity details are supplied in this note."),
    ("cand-7926", "Publication by Abate Orazio Martini cited for Tuscan painters' payments", "archive", 420,
     "The title, date, and edition are not supplied in Haskell's note."),
    ("cand-7927", "Fogolari (1937), Letter 83 (1703-03-17)", "archive", 421,
     "The number and date are given as a bibliographic locator; the letter and publication were not independently consulted."),
    ("cand-7928", "Fogolari (1937), Letter 6", "archive", 422,
     "Listed by Haskell as a cited letter; date, witness, and repository are not supplied here."),
    ("cand-7929", "Fogolari (1937), Letter 12", "archive", 422,
     "Listed by Haskell as a cited letter; date, witness, and repository are not supplied here."),
    ("cand-7930", "Fogolari (1937), Letter 60", "archive", 422,
     "Listed by Haskell as a cited letter; date, witness, and repository are not supplied here."),
    ("cand-7931", "Letter from Karl Loth to Grand Prince Ferdinand (1691-08-14; cited in Fogolari 1937)", "archive", 423,
     "Identified by date and described through Haskell's footnote; the letter and Fogolari's publication were not independently consulted."),
    ("cand-7932", "Copy after Titian's St Peter Martyr planned by Karl Loth", "work", 423,
     "Haskell says Loth was about to embark on a copy on 14 August 1691; this does not establish that it was completed."),
    ("cand-7933", "Self-portrait by Karl Loth sent to Florence in 1693", "work", 423,
     "The note reports that Loth sent the self-portrait; its present identity and location are not supplied."),
    ("cand-7934", "Fogolari (1937), Letter 77", "archive", 423,
     "A specific numbered letter cited as a locator; date, witness, and repository are not supplied here."),
    ("cand-7935", "Ewald (1965), catalogue entries on Karl Loth", "archive", 423,
     "Haskell cites catalogue entries but gives no title or edition in this note."),
    ("cand-7936", "Ferdinand's collection inventory of 1716", "archive", 423,
     "The note cites the inventory as recording six pictures by Loth; the inventory was not independently consulted."),
    ("cand-7937", "Pascoli, author of Francesco Trevisani's unpublished life (forename unspecified)", "person", 419,
     "The note supplies only the surname; do not identify this author with the indexed Lione Pascoli in S2."),
    ("cand-7938", "Ferdinand's second visit to Venice referenced in Haskell's Loth account", "event", 279,
     "Haskell calls it the second visit but supplies no date here; do not infer a date from other passages in this candidate."),
]

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"])
                 for row in candidate_rows if not row["index_entry_id"]}
new_keys = set()
expected_next_id = max(int(cid.removeprefix("cand-")) for cid in candidate_ids
                       if cid.startswith("cand-")) + 1
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id != f"cand-{expected_next_id}":
        raise SystemExit(f"unexpected candidate sequence at {candidate_id}; expected cand-{expected_next_id}")
    expected_next_id += 1
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 372 else P233
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
    mention_id = f"m-chp8-p233-{suffix}"
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
    (P233,272,"modelli","cand-1674","modelli","The modeling practice named in the p.232 continuation."),
    (P233,272,"canvas","cand-3571","canvas","Material discussed as part of painting procedure."),
    (P233,273,"gabbiani-1","cand-1093","Gabbiani","Reuse the indexed painter candidate."),
    (P233,273,"marattesque","cand-7873","Marattesque","Haskell's style characterization; not an independent attribution."),
    (P233,274,"florentine","cand-3397","Florentine","Place-derived adjective referring to Florence."),
    (P233,274,"gherardini","cand-1156","Gherardini","Reuse the indexed painter candidate."),
    (P233,274,"sagrestani","cand-2340","Sagrestani","Reuse the indexed painter candidate."),
    (P233,274,"galeotti","cand-1100","Galeotti","Reuse the indexed painter candidate."),
    (P233,274,"tastes","cand-1625","his tastes","Ferdinand's taste candidate."),
    (P233,275,"bassi","cand-0259","Francesco Bassi","Reuse the indexed painter candidate."),
    (P233,275,"grand-prince-continued","cand-1609","The Grand","The title continues over the line break as 'The Grand Prince'."),
    (P233,275,"gabbiani-2","cand-1093","Gabbiani","Gabbiani in Haskell's explanation of Ferdinand's patronage."),
    (P233,275,"ferdinand-possessive","cand-1609","Ferdinand","Ferdinand is named in the possessive before Sacconi's patronage discussion."),
    (P233,275,"venetian-painting","cand-5756","Venetian painting","The artistic tradition to which Gabbiani professed attachment."),
    (P233,275,"gabbiani-visit","cand-1093","Gabbiani","Artist named as making the 1699 visit.",1),
    (P233,275,"venice-visit","cand-3401","Venice","Destination of Gabbiani's visit."),
    (P233,275,"sacconi","cand-2325","Sacconi","Reuse the indexed artist candidate."),
    (P233,275,"venice-sacconi","cand-3401","Venice","Destination where Sacconi was sent.",1),
    (P233,276,"grand-prince","cand-1609","Prince","The printed title continues across the line break from L275: 'The Grand Prince'."),
    (P233,276,"sacconi-pronoun-1","cand-2325","him","Sacconi; the preceding sentence and career context fix the referent."),
    (P233,276,"sacconi-father","cand-7918","his father","Unidentified father of Sacconi."),
    (P233,276,"sacconi-pronoun-2","cand-2325","him","Sacconi, kept working under Cassana.",1),
    (P233,276,"cassana","cand-0593","Niccolo Cassana","The page image prints Niccolò; correction recorded on the statement."),
    (P233,276,"st-sebastian-work","cand-7919","a St Sebastian","Subject of an order for Sacconi; completion not asserted."),
    (P233,276,"st-giustina-work","cand-7920","a St Giustina","Subject of an order for Sacconi; completion not asserted."),
    (P233,276,"bacchanal-work","cand-7921","a Bacchanal","Subject of an order for Sacconi; completion not asserted."),
    (P233,277,"ferdinand-2","cand-1609","He","Coreference to Ferdinand, who is named as Prince on L276."),
    (P233,277,"cassana-2","cand-0593","Cassana","Reuse the indexed artist candidate."),
    (P233,276,"sacconi-colour","cand-2325","his colour","Sacconi's colour, improving under Cassana."),
    (P233,277,"corpus-domini","cand-6024","Corpus Domini","Reuse the event candidate."),
    (P233,277,"venice-result","cand-3401","Venice","Venice as the setting of the artists' instruction."),
    (P233,277,"artist-sacconi","cand-2325","the artist","Coreference to Sacconi."),
    (P233,278,"ferdinand-3","cand-1609","Ferdinand","Reuse the Grand Prince candidate."),
    (P233,279,"venice-loth","cand-3401","Venice","City where Loth was already painting for Ferdinand."),
    (P233,279,"loth-1","cand-1442","Karl Loth","Reuse the indexed painter candidate."),
    (P233,279,"loth-figures","cand-7923","half-length figures","Unidentified works sought but not confirmed as acquired."),
    (P233,279,"loth-2","cand-1442","Loth","Reuse the indexed painter candidate.",1),
    (P233,279,"ferdinand-second-visit","cand-7938","second visit to the city","The city is Venice; the passage supplies no date."),
    (P233,279,"ferdinand","cand-1609","Ferdinand","Reuse the Grand Prince candidate."),
    (P233,279,"fumiani-contextual","cand-1087","an artist","P.234 immediately turns to the Ferdinand-Fumiani relationship; this local referent remains contextually linked."),
    (NOTES,419,"trevisani","cand-2650","Francesco Trevisani","Reuse the indexed painter; the note's report is not independent verification."),
    (NOTES,419,"ferdinand-pronoun","cand-1609","him","Ferdinand is the recipient of the modello in the note."),
    (NOTES,419,"modello-work","cand-7915","modello","The specific preparatory work sent to Ferdinand."),
    (NOTES,419,"banquet-work","cand-7915","Banquet","The painting named in the work title."),
    (NOTES,419,"anthony","cand-7917","Anthony","Printed personal-name form in the title; identity left for S3."),
    (NOTES,419,"cleopatra","cand-4157","Cleopatra","Reuse the existing title/person candidate."),
    (NOTES,419,"fabrizio","cand-7916","Fabrizio Spada-Varallo","Named as cardinal and patron of the final painting."),
    (NOTES,419,"pascoli","cand-7937","Pascoli","Surname-only author reference; not equated with the indexed Lione Pascoli."),
    (NOTES,419,"biblioteca-augusta","cand-3531","Biblioteca Augusta","Reuse the institution candidate."),
    (NOTES,419,"perugia","cand-3532","Perugia","Reuse the place candidate."),
    (NOTES,419,"ms1383","cand-3533","MS. 1383","Reuse the existing manuscript candidate."),
    (NOTES,420,"florence","cand-3397","Florence","Location named in the archival note."),
    (NOTES,420,"archivio-guardaroba","cand-7924","Archivio Mediceo, Guardaroba 1055","Specific archival locator; not independently consulted."),
    (NOTES,420,"dandini","cand-0899","Pietro Dandini","Reuse the indexed artist candidate."),
    (NOTES,420,"foggini","cand-1043","Giovanni Battista Foggini","Reuse the indexed artist candidate; index spelling is Giovan Battista."),
    (NOTES,420,"franchi","cand-1074","Antonio Franchi","Reuse the indexed artist candidate."),
    (NOTES,420,"botti","cand-0418","Francesco Botti","Reuse the indexed artist candidate."),
    (NOTES,420,"pinacci","cand-1931","Giuseppe Pinacci","Reuse the indexed artist candidate."),
    (NOTES,420,"panfi","cand-1826","Romolo Panfi","Reuse the indexed artist candidate."),
    (NOTES,420,"monari","cand-1684","Cristofano Monari","Reuse the indexed artist candidate."),
    (NOTES,420,"martini","cand-7925","Abate Orazio Martini","Person named as a reference."),
    (NOTES,421,"fogolari-83","cand-7894","Fogolari","Reuse the 1937 publication candidate."),
    (NOTES,421,"letter83","cand-7927","Letter 83","Specific numbered letter cited."),
    (NOTES,422,"ibid-fogolari","cand-7894","ibid.","Refers to Fogolari (1937) in note 3."),
    (NOTES,422,"letter6","cand-7928","Letters 6","Specific numbered letter citation."),
    (NOTES,422,"letter12","cand-7929","12","Specific numbered letter citation."),
    (NOTES,422,"letter28","cand-7900","28","Reuse the numbered and dated letter candidate."),
    (NOTES,422,"letter60","cand-7930","60","Specific numbered letter citation."),
    (NOTES,422,"letter71","cand-7908","71","Reuse the numbered letter candidate."),
    (NOTES,423,"fogolari-letter","cand-7894","Fogolari","Reuse the 1937 publication candidate."),
    (NOTES,423,"loth-letter","cand-7931","letter from Loth","Specific letter identified by date."),
    (NOTES,423,"loth-letter-author","cand-1442","Loth","Reuse the indexed painter candidate."),
    (NOTES,423,"prince","cand-1609","the Prince","Ferdinand, based on the page context."),
    (NOTES,423,"loth-copy","cand-7932","copy","Planned copy after Titian's St Peter Martyr."),
    (NOTES,423,"titian-work","cand-2635","St Peter Martyr","Reuse the indexed Titian work subentry."),
    (NOTES,423,"self-portrait","cand-7933","self portrait","Unidentified work sent to Florence in 1693."),
    (NOTES,423,"florence-loth","cand-3397","Florence","Destination of Loth's self-portrait."),
    (NOTES,423,"pitti","cand-7662","The Pitti","Reuse the Pitti place candidate."),
    (NOTES,423,"death-abel","cand-1444","Death of Abel","Reuse the indexed Loth work subentry."),
    (NOTES,423,"loth-inventory-pictures","cand-1442","his pictures","Pictures by Loth in Ferdinand's collection."),
    (NOTES,423,"ferdinand-inventory","cand-1609","Ferdinand","Reuse the Grand Prince candidate."),
    (NOTES,423,"inventory-1716","cand-7936","1716 inventory","The collection inventory cited by Haskell."),
    (NOTES,423,"fogolari-ref","cand-7894","Fogolari","Reuse the 1937 publication candidate.",1),
    (NOTES,423,"letter22","cand-7903","Letters 22","Reuse the numbered letter candidate."),
    (NOTES,423,"letter77","cand-7934","77","Specific numbered letter citation."),
    (NOTES,423,"ewald","cand-7935","Ewald, 1965","Unidentified catalogue reference."),
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
        "source_line_start": first, "source_line_end": last, "printed_page": 233,
        "pdf_physical_page": 39, "claim": claim, "speaker": "Haskell",
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
    make_statement("st-chp8-p233-modelli-purposes", P233,272,272,"cand-1609","cand-1674",
                   "collected_and_inspected_modelli_for_aesthetic_and_accuracy_checks",
                   "Completing the p.232 sentence, Haskell says Ferdinand insisted on seeing modelli both for aesthetic reasons and to check the accuracy of their content; he had collected modelli of pictures made for other patrons before this practice became common.",
                   "This is Haskell's account of Ferdinand's practice. The cited correspondence is not independently consulted.",
    ["cand-1609","cand-1674"],
    extras={"continued_from_segment_id":P232,
            "continued_from_statement_id":"st-chp8-p232-modelli-order-and-review-open",
            "continuation_status":"closed"}),
    make_statement("st-chp8-p233-painting-process", P233,272,272,"cand-1609",None,
                   "watched_artists_and_discussed_painting_procedure",
                   "Haskell says Ferdinand enjoyed watching artists work and discussing practical painting procedure, including colours and canvas thickness.",
                   "This is Haskell's description; the note does not identify particular artists or a specific painting.",
                   ["cand-1609","cand-3571"],extras={"relation_candidate":False}),
    make_statement("st-chp8-p233-gabbiani-employment", P233,273,274,"cand-1609","cand-1093",
                   "employed_gabbiani_despite_other_florentine_artists_better_matching_his_taste",
                   "Haskell says Ferdinand employed Gabbiani for a long time despite describing him as mediocre and Marattesque, while ignoring Gherardini, Sagrestani, and Galeotti, whose styles better matched Ferdinand's tastes; Haskell says the reasons are impossible to fathom.",
                   "The assessment and stated fit with Ferdinand's tastes are Haskell's judgments, not independently established evaluations of the artists.",
                   ["cand-1609","cand-1093","cand-7873","cand-1156","cand-2340","cand-1100","cand-3397","cand-1625"],
                   extras={"speaker_judgment":True,"relation_candidate":True}),
    make_statement("st-chp8-p233-bassi-loyalty", P233,274,275,"cand-1609","cand-0259",
                   "may_have_protected_bassi_out_of_loyalty_despite_doubts",
                   "Haskell suggests Ferdinand may have taken particular care not to hurt the ageing landscape painter Francesco Bassi out of loyalty, despite doubts about the value of Bassi's work.",
                   "Haskell presents loyalty as a possible explanation, not a settled motive; the doubt concerns the value of Bassi's work.",
                   ["cand-1609","cand-0259"],extras={"speaker_judgment":True,"relation_candidate":True}),
    make_statement("st-chp8-p233-gabbiani-control-and-venetian-ambition", P233,275,275,"cand-1609","cand-1093",
                   "used_gabbiani_under_his_control_to_express_venetian_artistic_ambitions",
                   "Haskell offers as a more likely explanation that Gabbiani's professed attachment to Venetian painting made him seem directly controllable by Ferdinand and useful for expressing the Prince's artistic ambitions.",
                   "This is Haskell's proposed explanation, qualified as more likely; it is not independently verified evidence of Ferdinand's motive.",
                   ["cand-1609","cand-1093","cand-5756","cand-1622"],
                   extras={"speaker_judgment":True,"relation_candidate":True}),
    make_statement("st-chp8-p233-gabbiani-1699-visit", P233,275,275,"cand-1093","cand-7922",
                   "visited_venice_in_1699_to_improve_colour_for_ferdinand",
                   "Haskell says Gabbiani made a special visit to Venice in 1699, aged 47, to oblige Ferdinand by improving his colour; Haskell judges the outcome hardly successful.",
                   "The trip and purpose are reported by Haskell; the evaluation of its success is the author's judgment.",
                   ["cand-1093","cand-7922","cand-3401","cand-1609"],
                   extras={"date":"1699","relation_candidate":True,"speaker_judgment":True}),
    make_statement("st-chp8-p233-sacconi-patronage", P233,275,276,"cand-1609","cand-2325",
                   "supported_and_sent_sacconi_to_venice_under_cassana",
                   "Haskell says Ferdinand took a deep interest in Sacconi's career, provided for him financially after his father's death, kept him working under Niccolò Cassana, and sent him to Venice.",
                   "The father's identity is not supplied. The passage reports patronage and travel but does not identify an external record.",
                   ["cand-1609","cand-2325","cand-7918","cand-0593","cand-3401"],
                   extras={"relation_candidate":True,
                           "ocr_corrections":[{"source_line":276,"ocr":"Niccolo","print":"Niccolò","basis":"CHP-8.pdf physical page 39"}]}),
    make_statement("st-chp8-p233-sacconi-orders", P233,276,276,"cand-1609","cand-2325",
                   "ordered_three_subject_pictures_for_sacconi_and_set_learning_goal",
                   "Haskell reports that Ferdinand issued repeated orders for a St Sebastian, a St Giustina, and a Bacchanal, specifying that Sacconi needed to learn to paint full-length figures.",
                   "These are subjects in orders; the passage does not establish that any of the three pictures was completed.",
                   ["cand-1609","cand-2325","cand-7919","cand-7920","cand-7921"],
                   extras={"relation_candidate":True}),
    make_statement("st-chp8-p233-sacconi-colour-and-exhibition", P233,276,277,"cand-1609","cand-2325",
                   "noted_improving_colour_exhibited_sacconi_at_corpus_domini",
                   "Haskell says Ferdinand noted Sacconi's improving colour under Cassana, warned him to be meno flemmatico, arranged for his pictures to be exhibited on Corpus Domini, and enjoyed their humour.",
                   "The warning is quoted through Haskell; the exhibition and response are reported in the book, not independently checked.",
                   ["cand-1609","cand-2325","cand-0593","cand-6024"],
    extras={"relation_candidate":True,"speaker":"Ferdinand as reported by Haskell"}),
    make_statement("st-chp8-p233-sacconi-outcome", P233,277,277,"cand-1609","cand-2325",
                   "judged_sacconi_unsuccessful_despite_venice_and_patronage",
                   "Haskell concludes that even Venice and an encouraging patron could not make much of Sacconi.",
                   "This is Haskell's evaluation of the artistic outcome.",
                   ["cand-1609","cand-2325","cand-3401"],extras={"speaker_judgment":True,"relation_candidate":False}),
    make_statement("st-chp8-p233-loth-employment", P233,278,279,"cand-1609","cand-1442",
                   "employed_loth_from_1691_until_about_seven_years_later",
                   "Haskell says Loth was already painting for Ferdinand by 1691 and continued until his death about seven years later; he must have met the artist on his first visit to Venice.",
                   "The contact on the first visit is explicitly inferential in Haskell ('must have'); the death interval is relative, not converted into an exact year.",
                   ["cand-1609","cand-1442","cand-3401"],extras={"date_from":"1691",
                   "date_to":"about seven years later","relation_candidate":True}),
    make_statement("st-chp8-p233-loth-and-responsive-artist", P233,279,279,"cand-1609","cand-1087",
                   "sought_loth_half_length_figures_and_found_responsive_venetian_artist",
                   "Haskell says that by Ferdinand's second Venice visit he made particular efforts to obtain half-length figures by Loth, whom he considered best at them, and found an artist of mediocre ability exceptionally responsive to his patronal pressure.",
                   "The effort to obtain Loth's figures does not prove acquisition. P.233 calls the second artist only 'an artist'; the adjacent p.234 account turns to Ferdinand's relations with Giannantonio Fumiani, so the referent is contextually linked to Fumiani and remains recorded with that qualification.",
                   ["cand-1609","cand-1442","cand-7923","cand-7938","cand-3401","cand-1087"],
                   extras={"relation_candidate":True,"speaker_judgment":True,
                           "cross_reference_segments":[{"segment_id":P234,"source_line_start":282,"source_line_end":284}]})
]

new_statements.extend([
    make_statement("st-chp8-p233-note1-trevisani-modello", NOTES,419,419,"cand-2650","cand-7915",
                   "sent_ferdinand_modello_of_banquet_painted_for_spada_varallo",
                   "Footnote 1 reports that Francesco Trevisani sent Ferdinand the modello for his Banquet of Anthony and Cleopatra, painted for Cardinal Fabrizio Spada-Varallo.",
                   "This is Haskell's footnote report and source locator, not independent verification of the painting or manuscript. The printed personal-name form Anthony is retained for S3 identity review.",
                   ["cand-2650","cand-1609","cand-7915","cand-7916","cand-7917","cand-3533","cand-7937","cand-3531","cand-3532"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate":True,"linked_body_statement_ids":["st-chp8-p233-modelli-purposes"],
                           "ocr_corrections":[{"source_line":419,"ocr":"ofhis","print":"of his","basis":"CHP-8.pdf physical page 39"},
                                              {"source_line":419,"ocr":"Banquet 0/","print":"Banquet of","basis":"CHP-8.pdf physical page 39"}]}),
    make_statement("st-chp8-p233-note2-medici-payments", NOTES,420,420,"cand-1609","cand-7924",
                   "footnote_locates_payments_to_florentine_artists_and_sculptors",
                   "Footnote 2 says payments to painters and sculptors in Florence are recorded in Archivio Mediceo, Guardaroba 1055; it names Pietro Dandini, Giovanni Battista Foggini, Antonio Franchi, Francesco Botti, Giuseppe Pinacci, Romolo Panfi, and Cristofano Monari, and refers the reader to Abate Orazio Martini.",
                   "The archive and cited publication were not independently consulted. Haskell characterizes the latter artists as very minor; that is the author's wording, not an independent assessment.",
                   ["cand-1609","cand-7924","cand-0899","cand-1043","cand-1074","cand-0418","cand-1931","cand-1826","cand-1684","cand-7925","cand-7926","cand-3397"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate":False,
                           "linked_body_statement_ids":["st-chp8-p233-gabbiani-employment"],
                           "ocr_corrections":[{"source_line":420,"ocr":"8 Payments","print":"2 Payments","basis":"CHP-8.pdf physical page 39"}]}),
    make_statement("st-chp8-p233-note3-fogolari-letter83", NOTES,421,421,None,"cand-7927",
                   "footnote_cites_fogolari_letter83",
                   "Footnote 3 cites Fogolari (1937), Letter 83, dated 17 March 1703.",
                   "This is a locator through Haskell; neither Fogolari's publication nor the letter was independently consulted.",
                   ["cand-7894","cand-7927"],text_layer="footnote citation",
                   extras={"relation_candidate":False,
                           "linked_body_statement_ids":["st-chp8-p233-bassi-loyalty"]}),
    make_statement("st-chp8-p233-note4-fogolari-letters", NOTES,422,422,None,None,
                   "footnote_cites_fogolari_letters_6_12_28_60_71",
                   "Footnote 4 cites Fogolari (1937), with special reference to Letters 6, 12, 28, 60, and 71.",
                   "This is a bibliographic locator; the cited publication and letters were not independently consulted.",
                   ["cand-7894","cand-7928","cand-7929","cand-7900","cand-7930","cand-7908"],
                   text_layer="footnote citation",
                   extras={"relation_candidate":False,
                           "linked_body_statement_ids":["st-chp8-p233-sacconi-patronage"]}),
    make_statement("st-chp8-p233-note5-loth-letter", NOTES,423,423,"cand-1442","cand-7931",
                   "letter_reports_gift_and_planned_copy_after_titian",
                   "Footnote 5 reports that a letter from Loth dated 14 August 1691 thanks Ferdinand for oil and wine and says Loth was about to begin a copy of Titian's St Peter Martyr.",
                   "The letter is reported through Fogolari (1937); it was not independently consulted. The planned copy is not recorded as completed.",
                   ["cand-1442","cand-7931","cand-1609","cand-7932","cand-2635","cand-7894"],
                   text_layer="footnote report and citation",
                   extras={"date":"1691-08-14","relation_candidate":True,
                           "linked_body_statement_ids":["st-chp8-p233-loth-employment"]}),
    make_statement("st-chp8-p233-note5-self-portrait", NOTES,423,423,"cand-1442","cand-7933",
                   "sent_self_portrait_to_florence_in_1693",
                   "Footnote 5 reports that Loth sent his self-portrait to Florence in 1693.",
                   "The report is cited through Fogolari (1937); the object and its present location are not identified.",
                   ["cand-1442","cand-7933","cand-3397","cand-7894"],
                   text_layer="footnote report",extras={"date":"1693","relation_candidate":True}),
    make_statement("st-chp8-p233-note5-death-abel", NOTES,423,423,"cand-1442","cand-1444",
                   "pitti_contains_loths_death_of_abel",
                   "Footnote 5 says the Pitti contains a Death of Abel by Loth.",
                   "This is Haskell's reported location and attribution, not an independent catalogue verification.",
                   ["cand-1442","cand-1444","cand-7662"],text_layer="footnote report",
                   extras={"relation_candidate":True}),
    make_statement("st-chp8-p233-note5-inventory", NOTES,423,423,"cand-1609","cand-1442",
                   "1716_inventory_records_six_loth_pictures_in_ferdinands_collection",
                   "Footnote 5 says six pictures by Loth appear in Ferdinand's collection in the 1716 inventory.",
                   "The inventory is cited through Haskell and was not independently consulted; individual pictures are not identified here.",
                   ["cand-1609","cand-1442","cand-7936"],text_layer="footnote report",
                   extras={"date":"1716","relation_candidate":True}),
    make_statement("st-chp8-p233-note5-supporting-references", NOTES,423,423,None,None,
                   "footnote_cites_p239_note5_fogolari_letters_22_77_and_ewald_1965",
                   "Footnote 5 additionally directs readers to p.239 note 5, Fogolari (1937), Letters 22 and 77, and catalogue entries in Ewald (1965).",
                   "These are bibliographic locators only; the cited pages, letters, and catalogue were not independently consulted.",
                   ["cand-7894","cand-7903","cand-7934","cand-7935"],
                   text_layer="footnote citation",extras={"relation_candidate":False})
])

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p232-modelli-order-and-review-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.232 modelli statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continuation_to_segment_id": P233,
    "continuation_to_source_line": 272, "continued_to_segment_id": P233,
    "continued_to_source_line": 272,
    "continuation_closed_by_statement_id": "st-chp8-p233-modelli-purposes",
})

for row in coverage_rows:
    if row["segment_id"] == P232:
        row.update({"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L251-257",
                    "note":"p.232 body and notes 1-4 at L415-418 reviewed against CHP-8.pdf physical page 34; the modelli continuation closes at p.233 L272."})
    elif row["segment_id"] == P233:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L272-279",
                    "note":"p.233 body and notes 1-5 at L419-423 reviewed against CHP-8.pdf physical page 39; p.232 continuation closes at L272. The final sentence begins at L279 and continues on p.234 L282; consolidated notes L424-461 remain."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L373-423",
                    "note":"Post-text notes through p.233 n.5 migrated and linked to cited body claims; consolidated notes L424-461 remain to be processed."})

preview = {
    "mode":"dry-run", "new_candidates":len(new_candidates),
    "new_mentions":len(new_mentions), "new_statements":len(new_statements),
    "closed_continuation":{"statement_id":prior_id,"segment_id":P233,"line":272},
    "open_continuation":{"segment_id":P233,"line":279,"next_segment":P234,"next_line":282},
    "coverage_updates":{P232:"complete",P233:"partial",NOTES:"L373-423 partial"},
    "ocr_corrections":["L275 artistic'ambitions -> artistic ambitions; protege -> protégé",
                       "L276 Niccolo -> Niccolò",
                       "L419 ofhis -> of his; 0/ -> of",
                       "L420 note number OCR 8 -> printed 2"]
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
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
print(json.dumps(preview, ensure_ascii=False, indent=2))
