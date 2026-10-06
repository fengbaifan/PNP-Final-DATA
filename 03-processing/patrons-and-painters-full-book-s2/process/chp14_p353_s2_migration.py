"""Controlled S2 migration for printed p.353 body and note 1; dry-run by default."""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BODY_PREV = "chp-14:14_CHP-14_intro:l55-61"
BODY = "chp-14:14_CHP-14_intro:l63-71"
NOTES = "chp-14:14_CHP-14_intro:l168-220"
PLATES = "front-matter:00_05_List_of_Plates:l140-172"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
BACKUP_SUFFIX = ".bak-s2-chp14-p353-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.353 S2 migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        tmp = Path(f.name)
    tmp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        tmp = Path(f.name)
    tmp.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    64: "more disciplined. In the completed version",
    65: "-.. has gone",
    66: "The sleek greyhound",
    67: "two antique statues of Isis and Serapis",
    68: "Small changes, perhaps, but all pointing",
    69: "Algarotti commissioned two other pictures",
    70: "Flore qui change en endroits délicieux",
    71: "Neptune fountain by Lorenzo Mattielli",
    185: "For the two pictures ordered by Algarotti for Briihl",
}.items():
    if required not in source_lines[line_number - 1]:
        raise SystemExit(f"required source text changed at L{line_number}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
mention_by_id = {row["mention_id"]: row for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (BODY_PREV, BODY, NOTES, PLATES):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
if coverage_by_id[BODY_PREV]["disposition"] != "reviewed" or coverage_by_id[BODY_PREV]["migration_status"] != "partial":
    raise SystemExit("p.352 body segment is not in the expected partial state")
if coverage_by_id[BODY]["disposition"] != "queued":
    raise SystemExit("p.353 body segment is not queued; refusing to overwrite")
if coverage_by_id[NOTES]["disposition"] != "reviewed" or coverage_by_id[NOTES]["migration_status"] != "partial":
    raise SystemExit("consolidated chapter 14 notes segment is not in the expected partial state")
if coverage_by_id[PLATES]["disposition"] != "reviewed" or coverage_by_id[PLATES]["migration_status"] != "complete":
    raise SystemExit("plate-list segment is not reviewed; refusing to assume its caption data")
prior_closure = statement_by_id.get("st-chp14-p352-cleopatra-description-continuation")
if prior_closure is None:
    raise SystemExit("p.352 continuation statement is missing")
if any(sid.startswith("st-chp14-p353-") for sid in statement_by_id):
    raise SystemExit("p.353 statement IDs already exist; refusing duplicate migration")
if any(mid.startswith("m-chp14-p353-") for mid in mention_by_id):
    raise SystemExit("p.353 mention IDs already exist; refusing duplicate migration")

new_candidates = [
    ("cand-10284", "Mark Antony as depicted in Tiepolo’s Banquet of Cleopatra", "person", 66,
     "Named as the figure whose helmet feathers change between the two versions; no additional portrait identity is inferred."),
    ("cand-10285", "Pompeii (archaeological site named in the vase-form passage)", "place", 66,
     "Named as a site of excavations that Haskell says will introduce Greek vase forms into painting and decoration."),
    ("cand-10286", "Herculaneum (archaeological site named in the vase-form passage)", "place", 66,
     "Named alongside Pompeii as a site of excavations; no specific find or excavation date is identified here."),
    ("cand-10287", "Isis (mythological figure depicted as an antique statue)", "person", 67,
     "Named as one of two statues depicted in the Banquet; the passage does not identify an extant antique object."),
    ("cand-10288", "Serapis (mythological figure depicted as an antique statue)", "person", 67,
     "Named as one of two statues depicted in the Banquet; the passage does not identify an extant antique object."),
    ("cand-10289", "Pictorial scholarship as a quality praised in Tiepolo’s painting", "term", 68,
     "Haskell reports Algarotti’s praise of the picture’s ‘pictorial scholarship’; preserve this as a critical term, not a measurable property."),
    ("cand-10290", "Roman school as the traditional locus of pictorial scholarship in Haskell’s account", "term", 68,
     "The passage describes a claimed Roman prerogative; do not turn it into a formal institution or an uncontested history of art."),
    ("cand-10291", "Engraving of the original modello of The Banquet of Cleopatra (reported as being brought to the King)", "work", 68,
     "Algarotti is reported as intending to bring an engraving so the King could see the composition. Its maker and delivery are not stated; keep it distinct from Leonardis’s Maecenas engraving, Plate 68b."),
    ("cand-10292", "Undated Algarotti letter to Count Brühl quoted by Haskell on p.353", "archive", 68,
     "Haskell says Algarotti wrote to Brühl and quotes a first-person passage. This source does not give the letter date, repository, or publication locator."),
    ("cand-10293", "Hanging gardens attributed to Count Brühl’s residences (exact site unspecified)", "place", 70,
     "Named among Brühl’s prized possessions in his town and country houses; no particular residence or garden is identified."),
    ("cand-10294", "Neptune fountain by Lorenzo Mattielli (residence and object identity unspecified)", "work", 71,
     "Named as one of Brühl’s prized possessions represented in the commissioned picture or pictures; do not infer a particular house or surviving fountain."),
    ("cand-10295", "De Young Memorial Museum (name used in Haskell’s 1980 note)", "institution", 185,
     "The edition-era note names this museum as the reported location of the Flora picture; the name is retained as printed and is not a current custody claim."),
    ("cand-10296", "San Francisco (place named in p.353 note 1)", "place", 185,
     "Named as the location of the De Young Memorial Museum in Haskell’s note."),
    ("cand-10297", "Levey (author named by surname in p.353 note 1; identity unaligned)", "person", 185,
     "The note gives only the surname. Keep separate from other Levey candidates until S3 identity alignment and bibliography review."),
    ("cand-10298", "Levey, Burlington Magazine, 1957, pp. 89–91 (citation locator in p.353 note 1)", "archive", 185,
     "Short citation as printed. The title and bibliography match are deferred to the S2 bibliography pass; the article and cited pages were not independently consulted."),
]
for cid, name, suggested_type, source_line, detail in new_candidates:
    if cid in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {cid}")
    candidates.append({
        "candidate_id": cid, "index_entry_id": "", "canonical_name": name,
        "index_page_range": "", "suggested_type": suggested_type, "status": "open",
        "index_source_file": "", "sub_entry": "", "detail": detail,
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES if source_line >= 168 else BODY}#L{source_line}",
    })
    candidate_by_id[cid] = candidates[-1]

segment_bounds = {BODY: (63, 71), NOTES: (168, 220)}
segment_offsets = {}
for segment_id, (line_start, line_end) in segment_bounds.items():
    offset = 0
    for number in range(line_start, line_end + 1):
        segment_offsets[(segment_id, number)] = offset
        offset += len(source_lines[number - 1]) + (1 if number < line_end else 0)
occupied_same_candidate = set()
mention_counter = 1


def _add_mention(segment_id, candidate_id, surface, number, pos, note=""):
    global mention_counter
    start = segment_offsets[(segment_id, number)] + pos
    end = start + len(surface)
    if any(seg == segment_id and cid == candidate_id and s == start and e == end
           for seg, cid, s, e in occupied_same_candidate):
        return
    mention_id = f"m-chp14-p353-{mention_counter:04d}"
    if mention_id in mention_by_id:
        raise SystemExit(f"mention ID already exists: {mention_id}")
    row = {"mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
           "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note}
    mentions.append(row)
    mention_by_id[mention_id] = row
    occupied_same_candidate.add((segment_id, candidate_id, start, end))
    mention_counter += 1


def add_surface(segment_id, candidate_id, surface, line_numbers, note=""):
    matched = False
    for number in line_numbers:
        line = source_lines[number - 1]
        search_from = 0
        while True:
            pos = line.find(surface, search_from)
            if pos < 0:
                break
            matched = True
            _add_mention(segment_id, candidate_id, surface, number, pos, note)
            search_from = pos + 1
    if not matched:
        raise SystemExit(f"surface not found in requested lines: {segment_id} {surface!r} {line_numbers}")


def add_surface_occurrence(segment_id, candidate_id, surface, line_number, occurrence=0, note=""):
    line = source_lines[line_number - 1]
    positions = []
    search_from = 0
    while True:
        pos = line.find(surface, search_from)
        if pos < 0:
            break
        positions.append(pos)
        search_from = pos + 1
    if occurrence >= len(positions):
        raise SystemExit(f"surface occurrence not found: L{line_number} {surface!r} #{occurrence}")
    _add_mention(segment_id, candidate_id, surface, line_number, positions[occurrence], note)


def add_pronoun_occurrence(segment_id, candidate_id, form, line_number, occurrence=0, note="Coreference resolved from the local passage context."):
    matches = list(re.finditer(rf"(?<![\w]){re.escape(form)}(?![\w])", source_lines[line_number - 1]))
    if occurrence >= len(matches):
        raise SystemExit(f"pronoun occurrence not found: L{line_number} {form!r} #{occurrence}")
    _add_mention(segment_id, candidate_id, form, line_number, matches[occurrence].start(), note)


# Named entities, prior works, the recipient, and the note's separate Plate 68b engraving.
for surface, cid, lines, *extra in [
    ("the completed version", "cand-4101", [64]),
    ("in the sketch", "cand-4100", [66, 67]),
    ("Pompeii", "cand-10285", [66]),
    ("Herculaneum", "cand-10286", [66]),
    ("Mark Antony", "cand-10284", [66]),
    ("Isis", "cand-10287", [67]),
    ("Serapis", "cand-10288", [67]),
    ("Algarotti", "cand-0052", [68]),
    ("an engraving of the original modello", "cand-10291", [68]),
    ("wrote", "cand-10292", [68], "The particular letter is inferred from Haskell’s attribution of the quoted first-person text."),
    ("Bruhl", "cand-0458", [68]),
    ("Tiepolo", "cand-2577", [68]),
    ("His Majesty", "cand-0149", [68]),
    ("pictorial scholarship", "cand-10289", [68]),
    ("Roman school", "cand-10290", [68]),
    ("Venice", "cand-2719", [68]),
    ("Poussin", "cand-1984", [68]),
    ("High Renaissance", "cand-3579", [68]),
    ("Veronese", "cand-2755", [68]),
    ("old masters", "cand-4288", [68]),
    ("The King", "cand-0149", [68]),
    ("Augustus", "cand-0149", [68, 69]),
    ("Tiepolo", "cand-3781", [69]),
    ("Algarotti", "cand-0045", [69]),
    ("Briihl", "cand-0458", [69]),
    ("les Beaux Arts amenez par Mecène au Trône d’Auguste", "cand-2597", [69]),
    ("l’empire de", "cand-2590", [69]),
    ("Flore", "cand-2590", [70]),
    ("Bruhl’s", "cand-0458", [70]),
    ("hanging gardens", "cand-10293", [70]),
    ("Neptune fountain", "cand-10294", [71]),
    ("Lorenzo Mattielli", "cand-1584", [71]),
    ("Flora", "cand-2590", [185]),
    ("Hermitage", "cand-5795", [185]),
    ("De Young Memorial Museum", "cand-10295", [185]),
    ("San Francisco", "cand-10296", [185]),
    ("Levey", "cand-10297", [185]),
    ("Burlington Magazine, 1957, pp. 89-91", "cand-10298", [185]),
    ("Leonardis", "cand-3823", [185]),
    ("Plate 68b", "cand-4104", [185]),
]:
    add_surface(BODY if lines[0] < 168 else NOTES, cid, surface, lines, note=extra[0] if extra else "")

# The subject phrase continues across an OCR line break; preserve non-overlapping anchors.
add_surface_occurrence(BODY, "cand-2590", "l’empire de", 69, 0)
add_surface_occurrence(BODY, "cand-2590", "Flore", 70, 0)
add_surface_occurrence(NOTES, "cand-2597", "Maecenas", 185, 0)
add_surface_occurrence(NOTES, "cand-2597", "Maecenas", 185, 1)

# Resolve pronouns that carry a named referent in the page's interpretation and relationships.
for cid, form, line, occurrence in [
    ("cand-0052", "he", 68, 0), ("cand-0052", "he", 68, 1), ("cand-0052", "he", 68, 2),
    ("cand-2577", "he", 68, 3), ("cand-0052", "he", 68, 4), ("cand-0149", "he", 68, 5),
    ("cand-0052", "his", 68, 0), ("cand-2577", "his", 68, 1),
    ("cand-0149", "his", 68, 2), ("cand-0052", "his", 68, 3),
    ("cand-0149", "him", 68, 0),
    ("cand-4101", "its", 68, 0), ("cand-4101", "its", 68, 1), ("cand-4101", "its", 68, 2),
    ("cand-10289", "its", 68, 3),
    ("cand-4101", "this", 68, 0), ("cand-9266", "this", 68, 1), ("cand-4101", "this", 68, 2),
    ("cand-0052", "He", 69, 0),
    ("cand-0045", "he", 70, 0),
    ("cand-0458", "his", 71, 0),
]:
    add_pronoun_occurrence(BODY, cid, form, line, occurrence)

# Keep the standalone Renaissance mention; the later occurrence is nested in High Renaissance.
add_surface_occurrence(BODY, "cand-3578", "Renaissance", 68, 0)


def quote(start, end, exact):
    allowed = "\n".join(source_lines[start - 1:end])
    if exact not in allowed:
        raise SystemExit(f"statement quotation is not present in L{start}-L{end}: {exact[:90]!r}")
    return exact


def q(start, end, claim, layer, qualification, candidate_ids, **extra):
    out = {
        "source_line_start": start, "source_line_end": end, "printed_page": 353,
        "pdf_physical_page": 7, "claim": claim, "speaker": "Haskell",
        "text_layer": layer, "qualification": qualification,
        "mentioned_candidate_ids": candidate_ids,
    }
    out.update(extra)
    return out


def add_statement(statement_id, segment_id, subject, obj, predicate, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    start, end = qualifiers["source_line_start"], qualifiers["source_line_end"]
    bounds = (63, 71) if segment_id == BODY else (168, 220)
    if not (bounds[0] <= start <= end <= bounds[1]):
        raise SystemExit(f"statement span escapes source segment: {statement_id}")
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers, "original_quote": original_quote,
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


def add_note_statement(statement_id, qualifiers, original_quote):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    row = {
        "statement_id": statement_id, "segment_id": NOTES,
        "subject_candidate_id": None, "object_candidate_id": None,
        "predicate": "bibliographic_note", "qualifiers": qualifiers,
        "original_quote": original_quote, "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


link1 = {"footnote_marker": "1", "footnote_segment": NOTES, "footnote_line_range": "L185",
         "footnote_text_pending": False, "footnote_body_link_status": "linked",
         "footnote_note_statement_ids": [
             "st-chp14-p353-note1-picture-locations-and-source",
             "st-chp14-p353-note1-leonardis-engraving",
         ]}

add_statement("st-chp14-p353-cleopatra-comparison-closed", BODY, "cand-4101", "cand-4157", "described_cleopatra_and_servants_as_more_disciplined",
    q(64, 64, "The page completes the p.352 comparison: Cleopatra’s servants are described as more disciplined in the completed version.",
      "authorial visual comparison", "This closes p.352 L61 after ‘and’; it does not add any unstated feature to the comparison.",
      ["cand-4101", "cand-4157"], cross_reference_segments=[BODY_PREV],
      cross_reference_text="completes the unfinished sentence at p.352 L61"),
    quote(64, 64, "more disciplined."))

add_statement("st-chp14-p353-completed-version-classical-composition", BODY, "cand-4101", "cand-9266", "composition_emphasizes_classical_order",
    q(64, 65, "Haskell says the completed version emphasizes a classical scene through parallel planes and rigid verticals and horizontals; the arch is removed and the columns rise to the canvas edge.",
      "authorial visual analysis", "The statement describes Haskell’s comparison of the two versions; OCR artefacts and the misspelling ‘parellel’ are corrected only in this S2 qualifier, not in S0.",
      ["cand-4101", "cand-4100", "cand-9266"],
      ocr_corrections=[
          {"source_line": 65, "ocr": "-.. has gone", "print": "has gone", "basis": "CHP-14.pdf physical page 7."},
          {"source_line": 66, "ocr": "parellel", "print": "parallel", "basis": "CHP-14.pdf physical page 7."},
      ]),
    quote(64, 65, "In the completed version everything has been done to emphasise the classical nature of the scene. Recession into the picture is abandoned in favour of clear, parallel planes. Rigid verticals and horizontals divide up the spectacle. The curved arch\n-.. has gone, and the columns rise to the very top of the canvas and are cut off by the frame."))

add_statement("st-chp14-p353-greyhound-version-comparison", BODY, "cand-4101", "cand-4100", "compares_greyhound_placement_between_versions",
    q(66, 66, "In the completed version the greyhound is turned parallel to the floor’s horizontal paving lines, changing its role from a curious interloper to a tame pet.",
      "authorial visual comparison", "The greyhound is treated as a pictorial feature, not as a separately identified animal entity.",
      ["cand-4101", "cand-4100"]),
    quote(66, 66, "The sleek greyhound, which in the sketch faced into the picture and presented its tail to the spectator, now sits parellel to the horizontal lines of the floor paving, a tame pet rather than a curious interloper."))

add_statement("st-chp14-p353-jug-replaced-by-greek-vase", BODY, "cand-4101", None, "depicts_greek_wine_vase_in_place_of_masked_jug",
    q(66, 66, "The picture replaces a jug embossed with a mask with a simple Greek wine vase.",
      "authorial visual description", "The jug and vase are described as pictorial features, not individually identified works.",
      ["cand-4101"]),
    quote(66, 66, "A jug embossed with a mask has been replaced by a simple Greek wine vase"))

add_statement("st-chp14-p353-excavations-and-vase-forms", BODY, None, None, "excavations_at_pompeii_and_herculaneum_expected_to_introduce_vase_forms",
    q(66, 66, "Haskell predicts that excavations at Pompeii and Herculaneum will soon introduce this Greek wine-vase form into painting and decoration across Europe.",
      "authorial historical interpretation", "This is Haskell’s prospective claim; no excavation chronology or particular find is asserted here.",
      ["cand-10285", "cand-10286"]),
    quote(66, 66, "such as the excavations at Pompeii and Herculaneum will soon introduce into painting and decoration all over Europe."))

add_statement("st-chp14-p353-mark-antony-helmet-change", BODY, "cand-4101", "cand-10284", "depicts_mark_antony_with_feathers_replaced_by_eagle",
    q(66, 66, "The completed composition removes the feathers from Mark Antony’s helmet and makes way for the eagle.",
      "authorial visual comparison", "The claim concerns the depiction in the completed version; it does not identify a surviving helmet or eagle object.",
      ["cand-4101", "cand-10284"]),
    quote(66, 66, "The feathers on Mark Antony’s helmet, shimmering in the light breeze, have been discarded to make way for the eagle."))

add_statement("st-chp14-p353-isis-and-serapis-statues", BODY, "cand-4101", "cand-10287", "depicts_antique_statues_of_isis_and_serapis",
    q(67, 67, "Haskell describes two antique statues of Isis and Serapis in the colonnade niches; the sketch showed only one, half-concealed by a hanging jug.",
      "authorial visual comparison", "The deities are depicted figures, and the statues are features in the composition; no extant antiquities are identified.",
      ["cand-4101", "cand-10287", "cand-10288", "cand-4100"]),
    quote(67, 67, "In the niches of the colonnade are two antique statues of Isis and Serapis; in the sketch there had only been one, and that half-concealed by a hanging jug."))

add_statement("st-chp14-p353-changes-attributed-to-algarotti", BODY, "cand-4101", "cand-0052", "changes_attributed_by_haskell_to_algarotti",
    q(68, 68, "Haskell attributes the compositional changes unhesitatingly to Algarotti’s mind.",
      "authorial attribution", "This is Haskell’s interpretation of the changes, not documentary proof that Algarotti directed each one.",
      ["cand-4101", "cand-0052"], relation_candidate=True),
    quote(68, 68, "Small changes, perhaps, but all pointing so decisively in one direction that we can attribute them unhesitatingly to the mind of Algarotti."))

add_statement("st-chp14-p353-algarotti-letter-and-engraving-plan", BODY, "cand-0052", "cand-10292", "wrote_to_bruhl_about_bringing_modello_engraving",
    q(68, 68, "Haskell reports that Algarotti wrote to Brühl and quoted him as saying he was bringing an engraving of the original modello for His Majesty to see.",
      "authorial report of correspondence with embedded quotation", "The letter is undated and unlocated in this passage; Haskell reports an intended act, not confirmed delivery. The quoted ‘author’ refers to Tiepolo, and ‘His Majesty’ to Augustus III.",
      ["cand-0052", "cand-0458", "cand-10292", "cand-10291", "cand-0149", "cand-3781"], relation_candidate=True,
      cross_reference_segments=[BODY_PREV, PLATES],
      cross_reference_text="the Banquet modello discussed on p.352 is distinct from the Leonardis Maecenas engraving captioned as Plate 68b"),
    quote(68, 68, "‘I am bringing with me an engraving of the original modello so that His Majesty can see how greatly the imagination of the author has enriched and improved the composition’, he wrote to Bruhl"))

add_statement("st-chp14-p353-algarotti-praises-architectural-and-perspectival-features", BODY, "cand-0052", "cand-4101", "praised_architectural_reality_accuracy_perspective_and_grandeur",
    q(68, 68, "Haskell says Algarotti singled out the architecture’s reality and historical accuracy, together with the perspective and grandeur, for particular approval.",
      "authorial report of appraisal", "These are qualities Haskell attributes to Algarotti’s assessment of the Banquet composition.",
      ["cand-0052", "cand-4101"]),
    quote(68, 68, "he singled out for special praise some of the features that have been mentioned. The ‘reality’ of the architecture and its ‘historical accuracy’ win his particular approval, as do its perspective and grandeur."))

add_statement("st-chp14-p353-algarotti-praises-pictorial-scholarship", BODY, "cand-0052", "cand-10289", "praised_pictorial_scholarship_in_tiepolo_composition",
    q(68, 68, "Haskell reports that Algarotti especially admired the picture’s ‘pictorial scholarship’.",
      "authorial report of appraisal", "The phrase is retained as a critical term from Haskell’s account, not an objective measurement.",
      ["cand-0052", "cand-4101", "cand-10289"]),
    quote(68, 68, "Above all he admired its ‘pictorial scholarship’"))

add_statement("st-chp14-p353-roman-school-prerogative", BODY, "cand-10289", "cand-10290", "pictorial_scholarship_described_as_roman_school_prerogative",
    q(68, 68, "Haskell says pictorial scholarship was making its first appearance in Venice after long being considered the Roman school’s exclusive prerogative.",
      "authorial art-historical interpretation", "This is Haskell’s account of a perceived tradition; ‘first appearance’ is not generalized into a verified history of Venetian painting.",
      ["cand-10289", "cand-10290", "cand-2719"]),
    quote(68, 68, "which was now making its first appearance in Venice after being considered for so long the exclusive prerogative of the Roman school."))

add_statement("st-chp14-p353-tiepolo-compared-with-poussin", BODY, "cand-2577", "cand-1984", "described_by_algarotti_as_accurate_painter_comparable_to_poussin",
    q(68, 68, "Haskell says Algarotti claimed that Tiepolo was an ‘accurate’ painter comparable to Poussin.",
      "authorial report of Algarotti’s comparison", "The comparison is attributed to Algarotti; Haskell notes it may surprise the reader.",
      ["cand-2577", "cand-1984", "cand-0052"], relation_candidate=True),
    quote(68, 68, "The idea of Tiepolo as an ‘accurate’ painter comparable to Poussin (as Algarotti claimed)"))

add_statement("st-chp14-p353-classical-claim-and-period-comparison", BODY, "cand-4101", "cand-9266", "described_as_more_classical_than_tiepolo_and_venetian_precedents",
    q(68, 68, "Haskell judges this to be more classical than any picture Tiepolo had previously painted and than any Venetian painting since the Renaissance ended.",
      "authorial comparative interpretation", "The superlative is Haskell’s assessment. The OCR ‘may ell’ is corrected to printed ‘may well’ in this S2 record only.",
      ["cand-4101", "cand-2577", "cand-3578", "cand-9266"],
      ocr_corrections=[{"source_line": 68, "ocr": "may ell surprise us", "print": "may well surprise us", "basis": "CHP-14.pdf physical page 7."}]),
    quote(68, 68, "may ell surprise us: and yet this was certainly a more classical picture than any that he had hitherto painted, or, indeed, that had been painted by anyone in Venice since the end of the Renaissance."))

add_statement("st-chp14-p353-algarotti-promotes-classical-aspect-to-augustus", BODY, "cand-0052", "cand-0149", "encouraged_classical_aspect_in_dealings_with_augustus",
    q(68, 68, "Haskell says Algarotti had reason to encourage the classical aspect of Tiepolo’s art in his dealings with Augustus.",
      "authorial interpretation of motive", "This records Haskell’s explanation of Algarotti’s conduct, not a documented statement by Algarotti in this passage.",
      ["cand-0052", "cand-2577", "cand-0149", "cand-9266"], relation_candidate=True),
    quote(68, 68, "quite apart from Algarotti’s personal convictions, he had every reason to encourage this aspect of Tiepolo’s art and to stress it in his dealings with Augustus."))

add_statement("st-chp14-p353-king-prefers-old-masters", BODY, "cand-0149", "cand-4288", "reported_as_more_anxious_to_expand_old_master_collection_than_commission_contemporary_artists",
    q(68, 68, "Haskell reports that the King was not eager to commission contemporary artists and was more anxious to increase his old-master collection.",
      "authorial report", "This is Haskell’s description of the King’s collecting priorities, not an exhaustive statement about all commissions.",
      ["cand-0149", "cand-4288"]),
    quote(68, 68, "The King had not been very eager about commissioning contemporary artists; he was much more anxious to increase his collection of old masters."))

add_statement("st-chp14-p353-framing-tiepolo-in-italian-tradition", BODY, "cand-0052", "cand-4101", "framed_tiepolo_as_continuing_italian_painting_tradition_for_augustus",
    q(68, 68, "Haskell says Algarotti emphasized Tiepolo’s link to the Italian painting tradition when sending this modern painter to Augustus on his own initiative, presenting him as a latter-day Veronese whose accuracy exceeded that of the High Renaissance master.",
      "authorial interpretation of presentation strategy", "The wording is Haskell’s reconstruction of Algarotti’s purpose. The source does not state that Veronese or the High Renaissance master directly influenced this composition.",
      ["cand-0052", "cand-4101", "cand-0149", "cand-2577", "cand-2755", "cand-3579"], relation_candidate=True),
    quote(68, 68, "In this first and crucial example of a favourite modern painter that Algarotti was sending him on his own initiative it was therefore doubly important to emphasise the link with the great tradition of Italian painting: to show Tiepolo as a latter-day Veronese, if anything rather more concerned with accuracy than the High Renaissance master had been."))

add_statement("st-chp14-p353-commissioned-maecenas-picture-for-bruhl", BODY, "cand-0052", "cand-2597", "commissioned_tiepolo_maecenas_picture",
    q(69, 70, "Haskell says Algarotti commissioned the Tiepolo picture indexed under Maecenas as one of two other works at this time.",
      "authorial report", "The index candidate identifies the work by subject; the passage gives a French descriptive subject, not an independently verified formal title.",
      ["cand-0052", "cand-3781", "cand-2597", "cand-2590"], relation_candidate=True),
    quote(69, 70, "‘les Beaux Arts amenez par Mecène au Trône d’Auguste ... et l’empire de\nFlore qui change en endroits délicieux les lieux les plus sauvages’"))

add_statement("st-chp14-p353-commissioned-flora-picture-for-bruhl", BODY, "cand-0052", "cand-2590", "commissioned_tiepolo_flora_picture",
    q(69, 70, "The second named subject is a picture indexed under Flora, described as the Empire of Flora transforming wild places into delightful settings.",
      "authorial report of proposed subject", "The French phrase is Haskell’s descriptive subject; it is not treated as a verified formal title or an independently identified version.",
      ["cand-0052", "cand-3781", "cand-2590", "cand-0458"], relation_candidate=True),
    quote(69, 70, "l’empire de\nFlore qui change en endroits délicieux les lieux les plus sauvages"))

add_statement("st-chp14-p353-two-pictures-sent-to-bruhl", BODY, "cand-0052", "cand-0458", "sent_two_commissioned_pictures_to_count_bruhl",
    q(69, 69, "Haskell says both other pictures commissioned by Algarotti from Tiepolo were sent to Augustus III’s minister, Count Brühl.",
      "authorial report", "The OCR ‘whichdie’ is corrected to printed ‘which he’; the report does not establish that the works were received or installed.",
      ["cand-0052", "cand-3781", "cand-2597", "cand-2590", "cand-0149", "cand-0458"], relation_candidate=True,
      ocr_corrections=[{"source_line": 69, "ocr": "whichdie sent", "print": "which he sent", "basis": "CHP-14.pdf physical page 7."}],
      **link1),
    quote(69, 69, "Algarotti commissioned two other pictures from Tiepolo at this time, both of whichdie sent to Augustus’s all-powerful minister, Count Briihl.1"))

add_statement("st-chp14-p353-subjects-chosen-to-flatter-bruhl", BODY, "cand-0052", "cand-0458", "selected_subjects_to_flatter_bruhl",
    q(69, 70, "Haskell says Algarotti chose the two subjects to flatter Brühl’s artistic pretensions and emphasized that aim through the subject matter.",
      "authorial interpretation of motive", "This is Haskell’s interpretation; no statement by Brühl or contract language is quoted.",
      ["cand-0052", "cand-0458", "cand-2597", "cand-2590", "cand-3781"], relation_candidate=True,
      ocr_corrections=[{"source_line": 70, "ocr": "Bruhl’s", "print": "Brühl’s", "basis": "CHP-14.pdf physical page 7."}]),
    quote(70, 70, "to flatter the artistic pretensions of the minister, and he emphasised this aim"))

add_statement("st-chp14-p353-bruhl-possessions-in-the-pictures", BODY, None, None, "reported_bruhl_possessions_as_pictorial_motifs",
    q(70, 71, "Haskell reports that Tiepolo inserted two prized Brühl possessions—the hanging gardens and Mattielli’s Neptune fountain from Brühl’s town and country houses—into the picture.",
      "authorial report of pictorial content", "The passage does not assign each motif to one of the two commissioned works or identify a particular house; do not create a one-to-one work-to-motif relation.",
      ["cand-2597", "cand-2590", "cand-3781", "cand-0458", "cand-10293", "cand-10294", "cand-1584", "cand-4174"],
      relation_candidate=True, candidate_identity_questions=[
          {"candidate_id": "cand-2597", "issue": "The note identifies the Maecenas picture as a Brühl commission; p.353 does not specify which commissioned picture contains each motif."},
          {"candidate_id": "cand-2590", "issue": "The note identifies the Flora picture as a Brühl commission; p.353 does not specify which commissioned picture contains each motif."},
      ]),
    quote(70, 71, "making Tiepolo insert into the picture two of Bruhl’s most treasured possessions: the hanging gardens and the\nNeptune fountain by Lorenzo Mattielli from his town and country houses."))

note1_locations = {
    "source_line_start": 185, "source_line_end": 185, "printed_page": 353,
    "pdf_physical_page": 7,
    "claim": "Haskell’s note locates the Maecenas picture at the Hermitage and the Flora picture at the De Young Memorial Museum in San Francisco, and cites Levey’s 1957 Burlington Magazine pages 89–91.",
    "speaker": "Haskell", "text_layer": "authorial bibliographic note",
    "qualification": "These are edition-era reported locations, not verified current custody. Levey’s article and cited pages were not independently consulted; bibliography matching is deferred to its S2 pass.",
    "mentioned_candidate_ids": ["cand-2597", "cand-2590", "cand-5795", "cand-10295", "cand-10296", "cand-10297", "cand-10298"],
    "cross_reference_segments": [BODY, PLATES],
    "cross_reference_text": "footnote 1 after the two pictures sent to Count Brühl; Plate 68b identifies the separate Maecenas engraving",
}
add_note_statement("st-chp14-p353-note1-picture-locations-and-source", note1_locations,
    quote(185, 185, "1 For the two pictures ordered by Algarotti for Briihl—the Maecenas is in the Hermitage and the Flora in the De Young Memorial Museum, San Francisco—see Levey, in Burlington Magazine, 1957, pp. 89-91."))

note1_engraving = {
    "source_line_start": 185, "source_line_end": 185, "printed_page": 353,
    "pdf_physical_page": 7,
    "claim": "The note says an engraving by Leonardis of the Maecenas is reproduced as Plate 68b.",
    "speaker": "Haskell", "text_layer": "authorial bibliographic note",
    "qualification": "The plate-list candidate is the Leonardis engraving of Maecenas presenting the Arts to Augustus; it is distinct from the reported engraving of the Banquet modello in the preceding paragraph.",
    "mentioned_candidate_ids": ["cand-3823", "cand-4104", "cand-2597", "cand-4191", "cand-4192", "cand-4193"],
    "cross_reference_segments": [BODY, PLATES],
    "cross_reference_text": "the existing Plate 68b caption identifies Tiepolo as designer and Leonardis as engraver",
}
add_note_statement("st-chp14-p353-note1-leonardis-engraving", note1_engraving,
    quote(185, 185, "An engraving by Leonardis of the Maecenas is reproduced as Plate 68b."))

# The p.352 open sentence is now closed by p.353 L64; retain the source-local statement and link.
prior_closure["qualifiers"]["claim"] = "Haskell begins contrasting Cleopatra’s gesture and attendants at p.352; p.353 L64 completes the comparison by describing the servants as more disciplined."
prior_closure["qualifiers"]["qualification"] = "The p.352 OCR segment ends after ‘and’; the continuation was read against CHP-14.pdf physical page 7 and linked to st-chp14-p353-cleopatra-comparison-closed."
prior_closure["qualifiers"]["cross_reference_segments"] = [BODY]
prior_closure["qualifiers"]["cross_reference_text"] = "p.353 L64 supplies ‘more disciplined’ and closes the sentence"

# Coverage transitions preserve the open p.353-to-p.354 sentence and later notes.
coverage_by_id[BODY_PREV].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L56-61",
    "note": "Printed p.352 read against CHP-14.pdf physical p.6. Its comparison sentence continues at p.353 L64 (‘more disciplined’) and is linked to st-chp14-p353-cleopatra-comparison-closed. S0 unchanged.",
})
coverage_by_id[BODY].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L64-71",
    "note": "Printed p.353 read against CHP-14.pdf physical p.7. L64 closes the p.352 comparison; the final phrase at L71 (‘As in The’) continues at p.354 L74, so retain partial. Note 1 at L185 links to the Brühl pictures and Plate 68b; S0 unchanged.",
})
coverage_by_id[NOTES].update({
    "disposition": "reviewed", "migration_status": "partial", "source_line_ranges": "L169-185",
    "note": "Printed notes p.347-p.353 read against CHP-14.pdf physical pages 1-7. P.353 note 1 is linked to the Maecenas and Flora picture locations, Levey citation, and Leonardis engraving at Plate 68b; later notes remain pending.",
})

