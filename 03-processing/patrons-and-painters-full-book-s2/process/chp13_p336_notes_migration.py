"""Controlled S2 migration for printed p.336 notes and their body links."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
BODY = "chp-13:13_CHP-13_intro:l41-50"
PREVIOUS_BODY = "chp-13:13_CHP-13_intro:l32-39"
NEXT_BODY = "chp-13:13_CHP-13_intro:l52-59"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p336-notes-20261003"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write the reviewed p.336 notes migration")
args = parser.parse_args()


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


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")

source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
expected_prefixes = {
    195: "1 Hofer, p. 37.",
    196: "2 These paintings are divided between the museums of Washington, Copenhagen and Hull",
    197: "3 Morazzoni.",
    198: "4 G. A. Moschini, 1809, p. 5, and Gradenigo, p. 71.",
    199: "5 [G. B. Albrizzi] : Memorie.",
    200: "6 G. A. Moschini, 1815,1, p. xv.",
    201: "7 Morazzoni, p. 117.",
    202: "8 Letter from P. E. Gherardi to L. A. Muratori of 12 July 1749",
}
for line_number, prefix in expected_prefixes.items():
    if not source_lines[line_number - 1].startswith(prefix):
        raise SystemExit(f"canonical source changed at L{line_number}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
segments = read_jsonl(segment_path)
state = (len(candidates), len(mentions), len(statements), len(coverage_rows))
if state != (10139, 21916, 9800, 830):
    raise SystemExit(f"unexpected table pre-state: {state}")
candidate_by_id = {row["candidate_id"]: row for row in candidates}
max_candidate = max(int(row["candidate_id"].split("-")[1]) for row in candidates)
if max_candidate != 10152:
    raise SystemExit(f"unexpected maximum candidate ID: {max_candidate}")
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
segment_by_id = {row["segment_id"]: row for row in segments}

for segment_id in (BODY, PREVIOUS_BODY, NEXT_BODY, NOTES):
    if segment_id not in segment_by_id or segment_id not in coverage_by_id:
        raise SystemExit(f"required segment or coverage row missing: {segment_id}")
    segment = segment_by_id[segment_id]
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
        raise SystemExit(f"segment hash mismatch: {segment_id}")
if coverage_by_id[BODY]["migration_status"] != "partial":
    raise SystemExit("p.336 body is not awaiting its printed notes")
if coverage_by_id[NOTES]["migration_status"] != "partial":
    raise SystemExit("composite footnote segment is not partial")
if coverage_by_id[NOTES]["source_line_ranges"] != "L180-194":
    raise SystemExit("unexpected current source range in consolidated notes")

expected_body_markers = {
    "st-chp13-p336-gerbault-invited-orlando-subscriptions": 1,
    "st-chp13-p336-orlando-subscription-project-failed": 1,
    "st-chp13-p336-guardi-brothers-plagiarised-gerusalemme-illustrations": 2,
    "st-chp13-p336-novelli-provided-drawings-for-albrizzi-firm": 3,
    "st-chp13-p336-zais-provided-drawings-for-albrizzi-firm": 3,
    "st-chp13-p336-longhi-provided-drawings-for-albrizzi-firm": 3,
    "st-chp13-p336-adam-entrusted-book-sale-to-albrizzi": 4,
    "st-chp13-p336-albrizzi-proud-of-sacrifice-of-iphigenia": 5,
    "st-chp13-p336-albrizzi-patronised-zais": 6,
    "st-chp13-p336-albrizzi-held-high-regard-for-zais": 6,
    "st-chp13-p336-pasquali-friend-of-querini": 7,
    "st-chp13-p336-pasquali-friend-of-pilati": 7,
    "st-chp13-p336-pasquali-friend-of-albergati-capacelli": 7,
    "st-chp13-p336-gherardi-described-publishers-as-opposites": 8,
    "st-chp13-p336-gherardi-characterisation-of-publishers-open": 8,
}
false_same_line_markers = {
    "st-chp13-p336-piazzetta-designed-platnerus-frontispiece": (
        1, "The printed marker 1 follows the preceding Orlando Furioso project-failure clause, not this Platnerus frontispiece statement."
    ),
    "st-chp13-p336-albrizzi-took-zais-pictures-to-august-exhibition": (
        6, "The printed marker 6 follows the preceding high-regard sentence; it does not mark the later 1770 exhibition statement."
    ),
    "st-chp13-p336-zais-pictures-shown-at-1770-exhibition": (
        6, "The printed marker 6 follows the preceding high-regard sentence; it does not mark the later 1770 exhibition statement."
    ),
}
for statement_id, marker in {**expected_body_markers, **{k: v[0] for k, v in false_same_line_markers.items()}}.items():
    row = statement_by_id.get(statement_id)
    if row is None or row.get("segment_id") != BODY:
        raise SystemExit(f"required p.336 statement missing or moved: {statement_id}")
    if row.get("qualifiers", {}).get("footnote_marker") != marker:
        raise SystemExit(f"unexpected footnote marker on {statement_id}")
prior_continuation_id = "st-chp13-p335-gerusalemme-inspired-next-project-open"
prior_continuation = statement_by_id.get(prior_continuation_id)
if prior_continuation is None or prior_continuation.get("qualifiers", {}).get("continuation_footnote_marker") != 1:
    raise SystemExit("p.335-to-p.336 continuation footnote marker changed")

if candidate_by_id.get("cand-10007", {}).get("suggested_type") != "work":
    raise SystemExit("unexpected type for p.336 private-collection candidate")
if "L202 remains pending" not in candidate_by_id.get("cand-10008", {}).get("detail", ""):
    raise SystemExit("p.336 cited-letter candidate detail changed")

candidate_specs = [
    ("cand-10153", "Hofer (surname-only author cited in p.336 note 1)", "person",
     "Surname-only cited author; exact identity remains for S3."),
    ("cand-10154", "Hofer, p. 37 (p.336 note 1 citation locator)", "archive",
     "Citation locator only. The cited page was not independently consulted."),
    ("cand-10155", "Hull (city named for the reported distribution of Guardi canvases)", "place",
     "City named as one location of unnamed canvases; no museum or collection is identified."),
    ("cand-10156", "G. A. Moschini, 1809, p. 5 (p.336 note 4 citation locator)", "archive",
     "Abbreviated citation only; title, edition, and cited passage were not independently checked."),
    ("cand-10157", "Gradenigo, p. 71 (p.336 note 4 citation locator)", "archive",
     "Citation locator only; distinct from the existing Gradenigo p.91 citation; cited page not consulted."),
    ("cand-10158", "[G. B. Albrizzi]: Memorie (p.336 note 5 citation locator)", "archive",
     "Short title and bracketed author form as printed; publication identity and cited contents remain unchecked."),
    ("cand-10159", "G. A. Moschini, 1815, volume I, p. xv (p.336 note 6 citation locator)", "archive",
     "Citation locator only; title, edition, and cited page were not independently checked."),
    ("cand-10160", "Pietro Brandolese (person named in p.336 note 6)", "person",
     "Named by Haskell as the maker of a catalogue; personal identity is not expanded at S2."),
    ("cand-10161", "Untraced catalogue of Albrizzi’s print collection attributed to Pietro Brandolese", "archive",
     "Haskell says Brandolese made the catalogue but that he could not trace it. Title, date, and present location are not supplied."),
    ("cand-10162", "Morazzoni, p. 117 (p.336 note 7 citation locator)", "archive",
     "Citation locator only; title, edition, and cited passage were not independently checked."),
    ("cand-10163", "Albrizzi’s personal collection of prints (type unresolved)", "",
     "Haskell refers to a vast print collection. This is distinct from cand-10007, the drawings and paintings by Piazzetta. The taxonomy has no personal-collection type; retain the object with type undecided rather than coercing it to work, archive, or institution."),
]
new_candidates = []
for candidate_id, name, kind, detail in candidate_specs:
    if candidate_id in candidate_by_id:
        raise SystemExit(f"candidate ID already exists: {candidate_id}")
    if any(row["canonical_name"] == name for row in candidates):
        raise SystemExit(f"candidate name already exists: {name}")
    row = {field: "" for field in candidate_fields}
    line_number = {
        "cand-10153": 195, "cand-10154": 195, "cand-10155": 196,
        "cand-10156": 198, "cand-10157": 198, "cand-10158": 199,
        "cand-10159": 200, "cand-10160": 200, "cand-10161": 200,
        "cand-10162": 201, "cand-10163": 200,
    }[candidate_id]
    row.update({
        "candidate_id": candidate_id, "canonical_name": name, "suggested_type": kind,
        "status": "open", "detail": detail, "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
    })
    new_candidates.append(row)

all_candidate_ids = set(candidate_by_id) | {row["candidate_id"] for row in new_candidates}
note_text = "\n".join(source_lines[178:251])
note_lines = {number: source_lines[number - 1] for number in range(195, 203)}

mention_specs = [
    (195, "Hofer, p. 37", "cand-10154", "Short bibliographic citation; title unresolved."),
    (195, "Hofer", "cand-10153", "Surname-only cited author."),
    (196, "These paintings", "cand-9998", "Anaphoric reference to the Guardi canvases named in the body."),
    (196, "Washington", "cand-5523", "City named as a location; institution is not identified."),
    (196, "Copenhagen", "cand-9287", "City named as a location; institution is not identified."),
    (196, "Hull", "cand-10155", "City named as a location; institution is not identified."),
    (196, "London", "cand-1422", "City of unnamed private collections; no collection owner is identified."),
    (197, "Morazzoni.", "cand-10137", "Abbreviated citation with no page or title supplied."),
    (197, "Morazzoni", "cand-10129", "Surname-only cited author; exact identity remains unresolved."),
    (198, "G. A. Moschini, 1809, p. 5", "cand-10156", "Citation locator only."),
    (198, "G. A. Moschini", "cand-1709", "Named cited author; identity remains unresolved."),
    (198, "Gradenigo, p. 71", "cand-10157", "Citation locator only."),
    (198, "Gradenigo", "cand-8507", "Surname-only cited author."),
    (199, "[G. B. Albrizzi] : Memorie", "cand-10158", "Printed citation; the author is bracketed in the source."),
    (199, "[G. B. Albrizzi]", "cand-0025", "Bracketed author form as printed."),
    (200, "G. A. Moschini, 1815,1, p. xv", "cand-10159", "Citation locator as OCR; printed volume numeral is I."),
    (200, "G. A. Moschini", "cand-1709", "Named cited author; identity remains unresolved."),
    (200, "the same writer", "cand-1709", "Anaphoric reference to G. A. Moschini."),
    (200, "1806, HI, p. 49", "cand-8511", "Citation locator as OCR; printed volume numeral is III."),
    (200, "1924, p. 82", "cand-9561", "Citation locator; title unresolved."),
    (200, "Albrizzi", "cand-0025", "Named as owner of the print collection."),
    (200, "vast collection of prints", "cand-10163", "Collection object; taxonomy does not currently provide a collection type."),
    (200, "catalogue of these", "cand-10161", "Refers to the catalogue of the prints just mentioned."),
    (200, "Pietro Brandolese", "cand-10160", "Named as maker of the catalogue."),
    (201, "Morazzoni, p. 117", "cand-10162", "Citation locator only."),
    (201, "Morazzoni", "cand-10129", "Surname-only cited author; exact identity remains unresolved."),
    (202, "Letter from P. E. Gherardi to L. A. Muratori of 12 July 1749 in the Biblioteca Estense, Modena", "cand-10008", "Cited archival letter; the repository and contents are reported through Haskell."),
    (202, "P. E. Gherardi", "cand-1155", "Sender named in the archival citation."),
    (202, "L. A. Muratori", "cand-1717", "Recipient named in the archival citation."),
    (202, "Biblioteca Estense, Modena", "cand-8539", "Repository as named in the printed note."),
    (202, "Pasquali", "cand-1844", "Publisher named in the letter quotation."),
    (202, "Albrizzi", "cand-0025", "Publisher named in the letter quotation."),
]
existing_mention_keys = {
    (row["segment_id"], row["candidate_id"], str(row["start_char"]), str(row["end_char"]))
    for row in mentions
}
new_mentions = []
for index, (line_number, surface, candidate_id, note) in enumerate(mention_specs, start=1):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for mention {surface!r}: {candidate_id}")
    line_text = note_lines[line_number]
    positions = []
    cursor = 0
    while True:
        position = line_text.find(surface, cursor)
        if position < 0:
            break
        positions.append(position)
        cursor = position + 1
    if not positions:
        raise SystemExit(f"mention text is not exact at L{line_number}: {surface!r}")
    # Repeated author names are not needed in this batch; use the first exact occurrence.
    local_position = positions[0]
    local_segment_lines = source_lines[178:251]
    local_line = line_number - 179
    start = sum(len(line) + 1 for line in local_segment_lines[:local_line]) + local_position
    end = start + len(surface)
    if note_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    key = (NOTES, candidate_id, str(start), str(end))
    if key in existing_mention_keys:
        raise SystemExit(f"mention already exists: L{line_number} {surface!r} -> {candidate_id}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p336-notes-{index:03d}",
        "segment_id": NOTES, "candidate_id": candidate_id, "surface_form": surface,
        "start_char": start, "end_char": end, "note": note,
    })
    new_mentions.append(row)
    existing_mention_keys.add(key)

note_links = {
    1: [
        "st-chp13-p336-gerbault-invited-orlando-subscriptions",
        "st-chp13-p336-orlando-subscription-project-failed",
        "st-chp13-p335-gerusalemme-inspired-next-project-open",
    ],
    2: ["st-chp13-p336-guardi-brothers-plagiarised-gerusalemme-illustrations"],
    3: [
        "st-chp13-p336-novelli-provided-drawings-for-albrizzi-firm",
        "st-chp13-p336-zais-provided-drawings-for-albrizzi-firm",
        "st-chp13-p336-longhi-provided-drawings-for-albrizzi-firm",
    ],
    4: ["st-chp13-p336-adam-entrusted-book-sale-to-albrizzi"],
    5: ["st-chp13-p336-albrizzi-proud-of-sacrifice-of-iphigenia"],
    6: [
        "st-chp13-p336-albrizzi-patronised-zais",
        "st-chp13-p336-albrizzi-held-high-regard-for-zais",
    ],
    7: [
        "st-chp13-p336-pasquali-friend-of-querini",
        "st-chp13-p336-pasquali-friend-of-pilati",
        "st-chp13-p336-pasquali-friend-of-albergati-capacelli",
    ],
    8: [
        "st-chp13-p336-gherardi-described-publishers-as-opposites",
        "st-chp13-p336-gherardi-characterisation-of-publishers-open",
    ],
}
for linked_ids in note_links.values():
    for linked_id in linked_ids:
        if linked_id not in statement_by_id:
            raise SystemExit(f"footnote target statement missing: {linked_id}")

correction_196 = [{
    "source_line": 196, "ocr": "Hull and . private collections in London",
    "print": "Hull and private collections in London",
    "basis": "CHP-13.pdf physical page 5; the line-break hyphen is not a word or a named collection.",
}]
correction_200 = [
    {"source_line": 200, "ocr": "1815,1", "print": "1815, I", "basis": "CHP-13.pdf physical page 5."},
    {"source_line": 200, "ocr": "1806, HI", "print": "1806, III", "basis": "CHP-13.pdf physical page 5."},
    {"source_line": 200, "ocr": "Albrizzi��s", "print": "Albrizzi’s", "basis": "CHP-13.pdf physical page 5."},
]
correction_202 = [
    {"source_line": 202, "ocr": "Pasquali ��", "print": "Pasquali è", "basis": "CHP-13.pdf physical page 5."},
    {"source_line": 202, "ocr": "dell��Albrizzi", "print": "dell’Albrizzi", "basis": "CHP-13.pdf physical page 5."},
    {"source_line": 202, "ocr": "int��resse", "print": "interesse", "basis": "CHP-13.pdf physical page 5."},
]

statement_specs = [
    {
        "id": "st-chp13-p336-note1-hofer-citation", "line": 195,
        "subject": "cand-10153", "object": "cand-10154", "predicate": "cites_source_for_failed_orlando_project",
        "claim": "Printed note 1 cites Hofer, page 37, after the report that the projected Orlando Furioso edition came to nothing.",
        "qualification": "Citation locator only; the cited page was not independently consulted and does not establish any edition was published.",
        "mentioned": ["cand-10153", "cand-10154", "cand-9997"],
        "linked": note_links[1], "number": 1, "layer": "bibliographic citation locator",
        "citations": [{"source_candidate_id": "cand-10154", "author_candidate_id": "cand-10153", "page": "37"}],
    },
    {
        "id": "st-chp13-p336-note2-reported-canvas-distribution", "line": 196,
        "subject": "cand-9998", "object": None, "predicate": "reported_distribution_across_locations",
        "claim": "The note says the Guardi canvases are divided among museums in Washington, Copenhagen, and Hull and private collections in London.",
        "qualification": "The note does not identify individual canvases, any museum, or private collection owners. These are locations reported by Haskell, not independently verified current holdings.",
        "mentioned": ["cand-9998", "cand-5523", "cand-9287", "cand-10155", "cand-1422"],
        "linked": note_links[2], "number": 2, "layer": "footnote report", "relation_candidate": True,
        "ocr_corrections": correction_196,
    },
    {
        "id": "st-chp13-p336-note3-morazzoni-locator", "line": 197,
        "subject": "cand-10129", "object": "cand-10137", "predicate": "cites_morazzoni_without_page_locator",
        "claim": "Printed note 3 cites Morazzoni without supplying a title or page.",
        "qualification": "Abbreviated citation only; the cited work is not identified or independently consulted.",
        "mentioned": ["cand-10129", "cand-10137"],
        "linked": note_links[3], "number": 3, "layer": "bibliographic citation locator",
    },
    {
        "id": "st-chp13-p336-note4-moschini-gradenigo-locators", "line": 198,
        "subject": None, "object": None, "predicate": "cites_two_bibliographic_locators",
        "claim": "Printed note 4 cites G. A. Moschini, 1809, page 5, and Gradenigo, page 71.",
        "qualification": "The note supplies abbreviated references only; neither cited page was independently consulted.",
        "mentioned": ["cand-1709", "cand-10156", "cand-8507", "cand-10157"],
        "linked": note_links[4], "number": 4, "layer": "bibliographic citation locator",
        "citations": [
            {"source_candidate_id": "cand-10156", "author_candidate_id": "cand-1709", "year": "1809", "page": "5"},
            {"source_candidate_id": "cand-10157", "author_candidate_id": "cand-8507", "page": "71"},
        ],
    },
    {
        "id": "st-chp13-p336-note5-albrizzi-memorie-locator", "line": 199,
        "subject": "cand-0025", "object": "cand-10158", "predicate": "cites_albrizzi_memorie",
        "claim": "Printed note 5 gives “[G. B. Albrizzi]: Memorie” as a citation.",
        "qualification": "The author form is bracketed in the source; full bibliographic identity and cited contents remain unchecked.",
        "mentioned": ["cand-0025", "cand-10158"],
        "linked": note_links[5], "number": 5, "layer": "bibliographic citation locator",
        "citations": [{"source_candidate_id": "cand-10158", "author_candidate_id": "cand-0025", "title_as_printed": "Memorie"}],
    },
    {
        "id": "st-chp13-p336-note6-print-collection-references", "line": 200,
        "subject": "cand-10163", "object": None, "predicate": "cites_references_to_print_collection",
        "claim": "Printed note 6 points to Moschini 1815, volume I, page xv; Moschini 1806, volume III, page 49; and Moschini 1924, page 82, for references to Albrizzi’s large print collection.",
        "qualification": "These are citation locators reported by Haskell, not independently consulted evidence. The print collection is a distinct type-unresolved object, not cand-10007’s Piazzetta drawings and paintings.",
        "mentioned": ["cand-1709", "cand-10159", "cand-8511", "cand-9561", "cand-10163"],
        "linked": note_links[6], "number": 6, "layer": "bibliographic citation locator",
        "citations": [
            {"source_candidate_id": "cand-10159", "author_candidate_id": "cand-1709", "year": "1815", "volume": "I", "page": "xv"},
            {"source_candidate_id": "cand-8511", "author_candidate_id": "cand-1709", "year": "1806", "volume": "III", "page": "49"},
            {"source_candidate_id": "cand-9561", "author_candidate_id": "cand-1709", "year": "1924", "page": "82"},
        ],
        "ocr_corrections": correction_200, "relation_candidate": False,
    },
    {
        "id": "st-chp13-p336-note6-brandolese-catalogue-untraced", "line": 200,
        "subject": "cand-10160", "object": "cand-10161", "predicate": "catalogue_reported_as_untraced",
        "claim": "Haskell says Pietro Brandolese made a catalogue of the prints but that he was unable to trace it.",
        "qualification": "The note gives no catalogue title, date, or present location; the existence and contents are reported through Haskell.",
        "mentioned": ["cand-0025", "cand-10160", "cand-10161", "cand-10163"],
        "linked": note_links[6], "number": 6, "layer": "authorial statement in footnote",
        "ocr_corrections": correction_200,
    },
    {
        "id": "st-chp13-p336-note7-morazzoni-page117-locator", "line": 201,
        "subject": "cand-10129", "object": "cand-10162", "predicate": "cites_morazzoni_page",
        "claim": "Printed note 7 cites Morazzoni, page 117.",
        "qualification": "Citation locator only; the cited work was not independently consulted.",
        "mentioned": ["cand-10129", "cand-10162"],
        "linked": note_links[7], "number": 7, "layer": "bibliographic citation locator",
        "citations": [{"source_candidate_id": "cand-10162", "author_candidate_id": "cand-10129", "page": "117"}],
    },
    {
        "id": "st-chp13-p336-note8-letter-locator", "line": 202,
        "subject": "cand-1155", "object": "cand-1717", "predicate": "addressed_letter_to",
        "claim": "Printed note 8 identifies a letter from P. E. Gherardi to L. A. Muratori dated 12 July 1749 and names the Biblioteca Estense, Modena as its repository.",
        "qualification": "The letter and repository are cited by Haskell and were not independently consulted. The archival document is recorded as the cited source, not direct access to the document.",
        "mentioned": ["cand-1155", "cand-1717", "cand-10008", "cand-8539"],
        "linked": note_links[8], "number": 8, "layer": "archival citation locator",
        "quote_mode": "citation", "relation_candidate": True,
        "citations": [{"source_candidate_id": "cand-10008", "repository_candidate_id": "cand-8539", "date": "1749-07-12"}],
        "cross_reference_segments": [NEXT_BODY],
    },
    {
        "id": "st-chp13-p336-note8-letter-characterisation", "line": 202,
        "subject": "cand-1155", "object": None, "predicate": "quoted_contrast_between_pasquali_and_albrizzi",
        "claim": "The Italian passage quoted in note 8 says Pasquali was Albrizzi’s opposite and contrasts their caution, support, and prospects in their affairs.",
        "qualification": "This is the letter as quoted by Haskell, not an independently consulted archival statement; retain it as attributed characterization rather than verified biography.",
        "mentioned": ["cand-1155", "cand-1844", "cand-0025", "cand-10008"],
        "linked": note_links[8], "number": 8, "layer": "archival quotation reproduced in footnote",
        "quote_mode": "italian_quote", "ocr_corrections": correction_202,
        "cross_reference_segments": [NEXT_BODY],
    },
]

new_statements = []
for spec in statement_specs:
    statement_id = spec["id"]
    if statement_id in statement_by_id:
        raise SystemExit(f"statement already exists: {statement_id}")
    for candidate_id in [spec["subject"], spec["object"], *spec["mentioned"]]:
        if candidate_id is not None and candidate_id not in all_candidate_ids:
            raise SystemExit(f"candidate FK missing in {statement_id}: {candidate_id}")
    line_text = note_lines[spec["line"]]
    if spec.get("quote_mode") == "citation":
        quote = line_text.split(": ", 1)[0]
    elif spec.get("quote_mode") == "italian_quote":
        quote = line_text.split(": ", 1)[1]
    else:
        quote = line_text
    if quote not in line_text:
        raise SystemExit(f"statement quote is not anchored at L{spec['line']}: {statement_id}")
    qualifiers = {
        "source_line_start": spec["line"], "source_line_end": spec["line"],
        "printed_page": 336, "pdf_physical_page": 5, "claim": spec["claim"],
        "speaker": spec.get("speaker", "Haskell, printed footnote"),
        "text_layer": spec["layer"], "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"], "footnote_number": spec["number"],
        "linked_body_statement_ids": spec["linked"],
    }
    if spec.get("relation_candidate"):
        qualifiers["relation_candidate"] = True
    if spec.get("citations"):
        qualifiers["citations"] = spec["citations"]
    if spec.get("ocr_corrections"):
        qualifiers["ocr_corrections"] = spec["ocr_corrections"]
    if spec.get("cross_reference_segments"):
        qualifiers["cross_reference_segments"] = spec["cross_reference_segments"]
    if statement_id == "st-chp13-p336-note8-letter-locator":
        qualifiers["cited_source_candidate_id"] = "cand-10008"
        qualifiers["cited_repository_candidate_id"] = "cand-8539"
    new_statements.append({
        "statement_id": statement_id, "segment_id": NOTES,
        "subject_candidate_id": spec["subject"], "object_candidate_id": spec["object"],
        "predicate": spec["predicate"], "qualifiers": qualifiers,
        "original_quote": quote, "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    })

for statement_id, marker in expected_body_markers.items():
    body_statement = statement_by_id[statement_id]
    qualifiers = body_statement.setdefault("qualifiers", {})
    qualifiers["footnote_text_pending"] = False
    qualifiers["footnote_body_link_status"] = "linked"
    note_ids = [row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_number"] == marker]
    qualifiers["footnote_note_statement_ids"] = sorted(set(qualifiers.get("footnote_note_statement_ids", [])) | set(note_ids))
    refs = qualifiers.setdefault("footnote_refs", [])
    note_lines_for_marker = [row["qualifiers"]["source_line_start"] for row in new_statements if row["qualifiers"]["footnote_number"] == marker]
    ref = {
        "footnote_marker": str(marker), "footnote_printed_page": 336,
        "footnote_text_pending": False, "footnote_segment": NOTES,
        "footnote_line_range": f"L{min(note_lines_for_marker)}-L{max(note_lines_for_marker)}",
        "footnote_body_link_status": "linked", "footnote_note_statement_ids": note_ids,
    }
    if not any(item.get("footnote_marker") == str(marker) and item.get("footnote_printed_page") == 336 for item in refs):
        refs.append(ref)

for statement_id, (marker, explanation) in false_same_line_markers.items():
    qualifiers = statement_by_id[statement_id].setdefault("qualifiers", {})
    for key in (
        "footnote_marker", "footnote_printed_page", "footnote_text_pending",
        "footnote_segment", "footnote_body_link_status", "cross_reference_segments",
        "footnote_note_statement_ids", "footnote_refs",
    ):
        qualifiers.pop(key, None)
    qualifiers["footnote_scope_exclusion"] = explanation

prior_q = prior_continuation.setdefault("qualifiers", {})
prior_q["continuation_footnote_text_pending"] = False
prior_q["continuation_footnote_body_link_status"] = "linked"
prior_q["continuation_footnote_note_statement_ids"] = [
    row["statement_id"] for row in new_statements if row["qualifiers"]["footnote_number"] == 1
]
prior_q["continuation_footnote_citation_locator"] = "Hofer, p. 37"
prior_q["qualification"] = (
    "The p.336 printed note 1 cites Hofer, p.37; that citation is now recorded at L195. "
    "The projected edition did not come to fruition, as the p.336 continuation statement records; "
    "do not present it as published."
)
prior_refs = prior_q.setdefault("footnote_refs", [])
if not any(item.get("footnote_marker") == "1" and item.get("footnote_printed_page") == 336 for item in prior_refs):
    prior_refs.append({
        "footnote_marker": "1", "footnote_printed_page": 336,
        "footnote_text_pending": False, "footnote_segment": NOTES, "footnote_line_range": "L195",
        "footnote_body_link_status": "linked",
        "footnote_note_statement_ids": prior_q["continuation_footnote_note_statement_ids"],
    })

candidate_by_id["cand-10007"]["suggested_type"] = ""
candidate_by_id["cand-10007"]["detail"] = (
    "Haskell describes a private collection of several hundred drawings and many paintings by Piazzetta, "
    "including the Sacrifice of Iphigenia. A personal collection is not one artwork under the current taxonomy; "
    "retain the candidate with type unresolved rather than work. It is distinct from the published academic-drawing collection."
)
candidate_by_id["cand-10008"]["detail"] = (
    "Printed p.336 note 8 identifies this as the source of the comparison between Albrizzi and Pasquali, "
    "quotes its characterization, and names the Biblioteca Estense, Modena. The archival letter is cited by Haskell "
    "but was not independently consulted."
)

coverage_by_id[BODY]["migration_status"] = "complete"
coverage_by_id[BODY]["source_line_ranges"] = "L41-50"
coverage_by_id[BODY]["note"] = (
    "Printed p.336 body checked against CHP-13.pdf physical page 5. Notes 1-8 at L195-202 are migrated and linked; "
    "same-OCR-line false footnote assignments to the Platnerus and later exhibition statements are removed. "
    "The Gherardi quotation is cross-referenced to p.337."
)
coverage_by_id[NOTES]["source_line_ranges"] = "L180-202"
coverage_by_id[NOTES]["note"] = (
    "Notes L180-191 (pp.332-334) and L192-202 (pp.335-336) are migrated. "
    "L203-238 and mirrored caption lines L247-248 remain to process or map; the composite segment remains partial."
)

all_candidates = candidates + new_candidates
all_mentions = mentions + new_mentions
all_statements = statements + new_statements
print(
    f"p.336 notes dry-run: +{len(new_candidates)} candidates, +{len(new_mentions)} mentions, "
    f"+{len(new_statements)} statements; linked notes 1-8; removed 3 false same-line markers; "
    "corrected cand-10007 collection type to unresolved"
)
print(
    f"totals: candidates={len(all_candidates)}, mentions={len(all_mentions)}, "
    f"statements={len(all_statements)}, coverage={len(coverage_rows)}"
)
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
write_csv(candidate_path, candidate_fields, all_candidates)
write_csv(mention_path, mention_fields, all_mentions)
write_jsonl(statement_path, all_statements)
write_csv(coverage_path, coverage_fields, list(coverage_by_id.values()))
print(f"applied; four recovery copies created with suffix {BACKUP_SUFFIX}")
