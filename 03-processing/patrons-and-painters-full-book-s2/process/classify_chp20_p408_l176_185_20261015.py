#!/usr/bin/env python3
"""Classify the remaining p.408 postscript claims and correct verified OCR."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md"
SEGMENT_ID = "chp-20:20_CHP-20Postscript:l174-185"
SOURCE_SHA256 = "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90"
SEGMENT_SHA256 = "f89e7f29219a2e744feed8dcbec55161f6cff0e71cb6c5059fe4be68314b1fa7"
STATEMENTS_SHA256 = "7118e3b983df1fed91dfd526d6236b63d948a55cf03bbee17e58abc6477509db"
BACKUP_SUFFIX = ".bak-s2-chp20-p408-l176-185-20261015"
TARGET_IDS = {
    "st-chp20-p408-venetian-enlightenment-recent-scholarship",
    "st-chp20-p408-haskell-qualifies-enlightenment-term",
    "st-chp20-p408-byam-shaw-identifies-le-blon",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validating fixed preview inputs")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    original = statement_path.read_bytes()
    if sha256(original) != STATEMENTS_SHA256:
        raise SystemExit("statement table changed; rebuild and review preview")
    if sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("source file changed")
    segments = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("p.408 target segment fingerprint changed")

    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    output: list[bytes] = []
    seen: set[str] = set()
    for raw in original[len(bom) :].splitlines(keepends=True):
        ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
        line = raw[: -len(ending)] if ending else raw
        if not line.strip():
            output.append(raw)
            continue
        row = json.loads(line)
        sid = row.get("statement_id")
        if row.get("segment_id") == SEGMENT_ID and sid in TARGET_IDS:
            seen.add(sid)
            q = row.setdefault("qualifiers", {})
            if q.get("relation_candidate") is not None:
                raise SystemExit(f"statement is no longer unset: {sid}")

            if sid == "st-chp20-p408-venetian-enlightenment-recent-scholarship":
                q["relation_candidate"] = True
                q["relation_candidate_note"] = "Haskell reports recent scholarly attention to the Venetian Enlightenment from two named scholars; this is a secondary-source report, and the cited publications were not independently consulted."
                q["ocr_corrections"] = [
                    {
                        "source_line": 177,
                        "ocr": "oiLodoli",
                        "print": "of Lodoli",
                        "basis": "CHP-20Postscript.pdf physical page 17, printed page 408.",
                    },
                    {
                        "source_line": 178,
                        "ocr": "begji",
                        "print": "been",
                        "basis": "CHP-20Postscript.pdf physical page 17, printed page 408.",
                    },
                ]
            elif sid == "st-chp20-p408-haskell-qualifies-enlightenment-term":
                quote = row["original_quote"]
                start = quote.index("It is now clearer")
                row["original_quote"] = quote[start:]
                q["relation_candidate"] = False
                q["relation_candidate_note"] = "This is Haskell's qualification of his own umbrella term and of unnamed figures; it is an authorial scope statement, not a relation to identified works. The two figures are not assigned by adjacency."
            else:
                quote = row["original_quote"]
                start = quote.index("James Byam Shaw has shown")
                end = quote.index(" And", start)
                row["original_quote"] = quote[start:end].rstrip()
                q["ocr_corrections"] = [
                    correction
                    for correction in q.get("ocr_corrections", [])
                    if correction.get("source_line") != 178
                ]
                q["relation_candidate"] = True
                q["relation_candidate_note"] = "Haskell reports Byam Shaw's identification of Conti's German painter as Le Blon; preserve the attribution and do not treat the cited catalogue as independently checked."
            row["qualifiers"] = q
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
            continue
        output.append(raw)

    if seen != TARGET_IDS:
        raise SystemExit(f"pending statement set changed: missing {sorted(TARGET_IDS-seen)}")
    updated = bom + b"".join(output)
    final_segment = [
        json.loads(line)
        for line in b"".join(output).splitlines()
        if line.strip() and json.loads(line).get("segment_id") == SEGMENT_ID
    ]
    preview = {
        "segment_id": SEGMENT_ID,
        "classified_unset": len(seen),
        "relation_candidate_true_in_segment": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in final_segment),
        "relation_candidate_false_in_segment": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in final_segment),
        "output_sha256": sha256(updated),
        "backup": str(statement_path.with_name(statement_path.name + BACKUP_SUFFIX)),
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backup = statement_path.with_name(statement_path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(statement_path, backup)
    temporary: Path | None = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{statement_path.name}.", suffix=".tmp", dir=statement_path.parent)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, statement_path)
    except Exception:
        shutil.copy2(backup, statement_path)
        raise
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


if __name__ == "__main__":
    main()
