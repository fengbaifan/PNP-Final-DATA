#!/usr/bin/env python3
"""Controlled S2 migration for Appendix 4, printed p.390."""

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
P235_BODY = "chp-8:08_CHP-8_sec_ii:l291-301"
P235_NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
BACKUP_SUFFIX = ".bak-s2-chp19-p390-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the reviewed S2 migration")
parser.add_argument("--repair-coverage-format", action="store_true", help="repair the p.390 reviewed line-range notation")
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

if args.repair_coverage_format:
    row = coverage_by_id.get(P390)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != ("reviewed", "partial", "L87-L107"):
        raise SystemExit(f"unexpected p.390 coverage state; refusing format repair: {row}")
    row["source_line_ranges"] = "L87-107"
    if args.apply:
        backup = coverage_path.with_name(coverage_path.name + ".bak-s2-chp19-p390-coverage-format-20261004")
        if backup.exists():
            raise SystemExit(f"backup already exists; refusing overwrite: {backup.name}")
        shutil.copy2(coverage_path, backup)
        write_csv(coverage_path, coverage_fields, coverage)
        print(f"repaired p.390 coverage span; backup: {backup.name}")
    else:
        print("DRY RUN: p.390 coverage source_line_ranges L87-L107 -> L87-107; no files written")
    raise SystemExit(0)

if P390 not in segment_by_id or P390 not in coverage_by_id:
    raise SystemExit(f"missing S0 or S2 row: {P390}")
if (coverage_by_id[P390]["disposition"], coverage_by_id[P390]["migration_status"]) != ("queued", "pending"):
    raise SystemExit(f"p.390 must be queued/pending before migration: {coverage_by_id[P390]}")


def read_segment(segment_id):
    row = segment_by_id[segment_id]
    lines = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[row["line_start"] - 1:row["line_end"]])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != row["sha256"]:
        raise SystemExit(f"segment hash mismatch: {segment_id}")
    return text, lines


text390, source_lines = read_segment(P390)
text235_body, ch8_lines = read_segment(P235_BODY)
text235_notes, _ = read_segment(P235_NOTES)


def quote(first_line, last_line):
    return "\n".join(source_lines[first_line - 1:last_line])


new_candidate_specs = [
    ("cand-10798", "Two background paintings (sfondi) for Canon Marucelli sent in May 1706", "work", 93,
     "The 1 and 8 May 1706 letters describe two sfondi for Canon Marucelli, sent in a crate with a small picture. The letters do not name their painter or subjects; manuscript not independently consulted."),
    ("cand-10799", "Small picture packed with Canon Marucelli's two backgrounds in May 1706", "work", 93,
     "Ricci says the small picture travelled in the crate with two sfondi and that its figures were made by him; the complete authorship and subject are not stated. Keep distinct from Crespi's disputed small gallery picture of 1708."),
    ("cand-10800", "Canon Marucelli addressed in Sebastiano Ricci's 1706 correspondence (given name unresolved)", "person", 93,
     "The Appendix 4 letters call this person Sig. Canonico/Can. Marucelli. The name does not identify Francesco or Orazio; alignment with the Marucelli index candidates is deferred to S3."),
    ("cand-10801", "Small picture in the Grand Prince's gallery claimed by Crespi against an attribution to Tintoretto", "work", 102,
     "In a 26 February 1708 letter Crespi says another person offered Tintoretto as the author and Crespi claimed the picture as his own. No title or independent authorship verification is supplied; distinct from the 1706 small picture in cand-10799."),
    ("cand-10802", "Unidentified Spanish painter referred to in Ranuzzi's letter of 31 January 1708", "person", 107,
     "The p.390 letter begins by referring to lo Spagnuolo Pittore; its sentence continues on p.391. Name and identity are pending completion of that continuation."),
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
        "candidate_source_ref": f"{P390}#L{line}",
    }
    candidates.append(row)
    candidate_by_id[cid] = row
    existing_keys.add(key)

# Type index candidates only where this passage makes their object type explicit.
for cid, kind in {
    "cand-0873": "person", "cand-1554": "person", "cand-1611": "person",
    "cand-1617": "person", "cand-2096": "person", "cand-2149": "person",
    "cand-2154": "person", "cand-2179": "work", "cand-2186": "work",
    "cand-2627": "person", "cand-7962": "work", "cand-7963": "place",
    "cand-7983": "work", "cand-7974": "archive", "cand-7975": "archive",
    "cand-7976": "archive", "cand-8015": "archive", "cand-8016": "archive",
}.items():
    row = candidate_by_id.get(cid)
    if not row:
        raise SystemExit(f"expected candidate missing: {cid}")
    if row.get("suggested_type") and row["suggested_type"] != kind:
        raise SystemExit(f"candidate type conflict for {cid}: {row['suggested_type']} != {kind}")
    row["suggested_type"] = kind

