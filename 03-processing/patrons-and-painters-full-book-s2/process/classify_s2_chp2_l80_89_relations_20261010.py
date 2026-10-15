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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l80-89"
SEGMENT_SHA256 = "e1d901252d516f1c9a17a7024d6fb2ecefd1346c48f25c13aa87e1c48e8a8bf3"
STATEMENTS_SHA256 = "26022bb4b84bf08d278c801d29115266070a7eb04570027558fd8e892c2024da"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-ii-l80-89-20261010")

DECISIONS = {
    "st-chp2-secii-l80-89-annibale-comparison": (
        "Haskell directly compares Pietro's ability to evoke antiquity with Annibale Carracci's. "
        "Keep this as an authorial aesthetic comparison; it does not assert influence or artistic descent."
    ),
    "st-chp2-secii-l80-89-copying-as-baroque-foundation": (
        "Haskell links Marcello's encouragement of Pietro to copy Raphael and Titian with a focal point "
        "in seventeenth-century art and the establishment of Baroque painting. Preserve this as Haskell's "
        "art-historical interpretation, not a claim that Marcello alone created the movement."
    ),
    "st-chp2-secii-l80-89-pietro-aesthetic-capacity-and-domenichino-contrast": (
        "Haskell contrasts Pietro's vivid recreation of antiquity with the coldness he attributes to a "
        "classical artist such as Domenichino. This is a source-bound aesthetic comparison, not a social or training relation."
    ),
    "st-chp2-secii-l80-89-pietro-grand-manner-in-bibiana-frescoes": (
        "Haskell characterizes Pietro's S. Bibiana frescoes as bringing the warmth and breadth of his "
        "grand manner. Keep the claim as an authorial assessment of this work."
    ),
    "st-chp2-secii-l80-89-processional-style-development": (
        "Haskell describes a stylistic development in Pietro's canvases toward rich, warm, processional "
        "figures, which he says were soon adopted by other artists in the Sacchetti orbit. Preserve both "
        "the author's interpretation and the limited scope of the adoption claim."
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
