"""Controlled S2 migration for Chapter 8 printed page 223 and notes 1-5."""
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
P222 = "chp-8:08_CHP-8_sec_ii:l126-138"
P223 = "chp-8:08_CHP-8_sec_ii:l140-150"
P224 = "chp-8:08_CHP-8_sec_ii:l152-161"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P222, P223, P224, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p223-20261001"


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
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
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
segment_texts = {}
line_offsets = {}
for segment_id in TARGET_IDS:
    meta = segment_by_id[segment_id]
    lines = source_lines[meta["line_start"] - 1:meta["line_end"]]
    text = "\n".join(lines)
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != meta["sha256"]:
        raise SystemExit(f"segment content hash changed: {segment_id}")
    segment_texts[segment_id] = text
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
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

expected_coverage = {
    P222: ("reviewed", "partial", "L127-138"),
    P223: ("queued", "pending", ""),
}
for sid, expected in expected_coverage.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-385":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P223 for row in mention_rows + statement_rows):
    raise SystemExit("p.223 rows already exist; inspect before rerunning")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
new_candidates = [
    ("cand-7722", "Unidentified paintings by Donato Creti depicting scenes from the life of Solomon", "work", "body-mention", "At least two paintings are reported; individual titles and present locations are not given."),
    ("cand-7723", "Two unidentified bambocciate by Giuseppe Gambarini commissioned by Cardinal Tommaso Ruffo", "work", "body-mention", "The source gives a count and genre but no titles, dates, or locations."),
    ("cand-7724", "Four unidentified pictures sent by Luca Giordano to Cardinal Tommaso Ruffo", "work", "body-mention", "One is described on p.223 as Hebrew Women singing after crossing the Red Sea; the other three are not identified."),
    ("cand-7725", "Hebrew Women singing after crossing the Red Sea (painting by Luca Giordano)", "work", "body-mention", "Haskell says this was one of four pictures Giordano sent to Ruffo and may have been connected with Giordano's work at Santa Maria Maggiore, Bergamo."),
    ("cand-7726", "Nativity painting by Francesco Solimena for Cardinal Tommaso Ruffo", "work", "body-mention", "The source supplies a subject and patron but no date, location, or secure individual identification."),
    ("cand-7727", "Presentation painting by Francesco Solimena for Cardinal Tommaso Ruffo", "work", "body-mention", "The source supplies a subject and patron but no date, location, or secure individual identification."),
    ("cand-7728", "Rich chapel built by Nicola Salvi for Cardinal Tommaso Ruffo at S. Lorenzo in Damaso", "place", "body-mention", "An interior chapel within the existing Church of S. Lorenzo in Damaso; keep distinct from the church as a whole."),
    ("cand-7729", "Unidentified old and important family into which Raimondo Buonaccorsi was born", "family", "body-mention", "Haskell does not name the family in this passage; its extent and Church connection remain source-reported and unspecified."),
    ("cand-7730", "The Church (institutional referent not specified in Haskell's account of the Buonaccorsi family)", "institution", "body-mention", "The source capitalizes Church but does not define the institution or the family's particular connection."),
    ("cand-7731", "Raimondo Buonaccorsi's palace in Macerata", "place", "body-mention", "Haskell describes its decoration and continues its description onto p.224; do not infer a modern name or status from this passage."),
    ("cand-7732", "Undescribed 1726 manuscript Memoria written by Raimondo Buonaccorsi's wife", "archive", "body-mention", "Haskell says the family still held the manuscript and that it contains a few details about Raimondo; the manuscript was not independently consulted."),
    ("cand-7733", "Photographs of Raimondo Buonaccorsi's gallery taken by Dwight Miller", "archive", "body-mention", "Acknowledged by Haskell as copies supplied by Miller; photographs were not independently inspected in this task."),
    ("cand-7734", "Silvio Ubaldi", "person", "body-mention", "Named by Haskell as a source where some information about the Buonaccorsi family can be found; exact publication or archival item is not specified here."),
    ("cand-7735", "Dwight Miller", "person", "body-mention", "Named by Haskell as the source of gallery photographs and attribution suggestions; no fuller identity is supplied on this page."),
    ("cand-7736", "Tiberio Cenci", "person", "body-mention", "Named as the recipient of a 1705 letter from Raimondo Buonaccorsi in Haskell's footnote."),
    ("cand-7737", "Alessandro Borgia (Archbishop and Prince of Fermo)", "person", "body-mention", "Named as the sender of two letters to Raimondo Buonaccorsi; preserve the titles reported in the footnote without identity expansion."),
    ("cand-7738", "Vatican Library (repository named for the Buonaccorsi letters)", "institution", "body-mention", "Repository identification is reported by Haskell; current catalogues and shelfmarks were not independently checked."),
    ("cand-7739", "Letter from Raimondo Buonaccorsi to Tiberio Cenci, 23 February 1705 (Vat. Lat. 9041, c.39)", "archive", "body-mention", "Haskell locates this letter in the Vatican Library; its contents were not consulted."),
    ("cand-7740", "Letter from Alessandro Borgia to Raimondo Buonaccorsi, 13 September 1737 (Borg. Lat. 236, c.87)", "archive", "body-mention", "Haskell locates this letter in the Vatican Library; its contents were not consulted."),
    ("cand-7741", "Letter from Alessandro Borgia to Raimondo Buonaccorsi, 7 December 1742 (Borg. Lat. 236, c.125)", "archive", "body-mention", "Haskell locates this letter in the Vatican Library; its contents were not consulted."),
    ("cand-7742", "Unidentified portrait of Cardinal Tommaso Ruffo commissioned from Andrea Pozzo", "work", "body-mention", "Reported in p.223 n.3; the portrait is not otherwise identified on this page."),
    ("cand-7743", "Bergamo", "place", "body-mention", "City named as the location of S. Maria Maggiore in the p.223 account."),
    ("cand-7744", "Fermo", "place", "body-mention", "Place named in Alessandro Borgia's ecclesiastical and princely titles in Haskell's footnote."),
    ("cand-7745", "Cavaliere dello speron d'oro", "term", "body-mention", "Honorary title Ruffo is reported to have arranged for Donato Creti; authority and date are not specified here."),
    ("cand-7746", "Capriccio pittoresco", "term", "body-mention", "The phrase is attributed by Haskell to Creti's biographer as a description of the Dance of Nymphs; it is not Haskell's independent classification."),
]
for candidate_id, name, kind, origin, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    candidate_anchor_line = {
        "cand-7722": (P223, 142), "cand-7723": (P223, 142),
        "cand-7724": (P223, 143), "cand-7725": (P223, 143),
        "cand-7726": (P223, 143), "cand-7727": (P223, 144),
        "cand-7728": (P223, 144), "cand-7729": (P223, 147),
        "cand-7730": (P223, 147), "cand-7731": (P223, 148),
        "cand-7732": (NOTES, 388), "cand-7733": (NOTES, 388),
        "cand-7734": (NOTES, 388), "cand-7735": (NOTES, 388),
        "cand-7736": (P223, 150), "cand-7737": (P223, 150),
        "cand-7738": (P223, 150), "cand-7739": (P223, 150),
        "cand-7740": (P223, 150), "cand-7741": (P223, 150),
        "cand-7742": (NOTES, 387), "cand-7743": (P223, 143),
        "cand-7744": (P223, 150), "cand-7745": (P223, 141),
        "cand-7746": (P223, 142),
    }[candidate_id]
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": origin,
        "candidate_source_ref": f"{candidate_anchor_line[0]}#L{candidate_anchor_line[1]}",
    })
    candidate_ids.add(candidate_id)

