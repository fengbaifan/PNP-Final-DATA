"""Controlled S2 migration for Chapter 8 printed page 226 and note 1."""
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
P225 = "chp-8:08_CHP-8_sec_ii:l163-177"
P226 = "chp-8:08_CHP-8_sec_ii:l179-188"
P227 = "chp-8:08_CHP-8_sec_ii:l190-204"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
TARGET_IDS = {P225, P226, P227, NOTES}
BACKUP_SUFFIX = ".bak-s2-chp8-p226-20261001"


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
    P225: ("reviewed", "partial", "L163-177"),
    P226: ("queued", "pending", ""),
}
for segment_id, state in expected.items():
    row = coverage_by_id.get(segment_id)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage state for {segment_id}: {row}")
if coverage_by_id[NOTES]["source_line_ranges"] != "L373-398":
    raise SystemExit("footnote coverage changed; inspect before proceeding")
if any(row["segment_id"] == P226 for row in mention_rows + statement_rows):
    raise SystemExit("p.226 rows already exist; inspect before rerunning")

new_candidates = [
    ("cand-7784", "Stefano Conti's collection of ninety-seven pictures", "", 181,
     "A distinct collection referent described as 97 mostly small pictures; no collection entity type exists, so leave type unresolved."),
    ("cand-7785", "Stefano Conti's private picture gallery", "place", 183,
     "Purpose-built, well-lit gallery; the source does not name its building or architect."),
    ("cand-7786", "Stefano Conti's will (date and repository unspecified)", "archive", 183,
     "Named as one of the documents Haskell used; date, repository and text are not supplied here."),
    ("cand-7787", "Stefano Conti's picture-commission and payment requirements", "procedure", 184,
     "Reported operating practice covering prices, originality, dimensions and written subject/date guarantees."),
    ("cand-7788", "Marchesini's regular written reporting to Stefano Conti", "procedure", 187,
     "A reported communication practice; the text does not establish that specific letters survive."),
    ("cand-7789", "The school of Carlo Cignani in Bologna", "", 186,
     "Haskell calls it a school; whether this denotes a formal institution, workshop or artistic milieu remains undecided."),
    ("cand-7790", "Unidentified Haskell publication from 1956 on Stefano Conti", "archive", 399,
     "Section note cites Haskell, 1956 and says it supplies manuscript references; title and edition are not given."),
    ("cand-7791", "Unidentified father of Stefano Conti", "person", 183,
     "Unnamed individual identified only as Conti's father; no independent identity is inferred."),
    ("cand-7792", "Unidentified wife of Stefano Conti", "person", 183,
     "Unnamed individual identified only through the marriage and survival statement."),
    ("cand-7793", "Unnamed only son of Stefano Conti", "person", 183,
     "Unnamed individual identified only as Conti's only son; no name or other biography is inferred."),
    ("cand-7794", "Unidentified local architect employed by Stefano Conti", "person", 183,
     "The passage reports a local architect's work on the gallery but supplies no name or further identity."),
    ("cand-7795", "Lucchese nobility as a social estate", "term", 183,
     "The phrase denotes a social status into which Conti's father was accepted; it is not treated as a family or institution."),
    ("cand-7796", "Other unspecified documents concerning Stefano Conti", "archive", 183,
     "Haskell mentions documents beyond Conti's will as evidence of his business acumen but does not identify them."),
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
    anchor_segment = NOTES if line == 399 else P226
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


# Page 226: close the prior comparison, then preserve each distinct Conti claim and referent.
mention(P226, 180, "m-chp8-p226-apartments", "cand-7731", "apartments", "Private rooms in Raimondo Buonaccorsi's palace; cross-page continuation from p.225.")
mention(P226, 180, "m-chp8-p226-intimate-pictures", "cand-7779", "smaller and more intimate pictures", "The private-apartment pictures in the open p.225 comparison; no works are identified.")
mention(P226, 181, "m-chp8-p226-stefano-1", "cand-0833", "Stefano Conti", "Reuse the index candidate covering p.226.")
mention(P226, 181, "m-chp8-p226-collection-1", "cand-7784", "contemporary collection", "Stefano Conti's collection of 97 mostly small pictures.")
mention(P226, 181, "m-chp8-p226-lucca-1", "cand-1454", "Lucca", "Conti's city and birthplace.")
mention(P226, 181, "m-chp8-p226-picture-count", "cand-7784", "ninety-seven pictures", "Reported collection size; most works were small.")
mention(P226, 181, "m-chp8-p226-birthplace", "cand-1454", "his birthplace", "Coreference to Lucca.")
mention(P226, 181, "m-chp8-p226-bologna-1", "cand-3398", "Bologna", "City to which Conti looked for pictures.")
mention(P226, 181, "m-chp8-p226-venice-1", "cand-3401", "Venice", "City to which Conti looked for pictures.")
mention(P226, 182, "m-chp8-p226-conti-pronoun", "cand-0833", "lie", "OCR reads 'lie'; page image reads 'he', coreferential to Stefano Conti.")
mention(P226, 182, "m-chp8-p226-crespi", "cand-0871", "Crespi", "Reuse Giuseppe Maria Crespi's index candidate.")
mention(P226, 182, "m-chp8-p226-ricci", "cand-2154", "Sebastiano Ricci", "Reuse Sebastiano Ricci's index candidate.")
mention(P226, 182, "m-chp8-p226-canaletto", "cand-0498", "Canaletto", "Reuse Canaletto's index candidate.")
mention(P226, 183, "m-chp8-p226-conti-2", "cand-0833", "Conti", "Subject of the biographical statements.")
mention(P226, 183, "m-chp8-p226-father", "cand-7791", "a father", "Unnamed father; no identity beyond the relationship is supplied.")
mention(P226, 183, "m-chp8-p226-lucchese-nobility", "cand-7795", "Lucchese nobility", "Social estate, not an institution or family.")
mention(P226, 183, "m-chp8-p226-will-1", "cand-7786", "his will", "Conti's named but undated will; archive identity unresolved.")
mention(P226, 183, "m-chp8-p226-other-documents", "cand-7796", "other documents", "Unspecified documentary sources mentioned with the will.")
mention(P226, 183, "m-chp8-p226-wife", "cand-7792", "his wife", "Unnamed spouse; no name is inferred.")
mention(P226, 183, "m-chp8-p226-son", "cand-7793", "only son", "Unnamed son; no name is inferred.")
mention(P226, 183, "m-chp8-p226-venice-2", "cand-3401", "Venice", "Destination of Conti's late-1704 journey.")
mention(P226, 183, "m-chp8-p226-bologna-2", "cand-3398", "Bologna", "Destination of Conti's late-1704 journey.")
mention(P226, 183, "m-chp8-p226-collection-2", "cand-7784", "a number of pictures", "Paintings acquired during the subsequent three years.")
mention(P226, 183, "m-chp8-p226-architect", "cand-7794", "a local architect", "Unnamed architect employed to construct the gallery.")
mention(P226, 183, "m-chp8-p226-gallery", "cand-7785", "a well-lit gallery", "Purpose-built picture gallery; exact location is not stated in this sentence.")
mention(P226, 183, "m-chp8-p226-collection-3", "cand-7784", "the right number of pictures", "Collection display count, as characterized by Haskell.")
mention(P226, 183, "m-chp8-p226-will-2", "cand-7786", "his will", "Second reference to Conti's will in the same source line.", occurrence=1)
mention(P226, 183, "m-chp8-p226-collection-4", "cand-7784", "the collection", "Coreference to Stefano Conti's picture collection.")
mention(P226, 184, "m-chp8-p226-conti-3", "cand-0833", "He", "Coreference to Stefano Conti.")
mention(P226, 184, "m-chp8-p226-procedure-1", "cand-7787", "dealings with the painters themselves", "Conti's reported commissioning and payment requirements.")
mention(P226, 184, "m-chp8-p226-patron", "cand-0833", "a generous patron", "Haskell's characterization of Conti's patronage.")
mention(P226, 184, "m-chp8-p226-procedure-2", "cand-7787", "each work should be an originals", "OCR reads 'originals'; the page image reads 'an original'.")
mention(P226, 184, "m-chp8-p226-procedure-3", "cand-7787", "specified sizes", "Required dimensions for commissioned pictures.")
mention(P226, 184, "m-chp8-p226-guarantee", "cand-7787", "written guarantee", "Required written statement of a work's exact subject and date.")
mention(P226, 185, "m-chp8-p226-venice-3", "cand-3401", "Venice", "City visited by Conti and revisited later.")
mention(P226, 185, "m-chp8-p226-bologna-3", "cand-3398", "Bologna", "City visited by Conti and revisited later.")
mention(P226, 185, "m-chp8-p226-conti-4", "cand-0833", "Stefano Conti", "Patron commissioning works at artists' studios.")
mention(P226, 185, "m-chp8-p226-first-commissions", "cand-7787", "first commissions", "Initial commissions drawn up at artists' studios.")
mention(P226, 185, "m-chp8-p226-veronese-painter", "cand-1540", "a Veronese painter", "Description of Alessandro Marchesini, named on the next line.")
mention(P226, 186, "m-chp8-p226-marchesini", "cand-1540", "Alessandro Marchesini", "Reuse the p.226 index subentry for work for Stefano Conti.")
mention(P226, 186, "m-chp8-p226-collection-5", "cand-7784", "a number of pictures", "Works immediately ordered from Marchesini; no titles are supplied.")
mention(P226, 186, "m-chp8-p226-agent", "cand-1540", "his agent", "Marchesini's role for Conti.")
mention(P226, 186, "m-chp8-p226-venice-4", "cand-3401", "Venice", "Marchesini's stated residence.")
mention(P226, 186, "m-chp8-p226-school", "cand-7789", "the school of Carlo Cignani", "The text does not establish a formal institutional status.")
mention(P226, 186, "m-chp8-p226-cignani", "cand-0748", "Carlo Cignani", "Reuse Cignani's index candidate.")
mention(P226, 187, "m-chp8-p226-bologna-4", "cand-3398", "Bologna", "City locating Cignani's school.")
mention(P226, 187, "m-chp8-p226-school-2", "cand-7789", "which", "Coreference to Cignani's school; OCR 'siom' is corrected against the page image.")
mention(P226, 187, "m-chp8-p226-bologna-5", "cand-3398", "the city", "Coreference to Bologna.")
mention(P226, 187, "m-chp8-p226-agent-work", "cand-1540", "his job", "Marchesini's agency work for Conti.")
mention(P226, 187, "m-chp8-p226-conti-5", "cand-0833", "his patron", "Coreference to Stefano Conti.")
mention(P226, 187, "m-chp8-p226-correspondence", "cand-7788", "writing regularly to his patron", "Reported written-reporting practice from Marchesini to Conti; no surviving letter is identified.")
mention(P226, 187, "m-chp8-p226-advance-payments", "cand-7787", "the advance payments", "Payments administered by Marchesini; recipients are not named.")
mention(P226, 187, "m-chp8-p226-new-artists", "cand-7787", "suggesting new artists", "One reported part of Marchesini's agency work.")
mention(P226, 187, "m-chp8-p226-established-masters", "cand-7787", "alterations in the work of established masters", "Marchesini proposed alterations; the artists and works are not identified.")
mention(P226, 188, "m-chp8-p226-conti-6", "cand-0833", "Conti", "Subject of the per-figure payment practice.")
mention(P226, 188, "m-chp8-p226-procedure-4", "cand-7787", "pay his artists according to the number of figures", "Sentence continues on p.227; recipients and full terms remain open.")

mention(NOTES, 399, "m-chp8-p226-n1-haskell-publication", "cand-7790", "Haskell, 1956", "Unidentified publication cited as the general source for the section.")
mention(NOTES, 399, "m-chp8-p226-n1-haskell-author", "cand-3770", "Haskell", "Author mention nested within the Haskell, 1956 citation.")
mention(NOTES, 399, "m-chp8-p226-n1-lucca", "cand-1454", "Lucca", "City whose libraries and archives contain referenced manuscripts.")


def quote(segment_id: str, first: int, last: int) -> str:
    return "\n".join(source_lines[first - 1:last])


def make_statement(statement_id, segment_id, first_line, last_line, subject, obj, predicate,
                   claim, qualification, mentioned, text_layer="body", extras=None):
    if segment_id not in segment_by_id or first_line < segment_by_id[segment_id]["line_start"] or last_line > segment_by_id[segment_id]["line_end"]:
        raise SystemExit(f"statement lines outside segment: {statement_id}")
    if any(candidate_id not in candidate_ids for candidate_id in [subject, obj, *mentioned] if candidate_id):
        raise SystemExit(f"statement references missing candidate: {statement_id}")
    qualifiers = {
        "source_line_start": first_line, "source_line_end": last_line,
        "printed_page": 226, "pdf_physical_page": 28,
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


ocr = [
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 182, "ocr": "lie managed", "print": "he managed", "basis": "CHP-8.pdf physical page 28."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 183, "ocr": "Conti_was", "print": "Conti was", "basis": "CHP-8.pdf physical page 28."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 183, "ocr": "cloth,,", "print": "cloth, and", "basis": "CHP-8.pdf physical page 28."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 183, "ocr": "siom", "print": "from", "basis": "CHP-8.pdf physical page 28."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 183, "ocr": "silled", "print": "filled", "basis": "CHP-8.pdf physical page 28."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 187, "ocr": "siom", "print": "from", "basis": "CHP-8.pdf physical page 28."},
    {"source_file": SOURCE.relative_to(ROOT).as_posix(), "source_line": 184, "ocr": "originals", "print": "original", "basis": "CHP-8.pdf physical page 28."},
]


new_statements = [
    make_statement("st-chp8-p226-enlightenment-private-apartments-close", P226, 180, 180, "cand-0467", "cand-0974",
                   "author_infers_private_apartments_contained_intimate_modern_pictures",
                   "Haskell completes the p.225 contrast: Raimondo's private apartments were filled with smaller, more intimate pictures that betrayed a wholly new range of sensibility.",
                   "This closes the open cross-page inference; it remains Haskell's interpretation of the collection.",
                   ["cand-0467", "cand-0974", "cand-7731", "cand-7779", "cand-7765"],
                   extras={"continued_from_segment_id": P225, "continued_from_statement_id": "st-chp8-p225-enlightenment-patron-inference-open", "continuation_status": "closed"}),
    make_statement("st-chp8-p226-conti-collection-compared-to-buonaccorsi", P226, 181, 181, "cand-7784", "cand-7765",
                   "author_compares_collection_conflict",
                   "Haskell presents Stefano Conti's contemporary collection as showing a somewhat similar conflict to Raimondo Buonaccorsi's collection.",
                   "The comparison is Haskell's art-historical framing; the two collections remain distinct objects.",
                   ["cand-7784", "cand-0833", "cand-7765"], extras={"speaker_judgment": True}),
    make_statement("st-chp8-p226-conti-collection-size-and-origin", P226, 181, 181, "cand-0833", "cand-7784",
                   "owned_collection_of_97_mostly_small_pictures",
                   "Haskell says Conti owned 97 pictures, mostly small in dimension, in his contemporary collection.",
                   "The count and scale are reported by Haskell; no item-level inventory is supplied here.",
                   ["cand-0833", "cand-7784", "cand-1454"], extras={"quantity": 97, "relation_candidate": True}),
    make_statement("st-chp8-p226-conti-looks-outside-lucca", P226, 181, 182, "cand-0833", "cand-7784",
                   "collection_drawn_from_bologna_and_venice",
                   "Haskell says the very nature of Conti's birthplace forced him to look far outside his native province; he confined himself to Bologna and Venice, partly by chance and partly by design.",
                   "The text names the two cities but not the province's modern boundaries; the mix of chance and design is retained.",
                   ["cand-0833", "cand-1454", "cand-3398", "cand-3401", "cand-7784"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p226-conti-acquires-leading-painters", P226, 182, 182, "cand-0833", "cand-7784",
                   "acquired_pictures_by_crespi_ricci_canaletto_and_others",
                   "Haskell reports that Conti acquired pictures by Crespi, Sebastiano Ricci, Canaletto and other leading eighteenth-century painters.",
                   "Only the named painters are identified; the other artists and individual pictures are unspecified.",
                   ["cand-0833", "cand-7784", "cand-0871", "cand-2154", "cand-0498"], extras={"relation_candidate": True, "ocr_corrections": [ocr[0]]}),
    make_statement("st-chp8-p226-conti-birth", P226, 183, 183, "cand-0833", None,
                   "born_1654",
                   "Conti was born in 1654.",
                   "The date is reported by Haskell.",
                   ["cand-0833"]),
    make_statement("st-chp8-p226-father-entered-lucchese-nobility", P226, 183, 183, "cand-7791", "cand-7795",
                   "accepted_into_nobility_about_a_quarter_century_before_contis_birth",
                   "Haskell says Conti's father had been accepted into the Lucchese nobility about a quarter-century before Conti's 1654 birth.",
                   "The father is unnamed and the admission year is not exact; the relative chronology implies approximately 1629, not a documented date.",
                   ["cand-0833", "cand-7791", "cand-7795", "cand-1454"], extras={"approximate_year_inferred_from_relative_phrase": "c.1629", "relation_candidate": True}),
    make_statement("st-chp8-p226-conti-business-and-documents", P226, 183, 183, "cand-0833", "cand-7796",
                   "traded_in_silk_and_cloth_and_described_as_acute_businessman",
                   "Conti carried on a flourishing trade in silk and cloth; Haskell says his will and other documents show him to have been an acute businessman.",
                   "This is Haskell's characterization based on documents not independently consulted here.",
                   ["cand-0833", "cand-7786", "cand-7796"], extras={"speaker_judgment": True, "ocr_corrections": [ocr[1], ocr[2], ocr[3]]}),
    make_statement("st-chp8-p226-conti-marriage-and-death", P226, 183, 183, "cand-0833", "cand-7792",
                   "married_1685_outlived_wife_and_only_son_died_1739_age_85",
                   "Haskell says Conti married in 1685, outlived both his wife and only son, and died in 1739 aged 85.",
                   "The wife and son's identities are not supplied; the reported age and dates are preserved as stated.",
                   ["cand-0833", "cand-7792", "cand-7793"], extras={"dates": [1685, 1739], "reported_age": 85, "relation_candidate": True}),
    make_statement("st-chp8-p226-conti-collection-period", P226, 183, 183, "cand-0833", "cand-7784",
                   "began_collecting_late_1704_and_acquired_for_three_years",
                   "Conti began collecting suddenly at the end of 1704 after a journey to Venice and Bologna, then acquired pictures methodically in both cities for the next three years.",
                   "Haskell describes his spirit as purposeful and not carried away by undue enthusiasm; this is an authorial characterization.",
                   ["cand-0833", "cand-7784", "cand-3401", "cand-3398"], extras={"date_start": "1704-12 (approx.)", "duration_years": 3, "speaker_judgment": True}),
    make_statement("st-chp8-p226-conti-gallery-and-preservation", P226, 183, 183, "cand-0833", "cand-7784",
                   "built_gallery_refused_sale_and_willed_collection_preserved",
                   "Conti employed a local architect to build a well-lit gallery, filled it with the intended number of pictures, refused to sell when pressed, and tried through his will to preserve the collection as a whole.",
                   "The architect is unnamed; Haskell says the will tried to secure preservation, not that it succeeded.",
                   ["cand-0833", "cand-7794", "cand-7785", "cand-7784", "cand-7786"], extras={"relation_candidate": True, "ocr_corrections": [ocr[4]]}),
    make_statement("st-chp8-p226-conti-price-policy", P226, 184, 184, "cand-0833", "cand-7787",
                   "refused_to_pay_above_personal_valuation",
                   "Haskell characterizes Conti as a generous patron who nevertheless refused to pay more than he thought a picture was worth.",
                   "This reports Conti's stated purchasing practice, not an independently reconstructed price schedule.",
                   ["cand-0833", "cand-7787"], extras={"speaker_judgment": True}),
    make_statement("st-chp8-p226-conti-original-works-only", P226, 184, 184, "cand-0833", "cand-7787",
                   "required_originals_painted_for_him_not_copies",
                   "Conti insisted that each work be an original painted for him alone, not a copy.",
                   "The printed page reads 'an original'; source OCR pluralizes 'originals'. The requirement is reported by Haskell.",
                   ["cand-0833", "cand-7787", "cand-7784"], extras={"relation_candidate": True, "ocr_corrections": [ocr[6]]}),
    make_statement("st-chp8-p226-conti-subject-size-and-guarantees", P226, 184, 184, "cand-0833", "cand-7787",
                   "allowed_subject_choice_but_required_sizes_and_written_guarantees",
                   "Conti allowed artists freedom to choose subjects but required specified picture sizes and a written guarantee certifying each work's exact subject and date.",
                   "The guarantee requirement is a reported general practice; no individual guarantee document is identified.",
                   ["cand-0833", "cand-7787"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p226-conti-visits-studios-and-commissions", P226, 185, 186, "cand-0833", "cand-1540",
                   "visited_studios_commissioned_pictures_and_appointed_marchesini_agent",
                   "During visits to Venice and Bologna, Conti went to artists' studios and drew up his first commissions; he contacted Alessandro Marchesini, ordered a number of pictures from him and appointed him agent.",
                   "The pictures are untitled and not counted; the agent role is a book-based relation candidate, not a formal edge yet.",
                   ["cand-0833", "cand-3401", "cand-3398", "cand-1540", "cand-7784"], extras={"relation_candidate": True}),
    make_statement("st-chp8-p226-marchesini-profile-and-cignani-school", P226, 186, 187, "cand-1540", "cand-7789",
                   "veronese_painter_lived_venice_studied_cignani_school_bologna",
                   "Marchesini is described as a Veronese painter living in Venice who had studied in Carlo Cignani's school in Bologna; Haskell says that school produced the city's leading artists.",
                   "The school's organizational status and the scope of Haskell's generalization remain unresolved.",
                   ["cand-1540", "cand-0748", "cand-7789", "cand-3401", "cand-3398"], extras={"speaker_judgment": True, "ocr_corrections": [ocr[5]]}),
    make_statement("st-chp8-p226-marchesini-agent-work", P226, 187, 187, "cand-1540", "cand-0833",
                   "agent_followed_delays_corresponded_disbursed_advances_and_advised",
                   "Haskell says Marchesini pressed artists who delayed, wrote regularly to Conti, handed out advance payments, suggested new artists and proposed changes to established masters' work.",
                   "Recipients, letters, pictures and proposed changes are not individually identified; Marchesini's effectiveness is Haskell's assessment.",
                   ["cand-1540", "cand-0833", "cand-7788", "cand-7787"], extras={"relation_candidate": True, "speaker_judgment": True}),
    make_statement("st-chp8-p226-conti-per-figure-payment-open", P226, 188, 188, "cand-0833", "cand-7787",
                   "paid_artists_according_to_number_of_figures_open_continuation",
                   "Haskell begins a statement that Conti tended to pay artists according to the number of figures in each picture.",
                   "The sentence ends with a comma and continues on p.227 L190; do not infer the complete pricing rule yet.",
                   ["cand-0833", "cand-7787"], extras={"relation_candidate": True, "continuation_status": "open", "continuation_to_segment_id": P227, "continuation_to_source_line": 190}),
    make_statement("st-chp8-p226-n1-haskell-1956-reference", NOTES, 399, 399, "cand-3770", "cand-7790",
                   "section_note_cites_general_source_for_lucca_manuscript_references",
                   "Footnote 1 directs readers to Haskell, 1956 for the section and says it gives full references to manuscript sources in Lucca libraries and archives.",
                   "The publication title and edition are not supplied in this note and have not been independently identified.",
                   ["cand-3770", "cand-7790", "cand-1454"], text_layer="footnote citation", extras={"relation_candidate": False}),
]

if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("existing duplicate statement IDs")
statement_ids = {row["statement_id"] for row in statement_rows}
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("new statement ID already exists")
prior_id = "st-chp8-p225-enlightenment-patron-inference-open"
prior = next((row for row in statement_rows if row["statement_id"] == prior_id), None)
if not prior or prior["qualifiers"].get("continuation_status") != "open":
    raise SystemExit("expected open p.225 Enlightenment inference not found")
patched_prior = json.loads(json.dumps(prior))
patched_prior["qualifiers"].update({
    "continuation_status": "closed", "continued_to_segment_id": P226,
    "continued_to_source_line": 180,
    "continuation_closed_by_statement_id": "st-chp8-p226-enlightenment-private-apartments-close",
})

new_coverage = []
for row in coverage_rows:
    sid = row["segment_id"]
    if sid == P225:
        row.update({"disposition": "reviewed", "migration_status": "complete",
                    "source_line_ranges": "L163-177", "note": "p.225 final comparison closes at p.226 L180."})
    elif sid == P226:
        row.update({"disposition": "reviewed", "migration_status": "partial",
                    "source_line_ranges": "L179-188", "note": "p.226 read against CHP-8.pdf physical page 28; final pricing sentence continues at p.227 L190."})
    elif sid == NOTES:
        row.update({"source_line_ranges": "L373-399", "migration_status": "partial",
                    "note": "p.225 notes through L398 and p.226 note 1 at L399 migrated; later consolidated notes remain queued by printed page."})
    new_coverage.append(row)

preview = {
    "mode": "dry-run", "candidate_additions": len(new_candidates),
    "mention_additions": len(new_mentions), "statement_additions": len(new_statements),
    "statement_ids": [row["statement_id"] for row in new_statements],
    "continuations": [
        {"statement_id": prior_id, "status": "closed", "to": P226, "line": 180},
        {"statement_id": "st-chp8-p226-conti-per-figure-payment-open", "status": "open", "to": P227, "line": 190},
    ],
    "coverage_updates": {
        P225: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L163-177"},
        P226: {"disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L179-188"},
        NOTES: {"source_line_ranges": "L373-399", "migration_status": "partial"},
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