# Correct the previously OCR-derived locator using both printed page images.
letter_500 = candidate_by_id.get("cand-7976")
if not letter_500 or letter_500.get("canonical_name") != "Archivio Mediceo, Filza 5903, Letter 200 (1706-05-08)":
    raise SystemExit("expected prior Letter 200 candidate not found; inspect before applying")
letter_500["canonical_name"] = "Archivio Mediceo, Filza 5903, Letter 500 (1706-05-08)"
letter_500["detail"] = (
    "The 8 May 1706 letter is cited in Chapter 8 p.235 note 5 and reproduced in Appendix 4 p.390. "
    "Both printed page images read No. 500; the Chapter 8 OCR says 'zoo'. The manuscript itself was not independently consulted."
)
candidate_by_id["cand-7974"]["detail"] = (
    "Archivio Mediceo, Filza 5903, containing the 1 May 1706 Letter 197 and 8 May 1706 Letter 500 "
    "as cited in Chapter 8 p.235 and transcribed in Appendix 4 p.390; manuscripts not independently consulted."
)
candidate_by_id["cand-7975"]["detail"] = (
    "The 1 May 1706 letter is cited in Chapter 8 p.235 note 4 and reproduced in Appendix 4 p.390. "
    "Printed locator: Archivio Mediceo, Filza 5903, No. 197; manuscript not independently consulted."
)
candidate_by_id["cand-8015"]["detail"] = (
    "Crespi's 26 February 1708 letter is cited in Chapter 8 p.237 note 1 and transcribed in Appendix 4 p.390 "
    "as Archivio Mediceo, Filza 5904, No. 22; manuscript not independently consulted."
)
candidate_by_id["cand-8016"]["detail"] = (
    "The letter of introduction is cited in Chapter 8 p.237 note 2 and begins in Appendix 4 p.390 as a "
    "31 January 1708 letter from Vincenzo Ranuzzi, Filza 5897, No. 183. Its text continues on p.391; manuscript not independently consulted."
)
candidate_by_id["cand-7962"]["detail"] = (
    "The two landscapes are in the first crate described in the 1 May and 8 May 1706 letters. "
    "Chapter 8 p.235 identifies the nephew as Marco; titles and present locations are not given."
)
candidate_by_id["cand-7983"]["detail"] = (
    "The 1 and 8 May 1706 letters describe the two crates and their contents: two landscapes by Ricci's nephew, "
    "two sfondi for Canon Marucelli, and a small picture. The appendix transcription was consulted; manuscripts were not."
)
candidate_by_id["cand-7963"]["detail"] = (
    "The 1 May letter calls it the museum room commanded by Ferdinand; the 8 May reply says it was not ready and "
    "Ricci should wait. Chapter 8 p.235 locates the proposed room at Poggio a Caiano. Its identity with later galleries remains unestablished."
)
candidate_by_id["cand-2186"]["detail"] = (
    "Ricci says he is also committed to paint another room for Canon Marucelli (Appendix 4 p.390). "
    "Chapter 8 p.235 reports Ricci's decorations in the Marucelli palace; this individual room is not identified further."
)

correction_statement = next((row for row in statements if row.get("statement_id") == "st-chp8-p235-note5-letter200"), None)
if not correction_statement:
    raise SystemExit("expected Chapter 8 note 5 statement is missing")
q = correction_statement["qualifiers"]
if correction_statement.get("predicate") != "footnote_cites_letter_200" or "Letter 200" not in q.get("claim", ""):
    raise SystemExit("Chapter 8 note 5 statement changed from expected prior locator")
correction_statement["predicate"] = "footnote_cites_letter_500"
q["claim"] = "Haskell cites Letter 500 of 8 May 1706 in Archivio Mediceo, Filza 5903, published in Appendix 4."
q["qualification"] = (
    "This is a citation locator. The Appendix 4 transcription and Chapter 8 p.235 page image both read No. 500; "
    "the OCR form 'zoo' is corrected to 500. The archival manuscript itself was not independently consulted."
)
q["ocr_corrections"] = [{"source_line": 434, "ocr": "No. zoo", "print": "No. 500", "basis": "CHP-8.pdf physical page 41"}]
correction_statement["object_candidate_id"] = "cand-7976"

