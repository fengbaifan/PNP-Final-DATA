from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l130-139"
SOURCE_SHA = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA = "a79d7913c72e8efa785f510fd23415563725a4e6b77bb06b533a6c1eae10fd8f"
PRE_SHA = "c90027689d5b144c7a13c8c2be60cd0dcde0df78888023ceb71729bc0f4ef899"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp3-p89-quote-split-20261011")
TARGET_ID = "st-chp3-seciv-l130-139-quoted-description-praised-device"
NEW_ID = "st-chp3-seciv-l130-139-real-dome-forecast-many-years"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_preserving(rows: list[dict], original: bytes) -> bytes:
    lines = original.splitlines(keepends=True)
    by_id = {row["statement_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("duplicate statement IDs")
    eol = b"\r\n" if b"\r\n" in original else b"\n"
    bom = original.startswith(b"\xef\xbb\xbf")
    original_ids: set[str] = set()
    output: list[bytes] = []
    for index, line in enumerate(lines):
        if not line.strip():
            output.append(line)
            continue
        old = json.loads(line.decode("utf-8-sig"))
        sid = old["statement_id"]
        if sid in original_ids:
            raise SystemExit(f"duplicate ID in JSONL: {sid}")
        original_ids.add(sid)
        current = by_id.get(sid)
        if current is None:
            raise SystemExit(f"existing statement missing: {sid}")
        if old == current:
            output.append(line)
        else:
            encoded = (json.dumps(current, ensure_ascii=False, separators=(",", ":")) + eol.decode("ascii")).encode("utf-8")
            if index == 0 and bom:
                encoded = b"\xef\xbb\xbf" + encoded
            output.append(encoded)
    new_ids = set(by_id) - original_ids
    if new_ids and output and not output[-1].endswith((b"\n", b"\r")):
        output.append(eol)
    for row in rows:
        if row["statement_id"] in new_ids:
            output.append((json.dumps(row, ensure_ascii=False, separators=(",", ":")) + eol.decode("ascii")).encode("utf-8"))
    return b"".join(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Separate the quoted dome praise from its forecast about the planned masonry dome.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source_raw = SOURCE.read_bytes()
    if sha(source_raw) != SOURCE_SHA:
        raise SystemExit("source changed; review it again")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(source_lines[129:139])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA:
        raise SystemExit("segment changed; review it again")
    phrase = "it is thought that it will be many years before they decide to build a real dome"
    if phrase not in source_lines[136]:
        raise SystemExit("forecast phrase no longer matches source line 137")
    raw = TABLE.read_bytes()
    if sha(raw) != PRE_SHA:
        raise SystemExit(f"unexpected statement hash: {sha(raw)}")
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    target = [row for row in rows if row["statement_id"] == TARGET_ID]
    if len(target) != 1 or target[0].get("segment_id") != SEGMENT_ID:
        raise SystemExit("expected quote statement is not unique in the reviewed segment")
    row = target[0]
    q = row.get("qualifiers") or {}
    if q.get("relation_candidate") is not False or "delayed for many years" not in q.get("claim", ""):
        raise SystemExit("quote statement has changed or is already split")
    if any(entry.get("statement_id") == NEW_ID for entry in rows):
        raise SystemExit("new statement ID already exists")

    row["qualifiers"]["claim"] = "Haskell quotes a description calling the canvas device very beautiful and ingenious."
    row["qualifiers"]["qualification"] = "The quoted forecast about the planned real dome is recorded separately. The source behind the quotation is unnamed and its cited sources were not independently consulted."
    row["qualifiers"]["relation_candidate_note"] = "This is an attributed aesthetic description, not a relation to an identified evaluator."
    row["original_quote"] = "his device was described as ‘very beautiful and ingenious’"
    new_row = {
        "statement_id": NEW_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-5367",
        "object_candidate_id": None,
        "predicate": "real_dome_expected_to_be_decided_on_only_after_many_years",
        "qualifiers": {
            "source_line_start": 137,
            "source_line_end": 137,
            "claim": "Haskell reports an expectation that many years would pass before a decision to build a real dome.",
            "speaker": "Unidentified source quoted by Haskell through Pastor",
            "text_layer": "nested quotation reported by Haskell",
            "print_page": 89,
            "pdf_physical_page": 31,
            "qualification": "The source does not identify who 'they' refers to; this is a reported expectation, not a confirmed delay or a statement that the dome was never built. The original quoted source is unnamed, and Pastor and a Baldinucci manuscript are cited but not independently consulted.",
            "linked_body_statement_ids": ["st-chp3-seciv-l130-139-quoted-description-praised-device", "st-chp3-seciv-l130-139-rector-wanted-dome-substitute"],
            "footnote_markers": [3],
            "footnote_source_lines": [235],
            "footnote_segment_id": "chp-3:03_CHP-3_sec_iv:l189-243",
            "footnote_pending": False,
            "footnote_statement_ids": ["st-chp3-seciv-notes-l205-243-p89-n3-pastor-baldinucci"],
            "relation_candidate": False,
            "relation_candidate_note": "This is a reported expectation about a single planned structure, with no identified decision-making actor.",
        },
        "original_quote": phrase,
        "origin": "book",
        "source_file": SOURCE.relative_to(ROOT).as_posix(),
    }
    rows.append(new_row)

    segment_rows = [entry for entry in rows if entry.get("segment_id") == SEGMENT_ID]
    relation_count = sum((entry.get("qualifiers") or {}).get("relation_candidate") is True for entry in segment_rows)
    nonrelation_count = sum((entry.get("qualifiers") or {}).get("relation_candidate") is False for entry in segment_rows)
    unclassified_count = sum((entry.get("qualifiers") or {}).get("relation_candidate") is None for entry in segment_rows)
    global_relation_count = sum((entry.get("qualifiers") or {}).get("relation_candidate") is True for entry in rows)
    if (len(rows), len(segment_rows), relation_count, nonrelation_count, unclassified_count, global_relation_count) != (12823, 44, 33, 11, 0, 5192):
        raise SystemExit("unexpected post-split totals")
    prepared = encode_preserving(rows, raw)
    print("source and segment hashes match")
    print("split quoted appraisal from forecast about the planned real dome")
    print(f"segment: {len(segment_rows)} statements; {relation_count} relation candidates; {nonrelation_count} nonrelations; {unclassified_count} unclassified")
    print(f"statements={len(rows)}; relation_candidates={global_relation_count}; statement_sha256={sha(prepared)}")
    print("unchanged JSONL rows and blank lines are preserved byte-for-byte")
    if not args.apply:
        print("DRY-RUN PASS; no files written")
        return
    if BACKUP.exists():
        raise SystemExit("recovery copy exists; refusing to overwrite")
    shutil.copy2(TABLE, BACKUP)
    temp = TABLE.with_name(TABLE.name + ".tmp-write")
    if temp.exists():
        raise SystemExit("temporary output exists; refusing to overwrite")
    try:
        temp.write_bytes(prepared)
        os.replace(temp, TABLE)
        if TABLE.read_bytes() != prepared:
            raise SystemExit("post-write byte check failed")
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print("APPLY PASS")
    print(f"post_sha256 {sha(TABLE.read_bytes())}")
    print(f"recovery_copy {BACKUP.name}")


if __name__ == "__main__":
    main()
