#!/usr/bin/env python3
"""Controlled S2 migration for Appendix 5 continuation and Appendix 6, p.394."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "19_CHP-19Appendix.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-19Appendix.pdf"
EXPECTED_HASHES = {
    SOURCE: "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    PDF: "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb",
}
P393 = "chp-19:19_CHP-19Appendix:l140-155"
P394 = "chp-19:19_CHP-19Appendix:l157-183"
P395 = "chp-19:19_CHP-19Appendix:l185-208"
CH10_BODY = "chp-10:10_CHP-10_sec_ii:l258-267"
CH10_NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
BACKUP_SUFFIX = ".bak-s2-chp19-p394-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


for path, expected in EXPECTED_HASHES.items():
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)} ({actual})")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = [
    json.loads(line)
    for line in statement_path.read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
coverage_fields, coverage = read_csv(coverage_path)
segments = [
    json.loads(line)
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
statement_by_id = {row["statement_id"]: row for row in statements}

if any(seg not in segment_by_id or seg not in coverage_by_id for seg in (P393, P394, P395)):
    raise SystemExit("missing S0 or S2 row for p.393–395 sequence")
if (coverage_by_id[P393]["disposition"], coverage_by_id[P393]["migration_status"]) != (
    "reviewed", "partial"
):
    raise SystemExit(f"p.393 must be reviewed/partial before closure: {coverage_by_id[P393]}")
if (coverage_by_id[P394]["disposition"], coverage_by_id[P394]["migration_status"]) != (
    "queued", "pending"
):
    raise SystemExit(f"p.394 should be queued/pending before migration: {coverage_by_id[P394]}")
if (coverage_by_id[P395]["disposition"], coverage_by_id[P395]["migration_status"]) != (
    "queued", "pending"
):
    raise SystemExit(f"p.395 should remain queued/pending: {coverage_by_id[P395]}")

segment = segment_by_id[P394]
if segment["sha256"] != "efb8708a6b775c8c5cadd9363c5b45b0c646c0ec688228228459b9d8192f6dd9":
    raise SystemExit("registered p.394 S0 hash changed")
if segment["asset_sha256"] != EXPECTED_HASHES[SOURCE]:
    raise SystemExit("p.394 source asset hash is inconsistent")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text394 = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
if hashlib.sha256(text394.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit("p.394 S0 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment["line_start"], segment["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1


def quote(first_line, last_line):
    return "\n".join(source_lines[first_line - 1 : last_line])


new_candidate_specs = [
    {
        "candidate_id": "cand-10830",
        "canonical_name": "Joseph Smith's sale of a large quantity of books to Giacomo Caraboli and Domenico Pompeati",
        "suggested_type": "event",
        "source_line": 158,
        "detail": "Haskell says Smith had sold a large quantity of books to Caraboli and Pompeati some years before the last months of his life. The passage supplies no exact date; it reports a bitter dispute over the contract but does not establish its outcome.",
    },
    {
        "candidate_id": "cand-10831",
        "canonical_name": "Atti del Notaio Ludovico Gabrieli, Busta 7570, pp. 1215 and 1278 (contract citation locator)",
        "suggested_type": "archive",
        "source_line": 159,
        "detail": "Specific locator cited by Haskell for a contract dispute involving Smith's sale of books to Giacomo Caraboli and Domenico Pompeati. The notarial volume and cited pages were not independently consulted.",
    },
    {
        "candidate_id": "cand-10832",
        "canonical_name": "Catalogo di Libri Raccolti dal fu Signor Giuseppe Smith e pulitamente legati (Venice, 1771; Correr I. 5911)",
        "suggested_type": "archive",
        "source_line": 160,
        "detail": "Posthumous octavo catalogue described by Haskell as 136 pages and cited at Correr I.5911. The catalogue was not independently consulted; title spelling is retained from OCR except for page-image corrections recorded in the statement.",
    },
    {
        "candidate_id": "cand-10833",
        "canonical_name": "Bibliotheca Smithiana, pars altera (catalogue of the remaining Joseph Smith library, advertised 1773)",
        "suggested_type": "archive",
        "source_line": 161,
        "detail": "Posthumous catalogue/advertisement for the remaining part of Joseph Smith's library. The wording says it would be sold cheaply for ready money 'this Day' in 1773; no completed sale is established and the catalogue was not independently consulted.",
    },
    {
        "candidate_id": "cand-10834",
        "canonical_name": "C. Veneziano (unexpanded painter named in Andrea Memmo's notes)",
        "suggested_type": "person",
        "source_line": 169,
        "detail": "The transcribed note calls this person a famous living Venetian painter and gives only 'C.' The p.330 note proposes Canaletto as a qualified hypothesis, with a chronology tension; identity remains open for S3.",
    },
    {
        "candidate_id": "cand-10835",
        "canonical_name": "Academy of Painting at Naples (existence queried in Memmo's notes)",
        "suggested_type": "institution",
        "source_line": 175,
        "detail": "Source-local candidate in a question asking whether Naples has an Academy of Painting. The wording is not treated as proof that such an academy existed or as an identified institution.",
    },
    {
        "candidate_id": "cand-10836",
        "canonical_name": "Academy of Paris referenced in Memmo's notes (identity unresolved)",
        "suggested_type": "institution",
        "source_line": 181,
        "detail": "The notes ask about the privileges of academicians in Paris and mention conferences and lessons at the Academy of Paris. No exact institutional name or identity is supplied here; defer alignment to S3.",
    },
    {
        "candidate_id": "cand-10837",
        "canonical_name": "Terra-ferma (regional designation in Memmo's notes)",
        "suggested_type": "place",
        "source_line": 180,
        "detail": "Regional term in a question about publicly maintained academies and their costs. Its geographical scope is not standardized by this passage.",
    },
    {
        "candidate_id": "cand-10838",
        "canonical_name": "Architects as a professional group in Memmo's taxation queries",
        "suggested_type": "term",
        "source_line": 173,
        "detail": "Professional group whose tax burden Memmo proposes to investigate; the notes do not identify individual architects or establish a tax rule.",
    },
    {
        "candidate_id": "cand-10839",
        "canonical_name": "Painters as a professional group in Memmo's taxation queries",
        "suggested_type": "term",
        "source_line": 169,
        "detail": "Professional group discussed in the preparatory note, including a query about taxation in several cities. General remarks and questions are not treated as verified institutional rules.",
    },
    {
        "candidate_id": "cand-10840",
        "canonical_name": "Women painters as a professional group in Memmo's taxation queries",
        "suggested_type": "term",
        "source_line": 177,
        "detail": "The note asks whether women painters such as Rosalba pay the tax; it does not establish the answer or identify a general rule.",
    },
    {
        "candidate_id": "cand-10841",
        "canonical_name": "Publicly maintained academies in Terra-ferma (group queried by Memmo)",
        "suggested_type": "term",
        "source_line": 180,
        "detail": "Unspecified group about which the note asks for a count, names, and costs. No individual academy is identified by this question.",
    },
    {
        "candidate_id": "cand-10842",
        "canonical_name": "Foreign professors considered for associated academician status in Memmo's notes",
        "suggested_type": "term",
        "source_line": 178,
        "detail": "A proposed selection topic in the preparatory notes; no foreign professor is named and no appointment is reported.",
    },
    {
        "candidate_id": "cand-10843",
        "canonical_name": "Archivio di Stato, Venice, Inquisitoriato alle Arti (fonds/series locator for Memmo's sheet)",
        "suggested_type": "archive",
        "source_line": 165,
        "detail": "Archival fonds/series name in Haskell's locator for Andrea Memmo's preparatory query sheet, cited as Busta 15, fascicolo 6. Keep the archival series distinct from the Inquisitori alle Arti body; neither the series nor the sheet was independently consulted.",
    },
]
existing_keys = {
    (
        (row.get("canonical_name") or "").strip().casefold(),
        (row.get("suggested_type") or "").strip().casefold(),
    )
    for row in candidates
}
for spec in new_candidate_specs:
    cid = spec["candidate_id"]
    name = spec["canonical_name"]
    kind = spec["suggested_type"]
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in existing_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": spec["detail"],
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P394}#L{spec['source_line']}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

sheet_candidate = candidate_by_id.get("cand-9857")
if not sheet_candidate or sheet_candidate.get("status") != "open":
    raise SystemExit("expected open Memmo sheet candidate cand-9857")
if "no repository or shelfmark is given here" not in sheet_candidate.get("detail", ""):
    raise SystemExit("cand-9857 detail changed; inspect before updating archival locator")
sheet_candidate["detail"] = (
    "A sheet among Memmo's papers containing brief queries written while preparing a report; Haskell says it is "
    "published in full in Appendix 6. P.394 gives Archivio di Stato, Venice—Inquisitoriato alle Arti, Busta 15, "
    "fascicolo 6. The manuscript was not independently consulted; the notes' date remains Haskell's estimate."
)

mention_specs = [
    ("cand-9177", "library", 158, 158, "The Smith library described as catalogued in the 1755 Bibliotheca Smithiana; collection type remains unresolved.", 0),
    ("cand-9274", "Bibliotheca Smithiana", 158, 158, "The 1755 catalogue/inventory as described by Haskell; not independently consulted.", 0),
    ("cand-1844", "Pasquali", 158, 158, "Publisher named in Haskell's account of the 1755 catalogue.", 0),
    ("cand-1141", "George III", 158, 158, "Recipient of the library sale as reported by Haskell.", 0),
    ("cand-9171", "his palace", 158, 158, "Smith's palace in the account of books recorded at his death in 1770.", 0),
    ("cand-9177", "books", 158, 158, "Books recorded in Smith's palace at his death; Haskell infers continued purchases from the recent publications.", 0),
    ("cand-9177", "buying books", 158, 158, "Haskell's inference from recent publications, not a directly cited purchase record.", 0),
    ("cand-10830", "una grossa molla di Ebri", 158, 158, "Original OCR span; the page image reads 'libri' for OCR 'Ebri'. The sale date is unspecified.", 0),
    ("cand-0540", "Giacomo Caraboli", 159, 159, "Buyer named in Haskell's report of the book sale.", 0),
    ("cand-1972", "Domenico Pompeati", 159, 159, "Buyer named in Haskell's report of the book sale.", 0),
    ("cand-10831", "contract", 159, 159, "The contract in dispute, cited to a notarial record but not independently consulted.", 0),
    ("cand-10172", "Archivio di Stato, Venice", 159, 159, "Repository named in Haskell's archival citation; not independently consulted.", 0),
    ("cand-9485", "Atti del Notaio Ludovico\nGabrieE", 159, 160, "Notarial series named in the source. The printed surname is Gabrieli; the OCR error is recorded in the statement.", 0),
    ("cand-1096", "Ludovico", 159, 159, "Notary named in the citation; the surname continues on the next OCR line.", 0),
    ("cand-1096", "GabrieE", 160, 160, "Raw OCR surname; the page image reads Gabrieli.", 0),
    ("cand-10831", "Busta 7570—pp. 1215 and 1278", 160, 160, "Specific locator cited for the contract dispute; record not consulted.", 0),
    ("cand-10832", "Catalogo di Libri Raccolti dal Ju Signor Giuseppe Smith e pulitamenti legati", 160, 160, "Title as OCR; page image corrections are recorded with the catalogue statement.", 0),
    ("cand-2447", "Giuseppe Smith", 160, 160, "Joseph Smith named in the posthumous catalogue title.", 0),
    ("cand-8262", "Correr", 161, 161, "Repository named with shelfmark I.5911; catalogue copy not consulted.", 0),
    ("cand-10832", "I. 5911", 161, 161, "Correr locator associated with the 1771 catalogue.", 0),
    ("cand-10833", "Bibliotheca Smithiana, pars altera", 161, 161, "Title of the second posthumous catalogue/advertisement.", 0),
    ("cand-2447", "Joseph Smith", 161, 161, "Person named in the 1773 catalogue title.", 0),
    ("cand-2719", "Venice", 162, 162, "City in Smith's consular title within the 1773 catalogue advertisement.", 0),
    ("cand-10833", "1773", 162, 162, "Date stated at the end of the catalogue advertisement; no completed sale is established.", 0),
    ("cand-1642", "Andrea Memmo", 164, 164, "Author of the notes according to Haskell's Appendix 6 title.", 0),
    ("cand-9857", "Notes on the Status of Painters", 164, 164, "Appendix heading for the transcribed Memmo sheet; the original manuscript was not consulted.", 0),
    ("cand-10172", "Archivio di Stato, Venice", 165, 165, "Repository identified for the Memmo document; manuscript not consulted.", 0),
    ("cand-10843", "Inquisitoriato alle Arti", 166, 166, "Archival-series wording; keep the fonds/series distinct from the Inquisitori alle Arti body.", 0),
    ("cand-9857", "Busta 15, fascicolo 6", 166, 166, "Shelfmark supplied for the preparatory query sheet; archival original not consulted.", 0),
    ("cand-2644", "Gianfranco Torcellan", 166, 166, "Person Haskell credits with directing him to the document.", 0),
    ("cand-1642", "Memmo", 166, 166, "Andrea Memmo named as Inquisitore alle Arti from 1772 to 1775.", 0),
    ("cand-9851", "Inquisitore alle Arti", 166, 166, "Office/body in which Haskell says Memmo served; institutional scope remains for S3.", 0),
    ("cand-9857", "Memorie e Ricerche", 167, 167, "Heading in the transcribed sheet; its exact relation to a document title is not independently checked.", 0),
    ("cand-9867", "EberaE", 168, 168, "Raw OCR within 'arti liberali'; page image reads 'liberali'.", 0),
    ("cand-10839", "Pittori", 168, 168, "Painters named as a professional group in the preparatory note.", 0),
    ("cand-10834", "C. Veneziano", 169, 169, "Only an initial and the description 'Venetian' are supplied; do not expand to Canaletto in S2.", 0),
    ("cand-10834", "C.", 170, 170, "Initial repeated in Memmo's tax-exemption query; identity remains for S3.", 0),
    ("cand-9853", "Maestri di Musica", 171, 171, "Musicians considered as a professional group; source note asserts they are not taxed, which is not independently verified.", 0),
    ("cand-9852", "tansati", 171, 171, "Tax status named in the note; retain the note's assertion separately from externally verified law.", 0),
    ("cand-9854", "IntagEatori", 171, 171, "Raw OCR; page image reads Intagliatori (engravers).", 0),
    ("cand-10838", "Architetti", 173, 173, "Architects named as a professional group whose tax status Memmo proposes to investigate.", 0),
    ("cand-10839", "Pittori", 174, 174, "Painters' taxation is queried for the named cities.", 0),
    ("cand-4653", "Parigi", 174, 174, "Paris named as a comparison city in the painter-tax question.", 0),
    ("cand-4490", "Roma", 174, 174, "Rome named as a comparison city in the painter-tax question.", 0),
    ("cand-1041", "Firenze", 174, 174, "Florence named as a comparison city in the painter-tax question.", 0),
    ("cand-3398", "Bologna", 174, 174, "Bologna named as a comparison city in the painter-tax question.", 0),
    ("cand-3534", "NapoE", 175, 175, "Raw OCR; page image reads Napoli.", 0),
    ("cand-10835", "Accademia di Pittura", 175, 175, "Institution whose existence in Naples is posed as a question, not asserted as fact.", 0),
    ("cand-1838", "Accademia di Parma", 176, 176, "The note asks about the new institution of the Academy at Parma; no policy or outcome is asserted.", 0),
    ("cand-10840", "Pittrice", 177, 177, "Women painters named as a professional category; tax status is queried.", 0),
    ("cand-0581", "Rosalba", 177, 177, "First-name form only in the source; mapping to the indexed Rosalba Carriera candidate remains for S3.", 0),
    ("cand-0005", "Accademia", 178, 178, "Academy from which the notes ask how foreign associate professors should be selected; exact referent is not named here.", 0),
    ("cand-10842", "Professori\nForastieri", 178, 179, "Foreign professors considered for associated academician status; the OCR line break is retained; no individual is named or appointment established.", 0),
    ("cand-10842", "Accademici associati", 179, 179, "Associated academicians as a proposed status in the selection question.", 0),
    ("cand-10841", "l’Accademie mantenute dal PubbEco", 180, 180, "Raw OCR phrase; page image reads publicly maintained academies. The question gives no individual names.", 0),
    ("cand-10837", "Terra-ferma", 180, 180, "Regional designation in the query about publicly maintained academies.", 0),
    ("cand-10836", "Accademici dell’Arti del Disegno a Parigi", 181, 181, "Academicians and privileges associated with the Paris Academy as queried; exact institution remains unresolved.", 0),
    ("cand-4653", "Parigi", 181, 181, "Paris in the phrase about privileges of academicians; nested within the academy-related mention.", 0),
    ("cand-10836", "Accademia di Parigi", 182, 182, "Academy of Paris invoked as a model for conferences and lessons; no precise institutional identity is given.", 0),
    ("cand-0005", "nostra Accademia", 183, 183, "The note's 'our Academy'; p.330 links Memmo's queries to the Venetian Academy, but this local wording is not expanded by itself.", 0),
]

new_mentions = []
mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first_line, last_line, note, occurrence) in enumerate(mention_specs, start=1):
    mid = f"m-chp19-p394-{ordinal:03d}"
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    candidate = candidate_by_id.get(cid)
    if not candidate or candidate.get("status") != "open":
        raise SystemExit(f"mention targets missing or closed candidate: {cid}")
    lower = line_offset[first_line]
    upper = line_offset[last_line] + len(source_lines[last_line - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text394.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(
                f"surface not found in p.394 lines {first_line}-{last_line}: {surface!r}"
            )
        cursor = found + 1
    end = found + len(surface)
    if text394[found:end] != surface:
        raise SystemExit(f"span mismatch for {mid}")
    new_mentions.append({
        "mention_id": mid,
        "segment_id": P394,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(found),
        "end_char": str(end),
        "note": note,
    })
    mention_ids.add(mid)

intervals = sorted(
    (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
    for row in [*mentions, *new_mentions]
    if row["segment_id"] == P394
)
for index, left in enumerate(intervals):
    for right in intervals[index + 1 :]:
        if right[0] >= left[1]:
            break
        exact_duplicate = left[:2] == right[:2]
        strictly_nested = (
            (left[0] <= right[0] and right[1] <= left[1])
            or (right[0] <= left[0] and left[1] <= right[1])
        )
        if exact_duplicate or not strictly_nested:
            raise SystemExit(
                f"duplicate or crossing p.394 mention spans: {left[2]} and {right[2]}"
            )


def statement(statement_id, first, last, subject, object_, predicate, claim, speaker, text_layer,
              qualification, candidate_ids, date=None, relation=False, **extra):
    qualifiers = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": 394,
        "pdf_physical_page": 9,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
        "relation_candidate": relation,
        "cited_material_not_independently_consulted": True,
    }
    if date:
        qualifiers["date"] = date
    qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": P394,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote(first, last),
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
        "origin": "book",
    }


new_statements = [
    statement(
        "st-chp19-p394-smith-books-history-closure", 158, 158, "cand-2447", "cand-9177",
        "haskell_compared_smiths_book_history_with_picture_history_and_inferred_late_purchases",
        "Haskell completes the p.393 comparison: although the library catalogued in the 1755 Bibliotheca Smithiana was sold to George III in 1762, many books were recorded in Smith's palace at his death in 1770. He infers from recent publications that Smith continued buying books until the end of his life.",
        "Haskell", "authorial narrative and inference",
        "The 1770 inventory and 1755 catalogue are reported by Haskell and were not independently consulted. Continued buying is Haskell's inference from the publication dates, not a directly cited purchase record.",
        ["cand-2447", "cand-9177", "cand-9274", "cand-1844", "cand-1141", "cand-9171"],
        date="1755 / 1762 / 1770",
        cross_reference_segments=[P393],
        cross_reference_statement_ids=["st-chp19-p393-smith-books-history-open"],
        continuation_of_statement_id="st-chp19-p393-smith-books-history-open",
        ocr_corrections=[
            {"source_line": 158, "ocr": "Sòme", "print": "Some", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 158, "ocr": "very7", "print": "very", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 158, "ocr": "until-the", "print": "until the", "basis": "CHP-19Appendix.pdf physical page 9."},
        ],
    ),
    statement(
        "st-chp19-p394-smith-book-sale-caraboli-contract", 158, 160, "cand-2447", "cand-10830",
        "haskell_reported_smiths_earlier_book_sale_and_late_contract_dispute",
        "Haskell says Smith had sold a large quantity of books to Giacomo Caraboli and Domenico Pompeati some years earlier, and that the last months of Smith's life were spent in a bitter dispute about the contract; he cites the Gabrieli notarial records.",
        "Haskell", "authorial report of a cited archival dispute",
        "The phrase 'some years earlier' gives no exact date. The source documents and cited pages were not consulted; the dispute does not establish the contract's outcome.",
        ["cand-2447", "cand-9177", "cand-10830", "cand-0540", "cand-1972", "cand-10172", "cand-9485", "cand-1096", "cand-10831"],
        relation=True,
        cross_reference_segments=["chp-10:10_CHP-10_intro:l491-634"],
        ocr_corrections=[
            {"source_line": 158, "ocr": "Ebri", "print": "libri", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 159, "ocr": "Efe", "print": "life", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 160, "ocr": "GabrieE", "print": "Gabrieli", "basis": "CHP-19Appendix.pdf physical page 9."},
        ],
    ),
    statement(
        "st-chp19-p394-smith-catalogue-1771", 160, 161, "cand-2447", "cand-10832",
        "posthumous_1771_catalogue_of_smiths_books_was_published",
        "Haskell reports a posthumous Venice catalogue of Smith's books, dated 1771, described as an octavo of 136 pages and cited at Correr I.5911.",
        "Haskell", "authorial bibliographical report",
        "The catalogue was not independently consulted. The title and physical description are reported as printed; the Correr locator is not a claim that the copy was examined.",
        ["cand-2447", "cand-10832", "cand-8262"], date="1771",
        ocr_corrections=[
            {"source_line": 160, "ocr": "pubEshed", "print": "published", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 160, "ocr": "SmitE’s", "print": "Smith’s", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 160, "ocr": "Ju", "print": "fu", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 160, "ocr": "pulitamenti", "print": "pulitamente", "basis": "CHP-19Appendix.pdf physical page 9, enlarged title crop."},
            {"source_line": 161, "ocr": "ofJoseph", "print": "of Joseph", "basis": "CHP-19Appendix.pdf physical page 9."},
        ],
    ),
    statement(
        "st-chp19-p394-smith-catalogue-1773", 161, 162, "cand-2447", "cand-10833",
        "posthumous_1773_catalogue_advertised_remaining_smith_library_for_sale",
        "Haskell cites a second posthumous catalogue for the remaining part of Smith's library, describing it as an advertisement for a cheap cash sale in 1773.",
        "Haskell", "authorial bibliographical report and quoted advertisement",
        "The catalogue was not independently consulted. 'Which will be sold ... this Day' is advertisement wording and does not prove that a sale was completed.",
        ["cand-2447", "cand-10833", "cand-2719"], date="1773",
    ),
    statement(
        "st-chp19-p394-memmo-sheet-source-and-date", 164, 166, "cand-1642", "cand-9857",
        "haskell_identified_memmos_query_sheet_and_gave_an_estimated_date",
        "Haskell identifies the document behind Appendix 6 as a sheet in the Archivio di Stato, Venice, Inquisitoriato alle Arti, Busta 15, fascicolo 6; he credits Gianfranco Torcellan with directing him to it. Haskell says Memmo held the Inquisitore alle Arti office from 1772 to 1775 and estimates that the notes were written two or three years before he assumed office.",
        "Haskell", "authorial source note and date estimate",
        "The archival sheet was not independently consulted. The date two or three years before 1772 is Haskell's estimate, not a securely established date. The office/body and archival series are not collapsed into one identity.",
        ["cand-1642", "cand-9857", "cand-10172", "cand-10843", "cand-9851", "cand-2644", "cand-2719"],
        date="1772–1775; notes probably two or three years earlier", relation=True,
        cross_reference_segments=[CH10_BODY, CH10_NOTES],
        cross_reference_statement_ids=["st-chp10-p330-memmo-inquisitori-and-sheet", "st-chp10-p330-n01-memmo-sheet-appendix"],
    ),
    statement(
        "st-chp19-p394-memmo-liberal-arts-query", 168, 168, "cand-1642", "cand-9867",
        "memmo_planned_to_note_liberal_arts_practitioners_should_be_freed_from_dues",
        "The transcribed preparatory note says a memorandum should mention the need to free practitioners of the liberal arts from dues and the supposedly strange genius of painters.",
        "Andrea Memmo as transcribed by Haskell", "transcribed preparatory query",
        "This is a proposed topic in a working note, not evidence that any exemption was granted or that the generalization about painters was tested. The archival sheet was not consulted.",
        ["cand-1642", "cand-9857", "cand-9867", "cand-9852", "cand-10839"],
        relation=True, cross_reference_segments=[CH10_BODY],
        cross_reference_statement_ids=["st-chp10-p330-memmo-dues-query"],
        ocr_corrections=[
            {"source_line": 168, "ocr": "EberaE", "print": "liberali", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 168, "ocr": "scogliere", "print": "sciogliere", "basis": "CHP-19Appendix.pdf physical page 9."},
        ],
    ),
    statement(
        "st-chp19-p394-memmo-c-veneziano-exemption-query", 169, 170, "cand-1642", "cand-10834",
        "memmo_named_c_veneziano_as_an_example_and_queried_his_tax_exemption_claim",
        "The note gives the example of a famous living Venetian painter identified only as C. and asks why C. claims exemption from the tax.",
        "Andrea Memmo as transcribed by Haskell", "transcribed example and query",
        "The name is not expanded. Chapter 12 p.330 note 2 offers Canaletto as a qualified hypothesis but preserves a chronology tension; S2 keeps that identity unresolved. The query does not prove that C. received an exemption.",
        ["cand-1642", "cand-9857", "cand-10834", "cand-10839", "cand-9852", "cand-0498"],
        relation=True, cross_reference_segments=[CH10_BODY, CH10_NOTES],
        cross_reference_statement_ids=["st-chp10-p330-memmo-dues-query", "st-chp10-p330-n02-canaletto-hypothesis"],
        ocr_corrections=[
            {"source_line": 170, "ocr": "prettenda", "print": "pretenda", "basis": "CHP-19Appendix.pdf physical page 9."}
        ],
    ),
    statement(
        "st-chp19-p394-memmo-professional-tax-comparisons", 171, 174, "cand-1642", None,
        "memmo_recorded_a_claim_about_musicians_and_engravers_and_queried_other_professions_and_cities",
        "The note asks whether music teachers are taxed, then states that they are not and that engravers are not either; it asks about architects' taxes and whether painters are taxed in Paris, Rome, Florence, and Bologna.",
        "Andrea Memmo as transcribed by Haskell", "transcribed working queries with one assertion",
        "The statement that music teachers and engravers are not taxed belongs to the note and is not independently verified. The other items are questions, not findings about tax law in those cities.",
        ["cand-1642", "cand-9857", "cand-9853", "cand-9854", "cand-10838", "cand-10839", "cand-9852", "cand-4653", "cand-4490", "cand-1041", "cand-3398"],
        relation=True, cross_reference_segments=[CH10_BODY],
        cross_reference_statement_ids=["st-chp10-p330-reform-comparisons-and-professions"],
        ocr_corrections=[
            {"source_line": 171, "ocr": "IntagEatori", "print": "Intagliatori", "basis": "CHP-19Appendix.pdf physical page 9."}
        ],
    ),
    statement(
        "st-chp19-p394-memmo-academies-and-associates", 175, 179, "cand-1642", None,
        "memmo_queried_naples_and_parma_academies_womens_tax_status_and_foreign_associate_selection",
        "The note asks whether Naples has an Academy of Painting, refers to the new institution of the Academy of Parma, asks whether women painters such as Rosalba pay the tax, and considers how the Academy might select the most talented foreign professors as associated academicians.",
        "Andrea Memmo as transcribed by Haskell", "transcribed working queries",
        "These are questions and a proposed selection topic; they do not establish the Naples academy's existence, the tax status of women painters, or any appointment. 'Rosalba' remains in the source's first-name form.",
        ["cand-1642", "cand-9857", "cand-10835", "cand-1838", "cand-10840", "cand-0581", "cand-0005", "cand-10842", "cand-9852"],
        relation=True, cross_reference_segments=[CH10_BODY],
        cross_reference_statement_ids=["st-chp10-p330-reform-comparisons-and-professions"],
        ocr_corrections=[
            {"source_line": 175, "ocr": "NapoE", "print": "Napoli", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 178, "ocr": "migEore", "print": "migliore", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 178, "ocr": "scegEersi", "print": "scegliersi", "basis": "CHP-19Appendix.pdf physical page 9."},
        ],
    ),
    statement(
        "st-chp19-p394-memmo-terra-ferma-academies", 180, 180, "cand-1642", "cand-10841",
        "memmo_queried_the_number_names_and_costs_of_publicly_maintained_terra_ferma_academies",
        "The note asks how many publicly maintained academies exist in Terra-ferma, which they are, and how much they cost.",
        "Andrea Memmo as transcribed by Haskell", "transcribed working query",
        "This is an unanswered query; the passage names no individual academy and gives no count or cost. Terra-ferma is retained as the source's regional term.",
        ["cand-1642", "cand-9857", "cand-10841", "cand-10837"], relation=True,
        ocr_corrections=[
            {"source_line": 180, "ocr": "PubbEco", "print": "Pubblico", "basis": "CHP-19Appendix.pdf physical page 9."}
        ],
    ),
    statement(
        "st-chp19-p394-memmo-paris-academy-privileges-and-teaching", 181, 182, "cand-1642", "cand-10836",
        "memmo_queried_paris_academy_privileges_and_whether_other_academies_hold_conferences_and_lessons",
        "The note asks about the privileges, exemptions, prerogatives, and pre-eminences of academicians of the arts of design in Paris, and whether other academies, as at Paris, hold conferences and lessons.",
        "Andrea Memmo as transcribed by Haskell", "transcribed working queries",
        "The passage records topics for investigation, not a verified account of Parisian privileges or the practices of other academies. The exact Paris institution is not identified.",
        ["cand-1642", "cand-9857", "cand-10836", "cand-4653"], relation=True,
        ocr_corrections=[
            {"source_line": 181, "ocr": "quaE", "print": "quali", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 182, "ocr": "deHe", "print": "delle", "basis": "CHP-19Appendix.pdf physical page 9."},
        ],
    ),
    statement(
        "st-chp19-p394-memmo-academy-emblem-name-query", 183, 183, "cand-1642", "cand-0005",
        "memmo_queried_the_emblem_and_name_of_our_academy_for_confirmation_or_improvement",
        "The note asks what the emblem and name of 'our Academy' are, so that both can be confirmed or improved.",
        "Andrea Memmo as transcribed by Haskell", "transcribed working query",
        "No emblem or name change is reported. The internal p.330 account identifies the topic with the Venetian Academy, but the appendix's local phrase 'our Academy' is preserved and the alignment remains for S3.",
        ["cand-1642", "cand-9857", "cand-0005"], relation=True,
        cross_reference_segments=[CH10_BODY],
        cross_reference_statement_ids=["st-chp10-p330-memmo-vasari-academy-queries"],
        ocr_corrections=[
            {"source_line": 183, "ocr": "’1 nome", "print": "’l nome", "basis": "CHP-19Appendix.pdf physical page 9."},
            {"source_line": 183, "ocr": "migEorare", "print": "migliorare", "basis": "CHP-19Appendix.pdf physical page 9."},
        ],
    ),
]

existing_statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    sid = row["statement_id"]
    if sid in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {sid}")
    existing_statement_ids.add(sid)
    if row["original_quote"] not in text394:
        raise SystemExit(f"statement quote not contained in p.394 segment: {sid}")
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement {sid} references unavailable candidate {cid}")
    for ref_id in row["qualifiers"].get("cross_reference_statement_ids", []):
        if ref_id not in statement_by_id:
            raise SystemExit(f"statement {sid} references missing statement {ref_id}")

closing_statement_id = "st-chp19-p393-smith-books-history-open"
if closing_statement_id not in statement_by_id:
    raise SystemExit(f"missing open p.393 statement: {closing_statement_id}")
closing_statement = statement_by_id[closing_statement_id]
if closing_statement.get("qualifiers", {}).get("continuation_status") != "open":
    raise SystemExit("p.393 Smith-books statement is not open for closure")
if closing_statement.get("qualifiers", {}).get("continuation_to_segment_id") != P394:
    raise SystemExit("p.393 Smith-books continuation does not point to p.394")
closing_statement["qualifiers"]["continuation_status"] = "closed"
closing_statement["qualifiers"]["continuation_closed_by_segment_id"] = P394
closing_statement["qualifiers"]["continuation_line_start"] = 158
closing_statement["qualifiers"]["continuation_line_end"] = 158
closing_statement["qualifiers"]["continuation_statement_id"] = "st-chp19-p394-smith-books-history-closure"
closing_statement["qualifiers"]["cross_reference_statement_ids"] = [
    "st-chp19-p394-smith-books-history-closure"
]
closing_statement["qualifiers"]["qualification"] = (
    "The sentence continues and is completed on p.394 L158. Haskell compares the history of Smith's books with "
    "that of his pictures; the continuation and its qualified inference are recorded in the linked p.394 statement."
)

statements.extend(new_statements)
mentions.extend(new_mentions)

coverage_by_id[P393]["disposition"] = "reviewed"
coverage_by_id[P393]["migration_status"] = "complete"
coverage_by_id[P393]["source_line_ranges"] = "L141-155"
coverage_by_id[P393]["note"] = (
    "Printed p.393 (PDF physical page 8) read against the page image. Closes Smith's 9 April 1768 letter begun on "
    "p.392; records Haskell's qualified reports about Zais, Smith's collection, the 1776 Christie's lists, and the "
    "1789 anonymous sale. Page-image corrections include Moschini, '(f)', £20,000, 'lists', and Marieschi; the cited "
    "source and sale lists were not independently consulted. The p.155 sentence about Smith's books is closed by "
    "the p.394 continuation statement."
)
coverage_by_id[P394]["disposition"] = "reviewed"
coverage_by_id[P394]["migration_status"] = "complete"
coverage_by_id[P394]["source_line_ranges"] = "L158-183"
coverage_by_id[P394]["note"] = (
    "Printed p.394 (PDF physical page 9) read against the page image. Closes the p.393 sentence on Smith's books, "
    "records Haskell's report about the Caraboli/Pompeati book sale, cited notarial dispute, and the 1771/1773 "
    "posthumous catalogues, then transcribes Andrea Memmo's preparatory queries. The queries are not treated as "
    "resolved facts; C. Veneziano, the Naples/Paris academy references, and the Academy referred to as 'ours' retain "
    "their source-level uncertainty. OCR corrections are recorded on statements; cited records were not independently "
    "consulted."
)

files_to_backup = [candidate_path, mention_path, statement_path, coverage_path]
if args.apply:
    for path in files_to_backup:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print("applied p.394 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(new_candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.393: reviewed/partial -> reviewed/complete; p.394: queued/pending -> reviewed/complete")
    print("closed the p.393 books-history continuation; p.395 remains queued/pending")
    print("preserved the question and uncertainty status of Memmo's transcribed notes")
