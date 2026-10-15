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
STATEMENTS_SHA256 = "740737831af3a8648b49b4b62fbcd0023ec9ae84dc69c43fb7af5542bec5b3e5"
BACKUP = TABLE.with_name(TABLE.name + ".bak-s2-chp2-sec-ii-l127-193-20261010")

SEGMENT_HASHES = {
    "chp-2:02_CHP-2_sec_ii:l127-139": "4d2e65b99c5e5c8e49ecdc544ab6b88763a2ffa3ce1e5ca424eac5ca6d36da36",
    "chp-2:02_CHP-2_sec_ii:l141-145": "6ee183c4a1a0fb2eacd040ac7a9d12a50fc521cd13caabbc49aeaa15ebf3645b",
    "chp-2:02_CHP-2_sec_ii:l147-193": "eecca3166cf5e2c76b830b696b314e5c2b6f3cec09b463643578f0b0d44d1c4a",
}

DECISIONS = {
    "st-chp2-secii-l127-139-barberini-exile-and-resource-exploitation": (
        "chp-2:02_CHP-2_sec_ii:l127-139",
        "Haskell ironically links the Barberini family's expulsion from Rome to its exploitation of the city's resources. "
        "Preserve this as the author's retrospective assessment, not a neutral legal finding.",
    ),
    "st-chp2-secii-l127-139-urban-patronage-confusion-s-maria": (
        "chp-2:02_CHP-2_sec_ii:l127-139",
        "Haskell presents Urban VIII's dealings with S. Maria della Concezione as an example of contradictions in his "
        "religious patronage. Keep the evaluation attributed to the author.",
    ),
    "st-chp2-secii-l141-145-urban-dynastic-motive-continuation": (
        "chp-2:02_CHP-2_sec_ii:l141-145",
        "This fragment completes the reported dynastic motive: Urban VIII objected to other princes' arms appearing "
        "alongside the Barberini arms. Preserve its continuation link and the source's framing as reported thought.",
    ),
    "st-chp2-secii-l147-193-gregory-quotation-chain": (
        "chp-2:02_CHP-2_sec_ii:l147-193",
        "The footnote records a quotation attributed to Gregory XIII through Baglione and cited via Orbaan. This is a "
        "source chain reported by Haskell; the cited texts were not independently consulted.",
    ),
    "st-chp2-secii-l147-193-planned-rome-allegory": (
        "chp-2:02_CHP-2_sec_ii:l147-193",
        "Haskell says an allegory of Urban VIII's defence of Rome was intended for a Barberini palace wall. Preserve "
        "the planned status and cited Pastor reference; do not treat the decoration as executed or independently verified.",
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
    segment_map = {row["segment_id"]: row for row in segment_rows}
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    source_texts = {}
    for segment_id, expected_hash in SEGMENT_HASHES.items():
        segment = segment_map.get(segment_id)
        require(segment is not None and segment.get("sha256") == expected_hash, f"segment metadata mismatch: {segment_id}")
        text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
        require(digest(text.encode("utf-8")) == expected_hash, f"source segment content changed: {segment_id}")
        source_texts[segment_id] = text

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    require(len(by_id) == len(rows), "duplicate statement IDs in table")
    for statement_id, (segment_id, note) in DECISIONS.items():
        row = by_id.get(statement_id)
        require(row is not None, f"missing statement: {statement_id}")
        require(row.get("segment_id") == segment_id, f"unexpected segment: {statement_id}")
        q = row.get("qualifiers") or {}
        require("relation_candidate" not in q, f"already classified: {statement_id}")
        require(bool(row.get("subject_candidate_id") and row.get("object_candidate_id")), f"not bilateral: {statement_id}")
        require(row["original_quote"] in source_texts[segment_id], f"source quote mismatch: {statement_id}")
        q["relation_candidate"] = True
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
        "segments": list(SEGMENT_HASHES),
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
