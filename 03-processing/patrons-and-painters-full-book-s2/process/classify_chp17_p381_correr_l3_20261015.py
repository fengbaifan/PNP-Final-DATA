#!/usr/bin/env python3
"""Review the p.381 Correr introduction segment; preview by default."""

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
SEGMENT_ID = "chp-17:17_CHP-17_sec_ii:l3-5"
SOURCE_SHA256 = "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3"
SEGMENT_SHA256 = "fa1e88d174c0ace042923dce42542bd14f6fe6b69bc493c93919536ae43f8229"
STATEMENTS_SHA256 = "84ba6a486f290dbd0ecbf0376969f445a8865371f5904e66e5192c97705bcd22"
CANDIDATES_SHA256 = "e34a3c04ca54246cf04e6ab441ccbcaf8f27c827f58ce513f6071bd4d8096881"
MENTIONS_SHA256 = "16ea170f46d344ef50861a5a94c8dabd4309dd4c02923cf4cfaa1ca923f4fe7b"
BACKUP_SUFFIX = ".bak-s2-chp17-p381-correr-20261015"

STATUS_NOTES = {
    "st-chp17-p381-correr-republic-context": (
        True,
        "This source-attributed introduction asserts Correr's survival of the Republic's downfall and links him to its history; retain the political entity endpoint, with identity alignment deferred to S3.",
    ),
    "st-chp17-p381-correr-born-1750": (
        False,
        "Birth year is a unary biographical attribute, not a relation between independently represented entities.",
    ),
    "st-chp17-p381-correr-different-from-manfrin": (
        False,
        "The remaining claim is Haskell's comparative characterization of the two men's lives and characters. Their shared love of art is separated into its own relational statement.",
    ),
    "st-chp17-p381-correr-portrait-traits": (
        False,
        "The claim records Haskell's interpretation of personality from a portrait, not an independently established relation. The portrait-to-sitter identification is recorded separately.",
    ),
    "st-chp17-p381-correr-descent": (
        True,
        "The source asserts descent from a specific but unnamed Venetian family. A source-bound family candidate is retained with unresolved identity rather than omitted or guessed.",
    ),
    "st-chp17-p381-correr-meeting-poems": (
        False,
        "This is contextual description of an evening's fencing and unnamed friends' poems; neither the participants nor individual poems are identified as relation endpoints.",
    ),
    "st-chp17-p381-correr-political-career-1776": (
        False,
        "The beginning of a political career in 1776 is a biographical statement without a named office endpoint; the later Council of Ten membership is recorded separately.",
    ),
    "st-chp17-p381-correr-became-abate": (
        False,
        "This reports a change in Correr's biographical role and motive without identifying an institution or another relation endpoint.",
    ),
    "st-chp17-p381-correr-repeated-applications": (
        False,
        "This summarizes repeated applications to unnamed authorities without a bounded recipient endpoint; the continuation after 'However, there' remains in the next source segment.",
    ),
    "st-chp17-p381-correr-love-of-learning": (
        False,
        "This is a source-attributed biographical characterization, not a relation between distinct entities.",
    ),
}

NEW_CANDIDATES = [
    {
        "candidate_id": "cand-12255",
        "index_entry_id": "",
        "canonical_name": "Unnamed Venetian aristocratic family from which Teodoro Correr descended (p.381)",
        "index_page_range": "",
        "suggested_type": "family",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Correr descended from one of the oldest Venetian aristocratic families. No family name or identity is supplied; this source-bound candidate preserves the asserted family relation without guessing an identity.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L3",
    },
    {
        "candidate_id": "cand-12256",
        "index_entry_id": "",
        "canonical_name": "Unnamed club attended by Teodoro Correr in 1768 (p.381)",
        "index_page_range": "",
        "suggested_type": "institution",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "Haskell says Correr belonged to a club and read a paper there in 1768. The club is unnamed and its institutional identity is unresolved.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L3",
    },
]

