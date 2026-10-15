#!/usr/bin/env python3
"""Repair one nested mention span after the S2 p.84 batch audit."""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import tempfile
import os
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
SEGMENTS = TABLES / "segments.jsonl"
MENTIONS = TABLES / "mentions.csv"
SEGMENT_ID = "chp-3:03_CHP-3_sec_iv:l75-81"
SOURCE_SHA256 = "0b2a3412f679bc74e0427612522dad0df1ad9386e941f7646a6983dc76132aed"
SEGMENT_SHA256 = "ca3918cad3d1cb136990435e0f88b5ae190063146c4692673fba1399a9103c32"
MENTIONS_SHA256 = "e121d964d6b905cbc9374198b3fd926ff202b44f272f7cbeed14c4776947ca45"
MENTION_ID = "m-chp3-seciv-l75-81-0010"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("PREFLIGHT FAILED: " + message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    require(sha(SOURCE) == SOURCE_SHA256, "source file changed")
    require(sha(MENTIONS) == MENTIONS_SHA256, "mentions.csv changed")
    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    text = "\n".join(source_lines[74:81])
    segments = [__import__("json").loads(x) for x in SEGMENTS.read_text(encoding="utf-8").splitlines() if x.strip()]
    segment = [row for row in segments if row.get("segment_id") == SEGMENT_ID]
    require(len(segment) == 1 and segment[0].get("sha256") == SEGMENT_SHA256, "S0 segment changed")
    require(hashlib.sha256(text.encode("utf-8")).hexdigest() == SEGMENT_SHA256, "reconstructed segment hash mismatch")

    with MENTIONS.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    selected = [row for row in rows if row["mention_id"] == MENTION_ID]
    require(len(selected) == 1, "expected exactly one work mention")
    row = selected[0]
    require(
        (row["segment_id"], row["candidate_id"], row["surface_form"], row["start_char"], row["end_char"])
        == (SEGMENT_ID, "cand-5289", "S. Maria Maggiore", "318", "335"),
        "existing mention mapping changed",
    )
    new_surface = text[291:335]
    require(new_surface == "mosaics in S. Prassede and S. Maria Maggiore", "unexpected coordinated phrase")
    require(not any(
        other is not row and other["segment_id"] == SEGMENT_ID
        and other["start_char"] == "291" and other["end_char"] == "335"
        for other in rows
    ), "target span already exists")
    row["surface_form"] = new_surface
    row["start_char"] = "291"
    row["end_char"] = "335"
    row["note"] = "Coordinated mosaic phrase; this candidate covers the S. Maria Maggiore component, separately mapped as a place in cand-0712."
    print("mode:", "apply" if args.apply else "dry-run")
    print("mention:", MENTION_ID, "cand-5289 -> span [291,335)")
    print("surface:", new_surface)
    print("The S. Maria Maggiore place mention remains nested at [318,335).")
    if not args.apply:
        print("No files were written.")
        return

    backup = MENTIONS.with_name(MENTIONS.name + ".bak-s2-chp3-sec-iv-l75-81-maria-mention-20261011")
    require(not backup.exists(), "recovery-copy path already exists")
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    payload = b"\xef\xbb\xbf" + output.getvalue().encode("utf-8")
    fd, name = tempfile.mkstemp(prefix=MENTIONS.name + ".tmp-", dir=MENTIONS.parent)
    os.close(fd)
    temp = Path(name)
    try:
        temp.write_bytes(payload)
        shutil.copy2(MENTIONS, backup)
        os.replace(temp, MENTIONS)
    finally:
        temp.unlink(missing_ok=True)
    print("apply complete; recovery copy:", backup.relative_to(ROOT))
    print("pre-write sha256:", MENTIONS_SHA256)
    print("post-write sha256:", sha(MENTIONS))


if __name__ == "__main__":
    main()
