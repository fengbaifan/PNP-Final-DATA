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
SOURCE = ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l3-4"
SEGMENT_SHA256 = "b6105d2699fd40909d7c847e55bd8b5e9c9b45d2c0919fe6373b1649305b9243"
STATEMENTS_SHA256 = "d6af34aa63bbda7d59f3f9b643cdc9ae5b84dfb1e549c09d86d6b7d254c2d7a5"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-iv-l3-4-20261010")

DECISIONS = {
    "st-chp2-seciv-l3-4-francesco-age-at-urban-election": (
        True,
        "Haskell reports Francesco's age when his uncle Urban VIII was elected. Preserve the kinship and event-time relation; no age/date inference beyond the text.",
    ),
    "st-chp2-seciv-l3-4-francesco-artistic-role-rome": (
        True,
        "The source says all three named nephews played an increasingly important role in Rome's artistic life. This scalar record concerns Francesco only and retains the collective source wording.",
    ),
    "st-chp2-seciv-l3-4-francesco-paris-legation": (
        True,
        "Haskell reports Francesco's dispatch as a special legate to Paris in early 1625 and calls it his first crucial political test. Preserve authorial characterization and date wording.",
    ),
    "st-chp2-seciv-l3-4-francesco-portrait-description": (
        False,
        "This is a physical-appearance description of Francesco, not a relation to the portrait work. The Plate 3a parenthetical points to an illustration; the plate caption already records the work-to-sitter relation. Preserve the appearance claim as a person attribute, not a duplicate graph edge.",
    ),
    "st-chp2-seciv-l3-4-richelieu-spain-war-fragment": (
        True,
        "The source names Richelieu's policies and a threatened war with Spain; the clause continues in the next segment. Preserve fragment and modality; do not imply that war occurred.",
    ),
    "st-chp2-seciv-l3-4-taddeo-artistic-role-rome": (
        True,
        "The source explicitly includes Taddeo among the three nephews whose role in Rome's artistic life increased. Preserve the source's collective statement without expanding it beyond the named person.",
    ),
    "st-chp2-seciv-l3-4-young-antonio-artistic-role-rome": (
        True,
        "The source explicitly includes the named Antonio among the three nephews whose role in Rome's artistic life increased. Retain the younger Antonio's identity boundary and the collective wording.",
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
    for statement_id, (decision, note) in DECISIONS.items():
        row = by_id.get(statement_id)
        require(row is not None, f"missing statement: {statement_id}")
        require(row.get("segment_id") == SEGMENT_ID, f"unexpected segment: {statement_id}")
        q = row.get("qualifiers") or {}
        require("relation_candidate" not in q, f"already classified: {statement_id}")
        require(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")), f"not bilateral: {statement_id}")
        require(row["original_quote"] in source_text, f"source quote mismatch: {statement_id}")
        q["relation_candidate"] = decision
        q["relation_candidate_note"] = note

    output = (b"\xef\xbb\xbf" if bom else b"") + newline.join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") for row in rows
    ) + newline
    bilateral = [row for row in rows if row.get("subject_candidate_id") and row.get("object_candidate_id")]
    classified_true = sum((row.get("qualifiers") or {}).get("relation_candidate") is True for row in bilateral)
    classified_false = sum((row.get("qualifiers") or {}).get("relation_candidate") is False for row in bilateral)
    unclassified = sum("relation_candidate" not in (row.get("qualifiers") or {}) for row in bilateral)
    print(json.dumps({
        "action": "apply" if args.apply else "dry-run",
        "segment_id": SEGMENT_ID,
        "classified_true": [key for key, (decision, _) in DECISIONS.items() if decision],
        "classified_false": [key for key, (decision, _) in DECISIONS.items() if not decision],
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
