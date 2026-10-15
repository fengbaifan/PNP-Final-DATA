from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
CANDIDATES = ROOT / "04-knowledge/tables/entity-candidates.csv"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
COVERAGE = ROOT / "04-knowledge/tables/s2-coverage.csv"
SOURCE = ROOT / "02-sources/02-Markdown/00_03_Preface_1st_Ed.md"
EXPECTED_SHA256 = "d6a03e97f88f43139db93d9064bd8c8dcab4cf1c124f8219abab71b6f2ec19d9"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-front-matter-first-ed-preface-method-20261010")
SEGMENT = "front-matter:00_03_Preface_1st_Ed:l10-17"

ROWS = {
    "st-fm-c2-inherited-nondogmatic": {
        "predicate": "historical_interpretation",
        "subject": "cand-3770",
        "object": "cand-3992",
        "line_start": 11,
        "line_end": 11,
        "anchors": {11: "refusal to be bound by dogmatic principles"},
        "relation": False,
        "note": "This is Haskell's interpretation of the unnamed patron groups' inheritance from Roman patronage. The recorded endpoints are Haskell and the art-patronage concept, so this statement does not express a direct relation between those endpoints; preserve it as an attributed historical interpretation.",
    },
    "st-fm-c2-neapolitan-style": {
        "predicate": "historical_interpretation",
        "subject": "cand-3994",
        "object": "cand-3401",
        "line_start": 11,
        "line_end": 12,
        "anchors": {11: "appreciation of Neapolitan", 12: "which spread from Venice to many parts of Europe"},
        "relation": False,
        "note": "Retain Haskell's causal interpretation that the patron groups' reaction and appreciation prepared a Baroque resurgence, and his statement that it spread from Venice. This composite claim does not state a direct relation between the current endpoints (Neapolitan painting and Venice); do not promote this endpoint pair as a relation. Revisit statement granularity if the handoff audit separates the group-level cause from the Baroque movement's spread.",
    },
    "st-fm-c2-no-reduction": {
        "predicate": "methodological_position",
        "subject": "cand-3770",
        "object": "cand-3992",
        "line_start": 14,
        "line_end": 14,
        "anchors": {14: "Any attempt to ‘explain’ art in terms of patronage has been deliberately avoided."},
        "relation": False,
        "note": "This records Haskell's methodological choice, not a historical relation between Haskell and the topical concept of art patronage. It does not deny the art-society connections discussed elsewhere in the preface.",
    },
    "st-fm-c2-empirical-method": {
        "predicate": "authorial_method",
        "subject": "cand-4133",
        "object": "cand-3770",
        "line_start": 15,
        "line_end": 16,
        "anchors": {15: "tried to be severely empirical", 16: "general knowledge of an artist’s style"},
        "relation": False,
        "note": "This is Haskell's self-description of research method and limits. The method-to-author attribution is claim context, not a formal historical relation candidate in this S2 table.",
    },
    "st-fm-c2-enzo": {
        "predicate": "illustration_assistance",
        "subject": "cand-3770",
        "object": "cand-3758",
        "new_subject": "cand-3758",
        "new_object": "cand-3770",
        "line_start": 17,
        "line_end": 17,
        "anchors": {17: "helping me to organise this side of the book"},
        "relation": True,
        "claim": "Enzo Crea helped Haskell organize the book's illustrations; Haskell also calls Crea a friend.",
        "note": "The source directly reports Crea's assistance to Haskell with arranging the book's illustrations and identifies Crea as Haskell's friend. Orient the assistance provider as subject and recipient as object; this remains an S2 candidate, not an S6 formal edge.",
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify unresolved first-edition preface statements at lines 10-17.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    actual_sha = digest(raw)
    if actual_sha != EXPECTED_SHA256:
        raise SystemExit(f"input SHA mismatch: expected {EXPECTED_SHA256}, got {actual_sha}")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    candidate_rows = {row["candidate_id"]: row for row in read_csv(CANDIDATES)}
    candidate_ids = set(candidate_rows)
    mentions = read_csv(MENTIONS)
    coverage = read_csv(COVERAGE)
    coverage_row = next((row for row in coverage if row["segment_id"] == SEGMENT), None)
    if not coverage_row or (coverage_row["disposition"], coverage_row["migration_status"]) != ("reviewed", "complete"):
        raise SystemExit("segment coverage is not reviewed/complete")
    if not any(row["segment_id"] == SEGMENT and row["candidate_id"] == "cand-3758" for row in mentions):
        raise SystemExit("Enzo Crea mention is missing from the segment")
    if candidate_rows.get("cand-3758", {}).get("suggested_type") != "person":
        raise SystemExit("Enzo Crea candidate preflight failed")
    if candidate_rows.get("cand-3770", {}).get("suggested_type") != "person":
        raise SystemExit("Haskell candidate preflight failed")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    for statement_id, spec in ROWS.items():
        row = by_id.get(statement_id)
        if row is None:
            raise SystemExit(f"missing statement: {statement_id}")
        q = row.get("qualifiers") or {}
        if (
            row.get("segment_id") != SEGMENT
            or row.get("source_file") != "02-sources/02-Markdown/00_03_Preface_1st_Ed.md"
            or row.get("origin") != "book"
            or row.get("predicate") != spec["predicate"]
            or row.get("subject_candidate_id") != spec["subject"]
            or row.get("object_candidate_id") != spec["object"]
            or q.get("source_line_start") != spec["line_start"]
            or q.get("source_line_end") != spec["line_end"]
            or q.get("speaker") != "Haskell"
            or "relation_candidate" in q
        ):
            raise SystemExit(f"statement preflight mismatch: {statement_id}")
        for line_number, anchor in spec["anchors"].items():
            if line_number > len(source_lines) or anchor not in source_lines[line_number - 1]:
                raise SystemExit(f"source anchor mismatch: {statement_id} line {line_number}")
        for endpoint in (spec["subject"], spec["object"]):
            if endpoint and endpoint not in candidate_ids:
                raise SystemExit(f"missing candidate endpoint {endpoint}: {statement_id}")

    updated = {}
    for statement_id, spec in ROWS.items():
        row = deepcopy(by_id[statement_id])
        if "new_subject" in spec:
            row["subject_candidate_id"] = spec["new_subject"]
            row["object_candidate_id"] = spec["new_object"]
        if "claim" in spec:
            row["qualifiers"]["claim"] = spec["claim"]
        row["qualifiers"]["relation_candidate"] = spec["relation"]
        row["qualifiers"]["relation_candidate_note"] = spec["note"]
        updated[statement_id] = row

    output = []
    seen = set()
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        statement_id = row["statement_id"]
        if statement_id in updated:
            output.append(json.dumps(updated[statement_id], ensure_ascii=False, separators=(",", ":")))
            seen.add(statement_id)
        else:
            output.append(line)
    if seen != set(ROWS):
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output) + "\n").encode("utf-8")
    print(f"preflight passed: {len(seen)}/{len(ROWS)} statements; candidate endpoints, speaker, coverage and source anchors verified")
    print("classification: 1 relation candidate, 4 non-relational statements; Crea-to-Haskell assistance direction corrected")
    for statement_id, spec in ROWS.items():
        row = by_id[statement_id]
        subject = spec.get("new_subject", spec["subject"])
        obj = spec.get("new_object", spec["object"])
        print(
            f"review {statement_id}: relation_candidate absent -> {str(spec['relation']).lower()}; "
            f"endpoints {row.get('subject_candidate_id')} -> {row.get('object_candidate_id')} "
            f"to {subject} -> {obj}"
        )
        print(f"  rationale: {spec['note']}")
    if not args.apply:
        print(f"dry-run only; table unchanged; input_sha256={actual_sha}")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={digest(result)}")


if __name__ == "__main__":
    main()
