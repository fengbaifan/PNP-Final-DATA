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
PDF = ROOT / "02-sources/01-book/CHP-15.pdf"
PDF_SHA256 = "357e830cc4e880909edd62975bfcd06ade1c2b432d8866229831025fe86f2885"
SEGMENT_ID = "chp-15:15_CHP-15_sec_i:l3-14"
SEGMENT_SHA256 = "91e85c703307993e203cb7fda423cc27fc2acf91a902ec81bb365f41f41f44f2"
ASSET_SHA256 = "798e2903ab45c8a90ac5be9746c43964007426d3b2e2723baa20332665d11624"
STATEMENT_ID = "st-chp15-p361-men-encouraged-revival-venetian-painting"
OPEN_REASON = (
    "The demonstrative 'these men' has no complete roster in this paragraph. The preceding account names several collectors and collection episodes, but Haskell does not state which people the phrase includes. Do not construct a group from nearby names; keep the subject endpoint open."
)
EXPECTED_HASHES = {
    "statements": "d031777e6388656d80744ad9b1e946d81adf426fc09ba5b178381864bb1d3772",
    "mentions": "9ed666c4eafce131efd41c489b29d8a0214ba6669fc2a21c202a6db28133d3c7",
    "candidates": "0f990b0e9fba758ccfeeed84ef0e7336e21716d18cce35eec70bbb1fcf63dbc4",
}
BACKUP_SUFFIX = ".bak-s2-chp15-p361-unnamed-men-open-reason-20261015"
TEMP_SUFFIX = ".tmp-s2-chp15-p361-unnamed-men-open-reason-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record why the p.361 demonstrative subject remains unresolved.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    if sha(PDF.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-15.pdf changed.")
    segment_rows = read_jsonl(SEGMENTS.read_bytes())
    matches = [r for r in segment_rows if r.get("segment_id") == SEGMENT_ID]
    if len(matches) != 1:
        raise ValueError("The reviewed p.361 segment is missing or duplicated.")
    segment = matches[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != ASSET_SHA256:
        raise ValueError("Reviewed p.361 segment metadata changed.")
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source_text.encode("utf-8")) != SEGMENT_SHA256 or source_text.count("These were the men who had encouraged") != 1:
        raise ValueError("Reviewed p.361 source text changed.")

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
    matches = [r for r in statements if r.get("statement_id") == STATEMENT_ID]
    if len(matches) != 1:
        raise ValueError("The p.361 target statement is missing or duplicated.")
    updated = json.loads(json.dumps(matches[0], ensure_ascii=False))
    q = updated.get("qualifiers") or {}
    if (
        updated.get("segment_id") != SEGMENT_ID
        or updated.get("subject_candidate_id")
        or updated.get("object_candidate_id") != "cand-10429"
        or q.get("relation_candidate") is not True
        or q.get("open_endpoint_reason")
    ):
        raise ValueError("The p.361 target no longer matches the reviewed open state.")
    q["open_endpoint_reason"] = OPEN_REASON
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
        raise ValueError("The p.361 target was not rewritten exactly once.")
    statement_out = (("\ufeff" if bom else "") + "".join(out)).encode("utf-8")
    after = read_jsonl(statement_out)
    open_rows = [
        r for r in after
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    ]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 338 or no_reason != 10:
        raise ValueError(f"Unexpected post-edit endpoint inventory: open={len(open_rows)}, no_reason={no_reason}")

    print("reviewed=CHP-15 p.361 / PDF physical page 1 and full paragraph context")
    print("decision=keep the collective subject open; the paragraph gives no complete roster for 'these men'")
    print(f"open_true={338}->{len(open_rows)}; no_reason=11->{no_reason}; candidates=12399; mentions=26613; statements={len(statements)}")
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
