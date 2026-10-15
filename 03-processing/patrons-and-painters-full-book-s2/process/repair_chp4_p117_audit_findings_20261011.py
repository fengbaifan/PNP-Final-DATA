#!/usr/bin/env python3
"""Repair the three exact S2 audit findings from the p.117 writeback."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l207-216"
STATEMENT_ID = "st-chp4-sec-ii-p117-poussin-independence"
OLD_REFS = {
    "cand-11667": f"{SEGMENT_ID}#L211-213",
    "cand-11668": f"{SEGMENT_ID}#L211-213",
}
NEW_REFS = {
    "cand-11667": f"{SEGMENT_ID}#L212",
    "cand-11668": f"{SEGMENT_ID}#L211",
}
EXPECTED_SHA256 = {
    "book-statements.jsonl": "cd3b13d272c396f459b09bcd389aae109dfed8339e5b48259b2852e64021440f",
    "entity-candidates.csv": "8ca70c6b5c39c73bcd325d0aeb0a4a2e5969ae4651b1bec512a98f147904b930",
}
BACKUP_SUFFIX = ".bak-s2-chp4-p117-auditfix-20261011"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.split())


def prepare() -> tuple[dict[str, Path], dict[str, bytes], dict[str, bytes]]:
    paths = {
        "book-statements.jsonl": TABLES / "book-statements.jsonl",
        "entity-candidates.csv": TABLES / "entity-candidates.csv",
    }
    original = {name: path.read_bytes() for name, path in paths.items()}
    for name, expected in EXPECTED_SHA256.items():
        actual = digest(original[name])
        if actual != expected:
            raise SystemExit(f"{name}: SHA-256 changed; expected {expected}, got {actual}")

    source_lines = SOURCE.read_text(encoding="utf-8").splitlines()
    quote = None
    statement_lines = original["book-statements.jsonl"].splitlines(keepends=True)
    statement_output: list[bytes] = []
    found_statement = 0
    for raw in statement_lines:
        line = raw.rstrip(b"\r\n")
        row = json.loads(line.decode("utf-8"))
        if row.get("statement_id") == STATEMENT_ID:
            found_statement += 1
            qualifiers = row["qualifiers"]
            if (qualifiers.get("source_line_start"), qualifiers.get("source_line_end")) != (212, 212):
                raise SystemExit("p.117 statement source-line state changed")
            quote = row["original_quote"]
            if norm(quote) not in norm(source_lines[210]):
                raise SystemExit("the statement quote is not present on source line L211")
            qualifiers["source_line_start"] = 211
            qualifiers["source_line_end"] = 211
            updated = json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            if updated == line:
                raise SystemExit("statement repair produced no change")
            ending = raw[len(line):]
            statement_output.append(updated + ending)
        else:
            statement_output.append(raw)
    if found_statement != 1:
        raise SystemExit(f"expected one target statement, found {found_statement}")

    with COVERAGE.open(encoding="utf-8-sig", newline="") as f:
        coverage = {r["segment_id"]: r for r in csv.DictReader(f)}
    row = coverage.get(SEGMENT_ID)
    if not row or row.get("disposition") != "reviewed":
        raise SystemExit("p.117 segment is not marked reviewed")
    ranges = [
        (int(start), int(end))
        for start, end in __import__("re").findall(r"L(\d+)-(\d+)", row.get("source_line_ranges", ""))
    ]
    if not all(any(a <= int(ref.rsplit("#L", 1)[1]) <= b for a, b in ranges) for ref in NEW_REFS.values()):
        raise SystemExit("one or more repaired candidate references are outside reviewed coverage")

    candidate_bytes = original["entity-candidates.csv"]
    eol = b"\r\n" if b"\r\n" in candidate_bytes else b"\n"
    records = candidate_bytes.splitlines(keepends=True)
    replacements = {
        candidate_id.encode("ascii") + b",": (
            old_ref.encode("utf-8"),
            new_ref.encode("utf-8"),
        )
        for candidate_id, old_ref, new_ref in (
            (candidate_id, OLD_REFS[candidate_id], NEW_REFS[candidate_id])
            for candidate_id in OLD_REFS
        )
    }
    found_candidates: set[str] = set()
    candidate_output: list[bytes] = []
    for raw in records:
        changed = raw
        for prefix, (old_ref, new_ref) in replacements.items():
            if raw.startswith(prefix):
                candidate_id = prefix[:-1].decode("ascii")
                if candidate_id in found_candidates or old_ref not in raw:
                    raise SystemExit(f"unexpected CSV row for {candidate_id}")
                changed = raw.replace(old_ref, new_ref, 1)
                found_candidates.add(candidate_id)
        candidate_output.append(changed)
    if found_candidates != set(OLD_REFS):
        raise SystemExit(f"candidate rows missing: {sorted(set(OLD_REFS) - found_candidates)}")

    outputs = {
        "book-statements.jsonl": b"".join(statement_output),
        "entity-candidates.csv": b"".join(candidate_output),
    }
    parsed = {
        name: digest(data)
        for name, data in outputs.items()
    }
    for name, path in paths.items():
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            raise SystemExit(f"recovery backup already exists: {backup.name}")
    return paths, original, outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the validated audit repairs")
    args = parser.parse_args()
    paths, original, outputs = prepare()
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "prewrite_sha256": {name: digest(data) for name, data in original.items()},
        "repairs": {
            "statement_source_lines": {"statement_id": STATEMENT_ID, "from": [212, 212], "to": [211, 211]},
            "candidate_source_refs": {candidate_id: {"from": OLD_REFS[candidate_id], "to": NEW_REFS[candidate_id]} for candidate_id in OLD_REFS},
        },
        "postwrite_sha256": {name: digest(data) for name, data in outputs.items()},
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    backups = {name: path.with_name(path.name + BACKUP_SUFFIX) for name, path in paths.items()}
    for name, backup in backups.items():
        shutil.copy2(paths[name], backup)
    written: list[str] = []
    try:
        for name, path in paths.items():
            temporary = path.with_name(path.name + ".tmp-p117-auditfix")
            temporary.write_bytes(outputs[name])
        for name, path in paths.items():
            path.with_name(path.name + ".tmp-p117-auditfix").replace(path)
            written.append(name)
    except Exception:
        for name in written:
            shutil.copy2(backups[name], paths[name])
        raise
    print("applied; recovery backups: " + ", ".join(path.name for path in backups.values()))


if __name__ == "__main__":
    main()
