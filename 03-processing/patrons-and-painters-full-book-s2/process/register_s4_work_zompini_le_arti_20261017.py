from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-work-zompini-le-arti-20261017"
GROUP = "workgrp-4dad04ca7f0e40"
CANDIDATES = ("cand-2876", "cand-10111")
KU_ID = "units/works/le-arti-che-vanno-per-via-nella-citta-di-venezia"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "《威尼斯街头的各行各业》"
NAME_EN = "Street Trades of Venice"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv"
CHP13_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
CHP16_FILE = "02-sources/02-Markdown/16_CHP-16_intro.md"
QUOTES = {
    "index_title": "Le Arti che vanno per via nella Città di Venezia",
    "creation": "in 1753 he made the drawings for his masterpiece",
    "assessment": "the most serious attempt of any Venetian artist to break new ground in his subject-matter and a genuinely moving and convincing survey of the life of the tradesmen and the poor",
    "edition_plan": "He planned to bring out an edition of Zompini’s Le Arti che vanno per le vie nella citta di Venezia;",
}
CREATION_RELATION = "st-chp13-p344-zompini-drew_for_le_arti_1753"
ASSESSMENT_STATEMENT = "st-chp13-p344-haskell-le_arti_assessment"
EDITION_PLAN_RELATION = "st-chp16-p374-strange-zompini-publication-plan"


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, index, s.v. Zompini, Gaetano.",
            "location": "书后索引，UVWXYZ.csv#213；索引页码344、374。",
            "sentence_summary": "索引以 Zompini 为主项，将 Le Arti che vanno per via nella Città di Venezia 列为子目并指向第13、16章。",
            "original_quotes": [
                {"source_span": "UVWXYZ.csv#213", "text": "Le Arti che vanno per via nella Città di Venezia"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters-index",
                "source_file": INDEX_FILE,
                "source_span": "UVWXYZ.csv#213",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 13, p. 344.",
            "location": "第13章，印刷页344；OCR L120。",
            "sentence_summary": "哈斯克尔称 Zompini 于1753年为该作品作图稿，并将其评价为开拓题材、描绘威尼斯商贩与贫民生活的重要作品。评价语属于作者判断。",
            "original_quotes": [
                {"source_span": "line 120; print p. 344", "text": QUOTES["creation"]},
                {"source_span": "line 120; print p. 344", "text": QUOTES["assessment"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP13_FILE,
                "source_span": "line 120; print p. 344",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 16, p. 374.",
            "location": "第16章，印刷页374；OCR L18。",
            "sentence_summary": "哈斯克尔称 John Strange 曾计划出版该作品的一个版本；此处只支持计划，不支持版本已完成或实际出版。",
            "original_quotes": [
                {"source_span": "line 18; print p. 374", "text": QUOTES["edition_plan"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP16_FILE,
                "source_span": "line 18; print p. 374",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 题名

- 索引题名：Le Arti che vanno per via nella Città di Venezia。[S1]
- 中文描述性译题：《威尼斯街头的各行各业》；英文描述性译题：Street Trades of Venice。均为工作译名，不声称是原作的官方译名。
- 第16章将题名写作 Le Arti che vanno per le vie nella citta di Venezia；本卡按 S3 跨章身份组视为同一作品题名变体，不另建作品。[S1, S3]

### 作品信息

**中文：** 哈斯克尔称 Gaetano Zompini 于1753年为 Le Arti 作图稿，并将作品描述为对威尼斯商贩与贫民生活的呈现。这里的评价是哈斯克尔的判断。第16章提到 John Strange 曾计划推出该作品的一个版本，但没有说明计划是否实现。本卡记录作品身份与书内陈述，不推定具体版次、印数、媒介、技法、现藏地或存世状态。[S2, S3]

**English:** Haskell says that Gaetano Zompini made the drawings for Le Arti in 1753 and describes the work as a survey of the lives of tradesmen and the poor in Venice; that evaluation is Haskell’s. Chapter 16 says that John Strange planned to bring out an edition, without stating whether the plan was completed. This card records the work identity and the book’s statements; it does not infer a specific edition, print run, medium, technique, present location, or survival status. [S2, S3]

## 关系与证据

当前没有正式关系。下列 S2 关系候选留待 S6 按端点、角色和证据审查：

- {CREATION_RELATION}：Zompini 为该作品作图稿，书中将时间标为1753年。
- {EDITION_PLAN_RELATION}：John Strange 计划推出该作品的一个版本；不等同于确认其出版。

### 来源

- S1：书后索引 UVWXYZ.csv#213，指向印刷页344、374。
- S2：第13章 p. 344；`{ASSESSMENT_STATEMENT}` 是作者评价，不是关系。
- S3：第16章 p. 374；记录出版计划，不据此确认版本完成。
"""


def insert_accepted_path(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
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
    parser = argparse.ArgumentParser(description="Register the Le Arti work group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert all(candidate_map[cid].get("suggested_type") == "work" for cid in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)
    for cid in CANDIDATES:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert decisions["cand-2874"].get("decision") == "new"
    assert decisions["cand-2874"].get("ku_id") == "units/persons/gaetano-zompini"
    assert decisions["cand-2517"].get("decision") == "same"
    assert decisions["cand-2517"].get("ku_id") == "units/persons/john-strange"
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "work" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English title already exists in manifest"

    source_texts = {
        INDEX_FILE: (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig"),
        CHP13_FILE: (ROOT / CHP13_FILE).read_text(encoding="utf-8-sig"),
        CHP16_FILE: (ROOT / CHP16_FILE).read_text(encoding="utf-8-sig"),
    }
    assert QUOTES["index_title"] in source_texts[INDEX_FILE]
    assert all(quote in source_texts[CHP13_FILE] for quote in (QUOTES["creation"], QUOTES["assessment"]))
    assert QUOTES["edition_plan"] in source_texts[CHP16_FILE]
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    creation = statements[CREATION_RELATION]
    assert creation.get("subject_candidate_id") == "cand-2874"
    assert creation.get("object_candidate_id") == "cand-10111"
    assert creation["qualifiers"].get("relation_candidate") is True
    assessment = statements[ASSESSMENT_STATEMENT]
    assert assessment.get("subject_candidate_id") == "cand-10111"
    assert assessment["qualifiers"].get("relation_candidate") is False
    plan = statements[EDITION_PLAN_RELATION]
    assert plan.get("subject_candidate_id") == "cand-2517"
    assert plan.get("object_candidate_id") == "cand-2876"
    assert plan["qualifiers"].get("relation_candidate") is True

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: cross-chapter work identity group {GROUP} maps to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S4 work：Zompini《Le Arti》跨章作品组登记（{DATE}）

既有 S3 组 {GROUP} 包含索引候选 `cand-2876`（UVWXYZ.csv#213；页344、374）与第13章正文候选 `cand-10111`，两者均为 `new`，统一映射至[《威尼斯街头的各行各业》作品卡](../../../04-knowledge/units/works/le-arti-che-vanno-per-via-nella-citta-di-venezia.md)。第13章 p.344 称 Gaetano Zompini 于1753年为该作品作图稿，并对题材和内容作评价；第16章 p.374 记 John Strange 曾计划推出一个版本，但不证明出版计划落实。姓名端点已有去向：Zompini 为 `same/new` 决定所指向的 `units/persons/gaetano-zompini`，Strange 指向 `units/persons/john-strange`。

作品卡保留索引题名与第16章题名变体，中文及英文仅作描述性工作译名；没有推定媒介、版次、印数、收藏或存世情况。`{CREATION_RELATION}` 和 `{EDITION_PLAN_RELATION}` 作为 S2 关系候选留待 S6；`{ASSESSMENT_STATEMENT}` 保留为 Haskell 的评价性陈述，不登记为关系。本次未修改 `relations.csv`，未新增 S5 enrichment。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 work：Zompini《Le Arti》作品组（{DATE}）\n\n"
        "跨章索引与正文候选映射至一张 work KU；1753年作图稿和后来计划推出版本分别按原文限定记录，关系候选留待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {', '.join(CANDIDATES)} are the complete two-member S3 group {GROUP}")
        print("verified source title, 1753 drawings, later edition plan, and already registered person endpoints")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv and enrichment.jsonl unchanged")
        print("planned writes: one bilingual work card, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Le Arti work group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
