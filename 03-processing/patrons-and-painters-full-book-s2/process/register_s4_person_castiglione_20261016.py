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

GROUP = "new-person:benedetto-castiglione-giovanni-c3cfd274af"
MEMBERS = ("cand-0602", "cand-0603", "cand-0604", "cand-0605")
KU_ID = "units/persons/giovanni-benedetto-castiglione"
CARD_REL = "04-knowledge/units/persons/giovanni-benedetto-castiglione.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "乔瓦尼·贝内代托·卡斯蒂廖内"
NAME_EN = "Giovanni Benedetto Castiglione"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-castiglione-20261016"

SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "location": "第4章 p.114；OCR L173–174",
        "span": "lines 173–174; print p. 114",
        "summary": (
            "第4章称 Castiglione 为热那亚画家，并将其图画放在 Cassiano 的文化影响讨论中；"
            "原文同时说明无法确认 Cassiano 对他有直接兴趣。"
        ),
        "quotes": (
            (
                "line 173",
                "strangely beautiful drawings bythe Genoese painter Giovanni Benedetto Castiglione, an admirer of Poussin",
            ),
            (
                "line 173",
                "artists in whom he is not known to have taken a direct interest",
            ),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "location": "第5章 p.124 及注释；OCR L38–49",
        "span": "lines 38–49; print p. 124 and note 2",
        "summary": (
            "正文提到一幅由 Castiglione 的出版者献出的 Diogenes 版画；注释又称这是 Castiglione 的版画。"
        ),
        "quotes": (
            (
                "line 38",
                "Castiglione whose publisher dedicated to him a fine print of Diogenes searching in vain for one honest man",
            ),
            (
                "line 47",
                "comes from Castiglione’s print of Diogenes",
            ),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "location": "第8章 p.207；OCR L44",
        "span": "line 44; print p. 207",
        "summary": "第8章在一位收藏家的购藏语境中称 Castiglione 为动物题材专家。",
        "quotes": (("line 44", "works by the animal specialist Castiglione"),),
    },
    {
        "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
        "location": "第9章 pp.266–267；OCR L309–321",
        "span": "lines 309–321; print pp. 266–267",
        "summary": (
            "第9章以完整姓名说明 Castiglione 的素描集，并讨论其作品在十八世纪的接受；"
            "随后称这位艺术家曾在曼图亚任宫廷画家二十余年。"
        ),
        "quotes": (
            (
                "line 309; print p. 266",
                "his magnificent set of drawings, the finest in existence, by the Genoese artist Giovanni Benedetto Castiglione",
            ),
            (
                "line 321; print p. 267",
                "for this artist had been court painter at Mantua for over twenty years",
            ),
        ),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/C.csv",
        "location": "全书索引 C.csv#126–129",
        "span": "C.csv#126–129",
        "summary": (
            "索引主项及三个子项以相同全名列出人物、Sagredo 收藏中的素描、其对十八世纪的意义和 Diogenes 版画。"
        ),
        "quotes": (
            ("C.csv#126", "Castiglione, Giovanni Benedetto"),
            ("C.csv#127", "drawings in Sagredo collection"),
            ("C.csv#128", "importance of for 18th century"),
            ("C.csv#129", "print of Diogenes"),
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
    ch4 = "[第4章 p.114](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L173–174）"
    ch5 = "[第5章 p.124及注释](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L38–49）"
    ch8 = "[第8章 p.207](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L44）"
    ch9 = "[第9章 pp.266–267](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L309–321）"
    index = "[全书索引 C.csv#126–129](../../../02-sources/03-Index/03-2-Index-CSV/C.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡将全书索引主项及其三个相关子项归入同一人物：索引写作 “Castiglione, Giovanni Benedetto”，正文第4章称他为热那亚画家 Giovanni Benedetto Castiglione。第4章在讨论 Cassiano 的文化影响时提及其图画，并明确保留“无法确认 Cassiano 曾直接关注他”的限定；第5章提到由其出版者献出的 Diogenes 版画；第8章称其为动物题材专家；第9章记述其素描集及作品在十八世纪的接受，并称他曾在曼图亚任宫廷画家二十余年。中文名为本项目工作译名。{ch4} {ch5} {ch8} {ch9} {index}

**English:** This card groups the book’s main index entry and its three related subentries under one person. The index gives the name “Castiglione, Giovanni Benedetto,” and Chapter 4 calls him the Genoese painter Giovanni Benedetto Castiglione. In discussing Cassiano’s cultural influence, Chapter 4 mentions his drawings while explicitly qualifying that Cassiano is not known to have taken a direct interest in him. Chapter 5 mentions a print of Diogenes dedicated by his publisher; Chapter 8 calls him an animal specialist; and Chapter 9 describes his set of drawings and their reception in the eighteenth century, and says that he had been court painter at Mantua for over twenty years. The Chinese name is a project working transliteration. {ch4} {ch5} {ch8} {ch9} {index}

### 名称与书内身份

- **索引姓名：** Castiglione, Giovanni Benedetto；正文完整姓名为 Giovanni Benedetto Castiglione。中文标题采用项目工作译名。{index} {ch4}
- **身份依据：** 三个索引子项分别指向 Sagredo 收藏中的素描、该画家对十八世纪的意义及 Diogenes 版画；逐项对应的正文均以全名或明确的 Castiglione 指称锚定同一画家。{ch5} {ch9} {index}
- **陈述边界：** 第4章对 Cassiano 是否直接关注 Castiglione 保留不确定性；本卡不把文化影响语境改写成有据的直接关系，也不将 S2 关系候选预先登记为正式关系。{ch4}

## 关系与证据

当前没有登记正式关系。涉及该人物的 27 条 S2 关系候选留待 S6 逐条审查；本卡只整理来源支持的身份与书内语境。{ch4} {ch5} {ch8} {ch9}
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
    parser = argparse.ArgumentParser(description="Register the Castiglione person identity group in S4.")
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
        assert candidate.get("canonical_name") == "Castiglione, Giovanni Benedetto"
        assert row.get("decision") == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == GROUP
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (
            row.get("name_en", "").casefold() == NAME_EN.casefold()
            or "castiglione" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        )
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted

    for item in SOURCES:
        source_path = ROOT / item["source_file"]
        normalized = " ".join(source_path.read_text(encoding="utf-8-sig").split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized, (item["source_file"], quote)

    statements_path = TABLES / "book-statements.jsonl"
    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [row for row in statements if contains_candidate(row, "cand-0602")]
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in related)
    assert len(related) == 34, f"unexpected statement count involving Castiglione: {len(related)}"
    assert relation_count == 27, f"unexpected relation-candidate count involving Castiglione: {relation_count}"

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
    assert totals["registered_groups"] == 269 and totals["registered_members"] == 338, totals
    assert totals["pending_groups"] == 4566 and totals["pending_members"] == 4670, totals
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（cand-0602、cand-0603、cand-0604、cand-0605）映射至"
        "[乔瓦尼·贝内代托·卡斯蒂廖内人物卡](../units/persons/giovanni-benedetto-castiglione.md)，"
        "27条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S4 person：Giovanni Benedetto Castiglione 跨章身份组登记（2026-10-16）"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- {', '.join(MEMBERS)} → {GROUP} → {KU_ID}；该 S3 身份组四条候选共用一张 KU。索引 C.csv#126–129 "
        "以 Castiglione, Giovanni Benedetto 列出主项及三个相关子项；原始正文回查已分别锚定 Sagredo 收藏中的素描、"
        "其对十八世纪的意义和 Diogenes 版画。第4章 p.114 直接给出热那亚画家全名，并限定无法确认 Cassiano 曾直接关注他；"
        "第5章 p.124 正文及注释、第8章 p.207、第9章 pp.266–267 提供相应书内语境。中文标题为项目工作译名；未使用外部身份源，"
        "也未把 S2 关系候选转为正式关系。\n"
        f"- 主项 cand-0602 涉及34条 S2 陈述，其中27条为关系候选，均留待 S6 逐条审查；未开展 S5 补足。\n\n"
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
