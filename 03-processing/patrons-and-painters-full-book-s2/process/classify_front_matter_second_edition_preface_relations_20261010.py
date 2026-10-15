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
SOURCE = ROOT / "02-sources/02-Markdown/00_02_Preface_2nd_Ed.md"
EXPECTED_SHA256 = "7ce9a416dbdfb05bd7d8a338296dc4df6a7930882ab6bc0751315ddf9933ca4e"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-front-matter-second-ed-preface-relations-20261010")
SEGMENTS = {
    "front-matter:00_02_Preface_2nd_Ed:l3-8",
    "front-matter:00_02_Preface_2nd_Ed:l10-17",
}

ROWS = {
    "st-fm-b2-dbi": {
        "predicate": "recommends_reference", "subject": "cand-3770", "object": "cand-3599",
        "start": 5, "end": 6, "anchor": "Dizionario biografico degli Italiani", "relation": True,
        "note": "Haskell assumes readers interested in the figures will use this biographical reference. This records the preface's recommendation, not independent consultation of the reference.",
    },
    "st-fm-b2-chatto": {
        "predicate": "publication_support", "subject": "cand-3770", "object": "cand-3631",
        "start": 11, "end": 12, "anchor": "directors of Chatto and Windus", "relation": True,
        "note": "Haskell thanks the directors of Chatto and Windus for support and encouragement while working together on the first edition; the relation is limited to this acknowledgment.",
    },
    "st-fm-b2-norah": {
        "predicate": "acknowledged_support", "subject": "cand-3770", "object": "cand-3849",
        "start": 11, "end": 12, "anchor": "Mrs Norah Smallwood", "relation": True,
        "note": "Haskell especially acknowledges Norah Smallwood's support and encouragement in the first-edition work; no broader employment role is inferred.",
    },
    "st-fm-b2-nicoll": {
        "predicate": "edition_proposal_and_assistance", "subject": "cand-3770", "object": "cand-3815",
        "start": 12, "end": 12, "anchor": "John Nicoll for proposing a new edition", "relation": True,
        "note": "Haskell thanks John Nicoll for proposing the new edition and helping with it; this records the explicit acknowledgment only.",
    },
    "st-fm-b2-munby": {
        "predicate": "friendship_and_advice", "subject": "cand-3770", "object": "cand-3708",
        "start": 14, "end": 15, "anchor": "Tim Munby and Ben Nicolson, two very close friends", "relation": True,
        "note": "Haskell calls Tim Munby a close friend and says he often sought his advice while writing the book. The source attribution and writing context are retained.",
    },
    "st-fm-b2-nicolson": {
        "predicate": "friendship_and_advice", "subject": "cand-3770", "object": "cand-3732",
        "start": 14, "end": 15, "anchor": "Tim Munby and Ben Nicolson, two very close friends", "relation": True,
        "note": "Haskell calls Ben Nicolson a close friend and says he often sought his advice while writing the book. The source attribution and writing context are retained.",
    },
    "st-fm-b2-munbydeath": {
        "predicate": "reports_death_of", "subject": "cand-3770", "object": "cand-3708",
        "start": 14, "end": 15, "anchor": "the deaths of Tim Munby and Ben Nicolson", "relation": False,
        "note": "This row records the preface author's report that Munby had died, with Haskell as reporter and Munby as subject. It is not a direct relation between those endpoints; the friendship/advice relation is recorded separately.",
    },
    "st-fm-b2-nicolsondeath": {
        "predicate": "reports_death_of", "subject": "cand-3770", "object": "cand-3732",
        "start": 14, "end": 15, "anchor": "the deaths of Tim Munby and Ben Nicolson", "relation": False,
        "note": "This row records the preface author's report that Nicolson had died, with Haskell as reporter and Nicolson as subject. It is not a direct relation between those endpoints; the friendship/advice relation is recorded separately.",
    },
    "st-fm-b2-signature": {
        "predicate": "preface_signature", "subject": "cand-2962", "object": "cand-3943",
        "start": 16, "end": 17, "anchor": "Oxford,", "relation": True,
        "note": "The preface dateline gives Oxford and November 1979. This records the printed dateline only and does not independently verify the place of composition.",
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
    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        mention_pairs = {(row["segment_id"], row["candidate_id"]) for row in csv.DictReader(f)}
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
        segment = row.get("segment_id")
        if segment not in SEGMENTS or row.get("source_file") != "02-sources/02-Markdown/00_02_Preface_2nd_Ed.md" or row.get("origin") != "book":
            raise SystemExit(f"source provenance mismatch: {sid}")
        if (row.get("predicate") != spec["predicate"] or row.get("subject_candidate_id") != spec["subject"]
                or row.get("object_candidate_id") != spec["object"] or q.get("source_line_start") != spec["start"]
                or q.get("source_line_end") != spec["end"] or q.get("speaker") != "Haskell"
                or q.get("relation_candidate") is not None):
            raise SystemExit(f"statement preflight mismatch: {sid}")
        if spec["end"] > len(source_lines) or spec["anchor"] not in " ".join(source_lines[spec["start"] - 1:spec["end"]]):
            raise SystemExit(f"source anchor mismatch: {sid}")
        for endpoint in (spec["subject"], spec["object"]):
            if endpoint not in candidate_ids:
                raise SystemExit(f"missing candidate endpoint {endpoint}: {sid}")
        if (segment, spec["object"]) not in mention_pairs:
            raise SystemExit(f"object mention missing: {sid}")
        if spec["subject"] == "cand-3770" and q.get("speaker") != "Haskell":
            raise SystemExit(f"implicit first-person subject lacks author attribution: {sid}")

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
    print(f"preflight passed: {len(seen)}/{len(ROWS)} statements; author attribution, object mentions and source anchors verified; input_sha256={actual_sha}")
    print("classification: 7 relation candidates, 2 non-relational reports; no candidates or mentions added")
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
