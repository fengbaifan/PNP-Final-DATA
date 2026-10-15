from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-preserve-unchanged-format-20261011")
EXPECTED_HEAD = "638770a5be0599c41a8970a42d5849318ef2c869"
EXPECTED_PRE_SHA256 = "908470bdf28700f1867ef667ee0b30277cf64e5bcff3ce41bdb367037492100f"
GIT_PATH = "04-knowledge/tables/book-statements.jsonl"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_rows(data: bytes) -> list[dict]:
    return [json.loads(line) for line in data.decode("utf-8-sig").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preserve committed compact JSON bytes for semantically unchanged statements."
    )
    parser.add_argument("--apply", action="store_true", help="write the reviewed formatting-only repair")
    args = parser.parse_args()

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if head != EXPECTED_HEAD:
        raise SystemExit(f"unexpected HEAD: {head} != {EXPECTED_HEAD}")
    current = TABLE.read_bytes()
    if sha(current) != EXPECTED_PRE_SHA256:
        raise SystemExit(f"unexpected current table hash: {sha(current)} != {EXPECTED_PRE_SHA256}")
    base = subprocess.run(
        ["git", "show", f"HEAD:{GIT_PATH}"], cwd=ROOT, check=True, capture_output=True
    ).stdout

    base_rows: dict[str, tuple[dict, bytes]] = {}
    for line in base.splitlines():
        row = json.loads(line)
        sid = row["statement_id"]
        if sid in base_rows:
            raise SystemExit(f"duplicate statement ID in HEAD: {sid}")
        base_rows[sid] = (row, line)

    current_rows = parse_rows(current)
    current_ids = [row["statement_id"] for row in current_rows]
    if len(current_ids) != len(set(current_ids)):
        raise SystemExit("duplicate statement ID in current table")
    base_ids = set(base_rows)
    now_ids = set(current_ids)
    unchanged = 0
    changed = 0
    added = len(now_ids - base_ids)
    output_lines: list[bytes] = []
    for row in current_rows:
        sid = row["statement_id"]
        old = base_rows.get(sid)
        if old is not None and row == old[0]:
            output_lines.append(old[1])
            unchanged += 1
        else:
            output_lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
            changed += 1
    after = b"\n".join(output_lines) + b"\n"

    rebuilt = parse_rows(after)
    if rebuilt != current_rows:
        raise SystemExit("semantic equality check failed after preserving original row bytes")
    if (unchanged, changed, added, len(base_ids - now_ids)) != (9767, 3043, 389, 13):
        raise SystemExit(
            f"unexpected row comparison counts: unchanged={unchanged}, changed={changed}, "
            f"added={added}, deleted={len(base_ids-now_ids)}"
        )

    print(f"pre_sha256={sha(current)}")
    print(f"post_sha256={sha(after)}")
    print(f"unchanged_rows_preserved={unchanged}; changed_or_added_rows={changed}; added={added}; deleted={len(base_ids-now_ids)}")
    print("semantic_content=identical before and after")
    if not args.apply:
        print("DRY-RUN PASS; no files written")
        return 0

    if BACKUP.exists():
        raise SystemExit(f"refusing to overwrite recovery copy: {BACKUP.name}")
    temp = TABLE.with_name(TABLE.name + ".tmp-write")
    if temp.exists():
        raise SystemExit(f"temporary path already exists: {temp.name}")
    shutil.copy2(TABLE, BACKUP)
    try:
        temp.write_bytes(after)
        os.replace(temp, TABLE)
        if sha(TABLE.read_bytes()) != sha(after):
            raise SystemExit("post-write hash mismatch")
    except Exception:
        if temp.exists():
            temp.unlink()
        shutil.copy2(BACKUP, TABLE)
        raise
    print(f"backup={BACKUP.relative_to(ROOT)}")
    print(f"APPLY PASS post_sha256={sha(TABLE.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
