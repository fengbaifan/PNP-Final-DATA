"""Controlled S2 migration for chapter 13 Plates 58-60; dry-run by default."""
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
VISUAL = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro_plates_visual-transcription.md"
PDF = ROOT / "02-sources" / "01-book" / "CHP-13.pdf"
VISUAL_SHA = "73d5fad85a4b84f11508ef0cad9590bded516b69ed2ce203dc3afaf3079906bd"
PDF_SHA = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
BACKUP_SUFFIX = ".bak-s2-chp13-p344-plates58-60-final-20261003"
SEGMENTS = {
    "plate58": ("chp-13:13_CHP-13_intro_plates_visual-transcription:l5-7", 5, 7, 15, "chp-13:13_CHP-13_intro:l141-143"),
    "plate59": ("chp-13:13_CHP-13_intro_plates_visual-transcription:l9-11", 9, 11, 16, "chp-13:13_CHP-13_intro:l145-156"),
    "plate60": ("chp-13:13_CHP-13_intro_plates_visual-transcription:l13-14", 13, 14, 17, "chp-13:13_CHP-13_intro:l158-159"),
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="apply the reviewed Plates 58-60 migration")
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
        temp = Path(handle.name)
    temp.replace(path)


def write_jsonl(path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp = Path(handle.name)
    temp.replace(path)


def check_sha(path, expected, label):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"{label} SHA changed: {actual}")


check_sha(VISUAL, VISUAL_SHA, "chapter 13 visual transcription")
check_sha(PDF, PDF_SHA, "registered CHP-13 PDF")
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
visual_lines = VISUAL.read_text(encoding="utf-8-sig").splitlines()
for i, expected in {141: "[Page 58]", 145: "[Page 59]", 158: "[Page 60]"}.items():
    if source_lines[i - 1] != expected:
        raise SystemExit(f"expected original plate marker changed at source L{i}")
if not visual_lines[4].startswith("Plate 58") or not visual_lines[8].startswith("Plate 59") or not visual_lines[12].startswith("Plate 60"):
    raise SystemExit("visual plate headings changed")

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
segment_path = TABLES / "segments.jsonl"
candidate_fields, candidates = read_csv(candidate_path)
mention_fields, mentions = read_csv(mention_path)
statements = read_jsonl(statement_path)
coverage_fields, coverage = read_csv(coverage_path)
segments = read_jsonl(segment_path)
state = (len(candidates), len(mentions), len(statements), len(coverage))
if state != (10101, 21806, 9732, 827):
    raise SystemExit(f"unexpected pre-state: candidates/mentions/statements/coverage={state}")
segment_by_id = {row["segment_id"]: row for row in segments}
coverage_by_id = {row["segment_id"]: row for row in coverage}
for name, (sid, line_start, line_end, _, original_sid) in SEGMENTS.items():
    if sid not in segment_by_id or sid in coverage_by_id:
        raise SystemExit(f"missing source segment or pre-existing coverage for {name}")
    if original_sid not in coverage_by_id or coverage_by_id[original_sid]["disposition"] != "queued":
        raise SystemExit(f"original OCR segment is not queued for {name}")
    row = segment_by_id[sid]
    exact = "\n".join(visual_lines[line_start - 1:line_end])
    if hashlib.sha256(exact.encode("utf-8")).hexdigest() != row["sha256"]:
        raise SystemExit(f"visual transcription segment hash mismatch for {name}")

candidate_by_id = {row["candidate_id"]: row for row in candidates}
required = {
    "cand-0041", "cand-2838", "cand-3397", "cand-3713", "cand-3716", "cand-3733", "cand-3739",
    "cand-3776", "cand-3777", "cand-3798", "cand-3827", "cand-3887", "cand-3956", "cand-3999",
    "cand-4007", "cand-4016", "cand-4042", "cand-4048",
}
if not required.issubset(candidate_by_id):
    raise SystemExit(f"required existing candidates missing: {sorted(required - candidate_by_id.keys())}")
placeholder = candidate_by_id.get("cand-10059")
if not placeholder or placeholder["status"] != "open":
    raise SystemExit("expected Plate 58a placeholder candidate cand-10059 changed")
mention_ids = {row["mention_id"] for row in mentions}
statement_by_id = {row["statement_id"]: row for row in statements}

