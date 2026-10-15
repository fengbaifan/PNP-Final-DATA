#!/usr/bin/env python3
"""Classify the eight remaining p.380 S2 relation candidates; preview by default."""

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
SEGMENT_ID = "chp-17:17_CHP-17_sec_i:l8-20"
EXPECTED_SOURCE_SHA256 = "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4"
EXPECTED_SEGMENT_SHA256 = "4f3a9cd680dade7a13248a16b40639912ff4102640ab23f823e1bf72f20c2f83"
EXPECTED_STATEMENTS_SHA256 = "e3db878c999e2129f958306911f9288f2ef686a4a247b6827793cc3e1c7a9fd0"
BACKUP_SUFFIX = ".bak-s2-chp17-p380-residual-20261015"

CLASSIFICATIONS = {
    "st-chp17-p380-manfrin-death-rumour-reaches-bologna": (
        False,
        "The reported false rumour is a narrative event and no relation between Manfrin and Bologna is asserted; Armanni's response is recorded separately.",
    ),
    "st-chp17-p380-armanni-calls-manfrin-venices-only-art-spender": (
        False,
        "This is Armanni's attributed characterization of Manfrin, not a distinct historical relation; the concrete letter from Armanni to Sasso is recorded separately.",
    ),
    "st-chp17-p380-manfrin-forefront-until-1802": (
        False,
        "'In the forefront' is Haskell's qualitative career assessment; the phrase does not establish a specific relation to the city of Venice or an identified art-world group.",
    ),
    "st-chp17-p380-gallery-apparent-historical-survey": (
        True,
        "This preserves Haskell's qualified interpretation of the gallery's historical program and its relation to Italian and, to some extent, Flemish painting; it is an S2 relation candidate, not a verified intention or formal S6 edge.",
    ),
    "st-chp17-p380-manfrin-few-connoisseurship-pretensions": (
        False,
        "This is Haskell's qualified personal characterization of Manfrin in private, not a relation between distinct entities.",
    ),
    "st-chp17-p380-manfrin-prioritized-highest-quality": (
        False,
        "The quoted letter states a collecting preference, but identifies no particular work or completed selection relation; the separate adviser and delegated-selection claims retain the supported relations.",
    ),
    "st-chp17-p380-haskell-snobbishness-characterization": (
        False,
        "This is Haskell's evaluative interpretation of Manfrin's words, not a historical relation between distinct entities.",
    ),
    "st-chp17-p380-gallery-choice-quasi-national-status": (
        False,
        "'Some of the definitive status' is an interpretive analogy, not a claim that the gallery was a national institution or had a formal institutional relation.",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validating the fixed preview inputs")
    args = parser.parse_args()

    source_path = SOURCE
    statement_path = TABLES / "book-statements.jsonl"
    segment_path = TABLES / "segments.jsonl"
    source_bytes = source_path.read_bytes()
    original = statement_path.read_bytes()
    if sha256(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("Chapter 17 source asset changed")
    if sha256(original) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("Statement table changed; rebuild and review this preview")

    segments = [
        json.loads(line)
        for line in segment_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_SHA256:
        raise SystemExit("p.380 segment fingerprint changed")

    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    output: list[bytes] = []
    found: set[str] = set()
    before_statuses: dict[str, object] = {}
    for raw_line in original[len(bom):].splitlines(keepends=True):
        ending = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n" if raw_line.endswith(b"\n") else b""
        content = raw_line[:-len(ending)] if ending else raw_line
        row = json.loads(content)
        statement_id = row.get("statement_id")
        if statement_id not in CLASSIFICATIONS:
            output.append(raw_line)
            continue
        if row.get("segment_id") != SEGMENT_ID:
            raise SystemExit(f"statement moved to another segment: {statement_id}")
        qualifiers = row.get("qualifiers")
        if not isinstance(qualifiers, dict) or qualifiers.get("relation_candidate") is not None:
            raise SystemExit(f"statement is no longer unset: {statement_id}")
        if not row.get("original_quote") or not row.get("source_file", "").startswith("02-sources/"):
            raise SystemExit(f"missing source anchor: {statement_id}")
        qualifiers["relation_candidate"] = CLASSIFICATIONS[statement_id][0]
        qualifiers["relation_candidate_note"] = CLASSIFICATIONS[statement_id][1]
        output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        found.add(statement_id)
        before_statuses[statement_id] = None

    if found != set(CLASSIFICATIONS):
        raise SystemExit(f"pending statement set changed; missing {sorted(set(CLASSIFICATIONS) - found)}")

    updated = bom + b"".join(output)
    if updated == original:
        raise SystemExit("no output changes planned")
    preview = {
        "segment_id": SEGMENT_ID,
        "classified": len(found),
        "relation_candidate_true": sum(value for value, _ in CLASSIFICATIONS.values()),
        "relation_candidate_false": sum(not value for value, _ in CLASSIFICATIONS.values()),
        "classifications": {key: value for key, (value, _) in CLASSIFICATIONS.items()},
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
    temp: Path | None = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{statement_path.name}.", suffix=".tmp", dir=statement_path.parent)
        temp = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, statement_path)
    except Exception:
        shutil.copy2(backup, statement_path)
        raise
    finally:
        if temp and temp.exists():
            temp.unlink()


if __name__ == "__main__":
    main()
