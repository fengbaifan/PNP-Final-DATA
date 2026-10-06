#!/usr/bin/env python3
"""Controlled S2 migration for Appendix 4's p.391 continuation and Appendix 5 opening."""

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
CH8_SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
CH8_PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"
EXPECTED_HASHES = {
    SOURCE: "725dc16a2983bec379ce2a8b608542ab3defe348d2b2f2a336632ac4905388f1",
    PDF: "2a1c29e6c2864527482d231a85c4252e55524b436ae4dff5b0d55d9d5a67a9eb",
    CH8_SOURCE: "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6",
    CH8_PDF: "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3",
}
P390 = "chp-19:19_CHP-19Appendix:l86-107"
P391 = "chp-19:19_CHP-19Appendix:l109-124"
P235_NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
P10_NEGOTIATIONS = "chp-10:10_CHP-10_intro:l481-489"
BACKUP_SUFFIX = ".bak-s2-chp19-p391-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
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
statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
coverage_fields, coverage = read_csv(coverage_path)
segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}

if P390 not in segment_by_id or P391 not in segment_by_id or P390 not in coverage_by_id or P391 not in coverage_by_id:
    raise SystemExit("missing S0 or S2 row for the p.390/p.391 continuation")
if (coverage_by_id[P390]["disposition"], coverage_by_id[P390]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"p.390 must be reviewed/partial before continuation: {coverage_by_id[P390]}")
if (coverage_by_id[P391]["disposition"], coverage_by_id[P391]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.391 must be queued/pending before migration: {coverage_by_id[P391]}")


def read_segment(segment_id):
    row = segment_by_id[segment_id]
    lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[row["line_start"] - 1:row["line_end"]])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != row["sha256"]:
        raise SystemExit(f"segment hash mismatch: {segment_id}")
    return text, lines


text391, source_lines = read_segment(P391)
read_segment(P235_NOTES)
read_segment(P10_NEGOTIATIONS)


def quote(first_line, last_line):
    return "\n".join(source_lines[first_line - 1:last_line])


new_candidate_specs = [
    ("cand-10803", "Caldari (surname only; person addressed in Ranuzzi's 1708 letter)", "person", 110,
     "Ranuzzi says he is writing to Caldari about an incident concerning a picture; the source supplies no given name or independent identity."),
    ("cand-10804", "Unidentified painting belonging to Caldari mentioned by Ranuzzi in 1708", "work", 110,
     "The letter mentions an incident concerning Caldari's picture and says it is to be brought to Ferdinand's attention; neither subject nor outcome is given."),
    ("cand-10805", "Seven Years War (as cited in Haskell's account of Smith's interrupted collection negotiations)", "event", 123,
     "Appendix 5 says the war broke out and the plans came to nothing. No date or detailed sequence is added here."),
    ("cand-10806", "List of pictures in Joseph Smith's palace recorded by Ferdinando Uccelli (1770; Archivio di Stato, Petizion 467)", "archive", 118,
     "Haskell reports several hundred pictures recorded in Smith's palace at his death and says the list gives subjects, not artists, and was reprinted by C. A. Levi. The archival item was not independently consulted."),
    ("cand-10807", "Paintings and drawings sold by Joseph Smith to George III in 1762 (unnamed group)", "work", 117,
     "Haskell reports a very large number of paintings and drawings in the 1762 sale; no individual works or exact count are given in this passage."),
]
existing_keys = {
    ((row.get("canonical_name") or "").strip().casefold(), (row.get("suggested_type") or "").strip().casefold())
    for row in candidates
}
for cid, name, kind, line, detail in new_candidate_specs:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    key = (name.strip().casefold(), kind.casefold())
    if key in existing_keys:
        raise SystemExit(f"candidate natural key already exists: {name} / {kind}")
    row = {
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P391}#L{line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

