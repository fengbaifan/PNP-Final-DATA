from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLE = ROOT / "04-knowledge" / "tables" / "book-statements.jsonl"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
SEGMENT_ID = "chp-2:02_CHP-2_sec_iv:l190-245"
STATEMENTS_SHA = "27359840d20a73b63e4ef36505d05394ea4c07682256a44f77fbaebfd9b1c178"
SOURCE_SHA = "9f50e1396234faff664211d70a1231ef145bccdc24e91c088f1237d55ca34dbf"
SEGMENT_SHA = "5dd2839d3e713ca4795b2bfd4de98120305a38026d0d41ffcc7c84e19fbcfd2a"
NOTE = (
    "This statement preserves a bibliographic citation and locator. The citation is not itself a historical or domain relationship, "
    "and the cited material is not independently consulted by this source entry."
)
BACKUP = TABLE.with_name("book-statements.jsonl.bak-s2-chp2-seciv-l190-245-citations-20261013")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify the remaining bibliographic pointers in CHP-2 p.44–58 notes.")
    parser.add_argument("--apply", action="store_true", help="write after protected preview; default is preview")
    args = parser.parse_args()
    raw = TABLE.read_bytes()
    before = hashlib.sha256(raw).hexdigest()
    if before != STATEMENTS_SHA:
        raise SystemExit(f"protected statements changed: expected {STATEMENTS_SHA}, found {before}")
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise SystemExit("protected S0 source changed")
    segments = [json.loads(line) for line in (ROOT / "04-knowledge/tables/segments.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    segment = next((row for row in segments if row.get("segment_id") == SEGMENT_ID), None)
    if not segment or segment.get("sha256") != SEGMENT_SHA or segment.get("asset_sha256") != SOURCE_SHA:
        raise SystemExit("protected footnote segment record changed")
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[segment["line_start"] - 1:segment["line_end"]])
    if hashlib.sha256(segment_text.encode("utf-8")).hexdigest() != SEGMENT_SHA:
        raise SystemExit("footnote segment does not match its protected source hash")

    rows = [json.loads(line) for line in raw.decode("utf-8-sig").splitlines() if line.strip()]
    targets = [row for row in rows if row.get("segment_id") == SEGMENT_ID and (row.get("qualifiers") or {}).get("relation_candidate") is None]
    expected_ids = {f"st-chp2-seciv-l190-245-citation-{i:02d}" for i in range(1, 85)}
    actual_ids = {row.get("statement_id") for row in targets}
    if actual_ids != expected_ids or len(targets) != 84:
        raise SystemExit(f"unexpected residual citation set: count={len(targets)}, missing={sorted(expected_ids-actual_ids)}, extra={sorted(actual_ids-expected_ids)}")

    for row in targets:
        qualifiers = row.get("qualifiers") or {}
        if row.get("predicate") != "footnote_citation" or row.get("subject_candidate_id") not in (None, ""):
            raise SystemExit(f"residual is not a source-only citation pointer: {row['statement_id']}")
        if not row.get("object_candidate_id"):
            raise SystemExit(f"citation has no cited-source endpoint: {row['statement_id']}")
        start, end = int(qualifiers["source_line_start"]), int(qualifiers["source_line_end"])
        cited = " ".join(source_lines[start - 1:end])
        if " ".join(row["original_quote"].split()) not in " ".join(cited.split()):
            raise SystemExit(f"citation quote does not match source lines: {row['statement_id']}")
        qualifiers["relation_candidate"] = False
        qualifiers["relation_candidate_note"] = NOTE

    rendered = ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")
    if raw.startswith(b"\xef\xbb\xbf"):
        rendered = b"\xef\xbb\xbf" + rendered
    print(f"segment={SEGMENT_ID}; citations classified false={len(targets)}; no claims, candidates, mentions, or S0 lines changed")
    print(f"book-statements.jsonl: {before} -> {hashlib.sha256(rendered).hexdigest()}")
    if not args.apply:
        print("mode=preview; no files changed")
        return
    if BACKUP.exists():
        raise SystemExit(f"backup already exists: {BACKUP}")
    shutil.copy2(TABLE, BACKUP)
    tmp = TABLE.with_name(TABLE.name + ".tmp-s2-note-citations")
    tmp.write_bytes(rendered)
    tmp.replace(TABLE)
    print(f"mode=apply; backup={BACKUP.name}")


if __name__ == "__main__":
    main()
