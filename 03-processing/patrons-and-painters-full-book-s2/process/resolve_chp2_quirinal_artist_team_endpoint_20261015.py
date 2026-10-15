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
    CANDIDATES: "47b3ea3a52700b28e49f61e5932ab0cffa6df692159b9658ac3b2daabd3f54a5",
    MENTIONS: "320797c41296f3a484c2d6f55e64c3864e0a952dc21bb68b963339175e6885d4",
    STATEMENTS: "039103aeea1becf95ca51771cbcb70ec988577e5206b4a2413bc66bbaefd34b6",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp2-quirinal-artist-team-20261015")
    for path in (CANDIDATES, MENTIONS, STATEMENTS)
}
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l71-80"
STATEMENT_ID = "st-chp2-seci-l71-80-quirinal-decoration"
CANDIDATE_ID = "cand-12281"
MENTION_ID = "m-chp2-seci-l71-80-artist-teams"


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


def load_segment() -> tuple[dict, str]:
    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit(f"S0 asset/segment mismatch: {SEGMENT_ID}")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit(f"S0 segment hash mismatch: {SEGMENT_ID}")
    return segment, text


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
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    mention_ids = {row["mention_id"] for row in mention_rows}
    if CANDIDATE_ID in candidate_by_id or MENTION_ID in mention_ids:
        raise SystemExit("new candidate/mention ID already exists")
    if max(int(row["candidate_id"].split("-")[1]) for row in candidate_rows if row["candidate_id"].startswith("cand-")) != 12280:
        raise SystemExit("candidate ID sequence changed")

    _, text = load_segment()
    surface = "teams of artists"
    if text.count(surface) != 1:
        raise SystemExit("Quirinal artist-team phrase changed")
    start = text.index(surface)
    end = start + len(surface)
    if "Quirinal Palace where " not in text[max(0, start - 35):start] or "were at work on the decoration" not in text[end:end + 45]:
        raise SystemExit("Quirinal artist-team context changed")
    if any(row["segment_id"] == SEGMENT_ID and start < int(row["end_char"]) and end > int(row["start_char"]) for row in mention_rows):
        raise SystemExit("artist-team mention overlaps an existing mention")

    candidate = {
        "candidate_id": CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "Unidentified artist teams decorating newly built rooms at the Quirinal Palace",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says teams of artists were at work decorating newly built rooms at the Quirinal Palace. The artists, number of teams, membership, and organizational identity are not supplied; type remains open.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L76",
    }
    mention = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": CANDIDATE_ID,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": "Unnamed teams explicitly said to work on decoration in the newly built Quirinal Palace rooms; members and number are not identified.",
    }

    lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    out: list[bytes] = []
    found = False
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        row = json.loads(line)
        if row.get("statement_id") == STATEMENT_ID:
            q = dict(row.get("qualifiers", {}))
            if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") not in (None, "") or row.get("object_candidate_id") != "cand-4275":
                raise SystemExit("Quirinal statement endpoint state changed")
            if q.get("relation_candidate") is not True or q.get("source_line_start") != 76:
                raise SystemExit("Quirinal statement classification/source anchor changed")
            row["subject_candidate_id"] = CANDIDATE_ID
            q.pop("open_endpoint_reason", None)
            q["qualification"] = "The source-defined subject is an unnamed collective of artist teams; neither membership, team count, nor organizational identity is supplied."
            q["relation_candidate_note"] = "Haskell explicitly says teams of artists worked on decoration in the newly built Quirinal Palace rooms. The source-defined collective is recorded as an open candidate; no members or count are inferred."
            q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), CANDIDATE_ID]))
            row["qualifiers"] = q
            found = True
            ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
            out.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            out.append(line)
    if not found:
        raise SystemExit("target statement missing")

    mention_rows.append(mention)
    updated_mentions = write_csv(MENTIONS.read_bytes(), mention_headers, mention_rows)
    updated_candidates = append_csv(candidate_bytes, candidate_headers, candidate)
    updated_statements = b"".join(out)
    counts = (
        len(read_csv(updated_candidates)[1]),
        len(read_csv(updated_mentions)[1]),
        sum(bool(line.strip()) for line in updated_statements.splitlines()),
    )
    if counts != (12259, 26451, 15113):
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
    print(f"Quirinal decoration subject -> {CANDIDATE_ID}; mention [{start},{end})")
    print(f"projected counts: {counts}; open endpoints 534 -> 533")
    if args.apply:
        apply(updates)
        print("applied with recovery backups")
    else:
        print("preview only; no files or backups written")


if __name__ == "__main__":
    main()
