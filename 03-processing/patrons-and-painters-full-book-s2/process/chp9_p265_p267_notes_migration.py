"""Controlled S2 migration for the consolidated p.265-267 notes; dry-run by default."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l323-445"
BODY_P265 = "chp-9:09_CHP-9_intro:l291-301"
BODY_P266 = "chp-9:09_CHP-9_intro:l303-311"
BODY_P267 = "chp-9:09_CHP-9_intro:l313-321"
EXPECTED_SEGMENT_SHA = "51cc706d49319744d5efe4ed0c2528e68a2a3e1d82d75b14961092f0c36eebfc"
EXPECTED_ASSET_SHA = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
EXPECTED_MAX_CANDIDATE = 8637
BACKUP_SUFFIX = ".bak-s2-chp9-notes-p265-p267-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(handle.name)
    temporary.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if hashlib.sha256(source_bytes).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("chapter 9 source asset has changed")
segments = {row["segment_id"]: row for row in read_jsonl(segment_path)}
segment_meta = segments.get(SEGMENT_ID)
if not segment_meta or segment_meta.get("sha256") != EXPECTED_SEGMENT_SHA:
    raise SystemExit("consolidated note source segment is missing or changed")
if segment_meta.get("asset_sha256") != EXPECTED_ASSET_SHA:
    raise SystemExit("consolidated note source asset fingerprint mismatch")
segment_text = "\n".join(source_lines[322:445])
if not all(source_lines[line - 1].startswith(marker) for line, marker in [(429, "1 Haskell"), (430, "3 See print 428"), (432, "6 The pictures"), (445, "5 Blunt")]):
    raise SystemExit("expected p.265-267 note lines have changed")

candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}
max_candidate = max(int(re.search(r"\d+", row["candidate_id"]).group()) for row in candidates)
if max_candidate != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {max_candidate}")
note_coverage = coverage_by_id.get(SEGMENT_ID)
if not note_coverage or (note_coverage["disposition"], note_coverage["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"unexpected consolidated-note coverage state: {note_coverage}")
for body_id in (BODY_P265, BODY_P266, BODY_P267):
    row = coverage_by_id.get(body_id)
    if not row or (row["disposition"], row["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit(f"expected completed body segment is missing: {body_id}")

# Keep citation objects distinct where the short form or work identity is unresolved.
CANDIDATE_SPECS = [
    ("haskell_levey_1958", "Haskell and Levey, 1958, p.182 (citation locator; title pending bibliography review)", "archive", "Haskell cites this short-form source for the p.265 account of Piazzetta's Angelo Custode. The cited publication and page have not been independently consulted; reconcile the title when S2 reaches the bibliography.", 429),
    ("correr_print_428", "Print 428 in volume 3 of Raccolta Gherro (Biblioteca Correr)", "archive", "Haskell identifies this print as the source of the dedication to Zaccaria Sagredo quoted at p.265. The print itself has not been independently examined.", 430),
    ("marchesini_letter_aug", "Letter from Alessandro Marchesini to Stefano Conti, 11 August 1725 (cited in Haskell, 1956, p.298)", "archive", "A specific letter locator in p.265 note 4; its contents and archival witness have not been independently checked.", 431),
    ("marchesini_letter_dec", "Letter from Alessandro Marchesini to Stefano Conti, 1 December 1725 (cited in Haskell, 1956, p.298)", "archive", "A specific letter locator in p.265 note 4; the scan reads the date as 1 December, while S0 OCR renders the numeral as capital I. Contents and archival witness have not been independently checked.", 431),
    ("haskell_1956_p298", "Haskell, 1956, p.298 (publication locator for the Marchesini letters; title pending)", "archive", "Short-form publication locator in p.265 note 4. Full identity is deferred to the book bibliography pass; the cited page has not been independently consulted.", 431),
    ("moschini_v_1956", "V. Moschini, 1956, p.12 (citation locator; title pending bibliography review)", "archive", "Short-form citation in p.265 note 5 supporting Haskell's tentative Longhi commission discussion; the cited work and argument have not been independently consulted.", 431),
    ("crespi_l_p215", "L. Crespi, p.215 (citation locator; publication identity unresolved)", "archive", "Short-form source locator for the identification of Crespi's two religious pictures in p.265 note 6. Keep distinct from other abbreviated L. Crespi citations until the bibliography is processed.", 432),
    ("nativity_work", "Unidentified Nativity among the two religious works by Giuseppe Maria Crespi for Zaccaria Sagredo", "work", "P.265 note 6 identifies one of the two works only by subject as a Nativity; title, date, and present location are not supplied.", 432),
    ("mission_work", "Unidentified Mission among the two religious works by Giuseppe Maria Crespi for Zaccaria Sagredo", "work", "P.265 note 6 identifies one of the two works only as a Mission; preserve the possible Chicago identification separately.", 432),
    ("jesuit_mission_chicago", "Pictures described as a Jesuit Mission and reported in Chicago (possible match unresolved)", "work", "Haskell says the Mission may be the pictures described as a Jesuit Mission now in Chicago. The phrasing is tentative and plural; do not equate this group with the unidentified Mission without later evidence.", 432),
    ("moschini_ga_1806_v1_p84", "G. A. Moschini, 1806, volume I, p.84 (citation locator; title pending bibliography review)", "archive", "Short-form citation in p.266 note 2 for the account of Sagredo's commissioned pen-and-ink views. The cited page has not been independently consulted.", 434),
    ("da_canal_p77", "Da Canal, p.77 (citation locator; work and edition pending bibliography review)", "archive", "Short-form citation in p.266 note 3, given alongside Fontana p.64 for the reported Lazzarini and Diziani drawings. The cited page has not been independently consulted.", 435),
    ("fontana_p64", "Fontana, p.64 (citation locator; author-work identity unresolved)", "archive", "Short-form citation in p.266 note 3. The surname and cited page are preserved without choosing among possible Fontana identities.", 435),
    ("smith_will_parker_1948", "Joseph Smith's will as published by Parker, 1948, p.60 (citation locator)", "archive", "Cited in p.266 note 4 and p.267 note 2. The will and Parker publication are known here only through Haskell's locator and have not been independently consulted.", 436),
    ("popham_wilde_1949", "Popham and Wilde, 1949, p.14 (citation locator; title pending bibliography review)", "archive", "Short-form source cited in p.266 note 5 for the Raphael sheets in Sagredo's purchase; the cited publication has not been independently consulted.", 437),
    ("zanetti_letter_1728", "Letter from A. M. Zanetti to Francesco Gabburri, 11 January 1728 (published in Bottari, volume II, p.186)", "archive", "Specific letter locator in p.266 note 6. The letter is cited as support for the accompanying quotation, not independently consulted.", 438),
    ("blunt_1954", "Anthony Blunt, 1954, pp.24 and 36 (citation locators; title pending bibliography review)", "archive", "The two page references in p.266 note 7 and p.267 note 5 are kept under one provisional short-form source candidate; cited pages have not been independently consulted.", 439),
    ("fochessati_p278", "Fochessati, p.278 (citation locator; title pending bibliography review)", "archive", "Short-form source cited in p.267 note 3 for the characterization of Ferdinando Carlo; the cited page has not been independently consulted.", 443),
    ("malamani_1899_p46", "Malamani, 1899, p.46 (citation locator; title pending bibliography review)", "archive", "Short-form source cited in p.267 note 4 for the Mantuan-market account; the cited page has not been independently consulted.", 444),
    ("person_levey", "Levey (identified by surname in the p.265 note 1 citation)", "person", "The p.265 note gives only the surname in 'Haskell and Levey, 1958'; full identity is deferred to the bibliography and S3.", 429),
    ("person_v_moschini", "V. Moschini (identified by initial and surname in p.265 note 5)", "person", "The source supplies only an initial and surname; do not merge with G. A. Moschini at S2.", 431),
    ("person_fontana", "Fontana (surname-only author cited in p.266 note 3)", "person", "The short citation does not identify which Fontana or the work; identity remains open for the bibliography and S3.", 435),
    ("person_parker", "Parker (author cited for publication of Smith's will, 1948)", "person", "The p.266-267 notes give only a surname; full identity is deferred to the bibliography and S3.", 436),
    ("person_popham", "Popham (author cited with Wilde in 1949)", "person", "The note gives only a surname; full identity is deferred to the bibliography and S3.", 437),
    ("person_wilde", "Wilde (author cited with Popham in 1949)", "person", "The note gives only a surname; full identity is deferred to the bibliography and S3.", 437),
    ("person_fochessati", "Fochessati (surname-only author cited at p.267 note 3)", "person", "The short-form citation gives no initial or title; identity is deferred to the bibliography and S3.", 443),
    ("person_malamani", "Malamani (surname-only author cited at p.267 note 4)", "person", "The short-form citation gives no initial or title; identity is deferred to the bibliography and S3.", 444),
]

candidate_by_key = {}
new_candidates = []
for offset, (key, name, kind, detail, line_no) in enumerate(CANDIDATE_SPECS, 1):
    candidate_id = f"cand-{EXPECTED_MAX_CANDIDATE + offset:04d}"
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"] == name and row["suggested_type"] == kind for row in candidates):
        raise SystemExit(f"candidate natural key already exists: {name}")
    candidate_by_key[key] = candidate_id
    new_candidates.append({
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L{line_no}",
    })

candidate_ids |= {row["candidate_id"] for row in new_candidates}
P265, P266, P267 = BODY_P265, BODY_P266, BODY_P267
EXISTING = {
    "zaccaria": "cand-2339", "gmcrespi": "cand-0871", "marchesini": "cand-1539",
    "conti": "cand-0833", "correr": "cand-8262", "moschini_ga": "cand-1709",
    "moschini_source": "cand-7781", "smith": "cand-2440", "zanetti": "cand-2838",
    "gabburri": "cand-1097", "bottari_p186": "cand-8584", "blunt": "cand-0379",
    "dacan": "cand-7781", "crespi_l": "cand-7716", "chicago": "cand-4624",
    "angelo": "cand-8569", "canaletto": "cand-0522", "longhi": "cand-1431",
    "longhi_fresco": "cand-8613", "crespi_group": "cand-8591", "torresani_views": "cand-8625",
    "lazzarini_drawings": "cand-8626", "diziani_volume": "cand-8627", "raphael_sheets": "cand-8633",
    "zanetti_engravings": "cand-8630", "tiepolo": "cand-2569", "castiglione": "cand-0602",
    "ferdinando": "cand-1524", "schulenburg": "cand-2401", "ducal_collection": "cand-8631",
    "sagredo_drawings": "cand-8636", "jesuit_church": "cand-6672",
}
for key, candidate_id in EXISTING.items():
    if candidate_id not in candidate_ids:
        raise SystemExit(f"required existing candidate is missing: {key}={candidate_id}")

line_offsets = {}
offset = 0
for line_no in range(323, 446):
    line_offsets[line_no] = offset
    offset += len(source_lines[line_no - 1]) + 1

new_mentions = []
def add_mention(mention_id, line_no, candidate_id, surface, note, occurrence=0):
    if mention_id in mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    line = source_lines[line_no - 1]
    positions = []
    cursor = 0
    while True:
        found = line.find(surface, cursor)
        if found < 0:
            break
        positions.append(found)
        cursor = found + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface missing on L{line_no}: {surface!r}")
    start = line_offsets[line_no] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"invalid exact mention span: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown mention candidate: {candidate_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": SEGMENT_ID,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })


add_mention("m-chp9-p265n1-source", 429, candidate_by_key["haskell_levey_1958"], "1958, p. 182", "Short-form citation locator for the preceding Angelo Custode account; not independently consulted.")
add_mention("m-chp9-p265n1-levey", 429, candidate_by_key["person_levey"], "Levey", "Author is given by surname only; identity remains open for bibliography review and S3.")
add_mention("m-chp9-p265n3-print428", 430, candidate_by_key["correr_print_428"], "print 428", "Print number and volume locator; dedication continuation appears in p.265 body L298.")
add_mention("m-chp9-p265n3-correr", 430, EXISTING["correr"], "Biblioteca Correr", "Repository named by Haskell; its cited volume has not been independently consulted.")
add_mention("m-chp9-p265n4-date-aug", 431, candidate_by_key["marchesini_letter_aug"], "11 August", "Date locator for one of two letters; source scan confirms the printed day and month.")
add_mention("m-chp9-p265n4-date-dec", 431, candidate_by_key["marchesini_letter_dec"], "I December 1725", "Exact S0 surface retained; scan reads the initial date as 1 December 1725, not a letter I.")
add_mention("m-chp9-p265n4-marchesini", 431, EXISTING["marchesini"], "Alessandro Marchesini", "Author of the two letters cited by Haskell.")
add_mention("m-chp9-p265n4-conti", 431, EXISTING["conti"], "Stefano Conti", "Recipient of the two letters cited by Haskell.")
add_mention("m-chp9-p265n4-publication", 431, candidate_by_key["haskell_1956_p298"], "Haskell, 1956, p. 298", "Publication locator only; full bibliographic identity is deferred to the book bibliography pass.")
add_mention("m-chp9-p265n5-vmoschini", 431, candidate_by_key["person_v_moschini"], "V. Moschini", "Initial and surname only; do not merge with G. A. Moschini.")
add_mention("m-chp9-p265n5-source", 431, candidate_by_key["moschini_v_1956"], "1956, p. 12", "Citation locator for the arguments Haskell invokes; contents not independently consulted.")
add_mention("m-chp9-p265n6-source", 432, candidate_by_key["crespi_l_p215"], "p. 215", "L. Crespi citation; distinguish this locator from other short-form Crespi references until bibliography review.")
add_mention("m-chp9-p265n6-crespi-author", 432, EXISTING["crespi_l"], "L. Crespi", "Source form maps to the existing surname-and-initial person candidate; full identity remains for S3.")
add_mention("m-chp9-p265n6-nativity", 432, candidate_by_key["nativity_work"], "a Nativity", "One of two unnamed religious works; no title or surviving object is identified.")
add_mention("m-chp9-p265n6-mission", 432, candidate_by_key["mission_work"], "a Mission", "One of two unnamed religious works; the proposed Chicago match remains uncertain.")
add_mention("m-chp9-p265n6-jesuit-mission", 432, candidate_by_key["jesuit_mission_chicago"], "Jesuit Mission", "The cited comparison work or group is not identified at object level.")
add_mention("m-chp9-p265n6-chicago", 432, EXISTING["chicago"], "Chicago", "Place reported for the possible Jesuit Mission match; no institution is named.")
add_mention("m-chp9-p266n2-moschini", 434, EXISTING["moschini_ga"], "G. A. Moschini", "Indexed author; the scan confirms volume I where S0 OCR reads the numeral 1.")
add_mention("m-chp9-p266n2-source", 434, candidate_by_key["moschini_ga_1806_v1_p84"], "1806,1, p. 84", "Citation locator; S2 reads the volume as Roman numeral I from the scan.")
add_mention("m-chp9-p266n3-dacanal", 435, EXISTING["dacan"], "Da Canal", "Surname reference; publication identity to be linked when the bibliography is reviewed.")
add_mention("m-chp9-p266n3-dacanal-source", 435, candidate_by_key["da_canal_p77"], "p. 77", "Short-form cited page; no external source page consulted.")
add_mention("m-chp9-p266n3-fontana", 435, candidate_by_key["person_fontana"], "Fontana", "Surname only; author identity remains unresolved.")
add_mention("m-chp9-p266n3-fontana-source", 435, candidate_by_key["fontana_p64"], "p. 64", "Short-form cited page; no external source page consulted.")
add_mention("m-chp9-p266n4-smith", 436, EXISTING["smith"], "Smith", "Use the index candidate that includes p.266; the will reference concerns Joseph Smith but is not independently checked.")
add_mention("m-chp9-p266n4-parker", 436, candidate_by_key["person_parker"], "Parker", "Publication author is supplied by surname only.")
add_mention("m-chp9-p266n4-source", 436, candidate_by_key["smith_will_parker_1948"], "1948, p. 60", "Citation locator for the will as published; not independently consulted.")
add_mention("m-chp9-p266n5-popham", 437, candidate_by_key["person_popham"], "Popham", "Author is identified by surname only.")
add_mention("m-chp9-p266n5-wilde", 437, candidate_by_key["person_wilde"], "Wilde", "Author is identified by surname only.")
add_mention("m-chp9-p266n5-source", 437, candidate_by_key["popham_wilde_1949"], "1949, p. 14", "Short-form publication locator; not independently consulted.")
add_mention("m-chp9-p266n6-zanetti", 438, EXISTING["zanetti"], "A. M. Zanetti", "Indexed person candidate; this is a dated letter attribution, not an identity verification.")
add_mention("m-chp9-p266n6-gabburri", 438, EXISTING["gabburri"], "Francesco Gabburri", "Indexed letter recipient candidate.")
add_mention("m-chp9-p266n6-date", 438, candidate_by_key["zanetti_letter_1728"], "11 January 1728", "Date locator for the cited letter; no manuscript or printed letter independently consulted.")
add_mention("m-chp9-p266n6-bottari", 438, EXISTING["bottari_p186"], "Bottari, II, p. 186", "Reuse the existing exact Bottari volume II page-locator candidate.")
add_mention("m-chp9-p266n7-blunt", 439, EXISTING["blunt"], "Blunt", "Indexed Anthony Blunt candidate; cited page is a locator, not independent verification.")
add_mention("m-chp9-p266n7-source", 439, candidate_by_key["blunt_1954"], "1954, p. 24", "Short-form citation locator; not independently consulted.")
add_mention("m-chp9-p267n2-smith", 442, EXISTING["smith"], "Smith", "Will owner is identified through the index candidate; the source locator itself is not independently checked.")
add_mention("m-chp9-p267n2-parker", 442, candidate_by_key["person_parker"], "Parker", "Surname-only publication author.")
add_mention("m-chp9-p267n2-source", 442, candidate_by_key["smith_will_parker_1948"], "1948, p. 60", "Citation locator for the same cited will publication as p.266 note 4.")
add_mention("m-chp9-p267n3-fochessati", 443, candidate_by_key["person_fochessati"], "Fochessati", "Surname-only cited author.")
add_mention("m-chp9-p267n3-source", 443, candidate_by_key["fochessati_p278"], "p. 278", "Short-form cited page; not independently consulted.")
add_mention("m-chp9-p267n4-malamani", 444, candidate_by_key["person_malamani"], "Malamani", "Surname-only cited author.")
add_mention("m-chp9-p267n4-source", 444, candidate_by_key["malamani_1899_p46"], "1899, p. 46", "Short-form cited page; not independently consulted.")
add_mention("m-chp9-p267n5-blunt", 445, EXISTING["blunt"], "Blunt", "Same author candidate as p.266 note 7; publication identity remains provisional.")
add_mention("m-chp9-p267n5-source", 445, candidate_by_key["blunt_1954"], "1954, p. 36", "Second page locator for the provisional Blunt 1954 source candidate.")

new_statements = []
def ref(segment_id, start, end=None):
    return {"segment_id": segment_id, "source_line_start": start, "source_line_end": end if end is not None else start}


def note_quote(line_no, start=None, end=None):
    line = source_lines[line_no - 1]
    left = line.index(start) if start else 0
    right = line.index(end, left) + len(end) if end else len(line)
    return line[left:right]


def add_statement(statement_id, line_no, subject, object_, predicate, quote, claim, qualification, mentioned, *, page, physical, footnote=None, relation=False, crossrefs=(), text_layer="footnote citation", speaker="Haskell's footnote"):
    if statement_id in statement_ids or any(row["statement_id"] == statement_id for row in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in segment_text:
        raise SystemExit(f"quote not anchored to the consolidated note segment: {statement_id}")
    refs = set(mentioned)
    refs.update(candidate for candidate in (subject, object_) if candidate)
    if not refs <= candidate_ids:
        raise SystemExit(f"unknown statement candidate in {statement_id}: {sorted(refs - candidate_ids)}")
    qualifiers = {
        "source_line_start": line_no,
        "source_line_end": line_no,
        "printed_page": page,
        "pdf_physical_page": physical,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": sorted(refs),
    }
    if crossrefs:
        qualifiers["cross_reference_segments"] = list(crossrefs)
    if footnote is not None:
        qualifiers["footnote_marker"] = footnote
    if relation:
        qualifiers["relation_candidate"] = True
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
        "origin": "book",
    })


add_statement("st-chp9-p265-note1-source-locator", 429, None, candidate_by_key["haskell_levey_1958"], "cited_source_for_piazzetta_angelo_custode_account", note_quote(429), "Haskell cites Haskell and Levey, 1958, p.182, in connection with the preceding Angelo Custode account.", "Bibliographic locator only; neither the publication nor cited page was independently consulted. The full title is deferred to the book bibliography pass.", [candidate_by_key["haskell_levey_1958"], candidate_by_key["person_levey"], EXISTING["angelo"]], page=265, physical=31, footnote=1, crossrefs=[ref(BODY_P265, 292)])
add_statement("st-chp9-p265-note3-correr-print-dedication", 430, candidate_by_key["correr_print_428"], EXISTING["zaccaria"], "print_428_in_correr_collection_dedicated_to_zaccaria_sagredo", note_quote(430), "Haskell locates the dedication quoted at p.265 in print 428, volume 3 of Raccolta Gherro at Biblioteca Correr, and says it was dedicated to Zaccaria Sagredo.", "The scan supplies the dedication's continuation in p.265 body L298; the print itself was not independently examined. Preserve the source's honorific rather than infer a formal commission.", [candidate_by_key["correr_print_428"], EXISTING["correr"], EXISTING["zaccaria"]], page=265, physical=31, footnote=3, relation=True, crossrefs=[ref(BODY_P265, 294), ref(BODY_P265, 298)], text_layer="footnote source locator")
add_statement("st-chp9-p265-note4-marchesini-letter-1725-08-11", 431, EXISTING["marchesini"], candidate_by_key["marchesini_letter_aug"], "marchesini_letter_to_conti_dated_1725_08_11", note_quote(431, "4 See", "published by Haskell, 1956, p. 298."), "Haskell cites an 11 August 1725 letter from Alessandro Marchesini to Stefano Conti, published at Haskell 1956, p.298.", "Citation locator only; the letter's contents, edition identity and manuscript witness have not been independently checked.", [EXISTING["marchesini"], EXISTING["conti"], candidate_by_key["marchesini_letter_aug"], candidate_by_key["haskell_1956_p298"]], page=265, physical=31, footnote=4, relation=True, crossrefs=[ref(BODY_P265, 294)], text_layer="footnote citation")
add_statement("st-chp9-p265-note4-marchesini-letter-1725-12-01", 431, EXISTING["marchesini"], candidate_by_key["marchesini_letter_dec"], "marchesini_letter_to_conti_dated_1725_12_01", note_quote(431, "and I December 1725", "published by Haskell, 1956, p. 298."), "Haskell cites a 1 December 1725 letter from Alessandro Marchesini to Stefano Conti, published at Haskell 1956, p.298.", "The S0 OCR reads the day as capital I; the scan shows the numeral 1. Citation locator only; letter contents and edition identity have not been independently checked.", [EXISTING["marchesini"], EXISTING["conti"], candidate_by_key["marchesini_letter_dec"], candidate_by_key["haskell_1956_p298"]], page=265, physical=31, footnote=4, relation=True, crossrefs=[ref(BODY_P265, 294)], text_layer="footnote citation")
add_statement("st-chp9-p265-note5-vmoschini-citation", 431, EXISTING["zaccaria"], candidate_by_key["moschini_v_1956"], "moschini_1956_argument_cited_for_possible_longhi_commission", note_quote(431, "5 See", "p. 12."), "Haskell directs readers to V. Moschini, 1956, p.12, for the argument supporting the possible Zaccaria Sagredo commission of Longhi's Fall of the Giants.", "The author is given only as V. Moschini and is not merged with G. A. Moschini. The cited argument has not been independently consulted; Haskell's commission claim remains tentative.", [EXISTING["zaccaria"], EXISTING["longhi"], EXISTING["longhi_fresco"], candidate_by_key["person_v_moschini"], candidate_by_key["moschini_v_1956"]], page=265, physical=31, footnote=5, crossrefs=[ref(BODY_P265, 295)], text_layer="footnote citation")
add_statement("st-chp9-p265-note6-crespi-works-identified", 432, EXISTING["crespi_group"], None, "two_crespi_religious_works_identified_as_nativity_and_mission", note_quote(432, "6 The pictures", "L. Crespi, p. 215."), "Haskell identifies the two religious works attributed to Giuseppe Maria Crespi for Zaccaria Sagredo as a Nativity and a Mission, citing L. Crespi, p.215.", "The individual compositions have no full titles, dates or current locations here. The abbreviated Crespi publication remains unresolved and is kept distinct from other L. Crespi citations.", [EXISTING["crespi_group"], EXISTING["gmcrespi"], EXISTING["zaccaria"], candidate_by_key["crespi_l_p215"], EXISTING["crespi_l"], candidate_by_key["nativity_work"], candidate_by_key["mission_work"]], page=265, physical=31, footnote=6, crossrefs=[ref(BODY_P265, 295)], text_layer="footnote claim")
add_statement("st-chp9-p265-note6-possible-chicago-jesuit-mission", 432, candidate_by_key["mission_work"], candidate_by_key["jesuit_mission_chicago"], "mission_may_match_jesuit_mission_pictures_reported_in_chicago", note_quote(432, "The latter may", None), "Haskell says the Mission may be the pictures described as a Jesuit Mission now in Chicago.", "Preserve 'may' and the plural 'pictures'; this does not establish that the unidentified Mission is the Chicago work or group.", [candidate_by_key["mission_work"], candidate_by_key["jesuit_mission_chicago"], EXISTING["chicago"], EXISTING["crespi_group"]], page=265, physical=31, footnote=6, relation=True, crossrefs=[ref(BODY_P265, 295)], text_layer="footnote claim")
add_statement("st-chp9-p266-note1-breval-crossreference", 433, EXISTING["angelo"], None, "p266_note1_refers_to_p263_note3", note_quote(433, "1 See", "note 3."), "P.266 note 1 directs readers to p.263 note 3 for the preceding Breval-related discussion.", "Internal cross-reference only; it adds no new independent evidence or entity.", [EXISTING["angelo"]], page=266, physical=32, footnote=1, crossrefs=[ref(SEGMENT_ID, 416)], text_layer="internal note cross-reference")
add_statement("st-chp9-p266-note2-moschini-source", 434, EXISTING["torresani_views"], candidate_by_key["moschini_ga_1806_v1_p84"], "moschini_1806_cited_for_sagredo_torresani_views", note_quote(434), "Haskell cites G. A. Moschini, 1806, volume I, p.84, for Sagredo's commissioned views from Andrea Torresani.", "The scan reads Roman volume I; S0 OCR uses digit 1. The cited page has not been independently consulted.", [EXISTING["moschini_ga"], candidate_by_key["moschini_ga_1806_v1_p84"], EXISTING["torresani_views"]], page=266, physical=32, footnote=2, crossrefs=[ref(BODY_P266, 305, 306)])
add_statement("st-chp9-p266-note3-dacanal-fontana-citations", 435, None, None, "da_canal_and_fontana_cited_for_lazzarini_diziani_drawings", note_quote(435), "P.266 note 3 cites Da Canal, p.77, and Fontana, p.64, alongside Haskell's report about Lazzarini's drawings and Diziani's drawing volume.", "The note supplies short citations only; neither source page was independently consulted, and Fontana's identity and work remain unresolved.", [EXISTING["dacan"], candidate_by_key["da_canal_p77"], candidate_by_key["person_fontana"], candidate_by_key["fontana_p64"], EXISTING["lazzarini_drawings"], EXISTING["diziani_volume"]], page=266, physical=32, footnote=3, crossrefs=[ref(BODY_P266, 306)], text_layer="footnote citation")
add_statement("st-chp9-p266-note4-smith-will-citation", 436, EXISTING["smith"], candidate_by_key["smith_will_parker_1948"], "smith_will_published_by_parker_cited_for_sagredo_drawings", note_quote(436), "Haskell cites Smith's will as published by Parker, 1948, p.60, in the account of drawings acquired from the Sagredo collection.", "This is a locator through Haskell; the will and Parker publication have not been independently examined.", [EXISTING["smith"], candidate_by_key["person_parker"], candidate_by_key["smith_will_parker_1948"]], page=266, physical=32, footnote=4, crossrefs=[ref(BODY_P266, 308)], text_layer="footnote citation")
add_statement("st-chp9-p266-note5-popham-wilde-citation", 437, EXISTING["raphael_sheets"], candidate_by_key["popham_wilde_1949"], "popham_wilde_1949_cited_for_raphael_sheets", note_quote(437), "Haskell cites Popham and Wilde, 1949, p.14, in connection with the fine Raphael sheets in Sagredo's purchase.", "Short-form citation only; author identities, title and cited page are not independently verified.", [EXISTING["raphael_sheets"], candidate_by_key["person_popham"], candidate_by_key["person_wilde"], candidate_by_key["popham_wilde_1949"]], page=266, physical=32, footnote=5, crossrefs=[ref(BODY_P266, 308)], text_layer="footnote citation")
add_statement("st-chp9-p266-note6-zanetti-letter-citation", 438, EXISTING["zanetti"], candidate_by_key["zanetti_letter_1728"], "zanetti_letter_to_gabburri_cited_for_connoisseur_quote", note_quote(438), "Haskell cites an 11 January 1728 letter from A. M. Zanetti to Francesco Gabburri, published in Bottari, volume II, p.186, for the preceding quotation about original works by great masters.", "The citation is not an independent reading of either the letter or Bottari; reuse the existing Bottari II p.186 locator candidate.", [EXISTING["zanetti"], EXISTING["gabburri"], candidate_by_key["zanetti_letter_1728"], EXISTING["bottari_p186"]], page=266, physical=32, footnote=6, crossrefs=[ref(BODY_P266, 308)], relation=True, text_layer="footnote citation")
add_statement("st-chp9-p266-note7-blunt-citation", 439, EXISTING["castiglione"], candidate_by_key["blunt_1954"], "blunt_1954_p24_cited_for_castiglione_reception", note_quote(439), "Haskell directs readers to Anthony Blunt, 1954, p.24, in the discussion of Castiglione's reception and importance.", "Short-form citation locator only; source title and page content are deferred to bibliography review and have not been independently checked.", [EXISTING["blunt"], EXISTING["castiglione"], candidate_by_key["blunt_1954"]], page=266, physical=32, footnote=7, crossrefs=[ref(BODY_P266, 309)], text_layer="footnote citation")
add_statement("st-chp9-p266-note8-chapter-reference", 440, EXISTING["zanetti"], None, "zanetti_engraving_discussion_crossrefers_to_chapter_13", note_quote(440), "P.266 note 8 directs readers to Chapter 13 for the preceding statement about Zanetti's 1759 engravings.", "Internal book cross-reference only; no new evidence or entity is asserted.", [EXISTING["zanetti"], EXISTING["zanetti_engravings"]], page=266, physical=32, footnote=8, crossrefs=[ref(BODY_P266, 311)], text_layer="internal chapter cross-reference")
add_statement("st-chp9-p267-note1-chapter-reference", 441, EXISTING["tiepolo"], EXISTING["castiglione"], "tiepolo_castiglione_influence_discussion_crossrefers_to_chapter_14", note_quote(441), "P.267 note 1 directs readers to Chapter 14 for the preceding account of Algarotti pointing out Castiglione's influence on Tiepolo.", "Internal book cross-reference only; it does not add independent support to the influence claim.", [EXISTING["tiepolo"], EXISTING["castiglione"]], page=267, physical=33, footnote=1, crossrefs=[ref(BODY_P267, 314, 315)], text_layer="internal chapter cross-reference")
add_statement("st-chp9-p267-note2-smith-will-citation", 442, EXISTING["smith"], candidate_by_key["smith_will_parker_1948"], "smith_will_cited_for_sagredo_castiglione_drawing_price", note_quote(442), "Haskell cites Smith's will as published by Parker, 1948, p.60, for the reported price of Sagredo's Castiglione drawings.", "The price remains Haskell's report ('were said to'); the will and publication have not been independently examined.", [EXISTING["smith"], candidate_by_key["person_parker"], candidate_by_key["smith_will_parker_1948"], EXISTING["sagredo_drawings"]], page=267, physical=33, footnote=2, crossrefs=[ref(BODY_P267, 316, 317)], text_layer="footnote citation")
add_statement("st-chp9-p267-note3-fochessati-citation", 443, EXISTING["ferdinando"], candidate_by_key["fochessati_p278"], "fochessati_p278_cited_for_ferdinando_characterization", note_quote(443), "Haskell cites Fochessati, p.278, for the quoted characterization associated with Ferdinando Carlo's death.", "The cited page has not been independently consulted; retain the phrase as a nested source characterization, not a medical finding.", [EXISTING["ferdinando"], candidate_by_key["person_fochessati"], candidate_by_key["fochessati_p278"]], page=267, physical=33, footnote=3, crossrefs=[ref(BODY_P267, 318)], text_layer="footnote citation")
add_statement("st-chp9-p267-note4-malamani-citation", 444, EXISTING["schulenburg"], candidate_by_key["malamani_1899_p46"], "malamani_p46_cited_for_schulenburg_mantuan_market_purchase", note_quote(444, "4 Malamani", "Chapter II."), "Haskell cites Malamani, 1899, p.46, for the preceding account of Schulenburg's Mantuan-market purchase, and directs readers to Chapter 11.", "Short-form citation locator and internal cross-reference only; the cited page has not been independently checked.", [EXISTING["schulenburg"], candidate_by_key["person_malamani"], candidate_by_key["malamani_1899_p46"]], page=267, physical=33, footnote=4, crossrefs=[ref(BODY_P267, 320, 321)], text_layer="footnote citation")
add_statement("st-chp9-p267-note5-blunt-citation", 445, EXISTING["ferdinando"], candidate_by_key["blunt_1954"], "blunt_1954_p36_cited_for_tentative_sagredo_drawing_provenance", note_quote(445), "Haskell cites Anthony Blunt, 1954, p.36, in connection with the expressly tentative Mantuan provenance hypothesis for Sagredo's drawings.", "Citation locator only; do not upgrade the hypothesis to a confirmed transfer. The cited page has not been independently consulted.", [EXISTING["blunt"], EXISTING["ferdinando"], EXISTING["sagredo_drawings"], candidate_by_key["blunt_1954"]], page=267, physical=33, footnote=5, crossrefs=[ref(BODY_P267, 321)], text_layer="footnote citation")

all_statement_ids = {row["statement_id"] for row in statements} | {row["statement_id"] for row in new_statements}
if len(all_statement_ids) != len(statements) + len(new_statements):
    raise SystemExit("duplicate statement IDs in migration")
if len({row["mention_id"] for row in mentions + new_mentions}) != len(mentions) + len(new_mentions):
    raise SystemExit("duplicate mention IDs in migration")

note_coverage.update({
    "disposition": "reviewed",
    "migration_status": "complete",
    "source_line_ranges": "L349-445; p.255 L155 continuation; p.263 note 6 continues at p.264 L245-248; p.264 note 8 continued at p.265 L295-296; p.265 notes L429-432; p.266 notes L433-440; p.267 notes L441-445",
    "note": "Consolidated p.265-267 notes L429-445 have now been read against CHP-9.pdf physical pp.31-33 and migrated. Note 3's print 428 dedication continuation is cross-referenced to p.265 L298. Notes 4-6 identify the Marchesini letters, V. Moschini citation, and Crespi's Nativity/Mission with a tentative Chicago match. Short-form citations remain locators, not independent verification; reconcile their full identities when S2 reaches the bibliography. P.267 note 6 is not missing: it appears as line 4 in 09_CHP-9_sec_ii.md, where OCR reads its printed marker 6 as 'a'; it will be processed with that section's L3-4 segment. OCR sources remain unchanged; scan corrections are recorded in S2.",
})
for body_id, revised_note in {
    BODY_P265: "Printed p.265 body and notes read against CHP-9.pdf physical p.31. The p.264 note 8 continuation at L295-296 is closed. Notes 1-6 are now linked to the consolidated note segment L429-432, including print 428 dedication, two dated Marchesini letters, the tentative Longhi citation, and Crespi's Nativity/Mission identification. S0 OCR remains unchanged; scan-based corrections and unresolved short-form citations are recorded in S2.",
    BODY_P266: "Printed p.266 body (PDF physical p.32) read against the scan. S2 records visual corrections without changing S0: printed Cimaroli for OCR Cimatoli; 100 views for OCR 'too views'; 'the German' for 'thejGerman'; 'to' for 'tò'; 'of his' for 'ofhis'; and continuation 'who was also given' where OCR begins L310 with a comma. The unfinished p.266 L311 phrase 'Of greater' closes at p.267 L314. P.266 notes 1-8 at consolidated L433-440 are now migrated and linked to the corresponding body statements.",
    BODY_P267: "Printed p.267 body (PDF physical p.33) read against the scan; L314 closes p.266 L311. Haskell's interpretation, nested source claims, the reported 1500-zecchini price and expressly tentative Mantuan provenance are separated. Notes 1-5 at consolidated L441-445 are now migrated. Printed note 6 appears in the following section's S0 source at L4; OCR reads its superscript 6 as 'a', so it will be reviewed with section II L3-4 rather than duplicated here.",
}.items():
    coverage_by_id[body_id]["note"] = revised_note

summary = {
    "segment": SEGMENT_ID,
    "new_candidates": len(new_candidates),
    "new_candidate_ids": [row["candidate_id"] for row in new_candidates],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage": "reviewed/complete",
    "corrected_gap_assessment": "p.267 printed note 6 exists at chp-9:09_CHP-9_sec_ii:l3-4; OCR marker is 'a', not missing text",
    "scan_corrections": ["p.265 note 4: I December -> 1 December 1725", "p.266 note 2: OCR 1 -> printed volume I", "p.267 note 4: Chapter II -> Chapter 11 by Roman chapter numbering"],
    "remaining_note6_action": "process with chp-9:09_CHP-9_sec_ii:l3-4; do not create a duplicate visual-transcription segment",
    "counts_after": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements),
        "coverage_rows": len(coverage),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source_path, backup_path in zip(paths, backups):
        shutil.copy2(source_path, backup_path)
    try:
        write_csv(candidate_path, candidate_fields, candidates + new_candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(path.name for path in backups))
else:
    print("DRY RUN: no S2 table rows written")
