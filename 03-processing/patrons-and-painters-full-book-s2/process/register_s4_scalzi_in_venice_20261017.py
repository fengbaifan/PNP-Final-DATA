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
CANDIDATE = "cand-2389"
GROUP = "sg3-institution-cand-2389"
KU_ID = "units/institutions/scalzi-in-venice"
CARD_REL = "04-knowledge/units/institutions/scalzi-in-venice.md"
PROCESS_ANCHOR = "s3-s4-scalzi-in-venice-20261017"
NAME_ZH = "威尼斯赤足加尔默罗会"
NAME_EN = "Scalzi in Venice"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
ARRIVAL_QUOTE = (
    "The Scalzi, for instance, a particularly strict off-shoot of the Carmelite Order, "
    "came to Venice in 1633."
)
MOTHER_ORDER_QUOTE = "The patronage of their mother Order, the Carmelites, was fully as splendid."
RELATION_STATEMENTS = {
    "st-chp9-p269-benefactions-and-public-alms",
    "st-chp9-p269-scalzi-arrival-1633",
    "st-chp9-p269-scalzi-luxury-pamphlet",
    "st-chp9-p269-scalzi-noble-links-missions",
    "st-chp9-p269-scalzi-original-church-too-small",
    "st-chp9-p270-carmelite-patronage-comparison",
}


def normalized(text: str) -> str:
    return " ".join(text.split())


