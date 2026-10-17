from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"

CANDIDATE = "cand-1141"
GROUP = "new-person:england-george-iii-of-0d549c6e37"
KU_ID = "units/persons/george-iii"
CARD_REL = "04-knowledge/units/persons/george-iii.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "乔治三世"
NAME_EN = "George III, King of England"
SOURCE_CH10 = "02-sources/02-Markdown/10_CHP-10_intro.md"
SOURCE_CH15 = "02-sources/02-Markdown/15_CHP-15_sec_i.md"
SOURCE_APP5 = "02-sources/02-Markdown/19_CHP-19Appendix.md"
SOURCE_POSTSCRIPT = "02-sources/02-Markdown/20_CHP-20Postscript.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/G.csv"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-george-iii-20261016"

SOURCES = (
    {
        "source_file": SOURCE_CH10,
        "location": "第10章导言，印刷页300、310；OCR L369、488",
        "span": "lines 369, 488; print pp. 300, 310; PDF physical pp. 51, 61",
        "summary": (
            "Haskell 称 Consul Smith 于1762年将图书及多数绘画售予 King George III；"
            "后文又记其经艰难谈判售出多数精品画作、书籍、素描和宝石。"
        ),
        "quotes": (
            (
                "line 369; print p. 300",
                "In 1762, a year after resigning the consulship, he sold the bulk of his library and most of his pictures to King George III.",
            ),
            (
                "line 488; print p. 310",
                "in 1762, after difficult negotiations he at last managed to sell most of his best pictures, books, drawings and gems to King George III.",
            ),
        ),
    },
    {
        "source_file": SOURCE_CH15,
        "location": "第15章，印刷页361；OCR L11",
        "span": "line 11; print p. 361; PDF physical p. 3",
        "summary": "第15章回顾 Venetian collections 的流散，称 Smith 最好的绘画于1762年由 George III 获得。",
        "quotes": (
            ("line 11", "Smith’s best paintings had been acquired for George III in 1762"),
        ),
    },
    {
        "source_file": SOURCE_APP5,
        "location": "附录5，印刷页391–393；OCR L117–120、149",
        "span": "lines 117–120, 149; print pp. 391–393; PDF physical pp. 7–9",
        "summary": (
            "Haskell 确认1762年 Smith 将大量绘画与素描售予 George III，"
            "但将售出全部收藏还是部分选择作为未决问题；他明确说证据不能得出最终结论。"
        ),
        "quotes": (
            (
                "line 117",
                "in 1762 Smith sold to George III a very large number of paintings and drawings which still form one of the chief glories of the Royal Collection.",
            ),
            (
                "lines 119–120",
                "Two alternatives face us. Did Smith in 1762 sell only a selection of his pictures to the King, and keep the remainder for himself and perhaps go on adding to his collection? Or did he, in fact, sell everything to the King and purchase all these several hundred pictures between 1762 and 1770?",
            ),
            (
                "line 149",
                "This is the thoroughly confusing evidence. From it no final conclusion is possible, but I strongly believe that in 1762 Smith only sold part of his collections to the King",
            ),
        ),
    },
    {
        "source_file": SOURCE_POSTSCRIPT,
        "location": "第20章后记，印刷页406；OCR L160–162",
        "span": "lines 160–162; print p. 406; PDF physical p. 10",
        "summary": "后记称 Frances Vivian 未能解决 Smith 的“第二批收藏”问题，并倾向于认为1762年只售出一部分。",
        "quotes": (
            (
                "lines 160–162",
                "Like me, however, she is inclined to believe that in 1762 he sold only a portion of what he then owned",
            ),
        ),
    },
    {
        "source_file": INDEX_FILE,
        "location": "全书索引，G.csv#48；索引页码292、300、303、309、361、393、406",
        "span": "G.csv#48; indexed pages 292, 300, 303, 309, 361, 393, 406",
        "summary": "索引将人物列作 George III, King of England，并列出跨章定位页码。",
        "quotes": (("G.csv#48", "George III, King of England"),),
    },
)


def source_row(item: dict):
    return {
        "citation": BOOK_CITATION,
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [
            {"source_span": span, "text": quote}
            for span, quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["source_file"],
            "source_span": item["span"],
        },
    }


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [source_row(item) for item in SOURCES],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch10 = "[第10章 pp.300、310](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L369、488）"
    ch15 = "[第15章 p.361](../../../02-sources/02-Markdown/15_CHP-15_sec_i.md)（L11）"
    app5 = "[附录5 pp.391–393](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)（L117–120、149）"
    postscript = "[第20章后记 p.406](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L160–162）"
    index = "[全书索引 G.csv#48](../../../02-sources/03-Index/03-2-Index-CSV/G.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引将人物列为 “George III, King of England”。第10章称 Consul Smith 于1762年向 King George III 出售图书及多数绘画；第15章也记 Smith 最好的绘画于当年由 George III 获得。附录5明确提出售出全部收藏还是部分选择仍无法定论；本卡保留 Haskell 对该问题的限定，不将交易范围扩写为已确定事实。{ch10} {ch15} {app5} {postscript} {index}

