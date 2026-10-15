"""Give the p.205 Saraceni work-group mention a nested span beside the artist mention."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_i.md"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SEGMENT_ID = "chp-8:08_CHP-8_sec_i:l23-28"
MENTION_ID = "m-s2-chp8-p205-three-saraceni-works"
BASELINE_HASH = "ad34fbb00c468463484cc18555353cb0335f6a8e84b16bc9162281e98c2cc148"
SOURCE_HASH = "8449a867c1b0459a35c8ebbf7d37c0f770cd71ef0be987b12b7a1281d41e12bf"
SEGMENT_HASH = "927016e646ad420bf9f667b350e5937ba0fecf83bbcab992b7b5733703719db2"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp8-p205-saraceni-mention-fix-20261014")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    if sha(raw) != BASELINE_HASH or sha(SOURCE.read_bytes()) != SOURCE_HASH:
        raise SystemExit("mentions or source changed since this repair was reviewed")
    if BACKUP.exists():
        raise SystemExit("repair recovery copy already exists")
    segment = next(json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8").splitlines() if json.loads(line).get("segment_id") == SEGMENT_ID)
    if segment.get("sha256") != SEGMENT_HASH or (segment.get("line_start"), segment.get("line_end")) != (23, 28):
        raise SystemExit("p.205 segment metadata changed")
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(lines[22:28])
    surface = "and Carlo"
    starts = [i for i in range(len(segment_text)) if segment_text.startswith(surface, i)]
    if len(starts) != 1:
        raise SystemExit("expected one exact 'and Carlo' surface in p.205")
    with TABLE.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    target = next((row for row in rows if row["mention_id"] == MENTION_ID), None)
    artist = next((row for row in rows if row["mention_id"] == "m-chp8-p205-045"), None)
    if not target or target["surface_form"] != "Carlo" or target["candidate_id"] != "cand-12027":
        raise SystemExit("Saraceni work-group mention no longer matches expected prestate")
    if not artist or artist["surface_form"] != "Carlo" or artist["candidate_id"] != "cand-2358":
        raise SystemExit("artist mention no longer matches expected prestate")
    start = starts[0]
    target.update({
        "surface_form": surface,
        "start_char": str(start),
        "end_char": str(start + len(surface)),
        "note": "Final item in the shared 'three paintings each' list; the artist's surname completes as Saraceni on p.206. This nested span preserves the separate Carlo person mention.",
    })
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output = stream.getvalue().encode("utf-8")
    result = {"mode": "apply" if args.apply else "dry_run", "mention_id": MENTION_ID,
              "surface_form": surface, "start_char": start, "end_char": start + len(surface),
              "input_sha256": sha(raw), "output_sha256": sha(output), "recovery_copy": BACKUP.name}
    if args.apply:
        BACKUP.write_bytes(raw)
        with tempfile.NamedTemporaryFile("wb", dir=TABLE.parent, delete=False, suffix=".tmp") as handle:
            handle.write(output)
            temp = Path(handle.name)
        temp.replace(TABLE)
        if sha(TABLE.read_bytes()) != sha(output):
            raise SystemExit("post-write hash verification failed")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("applied; recovery copy written and post-write hash verified" if args.apply else "dry-run only; no files changed")


if __name__ == "__main__":
    main()
