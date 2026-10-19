from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
from scripts.build_field_facts import extract_records  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
KU = "units/works/scuola-del-carmine-second-ceiling-scheme"
CARD_REL = "04-knowledge/units/works/scuola-del-carmine-second-ceiling-scheme.md"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
AGENTS_PATH = ROOT / "AGENTS.md"
ANCHOR = "s4-scuola-second-scheme-structured-fields-20261020"


def update_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.M)
    assert count == 1, f"expected one {label}; found {count}"
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Scuola scheme card's book-derived structured fields.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with (TABLES / "ku-manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    targets = [row for row in manifest if row.get("ku_id") == KU]
    assert len(targets) == 1 and targets[0].get("card_path") == CARD_REL

    additions, source_registry, warnings, cards_with_tables = extract_records(targets)
    assert cards_with_tables == 1
    assert len(additions) == 6, f"expected one title field and five basic fields, got {len(additions)}"
    assert not warnings, warnings
    assert set(source_registry) == {"haskell-1980-rev-ed"}
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert all(row.get("origin") == "book" and row.get("source_ids") for row in additions)

    old_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in old_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") == KU for row in existing), "field rows already exist for this card"
    existing_ids = {row.get("enrichment_id", "") for row in existing}
    existing_occurrences = {row.get("occurrence_id", "") for row in existing}
    numeric_ids = [
        int(match.group(1))
        for value in existing_ids
        if (match := re.fullmatch(r"enr-(\d+)", value))
    ]
    next_id = max(numeric_ids, default=0) + 1
    for offset, row in enumerate(additions):
        row["enrichment_id"] = f"enr-{next_id + offset:05d}"
        assert row["enrichment_id"] not in existing_ids
        assert row.get("occurrence_id") not in existing_occurrences
        existing_ids.add(row["enrichment_id"])
        existing_occurrences.add(row.get("occurrence_id", ""))
    natural_keys = {
        (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id"))
        for row in existing
    }
    assert not any(
        (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id")) in natural_keys
        for row in additions
    )

    planned_count = len(existing) + len(additions)
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    result_text = update_once(
        result_text,
        r"^\| \[字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        f"| [字段表](../tables/enrichment.jsonl) | {planned_count:,}条，其中1,625条 unverified |",
        "current enrichment artifact row",
    )

    agents_text = AGENTS_PATH.read_text(encoding="utf-8-sig")
    agents_text = update_once(
        agents_text,
        r"S5字段表\s*11,725\s*条、其中\s*1,625\s*条unverified",
        f"S5字段表 {planned_count:,} 条、其中 1,625 条unverified",
        "current S5 count in AGENTS.md",
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S4 work：Scuola del Carmine 第二方案卡片字段结构化（2026-10-20）\n\n"
        f"从[第二套天顶装饰方案卡](../../../{CARD_REL})提取1条名称字段和5条书内基本信息字段，"
        "逐条保留 Haskell 第9章 p.273 的 source ID、位置和原始 Markdown 表格单元格；6条均标为 `source_backed`。"
        "这是把 S4 卡片的原书属性纳入既有字段索引，不是外部身份核验或外部补足；5条关系候选仍待 S6。"
    )
    result_text += (
        "\n\n### S4 work：Scuola del Carmine 第二方案结构化字段（2026-10-20）\n\n"
        "卡片中的1条名称字段与5条基本信息字段已登记至 `enrichment.jsonl`，均由第9章 p.273 原书支持并保留表格单元格和来源定位；"
        "未作外部身份核验或外部补足。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: card tables={cards_with_tables}; fields={len(additions)}; "
            f"source={','.join(sorted(source_registry))}; enrichment={len(existing):,}->{planned_count:,}"
        )
        print("all fields source_backed; raw cells, table metadata, and occurrence IDs preserved")
        return 0

    had_bom = ENRICHMENT_PATH.read_bytes().startswith(b"\xef\xbb\xbf")
    with ENRICHMENT_PATH.open("a", encoding="utf-8-sig", newline="\n") as handle:
        if old_text and not old_text.endswith(("\n", "\r")):
            handle.write("\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    if not had_bom and ENRICHMENT_PATH.read_bytes().startswith(b"\xef\xbb\xbf"):
        ENRICHMENT_PATH.write_bytes(ENRICHMENT_PATH.read_bytes()[3:])
    PROCESS_PATH.write_text(process_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(f"applied: fields={len(additions)}; enrichment={len(existing):,}->{planned_count:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
