#!/usr/bin/env python3
"""Resolve the p.381 residual claims and atomize the history-painters response."""

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_i.md"
SEGMENT_ID = "chp-17:17_CHP-17_sec_i:l22-24"
EXPECTED_SOURCE_SHA256 = "cbcb4e8f0eb163564f0b0c8e060c79f1a48981db45072a772c3ea16642ad3ca4"
EXPECTED_SEGMENT_SHA256 = "21470b07698f182320d2aa80a55540ce1e98365a1233f6c21397181b75d3dbc6"
EXPECTED_HASHES = {
    "entity-candidates.csv": "b035461967a3bd6cb291c42109203ee87e91e7b5acaea8fa87b6a5adcdcd59ca",
    "mentions.csv": "849998476387ed94a927ef186c54d71e8b599850e9ab8a83c8dd22096b97fcd7",
    "book-statements.jsonl": "097b8a613e9b4d797eff55a23e5ac2c85a51da026178fe76ff6c53727d3a642a",
}
BACKUP_SUFFIX = ".bak-s2-chp17-p381-residual-20261015"
NEW_CANDIDATE_ID = "cand-12254"
NEW_MENTION_ID = "m-chp17-p381-history-painters-group-0001"
NEW_STATEMENT_ID = "st-chp17-p381-competitions-aroused-history-painters"
HISTORY_STATEMENT_ID = "st-chp17-p381-history-painters-response"
COMPETITION_STATEMENT_ID = "st-chp17-p381-manfrin-competitions"

