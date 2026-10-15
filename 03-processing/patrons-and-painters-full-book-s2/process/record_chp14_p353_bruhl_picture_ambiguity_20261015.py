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
PDF = ROOT / "02-sources/01-book/CHP-14.pdf"
PDF_SHA256 = "f871a00a63cfa5a9f229930cfd4b0d979baa0491ca4e7fe4d50404fa020a52e0"
SEGMENT_ID = "chp-14:14_CHP-14_intro:l63-71"
SEGMENT_SHA256 = "def09441a0768efe65289db46f287add59632f45c8d99f53b3973b75696dc44d"
ASSET_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
STATEMENT_ID = "st-chp14-p353-bruhl-possessions-in-the-pictures"
CONTINUATION_ID = "st-chp14-p354-banquet-classicism-and-accuracy"
OPEN_REASON = (
    "Haskell says Tiepolo put Brühl's two named possessions into 'the picture' after identifying two commissioned paintings for Brühl (cand-2597 and cand-2590). The p.354 continuation refers to 'the two scenes' and does not identify which painting contains either motif. Keep the work endpoint open; do not choose one picture or assign the motifs one-to-one."
)
EXPECTED_HASHES = {
    "statements": "a354e03d27867fb45ed1519b8b65000c0e192ea38b57dd46464bdc5b2db4f8f3",
    "mentions": "9ed666c4eafce131efd41c489b29d8a0214ba6669fc2a21c202a6db28133d3c7",
    "candidates": "0f990b0e9fba758ccfeeed84ef0e7336e21716d18cce35eec70bbb1fcf63dbc4",
}
BACKUP_SUFFIX = ".bak-s2-chp14-p353-bruhl-picture-ambiguity-20261015"
TEMP_SUFFIX = ".tmp-s2-chp14-p353-bruhl-picture-ambiguity-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record why the p.353 Brühl motif statement keeps its picture endpoint open.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    if sha(PDF.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-14.pdf changed.")
    segment_rows = read_jsonl(SEGMENTS.read_bytes())
    segment_matches = [r for r in segment_rows if r.get("segment_id") == SEGMENT_ID]
    if len(segment_matches) != 1:
        raise ValueError("The reviewed p.353 segment is missing or duplicated.")
    segment = segment_matches[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != ASSET_SHA256:
        raise ValueError("Reviewed p.353 segment metadata changed.")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source_text.encode("utf-8")) != SEGMENT_SHA256 or source_text.count("making Tiepolo insert into the picture") != 1:
        raise ValueError("Reviewed p.353 source text changed.")

    actual = {
        "statements": sha(STATEMENTS.read_bytes()),
        "mentions": sha((TABLES / "mentions.csv").read_bytes()),
        "candidates": sha((TABLES / "entity-candidates.csv").read_bytes()),
    }
    if actual != EXPECTED_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual}")
    raw = STATEMENTS.read_bytes()
    statements = read_jsonl(raw)
    if len(statements) != 15158:
        raise ValueError("Unexpected statement inventory.")
    by_id = {r["statement_id"]: r for r in statements}
    if len(by_id) != len(statements):
        raise ValueError("Duplicate statement IDs.")
    target = by_id.get(STATEMENT_ID)
    continuation = by_id.get(CONTINUATION_ID)
    if not target or not continuation:
        raise ValueError("The p.353 statement or its p.354 continuation is missing.")
    updated = json.loads(json.dumps(target, ensure_ascii=False))
    q = updated.get("qualifiers") or {}
    if (
        updated.get("segment_id") != SEGMENT_ID
        or updated.get("subject_candidate_id") != "cand-2572"
        or updated.get("object_candidate_id")
        or q.get("relation_candidate") is not True
        or q.get("open_endpoint_reason")
        or CONTINUATION_ID not in q.get("cross_reference_statement_ids", [])
        or STATEMENT_ID not in continuation.get("qualifiers", {}).get("cross_reference_statement_ids", [])
    ):
        raise ValueError("The target no longer matches the reviewed ambiguity state.")
    target_candidate_ids = {item.get("candidate_id") for item in q.get("candidate_identity_questions", [])}
    if target_candidate_ids != {"cand-2597", "cand-2590"}:
        raise ValueError(f"Unexpected competing painting candidates: {target_candidate_ids}")
    q["open_endpoint_reason"] = OPEN_REASON
    updated["qualifiers"] = q

    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[str] = []
    seen = 0
    for line in raw.decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        if row.get("statement_id") == STATEMENT_ID:
            output.append(json.dumps(updated, ensure_ascii=False, separators=(",", ":")) + ending)
            seen += 1
        else:
            output.append(line)
    if seen != 1:
        raise ValueError("The p.353 statement did not occur exactly once.")
    statement_out = (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")
    after = read_jsonl(statement_out)
    open_rows = [
        r for r in after
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    ]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 338 or no_reason != 11:
        raise ValueError(f"Unexpected post-edit endpoint inventory: open={len(open_rows)}, no_reason={no_reason}")

    print("reviewed=CHP-14 p.353 physical page 7 and p.354 physical page 8 continuation")
    print("decision=retain the picture endpoint open between two named Brühl commissions; record why the continuation does not disambiguate it")
    print(f"open_true={338}->{len(open_rows)}; no_reason=12->{no_reason}; candidates=12399; mentions=26613; statements={len(statements)}")
    print(f"book-statements.jsonl sha256 {sha(raw)}->{sha(statement_out)}")
    if args.preview:
        return 0
    if {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    } != actual:
        raise ValueError("Apply requires the three input hashes printed by this preview.")
    backup = STATEMENTS.with_name(STATEMENTS.name + BACKUP_SUFFIX)
    temp = STATEMENTS.with_name(STATEMENTS.name + TEMP_SUFFIX)
    if backup.exists() or temp.exists():
        raise FileExistsError("A recovery copy or temporary statement table already exists.")
    shutil.copy2(STATEMENTS, backup)
    try:
        temp.write_bytes(statement_out)
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
