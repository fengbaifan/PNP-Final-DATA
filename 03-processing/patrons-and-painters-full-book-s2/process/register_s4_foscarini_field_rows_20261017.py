from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
from scripts.build_field_facts import extract_records  # noqa: E402

TABLES = ROOT / "04-knowledge" / "tables"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
PROCESS_PATH = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
ANCHOR = "s4-foscarini-card-table-fields-20261017"
KU_IDS = {
    "units/institutions/austrian-government",
    "units/institutions/hofbibliothek-vienna",
    "units/archives/marco-foscarini-library",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register structured rows for the Foscarini S4 cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    target_manifest = [row for row in manifest if row.get("ku_id") in KU_IDS]
    assert {row["ku_id"] for row in target_manifest} == KU_IDS
    additions, source_registry, warnings, cards_with_tables = extract_records(target_manifest)
    assert cards_with_tables == 3
    assert len(additions) == 10
    assert not warnings, warnings
    assert all(row.get("source_ref") and row.get("source_ids") for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert set(source_registry) == {"haskell-1980-rev-ed"}

    existing_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing_rows = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
    existing_ids = {row.get("enrichment_id", "") for row in existing_rows}
    max_id = max(
        (int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))),
        default=0,
    )
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + offset:05d}"
        assert row["enrichment_id"] not in existing_ids

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 结构化字段登记（2026-10-17）\n\n"
        "Foscarini 书籍与手稿收藏、Austrian government 和 Hofbibliothek 三张卡的表格字段已映射为10条 enrichment.jsonl 记录，"
        "统一关联本书来源 haskell-1980-rev-ed；本批无外部来源登记。此修复只补齐字段级来源结构，不改变 S3 身份裁决、KU 映射或 S6 关系状态。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: cards={cards_with_tables}; enrichment_rows={len(additions)}; "
            f"enrichment={len(existing_rows)}->{len(existing_rows) + len(additions)}; "
            f"sources={','.join(sorted(source_registry))}"
        )
        return 0

    with ENRICHMENT_PATH.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(existing_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: enrichment_rows={len(additions)}; enrichment={len(existing_rows)}->{len(existing_rows) + len(additions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
