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
KU = "units/persons/giorgio-massari"
ANCHOR = "s4-giorgio-massari-card-fields-20261018"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register source-backed structured fields for Giorgio Massari.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    target = [row for row in manifest if row.get("ku_id") == KU]
    assert len(target) == 1
    additions, source_registry, warnings, cards_with_tables = extract_records(target)
    assert cards_with_tables == 1
    assert len(additions) == 3
    assert {row["field"] for row in additions} == {"原文全名", "本书称谓", "受聘项目"}
    assert not warnings, warnings
    assert all(row.get("source_ref") and row.get("source_ids") == ["haskell-1980-rev-ed"] for row in additions)
    assert all(row.get("evidence_status") == "source_backed" for row in additions)
    assert set(source_registry) == {"haskell-1980-rev-ed"}

    existing_text = ENRICHMENT_PATH.read_text(encoding="utf-8-sig")
    existing = [json.loads(line) for line in existing_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") == KU for row in existing)
    natural_keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id")) for r in existing}
    ids = {row.get("enrichment_id", "") for row in existing}
    max_id = max((int(m.group(1)) for value in ids if (m := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{max_id + offset:05d}"
        key = (row["ku_id"], row["field"], row["value"], row.get("source_id", ""))
        assert key not in natural_keys
        assert row["enrichment_id"] not in ids

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 结构化字段登记（2026-10-18）\n\n"
        "Giorgio Massari 人物卡中的原文全名、建筑师称谓及 Gesuati 新教堂项目已按 "
        "`build_field_facts.extract_records` 登记为三条 enrichment.jsonl 记录，均由 Haskell 书内来源 "
        "`haskell-1980-rev-ed` 支持；未添加外部身份事实，关系候选仍待 S6。"
    )

    if args.dry_run:
        print(f"dry-run passed: card_tables={cards_with_tables}; rows={len(additions)}; enrichment={len(existing)}->{len(existing)+len(additions)}")
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
