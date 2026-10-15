#!/usr/bin/env python3
"""Classify and atomize pending claims in the p.384 conclusion passage."""

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
SOURCE = ROOT / "02-sources" / "02-Markdown" / "18_CHP-18Conclusion.md"
SEGMENT_ID = "chp-18:18_CHP-18Conclusion:l3-17"
SOURCE_SHA256 = "a3d40952beead96ac48136610fa3fa15f1dcdfcd1a354ef9f2c2262343aeff14"
SEGMENT_SHA256 = "82dcf7e4c5293e3898b5ce604330cd1b5b3237cc2b8c49592e743727880bf6da"
STATEMENTS_SHA256 = "8989c8e1384d3036a5ce323269f662c2bc5ed8e26f84eb3a6e63ed28a9aae239"
BACKUP_SUFFIX = ".bak-s2-chp18-p384-remaining-20261015"
NEW_IDS = {
    "st-chp18-conclusion-p384-venice-political-decline",
    "st-chp18-conclusion-p384-lodoli-writings-unpublished",
}
UNSET_IDS = {
    "st-chp18-conclusion-p384-political-decline",
    "st-chp18-conclusion-p384-italian-art-contribution",
    "st-chp18-conclusion-p384-foreign-artists-and-individual-outlook",
    "st-chp18-conclusion-p384-social-demands-and-originality",
    "st-chp18-conclusion-p384-bamboccianti",
    "st-chp18-conclusion-p384-salvator-rosa",
    "st-chp18-conclusion-p384-canaletto-tourist-views",
    "st-chp18-conclusion-p384-lodoli",
    "st-chp18-conclusion-p384-historians-and-writers",
    "st-chp18-conclusion-p384-patron-comparison-question",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mark(row: dict, value: bool, note: str) -> None:
    q = row.setdefault("qualifiers", {})
    if q.get("relation_candidate") is not None:
        raise SystemExit(f"statement is no longer unset: {row.get('statement_id')}")
    q["relation_candidate"] = value
    q["relation_candidate_note"] = note
    row["qualifiers"] = q


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
        raise SystemExit("p.384 target segment fingerprint changed")

    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    output_lines: list[bytes] = []
    seen: set[str] = set()
    emitted: set[str] = set()
    for raw in original[len(bom) :].splitlines(keepends=True):
        ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
        line = raw[: -len(ending)] if ending else raw
        if not line.strip():
            output_lines.append(raw)
            continue
        row = json.loads(line)
        sid = row.get("statement_id")
        if sid in NEW_IDS:
            raise SystemExit(f"new statement ID already exists: {sid}")
        if row.get("segment_id") == SEGMENT_ID and sid in UNSET_IDS:
            seen.add(sid)
            if (row.get("qualifiers") or {}).get("relation_candidate") is not None:
                raise SystemExit(f"statement is no longer unset: {sid}")

            if sid == "st-chp18-conclusion-p384-political-decline":
                q = row["qualifiers"]
                row["subject_candidate_id"] = "cand-4490"
                row["object_candidate_id"] = None
                q["claim"] = "Haskell says Rome's political decline between 1623 and 1797 was almost continuous."
                q["mentioned_candidate_ids"] = ["cand-4490"]
                mark(row, False, "Rome and Venice are parallel subjects of a shared political-condition claim, not related to each other; the two city claims are separated.")
                venice = json.loads(json.dumps(row, ensure_ascii=False))
                venice["statement_id"] = "st-chp18-conclusion-p384-venice-political-decline"
                venice["subject_candidate_id"] = "cand-2719"
                venice["qualifiers"]["claim"] = "Haskell says Venice's political decline between 1623 and 1797 was almost continuous."
                venice["qualifiers"]["mentioned_candidate_ids"] = ["cand-2719"]
                output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
                output_lines.append(json.dumps(venice, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
                emitted.add("st-chp18-conclusion-p384-venice-political-decline")
                continue

            if sid == "st-chp18-conclusion-p384-italian-art-contribution":
                mark(row, False, "This is Haskell's evaluative ranking of Italian artistic achievements; the existing Italy and art mentions do not identify a distinct contribution endpoint or a formal relation.")
            elif sid == "st-chp18-conclusion-p384-foreign-artists-and-individual-outlook":
                mark(row, False, "This is Haskell's broad comparison of artistic outlooks and public masterpieces; no bounded work group or specific artist-to-work relation is identified.")
            elif sid == "st-chp18-conclusion-p384-social-demands-and-originality":
                row["subject_candidate_id"] = "cand-3461"
                row["object_candidate_id"] = "cand-10735"
                mark(row, True, "Haskell explicitly links social demands in Italian art with the suppression of fresh and original approaches; this is his explanatory interpretation, not an independently measured causal result.")
            elif sid == "st-chp18-conclusion-p384-bamboccianti":
                row["object_candidate_id"] = "cand-10735"
                mark(row, True, "Haskell presents the Bamboccianti's shift from emerging realism to sentimentality as an example of the source-defined conformity problem; no individual member or work is inferred.")
            elif sid == "st-chp18-conclusion-p384-salvator-rosa":
                row["object_candidate_id"] = "cand-10735"
                mark(row, True, "Haskell connects Rosa's use of his temperament with artistic conformity; this is the author's evaluative characterization, not evidence of Rosa's stated intention.")
            elif sid == "st-chp18-conclusion-p384-canaletto-tourist-views":
                row["object_candidate_id"] = "cand-2719"
                q = row["qualifiers"]
                q["mentioned_candidate_ids"] = ["cand-0498", "cand-2719"]
                mark(row, True, "The source links Canaletto's changing treatment of his native city, Venice, with familiar views made for tourists; this preserves Haskell's characterization and does not assert a documented commission.")
            elif sid == "st-chp18-conclusion-p384-lodoli":
                q = row["qualifiers"]
                full_quote = row["original_quote"]
                lodoli_start = full_quote.index("of Padre Lodoli,")
                lodoli_quote = full_quote[lodoli_start:]
                writings_start = lodoli_quote.index("whose")
                office_quote = lodoli_quote[:writings_start].rstrip()
                if office_quote.endswith("and"):
                    office_quote = office_quote[:-3].rstrip()
                writings_quote = lodoli_quote[writings_start:]
                corrections = q.pop("ocr_corrections", [])
                q["source_line_start"] = 12
                q["source_line_end"] = 12
                q["claim"] = "Haskell says Padre Lodoli was honoured with an official government post."
                q["speaker"] = "Haskell"
                q["text_layer"] = "authorial report"
                q["qualification"] = "The post and appointing government are unnamed; the appointment is reported by Haskell and was not independently verified."
                q["mentioned_candidate_ids"] = ["cand-1411"]
                row["predicate"] = "lodoli_honoured_with_official_government_post"
                row["original_quote"] = office_quote
                mark(row, True, "The source asserts a named person's appointment to an official government post; the specific post and government remain unidentified, so this stays an open S2 candidate without a formal edge.")

                writings = {
                    "statement_id": "st-chp18-conclusion-p384-lodoli-writings-unpublished",
                    "segment_id": SEGMENT_ID,
                    "subject_candidate_id": None,
                    "object_candidate_id": None,
                    "predicate": "lodoli_explosive_writings_never_published",
                    "qualifiers": {
                        "source_line_start": 12,
                        "source_line_end": 13,
                        "printed_page": 384,
                        "pdf_physical_page": 1,
                        "claim": "Haskell says Padre Lodoli's explosive writings were never published.",
                        "speaker": "Haskell",
                        "text_layer": "authorial report",
                        "qualification": "No title or individually identifiable writing is named; this is Haskell's publication-status report, not an independently verified claim.",
                        "mentioned_candidate_ids": ["cand-1411"],
                        "ocr_corrections": corrections,
                        "relation_candidate": False,
                        "relation_candidate_note": "This is a publication-status assertion about unspecified writings, not a relation between independently identified entities; no work title or bounded work group is established.",
                    },
                    "original_quote": writings_quote,
                    "origin": "book",
                    "source_file": "02-sources/02-Markdown/18_CHP-18Conclusion.md",
                }
                output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
                output_lines.append(json.dumps(writings, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
                emitted.add(writings["statement_id"])
                continue
            elif sid == "st-chp18-conclusion-p384-historians-and-writers":
                row["object_candidate_id"] = "cand-10735"
                mark(row, True, "Haskell explicitly reports that modern Italian historians noted and resented the conformity issue; the claim remains attributed to him, and no individual historian or writer is inferred.")
            elif sid == "st-chp18-conclusion-p384-patron-comparison-question":
                mark(row, True, "This records Haskell's rhetorical comparison of named foreign and Italian patrons' tolerance and education only; the question form is retained and no comparative ranking or individual trait is asserted.")
            output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
            continue
        output_lines.append(raw)

    if seen != UNSET_IDS:
        raise SystemExit(f"pending statement set changed; missing={sorted(UNSET_IDS-seen)}, extra={sorted(seen-UNSET_IDS)}")
    if emitted != NEW_IDS:
        raise SystemExit(f"new statement insertion failed: {sorted(NEW_IDS-emitted)}")

    updated = bom + b"".join(output_lines)
    final_segment_rows = [
        json.loads(line)
        for line in b"".join(output_lines).splitlines()
        if line.strip() and json.loads(line).get("segment_id") == SEGMENT_ID
    ]
    preview = {
        "segment_id": SEGMENT_ID,
        "classified_unset": len(seen),
        "relation_candidate_true_in_segment": sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in final_segment_rows),
        "relation_candidate_false_in_segment": sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in final_segment_rows),
        "added_statements": sorted(NEW_IDS),
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
