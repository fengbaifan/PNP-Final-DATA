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
SEGMENT_ID = "chp-1:01_CHP-1_sec_ii:l40-46"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp1-market-open-endpoints-20261015")
EXPECTED_HEAD = "c65900801de1cb3af9089345250774161d67f5c9"
EXPECTED_HASHES = {
    TABLE: "8d39f4d40a20cb1f70b7c4042ab443285c8572e125838ba154ff0e4764ad8dd8",
    SEGMENTS: "ea19c1f482c86e80605af1d37562cb42248e78509a0ac77aacc3cbd88a50a036",
    SOURCE: "1b5890ce028c421718abcb28e4c6dc4070be1bc71597a96247b32ebee42e2268",
}
CHANGES = {
    "st-chp1-secii-l40-46-07": (
        "The claim is a generalized market pattern, not a particular sale or acquisition. "
        "The named Giustiniani acquisition and Adamo–Piola commission are separately recorded in "
        "st-chp1-secii-l40-46-08 and st-chp1-secii-l40-46-09; do not transfer their endpoints to this summary."
    ),
    "st-chp1-secii-l40-46-10": (
        "This is a generalized patron strategy. The Duke of Mantua’s inferred Samson scheme and the Marchese del Carpio "
        "commission are separately recorded in st-chp1-secii-l40-46-11 and st-chp1-secii-l40-46-13-del-carpio-commission; "
        "Alexander the Great is a subject-matter example here, not an endpoint."
    ),
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

    segment = next((row for row in load_jsonl(SEGMENTS.read_bytes()) if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("asset_sha256") != sha(SOURCE.read_bytes()):
        raise SystemExit("S0 asset/segment mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1:int(segment["line_end"])])
    if sha(text.encode("utf-8")) != segment.get("sha256"):
        raise SystemExit("S0 segment hash mismatch")
    for phrase in ("Marchese Giustiniani", "Giovanni Adamo", "Duke of Mantua", "Marchese del Carpio"):
        if phrase not in text:
            raise SystemExit(f"adjacent named example missing from S0: {phrase}")

    lines = TABLE.read_bytes().splitlines(keepends=True)
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
        raise SystemExit("target statement set changed")
    for statement_id, (_, row) in found.items():
        q = row.get("qualifiers", {})
        if row.get("segment_id") != SEGMENT_ID or row.get("subject_candidate_id") or row.get("object_candidate_id"):
            raise SystemExit(f"statement endpoints/source changed: {statement_id}")
        if q.get("relation_candidate") is not True or not q.get("open_endpoint_reason"):
            raise SystemExit(f"open relation state changed: {statement_id}")
    for supporting_id in (
        "st-chp1-secii-l40-46-08", "st-chp1-secii-l40-46-09",
        "st-chp1-secii-l40-46-11", "st-chp1-secii-l40-46-13-del-carpio-commission",
    ):
        row = all_rows.get(supporting_id)
        if not row or not row.get("subject_candidate_id") or not row.get("object_candidate_id"):
            raise SystemExit(f"named-example statement is not resolved: {supporting_id}")

    for statement_id, reason in CHANGES.items():
        index, row = found[statement_id]
        print(f"{statement_id} old reason: {row['qualifiers']['open_endpoint_reason']}")
        print(f"{statement_id} new reason: {reason}")
        updated = dict(row)
        q = dict(row["qualifiers"])
        q["open_endpoint_reason"] = reason
        updated["qualifiers"] = q
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
    print("Reviewed 2 open generalizations; both remain open and their named cases stay in separate statements.")
    print(f"book-statements.jsonl: {EXPECTED_HASHES[TABLE]} -> {sha(updated)}")
    if args.preview:
        print("preview only; no files or backups written")
        return
    apply(updated)
    print(f"applied with recovery backup {BACKUP.name}")


if __name__ == "__main__":
    main()
