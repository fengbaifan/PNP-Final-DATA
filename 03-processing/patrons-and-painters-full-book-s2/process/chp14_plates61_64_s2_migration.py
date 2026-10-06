"""Controlled S2 migration for Chapter 14 image pages, plates 61–64."""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "14_CHP-14_intro.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-14.pdf"
PLATES_61 = "chp-14:14_CHP-14_intro:l148-149"
PLATES_62_63 = "chp-14:14_CHP-14_intro:l151-153"
PLATE_64 = "chp-14:14_CHP-14_intro:l155-166"
SOURCE_FILE = "02-sources/02-Markdown/14_CHP-14_intro.md"
SOURCE_SHA = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
PDF_SHA = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
BACKUP_SUFFIX = ".bak-s2-chp14-plates61-64-20261004"

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply reviewed S2 image-caption migration")
args = parser.parse_args()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_csv(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise SystemExit("canonical chapter 14 Markdown source changed")
if hashlib.sha256(PDF.read_bytes()).hexdigest() != PDF_SHA:
    raise SystemExit("registered CHP-14 PDF asset changed")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
for line_number, required in [
    (149, "a. Early version"),
    (152, "Canaletto: The Prato della Valle in Padua"),
    (153, "Domenico Cerato: Project for the r"),
    (155, "[Page 64]"),
    (156, "osiverT"),
    (166, "ocsecnarF"),
]:
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
statement_by_id = {row["statement_id"]: row for row in statements}
coverage_by_id = {row["segment_id"]: row for row in coverage}

for segment_id in (PLATES_61, PLATES_62_63, PLATE_64):
    if segment_id not in coverage_by_id:
        raise SystemExit(f"missing S2 coverage row: {segment_id}")
    if coverage_by_id[segment_id]["migration_status"] != "pending":
        raise SystemExit(f"visual segment is no longer pending: {segment_id}")
if max(int(cid.split("-")[1]) for cid in candidate_by_id) != 10422:
    raise SystemExit("candidate sequence changed; expected max cand-10422")
required_refs = [
    "st-fm-pl-p61a-creator", "st-fm-pl-p61b-creator",
    "st-fm-pl-p62-creator", "st-fm-pl-p62-padua", "st-fm-pl-p62-site",
    "st-fm-pl-p63-creator", "st-fm-pl-p63-site",
    "st-fm-pl-p64-creator", "st-fm-pl-p64-paese", "st-fm-pl-p64-strange", "st-fm-pl-p64-treviso",
]
missing_refs = [sid for sid in required_refs if sid not in statement_by_id]
if missing_refs:
    raise SystemExit(f"missing existing plate-list statements: {missing_refs}")

segment_bounds = {PLATES_61: (148, 149), PLATES_62_63: (151, 153), PLATE_64: (155, 166)}
segment_texts = {sid: "\n".join(source_lines[first - 1:last]) for sid, (first, last) in segment_bounds.items()}
planned_mentions = []
mention_counter = 1


def add_mention(segment_id, candidate_id, surface, note=""):
    global mention_counter
    if candidate_id not in candidate_by_id:
        raise SystemExit(f"mention candidate missing: {candidate_id}")
    text = segment_texts[segment_id]
    occupied = [(int(r["start_char"]), int(r["end_char"])) for r in mentions + planned_mentions if r["segment_id"] == segment_id]
    start = 0
    while True:
        pos = text.find(surface, start)
        if pos < 0:
            original = text.find(surface)
            collisions = [r for r in mentions + planned_mentions if r["segment_id"] == segment_id
                          and int(r["start_char"]) < original + len(surface)
                          and original < int(r["end_char"])]
            raise SystemExit(f"surface not found in {segment_id}: {surface!r}; overlaps={collisions}")
        end = pos + len(surface)
        if not any(pos < old_end and old_start < end for old_start, old_end in occupied):
            break
        start = pos + 1
    mention_id = f"m-chp14-plates61-64-{mention_counter:04d}"
    if any(row["mention_id"] == mention_id for row in mentions):
        raise SystemExit(f"mention ID already exists: {mention_id}")
    planned_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id,
        "candidate_id": candidate_id, "surface_form": surface,
        "start_char": str(pos), "end_char": str(end), "note": note,
    })
    mention_counter += 1


add_mention(PLATES_61, "cand-4100", "a. Early version",
            "Plate 61a, mapped through the existing list-of-plates caption; the physical page also has a separately read final-version label.")