new_mentions = []
mention_ids = {row["mention_id"] for row in mentions}


def add_mention(ordinal, cid, surface, note="", occurrence=0):
    mid = f"m-chp19-p390-{ordinal:03d}"
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    if cid not in candidate_by_id or candidate_by_id[cid]["status"] != "open":
        raise SystemExit(f"mention targets missing or excluded candidate: {cid}")
    start = -1
    cursor = 0
    for _ in range(occurrence + 1):
        start = text390.find(surface, cursor)
        if start < 0:
            raise SystemExit(f"surface not found in p.390 segment: {surface!r}")
        cursor = start + 1
    end = start + len(surface)
    if text390[start:end] != surface:
        raise SystemExit(f"span mismatch for {mid}")
    new_mentions.append({
        "mention_id": mid, "segment_id": P390, "candidate_id": cid,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })
    mention_ids.add(mid)


mention_specs = [
    ("cand-2154", "Sebastiano Ricci", "Person named in the Appendix 4 heading.", 0),
    ("cand-0873", "G. M. Crespi", "Crespi candidate whose S1 subentry covers this appendix and his relation with Ferdinand."),
    ("cand-1617", "Grand Prince", "The person named in the Appendix 4 heading and in the Ricci letter context."),
    ("cand-1617", "Ferdinand of Tuscany", "Continuation of the title's Grand Prince identification."),
    ("cand-2154", "Sebastiano Ricci", "Writer named in the 1 May 1706 letter caption.", 1),
    ("cand-7975", "Letter from Sebastiano Ricci of I May 1706 in Archivio Mediceo, Filza 5903, No. 197", "Appendix 4 printed letter caption; its locator is No. 197."),
    ("cand-7974", "Archivio Mediceo, Filza 5903", "Holding locator for the 1 May and 8 May 1706 letters.", 0),
    ("cand-1617", "A. V. Reale", "Honorific reference to the Grand Prince in Ricci's letter."),
    ("cand-7983", "due cassette", "The two crates sent by Ricci; their contents are specified in the same letter."),
    ("cand-2149", "mio Nipote", "The letter itself says only 'my nephew'; Chapter 8 p.235 identifies this nephew as Marco."),
    ("cand-7962", "due paesi", "Two landscapes in the first crate; Marco is identified through Chapter 8 p.235."),
    ("cand-10800", "Sig.r Canonico Marucelli", "Canon named as recipient of the two sfondi; given name remains unresolved."),
    ("cand-10798", "due sfondi", "Two background paintings for Canon Marucelli in the second crate."),
    ("cand-10799", "un altro picciolo", "Small picture packed with the two sfondi."),
    ("cand-1617", "V.A.R.", "Abbreviation referring to the Grand Prince in the Ricci letter."),
    ("cand-2154", "da me", "First-person attribution to Ricci for the figures in the small picture."),
    ("cand-2149", "dal Paesista", "Role linked provisionally to Marco, the named landscape-painter nephew in Chapter 8 p.235; the phrase's scope is uncertain."),
    ("cand-1617", "all’altezza vostra", "Honorific address to the Grand Prince."),
    ("cand-7963", "stanza del museo", "The room Ferdinand had commanded Ricci to paint; Chapter 8 p.235 links the project to Poggio a Caiano."),
    ("cand-2186", "un altra stanza", "A separate room Ricci says he has undertaken to paint for Canon Marucelli."),
    ("cand-10800", "Sig. Can Marucelli", "Canon Marucelli named as the recipient of a separate room decoration."),
    ("cand-2154", "Sebastiano Ricci", "Addressee of the 8 May 1706 reply.", 2),
    ("cand-7974", "Archivio Mediceo, Filza 5903", "Holding locator repeated in the 8 May letter caption.", 1),
    ("cand-7976", "No. 500", "Printed locator for the 8 May 1706 letter; confirmed on both p.235 and p.390 page images."),
    ("cand-7983", "due Cassette", "The two crates whose receipt Ferdinand confirms."),
    ("cand-7962", "due Paesi", "Two landscapes in the crate; the letter calls them the nephew's."),
    ("cand-2149", "suo Nipote", "Ferdinand's reference to Ricci's nephew; Chapter 8 p.235 names him Marco."),
    ("cand-10800", "Canonico Marucelli", "Canon Marucelli who is to receive the two sfondi.", 1),
    ("cand-10799", "l’altro piccolo Quadro", "The small picture found in the crate; no painter or subject is given here."),
    ("cand-1617", "V.S.R.", "Honorific reference to the Grand Prince, identified from the Chapter 8 cross-reference."),
    ("cand-7963", "Stanza del Museo", "The museum room whose decoration Ferdinand says is not yet ready to proceed."),
    ("cand-0873", "Crespi", "Writer named in the 26 February 1708 letter caption."),
    ("cand-8015", "Archivio Mediceo, Filza 5904, No. 22", "Locator for Crespi's letter of 26 February 1708."),
    ("cand-1611", "V.ra Altezza Ser.ma Reale", "Crespi's honorific address to Ferdinand."),
    ("cand-1611", "Altezza V.S.R.", "Crespi's reference to Ferdinand in the letter body."),
    ("cand-10801", "quadro picolo", "A separate small picture in Ferdinand's gallery, not the 1706 shipment picture."),
    ("cand-2627", "Tintoreti", "The letter's printed name for the artist whom an unnamed person offered as the picture's author."),
    ("cand-0873", "di mia mano", "Crespi's own authorship claim; not an independent attribution decision."),
    ("cand-2179", "l’opere del Sig. Sebastiano Ricci", "Group of Ricci works Crespi says he saw and praised in Ferdinand's gallery."),
    ("cand-2154", "Sebastiano Ricci", "Artist named inside the works phrase.", 3),
    ("cand-0873", "Giuseppe Maria Crespi", "Printed signature at the end of the 26 February 1708 letter."),
    ("cand-2096", "Vincenzo Ranuzzi", "Writer named in the 31 January 1708 letter caption."),
    ("cand-8016", "Filza 5897, No. 183", "Archival locator of the letter of introduction cited in Chapter 8 p.237 note 2."),
    ("cand-1611", "Serenissima Altezza Reale", "Salutation to Ferdinand at the beginning of Ranuzzi's letter."),
    ("cand-10802", "lo Spagnuolo Pittore", "Unidentified Spanish painter introduced in the letter; its sentence continues on p.391."),
]
for i, (cid, surface, note, *rest) in enumerate(mention_specs, start=1):
    occurrence = rest[0] if rest else 0
    add_mention(i, cid, surface, note, occurrence)


