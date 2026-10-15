from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l127-137"
STATEMENTS_SHA = "7974c493854b6e771966039332582d241b9824e4ba63e6eeaf195c075ca9e15c"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
TARGETS = {
    "st-chp2-seciv-l127-137-joust-pastiche-approval-fragment": (
        True,
        "This is the opening fragment of the joust-reception statement completed at L140. The continuation reports delighted approval but does not identify the approving audience; retain the relation candidate with that endpoint unresolved.",
    ),
    "st-chp2-seciv-l127-137-sacchi-slow-worker": (
        False,
        "This is Haskell's evaluative description of Sacchi's pace of work, not a relation between distinct entities.",
    ),
}
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp2-seciv-l127-137-residuals-20261013")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    before = hashlib.sha256(raw).hexdigest()
    if before != STATEMENTS_SHA:
        raise SystemExit(f"protected statement table changed: expected {STATEMENTS_SHA}, found {before}")
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise SystemExit("protected S0 source changed")
    segment = next(json.loads(line) for line in (ROOT / "04-knowledge/tables/segments.jsonl").read_text(encoding="utf-8-sig").splitlines()
                   if json.loads(line).get("segment_id") == SEGMENT_ID)
    lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(lines[segment["line_start"] - 1:segment["line_end"]])
    if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != segment["sha256"]:
        raise SystemExit("p.55 segment source fingerprint mismatch")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    by_id = {row["statement_id"]: row for row in rows}
    unset = {
        row["statement_id"] for row in rows
        if row.get("segment_id") == SEGMENT_ID and (row.get("qualifiers") or {}).get("relation_candidate") is None
    }
    if unset != set(TARGETS):
        raise SystemExit(f"unexpected p.55 unset set: {sorted(unset)}")
    expected_quotes = {
        "st-chp2-seciv-l127-137-joust-pastiche-approval-fragment": "None the less this elaborate pastiche of feudal practices met",
        "st-chp2-seciv-l127-137-sacchi-slow-worker": "Sacelli was also an excessively slow worker,",
    }
    for statement_id, (classification, note) in TARGETS.items():
        row = by_id[statement_id]
        q = row["qualifiers"]
        if row["original_quote"] != expected_quotes[statement_id]:
            raise SystemExit(f"unexpected quote for {statement_id}")
        if q.get("relation_candidate") is not None:
            raise SystemExit(f"statement is no longer unset: {statement_id}")
        line_start, line_end = int(q["source_line_start"]), int(q["source_line_end"])
        cited_text = " ".join(lines[line_start - 1:line_end])
        if " ".join(row["original_quote"].split()) not in " ".join(cited_text.split()):
            raise SystemExit(f"quote does not match source lines: {statement_id}")
        q["relation_candidate"] = classification
        q["relation_candidate_note"] = note
        if classification:
            q["open_endpoint_reason"] = "The sentence reports delighted approval in passive voice and does not identify the approving audience."
        print(f"{statement_id}: {classification} — {note}")

    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    print(f"book-statements.jsonl: {before} -> {hashlib.sha256(rendered).hexdigest()}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    tmp = TABLE.with_name(TABLE.name + ".tmp-s2-l127-137")
    tmp.write_bytes(rendered)
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
