from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MENTIONS = ROOT / "04-knowledge/tables/mentions.csv"
BACKUP_SUFFIX = "bak-s2-chp9-p256-duplicate-mention-repair-20261015"
EXPECTED_HASH = "bfc3db7566de1fe79d3e1562b166158a3d26b5d72ed3e6c8239e1bf386c04abd"
DUPLICATE_ID = "m-chp9-p256-12380"
KEPT_ID = "m-chp9-p256-patrician-families"
ROLE_ID = "m-chp9-p256-cordellina-leading-advocate"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = MENTIONS.read_bytes()
    if digest(raw) != EXPECTED_HASH:
        raise ValueError("mentions.csv changed since this repair was reviewed")
    with MENTIONS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    by_id: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_id.setdefault(row["mention_id"], []).append(row)
    if len(by_id.get(DUPLICATE_ID, [])) != 1 or len(by_id.get(KEPT_ID, [])) != 1:
        raise ValueError("Expected exactly one duplicate and one canonical family mention")
    duplicate = by_id[DUPLICATE_ID][0]
    kept = by_id[KEPT_ID][0]
    shared = ("segment_id", "candidate_id", "surface_form", "start_char", "end_char")
    if any(duplicate[key] != kept[key] for key in ("segment_id", "surface_form", "start_char", "end_char")):
        raise ValueError("Rows do not represent the same remapped family mention")
    if duplicate["segment_id"] != "chp-9:09_CHP-9_intro:l157-165" or duplicate["candidate_id"] != "cand-12380" or kept["candidate_id"] != "cand-8108":
        raise ValueError("Duplicate mention is outside the reviewed p.256 group")
    if len(by_id.get(ROLE_ID, [])) != 1 or by_id[ROLE_ID][0]["candidate_id"] != "cand-0842":
        raise ValueError("Expected pre-update Cordellina role mention mapping is missing")

    kept["candidate_id"] = "cand-12380"
    kept["note"] = "Haskell's source-defined collective group claiming Roman descent; the scan confirms OCR 'famines' as 'families'."
    role = by_id[ROLE_ID][0]
    role["candidate_id"] = "cand-8372"
    role["note"] = "Professional-role phrase for Carlo Cordellina; the sentence identifies him as an advocate within the legal profession."

    filtered = [row for row in rows if row["mention_id"] != DUPLICATE_ID]
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator=newline.decode("ascii"))
    writer.writeheader()
    writer.writerows(filtered)
    output = stream.getvalue().encode("utf-8")
    print(f"mentions={len(rows)}->{len(filtered)}")
    print(f"removed={DUPLICATE_ID}; remapped={KEPT_ID}:cand-8108->cand-12380; {ROLE_ID}:cand-0842->cand-8372")
    print(f"sha256={digest(raw)}->{digest(output)}")
    if args.preview:
        return 0

    backup = MENTIONS.with_name(f"{MENTIONS.name}.{BACKUP_SUFFIX}")
    temporary = MENTIONS.with_name(f"{MENTIONS.name}.tmp-{BACKUP_SUFFIX}")
    if backup.exists() or temporary.exists():
        raise FileExistsError("Recovery or temporary file already exists")
    shutil.copy2(MENTIONS, backup)
    try:
        temporary.write_bytes(output)
        temporary.replace(MENTIONS)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        shutil.copy2(backup, MENTIONS)
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
