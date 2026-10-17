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

CANDIDATE = "cand-1739"
GROUP = "new-person:isaac-newton-800ef74820"
KU_ID = "units/persons/isaac-newton"
CARD_REL = "04-knowledge/units/persons/isaac-newton.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "艾萨克·牛顿"
NAME_EN = "Sir Isaac Newton"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-isaac-newton-20261016"

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章 p.301；OCR L259–260",
        "span": "lines 259–260; print p. 301",
        "summary": "第10章在讨论一组纪念图像的出版情况时明确写出 Sir Isaac Newton。",
        "quotes": (("lines 259–260", "Lord Dorset and Sir Isaac Newton—were given Characters"),),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章 pp.318–320；OCR L142–149",
        "span": "lines 142–149; print pp. 318–320",
        "summary": "同章后段多次以 Newton 指称人物，并讨论其哲学及光学思想。",
        "quotes": (("line 149; print p. 319", "Newton’s optical discoveries"),),
    },
    {
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "location": "第20章后记 p.408；OCR L178–179",
        "span": "lines 178–179; print p. 408",
        "summary": "后记再次写出 Sir Isaac Newton，并回顾相关光学理论语境。",
        "quotes": (("line 178", "the theories of Sir Isaac Newton"),),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/N.csv",
        "location": "全书索引 N.csv#19",
        "span": "N.csv#19",
        "summary": "索引主项列为 Newton, Sir Isaac，跨章定位至第10章 pp.288、301、318–320及后记 p.408。",
        "quotes": (("N.csv#19", "Newton, Sir Isaac"),),
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
    monument = "[第10章 p.301](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L259–260）"
    philosophy = "[第10章 pp.318–320](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L142–149）"
    postscript = "[第20章后记 p.408](../../../02-sources/02-Markdown/20_CHP-20Postscript.md)（L178–179）"
    index = "[全书索引 N.csv#19](../../../02-sources/03-Index/03-2-Index-CSV/N.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Newton, Sir Isaac” 列出人物，定位跨越第10章与后记。第10章 p.301 明确写出 Sir Isaac Newton；同章 pp.318–320 继续以 Newton 讨论哲学和光学思想。第20章后记再次写出 Sir Isaac Newton。本卡将同一索引主项下的正文提及归入一张人物卡，不将 S2 关系候选直接转成正式关系。{monument} {philosophy} {postscript} {index}

**English:** The book’s index lists “Newton, Sir Isaac” and points to passages across Chapter 10 and the postscript. Chapter 10 p. 301 explicitly names Sir Isaac Newton; pp. 318–320 of the same chapter continue to discuss Newton in the context of philosophical and optical ideas. The postscript again names Sir Isaac Newton. This card groups the body references under the same indexed person and does not turn S2 relation candidates directly into formal relations. {monument} {philosophy} {postscript} {index}

### 名称与书内身份

- **索引姓名：** Newton, Sir Isaac；正文写作 Sir Isaac Newton 或 Newton。中文标题采用“艾萨克·牛顿”。{index} {monument} {postscript}
- **跨章锚点：** 第10章不同段落和第20章后记均有相互吻合的正文姓名，索引页码覆盖相应章节；按同一人物候选组登记。{index} {monument} {philosophy} {postscript}

## 关系与证据

当前没有登记正式关系。涉及该人物的 24 条 S2 关系候选留待 S6 逐条审查；人物在思想、交往或纪念图像语境中的出现不在本阶段转为正式关系。{monument} {philosophy} {postscript}
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
    parser = argparse.ArgumentParser(description="Register Sir Isaac Newton's person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    target = next(
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    candidate = candidate_by_id[CANDIDATE]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Newton, Sir Isaac"
    assert candidate.get("index_entry_id") == "N.csv#19"
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
        and "newton" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in SOURCES:
        source_path = ROOT / item["source_file"]
        normalized = " ".join(source_path.read_text(encoding="utf-8-sig").split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["source_file"], quote)
    _, index_rows = sync.read_csv(ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "N.csv")
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
    assert len(related) == 31, f"unexpected statement count involving Newton: {len(related)}"
    assert relation_count == 24, f"unexpected relation-candidate count involving Newton: {relation_count}"

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
    assert totals["registered_groups"] == 271 and totals["registered_members"] == 340, totals
    assert totals["pending_groups"] == 4564 and totals["pending_members"] == 4668, totals
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[艾萨克·牛顿人物卡]"
        "(../units/persons/isaac-newton.md)，24条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S4 person：Sir Isaac Newton 跨章身份组登记（2026-10-16）"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 人物身份组只含一个候选。索引 N.csv#19 跨章定位第10章 pp.288、301、318–320 "
        "及第20章后记 p.408；第10章 p.301 和后记 p.408 明确写出 Sir Isaac Newton，第10章 pp.318–320 继续以 Newton 讨论哲学、光学语境。"
        "候选全名与索引、正文锚点一致；未发现既有同身份人物 KU，未使用外部身份源。\n"
        f"- 涉及该人物的31条 S2 陈述中24条为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。\n\n"
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
