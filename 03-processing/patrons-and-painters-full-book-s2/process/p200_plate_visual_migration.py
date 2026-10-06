"""Controlled S2 migration for the p.200 plate-page OCR fragments.

Default invocation is a read-only dry run.  The canonical OCR and PDF are
never rewritten; visually restored text lives in the registered derived
transcription asset.
"""
import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MAIN_SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_v.md"
VISUAL_SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_v_visual-transcription.md"
SEGMENTS_PATH = TABLES / "segments.jsonl"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"

SEGMENT_IDS = {
    "header_residual": "chp-7:07_CHP-7_sec_v:l20-21",
    "plate31_residual": "chp-7:07_CHP-7_sec_v:l23-37",
    "plate32a_ocr": "chp-7:07_CHP-7_sec_v:l39-40",
    "plate30_heading_visual": "chp-7:07_CHP-7_sec_v_visual-transcription:l1-1",
    "plate32b_visual": "chp-7:07_CHP-7_sec_v_visual-transcription:l3-3",
}
EXPECTED_CANDIDATES = {
    "cand-2223", "cand-3876", "cand-4089", "cand-4161",
    "cand-2426", "cand-3214", "cand-4071", "cand-4162",
}
BACKUP_SUFFIX = ".bak-s2-chp7-p200-plate-visual-retry-20260930"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_csv_atomic(path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


source_lines = MAIN_SOURCE.read_text(encoding="utf-8-sig").splitlines()
visual_lines = VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
segments = read_jsonl(SEGMENTS_PATH)
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments):
    raise SystemExit("segments.jsonl contains duplicate segment IDs")
for key, segment_id in SEGMENT_IDS.items():
    if segment_id not in segment_by_id:
        raise SystemExit(f"expected rebuilt segment missing: {key} {segment_id}")
for segment_id in SEGMENT_IDS.values():
    row = segment_by_id[segment_id]
    source_path = ROOT / row["source_file"]
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != row["asset_sha256"]:
        raise SystemExit(f"source asset changed after segmentation: {row['source_file']}")

candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
if not EXPECTED_CANDIDATES <= candidate_ids:
    raise SystemExit(f"missing expected existing candidates: {sorted(EXPECTED_CANDIDATES - candidate_ids)}")
mention_fields, mention_rows = read_csv(MENTION_PATH)
statement_rows = read_jsonl(STATEMENT_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

for key in ("header_residual", "plate31_residual", "plate32a_ocr"):
    segment_id = SEGMENT_IDS[key]
    row = coverage_by_id.get(segment_id)
    if row is None or row["disposition"] != "queued" or row["migration_status"] != "pending":
        raise SystemExit(f"expected queued/pending coverage before migration: {segment_id}")
for key in ("plate30_heading_visual", "plate32b_visual"):
    if SEGMENT_IDS[key] in coverage_by_id:
        raise SystemExit(f"visual coverage already exists; inspect before rerunning: {SEGMENT_IDS[key]}")

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_statement_ids = {row["statement_id"] for row in statement_rows}
target_segment_ids = set(SEGMENT_IDS.values())
if any(row["segment_id"] in target_segment_ids for row in mention_rows):
    raise SystemExit("mentions already exist for a target segment; inspect before rerunning")
if any(row["segment_id"] in target_segment_ids for row in statement_rows):
    raise SystemExit("statements already exist for a target segment; inspect before rerunning")


def segment_text(segment_id):
    meta = segment_by_id[segment_id]
    source = source_lines if meta["source_file"].endswith("07_CHP-7_sec_v.md") else visual_lines
    return "\n".join(source[meta["line_start"] - 1:meta["line_end"]])


new_mentions = []


def mention(segment_id, mention_id, candidate_id, surface, note):
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"mention references missing candidate: {mention_id} -> {candidate_id}")
    text = segment_text(segment_id)
    start = text.find(surface)
    if start < 0 or text.find(surface, start + 1) >= 0:
        raise SystemExit(f"surface must occur exactly once in {segment_id}: {surface!r}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })


plate32a_id = SEGMENT_IDS["plate32a_ocr"]
mention(plate32a_id, "m-chp7-p200-plate32a-creator", "cand-3876", "Ribera",
        "Printed Plate 32a attribution; reuses the existing List of Plates candidate.")
mention(plate32a_id, "m-chp7-p200-plate32a-work", "cand-4089", "Drunken Silenus",
        "Printed Plate 32a title; retain this image caption as a source-specific work reference.")
mention(plate32a_id, "m-chp7-p200-plate32a-subject", "cand-4161", "Silenus",
        "Nested figure mention in the work title; the title is not treated as evidence for a historical event.")
mention(plate32a_id, "m-chp7-p200-plate32a-patron", "cand-2223", "Gaspar Roomer",
        "Named as the person for whom the caption says the picture was painted; index identity remains for S3.")

plate32b_id = SEGMENT_IDS["plate32b_visual"]
mention(plate32b_id, "m-chp7-p200-plate32b-creator", "cand-3214", "Paolo de Matteis",
        "Printed Plate 32b attribution; reuses the existing List of Plates candidate.")
mention(plate32b_id, "m-chp7-p200-plate32b-work", "cand-4071", "The Choice of Hercules",
        "Printed Plate 32b title; the body and List of Plates references remain separately anchored.")
mention(plate32b_id, "m-chp7-p200-plate32b-subject", "cand-4162", "Hercules",
        "Nested figure mention in the work title; the title is not treated as evidence for a historical event.")
mention(plate32b_id, "m-chp7-p200-plate32b-patron", "cand-2426", "Lord Shaftesbury",
        "Named in the caption as the patron; the nearby p.198 reference is retained without a new identity decision.")


def make_statement(statement_id, segment_id, line, subject, obj, predicate, claim, qualification,
                   mentioned, quote, plate_label, cross_refs=None):
    q = {
        "source_line_start": line,
        "source_line_end": line,
        "pdf_physical_page": 42 if plate_label.startswith("32") else 40,
        "printed_page_locator": "Plate 32" if plate_label.startswith("32") else "Plate 30",
        "plate_label": plate_label,
        "claim": claim,
        "speaker": "printed plate caption" if plate_label.startswith("32") else "printed plate heading",
        "text_layer": "plate caption" if plate_label.startswith("32") else "editorial plate grouping",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
    }
    if cross_refs:
        q["cross_reference_segments"] = cross_refs
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": q,
        "original_quote": quote,
        "origin": "book",
        "source_file": segment_by_id[segment_id]["source_file"],
    }


