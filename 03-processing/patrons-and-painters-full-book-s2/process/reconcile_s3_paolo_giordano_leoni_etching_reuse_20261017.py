from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ENTITY_PATH = TABLES / "entity-candidates.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CID = "cand-5545"
GROUP = "workgrp-ce2612f695fe07"
KU = "units/works/ottavio-leoni-paolo-giordano-orsini-duke-of-bracciano"
STATEMENTS = [
    "st-chp4-sec-i-l20-24-leoni-etching",
    "st-chp4-sec-ii-l65-67-p17c-credit",
    "st-chp4-sec-ii-l65-67-p17c-subject",
    "st-chp4-sec-i-l20-24-etching-depicts-paolo",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(ENTITY_PATH)
    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CID)
    alignment_row = next(row for row in alignment if row.get("candidate_id") == CID and not row.get("external_source"))
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    assert candidate["suggested_type"] == "work"
    assert alignment_row["decision"] == "new" and not alignment_row.get("ku_id")
    assert sync.get_group(alignment_row.get("resolution_note", "")) == GROUP
    assert KU in manifest_by_id and manifest_by_id[KU]["type"] == "work"
    assert (ROOT / manifest_by_id[KU]["card_path"]).exists()

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    for sid in STATEMENTS:
        assert sid in statements and statements[sid].get("qualifiers", {}).get("relation_candidate")
    assert statements["st-chp4-sec-i-l20-24-leoni-etching"]["original_quote"].startswith("Ottavio Leoni made a superb etching")
    assert "Leoni: Paolo Giordano II" in statements["st-chp4-sec-ii-l65-67-p17c-credit"]["original_quote"]

    planned_alignment = [dict(row) for row in alignment]
    for row in planned_alignment:
        if row.get("candidate_id") == CID and not row.get("external_source"):
            row["decision"] = "same"
            row["ku_id"] = KU
            row["process_ref"] = "S3-cross-chapter-work-reuse-2026-10-17"
            row["resolution_note"] = (
                f"prior_group={GROUP}; S3 correction 2026-10-17: same as existing work KU {KU}. "
                "The chapter text identifies Ottavio Leoni's etching as Plate 17c; the plate caption names Leoni and Paolo Giordano II, "
                "and the accepted card records the same creator, subject, and plate. No separate work is indicated."
            )
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s3-paolo-giordano-plate17c-work-reuse\"></a>\n\n"
        "### S3 work 复用修正：Ottavio Leoni 图版17c（2026-10-17）\n\n"
        f"`{CID}` 原 `new` 组 `{GROUP}` 与既有 `{KU}` 为同一作品。第4章 p.20 称 Ottavio Leoni 制作了 Paolo Giordano II 蚀刻肖像并标作图版17c；"
        "图版17c目录再次署名 Leoni 并题为 Paolo Giordano Orsini, Duke of Bracciano。故将该候选改为 `same` 并复用既有作品 KU，不新建卡片。"
        "对应 S2 关系候选沿用既有作品端点；本次未改正式关系。\n\n"
        f"S4 登记仍为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )
    result_text += (
        "\n\n### S3 work：Paolo Giordano II 图版17c复用（2026-10-17）\n\n"
        f"`{CID}` 从原 `new` 身份组修正为 `same`，映射至[Paolo Giordano II 图版17c作品卡](../units/works/ottavio-leoni-paolo-giordano-orsini-duke-of-bracciano.md)。"
        "正文描述、图版目录署名及图版号支持同一作品判断；未重复建卡。"
        f"S4 登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )

    if args.dry_run:
        print(f"S3 work reuse dry-run passed: {CID} -> same {KU}; no new KU")
        print(
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
            f"manifest={len(manifest):,} (unchanged)"
        )
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CID}=same->{KU}; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
