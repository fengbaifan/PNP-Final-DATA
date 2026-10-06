"""Controlled S2 migration for printed p.345 notes 1-3; dry-run by default."""
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
VISUAL = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro_plates_visual-transcription.md"
BODY = "chp-13:13_CHP-13_intro:l161-171"
NOTES = "chp-13:13_CHP-13_intro:l179-251"
MIRROR_SEGMENTS = (
    "chp-13:13_CHP-13_intro_plates_visual-transcription:l1-3",
    "chp-13:13_CHP-13_intro_plates_visual-transcription:l5-7",
)
SOURCE_SHA = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p345-notes-20261003"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed p.345 footnote migration")
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
    raise SystemExit("canonical chapter 13 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-13 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in {
    249: "1 Pietro Monaco: Raccolta Ji centododici stampe.",
    250: "2 Letter of 4 February 1763/4 in British Museum, Add. MSS. 23,729, f. 49.",
    251: "3 Toni is referred to in G. A. Moschini, 1924, p. 167",
    171: "This was written in 1790, but internal evidence makes it clear that it was sketched out by 1762.",
}.items():
    if required not in source_lines[line_number - 1]:
        raise SystemExit(f"required source text changed at L{line_number}")
reversed_57 = source_lines[246][::-1].casefold()
reversed_58 = source_lines[247][::-1].casefold()
if not all(term in reversed_57 for term in ("pasquali", "gerusalemme liberata", "frontispiece", "endpiece", "vol.2")):
    raise SystemExit("p.345 mirrored L247 no longer matches the Plate 57 captions")
if not all(term in reversed_58 for term in ("z occhi", "zanetti", "longhi", "sasso")):
    raise SystemExit("p.345 mirrored L248 no longer matches the Plate 58 captions")
visual_text = VISUAL.read_text(encoding="utf-8-sig")
for required in (
    "Plate 57\na. PIAZZETTA:",
    "b. NOVELLI:",
    "Plate 58\na. ZOCCHI:",
    "b. A. LONGHI:",
):
    if required not in visual_text:
        raise SystemExit(f"derived visual transcription changed: {required!r}")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
statements = read_jsonl(statement_path)
candidate_by_id = {row["candidate_id"]: row for row in candidates}
statement_by_id = {row["statement_id"]: row for row in statements}
coverage = {row["segment_id"]: row for row in coverage_rows}
table_state = (len(candidates), max(int(row["candidate_id"].split("-")[1]) for row in candidates), len(mentions), len(statements))
if table_state != (10205, 10218, 22145, 9875):
    raise SystemExit(f"unexpected table pre-state: {table_state}")
if BODY not in coverage or NOTES not in coverage:
    raise SystemExit("p.345 body or consolidated-notes coverage row missing")
if coverage[NOTES]["source_line_ranges"] != "L180-246":
    raise SystemExit("consolidated-notes cursor changed")
if coverage[BODY]["migration_status"] != "partial":
    raise SystemExit("p.345 body coverage state changed")
for segment_id in MIRROR_SEGMENTS:
    if segment_id not in coverage or coverage[segment_id]["migration_status"] != "complete":
        raise SystemExit(f"mirror-caption segment is not already complete: {segment_id}")
if coverage["chp-13:13_CHP-13_intro:l124-139"]["migration_status"] != "complete":
    raise SystemExit("Plate 57 mirrored-caption source segment is not complete")
if any(row["segment_id"] == NOTES and row["mention_id"].startswith("m-s2-ch13-p345-notes-") for row in mentions):
    raise SystemExit("p.345 note mentions already exist")

required_candidate_ids = (
    "cand-1682", "cand-1709", "cand-1760", "cand-2516", "cand-2640", "cand-2719",
    "cand-5986", "cand-6589", "cand-7618", "cand-10115", "cand-10116", "cand-10119",
)
for candidate_id in required_candidate_ids:
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"required reusable candidate missing: {candidate_id}")
new_candidate_ids = {f"cand-{number}" for number in range(10219, 10222)}
if new_candidate_ids & set(candidate_by_id):
    raise SystemExit(f"candidate IDs already exist: {sorted(new_candidate_ids & set(candidate_by_id))}")
