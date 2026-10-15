#!/usr/bin/env python3
"""Reuse the existing exact-span mention for Correr's unnamed contemporaries."""

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
EXPECTED_SHA256 = "d505599d21edadb0ce2e1b2f8d20f7c711994e3a11127067fec2871e984f0c84"
BACKUP_SUFFIX = ".bak-s2-chp17-p382-contemporaries-mention-fix-20261015"
EXISTING_ID = "m-chp17-p382-0012"
DUPLICATE_ID = "m-chp17-p382-financially-weak-contemporaries-0001"
SEGMENT_ID = "chp-17:17_CHP-17_sec_ii:l7-17"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def serialize(values: list[str], ending: bytes) -> bytes:
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator="").writerow(values)
    return buffer.getvalue().encode("utf-8") + ending


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after preview checks")
    args = parser.parse_args()

    original = TABLE.read_bytes()
    if sha256(original) != EXPECTED_SHA256:
        raise SystemExit("mentions table changed; rebuild the repair preview")
    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    lines = original[len(bom) :].splitlines(keepends=True)
    header = next(csv.reader([lines[0].rstrip(b"\r\n").decode("utf-8")]))
    ix = {name: header.index(name) for name in ("mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note")}
    output = [lines[0]]
    seen_existing = seen_duplicate = False
    for raw in lines[1:]:
        ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
        content = raw[: -len(ending)] if ending else raw
        values = next(csv.reader([content.decode("utf-8")]))
        mention_id = values[ix["mention_id"]]
        if mention_id == DUPLICATE_ID:
            if (values[ix["segment_id"]], values[ix["candidate_id"]], values[ix["surface_form"]], values[ix["start_char"]], values[ix["end_char"]]) != (SEGMENT_ID, "cand-12257", "his contemporaries", "741", "759"):
                raise SystemExit("duplicate mention row differs from reviewed preview")
            seen_duplicate = True
            continue
        if mention_id == EXISTING_ID:
            expected = (SEGMENT_ID, "cand-0857", "his contemporaries", "741", "759")
            actual = tuple(values[ix[key]] for key in ("segment_id", "candidate_id", "surface_form", "start_char", "end_char"))
            if actual != expected:
                raise SystemExit("existing mention row differs from reviewed preview")
            values[ix["candidate_id"]] = "cand-12257"
            values[ix["note"]] = "Unnamed group of Correr's financially vulnerable contemporaries; individuals are not separately identified."
            if serialize(next(csv.reader([content.decode("utf-8")])), ending) != raw:
                raise SystemExit("original CSV row serialization differs; stop for manual review")
            output.append(serialize(values, ending))
            seen_existing = True
            continue
        output.append(raw)
    if not seen_existing or not seen_duplicate:
        raise SystemExit("expected original and duplicate mention rows were not both found")

    updated = bom + b"".join(output)
    preview = {
        "segment_id": SEGMENT_ID,
        "reused_mention_id": EXISTING_ID,
        "candidate_id": "cand-12257",
        "removed_duplicate_mention_id": DUPLICATE_ID,
        "output_sha256": sha256(updated),
        "backup": str(TABLE.with_name(TABLE.name + BACKUP_SUFFIX)),
    }
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