new_mentions = []
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}


def mention(segment_id, source_line, mention_id, candidate_id, surface, note, occurrence=0):
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing mention candidate: {mention_id} -> {candidate_id}")
    text = segment_texts[segment_id]
    at = line_offsets[(segment_id, source_line)]
    starts = []
    while True:
        found = text.find(surface, at)
        if found < 0:
            break
        starts.append(found)
        at = found + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention surface not found at/after L{source_line}: {surface!r} #{occurrence}; count={len(starts)}")
    start = starts[occurrence]
    key = (segment_id, str(start), str(start + len(surface)))
    if key in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == key for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(start + len(surface)), "note": note,
    })


# Body p.223: close the Creti continuation, then process the entire page in reading order.
mention(P223, 141, "m-chp8-p223-creti-him-watch", "cand-0889", "him", "Coreference to Donato Creti from the open p.222 sentence.")
mention(P223, 141, "m-chp8-p223-creti-him-created", "cand-0889", "him", "Coreference to Donato Creti from the open p.222 sentence.", 1)
mention(P223, 141, "m-chp8-p223-golden-spur", "cand-7745", "Cavaliere dello speron d'oro", "Honorific reported for Creti; exact authority and date are not given.")
mention(P223, 142, "m-chp8-p223-creti-pronoun", "cand-0889", "him", "Creti is the painter named in the p.222 continuation.")
mention(P223, 142, "m-chp8-p223-solomon", "cand-4269", "Solomon", "Biblical figure named as the subject of scenes in Creti's paintings.")
mention(P223, 142, "m-chp8-p223-dance-nymphs", "cand-0890", "Dance of Nymphs", "Index subentry identifies this work under Donato Creti.")
mention(P223, 142, "m-chp8-p223-capriccio", "cand-7746", "capriccio pittoresco", "Description attributed by Haskell to Creti's biographer.")
mention(P223, 142, "m-chp8-p223-ruffo-commission", "cand-2304", "Russo", "OCR spelling; CHP-8.pdf physical page 25 reads Ruffo.")
mention(P223, 142, "m-chp8-p223-cignani", "cand-0750", "Carlo Cignani", "Named among the Bolognese artists commissioned by Ruffo.")
mention(P223, 142, "m-chp8-p223-franceschini", "cand-1069", "Marcantonio Franceschini", "Named among the Bolognese artists; the source limits this reference to after 1720.")
mention(P223, 142, "m-chp8-p223-dal-sole", "cand-2480", "Giovan Gioseffo dal Sole", "Named among the Bolognese artists commissioned by Ruffo.")
mention(P223, 142, "m-chp8-p223-gambarini", "cand-1113", "Giuseppe Gambarini", "Painter named for two bambocciate.")
mention(P223, 143, "m-chp8-p223-ruffo-naples", "cand-2304", "Ruffo", "Subject of Haskell's characterization of Neapolitan attachment.")
mention(P223, 143, "m-chp8-p223-giordano", "cand-1172", "Luca Giordano", "Painter reported to have sent Ruffo four pictures.")
mention(P223, 143, "m-chp8-p223-four-pictures", "cand-7724", "four pictures", "Group of four Giordano pictures; only one is described here.")
mention(P223, 143, "m-chp8-p223-hebrew-women-picture", "cand-7725", "Hebrew Women singing after crossing the Red Sea", "Work described as one of the four pictures Giordano sent Ruffo.")
mention(P223, 143, "m-chp8-p223-maggiore", "cand-7627", "S. Maria Maggiore", "Church identified in the source as being in Bergamo.")
mention(P223, 143, "m-chp8-p223-bergamo", "cand-7743", "Bergamo", "City locating S. Maria Maggiore.")
mention(P223, 143, "m-chp8-p223-giordano-work-coref", "cand-7688", "his work", "Giordano's central-nave project at Santa Maria Maggiore described earlier on p.219; link remains qualified by 'may well'.")
mention(P223, 143, "m-chp8-p223-solimena", "cand-2484", "Solimena", "Painter named for the Nativity and Presentation commissioned by Ruffo.")
mention(P223, 143, "m-chp8-p223-ruffo-recipient", "cand-2304", "him", "Coreference to Cardinal Tommaso Ruffo.")
mention(P223, 144, "m-chp8-p223-nativity", "cand-7726", "Nativity", "Unidentified Solimena painting reported as made for Ruffo.")
mention(P223, 144, "m-chp8-p223-presentation", "cand-7727", "Presentation", "Unidentified Solimena painting reported as made for Ruffo.")
mention(P223, 144, "m-chp8-p223-rome-retirement", "cand-4490", "Rome", "City to which Ruffo retired, as reported by Haskell.")
mention(P223, 144, "m-chp8-p223-rich-chapel", "cand-7728", "The rich chapel", "Chapel built by Nicola Salvi for Ruffo, distinct from its host church.")
mention(P223, 144, "m-chp8-p223-salvi", "cand-2347", "Nicola Salvi", "Architect named as builder of the chapel.")
mention(P223, 144, "m-chp8-p223-chapel-ruffo", "cand-2304", "him", "Coreference to Cardinal Tommaso Ruffo.")
mention(P223, 145, "m-chp8-p223-san-lorenzo", "cand-6559", "Lorenzo in Damaso", "Church hosting the chapel; the source's preceding line ends with S.")
mention(P223, 145, "m-chp8-p223-conca", "cand-0818", "Cbnca", "OCR spelling; CHP-8.pdf physical page 25 reads Conca.")
mention(P223, 145, "m-chp8-p223-giaquinto", "cand-1165", "Corrado Giaquinto", "Named as a decorator of the chapel.")
mention(P223, 145, "m-chp8-p223-conca-former", "cand-0818", "the former", "Coreference to Sebastiano Conca, the first of the two decorators.")
mention(P223, 145, "m-chp8-p223-conca-ruffo", "cand-2304", "him", "Coreference to Cardinal Tommaso Ruffo.")
mention(P223, 145, "m-chp8-p223-palazzo-cibo", "cand-0746", "Palazzo Cibo", "Ruffo's Roman gallery location; index candidate retained pending identity alignment.")
mention(P223, 146, "m-chp8-p223-raimondo", "cand-0467", "Raimondo Buonaccorsi", "Named as a separate patron; reuse the index-seeded person candidate.")
mention(P223, 146, "m-chp8-p223-italy", "cand-3461", "Italy", "Geographical scope of Haskell's statement that Buonaccorsi ranged for pictures.")
mention(P223, 146, "m-chp8-p223-macerata", "cand-1475", "Macerata", "Town where Haskell says Raimondo lived.")
mention(P223, 147, "m-chp8-p223-nobleman", "cand-0467", "This provincial nobleman", "Coreference to Raimondo Buonaccorsi.")
mention(P223, 147, "m-chp8-p223-old-family", "cand-7729", "family", "Unidentified family described as old and important; not named in the source.")
mention(P223, 147, "m-chp8-p223-church", "cand-7730", "Church", "Institutional referent is capitalized but not specified; page image confirms the period, not the OCR question mark.")
mention(P223, 147, "m-chp8-p223-francesca", "cand-0474", "Francesca Bussi", "Named as Raimondo's wife in 1699.")
mention(P223, 147, "m-chp8-p223-simone", "cand-0469", "Simone", "Index candidate is Buonaccorsi, Cardinal Simone; this passage gives only the forename, so identity remains for S3.")
mention(P223, 148, "m-chp8-p223-raimondo-died", "cand-0467", "He", "Coreference to Raimondo Buonaccorsi.")
mention(P223, 148, "m-chp8-p223-raimondo-letters", "cand-0467", "him", "Coreference to Raimondo Buonaccorsi in the account of traceable letters.")
mention(P223, 148, "m-chp8-p223-palace", "cand-7731", "his palace", "Raimondo Buonaccorsi's palace in Macerata; the following description continues on p.224.")
mention(P223, 148, "m-chp8-p223-palace-continuation", "cand-7731", "The palace", "Coreference to Raimondo's palace; this sentence continues on p.224.")

