from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_TABLE_HASH = "c8c906d4e205e7297966f517e1f1d74a6bf07b39847c7cf5645e0af138181a9c"
SEGMENT_ID = "chp-3:03_CHP-3_sec_i:l16-24"
STATEMENT_ID = "st-chp3-seci-l16-24-orders-social-integration"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-social-integration-open-endpoint-20261015")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def open_counts(rows: list[dict]) -> tuple[int, int, int, int]:
    relations = [r for r in rows if r.get("qualifiers", {}).get("relation_candidate") is True]
    sm = sum(not r.get("subject_candidate_id") for r in relations)
    om = sum(not r.get("object_candidate_id") for r in relations)
    both = sum(not r.get("subject_candidate_id") and not r.get("object_candidate_id") for r in relations)
    return sm + om - both, om - both, sm - both, both


def build() -> bytes:
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    raw = TABLE.read_bytes()
    if sha(raw) != EXPECTED_TABLE_HASH:
        raise SystemExit("statement table hash changed")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((s for s in segments if s.get("segment_id") == SEGMENT_ID), None)
    if not segment:
        raise SystemExit("S0 segment missing")
    source = ROOT / segment["source_file"]
    if sha(source.read_bytes()) != segment.get("asset_sha256"):
        raise SystemExit("S0 source asset changed")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    row = by_id.get(STATEMENT_ID)
    if (
        len(by_id) != len(rows)
        or not row
        or row.get("segment_id") != SEGMENT_ID
        or row.get("subject_candidate_id") != "cand-2114"
        or row.get("object_candidate_id") not in (None, "")
        or row.get("qualifiers", {}).get("relation_candidate") is not True
        or "fabric of society" not in row.get("original_quote", "")
    ):
        raise SystemExit("social integration statement state changed")
    if open_counts(rows) != (507, 330, 64, 113):
        raise SystemExit(f"unexpected endpoint baseline: {open_counts(rows)}")
    row["qualifiers"]["open_endpoint_reason"] = "The passage uses 'the very fabric of society' as a broad metaphor for social integration and does not name a bounded society. Do not narrow it to Rome, the papal court, or a specific institution."
    if open_counts(rows) != (507, 330, 64, 113):
        raise SystemExit("endpoint count changed unexpectedly")
    line_ending = b"\r\n" if b"\r\n" in raw else b"\n"
    return line_ending.join(
        json.dumps(item, ensure_ascii=False, separators=(",", ":")).encode("utf-8") for item in rows
    ) + line_ending


def apply(output: bytes) -> None:
    if BACKUP.exists():
        raise SystemExit("recovery backup already exists")
    if sha(TABLE.read_bytes()) != EXPECTED_TABLE_HASH:
        raise SystemExit("statement table changed after preview")
    shutil.copy2(TABLE, BACKUP)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False) as handle:
            temp_path = Path(handle.name)
            handle.write(output)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, TABLE)
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    output = build()
    print(f"{TABLE.relative_to(ROOT)}: {EXPECTED_TABLE_HASH} -> {sha(output)}")
    print("No society endpoint is added; its scope remains unbounded in the source.")
    if args.apply:
        apply(output)
        print(f"Applied with recovery backup {BACKUP.name}.")


if __name__ == "__main__":
    main()
