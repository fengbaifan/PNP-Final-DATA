from __future__ import annotations

import argparse
import csv
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
GROUP = "new-person:philip-skippon-3ee8383fd8"
MEMBERS = ("cand-2438",)
KU_ID = "units/persons/philip-skippon"
CARD_REL = "04-knowledge/units/persons/philip-skippon.md"
NAME_ZH = "菲利普·斯基彭"
NAME_EN = "Philip Skippon"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/S.csv"
SOURCE_P104 = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
SOURCE_INTRO = "02-sources/02-Markdown/04_CHP-4_intro.md"
SOURCE_P160 = "02-sources/02-Markdown/06_CHP-6_sec_iv.md"
PROCESS_ANCHOR = "s4-person-philip-skippon-crosschapter-20261017"
INDEX_DATA_ROW = 127
INDEX_ENTRY = "Skippon, Philip"
RELATION_IDS = (
    "st-chp4-sec-ii-p104-footnote3-skippon-noted-bird-paintings",
    "st-chp4-sec-ii-p104-footnote3-skippon-shown-collection",
)
DIRECT_IDS = RELATION_IDS + ("st-chp4-intro-notes-01-bertolotti-skippon-assessment",)
QUOTE_INTRO = "1 Bertolotti, 1886, who has, however, missed the reference to him in Skippon, p. 650."
QUOTE_P104 = (
    "When Skippon was taken round the collection in 1663 (p. 679) by Cassiano’s nephew "
    "he noted a large number of bird paintings, but he failed to record whether or not "
    "they were by Poussin, the ‘old French painter’, who, he was told, was still living in Rome."
)
QUOTE_P160 = "3 Skippon, p. 676, and Misson, 1717, II, p. 167."


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def sources():
    return [
        {
            "citation": "Haskell, *Patrons and Painters*, full-book index.",
            "location": "S.csv#127（零基数据行索引；文件物理行129）。",
            "sentence_summary": "全书索引以倒置姓名形式列出 Philip Skippon，标注本书印刷页104注。",
            "original_quotes": [
                {"source_span": "S.csv#127; physical line 129", "text": '"Skippon, Philip",,,,"104n"'}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters-index",
                "source_file": INDEX_FILE,
                "source_span": "S.csv#127; physical line 129",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第4章导言注1；Markdown L11；PDF物理页1。",
            "sentence_summary": (
                "Haskell称Bertolotti未提及Skippon p.650中对某人的引用；紧邻正文表明代词him指Jacopo Ghibbesio。"
                "这是书目比较，不是关于Skippon的历史关系或生平断言。"
            ),
            "original_quotes": [{"source_span": "line 11; chapter 4 introduction, note 1", "text": QUOTE_INTRO}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_INTRO,
                "source_span": "line 11; chapter 4 introduction, note 1; PDF physical p. 1",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第4章，印刷页104注3；Markdown L254；PDF物理页11。",
            "sentence_summary": (
                "Haskell称Skippon于1663年由Cassiano未具名的侄子带看藏品，并记录其见到许多鸟类绘画；"
                "他没有判断这些画是否出自Poussin，也没有指认单件作品。"
            ),
            "original_quotes": [{"source_span": "line 254; print p. 104, note 3", "text": QUOTE_P104}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_P104,
                "source_span": "line 254; print p. 104, note 3; PDF physical p. 11",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第6章，印刷页160注3；Markdown L68；PDF物理页10。",
            "sentence_summary": (
                "Haskell在相关注释中引用Skippon p.676与Misson 1717年第二卷p.167；"
                "两项被引文献均未在本次登记中独立查阅。"
            ),
            "original_quotes": [{"source_span": "line 68; print p. 160, note 3", "text": QUOTE_P160}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_P160,
                "source_span": "line 68; print p. 160, note 3; PDF physical p. 10",
            },
        },
    ]


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    index_ref = f"[全书索引 S.csv#127](../../../{INDEX_FILE})"
    intro_ref = f"[第4章导言注1](../../../{SOURCE_INTRO})（L11）"
    p104 = f"[第4章 p.104 注3](../../../{SOURCE_P104})（L254）"
    p160 = f"[第6章 p.160 注3](../../../{SOURCE_P160})（L68）"
    relation_list = "\n".join(f"- {statement_id}" for statement_id in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记全书索引以 Philip Skippon 列出的书内人物，中文名采用项目工作音译。第4章 p.104 注3称 Skippon 于1663年由 Cassiano 未具名的侄子带看藏品，并记其注意到许多鸟类绘画；Haskell明确说 Skippon 没有记录这些画是否由 Poussin 创作。该段没有指认单件绘画。第4章导言及第6章注释另有对 Skippon 不同页码的书目引用；这只记录 Haskell 的引用情况，不视为独立阅读 Skippon 著作。本卡不补外部生平或人物核验。{index_ref}；{p104}；{intro_ref}；{p160}

**English:** This card records the person listed as Philip Skippon in the book’s index; the Chinese name is a project transliteration. Chapter 4, note 3, says that Cassiano’s unnamed nephew took Skippon round the collection in 1663 and that Skippon noted many bird paintings. Haskell explicitly says that Skippon did not record whether the paintings were by Poussin; the passage identifies no individual painting. The chapter 4 introduction and a chapter 6 note also cite different pages by Skippon. These are Haskell’s references and do not indicate that Skippon’s works were independently consulted. This card adds no external biography or identity verification. {index_ref}; {p104}; {intro_ref}; {p160}

### 姓名与身份范围

- **索引全名：** Philip Skippon；索引标注第4章印刷页104注。{index_ref}
- **中文工作音译：** {NAME_ZH}，仅作项目展示名，不作为原语姓名或独立身份依据。
- **身份范围：** 本卡对应 cand-2438 的单一 S3 new 人物组；跨章索引与第4章、第6章的书内提及按同一全名组登记。

### 本书相关内容

- 第4章 p.104 注3称，Skippon 于1663年被 Cassiano 未具名的侄子带看藏品，记录了许多鸟类绘画；他没有判断这些画是否为 Poussin 所作，不能据此添加具体作品或作者归属。{p104}
- 第4章导言注1称 Bertolotti 漏掉了 Skippon p.650 中对 Ghibbesio 的引用；此句中的 him 指 Jacopo Ghibbesio，不表达 Skippon 与 Ghibbesio 的历史关系。{intro_ref}
- 第6章 p.160 注3另引 Skippon p.676；这项书目线索不代表已阅读被引文献。{p160}

## 关系与证据

当前没有正式关系记录。下列两条直接 S2 关系候选留待 S6 核对端点、方向、语境和证据：

{relation_list}

Cassiano 的侄子仍未具名；鸟类绘画未逐件识别，Poussin 归属未获该段确认。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Philip Skippon's cross-chapter S4 person group")
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
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert set(MEMBERS) <= set(candidate_by_id)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "person"
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")

    with (ROOT / INDEX_FILE).open(encoding="utf-8-sig", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    assert index_rows[INDEX_DATA_ROW].get("Main Entry") == INDEX_ENTRY
    assert index_rows[INDEX_DATA_ROW].get("Page Numbers") == "104n"

    card_path = ROOT / CARD_REL
    registered = [
        row for row in manifest
        if row.get("ku_id") == KU_ID and row.get("card_path") == CARD_REL
    ]
    if (
        registered and card_path.exists() and CARD_REL in accepted
        and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS)
    ):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 2 relation candidates remain pending S6.")
        return 0
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and NAME_EN.casefold() == (row.get("name_en") or "").casefold()
        for row in manifest
    )

    for relative, quote in (
        (SOURCE_INTRO, QUOTE_INTRO),
        (SOURCE_P104, QUOTE_P104),
        (SOURCE_P160, QUOTE_P160),
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
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [
        row for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row.get("statement_id") for row in direct} == set(DIRECT_IDS)
    assert {row.get("statement_id") for row in relations} == set(RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration: mapped {GROUP} to {KU_ID}; "
            "index name and chapter 4/6 references retained; no external identity verification."
        )
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
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated person card frontmatter is invalid"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S4 person：Philip Skippon 跨章身份组登记（{DATE}）\n\n"
        f"- cand-2438 保持 S3 new 组 {GROUP}，映射至[{NAME_ZH}（{NAME_EN}）人物卡](../../../{CARD_REL})（{KU_ID}）。"
        "索引 S.csv#127 给出倒置全名与 p.104 注定位；第4章 p.104、第6章 p.160及第4章导言的提及均保留原书语境，未作外部人物核验。\n"
        "- 第4章 p.104 注3称 Skippon 于1663年由 Cassiano 未具名的侄子带看藏品，记有许多鸟类绘画；"
        "Haskell明确说他未记录这些画是否为 Poussin，且未指认单件作品。导言注1的 him 指 Ghibbesio，不构成 Skippon 的历史关系。\n"
        f"- 两条直接关系候选（{', '.join(RELATION_IDS)}）留待 S6；未具名侄子、单件绘画身份及 Poussin 归属均保持未决。本批未登记正式关系或外部身份核验。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"
    next_result += (
        f"\n\n### person：Philip Skippon 跨章身份组 S4 登记（{DATE}）\n\n"
        f"cand-2438 登记至[人物卡](../units/persons/philip-skippon.md)。索引全名、1663年藏品记录与第4章及第6章的引用作为同一书内人物组；"
        "两条直接关系候选待 S6。鸟类绘画未逐件识别，Poussin 归属不确定，Cassiano 的侄子未具名。\n\n"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; sources=4; direct_statements={len(direct)}; "
            f"relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; no files changed"
        )
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
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
        f"applied: {GROUP} -> {KU_ID}; relation_candidates_pending={len(relations)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