new_candidates = []


def add_candidate(candidate_id, name, kind, detail, line_number):
    if any(row["canonical_name"].casefold() == name.casefold() for row in candidates):
        raise SystemExit(f"candidate name already exists: {name}")
    row = {field: "" for field in candidate_fields}
    row.update({
        "candidate_id": candidate_id,
        "canonical_name": name,
        "suggested_type": kind,
        "status": "open",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{NOTES}#L{line_number}",
        "detail": detail,
    })
    new_candidates.append(row)


add_candidate(
    "cand-10219",
    "Raccolta di centododici stampe (Pietro Monaco; p.345 note 1, edition unresolved)",
    "archive",
    "P.345 note 1 gives the title of Monaco's 112-print collection without a date or edition. Keep distinct from the bibliography's 1763 edition candidate cand-7618 and the posthumous 1779 edition cand-10116 until S3 resolves their relationship.",
    249,
)
add_candidate(
    "cand-10220",
    "G. A. Moschini, 1924, p.167 (citation locator)",
    "archive",
    "P.345 note 3 cites page 167 for Toni and says Moschini derives his information from a manuscript life by P. A. Novelli. The cited page was not consulted.",
    251,
)
add_candidate(
    "cand-10221",
    "Manuscript life of Don Pietro Antonio Toni by P. A. Novelli (Seminario Patriarcale, Venice, MSS. 788.25)",
    "archive",
    "P.345 note 3 identifies this manuscript life and shelfmark, reporting that it was written in 1790 but internally appears to have been sketched out by 1762. Manuscript not consulted; attribution and date remain Haskell's report.",
    251,
)

all_candidate_ids = set(candidate_by_id) | new_candidate_ids
candidate_by_id["cand-10119"]["detail"] += " P.345 note 2 gives the exact locator British Museum, Add. MSS. 23,729, f. 49, and the printed date 4 February 1763/4; retain the ambiguous year form and do not resolve the shelfmark independently."
candidate_by_id["cand-5986"]["detail"] += " P.345 note 2 also cites this repository for the Monaco-to-Strange letter in Add. MSS. 23,729, f. 49; the manuscript was not consulted."
candidate_by_id["cand-7618"]["detail"] += " P.345 note 1 supplies a matching short title but no year; do not infer that its note names this 1763 edition rather than the 1779 edition."
candidate_by_id["cand-10116"]["detail"] += " P.345 note 1 supplies the title Raccolta di centododici stampe but no year; edition mapping against the 1763 bibliography candidate cand-7618 remains unresolved."

notes_text = "\n".join(source_lines[178:251])
notes_offsets = {}
offset = 0
for line_number, line_text in enumerate(source_lines[178:251], start=179):
    notes_offsets[line_number] = offset
    offset += len(line_text) + 1
body_text = "\n".join(source_lines[160:171])
body_offsets = {}
offset = 0
for line_number, line_text in enumerate(source_lines[160:171], start=161):
    body_offsets[line_number] = offset
    offset += len(line_text) + 1
new_mentions = []


def add_mention(line_number, surface, candidate_id, segment, segment_text, offsets, note="", occurrence=0):
    if candidate_id not in all_candidate_ids:
        raise SystemExit(f"candidate FK missing for mention {surface!r}: {candidate_id}")
    line_text = source_lines[line_number - 1]
    positions, cursor = [], 0
    while True:
        at = line_text.find(surface, cursor)
        if at < 0:
            break
        positions.append(at)
        cursor = at + 1
    if occurrence >= len(positions):
        raise SystemExit(f"mention text missing at L{line_number}: {surface!r}")
    start = offsets[line_number] + positions[occurrence]
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit(f"mention offset mismatch at L{line_number}: {surface!r}")
    if any(row["segment_id"] == segment and row["candidate_id"] == candidate_id and row["start_char"] == str(start) and row["end_char"] == str(end) for row in mentions + new_mentions):
        raise SystemExit(f"duplicate mention at L{line_number}: {surface!r}")
    row = {field: "" for field in mention_fields}
    row.update({
        "mention_id": f"m-s2-ch13-p345-notes-{len(new_mentions)+1:03d}",
        "segment_id": segment,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })
    new_mentions.append(row)


