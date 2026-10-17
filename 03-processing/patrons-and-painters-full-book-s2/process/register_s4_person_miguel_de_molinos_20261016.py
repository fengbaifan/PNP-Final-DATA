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

CANDIDATE = "cand-1680"
GROUP = "new-person:de-miguel-molinos-a5f7ffff73"
KU_ID = "units/persons/miguel-de-molinos"
CARD_REL = "04-knowledge/units/persons/miguel-de-molinos.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "米格尔·德·莫利诺斯"
NAME_EN = "Miguel de Molinos"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-miguel-de-molinos-20261016"

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "location": "第3章 p.81；OCR L54–55",
        "span": "lines 54–55; print p. 81",
        "summary": (
            "Haskell 称 Miguel de Molinos 为西班牙司铎，记其1664年抵达罗马，并概述其教义及影响。"
        ),
        "quotes": (
            (
                "line 54",
                "the arrival in 1664 of a Spanish priest, Miguel de Molinos, who rapidly acquired a wide and exceedingly influential following",
            ),
            (
                "line 54",
                "that communion could be administered daily to the faithful if they required it",
            ),
            (
                "line 54",
                "far more stress should be placed on passive contemplation than active meditation",
            ),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "location": "第3章 p.82；OCR L61–64",
        "span": "lines 61–64; print p. 82",
        "summary": (
            "Haskell 讨论 Molinos 的神学主题及另一位艺术家可能受其影响的说法，同时明确保留来源关系的不确定性。"
        ),
        "quotes": (
            (
                "lines 61–63",
                "it is impossible to say whether or not he derived the notion from Molinos",
            ),
        ),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
        "location": "全书索引 M.csv#220",
        "span": "M.csv#220",
        "summary": "全书索引以 Molinos, Miguel de 列出该人物，并定位至第3章 pp.81–83。",
        "quotes": (("M.csv#220", "Molinos, Miguel de"),),
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
    ch3 = "[第3章 pp.81–82](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L54–64）"
    index = "[全书索引 M.csv#220](../../../02-sources/03-Index/03-2-Index-CSV/M.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本书称 Miguel de Molinos 为西班牙司铎，记其于1664年抵达罗马，并将其广泛影响与每日领圣体、强调静观等教义主张相联系。第3章还讨论其神学观念与另一位艺术家作品主题的相似性，但明确表示无法判定该观念是否源自 Molinos；本卡保留原文的不确定性，不将其写成确定影响关系。中文名为本项目工作译名。{ch3} {index}

**English:** The book identifies Miguel de Molinos as a Spanish priest who arrived in Rome in 1664, and connects his wide influence with teachings including daily communion and an emphasis on passive contemplation. Chapter 3 also discusses a possible similarity between his theological ideas and the subject of another artist’s work, while explicitly saying that it is impossible to determine whether the idea derived from Molinos. This card preserves that uncertainty and does not state a definite influence relationship. The Chinese name is a project working transliteration. {ch3} {index}

### 名称与书内身份

- **索引姓名：** Molinos, Miguel de；正文以完整姓名 Miguel de Molinos 指称。中文标题采用项目工作译名。{index} {ch3}
- **书内语境：** 本卡只记录第3章对其身份、抵达罗马时间及教义影响的叙述；其中教义概括归属于 Haskell 的原文说明，不扩写为外部传记结论。{ch3}
- **不确定性：** Haskell 明言无法判断另一位艺术家关于基督圣血的观念是否源自 Molinos；该问题不作为已成立的关系事实。{ch3}

## 关系与证据

当前没有登记正式关系。涉及该人物的 10 条 S2 关系候选留待 S6 逐条审查；不根据共现或主题相似直接建边。{ch3}
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
    parser = argparse.ArgumentParser(description="Register Miguel de Molinos's source-backed person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate = candidate_by_id[CANDIDATE]
    target = alignment_by_id[CANDIDATE]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Molinos, Miguel de"
    assert candidate.get("index_entry_id") == "M.csv#220"
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
        and NAME_EN.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in SOURCES:
        source_path = ROOT / item["source_file"]
        normalized = " ".join(source_path.read_text(encoding="utf-8-sig").split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["source_file"], quote)

    _, index_rows = sync.read_csv(ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "M.csv")
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
    assert len(related) == 10, f"unexpected statement count involving Molinos: {len(related)}"
    assert relation_count == 10, f"unexpected relation-candidate count involving Molinos: {relation_count}"

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
    assert totals["registered_groups"] == 270 and totals["registered_members"] == 339, totals
    assert totals["pending_groups"] == 4565 and totals["pending_members"] == 4669, totals
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[米格尔·德·莫利诺斯人物卡]"
        "(../units/persons/miguel-de-molinos.md)，10条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S4 person：Miguel de Molinos 跨章身份组登记（2026-10-16）"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 人物身份组只含一个候选。索引 M.csv#220 与第3章 p.81 的正文全名锚点一致。"
        "第3章称其为西班牙司铎，记其1664年抵达罗马并概述其教义及影响；第3章 p.82 明言无法判断另一位艺术家关于基督圣血的观念是否源自 Molinos。"
        "卡片保留该不确定性；中文名为项目工作译名，未使用外部身份源。\n"
        f"- 涉及该人物的10条 S2 陈述均为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。\n\n"
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