# Define each mention by an exact substring in its visual transcription segment.
mention_specs = [
    ("m-s2-ch13-p344-plates58-60-001", "plate58", "cand-4048", "A. M. Zanetti the Elder with Marchese Gerini of Florence", "Caption wording identifying the existing Zocchi portrait work."),
    ("m-s2-ch13-p344-plates58-60-002", "plate58", "cand-3798", "ZOCCHI", "Printed artist attribution; no external attribution verification is implied."),
    ("m-s2-ch13-p344-plates58-60-003", "plate58", "cand-2838", "A. M. Zanetti the Elder", "Named sitter in the printed caption."),
    ("m-s2-ch13-p344-plates58-60-004", "plate58", "cand-3827", "Marchese Gerini", "Named sitter as captioned; no further biographical detail is added."),
    ("m-s2-ch13-p344-plates58-60-005", "plate58", "cand-3397", "Florence", "The caption's wording 'of Florence'; this does not establish present location."),
    ("m-s2-ch13-p344-plates58-60-006", "plate58", "cand-3999", "b. A. LONGHI: G. M. Sasso", "The complete caption identifies the existing portrait work; the sitter is also recorded with a nested mention."),
    ("m-s2-ch13-p344-plates58-60-007", "plate58", "cand-3713", "A. LONGHI", "Printed artist attribution; mapped to the existing Alessandro Longhi candidate pending S3."),
    ("m-s2-ch13-p344-plates58-60-008", "plate58", "cand-3776", "G. M. Sasso", "Named sitter in the printed caption."),
    ("m-s2-ch13-p344-plates58-60-009", "plate59", "cand-4016", "a. CANOVA: Amadeo Swajer", "The complete caption identifies the existing portrait work; the sitter is also recorded with a nested mention."),
    ("m-s2-ch13-p344-plates58-60-010", "plate59", "cand-3739", "CANOVA", "Printed artist attribution; no external attribution verification is implied."),
    ("m-s2-ch13-p344-plates58-60-011", "plate59", "cand-3716", "Amadeo Swajer", "Named sitter in the printed caption."),
    ("m-s2-ch13-p344-plates58-60-012", "plate59", "cand-4007", "b. BERNARDINO CASTELLI: Teodoro Correr", "The complete caption identifies the existing portrait work; the sitter is also recorded with a nested mention."),
    ("m-s2-ch13-p344-plates58-60-013", "plate59", "cand-3733", "BERNARDINO CASTELLI", "Printed artist attribution; no external attribution verification is implied."),
    ("m-s2-ch13-p344-plates58-60-014", "plate59", "cand-3887", "Teodoro Correr", "Named sitter in the printed caption."),
    ("m-s2-ch13-p344-plates58-60-015", "plate60", "cand-4042", "Mourners at tomb of Francesco Algarotti in Pisa", "Caption wording identifying the existing Volpato work."),
    ("m-s2-ch13-p344-plates58-60-016", "plate60", "cand-3777", "VOLPATO", "Printed artist attribution; mapped to the existing Giovanni Volpato candidate pending S3."),
    ("m-s2-ch13-p344-plates58-60-017", "plate60", "cand-0041", "Francesco Algarotti", "The caption names the deceased whose tomb is represented."),
    ("m-s2-ch13-p344-plates58-60-018", "plate60", "cand-3956", "Pisa", "Location named in the printed caption; no current holding is inferred."),
]

new_mentions = []
for mid, plate, cid, surface, note in mention_specs:
    if mid in mention_ids:
        raise SystemExit(f"mention ID already exists: {mid}")
    sid, start_line, end_line, _, _ = SEGMENTS[plate]
    segment_text = "\n".join(visual_lines[start_line - 1:end_line])
    start = segment_text.find(surface)
    if start < 0 or segment_text.find(surface, start + 1) >= 0:
        raise SystemExit(f"mention anchor is absent or ambiguous: {mid}")
    new_mentions.append({
        "mention_id": mid,
        "segment_id": sid,
        "candidate_id": cid,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })

