#!/usr/bin/env python3
"""Repair two verified broken statement-ID links in Chapter 5.

Default mode previews the exact two-field repair. --apply writes only the
affected JSONL records after checking the source and table fingerprints.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
EXPECTED_TABLE_SHA256 = "32f4218d1c22fa7d7489def330c76ec6c9961cdf3b95f00dd3b1b6170bfae346"
SOURCE_HASHES = {
    "02-sources/02-Markdown/05_CHP-5_sec_iii.md": "9b095b1a93570102ad2cdb117580f2fbeccd2ff017033a2f66557c58a0d1ef0a",
    "02-sources/02-Markdown/05_CHP-5_sec_i.md": "8ef51cd646ed6abf398c9faeb47df9a03f70de696d9a871c6d0b734b2adeeeee",
}
BACKUP_SUFFIX = ".bak-s2-ch5-recursive-statement-links-20261015"
UPDATES = {
    "st-chp5-p137-careful-work-characterization-partial": (
        ("qualifiers", "continued_by_statement_id"),
        "st-chp5-p138-cerquozzi-careful-in-work",
        "st-chp5-p138-cerquozzi-careful-and-conscientious-in-work",
    ),
    "st-chp5-note-p124-n1-castiglione-publisher-identification": (
        ("qualifiers", "linked_body_statement_ids"),
        ["st-chp5-p124-simonelli-castiglione-print", "st-chp5-note-p124-castiglione-dedication-interpretation"],
        ["st-chp5-p124-simonelli-castiglione-print", "st-chp5-p124-castiglione-dedication-interpretation"],
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write after previewing the fixed repairs")
    args = parser.parse_args()

    original = TABLE.read_bytes()
    if sha256(original) != EXPECTED_TABLE_SHA256:
        raise SystemExit("statement table changed; rebuild and review preconditions")
    for rel, expected in SOURCE_HASHES.items():
        if sha256((ROOT / rel).read_bytes()) != expected:
            raise SystemExit(f"source changed: {rel}")

    records = [
        json.loads(line)
        for line in original.decode("utf-8").splitlines()
        if line.strip()
    ]
    ids = {row.get("statement_id") for row in records}
    required_targets = {
        "st-chp5-p138-cerquozzi-careful-and-conscientious-in-work",
        "st-chp5-p124-simonelli-castiglione-print",
        "st-chp5-p124-castiglione-dedication-interpretation",
    }
    if not required_targets.issubset(ids):
        raise SystemExit(f"verified target statement missing: {sorted(required_targets - ids)}")

    output: list[bytes] = []
    seen: set[str] = set()
    details: list[dict[str, str]] = []
    for raw in original.decode("utf-8").splitlines(keepends=True):
        ending = "\r\n" if raw.endswith("\r\n") else "\n" if raw.endswith("\n") else ""
        body = raw[:-len(ending)] if ending else raw
        row = json.loads(body)
        sid = row.get("statement_id")
        if sid not in UPDATES:
            output.append(raw.encode("utf-8"))
            continue
        if sid in seen:
            raise SystemExit(f"duplicate source statement: {sid}")
        seen.add(sid)
        path, expected_old, new_value = UPDATES[sid]
        current = row
        for key in path:
            current = current[key]
        if current != expected_old:
            raise SystemExit(f"unexpected pointer in {sid}: {current!r}")
        current_parent = row
        for key in path[:-1]:
            current_parent = current_parent[key]
        current_parent[path[-1]] = new_value
        output.append((json.dumps(row, ensure_ascii=False) + ending).encode("utf-8"))
        details.append({"statement_id": sid, "from": str(expected_old), "to": str(new_value)})

    if seen != set(UPDATES):
        raise SystemExit(f"source statements missing: {sorted(set(UPDATES) - seen)}")
    updated = b"".join(output)
    print(json.dumps({
        "mode": "apply" if args.apply else "preview",
        "repairs": details,
        "before_sha256": sha256(original),
        "after_sha256": sha256(updated),
        "backup": TABLE.name + BACKUP_SUFFIX,
    }, ensure_ascii=True, indent=2))
    if not args.apply:
        return

    backup = TABLE.with_name(TABLE.name + BACKUP_SUFFIX)
    if backup.exists():
        raise SystemExit(f"backup already exists: {backup.name}")
    shutil.copy2(TABLE, backup)
    temporary: Path | None = None
    try:
        fd, name = tempfile.mkstemp(prefix=f".{TABLE.name}.", suffix=".tmp", dir=TABLE.parent)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(updated)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, TABLE)
    except Exception:
        shutil.copy2(backup, TABLE)
        raise
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


if __name__ == "__main__":
    main()
