from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATE = "cand-2289"
GROUP = "new-person:jacques-jean-rousseau-ad86218db7"
KU_ID = "units/persons/jean-jacques-rousseau"
CARD_REL = "04-knowledge/units/persons/jean-jacques-rousseau.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/Q-R.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp10-p328-biffi-diary-on-rousseau",
    "st-chp10-p328-ode-rousseau-influence",
    "st-chp15-p369-rousseau-influence-alticchiero",
    "st-chp15-p372-rousseau-influence-on-querini-view-of-past",
    "st-chp10-p328-biffi-follower-of-rousseau-inferred",
}
NON_RELATION_STATEMENTS = {
    "st-chp10-p328-arcadia-not-necessary-cause",
    "st-chp10-p328-biffi-diary-entry-after-rousseau-death",
}


def make_card() -> str:
    citation = BOOK_CITATION
    sources = [
        {
            "citation": citation,
            "location": "第10章；印刷页328；OCR L241–246",
            "sentence_summary": (
                "Haskell 第10章称 Il Filosofo dell’Alpi 受 Rousseau 影响，引用 Biffi 对 Rousseau 去世的日记评价，"
                "并评论 Rousseau 的教导与后世艺术家对自然的处理之间的关系。"
            ),
            "original_quotes": [
                {"source_span": "line 242", "text": "was strongly influenced by Rousseau;"},
                {
                    "source_span": "lines 244–245",
                    "text": (
                        "when Biffi heard later of that philosopher’s death, he wrote in his diary6: "
                        "‘The greatest genius of the century is dead.... He was my father, my guide, my master, my idol... . .’"
                    ),
                },
                {
                    "source_span": "line 246",
                    "text": "the more scrupulous and deeply felt treatment of nature that was adopted by later artists was by no means a necessary consequence of that philosopher’s teaching.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "lines 241–246; print p. 328",
            },
        },
        {
            "citation": citation,
            "location": "第15章；印刷页369；OCR L49–59",
            "sentence_summary": (
                "Haskell 记述 Alticchiero 的桌上陈列 Voltaire 与 Rousseau 的 Houdon 半身像，"
                "并称两人的影响贯穿别墅和园林；这是本书对该场所的叙述。"
            ),
            "original_quotes": [
                {
                    "source_span": "lines 57–59",
                    "text": "among them Voltaire and Rousseau by Houdon, and the influence of both men is felt throughout the villa and gardens.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "source_span": "lines 57–59; print p. 369",
            },
        },
        {
            "citation": citation,
            "location": "第15章；印刷页372；OCR L85–88",
            "sentence_summary": "Haskell 将 Querini 对过去的看法与 Rousseau 的影响联系起来。",
            "original_quotes": [
                {
                    "source_span": "lines 87–88",
                    "text": "And his view of it was inextricably bound up with the influence of Rousseau.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "source_span": "lines 85–88; print p. 372",
            },
        },
        {
            "citation": citation,
            "location": "书后索引；Q-R.csv#217；印刷页328、369、372",
            "sentence_summary": "索引以 Rousseau, Jean Jacques 形式列出此人物，并将其跨章定位至第10、15章。",
            "original_quotes": [
                {
                    "source_span": "index entry Q-R.csv#217",
                    "text": "| Rousseau, Jean Jacques |  |  |  | 328, 369, 372 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry Q-R.csv#217",
            },
        },
    ]
    frontmatter = {
        "title": "让-雅克·卢梭（Jean Jacques Rousseau）",
        "name_en": "Jean Jacques Rousseau",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** 索引 Q-R.csv#217 以 Rousseau, Jean Jacques 形式，将该人物定位至第10章 p.328 及第15章 pp.369、372。Haskell 第10章称 Il Filosofo dell’Alpi 受 Rousseau 影响，引用 Biffi 在其去世后的日记评价，并讨论其教导与后世艺术家表现自然之间的关系；第15章将 Rousseau 与 Alticchiero 别墅、园林及 Querini 对过去的理解联系起来。以上均保留为 Haskell 的书内叙述；本卡不增加生卒年或外部传记。[第10章 p.328](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L241–246）；[第15章 p.369](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L57–59）；[第15章 p.372](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L85–88）；[索引](../../../{INDEX_FILE})（Q-R.csv#217）

**English:** Index entry Q-R.csv#217 files the person as Rousseau, Jean Jacques and locates him at Chapter 10, p.328, and Chapter 15, pp.369 and 372. Haskell says Il Filosofo dell’Alpi was influenced by Rousseau, quotes Biffi’s diary after Rousseau’s death, and discusses whether Rousseau’s teaching necessarily explains later artists’ treatment of nature. Chapter 15 connects Rousseau with the villa and gardens at Alticchiero and with Querini’s view of the past. These remain Haskell’s account in the book; this card adds no birth or death dates or external biography. [Chapter 10, p.328](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md) (L241–246); [Chapter 15, p.369](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md) (L57–59); [Chapter 15, p.372](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md) (L85–88); [Index](../../../{INDEX_FILE}) (Q-R.csv#217)

### 名称

书后索引写作 Rousseau, Jean Jacques；英文显示名遵循该索引姓名次序。中文名“让-雅克·卢梭”为工作音译。

The index form is Rousseau, Jean Jacques; the English display name follows the indexed personal name. The Chinese display name is a working transliteration.

### 身份边界

本卡对应书后索引 Q-R.csv#217 所指人物；第10章称其为哲学家，第15章沿用 Rousseau 指称。S3 将这三个页段归入同一 source-local person 组。本轮未查阅外部身份记录，不将本书的评价性或因果性表述升级为独立核实的事实。

This card represents the person under index entry Q-R.csv#217; Chapter 10 calls him a philosopher and Chapter 15 continues to refer to Rousseau. S3 grouped the three page locations as one book-local person. No external identity authority was consulted, and the book’s evaluative or causal statements are not presented as independently verified facts.

## 关系与证据

5条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。另有两条涉及 Rousseau 教导或 Biffi 日记的 statement 保持 `relation_candidate=false`，不改写为正式关系：`st-chp10-p328-arcadia-not-necessary-cause`、`st-chp10-p328-biffi-diary-entry-after-rousseau-death`。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Jean Jacques Rousseau's cross-chapter person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, mentions = sync.read_csv(TABLES / "mentions.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    alignment = next(row for row in alignments if row.get("candidate_id") == CANDIDATE)
    assert candidate["index_entry_id"] == "Q-R.csv#217"
    assert candidate["canonical_name"] == "Rousseau, Jean Jacques"
    assert candidate["index_page_range"] == "328, 369, 372"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not any(
        row.get("ku_id") == KU_ID
        or (row.get("type") == "person" and (row.get("name_en") or "").casefold() == "jean jacques rousseau")
        for row in manifest
    )
    card_path = ROOT / CARD_REL
    assert not card_path.exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted

    chapter10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_sec_ii.md").read_text(encoding="utf-8-sig")
    chapter15 = (ROOT / "02-sources/02-Markdown/15_CHP-15_sec_ii.md").read_text(encoding="utf-8-sig")
    index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "was strongly influenced by Rousseau;" in chapter10
    assert "when Biffi heard later of that philosopher’s death" in chapter10
    assert "the more scrupulous and deeply felt treatment of nature" in chapter10
    assert "the influence of both men is felt throughout the villa and gardens" in chapter15
    assert "his view of it was inextricably bound up with the influence of Rousseau" in chapter15
    assert "| Rousseau, Jean Jacques |  |  |  | 328, 369, 372 |" in index
    assert len([row for row in mentions if row.get("candidate_id") == CANDIDATE]) == 5

    statements = sync.load_statements()
    direct_relation_ids = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relation_ids == RELATION_CANDIDATES, direct_relation_ids
    direct_nonrelations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE)
        and (row.get("qualifiers") or {}).get("relation_candidate") is False
    }
    assert direct_nonrelations == NON_RELATION_STATEMENTS, direct_nonrelations

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE)
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "让-雅克·卢梭",
        "name_en": "Jean Jacques Rousseau",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, n = re.subn(
        r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        "| [既有字段表](../tables/enrichment.jsonl) | 10,509条，其中1,611条 unverified |",
        result_text, count=1, flags=re.M,
    )
    assert n == 1
    audit_line = (
        "2026-10-17 strict-stage 表审计通过：`errors=[]`、`s2_missing=[]`。审计警告中的4,548条待登记 "
        "`decision=new` alignment 行，含4,533条候选决定映射（4,463组）和15条外部身份记录。另有两条既有字段来源引用未能从对应卡片source列表解析 "
        "（`enr-06678`、`enr-06937`）；相关字段仍保留原状态。审计还提示S2迁移的语义质量仍须按关联过程记录检查；结构一致性不代表独立语义验收，也不产生准确率、召回率或语义处理吞吐指标。"
    )
    result_text, n = re.subn(
        r"^\d{4}-\d{2}-\d{2} strict-stage 表审计通过：.*$",
        audit_line, result_text, count=1, flags=re.M,
    )
    assert n == 1
    result_text += (
        "\n\n### S4 person：Jean Jacques Rousseau 跨章人物组（2026-10-17）\n\n"
        f"`{CANDIDATE}`（Q-R.csv#217）按 S3 组 `{GROUP}` 登记至[让-雅克·卢梭人物卡](../units/persons/jean-jacques-rousseau.md)。"
        "索引将第10章 p.328 与第15章 pp.369、372 归入同一人物条目；本卡保留 Haskell 对 Rousseau 影响的书内叙述，不补外部身份或生卒信息。"
        "5条直接关系候选留待 S6；两条 `relation_candidate=false` 陈述保持原分类，未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-rousseau-person\"></a>\n\n"
        "### S4 person：Jean Jacques Rousseau 跨章直接关系端点登记（2026-10-17）\n\n"
        f"候选 `{CANDIDATE}`（Q-R.csv#217）保持 S3 `new` 组 `{GROUP}`，单候选映射至[人物卡](../../../{CARD_REL})。"
        "索引页码328、369、372跨第10、15章同列；第10章 p.328 以 Rousseau 指向哲学家，并记 Il Filosofo dell’Alpi、Biffi 日记及自然观论述；"
        "第15章 p.369 将其与 Alticchiero 的 Houdon 半身像及园林影响并述，p.372 将其与 Querini 的历史观相联。"
        "同组按 S3 归并，不与其他 Rousseau 姓名候选臆合；本轮未查阅外部身份记录，也未补生卒年。"
        "5条直接 relation_candidate 保持原状待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。"
        "`st-chp10-p328-arcadia-not-necessary-cause` 与 `st-chp10-p328-biffi-diary-entry-after-rousseau-death` 均继续保持 `relation_candidate=false`；"
        "另两条将 Rousseau 列于 `mentioned_candidate_ids`、但端点为 Alticchiero 与 Houdon 的陈述也不改成 Rousseau 的正式边。"
        "本轮未写 relations.csv、未新增 enrichment 字段事实或 sources.csv 记录。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 Rousseau dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"index=Q-R.csv#217; mentions=5; direct_relation_candidates={len(direct_relation_ids)}; false_relation_statements={len(direct_nonrelations)}")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
