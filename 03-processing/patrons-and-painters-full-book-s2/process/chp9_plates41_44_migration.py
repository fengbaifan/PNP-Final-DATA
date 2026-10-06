"""Controlled S2 migration for Chapter 9 Plates 41–44.

Default invocation is a read-only dry run. Reversed OCR is preserved; two
printed captions are supplied as a derived, line-addressable transcription.
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
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
PDF = ROOT / "02-sources" / "01-book" / "CHP-9.pdf"
MAIN_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
VISUAL_SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro_plates_visual-transcription.md"
LIST_SEGMENT = "front-matter:00_05_List_of_Plates:l83-118"
P248 = "chp-9:09_CHP-9_intro:l38-46"
P41_OCR = "chp-9:09_CHP-9_intro:l48-59"
P42_OCR = "chp-9:09_CHP-9_intro:l61-63"
P43_OCR = "chp-9:09_CHP-9_intro:l65-72"
P44_OCR = "chp-9:09_CHP-9_intro:l74-75"
V41 = "chp-9:09_CHP-9_intro_plates_visual-transcription:l1-2"
V43 = "chp-9:09_CHP-9_intro_plates_visual-transcription:l4-4"
EXPECTED_ASSET_HASH = "ee4f53b8d2f38f89271c6b62f8bc007d0c74db962aab2c0032e3054cfb10ff1e"
EXPECTED_V41_HASH = "7d30c5b097201d2af051669a17fe0bdbed95e20438c2c521d7c5f8ef12d07f02"
EXPECTED_V43_HASH = "e1f766fcaf0f4e12021da1588565eb1cf58d0489a8923bf13e11f753855dbba2"
BACKUP_SUFFIX = ".bak-s2-chp9-plates41-43-20261001"


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


def write_jsonl_atomic(path: Path, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False, suffix=".tmp") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary = Path(stream.name)
    temporary.replace(path)


segments = read_jsonl(TABLES / "segments.jsonl")
segment_by_id = {row["segment_id"]: row for row in segments}
if len(segment_by_id) != len(segments) or len(segments) != 814:
    raise SystemExit(f"unexpected segment inventory: {len(segments)} rows")
for required in (LIST_SEGMENT, P248, P41_OCR, P42_OCR, P43_OCR, P44_OCR, V41, V43):
    if required not in segment_by_id:
        raise SystemExit(f"missing required source segment: {required}")
if segment_by_id[V41]["sha256"] != EXPECTED_V41_HASH or segment_by_id[V43]["sha256"] != EXPECTED_V43_HASH:
    raise SystemExit("derived visual-transcription segment hash changed")
if segment_by_id[V41]["asset_sha256"] != EXPECTED_ASSET_HASH or segment_by_id[V43]["asset_sha256"] != EXPECTED_ASSET_HASH:
    raise SystemExit("visual-transcription asset hash changed")
if hashlib.sha256(VISUAL_SOURCE.read_bytes()).hexdigest() != EXPECTED_ASSET_HASH:
    raise SystemExit("visual-transcription asset changed")
if not PDF.is_file() or not all((PROCESS / name).is_file() for name in (
    "plate41_page_review.png", "plate42_page_review.png", "plate43_page_review.png", "plate44_page_review.png"
)):
    raise SystemExit("CHP-9.pdf or one of the reviewed plate images is missing")

visual_lines = VISUAL_SOURCE.read_text(encoding="utf-8-sig").splitlines()
main_lines = MAIN_SOURCE.read_text(encoding="utf-8-sig").splitlines()

candidate_path = TABLES / "entity-candidates.csv"
mention_path = TABLES / "mentions.csv"
statement_path = TABLES / "book-statements.jsonl"
coverage_path = TABLES / "s2-coverage.csv"
candidate_fields, candidate_rows = read_csv(candidate_path)
mention_fields, mention_rows = read_csv(mention_path)
statement_rows = read_jsonl(statement_path)
coverage_fields, coverage_rows = read_csv(coverage_path)
coverage_by_id = {row["segment_id"]: row for row in coverage_rows}
if len(coverage_by_id) != len(coverage_rows):
    raise SystemExit("s2-coverage.csv contains duplicate segment IDs")

expected_coverage = {
    P248: ("reviewed", "partial", "L38-46"),
    P41_OCR: ("queued", "pending", ""),
    P42_OCR: ("queued", "pending", ""),
    P43_OCR: ("queued", "pending", ""),
    P44_OCR: ("queued", "pending", ""),
}
for segment_id, expected in expected_coverage.items():
    row = coverage_by_id.get(segment_id)
    if row is None or (row["disposition"], row["migration_status"], row["source_line_ranges"]) != expected:
        raise SystemExit(f"unexpected coverage for {segment_id}: {row}")
for segment_id in (V41, V43):
    if segment_id in coverage_by_id:
        raise SystemExit(f"visual transcription already has S2 coverage: {segment_id}")

candidate_ids = {row["candidate_id"] for row in candidate_rows}
if len(candidate_ids) != len(candidate_rows) or max(int(value.split("-")[1]) for value in candidate_ids) != 8168:
    raise SystemExit("candidate inventory changed since p.248; inspect before migration")
new_candidate_id = "cand-8169"
new_candidate_name = "Barbaro family"
new_candidate_type = "family"
if new_candidate_id in candidate_ids:
    raise SystemExit(f"candidate ID already exists: {new_candidate_id}")
if any(row["canonical_name"] == new_candidate_name and row["suggested_type"] == new_candidate_type for row in candidate_rows):
    raise SystemExit("Barbaro family natural key already exists; reuse it after inspection")
candidate_rows.append({
    "candidate_id": new_candidate_id,
    "index_entry_id": "",
    "canonical_name": new_candidate_name,
    "index_page_range": "",
    "suggested_type": new_candidate_type,
    "status": "open",
    "index_source_file": "",
    "sub_entry": "",
    "detail": "Family named collectively in the Plate 41a caption as represented in portraits; members are not enumerated or identified from this caption alone.",
    "exclude_reason": "",
    "candidate_origin": "body-mention",
    "candidate_source_ref": f"{V41}#L1",
})
candidate_ids.add(new_candidate_id)

existing_mention_ids = {row["mention_id"] for row in mention_rows}
existing_spans = {(row["segment_id"], row["start_char"], row["end_char"]) for row in mention_rows}
new_mentions = []
source_by_segment = {V41: visual_lines, V43: visual_lines}
line_offsets = {}
for segment_id in (V41, V43):
    meta = segment_by_id[segment_id]
    selected = source_by_segment[segment_id][meta["line_start"] - 1:meta["line_end"]]
    offsets = {}
    offset = 0
    for line_no, line in zip(range(meta["line_start"], meta["line_end"] + 1), selected):
        offsets[line_no] = offset
        offset += len(line) + 1
    line_offsets[segment_id] = offsets


def mention(segment_id, line_no, suffix, candidate_id, surface, note):
    mention_id = f"m-chp9-plates-{suffix}"
    if mention_id in existing_mention_ids or any(row["mention_id"] == mention_id for row in new_mentions):
        raise SystemExit(f"duplicate mention ID: {mention_id}")
    if candidate_id not in candidate_ids:
        raise SystemExit(f"mention references missing candidate: {mention_id} -> {candidate_id}")
    line = source_by_segment[segment_id][line_no - 1]
    start_in_line = line.find(surface)
    if start_in_line < 0 or line.find(surface, start_in_line + 1) >= 0:
        raise SystemExit(f"surface must occur once at L{line_no}: {surface!r}")
    start = line_offsets[segment_id][line_no] + start_in_line
    end = start + len(surface)
    span = (segment_id, str(start), str(end))
    if span in existing_spans or any((row["segment_id"], row["start_char"], row["end_char"]) == span for row in new_mentions):
        raise SystemExit(f"duplicate mention span: {mention_id} {surface!r}")
    new_mentions.append({
        "mention_id": mention_id,
        "segment_id": segment_id,
        "candidate_id": candidate_id,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": note,
    })


mention(V41, 1, "p41a-facade", "cand-4032", "Façade of S. Maria del Giglio", "Printed Plate 41a caption; reuses the List of Plates work candidate.")
mention(V41, 1, "p41a-church", "cand-3968", "S. Maria del Giglio", "Nested building mention; distinct from the façade work.")
mention(V41, 1, "p41a-barbaro-family", new_candidate_id, "Barbaro family", "Collective portrait group named by the printed caption; no individual sitter is identified.")
mention(V41, 2, "p41b-monument", "cand-4063", "Monument to Doge Giovanni Pesaro", "Printed Plate 41b monument caption; reuses the List of Plates candidate.")
mention(V41, 2, "p41b-subject", "cand-3791", "Giovanni Pesaro", "Named subject of the monument; the caption supplies the Doge title.")
mention(V41, 2, "p41b-church", "cand-3917", "Church of the Frari", "Building location named in the printed caption.")
mention(V43, 4, "p43-creator", "cand-3781", "Tiepolo", "Printed creator attribution; reuses the List of Plates candidate.")
mention(V43, 4, "p43-work", "cand-4105", "Marriage Allegory of Rezzonico family", "Printed Plate 43 work caption; preserves the wording shown on the plate page.")
mention(V43, 4, "p43-family", "cand-3615", "Rezzonico family", "Captioned subject group; the plate page does not identify the marriage partners.")

existing_statement_ids = {row["statement_id"] for row in statement_rows}
new_statements = []


def make_statement(statement_id, segment_id, first_line, last_line, pdf_page, plate_label,
                   subject, obj, predicate, claim, qualification, mentioned, quote,
                   cross_refs):
    meta = segment_by_id[segment_id]
    excerpt = "\n".join(source_by_segment[segment_id][first_line - 1:last_line])
    if quote not in excerpt:
        raise SystemExit(f"statement quote is not present in source lines: {statement_id}")
    if any(candidate_id not in candidate_ids for candidate_id in mentioned):
        raise SystemExit(f"statement has missing candidate: {statement_id}")
    if any(ref["segment_id"] not in segment_by_id for ref in cross_refs):
        raise SystemExit(f"statement has missing cross-reference segment: {statement_id}")
    return {
        "statement_id": statement_id,
        "segment_id": segment_id,
        "subject_candidate_id": subject,
        "object_candidate_id": obj,
        "predicate": predicate,
        "qualifiers": {
            "source_line_start": first_line,
            "source_line_end": last_line,
            "pdf_physical_page": pdf_page,
            "printed_page_locator": f"Plate {plate_label[:2]}",
            "plate_label": plate_label,
            "claim": claim,
            "speaker": "printed plate caption",
            "text_layer": "plate caption",
            "qualification": qualification,
            "mentioned_candidate_ids": mentioned,
            "cross_reference_segments": cross_refs,
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": meta["source_file"],
    }


new_statements = [
    make_statement(
        "st-chp9-plate41a-barbaro-family-portraits", V41, 1, 1, 7, "41a",
        "cand-4032", new_candidate_id, "caption_subject_group",
        "The Plate 41a caption says the façade of S. Maria del Giglio is shown with portraits of the Barbaro family.",
        "The family is named collectively; the caption does not identify individual sitters or establish membership beyond its wording.",
        ["cand-4032", "cand-3968", new_candidate_id], visual_lines[0],
        [{"segment_id": LIST_SEGMENT, "source_line_start": 112, "source_line_end": 112},
         {"segment_id": P248, "source_line_start": 42, "source_line_end": 45}],
    ),
    make_statement(
        "st-chp9-plate41b-monument-subject", V41, 2, 2, 7, "41b",
        "cand-4063", "cand-3791", "caption_subject",
        "The Plate 41b caption names Giovanni Pesaro as the subject of his monument.",
        "The caption gives the Doge title but no maker or date.",
        ["cand-4063", "cand-3791", "cand-3917"], visual_lines[1],
        [{"segment_id": LIST_SEGMENT, "source_line_start": 113, "source_line_end": 113}],
    ),
    make_statement(
        "st-chp9-plate41b-monument-location", V41, 2, 2, 7, "41b",
        "cand-4063", "cand-3917", "caption_location_or_collection",
        "The Plate 41b caption locates the monument in the Church of the Frari.",
        "Venice appears in the List of Plates caption but not in this visual caption line.",
        ["cand-4063", "cand-3917", "cand-3791"], visual_lines[1],
        [{"segment_id": LIST_SEGMENT, "source_line_start": 113, "source_line_end": 113}],
    ),
    make_statement(
        "st-chp9-plate43-tiepolo-attribution", V43, 4, 4, 9, "43",
        "cand-4105", "cand-3781", "caption_attribution",
        "The Plate 43 caption credits Tiepolo with the Marriage Allegory of the Rezzonico family.",
        "Printed caption attribution; no external attribution judgment is added.",
        ["cand-4105", "cand-3781", "cand-3615"], visual_lines[3],
        [{"segment_id": LIST_SEGMENT, "source_line_start": 116, "source_line_end": 117}],
    ),
    make_statement(
        "st-chp9-plate43-rezzonico-family-subject", V43, 4, 4, 9, "43",
        "cand-4105", "cand-3615", "caption_subject_group",
        "The Plate 43 caption names the Rezzonico family as the subject group of the marriage allegory.",
        "Preserve the plate-page wording without the article and location supplied in the List of Plates; the marriage partners remain unnamed here.",
        ["cand-4105", "cand-3781", "cand-3615"], visual_lines[3],
        [{"segment_id": LIST_SEGMENT, "source_line_start": 116, "source_line_end": 117}],
    ),
]
new_statement_ids = {row["statement_id"] for row in new_statements}
if len(new_statement_ids) != len(new_statements) or existing_statement_ids & new_statement_ids:
    raise SystemExit("duplicate statement ID")

coverage_updates = {
    P41_OCR: {"disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
              "note": "CHP-9.pdf physical p.7 confirms Plate 41. The rotated/reversed OCR residual is replaced by the registered transcription segments for captions 41a and 41b; the grouping title is editorial navigation. The unique family-portrait wording is captured from the printed caption, not inferred from the OCR residue."},
    P42_OCR: {"disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
              "note": "CHP-9.pdf physical p.8 confirms Plate 42. Both readable captions match the semantically processed List of Plates entries; the plate-page OCR adds no distinct caption claim and is excluded as duplicate caption text, not as an unreviewed page."},
    P43_OCR: {"disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
              "note": "CHP-9.pdf physical p.9 confirms the rotated Plate 43 caption. The reversed OCR residual is replaced by the registered visual-transcription segment, preserving the plate-page wording separately from the fuller List of Plates entry."},
    P44_OCR: {"disposition": "excluded", "migration_status": "complete", "source_line_ranges": "",
              "note": "CHP-9.pdf physical p.10 confirms Plate 44. Its readable caption matches the semantically processed List of Plates entry; the plate-page OCR adds no distinct caption claim and is excluded as duplicate caption text, not as an unreviewed page."},
    V41: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L1-2",
          "note": "Derived visual transcription of CHP-9.pdf physical p.7 Plate 41a–b. Reuses the indexed work, subject, and church candidates for the printed captions; Plate 41a's additional Barbaro-family portrait phrase is recorded with a family candidate and no individual sitters inferred. The group heading in the OCR residual is editorial navigation."},
    V43: {"disposition": "reviewed", "migration_status": "complete", "source_line_ranges": "L4-4",
          "note": "Derived visual transcription of CHP-9.pdf physical p.9 Plate 43. Records the plate-page caption wording and links the existing work, creator, and family candidates; no location or marriage partners are inferred."},
}
updated_coverage = []
for segment in segments:
    segment_id = segment["segment_id"]
    if segment_id in coverage_updates:
        updated_coverage.append({"chapter": segment["chapter"], "segment_id": segment_id, **coverage_updates[segment_id]})
    elif segment_id in coverage_by_id:
        updated_coverage.append(dict(coverage_by_id[segment_id]))
    else:
        raise SystemExit(f"no coverage row or update for segment: {segment_id}")
if len(updated_coverage) != len(segments) or {row["segment_id"] for row in updated_coverage} != set(segment_by_id):
    raise SystemExit("coverage rows do not exactly match the source-segment inventory")

preview = {
    "segments": [P41_OCR, P42_OCR, P43_OCR, P44_OCR, V41, V43],
    "new_candidates": [new_candidate_id],
    "new_mentions": len(new_mentions),
    "new_statements": len(new_statements),
    "coverage_updates": {key: [value["disposition"], value["migration_status"]] for key, value in coverage_updates.items()},
    "statement_ids": [row["statement_id"] for row in new_statements],
}

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the preflighted plate migration")
args = parser.parse_args()
print(json.dumps(preview, ensure_ascii=False))
if not args.apply:
    print("DRY RUN: no table files changed")
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
    write_csv_atomic(candidate_path, candidate_fields, candidate_rows)
    write_csv_atomic(mention_path, mention_fields, mention_rows + new_mentions)
    write_jsonl_atomic(statement_path, statement_rows + new_statements)
    write_csv_atomic(coverage_path, coverage_fields, updated_coverage)
    print("applied; backups=" + ", ".join(backup.name for _, backup in backups))
