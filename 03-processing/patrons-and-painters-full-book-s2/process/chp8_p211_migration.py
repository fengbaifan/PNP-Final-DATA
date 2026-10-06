"""Controlled S2 migration for chapter 8 printed p.211 and its omitted notes.

Default invocation is a read-only dry run. The supplemental transcription is
derived from CHP-8.pdf physical page 9; immutable OCR sources remain untouched.
"""
from __future__ import annotations

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
BODY_REL = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
NOTES_REL = "02-sources/02-Markdown/08_CHP-8_sec_i_notes_p211_visual-transcription.md"
BODY_ID = "chp-8:08_CHP-8_sec_i:l84-96"
NOTES_ID = "chp-8:08_CHP-8_sec_i_notes_p211_visual-transcription:l1-4"
PREVIOUS_ID = "chp-8:08_CHP-8_sec_i:l72-82"
NEXT_ID = "chp-8:08_CHP-8_sec_i:l98-106"
PREVIOUS_OPEN = "st-chp8-p210-house-inhabited-by-three-rosso-brothers-open"
BACKUP_SUFFIX = ".bak-s2-chp8-p211-20260930"
EXPECTED_MAX_CANDIDATE = 7488


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)
segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}


def load_segment(segment_id: str, relative_path: str, start: int, end: int):
    meta = segments.get(segment_id)
    if not meta or meta["source_file"] != relative_path or (int(meta["line_start"]), int(meta["line_end"])) != (start, end):
        raise SystemExit(f"segment metadata changed; review before migration: {segment_id}")
    path = ROOT / relative_path
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset fingerprint changed: {relative_path}")
    all_lines = path.read_text(encoding="utf-8-sig").splitlines()
    sliced = all_lines[start - 1:end]
    text = "\n".join(sliced)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"source line-slice hash changed: {segment_id}")
    cov = coverage_by_id.get(segment_id, {})
    if cov.get("disposition") != "queued" or cov.get("migration_status") != "pending":
        raise SystemExit(f"expected queued/pending coverage: {segment_id}")
    if any(row["segment_id"] == segment_id for row in mention_rows + statement_rows):
        raise SystemExit(f"mentions or statements already exist: {segment_id}")
    return meta, all_lines, sliced, text


body_meta, body_all_lines, body_lines, body_text = load_segment(BODY_ID, BODY_REL, 84, 96)
notes_meta, notes_all_lines, notes_lines, notes_text = load_segment(NOTES_ID, NOTES_REL, 1, 4)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")


def candidate(cid, name, typ, detail, source_segment, line):
    return {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": typ, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{source_segment}#L{line}",
    }


