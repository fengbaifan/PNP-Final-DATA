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

CANDIDATE = "cand-0452"
GROUP = "new-person:brienne-de-lomenie-6472b0f466"
KU_ID = "units/persons/lomenie-de-brienne"
CARD_REL = "04-knowledge/units/persons/lomenie-de-brienne.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "洛梅尼·德·布里埃讷"
NAME_EN = "Loménie de Brienne"
FULL_NAME_EN = "Louis-Henri de Loménie, Comte de Brienne"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-lomenie-de-brienne-20261016"

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "location": "第7章 pp.181、184–186；OCR L142、170–176、205–222",
        "span": "lines 142, 170–176, 205–222; print pp. 181, 184–186",
        "summary": "第7章称其为宫廷侍臣 Loménie de Brienne，并在连续的 Mazarin 叙事中多次以 Brienne 指称。",
        "quotes": (
            ("line 142; print p. 181", "courtier Loménie de Brienne"),
            ("line 213; print p. 185", "the account given by Brienne of this occasion"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography_intro.md",
        "location": "参考书目；OCR L254–255",
        "span": "lines 254–255",
        "summary": "参考书目列出其回忆录作者为 Louis-Henri de Loménie, Comte de Brienne。",
        "quotes": (
            (
                "lines 254–255",
                "Brienne, Louis-Henri de Loménie Comte de: Mémoires, publiés par Paul Bonnefon, 3 vols., Paris 1916-19.",
            ),
        ),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/B.csv",
        "location": "全书索引 B.csv#299",
        "span": "B.csv#299",
        "summary": "索引以 Brienne, Lomenie de 为人物主项，并定位至第7章 pp.181、184–186。",
        "quotes": (("B.csv#299", "Brienne, Lomenie de"),),
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
    chapter = "[第7章 pp.181、184–186](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L142、170–176、205–222）"
    bibliography = "[参考书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography_intro.md)（L254–255）"
    index = "[全书索引 B.csv#299](../../../02-sources/03-Index/03-2-Index-CSV/B.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Brienne, Lomenie de” 列出人物；第7章正文称其为宫廷侍臣 Loménie de Brienne，并在同一连续叙述中多次以 Brienne 指称。参考书目给出其回忆录作者的完整姓名形式 “Louis-Henri de Loménie Comte de Brienne”。本卡据同书正文、索引和书目将这些姓名形式合并为一个来源人物；中文名为项目工作译名。{chapter} {bibliography} {index}

**English:** The book’s index lists “Brienne, Lomenie de.” Chapter 7 identifies a courtier as Loménie de Brienne and repeatedly refers to Brienne in the same continuous account. The bibliography gives the full name form “Louis-Henri de Loménie Comte de Brienne” for the author of his memoirs. This card consolidates the forms under one source-local person identity using the book’s body text, index, and bibliography. The Chinese name is a project working transliteration. {chapter} {bibliography} {index}

### 名称与书内身份

- **索引姓名：** Brienne, Lomenie de；正文写作 Loménie de Brienne，参考书目列作 {FULL_NAME_EN}。中文标题采用项目工作译名。{index} {chapter} {bibliography}
- **来源范围：** 第7章的相关段落围绕 Mazarin 的收藏与 Brienne 的记述展开；本卡只登记人物身份与原书姓名形式，不在 S4 裁决具体关系。{chapter}

## 关系与证据

当前没有登记正式关系。涉及该人物的 19 条 S2 关系候选留待 S6 逐条审查；本卡不将其在叙述、回忆引文或目录中的出现直接转为正式关系。{chapter} {index}
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
    parser = argparse.ArgumentParser(description="Register the Loménie de Brienne source-backed person group in S4.")
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
    assert candidate.get("canonical_name") == "Brienne, Lomenie de"
    assert candidate.get("index_entry_id") == "B.csv#299"
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
        and any(t in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for t in ("lomenie", "brienne"))
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in SOURCES:
        normalized = " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["source_file"], quote)
    _, index_rows = sync.read_csv(ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "B.csv")
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
    assert len(related) == 19, f"unexpected statement count involving Brienne: {len(related)}"
    assert relation_count == 19, f"unexpected relation-candidate count involving Brienne: {relation_count}"

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
    assert totals["registered_groups"] == 273 and totals["registered_members"] == 342, totals
    assert totals["pending_groups"] == 4561 and totals["pending_members"] == 4664, totals
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[洛梅尼·德·布里埃讷人物卡]"
        "(../units/persons/lomenie-de-brienne.md)，19条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S4 person：Loménie de Brienne 跨章身份组登记（2026-10-16）"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 人物身份组只含一个候选。索引 B.csv#299、正文第7章 p.181 的姓名形式 "
        "Loménie de Brienne，以及参考书目所列 Louis-Henri de Loménie Comte de Brienne 相互对应。第7章 p.184–186 在同一叙事中继续以 Brienne "
        "称呼，支持将这些姓名形归入同一来源人物。未发现同身份既有 KU；中文名为项目工作译名，未使用外部身份源。\n"
        f"- 涉及该人物的19条 S2 陈述均为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。\n\n"
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
