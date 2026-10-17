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

CANDIDATE = "cand-1390"
GROUP = "new-person:da-leonardo-vinci-092752ba56"
KU_ID = "units/persons/leonardo-da-vinci"
CARD_REL = "04-knowledge/units/persons/leonardo-da-vinci.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "莱昂纳多·达·芬奇"
NAME_EN = "Leonardo da Vinci"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-leonardo-da-vinci-20261016"

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "location": "第4章 pp.106、113；OCR L91–99、161–170",
        "span": "lines 91–99, 161–170; print pp. 106, 113",
        "summary": "第4章 p.106直接写出 Leonardo da Vinci 全名，并在 p.113继续以 Leonardo 指称。",
        "quotes": (
            ("lines 95–96; print p. 106", "a manuscript of Leonardo da Vinci’s Trattato della,pittura"),
            ("line 165; print p. 113", "Leonardo’s thought at Cassiano’s behest"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章注释 p.319；OCR L305",
        "span": "line 305; print p. 319, note 2",
        "summary": "第10章注释再次出现完整姓名 Leonardo da Vinci。",
        "quotes": (("line 305", "Leonardo da Vinci cita un suo manoscritto"),),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/L.csv",
        "location": "全书索引 L.csv#47",
        "span": "L.csv#47",
        "summary": "索引以 Leonardo da Vinci 列出人物，并定位至第4章及第10章注释。",
        "quotes": (("L.csv#47", "Leonardo da Vinci"),),
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
    ch4 = "[第4章 pp.106、113](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L91–99、161–170）"
    ch10 = "[第10章注释 p.319](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L305）"
    index = "[全书索引 L.csv#47](../../../02-sources/03-Index/03-2-Index-CSV/L.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以 “Leonardo da Vinci” 列出人物；第4章 p.106 直接使用完整姓名，p.113 在同一章中继续以 Leonardo 指称。第10章注释又出现完整姓名。索引与正文跨章姓名锚点对应本轮 S3 人物候选，本卡据此归并为一个来源人物。中文名采用项目常用译名。{ch4} {ch10} {index}

**English:** The book’s index lists “Leonardo da Vinci.” Chapter 4 p. 106 uses the full name, and p. 113 continues to refer to Leonardo within the same chapter. The full name appears again in a Chapter 10 note. These index and cross-chapter name anchors correspond to the current S3 person candidate and are consolidated here as one source-local person. The Chinese name follows the project’s working form. {ch4} {ch10} {index}

### 名称与书内身份

- **索引姓名：** Leonardo da Vinci；正文及第10章注释亦以完整姓名或 Leonardo 指称。中文标题采用“莱昂纳多·达·芬奇”。{index} {ch4} {ch10}
- **来源范围：** 卡片只整合书中对同一姓名的跨章提及。涉及本人、手稿及相关艺术史叙述的 S2 陈述和关系候选仍按其自身证据状态处理。{ch4} {ch10}

## 关系与证据

当前没有登记正式关系。涉及该人物的 17 条 S2 关系候选留待 S6 逐条审查；正文同段出现或目录定位不自动转为正式关系。{ch4} {ch10}
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
    parser = argparse.ArgumentParser(description="Register Leonardo da Vinci's source-backed person identity group in S4.")
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
    assert candidate.get("canonical_name") == "Leonardo da Vinci"
    assert candidate.get("index_entry_id") == "L.csv#47"
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
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_EN.casefold())
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in SOURCES:
        normalized = " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["source_file"], quote)
    _, index_rows = sync.read_csv(ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "L.csv")
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
    assert len(related) == 19, f"unexpected statement count involving Leonardo: {len(related)}"
    assert relation_count == 17, f"unexpected relation-candidate count involving Leonardo: {relation_count}"

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
    assert totals["registered_groups"] == 274 and totals["registered_members"] == 343, totals
    assert totals["pending_groups"] == 4560 and totals["pending_members"] == 4663, totals
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[莱昂纳多·达·芬奇人物卡]"
        "(../units/persons/leonardo-da-vinci.md)，17条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S4 person：Leonardo da Vinci 跨章身份组登记（2026-10-16）"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 人物身份组只含一个候选。索引 L.csv#47 与第4章 pp.106、113、第10章注释 p.319 "
        "均以完整姓名或稳定简称指称 Leonardo da Vinci。manifest 中有 Leonardo Pesaro、Leonardo Valmarana 两名不同人物，"
        "均与本候选全名不同，不作为同一性复用目标。未使用外部身份源。\n"
        f"- 涉及该人物的19条 S2 陈述中17条为关系候选，留待 S6 逐条审查；未登记正式关系，也未开展 S5 补足。\n\n"
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
