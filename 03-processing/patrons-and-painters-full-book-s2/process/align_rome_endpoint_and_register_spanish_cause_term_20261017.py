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
ROME_CANDIDATE = "cand-6474"
ROME_KU = "units/places/rome"
SPANISH_CAUSE_CANDIDATE = "cand-4404"
GROUP = "sg3-term-cand-4404"
KU_ID = "units/terms/spanish-cause-in-rome-haskell-account"
CARD_REL = "04-knowledge/units/terms/spanish-cause-in-rome-haskell-account.md"
PROCESS_ANCHOR = "s3-s4-spanish-cause-in-rome-20261017"
NAME_ZH = "哈斯克尔所述罗马的亲西班牙政治倾向"
NAME_EN = "The Spanish cause in Rome in Haskell's account"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
QUOTES = {
    "02-sources/02-Markdown/02_CHP-2_sec_ii.md": (
        "one of the chief partisans in Rome of the Spanish cause",
    ),
    "02-sources/02-Markdown/05_CHP-5_sec_iii.md": (
        "Monsignor Raggi, another of his admirers, was a Genoese and also devoted to the Spanish cause. "
        "So too was the Modenese Count Camillo Carandini.",
    ),
    "02-sources/02-Markdown/07_CHP-7_sec_i.md": (
        "Moreover, both were devoted to the Spanish cause.",
    ),
}
RELATION_STATEMENTS = {
    "st-chp2-secii-l42-50-ginnasi_profile_partisan",
    "st-chp5-notes-l142-rapaccioli-report",
    "st-chp5-p137-carandini-spanish-alignment",
    "st-chp5-p137-raggi-devoted-to-spanish-cause",
    "st-chp7-p173-i07",
    "st-chp7-p173-i08",
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
                "location": "第2章，印刷页35，来源行49。",
                "sentence_summary": "哈斯克尔称枢机 Ginnasi 是罗马西班牙政治事业的主要支持者之一；此称谓指政治倾向，不是正式机构名称。",
                "original_quotes": [{"source_span": "line 49; print p. 35", "text": QUOTES["02-sources/02-Markdown/02_CHP-2_sec_ii.md"][0]}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md", "source_span": "line 49; print p. 35"},
            },
            {
                "citation": BOOK_CITATION,
                "location": "第5章，印刷页137，来源行73。",
                "sentence_summary": "哈斯克尔称 Raggi 与 Carandini 都支持西班牙事业；这是对两人政治倾向的书内描述，不据此建立党派或固定成员组织。",
                "original_quotes": [{"source_span": "line 73; print p. 137", "text": QUOTES["02-sources/02-Markdown/05_CHP-5_sec_iii.md"][0]}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "source_span": "line 73; print p. 137"},
            },
            {
                "citation": BOOK_CITATION,
                "location": "第7章，印刷页173，来源行38。",
                "sentence_summary": "哈斯克尔称 Giovanni Battista Crescenzi 与其枢机兄弟均支持西班牙事业；表述属于作者的政治关联叙述。",
                "original_quotes": [{"source_span": "line 38; print p. 173", "text": QUOTES["02-sources/02-Markdown/07_CHP-7_sec_i.md"][0]}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "source_span": "line 38; print p. 173"},
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch2 = "../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md"
    ch5 = "../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md"
    ch7 = "../../../02-sources/02-Markdown/07_CHP-7_sec_i.md"
    sphere = "cerquozzi-patrons-spanish-sphere-context.md"
    process_link = f"../../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本术语记录哈斯克尔在《赞助人与画家》中对罗马及相关赞助人所用的“Spanish cause”称谓。第2章称枢机 Ginnasi 是罗马西班牙事业的主要支持者之一；第5章称 Raggi 与 Carandini 支持这一事业；第7章又以同样表述描述 Giovanni Battista Crescenzi 与其枢机兄弟。此处将该词组作为书内政治倾向概念，不把它写成正式党派、机构或具有固定成员的组织。

**English:** This term records Haskell’s use of “the Spanish cause” for political alignment in Rome and related patronage contexts in *Patrons and Painters*. Chapter 2 calls Cardinal Ginnasi one of Rome’s chief partisans of the Spanish cause; Chapter 5 says Raggi and Carandini were devoted to it; Chapter 7 uses the same description for Giovanni Battista Crescenzi and his cardinal brother. The phrase is treated here as a source-bound political alignment, not as a formally named party, institution, or organization with fixed membership.

### 术语范围与边界

- 书内称谓包括 “partisan of the Spanish cause,” “devoted to the Spanish cause” 及相关 political affiliations，分别按原句和说话者保留。[第2章 p.35]({ch2})（L49）；[第5章 p.137]({ch5})（L73）；[第7章 p.173]({ch7})（L38）。
- 与[塞尔奎齐赞助人的西班牙势力圈语境]({sphere})分开：该卡记录特定赞助人群体的 “Spanish sphere of influence” 语境，本卡记录跨章节出现的政治事业／倾向称谓。二者有重叠语境，不据此推定正式组织或统一政治控制。
- 中文显示名为语义性项目译名；不将 “Spanish cause” 翻译成某个具名政党或机构。

### 名称

- 原文名称：Spanish cause；第2章 p.35（L49）、第5章 p.137（L73）、第7章 p.173（L38）。
- 中文显示名性质：项目描述性译名。

## 关系与证据

### 关系记录

当前没有已登记的正式关系。六条直接 S2 关系候选留待 S6 审查人物与该政治倾向之间的表述、方向、语气和证据。

### 关系候选入口

[本次 S3/S4 裁决与关系候选清单]({process_link})
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Align the Rome endpoint and register the Spanish-cause term in S4.")
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
    decision_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    assert len(decision_by_id) == len(candidate_by_id)
    rome_row = decision_by_id[ROME_CANDIDATE]
    term_row = decision_by_id[SPANISH_CAUSE_CANDIDATE]
    assert rome_row["decision"] == "new" and not rome_row.get("ku_id")
    assert "sg3-place-cand-6474" in rome_row["resolution_note"]
    assert term_row["decision"] == "new" and not term_row.get("ku_id")
    assert "group=sg3-term-cand-4404" in term_row["resolution_note"]
    assert candidate_by_id[ROME_CANDIDATE]["suggested_type"] == "place"
    assert candidate_by_id[SPANISH_CAUSE_CANDIDATE]["suggested_type"] == "term"
    assert any(row.get("ku_id") == ROME_KU for row in manifest)
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not (ROOT / CARD_REL).exists() and CARD_REL not in accepted
    assert PROCESS_ANCHOR not in process_text
    sphere_card = ROOT / "04-knowledge" / "units" / "terms" / "cerquozzi-patrons-spanish-sphere-context.md"
    assert "within the Spanish sphere of influence" in sphere_card.read_text(encoding="utf-8-sig")

    for relative, quotes in QUOTES.items():
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        for quote in quotes:
            assert normalized(quote) in normalized(source_text), f"source quote changed: {relative}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_term = [
        row for row in statements
        if row.get("subject_candidate_id") == SPANISH_CAUSE_CANDIDATE
        or row.get("object_candidate_id") == SPANISH_CAUSE_CANDIDATE
    ]
    relation_candidates = [
        row for row in direct_term
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row["statement_id"] for row in relation_candidates} == RELATION_STATEMENTS
    direct_rome = [
        row for row in statements
        if (row.get("subject_candidate_id") == ROME_CANDIDATE or row.get("object_candidate_id") == ROME_CANDIDATE)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert len(direct_rome) == 7

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id[ROME_CANDIDATE]["decision"] = "same"
    planned_by_id[ROME_CANDIDATE]["ku_id"] = ROME_KU
    planned_by_id[ROME_CANDIDATE]["process_ref"] = "S3-review-rome-place-2026-10-17"
    planned_by_id[ROME_CANDIDATE]["resolution_note"] += (
        " S3复核（2026-10-17）：原 new 组撤回；改判 same → units/places/rome。候选 canonical name 虽以第6章 p.161 的"
        "Altieri fresco/Cortona 语境标记，同组核心指称均为 Rome 城市。唯一“countryside around Rome”提及只作城外农业语境，"
        "不并入 Rome 城市范围，也不在此新增无专名乡野端点；七条直接关系候选中的 Rome 均指城市或前往该城。"
        "旧组号与旧判断保留，本行不进入 S4 新组。"
    )
    planned_by_id[SPANISH_CAUSE_CANDIDATE]["process_ref"] = "S3-review-spanish-cause-2026-10-17"
    planned_by_id[SPANISH_CAUSE_CANDIDATE]["resolution_note"] += (
        " S3复核（2026-10-17）：维持 new，单成员组 sg3-term-cand-4404。第2、5、7章的 Spanish cause、"
        "partisan 与 devoted 等表述指向同一书内政治倾向概念。它与既有塞尔奎齐赞助人 Spanish sphere 术语"
        "有交集但身份范围不同：既有 term 是一组赞助人的来源局部语境，本候选覆盖跨章政治倾向称谓；"
        "两者均不推定正式组织。未发现精确同类既有 KU。"
    )
    planned_by_id[SPANISH_CAUSE_CANDIDATE]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_by_id[SPANISH_CAUSE_CANDIDATE]["ku_id"] = KU_ID

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
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    next_process = next_process.rstrip() + (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S3/S4 place、term：Rome 端点复用与 Spanish cause 跨章登记（{DATE}）\n\n"
        f"- S3 将 {ROME_CANDIDATE} 从原 new 组改为 same → {ROME_KU}。"
        "该候选的来源锚点以第6章 p.161 的叙述语境命名，同组核心指称均为 Rome 城市；"
        "唯一“countryside around Rome”提及保留为城外农业语境，不并入城市范围或另造无专名端点。"
        "七条直接关系候选中的 Rome 均指城市或前往该城。现有 Rome place KU 可复用，候选旧组号与旧判断保留在对齐行中。\n"
        f"- {SPANISH_CAUSE_CANDIDATE} 保持 new，单成员 term 组 {GROUP}，登记为"
        f"[{NAME_ZH}（{NAME_EN}）](../../../{CARD_REL})（{KU_ID}）。"
        "第2章 p.35、第5章 p.137、第7章 p.173 对 Ginnasi、Raggi、Carandini 与 Crescenzi 兄弟的表述"
        "支持同一书内政治倾向概念。它与既有 Cerquozzi patrons/Spanish sphere term 有交集但不等同；"
        "本组记录跨章的 cause/alignment 称谓，不把它当作正式组织。\n"
        f"- 六条直接 S2 关系候选为{', '.join(sorted(RELATION_STATEMENTS))}，留待 S6；"
        "Rome 候选关联的七条 S2 关系端点也可映射至现有 Rome KU，但本次均未写入 relations.csv。"
        "未新增 enrichment.jsonl 事实。\n"
        f"- S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    ) + "\n"
    next_result = next_result.rstrip() + (
        f"\n\n### S3/S4 place、term：Rome 端点复用与 Spanish cause 跨章登记（{DATE}）\n\n"
        f"{ROME_CANDIDATE} 改判 same → {ROME_KU}，原 new 组撤回；"
        f"{SPANISH_CAUSE_CANDIDATE} 维持 new 并登记至[{NAME_ZH}（{NAME_EN}）]"
        "(../units/terms/spanish-cause-in-rome-haskell-account.md)。"
        "六条直接关系候选仍待 S6；另有七条 Rome 端点映射至既有城市 KU，本次没有新增正式关系或补足事实。"
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
            f"dry-run passed: {ROME_CANDIDATE} same->{ROME_KU}; {GROUP}->{KU_ID}; "
            f"direct_term_relations={len(relation_candidates)}; same={totals['same_candidates']}; "
            f"new={totals['new_candidates']}/{totals['new_groups']}; "
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
        f"applied: {ROME_CANDIDATE} same->{ROME_KU}; {GROUP}->{KU_ID}; "
        f"direct_term_relations={len(relation_candidates)}; same={totals['same_candidates']}; "
        f"new={totals['new_candidates']}/{totals['new_groups']}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