def statement(statement_id, first, last, subject, object_, predicate, claim, speaker, text_layer,
              qualification, candidates, date=None, relation=False, **extra):
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 390,
        "pdf_physical_page": 5, "claim": claim, "speaker": speaker,
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": candidates, "relation_candidate": relation,
        "cited_material_not_independently_consulted": True,
    }
    if date:
        qualifiers["date"] = date
    qualifiers.update(extra)
    return {
        "statement_id": statement_id, "segment_id": P390,
        "subject_candidate_id": subject, "object_candidate_id": object_,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(first, last),
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "origin": "book",
    }


new_statements = [
    statement(
        "st-chp19-p390-ricci-shipment", 91, 94, "cand-2154", "cand-7983",
        "ricci_sent_two_crates_for_ferdinand_and_marucelli",
        "Ricci says he sent two crates to Ferdinand: one held two landscapes by his nephew, and the other held two sfondi for Canon Marucelli plus a small picture. He asks that the items be placed in one of Ferdinand's villas and frames them as a gift.",
        "Sebastiano Ricci", "quoted archival letter, Archivio Mediceo, Filza 5903, No. 197",
        "The letter says 'my nephew'; Chapter 8 p.235 identifies him as Marco and describes the landscapes as for the Marucelli. The small picture is in the crate with the sfondi. A lacuna remains in line 94; the manuscript was not independently consulted.",
        ["cand-2154", "cand-7975", "cand-7974", "cand-7983", "cand-7962", "cand-2149", "cand-10798", "cand-10799", "cand-10800", "cand-1617"],
        date="1706-05-01", relation=True,
        reported_addressee="Grand Prince Ferdinand de' Medici",
        cross_reference_segments=[P235_BODY, P235_NOTES],
        ocr_corrections=[{"source_line": 94, "ocr": "ima Villa", "print": "una Villa", "basis": "CHP-19Appendix.pdf physical page 5"}],
    ),
    statement(
        "st-chp19-p390-ricci-small-picture-figures", 94, 94, "cand-2154", "cand-10799",
        "ricci_claimed_figures_in_small_picture_and_landscape_painter_made_others",
        "Ricci says he painted the figures in the small picture and that the others were made by the landscape painter.",
        "Sebastiano Ricci", "quoted archival letter, Archivio Mediceo, Filza 5903, No. 197",
        "The scope of 'the others' is unclear. Chapter 8 p.235 identifies Ricci's nephew Marco as the landscape painter, but this wording does not specify which other figures it covers; no complete authorship claim is inferred.",
        ["cand-2154", "cand-10799", "cand-2149", "cand-7962", "cand-7975"],
        date="1706-05-01", relation=True,
        cross_reference_segments=[P235_BODY],
    ),
    statement(
        "st-chp19-p390-ricci-museum-room-plan", 95, 95, "cand-2154", "cand-7963",
        "ricci_expected_to_paint_ferdinands_museum_room",
        "Ricci hopes to come in early June and paint the museum room Ferdinand had commanded him to paint.",
        "Sebastiano Ricci", "quoted archival letter, Archivio Mediceo, Filza 5903, No. 197",
        "This is a prospective commission, not a completed room decoration. Chapter 8 p.235 identifies the proposed room with Ferdinand's gallery of Venetian pictures at Poggio a Caiano.",
        ["cand-2154", "cand-7963", "cand-7975", "cand-1617"],
        date="1706-05-01", relation=True,
        cross_reference_segments=[P235_BODY, P235_NOTES],
    ),
    statement(
        "st-chp19-p390-ricci-marucelli-room-commitment", 96, 96, "cand-2154", "cand-2186",
        "ricci_committed_to_paint_another_room_for_canon_marucelli",
        "Ricci says he has also committed himself to paint another room for Canon Marucelli.",
        "Sebastiano Ricci", "quoted archival letter, Archivio Mediceo, Filza 5903, No. 197",
        "The letter reports an undertaking, not completion. The Canon's given name is not supplied and is kept unresolved; Chapter 8 p.235 reports decorations for the Marucelli palace but does not identify this individual room.",
        ["cand-2154", "cand-2186", "cand-10800", "cand-7975"],
        date="1706-05-01", relation=True,
        cross_reference_segments=[P235_BODY, P235_NOTES],
    ),
    statement(
        "st-chp19-p390-ferdinand-received-crates", 98, 98, "cand-1617", "cand-7983",
        "ferdinand_confirmed_receipt_of_crates_and_arranged_marucelli_delivery",
        "The 8 May reply says both crates arrived in good condition, repeats that the crates held the nephew's two landscapes, two sfondi for Canon Marucelli and the small picture, and says Ferdinand ordered the sfondi to be delivered to the Canon.",
        "Grand Prince Ferdinand (identified by the Chapter 8 p.235 cross-reference)", "quoted archival letter, Archivio Mediceo, Filza 5903, No. 500",
        "The letter does not identify the Canon by given name or identify the small picture's painter. Chapter 8 p.235 identifies the nephew as Marco. The printed locator is No. 500, not 200.",
        ["cand-1617", "cand-7976", "cand-7974", "cand-7983", "cand-7962", "cand-2149", "cand-10798", "cand-10799", "cand-10800"],
        date="1706-05-08", relation=True,
        cross_reference_segments=[P235_BODY, P235_NOTES],
        ocr_corrections=[{"source_line": 98, "ocr": "nell’altra E due Sfondi", "print": "nell’altra li due Sfondi", "basis": "CHP-19Appendix.pdf physical page 5"}],
    ),
    statement(
        "st-chp19-p390-ferdinand-defers-room", 98, 99, "cand-1617", "cand-7963",
        "ferdinand_deferred_museum_room_and_told_ricci_to_wait",
        "Ferdinand says the museum room is not yet ready to be worked on because he had been ill and travelled to Pisa and then to a villa; he confirms Ricci is still intended to paint it when the time comes and says he will notify him, so Ricci may refrain from travelling for this room for now.",
        "Grand Prince Ferdinand (identified by the Chapter 8 p.235 cross-reference)", "quoted archival letter, Archivio Mediceo, Filza 5903, No. 500",
        "The passage describes a deferred project, not completed work. The letter names no specific villa; the room's location at Poggio a Caiano is given in Chapter 8 p.235.",
        ["cand-1617", "cand-7963", "cand-7976", "cand-2154"],
        date="1706-05-08", relation=True,
        cross_reference_segments=[P235_BODY, P235_NOTES],
    ),
    statement(
        "st-chp19-p390-crespi-return-and-thanks", 102, 104, "cand-0873", "cand-1611",
        "crespi_reported_returning_home_and_thanked_ferdinand",
        "Crespi reports his arrival in patria and thanks Ferdinand for the favors granted to him, saying he will preserve their memory.",
        "Giuseppe Maria Crespi", "quoted archival letter, Archivio Mediceo, Filza 5904, No. 22",
        "The note in Chapter 8 p.237 identifies this as Crespi's letter to Ferdinand; the passage does not specify which places he passed through.",
        ["cand-0873", "cand-1611", "cand-8015"],
        date="1708-02-26", relation=False,
        cross_reference_segments=[P235_NOTES],
    ),
    statement(
        "st-chp19-p390-crespi-claims-small-picture", 102, 102, "cand-0873", "cand-10801",
        "crespi_claimed_small_gallery_picture_after_tintoretto_attribution_was_reported",
        "Crespi says that after he asked who painted a small picture in Ferdinand's gallery, someone told him it was by Tintoretto; Crespi then says he can truthfully state that it was by his own hand.",
        "Giuseppe Maria Crespi", "quoted archival letter, Archivio Mediceo, Filza 5904, No. 22",
        "This is Crespi's self-attribution and a report of an unidentified person's prior attribution, not an independent authorship finding. This 1708 picture is distinct from the small picture shipped in 1706.",
        ["cand-0873", "cand-10801", "cand-2627", "cand-1611", "cand-8015"],
        date="1708-02-26", relation=True,
        reported_attribution="Tintoretto, as stated by an unidentified person",
        cross_reference_segments=[P235_NOTES],
    ),
    statement(
        "st-chp19-p390-crespi-praises-ricci", 102, 102, "cand-0873", "cand-2179",
        "crespi_reported_seeing_and_praised_riccis_works",
        "Crespi says he saw Sebastiano Ricci's works with great satisfaction and praises their spirit and skill.",
        "Giuseppe Maria Crespi", "quoted archival letter, Archivio Mediceo, Filza 5904, No. 22",
        "This preserves Crespi's evaluation; it is not an independently verified quality judgment. The letter identifies a group of works but gives no titles.",
        ["cand-0873", "cand-2179", "cand-2154", "cand-8015"],
        date="1708-02-26", relation=False,
        cross_reference_segments=[P235_NOTES],
    ),
    statement(
        "st-chp19-p390-ranuzzi-letter-heading", 105, 107, "cand-2096", "cand-8016",
        "appendix_identifies_ranuzzi_letter_of_introduction_and_begins_its_text",
        "The Appendix 4 heading identifies a letter from Vincenzo Ranuzzi dated 31 January 1708, Archivio Mediceo, Filza 5897, No. 183; the text begins with a formal address and refers to an unidentified Spanish painter before continuing on p.391.",
        "Printed Appendix 4 letter caption and opening lines", "quoted archival letter, continued across pages",
        "Only the heading and opening fragment are covered by this segment. The Spanish painter's name and the letter's full purpose remain pending p.391.",
        ["cand-2096", "cand-8016", "cand-1611", "cand-10802"],
        date="1708-01-31", relation=False,
        continuation_status="open", cross_reference_segments=[P235_NOTES],
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
    if row["original_quote"] not in (text390 if row["segment_id"] == P390 else ""):
        raise SystemExit(f"statement quote not contained in p.390 segment: {row['statement_id']}")

mentions.extend(new_mentions)
statements.extend(new_statements)
coverage_by_id[P390]["disposition"] = "reviewed"
coverage_by_id[P390]["migration_status"] = "partial"
coverage_by_id[P390]["source_line_ranges"] = "L87-107"
coverage_by_id[P390]["note"] = (
    "Printed p.390 (PDF physical page 5) read against the page image. Processes the two 1706 Ricci/Ferdinand letters "
    "and Crespi's 26 February 1708 letter; the 31 January Ranuzzi letter begins at L105 and continues on p.391, "
    "so this S0 segment remains partial. Chapter 8 p.235 image confirms No. 500 for the 8 May letter; the earlier "
    "No. 200 OCR correction was erroneous and is corrected in the statement/candidate records. Manuscripts not independently consulted."
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
    print("applied p.390 S2 migration; backups:")
    for path in files_to_backup:
        print(f"  {path.name}{BACKUP_SUFFIX}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates: {len(new_candidate_specs)}; mentions: {len(new_mentions)}; statements: {len(new_statements)}")
    print("p.390: queued/pending -> reviewed/partial; Ranuzzi letter continuation remains for p.391")
    print("corrected Chapter 8 note 5 / cand-7976 locator: No. 200 -> No. 500, supported by both printed page images")
