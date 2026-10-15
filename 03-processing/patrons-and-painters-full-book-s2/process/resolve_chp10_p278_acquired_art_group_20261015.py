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
SEGMENT_ID = "chp-10:10_CHP-10_intro:l26-41"
SEGMENT_SHA256 = "11109dec2da0c22589297ae786772e434dfb0571e62cde36113512f37e6db0ab"
SEGMENT_ASSET_SHA256 = "f912dba9e5c8460538222c57d32c3734d0c23c72cb32a0871b50b6901ce9e27f"
PDF_SHA256 = "c4dc87df223967525a92edae8d28dc5307ce45787eb7b5e337f079c33dcfadbb"
STATEMENT_ID = "st-chp10-p278-german-courts-art-from-italy-late-baroque"
ART_GROUP_ID = "cand-12419"
ART_GROUP_MENTION_1 = "m-chp10-p278-german-court-purchased-artworks"
ART_GROUP_MENTION_2 = "m-chp10-p278-late-baroque-pictures"
EXPECTED_HASHES = {
    "statements": "8aa57fb5d766758505aecdff7e4e6a484a9f177dbf21e7cc560f3b5e9275df59",
    "mentions": "dd60b41ccdd63bd9a8dd10c4121877a0161ffe09b766c0fce5ca0f0f48cba738",
    "candidates": "7382337a2c610047feabf75cb9119a746d62acb0b7d5921caa531184e6a51c0c",
}
BACKUP_SUFFIX = ".bak-s2-chp10-p278-art-group-20261015"
TEMP_SUFFIX = ".tmp-s2-chp10-p278-art-group-20261015"


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
        raise ValueError(f"A planned {key} ID already exists.")
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
            raise ValueError("Could not map CSV record to source lines.")
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
    parser = argparse.ArgumentParser(description="Add the source-described art-purchase group for the p.278 German-courts claim.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-statements-sha256")
    parser.add_argument("--expected-mentions-sha256")
    parser.add_argument("--expected-candidates-sha256")
    args = parser.parse_args()

    pdf = ROOT / "02-sources/01-book/CHP-10.pdf"
    if sha(pdf.read_bytes()) != PDF_SHA256:
        raise ValueError("Reviewed CHP-10.pdf changed.")
    segment_matches = [r for r in jsonl(SEGMENTS.read_bytes()) if r.get("segment_id") == SEGMENT_ID]
    if len(segment_matches) != 1:
        raise ValueError("Reviewed p.278 segment is missing or duplicated.")
    segment = segment_matches[0]
    if segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SEGMENT_ASSET_SHA256:
        raise ValueError("Reviewed p.278 segment metadata changed.")
    lines = (ROOT / segment["source_file"]).read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != SEGMENT_SHA256:
        raise ValueError("Reviewed p.278 transcription changed.")
    phrase1 = "works of art from\nItaly"
    phrase2 = "pictures in the late Baroque style"
    if text.count(phrase1) != 1 or text.count(phrase2) != 1 or "they went on purchasing" not in text:
        raise ValueError("The reviewed p.278 acquisition phrases changed.")

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
        or updated.get("subject_candidate_id") != "cand-8852"
        or updated.get("object_candidate_id")
        or q.get("relation_candidate") is not True
        or q.get("open_endpoint_reason")
    ):
        raise ValueError("Reviewed statement no longer matches its expected open state.")
    _, _, mention_rows = csv_rows(raw["mentions"])
    _, _, candidate_rows = csv_rows(raw["candidates"])
    if len(mention_rows) != 26609 or len(candidate_rows) != 12396:
        raise ValueError("Unexpected mention or candidate inventory.")
    mention_ids = {row["mention_id"] for row in mention_rows}
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    if {ART_GROUP_MENTION_1, ART_GROUP_MENTION_2} & mention_ids or ART_GROUP_ID in candidate_ids:
        raise ValueError("A planned p.278 candidate or mention ID already exists.")

    group_candidate = {
        "candidate_id": ART_GROUP_ID,
        "index_entry_id": "",
        "canonical_name": "German-court art acquisitions described on p.278 (Italian works and familiar Late Baroque pictures; individual works unspecified)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says many German courts had obtained works of art from Italy for at least a generation and continued to purchase pictures in the late Baroque style. This source-defined group records the acquired works as a broad object set; exact works and overlap between the Italian-origin and style descriptions are unspecified. The style itself remains separately represented by cand-8853.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L28",
    }
    start1, start2 = text.index(phrase1), text.index(phrase2)
    mentions = [
        {
            "mention_id": ART_GROUP_MENTION_1,
            "segment_id": SEGMENT_ID,
            "candidate_id": ART_GROUP_ID,
            "surface_form": phrase1,
            "start_char": str(start1),
            "end_char": str(start1 + len(phrase1)),
            "note": "Italian-origin art objects obtained by the German courts; the transcription preserves the page line break.",
        },
        {
            "mention_id": ART_GROUP_MENTION_2,
            "segment_id": SEGMENT_ID,
            "candidate_id": ART_GROUP_ID,
            "surface_form": phrase2,
            "start_char": str(start2),
            "end_char": str(start2 + len(phrase2)),
            "note": "Pictures the courts continued to purchase; style is separately mapped to cand-8853.",
        },
    ]
    updated["object_candidate_id"] = ART_GROUP_ID
    q["claim"] = "Haskell says many German courts had obtained works of art from Italy for at least a generation and continued buying pictures in the late Baroque style to which they were accustomed."
    q["qualification"] = "This is a group-level historical summary. The individual courts and artworks are not identified; the Italian-origin set and Late Baroque-style set may overlap, but the passage does not specify how."
    q["mentioned_candidate_ids"] = ["cand-3461", "cand-8852", ART_GROUP_ID, "cand-8853"]
    q["relation_candidate_note"] = "The source explicitly connects the German-court group to a broad group of acquired art objects; the style term is kept separate from the works themselves."
    q.pop("open_endpoint_reason", None)
    updated["qualifiers"] = q

    statement_out = rewrite_statement(raw["statements"], updated)
    mention_out = patch_csv(raw["mentions"], "mention_id", mentions)
    candidate_out = patch_csv(raw["candidates"], "candidate_id", [group_candidate])
    after_statements = jsonl(statement_out)
    open_rows = [r for r in after_statements if (r.get("qualifiers") or {}).get("relation_candidate") is True and (not r.get("subject_candidate_id") or not r.get("object_candidate_id"))]
    no_reason = sum(not (r.get("qualifiers") or {}).get("open_endpoint_reason") for r in open_rows)
    if len(open_rows) != 358 or no_reason != 35:
        raise ValueError(f"Unexpected open endpoint inventory: open={len(open_rows)}, no_reason={no_reason}")
    if len(csv_rows(mention_out)[2]) != 26611 or len(csv_rows(candidate_out)[2]) != 12397:
        raise ValueError("Unexpected post-edit mention or candidate inventory.")
    for mention in mentions:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if end - start != len(mention["surface_form"]) or text[start:end] != mention["surface_form"]:
            raise ValueError(f"Mention span mismatch: {mention['mention_id']}")

    outputs = {STATEMENTS: statement_out, MENTIONS: mention_out, CANDIDATES: candidate_out}
    print("reviewed=CHP-10 p.278 / PDF physical page 3 against page image and transcription")
    print("change=connect German-court acquisition claim to a scoped art-object group; keep Late Baroque style as a separate term")
    print("open_endpoints=359->358; no_reason_open=36->35; candidates=12396->12397; mentions=26609->26611")
    for path, data in outputs.items():
        print(f"{path.name} sha256 {sha(path.read_bytes())}->{sha(data)}")
    if args.preview:
        return 0
    requested = {
        "statements": args.expected_statements_sha256,
        "mentions": args.expected_mentions_sha256,
        "candidates": args.expected_candidates_sha256,
    }
    if requested != actual:
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
