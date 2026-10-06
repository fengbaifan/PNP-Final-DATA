"""Controlled S2 migration for Chapter 8 printed page 235 and notes 1-6.

The default invocation is a read-only dry run. Source OCR is preserved; print
corrections are recorded on the statements after comparison with the page scan.
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
P235 = "chp-8:08_CHP-8_sec_ii:l291-301"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P235, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p235-20261001"


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
expected = {
    P235: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L373-429"),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")

new_candidates = [
    ("cand-7956", "Luca Giordano’s pictures on glass of The Flight into Egypt for Ferdinand", "work", 292,
     "A group of pictures is named; individual objects, number, present location, and relation to any other Flight into Egypt work are unspecified."),
    ("cand-7957", "Crucifixion with the Madonna, St John, and St Charles Borromeo (Sebastiano Ricci, 1704 commission)", "work", 295,
     "Haskell reports a 1704 commission; the work is not identified by present location in this passage."),
    ("cand-7958", "Two unnamed artists whose late work met Ferdinand’s demands", "term", 294,
     "A two-person artist group described by Haskell; the individuals are not identified on this page."),
    ("cand-7959", "Marucelli brothers, Florentine patrons of Sebastiano Ricci", "family", 296,
     "The text identifies brothers collectively but names only Francesco; the other brother or brothers remain unresolved."),
    ("cand-7960", "S. Francesco de’ Macci (house associated with the nuns from whom Ferdinand bought Madonna delle Arpie)", "", 296,
     "The passage does not resolve whether the name denotes a church, convent, or other institution; do not force a type."),
    ("cand-7961", "Ferdinand’s own gallery where Madonna delle Arpie was kept (location unspecified)", "place", 296,
     "A gallery is named without a location; it is not assumed to be either the Pitti room or Poggio a Caiano gallery."),
    ("cand-7962", "Two small landscapes by Marco Ricci sent to Ferdinand in May 1706", "work", 298,
     "The number and artist are reported, but the landscapes have no titles, dates, or present locations here."),
    ("cand-7963", "Room in Ferdinand’s gallery of Venetian pictures at Poggio a Caiano", "place", 298,
     "A proposed room-painting location; its identity with the later favourite gallery or Farsetti’s room is not established."),
    ("cand-7964", "Ferdinand’s favourite gallery mentioned in connection with Ricci’s Allegory of the Arts", "place", 300,
     "The gallery is not named in this sentence; possible identity with the preceding Poggio gallery remains implicit."),
    ("cand-7965", "Allegory of the Arts painted by Sebastiano Ricci for Ferdinand (reported destroyed)", "work", 300,
     "Haskell reports the work as destroyed; do not identify it with the ceiling decoration described in note 6."),
    ("cand-7966", "Sebastiano Ricci’s surviving decorations for the Marucelli palace", "work", 300,
     "A group of decorations is reported to survive; individual rooms and subjects are not specified."),
    ("cand-7967", "Sebastiano Ricci’s surviving decoration for Ferdinand in a small room at the Pitti", "work", 300,
     "The decoration is not titled; the passage does not equate it with the destroyed Allegory of the Arts."),
    ("cand-7968", "Venetian market for pictures reported to Ferdinand", "term", 296,
     "A market context in Cassana’s reported information role; no specific sale or transaction is named."),
    ("cand-7969", "Luca Giordano’s visit to Grand Prince Ferdinand at Livorno in May 1702", "event", 293,
     "The date and meeting are reported by Haskell and cited letter; the letter itself was not independently consulted."),
    ("cand-7970", "Ferdinand’s two prior visits to Venice before the 1704 Ricci commission", "event", 295,
     "The visits are mentioned without dates; no more exact itinerary is inferred."),
    ("cand-7971", "Fogolari (1937), Letter 75 (1702-05-26), Grand Prince Ferdinand at Livorno", "archive", 430,
     "Locator cited in Haskell’s footnote; the letter was not independently consulted."),
    ("cand-7972", "Fogolari (1937), Letter 98 (1704-08-30)", "archive", 431,
     "Locator cited in Haskell’s footnote; the letter was not independently consulted."),
    ("cand-7973", "Fogolari (1937), Letter 99 (1704-09-20)", "archive", 431,
     "Locator cited in Haskell’s footnote; the letter was not independently consulted."),
    ("cand-7974", "Archivio Mediceo, Filza 5903", "archive", 433,
     "Archival series cited as the holding locator for Letters 197 and 200; no independent archival inspection is claimed."),
    ("cand-7975", "Archivio Mediceo, Filza 5903, Letter 197 (1706-05-01)", "archive", 433,
     "Specific letter locator cited in Haskell’s footnote and published in Appendix 4; not independently consulted."),
    ("cand-7976", "Archivio Mediceo, Filza 5903, Letter 200 (1706-05-08)", "archive", 434,
     "Specific letter locator cited in Haskell’s footnote and published in Appendix 4; not independently consulted."),
    ("cand-7977", "October 1706 exhibition referenced by Haskell", "event", 433,
     "The exhibition is referenced through p. 240 note 5; its venue and catalogue are not independently checked here."),
    ("cand-7978", "Flora by Sebastiano Ricci exhibited by Orazio Marucelli in October 1706", "work", 433,
     "The work is identified by subject and painter only; no present location or independent object identification is supplied."),
    ("cand-7979", "T. G. Farsetti’s late-eighteenth-century description of the Venetian-pictures room at Poggio", "archive", 435,
     "A descriptive source excerpt quoted through Fogolari (1937), p. 186; the underlying text was not independently consulted."),
    ("cand-7980", "Painted ceiling with allegories at Poggio a Caiano described by Farsetti", "work", 435,
     "Farsetti’s quoted description concerns a ceiling and Sister Arts allegories; identity with Ricci’s destroyed Allegory remains unresolved."),
    ("cand-7981", "Saint John named in the title of Ricci’s Crucifixion (identity not specified)", "person", 296,
     "The title gives only St John; no more specific identity is imposed."),
    ("cand-7982", "Saint Charles Borromeo", "person", 296,
     "Named in the title of Ricci’s 1704 Crucifixion."),
    ("cand-7983", "Paintings sent by Sebastiano Ricci to the Marucelli in May 1706 (group, partly unidentified)", "work", 297,
     "The source says some paintings were sent in two crates and identifies only two small Marco Ricci landscapes among them."),
    ("cand-7984", "Unspecified letters from Sebastiano Ricci to Ferdinand about pictures on the Venetian market (Fogolari 1937)", "archive", 432,
     "The note gives no letter numbers; do not merge these with Letters 98 and 99 without further evidence."),
    ("cand-7985", "Galleria mentioned as a destination for pictures moved from Poggio (identity unresolved)", "", 435,
     "Farsetti’s quoted wording capitalizes Galleria but does not establish whether this is a place, institution, or named collection."),
    ("cand-7986", "Sister Arts as an allegorical group in Farsetti’s quotation", "term", 301,
     "The phrase Arti sorelle is retained as the stated allegorical subject; no individual arts are enumerated."),
    ("cand-7987", "Ferdinand’s favourite villa mentioned with Ricci’s Allegory of the Arts (not named here)", "place", 300,
     "The villa is not named in this sentence; Poggio a Caiano is a contextual possibility, not a confirmed identification."),
    ("cand-7988", "Venetian pictures formerly in the Poggio room and later moved to Galleria and other places", "work", 435,
     "Farsetti’s quoted account describes a group of pictures, without individual titles or a complete destination list."),
]

candidate_ids = {row["candidate_id"] for row in candidate_rows}
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
    anchor_segment = NOTES if source_line >= 372 else P235
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{source_line}",
    })
    candidate_ids.add(candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"])
                  for row in mention_rows}
new_mentions = []


def mention(segment_id, source_line, suffix, candidate_id, surface, note, occurrence=0):
    mention_id = f"m-chp8-p235-{suffix}"
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
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span
                                     for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({"mention_id": mention_id, "segment_id": segment_id,
                         "candidate_id": candidate_id, "surface_form": surface,
                         "start_char": str(start), "end_char": str(end), "note": note})


mention_specs = [
    (P235, 292, "glass-pictures", "cand-7956", "pictures on glass", "Group-level work reference; individual count and objects are not identified."),
    (P235, 292, "flight-title", "cand-7956", "The Flight into Egypt", "Work title as printed; not merged with other works of the same subject."),
    (P235, 292, "ferdinand-1", "cand-1609", "Ferdinand", "Grand Prince Ferdinand de’ Medici."),
    (P235, 292, "giordano-1", "cand-1172", "Luca Giordano", "Indexed painter candidate."),
    (P235, 292, "neapolitan-painter", "cand-1172", "Neapolitan painter", "Descriptive reference to Luca Giordano; not a separate group."),
    (P235, 293, "prince-1", "cand-1609", "Prince", "Continuation of ‘Grand Prince’ across the line break."),
    (P235, 293, "livorno-1", "cand-6716", "Livorno", "Place of the reported May 1702 meeting."),
    (P235, 293, "ferdinand-him-1", "cand-1609", "him", "Coreference to Ferdinand."),
    (P235, 293, "spain-1", "cand-5120", "Spain", "Geographic place from which Giordano was returning."),
    (P235, 294, "ferdinand-patronage", "cand-1609", "Ferdinand’s patronage", "Subject of Haskell’s evaluative account."),
    (P235, 294, "exception", "cand-1172", "this one exception", "Likely refers to the Luca Giordano passage, but the antecedent is not explicit."),
    (P235, 294, "he-interesting", "cand-1609", "he", "Coreference to Ferdinand.", 0),
    (P235, 294, "painters", "cand-7958", "the painters who worked for him", "Generic painters are not enumerated; phrase is retained as collective context."),
    (P235, 294, "him-painters", "cand-1609", "him", "Coreference to Ferdinand.", 0),
    (P235, 294, "he-remembered", "cand-1609", "he", "Coreference to Ferdinand.", 1),
    (P235, 294, "his-life", "cand-1609", "his life", "Coreference to Ferdinand."),
    (P235, 294, "he-found-artists", "cand-1609", "he", "Coreference to Ferdinand.", 2),
    (P235, 294, "two-artists", "cand-7958", "two artists", "Identity unresolved at this point in the source sequence."),
    (P235, 294, "their-talents", "cand-7958", "whose talents", "Coreference to the two unnamed artists."),
    (P235, 294, "demands", "cand-1609", "the demands", "Haskell’s characterization of Ferdinand’s requirements."),
    (P235, 294, "he-demands", "cand-1609", "he", "Coreference to Ferdinand.", 3),
    (P235, 294, "them-artists", "cand-7958", "them", "Coreference to the two unnamed artists."),
    (P235, 294, "him-late-work", "cand-1609", "him", "Coreference to Ferdinand.", 1),
    (P235, 295, "ferdinand-contact", "cand-1609", "Ferdinand", "Patron whose first contact with Ricci is described as unclear.", 0),
    (P235, 295, "ricci-full", "cand-2179", "Sebastiano Ricci", "Indexed artist candidate; multiple index entries are resolved later in S3."),
    (P235, 295, "artist-ricci", "cand-2179", "the artist", "Coreference to Sebastiano Ricci."),
    (P235, 295, "venice", "cand-3401", "Venice", "Place visited by Ferdinand; the source says Ricci was absent during both visits."),
    (P235, 295, "grand-prince-visits", "cand-7970", "the Grand Prince’s two visits", "Unspecified earlier visits to Venice; no dates supplied."),
    (P235, 295, "ferdinand-commission", "cand-1609", "Ferdinand", "Commissioning patron.", 1),
    (P235, 295, "him-commission", "cand-2179", "him", "Coreference to Ricci as commissioned artist."),
    (P235, 295, "crucifixion-title-start", "cand-7957", "Crucifixion with the Madonna,", "First line of a title continuing at L296."),
    (P235, 296, "crucifixion-title-john", "cand-7981", "St John", "Figure named in the work title; exact identity is not specified."),
    (P235, 296, "crucifixion-title-charles", "cand-7982", "St Charles Borromeo", "Figure named in the work title."),
    (P235, 296, "andrea-del-sarto", "cand-2362", "Andrea del Sarto’s", "Indexed painter candidate; his named painting follows."),
    (P235, 296, "madonna-delle-arpie", "cand-7862", "Madonna delle Arpie", "Reuse the existing work candidate."),
    (P235, 296, "bought-he", "cand-1609", "he", "Ferdinand is the purchaser according to the sentence."),
    (P235, 296, "nuns-house", "cand-7960", "the nuns of S. Francesco de’ Macci", "The source does not resolve whether the named house is a church, convent, or institution."),
    (P235, 296, "ferdinand-gallery", "cand-7961", "his own gallery", "Ferdinand’s gallery; location not given."),
    (P235, 296, "ricci-visit", "cand-2179", "Ricci", "Coreference to Sebastiano Ricci."),
    (P235, 296, "picture-on-spot", "cand-7957", "the picture", "The 1704 Crucifixion commission."),
    (P235, 296, "florence-first", "cand-3397", "Florence", "Destination of the reported short visit."),
    (P235, 296, "cassana", "cand-0593", "Cassana", "Indexed artist and adviser candidate."),
    (P235, 296, "prince-informed", "cand-1609", "the Prince", "Coreference to Ferdinand."),
    (P235, 296, "venetian-market", "cand-7968", "Venetian market", "Market for pictures available to Ferdinand; no specific transaction is asserted."),
    (P235, 296, "ricci-found-patrons", "cand-2179", "Ricci", "Coreference to Sebastiano Ricci.", 1),
    (P235, 296, "florence-patrons", "cand-3397", "Florence", "Place where Ricci found further patrons.", 1),
    (P235, 296, "prince-circle", "cand-1609", "Grand Prince’s", "Coreference to Ferdinand in ‘Grand Prince’s circle of friends’."),
    (P235, 296, "marucelli-brothers", "cand-7959", "brothers Marucelli", "Collective family reference; only Francesco is named here."),
    (P235, 296, "francesco-marucelli", "cand-1554", "Francesco", "Francesco Marucelli, described as the most distinguished brother."),
    (P235, 296, "rome", "cand-4490", "Rome", "Place of Francesco Marucelli’s reported death."),
    (P235, 297, "ricci-employed-him", "cand-2179", "him", "Coreference to Ricci, whom the brothers employed."),
    (P235, 297, "their-palace", "cand-1558", "their palace", "Reuse the indexed Marucelli Palace candidate."),
    (P235, 297, "ricci-sent-paintings", "cand-2179", "he", "Coreference to Ricci.", 0),
    (P235, 297, "paintings-in-crates", "cand-7983", "some paintings", "Group of works sent for the Marucelli; only two landscapes are identified."),
    (P235, 297, "paintings-for-marucelli", "cand-7959", "for them", "Coreference to the Marucelli brothers."),
    (P235, 297, "two-crates", "cand-7983", "two crates", "Container count in the shipment report; not a separate entity."),
    (P235, 297, "grand-prince-shipment", "cand-1609", "the Grand Prince", "Recipient of the shipment."),
    (P235, 298, "two-landscapes", "cand-7962", "a couple of small landscapes", "Two works by Marco Ricci; no titles or locations supplied."),
    (P235, 298, "ricci-nephew", "cand-2179", "his nephew", "The possessive refers to Sebastiano Ricci as Marco’s uncle."),
    (P235, 298, "marco-ricci", "cand-2149", "Marco", "Indexed painter candidate, identified here as Ricci’s nephew."),
    (P235, 298, "ricci-proposed-visit", "cand-2179", "he", "Coreference to Sebastiano Ricci.", 0),
    (P235, 298, "visit-florence", "cand-3397", "Florence", "Destination of the proposed visit."),
    (P235, 298, "poggio-gallery-room", "cand-7963", "Ferdinand’s gallery of Venetian pictures at Poggio a Caiano", "Proposed room-painting location; relation to the later favourite gallery is not explicit."),
    (P235, 298, "ferdinand-reply", "cand-1609", "Ferdinand’s reply", "The Prince’s reply a week later."),
    (P235, 298, "ferdinand-scheme", "cand-1609", "Ferdinand’s", "Possessive in the reference to the postponed scheme."),
    (P235, 298, "projected-scheme", "cand-7963", "the projected scheme", "The proposed visit to paint a room in the Poggio gallery."),
    (P235, 299, "ricci-arrival", "cand-2179", "Ricci", "Coreference to Sebastiano Ricci."),
    (P235, 300, "allegory-work", "cand-7965", "Allegory of the Arts", "Named work reported as painted for Ferdinand and later destroyed."),
    (P235, 300, "favourite-gallery", "cand-7964", "Ferdinand’s favourite gallery", "Unlocated gallery; possible relation to Poggio remains implicit."),
    (P235, 300, "favourite-villa", "cand-7987", "his favourite villa", "Coreference to Ferdinand; villa not named in this sentence."),
    (P235, 300, "this-work", "cand-7965", "This work", "Coreference to the Allegory of the Arts."),
    (P235, 300, "ricci-activities", "cand-2179", "Ricci’s Florentine activities", "The artist whose work is discussed."),
    (P235, 300, "marucelli-decorations", "cand-7966", "the great decorations", "Surviving group of Ricci decorations for the Marucelli."),
    (P235, 300, "ricci-painted", "cand-2179", "he", "Coreference to Ricci."),
    (P235, 300, "marucelli-friends", "cand-7959", "Ferdinand’s friends the Marucelli", "Collective reference to the Marucelli brothers."),
    (P235, 300, "grand-prince-pitti", "cand-1609", "the Grand Prince himself", "Coreference to Ferdinand."),
    (P235, 300, "pitti-small-room", "cand-7967", "a small room in the Pitti", "Location of the reported surviving Ricci decoration."),
    (NOTES, 430, "letter75", "cand-7971", "Letter 75", "Specific letter locator cited in note 1."),
    (NOTES, 430, "grand-prince-letter", "cand-1609", "the Grand Prince", "Writer of the quoted letter according to Haskell’s footnote."),
    (NOTES, 430, "letter75-luca", "cand-1172", "Luca Giordano", "Person named in the quoted Italian letter."),
    (NOTES, 430, "letter75-livorno", "cand-6716", "[Livorno]", "Editorially supplied place name in Haskell’s quotation."),
    (NOTES, 430, "letter75-naples", "cand-3534", "Napoli", "Italian place name in the quoted letter."),
    (NOTES, 430, "martini", "cand-7925", "The Abate Orazio Martini", "Author cited by Haskell; not independently consulted."),
    (NOTES, 430, "martini-publication", "cand-7926", "Parte I, Vol. I", "Publication locator cited for Martini; title remains unspecified."),
    (NOTES, 430, "martini-spain", "cand-5120", "Spain", "Place from which Giordano is reported to have returned."),
    (NOTES, 430, "martini-luca", "cand-1172", "Luca Giordano", "Person named in the secondary report.", 1),
    (NOTES, 430, "martini-ferdinand", "cand-1609", "Ferdinand", "Patron in the report."),
    (NOTES, 430, "martini-florence", "cand-3397", "Florence", "Place where the paintings are reported to have been made."),
    (NOTES, 431, "fogolari-note2", "cand-7894", "Fogolari, 1937", "Cited publication; underlying letters not independently consulted."),
    (NOTES, 431, "letter98", "cand-7972", "Letters 98", "Letter locator and date reported in the footnote."),
    (NOTES, 431, "letter99", "cand-7973", "99", "Second letter locator and date reported in the footnote."),
    (NOTES, 432, "letters-ricci", "cand-7984", "Some of these letters", "Unnumbered letters; not equated with notes 1 or 2 letter locators."),
    (NOTES, 432, "fogolari-note3", "cand-7894", "Fogolari, 1937", "Cited publication; letters not independently consulted."),
    (NOTES, 432, "ricci-note3", "cand-2179", "Ricci", "Author of the letters as reported by Haskell."),
    (NOTES, 432, "ferdinand-note3", "cand-1609", "Ferdinand", "Recipient of the letters as reported by Haskell."),
    (NOTES, 432, "mehus", "cand-1632", "Livio Mehus", "Artist named in Haskell’s summary of the letters."),
    (NOTES, 432, "ghisolfi", "cand-1159", "Ghisolfi", "Artist named in Haskell’s summary of the letters."),
    (NOTES, 432, "lyss", "cand-1462", "Lyss", "Artist named in Haskell’s summary of the letters."),
    (NOTES, 432, "vouet", "cand-2792", "Simon Vouet", "Artist named in Haskell’s summary of the letters."),
    (NOTES, 433, "letter197", "cand-7975", "Letter of 1 May 1706", "Specific archival letter locator; published in Appendix 4."),
    (NOTES, 433, "archivio-mediceo", "cand-7974", "Archivio Mediceo", "Archival series named as the location of Letter 197."),
    (NOTES, 433, "filza5903", "cand-7974", "Filza 5903", "Filing unit for the cited letter."),
    (NOTES, 433, "letter197-number", "cand-7975", "No. 197", "Specific archival locator."),
    (NOTES, 433, "exhibition-october", "cand-7977", "exhibition of October 1706", "Specific exhibition event, referenced through p.240 note 5."),
    (NOTES, 433, "orazio-marucelli", "cand-1557", "Orazio Marucelli", "Indexed person candidate."),
    (NOTES, 433, "flora-work", "cand-7978", "a Flora", "Painting identified only by subject and artist."),
    (NOTES, 433, "sebastiano-ricci-note4", "cand-2179", "Sebastiano Ricci", "Painter of the reported Flora."),
    (NOTES, 434, "letter200", "cand-7976", "Letter of 8 May 1706", "Specific archival letter locator; published in Appendix 4."),
    (NOTES, 434, "archivio-mediceo-note5", "cand-7974", "Archivio Mediceo", "Archival series named for Letter 200."),
    (NOTES, 434, "filza5903-note5", "cand-7974", "Filza 5903", "Filing unit for Letter 200."),
    (NOTES, 434, "letter200-number", "cand-7976", "No. zoo", "OCR form of the locator; page image reads No. 200."),
    (NOTES, 435, "farsetti", "cand-1013", "T. G. Farsetti", "Indexed author candidate; cited through Fogolari."),
    (NOTES, 435, "farsetti-account", "cand-7979", "referred to the ceiling as follows", "Descriptive source candidate for the late-eighteenth-century Farsetti excerpt."),
    (NOTES, 435, "ceiling-description", "cand-7980", "the ceiling", "Work described by Farsetti; identity with the destroyed Allegory is unresolved."),
    (NOTES, 435, "fogolari-farsetti", "cand-7894", "Fogolari, 1937", "Publication carrying the quoted Farsetti passage; not independently consulted."),
    (NOTES, 435, "venetian-room", "cand-7963", "Nella camera de’ quadri veneziani", "Farsetti’s named room at Poggio; possible identity with the room in the body remains unconfirmed."),
    (NOTES, 435, "prince-ferdinando-quote", "cand-1609", "Principe Ferdinando", "Ferdinand in Farsetti’s quotation."),
    (NOTES, 435, "poggio-quote", "cand-1966", "al Poggio", "Poggio a Caiano, named in the quotation."),
    (NOTES, 435, "venetian-pictures-quote", "cand-7988", "detti quadri", "Coreference to the Venetian pictures described in Farsetti’s quoted passage."),
    (NOTES, 435, "galleria-quote", "cand-7985", "Galleria", "Destination named in Farsetti’s text; exact repository or place unresolved."),
    (NOTES, 435, "painted-ceiling", "cand-7980", "un soffitto dipinto", "The quoted description of a painted ceiling."),
    (P235, 301, "farsetti-ceiling-continuation", "cand-7980", "In questo si rappresentano allegorie", "Continuation of Farsetti’s quoted note 6; not a body-text assertion."),
    (P235, 301, "sister-arts", "cand-7986", "Arti sorelle", "Allegorical group named in the continuation of Farsetti’s quotation."),
]
for spec in mention_specs:
    mention(*spec)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 235,
        "pdf_physical_page": 41, "claim": claim, "speaker": "Haskell",
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote(segment_id, first, last), "origin": "book",
            "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p235-giordano-pictures-and-visit", P235, 292, 293,
                   "cand-1172", "cand-7956", "painted_glass_pictures_and_visited_ferdinand_at_livorno",
                   "Haskell says Luca Giordano painted valuable pictures on glass of The Flight into Egypt for Ferdinand; in May 1702 Giordano called on the Grand Prince at Livorno on his return from Spain and is reported to have worked for him for a time before leaving for home.",
                   "The account is Haskell’s. Main text says Giordano was returning from Spain, while the quoted letter says he was returning from Naples; they may describe successive legs, so the itinerary is not forced into one reading. Neither underlying source was independently consulted. ‘Home’ is not assigned a more precise destination.",
                   ["cand-1172", "cand-7956", "cand-1609", "cand-6716", "cand-5120", "cand-7969"],
                   extras={"date": "1702-05", "relation_candidate": True,
                           "ocr_corrections": [{"source_line": 291, "ocr": "[Page 23]", "print": "[Page 235]", "basis": "CHP-8.pdf physical page 41"},
                                               {"source_line": 292, "ocr": "painted, for", "print": "painted for", "basis": "CHP-8.pdf physical page 41"}],
                           "linked_note_statement_ids": ["st-chp8-p235-note1-letter75", "st-chp8-p235-note1-martini"]}),
    make_statement("st-chp8-p235-haskell-patronage-assessment", P235, 294, 294,
                   "cand-1609", "cand-7958", "assessed_ferdinands_patronage_and_two_unnamed_artists",
                   "Haskell judges Ferdinand more interesting than most painters who worked for him, with ‘this one exception’; he says that near the end of Ferdinand’s life two artists finally met his demands and painted some of their most striking work for him.",
                   "This is Haskell’s evaluative rhetoric. The antecedent of ‘this one exception’ is not explicit, and the two artists are not identified on this page; neither phrase is used to settle their identities.",
                   ["cand-1609", "cand-1172", "cand-7958"],
                   extras={"relation_candidate": True}),
    make_statement("st-chp8-p235-ricci-contact-context", P235, 295, 295,
                   "cand-1609", "cand-2179", "contact_and_venice_visit_context_uncertain",
                   "Haskell says it is unclear how Ferdinand first contacted Sebastiano Ricci; Ricci was not in Venice during either of the Grand Prince’s two visits there.",
                   "The source explicitly marks the contact history as unclear. The visits are not dated here.",
                   ["cand-1609", "cand-2179", "cand-3401", "cand-7970"],
                   extras={"relation_candidate": True}),
    make_statement("st-chp8-p235-ricci-commission", P235, 295, 296,
                   "cand-1609", "cand-7957", "commissioned_crucifixion_to_replace_madonna_delle_arpie",
                   "In 1704 Ferdinand commissioned from Ricci a Crucifixion with the Madonna, St John, and St Charles Borromeo to replace Andrea del Sarto’s Madonna delle Arpie, which Ferdinand had bought from the nuns of S. Francesco de’ Macci for his own gallery.",
                   "This is Haskell’s report. The source does not identify the gallery’s location or resolve the institutional/spatial identity of S. Francesco de’ Macci. The page image confirms the OCR punctuation correction at L296.",
                   ["cand-1609", "cand-2179", "cand-7957", "cand-2362", "cand-7862", "cand-7960", "cand-7961", "cand-7981", "cand-7982"],
                   extras={"date": "1704", "relation_candidate": True,
                           "ocr_corrections": [{"source_line": 296, "ocr": "Marucelli.of", "print": "Marucelli, of", "basis": "CHP-8.pdf physical page 41"}],
                           "linked_note_statement_ids": ["st-chp8-p235-note2-fogolari-letters"]}),
    make_statement("st-chp8-p235-ricci-visit-and-cassana-advice", P235, 296, 296,
                   "cand-2179", "cand-1609", "visited_florence_and_assisted_cassana_with_market_information",
                   "Ricci seems to have made a short visit to Florence to paint the commissioned picture on site and thereafter to have assisted Cassana in keeping Ferdinand informed about pictures available on the Venetian market.",
                   "Haskell marks the visit and its purpose as inferential (‘seems to have’). The account does not identify specific market transactions or pictures in this clause.",
                   ["cand-2179", "cand-7957", "cand-3397", "cand-0593", "cand-1609", "cand-3401", "cand-7968"],
                   extras={"relation_candidate": True,
                           "linked_note_statement_ids": ["st-chp8-p235-note3-ricci-letters"]}),
    make_statement("st-chp8-p235-marucelli-patronage", P235, 296, 297,
                   "cand-2179", "cand-7959", "employed_by_marucelli_brothers_for_palace_decorations",
                   "Within a year or two Ricci found further patrons among Ferdinand’s Florentine circle of friends: the brothers Marucelli employed him to decorate several rooms in their palace. Francesco, described as the most distinguished, had died in Rome in 1703.",
                   "The unnamed brother or brothers are not individually identified. The death and employment details are Haskell’s report; no exact year is assigned to Ricci’s employment beyond the source’s interval.",
                   ["cand-2179", "cand-7959", "cand-1554", "cand-3397", "cand-1609", "cand-4490", "cand-1558"],
                   extras={"relation_candidate": True,
                           "ocr_corrections": [{"source_line": 296, "ocr": "Marucelli.of", "print": "Marucelli, of", "basis": "CHP-8.pdf physical page 41"}]}),
    make_statement("st-chp8-p235-crates-and-landscapes", P235, 297, 298,
                   "cand-2179", "cand-7983", "sent_paintings_for_marucelli_to_ferdinand_in_two_crates",
                   "In May 1706 Ricci enclosed paintings for the Marucelli in two crates sent to Ferdinand; the shipment included a couple of small landscapes by Ricci’s nephew Marco.",
                   "Only the two small landscapes are described; the other paintings and their number are unspecified. The kinship is reported by Haskell and not independently verified.",
                   ["cand-2179", "cand-7983", "cand-7959", "cand-1609", "cand-7962", "cand-2149"],
                   extras={"date": "1706-05", "relation_candidate": True,
                           "ocr_corrections": [{"source_line": 297, "ocr": "Grand Princewhich", "print": "Grand Prince which", "basis": "CHP-8.pdf physical page 41"},
                                               {"source_line": 298, "ocr": ". included", "print": "included", "basis": "CHP-8.pdf physical page 41"}],
                           "linked_note_statement_ids": ["st-chp8-p235-note4-letter197-and-exhibition"]}),
    make_statement("st-chp8-p235-poggio-visit-postponed", P235, 298, 298,
                   "cand-2179", "cand-7963", "proposed_gallery_visit_postponed_due_to_ferdinands_ill_health",
                   "Ricci first alluded to a forthcoming visit to Florence to paint a room in Ferdinand’s gallery of Venetian pictures at Poggio a Caiano; Ferdinand replied a week later that ill health was causing him to postpone the scheme.",
                   "The visit and painting are prospective in this passage. Haskell does not say that this planned room is the same location as the later favourite gallery or Farsetti’s quoted room.",
                   ["cand-2179", "cand-3397", "cand-1609", "cand-7963", "cand-1966"],
                   extras={"relation_candidate": True,
                           "ocr_corrections": [{"source_line": 297, "ocr": "Grand Princewhich", "print": "Grand Prince which", "basis": "CHP-8.pdf physical page 41"},
                                               {"source_line": 298, "ocr": ". included", "print": "included", "basis": "CHP-8.pdf physical page 41"}],
                           "linked_note_statement_ids": ["st-chp8-p235-note5-letter200"]}),
    make_statement("st-chp8-p235-allegory-destroyed", P235, 299, 300,
                   "cand-2179", "cand-7965", "painted_allegory_of_the_arts_for_ferdinand_reported_destroyed",
                   "Shortly afterward Ricci arrived to paint an Allegory of the Arts in Ferdinand’s favourite gallery in his favourite villa; Haskell says this work has been destroyed.",
                   "The favourite gallery and villa are not named in this sentence. Their identity with Poggio a Caiano is plausible from context but remains unresolved; Farsetti’s ceiling description in note 6 is not merged with this work.",
                   ["cand-2179", "cand-7965", "cand-1609", "cand-7964", "cand-7987"],
                   extras={"relation_candidate": True,
                           "linked_note_statement_ids": ["st-chp8-p235-note6-farsetti-reference", "st-chp8-p235-note6-farsetti-quote-tail"]}),
    make_statement("st-chp8-p235-surviving-decorations", P235, 300, 300,
                   "cand-2179", "cand-7966", "surviving_decorations_for_marucelli_and_ferdinand",
                   "Haskell says Ricci’s Florentine activities are attested by surviving decorations for the Marucelli and for the Grand Prince himself in a small room in the Pitti.",
                   "The subjects of these surviving decorations are not specified. The source does not identify either group with the destroyed Allegory of the Arts.",
                   ["cand-2179", "cand-7966", "cand-7959", "cand-1609", "cand-7967", "cand-7662"],
                   extras={"relation_candidate": True}),
    make_statement("st-chp8-p235-note1-letter75", NOTES, 430, 430,
                   "cand-1609", "cand-7971", "footnote_cites_letter_75_and_quotes_luca_giordano_at_livorno",
                   "Haskell’s note cites a letter from the Grand Prince dated 26 May 1702 as Fogolari Letter 75 and quotes it reporting Luca Giordano at Livorno on his return from Naples.",
                   "The letter is cited through Haskell and Fogolari, not independently consulted. The scan reads ‘Mentre che scrivo è qui [Livorno] da me Luca Giordano che ritorna da Napoli’; the OCR’s extra punctuation after ‘è’ is removed in the reading.",
                   ["cand-1609", "cand-7971", "cand-7894", "cand-1172", "cand-6716", "cand-3534"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p235-giordano-pictures-and-visit"],
                           "ocr_corrections": [{"source_line": 430, "ocr": "ibid..", "print": "ibid.", "basis": "CHP-8.pdf physical page 41"},
                                               {"source_line": 430, "ocr": "è , qui", "print": "è qui", "basis": "CHP-8.pdf physical page 41"}]}),
    make_statement("st-chp8-p235-note1-martini", NOTES, 430, 430,
                   "cand-7925", "cand-1172", "martini_reports_giordano_painted_for_ferdinand_in_florence",
                   "Haskell cites Abate Orazio Martini, Parte I, Vol. I, p. 38, for the report that Luca Giordano painted various pictures for Ferdinand in Florence after returning from Spain.",
                   "The named publication is cited as a source locator only; its title and text were not independently verified. Giordano’s work and patronage remain Haskell’s report here.",
                   ["cand-7925", "cand-7926", "cand-1172", "cand-1609", "cand-3397", "cand-5120"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p235-giordano-pictures-and-visit"]}),
    make_statement("st-chp8-p235-note2-fogolari-letters", NOTES, 431, 431,
                   None, "cand-7894", "footnote_cites_fogolari_letters_98_and_99",
                   "Haskell cites Fogolari (1937), Letters 98 and 99, dated 30 August and 20 September 1704.",
                   "The letters and cited publication were not independently consulted; the locators are retained as reported.",
                   ["cand-7894", "cand-7972", "cand-7973"], text_layer="footnote citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p235-ricci-commission"]}),
    make_statement("st-chp8-p235-note3-ricci-letters", NOTES, 432, 432,
                   "cand-2179", "cand-7984", "footnote_reports_ricci_letters_about_available_pictures",
                   "Haskell says some letters published by Fogolari show Ricci writing to Ferdinand about works by Livio Mehus, Ghisolfi, Lyss, Simon Vouet, and others.",
                   "The letters are not numbered in this note and were not independently consulted. ‘Others’ remains unenumerated; this does not establish a complete market list.",
                   ["cand-2179", "cand-7984", "cand-7894", "cand-1609", "cand-1632", "cand-1159", "cand-1462", "cand-2792"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p235-ricci-visit-and-cassana-advice"],
                           "ocr_corrections": [{"source_line": 432, "ocr": "others. -", "print": "others.", "basis": "CHP-8.pdf physical page 41"}]}),
    make_statement("st-chp8-p235-note4-letter197-and-exhibition", NOTES, 433, 433,
                   "cand-7975", "cand-7978", "footnote_cites_letter_197_and_reports_marucelli_exhibited_flora",
                   "Haskell cites Letter 197 of 1 May 1706 in Archivio Mediceo, Filza 5903, published in Appendix 4; he also reports that Orazio Marucelli exhibited a Flora by Sebastiano Ricci in an October 1706 exhibition.",
                   "The letter and Appendix 4 were not independently consulted. The exhibition venue is not stated here; the reference to p. 240 note 5 is not independently checked.",
                   ["cand-7974", "cand-7975", "cand-7977", "cand-1557", "cand-7978", "cand-2179"],
                   text_layer="footnote report and citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p235-crates-and-landscapes"],
                           "cross_reference_page": "240n5"}),
    make_statement("st-chp8-p235-note5-letter200", NOTES, 434, 434,
                   None, "cand-7976", "footnote_cites_letter_200",
                   "Haskell cites Letter 200 of 8 May 1706 in Archivio Mediceo, Filza 5903, published in Appendix 4.",
                   "This is a citation locator only; the letter and Appendix 4 were not independently consulted. The OCR form ‘zoo’ is corrected to 200 against the page image.",
                   ["cand-7974", "cand-7976"], text_layer="footnote citation",
                   extras={"relation_candidate": False,
                           "linked_body_statement_ids": ["st-chp8-p235-poggio-visit-postponed"],
                           "ocr_corrections": [{"source_line": 434, "ocr": "No. zoo", "print": "No. 200", "basis": "CHP-8.pdf physical page 41"}]}),
    make_statement("st-chp8-p235-note6-farsetti-reference", NOTES, 435, 435,
                   "cand-1013", "cand-7980", "footnote_quotes_farsetti_description_of_poggio_ceiling",
                   "Haskell cites T. G. Farsetti’s late-eighteenth-century description of the ceiling through Fogolari (1937), p. 186; Farsetti describes a painted ceiling in the Venetian-pictures room at Poggio.",
                   "The quotation is a nested source report, not independently verified. Its ceiling decoration is not assumed to be the destroyed Allegory of the Arts in the body text. The scan identifies this as note 6; the OCR gives 8.",
                   ["cand-1013", "cand-7979", "cand-7894", "cand-7980", "cand-7963", "cand-1609", "cand-1966", "cand-7988", "cand-7985"],
                   text_layer="footnote quotation and citation",
                   extras={"relation_candidate": False, "quoted_speaker": "T. G. Farsetti",
                           "linked_body_statement_ids": ["st-chp8-p235-allegory-destroyed"],
                           "continued_to_segment_id": P235, "continued_to_source_line": 301,
                           "ocr_corrections": [{"source_line": 435, "ocr": "note number 8", "print": "note number 6", "basis": "CHP-8.pdf physical page 41"}]}),
    make_statement("st-chp8-p235-note6-farsetti-quote-tail", P235, 301, 301,
                   "cand-7980", "cand-7986", "footnote_quote_describes_sister_arts_allegories_on_ceiling",
                   "The final line of Farsetti’s quotation says that the ceiling represents allegories suitable to the Sister Arts.",
                   "This line continues the page-end footnote 6 from the consolidated notes segment L435; it is not body prose. The relation between this ceiling and Ricci’s destroyed Allegory of the Arts remains unresolved.",
                   ["cand-7980", "cand-7986", "cand-7979", "cand-7894"],
                   text_layer="footnote quotation continuation",
                   extras={"relation_candidate": False, "quoted_speaker": "T. G. Farsetti",
                           "linked_body_statement_ids": ["st-chp8-p235-allegory-destroyed"],
                           "continued_from_segment_id": NOTES, "continued_from_source_line": 435,
                           "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 435, "source_line_end": 435}]})
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")

for row in coverage_rows:
    if row["segment_id"] == P235:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L291-301",
                    "note": "p.235 body and page-end footnote 6 continuation at L301 reviewed against CHP-8.pdf physical page 41. The page marker OCR [Page 23] is corrected in S2; footnotes 1-6 are represented at consolidated lines L430-435."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-435",
                    "note": "Consolidated footnotes reviewed through p.235 note 6 at L435; its quotation continues at p.235 segment L301. Remaining consolidated notes L436-461 are queued for sequential review."})

preview = {
    "mode": "dry-run", "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage_updates": {P235: "L291-301 complete", NOTES: "L373-435 partial; L436-461 remain"},
    "ocr_corrections": [
        "L291 [Page 23] -> [Page 235]",
        "L292 remove comma in 'painted, for'",
        "L296 Marucelli.of -> Marucelli, of",
        "L297 Grand Princewhich -> Grand Prince which; remove stray period before included",
        "L430 ibid.. -> ibid.; remove stray comma after è",
        "L432 remove trailing OCR hyphen after others.",
        "L434 No. zoo -> No. 200",
        "L435 footnote number 8 -> 6",
    ],
    "ambiguities_preserved": [
        "identity of 'this one exception' and the two late-career artists",
        "identity of Ferdinand’s favourite gallery/villa and the proposed Poggio room",
        "identity of the Farsetti ceiling with Ricci’s destroyed Allegory of the Arts",
        "institutional/spatial type of S. Francesco de’ Macci and Galleria",
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
