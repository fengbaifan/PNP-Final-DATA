"""Controlled S2 migration for printed p.330 and consolidated notes L346-349."""
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
PREVIOUS = "chp-10:10_CHP-10_sec_ii:l248-256"
BODY = "chp-10:10_CHP-10_sec_ii:l258-267"
NEXT = "chp-10:10_CHP-10_sec_ii:l269-271"
NOTES = "chp-10:10_CHP-10_sec_ii:l273-349"
MARKDOWN_SHA = "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9"
PDF_SHA = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
BODY_SHA = "e0328eba97f348fd7933a3a0b441d841705e8d14474f2fbc0f7d92f3dc7199c2"
NOTE_SHA = "3bbeddd85c523a4217bcc1640792eb738ce7ed4dc4f18aef00a96d57101e2f52"
BACKUP_SUFFIX = ".bak-s2-chp10-p330-20261003"


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
parser.add_argument("--apply", action="store_true", help="write reviewed p.330 rows after making recovery copies")
args = parser.parse_args()

if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != MARKDOWN_SHA:
    raise SystemExit("canonical source Markdown changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-10 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
body_lines = {n: source_lines[n - 1] for n in range(258, 268)}
note_lines = {n: source_lines[n - 1] for n in range(273, 350)}
segment_text = {
    BODY: "\n".join(body_lines.values()),
    NOTES: "\n".join(note_lines.values()),
}
if hashlib.sha256(segment_text[BODY].encode("utf-8")).hexdigest() != BODY_SHA:
    raise SystemExit("registered source segment changed: p.330")
note_slice = "\n".join(note_lines[n] for n in range(346, 350))
if hashlib.sha256(note_slice.encode("utf-8")).hexdigest() != NOTE_SHA:
    raise SystemExit("registered note range changed: p.330 notes L346-349")
if body_lines[258] != "[Page 330]" or not body_lines[264].endswith("adjoining"):
    raise SystemExit("p.330 source boundaries changed")
if not all(token in note_slice for token in ("Appendix 6", "Canaletto", "Accademia di Disegno", "Haskell and Levey")):
    raise SystemExit("p.330 footnote range L346-349 changed")
if not all(token in segment_text[BODY] for token in ("Thomas Martyn", "Nuova Gazzetta Veneta")):
    raise SystemExit("p.330 footnote continuation in body L265-267 changed")

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
if state != (9837, 9850, 20887, 9288):
    raise SystemExit(f"unexpected table pre-state: {state}")
for sid in (PREVIOUS, BODY, NEXT, NOTES):
    if sid not in coverage:
        raise SystemExit(f"required coverage row missing: {sid}")
if (coverage[PREVIOUS]["disposition"], coverage[PREVIOUS]["migration_status"]) != ("reviewed", "partial"):
    raise SystemExit("p.329 is not reviewed/partial")
if (coverage[BODY]["disposition"], coverage[BODY]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.330 is not queued/pending")
if (coverage[NEXT]["disposition"], coverage[NEXT]["migration_status"]) != ("queued", "pending"):
    raise SystemExit("p.331 is not queued/pending")
if (coverage[NOTES]["disposition"], coverage[NOTES]["migration_status"], coverage[NOTES]["source_line_ranges"]) != ("reviewed", "partial", "L325-345"):
    raise SystemExit("consolidated notes are not in the expected p.324-329 partial state")
if any(row["segment_id"] == BODY for row in mentions) or any(row["segment_id"] == BODY for row in statements):
    raise SystemExit("p.330 body rows already exist")
if any(row["segment_id"] == NOTES and 346 <= int(row.get("qualifiers", {}).get("source_line_start", 0)) <= 349 for row in statements):
    raise SystemExit("p.330 footnote statements already exist")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
for cid in ("cand-0004", "cand-0005", "cand-0041", "cand-0137", "cand-0138", "cand-0140", "cand-0498", "cand-1041", "cand-1053", "cand-1642", "cand-1649", "cand-1699", "cand-1838", "cand-2702", "cand-3151", "cand-3398", "cand-3469", "cand-3678", "cand-4490", "cand-6439", "cand-8587", "cand-8588", "cand-8638", "cand-9735", "cand-9808"):
    if cid not in candidate_by_id:
        raise SystemExit(f"expected existing candidate missing: {cid}")
if candidate_by_id["cand-1642"]["canonical_name"] != "Memmo, Andrea":
    raise SystemExit("expected Andrea Memmo index candidate not found")
if candidate_by_id["cand-1053"]["canonical_name"] != "Foscarini, Marco":
    raise SystemExit("expected Marco Foscarini candidate not found")

new_candidates = []


def add_candidate(cid, name, kind, detail, segment, line):
    if cid in candidate_ids or any(row["candidate_id"] == cid for row in new_candidates):
        raise SystemExit(f"candidate id already exists: {cid}")
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


add_candidate("cand-9851", "Inquisitori alle Arti", "institution", "Venetian body concerned with reorganising guilds; named in Haskell's account of Andrea Memmo. Institutional identity and remit await S3; do not merge with Inquisitori di Stato.", BODY, 260)
add_candidate("cand-9852", "Proposed freedom of liberal-arts practitioners from dues in Memmo's reform queries", "term", "A proposal recorded among Andrea Memmo's preparatory queries; not evidence that dues or taxes were actually waived.", BODY, 260)
add_candidate("cand-9853", "Musicians as a professional group in Memmo's guild-reform queries", "term", "One of the other professions Memmo asks about while considering guild reform; no particular musicians are named.", BODY, 261)
add_candidate("cand-9854", "Engravers as a professional group in Memmo's guild-reform queries", "term", "One of the other professions Memmo asks about while considering guild reform; no particular engravers are named.", BODY, 261)
add_candidate("cand-9855", "Traditional patronage and art's capacity to attract patrons", "term", "Theoretical question discussed at Academy prize-giving sessions: whether traditional patronage was necessary for art to survive, or great art would itself bring patrons. Haskell attributes the second view to Francesco Algarotti.", BODY, 262)
add_candidate("cand-9856", "Piazza S. Marco (art-display location named on p.330)", "place", "A location in Venice where painters displayed work; p.330 identifies the Procuratie Nuove wing but the description continues onto p.331.", BODY, 264)
add_candidate("cand-9857", "Andrea Memmo's preparatory query sheet for a report on guild reorganisation", "archive", "A sheet among Memmo's papers containing brief queries written while preparing a report; Haskell says it is published in full in Appendix 6. The manuscript was not independently consulted and no repository or shelfmark is given here.", BODY, 260)
add_candidate("cand-9858", "Thomas Martyn", "person", "Named as the author of a passage at p.448 cited in Haskell's note on S. Rocco exhibitions; identity is not externally aligned.", BODY, 265)
add_candidate("cand-9859", "A Tour through Italy (Thomas Martyn; new edition, London, [1791])", "archive", "Matched to the local bibliography entry for Thomas Martyn and cited at p.448 in Haskell's note. The work and cited page were not independently consulted.", BODY, 265)
add_candidate("cand-9860", "Nuova Gazzetta Veneta, issue of 21 August 1762", "archive", "Periodical issue cited by Haskell for praise of a portrait of Doge Marco Foscarini. Keep distinct from Gazzetta Veneta and Nuova Veneta Gazzetta candidates pending bibliography and identity review; the issue was not independently consulted.", BODY, 266)
add_candidate("cand-9861", "Unidentified painter named Nassi [possibly Nazari] in a 1762 notice", "person", "Haskell transcribes Signor Nassi and adds sic—Nazari?; preserve this as an unresolved attribution, not a confirmed match to the indexed Bartolommeo Nazari candidates.", BODY, 267)
add_candidate("cand-9862", "Portrait of Doge Marco Foscarini reported in the 1762 Gazzetta", "work", "The notice praises a portrait attributed there to Signor Nassi [sic—Nazari?]. No present location, survival, or secure artist attribution is established.", BODY, 267)
add_candidate("cand-9863", "Papal Nunzio report of 20 August 1729 (Archivio Vaticano—Venezia, n. 180)", "archive", "Haskell quotes the report as a reference to paintings displayed during the occasion; the archival item was not independently consulted.", NOTES, 349)
add_candidate("cand-9864", "Vasari's Life of Montorsoli", "archive", "Work referred to in Memmo's notes and Haskell's note 3 as containing an account of the formation of the Accademia di Disegno in Florence; the text was not independently consulted.", NOTES, 348)
add_candidate("cand-9865", "Signory of Venice (as named in Thomas Martyn's account)", "institution", "The body said to process to the church on S. Rocco's day in Martyn's cited passage; retain the source's term and do not normalize it to the Venetian Senate.", BODY, 265)
add_candidate("cand-9866", "Painters mentioned in reports of S. Rocco exhibitions", "term", "Collective references to present Venetian school painters and other old and living painters in Haskell's cited sources; no individual members are inferred.", BODY, 265)
add_candidate("cand-9867", "Liberal arts as an artist-professional category in Memmo's notes", "term", "The category whose practitioners Memmo discusses in relation to dues and whose imaginative practice he says should not be fettered; keep this occurrence distinct from the 1772 economic argument pending S3.", BODY, 260)

all_candidate_ids = candidate_ids | {row["candidate_id"] for row in new_candidates}
new_mentions = []


def add_mention(segment, line_no, surface, cid, note="", occurrence=0):
    line_map = body_lines if segment == BODY else note_lines
    if segment not in segment_text or cid not in all_candidate_ids:
        raise SystemExit(f"invalid mention segment/candidate: {segment} {surface!r} {cid}")
    line = line_map[line_no]
    starts = []
    cursor = 0
    while True:
        at = line.find(surface, cursor)
        if at < 0:
            break
        starts.append(at)
        cursor = at + 1
    if occurrence >= len(starts):
        raise SystemExit(f"mention text missing at L{line_no}: {surface!r} occurrence {occurrence}")
    first_line = min(line_map)
    start = sum(len(line_map[n]) + 1 for n in range(first_line, line_no)) + starts[occurrence]
    if segment_text[segment][start:start + len(surface)] != surface:
        raise SystemExit(f"mention span mismatch at L{line_no}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch10-p330-{len(new_mentions) + 1:04d}",
        "segment_id": segment,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": start,
        "end_char": start + len(surface),
        "note": note,
    })
    new_mentions.append(row)


# Main text. Existing index/KU candidates are reused where their scope fits.
add_mention(BODY, 259, "Andrea Memmo", "cand-1642")
add_mention(BODY, 260, "Inquisitor! alle Arti", "cand-9851", "OCR reads 'Inquisitor!'; p.330 image reads 'Inquisitori alle Arti'.")
add_mention(BODY, 260, "his papers", "cand-9857", "Reference to a sheet among Memmo's papers, not a claim that the papers were independently consulted.")
add_mention(BODY, 260, "liberal arts", "cand-9867")
add_mention(BODY, 260, "temperament of Painters", "cand-3151", "Memmo's quoted query; do not turn it into a general fact about painters.")
add_mention(BODY, 260, "C.", "cand-0498", "Haskell's note says this almost certainly refers to Canaletto but records a chronology tension; identity remains qualified.")
add_mention(BODY, 260, "subjection of dues", "cand-9852", "Memmo's draft argument proposes freedom from dues; it is not evidence the exemption was implemented.")
add_mention(BODY, 260, "freed from taxes", "cand-9852", "Memmo asks why C. claims tax exemption; this is a question, not evidence an exemption was granted.")
add_mention(BODY, 260, "Rome", "cand-4490")
add_mention(BODY, 260, "Florence", "cand-1041")
add_mention(BODY, 260, "Bologna", "cand-3398")
add_mention(BODY, 260, "Paris", "cand-4653")
add_mention(BODY, 260, "Academy of Arts at Parma", "cand-1838")
add_mention(BODY, 261, "musicians", "cand-9853")
add_mention(BODY, 261, "engravers", "cand-9854")
add_mention(BODY, 261, "Vasari", "cand-2702")
add_mention(BODY, 261, "Montorsoli", "cand-1699")
add_mention(BODY, 261, "Venetian Academy", "cand-0005")
add_mention(BODY, 261, "genius", "cand-9735")
add_mention(BODY, 261, "fine arts", "cand-9867")
add_mention(BODY, 261, "anarchic tendencies in artists", "cand-3585")
add_mention(BODY, 262, "artist", "cand-0140")
add_mention(BODY, 262, "Academy prize-giving sessions", "cand-0005")
add_mention(BODY, 262, "patronage", "cand-9855")
add_mention(BODY, 263, "Francesco\" Algarotti", "cand-0041", "OCR punctuation retained in the surface span; the printed page reads Francesco Algarotti.")
add_mention(BODY, 264, "Venice", "cand-2719")
add_mention(BODY, 264, "art exhibitions", "cand-0137")
add_mention(BODY, 264, "Piazza S. Marco", "cand-9856")
add_mention(BODY, 264, "Procuratie Nuove", "cand-9808")

# The footnote is split: item (i) is in the consolidated note segment; items (ii)-(iii) remain in the body segment.
add_mention(NOTES, 347, "Canaletto", "cand-0498", "Haskell says 'almost certainly' and immediately notes the chronology tension; do not resolve the identity here.")
add_mention(NOTES, 348, "Accademia di Disegno", "cand-0004")
add_mention(NOTES, 348, "Florence", "cand-1041")
add_mention(NOTES, 349, "Haskell and Levey, 1958", "cand-8638", "The local bibliography identifies the cited article, but S2 does not independently consult it.")
add_mention(BODY, 265, "Thomas Martyn", "cand-9858")
add_mention(BODY, 265, "Signory", "cand-9865")
add_mention(BODY, 265, "S. Rocco’s day", "cand-8588")
add_mention(BODY, 265, "painters of the present Venetian school", "cand-9866", "A professional group named in Martyn's quoted account; no membership list is supplied.")
add_mention(BODY, 266, "Scuola", "cand-0138")
add_mention(BODY, 266, "Nuova Gazzetta Veneta", "cand-9860")
add_mention(BODY, 267, "Doge Marco Foscarini", "cand-1053")
add_mention(BODY, 267, "Nassi", "cand-9861", "The printed note adds '[sic—Nazari?]'; retain the uncertainty and do not map to either Bartolommeo Nazari index candidate as a settled identity.")
add_mention(BODY, 267, "Pittori antichi, e viventi", "cand-9866", "The notice praises other old and living painters' works; no individual painters are identified.")

new_mentions.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
for left, right in zip(new_mentions, new_mentions[1:]):
    if left["segment_id"] == right["segment_id"] and int(left["end_char"]) > int(right["start_char"]):
        raise SystemExit(f"overlapping mention spans: {left['mention_id']} and {right['mention_id']}")
if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")

new_statements = []


def add_statement(sid, segment, subject, obj, predicate, start, end, claim, quote,
                  qualification, mentioned, *, speaker="Haskell", layer="authorial narrative", extra=None):
    if sid in statement_ids or any(row["statement_id"] == sid for row in new_statements):
        raise SystemExit(f"statement id already exists: {sid}")
    if quote not in segment_text[segment]:
        raise SystemExit(f"statement quote is not anchored: {sid}")
    if any(cid not in all_candidate_ids for cid in mentioned):
        raise SystemExit(f"missing mentioned candidate in {sid}")
    if subject and subject not in all_candidate_ids:
        raise SystemExit(f"missing subject candidate in {sid}")
    if obj and obj not in all_candidate_ids:
        raise SystemExit(f"missing object candidate in {sid}")
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": 330,
        "pdf_physical_page": 63,
        "claim": claim,
        "speaker": speaker,
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
    }
    if extra:
        qualifiers.update(extra)
    new_statements.append({
        "statement_id": sid,
        "segment_id": segment,
        "subject_candidate_id": subject or None,
        "object_candidate_id": obj or None,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    })