add_mention(PLATES_62_63, "cand-3738", "Canaletto")
add_mention(PLATES_62_63, "cand-4014", "The Prato della Valle in Padua",
            "S0 OCR uses ‘Prato’; print image reads ‘Prà’. Preserve both source forms and cross-reference the plate-list entry.")
add_mention(PLATES_62_63, "cand-3753", "Domenico Cerato")
add_mention(PLATES_62_63, "cand-4031", "Project for the r",
            "Visible OCR fragment for Plate 63; complete caption is separately recorded in the front-matter plate list.")
add_mention(PLATE_64, "cand-3768", ":idrauG", "OCR reverses the printed caption; page image reads Guardi:")
add_mention(PLATE_64, "cand-4036", "weiV", "OCR reverses the printed caption; page image reads View.")
add_mention(PLATE_64, "cand-3817", "nhoJfo", "OCR reverses the printed caption; token is part of ‘of John Strange’s’.")
add_mention(PLATE_64, "cand-3817", "egnartS", "OCR reverses the printed caption; token is part of ‘John Strange’s’.")
add_mention(PLATE_64, "cand-3945", "eseaP", "OCR reverses the printed caption; page image reads Paese.")
add_mention(PLATE_64, "cand-3981", "osiverT", "OCR reverses the printed caption; page image reads Treviso.")


def quote(segment_id, line_start, line_end):
    return "\n".join(source_lines[line_start - 1:line_end])


def add_statement(statement_id, segment_id, subject, obj, predicate, line_start, line_end,
                  claim, text_layer, speaker, qualification, mentioned=(),
                  original_quote_override=None, **extra):
    if statement_id in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement_id}")
    qualifiers = {
        "source_line_start": line_start, "source_line_end": line_end,
        "claim": claim, "speaker": speaker, "text_layer": text_layer,
        "qualification": qualification,
        "mentioned_candidate_ids": list(dict.fromkeys(mentioned)),
    }
    qualifiers.update(extra)
    row = {
        "statement_id": statement_id, "segment_id": segment_id,
        "subject_candidate_id": subject, "object_candidate_id": obj,
        "predicate": predicate, "qualifiers": qualifiers,
        "original_quote": original_quote_override if original_quote_override is not None else quote(segment_id, line_start, line_end),
        "origin": "book", "source_file": SOURCE_FILE,
    }
    statements.append(row)
    statement_by_id[statement_id] = row


add_statement(
    "st-chp14-p361-plate61-version-sequence", PLATES_61, "cand-4100", "cand-4101",
    "plate_page_distinguishes_early_and_final_versions", 149, 149,
    "The Plate 61 image page distinguishes an early and a final version of Tiepolo’s Banquet of Antony and Cleopatra; its page heading frames the changes as made under Algarotti’s impact.",
    "plate-page heading and subcaptions", "printed image page",
    "The OCR segment preserves ‘a. Early version’ but omits the visible ‘b. Final version’ label and the main page heading. Those two print readings were taken directly from CHP-14.pdf physical p.15; Plate 61a/61b object identities link to the separate front-matter captions.",
    mentioned=["cand-4100", "cand-4101", "cand-3781", "cand-0050"],
    original_quote_override="a. Early version",
    visual_page_physical_page=15,
    visual_page_heading="Tiepolo’s Changes to the Banquet of Antony and Cleopatra under the Impact of Algarotti",
    visual_page_subcaptions=["a. Early version", "b. Final version"],
    s0_ocr_omissions=["main page heading", "b. Final version"],
    cross_reference_statement_ids=["st-fm-pl-p61a-creator", "st-fm-pl-p61b-creator"])

add_statement(
    "st-chp14-p362-plate62-canaletto-caption", PLATES_62_63, "cand-4014", "cand-3738",
    "image_caption_attributes_pradella_valle_view_to_canaletto", 152, 152,
    "The Plate 62 image caption identifies the view as Canaletto’s and names its subject setting as Prà della Valle in Padua.",
    "plate image caption", "printed image caption",
    "This image caption repeats the existing front-matter plate-list attribution and setting; it does not independently verify the work’s current title, date, or location.",
    mentioned=["cand-4014", "cand-3738", "cand-1804", "cand-3960"],
    visual_page_physical_page=16,
    ocr_corrections=[{"source_line": 152, "ocr": "Prato", "print": "Prà"}],
    cross_reference_statement_ids=["st-fm-pl-p62-creator", "st-fm-pl-p62-padua", "st-fm-pl-p62-site"])

