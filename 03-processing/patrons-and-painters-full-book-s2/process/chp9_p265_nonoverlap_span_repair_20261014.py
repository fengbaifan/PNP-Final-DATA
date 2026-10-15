"""Repair the p.265 work mention span that crossed the Corradini sculpture span."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process"
MENTIONS = TABLES / "mentions.csv"
COVERAGE = TABLES / "s2-coverage.csv"
SEGMENTS = TABLES / "segments.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md"
SEGMENT_ID = "chp-9:09_CHP-9_intro:l291-301"
MENTION_ID = "m-chp9-p265-drawing-work"
SURFACE = "Tiepolo drew for the engraver Andrea Zucchi"
EXPECTED_HASHES = {
    MENTIONS: "afbf0dff77392120387cb65c48a2fc86e9683cf422237112a099d49b4910fa9d",
    COVERAGE: "d5dafbf3bc5bb77ec94f5f0ddf1c34958fd97f97b18c9dbb46eb61c2e150d9f8",
}
BACKUP_SUFFIX = ".bak-s2-chp9-p265-nonoverlap-span-repair-20261014"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, fields, rows):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(f.name)
    temp_path.replace(path)


for path, expected in EXPECTED_HASHES.items():
    if sha256(path) != expected:
        raise SystemExit(f"fingerprint changed; inspect before continuing: {path.relative_to(ROOT)}")

mentions_fields, mentions = read_csv(MENTIONS)
rows = [r for r in mentions if r["mention_id"] == MENTION_ID]
if len(rows) != 1:
    raise SystemExit(f"expected one {MENTION_ID}, found {len(rows)}")
row = rows[0]
if row["segment_id"] != SEGMENT_ID or row["surface_form"] != "Tiepolo drew for the engraver Andrea Zucchi the statue of":
    raise SystemExit("p.265 mention no longer matches the reviewed crossing span")
sculpture = next((r for r in mentions if r["mention_id"] == "m-chp9-p265-corradini-statue"), None)
if sculpture is None or sculpture["segment_id"] != SEGMENT_ID:
    raise SystemExit("Corradini sculpture mention is missing or moved")

segments = {r["segment_id"]: r for r in (json.loads(x) for x in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if x.strip())}
meta = segments[SEGMENT_ID]
source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
text = "\n".join(source_lines[meta["line_start"] - 1:meta["line_end"]])
start = text.index(SURFACE)
end = start + len(SURFACE)
if text[start:end] != SURFACE:
    raise SystemExit("new surface does not match the S0 source span")
if end > int(sculpture["start_char"]):
    raise SystemExit("repaired work mention would still overlap the sculpture mention")
row["surface_form"] = SURFACE
row["start_char"] = str(start)
row["end_char"] = str(end)
row["note"] = (
    "Anchor the drawing work to the act of Tiepolo drawing for engraver Andrea Zucchi; "
    "the following Corradini sculpture has its own non-overlapping mention. The individual drawing is unnamed."
)

coverage_fields, coverage_rows = read_csv(COVERAGE)
coverage = next((r for r in coverage_rows if r["segment_id"] == SEGMENT_ID), None)
if coverage is None:
    raise SystemExit(f"missing coverage row: {SEGMENT_ID}")
coverage["note"] += (
    " 2026-10-14 audit repair shortened the Tiepolo drawing-work mention to its non-overlapping "
    "source phrase; Corradini's sculpture retains a separate span."
)

print(json.dumps({
    "mode": "apply" if "--apply" in __import__("sys").argv else "dry-run",
    "mention_id": MENTION_ID,
    "new_surface_form": SURFACE,
    "new_span": [start, end],
    "sculpture_span": [int(sculpture["start_char"]), int(sculpture["end_char"])],
    "non_overlapping": end <= int(sculpture["start_char"]),
}, ensure_ascii=False, indent=2))

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="write the verified non-overlapping span and coverage note")
args = parser.parse_args()
if args.apply:
    paths = [MENTIONS, COVERAGE]
    backups = [path.with_name(path.name + BACKUP_SUFFIX) for path in paths]
    for path, backup in zip(paths, backups):
        if backup.exists():
            if sha256(backup) != EXPECTED_HASHES[path] or sha256(path) != EXPECTED_HASHES[path]:
                raise SystemExit(f"existing recovery backup does not match the unchanged baseline: {backup.name}")
        else:
            shutil.copy2(path, backup)
    try:
        write_csv(MENTIONS, mentions_fields, mentions)
        write_csv(COVERAGE, coverage_fields, coverage_rows)
    except Exception:
        for path, backup in zip(paths, backups):
            shutil.copy2(backup, path)
        raise
    print("applied; recovery backups: " + ", ".join(path.name for path in backups))
