"""Controlled S2 migration for Chapter 8 printed page 232 and notes 1–4."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
P231 = "chp-8:08_CHP-8_sec_ii:l238-249"
P232 = "chp-8:08_CHP-8_sec_ii:l251-257"
P233 = "chp-8:08_CHP-8_sec_ii:l271-279"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P231, P232, P233, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p232-reviewed-20261001"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


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
expected_coverage = {
    P231: ("reviewed", "partial", "L238-249"),
    P232: ("queued", "pending", ""),
    P233: ("queued", "pending", ""),
}
for segment_id, state in expected_coverage.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-414":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P232 for row in mention_rows + statement_rows):
    raise SystemExit("p.232 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7877", "Unidentified Veronese painting praised in Ferdinand's letters", "work", 254,
     "A painting referred to as 'a Veronese'; its title, present location, and precise identity are not supplied."),
    ("cand-7878", "Unidentified engraving praised by Ferdinand in his letters to Cassana", "work", 254,
     "The engraving is described as bizarre and in good taste; no subject, maker, or title is supplied."),
    ("cand-7879", "Unidentified artist asked by Ferdinand to paint something bizzarro", "person", 254,
     "The artist is not named; do not identify this person with the separate artist in the following example."),
    ("cand-7880", "Unidentified second artist told by Ferdinand to be meno flemmatico", "person", 254,
     "The artist is not named and is textually introduced as another artist; identity remains open."),
    ("cand-7881", "Unidentified painting by Francesco Maffei admired by Ferdinand", "work", 254,
     "Haskell reports that Ferdinand saw a Maffei painting for the first time and praised its impasto; the work is not titled."),
    ("cand-7882", "Rape of the Sabines by Virgilio Bassanino at Livorno", "work", 254,
     "A specific painting reported at Livorno; Ferdinand compares its appearance to a Strozzi, but no present identity or location is given."),
    ("cand-7883", "Unidentified Van Dyck bozzetto praised by Ferdinand", "work", 254,
     "The sketch is called spiritoso in the cited correspondence; subject, date, and present identity are unspecified."),
    ("cand-7884", "Unidentified Rubens painting examined by Ferdinand", "work", 254,
     "Haskell reports Ferdinand's suspicion about a later-added satyr and a difference of touch in the foliage; no title or location is supplied."),
    ("cand-7885", "Parmigianino's Madonna del Collo Lungo acquired by Ferdinand in 1698", "work", 255,
     "The passage reports the purchase and quotes a contemporary description; it does not identify the painting's present location or settle its version."),
    ("cand-7886", "Unidentified Lives of the Painters text read by Ferdinand", "archive", 254,
     "Haskell names no author, edition, or exact title; retain this as an unidentified text rather than guessing a specific Lives."),
    ("cand-7887", "Impasto as paint handling praised in Ferdinand's reported taste", "term", 254,
     "The Italian term appears in Haskell's report of Ferdinand's response to a Maffei painting; this candidate records the passage-level concept."),
    ("cand-7888", "Belle matière in Haskell's account of Ferdinand's sensitivity to paint quality", "term", 254,
     "Haskell uses the French phrase for the quality of the paint and relates it to eighteenth-century connoisseurs."),
    ("cand-7889", "Correct drawing as a priority in Haskell's account of Roman art theory", "term", 254,
     "A passage-level art-theoretical criterion contrasted with Ferdinand's preference for lively brushwork and colour."),
    ("cand-7890", "Ferdinand's unidentified court painter in the Ganymede collaboration anecdote", "person", 257,
     "The painter is not named here. Do not infer an identity from adjacent discussion of Gabbiani or other painters."),
    ("cand-7891", "Unidentified eagle supplied to Ferdinand's court painter for a Ganymede", "", 257,
     "The source does not establish whether this was a live animal, a model, or another aid; preserve the referent with type unresolved."),
    ("cand-7892", "Unidentified Ganymede composition in Ferdinand's collaboration anecdote", "work", 257,
     "The work is described only as a Ganymede; its maker, medium, and completion are not stated."),
    ("cand-7893", "Unidentified Fumiani composition for which Ferdinand requested a David figure", "work", 257,
     "The letter reports a requested figure and reworking; it does not establish an exact title or that a final work was completed."),
    ("cand-7894", "Gino Fogolari, Lettere pittoriche del Gran Principe Ferdinando di Toscana a Niccolò Cassana (1937)", "archive", 415,
     "Bibliography identifies the 1937 publication in Rivista del R. Istituto d'Archeologia e Storia dell'Arte, pp.145-186; the cited article and letters were not independently consulted."),
    ("cand-7895", "E. Robiony, La Madonna dal collo lungo di Parmigianino (1904)", "archive", 416,
     "Bibliography identifies the article in Rivista d'Arte, 1904, pp.19-22; the cited article was not independently consulted."),
    ("cand-7896", "Emilio Robiony, named as publisher of Ferdinand's letters", "person", 416,
     "The note names Emilio Robiony in connection with publication of two 1698 letters; no further identity details are added."),
    ("cand-7897", "Duke of Parma addressed in Ferdinand's 1698 letters (identity unresolved)", "person", 416,
     "The note gives only the title. Do not reuse or conflate other Duke of Parma candidates without S3 identity evidence."),
    ("cand-7898", "Ferdinand's letter to the Duke of Parma, 1698-10-11 (published by Robiony)", "archive", 416,
     "Identified by date and addressee in Haskell's note; the letter and its publication were not independently consulted."),
    ("cand-7899", "Ferdinand's letter to the Duke of Parma, 1698-12-01 (published by Robiony)", "archive", 416,
     "Identified by date and addressee in Haskell's note; the OCR's capital I in the day number is corrected against the page image."),
    ("cand-7900", "Fogolari (1937), Letter 28, 1699-01-09", "archive", 416,
     "The note gives the printed letter number and date; underlying correspondence and cited publication were not independently consulted."),
    ("cand-7901", "Fogolari (1937), Letter 45, 1699-05-16", "archive", 417,
     "The note gives the printed letter number and date; underlying correspondence and cited publication were not independently consulted."),
    ("cand-7902", "Ferdinand's letters to Niccolò Cassana discussed in Fogolari (1937)", "archive", 415,
     "A correspondence group discussed through the cited publication; individual archival witnesses, dates, and repository details remain unverified."),
    ("cand-7903", "Fogolari (1937), Letter 22", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7904", "Fogolari (1937), Letter 23", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7905", "Fogolari (1937), Letter 26", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7906", "Fogolari (1937), Letter 49", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7907", "Fogolari (1937), Letter 59", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7908", "Fogolari (1937), Letter 71", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7909", "Fogolari (1937), Letter 74", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7910", "Fogolari (1937), Letter 81", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7911", "Fogolari (1937), Letter 91", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7912", "Fogolari (1937), Letter 93", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7913", "Fogolari (1937), Letter 124", "archive", 415,
     "A specific numbered letter cited in note 1; date, archival witness, and repository are not supplied in this passage."),
    ("cand-7914", "Painter referred to only as a Strozzi in the Bassanino comparison", "person", 254,
     "The surname-only comparison does not identify which Strozzi is meant. Keep this local candidate distinct from the index item until S3 can assess identity."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"])
                 for row in candidate_rows if not row["index_entry_id"]}
new_keys = set()
expected_next_id = max(int(cid.removeprefix("cand-")) for cid in candidate_ids if cid.startswith("cand-")) + 1
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id != f"cand-{expected_next_id}":
        raise SystemExit(f"unexpected candidate sequence at {candidate_id}; expected cand-{expected_next_id}")
    expected_next_id += 1
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 415 else P232
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, source_line, suffix, candidate_id, surface, note, occurrence=0):
    mention_id = f"m-chp8-p232-{suffix}"
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
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


mentions = [
    (P232,252,"cassana","cand-0593","Niccolo Cassana","Name in OCR; the page image prints Niccolò."),
    (P232,252,"genoese","cand-1131","Genoese","Adjectival place reference to Genoa."),
    (P232,252,"cassana-agent","cand-0594","his agent","Role subentry for Cassana; keep its identity mapping for S3."),
    (P232,252,"venice","cand-3401","Venice","City where Cassana acted as Ferdinand's agent."),
    (P232,253,"letters-group","cand-7902","these letters","Coreference to Ferdinand's letters to Cassana."),
    (P232,253,"he-admired","cand-1609","he admired","Coreference to Ferdinand."),
    (P232,253,"venetians","cand-3401","Venetians","People/artists associated with Venice in the author's generalization."),
    (P232,253,"he-uses","cand-1609","he uses","Coreference to Ferdinand."),
    (P232,253,"gran-gusto","cand-1625","gran gusto","Ferdinand's indexed taste-in-painting entry; preserve Italian wording."),
    (P232,253,"buon-gusto","cand-1625","buon gusto","Ferdinand's indexed taste-in-painting entry; preserve Italian wording."),
    (P232,254,"veronese-work","cand-7877","a Veronese","Unidentified painting referred to by its maker's name."),
    (P232,254,"colour-taste","cand-1625","gran gusto di colore","Phrase from Ferdinand's reported appraisal."),
    (P232,254,"bizzarro-veronese","cand-1625","bizzarre","Quoted evaluative vocabulary in the Veronese appraisal."),
    (P232,254,"engraving","cand-7878","an engraving","Unidentified engraved work praised in the letters."),
    (P232,254,"bizzarro-engraving","cand-1625","molto bizzarro","Ferdinand's reported evaluation of the engraving."),
    (P232,254,"unnamed-artist-bizzarro","cand-7879","an artist working for him","Unidentified artist; do not infer identity from the surrounding passage."),
    (P232,254,"requested-thing","cand-1625","qualche cosa di bizzarro","Quoted instruction about the quality of a requested painting."),
    (P232,254,"unnamed-artist-less-flemmatico","cand-7880","another","A second, separately mentioned unnamed artist."),
    (P232,254,"maffei-artist","cand-1486","Maffei","Surname referring to Francesco Maffei in the index context."),
    (P232,254,"maffei-work-pronoun","cand-7881","its","Coreference to the unidentified Maffei painting."),
    (P232,254,"impasto-term","cand-7887","bellissimo impasto","Italian technical/aesthetic term applied to the painting's surface."),
    (P232,254,"livorno","cand-6716","Livorno","Place where Haskell reports the painting."),
    (P232,254,"rape-sabines-work","cand-7882","Rape of the Sabines","Work title; separate from the painter candidate."),
    (P232,254,"bassanino-artist","cand-0255","Virgilio Bassanino","Painter named as maker of the Rape of the Sabines."),
    (P232,254,"strozzi-comparison","cand-7914","a Strozzi","Surname-only stylistic comparison; leave identity unresolved."),
    (P232,254,"brio-brush","cand-1625","brio di pennello","Quoted appraisal of brushwork."),
    (P232,254,"van-dyck-artist","cand-0958","Van Dyck","Artist named through metonymic work reference."),
    (P232,254,"van-dyck-bozzetto","cand-7883","bozzetto","Unidentified sketch by Van Dyck."),
    (P232,254,"spiritoso","cand-1625","spiritoso","Quoted appraisal of the bozzetto."),
    (P232,254,"brushstroke","cand-1625","individual brushstroke","Haskell's summary of Ferdinand's taste."),
    (P232,254,"colour","cand-1625","colour","Aesthetic criterion in Haskell's summary."),
    (P232,254,"correct-drawing","cand-7889","correct drawing","Criterion attributed to Roman art theory by Haskell."),
    (P232,254,"roman-art-theory","cand-7889","Roman art theory","Theoretical context in Haskell's comparison."),
    (P232,254,"belle-matiere","cand-7888","belle matière","French phrase for paint quality in Haskell's account."),
    (P232,254,"ferdinand-sensitivity","cand-1609","Ferdinand","Named subject of Haskell's evaluative account."),
    (P232,254,"rubens-work","cand-7884","a Rubens","Unidentified painting referred to by maker's name."),
    (P232,254,"lives-of-painters","cand-7886","Lives of the Painters","Unidentified book/text; do not infer an author or edition."),
    (P232,255,"ferdinand-purchase","cand-1609","he","Coreference to Ferdinand."),
    (P232,255,"parmigianino","cand-1839","Parmigianino’s","Maker of the painting; work recorded separately."),
    (P232,255,"madonna-collo-lungo","cand-7885","Madonna del Collo Lungo","Specific painting, separate from its maker."),
    (P232,255,"raphael-quote","cand-2102","Raffaello","Artist named in the quoted appraisal; spelling retained as printed."),
    (P232,255,"ferdinand-patronage","cand-1609","his","Coreference to Ferdinand."),
    (P232,256,"baroque","cand-3569","Baroque","Art-historical period in Haskell's characterization."),
    (P232,257,"ferdinand-collaboration","cand-1609","Ferdinand","Named subject of the patronage account."),
    (P232,257,"court-painter","cand-7890","his court painter","Unidentified person; no identity inferred."),
    (P232,257,"eagle","cand-7891","an eagle","Referent preserved with type unresolved."),
    (P232,257,"ganymede-work","cand-7892","a Ganymede","Unidentified Ganymede composition; distinguish from the mythological figure."),
    (P232,257,"cassana-letter","cand-7901","a letter to Cassana","Footnote 4 identifies the cited item as Fogolari Letter 45."),
    (P232,257,"fumiani","cand-1087","Fumiani","Painter addressed in the reported letter."),
    (P232,257,"david","cand-4268","David","Biblical figure requested for the composition."),
    (P232,257,"modelli","cand-1674","tnodelli","OCR surface; the page image reads modelli."),
    (NOTES,415,"fogolari-note1","cand-7894","Fogolari","Citation to the 1937 publication identified in the book bibliography."),
    (NOTES,415,"letters-series-note1","cand-7902","Letters","Reference to the correspondence group discussed in Fogolari."),
    (NOTES,415,"letter22","cand-7903","22","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter23","cand-7904","23","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter26","cand-7905","26","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter49","cand-7906","49","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter59","cand-7907","59","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter71","cand-7908","71","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter74","cand-7909","74","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter81","cand-7910","81","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter91","cand-7911","91","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter93","cand-7912","93","Specific numbered letter in the Fogolari reference."),
    (NOTES,415,"letter124","cand-7913","124","Specific numbered letter in the Fogolari reference."),
    (NOTES,416,"ferdinand-letter-date1","cand-1609","Ferdinand","Letter writer named in the note."),
    (NOTES,416,"letter-october-1698","cand-7898","11 October","Date identifying the first letter."),
    (NOTES,416,"letter-december-1698","cand-7899","I December","OCR capital I; page image confirms 1 December."),
    (NOTES,416,"duke-parma","cand-7897","the Duke of Parma","Addressee; identity deliberately unresolved."),
    (NOTES,416,"robiony-person","cand-7896","Emilio Robiony","Person named in the publication note."),
    (NOTES,416,"fogolari-note2","cand-7894","Fogolari","Citation to the 1937 publication."),
    (NOTES,416,"letter28","cand-7900","Letter 28","Specific numbered and dated letter."),
    (NOTES,417,"hugford-note3","cand-7871","Hugford","Citation to an existing bibliography-identified work candidate."),
    (NOTES,417,"bartolozzi-note3","cand-7868","Bartolozzi","Citation to an existing bibliography-identified work candidate."),
    (NOTES,417,"elogio-note3","cand-7848","the Elogio","Citation to the existing Elogio work candidate."),
    (NOTES,417,"fogolari-note3","cand-7894","Fogolari","Citation to the 1937 publication."),
    (NOTES,417,"letter45-note3","cand-7901","Letter 45","Specific numbered and dated letter."),
    (NOTES,418,"fogolari-note4","cand-7894","Fogolari","Citation to the 1937 publication."),
    (NOTES,418,"letter45-note4","cand-7901","Letter 45","Same letter as p.232 note 3."),
]
for row in mentions:
    mention(*row)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate, claim,
                   qualification, mentioned, text_layer="body", extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(candidate_id not in candidate_ids for candidate_id in [subject, obj, *mentioned] if candidate_id):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {"source_line_start": first, "source_line_end": last, "printed_page": 232,
                  "pdf_physical_page": 34, "claim": claim, "speaker": "Haskell",
                  "text_layer": text_layer, "qualification": qualification,
                  "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj, "predicate": predicate,
            "qualifiers": qualifiers, "original_quote": quote(segment_id, first, last),
            "origin": "book", "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p232-cassana-agent", P232,252,253,"cand-1609","cand-0593",
                   "employed_cassana_as_venice_agent_from_1698",
                   "Completing the p.231 sentence, Haskell identifies Niccolò Cassana as a Genoese artist who acted as Ferdinand's agent in Venice from 1698.",
                   "The date is reported with footnote 1; the page image confirms the raised note marker after 1698. Cassana's indexed person and role entries remain for S3 identity review.",
                   ["cand-1609","cand-0593","cand-0594","cand-1131","cand-3401","cand-7902"],
                   extras={"continued_from_segment_id":P231,"continued_from_statement_id":"st-chp8-p231-artists-recur-in-ferdinand-letters-open","continuation_status":"closed","relation_candidate":True,"date_from":"1698","ocr_corrections":[{"source_line":252,"ocr":"Niccolo","print":"Niccolò","basis":"CHP-8.pdf physical page 34"},{"source_line":253,"ocr":"1698?","print":"1698.¹","basis":"CHP-8.pdf physical page 34"}]}),
    make_statement("st-chp8-p232-ferdinand-approval-vocabulary", P232,253,254,"cand-1609","cand-1625",
                   "used_gran_gusto_and_buon_gusto_to_express_approval",
                   "Haskell says Ferdinand's letters most often express approval with gran gusto or buon gusto, vague terms that nevertheless suggest relish for painting.",
                   "This is Haskell's characterization of Ferdinand's vocabulary; the letters are accessed through the cited publication, not independently consulted.",
                   ["cand-1609","cand-1625","cand-7902"],extras={"relation_candidate":False,"ocr_corrections":[{"source_line":253,"ocr":"sec","print":"see","basis":"CHP-8.pdf physical page 34"}]}),
    make_statement("st-chp8-p232-veronese-colour-invention", P232,254,254,"cand-1609","cand-7877",
                   "praised_unidentified_veronese_painting_for_colour_and_invention",
                   "Ferdinand praised an unidentified Veronese painting for its colour and bizarre invention, saying it seemed newly emerged from its maker's brush.",
                   "Haskell quotes Ferdinand through correspondence; the painting's title and location are not identified. The quotation's Italian spelling is transcribed from the page image.",
                   ["cand-1609","cand-2755","cand-7877","cand-1625","cand-7902"],
                   extras={"speaker":"Ferdinand (quoted through Haskell)","text_layer":"quoted letter as reported by Haskell","relation_candidate":False,"ocr_corrections":[{"source_line":254,"ocr":"Tinvenzione","print":"l’invenzione","basis":"CHP-8.pdf physical page 34"},{"source_line":254,"ocr":"adcsso","print":"adesso","basis":"CHP-8.pdf physical page 34"},{"source_line":254,"ocr":"penello dcH’Autore","print":"pennello dell’Autore","basis":"CHP-8.pdf physical page 34"}]}),
    make_statement("st-chp8-p232-engraving-appraisal", P232,254,254,"cand-1609","cand-7878",
                   "called_engraving_bizzarro_and_in_good_taste",
                   "Ferdinand described an unidentified engraving as molto bizzarro and di buon gusto.",
                   "The engraving is not titled and its maker is not identified; the evaluation is transmitted through Haskell's account of the letters.",
                   ["cand-1609","cand-7878","cand-1625","cand-7902"],
                   extras={"speaker":"Ferdinand (quoted through Haskell)","text_layer":"quoted letter as reported by Haskell","relation_candidate":False}),
    make_statement("st-chp8-p232-instructions-to-unnamed-artists", P232,254,254,"cand-1609",None,
                   "instructed_two_unnamed_artists_on_pictorial_character",
                   "Haskell reports that Ferdinand asked one unnamed artist working for him to paint something bizzarro and told another to be meno flemmatico.",
                   "The two artists are distinct in the wording but remain unidentified; the passage does not supply the works or establish completion.",
                   ["cand-1609","cand-7879","cand-7880","cand-1625","cand-7902"],
                   extras={"speaker":"Ferdinand (quoted through Haskell)","text_layer":"reported instructions in correspondence","relation_candidate":True}),
    make_statement("st-chp8-p232-maffei-painting-impasto", P232,254,254,"cand-1609","cand-7881",
                   "admired_impasto_of_first_seen_maffei_painting",
                   "Haskell says Ferdinand was delighted by the bellissimo impasto of a Maffei painting he saw for the first time.",
                   "The maker is indexed as Francesco Maffei, but the work is unidentified; this report is not an independently verified attribution.",
                   ["cand-1609","cand-1486","cand-7881","cand-7887","cand-1625","cand-7902"],
                   extras={"speaker":"Ferdinand (quoted through Haskell)","text_layer":"quoted letter as reported by Haskell","relation_candidate":False}),
    make_statement("st-chp8-p232-bassanino-rape-sabines", P232,254,254,"cand-1609","cand-7882",
                   "saw_bassanino_rape_of_sabines_at_livorno_and_compared_it_to_strozzi",
                   "Haskell reports a Rape of the Sabines by Virgilio Bassanino at Livorno that Ferdinand thought looked like a Strozzi and praised for its brio di pennello.",
                   "The comparison is Ferdinand's reported appraisal, not an attribution to Strozzi; the painting's present identity and location are unspecified.",
                   ["cand-1609","cand-6716","cand-0255","cand-7882","cand-7914","cand-1625","cand-7902"],
                   extras={"speaker":"Ferdinand (quoted through Haskell)","text_layer":"reported appraisal in correspondence","relation_candidate":False}),
    make_statement("st-chp8-p232-vandyck-bozzetto", P232,254,254,"cand-1609","cand-7883",
                   "called_van_dyck_bozzetto_spiritoso",
                   "Haskell says Ferdinand called an unidentified Van Dyck bozzetto spiritoso.",
                   "The sketch's subject, date, and current identity are not provided; the appraisal is reported rather than independently checked.",
                   ["cand-1609","cand-0958","cand-7883","cand-1625","cand-7902"],
                   extras={"speaker":"Ferdinand (quoted through Haskell)","text_layer":"quoted letter as reported by Haskell","relation_candidate":False}),
    make_statement("st-chp8-p232-brushstroke-colour-vs-drawing", P232,254,254,"cand-1609","cand-1625",
                   "valued_lively_brushstroke_and_colour_above_correct_drawing",
                   "Haskell interprets Ferdinand's taste as valuing the liveliness of the individual brushstroke and colour far above correct drawing, which played a vital role in Roman art theory.",
                   "This is Haskell's comparative art-historical interpretation, not a direct quotation or an independently established account of all Roman theory.",
                   ["cand-1609","cand-1625","cand-7889"],extras={"speaker_judgment":True,"relation_candidate":False}),
    make_statement("st-chp8-p232-belle-matiere", P232,254,254,"cand-1609","cand-7888",
                   "showed_sensitivity_to_quality_of_paint_belle_matiere",
                   "Haskell says Ferdinand showed acute sensitivity to the actual quality of paint, the belle matière later attractive to eighteenth-century connoisseurs.",
                   "The phrase and historical comparison belong to Haskell's interpretation; no individual connoisseur or specific work is identified.",
                   ["cand-1609","cand-7888","cand-1625"],extras={"speaker_judgment":True,"relation_candidate":False}),
    make_statement("st-chp8-p232-artistic-discrimination", P232,254,254,"cand-1609","cand-1625",
                   "combined_sensitivity_to_paint_with_understanding_of_artistic_quality",
                   "Haskell contrasts Ferdinand's sensitivity to paint and artistic quality with that of most aristocratic collectors, saying this enabled discrimination in his appreciation of pictures.",
                   "This is the author's evaluative comparison; the collectors are a general group, not individually identified.",
                   ["cand-1609","cand-1625"],extras={"speaker_judgment":True,"relation_candidate":False}),
    make_statement("st-chp8-p232-rubens-examination", P232,254,254,"cand-1609","cand-7884",
                   "suspected_later_satyr_and_different_touch_in_rubens_foliage",
                   "Haskell reports that Ferdinand suspected one satyr in an unidentified Rubens painting had been added later and noticed a difference of touch in the foliage.",
                   "This is Ferdinand's reported suspicion and visual observation, not a settled attribution or conservation finding; the picture is unidentified.",
                   ["cand-1609","cand-2293","cand-7884","cand-7902"],
                   extras={"speaker":"Ferdinand as reported by Haskell","relation_candidate":False}),
    make_statement("st-chp8-p232-packing-instructions", P232,254,254,"cand-1609",None,
                   "gave_detailed_practical_picture_packing_instructions",
                   "Haskell says Ferdinand gave detailed practical instructions for packing a picture.",
                   "The picture, recipient, and specific instructions are not identified in this sentence.",
                   ["cand-1609"],extras={"relation_candidate":False}),
    make_statement("st-chp8-p232-read-lives-painters", P232,254,254,"cand-1609","cand-7886",
                   "read_unidentified_lives_of_painters_text",
                   "Haskell says Ferdinand read through a text referred to as Lives of the Painters.",
                   "No author, edition, or exact title is supplied; it is not identified with a specific canonical work.",
                   ["cand-1609","cand-7886"],extras={"relation_candidate":False}),
    make_statement("st-chp8-p232-jokes-on-attribution", P232,254,254,"cand-1609",None,
                   "joked_about_people_unable_to_distinguish_artists_work",
                   "Haskell says Ferdinand joked about people who could not distinguish one artist's work from another's.",
                   "The joke is summarized rather than quoted; its target and occasion are not identified.",
                   ["cand-1609"],extras={"speaker_judgment":True,"relation_candidate":False}),
    make_statement("st-chp8-p232-madonna-collo-lungo-purchase", P232,255,255,"cand-1609","cand-7885",
                   "bought_madonna_del_collo_lungo_in_1698",
                   "Haskell reports that Ferdinand bought Parmigianino's Madonna del Collo Lungo in 1698 and quotes its description as designed as if by Raphael and finished with soul.",
                   "The purchase and quoted appraisal are reported through Haskell and the cited letters; the work's present location and precise version are not established here.",
                   ["cand-1609","cand-1839","cand-1840","cand-7885","cand-2102","cand-1625","cand-7894","cand-7895","cand-7898","cand-7899","cand-7900"],
                   extras={"date":"1698","relation_candidate":True,"speaker":"Ferdinand (quoted through Haskell)","text_layer":"reported purchase and quoted letter","ocr_corrections":[{"source_line":255,"ocr":"sinita","print":"finita","basis":"CHP-8.pdf physical page 34"},{"source_line":255,"ocr":"1’anima","print":"l’anima","basis":"CHP-8.pdf physical page 34"},{"source_line":255,"ocr":"l’anima’2","print":"l’anima.²","basis":"CHP-8.pdf physical page 34"}]}),
    make_statement("st-chp8-p232-contemporary-patronage-conflict", P232,255,256,"cand-1609","cand-3569",
                   "personal_taste_conflicted_with_contemporary_art_theory",
                   "Haskell says Ferdinand's refinement affected his collecting and mattered to his patronage, but the general direction of art theory conflicted with his tastes and made suitable painters difficult to find, apart from two conspicuous exceptions.",
                   "The two exceptions are not named here; the account is Haskell's interpretation rather than a claim that all contemporary painters shared one doctrine.",
                   ["cand-1609","cand-1622","cand-3569"],extras={"speaker_judgment":True,"relation_candidate":False}),
    make_statement("st-chp8-p232-collaborative-patronage", P232,257,257,"cand-1609","cand-1623",
                   "collaborated_with_painters_more_than_was_usual",
                   "Haskell characterizes Ferdinand's patronage as involving greater collaboration between prince and painter than was usual.",
                   "This is Haskell's comparative generalization; the passage does not define a population or measure of usual practice.",
                   ["cand-1609","cand-1623"],extras={"speaker_judgment":True,"relation_candidate":False}),
    make_statement("st-chp8-p232-eagle-ganymede-example", P232,257,257,"cand-1609","cand-7892",
                   "sent_eagle_to_court_painter_for_ganymede_composition",
                   "Haskell gives an example in which Ferdinand sent his unnamed court painter an eagle to help with a Ganymede composition.",
                   "The eagle's status and the composition's maker, medium, and completion are not specified; the painter is not inferred from adjacent text.",
                   ["cand-1609","cand-7890","cand-7891","cand-7892","cand-3436"],extras={"relation_candidate":True}),
    make_statement("st-chp8-p232-fumiani-david-instruction", P232,257,257,"cand-1609","cand-1087",
                   "in_letter_to_cassana_requested_fumiani_retain_david_figure_and_rework_composition",
                   "Haskell quotes Ferdinand's letter to Cassana instructing Fumiani that only the figure of David was wanted, that it could be removed, and that the work should be done 'in our way'.",
                   "The exact composition is unidentified; the letter is located by note 4 as Fogolari Letter 45 but was not independently consulted.",
                   ["cand-1609","cand-0593","cand-1087","cand-4268","cand-7893","cand-7901","cand-7894"],
                   extras={"relation_candidate":True,"speaker":"Ferdinand (quoted in letter to Cassana, through Haskell)","text_layer":"quoted letter as reported by Haskell"}),
    make_statement("st-chp8-p232-modelli-order-and-review-open", P232,257,257,"cand-1609","cand-1674",
                   "insisted_on_seeing_modelli_of_ordered_pictures_open",
                   "Haskell says Ferdinand insisted on always seeing modelli of pictures he ordered; the sentence continues with the purposes of this practice on p.233.",
                   "The continuation is open at p.232 L257 and must be closed against p.233 L272 before semantic completion.",
                   ["cand-1609","cand-1674"],extras={"continuation_status":"open","continuation_expected_segment_id":P233,"continuation_expected_source_line":272,"relation_candidate":False,"ocr_corrections":[{"source_line":257,"ocr":"tnodelli","print":"modelli","basis":"CHP-8.pdf physical page 34"}]}),
    make_statement("st-chp8-p232-note1-fogolari-letter-citations", NOTES,415,415,None,"cand-7894",
                   "footnote_cites_fogolari_and_specific_letters",
                   "Footnote 1 cites Fogolari (1937), highlighting Letters 22, 23, 26, 49, 59, 71, 74, 81, 91, 93 and 124.",
                   "This is a bibliographic locator; the article and individual letters were not independently consulted and their archival witnesses are not established.",
                   ["cand-7894","cand-7902","cand-7903","cand-7904","cand-7905","cand-7906","cand-7907","cand-7908","cand-7909","cand-7910","cand-7911","cand-7912","cand-7913"],
                   text_layer="footnote citation",extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p232-cassana-agent","st-chp8-p232-ferdinand-approval-vocabulary"]}),
    make_statement("st-chp8-p232-note2-parma-letters", NOTES,416,416,"cand-1609","cand-7897",
                   "footnote_locates_purchase_claim_in_two_1698_letters_and_fogolari_letter28",
                   "Footnote 2 cites two letters from Ferdinand to the Duke of Parma dated 11 October and 1 December 1698, published by Emilio Robiony, and Fogolari Letter 28 of 9 January 1699.",
                   "The note does not identify the Duke of Parma beyond title; the cited letters and publications were not independently consulted. The OCR date 'I December' is corrected against the page image.",
                   ["cand-1609","cand-7895","cand-7896","cand-7897","cand-7898","cand-7899","cand-7900","cand-7894"],
                   text_layer="footnote citation",extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p232-madonna-collo-lungo-purchase"],"ocr_corrections":[{"source_line":416,"ocr":"I December 1698","print":"1 December 1698","basis":"CHP-8.pdf physical page 34"}]}),
    make_statement("st-chp8-p232-note3-supporting-sources", NOTES,417,417,None,None,
                   "footnote_cites_biographies_and_fogolari_letter45",
                   "Footnote 3 cites Hugford, Bartolozzi, the Elogio, and Fogolari (1937), Letter 45 of 16 May 1699.",
                   "The cited sources are locators only; the works and letter were not independently consulted.",
                   ["cand-7871","cand-7868","cand-7848","cand-7894","cand-7901"],
                   text_layer="footnote citation",extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p232-eagle-ganymede-example","st-chp8-p232-fumiani-david-instruction"],"ocr_corrections":[{"source_line":417,"ocr":"193 7","print":"1937","basis":"CHP-8.pdf physical page 34"}]}),
    make_statement("st-chp8-p232-note4-fogolari-letter45", NOTES,418,418,None,"cand-7901",
                   "footnote_identifies_cassana_letter_as_fogolari_letter45",
                   "Footnote 4 locates the letter to Cassana as Fogolari (1937), Letter 45 of 16 May 1699.",
                   "This is a locator through Haskell; neither Fogolari's text nor the underlying letter was independently consulted.",
                   ["cand-7894","cand-7901"],text_layer="footnote citation",
                   extras={"relation_candidate":False,"linked_body_statement_ids":["st-chp8-p232-fumiani-david-instruction"]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p231-artists-recur-in-ferdinand-letters-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.231 letter statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({"continuation_status":"closed","continuation_to_segment_id":P232,
                                   "continuation_to_source_line":252,"continued_to_segment_id":P232,
                                   "continued_to_source_line":252,
                                   "continuation_closed_by_statement_id":"st-chp8-p232-cassana-agent"})

for row in coverage_rows:
    if row["segment_id"] == P231:
        row.update({"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L238-249",
                    "note":"p.231 body and notes 1–6 at L409–414 reviewed against CHP-8.pdf physical page 33; final sentence closed at p.232 L252–253."})
    elif row["segment_id"] == P232:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L251-257",
                    "note":"p.232 body and notes 1–4 at L415–418 reviewed against CHP-8.pdf physical page 34; final modelli sentence continues at p.233 L272."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L373-418",
                    "note":"Post-text notes through p.232 n.4 migrated; later consolidated notes remain to be processed."})

preview = {"mode":"dry-run","candidate_additions":len(new_candidates),"mention_additions":len(new_mentions),
           "statement_additions":len(new_statements),"closed_continuation":{"statement_id":prior_id,"segment_id":P232,"line":252},
           "open_continuation":{"statement_id":"st-chp8-p232-modelli-order-and-review-open","segment_id":P233,"line":272},
           "coverage":{P231:"complete",P232:"partial",NOTES:"L373-418 partial"},
           "ocr_corrections":["L252 Niccolo -> Niccolò","L253 1698? -> 1698.¹; sec -> see","L254 Italian quote OCR corrections","L255 sinita -> finita; 1’anima -> l’anima; footnote 2 marker","L257 tnodelli -> modelli","L416 I December -> 1 December","L417 193 7 -> 1937"]}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (TABLES / "entity-candidates.csv", TABLES / "mentions.csv", TABLES / "book-statements.jsonl", TABLES / "s2-coverage.csv"):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)
patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
patched_statements.extend(new_statements)
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", patched_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, coverage_rows)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