# Page 223 citations and acknowledgements; these remain source reports, not independent verification.
mention(P223, 149, "m-chp8-p223-n2-zanotti-citation", "cand-7115", "Zanotti, I, p. 239", "Citation as printed in footnote 2; the cited page was not independently read.")
mention(P223, 149, "m-chp8-p223-n2-zanotti-author", "cand-7114", "Zanotti", "Author mention nested in the citation span.")
mention(NOTES, 386, "m-chp8-p223-n1-zanotti-citation", "cand-7115", "Zanotti, II, p. 115", "Citation as printed in footnote 1; the cited page was not independently read.")
mention(NOTES, 386, "m-chp8-p223-n1-zanotti-author", "cand-7114", "Zanotti", "Author mention nested in the citation span.")
mention(NOTES, 386, "m-chp8-p223-n1-crespi-citation", "cand-6591", "L. Crespi, p. 259", "Bibliographic work identified from the book bibliography; the cited page was not independently read.")
mention(NOTES, 386, "m-chp8-p223-n1-crespi-author", "cand-7716", "L. Crespi", "Author mention nested in the citation span.")
mention(NOTES, 387, "m-chp8-p223-n3-dominici-citation", "cand-4835", "De Dominici, IV, p. 538", "Citation to volume IV; the cited page was not independently read.")
mention(NOTES, 387, "m-chp8-p223-n3-dominici-author", "cand-7116", "De Dominici", "Author mention nested in the citation span.")
mention(NOTES, 387, "m-chp8-p223-n3-moroni-citation", "cand-7696", "Moroni, XII, p. 71", "Citation to the multivolume dictionary; volume XII page 71 was not independently read.")
mention(NOTES, 387, "m-chp8-p223-n3-moroni-author", "cand-5954", "Moroni", "Surname-only source attribution remains unresolved.")
mention(NOTES, 387, "m-chp8-p223-n3-ruffo-portrait", "cand-7742", "his portrait", "Portrait commissioned by Cardinal Ruffo according to the footnote.")
mention(NOTES, 387, "m-chp8-p223-n3-pozzo", "cand-2033", "Andrea Pozzo", "Painter named for Ruffo's portrait.")
mention(NOTES, 387, "m-chp8-p223-n3-pascoli-citation", "cand-4552", "Pascoli, II, p. 265", "Citation to volume II; the cited page was not independently read.")
mention(NOTES, 387, "m-chp8-p223-n3-pascoli-author", "cand-1842", "Pascoli", "Author mention nested in the citation span.")

