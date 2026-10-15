#!/usr/bin/env python3
"""Classify p.382-p.383 citation notes and split the archival confirmation."""

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "17_CHP-17_sec_ii.md"
SEGMENT_ID = "chp-17:17_CHP-17_sec_ii:l24-33"
SOURCE_SHA256 = "d23af9f50ab9ac84fb250f5c7c5c260908096616ca83773a647977b8e07f4ff3"
SEGMENT_SHA256 = "9c475e85fa962219537da954e1f299de3df3f277850a16612105fbb8fd7c46df"
STATEMENTS_SHA256 = "9bba52eb306ee2ab48f394e19bbe0730b07117b4c265194f85c8773d3ab11ab1"
BACKUP_SUFFIX = ".bak-s2-chp17-p383-notes-20261015"

CLASSIFICATIONS = {
    "st-chp17-p382-note1-dandolo": (
        False,
        "This is a citation locator only: the source is given as Dandolo, p.97, without a title or edition, and no source-content relation is asserted beyond the reference.",
    ),
    "st-chp17-p382-note3-urbani-publication": (
        True,
        "The note gives an explicit Biblioteca Correr locator for the named Urbani de Ghelthof publication. Its separate claim that archive papers confirm the account is split into a linked statement; neither source was independently consulted.",
    ),
    "st-chp17-p382-note5-dandolo": (
        False,
        "This repeats the Dandolo p.97 citation as a source locator; the work remains unidentified beyond surname and page, and no distinct relation claim is added.",
    ),
    "st-chp17-p383-note3-levi": (
        False,
        "This is a surname, volume and page citation locator only; the title and edition are absent, and the cited page was not consulted.",
    ),
}
NEW_STATEMENT_ID = "st-chp17-p382-note3-archive-confirmation"


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
    segments = [json.loads(line) for line in (TABLES / "segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256 or segment.get("asset_sha256") != SOURCE_SHA256:
        raise SystemExit("p.383 notes segment fingerprint changed")

    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    output: list[bytes] = []
    seen: set[str] = set()
    segment_rows: list[dict[str, object]] = []
    existing_ids: set[str] = set()
    for raw in original[len(bom) :].splitlines(keepends=True):
        ending = b"\n" if raw.endswith(b"\n") else b""
        row = json.loads(raw[:-1] if ending else raw)
        sid = row.get("statement_id")
        existing_ids.add(sid)
        if sid == NEW_STATEMENT_ID:
            raise SystemExit(f"new statement ID already exists: {sid}")
        if row.get("segment_id") == SEGMENT_ID:
            segment_rows.append(row)
        qualifiers = row.get("qualifiers") or {}
        if sid in CLASSIFICATIONS:
            if row.get("segment_id") != SEGMENT_ID or qualifiers.get("relation_candidate") is not None:
                raise SystemExit(f"statement moved or is no longer unset: {sid}")
            status, note = CLASSIFICATIONS[sid]
            qualifiers["relation_candidate"] = status
            qualifiers["relation_candidate_note"] = note
            if sid == "st-chp17-p382-note3-urbani-publication":
                row["predicate"] = "publication_locator_at_biblioteca_correr"
                qualifiers["claim"] = "Printed note 3 points to Urbani de Ghelthof's Teodoro Correr e il suo museo and locates it at Biblioteca Correr, shelfmark Op. P.D. 18796."
                qualifiers["mentioned_candidate_ids"] = ["cand-10719", "cand-8262"]
            row["qualifiers"] = qualifiers
            seen.add(sid)
        elif sid == "st-chp17-p382-correr-financial-weakness-exploitation":
            note_ids = qualifiers.get("footnote_note_statement_ids", [])
            if NEW_STATEMENT_ID not in note_ids:
                note_ids.append(NEW_STATEMENT_ID)
                qualifiers["footnote_note_statement_ids"] = note_ids
            qualifiers["footnote_link_note"] = "Note 3 supplies a publication locator and separately attributes confirmation to Correr archive papers; neither was independently consulted."
            row["qualifiers"] = qualifiers
        output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending if row.get("segment_id") == SEGMENT_ID or sid in CLASSIFICATIONS or sid == "st-chp17-p382-correr-financial-weakness-exploitation" else raw)

    if seen != set(CLASSIFICATIONS):
        raise SystemExit(f"pending note statement set changed; missing {sorted(set(CLASSIFICATIONS) - seen)}")
    if not segment_rows:
        raise SystemExit("target notes segment contains no statements")
    if NEW_STATEMENT_ID in existing_ids:
        raise SystemExit("new statement ID collision")

    quote = next(row["original_quote"] for row in segment_rows if row["statement_id"] == "st-chp17-p382-note3-urbani-publication")
    new_statement = {
        "statement_id": NEW_STATEMENT_ID,
        "segment_id": SEGMENT_ID,
        "subject_candidate_id": "cand-10719",
        "object_candidate_id": "cand-10722",
        "predicate": "account_confirmed_by_archive_papers",
        "qualifiers": {
            "source_line_start": 27,
            "source_line_end": 27,
            "printed_page": 382,
            "pdf_physical_page": 4,
            "claim": "Haskell says Urbani de Ghelthof's account of Correr and his museum is confirmed by papers in Correr's archives.",
            "speaker": "Haskell",
            "text_layer": "bibliographic citation with archival corroboration claim",
            "qualification": "This is Haskell's attribution of corroboration; the publication and archival papers were not independently consulted, and no specific papers are identified.",
            "mentioned_candidate_ids": ["cand-10719", "cand-10722"],
            "relation_candidate": True,
            "footnote_marker": "3",
            "footnote_segment": SEGMENT_ID,
            "footnote_line_range": "L27-L27",
            "footnote_text_pending": False,
            "footnote_body_link_status": "linked",
            "footnote_body_segment_id": "chp-17:17_CHP-17_sec_ii:l7-17",
            "footnote_body_line_range": "L10-L10",
            "footnote_link_note": "The note attributes confirmation to archive papers; neither the source nor those papers were independently consulted.",
        },
        "original_quote": quote,
        "origin": "book",
        "source_file": "02-sources/02-Markdown/17_CHP-17_sec_ii.md",
    }
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
        raise SystemExit("could not locate target segment insertion point")

    updated = bom + b"".join(inserted)
    preview = {
        "segment_id": SEGMENT_ID,
        "classified_unset": len(seen),
        "relation_candidate_true_existing": sum(value for value, _ in CLASSIFICATIONS.values()),
        "relation_candidate_false_existing": sum(not value for value, _ in CLASSIFICATIONS.values()),
        "added_statement": NEW_STATEMENT_ID,
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
