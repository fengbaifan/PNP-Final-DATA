#!/usr/bin/env python3
"""Build stable source segments using physical line offsets; preview by default."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SOURCE_DIR = BASE / "02-sources" / "02-Markdown"
TABLES = BASE / "04-knowledge" / "tables"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def chapter_for(name: str) -> str:
    match = re.search(r"CHP-(\d+)", name, re.I)
    return f"chp-{int(match.group(1))}" if match else "front-matter"


def build_segments() -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    issues: list[str] = []
    files = [p for p in sorted(SOURCE_DIR.glob("*.md")) if not re.match(r"^\d+_CHP-\d+\.md$", p.name)]
    if not files:
        return [], [f"no section Markdown files found in {SOURCE_DIR}"]
    for path in files:
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            issues.append(f"{path.name}: invalid UTF-8 at byte {exc.start}")
            continue
        lines = text.splitlines()
        asset_hash = sha256(raw)
        start = None
        for index in range(len(lines) + 1):
            nonblank = index < len(lines) and bool(lines[index].strip())
            if nonblank and start is None:
                start = index + 1
            if not nonblank and start is not None:
                end = index
                exact_text = "\n".join(lines[start - 1:end])
                digest = sha256(exact_text.encode("utf-8"))
                chapter = chapter_for(path.name)
                rows.append({
                    "segment_id": f"{chapter}:{path.stem}:l{start}-{end}",
                    "source_id": "haskell-1980-rev-ed",
                    "chapter": chapter,
                    "section": path.stem,
                    "source_file": path.relative_to(BASE).as_posix(),
                    "line_start": start,
                    "line_end": end,
                    "sha256": digest,
                    "asset_sha256": asset_hash,
                    "release_excluded": True,
                })
                start = None
    ids = [row["segment_id"] for row in rows]
    if len(ids) != len(set(ids)):
        issues.append("segment_id collision detected")
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["source_file"], []).append(row)
    for source_file, items in grouped.items():
        previous_end = 0
        for row in items:
            if row["line_start"] <= previous_end or row["line_end"] < row["line_start"]:
                issues.append(f"overlap or invalid interval: {source_file} {row['segment_id']}")
            previous_end = row["line_end"]
        path = BASE / source_file
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        expected = sum(bool(line.strip()) for line in lines)
        covered = sum(row["line_end"] - row["line_start"] + 1 for row in items)
        if covered != expected:
            issues.append(f"nonblank line coverage mismatch: {source_file} covered={covered} expected={expected}")
        for row in items:
            exact_text = "\n".join(lines[row["line_start"] - 1:row["line_end"]])
            if sha256(exact_text.encode("utf-8")) != row["sha256"]:
                issues.append(f"line-slice hash mismatch: {source_file} {row['segment_id']}")
    return rows, issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write segments.jsonl")
    args = parser.parse_args()
    rows, issues = build_segments()
    print(f"section_files={len({row['source_file'] for row in rows})} segments={len(rows)} issues={len(issues)}")
    for issue in issues[:30]:
        print(f"ERROR: {issue}")
    if issues:
        return 2
    if args.apply:
        path = TABLES / "segments.jsonl"
        temp = path.with_suffix(path.suffix + ".tmp")
        with temp.open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        temp.replace(path)
        print(f"applied={path.relative_to(BASE)}")
    else:
        print("preview only; pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
