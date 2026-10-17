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

TABLES = ROOT / "04-knowledge" / "tables"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
PROCESS_PATH = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
ANCHOR = "s4-person-endpoint-name-fields-bencovich-borzone-bossuet-breughel-brusasorci-buckingham-20261017"
TARGET_KUS = [
    "units/persons/federico-bencovich",
    "units/persons/francesco-borzone",
    "units/persons/jacques-benigne-bossuet",
    "units/persons/abram-breughel",
    "units/persons/felice-brusasorci",
    "units/persons/charles-villiers-duke-of-buckingham",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register source-backed index-name fields for six new S4 person cards.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with (TABLES / "ku-manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    selected = [row for row in manifest if row.get("ku_id") in TARGET_KUS]
    assert len(selected) == len(TARGET_KUS) and {row["ku_id"] for row in selected} == set(TARGET_KUS)
    additions, source_registry, warnings, cards_with_tables = extract_records(selected)
    assert cards_with_tables == len(TARGET_KUS) and len(additions) == len(TARGET_KUS)
    assert not warnings, warnings
    assert {row.get("field") for row in additions} == {"索引名"}
    assert all(row.get("source_ref") and row.get("source_ids") == ["haskell-1980-rev-ed"] for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert set(source_registry) == {"haskell-1980-rev-ed"}

    existing_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") in TARGET_KUS for row in existing)
    natural_keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id")) for r in existing}
    ids = {row.get("enrichment_id", "") for row in existing}
    max_id = max((int(match.group(1)) for value in ids if (match := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + offset:05d}"
        key = (row["ku_id"], row["field"], row["value"], row.get("source_id", ""))
        assert key not in natural_keys and row["enrichment_id"] not in ids

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4结构化字段：六个人物索引名（2026-10-17）\n\n"
        "Federico Bencovich、Francesco Borzone、Jacques-Bénigne Bossuet、Abram Breughel、Felice Brusasorci"
        "与Charles Villiers, Duke of Buckingham六张人物卡各登记一条索引名enrichment记录，均引用既有索引来源haskell-1980-rev-ed并标记source_backed。"
        "本批不写入生平或formal relations字段。"
    )

    if args.dry_run:
        print(f"dry-run passed: cards={cards_with_tables}; rows={len(additions)}; enrichment={len(existing)}->{len(existing)+len(additions)}; warnings=0; no files changed")
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
