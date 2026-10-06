"""Controlled S2 migration for Chapter 8 printed page 225 and notes 1-9."""
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
P224 = "chp-8:08_CHP-8_sec_ii:l152-161"
P225 = "chp-8:08_CHP-8_sec_ii:l163-177"
P226 = "chp-8:08_CHP-8_sec_ii:l179-188"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P224, P225, P226, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p225-20261001"


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

expected = {
    P224: ("reviewed", "partial", "L152-161"),
    P225: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-391":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P225 for row in mention_rows + statement_rows):
    raise SystemExit("p.225 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7765", "Raimondo Buonaccorsi art collection at Macerata", "", 175,
     "Collection is a meaningful referent distinct from the palace and its gallery; current taxonomy has no collection type, so retain type as pending."),
    ("cand-7766", "Marcantonio Franceschini's Libro dei Conti (Biblioteca Comunale, Bologna, MS B.4067)", "archive", 177,
     "Manuscript account book cited as recording a 1000-lire payment; the manuscript was not consulted."),
    ("cand-7767", "Pascoli's unpublished life of Antonio Balestra (Biblioteca Augusta, Perugia, MS 1383)", "archive", 394,
     "Specific life/section cited for Balestra's Aeneid fable; possible relationship to other contents of MS 1383 remains for S3."),
    ("cand-7768", "Unidentified D. Miller publication from 1958", "archive", 397,
     "Footnote gives author abbreviation and year only; title and publication details are unresolved."),
    ("cand-7769", "d'Orsi (identity unresolved)", "person", 398,
     "Surname-only author cited by Haskell at pp. 31-32; first name and bibliographic identity are not supplied here."),
    ("cand-7770", "Unidentified d'Orsi publication on Giaquinto's work in Macerata (pp. 31-32)", "archive", 398,
     "Source cited second-hand by Haskell; title and edition are unresolved and the cited pages were not read."),
    ("cand-7771", "Pinacoteca Nazionale, Bologna", "institution", 396,
     "Museum named as the reported present location of Crespi's Leto painting."),
    ("cand-7772", "Mercury (mythological figure represented in Franceschini's Aeneas painting)", "person", 177,
     "Named in the title Mercury awaking Aeneas; distinguish the mythological figure from works titled Mercury."),
    ("cand-7773", "Leto (mythological figure represented in Crespi's painting)", "person", 172,
     "Named in the title Leto turning the Shepherds into Frogs."),
    ("cand-7774", "Andromache (mythological figure named in the dal Sole canvas)", "person", 165,
     "Named in the title Andromache weeping before Aeneas; work identity remains aligned to the index subentry cand-2481."),
    ("cand-7775", "Four fables painted by Giuseppe Maria Crespi for Raimondo Buonaccorsi", "work", 172,
     "Haskell reports a group of four; only the surviving Leto painting is identified here."),
    ("cand-7776", "Further Aeneid scenes painted by Gambarini, Franceschini, Lazzarini and Balestra for the gallery", "work", 170,
     "Unspecified group of further scenes; no individual titles or count are supplied in this passage."),
    ("cand-7777", "Other unidentified pictures by Gregorio Lazzarini for the Buonaccorsi", "work", 393,
     "Additional works reported by Haskell through da Canal; no titles are supplied."),
    ("cand-7778", "Unidentified pagan scenes by Giuseppe Gambarini for Raimondo Buonaccorsi", "work", 173,
     "Commissioned group reported by Haskell; individual subjects are not given."),
    ("cand-7779", "Unidentified modern paintings in other rooms of Raimondo Buonaccorsi's palace", "work", 171,
     "Haskell contrasts these works with the Aeneid scenes but identifies no artists or titles here."),
    ("cand-7780", "Antonio Balestra's unnamed Aeneid fable for the Buonaccorsi", "work", 394,
     "The subject is described only as una favola d'Enea; no individual title is supplied."),
    ("cand-7781", "Vincenzo da Canal", "person", 393,
     "Author cited for the Lazzarini works; reuse candidate source cand-6593 for his Vita."),
    ("cand-7782", "Mezentius (mythological figure named in Lazzarini's painting title)", "person", 393,
     "Named in The Battle of Aeneas and Mezentius."),
    ("cand-7783", "Unidentified minor decoration in window niches in Macerata attributed to Giaquinto by d'Orsi", "work", 398,
     "Second-hand attribution reported by Haskell; no building is identified, so do not assign it to the Buonaccorsi palace."),
]
candidate_ids = {row["candidate_id"] for row in candidate_rows}
if any(candidate_id in candidate_ids for candidate_id, *_ in new_candidates):
    raise SystemExit("new candidate ID already exists")
existing_candidate_keys = {(row["canonical_name"], row["suggested_type"])
                           for row in candidate_rows if not row["index_entry_id"]}
