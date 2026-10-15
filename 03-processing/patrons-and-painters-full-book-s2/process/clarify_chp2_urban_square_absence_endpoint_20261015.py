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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_viii.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_TABLE_HASH = "72bda4233bb3bdbb763b84abffb8cae6ee9c4ebc77aa2ae489a91dcf4d58c8f7"
SEGMENT_ID = "chp-2:02_CHP-2_sec_viii:l3-7"
STATEMENT_ID = "st-chp2-sec-viii-l3-7-no-new-squares-recall-urban"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-urban-square-absence-20261015")


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
    if sha(SOURCE.read_bytes()) != "95f938db89eb64a86bbc54065bf1e93e2d4849cd6ed5e6b02aedbe0f1e23350a":
        raise SystemExit("source asset changed")
    if not any(
        json.loads(line).get("segment_id") == SEGMENT_ID
        and json.loads(line).get("sha256") == "a371cfa6ead9f7cfc7973cb642a80e128b6e8a89422a0c02d7c813af313ca735"
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ):
        raise SystemExit("S0 segment hash mismatch")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    row = by_id.get(STATEMENT_ID)
    if (
        len(by_id) != len(rows)
        or not row
        or row.get("segment_id") != SEGMENT_ID
        or row.get("subject_candidate_id") != "cand-0209"
        or row.get("object_candidate_id") not in (None, "")
        or row.get("predicate") != "urban-memory-public-space-comparison"
        or row.get("qualifiers", {}).get("relation_candidate") is not True
        or row.get("qualifiers", {}).get("comparison_person_candidate_ids") != ["cand-1819", "cand-0665"]
    ):
        raise SystemExit("Urban VIII square-comparison statement state changed")
    if open_counts(rows) != (507, 330, 64, 113):
        raise SystemExit(f"unexpected endpoint baseline: {open_counts(rows)}")
    true_count = sum(r.get("qualifiers", {}).get("relation_candidate") is True for r in rows)
    if true_count != 10380:
        raise SystemExit(f"unexpected relation candidate count: {true_count}")

    q = row["qualifiers"]
    q["relation_candidate_note"] = "The source makes a negative public-commemoration claim about Urban VIII, contrasted with squares recalling Innocent X and Alexander VII. No Urban-associated square is named; the successors' squares are not interchangeable endpoints."
    q["open_endpoint_reason"] = "The claim concerns the absence of an identifiable new square recalling Urban VIII. No existing square is named for him, and the text does not identify the successors' squares as the object of a relation to Urban."
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
    print("Keep the negative commemoration relation open; no named Urban VIII square is supplied.")
    if args.apply:
        apply(output)
        print(f"Applied with recovery backup {BACKUP.name}.")


if __name__ == "__main__":
    main()
