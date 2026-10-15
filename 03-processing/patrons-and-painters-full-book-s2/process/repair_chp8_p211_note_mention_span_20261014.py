"""Resolve the p.211 person/archive mention overlap by narrowing the archive span."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_i.md"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l84-96"
EXPECTED_MENTIONS_SHA = "cb214e12a72acb9d039d7bc005e0bb784da3a2471cf9abd518f190ea631e7fca"
BACKUP = MENTIONS.with_name("mentions.csv.bak-s2-chp8-p211-mention-span-repair-20261014")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    original = MENTIONS.read_bytes()
    if digest(original) != EXPECTED_MENTIONS_SHA:
        raise SystemExit("mentions.csv changed since the overlap was reviewed")
    if BACKUP.exists():
        raise SystemExit("repair recovery copy already exists; inspect it before applying")

    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[83:96])
    if segment_text.count("notes") != 1:
        raise SystemExit("the target 'notes' span is not unique in p.211 S0 text")
    start = segment_text.index("notes")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    by_id = {row["mention_id"]: row for row in rows}
    archive = by_id.get("m-chp8-p211-081")
    person = by_id.get("m-chp8-p211-046")
    if not archive or (archive["candidate_id"], archive["surface_form"]) != ("cand-12049", "Ghezzi’s notes"):
        raise SystemExit("archive mention no longer matches the reviewed overlap")
    if not person or person["surface_form"] != "Giuseppe Ghezzi":
        raise SystemExit("the adjacent person mention changed since review")
    if segment_text[int(person["start_char"]):int(person["end_char"])] != person["surface_form"]:
        raise SystemExit("the existing Ghezzi person offset is not exact")
    if start < int(person["end_char"]) and start + len("notes") > int(person["start_char"]):
        raise SystemExit("the narrowed archive mention still overlaps the person span")

    archive["surface_form"] = "notes"
    archive["start_char"] = str(start)
    archive["end_char"] = str(start + len("notes"))
    archive["note"] = "The plural 'notes' refers to Giuseppe Ghezzi's source notes; no title or repository is supplied here."
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output = stream.getvalue().encode("utf-8")
    print("mode:", "APPLY" if args.apply else "DRY RUN")
    print("mention:", archive["mention_id"], "surface=notes", "offsets=", archive["start_char"], archive["end_char"])
    print("mentions.csv sha256:", digest(output))
    if args.apply:
        shutil.copy2(MENTIONS, BACKUP)
        with tempfile.NamedTemporaryFile("wb", dir=MENTIONS.parent, delete=False, suffix=".tmp") as handle:
            handle.write(output)
            temporary = Path(handle.name)
        temporary.replace(MENTIONS)
        print("recovery copy:", BACKUP.relative_to(ROOT))


if __name__ == "__main__":
    main()
