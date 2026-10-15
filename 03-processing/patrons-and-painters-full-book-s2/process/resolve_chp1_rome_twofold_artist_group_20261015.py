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
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l79-84"
STATEMENT_ID = "st-chp1-secii-l79-84-17"
ARTIST_GROUP_ID = "cand-11845"
NEW_MENTION_ID = "m-chp1-secii-rome-twofold-appeal-artists"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    MENTIONS: "549e103532926a24508864224447b3d2993efd347420ccbb3a29ae7e73e25ac5",
    STATEMENTS: "6c12d7a2ee3b513ea6fc505a6e76316be3b39616ce1e3e9f55293477beb9c4e0",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
}
BACKUPS = {
    path: path.with_name(path.name + ".bak-s2-chp1-secii-rome-twofold-artists-20261015")
    for path in (MENTIONS, STATEMENTS)
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


def build() -> dict[Path, bytes]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    segment_rows = [
        json.loads(line)
        for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 asset/segment mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(segment_text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    surface = "artists"
    positions = [i for i in range(len(segment_text)) if segment_text.startswith(surface, i)]
    if len(positions) != 2 or not segment_text.startswith("To artists her appeal", positions[1] - 3):
        raise SystemExit(f"expected the twofold-appeal artist reference, got {positions}")
    start = positions[1]
    end = start + len(surface)

    mention_bytes = MENTIONS.read_bytes()
    mention_headers, mention_rows = read_csv(mention_bytes)
    mention_ids = {row["mention_id"] for row in mention_rows}
    if NEW_MENTION_ID in mention_ids:
        raise SystemExit("new mention ID already exists")
    if any(
        row["segment_id"] == SEGMENT_ID
        and start < int(row["end_char"])
        and end > int(row["start_char"])
        for row in mention_rows
    ):
        raise SystemExit("new mention overlaps an existing mention")

    candidates = {row["candidate_id"]: row for row in read_csv((TABLES / "entity-candidates.csv").read_bytes())[1]}
    artist_group = candidates.get(ARTIST_GROUP_ID)
    if not artist_group or "artists" not in artist_group.get("canonical_name", "").lower():
        raise SystemExit("continuation artist-group candidate changed")
    if "l86-94#L575" not in artist_group.get("candidate_source_ref", ""):
        raise SystemExit("artist-group source anchor changed")

    statement_lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    found = None
    updated_lines: list[bytes] = []
    for line in statement_lines:
        if line.strip():
            row = json.loads(line)
            if row.get("statement_id") == STATEMENT_ID:
                found = row
                if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") != "cand-3126" or row.get("object_candidate_id") not in (None, ""):
                    raise SystemExit("target endpoint state changed")
                q = dict(row.get("qualifiers", {}))
                if q.get("relation_candidate") is not True or q.get("source_line_start") != 561:
                    raise SystemExit("target relation/source anchor changed")
                linked = set(q.get("linked_statement_ids", []))
                if not {"st-chp1-secii-l86-94-01", "st-chp1-secii-l86-94-01b"}.issubset(linked):
                    raise SystemExit("twofold continuation links changed")
                q.pop("open_endpoint_reason", None)
                q["claim"] = "Haskell introduces Rome’s twofold appeal to the artist group described in the immediate continuation; the following statements distinguish aristocratic invitations from artists’ own search for scope and rewards."
                q["qualification"] = "The preceding segment names the artist group; the linked continuation defines its two routes of attraction. This summary relation does not add a separate invitation or migration event."
                q["relation_candidate_note"] = "Rome’s twofold appeal is explicitly directed to artists; the following segment defines the source-group as painters invited by aristocrats and those seeking scope and rewards."
                q["mentioned_candidate_ids"] = list(dict.fromkeys([*q.get("mentioned_candidate_ids", []), ARTIST_GROUP_ID]))
                row["object_candidate_id"] = ARTIST_GROUP_ID
                row["qualifiers"] = q
                ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
                updated_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    if found is None:
        raise SystemExit("target statement missing")

    mention_rows.append({
        "mention_id": NEW_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": ARTIST_GROUP_ID,
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": "The artist group named at the start of Rome’s twofold appeal; the immediate continuation expands this group into two source-defined routes of attraction.",
    })
    updated_mentions = write_csv(mention_bytes, mention_headers, mention_rows)
    updated_statements = b"".join(updated_lines)
    if len(mention_rows) != 26446 or sum(bool(line.strip()) for line in updated_statements.splitlines()) != 15113:
        raise SystemExit("projected table counts changed")
    return {MENTIONS: updated_mentions, STATEMENTS: updated_statements}


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
    updates = build()
    print(f"{STATEMENT_ID}: object -> {ARTIST_GROUP_ID}; add exact mention {NEW_MENTION_ID} [2808,2815)")
    print("scope: resolve only the cross-segment artist-group referent; retain the two following relation statements as its detailed grounds")
    for path, data in updates.items():
        print(f"{path.relative_to(ROOT)}: {EXPECTED_HASHES[path]} -> {sha(data)}")
    print("projected counts: 12,256 candidates; 26,446 mentions; 15,113 statements; open endpoints 539 -> 538")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply(updates)
    print("applied with recovery backups")


if __name__ == "__main__":
    main()
