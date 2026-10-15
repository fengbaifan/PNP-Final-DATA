from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_vii.md"
SEGMENTS = ROOT / "04-knowledge" / "tables" / "segments.jsonl"
SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l32-36"
STATEMENTS_SHA256 = "100cee927a40b0fab6a605d18442a0be67bfc42ccdfce6aae9787aaa6451463c"
SOURCE_SHA256 = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
SEGMENT_SHA256 = "b10e9ecda86062c0c1dad7a7c4fb34561c726f8ed3d3d9f9d3a4acb3adef5d34"
TARGETS = {
    "st-chp2-secvii-l32-36-francesco-limited-role-in-current-culture": (
        "Haskell's comparison that Francesco played little part in the more vital culture of the day is an authorial assessment; the passage does not define that culture as a separate relation endpoint.",
    ),
    "st-chp2-secvii-l32-36-francesco-love-art-learning-remained": (
        "Haskell's statement that Francesco's love of art and learning remained deep is a scalar authorial characterization, not a relation between distinct entities.",
    ),
}
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp2-secvii-l32-36-residual-scalars-20261013")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    raw = TABLE.read_bytes()
    if sha256(raw) != STATEMENTS_SHA256:
        raise SystemExit("protected statements table changed")
    if sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise SystemExit("protected S0 source changed")
    segments = [json.loads(line) for line in SEGMENTS.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA256:
        raise SystemExit("protected segment metadata changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if sha256(segment_text.encode("utf-8")) != SEGMENT_SHA256:
        raise SystemExit("protected segment source lines changed")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    row_map = {row.get("statement_id"): row for row in rows}
    if len(row_map) != len(rows) or not set(TARGETS).issubset(row_map):
        raise SystemExit("target statement set changed")
    for statement_id, note in TARGETS.items():
        row = row_map[statement_id]
        if row.get("segment_id") != SEGMENT_ID or row.get("qualifiers", {}).get("relation_candidate") is not None:
            raise SystemExit(f"target is no longer an unset statement in {SEGMENT_ID}: {statement_id}")
        q = row["qualifiers"]
        cited = " ".join(" ".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])]).split())
        quote = " ".join(row.get("original_quote", "").split())
        if quote not in cited:
            raise SystemExit(f"quote does not match cited source lines: {statement_id}")
        q["relation_candidate"] = False
        q["relation_candidate_note"] = note

    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    for statement_id, note in TARGETS.items():
        print(f"{statement_id}: false — {note}")
    print(f"book-statements.jsonl: {sha256(raw)} -> {sha256(rendered)}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP.name}")
    shutil.copy2(TABLE, BACKUP)
    tmp = TABLE.with_name(TABLE.name + ".tmp-s2-secvii-l32-36")
    tmp.write_bytes(rendered)
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
