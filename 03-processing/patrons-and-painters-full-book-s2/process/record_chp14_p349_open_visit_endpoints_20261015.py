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
SEGMENT_ID = "chp-14:14_CHP-14_intro:l23-33"
SEGMENT_SHA256 = "1745cb7234b595f967f5d20f960d680c3f2635e0e1aafbeaecd6eff54fe6663b"
ASSET_SHA256 = "d472c0aed1891f38546c3f73557c46583dcc7f744b0dbb764fc7a94cff71cdf7"
ENDPOINT_REASONS = {
    "st-chp14-p349-stay-between-venice-and-milan": (
        "Haskell says Algarotti stayed for about a year between Venice and Milan but names no distinct place or bounded area and does not assign residence to either city. Preserve the source's location range; do not infer an endpoint from the two city mentions."
    ),
    "st-chp14-p349-brief-visit-1760": (
        "The source does not name the destination of the visit in 1760. It then says Algarotti returned to Venice on only three occasions (1737, 1743–45, and 1753–56), so this visit cannot be assigned to Venice; no other destination is supplied."
    ),
}
EXPECTED_HASHES = {
    "statements": "97ef59f12b9523d03a9e538802247cf2c87097f3a339b7e81df389bdad05cf85",
    "mentions": "9ed666c4eafce131efd41c489b29d8a0214ba6669fc2a21c202a6db28133d3c7",
    "candidates": "0f990b0e9fba758ccfeeed84ef0e7336e21716d18cce35eec70bbb1fcf63dbc4",
}
BACKUP_SUFFIX = ".bak-s2-chp14-p349-open-endpoint-reasons-20261015"
TEMP_SUFFIX = ".tmp-s2-chp14-p349-open-endpoint-reasons-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Record source-supported open endpoint reasons for CHP-14 p.349.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    segment_rows = read_jsonl((TABLES / "segments.jsonl").read_bytes())
    segment_matches = [r for r in segment_rows if r.get("segment_id") == SEGMENT_ID]
    if len(segment_matches) != 1:
        raise ValueError("The reviewed p.349 segment is missing or duplicated.")
    segment = segment_matches[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != ASSET_SHA256:
        raise ValueError("The reviewed p.349 segment metadata changed.")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source_text.encode("utf-8")) != segment.get("sha256"):
        raise ValueError("The reviewed p.349 source text changed.")
    if sha(PDF.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-14.pdf changed.")

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
    replacements = {}
    for statement_id, reason in ENDPOINT_REASONS.items():
        row = by_id.get(statement_id)
        if not row:
            raise ValueError(f"Target statement is missing: {statement_id}")
        updated = json.loads(json.dumps(row, ensure_ascii=False))
        q = updated.get("qualifiers") or {}
        if (
            updated.get("segment_id") != SEGMENT_ID
            or updated.get("subject_candidate_id") != "cand-0080"
            or updated.get("object_candidate_id")
            or q.get("relation_candidate") is not True
            or q.get("open_endpoint_reason")
        ):
            raise ValueError(f"Target no longer matches the reviewed open state: {statement_id}")
        q["open_endpoint_reason"] = reason
        updated["qualifiers"] = q
        replacements[statement_id] = updated

    bom = raw.startswith(b"\xef\xbb\xbf")
    output: list[str] = []
    seen: set[str] = set()
    for line in raw.decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        statement_id = row.get("statement_id")
        if statement_id in replacements:
            output.append(json.dumps(replacements[statement_id], ensure_ascii=False, separators=(",", ":")) + ending)
            seen.add(statement_id)
        else:
            output.append(line)
    if seen != set(replacements):
        raise ValueError("Target statements were not rewritten exactly once.")
    statement_out = (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")
    after = read_jsonl(statement_out)
    open_rows = [
        r for r in after
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    ]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 338 or no_reason != 12:
        raise ValueError(f"Unexpected post-edit endpoint inventory: open={len(open_rows)}, no_reason={no_reason}")

    print("reviewed=CHP-14 p.349 / PDF physical page 3")
    print("decision=retain two missing destination endpoints with reasons; do not map the between-cities stay or 1760 visit to either city")
    print(f"open_true={338}->{len(open_rows)}; no_reason=14->{no_reason}; candidates=12399; mentions=26613; statements={len(statements)}")
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
