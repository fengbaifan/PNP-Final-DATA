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
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
KU = "units/archives/giuseppe-delogu-g-b-castiglione-il-grechetto-1928"
ANCHOR = "s4-archive-delogu-grechetto-fields-20261017"

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    target = [r for r in manifest if r.get("ku_id") == KU]
    assert len(target) == 1
    additions, sources, warnings, cards = extract_records(target)
    expected = {"中文工作题名", "原题名", "文献类型", "作者（按书目著录）", "出版地", "出版年"}
    assert cards == 1 and len(additions) == 6 and not warnings, warnings
    assert {r["field"] for r in additions} == expected
    assert set(sources) == {"haskell-1980-rev-ed"}
    assert all(r.get("source_ref") and r.get("source_ids") == ["haskell-1980-rev-ed"] and r.get("evidence_status") == "source_backed" for r in additions)

    old_text = ENRICHMENT.read_text(encoding="utf-8-sig")
    old_rows = [json.loads(line) for line in old_text.splitlines() if line.strip()]
    assert not any(r.get("ku_id") == KU for r in old_rows)
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
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 archive 结构化字段登记（2026-10-17）\n\n"
        "Delogu 1928 书目卡的中文工作题名、原题名、文献类型、作者、出版地及出版年已登记为六条 enrichment.jsonl 记录，"
        "均由 Haskell 全书书目或第1章引文支持。原题名按 S2 页图校正，Delogu 专著和其第40页注9未独立查阅。"
    )
    result_text = RESULT.read_text(encoding="utf-8-sig")
    result_text, n = re.subn(
        r"(\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \| )[0-9,]+(条，其中)",
        rf"\g<1>{len(old_rows) + len(additions):,}\g<2>",
        result_text,
        count=1,
    )
    assert n == 1

    if args.dry_run:
        print(f"dry-run passed: card_tables={cards}; rows={len(additions)}; enrichment={len(old_rows)}->{len(old_rows)+len(additions)}")
        return 0
    with ENRICHMENT.open("w", encoding="utf-8-sig", newline="\n") as handle:
        handle.write(old_text.rstrip("\r\n") + "\n")
        for row in additions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: enrichment_rows={len(additions)}; enrichment={len(old_rows)}->{len(old_rows)+len(additions)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
