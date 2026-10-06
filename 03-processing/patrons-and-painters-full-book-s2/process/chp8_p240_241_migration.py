"""Controlled S2 migration for Chapter 8 printed pages 240-241 and notes.

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
P239 = "chp-8:08_CHP-8_sec_ii:l338-348"
P240 = "chp-8:08_CHP-8_sec_ii:l350-359"
P241 = "chp-8:08_CHP-8_sec_ii:l361-370"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGETS = {P239, P240, P241, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p240-241-20261001"
PAGE240_SCAN = PROCESS / "p240_page_review.png"
PAGE241_SCAN = PROCESS / "p241_page_review.png"
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
if not all(path.is_file() for path in (PDF, PAGE240_SCAN, PAGE241_SCAN)):
    raise SystemExit("page 240/241 PDF or review image is missing")

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
    P239: ("reviewed", "partial", "L339-348"),
    P240: ("queued", "pending", ""),
    P241: ("queued", "pending", ""),
    NOTES: ("reviewed", "partial", "L373-451"),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")

new_candidates = [
    ("cand-8059", "Livio Mehus's unnamed son receiving support from Ferdinand", "person", P240, 351,
     "The son is unnamed in this passage; no identity or career is supplied."),
    ("cand-8060", "Thirty works by Livio Mehus owned by Ferdinand", "work", P240, 351,
     "An aggregate of thirty works reported in Haskell's description; no titles or individual objects are identified."),
    ("cand-8061", "Unspecified Flemish works in Ferdinand's collection", "work", P240, 351,
     "Haskell notes Flemish works without identifying their makers, titles, or number."),
    ("cand-8062", "Ferdinand's special room at Poggio a Caiano for small examples by favourite artists", "place", P240, 352,
     "Haskell describes a room holding small examples of ancient and contemporary favourite artists; its identity with the distinct room candidate cand-7963 is unresolved."),
    ("cand-8063", "Unidentified 1707 work by Sebastiano Ricci associated with Ferdinand's special room", "work", P240, 353,
     "Haskell says Ricci painted 'this' for Ferdinand in 1707; the exact object and the referent of 'this' are not further specified."),
    ("cand-8064", "Villa di Castello", "place", P240, 354,
     "Residence named as a site of Ferdinand's large collections; its relation to other Medici sites is not inferred."),
    ("cand-8065", "Piazza del Duomo in Florence", "place", P240, 356,
     "Public display location named by Haskell; no more specific modern site identification is supplied."),
    ("cand-8066", "Saint Luke referred to in the 18 October feast day and chapel dedication", "person", P240, 359,
     "Local S2 candidate for the saint named in this passage; possible identity with chp.1 candidate cand-3564 is deferred to S3."),
    ("cand-8067", "Chapel dedicated to Saint Luke in the Annunziata cloister", "place", P240, 359,
     "The chapel is identified by dedication and location only; no separate building history is added."),
    ("cand-8068", "Cloister of the Monastery of the SS Annunziata in Florence", "place", P240, 359,
     "Haskell locates the exhibition in the Annunziata cloisters; the catalogue title supplies the monastery wording."),
    ("cand-8069", "Nota de' Quadri che sono esposti per la festa di S. Luca ... Firenze 1706", "archive", NOTES, 456,
     "Printed catalogue title transcribed as given in the OCR, with title spelling and capitalization preserved; the catalogue was not independently consulted."),
    ("cand-8070", "Twelve pictures lent by Ferdinand for the first lunette of the 1706 exhibition", "work", NOTES, 452,
     "The twelve works are not individually identified. The printed page places this text in the body, although the OCR stores it in the consolidated notes segment."),
    ("cand-8071", "Unidentified portrait of Grand Prince Ferdinand displayed above the chapel door in 1706", "work", NOTES, 452,
     "Portrait is identified only by sitter and display position; maker, title, and ownership are unstated."),
    ("cand-8072", "About 250 pictures shown at the 1706 Annunziata exhibition", "work", NOTES, 452,
     "Aggregate exhibition display as reported by Haskell; the source says nearly all were borrowed from Florence collections and none from the Grand Duke's."),
    ("cand-8073", "Unidentified Grand Duke whose collection supplied no pictures to the 1706 exhibition", "person", NOTES, 452,
     "The title is not named here and is kept distinct from Grand Prince Ferdinand; identity is unresolved."),
    ("cand-8074", "Unidentified Cardinal Medici who lent Venetian paintings to the 1706 exhibition", "person", P241, 364,
     "Haskell gives only the title and family name; not identified with Cardinal Leopoldo or another Medici."),
    ("cand-8075", "Further Venetian paintings lent by Cardinal Medici to the 1706 exhibition", "work", P241, 364,
     "The paintings are unspecified; the lender is not identified beyond the title Cardinal Medici."),
    ("cand-8076", "Twenty-odd pictures lent by Ferdinand to the 1706 exhibition", "work", P241, 362,
     "Haskell gives an approximate total and names some works; the group is not reduced to the twelve in the first lunette."),
    ("cand-8077", "Four landscapes by Marco Ricci probably lent to the 1706 exhibition", "work", P241, 363,
     "Haskell says almost certainly; note 2 says the lender is unnamed and only probably links two landscapes received by Ferdinand to this group."),
    ("cand-8078", "Del Rosso brothers as a collective lending group at the 1706 exhibition", "family", P241, 366,
     "The passage names the brothers collectively but does not identify which member lent which work; do not expand this to individual endpoints."),
    ("cand-8079", "Later Florentine exhibitions on similar lines in 1715, 1724, 1729, 1737, and 1767", "event", P241, 367,
     "Haskell lists later exhibitions at irregular intervals; the individual events are not otherwise identified here."),
    ("cand-8080", "Florentine exhibition of 1767 cited by Haskell", "event", NOTES, 459,
     "The event is referenced in note 3 as a later exhibition; details beyond its catalogue title are not added."),
    ("cand-8081", "Il trionfo delle Bell'Arti ... Maria Luisa di Borbone (introduction to the 1767 exhibition)", "archive", NOTES, 459,
     "The source is cited by Haskell as the introduction to the 1767 exhibition; its full text was not independently consulted."),
    ("cand-8082", "Unidentified Giorgione painting lent by Ferdinand to the 1706 exhibition", "work", P241, 362,
     "Haskell names the painter but not the painting's title, subject, or present location."),
    ("cand-8083", "Unidentified Titian painting lent by Ferdinand to the 1706 exhibition", "work", P241, 362,
     "A single painting is included in Haskell's list of seven Venetian old masters; it is not identified with a work from the earlier group of about ten attributed Titians."),
    ("cand-8084", "Unidentified Paolo Veronese painting lent by Ferdinand to the 1706 exhibition", "work", P241, 362,
     "Haskell names the painter but not the painting's title, subject, or present location."),
    ("cand-8085", "Unidentified Tintoretto painting lent by Ferdinand to the 1706 exhibition", "work", P241, 362,
     "Haskell names the painter but not the painting's title, subject, or present location."),
    ("cand-8086", "Unidentified Giovanni Antonio da Pordenone painting lent by Ferdinand to the 1706 exhibition", "work", P241, 362,
     "Haskell names the painter but not the painting's title, subject, or present location."),
    ("cand-8087", "Unidentified Andrea Schiavone painting lent by Ferdinand to the 1706 exhibition", "work", P241, 362,
     "Haskell names the painter but not the painting's title, subject, or present location."),
    ("cand-8088", "Unidentified Paris Bordone painting lent by Ferdinand to the 1706 exhibition", "work", P241, 362,
     "Haskell names the painter but not the painting's title, subject, or present location."),
    ("cand-8089", "Unidentified early Guercino painting included in the 1706 exhibition", "work", P241, 362,
     "Haskell describes it as an early Guercino but supplies no title, date, subject, or lender."),
    ("cand-8090", "Unidentified Lodovico Carracci painting included in the 1706 exhibition", "work", P241, 362,
     "Haskell names the painter but not the painting's title, subject, or lender."),
    ("cand-8091", "Unidentified Schedoni painting included in the 1706 exhibition", "work", P241, 362,
     "Haskell names the painter but not the painting's title, subject, or lender."),
    ("cand-8092", "Unspecified Neapolitan works shown in the 1706 exhibition", "work", P241, 366,
     "Haskell describes a strong Neapolitan contingent, mainly lent by the del Rosso brothers, without identifying the works."),
    ("cand-8093", "About ten paintings attributed to Titian in Ferdinand's collection", "work", P240, 351,
     "Haskell gives an approximate count and qualified attribution; no titles or locations are supplied."),
    ("cand-8094", "Venetian school of painting in Haskell's account of Italian art", "term", P241, 369,
     "Art-historical category used by Haskell; its boundaries are not independently defined here."),
    ("cand-8095", "Contemporary Roman painting in Haskell's account of Ferdinand's collection", "term", P240, 351,
     "Art-historical category used to describe the small representation in the collection; no individual painter or work is specified."),
    ("cand-8096", "F. Haskell's article on Andrea Gerini in Boll. dei Musei Civici Veneziani (1960)", "archive", NOTES, 461,
     "Cited by Haskell as further reading on Gerini; article title and page range are not given in this note."),
    ("cand-8097", "Pietro Leopoldo, Archduke of Austria, named in the 1767 exhibition catalogue title", "person", NOTES, 459,
     "Name and title appear in the cited catalogue title; identity is not independently aligned here."),
    ("cand-8098", "Maria Luisa di Borbone named in the 1767 exhibition catalogue title", "person", NOTES, 459,
     "Name appears in the cited catalogue title; identity is not independently aligned here."),
    ("cand-8099", "Fogolari (1937), Letter 116, 1705-10-17", "archive", NOTES, 457,
     "Archival letter identified through Haskell's footnote; original letter was not independently consulted."),
    ("cand-8100", "Contemporary art promoted by Ferdinand in Haskell's account", "term", P241, 369,
     "Broad category in Haskell's argument; not equated with a named school or organized movement."),
    ("cand-8101", "Contemporary Venetian art discussed in Haskell's account of Ferdinand's patronage", "term", NOTES, 461,
     "Art-historical category in Haskell's note; not equated with the entire Venetian school."),
    ("cand-8102", "Florentine school of painting in Haskell's account of Ferdinand's collection", "term", P240, 351,
     "Art-historical category used by Haskell; it is not treated as a formal institution."),
    ("cand-8103", "Unspecified Florentine artists represented in Ferdinand's collection", "term", P241, 364,
     "Collective reference to old and new Florentine artists; none is individually named in the statement."),
    ("cand-8104", "Venetian artists (collective category in Haskell's account)", "term", P241, 365,
     "Collective geographic/artistic category used both for exhibition participants and artists in correspondence; it does not assert that the same individuals are involved."),
]

candidate_ids = {row["candidate_id"] for row in candidate_rows}
if len(candidate_ids) != len(candidate_rows) or max(int(cid.split("-")[1]) for cid in candidate_ids) != 8058:
    raise SystemExit("candidate inventory changed since p.239; inspect before allocating IDs")
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidate_rows}
new_keys = set()
for candidate_id, name, kind, anchor_segment, source_line, detail in new_candidates:
    if candidate_id in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if (name, kind) in existing_keys or (name, kind) in new_keys:
        raise SystemExit(f"candidate natural-key collision: {(name, kind)}")
    new_keys.add((name, kind))
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
    mention_id = f"m-chp8-p240-241-{suffix}"
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
    (P240, 351, "titian-context", "cand-2630", "Titian", "Painter in the approximate collection count."),
    (P240, 351, "ten-titian-group", "cand-8093", "about ten attributed to Titian", "Approximate number and attribution qualifier are retained."),
    (P240, 351, "flemish-works", "cand-8061", "Flemish works", "Unidentified works in the collection."),
    (P240, 351, "roman-painting", "cand-8095", "contemporary Roman painting", "Art-historical category, not a named school institution."),
    (P240, 351, "florentine-school", "cand-8102", "Florentine school", "Art-historical category; not a formal organization."),
    (P240, 351, "mehus-first", "cand-1632", "Livio Mehus", "Painter identified in the index."),
    (P240, 351, "mehus-thirty-works", "cand-8060", "thirty of whose works", "Works owned by Ferdinand; titles not supplied."),
    (P240, 351, "ferdinand-owns-mehus-works", "cand-1609", "Ferdinand", "Grand Prince Ferdinand de' Medici.", 0),
    (P240, 351, "mehus-second", "cand-1632", "Mehus", "Coreference to Livio Mehus.", 1),
    (P240, 351, "ferdinand-entourage", "cand-1609", "his entourage", "Coreference to Ferdinand."),
    (P240, 351, "mehus-vivacity", "cand-1632", "his tremendous vivacity", "Coreference to Mehus; Haskell's characterization."),
    (P240, 351, "ferdinand-appeal", "cand-1609", "Ferdinand", "Patron to whom Mehus's qualities appealed.", 1),
    (P240, 351, "mehus-this-painter", "cand-1632", "this painter", "Coreference to Mehus."),
    (P240, 351, "ferdinand-patronage", "cand-1609", "Ferdinand’s patronage", "Grand Prince Ferdinand de' Medici."),
    (P240, 351, "mehus-him-direct", "cand-1632", "him", "Coreference to Livio Mehus."),
    (P240, 351, "grand-prince-ferdinand", "cand-1609", "the Grand Prince", "Coreference to Ferdinand."),
    (P240, 351, "ferdinand-neglect", "cand-1609", "this neglect", "Haskell frames collecting and support as amends by Ferdinand."),
    (P240, 351, "mehus-canvases", "cand-8060", "his canvases", "Mehus's unspecified works."),
    (P240, 351, "mehus-son", "cand-8059", "his son", "Unnamed son of Livio Mehus."),
    (P240, 352, "poggio", "cand-1966", "Poggio a Caiano", "Named residence."),
    (P240, 352, "ferdinand-room", "cand-1609", "Ferdinand", "Grand Prince Ferdinand de' Medici."),
    (P240, 352, "special-room", "cand-8062", "a special room", "Room at Poggio a Caiano; relation to other room descriptions is unresolved."),
    (P240, 352, "ricci-first-name", "cand-2179", "Sebastiano", "First part of a name broken across OCR lines; index entry concerns work for Ferdinand."),
    (P240, 353, "ricci-surname", "cand-2179", "Ricci", "Continuation of the name Sebastiano Ricci on the following OCR line."),
    (P240, 353, "ricci-room-work", "cand-8063", "painted for him in 1707", "Haskell's referent 'this' and the exact painted object remain unclear."),
    (P240, 353, "ferdinand-for-whom-ricci-painted", "cand-1609", "him", "Coreference to Ferdinand."),
    (P240, 353, "ferdinand-collections", "cand-1609", "He kept", "Coreference to Ferdinand as collector."),
    (P240, 353, "pratolino", "cand-7838", "Pratolino", "Named residence."),
    (P240, 354, "villa-di-castello", "cand-8064", "Villa di Castello", "Named residence."),
    (P240, 355, "ferdinand-patron-activities", "cand-1609", "Ferdinand’s activities as patron", "Grand Prince Ferdinand de' Medici."),
    (P240, 355, "ferdinand-own-collection", "cand-1609", "his own collection", "Coreference to Ferdinand."),
    (P240, 355, "ferdinand-favoured-artists", "cand-1609", "his fancy", "Coreference to Ferdinand's preferences."),
    (P240, 355, "ferdinand-guide-painters", "cand-1609", "He was also anxious", "Coreference to Ferdinand."),
    (P240, 355, "florence-direction", "cand-1041", "the Florence of his day", "City and local painting context."),
    (P240, 355, "art-exhibition-instrument", "cand-0128", "the art exhibition", "General practice indexed under art exhibitions."),
    (P240, 355, "exhibition-instrument-used", "cand-0128", "it in an entirely new way", "Coreference to the exhibition as an instrument."),
    (P240, 355, "exhibitions-florence", "cand-1041", "Florence", "City where Corpus Domini picture displays occurred."),
    (P240, 355, "italian-cities", "cand-3461", "Italian cities", "Italy as the geographic scope; cities are unnamed."),
    (P240, 355, "corpus-domini-processions", "cand-6024", "Corpus Domini processions", "Recurring feast/processions, not a dated single event."),
    (P240, 355, "ferdinand-shows-works", "cand-1609", "Ferdinand", "Patron and exhibitor in Haskell's account.", 0),
    (P240, 355, "ferdinand-works-painted-for-him", "cand-1609", "him", "Coreference to Ferdinand."),
    (P240, 355, "ferdinand-approves", "cand-1609", "he approved", "Coreference to Ferdinand's artistic preferences."),
    (P240, 356, "gabbiani", "cand-1093", "Gabbiani", "Anton Domenico Gabbiani."),
    (P240, 356, "flight-into-egypt", "cand-1095", "Flight into Egypt", "Index subentry for Gabbiani's work."),
    (P240, 356, "ferdinand-display", "cand-1609", "he put on view", "Coreference to Ferdinand."),
    (P240, 356, "piazza-del-duomo", "cand-8065", "Piazza del Duomo", "Public display location in Florence."),
    (P240, 357, "ferdinand-sacconi-policy", "cand-1609", "He adopted the same policy", "Coreference to Ferdinand and his exhibition policy."),
    (P240, 357, "sacconi", "cand-2325", "Sacconi", "Marco Sacconi."),
    (P240, 357, "cassana", "cand-0593", "Cassana", "Niccolò Cassana."),
    (P240, 357, "cassana-letter-recipient", "cand-0593", "whom", "Relative pronoun referring to Cassana."),
    (P240, 357, "ferdinand-wrote", "cand-1609", "he wrote", "Coreference to Ferdinand."),
    (P240, 357, "portrait-cook", "cand-7940", "his Portrait of a Cook", "Named painting by Niccolò Cassana; object candidate reused."),
    (P240, 357, "ferdinand-intends-exhibit", "cand-1609", "he intended to exhibit", "Coreference to Ferdinand."),
    (P240, 357, "ferdinand-exhibitions-casual", "cand-1609", "Ferdinand probably found", "Haskell's qualified interpretation."),
    (P240, 357, "art-exhibitions-casual", "cand-0128", "such exhibitions", "General exhibition practice."),
    (P240, 357, "ferdinand-organizes-1706", "cand-1609", "he had already organised", "Coreference to Ferdinand."),
    (P240, 357, "st-rocco-exhibitions", "cand-0138", "S. Rocco exhibitions", "Index candidate; exact individual exhibitions and dates are not supplied."),
    (P240, 357, "venice-s-rocco", "cand-2719", "Venice", "City location for the S. Rocco exhibitions."),
    (P240, 357, "ferdinand-ran-own-exhibition", "cand-1609", "he ran his own one", "Coreference to Ferdinand; event candidate is the October 1706 exhibition."),
    (P240, 358, "catalogue-issued", "cand-8069", "A printed catalogue", "Catalogue of the 1706 exhibition."),
    (P240, 358, "italy-catalogue-innovation", "cand-3461", "Italy", "Geographic scope of Haskell's innovation claim."),
    (P240, 358, "this-catalogue", "cand-8069", "this catalogue", "The printed exhibition catalogue."),
    (P240, 358, "event-reconstruction", "cand-7977", "the event", "October 1706 exhibition candidate."),
    (P240, 358, "exhibition-annunziata", "cand-7977", "The exhibition", "October 1706 exhibition."),
    (P240, 358, "st-lukes-day", "cand-8066", "St Luke’s day", "Saint Luke's feast day, identified as 18 October."),
    (P240, 359, "that-saint", "cand-8066", "that saint", "Coreference to Saint Luke."),
    (P240, 359, "chapel", "cand-8067", "the chapel", "Chapel dedicated to Saint Luke."),
    (P240, 359, "cloisters", "cand-8068", "the cloisters", "Annunziata cloister."),
    (P240, 359, "annunziata", "cand-8068", "the Annunziata", "Monastery/cloister named as the venue."),
    (NOTES, 452, "two-fifty-pictures", "cand-8072", "250 pictures", "Body continuation on printed p.240, stored in the consolidated OCR segment."),
    (NOTES, 452, "florence-collections", "cand-1041", "collections of Florence", "Florentine lending collections; individual repositories are unnamed."),
    (NOTES, 452, "grand-duke", "cand-8073", "the Grand Duke’s", "Unidentified Grand Duke distinct from Ferdinand."),
    (NOTES, 452, "pictures-arranged", "cand-8072", "The pictures", "Coreference to the approximately 250 pictures in the exhibition."),
    (NOTES, 452, "cloister-lunettes", "cand-8068", "the lunettes of the cloister", "Display arrangement within the Annunziata cloister."),
    (NOTES, 452, "twelve-pictures-first-lunette", "cand-8070", "twelve pictures lent by Ferdinand himself", "Unidentified group lent by Ferdinand."),
    (NOTES, 452, "ferdinand-twelve-loan", "cand-1609", "Ferdinand himself", "Grand Prince Ferdinand de' Medici."),
    (NOTES, 452, "portrait-grand-prince", "cand-8071", "a portrait of the Grand Prince", "Unidentified portrait displayed above the chapel door."),
    (NOTES, 452, "ferdinand-portrait-sitter", "cand-1609", "the Grand Prince", "Sitter is Ferdinand de' Medici."),
    (P241, 362, "portrait-shows-patronage", "cand-1609", "who thus unmistakably showed his patronage", "The 'who' resumes the Grand Prince in the portrait display description; Haskell's inference."),
    (P241, 362, "venture", "cand-7977", "the whole venture", "October 1706 exhibition."),
    (P241, 362, "ferdinand-taste", "cand-1609", "his taste", "Coreference to Ferdinand."),
    (P241, 362, "ferdinand-art-direction", "cand-1609", "he wished to give", "Coreference to Ferdinand."),
    (P241, 362, "twenty-odd-pictures", "cand-8076", "twenty-odd pictures", "Approximate group lent by Ferdinand."),
    (P241, 362, "ferdinand-twenty-odd", "cand-1609", "he lent", "Coreference to Ferdinand."),
    (P241, 362, "giorgione-work", "cand-8082", "a Giorgione", "Unidentified painting; painter is separately annotated within the span."),
    (P241, 362, "giorgione-painter", "cand-1188", "Giorgione", "Painter named within the unidentified-work phrase."),
    (P241, 362, "titian-work", "cand-8083", "a Titian", "Unidentified painting; distinct from the collection's group of attributed Titians."),
    (P241, 362, "titian-painter", "cand-2630", "Titian", "Painter named within the unidentified-work phrase."),
    (P241, 362, "veronese-work", "cand-8084", "a Veronese", "Unidentified painting."),
    (P241, 362, "veronese-painter", "cand-2755", "Veronese", "Paolo Veronese."),
    (P241, 362, "tintoretto-work", "cand-8085", "a Tintoretto", "Unidentified painting."),
    (P241, 362, "tintoretto-painter", "cand-2627", "Tintoretto", "Painter named within the unidentified-work phrase."),
    (P241, 362, "pordenone-work", "cand-8086", "a Pordenone", "Unidentified painting."),
    (P241, 362, "pordenone-painter", "cand-1975", "Pordenone", "Giovanni Antonio da Pordenone."),
    (P241, 362, "schiavone-work", "cand-8087", "a Schiavone", "Unidentified painting."),
    (P241, 362, "schiavone-painter", "cand-2395", "Schiavone", "Andrea Schiavone."),
    (P241, 362, "bordone-work", "cand-8088", "a Paris Bordone", "Unidentified painting."),
    (P241, 362, "bordone-painter", "cand-0391", "Paris Bordone", "Painter named within the unidentified-work phrase."),
    (P241, 362, "guercino-work", "cand-8089", "an early Guercino", "Unidentified early work; not dated more precisely."),
    (P241, 362, "guercino-painter", "cand-1258", "Guercino", "Francesco Barbieri."),
    (P241, 362, "carracci-work", "cand-8090", "a Lodovico Carracci", "Unidentified painting."),
    (P241, 362, "carracci-painter", "cand-0580", "Lodovico Carracci", "Painter named within the unidentified-work phrase."),
    (P241, 363, "schedoni-painter", "cand-2394", "Schedoni", "Bartolommeo Schedoni; the work mention is in the previous line's phrase fragment."),
    (P241, 363, "ferdinand-cagnacci-loan", "cand-1609", "his", "Coreference to Ferdinand as lender of the Cagnacci Magdalene.", 0),
    (P241, 363, "cagnacci-magdalene", "cand-0479", "his Guido Cagnacci Magdalene", "Indexed Magdalene painting; Haskell quotes its colour description."),
    (P241, 363, "cagnacci-painter", "cand-0478", "Guido Cagnacci", "Painter named within the work phrase."),
    (P241, 363, "magdalene-colour", "cand-0479", "Magdalene", "Work title/subentry; exact title form in the source."),
    (P241, 363, "cagnacci-quote", "cand-0479", "di colore freschissimo", "Haskell's quoted Italian descriptor; original speaker is not identified here."),
    (P241, 363, "cassana-hunter", "cand-0599", "his Cassana Portrait of a Hunter", "Indexed painting lent by Ferdinand; identity is not enriched from this passage."),
    (P241, 363, "cassana-hunter-painter", "cand-0593", "Cassana", "Niccolò Cassana."),
    (P241, 363, "hunter-title", "cand-0599", "Portrait of a Hunter", "Indexed painting title."),
    (P241, 363, "four-marco-landscapes", "cand-8077", "four landscapes by Marco Ricci", "Haskell's attribution is explicitly almost certain; lender is qualified in note 2."),
    (P241, 363, "marco-ricci", "cand-2149", "Marco Ricci", "Painter named within the group-of-works phrase."),
    (P241, 364, "florentine-artists", "cand-8103", "Florentine artists", "Collective reference; individual artists are unnamed."),
    (P241, 364, "ferdinand-collection-no-florentine", "cand-1609", "his collection", "Coreference to Ferdinand."),
    (P241, 364, "grand-prince-no-florentine", "cand-1609", "the Grand Prince", "Ferdinand de' Medici."),
    (P241, 364, "cardinal-venetian-paintings", "cand-8075", "further Venetian paintings", "Additional unnamed works lent by Cardinal Medici."),
    (P241, 364, "cardinal-medici", "cand-8074", "Cardinal Medici", "Identity not inferred from title alone."),
    (P241, 365, "venetian-contingent", "cand-8104", "Venetians", "Collective reference to Venetian artists/works in the exhibition."),
    (P241, 366, "neapolitan-contingent", "cand-8092", "Neapolitan contingent", "Unspecified works in the exhibition."),
    (P241, 366, "del-rosso-brothers", "cand-8078", "the del Rosso brothers", "Collective lender group; no individual member assigned."),
    (P241, 366, "luca-giordano", "cand-1172", "Luca Giordano", "Neapolitan painter represented prominently; no specific work is named."),
    (P241, 367, "ferdinand-attended", "cand-1609", "The Grand Prince himself", "Ferdinand personally attended the exhibition."),
    (P241, 367, "exhibition-remained-open", "cand-7977", "the exhibition", "October 1706 exhibition."),
    (P241, 367, "ferdinand-ill", "cand-1609", "Ferdinand", "Grand Prince Ferdinand de' Medici."),
    (P241, 367, "academy-organizer", "cand-0004", "the Accademia del Disegno", "Institution under whose auspices the exhibition was organized."),
    (P241, 367, "exhibition-organized", "cand-7977", "it had been organised", "Coreference to the October 1706 exhibition."),
    (P241, 367, "academy-recent-existence", "cand-0004", "its recent existence", "Coreference to the Accademia del Disegno."),
    (P241, 367, "later-exhibition-series", "cand-8079", "Exhibitions, planned on similar lines", "Series with dates 1715, 1724, 1729, 1737, and 1767."),
    (P241, 368, "ferdinand-died", "cand-1609", "Ferdinand", "Grand Prince Ferdinand de' Medici."),
    (P241, 368, "later-events", "cand-8079", "any of these", "Coreference to the exhibitions listed on the preceding line."),
    (P241, 369, "venetian-school", "cand-8094", "the Venetian school of painting", "Art-historical category used by Haskell."),
    (P241, 369, "italian-painting", "cand-3461", "Italy", "Geographic scope of Haskell's assessment."),
    (P241, 369, "ferdinand-not-greatest-masters", "cand-1609", "he did not see", "Coreference to Ferdinand."),
    (P241, 369, "venetian-masters", "cand-8094", "its greatest masters", "Coreference to the Venetian school."),
    (P241, 369, "ferdinand-promotion", "cand-1609", "he had derived immense satisfaction", "Coreference to Ferdinand."),
    (P241, 369, "contemporary-art", "cand-8100", "contemporary art", "Broad art-historical category in Haskell's argument."),
    (P241, 369, "ferdinand-florence", "cand-1609", "he turned Florence", "Ferdinand's reported effect on Florence."),
    (P241, 369, "florence-centre", "cand-1041", "Florence", "City described as a centre of the painterly mode."),
    (P241, 369, "rome-theories", "cand-4490", "Rome", "City whose classical-academic theories are contrasted by Haskell."),
    (P241, 369, "rome-papal-city", "cand-4490", "the papal city", "Coreference to Rome."),
    (P241, 369, "artists-work-for-ferdinand", "cand-1609", "work for him", "Coreference to Ferdinand; this is Haskell's explanation of artists' preference."),
    (P241, 370, "ferdinand-anticipated-venice", "cand-1609", "he had anticipated", "Coreference to Ferdinand."),
    (P241, 370, "italian-painting-venice", "cand-3461", "Italian painting", "Geographic/art-historical category."),
    (P241, 370, "venice-itself", "cand-2719", "Venice itself", "City in Haskell's concluding assessment."),
    (NOTES, 453, "fogolari-note1", "cand-7894", "Fogolari, 1937", "Citation to Fogolari's publication, not independently consulted."),
    (NOTES, 453, "ricci-acquired-mehus", "cand-2179", "Ricci", "Sebastiano Ricci in the cited acquisition reference."),
    (NOTES, 453, "mehus-acquired", "cand-1632", "Mehus", "Livio Mehus."),
    (NOTES, 453, "ferdinand-acquisition", "cand-1609", "Ferdinand", "Grand Prince Ferdinand de' Medici."),
    (NOTES, 454, "hugford-note2", "cand-7871", "Hugford", "Cited at p.10 in support of the Gabbiani display passage; the page was not independently read."),
    (NOTES, 454, "fogolari-note3", "cand-7894", "Fogolari, 1937", "Cited publication."),
    (NOTES, 454, "fogolari-letter12", "cand-7929", "Letter 12 of 7 June 1698", "Letter locator; original not independently consulted."),
    (NOTES, 455, "fogolari-letter120", "cand-7950", "Letter 120 of 3 September 1707", "Letter locator supporting the quoted Cassana letter; original not independently consulted."),
    (NOTES, 456, "catalogue-title", "cand-8069", "Nota de’ Quadri che sono esposti", "Title as printed catalogue reference; title remainder retained in the statement quote."),
    (NOTES, 456, "catalogue-annunziata", "cand-8068", "SS. Nonziata", "OCR spelling in the title; page image reviewed, title form left as printed."),
    (NOTES, 456, "catalogue-firenze", "cand-1041", "Firenze", "Florence as named in the catalogue title."),
    (NOTES, 457, "fogolari-note1-p241", "cand-7894", "Fogolari", "Cited author and edition."),
    (NOTES, 457, "fogolari-letter116", "cand-8099", "Letter 116 of 17 October 1705", "Cited letter, not independently consulted."),
    (NOTES, 457, "cagnacci-picture-now-pitti", "cand-0479", "The picture", "Coreference to Guido Cagnacci's Magdalene in the preceding body text."),
    (NOTES, 457, "pitti-location", "cand-1949", "the Pitti", "Pitti Palace as reported by Haskell's footnote."),
    (NOTES, 458, "landscapes-note2", "cand-7962", "two of Marco’s landscapes", "Two works received by Ferdinand; do not equate with the four-work exhibition group."),
    (NOTES, 458, "ferdinand-received-landscapes", "cand-1609", "Ferdinand", "Grand Prince Ferdinand de' Medici."),
    (NOTES, 458, "landscapes-likely-lent", "cand-8077", "these were among those lent", "Haskell's likelihood qualification is retained."),
    (NOTES, 459, "exhibition-1767", "cand-8080", "the 1767 exhibition", "Later exhibition cited in note 3."),
    (NOTES, 459, "exhibition-1767-title", "cand-8081", "Il trionfo Jelle Bell'Arti", "OCR reads Jelle; p.241 image shows delle."),
    (NOTES, 459, "pietro-leopoldo", "cand-8097", "Pietro Leopoldo", "Person named in the catalogue title; no external identity alignment here."),
    (NOTES, 459, "maria-luisa", "cand-8098", "Maria Luisa di Borbone", "Person named in the catalogue title; no external identity alignment here."),
    (NOTES, 460, "sgrilli-p3", "cand-7847", "Sgrilli, p. z", "Citation locator; scan confirms p.3, not OCR p.z."),
    (NOTES, 461, "ferdinand-patronage-followers", "cand-1609", "Ferdinand’s patronage", "Grand Prince Ferdinand de' Medici."),
    (NOTES, 461, "contemporary-venetian-art", "cand-8101", "contemporary Venetian art", "Art-historical category in Haskell's note."),
    (NOTES, 461, "venetian-artists-gabburri", "cand-8104", "Venetian artists", "Collective artistic category; exact correspondents are unnamed."),
    (NOTES, 461, "gerini", "cand-1143", "the Marchese Andrea Gerini", "Index candidate for Marchese Andrea Gerini."),
    (NOTES, 461, "haskell-article", "cand-8096", "F. Haskell in Boll, dei Musei Civici Veneziani, i960", "Citation to Haskell's article; OCR i960 corrected to printed 1960."),
    (NOTES, 461, "gabburri", "cand-1097", "Francesco Gabburri", "Draftsman/connoisseur named in the note."),
    (NOTES, 461, "bottari-volume2", "cand-7516", "Bottari, Vol. II", "Cited publication candidate reused from chapter 8 section i."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first, last, subject, obj, predicate,
                   claim, qualification, mentioned, printed_page, pdf_physical_page,
                   text_layer="body", marker=None, extras=None):
    meta = segment_by_id[segment_id]
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first, "source_line_end": last,
        "printed_page": printed_page, "pdf_physical_page": pdf_physical_page,
        "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
        "qualification": qualification,
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
    make_statement("st-chp8-p240-mehus-collection", P240, 351, 351,
        "cand-1609", "cand-8060", "owns_about_thirty_works_by_livio_mehus",
        "Haskell says that among the Florentine school of the day only one artist was present in bulk, Livio Mehus, of whose works Ferdinand owned thirty; he also notes other Flemish works and only a bare representation of contemporary Roman painting.",
        "The count is about Mehus's works and is retained as given; Haskell calls Mehus Flemish and describes the Venetian quality of his art. The contemporary Roman painting phrase is a category, not a named artist or work.",
        ["cand-1609", "cand-1632", "cand-8060", "cand-8061", "cand-8093", "cand-8095", "cand-1041", "cand-8102", "cand-2630"], 240, 46,
        extras={"continuation_from_segment_id": P239}),
    make_statement("st-chp8-p240-mehus-appeal", P240, 351, 351,
        "cand-1632", "cand-1609", "vivacity_and_eroticism_appealed_to_ferdinand",
        "Haskell says Mehus was the most Venetian of the artists in Ferdinand's entourage and that his great vivacity, combined with slightly troubled eroticism, obviously appealed to Ferdinand.",
        "This is Haskell's art-historical characterization, not a statement attributed to Ferdinand himself.",
        ["cand-1632", "cand-1609"], 240, 46),
    make_statement("st-chp8-p240-mehus-death-and-patronage", P240, 351, 351,
        "cand-1632", "cand-1609", "death_may_have_prevented_direct_work_for_ferdinand",
        "Haskell says Mehus's death in 1691, before Ferdinand's patronage reached its fullest extent, can have prevented him from working directly for the Grand Prince.",
        "The causal wording is explicitly conjectural ('can have'); it is not upgraded to certainty.",
        ["cand-1632", "cand-1609"], 240, 46),
    make_statement("st-chp8-p240-ferdinand-mehus-canvases-and-son", P240, 351, 351,
        "cand-1609", "cand-8059", "collected_mehus_canvases_and_supported_his_son",
        "Haskell says Ferdinand sought to make amends by assiduously collecting Mehus's canvases and supporting Mehus's son.",
        "The son is unnamed; no identity or specific support is supplied. The note on this page cites Fogolari concerning Ricci acquiring Mehus works for Ferdinand, but the cited text was not independently read.",
        ["cand-1609", "cand-1632", "cand-8060", "cand-8059"], 240, 46,
        extras={"relation_candidate": True, "footnote_marker": 1,
                "continuation_closed_by_segment_id": P240}),
    make_statement("st-chp8-p240-room-and-ricci", P240, 352, 353,
        "cand-2179", "cand-8062", "painted_an_ambiguous_room_or_arrangement_for_ferdinand_in_1707",
        "Haskell describes Ferdinand's special room at Poggio a Caiano, holding small examples by ancient and contemporary favourite artists, and says Sebastiano Ricci painted 'this' for him in 1707.",
        "The exact referent of 'this' and the identity of the work are unclear; the room is kept separate from the other Poggio room candidate cand-7963 pending comparison.",
        ["cand-1609", "cand-1966", "cand-8062", "cand-2179", "cand-8063"], 240, 46,
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p240-collections-at-pratolino-and-castello", P240, 353, 354,
        "cand-1609", "cand-7838", "kept_large_collections_at_pratolino_and_villa_di_castello",
        "Haskell says Ferdinand kept further large collections at Pratolino and the Villa di Castello.",
        "The passage names the residences but does not enumerate or equate their holdings.",
        ["cand-1609", "cand-7838", "cand-8064"], 240, 46,
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p240-exhibition-as-art-direction", P240, 355, 355,
        "cand-1609", "cand-0128", "used_exhibitions_to_guide_florentine_painting",
        "Haskell says Ferdinand sought to guide the direction of painting in Florence and used the still-rudimentary art exhibition as an instrument in a new way.",
        "This is Haskell's account of Ferdinand's purpose and innovation; it does not identify an institution in this sentence.",
        ["cand-1609", "cand-1041", "cand-0128"], 240, 46,
        extras={"relation_candidate": True,
                "ocr_corrections": [{"source_line": 355, "ocr": "confmed", "print": "confined", "basis": "CHP-8.pdf physical page 46"},
                                    {"source_line": 355, "ocr": "instrumentof", "print": "instrument of", "basis": "CHP-8.pdf physical page 46"}]}),
    make_statement("st-chp8-p240-corpus-domini-exhibitions", P240, 355, 355,
        "cand-6024", "cand-1041", "corpus_domini_processions_were_occasions_for_picture_displays",
        "Haskell says pictures had been exhibited in Florence and many other Italian cities on the occasion of Corpus Domini processions.",
        "The statement describes a recurring occasion, not a single dated exhibition.",
        ["cand-6024", "cand-1041", "cand-3461", "cand-0128"], 240, 46),
    make_statement("st-chp8-p240-ferdinand-displays-gabbiani", P240, 355, 356,
        "cand-1609", "cand-1095", "showed_gabbianis_flight_into_egypt_at_piazza_del_duomo",
        "Haskell says Ferdinand regularly showed works painted for him by artists he approved, including Gabbiani's Flight into Egypt, which he put on public view in Piazza del Duomo.",
        "The work and display are reported by Haskell; the passage does not identify a precise date or present location.",
        ["cand-1609", "cand-1093", "cand-1095", "cand-8065"], 240, 46,
        extras={"relation_candidate": True, "footnote_marker": 2}),
    make_statement("st-chp8-p240-ferdinand-displays-sacconi-and-cassana", P240, 357, 357,
        "cand-1609", "cand-0593", "extended_display_policy_to_sacconi_and_cassana",
        "Haskell says Ferdinand applied the same exhibition policy to Sacconi and especially Cassana; in 1707 Ferdinand wrote admiring the 'gran gusto' of Cassana's Portrait of a Cook and intended to exhibit it so local artists could see how timidly they painted.",
        "The quotation is reported by Haskell and linked in note 4 to Fogolari, Letter 120 of 3 September 1707; the letter was not independently consulted. The OCR footnote marker after the quotation is corrected from '?' to printed 4.",
        ["cand-1609", "cand-2325", "cand-0593", "cand-7940", "cand-7950"], 240, 46,
        extras={"relation_candidate": True, "quoted_speaker": "Ferdinand, as reported by Haskell",
                "ocr_corrections": [{"source_line": 357, "ocr": "?", "print": "4", "basis": "CHP-8.pdf physical page 46"}]}),
    make_statement("st-chp8-p240-1706-exhibition-and-san-rocco", P240, 357, 357,
        "cand-1609", "cand-7977", "organized_a_larger_1706_exhibition_probably_inspired_by_san_rocco",
        "Haskell says Ferdinand probably found the casual displays ineffective and by 1706 had organized something grander, perhaps taking the idea from the S. Rocco exhibitions in Venice but running his own on more spectacular lines.",
        "Both the judgment about the casual displays and the San Rocco inspiration are qualified by Haskell; the individual Venetian exhibitions are not identified.",
        ["cand-1609", "cand-0128", "cand-7977", "cand-0138", "cand-2719"], 240, 46,
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p240-catalogue-and-reconstruction", P240, 358, 358,
        "cand-8069", "cand-7977", "printed_catalogue_issued_for_1706_exhibition",
        "Haskell says a printed catalogue was issued, an innovation for Italy, and that the event can be reconstructed from it.",
        "The catalogue is described in note 5 at OCR L456; neither it nor its contents were independently consulted.",
        ["cand-8069", "cand-7977", "cand-3461"], 240, 46,
        extras={"relation_candidate": True, "footnote_marker": 5}),
    make_statement("st-chp8-p240-exhibition-date-and-venue", P240, 358, 359,
        "cand-7977", "cand-8067", "held_on_saint_lukes_day_in_annunziata_chapel",
        "Haskell dates the exhibition to St Luke's day, 18 October, in the chapel dedicated to that saint in the Annunziata cloisters.",
        "The year 1706 is supplied by the surrounding account and the catalogue title; the venue is not expanded beyond the source wording.",
        ["cand-7977", "cand-8066", "cand-8067", "cand-8068"], 240, 46,
        extras={"relation_candidate": True, "continuation_to_segment_id": NOTES}),
    make_statement("st-chp8-p240-exhibition-count-and-loan-sources", NOTES, 452, 452,
        "cand-7977", "cand-8072", "showed_about_250_pictures_mostly_borrowed_from_florence_collections",
        "Haskell says about 250 pictures were shown, nearly all borrowed from Florence's great collections and none from the Grand Duke's collection.",
        "This is printed body text on p.240, physically confirmed by the PDF, but stored at L452 in the consolidated OCR notes segment. The Grand Duke remains unidentified and distinct from Ferdinand.",
        ["cand-7977", "cand-8072", "cand-1041", "cand-8073"], 240, 46,
        text_layer="body continuation in consolidated OCR segment"),
    make_statement("st-chp8-p240-lunette-display", NOTES, 452, 452,
        "cand-7977", "cand-8070", "displayed_twelve_ferdinand_pictures_in_first_lunette_and_portrait_above_chapel_door",
        "Haskell describes groups of about eight to ten pictures in the cloister lunettes; the first lunette held twelve pictures lent by Ferdinand, followed above the chapel door by a portrait of the Grand Prince.",
        "This is printed body text on p.240 stored at OCR L452. The twelve works and portrait are kept as separate unidentified work candidates; p.241 continues the portrait sentence.",
        ["cand-7977", "cand-8068", "cand-8070", "cand-1609", "cand-8071"], 240, 46,
        text_layer="body continuation in consolidated OCR segment",
        extras={"relation_candidate": True, "continuation_to_segment_id": P241}),
    make_statement("st-chp8-p241-portrait-as-patronage-signal", P241, 362, 362,
        "cand-8071", "cand-7977", "portrait_signalled_ferdinands_patronage_of_exhibition",
        "Haskell says the portrait of the Grand Prince above the chapel door unmistakably showed his patronage of the exhibition and that the orientation of his taste made clear the impulse he wanted to give contemporary art.",
        "This is Haskell's interpretation of the display and patronage signal; the portrait's maker and exact identity remain unknown.",
        ["cand-8071", "cand-1609", "cand-7977"], 241, 47,
        extras={"relation_candidate": True, "continuation_from_segment_id": NOTES}),
    make_statement("st-chp8-p241-twenty-odd-loans", P241, 362, 363,
        "cand-1609", "cand-8076", "lent_twenty_odd_pictures_to_1706_exhibition",
        "Haskell says Ferdinand lent twenty-odd pictures in all and lists seven Venetian old-master paintings, followed by an early Guercino, a Lodovico Carracci, and a Schedoni.",
        "The count is approximate; titles and locations for the unnamed paintings are not supplied.",
        ["cand-1609", "cand-8076", "cand-8082", "cand-8083", "cand-8084", "cand-8085", "cand-8086", "cand-8087", "cand-8088", "cand-8089", "cand-8090", "cand-8091"], 241, 47,
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p241-additional-loans", P241, 363, 363,
        "cand-1609", "cand-0479", "also_lent_cagnacci_magdalene_cassana_hunter_and_probably_marco_landscapes",
        "Haskell says Ferdinand also lent Guido Cagnacci's Magdalene, Cassana's Portrait of a Hunter, and, almost certainly, four landscapes by Marco Ricci.",
        "The Marco Ricci attribution is explicitly probable and note 2 says the lender is not named; only two landscapes received by Ferdinand in May 1706 are said to be likely among those lent.",
        ["cand-1609", "cand-0478", "cand-0479", "cand-0593", "cand-0599", "cand-2149", "cand-8077"], 241, 47,
        extras={"relation_candidate": True, "footnote_markers": [1, 2]}),
    make_statement("st-chp8-p241-florentine-absence-and-cardinal-loan", P241, 364, 364,
        "cand-1609", "cand-8075", "omitted_florentine_works_and_cardinal_medici_lent_more_venetian_paintings",
        "Haskell says the Grand Prince showed no works by Florentine artists represented in his collection, an unmistakable hint reinforced by further Venetian paintings lent by Cardinal Medici.",
        "The 'hint' is Haskell's interpretation. Cardinal Medici's identity and the works are unspecified; the Grand Prince is Ferdinand.",
        ["cand-1609", "cand-1041", "cand-8103", "cand-8075", "cand-8074"], 241, 47,
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p241-venetian-and-neapolitan-contingents", P241, 365, 366,
        "cand-7977", "cand-8092", "showed_impressive_venetian_and_strong_neapolitan_contingents",
        "Haskell says Venetians made an impressive showing and that there was also a strong Neapolitan contingent, mainly lent by the del Rosso brothers, with Luca Giordano much in evidence.",
        "The paintings, individual lenders, and Giordano works are not specified; the del Rosso brothers remain a collective endpoint.",
        ["cand-7977", "cand-8104", "cand-8092", "cand-8078", "cand-1172"], 241, 47,
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p241-attendance-success-and-academy", P241, 367, 367,
        "cand-1609", "cand-0004", "attended_successful_exhibition_organized_under_academy_auspices",
        "Haskell says Ferdinand attended the exhibition, which remained open several days and was evidently successful; after Ferdinand fell seriously ill, the Accademia del Disegno returned to inactivity after organizing it under its auspices.",
        "Evidently successful and the characterization of institutional inactivity are Haskell's assessments; the illness is not diagnosed.",
        ["cand-1609", "cand-7977", "cand-0004"], 241, 47,
        extras={"relation_candidate": True,
                "ocr_corrections": [{"source_line": 367, "ocr": "173 7", "print": "1737", "basis": "CHP-8.pdf physical page 47"}]}),
    make_statement("st-chp8-p241-later-exhibitions-before-ferdinands-death", P241, 367, 368,
        "cand-8079", "cand-1609", "later_similar_exhibitions_occurred_after_ferdinands_death",
        "Haskell lists later exhibitions on similar lines in 1715, 1724, 1729, 1737, and 1767, then says Ferdinand died before any of them.",
        "No death year is added; the temporal relation is only that he died before the listed events.",
        ["cand-8079", "cand-1609"], 241, 47),
    make_statement("st-chp8-p241-venetian-school-and-florence", P241, 369, 369,
        "cand-1609", "cand-1041", "promoted_contemporary_art_and_made_florence_a_painterly_centre",
        "Haskell says the Venetian school was widely recognized as Italy's liveliest; Ferdinand took satisfaction in promoting vital contemporary art and for a few years turned Florence into a centre of the painterly, against classical-academic theories that dictated practice in Rome.",
        "These are Haskell's broad art-historical evaluations, not independently verified consensus claims. The theoretical contrast is preserved without defining a formal movement.",
        ["cand-1609", "cand-8094", "cand-3461", "cand-1041", "cand-4490"], 241, 47),
    make_statement("st-chp8-p241-artists-preferred-ferdinand", P241, 369, 369,
        "cand-1609", "cand-4490", "artists_fearing_stifling_in_rome_delighted_to_work_for_ferdinand",
        "Haskell says it is unsurprising that artists who felt their talents would have been stifled in the papal city were delighted to work for Ferdinand.",
        "This is Haskell's explanation of artists' reported preference; no individual artists are named in this sentence.",
        ["cand-1609", "cand-4490"], 241, 47,
        extras={"relation_candidate": True}),
    make_statement("st-chp8-p241-quoted-praise-and-art-patronage", P241, 369, 369,
        "cand-1609", "cand-7847", "haskell_partly_accepts_mid_eighteenth_century_praise_of_ferdinand",
        "Haskell says Ferdinand played a notable part in accounts of Italian art patronage and that one can understand, though not wholly endorse, a mid-eighteenth-century writer's description of him as unrivalled in magnanimity and generosity.",
        "The attribution is Haskell's; note 4 cites Sgrilli p.3, but the cited page was not independently consulted and the writer is not identified in the body text.",
        ["cand-1609", "cand-3461", "cand-7847"], 241, 47,
        marker=4),
    make_statement("st-chp8-p241-venice-concluding-assessment", P241, 370, 370,
        "cand-1609", "cand-2719", "anticipated_venice_as_location_of_most_interesting_italian_painting",
        "Haskell concludes that by that time the most interesting Italian painting was to be found in Venice, as Ferdinand had anticipated.",
        "This is Haskell's art-historical assessment; the comparison is not independently tested.",
        ["cand-1609", "cand-3461", "cand-2719"], 241, 47,
        marker=5),
    make_statement("st-chp8-p240-note1-fogolari-mehus-acquisition", NOTES, 453, 453,
        "cand-2179", "cand-1632", "note_cites_fogolari_on_ricci_acquiring_mehus_works_for_ferdinand",
        "Note 1 directs readers to Fogolari, 1937, p.161 note 43, concerning Ricci acquiring works by Mehus for Ferdinand.",
        "This is a citation locator and Haskell's summary of its relevance; the cited source was not independently consulted. OCR p. l6l is corrected to printed p.161.",
        ["cand-7894", "cand-2179", "cand-1632", "cand-1609"], 240, 46,
        text_layer="footnote source locator", marker=1,
        extras={"linked_body_statement_ids": ["st-chp8-p240-mehus-collection", "st-chp8-p240-ferdinand-mehus-canvases-and-son"],
                "ocr_corrections": [{"source_line": 453, "ocr": "p. l6l", "print": "p. 161", "basis": "CHP-8.pdf physical page 46"}]}),
    make_statement("st-chp8-p240-note2-hugford-locator", NOTES, 454, 454,
        None, "cand-7871", "note_cites_hugford_page_10",
        "Note 2 cites Hugford, p.10, in support of the Gabbiani display passage.",
        "Citation only; Hugford's page was not independently consulted.",
        ["cand-7871"], 240, 46, text_layer="footnote citation", marker=2,
        extras={"linked_body_statement_ids": ["st-chp8-p240-ferdinand-displays-gabbiani"]}),
    make_statement("st-chp8-p240-note3-fogolari-letter12", NOTES, 454, 454,
        None, "cand-7929", "note_cites_fogolari_letter_12",
        "Note 3 cites Fogolari, 1937, Letter 12 of 7 June 1698.",
        "Citation only; the letter was not independently consulted.",
        ["cand-7894", "cand-7929"], 240, 46, text_layer="footnote citation", marker=3,
        extras={"linked_body_statement_ids": ["st-chp8-p240-ferdinand-displays-sacconi-and-cassana"]}),
    make_statement("st-chp8-p240-note4-fogolari-letter120", NOTES, 455, 455,
        None, "cand-7950", "note_cites_fogolari_letter_120",
        "Note 4 cites Fogolari, 1937, Letter 120 of 3 September 1707.",
        "Citation locator for the reported Cassana letter; the archival source was not independently consulted.",
        ["cand-7894", "cand-7950"], 240, 46, text_layer="footnote citation", marker=4,
        extras={"linked_body_statement_ids": ["st-chp8-p240-ferdinand-displays-sacconi-and-cassana"]}),
    make_statement("st-chp8-p240-note5-catalogue-title", NOTES, 456, 456,
        None, "cand-8069", "note_gives_1706_catalogue_title",
        "Note 5 gives the title and Firenze 1706 publication line of the St Luke's Day exhibition catalogue.",
        "The catalogue was not independently consulted. The OCR title's spelling is retained; the image confirms printed note number 5.",
        ["cand-8069", "cand-7977", "cand-8068", "cand-1041"], 240, 46,
        text_layer="footnote source description", marker=5,
        extras={"linked_body_statement_ids": ["st-chp8-p240-catalogue-and-reconstruction"],
                "ocr_corrections": [{"source_line": 456, "ocr": "I’Anno", "print": "l’Anno", "basis": "CHP-8.pdf physical page 46"}]}),
    make_statement("st-chp8-p241-note1-fogolari-letter116", NOTES, 457, 457,
        "cand-7894", "cand-8099", "note_cites_letter_116_and_reports_picture_in_pitti_no_75",
        "Note 1 cites Fogolari, 1937, Letter 116 of 17 October 1705, and says the picture is now in the Pitti, No.75.",
        "The cited letter and current location were not independently checked; 'the picture' links to the immediately preceding Cagnacci Magdalene. OCR 193 7 is corrected to printed 1937.",
        ["cand-7894", "cand-8099", "cand-0479", "cand-1949"], 241, 47,
        text_layer="footnote report", marker=1,
        extras={"linked_body_statement_ids": ["st-chp8-p241-additional-loans"],
                "ocr_corrections": [{"source_line": 457, "ocr": "193 7", "print": "1937", "basis": "CHP-8.pdf physical page 47"}]}),
    make_statement("st-chp8-p241-note2-uncertain-landscape-lender", NOTES, 458, 458,
        "cand-1609", "cand-8077", "two_received_marco_landscapes_may_be_among_four_lent",
        "Note 2 says the lender is unnamed, but that Ferdinand had received two Marco landscapes in May 1706 and it seems very likely those were among the four lent.",
        "The connection is explicitly probable; the two received landscapes cand-7962 are not merged with the four-work exhibition group cand-8077. The note cross-refers to p.235 note 4 and Appendix 4.",
        ["cand-1609", "cand-2149", "cand-7962", "cand-8077"], 241, 47,
        text_layer="footnote report", marker=2,
        extras={"linked_body_statement_ids": ["st-chp8-p241-additional-loans"],
                "cross_reference_pages": ["p.235 note 4", "Appendix 4"]}),
    make_statement("st-chp8-p241-note3-1767-catalogue", NOTES, 459, 459,
        None, "cand-8081", "note_cites_introduction_to_1767_exhibition",
        "Note 3 refers readers to the introduction to the 1767 exhibition and gives its title, naming Pietro Leopoldo and Maria Luisa di Borbone.",
        "The catalogue introduction was not independently consulted; the OCR Jelle is corrected to the printed delle. People in the title remain unaligned pending S3.",
        ["cand-8080", "cand-8081", "cand-8097", "cand-8098"], 241, 47,
        text_layer="footnote source description", marker=3,
        extras={"linked_body_statement_ids": ["st-chp8-p241-later-exhibitions-before-ferdinands-death"],
                "ocr_corrections": [{"source_line": 459, "ocr": "Jelle", "print": "delle", "basis": "CHP-8.pdf physical page 47"}]}),
    make_statement("st-chp8-p241-note4-sgrilli-locator", NOTES, 460, 460,
        None, "cand-7847", "note_cites_sgrilli_page_3",
        "Note 4 cites Sgrilli, p.3, for the mid-eighteenth-century praise quoted in the body.",
        "The source page was not independently consulted; OCR p.z is corrected to printed p.3.",
        ["cand-7847"], 241, 47, text_layer="footnote citation", marker=4,
        extras={"linked_body_statement_ids": ["st-chp8-p241-quoted-praise-and-art-patronage"],
                "ocr_corrections": [{"source_line": 460, "ocr": "p. z", "print": "p. 3", "basis": "CHP-8.pdf physical page 47"}]}),
    make_statement("st-chp8-p241-note5-gerini-follower", NOTES, 461, 461,
        "cand-1143", "cand-1609", "was_a_significant_follower_of_ferdinands_venetian_patronage",
        "Note 5 says Ferdinand's patronage of contemporary Venetian art had at least one significant follower in Florence: Marchese Andrea Gerini.",
        "This is Haskell's report and directs readers to his article; the article was not independently consulted. Printed note number is 5, although OCR gives 6.",
        ["cand-1143", "cand-1609", "cand-8096", "cand-8101"], 241, 47,
        text_layer="footnote report", marker=5,
        extras={"linked_body_statement_ids": ["st-chp8-p241-venetian-school-and-florence"],
                "ocr_corrections": [{"source_line": 461, "ocr": "6", "print": "5", "basis": "CHP-8.pdf physical page 47"},
                                    {"source_line": 461, "ocr": "sec F. Haskell", "print": "see F. Haskell", "basis": "CHP-8.pdf physical page 47"},
                                    {"source_line": 461, "ocr": "i960", "print": "1960", "basis": "CHP-8.pdf physical page 47"}]}),
    make_statement("st-chp8-p241-note5-gabburri-correspondence", NOTES, 461, 461,
        "cand-1097", "cand-8104", "kept_in_touch_with_venetian_artists_via_letters_published_by_bottari",
        "Note 5 says Francesco Gabburri, a connoisseur of drawings, kept in touch with Venetian artists, as shown by many letters published by Bottari, volume II.",
        "The letters and cited publication were not independently consulted; individual correspondents are not named in this note.",
        ["cand-1097", "cand-8104", "cand-7516"], 241, 47,
        text_layer="footnote report", marker=5,
        extras={"ocr_corrections": [{"source_line": 461, "ocr": "connoisssur", "print": "connoisseur", "basis": "CHP-8.pdf physical page 47"}]}),
]

statement_ids = {row["statement_id"] for row in statement_rows}
if len(statement_ids) != len(statement_rows) or any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("duplicate statement ID")

for row in coverage_rows:
    if row["segment_id"] == P239:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L339-348",
                    "note": "p.239 body reviewed against physical page 45; its unfinished Venetian-picture sentence closes at p.240 L351. Embedded note 4 and notes 1-3/5 are migrated."})
    elif row["segment_id"] == P240:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L351-359",
                    "note": "p.240 body reviewed against physical page 46. The body continuation stored at consolidated segment L452 was verified on the same printed page; the portrait sentence closes at p.241 L362. Notes 1-5 at L453-456 are migrated."})
    elif row["segment_id"] == P241:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L362-370",
                    "note": "p.241 body reviewed against physical page 47, including closure of p.240 L452 portrait sentence at L362. Notes 1-5 are mapped to consolidated segment L457-461."})
    elif row["segment_id"] == NOTES:
        row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L373-461",
                    "note": "Consolidated notes reviewed through p.241 note 5. L452 is body continuation printed on p.240, verified against the PDF and recorded as body text; notes p.240 are L453-456 and p.241 are L457-461."})

prior_venetian = next((row for row in statement_rows if row["statement_id"] == "st-chp8-p239-venetian-emphasis"), None)
if not prior_venetian:
    raise SystemExit("missing p.239 continuation statement")
prior_venetian["qualifiers"]["qualification"] = "The sentence continues and closes at p.240 L351, where Haskell says about ten paintings were attributed to Titian. No individual work identity or exact total is inferred."
prior_venetian["qualifiers"].pop("continuation_to_segment_id", None)
prior_venetian["qualifiers"]["continuation_closed_by_segment_id"] = P240
prior_venetian["qualifiers"]["continuation_closed_by_line"] = 351

preview = {
    "mode": "dry-run", "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage_updates": {P239: "complete", P240: "complete", P241: "complete", NOTES: "complete through L461"},
    "print_corrections": [
        "p.240 L355 confmed -> confined; instrumentof -> instrument of",
        "p.240 L357 OCR ? -> printed footnote marker 4",
        "p.240 L453 p. l6l -> p.161",
        "p.240 L456 I’Anno -> l’Anno",
        "p.241 L367 173 7 -> 1737",
        "p.241 L457 193 7 -> 1937",
        "p.241 L459 Jelle -> delle",
        "p.241 L460 p. z -> p.3",
        "p.241 L461 note marker 6 -> 5; sec -> see; i960 -> 1960; connoisssur -> connoisseur",
    ],
    "preserved_uncertainties": [
        "Livio Mehus's son is unnamed",
        "Sebastiano Ricci's 1707 work and the referent of 'this' are unspecified",
        "the special Poggio a Caiano room is not merged with candidate cand-7963",
        "the 1706 exhibition's Grand Duke and Cardinal Medici remain unidentified",
        "the twelve first-lunette pictures and the Prince's portrait remain unidentified works",
        "Haskell's four Marco Ricci landscapes are 'almost certainly'; note 2 keeps the lender unknown and only probably links two works received by Ferdinand",
        "the del Rosso brothers remain a collective endpoint; no individual lender is assigned",
        "Saint Luke candidate cand-8066 is not merged with chp.1 candidate cand-3564 before S3",
        "the cited letters, exhibition catalogues, and publications were not independently consulted",
        "OCR L452 is body text on printed p.240 and continues at p.241 L362",
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