quote_a = "a. Ribera: Drunken Silenus painted for Gaspar Roomer"
quote_b = "b. Paolo de Matteis: The Choice of Hercules painted for Lord Shaftesbury"
cross_a = [{"segment_id": "front-matter:00_05_List_of_Plates:l83-118", "source_line_start": 92, "source_line_end": 92}]
cross_b = [
    {"segment_id": "front-matter:00_05_List_of_Plates:l83-118", "source_line_start": 93, "source_line_end": 93},
    {"segment_id": "chp-7:07_CHP-7_sec_iv:l77-87", "source_line_start": 84, "source_line_end": 85},
]
new_statements = [
    make_statement("st-chp7-p200-plate32a-ribera-attribution", plate32a_id, 40, "cand-4089", "cand-3876",
                   "caption_attribution", "The Plate 32a caption credits Ribera with the Drunken Silenus.",
                   "Printed caption attribution; no external attribution judgment is added.",
                   ["cand-4089", "cand-3876", "cand-4161", "cand-2223"], quote_a, "32a", cross_a),
    make_statement("st-chp7-p200-plate32a-silenus-title-subject", plate32a_id, 40, "cand-4089", "cand-4161",
                   "caption_iconographic_subject", "The Plate 32a title names Silenus as the work's subject.",
                   "The title is not treated as evidence for a historical event.",
                   ["cand-4089", "cand-3876", "cand-4161", "cand-2223"], quote_a, "32a", cross_a),
    make_statement("st-chp7-p200-plate32a-painted-for-roomer", plate32a_id, 40, "cand-4089", "cand-2223",
                   "caption_painted_for", "The Plate 32a caption says that the Drunken Silenus was painted for Gaspar Roomer.",
                   "This is the caption's wording; it is not promoted here to a formal commission or ownership relation.",
                   ["cand-4089", "cand-3876", "cand-4161", "cand-2223"], quote_a, "32a", cross_a),
    make_statement("st-chp7-p200-plate32b-paolo-attribution", plate32b_id, 3, "cand-4071", "cand-3214",
                   "caption_attribution", "The Plate 32b caption credits Paolo de Matteis with The Choice of Hercules.",
                   "The visual transcription restores the printed caption omitted from the canonical OCR; the two captions refer to the same plate number, but no identity merge is made among work candidates.",
                   ["cand-4071", "cand-3214", "cand-4162", "cand-2426"], quote_b, "32b", cross_b),
    make_statement("st-chp7-p200-plate32b-hercules-title-subject", plate32b_id, 3, "cand-4071", "cand-4162",
                   "caption_iconographic_subject", "The Plate 32b title names Hercules as an iconographic subject.",
                   "The title is not treated as evidence for a historical event; keep this caption candidate linked to the p.198 reference for later alignment.",
                   ["cand-4071", "cand-3214", "cand-4162", "cand-2426"], quote_b, "32b", cross_b),
    make_statement("st-chp7-p200-plate32b-painted-for-shaftesbury", plate32b_id, 3, "cand-4071", "cand-2426",
                   "caption_painted_for", "The Plate 32b caption says that The Choice of Hercules was painted for Lord Shaftesbury.",
                   "This preserves a printed caption claim; S2 does not turn it into a formal relation or independently verify it.",
                   ["cand-4071", "cand-3214", "cand-4162", "cand-2426"], quote_b, "32b", cross_b),
]
if len({row["statement_id"] for row in new_statements}) != len(new_statements):
    raise SystemExit("duplicate statement ID in migration payload")