new_statements = []
def add_statement(statement_id, plate, subject, object_id, predicate, caption_line, physical_page, claim, qualification, ids):
    sid, start_line, end_line, _, _ = SEGMENTS[plate]
    quote = visual_lines[caption_line - 1]
    if not quote.startswith(("a. ", "b. ", "G. ")):
        raise SystemExit(f"caption line anchor changed: {statement_id}")
    new_statements.append({
        "statement_id": statement_id,
        "segment_id": sid,
        "subject_candidate_id": subject,
        "object_candidate_id": object_id,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": caption_line,
            "source_line_end": caption_line,
            "pdf_physical_page": physical_page,
            "plate_ref": (f"{plate[-2:]}{'a' if caption_line == start_line + 1 else 'b'}" if plate != "plate60" else "60"),
            "claim": claim,
            "speaker": "printed plate caption",
            "text_layer": "plate caption",
            "qualification": qualification,
            "mentioned_candidate_ids": ids,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro_plates_visual-transcription.md",
    })

add_statement("st-chp13-plates58a-zocchi-attribution", "plate58", "cand-4048", "cand-3798", "caption_attribution", 6, 15, "The printed caption attributes the Zanetti and Gerini portrait to Zocchi.", "Caption attribution only; no external attribution verification is implied.", ["cand-4048", "cand-3798", "cand-2838", "cand-3827"])
add_statement("st-chp13-plates58a-depicts-zanetti", "plate58", "cand-4048", "cand-2838", "caption_depicts_person", 6, 15, "The caption identifies A. M. Zanetti the Elder as one of the depicted sitters.", "This records the caption's identification; it does not independently verify the portrait's sitter.", ["cand-4048", "cand-2838"])
add_statement("st-chp13-plates58a-depicts-gerini", "plate58", "cand-4048", "cand-3827", "caption_depicts_person", 6, 15, "The caption identifies Marchese Gerini of Florence as the other depicted sitter.", "The caption gives a title and place association only; no further identity or current-location claim is inferred.", ["cand-4048", "cand-3827", "cand-3397"])
add_statement("st-chp13-plates58b-longhi-attribution", "plate58", "cand-3999", "cand-3713", "caption_attribution", 7, 15, "The caption attributes the G. M. Sasso portrait to A. Longhi.", "The caption gives only an initial and surname; mapped to the existing Alessandro Longhi candidate pending S3.", ["cand-3999", "cand-3713", "cand-3776"])
add_statement("st-chp13-plates58b-depicts-sasso", "plate58", "cand-3999", "cand-3776", "caption_depicts_person", 7, 15, "The caption identifies G. M. Sasso as the sitter.", "The caption gives initials and surname only; the existing Sasso candidate is reused pending S3.", ["cand-3999", "cand-3776"])
add_statement("st-chp13-plates59a-canova-attribution", "plate59", "cand-4016", "cand-3739", "caption_attribution", 10, 16, "The caption attributes the Amadeo Swajer portrait to Canova.", "Printed surname attribution only; no external attribution verification is implied.", ["cand-4016", "cand-3739", "cand-3716"])
add_statement("st-chp13-plates59a-depicts-swajer", "plate59", "cand-4016", "cand-3716", "caption_depicts_person", 10, 16, "The caption identifies Amadeo Swajer as the sitter.", "This records the caption's identification; it does not independently verify the sitter.", ["cand-4016", "cand-3716"])
add_statement("st-chp13-plates59b-castelli-attribution", "plate59", "cand-4007", "cand-3733", "caption_attribution", 11, 16, "The caption attributes the Teodoro Correr portrait to Bernardino Castelli.", "Caption attribution only; no external attribution verification is implied.", ["cand-4007", "cand-3733", "cand-3887"])
add_statement("st-chp13-plates59b-depicts-correr", "plate59", "cand-4007", "cand-3887", "caption_depicts_person", 11, 16, "The caption identifies Teodoro Correr as the sitter.", "This records the caption's identification; it does not independently verify the sitter.", ["cand-4007", "cand-3887"])
add_statement("st-chp13-plate60-volpato-attribution", "plate60", "cand-4042", "cand-3777", "caption_attribution", 14, 17, "The caption attributes the mourners-at-the-tomb image to G. Volpato.", "The caption supplies an initial and surname; the existing Giovanni Volpato candidate is reused pending S3.", ["cand-4042", "cand-3777", "cand-0041", "cand-3956"])
add_statement("st-chp13-plate60-tomb-of-algarotti", "plate60", "cand-4042", "cand-0041", "caption_depicts_tomb_of", 14, 17, "The caption identifies the tomb as that of Francesco Algarotti.", "This is the caption's description of the represented scene, not independent confirmation of the monument.", ["cand-4042", "cand-0041"])
add_statement("st-chp13-plate60-location-pisa", "plate60", "cand-4042", "cand-3956", "caption_locates_tomb_at", 14, 17, "The caption locates the tomb in Pisa.", "Caption location only; no present-day site identification or holding is inferred.", ["cand-4042", "cand-3956"])
for statement in new_statements:
    if statement["statement_id"] in statement_by_id:
        raise SystemExit(f"statement ID already exists: {statement['statement_id']}")

