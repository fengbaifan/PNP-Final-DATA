from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as process_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
CANDIDATE = "cand-4904"
GROUP = "sg3-event-cand-4904"
KU_ID = "units/events/first-war-of-castro"
CARD_REL = "04-knowledge/units/events/first-war-of-castro.md"
PROCESS_ANCHOR = "s3-s4-first-war-of-castro-20261017"
NAME_ZH = "第一次卡斯特罗战争"
NAME_EN = "First War of Castro"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CH2_QUOTE = "In 1641 the War of Castro broke out."
CH6_QUOTE_1 = (
    "The decline had already begun some three years earher with the outbreak of the\n"
    "War of Castro, a little town belonging to the Duke of Parma but situated well within papal territory."
)
CH6_QUOTE_2 = "In\nMarch 1644 a humiliating peace was signed"
RELATION_STATEMENTS = {
    "st-chp2-secvii-l3-3-parma-consequences-fragment",
    "st-chp2-secvii-l5-19-barberini-effects-continuation",
    "st-chp2-secvii-l5-19-financial-inquiry-threat",
    "st-chp6-p146-1644-peace",
    "st-chp6-p146-decline-war-onset",
}


def normalized(text: str) -> str:
    return " ".join(text.split())


def card_text() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第2章，印刷页58，来源行3。",
                "sentence_summary": "哈斯克尔明确称卡斯特罗战争于1641年爆发；同段继续叙述其对巴贝里尼的影响。",
                "original_quotes": [
                    {"source_span": "line 3; print p. 58", "text": CH2_QUOTE},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
                    "source_span": "line 3; print p. 58",
                },
            },
            {
                "citation": BOOK_CITATION,
                "location": "第6章，印刷页146，来源行5–8。",
                "sentence_summary": (
                    "哈斯克尔概述卡斯特罗战争的财政争端、军事联盟、行军至罗马及赞助受损，并称1644年3月签订不利和平；"
                    "战争细节与因果均按作者叙述保留。"
                ),
                "original_quotes": [
                    {"source_span": "lines 5–6; print p. 146", "text": CH6_QUOTE_1},
                    {"source_span": "lines 8; print p. 146", "text": CH6_QUOTE_2},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                    "source_span": "lines 5–8; print p. 146",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch2 = "../../../02-sources/02-Markdown/02_CHP-2_sec_vii.md"
    ch6 = "../../../02-sources/02-Markdown/06_CHP-6_sec_i.md"
    process_link = f"../../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔叙述的第一次卡斯特罗战争。第2章称战事于1641年爆发；第6章回顾财政争端、对帕尔马公爵的绝罚及卡斯特罗的迅速占领，并称法国、托斯卡纳、威尼斯和摩德纳联合反对巴贝里尼的扩张计划。哈斯克尔说外军再度向罗马进军、城市出现金融恐慌、艺术赞助遭受严重打击；他同时指出战争于1644年3月以一场屈辱性和约收束。这里保留作者叙述，不补写未见于来源的法律争端内容、条约名称或精确终战日。

**English:** This unit records the First War of Castro as narrated by Haskell. Chapter 2 says that the war broke out in 1641. Chapter 6 recalls financial disputes, the excommunication of the Duke of Parma, and the rapid occupation of Castro; it says that France, Tuscany, Venice, and Modena joined against the Barberini plan for territorial expansion. Haskell states that foreign troops again marched on Rome, the city experienced financial panic, and artistic patronage suffered severely; he also reports that a humiliating peace was signed in March 1644. This preserves the author's account without supplying an undocumented legal claim, treaty title, or exact end date.

### 名称与身份边界

- 中文名称“第一次卡斯特罗战争”是项目描述性名称，用于区别书中后来提到的第二次战争；来源在本段称 War of Castro。[第2章 p.58]({ch2})（L3）；[第6章 p.146]({ch6})（L5–8）。
- 本卡仅指1641年爆发的战争。索引项“First and Second Wars of Castro”是合并定位入口，现仍待证，不作为单一事件身份；后续第二次战争候选保持分立。
- 1644年3月和约在本来源段中没有正式名称或明确缔约方，本卡只记录战争叙述中的结果，不据此把未命名和平候选提升为独立 KU。

### 事件信息

- 事件性质：军事冲突；书内名称为 War of Castro。
- 开始时间：1641年，来源明言战争爆发。
- 结束时间：未给出精确日期；来源称1644年3月签订屈辱性和约。
- 地点：卡斯特罗；哈斯克尔称该镇属帕尔马公爵、位于教皇领土内。
- 书内叙述：作者概述军事联盟、外军进军罗马、城市金融恐慌及艺术赞助受损；这些影响和因果按哈斯克尔的叙述保留。

## 关系与证据

### 关系记录

当前没有已登记的正式关系。五条直接 S2 关系候选留待 S6 审查战争与帕尔马公爵、巴贝里尼及其他行动方之间的关系、方向和限定。

### 关系候选入口

[本次 S3/S4 裁决与未决战争候选]({process_link})
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the 1641–44 First War of Castro candidate in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id)
    decision = decision_by_id[CANDIDATE]
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "event"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert f"group={GROUP}" in decision["resolution_note"]
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted
    assert PROCESS_ANCHOR not in process_text
    legacy_path = ROOT / CARD_REL
    assert legacy_path.is_file()
    legacy_text = legacy_path.read_text(encoding="utf-8-sig")
    assert "第一、六章限定测试" in legacy_text
    assert "units/events/first-war-of-castro" not in {row.get("ku_id") for row in manifest}

    for relative, quotes in (
        ("02-sources/02-Markdown/02_CHP-2_sec_vii.md", (CH2_QUOTE,)),
        ("02-sources/02-Markdown/06_CHP-6_sec_i.md", (CH6_QUOTE_1, CH6_QUOTE_2)),
    ):
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        for quote in quotes:
            assert normalized(quote) in normalized(source_text), f"source quote changed: {relative}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    relation_candidates = [
        row for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row["statement_id"] for row in relation_candidates} == RELATION_STATEMENTS

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[CANDIDATE]["process_ref"] = "S3-review-castro-events-2026-10-17"
    planned_by_id[CANDIDATE]["resolution_note"] += (
        " S3复核（2026-10-17）：维持 new，单成员组 sg3-event-cand-4904。旧路径"
        "04-knowledge/units/events/first-war-of-castro.md 虽有历史草稿，但不在 ku-manifest.csv 或 accepted.yml，"
        "故不视为已有有效 KU 或 same 目标；本次沿用其稳定对象路径，按现行双语与来源契约完成 S4 登记。"
        "该事件指1641年爆发的第一次战争，不并入索引的 First and Second Wars of Castro 总入口、"
        "后续第二次战争候选 cand-6289，或身份边界仍待证的未命名和约候选 cand-6259。"
    )
    planned_by_id[CANDIDATE]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_by_id[CANDIDATE]["ku_id"] = KU_ID

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "event",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    next_process = next_process.rstrip() + (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S3/S4 event：第一次卡斯特罗战争跨章身份登记（{DATE}）\n\n"
        f"- {CANDIDATE} 保持 new，单成员组 {GROUP}，登记为"
        f"[{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "第2章 p.58 明言1641年战争爆发；第6章 p.146 补述对帕尔马公爵的财政争端、军事进程及1644年3月和约。"
        "卡片路径此前存在一张未登记的历史草稿，但 manifest 和 accepted.yml 均无该对象；本次沿用固定路径，"
        "将其改写为当前有效的双语来源卡，不把孤立文件当作既有 KU。\n"
        "- 身份边界保持明确：cand-0607 是合并索引入口且仍 undecided；cand-6289 是后续第二次战争；"
        "cand-6259 的未命名和约仍 undecided，不因记录战争结果而提升。五条直接 S2 关系候选"
        f"（{', '.join(sorted(RELATION_STATEMENTS))}）留待 S6；未写入 relations.csv 或 enrichment.jsonl。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    ) + "\n"
    next_result = next_result.rstrip() + (
        f"\n\n### S3/S4 event：第一次卡斯特罗战争跨章身份登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持 new 并登记为[{NAME_ZH}（{NAME_EN}）]"
        "(../units/events/first-war-of-castro.md)。历史草稿不在当前 manifest/accepted 中；"
        "本次沿用对象路径并更新为双语来源卡。索引总入口、第二次战争和未命名和约分别保留原待决／独立去向。"
        "五条直接关系候选仍待 S6，本次未新增正式关系或补足事实。"
        f"当前 S3 same={sync.fmt(totals['same_candidates'])}、"
        f"new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组）；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射；KU总数{len(planned_manifest)}。"
    ) + "\n"
    next_result, n = re.subn(
        r"^2026-10-17 strict-stage 表审计通过：.*$",
        (
            "2026-10-17 strict-stage 表审计通过：errors=[]、s2_missing=[]。"
            f"当前待登记 S4 的 new 候选映射为{sync.fmt(totals['pending_members'])}条（不含外部身份记录）；"
            "逐类型候选决定、new 组及 S4 登记/待登记分布见"
            "[过程记录的S3统计表](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#按类型决定数)。"
            "另有两条既有字段来源引用未能从对应卡片source列表解析（enr-06678、enr-06937）；相关字段仍保留原状态。"
            "审计还提示S2迁移的语义质量仍须按关联过程记录检查；结构一致性不代表独立语义验收，也不产生准确率、召回率或语义处理吞吐指标。"
        ),
        next_result,
        count=1,
        flags=re.M,
    )
    assert n == 1

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} new->{KU_ID}; relation_candidates={len(relation_candidates)}; "
            f"same={totals['same_candidates']}; new={totals['new_candidates']}/{totals['new_groups']}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; legacy_path_reused=true; card_frontmatter=valid"
        )
        return 0

    legacy_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} new->{KU_ID}; relation_candidates={len(relation_candidates)}; "
        f"same={totals['same_candidates']}; new={totals['new_candidates']}/{totals['new_groups']}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; legacy_path_reused=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
