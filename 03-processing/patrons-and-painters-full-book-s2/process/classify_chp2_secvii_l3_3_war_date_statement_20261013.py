from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_vii.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_vii:l3-3"
STATEMENT_ID = "st-chp2-secvii-l3-3-war-castro-outbreak"
STATEMENTS_SHA = "6cb4407d1f30cf3e15b0aed376e1e137d16b93286b5ebc8f68669027f8305b08"
SOURCE_SHA = "5f2ec3c85927ed4aded258d7a6b1801ccb3b8e0416f0f3f9e57ad7b2fae8dd4c"
SEGMENT_SHA = "992305b74428b480ca4d08bc1f0240b8c0fccca008086a11f3600d120bae896b"
NOTE = "This is a date-bearing narrative assertion about the outbreak of an event, not a relation between distinct entities."
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp2-secvii-l3-3-date-20261013")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    before = hashlib.sha256(raw).hexdigest()
    if before != STATEMENTS_SHA:
        raise SystemExit(f"protected statements changed: expected {STATEMENTS_SHA}, found {before}")
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise SystemExit("protected S0 source changed")
    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    target = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
    if len(target) != 1 or target[0].get("segment_id") != SEGMENT_ID:
        raise SystemExit("expected exactly one target War of Castro statement")
    segment = next(json.loads(line) for line in (ROOT / "04-knowledge/tables/segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
                   if json.loads(line).get("segment_id") == SEGMENT_ID)
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if segment.get("sha256") != SEGMENT_SHA or hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
        raise SystemExit("protected War of Castro segment hash mismatch")
    row = target[0]
    q = row["qualifiers"]
    if q.get("relation_candidate") is not None or row.get("original_quote") != (
        "In 1641 the War of Castro broke out. The final consequences of this absurd dispute with the Duke of Parma were insignificant, but its effects on the Barberini were of great"
    ):
        raise SystemExit("target classification or quote changed")
    cited = " ".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])])
    if " ".join(row["original_quote"].split()) not in " ".join(cited.split()):
        raise SystemExit("quote does not match cited source line")
    q["relation_candidate"] = False
    q["relation_candidate_note"] = NOTE
    rendered = ("\n".join(json.dumps(item, ensure_ascii=False) for item in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    print(f"{STATEMENT_ID}: false — {NOTE}")
    print(f"book-statements.jsonl: {before} -> {hashlib.sha256(rendered).hexdigest()}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    tmp = TABLE.with_name(TABLE.name + ".tmp-s2-secvii-l3-3")
    tmp.write_bytes(rendered)
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