# Resolve the p.341 Plate 58a placeholder to the already registered Zocchi portrait.
placeholder_mention = next((m for m in mentions if m["mention_id"] == "m-s2-ch13-p341-007"), None)
if not placeholder_mention or placeholder_mention["candidate_id"] != "cand-10059":
    raise SystemExit("p.341 Plate 58a placeholder mention changed")
p341_statement = statement_by_id.get("st-chp13-p341-zanetti_portrait_reference_and_authorial_interest")
if not p341_statement or p341_statement["object_candidate_id"] != "cand-10059":
    raise SystemExit("p.341 Plate 58a placeholder statement changed")

for original_id, visual_key, source_range, note in [
    (SEGMENTS["plate58"][4], "plate58", "L141-143", "no_semantic_content: reversed OCR fragments do not preserve the Plate 58 captions legibly. Both captions were checked against CHP-13.pdf physical page 15 and represented in the derived visual transcription; canonical OCR and PDF remain unchanged."),
    (SEGMENTS["plate59"][4], "plate59", "L145-156", "no_semantic_content: reversed OCR fragments do not preserve the Plate 59 captions legibly. Both captions were checked against CHP-13.pdf physical page 16 and represented in the derived visual transcription; canonical OCR and PDF remain unchanged."),
    (SEGMENTS["plate60"][4], "plate60", "L158-159", "no_semantic_content: the original OCR caption is represented in the derived visual transcription, which preserves its Plate 60 heading and printed caption structure. The OCR and PDF remain unchanged."),
]:
    row = coverage_by_id[original_id]
    row.update({"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": source_range, "note": note})

new_coverage = []
for plate, (sid, start_line, end_line, physical_page, original_sid) in SEGMENTS.items():
    new_coverage.append({
        "chapter": "chp-13",
        "segment_id": sid,
        "disposition": "reviewed",
        "migration_status": "complete",
        "source_line_ranges": f"L{start_line}-{end_line}",
        "note": f"Plate {plate[-2:]} caption(s) were transcribed from CHP-13.pdf physical page {physical_page}; existing candidate work/person mappings are preserved as caption claims and do not constitute external verification.",
    })

# Apply the explicit p.341 cross-reference correction in-place.
placeholder["status"] = "excluded"
placeholder["exclude_reason"] = "Plate 58a was a provisional image placeholder; the inspected caption identifies the existing Zocchi portrait candidate cand-4048, so this duplicate placeholder is excluded."
placeholder["detail"] = "Provisional Plate 58a placeholder. Caption review resolved the referenced object to existing work candidate cand-4048."
placeholder_mention["candidate_id"] = "cand-4048"
placeholder_mention["note"] = "Cross-reference resolved to the existing Zocchi portrait work cand-4048 after the Plate 58a caption was visually checked."
p341_statement["object_candidate_id"] = "cand-4048"
p341_statement["qualifiers"]["mentioned_candidate_ids"] = ["cand-2838", "cand-4048"]
p341_statement["qualifiers"]["qualification"] = "The superlative is Haskell's evaluation. Plate 58a is the existing Zocchi portrait work; its caption identifies Zanetti and Marchese Gerini as sitters."

new_coverage_rows = coverage + new_coverage
new_mention_rows = mentions + new_mentions
new_statement_rows = statements + new_statements
print(f"existing works reused; placeholder cand-10059 excluded and redirected to cand-4048")
print(f"mentions +{len(new_mentions)}; statements +{len(new_statements)}; coverage {state[3]} -> {len(new_coverage_rows)}")
if not args.apply:
    print("dry-run only; pass --apply to write")
    raise SystemExit(0)
for path in (candidate_path, mention_path, statement_path, coverage_path):
    backup = Path(str(path) + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(path, backup)
write_csv(candidate_path, candidate_fields, candidates)
write_csv(mention_path, mention_fields, new_mention_rows)
write_jsonl(statement_path, new_statement_rows)
write_csv(coverage_path, coverage_fields, new_coverage_rows)
print("applied; recovery backups saved for candidate, mention, statement, and coverage tables")
