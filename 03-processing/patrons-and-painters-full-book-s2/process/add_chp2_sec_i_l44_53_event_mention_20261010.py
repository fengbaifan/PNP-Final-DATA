from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS = TABLES / "mentions.csv"
BACKUP = TABLES / "mentions.csv.bak-s2-chp2-sec-i-l44-53-event-20261010"
SEGMENT_ID = "chp-2:02_CHP-2_sec_i:l44-53"
SOURCE_FILE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_i.md"
EXPECTED_HASHES = {
    "04-knowledge/tables/mentions.csv": "7981656efea75e28f877a5dfd0ccd6f68785d1a0368998bcf62cd5ac5fdd31fd",
    "04-knowledge/tables/entity-candidates.csv": "b214ec44c825690db146c4efdcb96e1de4acbbc5d682104ec0c35535d53b2dae",
    "02-sources/02-Markdown/02_CHP-2_sec_i.md": "5eca92acb03fe9934be85c82a6ec6806d3c564002955e99bd317916f3c7c8dc6",
}
MENTION = {
    "mention_id": "m-s2-chp2-seci-l44-53-event-cand-4254",
    "segment_id": SEGMENT_ID,
    "candidate_id": "cand-4254",
    "surface_form": "visit to Ferrara to take over the city",
    "start_char": "986",
    "end_char": "1024",
    "note": "Haskell's event statement for Clement VIII's 1598 visit to Ferrara and the takeover; the phrase explicitly names the visit and its purpose.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PRECONDITION FAILED: {message}")


def preflight() -> tuple[list[str], list[dict[str, str]]]:
    for relative, expected_hash in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.is_file(), f"missing input: {relative}")
        require(sha256(path) == expected_hash, f"input hash changed: {relative}")

    with MENTIONS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    require(fieldnames == ["mention_id", "segment_id", "candidate_id", "surface_form", "start_char", "end_char", "note"],
            "mentions.csv columns changed")
    require(not any(row.get("mention_id") == MENTION["mention_id"] for row in rows), "mention ID already exists")
    require(not any(row.get("segment_id") == SEGMENT_ID and row.get("candidate_id") == "cand-4254" for row in rows),
            "candidate already has a mention in this segment")

    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    candidate = [row for row in candidates if row.get("candidate_id") == "cand-4254"]
    require(len(candidate) == 1 and candidate[0].get("suggested_type") == "event", "event candidate changed")
    require(candidate[0].get("candidate_source_ref") == SEGMENT_ID + "#L48", "candidate source reference changed")

    lines = SOURCE_FILE.read_text(encoding="utf-8").splitlines()
    segment_text = "\n".join(lines[43:53])
    start, end = int(MENTION["start_char"]), int(MENTION["end_char"])
    require(segment_text[start:end] == MENTION["surface_form"], "mention offsets do not match exact source text")
    require("his visit to Ferrara to take over the city" in lines[47], "event wording is absent from source line 48")
    return fieldnames, rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the existing Ferrara event candidate in its cited S2 segment.")
    parser.add_argument("--apply", action="store_true", help="write the preflighted mention")
    args = parser.parse_args()
    fieldnames, rows = preflight()
    updated = rows + [MENTION]
    print(f"PREVIEW: add one source-grounded mention for cand-4254 in {SEGMENT_ID}")
    print(f"  surface={MENTION['surface_form']!r}; offsets={MENTION['start_char']}:{MENTION['end_char']}")
    print(f"  mentions: {len(rows)} -> {len(updated)}")
    if not args.apply:
        print("DRY RUN ONLY; no files written. Use --apply to add the mention.")
        return

    require(not BACKUP.exists(), f"backup already exists: {BACKUP.relative_to(ROOT)}")
    shutil.copy2(MENTIONS, BACKUP)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=MENTIONS.parent, delete=False) as handle:
        temporary = Path(handle.name)
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(updated)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, MENTIONS)
    print(f"APPLIED; backup: {BACKUP.relative_to(ROOT)}")
    print(f"new SHA-256: {sha256(MENTIONS)}")


if __name__ == "__main__":
    main()
