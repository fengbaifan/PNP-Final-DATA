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
KU = "units/persons/tirso-gonzalez"
ANCHOR = "s4-tirso-card-table-fields-20261017"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register structured fields for the Tirso Gonzalez S4 card.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    target_manifest = [row for row in manifest if row.get("ku_id") == KU]
    assert len(target_manifest) == 1
    additions, source_registry, warnings, cards_with_tables = extract_records(target_manifest)
    assert cards_with_tables == 1
    assert len(additions) == 2
    assert not warnings, warnings
    assert all(row.get("source_ref") and row.get("source_ids") for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert set(source_registry) == {"haskell-1980-rev-ed"}

    existing_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing_rows = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") == KU for row in existing_rows)
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
        "Tirso Gonzalez 人物卡的原文姓名与本书称谓两行已映射为 enrichment.jsonl，均关联 Haskell 来源 haskell-1980-rev-ed。"
        "本记录只补齐字段级来源结构，不改变 S3 身份决定、KU 映射或三条 S6 待审关系候选。"
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
