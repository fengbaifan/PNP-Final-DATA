#!/usr/bin/env python3
"""Classify the remaining p.380-p.381 footnote statements; preview by default."""

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
SEGMENT_ID = "chp-17:17_CHP-17_sec_i:l26-35"
EXPECTED_SOURCE_SHA256 = "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4"
EXPECTED_SEGMENT_SHA256 = "b7ee0285d3a437cbf212342c2367ffaef8a3419d6472837e7c35c8e5fe393784"
EXPECTED_STATEMENTS_SHA256 = "4dc703f9870efe360e6e022354ca6da69f6b37d785809c96e0f1c6c4de044265"
BACKUP_SUFFIX = ".bak-s2-chp17-p380-p381-notes-20261015"

CLASSIFICATIONS = {
    "st-chp17-p380-note1-armanni-sasso-letter-locator": (
        True,
        "The note explicitly locates the dated Armanni-Sasso letter in Seminario Patriarcale MSS. 566; the manuscript remains unconsulted.",
    ),
    "st-chp17-p380-note3-portrait-volume-locator": (
        True,
        "The note gives Biblioteca Correr and Stampe D.30 as the cited volume's repository locator; the item and current shelfmark were not checked.",
    ),
    "st-chp17-p380-note4-meschini-gallery-description": (
        True,
        "Haskell quotes Meschini's description of the Manfrin gallery and its historical scope; the cited work was not independently consulted, so this remains a source-attributed candidate.",
    ),
    "st-chp17-p380-note5-edwards-record": (
        True,
        "Haskell attributes the gallery's first record to Pietro Edwards and locates the manuscript in Seminario Patriarcale MSS. 788.13; the manuscript was not consulted.",
    ),
    "st-chp17-p381-note1-moschini-1806": (
        True,
        "The note explicitly cites Moschini, 1806, II, p.107 for the patronage passage; its spelling differs from p.380's Meschini citation at the same volume/page, and the discrepancy is retained pending identity review.",
    ),
    "st-chp17-p381-note1-moschini-1810": (
        True,
        "The note adds an 1810 citation by the same source-named author; title and page are absent, and the work was not consulted.",
    ),
    "st-chp17-p381-note2-catalogue-references": (
        True,
        "The note explicitly directs readers to bibliography and catalogues for Correr and the museum collections; the cited authors/work candidates remain source leads, not independently verified evidence, and the reference list is aggregate.",
    ),
    "st-chp17-p381-note3-portrait-date": (
        False,
        "This is date metadata for the portrait and an unnamed engraving; it does not identify a separate engraving object or engraver. The portrait's creator and the Pignatti citation are recorded in linked statements.",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validating the fixed preview inputs")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    segment_path = TABLES / "segments.jsonl"
    source_bytes = SOURCE.read_bytes()
    original = statement_path.read_bytes()
    if sha256(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("chapter 17 source asset changed")
    if sha256(original) != EXPECTED_STATEMENTS_SHA256:
        raise SystemExit("statement table changed; rebuild and review this preview")
    segments = [json.loads(line) for line in segment_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_SHA256 or segment.get("asset_sha256") != EXPECTED_SOURCE_SHA256:
        raise SystemExit("p.380-p.381 footnote segment fingerprint changed")

    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    output: list[bytes] = []
    seen: set[str] = set()
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
        status, rationale = CLASSIFICATIONS[statement_id]
        qualifiers["relation_candidate"] = status
        qualifiers["relation_candidate_note"] = rationale
        output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        seen.add(statement_id)
    if seen != set(CLASSIFICATIONS):
        raise SystemExit(f"pending note statement set changed; missing {sorted(set(CLASSIFICATIONS) - seen)}")

    updated = bom + b"".join(output)
    preview = {
        "segment_id": SEGMENT_ID,
        "classified": len(seen),
        "relation_candidate_true": sum(status for status, _ in CLASSIFICATIONS.values()),
        "relation_candidate_false": sum(not status for status, _ in CLASSIFICATIONS.values()),
        "classifications": {key: status for key, (status, _) in CLASSIFICATIONS.items()},
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