mention(NOTES, 388, "m-chp8-p223-n4-orlando", "cand-0466", "Count Orlando Buonaccorsi", "Acknowledged by Haskell as making surviving material about his ancestor available.")
mention(NOTES, 388, "m-chp8-p223-n4-dwight", "cand-7735", "Dwight Miller", "Acknowledged as supplying gallery photographs and attribution suggestions.")
mention(NOTES, 388, "m-chp8-p223-n4-gallery-photos", "cand-7733", "photographs he had taken of the gallery", "Photographs named in Haskell's acknowledgement.")
mention(NOTES, 388, "m-chp8-p223-n4-ubaldi", "cand-7734", "Silvio Ubaldi", "Named as a source for some family information; the source item is not identified.")
mention(NOTES, 388, "m-chp8-p223-n4-family", "cand-7729", "the family", "Coreference to the unidentified Buonaccorsi family described on p.223.")
mention(NOTES, 388, "m-chp8-p223-n4-memoria", "cand-7732", "Memoria", "Undescribed 1726 manuscript written by Raimondo's wife, according to Haskell.")
mention(NOTES, 388, "m-chp8-p223-n4-wife", "cand-0474", "his wife", "Likely coreference to Francesca Bussi, the wife named in the body; retain as an alignment lead.")
mention(NOTES, 388, "m-chp8-p223-n4-family-again", "cand-7729", "the family", "Reported current holder of the manuscript; family identity remains source-contextual.", 1)

mention(P223, 150, "m-chp8-p223-n5-vatican-library", "cand-7738", "Vatican Library", "Repository reported by Haskell for the three letters.")
mention(P223, 150, "m-chp8-p223-n5-letter-1705", "cand-7739", "From Raimondo Buonaccorsi to Tiberio Cenci, dated 23 February 1705", "Archival letter identified by sender, recipient, date, and shelfmark.")
mention(P223, 150, "m-chp8-p223-n5-raimondo-1705", "cand-0467", "Raimondo Buonaccorsi", "Sender of the 1705 letter.")
mention(P223, 150, "m-chp8-p223-n5-cenci", "cand-7736", "Tiberio Cenci", "Recipient of the 1705 letter.")
mention(P223, 150, "m-chp8-p223-n5-vat-lat", "cand-7739", "Vat. , c. 39", "OCR omits Lat. 9041; page image reads Vat. Lat. 9041, c.39.")
mention(P223, 150, "m-chp8-p223-n5-letter-1737", "cand-7740", "from Alessandro Borgia, Arcivescovo e principe di Fermo, to Raimondo Buonaccorsi, dated 13 September 1737", "Archival letter identified by sender, recipient, date, and shelfmark.")
mention(P223, 150, "m-chp8-p223-n5-borgia", "cand-7737", "Alessandro Borgia", "Sender of the 1737 and 1742 letters.")
mention(P223, 150, "m-chp8-p223-n5-fermo", "cand-7744", "Fermo", "Place named in Borgia's title.")
mention(P223, 150, "m-chp8-p223-n5-raimondo-1737", "cand-0467", "Raimondo Buonaccorsi", "Recipient of the 1737 letter.", 1)
mention(P223, 150, "m-chp8-p223-n5-borg-lat-87", "cand-7740", "Borg. , c. 87", "OCR omits Lat. 236; page image reads Borg. Lat. 236, c.87.")
mention(P223, 150, "m-chp8-p223-n5-letter-1742", "cand-7741", "dated 7 December 1742", "Third archival letter, with sender and recipient supplied by the preceding 'as (ii)'.")
mention(P223, 150, "m-chp8-p223-n5-borg-lat-125", "cand-7741", "Borg. , c. 125", "OCR omits Lat. 236; page image reads Borg. Lat. 236, c.125.")


def lines_quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


ocr = [
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 142, "ocr": "Russo", "print": "Ruffo", "basis": "CHP-8.pdf physical page 25."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 145, "ocr": "Cbnca", "print": "Conca", "basis": "CHP-8.pdf physical page 25."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 147, "ocr": "Church?", "print": "Church.", "basis": "CHP-8.pdf physical page 25."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 149, "ocr": "- 2", "print": "2", "basis": "CHP-8.pdf physical page 25."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 150, "ocr": "s The letters", "print": "5 The letters", "basis": "CHP-8.pdf physical page 25."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 150, "ocr": "oflittle", "print": "of little", "basis": "CHP-8.pdf physical page 25."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 150, "ocr": "Vat. , c. 39", "print": "Vat. Lat. 9041, c. 39", "basis": "CHP-8.pdf physical page 25."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 150, "ocr": "Borg. , c. 87", "print": "Borg. Lat. 236, c. 87", "basis": "CHP-8.pdf physical page 25."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 150, "ocr": "Borg. , c. 125", "print": "Borg. Lat. 236, c. 125", "basis": "CHP-8.pdf physical page 25."},
]


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", speaker="Haskell", extras=None):
    qualifiers = {
        "source_line_start": first_line, "source_line_end": last_line,
        "printed_page": 223, "pdf_physical_page": 25,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": lines_quote(segment_id, first_line, last_line),
        "origin": "book", "source_file": segment_by_id[segment_id]["source_file"],
    }


