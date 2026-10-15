from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
COVERAGE = TABLES / "s2-coverage.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_i.md"
SEGMENT_ID = "chp-1:01_CHP-1_sec_i:l15-24"
STATEMENT_ID = "st-chp1-l57-60-papal-clients"
CANDIDATE_ID = "cand-12270"
MENTION_ID = "m-chp1-seci-successive-popes"
SURFACE = "successive popes"

EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "4036994c619d907a075ab663608c8a20ce94a571931173c33bae7f3db4a5c480",
    MENTIONS: "efb923d5c7383bedf8a9636925b2863bdd31000f82d3825a28337e42c27390fc",
    STATEMENTS: "aeff3d38e0acb2e1536795000c5d5cbbfaab1ec6fdfceab8e5ccd84886d3ee61",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    COVERAGE: "1352b756f0f0310c00d21bfc3bfe194b5a347d291b699db78b5c85fa6e636a4d",
    SOURCE: "fb6198d0392e70a23a2d9ed05c0d432d4466de4ba75cc96762e3b4e45a204c40",
}
BACKUPS = {
    CANDIDATES: CANDIDATES.with_name(CANDIDATES.name + ".bak-s2-chp1-successive-popes-20261015"),
    MENTIONS: MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp1-successive-popes-20261015"),
    STATEMENTS: STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp1-successive-popes-20261015"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_csv(data: bytes):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def csv_row(headers, row):
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n", extrasaction="ignore").writerow(row)
    return buffer.getvalue().encode("utf-8")


def append_bytes(data: bytes, addition: bytes) -> bytes:
    return data + (b"" if data.endswith((b"\n", b"\r")) else b"\n") + addition


def build():
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit(f"HEAD changed: expected {EXPECTED_HEAD}, got {head}")
    for path, expected in EXPECTED_HASHES.items():
        actual = digest(path.read_bytes())
        if actual != expected:
            raise SystemExit(f"{path.relative_to(ROOT)} hash changed: expected {expected}, got {actual}")

    candidate_bytes, mention_bytes, statement_bytes = CANDIDATES.read_bytes(), MENTIONS.read_bytes(), STATEMENTS.read_bytes()
    candidate_headers, candidates = parse_csv(candidate_bytes)
    mention_headers, mentions = parse_csv(mention_bytes)
    if len(candidates) != 12_247 or len(mentions) != 26_435:
        raise SystemExit("unexpected candidate or mention table counts")
    if CANDIDATE_ID in {row["candidate_id"] for row in candidates} or MENTION_ID in {row["mention_id"] for row in mentions}:
        raise SystemExit("new candidate or mention ID already exists")
    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row["segment_id"] == SEGMENT_ID), None)
    if not segment:
        raise SystemExit(f"missing S0 segment {SEGMENT_ID}")
    source_bytes = SOURCE.read_bytes()
    if digest(source_bytes) != segment["asset_sha256"]:
        raise SystemExit("S0 source asset hash mismatch")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if digest(segment_text.encode("utf-8")) != segment["sha256"]:
        raise SystemExit("S0 segment hash mismatch")
    if segment_text.count(SURFACE) != 1:
        raise SystemExit("the target group phrase is not unique in the S0 segment")
    start, end = segment_text.index(SURFACE), segment_text.index(SURFACE) + len(SURFACE)
    for row in mentions:
        if row["segment_id"] != SEGMENT_ID:
            continue
        old_start, old_end = int(row["start_char"]), int(row["end_char"])
        if start < old_end and end > old_start:
            raise SystemExit(f"new group mention overlaps existing mention {row['mention_id']}")
    coverage_rows = list(csv.DictReader(COVERAGE.open(encoding="utf-8-sig", newline="")))
    coverage = next((row for row in coverage_rows if row["segment_id"] == SEGMENT_ID), None)
    if not coverage or coverage.get("disposition") != "reviewed" or coverage.get("migration_status") != "complete":
        raise SystemExit("S2 coverage is not reviewed/complete for the source segment")

    statement_lines = statement_bytes.splitlines(keepends=True)
    target_index = target = None
    for index, raw in enumerate(statement_lines):
        if raw.strip():
            row = json.loads(raw)
            if row.get("statement_id") == STATEMENT_ID:
                target_index, target = index, row
                break
    if target is None or target.get("segment_id") != SEGMENT_ID:
        raise SystemExit(f"missing or changed statement {STATEMENT_ID}")
    if target.get("subject_candidate_id") not in (None, "") or target.get("object_candidate_id") != "cand-11819":
        raise SystemExit("statement endpoints changed")
    qualifiers = target.get("qualifiers", {})
    if qualifiers.get("relation_candidate") is not True or qualifiers.get("source_line_start") != 57:
        raise SystemExit("statement classification or source anchor changed")

    new_candidate = {
        "candidate_id": CANDIDATE_ID, "index_entry_id": "",
        "canonical_name": "Successive popes who brought relatives, friends and clients to Rome (source-defined group)",
        "index_page_range": "", "suggested_type": "", "status": "open", "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes successive popes as surrounding themselves with relatives, friends and clients when they came to the throne. No individual pope, count or complete membership list is identified. Type remains unset because the taxonomy has no person-group type.",
        "exclude_reason": "", "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L57",
    }
    new_mention = {
        "mention_id": MENTION_ID, "segment_id": SEGMENT_ID, "candidate_id": CANDIDATE_ID,
        "surface_form": SURFACE, "start_char": str(start), "end_char": str(end),
        "note": "Source-defined recurring group subject; no named pope or count is inferred.",
    }
    updated = dict(target)
    updated["subject_candidate_id"] = CANDIDATE_ID
    updated_qualifiers = dict(qualifiers)
    updated_qualifiers.pop("open_endpoint_reason", None)
    updated_qualifiers["relation_candidate_note"] = "The source's generic phrase 'successive popes' is mapped to an open, source-defined group; the object remains the already mapped group of relatives, friends and clients cand-11819. No individual pope or officeholder is inferred."
    updated["qualifiers"] = updated_qualifiers

    candidate_after = append_bytes(candidate_bytes, csv_row(candidate_headers, new_candidate))
    mention_after = append_bytes(mention_bytes, csv_row(mention_headers, new_mention))
    original_line = statement_lines[target_index]
    ending = b"\r\n" if original_line.endswith(b"\r\n") else b"\n" if original_line.endswith(b"\n") else b""
    statement_lines[target_index] = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending
    statement_after = b"".join(statement_lines)
    _, candidate_check = parse_csv(candidate_after)
    _, mention_check = parse_csv(mention_after)
    if len(candidate_check) != 12_248 or len(mention_check) != 26_436:
        raise SystemExit("projected row counts do not match")
    if len({row["candidate_id"] for row in candidate_check}) != len(candidate_check) or len({row["mention_id"] for row in mention_check}) != len(mention_check):
        raise SystemExit("projected candidate or mention IDs are not unique")
    updates = {CANDIDATES: candidate_after, MENTIONS: mention_after, STATEMENTS: statement_after}
    return updates, start, end


