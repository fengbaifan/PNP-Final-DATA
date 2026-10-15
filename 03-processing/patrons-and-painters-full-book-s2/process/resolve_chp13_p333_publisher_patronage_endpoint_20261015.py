from __future__ import annotations

import argparse
import csv
import hashlib
import io
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
SEGMENT_ID = "chp-13:13_CHP-13_intro:l14-19"
SEGMENT_SHA256 = "14b387b94bdd8ff02e1b97b42c2ab554839d8a2d55645f6a7d5d00b82a554bf6"
SEGMENT_ASSET_SHA256 = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
PDF_SHA256 = "da49addcf425e7473770ba02db64284d1189934cf38f2b773f0672f052fca2bc"
STATEMENT_ID = "st-chp13-p333-publishers-depended-on-patronage-for-expensive-ventures"
PATRONAGE_ID = "cand-12420"
PATRONAGE_MENTION_ID = "m-chp13-p333-expensive-venture-patronage"
EXPECTED_HASHES = {
    "statements": "24873e74c23e3cdf28e8e2aea9171ea751b4cc3c66a6d811e89e0ab2a2f1a6ea",
    "mentions": "effa39971bac832b92e4db71bbb03dfab673cacaf83fab81a5cea72957ef9785",
    "candidates": "ff685facf31062a4023534d2caed8813df8a8fc87ac32b745f5fc2d2a4cdb0e4",
}
BACKUP_SUFFIX = ".bak-s2-chp13-p333-patronage-term-20261015"
TEMP_SUFFIX = ".tmp-s2-chp13-p333-patronage-term-20261015"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def jsonl(raw: bytes) -> list[dict]:
    return [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]


def csv_rows(raw: bytes) -> tuple[bool, list[str], list[dict[str, str]]]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return bom, list(reader.fieldnames or []), list(reader)


def patch_csv(raw: bytes, key: str, additions: list[dict[str, str]]) -> bytes:
    bom, fields, parsed = csv_rows(raw)
    ids = [row.get(key, "") for row in parsed]
    if not fields or len(ids) != len(set(ids)) or any(set(row) != set(fields) for row in additions):
        raise ValueError(f"Invalid {key} table schema or duplicate IDs.")
    if any(row[key] in set(ids) for row in additions):
        raise ValueError(f"Planned {key} ID already exists.")
    text = raw.decode("utf-8-sig")
    physical = text.splitlines(keepends=True)
    newline = "\r\n" if b"\r\n" in raw else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != fields or reader.line_num != 1:
        raise ValueError("CSV header is changed or multiline.")
    previous_line = reader.line_num
    output = [physical[0]]
    for _row in reader:
        end_line = reader.line_num
        chunk = "".join(physical[previous_line:end_line])
        if not chunk:
            raise ValueError("Could not map CSV record to physical lines.")
        output.append(chunk)
        previous_line = end_line
    for row in additions:
        stream = io.StringIO(newline="")
        csv.DictWriter(stream, fieldnames=fields, lineterminator=newline).writerow(row)
        output.append(stream.getvalue())
    return (("\ufeff" if bom else "") + "".join(output)).encode("utf-8")


