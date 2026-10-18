from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.build_field_facts import assign_ids, extract_records  # noqa: E402

TASK_DIR = ROOT / "03-processing" / "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
SOURCES_PATH = TABLES / "sources.csv"
PROCESS_PATH = TASK_DIR / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
DATE = "2026-10-18"
ANCHOR = "s4-person-name-fields-schmidt-schonborn-20261018"
KU_IDS = {
    "units/persons/georg-friedrich-schmidt",
    "units/persons/friedrich-karl-schonborn",
    "units/persons/johann-philip-franz-schonborn",
    "units/persons/lothar-franz-von-schonborn",
}


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Register structured names for four new S4 person cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with MANIFEST_PATH.open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    target_manifest = [row for row in manifest if row.get("ku_id") in KU_IDS]
    assert {row["ku_id"] for row in target_manifest} == KU_IDS
    additions, source_registry, warnings, cards_with_tables = extract_records(target_manifest)
    assert cards_with_tables == 4
    assert len(additions) == 9
    assert not warnings, warnings
    assert {row.get("ku_id") for row in additions} == KU_IDS
    assert all(row.get("source_ref") and row.get("source_ids") == ["haskell-1980-rev-ed"] for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert all(
        len([row for row in additions if row.get("ku_id") == ku_id]) == expected
        for ku_id, expected in {
            "units/persons/georg-friedrich-schmidt": 2,
            "units/persons/friedrich-karl-schonborn": 3,
            "units/persons/johann-philip-franz-schonborn": 2,
            "units/persons/lothar-franz-von-schonborn": 2,
        }.items()
    )

    with SOURCES_PATH.open(encoding="utf-8-sig", newline="") as handle:
        registered_sources = {row["source_id"] for row in csv.DictReader(handle)}
    assert set(source_registry) == {"haskell-1980-rev-ed"}
    assert set(source_registry) <= registered_sources

    existing_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") in KU_IDS for row in existing)
    assign_ids(additions, ENRICHMENT_PATH)
    existing_ids = {row.get("enrichment_id") for row in existing}
    existing_occurrences = {row.get("occurrence_id") for row in existing}
    for row in additions:
        assert row.get("enrichment_id") not in existing_ids
        assert row.get("occurrence_id") not in existing_occurrences
        existing_ids.add(row.get("enrichment_id"))
        existing_occurrences.add(row.get("occurrence_id"))
    planned = existing + additions

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    enrichment_ids = "、".join(row["enrichment_id"] for row in additions)
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4结构化姓名字段登记：四张人物卡（{DATE}）\n\n"
        f"四张卡姓名表共登记{len(additions)}条source_backed enrichment行（{enrichment_ids}），"
        "全部关联既有Haskell书目来源ID；未新增sources.csv记录、S5生平字段或formal relation。"
    )

    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    unverified = sum(row.get("evidence_status") == "unverified" for row in planned)
    result_text, count = re.subn(
        r"^\| \[既有字段表\].*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {len(planned):,}条，其中{unverified:,}条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert count == 1

    if args.dry_run:
        print(
            f"dry-run passed: cards={cards_with_tables}; name_rows={len(additions)}; "
            f"enrichment={len(existing)}->{len(planned)}; new_sources=0; warnings=0; no files changed"
        )
        return 0

    ENRICHMENT_PATH.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in planned) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: name_rows={len(additions)}; enrichment={len(existing)}->{len(planned)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
