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
ANCHOR = "s4-person-name-fields-sagredo-family-20261018"
KU_IDS = {
    "units/persons/gherardo-sagredo",
    "units/persons/niccolo-sagredo",
    "units/persons/stefano-sagredo",
}
EXPECTED_NAMES = {
    "units/persons/gherardo-sagredo": {"Sagredo, Gherardo", "Girardo P.O Sagredio"},
    "units/persons/niccolo-sagredo": {"Sagredo, Niccolò", "Niccolò Sagredo"},
    "units/persons/stefano-sagredo": {"Sagredo, Stefano", "Stessano Sagredo", "Steffano Sagredo"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Register structured names for three Sagredo person cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with (TABLES / "ku-manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    target_manifest = [row for row in manifest if row.get("ku_id") in KU_IDS]
    assert {row["ku_id"] for row in target_manifest} == KU_IDS
    additions, source_registry, warnings, cards_with_tables = extract_records(target_manifest)
    assert cards_with_tables == len(KU_IDS)
    assert len(additions) == sum(len(values) for values in EXPECTED_NAMES.values()) == 7
    assert not warnings, warnings
    assert {row.get("ku_id") for row in additions} == KU_IDS
    assert all(row.get("source_ref") and row.get("source_ids") == ["haskell-1980-rev-ed"] for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    for ku_id, expected in EXPECTED_NAMES.items():
        actual = {row.get("value") for row in additions if row.get("ku_id") == ku_id}
        assert actual == expected, (ku_id, actual, expected)
        assert len([row for row in additions if row.get("ku_id") == ku_id]) == len(expected)

    with SOURCES_PATH.open(encoding="utf-8-sig", newline="") as handle:
        registered_sources = {row["source_id"] for row in csv.DictReader(handle)}
    assert "haskell-1980-rev-ed" in registered_sources
    assert set(source_registry) == {"haskell-1980-rev-ed"}

    existing_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") in KU_IDS for row in existing)
    ids = {row.get("enrichment_id", "") for row in existing}
    occurrences = {row.get("occurrence_id", "") for row in existing}
    natural_keys = {
        (row.get("ku_id"), row.get("field"), row.get("value"), row.get("source_id"))
        for row in existing
    }
    max_id = max(
        (int(match.group(1)) for value in ids if (match := re.fullmatch(r"enr-(\d+)", value))),
        default=0,
    )
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + offset:05d}"
        assert row["enrichment_id"] not in ids
        assert row.get("occurrence_id") not in occurrences
        key = (row["ku_id"], row["field"], row["value"], row.get("source_id", ""))
        assert key not in natural_keys

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    id_list = "、".join(f"`{row['enrichment_id']}`" for row in additions)
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4结构化姓名字段登记：Sagredo三张人物卡（{DATE}）\n\n"
        f"三张人物卡登记{len(additions)}条source_backed姓名enrichment行（{id_list}），均引用既有Haskell书目来源ID。"
        "Gherardo卡保留遗嘱拼写“Girardo P.O Sagredio”；Niccolò卡保留索引名与第6章正文全名；Stefano卡分列索引“Stefano”、脚注OCR“Stessano”及页图校读“Steffano”。"
        "Princeton馆藏沿革的外部身份比对仍为undecided，未写成姓名事实。本批未新增sources.csv记录、生平字段或formal relation。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: cards={cards_with_tables}; name_rows={len(additions)}; "
            f"enrichment={len(existing)}->{len(existing)+len(additions)}; new_sources=0; "
            "source/variant/natural-key checks passed; warnings=0; no files changed"
        )
        return 0

    with ENRICHMENT_PATH.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(existing_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: name_rows={len(additions)}; enrichment={len(existing)}->{len(existing)+len(additions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
