from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
EXPECTED_SHA = "c2a8747dffe7da2b2e5b275e72e5eeb633ed335415a766aae0d06143a53d516a"
OLD_REF = "chp-2:02_CHP-2_sec_iv:l114-125#L120-L121"
NEW_REF = "chp-2:02_CHP-2_sec_iv:l114-125#L121"
BACKUP = TABLE.with_name("entity-candidates.csv.bak-s2-cand11893-source-ref-20261013")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    before = hashlib.sha256(raw).hexdigest()
    if before != EXPECTED_SHA:
        raise SystemExit(f"protected candidate table changed: expected {EXPECTED_SHA}, found {before}")
    with TABLE.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields, rows = list(reader.fieldnames or []), list(reader)
    matches = [row for row in rows if row.get("candidate_id") == "cand-11893"]
    if len(matches) != 1 or matches[0].get("candidate_source_ref") != OLD_REF:
        raise SystemExit("cand-11893 does not have the expected source reference")
    matches[0]["candidate_source_ref"] = NEW_REF
    buffer = io.StringIO(newline="")
    ending = "\r\n" if b"\r\n" in raw else "\n"
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator=ending, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    payload = buffer.getvalue().encode("utf-8")
    rendered = (b"\xef\xbb\xbf" + payload) if raw.startswith(b"\xef\xbb\xbf") else payload
    print(f"cand-11893: {OLD_REF} -> {NEW_REF}")
    print(f"sha256={before} -> {hashlib.sha256(rendered).hexdigest()}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    tmp = TABLE.with_name(TABLE.name + ".tmp-s2-cand11893-ref")
    tmp.write_bytes(rendered)
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
