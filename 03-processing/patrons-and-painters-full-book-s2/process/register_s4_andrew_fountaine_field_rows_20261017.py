from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
from scripts.build_field_facts import extract_records

TABLES = ROOT / "04-knowledge" / "tables"
ENRICHMENT = TABLES / "enrichment.jsonl"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
KU = "units/persons/andrew-fountaine"
ANCHOR = "s4-andrew-fountaine-card-fields-20261017"

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    target = [row for row in manifest if row.get("ku_id") == KU]
    assert len(target) == 1
    additions, sources, warnings, cards = extract_records(target)
    assert cards == 1 and len(additions) == 3 and not warnings, warnings
    assert {row["field"] for row in additions} == {"原文全名", "本书称谓", "乡间居所"}
    assert set(sources) == {"haskell-1980-rev-ed"}
    assert all(row.get("source_ref") and row.get("source_ids") == ["haskell-1980-rev-ed"] and row.get("evidence_status") == "source_backed" for row in additions)
    old_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    old_rows = [json.loads(line) for line in old_text.splitlines() if line.strip()]
    assert not any(row.get("ku_id") == KU for row in old_rows)
    keys = {(r.get("ku_id"), r.get("field"), r.get("value"), r.get("source_id")) for r in old_rows}
    ids = {r.get("enrichment_id", "") for r in old_rows}
    maximum = max((int(m.group(1)) for value in ids if (m := re.fullmatch(r"enr-(\d+)", value))), default=0)
    for offset, row in enumerate(additions, 1):
        row["enrichment_id"] = f"enr-{maximum + offset:05d}"
        assert (row["ku_id"], row["field"], row["value"], row.get("source_id", "")) not in keys
        assert row["enrichment_id"] not in ids
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 结构化字段登记（2026-10-17）\n\n"
        "Sir Andrew Fountaine 人物卡的原文全名、Haskell称谓与 Narford Hall 乡间居所已登记为三条 enrichment.jsonl 记录，"
        "均由 Haskell 书内来源 haskell-1980-rev-ed 支持；第13章受赠者名单没有被拆成逐件关系。"
    )
    if args.dry_run:
        print(f"dry-run passed: card_tables={cards}; rows={len(additions)}; enrichment={len(old_rows)}->{len(old_rows)+len(additions)}")
        return 0
    with ENRICHMENT.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(old_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: enrichment_rows={len(additions)}; enrichment={len(old_rows)}->{len(old_rows)+len(additions)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