# Preflight foreign keys and exact character anchors for this batch.
known_ids = set(candidate_by_id)
for row in mentions:
    if row["mention_id"].startswith("m-chp14-p353-"):
        seg = row["segment_id"]
        bounds = segment_bounds[seg]
        text = "\n".join(source_lines[bounds[0] - 1:bounds[1]])
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise SystemExit(f"mention span mismatch: {row['mention_id']} {row['surface_form']!r}")
        if row["candidate_id"] not in known_ids:
            raise SystemExit(f"mention candidate missing: {row['mention_id']}")
for row in statements:
    if row["statement_id"].startswith(("st-chp14-p353-",)):
        if row["source_file"] != SOURCE_FILE or row["origin"] != "book":
            raise SystemExit(f"statement source mismatch: {row['statement_id']}")
        for cid in (row["subject_candidate_id"], row["object_candidate_id"]):
            if cid and cid not in known_ids:
                raise SystemExit(f"statement candidate missing: {row['statement_id']} -> {cid}")
        for cid in row["qualifiers"].get("mentioned_candidate_ids", []):
            if cid not in known_ids:
                raise SystemExit(f"statement mentioned candidate missing: {row['statement_id']} -> {cid}")

new_mentions = [r for r in mentions if r["mention_id"].startswith("m-chp14-p353-")]
new_statements = [r for r in statements if r["statement_id"].startswith("st-chp14-p353-")]
for segment_id in (BODY, NOTES):
    spans = sorted(
        (int(row["start_char"]), int(row["end_char"]), row["mention_id"])
        for row in new_mentions if row["segment_id"] == segment_id
    )
    for left, right in zip(spans, spans[1:]):
        if left[1] > right[0]:
            surfaces = {row["mention_id"]: row["surface_form"] for row in new_mentions}
            raise SystemExit(
                f"overlapping planned mentions: {left[2]} {surfaces[left[2]]!r} "
                f"and {right[2]} {surfaces[right[2]]!r}"
            )
print(json.dumps({
    "mode": "apply" if args.apply else "dry-run",
    "new_candidates": len(new_candidates), "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_updates": {BODY_PREV: coverage_by_id[BODY_PREV], BODY: coverage_by_id[BODY], NOTES: coverage_by_id[NOTES]},
}, ensure_ascii=False, indent=2))

if args.apply:
    for path in (candidate_path, mention_path, statement_path, coverage_path):
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            if hashlib.sha256(backup.read_bytes()).digest() != hashlib.sha256(path.read_bytes()).digest():
                raise SystemExit(f"existing backup differs from current pre-write file: {backup.name}")
        else:
            shutil.copy2(path, backup)
    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(mention_path, mention_fields, mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
