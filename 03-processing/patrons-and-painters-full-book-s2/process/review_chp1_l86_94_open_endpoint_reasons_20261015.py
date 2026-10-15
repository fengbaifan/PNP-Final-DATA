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
TABLES = ROOT / "04-knowledge" / "tables"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l86-94"
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    STATEMENTS: "051150589198af30907d6709737736ebb2ce872e5cad9825d787df35663fb16f",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
}
BACKUP = STATEMENTS.with_name(STATEMENTS.name + ".bak-s2-chp1-l86-94-open-reasons-20261015")
REASONS = {
    "st-chp1-secii-l86-94-02": "The unnamed family is represented as a source-defined group subject, but the passage supplies no discrete patronage object or episode; Borghese and Barberini illustrate the claimed scale and are not substitute object endpoints.",
    "st-chp1-secii-l86-94-02b": "The source makes a conditional claim about a large group of regularly employed artists; “thrown on to the market” is a labor-market outcome, not a named institution or episode with a distinct object endpoint.",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build() -> bytes:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != EXPECTED_HEAD:
        raise SystemExit("HEAD changed")
    for path, expected in EXPECTED_HASHES.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"hash changed: {path.relative_to(ROOT)}")

    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 asset/segment mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(segment_text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    if "Only the family that actually had its hand in the treasury" not in segment_text or "previously engaged in regular employment" not in segment_text:
        raise SystemExit("expected source claims changed")

    lines = STATEMENTS.read_bytes().splitlines(keepends=True)
    out: list[bytes] = []
    seen: set[str] = set()
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        row = json.loads(line)
        statement_id = row.get("statement_id")
        if statement_id in REASONS:
            if row.get("segment_id") != SEGMENT_ID or row.get("object_candidate_id") not in (None, ""):
                raise SystemExit(f"endpoint state changed: {statement_id}")
            expected_subject = "cand-11856" if statement_id.endswith("-02") else "cand-11849"
            if row.get("subject_candidate_id") != expected_subject:
                raise SystemExit(f"subject candidate changed: {statement_id}")
            q = dict(row.get("qualifiers", {}))
            if q.get("relation_candidate") is not True or not q.get("open_endpoint_reason"):
                raise SystemExit(f"relation/open-reason state changed: {statement_id}")
            q["open_endpoint_reason"] = REASONS[statement_id]
            row["qualifiers"] = q
            ending = b"\r\n" if line.endswith(b"\r\n") else b"\n" if line.endswith(b"\n") else b""
            out.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
            seen.add(statement_id)
        else:
            out.append(line)
    if seen != set(REASONS):
        raise SystemExit(f"target statement set mismatch: {seen}")
    return b"".join(out)


def apply(updated: bytes) -> None:
    if BACKUP.exists():
        raise SystemExit("recovery backup already exists")
    if sha(STATEMENTS.read_bytes()) != EXPECTED_HASHES[STATEMENTS]:
        raise SystemExit("statement table changed after preview")
    shutil.copy2(STATEMENTS, BACKUP)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=STATEMENTS.parent, delete=False) as handle:
            temp_path = Path(handle.name)
            handle.write(updated)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, STATEMENTS)
    except Exception:
        shutil.copy2(BACKUP, STATEMENTS)
        raise
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    updated = build()
    for statement_id, reason in REASONS.items():
        print(f"{statement_id}: clarify missing object endpoint -> {reason}")
    print(f"{STATEMENTS.relative_to(ROOT)}: {EXPECTED_HASHES[STATEMENTS]} -> {sha(updated)}")
    print("preview only; endpoints and counts unchanged")
    if args.preview:
        return
    apply(updated)
    print(f"applied with recovery backup {BACKUP.name}")


if __name__ == "__main__":
    main()
