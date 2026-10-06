"""Controlled S2 migration for Chapter 8 printed page 239 and its notes.

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
P238 = "chp-8:08_CHP-8_sec_ii:l327-336"
P239 = "chp-8:08_CHP-8_sec_ii:l338-348"
P240 = "chp-8:08_CHP-8_sec_ii:l350-359"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGETS = {P238, P239, P240, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p239-20261001"
PAGE_SCAN = PROCESS / "p239_page_review.png"
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
    raise SystemExit("page 239 PDF or review image is missing")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
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
    P238: ("reviewed", "partial", "L328-336"),
    P239: ("queued", "pending", ""),
    P240: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L373-448"),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")

new_candidates = [
    ("cand-8049", "Crespi's picture shown in the Medici collections and misattributed to Tintoretto", "work", 341,
     "A particular but otherwise unidentified picture that Crespi said he had painted himself, although it was attributed to Tintoretto; title, date, and present location are not given."),
    ("cand-8050", "Crespi letter reporting his picture attributed to Tintoretto", "archive", 341,
     "Unidentified letter in which Crespi reportedly says he was shown the painting in the Medici collections; no date, recipient, or archival locator is supplied."),
    ("cand-8051", "Ferdinand's gallery where Crespi studied Venetian painters (location unspecified)", "place", 340,
     "Gallery referred to as Ferdinand's; no building or location is specified, and it is not merged with other Medici galleries."),
    ("cand-8052", "Medici collections as viewing context for a painting (exact site unspecified)", "",
     341, "The collections in which a picture was reportedly shown to Crespi; exact repository, organization, and physical site are unresolved."),
    ("cand-8053", "Soprintendenza alle Gallerie di Firenze", "institution", 451,
     "Institution named by Haskell as keeper of the cited inventory; its current name and institutional continuity are not independently checked."),
    ("cand-8054", "Inventario di Quadri, che si ritrovano negl'appartamenti del gran palazzo de Pitti di S.A.R. (1716 Inventory)", "archive", 451,
     "Inventory Haskell dates between 1716 and 1723 and calls the 1716 Inventory for convenience; original not independently consulted."),
    ("cand-8055", "Venetian pictures among Ferdinand's amassed pictures", "work", 347,
     "Unspecified group in Haskell's description of Ferdinand's picture collection; the precise scope of the Venetian emphasis is not limited to the Pitti count. The sentence continues on p.240; individual works and locations are not inferred."),
    ("cand-8056", "Ferdinand's recorded opinions and letters concerning Crespi's humour", "archive", 342,
     "Unspecified documentary group cited by Haskell for Ferdinand's view of Crespi as a humourist; no individual letter is identified."),
    ("cand-8057", "S.P.F. (mark on pictures in Ferdinand's own collection)", "term", 451,
     "Inventory mark reported by Haskell for pictures from Ferdinand's own collection; the initials are not expanded."),
    ("cand-8058", "R. Longhi (author of an introduction to the 1948 exhibition catalogue)", "person", 348,
     "Abbreviated name in Haskell's note 4. It may refer to the existing Roberto Longhi candidate, but identity is deferred to S3."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
if max(int(cid.split("-")[1]) for cid in candidate_ids) != 8048:
    raise SystemExit("candidate ID sequence changed since p.238; inspect before allocating IDs")
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 439 else P239
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
new_mentions = []


def mention(segment_id, line_no, suffix, candidate_id, surface, note="", occurrence=0):
    mention_id = f"m-chp8-p239-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    line = source_lines[line_no - 1]
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
    (P239, 339, "crespi-last-artist", "cand-0871", "Crespi", "Giuseppe Maria Crespi."),
    (P239, 339, "ferdinand-last-artist", "cand-1609", "him", "Coreference to Ferdinand."),
    (P239, 340, "ferdinand-collector", "cand-1609", "Ferdinand", "Ferdinand de' Medici."),
    (P239, 340, "crespi-collector", "cand-0871", "Crespi", "Giuseppe Maria Crespi."),
    (P239, 340, "ferdinand-gallery", "cand-8051", "his gallery", "Ferdinand's gallery; location and identity are unspecified."),
    (P239, 340, "artist-studies", "cand-0871", "the artist", "Coreference to Crespi."),
    (P239, 341, "crespi-letter", "cand-8050", "a letter", "Unidentified letter attributed to Crespi by Haskell's report."),
    (P239, 341, "medici-collections", "cand-8052", "the Medici collections", "Viewing context; not equated with Ferdinand's gallery or Pitti Palace."),
    (P239, 341, "tintoretto-picture", "cand-8049", "a picture attributed to Tintoretto", "A work misattributed in the reported account; Haskell says Crespi painted it."),
    (P239, 341, "tintoretto-painter", "cand-2627", "Tintoretto", "Painter to whom the picture was attributed."),
    (P239, 341, "crespi-picture-painter", "cand-0871", "himself", "Coreference to Crespi as the reported painter of the picture."),
    (P239, 341, "ferdinand-support", "cand-1609", "Ferdinand", "Patron whose support is discussed."),
    (P239, 341, "history-picture", "cand-1612", "the conventional ‘history picture’", "The indexed term in Haskell's discussion of Crespi's break with conventional history painting."),
    (P239, 341, "crespi-history-picture", "cand-0871", "him", "Coreference to Crespi."),
    (P239, 341, "crespi-painting", "cand-0871", "Crespi", "Painter whose contemporaries approached his work with humour."),
    (P239, 341, "crespi-unconventional-painting", "cand-0871", "his unconventional painting", "Coreference to Crespi's work."),
    (P239, 341, "crespi-art", "cand-0871", "his art", "Coreference to Crespi's artistic production."),
    (P239, 341, "ferdinand-misconceptions", "cand-1609", "Ferdinand himself", "Ferdinand de' Medici."),
    (P239, 341, "crespi-misconceptions", "cand-0871", "Crespi’s art", "Artistic production by Giuseppe Maria Crespi."),
    (P239, 342, "ferdinand-opinions", "cand-1609", "His", "Coreference to Ferdinand."),
    (P239, 342, "ferdinand-records", "cand-8056", "his letters", "Unspecified recorded opinions and letters cited by Haskell."),
    (P239, 342, "ferdinand-humourist-view", "cand-1609", "he", "Coreference to Ferdinand."),
    (P239, 342, "crespi-humourist", "cand-0871", "him", "Coreference to Crespi, whom Ferdinand reportedly saw primarily as a humourist."),
    (P239, 342, "crespi-bawdy-subjects", "cand-0871", "the artist", "Giuseppe Maria Crespi."),
    (P239, 342, "ferdinand-bawdy-art", "cand-1609", "him", "Coreference to Ferdinand as the intended recipient of Crespi's paintings.", 1),
    (P239, 342, "ferdinand-appreciation", "cand-1609", "Ferdinand’s", "Ferdinand de' Medici."),
    (P239, 342, "crespi-temperament", "cand-0871", "his temperament", "Coreference to Crespi."),
    (P239, 343, "ferdinand-patronage", "cand-1609", "Ferdinand", "Ferdinand de' Medici."),
    (P239, 344, "crespi-middle-class", "cand-0871", "Crespi", "Giuseppe Maria Crespi."),
    (P239, 344, "chardin-comparison", "cand-0649", "Chardin", "Jean-Baptiste-Siméon Chardin; named as a qualified artistic comparison."),
    (P239, 344, "ferdinand-removed", "cand-1609", "Ferdinand", "Ferdinand de' Medici."),
    (P239, 344, "modern-prince", "cand-1609", "prince", "Coreference to Ferdinand, described by Haskell as the most modern prince of the age in Italy."),
    (P239, 344, "italy-modern-prince", "cand-3461", "Italy", "Geographic scope in Haskell's characterization."),
    (P239, 344, "crespi-retired", "cand-0871", "Crespi", "Giuseppe Maria Crespi.", 1),
    (P239, 344, "bologna-backwater", "cand-3398", "Bologna", "City described by Haskell as Crespi's provincial backwater after Ferdinand's death."),
    (P239, 345, "ferdinand-pictures", "cand-1609", "Ferdinand", "Collector and owner in Haskell's account."),
    (P239, 345, "pitti-apartments", "cand-1949", "the Pitti", "Pitti Palace; the apartments are not separately identified."),
    (P239, 346, "pitti-palace", "cand-1949", "Palace", "Continuation of Pitti Palace from the preceding line."),
    (P239, 346, "ferdinand-country-houses", "cand-1609", "he", "Coreference to Ferdinand, who moved among the country houses."),
    (P239, 347, "private-collection", "cand-1609", "his private collection", "The collection is attributed to Ferdinand; no separate collection object is identified."),
    (P239, 347, "family-members", "cand-5179", "members of the family", "Medici family members preceding Ferdinand; individual members are unspecified."),
    (P239, 347, "venetian-picture-group", "cand-8055", "Venetian pictures", "Collective group in Ferdinand's collection; the sentence continues on p.240."),
    (P239, 348, "longhi", "cand-8058", "R. Longhi", "Person named by abbreviated initials; identity against Roberto Longhi is deferred to S3."),
    (P239, 348, "crespi-art-note4", "cand-0871", "Crespi’s art", "Artistic production by Giuseppe Maria Crespi."),
    (P239, 348, "exhibition-catalogue", "cand-8022", "the 1948 exhibition catalogue", "Likely the Mostra Celebrativa catalogue cited at p.237 note 2; the identity is not independently verified."),
    (NOTES, 449, "luigi-crespi-n1", "cand-7716", "L. Crespi", "Abbreviated author reference."),
    (NOTES, 449, "luigi-crespi-work-n1", "cand-7578", "L. Crespi, p. 211", "Existing source candidate; not equated with painter Giuseppe Maria Crespi."),
    (NOTES, 449, "florence-n1a", "cand-3397", "Florence", "Place in the reported duration of Crespi's stay."),
    (NOTES, 449, "crespi-two-years", "cand-0871", "he", "Coreference to Crespi in L. Crespi's reported claim."),
    (NOTES, 449, "florence-n1b", "cand-3397", "there", "Coreference to Florence."),
    (NOTES, 449, "zanotti-n1-author", "cand-7114", "Zanotti", "Surname-only author citation; identity remains for S3."),
    (NOTES, 449, "zanotti-n1-book", "cand-7115", "Zanotti, II", "Locator to volume II of Storia dell’Accademia Clementina."),
    (NOTES, 449, "florence-n1c", "cand-3397", "there", "The place Crespi is said possibly to have visited several times.", 1),
    (NOTES, 449, "p237-note-crossref", "cand-8015", "p. 237, note 1", "Cross-reference to the p.237 letter locator; it does not add independent evidence."),
    (NOTES, 450, "zanotti-n3-author", "cand-7114", "Zanotti", "Surname-only author citation."),
    (NOTES, 450, "zanotti-n3-book", "cand-7115", "Zanotti, II", "Locator to volume II."),
    (NOTES, 450, "ferdinand-letter-no357", "cand-1609", "Ferdinand", "Sender of the letter dated 28 April 1708."),
    (NOTES, 450, "archivio-no357", "cand-8040", "Archivio Medicco, Filza 5904", "OCR surface form; print reads Archivio Mediceo, Filza 5904."),
    (NOTES, 450, "letter-no357", "cand-8032", "No. 3 57", "OCR form of the letter locator; printed form is No.357."),
    (NOTES, 451, "inventory-title", "cand-8054", "Inventario di Quadri, che si ritrovano negl'appartamenti del gran palazzo de Pitti di S.A.R.", "Inventory title transcribed from the page; no catalogue copy was consulted."),
    (NOTES, 451, "inventory-holding-institution", "cand-8053", "Soprintendenza alle Gallerie di Firenze", "Institution named as holding the inventory."),
    (NOTES, 451, "inventory-pitti", "cand-1949", "gran palazzo de Pitti", "Pitti Palace named in the inventory title."),
    (NOTES, 451, "ferdinand-inventory", "cand-1609", "Ferdinand’s", "Ferdinand de' Medici."),
    (NOTES, 451, "inventory-convenience-name", "cand-8054", "1716 Inventory", "Haskell's convenience label for an inventory dated between 1716 and 1723."),
    (NOTES, 451, "ferdinand-collection-mark", "cand-1609", "Ferdinand’s own collection", "His pictures within the inventory, not the entire Pitti holdings."),
    (NOTES, 451, "spf-mark", "cand-8057", "S.P.F.", "Inventory marking reported for pictures from Ferdinand's own collection."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", marker=None,
                   extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 239,
        "pdf_physical_page": 45, "claim": claim, "speaker": "Haskell",
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
    make_statement("st-chp8-p239-last-known-artist", P239, 339, 339,
        "cand-0871", "cand-1609", "last_artist_known_to_have_worked_for_ferdinand",
        "Haskell says Crespi is the last artist known to have worked for Ferdinand.",
        "This closes p.238's sentence about Ferdinand's patronage; it does not say Crespi was the last artist to work for Ferdinand in fact.",
        ["cand-0871", "cand-1609"], extras={"continuation_from_segment_id": P238}),
    make_statement("st-chp8-p239-close-partnership", P239, 340, 340,
        "cand-0871", "cand-1609", "both_benefited_from_close_partnership",
        "Haskell says both painter and patron benefited greatly from their close partnership.",
        "This is Haskell's retrospective assessment.",
        ["cand-0871", "cand-1609"]),
    make_statement("st-chp8-p239-ferdinand-sensitive-collector", P239, 340, 340,
        "cand-1609", "cand-0871", "most_cultivated_and_sensitive_collector_crespi_had_known",
        "Haskell describes Ferdinand as the most cultivated and sensitive collector Crespi had yet—or ever was to—encounter.",
        "The parenthetical alternative and superlative remain Haskell's assessment.",
        ["cand-1609", "cand-0871"]),
    make_statement("st-chp8-p239-crespi-studies-venetian-painters", P239, 340, 341,
        "cand-0871", "cand-8051", "studied_venetian_painters_in_ferdinands_gallery",
        "Haskell says Crespi was able to study at length the Venetian painters he and Ferdinand both loved in Ferdinand's gallery.",
        "The passage does not name those painters or identify the gallery's physical site.",
        ["cand-0871", "cand-1609", "cand-8051"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p239-crespi-claimed-tintoretto-picture", P239, 341, 341,
        "cand-0871", "cand-8049", "letter_reports_crespi_painted_picture_attributed_to_tintoretto",
        "Haskell says a letter by Crespi records that he was shown a picture in the Medici collections attributed to Tintoretto, but which had actually been painted by Crespi.",
        "The letter is not dated or located, and the picture is unidentified. The Medici collections are not equated with Ferdinand's gallery or the Pitti.",
        ["cand-0871", "cand-8049", "cand-8050", "cand-8052", "cand-2627"],
        extras={"relation_candidate": True, "quoted_speaker": "Giuseppe Maria Crespi, as reported by Haskell"}),
    make_statement("st-chp8-p239-ferdinand-supported-history-picture-break", P239, 341, 341,
        "cand-1609", "cand-0871", "supported_crespis_attempt_to_break_from_history_picture",
        "Haskell calls Ferdinand's support fully as important to Crespi's attempt to break away from the conventional history picture.",
        "This is an art-historical relation candidate; the term and its period boundaries are not independently defined here.",
        ["cand-1609", "cand-0871", "cand-1612"], extras={"relation_candidate": True,
        "ocr_corrections": [{"source_line": 341, "ocr": "die support", "print": "the support", "basis": "CHP-8.pdf physical page 45"}]}),
    make_statement("st-chp8-p239-contemporaries-misread-crespi-humour", P239, 341, 341,
        "cand-0871", None, "contemporaries_humour_reflected_bewilderment_at_unconventional_painting",
        "Haskell says the humour with which Crespi's contemporaries approached him partly reflected their bewilderment at his unconventional painting and coloured their appreciation of his art.",
        "The passage reports Haskell's explanation of critical reception, not the views of any named contemporary.",
        ["cand-0871"], extras={"ocr_corrections": [{"source_line": 341, "ocr": "Crcspi", "print": "Crespi", "basis": "CHP-8.pdf physical page 45"}]}),
    make_statement("st-chp8-p239-crespi-humour-melancholy-sympathy", P239, 341, 341,
        "cand-0871", None, "humour_tinged_with_melancholy_and_poetic_sympathy",
        "Haskell characterizes Crespi's humour as often tinged with melancholy and counteracted by deep poetic sympathy for the people he painted.",
        "This is Haskell's interpretive characterization.",
        ["cand-0871"]),
    make_statement("st-chp8-p239-ferdinand-view-as-humourist", P239, 341, 342,
        "cand-1609", "cand-0871", "letters_suggest_ferdinand_saw_crespi_primarily_as_humourist",
        "Haskell says it is difficult to judge how much Ferdinand shared common misconceptions about Crespi's art, but Ferdinand's recorded opinions and especially his letters suggest that he too saw Crespi primarily as a humourist.",
        "The attribution is an inference from unspecified recorded opinions and letters, not an independently checked letter reading.",
        ["cand-1609", "cand-0871", "cand-8056"], extras={"relation_candidate": True,
        "ocr_corrections": [{"source_line": 342, "ocr": "ef his temperament", "print": "of his temperament", "basis": "CHP-8.pdf physical page 45"}]}),
    make_statement("st-chp8-p239-restraint-and-ferdinand-appreciation", P239, 342, 342,
        "cand-0871", "cand-1609", "restraint_suggests_crespi_relied_on_ferdinands_appreciation",
        "Haskell says the restraint with which Crespi painted subjects open to gross or bawdy treatment makes clear that he must have relied on Ferdinand appreciating a side of his temperament ignored by many.",
        "The phrase must have relied is Haskell's inference. Plate 36b is an illustration cross-reference; its subject is not identified here.",
        ["cand-0871", "cand-1609"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p239-ferdinand-distinctive-patronage", P239, 343, 343,
        "cand-1609", None, "unique_patronage_position_shown_by_exceptional_sympathetic_art",
        "Haskell argues Ferdinand's unique place in Italian patronage is shown by the exceptional sober and sympathetic treatment of the poor and simple in Italian art.",
        "This is Haskell's historical argument; it does not identify the pictured people or a separate patronage organization.",
        ["cand-1609"]),
    make_statement("st-chp8-p239-chardin-counterfactual", P239, 344, 344,
        "cand-0871", "cand-0649", "might_have_become_chardin_with_middle_class_backing",
        "Haskell speculates that with support from a cultivated middle class Crespi might have become the Chardin to whom he was sometimes close.",
        "The comparison is explicitly counterfactual and qualified; it does not claim influence or identity.",
        ["cand-0871", "cand-0649"]),
    make_statement("st-chp8-p239-ferdinand-removal-and-bologna", P239, 344, 344,
        "cand-1609", "cand-0871", "removal_of_princely_patron_led_crespi_back_to_bologna",
        "Haskell says after Ferdinand's removal from the scene, and in a period when only princes could be influential patrons, Crespi retired to Bologna, described as a provincial backwater.",
        "This is Haskell's causal interpretation, not an independently tested account of Crespi's motives.",
        ["cand-1609", "cand-0871", "cand-3398", "cand-3461"]),
    make_statement("st-chp8-p239-longhi-on-restricting-effect", P239, 348, 348,
        "cand-5505", "cand-0871", "longhi-noted-restricting-effect-on-crespis-art",
        "Note 4 says R. Longhi pointed out the restricting effect on Crespi's art in his introduction to the 1948 exhibition catalogue.",
        "Haskell's shorthand likely refers to the Crespi exhibition catalogue cited on p.237, but the exact catalogue relation was not independently verified.",
        ["cand-8058", "cand-0871", "cand-8022"], text_layer="footnote report", marker=4,
        extras={"linked_body_statement_ids": ["st-chp8-p239-ferdinand-removal-and-bologna"]}),
    make_statement("st-chp8-p239-pictures-distributed-among-medici-residences", P239, 345, 346,
        "cand-1609", "cand-1949", "pictures_distributed_in_pitti_apartments_and_country_houses",
        "Haskell says Ferdinand's amassed pictures were distributed among his apartments in the Pitti Palace and the various country houses through which he moved during the year.",
        "The individual apartments and country houses are not named; no other residence is inferred.",
        ["cand-1609", "cand-1949"]),
    make_statement("st-chp8-p239-three-hundred-pitti-pictures", P239, 347, 347,
        "cand-1609", "cand-1949", "about_300_pictures_from_ferdinands_private_collection_in_pitti",
        "By the end of Ferdinand's life the collection was very considerable; in the Pitti alone were 300 pictures from his private collection, apart from many assembled by earlier family members.",
        "The count applies to Ferdinand's own collection in the Pitti and excludes earlier family holdings; the sentence continues with a description of its Venetian emphasis on p.240.",
        ["cand-1609", "cand-1949", "cand-5179"], extras={"continuation_to_segment_id": P240,
        "ocr_corrections": [{"source_line": 347, "ocr": "collection. quite apart", "print": "collection, quite apart", "basis": "CHP-8.pdf physical page 45"}]}),
    make_statement("st-chp8-p239-venetian-emphasis", P239, 347, 347,
        "cand-1609", "cand-8055", "collection-emphasized-venetian-pictures",
        "Haskell begins to describe the strong emphasis on Venetian pictures in Ferdinand's collection.",
        "The sentence is unfinished at p.239 L347 and continues on p.240; no total or individual work list is inferred yet.",
        ["cand-1609", "cand-8055"], extras={"continuation_to_segment_id": P240}),
    make_statement("st-chp8-p239-note1-luigi-crespi-stay", NOTES, 449, 449,
        "cand-7716", "cand-0871", "luigi_crespi_reports_two_year_florence_stay",
        "Note 1 says L. Crespi, p.211, reports that Crespi was in Florence for two years.",
        "This is Haskell's report of Luigi Crespi's claim; the cited page was not independently consulted.",
        ["cand-7716", "cand-7578", "cand-0871", "cand-3397"],
        text_layer="footnote report", marker=1,
        extras={"linked_body_statement_ids": ["st-chp8-p239-returned-to-florence-and-housed-at-pratolino"],
        "ocr_corrections": [
            {"source_line": 449, "ocr": "during - 1709", "print": "during 1709", "basis": "CHP-8.pdf physical page 45"},
            {"source_line": 449, "ocr": "was-there", "print": "was there", "basis": "CHP-8.pdf physical page 45"},
            {"source_line": 449, "ocr": "p. $4", "print": "p. 54", "basis": "CHP-8.pdf physical page 45"}]}),
    make_statement("st-chp8-p239-note1-haskell-eight-month-maximum", NOTES, 449, 449,
        None, "cand-0871", "haskell-says-during-1709-florence-stay-at-most-eight-months",
        "Note 1 says Crespi was in Florence during 1709 for eight months at most.",
        "This is Haskell's counterclaim to L. Crespi's reported two-year stay; the phrase it has been shown is retained, though its demonstration is not supplied here.",
        ["cand-0871", "cand-3397"], text_layer="footnote report", marker=1,
        extras={"linked_body_statement_ids": ["st-chp8-p239-returned-to-florence-and-housed-at-pratolino"]}),
    make_statement("st-chp8-p239-note1-zanotti-multiple-visits", NOTES, 449, 449,
        "cand-7114", "cand-0871", "zanotti-implies-several-florence-visits",
        "Haskell says Zanotti, volume II, p.54, implies Crespi went to Florence several times.",
        "This is Haskell's interpretation of the cited page, not an independently checked reading.",
        ["cand-7114", "cand-7115", "cand-0871", "cand-3397"],
        text_layer="footnote report", marker=1,
        extras={"linked_body_statement_ids": ["st-chp8-p239-returned-to-florence-and-housed-at-pratolino"]}),
    make_statement("st-chp8-p239-note2-cross-reference", NOTES, 449, 449,
        None, "cand-8030", "footnote_cross_reference_to_p237_note1",
        "Note 2 directs the reader to p.237 note 1.",
        "This is an internal citation only; it adds no new claim or independent evidence.",
        ["cand-8015"], text_layer="footnote cross-reference", marker=2,
        extras={"cross_reference_statement_ids": ["st-chp8-p237-note1-letter-citation"]}),
    make_statement("st-chp8-p239-note3-zanotti-and-letter-357", NOTES, 450, 450,
        "cand-1609", "cand-8032", "footnote-cites-zanotti-and-ferdinand-letter-28-april-1708",
        "Note 3 cites Zanotti, volume II, pp.52 and 54, and a letter from Ferdinand dated 28 April 1708 in Archivio Mediceo, Filza 5904, No.357.",
        "The cited pages and archival letter were not independently consulted; the letter is reidentified through the No.357 candidate created at p.238.",
        ["cand-7114", "cand-7115", "cand-1609", "cand-8040", "cand-8032"],
        text_layer="footnote citation", marker=3,
        extras={"ocr_corrections": [
            {"source_line": 450, "ocr": "Archivio Medicco", "print": "Archivio Mediceo", "basis": "CHP-8.pdf physical page 45"},
            {"source_line": 450, "ocr": "No. 3 57", "print": "No. 357", "basis": "CHP-8.pdf physical page 45"}]}),
    make_statement("st-chp8-p239-note5-inventory-description", NOTES, 451, 451,
        None, "cand-8054", "footnote-describes-pitti-apartment-inventory",
        "Note 5 names the Inventario di Quadri for the apartments in the grand Pitti palace, says it is kept at the Soprintendenza alle Gallerie di Firenze, dates it between 1716 and 1723, and says Haskell uses 1716 Inventory as a convenience label.",
        "This is Haskell's source description; neither the inventory nor the holding institution was independently consulted. The date range is not collapsed to 1716.",
        ["cand-8054", "cand-8053", "cand-1949", "cand-1609"],
        text_layer="footnote source description", marker=5,
        extras={"linked_body_statement_ids": ["st-chp8-p239-three-hundred-pitti-pictures"],
        "ocr_corrections": [{"source_line": 451, "ocr": "6 Inventario", "print": "5 Inventario", "basis": "CHP-8.pdf physical page 45"}]}),
    make_statement("st-chp8-p239-note5-spf-mark", NOTES, 451, 451,
        "cand-8054", "cand-8057", "inventory-marks-ferdinands-own-pictures-spf",
        "Note 5 says pictures from Ferdinand's own collection are marked S.P.F. in the inventory.",
        "The initials are preserved without expansion; the note does not say that every Pitti picture carries the mark.",
        ["cand-8054", "cand-1609", "cand-8057"],
        text_layer="footnote source description", marker=5,
        extras={"linked_body_statement_ids": ["st-chp8-p239-three-hundred-pitti-pictures"]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")

for row in coverage_rows:
    if row["segment_id"] == P238:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L328-336",
                    "note": "p.238 body reviewed against physical page 44; its final sentence is closed by p.239 L339. Notes 1-6 are migrated at L443-448."})
    elif row["segment_id"] == P239:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L339-348",
                    "note": "p.239 body and embedded note 4 reviewed against physical page 45. The final body phrase at L347 ends with 'Venetian pictures,' and continues on p.240 L351; notes 1-3 and 5 are in the consolidated note segment through L451."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-451",
                    "note": "Consolidated notes reviewed through p.239 notes 1-3 and 5 at L449-451; p.239 note 4 is at L348 and cross-linked. L452 onward remains unmapped to printed pages and queued for later review."})

preview = {
    "mode": "dry-run", "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage_updates": {P238: "complete", P239: "partial through L339-348", NOTES: "partial through L373-451"},
    "print_corrections": [
        "L341 die support -> the support",
        "L341 Crcspi -> Crespi",
        "L342 ef -> of",
        "L347 private collection. quite apart -> private collection, quite apart",
        "L449 remove OCR dashes and read p. $4 as p.54",
        "L450 Medicco -> Mediceo; No. 3 57 -> No.357",
        "L451 note marker 6 -> printed 5",
    ],
    "preserved_uncertainties": [
        "p.239's phrase about Venetian pictures continues at p.240 L351",
        "Ferdinand's gallery and the Medici collections are not assumed to be the same place",
        "the Crespi letter, Ferdinand's letters, picture, and inventory were not independently consulted",
        "Luigi Crespi's two-year duration and Haskell's eight-month maximum for 1709 are retained as distinct reports",
        "the 1716 Inventory is dated between 1716 and 1723, as Haskell states",
        "notes segment L452 onward is not assigned to p.239 without page evidence",
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
