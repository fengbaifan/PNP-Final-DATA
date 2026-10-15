from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/entity-candidates.csv"
BACKUP = TABLE.with_name("entity-candidates.csv.bak-s2-source-ref-repair-20261013")
EXPECTED_SHA = "c606b8ce9cb40044830f5a496205936920fcbe133d37a9647543ddc91f80288c"
REFS = {
    "cand-11903": ("chp-4:04_CHP-4_intro:l3-8#L7-8", "chp-4:04_CHP-4_intro:l3-8#L7"),
    "cand-11908": ("chp-5:05_CHP-5_sec_i:l9-15#L10-11", "chp-5:05_CHP-5_sec_i:l9-15#L10"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render(raw: bytes, fields: list[str], rows: list[dict[str, str]]) -> bytes:
    newline = "\r\n" if b"\r\n" in raw else "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator=newline, extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    body = output.getvalue().encode("utf-8")
    return b"\xef\xbb\xbf" + body if raw.startswith(b"\xef\xbb\xbf") else body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    if sha(raw) != EXPECTED_SHA:
        raise SystemExit("candidate table changed; re-audit before applying")
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    fields, rows = list(reader.fieldnames or []), list(reader)
    by_id = {row["candidate_id"]: row for row in rows}
    for candidate_id, (old, new) in REFS.items():
        row = by_id.get(candidate_id)
        if not row or row.get("candidate_source_ref") != old:
            raise SystemExit(f"protected candidate source reference changed: {candidate_id}")
        row["candidate_source_ref"] = new
    output = render(raw, fields, rows)
    print("Candidate source reference preview:")
    for candidate_id, (old, new) in REFS.items():
        print(f"{candidate_id}: {old} -> {new}")
    print(f"{TABLE.relative_to(ROOT)}: {sha(raw)} -> {sha(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    shutil.copy2(TABLE, BACKUP)
    temporary = TABLE.with_name(TABLE.name + ".tmp-s2-source-ref-repair")
    temporary.write_bytes(output)
    temporary.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
