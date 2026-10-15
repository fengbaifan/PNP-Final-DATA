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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_vii.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_TABLE_HASH = "de12e0ce9c16a0fcbda308a6543498d40eb13eaf0d533f12db8a411b212e9414"
SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l38-54"
STATEMENT_ID = "st-chp2-secvii-l38-54-fn-p60-7b-ferri-attribution-suggested"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-ferri-attribution-scope-20261015")


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
    if not any(
        json.loads(line).get("segment_id") == SEGMENT_ID
        and json.loads(line).get("sha256") == "e158059bf39e132e67c04028d3dc23c4f6f3bda83e9648b8c5dceabe09522409"
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ):
        raise SystemExit("S0 segment hash mismatch")
    if sha(SOURCE.read_bytes()) != "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c":
        raise SystemExit("source asset changed")

    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    row = by_id.get(STATEMENT_ID)
    if (
        len(by_id) != len(rows)
        or not row
        or row.get("segment_id") != SEGMENT_ID
        or row.get("subject_candidate_id") not in (None, "")
        or row.get("object_candidate_id") != "cand-1027"
        or row.get("qualifiers", {}).get("relation_candidate") is not True
        or row.get("qualifiers", {}).get("possible_subject_candidate_ids") != ["cand-4935", "cand-4936"]
        or row.get("qualifiers", {}).get("citation_statement_id") != "st-chp2-secvii-l38-54-fn-p60-7b-blunt-cooke-citation"
    ):
        raise SystemExit("Ciro Ferri attribution state changed")
    if open_counts(rows) != (507, 330, 64, 113):
        raise SystemExit(f"unexpected endpoint baseline: {open_counts(rows)}")
    count_true = sum(r.get("qualifiers", {}).get("relation_candidate") is True for r in rows)
    if count_true != 10380:
        raise SystemExit(f"unexpected relation candidate count: {count_true}")

    q = row["qualifiers"]
    q["relation_candidate_note"] = "Blunt and Cooke are named as the source of the tentative attribution to Ciro Ferri; the attribution's work subject remains unresolved between the tapestry set and its preparatory cartoons. The publication is evidence, not the work endpoint."
    q["open_endpoint_reason"] = "The footnote does not make clear whether Ciro Ferri is suggested as artist of the finished tapestry set cand-4935 or of the cartoons/designs cand-4936. Preserve both possible subjects without selecting one."
    if open_counts(rows) != (507, 330, 64, 113):
        raise SystemExit("endpoint counts changed unexpectedly")
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
    print("No endpoint is assigned; the open reason now distinguishes the tapestry set from its preparatory cartoons.")
    if args.apply:
        apply(output)
        print(f"Applied with recovery backup {BACKUP.name}.")


if __name__ == "__main__":
    main()