NEW_MENTIONS = [
    {
        "mention_id": "m-chp17-p381-correr-family-0001",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12255",
        "surface_form": "one of the oldest of the Venetian aristocratic families",
        "start_char": "409",
        "end_char": "464",
        "note": "Unnamed family endpoint in Haskell's descent claim; no identity is inferred.",
    },
    {
        "mention_id": "m-chp17-p381-correr-club-0001",
        "segment_id": SEGMENT_ID,
        "candidate_id": "cand-12256",
        "surface_form": "a club to which he belonged",
        "start_char": "647",
        "end_char": "674",
        "note": "Unnamed club to which Correr belonged and at which he read his 1768 paper.",
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
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator=newline)
    writer.writerows(rows)
    addition = buffer.getvalue().encode("utf-8")
    if data and not data.endswith((b"\n", b"\r")):
        data += newline.encode()
    return bom + data[len(bom) :] + addition


def make_statement(
    statement_id: str,
    subject: str,
    object_: str,
    predicate: str,
    claim: str,
    layer: str,
    qualification: str,
    mentioned: list[str],
    original_quote: str,
    **extra: object,
) -> dict[str, object]:
    qualifiers: dict[str, object] = {
        "source_line_start": 3,
        "source_line_end": 3,
        "printed_page": 381,
        "pdf_physical_page": 3,
        "claim": claim,
        "speaker": "Haskell",
        "text_layer": layer,
        "qualification": qualification,
        "mentioned_candidate_ids": mentioned,
        "relation_candidate": True,
    }
    qualifiers.update(extra)
    return {
        "statement_id": statement_id,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": subject,
        "object_candidate_id": object_,
        "predicate": predicate,
        "qualifiers": qualifiers,
        "original_quote": original_quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after validating fixed preview inputs")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    statement_path = TABLES / "book-statements.jsonl"
    candidate_path = TABLES / "entity-candidates.csv"
    mention_path = TABLES / "mentions.csv"
    originals = {
        statement_path: statement_path.read_bytes(),
        candidate_path: candidate_path.read_bytes(),
        mention_path: mention_path.read_bytes(),
    }
    expected = {
        SOURCE: SOURCE_SHA256,
        statement_path: STATEMENTS_SHA256,
        candidate_path: CANDIDATES_SHA256,
        mention_path: MENTIONS_SHA256,
    }
    for path, fingerprint in expected.items():
        if sha256(path.read_bytes()) != fingerprint:
            raise SystemExit(f"input changed; rebuild and review preview: {path.relative_to(ROOT)}")
    if sha256(source_bytes) != SOURCE_SHA256:
        raise SystemExit("source file fingerprint changed")
    segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("p.381 segment fingerprint changed")

    source_lines = source_bytes.decode("utf-8-sig").splitlines()
    if source_lines[2][409:464] != NEW_MENTIONS[0]["surface_form"] or source_lines[2][647:674] != NEW_MENTIONS[1]["surface_form"]:
        raise SystemExit("new mention spans do not match the source line")

    candidate_text = originals[candidate_path][3:].decode("utf-8")
    candidate_rows = list(csv.DictReader(io.StringIO(candidate_text, newline="")))
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    if candidate_ids.intersection(row["candidate_id"] for row in NEW_CANDIDATES):
        raise SystemExit("new candidate ID already exists")
    expected_new_candidate_ids = {"cand-12255", "cand-12256"}
    if not {row["candidate_id"] for row in NEW_CANDIDATES} == expected_new_candidate_ids:
        raise SystemExit("unexpected candidate set")

    mention_text = originals[mention_path][3:].decode("utf-8")
    mention_rows = list(csv.DictReader(io.StringIO(mention_text, newline="")))
    mention_ids = {row["mention_id"] for row in mention_rows}
    if mention_ids.intersection(row["mention_id"] for row in NEW_MENTIONS):
        raise SystemExit("new mention ID already exists")
    if any(row["candidate_id"] not in candidate_ids | expected_new_candidate_ids for row in NEW_MENTIONS):
        raise SystemExit("new mention points to an absent candidate")

    statements = originals[statement_path]
    bom = b"\xef\xbb\xbf" if statements.startswith(b"\xef\xbb\xbf") else b""
    output: list[bytes] = []
    seen: set[str] = set()
    segment_rows: list[dict[str, object]] = []
    new_ids = {
        "st-chp17-p381-correr-shared-love-of-art",
        "st-chp17-p381-correr-portrait-identification",
        "st-chp17-p381-correr-club-membership",
    }
    all_existing_ids = set()
    for raw in statements[len(bom) :].splitlines(keepends=True):
        ending = b"\n" if raw.endswith(b"\n") else b""
        content = raw[:-1] if ending else raw
        row = json.loads(content)
        sid = row.get("statement_id")
        if sid in new_ids:
            raise SystemExit(f"new statement ID already exists: {sid}")
        all_existing_ids.add(sid)
        if row.get("segment_id") != SEGMENT_ID:
            output.append(raw)
            continue
        segment_rows.append(row)
        qualifiers = row.get("qualifiers") or {}
        if sid in STATUS_NOTES:
            if qualifiers.get("relation_candidate") is not None:
                raise SystemExit(f"statement is no longer unset: {sid}")
            status, note = STATUS_NOTES[sid]
            qualifiers["relation_candidate"] = status
            qualifiers["relation_candidate_note"] = note
            row["qualifiers"] = qualifiers
            seen.add(sid)
        if sid == "st-chp17-p381-correr-different-from-manfrin":
            row["predicate"] = "life_and_character_differed_from_manfrin"
            qualifiers["claim"] = "Haskell characterizes Correr's life and character as differing from Manfrin's."
        elif sid == "st-chp17-p381-correr-paper-read-1768":
            row["predicate"] = "read_paper_in_1768"
            qualifiers["claim"] = "Haskell says Correr read an elaborate paper titled The Sacrifices of the Ancients in 1768."
            mentions = qualifiers.get("mentioned_candidate_ids", [])
            if "cand-12256" not in mentions:
                mentions.append("cand-12256")
                qualifiers["mentioned_candidate_ids"] = mentions
        elif sid == "st-chp17-p381-correr-descent":
            row["object_candidate_id"] = "cand-12255"
            mentions = qualifiers.get("mentioned_candidate_ids", [])
            if "cand-12255" not in mentions:
                mentions.append("cand-12255")
                qualifiers["mentioned_candidate_ids"] = mentions
        row["qualifiers"] = qualifiers
        output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)

    if seen != set(STATUS_NOTES):
        raise SystemExit(f"pending statement set changed; missing {sorted(set(STATUS_NOTES) - seen)}")
    if not segment_rows:
        raise SystemExit("target segment contains no statement rows")
    original_quote = next(row["original_quote"] for row in segment_rows if row["statement_id"] == "st-chp17-p381-correr-different-from-manfrin")
    shared = make_statement(
        "st-chp17-p381-correr-shared-love-of-art",
        "cand-0857",
        "cand-1512",
        "shared_interest_in_art",
        "Haskell says Correr and Manfrin shared a love of art.",
        "authorial characterization",
        "The shared interest is separated from Haskell's comparison of their lives and characters.",
        ["cand-0857", "cand-1512"],
        original_quote,
    )
    portrait = make_statement(
        "st-chp17-p381-correr-portrait-identification",
        "cand-4007",
        "cand-0857",
        "depicts_sitter",
        "The passage identifies Plate 59b as a portrait of Teodoro Correr.",
        "authorial report",
        "The identification is taken from 'His portrait' and the linked Plate 59b reference; personality traits inferred from the portrait remain in a separate non-relational statement.",
        ["cand-4007", "cand-0857"],
        next(row["original_quote"] for row in segment_rows if row["statement_id"] == "st-chp17-p381-correr-portrait-traits"),
        footnote_marker="3",
        footnote_segment="chp-17:17_CHP-17_sec_i:l26-35",
        footnote_line_range="L34-L34",
        footnote_text_pending=False,
        footnote_body_link_status="linked",
        footnote_body_line_range="L3-L3",
        footnote_note_statement_ids=["st-chp17-p381-note3-castelli-portrait", "st-chp17-p381-note3-portrait-date"],
    )
    club = make_statement(
        "st-chp17-p381-correr-club-membership",
        "cand-0857",
        "cand-12256",
        "member_of",
        "Haskell says Correr belonged to the unnamed club to which he delivered his 1768 paper.",
        "authorial report",
        "The club is retained as a source-bound institution candidate; its name and identity are unknown.",
        ["cand-0857", "cand-12256"],
        next(row["original_quote"] for row in segment_rows if row["statement_id"] == "st-chp17-p381-correr-paper-read-1768"),
    )
    additions = [shared, portrait, club]
    if all_existing_ids.intersection(row["statement_id"] for row in additions):
        raise SystemExit("new statement ID collision")

    # Insert the new atomic statements immediately after the segment's final row.
    last_segment_id = segment_rows[-1]["statement_id"]
    inserted: list[bytes] = []
    for raw in output:
        inserted.append(raw)
        try:
            row = json.loads(raw)
        except Exception:
            continue
        if row.get("statement_id") == last_segment_id:
            inserted.extend(json.dumps(item, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n" for item in additions)
    if len(inserted) == len(output):
        raise SystemExit("could not locate segment insertion point")
    updated_statements = bom + b"".join(inserted)
    updated_candidates = csv_append(originals[candidate_path], NEW_CANDIDATES)
    updated_mentions = csv_append(originals[mention_path], NEW_MENTIONS)
    updated = {
        statement_path: updated_statements,
        candidate_path: updated_candidates,
        mention_path: updated_mentions,
    }
    preview = {
        "segment_id": SEGMENT_ID,
        "classified_existing_unset": len(seen),
        "relation_candidate_true_existing": sum(v for v, _ in STATUS_NOTES.values()),
        "relation_candidate_false_existing": sum(not v for v, _ in STATUS_NOTES.values()),
        "added_candidates": [row["candidate_id"] for row in NEW_CANDIDATES],
        "added_mentions": [row["mention_id"] for row in NEW_MENTIONS],
        "added_relation_statements": [row["statement_id"] for row in additions],
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
