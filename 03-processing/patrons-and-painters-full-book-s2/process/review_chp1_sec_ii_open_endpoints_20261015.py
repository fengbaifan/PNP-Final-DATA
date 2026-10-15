from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp1-sec-ii-open-endpoints-20261015")
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    TABLE: "d0fb6de1cc802c818ce09d75e12a12e0c36d27f2f5a17520aa29a85d909bee52",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
}
CHANGES = {
    "st-chp1-secii-l3-8-09": (
        "The sentence continues into the next S0 segment as a general account of a sliding scale of court rewards and positions. "
        "The following Andrea Sacchi–Cardinal Antonio Barberini example is recorded separately in "
        "st-chp1-secii-l10-17-01; do not transfer its endpoints to this generalized model."
    ),
    "st-chp1-secii-l10-17-08": (
        "This is a generalized comparison about birthplace and access to servitù particolare. "
        "The specific Pietro da Cortona–Marcello Sacchetti and Francesco Trevisani–Cardinal Ottoboni examples "
        "are recorded separately in st-chp1-secii-l10-17-09 and st-chp1-secii-l10-17-10; do not transfer their endpoints here."
    ),
}
SEGMENT_IDS = {
    "chp-1:01_CHP-1_sec_ii:l3-8",
    "chp-1:01_CHP-1_sec_ii:l10-17",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_jsonl(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8-sig").splitlines() if line.strip()]


def build() -> bytes:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, digest in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != digest:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    segment_rows = {row["segment_id"]: row for row in load_jsonl(SEGMENTS.read_bytes()) if row.get("segment_id") in SEGMENT_IDS}
    if set(segment_rows) != SEGMENT_IDS:
        raise SystemExit("expected S0 segments are missing")
    source_bytes = SOURCE.read_bytes()
    source_text = SOURCE.read_text(encoding="utf-8-sig")
    source_lines = source_text.splitlines()
    for segment_id, segment in segment_rows.items():
        if segment.get("asset_sha256") != sha(source_bytes):
            raise SystemExit(f"S0 asset mismatch: {segment_id}")
        text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
        if sha(text.encode("utf-8")) != segment.get("sha256"):
            raise SystemExit(f"S0 segment mismatch: {segment_id}")

    raw = TABLE.read_bytes()
    lines = raw.splitlines(keepends=True)
    found: dict[str, tuple[int, dict]] = {}
    all_rows: dict[str, dict] = {}
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        row = json.loads(line)
        all_rows[row["statement_id"]] = row
        if row.get("statement_id") in CHANGES:
            found[row["statement_id"]] = (index, row)
    if set(found) != set(CHANGES):
        raise SystemExit("target statements are missing")

    for statement_id, (_, row) in found.items():
        expected_segment = "chp-1:01_CHP-1_sec_ii:l3-8" if statement_id.endswith("l3-8-09") else "chp-1:01_CHP-1_sec_ii:l10-17"
        qualifiers = row.get("qualifiers", {})
        if row.get("segment_id") != expected_segment or row.get("origin") != "book":
            raise SystemExit(f"source mapping changed: {statement_id}")
        if row.get("subject_candidate_id") or row.get("object_candidate_id"):
            raise SystemExit(f"endpoint state changed: {statement_id}")
        if qualifiers.get("relation_candidate") is not True or not qualifiers.get("open_endpoint_reason"):
            raise SystemExit(f"open relation state changed: {statement_id}")

    expected_open = {
        "chp-1:01_CHP-1_sec_ii:l3-8": 9,
        "chp-1:01_CHP-1_sec_ii:l10-17": 8,
    }
    actual_open = {segment_id: 0 for segment_id in expected_open}
    for row in all_rows.values():
        segment_id = row.get("segment_id")
        qualifiers = row.get("qualifiers", {})
        if segment_id in actual_open and qualifiers.get("relation_candidate") is True and (
            not row.get("subject_candidate_id") or not row.get("object_candidate_id")
        ):
            if not qualifiers.get("open_endpoint_reason"):
                raise SystemExit(f"missing open endpoint reason: {row['statement_id']}")
            actual_open[segment_id] += 1
    if actual_open != expected_open:
        raise SystemExit(f"open endpoint counts changed: {actual_open}")

    if all_rows["st-chp1-secii-l10-17-01"].get("subject_candidate_id") != "cand-2998":
        raise SystemExit("Sacchi example mapping changed")
    if not all_rows["st-chp1-secii-l10-17-09"].get("subject_candidate_id") or not all_rows["st-chp1-secii-l10-17-10"].get("subject_candidate_id"):
        raise SystemExit("named birthplace examples are no longer mapped")

    for statement_id, reason in CHANGES.items():
        index, row = found[statement_id]
        print(f"{statement_id} old reason: {row['qualifiers']['open_endpoint_reason']}")
        print(f"{statement_id} new reason: {reason}")
        updated = dict(row)
        qualifiers = dict(row["qualifiers"])
        qualifiers["open_endpoint_reason"] = reason
        updated["qualifiers"] = qualifiers
        ending = b"\r\n" if lines[index].endswith(b"\r\n") else b"\n"
        lines[index] = json.dumps(updated, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending
    return b"".join(lines)


def apply(data: bytes) -> None:
    if BACKUP.exists():
        raise SystemExit(f"recovery backup already exists: {BACKUP.name}")
    if sha(TABLE.read_bytes()) != EXPECTED_HASHES[TABLE]:
        raise SystemExit("statement table changed after preview")
    shutil.copy2(TABLE, BACKUP)
    temp = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False) as handle:
            temp = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, TABLE)
    except Exception:
        shutil.copy2(BACKUP, TABLE)
        raise
    finally:
        if temp and temp.exists():
            temp.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updated = build()
    print("Reviewed 9 open endpoints in l3-8 and 8 in l10-17; all remain open on source evidence.")
    print("Refined two open-endpoint reasons to keep adjacent named examples separate from generalized claims.")
    print(f"book-statements.jsonl: {EXPECTED_HASHES[TABLE]} -> {sha(updated)}")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply(updated)
    print(f"applied with recovery backup {BACKUP.name}")


if __name__ == "__main__":
    main()
