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
MENTIONS = TABLES / "mentions.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/07_CHP-7_sec_v.md"
SEGMENT_ID = "chp-7:07_CHP-7_sec_v:l57-60"
STATEMENT_ID = "st-chp7-p202-v-turin-attracted-painters-or-pictures"
MENTION_ID = "m-chp7-p202-v-origin-cities"
TARGET_CANDIDATE_ID = "cand-12005"
SURFACE_FORM = "more richly endowed cities"
BACKUP_SUFFIX = "bak-s2-chp7-p202-origin-cities-mention-20261015"
EXPECTED_MENTIONS_HASH = "0ea78f194a108c6dbff367756669059eee229d74ab3a0b8ff2a8f176d385d086"
EXPECTED_SEGMENT_HASH = "23f500dd20ab35e415f6e3d39bf8df9580d68fddfa74e3a502d05076458ee825"


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


def open_count(rows: list[dict[str, object]]) -> int:
    return sum(
        1 for row in rows
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and (not row.get("subject_candidate_id") or not row.get("object_candidate_id"))
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw, fields, mentions = read_csv(MENTIONS)
    if digest(raw) != EXPECTED_MENTIONS_HASH:
        raise ValueError("Mentions table changed since preview")
    if MENTION_ID in {row["mention_id"] for row in mentions}:
        raise ValueError("Planned mention ID already exists")
    candidate_ids = {row["candidate_id"] for row in read_csv(CANDIDATES)[2]}
    if TARGET_CANDIDATE_ID not in candidate_ids:
        raise ValueError("Target candidate is missing")

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

    statements = [
        json.loads(line) for line in STATEMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    statement = next(row for row in statements if row["statement_id"] == STATEMENT_ID)
    qualifiers = statement.get("qualifiers") or {}
    if (
        statement.get("segment_id") != SEGMENT_ID
        or statement.get("subject_candidate_id") != "cand-2388"
        or statement.get("object_candidate_id") is not None
        or TARGET_CANDIDATE_ID not in (qualifiers.get("mentioned_candidate_ids") or [])
    ):
        raise ValueError("The open disjunctive statement changed")
    if open_count(statements) != 460:
        raise ValueError("Open endpoint count changed")

    new_row = {
        "mention_id": MENTION_ID,
        "segment_id": SEGMENT_ID,
        "candidate_id": TARGET_CANDIDATE_ID,
        "surface_form": SURFACE_FORM,
        "start_char": str(start),
        "end_char": str(end),
        "note": "The unnamed source-city group described as more richly endowed; no individual city is identified.",
    }
    updated = append_csv(raw, fields, [new_row])
    print(f"mention_rows={len(mentions)}->{len(mentions) + 1}")
    print(f"planned_mention={MENTION_ID}|{TARGET_CANDIDATE_ID}|[{start},{end}) {SURFACE_FORM}")
    print(f"open_endpoints={open_count(statements)}->{open_count(statements)}")
    print(f"{MENTIONS.relative_to(ROOT)} {digest(raw)}->{digest(updated)}")
    if args.preview:
        return 0

    backup = MENTIONS.with_name(f"{MENTIONS.name}.{BACKUP_SUFFIX}")
    temp = MENTIONS.with_name(f"{MENTIONS.name}.tmp-{BACKUP_SUFFIX}")
    if backup.exists() or temp.exists():
        raise FileExistsError("Recovery or temporary file already exists")
    shutil.copy2(MENTIONS, backup)
    try:
        temp.write_bytes(updated)
        temp.replace(MENTIONS)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise
    print(f"backup={backup.relative_to(ROOT)}")
    print(f"applied_sha256={digest(MENTIONS.read_bytes())}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