mention_specs = [
    (249, "Pietro Monaco", "cand-1682", NOTES, notes_text, notes_offsets, "Reuse the indexed engraver candidate; S3 identity alignment remains pending."),
    (249, "Raccolta Ji centododici stampe", "cand-10219", NOTES, notes_text, notes_offsets, "S0 reads Ji; the print reads di. Edition is unspecified."),
    (250, "Letter of 4 February 1763/4", "cand-10119", NOTES, notes_text, notes_offsets, "Printed date retained as ambiguous 1763/4."),
    (250, "British Museum", "cand-5986", NOTES, notes_text, notes_offsets, "Repository named in the citation; current holdings were not checked."),
    (250, "Add. MSS. 23,729, f. 49", "cand-10119", NOTES, notes_text, notes_offsets, "Printed shelfmark; manuscript not consulted."),
    (251, "Toni", "cand-2640", NOTES, notes_text, notes_offsets, "Reuse the person candidate named in the p.345 body."),
    (251, "G. A. Moschini, 1924, p. 167", "cand-10220", NOTES, notes_text, notes_offsets, "Short-form citation; cited page not consulted."),
    (251, "G. A. Moschini", "cand-1709", NOTES, notes_text, notes_offsets, "Author named in the citation."),
    (251, "manuscript life by the artist P. A. Novelli", "cand-10221", NOTES, notes_text, notes_offsets, "Specific manuscript source described by Haskell; not consulted."),
    (251, "P. A. Novelli", "cand-1760", NOTES, notes_text, notes_offsets, "Person as named in the note; reuse the chapter's candidate pending S3."),
    (251, "Seminario Patriarcale", "cand-6589", NOTES, notes_text, notes_offsets, "Repository as named in the note; manuscript not consulted."),
    (251, "Venice", "cand-2719", NOTES, notes_text, notes_offsets, "Repository location as printed."),
    (251, "MSS. 788. 25", "cand-10221", NOTES, notes_text, notes_offsets, "Printed shelfmark, preserving spacing as transcribed."),
    (171, "1790", "cand-10221", BODY, body_text, body_offsets, "Year stated for the manuscript life; Haskell's report, not independently verified."),
    (171, "1762", "cand-10221", BODY, body_text, body_offsets, "Earlier sketch date inferred from internal evidence by Haskell; not independently verified."),
]
for spec in mention_specs:
    add_mention(*spec)

