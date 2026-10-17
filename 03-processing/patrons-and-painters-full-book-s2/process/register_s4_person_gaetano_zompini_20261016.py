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

GROUP = "new-person:gaetano-zompini-1b920c543e"
MEMBERS = ("cand-2874", "cand-2877")
KU_ID = "units/persons/gaetano-zompini"
CARD_REL = "04-knowledge/units/persons/gaetano-zompini.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "加埃塔诺·宗皮尼"
NAME_EN = "Gaetano Zompini"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-gaetano-zompini-20261016"

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章 pp.273–274；OCR L68–72",
        "span": "lines 68–72; print pp. 273–274",
        "summary": "第9章以完整姓名称其为画家，并讨论其提出的方案。",
        "quotes": (
            (
                "line 68; print p. 273",
                "The painter Gaetano Zompini, whose idea was accepted, put forward an iconographical proposal of some complexity",
            ),
            (
                "line 72; print p. 274",
                "Like Tiepolo, Zompini must certainly have taken clerical advice",
            ),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章 pp.339–340、344；OCR L76、119–120",
        "span": "lines 76, 119–120; print pp. 340, 344",
        "summary": (
            "第13章以 Gaetano Zompini 全名列出画家，并在第344页继续以姓氏指称其创作。"
        ),
        "quotes": (
            (
                "line 76; print p. 340",
                "the two artists who especially worked for him, Francesco Fontebasso and Gaetano Zompini",
            ),
            (
                "line 119; print p. 344",
                "his employment of Gaetano Zompini, whom he took into his house and provided with a regular allowance",
            ),
            (
                "line 120; print p. 344",
                "Zompini engraved a series of Castiglione drawings",
            ),
        ),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "location": "全书索引 UVWXYZ.csv#211、#214",
        "span": "UVWXYZ.csv#211, #214",
        "summary": (
            "索引主项与 Zanetti 相关子项均以 Zompini, Gaetano 列出同一人物。"
        ),
        "quotes": (
            ("UVWXYZ.csv#211", "Zompini, Gaetano"),
            ("UVWXYZ.csv#214", "work for A. M. Zanetti the Elder"),
        ),
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
    ch9 = "[第9章 pp.273–274](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L68–72）"
    ch13 = "[第13章 pp.340、344](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L76、119–120）"
    index = "[全书索引 UVWXYZ.csv#211、#214](../../../02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Zompini, Gaetano” 列出人物主项，并在关于 Zanetti 的子项下重复同一姓名。正文第9章称 Gaetano Zompini 为画家，并以完整姓名说明其提出的方案；第13章再次以完整姓名列出他，并在第344页继续以姓氏指称其作品。正文与索引共同提供同一人物的跨章身份锚点。中文名为本项目工作译名。{ch9} {ch13} {index}

**English:** The book’s index lists “Zompini, Gaetano” as a person entry and repeats the same name in a Zanetti-related subentry. Chapter 9 identifies Gaetano Zompini as a painter and uses his full name when describing a proposal he put forward. Chapter 13 lists him again by his full name and continues to refer to his work by surname on p. 344. The body text and index provide cross-chapter identity anchors for one person. The Chinese name is a project working transliteration. {ch9} {ch13} {index}

### 名称与书内身份

- **索引姓名：** Zompini, Gaetano；正文多处写作 Gaetano Zompini。中文标题采用项目工作译名。{index} {ch9} {ch13}
- **组内映射：** 主项 cand-2874 与子项 cand-2877 同属该人物；子项描述索引对同一人的作品语境，不另建人物、作品或关系 KU。{index} {ch13}

## 关系与证据

当前没有登记正式关系。涉及该人物的 9 条 S2 关系候选留待 S6 逐条审查；索引子项和正文提及不直接转为正式关系。{ch9} {ch13}
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
    parser = argparse.ArgumentParser(description="Register the Gaetano Zompini person identity group in S4.")
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
    assert all(cid in candidate_by_id and cid in alignment_by_id for cid in MEMBERS)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(MEMBERS)
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("canonical_name") == "Zompini, Gaetano"
        assert row.get("decision") == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == GROUP
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and "zompini" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in SOURCES:
        source_path = ROOT / item["source_file"]
        normalized = " ".join(source_path.read_text(encoding="utf-8-sig").split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["source_file"], quote)

    _, index_rows = sync.read_csv(ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "UVWXYZ.csv")
    for entry_num, expected_subentry in ((211, ""), (214, "work for A. M. Zanetti the Elder")):
        row = index_rows[entry_num]
        assert row["Main Entry"] == "Zompini, Gaetano"
        assert row["Sub-entry"] == expected_subentry

    statements_path = TABLES / "book-statements.jsonl"
    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [row for row in statements if contains_candidate(row, MEMBERS[0]) or contains_candidate(row, MEMBERS[1])]
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in related)
    assert len(related) == 14, f"unexpected statement count involving Zompini: {len(related)}"
    assert relation_count == 10, f"unexpected relation-candidate count involving Zompini: {relation_count}"

    planned_alignment = [dict(row) for row in alignments]
    for cid in MEMBERS:
        row = next(
            item for item in planned_alignment
            if item.get("candidate_id") == cid and not item.get("external_source")
        )
        row["ku_id"] = KU_ID
        row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
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
    assert totals["registered_groups"] == 275 and totals["registered_members"] == 345, totals
    assert totals["pending_groups"] == 4559 and totals["pending_members"] == 4661, totals
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（cand-2874、cand-2877）映射至[加埃塔诺·宗皮尼人物卡]"
        "(../units/persons/gaetano-zompini.md)，10条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S4 person：Gaetano Zompini 跨章身份组登记（2026-10-16）"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {', '.join(MEMBERS)} → {GROUP} → {KU_ID}；该 S3 身份组两条候选共用一张 KU。索引 UVWXYZ.csv#211、#214 "
        "以同一姓名列出人物主项和 Zanetti 相关子项；第9章 pp.273–274 与第13章 pp.340、344 的正文均有相应全名锚点。"
        "本卡将索引子项映射到同一人物，不另建人物或作品 KU；中文名为项目工作译名。\n"
        f"- 涉及该人物的14条 S2 陈述中10条为关系候选，均留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_accepted = insert_accepted(accepted)

    target_files = [ALIGNMENT, MANIFEST, ACCEPTED, KNOWLEDGE, RESULT]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in target_files)
    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; group_members={len(MEMBERS)}; source_records={len(SOURCES)}; "
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
        f"applied: {GROUP} -> {KU_ID}; members={len(MEMBERS)}; relation_candidates_pending={relation_count}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; recovery_backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