if any(row["statement_id"] in existing_statement_ids for row in new_statements):
    raise SystemExit("statement ID already exists; inspect before rerunning")

for row in new_statements:
    segment_id = row["segment_id"]
    meta = segment_by_id[segment_id]
    lines = source_lines if meta["source_file"].endswith("07_CHP-7_sec_v.md") else visual_lines
    excerpt = "\n".join(lines[row["qualifiers"]["source_line_start"] - 1:row["qualifiers"]["source_line_end"]])
    if row["original_quote"] not in excerpt:
        raise SystemExit(f"statement quote is not present in its source lines: {row['statement_id']}")
    for candidate_id in row["qualifiers"]["mentioned_candidate_ids"]:
        if candidate_id not in candidate_ids:
            raise SystemExit(f"statement references missing candidate: {row['statement_id']} -> {candidate_id}")
    for ref in row["qualifiers"].get("cross_reference_segments", []):
        if ref["segment_id"] not in segment_by_id:
            raise SystemExit(f"cross-reference segment missing: {row['statement_id']} -> {ref['segment_id']}")


coverage_updates = {
    SEGMENT_IDS["header_residual"]: {
        "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
        "note": "OCR segment contains only the [Page 30] locator and a reversed suffix of the Plate 30 grouping title. The full printed heading is preserved in the derived visual-transcription segment and treated as editorial navigation; no entity, claim, or hierarchy node is derived from it.",
    },
    SEGMENT_IDS["plate31_residual"]: {
        "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
        "note": "Rotated/reversed OCR fragments reproduce the Plate 31 captions already semantically covered in front-matter:00_05_List_of_Plates:l83-118; the scan adds no distinct caption claim. Excluded as duplicate OCR rendering, not as an unreviewed page.",
    },
    SEGMENT_IDS["plate32a_ocr"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L39-40",
        "note": "Printed p.200 Plate 32a caption read against CHP-7.pdf physical p.42; creator, work, title subject, and 'painted for Gaspar Roomer' are migrated. The printed 32b caption is absent from this S0 OCR block and is restored in the registered visual-transcription segment; no source OCR is overwritten.",
    },
    SEGMENT_IDS["plate30_heading_visual"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L1-1",
        "note": "no_semantic_content: CHP-7.pdf physical p.40 Plate 30 grouping title and cross-reference to Plates 30–31 visually transcribed because the OCR retained only a reversed suffix. Editorial navigation; it does not establish a research theme or hierarchy node.",
    },
    SEGMENT_IDS["plate32b_visual"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-3",
        "note": "CHP-7.pdf physical p.42 Plate 32b caption visually transcribed because the canonical OCR omitted it. Reuses existing caption candidates and anchors the 'painted for Lord Shaftesbury' claim; linked to the List of Plates and p.198 body reference without resolving identity or work-version questions.",
    },
}

updated_coverage = []
for segment in segments:
    segment_id = segment["segment_id"]
    if segment_id in coverage_updates:
        updated_coverage.append({
            "chapter": segment["chapter"], "segment_id": segment_id,
            **coverage_updates[segment_id],
        })
    elif segment_id in coverage_by_id:
        updated_coverage.append(dict(coverage_by_id[segment_id]))
    else:
        raise SystemExit(f"no coverage row or planned update for rebuilt segment: {segment_id}")
if set(row["segment_id"] for row in updated_coverage) != set(segment_by_id):
    raise SystemExit("coverage rows do not match rebuilt segments")

preview = {
    "mode": "dry-run",
    "segments": {key: value for key, value in SEGMENT_IDS.items()},
    "excluded_ocr_residuals": [SEGMENT_IDS["header_residual"], SEGMENT_IDS["plate31_residual"]],
    "visual_transcription_segments": [SEGMENT_IDS["plate30_heading_visual"], SEGMENT_IDS["plate32b_visual"]],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "updated_coverage_rows": len(coverage_updates),
    "statement_ids": [row["statement_id"] for row in new_statements],
    "mention_preview": [
        {"mention_id": row["mention_id"], "surface": row["surface_form"],
         "candidate_id": row["candidate_id"], "span": [row["start_char"], row["end_char"]]}
        for row in new_mentions
    ],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if not parser.parse_args().apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (SEGMENTS_PATH, MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists; refusing overwrite: {backup}")
    shutil.copy2(path, backup)

mention_rows.extend(new_mentions)
write_csv_atomic(MENTION_PATH, mention_fields, mention_rows)
statement_rows.extend(new_statements)
with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=STATEMENT_PATH.parent,
                                 delete=False, suffix=".tmp") as stream:
    for row in statement_rows:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary = Path(stream.name)
temporary.replace(STATEMENT_PATH)
write_csv_atomic(COVERAGE_PATH, coverage_fields, updated_coverage)

preview["mode"] = "applied"
print(json.dumps(preview, ensure_ascii=False, indent=2))
