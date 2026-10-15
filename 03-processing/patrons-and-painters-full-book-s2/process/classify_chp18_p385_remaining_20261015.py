#!/usr/bin/env python3
"""Classify pending p.385 conclusion claims and separate a compound comparison."""

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
SEGMENT_ID = "chp-18:18_CHP-18Conclusion:l19-23"
SOURCE_SHA256 = "a3d40952beead96ac48136610fa3fa15f1dcdfcd1a354ef9f2c2262343aeff14"
SEGMENT_SHA256 = "0dcce09dce75a62951299c736a8a20863cfd39be27e8ceed98773c7f5f71eee6"
STATEMENTS_SHA256 = "ee9699e75c231050f57f88103e99c5353a2a13a027a933a5e403d63d1f7e3c2c"
BACKUP_SUFFIX = ".bak-s2-chp18-p385-remaining-20261015"
PENDING_IDS = {
    "st-chp18-conclusion-p385-fetti-and-centres",
    "st-chp18-conclusion-p385-france-england-and-fall-of-venice",
}
NEW_ID = "st-chp18-conclusion-p385-painting-level-comparison"


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
        raise SystemExit("p.385 target segment fingerprint changed")

    bom = b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b""
    output: list[bytes] = []
    seen: set[str] = set()
    inserted = False
    for raw in original[len(bom) :].splitlines(keepends=True):
        ending = b"\r\n" if raw.endswith(b"\r\n") else b"\n" if raw.endswith(b"\n") else b""
        line = raw[: -len(ending)] if ending else raw
        if not line.strip():
            output.append(raw)
            continue
        row = json.loads(line)
        sid = row.get("statement_id")
        if sid == NEW_ID:
            raise SystemExit(f"new statement ID already exists: {sid}")
        if row.get("segment_id") == SEGMENT_ID and sid in PENDING_IDS:
            seen.add(sid)
            q = row.setdefault("qualifiers", {})
            if q.get("relation_candidate") is not None:
                raise SystemExit(f"statement is no longer unset: {sid}")

            if sid == "st-chp18-conclusion-p385-fetti-and-centres":
                quote = row["original_quote"]
                start = quote.index("If it is true")
                marker = ", it is also true that the general level of painting in Rome,"
                end = quote.index(marker, start)
                fetti_quote = quote[start:end].rstrip().rstrip(",")
                painting_quote = "it is also true that the general level of painting in Rome,\nBologna, Naples and Venice—to name only a few of the most important centres—was certainly higher than in almost any other town in Europe."

                row["predicate"] = "fetti_as_exception_to_withdrawn_artist_type"
                row["object_candidate_id"] = None
                q["claim"] = "Haskell calls Domenico Fetti the most beautiful exception to the relatively individual and withdrawn artist type he says is missing in Italy."
                q["source_line_start"] = 21
                q["source_line_end"] = 21
                q["mentioned_candidate_ids"] = ["cand-1033", "cand-3461"]
                q["relation_candidate"] = False
                q["relation_candidate_note"] = "This is Haskell's subjective typological exception, not a relation between Fetti and a distinct patron, work, or institution."
                row["original_quote"] = fetti_quote
                output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)

                painting = {
                    "statement_id": NEW_ID,
                    "segment_id": SEGMENT_ID,
                    "subject_candidate_id": "cand-3461",
                    "object_candidate_id": "cand-3462",
                    "predicate": "painting_level_in_major_italian_centres_exceeded_most_european_towns",
                    "qualifiers": {
                        "source_line_start": 21,
                        "source_line_end": 22,
                        "printed_page": 385,
                        "pdf_physical_page": 2,
                        "claim": "Haskell says the general level of painting in Rome, Bologna, Naples and Venice was higher than in almost any other European town.",
                        "speaker": "Haskell",
                        "text_layer": "authorial comparative evaluation",
                        "qualification": "This is Haskell's aggregate regional judgment, not measured data or an assessment of every work in the named cities.",
                        "mentioned_candidate_ids": ["cand-3461", "cand-4490", "cand-3398", "cand-1722", "cand-2719", "cand-3462"],
                        "relation_candidate": True,
                        "relation_candidate_note": "Regional comparison between the named Italian centres and other European towns; no individual artist or work-level relation is asserted.",
                    },
                    "original_quote": painting_quote,
                    "origin": "book",
                    "source_file": "02-sources/02-Markdown/18_CHP-18Conclusion.md",
                }
                output.append(json.dumps(painting, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
                inserted = True
                continue

            row["object_candidate_id"] = "cand-3461"
            q["claim"] = "Haskell contrasts painting's renewed life in France and England as the Church and feudal aristocracy declined with Venice's fall as the humiliating expiry of Italian art."
            q["relation_candidate"] = True
            q["relation_candidate_note"] = "This preserves Haskell's broad regional contrast and historical interpretation; it does not establish a direct causal edge between a named institution and an individual work or artist."
            output.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + ending)
            continue
        output.append(raw)

    if seen != PENDING_IDS:
        raise SystemExit(f"pending statement set changed: missing {sorted(PENDING_IDS-seen)}")
    if not inserted:
        raise SystemExit("painting-level comparison statement was not inserted")
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
        "added_statement": NEW_ID,
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