**English:** The book’s index lists the person as “George III, King of England.” Chapter 10 says that Consul Smith sold books and most of his pictures to King George III in 1762; Chapter 15 likewise says Smith’s best paintings were acquired by George III that year. Appendix 5 states that the evidence cannot establish whether the whole collection or only a selection was sold. This card preserves Haskell’s qualification and does not present the scope of the transaction as settled. {ch10} {ch15} {app5} {postscript} {index}

### 名称与书内身份

- **索引姓名：** George III, King of England；正文亦写作 King George III 或 George III。中文显示名“乔治三世”为项目工作译名。{index} {ch10}
- **书内语境：** Haskell 在多章将 George III 置于 Consul Smith 的收藏与1762年交易叙述中；此处仅记录书中姓名和被提及的语境，不扩展生卒、王位年表或其他传记。{ch10} {ch15}
- **交易范围边界：** Haskell 对 Smith 是否售出全部收藏保留两种可能，并在附录中说无法作最终结论；本卡不将“多数”或“最佳作品”的叙述改写成全部收藏的确证。{app5} {postscript}

## 关系与证据

当前没有登记正式关系。涉及 George III 的 28 条 S2 关系候选保留待 S6 逐条裁决；Smith 与王室收藏的交易范围、作品端点和对应语境继续按原书记录的限定处理。{ch10} {ch15} {app5}
"""


def insert_accepted(accepted_text: str) -> str:
    lines = accepted_text.splitlines()
    assert CARD_REL not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register George III's cross-chapter person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert CANDIDATE in candidate_by_id
    candidate = candidate_by_id[CANDIDATE]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "George III, King of England"
    assert candidate.get("index_entry_id") == "G.csv#48"
    target = alignment_by_id[CANDIDATE]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and ("george iii" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold())
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    normalized_sources = {}
    for item in SOURCES:
        text = (ROOT / item["source_file"]).read_text(encoding="utf-8-sig")
        normalized_sources[item["source_file"]] = " ".join(text.split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized_sources[item["source_file"]], quote
    assert "George III, King of England" in normalized_sources[INDEX_FILE]

    statements_path = TABLES / "book-statements.jsonl"
    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    def contains_candidate(value) -> bool:
        if isinstance(value, dict):
            return any(contains_candidate(v) for v in value.values())
        if isinstance(value, list):
            return any(contains_candidate(v) for v in value)
        return value == CANDIDATE

    related = [row for row in statements if contains_candidate(row)]
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in related)
    assert len(related) == 41, f"unexpected statement count involving George III: {len(related)}"
    assert relation_count == 28, f"unexpected relation-candidate count involving George III: {relation_count}"

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[乔治三世人物卡]"
        f"(../units/persons/george-iii.md)，28条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"S4 person：George III {GROUP}" not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n### S4 person：George III 跨章身份组登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 组只含此候选。索引 G.csv#48 将人物列为 "
        "George III, King of England，指向第10章 pp.292、300、303、309，第15章 p.361，第19章附录5 "
        "p.393及第20章后记 p.406。正文 p.300、310及第15章明确写作 King George III / George III；"
        "第19章附录讨论 Smith 于1762年售出全部收藏还是部分选择，并明确表示无法得出最终结论。本卡保留该限定，"
        "不把交易范围写成已定事实；未使用外部身份源。\n"
        f"- 涉及该人物的41条 S2 陈述中28条为关系候选，均留待 S6；未登记正式关系或开展 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_accepted = insert_accepted(accepted)
    target_files = [
        TABLES / "alignment.csv", TABLES / "ku-manifest.csv",
        ACCEPTED, KNOWLEDGE, RESULT,
    ]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in target_files)

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members=1; identity_sources={len(SOURCES)}; "
            f"related_statements={len(related)}; relation_candidates_pending={relation_count}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    write_targets = {
        TABLES / "alignment.csv": None,
        TABLES / "ku-manifest.csv": None,
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        RESULT: next_result,
    }
    for path in write_targets:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    for path, content in write_targets.items():
        if content is not None:
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; relation_candidates_pending={relation_count}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; recovery_backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