new_candidates = [
    candidate("cand-7489", "Del Rosso family in Florence", "family", "Florentine mercantile family represented here by Andrea, Lorenzo, Ottavio and Nicola del Rosso; keep distinct from their grandfather Andrea.", BODY_ID, 85),
    candidate("cand-7490", "Mainz", "place", "City named as the origin of two modern glass pictures in the del Rosso collection.", BODY_ID, 88),
    candidate("cand-7491", "Volterra", "place", "City where Ottavio del Rosso served as bishop; the specific see is not otherwise described here.", BODY_ID, 87),
    candidate("cand-7492", "Poland", "place", "Destination named for an unidentified picture sent by the del Rosso brothers.", BODY_ID, 88),
    candidate("cand-7493", "Two modern pictures on glass in the del Rosso collection", "work", "A source-described pair acquired from Mainz; individual titles, makers and later locations are not supplied.", BODY_ID, 88),
    candidate("cand-7494", "Two pictures attributed to Albrecht Dürer in the del Rosso collection", "work", "A source-described pair said in Andrea del Rosso's inventory to have been bought in Cologne; individual titles are not supplied.", BODY_ID, 88),
    candidate("cand-7495", "Carlo Dolci's Flight into Egypt sent to Lord Exeter", "work", "A small picture mentioned in the p.211 text and footnote 3; the exact surviving object is not independently established here.", BODY_ID, 88),
    candidate("cand-7496", "Unidentified picture sent by the del Rosso brothers to Poland", "work", "The text distinguishes this picture from Carlo Dolci's Flight into Egypt but gives no title, maker or destination beyond Poland.", BODY_ID, 88),
    candidate("cand-7497", "Papal postal services", "institution", "Named as the service whose director-general was Andrea del Rosso; institutional history and formal name are not supplied.", BODY_ID, 86),
    candidate("cand-7498", "Florentine flour monopoly shared by Andrea and Lorenzo del Rosso", "procedure", "A lucrative nine-year concession beginning in 1676 is described in the body and documented in footnote 2.", BODY_ID, 85),
    candidate("cand-7499", "Cinelli's 1677 account of the del Rosso collection", "archive", "A collection account identified by Haskell as one of the principal sources; Cinelli's full identity and the account's title are not supplied.", NOTES_ID, 1),
    candidate("cand-7500", "Andrea del Rosso's 1689 inventory of the family collection", "archive", "The complete inventory was drawn up by Andrea twelve years after the 1677 account and published in Gualandi, volume II, pp.113-128; cited, not independently consulted.", NOTES_ID, 1),
    candidate("cand-7501", "Gualandi, volume II, cited publication", "archive", "Publication location for Andrea del Rosso's inventory, volume II, pp.113-128; full title and edition are not given in this note.", NOTES_ID, 1),
    candidate("cand-7502", "Passerini 19(25), Informazione sopra la Nobiltà della Famiglia del Rosso di Firenze", "archive", "A 1747 manuscript genealogy cited from Passerini's manuscript collections; title spelling follows the visual transcription and the manuscript was not independently consulted.", NOTES_ID, 2),
    candidate("cand-7503", "Biblioteca Nazionale (branch unspecified)", "institution", "Named as the holding library for the Passerini manuscripts and Poligrafo Gargano; the precise branch is not identified in this footnote.", NOTES_ID, 2),
    candidate("cand-7504", "Poligrafo Gargano manuscript collection", "archive", "A collection of sources in the same Biblioteca Nazionale cited by Haskell; contents are not individually identified here.", NOTES_ID, 2),
    candidate("cand-7505", "Giuseppe Manini", "person", "Named with Salvino Salvini as an author of brief accounts of Andrea and Ottavio del Rosso; work titles and dates are not supplied.", BODY_ID, 90),
    candidate("cand-7506", "Salvino Salvini", "person", "Named with Giuseppe Manini as an author of brief accounts of Andrea and Ottavio del Rosso; work titles and dates are not supplied.", BODY_ID, 90),
    candidate("cand-7507", "Lorenzo del Rosso's will", "archive", "Will cited in the Archivio di Stato notarial protocols; the footnote says its only picture-related bequest was a Caravaggio painting to Coriolano Montemagni.", BODY_ID, 92),
    candidate("cand-7508", "Ottavio del Rosso's will", "archive", "Will cited in the Archivio di Stato notarial protocols; Haskell says it contains no picture bequest of interest here.", BODY_ID, 92),
    candidate("cand-7509", "Archivio di Stato (branch unspecified)", "institution", "Named repository for the del Rosso wills and the Florentine flour decree; keep the archival institution distinct from its cited records.", BODY_ID, 92),
    candidate("cand-7510", "Nicola Taddei", "person", "Notary named in the protocol holding Lorenzo del Rosso's will; identity is not otherwise established in this passage.", BODY_ID, 92),
    candidate("cand-7511", "Niccolò Salvetti", "person", "Notary named in the protocol holding Ottavio del Rosso's will; the source OCR omits the accent, checked against the page image.", BODY_ID, 93),
    candidate("cand-7512", "Coriolano Montemagni", "person", "Named recipient of Lorenzo del Rosso's bequest of a Caravaggio picture; described as secretary of state to His Royal Highness.", BODY_ID, 93),
    candidate("cand-7513", "Caravaggio (p.211 will reference)", "person", "The artist is named in the will report; identity alignment with existing Caravaggio candidates is deferred to S3.", BODY_ID, 94),
    candidate("cand-7514", "Caravaggio painting of S. Gio. Decollato in Lorenzo del Rosso's will", "work", "A bequeathed picture described by subject and dimensions in the quoted will; do not identify it with another known Caravaggio work without evidence.", BODY_ID, 94),
    candidate("cand-7515", "Two letters from Sebastiano Resta to Francesco Gabburri", "archive", "Two letters cited by Haskell through Bottari, volume II, pp.100 and 104; the letters and cited pages were not independently consulted.", BODY_ID, 95),
    candidate("cand-7516", "Bottari, volume II, cited publication", "archive", "Publication in which Haskell says the two Resta-to-Gabburri letters appeared; full title and edition are not specified in this note.", BODY_ID, 95),
    candidate("cand-7517", "Florentine flour monopoly decree of 1 June 1676", "archive", "Decree granting the Appalto Generale for nine years, cited in Archivio di Stato, Miscellanea Medicea 533, Uffizio delle Farine; cited, not independently consulted.", NOTES_ID, 3),
    candidate("cand-7518", "Gio:Batta Dei", "person", "Name given as the author/sender in the title of the 1747 Passerini genealogy; full identity is unresolved.", NOTES_ID, 2),
    candidate("cand-7519", "Falconieri addressees of the 1747 del Rosso genealogy", "family", "Plural addressees named in the title of Passerini 19(25); individual recipients are not identified.", NOTES_ID, 2),
]
new_candidate_ids = {row["candidate_id"] for row in new_candidates}
if len(new_candidate_ids) != len(new_candidates) or new_candidate_ids & candidate_ids:
    raise SystemExit("planned candidate IDs collide")
natural = {(r["canonical_name"].casefold(), (r.get("suggested_type") or "").casefold()) for r in candidate_rows}
for row in new_candidates:
    key = (row["canonical_name"].casefold(), row["suggested_type"].casefold())
    if key in natural:
        raise SystemExit(f"candidate natural-key collision: {row['canonical_name']}")
    natural.add(key)


