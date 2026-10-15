from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
SEGMENTS = TABLES / "segments.jsonl"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENT_ID = "chp-8:08_CHP-8_sec_ii:l112-124"
SEGMENT_SHA256 = "d2da0e390237cbab6a9b1ca7e8c3cf52be8034c1aff7a35369072ccf12bf88f4"
SEGMENT_ASSET_SHA256 = "5d9a17efc3835c30947b8c714c65649be10295661b6cca6b117f5902882bcef6"
PDF_SHA256 = "cb11451ac726f37ed5badf21a569af88f790f858f1c39eb63f2efb58a0fe4ac3"
STATEMENT_ID = "st-chp8-p221-abraham-picture-approved"
EXPECTED_STATEMENTS_SHA256 = "c6189a455a3c9469246c610fdcd67ebf63a9aac11670712663b9908b153a3fa1"
BACKUP_SUFFIX = ".bak-s2-chp8-p221-approval-open-reason-20261015"
TEMP_SUFFIX = ".tmp-s2-chp8-p221-approval-open-reason-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def rows(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record why the p.221 approval statement has no identified approver.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    args = parser.parse_args()
    pdf = ROOT / "02-sources/01-book/CHP-8.pdf"
    if sha(pdf.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-8.pdf changed.")
    segment_matches = [r for r in rows(SEGMENTS.read_bytes()) if r.get("segment_id") == SEGMENT_ID]
    if len(segment_matches) != 1:
        raise ValueError("Reviewed p.221 source segment is missing or duplicated.")
    segment = segment_matches[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SEGMENT_ASSET_SHA256:
        raise ValueError("Reviewed p.221 segment metadata changed.")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.221 transcription changed.")
    if "and met with approval. It was arranged that Melanconici" not in source_text:
        raise ValueError("The approval and following passive clause changed.")

    raw = STATEMENTS.read_bytes()
    input_hash = sha(raw)
    if input_hash != EXPECTED_STATEMENTS_SHA256:
        raise ValueError(f"Protected statement snapshot changed: {input_hash}")
    statements = rows(raw)
    if len(statements) != 15158:
        raise ValueError("Unexpected statement inventory.")
    matches = [r for r in statements if r.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise ValueError("Target statement is missing or duplicated.")
    updated = json.loads(json.dumps(matches[0], ensure_ascii=False))
    q = updated.get("qualifiers") or {}
    if (
        updated.get("segment_id") != SEGMENT_ID
        or updated.get("subject_candidate_id") != "cand-1637"
        or updated.get("object_candidate_id")
        or q.get("relation_candidate") is not True
        or q.get("open_endpoint_reason")
        or updated.get("original_quote") != "and met with approval"
    ):
        raise ValueError("Reviewed statement no longer matches its expected state.")
    q["claim"] = "Haskell reports that the experimental Abraham picture met with approval."
    q["qualification"] = "The approver is not named; the following passive 'It was arranged' does not identify the acting body."
    q["relation_candidate_note"] = "The source reports an approval reaction to the painting, but no approving person or body is identified."
    q["open_endpoint_reason"] = "The p.220-221 passage says the picture 'met with approval' and then uses the passive 'It was arranged'; it does not name who approved it. The following retrospective refers generally to the Governors of S. Maria Maggiore but does not assign this specific approval to either those governors or the earlier committee. Keep the approver endpoint open."
    updated["qualifiers"] = q

    bom = raw.startswith(b"\xef\xbb\xbf")
    out: list[str] = []
    seen = 0
    for line in raw.decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        if row.get("statement_id") == STATEMENT_ID:
            out.append(json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + ending)
            seen += 1
        else:
            out.append(line)
    if seen != 1:
        raise ValueError("Target statement did not occur exactly once.")
    rewritten = (("\ufeff" if bom else "") + "".join(out)).encode("utf-8")
    after = rows(rewritten)
    open_rows = [
        r for r in after
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    ]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 360 or no_reason != 37:
        raise ValueError(f"Unexpected post-edit state: open={len(open_rows)}, no_reason={no_reason}")
    print("reviewed=CHP-8 p.221 / PDF physical page 23 and preceding p.220 narrative")
    print("change=retain subject cand-1637; record unresolved approver without inferring committee or governors")
    print("open_endpoints=360 (unchanged); no_reason_open=38->37")
    print(f"book-statements.jsonl sha256 {input_hash}->{sha(rewritten)}")
    if args.preview:
        return 0
    if args.expected_statements_sha256 != input_hash:
        raise ValueError("Apply requires the input hash printed by this preview.")
    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    temp = STATEMENTS.with_name(STATEMENTS.name + TEMP_SUFFIX)
    if backup.exists() or temp.exists():
        raise FileExistsError("Recovery copy or temporary table already exists.")
    shutil.copy2(STATEMENTS, backup)
    try:
        temp.write_bytes(rewritten)
        temp.replace(STATEMENTS)
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(backup, STATEMENTS)
        raise
    print("applied=yes")
    print(f"backup={backup.relative_to(ROOT)}")
    print(f"applied_sha256={sha(STATEMENTS.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