def rewrite_statement(raw: bytes, updated: dict) -> bytes:
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
    return (("\ufeff" if bom else "") + "".join(out)).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Represent patronage as the explicit support concept in the p.333 publisher claim.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()
    if sha((ROOT / "02-sources/01-book/CHP-13.pdf").read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-13.pdf changed.")
    segments = [r for r in jsonl(SEGMENTS.read_bytes()) if r.get("segment_id") == SEGMENT_ID]
    if len(segments) != 1:
        raise ValueError("Reviewed p.333 segment is missing or duplicated.")
    segment = segments[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SEGMENT_ASSET_SHA256:
        raise ValueError("Reviewed p.333 segment metadata changed.")
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != SEGMENT_SHA256 or text.count("they themselves depended on patronage to make it possible") != 1:
        raise ValueError("Reviewed p.333 statement text changed.")

    raw = {"statements": STATEMENTS.read_bytes(), "mentions": MENTIONS.read_bytes(), "candidates": CANDIDATES.read_bytes()}
    actual = {name: sha(data) for name, data in raw.items()}
    if actual != EXPECTED_HASHES:
        raise ValueError(f"Protected table snapshot changed: {actual}")
    statements = jsonl(raw["statements"])
    found = [r for r in statements if r.get("statement_id") == STATEMENT_ID]
    if len(statements) != 15158 or len(found) != 1:
        raise ValueError("Unexpected statement inventory or target multiplicity.")
    updated = json.loads(json.dumps(found[0], ensure_ascii=False))
    q = updated.get("qualifiers") or {}
    if (
        updated.get("segment_id") != SEGMENT_ID
        or updated.get("subject_candidate_id") != "cand-2068"
        or updated.get("object_candidate_id")
        or q.get("relation_candidate") is not True
        or q.get("open_endpoint_reason")
    ):
        raise ValueError("Target statement no longer matches its expected open state.")
    _, _, mention_rows = csv_rows(raw["mentions"])
    _, _, candidate_rows = csv_rows(raw["candidates"])
    if len(mention_rows) != 26611 or len(candidate_rows) != 12397:
        raise ValueError("Unexpected mention or candidate inventory.")
    if any(r["mention_id"] == PATRONAGE_MENTION_ID for r in mention_rows) or any(r["candidate_id"] == PATRONAGE_ID for r in candidate_rows):
        raise ValueError("Planned patronage candidate or mention ID already exists.")

    candidate = {
        "candidate_id": PATRONAGE_ID,
        "index_entry_id": "",
        "canonical_name": "Patronage as support enabling expensive Venetian publishing ventures (Haskell, p.333)",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says publishers sometimes depended on patronage to make an expensive venture possible. This term represents general financial or social support, not a named donor; no particular venture is identified in this clause.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L17",
    }
    phrase = "patronage"
    anchor = "they themselves depended on "
    start = text.index(anchor) + len(anchor)
    mention = {
        "mention_id": PATRONAGE_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": PATRONAGE_ID,
        "surface_form": phrase,
        "start_char": str(start),
        "end_char": str(start + len(phrase)),
        "note": "General support concept publishers relied on for expensive ventures; no patron is identified here.",
    }
    updated["object_candidate_id"] = PATRONAGE_ID
    q["claim"] = "Haskell says Venetian publishers sometimes depended on patronage to make expensive publishing ventures possible."
    q["qualification"] = "The endpoint is the support concept, not an identified patron; neither a provider nor a particular venture is named in this clause."
    q["mentioned_candidate_ids"] = ["cand-2068", PATRONAGE_ID]
    q["relation_candidate_note"] = "The sentence explicitly says publishers depended on patronage; no external patron is assigned as the grammatical object."
    q.pop("open_endpoint_reason", None)
    updated["qualifiers"] = q

    statement_out = rewrite_statement(raw["statements"], updated)
    mention_out = patch_csv(raw["mentions"], "mention_id", [mention])
    candidate_out = patch_csv(raw["candidates"], "candidate_id", [candidate])
    after = jsonl(statement_out)
    open_rows = [r for r in after if (r.get("qualifiers") or {}).get("relation_candidate") is True and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 357 or no_reason != 33:
        raise ValueError(f"Unexpected open endpoint state: open={len(open_rows)}, no_reason={no_reason}")
    if len(csv_rows(mention_out)[2]) != 26612 or len(csv_rows(candidate_out)[2]) != 12398:
        raise ValueError("Unexpected post-edit mention or candidate inventory.")
    if text[int(mention["start_char"]):int(mention["end_char"])] != phrase:
        raise ValueError("New patronage mention does not match the source span.")

    outputs = {STATEMENTS: statement_out, MENTIONS: mention_out, CANDIDATES: candidate_out}
    print("reviewed=CHP-13 p.333 / PDF physical page 2 against page image and transcription")
    print("change=map missing object to the explicit support concept of patronage; retain provider and specific venture as unstated")
    print("open_endpoints=358->357; no_reason_open=34->33; candidates=12397->12398; mentions=26611->26612")
    for path, data in outputs.items():
        print(f"{path.name} sha256 {sha(path.read_bytes())}->{sha(data)}")
    if args.preview:
        return 0
    if {"statements": args.expected_statements_sha256, "mentions": args.expected_mentions_sha256, "candidates": args.expected_candidates_sha256} != actual:
        raise ValueError("Apply requires the three input hashes printed by this preview.")
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    temps = {path: path.with_name(path.name + TEMP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()) or any(path.exists() for path in temps.values()):
        raise FileExistsError("Recovery copy or temporary table already exists.")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    try:
        for path, data in outputs.items():
            temps[path].write_bytes(data)
        for path in outputs:
            temps[path].replace(path)
    except Exception:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()
        for path, backup in backups.items():
            shutil.copy2(backup, path)
        raise
    print("applied=yes")
    for path, backup in backups.items():
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.name}:{sha(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