# (segment id, absolute source line, exact source surface, candidate id, note, occurrence)
M, N = BODY_ID, NOTES_ID
mention_specs = [
    (M,85,"del Rosso","cand-7489","Completes the p.210 first names with the surname and closes the open sentence.",1),
    (M,85,"Florentine","cand-1041","Citizenship and social advancement are described in the Florence context.",1),
    (M,85,"Cavalieri di Santo Stefano","cand-0612","Chivalric order named as a stage in the family's advancement.",1),
    (M,85,"Andrea","cand-2275","Andrea del Rosso, the eldest brother; the source gives his birth year as 1640.",1),
    (M,85,"Lorenzo","cand-2282","Named as Andrea's partner in the flour monopoly.",1),
    (M,85,"Andrea","cand-2275","Andrea del Rosso, later a senator and director-general of papal postal services.",2),
    (M,85,"Rome","cand-4490","City where Andrea is said to have died.",1),
    (M,85,"exhibitions","cand-0134","The indexed art-exhibitions candidate covers p.211; this occurrence does not identify an individual event.",1),
    (M,85,"S.","cand-6052","First OCR fragment of S. Salvatore in Lauro; name continues on the next line.",1),
    (M,86,"Salvatore in Lauro","cand-6052","Completes the church name split across the source line break.",1),
    (M,86,"papal postal services","cand-7497","Service named as Andrea's office; no additional institutional identity inferred.",1),
    (M,86,"Ottavio","cand-2286","Ottavio del Rosso entered the Church.",1),
    (M,87,"Bjshop","cand-2286","OCR form; p.211 print reads Bishop. The role is reported of Ottavio.",1),
    (M,87,"Volterra","cand-7491","City of Ottavio's bishopric.",1),
    (M,88,"the brothers","cand-7489","The three del Rosso brothers; the sentence infers extensive travel from collection records.",1),
    (M,88,"their collection","cand-7489","Collection associated with the del Rosso family.",1),
    (M,88,"Mainz","cand-7490","Place from which two modern glass pictures are said to have come.",1),
    (M,88,"two modern ones on glass","cand-7493","Unidentified pair of glass pictures recorded in the collection.",1),
    (M,88,"Albert Diirer","cand-0954","S0 OCR form; print reads Albrecht Dürer. Mention is linked to the indexed artist, with identity review at S3.",1),
    (M,88,"Cologne","cand-6300","City where the Dürer pictures are said to have been bought.",1),
    (M,88,"two ‘by Albert Diirer bought by me in Cologne’","cand-7494","Quotation attributed to Andrea's inventory; two works, individual identities unspecified.",1),
    (M,88,"Gaspar Roomer","cand-2223","Named as a comparison for the brothers' connected trade and patronage.",1),
    (M,88,"Carlo Dolci","cand-0924","Indexed artist with a p.211 entry.",1),
    (M,88,"Flight into Egypt","cand-7495","Carlo Dolci picture reportedly sent to Lord Exeter.",1),
    (M,88,"Lord Exeter","cand-0984","Indexed 5th Lord Exeter; p.211 page range matches.",1),
    (M,88,"England","cand-7200","Destination context for Lord Exeter; use the existing geographic-place candidate.",1),
    (M,88,"another picture","cand-7496","Second, distinct picture sent as far as Poland; title and maker absent.",1),
    (M,88,"Poland","cand-7492","Destination of the unidentified second picture.",1),
    (M,89,"their immediate forebears","cand-7489","The family forebears whose patronage Haskell introduces for comparison.",1),
    (M,89,"their grandfather","cand-2279","Index candidate specifies Andrea del Rosso, grandfather of the three brothers; the sentence continues on p.212.",1),
    (M,90,"Andrea","cand-2275","One of the brothers whose career is summarized by Manini and Salvini.",1),
    (M,90,"Ottavio","cand-2286","One of the brothers whose career is summarized by Manini and Salvini.",1),
    (M,90,"Giuseppe Manini","cand-7505","Author of one brief career account, as cited by Haskell.",1),
    (M,90,"Salvino","cand-7506","First half of the surname split at the OCR line break; the next line completes Salvini.",1),
    (M,91,"Salvini","cand-7506","Completes the split name Salvino Salvini across the source line break.",1),
    (M,92,"wills of Lorenzo and Ottavio","cand-7507","Plural documentary reference; separate candidate rows represent the two individually named wills.",1),
    (M,92,"Archivio di Stato","cand-7509","Repository named for the notarial protocols; branch unspecified in this sentence.",1),
    (M,92,"Nicola Taddei","cand-7510","Notary named in the protocol containing Lorenzo's will.",1),
    (M,93,"Niccolo Salvetti","cand-7511","Notary named in the protocol containing Ottavio's will; S0 omits the accent.",1),
    (M,93,"Lorenzo","cand-2282","Testator who made the bequest.",1),
    (M,93,"Priore Coriolano Montemagni","cand-7512","Named bequest recipient; office and title are kept with the person candidate.",1),
    (M,94,"Caravaggio","cand-7513","Artist named in the reported will; identity alignment remains for S3.",1),
    (M,94,"S. Gio. Decollato","cand-7514","Subject description of the bequeathed painting; no specific surviving work is identified.",1),
    (M,95,"Andrea","cand-2275","The brother whose artistic activities in Rome are cited.",1),
    (M,95,"Rome","cand-4490","Location of Andrea's reported artistic activities.",1),
    (M,95,"Giuseppe Ghezzi","cand-1157","Artist and note-writer named as a source for Andrea's activities.",1),
    (M,95,"Sebastiano Resta","cand-2134","Author of two cited letters to Francesco Gabburri.",1),
    (M,95,"Francesco Gabburri","cand-1097","Recipient of the two letters cited by Haskell.",1),
    (M,95,"two letters from Sebastiano Resta to Francesco Gabburri","cand-7515","Document set cited through Bottari, volume II, pp.100 and 104.",1),
    (M,95,"Bottari","cand-7516","Cited publication, volume II; title and edition unspecified here.",1),
    (M,96,"Ottavio","cand-2286","Death reported in 1714.",1),
    (M,96,"Andrea","cand-2275","Death reported in 1715.",1),
    (M,96,"Lorenzo","cand-2282","Death reported in 1719.",1),
    (M,96,"Antonio","cand-2280","One of Nicola's two sons and an heir named in the p.211 index.",1),
    (M,96,"Giovanni Battista","cand-2281","One of Nicola's two sons and an heir named in the p.211 index.",1),
    (M,96,"fourth brother Nicola","cand-2285","Nicola del Rosso, father of Antonio and Giovanni Battista; index candidate covers p.211.",1),
    (N,1,"del Rosso brothers","cand-7489","Family whose collection is discussed in the cited sources.",1),
    (N,1,"Cinelli","cand-0765","Author of a 1677 account; the index entry covers p.211n.",1),
    (N,1,"Andrea del Rosso","cand-2275","Compiler of the complete inventory dated twelve years after the 1677 account.",1),
    (N,1,"Gualandi, II","cand-7501","Cited publication location for the inventory, pp.113-128.",1),
    (N,1,"Dottoressa Paola Zambelli","cand-2833","Person whom Haskell acknowledges for archival assistance.",1),
    (N,1,"Archivio di Stato","cand-7509","Florentine state archive named in the acknowledgement.",1),
    (N,2,"Passerini","cand-7502","Manuscript collection attribution in the footnote.",1),
    (N,2,"Biblioteca Nazionale","cand-7503","Library named as the holding institution; branch not specified.",1),
    (N,2,"Passerini 19(25)","cand-7502","Specific manuscript shelfmark cited by Haskell.",1),
    (N,2,"Informazione sopra la Nobiltà della Famiglia del Rosso di Firenze","cand-7502","Manuscript title as visually transcribed from the printed page.",1),
    (N,2,"Gio:Batta Dei","cand-7518","Name attributed in the manuscript title; full identity unresolved.",1),
    (N,2,"Falconieri","cand-7519","Plural addressees named in the genealogy manuscript title.",1),
    (N,2,"Poligrafo Gargano","cand-7504","Manuscript collection cited in the same library.",1),
    (N,3,"Appalto Generale della rendita della Farine della Città, e Dominio di Firenze","cand-7517","Named Florentine flour concession decree cited in note 2.",1),
    (N,3,"Archivio di Stato","cand-7509","Repository named for the 1676 decree.",1),
    (N,3,"Miscellanea Medicea 533, Uffizio delle Farine","cand-7517","Archival locator for the decree; not an independent source consulted here.",1),
    (N,4,"Baldinucci","cand-4846","Volume VI, 1728, page 500; reuse existing cited-publication candidate.",1),
    (N,4,"This picture","cand-7495","Footnote marker 3 follows the reference to Carlo Dolci's Flight into Egypt; the note's referent is that picture.",1),
    (N,4,"Burghley","cand-7237","Place where the cited note says the picture was still located.",1),
    (N,4,"London","cand-1422","City of the reported 1960 exhibition.",1),
    (N,4,"Italian Art and Britain","cand-7256","Exhibition catalogue/source cited at page 24; page itself not independently consulted.",1),
]


