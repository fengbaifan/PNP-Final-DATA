from __future__ import annotations

import argparse
import json
from pathlib import Path

import register_s4_archive_memmo_query_sheet_20261017 as sync_module

sync = sync_module.sync
ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
CANDIDATE = "cand-7285"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_v.md"
STAGES = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "stages.md"
OLD_MARKER = "Footnote 1 is in a later composite source segment and remains to be migrated"
NEW_DETAIL = (
    "Haskell's p.200 body names Admiral ‘Pekemburgh’, who entered Genoa with an English squadron before 1703 "
    "and commissioned a bust from Domenico Parodi. Footnote 1, now migrated as st-chp7-p200-n1-possible-peterborough "
    "and related statements, tentatively proposes that he may be the 3rd Earl of Peterborough. The identity remains "
    "undecided; do not merge with cand-1891."
)
LOG_MARKER = "### S2 cand-7285 metadata refresh after p.200 note 1 migration (2026-10-17)"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, alignments = sync.read_csv(TABLES / "alignment.csv")
    by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    row = by_id[CANDIDATE]
    assert alignment_by_id[CANDIDATE].get("decision") == "undecided"
    assert alignment_by_id["cand-1891"].get("decision") == "new"
    source_text = SOURCE.read_text(encoding="utf-8-sig")
    assert "This may possibly be tbe famous 3rd Earl ofPeterborough" in source_text
    statement_lines = (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    statements = [json.loads(line) for line in statement_lines if line.strip()]
    statement = next(s for s in statements if s.get("statement_id") == "st-chp7-p200-n1-possible-peterborough")
    assert statement.get("subject_candidate_id") == CANDIDATE
    assert statement.get("object_candidate_id") == "cand-1891"
    assert (statement.get("qualifiers") or {}).get("relation_candidate") is True
    assert OLD_MARKER in row.get("detail", "") or row.get("detail") == NEW_DETAIL
    planned_candidates = [dict(item) for item in candidates]
    planned_by_id = {item["candidate_id"]: item for item in planned_candidates}
    planned_by_id[CANDIDATE]["detail"] = NEW_DETAIL
    stages_text = STAGES.read_text(encoding="utf-8-sig")
    if LOG_MARKER not in stages_text:
        stages_text = stages_text.rstrip() + (
            f"\n\n{LOG_MARKER}\n\n"
            "- cand-7285 的 detail 原称 p.200 注1尚未迁移；当前 statement 表已完整包含该注，旧状态过时。"
            "现更新为明确记录正文与注1的来源锚点，并保留注释中的 tentative identification：cand-7285 与 cand-1891 不合并，"
            "cand-7285 的 S3 决定继续为 undecided。未修改候选、提及或 statement 数量。"
        ) + "\n"

    if args.dry_run:
        print("dry-run passed: cand-7285 detail will reflect migrated p.200 note 1; identity remains undecided")
        print("S2 counts and S3 decision unchanged; no files changed")
        return 0

    sync.write_csv(TABLES / "entity-candidates.csv", candidate_fields, planned_candidates)
    STAGES.write_text(stages_text, encoding="utf-8-sig", newline="\n")
    print("applied: cand-7285 detail refreshed; decision remains undecided; no S2 coverage counts changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