CLASSIFICATIONS = {
    "st-chp17-p381-gallery-evaluation": (
        False,
        "This is Haskell's comparative quality judgment; 'in Venice' identifies the comparison context and does not by itself assert a formal gallery-city relation.",
    ),
    "st-chp17-p381-gallery-tourist-attraction": (
        True,
        "Haskell explicitly describes the gallery as one of Venice's long-standing chief tourist attractions; 'long' and 'one of' remain qualified, and this is an S2 candidate only.",
    ),
    "st-chp17-p381-manfrin-patronage-evaluation": (
        False,
        "This is Haskell's evaluative judgment about the quality and character of Manfrin's patronage, including the author's qualification about the lack of talented painters.",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader), raw


def encode_csv(fields: list[str], rows: list[dict[str, str]], original: bytes) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    return bom + stream.getvalue().encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    temporary: Path | None = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed plan; default is preview only")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    if sha256(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("chapter 17 source asset changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_path = TABLES / "segments.jsonl"
    segments = [json.loads(line) for line in segment_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != EXPECTED_SEGMENT_SHA256 or segment.get("asset_sha256") != EXPECTED_SOURCE_SHA256:
        raise SystemExit("p.381 source-segment fingerprint changed")
    if "history painters starved of commissions" not in source_lines[23]:
        raise SystemExit("the source phrase for the group endpoint changed")

    paths = {name: TABLES / name for name in EXPECTED_HASHES}
    originals = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED_HASHES.items():
        if sha256(originals[name]) != expected:
            raise SystemExit(f"{name} changed; rebuild and review this preview")

    candidate_fields, candidates, candidate_raw = read_csv(paths["entity-candidates.csv"])
    mention_fields, mentions, mention_raw = read_csv(paths["mentions.csv"])
    statement_raw = originals["book-statements.jsonl"]
    statement_bom = b"\xef\xbb\xbf" if statement_raw.startswith(b"\xef\xbb\xbf") else b""
    statement_rows = [json.loads(line) for line in statement_raw.decode("utf-8-sig").splitlines() if line.strip()]
    candidate_ids = {row["candidate_id"] for row in candidates}
    statement_by_id = {row["statement_id"]: row for row in statement_rows}
    mention_ids = {row["mention_id"] for row in mentions}
    expected_unset = set(CLASSIFICATIONS) | {HISTORY_STATEMENT_ID}
    actual_unset = {
        row["statement_id"] for row in statement_rows
        if row.get("segment_id") == SEGMENT_ID
        and row.get("qualifiers", {}).get("relation_candidate") is None
    }
    if actual_unset != expected_unset:
        raise SystemExit(f"p.381 pending statement set changed: {sorted(actual_unset)}")
    if NEW_CANDIDATE_ID in candidate_ids or NEW_MENTION_ID in mention_ids or NEW_STATEMENT_ID in statement_by_id:
        raise SystemExit("a planned candidate, mention, or statement ID already exists")
    if HISTORY_STATEMENT_ID not in statement_by_id or COMPETITION_STATEMENT_ID not in statement_by_id:
        raise SystemExit("the p.381 competition or response statement is missing")

    candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "History painters starved of commissions (unnamed group, p.381)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell identifies history painters lacking commissions as the group whose enthusiasm was aroused by Manfrin's competitions; individuals and particular commissions are not named.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L24",
    }
    candidates.append(candidate)

    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    surface = "history painters starved of commissions"
    local_start = source_lines[23].index(surface)
    start_char = sum(len(source_lines[index]) + 1 for index in range(segment["line_start"] - 1, 23)) + local_start
    end_char = start_char + len(surface)
    if segment_text[start_char:end_char] != surface:
        raise SystemExit("the group mention offset does not reproduce the exact source text")
    for row in mentions:
        if row["segment_id"] != SEGMENT_ID:
            continue
        old_start, old_end = int(row["start_char"]), int(row["end_char"])
        if start_char < old_end and old_start < end_char:
            nested = (start_char <= old_start and old_end <= end_char) or (old_start <= start_char and end_char <= old_end)
            if not nested or (start_char, end_char) == (old_start, old_end):
                raise SystemExit(f"group mention overlaps existing mention {row['mention_id']}")
    mention = {
        "mention_id": NEW_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": NEW_CANDIDATE_ID,
        "surface_form": surface,
        "start_char": str(start_char),
        "end_char": str(end_char),
        "note": "Unnamed source-defined group; no members or particular commissions are identified.",
    }
    mentions.append(mention)

    updated_rows: list[dict] = []
    for row in statement_rows:
        statement_id = row.get("statement_id")
        if statement_id in CLASSIFICATIONS:
            status, note = CLASSIFICATIONS[statement_id]
            row["qualifiers"]["relation_candidate"] = status
            row["qualifiers"]["relation_candidate_note"] = note
        elif statement_id == HISTORY_STATEMENT_ID:
            qualifiers = row["qualifiers"]
            row["predicate"] = "competitions_not_basis_for_posterity_gratitude"
            row["subject_candidate_id"] = "cand-1512"
            row["object_candidate_id"] = None
            row["original_quote"] = "it is hardly this that has entitled him to the gratitude of posterity."
            qualifiers.update({
                "claim": "Haskell says Manfrin's competitions were hardly what entitled him to posterity's gratitude.",
                "text_layer": "authorial evaluation",
                "qualification": "This is Haskell's retrospective assessment; 'this' refers to the competitions recorded in the preceding statement, not to a named audience relation.",
                "mentioned_candidate_ids": ["cand-1512", "cand-0817"],
                "relation_candidate": False,
                "relation_candidate_note": "The sentence evaluates the competitions' place in Manfrin's later reputation; 'posterity' is an undefined retrospective audience, not a bounded relation endpoint.",
                "cross_reference_statement_ids": [COMPETITION_STATEMENT_ID],
                "cross_reference_text": "The phrase 'this' refers to Manfrin's competitions in the immediately preceding sentence.",
            })
        updated_rows.append(row)
        if statement_id == COMPETITION_STATEMENT_ID:
            updated_rows.append({
                "statement_id": NEW_STATEMENT_ID,
                "segment_id": SEGMENT_ID,
                "subject_candidate_id": "cand-0817",
                "object_candidate_id": NEW_CANDIDATE_ID,
                "predicate": "competitions_aroused_enthusiasm_among_history_painters",
                "qualifiers": {
                    "source_line_start": 24,
                    "source_line_end": 24,
                    "printed_page": 381,
                    "pdf_physical_page": 3,
                    "claim": "Haskell says Manfrin's competitions aroused enthusiasm among history painters starved of commissions.",
                    "speaker": "Haskell",
                    "text_layer": "authorial report",
                    "qualification": "The group is unnamed and defined here by its lack of commissions; the response is Haskell's report, with no individual painters or particular commissions identified.",
                    "mentioned_candidate_ids": ["cand-1512", "cand-0817", NEW_CANDIDATE_ID],
                    "relation_candidate": True,
                    "relation_candidate_note": "Haskell reports a response by a source-defined group to Manfrin's competitions; preserve the unnamed group and do not infer members or specific commissions.",
                },
                "original_quote": "But despite the enthusiasm aroused among history painters starved of commissions",
                "origin": "book",
                "source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md",
            })

    quote_by_id = {row["statement_id"]: row.get("original_quote", "") for row in updated_rows}
    for sid in (HISTORY_STATEMENT_ID, NEW_STATEMENT_ID):
        quote = quote_by_id[sid]
        if quote not in source_lines[23]:
            raise SystemExit(f"reviewed quote is not an exact p.381 source substring: {sid}")

    candidate_bytes = encode_csv(candidate_fields, candidates, candidate_raw)
    mention_bytes = encode_csv(mention_fields, mentions, mention_raw)
    statement_bytes = statement_bom + "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in updated_rows
    ).encode("utf-8")
    preview = {
        "segment_id": SEGMENT_ID,
        "remaining_statements_classified": len(expected_unset),
        "new_statement": NEW_STATEMENT_ID,
        "new_candidate": NEW_CANDIDATE_ID,
        "new_mention": {"id": NEW_MENTION_ID, "surface": surface, "span": [start_char, end_char]},
        "planned_counts": {
            "statements": len(updated_rows),
            "relation_candidate_true_in_segment": sum(row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is True for row in updated_rows),
            "relation_candidate_false_in_segment": sum(row.get("segment_id") == SEGMENT_ID and row.get("qualifiers", {}).get("relation_candidate") is False for row in updated_rows),
            "candidates": len(candidates),
            "mentions": len(mentions),
        },
        "output_sha256": {"entity-candidates.csv": sha256(candidate_bytes), "mentions.csv": sha256(mention_bytes), "book-statements.jsonl": sha256(statement_bytes)},
        "backups": {name: str(path.with_name(path.name + BACKUP_SUFFIX)) for name, path in paths.items()},
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = {name: path.with_name(path.name + BACKUP_SUFFIX) for name, path in paths.items()}
    existing = [str(path) for path in backups.values() if path.exists()]
    if existing:
        raise SystemExit(f"refusing to overwrite existing backup(s): {existing}")
    for name, path in paths.items():
        shutil.copy2(path, backups[name])
    outputs = {
        "entity-candidates.csv": candidate_bytes,
        "mentions.csv": mention_bytes,
        "book-statements.jsonl": statement_bytes,
    }
    try:
        for name, path in paths.items():
            atomic_write(path, outputs[name])
    except Exception:
        for name, path in paths.items():
            shutil.copy2(backups[name], path)
        raise
    print("Applied p.381 classification and atomization with three recovery backups.")


if __name__ == "__main__":
    main()
