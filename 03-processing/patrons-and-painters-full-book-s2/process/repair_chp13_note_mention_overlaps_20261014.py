"""Repair ambiguous and crossing S2 mention spans in the chp-13 notes segment.

Default mode is a dry run. Pass --apply to write the reviewed repair after all
hash, source-span, candidate, and overlap preconditions pass.
"""
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
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
SEGMENTS = TABLES / "segments.jsonl"
CANDIDATES = TABLES / "entity-candidates.csv"
SEGMENT_ID = "chp-13:13_CHP-13_intro:l179-251"
SEGMENT_SHA256 = "f592d5913122cf2c4c2e7db9a39b8016c82dbc232a869018793ef11096faacb9"
MENTIONS_SHA256 = "9b568034eb69593a85a0602c18430d1a6c80798d952541f3d1f7c787b7d96361"
BACKUP_SUFFIX = ".bak-s2-ch13-notes-mention-overlap-repair-20261014"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv_bytes(path: Path) -> tuple[list[str], list[dict[str, str]], bool]:
    payload = path.read_bytes()
    has_bom = payload.startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader), has_bom


def segment_text() -> str:
    records = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    row = next((item for item in records if item.get("segment_id") == SEGMENT_ID), None)
    if row is None or row.get("sha256") != SEGMENT_SHA256:
        raise ValueError("segment registry entry or source-segment hash changed")
    source = (ROOT / row["source_file"]).read_text(encoding="utf-8-sig")
    lines = source.splitlines()
    return "\n".join(lines[int(row["line_start"]) - 1 : int(row["line_end"])])


def validate_rows(rows: list[dict[str, str]], text: str, candidate_ids: set[str]) -> None:
    segment_rows = [row for row in rows if row["segment_id"] == SEGMENT_ID]
    for row in segment_rows:
        start, end = int(row["start_char"]), int(row["end_char"])
        if text[start:end] != row["surface_form"]:
            raise ValueError(f"source span mismatch: {row['mention_id']}")
        if row["candidate_id"] not in candidate_ids:
            raise ValueError(f"unknown candidate: {row['mention_id']} -> {row['candidate_id']}")
    intervals = sorted((int(r["start_char"]), int(r["end_char"]), r["mention_id"]) for r in segment_rows)
    for index, left in enumerate(intervals):
        for right in intervals[index + 1 :]:
            if right[0] >= left[1]:
                break
            nested = (left[0] <= right[0] and right[1] <= left[1]) or (right[0] <= left[0] and left[1] <= right[1])
            if left[:2] == right[:2] or not nested:
                raise ValueError(f"duplicate or crossing spans: {left[2]} / {right[2]}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the repair after all preconditions pass")
    args = parser.parse_args()

    original = MENTIONS.read_bytes()
    if sha256(original) != MENTIONS_SHA256:
        raise SystemExit(f"mentions.csv precondition failed: {sha256(original)}")
    fields, rows, has_bom = read_csv_bytes(MENTIONS)
    if fields != ["mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note"]:
        raise SystemExit(f"unexpected mentions.csv columns: {fields}")
    text = segment_text()
    if sha256(text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("source segment changed")
    with CANDIDATES.open(encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["candidate_id"] for row in csv.DictReader(handle)}

    by_id = {row["mention_id"]: row for row in rows}
    remove_ids = {
        "m-s2-ch13-notes-20261014-009",  # author span duplicated a source citation candidate
        "m-s2-ch13-notes-20261014-050",
        "m-s2-ch13-notes-20261014-110",  # shared repository name does not identify either record
        "m-s2-ch13-notes-20261014-112",
    }
    if not remove_ids.issubset(by_id):
        raise SystemExit("one or more expected overlapping mention rows are absent")

    # Split the author's name from the citation locator so each span has one referent.
    by_id["m-s2-ch13-notes-20261014-163"].update(
        surface_form="1917, p. 145", start_char="4793", end_char="4805", note="Citation locator as printed."
    )
    by_id["m-s2-ch13-notes-20261014-164"].update(
        candidate_id="cand-9947", surface_form="Lorenzetti", start_char="4781", end_char="4791", note="Author named in the citation."
    )

    # The painting titles identify the paintings; the printed catalogue numbers identify the engravings.
    by_id["m-s2-ch13-notes-20261014-201"].update(
        surface_form="41", start_char="7019", end_char="7021", note="Engraving number as printed."
    )
    by_id["m-s2-ch13-notes-20261014-203"].update(
        surface_form="84", start_char="7026", end_char="7028", note="Engraving number as printed."
    )

    new_rows = [
        {
            "mention_id": "m-s2-ch13-notes-20261014-267",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-9947",
            "surface_form": "Lorenzetti",
            "start_char": "4615",
            "end_char": "4625",
            "note": "Author named in the citation.",
        },
        {
            "mention_id": "m-s2-ch13-notes-20261014-268",
            "segment_id": SEGMENT_ID,
            "candidate_id": "cand-10205",
            "surface_form": "Third letter",
            "start_char": "6760",
            "end_char": "6772",
            "note": "Cross-reference within the cited letter group.",
        },
    ]
    if any(row["candidate_id"] not in candidate_ids for row in new_rows):
        raise SystemExit("new mention refers to an unknown candidate")
    rows = [row for row in rows if row["mention_id"] not in remove_ids]
    rows.extend(new_rows)
    if sum(row["segment_id"] == SEGMENT_ID for row in rows) != 264:
        raise SystemExit("unexpected repaired segment mention count")
    validate_rows(rows, text, candidate_ids)

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    payload = stream.getvalue().encode("utf-8")
    if has_bom:
        payload = b"\xef\xbb\xbf" + payload

    if not args.apply:
        print(f"dry_run=true; removed={len(remove_ids)}; added={len(new_rows)}; segment_mentions=264")
        print(f"before_sha256={sha256(original)}; proposed_sha256={sha256(payload)}")
        print("all repaired source spans match and the segment has no duplicate or crossing offsets")
        return 0

    backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup}")
    shutil.copy2(MENTIONS, backup)
    try:
        MENTIONS.write_bytes(payload)
        if sha256(MENTIONS.read_bytes()) != sha256(payload):
            raise OSError("post-write hash mismatch")
        _, written_rows, _ = read_csv_bytes(MENTIONS)
        validate_rows(written_rows, text, candidate_ids)
    except Exception:
        shutil.copy2(backup, MENTIONS)
        raise
    print(f"applied=true; backup={backup.name}; mentions_sha256={sha256(payload)}; segment_mentions=264")
    return 0


if __name__ == "__main__":
    sys.exit(main())