body_note_targets = {
    "1": [
        "st-chp13-p345-monaco-1763-1779-editions",
        "st-chp13-p345-monaco-reproduced-work-groups",
    ],
    "2": ["st-chp13-p345-monaco-letter-to-strange-seventeen-pictures"],
    "3": [
        "st-chp13-p345-toni-born-near-modena",
        "st-chp13-p345-toni-settled-in-venice",
        "st-chp13-p345-toni-ricci-friendship-and-care",
        "st-chp13-p345-ricci-engravings-given-to-toni",
        "st-chp13-p345-ricci-modello-given-to-toni",
        "st-chp13-p345-toni-gambled-on-ricci-behalf",
        "st-chp13-p345-toni-contact-with-pittoni",
        "st-chp13-p345-toni-adviser-and-patron-to-novelli",
        "st-chp13-p345-toni-collections-left-to-novelli-1748",
        "st-chp13-p345-toni-discussions-may-have-shaped-novelli",
        "st-chp13-p345-note3-date-continuation",
    ],
}
new_statement_specs = [
    {
        "id": "st-chp13-p345-notes-note1-monaco-112-title", "marker": "1", "line": 249,
        "subject": "cand-10219", "object": None, "predicate": "printed_note_supplies_title_for_monaco_112_print_collection",
        "claim": "P.345 note 1 gives the title Raccolta di centododici stampe for the Pietro Monaco collection discussed on the page.",
        "qualification": "The note supplies no year or edition. Its title may correspond to the bibliography's 1763 candidate or the posthumous 1779 edition; the mapping remains unresolved for S3. The cited publication was not consulted.",
        "mentioned": ["cand-10219", "cand-1682", "cand-7618", "cand-10115", "cand-10116"],
        "citations": [{"source_candidate_id": "cand-10219", "author_candidate_id": "cand-1682", "title_as_printed": "Raccolta di centododici stampe", "edition_mapping_candidates": ["cand-7618", "cand-10116"]}],
        "linked": body_note_targets["1"],
        "ocr_corrections": [{"source_line": 249, "ocr": "Raccolta Ji", "print": "Raccolta di", "basis": "CHP-13.pdf physical page 18."}],
    },
    {
        "id": "st-chp13-p345-notes-note2-monaco-strange-letter-locator", "marker": "2", "line": 250,
        "subject": "cand-10119", "object": "cand-2516", "predicate": "printed_note_gives_locator_for_monaco_letter_to_strange",
        "claim": "P.345 note 2 locates Monaco's letter to John Strange at the British Museum, Add. MSS. 23,729, folio 49, and prints its date as 4 February 1763/4.",
        "qualification": "Preserve 1763/4 as printed; do not choose a year. The letter and repository catalogue were not consulted.",
        "mentioned": ["cand-10119", "cand-5986"],
        "citations": [{"source_candidate_id": "cand-10119", "recipient_candidate_id": "cand-2516", "repository_candidate_id": "cand-5986", "date_as_printed": "4 February 1763/4", "shelfmark": "Add. MSS. 23,729, f. 49"}],
        "linked": body_note_targets["2"],
    },
    {
        "id": "st-chp13-p345-notes-note3-moschini-novelli-manuscript-provenance", "marker": "3", "line": 251,
        "subject": "cand-10220", "object": "cand-10221", "predicate": "moschini_1924_p167_derives_toni_information_from_novelli_manuscript",
        "claim": "Haskell's note says Toni is discussed in Moschini, 1924, page 167, and that Moschini derives all his information from a manuscript life by the artist P. A. Novelli at Seminario Patriarcale, Venice, MSS. 788.25.",
        "qualification": "The note continues at p.345 L171: Haskell says the manuscript was written in 1790 but internal evidence indicates it was sketched out by 1762. This provenance and dating are Haskell's report; the manuscript and cited page were not independently consulted. The note's marker follows the opening Toni biographical sentence, while its wording identifies the manuscript as the source for the Toni account; preserve that attribution without presenting independent verification.",
        "mentioned": ["cand-10220", "cand-1709", "cand-10221", "cand-1760", "cand-6589", "cand-2719", "cand-2640"],
        "citations": [{"source_candidate_id": "cand-10220", "author_candidate_id": "cand-1709", "year": "1924", "page": "167", "manuscript_candidate_id": "cand-10221", "manuscript_author_candidate_id": "cand-1760", "repository_candidate_id": "cand-6589", "shelfmark": "MSS. 788.25"}],
        "linked": body_note_targets["3"],
    },
]

