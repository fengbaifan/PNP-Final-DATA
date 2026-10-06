"""Controlled S2 migration for Chapter 8 printed page 237 and its notes.

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
P236 = "chp-8:08_CHP-8_sec_ii:l303-309"
P237 = "chp-8:08_CHP-8_sec_ii:l311-325"
P238 = "chp-8:08_CHP-8_sec_ii:l327-336"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGETS = {P236, P237, P238, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p237-20261001"
PAGE_SCAN = PROCESS / "p237_page_review.png"
PDF = ROOT / "02-sources" / "01-book" / "CHP-8.pdf"


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
if len(segment_by_id) != len(segments) or not TARGETS <= set(segment_by_id):
    raise SystemExit("missing or duplicate target segment metadata")
for segment_id in TARGETS:
    meta = segment_by_id[segment_id]
    asset = ROOT / meta["source_file"]
    if hashlib.sha256(asset.read_bytes()).hexdigest() != meta["asset_sha256"]:
        raise SystemExit(f"source asset hash changed: {meta['source_file']}")
if not PAGE_SCAN.is_file() or not PDF.is_file():
    raise SystemExit("page 237 PDF or review image is missing")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
line_offsets = {}
for segment_id in TARGETS:
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
expected = {
    P236: ("reviewed", "partial", "L303-309"),
    P237: ("queued", "pending", ""),
    P238: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L373-438"),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")

new_candidates = [
    ("cand-8012", "Late Baroque conventions in the Crespi–Ricci comparison", "term", 317,
     "The art-historical category used in Haskell’s comparison; it is not a separate periodization claim."),
    ("cand-8013", "Venetian tradition invoked in the Crespi–Ricci comparison", "term", 317,
     "A stylistic tradition named by Haskell; identity with other broad Venetian-art candidates is left to S3."),
    ("cand-8014", "Crespi’s couple of still-life paintings commissioned by Ferdinand", "work", 320,
     "An unspecified pair of still lives reported by Haskell; titles and object identities are not supplied."),
    ("cand-8015", "Crespi letter to Ferdinand dated 26 February 1708", "archive", 439,
     "Specific letter locator cited by Haskell; the original document and Appendix 4 were not independently consulted."),
    ("cand-8016", "Letter of introduction concerning Crespi, Filza 5897 No. 183", "archive", 440,
     "Specific archival locator cited by Haskell; sender, recipient, and full contents are not given here."),
    ("cand-8017", "Ferdinand–Silva letter, Filza 5904 No. 96", "archive", 322,
     "One of four letters cited for the Crespi–Silva disputes; its contents were not independently consulted."),
    ("cand-8018", "Ferdinand–Silva letter, Filza 5904 No. 155", "archive", 322,
     "One of four letters cited for the Crespi–Silva disputes; its contents were not independently consulted."),
    ("cand-8019", "Ferdinand–Silva letter, Filza 5904 No. 299", "archive", 322,
     "One of four letters cited for the Crespi–Silva disputes; its contents were not independently consulted."),
    ("cand-8020", "Ferdinand–Silva letter, Filza 5904 No. 607", "archive", 322,
     "One of four letters cited for the Crespi–Silva disputes; its contents were not independently consulted."),
    ("cand-8021", "Ferdinand’s letter to Eleonora Zambeccari, Filza 5897 No. 287", "archive", 322,
     "Specific archival locator cited for the disputes; the original letter was not independently consulted."),
    ("cand-8022", "Mostra Celebrativa di Giuseppe M. Crespi (Bologna, 1948)", "archive", 440,
     "Exhibition catalogue cited by Haskell at p. 29; that page was not independently consulted."),
    ("cand-8023", "Lanfranco’s picture of the Ecstasy of St Margaret", "work", 441,
     "Earlier picture named as the work replaced by Crespi’s Ecstasy; no title beyond the subject is supplied."),
    ("cand-8024", "Cortona", "place", 441,
     "Geographic location of S. Maria Nuova and the Diocesan Museum as described in Haskell’s note."),
    ("cand-8025", "Diocesan Museum in Cortona", "institution", 441,
     "Institution named by Haskell as the later location of Crespi’s Ecstasy; current custody was not checked."),
    ("cand-8026", "S. Maria Nuova in Cortona", "place", 441,
     "Church/building named as the original location of Crespi’s Ecstasy."),
    ("cand-8027", "Crespi–Silva disputes and litigation over the Massacre presentation", "event", 322,
     "The dispute and litigation described by Haskell; the underlying letters were not independently consulted."),
    ("cand-8028", "Ferdinand correspondence, Filza 5904 No. 44", "archive", 324,
     "One of two April/May 1708 letters cited concerning Bolognese artists in touch with Ferdinand."),
    ("cand-8029", "Ferdinand correspondence, Filza 5904 No. 64", "archive", 324,
     "One of two April/May 1708 letters cited concerning Bolognese artists in touch with Ferdinand."),
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
    anchor_segment = NOTES if source_line >= 439 else P237
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


def mention(segment_id, line_no, suffix, candidate_id, surface, note, occurrence=0):
    mention_id = f"m-chp8-p237-{suffix}"
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
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span
                                     for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {span}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


MENTION_SPECS = [
    (P237, 312, "ricci-return-venice", "cand-2179", "Venice", "Destination of Ricci’s return mentioned on p.236; this line continues that sentence."),
    (P237, 312, "ricci-england", "cand-2179", "he", "Coreference to Sebastiano Ricci."),
    (P237, 312, "england", "cand-6809", "England", "Geographic destination in Haskell’s account."),
    (P237, 314, "grand-prince", "cand-1609", "The Grand Prince", "Ferdinand de’ Medici."),
    (P237, 314, "ricci-work", "cand-2179", "Ricci", "Sebastiano Ricci."),
    (P237, 315, "bologna", "cand-3398", "Bologna", "City where Crespi was back in February 1708."),
    (P237, 315, "florence-visit", "cand-3397", "Florence", "The Medici capital visited briefly by Crespi."),
    (P237, 315, "medici-capital", "cand-3397", "the Medici capital", "Coreferential description of Florence."),
    (P237, 316, "crespi-named", "cand-0871", "Giuseppe Maria Crespi", "Painter named in the body; index identity is reserved for S3."),
    (P237, 316, "ferdinand-letter-recipient", "cand-1609", "Ferdinand", "Recipient of Crespi’s reported letter."),
    (P237, 317, "venetian-painter", "cand-2179", "Venetian painter", "Sebastiano Ricci, identified by the contextual epithet."),
    (P237, 317, "crespi-innovation", "cand-0873", "Crespi", "Uses the index subentry for Crespi and Ferdinand in this direct comparison."),
    (P237, 317, "ricci-innovation", "cand-2179", "Ricci", "Sebastiano Ricci, compared with Crespi."),
    (P237, 317, "late-baroque", "cand-8012", "late Baroque conventions", "Art-historical category in Haskell’s comparison."),
    (P237, 317, "venetian-tradition", "cand-8013", "Venetian tradition", "Stylistic tradition attributed to Crespi’s innovations."),
    (P237, 317, "ferdinand-court", "cand-8010", "court", "Ferdinand de’ Medici’s court as the place where the two artists missed each other."),
    (P237, 318, "ferdinand-encouragement", "cand-1609", "Ferdinand", "Patron who encouraged Crespi."),
    (P237, 318, "florence-arrival", "cand-3397", "Florence", "Crespi’s reported arrival location."),
    (P237, 319, "massacre-painting", "cand-0882", "Massacre of the Innocents", "Crespi index subentry for the specific picture discussed here."),
    (P237, 319, "crespi-anxiety", "cand-0873", "Crespi", "The index subentry concerns Crespi’s work for Ferdinand."),
    (P237, 319, "ferdinand-work", "cand-1609", "Ferdinand", "Patron for whom Crespi wished to work."),
    (P237, 319, "grand-prince-court", "cand-8010", "court", "Court as an artistic context beyond Florence."),
    (P237, 320, "florence-outside", "cand-3397", "Florence", "Geographic reference delimiting artists outside the city."),
    (P237, 320, "crespi-brings-picture", "cand-0871", "he", "Coreference to Giuseppe Maria Crespi."),
    (P237, 320, "picture-to-ferdinand", "cand-0882", "the picture", "The Massacre of the Innocents discussed in the preceding sentence."),
    (P237, 320, "ferdinand-impressed", "cand-1609", "Ferdinand", "Patron receiving the picture."),
    (P237, 320, "grand-prince-commission", "cand-1609", "The Grand Prince", "Coreference to Ferdinand de’ Medici."),
    (P237, 320, "still-lives", "cand-8014", "a couple of still lives", "Unspecified pair of paintings commissioned from Crespi."),
    (P237, 320, "crespi-commission-recipient", "cand-0871", "Crespi", "Artist commissioned to make the still lives."),
    (P237, 320, "history-painting", "cand-0882", "the history painting", "Coreference to Crespi’s Massacre painting."),
    (P237, 321, "ferdinand-career", "cand-1609", "Ferdinand", "Patron discussed in Crespi’s career."),
    (P237, 321, "crespi-career", "cand-0871", "Crespi", "Giuseppe Maria Crespi in the career statement."),
    (P237, 321, "crespi-talents", "cand-0871", "Crespi", "Giuseppe Maria Crespi in the discussion of his talents.", 1),
    (P237, 321, "ferdinand-protector", "cand-1609", "protector", "Refers to Ferdinand in the patronage context."),
    (P237, 321, "crespi-output", "cand-0871", "his", "Coreference to Crespi’s artistic output."),
    (P237, 322, "ferdinand-litigation", "cand-1609", "Ferdinand", "Ferdinand’s reported involvement in the Crespi–Silva litigation."),
    (P237, 322, "crespi-litigation", "cand-0873", "Crespi", "Giuseppe Maria Crespi in the dispute with Silva."),
    (P237, 322, "silva-litigation", "cand-2433", "Silva", "Don Carlo Silva, by context and note 2."),
    (P237, 322, "letter-96", "cand-8017", "96", "First Ferdinand–Silva letter number, following ‘Nos.’ in the printed locator."),
    (P237, 322, "letter-155", "cand-8018", "155", "Second Ferdinand–Silva letter number."),
    (P237, 322, "letter-299", "cand-8019", "299", "Third Ferdinand–Silva letter number."),
    (P237, 322, "letter-607", "cand-8020", "607", "Fourth Ferdinand–Silva letter number."),
    (P237, 322, "eleonora-zambeccari", "cand-2831", "Eleonora Zambeccari", "Marchesa Eleonora Zambeccari."),
    (P237, 322, "zambeccari-letter", "cand-8021", "No. 287", "Ferdinand’s cited letter to Eleonora Zambeccari."),
    (P237, 323, "other-bolognese-ferdinand", "cand-1609", "Ferdinand", "Artists said to have been in touch with Ferdinand."),
    (P237, 323, "ercole-graziani", "cand-1229", "Ercole Graziani", "Index candidate; identity alignment is deferred."),
    (P237, 323, "giovan-gioseffo-santi", "cand-2356", "Giovan Gioseffo Santi", "Index candidate; identity alignment is deferred."),
    (P237, 323, "zanotti-volume-one", "cand-7115", "Zanotti, I", "Citation locator to volume I of Storia dell’Accademia Clementina."),
    (P237, 323, "giovan-gioseffo-dal-sole", "cand-2480", "Giovan Gioseffo dal Sole", "Index candidate; identity alignment is deferred."),
    (P237, 324, "letter-44", "cand-8028", "44", "One of two cited April/May 1708 letter numbers."),
    (P237, 324, "letter-64", "cand-8029", "64", "One of two cited April/May 1708 letter numbers."),
    (P237, 325, "he-back-bologna", "cand-0871", "He", "Coreference to Crespi."),
    (P237, 325, "bologna-return", "cand-3398", "Bologna", "Crespi’s reported return location."),
    (NOTES, 439, "letter-22", "cand-8015", "Letter of 26 February 1708", "Footnote 1 locator for Crespi’s letter to Ferdinand."),
    (NOTES, 439, "letter-22-number", "cand-8015", "No. 22", "Filza 5904 letter number."),
    (NOTES, 440, "letter-intro-183", "cand-8016", "No. 183", "Introduction-letter locator in Filza 5897."),
    (NOTES, 440, "zanotti-author", "cand-7114", "Zanotti", "Surname-only author attribution; identity remains subject to S3."),
    (NOTES, 440, "zanotti-volume-two", "cand-7115", "Zanotti, II", "Citation locator to volume II of Storia dell’Accademia Clementina."),
    (NOTES, 440, "massacre-note2", "cand-0882", "Massacre of the Innocents", "Same Crespi painting indexed under the specific work subentry."),
    (NOTES, 440, "ferdinand-presentation", "cand-1609", "Ferdinand", "Intended recipient of the painting."),
    (NOTES, 440, "mostra-catalogue", "cand-8022", "Mostra Celebration di Giuseppe M. Crespi", "OCR surface form for the 1948 exhibition catalogue; print reading is recorded on its statement."),
    (NOTES, 440, "crespi-in-catalogue", "cand-0871", "Giuseppe M. Crespi", "Person named within the catalogue title."),
    (NOTES, 440, "silva-commission", "cand-2433", "Don Carlo Silva", "Priest reported as the original commissioner."),
    (NOTES, 440, "crespi-arrival-livorno", "cand-0871", "Crespi", "Painter said to have travelled in person after the default."),
    (NOTES, 440, "livorno", "cand-6716", "Livorno", "Place of Crespi’s personal arrival as described in note 2."),
    (NOTES, 441, "crespi-employment", "cand-0871", "Crespi", "The conditional claim about possible earlier employment."),
    (NOTES, 441, "ferdinand-men-met", "cand-1609", "the two men", "Crespi and Ferdinand, named in the sentence context."),
    (NOTES, 441, "ecstasy-work", "cand-0877", "The Ecstasy of St Margaret", "Crespi work subentry in the book index."),
    (NOTES, 441, "santa-maria-nuova", "cand-8026", "S. Maria Nuova", "Original church location named in the note."),
    (NOTES, 441, "cortona-first", "cand-8024", "Cortona", "Location of S. Maria Nuova."),
    (NOTES, 441, "diocesan-museum", "cand-8025", "the Diocesan Museum", "Later location named by Haskell; the following ‘there’ refers to Cortona."),
    (NOTES, 441, "cortona-there", "cand-8024", "there", "Coreference to Cortona in the museum-location statement."),
    (NOTES, 441, "lanfranco", "cand-1359", "Lanfranco", "Giovanni Lanfranco as named in the index candidate."),
    (NOTES, 441, "lanfranco-picture", "cand-8023", "picture", "The painting by Giovanni Lanfranco; its title is not supplied."),
    (NOTES, 441, "ferdinand-bought-lanfranco", "cand-1609", "Ferdinand", "Buyer of Lanfranco’s picture according to Haskell."),
    (NOTES, 441, "crespi-earlier-work", "cand-0871", "Crespi", "Subject of the comparison with the later painting group.", 1),
    (NOTES, 441, "zanotti-44", "cand-7115", "Zanotti, II", "Citation locator to vol. II, p.44."),
    (NOTES, 441, "mostra-crespi-note3", "cand-8022", "Mostra di Giuseppe M. Crespi", "Shortened reference to the 1948 exhibition catalogue."),
    (NOTES, 442, "luigi-crespi-author", "cand-7716", "L. Crespi", "Bibliography-matched author; the cited source candidate is separately mentioned."),
    (NOTES, 442, "luigi-crespi-work", "cand-7578", "L. Crespi, p. 211", "Abbreviated page locator for the cited work; retain its existing source-candidate mapping."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", marker=None,
                   quoted_speaker=None, extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last, "printed_page": 237,
        "pdf_physical_page": 43, "claim": claim, "speaker": "Haskell",
        "text_layer": text_layer, "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    if marker is not None:
        qualifiers["footnote_marker"] = marker
    if quoted_speaker:
        qualifiers["quoted_speaker"] = quoted_speaker
    if extras:
        qualifiers.update(extras)
    return {"statement_id": statement_id, "segment_id": segment_id,
            "subject_candidate_id": subject, "object_candidate_id": obj,
            "predicate": predicate, "qualifiers": qualifiers,
            "original_quote": quote(segment_id, first, last), "origin": "book",
            "source_file": meta["source_file"]}


new_statements = [
    make_statement("st-chp8-p237-ricci-england-1716", P237, 312, 313,
        "cand-2179", "cand-6809", "travelled_to_england_and_remained_abroad_until_1716",
        "Haskell says Ricci returned to Venice and, a year later, went to England, where he remained abroad until 1716.",
        "This completes the sentence begun on p.236 L309. ‘His’ refers to Ricci; the account is Haskell’s narrative.",
        ["cand-2179", "cand-3401", "cand-6809"], text_layer="body continuation",
        extras={"continuation_from_segment_id": P236,
                "continued_from_statement_id": "st-chp8-p236-ricci-small-figure-pictures"}),
    make_statement("st-chp8-p237-crespi-struck-by-ricci", P237, 314, 317,
        "cand-0871", "cand-2179", "reported_as_struck_by_ricci_spirit",
        "After a brief Florence visit, Crespi was back in Bologna in February 1708 and wrote Ferdinand that Ricci’s spirit had also impressed him.",
        "Haskell reports the content of Crespi’s letter; the cited letter itself was not independently consulted.",
        ["cand-0871", "cand-3398", "cand-3397", "cand-1609", "cand-2179", "cand-8015"],
        marker=1, quoted_speaker="Giuseppe Maria Crespi", extras={"relation_candidate": True}),
    make_statement("st-chp8-p237-ricci-crespi-missed-meeting", P237, 317, 317,
        "cand-0871", "cand-2179", "missed_meeting_at_ferdinands_court_by_two_or_three_months",
        "Haskell says Crespi and Ricci missed meeting at Ferdinand’s court by two or three months, although both were pioneering a break with late Baroque conventions and were affected by the new mood there.",
        "The two artists are identified from the immediate paragraph context. ‘New mood’ and the historical characterization are Haskell’s interpretation.",
        ["cand-0871", "cand-0873", "cand-2179", "cand-8010", "cand-8012"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p237-crespi-style-compared-with-ricci", P237, 317, 317,
        "cand-0871", "cand-2179", "stylistic_innovations_compared_with_ricci",
        "Haskell compares Crespi’s innovations with Ricci’s: looser brushwork, a more painterly and spirited manner, greater individual temperament, and devotion to Venetian tradition.",
        "This is Haskell’s stylistic comparison, not an independently measured attribution or influence claim.",
        ["cand-0871", "cand-0873", "cand-2179", "cand-8012", "cand-8013"], extras={"relation_candidate": False,
        "ocr_corrections": [{"source_line":317,"ocr":"had'much","print":"had much","basis":"CHP-8.pdf physical page 43"}]}),
    make_statement("st-chp8-p237-ferdinand-encouraged-crespi", P237, 318, 319,
        "cand-1609", "cand-0871", "encouraged_crespi_to_present_massacre",
        "Haskell says Ferdinand encouraged Crespi when he arrived in Florence early in 1708 to present his Massacre of the Innocents, and treats Crespi’s wish to work for Ferdinand as evidence of the court’s importance to artists outside Florence.",
        "Body wording says Florence; note 2 separately describes Crespi’s decision to come to Livorno after Silva defaulted. The journey details are not silently collapsed.",
        ["cand-1609", "cand-0871", "cand-0873", "cand-3397", "cand-0882", "cand-8010"],
        marker=2, extras={"relation_candidate": True}),
    make_statement("st-chp8-p237-ferdinand-commissioned-still-lives", P237, 320, 320,
        "cand-1609", "cand-8014", "commissioned_still_lives_from_crespi",
        "After seeing Crespi’s Massacre, Ferdinand was impressed by his discrimination and enthusiasm and immediately commissioned a couple of still lives from him.",
        "The still lives are an unspecified pair. The comparison with the history painting is Haskell’s characterization.",
        ["cand-1609", "cand-0871", "cand-0882", "cand-8014"], marker=4, extras={"relation_candidate": True}),
    make_statement("st-chp8-p237-ferdinand-role-in-crespi-career", P237, 321, 321,
        "cand-1609", "cand-0871", "patronage_enabled-intimate_and_genre_work",
        "Haskell says Ferdinand was important to Crespi’s career, seems to have been among the first to appreciate the intimate side of his talent, and supported commissions on ‘pleasant subjects’ that enabled a break from religious and secular histories.",
        "‘Seems’ and the assessment of Ferdinand’s role remain qualified as Haskell’s interpretation.",
        ["cand-1609", "cand-0871"], marker=5, extras={"relation_candidate": True}),
    make_statement("st-chp8-p237-note1-letter-citation", NOTES, 439, 439,
        None, "cand-8015", "footnote_cites_crespi_letter_dated_26_february_1708",
        "Haskell cites a letter dated 26 February 1708 in Archivio Mediceo, Filza 5904, No.22, published in Appendix 4.",
        "This is a citation locator. The original letter and appendix were not independently consulted.",
        ["cand-8015", "cand-0871", "cand-1609"], text_layer="footnote citation", marker=1,
        extras={"linked_body_statement_ids": ["st-chp8-p237-crespi-struck-by-ricci"]}),
    make_statement("st-chp8-p237-note2-introduction-letter-citation", NOTES, 440, 440,
        None, "cand-8016", "footnote_cites_letter_of_introduction",
        "Haskell cites a letter of introduction for Crespi, Archivio Mediceo, Filza 5897, No.183, published in Appendix 4.",
        "The note does not identify sender or recipient; the original letter was not independently consulted.",
        ["cand-8016", "cand-0871"], text_layer="footnote citation", marker=2,
        extras={"linked_body_statement_ids": ["st-chp8-p237-ferdinand-encouraged-crespi"]}),
    make_statement("st-chp8-p237-note2-massacre-commission-and-default", NOTES, 440, 440,
        "cand-2433", "cand-0882", "commissioned_massacre_for_ferdinand_then_defaulted",
        "Haskell reports that Don Carlo Silva commissioned Crespi’s Massacre of the Innocents to present to Ferdinand, then defaulted on his obligations and said he no longer intended to give it to the Grand Prince.",
        "A report by Haskell citing Zanotti and a 1948 exhibition catalogue; those cited accounts were not independently consulted. The painting is the Crespi-specific index subentry, not another Massacre subject candidate.",
        ["cand-2433", "cand-0871", "cand-0882", "cand-1609", "cand-7115", "cand-8022"],
        text_layer="footnote report", marker=2, extras={"relation_candidate": True,
        "ocr_corrections": [{"source_line":440,"ocr":"Mostra Celebration","print":"Mostra Celebrativa","basis":"CHP-8.pdf physical page 43"}],
        "linked_body_statement_ids": ["st-chp8-p237-ferdinand-encouraged-crespi"]}),
    make_statement("st-chp8-p237-note2-crespi-arrival-livorno", NOTES, 440, 440,
        "cand-0871", "cand-6716", "travelled_in_person_to_livorno_after_silva_default",
        "Haskell says Crespi then decided to come in person to Livorno, where Zanotti colourfully describes his arrival and welcome.",
        "This wording is kept distinct from the body’s statement that Crespi arrived in Florence; no exact itinerary is inferred.",
        ["cand-0871", "cand-6716", "cand-7114", "cand-7115", "cand-2433"],
        text_layer="footnote report", marker=2, extras={"relation_candidate": True,
        "linked_body_statement_ids": ["st-chp8-p237-ferdinand-encouraged-crespi"]}),
    make_statement("st-chp8-p237-note2-ferdinand-litigation", P237, 322, 322,
        "cand-1609", "cand-8027", "intervened_in_crespi_silva_disputes_and_litigation",
        "Haskell says Ferdinand took part in the disputes and litigation from which Crespi emerged victorious.",
        "This line continues footnote 2 from p.237 L440. The cited letters are locators, not independently consulted evidence.",
        ["cand-1609", "cand-0871", "cand-0873", "cand-2433", "cand-8027", "cand-8017", "cand-8018", "cand-8019", "cand-8020", "cand-8021"],
        text_layer="footnote report", marker=2, extras={"relation_candidate": True,
        "linked_body_statement_ids": ["st-chp8-p237-ferdinand-encouraged-crespi"],
        "ocr_corrections": [{"source_line":322,"ocr":"letters-between","print":"letters between","basis":"CHP-8.pdf physical page 43"}]}),
    make_statement("st-chp8-p237-note2-silva-correspondence-citations", P237, 322, 322,
        None, "cand-8017", "footnote_cites_ferdinand_silva_letters_and_zambeccari_letter",
        "Haskell lists Ferdinand–Silva letters in Filza 3904 Nos.96, 155, 299 and 607 and a Ferdinand letter to Marchesa Eleonora Zambeccari in Filza 5897 No.287.",
        "The letter texts are cited for the litigation narrative but were not independently consulted.",
        ["cand-1609", "cand-2433", "cand-2831", "cand-8017", "cand-8018", "cand-8019", "cand-8020", "cand-8021"],
        text_layer="footnote citation", marker=2),
    make_statement("st-chp8-p237-note3-possible-earlier-employment", NOTES, 441, 441,
        "cand-0871", "cand-1609", "may_have_worked_for_ferdinand_before_they_met",
        "Haskell says Crespi may possibly have been employed some years before he and Ferdinand actually met.",
        "Both ‘may possibly’ and ‘some years’ are preserved; the employment is not stated as certain.",
        ["cand-0871", "cand-0873", "cand-1609"], text_layer="footnote report", marker=3,
        extras={"relation_candidate": True,
        "linked_body_statement_ids": ["st-chp8-p237-ferdinand-encouraged-crespi"]}),
    make_statement("st-chp8-p237-note3-ecstasy-replaces-lanfranco", NOTES, 441, 441,
        "cand-0877", "cand-8023", "painted_to_replace_lanfranco_picture",
        "Haskell says Crespi’s Ecstasy of St Margaret, then in S. Maria Nuova at Cortona and later in Cortona’s Diocesan Museum, replaced Lanfranco’s picture of the same subject, which Ferdinand bought for himself.",
        "The two pictures remain distinct. Current museum custody and the identity/title of Lanfranco’s picture were not independently checked.",
        ["cand-0877", "cand-8026", "cand-8024", "cand-8025", "cand-8023", "cand-1359", "cand-1609"],
        text_layer="footnote report", marker=3, extras={"relation_candidate": True}),
    make_statement("st-chp8-p237-note3-ecstasy-earlier-work", NOTES, 441, 441,
        "cand-0877", "cand-0871", "described_as_much_earlier_than_current_painting_group",
        "Haskell says the Ecstasy seems much earlier than the group of Crespi paintings discussed in the surrounding chapter, and cites Zanotti, volume II, p.44 and the 1948 exhibition catalogue, p.29.",
        "The date comparison is expressly Haskell’s qualified assessment; the cited pages were not independently consulted.",
        ["cand-0877", "cand-0871", "cand-7115", "cand-8022"], text_layer="footnote report", marker=3),
    make_statement("st-chp8-p237-note3-other-bolognese-artists", P237, 323, 324,
        "cand-1609", "cand-1229", "other_bolognese_artists_in_touch_with_ferdinand",
        "Haskell names Ercole Graziani, Giovan Gioseffo Santi and Giovan Gioseffo dal Sole as other Bolognese artists in touch with Ferdinand, citing Zanotti volume I and two April/May 1708 letters.",
        "This paragraph follows note 3 on the printed page without a repeated marker; its placement and topic support treating it as the continuation of note 3. Identity matching remains for S3.",
        ["cand-1609", "cand-1229", "cand-2356", "cand-2480", "cand-7115", "cand-8028", "cand-8029"],
        text_layer="footnote 3 continuation", marker=3, extras={"relation_candidate": True,
        "linked_body_statement_ids": ["st-chp8-p237-ferdinand-encouraged-crespi"],
        "ocr_corrections": [{"source_line":323,"ocr":"sec letters","print":"see letters","basis":"CHP-8.pdf physical page 43"}]}),
    make_statement("st-chp8-p237-note4-luigi-crespi-citation", NOTES, 442, 442,
        None, "cand-7578", "footnote_cites_l_crespi_page_211",
        "Haskell’s note 4 cites L. Crespi, p.211.",
        "The abbreviated source remains linked to the existing citation candidate; it is not equated with painter Giuseppe Maria Crespi.",
        ["cand-7578", "cand-7716"], text_layer="footnote citation", marker=4,
        extras={"linked_body_statement_ids": ["st-chp8-p237-ferdinand-commissioned-still-lives"]}),
    make_statement("st-chp8-p237-note5-return-to-bologna", P237, 325, 325,
        "cand-0871", "cand-3398", "back_in_bologna_by_26_february_1708",
        "Haskell says Crespi was back in Bologna by 26 February 1708 and directs the reader to note 1.",
        "The date is the latest stated by Haskell and points to the dated letter; it does not independently establish the exact return day.",
        ["cand-0871", "cand-3398", "cand-8015"], text_layer="footnote 5 report", marker=5,
        extras={"cross_reference_statement_ids": ["st-chp8-p237-note1-letter-citation"],
        "ocr_corrections": [{"source_line":325,"ocr":"26,1708","print":"26, 1708","basis":"CHP-8.pdf physical page 43"}]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")

for row in coverage_rows:
    if row["segment_id"] == P236:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L303-309",
                    "note": "p.236 body and notes 1-3 were reviewed against physical page 42; the final sentence closes at p.237 L312-313. OCR corrections remain in S2 qualifiers; source OCR is unchanged."})
    elif row["segment_id"] == P237:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L312-325",
                    "note": "p.237 body and page notes 1-5 reviewed against physical page 43. The last body clause ends ‘but he’ and continues at p.238 L328; footnote 2 continues at L322 and note 3 includes the following unnumbered paragraph at L323-324."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-442",
                    "note": "Consolidated notes reviewed in source order through p.237 notes 1-5 at L439-442; notes 1-3 and their body links are recorded. Remaining notes L443-461 are queued for later pages."})

preview = {
    "mode": "dry-run", "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage_updates": {P236: "complete", P237: "partial through L312-325", NOTES: "partial through L373-442"},
    "print_corrections": [
        "L317 had'much -> had much", "L322 letters-between -> letters between",
        "L323 sec letters -> see letters", "L325 26,1708 -> 26, 1708",
        "L440 Mostra Celebration -> Mostra Celebrativa",
    ],
    "preserved_uncertainties": [
        "Body says Crespi arrived in Florence; note 2 says he decided to come to Livorno after Silva defaulted; no itinerary inferred",
        "Ferdinand encouraged presentation of Crespi’s Massacre, while Don Carlo Silva is reported as the commissioner",
        "Note 3’s may-possibly claim remains conditional; Lanfranco picture remains unidentified",
        "L323-324 is treated as note 3 continuation because of page layout and topic, without inventing another marker",
        "p.237 L321 remains open to p.238 L328",
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
