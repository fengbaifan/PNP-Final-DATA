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
DATE = "2026-10-18"
ANCHOR = "s4-person-name-fields-luigi-scaramuccia-gonzaga-crespi-spezzaferro-20261018"
KU_IDS = {
    "units/persons/aloysius-gonzaga",
    "units/persons/luigi-crespi-author",
    "units/persons/luigi-scaramuccia",
    "units/persons/luigi-spezzaferro",
}
VATICAN_URL = (
    "https://www.vatican.va/news_services/liturgy/libretti/2025/"
    "20250423-libretto-traslazione-bara.pdf"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register structured name fields for four new S4 person cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    target_manifest = [row for row in manifest if row.get("ku_id") in KU_IDS]
    assert {row["ku_id"] for row in target_manifest} == KU_IDS
    additions, source_registry, warnings, cards_with_tables = extract_records(target_manifest)
    assert cards_with_tables == len(KU_IDS)
    assert len(additions) == 6
    assert not warnings, warnings
    assert {row["ku_id"] for row in additions} == KU_IDS
    assert all(row.get("source_ref") and row.get("source_ids") for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert {row["field"] for row in additions} == {
        "英文惯用名", "意大利文名", "书中称号", "书目全名", "原文全名"
    }
    assert len([row for row in additions if row["ku_id"] == "units/persons/aloysius-gonzaga"]) == 3

    source_fields, source_rows = sync.read_csv(SOURCES_PATH)
    source_by_id = {row["source_id"]: row for row in source_rows}
    assert len(source_by_id) == len(source_rows)
    assert "haskell-1980-rev-ed" in source_by_id
    vatican_sources = [row for row in source_registry.values() if row.get("url") == VATICAN_URL]
    assert len(vatican_sources) == 1
    new_sources = []
    for row in source_registry.values():
        source_id = row["source_id"]
        if source_id in source_by_id:
            existing = source_by_id[source_id]
            if row.get("kind") == "external":
                assert existing.get("citation") == row.get("citation")
                if row.get("url"):
                    assert existing.get("url") == row.get("url")
            else:
                assert row.get("kind") == "book"
            continue
        if row.get("url"):
            assert row["url"] == VATICAN_URL
            assert not any(existing.get("url") == VATICAN_URL for existing in source_rows)
            new_sources.append(row)
    assert len(new_sources) == 1
    assert new_sources[0]["url"] == VATICAN_URL

    existing_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") in KU_IDS for row in existing)
    existing_ids = {row.get("enrichment_id", "") for row in existing}
    existing_occurrences = {row.get("occurrence_id", "") for row in existing}
    natural_keys = {
        (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id"))
        for row in existing
    }
    max_id = max(
        (int(match.group(1)) for value in existing_ids if (match := re.fullmatch(r"enr-(\d+)", value))),
        default=0,
    )
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + offset:05d}"
        assert row["enrichment_id"] not in existing_ids
        assert row.get("occurrence_id") not in existing_occurrences
        natural_key = (row["ku_id"], row["field"], row["value"], row.get("source_id", ""))
        assert natural_key not in natural_keys
    registered_sources = set(source_by_id) | {row["source_id"] for row in new_sources}
    referenced_sources = {
        source_id for row in additions for source_id in row.get("source_ids", []) if source_id
    }
    assert referenced_sources <= registered_sources

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    ids = ", ".join(f"`{row['enrichment_id']}`" for row in additions)
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4结构化字段与来源登记：四张人物卡姓名（{DATE}）\n\n"
        f"四张新人物卡的姓名表行登记为{len(additions)}条enrichment.jsonl记录（{ids}），来源序号与卡片sources对应。"
        f"Luigi/Aloysius Gonzaga的英文惯用名字段引用Holy See礼仪文本来源`{new_sources[0]['source_id']}`；"
        "该外部来源已列入sources.csv，URL与PDF页码定位见人物卡。其余姓名字段引用Haskell书内页段或索引。"
        "本批只登记名称字段，不新增生平事实、formal relation或S6裁决。"
    )
    planned_sources = [*source_rows, *new_sources]

    if args.dry_run:
        print(
            f"dry-run passed: cards={cards_with_tables}; enrichment_rows={len(additions)}; "
            f"external_sources={len(new_sources)}; enrichment={len(existing)}->{len(existing)+len(additions)}; "
            f"sources={len(source_rows)}->{len(planned_sources)}; warnings=0; no files changed"
        )
        return 0

    with ENRICHMENT_PATH.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(existing_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    sync.write_csv(SOURCES_PATH, source_fields, planned_sources)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: enrichment_rows={len(additions)}; external_sources={len(new_sources)}; "
        f"enrichment={len(existing)}->{len(existing)+len(additions)}; "
        f"sources={len(source_rows)}->{len(planned_sources)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
