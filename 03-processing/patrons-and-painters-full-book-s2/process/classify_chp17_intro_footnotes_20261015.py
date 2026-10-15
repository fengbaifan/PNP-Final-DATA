#!/usr/bin/env python3
"""Classify the eight unreviewed S2 statements in the chapter 17 opening notes."""

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_intro.md"
SEGMENT_ID = "chp-17:17_CHP-17_intro:l7-13"
EXPECTED_SEGMENT_HASH = "98be4855ecf5ebcd66425ebb154c0d7288917ce3b6d84856e41e15045e7d3405"
EXPECTED_STATEMENTS_HASH = "0a6c816513664da1cb944a317780f8b5b94f1e3d75bdfb1999494794fbca510c"
BACKUP_SUFFIX = ".bak-s2-chp17-intro-footnotes-20261015"
PENDING = {
    "st-chp17-pi-note1-manfrin-material-status": False,
    "st-chp17-pi-note1-meschini-account": True,
    "st-chp17-pi-note2-correr-manuscript-locator": True,
    "st-chp17-pi-note3-pamphlet-locator": True,
    "st-chp17-pi-note3-unpopularity-assessment": False,
    "st-chp17-pi-note4-1770-archive-locator": True,
    "st-chp17-pi-note5-1786-archive-locator": True,
    "st-chp17-pi-note6-tassini-locator": True,
}
RATIONALES = {
    "st-chp17-pi-note1-manfrin-material-status": (
        "This is Haskell's comment about the publication status of his source material, not a relation "
        "between the named entities."
    ),
    "st-chp17-pi-note1-meschini-account": (
        "Haskell attributes the only general account of Manfrin and his gallery to Meschini and identifies "
        "the cited work and page; this does not independently verify completeness."
    ),
    "st-chp17-pi-note2-correr-manuscript-locator": (
        "The note explicitly locates the cited manuscript at Biblioteca Correr."
    ),
    "st-chp17-pi-note3-pamphlet-locator": (
        "The note explicitly locates the cited pamphlet at Biblioteca Marciana, shelfmark 183.C.89, p.321."
    ),
    "st-chp17-pi-note3-unpopularity-assessment": (
        "This is Haskell's inferred reputational assessment; it identifies no specific social group or "
        "other relation endpoint, and it does not establish dishonesty."
    ),
    "st-chp17-pi-note4-1770-archive-locator": (
        "Haskell explicitly locates the cited 1770 record in the Inquisitori series."
    ),
    "st-chp17-pi-note5-1786-archive-locator": (
        "Haskell's ibid. explicitly locates the cited 1786 record in the same Inquisitori series."
    ),
    "st-chp17-pi-note6-tassini-locator": (
        "The citation attributes the cited edition to the surname-only Tassini author form; identity remains unresolved."
    ),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_output() -> tuple[Path, bytes, dict]:
    path = TABLES / "book-statements.jsonl"
    raw = path.read_bytes()
    if digest(raw) != EXPECTED_STATEMENTS_HASH:
        raise ValueError(f"Stale statement table: {digest(raw)}")

    segment_rows = [
        json.loads(line)
        for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("The chapter 17 footnote segment fingerprint changed.")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if source_lines[7] != (
        "1 Most of the available material about Manfrin is still unpublished and will be referred to as "
        "occasion arises. The only general account of him and his gallery is given by G. A. Meschini, "
        "1806, II, p. 107."
    ):
        raise ValueError("Chapter 17 note 1 text changed.")
    if "8 See, for instance" not in source_lines[9] or "4 Archivio di Stato" not in source_lines[10]:
        raise ValueError("The source lines carrying printed note markers changed.")
    if not source_lines[11].startswith("6 ibid.") or not source_lines[12].startswith("8 Tassini:"):
        raise ValueError("Expected OCR note-marker forms changed.")

    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    body = raw[len(bom) :]
    output: list[bytes] = []
    seen: set[str] = set()
    for raw_line in body.splitlines(keepends=True):
        ending = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n" if raw_line.endswith(b"\n") else b""
        content = raw_line[: -len(ending)] if ending else raw_line
        row = json.loads(content)
        statement_id = row.get("statement_id")
        if statement_id in PENDING:
            q = row.get("qualifiers")
            if not isinstance(q, dict) or q.get("relation_candidate") is not None:
                raise ValueError(f"Target no longer has an unset relation status: {statement_id}")
            if PENDING[statement_id] and (
                not row.get("subject_candidate_id") or not row.get("object_candidate_id")
            ):
                raise ValueError(f"Relation candidate lacks an endpoint: {statement_id}")
            q["relation_candidate"] = PENDING[statement_id]
            q["relation_candidate_note"] = RATIONALES[statement_id]
            output.append(json.dumps(row, ensure_ascii=False).encode("utf-8") + ending)
            seen.add(statement_id)
        else:
            output.append(raw_line)
    if seen != set(PENDING):
        raise ValueError(f"Target set changed: missing {sorted(set(PENDING) - seen)}")

    updated = bom + b"".join(output)
    preview = {
        "segment_id": SEGMENT_ID,
        "statements": len(PENDING),
        "relation_candidate_true": sum(PENDING.values()),
        "relation_candidate_false": sum(not value for value in PENDING.values()),
        "changes": {key: PENDING[key] for key in sorted(PENDING)},
        "output_sha256": digest(updated),
        "backup": str(path.with_name(path.name + BACKUP_SUFFIX)),
    }
    return path, updated, preview


def apply_output(path: Path, data: bytes) -> None:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if backup.exists():
        raise FileExistsError(f"Backup already exists: {backup}")
    shutil.copy2(path, backup)
    temp: Path | None = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temp = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except Exception:
        shutil.copy2(backup, path)
        raise
    finally:
        if temp and temp.exists():
            temp.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    path, data, preview = build_output()
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if args.apply:
        apply_output(path, data)
        print("APPLIED")
    else:
        print("PREVIEW ONLY; no table changed.")


if __name__ == "__main__":
    main()