new_mentions = []
source_cache = {BODY_ID: (body_meta, body_all_lines, body_lines, body_text), NOTES_ID: (notes_meta, notes_all_lines, notes_lines, notes_text)}
for segment_id, line_number, surface, cid, note, occurrence in mention_specs:
    if cid not in candidate_ids | new_candidate_ids:
        raise SystemExit(f"mention references missing candidate: {cid}")
    meta, all_lines, sliced_lines, segment_text = source_cache[segment_id]
    source_line = all_lines[line_number - 1]
    if surface and surface[0].isalnum() and surface[-1].isalnum():
        starts = [match.start() for match in re.finditer(rf"(?<!\w){re.escape(surface)}(?!\w)", source_line)]
        # Printed footnote markers can be attached directly after a word in OCR.
        if not starts:
            starts = [match.start() for match in re.finditer(re.escape(surface), source_line)]
    else:
        starts = []
        cursor = 0
        while True:
            found = source_line.find(surface, cursor)
            if found < 0:
                break
            starts.append(found)
            cursor = found + 1
    if occurrence > len(starts):
        raise SystemExit(f"line {line_number}: occurrence missing for {surface!r}; found {len(starts)}")
    offset = sum(len(line) + 1 for line in sliced_lines[:line_number - int(meta["line_start"])])
    start = offset + starts[occurrence - 1]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch: {segment_id} {line_number} {surface!r}")
    new_mentions.append({
        "mention_id": f"m-chp8-p211-{len(new_mentions)+1:03d}", "segment_id": segment_id,
        "candidate_id": cid, "surface_form": surface, "start_char": str(start),
        "end_char": str(end), "note": note,
    })

new_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["candidate_id"]))
for row in new_mentions:
    if row["mention_id"] in existing_mention_ids:
        raise SystemExit(f"mention ID collision: {row['mention_id']}")
for i, first in enumerate(new_mentions):
    a, b = int(first["start_char"]), int(first["end_char"])
    for second in new_mentions[i+1:]:
        if first["segment_id"] != second["segment_id"]:
            continue
        c, d = int(second["start_char"]), int(second["end_char"])
        if c >= b:
            break
        if (a, b) == (c, d):
            raise SystemExit(f"duplicate exact-span mentions: {first!r} / {second!r}")
        if not ((a <= c and d <= b) or (c <= a and b <= d)):
            raise SystemExit(f"overlapping non-nested mentions: {first!r} / {second!r}")


