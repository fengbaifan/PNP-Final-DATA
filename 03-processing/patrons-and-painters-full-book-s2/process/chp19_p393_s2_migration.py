#!/usr/bin/env python3
"""Controlled S2 migration for Appendix 5, printed p.393."""

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
P392 = "chp-19:19_CHP-19Appendix:l126-138"
P393 = "chp-19:19_CHP-19Appendix:l140-155"
P394 = "chp-19:19_CHP-19Appendix:l157-183"
P10_SALE_NOTE = "chp-10:10_CHP-10_intro:l491-634"
BACKUP_SUFFIX = ".bak-s2-chp19-p393-20261004"

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
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit(f"registered input changed: {path.relative_to(ROOT)}")

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

if any(seg not in segment_by_id or seg not in coverage_by_id for seg in (P392, P393, P394)):
    raise SystemExit("missing S0 or S2 row for p.392–394 sequence")
if (coverage_by_id[P392]["disposition"], coverage_by_id[P392]["migration_status"]) != (
    "reviewed", "partial"
):
    raise SystemExit(f"p.392 must be reviewed/partial before closing its letter: {coverage_by_id[P392]}")
if (coverage_by_id[P393]["disposition"], coverage_by_id[P393]["migration_status"]) != (
    "queued", "pending"
):
    raise SystemExit(f"p.393 should be queued/pending before migration: {coverage_by_id[P393]}")
if (coverage_by_id[P394]["disposition"], coverage_by_id[P394]["migration_status"]) != (
    "queued", "pending"
):
    raise SystemExit(f"p.394 should remain queued/pending: {coverage_by_id[P394]}")