new_statements = []
note_statement_ids_by_marker = {str(number): [] for number in range(1, 4)}
for spec in new_statement_specs:
    for candidate_id in spec["mentioned"]:
        if candidate_id not in all_candidate_ids:
            raise SystemExit(f"statement candidate missing: {spec['id']} -> {candidate_id}")
    qualifiers = {
        "source_line_start": spec["line"],
        "source_line_end": spec["line"],
        "printed_page": 345,
        "pdf_physical_page": 18,
        "claim": spec["claim"],
        "speaker": "Haskell, printed footnote",
        "text_layer": "secondary source note and citation",
        "qualification": spec["qualification"],
        "mentioned_candidate_ids": spec["mentioned"],
        "footnote_marker": spec["marker"],
        "footnote_printed_page": 345,
        "linked_body_statement_ids": spec["linked"],
        "citations": spec["citations"],
        "relation_candidate": False,
    }
    if spec.get("ocr_corrections"):
        qualifiers["ocr_corrections"] = spec["ocr_corrections"]
    row = {
        "statement_id": spec["id"],
        "segment_id": NOTES,
        "subject_candidate_id": spec["subject"],
        "object_candidate_id": spec["object"],
        "predicate": spec["predicate"],
        "qualifiers": qualifiers,
        "original_quote": source_lines[spec["line"] - 1],
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
    }
    if row["statement_id"] in statement_by_id:
        raise SystemExit(f"duplicate statement ID: {row['statement_id']}")
    new_statements.append(row)
    note_statement_ids_by_marker[spec["marker"]].append(spec["id"])

for marker, targets in body_note_targets.items():
    for statement_id in targets:
        if statement_id not in statement_by_id:
            raise SystemExit(f"p.345 marker {marker} target missing: {statement_id}")
        pending = statement_by_id[statement_id].get("qualifiers", {}).get("note_refs_pending", [])
        if not any(ref.get("printed_note") == int(marker) and ref.get("segment_id") == NOTES for ref in pending):
            raise SystemExit(f"p.345 marker {marker} is not pending on {statement_id}")

# Convert only the three printed p.345 markers to completed, source-local links.
for statement_id, row in statement_by_id.items():
    if row.get("segment_id") != BODY:
        continue
    q = row.setdefault("qualifiers", {})
    pending = q.get("note_refs_pending", [])
    kept = []
    for ref in pending:
        if ref.get("segment_id") != NOTES:
            kept.append(ref)
            continue
        marker = str(ref.get("printed_note"))
        if marker not in body_note_targets or statement_id not in body_note_targets[marker]:
            raise SystemExit(f"unexpected p.345 note target: marker {marker}, {statement_id}")
        refs = q.setdefault("footnote_refs", [])
        if any(r.get("footnote_marker") == marker and r.get("footnote_printed_page") == 345 for r in refs):
            raise SystemExit(f"duplicate p.345 footnote ref on {statement_id}")
        note_ids = note_statement_ids_by_marker[marker]
        refs.append({
            "footnote_marker": marker,
            "footnote_printed_page": 345,
            "footnote_text_pending": False,
            "footnote_segment": NOTES,
            "footnote_line_range": f"L{248 + int(marker)}",
            "footnote_body_link_status": "linked",
            "footnote_note_statement_ids": note_ids,
        })
        q["footnote_note_statement_ids"] = sorted(set(q.get("footnote_note_statement_ids", [])) | set(note_ids))
        q["footnote_text_pending"] = False
        q["footnote_body_link_status"] = "linked"
    if kept:
        q["note_refs_pending"] = kept
    else:
        q.pop("note_refs_pending", None)

for marker, targets in body_note_targets.items():
    note_ids = note_statement_ids_by_marker[marker]
    for statement_id in targets:
        refs = statement_by_id[statement_id].get("qualifiers", {}).get("footnote_refs", [])
        if not any(
            ref.get("footnote_marker") == marker
            and ref.get("footnote_printed_page") == 345
            and not ref.get("footnote_text_pending")
            and ref.get("footnote_note_statement_ids") == note_ids
            for ref in refs
        ):
            raise SystemExit(f"p.345 marker {marker} did not link to {statement_id}")

for row in new_statements:
    if row["original_quote"] not in notes_text:
        raise SystemExit(f"statement quote is outside the consolidated notes segment: {row['statement_id']}")
