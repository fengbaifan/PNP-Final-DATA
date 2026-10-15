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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l118-125"
SEGMENT_SHA256 = "b45e5832e49f40c221c95f72d8e4be732de3b687fd4ac95821a1cfafe469b27f"
STATEMENTS_SHA256 = "8b1c5ac89fb3a71fdeb897b6bc467cde4b1eff7d9e71cafb599a8d997f82375c"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-ii-l118-125-20261010")

DECISIONS = {
    "st-chp2-secii-l118-125-angelo-giori-background": (
        "Haskell reports Angelo Giori's Camerino schoolmaster background and his walk to Rome after hearing of "
        "preferment opportunities. Preserve these as source-reported biographical and place relations; identity details remain for S3."
    ),
    "st-chp2-secii-l118-125-carlo-caesar-comparison": (
        "Haskell says Carlo Barberini had scarcely been a Julius Caesar. This is a rhetorical historical comparison, "
        "not a personal or political relation between the two men."
    ),
    "st-chp2-secii-l118-125-carlo-character-and-honours": (
        "Haskell characterizes Carlo as overwhelmed by honours after his younger brother's accession. Preserve the "
        "family context and the author's judgment that the honours went to Carlo's head; do not treat that judgment as independently verified psychology."
    ),
    "st-chp2-secii-l118-125-carlo-monument-memorial-assessment": (
        "Haskell judges the Capitol monument to memorialize Barberini aspirations more than prowess. Keep this as an "
        "authorial assessment of the monument and family image; execution and identity details remain unresolved."
    ),
    "st-chp2-secii-l118-125-urban-julius-ii-comparison": (
        "Haskell compares Urban VIII's efforts to perpetuate himself with Julius II's. Preserve the comparison as an "
        "authorial historical interpretation, not a personal relation."
    ),
    "st-chp2-secii-l118-125-urban-portrait-appearance-continuation": (
        "This continues the earlier description of Urban VIII's portrait busts. Preserve the existing cross-segment "
        "continuation and attribute the grooming and temperament assessment to Haskell."
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
