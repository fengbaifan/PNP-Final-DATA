"""Controlled S2 migration for the Plate 33–36 image captions in Chapter 8.

Default invocation is a read-only dry run. Canonical OCR and the source PDF
remain unchanged; missing/rotated caption text is kept in a registered derived
visual-transcription asset.
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
MAIN_SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii.md"
VISUAL_SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii_plates_visual-transcription.md"
SEGMENTS_PATH = TABLES / "segments.jsonl"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
BACKUP_SUFFIX = ".bak-s2-chp8-plates33-36-20261001"

MAIN_IDS = {
    "plate33": "chp-8:08_CHP-8_sec_ii:l37-39",
    "plate34": "chp-8:08_CHP-8_sec_ii:l41-43",
    "plate35a": "chp-8:08_CHP-8_sec_ii:l45-46",
    "plate36_ocr": "chp-8:08_CHP-8_sec_ii:l48-67",
}
VISUAL_IDS = {
    "plate35b": "chp-8:08_CHP-8_sec_ii_plates_visual-transcription:l1-1",
    "plate36_heading": "chp-8:08_CHP-8_sec_ii_plates_visual-transcription:l3-3",
    "plate36a": "chp-8:08_CHP-8_sec_ii_plates_visual-transcription:l5-5",
    "plate36b": "chp-8:08_CHP-8_sec_ii_plates_visual-transcription:l7-7",
}
PLATE_LIST_SEGMENT = "front-matter:00_05_List_of_Plates:l83-118"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv_atomic(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(SEGMENTS_PATH)
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments):
    raise SystemExit("segments.jsonl contains duplicate segment IDs")
expected_ids = set(MAIN_IDS.values()) | set(VISUAL_IDS.values()) | {PLATE_LIST_SEGMENT}
if not expected_ids <= set(segment_by_id):
    raise SystemExit(f"required segments missing: {sorted(expected_ids - set(segment_by_id))}")
for segment_id in expected_ids:
    row = segment_by_id[segment_id]
    source_path = ROOT / row["source_file"]
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != row["asset_sha256"]:
        raise SystemExit(f"source asset changed after segmentation: {row['source_file']}")

main_lines = MAIN_SOURCE.read_text(encoding="utf-8-sig").splitlines()
visual_lines = VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
candidate_fields, candidate_rows = read_csv(CANDIDATE_PATH)
candidate_ids = {row["candidate_id"] for row in candidate_rows}
mention_fields, mention_rows = read_csv(MENTION_PATH)
statement_rows = read_jsonl(STATEMENT_PATH)
coverage_fields, coverage_rows = read_csv(COVERAGE_PATH)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

for segment_id in MAIN_IDS.values():
    row = coverage_by_id.get(segment_id)
    if row is None or row["disposition"] != "queued" or row["migration_status"] != "pending":
        raise SystemExit(f"expected queued/pending coverage: {segment_id}")
for segment_id in VISUAL_IDS.values():
    if segment_id in coverage_by_id:
        raise SystemExit(f"visual coverage already exists; inspect before rerunning: {segment_id}")

target_segment_ids = set(MAIN_IDS.values()) | set(VISUAL_IDS.values())
if any(row["segment_id"] in target_segment_ids for row in mention_rows):
    raise SystemExit("mentions already exist for a target segment; inspect before rerunning")
if any(row["segment_id"] in target_segment_ids for row in statement_rows):
    raise SystemExit("statements already exist for a target segment; inspect before rerunning")

def get_source_lines(segment_id):
    meta = segment_by_id[segment_id]
    if meta["source_file"].endswith("08_CHP-8_sec_ii.md"):
        return main_lines
    if meta["source_file"].endswith("08_CHP-8_sec_ii_plates_visual-transcription.md"):
        return visual_lines
    if meta["source_file"].endswith("00_05_List_of_Plates.md"):
        return (ROOT / meta["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    raise SystemExit(f"unexpected source file for segment {segment_id}: {meta['source_file']}")


def segment_text(segment_id):
    meta = segment_by_id[segment_id]
    lines = get_source_lines(segment_id)
    return "\n".join(lines[meta["line_start"] - 1:meta["line_end"]])


existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_mention_keys = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
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
    key = (segment_id, str(start), str(start + len(surface)))
    if key in existing_mention_keys or any((r["segment_id"], r["start_char"], r["end_char"]) == key for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": note,
    })


mention(MAIN_IDS["plate33"], "m-chp8-pl33a-work", "cand-4099", "Dido and Aeneas",
        "Plate 33a work caption; reuses the work candidate already anchored in the List of Plates.")
mention(MAIN_IDS["plate33"], "m-chp8-pl33a-creator", "cand-3884", "Soumena",
        "The S0 OCR reads Soumena; CHP-8.pdf physical p.15 confirms printed Solimena. Keep the source surface and correction in S2.")
mention(MAIN_IDS["plate33"], "m-chp8-pl33a-dido", "cand-4163", "Dido",
        "Named mythological figure in the captioned work title; no event claim is inferred.")
mention(MAIN_IDS["plate33"], "m-chp8-pl33a-aeneas", "cand-4164", "Aeneas",
        "Named mythological figure in the captioned work title; no event claim is inferred.")
mention(MAIN_IDS["plate33"], "m-chp8-pl33b-gallery", "cand-3925", "gallery of the Palazzo Buonaccorsi",
        "Plate 33b names an architectural gallery space, separate from its parent palace.")
mention(MAIN_IDS["plate33"], "m-chp8-pl33b-palace", "cand-3949", "Palazzo Buonaccorsi",
        "Named as the parent building of the gallery space.")
mention(MAIN_IDS["plate33"], "m-chp8-pl33b-city", "cand-3935", "Macerata",
        "Printed location in the Plate 33b caption.")

mention(MAIN_IDS["plate34"], "m-chp8-pl34-work", "cand-4111", "Velasquez: Juan de Pareja",
        "Plate 34 work caption; reuses the List of Plates candidate without adding museum or acquisition data absent from this page.")
mention(MAIN_IDS["plate34"], "m-chp8-pl34-creator", "cand-3894", "Velasquez",
        "Printed creator attribution; not independently validated.")
mention(MAIN_IDS["plate34"], "m-chp8-pl34-sitter", "cand-3818", "Juan de Pareja",
        "Named portrait subject in the plate caption.")

mention(MAIN_IDS["plate35a"], "m-chp8-pl35a-work", "cand-4088", "Rembrandt: Aristotle contemplating the Bust of Homer",
        "Plate 35a work caption; reuses the List of Plates candidate.")
mention(MAIN_IDS["plate35a"], "m-chp8-pl35a-creator", "cand-3471", "Rembrandt",
        "Printed creator attribution; not independently validated.")
mention(MAIN_IDS["plate35a"], "m-chp8-pl35a-aristotle", "cand-3727", "Aristotle",
        "Named figure in the work title; the title is not evidence for a historical event.")
mention(MAIN_IDS["plate35a"], "m-chp8-pl35a-homer", "cand-3805", "Homer",
        "Named as the subject of the bust in the work title.")

mention(VISUAL_IDS["plate35b"], "m-chp8-pl35b-work", "cand-4092", "The Feast of Herod",
        "Plate 35b title restored from the scan; reuses the List of Plates work candidate.")
mention(VISUAL_IDS["plate35b"], "m-chp8-pl35b-creator", "cand-3093", "Rubens",
        "Printed creator attribution restored from the scan; not independently validated.")
mention(VISUAL_IDS["plate35b"], "m-chp8-pl35b-herod", "cand-4165", "Herod",
        "Named in the work title; the caption does not identify which Herod.")

mention(VISUAL_IDS["plate36a"], "m-chp8-pl36a-work", "cand-4037", "a. Francesco Petrucci: Grand Prince Ferdinand",
        "Full Plate 36a caption identifies the work; reuses the List of Plates work candidate with its fuller title.")
mention(VISUAL_IDS["plate36a"], "m-chp8-pl36a-creator", "cand-3769", "Francesco Petrucci",
        "Creator attribution restored from the rotated scan; identity remains for S3 alignment.")
mention(VISUAL_IDS["plate36a"], "m-chp8-pl36a-subject", "cand-3761", "Grand Prince Ferdinand",
        "Named portrait subject; identity is reused from the existing List of Plates candidate.")

mention(VISUAL_IDS["plate36b"], "m-chp8-pl36b-work", "cand-4039", "Girl at her toilet",
        "Plate 36b title restored from the rotated scan; reuses the List of Plates work candidate.")
mention(VISUAL_IDS["plate36b"], "m-chp8-pl36b-creator", "cand-3797", "G. M. Crespi",
        "Printed creator attribution restored from the rotated scan; not independently validated.")


def make_statement(statement_id, segment_id, line_start, line_end, subject, obj, predicate, claim,
                   qualification, mentioned_ids, quote, plate, physical_page, crossref_line,
                   ocr_corrections=None):
    qualifiers = {
        "source_line_start": line_start,
        "source_line_end": line_end,
        "pdf_physical_page": physical_page,
        "printed_page_locator": f"Plate {plate[:2]}",
        "plate_label": plate,
        "claim": claim,
        "speaker": "printed plate caption",
        "text_layer": "plate caption",
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned_ids,
        "cross_reference_segments": [{
            "segment_id": PLATE_LIST_SEGMENT,
            "source_line_start": crossref_line,
            "source_line_end": crossref_line,
        }],
    }
    if ocr_corrections:
        qualifiers["ocr_corrections"] = ocr_corrections
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": quote,
        "origin": "book",
        "source_file": segment_by_id[segment_id]["source_file"],
    }


all_33a = ["cand-4099", "cand-3884", "cand-4163", "cand-4164"]
all_33b = ["cand-3925", "cand-3949", "cand-3935"]
all_34 = ["cand-4111", "cand-3894", "cand-3818"]
all_35a = ["cand-4088", "cand-3471", "cand-3727", "cand-3805"]
all_35b = ["cand-4092", "cand-3093", "cand-4165"]
all_36a = ["cand-4037", "cand-3769", "cand-3761"]
all_36b = ["cand-4039", "cand-3797"]

q33a = "a. Soumena: Dido and Aeneas"
q33b = "b. The gallery of the Palazzo Buonaccorsi, Macerata"
q34 = "Velasquez: Juan de Pareja"
q35a = "a. Rembrandt: Aristotle contemplating the Bust of Homer"
q35b = "b. Rubens: The Feast of Herod"
q36a = "a. Francesco Petrucci: Grand Prince Ferdinand"
q36b = "b. G. M. Crespi: Girl at her toilet"

new_statements = [
    make_statement("st-chp8-pl33a-credit", MAIN_IDS["plate33"], 38, 38, "cand-4099", "cand-3884",
                   "caption_attribution", "The Plate 33a caption credits Solimena with Dido and Aeneas.",
                   "This records the printed attribution only; no external attribution judgment is added.", all_33a,
                   q33a, "33a", 15, 94, [{"source_file": MAIN_SOURCE.relative_to(ROOT).as_posix(),
                                           "source_line": 38, "ocr": "Soumena", "print": "Solimena",
                                           "basis": "CHP-8.pdf physical page 15, Plate 33."}]),
    make_statement("st-chp8-pl33a-dido", MAIN_IDS["plate33"], 38, 38, "cand-4099", "cand-4163",
                   "caption_iconographic_subject", "The Plate 33a title names Dido as an iconographic subject.",
                   "A work-title reference only; no historical event is asserted.", all_33a,
                   q33a, "33a", 15, 94),
    make_statement("st-chp8-pl33a-aeneas", MAIN_IDS["plate33"], 38, 38, "cand-4099", "cand-4164",
                   "caption_iconographic_subject", "The Plate 33a title names Aeneas as an iconographic subject.",
                   "A work-title reference only; no historical event is asserted.", all_33a,
                   q33a, "33a", 15, 94),
    make_statement("st-chp8-pl33b-city", MAIN_IDS["plate33"], 39, 39, "cand-3925", "cand-3935",
                   "caption_location_or_collection", "The Plate 33b caption locates the gallery of Palazzo Buonaccorsi at Macerata.",
                   "This records the captioned architectural space and location, not the current custody of any painting.", all_33b,
                   q33b, "33b", 15, 95),
    make_statement("st-chp8-pl33b-palace", MAIN_IDS["plate33"], 39, 39, "cand-3925", "cand-3949",
                   "caption_architectural_space", "The Plate 33b caption names the gallery as a space within Palazzo Buonaccorsi.",
                   "The gallery and its parent palace remain distinct place candidates.", all_33b,
                   q33b, "33b", 15, 95),
    make_statement("st-chp8-pl33b-space", MAIN_IDS["plate33"], 39, 39, "cand-3925", None,
                   "caption_architectural_space", "The Plate 33b caption identifies an architectural gallery space.",
                   "No designer, owner, date, or current use is supplied by this caption.", all_33b,
                   q33b, "33b", 15, 95),
    make_statement("st-chp8-pl34-credit", MAIN_IDS["plate34"], 43, 43, "cand-4111", "cand-3894",
                   "caption_attribution", "The Plate 34 caption credits Velasquez with the Juan de Pareja portrait.",
                   "The caption wording is recorded without importing the museum and location printed only in the List of Plates.", all_34,
                   q34, "34", 16, 96),
    make_statement("st-chp8-pl34-sitter", MAIN_IDS["plate34"], 43, 43, "cand-4111", "cand-3818",
                   "caption_subject", "The Plate 34 caption names Juan de Pareja as the depicted subject.",
                   "No further identity or biography is inferred from the caption.", all_34,
                   q34, "34", 16, 96),
    make_statement("st-chp8-pl35a-credit", MAIN_IDS["plate35a"], 46, 46, "cand-4088", "cand-3471",
                   "caption_attribution", "The Plate 35a caption credits Rembrandt with Aristotle contemplating the Bust of Homer.",
                   "Printed caption attribution only; no external attribution judgment is added.", all_35a,
                   q35a, "35a", 17, 97,
                   [{"source_file": MAIN_SOURCE.relative_to(ROOT).as_posix(), "source_line": 45,
                     "ocr": "[Page 3]", "print": "Plate 35", "basis": "CHP-8.pdf physical page 17."}]),
    make_statement("st-chp8-pl35a-aristotle", MAIN_IDS["plate35a"], 46, 46, "cand-4088", "cand-3727",
                   "caption_iconographic_subject", "The Plate 35a title names Aristotle as an iconographic subject.",
                   "A work-title reference only; no historical event is asserted.", all_35a,
                   q35a, "35a", 17, 97),
    make_statement("st-chp8-pl35a-homer", MAIN_IDS["plate35a"], 46, 46, "cand-4088", "cand-3805",
                   "caption_iconographic_subject", "The Plate 35a title names Homer as the subject of the bust.",
                   "This preserves the nested subject expressed in the title.", all_35a,
                   q35a, "35a", 17, 97),
    make_statement("st-chp8-pl35b-credit", VISUAL_IDS["plate35b"], 1, 1, "cand-4092", "cand-3093",
                   "caption_attribution", "The Plate 35b caption credits Rubens with The Feast of Herod.",
                   "Restored from the printed caption omitted by the section OCR; attribution is not independently verified.", all_35b,
                   q35b, "35b", 17, 100),
    make_statement("st-chp8-pl35b-herod", VISUAL_IDS["plate35b"], 1, 1, "cand-4092", "cand-4165",
                   "caption_iconographic_subject", "The Plate 35b title names Herod as an iconographic subject.",
                   "The caption does not identify which Herod.", all_35b,
                   q35b, "35b", 17, 100),
    make_statement("st-chp8-pl36a-credit", VISUAL_IDS["plate36a"], 5, 5, "cand-4037", "cand-3769",
                   "caption_attribution", "The Plate 36a caption credits Francesco Petrucci with the Grand Prince Ferdinand portrait.",
                   "The image-page caption omits 'of Tuscany', which appears in the List of Plates; this quote preserves the shorter printed wording.", all_36a,
                   q36a, "36a", 18, 101),
    make_statement("st-chp8-pl36a-subject", VISUAL_IDS["plate36a"], 5, 5, "cand-4037", "cand-3761",
                   "caption_subject", "The Plate 36a caption names Grand Prince Ferdinand as the depicted subject.",
                   "The candidate is reused from the List of Plates; no additional identity decision is made here.", all_36a,
                   q36a, "36a", 18, 101),
    make_statement("st-chp8-pl36b-credit", VISUAL_IDS["plate36b"], 7, 7, "cand-4039", "cand-3797",
                   "caption_attribution", "The Plate 36b caption credits G. M. Crespi with Girl at her toilet.",
                   "Restored from the rotated printed page; no sitter identity is inferred.", all_36b,
                   q36b, "36b", 18, 102),
]

existing_statement_ids = {row["statement_id"] for row in statement_rows}
new_statement_ids = [row["statement_id"] for row in new_statements]
if len(set(new_statement_ids)) != len(new_statement_ids) or existing_statement_ids.intersection(new_statement_ids):
    raise SystemExit("duplicate statement ID in migration payload or current table")
for row in new_statements:
    if row["segment_id"] not in segment_by_id:
        raise SystemExit(f"statement references missing segment: {row['statement_id']}")
    text = segment_text(row["segment_id"])
    if row["original_quote"] not in text:
        raise SystemExit(f"statement quote is not present in segment: {row['statement_id']}")
    for candidate_id in row["qualifiers"]["mentioned_candidate_ids"]:
        if candidate_id not in candidate_ids:
            raise SystemExit(f"statement references missing candidate: {row['statement_id']} -> {candidate_id}")
    for crossref in row["qualifiers"]["cross_reference_segments"]:
        if crossref["segment_id"] not in segment_by_id:
            raise SystemExit(f"statement cross-reference missing: {row['statement_id']}")

coverage_updates = {
    MAIN_IDS["plate33"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L38-39",
        "note": "Printed Plate 33 captions read against CHP-8.pdf physical p.15. Reuses front-matter work, figure, gallery, parent-palace, and city candidates; S0 'Soumena' is corrected to printed 'Solimena' only in S2 qualifiers. The caption's 'formerly at Palazzo Buonaccorsi' wording occurs in the List of Plates, not on this image page, and is not imported into these statements.",
    },
    MAIN_IDS["plate34"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L42-43",
        "note": "Printed Plate 34 header and Velasquez: Juan de Pareja caption read against CHP-8.pdf physical p.16. The generic plate-group heading is editorial navigation; caption claims are anchored to L43 and reuse the List of Plates candidates. Museum and city information absent from this image page is not copied into its statements.",
    },
    MAIN_IDS["plate35a"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L46-46",
        "note": "Printed Plate 35a caption read against CHP-8.pdf physical p.17. The S0 page marker at L45 is misread as [Page 3]; the plate label is corrected in S2. Work, artist, Aristotle, and Homer reuse candidates from the List of Plates; the acquisition and museum details from that list are not imported here.",
    },
    MAIN_IDS["plate36_ocr"]: {
        "disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
        "note": "L48-67 is a rotated/reversed OCR residue for Plate 36 and does not preserve reliable caption text. The heading and two image captions are restored in the registered visual-transcription segments for CHP-8.pdf physical p.18; no unique semantic content is lost by excluding this OCR rendering.",
    },
    VISUAL_IDS["plate35b"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L1-1",
        "note": "Caption b of printed Plate 35 is visually transcribed from CHP-8.pdf physical p.17 because section OCR omitted it. It reuses the Plate 35b work, Rubens, and Herod candidates already created from the List of Plates; no external attribution or identity claim is added.",
    },
    VISUAL_IDS["plate36_heading"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L3-3",
        "note": "no_semantic_content: Printed Plate 36 grouping heading visually transcribed from CHP-8.pdf physical p.18. It is editorial plate navigation referring to Plates 36-40; it does not establish a patronage relation, research topic, or hierarchy node.",
    },
    VISUAL_IDS["plate36a"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L5-5",
        "note": "Caption a of printed Plate 36 visually transcribed from CHP-8.pdf physical p.18. Reuses the Petrucci, work, and Grand Prince Ferdinand candidates from the List of Plates. The image caption omits 'of Tuscany'; its shorter wording is preserved.",
    },
    VISUAL_IDS["plate36b"]: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L7-7",
        "note": "Caption b of printed Plate 36 visually transcribed from CHP-8.pdf physical p.18. Reuses the Crespi and work candidates from the List of Plates; no sitter identity is inferred.",
    },
}

updated_coverage = []
for segment in segments:
    sid = segment["segment_id"]
    if sid in coverage_updates:
        updated_coverage.append({"chapter": segment["chapter"], "segment_id": sid, **coverage_updates[sid]})
    elif sid in coverage_by_id:
        updated_coverage.append(dict(coverage_by_id[sid]))
    else:
        raise SystemExit(f"coverage row missing and no migration update supplied: {sid}")
if set(row["segment_id"] for row in updated_coverage) != set(segment_by_id):
    raise SystemExit("coverage rows do not match current source segments")

preview = {
    "mode": "dry-run",
    "main_segments": MAIN_IDS,
    "visual_segments": VISUAL_IDS,
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_updates": len(coverage_updates),
    "coverage_total": len(updated_coverage),
    "statement_ids": new_statement_ids,
    "ocr_corrections": ["L38 Soumena -> Solimena", "L45 [Page 3] -> Plate 35"],
}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--apply", action="store_true", help="write mentions, statements, and coverage")
args = parser.parse_args()
if not args.apply:
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    raise SystemExit(0)

for path in (MENTION_PATH, STATEMENT_PATH, COVERAGE_PATH):
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
