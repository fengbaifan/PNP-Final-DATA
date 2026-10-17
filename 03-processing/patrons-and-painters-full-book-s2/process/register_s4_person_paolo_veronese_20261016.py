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

CANDIDATE = "cand-2755"
GROUP = "new-person:paolo-veronese-4afb8ff702"
KU_ID = "units/persons/paolo-veronese"
CARD_REL = "04-knowledge/units/persons/paolo-veronese.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "保罗·委罗内塞"
NAME_EN = "Paolo Veronese"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-paolo-veronese-20261016"

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "location": "第5章 p.128；OCR L86–87",
        "span": "lines 85–87; print p. 128",
        "summary": "第5章以 Paolo Veronese 全名指称这位画家。",
        "quotes": (("lines 86–87", "the Paolo Veronese, the Parmigianino, the Carracci"),),
    },
    {
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章 p.216；OCR L31",
        "span": "line 31; print p. 216",
        "summary": "第8章以 Paolo Veronese 全名比较另一幅作品的画风。",
        "quotes": (("line 31", "a vigorous and efficient rehash of Paolo Veronese"),),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章 p.284；OCR L168",
        "span": "line 168; print p. 284",
        "summary": "第10章以 Veronese 姓氏指称其绘画范例，并称其影响威尼斯画家。",
        "quotes": (("line 168", "the example of Veronese"),),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "location": "全书索引 UVWXYZ.csv#91",
        "span": "UVWXYZ.csv#91",
        "summary": "索引以 Veronese, Paolo 列出人物并提供跨章定位。",
        "quotes": (("UVWXYZ.csv#91", "Veronese, Paolo"),),
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
    ch5 = "[第5章 p.128](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L85–87）"
    ch8 = "[第8章 p.216](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)（L31）"
    ch10 = "[第10章 p.284](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L168）"
    index = "[全书索引 UVWXYZ.csv#91](../../../02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Veronese, Paolo” 列为人物主项；正文第5章和第8章均直接写出 “Paolo Veronese”，第10章又以其姓氏指称绘画范例。相关正文定位跨越多个章节，与本轮 S3 人物候选的来源映射一致。本卡只归并书内同一人物身份，不将这些提及扩写成未经 S6 审查的正式关系。中文名采用项目常用译名。{ch5} {ch8} {ch10} {index}

**English:** The book’s index lists “Veronese, Paolo” as a person entry. Chapters 5 and 8 both name “Paolo Veronese” explicitly, and Chapter 10 later refers to a painting example by his surname. These body references span several chapters and match the source mapping of the current S3 person candidate. This card consolidates the book-local identity without expanding these mentions into formal relations before S6 review. The Chinese name follows the project’s working form. {ch5} {ch8} {ch10} {index}

### 名称与书内身份

- **索引姓名：** Veronese, Paolo；正文全名 Paolo Veronese，后文亦作 Veronese。中文标题采用项目常用译名。{index} {ch5} {ch8}
- **跨章锚点：** 第5章 p.128、第8章 p.216及第10章 p.284 的正文姓名均与同一索引主项对应；本卡只整合身份，不裁定单条作品、影响或交往关系。{ch5} {ch8} {ch10}

## 关系与证据

当前没有登记正式关系。涉及该人物的 19 条 S2 关系候选留待 S6 逐条审查；正文共现、艺术比较或索引定位不自动成为正式关系。{ch5} {ch8} {ch10}
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
    parser = argparse.ArgumentParser(description="Register Paolo Veronese's source-backed person identity group in S4.")
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
    assert candidate.get("canonical_name") == "Veronese, Paolo"
    assert candidate.get("index_entry_id") == "UVWXYZ.csv#91"
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
        and "veronese" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(related) == 26, f"unexpected statement count involving Veronese: {len(related)}"
    assert relation_count == 19, f"unexpected relation-candidate count involving Veronese: {relation_count}"

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
    assert totals["registered_groups"] == 272 and totals["registered_members"] == 341, totals
    assert totals["pending_groups"] == 4562 and totals["pending_members"] == 4665, totals
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[保罗·委罗内塞人物卡]"
        "(../units/persons/paolo-veronese.md)，19条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S4 person：Paolo Veronese 跨章身份组登记（2026-10-16）"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 人物身份组只含一个候选。索引 UVWXYZ.csv#91 与第5章 p.128、第8章 p.216 "
        "的正文全名相互印证；第10章 p.284继续以 Veronese 指称同一画家。索引正文存在 pp.279、355/356 的定位差异，候选原记录保留了该差异，"
        "本卡引用直接核对过的正文页码，不将索引差异改写为已解决。未发现同身份既有 KU，未使用外部身份源。\n"
        f"- 涉及该人物的26条 S2 陈述中19条为关系候选，留待 S6 逐条审查；未登记正式关系，也未开展 S5 补足。\n\n"
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
