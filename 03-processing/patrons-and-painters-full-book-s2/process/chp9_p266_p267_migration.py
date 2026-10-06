"""Controlled S2 migration for chapter 9 printed pp.266-267; defaults to dry run."""
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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_266 = "chp-9:09_CHP-9_intro:l303-311"
SEGMENT_267 = "chp-9:09_CHP-9_intro:l313-321"
NOTE_SEGMENT = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_SEGMENT_SHA = {
    SEGMENT_266: "6153ee105244f9e9bf25cd7cfbffef26cd195c6648061760e56bd83c9de98270",
    SEGMENT_267: "3b6bb69ba75dac969f2059036fd7dd45a1a67b771e41ba507f85bd982dc70080",
}
EXPECTED_ASSET_SHA = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p266-p267-20261001"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"

source_bytes = SOURCE.read_bytes()
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
segments = {r["segment_id"]: r for r in read_jsonl(segment_path)}
if hashlib.sha256(source_bytes).hexdigest() != EXPECTED_ASSET_SHA:
    raise SystemExit("chapter 9 source asset has changed")
for sid, expected in EXPECTED_SEGMENT_SHA.items():
    if sid not in segments or segments[sid].get("sha256") != expected:
        raise SystemExit(f"S0 segment is missing or changed: {sid}")
    if segments[sid].get("asset_sha256") != EXPECTED_ASSET_SHA:
        raise SystemExit(f"S0 segment source fingerprint mismatch: {sid}")

SEGMENT_BOUNDS = {SEGMENT_266: (303, 311), SEGMENT_267: (313, 321)}
SEGMENT_TEXT = {sid: "\n".join(source_lines[a - 1:b]) for sid, (a, b) in SEGMENT_BOUNDS.items()}
LINE_OFFSETS = {}
for sid, (first, last) in SEGMENT_BOUNDS.items():
    offset = 0
    for line_no in range(first, last + 1):
        LINE_OFFSETS[(sid, line_no)] = offset
        offset += len(source_lines[line_no - 1]) + 1

candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_ids = {r["candidate_id"] for r in candidates}
mention_ids = {r["mention_id"] for r in mentions}
statement_ids = {r["statement_id"] for r in statements}
coverage_by_id = {r["segment_id"]: r for r in coverage}

for sid in (SEGMENT_266, SEGMENT_267):
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != ("queued", "pending", ""):
        raise SystemExit(f"unexpected coverage state for {sid}: {row}")
