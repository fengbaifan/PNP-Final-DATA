from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MENTIONS = ROOT / "04-knowledge" / "tables" / "mentions.csv"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
BACKUP = MENTIONS.with_name(MENTIONS.name + ".bak-s2-ch13-p332-audience-offset-fix-20261014")
EXPECTED_HASH = "8579120301b8600d8a158e3bcb3676b726718a24b8a56b81a122f0b4ec404756"
SOURCE_HASH = "c0b93d35aab60ec8261eb14db1e2f1b4d9ec7cae9709e19f236ccddbd12996a8"
MENTION_ID = "m-s2-ch13-p332-036"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct p.332 audience mention to segment-relative offsets")
    parser.add_argument("--apply", action="store_true", help="write after exact-hash and source-span preflight")
    args = parser.parse_args()

    if sha(MENTIONS) != EXPECTED_HASH or sha(SOURCE) != SOURCE_HASH:
        raise SystemExit("preflight hash mismatch; no writes made")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[2:12])
    local = source_lines[11].find("travellers")
    if local != 315 or source_lines[11][local:local + 10] != "travellers":
        raise SystemExit("p.332 source surface changed")
    line12_start = len("\n".join(source_lines[2:11])) + 1
    start, end = line12_start + local, line12_start + local + 10
    if (start, end) != (2055, 2065) or segment_text[start:end] != "travellers":
        raise SystemExit("computed segment-relative span does not match source")

    with MENTIONS.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    matches = [row for row in rows if row["mention_id"] == MENTION_ID]
    if len(matches) != 1:
        raise SystemExit(f"expected one target mention, found {len(matches)}")
    row = matches[0]
    if (row["candidate_id"], row["surface_form"], row["start_char"], row["end_char"]) != (
        "cand-12119", "travellers", "315", "325"
    ):
        raise SystemExit("target mention changed from expected incorrect line-relative state")
    row["start_char"], row["end_char"] = str(start), str(end)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=MENTIONS.parent, delete=False) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp = Path(stream.name)
    data = temp.read_bytes()
    print(f"{MENTION_ID}: segment-relative [{start}, {end}); surface={segment_text[start:end]!r}")
    print("planned mentions.csv sha256:", hashlib.sha256(data).hexdigest())
    if not args.apply:
        temp.unlink()
        print("preview only; no files written")
        return 0
    if BACKUP.exists():
        temp.unlink()
        raise SystemExit(f"backup already exists; refusing overwrite: {BACKUP.name}")
    shutil.copy2(MENTIONS, BACKUP)
    temp.replace(MENTIONS)
    print("applied; backup:", BACKUP.name)
    print("written mentions.csv sha256:", sha(MENTIONS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
