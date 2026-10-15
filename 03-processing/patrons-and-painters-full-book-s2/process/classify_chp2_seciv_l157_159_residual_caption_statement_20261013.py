from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l157-159"
STATEMENTS_SHA = "fefe0d1da324f005d519ceeac8d0c7da3f980da438db333d6b8730ad463045be"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
STATEMENT_ID = "st-chp2-seciv-l157-159-10a-title-content"
QUOTE = "a. Pietro da Cortona: Rape of the Sabines"
NOTE = "This records the printed caption's title content for the identified work. The mythological subject remains part of the caption description here; no separate event endpoint is asserted, and the caption does not establish historicity."
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp2-seciv-l157-159-caption-20261013")


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
    targets = [row for row in rows if row.get("statement_id") == STATEMENT_ID]
    if len(targets) != 1 or targets[0].get("segment_id") != SEGMENT_ID:
        raise SystemExit("expected one p.59 caption-title statement")
    row = targets[0]
    q = row.get("qualifiers") or {}
    if q.get("relation_candidate") is not None or row.get("original_quote") != QUOTE:
        raise SystemExit("caption-title statement changed or is no longer unset")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    cited = " ".join(source_lines[int(q["source_line_start"]) - 1:int(q["source_line_end"])])
    if " ".join(QUOTE.split()) not in " ".join(cited.split()):
        raise SystemExit("caption quote does not match its cited source line")
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
    tmp = TABLE.with_name(TABLE.name + ".tmp-s2-l157-159")
    tmp.write_bytes(rendered)
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
