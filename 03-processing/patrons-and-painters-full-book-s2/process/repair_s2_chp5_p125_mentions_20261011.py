from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md"
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
SOURCE_SHA256 = "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee"
SEGMENT_ID = "chp-5:05_CHP-5_sec_i:l51-58"
SEGMENT_SHA256 = "4608edfb8cd37a6e30c08ff2a88ac9896834e424339dad4474c4f5c4bf57075c"
MENTIONS_SHA256 = "d34735b81f51072fb9136254ca7d7f79f48fa6f21bf7e49ed83d2c2464644964"
BACKUP_SUFFIX = ".bak-s2-chp5-p125-mention-overlap-repair-20261011"
REMOVE = {
    "m-chp5-p125-0041": ("cand-11729", "church of S. Bartolomeo", "2185", "2208"),
    "m-chp5-p125-0047": ("cand-11735", "S. Bartolomeo all’Isola", "2757", "2780"),
}
UPDATE_NOTES = {
    "m-chp5-p125-0019": (
        "cand-11729",
        "Named church and courtyard venue; distinct from S. Bartolomeo all’Isola.",
    ),
    "m-chp5-p125-0020": (
        "cand-11735",
        "Site named for less important name-day exhibitions; organizer identity remains unresolved.",
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove two duplicate p.125 venue mentions; dry-run by default.")
    parser.add_argument("--apply", action="store_true", help="write the validated mention repair")
    args = parser.parse_args()

    if sha(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("STOP: canonical source changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment = "\n".join(source_lines[50:58])
    if sha(segment.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("STOP: p.125 S0 segment changed")
    raw = MENTIONS.read_bytes()
    if sha(raw) != MENTIONS_SHA256:
        raise SystemExit(f"STOP: mention table changed: {sha(raw)}")
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    headers = reader.fieldnames
    rows = list(reader)
    by_id = {row["mention_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise SystemExit("STOP: duplicate mention IDs")

    for mention_id, expected in REMOVE.items():
        row = by_id.get(mention_id)
        if row is None or (
            row["candidate_id"], row["surface_form"], row["start_char"], row["end_char"]
        ) != expected:
            raise SystemExit(f"STOP: duplicate mention no longer matches expected source span: {mention_id}")
        start, end = int(row["start_char"]), int(row["end_char"])
        if segment[start:end] != row["surface_form"]:
            raise SystemExit(f"STOP: duplicate mention span does not match p.125 source: {mention_id}")

    for mention_id, (candidate_id, note) in UPDATE_NOTES.items():
        row = by_id.get(mention_id)
        if row is None or row["segment_id"] != SEGMENT_ID or row["candidate_id"] != candidate_id:
            raise SystemExit(f"STOP: retained venue mention changed: {mention_id}")
        row["note"] = note

    removed = [row for row in rows if row["mention_id"] in REMOVE]
    output_rows = [row for row in rows if row["mention_id"] not in REMOVE]
    for mention_id in REMOVE:
        del by_id[mention_id]

    offsets = {}
    for row in output_rows:
        if row["segment_id"] != SEGMENT_ID:
            continue
        key = (row["start_char"], row["end_char"])
        if key in offsets:
            raise SystemExit(f"STOP: duplicate p.125 mention offsets remain: {offsets[key]} and {row['mention_id']}")
        offsets[key] = row["mention_id"]

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator=newline, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(output_rows)
    output = (b"\xef\xbb\xbf" if bom else b"") + buffer.getvalue().encode("utf-8")
    print("source, p.125 segment, mention table hash, duplicate IDs and exact spans verified")
    print("remove:", ", ".join(row["mention_id"] for row in removed))
    print("update retained mention notes:", ", ".join(UPDATE_NOTES))
    print(f"mentions: {len(rows)} -> {len(output_rows)}; sha256={sha(output)}")
    if not args.apply:
        print("dry-run only; no file written")
        return 0

    backup = MENTIONS.with_name(MENTIONS.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"STOP: recovery copy already exists: {backup.name}")
    shutil.copy2(MENTIONS, backup)
    temp = MENTIONS.with_name(MENTIONS.name + ".tmp-s2-chp5-p125-overlap-repair")
    try:
        temp.write_bytes(output)
        temp.replace(MENTIONS)
    except Exception:
        shutil.copy2(backup, MENTIONS)
        raise
    print(f"written; recovery copy: {backup.name}; sha256={sha(MENTIONS.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
