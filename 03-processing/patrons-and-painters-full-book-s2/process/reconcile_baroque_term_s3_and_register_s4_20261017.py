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
BAROQUE_PERIOD_CANDIDATE = "cand-3569"
CULTURAL_CATEGORY_CANDIDATE = "cand-4500"
PERIOD_KU = "units/terms/baroque"
GROUP = "sg3-term-cand-4500"
KU_ID = "units/terms/baroque-cultural-category-haskell"
CARD_REL = "04-knowledge/units/terms/baroque-cultural-category-haskell.md"
PROCESS_ANCHOR = "s3-s4-baroque-term-identity-20261017"
NAME_ZH = "哈斯克尔论述中的巴洛克艺术文化范畴"
NAME_EN = "The Baroque as an artistic-cultural category in Haskell's account"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CH2_QUOTE = (
    "The art of flattery was an essential ingredient of the Baroque. "
    "Urban VIII gave it every opportunity for expression."
)
CH10_QUOTE = (
    "The last ten years of the seventeenth century in England and France had seen "
    "the beginnings of an intellectual revolution that was to destroy the foundations On which\n"
    "Baroque civilisation had rested."
)
RELATION_STATEMENTS = {
    "st-chp2-secii-l91-104-baroque-flattery-interpretation",
    "st-chp2-seciv-l31-43-patronage-encouraged-barque-style",
    "st-chp3-seci-l3-14-mother-churches-baroque-inference",
    "st-chp3-secii-l74-81-decoration-major-baroque-achievement",
    "st-chp3-seciv-l141-150-cycle-reaction-against-baroque",
    "st-chp4-sec-ii-p112-attack-on-baroque",
    "st-chp6-p151-baroque-flowering-obscures-economic-crisis",
}


def normalized(text: str) -> str:
    return " ".join(text.split())


