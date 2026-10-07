#!/usr/bin/env python3
"""Classify p.471 index entries and correct candidate variants supported by print."""

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MARKER_SEGMENT = "chp-22:22_CHP-22Index:l3181-3182"
CONTENT_SEGMENT = "chp-22:22_CHP-22Index:l3184-3292"
BACKUP_SUFFIX = ".bak-s2-chp22-index-p471-left-l3181-3292-20261007"

EXPECTED_HASHES = {
    "02-sources/02-Markdown/22_CHP-22Index.md": "421811ae101e6445964aa155f253a566b42ca634b60d547c5057674c3c7f7081",
    "02-sources/01-book/CHP-22Index.pdf": "1a9edbab073c716ee650f6159a38918e54ee3e18bf1f18c1d92b8fe0de720be5",
    "02-sources/03-Index/03-2-Index-CSV/T.csv": "0bb8f044307aa705fdbef065e4c4353c3f46cf598d5ae888772db227de41266a",
    "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv": "19a9e5db94a3da83c673a7fa03b003ed501317de161e4664ca572b0f0d6d5e21",
    "04-knowledge/tables/segments.jsonl": "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    "01-domain/taxonomy-registry.md": "0e870a66df957937765f45d39879add56c003faadbd5e17d7d0c3d002b57885c",
    "02-sources/02-Markdown/06_CHP-6_sec_v.md": "724f421d1c98612a8820404c82dda956dadaf6006483fcdf394cc53af4e72d15",
    "02-sources/02-Markdown/09_CHP-9_intro.md": "9b63ad7d1e2326f0ca7448efcd490c9ae5fce8c237c4289161227fe55a8518c3",
    "02-sources/02-Markdown/09_CHP-9_sec_ii.md": "67d60205c246f2f126433bab8a22ddb29ed73e2af2fed5fff5978c319b3ee923",
    "02-sources/02-Markdown/10_CHP-10_intro.md": "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f",
    "02-sources/02-Markdown/10_CHP-10_sec_ii.md": "25542734fde53358cde0a489f1c62ff3f021f32d68be733162b406d4d8a229f9",
    "04-knowledge/tables/entity-candidates.csv": "32157b80e88e83e68ada42377e67f92838a15f7f5e956b3891ba5a6d92b77646",
    "04-knowledge/tables/s2-coverage.csv": "64cee36d44eb69b10f58518b24c86d397776dd8399fcc1b366a239fd40ec2965",
    "04-knowledge/tables/book-statements.jsonl": "b630934782614535a24f6d0dcce230cce5c7d42e08deedf1e2d8a20c5cea1db9",
}

TYPE_BY_ENTRY = {
    **{f"T.csv#{i}": "person" for i in (
        38, 42, 54, 76, 78, 79, 80, 81, 82, 87, 90, 93,
        102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
        112, 113, 115, 116, 117, 118, 119, 120, 121, 123,
    )},
    **{f"T.csv#{i}": "work" for i in (
        39, 40, 41, 43, 45, 46, 47, 48, 49, 50, 51, 52, 53,
        55, 56, 57, 58, 59, 60, 61, 62, 63, 65, 67, 68, 69,
        70, 71, 72, 73, 74, 75, 83, 84, 85, 86, 88, 89, 91,
        92, 94, 95, 96, 97, 98, 99, 100, 114, 122, 124,
    )},
    **{f"T.csv#{i}": "term" for i in (44, 66, 101, 126)},
    **{f"T.csv#{i}": "event" for i in (64, 77)},
    **{f"T.csv#{i}": "place" for i in (125, 127)},
    "UVWXYZ.csv#0": "person",
    "UVWXYZ.csv#1": "place",
    "UVWXYZ.csv#2": "person",
    "UVWXYZ.csv#3": "person",
}

PREEXISTING_TYPES = {
    "T.csv#90": "person",
    "T.csv#109": "person",
    "T.csv#111": "person",
    "UVWXYZ.csv#0": "person",
}

STATEMENT_EXPECTATIONS = {
    "st-chp9-p253-udine-fresco-sites-and-works": {
        "subject_candidate_id": "cand-2569",
        "object_candidate_id": "cand-8281",
        "predicate": "painted_staircase_ceiling_then_abraham_scenes_and_justice_of_solomon",
        "qualification": "The works are kept distinct by setting and description. The printed title 'Justice' differs from index subentry cand-2595 'Judgment'; their identity remains for S3.",
    },
    "st-chp6-p164-v1-22": {
        "subject_candidate_id": "cand-2650",
        "object_candidate_id": "cand-6548",
        "predicate": "painted_scenes_and_portraits_for_ottoboni",
    },
}

PRINT_CORRECTION_NOTES = {
    "cand-2595": "T.csv#58 transcribes 'Judgment of Solomon'; CHP-22Index.pdf physical p.29 and chapter 9 p.253 read 'Justice of Solomon'. Candidate follows print; identity with body candidate cand-8283 remains for S3.",
    "cand-2607": "T.csv#70 transcribes 'Saints Agnes, Rose and Catherine'; CHP-22Index.pdf physical p.29 and chapter 9 p.271 read 'Saints Agnes, Rosa and Catherine'. Candidate follows print.",
}

