"""Controlled S2 migration for Chapter 8 printed page 238 and its notes.

Default invocation is a read-only dry run. OCR source files are never edited.
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
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
P237 = "chp-8:08_CHP-8_sec_ii:l311-325"
P238 = "chp-8:08_CHP-8_sec_ii:l327-336"
P239 = "chp-8:08_CHP-8_sec_ii:l338-348"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
BIB = "chp-21:21_CHP-21Bibliography:l295-334"
TARGETS = {P237, P238, P239, NOTES, BIB}
BACKUP_SUFFIX = ".bak-s2-chp8-p238-20261001"
PAGE_SCAN = PROCESS / "p238_page_review.png"
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp"
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or not TARGETS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
for segment_id in TARGETS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")
if not PAGE_SCAN.is_file() or not PDF.is_file():
    raise SystemExit("page 238 PDF or review image is missing")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
bib_lines = (ROOT / segment_by_id[BIB]["source_file"]).read_text(encoding="utf-8-sig").splitlines()
if "Casini, Giorgio: ‘Aggiunte al Crespi’ in L’Archiginnasio, Gennaio—Giugno, 1941, pp. 42-50." not in bib_lines[320]:
    raise SystemExit("bibliography line 321 no longer matches the cited Casini entry")

line_offsets = {}
for segment_id in TARGETS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    lines = asset.read_text(encoding="utf-8-sig").splitlines()
    selected = lines[meta["line_start"] - 1:meta["line_end"]]
    if hashlib.sha256("\n".join(selected).encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), selected):
        line_offsets[(segment_id, line_no)] = offset
        offset += len(line) + 1

candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
mention_fields, mention_rows = read_csv(TABLES / "mentions.csv")
statement_rows = read_jsonl(TABLES / "book-statements.jsonl")
coverage_fields, coverage_rows = read_csv(TABLES / "s2-coverage.csv")
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
expected = {
    P237: ("reviewed", "partial", "L312-325"),
    P238: ("queued", "pending", ""),
    P239: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L373-442"),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")

new_candidates = [
    ("cand-8030", "Archivio Mediceo, Filza 5904, letter No. 26", "archive", 443,
     "One of three letters cited for March and April 1708; its date and contents are not individually specified here."),
    ("cand-8031", "Archivio Mediceo, Filza 5904, letter No. 38", "archive", 443,
     "One of three letters cited for March and April 1708; its date and contents are not individually specified here."),
    ("cand-8032", "Archivio Mediceo, Filza 5904, letter No. 357", "archive", 443,
     "One of three letters cited for March and April 1708; a later note separately identifies a Ferdinand letter of 28 April 1708 as No. 357."),
    ("cand-8033", "Archivio Mediceo, Filza 5904, letter No. 167", "archive", 444,
     "Letter locator cited for correspondence between Ferdinand and Giovanni Ricci; text not independently consulted."),
    ("cand-8034", "Archivio Mediceo, Filza 5904, letter No. 476", "archive", 444,
     "Letter locator cited for correspondence between Ferdinand and Giovanni Ricci; text not independently consulted."),
    ("cand-8035", "Archivio Mediceo, Filza 5904, letter No. 174", "archive", 444,
     "Letter locator cited for correspondence between Ferdinand and the Pepoli; its relation to the two urgent letters is unresolved."),
    ("cand-8036", "Archivio Mediceo, Filza 5904, letter No. 489", "archive", 444,
     "Letter locator cited for correspondence between Ferdinand and the Pepoli; its relation to the two urgent letters is unresolved."),
    ("cand-8037", "Archivio Mediceo, Filza 5904, letter No. 490", "archive", 444,
     "Letter locator cited for correspondence between Ferdinand and the Pepoli; its relation to the two urgent letters is unresolved."),
    ("cand-8038", "Archivio Mediceo, Filza 5904, letter No. 475", "archive", 445,
     "Original draft of a letter from Ferdinand, also published by Luigi Crespi at p.203; document and published text not independently consulted."),
    ("cand-8039", "Archivio Mediceo, Filza 5904, letter No. 272", "archive", 448,
     "Letter dated 3 November 1709 cited as reporting Crespi's return to Bologna; original not independently consulted."),
    ("cand-8040", "Archivio Mediceo, Filza 5904 (archival series)", "archive", 443,
     "Archival series repeated in the page's citations; repository catalogue and series boundaries were not checked."),
    ("cand-8041", "Crespi's ceiling frescoes in the Pepoli palace", "work", 329,
     "Group of ceiling frescoes Haskell says Crespi painted at the Pepoli palace about fifteen years before 1708; individual scenes are not identified."),
    ("cand-8042", "Two urgent Ferdinand letters to the Pepoli that halted the planned palace alterations", "archive", 329,
     "The body calls these two letters urgent; note 2 lists three Pepoli correspondence locators, and their exact mapping to the pair is unresolved."),
    ("cand-8043", "Ferdinando, newborn son of Giuseppe Maria Crespi (1709)", "person", 334,
     "Named as Crespi's newborn son and Ferdinand's godson; no further identity or biography is inferred."),
    ("cand-8044", "pittore attuale (court designation given to Crespi)", "term", 334,
     "Italian designation quoted by Haskell as official recognition of Crespi's position at court; no modern office equivalence is inferred."),
    ("cand-8045", "vasallaggio (Crespi's wording in a promise to Ferdinand)", "term", 328,
     "Quoted wording for Crespi's promised service or allegiance; it is not treated as evidence of a legal feudal status."),
    ("cand-8046", "Casini, Giorgio", "person", 446,
     "The note gives the surname; the directly consulted book bibliography entry at chp-21 L321 identifies the author as Giorgio Casini. That segment remains queued for full semantic processing; identity alignment remains for S3."),
    ("cand-8047", "Giorgio Casini, Aggiunte al Crespi (1941 article)", "archive", 446,
     "Article cited at pp.42-50 in note 4; title and publication details were retrieved by direct cross-reference to the book bibliography at chp-21 L321. That segment remains queued for full semantic processing; the article was not independently read."),
    ("cand-8048", "Gabinetto del R. Intendente di Finanza di Pisa", "institution", 446,
     "Named as a reported location for pictures; the wording may denote an office, cabinet, or associated holding space, and the exact boundary is unresolved."),
]

candidate_ids = {row["candidate_id"] for row in candidate_rows}
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 8029:
    raise SystemExit("candidate ID sequence changed since p.237; inspect before allocating IDs")
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 439 else P238
    source_ref = f"{anchor_segment}#L{source_line}"
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": source_ref,
    })
    candidate_ids.add(candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
new_mentions = []


def mention(segment_id, line_no, suffix, candidate_id, surface, note="", occurrence=0):
    mention_id = f"m-chp8-p238-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    asset_lines = source_lines if segment_id != BIB else bib_lines
    line = asset_lines[line_no - 1]
    position = -1
    search_at = 0
    for _ in range(occurrence + 1):
        position = line.find(surface, search_at)
        if position < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r} #{occurrence}")
        search_at = position + 1
    start = line_offsets[(segment_id, line_no)] + position
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans:
        prior = next(row for row in mention_rows if (row["segment_id"], row["start_char"], row["end_char"]) == span)
        raise SystemExit(f"duplicate existing mention span {span}: {prior['mention_id']} {prior['surface_form']!r}")
    duplicate = next((row for row in new_mentions if (row["segment_id"], row["start_char"], row["end_char"]) == span), None)
    if duplicate:
        raise SystemExit(f"duplicate new mention span {span}: {duplicate['mention_id']} {duplicate['surface_form']!r} conflicts with {mention_id} {surface!r}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


MENTION_SPECS = [
    (P238, 328, "opening-ferdinand", "cand-1609", "Ferdinand", "Ferdinand de’ Medici."),
    (P238, 328, "painter", "cand-0871", "a painter", "Giuseppe Maria Crespi, whose gifts suited Ferdinand’s temperament."),
    (P238, 328, "bologna-return", "cand-3398", "Bologna", "Crespi’s reported return location."),
    (P238, 328, "new-patron", "cand-1609", "his new patron", "Coreference to Ferdinand de’ Medici."),
    (P238, 328, "nativity", "cand-0883", "a Nativity", "Crespi index subentry for the work; exact object identity remains for S3."),
    (P238, 328, "selfportrait-first", "cand-0886", "a Self portrait", "Source OCR spacing retained in the mention; printed form is Selfportrait."),
    (P238, 328, "prince-kindness", "cand-1609", "the Prince’s", "Ferdinand de’ Medici."),
    (P238, 328, "artist-remembrance", "cand-0871", "the artist’s", "Coreference to Crespi."),
    (P238, 328, "vasallaggio", "cand-8045", "‘vasallaggio’", "Quoted Italian wording; do not infer legal vassal status."),
    (P238, 328, "prince-reply", "cand-1609", "The Prince", "Ferdinand de’ Medici."),
    (P238, 329, "selfportrait-second", "cand-0886", "Selfportrait", "Crespi’s self-portrait; title spelling follows the printed page."),
    (P238, 329, "artist-good-humour", "cand-0871", "the artist’s", "Coreference to Crespi."),
    (P238, 329, "ferdinand-interest", "cand-1609", "Ferdinand’s", "Ferdinand de’ Medici."),
    (P238, 329, "crespi-interest", "cand-0871", "Crespi", "Giuseppe Maria Crespi."),
    (P238, 329, "bologna-patrons", "cand-3398", "Bologna", "City where Crespi’s patrons are described."),
    (P238, 329, "giovanni-ricci", "cand-2147", "Giovanni Ricci", "Index candidate; identity alignment remains for S3."),
    (P238, 329, "ricci-travels", "cand-2147", "his", "Possessive referring to Giovanni Ricci in context; financing is attributed to Ricci."),
    (P238, 329, "italy-travels", "cand-3461", "Italy", "Geographic extent of Ricci’s financing of Crespi’s early travels."),
    (P238, 329, "ricci-work", "cand-2147", "he", "Coreference to Giovanni Ricci as the acquirer of Crespi’s work."),
    (P238, 329, "crespi-work-acquired", "cand-0871", "his work", "Coreference to Crespi’s artistic production."),
    (P238, 329, "pepoli-family", "cand-7377", "the Pepoli family", "Family named as Crespi’s patrons."),
    (P238, 329, "pepoli-palace", "cand-1872", "palace", "The Pepoli palace; exact architectural identity remains for S3."),
    (P238, 329, "crespi-fresco-painter", "cand-0871", "he", "Coreference to Crespi as painter of the frescoes.", 1),
    (P238, 329, "ceiling-frescoes", "cand-8041", "the great ceiling frescoes", "Unidentified group of Crespi frescoes in the Pepoli palace."),
    (P238, 329, "crespi-reputation", "cand-0871", "his reputation", "Coreference to Crespi."),
    (P238, 329, "pepoli-plans", "cand-7377", "the Pepoli", "The Pepoli family; individual decision-makers are not named."),
    (P238, 329, "palace-alterations", "cand-1872", "the palace", "The Pepoli palace."),
    (P238, 329, "frescoes-threatened", "cand-8041", "the frescoes", "Coreference to the ceiling-fresco group."),
    (P238, 329, "urgent-letter-pair", "cand-8042", "two urgent letters", "The two letters are not identified among the three Pepoli correspondence locators in note 2."),
    (P238, 329, "ferdinand-stopped-plan", "cand-1609", "Ferdinand", "Sender of the two urgent letters as reported in the body."),
    (P238, 330, "crespi-worked", "cand-0871", "Crespi", "Giuseppe Maria Crespi."),
    (P238, 330, "ferdinand-worked-for", "cand-1609", "him", "Coreference to Ferdinand."),
    (P238, 330, "crespi-copy", "cand-0875", "a copy", "Crespi index subentry for his copy of Guercino’s St William of Aquitaine."),
    (P238, 330, "guercino", "cand-1258", "Guercino", "Francesco Barbieri, subject to S3 identity alignment."),
    (P238, 330, "st-william-original", "cand-1269", "St William of Aquitaine", "Guercino index subentry for the source painting; kept distinct from Crespi’s copy."),
    (P238, 330, "painter-family-work", "cand-0884", "his own small painting of", "Work title continues on p.238 L331."),
    (P238, 331, "painters-family-title", "cand-0884", "The Painter’s Family", "Crespi index subentry for the painting."),
    (P238, 331, "crespi-confidence", "cand-0871", "Crespi’s", "Giuseppe Maria Crespi."),
    (P238, 331, "ferdinand-tastes", "cand-1609", "Ferdinand’s", "Ferdinand de’ Medici."),
    (P238, 332, "crespi-satirical-picture", "cand-0885", "a satirical picture", "Index subentry for the picture of Don Carlo Silva."),
    (P238, 332, "silva-priest", "cand-2433", "the priest", "Don Carlo Silva, identified by p.237 note 2; no new priest identity is inferred."),
    (P238, 332, "silva-massacre", "cand-0882", "the Massacre of the Innocents", "Crespi index subentry for the painting discussed on p.237."),
    (P238, 332, "ferdinand-gift-recipient", "cand-1609", "Ferdinand", "Intended recipient of the proposed gift."),
    (P238, 332, "children-at-play", "cand-0874", "Children at Play", "Crespi index subentry for the genre scene."),
    (P238, 332, "women-washing", "cand-0887", "Women washing their Laundry at a Fountain", "Crespi index subentry for the genre scene."),
    (P238, 333, "crespi-florence-return", "cand-0871", "Crespi", "Giuseppe Maria Crespi."),
    (P238, 333, "florence-1709", "cand-3397", "Florence", "City Crespi returned to in 1709."),
    (P238, 334, "ferdinand-rooms", "cand-1609", "Ferdinand", "Provider of rooms at his villa."),
    (P238, 334, "pratolino-villa", "cand-7838", "Pratolino", "Place named for Ferdinand’s villa; the precise villa identity is not supplied."),
    (P238, 334, "grand-prince", "cand-1609", "the Grand Prince", "Ferdinand de’ Medici."),
    (P238, 334, "crespi-many-works", "cand-0871", "he", "Coreference to Crespi."),
    (P238, 334, "newborn-son", "cand-8043", "Crespi’s newborn son", "Named as Ferdinando; later identity and biography remain unknown."),
    (P238, 334, "son-name", "cand-8043", "Ferdinando", "Name given to Crespi’s newborn son."),
    (P238, 334, "son-honour-prince", "cand-1609", "his honour", "The name honours Ferdinand de’ Medici."),
    (P238, 334, "court-recognition", "cand-8010", "at court", "Ferdinand’s court as an institutional setting."),
    (P238, 334, "court-title", "cand-8044", "‘pittore attuale’", "Quoted court designation; English equivalent is not imposed."),
    (P238, 334, "crespi-title-holder", "cand-0871", "Crespi’s", "Giuseppe Maria Crespi."),
    (P238, 334, "crespi-responded", "cand-0871", "Crespi", "Giuseppe Maria Crespi."),
    (P238, 334, "fair-work", "cand-0878", "the Fair at Poggio a Caiano", "Crespi index subentry for the painting."),
    (P238, 334, "poggio-place", "cand-1966", "Poggio a Caiano", "Place embedded in the painting title."),
    (P238, 335, "ferdinand-courtiers", "cand-8010", "Ferdinand’s courtiers", "Members of the court are collectively named; no individuals are identified here."),
    (P238, 336, "bologna-november", "cand-3398", "Bologna", "Crespi’s reported location by the beginning of November."),
    (P238, 336, "possible-third-florence", "cand-3397", "Florence", "Haskell says a third visit is possible, not certain."),
    (P238, 336, "ferdinand-final-illness", "cand-1609", "Ferdinand’s", "Ferdinand de’ Medici; final illness is reported by Haskell."),
    (NOTES, 443, "archive-series-n1", "cand-8040", "Archivio Mediceo, Filza 5904", "Archival series cited in note 1."),
    (NOTES, 443, "letter-26", "cand-8030", "26", "First cited letter number; the note does not assign this number an individual date."),
    (NOTES, 443, "letter-38", "cand-8031", "38", "Second cited letter number."),
    (NOTES, 443, "letter-357", "cand-8032", "357", "Third cited letter number; p.239 note 3 also cites No.357."),
    (NOTES, 444, "ferdinand-ricci-corr", "cand-1609", "Ferdinand", "One party to correspondence with Ricci."),
    (NOTES, 444, "giovanni-ricci-note", "cand-2147", "Ricci", "Giovanni Ricci."),
    (NOTES, 444, "archive-series-n2a", "cand-8040", "Archivio Mediceo, Filza 5904", "Archival series for the cited correspondence."),
    (NOTES, 444, "letter-167", "cand-8033", "167", "First Ferdinand–Ricci correspondence locator."),
    (NOTES, 444, "letter-476", "cand-8034", "476", "Second Ferdinand–Ricci correspondence locator."),
    (NOTES, 444, "ferdinand-pepoli-corr", "cand-1609", "Ferdinand", "One party to correspondence with the Pepoli.", 1),
    (NOTES, 444, "pepoli-correspondence", "cand-7377", "the Pepoli", "Pepoli family; no individual correspondent is specified."),
    (NOTES, 444, "letter-174", "cand-8035", "174", "First Ferdinand–Pepoli correspondence locator."),
    (NOTES, 444, "letter-489", "cand-8036", "489", "Second Ferdinand–Pepoli correspondence locator."),
    (NOTES, 444, "letter-490", "cand-8037", "490", "Third Ferdinand–Pepoli correspondence locator."),
    (NOTES, 445, "ferdinand-letter-published", "cand-1609", "Ferdinand", "Sender named by Haskell; recipient is not specified in this note."),
    (NOTES, 445, "luigi-crespi", "cand-7716", "Luigi Crespi", "Bibliography-matched person named as publisher of the cited letter."),
    (NOTES, 445, "letter-475-published", "cand-8038", "the letter from Ferdinand", "The letter cited as published at Luigi Crespi p.203."),
    (NOTES, 445, "letter-475-original", "cand-8038", "No. 475", "Archival locator for the original draft of the same letter."),
    (NOTES, 445, "painter-family-note", "cand-0884", "The Painter's Family", "Crespi work named in the note."),
    (NOTES, 445, "uffizi-n3", "cand-7945", "the Uffizi", "Repository named for The Painter’s Family; exact institution/place boundary remains for S3."),
    (NOTES, 446, "cabinet-name", "cand-8048", "the Gabinetto del R. Intendente di Finanza di Pisa", "Named as the reported location; administrative versus physical boundary remains unresolved."),
    (NOTES, 446, "pisa-place", "cand-5628", "Pisa", "City within the cabinet’s name."),
    (NOTES, 446, "casini-author", "cand-8046", "Casini", "Surname in the note; full name resolved from the book bibliography at chp-21 L321."),
    (NOTES, 446, "casini-citation", "cand-8047", "Casini, pp. 42-50", "Citation to Giorgio Casini’s 1941 article; it was not independently read."),
    (NOTES, 447, "fair-at-uffizi", "cand-0878", "The picture", "Coreference to The Fair at Poggio a Caiano, marked by footnote 5 in the printed page."),
    (NOTES, 447, "uffizi-fair", "cand-7945", "the Uffizi", "Reported repository of the Fair; exact place/institution boundary remains for S3."),
    (NOTES, 447, "zanotti-author-n5", "cand-7114", "Zanotti", "Surname-only author citation; identity is deferred to S3."),
    (NOTES, 447, "zanotti-volume-n5", "cand-7115", "Zanotti, n", "OCR locator; the page image reads volume II of Storia dell’Accademia Clementina."),
    (NOTES, 447, "luigi-crespi-author-n5", "cand-7716", "L. Crespi", "Abbreviated author name for Luigi Crespi."),
    (NOTES, 447, "luigi-crespi-source-n5", "cand-7578", "L. Crespi, p. 211", "Existing abbreviated cited-source candidate; not equated with painter Giuseppe Maria Crespi."),
    (NOTES, 448, "archive-series-n6", "cand-8040", "Archivio Mediceo, Filza 5904", "Archival series cited in note 6."),
    (NOTES, 448, "letter-272", "cand-8039", "No. 272", "Letter dated 3 November 1709, cited as reporting Crespi’s return."),
    (NOTES, 448, "crespi-return-note6", "cand-0871", "his", "Coreference to Crespi in the report of his return to Bologna."),
    (NOTES, 448, "bologna-note6", "cand-3398", "Bologna", "Reported return location."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(segment_id: str, first: int, last: int) -> str:
    lines = source_lines if segment_id != BIB else bib_lines
    return "\n".join(lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", marker=None,
                   extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 238,
        "pdf_physical_page": 44, "claim": claim, "speaker": "Haskell",
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if marker is not None:
        qualifiers["footnote_marker"] = marker
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote(segment_id, first, last), "origin": "book",
            "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p238-mutual-patronage-connection", P238, 328, 328,
        "cand-0871", "cand-1609", "maintained_patronage_connection",
        "The continuation says Crespi was as anxious to maintain his connection with Ferdinand as Ferdinand was to use a painter whose gifts suited his temperament.",
        "This begins the sentence left open at p.237 L321; the comparative assessment is Haskell’s, not an independently established motive.",
        ["cand-0871", "cand-1609"], extras={"continuation_from_segment_id": P237}),
    make_statement("st-chp8-p238-return-to-bologna", P238, 328, 328,
        "cand-0871", "cand-3398", "returned_to_bologna_at_end_of_february_1708",
        "Haskell places Crespi’s return to Bologna at the end of February 1708.",
        "The phrase is approximate; note 6 on p.237 gives a separate latest-by date of 26 February, not a precise travel itinerary.",
        ["cand-0871", "cand-3398", "cand-1609"]),
    make_statement("st-chp8-p238-nativity-and-selfportrait-sent", P238, 328, 328,
        "cand-0871", "cand-0883", "sent_nativity_early_march_and_selfportrait_about_a_month_later",
        "After returning to Bologna, Crespi began sending pictures to Ferdinand: a Nativity arrived early in March, followed by a Selfportrait about a month later.",
        "The second work is indexed as Crespi’s Selfportrait; the source’s spacing at L328 is corrected only in the S2 transcription.",
        ["cand-0871", "cand-3398", "cand-1609", "cand-0883", "cand-0886"],
        extras={"relation_candidate": True, "ocr_corrections": [
            {"source_line": 328, "ocr": "Self portrait", "print": "Selfportrait", "basis": "CHP-8.pdf physical page 44"}]}),
    make_statement("st-chp8-p238-vassalage-promise", P238, 328, 328,
        "cand-0871", "cand-1609", "promised_remembrance_and_vasallaggio",
        "With the Selfportrait Crespi sent assurances of eternal remembrance of the Prince’s kindness and promises of his own ‘vasallaggio’.",
        "Retain the quoted Italian word and its source context; this is not treated as proof of a legal feudal status.",
        ["cand-0871", "cand-1609", "cand-8045"]),
    make_statement("st-chp8-p238-selfportrait-response-and-friendship", P238, 328, 329,
        "cand-1609", "cand-0886", "welcomed_selfportrait_and_friendship_was_sealed",
        "Ferdinand replied that he was delighted with Crespi’s Selfportrait, which showed the artist’s good humour; Haskell says the friendship between the two men was thereafter sealed.",
        "The evaluation of good humour and the characterization of friendship are Haskell’s account; no formal relationship is created here.",
        ["cand-1609", "cand-0871", "cand-0886"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-ricci-financed-travels", P238, 329, 329,
        "cand-2147", "cand-0871", "financed_crespis_early_travels_through_italy",
        "Haskell describes Giovanni Ricci as a wealthy marchand-amateur who financed Crespi’s early travels throughout Italy.",
        "The OCR’s missing line-break hyphen in marchand-amateur is corrected only in the S2 transcription.",
        ["cand-2147", "cand-0871", "cand-3461"], extras={"relation_candidate": True,
        "ocr_corrections": [{"source_line": 329, "ocr": "marchandamateur", "print": "marchand-amateur", "basis": "CHP-8.pdf physical page 44"}]}),
    make_statement("st-chp8-p238-ricci-acquired-work", P238, 329, 329,
        "cand-2147", "cand-0871", "acquired_very_large_proportion_of_crespis_work",
        "After financing Crespi’s early travels, Ricci subsequently acquired a very large proportion of his work.",
        "“A very large proportion” is retained as Haskell’s qualitative wording and is not converted to a count.",
        ["cand-2147", "cand-0871"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-pepoli-frescoes-and-reputation", P238, 329, 329,
        "cand-0871", "cand-8041", "painted_pepoli_palace_ceiling_frescoes_and_established_reputation",
        "About fifteen years before 1708 Crespi painted the great ceiling frescoes in the Pepoli palace; Haskell says these first established his reputation as a considerable and highly original master.",
        "The date is relative, not recalculated to a year; the frescoes remain a group whose individual scenes are unidentified.",
        ["cand-0871", "cand-7377", "cand-1872", "cand-8041"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-letters-prevented-fresco-destruction", P238, 329, 329,
        "cand-1609", "cand-8041", "urgent_letters_stopped_pepoli_plan_that_would_destroy_frescoes",
        "In 1708 the Pepoli were considering structural alterations to their palace that would involve destroying the frescoes; two urgent letters from Ferdinand stopped the plan.",
        "The body identifies two letters but not their archival numbers. Note 2 lists three Pepoli correspondence locators; their exact mapping to the pair remains unresolved.",
        ["cand-7377", "cand-1872", "cand-8041", "cand-1609", "cand-8042",
         "cand-8035", "cand-8036", "cand-8037"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-crespi-worked-for-ferdinand-through-1708", P238, 330, 330,
        "cand-0871", "cand-1609", "continued_working_for_ferdinand_throughout_1708",
        "Haskell says Crespi continued to work for Ferdinand throughout 1708.",
        "This is a patronage/work relation candidate, not yet a formal S6 edge.",
        ["cand-0871", "cand-1609"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-copy-st-william-sent", P238, 330, 330,
        "cand-0871", "cand-0875", "sent_copy_of_guercinos_st_william_in_december_1708",
        "In December 1708 Crespi sent Ferdinand a copy of Guercino’s St William of Aquitaine.",
        "The passage distinguishes Crespi’s copy from the Guercino source painting; it does not identify the copy’s present location.",
        ["cand-0871", "cand-1609", "cand-0875", "cand-1258", "cand-1269"],
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-painters-family-sent-and-evaluated", P238, 330, 331,
        "cand-0871", "cand-0884", "sent_painters_family_to_ferdinand",
        "Crespi also sent his small painting The Painter’s Family. Haskell calls it the most informal portrait group yet to appear in Italian art and a striking testimony to Crespi’s confidence in Ferdinand’s taste.",
        "The comparative art-historical assessment is attributed to Haskell; the painting is kept distinct from the copy of Guercino’s St William.",
        ["cand-0871", "cand-0884", "cand-1609"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-silva-satirical-picture", P238, 332, 332,
        "cand-0871", "cand-0885", "sent_satirical_picture_about_priest_who_defaulted",
        "During these months Crespi sent a satirical picture of the priest who had commissioned the Massacre of the Innocents as a gift for Ferdinand and then failed to keep the agreement.",
        "P.237 note 2 identifies the priest as Don Carlo Silva and reports the commission/default; this sentence is linked to that earlier statement without adding details.",
        ["cand-0871", "cand-0885", "cand-2433", "cand-0882", "cand-1609"],
        extras={"relation_candidate": True,
        "cross_reference_statement_ids": ["st-chp8-p237-note2-massacre-commission-and-default"]}),
    make_statement("st-chp8-p238-genre-scenes-and-subject-popularity", P238, 332, 332,
        "cand-0871", "cand-0874", "sent_two_named_genre_scenes_and_haskell_predicts_subject_popularity",
        "Crespi also sent two small genre scenes, Children at Play and Women washing their Laundry at a Fountain; Haskell describes this as an early treatment of a subject that would become immensely popular with eighteenth-century artists.",
        "The source does not separately identify the subject beyond these scenes; note 4’s demonstrative referent is left unresolved rather than assigned to one painting.",
        ["cand-0871", "cand-0874", "cand-0887"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-returned-to-florence-and-housed-at-pratolino", P238, 333, 334,
        "cand-0871", "cand-3397", "returned_with_family_and_stayed_in_ferdinands_pratolino_villa",
        "In 1709 Crespi returned to Florence with his family; Ferdinand gave him rooms in his villa at Pratolino, where Crespi stayed for several months.",
        "The family members are unnamed. Pratolino is recorded as named; no more specific villa identity is inferred.",
        ["cand-0871", "cand-3397", "cand-1609", "cand-7838"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-many-pictures-gifts-and-godfather", P238, 334, 334,
        "cand-0871", "cand-1609", "painted_many_pictures_and_received_gifts_and_godfatherhood",
        "During the visit Crespi painted a large number of pictures for Ferdinand, who collected his work with increasing enthusiasm, gave lavish presents, and consented to become godfather to Crespi’s newborn son Ferdinando.",
        "The son is kept distinct from the Grand Prince and is named only as the source does; this claim supports candidate relationships for patronage, gifts, and godparenthood.",
        ["cand-0871", "cand-1609", "cand-8043"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-son-named-in-ferdinands-honour", P238, 334, 334,
        "cand-0871", "cand-8043", "named_son_ferdinando_in_honour_of_ferdinand",
        "Crespi’s newborn son was called Ferdinando in Ferdinand’s honour.",
        "The name and relationship are recorded from Haskell; no later-life identity details are inferred.",
        ["cand-0871", "cand-8043", "cand-1609"]),
    make_statement("st-chp8-p238-pittore-attuale-recognition", P238, 334, 334,
        "cand-1609", "cand-0871", "officially_recognized_crespis_court_position_as_pittore_attuale",
        "Ferdinand gave official recognition to Crespi’s position at court by naming him his pittore attuale.",
        "The Italian designation is preserved; no present-day job title is imposed.",
        ["cand-1609", "cand-0871", "cand-8010", "cand-8044"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-genre-scenes-and-fair", P238, 334, 335,
        "cand-0871", "cand-0878", "painted_genre_scenes_and_fair_with_courtier_portraits",
        "Crespi responded with many genre scenes and what Haskell calls one of his masterpieces, The Fair at Poggio a Caiano, which included portraits of Ferdinand’s courtiers.",
        "The work title is linked to the Crespi index subentry; the footnote marker after Plate 37b is 5 in print, not 6 in OCR.",
        ["cand-0871", "cand-0878", "cand-1966", "cand-1609", "cand-8010"],
        extras={"relation_candidate": True,
        "ocr_corrections": [{"source_line": 335, "ocr": "Plate 37b).6", "print": "Plate 37b).5", "basis": "CHP-8.pdf physical page 44"}]}),
    make_statement("st-chp8-p238-return-bologna-and-possible-third-visit", P238, 336, 336,
        "cand-0871", "cand-3398", "back_in_bologna_by_early_november_1709_with_possible_third_florence_visit",
        "By the beginning of November Crespi was back in Bologna. Haskell says it is possible that he paid a third visit to Florence, while Ferdinand’s final illness was then upon him.",
        "The third Florence visit remains explicitly possible, not certain; the sentence continues at p.239 L339, so this statement does not close the passage.",
        ["cand-0871", "cand-3398", "cand-3397", "cand-1609"], extras={"relation_candidate": True,
        "continuation_to_segment_id": P239,
        "ocr_corrections": [{"source_line": 336, "ocr": "Bologna.8", "print": "Bologna.6", "basis": "CHP-8.pdf physical page 44"}]}),
    make_statement("st-chp8-p238-note1-march-april-letter-locators", NOTES, 443, 443,
        None, "cand-8040", "footnote_cites_three_archivio_mediceo_letters",
        "Note 1 cites letters of March and April 1708 in Archivio Mediceo, Filza 5904, Nos. 26, 38 and 357.",
        "The note is recorded as a source locator; no date or content is assigned individually to letters 26 and 38, and the documents were not independently consulted.",
        ["cand-8040", "cand-8030", "cand-8031", "cand-8032"],
        text_layer="footnote citation", marker=1,
        extras={"linked_body_statement_ids": ["st-chp8-p238-nativity-and-selfportrait-sent"]}),
    make_statement("st-chp8-p238-note2-ricci-pepoli-correspondence", NOTES, 444, 444,
        None, "cand-8040", "footnote_cites_ferdinand_ricci_and_pepoli_correspondence",
        "Note 2 locates correspondence between Ferdinand and Ricci at Filza 5904 Nos. 167 and 476, and letters between Ferdinand and the Pepoli at Nos. 174, 489 and 490.",
        "The underlying letters were not independently consulted. The three Pepoli locators are not equated with the two urgent letters mentioned in the body.",
        ["cand-8040", "cand-1609", "cand-2147", "cand-7377", "cand-8033", "cand-8034",
         "cand-8035", "cand-8036", "cand-8037"],
        text_layer="footnote citation", marker=2,
        extras={"linked_body_statement_ids": ["st-chp8-p238-ricci-financed-travels",
            "st-chp8-p238-ricci-acquired-work", "st-chp8-p238-letters-prevented-fresco-destruction"],
            "ocr_corrections": [{"source_line": 444, "ocr": "anf", "print": "and", "basis": "CHP-8.pdf physical page 44"}]}),
    make_statement("st-chp8-p238-note3-ferdinand-letter-draft", NOTES, 445, 445,
        "cand-1609", "cand-8038", "letter_published_by_luigi_crespi_and_original_draft_in_filza_5904_no_475",
        "Note 3 refers to a letter from Ferdinand published by Luigi Crespi at p.203 and says the original draft is in Archivio Mediceo, Filza 5904, No. 475.",
        "The cited published text and archival document were not independently consulted; the recipient and letter contents are not supplied here.",
        ["cand-1609", "cand-7716", "cand-8038", "cand-8040"],
        text_layer="footnote citation", marker=3,
        extras={"linked_body_statement_ids": ["st-chp8-p238-painters-family-sent-and-evaluated"]}),
    make_statement("st-chp8-p238-note3-painters-family-uffizi", NOTES, 445, 445,
        None, "cand-0884", "footnote_reports_painters_family_at_uffizi_no_5382",
        "Note 3 says The Painter’s Family is in the Uffizi, No. 5382.",
        "This is Haskell’s report and has not been independently checked against the repository catalogue.",
        ["cand-0884", "cand-7945"], text_layer="footnote report", marker=3,
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-note4-pictures-at-pisa-cabinet", NOTES, 446, 446,
        None, "cand-8048", "footnote_reports_pictures_at_pisa_cabinet",
        "Note 4 says the pictures referred to as “These pictures” are—or were in 1941—in the Gabinetto del R. Intendente di Finanza di Pisa, and cites Casini, pp.42-50.",
        "Haskell’s wording leaves both the time status and the antecedent scope unresolved: it may refer to the two genre scenes or also the immediately preceding satirical picture. No individual work-to-location edge is asserted; the article was not independently read.",
        ["cand-8048", "cand-5628", "cand-0874", "cand-0887", "cand-0885",
         "cand-8046", "cand-8047"],
        text_layer="footnote report", marker=4, extras={"relation_candidate": True}),
    make_statement("st-chp8-p238-note5-fair-at-uffizi", NOTES, 447, 447,
        None, "cand-0878", "footnote_reports_fair_at_uffizi",
        "Note 5 says The Fair at Poggio a Caiano is now in the Uffizi and cites Zanotti, volume II, p.55 and L. Crespi, p.211.",
        "The repository claim is Haskell’s report; the cited pages and present-day location were not independently checked.",
        ["cand-0878", "cand-1966", "cand-7945", "cand-7114", "cand-7115", "cand-7716", "cand-7578"],
        text_layer="footnote report", marker=5, extras={"relation_candidate": True,
        "ocr_corrections": [{"source_line": 447, "ocr": "Zanotti, n", "print": "Zanotti, II", "basis": "CHP-8.pdf physical page 44"}]}),
    make_statement("st-chp8-p238-note6-return-letter", NOTES, 448, 448,
        "cand-8039", "cand-0871", "letter_of_3_november_1709_reports_crespis_return_to_bologna",
        "Note 6 cites a letter of 3 November 1709 in Filza 5904 No. 272 as reporting Crespi’s return to Bologna.",
        "The letter date is a citation date, not necessarily the date of travel; the original was not independently consulted.",
        ["cand-8039", "cand-8040", "cand-0871", "cand-3398"],
        text_layer="footnote citation", marker=6,
        extras={"linked_body_statement_ids": ["st-chp8-p238-return-bologna-and-possible-third-visit"]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")

for row in coverage_rows:
    if row["segment_id"] == P237:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L312-325",
                    "note": "p.237 body and page notes 1-5 reviewed against physical page 43. Its final clause is completed by p.238 L328; notes 2 and 3 and their continuations are recorded through L442."})
    elif row["segment_id"] == P238:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L328-336",
                    "note": "p.238 body reviewed against physical page 44; its final sentence continues at p.239 L339. Printed note markers at L335-L336 are 5 and 6; the continuation is not yet closed."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-448",
                    "note": "Consolidated notes reviewed in source order through p.238 notes 1-6 at L443-448 and linked to body statements. Remaining L449-461 is queued for later pages."})

preview = {
    "mode": "dry-run", "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage_updates": {P237: "complete", P238: "partial through L328-336", NOTES: "partial through L373-448"},
    "print_corrections": [
        "L328 Self portrait -> Selfportrait",
        "L329 marchandamateur -> marchand-amateur",
        "L335 Plate 37b marker 6 -> printed 5",
        "L336 Bologna marker 8 -> printed 6",
        "L444 anf -> and",
    ],
    "preserved_uncertainties": [
        "p.237 final clause closes at p.238 L328; p.238 final sentence remains open to p.239 L339",
        "two urgent letters in the body are not mapped to the three Pepoli letter locators in note 2",
        "note 4 leaves the referent of These pictures and their present-versus-1941 status unresolved",
        "Casini is linked to the bibliography entry at chp-21 L321; that bibliography segment remains queued for full semantic processing",
        "all cited archival documents and publication pages remain source locators, not independently consulted evidence",
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
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", statement_rows + new_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, coverage_rows)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=True, indent=2))
