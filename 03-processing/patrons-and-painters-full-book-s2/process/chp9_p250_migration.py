"""Controlled S2 migration for printed page 250; default is a read-only dry run."""
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
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
P249 = "chp-9:09_CHP-9_intro:l77-88"
P250 = "chp-9:09_CHP-9_intro:l90-104"
P251 = "chp-9:09_CHP-9_intro:l106-114"
NOTES = "chp-9:09_CHP-9_intro:l323-445"
EXPECTED_HASH = "166b580e0d98274a4cef63638b625bce87aa307685138b9f311f4eba9d1f992d"
EXPECTED_ASSET_HASH = "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3"
BACKUP_SUFFIX = ".bak-s2-chp9-p250-20261001"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(stream.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(stream.name)
    tmp.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
for sid in (P249, P250, P251, NOTES):
    if sid not in segment_by_id:
        raise SystemExit(f"missing segment metadata: {sid}")
meta = segment_by_id[P250]
if meta["sha256"] != EXPECTED_HASH or meta["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("source segment or asset hash changed; inspect before migration")
asset = ROOT / meta["source_file"]
if hashlib.sha256(asset.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("source asset hash changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
selected = source_lines[meta["line_start"] - 1:meta["line_end"]]
if hashlib.sha256("\n".join(selected).encode("utf-8")).hexdigest() != EXPECTED_HASH:
    raise SystemExit("p.250 text changed; inspect before migration")
line_offsets = {}
offset = 0
for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), selected):
    line_offsets[line_no] = offset
    offset += len(line) + 1

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage}
expected_states = {
    P249: ("reviewed", "partial", "L77-88"),
    P250: ("queued", "pending", ""),
    P251: ("queued", "pending", ""),
    NOTES: ("queued", "pending", ""),
}
for sid, state in expected_states.items():
    row = coverage_by_id.get(sid)
    if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != state:
        raise SystemExit(f"unexpected coverage for {sid}: {row}")

candidate_ids = {row["candidate_id"] for row in candidates}
if len(candidate_ids) != len(candidates) or max(int(cid.split("-")[1]) for cid in candidate_ids) != 8183:
    raise SystemExit("candidate inventory changed; inspect before allocating IDs")
candidate_specs = [
    (8184, "Carmini area, Venice", "place", 92, "Location named as the site of the Zenobio palace; the precise spatial referent is not further specified."),
    (8185, "Twelve Apostolic families of Venice", "term", 92, "Haskell's collective name for the twelve oldest Venetian families; keep as a social grouping, not a literal apostolic entity."),
    (8186, "Mythological fresco cycle at the Zenobio palace", "work", 92, "A series of spectacular mythological frescoes commissioned for the Zenobio palace; individual scenes are not named here."),
    (8187, "Painted architectural framework of the Zenobio frescoes", "work", 92, "Heavy, elaborate painted framework containing the mythological fresco series."),
    (8188, "Bolognese type of painted architectural framework", "term", 92, "Stylistic/design category used for the fresco framework."),
    (8189, "Carraccesque nude figures", "term", 92, "Figure type described as part of the painted framework; no individual figure is identified."),
    (8190, "Carinthia", "place", 94, "Region named as the Widmann family's place of origin."),
    (8191, "Romantic landscape series by Luca Carlevarijs at the Zenobio palace", "work", 93, "Series of views inserted into frames along the corridor leading to the Salone."),
    (8192, "Corridor leading to the Salone in the Zenobio palace", "place", 93, "Interior passage where Carlevarijs's framed landscapes were installed."),
    (8193, "Salone of the Zenobio palace", "place", 93, "Named hall at the end of the corridor in which the landscapes were installed."),
    (8194, "Ceiling painting of Ceres and Bacchus at the Zenobio palace", "work", 93, "Ceiling decoration attributed in the text to Gregorio Lazzarini."),
    (8195, "Ceres", "person", 93, "Mythological figure named as a subject of the Zenobio palace ceiling painting."),
    (8196, "Scipio Africanus", "person", 94, "Historical figure whose life supplied subjects for the Widmann canvases."),
    (8197, "Widmann palace canvases with scenes from the life of Scipio Africanus", "work", 94, "A series of large canvases by Gregorio Lazzarini in the Widmann palace."),
    (8198, "Church of San Canciano in Venice", "place", 94, "Landmark used to locate the Widmann palace; the source abbreviates it as S. Canciano."),
    (8199, "Bagnoli di Sopra", "place", 94, "Location of the Widmann country house."),
    (8200, "Diana and Actaeon frescoes at the Widmann country house", "work", 94, "Frescoes attributed to Louis Dorigny at Bagnoli di Sopra; distinct from other Diana-and-Actaeon works."),
    (8201, "Labia Palace, Venice", "place", 95, "Large palace built by the Labia family in Venice; no more specific palace name is supplied here."),
    (8202, "Catalonia", "place", 95, "Broad region implied by the Labia family's described Catalan origin; no more precise origin is given."),
    (8203, "S. Gerolamo nel Deserto", "work", 97, "Picture title as recorded in the 1749 Labia inventory; exact surviving object is not identified."),
    (8204, "La Notte (Labia inventory picture)", "work", 97, "Inventory title for a Labia picture; do not merge with other works titled or themed Night."),
    (8205, "Il Giudicio di Paride", "work", 98, "Picture title as transcribed in the Labia inventory; no object-level identification is supplied."),
    (8206, "Tre Animali", "work", 99, "Inventory title for a picture; composition and present identity remain unspecified."),
    (8207, "Architettura (Labia inventory picture)", "work", 100, "Inventory title for a picture; no composition details are supplied."),
    (8208, "Un trionfo d'armi", "work", 100, "Inventory title printed as 'Un trionfo d'armi'; the page OCR misreads 'trionfo' as 'trionso'."),
    (8209, "Battaria di Cusina", "work", 101, "Inventory title retained as printed; exact subject and object identity remain open."),
    (8210, "Quadi [sic], fatti della Sacra Scrittura", "work", 102, "Inventory entry explicitly marked [sic] by Haskell; retain the printed spelling rather than silently normalizing it."),
    (8211, "4 Dissegni con Cristallo", "work", 103, "Inventory entry for four drawings with crystal; object identities are not supplied."),
    (8212, "Job and his Wife (Cochin title)", "work", 104, "Picture identified by Cochin; its mapping to one inventory number is not supplied."),
    (8213, "Isaac blessing Jacob (Cochin title)", "work", 104, "Picture identified by Cochin; its mapping to one inventory number is not supplied."),
    (8214, "Sonates (Cochin reference)", "work", 104, "Unidentified picture referred to by Cochin using the term 'Sonates'; retain the uncertain source wording."),
    (8215, "St Peter receiving the Keys (Cochin reference)", "work", 104, "Picture mentioned by Cochin; no artist, inventory number, or surviving object is identified here."),
    (8216, "Pastoral picture with shepherds (Cochin reference)", "work", 104, "Picture described in Cochin's French phrase about shepherds and sheep; no title or object identity is given."),
]
existing_keys = {(row["canonical_name"], row["suggested_type"]) for row in candidates}
for number, name, kind, line_no, detail in candidate_specs:
    cid = f"cand-{number:04d}"
    if cid in candidate_ids or (name, kind) in existing_keys:
        raise SystemExit(f"candidate ID or natural-key collision: {cid} {name}")
    candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name, "index_page_range": "",
        "suggested_type": kind, "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": detail, "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{P250}#L{line_no}",
    })
    candidate_ids.add(cid)

