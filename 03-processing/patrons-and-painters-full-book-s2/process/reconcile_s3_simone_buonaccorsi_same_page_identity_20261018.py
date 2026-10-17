from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
ANCHOR = "s3-simone-buonaccorsi-same-page-identity-20261018"
EXPECTED = {
    "st-chp8-p223-francesca-eighteen-children": "The source names only Simone in this passage; S3 maps that mention to index candidate cand-0469 (B.csv#317) from the same page, matching given name, and cardinal status. The count and future-tense status are retained as written; no external identity verification is claimed.",
    "st-chp8-p223-francesca-mother-of-simone": "The passage gives only Simone; S3 maps the mention to index candidate cand-0469 (B.csv#317) from the same page, matching given name, and cardinal status. This resolves the book-internal identity link only; the mother-child predicate remains an S2 relation candidate for S6, with no external identity verification claimed.",
    "st-chp8-p223-simone-cardinal": "The future status is retained as written. S3 maps Simone to index candidate cand-0469 (B.csv#317) from the same page, matching given name, and cardinal status; this is a book-internal identity link, not external identity verification.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the same-page identity link for the Simone named on p.223.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with ALIGNMENT_PATH.open(encoding="utf-8-sig", newline="") as handle:
        alignments = list(csv.DictReader(handle))
    target = [row for row in alignments if row.get("candidate_id") == "cand-0469" and not row.get("external_source")]
    assert len(target) == 1
    alignment = target[0]
    assert alignment.get("decision") == "new"
    assert alignment.get("ku_id") == "units/persons/simone-buonaccorsi"
    assert "S3补充复核" in alignment.get("resolution_note", "")

    index_path = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "B.csv"
    raw_index = index_path.read_bytes()
    try:
        index_text = raw_index.decode("utf-8-sig")
    except UnicodeDecodeError:
        index_text = raw_index.decode("cp1252")
    index_rows = list(csv.DictReader(io.StringIO(index_text)))
    assert index_rows[317].get("Main Entry") == "Buonaccorsi, Cardinal Simone"
    assert index_rows[317].get("Page Numbers") == "223"
    source_text = (ROOT / "02-sources/02-Markdown/08_CHP-8_sec_ii.md").read_text(encoding="utf-8-sig")
    assert "one of whom, Simone, was to become a Cardinal" in source_text

    original_lines = STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
    output_lines = []
    found = set()
    for raw in original_lines:
        if not raw.strip():
            continue
        statement = json.loads(raw)
        sid = statement.get("statement_id")
        if sid in EXPECTED:
            q = statement.setdefault("qualifiers", {})
            assert "identity" in q.get("qualification", "").lower() or sid == "st-chp8-p223-francesca-eighteen-children"
            q["qualification"] = EXPECTED[sid]
            found.add(sid)
            output_lines.append(json.dumps(statement, ensure_ascii=False))
        else:
            output_lines.append(raw)
    assert found == set(EXPECTED), found

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3补充：Simone Buonaccorsi同页身份映射落入陈述限定（2026-10-18）\n\n"
        "对 `st-chp8-p223-francesca-eighteen-children`、`st-chp8-p223-francesca-mother-of-simone` 与 "
        "`st-chp8-p223-simone-cardinal` 的 `qualification` 更新，保留正文只写Simone、人数及将成为枢机的时态，"
        "并记录S3依据同一印刷页上的索引B.csv#317映射至cand-0469。mother_of仍为S2候选，留待S6；"
        "该对齐仅属书内证据，不表示外部身份核验或正式关系成立。"
    )

    if args.dry_run:
        print(f"dry-run passed: same-page index/source anchors matched; statements_updated={len(found)}; no files changed")
        return 0

    STATEMENTS_PATH.write_text("\n".join(output_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: statements_updated={len(found)}; identity=st-chp8-p223-simone -> cand-0469; formal_relations_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
