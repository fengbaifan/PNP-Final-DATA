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
SOURCE = ROOT / "02-sources/02-Markdown/00_03_Preface_1st_Ed.md"
EXPECTED_SHA256 = "9289f6713a93a062c41e900c7804c41a759f80ee277ad27315abd042d417f623"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-front-matter-first-ed-preface-scope-20261010")
SEGMENT = "front-matter:00_03_Preface_1st_Ed:l3-8"

ROWS = {
    "st-fm-c1-title": {
        "predicate": "title_scope", "subject": "cand-3770", "object": "cand-2962", "line": 4,
        "anchor": "the present one is so inadequate", "relation": False,
        "note": "This is Haskell's assessment that the book title inadequately represents its scope and explains why he wrote a preface. It is an authorial observation, not a relation between the author and the work.",
    },
    "st-fm-c1-climax": {
        "predicate": "term_scope_climax", "subject": "cand-3993", "object": "cand-3104", "line": 5,
        "anchor": "reached a climax during the pontificate of Urban VIII", "relation": True,
        "note": "Haskell's definition places the Baroque phase's climax during Urban VIII's pontificate. The historical periodization remains explicitly attributed to Haskell.",
    },
    "st-fm-c1-definition": {
        "predicate": "defines_term", "subject": "cand-3770", "object": "cand-3993", "line": 5,
        "anchor": "I have termed", "relation": False,
        "note": "This records Haskell's methodological definition of the label 'Baroque'. It is a term definition, not a historical relation between the author and the period.",
    },
    "st-fm-c1-selection-scope": {
        "predicate": "selection_rationale", "subject": "cand-3770", "object": "cand-3992", "line": 5,
        "anchor": "a mere list of the art patrons and their collections", "relation": False,
        "note": "This is Haskell's explanation for rigorous selection in the book, not a relation between the author and the topical concept endpoint.",
    },
    "st-fm-c1-taste-quality": {
        "predicate": "patronage_method", "subject": "cand-3770", "object": "cand-3992", "line": 5,
        "anchor": "the intrinsic interest of their personalities and tastes", "relation": False,
        "note": "This states Haskell's methodological comparison between patron interest/taste and the quality of commissioned art. It is an argument about selection criteria, not a formal relation between these endpoints.",
    },
    "st-fm-c1-venice-republic": {
        "predicate": "term_scope_duration", "subject": "cand-3993", "object": "cand-3401", "line": 5,
        "anchor": "lingered on in Venice until the downfall of the Republic", "relation": True,
        "note": "Haskell's periodization says the Baroque phase lingered in Venice until the Republic fell. The geographic and temporal limits remain attributed to this preface.",
    },
    "st-fm-c1-first-section": {
        "predicate": "book_section_scope", "subject": "cand-2962", "object": "cand-3126", "line": 7,
        "anchor": "The first section of the book deals entirely with Rome", "relation": True,
        "note": "The preface explicitly identifies Rome as the subject of the book's first section. The accompanying Urban VIII time and taste context remains a section-specific qualifier.",
    },
    "st-fm-c1-leaves-rome": {
        "predicate": "authorial_scope_choice", "subject": "cand-3770", "object": "cand-3126", "line": 7,
        "anchor": "I then leave the city altogether, never to return", "relation": False,
        "note": "This is Haskell's narrative and scope decision after the chapter on Rome's decline, not a direct relation between the author and Rome.",
    },
    "st-fm-c1-omit-eighteenth-rome": {
        "predicate": "authorial_scope_choice", "subject": "cand-3770", "object": "cand-3126", "line": 7,
        "anchor": "decision to neglect eighteenth-century Rome", "relation": False,
        "note": "This records Haskell's reason for excluding eighteenth-century Rome from the book. It is an authorial scope decision, not a historical relation to Rome.",
    },
    "st-fm-c1-inherited-international": {
        "predicate": "historical_interpretation", "subject": "cand-3770", "object": "cand-3992", "line": 8,
        "anchor": "inherited what had been the most fruitful elements in Roman patronage", "relation": False,
        "note": "This is Haskell's interpretation that the discussed groups inherited aspects of Roman patronage. The current endpoints are the reporting author and a patronage concept, so this row does not express the interpreted groups' relation directly.",
    },
    "st-fm-c1-middle-vacuum": {
        "predicate": "book_section_scope", "subject": "cand-2962", "object": "cand-3126", "line": 8,
        "anchor": "The whole of the middle section deals with the vacuum that resulted from the decline of Rome", "relation": True,
        "note": "The preface explicitly identifies Rome's decline and its resulting vacuum as the subject of the book's middle section. The section scope remains attributed to Haskell.",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    actual_sha = sha256(raw)
    if actual_sha != EXPECTED_SHA256:
        raise SystemExit(f"input SHA mismatch: expected {EXPECTED_SHA256}, got {actual_sha}")

    with CANDIDATES.open(encoding="utf-8-sig", newline="") as f:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(f)}
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")

    for sid, spec in ROWS.items():
        row = by_id.get(sid)
        if row is None:
            raise SystemExit(f"missing statement: {sid}")
        q = row.get("qualifiers") or {}
        if (row.get("segment_id") != SEGMENT or row.get("source_file") != "02-sources/02-Markdown/00_03_Preface_1st_Ed.md"
                or row.get("origin") != "book" or row.get("predicate") != spec["predicate"]
                or row.get("subject_candidate_id") != spec["subject"] or row.get("object_candidate_id") != spec["object"]
                or q.get("source_line_start") != spec["line"] or q.get("source_line_end") != spec["line"]
                or q.get("speaker") != "Haskell" or q.get("relation_candidate") is not None):
            raise SystemExit(f"statement preflight mismatch: {sid}")
        if spec["line"] > len(source_lines) or spec["anchor"] not in source_lines[spec["line"] - 1]:
            raise SystemExit(f"source anchor mismatch: {sid}")
        for endpoint in (spec["subject"], spec["object"]):
            if endpoint not in candidate_ids:
                raise SystemExit(f"missing candidate endpoint {endpoint}: {sid}")

    updated = {}
    for sid, spec in ROWS.items():
        row = deepcopy(by_id[sid])
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = spec["relation"]
        q["relation_candidate_note"] = spec["note"]
        updated[sid] = row

    output, seen = [], set()
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        sid = row["statement_id"]
        if sid in updated:
            output.append(json.dumps(updated[sid], ensure_ascii=False, separators=(",", ":")))
            seen.add(sid)
        else:
            output.append(line)
    if seen != set(ROWS):
        raise SystemExit("write coverage mismatch")
    result = ("\n".join(output) + "\n").encode("utf-8")
    print(f"preflight passed: {len(seen)}/{len(ROWS)} statements; endpoints, author attribution, source lines and anchors verified; input_sha256={actual_sha}")
    print("classification: 4 relation candidates, 7 non-relational statements; no candidates, mentions or statements added")
    if not args.apply:
        print("dry-run only; table unchanged")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    fd, temp_name = tempfile.mkstemp(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(result)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_name, TABLE)
    except Exception:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise
    print(f"applied: backup={BACKUP.relative_to(ROOT)} output_sha256={sha256(result)}")


if __name__ == "__main__":
    main()
