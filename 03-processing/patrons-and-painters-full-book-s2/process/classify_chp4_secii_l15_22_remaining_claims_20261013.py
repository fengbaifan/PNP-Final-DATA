from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp4-secii-l15-22-20261013")
EXPECTED_TABLE_SHA = "a0e5f8c2817d375a05d3d6218f58a38ded957930d9805a458d1f53ff5a73929e"
EXPECTED_SOURCE_SHA = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l15-22"
REASONS = {
    "st-chp4-sec-ii-l15-22-admiration-affection": (
        "Haskell's comparative assessment of Cassiano's character; it gives no discrete second entity or event."
    ),
    "st-chp4-sec-ii-l15-22-bachelor-reserved": (
        "A single-person biographical and character description, including Haskell's interpretation of his reserve."
    ),
    "st-chp4-sec-ii-l15-22-collection-contents": (
        "The passage reports broad categories of collection contents but identifies no individual works or bounded item group; preserve it as an inventory summary without unsupported collection-item edges."
    ),
    "st-chp4-sec-ii-l15-22-family-credit": (
        "Haskell's explanation of how recognition was assigned within the family; the statement identifies no separate credit-bearing object or relation endpoint."
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source_bytes = SOURCE.read_bytes()
    raw = TABLE.read_bytes()
    if sha(source_bytes) != EXPECTED_SOURCE_SHA:
        raise SystemExit("source hash changed; re-read the current segment")
    if sha(raw) != EXPECTED_TABLE_SHA:
        raise SystemExit("statement table hash changed; re-read the current table")
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    targets = {r["statement_id"]: r for r in rows if r.get("segment_id") == SEGMENT_ID and r["statement_id"] in REASONS}
    if set(targets) != set(REASONS):
        raise SystemExit("target statement set changed")
    for sid, row in targets.items():
        q = row.get("qualifiers") or {}
        if "relation_candidate" in q:
            raise SystemExit(f"{sid} is no longer unset")
        if row.get("origin") != "book" or row.get("source_file") != "02-sources/02-Markdown/04_CHP-4_sec_ii.md":
            raise SystemExit(f"{sid} source identity changed")

    for sid, row in targets.items():
        q = row.setdefault("qualifiers", {})
        q["relation_candidate"] = False
        q["relation_candidate_note"] = REASONS[sid]

    output = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    print("Chapter 4 section II L15-22 preview:")
    for sid, reason in REASONS.items():
        print(f"relation_candidate=false: {sid} — {reason}")
    print(f"{TABLE.relative_to(ROOT)}: {sha(raw)} -> {sha(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    shutil.copy2(TABLE, BACKUP)
    temporary = TABLE.with_name(TABLE.name + ".tmp-s2-chp4-secii-l15-22")
    temporary.write_bytes(output)
    temporary.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