def card_text() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第2章，印刷页40，来源行99。",
                "sentence_summary": (
                    "哈斯克尔称奉承是巴洛克的重要成分，并说乌尔班八世为其表达提供了充分机会；"
                    "此处是作者的艺术文化解释。"
                ),
                "original_quotes": [
                    {"source_span": "line 99; print p. 40", "text": CH2_QUOTE},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                    "source_span": "line 99; print p. 40",
                },
            },
            {
                "citation": BOOK_CITATION,
                "location": "第10章，印刷页317，来源行123–124。",
                "sentence_summary": (
                    "哈斯克尔把英法17世纪末的思想革命描述为将动摇巴洛克文明的根基；"
                    "此句记录作者的文化史叙述，不作为独立验证的文明分期。"
                ),
                "original_quotes": [
                    {"source_span": "lines 123–124; print p. 317", "text": CH10_QUOTE},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                    "source_span": "lines 123–124; print p. 317",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch2 = "../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md"
    ch10 = "../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md"
    baroque = "baroque.md"
    process_link = f"../../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔在《赞助人与画家》中将“Baroque／巴洛克”作为艺术文化范畴使用的书内语境。第2章称奉承是巴洛克的重要成分，并说乌尔班八世给了这种表达充分机会；第10章将英法思想革命描述为将动摇“巴洛克文明”的根基。这些均是哈斯克尔的论述，不外推为独立验证的文明分期或外部通说。

**English:** This card records Haskell’s use of “Baroque” as an artistic-cultural category in *Patrons and Painters*. Chapter 2 calls flattery an essential ingredient of the Baroque and says Urban VIII gave it ample opportunity for expression. Chapter 10 describes the intellectual revolution in England and France as undermining the foundations of “Baroque civilisation.” These are Haskell’s claims; the card does not treat them as an independently verified civilizational periodization or a general scholarly consensus.

### 术语范围与边界

- 本卡收录书中把 Baroque 用作艺术文化范畴的语境，包括风格评价与“Baroque civilisation”表述。[第2章 p.40]({ch2})（L99）；[第10章 p.317]({ch10})（L123–124）。
- 与[巴洛克（Baroque）]({baroque})分开记录：该卡依据第一版序言，保存哈斯克尔对意大利艺术整体阶段的操作性分期。本卡记录其他章节中的文化—艺术范畴用法；两类语境相关，但不据此断言其在一般艺术史中互斥。
- Baroque painting 等较窄的媒介或具体风格候选保持各自的来源范围，不并入本卡。

### 名称

- 原文名称：Baroque；第2章 p.40（L99）、第10章 p.317（L123–124）。
- 中文显示名性质：项目描述性译名。

## 关系与证据

### 关系记录

当前没有已登记的正式关系。直接相关的七条 S2 关系候选留待 S6 逐条审查端点、关系类型、方向、语境与证据，不因本次登记转为正式关系。

### 关系候选入口

[本次 S3/S4 裁决与关系候选清单]({process_link})
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve Baroque term identity and register its broader source-local category."
    )
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
    period_row = decision_by_id[BAROQUE_PERIOD_CANDIDATE]
    cultural_row = decision_by_id[CULTURAL_CATEGORY_CANDIDATE]
    assert period_row["decision"] == "new" and not period_row.get("ku_id")
    assert "sg3-term-cand-3569" in period_row["resolution_note"]
    assert cultural_row["decision"] == "new" and not cultural_row.get("ku_id")
    assert "group=sg3-term-cand-4500" in cultural_row["resolution_note"]
    assert candidate_by_id[BAROQUE_PERIOD_CANDIDATE]["suggested_type"] == "term"
    assert candidate_by_id[CULTURAL_CATEGORY_CANDIDATE]["suggested_type"] == "term"

    period_card = ROOT / "04-knowledge" / "units" / "terms" / "baroque.md"
    period_card_text = period_card.read_text(encoding="utf-8-sig")
    assert "that whole phase of Italian art" in period_card_text
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(row.get("card_path") == CARD_REL for row in manifest)
    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "term"
        and NAME_EN.casefold() == (row.get("name_en") or "").casefold()
        for row in manifest
    )
    assert cultural_row["resolution_note"].count("group=sg3-term-cand-4500") == 1
    assert PROCESS_ANCHOR not in process_text

    for relative, quote in (
        ("02-sources/02-Markdown/02_CHP-2_sec_ii.md", CH2_QUOTE),
        ("02-sources/02-Markdown/10_CHP-10_sec_ii.md", CH10_QUOTE),
    ):
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert normalized(quote) in normalized(source_text), f"source quote changed: {relative}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CULTURAL_CATEGORY_CANDIDATE
        or row.get("object_candidate_id") == CULTURAL_CATEGORY_CANDIDATE
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
    period_note = (
        " S3复核（2026-10-17）：原 new 身份组决定撤回；此前 sg3-term-cand-3569 不再是有效新组。"
        f"改判 same → {PERIOD_KU}。候选在第1章称 Baroque period，并在第2、6、7、8、18章以 "
        "history of the Baroque、Roman Baroque、the Baroque 等形式延续；这与现有知识元直接引用哈斯克尔"
        "对 whole phase of Italian art 的操作性界定相符。此处是同一历史艺术阶段的跨章指称，没有证据要求另建时期 KU。"
    )
    planned_by_id[BAROQUE_PERIOD_CANDIDATE]["decision"] = "same"
    planned_by_id[BAROQUE_PERIOD_CANDIDATE]["ku_id"] = PERIOD_KU
    planned_by_id[BAROQUE_PERIOD_CANDIDATE]["process_ref"] = "S3-review-baroque-2026-10-17"
    planned_by_id[BAROQUE_PERIOD_CANDIDATE]["resolution_note"] += period_note

    category_note = (
        " S3复核（2026-10-17）：维持 new，单成员身份组 sg3-term-cand-4500。跨第2、3、4、6、10、14章"
        "的提及以 Baroque 作为艺术文化范畴承载风格、文明和历史评价；与现有 Baroque KU 的意大利艺术阶段"
        "操作性分期及 Baroque painting 媒介类别范围不同，未发现精确同类既有 KU。此区分只记录本书语境，"
        "不声称这些艺术史范畴在一般用法中互斥。第2章 p.40 L99 与第10章 p.317 L123–124 支持该书内范围。"
    )
    planned_by_id[CULTURAL_CATEGORY_CANDIDATE]["process_ref"] = "S3-review-baroque-2026-10-17"
    planned_by_id[CULTURAL_CATEGORY_CANDIDATE]["resolution_note"] += category_note
    planned_by_id[CULTURAL_CATEGORY_CANDIDATE]["resolution_note"] += (
        f" S4 registration: mapped {GROUP} to {KU_ID}."
    )
    planned_by_id[CULTURAL_CATEGORY_CANDIDATE]["ku_id"] = KU_ID

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "term",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {
        key: sum(row[key] for row in stats.values())
        for key in next(iter(stats.values()))
    }
    next_result = sync.update_result(
        result_text, stats, totals, len(planned_manifest)
    )
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S3/S4 term：Baroque 跨章身份复核与文化范畴登记（{DATE}）\n\n"
        f"- S3 将 {BAROQUE_PERIOD_CANDIDATE} 从原 new 组改为 same → {PERIOD_KU}。"
        "其“Baroque period”候选及第1、2、6、7、8、18章的相关提及，"
        "与既有卡所引哈斯克尔第一版序言的操作性分期相同；原组号与旧决定保留在对齐行中，"
        "但不再计入 S4 新组。\n"
        f"- {CULTURAL_CATEGORY_CANDIDATE} 维持 new，单成员组 {GROUP}，登记为"
        f"[{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "跨第2、3、4、6、10、14章的提及共同指向书内较广的艺术文化范畴，"
        "与巴洛克时期卡及 Baroque painting 媒介类别分开；本区分不外推为一般艺术史范畴互斥。"
        "卡片引第2章 p.40 L99 与第10章 p.317 L123–124，未作外部术语核验。\n"
        f"- 直接关联的七条 S2 关系候选为{', '.join(sorted(RELATION_STATEMENTS))}，均留待 S6；"
        "本次未写入 relations.csv 或 enrichment.jsonl。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"
    next_result = next_result.rstrip() + (
        f"\n\n### S3/S4 term：Baroque 跨章身份复核与文化范畴登记（{DATE}）\n\n"
        f"{BAROQUE_PERIOD_CANDIDATE} 改判 same → {PERIOD_KU}；原 new 组撤回。"
        f"{CULTURAL_CATEGORY_CANDIDATE} 保持 new，登记至[{NAME_ZH}（{NAME_EN}）]"
        "(../units/terms/baroque-cultural-category-haskell.md)。"
        "两项分别落实哈斯克尔的操作性历史分期与跨章艺术文化范畴用法。"
        "七条直接 S2 关系候选仍待 S6；本次未新增正式关系或 S5 补足。"
        f"当前 S3 same={sync.fmt(totals['same_candidates'])}、"
        f"new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组）；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条映射；KU总数{len(planned_manifest)}。"
    ) + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {BAROQUE_PERIOD_CANDIDATE} same->{PERIOD_KU}; "
            f"{GROUP}->{KU_ID}; relation_candidates={len(relation_candidates)}; "
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
        (
            i for i, line in enumerate(accepted_lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text(
        "\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n"
    )
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {BAROQUE_PERIOD_CANDIDATE} same->{PERIOD_KU}; "
        f"{GROUP}->{KU_ID}; relation_candidates={len(relation_candidates)}; "
        f"same={totals['same_candidates']}; new={totals['new_candidates']}/{totals['new_groups']}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
