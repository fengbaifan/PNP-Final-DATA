from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge/tables/book-statements.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp4-secii-l69-71-20261013")
EXPECTED_TABLE_SHA = "7407a87bbcb1fdd2607b673bf4e70c9b4372374cf07fee176ac4aa30620a0956"
EXPECTED_SOURCE_SHA = "fd05a5c61deb6ba897878f510450d589d1ec0ef1276ff585ae601943bfd59575"
STATEMENT_ID = "st-chp4-sec-ii-l69-71-p18b-title"
SEGMENT_ID = "chp-4:04_CHP-4_sec_ii:l69-71"
NOTE = "This records a printed caption's title wording and its same-plate mapping; it is work metadata, not an event-level or entity-to-entity relation."


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    if sha(raw) != EXPECTED_TABLE_SHA or sha(SOURCE.read_bytes()) != EXPECTED_SOURCE_SHA:
        raise SystemExit("source or statement table changed; re-read before applying")
    if BACKUP.exists():
        raise SystemExit(f"protected backup already exists: {BACKUP.name}")

    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    targets = [r for r in rows if r.get("statement_id") == STATEMENT_ID and r.get("segment_id") == SEGMENT_ID]
    if len(targets) != 1:
        raise SystemExit("target statement missing or duplicated")
    row = targets[0]
    q = row.get("qualifiers") or {}
    if "relation_candidate" in q or row.get("subject_candidate_id") != "cand-4086" or row.get("object_candidate_id") is not None:
        raise SystemExit("target classification or endpoints changed")
    if row.get("original_quote") != "b. Poussin: The Sacrament of Marriage":
        raise SystemExit("target quote changed")
    q["relation_candidate"] = False
    q["relation_candidate_note"] = NOTE
    row["qualifiers"] = q
    output = ("\n".join(json.dumps(item, ensure_ascii=False) for item in rows) + "\n").encode("utf-8")
    print(f"{STATEMENT_ID}: relation_candidate=false")
    print(f"reason: {NOTE}")
    print(f"{TABLE.relative_to(ROOT)}: {sha(raw)} -> {sha(output)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    shutil.copy2(TABLE, BACKUP)
    temporary = TABLE.with_name(TABLE.name + ".tmp-s2-chp4-secii-l69-71")
    temporary.write_bytes(output)
    temporary.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
