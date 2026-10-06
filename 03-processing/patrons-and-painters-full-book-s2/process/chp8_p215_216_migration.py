"""Controlled S2 migration for chapter 8 printed pp.215-216 and their notes.

Default invocation performs a read-only preflight.  --apply writes candidates,
mentions, statements, and coverage after checking source fingerprints, exact
spans, quotes, IDs, coverage state, and foreign keys.  S0 remains unchanged.
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
SOURCE_REL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE_FILE = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
P214 = "chp-8:08_CHP-8_sec_ii:l3-9"
P215 = "chp-8:08_CHP-8_sec_ii:l11-19"
P216 = "chp-8:08_CHP-8_sec_ii:l21-35"
NOTES = "chp-8:08_CHP-8_sec_ii:l372-461"
EXPECTED_MAX_CANDIDATE = 7626
BACKUP_SUFFIX = ".bak-s2-chp8-p215-216-20261001"

SEGMENT_EXPECTATIONS = {
    P214: (3, 9, "reviewed", "partial", "L3-6"),
    P215: (11, 19, "queued", "pending", ""),
    P216: (21, 35, "queued", "pending", ""),
    NOTES: (372, 461, "queued", "pending", ""),
}

IDS = {
    "church": "cand-7627",
    "palazzo_ragione": "cand-7628",
    "gothic_portico": "cand-7629",
    "stone_lions": "cand-7630",
    "south_entrance": "cand-7631",
    "campanile": "cand-7632",
    "sacristy": "cand-7633",
    "gothic_frescoes": "cand-7634",
    "altar_paintings": "cand-7635",
    "dome": "cand-7636",
    "stucco": "cand-7637",
    "cavagna_frescoes": "cand-7638",
    "programme": "cand-7639",
    "consiglio": "cand-7640",
    "committee": "cand-7641",
    "central_crossing": "cand-7642",
    "south_transept": "cand-7643",
    "north_transept": "cand-7644",
    "the_levites": "cand-7645",
    "magni_picture": "cand-7646",
    "cocchi_group": "cand-7647",
    "guercino_canvas": "cand-7648",
    "sisera": "cand-7649",
    "sacrifice_isaac": "cand-7650",
    "jacobs_ladder": "cand-7651",
    "murder_cain": "cand-7652",
    "massacre": "cand-7653",
    "pesenti_person": "cand-7654",
    "pesenti_book": "cand-7655",
    "pinetti_person": "cand-7656",
    "pinetti_article": "cand-7657",
    "dora_coggiola": "cand-7658",
    "biblioteca_civica": "cand-7659",
    "cremona": "cand-7660",
    "verona": "cand-7661",
}
EXISTING = {
    "rome": "cand-4490",
    "bergamo": "cand-6208",
    "venice_city": "cand-2719",
    "venice_polity": "cand-6255",
    "milan": "cand-3418",
    "italy": "cand-3461",
    "naples": "cand-3534",
    "giovanni_campione": "cand-0494",
    "ricchini": "cand-2146",
    "cavagna": "cand-0611",
    "storer": "cand-2513",
    "procaccini": "cand-2064",
    "magni": "cand-1493",
    "marquis_mantua": "cand-1525",
    "cocchi": "cand-0792",
    "guercino": "cand-1258",
    "bologna": "cand-1131",
    "padre_massimo": "cand-1576",
    "brusasorci": "cand-0460",
    "capuchins": "cand-3405",
    "paolo_veronese": "cand-2755",
    "veneto": "cand-4207",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


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


candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statement_rows = read_jsonl(statement_path)
segment_rows = read_jsonl(segment_path)
segments = {row["segment_id"]: row for row in segment_rows}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}

source_path = ROOT / SOURCE_REL
source_bytes = source_path.read_bytes()
source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
source_asset_hash = hashlib.sha256(source_bytes).hexdigest()
segment_texts = {}
for segment_id, expected in SEGMENT_EXPECTATIONS.items():
    start, end, disposition, status, ranges = expected
    row = segments.get(segment_id)
    if (not row or row.get("source_file") != SOURCE_FILE
            or (int(row["line_start"]), int(row["line_end"])) != (start, end)):
        raise SystemExit(f"segment metadata changed; review before migration: {segment_id}")
    text = "\n".join(source_lines[start - 1:end])
    if row.get("asset_sha256") != source_asset_hash:
        raise SystemExit(f"source asset fingerprint changed: {SOURCE_REL}")
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != row.get("sha256"):
        raise SystemExit(f"source line-slice hash changed: {segment_id}")
    cov = coverage_by_id.get(segment_id, {})
    actual = (cov.get("disposition"), cov.get("migration_status"), cov.get("source_line_ranges", ""))
    if actual != (disposition, status, ranges):
        raise SystemExit(f"unexpected coverage state for {segment_id}: {actual}")
    segment_texts[segment_id] = text

candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_ids = {row["mention_id"] for row in mention_rows}
statement_ids = {row["statement_id"] for row in statement_rows}
current_max = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows)
if current_max != EXPECTED_MAX_CANDIDATE:
    raise SystemExit(f"candidate sequence changed: expected {EXPECTED_MAX_CANDIDATE}, found {current_max}")
if any(value not in candidate_ids for value in EXISTING.values()):
    raise SystemExit("an expected existing candidate ID is missing")

candidate_specs_raw = [
    ("church", "Santa Maria Maggiore in Bergamo", "place",
     "The church discussed on printed p.215; keep distinct from its spaces, architectural components, and interior works.", P215, 13),
    ("palazzo_ragione", "Palazzo della Ragione, Bergamo", "place",
     "The building faced by the Gothic portico; exact historical building identity is not expanded here.", P215, 13),
    ("gothic_portico", "Gothic portico of Santa Maria Maggiore, Bergamo", "work",
     "The portico Giovanni da Campione is said to have erected in 1355.", P215, 13),
    ("stone_lions", "Pair of stone lions supporting the Gothic portico at Santa Maria Maggiore", "work",
     "Sculptural supports described as two stone lions; authorship is not stated.", P215, 13),
    ("south_entrance", "South entrance of Santa Maria Maggiore, Bergamo", "work",
     "Architectural component said to have been built by Giovanni da Campione a few years after 1355.", P215, 13),
    ("campanile", "Campanile of Santa Maria Maggiore, Bergamo", "place",
     "The church tower completed in 1425.", P215, 13),
    ("sacristy", "Bramantesque sacristy of Santa Maria Maggiore, Bergamo", "place",
     "A sacristy added towards the end of the fifteenth century.", P215, 13),
    ("gothic_frescoes", "Surviving Gothic frescoes in Santa Maria Maggiore, Bergamo", "work",
     "Only traces are reported as remaining.", P215, 13),
    ("altar_paintings", "Altar paintings by local and Venetian artists in Santa Maria Maggiore", "work",
     "An unidentified group said to have appeared from the middle of the sixteenth century.", P215, 13),
    ("dome", "Dome of Santa Maria Maggiore planned by Francesco Maria Ricchini", "work",
     "Architectural component planned in 1612; distinguish it from stucco ornament and frescoes on its interior.", P215, 13),
    ("stucco", "Stucco ornamentation over the interior of the Santa Maria Maggiore dome", "work",
     "Rich stucco decoration described as covering the dome interior.", P215, 13),
    ("cavagna_frescoes", "Angels-and-prophets frescoes in the Santa Maria Maggiore dome", "work",
     "Fresco decoration completed in 1614 by Giampaolo Cavagna with two unnamed local artists.", P215, 15),
    ("programme", "1653 decoration programme for Santa Maria Maggiore, Bergamo", "event",
     "Programme initiated by the church governors; the stated main purpose was to provide pictures for the central crossing.", P215, 17),
    ("consiglio", "Consiglio del Consorzio, governors of Santa Maria Maggiore", "institution",
     "Named church governing body in Haskell's account.", P215, 16),
    ("committee", "Committee appointed by the Consiglio del Consorzio in 1653", "institution",
     "Unnamed committee appointed to order oil paintings for the decoration programme.", P215, 17),
    ("central_crossing", "Central crossing of Santa Maria Maggiore, Bergamo", "place",
     "Interior location for which the 1653 programme primarily sought pictures.", P215, 17),
    ("south_transept", "Southern transept of Santa Maria Maggiore, Bergamo", "place",
     "Interior location for Storer's proposed picture and Padre Massimo's Massacre of the Innocents.", P216, 25),
    ("north_transept", "Northern transept of Santa Maria Maggiore, Bergamo", "place",
     "Interior location whose vault became the next decoration target after the first stage.", P216, 35),
    ("the_levites", "The Levites, painting commissioned from Cristoforo Storer for Santa Maria Maggiore", "work",
     "The subject assigned to one of the thirteen pictures planned for the southern transept; Haskell says it was eventually produced.", P216, 25),
    ("magni_picture", "Unidentified experimental picture commissioned from Pietro Magni for Santa Maria Maggiore", "work",
     "One picture commissioned in 1656 as a trial, with the possibility of a larger commission if it proved satisfactory.", P216, 25),
    ("cocchi_group", "Five unidentified pictures commissioned from Ottavio Cocchi for Santa Maria Maggiore", "work",
     "One proposed picture was accepted in 1657 and Cocchi was subsequently asked for four more; subjects are not given here.", P216, 26),
    ("guercino_canvas", "Projected Guercino canvas for a main door of Santa Maria Maggiore", "work",
     "One of three large canvases; the proposed subject changed from The Story of Esther to Marriage at Cana, and the account says the commission did not appeal to Guercino.", P216, 28),
    ("sisera", "Unidentified painting of The Killing of Sisera for Santa Maria Maggiore", "work",
     "Commissioned from an unnamed artist from Milan or its surroundings.", P216, 33),
    ("sacrifice_isaac", "Unidentified painting of The Sacrifice of Isaac for Santa Maria Maggiore", "work",
     "Commissioned from an unnamed artist from Milan or its surroundings.", P216, 34),
    ("jacobs_ladder", "Unidentified painting of Jacob's Ladder for Santa Maria Maggiore", "work",
     "Commissioned from an unnamed artist from Milan or its surroundings; the S0 OCR reads facob's.", P216, 34),
    ("murder_cain", "Unidentified painting of The Murder of Cain for Santa Maria Maggiore", "work",
     "Commissioned from an unnamed artist from Milan or its surroundings.", P216, 34),
    ("massacre", "Padre Massimo's Massacre of the Innocents for Santa Maria Maggiore", "work",
     "Specific painting for the right wall of the southern transept; keep distinct from the generic subject candidate cand-3488.", P216, 30),
    ("pesenti_person", "P. Pesenti (author cited at p.215 n.1)", "person",
     "The note gives only the surname; the initial and book title are recovered from this volume's bibliography, without expanding the author's identity.", NOTES, 373),
    ("pesenti_book", "La basilica di Santa Maria Maggiore in Bergamo (P. Pesenti, 1938)", "archive",
     "Identified from this volume's bibliography; p.215 n.1 itself cites only Pesenti and gives no page.", NOTES, 373),
    ("pinetti_person", "Angelo Pinetti", "person",
     "Named by Haskell as author of the documentary article used for the Bergamo church discussion.", NOTES, 374),
    ("pinetti_article", "La decorazione pittorica seicentesca di S. Maria Maggiore (Angelo Pinetti, 1916)", "archive",
     "The note identifies Pinetti's article; the article title, venue, and pages are supplied by this volume's bibliography (Bollettino della Civica Biblioteca di Bergamo, 1916, pp.113-142).", NOTES, 374),
    ("dora_coggiola", "Dora Coggiola", "person",
     "Named only in Haskell's acknowledgment; no further identity is inferred.", NOTES, 374),
    ("biblioteca_civica", "Biblioteca Civica, Bergamo (as named in p.215 n.2)", "institution",
     "Institution named in Haskell's acknowledgment; not equated here with a differently styled or fully named library.", NOTES, 374),
    ("cremona", "Cremona (origin indicated by the adjective Cremonese)", "place",
     "Geographic origin of Ottavio Cocchi as described on printed p.216.", P216, 25),
    ("verona", "Verona (origin indicated by the adjective Veronese)", "place",
     "Geographic origin associated with Brusasorci on printed p.216.", P216, 31),
]

candidate_specs = []
for key, name, kind, detail, segment_id, line in candidate_specs_raw:
    candidate_specs.append({
        "candidate_id": IDS[key],
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
        "candidate_source_ref": f"{segment_id}#L{line}",
    })

if [int(row["candidate_id"].split("-")[1]) for row in candidate_specs] != list(range(EXPECTED_MAX_CANDIDATE + 1, EXPECTED_MAX_CANDIDATE + 1 + len(candidate_specs))):
    raise SystemExit("new candidate IDs are not a consecutive append after the current maximum")
new_candidate_ids = {row["candidate_id"] for row in candidate_specs}
if len(new_candidate_ids) != len(candidate_specs) or candidate_ids & new_candidate_ids:
    raise SystemExit("duplicate candidate ID in migration")

mention_specs = [
    (P215, 12, "Rome", EXISTING["rome"], "City named in the account of painters who went there."),
    (P215, 13, "Santa Maria Maggiore", IDS["church"], "Church discussed in the Bergamo architectural history."),
    (P215, 13, "Bergamo", EXISTING["bergamo"], "Location of the church."),
    (P215, 13, "Giovanni da Campione", EXISTING["giovanni_campione"], "Architect named for the portico and later south entrance."),
    (P215, 13, "Gothic portico", IDS["gothic_portico"], "Architectural component erected in 1355."),
    (P215, 13, "two stone lions", IDS["stone_lions"], "Sculptural supports described for the portico."),
    (P215, 13, "Palazzo della Ragione", IDS["palazzo_ragione"], "Building faced by the portico."),
    (P215, 13, "entrance to the south", IDS["south_entrance"], "Architectural component built a few years after the portico."),
    (P215, 13, "campanile", IDS["campanile"], "Church tower completed in 1425."),
    (P215, 13, "sacristy", IDS["sacristy"], "Bramantesque sacristy added late in the fifteenth century."),
    (P215, 13, "Gothic frescoes", IDS["gothic_frescoes"], "Only traces are said to remain."),
    (P215, 13, "Altar paintings", IDS["altar_paintings"], "Unidentified group of works."),
    (P215, 13, "Venetian", EXISTING["venice_city"], "Regional adjective for artists; linked to Venice as a cultural source."),
    (P215, 13, "stucco ornamentation", IDS["stucco"], "Interior decorative work on the dome."),
    (P215, 13, "dome", IDS["dome"], "Architectural component planned by Ricchini."),
    (P215, 13, "Milanese", EXISTING["milan"], "Regional adjective for architect Ricchini."),
    (P215, 14, "Francesco Maria Ricchini", EXISTING["ricchini"], "Architect named as planner of the dome."),
    (P215, 14, "Giampaolo\nCavagna", EXISTING["cavagna"], "Name spans an OCR line break; candidate records the artist.", 15),
    (P215, 14, "Bcrgamasque", EXISTING["bergamo"], "OCR adjective for the painter's regional association; printed as Bergamasque."),
    (P215, 15, "frescoes of angels and prophets", IDS["cavagna_frescoes"], "Subject of the dome fresco decoration completed in 1614."),
    (P215, 16, "Consiglio del\nConsorzio", IDS["consiglio"], "Named governing body; name spans a line break.", 17),
    (P215, 17, "the governors of the church", IDS["consiglio"], "Appositional description of the Consiglio del Consorzio."),
    (P215, 17, "programme of decoration", IDS["programme"], "1653 project decided by the church governors."),
    (P215, 17, "central crossing", IDS["central_crossing"], "Main location the programme intended to supply with pictures."),
    (P215, 17, "A committee", IDS["committee"], "Unnamed committee appointed to order oil paintings."),
    (P215, 18, "the committee", IDS["committee"], "Committee facing the scale and difficulty of the task."),
    (P215, 19, "Bergamasque", EXISTING["bergamo"], "Regional adjective for artists of Bergamo."),
    (P215, 19, "Bergamo", EXISTING["bergamo"], "City described in relation to Venice and Milan."),
    (P215, 19, "Venice", EXISTING["venice_polity"], "Political entity in the statement that it ruled Bergamo."),
    (P215, 19, "Milan", EXISTING["milan"], "Nearby city and source of artistic culture."),
    (P215, 19, "Italy", EXISTING["italy"], "Extent of the subsequent negotiations."),
    (P216, 23, "Cristoforo Storer", EXISTING["storer"], "Swiss artist selected first by the committee."),
    (P216, 23, "Milanese", EXISTING["milan"], "Regional adjective for Ercole Procaccini."),
    (P216, 24, "Ercole Proccaccini", EXISTING["procaccini"], "S0 spelling retained in the mention; candidate uses the index spelling Procaccini."),
    (P216, 24, "Bergamo", EXISTING["bergamo"], "City whose leading families had previous contacts with Storer."),
    (P216, 25, "southern transept", IDS["south_transept"], "Church location for the thirteen-picture scheme."),
    (P216, 25, "The Levites", IDS["the_levites"], "Subject of Storer's painting."),
    (P216, 25, "the committee", IDS["committee"], "Committee considering a quicker fresco alternative."),
    (P216, 25, "the church", IDS["church"], "Destination of the proposed commission."),
    (P216, 25, "Neapolitan", EXISTING["naples"], "Regional adjective for Pietro Magni."),
    (P216, 25, "Pietro Magni", EXISTING["magni"], "Painter commissioned for an experimental picture."),
    (P216, 25, "Marquis of Mantua", EXISTING["marquis_mantua"], "Patron for whom Magni was then working."),
    (P216, 25, "Cremonese", IDS["cremona"], "Regional adjective for Ottavio Cocchi."),
    (P216, 25, "Ottavio\nCocchi", EXISTING["cocchi"], "Name spans an OCR line break.", 26),
    (P216, 27, "cominittee", IDS["committee"], "S0 OCR spelling; page image reads committee."),
    (P216, 27, "one of the three very large canvases", IDS["guercino_canvas"], "One intended work among the three described."),
    (P216, 28, "Guercino", EXISTING["guercino"], "Artist selected unanimously for the proposed canvas."),
    (P216, 28, "Bologna", EXISTING["bologna"], "City to which the messenger was sent."),
    (P216, 28, "The\nStory of Esther", IDS["guercino_canvas"], "First proposed subject for the same projected canvas.", 29),
    (P216, 29, "Marriage at Cana", IDS["guercino_canvas"], "Revised proposed subject; not the separate Chicago painting candidate."),
    (P216, 29, "Guercino", EXISTING["guercino"], "Artist whose response Haskell qualifies as seeming lack of interest."),
    (P216, 30, "The committee", IDS["committee"], "Committee responding after the Guercino approach failed."),
    (P216, 30, "Massacre of the Innocents", IDS["massacre"], "Specific painting commissioned for the southern transept wall."),
    (P216, 30, "southern transept", IDS["south_transept"], "Location for the Massacre painting."),
    (P216, 30, "Capuchin", EXISTING["capuchins"], "Order to which Padre Massimo belonged."),
    (P216, 31, "Brusasorci", EXISTING["brusasorci"], "Artist described as the Veronese master of Padre Massimo."),
    (P216, 31, "Veronese", IDS["verona"], "Regional adjective for Brusasorci."),
    (P216, 31, "Paolo Veronese", EXISTING["paolo_veronese"], "Artist whose work is invoked in Haskell's evaluation."),
    (P216, 31, "Padre Massimo", EXISTING["padre_massimo"], "First name occurrence in the request to release him temporarily."),
    (P216, 32, "Capuchins", EXISTING["capuchins"], "Order asked to release Padre Massimo temporarily."),
    (P216, 32, "Padre Massimo", EXISTING["padre_massimo"], "Painter asked to settle in Bergamo temporarily."),
    (P216, 31, "Veneto", EXISTING["veneto"], "Region where Haskell says Padre Massimo had already painted altar pictures."),
    (P216, 33, "Bergamo", EXISTING["bergamo"], "City where Padre Massimo was asked to work."),
    (P216, 33, "Milan", EXISTING["milan"], "City and surrounding area from which other artists were commissioned."),
    (P216, 33, "The Killing of Sisera", IDS["sisera"], "One of four titled paintings commissioned from unnamed artists."),
    (P216, 33, "The\nSacrifice of Isaac", IDS["sacrifice_isaac"], "One of four titled paintings commissioned from unnamed artists.", 34),
    (P216, 34, "facob’s Ladder", IDS["jacobs_ladder"], "S0 OCR form; the print reads Jacob's Ladder."),
    (P216, 34, "the Murder of Cain", IDS["murder_cain"], "One of four titled paintings commissioned from unnamed artists."),
    (P216, 35, "northern transept", IDS["north_transept"], "Location of the next decoration phase."),
    (NOTES, 373, "Pesenti", IDS["pesenti_person"], "Surname-only source in the note; resolved to the bibliography entry without expanding the name."),
    (NOTES, 374, "Angelo Pinetti", IDS["pinetti_person"], "Author named in the documentary-source note."),
    (NOTES, 374, "Pinetti", IDS["pinetti_person"], "Second reference to the same author in the note."),
    (NOTES, 374, "Dora Coggiola", IDS["dora_coggiola"], "Research acknowledgment; no further identity inferred."),
    (NOTES, 374, "Biblioteca Cívica", IDS["biblioteca_civica"], "Library named in the acknowledgment."),
    (NOTES, 374, "Bergamo", EXISTING["bergamo"], "City given for the Biblioteca Cívica."),
]


def mention_row(index, spec):
    segment_id, line_no, surface, candidate_id, note, *tail = spec
    segment = segments[segment_id]
    local_lines = segment_texts[segment_id].split("\n")
    first = int(segment["line_start"])
    line_index = line_no - first
    end_line = int(tail[0]) if tail else line_no
    end_index = end_line - first
    if line_index < 0 or line_index >= len(local_lines):
        raise SystemExit(f"mention line is outside segment: {segment_id} L{line_no}")
    if end_index < line_index or end_index >= len(local_lines):
        raise SystemExit(f"mention end line is outside segment: {segment_id} L{end_line}")
    prefix = "\n".join(local_lines[:line_index])
    base = len(prefix) + (1 if line_index else 0)
    through_end = "\n".join(local_lines[:end_index + 1])
    limit = len(through_end) + (1 if end_index + 1 < len(local_lines) else 0)
    start = segment_texts[segment_id].find(surface, base, limit)
    if start < 0:
        raise SystemExit(f"mention span mismatch: {segment_id} L{line_no}: {surface!r}")
    end = start + len(surface)
    text = segment_texts[segment_id]
    if text[start:end] != surface:
        raise SystemExit(f"mention span mismatch: {segment_id} L{line_no}: {surface!r}")
    return {
        "mention_id": f"m-chp8-s2-p215-216-{index:03d}",
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": start,
        "end_char": end,
        "note": note,
    }


new_mentions = [mention_row(i, spec) for i, spec in enumerate(mention_specs, 1)]
new_mention_ids = {row["mention_id"] for row in new_mentions}
if len(new_mention_ids) != len(new_mentions) or mention_ids & new_mention_ids:
    raise SystemExit("duplicate mention ID in migration")


def stmt(statement_id, segment_id, start, end, page, pdf_page, predicate, claim,
         qualification, quote, mentioned=(), subject=None, obj=None, footnote_marker=None,
         text_layer="body", extra=None):
    source_quote = "\n".join(source_lines[start - 1:end])
    if " ".join(quote.split()) not in " ".join(source_quote.split()):
        raise SystemExit(f"statement quote not found in cited source lines: {statement_id}")
    qualifiers = {
        "source_line_start": start,
        "source_line_end": end,
        "printed_page": page,
        "pdf_physical_page": pdf_page,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(mentioned),
    }
    if footnote_marker is not None:
        qualifiers["footnote_marker"] = footnote_marker
    if extra:
        qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": SOURCE_FILE,
    }


stmts = [
    stmt("st-chp8-p215-provincial-collections-neglect-roman-painting", P215, 12, 12, 215, 13,
         "provincial_collections_neglect_roman_painting",
         "Haskell identifies the neglect of Roman painting as a distinctive aspect of these provincial collections.",
         "Evaluative authorial synthesis; the preceding phrase begins in p.214 L6 and is completed here.",
         "aspect of these collections lies in their neglect of Roman painting.",
         mentioned=[IDS["church"], EXISTING["rome"]],
         extra={"continuation_from": f"{P214}#L6"}),
    stmt("st-chp8-p215-classicising-institutions-outside-rome", P215, 12, 12, 215, 13,
         "classicising_doctrines_and_institutions_absent_from_remote_places",
         "Haskell says that classicising doctrines and institutions which paralysed or boycotted many Rome-going painters were absent in remote cities, where different canons of appreciation could grow.",
         "Preserve the author's causal framing and the qualification that it concerns many, not all, painters.",
         "The classicising doctrines and institutions that paralysed or boycotted so many of those painters who actually went to Rome were not to be found in these out-of-the-way places, and a taste could thus growup in them based on very different canons of appreciation.",
         mentioned=[EXISTING["rome"]],
         extra={"ocr_corrections": [
             {"source_file": SOURCE_FILE, "source_line": 12, "ocr": "growup", "print": "grow up",
              "basis": "CHP-8.pdf physical page 13."}]}),
    stmt("st-chp8-p215-collections-estimated-frequency", P215, 12, 12, 215, 13,
         "provincial_collections_frequency_estimate",
         "Haskell says such collections were probably few, while judging that there must have been more than the few recorded.",
         "Retain probably and the author's inference; this is not a count.",
         "It is true that these collections were probably not many—though they obviously must have been far more than the few that are here recorded",
         extra={"qualification_terms": ["probably", "obviously must have been"]}),
    stmt("st-chp8-p215-one-collection-influential", P215, 12, 12, 215, 13,
         "provincial_collection_influence",
         "Haskell says that at least one such collection was highly influential.",
         "At least one; the passage does not identify the collection in this sentence.",
         "but in at least one case they were highly influential.",
         extra={"qualification_terms": ["at least one"]}),
    stmt("st-chp8-p215-patronage-mechanism-and-roman-values", P215, 12, 12, 215, 13,
         "unusual_patronage_mechanism",
         "Haskell presents the collections' development as evidence for an unusual and intrinsically interesting patronage mechanism that mattered to his argument about the demolition of Roman values.",
         "Haskell's interpretive framing; do not turn demolition of Roman values into an independently verified event.",
         "Moreover, the history of their development shows us the mechanism of an unusual type of patronage which is of great intrinsic interest and of some importance in the demolition of Roman values.",
         extra={"qualification_terms": ["some importance"], "text_layer": "authorial interpretation"}),
    stmt("st-chp8-p215-church-work-began-1137", P215, 13, 13, 215, 13,
         "church_construction_history",
         "Haskell dates work on Santa Maria Maggiore in Bergamo to 1137 and says it continued fitfully over following centuries.",
         "The note marker 1 points to Pesenti; the citation is recorded separately and was not independently checked.",
         "Work on the church of Santa Maria Maggiore in Bergamo began in 1137, and continued fitfully over the next few centuries.",
         mentioned=[IDS["church"], EXISTING["bergamo"]],
         subject=IDS["church"], footnote_marker=1),
    stmt("st-chp8-p215-campione-portico-and-south-entrance", P215, 13, 13, 215, 13,
         "architectural_construction",
         "Haskell says Giovanni da Campione erected the Gothic portico in 1355 and built the more restrained south entrance a few years later.",
         "The passage distinguishes the portico from the later entrance; the exact interval is not specified.",
         "In 1355 Giovanni da Campione erected the delicate but richly ornamented Gothic portico supported on two stone lions which faces the Palazzo della Ragione, and a few years later he also built the rather more restrained entrance to the south.",
         mentioned=[EXISTING["giovanni_campione"], IDS["gothic_portico"], IDS["stone_lions"],
                    IDS["palazzo_ragione"], IDS["south_entrance"], EXISTING["bergamo"]],
         subject=EXISTING["giovanni_campione"], obj=IDS["gothic_portico"]),
    stmt("st-chp8-p215-renaissance-campanile-sacristy", P215, 13, 13, 215, 13,
         "church_architectural_additions",
         "Haskell describes Renaissance additions, completion of the campanile in 1425, and a late-fifteenth-century Bramantesque sacristy that obscured the original plan.",
         "Chronology and Haskell's judgment about the effect on reading the original plan are retained.",
         "The Renaissance brought further additions to this essentially Romanesque structure. In 1425, after nearly three centuries, the campanile was completed, and towards the end of the century a sacristy in the new Bramantesque style made it still harder to appreciate the original plan.",
         mentioned=[IDS["church"], IDS["campanile"], IDS["sacristy"]]),
    stmt("st-chp8-p215-interior-decoration-and-ricchini-dome", P215, 13, 14, 215, 13,
         "church_interior_decoration_history",
         "Haskell says the interior changed substantially: traces of Gothic frescoes remained, altar paintings by local and Venetian artists appeared from the mid-sixteenth century, and stucco covered the interior of a dome planned by Ricchini in 1612.",
         "Keep the group descriptions unresolved; distinguish the dome, its stucco ornament, and the altar paintings. Ricchini's design is a report in the book, not independently verified.",
         "The successive modifications of the interior were far more drastic. Traces of Gothic frescoes still remain, but from the middle of the sixteenth century the whole decoration was changed. Altar paintings by local and Venetian artists began to appear, and rich and heavy stucco ornamentation crept over the interior of the dome which was planned by the Milanese architect\nFrancesco Maria Ricchini in 1612.",
         mentioned=[IDS["church"], IDS["gothic_frescoes"], IDS["altar_paintings"], IDS["stucco"], IDS["dome"],
                    EXISTING["venice_city"], EXISTING["milan"], EXISTING["ricchini"]],
         subject=EXISTING["ricchini"], obj=IDS["dome"]),
    stmt("st-chp8-p215-cavagna-dome-frescoes-1614", P215, 14, 15, 215, 13,
         "fresco_decoration_completion",
         "Haskell says Giampaolo Cavagna and two unnamed local artists completed angels-and-prophets frescoes for the dome in 1614.",
         "The two collaborators remain unnamed; the S0 adjective Bcrgamasque is corrected to Bergamasque only in S2.",
         "Two years later the Bcrgamasque painter Giampaolo\nCavagna, helped by two other local artists, completed the decoration of the dome with frescoes of angels and prophets.",
         mentioned=[EXISTING["cavagna"], EXISTING["bergamo"], IDS["cavagna_frescoes"], IDS["dome"]],
         subject=EXISTING["cavagna"], obj=IDS["cavagna_frescoes"],
         extra={"ocr_corrections": [
             {"source_file": SOURCE_FILE, "source_line": 14, "ocr": "Bcrgamasque", "print": "Bergamasque",
              "basis": "CHP-8.pdf physical page 13."}]}),
    stmt("st-chp8-p215-interior-mid-century-spectacle", P215, 16, 16, 215, 13,
         "church_interior_appearance_by_mid_seventeenth_century",
         "Haskell says the church interior must by mid-seventeenth century have presented a confusing spectacle because incomplete decoration from several periods competed for attention.",
         "Must already is Haskell's inference; it is not a direct inventory of the room.",
         "Thus by the middle of the seventeenth century the interior must already have presented a confusing spectacle with the spasmodic and incomplete decoration of several very different periods competing for attention.",
         mentioned=[IDS["church"]], extra={"qualification_terms": ["must already"]}),
    stmt("st-chp8-p215-1653-decoration-programme", P215, 16, 17, 215, 13,
         "decoration_programme_initiated",
         "Haskell says the Consiglio del Consorzio decided in 1653 to begin an extensive decoration programme, mainly to provide pictures for the church's central crossing.",
         "The source calls the Consorzio governors of the church; this does not establish a modern legal identity for the body.",
         "It was in 1653 that the Consiglio del\nConsorzio, the governors of the church, decided to embark on an extensive programme of decoration, whose main purpose was to provide pictures for the central crossing of the church.",
         mentioned=[IDS["consiglio"], IDS["programme"], IDS["central_crossing"], IDS["church"]],
         subject=IDS["consiglio"], obj=IDS["programme"]),
    stmt("st-chp8-p215-committee-orders-oil-paintings", P215, 17, 17, 215, 13,
         "committee_appointed_to_order_paintings",
         "A committee was appointed to order oil paintings according to its considered judgment.",
         "This is the committee's quoted charge; the passage does not identify its members or establish that the paintings were all produced.",
         "A committee was appointed ‘to order oil paintings in the manner that should seem most suitable to their considered judgement’.",
         mentioned=[IDS["committee"], IDS["programme"]],
         subject=IDS["consiglio"], obj=IDS["committee"], footnote_marker=2,
         extra={"quotation_speaker": "appointment record as quoted by Haskell"}),
    stmt("st-chp8-p215-local-capacity-and-foreign-commission", P215, 18, 19, 215, 13,
         "local_artists_assessed_below_required_calibre",
         "Haskell says the committee judged that Bergamo no longer had artists of the required calibre and that the commission would have to go to a foreigner.",
         "Reported committee assessment, not an objective ranking of all Bergamasque artists.",
         "It was clear that there were no longer any Bergamasque artists of the calibre required and that the commission would have to be given to a foreigner.",
         mentioned=[EXISTING["bergamo"], IDS["committee"]]),
    stmt("st-chp8-p215-bergamo-venice-milan-context", P215, 19, 19, 215, 13,
         "bergamo_political_and_artistic_context",
         "Haskell says Venice had ruled Bergamo since 1430, that Bergamo lay thirty miles from Milan, and that its artistic culture reflected both associated centres.",
         "In the political clause Venice denotes the ruling polity; the later reference to two cities is geographical/cultural. The source's distance is retained as reported.",
         "Bergamo had been ruled by Venice since 1430, but it lies only thirty miles from Milan. Its artistic culture reflected those of the two cities with which it was so closely associated",
         mentioned=[EXISTING["venice_polity"], EXISTING["bergamo"], EXISTING["milan"]],
         subject=EXISTING["venice_polity"], obj=EXISTING["bergamo"],
         extra={"date_or_period": "since 1430", "venice_city_candidate_id": EXISTING["venice_city"]}),
    stmt("st-chp8-p215-negotiations-follow-relative-failure", P215, 19, 19, 215, 13,
         "negotiations_followed_relative_failure",
         "After the committee's relative failure, Haskell says negotiations spread to towns across Italy.",
         "The sentence continues with the outcome at p.216 L22; that continuation is recorded under its own source segment with its antecedent resolved here.",
         "Their relative failure led to a complicated series of negotiations in towns all over Italy",
         mentioned=[IDS["committee"], EXISTING["italy"]],
         extra={"continuation_in": f"{P216}#L22"}),
    stmt("st-chp8-p216-negotiations-outcome", P216, 22, 22, 216, 14,
         "negotiations_outcome_and_historical_impression",
         "Haskell says the negotiations produced no real masterpieces and few pictures of great value, but give historians an engrossing view of the difficulties faced by a persistent small-town patron.",
         "The demonstrative these refers to negotiations named at p.215 L19; preserve Haskell's evaluative language.",
         "these led to no real masterpieces and few pictures of any great value they give the historian an enthralling impression of the difficulties that faced a persistent patron in a small town.",
         mentioned=[IDS["committee"], EXISTING["bergamo"]],
         extra={"anaphora_resolution": {"surface": "these", "antecedent": f"{P215}#L19 negotiations"}}),
    stmt("st-chp8-p216-storer-selection-and-background", P216, 23, 24, 216, 14,
         "artist_selection_and_training",
         "The committee's first choice was Cristoforo Storer, described as Swiss, a pupil of Ercole Proccaccini of Milan, and already closely connected with leading Bergamo families.",
         "The source supplies no names for the Bergamo families; retain its printed Proccaccini form in the quotation and map the mention to the existing Procaccini candidate.",
         "Their first choice fell on a Swiss artist, Cristoforo Storer, a pupil of the Milanese\nErcole Proccaccini, who had already had close contacts with leading families in Bergamo.",
         mentioned=[IDS["committee"], EXISTING["storer"], EXISTING["procaccini"], EXISTING["milan"], EXISTING["bergamo"]]),
    stmt("st-chp8-p216-storer-the-levites-commission", P216, 25, 25, 216, 14,
         "painting_commission",
         "In February 1654 Storer was commissioned for one of thirteen pictures planned for the southern transept vault and lunettes; the assigned subject was The Levites, and Haskell says the picture was eventually produced.",
         "The count and location belong to the scheme; no present-day location or condition of the painting is asserted.",
         "In February 1654 he was commissioned to paint one of the thirteen pictures to be embedded in the stucco of the vault and lunettes above the cornice of the southern transept. The subject given was The Levites, and though the picture was eventually produced",
         mentioned=[EXISTING["storer"], IDS["the_levites"], IDS["south_transept"]],
         subject=EXISTING["storer"], obj=IDS["the_levites"]),
    stmt("st-chp8-p216-storer-delay-and-assessment-visit", P216, 25, 25, 216, 14,
         "commission_delay_and_alternative_assessment",
         "Haskell says Storer's delay led the committee to consider a quicker fresco scheme by April 1655; a few months later two committee members inspected frescoes at an unnamed local aristocrat's country house to assess an unnamed artist.",
         "Neither the aristocrat nor the painter is named; the visit is an assessment, not a commission.",
         "the artist’s dilatoriness caused the first of the many long delays which the committee had to suffer, so that by April 1655 they were considering changing their original scheme and having the vault frescoed as a quicker alternative. Indeed a few months later they sent two of their members to die country house of a local aristocrat to look at some frescoes he had had painted there and to decide whether or not the artist concerned would prove suitable for the church.",
         mentioned=[EXISTING["storer"], IDS["committee"], IDS["church"]],
         extra={"ocr_corrections": [
             {"source_file": SOURCE_FILE, "source_line": 25, "ocr": "die country house", "print": "the country house",
              "basis": "CHP-8.pdf physical page 14."}]}),
    stmt("st-chp8-p216-magni-experimental-commission", P216, 25, 25, 216, 14,
         "experimental_painting_commission",
         "In 1656 the committee returned to its original plan and commissioned Pietro Magni, then working for the Marquis of Mantua, to make one experimental picture, with a larger commission conditional on satisfaction.",
         "The source says evidently it did not prove satisfactory; it does not name an independent evaluator.",
         "However, they soon returned to the original plan, and in 1656 they commissioned a Neapolitan painter, Pietro Magni, who was then working for the Marquis of Mantua, to produce one picture for the site as an experiment, with the possibility, should it prove satisfactory, of being given the whole job.",
         mentioned=[IDS["committee"], EXISTING["magni"], EXISTING["marquis_mantua"], IDS["magni_picture"]],
         subject=IDS["committee"], obj=IDS["magni_picture"]),
    stmt("st-chp8-p216-cocchi-five-pictures", P216, 25, 26, 216, 14,
         "painting_commissions_offered_to_cocchi",
         "After the Magni experiment apparently failed, the Cremonese Ottavio Cocchi offered in January 1657 to paint one picture; the committee accepted and later asked him for four more.",
         "The statement that the commission was attractive to comparatively minor artists is Haskell's interpretation, not a status classification assigned by this project.",
         "Evidently it did not—for when in January 1657 a Cremonese painter, Ottavio\nCocchi, offered on his own initiative to paint one of the pictures, his proposal was accepted and he was subsequently asked to paint four more. It was clear that the commission was an attractive one to comparatively minor artists.",
         mentioned=[IDS["committee"], EXISTING["magni"], EXISTING["cocchi"], IDS["cocchi_group"], IDS["cremona"]]),
    stmt("st-chp8-p216-guercino-proposed-door-canvas", P216, 27, 29, 216, 14,
         "unsuccessful_approach_for_large_canvas",
         "In the same year the committee unanimously selected Guercino for one of three large canvases above the main doors and sent a messenger to Bologna; the subject changed from The Story of Esther to Marriage at Cana, but Haskell says the overloaded artist seems to have had no interest.",
         "The projected canvas is not represented as executed; preserve seems and do not confuse this proposal with the separate Marriage at Cana candidate reported at p.204.",
         "Meanwhile in the same year the cominittee began looking around for a suitable painter for one of the three very large canvases to be placed above the main doors of the church. After a unanimous vote it was decided that the task should be given to Guercino and a messenger was sent to him in Bologna. The subject chosen was The\nStory of Esther, but a few months later this was changed to the Marriage at Cana. Guercino, however, was already overwhelmed with commissions and this one seems to have made no appeal to him.",
         mentioned=[IDS["committee"], EXISTING["guercino"], IDS["guercino_canvas"], EXISTING["bologna"]],
         subject=IDS["committee"], obj=IDS["guercino_canvas"],
         extra={"qualification_terms": ["seems", "one of three", "subject changed"],
                "ocr_corrections": [
                    {"source_file": SOURCE_FILE, "source_line": 27, "ocr": "cominittee", "print": "committee",
                     "basis": "CHP-8.pdf physical page 14."},
                    {"source_file": SOURCE_FILE, "source_line": 29, "ocr": " - .", "print": "",
                     "basis": "CHP-8.pdf physical page 14."}]}),
    stmt("st-chp8-p216-padre-massimo-massacre-commission", P216, 30, 31, 216, 14,
         "painting_commission_after_guercino_declined",
         "After the Guercino approach failed, the committee commissioned Padre Massimo's Massacre of the Innocents for the right wall of the southern transept; he was a Capuchin pupil of Brusasorci and had painted altar pictures in the Veneto.",
         "The attribution and career description are Haskell's report; the regional adjective Veronese is linked to Verona, not treated as a separate artist.",
         "The committee’s one attempt to move outside the limited range of local talent and employ an artist of international fame had thus met with no success. They put as good a face on this as they could and ‘tó the full satisfaction not just of the Magnifico Consiglio del Consorzio but of the whole city’ they commissioned a Massacre of the Innocents, to be placed in the right wall of the southern transept, from a Capuchin pupil of the Veronese Brusasorci, Padre Massimo, a man who had already painted a number of altar pictures in the Veneto.",
         mentioned=[IDS["committee"], EXISTING["guercino"], IDS["massacre"], IDS["south_transept"],
                    EXISTING["capuchins"], EXISTING["brusasorci"], IDS["verona"], EXISTING["padre_massimo"],
                    EXISTING["veneto"], EXISTING["bergamo"]],
         subject=EXISTING["padre_massimo"], obj=IDS["massacre"],
         extra={"ocr_corrections": [
             {"source_file": SOURCE_FILE, "source_line": 30, "ocr": "tó the", "print": "to the",
              "basis": "CHP-8.pdf physical page 14."}]}),
    stmt("st-chp8-p216-massimo-response-and-no-further-work", P216, 31, 33, 216, 14,
         "painting_reception_and_unrealized_further_work",
         "Haskell describes the Massacre as a vigorous and efficient reworking of Paolo Veronese, says the governors were pleased, and reports that they unsuccessfully sought temporary leave for Padre Massimo to paint more in Bergamo.",
         "The style judgment is Haskell's. The requested leave did not result in the stated further work; the proposed continuation should not be represented as completed.",
         "So pleased were they with the work—a vigorous and efficient rehash of Paolo Veronese—that, with the promise-of lavish alms, they implored the\nCapuchins to give temporary leave to Padre Massimo and allow him to settle in\nBergamo to paint further pictures. But this too came to nothing.",
         mentioned=[IDS["massacre"], EXISTING["paolo_veronese"], IDS["consiglio"], EXISTING["capuchins"],
                    EXISTING["padre_massimo"], EXISTING["bergamo"]],
         extra={"ocr_corrections": [
             {"source_file": SOURCE_REL, "source_line": 31, "ocr": "promise-of", "print": "promise of",
              "basis": "CHP-8.pdf physical page 14."}]}),
    stmt("st-chp8-p216-milan-pictures-first-stage-complete", P216, 33, 34, 216, 14,
         "four_paintings_commissioned_and_first_stage_complete",
         "Other artists from Milan and its surroundings were commissioned for four named paintings, and Haskell says the first stage of the decoration was complete by 1659.",
         "The artists are unnamed; no authorship is assigned to the four works.",
         "Instead, other artists from Milan and its surroundings were commissioned to paint The Killing of Sisera, The\nSacrifice of Isaac, facob’s Ladder and the Murder of Cain. By 1659 the first stage in the decoration was complete.",
         mentioned=[EXISTING["milan"], IDS["sisera"], IDS["sacrifice_isaac"], IDS["jacobs_ladder"], IDS["murder_cain"]],
         extra={"ocr_corrections": [
             {"source_file": SOURCE_FILE, "source_line": 34, "ocr": "facob’s Ladder", "print": "Jacob’s Ladder",
              "basis": "CHP-8.pdf physical page 14."}]}),
    stmt("st-chp8-p216-next-north-transept-phase-open", P216, 35, 35, 216, 14,
         "next_decoration_phase_begins",
         "After the first stage, the committee turned to the northern transept vault; the number and plan of its paintings continue on p.217.",
         "The sentence ends at the word thirteen in this source segment and remains open until p.217 L70.",
         "The committee now turned to the vault of the northern transept, where thirteen",
         mentioned=[IDS["committee"], IDS["north_transept"]],
         extra={"continuation_in": "chp-8:08_CHP-8_sec_ii:l69-76#L70"}),
    stmt("st-chp8-p215-pesenti-church-citation", NOTES, 373, 373, 215, 13,
         "footnote_citation",
         "Haskell cites Pesenti for the history of work on Santa Maria Maggiore in Bergamo.",
         "The note gives only a surname and no page; the bibliography identifies P. Pesenti's 1938 book. The cited book was not independently consulted.",
         "1 Pesenti.",
         mentioned=[IDS["pesenti_person"], IDS["pesenti_book"], IDS["church"]],
         obj=IDS["pesenti_book"], footnote_marker=1, text_layer="footnote",
         extra={"linked_statement_ids": ["st-chp8-p215-church-work-began-1137"],
                "bibliography_source": "02-sources/02-Markdown/21_CHP-21Bibliography.md#L948"}),
    stmt("st-chp8-p215-pinetti-document-source-note", NOTES, 374, 374, 215, 13,
         "documentary_source_and_interpretation_note",
         "Haskell says that unless otherwise indicated the documents discussed here come from Angelo Pinetti's 1916 article, while the interpretation is his own though he followed Pinetti closely.",
         "The note's here is limited to this local documentary discussion; it does not make the cited article an independently checked source for every claim in the section.",
         "2 Unless specially indicated, all die documents here are taken from the very full article by Angelo Pinetti, 1916. The interpretation put on these documents is naturally my own, though it will be seen that I have followed Pinetti closely.",
         mentioned=[IDS["pinetti_person"], IDS["pinetti_article"]],
         obj=IDS["pinetti_article"], footnote_marker=2, text_layer="footnote",
         extra={"bibliography_source": "02-sources/02-Markdown/21_CHP-21Bibliography.md#L959-L961",
                "ocr_corrections": [
                    {"source_file": SOURCE_FILE, "source_line": 374, "ocr": "die documents", "print": "the documents",
                     "basis": "CHP-8.pdf physical page 13."}]}),
    stmt("st-chp8-p215-dora-coggiola-acknowledgment", NOTES, 374, 374, 215, 13,
         "author_research_acknowledgment",
         "Haskell thanks Dora Coggiola of the Biblioteca Civica in Bergamo for her help.",
         "Record as an acknowledgment only; it does not establish Coggiola's occupation or a fuller institutional name.",
         "I am most grateful to Signorina Dora Coggiola of the Biblioteca Cívica, Bergamo, for her great help.",
         mentioned=[IDS["dora_coggiola"], IDS["biblioteca_civica"], EXISTING["bergamo"]],
         obj=IDS["dora_coggiola"], footnote_marker=2, text_layer="footnote"),
]

new_statement_ids = {row["statement_id"] for row in stmts}
if len(new_statement_ids) != len(stmts) or statement_ids & new_statement_ids:
    raise SystemExit("duplicate statement ID in migration")
for row in stmts:
    for endpoint in ("subject_candidate_id", "object_candidate_id"):
        value = row[endpoint]
        if value and value not in candidate_ids | new_candidate_ids:
            raise SystemExit(f"{row['statement_id']}: unknown {endpoint} {value}")
    for candidate_id in row["qualifiers"].get("mentioned_candidate_ids", []):
        if candidate_id not in candidate_ids | new_candidate_ids:
            raise SystemExit(f"{row['statement_id']}: unknown mentioned candidate {candidate_id}")

# Correct the earlier p.214 statement so its quote does not absorb the start
# of the following sentence, which closes on this page.
PREVIOUS_STATEMENT = "st-chp8-sec-ii-intro-younger-painters"
previous = next((row for row in statement_rows if row.get("statement_id") == PREVIOUS_STATEMENT), None)
if not previous or previous["segment_id"] != P214:
    raise SystemExit(f"previous p.214 statement changed: {PREVIOUS_STATEMENT}")
old_quote = previous["original_quote"]
tail = " Indeed, the most striking"
if tail in old_quote:
    previous["original_quote"] = old_quote.replace(tail, "", 1)
elif "those men such as Crespi, Solimena, Sebastiano Ricci and others who had declined to visit or to remain in Rome." not in old_quote:
    raise SystemExit("p.214 younger-painters quote no longer contains the expected sentence fragment")
previous["qualifiers"]["qualification"] = (
    "Keep the traveller's scenario modal (might have found); do not assign each named painter to every city. "
    "The following sentence begins with the fragment Indeed, the most striking at p.214 L6 and is analyzed "
    "with its continuation at p.215 L12 under a separate statement."
)

coverage_updates = {
    P214: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-6",
        "note": "L3-6 read against CHP-8.pdf physical p.12. L6 ends with the fragment 'Indeed, the most striking'; the sentence is analyzed with its continuation at p.215 L12 under a separate statement. L7 is p.214 note 2, present only in the p.214 visual transcription; L8-9 repeat the end of note 4, whose opening is in sec_i L157 and completion in that visual transcription. Reuse without duplicate mentions or statements. S0 'Don Antonio Russo' is corrected to printed Ruffo only in S2 qualifiers."
    },
    P215: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L12-19",
        "note": "L11 is the printed-page navigation marker; prose L12-19 was read against CHP-8.pdf physical p.13. L12 closes p.214's opening fragment and is recorded as a separate statement; L19's negotiations clause is linked to its outcome at p.216 L22. p.215 notes 1-2 were read at the bottom of physical p.13 and migrated from the footnote segment L373-374. S2-only OCR corrections: growup/grow up and Bcrgamasque/Bergamasque. S0 remains unchanged."
    },
    P216: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L22-35",
        "note": "L21 is the printed-page navigation marker; prose L22-35 was read against CHP-8.pdf physical p.14. L22 resolves the negotiations reference from p.215 L19. L35 ends at 'thirteen' and continues at p.217 L70, so coverage remains partial. S2-only OCR corrections: die/the, cominittee/committee, tó/to, promise-of/promise of, and facob's/Jacob's. S0 remains unchanged."
    },
    NOTES: {
        "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L373-374",
        "note": "Reviewed p.215 footnotes 1-2 only (physical p.13), with the citation and source-method note linked to their body statements. L372 is a generated footnote heading; L375-461 remain unreviewed and queued within this composite notes segment. Pinetti and Pesenti titles are identified from the book bibliography, not independently read."
    },
}
for segment_id, update in coverage_updates.items():
    row = coverage_by_id[segment_id]
    row.update(update)

if not set(coverage_updates).issubset(coverage_by_id):
    raise SystemExit("a target coverage row is missing")

all_candidate_ids = candidate_ids | new_candidate_ids
all_statement_ids = statement_ids | new_statement_ids
for row in stmts:
    for linked_id in row["qualifiers"].get("linked_statement_ids", []):
        if linked_id not in all_statement_ids:
            raise SystemExit(f"{row['statement_id']}: unknown linked statement {linked_id}")

print(f"source: {SOURCE_REL}; SHA256={source_asset_hash}")
print(f"new candidates: {len(candidate_specs)} ({candidate_specs[0]['candidate_id']} through {candidate_specs[-1]['candidate_id']})")
print(f"new mentions: {len(new_mentions)}")
print(f"new statements: {len(stmts)}")
print("coverage changes:")
for segment_id, update in coverage_updates.items():
    print(f"  {segment_id}: {update['disposition']}/{update['migration_status']} {update['source_line_ranges']}")
print("quote/span preflight: passed")
print("foreign-key and ID preflight: passed")

def apply():
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    if any(path.exists() for path in backups):
        raise SystemExit(f"recovery backup already exists for suffix {BACKUP_SUFFIX}; inspect before applying")
    for source, backup in zip(paths, backups):
        shutil.copy2(source, backup)
    updated_candidates = candidate_rows + candidate_specs
    updated_mentions = mention_rows + new_mentions
    updated_statements = statement_rows + stmts
    updated_coverage = [coverage_by_id.get(row["segment_id"], row) for row in coverage_rows]
    write_csv_atomic(candidate_path, candidate_fields, updated_candidates)
    write_csv_atomic(mention_path, mention_fields, updated_mentions)
    write_jsonl_atomic(statement_path, updated_statements)
    write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
    print("APPLIED: four S2 tables written with recovery backups.")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write after all preflight checks pass")
args = parser.parse_args()
if args.apply:
    apply()
else:
    print("DRY RUN: no S2 table files written")
