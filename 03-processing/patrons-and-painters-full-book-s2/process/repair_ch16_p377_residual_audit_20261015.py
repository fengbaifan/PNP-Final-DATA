#!/usr/bin/env python3
"""Repair three narrowly scoped issues found by strict S2 table audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SEGMENT_ID = "chp-16:16_CHP-16_intro:l48-64"
EXPECTED = {
    "entity-candidates.csv": "dc1830908fc671cc995b6e88ca8a94a6f826ed1044eb0fb11685e42dd88ce709",
    "book-statements.jsonl": "9b8f4c0f8df295ae8bb472f8a82cde9e8712383fc12899f9ac5b231fb1c0b03f",
}
BACKUP_SUFFIX = ".bak-s2-ch16-p377-audit-fix-20261015"
PERSON_ID = "cand-12253"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_outputs() -> dict[Path, bytes]:
    candidate_path = TABLES / "entity-candidates.csv"
    statements_path = TABLES / "book-statements.jsonl"
    candidate_raw = candidate_path.read_bytes()
    statement_raw = statements_path.read_bytes()
    for path, raw in ((candidate_path, candidate_raw), (statements_path, statement_raw)):
        expected = EXPECTED[path.name]
        actual = digest(raw)
        if actual != expected:
            raise ValueError(f"Stale input {path.name}: {actual}")

    old_ref = f"{SEGMENT_ID}#L63-L64".encode()
    new_ref = f"{SEGMENT_ID}#L64".encode()
    if candidate_raw.count(old_ref) != 1:
        raise ValueError("Expected exactly one candidate source ref to repair.")
    candidate_out = candidate_raw.replace(old_ref, new_ref, 1)

    bom = b"\xef\xbb\xbf" if statement_raw.startswith(b"\xef\xbb\xbf") else b""
    body = statement_raw[len(bom) :]
    outputs: list[bytes] = []
    seen: set[str] = set()
    target_ids = {
        "st-chp16-p377-note3-ghelthof-provenance-claim",
        "st-chp16-p377-note3-state-archive-locator",
    }
    for raw_line in body.splitlines(keepends=True):
        ending = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n" if raw_line.endswith(b"\n") else b""
        line_body = raw_line[: -len(ending)] if ending else raw_line
        row = json.loads(line_body)
        statement_id = row.get("statement_id")
        if statement_id == "st-chp16-p377-note3-ghelthof-provenance-claim":
            q = row["qualifiers"]
            q["source_line_start"] = 64
            q["source_line_end"] = 64
            row["original_quote"] = "is claimed to belong to Urbani de Ghelthof’s own collection"
            outputs.append(json.dumps(row, ensure_ascii=False).encode("utf-8") + ending)
            seen.add(statement_id)
        elif statement_id == "st-chp16-p377-note3-state-archive-locator":
            q = row["qualifiers"]
            q["relation_candidate"] = True
            q["relation_candidate_note"] = (
                "The note locates Swajer's papers and manuscripts in a specific archive record."
            )
            outputs.append(json.dumps(row, ensure_ascii=False).encode("utf-8") + ending)
            seen.add(statement_id)
        else:
            outputs.append(raw_line)
    if seen != target_ids:
        raise ValueError(f"Missing target rows: {sorted(target_ids - seen)}")

    return {
        candidate_path: candidate_out,
        statements_path: bom + b"".join(outputs),
    }


def apply_outputs(outputs: dict[Path, bytes]) -> list[str]:
    backups = {path: path.with_name(path.name + BACKUP_SUFFIX) for path in outputs}
    if any(path.exists() for path in backups.values()):
        raise FileExistsError("A dated audit-fix backup already exists.")
    for path, backup in backups.items():
        shutil.copy2(path, backup)
    staged: dict[Path, Path] = {}
    try:
        for path, data in outputs.items():
            fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
            temp = Path(name)
            staged[path] = temp
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        for path, temp in staged.items():
            os.replace(temp, path)
    except Exception:
        for path, backup in backups.items():
            if backup.exists():
                shutil.copy2(backup, path)
        raise
    finally:
        for temp in staged.values():
            if temp.exists():
                temp.unlink()
    return [str(path) for path in backups.values()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    print(json.dumps({path.name: digest(data) for path, data in outputs.items()}, indent=2))
    if args.apply:
        print(json.dumps({"backups": apply_outputs(outputs)}, ensure_ascii=False, indent=2))
        print("APPLIED")
    else:
        print("PREVIEW ONLY; no tables changed.")


if __name__ == "__main__":
    main()
