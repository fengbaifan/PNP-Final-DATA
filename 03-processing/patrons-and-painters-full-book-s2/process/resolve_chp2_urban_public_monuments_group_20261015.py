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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "2f9eac78b189591b0605fdf745b7a972c1f4448c91a6bfae3e4c3ffac1d5f29a",
    MENTIONS: "3ed7a55a7e489e10c8c57b8493f7ff8c0c9054d0a8a18d3d54aa276c71c7987e",
    STATEMENTS: "3d7954179817b566e8ce2aee45756d5e2cb564e2d30313c966b5ac97cb59a4c4",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "7efde367c2d7d600f599c17d09fbc4f57bf29aa6b7efb439859a1f45b8c863a9",
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l118-125"
STATEMENT_ID = "st-chp2-secii-l118-125-urban-public-monuments"
CANDIDATE_ID = "cand-12296"
MENTION_ID = "m-chp2-secii-l118-125-urban-public-monuments"
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-urban-public-monuments-group-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def write_csv(data: bytes, headers: list[str], rows: list[dict[str, str]]) -> bytes:
    line_ending = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    return bom + buffer.getvalue().encode("utf-8")


def source_segment() -> str:
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 segment or source asset mismatch")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    return text


def build() -> tuple[dict[Path, bytes], tuple[int, int]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")
    candidate_bytes = CANDIDATES.read_bytes()
    candidate_headers, candidate_rows = read_csv(candidate_bytes)
    mention_bytes = MENTIONS.read_bytes()
    mention_headers, mention_rows = read_csv(mention_bytes)
    if any(row["candidate_id"] == CANDIDATE_ID for row in candidate_rows) or any(row["mention_id"] == MENTION_ID for row in mention_rows):
        raise SystemExit("new candidate or mention ID already exists")
    max_id = max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-"))
    if max_id != 12295:
        raise SystemExit(f"candidate sequence changed: {max_id}")

    text = source_segment()
    surface = "grander and more public monuments"
    if text.count(surface) != 1:
        raise SystemExit("source phrase changed")
    start = text.index(surface)
    end = start + len(surface)
    if "to himself" not in text[end:end + 25]:
        raise SystemExit("monument ownership context changed")
    if any(row["segment_id"] == SEGMENT_ID and start < int(row["end_char"]) and end > int(row["start_char"]) for row in mention_rows):
        raise SystemExit("monuments mention overlaps an existing mention")

    candidate_rows.append({
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unspecified grander and more public monuments allowed or encouraged for Urban VIII",
        "index_page_range": "",
        "suggested_type": "work",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell describes an unspecified class of grander, more public monuments to Urban VIII. The number and membership of the group are not given. The Velletri bronze statue and Senate-commissioned marble figure remain separately recorded; they are not an exhaustive list, and Urban is not inferred as commissioner of the Senate work.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L120",
    })
    mention_rows.append({
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": "Open group of grander public monuments to Urban VIII; individual works and group membership are unspecified.",
    })

    output: list[bytes] = []
    found = False
    for raw in STATEMENTS.read_bytes().splitlines(keepends=True):
        if not raw.strip():
            output.append(raw)
            continue
        row = json.loads(raw)
        if row.get("statement_id") == STATEMENT_ID:
            q = dict(row.get("qualifiers", {}))
            if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != "cand-0220" or row.get("object_candidate_id") not in (None, "") or q.get("relation_candidate") is not True:
                raise SystemExit("target statement state changed")
            row["object_candidate_id"] = CANDIDATE_ID
            q.pop("open_endpoint_reason", None)
            q["qualification"] = "The source explicitly refers to a general class of grander public monuments to Urban VIII; it does not enumerate the class or state that the two following examples exhaust it."
            q["relation_candidate_note"] = "Use an open work-group candidate for the source’s explicit plural class. Keep the Velletri bronze and Senate-commissioned marble statue separately identified; do not make Urban VIII the latter’s commissioner."
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), CANDIDATE_ID]))
            row["qualifiers"] = q
            found = True
            ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            output.append(raw)
    if not found:
        raise SystemExit("target statement not found")

    updated_candidates = write_csv(candidate_bytes, candidate_headers, candidate_rows)
    updated_mentions = write_csv(mention_bytes, mention_headers, mention_rows)
    updated_statements = b"".join(output)
    counts = (len(candidate_rows), len(mention_rows), sum(bool(line.strip()) for line in updated_statements.splitlines()))
    if counts != (12274, 26466, 15114):
        raise SystemExit(f"projected counts changed: {counts}")
    return {CANDIDATES: updated_candidates, MENTIONS: updated_mentions, STATEMENTS: updated_statements}, (start, end)


def apply(updates: dict[Path, bytes]) -> None:
    if any(path.exists() for path in BACKUPS.values()):
        raise SystemExit("recovery backup already exists")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"file changed after preview: {path.relative_to(ROOT)}")
    for path, backup in BACKUPS.items():
        shutil.copy2(path, backup)
    temporary: dict[Path, Path] = {}
    written: list[Path] = []
    try:
        for path, data in updates.items():
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
                temp_path = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            temporary[path] = temp_path
        for path, temp_path in temporary.items():
            os.replace(temp_path, path)
            written.append(path)
    except Exception:
        for path in reversed(written):
            shutil.copy2(BACKUPS[path], path)
        raise
    finally:
        for temp_path in temporary.values():
            if temp_path.exists():
                temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updates, (start, end) = build()
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha(path.read_bytes())} -> {sha(data)}")
    print(f"Added open work-group candidate {CANDIDATE_ID}, mention [{start},{end}), linked to {STATEMENT_ID}.")
    print("Projected counts: 12,274 candidates, 26,466 mentions, 15,114 statements; open endpoints 518 -> 517.")
    if args.apply:
        apply(updates)
        print("Applied with recovery backups.")


if __name__ == "__main__":
    main()