for cid, kind in {
    "cand-0873": "person", "cand-1141": "person", "cand-2096": "person",
    "cand-2447": "person", "cand-2471": "person", "cand-2476": "person",
    "cand-2665": "person", "cand-8651": "archive", "cand-9171": "place",
    "cand-9186": "person", "cand-9276": "event", "cand-9278": "event",
}.items():
    row = candidate_by_id.get(cid)
    if not row:
        raise SystemExit(f"expected candidate missing: {cid}")
    if row.get("suggested_type") and row["suggested_type"] != kind:
        raise SystemExit(f"candidate type conflict for {cid}: {row['suggested_type']} != {kind}")
    row["suggested_type"] = kind

# The marginal note closes the local referent from the prior segment as Crespi.
local_painter = candidate_by_id.get("cand-10802")
if not local_painter or local_painter.get("status") != "open":
    raise SystemExit("expected open local Spanish-painter candidate is missing")
local_painter["status"] = "excluded"
local_painter["exclude_reason"] = (
    "The p.391 continuation places the marginal note 'Gius.e Crespi d.o' after the phrase 'lo Spagnuolo Pittore'; "
    "Chapter 8 p.237 note 2 identifies this Filza 5897 No.183 letter as Crespi's letter of introduction. "
    "Map the p.390 role mention to existing candidate cand-0873; this is not a new person or external identity alignment."
)
local_painter["detail"] = "Retired after p.391 continuation identified the p.390 role through a marginal note; retained as a traceable local resolution."

for cid, detail in {
    "cand-2096": "The 31 January 1708 letter to Ferdinand is reproduced across Appendix 4 pp.390–391, Filza 5897, No.183. The p.391 margin reads 'Gius.e Crespi d.o' beside 'lo Spagnuolo Pittore'; its text also names Caldari and an incident concerning his picture. The manuscript was not independently consulted.",
    "cand-8016": "The letter of introduction cited in Chapter 8 p.237 note 2 begins on Appendix 4 p.390 as a 31 January 1708 letter from Vincenzo/Vincenzio Ranuzzi, Filza 5897, No.183, and closes on p.391. Its marginal note reads 'Gius.e Crespi d.o'; the manuscript was not independently consulted.",
    "cand-8651": "The will is cited in Chapter 9 and summarized/quoted by Haskell in Appendix 5 p.391 as a 1761 will addressing the disposal of Smith's collection. The will and Parker publication were not independently consulted.",
    "cand-8533": "C. A. Levi's inventory publication is cited in Appendix 5 p.391, vol. II, pp.236–248, as reprinting the Petizion 467 list. Exact title/edition and the publication itself remain unverified.",
    "cand-9177": "Chapter 10 and Appendix 5 p.391 discuss the library in relation to George III: Haskell says negotiations were under way by about 1755 and describes later collection-disposal plans. The type of this collection-level object remains unresolved.",
    "cand-9276": "Chapter 10 p.310 dates Smith's negotiations to 1756 and says the war interrupted them; Appendix 5 p.391 says negotiations were under way by about 1755 and the plans came to nothing. Preserve both source-specific date formulations.",
}.items():
    if cid not in candidate_by_id:
        raise SystemExit(f"expected reusable candidate missing: {cid}")
    candidate_by_id[cid]["detail"] = detail

