from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATES_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CARDINAL_CANDIDATE = "cand-0639"
MONSIGNOR_CANDIDATE = "cand-10945"
CARDINAL_GROUP = "new-person:angelo-cesi-d4e25faff9"
MONSIGNOR_GROUP = "new-person:angelo-cesi-monsignor-20261017"
PROCESS_REF = "S3-cross-chapter-groups-2026-10-17"


def main() -> int:
    parser = argparse.ArgumentParser(description="Separate the two Angelo Cesi identities in S3.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(CANDIDATES_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_by_candidate = {
        row["candidate_id"]: row
        for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert {CARDINAL_CANDIDATE, MONSIGNOR_CANDIDATE} <= alignment_by_candidate.keys()
    assert CARDINAL_CANDIDATE in candidate_by_id and MONSIGNOR_CANDIDATE in candidate_by_id
    assert candidate_by_id[CARDINAL_CANDIDATE]["suggested_type"] == "person"
    assert candidate_by_id[MONSIGNOR_CANDIDATE]["suggested_type"] == "person"
    assert candidate_by_id[MONSIGNOR_CANDIDATE]["detail"].startswith(
        "Keep distinct in S2 from the indexed Bishop Angelo Cesi candidate until global identity alignment."
    )
    for cid in (CARDINAL_CANDIDATE, MONSIGNOR_CANDIDATE):
        row = alignment_by_candidate[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == CARDINAL_GROUP
    assert {
        row["candidate_id"] for row in alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row["decision"] == "new"
        and sync.get_group(row.get("resolution_note", "")) == CARDINAL_GROUP
    } == {CARDINAL_CANDIDATE, MONSIGNOR_CANDIDATE}

    ch3 = (ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_ii.md").read_text(encoding="utf-8-sig")
    ch20 = (ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
    assert "The High Altar had been originally dedicated to the Nativity; its decoration had been promised by Cardinal Angelo Cesi." in " ".join(ch3.split())
    assert "his brother, Monsignor Angelo Cesi, was a much less accommodating patron." in " ".join(ch20.split())

    previous_cardinal_note = alignment_by_candidate[CARDINAL_CANDIDATE]["resolution_note"]
    previous_monsignor_note = alignment_by_candidate[MONSIGNOR_CANDIDATE]["resolution_note"]
    planned_alignment = [dict(row) for row in alignment]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[CARDINAL_CANDIDATE]["process_ref"] = PROCESS_REF
    planned_by_id[CARDINAL_CANDIDATE]["resolution_note"] = (
        f"source_ref=candidate={CARDINAL_CANDIDATE};index_entry=C.csv#163;index_pages=69,70,400; "
        f"group={CARDINAL_GROUP}; S3 cross-chapter review 2026-10-17: retain as a source-local person group for Cardinal Angelo Cesi, "
        "named in chapter 3, pp.69–70. The postscript, p.400, separately names Monsignor Angelo Cesi as the Cardinal's brother; "
        f"the brother is {MONSIGNOR_CANDIDATE} and is no longer grouped here. The index page locator is not identity evidence for merging the two brothers. "
        f"Previous same-name grouping rationale superseded; see {PROCESS_REF}. No existing same-type person KU matched; S4 registration pending."
    )
    planned_by_id[MONSIGNOR_CANDIDATE]["process_ref"] = PROCESS_REF
    planned_by_id[MONSIGNOR_CANDIDATE]["resolution_note"] = (
        f"source_ref=candidate={MONSIGNOR_CANDIDATE};candidate_source_ref=chp-20:20_CHP-20Postscript:l46-57#L53; "
        "source_file=02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57; "
        "s2_mentions=m-chp20-p400-037@02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57[Monsignor Angelo Cesi]; "
        f"group={MONSIGNOR_GROUP}; S3 cross-chapter review 2026-10-17: the p.400 passage explicitly identifies Monsignor Angelo Cesi as the brother of Cardinal Angelo Cesi ({CARDINAL_CANDIDATE}). "
        "They share a name but are distinct people. Retain as a source-local new person group; no existing same-type person KU matched; S4 registration pending. "
        f"Previous same-name grouping rationale superseded; see {PROCESS_REF}."
    )

    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    planned_candidate_by_id[MONSIGNOR_CANDIDATE]["detail"] = (
        "S3 cross-chapter review 2026-10-17 resolves this Monsignor Angelo Cesi as a distinct person from the indexed Cardinal Angelo Cesi candidate cand-0639: "
        "the p.400 passage identifies him as the Cardinal's brother. The sibling statement remains source evidence, not a formal relation."
    )

    stats = sync.summarize_by_type(planned_candidates, planned_alignment)
    totals = {key: sum(part[key] for part in stats.values()) for key in next(iter(stats.values()))}
    assert totals["new_candidates"] == 5009 and totals["new_groups"] == 4832
    assert totals["registered_groups"] == 422 and totals["pending_groups"] == 4410
    assert totals["pending_members"] == 4471

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    old_audit_detail = "含4,471条候选决定映射（4,409组）和15条外部身份记录。"
    assert result_text.count(old_audit_detail) == 1
    result_text = result_text.replace(
        old_audit_detail, "含4,471条候选决定映射（4,410组）和15条外部身份记录。"
    )
    result_text += (
        "\n\n### S3 跨章多候选身份组：分类型核对（2026-10-17）\n\n"
        "接续现有 alignment 记录，核对29个跨章、多候选 `decision=new` 身份组的组边界：archive 3组、institution 1组、person 16组、place 2组、term 4组、work 3组。28组保留原有分组；原 Angelo Cesi 人物组拆分为 Cardinal Angelo Cesi 与其兄弟 Monsignor Angelo Cesi 两个 new person 组。分类型 S3/S4 计数见上表；逐候选证据及历史理由见[对齐表](../tables/alignment.csv)与[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)。\n"
        "S3 new=5,009个候选／4,832组；S4 已登记422组／538条映射，待登记4,410组／4,471条映射；KU总数1,441。"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    assert "#s3-cross-chapter-group-review-20261017" not in process_text
    process_text += (
        "\n\n<a id=\"s3-cross-chapter-group-review-20261017\"></a>\n\n"
        "### S3 跨章多候选身份组：分类型核对与 Cesi 拆分（2026-10-17）\n\n"
        "从现有 alignment 中筛出29个跨章、多候选 `new` 组；组成员和逐候选来源锚点仍以各 alignment 行为准。未重跑或改写其余已有裁决。类型分布如下：\n\n"
        "| 类型 | 原多候选跨章组数 | 处置 |\n|---|---:|---|\n"
        "| archive | 3 | 保留现有 new 组 |\n"
        "| institution | 1 | 保留现有 new 组 |\n"
        "| person | 16 | 15组保留；1组拆分为两个独立 new person 组 |\n"
        "| place | 2 | 保留现有 new 组 |\n"
        "| term | 4 | 保留现有 new 组 |\n"
        "| work | 3 | 保留现有 new 组 |\n"
        "| **合计** | **29** | **28组保留；1组拆分** |\n\n"
        "拆分依据：第3章 p.69 明称 `Cardinal Angelo Cesi`，说明他在1606年去世；第二版后记 p.400 称 `Monsignor Angelo Cesi` 为 Cardinal Cesi 的兄弟。两处同名并非同一人物。索引候选 `cand-0639` 保留 `new-person:angelo-cesi-d4e25faff9`；`cand-10945` 单独进入 `new-person:angelo-cesi-monsignor-20261017`。原两行按同名归组的理由完整保存在本过程记录及下文；alignment 当前备注改述明确的兄弟关系。两个新组均待 S4，不复用现有同类型人物 KU。\n\n"
        "原裁决理由（保留历史）：\n\n"
        f"- `{CARDINAL_CANDIDATE}`：{previous_cardinal_note}\n"
        f"- `{MONSIGNOR_CANDIDATE}`：{previous_monsignor_note}\n\n"
        "未更改原文 statement 端点或 `relations.csv`；兄弟关系仍以 S2 来源陈述为据，不在 S3 新增正式关系。其余28个原多候选跨章组沿用各自已有 `resolution_note`、`process_ref` 和 S4 去向。当前 S3 new=5,009个候选／4,832组；S4已登记422组／538条映射，待登记4,410组／4,471条映射；KU总数1,441。"
    )

    if args.dry_run:
        print("Angelo Cesi sibling identity dry-run passed")
        print(f"{CARDINAL_CANDIDATE} -> {CARDINAL_GROUP}; {MONSIGNOR_CANDIDATE} -> {MONSIGNOR_GROUP}")
        print("29 cross-chapter multi-candidate new groups reviewed by type; 28 retained, one split")
        print(f"S3 new={totals['new_candidates']}/{totals['new_groups']}; pending S4={totals['pending_groups']}/{totals['pending_members']}")
        print("source sibling statement, prior rationale preservation, type table, and result counts checked; no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    sync.write_csv(CANDIDATES_PATH, candidate_fields, planned_candidates)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CARDINAL_CANDIDATE} and {MONSIGNOR_CANDIDATE} separated; "
        f"new groups={totals['new_groups']}; pending S4={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