new_statements = [
    make_statement("st-chp8-p223-ruffo-affinity-for-creti", P223, 141, 141, "cand-2304", "cand-0889",
                   "reported_patron_affinity_and_honor_for_artist",
                   "Haskell continues that Ruffo would watch Donato Creti at work for hours and arranged for him to receive the title Cavaliere dello speron d'oro.",
                   "This closes the open p.222 sentence. The honor's conferring authority and date are not stated; retain Haskell's report.",
                   ["cand-2304", "cand-0889", "cand-7745"], extras={"continued_from_segment_id": P222,
                   "continued_from_statement_id": "st-chp8-p222-ruffo-fondness-for-creti-open",
                   "ocr_corrections": []}),
    make_statement("st-chp8-p223-creti-solomon-paintings", P223, 142, 142, "cand-2304", "cand-7722",
                   "owned_at_least_two_paintings_by_creti",
                   "Haskell reports that Ruffo owned at least two paintings by Creti depicting scenes from the life of Solomon.",
                   "The lower bound 'at least two' is preserved; the individual scenes and present locations are not identified.",
                   ["cand-2304", "cand-0889", "cand-7722", "cand-4269"], extras={"minimum_count": 2, "relation_candidate": True}),
    make_statement("st-chp8-p223-creti-dance-of-nymphs", P223, 142, 142, "cand-2304", "cand-0890",
                   "owned_dance_of_nymphs_attributed_to_creti",
                   "The passage also includes Creti's Dance of Nymphs among Ruffo's paintings; Haskell attributes the description capriccio pittoresco with twenty-four figures to the artist's biographer.",
                   "The count and genre description are second-hand as stated; the work's identity beyond the index entry is not independently established.",
                   ["cand-2304", "cand-0889", "cand-0890", "cand-7746"], extras={"figure_count": 24, "attribution_layer": "artist's biographer as reported by Haskell", "relation_candidate": True}),
    make_statement("st-chp8-p223-ruffo-commissions-cignani", P223, 142, 142, "cand-2304", "cand-0750",
                   "commissioned_religious_paintings_and_histories_from",
                   "Haskell includes Carlo Cignani among the leading Bolognese artists from whom Ruffo commissioned religious paintings and histories.",
                   "The source says 'most ... such as'; no individual Cignani work is named here.",
                   ["cand-2304", "cand-0750"], extras={"relation_candidate": True, "work_titles_identified": False}),
    make_statement("st-chp8-p223-ruffo-commissions-franceschini", P223, 142, 142, "cand-2304", "cand-1069",
                   "commissioned_religious_paintings_and_histories_from",
                   "Haskell includes Marcantonio Franceschini among the leading Bolognese artists from whom Ruffo commissioned religious paintings and histories after 1720.",
                   "The date qualifier 'after 1720' belongs to this named example; no individual work is identified here.",
                   ["cand-2304", "cand-1069"], extras={"relation_candidate": True, "time_qualifier": "after 1720", "work_titles_identified": False}),
    make_statement("st-chp8-p223-ruffo-commissions-dal-sole", P223, 142, 142, "cand-2304", "cand-2480",
                   "commissioned_religious_paintings_and_histories_from",
                   "Haskell includes Giovan Gioseffo dal Sole among the leading Bolognese artists from whom Ruffo commissioned religious paintings and histories.",
                   "The source says 'most ... such as'; no individual dal Sole work is named here.",
                   ["cand-2304", "cand-2480"], extras={"relation_candidate": True, "work_titles_identified": False}),
    make_statement("st-chp8-p223-ruffo-commissions-gambarini", P223, 142, 142, "cand-2304", "cand-7723",
                   "commissioned_two_bambocciate_from_gambarini",
                   "Haskell reports that Ruffo also commissioned two bambocciate by Giuseppe Gambarini.",
                   "The two works are not individually titled or located in this passage.",
                   ["cand-2304", "cand-1113", "cand-7723"], extras={"quantity": 2, "genre_as_printed": "bambocciate", "relation_candidate": True}),
    make_statement("st-chp8-p223-ruffo-neapolitan-attachment", P223, 143, 143, "cand-2304", None,
                   "author_characterizes_attachment_to_neapolitan_background",
                   "Haskell says that despite spending nearly all his life in the North, Ruffo remained closely attached to his Neapolitan background.",
                   "This is the author's characterization of Ruffo's attachment, not a statement that he lived mainly in Naples.",
                   ["cand-2304"], extras={"qualification_terms": ["Despite", "almost entirely", "closely attached"]}),
    make_statement("st-chp8-p223-giordano-sent-four-pictures", P223, 143, 143, "cand-1172", "cand-2304",
                   "sent_four_pictures_to",
                   "Haskell reports that Luca Giordano sent four pictures to Ruffo, one of which is described as Hebrew Women singing after crossing the Red Sea.",
                   "Only one of the four pictures is identified on this page; this statement is not an independent provenance verification.",
                   ["cand-1172", "cand-2304", "cand-7724", "cand-7725"], extras={"quantity": 4, "work_group_candidate_id": "cand-7724", "relation_candidate": True}),
    make_statement("st-chp8-p223-hebrew-women-possible-maggiore-link", P223, 143, 143, "cand-7725", "cand-7688",
                   "may_be_connected_with_giordano_work_at_santa_maria_maggiore",
                   "Haskell says the Hebrew Women painting may well have been connected with Giordano's work for S. Maria Maggiore in Bergamo.",
                   "The source's 'may well' is retained; this is a possible connection to the previously described Giordano commission, not a confirmed identity or placement.",
                   ["cand-7725", "cand-1172", "cand-7688", "cand-7627", "cand-7743"], extras={"modality": "may well", "relation_candidate": True}),
    make_statement("st-chp8-p223-solimena-nativity", P223, 143, 144, "cand-2484", "cand-2304",
                   "painted_work_for_patron",
                   "Haskell reports that Francesco Solimena painted a Nativity for Ruffo.",
                   "The painting is not individually identified by date or location here.",
                   ["cand-2484", "cand-2304", "cand-7726"], extras={"relation_candidate": True, "work_candidate_id": "cand-7726"}),
    make_statement("st-chp8-p223-solimena-presentation", P223, 144, 144, "cand-2484", "cand-2304",
                   "painted_work_for_patron",
                   "Haskell reports that Francesco Solimena painted a Presentation for Ruffo.",
                   "The painting's exact subject, date, and location are not specified here.",
                   ["cand-2484", "cand-2304", "cand-7727"], extras={"relation_candidate": True, "work_candidate_id": "cand-7727"}),
    make_statement("st-chp8-p223-ruffo-retirement-to-rome", P223, 144, 144, "cand-2304", "cand-4490",
                   "retired_to_rome_and_turned_to_compatriots",
                   "Haskell says that on retiring to Rome, Ruffo again turned to his Neapolitan compatriots.",
                   "This broad contextual description does not identify every person or commission involved.",
                   ["cand-2304", "cand-4490"]),
    make_statement("st-chp8-p223-salvi-built-chapel", P223, 144, 145, "cand-2347", "cand-7728",
                   "built_chapel_for_ruffo_at_san_lorenzo",
                   "Haskell reports that Nicola Salvi built the rich chapel for Ruffo at S. Lorenzo in Damaso.",
                   "The chapel is recorded as an interior space distinct from the host church; this report is not independently verified.",
                   ["cand-2347", "cand-2304", "cand-7728", "cand-6559"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p223-conca-decorated-chapel", P223, 145, 145, "cand-7728", "cand-0818",
                   "was_decorated_by",
                   "Haskell says Sebastiano Conca decorated Ruffo's chapel at S. Lorenzo in Damaso and also painted other pictures for Ruffo.",
                   "The chapel decoration and Conca's other pictures are reported but not individually identified here.",
                   ["cand-7728", "cand-0818", "cand-2304"], extras={"relation_candidate": True, "ocr_corrections": [ocr[1]]}),
    make_statement("st-chp8-p223-giaquinto-decorated-chapel", P223, 145, 145, "cand-7728", "cand-1165",
                   "was_decorated_by",
                   "Haskell names Corrado Giaquinto as a decorator of Ruffo's chapel at S. Lorenzo in Damaso.",
                   "No specific decorative work is separately identified in this sentence.",
                   ["cand-7728", "cand-1165", "cand-6559"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p223-conca-other-pictures-for-ruffo", P223, 145, 145, "cand-0818", "cand-2304",
                   "painted_other_pictures_for",
                   "Haskell adds that Sebastiano Conca painted other pictures for Ruffo besides decorating the chapel.",
                   "The other pictures are not identified in this passage.",
                   ["cand-0818", "cand-2304"], extras={"relation_candidate": True, "work_titles_identified": False}),
    make_statement("st-chp8-p223-ruffo-opinion-of-roman-artists", P223, 145, 145, "cand-2304", None,
                   "author_reports_little_interest_in_roman_artists",
                   "Haskell says Ruffo found Roman artists to be of little interest.",
                   "This is Haskell's account of Ruffo's taste and does not identify a particular artist or commission.",
                   ["cand-2304"], extras={"speaker": "Haskell"}),
    make_statement("st-chp8-p223-palazzo-cibo-gallery-characterization", P223, 145, 145, "cand-2304", "cand-0746",
                   "gallery_must_have_retained_exotic_and_delicate_flavour",
                   "Haskell infers that Ruffo's gallery in Palazzo Cibo must have retained an exotic and delicate flavour until his death.",
                   "The phrase 'must have' marks the author's inference; it is not a verified description of the gallery at his death.",
                   ["cand-2304", "cand-0746"], extras={"modality": "must have", "qualification_terms": ["exotic", "delicate flavour", "until his death"]}),
    make_statement("st-chp8-p223-raimondo-patron-range", P223, 146, 146, "cand-0467", "cand-3461",
                   "ranged_over_italy_for_pictures",
                   "Haskell introduces Raimondo Buonaccorsi as a patron who ranged freely over Italy for pictures during these years.",
                   "This is the author's summary of his collecting activity; the passage does not enumerate the journeys or pictures.",
                   ["cand-0467", "cand-3461"]),
    make_statement("st-chp8-p223-raimondo-lived-macerata", P223, 146, 147, "cand-0467", "cand-1475",
                   "lived_in_macerata",
                   "Haskell says Raimondo Buonaccorsi lived in Macerata.",
                   "The description 'little Marchigian town' is Haskell's wording; no broader residence history is inferred.",
                   ["cand-0467", "cand-1475"]),
    make_statement("st-chp8-p223-raimondo-born-into-family", P223, 147, 147, "cand-0467", "cand-7729",
                   "born_into_unidentified_family",
                   "Haskell says Raimondo was born in 1669 into an old and important family with extensive ramifications throughout the peninsula.",
                   "The family is not named in this passage; the date and family characterization remain Haskell's report.",
                   ["cand-0467", "cand-7729"], extras={"birth_year": 1669}),
    make_statement("st-chp8-p223-family-church-connection", P223, 147, 147, "cand-7729", "cand-7730",
                   "described_as_having_close_church_connection",
                   "Haskell describes Raimondo's unidentified family as having a particularly close relationship with the Church.",
                   "Neither the institution's exact scope nor the form of the family's relationship is specified.",
                   ["cand-7729", "cand-7730"]),
    make_statement("st-chp8-p223-raimondo-married-francesca", P223, 147, 147, "cand-0467", "cand-0474",
                   "married",
                   "Haskell reports that Raimondo married Francesca Bussi in 1699.",
                   "The marriage date is reported by the source; no additional kinship or family-branch claims are added.",
                   ["cand-0467", "cand-0474"], extras={"time": "1699", "relation_candidate": True}),
    make_statement("st-chp8-p223-francesca-eighteen-children", P223, 147, 147, "cand-0474", None,
                   "bore_eighteen_children_by_1726",
                   "Haskell says Francesca Bussi had borne eighteen children by 1726, one of whom, Simone, was to become a cardinal.",
                   "The source names only Simone and gives no full identity for him; the count and future-tense status are preserved.",
                   ["cand-0474", "cand-0467", "cand-0469"], extras={"quantity": 18, "as_of": 1726}),
    make_statement("st-chp8-p223-francesca-mother-of-simone", P223, 147, 147, "cand-0474", "cand-0469",
                   "mother_of",
                   "The text identifies Simone as one of the eighteen children Francesca Bussi had borne by 1726.",
                   "The indexed candidate is named Cardinal Simone Buonaccorsi, but this passage gives only Simone; retain the identity question for S3.",
                   ["cand-0474", "cand-0469"], extras={"relation_candidate": True, "identity_status": "forename only in this passage"}),
    make_statement("st-chp8-p223-simone-cardinal", P223, 147, 147, "cand-0469", None,
                   "was_to_become_cardinal",
                   "Haskell says that one of Raimondo and Francesca's children, named only as Simone, was to become a Cardinal.",
                   "Future status is retained as written; the index candidate's full identity awaits S3 alignment.",
                   ["cand-0467", "cand-0474", "cand-0469"], extras={"time_qualifier": "future relative to the passage", "identity_status": "forename only in this passage"}),
    make_statement("st-chp8-p223-raimondo-died", P223, 148, 148, "cand-0467", None,
                   "died_in_1743",
                   "Haskell reports that Raimondo Buonaccorsi died in 1743.",
                   "The date is recorded as a book-reported fact and has not been independently checked here.",
                   ["cand-0467"], extras={"death_year": 1743}),
    make_statement("st-chp8-p223-raimondo-characterization-from-limited-letters", P223, 148, 148, "cand-0467", None,
                   "author_characterizes_person_from_few_letters_and_later_writers",
                   "Haskell says that fewer than a handful of traceable letters to and from Raimondo, as transmitted by later writers, suggest an image of an elaborately courteous, proud gentleman deeply attached to established powers and also ambitious with some arrogance.",
                   "This is explicitly a tentative authorial sketch based on sparse, mediated evidence; it is not entered as settled personality fact.",
                   ["cand-0467", "cand-7739", "cand-7740", "cand-7741"], extras={"evidence_limit": "less than a handful of traceable letters", "mediation": "subsequent writers", "modality": "suggest", "qualification_terms": ["suggest", "almost", "shadowy sketch", "until further evidence"]}),
    make_statement("st-chp8-p223-buonaccorsi-palace-and-patronage", P223, 148, 148, "cand-0467", "cand-7731",
                   "author_assesses_palace_decoration_and_patronage",
                   "Haskell says the splendid decoration of Raimondo's palace shows him to have been a patron of great enterprise and interest.",
                   "This is the author's interpretation of the palace decoration; it does not establish who designed or executed it.",
                   ["cand-0467", "cand-7731"]),
    make_statement("st-chp8-p223-palace-superlative-open", P223, 148, 148, "cand-0467", "cand-7731",
                   "author_calls_palace_finest_in_town_open_continuation",
                   "Haskell begins to call the palace the finest in the hill town, but the sentence continues on p.224.",
                   "Keep this claim open until its continuation is read; the place-name and comparison scope continue beyond this segment.",
                   ["cand-0467", "cand-7731"], extras={"continuation_to_segment_id": P224, "continuation_to_source_line": 152, "continuation_status": "open"}),
    make_statement("st-chp8-p223-n2-zanotti-citation", P223, 149, 149, None, "cand-7115",
                   "footnote_citation",
                   "Footnote 2 cites Zanotti, volume I, page 239.",
                   "This is a bibliographic locator only; the cited page was not independently read.",
                   ["cand-7114", "cand-7115"], text_layer="bibliographic citation", extras={"footnote_marker": 2, "printed_page_locator": "p.223 n.2", "volume": "I", "page_start": "239", "page_end": "239"}),
    make_statement("st-chp8-p223-n1-zanotti-citation", NOTES, 386, 386, None, "cand-7115",
                   "footnote_citation",
                   "Footnote 1 cites Zanotti, volume II, page 115.",
                   "Bibliographic locator only; the cited page was not independently read.",
                   ["cand-7114", "cand-7115"], text_layer="bibliographic citation", extras={"footnote_marker": 1, "printed_page_locator": "p.223 n.1", "volume": "II", "page_start": "115", "page_end": "115"}),
    make_statement("st-chp8-p223-n1-crespi-citation", NOTES, 386, 386, None, "cand-6591",
                   "footnote_citation",
                   "Footnote 1 also cites L. Crespi, page 259.",
                   "The book bibliography identifies the work; the cited page was not independently read.",
                   ["cand-7716", "cand-6591"], text_layer="bibliographic citation", extras={"footnote_marker": 1, "printed_page_locator": "p.223 n.1", "page_start": "259", "page_end": "259"}),
    make_statement("st-chp8-p223-n3-dominici-citation", NOTES, 387, 387, None, "cand-4835",
                   "footnote_citation",
                   "Footnote 3 cites De Dominici, volume IV, page 538.",
                   "Bibliographic locator only; the cited page was not independently read.",
                   ["cand-7116", "cand-4835"], text_layer="bibliographic citation", extras={"footnote_marker": 3, "printed_page_locator": "p.223 n.3", "volume": "IV", "page_start": "538", "page_end": "538"}),
    make_statement("st-chp8-p223-n3-moroni-citation", NOTES, 387, 387, None, "cand-7696",
                   "footnote_citation",
                   "Footnote 3 also cites Moroni, volume XII, page 71.",
                   "The multivolume work is identified in the project's existing bibliography candidate; volume XII page 71 was not independently read.",
                   ["cand-5954", "cand-7696"], text_layer="bibliographic citation", extras={"footnote_marker": 3, "printed_page_locator": "p.223 n.3", "volume": "XII", "page_start": "71", "page_end": "71"}),
    make_statement("st-chp8-p223-ruffo-pozzo-portrait", NOTES, 387, 387, "cand-2304", "cand-2033",
                   "commissioned_portrait_from",
                   "The footnote reports that Ruffo commissioned his portrait from Andrea Pozzo.",
                   "The portrait is unidentified here; Pascoli is a cited source, not an independently consulted source in this task.",
                   ["cand-2304", "cand-7742", "cand-2033", "cand-4552"], text_layer="footnote report", extras={"relation_candidate": True, "work_candidate_id": "cand-7742"}),
    make_statement("st-chp8-p223-n3-pascoli-citation", NOTES, 387, 387, None, "cand-4552",
                   "footnote_citation",
                   "The portrait report cites Pascoli, volume II, page 265.",
                   "Bibliographic locator only; the cited page was not independently read.",
                   ["cand-1842", "cand-4552"], text_layer="bibliographic citation", extras={"footnote_marker": 3, "printed_page_locator": "p.223 n.3", "volume": "II", "page_start": "265", "page_end": "265"}),
    make_statement("st-chp8-p223-n4-orlando-acknowledgement", NOTES, 388, 388, "cand-0466", "cand-0467",
                   "made_surviving_material_available_to_haskell",
                   "Haskell thanks Count Orlando Buonaccorsi for making available what little material survives about his ancestor Raimondo.",
                   "This records Haskell's acknowledgement, not an independent assessment of the surviving material.",
                   ["cand-0466", "cand-0467"], text_layer="acknowledgement"),
    make_statement("st-chp8-p223-n4-miller-photos-and-attributions", NOTES, 388, 388, "cand-7735", "cand-7733",
                   "supplied_gallery_photographs_and_suggested_attributions",
                   "Haskell thanks Dwight Miller for copies of photographs he took of the gallery and for suggesting many attributions.",
                   "Photographs and attribution suggestions were not independently consulted or verified here.",
                   ["cand-7735", "cand-7733", "cand-0467"], text_layer="acknowledgement"),
    make_statement("st-chp8-p223-n4-ubaldi-family-information", NOTES, 388, 388, "cand-7734", "cand-7729",
                   "source_for_some_family_information",
                   "Haskell says some information about the family can be found in Silvio Ubaldi.",
                   "The publication or document is not identified in this note; do not infer a particular title.",
                   ["cand-7734", "cand-7729"], text_layer="footnote report"),
    make_statement("st-chp8-p223-n4-memoria-source", NOTES, 388, 388, "cand-7732", "cand-0467",
                   "contains_few_details_about_raimondo_and_remained_with_family",
                   "Haskell reports a few details about Raimondo in a small manuscript Memoria written by his wife in 1726 and still belonging to the family.",
                   "The manuscript was not independently consulted; Francesca Bussi is the likely referent of 'his wife' from the adjacent body text, but authorship identity remains for S3.",
                   ["cand-7732", "cand-0474", "cand-0467", "cand-7729"], text_layer="footnote report", extras={"date": 1726, "relation_candidate": True}),
    make_statement("st-chp8-p223-n5-letter-1705", P223, 150, 150, "cand-0467", "cand-7736",
                   "wrote_letter_to",
                   "Footnote 5 identifies a letter from Raimondo Buonaccorsi to Tiberio Cenci dated 23 February 1705, cited as Vat. Lat. 9041, c.39, in the Vatican Library.",
                   "The letter's contents and catalogue record were not consulted; shelfmark text is corrected against the page image.",
                   ["cand-0467", "cand-7736", "cand-7738", "cand-7739"], text_layer="footnote report", extras={"date": "1705-02-23", "shelfmark": "Vat. Lat. 9041, c.39", "document_candidate_id": "cand-7739", "repository_candidate_id": "cand-7738", "relation_candidate": True, "ocr_corrections": [ocr[4], ocr[5], ocr[6]]}),
    make_statement("st-chp8-p223-n5-letter-1737", P223, 150, 150, "cand-7737", "cand-0467",
                   "wrote_letter_to",
                   "Footnote 5 identifies a letter from Alessandro Borgia, titled Archbishop and Prince of Fermo, to Raimondo Buonaccorsi dated 13 September 1737, cited as Borg. Lat. 236, c.87, in the Vatican Library.",
                   "The letter's contents and catalogue record were not consulted; shelfmark text is corrected against the page image.",
                   ["cand-7737", "cand-0467", "cand-7738", "cand-7740", "cand-7744"], text_layer="footnote report", extras={"date": "1737-09-13", "shelfmark": "Borg. Lat. 236, c.87", "document_candidate_id": "cand-7740", "repository_candidate_id": "cand-7738", "relation_candidate": True, "ocr_corrections": [ocr[4], ocr[5], ocr[7]]}),
    make_statement("st-chp8-p223-n5-letter-1742", P223, 150, 150, "cand-7737", "cand-0467",
                   "wrote_letter_to",
                   "Footnote 5 identifies a second letter from Alessandro Borgia to Raimondo Buonaccorsi dated 7 December 1742, cited as Borg. Lat. 236, c.125, in the Vatican Library.",
                   "'As (ii)' carries the sender, recipient, and repository from the preceding letter; the letter's contents and catalogue record were not consulted.",
                   ["cand-7737", "cand-0467", "cand-7738", "cand-7741", "cand-7744"], text_layer="footnote report", extras={"date": "1742-12-07", "shelfmark": "Borg. Lat. 236, c.125", "document_candidate_id": "cand-7741", "repository_candidate_id": "cand-7738", "relation_candidate": True, "ocr_corrections": [ocr[4], ocr[5], ocr[8]]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")
prior_id = "st-chp8-p222-ruffo-fondness-for-creti-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected p.222 open Creti statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continued_to_segment_id": P223,
    "continued_to_source_line": 141,
    "continuation_closed_by_statement_id": "st-chp8-p223-ruffo-affinity-for-creti",
})

new_coverage = []
for row in coverage_rows:
    sid = row["segment_id"]
    if sid == P222:
        row.update({"disposition": "reviewed", "migration_status": "complete",
                    "source_line_ranges": "L127-138", "note": "p.222 Creti sentence closes at p.223 L141."})
    elif sid == P223:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L140-150", "note": "p.223 read against CHP-8.pdf physical page 25; final sentence about Raimondo Buonaccorsi's palace continues on p.224 L152."})
    elif sid == NOTES:
        row.update({"source_line_ranges": "L373-388", "migration_status": "partial",
                    "note": "p.223 notes 1, 3 and 4 migrated; notes 2 and 5 are embedded in the p.223 body segment; later consolidated notes remain queued by printed page."})
    new_coverage.append(row)

new_candidate_id_set = {row[0] for row in new_candidates}
candidate_keys = {(row["canonical_name"], row["suggested_type"])
                  for row in candidate_rows if not row["index_entry_id"] and row["candidate_id"] not in new_candidate_id_set}
for candidate_id, name, kind, origin, detail in new_candidates:
    if (name, kind) in candidate_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    candidate_keys.add((name, kind))

preview = {
    "mode": "dry-run", "candidate_additions": len(new_candidates),
    "mention_additions": len(new_mentions), "statement_additions": len(new_statements),
    "statement_ids": [row["statement_id"] for row in new_statements],
    "continuations": [
        {"statement_id": prior_id, "status": "closed", "to": P223, "line": 141},
        {"statement_id": "st-chp8-p223-palace-superlative-open", "status": "open", "to": P224, "line": 152},
    ],
    "coverage_updates": {
        P222: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L127-138"},
        P223: {"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L140-150"},
        NOTES: {"source_line_ranges": "L373-388", "migration_status": "partial"},
    },
    "ocr_corrections": [f"L{x['source_line']} {x['ocr']} -> {x['print']}" for x in ocr],
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the preflighted S2 migration")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (TABLES / "entity-candidates.csv", TABLES / "mentions.csv", TABLES / "book-statements.jsonl", TABLES / "s2-coverage.csv"):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

candidate_rows.extend([])  # new candidates were appended during preflight construction.
patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
patched_statements.extend(new_statements)
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", patched_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, new_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
