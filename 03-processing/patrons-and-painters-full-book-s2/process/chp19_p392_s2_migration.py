#!/usr/bin/env python3
"""Controlled S2 migration for Appendix 5, printed p.392."""

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
P391 = "chp-19:19_CHP-19Appendix:l109-124"
P393 = "chp-19:19_CHP-19Appendix:l140-155"
P10_ADAM = "chp-10:10_CHP-10_intro:l491-634"
BACKUP_SUFFIX = ".bak-s2-chp19-p392-20261004"

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

if any(seg not in segment_by_id or seg not in coverage_by_id for seg in (P391, P392, P393)):
    raise SystemExit("missing S0 or S2 row for p.391–393 sequence")
if (coverage_by_id[P391]["disposition"], coverage_by_id[P391]["migration_status"]) != ("reviewed", "complete"):
    raise SystemExit("p.391 must be complete before migrating p.392")
if (coverage_by_id[P392]["disposition"], coverage_by_id[P392]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.392 must be queued/pending before migration: {coverage_by_id[P392]}")
if coverage_by_id[P393]["migration_status"] != "pending":
    raise SystemExit(f"p.393 should remain pending until p.392 is reviewed: {coverage_by_id[P393]}")

segment = segment_by_id[P392]
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text392 = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
if hashlib.sha256(text392.encode("utf-8")).hexdigest() != segment["sha256"]:
    raise SystemExit("p.392 S0 segment hash mismatch")
line_offset = {}
offset = 0
parts = text392.split("\n")
for line_number, part in zip(range(segment["line_start"], segment["line_end"] + 1), parts):
    line_offset[line_number] = offset
    offset += len(part) + 1


def quote(first_line, last_line):
    return "\n".join(source_lines[first_line - 1:last_line])


new_candidate_specs = [
    ("cand-10808", "Gradenigo, p.82 (Appendix 5 p.392 citation locator)", "archive", 128,
     "Citation locator for a Venetian report about Smith's plans in 1761. The cited source, title, edition, and page were not independently consulted."),
    ("cand-10809", "Moschini, 1806, volume III, p.51 (Appendix 5 p.392 citation locator)", "archive", 129,
     "Citation locator as printed in Haskell's discussion of the disputed disposition of Smith's pictures. Page image reads Moschini at p.392 L129; cited source not independently consulted."),
    ("cand-10810", "Giovanni Volpato letter to Remondini, 22 April 1766 (Epistolario Trivellini, XXX, 10)", "archive", 133,
     "Haskell quotes a letter located at Biblioteca Civica, Bassano, Epistolario Trivellini, XXX, 10. The manuscript was not independently consulted; the shelfmark is transcribed from the page image."),
    ("cand-10811", "Joseph Smith letter to an unidentified correspondent in Bologna, 9 April 1768 (MS B.153, No.92)", "archive", 134,
     "Printed in Appendix 5 from Biblioteca Comunale, Bologna, MS B.153, No.92; Haskell credits Denis Mahon for access. The manuscript and the correspondent's identity were not independently consulted."),
    ("cand-10812", "Note of the Gennari collection of paintings and drawings referred to in Smith's 1768 letter", "archive", 137,
     "The 1768 letter says Smith received and returned a note/list of the Gennari collection for clearer copying. The note itself is not reproduced or independently consulted."),
    ("cand-10813", "Unspecified paintings and drawings in the Gennari collection discussed in 1768", "work", 137,
     "Collection-level group named in Smith's letter; no individual works, artist named Gennari, owner, or completed purchase are established by this passage."),
    ("cand-10814", "Unidentified owner of the Gennari collection discussed in Smith's 1768 letter", "person", 138,
     "The quoted letter refers only to 'il Proprietario'. No name, identity, or completed transaction is given."),
    ("cand-10815", "Unidentified correspondent of Joseph Smith in Bologna, 1768", "person", 135,
     "Haskell describes Smith's 9 April 1768 letter as addressed to an unknown correspondent in Bologna. The person is not named or independently identified."),
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
        "candidate_source_ref": f"{P392}#L{line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

mention_specs = [
    ("cand-2471", "Smith", 128, "Joseph Smith; the passage reports possible plans rather than an accomplished move or sale.", 0),
    ("cand-2719", "Venice", 128, "City named as Smith's residence before the contemplated move.", 0),
    ("cand-8983", "England", 128, "Destination Smith was reportedly considering; the passage does not say that he moved.", 0),
    ("cand-9171", "his palace", 128, "Smith's palace, which Venetian reports said might be sold.", 0),
    ("cand-9177", "his library", 128, "Smith's library mentioned among the property reportedly considered for sale.", 0),
    ("cand-8507", "Gradenigo", 128, "Surname-only author cited for a Venetian report.", 0),
    ("cand-10808", "p. 82", 128, "Gradenigo page locator; source not independently consulted.", 0),
    ("cand-8660", "Parker", 128, "Author cited for Smith's reported plans and collection statement.", 0),
    ("cand-8651", "p. 62", 128, "Parker page locator; the publication was not independently consulted.", 0),
    ("cand-8651", "p. 61", 128, "Parker page locator for the quoted phrase about the collection.", 0),
    ("cand-0011", "James", 128, "James Adam, identified by the matching dated letter cited in Chapter 10 p.310 note 5.", 0),
    ("cand-0012", "Robert Adam", 128, "Robert Adam, recipient of the 20 August 1760 letter.", 0),
    ("cand-2471", "Smith", 128, "Smith is the person discussed in the James Adam letter.", 1),
    ("cand-9558", "Fleming, 1962, p. 270", 128, "Citation locator for the James-to-Robert Adam letter; not independently consulted.", 0),
    ("cand-1709", "Meschini", 129, "Raw OCR reads Meschini; the page image reads Moschini. Keep this printed-name reading distinct from other Meschini candidates pending S3.", 0),
    ("cand-10809", "p. 51", 129, "Citation locator for the 1806 volume III passage; not independently consulted.", 0),
    ("cand-1141", "George III", 130, "King named in the cited account of pictures taken to England.", 0),
    ("cand-1709", "Moschini", 131, "Narrative spelling on the page image; its relation to the p.392 citation and other Meschini/Moschini candidates remains for S3.", 0),
    ("cand-0581", "Rosalba Carriera", 132, "Artist named among those most represented in the pictures sold to the King.", 0),
    ("cand-0498", "Canaletto", 132, "Artist named among those most represented in the pictures sold to the King.", 0),
    ("cand-2879", "Zuccarelli", 132, "Surname as printed; the passage does not expand the given name.", 0),
    ("cand-1141", "the King", 132, "The King refers to George III in the account of the sale.", 0),
    ("cand-2471", "Smith’s activities", 132, "Joseph Smith's post-1762 artistic activity is the subject of Haskell's inference.", 0),
    ("cand-2790", "engraver Giovanni Volpato", 132, "Volpato is described as the engraver who wrote to Remondini.", 0),
    ("cand-2122", "publisher Remondini", 132, "Remondini is described as the publisher addressed by Volpato.", 0),
    ("cand-10810", "Epistolario Trivellini, XXX, io", 133, "Raw OCR shelfmark; the page image reads XXX, 10. The letter was not independently consulted.", 0),
    ("cand-10810", "22 April 1766", 133, "Date assigned to the quoted Volpato letter by Haskell.", 0),
    ("cand-2471", "Smit", 134, "Italian letter's printed spelling for Smith; preserve as printed.", 0),
    ("cand-1422", "Londra", 134, "Italian place-name for London in Volpato's quoted letter.", 0),
    ("cand-2471", "Smith", 134, "Smith as the writer of the Bologna letter; this is not a claim that he bought the collection.", 0),
    ("cand-10815", "unknown correspondent", 134, "Unidentified addressee of the 9 April 1768 letter.", 0),
    ("cand-3398", "Bologna", 134, "City given for the unidentified correspondent.", 0),
    ("cand-10811", "MS. B.153", 134, "Manuscript locator for Smith's 1768 letter; not independently consulted.", 0),
    ("cand-1494", "Denis Mahon", 135, "Haskell credits Mahon with making the letter available for publication.", 0),
    ("cand-10811", "9 Aprile 1768", 136, "Date and place heading of Smith's letter; the letter continues on p.393.", 0),
    ("cand-2719", "Venezia", 136, "Italian name for Venice in the letter heading.", 0),
    ("cand-10812", "nota della", 137, "The note/list of the Gennari collection referred to in the letter.", 0),
    ("cand-10813", "raccolta Gennari", 137, "Collection-level group; its individual contents and owner are not identified.", 0),
    ("cand-10813", "depinti et desegne", 137, "Paintings and drawings described as the contents of the Gennari collection.", 0),
    ("cand-10814", "Proprietario", 138, "Unidentified owner of the collection; do not merge with the unknown correspondent.", 0),
]

new_mentions = []
mention_ids = {row["mention_id"] for row in mentions}
for ordinal, (cid, surface, source_line, note, occurrence) in enumerate(mention_specs, start=1):
    mid = f"m-chp19-p392-{ordinal:03d}"
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention targets missing or excluded candidate: {cid}")
    local_line = source_lines[source_line - 1]
    start_in_line = -1
    cursor = 0
    for _ in range(occurrence + 1):
        start_in_line = local_line.find(surface, cursor)
        if start_in_line < 0:
            raise SystemExit(f"surface not found on source line {source_line}: {surface!r}")
        cursor = start_in_line + 1
    start = line_offset[source_line] + start_in_line
    end = start + len(surface)
    if text392[start:end] != surface:
        raise SystemExit(f"span mismatch for {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": P392, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_ids.add(mid)


def statement(statement_id, first, last, subject, object_, predicate, claim, speaker, text_layer,
              qualification, candidates, date=None, relation=False, **extra):
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 392,
        "pdf_physical_page": 7, "claim": claim, "speaker": speaker,
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": candidates, "relation_candidate": relation,
        "cited_material_not_independently_consulted": True,
    }
    if date:
        qualifiers["date"] = date
    qualifiers.update(extra)
    return {
        "statement_id": statement_id, "segment_id": P392,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(first, last),
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    }


new_statements = [
    statement(
        "st-chp19-p392-transition-only-certain-knowledge", 127, 127, "cand-2447", None,
        "haskell_said_prior_account_was_only_certain_knowledge_before_conflicting_evidence",
        "Haskell says the preceding account is the only certain knowledge about Smith's picture collection and introduces further conflicting evidence.",
        "Haskell", "authorial transition",
        "This explicitly continues the unresolved alternatives stated on p.391; it does not choose between them.",
        ["cand-2447", "cand-10806"], cross_reference_segments=[P391],
        cross_reference_statement_ids=["st-chp19-p391-smith-sale-hypotheses-unresolved"],
    ),
    statement(
        "st-chp19-p392-smith-1761-relocation-and-reports", 128, 128, "cand-2447", "cand-9171",
        "haskell_reported_smiths_possible_1761_move_and_venetian_reports_of_a_palace_sale",
        "Haskell says Smith was considering leaving Venice for England in 1761; Venetian reports said he was preparing to sell his palace with its library, print collections, and other valuables. Parker is cited for a later statement that Smith planned to return to England and for his phrase 'this whole Collection, the work of my life'.",
        "Haskell reporting Venetian claims and Parker-cited documents", "authorial report with citations",
        "These are plans and contemporary reports, not proof that Smith moved or sold the whole collection. Gradenigo and Parker citations were not independently consulted.",
        ["cand-2447", "cand-2719", "cand-8983", "cand-9171", "cand-9177", "cand-8507", "cand-10808", "cand-8660", "cand-8651"],
        date="1761–1762", relation=True,
        ocr_corrections=[
            {"source_line": 128, "ocr": "rarità'pregevoli", "print": "rarità pregevoli", "basis": "CHP-19Appendix.pdf physical page 7."},
            {"source_line": 128, "ocr": "decided-to", "print": "decided to", "basis": "CHP-19Appendix.pdf physical page 7."},
            {"source_line": 128, "ocr": "buyexpensive", "print": "buy expensive", "basis": "CHP-19Appendix.pdf physical page 7."},
        ],
    ),
    statement(
        "st-chp19-p392-adam-1760-financial-report", 128, 128, "cand-9519", "cand-2447",
        "james_adam_told_robert_adam_smith_was_very_poor_and_might_die_bankrupt",
        "Haskell quotes James Adam's 20 August 1760 letter to Robert Adam saying Smith was very poor and might die bankrupt if he lived several more years.",
        "James Adam, as quoted by Haskell", "quoted letter mediated through Fleming",
        "The statement is a contemporary financial assessment quoted by Haskell, not proof that Smith became bankrupt. Fleming's 1962 publication and letter copy were not independently consulted.",
        ["cand-9519", "cand-0011", "cand-0012", "cand-2447", "cand-9558"],
        date="1760-08-20", relation=True,
        cross_reference_segments=[P10_ADAM],
    ),
    statement(
        "st-chp19-p392-smith-disposal-and-purchase-inferences", 128, 128, "cand-2447", None,
        "haskell_inferred_possible_disposal_but_doubted_extensive_new_picture_buying",
        "Haskell says Smith may have decided to sell all or anything valuable, while his poverty and extreme old age make it equally possible that he did not begin buying expensive pictures after 1762; he notes that Smith resumed the consulate in 1766.",
        "Haskell", "authorial inference based on cited reports",
        "Haskell marks these as competing deductions and uses 'may'; neither a complete sale nor absence of later purchases is established.",
        ["cand-2447", "cand-8651"], date="1761–1766", relation=False,
    ),
    statement(
        "st-chp19-p392-moschini-conflicting-widow-account", 129, 131, "cand-2447", "cand-10809",
        "haskell_said_1806_account_did_not_resolve_which_smith_pictures_went_to_england",
        "Haskell reports a passage attributed in the citation to Meschini/Moschini (1806, III, p.51) claiming that Smith's widow took paintings he had reserved to England; he says the later author seems unaware of Smith's sale to the King and mentions £20,000 for books and cameos only. Haskell concludes it remains unclear whether the widow took pictures retained in 1762 or pictures bought afterward.",
        "Haskell summarizing and evaluating a cited 1806 account", "authorial report with quoted Italian source",
        "The p.392 page image reads '(b) Moschini' at L129 and 'Moschini' at L131, while OCR L129 reads '(¿) Meschini'. The cited 1806 passage was not independently consulted; do not reconcile the spelling or identity with other Meschini/Moschini candidates here.",
        ["cand-2447", "cand-1709", "cand-10809", "cand-1141"],
        relation=True,
        ocr_corrections=[
            {"source_line": 129, "ocr": "(¿) Meschini", "print": "(b) Moschini", "basis": "CHP-19Appendix.pdf physical page 7."},
            {"source_line": 131, "ocr": "^20,000", "print": "£20,000", "basis": "CHP-19Appendix.pdf physical page 7."},
        ],
    ),
    statement(
        "st-chp19-p392-artists-in-1762-sale-selection-inference", 132, 132, "cand-2471", "cand-9278",
        "haskell_inferred_deliberate_selection_from_artists_familiar_to_english_buyers",
        "Haskell notes that the pictures sold to the King most fully represented the two Riccis, Rosalba Carriera, Canaletto, and Zuccarelli, artists familiar to English buyers, and says this seems to suggest deliberate selection.",
        "Haskell", "authorial inference",
        "The passage does not identify the two Riccis by given name or specify individual pictures; deliberate selection remains Haskell's inference.",
        ["cand-2471", "cand-1141", "cand-0581", "cand-0498", "cand-2879", "cand-9278"],
        date="1762", relation=True,
        ocr_corrections=[{"source_line": 132, "ocr": "- (d)", "print": "(d)", "basis": "CHP-19Appendix.pdf physical page 7."}],
    ),
    statement(
        "st-chp19-p392-post1762-source-scarcity-and-inference", 132, 132, "cand-2447", None,
        "haskell_inferred_limited_post1762_sources_made_extensive_purchases_unlikely",
        "Haskell says Smith's activities are almost never mentioned after 1762 and infers that extensive purchases are unlikely; he identifies a 1766 Volpato letter and a 1768 letter from Smith as the only references he could trace.",
        "Haskell", "authorial inference and source description",
        "This is Haskell's account of the sources he had traced, not a claim that no other records exist.",
        ["cand-2447", "cand-2790", "cand-2122", "cand-10810", "cand-10811"],
        ocr_corrections=[
            {"source_line": 132, "ocr": "come ih a letter from-the engraver", "print": "come in a letter from the engraver", "basis": "CHP-19Appendix.pdf physical page 7."},
            {"source_line": 133, "ocr": "XXX, io", "print": "XXX, 10", "basis": "CHP-19Appendix.pdf physical page 7."},
        ],
    ),
    statement(
        "st-chp19-p392-volpato-1766-letter", 133, 134, "cand-2790", "cand-2447",
        "volpato_reported_two_rametti_for_smith_and_further_items_for_london",
        "In the quoted 22 April 1766 letter to Remondini, Volpato says he has two 'Rametti' on commission for Smith, who pays seventy zecchini, and expects to make more things for him for London over a year or more.",
        "Giovanni Volpato", "quoted archival letter mediated through Haskell",
        "The manuscript was not independently consulted. 'Rametti' is retained without identifying the objects; this wording suggests work for Smith but does not establish that Smith bought the objects for his own collection.",
        ["cand-2790", "cand-2122", "cand-10810", "cand-2447", "cand-1422"],
        date="1766-04-22", relation=True,
    ),
    statement(
        "st-chp19-p392-smith-1768-letter-dealing", 134, 135, "cand-2447", "cand-10811",
        "haskell_said_1768_letter_shows_smith_dealt_in_pictures_not_necessarily_for_himself",
        "Haskell says Smith's 1768 letter to an unidentified correspondent in Bologna shows that he was dealing in pictures, even if not buying them for himself, and credits Denis Mahon with making the letter available for publication.",
        "Haskell", "authorial report introducing a quoted letter",
        "The manuscript and recipient were not independently consulted or identified; the passage expressly leaves personal collection purchase uncertain.",
        ["cand-2447", "cand-10811", "cand-10815", "cand-3398", "cand-1494"],
        date="1768-04-09", relation=True,
    ),
    statement(
        "st-chp19-p392-smith-conditional-gennari-collection-offer", 136, 138, "cand-2447", "cand-10813",
        "smith_offered_to_acquire_gennari_collection_if_owner_would_sell_at_a_discreet_price",
        "In the opening of his 9 April 1768 letter, Smith thanks the recipient for a note of the Gennari collection of paintings and drawings and says he would acquire them at a reasonable price if the owner wished to sell; he asks whether all should be offered together or separately and requests clear, legible notes.",
        "Joseph Smith", "quoted archival letter",
        "This is a conditional offer and request, not evidence of a completed purchase. The collection's individual works, the owner, and the correspondent remain unidentified; the letter continues on p.393.",
        ["cand-2447", "cand-10811", "cand-10812", "cand-10813", "cand-10814", "cand-10815", "cand-3398"],
        date="1768-04-09", relation=True, continuation_status="open",
        cross_reference_segments=[P393],
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
    if row["original_quote"] not in text392:
        raise SystemExit(f"statement quote not contained in p.392 segment: {row['statement_id']}")

mentions.extend(new_mentions)
statements.extend(new_statements)
coverage_by_id[P392]["disposition"] = "reviewed"
coverage_by_id[P392]["migration_status"] = "partial"
coverage_by_id[P392]["source_line_ranges"] = "L127-138"
coverage_by_id[P392]["note"] = (
    "Printed p.392 (PDF physical page 7) read against the page image. Processes Haskell's competing evidence about "
    "Joseph Smith's 1761–1762 plans, the attributed 1806 account, artists in the King's sale, and two post-1762 letters. "
    "Page-image corrections are recorded on statements; cited sources and archival manuscripts were not independently consulted. "
    "The 9 April 1768 letter continues on p.393, so this segment remains partial."
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
    print("applied p.392 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(new_candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.392: queued/pending -> reviewed/partial; p.393 remains pending as the continuation")
    print("preserved the conflict between the two Smith-sale explanations and the conditional 1768 offer")
