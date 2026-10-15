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
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE = ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
BACKUP = MENTIONS.with_name(
    MENTIONS.name + ".bak-s2-chp3-sec-iv-l35-46-mention-offset-fix-20261010"
)
EXPECTED_MENTIONS_SHA256 = "02aab28e3fcb157a2f347f2db55464cd2b054d60080343c6cbed4464c89731df"
EXPECTED_SOURCE_SHA256 = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l35-46"
FIXES = {
    "m-chp3-seciv-l35-46-0058": {
        "surface_form": "the general public",
        "old": ("2314", "2332"),
        "new": ("2324", "2342"),
    },
    "m-chp3-seciv-l35-46-0059": {
        "surface_form": "The experts",
        "old": ("2231", "2242"),
        "new": ("2241", "2252"),
    },
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, payload: bytes) -> None:
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=path.name + ".s2tmp-", delete=False
        ) as stream:
            stream.write(payload)
            temp = Path(stream.name)
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def read_segments(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Correct two S2 mention spans to match the table audit's inclusive segment range."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write only after fixed hash, row, and source-span preflight checks pass; default is dry-run.",
    )
    args = parser.parse_args()

    require(digest(MENTIONS) == EXPECTED_MENTIONS_SHA256, "mentions table hash changed")
    require(digest(SOURCE) == EXPECTED_SOURCE_SHA256, "source hash changed")
    require(not BACKUP.exists(), f"recovery backup already exists: {BACKUP.name}")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_rows = [row for row in read_segments(SEGMENTS) if row.get("segment_id") == SEGMENT_ID]
    require(len(segment_rows) == 1, "target segment is missing or duplicated")
    start_line = segment_rows[0].get("line_start")
    end_line = segment_rows[0].get("line_end")
    require((start_line, end_line) == (35, 46), "target segment line range changed")
    segment_text = "\n".join(source_lines[start_line - 1 : end_line])

    raw = MENTIONS.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    prefix = "\ufeff" if raw.startswith(b"\xef\xbb\xbf") else ""
    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    require(len(rows) == 27522, "mention row count changed")
    selected = {row["mention_id"]: row for row in rows if row["mention_id"] in FIXES}
    require(set(selected) == set(FIXES), "target mention set changed")

    for mention_id, fix in FIXES.items():
        row = selected[mention_id]
        require(row["segment_id"] == SEGMENT_ID, f"mention segment changed: {mention_id}")
        require(row["surface_form"] == fix["surface_form"], f"mention surface changed: {mention_id}")
        require(
            (row["start_char"], row["end_char"]) == fix["old"],
            f"mention offsets changed: {mention_id}",
        )
        start = segment_text.index(fix["surface_form"])
        end = start + len(fix["surface_form"])
        require((str(start), str(end)) == fix["new"], f"computed span changed: {mention_id}")
        require(segment_text[start:end] == fix["surface_form"], f"source span mismatch: {mention_id}")
        row["start_char"], row["end_char"] = str(start), str(end)

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline)
    writer.writeheader()
    writer.writerows(rows)
    payload = (prefix + output.getvalue()).encode("utf-8")

    print("APPLY" if args.apply else "DRY_RUN", "mention_offset_repairs=2")
    for mention_id, fix in FIXES.items():
        print(f"  {mention_id}: {fix['old']} -> {fix['new']} ({fix['surface_form']})")
    print(f"source_segment={SEGMENT_ID} lines={start_line}-{end_line}")

    if not args.apply:
        return

    shutil.copy2(MENTIONS, BACKUP)
    atomic_write(MENTIONS, payload)
    require(digest(BACKUP) == EXPECTED_MENTIONS_SHA256, "backup hash mismatch after copy")
    require(len(list(csv.DictReader(MENTIONS.open(encoding="utf-8-sig", newline="")))) == 27522,
            "postwrite mention row count mismatch")
    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        written = {row["mention_id"]: row for row in csv.DictReader(stream) if row["mention_id"] in FIXES}
    require(set(written) == set(FIXES), "postwrite target mentions missing")
    for mention_id, fix in FIXES.items():
        row = written[mention_id]
        require((row["start_char"], row["end_char"]) == fix["new"], f"postwrite span mismatch: {mention_id}")
        begin, end = map(int, fix["new"])
        require(segment_text[begin:end] == row["surface_form"], f"postwrite source mismatch: {mention_id}")
    print(f"backup={BACKUP.relative_to(ROOT).as_posix()}")
    print(f"backup_sha256={digest(BACKUP)}")
    print(f"mentions_sha256={digest(MENTIONS)}")


if __name__ == "__main__":
    main()