new_candidate_keys = set()
for candidate_id, name, kind, line, detail in new_candidates:
    if (name, kind) in existing_candidate_keys or (name, kind) in new_candidate_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_candidate_keys.add((name, kind))
    anchor_segment = P225 if 163 <= line <= 177 else NOTES
    candidate_rows.append({
        "candidate_id": candidate_id, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": kind, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{anchor_segment}#L{line}",
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
    line = source_lines[source_line - 1]
    offset = line_offsets[(segment_id, source_line)]
    found_at = -1
    search_at = 0
    for _ in range(occurrence + 1):
        found_at = line.find(surface, search_at)
        if found_at < 0:
            raise SystemExit(f"mention surface not found at L{source_line}: {surface!r} #{occurrence}")
        search_at = found_at + 1
    start = offset + found_at
    end = start + len(surface)
    key = (segment_id, str(start), str(end))
    if key in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == key for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


# Body: close p.224's open sentence and preserve Haskell's distinctions and evaluative language.
mention(P225, 164, "m-chp8-p225-bologna-1", "cand-3398", "Bologna", "City in which dal Sole was working.")
mention(P225, 164, "m-chp8-p225-dal-sole", "cand-2480", "Giovan Gioseffo dal Sole", "Painter working on his own Andromache canvas.")
mention(P225, 165, "m-chp8-p225-andromache-work", "cand-2481", "Andromache weeping before Aeneas", "Reuse dal Sole's index subentry for the specific canvas.")
mention(P225, 165, "m-chp8-p225-andromache", "cand-7774", "Andromache", "Mythological figure named in the canvas title.")
mention(P225, 165, "m-chp8-p225-aeneas-title", "cand-4164", "Aeneas", "Mythological figure named in the canvas title.")
mention(P225, 165, "m-chp8-p225-dido-arrival", "cand-2486", "its arrival", "Coreference to Solimena's Dido painting, which arrived at the palace.")
mention(P225, 166, "m-chp8-p225-palace", "cand-7731", "Buonaccorsi palace", "Raimondo's palace in Macerata.")
mention(P225, 166, "m-chp8-p225-macerata", "cand-1475", "Macerata", "City where the palace is located.")
mention(P225, 166, "m-chp8-p225-solimena-rival", "cand-2484", "his Neapolitan rival", "Coreference to Francesco Solimena, named on p.224; regional descriptor retained.")
mention(P225, 167, "m-chp8-p225-rome", "cand-4490", "Rome", "City named in Haskell's cultural-exchange characterization.")
mention(P225, 168, "m-chp8-p225-gallery", "cand-7749", "the gallery", "Raimondo's long gallery and its Aeneid decoration.")
mention(P225, 168, "m-chp8-p225-gambarini-1", "cand-1113", "Giuseppe Gambarini", "Painter named among the gallery artists.")
mention(P225, 169, "m-chp8-p225-franceschini", "cand-1069", "Marcantonio Franceschini", "Painter named among the gallery artists.")
mention(P225, 169, "m-chp8-p225-bologna-2", "cand-3398", "Bologna", "City associated with Franceschini in the passage.")
mention(P225, 169, "m-chp8-p225-lazzarini", "cand-1368", "Gregorio Lazzarini", "Painter named among the gallery artists.")
mention(P225, 169, "m-chp8-p225-balestra", "cand-0168", "Antonio Balestra", "Painter named among the gallery artists.")
mention(P225, 170, "m-chp8-p225-venice", "cand-3401", "Venice", "City associated with Balestra and the works described.")
mention(P225, 170, "m-chp8-p225-scenes-poem", "cand-7776", "further scenes from the poem", "Unspecified group of scenes by the four named painters.")
mention(P225, 170, "m-chp8-p225-aeneid-poem", "cand-7763", "the poem", "Coreference to Virgil's Aeneid.")
mention(P225, 170, "m-chp8-p225-their-works", "cand-7776", "Their works", "Coreference to the further Aeneid scenes just mentioned.")
mention(P225, 171, "m-chp8-p225-other-rooms-works", "cand-7779", "works by the more interesting", "Unidentified works in other palace rooms; preserve Haskell's evaluative wording.")
mention(P225, 171, "m-chp8-p225-raimondo-palace", "cand-7731", "Raimondo", "Building containing the other rooms.")
mention(P225, 171, "m-chp8-p225-aeneid-scenes", "cand-7776", "the scenes from the Aeneid", "Coreference to the gallery's further Aeneid paintings.")
mention(P225, 171, "m-chp8-p225-aeneid", "cand-7763", "the Aeneid", "Epic named as the subject source of the gallery scenes.")
mention(P225, 172, "m-chp8-p225-raimondo-inference", "cand-0467", "Raimondo", "Subject of Haskell's explicitly inferential statement about artistic awareness.")
mention(P225, 172, "m-chp8-p225-crespi", "cand-0871", "Crespi", "Giuseppe Maria Crespi, named as painter of four fables.")
mention(P225, 172, "m-chp8-p225-crespi-fables", "cand-7775", "four fables", "Group of four commissioned works; only one is identified here.")
mention(P225, 172, "m-chp8-p225-leto-work", "cand-0880", "Leto turning the Shepherds into Frogs", "Reuse Crespi's index subentry for the surviving painting.")
mention(P225, 172, "m-chp8-p225-leto", "cand-7773", "Leto", "Mythological figure named in the work title.")
mention(P225, 173, "m-chp8-p225-gambarini-2", "cand-1113", "Giuseppe Gambarini", "Painter also commissioned to paint pagan scenes.")
mention(P225, 173, "m-chp8-p225-pagan-scenes", "cand-7778", "pagan scenes", "Unidentified group commissioned for the collection.")
mention(P225, 173, "m-chp8-p225-crespi-humour", "cand-0871", "Crespi", "Painter used as a contrast to Gambarini's characterization.")
mention(P225, 174, "m-chp8-p225-collection-records", "cand-7765", "the collection", "Raimondo Buonaccorsi's art collection at Macerata; type remains pending.")
mention(P225, 175, "m-chp8-p225-giaquinto", "cand-1165", "Corrado Giaquinto", "Painter reported to have worked for the Buonaccorsi.")
mention(P225, 175, "m-chp8-p225-buonaccorsi", "cand-7729", "the Buonaccorsi", "Family/patronal referent; exact members are not specified.")
mention(P225, 175, "m-chp8-p225-collection-split", "cand-7765", "the pictures", "Pictures in the Buonaccorsi collection, reported as repeatedly divided among family members.")
mention(P225, 175, "m-chp8-p225-family-split", "cand-7729", "members of the family", "Family members among whom the pictures were repeatedly split.")
mention(P225, 175, "m-chp8-p225-raimondo-enlightenment", "cand-0467", "Raimondo", "Subject of Haskell's tentative comparison to patrons of the Enlightenment.")
mention(P225, 175, "m-chp8-p225-enlightenment", "cand-0974", "the dawning Age of the Enlightenment", "Reuse the index concept for Enlightenment in Italy; this is Haskell's tentative framing.")

# Footnote citations and reports; statements remain at the source's reported level.
mention(NOTES, 392, "m-chp8-p225-n1-zanotti-citation", "cand-7115", "Zanotti, I, p. 305", "Footnote 1 citation; cited page was not independently read.")
mention(NOTES, 392, "m-chp8-p225-n1-zanotti-author", "cand-7114", "Zanotti", "Author nested within the citation span.")
mention(P225, 176, "m-chp8-p225-n2-miller-1963", "cand-7757", "1963", "One of two abbreviated D. Miller citations.")
mention(P225, 176, "m-chp8-p225-n2-miller-author", "cand-7735", "D. Miller", "Abbreviated author; identity with p.223's Dwight Miller remains for S3.")
mention(P225, 176, "m-chp8-p225-n2-miller-1964", "cand-7758", "1964", "Second abbreviated D. Miller citation.")
mention(P225, 177, "m-chp8-p225-n3-franceschini", "cand-1069", "Franceschini", "Painter credited in the footnote report.")
mention(P225, 177, "m-chp8-p225-n3-mercury-work", "cand-1071", "Mercury awaking Aeneas", "Reuse the Franceschini work-specific index candidate.")
mention(P225, 177, "m-chp8-p225-n3-mercury", "cand-7772", "Mercury", "Mythological figure named in the work title.")
mention(P225, 177, "m-chp8-p225-n3-aeneas", "cand-4164", "Aeneas", "Mythological figure named in the work title.")
mention(P225, 177, "m-chp8-p225-n3-zanotti-citation", "cand-7115", "Zanotti, I, p. 236", "Citation to Zanotti supporting the work attribution; not independently read.")
mention(P225, 177, "m-chp8-p225-n3-zanotti-author", "cand-7114", "Zanotti", "Author nested within the citation span.")
mention(P225, 177, "m-chp8-p225-n3-account-book", "cand-7766", "Libra dei Conti", "OCR spelling; physical page reads Libro dei Conti.")
mention(P225, 177, "m-chp8-p225-n3-library", "cand-7386", "Biblioteca Comunale", "Repository identified by the page image; manuscript not consulted.")
mention(P225, 177, "m-chp8-p225-n3-bologna", "cand-3398", "Bologna", "City in the repository name.")
mention(P225, 177, "m-chp8-p225-n3-shelfmark", "cand-7766", "MS. B.4067", "Shelfmark for the cited artist's account book.")
mention(NOTES, 393, "m-chp8-p225-n4-lazzarini", "cand-1368", "Lazzarini", "Painter named in the report attributed to da Canal.")
mention(NOTES, 393, "m-chp8-p225-n4-death-dido-work", "cand-1372", "The Death of Dido", "Reuse Lazzarini's work-specific index candidate.")
mention(NOTES, 393, "m-chp8-p225-n4-dido", "cand-4163", "Dido", "Mythological figure named in the work title.")
mention(NOTES, 393, "m-chp8-p225-n4-battle-work", "cand-1369", "The Battle of Aeneas and Mezentius", "Reuse Lazzarini's work-specific index candidate.")
mention(NOTES, 393, "m-chp8-p225-n4-aeneas", "cand-4164", "Aeneas", "Mythological figure named in the work title.")
mention(NOTES, 393, "m-chp8-p225-n4-mezentius", "cand-7782", "Mezentius", "Mythological figure named in the work title.")
mention(NOTES, 393, "m-chp8-p225-n4-other-works", "cand-7777", "other pictures", "Unspecified additional Lazzarini works reported for the family.")
mention(NOTES, 393, "m-chp8-p225-n4-family", "cand-7729", "the family", "Buonaccorsi family, without specifying which members commissioned the pictures.")
mention(NOTES, 393, "m-chp8-p225-n4-dacanal-citation", "cand-6593", "da Canal, p. 38", "Citation to Vincenzo da Canal's Vita; the cited page was not independently read.")
mention(NOTES, 393, "m-chp8-p225-n4-dacanal-author", "cand-7781", "da Canal", "Author mention nested within the citation span.")
mention(NOTES, 394, "m-chp8-p225-n5-balestra", "cand-0168", "Balcstra", "OCR spelling; physical page reads Balestra.")
mention(NOTES, 394, "m-chp8-p225-n5-balestra-work", "cand-7780", "una favola d'Enea", "Unspecified Aeneid fable attributed to Balestra for the Buonaccorsi.")
mention(NOTES, 394, "m-chp8-p225-n5-family", "cand-7729", "the Buonaccorsi", "Family/patronal referent in the reported commission.")
mention(NOTES, 394, "m-chp8-p225-n5-pascoli-life", "cand-7767", "unpublished Use of the artist", "OCR reads 'Use'; the physical page reads 'life'.")
mention(NOTES, 394, "m-chp8-p225-n5-pascoli", "cand-1842", "Pascoli", "Author named for the unpublished life.")
mention(NOTES, 394, "m-chp8-p225-n5-biblioteca-augusta", "cand-3531", "ioteca Augusta", "OCR is damaged; physical page reads Biblioteca Augusta.")
mention(NOTES, 394, "m-chp8-p225-n5-perugia", "cand-3532", "Perugia", "City of the cited library.")
mention(NOTES, 394, "m-chp8-p225-n5-ms1383", "cand-7767", "MS. 1383", "Shelfmark for the cited unpublished life.")
mention(NOTES, 395, "m-chp8-p225-n6-zanotti-citation", "cand-7115", "Zanotti, 11, p. 52", "OCR reads 11; the physical page reads volume II, p.52; page not independently read.")
mention(NOTES, 395, "m-chp8-p225-n6-zanotti-author", "cand-7114", "Zanotti", "Author nested within the citation span.")
mention(NOTES, 396, "m-chp8-p225-n7-leto-picture", "cand-0880", "This picture", "Coreference to Crespi's Leto painting on p.225 L172.")
mention(NOTES, 396, "m-chp8-p225-n7-pinacoteca", "cand-7771", "the Pinacoteca Nazionale", "Reported current holding institution for the painting.")
mention(NOTES, 396, "m-chp8-p225-n7-bologna", "cand-3398", "Bologna", "City locating the Pinacoteca Nazionale.")
mention(NOTES, 397, "m-chp8-p225-n8-miller-publication", "cand-7768", "D. Miller, 1958", "Bibliographic citation; title and page details are not supplied.")
mention(NOTES, 397, "m-chp8-p225-n8-miller-author", "cand-7735", "D. Miller", "Abbreviated author; identity with p.223's Dwight Miller remains for S3.")
mention(NOTES, 398, "m-chp8-p225-n9-ricci-citation", "cand-7755", "Amico Ricci, II, p. 436", "Citation; cited page was not independently read.")
mention(NOTES, 398, "m-chp8-p225-n9-ricci-author", "cand-7756", "Amico Ricci", "Author nested within the citation span.")
mention(NOTES, 398, "m-chp8-p225-n9-collection", "cand-7765", "the collection", "Buonaccorsi art collection at Macerata, type pending.")
mention(NOTES, 398, "m-chp8-p225-n9-giaquinto", "cand-1165", "Giaquinto", "Painter discussed in Haskell's observation and d'Orsi's reported account.")
mention(NOTES, 398, "m-chp8-p225-n9-dorsi-source", "cand-7770", "Orsi (pp. 31-2)", "OCR has damaged the apostrophe; title and edition are unresolved.")
mention(NOTES, 398, "m-chp8-p225-n9-dorsi-author", "cand-7769", "Orsi", "Surname-only author mention, nested in the citation.")
mention(NOTES, 398, "m-chp8-p225-n9-macerata", "cand-1475", "Macerata", "Geographic scope of d'Orsi's reported account.")
mention(NOTES, 398, "m-chp8-p225-n9-window-decoration", "cand-7783", "some very minor decoration in the window niches", "Unidentified decorative work in Macerata; the source does not name its building.")


ocr = [
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 164, "ocr": "own. canvas", "print": "own canvas", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 171, "ocr": "in-some", "print": "in some", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 175, "ocr": "forthe", "print": "for the", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 176, "ocr": "2D. Miller", "print": "2 D. Miller", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 177, "ocr": '" 3 -Franceschini', "print": "3 Franceschini", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 177, "ocr": "Libra dei Conti", "print": "Libro dei Conti", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 394, "ocr": "8 Balcstra", "print": "5 Balestra", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 394, "ocr": "unpublished Use of the artist", "print": "unpublished life of the artist", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 394, "ocr": "Bib\ufffd\ufffd.ioteca Augusta", "print": "Biblioteca Augusta", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 395, "ocr": "Zanotti, 11, p. 52", "print": "Zanotti, II, p. 52", "basis": "CHP-8.pdf physical page 27."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 398, "ocr": "d\ufffd\ufffdOrsi", "print": "d'Orsi", "basis": "CHP-8.pdf physical page 27."},
]


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", extras=None):
    qualifiers = {
        "source_line_start": first_line, "source_line_end": last_line,
        "printed_page": 225, "pdf_physical_page": 27,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if extras:
        qualifiers.update(extras)
    return {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": quote(segment_id, first_line, last_line),
        "origin": "book", "source_file": segment_by_id[segment_id]["source_file"],
    }


new_statements = [
    make_statement("st-chp8-p225-dido-interest-closes", P225, 164, 164, "cand-2486", None,
                   "aroused_great_enthusiasm_and_interest",
                   "Haskell completes the p.224 sentence: Solimena's Dido painting aroused the greatest enthusiasm and interest.",
                   "This closes the p.224 open continuation; the following Dal Sole episode is a separate claim.",
                   ["cand-2486"], extras={"continued_from_segment_id": P224,
                   "continued_from_statement_id": "st-chp8-p224-dido-enthusiasm-open", "continuation_status": "closed",
                   "ocr_corrections": [ocr[0]]}),
    make_statement("st-chp8-p225-dal-sole-visits-dido", P225, 164, 166, "cand-2480", "cand-2486",
                   "visited_palace_to_see_arrived_painting",
                   "Haskell reports that Giovan Gioseffo dal Sole, working on his own Andromache canvas in Bologna, heard that Solimena's Dido painting had arrived and insisted on coming to the Buonaccorsi palace to see it.",
                   "The passage reports a visit prompted by the painting's arrival; it does not say dal Sole commissioned or evaluated it in writing.",
                   ["cand-2480", "cand-2481", "cand-7774", "cand-4164", "cand-2486", "cand-7731", "cand-3398", "cand-1475", "cand-2484"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p225-rome-cultural-exchange", P225, 166, 167, "cand-4490", None,
                   "author_says_rome_no_longer_cultural_exchange_centre",
                   "Haskell presents dal Sole's cross-regional visit as proof that Rome was no longer the great centre of cultural exchange it had once been.",
                   "This is Haskell's historical interpretation, not a quantified measure of cultural exchange.",
                   ["cand-2480", "cand-4490"], extras={"speaker_judgment": True}),
    make_statement("st-chp8-p225-aeneid-artists-and-evaluation", P225, 168, 170, "cand-7776", "cand-7763",
                   "artists_produced_further_scenes_and_author_criticizes_style",
                   "Haskell says Gambarini, Franceschini, Lazzarini and Balestra produced further Aeneid scenes for the gallery, then judges their works clumsy and unconvincing and the large-scale romantic history-painting tradition an empty academic exercise.",
                   "The evaluation is Haskell's; it is not an independently assessed quality judgment.",
                   ["cand-1113", "cand-1069", "cand-1368", "cand-0168", "cand-7776", "cand-7763", "cand-7749"], extras={"relation_candidate": True, "speaker_judgment": True}),
    make_statement("st-chp8-p225-modern-works-in-palace-rooms", P225, 171, 172, "cand-7779", "cand-7731",
                   "other_rooms_contained_works_by_modern_painters",
                   "Haskell contrasts the Aeneid scenes in the gallery with unidentified works by more interesting and modern painters in other rooms of Raimondo's palace, inferring that Raimondo must have understood their essential qualities.",
                   "The phrase 'must have' marks Haskell's inference; no artists or works in the other rooms are identified here.",
                   ["cand-7779", "cand-7731", "cand-0467", "cand-7776"], extras={"modality": "must have", "speaker_judgment": True, "ocr_corrections": [ocr[1]]}),
    make_statement("st-chp8-p225-crespi-four-fables", P225, 172, 172, "cand-0871", "cand-7775",
                   "required_to_paint_four_fables_for_patron",
                   "Haskell says Crespi, though unsuited to heroic melodrama, was required to paint four fables for Raimondo's collection.",
                   "The four works are not individually titled here; retain Haskell's characterization of Crespi's suitability as evaluation.",
                   ["cand-0871", "cand-7775", "cand-0467", "cand-7765"], extras={"quantity": 4, "relation_candidate": True}),
    make_statement("st-chp8-p225-crespi-leto-surviving-work", P225, 172, 172, "cand-0871", "cand-0880",
                   "surviving_fable_depicts_leto_and_shepherds",
                   "Haskell identifies the one surviving fable as Leto turning the Shepherds into Frogs and praises the engaging irony of Crespi's interpretation.",
                   "The survival and interpretation are reported by Haskell; the work's present location is supplied separately in footnote 7.",
                   ["cand-0871", "cand-0880", "cand-7773"], extras={"speaker_judgment": True}),
    make_statement("st-chp8-p225-gambarini-pagan-scenes", P225, 173, 173, "cand-1113", "cand-7778",
                   "commissioned_to_paint_pagan_scenes",
                   "Haskell says Giuseppe Gambarini was also commissioned to paint pagan scenes and contrasts his placid, sensual manner with Crespi's humour.",
                   "The scenes are not individually identified; style comparison is Haskell's characterization.",
                   ["cand-1113", "cand-7778", "cand-0871", "cand-0467"], extras={"relation_candidate": True, "speaker_judgment": True}),
    make_statement("st-chp8-p225-antique-and-christian-themes-as-genre", P225, 173, 173, None, None,
                   "author_characterizes_themes_as_pretexts_for_genre",
                   "Haskell places both Gambarini and Crespi in an eighteenth-century shift that turned themes from antiquity and Christianity into pretexts for genre painting.",
                   "This is an authorial art-historical interpretation, not a claim that either painter abandoned the named themes.",
                   ["cand-1113", "cand-0871"], extras={"speaker_judgment": True}),
    make_statement("st-chp8-p225-few-records-of-collection", P225, 174, 174, "cand-7765", None,
                   "author_reports_few_records_survive",
                   "Haskell says that apart from the works of the named masters, few records of the Buonaccorsi collection survive.",
                   "This reports the state of records known to Haskell, not absence of the collection or its works.",
                   ["cand-7765"]),
    make_statement("st-chp8-p225-giaquinto-reported-work-and-little-trace", P225, 175, 175, "cand-1165", "cand-7729",
                   "reported_to_have_worked_for_buonaccorsi_but_little_trace",
                   "Haskell says little or no trace is found of Corrado Giaquinto, who is reported to have worked for the Buonaccorsi.",
                   "The reported work and the scarcity of surviving evidence are both retained; no specific work is named.",
                   ["cand-1165", "cand-7729"], extras={"relation_candidate": True, "qualification_terms": ["little or no trace", "is reported"]}),
    make_statement("st-chp8-p225-collection-divided-and-no-inventory", P225, 175, 175, "cand-7765", "cand-7729",
                   "pictures_split_among_family_and_no_inventory_survives",
                   "Haskell says the collection's pictures were repeatedly divided among family members and that no inventory survived.",
                   "The statement reports dispersed pictures and a missing inventory; it does not establish a complete present-day object list.",
                   ["cand-7765", "cand-7729"], extras={"relation_candidate": True, "ocr_corrections": [ocr[2]]}),
    make_statement("st-chp8-p225-enlightenment-patron-inference-open", P225, 175, 175, "cand-0467", "cand-0974",
                   "may_have_been_enlightenment_patron_open_continuation",
                   "Haskell tentatively suggests Raimondo may have been among Enlightenment patrons whose public galleries looked to the past while private apartments held smaller, more intimate pictures expressing a new sensibility.",
                   "Both 'possible to suggest' and 'may have been' are retained; the contrast continues on p.226 L180.",
                   ["cand-0467", "cand-0974", "cand-7765"], extras={"modality": ["possible to suggest", "may have been"], "continuation_status": "open", "continuation_to_segment_id": P226, "continuation_to_source_line": 180, "ocr_corrections": [ocr[2]]}),
    make_statement("st-chp8-p225-n1-zanotti-citation", NOTES, 392, 392, "cand-7114", "cand-7115",
                   "cites_source",
                   "Footnote 1 cites Zanotti, volume I, page 305.",
                   "The citation is page-image verified; the cited page was not independently read.",
                   ["cand-7114", "cand-7115"], text_layer="footnote citation", extras={"relation_candidate": False}),
    make_statement("st-chp8-p225-n2-miller-citations", P225, 176, 176, "cand-7735", None,
                   "cites_two_publications_by_abbreviated_author",
                   "Footnote 2 cites D. Miller, 1963 and 1964.",
                   "Titles and page details are absent; identity with Dwight Miller acknowledged on p.223 remains an S3 alignment question.",
                   ["cand-7735", "cand-7757", "cand-7758"], text_layer="footnote citation", extras={"relation_candidate": False, "ocr_corrections": [ocr[3]]}),
    make_statement("st-chp8-p225-n3-franceschini-mercury-painting", P225, 177, 177, "cand-1069", "cand-1071",
                   "painted_work_and_received_1000_lire",
                   "Footnote 3 reports that Franceschini painted Mercury awaking Aeneas and that an entry in his Libro dei Conti shows he was paid 1000 lire.",
                   "The note cites Zanotti and a manuscript account book; neither source was independently consulted, and the payment is reported without an explicit transaction date.",
                   ["cand-1069", "cand-1071", "cand-7772", "cand-4164", "cand-7115", "cand-7766", "cand-7386", "cand-3398"], text_layer="footnote report",
                   extras={"relation_candidate": True, "amount": {"value": 1000, "currency": "lire"}, "source_candidate_ids": ["cand-7115", "cand-7766"], "ocr_corrections": [ocr[4], ocr[5]]}),
    make_statement("st-chp8-p225-n4-lazzarini-death-of-dido", NOTES, 393, 393, "cand-1368", "cand-1372",
                   "painted_work_for_buonaccorsi_family",
                   "Footnote 4 reports that Lazzarini painted The Death of Dido for the Buonaccorsi family.",
                   "The work and commission are reported through da Canal, page 38; the source page was not independently read.",
                   ["cand-1368", "cand-1372", "cand-4163", "cand-7729", "cand-6593"], text_layer="footnote report", extras={"relation_candidate": True}),
    make_statement("st-chp8-p225-n4-lazzarini-battle-of-aeneas", NOTES, 393, 393, "cand-1368", "cand-1369",
                   "painted_work_for_buonaccorsi_family",
                   "Footnote 4 reports that Lazzarini painted The Battle of Aeneas and Mezentius for the Buonaccorsi family.",
                   "The work and commission are reported through da Canal, page 38; the source page was not independently read.",
                   ["cand-1368", "cand-1369", "cand-4164", "cand-7782", "cand-7729", "cand-6593"], text_layer="footnote report", extras={"relation_candidate": True}),
    make_statement("st-chp8-p225-n4-lazzarini-other-works", NOTES, 393, 393, "cand-1368", "cand-7777",
                   "painted_other_pictures_for_buonaccorsi_family",
                   "Footnote 4 adds that Lazzarini painted other pictures for the Buonaccorsi family.",
                   "No titles are supplied; the report is attributed to da Canal, page 38, which was not independently read.",
                   ["cand-1368", "cand-7777", "cand-7729", "cand-6593"], text_layer="footnote report", extras={"relation_candidate": True}),
    make_statement("st-chp8-p225-n5-balestra-aeneid-fable", NOTES, 394, 394, "cand-0168", "cand-7780",
                   "painted_aeneid_fable_for_buonaccorsi",
                   "Footnote 5 reports that Balestra's Aeneid fable for the Buonaccorsi is noted in Pascoli's unpublished life of the artist.",
                   "The work has no individual title here; the manuscript was not consulted and the source's OCR has been page-image corrected only in S2.",
                   ["cand-0168", "cand-7780", "cand-7729", "cand-7767", "cand-1842", "cand-3531", "cand-3532"], text_layer="footnote report",
                   extras={"relation_candidate": True, "shelfmark": "MS. 1383", "ocr_corrections": [ocr[6], ocr[7], ocr[8]]}),
    make_statement("st-chp8-p225-n6-zanotti-citation", NOTES, 395, 395, "cand-7114", "cand-7115",
                   "cites_source",
                   "Footnote 6 cites Zanotti, volume II, page 52.",
                   "The OCR volume numeral is corrected against the page image; the cited page was not independently read.",
                   ["cand-7114", "cand-7115"], text_layer="footnote citation", extras={"relation_candidate": False, "ocr_corrections": [ocr[9]]}),
    make_statement("st-chp8-p225-n7-leto-painting-location", NOTES, 396, 396, "cand-0880", "cand-7771",
                   "reported_present_location",
                   "Footnote 7 says the Leto painting was then in the Pinacoteca Nazionale, Bologna.",
                   "'Now' is relative to Haskell's publication; the location is not current-verified.",
                   ["cand-0880", "cand-7771", "cand-3398"], text_layer="footnote report", extras={"relation_candidate": True, "temporal_reference": "at time of Haskell's publication"}),
    make_statement("st-chp8-p225-n8-miller-citation", NOTES, 397, 397, "cand-7735", "cand-7768",
                   "cites_source",
                   "Footnote 8 cites D. Miller, 1958.",
                   "The title and page details are not supplied; identity with Dwight Miller remains for S3.",
                   ["cand-7735", "cand-7768"], text_layer="footnote citation", extras={"relation_candidate": False}),
    make_statement("st-chp8-p225-n9-ricci-citation", NOTES, 398, 398, "cand-7756", "cand-7755",
                   "cites_source",
                   "Footnote 9 cites Amico Ricci, volume II, page 436.",
                   "The cited page was not independently read.",
                   ["cand-7756", "cand-7755"], text_layer="footnote citation", extras={"relation_candidate": False}),
    make_statement("st-chp8-p225-n9-haskell-collection-visit", NOTES, 398, 398, "cand-0467", "cand-7765",
                   "author_reports_personal_visit_and_no_attribution_to_giaquinto",
                   "Haskell reports that when he visited the Buonaccorsi collection a few years earlier, none of its pictures could be attributed to Giaquinto.",
                   "This is the author's first-person report, not an independent re-examination of the collection or an attribution catalogue.",
                   ["cand-0467", "cand-7765", "cand-1165"], text_layer="footnote report"),
    make_statement("st-chp8-p225-n9-dorsi-limits-macerata-work", NOTES, 398, 398, "cand-7770", "cand-7783",
                   "limits_giaquinto_work_in_macerata_to_minor_niche_decoration",
                   "Haskell says d'Orsi, cited at pages 31-32, limits Giaquinto's work in Macerata to very minor decoration in window niches.",
                   "This is a second-hand report from an unidentified d'Orsi publication; the source pages were not read and no building is identified.",
                   ["cand-7769", "cand-7770", "cand-1165", "cand-1475", "cand-7783"], text_layer="footnote report", extras={"relation_candidate": True, "ocr_corrections": [ocr[10]]}),
]

if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("existing duplicate statement IDs")
statement_ids = {row["statement_id"] for row in statement_rows}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("new statement ID already exists")
prior_id = "st-chp8-p224-dido-enthusiasm-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.224 Dido-enthusiasm statement not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continued_to_segment_id": P225,
    "continued_to_source_line": 164,
    "continuation_closed_by_statement_id": "st-chp8-p225-dido-interest-closes",
})

new_coverage = []
for row in coverage_rows:
    sid = row["segment_id"]
    if sid == P224:
        row.update({"disposition": "reviewed", "migration_status": "complete",
                    "source_line_ranges": "L152-161", "note": "p.224 Dido-painting sentence closes at p.225 L164."})
    elif sid == P225:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L163-177", "note": "p.225 read against CHP-8.pdf physical page 27; final public/private gallery comparison continues at p.226 L180."})
    elif sid == NOTES:
        row.update({"source_line_ranges": "L373-398", "migration_status": "partial",
                    "note": "p.225 notes 1, 4-9 migrated from the composite notes segment; notes 2-3 are embedded at p.225 L176-177; later consolidated notes remain queued by printed page."})
    new_coverage.append(row)

ocr_by_line = {item["source_line"] for item in ocr}
preview = {
    "mode": "dry-run", "candidate_additions": len(new_candidates),
    "mention_additions": len(new_mentions), "statement_additions": len(new_statements),
    "statement_ids": [row["statement_id"] for row in new_statements],
    "continuations": [
        {"statement_id": prior_id, "status": "closed", "to": P225, "line": 164},
        {"statement_id": "st-chp8-p225-enlightenment-patron-inference-open", "status": "open", "to": P226, "line": 180},
    ],
    "coverage_updates": {
        P224: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L152-161"},
        P225: {"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L163-177"},
        NOTES: {"source_line_ranges": "L373-398", "migration_status": "partial"},
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

patched_statements = [patched_prior if row["statement_id"] == prior_id else row for row in statement_rows]
patched_statements.extend(new_statements)
write_csv_atomic(TABLES / "entity-candidates.csv", candidate_fields, candidate_rows)
write_csv_atomic(TABLES / "mentions.csv", mention_fields, mention_rows + new_mentions)
write_jsonl_atomic(TABLES / "book-statements.jsonl", patched_statements)
write_csv_atomic(TABLES / "s2-coverage.csv", coverage_fields, new_coverage)
preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
