#!/usr/bin/env python3
"""Classify the p.382 Correr collection segment; preview by default."""

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
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_ii.md"
SEGMENT_ID = "chp-17:17_CHP-17_sec_ii:l7-17"
SOURCE_SHA256 = "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3"
SEGMENT_SHA256 = "f1b591c03376bdcb6f4d66321dac8a976bad66006b8d284ba5224ce84ef250a6"
STATEMENTS_SHA256 = "03dbbe644ef3e5ceb6530347cde30dae037ebc413a170b21a3cfb2392ca6800d"
CANDIDATES_SHA256 = "a7ef1ffa25f5566a7af5f9162f718975ef1cbefcc466444596f22229ab062677"
MENTIONS_SHA256 = "84f14eee0de7300277bc18762b19991d2def7310906b9a28d9dcd93890ad5a4a"
BACKUP_SUFFIX = ".bak-s2-chp17-p382-correr-20261015"

CLASSIFICATIONS = {
    "st-chp17-p382-correr-services-to-venice": (
        True,
        "The person-to-city service relation is explicit; the comparative value judgment belongs to Haskell, and this sentence does not name specific services.",
    ),
    "st-chp17-p382-correr-collection-beginnings": (
        True,
        "This is a person-to-collection relation with Haskell's uncertainty and probability retained; no start date is inferred.",
    ),
    "st-chp17-p382-correr-commissioning-living-artists": (
        True,
        "This is a qualified negative commissioning claim with an open source-defined artist-group endpoint. Note 2 allows an occasional direct purchase from Pietro Longhi but does not establish a commission.",
    ),
    "st-chp17-p382-correr-financial-weakness-exploitation": (
        True,
        "Haskell asserts an action by Correr toward his financially vulnerable contemporaries; the group is retained as unnamed and unbounded at individual level, and 'ruthless' remains Haskell's evaluation.",
    ),
    "st-chp17-p382-correr-attended-sales": (
        False,
        "This reports attendance at generic sales and public auctions without identifying a particular event or counterparty.",
    ),
    "st-chp17-p382-correr-collecting-aim": (
        True,
        "The claim connects Correr's collection to Venice's history and cultural achievements; the list of collected material is not treated as exhaustive.",
    ),
    "st-chp17-p382-correr-taste-criticism": (
        False,
        "The statement summarizes unnamed contemporaries' and nineteenth-century writers' critical views; no bounded author or work endpoint is identified.",
    ),
    "st-chp17-p382-correr-collected-unfashionable-periods": (
        True,
        "This describes what Correr collected and when those periods were unfashionable; the claim remains attributed to Haskell and does not identify every work.",
    ),
    "st-chp17-p382-correr-owned-inferior-paintings": (
        True,
        "This is a collection-content relation; the qualitative ranking and relative count remain Haskell's assessment, not independently verified measurements.",
    ),
    "st-chp17-p382-correr-historical-curiosity": (
        False,
        "This is Haskell's qualified account of Correr's motive, not a relation between independently represented entities.",
    ),
    "st-chp17-p382-correr-awareness-of-venice-change": (
        True,
        "Haskell's 'it almost seems' presents a speculative Correr-to-Venice interpretation; preserve it as a qualified relation candidate, not as Correr's own stated motive.",
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12257",
        "index_entry_id": "",
        "canonical_name": "Correr's financially vulnerable contemporaries (unnamed group, p.382)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Correr took advantage of financial weakness among his contemporaries. Individuals and group boundaries are not supplied; this source-bound group candidate preserves the relation without inventing members or a taxonomy type.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L10",
    },
    {
        "candidate_id": "cand-12258",
        "index_entry_id": "",
        "canonical_name": "Living artists in Correr's qualified commissioning claim (unnamed group, p.382)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell considers it unlikely Correr commissioned work from living artists. Note 2 says an occasional direct purchase from Pietro Longhi is possible; it does not identify any commission or member of this source-defined group.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L10",
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-chp17-p382-financially-weak-contemporaries-0001",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12257",
        "surface_form": "his contemporaries",
        "start_char": "387",
        "end_char": "405",
        "note": "Unnamed source-defined group toward whom Correr is said to have acted; individuals are not identified.",
    },
    {
        "mention_id": "m-chp17-p382-living-artists-0001",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12258",
        "surface_form": "living artists",
        "start_char": "122",
        "end_char": "136",
        "note": "Open group endpoint in Haskell's qualified negative commissioning claim.",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_append(data: bytes, rows: list[dict[str, str]]) -> bytes:
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    text = data[len(bom) :].decode("utf-8")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fieldnames = reader.fieldnames
    if not fieldnames:
        raise SystemExit("CSV header is missing")
    newline = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator=newline).writerows(rows)
    addition = buffer.getvalue().encode("utf-8")
    body = data[len(bom) :]
    if body and not body.endswith((b"\n", b"\r")):
        body += newline.encode()
    return bom + body + addition


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validating fixed preview inputs")
    args = parser.parse_args()

    source_path = SOURCE
    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    originals = {path: path.read_bytes() for path in (statement_path, candidate_path, mention_path)}
    expected = {
        source_path: SOURCE_SHA256,
        statement_path: STATEMENTS_SHA256,
        candidate_path: CANDIDATES_SHA256,
        mention_path: MENTIONS_SHA256,
    }
    for path, fingerprint in expected.items():
        if sha256(path.read_bytes()) != fingerprint:
            raise SystemExit(f"input changed; rebuild and review preview: {path.relative_to(ROOT)}")
    segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("p.382 segment fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if source_lines[9][363:405] != "financial weaknesses of his contemporaries" or source_lines[9][122:136] != "living artists":
        raise SystemExit("new mention spans do not match the source line")

    candidate_text = originals[candidate_path][3:].decode("utf-8")
    candidate_rows = list(csv.DictReader(io.StringIO(candidate_text, newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    new_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if candidate_ids.intersection(new_candidate_ids) or new_candidate_ids != {"cand-12257", "cand-12258"}:
        raise SystemExit("new candidate IDs collide or differ from the reviewed set")
    mention_text = originals[mention_path][3:].decode("utf-8")
    mention_rows = list(csv.DictReader(io.StringIO(mention_text, newline="")))
    mention_ids = {row["mention_id"] for row in mention_rows}
    if mention_ids.intersection(row["mention_id"] for row in NEW_MENTIONS):
        raise SystemExit("new mention ID already exists")

    bom = b"\xef\xbb\xbf" if originals[statement_path].startswith(b"\xef\xbb\xbf") else b""
    output: list[bytes] = []
    seen: set[str] = set()
    for raw in originals[statement_path][len(bom) :].splitlines(keepends=True):
        ending = b"\n" if raw.endswith(b"\n") else b""
        row = json.loads(raw[:-1] if ending else raw)
        sid = row.get("statement_id")
        if row.get("segment_id") == SEGMENT_ID and sid in CLASSIFICATIONS:
            qualifiers = row.get("qualifiers") or {}
            if qualifiers.get("relation_candidate") is not None:
                raise SystemExit(f"statement is no longer unset: {sid}")
            status, note = CLASSIFICATIONS[sid]
            qualifiers["relation_candidate"] = status
            qualifiers["relation_candidate_note"] = note
            if sid == "st-chp17-p382-correr-commissioning-living-artists":
                row["object_candidate_id"] = "cand-12258"
                mentions = qualifiers.get("mentioned_candidate_ids", [])
                if "cand-12258" not in mentions:
                    mentions.append("cand-12258")
                    qualifiers["mentioned_candidate_ids"] = mentions
            elif sid == "st-chp17-p382-correr-financial-weakness-exploitation":
                row["object_candidate_id"] = "cand-12257"
                mentions = qualifiers.get("mentioned_candidate_ids", [])
                if "cand-12257" not in mentions:
                    mentions.append("cand-12257")
                    qualifiers["mentioned_candidate_ids"] = mentions
            row["qualifiers"] = qualifiers
            seen.add(sid)
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
        else:
            output.append(raw)
    if seen != set(CLASSIFICATIONS):
        raise SystemExit(f"pending statement set changed; missing {sorted(set(CLASSIFICATIONS) - seen)}")

    updated = {
        statement_path: bom + b"".join(output),
        candidate_path: csv_append(originals[candidate_path], NEW_CANDIDATES),
        mention_path: csv_append(originals[mention_path], NEW_MENTIONS),
    }
    preview = {
        "segment_id": SEGMENT_ID,
        "classified": len(seen),
        "relation_candidate_true": sum(value for value, _ in CLASSIFICATIONS.values()),
        "relation_candidate_false": sum(not value for value, _ in CLASSIFICATIONS.values()),
        "added_candidates": sorted(new_candidate_ids),
        "added_mentions": [row["mention_id"] for row in NEW_MENTIONS],
        "output_sha256": {path.name: sha256(data) for path, data in updated.items()},
        "backups": {path.name: str(path.with_name(path.name + BACKUP_SUFFIX)) for path in updated},
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in updated}
    if any(path.exists() for path in backups.values()):
        raise SystemExit("one or more backup paths already exist")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    temporaries: dict[Path, Path] = {}
    try:
        for path, data in updated.items():
            fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
            temporary = Path(name)
            temporaries[path] = temporary
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        for path, temporary in temporaries.items():
            os.replace(temporary, path)
    except Exception:
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    finally:
        for temporary in temporaries.values():
            if temporary.exists():
                temporary.unlink()


if __name__ == "__main__":
    main()
