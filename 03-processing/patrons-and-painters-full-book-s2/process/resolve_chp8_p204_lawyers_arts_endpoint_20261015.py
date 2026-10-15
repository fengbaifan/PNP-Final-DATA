from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge/tables"
CANDIDATES = TABLES / "entity-candidates.csv"
MENTIONS = TABLES / "mentions.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l14-21"
STATEMENT_ID = "st-chp8-p204-naples-lawyers-supported-arts"
NEW_CANDIDATE_ID = "cand-12348"
NEW_MENTION_ID = "m-chp8-p204-lawyers-support-arts"
SURFACE_FORM = "the arts"
BACKUP_SUFFIX = "bak-s2-chp8-p204-arts-term-endpoint-20261015"
EXPECTED_HASHES = {
    "entity-candidates.csv": "62ac78a5a0de70b505baa349c38cb741ce561ec3cf441aaecbb3e0f29befe8a3",
    "mentions.csv": "e47ee6770d121192112fd20f385a5b85b3c59b531b7231e530a173c3c4624b24",
    "book-statements.jsonl": "d700e38f5f740e752cf689a3686170cdc8bac215685d32fcf663ecf2eb4e8e4f",
}
EXPECTED_SEGMENT_HASH = "5cd6b281b486fa731569479441cc2a31e7ee373c60180eb5cde46840e4a602bc"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> tuple[bytes, list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return raw, list(reader.fieldnames or []), list(reader)


def append_csv(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=fields, lineterminator=newline.decode("ascii"),
        extrasaction="raise",
    )
    writer.writerows(rows)
    if raw and not raw.endswith((b"\n", b"\r")):
        raw += newline
    return raw + stream.getvalue().encode("utf-8")


def is_open_true(row: dict[str, object]) -> bool:
    qualifiers = row.get("qualifiers") or {}
    return qualifiers.get("relation_candidate") is True and (
        not row.get("subject_candidate_id") or not row.get("object_candidate_id")
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_raw, candidate_fields, candidates = read_csv(CANDIDATES)
    mention_raw, mention_fields, mentions = read_csv(MENTIONS)
    statement_raw = STATEMENTS.read_bytes()
    actual_hashes = {
        "entity-candidates.csv": candidate_raw,
        "mentions.csv": mention_raw,
        "book-statements.jsonl": statement_raw,
    }
    for name, expected in EXPECTED_HASHES.items():
        if digest(actual_hashes[name]) != expected:
            raise ValueError(f"Input table changed since preview: {name}")

    candidate_ids = {row["candidate_id"] for row in candidates}
    mention_ids = {row["mention_id"] for row in mentions}
    if NEW_CANDIDATE_ID in candidate_ids or NEW_MENTION_ID in mention_ids:
        raise ValueError("A planned candidate or mention ID already exists")
    if max(int(candidate_id.removeprefix("cand-")) for candidate_id in candidate_ids) != 12347:
        raise ValueError("Candidate sequence changed")

    segment = next(
        json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines()
        if json.loads(line).get("segment_id") == SEGMENT_ID
    )
    if segment.get("sha256") != EXPECTED_SEGMENT_HASH:
        raise ValueError("Source segment hash changed")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[int(segment["line_start"]) - 1 : int(segment["line_end"])])
    start = text.find(SURFACE_FORM)
    if start < 0 or text.find(SURFACE_FORM, start + 1) >= 0:
        raise ValueError("Source phrase missing or repeated")
    end = start + len(SURFACE_FORM)
    if any(
        row["segment_id"] == SEGMENT_ID
        and start < int(row["end_char"])
        and int(row["start_char"]) < end
        for row in mentions
    ):
        raise ValueError("New mention overlaps an existing mention")

    rows = [json.loads(line) for line in statement_raw.decode("utf-8").splitlines() if line.strip()]
    statement_index = {row["statement_id"]: index for index, row in enumerate(rows)}
    if STATEMENT_ID not in statement_index:
        raise ValueError("Target statement is missing")
    statement = rows[statement_index[STATEMENT_ID]]
    qualifiers = statement.get("qualifiers") or {}
    if (
        statement.get("segment_id") != SEGMENT_ID
        or statement.get("subject_candidate_id") != "cand-12018"
        or statement.get("object_candidate_id") is not None
        or qualifiers.get("relation_candidate") is not True
        or qualifiers.get("open_endpoint_reason") is None
    ):
        raise ValueError("Target statement identity or open endpoint changed")
    before_open = sum(is_open_true(row) for row in rows)
    if before_open != 460:
        raise ValueError(f"Open endpoint count changed: {before_open}")

    new_candidate = {
        "candidate_id": NEW_CANDIDATE_ID,
        "index_entry_id": "",
        "canonical_name": "The arts in Naples",
        "index_page_range": "",
        "suggested_type": "term",
        "status": "open",
        "index_source_file": "",
        "sub_entry": "",
        "detail": "The broad artistic and cultural activity that Haskell says Naples lawyers supported. No particular work, institution, or programme is identified; this is a generic conceptual object, not a discrete commission.",
        "exclude_reason": "",
        "candidate_origin": "body-mention",
        "candidate_source_ref": f"{SEGMENT_ID}#L17",
    }
    new_mention = {
        "mention_id": NEW_MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": NEW_CANDIDATE_ID,
        "surface_form": SURFACE_FORM,
        "start_char": str(start),
        "end_char": str(end),
        "note": "The explicit general concept that the Naples lawyers supported; no specific work, institution, or programme is implied.",
    }
    statement["object_candidate_id"] = NEW_CANDIDATE_ID
    qualifiers["mentioned_candidate_ids"] = list(dict.fromkeys(
        (qualifiers.get("mentioned_candidate_ids") or []) + [NEW_CANDIDATE_ID]
    ))
    qualifiers["relation_candidate_note"] = "The object is the explicitly named general concept 'the arts' in the Naples context. This captures the source's broad account of lawyers' support without inferring a particular work, institution, or programme."
    qualifiers.pop("open_endpoint_reason", None)
    statement["qualifiers"] = qualifiers

    candidate_after = append_csv(candidate_raw, candidate_fields, [new_candidate])
    mention_after = append_csv(mention_raw, mention_fields, [new_mention])
    statement_after = ("".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
        for row in rows
    )).encode("utf-8")
    after_open = sum(is_open_true(row) for row in rows)
    if after_open != 459:
        raise ValueError(f"Unexpected post-update open count: {after_open}")

    print(f"candidate_rows={len(candidates)}->{len(candidates) + 1}")
    print(f"mention_rows={len(mentions)}->{len(mentions) + 1}")
    print(f"statement_rows={len(rows)}->{len(rows)}")
    print(f"planned_candidate={NEW_CANDIDATE_ID}|term|{new_candidate['canonical_name']}")
    print(f"planned_mention={NEW_MENTION_ID}|{NEW_CANDIDATE_ID}|[{start},{end}) {SURFACE_FORM}")
    print(f"planned_endpoint={STATEMENT_ID}|None->{NEW_CANDIDATE_ID}")
    print(f"open_endpoints={before_open}->{after_open}")
    for path, data in ((CANDIDATES, candidate_after), (MENTIONS, mention_after), (STATEMENTS, statement_after)):
        print(f"{path.relative_to(ROOT)} {digest(path.read_bytes())}->{digest(data)}")
    if args.preview:
        return 0

    paths = ((CANDIDATES, candidate_after), (MENTIONS, mention_after), (STATEMENTS, statement_after))
    backups: list[tuple[Path, Path]] = []
    temporaries: list[tuple[Path, Path]] = []
    for path, data in paths:
        backup = path.with_name(f"{path.name}.{BACKUP_SUFFIX}")
        temp = path.with_name(f"{path.name}.tmp-{BACKUP_SUFFIX}")
        if backup.exists() or temp.exists():
            raise FileExistsError(f"Recovery or temporary file already exists: {path.name}")
        backups.append((path, backup))
        temporaries.append((path, temp))
    for path, backup in backups:
        shutil.copy2(path, backup)
    try:
        for (path, temp), (_, data) in zip(temporaries, paths, strict=True):
            temp.write_bytes(data)
        for (path, temp) in temporaries:
            temp.replace(path)
    except Exception:
        for _, temp in temporaries:
            if temp.exists():
                temp.unlink()
        raise
    for path, backup in backups:
        print(f"backup={backup.relative_to(ROOT)}")
        print(f"applied_sha256={path.relative_to(ROOT)}:{digest(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
