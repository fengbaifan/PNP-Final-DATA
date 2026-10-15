#!/usr/bin/env python3
"""Classify the last ten unclassified S2 statements on printed pp.409-410.

Default mode is a read-only preview. --apply writes only the two reviewed
JSONL records, the corrected mention mapping, and one exact nested work
mention. Unchanged bytes in both tables are preserved.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE_REL = Path("02-sources/02-Markdown/20_CHP-20Postscript.md")
STATEMENTS_REL = Path("04-knowledge/tables/book-statements.jsonl")
MENTIONS_REL = Path("04-knowledge/tables/mentions.csv")
SEGMENTS_REL = Path("04-knowledge/tables/segments.jsonl")
EXPECTED = {
    SOURCE_REL.as_posix(): "e6b2ed7396fa79ff075f74dac37360c48e7e41a4969dc74ed57a8ce39bcb5f90",
    STATEMENTS_REL.as_posix(): "c1bf0f1b70b507698ce6e89cd2ca506d45f51c5ca6e9a671044812949311d89e",
    MENTIONS_REL.as_posix(): "0ae0e3e8703a68b91d58560862e2fe3abdb380e3bf4097e97436c1cff1fffd4a",
}
BACKUP_SUFFIX = "-bak-s2-chp20-p409-p410-classification-20261015"

CLASSIFICATIONS = {
    "st-chp20-p409-maggiotto-historical-portraiture": {
        "relation_candidate": False,
        "relation_candidate_note": (
            "Haskell's phrase is a source-attributed art-historical characterization "
            "of the portrait series, not a concrete relation between distinct entities."
        ),
    },
    "st-chp20-p409-schmidt-salimbeni-etching": {
        "relation_candidate": True,
        "relation_candidate_note": (
            "Haskell explicitly reports this etching by Schmidt. The existing print "
            "candidate is the work endpoint and Schmidt is its maker; Salimbeni and "
            "Algarotti remain the named sitter and recipient roles in the source claim."
        ),
    },
    "st-chp20-p410-tomb-detail-dust-jacket": {
        "relation_candidate": True,
        "relation_candidate_note": (
            "The source explicitly states that a detail of the painting is reproduced "
            "on the book's dust jacket; this is an illustration/use relation."
        ),
        "open_endpoint_reason": (
            "The dust jacket is identified only as a component of the source book and "
            "is not represented as a separate dataset entity."
        ),
    },
    "st-chp20-p410-sasso-scholarly-associations": {
        "relation_candidate": True,
        "relation_candidate_note": (
            "Haskell explicitly reports Sasso's association with a collective of "
            "scholars and artists involved in rediscovering early Italian painters."
        ),
        "open_endpoint_reason": (
            "The scholars and artists are unnamed in this sentence; retain the "
            "association claim without inventing individual endpoints."
        ),
    },
    "st-chp20-p410-lloyd-venezia-pittrice-project": {
        "relation_candidate": True,
        "relation_candidate_note": (
            "The source reports Lloyd's treatment of the projected, uncompleted "
            "Venezia Pittrice project in an exhibition catalogue."
        ),
    },
    "st-chp20-p410-olivato-sasso-article": {
        "relation_candidate": True,
        "relation_candidate_note": (
            "Haskell reports that Olivato's article discusses Sasso and reproduces "
            "letters linking him with other figures; the article remains unconsulted."
        ),
    },
    "st-chp20-p410-della-lena-treatise-content": {
        "relation_candidate": True,
        "relation_candidate_note": (
            "The statement reports the treatise's account of art removals and "
            "Della Lena's assistance; it remains Haskell's report of a source not "
            "independently consulted."
        ),
        "open_endpoint_reason": (
            "The foreigners, friends, and removed artworks are not individually "
            "identified; do not infer specific removal events or endpoints."
        ),
    },
    "st-chp20-p410-della-lena-painter-appreciations": {
        "relation_candidate": True,
        "relation_candidate_note": (
            "The source reports Della Lena's appreciation of Guardi and earlier "
            "Venetian painters; the statement retains the named painters as mentions."
        ),
        "open_endpoint_reason": (
            "The source's Vivarini reference remains unresolved between an individual "
            "painter and the family; keep that endpoint open pending identity review."
        ),
    },
    "st-chp20-p410-manfrin-acquisition-sources-uncertain": {
        "relation_candidate": False,
        "relation_candidate_note": (
            "This records Haskell's stated research gap about Manfrin's acquisition "
            "sources, not an affirmative acquisition event or relation."
        ),
    },
    "st-chp20-p410-fontana-manfrin-tobacco-article": {
        "relation_candidate": True,
        "relation_candidate_note": (
            "Haskell reports Fontana's argument connecting Manfrin's tobacco "
            "manufacturing and the fortune used to form his collection; the article "
            "has not been independently consulted."
        ),
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require_hash(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    actual = sha256(data)
    if actual != expected:
        raise SystemExit(f"Precondition failed for {path.relative_to(ROOT)}: {actual}")
    return data


def encode_jsonl_updates(raw: bytes) -> tuple[bytes, list[str]]:
    text = raw.decode("utf-8")
    output: list[str] = []
    seen: set[str] = set()
    changed: list[str] = []
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        record = json.loads(body)
        statement_id = record.get("statement_id")
        if statement_id in CLASSIFICATIONS:
            if statement_id in seen:
                raise SystemExit(f"Duplicate statement ID: {statement_id}")
            seen.add(statement_id)
            qualifiers = record.setdefault("qualifiers", {})
            if "relation_candidate" in qualifiers:
                raise SystemExit(f"Statement already classified: {statement_id}")
            classification = CLASSIFICATIONS[statement_id]
            qualifiers.update(classification)
            if statement_id == "st-chp20-p409-schmidt-salimbeni-etching":
                record["subject_candidate_id"] = "cand-11136"
                record["object_candidate_id"] = "cand-2396"
                record["predicate"] = "created_by"
            output.append(json.dumps(record, ensure_ascii=False) + ending)
            changed.append(statement_id)
        else:
            output.append(line)
    missing = set(CLASSIFICATIONS) - seen
    if missing:
        raise SystemExit(f"Target statements not found: {sorted(missing)}")
    return "".join(output).encode("utf-8"), changed


def csv_row(fields: list[str], ending: str) -> str:
    buf = io.StringIO(newline="")
    csv.writer(buf, lineterminator="\n").writerow(fields)
    return buf.getvalue().rstrip("\n") + ending


def encode_mention_updates(raw: bytes, segment_text: str) -> tuple[bytes, list[str]]:
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    if not lines:
        raise SystemExit("mentions.csv is empty")
    header_line = lines[0].rstrip("\r\n")
    headers = next(csv.reader([header_line]))
    col = {name: index for index, name in enumerate(headers)}
    required = {"mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note"}
    if not required.issubset(col):
        raise SystemExit(f"Unexpected mentions.csv columns: {headers}")

    target_seen = False
    new_id_seen = False
    output = [lines[0]]
    changed: list[str] = []
    for line in lines[1:]:
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        fields = next(csv.reader([body]))
        mention_id = fields[col["mention_id"]]
        if mention_id == "m-chp20-p409-035":
            if target_seen:
                raise SystemExit("Duplicate target mention m-chp20-p409-035")
            target_seen = True
            expected = {
                "segment_id": "chp-20:20_CHP-20Postscript:l187-199",
                "candidate_id": "cand-11136",
                "surface_form": "the same artist",
                "start_char": "1831",
                "end_char": "1846",
            }
            for key, value in expected.items():
                if fields[col[key]] != value:
                    raise SystemExit(f"Unexpected m035 {key}: {fields[col[key]]!r}")
            fields[col["candidate_id"]] = "cand-2396"
            fields[col["note"]] = (
                "Refers to Georg Friedrich Schmidt, the antecedent of 'the same artist'."
            )
            output.append(csv_row(fields, ending))
            changed.append(mention_id)
            continue
        if mention_id == "m-chp20-p409-054":
            new_id_seen = True
        output.append(line)

    if not target_seen:
        raise SystemExit("Target mention m-chp20-p409-035 not found")
    if new_id_seen:
        raise SystemExit("New mention ID already exists: m-chp20-p409-054")

    surface = (
        "etched for Algarotti the rather epicene features of a singer called "
        "Felice Salimbeni"
    )
    start = segment_text.find(surface)
    if start < 0 or segment_text.find(surface, start + 1) >= 0:
        raise SystemExit("Expected unique work-mention surface not found in p.409 segment")
    end = start + len(surface)
    if segment_text[start:end] != surface:
        raise SystemExit("New work mention span does not match source text")
    new_fields = [""] * len(headers)
    new_values = {
        "mention_id": "m-chp20-p409-054",
        "segment_id": "chp-20:20_CHP-20Postscript:l187-199",
        "candidate_id": "cand-11136",
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(end),
        "note": (
            "Verbal mention of the described etching; the sentence identifies the "
            "print through its making and sitter, without giving a separate title."
        ),
    }
    for key, value in new_values.items():
        new_fields[col[key]] = value
    output.append(csv_row(new_fields, "\n"))
    changed.append("m-chp20-p409-054")
    result = "".join(output).encode("utf-8")
    return (b"\xef\xbb\xbf" + result if has_bom else result), changed


def segment_text(source: str, start_line: int, end_line: int) -> str:
    lines = source.splitlines()
    return "\n".join(lines[start_line - 1:end_line])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write reviewed table changes")
    args = parser.parse_args()

    source_path = ROOT / SOURCE_REL
    source_raw = require_hash(source_path, EXPECTED[SOURCE_REL.as_posix()])
    source = source_raw.decode("utf-8")
    p409 = segment_text(source, 187, 199)
    p410 = segment_text(source, 201, 209)
    if sha256(p409.encode("utf-8")) != "4069d1a70c6f7c47738ad808a9903b2a9686fe2f93040ce2824b5e7ede8b68b9":
        raise SystemExit("p.409 source-segment hash mismatch")
    if sha256(p410.encode("utf-8")) != "f4e39e0fcef93589ba4c19903bcdf28327563e5bed48058ba6dc841a159b7932":
        raise SystemExit("p.410 source-segment hash mismatch")

    segments_path = ROOT / SEGMENTS_REL
    segments = [json.loads(line) for line in segments_path.read_text(encoding="utf-8").splitlines()]
    expected_segments = {
        "chp-20:20_CHP-20Postscript:l187-199": "4069d1a70c6f7c47738ad808a9903b2a9686fe2f93040ce2824b5e7ede8b68b9",
        "chp-20:20_CHP-20Postscript:l201-209": "f4e39e0fcef93589ba4c19903bcdf28327563e5bed48058ba6dc841a159b7932",
    }
    for segment in segments:
        segment_id = segment.get("segment_id")
        if segment_id in expected_segments and segment.get("sha256") != expected_segments[segment_id]:
            raise SystemExit(f"Segment registry mismatch: {segment_id}")

    statements_path = ROOT / STATEMENTS_REL
    mentions_path = ROOT / MENTIONS_REL
    statements_raw = require_hash(statements_path, EXPECTED[STATEMENTS_REL.as_posix()])
    mentions_raw = require_hash(mentions_path, EXPECTED[MENTIONS_REL.as_posix()])
    next_statements, changed_statements = encode_jsonl_updates(statements_raw)
    next_mentions, changed_mentions = encode_mention_updates(mentions_raw, p409)

    print(json.dumps({
        "mode": "apply" if args.apply else "preview",
        "statements_changed": changed_statements,
        "mentions_changed": changed_mentions,
        "mentions_added": 1,
        "p409_work_mention_span": {
            "start_char": segment_text(source, 187, 199).find(
                "etched for Algarotti the rather epicene features of a singer called Felice Salimbeni"
            ),
            "surface_form": (
                "etched for Algarotti the rather epicene features of a singer called "
                "Felice Salimbeni"
            ),
        },
        "statements_sha256_before": sha256(statements_raw),
        "statements_sha256_after": sha256(next_statements),
        "mentions_sha256_before": sha256(mentions_raw),
        "mentions_sha256_after": sha256(next_mentions),
    }, ensure_ascii=True, indent=2))

    if not args.apply:
        return

    statement_backup = statements_path.with_name(statements_path.name + BACKUP_SUFFIX)
    mention_backup = mentions_path.with_name(mentions_path.name + BACKUP_SUFFIX)
    if statement_backup.exists() or mention_backup.exists():
        raise SystemExit("Refusing to overwrite an existing recovery backup")
    shutil.copy2(statements_path, statement_backup)
    shutil.copy2(mentions_path, mention_backup)
    statements_path.write_bytes(next_statements)
    mentions_path.write_bytes(next_mentions)
    print(f"Backups: {statement_backup.name}, {mention_backup.name}")


if __name__ == "__main__":
    main()
