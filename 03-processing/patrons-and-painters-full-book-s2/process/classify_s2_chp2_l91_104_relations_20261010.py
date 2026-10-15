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
SEGMENT_ID = "chp-2:02_CHP-2_sec_ii:l91-104"
SEGMENT_SHA256 = "716087759fa887391584b7f7ba1c97d9b5abd70acc8bb895e07045a70d5c04d7"
STATEMENTS_SHA256 = "e4149c2da0c79951f89b371f31f49aed089ae9bd5886d832791225a458c02801"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-ii-l91-104-20261010")

DECISIONS = {
    "st-chp2-secii-l91-104-baroque-flattery-interpretation": (
        "Haskell identifies flattery as an element of the Baroque and says Urban VIII gave it broad scope. "
        "Preserve this as the author's cultural interpretation, not a claim that Urban alone caused Baroque flattery."
    ),
    "st-chp2-secii-l91-104-urban-busts-as-self-image": (
        "Haskell interprets Bernini's portrait busts as giving an impression of how Urban VIII saw himself. "
        "This is an authorial reading of the portraits, not a documented statement by Urban."
    ),
    "st-chp2-secii-l91-104-urban-busts-contrast-with-royal-portraits": (
        "Haskell contrasts the restraint of Urban VIII's portraits with Bernini's treatment of royal patrons. "
        "Keep the comparison and the Vicar-of-Christ rationale as authorial characterization."
    ),
    "st-chp2-secii-l91-104-urban-lifelong-love-of-poetry": (
        "The source attributes a lifelong love of poetry to Urban VIII. The poem group is not expanded into named titles."
    ),
    "st-chp2-secii-l91-104-urban-poems-nature-and-country-life": (
        "The source says Urban VIII wrote many poems about nature and country life, especially at Castel Gandolfo. "
        "Keep the villa as the stated subject context, not as proof that every poem was written there."
    ),
    "st-chp2-secii-l91-104-urban-poetry-editions-after-accession": (
        "Haskell reports Roman editions of Urban VIII's poems beginning within months of his accession and a "
        "1631 volume produced by the Jesuits and illustrated by Bernini. Preserve the publication roles and source attribution."
    ),
    "st-chp2-secii-l91-104-urban-portrait-appearance-continues-at-l119": (
        "This fragment begins a description of Urban VIII's appearance in the portrait group and continues later in the source. "
        "Keep its existing continuation linkage and do not treat the fragment as a separate portrait version."
    ),
    "st-chp2-secii-l91-104-urban-portrait-hieratic-dignity": (
        "Haskell interprets the portraits as hieratic images of a ruler who need not assert his right to rule. "
        "Preserve this as an interpretation of the image, not as a claim about Urban's actual political authority."
    ),
    "st-chp2-secii-l91-104-urban-portrait-image-changes-over-rule": (
        "Haskell describes a change in the image of Urban VIII after several years of rule. Keep the chronology and "
        "the grave, authoritarian, withdrawn characterization attributed to the author."
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
