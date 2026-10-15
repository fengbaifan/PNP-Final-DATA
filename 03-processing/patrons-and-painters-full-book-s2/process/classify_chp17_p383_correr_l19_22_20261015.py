#!/usr/bin/env python3
"""Classify the p.383 Correr passage; preview by default."""

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
SEGMENT_ID = "chp-17:17_CHP-17_sec_ii:l19-22"
SOURCE_SHA256 = "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3"
SEGMENT_SHA256 = "4ef9f0d9870a51255d3704380b45e3c0bf47992d7f81510a14cc29d6de59130d"
STATEMENTS_SHA256 = "7c9b597076b47b33fb008fcfb2739429fdadf7b018f0ae6bd10617b23840289f"
CANDIDATES_SHA256 = "cde2ec235f1a0f7b0f0fe1e73d1ea7794fcadcb9822409cdbac4cca0c24d60bc"
MENTIONS_SHA256 = "2d2c1f20f2f02c86d9f8eee0b99f29508d7d2d429e228fb648edab66bb48fff4"
BACKUP_SUFFIX = ".bak-s2-chp17-p383-correr-20261015"

CLASSIFICATIONS = {
    "st-chp17-p383-ridotto-room-closed": (
        True,
        "This asserts an institutional closure of the named Ridotto gambling room. The closing government remains unidentified and distinct from the later democratic rulers; the timing relative to Correr's career is retained without inferring an exact year.",
    ),
    "st-chp17-p383-revolution-and-paintings-market": (
        True,
        "Haskell makes an explicit causal claim from the 1797 revolution and ensuing occupation to pictures reaching the market. The foreign power, collections, individual pictures and transactions remain unspecified.",
    ),
    "st-chp17-p383-correr-avoided-political-commitment": (
        True,
        "This is Haskell's interpretation of Correr's stance toward the unnamed post-revolution democratic rulers; it is retained as a source-attributed candidate, not Correr's own stated motive.",
    ),
    "st-chp17-p383-correr-kept-collecting-into-nineteenth-century": (
        True,
        "Continued buying is retained as a source-attributed activity relation; the acquired objects and sellers are not identified, and no exact end year is inferred.",
    ),
    "st-chp17-p383-correr-background-and-bachelor-characterization": (
        False,
        "This is Haskell's personality and social-position characterization, not a relation between independently represented entities.",
    ),
    "st-chp17-p383-correr-unnoticed-in-byron-bonington-venice": (
        False,
        "The phrase is a cultural characterization of Correr's visibility in Venice; it does not assert that Byron or Bonington met or interacted with him.",
    ),
    "st-chp17-p383-correr-vulnerable-to-dealers": (
        True,
        "Haskell asserts a vulnerability relation between Correr and a source-defined but unnamed group of second-hand dealers; no individual dealer or transaction is inferred.",
    ),
    "st-chp17-p383-correr-died-in-1830": (
        False,
        "The death year is a unary biographical attribute, not a relation between distinct entities.",
    ),
    "st-chp17-p383-haskell-closes-aristocratic-art-tradition": (
        False,
        "This is Haskell's long-range historical periodization of aristocratic interest in the arts, not a relation between Correr and an independently identified endpoint.",
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12259",
        "index_entry_id": "",
        "canonical_name": "Unnamed government that closed the Ridotto gambling room (p.383)",
        "index_page_range": "",
        "suggested_type": "institution",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says the government closed the Ridotto as Correr was beginning his political career. The responsible regime is not named and is not identified with the later democratic rulers.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L21",
    },
    {
        "candidate_id": "cand-12260",
        "index_entry_id": "",
        "canonical_name": "Unnamed democratic rulers addressed by Teodoro Correr after 1797 (p.383)",
        "index_page_range": "",
        "suggested_type": "institution",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell reports that Correr wrote to his new democratic rulers when seeking Civic Guard exemption. No individual ruler or exact governing body is identified.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L22",
    },
    {
        "candidate_id": "cand-12261",
        "index_entry_id": "",
        "canonical_name": "More unscrupulous second-hand dealers in Haskell's Correr account (unnamed group, p.383)",
        "index_page_range": "",
        "suggested_type": "",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell characterizes Correr as an easy prey to this group but names no dealer or transaction. The group is source-bound and its taxonomy type remains open.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L22",
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-chp17-p383-ridotto-government-0001",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12259",
        "surface_form": "the government",
        "start_char": "142",
        "end_char": "156",
        "note": "Unnamed institution said to have closed the Ridotto; not equated with a named regime.",
    },
    {
        "mention_id": "m-chp17-p383-democratic-rulers-0001",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12260",
        "surface_form": "his new democratic rulers",
        "start_char": "582",
        "end_char": "607",
        "note": "Unnamed political authorities addressed by Correr after the revolution of 1797.",
    },
    {
        "mention_id": "m-chp17-p383-second-hand-dealers-0001",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12261",
        "surface_form": "the more unscrupulous second-hand dealers",
        "start_char": "1014",
        "end_char": "1055",
        "note": "Unnamed group in Haskell's characterization; no individual dealer or transaction is identified.",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def csv_append(data: bytes, rows: list[dict[str, str]]) -> bytes:
    bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
    text = data[len(bom) :].decode("utf-8")
    fieldnames = csv.DictReader(io.StringIO(text, newline="")).fieldnames
    if not fieldnames:
        raise SystemExit("CSV header is missing")
    newline = "\r\n" if b"\r\n" in data else "\n"
    buffer = io.StringIO(newline="")
    csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator=newline).writerows(rows)
    body = data[len(bom) :]
    if body and not body.endswith((b"\n", b"\r")):
        body += newline.encode()
    return bom + body + buffer.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validating fixed preview inputs")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    originals = {path: path.read_bytes() for path in (statement_path, candidate_path, mention_path)}
    expected = {
        SOURCE: SOURCE_SHA256,
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
        raise SystemExit("p.383 segment fingerprint changed")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[18:22])
    for mention in NEW_MENTIONS:
        start, end = int(mention["start_char"]), int(mention["end_char"])
        if segment_text[start:end] != mention["surface_form"]:
            raise SystemExit(f"mention span differs from segment text: {mention['mention_id']}")

    candidate_text = originals[candidate_path][3:].decode("utf-8")
    candidate_rows = list(csv.DictReader(io.StringIO(candidate_text, newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    new_candidate_ids = {row["candidate_id"] for row in NEW_CANDIDATES}
    if candidate_ids.intersection(new_candidate_ids) or new_candidate_ids != {"cand-12259", "cand-12260", "cand-12261"}:
        raise SystemExit("new candidate IDs collide or differ from the reviewed set")
    mention_text = originals[mention_path][3:].decode("utf-8")
    existing_mentions = list(csv.DictReader(io.StringIO(mention_text, newline="")))
    mention_ids = {row["mention_id"] for row in existing_mentions}
    if mention_ids.intersection(row["mention_id"] for row in NEW_MENTIONS):
        raise SystemExit("new mention ID already exists")

    bom = b"\xef\xbb\xbf" if originals[statement_path].startswith(b"\xef\xbb\xbf") else b""
    output: list[bytes] = []
    seen: set[str] = set()
    existing_ids: set[str] = set()
    segment_rows: list[dict[str, object]] = []
    new_statement_id = "st-chp17-p383-correr-wrote-to-democratic-rulers"
    for raw in originals[statement_path][len(bom) :].splitlines(keepends=True):
        ending = b"\n" if raw.endswith(b"\n") else b""
        row = json.loads(raw[:-1] if ending else raw)
        sid = row.get("statement_id")
        existing_ids.add(sid)
        if sid == new_statement_id:
            raise SystemExit(f"new statement ID already exists: {sid}")
        if row.get("segment_id") != SEGMENT_ID:
            output.append(raw)
            continue
        segment_rows.append(row)
        qualifiers = row.get("qualifiers") or {}
        if sid in CLASSIFICATIONS:
            if qualifiers.get("relation_candidate") is not None:
                raise SystemExit(f"statement is no longer unset: {sid}")
            status, note = CLASSIFICATIONS[sid]
            qualifiers["relation_candidate"] = status
            qualifiers["relation_candidate_note"] = note
            if sid == "st-chp17-p383-ridotto-room-closed":
                row["subject_candidate_id"] = "cand-12259"
                row["object_candidate_id"] = "cand-10725"
                row["predicate"] = "closed_ridotto_gambling_room"
                mentions = qualifiers.get("mentioned_candidate_ids", [])
                if "cand-12259" not in mentions:
                    mentions.append("cand-12259")
                    qualifiers["mentioned_candidate_ids"] = mentions
            elif sid == "st-chp17-p383-correr-avoided-political-commitment":
                row["object_candidate_id"] = "cand-12260"
                mentions = qualifiers.get("mentioned_candidate_ids", [])
                if "cand-12260" not in mentions:
                    mentions.append("cand-12260")
                    qualifiers["mentioned_candidate_ids"] = mentions
            elif sid == "st-chp17-p383-correr-vulnerable-to-dealers":
                row["object_candidate_id"] = "cand-12261"
                mentions = qualifiers.get("mentioned_candidate_ids", [])
                if "cand-12261" not in mentions:
                    mentions.append("cand-12261")
                    qualifiers["mentioned_candidate_ids"] = mentions
            row["qualifiers"] = qualifiers
            seen.add(sid)
        elif sid == "st-chp17-p383-correr-exemption-correspondence":
            qualifiers["claim"] = "Haskell reports that Correr wrote under the headings Libertà and Eguaglianza that ill-health compelled him to resist the stimulus of patriotism and seek exemption from the Civic Guard."
            mentions = qualifiers.get("mentioned_candidate_ids", [])
            if "cand-12260" not in mentions:
                mentions.append("cand-12260")
                qualifiers["mentioned_candidate_ids"] = mentions
            row["qualifiers"] = qualifiers
        output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
    if seen != set(CLASSIFICATIONS):
        raise SystemExit(f"pending statement set changed; missing {sorted(set(CLASSIFICATIONS) - seen)}")
    if not segment_rows:
        raise SystemExit("target segment contains no statement rows")

    original_quote = next(row["original_quote"] for row in segment_rows if row["statement_id"] == "st-chp17-p383-correr-exemption-correspondence")
    new_statement = {
        "statement_id": new_statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-0857",
        "object_candidate_id": "cand-12260",
        "predicate": "wrote_to_democratic_rulers",
        "qualifiers": {
            "source_line_start": 22,
            "source_line_end": 22,
            "printed_page": 383,
            "pdf_physical_page": 5,
            "claim": "Haskell says Correr wrote to his new democratic rulers under the headings Libertà and Eguaglianza.",
            "speaker": "Haskell",
            "text_layer": "authorial report of correspondence",
            "qualification": "The rulers remain unnamed and the original correspondence was not consulted; Haskell's archival locator appears in linked note 2.",
            "mentioned_candidate_ids": ["cand-0857", "cand-12260", "cand-10730"],
            "relation_candidate": True,
            "footnote_marker": "2",
            "footnote_segment": "chp-17:17_CHP-17_sec_ii:l24-33",
            "footnote_line_range": "L31-L32",
            "footnote_text_pending": False,
            "footnote_body_link_status": "linked",
            "footnote_body_segment_id": SEGMENT_ID,
            "footnote_body_line_range": "L22-L22",
            "footnote_note_statement_ids": ["st-chp17-p383-note2-archival-locator"],
            "footnote_link_note": "P.383 note 2 gives an Archivio Correr locator; the manuscript was not consulted.",
        },
        "original_quote": original_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md",
    }
    if new_statement_id in existing_ids:
        raise SystemExit("new statement ID collision")
    last_segment_id = segment_rows[-1]["statement_id"]
    inserted: list[bytes] = []
    for raw in output:
        inserted.append(raw)
        try:
            row = json.loads(raw)
        except Exception:
            continue
        if row.get("statement_id") == last_segment_id:
            inserted.append(json.dumps(new_statement, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n")
    if len(inserted) == len(output):
        raise SystemExit("could not locate segment insertion point")

    updated = {
        statement_path: bom + b"".join(inserted),
        candidate_path: csv_append(originals[candidate_path], NEW_CANDIDATES),
        mention_path: csv_append(originals[mention_path], NEW_MENTIONS),
    }
    preview = {
        "segment_id": SEGMENT_ID,
        "classified": len(seen),
        "relation_candidate_true": sum(value for value, _ in CLASSIFICATIONS.values()),
        "relation_candidate_false": sum(not value for value, _ in CLASSIFICATIONS.values()),
        "added_statement": new_statement_id,
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