def make_statement(sid, segment_id, source_rel, start, end, printed_page, physical_page,
                   predicate, claim, qualification, quote, *, subject=None, obj=None,
                   mentioned=(), text_layer="body", speaker="Haskell", extra=None):
    q = {
        "source_line_start": start, "source_line_end": end,
        "printed_page": printed_page, "pdf_physical_page": physical_page,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extra:
        q.update(extra)
    return {
        "statement_id": sid, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": q,
        "original_quote": quote, "origin": "book", "source_file": source_rel,
    }


statements = [
    make_statement("st-chp8-p211-three-del-rosso-brothers-notable-collectors", M, BODY_REL, 85, 85, 211, 9,
                  "three_del_rosso_brothers_named_as_notable_collectors",
                  "Haskell identifies Andrea, Lorenzo and Ottavio del Rosso and says they were among the notable collectors of their day.",
                  "The surname at the start of p.211 completes the p.210 open sentence. The brothers remain distinct from their grandfather Andrea del Rosso.",
                  "del Rosso, who were among the most notable collectors of their day", subject="cand-7489", obj="cand-2275",
                  mentioned=["cand-7489","cand-2275","cand-2282","cand-2286"],
                  extra={"continuation_of_statement_id": PREVIOUS_OPEN, "continuation_status": "closed", "continuation_source_segment_id": PREVIOUS_ID, "continuation_source_line": 82,"footnote_marker":1,"ocr_corrections":[{"source_line":85,"ocr":"dayd","print":"day.¹","basis":"CHP-8.pdf physical page 9; OCR merged the superscript footnote marker."}]}),
    make_statement("st-chp8-p211-del-rosso-family-social-advancement", M, BODY_REL, 85, 85, 211, 9,
                  "family_social_advancement_through_merchant_wealth_and_marriage_alliances",
                  "Haskell describes the del Rosso family as wealthy merchants who had gradually gained Florentine citizenship, admission to the Cavalieri di Santo Stefano, marriage alliances, dignities and official posts.",
                  "This is the author's account of a multigenerational family trajectory; the passage does not name the marriage partners or date each step.",
                  "a family of rich merchants which throughout the previous century had been laboriously engaged in worming its way up to the centres of power and prestige. Money had opened all the doors: first, Florentine citizenship and admission to the recently founded chivalrous order of the Cavalieri di Santo Stefano; then a series of ingenious marriage alliances with the best families; and, finally, as a logical development, an increasing number of dignities and official posts", subject="cand-7489",
                  mentioned=["cand-7489","cand-1041","cand-0612"], extra={"relation_candidate": True}),
    make_statement("st-chp8-p211-andrea-born-and-flour-monopoly", M, BODY_REL, 85, 85, 211, 9,
                  "andrea_born_1640_awarded_shared_florentine_flour_monopoly_at_age_36",
                  "Haskell says the eldest brother Andrea was born in 1640 and, at age 36, received the lucrative flour monopoly shared with Lorenzo.",
                  "The award year follows from the stated age and birth year, while footnote 2 separately cites a decree beginning 1 June 1676; preserve the distinction between the body report and the cited document.",
                  "Andrea, the eldest of the brothers, who was born in 1640, was at the age of 36 awarded the lucrative flour monopoly which he shared with the slightly younger Lorenzo", subject="cand-2275", obj="cand-7498",
                  mentioned=["cand-2275","cand-2282","cand-7498"], extra={"reported_birth_year":1640,"reported_age_at_award":36,"relation_candidate":True}),
    make_statement("st-chp8-p211-andrea-lorenzo-senators-and-andrea-postal-director", M, BODY_REL, 85, 86, 211, 9,
                  "brothers_later_senators_and_andrea_director_of_papal_postal_services",
                  "Haskell says both Andrea and Lorenzo later became senators and Andrea died in Rome while serving as director-general of the papal postal services.",
                  "The text does not give the dates of the senatorial appointments or of Andrea's postal-service tenure.",
                  "Both men later became Senators, and Andrea eventually died in Rome, where he frequently lent pictures to the exhibitions at S.\nSalvatore in Lauro, as director-general of the papal postal services", subject="cand-2275",
                  mentioned=["cand-2275","cand-2282","cand-4490","cand-6051","cand-6052","cand-7497"], extra={"relation_candidate":True}),
    make_statement("st-chp8-p211-andrea-lent-pictures-to-salvatore-exhibitions", M, BODY_REL, 85, 86, 211, 9,
                  "andrea_frequently_lent_pictures_to_exhibitions_at_s_salvatore_in_lauro",
                  "Haskell says Andrea frequently lent pictures to art exhibitions at S. Salvatore in Lauro in Rome.",
                  "The source describes lending to exhibitions and does not identify the pictures individually.",
                  "frequently lent pictures to the exhibitions at S.\nSalvatore in Lauro", subject="cand-2275", obj="cand-0134",
                  mentioned=["cand-2275","cand-4490","cand-0134","cand-6052"], extra={"relation_candidate":True}),
    make_statement("st-chp8-p211-ottavio-bishop-volterra", M, BODY_REL, 86, 87, 211, 9,
                  "ottavio_entered_church_became_bishop_of_volterra",
                  "Haskell says Ottavio entered the Church and became Bishop of Volterra, where he lived in a phrase of extraordinary goodness.",
                  "The OCR has 'Bjshop' and corrupted accented Italian; p.211 scan confirms 'Bishop' and the quoted Italian phrase. The quotation remains Haskell's characterization.",
                  "Church and became Bjshop of Volterra", subject="cand-2286", obj="cand-7491",
                  mentioned=["cand-2286","cand-7491"], extra={"ocr_corrections":[{"source_line":87,"ocr":"Bjshop","print":"Bishop","basis":"CHP-8.pdf physical page 9."},{"source_line":87,"ocr":"concetto di straordinaria bontà","print":"concetto di straordinaria bontà","basis":"CHP-8.pdf physical page 9; OCR encoding corruption only."}]}),
    make_statement("st-chp8-p211-collection-records-indicate-brothers-travelled", M, BODY_REL, 88, 88, 211, 9,
                  "collection_records_used_to_infer_brothers_travelled_extensively",
                  "Haskell infers that the brothers travelled a great deal from records of pictures from Mainz and pictures bought in Cologne.",
                  "This is Haskell's inference from collection evidence, not a dated itinerary for each brother.",
                  "In their earlier days the brothers clearly travelled a great deal, for among the pictures recorded in their collection are", subject="cand-7489",
                  mentioned=["cand-7489","cand-7490","cand-7493","cand-7494","cand-0954","cand-6300"]),
    make_statement("st-chp8-p211-del-rosso-inventory-reports-glass-and-durer-pairs", M, BODY_REL, 88, 88, 211, 9,
                  "collection_inventory_records_two_glass_pictures_and_two_durer_pictures",
                  "Haskell quotes the collection record as listing two modern pictures on glass from Mainz and two pictures by Albrecht Dürer bought in Cologne.",
                  "The first-person 'bought by me' is an inventory quotation attributed to Andrea del Rosso; individual pictures are unidentified. S0's 'Diirer' is checked against the printed 'Dürer'.",
                  "‘two modern ones on glass’ from Mainz and two ‘by Albert Diirer bought by me in Cologne’", subject="cand-7489",
                  mentioned=["cand-7489","cand-7490","cand-7493","cand-7494","cand-0954","cand-6300"],
                  speaker="Andrea del Rosso, as quoted from his inventory by Haskell", extra={"quantity":2,"ocr_corrections":[{"source_line":88,"ocr":"Albert Diirer","print":"Albrecht Dürer","basis":"CHP-8.pdf physical page 9."}]}),
    make_statement("st-chp8-p211-del-rosso-trade-patronage-connected", M, BODY_REL, 88, 88, 211, 9,
                  "trading_and_patronage_described_as_closely_connected",
                  "Haskell says the brothers' trading and patronage were closely connected, comparing them with Gaspar Roomer.",
                  "This is an authorial characterization; no specific commercial transaction beyond the following picture transfers is inferred.",
                  "Inevitably, like Gaspar Roomer and so many other businessmen, their trading and patronage were closely connected", subject="cand-7489",
                  mentioned=["cand-7489","cand-2223"]),
    make_statement("st-chp8-p211-dolci-flight-sent-to-lord-exeter", M, BODY_REL, 88, 88, 211, 9,
                  "brothers_sent_carlo_dolci_flight_into_egypt_to_lord_exeter_in_england",
                  "Haskell reports that the brothers sent Carlo Dolci's small Flight into Egypt to Lord Exeter in England.",
                  "Footnote 3 links the picture to Baldinucci and an exhibition catalogue; the cited pages were not independently consulted, so the surviving object's identity remains open.",
                  "sending Carlo Dolci’s little Flight into Egypt to Lord Exeter in England", subject="cand-7489", obj="cand-7495",
                  mentioned=["cand-7489","cand-0924","cand-7495","cand-0984","cand-7200"], extra={"relation_candidate":True,"footnote_marker":3}),
    make_statement("st-chp8-p211-second-picture-sent-to-poland", M, BODY_REL, 88, 88, 211, 9,
                  "brothers_sent_another_unidentified_picture_as_far_as_poland",
                  "Haskell says the brothers sent another, unidentified picture as far as Poland.",
                  "This is a distinct picture from the Carlo Dolci work sent to Lord Exeter; no maker, title, recipient or date is supplied.",
                  "and another picture as far as Poland", subject="cand-7489", obj="cand-7496",
                  mentioned=["cand-7489","cand-7496","cand-7492"], extra={"relation_candidate":True}),
    make_statement("st-chp8-p211-forebears-grandfather-open", M, BODY_REL, 89, 89, 211, 9,
                  "comparison_with_forebears_begins_grandfather_account_continues",
                  "Haskell introduces a comparison between the brothers' patronage and that of their immediate forebears, beginning a statement about their grandfather in 1642.",
                  "The sentence ends mid-clause at 'their grandfather' and continues on p.212. No action or relationship beyond the indexed grandfather identification is inferred yet.",
                  "In 1642, two years before his death, their grandfather", subject="cand-7489", obj="cand-2279",
                  mentioned=["cand-7489","cand-2279"], extra={"continuation_status":"open","continuation_expected_segment_id":NEXT_ID,"continuation_note":"p.212 starts 'Andrea had had built…' and continues this sentence."}),
    make_statement("st-chp8-p211-principal-sources-for-del-rosso-collection", N, NOTES_REL, 1, 1, 211, 9,
                  "haskell_names_cinelli_1677_account_and_andrea_1689_inventory_as_main_collection_sources",
                  "Haskell identifies Cinelli's 1677 account and Andrea del Rosso's complete inventory, drawn up twelve years later and published in Gualandi volume II, as the principal sources for the brothers' collection.",
                  "The cited account, inventory and publication are bibliographic or archival locators; Haskell says both documents provide incidental biographical information, but they are not independently consulted here.",
                  "The main sources for the collection of the del Rosso brothers are the account given of it in 1677 by Cinelli and the complete inventory drawn up twelve years later by Andrea del Rosso himself published in Gualandi, II, pp. 113-28", subject="cand-7489",
                  mentioned=["cand-7489","cand-0765","cand-2275","cand-7499","cand-7500","cand-7501"], text_layer="footnote", extra={"footnote_number":1,"citation_only":True}),
    make_statement("st-chp8-p211-haskell-acknowledges-paola-zambelli", N, NOTES_REL, 1, 1, 211, 9,
                  "haskell_acknowledges_paola_zambelli_archival_assistance",
                  "Haskell thanks Dottoressa Paola Zambelli of the Archivio di Stato for her help.",
                  "This records the author's acknowledgement, not a claim about the contents of the cited records.",
                  "I am most grateful to Dottoressa Paola Zambelli of the Archivio di Stato for her help", subject="cand-2275",
                  mentioned=["cand-2833","cand-7509"], text_layer="footnote", extra={"footnote_number":1}),
    make_statement("st-chp8-p211-cinelli-inventory-incidental-biographical-information", N, NOTES_REL, 1, 1, 211, 9,
                  "cinelli_account_and_del_rosso_inventory_said_to_provide_incidental_biographical_information",
                  "Haskell says both the 1677 account and the later inventory provide some incidental biographical information.",
                  "This describes Haskell's assessment of the cited sources; neither source was independently consulted here.",
                  "Both these documents provide a certain amount of incidental biographical information", subject="cand-7499", obj="cand-7500",
                  mentioned=["cand-7499","cand-7500"], text_layer="footnote", extra={"footnote_number":1,"citation_only":True}),
    make_statement("st-chp8-p211-haskell-used-florentine-archive-and-manuscript-sources", N, NOTES_REL, 1, 1, 211, 9,
                  "haskell_says_he_drew_on_published_and_manuscript_sources_in_florentine_collections",
                  "Haskell says he supplemented the collection account and inventory with published and manuscript sources in Florentine archives and libraries.",
                  "This records the author's description of his research sources and does not imply those sources have been independently consulted in this project.",
                  "To supplement these I have drawn heavily on a number of published and manuscript sources in Florentine archives and libraries", text_layer="footnote", extra={"footnote_number":1,"citation_only":True}),
    make_statement("st-chp8-p211-passerini-and-poligrafo-gargano-genealogical-sources", N, NOTES_REL, 2, 2, 211, 9,
                  "family_genealogies_and_other_references_located_in_named_manuscript_collections",
                  "Haskell locates family genealogies in Passerini's manuscripts at the Biblioteca Nazionale, especially manuscript 19(25), and says other references occur in the Poligrafo Gargano in the same library.",
                  "The named manuscript and collection are citations in Haskell's footnote, not independently examined; the exact library branch is left unresolved.",
                  "General information about the family and genealogies exist in the manuscript collections of Passerini in the Biblioteca Nazionale—in particular, Passerini 19(25): Informazione sopra la Nobiltà della Famiglia del Rosso di Firenze mandata a i SSri Falconieri di Roma, da me Gio:Batta Dei, quest'anno 1747. There are also a number of references drawn from a variety of sources in the Poligrafo Gargano in the same library", subject="cand-7489",
                  mentioned=["cand-7489","cand-7502","cand-7503","cand-7504","cand-7518","cand-7519"], text_layer="footnote", extra={"footnote_number":1,"citation_only":True}),
    make_statement("st-chp8-p211-manini-salvini-career-accounts", M, BODY_REL, 90, 91, 211, 9,
                  "brief_career_accounts_for_andrea_and_ottavio_attributed_to_manini_and_salvini",
                  "Haskell says Giuseppe Manini and Salvino Salvini give brief accounts of Andrea's and Ottavio's careers.",
                  "The note does not identify the titles, dates or exact contents of those accounts.",
                  "Very brief accounts of the careers of Andrea and Ottavio are given by Giuseppe Manini and Salvino Salvini", subject="cand-7505",
                  mentioned=["cand-2275","cand-2286","cand-7505","cand-7506"], text_layer="footnote", extra={"footnote_number":1,"citation_only":True}),
    make_statement("st-chp8-p211-wills-and-caravaggio-bequest", M, BODY_REL, 92, 94, 211, 9,
                  "wills_cited_and_lorenzo_bequest_of_caravaggio_picture_to_montemagni",
                  "Haskell locates Lorenzo's and Ottavio's wills in Archivio di Stato notarial protocols and says they contain no picture references except Lorenzo's bequest of a Caravaggio picture of S. Gio. Decollato to Priore Coriolano Montemagni.",
                  "This is Haskell's report and transcription of the will; neither will nor the painting is independently examined. The quoted dimensions are retained as written, without unit conversion or identification with a surviving work.",
                  "The wills of Lorenzo and Ottavio are in the Archivio di Stato—Protocolli del notaio Nicola Taddei, 24,253, Testamenti and Protocolli del notaio Niccolo Salvetti, Testamenti, 23,516—but they are of no great interest and do not refer to pictures except for a bequest by Lorenzo", subject="cand-2282", obj="cand-7514",
                  mentioned=["cand-2282","cand-2286","cand-7507","cand-7508","cand-7509","cand-7510","cand-7511","cand-7512","cand-7513","cand-7514"], text_layer="footnote", extra={"footnote_number":1,"relation_candidate":True}),
    make_statement("st-chp8-p211-caravaggio-bequest-description-and-dimensions", M, BODY_REL, 94, 94, 211, 9,
                  "bequeathed_caravaggio_picture_described_as_saint_john_beheaded_with_dimensions",
                  "The reported bequest describes a Caravaggio picture of S. Gio. Decollato, approximately two braccia wide and one and two-thirds braccia high.",
                  "The Italian wording comes from Haskell's quotation of Lorenzo's will; retain the historic unit and leave the work's identity unresolved.",
                  "un Quadro di mano del Caravaggio di Larghezza braccia due con l’ornamento, et Altezza braccia uno, e due terzi incirca dipintovi fra l’altro S. Gio. Decollato", subject="cand-7514",
                  mentioned=["cand-7512","cand-7513","cand-7514"], text_layer="footnote", speaker="Lorenzo del Rosso's will, as quoted by Haskell", extra={"footnote_number":1,"reported_dimensions":"about 2 braccia wide by 1 2/3 braccia high"}),
    make_statement("st-chp8-p211-andrea-artistic-activity-sources", M, BODY_REL, 95, 95, 211, 9,
                  "andrea_roman_artistic_activities_referred_to_in_ghezzi_notes_and_resta_letters",
                  "Haskell says Andrea's artistic activities in Rome are mentioned in Giuseppe Ghezzi's notes and in two letters from Sebastiano Resta to Francesco Gabburri published by Bottari, volume II, pages 100 and 104.",
                  "The note identifies source locations; the notes, letters and cited pages are not independently consulted here.",
                  "two letters from Sebastiano Resta to Francesco Gabburri published by Bottari, II, pp. 100 and 104", subject="cand-2275",
                  mentioned=["cand-2275","cand-4490","cand-1157","cand-2134","cand-1097","cand-7515","cand-7516"], text_layer="footnote", extra={"footnote_number":1,"citation_only":True}),
    make_statement("st-chp8-p211-brothers-deaths-and-nicola-heirs", M, BODY_REL, 96, 96, 211, 9,
                  "ottavio_andrea_lorenzo_death_years_and_nicola_sons_as_heirs",
                  "Haskell reports that Ottavio died in 1714, Andrea in 1715 and Lorenzo in 1719; the heirs were Antonio and Giovanni Battista, sons of their fourth brother Nicola, who died in 1710.",
                  "The death years and kinship are reported by Haskell; this statement does not infer additional family relationships beyond the wording.",
                  "Ottavio died in 1714, Andrea in 1715 and Lorenzo in 1719. The heirs were the two sons, Antonio and Giovanni Battista, of a fourth brother Nicola who died in 1710", subject="cand-7489",
                  mentioned=["cand-7489","cand-2286","cand-2275","cand-2282","cand-2280","cand-2281","cand-2285"], text_layer="footnote", extra={"footnote_number":1,"relation_candidate":True}),
    make_statement("st-chp8-p211-flour-decree-citation", N, NOTES_REL, 3, 4, 211, 9,
                  "nine_year_florentine_flour_concession_decree_effective_from_1_june_1676_cited",
                  "Footnote 2 cites a decree granting the Appalto Generale of flour revenues in Florence for nine years from 1 June 1676, held in Archivio di Stato, Miscellanea Medicea 533, Uffizio delle Farine.",
                  "Haskell cites the archival decree and says related operating information is elsewhere in the collection; the decree and related records are not independently consulted here.",
                  "A copy of the decree conferring the Appalto Generale della rendita della Farine della Città, e Dominio di Firenze for nine years as from 1 June 1676 is preserved in the Archivio di Stato—Miscellanea Medicea 533, Uffizio delle Farine", subject="cand-7517",
                  mentioned=["cand-7517","cand-1041","cand-7509"], text_layer="footnote", extra={"footnote_number":2,"citation_only":True}),
    make_statement("st-chp8-p211-flour-decree-further-operating-information-cited", N, NOTES_REL, 3, 4, 211, 9,
                  "haskell_points_to_other_documents_for_information_on_flour_concession_operation",
                  "Haskell says information about the flour concession's operation can be found elsewhere in the same archival collection.",
                  "The additional records are not identified or consulted in the footnote.",
                  "some information about its functioning can be found elsewhere in the same collection of documents", subject="cand-7517",
                  mentioned=["cand-7517","cand-7509"], text_layer="footnote", extra={"footnote_number":2,"citation_only":True}),
    make_statement("st-chp8-p211-dolci-picture-burghley-exhibition-reference", N, NOTES_REL, 4, 4, 211, 9,
                  "baldinucci_and_1960_exhibition_catalogue_cited_for_dolci_picture_at_burghley",
                  "Footnote 3 cites Baldinucci, volume VI (1728), page 500, and Italian Art and Britain, page 24, saying the picture was still at Burghley and had been exhibited in London in 1960.",
                  "This is Haskell's footnote report and bibliographic locator; neither cited page is independently consulted. The printed footnote number is 3, although the whole-chapter OCR reads 8.",
                  "Baldinucci, VI, 1728, p. 500. This picture, which is still at Burghley, was exhibited in London in 1960—Italian Art and Britain, p. 24", subject="cand-7495",
                  mentioned=["cand-7495","cand-4846","cand-7237","cand-1422","cand-7256"], text_layer="footnote", extra={"footnote_number":3,"citation_only":True,"ocr_corrections":[{"source_file":"02-sources/02-Markdown/08_CHP-8.md","source_line":180,"ocr":"8 Baldinucci","print":"3 Baldinucci","basis":"CHP-8.pdf physical page 9."},{"source_file":NOTES_REL,"source_line":4,"ocr":"i960","print":"1960","basis":"CHP-8.pdf physical page 9."}]}),
]


if len({row["statement_id"] for row in statements}) != len(statements) or {row["statement_id"] for row in statements} & existing_statement_ids:
    raise SystemExit("planned statement ID collision")
closed_previous = False
updated_statements = []
for row in statement_rows:
    row = dict(row)
    if row["statement_id"] == PREVIOUS_OPEN:
        q = dict(row["qualifiers"])
        if q.get("continuation_status") != "open" or q.get("continuation_expected_segment_id") != BODY_ID:
            raise SystemExit("p.210 continuation changed; inspect before closing")
        q.update({"continuation_status":"closed","continuation_source_segment_id":BODY_ID,"continuation_source_line":85,
                  "continuation_statement_id":"st-chp8-p211-three-del-rosso-brothers-notable-collectors",
                  "continuation_resolution":"p.211 L85 supplies 'del Rosso' and completes the three brothers' surname."})
        q.pop("continuation_expected_segment_id",None); q.pop("continuation_note",None)
        row["qualifiers"] = q
        closed_previous = True
    updated_statements.append(row)
if not closed_previous:
    raise SystemExit("expected p.210 open statement not found")

all_candidates = candidate_ids | new_candidate_ids
coverage_updates = {
    PREVIOUS_ID: {"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L73-82",
                  "note":"P.210 body and cross-page sentence are complete. The open surname is supplied by p.211 L85; no printed footnote occurs on p.210."},
    BODY_ID: {"disposition":"reviewed","migration_status":"partial","source_line_ranges":"L85-96",
              "note":"P.211 body, footnote 1 continuation and note references read against CHP-8.pdf physical p.9. The first sentence closes p.210; the final grandfather sentence continues to p.212 L99. Unique footnote 1 opening and notes 2-3 are captured in the supplemental visual-transcription segment; repeated note text is counted once."},
    NOTES_ID: {"disposition":"reviewed","migration_status":"complete","source_line_ranges":"L1-4",
               "note":"Physical p.211 footnote 1 opening and notes 2-3 transcribed from CHP-8.pdf; p.211 footnote 3 is verified as 3 (whole-chapter OCR reads 8). No duplicate of the note 1 tail already present in section OCR L90-96."},
}
updated_coverage = []
for row in coverage_rows:
    row = dict(row)
    if row["segment_id"] in coverage_updates:
        row.update(coverage_updates[row["segment_id"]])
    updated_coverage.append(row)

for row in statements:
    seg = row["segment_id"]
    meta, all_lines, sliced_lines, segment_text = source_cache[seg]
    q = row["qualifiers"]
    start, end = q["source_line_start"], q["source_line_end"]
    cov = coverage_updates[seg]
    ranges = [(int(a),int(b)) for a,b in re.findall(r"L(\d+)-(\d+)",cov["source_line_ranges"])]
    if not any(a <= start and end <= b for a,b in ranges):
        raise SystemExit(f"statement outside coverage: {row['statement_id']}")
    cited = "\n".join(all_lines[start-1:end])
    if " ".join(row["original_quote"].split()) not in " ".join(cited.split()):
        raise SystemExit(f"quote not reproducible: {row['statement_id']}")
    referenced = set(q.get("mentioned_candidate_ids",[]))
    if row.get("subject_candidate_id"): referenced.add(row["subject_candidate_id"])
    if row.get("object_candidate_id"): referenced.add(row["object_candidate_id"])
    if not referenced <= all_candidates:
        raise SystemExit(f"missing candidate FK: {row['statement_id']}")

preview = {
    "mode":"dry-run", "segments":[BODY_ID,NOTES_ID], "new_candidates":len(new_candidates),
    "candidate_ids":[row["candidate_id"] for row in new_candidates], "new_mentions":len(new_mentions),
    "new_statements":len(statements), "closed_previous_statement":PREVIOUS_OPEN,
    "open_continuation":{"statement_id":"st-chp8-p211-forebears-grandfather-open","next_segment_id":NEXT_ID},
    "coverage":coverage_updates,
}
parser=argparse.ArgumentParser()
parser.add_argument("--apply",action="store_true",help="write validated tables and create recovery backups")
if not parser.parse_args().apply:
    print(json.dumps(preview,ensure_ascii=False,indent=2)); raise SystemExit(0)

for path in (candidate_path,mention_path,statement_path,coverage_path):
    backup=path.with_name(path.name+BACKUP_SUFFIX)
    if backup.exists(): raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path,backup)
candidate_rows.extend(new_candidates)
mention_rows.extend(new_mentions)
updated_statements.extend(statements)
write_csv_atomic(candidate_path,candidate_fields,candidate_rows)
write_csv_atomic(mention_path,mention_fields,mention_rows)
write_jsonl_atomic(statement_path,updated_statements)
write_csv_atomic(coverage_path,coverage_fields,updated_coverage)
preview["mode"]="applied"
print(json.dumps(preview,ensure_ascii=False,indent=2))