COVERAGE_NOTES = {
    MARKER_SEGMENT: (
        "no_semantic_content: S0 L3181-3182 [Page 471] and INDEX are generated navigation/header text, "
        "confirmed on CHP-22Index.pdf physical p.29; not an indexed object or factual claim."
    ),
    CONTENT_SEGMENT: (
        "no_semantic_content: index-seed classification only. CHP-22Index.pdf physical p.29 prints p.471; "
        "the segment contains T.csv#38-127 and UVWXYZ.csv#0-3 (94 entries): 35 person, 50 work, 4 term, "
        "3 place and 2 event. Broad Tiepolo patron/work contexts remain person candidates; named paintings, "
        "frescoes, drawings, prints and models are work candidates; payments and the Madrid visit are event "
        "candidates. Correct candidate cand-2595 to the printed title Justice of Solomon and cand-2607 to "
        "Saints Agnes, Rosa and Catherine; the index CSV spellings remain unchanged. Correct cand-2630's "
        "Titian locator 374 to printed 376. S0 L3241 OCR reads 1136, but the index image and chapter 10 p.296 "
        "read 1156; candidate cand-2622 retains 1156. The printed index appears to read S. Pola for Via Crucis; "
        "candidate follows T.csv and chapter 10's S. Polo. Existing statement st-chp6-p164-v1-22 is marked "
        "for S6 review; no new statement or formal relation is created."
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return raw.startswith(b"\xef\xbb\xbf"), "\r\n" if "\r\n" in text else "\n", list(csv.DictReader(io.StringIO(text, newline="")))


def write_csv(path, rows, bom, line_ending):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    payload = output.getvalue().encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def read_jsonl(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    return raw.startswith(b"\xef\xbb\xbf"), text.splitlines(keepends=True)


def write_jsonl(path, lines, bom):
    payload = "".join(lines).encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(payload)
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write the guarded migration; default is dry-run.")
    args = parser.parse_args()

    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"preflight hash mismatch: {relative}")

    source_path = ROOT / "02-sources/02-Markdown/22_CHP-22Index.md"
    segments_path = TABLES / "segments.jsonl"
    segment_rows = [json.loads(line) for line in segments_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment_by_id = {row["segment_id"]: row for row in segment_rows}
    expected_segment_hashes = {
        MARKER_SEGMENT: "1c46ec7955ddb260bff1959e135ee4be9aaef8833dd895db2cf389d1672784ad",
        CONTENT_SEGMENT: "e5d299c67539599e59652a38054940fb461536edb39071785ad9ff4aace087c6",
    }
    source_lines = source_path.read_text(encoding="utf-8-sig").splitlines()
    for segment_id, digest in expected_segment_hashes.items():
        segment = segment_by_id.get(segment_id)
        if not segment or segment["sha256"] != digest:
            raise SystemExit(f"segment manifest changed: {segment_id}")
        text = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != digest:
            raise SystemExit(f"segment source text changed: {segment_id}")

    candidate_path = TABLES / "entity-candidates.csv"
    coverage_path = TABLES / "s2-coverage.csv"
    statement_path = TABLES / "book-statements.jsonl"
    candidate_bom, candidate_eol, candidates = read_csv(candidate_path)
    coverage_bom, coverage_eol, coverage = read_csv(coverage_path)
    statement_bom, statement_lines = read_jsonl(statement_path)

    candidate_by_entry = {row["index_entry_id"]: row for row in candidates}
    if len(TYPE_BY_ENTRY) != 94 or set(TYPE_BY_ENTRY) != {
        *(f"T.csv#{i}" for i in range(38, 128)),
        *(f"UVWXYZ.csv#{i}" for i in range(4)),
    }:
        raise SystemExit("the p.471 index-entry classification map is incomplete")
    newly_typed = 0
    for entry_id, entity_type in TYPE_BY_ENTRY.items():
        candidate = candidate_by_entry.get(entry_id)
        if not candidate or candidate["status"] != "open":
            raise SystemExit(f"unexpected or missing candidate: {entry_id}")
        expected_type = PREEXISTING_TYPES.get(entry_id, "")
        if candidate["suggested_type"] != expected_type:
            raise SystemExit(f"unexpected candidate type pre-state: {entry_id}")
        if not expected_type:
            newly_typed += 1
        candidate["suggested_type"] = entity_type

    corrections = {
        "cand-2595": ("sub_entry", "Judgment of Solomon", "Justice of Solomon"),
        "cand-2607": ("sub_entry", "Saints Agnes, Rose and Catherine", "Saints Agnes, Rosa and Catherine"),
        "cand-2630": (
            "index_page_range",
            "19, 38, 39, 54, 56, 97, 114, 128, 160, 181, 184, 192, 222, 231, 241, 262, 283, 340, 348, 354, 359, 373, 374, 401",
            "19, 38, 39, 54, 56, 97, 114, 128, 160, 181, 184, 192, 222, 231, 241, 262, 283, 340, 348, 354, 359, 373, 376, 401",
        ),
    }
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for candidate_id, (field, before, after) in corrections.items():
        candidate = candidate_by_id.get(candidate_id)
        if not candidate or candidate[field] != before:
            raise SystemExit(f"unexpected candidate correction pre-state: {candidate_id}.{field}")
        candidate[field] = after
    for candidate_id, note in PRINT_CORRECTION_NOTES.items():
        candidate = candidate_by_id[candidate_id]
        if candidate["detail"]:
            raise SystemExit(f"candidate correction note field is not empty: {candidate_id}")
        candidate["detail"] = note

    coverage_by_id = {row["segment_id"]: row for row in coverage}
    for segment_id, disposition, line_range in (
        (MARKER_SEGMENT, "excluded", "L3181-3182"),
        (CONTENT_SEGMENT, "reviewed", "L3184-3292"),
    ):
        row = coverage_by_id.get(segment_id)
        if not row or (row["disposition"], row["migration_status"], row["source_line_ranges"], row["note"]) != (
            "queued", "pending", "", "",
        ):
            raise SystemExit(f"p.471 coverage is not queued/pending: {segment_id}")
        row.update({
            "disposition": disposition,
            "migration_status": "complete",
            "source_line_ranges": line_range,
            "note": COVERAGE_NOTES[segment_id],
        })

    statement_rows = {}
    rewritten_lines = []
    statement_updates = []
    for line in statement_lines:
        newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        body = line.rstrip("\r\n")
        if not body.strip():
            rewritten_lines.append(line)
            continue
        row = json.loads(body)
        statement_id = row.get("statement_id")
        if statement_id in STATEMENT_EXPECTATIONS:
            expected = STATEMENT_EXPECTATIONS[statement_id]
            if any(row.get(key) != expected[key] for key in ("subject_candidate_id", "object_candidate_id", "predicate")):
                raise SystemExit(f"statement identity changed: {statement_id}")
            qualifiers = row.setdefault("qualifiers", {})
            if statement_id == "st-chp9-p253-udine-fresco-sites-and-works":
                if qualifiers.get("qualification") != expected["qualification"]:
                    raise SystemExit(f"Justice title qualification changed: {statement_id}")
                qualifiers["qualification"] = (
                    "Chapter 9 p.253 and the index print read 'Justice of Solomon'; candidate cand-2595 now "
                    "follows the printed title. Whether it identifies the same work as body candidate cand-8283 "
                    "remains for S3 alignment."
                )
            elif statement_id == "st-chp6-p164-v1-22":
                if qualifiers.get("relation_candidate") is True:
                    raise SystemExit(f"relation candidate already marked: {statement_id}")
                qualifiers["relation_candidate"] = True
            statement_updates.append(statement_id)
            statement_rows[statement_id] = row
            rewritten_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + newline)
        else:
            rewritten_lines.append(line)
    if set(statement_rows) != set(STATEMENT_EXPECTATIONS):
        raise SystemExit("one or more expected statements are absent")

    index_counts = dict(sorted(Counter(TYPE_BY_ENTRY.values()).items()))
    summary = {
        "segments": {MARKER_SEGMENT: "excluded/complete", CONTENT_SEGMENT: "reviewed/complete"},
        "index_rows": len(TYPE_BY_ENTRY),
        "newly_typed_candidates": newly_typed,
        "classified_types": index_counts,
        "candidate_corrections": [
            {"candidate_id": key, "field": value[0], "before": value[1], "after": value[2]}
            for key, value in corrections.items()
        ],
        "relation_candidate_added": "st-chp6-p164-v1-22",
        "statement_qualification_updated": "st-chp9-p253-udine-fresco-sites-and-works",
        "mentions_or_statements_added": False,
        "formal_relations_added": False,
        "apply": args.apply,
    }

    if args.apply:
        backup_paths = [
            candidate_path.with_name(candidate_path.name + BACKUP_SUFFIX),
            coverage_path.with_name(coverage_path.name + BACKUP_SUFFIX),
            statement_path.with_name(statement_path.name + BACKUP_SUFFIX),
        ]
        if any(path.exists() for path in backup_paths):
            raise SystemExit("a backup with this task suffix already exists")
        for original, backup in zip((candidate_path, coverage_path, statement_path), backup_paths):
            shutil.copy2(original, backup)
        write_csv(candidate_path, candidates, candidate_bom, candidate_eol)
        write_csv(coverage_path, coverage, coverage_bom, coverage_eol)
        write_jsonl(statement_path, rewritten_lines, statement_bom)
        summary["backups"] = [str(path.relative_to(ROOT)) for path in backup_paths]

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
