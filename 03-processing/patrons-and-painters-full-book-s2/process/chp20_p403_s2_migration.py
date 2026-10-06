#!/usr/bin/env python3
"""Controlled S2 migration for printed page 403 and p.402 continuation."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-20Postscript.pdf"
P402 = "chp-20:20_CHP-20Postscript:l98-108"
P403 = "chp-20:20_CHP-20Postscript:l110-121"
P404 = "chp-20:20_CHP-20Postscript:l123-135"
NOTES = "chp-20:20_CHP-20Postscript:l211-280"
BACKUP = ".bak-s2-chp20-p403-20261004"
SOURCE_SHA = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
PDF_SHA = "f4c3852b60596ee0116b941ad97c7f2cb79414fe6b6b0388efcebeef538c1788"
P402_SHA = "64eb2299cfe55d839d396f3ac35f345ecc661c6ccde89528b08263d70b99e765"
P403_SHA = "7bc5e518a943cfa45d60c928cbff4ae1a8be817201c0d88fb9d8c4d00c5fe81b"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
ARGS = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


if sha(SOURCE) != SOURCE_SHA:
    raise SystemExit("source asset changed")
if sha(PDF) != PDF_SHA:
    raise SystemExit("PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body = "\n".join(source_lines[109:121])
if hashlib.sha256(body.encode("utf-8")).hexdigest() != P403_SHA:
    raise SystemExit("p.403 S0 segment hash mismatch")
if hashlib.sha256("\n".join(source_lines[97:108]).encode("utf-8")).hexdigest() != P402_SHA:
    raise SystemExit("p.402 S0 segment hash mismatch")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage = read_csv(coverage_path)
statements = [
    json.loads(line)
    for line in statement_path.read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
segments = [
    json.loads(line)
    for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
    if line.strip()
]
segment_by_id = {row["segment_id"]: row for row in segments}
candidate_by_id = {row["candidate_id"]: row for row in candidates}
coverage_by_id = {row["segment_id"]: row for row in coverage}
for segment_id in (P402, P403, P404, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"missing S0/S2 segment: {segment_id}")
if segment_by_id[P403]["sha256"] != P403_SHA or segment_by_id[P403]["asset_sha256"] != SOURCE_SHA:
    raise SystemExit("p.403 segment registration changed")
if coverage_by_id[P402]["migration_status"] != "partial":
    raise SystemExit("p.402 must be partial before continuation")
if (coverage_by_id[P403]["disposition"], coverage_by_id[P403]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.403 is not queued/pending")
if coverage_by_id[P404]["disposition"] != "queued":
    raise SystemExit("p.404 must remain queued")
if coverage_by_id[NOTES]["disposition"] != "queued":
    raise SystemExit("notes segment must remain queued")

# Resolve the only source-derived placeholder on p.402 now that p.403 identifies the work.
placeholder_id = "cand-10994"
placeholder = candidate_by_id.get(placeholder_id)
if not placeholder or placeholder["canonical_name"] != "Unspecified picture in Alazard's commissioned-work reference (commissioner, title, and artist unresolved)":
    raise SystemExit("p.402 placeholder candidate changed")
continuation_mention_id = "m-chp20-p402-038"
continuation_mention = next((row for row in mentions if row["mention_id"] == continuation_mention_id), None)
if not continuation_mention or continuation_mention["segment_id"] != P402 or continuation_mention["candidate_id"] != placeholder_id:
    raise SystemExit("p.402 continuation mention changed")
if continuation_mention["surface_form"] != "a picture commissioned":
    raise SystemExit("p.402 continuation anchor changed")
continuation_statement_id = "st-chp20-p402-louisxiv-alazard-commissioned-picture-open"
continuation_statement = next((row for row in statements if row["statement_id"] == continuation_statement_id), None)
if not continuation_statement or continuation_statement["object_candidate_id"] != placeholder_id:
    raise SystemExit("p.402 open statement changed")

candidate_specs = [
    ("cand-10995", "Pierre Rosenberg", "person", "Named as the scholar who identified and published the painting; identity alignment is deferred to S3."),
    ("cand-10996", "Prince of Liechtenstein (patron discussed through Lankheit's research)", "person", "The passage gives no personal name; do not merge with other Prince of Liechtenstein candidates before S3."),
    ("cand-10997", "Lankheit (scholar cited by surname on p.403)", "person", "Surname only in the source passage; full identity is deferred to S3 and the notes/bibliography pass."),
    ("cand-10998", "English royal patronage of Italian painting in the seventeenth and eighteenth centuries", "term", "Subject of Levey's survey; the passage describes a field of patronage, not a separate institution."),
    ("cand-10999", "Michael Levey", "person", "Full name supplied in the passage; keep separate from surname-only candidates until S3 resolves identity."),
    ("cand-11000", "Michael Levey's catalogue of later Italian pictures in the Queen's collection", "archive", "A catalogue cited as a survey of English royal patronage; not independently consulted here."),
    ("cand-11001", "Croft-Murray (scholar cited on p.403)", "person", "Surname only in the passage; do not merge with the earlier p.284 candidate before S3."),
    ("cand-11002", "Croft-Murray's account of Antonio Verrio's career in England", "archive", "A detailed account cited for Restoration-period patronage; bibliographic identity awaits notes and bibliography review."),
    ("cand-11003", "Exhibition devoted to Sir Thomas Isham", "event", "The exhibition is named only by its subject; no title or date is supplied in this passage."),
    ("cand-11004", "Catalogue of the exhibition devoted to Sir Thomas Isham", "archive", "A useful catalogue is mentioned but not independently consulted; bibliographic details remain pending."),
    ("cand-11005", "Seventeenth-century Florentine art (Florentine Seicento)", "term", "The passage discusses this field of art; it does not provide a fixed exhibition or disciplinary title."),
    ("cand-11006", "Artisti alla Corte Granducale exhibition (1969)", "event", "The source and page image identify the 1969 exhibition; keep the OCR title correction in the statement."),
    ("cand-11007", "Catalogue of the Artisti alla Corte Granducale exhibition (1969)", "archive", "The important catalogue is attributed to Marco Chiarini; it is not independently consulted here."),
    ("cand-11008", "Marco Chiarini", "person", "Named as the writer of the exhibition catalogue; identity alignment is deferred to S3."),
    ("cand-11009", "Malcolm Campbell", "person", "Named as the scholar whose article and book are discussed; identity alignment is deferred to S3."),
    ("cand-11010", "Malcolm Campbell's article on Grand Duke Ferdinand II's decision (1966)", "archive", "Article cited by footnote 8; exact title and publication details await notes/bibliography review."),
    ("cand-11011", "Malcolm Campbell's book on Florentine art and patronage (1977)", "archive", "Book cited by footnote 9; exact title and publication details await notes/bibliography review."),
    ("cand-11012", "Provincial Florentine artists", "term", "A source-derived characterization of artists in the passage; do not turn it into a named group or institution."),
    ("cand-11013", "Evelina Borea", "person", "Named as the author of a catalogue; identity alignment is deferred to S3."),
    ("cand-11014", "Evelina Borea's catalogue of the exhibition devoted to Don Lorenzo de' Medici's collection", "archive", "The catalogue and exhibition are described, but neither is independently consulted in this passage."),
    ("cand-11015", "Florentine provincialism", "term", "The source's interpretive characterization; preserve its attributed context and incomplete sentence."),
    ("cand-11016", "Florentine culture", "term", "The source's cultural concept; no separate institution is implied."),
    ("cand-11017", "Italian painting", "term", "Named as the subject of the royal collection catalogue; distinguish from Italian art generally."),
    ("cand-11018", "Restoration period patronage in England", "term", "Period and subject of the source's account; this does not designate a separate event."),
    ("cand-11019", "Exhibition on seventeenth-century Florentine art in New York (1969)", "event", "Descriptive source-derived label only; no official exhibition title is given."),
    ("cand-11020", "Exhibition on seventeenth-century Florentine art in Florence (1965)", "event", "Descriptive source-derived label only; no official exhibition title is given."),
    ("cand-11021", "Exhibition on seventeenth-century Florentine art in Florence (1974)", "event", "Descriptive source-derived label only; no official exhibition title is given."),
    ("cand-11022", "Exhibition on seventeenth-century Florentine art in London (1979)", "event", "Descriptive source-derived label only; no official exhibition title is given."),
]
candidate_source_lines = {
    "cand-10995": 113, "cand-10996": 114, "cand-10997": 114,
    "cand-10998": 115, "cand-10999": 115, "cand-11000": 115,
    "cand-11001": 115, "cand-11002": 115, "cand-11003": 116,
    "cand-11004": 116, "cand-11005": 118, "cand-11006": 120,
    "cand-11007": 120, "cand-11008": 120, "cand-11009": 120,
    "cand-11010": 120, "cand-11011": 120, "cand-11012": 120,
    "cand-11013": 121, "cand-11014": 121, "cand-11015": 121,
    "cand-11016": 121, "cand-11017": 115, "cand-11018": 115,
    "cand-11019": 118, "cand-11020": 118, "cand-11021": 118,
    "cand-11022": 118,
}

natural_keys = {
    (row["canonical_name"].strip().casefold(), row["suggested_type"].strip().casefold())
    for row in candidates
}
for candidate_id, name, kind, detail in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID exists: {candidate_id}")
    key = (name.strip().casefold(), kind.casefold())
    if key in natural_keys:
        raise SystemExit(f"candidate natural-key collision: {name}")
    row = {
        "candidate_id": candidate_id,
        "index_entry_id": "",
        "canonical_name": name,
        "index_page_range": "",
        "suggested_type": kind,
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": detail,
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P403}#L{candidate_source_lines[candidate_id]}",
    }
    candidates.append(row)
    candidate_by_id[candidate_id] = row
    natural_keys.add(key)

# candidate, exact source spelling, first/last source line, occurrence within that line span, note
mention_specs = [
    ("cand-0800", "Colbert", 111, 111, 0, "Named as an intermediary in the commission account; not identified as commissioner."),
    ("cand-2528", "Abate Luigi Strozzi", 111, 111, 0, "Named as an intermediary; the text does not define his precise role beyond the parenthetical."),
    ("cand-1066", "Baldassare Franceschini, il\nVolterrano", 111, 112, 0, "Full name and alias span a source line break; reuse the indexed artist candidate."),
    ("cand-6888", "Fame Carrying the Name os the King to the Temple of Immortality", 112, 112, 0, "Reuse the Plate 66 work candidate; source OCR reads 'os', corrected to 'of' by the page image."),
    ("cand-4186", "Fame", 112, 112, 0, "Allegorical figure within the work title; reuse the existing candidate."),
    ("cand-1447", "the King", 112, 112, 0, "The Plate 66 title identifies the King as Louis XIV; reuse the existing candidate."),
    ("cand-4189", "Temple of Immortality", 112, 112, 0, "Allegorical setting within the work title; reuse the existing candidate."),
    ("cand-6888", "this picture", 112, 112, 0, "Anaphoric reference to the Plate 66 painting."),
    ("cand-7287", "Versailles", 112, 112, 0, "Haskell reports the painting was still there in the second-edition text; this is not a current-location verification."),
    ("cand-10995", "Pierre\nRosenberg", 112, 113, 0, "Full name spans a line break; source says he identified and published the painting."),
    ("cand-6994", "Holy Roman Empire", 114, 114, 0, "Reuse the existing political-entity candidate."),
    ("cand-4131", "Italian art", 114, 114, 0, "Reuse the existing term candidate."),
    ("cand-10996", "Prince Liechtenstein", 114, 114, 0, "Person is not named; do not map to the Liechtenstein family or another prince."),
    ("cand-10997", "Lankheit", 114, 114, 0, "Surname-only scholar; full identity awaits S3 and bibliography review."),
    ("cand-2384", "Prince Eugens", 114, 114, 0, "Reuse Prince Eugene candidate; OCR/source text omits the possessive apostrophe."),
    ("cand-10998", "English royal patronage of Italian painting", 115, 115, 0, "Subject of the general survey; reuse the p.403 term candidate."),
    ("cand-11017", "Italian painting", 115, 115, 0, "Field named in the catalogue description."),
    ("cand-7200", "England", 115, 115, 0, "Geographic context of the patronage account."),
    ("cand-10999", "Michael Levey", 115, 115, 0, "Full name in the source; keep separate from unresolved surname-only candidates pending S3."),
    ("cand-11000", "catalogue of the later Italian pictures in the Queen’s collection", 115, 115, 0, "Descriptive bibliographic object; exact title is not supplied."),
    ("cand-2292", "Queen’s collection", 115, 115, 0, "Reuse the Royal Collection candidate; the phrasing is Haskell's."),
    ("cand-11001", "Croft-Murray", 115, 115, 0, "Surname-only scholar; keep separate from the p.284 candidate pending S3."),
    ("cand-11002", "account of the career of Antonio Verrio in England", 115, 115, 0, "Descriptive account cited for patronage; exact publication details remain unresolved."),
    ("cand-2759", "Antonio Verrio", 115, 115, 0, "Reuse the indexed artist candidate."),
    ("cand-11018", "patronage in the Restoration period", 115, 115, 0, "Period-specific patronage term; not a separate institution or event."),
    ("cand-1315", "Sir Thomas Isham", 116, 116, 0, "Reuse the indexed person candidate."),
    ("cand-11003", "an exhibition", 116, 116, 0, "Exhibition dedicated to Isham; no title or date is supplied."),
    ("cand-11004", "a useful catalogue", 116, 116, 0, "Catalogue associated with the Isham exhibition; bibliographic details await notes."),
    ("cand-11005", "art of seventeenth-century Florence", 118, 118, 0, "Field of art under reassessment; Florence is also recorded as a nested place mention."),
    ("cand-3397", "Florence", 118, 118, 0, "First Florence mention, within the art-field phrase."),
    ("cand-11019", "exhibitions in New York (1969)", 118, 118, 0, "Descriptive event reference; official title is not supplied."),
    ("cand-7473", "New York", 118, 118, 0, "Place of the 1969 exhibition reference."),
    ("cand-11020", "Florence (1965", 118, 118, 0, "Descriptive event reference; source punctuation continues after the date."),
    ("cand-3397", "Florence", 118, 118, 1, "Place in the exhibition list."),
    ("cand-11021", "1974", 118, 118, 0, "Year is part of the second Florence exhibition reference; no separate title is supplied."),
    ("cand-11022", "London (1979)", 118, 118, 0, "Descriptive event reference; official title is not supplied."),
    ("cand-1422", "London", 118, 118, 0, "Place of the 1979 exhibition reference."),
    ("cand-8078", "Del Rosso brothers", 118, 118, 0, "Reuse the collective candidate; no individual brother is identified here."),
    ("cand-1609", "Grand Prince Ferdinand de’ Medici", 118, 118, 0, "Reuse the indexed person candidate."),
    ("cand-1609", "Prince’s patronage", 119, 119, 0, "Anaphoric reference to Grand Prince Ferdinand de’ Medici."),
    ("cand-11005", "Florentine Seicento art", 119, 119, 0, "Second source phrase for the field of seventeenth-century Florentine art."),
    ("cand-5179", "Medici patrons", 119, 119, 0, "Family-level plural reference; reuse the Medici family candidate."),
    ("cand-1609", "the Prince’s taste", 119, 119, 0, "Anaphoric reference to Grand Prince Ferdinand de’ Medici."),
    ("cand-5520", "Medici court", 119, 119, 0, "Reuse the court/institution candidate; the sentence describes its patronage across two centuries."),
    ("cand-11006", "Artisti alia Corte Granducale", 120, 120, 0, "OCR title spelling is 'alia'; page image reads 'alla'."),
    ("cand-11007", "important catalogue", 120, 120, 0, "Catalogue of the 1969 exhibition, attributed to Marco Chiarini."),
    ("cand-11008", "Marco Chiarini", 120, 120, 0, "Named as the catalogue writer; do not merge with similarly named candidates."),
    ("cand-11010", "an article", 120, 120, 0, "Campbell article cited in footnote 8; title awaits notes/bibliography review."),
    ("cand-11011", "well documented book", 120, 120, 0, "Campbell book cited in footnote 9; title awaits notes/bibliography review."),
    ("cand-11009", "Malcolm Campbell", 120, 120, 0, "Named scholar; do not merge with Colen Campbell before S3."),
    ("cand-0198", "Barberini", 120, 120, 0, "Reuse the Barberini family candidate in the book's patronage context."),
    ("cand-4452", "Sacchetti", 120, 120, 0, "Reuse the Sacchetti family candidate; no individual member is named here."),
    ("cand-1608", "Grand Duke Ferdinand Il’s", 120, 120, 0, "Reuse Ferdinando II de’ Medici; page image reads Roman numeral II, not OCR 'Il'."),
    ("cand-11012", "provincial Florentine artists", 120, 120, 0, "Source-derived group term; no unnamed individuals are created."),
    ("cand-0342", "Pietroda Cortona", 120, 120, 0, "OCR omits spaces; page image reads Pietro da Cortona. Reuse the artist candidate."),
    ("cand-7662", "Palazzo Pitti", 120, 120, 0, "Reuse the architectural-place candidate."),
    ("cand-11014", "catalogue of the exhibition devoted to the collection of Don\nLorenzo de’ Medici", 120, 121, 0, "Borea's catalogue and exhibition are not independently consulted; Don Lorenzo is reused as the person candidate."),
    ("cand-11013", "Evelina Borea", 121, 121, 0, "Named as the catalogue author; identity alignment is deferred to S3."),
    ("cand-1608", "that Grand Duke’s uncle", 121, 121, 0, "The apposition identifies Don Lorenzo as uncle of Ferdinando II; record as a relation candidate, not a formal edge."),
    ("cand-1608", "Ferdinand IDand", 121, 121, 0, "OCR has 'IDand'; page image reads 'II and'."),
    ("cand-1629", "Cardinal Leopoldo", 121, 121, 0, "Reuse the indexed person candidate; the page image reads Ferdinand II and his brother."),
    ("cand-11015", "that provincialism", 121, 121, 0, "Anaphoric characterization of provincial Florentine culture; the sentence continues on p.404."),
    ("cand-11016", "Florentine culture", 121, 121, 0, "Cultural concept in the unfinished sentence; preserve Haskell's attribution and qualification."),
]

line_offsets = {}
cursor = 0
for line_number in range(110, 122):
    line_offsets[line_number] = cursor
    cursor += len(source_lines[line_number - 1]) + 1
mention_ids = {row["mention_id"] for row in mentions}
new_mentions = []
for index, (candidate_id, surface, first_line, last_line, occurrence, note) in enumerate(mention_specs, start=1):
    mention_id = f"m-chp20-p403-{index:03d}"
    if mention_id in mention_ids:
        raise SystemExit(f"mention ID exists: {mention_id}")
    if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["status"] != "open":
        raise SystemExit(f"unavailable mention candidate: {candidate_id}")
    range_start = line_offsets[first_line]
    range_end = line_offsets[last_line] + len(source_lines[last_line - 1])
    position = range_start
    for _ in range(occurrence + 1):
        position = body.find(surface, position, range_end)
        if position < 0:
            raise SystemExit(f"exact source surface not found at L{first_line}-{last_line}: {surface!r}")
        position += len(surface)
    position -= len(surface)
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": P403,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(position),
        "end_char": str(position + len(surface)),
        "note": note,
    })
    mention_ids.add(mention_id)

note_lines = {1: 239, 2: 239, 3: 240, 4: 240, 5: 241, 6: 241, 7: 242, 8: 242, 9: 243, 10: 243}


def make_statement(statement_id, first, last, subject, obj, predicate, claim, speaker, layer, qualification, ids, note_markers=(), relation=False, extra=None):
    qualifiers = {
        "source_line_start": first,
        "source_line_end": last,
        "printed_page": 403,
        "pdf_physical_page": 12,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": ids,
        "relation_candidate": relation,
    }
    if note_markers:
        qualifiers.update({
            "footnote_markers": list(note_markers),
            "footnote_text_pending": True,
            "footnote_segment": NOTES,
            "footnote_refs": [
                {"marker": marker, "segment_id": NOTES, "source_line": note_lines[marker]}
                for marker in note_markers
            ],
            "footnote_statement_ids": [],
            "footnote_body_link_status": "pending",
        })
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": P403,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": "\n".join(source_lines[first - 1:last]),
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "origin": "book",
    }


new_statements = [
    make_statement(
        "st-chp20-p403-alazard-commissioned-franceschini-picture", 111, 113,
        None, "cand-6888", "haskell_reports_commissioned_franceschini_picture",
        "Haskell completes the p.402 reference to Alazard's account of a picture commissioned (through Colbert and Abate Luigi Strozzi) from Baldassare Franceschini, il Volterrano; the Plate 66 title identifies it as Fame Carrying the Name of the King to the Temple of Immortality.",
        "Haskell", "authorial report of a cited account and work identification",
        "The person or institution that commissioned the work is not named in this passage. Colbert and Abate Luigi Strozzi are intermediaries in the wording, not established as commissioners. The OCR title reads 'os the King'; the page image reads 'of the King'. Footnote 1 is linked to the queued notes segment.",
        ["cand-6888", "cand-0800", "cand-2528", "cand-1066", "cand-4186", "cand-1447", "cand-4189", "cand-10995"],
        (), True,
        {"cross_reference_segments": [{"segment_id": P402, "source_line_start": 107, "source_line_end": 108}, {"segment_id": P403, "source_line_start": 111, "source_line_end": 113}, {"segment_id": "chp-20:20_CHP-20Postscript:l69-70", "source_line_start": 69, "source_line_end": 70}],
         "ocr_corrections": [{"source_line": 112, "ocr": "os the King", "print": "of the King", "basis": "CHP-20Postscript.pdf physical page 12 image"}]}
    ),
    make_statement(
        "st-chp20-p403-fame-picture-still-at-versailles", 112, 112,
        "cand-6888", "cand-7287", "reported_location_at_time_of_second_edition",
        "Haskell states that the Fame painting was still at Versailles when this second-edition postscript was written.",
        "Haskell", "authorial report of location",
        "This is a historically situated statement in Haskell's text, not verification of the painting's present location.",
        ["cand-6888", "cand-7287"], relation=True,
        extra={"cross_reference_segments": [{"segment_id": "chp-20:20_CHP-20Postscript:l69-70", "source_line_start": 69, "source_line_end": 70}]}
    ),
    make_statement(
        "st-chp20-p403-rosenberg-identifies-publishes-fame-picture", 112, 113,
        "cand-10995", "cand-6888", "identified_and_published",
        "Haskell reports that Pierre Rosenberg had identified and published the painting.",
        "Haskell", "authorial report of later scholarship",
        "Rosenberg's publication is cited by footnote 1, whose note text remains queued and has not been independently consulted.",
        ["cand-10995", "cand-6888"], [1], True,
        {"cited_material_not_independently_consulted": True}
    ),
    make_statement(
        "st-chp20-p403-lankheit-prince-liechtenstein-research", 114, 114,
        "cand-10997", "cand-10996", "research_on_patronage",
        "Haskell says that Lankheit's research has substantially increased knowledge of a Prince of Liechtenstein among patrons of the Holy Roman Empire interested in Italian art.",
        "Haskell", "authorial report of scholarship",
        "The prince is not personally named, and Lankheit is given by surname only. Footnote 2 remains pending; do not merge either candidate with similarly named candidates before S3.",
        ["cand-10997", "cand-10996", "cand-6994", "cand-4131"], [2], True,
        {"cited_material_not_independently_consulted": True}
    ),
    make_statement(
        "st-chp20-p403-prince-eugene-collecting-research", 114, 114,
        "cand-2384", "cand-2384", "collecting_research_updated",
        "Haskell notes contributions to knowledge of this aspect of Prince Eugene's collecting.",
        "Haskell", "authorial report of scholarship",
        "The source OCR omits the possessive apostrophe in 'Prince Eugens'. Footnote 3 remains pending; the source does not name the contribution in this sentence.",
        ["cand-2384"], [3], True,
        {"cited_material_not_independently_consulted": True,
         "ocr_corrections": [{"source_line": 114, "ocr": "Prince Eugens", "print": "Prince Eugene's", "basis": "CHP-20Postscript.pdf physical page 12 image"}]}
    ),
    make_statement(
        "st-chp20-p403-levey-english-royal-patronage-survey", 115, 115,
        "cand-10999", "cand-10998", "catalogue_surveys_royal_patronage",
        "Haskell says Michael Levey's catalogue of later Italian pictures in the Queen's collection provides a general survey of English royal patronage of Italian painting in the seventeenth and eighteenth centuries.",
        "Haskell", "authorial report of a research resource",
        "The catalogue is cited in footnote 4 but has not been independently consulted; its full bibliographic identity awaits the notes/bibliography pass.",
        ["cand-10999", "cand-11000", "cand-10998", "cand-11017", "cand-2292", "cand-7200"], [4], True,
        {"cited_material_not_independently_consulted": True}
    ),
    make_statement(
        "st-chp20-p403-croft-murray-verrio-restoration-patronage", 115, 115,
        "cand-11001", "cand-2759", "career_account_adds_patronage_knowledge",
        "Haskell says Croft-Murray's detailed and entertaining account of Antonio Verrio's career in England adds substantially to knowledge of patronage in the Restoration period.",
        "Haskell", "authorial report of scholarship",
        "Croft-Murray is surname-only here; footnote 5 remains pending, and the account has not been independently consulted.",
        ["cand-11001", "cand-11002", "cand-2759", "cand-7200", "cand-11018"], [5], True,
        {"cited_material_not_independently_consulted": True}
    ),
    make_statement(
        "st-chp20-p403-isham-exhibition-catalogue", 115, 116,
        "cand-11003", "cand-1315", "subject_of_exhibition_with_catalogue",
        "Haskell says Sir Thomas Isham was the subject of an exhibition for which a useful catalogue exists.",
        "Haskell", "authorial report of an exhibition and catalogue",
        "The catalogue is cited by footnote 6, which remains pending; the exhibition title and date are not supplied here. Preserve the source's period-like punctuation in 'exhibition.of'; the page image does not justify silently changing it to a comma.",
        ["cand-11003", "cand-1315", "cand-11004"], [6], True,
        {"cited_material_not_independently_consulted": True}
    ),
    make_statement(
        "st-chp20-p403-florentine-art-reappraisal-exhibitions", 118, 118,
        "cand-11005", "cand-11019", "field_reappraised_in_light_of_exhibitions",
        "Haskell says seventeenth-century Florentine art had been radically reappraised since 1963 in light of exhibitions in New York in 1969, Florence in 1965 and 1974, and London in 1979; he recognizes that he had underestimated the quality of much of the city's painting while trying to identify the achievements of the Del Rosso brothers and especially Grand Prince Ferdinand de' Medici.",
        "Haskell", "authorial retrospective assessment",
        "The exhibition titles are not given, so event candidates use descriptive labels only. The OCR 'sine' is corrected to 'since'; no exhibition catalogue is claimed to have been consulted.",
        ["cand-11005", "cand-11019", "cand-11020", "cand-11021", "cand-11022", "cand-7473", "cand-3397", "cand-1422", "cand-8078", "cand-1609"], relation=True,
        extra={"ocr_corrections": [{"source_line": 118, "ocr": "sine 1963", "print": "since 1963", "basis": "CHP-20Postscript.pdf physical page 12 image"}]}
    ),
    make_statement(
        "st-chp20-p403-grand-prince-medici-patronage-reassessment", 119, 119,
        "cand-1609", "cand-5179", "new_research_supports_balanced_assessment_of_taste",
        "Haskell maintains that Grand Prince Ferdinand's patronage had exceptional flair and originality, while saying that close study of many Medici patrons now permits a more balanced appreciation of the Prince's taste.",
        "Haskell", "authorial assessment",
        "This records Haskell's evaluation and his account of later scholarship, not an independent assessment of the Prince's taste.",
        ["cand-1609", "cand-5179", "cand-11005"], relation=True
    ),
    make_statement(
        "st-chp20-p403-medici-court-survey-chiarini-catalogue", 119, 120,
        "cand-5520", "cand-11006", "patronage_survey_presented_at_exhibition",
        "Haskell says a general survey of patronage offered by the Medici court in the seventeenth and eighteenth centuries was provided by the 1969 exhibition Artisti alla Corte Granducale, whose important catalogue was written by Marco Chiarini.",
        "Haskell", "authorial report of scholarship and research resource",
        "The OCR title 'Artisti alia' is corrected from the page image to 'Artisti alla'. Footnote 7 remains pending; the catalogue has not been independently consulted.",
        ["cand-5520", "cand-11006", "cand-11007", "cand-11008"], [7], True,
        {"cited_material_not_independently_consulted": True,
         "ocr_corrections": [{"source_line": 120, "ocr": "Artisti alia Corte Granducale", "print": "Artisti alla Corte Granducale", "basis": "CHP-20Postscript.pdf physical page 12 image"}, {"source_line": 119, "ocr": "was-provided b/The exhibition", "print": "was provided by the exhibition", "basis": "CHP-20Postscript.pdf physical page 12 image"}]}
    ),
    make_statement(
        "st-chp20-p403-campbell-ferdinand-ii-palazzo-pitti", 120, 120,
        "cand-11009", "cand-1608", "demonstrated_significance_of_employment_decision",
        "Haskell says Malcolm Campbell demonstrated the significance of Grand Duke Ferdinand II's 1637 decision to break with provincial Florentine artists and employ Pietro da Cortona to decorate Palazzo Pitti; Campbell's book also sheds light on the patronage of the Barberini and the Sacchetti.",
        "Haskell reporting Malcolm Campbell", "authorial report of scholarship",
        "The article and book are cited by footnotes 8 and 9 but are not independently consulted; their full titles await notes/bibliography review. The OCR spellings 'Il', 'Pietroda', and the broken 'was-provided b/The exhibition' are corrected only in the statement using the page image.",
        ["cand-11009", "cand-11010", "cand-11011", "cand-1608", "cand-11012", "cand-0342", "cand-7662", "cand-0198", "cand-4452"], [8, 9], True,
        {"cited_material_not_independently_consulted": True,
         "ocr_corrections": [{"source_line": 120, "ocr": "Ferdinand Il's", "print": "Ferdinand II's", "basis": "CHP-20Postscript.pdf physical page 12 image"}, {"source_line": 120, "ocr": "Pietroda Cortona", "print": "Pietro da Cortona", "basis": "CHP-20Postscript.pdf physical page 12 image"}]}
    ),
    make_statement(
        "st-chp20-p403-borea-don-lorenzo-ferdinand-leopoldo-open", 120, 121,
        "cand-11013", "cand-1630", "catalogue_documents_collection_and_florentine_provincialism_open",
        "Haskell says Evelina Borea's catalogue of an exhibition devoted to Don Lorenzo de' Medici's collection illustrates the provincialism from which Grand Duke Ferdinand II and his brother Cardinal Leopoldo helped rescue Florentine culture.",
        "Haskell reporting Evelina Borea", "authorial report of a scholarly catalogue",
        "The final clause ends with 'an' and continues on p.404; retain this statement as partial. Haskell identifies Don Lorenzo as Ferdinand II's uncle. The kinship and cultural-rescue claims are relationship candidates, not formal relations. Footnote 10 remains pending.",
        ["cand-11013", "cand-11014", "cand-1630", "cand-1608", "cand-1629", "cand-11015", "cand-11016"], [10], True,
        {"cited_material_not_independently_consulted": True,
         "open_across_segment": True,
         "continues_in_segment": P404,
         "cross_reference_segments": [{"segment_id": P404, "source_line_start": 123, "source_line_end": 135}],
         "ocr_corrections": [{"source_line": 121, "ocr": "Ferdinand IDand", "print": "Ferdinand II and", "basis": "CHP-20Postscript.pdf physical page 12 image"}]}
    ),
]

existing_statement_ids = {row["statement_id"] for row in statements}
for statement in new_statements:
    if statement["statement_id"] in existing_statement_ids:
        raise SystemExit(f"statement ID exists: {statement['statement_id']}")
    existing_statement_ids.add(statement["statement_id"])
    if statement["original_quote"] not in "\n".join(source_lines[statement["qualifiers"]["source_line_start"] - 1:statement["qualifiers"]["source_line_end"]]):
        raise SystemExit(f"statement quote mismatch: {statement['statement_id']}")
    for candidate_id in statement["qualifiers"]["mentioned_candidate_ids"]:
        if candidate_id not in candidate_by_id or candidate_by_id[candidate_id]["status"] != "open":
            raise SystemExit(f"statement references unavailable candidate {candidate_id}")

# Replace the vague p.402 object placeholder with the now identified Plate 66 work.
continuation_mention["candidate_id"] = "cand-6888"
continuation_statement["object_candidate_id"] = "cand-6888"
continuation_qualifiers = continuation_statement["qualifiers"]
continuation_qualifiers["claim"] = "Haskell's p.402 sentence about the young Louis XIV looking to Italy continues with Alazard's reference to the Fame painting commissioned through Colbert and Abate Luigi Strozzi from Baldassare Franceschini, il Volterrano. The passage does not name the commissioner."
continuation_qualifiers["qualification"] = "The sentence is closed by p.403. The painting is identified by its Plate 66 title; commissioner remains unspecified. Colbert and Abate Luigi Strozzi are mentioned as intermediaries, not established as commissioners."
continuation_qualifiers["mentioned_candidate_ids"] = [
    "cand-1447", "cand-3461", "cand-7098", "cand-6888", "cand-0800", "cand-2528", "cand-1066"
]
continuation_qualifiers.pop("open_across_segment", None)
continuation_qualifiers.pop("continues_in_segment", None)
continuation_qualifiers["cross_reference_segments"] = [
    {"segment_id": P403, "source_line_start": 111, "source_line_end": 113},
    {"segment_id": "chp-20:20_CHP-20Postscript:l69-70", "source_line_start": 69, "source_line_end": 70},
]

# Delete only the now-resolved placeholder candidate; its only S2 FK is remapped above.
if any(row["candidate_id"] == placeholder_id for row in mentions if row["mention_id"] != continuation_mention_id):
    raise SystemExit("p.402 placeholder has unexpected additional mention references")
if any(
    placeholder_id in row.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    for row in statements if row["statement_id"] != continuation_statement_id
):
    raise SystemExit("p.402 placeholder has unexpected additional statement references")
candidates = [row for row in candidates if row["candidate_id"] != placeholder_id]
candidate_by_id.pop(placeholder_id)

all_mentions = mentions + new_mentions
for segment_id in (P402, P403):
    spans = sorted(
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
        for row in all_mentions if row["segment_id"] == segment_id
    )
    for index, left in enumerate(spans):
        for right in spans[index + 1:]:
            if right[0] >= left[1]:
                break
            nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
            if left[:2] == right[:2] or not nested:
                raise SystemExit(f"crossing or duplicate mention spans: {left[2]} / {right[2]}")

coverage_by_id[P402]["disposition"] = "reviewed"
coverage_by_id[P402]["migration_status"] = "complete"
coverage_by_id[P402]["source_line_ranges"] = "L99-108"
coverage_by_id[P402]["note"] = "Printed p.402 (PDF physical page 11) complete; the Alazard commissioned-picture sentence closes on p.403 with the Plate 66 work identified. Footnotes 1-7 link to the queued notes segment L235-238."
coverage_by_id[P403]["disposition"] = "reviewed"
coverage_by_id[P403]["migration_status"] = "partial"
coverage_by_id[P403]["source_line_ranges"] = "L110-121"
coverage_by_id[P403]["note"] = "Printed p.403 (PDF physical page 12) checked against the page image. Closes p.402 sentence; records postscript scholarship and chapter 8 reassessment. Final Borea sentence continues to p.404 L123-135; footnotes 1-10 link to queued notes L239-243."

paths = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP) for path in paths]
if ARGS.apply:
    if any(path.exists() for path in backups):
        raise SystemExit("p.403 recovery backup already exists")
    for path, backup in zip(paths, backups):
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, all_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, coverage)
    print(f"applied p.403 S2 migration; backup suffix {BACKUP}")
else:
    print("DRY RUN: no files written")
    print(f"new candidates={len(candidate_specs)}; new mentions={len(new_mentions)}; new statements={len(new_statements)}")
    print("p.402 continuation remapped to cand-6888; placeholder cand-10994 removed")
    print("source/PDF/S0 hashes, candidate FKs, exact mention spans, statement anchors, notes links, and p.404 continuation validated")