def apply_transaction(updates):
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("one or more recovery backups already exist")
    for path, expected in EXPECTED_HASHES.items():
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"{path.relative_to(ROOT)} changed after preview")
    for source, backup in BACKUPS.items():
        shutil.copy2(source, backup)
    temps, replaced = {}, []
    try:
        for target, data in updates.items():
            with tempfile.NamedTemporaryFile("wb", dir=target.parent, delete=False) as stream:
                temp = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            temps[target] = temp
        for target, temp in temps.items():
            os.replace(temp, target)
            replaced.append(target)
    except Exception:
        for target in reversed(replaced):
            shutil.copy2(BACKUPS[target], target)
        raise
    finally:
        for temp in temps.values():
            if temp.exists():
                temp.unlink()


def main():
    parser = argparse.ArgumentParser(description="Resolve the source-defined successive-popes endpoint for one S2 statement.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updates, start, end = build()
    print(f"{STATEMENT_ID}: subject None -> {CANDIDATE_ID}; mention span {start}:{end} {SURFACE!r}")
    print("projected candidates=12248 mentions=26436 statements=15109")
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {digest(path.read_bytes())} -> {digest(data)}")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply_transaction(updates)
    print("backups:")
    for backup in BACKUPS.values():
        print(backup)
    print("applied")


if __name__ == "__main__":
    main()