prior_ranuzzi = next((row for row in statements if row.get("statement_id") == "st-chp19-p390-ranuzzi-letter-heading"), None)
if not prior_ranuzzi or prior_ranuzzi["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("p.390 Ranuzzi opening statement is missing or already closed")
prior_ranuzzi["qualifiers"]["claim"] = (
    "The Appendix 4 heading identifies a letter from Vincenzo Ranuzzi dated 31 January 1708, Archivio Mediceo, Filza 5897, No. 183. "
    "The opening calls its subject the Spanish painter; the p.391 continuation gives the marginal words 'Gius.e Crespi d.o', "
    "and Chapter 8 p.237 note 2 identifies this as Crespi's letter of introduction."
)
prior_ranuzzi["qualifiers"]["qualification"] = (
    "The identity mapping follows the printed marginal note and the Chapter 8 cross-reference; the abbreviation 'd.o' is retained without expansion. "
    "The letter's further remarks about Caldari and a picture are recorded separately."
)
prior_ranuzzi["qualifiers"]["mentioned_candidate_ids"] = ["cand-2096", "cand-8016", "cand-1611", "cand-0873"]
prior_ranuzzi["qualifiers"]["continuation_status"] = "closed"
prior_ranuzzi["qualifiers"]["continuation_closed_by_statement_id"] = "st-chp19-p391-ranuzzi-margin-crespi"
prior_ranuzzi["qualifiers"]["cross_reference_segments"] = [P391, P235_NOTES]

prior_role_mention = next((row for row in mentions if row.get("mention_id") == "m-chp19-p390-045"), None)
if not prior_role_mention or prior_role_mention.get("candidate_id") != "cand-10802":
    raise SystemExit("expected p.390 unresolved painter mention is missing or changed")
prior_role_mention["candidate_id"] = "cand-0873"
prior_role_mention["note"] = "The p.391 marginal note reads 'Gius.e Crespi d.o'; Chapter 8 p.237 note 2 identifies the letter as Crespi's introduction letter."

new_mentions = []
mention_ids = {row["mention_id"] for row in mentions}


def add_mention(ordinal, cid, surface, note="", occurrence=0):
    mid = f"m-chp19-p391-{ordinal:03d}"
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention targets missing or excluded candidate: {cid}")
    start = -1
    cursor = 0
    for _ in range(occurrence + 1):
        start = text391.find(surface, cursor)
        if start < 0:
            raise SystemExit(f"surface not found in p.391 segment: {surface!r}")
        cursor = start + 1
    end = start + len(surface)
    if text391[start:end] != surface:
        raise SystemExit(f"span mismatch for {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": P391, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_ids.add(mid)


mention_specs = [
    ("cand-0873", "Gius.e Crespi d.o", "Printed marginal identification following the p.390 phrase 'lo Spagnuolo Pittore'; retain the source abbreviation."),
    ("cand-10803", "Al Caldari", "Person named only by surname in Ranuzzi's letter."),
    ("cand-10804", "Suo Quadro", "Caldari's picture mentioned in connection with an unspecified incident."),
    ("cand-1611", "V.A.R.", "Ranuzzi's honorific reference to Ferdinand."),
    ("cand-2096", "Vincenzio Ranuzzi", "Printed subscription; the indexed candidate is Ranuzzi, Vincenzo."),
    ("cand-8016", "Bologna 31 Gennaro 1708", "Date and place in the closing of the letter of introduction."),
    ("cand-2447", "Consul Smith", "Subject named in the Appendix 5 heading."),
    ("cand-2292", "Royal Collection", "Collection named in the Appendix 5 heading.", 0),
    ("cand-2447", "Smith’s activities", "Haskell's account of Smith as collector and patron."),
    ("cand-2471", "Smith sold to George III", "Smith candidate for the sale subentry."),
    ("cand-1141", "George III", "Buyer identified in the account of the 1762 sale.", 0),
    ("cand-10807", "paintings and drawings", "The aggregate group of artworks reported in the 1762 sale."),
    ("cand-2292", "Royal Collection", "Current collection identified by Haskell as holding works from the sale.", 1),
    ("cand-2471", "logued by him", "The printed word is split by line-end hyphenation as cata- / . logued; the pronoun refers to Joseph Smith."),
    ("cand-10806", "several hundred pictures", "Pictures reportedly still recorded in Smith's palace at his death.", 0),
    ("cand-2665", "Ferdinando Uccelli", "Notary named as recorder of the pictures."),
    ("cand-9171", "his palace", "Joseph Smith's palace referenced in the collection account."),
    ("cand-10806", "The list of these", "The list recording the pictures in Smith's palace."),
    ("cand-10806", "Archivio di Stato-Petizion 467", "Archival locator from which the list is reported to be reprinted."),
    ("cand-8532", "C. A. Levi", "Person named as publisher/reprinter of the list."),
    ("cand-8533", "II, pp. 236-48", "Volume and pages cited for Levi's inventory publication."),
    ("cand-2471", "Smith in 1762", "Smith named in the first alternative about the 1762 sale."),
    ("cand-1141", "the King", "The King in the first alternative refers to George III."),
    ("cand-8651", "will of 1761", "The will as cited by Haskell; the document itself was not independently consulted."),
    ("cand-2476", "Smith wrote", "Smith as testator in Haskell's report of the will."),
    ("cand-9186", "his widow", "The unnamed wife referred to in the 1761 will; Chapter 10 describes her as Smith's second wife."),
    ("cand-9177", "my Library", "One class of Smith's collection that he hoped would remain united."),
    ("cand-10807", "Drawings", "Collection class named in the will excerpt; individual items are not identified."),
    ("cand-10807", "Pictures", "Collection class named in the will excerpt; individual items are not identified."),
    ("cand-1141", "George III", "Proposed purchaser of the library by about 1755.", 1),
    ("cand-9177", "the Library", "Library named in the reported negotiations with George III."),
    ("cand-10807", "the drawings", "Drawings said to be included in the proposed library purchase."),
    ("cand-10805", "Seven Years War", "War named as the event after which the negotiations failed."),
    ("cand-9276", "the plans came to nothing", "The planned collection purchase said to have failed after the war."),
    ("cand-2476", "Smith assumed", "Smith's 1761 expectation about disposal after his death."),
    ("cand-9186", "young wife", "The wife whom Haskell says Smith had married three years earlier."),
    ("cand-2447", "all the collection", "The entire collection Smith thought would be sold after his death."),
    ("cand-9278", "the deal whereby the pictures", "Reference to the reported 1762 sale; this is the same transaction described at p.391 L117-118."),
    ("cand-2292", "the Royal", "The Royal Collection name is split by the p.391 line break; this occurrence is in the concluding sentence.", 2),
    ("cand-1141", "the King", "The King in the concluding sentence refers to George III.", 2),
]
for i, (cid, surface, note, *rest) in enumerate(mention_specs, start=1):
    occurrence = rest[0] if rest else 0
    add_mention(i, cid, surface, note, occurrence)


def statement(statement_id, first, last, subject, object_, predicate, claim, speaker, text_layer,
              qualification, candidates, date=None, relation=False, **extra):
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 391,
        "pdf_physical_page": 6, "claim": claim, "speaker": speaker,
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": candidates, "relation_candidate": relation,
        "cited_material_not_independently_consulted": True,
    }
    if date:
        qualifiers["date"] = date
    qualifiers.update(extra)
    return {
        "statement_id": statement_id, "segment_id": P391,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(first, last),
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    }


new_statements = [
    statement(
        "st-chp19-p391-ranuzzi-margin-crespi", 110, 113, "cand-2096", "cand-0873",
        "ranuzzi_letter_marginal_note_identifies_the_introduced_painter_as_crespi",
        "The continuation of Ranuzzi's letter says the margin bears the words 'Gius.e Crespi d.o' after the reference to the Spanish painter; the letter closes at Bologna on 31 January 1708 under Vincenzio Ranuzzi's signature. Chapter 8 p.237 note 2 identifies the same letter as Crespi's letter of introduction.",
        "Vincenzio Ranuzzi and the printed marginal note", "quoted archival letter and marginal annotation",
        "The internal mapping to Giuseppe Maria Crespi follows the margin and the Chapter 8 cross-reference. The abbreviation 'd.o' is preserved and not expanded; the archival manuscript was not independently consulted.",
        ["cand-2096", "cand-0873", "cand-8016", "cand-1611"],
        date="1708-01-31", relation=True,
        cross_reference_segments=[P390, P235_NOTES],
    ),
    statement(
        "st-chp19-p391-ranuzzi-caldari-picture-incident", 110, 110, "cand-2096", "cand-10804",
        "ranuzzi_wrote_caldari_about_an_unspecified_incident_concerning_his_picture",
        "Ranuzzi says he is writing to Caldari to inform him of an incident concerning one of Caldari's pictures, so that it can be presented to Ferdinand, and asks that his service not remain idle.",
        "Vincenzio Ranuzzi", "quoted archival letter",
        "The letter gives no detail about the incident, picture, or any resulting presentation; the manuscript was not independently consulted.",
        ["cand-2096", "cand-10803", "cand-10804", "cand-1611"],
        date="1708-01-31", relation=True,
    ),
    statement(
        "st-chp19-p391-smith-evidence-gap", 116, 116, "cand-2447", None,
        "haskell_identified_a_crucial_evidence_gap_in_assessing_smith_as_collector_and_patron",
        "Haskell says his assessment of Smith's collecting and patronage is seriously impaired by a crucial gap in the available knowledge.",
        "Haskell", "authorial discussion",
        "This records Haskell's stated research problem, not an independent evaluation of the surviving evidence.",
        ["cand-2447", "cand-2292"], relation=False,
    ),
    statement(
        "st-chp19-p391-smith-1762-sale-to-george-iii", 117, 118, "cand-2471", "cand-2292",
        "haskell_reported_1762_sale_of_many_smith_paintings_and_drawings_to_george_iii",
        "Haskell reports that in 1762 Smith sold a very large number of paintings and drawings to George III; these works still form one of the chief glories of the Royal Collection, Smith catalogued them, and most are recognizable or traceable.",
        "Haskell", "authorial report",
        "The passage does not give an exact count or identify each work. This sale is the same transaction described again at p.391 L123-124, not a second sale.",
        ["cand-2471", "cand-1141", "cand-2292", "cand-10807", "cand-9278"],
        date="1762", relation=True,
    ),
    statement(
        "st-chp19-p391-smith-1770-picture-list", 118, 119, "cand-2665", "cand-10806",
        "uccelli_recorded_several_hundred_smith_palace_pictures_in_1770",
        "Haskell says that at Smith's death in 1770 several hundred pictures were recorded by notary Ferdinando Uccelli as being in Smith's palace. The list gives subjects but not artists; Haskell says it was reprinted from Archivio di Stato, Petizion 467 by C. A. Levi, vol. II, pp.236-248.",
        "Haskell", "authorial report and citation",
        "The original list, archival record, and Levi publication were not independently consulted. The source does not identify the palace by name in this passage.",
        ["cand-2665", "cand-10806", "cand-2447", "cand-9171", "cand-8532", "cand-8533"],
        date="1770", relation=True,
    ),
    statement(
        "st-chp19-p391-smith-sale-hypotheses-unresolved", 119, 121, "cand-2447", "cand-10806",
        "haskell_presented_two_unresolved_explanations_for_smiths_1770_picture_list",
        "Haskell presents two alternatives: Smith may have sold only a selection in 1762 and retained or continued adding to the rest, or he may have sold everything and acquired several hundred pictures between 1762 and 1770. He says the dilemma is central and that the available evidence does not yet establish which account is correct.",
        "Haskell", "authorial analysis",
        "The alternatives remain hypotheses, not facts adopted by this dataset. Haskell says the 1770 list gives subjects but not artists, so it cannot by itself settle the date or provenance of the pictures.",
        ["cand-2447", "cand-10806", "cand-2471", "cand-1141"],
        relation=False,
    ),
    statement(
        "st-chp19-p391-smith-1761-will-and-collection-classes", 122, 122, "cand-2476", "cand-8651",
        "haskell_reported_smiths_1761_will_and_desire_to_keep_some_collection_classes_united",
        "Haskell reports that Smith's 1761 will authorized his widow to sell all or part of the collection to secure a comfortable settlement for herself, while Smith also expressed a hope that some entire classes—his library, drawings, gems, or pictures—might remain together.",
        "Haskell reporting and quoting Smith's will", "authorial report with quotation from a cited document",
        "The will and its published text were not independently consulted. Haskell names neither the wife nor the individual books, drawings, gems, or pictures in this passage.",
        ["cand-2476", "cand-8651", "cand-9186", "cand-9177", "cand-10807"],
        date="1761", relation=False,
    ),
    statement(
        "st-chp19-p391-smith-library-negotiations-and-war", 122, 123, "cand-2447", "cand-9177",
        "haskell_reported_library_purchase_negotiations_by_about_1755_failed_after_the_seven_years_war",
        "Haskell says negotiations were under way by about 1755 for George III to purchase Smith's library, including the drawings; after the Seven Years War broke out, the plans came to nothing.",
        "Haskell", "authorial report",
        "Appendix 5 says 'by about 1755'; Chapter 10 p.310 dates the start to 1756, a year after the 1755 inventory. Preserve the source-specific date formulations rather than forcing a single exact year.",
        ["cand-2447", "cand-1141", "cand-9177", "cand-10805", "cand-9276"],
        relation=True, cross_reference_segments=[P10_NEGOTIATIONS],
    ),
    statement(
        "st-chp19-p391-smith-1761-expectation-and-1762-sale", 123, 124, "cand-2476", "cand-9278",
        "haskell_described_smiths_expected_posthumous_sale_replaced_by_a_1762_sale_to_george_iii",
        "Haskell says that in 1761 Smith expected the collection to be sold after his death by his young wife, whom he had married three years earlier; in 1762 the position changed and Smith concluded the deal selling pictures and books now in the Royal Collection to the King.",
        "Haskell", "authorial report",
        "The wife remains unnamed in this passage and maps to the existing local wife candidate. This describes the same 1762 transaction reported at p.391 L117-118; the two passages give different details of it.",
        ["cand-2476", "cand-2447", "cand-9186", "cand-9278", "cand-2292", "cand-1141", "cand-9177", "cand-10807"],
        relation=True,
    ),
]

existing_statement_ids = {row["statement_id"] for row in statements}
for row in new_statements:
    if row["statement_id"] in existing_statement_ids:
        raise SystemExit(f"statement ID already exists: {row['statement_id']}")
    existing_statement_ids.add(row["statement_id"])
    for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
        if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
            raise SystemExit(f"statement {row['statement_id']} references unavailable candidate {cid}")
    if row["original_quote"] not in text391:
        raise SystemExit(f"statement quote not contained in p.391 segment: {row['statement_id']}")

mentions.extend(new_mentions)
statements.extend(new_statements)
coverage_by_id[P390]["migration_status"] = "complete"
coverage_by_id[P390]["note"] = (
    "The p.390 Ranuzzi letter continues on p.391; the marginal note 'Gius.e Crespi d.o' and Chapter 8 p.237 note 2 "
    "map the p.390 'Spagnuolo Pittore' mention to Crespi. The letter closes at Bologna on 31 January 1708."
)
coverage_by_id[P391]["disposition"] = "reviewed"
coverage_by_id[P391]["migration_status"] = "complete"
coverage_by_id[P391]["source_line_ranges"] = "L110-124"
coverage_by_id[P391]["note"] = (
    "Printed p.391 (PDF physical page 6) read against the page image. Closes Ranuzzi's 31 January 1708 letter, "
    "including its marginal Crespi identification and Caldari/picture reference; processes Appendix 5 lines 114-124 "
    "on Smith's 1762 sale, the 1770 picture list, unresolved alternatives, 1761 will and failed earlier negotiations. "
    "Quoted archival materials and cited publications were not independently consulted."
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
    print("applied p.391 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(new_candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.390: reviewed/partial -> reviewed/complete; p.391: queued/pending -> reviewed/complete")
    print("resolved p.390 Spanish-painter role to Crespi through the p.391 marginal note and Chapter 8 cross-reference")
