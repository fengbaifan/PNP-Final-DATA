"""Controlled S2 migration for p.311-312 notes; dry-run by default."""

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-10.pdf"
BODY = "chp-10:10_CHP-10_sec_ii:l17-32"
PREVIOUS = "chp-10:10_CHP-10_sec_ii:l7-15"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
SOURCE_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BACKUP_SUFFIX = ".bak-s2-chp10-p311-312-notes-20261003"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write p.311-312 note rows and links")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical source markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
if source_lines[272] != "**Footnotes:**" or "Romanin" not in source_lines[273] or "Morassi" not in source_lines[282]:
    raise SystemExit("p.311-312 note source boundaries changed")
body_text = "\n".join(source_lines[16:32])
notes_text = "\n".join(source_lines[272:283])

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_ids = {row["candidate_id"] for row in candidates}
mention_ids = {row["mention_id"] for row in mentions}
statement_ids = {row["statement_id"] for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}

state = (
    len(candidates),
    max(int(row["candidate_id"].split("-")[1]) for row in candidates),
    len(mentions),
    len(statements),
)
if state != (9862, 9875, 20953, 9315):
    raise SystemExit(f"unexpected table pre-state: {state}")
for segment in (BODY, PREVIOUS, NOTES):
    if segment not in coverage:
        raise SystemExit(f"required coverage row missing: {segment}")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.311 is not reviewed/partial")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.312 is not reviewed/partial")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("consolidated notes segment is not reviewed/partial")
if any(row["segment_id"] == NOTES and 274 <= int(row.get("qualifiers", {}).get("source_line_start", 0)) <= 283 for row in statements):
    raise SystemExit("p.311-312 canonical note statements already exist")
if any(row["statement_id"].startswith("st-chp10-p311-n0") or row["statement_id"].startswith("st-chp10-p312-n0") for row in statements):
    raise SystemExit("p.311-312 note statement ID already exists")

new_candidates = []


def add_candidate(cid, name, kind, detail, line, segment=NOTES):
    if cid in candidate_ids or any(row["candidate_id"] == cid for row in new_candidates):
        raise SystemExit(f"candidate ID already exists: {cid}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": cid,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "detail": detail,
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{segment}#L{line}",
    })
    new_candidates.append(row)


add_candidate("cand-9876", "Leben und Denkwürdigkeiten Johann Mathias Reichsgrafen von der Schulenburg (Leipzig, 1834)", "archive", "Cited at p.311 notes 1 and 4 as the main biographical source and volume II, page 312. The cited book was not independently consulted.", 274)
add_candidate("cand-9877", "Romanin, volume VIII, page 53 (citation locator)", "archive", "P.311 note 2; the print reads VIII where the split OCR reads VID. The cited passage was not independently consulted.", 274)
add_candidate("cand-9878", "Drawing of Schulenburg's funeral procession, Archivio di Stato, VIII, Vari, no. 35", "archive", "Cited at p.311 note 3. The drawing and archive catalogue were not independently consulted.", 275)
add_candidate("cand-9879", "De Brosses, volume I, page 142 (citation locator)", "archive", "P.311 note 5 quotes De Brosses through Haskell. The cited volume and page were not independently consulted.", 278)
add_candidate("cand-9880", "Lord Rockingham to Lord Essex, Verona, 2 February 1733 (British Museum, Add. MSS. 27,733, f. 13)", "archive", "P.311 note 6 supplies this manuscript locator. The letter and current repository catalogue were not consulted.", 278)
add_candidate("cand-9881", "Schulenburg family papers, Biblioteca Marciana, It. VII, 480 (7785), cc. 234-264", "archive", "P.312 note 1 cites this shelfmark. The manuscript and current catalogue were not consulted.", 279)
add_candidate("cand-9882", "Haskell, 1956, page 298 (citation locator)", "archive", "P.312 note 2. The cited publication is not identified further in this note and was not independently consulted.", 280)
add_candidate("cand-9883", "Keysler, Travels, volume III, page 296 (citation locator)", "archive", "P.312 note 2 cites a passage about Schulenburg's Corfu collection. The cited volume and page were not independently consulted.", 27, BODY)
add_candidate("cand-9884", "Inventaire de la Galerie de feu Mgr. le Feldtnarechal Comte de Schulenburg (published inventory, n.d.)", "archive", "P.312 note 2 calls this Schulenburg's inventory and cross-refers to p.313 note 3, which gives this title. The inventory was not independently consulted.", 28, BODY)
add_candidate("cand-9885", "Morassi, 1952, pages 85-91 (citation locator)", "archive", "Cited for Schulenburg portraits in p.312 note 2 and p.313 note 3. The cited pages were not independently consulted.", 32, BODY)
add_candidate("cand-9886", "G. A. Moschini, 1924, page 93 (citation locator)", "archive", "P.312 note 3 cites Moschini for dealings with Pitteri. The cited passage was not independently consulted.", 281)
add_candidate("cand-9887", "Manuscript inventories of the Schulenburg collection, 1724-1737 (Staatsarchiv, Hanover)", "archive", "P.312 note 4 cites these collection inventories. The manuscripts and archive catalogue were not independently consulted.", 282)
add_candidate("cand-9888", "Edward Wright, volume I, page 78 (citation locator)", "archive", "P.312 note 4 cites Wright's reference to the Puget and works from the Duke of Mantua's collection. The cited page was not independently consulted.", 282)
add_candidate("cand-9889", "Morassi, 1960, pages 147-164 and 199-212 (citation locator)", "archive", "P.312 note 5; the print reads 1960 where OCR reads i960. The cited pages were not independently consulted.", 283)
add_candidate("cand-9890", "Romanin (author cited at p.311 note 2; identity unresolved)", "person", "Surname-only author reference in Haskell's note; no identity beyond the printed citation is assumed.", 274)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []
segment_bounds = {BODY: (17, 32), NOTES: (273, 349)}