segment = segment_by_id[P393]
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text393 = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
if hashlib.sha256(text393.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit("p.393 S0 segment hash mismatch")
line_offset = {}
offset = 0
for line_number in range(segment["line_start"], segment["line_end"] + 1):
    line_offset[line_number] = offset
    offset += len(source_lines[line_number - 1]) + 1


def quote(first_line, last_line):
    return "\n".join(source_lines[first_line - 1:last_line])


new_candidate_specs = [
    {
        "candidate_id": "cand-10816",
        "canonical_name": "Christie's sale of Joseph Smith's remaining pictures and drawings, 22 April 1776",
        "suggested_type": "event",
        "source_line": 150,
        "detail": "One of the two London sale dates Haskell gives for Smith's remaining pictures and drawings. The specific lots assigned to this date are not identified in the passage.",
    },
    {
        "candidate_id": "cand-10817",
        "canonical_name": "Christie's sale of Joseph Smith's remaining pictures and drawings, 16 May 1776",
        "suggested_type": "event",
        "source_line": 150,
        "detail": "One of the two London sale dates Haskell gives for Smith's remaining pictures and drawings. The specific lots assigned to this date are not identified in the passage; do not equate the fourteen Canaletto views here with the fourteen further pictures mentioned at p.304 note 7.",
    },
    {
        "candidate_id": "cand-10818",
        "canonical_name": "Anonymous sale identified by Haskell with John Strange, 10 December 1789",
        "suggested_type": "event",
        "source_line": 150,
        "detail": "Haskell says pictures said to have come from Smith's collection appeared in an anonymous sale and parenthetically identifies it as John Strange. The role of Strange and the catalogue were not independently verified.",
    },
    {
        "candidate_id": "cand-10819",
        "canonical_name": "Christie's 22 April 1776 list of Joseph Smith's remaining pictures and drawings",
        "suggested_type": "archive",
        "source_line": 150,
        "detail": "Locator for one of the sale lists Haskell calls unsatisfactory. No catalogue title or individual catalogue record is supplied here; the list was not independently consulted.",
    },
    {
        "candidate_id": "cand-10820",
        "canonical_name": "Fourteen Venice views by Canaletto recorded among Smith's 1776 sale pictures",
        "suggested_type": "work",
        "source_line": 150,
        "detail": "Group of fourteen views as described by Haskell. Individual titles and which of the two 1776 sale dates contained them are not given; attributions are expressly not definitive.",
    },
    {
        "candidate_id": "cand-10821",
        "canonical_name": "Two Pietro Longhi conversations described as Mr Murray and family",
        "suggested_type": "work",
        "source_line": 150,
        "detail": "Group named in Haskell's account of the 1776 sale lists. No individual titles are supplied and the identity of Mr Murray is unresolved.",
    },
    {
        "candidate_id": "cand-10822",
        "canonical_name": "Amigoni portrait of Farinelli and two others (1776 sale-list entry)",
        "suggested_type": "work",
        "source_line": 150,
        "detail": "Group/entry described by Haskell as a portrait of Farinelli and two others. No full title, identities for the other sitters, or definitive attribution is established.",
    },
    {
        "candidate_id": "cand-10823",
        "canonical_name": "Unidentified Sebastiano Ricci self-portrait said to appear in the 1789 sale",
        "suggested_type": "work",
        "source_line": 150,
        "detail": "Haskell lists a self-portrait by Sebastiano Ricci among pictures said to have come from Smith's collection in the 10 December 1789 sale. No title or independent provenance/attribution check is supplied.",
    },
    {
        "candidate_id": "cand-10824",
        "canonical_name": "Unspecified landscapes by Marco Ricci and Zuccarelli said to appear in the 1789 sale",
        "suggested_type": "work",
        "source_line": 150,
        "detail": "Group-level entry in Haskell's report of pictures said to have come from Smith's collection. Individual titles, number, and attribution are not established.",
    },
    {
        "candidate_id": "cand-10825",
        "canonical_name": "Pictures by Carpioni, Mastelletta, Pietro Liberi, Strozzi, Fetti, and Lazzarini reported in the 1789 sale",
        "suggested_type": "work",
        "source_line": 151,
        "detail": "Unspecified group in Haskell's account of pictures said to have come from Smith's collection. Individual works and the identities behind surname-only names are not resolved here.",
    },
    {
        "candidate_id": "cand-10826",
        "canonical_name": "Drawings and etchings listed in the 1776 Smith sales",
        "suggested_type": "work",
        "source_line": 152,
        "detail": "Group of drawings and etchings that Haskell says is more numerous than the pictures in the 1776 lists. Individual sheets, exact count, sale date, and definitive attributions are not supplied.",
    },
    {
        "candidate_id": "cand-10827",
        "canonical_name": "Mr Murray named as sitter with family in two Pietro Longhi conversations",
        "suggested_type": "person",
        "source_line": 150,
        "detail": "The sale-list wording gives only 'Mr Murray'; identity is not established and is not merged with the indexed John Murray candidate.",
    },
    {
        "candidate_id": "cand-10828",
        "canonical_name": "Farinelli named as sitter in an Amigoni portrait entry",
        "suggested_type": "person",
        "source_line": 150,
        "detail": "Name as printed in Haskell's account of the sale list. No given name or further sitter identification is supplied.",
    },
    {
        "candidate_id": "cand-10829",
        "canonical_name": "Moschini, 1806, volume III, p.78 (Appendix 5 p.393 citation locator)",
        "suggested_type": "archive",
        "source_line": 144,
        "detail": "Citation locator for the Venetian source Haskell invokes regarding Giuseppe Zais. The page image reads Moschini while OCR reads Meschini; the cited volume/page was not independently consulted.",
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
    candidates.append({
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
        "candidate_source_ref": f"{P393}#L{spec['source_line']}",
    })
    candidate_by_id[cid] = candidates[-1]
    existing_keys.add(key)

mention_specs = [
    ("cand-10813", "raccolta Gennari", 142, 142, "The Gennari collection named in the continuing letter; no new owner or completed transaction is identified.", 0),
    ("cand-2447", "G. Smith", 144, 144, "Signature closing the letter that begins at p.392; the manuscript was not independently consulted.", 0),
    ("cand-2719", "Venetian", 144, 144, "Adjectival reference to sources from Venice; source identity is not supplied in this sentence.", 0),
    ("cand-1709", "Meschini", 144, 144, "Raw OCR spelling; the page image reads Moschini. Keep the printed reading and person identity open for S3.", 0),
    ("cand-10829", "1806, III, p. 78", 144, 144, "Citation locator as printed; the cited volume/page was not independently consulted.", 0),
    ("cand-2830", "Giuseppe Zais", 145, 145, "Painter named by Haskell through the cited Venetian source.", 0),
    ("cand-2447", "Smith", 145, 145, "Person reported as having employed Zais; this is Haskell's report, not an independently checked contract.", 0),
    ("cand-1141", "George\nIII", 145, 146, "King to whom Haskell says Smith's pictures were sold; the name crosses the OCR line break.", 0),
    ("cand-2830", "Zais", 146, 146, "Surname repeated in Haskell's unresolved alternative explanations.", 0),
    ("cand-8983", "England", 146, 146, "Country invoked in Haskell's first possible explanation for Zais's absence from the sale.", 0),
    ("cand-2447", "Smith", 146, 146, "Person for whom Zais may have begun work only after 1762, as Haskell speculates.", 0),
    ("cand-2447", "Smith", 147, 147, "Subject of the statement Haskell attributes to Smith about forming a collection.", 0),
    ("cand-2447", "Smith", 149, 149, "Subject of Haskell's provisional synthesis about the 1762 sale and long-term accumulation.", 0),
    ("cand-1141", "the King", 149, 149, "The King refers to George III in Haskell's discussion of the 1762 sale.", 0),
    ("cand-9171", "his palace", 149, 149, "Smith's palace in which Haskell says most pictures found in 1770 had accumulated over a long period.", 0),
    ("cand-10816", "22 April", 150, 150, "Date of one of the two Christie’s sale sessions Haskell names.", 0),
    ("cand-10817", "16 May", 150, 150, "Date of the other Christie’s sale session; p.393 does not assign the listed lots to a date.", 0),
    ("cand-2447", "Smith’s", 150, 150, "Possessive reference to Smith's wishes about sale of the remaining pictures and drawings.", 0),
    ("cand-1422", "London", 150, 150, "City where Haskell says the remaining pictures and drawings were sold.", 0),
    ("cand-9400", "Christie’s", 150, 150, "Auction institution named for the 1776 sessions; reuse remains subject to global identity alignment.", 0),
    ("cand-2719", "Venice", 150, 150, "City represented in the group of Canaletto views.", 0),
    ("cand-0498", "Canaletto", 150, 150, "Artist attributed by Haskell to fourteen Venice views; the passage says attributions are not definitive.", 0),
    ("cand-10827", "Mr Murray", 150, 150, "Sitter named only as Mr Murray; not assumed to be the indexed John Murray.", 0),
    ("cand-1430", "Pietro Longhi", 150, 150, "Artist named for the two conversation pictures.", 0),
    ("cand-0094", "Amigoni", 150, 150, "Artist named for the portrait entry; attribution is not definitive.", 0),
    ("cand-10828", "Farinelli", 150, 150, "Sitter name as given in the sale-list entry; no given name is added.", 0),
    ("cand-2447", "Smith’s", 150, 150, "Possessive reference in the qualified provenance phrase 'said to have come from Smith's collection'.", 1),
    ("cand-10818", "anonymous sale", 150, 150, "Event described as anonymous by Haskell, who parenthetically identifies it with John Strange.", 0),
    ("cand-2516", "John Strange", 150, 150, "Haskell's parenthetical identification of the otherwise anonymous sale; role not established.", 0),
    ("cand-10818", "10 December 1789", 150, 150, "Date of the anonymous sale as reported by Haskell.", 0),
    ("cand-10823", "self portrait", 150, 150, "Unidentified work entry attributed to Sebastiano Ricci in Haskell's list.", 0),
    ("cand-2154", "Sebastiano Ricci", 150, 150, "Artist named for the self-portrait entry.", 0),
    ("cand-2149", "Marco Ricci", 150, 150, "Artist named for an unspecified landscape group.", 0),
    ("cand-2879", "Zuccarelli", 150, 150, "Surname as printed for an unspecified landscape group.", 0),
    ("cand-0575", "Giulio\nCarpioni", 150, 151, "Artist name split by the printed/OCR line break; preserved as a single source span.", 0),
    ("cand-1577", "Mastelletta", 151, 151, "Artist surname listed for unspecified pictures.", 0),
    ("cand-1401", "Pietro Liberi", 151, 151, "Artist named for unspecified pictures.", 0),
    ("cand-2527", "Strozzi", 151, 151, "Surname-only artist entry; identity remains for S3.", 0),
    ("cand-1033", "Fetti", 151, 151, "Printed page reads Fetti; the index candidate spells Feti, Domenico. Preserve the difference for S3.", 0),
    ("cand-1368", "Lazzarini", 151, 151, "Artist surname listed for unspecified pictures.", 0),
    ("cand-2447", "Smith’s", 152, 152, "Possessive reference in Haskell's statement that no further pictures from Smith's collection had been traced.", 0),
    ("cand-2569", "Tiepolo", 152, 152, "Artist in Haskell's inference that an important painter absent from the George III lot was unlikely to appear in future finds.", 0),
    ("cand-1141", "George III", 152, 152, "King named in the qualification about artists absent from the 1762 lot.", 0),
    ("cand-10826", "drawings and etchings", 152, 152, "Group of works in the 1776 sale lists; Haskell gives no exact count.", 0),
    ("cand-0498", "Canaletto", 152, 152, "Artist named in the 1776 drawings/etchings list.", 0),
    ("cand-1546", "Maneschi", 152, 152, "Raw OCR surface; the page image reads Marieschi. Link to the p.393 index candidate, while identity alignment remains S3.", 0),
    ("cand-1827", "Pannini", 153, 153, "Artist surname as printed in the 1776 drawings/etchings list.", 0),
    ("cand-2830", "Zais", 153, 153, "Artist surname repeated in the 1776 drawings/etchings list.", 0),
    ("cand-2879", "Zuccarelli", 153, 153, "Artist surname repeated in the 1776 drawings/etchings list.", 0),
    ("cand-2149", "Marco Ricci", 153, 153, "Artist named in the 1776 drawings/etchings list.", 0),
    ("cand-2569", "Tiepolo", 153, 153, "Artist surname as printed in the 1776 drawings/etchings list.", 0),
    ("cand-2447", "Smith’s", 154, 154, "Person whose taste Haskell says he discusses on the basis of known 1762 holdings.", 0),
    ("cand-2447", "his collection in 1762", 154, 154, "Haskell's stated evidence base; the passage allows that Smith likely owned many more pictures.", 0),
    ("cand-2447", "Smith’s", 155, 155, "Possessive reference in the opening sentence about the difficult history of Smith's books.", 0),
]

new_mentions = []
mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, first_line, last_line, note, occurrence) in enumerate(mention_specs, start=1):
    mid = f"m-chp19-p393-{ordinal:03d}"
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention targets missing or excluded candidate: {cid}")
    lower = line_offset[first_line]
    upper = line_offset[last_line] + len(source_lines[last_line - 1])
    cursor = lower
    found = -1
    for _ in range(occurrence + 1):
        found = text393.find(surface, cursor, upper)
        if found < 0:
            raise SystemExit(
                f"surface not found in p.393 lines {first_line}-{last_line}: {surface!r}"
            )
        cursor = found + 1
    end = found + len(surface)
    if end > upper or text393[found:end] != surface:
        raise SystemExit(f"span mismatch for {mid}")
    new_mentions.append({
        "mention_id": mid,
        "segment_id": P393,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(found),
        "end_char": str(end),
        "note": note,
    })
    mention_ids.add(mid)


def statement(statement_id, first, last, subject, object_, predicate, claim, speaker, text_layer,
              qualification, candidate_ids, date=None, relation=False, **extra):
    qualifiers = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": 393,
        "pdf_physical_page": 8,
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
        "segment_id": P393,
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
        "st-chp19-p393-smith-1768-letter-continuation", 141, 141, "cand-2447", None,
        "smith_continued_1768_letter_about_fewer_buyers_and_his_purchase_of_several_pictures_and_prints",
        "The p.393 continuation says buyers were fewer, pictures and prints were frequently offered, and Smith had bought several of each and might show them to the correspondent on a future visit.",
        "Joseph Smith", "quoted archival letter",
        "The sentence begins on p.392 and closes on this page. Smith's wording does not establish that the pictures and prints were bought for his own collection rather than handled for others; no individual works are identified.",
        ["cand-2447", "cand-10811", "cand-10815"], date="1768-04-09", relation=True,
        cross_reference_segments=[P392],
        cross_reference_statement_ids=["st-chp19-p392-smith-conditional-gennari-collection-offer"],
        cited_material_not_independently_consulted=True,
        continuation_of_statement_id="st-chp19-p392-smith-conditional-gennari-collection-offer",
    ),
    statement(
        "st-chp19-p393-smith-gennari-note-and-letter-signature", 142, 143, "cand-2447", "cand-10812",
        "smith_returned_gennari_collection_note_for_clearer_copy_and_requested_discretion",
        "Smith says he is returning the Gennari collection note so the correspondent can send a clearer copy, because he dislikes handing it to other people; the letter then closes with Smith's signature.",
        "Joseph Smith", "quoted archival letter",
        "The note/list is not reproduced here; this request does not establish the owner's identity or a completed purchase. The addressee remains unidentified.",
        ["cand-2447", "cand-10811", "cand-10812", "cand-10813", "cand-10814", "cand-10815"],
        date="1768-04-09", relation=True,
        cross_reference_segments=[P392],
        cross_reference_statement_ids=["st-chp19-p392-smith-conditional-gennari-collection-offer"],
        cited_material_not_independently_consulted=True,
        continuation_status="closed",
    ),
    statement(
        "st-chp19-p393-zais-and-1762-sale-uncertainty", 144, 146, "cand-2830", "cand-2447",
        "haskell_reported_zais_worked_for_smith_and_left_his_absence_from_the_1762_sale_unexplained",
        "Haskell reports from a Venetian source that Giuseppe Zais worked for Smith and that Zais's pictures were not among those sold to George III; he asks whether Zais was unknown in England and not selected by the royal agent, or began working for Smith only after 1762.",
        "Haskell summarizing a cited Venetian source and posing alternatives", "authorial report and unresolved questions",
        "The cited Moschini volume III, p.78 was not independently consulted. The page image reads Moschini while OCR reads Meschini. Haskell presents both explanations as questions and does not resolve them.",
        ["cand-2830", "cand-2447", "cand-10807", "cand-1141", "cand-8983", "cand-2719", "cand-1709", "cand-10829"],
        date="1762", relation=True,
        ocr_corrections=[
            {"source_line": 144, "ocr": "Meschini", "print": "Moschini", "basis": "CHP-19Appendix.pdf physical page 8."}
        ],
        cited_material_not_independently_consulted=True,
    ),
    statement(
        "st-chp19-p393-smith-own-collection-remark", 147, 148, "cand-2447", "cand-10807",
        "haskell_quoted_smith_on_the_difficulty_of_forming_a_similar_collection_and_interpreted_the_1762_payment",
        "Haskell attributes to Smith the statement that a collection of this kind could no longer be formed because suitable subjects no longer existed or were hardly purchasable; Haskell adds that the £20,000 Smith received in 1762 would have helped.",
        "Joseph Smith as quoted by Haskell; Haskell for the £20,000 comment", "embedded quotation and authorial comment",
        "The underlying source for Smith's quotation is not identified on this page and was not independently checked. The final clause about £20,000 is Haskell's comment; neither passage independently establishes what pictures were included in the 1762 sale.",
        ["cand-2447", "cand-10807"],
        date="1762",
        ocr_corrections=[
            {"source_line": 147, "ocr": "(/)", "print": "(f)", "basis": "CHP-19Appendix.pdf physical page 8."},
            {"source_line": 147, "ocr": "¿20,000", "print": "£20,000", "basis": "CHP-19Appendix.pdf physical page 8."},
        ],
        cited_material_not_independently_consulted=True,
    ),
    statement(
        "st-chp19-p393-haskell-smith-sale-synthesis", 149, 149, "cand-2447", "cand-1141",
        "haskell_strongly_but_provisionally_believed_smith_sold_only_part_in_1762",
        "Haskell says the evidence permits no final conclusion but strongly believes Smith sold only part of his collection to the King in 1762 and that most pictures found in Smith's palace in 1770 had accumulated over a long period. He acknowledges this could affect his account of patronage in Chapter 11, while arguing the evidence does not require a drastic revision.",
        "Haskell", "authorial synthesis and qualified inference",
        "This is Haskell's provisional interpretation, not a settled result. It preserves the unresolved alternatives from pp.391–392 and explicitly leaves room for future evidence.",
        ["cand-2447", "cand-1141", "cand-9171", "cand-10807"],
        date="1762–1770", relation=True,
        cross_reference_segments=[
            "chp-19:19_CHP-19Appendix:l109-124",
            P392,
        ],
        cross_reference_statement_ids=[
            "st-chp19-p391-smith-sale-hypotheses-unresolved",
            "st-chp19-p392-transition-only-certain-knowledge",
        ],
    ),
    statement(
        "st-chp19-p393-christies-1776-sales-and-listed-pictures", 150, 150, "cand-2447", None,
        "haskell_reported_two_1776_christies_sales_and_qualified_their_lists_and_picture_entries",
        "Haskell says the remaining pictures and drawings were sold in London at Christie's on 22 April and 16 May 1776. He considers the lists unsatisfactory and the attributions non-definitive, then names fourteen Canaletto Venice views, two Pietro Longhi conversations described as Mr Murray and family, and an Amigoni portrait entry for Farinelli and two others.",
        "Haskell", "authorial report of sale lists",
        "The catalogues/lists were not independently consulted. The passage does not assign any named picture group to one of the two dates. The fourteen Canaletto views are not established as the fourteen further pictures attributed to the 16 May catalogue at p.304 note 7.",
        ["cand-2447", "cand-1422", "cand-9400", "cand-10816", "cand-10817", "cand-10819",
         "cand-0498", "cand-2719", "cand-10820", "cand-1430", "cand-10821", "cand-10827",
         "cand-0094", "cand-10822", "cand-10828", "cand-9543", "cand-9544"],
        date="1776-04-22 / 1776-05-16", relation=True,
        cross_reference_segments=[P10_SALE_NOTE],
        cross_reference_statement_ids=["st-chp10-p304-note7-christies-sale-catalogue"],
        ocr_corrections=[
            {"source_line": 150, "ocr": "fists", "print": "lists", "basis": "CHP-19Appendix.pdf physical page 8."}
        ],
        cited_material_not_independently_consulted=True,
    ),
    statement(
        "st-chp19-p393-1789-anonymous-sale-and-attributed-groups", 150, 151, "cand-2447", "cand-10818",
        "haskell_reported_pictures_said_to_come_from_smiths_collection_in_a_1789_anonymous_sale",
        "Haskell adds pictures said to have come from Smith's collection in an anonymous sale of 10 December 1789, parenthetically identifying it with John Strange. The entries include a Sebastiano Ricci self-portrait, landscapes by Marco Ricci and Zuccarelli, and unspecified pictures by Carpioni, Mastelletta, Pietro Liberi, Strozzi, Fetti, and Lazzarini.",
        "Haskell", "qualified provenance report",
        "The phrase 'said to have come from Smith's collection' is retained as reported provenance, not verified ownership. The sale catalogue, individual works, artist identities behind surname-only entries, and attributions were not independently checked. The p.393 index spells Feti, Domenico, while the page text reads Fetti; defer identity alignment to S3.",
        ["cand-2447", "cand-10818", "cand-2516", "cand-10823", "cand-2154", "cand-10824",
         "cand-2149", "cand-2879", "cand-10825", "cand-0575", "cand-1577", "cand-1401",
         "cand-2527", "cand-1033", "cand-1368"],
        date="1789-12-10", relation=True,
        cited_material_not_independently_consulted=True,
    ),
    statement(
        "st-chp19-p393-haskell-future-picture-find-inference", 152, 152, "cand-2447", None,
        "haskell_inferred_future_picture_finds_would_follow_the_known_pattern_and_tiepolo_was_unlikely",
        "Haskell says no further pictures from Smith's collection had been traced and judges it likely that future finds would fit the existing pattern; he considers it most improbable that Tiepolo or other important artists absent from the George III lot would appear.",
        "Haskell", "authorial inference",
        "This describes Haskell's state of tracing and prediction, not proof that no further works exist. The prediction is explicitly probabilistic.",
        ["cand-2447", "cand-10807", "cand-1141", "cand-2569"],
        date="1776 / 1780s inference",
    ),
    statement(
        "st-chp19-p393-1776-drawings-etchings-and-artists", 152, 153, "cand-2447", "cand-10826",
        "haskell_said_1776_drawings_and_etchings_were_more_numerous_and_named_represented_artists",
        "Haskell says the drawings and etchings in the 1776 sale were much more numerous and lists Canaletto, Marieschi, Pannini, Zais, Zuccarelli, Marco Ricci, and Tiepolo as well represented.",
        "Haskell", "authorial report of sale lists",
        "The page image reads Marieschi where OCR reads Maneschi. No individual drawing or etching is identified, and 'well represented' is Haskell's summary rather than an exhaustive count. The sale lists were not independently consulted.",
        ["cand-2447", "cand-10826", "cand-0498", "cand-1546", "cand-1827", "cand-2830",
         "cand-2879", "cand-2149", "cand-2569"],
        date="1776",
        ocr_corrections=[
            {"source_line": 152, "ocr": "Maneschi", "print": "Marieschi", "basis": "CHP-19Appendix.pdf physical page 8."}
        ],
        cited_material_not_independently_consulted=True,
    ),
    statement(
        "st-chp19-p393-haskell-basis-for-smith-taste-discussion", 154, 154, "cand-2447", "cand-10807",
        "haskell_based_his_discussion_of_smiths_taste_on_known_1762_holdings_despite_likely_additional_pictures",
        "Haskell says he felt justified, though reluctantly, in discussing Smith's taste on the basis of what was known to have been in his collection in 1762, while thinking it likely Smith owned many more pictures.",
        "Haskell", "authorial methodological statement",
        "This explains Haskell's stated evidentiary basis; it does not establish that the known 1762 holdings were Smith's complete collection.",
        ["cand-2447", "cand-10807"],
        date="1762",
    ),
    statement(
        "st-chp19-p393-smith-books-history-open", 155, 155, "cand-2447", None,
        "haskell_opened_a_qualified_statement_about_the_difficult_history_of_smiths_books",
        "Haskell begins to say that the history of Smith's books is difficult to reconstruct, but the sentence is cut off at the page boundary.",
        "Haskell", "authorial transition",
        "This is an incomplete sentence; do not infer its comparison or conclusion before reading p.394.",
        ["cand-2447"], continuation_to_segment_id=P394, continuation_status="open",
    ),
]

