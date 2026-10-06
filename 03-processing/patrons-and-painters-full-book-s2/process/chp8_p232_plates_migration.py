"""Controlled S2 migration for the p.232 Plate 37-40 captions.

Default invocation is a read-only dry run. Plate 38's omitted printed heading
is in a registered visual-transcription segment; cropped/absent captions are
not reconstructed from the List of Plates as if visible on the image page.
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
VISUAL_SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_ii_plates_p232_visual-transcription.md"
PLATES_SOURCE = ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md"
SEGMENTS_PATH = TABLES / "segments.jsonl"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MENTION_PATH = TABLES / "mentions.csv"
STATEMENT_PATH = TABLES / "book-statements.jsonl"
COVERAGE_PATH = TABLES / "s2-coverage.csv"
BACKUP_SUFFIX = ".bak-s2-chp8-p232-plates-20261001"

MAIN_IDS = {
    "plate37": "chp-8:08_CHP-8_sec_ii:l259-261",
    "plate38": "chp-8:08_CHP-8_sec_ii:l263-266",
    "plate40": "chp-8:08_CHP-8_sec_ii:l268-269",
}
VISUAL_ID = "chp-8:08_CHP-8_sec_ii_plates_p232_visual-transcription:l1-1"
PLATE_LIST_ID = "front-matter:00_05_List_of_Plates:l83-118"
TARGET_IDS = set(MAIN_IDS.values()) | {VISUAL_ID}


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
if not TARGET_IDS <= set(segment_by_id):
    raise SystemExit(f"required segments missing: {sorted(TARGET_IDS - set(segment_by_id))}")

for segment_id in TARGET_IDS | {PLATE_LIST_ID}:
    row = segment_by_id.get(segment_id)
    if row is None:
        raise SystemExit(f"required cross-reference segment missing: {segment_id}")
    source_path = ROOT / row["source_file"]
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != row["asset_sha256"]:
        raise SystemExit(f"source asset changed after segmentation: {row['source_file']}")

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
if VISUAL_ID in coverage_by_id:
    raise SystemExit(f"visual segment already has coverage; inspect before rerunning: {VISUAL_ID}")
if any(row["segment_id"] in TARGET_IDS for row in mention_rows):
    raise SystemExit("mentions already exist for a target segment; inspect before rerunning")
if any(row["segment_id"] in TARGET_IDS for row in statement_rows):
    raise SystemExit("statements already exist for a target segment; inspect before rerunning")


def segment_text(segment_id: str) -> str:
    meta = segment_by_id[segment_id]
    lines = (ROOT / meta["source_file"]).read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[meta["line_start"] - 1:meta["line_end"]])
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if digest != meta["sha256"]:
        raise SystemExit(f"line-slice hash mismatch: {segment_id}")
    return text


texts = {segment_id: segment_text(segment_id) for segment_id in TARGET_IDS | {PLATE_LIST_ID}}
existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_mention_keys = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
new_mentions = []


def add_mention(segment_id, mention_id, candidate_id, surface, note, occurrence=0):
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"missing candidate: {mention_id} -> {candidate_id}")
    text = texts[segment_id]
    starts = []
    offset = 0
    while True:
        start = text.find(surface, offset)
        if start < 0:
            break
        starts.append(start)
        offset = start + 1
    if occurrence >= len(starts):
        raise SystemExit(f"surface occurrence missing in {segment_id}: {surface!r} #{occurrence}")
    start = starts[occurrence]
    end = start + len(surface)
    key = (segment_id, str(start), str(end))
    if key in existing_mention_keys or any((r["segment_id"], r["start_char"], r["end_char"]) == key for r in new_mentions):
        raise SystemExit(f"duplicate mention span: {key}")
    new_mentions.append({
        "mention_id": mention_id, "segment_id": segment_id, "candidate_id": candidate_id,
        "surface_form": surface, "start_char": str(start), "end_char": str(end), "note": note,
    })


add_mention(MAIN_IDS["plate37"], "m-chp8-pl37a-work", "cand-4041", "The Painter’s family",
            "Printed Plate 37a work title; reuses the List of Plates work candidate.")
add_mention(MAIN_IDS["plate37"], "m-chp8-pl37a-creator", "cand-3797", "G. M. Crespi",
            "Printed creator attribution; no external attribution judgment is added.")
add_mention(MAIN_IDS["plate37"], "m-chp8-pl37b-work", "cand-4038", "The Fair at Poggio a Caiano",
            "Printed Plate 37b title; reuses the List of Plates work candidate.")
add_mention(MAIN_IDS["plate37"], "m-chp8-pl37b-creator", "cand-3797", "G. M. Crespi",
            "Printed creator attribution; no external attribution judgment is added.", occurrence=1)

add_mention(MAIN_IDS["plate38"], "m-chp8-pl38a-work", "cand-4097", "Rape of Europa",
            "Printed Plate 38a title; keeps the title claim separate from historical event claims.")
add_mention(MAIN_IDS["plate38"], "m-chp8-pl38a-figure", "cand-4168", "Europa",
            "Named in the work title; no event claim is inferred.")
add_mention(MAIN_IDS["plate38"], "m-chp8-pl38b-work", "cand-4096", "Pan and Syrinx",
            "Printed Plate 38b title; keeps the title claim separate from historical event claims.")
add_mention(MAIN_IDS["plate38"], "m-chp8-pl38b-pan", "cand-4169", "Pan",
            "Named in the work title; no event claim is inferred.")
add_mention(MAIN_IDS["plate38"], "m-chp8-pl38b-syrinx", "cand-4170", "Syrinx",
            "Named in the work title; no event claim is inferred.")
add_mention(MAIN_IDS["plate38"], "m-chp8-pl38-palace", "cand-3952", "PITTI PALACE",
            "Printed plate heading venue; caption-level label only, not a current-custody claim.")
add_mention(MAIN_IDS["plate38"], "m-chp8-pl38-city", "cand-3397", "FLORENCE",
            "Printed plate heading location; reused from the List of Plates candidate.")
add_mention(VISUAL_ID, "m-chp8-pl38-creator", "cand-3101", "SEBASTIANO RICCI",
            "Creator named in the printed heading restored from CHP-8.pdf physical p.36.")

add_mention(MAIN_IDS["plate40"], "m-chp8-pl40a-work", "cand-3996", "A group of musicians",
            "Printed Plate 40a title; reuses the List of Plates work candidate.")
add_mention(MAIN_IDS["plate40"], "m-chp8-pl40a-creator", "cand-3705", "A. D. Gabbiani",
            "Printed creator attribution; no external attribution judgment is added.")


def make_statement(statement_id, segment_id, line_start, line_end, quote, predicate, subject, obj,
                   claim, qualification, mentioned_ids, plate_label, physical_page, crossrefs,
                   speaker="printed plate caption", text_layer="plate caption"):
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": line_start,
            "source_line_end": line_end,
            "pdf_physical_page": physical_page,
            "printed_page_locator": f"Plate {plate_label[:2]}",
            "plate_label": plate_label,
            "claim": claim,
            "speaker": speaker,
            "text_layer": text_layer,
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned_ids,
            "cross_reference_segments": crossrefs,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": segment_by_id[segment_id]["source_file"],
    }


plate_list = lambda start, end: {"segment_id": PLATE_LIST_ID, "source_line_start": start, "source_line_end": end}
main37 = MAIN_IDS["plate37"]
main38 = MAIN_IDS["plate38"]
main40 = MAIN_IDS["plate40"]
visual_quote = "FRESCOES BY SEBASTIANO RICCI"
location_quote = "IN PITTI PALACE, FLORENCE (see Plates 38 and 39)"
quote37a = "a. G. M. Crespi: The Painter’s family"
quote37b = "b. G. M. Crespi: The Fair at Poggio a Caiano"
quote38a = "a. Rape of Europa"
quote38b = "b. Pan and Syrinx"
quote40a = "a. A. D. Gabbiani: A group of musicians"

new_statements = [
    make_statement("st-chp8-pl37a-credit", main37, 260, 260, quote37a, "caption_attribution",
                   "cand-4041", "cand-3797", "The Plate 37a caption credits Crespi with The Painter’s family.",
                   "Printed caption attribution only; no external authorship judgment is added.",
                   ["cand-4041", "cand-3797"], "37a", 35, [plate_list(103, 103)]),
    make_statement("st-chp8-pl37b-credit", main37, 260, 260, quote37b, "caption_attribution",
                   "cand-4038", "cand-3797", "The Plate 37b caption credits Crespi with The Fair at Poggio a Caiano.",
                   "Printed caption attribution only; no external authorship judgment is added.",
                   ["cand-4038", "cand-3797"], "37b", 35, [plate_list(104, 104)]),
    make_statement("st-chp8-pl37b-detail", main37, 260, 261, quote37b, "caption_title_context",
                   "cand-4038", None, "The Plate 37b image is marked as a detail of The Fair at Poggio a Caiano.",
                   "The scan shows '(detail)' after the title; S0 OCR places a stray leading period on L261. The full caption is not reconstructed from the List of Plates.",
                   ["cand-4038"], "37b", 35, [plate_list(104, 104)]),
    make_statement("st-chp8-pl38-group-attribution", VISUAL_ID, 1, 1, visual_quote, "caption_attribution",
                   None, "cand-3101", "The printed Plate 38–39 heading identifies the grouped frescos as by Sebastiano Ricci.",
                   "Group heading attribution only; its Plate 38–39 scope is resolved by the adjacent printed cross-reference and the List of Plates.",
                   ["cand-3101", "cand-4097", "cand-4096", "cand-4098"], "38–39", 36,
                   [{"segment_id": main38, "source_line_start": 264, "source_line_end": 264},
                    plate_list(107, 109)], speaker="printed plate heading", text_layer="caption heading"),
    make_statement("st-chp8-pl38-group-site", main38, 264, 264, location_quote, "caption_location_or_collection",
                   None, "cand-3952", "The Plate 38–39 caption heading places the grouped frescoes in Pitti Palace.",
                   "Printed caption venue only; this does not independently verify present custody.",
                   ["cand-3952", "cand-4097", "cand-4096", "cand-4098"], "38–39", 36,
                   [plate_list(107, 109)], speaker="printed plate heading", text_layer="caption heading"),
    make_statement("st-chp8-pl38-group-city", main38, 264, 264, location_quote, "caption_location_or_collection",
                   None, "cand-3397", "The Plate 38–39 caption heading locates the grouped frescoes in Florence.",
                   "Printed caption location only; not an independent verification of the works or their custody.",
                   ["cand-3397", "cand-4097", "cand-4096", "cand-4098"], "38–39", 36,
                   [plate_list(107, 109)], speaker="printed plate heading", text_layer="caption heading"),
    make_statement("st-chp8-pl38a-europa", main38, 265, 265, quote38a, "caption_iconographic_subject",
                   "cand-4097", "cand-4168", "The Plate 38a title names Europa as an iconographic subject.",
                   "Work-title reference only; no historical event is asserted.",
                   ["cand-4097", "cand-4168"], "38a", 36, [plate_list(107, 107)]),
    make_statement("st-chp8-pl38b-pan", main38, 266, 266, quote38b, "caption_iconographic_subject",
                   "cand-4096", "cand-4169", "The Plate 38b title names Pan as an iconographic subject.",
                   "Work-title reference only; no historical event is asserted.",
                   ["cand-4096", "cand-4169"], "38b", 36, [plate_list(108, 108)]),
    make_statement("st-chp8-pl38b-syrinx", main38, 266, 266, quote38b, "caption_iconographic_subject",
                   "cand-4096", "cand-4170", "The Plate 38b title names Syrinx as an iconographic subject.",
                   "Work-title reference only; no historical event is asserted.",
                   ["cand-4096", "cand-4170"], "38b", 36, [plate_list(108, 108)]),
    make_statement("st-chp8-pl40a-credit", main40, 269, 269, quote40a, "caption_attribution",
                   "cand-3996", "cand-3705", "The Plate 40a caption credits A. D. Gabbiani with A group of musicians.",
                   "Printed caption attribution only; the Plate 40b caption is cropped and is not inferred here.",
                   ["cand-3996", "cand-3705"], "40a", 38, [plate_list(110, 110)]),
]

existing_statement_ids = {row["statement_id"] for row in statement_rows}
new_statement_ids = [row["statement_id"] for row in new_statements]
if len(set(new_statement_ids)) != len(new_statement_ids) or existing_statement_ids.intersection(new_statement_ids):
    raise SystemExit("duplicate statement ID in migration payload or current table")
for row in new_statements:
    if row["segment_id"] not in segment_by_id or row["original_quote"] not in texts[row["segment_id"]]:
        raise SystemExit(f"statement quote is not present in its segment: {row['statement_id']}")
    for candidate_id in ([row["subject_candidate_id"], row["object_candidate_id"]]
                         + row["qualifiers"]["mentioned_candidate_ids"]):
        if candidate_id is not None and candidate_id not in candidate_ids:
            raise SystemExit(f"statement references missing candidate: {row['statement_id']} -> {candidate_id}")
    for crossref in row["qualifiers"]["cross_reference_segments"]:
        if crossref["segment_id"] not in segment_by_id:
            raise SystemExit(f"statement cross-reference missing: {row['statement_id']}")
        if crossref["source_line_end"] > segment_by_id[crossref["segment_id"]]["line_end"]:
            raise SystemExit(f"cross-reference line exceeds its segment: {row['statement_id']}")

coverage_updates = {
    main37: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L260-261",
        "note": "Plate 37a/b captions read against CHP-8.pdf physical p.35. Reuses the List of Plates work and Crespi candidates. The lower c caption is cut off at the scan edge; its complete text is already represented in the separately anchored List of Plates segment and is not reconstructed here.",
    },
    main38: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L264-266",
        "note": "Plate 38 heading and a/b titles read against CHP-8.pdf physical p.36. OCR omits the heading 'Frescoes by Sebastiano Ricci', supplied in the registered visual-transcription segment. L264 prints Pitti Palace, Florence and refers to Plates 38–39; Plate 39 itself has no separate caption. Work and subject candidates are reused from the List of Plates.",
    },
    main40: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L269-269",
        "note": "Plate 40a caption read against CHP-8.pdf physical p.38; reuses the List of Plates work and Gabbiani candidates. Plate 40b caption is cropped at the scan edge; the complete List of Plates caption is not imported into this image-page segment.",
    },
    VISUAL_ID: {
        "disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L1-1",
        "note": "Plate 38 heading visually transcribed from CHP-8.pdf physical p.36 because the canonical section OCR omitted it. The venue line remains in the canonical OCR and is not duplicated.",
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
    "segments": sorted(TARGET_IDS),
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_updates": len(coverage_updates),
    "coverage_total": len(updated_coverage),
    "statement_ids": new_statement_ids,
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