def card_text() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第9章，印刷页269，来源行21。",
                "sentence_summary": (
                    "哈斯克尔将 Scalzi 描述为加尔默罗会的严格分支，并称其1633年到达威尼斯；"
                    "该年份是到达威尼斯的时间，不是该修会的创立时间。"
                ),
                "original_quotes": [
                    {"source_span": "line 21; print p. 269", "text": ARRIVAL_QUOTE},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                    "source_span": "line 21; print p. 269",
                },
            },
            {
                "citation": BOOK_CITATION,
                "location": "第9章，印刷页270，来源行29。",
                "sentence_summary": (
                    "哈斯克尔把加尔默罗会称作 Scalzi 的母会；此处明确将两个机构层级分开。"
                ),
                "original_quotes": [
                    {"source_span": "line 29; print p. 270", "text": MOTHER_ORDER_QUOTE},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                    "source_span": "line 29; print p. 270",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = "../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md"
    carmelites = "carmelites.md"
    process_link = f"../../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔所述的威尼斯赤足加尔默罗会（Scalzi）。第9章称其为加尔默罗会的严格分支，并记载其1633年到达威尼斯。哈斯克尔还叙述其与当地贵族的联系、在伯罗奔尼撒的传教活动以及与威尼斯军队的联系；这些内容限于本书对其威尼斯活动的记载，不外推为该修会的完整历史。

**English:** This unit records the Scalzi in Haskell’s Venetian account. Chapter 9 describes them as a particularly strict offshoot of the Carmelite Order and says they came to Venice in 1633. Haskell also notes their links with local nobles, missionary work in the Peloponnese, and association with Venetian troops. These points are limited to the book’s account of their Venetian activity and do not supply a complete history of the order.

### 名称与身份边界

- 原文称谓：Scalzi；中文显示名“威尼斯赤足加尔默罗会”为项目描述性译名。[第9章 p.269]({source})（L21）。
- 第9章 p.270 明确称 Carmelites 为 Scalzi 的母会。[第9章 p.270]({source})（L29）；本卡只记录其分支／威尼斯语境，不与母会合并。
- “Scalzi”在这里是修会分支，不是其在威尼斯的教堂建筑；教堂及相关委托事实保留为独立对象和关系候选。

### 基本信息

- 机构性质：哈斯克尔所述加尔默罗会的严格分支。
- 威尼斯活动：来源称其于1633年到达威尼斯；该年不作为修会创立时间。
- 来源描述的活动：与多位当地贵族建立联系；在伯罗奔尼撒传教并与威尼斯军队保持密切联系。
- 与母会的边界：[加尔默罗会（Carmelites）]({carmelites})在原书中被明确称为其母会；该机构身份与本卡分开。

## 关系与证据

### 关系记录

当前没有已登记的正式关系。六条直接 S2 关系候选留待 S6 审查修会、母会、教堂、赞助人和建筑师之间的端点、角色、方向及语境。

### 关系候选入口

[本次 S3/S4 裁决与关系候选清单]({process_link})
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Scalzi institution in Venice in S4.")
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
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "institution"
    assert decision["decision"] == "new" and not decision.get("ku_id")
    assert f"group={GROUP}" in decision["resolution_note"]
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not (ROOT / CARD_REL).exists() and CARD_REL not in accepted
    assert PROCESS_ANCHOR not in process_text
    assert any(row.get("candidate_id") == "cand-0563" and row.get("decision") == "new" for row in alignments)
    assert any(row.get("candidate_id") == "cand-5119" and row.get("decision") == "new" for row in alignments)
    assert not any(
        row.get("type") == "institution"
        and NAME_EN.casefold() == (row.get("name_en") or "").casefold()
        for row in manifest
    )

    source_file = ROOT / "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
    source_text = source_file.read_text(encoding="utf-8-sig")
    assert normalized(ARRIVAL_QUOTE) in normalized(source_text)
    assert normalized(MOTHER_ORDER_QUOTE) in normalized(source_text)
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
    planned_by_id[CANDIDATE]["process_ref"] = "S3-review-scalzi-institution-2026-10-17"
    planned_by_id[CANDIDATE]["resolution_note"] += (
        " S3复核（2026-10-17）：维持 new，单成员组 sg3-institution-cand-2389。S.csv#77 的第9章 pp.269–270"
        "将 Scalzi 识别为加尔默罗会的严格分支，并称其1633年到达威尼斯。第9章 p.270 另称 Carmelites 是其母会，"
        "支持与 cand-0563 的广义母会候选保持分立；cand-5119 是另一修会 Discalced Trinitarians，也不因“赤足”相似而合并。"
        "当前 manifest 未见与本候选同粒度的有效 institution KU。"
    )
    planned_by_id[CANDIDATE]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_by_id[CANDIDATE]["ku_id"] = KU_ID

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "institution",
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
        f"### S3/S4 institution：Scalzi 威尼斯分支登记（{DATE}）\n\n"
        f"- {CANDIDATE} 保持 new，单成员身份组 {GROUP}，登记为"
        f"[{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "第9章 p.269 将 Scalzi 说成加尔默罗会的严格分支，并称其1633年到达威尼斯；p.270 明确将 Carmelites 称为其母会。"
        f"因此 cand-0563 母会候选保持独立；cand-5119 Discalced Trinitarians 亦为不同修会，不因共享“赤足”描述合并。\n"
        f"- 六条直接 S2 关系候选为{', '.join(sorted(RELATION_STATEMENTS))}，留待 S6；"
        "修会、母会、教堂、赞助人和建筑师之间本次未登记 formal relations 或 enrichment。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    ) + "\n"
    next_result = next_result.rstrip() + (
        f"\n\n### S3/S4 institution：Scalzi 威尼斯分支登记（{DATE}）\n\n"
        f"{CANDIDATE} 保持 new 并登记至[{NAME_ZH}（{NAME_EN}）]"
        "(../units/institutions/scalzi-in-venice.md)。卡片将其与母会 Carmelites 及另一修会 Discalced Trinitarians 分开。"
        "六条直接关系候选仍待 S6；本次未新增正式关系或 S5 补足。"
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
            f"dry-run passed: {GROUP}->{KU_ID}; relation_candidates={len(relation_candidates)}; "
            f"same={totals['same_candidates']}; new={totals['new_candidates']}/{totals['new_groups']}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; card_frontmatter=valid"
        )
        return 0

    (ROOT / CARD_REL).write_text(card, encoding="utf-8-sig", newline="\n")
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
        f"applied: {GROUP}->{KU_ID}; relation_candidates={len(relation_candidates)}; "
        f"same={totals['same_candidates']}; new={totals['new_candidates']}/{totals['new_groups']}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