notes_cov = coverage_by_id.get(NOTE_SEGMENT)
if not notes_cov or (notes_cov["disposition"], notes_cov["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit(f"unexpected consolidated-notes coverage state: {notes_cov}")

NEW_CANDIDATES = [
    ("cand-8622", "King of Saxony (unidentified; intended recipient of Sagredo's Castiglione volumes)", "person", "Haskell says Francesco Algarotti wanted to buy Sagredo's volumes for the King of Saxony; the source gives no personal name or exact date, so do not identify the monarch at S2.", 309),
    ("cand-8623", "Elector Palatine (unidentified; recipient of two paintings from the Mantuan market)", "person", "Haskell says Rosalba Carriera bought two pictures for the Elector Palatine; no personal name or exact date is supplied, so identity remains open.", 320),
    ("cand-8624", "Unidentified posthumous inventories of Zaccaria Sagredo's collection (eighteenth century)", "archive", "Haskell refers to inventories drawn up some years after Sagredo's death; individual records, repositories and dates are not identified. Keep these distinct from the specifically dated 1743 first inventory candidate.", 305),
    ("cand-8625", "One hundred pen-and-ink views commissioned by Zaccaria Sagredo from Andrea Torresani", "work", "Haskell reports through Moschini that Sagredo commissioned 100 views; the printed page reads 100, while S0 OCR reads 'too'. Individual sheets are not identified.", 305),
    ("cand-8626", "Unidentified drawings by Lazzarini bought by Zaccaria Sagredo", "work", "Haskell reports that Sagredo bought all the rare and very correct Lazzarini drawings; titles, count and date are not supplied. The surname-only source mention is not independently aligned to a person at S2.", 306),
    ("cand-8627", "Unidentified drawings by Gaspare Diziani bound by Zaccaria Sagredo in one volume", "work", "Haskell reports that Sagredo bound all Diziani drawings into a volume; individual titles and count are not supplied.", 306),
    ("cand-8628", "Unidentified monotype by Giovanni Benedetto Castiglione owned by Giambattista Tiepolo", "work", "Haskell says Tiepolo owned a monotype by Castiglione; no title, present location or independent object verification is supplied.", 314),
    ("cand-8629", "Unidentified etchings by Giambattista Tiepolo in which Haskell sees Castiglione's influence", "work", "Haskell interprets the subject matter and technique of Tiepolo's etchings as showing study of Castiglione; the prints are not individually identified.", 314),
    ("cand-8630", "Twelve engravings made by A. M. Zanetti the Elder after Castiglione drawings (1759)", "work", "Haskell reports that Zanetti engraved twelve drawings in 1759; titles and present locations are not supplied. Footnote 8 directs readers to a later chapter.", 311),
    ("cand-8631", "More than nine hundred pictures sent from Mantuan ducal collections to Ferdinando Carlo Gonzaga", "work", "Haskell reports a group of over 900 pictures sent to Ferdinando Carlo and later distributed among his courtiers; no individual works or sending agent are identified.", 318),
    ("cand-8632", "Several paintings by Giovanni Benedetto Castiglione in Field Marshal Schulenburg's Mantuan-market purchase", "work", "Haskell says Schulenburg bought a large batch from the Mantuan market including several Castiglione pictures; individual paintings are not identified. The source distinguishes pictures from Sagredo's drawings.", 321),
    ("cand-8633", "Unidentified fine sheets by Raphael included in Sagredo's purchase of Carracci drawings", "work", "Haskell says the purchase included fine sheets by Raphael; no sheet is titled or individually described in this passage.", 308),
    ("cand-8634", "Two unidentified pictures bought by Rosalba Carriera for the Elector Palatine from the Mantuan market", "work", "Haskell says Carriera bought two pictures for the Elector Palatine among works from Mantua; no titles, exact date or recipient identity are supplied.", 320),
    ("cand-8635", "Unidentified drawing volumes listed in posthumous inventories of Zaccaria Sagredo's collection", "work", "Haskell says inventories compiled some years after Sagredo's death listed many volumes of drawings. Some complete volumes were later bought by Joseph Smith and were reported to survive in the Royal Collection; individual volumes are not identified.", 305),
    ("cand-8636", "Extensive set of unidentified drawings by Giovanni Benedetto Castiglione collected by Zaccaria Sagredo", "work", "Haskell describes a large, carefully chosen set collected by Sagredo and later admired; individual sheets and exact volume boundaries are not identified.", 309),
    ("cand-8637", "Additional unidentified Castiglione drawings given by Francesco Algarotti to Joseph Smith", "work", "Haskell says Smith received a large number of additional Castiglione drawings from Algarotti; individual sheets, date and location are not supplied.", 310),
]
for cid, name, *_ in NEW_CANDIDATES:
    if cid in candidate_ids:
        raise SystemExit(f"candidate ID already exists: {cid}")
    if any(c["canonical_name"] == name for c in candidates):
        raise SystemExit(f"candidate natural key already exists: {name}")

new_candidates = []
for cid, name, kind, detail, line_no in NEW_CANDIDATES:
    sid = SEGMENT_266 if line_no <= 311 else SEGMENT_267
    new_candidates.append({
        "candidate_id": cid,
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
        "candidate_source_ref": f"{sid}#L{line_no}",
    })
candidate_ids |= {r["candidate_id"] for r in new_candidates}

new_mentions = []


def add_mention(mention_id, sid, line_no, candidate_id, surface, note, occurrence=0):
    if mention_id in mention_ids or any(r["mention_id"] == mention_id for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    line = source_lines[line_no - 1]
    starts = []
    cursor = 0
    while True:
        found = line.find(surface, cursor)
        if found < 0:
            break
        starts.append(found)
        cursor = found + 1
    if occurrence >= len(starts):
        raise SystemExit(f"surface occurrence not found on L{line_no}: {surface!r}")
    start = LINE_OFFSETS[(sid, line_no)] + starts[occurrence]
    if SEGMENT_TEXT[sid][start:start + len(surface)] != surface:
        raise SystemExit(f"invalid exact-span anchor: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown candidate for mention {mention_id}: {candidate_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": sid,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })


def add_span(mention_id, sid, candidate_id, surface, note):
    if mention_id in mention_ids or any(r["mention_id"] == mention_id for r in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    start = SEGMENT_TEXT[sid].find(surface)
    if start < 0:
        raise SystemExit(f"surface span not found in {sid}: {surface!r}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"unknown candidate for mention {mention_id}: {candidate_id}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": sid,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })


# Printed p.266 / PDF physical p.32.
add_mention("m-chp9-p266-sagredo", SEGMENT_266, 304, "cand-2329", "Sagredo", "Use Zaccaria Sagredo's base candidate; S3 identity alignment remains separate.")
add_mention("m-chp9-p266-tiepolo-contact", SEGMENT_266, 304, "cand-2569", "Tiepolo", "Haskell qualifies the early contact as probable.")
add_mention("m-chp9-p266-piazzetta-contact", SEGMENT_266, 304, "cand-1901", "Piazzetta", "Artist named in Haskell's probable-contact summary.")
add_mention("m-chp9-p266-canaletto-contact", SEGMENT_266, 304, "cand-0522", "Canaletto", "Artist named in Haskell's probable-contact summary.")
add_mention("m-chp9-p266-longhi-contact", SEGMENT_266, 304, "cand-1429", "Longhi", "Surname-only mention; use the base index candidate pending S3.")
add_mention("m-chp9-p266-print-collection", SEGMENT_266, 304, "cand-2334", "prints and drawings", "Use the Sagredo index sub-entry for his collection of prints and drawings.")
add_mention("m-chp9-p266-breval", SEGMENT_266, 304, "cand-0451", "John Breval", "Author quoted by Haskell; the exact cited title is cross-referenced in note 1.")
add_mention("m-chp9-p266-inventories", SEGMENT_266, 305, "cand-8624", "inventories of the Sagredo collection", "Unidentified posthumous collection inventories; not the specific 1743 first inventory noted on p.265.")
add_mention("m-chp9-p266-drawing-volumes", SEGMENT_266, 305, "cand-8635", "many volumes of drawings", "Collection group reported in the posthumous inventories; Haskell says assembly by Zaccaria can be assumed.")
add_mention("m-chp9-p266-rembrandt", SEGMENT_266, 305, "cand-2117", "Rembrandt", "The works are attributed to Rembrandt in the source, not independently verified.")
add_mention("m-chp9-p266-tiepolo-drawings", SEGMENT_266, 305, "cand-2569", "Tiepolo", "Named among contemporary artists represented in the drawing volumes.")
add_mention("m-chp9-p266-piazzetta-drawings", SEGMENT_266, 305, "cand-1901", "Piazzetta", "Named among contemporary artists represented in the drawing volumes.")
add_mention("m-chp9-p266-cimaroli", SEGMENT_266, 305, "cand-0758", "Cimatoli", "S0 OCR reads Cimatoli; CHP-9.pdf physical p.32 reads Cimaroli. Map to the matching index candidate provisionally and preserve the OCR form.")
add_mention("m-chp9-p266-manaigo", SEGMENT_266, 305, "cand-1503", "Silvestro Manaigo", "Named among contemporary artists represented in the drawing volumes.")
add_mention("m-chp9-p266-moschini", SEGMENT_266, 305, "cand-1709", "Moschini", "Haskell reports Moschini as the source for the Torresani commission.")
add_mention("m-chp9-p266-torresani", SEGMENT_266, 306, "cand-2649", "Andrea Torresani", "Artist named as Brescian; the claim is mediated through Haskell's citation to Moschini.")
add_mention("m-chp9-p266-hundred-views", SEGMENT_266, 305, "cand-8625", "too views", "OCR surface retained for anchoring; the scan reads 100 views, and the S2 claim interprets it as one hundred.")
add_mention("m-chp9-p266-lazzarini", SEGMENT_266, 306, "cand-1368", "Lazzarini", "Surname-only source form; mapping to the indexed Gregorio Lazzarini candidate remains provisional.")
add_mention("m-chp9-p266-lazzarini-drawings", SEGMENT_266, 306, "cand-8626", "all the rare and very correct drawings", "Unidentified group of drawings bought at a high price; the artist's surname is anchored separately.")
add_mention("m-chp9-p266-diziani", SEGMENT_266, 306, "cand-0922", "Gaspare] Diziani", "The source supplies Gaspare in brackets; do not treat the bracket as original authorial wording.")
add_mention("m-chp9-p266-diziani-volume", SEGMENT_266, 306, "cand-8627", "bound into a volume all the drawings", "Unidentified drawings said to have been bound together in one volume; the artist's name is anchored separately.")
add_mention("m-chp9-p266-sagredo-heirs", SEGMENT_266, 307, "cand-2329", "Zaccaria", "Named as the owner whose heirs later sold the drawings.")
add_mention("m-chp9-p266-smith", SEGMENT_266, 307, "cand-2440", "Joseph Smith", "Use the indexed person candidate; keep purchase of drawing volumes distinct from the later sale to George III.")
add_mention("m-chp9-p266-royal-collection", SEGMENT_266, 307, "cand-2292", "Royal Collection", "Repository named as the survival location in Haskell's account; current status is not independently checked.")
add_mention("m-chp9-p266-carracci-group", SEGMENT_266, 308, "cand-8590", "Carracci drawings", "Reuse the group candidate already created from p.263 note 5; p.266 adds the three-volume provenance detail.")
add_mention("m-chp9-p266-bonfiglioli", SEGMENT_266, 308, "cand-0387", "Bonfiglioli collection", "Use the indexed collection candidate; its relation to the Bonfiglioli family candidate remains for S3.")
add_mention("m-chp9-p266-bologna", SEGMENT_266, 308, "cand-8605", "Bologna", "Reuse the place candidate established for the Bonfiglioli family on p.263 note 5.")
add_mention("m-chp9-p266-raphael", SEGMENT_266, 308, "cand-2098", "Raphael", "Artist of the fine sheets reported as included in the purchase.")
add_mention("m-chp9-p266-raphael-sheets", SEGMENT_266, 308, "cand-8633", "fine sheets", "Unidentified drawing sheets; the artist is anchored separately and no titles are assigned from other Raphael candidates.")
add_mention("m-chp9-p266-castiglione", SEGMENT_266, 309, "cand-0602", "Giovanni Benedetto Castiglione", "Use the indexed artist candidate.")
add_mention("m-chp9-p266-castiglione-collection", SEGMENT_266, 309, "cand-2333", "set of drawings", "Use the Sagredo index sub-entry for Castiglione drawings; the group has no titles in this passage.")
add_mention("m-chp9-p266-algarotti", SEGMENT_266, 309, "cand-0041", "Francesco Algarotti", "Named as a prospective purchaser of Sagredo's volumes.")
add_mention("m-chp9-p266-king-saxony", SEGMENT_266, 309, "cand-8622", "King of Saxony", "Title-only reference; do not infer Augustus II or Augustus III without a date or explicit identification.")
add_mention("m-chp9-p266-smith-transfer", SEGMENT_266, 309, "cand-2440", "Joseph Smith", "Actual purchaser of Sagredo's volumes in Haskell's account.")
add_mention("m-chp9-p266-algarotti-gift", SEGMENT_266, 310, "cand-0041", "Algarotti", "Source line continues from 'who'; the scan confirms Joseph Smith is the recipient of additional drawings.")
add_mention("m-chp9-p266-additional-drawings", SEGMENT_266, 310, "cand-8637", "a large number of additional Castiglione drawings", "A separately acquired group from the volumes Smith obtained from Sagredo; the source gives no titles or count.")
add_mention("m-chp9-p266-zanetti", SEGMENT_266, 311, "cand-2838", "Antonio Maria Zanetti the Elder", "Use the indexed artist/connoisseur candidate.")
add_mention("m-chp9-p266-sagredo-zanetti", SEGMENT_266, 311, "cand-2329", "Sagredo", "The text explicitly says Zanetti was Sagredo's friend.")
add_mention("m-chp9-p266-castiglione-zanetti", SEGMENT_266, 311, "cand-0602", "Castiglione", "The pronoun in 'his drawings' refers to Castiglione.")
add_mention("m-chp9-p266-zanetti-prints", SEGMENT_266, 311, "cand-8630", "twelve ofhis drawings", "OCR merges 'of his'; printed p.32 has the space. Group of twelve engravings after Castiglione drawings; footnote 8 sends readers to a later chapter.")

# Printed p.267 / PDF physical p.33; this closes the sentence begun at p.266 L311.
add_mention("m-chp9-p267-tiepolo", SEGMENT_267, 314, "cand-2569", "Tiepolo", "Subject of Haskell's account of admiration for Castiglione.")
add_mention("m-chp9-p267-castiglione", SEGMENT_267, 314, "cand-0602", "Castiglione", "Use the indexed artist candidate.")
add_mention("m-chp9-p267-monotype", SEGMENT_267, 314, "cand-8628", "a monotype by the artist", "The artist is Castiglione, named earlier in the same line; no title or location is given.")
add_mention("m-chp9-p267-etchings", SEGMENT_267, 314, "cand-8629", "his own etchings", "Pronoun refers to Tiepolo; Haskell interprets subject and technique as evidence of study of Castiglione.")
add_mention("m-chp9-p267-algarotti", SEGMENT_267, 315, "cand-0041", "Algarotti", "Named as the first to point out the influence that Haskell sees.")
add_mention("m-chp9-p267-castiglione-reception", SEGMENT_267, 316, "cand-0602", "Castiglione’s prints and drawings", "Use the indexed artist candidate and the Sagredo collection sub-entry.")
add_mention("m-chp9-p267-venice", SEGMENT_267, 316, "cand-2719", "Venice", "Place named in Haskell's account of early reception.")
add_mention("m-chp9-p267-sagredo", SEGMENT_267, 316, "cand-2329", "Zaccaria Sagredo", "Named in the posthumous-reception and collection statement.")
add_mention("m-chp9-p267-castiglione-collection", SEGMENT_267, 316, "cand-8636", "The drawings", "Context identifies the set of Castiglione drawings in Sagredo's collection; purchase price is reported, not independently verified.")
add_mention("m-chp9-p267-collection-works", SEGMENT_267, 316, "cand-8636", "these works by the master", "Castiglione drawings Sagredo is said to have collected extensively.")
add_mention("m-chp9-p267-ferdinando", SEGMENT_267, 317, "cand-1524", "Ferdinando Carlo Gonzaga", "Use the indexed Duke of Mantua person candidate; preserve the title and identity as reported.")
add_mention("m-chp9-p267-austrians", SEGMENT_267, 318, "cand-7284", "invading Austrians", "Collective military-political actor; reuse the existing Austria actor candidate, with no unit specified.")
add_mention("m-chp9-p267-venice-refuge", SEGMENT_267, 318, "cand-2719", "Venice", "Destination of Ferdinando Carlo's reported refuge.")
add_mention("m-chp9-p267-padua", SEGMENT_267, 318, "cand-1803", "Padua", "Place of death reported by Haskell.")
add_mention("m-chp9-p267-mantua", SEGMENT_267, 318, "cand-6672", "Mantua", "Use the place candidate for the ducal collections and the Duke's title context.")
add_mention("m-chp9-p267-pictures-900", SEGMENT_267, 318, "cand-8631", "over 900 pictures from the ducal collections", "Haskell reports the number and transfer; the sending agent and individual paintings are unknown.")
add_span("m-chp9-p267-lorraine", SEGMENT_267, "cand-1441", "Duke of\nLorraine", "Title is split at the OCR line break; use the title-only index candidate and defer personal identity.")
add_mention("m-chp9-p267-gonzaga", SEGMENT_267, 319, "cand-6669", "Gonzaga effects", "The phrase refers to estate/property claimed by the Duke of Lorraine, not a claim about a family relationship.")
add_mention("m-chp9-p267-mantua-market", SEGMENT_267, 319, "cand-6672", "Mantua", "Source says many pictures from Mantua reached the Venetian market.")
add_mention("m-chp9-p267-venice-market", SEGMENT_267, 319, "cand-2719", "Venetian market", "Place reference is Venice; 'market' is not a separately named institution.")
add_mention("m-chp9-p267-carriera", SEGMENT_267, 320, "cand-0581", "Rosalba Carriera", "Use the indexed artist candidate.")
add_mention("m-chp9-p267-elector-palatine", SEGMENT_267, 320, "cand-8623", "Elector Palatine", "Title-only recipient; the source does not identify the person or date of purchase.")
add_mention("m-chp9-p267-carriera-pictures", SEGMENT_267, 320, "cand-8634", "bought two", "Two unnamed pictures Carriera bought; keep separate from Schulenburg's batch of Castiglione paintings and the recipient mention that follows.")
add_span("m-chp9-p267-schulenburg", SEGMENT_267, "cand-2401", "Field\nMarshall Schulenburg", "Name is split at the OCR line break; reuse the indexed Field Marshal Johann Matthias von der Schulenburg candidate.")
add_mention("m-chp9-p267-schulenburg-castiglione", SEGMENT_267, 321, "cand-8632", "several Castigliones", "Several paintings by Castiglione within Schulenburg's batch; do not confuse them with the drawings in Sagredo's collection.")
add_mention("m-chp9-p267-court-painter", SEGMENT_267, 321, "cand-0602", "this artist", "Pronoun refers to Castiglione, who Haskell says had been court painter at Mantua for over twenty years.")
add_mention("m-chp9-p267-castiglione-provenance", SEGMENT_267, 321, "cand-0602", "Castiglione", "Explicit artist reference in Haskell's statement that some drawings relate to pictures he painted at Mantua.", 1)
add_mention("m-chp9-p267-mantua-court", SEGMENT_267, 321, "cand-6672", "Mantua", "Place of Castiglione's reported court-painter service.")
add_mention("m-chp9-p267-ferdinando-provenance", SEGMENT_267, 321, "cand-1524", "Ferdinando Carlo", "One of two possible owners in Haskell's expressly tentative provenance hypothesis.")
add_mention("m-chp9-p267-sagredo-provenance", SEGMENT_267, 321, "cand-2329", "Sagredo", "Owner/assembler of the drawings in the tentative provenance hypothesis.")
add_mention("m-chp9-p267-drawings-provenance", SEGMENT_267, 321, "cand-8636", "his volumes", "The volumes are Sagredo's Castiglione drawings; source explicitly says no specific reference to drawings was found among the works sent to the Duke.")


def q(line_no, start_text, end_text=None):
    text = source_lines[line_no - 1]
    start = text.index(start_text)
    if end_text is None:
        return text[start:]
    end = text.index(end_text, start) + len(end_text)
    return text[start:end]


def q2(line1, start_text, line2, end_text):
    return q(line1, start_text) + "\n" + q(line2, "", end_text)


new_statements = []


def add_statement(statement_id, sid, subject, object_, predicate, quote, line_start, line_end, claim, qualification, mentioned, *, speaker="Haskell", text_layer="authorial narrative", relation=False, crossrefs=None, footnote=None):
    if statement_id in statement_ids or any(s["statement_id"] == statement_id for s in new_statements):
        raise SystemExit(f"duplicate statement ID: {statement_id}")
    if quote not in SEGMENT_TEXT[sid]:
        raise SystemExit(f"statement quote is not anchored in its segment: {statement_id}")
    refs = set(mentioned)
    if subject:
        refs.add(subject)
    if object_:
        refs.add(object_)
    if not refs <= candidate_ids:
        raise SystemExit(f"statement has missing candidate keys: {statement_id}: {refs - candidate_ids}")
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "printed_page": 266 if sid == SEGMENT_266 else 267,
        "pdf_physical_page": 32 if sid == SEGMENT_266 else 33,
        "claim": claim,
        "speaker": speaker,
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": sorted(refs),
    }
    if relation:
        qualifiers["relation_candidate"] = True
    if crossrefs:
        qualifiers["cross_reference_segments"] = crossrefs
    if footnote:
        qualifiers["footnote_marker"] = footnote
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": sid,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
        "origin": "book",
    })


NOTES = lambda start, end=None: {"segment_id": NOTE_SEGMENT, "source_line_start": start, "source_line_end": end or start}
P263_BREVAL = {"segment_id": NOTE_SEGMENT, "source_line_start": 416, "source_line_end": 416}
P263_N5 = {"segment_id": NOTE_SEGMENT, "source_line_start": 418, "source_line_end": 418}

# Printed p.266: probable contacts, reputation and print/drawing collection.
add_statement(
    "st-chp9-p266-probable-artist-contacts", SEGMENT_266,
    "cand-2329", None, "sagredo_probably_contacted_tiepolo_piazzetta_canaletto_and_longhi_early_in_their_careers",
    q(304, "Despite his probable contacts", "so late in his,"), 304, 304,
    "Haskell says Zaccaria Sagredo probably had contacts with Tiepolo, Piazzetta, Canaletto and Longhi early in their careers and late in his own life.",
    "Preserve 'probable' and the relative chronology; the passage names no specific meeting, correspondence or date.",
    ["cand-2329", "cand-2569", "cand-1901", "cand-0522", "cand-1429"], relation=True,
)
add_statement(
    "st-chp9-p266-reputation-and-collection", SEGMENT_266,
    "cand-2329", None, "sagredo_patronage_reputation_rest_on_contemporary_enthusiasm_and_print_collection",
    q(304, "our knowledge of Sagredo", "prints and drawings."), 304, 304,
    "Haskell says little is known of Sagredo, that contemporaries' enthusiasm explains attention to his patronage, and that he was a passionate collector of prints and drawings.",
    "This is Haskell's account of his historical reputation, not a measured comparison of all patrons.",
    ["cand-2329", "cand-2334"],
)
add_statement(
    "st-chp9-p266-breval-assessment", SEGMENT_266,
    "cand-0451", None, "breval_described_sagredos_print_collection_as_largest_in_europe_but_called_it_his_only_famous_branch",
    q(304, "Indeed, John Breval wrote") + "\n" + q(305, "‘This is the only Branch", "Gentleman is famous for.’1"), 304, 305,
    "Haskell quotes John Breval as saying Sagredo was reckoned to have Europe's largest print collection; Breval then called print collecting the only branch of virtue for which Sagredo was famous.",
    "Nested quotation attributed to Breval; Haskell calls the latter judgment unfair. Footnote 1 points to Breval 1738, vol. I, p.230, via p.263 note 3.",
    ["cand-0451", "cand-2334", "cand-7713"], speaker="John Breval, quoted by Haskell", text_layer="nested quotation",
    crossrefs=[NOTES(433), P263_BREVAL], footnote=1,
)
add_statement(
    "st-chp9-p266-inventories-record-volumes", SEGMENT_266,
    "cand-8624", "cand-8635", "posthumous_sagredo_inventories_list_many_drawing_volumes_assumed_assembled_by_him",
    q(305, "In the inventories of the Sagredo collection", "assembled by him."), 305, 305,
    "Haskell says inventories drawn up some years after Zaccaria Sagredo's death list many volumes of drawings, which he assumes Sagredo assembled.",
    "The records and dates are not specified; the assembly claim is explicitly an inference and the group is distinct from the named 1743 first inventory.",
    ["cand-8624", "cand-2329", "cand-8635"], relation=True,
)
add_statement(
    "st-chp9-p266-attributed-artists-in-volumes", SEGMENT_266,
    "cand-8624", "cand-8635", "inventories_include_drawings_attributed_to_rembrandt_german_old_masters_and_contemporaries",
    q(305, "They include works attributed", "and others."), 305, 305,
    "Haskell says the volumes include works attributed to Rembrandt and German old masters, as well as contemporary artists including Tiepolo, Piazzetta, Cimaroli and Silvestro Manaigo.",
    "The source uses attribution language; it does not establish Rembrandt's authorship or identify individual sheets. Scan p.32 reads 'Cimaroli'; S0 OCR 'Cimatoli' is retained with a correction note.",
    ["cand-8624", "cand-8635", "cand-2117", "cand-2569", "cand-1901", "cand-0758", "cand-1503"],
)
add_statement(
    "st-chp9-p266-torresani-views", SEGMENT_266,
    "cand-2329", "cand-8625", "sagredo_commissioned_one_hundred_pen_and_ink_views_from_andrea_torresani",
    q(305, "From Moschini we learn") + "\n" + q(306, "Andrea Torresani", "Andrea Torresani"), 305, 306,
    "Haskell, citing Moschini, says Sagredo also commissioned 100 pen-and-ink views from the Brescian artist Andrea Torresani.",
    "The printed scan reads '100 views'; S0 OCR reads 'too views'. This is a visual correction recorded at S2. Individual views and the cited Moschini passage have not been independently examined.",
    ["cand-2329", "cand-8625", "cand-2649", "cand-1709"], relation=True, crossrefs=[NOTES(434)], footnote=2,
)
add_statement(
    "st-chp9-p266-lazzarini-drawings", SEGMENT_266,
    "cand-2329", "cand-8626", "sagredo_bought_lazzarini_drawings_at_high_price",
    q(306, "other sources tell us that he bought", "drawings of Lazzarini,"), 306, 306,
    "Haskell says other sources report Sagredo bought at a high price all the rare and very correct drawings of Lazzarini.",
    "The sources are only identified in footnote 3 as Da Canal and Fontana; they have not been independently consulted. Keep the artist surname-only mapping provisional.",
    ["cand-2329", "cand-8626", "cand-1368"], relation=True, crossrefs=[NOTES(435)], footnote=3,
)
add_statement(
    "st-chp9-p266-diziani-volume", SEGMENT_266,
    "cand-2329", "cand-8627", "sagredo_bound_diziani_drawings_together_in_a_volume",
    q(306, "and also bound into a volume", "Diziani’.") , 306, 306,
    "The source quoted by Haskell says Sagredo bound all the drawings of the Bellunese [Gaspare] Diziani into a volume.",
    "The source supplies Gaspare in brackets; preserve this editorial identification and do not infer titles or a count beyond 'all the drawings'. The underlying sources are cited, not independently read.",
    ["cand-2329", "cand-8627", "cand-0922"], relation=True, crossrefs=[NOTES(435)], footnote=3,
)
add_statement(
    "st-chp9-p266-sagredo-heirs-sold-volumes", SEGMENT_266,
    None, "cand-8635", "sagredo_heirs_later_sold_drawing_volumes",
    q(307, "In later years these drawings were sold by Zaccaria’s heirs"), 307, 307,
    "Haskell says the drawing volumes were sold by Zaccaria Sagredo's heirs in later years.",
    "The heirs are unnamed and the sale date and terms are not supplied.",
    ["cand-2329", "cand-8635"], relation=True,
)
add_statement(
    "st-chp9-p266-smith-bought-several-volumes", SEGMENT_266,
    "cand-2440", "cand-8635", "joseph_smith_bought_several_complete_sagredo_drawing_volumes",
    q(307, "among those who bought several complete volumes was the Englishman Joseph Smith."), 307, 307,
    "Haskell says Joseph Smith bought several complete volumes from the drawings sold by Sagredo's heirs.",
    "The passage does not specify which volumes or the date and terms of Smith's purchases.",
    ["cand-2440", "cand-8635", "cand-2329"], relation=True,
)
add_statement(
    "st-chp9-p266-volumes-survive-royal-collection", SEGMENT_266,
    "cand-8635", "cand-2292", "sagredo_drawing_volumes_survived_in_royal_collection_by_haskells_account",
    q(307, "As these still survive", "connoisseurship."), 307, 307,
    "Haskell says the drawing volumes still survived in the Royal Collection, allowing Sagredo's connoisseurship to be assessed.",
    "The survival statement is Haskell's at publication time; it does not independently confirm the collection's present holdings.",
    ["cand-8635", "cand-2292", "cand-2440"], relation=True,
)
add_statement(
    "st-chp9-p266-carracci-volumes-from-bonfiglioli", SEGMENT_266,
    "cand-2329", "cand-8590", "sagredo_bought_three_volumes_of_carracci_drawings_from_bonfiglioli_collection_in_bologna",
    q(308, "Thus the Carracci drawings there", "collection in Bologna.4"), 308, 308,
    "Haskell says the Carracci drawings in the surviving volumes came from three volumes Sagredo bought near the end of his life from the Bonfiglioli collection in Bologna.",
    "Reuse the Carracci drawings candidate from p.263 note 5. P.263 note 5 names the Bonfiglioli family; whether that family and the indexed collection represent the same provenance is deferred to S3.",
    ["cand-2329", "cand-8590", "cand-0387", "cand-8605", "cand-2292"], relation=True,
    crossrefs=[P263_N5, NOTES(436)], footnote=4,
)
add_statement(
    "st-chp9-p266-raphael-sheets-in-purchase", SEGMENT_266,
    "cand-2329", "cand-8633", "sagredo_bonfiglioli_purchase_included_fine_raphael_sheets",
    q(308, "This purchase, which included fine sheets by Raphael", "fine sheets by Raphael"), 308, 308,
    "Haskell says the purchase included fine sheets by Raphael.",
    "The sheets are not individually identified; footnote 5 cites Popham and Wilde 1949, p.14, not independently examined.",
    ["cand-2329", "cand-8633", "cand-2098", "cand-8590"], relation=True, crossrefs=[NOTES(437)], footnote=5,
)
add_statement(
    "st-chp9-p266-original-pieces-and-attention", SEGMENT_266,
    "cand-2329", None, "reported_original_pieces_by_greatest_masters_attracted_connoisseur_attention",
    q(308, "and ‘numbers of Original Pieces", "connoisseurs of the day.6"), 308, 308,
    "Haskell says the purchase included 'numbers of Original Pieces by the greatest masters' and attracted much attention among the day's connoisseurs.",
    "The quoted phrase is preserved as printed; footnote 6 points to a 1728 letter by A. M. Zanetti published in Bottari, not independently consulted. The individual works are unidentified.",
    ["cand-2329", "cand-8590", "cand-2838"], crossrefs=[NOTES(438)], footnote=6,
)
add_statement(
    "st-chp9-p266-castiglione-set-and-later-taste", SEGMENT_266,
    "cand-2329", "cand-8636", "sagredo_owned_a_magnificent_extensive_castiglione_drawing_set_important_to_later_taste",
    q(308, "However, another of Sagredo’s possessions") + "\n" + q(309, "Venetian", "Giovanni Benedetto Castiglione.7"), 308, 309,
    "Haskell calls Sagredo's Castiglione drawing set magnificent and the finest in existence, and says it mattered greatly for later Venetian taste and art.",
    "The ranking and assessment are Haskell's evaluation; no individual sheet or comparison method is specified.",
    ["cand-2329", "cand-8636", "cand-0602"], relation=True, crossrefs=[NOTES(439)], footnote=7,
)
add_statement(
    "st-chp9-p266-algarotti-intended-purchase", SEGMENT_266,
    "cand-0041", "cand-8636", "algarotti_wanted_sagredo_volumes_for_king_of_saxony",
    q(309, "The connoisseur Francesco Algarotti", "Joseph Smith, who"), 309, 309,
    "Haskell says Francesco Algarotti was keen to acquire Sagredo's volumes for the King of Saxony.",
    "The King is unnamed and the passage does not state that Algarotti completed a purchase; the title-holder's identity remains unresolved.",
    ["cand-0041", "cand-8636", "cand-8622"], relation=True,
)
add_statement(
    "st-chp9-p266-smith-acquired-sagredo-volumes", SEGMENT_266,
    "cand-2440", "cand-8636", "joseph_smith_acquired_sagredos_castiglione_volumes",
    q(309, "but they were in fact obtained by Joseph Smith"), 309, 309,
    "Haskell says Joseph Smith actually obtained the Sagredo volumes that Algarotti had wanted to buy for the King of Saxony.",
    "The King is an intended recipient in Algarotti's proposed purchase, not the actual buyer; the two transactions remain distinct.",
    ["cand-2440", "cand-8636", "cand-0041", "cand-8622"], relation=True,
)
add_statement(
    "st-chp9-p266-algarotti-gave-additional-drawings", SEGMENT_266,
    "cand-0041", "cand-8637", "algarotti_gave_smith_additional_castiglione_drawings",
    q(310, ", was also given", "Algarotti himself."), 310, 310,
    "Haskell says Joseph Smith was also given many additional Castiglione drawings by Algarotti.",
    "The scan shows 'who was also given'; OCR line L310 begins ', was also given'. This is a continuation of the preceding line, not a new subject or a separate punctuation claim.",
    ["cand-0041", "cand-2440", "cand-8637"], relation=True,
)
add_statement(
    "st-chp9-p266-smith-received-additional-drawings", SEGMENT_266,
    "cand-8637", "cand-2440", "additional_castiglione_drawings_were_given_to_smith",
    q(310, ", was also given", "Algarotti himself."), 310, 310,
    "Haskell says Smith received the additional Castiglione drawings from Algarotti.",
    "Smith is the antecedent of 'who' at the end of p.266 L309; scan p.32 confirms the sentence continues across the OCR line break.",
    ["cand-8637", "cand-2440", "cand-0041"], relation=True,
)
add_statement(
    "st-chp9-p266-zanetti-friend-of-sagredo", SEGMENT_266,
    "cand-2838", "cand-2329", "zanetti_was_sagredos_friend",
    q(311, "Another connoisseur", "himself a friend of Sagredo,"), 311, 311,
    "Haskell says A. M. Zanetti the Elder was a friend of Sagredo.",
    "The source supplies no detail about when or how the friendship formed.",
    ["cand-2838", "cand-2329"], relation=True,
)
add_statement(
    "st-chp9-p266-zanetti-admired-castiglione", SEGMENT_266,
    "cand-2838", "cand-0602", "zanetti_admired_castiglione",
    q(311, "was also a lover of Castiglione", "was also a lover of Castiglione"), 311, 311,
    "Haskell says A. M. Zanetti the Elder was an admirer of Castiglione.",
    "The source's 'lover' describes artistic admiration, not a personal relationship.",
    ["cand-2838", "cand-0602"], relation=True,
)
add_statement(
    "st-chp9-p266-zanetti-engraved-twelve", SEGMENT_266,
    "cand-2838", "cand-8630", "zanetti_engraved_twelve_castiglione_drawings_in_1759",
    q(311, "and in 1759 engraved twelve ofhis drawings.8"), 311, 311,
    "Haskell says Zanetti engraved twelve of Castiglione's drawings in 1759.",
    "The individual engravings are not titled or located; scan p.32 reads 'of his' while S0 OCR merges it as 'ofhis'. Note 8 directs readers to a later chapter.",
    ["cand-2838", "cand-0602", "cand-8630"], relation=True, crossrefs=[NOTES(440)], footnote=8,
)

# Printed p.267 / PDF physical p.33.
add_statement(
    "st-chp9-p267-tiepolo-admired-castiglione", SEGMENT_267,
    "cand-2569", "cand-0602", "tiepolo_admired_castiglione",
    q(314, "significance was the admiration that Tiepolo felt for Castiglione."), 314, 314,
    "Haskell says Tiepolo's admiration for Castiglione was of particular significance.",
    "Authorial emphasis; no specific date or meeting is asserted.",
    ["cand-2569", "cand-0602"], relation=True,
)
add_statement(
    "st-chp9-p267-tiepolo-owned-castiglione-monotype", SEGMENT_267,
    "cand-2569", "cand-8628", "tiepolo_owned_a_castiglione_monotype",
    q(314, "We know that he himself owned a monotype by the artist"), 314, 314,
    "Haskell says Tiepolo owned a monotype by Castiglione.",
    "No title, location or independent object evidence is supplied; 'the artist' refers to Castiglione named earlier in the sentence.",
    ["cand-2569", "cand-8628", "cand-0602"], relation=True,
)
add_statement(
    "st-chp9-p267-tiepolo-etchings-study-castiglione", SEGMENT_267,
    "cand-8629", "cand-0602", "castiglione_study_apparent_in_subject_and_technique_of_tiepolo_etchings",
    q(314, "and his passionate study", "his own etchings, as") + "\n" + q(315, "Algarotti was the first to point out."), 314, 315,
    "Haskell says Castiglione's influence is apparent in the subject matter and technique of Tiepolo's etchings, as Algarotti was the first to point out.",
    "This is Haskell's art-historical interpretation, attributed to Algarotti as an earlier observer; it does not establish that any specific etching copied a specific Castiglione work.",
    ["cand-8629", "cand-2569", "cand-0602", "cand-0041"], relation=True, crossrefs=[NOTES(441)], footnote=1,
)
add_statement(
    "st-chp9-p267-posthumous-castiglione-reception", SEGMENT_267,
    "cand-0602", None, "castiglione_prints_and_drawings_became_fervently_admired_after_sagredos_death",
    q(316, "This admiration for Castiglione’s prints and drawings", "after Zaccaria Sagredo’s death"), 316, 316,
    "Haskell says widespread fervent admiration for Castiglione's prints and drawings came only after Zaccaria Sagredo's death.",
    "This is a broad chronological generalization by Haskell, not a claim that no earlier individual admired the works.",
    ["cand-0602", "cand-2329", "cand-8636"],
)
add_statement(
    "st-chp9-p267-sagredo-early-venetian-collector", SEGMENT_267,
    "cand-2329", "cand-8636", "sagredo_seems_first_in_venice_to_admire_and_collect_castiglione_works_extensively",
    q(316, "but he seems to have been the first in Venice", "on an extensive scale."), 316, 316,
    "Haskell says Sagredo seems to have been the first in Venice to experience admiration for Castiglione and to collect his works extensively.",
    "Preserve 'seems'; the priority claim is Haskell's inference, not independently established here.",
    ["cand-2329", "cand-8636", "cand-0602", "cand-2719"], relation=True,
)
add_statement(
    "st-chp9-p267-sagredo-paid-1500-zecchini", SEGMENT_267,
    "cand-2329", "cand-8636", "sagredo_was_said_to_buy_castiglione_drawings_for_1500_zecchini",
    q(316, "The drawings were chosen with great care") + "\n" + q(317, "Sagredo for 1500 zecchini.2", "1500 zecchini.2"), 316, 317,
    "Haskell says the drawings were chosen with great care and were said to have been bought by Sagredo for 1,500 zecchini.",
    "Retain 'were said to'; footnote 2 cites Smith's will as published by Parker 1948, p.60, not independently checked.",
    ["cand-2329", "cand-8636"], relation=True, crossrefs=[NOTES(442)], footnote=2,
)
add_statement(
    "st-chp9-p267-seller-of-drawings-unknown", SEGMENT_267,
    None, "cand-8636", "seller_of_sagredo_castiglione_drawings_not_certain",
    q(317, "We have no certain knowledge of who sold them to him", "one source seems very likely."), 317, 317,
    "Haskell says the seller of the drawings is not known with certainty, though one source seems likely.",
    "Do not upgrade the following provenance hypothesis into a confirmed seller or transfer.",
    ["cand-2329", "cand-8636"],
)
add_statement(
    "st-chp9-p267-ferdinando-refuge-in-venice", SEGMENT_267,
    "cand-1524", "cand-2719", "ferdinando_carlo_sought_refuge_in_venice_from_austrian_invasion_in_1706",
    q(317, "In 1706 Ferdinando Carlo Gonzaga") + "\n" + q(318, "Mantua, sought refuge in Venice from the invading Austrians.", "invading Austrians."), 317, 318,
    "Haskell says Ferdinando Carlo Gonzaga, the last Duke of Mantua, sought refuge in Venice from the invading Austrians in 1706.",
    "This is Haskell's historical account; the Austrian force is unnamed. Reuse the existing Austria political-military candidate without inferring a specific unit.",
    ["cand-1524", "cand-2719", "cand-7284", "cand-6672"], relation=True,
)
add_statement(
    "st-chp9-p267-ferdinando-death-in-padua", SEGMENT_267,
    "cand-1524", "cand-1803", "ferdinando_carlo_died_two_years_later_in_padua_at_age_56",
    q(318, "Two years later", "age of 56."), 318, 318,
    "Haskell says Ferdinando Carlo died two years later in Padua at age 56, describing him with the quoted French phrase about debauchery and gout.",
    "The two-year interval follows the stated 1706 refuge and is not restated as a calendar year. The condition phrase is a nested source characterization cited to Fochessati, p.278, not an independent medical claim.",
    ["cand-1524", "cand-1803"], crossrefs=[NOTES(443)], footnote=3,
)
add_statement(
    "st-chp9-p267-ducal-pictures-sent-and-distributed", SEGMENT_267,
    "cand-8631", "cand-1524", "over_nine_hundred_ducal_pictures_sent_to_ferdinando_then_distributed_among_courtiers",
    q(318, "In the meantime, however", "among his courtiers."), 318, 318,
    "Haskell says over 900 pictures from the ducal collections were sent to Ferdinando Carlo and widely distributed among his courtiers before his death.",
    "The sending agent, specific collection, individual pictures and recipients are not identified. The number is Haskell's report, not independently verified.",
    ["cand-8631", "cand-1524", "cand-6672"], relation=True,
)
add_statement(
    "st-chp9-p267-lorraine-claim", SEGMENT_267,
    "cand-1441", None, "duke_of_lorraine_established_claim_to_gonzaga_effects",
    q(318, "Eventually the Duke of") + "\n" + q(319, "Lorraine successfully established his claim", "Gonzaga effects,"), 318, 319,
    "Haskell says the Duke of Lorraine successfully established a claim to be heir to the Gonzaga effects.",
    "The Duke is unnamed; 'Gonzaga effects' refers to property or an estate, not a family relationship.",
    ["cand-1441", "cand-6669"], relation=True,
)
add_statement(
    "st-chp9-p267-mantua-pictures-entered-venetian-market", SEGMENT_267,
    None, None, "many_pictures_from_mantua_appeared_on_venetian_market",
    q(319, "but despite this a great number of pictures from Mantua turned up on the Venetian market."), 319, 319,
    "Haskell says a great number of pictures from Mantua appeared on the Venetian market despite the inheritance claim.",
    "No individual pictures or collection-to-market chain is identified; do not assume all market works came from the ducal collection.",
    ["cand-6672", "cand-2719"],
)
add_statement(
    "st-chp9-p267-carriera-bought-two-pictures", SEGMENT_267,
    "cand-0581", "cand-8634", "carriera_bought_two_pictures_for_elector_palatine",
    q(320, "Rosalba Carriera", "Elector Palatine"), 320, 320,
    "Haskell says Rosalba Carriera bought two pictures for the Elector Palatine.",
    "The pictures are unnamed and the title-holder's identity is not explicit.",
    ["cand-0581", "cand-8634", "cand-8623", "cand-6672"], relation=True,
)
add_statement(
    "st-chp9-p267-carriera-pictures-for-elector", SEGMENT_267,
    "cand-8634", "cand-8623", "carriera_pictures_were_for_elector_palatine",
    q(320, "Rosalba Carriera", "Elector Palatine"), 320, 320,
    "Haskell says Carriera's two pictures were for the Elector Palatine.",
    "The paintings and recipient are not individually named; keep the elector's identity unresolved.",
    ["cand-0581", "cand-8634", "cand-8623"], relation=True,
)
add_statement(
    "st-chp9-p267-schulenburg-bought-castiglione-batch", SEGMENT_267,
    "cand-2401", "cand-8632", "schulenburg_bought_market_batch_including_castiglione_paintings",
    q(320, "and the German collector Field") + "\n" + q(321, "Marshall Schulenburg", "several Castigliones,"), 320, 321,
    "Haskell says Field Marshal Schulenburg bought a large batch from the Mantuan market including several Castiglione paintings.",
    "The individual paintings are not identified; keep these pictures separate from Sagredo's drawing volumes.",
    ["cand-2401", "cand-8632", "cand-0602", "cand-6672"], relation=True, crossrefs=[NOTES(444)], footnote=4,
)
add_statement(
    "st-chp9-p267-castiglione-court-painter", SEGMENT_267,
    "cand-0602", "cand-6672", "castiglione_was_court_painter_at_mantua_for_over_twenty_years",
    q(321, "for this artist had been court painter", "over twenty years."), 321, 321,
    "Haskell says Castiglione had been court painter at Mantua for over twenty years.",
    "The source gives a duration but no exact appointment dates.",
    ["cand-0602", "cand-6672"], relation=True,
)
add_statement(
    "st-chp9-p267-tentative-mantuan-origin-of-sagredo-drawings", SEGMENT_267,
    None, "cand-8636", "sagredo_castiglione_volumes_may_derive_from_drawings_owned_by_ferdinando_or_his_entourage",
    q(321, "Although there is no specific reference", "Castiglione painted at Mantua.5"), 321, 321,
    "Haskell says that, despite no specific reference to drawings among works sent to the Duke in Venice, Ferdinando Carlo or someone in his entourage may well have owned the large quantity from which Sagredo assembled his volumes; some drawings relate to Castiglione pictures painted at Mantua.",
    "This is explicitly a tentative provenance hypothesis. Preserve the missing direct evidence and the alternative owner; it does not establish Ferdinando as seller or prove that all volumes came from the ducal collections. Footnote 5 cites Blunt 1954, p.36.",
    ["cand-1524", "cand-8636", "cand-0602", "cand-6672", "cand-8631"], relation=True, crossrefs=[NOTES(445)], footnote=5,
)
add_statement(
    "st-chp9-p267-sagredo-importance-in-taste", SEGMENT_267,
    "cand-2329", "cand-8636", "haskell_says_sagredo_fame_as_taste_pioneer_depends_on_castiglione_drawings",
    q(321, "But whatever their origin", "these drawings."), 321, 321,
    "Haskell says that, whatever their origin, Sagredo's main claim to fame as a pioneer in taste rests on his collection of Castiglione drawings.",
    "This is the author's assessment of historical significance, not a measured rank or a formal research finding.",
    ["cand-2329", "cand-8636", "cand-0602"],
)
add_statement(
    "st-chp9-p267-imagined-image-of-sagredo", SEGMENT_267,
    None, None, "haskell_uses_an_imagined_scene_of_sagredo_studying_castiglione_to_interpret_character",
    q(321, "And, on a more personal level", "records that have survived."), 321, 321,
    "Haskell says the imagined scene of Sagredo poring over Castiglione's 'sad, secret poetry' offers insight into Sagredo's character absent from the sparse surviving records.",
    "This is explicit authorial interpretation and metaphor, not evidence that a particular scene occurred.",
    ["cand-2329", "cand-0602", "cand-8636"], text_layer="authorial interpretation",
)

new_candidates_ids = {r["candidate_id"] for r in new_candidates}
new_statement_ids = {r["statement_id"] for r in new_statements}
if len(new_candidates_ids) != len(new_candidates) or len(new_statement_ids) != len(new_statements):
    raise SystemExit("duplicate candidate or statement ID within migration")

for sid, (start, end) in SEGMENT_BOUNDS.items():
    row = coverage_by_id[sid]
    if sid == SEGMENT_266:
        row.update({
            "disposition": "reviewed",
            "migration_status": "complete",
            "source_line_ranges": "L303-311",
            "note": "Printed p.266 body (PDF physical p.32) read against CHP-9.pdf. S2 records visual corrections without changing S0: printed Cimaroli for OCR Cimatoli; 100 views for OCR 'too views'; 'the German' for 'thejGerman'; 'to' for 'tò'; 'of his' for 'ofhis'; and continuation 'who was also given' where OCR begins L310 with a comma. The unfinished p.266 L311 phrase 'Of greater' closes at p.267 L314. P.266 notes 1-8 remain in the consolidated note segment L433-440 for separate migration.",
        })
    else:
        row.update({
            "disposition": "reviewed",
            "migration_status": "complete",
            "source_line_ranges": "L313-321",
            "note": "Printed p.267 body (PDF physical p.33) read against CHP-9.pdf; L314 closes p.266 L311. Haskell's interpretation, nested source claims, the reported 1500-zecchini price, and the expressly tentative Mantuan provenance hypothesis are separated. Notes 1-5 remain at consolidated L441-445. The scan contains a printed note 6 at the bottom of p.267, but it is absent from the current S0 OCR segment; add a derived visual-transcription segment before the consolidated notes are marked complete.",
        })

notes_cov.update({
    "source_line_ranges": notes_cov["source_line_ranges"] + "; p.265 notes L429-432, p.266 notes L433-440, p.267 notes L441-445 pending; p.267 printed note 6 absent from OCR",
    "note": notes_cov["note"] + " P.265 notes L429-432 and p.266 notes L433-440 remain pending; p.267 notes L441-445 remain pending. Visual review confirms p.267 footnote 6 is omitted from S0 OCR and requires a derived transcription before note coverage closes.",
})

summary = {
    "new_candidates": len(new_candidates),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "segments": [SEGMENT_266, SEGMENT_267],
    "visual_corrections": ["Cimatoli -> Cimaroli", "too views -> 100 views", "thejGerman -> the German", "tò -> to", "ofhis -> of his", "L310 leading comma -> continuation from who"],
    "open_source_gap": "p.267 printed footnote 6 is missing from S0 aggregate OCR; derived visual transcription remains required",
    "next_segment": "chp-9:09_CHP-9_intro:l323-445 (consolidated notes L429 onward)",
    "counts": {
        "candidates": len(candidates) + len(new_candidates),
        "mentions": len(mentions) + len(new_mentions),
        "statements": len(statements) + len(new_statements),
        "coverage_rows": len(coverage),
    },
}
print(json.dumps(summary, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the preflighted migration")
args = parser.parse_args()
if args.apply:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [p.with_name(p.name + BACKUP_SUFFIX) for p in paths]
    if any(p.exists() for p in backups):
        raise SystemExit("one or more recovery backups already exist; inspect before retrying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    try:
        write_csv(candidate_path, candidate_fields, candidates + new_candidates)
        write_csv(mention_path, mention_fields, mentions + new_mentions)
        write_jsonl(statement_path, statements + new_statements)
        write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    except Exception:
        for target, backup in zip(paths, backups):
            shutil.copy2(backup, target)
        raise
    print("APPLIED; recovery backups retained: " + ", ".join(p.name for p in backups))
else:
    print("DRY RUN: no S2 table rows written")
