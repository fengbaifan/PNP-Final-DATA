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
SEGMENTS = ROOT / "04-knowledge/tables/segments.jsonl"
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l71-78"
SEGMENT_SHA256 = "4553743974bb21f3bdf2c258c0c6d80807998e704df129b44061ac34ad97749f"
STATEMENTS_SHA256 = "51f16697345d2bf07d8369953ad8023470e3a8123d5db598d6cda7a11b2d9884"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-ii-l71-78-20261010")

DECISIONS = {
    "st-chp2-secii-l71-78-marino-return-from-paris": (
        "The source reports Marino's return to Italy from an eight-year visit to Paris in 1623. "
        "Keep the duration and date source-bound; this is a travel statement, not evidence of residence."
    ),
    "st-chp2-secii-l71-78-marino-rome-naples-and-patronage-disappointment": (
        "The source says Marino left Rome for Naples and died there soon afterwards. His disappointment "
        "in hoped-for papal patronage and Haskell's inferred explanation about Urban VIII's taste remain "
        "authorial interpretation, not proof of an actual patronage refusal."
    ),
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed S2 classifications")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    require(digest(raw) == STATEMENTS_SHA256, "statement table SHA-256 changed; re-review before writing")
    bom = raw.startswith(b"\xef\xbb\xbf")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"

    segment_rows = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segment_rows if row.get("segment_id") == SEGMENT_ID), None)
    require(segment is not None and segment.get("sha256") == SEGMENT_SHA256, "segment metadata mismatch")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    require(digest(source_text.encode("utf-8")) == SEGMENT_SHA256, "source segment content changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    require(len(by_id) == len(rows), "duplicate statement IDs in table")
    for statement_id, note in DECISIONS.items():
        row = by_id.get(statement_id)
        require(row is not None, f"missing statement: {statement_id}")
        require(row.get("segment_id") == SEGMENT_ID, f"unexpected segment: {statement_id}")
        q = row.get("qualifiers") or {}
        require("relation_candidate" not in q, f"already classified: {statement_id}")
        require(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")), f"not bilateral: {statement_id}")
        require(row["original_quote"] in source_text, f"source quote mismatch: {statement_id}")
        q["relation_candidate"] = True
        q["relation_candidate_note"] = note

    output = (b"\xef\xbb\xbf" if bom else b"") + newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") for row in rows
    ) + newline
    classified_true = sum(bool((row.get("qualifiers") or {}).get("relation_candidate")) for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id"))
    classified_false = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id"))
    unclassified = sum("relation_candidate" not in (row.get("qualifiers") or {}) for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id"))
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "classified_true": list(DECISIONS),
        "classified_false": [],
        "after_bilateral": {"relation_true": classified_true, "relation_false": classified_false, "unclassified": unclassified},
        "sha256_before": digest(raw),
        "sha256_after": digest(output),
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Dry-run only. Pass --apply to write.")
        return

    if BACKUP.exists():
        require(digest(BACKUP.read_bytes()) == STATEMENTS_SHA256, f"backup exists with unexpected contents: {BACKUP.name}")
    else:
        shutil.copy2(TABLE, BACKUP)
    handle = tempfile.NamedTemporaryFile(prefix=TABLE.name + ".", suffix=".tmp", dir=TABLE.parent, delete=False)
    temp_path = Path(handle.name)
    try:
        with handle:
            handle.write(output)
        os.replace(temp_path, TABLE)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    require(digest(TABLE.read_bytes()) == digest(output), "post-write SHA-256 mismatch")
    print(json.dumps({"result": "applied", "backup": BACKUP.name, "sha256_after": digest(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
