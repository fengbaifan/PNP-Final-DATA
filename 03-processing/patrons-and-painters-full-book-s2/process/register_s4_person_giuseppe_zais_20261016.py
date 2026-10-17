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
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"

CANDIDATE = "cand-2830"
GROUP = "new-person:giuseppe-zais-1e534535f3"
KU_ID = "units/persons/giuseppe-zais"
CARD_REL = "04-knowledge/units/persons/giuseppe-zais.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "朱塞佩·扎伊斯"
NAME_EN = "Giuseppe Zais"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-giuseppe-zais-20261016"

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "location": "第9章 p.261；OCR L212–216",
        "span": "lines 212–216; print p. 261",
        "summary": "第9章以 Giuseppe Zais 全名介绍一位热那亚画家。",
        "quotes": (("line 214", "the landscape painter Giuseppe Zais"),),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章 p.328；OCR L243–245",
        "span": "lines 243–245; print p. 328",
        "summary": "第10章以完整姓名谈论其在威尼斯风景画中的位置。",
        "quotes": (("line 244", "Giuseppe Zais, a more authentic and robust interpreter of the countryside"),),
    },
    {
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix_intro.md",
        "location": "附录5 p.393；OCR L139–142",
        "span": "lines 139–142; print p. 393",
        "summary": (
            "附录5再次写出 Giuseppe Zais，并提出相关绘画活动开始于1762年前还是之后尚无法确定。"
        ),
        "quotes": (
            (
                "lines 139–141",
                "Giuseppe Zais, who worked for Smith and whose pictures are not among those sold to George III. But is this because the artist was unknown in England and therefore not selected by the royal agent, or did Zais only begin to work for Smith after 1762?",
            ),
        ),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "location": "全书索引 UVWXYZ.csv#167",
        "span": "UVWXYZ.csv#167",
        "summary": "索引以 Zais, Giuseppe 列出人物并提供跨章定位。",
        "quotes": (("UVWXYZ.csv#167", "Zais, Giuseppe"),),
    },
)


def source_row(item: dict) -> dict:
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
    ch9 = "[第9章 p.261](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L212–216）"
    ch10 = "[第10章 p.328](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L243–245）"
    appendix = "[附录5 p.393](../../../02-sources/02-Markdown/19_CHP-19Appendix_intro.md)（L139–142）"
    index = "[全书索引 UVWXYZ.csv#167](../../../02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Zais, Giuseppe” 列出人物。第9章 p.261 称其为风景画家；第10章 p.328 再次以完整姓名提及他。附录5 p.393 也出现完整姓名，但对相关绘画活动是否始于1762年前后提出未决问题。本卡保留原文的年代不确定性，不将该问题改写为已确定的委托、所有权或交易事实。中文名为项目工作译名。{ch9} {ch10} {appendix} {index}

**English:** The book’s index lists “Zais, Giuseppe.” Chapter 9 p. 261 calls him a landscape painter, and Chapter 10 p. 328 again uses his full name. Appendix 5 p. 393 also names him but leaves open whether the relevant painting activity began before or after 1762. This card preserves the source’s chronological uncertainty and does not turn the question into a settled commission, ownership, or sale fact. The Chinese name is a project working transliteration. {ch9} {ch10} {appendix} {index}

### 名称与书内身份

- **索引姓名：** Zais, Giuseppe；正文多处写作 Giuseppe Zais 或 Zais。中文标题采用项目工作译名。{index} {ch9} {ch10}
- **年代限定：** 附录5 对其绘画活动与1762年交易的时间关系提出问题，未给出定论；本卡不替原文消解该不确定性。{appendix}

## 关系与证据

当前没有登记正式关系。涉及该人物的 16 条 S2 关系候选留待 S6 逐条审查；附录所载问题与其他正文关系候选仍按各自证据范围裁决。{ch9} {ch10} {appendix}
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


def contains_candidate(value, candidate_id: str) -> bool:
    if isinstance(value, dict):
        return any(contains_candidate(item, candidate_id) for item in value.values())
    if isinstance(value, list):
        return any(contains_candidate(item, candidate_id) for item in value)
    return value == candidate_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Giuseppe Zais's source-backed person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate = candidate_by_id[CANDIDATE]
    target = next(
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Zais, Giuseppe"
    assert candidate.get("index_entry_id") == "UVWXYZ.csv#167"
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and "zais" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in SOURCES:
        normalized = " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["source_file"], quote)
    _, index_rows = sync.read_csv(ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "UVWXYZ.csv")
    index_row = index_rows[int(candidate["index_entry_id"].split("#")[1])]
    assert index_row["Main Entry"] == candidate["canonical_name"]

    statements_path = TABLES / "book-statements.jsonl"
    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [row for row in statements if contains_candidate(row, CANDIDATE)]
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in related)
    assert len(related) == 25, f"unexpected statement count involving Zais: {len(related)}"
    assert relation_count == 16, f"unexpected relation-candidate count involving Zais: {relation_count}"

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
    assert totals["registered_groups"] == 276 and totals["registered_members"] == 346, totals
    assert totals["pending_groups"] == 4558 and totals["pending_members"] == 4660, totals
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[朱塞佩·扎伊斯人物卡]"
        "(../units/persons/giuseppe-zais.md)，16条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S4 person：Giuseppe Zais 跨章身份组登记（2026-10-16）"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 人物身份组只含一个候选。索引 UVWXYZ.csv#167 与第9章 p.261、第10章 p.328、"
        "附录5 p.393 的正文全名相互印证。附录5 对相关绘画活动与1762年交易的时间关系提出问题但未定论，卡片保留此边界；未发现同身份既有 KU，"
        "中文名为项目工作译名，未使用外部身份源。\n"
        f"- 涉及该人物的25条 S2 陈述中16条为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_accepted = insert_accepted(accepted)

    target_files = [ALIGNMENT, MANIFEST, ACCEPTED, KNOWLEDGE, RESULT]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in target_files)
    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members=1; source_records={len(SOURCES)}; "
            f"related_statements={len(related)}; relation_candidates_pending={relation_count}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    write_targets = {
        ALIGNMENT: None,
        MANIFEST: None,
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        RESULT: next_result,
    }
    for path in write_targets:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    sync.write_csv(MANIFEST, manifest_fields, planned_manifest)
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