def add_mention(cid, segment, line_no, needle, note="", occurrence=0):
    if cid not in all_candidate_ids:
        raise SystemExit(f"mention candidate missing: {cid}")
    start_line, end_line = segment_bounds[segment]
    if not start_line <= line_no <= end_line:
        raise SystemExit(f"mention line outside segment: {segment} L{line_no}")
    line = source_lines[line_no - 1]
    matches = []
    cursor = 0
    while True:
        at = line.find(needle, cursor)
        if at < 0:
            break
        matches.append(at)
        cursor = at + max(1, len(needle))
    if occurrence >= len(matches):
        raise SystemExit(f"mention needle missing at L{line_no}: {needle!r}")
    at = matches[occurrence]
    surface = line[at:at + len(needle)]
    segment_text = "\n".join(source_lines[start_line - 1:end_line])
    start = sum(len(source_lines[index - 1]) + 1 for index in range(start_line, line_no)) + at
    if segment_text[start:start + len(surface)] != surface:
        raise SystemExit(f"mention offset mismatch: {segment} L{line_no} {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p311-312-note-{len(new_mentions) + 1:04d}",
        "segment_id": segment,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


# Bibliographic and archival mentions in the canonical consolidated note block.
for cid, line, needle in [
    ("cand-9876", 274, "Leben und"), ("cand-9876", 277, "Leben, II, p. 312"),
    ("cand-9877", 274, "Romanin, VID, p. 53"), ("cand-9890", 274, "Romanin"),
    ("cand-9878", 275, "Archivio di Stato"),
    ("cand-9879", 278, "De Brosses, I, p. 142"),
    ("cand-9880", 278, "Letter from Lord Rockingham"),
    ("cand-9881", 279, "It. VU, 480"),
    ("cand-9882", 280, "Haskell, 1956, p. 298"),
    ("cand-9886", 281, "G. A. Moschini, 1924, p. 93"),
    ("cand-9887", 282, "manuscript inventories"),
    ("cand-9888", 282, "Edward Wright, I, p. 78"),
    ("cand-9889", 283, "Morassi, i960"),
]:
    add_mention(cid, NOTES, line, needle)

# The expanded p.312 note 2 is present in the OCR stream at L27-32; L280 is its short citation header.
for cid, line, needle in [
    ("cand-9883", 27, "Keysler, III, p. 296"),
    ("cand-9884", 28, "inventory"),
    ("cand-9885", 32, "Morassi, 1952, pp. 85-91"),
]:
    add_mention(cid, BODY, line, needle)

# Reused people and repository candidates already present elsewhere in the ledger.
for cid, segment, line, needle in [
    ("cand-9436", NOTES, 278, "De Brosses"),
    ("cand-2206", NOTES, 278, "Lord Rockingham"),
    ("cand-0980", NOTES, 278, "Lord Essex"),
    ("cand-5986", NOTES, 278, "British Museum"),
    ("cand-9448", NOTES, 279, "Biblioteca Marciana"),
    ("cand-8578", BODY, 27, "Keysler"),
    ("cand-8257", BODY, 32, "Morassi"),
    ("cand-1709", NOTES, 281, "G. A. Moschini"),
    ("cand-8257", NOTES, 283, "Morassi"),
]:
    add_mention(cid, segment, line, needle)

all_mentions = mentions + new_mentions
mention_ids = {row["mention_id"] for row in all_mentions}

new_statements = []


def span_quote(start_line, end_line, segment=NOTES, start_needle=None, end_needle=None):
    if start_line == end_line and (start_needle or end_needle):
        line = source_lines[start_line - 1]
        start = line.find(start_needle) if start_needle else 0
        end = line.find(end_needle, start) if end_needle else len(line)
        if start < 0 or end < 0:
            raise SystemExit(f"could not locate source quote at L{start_line}")
        return line[start:end].strip()
    return "\n".join(source_lines[start_line - 1:end_line])


def add_statement(sid, segment, subject, object_id, predicate, start_line, end_line, printed_page, physical_page,
                  claim, quote, qualification, mentioned, speaker="Haskell footnote", layer="bibliographic citation", extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement ID already exists: {sid}")
    if segment == NOTES:
        segment_start, segment_end = 273, 349
    else:
        segment_start, segment_end = 17, 32
    if not segment_start <= start_line <= end_line <= segment_end:
        raise SystemExit(f"statement source range outside segment: {sid}")
    if quote not in "\n".join(source_lines[segment_start - 1:segment_end]):
        raise SystemExit(f"statement quote not found in its source segment: {sid}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing subject candidate for {sid}: {subject}")
    if object_id and object_id not in all_candidate_ids:
        raise SystemExit(f"missing object candidate for {sid}: {object_id}")
    mentioned = list(dict.fromkeys(mentioned))
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate for {sid}")
    qualifiers = {
        "source_line_start": start_line,
        "source_line_end": end_line,
        "printed_page": printed_page,
        "pdf_physical_page": physical_page,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": False,
    }
    if extra:
        qualifiers.update(extra)
    row = {
        "statement_id": sid,
        "segment_id": segment,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    }
    new_statements.append(row)


q274 = source_lines[273]
q1 = q274[q274.find("1 The main"):q274.find("2 Romanin")].strip()
q2 = q274[q274.find("2 Romanin"):].strip()
q278 = source_lines[277]
q5 = q278[q278.find("5 De Brosses"):q278.find("Letter from Lord Rockingham")].strip()
q6 = q278[q278.find("Letter from Lord Rockingham"):].strip()
q312n2 = "\n".join(source_lines[26:32])

add_statement("st-chp10-p311-n01-leben-source", NOTES, "cand-2401", "cand-9876", "cites_biographical_source", 274, 274, 311, 40,
              "Haskell identifies Leben und Denkwürdigkeiten as the main source for Schulenburg's life.", q1,
              "The cited 1834 book was not independently consulted; the print title was checked against the OCR transcription.",
              ["cand-2401", "cand-9876"], extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p311-schulenburg-birth-and-origin"], "citations": [{"source_candidate_id": "cand-9876", "year": "1834"}]})
add_statement("st-chp10-p311-n02-romanin-citation", NOTES, "cand-2401", "cand-9877", "cites_venetian_history", 274, 274, 311, 40,
              "Haskell cites Romanin, volume VIII, page 53.", q2,
              "The print reads VIII; the OCR transcription reads VID. The cited passage was not independently consulted.",
              ["cand-2401", "cand-9877", "cand-9890"], extra={"footnote_number": 2, "linked_body_statement_ids": ["st-chp10-p311-venice-honored-schulenburg-with-statue-and-pension"], "citations": [{"source_candidate_id": "cand-9877", "volume": "VIII", "page": "53"}], "ocr_corrections": [{"source_line": 274, "ocr": "VID", "print": "VIII"}]})
add_statement("st-chp10-p311-n03-funeral-drawing-and-itinerary", NOTES, "cand-2401", "cand-9878", "cites_funeral_drawing_and_lists_residences", 275, 276, 311, 40,
              "Haskell cites a drawing of Schulenburg's funeral procession in Verona and lists periods he spent in Venice and Verona.", span_quote(275, 276),
              "The drawing and cited archive were not consulted; the listed periods remain Haskell's note rather than independently verified residence dates.",
              ["cand-2401", "cand-9878", "cand-8681"], extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p311-schulenburg-last-years-and-funeral-at-verona"], "citations": [{"source_candidate_id": "cand-9878", "archive": "Archivio di Stato, VIII, Vari, no. 35"}], "reported_periods": {"Venice": ["1729/30", "1732-1734", "1737-1741"], "Verona": ["1734-1736", "1742-1747"]}})
add_statement("st-chp10-p311-n04-leben-page", NOTES, "cand-2401", "cand-9876", "cites_biographical_source_page", 277, 277, 311, 40,
              "Haskell cites volume II, page 312 of Leben for the passage about Frederick's request for a castrato.", span_quote(277, 277),
              "The cited page was not independently consulted.", ["cand-2401", "cand-9876"], extra={"footnote_number": 4, "linked_body_statement_ids": ["st-chp10-p311-frederick-requested-young-castrato"], "citations": [{"source_candidate_id": "cand-9876", "volume": "II", "page": "312"}]})
add_statement("st-chp10-p311-n05-de-brosses-quotation", NOTES, "cand-9436", "cand-2401", "quoted_description_of_schulenburg", 278, 278, 311, 40,
              "Haskell quotes De Brosses describing Schulenburg as capable in war but poor in morals and recounting his frequent, unheeded sermons about women.", q5,
              "This is a quotation attributed to De Brosses through Haskell; the cited volume and page were not independently consulted.",
              ["cand-9436", "cand-2401", "cand-9879"], speaker="Charles de Brosses, quoted by Haskell", layer="nested quotation in footnote",
              extra={"footnote_number": 5, "linked_body_statement_ids": ["st-chp10-p311-schulenburg-talked-about-women"], "citations": [{"source_candidate_id": "cand-9879", "volume": "I", "page": "142"}]})
add_statement("st-chp10-p311-n06-rockingham-letter", NOTES, "cand-2206", "cand-9880", "cites_correspondence", 278, 278, 311, 40,
              "Haskell cites a letter from Lord Rockingham in Verona to Lord Essex dated 2 February 1733 and gives the British Museum Add. MSS. locator.", q6,
              "The letter and current repository catalogue were not consulted; the shelfmark is recorded as Haskell's locator.",
              ["cand-2206", "cand-0980", "cand-5986", "cand-9880"], extra={"footnote_number": 6, "linked_body_statement_ids": ["st-chp10-p311-schulenburg-questioned-unnamed-nobleman-about-health"], "citations": [{"source_candidate_id": "cand-9880", "repository_candidate_id": "cand-5986", "shelfmark": "Add. MSS. 27,733, f. 13", "date": "1733-02-02"}]})
add_statement("st-chp10-p312-n01-marciana-shelfmark", NOTES, "cand-2401", "cand-9881", "cites_manuscript_shelfmark", 279, 279, 312, 41,
              "P.312 note 1 cites Biblioteca Marciana, It. VII, 480 (7785), cc. 234-264.", span_quote(279, 279),
              "The manuscript and current catalogue were not consulted; the note is retained as a source locator.",
              ["cand-2401", "cand-9448", "cand-9881"], extra={"footnote_number": 1, "linked_body_statement_ids": ["st-chp10-p312-will-maintain-family-noble-status"], "citations": [{"source_candidate_id": "cand-9881", "repository_candidate_id": "cand-9448", "shelfmark": "It. VII, 480 (7785), cc. 234-264"}], "ocr_corrections": [{"source_line": 279, "ocr": "It. VU", "print": "It. VII"}]})
add_statement("st-chp10-p312-n02-corfu-and-collection-sources", BODY, "cand-2401", "cand-9882", "cites_corfu_collection_and_portrait_sources", 27, 32, 312, 41,
              "The p.312 note 2 continuation quotes Keysler on Corfu paintings and a wooden model, transcribes a Canaletto inventory description, notes other Corfu models and pictures, and directs readers to Morassi on Schulenburg portraits.", q312n2,
              "Haskell's citation at canonical note line 280 heads this continuation. Keysler, the inventory, Morassi, and the cited passages were not independently consulted; the p.313 note 3 cross-reference is retained.",
              ["cand-2401", "cand-0525", "cand-8578", "cand-9882", "cand-9883", "cand-9884", "cand-9885", "cand-8257"],
              layer="bibliographic note with nested quotation",
              extra={"footnote_number": 2, "footnote_segment": NOTES, "linked_body_statement_ids": ["st-chp10-p312-canaletto-corfu-view-1726", "st-chp10-p312-puget-relief-and-attributed-paintings"], "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 280, "source_line_end": 280}, {"segment_id": NOTES, "source_line_start": 286, "source_line_end": 286}], "citations": [{"source_candidate_id": "cand-9882", "line": 280, "year": "1956", "page": "298"}, {"source_candidate_id": "cand-9883", "volume": "III", "page": "296"}, {"source_candidate_id": "cand-9884", "work_title": "Inventaire de la Galerie de feu Mgr. le Feldtnarechal Comte de Schulenburg"}, {"source_candidate_id": "cand-9885", "year": "1952", "pages": ["85", "91"]}]})
add_statement("st-chp10-p312-n03-moschini-citation", NOTES, "cand-2401", "cand-9886", "cites_moschini_on_pitteri", 281, 281, 312, 41,
              "P.312 note 3 refers to Moschini's 1924 account of Schulenburg's dealings with Pitteri.", span_quote(281, 281),
              "The cited work and page were not independently consulted.", ["cand-2401", "cand-1709", "cand-9886"], extra={"footnote_number": 3, "linked_body_statement_ids": ["st-chp10-p312-royal-generosity-to-artists"], "citations": [{"source_candidate_id": "cand-9886", "year": "1924", "page": "93"}]})
add_statement("st-chp10-p312-n04-inventories-and-wright", NOTES, "cand-2401", "cand-9887", "cites_collection_inventories_and_wright", 282, 282, 312, 41,
              "P.312 note 4 cites manuscript inventories of Schulenburg's collection from 1724 to 1737 at the Staatsarchiv in Hanover and Edward Wright, volume I, page 78, on the Puget and goods from the Duke of Mantua's collection.", span_quote(282, 282),
              "The manuscripts, Wright's cited page, and archive catalogue were not independently consulted.", ["cand-2401", "cand-2287", "cand-2070", "cand-9887", "cand-9888"], extra={"footnote_number": 4, "linked_body_statement_ids": ["st-chp10-p312-1724-purchase-from-rota", "st-chp10-p312-gonzaga-belongings-venetian-market", "st-chp10-p312-puget-relief-and-attributed-paintings", "st-chp10-p312-works-from-gonzaga-gallery"], "citations": [{"source_candidate_id": "cand-9887", "repository": "Staatsarchiv, Hanover", "date_range": ["1724", "1737"]}, {"source_candidate_id": "cand-9888", "volume": "I", "page": "78"}]})
add_statement("st-chp10-p312-n05-morassi-citation", NOTES, "cand-1245", "cand-9889", "cites_morassi_study", 283, 283, 312, 41,
              "P.312 note 5 cites Morassi, 1960, pages 147-164 and 199-212.", span_quote(283, 283),
              "The print reads note number 5 and year 1960; the OCR reads 8 and i960. The cited pages were not independently consulted.", ["cand-1245", "cand-8257", "cand-9889"], extra={"footnote_number": 5, "linked_body_statement_ids": ["st-chp10-p312-guardi-first-contact-and-tenure"], "citations": [{"source_candidate_id": "cand-9889", "year": "1960", "pages": ["147-164", "199-212"]}], "ocr_corrections": [{"source_line": 283, "ocr_note_number": 8, "print_note_number": 5}, {"source_line": 283, "ocr_year": "i960", "print_year": "1960"}]})

all_statements = statements + new_statements
statement_by_id = {row["statement_id"]: row for row in all_statements}


def add_footnote_ref(statement_id, marker, source_line, note_statement_id):
    row = statement_by_id.get(statement_id)
    if not row:
        raise SystemExit(f"body statement missing: {statement_id}")
    q = row["qualifiers"]
    q["footnote_marker"] = marker
    q["footnote_text_pending"] = False
    q["footnote_segment"] = NOTES
    refs = q.setdefault("footnote_refs", [])
    ref = {"marker": marker, "segment_id": NOTES, "source_line": source_line}
    if ref not in refs:
        refs.append(ref)
    ids = q.setdefault("footnote_statement_ids", [])
    if note_statement_id not in ids:
        ids.append(note_statement_id)
    q["footnote_body_link_status"] = "linked"


for sid, marker, line, note_sid in [
    ("st-chp10-p311-schulenburg-birth-and-origin", 1, 274, "st-chp10-p311-n01-leben-source"),
    ("st-chp10-p311-venice-honored-schulenburg-with-statue-and-pension", 2, 274, "st-chp10-p311-n02-romanin-citation"),
    ("st-chp10-p311-schulenburg-last-years-and-funeral-at-verona", 3, 275, "st-chp10-p311-n03-funeral-drawing-and-itinerary"),
    ("st-chp10-p311-frederick-requested-young-castrato", 4, 277, "st-chp10-p311-n04-leben-page"),
    ("st-chp10-p311-schulenburg-talked-about-women", 5, 278, "st-chp10-p311-n05-de-brosses-quotation"),
    ("st-chp10-p311-schulenburg-questioned-unnamed-nobleman-about-health", 6, 278, "st-chp10-p311-n06-rockingham-letter"),
    ("st-chp10-p312-will-maintain-family-noble-status", 1, 279, "st-chp10-p312-n01-marciana-shelfmark"),
    ("st-chp10-p312-canaletto-corfu-view-1726", 2, 280, "st-chp10-p312-n02-corfu-and-collection-sources"),
    ("st-chp10-p312-royal-generosity-to-artists", 3, 281, "st-chp10-p312-n03-moschini-citation"),
    ("st-chp10-p312-1724-purchase-from-rota", 4, 282, "st-chp10-p312-n04-inventories-and-wright"),
    ("st-chp10-p312-gonzaga-belongings-venetian-market", 4, 282, "st-chp10-p312-n04-inventories-and-wright"),
    ("st-chp10-p312-puget-relief-and-attributed-paintings", 4, 282, "st-chp10-p312-n04-inventories-and-wright"),
    ("st-chp10-p312-works-from-gonzaga-gallery", 4, 282, "st-chp10-p312-n04-inventories-and-wright"),
]:
    add_footnote_ref(sid, marker, line, note_sid)

# The p.312 print has five notes. Correct two OCR-derived false markers and restore the printed marker 5.
portrait_statement = statement_by_id["st-chp10-p312-portrait-sculpture-engraving-artists"]
portrait_q = portrait_statement["qualifiers"]
portrait_q.pop("footnote_marker", None)
portrait_q.pop("footnote_text_pending", None)
portrait_q["qualification"] = "The sentence says 'many others' beyond the named artists. Print comparison confirms no note marker follows this list; the printed note 5 belongs after Guardi's 1745 end date in the next sentence."
portrait_q["ocr_corrections"] = [{"source_line": 20, "prior_s2_marker": 5, "print_marker": "none", "correction": "removed misplaced footnote marker"}]
artist_statement = statement_by_id["st-chp10-p312-employed-artists-recorded-dropsical-features"]
artist_q = artist_statement["qualifiers"]
artist_q.pop("footnote_marker", None)
artist_q.pop("footnote_text_pending", None)
artist_q["qualification"] = "The printed sentence has no footnote marker after 'features'; the prior S2 marker 6 was an OCR carryover and has been removed after comparison with CHP-10.pdf physical page 41."
artist_q["ocr_corrections"] = [{"source_line": 18, "prior_s2_marker": 6, "print_marker": "none", "correction": "removed misplaced footnote marker"}]
guardi_statement = statement_by_id["st-chp10-p312-guardi-first-contact-and-tenure"]
guardi_q = guardi_statement["qualifiers"]
guardi_q["footnote_marker"] = 5
guardi_q["footnote_text_pending"] = True
guardi_q["ocr_corrections"] = [{"source_line": 26, "printed_marker": 5, "ocr_marker_missing": True, "location": "after 1745"}]
add_footnote_ref("st-chp10-p312-guardi-first-contact-and-tenure", 5, 283, "st-chp10-p312-n05-morassi-citation")

# p.311 closes at p.312 L18. P.312's Guardi salary contrast closes at p.313 L73.
previous_continuation = statement_by_id["st-chp10-p312-will-maintain-family-noble-status"]["qualifiers"].get("continuation_of")
next_continuation = statement_by_id["st-chp10-p313-guardi-copyist-role-continuation"]["statement_id"] if "st-chp10-p313-guardi-copyist-role-continuation" in statement_by_id else None
if not previous_continuation or previous_continuation != "st-chp10-p311-will-asserted-authority-no-children":
    raise SystemExit("p.311 will continuation is not linked to p.312")
if not next_continuation or statement_by_id["st-chp10-p312-guardi-salary-and-role-fragment"]["qualifiers"].get("continuation_statement_id") != next_continuation:
    raise SystemExit("p.312 Guardi role continuation to p.313 is not linked")

candidate_rows = candidates + new_candidates
statement_rows = all_statements
if len({row["candidate_id"] for row in candidate_rows}) != len(candidate_rows):
    raise SystemExit("duplicate candidate ID")
if len({row["mention_id"] for row in all_mentions}) != len(all_mentions):
    raise SystemExit("duplicate mention ID")
if len({row["statement_id"] for row in statement_rows}) != len(statement_rows):
    raise SystemExit("duplicate statement ID")
for row in new_mentions:
    if row["candidate_id"] not in {candidate["candidate_id"] for candidate in candidate_rows}:
        raise SystemExit(f"missing mention foreign key: {row['mention_id']}")
for row in new_statements:
    q = row["qualifiers"]
    if any(cid not in {candidate["candidate_id"] for candidate in candidate_rows} for cid in q["mentioned_candidate_ids"]):
        raise SystemExit(f"missing statement mention foreign key: {row['statement_id']}")

coverage[PREVIOUS].update({"migration_status": "complete", "source_line_ranges": "L7-15; p.312 L18", "note": "Printed p.311 notes 1-6 (L274-278) have been recorded and linked. The final will sentence closes at p.312 L18; all six printed footnotes are linked."})
coverage[BODY].update({"migration_status": "complete", "source_line_ranges": "L18-32", "note": "Printed p.312 notes 1-5 are linked. The expanded note 2 at L27-32 is recorded as note text, with its short canonical citation header at L280 cross-referenced. The printed note 5 after Guardi's 1745 date is restored; erroneous OCR-derived markers 5 and 6 on preceding statements are removed. The Guardi role sentence closes at p.313 L73."})
coverage[NOTES].update({"migration_status": "partial", "source_line_ranges": "L274-283; L325-349", "note": "P.311-312 notes L274-283 are reviewed and linked. L325-349 was already processed; the remaining gap is L284-324 (p.313-323 notes), after which this merged note segment can close."})

candidate_rows.sort(key=lambda row: row["candidate_id"])
all_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
print(f"p.311-312 notes preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage changes: p.311 partial->complete; p.312 partial->complete; consolidated notes remain partial")
print(f"totals: {len(candidate_rows)} candidates, {len(all_mentions)} mentions, {len(statement_rows)} statements")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

paths = [candidate_path, mention_path, statement_path, coverage_path]
for path in paths:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in paths:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, all_mentions)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print(f"applied; recovery copies created with suffix {BACKUP_SUFFIX}")