F1 = [{"marker": 1, "segment_id": NOTES, "source_line": 346}]
F2 = [{"marker": 2, "segment_id": NOTES, "source_line": 347}]
F3 = [{"marker": 3, "segment_id": NOTES, "source_line": 348}]
F4 = [
    {"marker": 4, "segment_id": NOTES, "source_line": 349},
    {"marker": 4, "segment_id": BODY, "source_line": 265},
    {"marker": 4, "segment_id": BODY, "source_line": 266},
    {"marker": 4, "segment_id": BODY, "source_line": 267},
]


def body_extra(marker, note_ids):
    refs = {1: F1, 2: F2, 3: F3, 4: F4}[marker]
    return {
        "footnote_marker": marker,
        "footnote_segment": NOTES,
        "footnote_refs": refs,
        "footnote_statement_ids": note_ids,
        "footnote_body_link_status": "linked",
    }


# Close the open artist-status statement from p.329; preserve the p.330-to-p.331 exhibition continuation.
add_statement(
    "st-chp10-p330-status-debate-continuation", BODY, "cand-0140", "cand-0005", "debated_again_with_greater_insight",
    259, 259,
    "Haskell says the status of the artist was debated again, now with greater insight into practical problems.",
    "was debated again, but with much more insight into real problems.",
    "Closes the sentence begun at p.329 L256; the change in debate is Haskell's assessment.",
    ["cand-0140", "cand-0005"],
    extra={"continuation_from_segment_id": PREVIOUS, "continuation_prefix": "Very shortly after the institution of the Academy the position of the artist in society", "continuation_status": "closed"},
)
add_statement(
    "st-chp10-p330-memmo-inquisitori-and-sheet", BODY, "cand-1642", "cand-9851", "served_as_member_of_body_concerned_with_guild_reorganisation",
    259, 260,
    "Haskell identifies Andrea Memmo as one of the Inquisitori alle Arti concerned with guild reorganisation and says a sheet among Memmo's papers records queries prepared for his report.",
    "Andrea Memmo, himself a patron of great interest to be discussed in a later chapter, was one of the\nInquisitor! alle Arti, who were concerned with the reorganisation of the guilds. Among his papers there survives a sheet on which he briefly scribbled some queries to himself when preparing his-report.",
    "The page image reads Inquisitori alle Arti; this is distinct from Inquisitori di Stato. The sheet is known here through Haskell and the internal Appendix 6 reference, not independent archival consultation.",
    ["cand-1642", "cand-9851", "cand-9857"],
    extra={**body_extra(1, ["st-chp10-p330-n01-memmo-sheet-appendix"]), "ocr_corrections": [{"source_line": 260, "ocr": "Inquisitor! alle Arti", "print": "Inquisitori alle Arti"}]},
)
add_statement(
    "st-chp10-p330-memmo-dues-query", BODY, "cand-1642", "cand-9852", "queried_freedom_from_dues_for_liberal_arts_practitioners",
    260, 260,
    "In the quoted preparatory query, Memmo argues that practitioners of the liberal arts should be freed from dues and asks why painter C. claims tax exemption.",
    "It will be necessary’, he begins, ‘to show how important it is for the liberal arts to free from the subjection of dues those men who practise them, and to explain how strange is the temperament of Painters. An example is the famous living Venetian painter C. Why does C. claim to be freed from taxes?",
    "This is a draft query/argument, not evidence that a tax or guild-dues exemption was enacted. Painter C. remains unidentified in S2 because the footnote supplies only a qualified hypothesis and an apparent chronology tension.",
    ["cand-1642", "cand-9852", "cand-9867", "cand-3151", "cand-0498"], speaker="Andrea Memmo as quoted by Haskell", layer="quoted preparatory note",
    extra={"footnote_marker": 2, "footnote_segment": NOTES, "footnote_refs": F2, "footnote_statement_ids": ["st-chp10-p330-n02-canaletto-hypothesis"], "footnote_body_link_status": "linked"},
)
add_statement(
    "st-chp10-p330-reform-comparisons-and-professions", BODY, "cand-1642", None, "considered_comparative_models_and_other_professions_for_reform",
    260, 261,
    "Memmo's queries consider reforms in Rome, Florence, Bologna, Paris and Parma, and ask about musicians and engravers as well as painters.",
    "Memmo looks to other towns for suggestions of reform—Rome, Florence, Bologna and, above all, Paris. What about the new Academy of Arts at Parma? And to other professions.\nWhat about musicians? And engravers?",
    "These are questions and possible models in a preparatory note, not evidence that the reforms were adopted.",
    ["cand-1642", "cand-4490", "cand-1041", "cand-3398", "cand-4653", "cand-1838", "cand-9853", "cand-9854"], speaker="Haskell's account of Memmo's note", layer="reported preparatory queries",
)
add_statement(
    "st-chp10-p330-memmo-vasari-academy-queries", BODY, "cand-1642", "cand-0005", "queried_academy_identity_patron_saint_and_referenced_vasari_life",
    261, 261,
    "Memmo's queries turn to Vasari's life of Montorsoli and ask about the Venetian Academy's device, name and patron saint.",
    "He looks to the past and reminds himself to read Vasari’s life of Montorsoli.3 He even wonders what is the device and the name of the Venetian Academy and whether they could not be improved. Under the protection of which saint is the Academy placed?",
    "The passage reports questions, not a revised emblem/name or an identified patron saint.",
    ["cand-1642", "cand-2702", "cand-1699", "cand-0005", "cand-9851"],
    extra={"footnote_marker": 3, "footnote_segment": NOTES, "footnote_refs": F3, "footnote_statement_ids": ["st-chp10-p330-n03-vasari-life"], "footnote_body_link_status": "linked"},
)
add_statement(
    "st-chp10-p330-memmo-artistic-freedom", BODY, "cand-1642", "cand-9735", "advocated_free_exercise_of_imaginative_side_of_painting",
    261, 261,
    "Memmo concludes that painting's imaginative side should be practised freely and nobly and that genius should not be fettered; Haskell describes him as exceptional among administrators.",
    "And at the end of his remarkably open-minded survey of the situation he concludes: ‘It is right that the imaginative side of painting should be exercised freely and with nobility; genius should not be fettered in the practice of the fine arts. That is why they were called liberal.’ But Memmo, with his interest in the concept of genius and his appreciation of certain anarchic tendencies in artists, was exceptional among administrators, even if his ideas in themselves were not wholly new.",
    "The quotation is attributed to Memmo's note; the subsequent description of his interests and exceptional position is Haskell's characterization.",
    ["cand-1642", "cand-9735", "cand-3151", "cand-3585", "cand-9867"], speaker="Memmo as quoted, followed by Haskell", layer="quotation and authorial evaluation",
)
add_statement(
    "st-chp10-p330-patronage-debate", BODY, "cand-9855", "cand-0041", "framed_alternative_views_on_patronage_and_art",
    262, 263,
    "Haskell says the artist's status remained unchanged and reports a theoretical debate over traditional patronage; Francesco Algarotti maintained that great art itself would bring patrons into being.",
    "The status of the artist remained unchanged, and the only theoretical question that was seriously discussed—particularly at the Academy prize-giving sessions—was whether patronage of the traditional kind was necessary for the survival of art or whether, as\nFrancesco\" Algarotti maintained, the existence of great art would of itself bring patrons into being.",
    "The statement records the debate and Haskell's attribution to Algarotti; it does not assert either position as settled fact.",
    ["cand-0140", "cand-0005", "cand-9855", "cand-0041"],
    extra={"ocr_corrections": [{"source_line": 263, "ocr": "Francesco\" Algarotti", "print": "Francesco Algarotti"}]},
)
add_statement(
    "st-chp10-p330-venetian-exhibition-sites-open", BODY, "cand-0137", "cand-9856", "identified_early_eighteenth_century_art_display_site",
    264, 264,
    "Haskell says two locations in Venice were used for art exhibitions by the early eighteenth century and begins identifying one at Piazza S. Marco beside the Procuratie Nuove.",
    "By the early years of the eighteenth century there were two spots in the city which were given over to art exhibitions.4 In the Piazza S. Marco, by the left-hand projecting wing of the Procuratie Nuove adjoining",
    "The sentence ends mid-description and continues at p.331 L270; only the Piazza S. Marco location is identified in this segment. The accompanying note 4 has three citations split between this segment and the consolidated notes segment.",
    ["cand-0137", "cand-9856", "cand-9808", "cand-8587", "cand-8588"],
    extra={"continuation_to_segment_id": NEXT, "continuation_status": "open", **body_extra(4, ["st-chp10-p330-n04-haskell-levey", "st-chp10-p330-n04-i-nunzio-report", "st-chp10-p330-n04-ii-martyn", "st-chp10-p330-n04-iii-gazzetta"])},
)