existing_mention_ids = {row["mention_id"] for row in mentions}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mentions}
new_mentions = []


def mention(line_no, suffix, cid, surface, note="", occurrence=0):
    mid = f"m-chp9-p250-{suffix}"
    if mid in existing_mention_ids:
        raise SystemExit(f"duplicate mention ID: {mid}")
    line = source_lines[line_no - 1]
    start_at = 0
    pos = -1
    for _ in range(occurrence + 1):
        pos = line.find(surface, start_at)
        if pos < 0:
            raise SystemExit(f"surface not found at L{line_no}: {surface!r}")
        start_at = pos + len(surface)
    start = line_offsets[line_no] + pos
    end = start + len(surface)
    span = (P250, str(start), str(end))
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {mid}")
    if cid not in candidate_ids:
        raise SystemExit(f"missing candidate for mention: {mid} -> {cid}")
    new_mentions.append({"mention_id": mid, "segment_id": P250, "candidate_id": cid,
                         "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note})


MENTION_SPECS = [
    (91, "newly-ennobled-families", "cand-8134", "four or five families", "Unnamed families ennobled about fifty years before the early eighteenth century."),
    (91, "artistic-patronage", "cand-2720", "artistic patronage", "Venetian art patronage as the role in which these families were prominent."),
    (91, "venice", "cand-2719", "Venice", "City and artistic-patronage setting."),
    (92, "zenobio-family", "cand-2870", "The Zenobio", "Zenobio family; the claim about wealth is reported as hearsay."),
    (92, "city", "cand-2719", "the city", "Venice from the immediate context."),
    (92, "zenobio-palace", "cand-2871", "The palace", "Zenobio palace indexed at p.250."),
    (92, "carmini", "cand-8184", "the Carmini", "Place-name kept distinct from Scuola Grande dei Carmini."),
    (92, "morosini-family", "cand-1706", "the Morosini", "Morosini family from which the Zenobio bought the palace."),
    (92, "twelve-oldest-families", "cand-8185", "the twelve oldest families", "Collective group called the Apostles parenthetically."),
    (92, "apostles", "cand-8185", "the socalled Apostles", "OCR span; print has 'the so-called Apostles'."),
    (92, "dorigny", "cand-0944", "Dorigny", "Louis Dorigny index candidate reused."),
    (92, "mythological-frescoes", "cand-8186", "a series of spectacular mythological frescoes", "Unspecified fresco cycle at the Zenobio palace."),
    (92, "painted-framework", "cand-8187", "painted architectural framework", "Architectural painting around the frescoes."),
    (92, "bolognese-type", "cand-8188", "the Bolognese type", "Stylistic framework type."),
    (92, "carraccesque-nudes", "cand-8189", "Carraccesque nudes", "Stylistic description of the nude figures."),
    (92, "palazzo-farnese", "cand-0999", "the Palazzo Farnese", "Roman palace used as the source/comparison for the framework."),
    (92, "rome", "cand-4490", "Rome", "City location of Palazzo Farnese."),
    (93, "carlevarijs", "cand-0554", "Luca Carlevarijs", "Page-250 index candidate reused."),
    (93, "zenobio-palace-carlevarijs", "cand-2871", "the palace", "Zenobio palace."),
    (93, "landscape-series", "cand-8191", "a series of romantic landscapes", "Carlevarijs's series for the palace."),
    (93, "corridor", "cand-8192", "the corridor", "Specific palace corridor leading to the Salone."),
    (93, "salone", "cand-8193", "the Salone", "Named interior hall in the Zenobio palace."),
    (93, "lazzarini", "cand-1368", "Lazzarini", "Gregorio Lazzarini index candidate reused."),
    (93, "ceres-bacchus-work", "cand-8194", "a ceiling with Ceres and Bacchus", "Ceiling painting in the Zenobio palace."),
    (93, "ceres", "cand-8195", "Ceres", "Mythological subject of the ceiling painting."),
    (93, "bacchus", "cand-7814", "Bacchus", "Mythological subject of the ceiling painting."),
    (93, "tiepolo", "cand-2569", "Tiepolo", "Giambattista Tiepolo index candidate reused."),
    (93, "zenobio-family-coreference", "cand-2870", "them", "Coreference to the Zenobio family."),
    (94, "widmann-family", "cand-2812", "The Widmann", "Widmann family candidate reused."),
    (94, "carinthia", "cand-8190", "Carinthian", "Regional origin descriptor; no more precise origin is given."),
    (94, "widmann-palace", "cand-2813", "palace", "Widmann palace indexed at p.250."),
    (94, "s-canciano", "cand-8198", "S. Canciano", "Church landmark locating the Widmann palace."),
    (94, "widmann-canvas-series", "cand-8197", "a series of large canvases", "Scipio Africanus scenes by Lazzarini."),
    (94, "lazzarini-widmann", "cand-1368", "Lazzarini", "Gregorio Lazzarini."),
    (94, "scipio-africanus", "cand-8196", "Scipio Africanus", "Historical subject of the canvas series."),
    (94, "widmann-country-house", "cand-2811", "their country house", "Widmann country house candidate reused."),
    (94, "bagnoli", "cand-8199", "Bagnoli di Sopra", "Country-house location."),
    (94, "dorigny-widmann-house", "cand-0944", "Dorigny", "Louis Dorigny."),
    (94, "diana-actaeon-frescoes", "cand-8200", "frescoes of Diana and Actaeon", "Work group at the Widmann country house, separate from the Pitti cycle."),
    (94, "diana", "cand-4136", "Diana", "Mythological subject."),
    (94, "actaeon", "cand-7995", "Actaeon", "Mythological figure; reuse its identity, not the distinct Pitti artwork."),
    (95, "labia-family", "cand-1349", "The Labia", "Labia family candidate reused."),
    (95, "catalan-origin", "cand-8202", "Catalan origin", "Broad regional origin description; no specific town is named."),
    (95, "labia-palace", "cand-8201", "a gigantic palace", "Labia family palace in Venice."),
    (95, "lazzarini-labia", "cand-1368", "Lazzarini", "Gregorio Lazzarini."),
    (96, "venice-collection", "cand-2719", "Venice", "City in which the picture collection was held and Giordano's visit took place."),
    (95, "labia-collection", "cand-1348", "the largest collection", "Labia collection; described comparatively by Haskell."),
    (96, "giordano", "cand-1182", "Luca Giordano", "Index candidate explicitly scoped to paintings in the Labia collection."),
    (97, "gerolamo-desert", "cand-8203", "S. Gerolamo nel Deserto", "Inventory picture title; exact object identity is not given."),
    (97, "la-notte", "cand-8204", "La Notte", "Inventory title; do not merge with other Night pictures."),
    (98, "giudicio-paride", "cand-8205", "Il Giudicio di Paride", "Inventory picture title."),
    (99, "tre-animali", "cand-8206", "Tre Animali", "Inventory picture title."),
    (100, "architettura", "cand-8207", "Architettura", "Inventory picture title."),
    (100, "trionfo-armi", "cand-8208", "Un trionso d'armi", "OCR span; printed title is 'Un trionfo d'armi'."),
    (101, "battaria-cusina", "cand-8209", "Battaria di Cusina", "Inventory title retained as printed."),
    (102, "quadi-sic", "cand-8210", "Quadi [sic]", "Haskell's explicitly sic-marked inventory entry."),
    (103, "dissegni-cristallo", "cand-8211", "4 Dissegni con Cristallo", "Inventory entry for four drawings with crystal."),
    (104, "cochin", "cand-0793", "Cochin", "Charles-Nicolas Cochin index candidate reused."),
    (104, "job-wife", "cand-8212", "Job and his Wife", "Cochin title, not mapped to a numbered inventory entry."),
    (104, "isaac-jacob", "cand-8213", "Isaac blessing Jacob", "Cochin title, not mapped to a numbered inventory entry."),
    (104, "sonates", "cand-8214", "a Sonates", "Ambiguous work reference retained in Cochin's wording."),
    (104, "st-peter-keys-work", "cand-8215", "a St Peter receiving the Keys", "Unidentified picture mentioned by Cochin."),
    (104, "st-peter", "cand-4231", "St Peter", "Subject of the picture mentioned by Cochin."),
    (104, "pastoral-picture", "cand-8216", "a picture", "Cochin's additional picture described by its shepherds-and-sheep subject."),
]
for spec in MENTION_SPECS:
    mention(*spec)


def quote(first, last):
    return "\n".join(source_lines[first - 1:last])


def statement(sid, first, last, subject, obj, predicate, claim, qualification, mentioned,
              marker=None, note_start=None, note_end=None, text_layer="body", extras=None):
    q = {"source_line_start": first, "source_line_end": last, "printed_page": 250,
         "pdf_physical_page": 12, "claim": claim, "speaker": "Haskell", "text_layer": text_layer,
         "qualification": qualification, "mentioned_candidate_ids": list(dict.fromkeys(mentioned))}
    if marker is not None:
        q["footnote_marker"] = marker
    if note_start is not None:
        q["cross_reference_segments"] = [{"segment_id": NOTES, "source_line_start": note_start,
                                             "source_line_end": note_end if note_end is not None else note_start}]
    if extras:
        q.update(extras)
    if any(cid not in candidate_ids for cid in [subject, obj, *mentioned] if cid):
        raise SystemExit(f"missing candidate in statement: {sid}")
    if first < meta["line_start"] or last > meta["line_end"]:
        raise SystemExit(f"statement lines outside p.250 segment: {sid}")
    return {"statement_id": sid, "segment_id": P250, "subject_candidate_id": subject,
            "object_candidate_id": obj, "predicate": predicate, "qualifiers": q,
            "original_quote": quote(first, last), "origin": "book", "source_file": meta["source_file"]}


OCR_CORRECTIONS = [
    {"source_line": 92, "ocr": "socalled", "print": "so-called", "basis": "CHP-9.pdf physical page 12"},
    {"source_line": 95, "ocr": "i68os", "print": "1680s", "basis": "CHP-9.pdf physical page 12"},
    {"source_line": 100, "ocr": "trionso", "print": "trionfo", "basis": "CHP-9.pdf physical page 12"},
    {"source_line": 104, "ocr": "138139-", "print": "138-139.", "basis": "CHP-9.pdf physical page 12"},
]

new_statements = [
    statement("st-chp9-p250-new-families-patronage", 91, 91, "cand-8134", "cand-2720",
        "newly_ennobled_families_led_early_18c_artistic_patronage",
        "Closing p.249's sentence, Haskell says that four or five families ennobled only about fifty years earlier were at the forefront of Venice's artistic patronage at the beginning of the eighteenth century.",
        "Preserve the approximate family count, approximate interval and source's temporal wording; no family names are supplied in this sentence.",
        ["cand-8134", "cand-2720", "cand-2719"],
        extras={"continued_from_segment_id": P249, "continued_from_source_line": 86,
                "cross_reference_segments": [{"segment_id": P249, "source_line_start": 86, "source_line_end": 86}],
                "ocr_corrections": OCR_CORRECTIONS[:1]}),
    statement("st-chp9-p250-zenobio-wealth-and-palace", 92, 92, "cand-2870", "cand-2871",
        "zenobio_family_bought_morosini_palace_at_carmini",
        "The Zenobio were said to be Venice's richest family; they had bought the palace at the Carmini from the Morosini, one of the twelve oldest families known as the Apostles.",
        "Retain 'were said to be' as reported reputation; do not equate the family group with an individual Morosini or identify a more precise Carmini site than the text supplies.",
        ["cand-2870", "cand-2719", "cand-2871", "cand-8184", "cand-1706", "cand-8185"],
        marker=1, note_start=344, extras={"relation_candidate": True}),
    statement("st-chp9-p250-zenobio-palace-transformation", 92, 92, "cand-2870", "cand-2871",
        "transformed_zenobio_palace_neared_completion_by_1703",
        "The Zenobio palace was completely transformed and nearing completion by 1703.",
        "The source gives a terminus/status by 1703, not an exact completion date.",
        ["cand-2870", "cand-2871"]),
    statement("st-chp9-p250-zenobio-fresco-cycle", 92, 92, "cand-0944", "cand-8186",
        "dorigny_painted_zenobio_mythological_fresco_cycle",
        "About fifteen years earlier, the French artist Dorigny had been called to paint a spectacular mythological fresco series at the palace, within an elaborate painted architectural framework described as Bolognese and Carraccesque and derived from the Palazzo Farnese in Rome.",
        "Keep 'some fifteen years earlier' approximate and 'derived from' as a comparison/influence claim; no exact commission year or individual fresco titles are given.",
        ["cand-0944", "cand-2871", "cand-8186", "cand-8187", "cand-8188", "cand-8189", "cand-0999", "cand-4490"],
        extras={"ocr_corrections": OCR_CORRECTIONS[:1], "relation_candidate": True}),
    statement("st-chp9-p250-frescoes-family-virtues", 92, 92, "cand-8186", "cand-2870",
        "frescoes_celebrated_family_virtues_and_protection_of_fine_arts",
        "The frescoes were designed to celebrate the family's virtues and its protection of the fine arts.",
        "This records the stated programme and function; it does not infer specific virtues or named artists beyond those in the source.",
        ["cand-8186", "cand-2870", "cand-2720"]),
    statement("st-chp9-p250-carlevarijs-landscapes", 93, 93, "cand-0554", "cand-8191",
        "carlevarijs_lodged_and_painted_landscapes_for_zenobio_palace",
        "Luca Carlevarijs, described as a painter of views, lodged in the palace and painted a series of romantic landscapes for it, inserted into frames along the corridor leading to the Salone.",
        "The source names a series but gives no number or individual titles for the landscapes.",
        ["cand-0554", "cand-2871", "cand-8191", "cand-8192", "cand-8193"], marker=2, note_start=344,
        extras={"relation_candidate": True}),
    statement("st-chp9-p250-lazzarini-ceres-bacchus", 93, 93, "cand-1368", "cand-8194",
        "decorated_zenobio_ceiling_with_ceres_and_bacchus",
        "Gregorio Lazzarini decorated a ceiling at the Zenobio palace with Ceres and Bacchus.",
        "The source does not give a date or further iconographic description.",
        ["cand-1368", "cand-2871", "cand-8194", "cand-8195", "cand-7814"], extras={"relation_candidate": True}),
    statement("st-chp9-p250-tiepolo-early-works", 93, 93, "cand-2569", "cand-2870",
        "produced_early_works_for_zenobio_family",
        "The young Giambattista Tiepolo produced some of his earliest works for the Zenobio family.",
        "Preserve 'some of his earliest'; the source does not identify individual works or give a date.",
        ["cand-2569", "cand-2870"], marker=3, note_start=345, extras={"relation_candidate": True}),
    statement("st-chp9-p250-widmann-palace-and-scipio-canvases", 94, 94, "cand-2812", "cand-2813",
        "widmann_palace_decorated_with_lazzarini_scipio_canvases",
        "The Widmann family, described as of Carinthian origin, had a splendid palace near S. Canciano and lavishly decorated it with large Lazzarini canvases showing scenes from the life of Scipio Africanus.",
        "The text does not identify individual canvases or specify the family's exact Carinthian place of origin.",
        ["cand-2812", "cand-8190", "cand-2813", "cand-8198", "cand-8197", "cand-1368", "cand-8196"],
        marker=4, note_start=346, extras={"relation_candidate": True}),
    statement("st-chp9-p250-widmann-country-house-frescoes", 94, 94, "cand-0944", "cand-8200",
        "painted_diana_actaeon_frescoes_at_widmann_country_house",
        "Louis Dorigny painted the Widmann country house at Bagnoli di Sopra with frescoes of Diana and Actaeon.",
        "Keep this work group distinct from the similarly titled Diana-and-Actaeon wall scene in Ricci's Pitti decoration.",
        ["cand-0944", "cand-2812", "cand-2811", "cand-8199", "cand-8200", "cand-4136", "cand-7995"],
        marker=5, note_start=346, extras={"relation_candidate": True}),
    statement("st-chp9-p250-labia-palace-and-wealth", 95, 95, "cand-1349", "cand-8201",
        "labia_family_built_large_palace_and_displayed_wealth",
        "The Labia, described as rich businessmen of Catalan origin, began building a gigantic palace completed in the early eighteenth century and displayed their wealth ostentatiously.",
        "The source supplies a broad regional origin and approximate completion period, not exact dates or named individual builders.",
        ["cand-1349", "cand-8202", "cand-8201"], marker=6, note_start=347, extras={"relation_candidate": True}),
    statement("st-chp9-p250-labia-employed-lazzarini", 95, 95, "cand-1349", "cand-1368",
        "labia_employed_lazzarini_throughout_1680s",
        "The Labia employed Gregorio Lazzarini throughout the 1680s.",
        "The OCR 'i68os' is corrected to printed '1680s'; retain the decade-level time range.",
        ["cand-1349", "cand-1368"], marker=7, note_start=347,
        extras={"relation_candidate": True, "ocr_corrections": OCR_CORRECTIONS[1:2]}),
    statement("st-chp9-p250-labia-giordano-collection", 95, 96, "cand-1349", "cand-1348",
        "owned_largest_venetian_collection_of_giordano_pictures",
        "The Labia owned what Haskell calls Venice's largest collection of pictures by Luca Giordano, presumably painted for them during his visit in 1682.",
        "Preserve 'presumably' and attribute the superlative to Haskell; this does not establish authorship for each work or independently verify Giordano's 1682 visit.",
        ["cand-1349", "cand-1348", "cand-1182", "cand-2719"], marker=8, note_start=348,
        extras={"relation_candidate": True, "continuation_to_source_line": 96,
                "cross_reference_segments": [{"segment_id": NOTES, "source_line_start": 348, "source_line_end": 348}],
                "ocr_corrections": OCR_CORRECTIONS[1:2]}),
    statement("st-chp9-p250-labia-inventory-title-list", 97, 103, "cand-1348", "cand-1182",
        "1749_inventory_listed_labia_giordano_picture_titles",
        "The continuation of note 8 lists nine further inventory entries for pictures in the Labia palace, including S. Gerolamo nel Deserto, La Notte, Il Giudicio di Paride, Tre Animali, Architettura, Un trionfo d'armi, Battaria di Cusina, Quadi [sic] on scriptural subjects, and four drawings with crystal.",
        "The preceding consolidated note L348 identifies a 1749 notarial inventory and says these are pictures by Giordano; retain its reported-source status and do not infer surviving-object identities. Inventory numbers 6, 7 and 12 are not titled in this page continuation.",
        ["cand-1348", "cand-1182", "cand-8203", "cand-8204", "cand-8205", "cand-8206", "cand-8207", "cand-8208", "cand-8209", "cand-8210", "cand-8211"],
        marker=8, note_start=348, text_layer="footnote",
        extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 348,
                "ocr_corrections": OCR_CORRECTIONS[2:3]}),
    statement("st-chp9-p250-cochin-inventory-references", 104, 104, "cand-0793", "cand-1348",
        "cochin_referred_to_labia_inventory_pictures_and_other_images",
        "Haskell says Cochin, who was in Venice in 1750, referred to several pictures from the inventory; the text says the group almost certainly included Job and his Wife and Isaac blessing Jacob, and adds Cochin's references to a Sonates, St Peter receiving the Keys and a shepherds-and-sheep picture.",
        "The parenthetical identification is expressly 'almost certainly'; no exact mapping from the two titles to inventory numbers is supplied. The additional works are not assumed to be by Giordano or identical to inventory entries.",
        ["cand-0793", "cand-2719", "cand-1348", "cand-8212", "cand-8213", "cand-8214", "cand-8215", "cand-4231", "cand-8216"],
        marker=8, note_start=348, text_layer="footnote",
        extras={"continued_from_segment_id": NOTES, "continued_from_source_line": 348,
                "citation_locator": "Cochin, vol. III, pp. 138-139",
                "ocr_corrections": OCR_CORRECTIONS[3:4]}),
]
statement_ids = {row["statement_id"] for row in statements}
new_statement_ids = {row["statement_id"] for row in new_statements}
if len(statement_ids) != len(statements) or len(new_statement_ids) != len(new_statements) or statement_ids & new_statement_ids:
    raise SystemExit("duplicate statement ID")

coverage_by_id[P249].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L77-88",
    "note": "Printed p.249 reviewed against CHP-9.pdf physical p.11. L78 closes p.248 L46; p.249 L86 ends 'At' and is closed by p.250 L91. Body claims and note markers 1-5 are linked to their printed/consolidated note locations. Note 4's earlier citation at L338 is retained as contextual support for Barbaro's will."
})
coverage_by_id[P250].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L90-104",
    "note": "Printed p.250 (CHP-9.pdf physical p.12) reviewed against the page image. L91 closes p.249 L86. Body claims and markers 1-8 are anchored; notes 1-8 link to the consolidated notes segment L344-348. Page lines L97-104 preserve the unique continuation of note 8: the remaining 1749 inventory titles and Cochin's references; these are not duplicated from the earlier consolidated note text. OCR corrections are recorded in S2 only; S0 is unchanged."
})

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
args = parser.parse_args()
print(json.dumps({
    "segments": [P249, P250], "new_candidates": len(candidate_specs),
    "new_mentions": len(new_mentions), "new_statements": len(new_statements),
    "coverage": {sid: [coverage_by_id[sid]["disposition"], coverage_by_id[sid]["migration_status"]]
                 for sid in (P249, P250)},
    "continuations": [f"{P249} L86 -> {P250} L91"],
    "footnote_links": [f"marker 1 -> {NOTES} L344", f"marker 2 -> {NOTES} L344",
                       f"marker 3 -> {NOTES} L345", f"marker 4 -> {NOTES} L346",
                       f"marker 5 -> {NOTES} L346", f"marker 6 -> {NOTES} L347",
                       f"marker 7 -> {NOTES} L347", f"marker 8 -> {NOTES} L348 + {P250} L97-104"],
}, ensure_ascii=False))
if not args.apply:
    print("DRY RUN: no files changed")
else:
    paths = [candidate_path, mention_path, statement_path, coverage_path]
    backups = []
    for path in paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"refusing to overwrite existing backup: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions + new_mentions)
    write_jsonl(statement_path, statements + new_statements)
    write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
    print("applied; backups=" + ", ".join(backup.name for _, backup in backups))
