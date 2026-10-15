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
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
PDF = ROOT / "02-sources/01-book/CHP-13.pdf"
PDF_SHA256 = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l173-177"
SEGMENT_SHA256 = "1707ce58364293f8f81819502d125502c9cc25d285580b0ecb3377ab547939d1"
ASSET_SHA256 = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
ENDPOINTS = {
    "st-chp13-p346-toni-agent-for-zaccaria-sagredo": ("cand-2640", "cand-2329"),
    "st-chp13-p346-toni-agent-for-zanetti": ("cand-2640", "cand-2838"),
    "st-chp13-p346-toni-agent-for-consul-smith": ("cand-2640", "cand-2440"),
}
MENTION_EXPECTATIONS = {
    "m-s2-ch13-p346-003": ("cand-2329", "Zaccaria Sagredo"),
    "m-s2-ch13-p346-004": ("cand-2838", "Zanetti"),
    "m-s2-ch13-p346-005": ("cand-2440", "Consul Smith"),
}
EXPECTED_HASHES = {
    "statements": "d81aae7b25c042b25d8ddca9bba159299f2767c48a5df383d9cf79d0ff910ae5",
    "mentions": "9ed666c4eafce131efd41c489b29d8a0214ba6669fc2a21c202a6db28133d3c7",
    "candidates": "0f990b0e9fba758ccfeeed84ef0e7336e21716d18cce35eec70bbb1fcf63dbc4",
}
BACKUP_SUFFIX = ".bak-s2-chp13-p346-agent-endpoints-20261015"
TEMP_SUFFIX = ".tmp-s2-chp13-p346-agent-endpoints-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve Toni agency endpoints from p.346 and the book's index mappings.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    if sha(PDF.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-13.pdf changed.")
    segment_rows = read_jsonl(SEGMENTS.read_bytes())
    found_segments = [r for r in segment_rows if r.get("segment_id") == SEGMENT_ID]
    if len(found_segments) != 1:
        raise ValueError("The reviewed p.346 segment is missing or duplicated.")
    segment = found_segments[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != ASSET_SHA256:
        raise ValueError("The reviewed p.346 segment metadata changed.")
    source_lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    source_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(source_text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("The reviewed p.346 source text changed.")

    raw = {
        "statements": STATEMENTS.read_bytes(),
        "mentions": MENTIONS.read_bytes(),
        "candidates": CANDIDATES.read_bytes(),
    }
    actual = {name: sha(data) for name, data in raw.items()}
    if actual != EXPECTED_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual}")
    statements = read_jsonl(raw["statements"])
    statement_by_id = {r["statement_id"]: r for r in statements}
    if len(statements) != 15158 or len(statement_by_id) != len(statements):
        raise ValueError("Unexpected statement inventory or duplicate IDs.")

    import csv
    import io
    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        mentions = {r["mention_id"]: r for r in csv.DictReader(handle)}
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidates = {r["candidate_id"]: r for r in csv.DictReader(handle)}
    for mention_id, (candidate_id, surface) in MENTION_EXPECTATIONS.items():
        mention = mentions.get(mention_id)
        if not mention or mention.get("segment_id") != SEGMENT_ID or mention.get("candidate_id") != candidate_id or mention.get("surface_form") != surface:
            raise ValueError(f"P.346 mention changed: {mention_id}")
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if source_text[start:end] != surface:
            raise ValueError(f"P.346 mention span does not match source: {mention_id}")
    for candidate_id in {endpoint for pair in ENDPOINTS.values() for endpoint in pair}:
        if candidate_id not in candidates:
            raise ValueError(f"Required candidate is missing: {candidate_id}")
        if "346" not in [p.strip() for p in candidates[candidate_id].get("index_page_range", "").split(",")]:
            raise ValueError(f"The source index does not map p.346 to {candidate_id}")

    replacements = {}
    for statement_id, (subject_id, object_id) in ENDPOINTS.items():
        row = statement_by_id.get(statement_id)
        if not row:
            raise ValueError(f"P.346 statement is missing: {statement_id}")
        updated = json.loads(json.dumps(row, ensure_ascii=False))
        q = updated.get("qualifiers") or {}
        if (
            updated.get("segment_id") != SEGMENT_ID
            or updated.get("subject_candidate_id")
            or updated.get("object_candidate_id")
            or q.get("relation_candidate") is not True
            or q.get("open_endpoint_reason")
            or not set(q.get("mentioned_candidate_ids", [])) >= {subject_id, object_id}
        ):
            raise ValueError(f"P.346 statement changed from reviewed open state: {statement_id}")
        updated["subject_candidate_id"] = subject_id
        updated["object_candidate_id"] = object_id
        if statement_id == "st-chp13-p346-toni-agent-for-zanetti":
            q["qualification"] = (
                "The text gives only the surname, but Haskell's own index maps p.346 to A. M. Zanetti the Elder. Use this source-local mapping; external identity alignment and any specific commission remain unresolved."
            )
            q["relation_candidate_note"] = (
                "Toni's agency for the p.346 Zanetti is explicit; the book's index maps this page to its A. M. Zanetti the Elder entry (cand-2838)."
            )
        elif statement_id == "st-chp13-p346-toni-agent-for-consul-smith":
            q["qualification"] = (
                "The text gives title and surname, while Haskell's own index maps p.346 to Joseph Smith (cand-2440). Use the source-local mapping; external identity alignment and any specific commission remain unresolved."
            )
            q["relation_candidate_note"] = (
                "Toni's agency for Consul Smith is explicit; the book's index maps this page to its Joseph Smith entry (cand-2440)."
            )
        updated["qualifiers"] = q
        replacements[statement_id] = updated

    bom = raw["statements"].startswith(b"\xef\xbb\xbf")
    out: list[str] = []
    seen: set[str] = set()
    for line in raw["statements"].decode("utf-8-sig").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        row = json.loads(body)
        statement_id = row.get("statement_id")
        if statement_id in replacements:
            out.append(json.dumps(replacements[statement_id], ensure_ascii=False, separators=(",", ":")) + ending)
            seen.add(statement_id)
        else:
            out.append(line)
    if seen != set(replacements):
        raise ValueError("Not all p.346 statements were rewritten exactly once.")
    statement_out = (("\ufeff" if bom else "") + "".join(out)).encode("utf-8")
    result = read_jsonl(statement_out)
    open_rows = [
        r for r in result
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
        and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))
    ]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 338 or no_reason != 14:
        raise ValueError(f"Unexpected post-edit open endpoint inventory: open={len(open_rows)}, no_reason={no_reason}")

    print("reviewed=CHP-13 p.346 / PDF physical page 19; source text and Haskell index page ranges")
    print("decision=resolve Toni's agency for Sagredo, A. M. Zanetti the Elder, and Joseph Smith using explicit p.346 index mappings")
    print(f"open_true=341->{len(open_rows)}; no_reason=17->{no_reason}; candidates={len(candidates)}; mentions={len(mentions)}; statements={len(statements)}")
    print(f"book-statements.jsonl sha256 {sha(raw['statements'])}->{sha(statement_out)}")
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
