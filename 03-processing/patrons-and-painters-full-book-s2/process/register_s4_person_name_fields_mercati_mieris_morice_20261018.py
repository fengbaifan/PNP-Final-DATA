from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.build_field_facts import extract_records  # noqa: E402

TASK_DIR = ROOT / "03-processing" / "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
SOURCES_PATH = TABLES / "sources.csv"
PROCESS_PATH = TASK_DIR / "process" / "knowledge.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-name-fields-mercati-mieris-morice-20261018"
KU_IDS = {
    "units/persons/giovanni-battista-mercati",
    "units/persons/frans-van-mieris",
    "units/persons/sir-william-morice",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register structured names for three new S4 person cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with (TABLES / "ku-manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    target_manifest = [row for row in manifest if row.get("ku_id") in KU_IDS]
    assert {row["ku_id"] for row in target_manifest} == KU_IDS
    additions, source_registry, warnings, cards_with_tables = extract_records(target_manifest)
    assert cards_with_tables == 3 and len(additions) == 3
    assert not warnings, warnings
    assert {row["ku_id"] for row in additions} == KU_IDS
    assert all(row.get("source_ref") and row.get("source_ids") == ["haskell-1980-rev-ed"] for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)

    with SOURCES_PATH.open(encoding="utf-8-sig", newline="") as handle:
        registered_sources = {row["source_id"] for row in csv.DictReader(handle)}
    assert "haskell-1980-rev-ed" in registered_sources and set(source_registry) == {"haskell-1980-rev-ed"}
    existing_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") in KU_IDS for row in existing)
    ids = {row.get("enrichment_id", "") for row in existing}
    occurrences = {row.get("occurrence_id", "") for row in existing}
    natural_keys = {(row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id")) for row in existing}
    max_id = max((int(match.group(1)) for value in ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + offset:05d}"
        assert row["enrichment_id"] not in ids and row.get("occurrence_id") not in occurrences
        assert (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id", "")) not in natural_keys

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    id_list = "、".join(f"`{row['enrichment_id']}`" for row in additions)
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4结构化姓名字段登记：三张人物卡（{DATE}）\n\n"
        f"三张卡姓名表登记{len(additions)}条source_backed enrichment行（{id_list}），全部引用既有Haskell书目来源ID。"
        "本批未新增sources.csv记录、生平字段或formal relation。"
    )

    if args.dry_run:
        print(f"dry-run passed: cards={cards_with_tables}; rows={len(additions)}; enrichment={len(existing)}->{len(existing)+len(additions)}; new_sources=0; warnings=0; no files changed")
        return 0
    with ENRICHMENT_PATH.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(existing_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: enrichment_rows={len(additions)}; enrichment={len(existing)}->{len(existing)+len(additions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