# The signature shares source line 144 with the next paragraph's marker and prose.
# Include the signature substring without importing Haskell's following paragraph.
new_statements[1]["qualifiers"]["source_line_end"] = 144
new_statements[1]["original_quote"] = quote(142, 143) + "\nG. Smith"

existing_statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    sid = row["statement_id"]
    if sid in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {sid}")
    existing_statement_ids.add(sid)
    if row["original_quote"] not in text393:
        raise SystemExit(f"statement quote not contained in p.393 segment: {sid}")
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement {sid} references unavailable candidate {cid}")
    for ref_id in row["qualifiers"].get("cross_reference_statement_ids", []):
        if ref_id not in statement_by_id and ref_id not in existing_statement_ids:
            raise SystemExit(f"statement {sid} references missing statement {ref_id}")

closing_statement_id = "st-chp19-p392-smith-conditional-gennari-collection-offer"
if closing_statement_id not in statement_by_id:
    raise SystemExit(f"missing open p.392 statement: {closing_statement_id}")
closing_statement = statement_by_id[closing_statement_id]
if closing_statement.get("qualifiers", {}).get("continuation_status") != "open":
    raise SystemExit("p.392 Gennari-letter statement is not open for closure")
if (
    closing_statement.get("qualifiers", {}).get("continuation_to_segment_id") != P393
    and P393 not in closing_statement.get("qualifiers", {}).get("cross_reference_segments", [])
):
    raise SystemExit("p.392 Gennari-letter continuation does not point to p.393")