for row in new_mentions:
    source = notes_text if row["segment_id"] == NOTES else body_text
    if source[int(row["start_char"]):int(row["end_char"])] != row["surface_form"]:
        raise SystemExit(f"final mention span failed: {row['mention_id']}")

coverage[NOTES]["source_line_ranges"] = "L180-251"
coverage[NOTES]["migration_status"] = "complete"
coverage[NOTES]["note"] = (
    "Consolidated notes L180-251 (pp.332-345) are migrated and printed notes 1-3 on p.345 are linked to their marked claims. "
    "Mirrored OCR at L247-248 duplicates the Plate 57 and Plate 58 captions already recorded in derived visual transcription segments l1-3 and l5-7; no duplicate statements were added. "
    "P.344 note 5 continuation at L122 and p.342 note 6 cross-page letter locator remain source-local and linked."
)
coverage[BODY]["source_line_ranges"] = "L161-171"
coverage[BODY]["migration_status"] = "complete"
coverage[BODY]["note"] = (
    "Printed p.345 body and notes 1-3 were checked against CHP-13.pdf physical page 18 and linked to their marked claims. "
    "The p.344 Zanetti quotation closes at L162; the Toni dealer/agent sentence closes at p.346 L174-175, both cross-linked. "
    "Note 3's continuation at L171 is linked to the Moschini/Novelli manuscript citation. S2-only OCR corrections: L164 Varíe→Varie and Use→life; L166 112?→112; canonical OCR unchanged."
)

candidate_out = candidates + new_candidates
mention_out = mentions + new_mentions
statement_out = [statement_by_id.get(row["statement_id"], row) for row in statements] + new_statements
if len({row["candidate_id"] for row in candidate_out}) != len(candidate_out):
    raise SystemExit("candidate IDs are not unique after migration")
if len({row["mention_id"] for row in mention_out}) != len(mention_out):
    raise SystemExit("mention IDs are not unique after migration")
if len({row["statement_id"] for row in statement_out}) != len(statement_out):
    raise SystemExit("statement IDs are not unique after migration")
candidate_ids_out = {row["candidate_id"] for row in candidate_out}
statement_ids_out = {row["statement_id"] for row in statement_out}
for row in new_statements:
    for field in ("subject_candidate_id", "object_candidate_id"):
        if row.get(field) and row[field] not in candidate_ids_out:
            raise SystemExit(f"statement candidate FK missing: {row['statement_id']} -> {row[field]}")
    for linked_id in row.get("qualifiers", {}).get("linked_body_statement_ids", []):
        if linked_id not in statement_ids_out:
            raise SystemExit(f"linked body statement missing: {row['statement_id']} -> {linked_id}")
for row in new_mentions:
    if row["candidate_id"] not in candidate_ids_out:
        raise SystemExit(f"mention candidate FK missing: {row['mention_id']}")

print(f"candidate rows: {len(candidates)} -> {len(candidate_out)} (+{len(new_candidates)})")
print(f"mention rows: {len(mentions)} -> {len(mention_out)} (+{len(new_mentions)})")
print(f"statement rows: {len(statements)} -> {len(statement_out)} (+{len(new_statements)})")
print("coverage: mirrored Plate 57/58 OCR reconciled without duplicate facts; p.345 notes 1-3 linked; p.345 body and notes complete")
print("print correction recorded only in S2: Raccolta Ji -> Raccolta di; the 1763/4 date and edition alignment remain unresolved")
if not args.apply:
    print("dry-run only; no tables written")
    raise SystemExit(0)

targets = [candidate_path, mention_path, statement_path, coverage_path]
backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in targets]
if any(path.exists() for path in backups):
    raise SystemExit("one or more migration backup paths already exist")
for path, backup in zip(targets, backups):
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidate_out)
write_csv(mention_path, mention_fields, mention_out)
write_jsonl(statement_path, statement_out)
write_csv(coverage_path, coverage_fields, coverage_rows)
print("applied with four table backups:")
for path in backups:
    print(f"  {path.relative_to(ROOT)}")
