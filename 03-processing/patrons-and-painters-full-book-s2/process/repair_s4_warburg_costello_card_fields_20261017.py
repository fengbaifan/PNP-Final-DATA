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
SOURCES_PATH = TABLES / "sources.csv"
PROCESS_PATH = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
ANCHOR = "s4-costello-card-table-provenance-20261017"
KU_IDS = {
    "units/persons/jane-costello",
    "units/archives/journal-warburg-courtauld-institutes",
    "units/archives/costello-twelve-pictures-ordered-velasquez-1950",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register structured rows and citations for the three S4 Costello cluster cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    target_manifest = [row for row in manifest if row.get("ku_id") in KU_IDS]
    assert {row["ku_id"] for row in target_manifest} == KU_IDS

    additions, source_registry, warnings, cards_with_tables = extract_records(target_manifest)
    assert cards_with_tables == 3
    assert len(additions) == 15
    assert not warnings, warnings
    assert all(row.get("source_ref") and row.get("source_ids") for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)

    source_fields, source_rows = sync.read_csv(SOURCES_PATH)
    source_by_id = {row["source_id"]: row for row in source_rows}
    new_sources = []
    for source_id, row in sorted(source_registry.items()):
        if row.get("kind") != "external":
            continue
        if source_id in source_by_id:
            assert source_by_id[source_id].get("citation") == row.get("citation")
            continue
        new_sources.append(row)
    assert len(new_sources) == 3
    assert {row["url"] for row in new_sources} == {
        "https://www.journals.uchicago.edu/journals/jwci/history",
        "https://www.journals.uchicago.edu/toc/jwci/1950/13/3-4",
        "https://www.jstor.org/stable/i230411",
    }

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
    assert len(existing_rows) == 10577
    assert len(existing_rows) + len(additions) == 10592

    added_ids = {row["source_id"] for row in new_sources}
    assert not (added_ids & set(source_by_id))
    planned_sources = [*source_rows, *new_sources]
    assert len(planned_sources) == len(source_rows) + 3

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 结构化字段与来源登记（{sync.DATE if hasattr(sync, 'DATE') else '2026-10-17'}）\n\n"
        "Costello 三张 S4 卡的字段表已映射为 enrichment.jsonl 行，按卡片来源序号关联 Haskell、University of Chicago Press 与 JSTOR 记录；"
        "三条外部来源登记至 sources.csv。此修复只补齐既有卡片结构化字段及来源映射，不改变身份组、KU 数量或关系决定。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: cards={cards_with_tables}; enrichment_rows={len(additions)}; "
            f"sources={len(new_sources)}; enrichment={len(existing_rows)}->{len(existing_rows) + len(additions)}; "
            f"source_registry={len(source_rows)}->{len(planned_sources)}"
        )
        return 0

    with ENRICHMENT_PATH.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(existing_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    sync.write_csv(SOURCES_PATH, source_fields, planned_sources)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: enrichment_rows={len(additions)}; sources={len(new_sources)}; "
        f"enrichment={len(existing_rows)}->{len(existing_rows) + len(additions)}; "
        f"source_registry={len(source_rows)}->{len(planned_sources)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