add_statement(
    "st-chp14-p363-plate63-cerato-caption-fragment", PLATES_62_63, "cand-4031", "cand-3753",
    "image_caption_fragment_attributes_pradella_valle_proposal_to_cerato", 153, 153,
    "The Plate 63 image page carries the visible caption fragment ‘Domenico Cerato: Project for the r…’; the separate list-of-plates caption identifies the work as Cerato’s original proposals for reclaiming Prà della Valle.",
    "plate image caption fragment", "printed image caption and cross-referenced plate list",
    "The scan/OCR fragment is left incomplete; the full title comes from the separate list-of-plates source, not from a silent reconstruction of this caption.",
    mentioned=["cand-4031", "cand-3753", "cand-3960"],
    visual_pages_physical=[16, 17],
    cross_reference_statement_ids=["st-fm-pl-p63-creator", "st-fm-pl-p63-site"])

add_statement(
    "st-chp14-p364-plate64-guardi-caption", PLATE_64, "cand-4036", "cand-3768",
    "image_caption_attributes_view_of_strange_villa_to_guardi", 156, 166,
    "The Plate 64 caption credits Francesco Guardi with a view of John Strange’s villa at Paese near Treviso.",
    "plate image caption", "printed image caption",
    "The extracted OCR reverses the caption’s word order because the caption is rotated on the page. The complete reading was checked against CHP-14.pdf physical p.18; ownership remains as separately qualified by the front-matter caption.",
    mentioned=["cand-4036", "cand-3768", "cand-3817", "cand-3945", "cand-3981"],
    visual_page_physical_page=18,
    visual_print_reading="Francesco Guardi: View of John Strange’s villa at Paese near Treviso",
    ocr_corrections=[{"source_lines": "L156-L166", "ocr": "osiverT / raen / eseaP / ta / alliv / s’ / egnartS / nhoJfo / weiV / :idrauG / ocsecnarF", "print": "Francesco Guardi: View of John Strange’s villa at Paese near Treviso"}],
    cross_reference_statement_ids=["st-fm-pl-p64-creator", "st-fm-pl-p64-paese", "st-fm-pl-p64-strange", "st-fm-pl-p64-treviso", "st-fm-pl-p64-private-collection"])

expected_statement_ids = {
    "st-chp14-p361-plate61-version-sequence",
    "st-chp14-p362-plate62-canaletto-caption",
    "st-chp14-p363-plate63-cerato-caption-fragment",
    "st-chp14-p364-plate64-guardi-caption",
}
actual_statement_ids = {sid for sid in expected_statement_ids if sid in statement_by_id}
if actual_statement_ids != expected_statement_ids:
    raise SystemExit("expected Chapter 14 plate statements were not created")

coverage_by_id[PLATES_61].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L148-149",
    "note": "Checked CHP-14.pdf physical p.15 (Plate 61). Linked the visible ‘a. Early version’ subcaption to the existing Plate 61a object and recorded the page heading plus ‘b. Final version’ from the scan because OCR omitted them; did not change S0. Existing front-matter Plate 61a/61b captions retain the work identities.",
})
coverage_by_id[PLATES_62_63].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L151-153",
    "note": "Checked CHP-14.pdf physical pp.16–17 (Plates 62–63). Plate 62’s Canaletto caption matches the existing plate-list work/site attribution. The Cerato caption is clipped in this image/OCR segment; its visible fragment is preserved and cross-referenced to the separate full Plate 63 entry in the plate list. No title completion was inserted into S0.",
})
coverage_by_id[PLATE_64].update({
    "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L155-166",
    "note": "Checked CHP-14.pdf physical p.18 (Plate 64). OCR word order is reversed because the caption is rotated; corrected reading is Francesco Guardi: View of John Strange’s villa at Paese near Treviso. Linked to existing front-matter caption statements; S0 unchanged.",
})

result = {
    "mode": "apply" if args.apply else "dry-run",
    "source_sha256": SOURCE_SHA,
    "pdf_sha256": PDF_SHA,
    "new_candidates": 0,
    "new_mentions": len(planned_mentions),
    "new_statements": len(expected_statement_ids),
    "coverage_updates": {sid: coverage_by_id[sid] for sid in (PLATES_61, PLATES_62_63, PLATE_64)},
}

if args.apply:
    touched = [mention_path, statement_path, coverage_path]
    backups = []
    for path in touched:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup.name}")
        backups.append((path, backup))
    for path, backup in backups:
        shutil.copy2(path, backup)
    write_csv(mention_path, mention_fields, mentions + planned_mentions)
    write_jsonl(statement_path, statements)
    write_csv(coverage_path, coverage_fields, coverage)
print(json.dumps(result, ensure_ascii=False, indent=2))
