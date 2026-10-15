from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md"
STATEMENT_ID = "st-chp7-p177-i25"
SEGMENT_ID = "chp-7:07_CHP-7_sec_i:l91-100"
SEGMENT_SHA256 = "705e5b2220b0a9362c5cafac8a5a328ab657ddc7a2dfc45370f410c1e9c5f084"
SOURCE_SHA256 = "f4deca5516d930080d5913f94c2d47593e5674e5918a0e8a6188adc1180b4ae3"
EXPECTED_TABLE_SHA256 = "6e12e6775dccad9d61d390507ee46f02a62439dc4787574c79bacaa46642e6e9"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp7-p177-event-claim-20261015")
TEMP = TABLE.with_name("book-statements.jsonl.tmp-s2-chp7-p177-event-claim-20261015")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def open_counts(rows: list[dict]) -> tuple[int, int]:
    opened = []
    for row in rows:
        q = row.get("qualifiers") or {}
        if q.get("relation_candidate") is True and (
            not row.get("subject_candidate_id") or not row.get("object_candidate_id")
        ):
            opened.append(row)
    no_reason = sum(
        not (row.get("qualifiers") or {}).get("open_endpoint_reason")
        for row in opened
    )
    return len(opened), no_reason


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Classify the 1642 breakdown statement as an event-intrinsic claim."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-table-sha256")
    args = parser.parse_args()

    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("Chapter 7 source asset changed.")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[90:100])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.177 source segment changed.")
    if "The whole precarious balance broke down in 1642" not in segment_text:
        raise ValueError("Reviewed p.177 sentence is missing.")
    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    matches = [row for row in segment_rows if row.get("segment_id") == SEGMENT_ID]
    if len(matches) != 1 or (
        matches[0].get("sha256") != SEGMENT_SHA256
        or matches[0].get("asset_sha256") != SOURCE_SHA256
    ):
        raise ValueError("Segment manifest no longer matches the reviewed source.")

    raw = TABLE.read_bytes()
    current_hash = sha(raw)
    if current_hash != EXPECTED_TABLE_SHA256:
        raise ValueError(f"Statement table changed: {current_hash}")
    text = raw.decode("utf-8-sig")
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    lines = text.splitlines(keepends=True)
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("Duplicate statement IDs in input.")
    target = by_id.get(STATEMENT_ID)
    if not target or (
        target.get("segment_id") != SEGMENT_ID
        or target.get("subject_candidate_id") != "cand-6733"
        or target.get("object_candidate_id") is not None
        or target.get("predicate") != "england_rome_balance_broke_down_in_1642"
        or target.get("original_quote") != "The whole precarious balance broke down in 1642"
        or (target.get("qualifiers") or {}).get("source_line_start") != 98
        or (target.get("qualifiers") or {}).get("source_line_end") != 98
        or (target.get("qualifiers") or {}).get("relation_candidate") is not True
        or (target.get("qualifiers") or {}).get("open_endpoint_reason")
    ):
        raise ValueError("The p.177 statement changed from its reviewed precondition.")
    if len(rows) != 15151 or open_counts(rows) != (371, 50):
        raise ValueError(
            f"Unexpected table state: rows={len(rows)}, open={open_counts(rows)}."
        )

    updated = json.loads(json.dumps(target, ensure_ascii=False))
    qualifiers = updated.setdefault("qualifiers", {})
    qualifiers["relation_candidate"] = False
    qualifiers["relation_candidate_note"] = (
        "This is Haskell's claim about the breakdown event's outcome and date. "
        "The event itself is the subject candidate; 1642 is its time, not a second "
        "entity endpoint or an entity-to-entity relation."
    )

    output_lines: list[str] = []
    replaced = 0
    for line in lines:
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        if row.get("statement_id") == STATEMENT_ID:
            output_lines.append(json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + ending)
            replaced += 1
        else:
            output_lines.append(line)
    if replaced != 1:
        raise ValueError(f"Expected one target line; found {replaced}.")
    output = (("\ufeff" if has_bom else "") + "".join(output_lines)).encode("utf-8")
    after_rows = [json.loads(line) for line in output.decode("utf-8-sig").splitlines() if line.strip()]
    if len(after_rows) != len(rows) or open_counts(after_rows) != (370, 49):
        raise ValueError(f"Unexpected post-edit state: {open_counts(after_rows)}.")

    print("reviewed=event-intrinsic claim: balance breakdown dated 1642")
    print("change=relation_candidate true->false; statement and event candidate retained")
    print("open_endpoints=371->370; no_reason_open=50->49")
    print(f"book-statements.jsonl sha256 {current_hash}->{sha(output)}")
    if args.preview:
        return 0
    if args.expected_table_sha256 != current_hash:
        raise ValueError("Apply requires --expected-table-sha256 equal to this preview's input hash.")
    if BACKUP.exists() or TEMP.exists():
        raise FileExistsError("Recovery copy or temporary output already exists.")
    shutil.copy2(TABLE, BACKUP)
    try:
        TEMP.write_bytes(output)
        TEMP.replace(TABLE)
    except Exception:
        if TEMP.exists():
            TEMP.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"applied_sha256={sha(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
