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
SOURCE = ROOT / "02-sources/02-Markdown/08_CHP-8_sec_i.md"
PRIOR_REVIEW = ROOT / (
    "03-processing/patrons-and-painters-full-book-s2/process/"
    "classify_chp8_p204_p213_footnote_relation_candidates_20261014.py"
)
STATEMENT_ID = "st-chp8-p212-n5-archivio-letter-content"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l126-157"
SEGMENT_SHA256 = "0ecf16986f97d6044129c91ccafde31ac1ebe6dadef71c79a6d4691c10d90b4c"
SOURCE_SHA256 = "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf"
EXPECTED_TABLE_SHA256 = "811603cdf2188fe3c4237966f962c5644d44048a2daf0e2ceb5296d27e7ad238"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp8-p212-n5-open-reason-20261015")
TEMP = TABLE.with_name("book-statements.jsonl.tmp-s2-chp8-p212-n5-open-reason-20261015")


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
    return len(opened), sum(
        not (row.get("qualifiers") or {}).get("open_endpoint_reason")
        for row in opened
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-table-sha256")
    args = parser.parse_args()

    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise ValueError("Chapter 8 source asset changed.")
    segment_text = "\n".join(SOURCE.read_text(encoding="utf-8").splitlines()[125:157])
    if sha(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.212-p.214 segment changed.")
    if (
        "dated 2 April 1686" not in segment_text
        or "Sig.r V.Re diretta al Pittore Giordani" not in segment_text
        or "da me" not in segment_text
    ):
        raise ValueError("The reviewed letter date, inner correspondence, or first-person wording is missing.")
    segments = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    matches = [row for row in segments if row.get("segment_id") == SEGMENT_ID]
    if len(matches) != 1 or (
        matches[0].get("sha256") != SEGMENT_SHA256
        or matches[0].get("asset_sha256") != SOURCE_SHA256
    ):
        raise ValueError("Segment manifest no longer matches the reviewed source.")
    prior = PRIOR_REVIEW.read_text(encoding="utf-8")
    if (
        "sender and Viceroy remain unidentified" not in prior
        or STATEMENT_ID not in prior
    ):
        raise ValueError("The earlier semantic decision about the unidentified actors changed.")

    raw = TABLE.read_bytes()
    current_hash = sha(raw)
    if current_hash != EXPECTED_TABLE_SHA256:
        raise ValueError(f"Statement table changed: {current_hash}")
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    by_id = {row.get("statement_id"): row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("Duplicate statement IDs in input.")
    target = by_id.get(STATEMENT_ID)
    if not target or (
        target.get("segment_id") != SEGMENT_ID
        or target.get("subject_candidate_id") is not None
        or target.get("object_candidate_id") != "cand-7613"
        or target.get("predicate") != "archival_letter_reports_viceroy_letter_forwarded_to_giordani"
        or target.get("qualifiers", {}).get("source_line_start") != 153
        or target.get("qualifiers", {}).get("source_line_end") != 153
        or target.get("qualifiers", {}).get("relation_candidate") is not True
        or target.get("qualifiers", {}).get("open_endpoint_reason")
    ):
        raise ValueError("The p.212 letter-content statement changed from its reviewed precondition.")
    if (
        len(rows) != 15151
        or open_counts(rows) != (368, 47)
        or "writer" not in target.get("qualifiers", {}).get("qualification", "")
    ):
        raise ValueError(f"Unexpected table state: rows={len(rows)}, open={open_counts(rows)}.")

    updated = json.loads(json.dumps(target, ensure_ascii=False))
    q = updated.setdefault("qualifiers", {})
    q["open_endpoint_reason"] = (
        "The statement is a report-level summary of an archival letter's nested correspondence. "
        "Haskell identifies neither the outer letter's writer nor the Viceroy behind the inner "
        "letter to Giordani, and the archival original/file was not independently consulted. "
        "Keep the missing subject open; do not infer either person's identity from the date, "
        "recipient, or surrounding narrative."
    )

    lines = text.splitlines(keepends=True)
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
    if len(after_rows) != len(rows) or open_counts(after_rows) != (368, 46):
        raise ValueError(f"Unexpected post-edit state: rows={len(after_rows)}, open={open_counts(after_rows)}.")

    print("reviewed=p.212 n.5 nested correspondence; sender and Viceroy remain unidentified")
    print("change=recorded a source-grounded reason for leaving the subject endpoint open")
    print("open_endpoints=368 (unchanged); no_reason_open=47->46")
    print(f"book-statements.jsonl sha256 {current_hash}->{sha(output)}")
    if args.preview:
        return 0
    if args.expected_table_sha256 != current_hash:
        raise ValueError("Apply requires --expected-table-sha256 equal to this preview's input hash.")
    if BACKUP.exists() or TEMP.exists():
        raise FileExistsError("Recovery copy or temporary file already exists.")
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
