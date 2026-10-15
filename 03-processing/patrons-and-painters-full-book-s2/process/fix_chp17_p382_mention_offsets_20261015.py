#!/usr/bin/env python3
"""Repair two p.382 mention offsets to use segment-relative coordinates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_ii.md"
SEGMENT_ID = "chp-17:17_CHP-17_sec_ii:l7-17"
EXPECTED_TABLE_SHA256 = "99be3f38a0a95dbcf25a3ecc2b1b20740f8d1c940f8afe404f47570b04c74d4b"
EXPECTED_SOURCE_SHA256 = "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3"
EXPECTED_SEGMENT_SHA256 = "f1b591c03376bdcb6f4d66321dac8a976bad66006b8d284ba5224ce84ef250a6"
BACKUP_SUFFIX = ".bak-s2-chp17-p382-mention-offset-fix-20261015"
FIXES = {
    "m-chp17-p382-financially-weak-contemporaries-0001": ("387", "405", "741", "759", "his contemporaries"),
    "m-chp17-p382-living-artists-0001": ("122", "136", "476", "490", "living artists"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def serialize_row(values: list[str], ending: bytes) -> bytes:
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator="").writerow(values)
    return buffer.getvalue().encode("utf-8") + ending


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after preview checks")
    args = parser.parse_args()

    original = TABLE.read_bytes()
    source = SOURCE.read_bytes()
    if sha256(original) != EXPECTED_TABLE_SHA256:
        raise SystemExit("mentions table changed; rerun the audit and review current rows")
    if sha256(source) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("source asset changed")
    segments = [json.loads(line) for line in (ROOT / "04-knowledge/tables/segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_SHA256 or segment.get("asset_sha256") != EXPECTED_SOURCE_SHA256:
        raise SystemExit("source segment fingerprint changed")

    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    lines = original[len(bom) :].splitlines(keepends=True)
    header_line = lines[0].rstrip(b"\r\n").decode("utf-8")
    header = next(csv.reader([header_line]))
    id_i, seg_i = header.index("mention_id"), header.index("segment_id")
    surface_i, start_i, end_i = header.index("surface_form"), header.index("start_char"), header.index("end_char")
    output = [lines[0]]
    seen: set[str] = set()
    changes: list[dict[str, str]] = []
    for raw in lines[1:]:
        ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
        content = raw[: -len(ending)] if ending else raw
        values = next(csv.reader([content.decode("utf-8")]))
        mention_id = values[id_i]
        if mention_id not in FIXES:
            output.append(raw)
            continue
        if values[seg_i] != SEGMENT_ID:
            raise SystemExit(f"mention is not in target segment: {mention_id}")
        old_start, old_end, new_start, new_end, expected_surface = FIXES[mention_id]
        if (values[start_i], values[end_i], values[surface_i]) != (old_start, old_end, expected_surface):
            raise SystemExit(f"unexpected current mention row: {mention_id}")
        candidate = values.copy()
        candidate[start_i], candidate[end_i] = new_start, new_end
        serialized = serialize_row(candidate, ending)
        if serialize_row(values, ending) != raw:
            raise SystemExit(f"CSV row serialization differs from original: {mention_id}")
        output.append(serialized)
        changes.append({"mention_id": mention_id, "surface_form": expected_surface, "old_span": f"{old_start}:{old_end}", "new_span": f"{new_start}:{new_end}"})
        seen.add(mention_id)
    if seen != set(FIXES):
        raise SystemExit(f"target mention set changed; missing {sorted(set(FIXES) - seen)}")
    updated = bom + b"".join(output)
    preview = {"segment_id": SEGMENT_ID, "changes": changes, "output_sha256": sha256(updated), "backup": str(TABLE.with_name(TABLE.name + BACKUP_SUFFIX))}
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(TABLE, backup)
    temporary: Path | None = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{TABLE.name}.", suffix=".tmp", dir=TABLE.parent)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, TABLE)
    except Exception:
        shutil.copy2(backup, TABLE)
        raise
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


if __name__ == "__main__":
    main()