closing_statement["qualifiers"]["continuation_to_segment_id"] = P393
closing_statement["qualifiers"]["continuation_status"] = "closed"
closing_statement["qualifiers"]["continuation_closed_by_segment_id"] = P393
closing_statement["qualifiers"]["continuation_line_start"] = 141
closing_statement["qualifiers"]["continuation_line_end"] = 144
closing_statement["qualifiers"]["continuation_suffix"] = "G. Smith"
closing_statement["qualifiers"]["cross_reference_statement_ids"] = [
    "st-chp19-p393-smith-1768-letter-continuation"
]
closing_statement["qualifiers"]["qualification"] = (
    "This is a conditional offer and request, not evidence of a completed purchase. The collection's individual "
    "works, the owner, and the correspondent remain unidentified. The sentence continues and closes on p.393 L141; "
    "the returned-note request and signature are recorded in a linked p.393 statement."
)

statements.extend(new_statements)
mentions.extend(new_mentions)

coverage_by_id[P392]["disposition"] = "reviewed"
coverage_by_id[P392]["migration_status"] = "complete"
coverage_by_id[P392]["source_line_ranges"] = "L127-138"
coverage_by_id[P392]["note"] = (
    "Printed p.392 (PDF physical page 7) read against the page image. Processes Haskell's competing evidence about "
    "Joseph Smith's 1761–1762 plans, the attributed 1806 account, artists in the King's sale, and two post-1762 letters. "
    "Page-image corrections are recorded on statements; cited sources and archival manuscripts were not independently "
    "consulted. The 9 April 1768 letter's sentence closes on p.393 L141 and its signature is on L144."
)
coverage_by_id[P393]["disposition"] = "reviewed"
coverage_by_id[P393]["migration_status"] = "partial"
coverage_by_id[P393]["source_line_ranges"] = "L141-155"
coverage_by_id[P393]["note"] = (
    "Printed p.393 (PDF physical page 8) read against the page image. Closes Smith's 9 April 1768 letter begun on "
    "p.392; records Haskell's qualified reports about Zais, Smith's collection, the 1776 Christie’s lists, and the "
    "1789 anonymous sale. Page-image corrections include Moschini, '(f)', £20,000, 'lists', and Marieschi; the "
    "cited source and sale lists were not independently consulted. The opening sentence about Smith's books at "
    "L155 continues on p.394, so this segment remains partial."
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
    print("applied p.393 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(new_candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.392: reviewed/partial -> reviewed/complete; p.393: queued/pending -> reviewed/partial")
    print("p.394 remains queued/pending; the books-history sentence stays open for its continuation")
    print("preserved Haskell's unresolved sale interpretations, qualified provenance, and uncertain attributions")
