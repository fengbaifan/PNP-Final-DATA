#!/usr/bin/env python3
"""Mark nine source-bounded Exeter collector/artist statements as S2 candidates.

Default mode is a read-only dry run. --apply requires the reviewed statement
table hash and source segment hash, creates a recoverable backup, and atomically
replaces book-statements.jsonl.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
EXPECTED_STATEMENTS_SHA256 = "2b6da7dc7efa0260ae0670a26806ec94077bad874d74352f59cf825399ac3914"
SEGMENT_ID = "chp-7:07_CHP-7_sec_iv:l63-75"
EXPECTED_SEGMENT_SHA256 = "2df26f10a0058c44555f97648bc149b25cae27244fb79f608b3d1ba33a57fb27"
BACKUP_SUFFIX = ".bak-s2-handoff-exeter-collector-associations-20261010"
BASIS = (
    "The source places this named artist in Exeter's city-organized collecting account. "
    "This is a source-bounded association candidate; do not infer an individual work "
    "or transaction details beyond any explicit verb in the statement."
)

EXPECTED_ENDPOINTS = {
    "st-chp7-p197-exeter-collected-assereto-genoa": ("cand-0984", "cand-0143"),
    "st-chp7-p197-exeter-collected-brandi-rome": ("cand-0984", "cand-0446"),
    "st-chp7-p197-exeter-collected-calandrucci-rome": ("cand-0984", "cand-0481"),
    "st-chp7-p197-exeter-collected-castelli-genoa": ("cand-0984", "cand-7231"),
    "st-chp7-p197-exeter-collected-gaulli-rome": ("cand-0984", "cand-1117"),
    "st-chp7-p197-exeter-collected-liberi-venice": ("cand-0984", "cand-1401"),
    "st-chp7-p197-exeter-collected-maratta-rome": ("cand-0984", "cand-1526"),
    "st-chp7-p197-exeter-collected-pasinelli-bologna": ("cand-0984", "cand-1843"),
    "st-chp7-p197-exeter-collected-piola-genoa": ("cand-0984", "cand-1935"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed S2 marker changes")
    args = parser.parse_args()

    path = TABLES / "book-statements.jsonl"
    actual_hash = digest(path)
    if actual_hash != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit(f"statement table hash mismatch: {actual_hash}")

    source_path = ROOT / "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    segment = next(
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8").splitlines()
        if json.loads(line)["segment_id"] == SEGMENT_ID
    )
    segment_text = "\n".join(source_lines[segment["line_start"] - 1 : segment["line_end"]])
    segment_hash = hashlib.sha256(segment_text.encode("utf-8")).hexdigest()
    if segment_hash != EXPECTED_SEGMENT_SHA256 or segment["sha256"] != EXPECTED_SEGMENT_SHA256:
        raise SystemExit(f"source segment hash mismatch: {segment_hash}")

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    selected = {row["statement_id"]: row for row in rows if row.get("statement_id") in EXPECTED_ENDPOINTS}
    if set(selected) != set(EXPECTED_ENDPOINTS):
        raise SystemExit("the expected nine statement IDs are not present exactly once")
    counts = {"updated": 0, "true_after": 0, "unclassified_dual_after": 0}
    for statement_id, endpoints in EXPECTED_ENDPOINTS.items():
        row = selected[statement_id]
        q = row.get("qualifiers", {})
        if row.get("segment_id") != SEGMENT_ID or row.get("predicate") != "collector_artist_association_in_city":
            raise SystemExit(f"unexpected statement context: {statement_id}")
        if (row.get("subject_candidate_id"), row.get("object_candidate_id")) != endpoints:
            raise SystemExit(f"unexpected endpoints: {statement_id}")
        if q.get("relation_candidate") is not None:
            raise SystemExit(f"statement already classified: {statement_id}")
        start, end = q.get("source_line_start"), q.get("source_line_end")
        excerpt = "\n".join(source_lines[start - 1 : end])
        if excerpt != row.get("original_quote"):
            raise SystemExit(f"source quote mismatch: {statement_id}")
        row["qualifiers"]["relation_candidate"] = True
        row["qualifiers"]["relation_candidate_basis"] = BASIS
        counts["updated"] += 1

    for row in rows:
        q = row.get("qualifiers", {})
        if q.get("relation_candidate") is True:
            counts["true_after"] += 1
        if (
            row.get("subject_candidate_id")
            and row.get("object_candidate_id")
            and q.get("relation_candidate") is None
        ):
            counts["unclassified_dual_after"] += 1

    output = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
    report = {"mode": "apply" if args.apply else "dry-run", "segment": SEGMENT_ID, "statement_ids": list(EXPECTED_ENDPOINTS), **counts}
    if args.apply:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"backup already exists: {backup.name}")
        original = path.read_bytes()
        backup.write_bytes(original)
        with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            stream.write(output)
            temporary = Path(stream.name)
        try:
            os.replace(temporary, path)
        except Exception:
            path.write_bytes(original)
            raise
        finally:
            if temporary.exists():
                temporary.unlink()
        report["backup"] = backup.name
        report["output_sha256"] = digest(path)
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
