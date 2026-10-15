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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    CANDIDATES: "bd6381a1b34842da10ab29138b10a3daf99d903e1e3775d6355d5735c13a8066",
    MENTIONS: "977df8e921422f2c3340eb0c488b6521a7dace02fc47756a5de6f78b5b08bbe6",
    STATEMENTS: "bff63186a689c49fc687393d1956a29ec07dfa971640754f0369b871bc014beb",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-strozzi-rucellai-chapels-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l124-157"
CANDIDATE_ID = "cand-12289"
MENTION_ID = "m-chp2-seci-l124-157-other-chapels"
STATEMENT_FAMILIES = {
    "st-chp2-seci-l124-157-strozzi-chapels": "cand-4360",
    "st-chp2-seci-l124-157-rucellai-chapels": "cand-4361",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    return list(reader.fieldnames or []), list(reader)


def append_csv(data: bytes, headers: list[str], row: dict[str, str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n")
    writer.writerow(row)
    ending = b"\r\n" if b"\r\n" in data else b"\n"
    separator = b"" if data.endswith((b"\n", b"\r")) else ending
    return data + separator + buffer.getvalue().encode("utf-8")


def write_csv(data: bytes, headers: list[str], rows: list[dict[str, str]]) -> bytes:
    line_ending = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    return bom + buffer.getvalue().encode("utf-8")


def load_segment() -> str:
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit(f"S0 asset/segment mismatch: {SEGMENT_ID}")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit(f"S0 segment hash mismatch: {SEGMENT_ID}")
    return text


def build() -> tuple[dict[Path, bytes], dict[str, int], tuple[int, int]]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    candidate_bytes = CANDIDATES.read_bytes()
    candidate_headers, candidate_rows = read_csv(candidate_bytes)
    mention_headers, mention_rows = read_csv(MENTIONS.read_bytes())
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    if CANDIDATE_ID in candidates or any(row["mention_id"] == MENTION_ID for row in mention_rows):
        raise SystemExit("new candidate/mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-")) != 12288:
        raise SystemExit("candidate ID sequence changed")

    text = load_segment()
    surface = "Other chapels"
    if text.count(surface) != 1:
        raise SystemExit("source phrase changed")
    start = text.index(surface)
    end = start + len(surface)
    if "belonged to the Strozzi and the Rucellai" not in text[end:end + 60]:
        raise SystemExit("chapel ownership context changed")
    if any(row["segment_id"] == SEGMENT_ID and start < int(row["end_char"]) and end > int(row["start_char"]) for row in mention_rows):
        raise SystemExit("other-chapels mention overlaps an existing mention")

    candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Other chapels associated collectively with the Strozzi and Rucellai families (sites unidentified)",
        "index_page_range": "",
        "suggested_type": "place",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Footnote 6 says other chapels belonged to the Strozzi and the Rucellai. It does not identify or locate individual chapels, give their number, or allocate each chapel to a family. Keep this shared collective distinct from the specifically named Barberini family chapel; ‘Ortolani’ remains a separate ambiguous citation.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L131",
    }
    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": "Collective reference to unspecified chapels attributed to the Strozzi and Rucellai families; individual locations and family allocation are not given.",
    }

    lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    out: list[bytes] = []
    found: set[str] = set()
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in STATEMENT_FAMILIES:
            q = dict(row.get("qualifiers", {}))
            if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") not in (None, "") or row.get("object_candidate_id") != STATEMENT_FAMILIES[statement_id]:
                raise SystemExit(f"chapel-family endpoint state changed: {statement_id}")
            if q.get("relation_candidate") is not True or q.get("source_line_start") != 131:
                raise SystemExit(f"chapel-family classification/source anchor changed: {statement_id}")
            row["subject_candidate_id"] = CANDIDATE_ID
            q.pop("open_endpoint_reason", None)
            q["qualification"] = "The subject is the footnote’s shared, unnamed chapel collective; no individual site, number, or allocation to Strozzi versus Rucellai is supplied."
            q["relation_candidate_note"] = "Footnote 6 collectively associates other unidentified chapels with this family. The same source-defined chapel group is used for both family statements because the note does not map individual sites to each family; no specific chapel or branch is inferred."
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), CANDIDATE_ID]))
            row["qualifiers"] = q
            found.add(statement_id)
            ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
            out.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            out.append(line)
    if found != set(STATEMENT_FAMILIES):
        raise SystemExit(f"target statement set mismatch: {found}")

    updated_candidates = append_csv(candidate_bytes, candidate_headers, candidate)
    mention_rows.append(mention)
    updated_mentions = write_csv(MENTIONS.read_bytes(), mention_headers, mention_rows)
    updated_statements = b"".join(out)
    counts = (
        len(read_csv(updated_candidates)[1]),
        len(read_csv(updated_mentions)[1]),
        sum(bool(line.strip()) for line in updated_statements.splitlines()),
    )
    if counts != (12267, 26459, 15113):
        raise SystemExit(f"projected counts changed: {counts}")
    return {CANDIDATES: updated_candidates, MENTIONS: updated_mentions, STATEMENTS: updated_statements}, {
        "candidates": counts[0], "mentions": counts[1], "statements": counts[2]
    }, (start, end)


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
    updates, counts, (start, end) = build()
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {sha(path.read_bytes())} -> {sha(data)}")
    print(f"Shared chapel group -> {CANDIDATE_ID}; mention [{start},{end}) connects both family statements")
    print(f"projected counts: {counts}; open endpoints 526 -> 524")
    if args.apply:
        apply(updates)
        print("applied with recovery backups")
    else:
        print("preview only; no files or backups written")


if __name__ == "__main__":
    main()