# Notes L346-349 and footnote items (ii)-(iii) that S0 retained in the p.330 body segment.
add_statement(
    "st-chp10-p330-n01-memmo-sheet-appendix", NOTES, "cand-9857", "cand-2962", "published_in_full_in_appendix",
    346, 346,
    "Haskell's note says the source sheet is published in full in Appendix 6.",
    note_lines[346],
    "An internal cross-reference; the appendix text itself is not independently consulted in this migration.",
    ["cand-9857", "cand-2962"], speaker="Haskell's note", layer="internal source cross-reference",
    extra={"footnote_marker": 1, "cited_source_independently_consulted": False},
)
add_statement(
    "st-chp10-p330-n02-canaletto-hypothesis", NOTES, "cand-1642", "cand-0498", "qualified_identification_of_painter_c",
    347, 347,
    "Haskell says painter C. almost certainly refers to Canaletto, while noting that Canaletto died in 1768 before Memmo began work.",
    note_lines[347],
    "Preserve Haskell's qualification and the chronology tension; no identity adjudication is made in S2.",
    ["cand-1642", "cand-0498"], speaker="Haskell's note", layer="qualified identification",
    extra={"footnote_marker": 2, "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 347, "ocr": "refers’to", "print": "refers to"}]},
)
add_statement(
    "st-chp10-p330-n03-vasari-life", NOTES, "cand-2702", "cand-9864", "life_contains_account_of_academy_formation",
    348, 348,
    "Haskell's note says the cited Life contains an account of the formation of the Accademia di Disegno in Florence.",
    note_lines[348],
    "The printed word is Life; the OCR reads Lise. The cited text is not independently consulted.",
    ["cand-2702", "cand-1699", "cand-9864", "cand-0004", "cand-1041"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 3, "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 348, "ocr": "Lise", "print": "Life"}]},
)
add_statement(
    "st-chp10-p330-n04-haskell-levey", NOTES, "cand-8638", None, "cited_for_full_discussion_of_s_rocco_exhibitions",
    349, 349,
    "Haskell cites Haskell and Levey (1958), pp.179-185, for a full discussion and says he adds three references discovered after the article was published.",
    "For a full discussion see Haskell and Levey, 1958, pp. 179-85. For the sake of completeness I add here the only three references to the S. Rocco exhibitions that I have discovered since this article was published:",
    "The local bibliography identifies the 1958 article; neither it nor the sources added in the note were independently consulted.",
    ["cand-8638", "cand-8587", "cand-8588"], speaker="Haskell's note", layer="bibliographic citation",
    extra={"footnote_marker": 4, "cited_source_independently_consulted": False},
)
add_statement(
    "st-chp10-p330-n04-i-nunzio-report", NOTES, "cand-9863", "cand-8587", "reported_paintings_displayed_before_crowd",
    349, 349,
    "The cited report says that old and modern painters' works were displayed on the occasion and attracted a large crowd.",
    ".(i) A report from the papal Nunzio of 20 August 1729 in the Archivio Vaticano—Venezia, n. 180: . . . e in tai congiuntura si viddero esposti diversi Quadri di antichi, e moderni Pennelli, con numero concorso di Popolo . . .’.",
    "A quotation transmitted by Haskell's note from an archival report; the report was not independently consulted. The exact exhibition venue is not supplied in this item.",
    ["cand-9863", "cand-8587"], speaker="Papal Nunzio as quoted by Haskell", layer="indirect archival quotation",
    extra={"footnote_marker": 4, "footnote_subitem": "i", "cited_source_independently_consulted": False},
)
martyn_quote = body_lines[265] + "\n" + body_lines[266].split(" (iii)", 1)[0]
add_statement(
    "st-chp10-p330-n04-ii-martyn", BODY, "cand-9859", "cand-8588", "reported_procession_and_painters_exhibition_at_s_rocco",
    265, 266,
    "Thomas Martyn's cited passage says the Signory processed to the church on S. Rocco's day and painters of the present Venetian school exhibited their work in the Scuola.",
    martyn_quote,
    "Haskell cites Martyn, p.448; the book and cited page were not independently consulted. This quotation is an indirect source reference, not a direct observation by Haskell.",
    ["cand-9858", "cand-9859", "cand-9865", "cand-8587", "cand-8588", "cand-0138", "cand-9866"], speaker="Thomas Martyn as quoted by Haskell", layer="indirect printed-source quotation",
    extra={"footnote_marker": 4, "footnote_subitem": "ii", "footnote_body_link_status": "linked", "cited_source_independently_consulted": False},
)
gazzetta_quote = body_lines[266].split("(iii) ", 1)[1] + "\n" + body_lines[267]
add_statement(
    "st-chp10-p330-n04-iii-gazzetta", BODY, "cand-9860", "cand-9862", "reported_praise_of_portrait_and_other_paintings",
    266, 267,
    "The 1762 notice praises a portrait of Doge Marco Foscarini attributed to Signor Nassi [sic—Nazari?] and says other works by old and living painters also received praise.",
    gazzetta_quote,
    "An indirect quotation cited by Haskell; the newspaper issue was not consulted. Preserve the notice's uncertain painter attribution and do not infer the portrait's survival or present location.",
    ["cand-9860", "cand-9862", "cand-1053", "cand-9861", "cand-9866"], speaker="Nuova Gazzetta Veneta as quoted by Haskell", layer="indirect periodical quotation",
    extra={"footnote_marker": 4, "footnote_subitem": "iii", "footnote_body_link_status": "linked", "cited_source_independently_consulted": False, "ocr_corrections": [{"source_line": 266, "ocr": "ku", "print": "fu"}, {"source_line": 267, "ocr": "piu", "print": "più"}]},
)

if any(row["mention_id"] in mention_ids for row in new_mentions):
    raise SystemExit("mention id already exists")
if any(row["statement_id"] in statement_ids for row in new_statements):
    raise SystemExit("statement id already exists")
all_statement_ids = statement_ids | {row["statement_id"] for row in new_statements}
for row in new_statements:
    qualifiers = row.get("qualifiers", {})
    for cid in qualifiers.get("mentioned_candidate_ids", []):
        if cid not in all_candidate_ids:
            raise SystemExit(f"missing mentioned candidate in {row['statement_id']}: {cid}")
    for field in ("subject_candidate_id", "object_candidate_id"):
        cid = row.get(field)
        if cid and cid not in all_candidate_ids:
            raise SystemExit(f"missing {field} in {row['statement_id']}: {cid}")
    for sid in qualifiers.get("footnote_statement_ids", []):
        if sid not in all_statement_ids:
            raise SystemExit(f"dangling footnote statement reference in {row['statement_id']}: {sid}")

previous_statement = next((row for row in statements if row["statement_id"] == "st-chp10-p329-artist-status-debate-open"), None)
if not previous_statement or previous_statement.get("qualifiers", {}).get("continuation_status") != "open":
    raise SystemExit("p.329 artist-status continuation is not open")
previous_statement["qualifiers"].update({
    "continuation_status": "closed",
    "continuation_closed_by_segment_id": BODY,
    "continuation_closed_by_statement_id": "st-chp10-p330-status-debate-continuation",
})

candidate_rows = candidates + new_candidates
mention_rows = mentions + new_mentions
statement_rows = statements + new_statements
coverage_rows[coverage_rows.index(coverage[PREVIOUS])].update({
    "migration_status": "complete",
    "source_line_ranges": "L248-256",
    "note": "p.329 artist-status sentence closes at p.330 L258; p.329 footnotes 1-3 linked.",
})
coverage_rows[coverage_rows.index(coverage[BODY])].update({
    "disposition": "reviewed",
    "migration_status": "partial",
    "source_line_ranges": "L258-267",
    "note": "p.329 sentence closes at p.330 L258; final exhibition sentence continues at p.331 L270; footnote 4 items (ii)-(iii) are retained in body L265-267 and linked with note L349.",
})
coverage_rows[coverage_rows.index(coverage[NOTES])].update({
    "migration_status": "partial",
    "source_line_ranges": "L325-349",
    "note": "p.324-330 footnotes linked; continue with earlier p.312-323 notes L284-324 before closing this merged note segment.",
})
candidate_rows.sort(key=lambda row: row["candidate_id"])
mention_rows.sort(key=lambda row: (row["segment_id"], int(row["start_char"]), int(row["end_char"]), row["mention_id"]))
statement_rows.sort(key=lambda row: row["statement_id"])
coverage_rows.sort(key=lambda row: row["segment_id"])

print(f"p.330 preview: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, +{len(new_statements)} statements")
print("coverage: p.329 complete; p.330 partial to p.331; notes L325-349 partial")
print("footnote 4: note text and item (i) linked from L349; items (ii)-(iii) linked from body L265-267")
if not args.apply:
    print("dry-run only; no files written")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
for path in targets:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"recovery copy already exists: {backup.name}")
for path in targets:
    shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
write_csv(candidate_path, candidate_fields, candidate_rows)
write_csv(mention_path, mention_fields, mention_rows)
write_jsonl(statement_path, statement_rows)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied; four recovery copies saved")
