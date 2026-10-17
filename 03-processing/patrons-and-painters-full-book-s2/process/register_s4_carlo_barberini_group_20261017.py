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

CANDIDATES = ("cand-0194", "cand-0195")
GROUP = "new-person:barberini-carlo-2f55dd94e4"
KU_ID = "units/persons/carlo-barberini-brother-of-urban-viii"
CARD_REL = "04-knowledge/units/persons/carlo-barberini-brother-of-urban-viii.md"
CHAPTER_1 = "02-sources/02-Markdown/02_CHP-2_sec_i.md"
CHAPTER_2 = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/B.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp2-sec-ii-l3-8-colonna-sale",
    "st-chp2-sec-ii-l3-8-orsini-sale",
    "st-chp2-secii-l118-125-carlo-caesar-comparison",
    "st-chp2-secii-l118-125-carlo-character-and-honours",
    "st-chp2-secii-l118-125-urban-sibling-carlo",
    "st-chp2-secii-l118-125-carlo-command-in-chief",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第2章；印刷页26；OCR L68",
            "sentence_summary": "Haskell 记述当时为枢机的 Urban 与其兄 Carlo 共同购置并布置 Via de’ Giubbonari 附近的宫殿。",
            "original_quotes": [
                {
                    "source_span": "line 68",
                    "text": "He had continued, while in Paris, with the decoration of his chapel in S. Andrea della Valle, and had also joined with his brother Carlo in buying and furnishing a palace near the Via de’ Giubbonari to match his new status.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_1,
                "source_span": "line 68; print p. 26",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第2章；印刷页31；OCR L7–8",
            "sentence_summary": "Haskell 称 Carlo Barberini 于1624年购入 Orsini 的 Monte Rotondo 地产，翌年购入 Colonna 的 Roviano 城堡。",
            "original_quotes": [
                {
                    "source_span": "lines 7–8",
                    "text": "In 1624, for instance, the Orsini sold their estates at Monte Rotondo to Carlo Barberini; a year later the Colonna sold their Castle of Roviano to the same buyer.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_2,
                "source_span": "lines 7–8; print p. 31",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第2章；印刷页41；OCR L121–123",
            "sentence_summary": "Haskell 称 Urban VIII 的兄长 Carlo 于1630年去世；并将其记为教宗陆海军总司令和温和、能干的商人。",
            "original_quotes": [
                {
                    "source_span": "lines 121–123",
                    "text": "When his brother Carlo died in 1630 the Pope commissioned a memorial plaque from Bernini and the Senate obsequiously followed suit by ordering the erection of a statue on the Capitol. ... Though commander-in-chief of the papal land and sea forces, Carlo had scarcely been a Julius Caesar. A mild and yet efficient businessman",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_2,
                "source_span": "lines 121–123; print p. 41",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；B.csv#41 主项、B.csv#42 子项；印刷页26、31、41",
            "sentence_summary": "主项以 Barberini, Carlo (brother to Urban VIII) 定位第26、31页；monuments to 子项将同一姓名定位第41页。",
            "original_quotes": [
                {
                    "source_span": "index entry B.csv#41",
                    "text": "| Barberini, Carlo (brother to Urban VIII) |  |  |  | 26, 31 |",
                },
                {
                    "source_span": "index entry B.csv#42",
                    "text": "| Barberini, Carlo (brother to Urban VIII) |  | monuments to |  | 41 |",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entries B.csv#41–42",
            },
        },
    ]
    frontmatter = {
        "title": "卡洛·巴贝里尼（Carlo Barberini）",
        "name_en": "Carlo Barberini",
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

**中文：** 书后索引 B.csv#41 将 Carlo Barberini 标作 Urban VIII 之兄，并定位至第2章 pp.26、31；同一子项 B.csv#42 的 monuments to 定位至 p.41。第26页记 Urban 与兄长 Carlo 共同购置宫殿；第31页以全名 Carlo Barberini 指称1624、1625年两次地产交易的买方；第41页记其于1630年去世并由 Pope 订制纪念牌。上述全名、亲属称谓和页段相互吻合，支持将两个候选合为一个 source-local 人物 KU。本卡对应 Urban VIII 的兄长，不是其父亲 Carlo Barberini；不据此补充外部生平。[第2章 p.26](../../../{CHAPTER_1})（L68）；[第2章 p.31](../../../{CHAPTER_2})（L7–8）；[第2章 p.41](../../../{CHAPTER_2})（L121–123）；[书后索引](../../../{INDEX_FILE})（B.csv#41–42）

**English:** Index entry B.csv#41 identifies Carlo Barberini as the brother of Urban VIII and locates him at Chapter 2, pp.26 and 31; subentry B.csv#42, “monuments to,” locates p.41. Page 26 says Urban and his brother Carlo jointly bought and furnished a palace. Page 31 names Carlo Barberini as the buyer in two property transactions in 1624 and 1625. Page 41 records his death in 1630 and a memorial plaque commissioned by the Pope. These names, kinship terms and page locations support mapping the two candidates to one book-local person KU. This card refers to Urban VIII’s brother, not his father, who was also named Carlo Barberini; no external biography is added. [Chapter 2, p.26](../../../{CHAPTER_1}) (L68); [Chapter 2, p.31](../../../{CHAPTER_2}) (L7–8); [Chapter 2, p.41](../../../{CHAPTER_2}) (L121–123); [Index](../../../{INDEX_FILE}) (B.csv#41–42)

### 名称

原书全名为 Carlo Barberini。索引形式为 Barberini, Carlo (brother to Urban VIII)；中文显示名“卡洛·巴贝里尼”为工作音译。

The source gives the full name Carlo Barberini. The index form is Barberini, Carlo (brother to Urban VIII). The Chinese display name is a working transliteration.

### 身份边界

本卡只指索引所标 Urban VIII 之兄 Carlo Barberini。现有 Antonio Barberini 人物卡所记父亲 Carlo Barberini 属不同亲属代际，不映射至本卡。此身份区分依据本书索引及第2章语境；本轮未查阅外部身份记录。

This card refers only to the Carlo Barberini identified by the index as Urban VIII’s brother. The Carlo Barberini recorded as the father in the existing Antonio Barberini card belongs to a different generation and is not mapped here. This distinction follows the book’s index and Chapter 2 context; no external identity authority was consulted.

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register both S3 candidates in Carlo Barberini's one S4 person group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    _, mentions = sync.read_csv(TABLES / "mentions.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert not (ROOT / CARD_REL).exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    assert not any(
        row.get("ku_id") == KU_ID
        or (row.get("type") == "person" and (row.get("name_en") or "").casefold() == "carlo barberini")
        for row in manifest
    )

    for cid, entry, page_range, mention_count in [
        ("cand-0194", "B.csv#41", "26, 31", 2),
        ("cand-0195", "B.csv#42", "41", 3),
    ]:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["index_entry_id"] == entry
        assert candidate["canonical_name"] == "Barberini, Carlo (brother to Urban VIII)"
        assert candidate["index_page_range"] == page_range
        assert candidate["suggested_type"] == "person"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
        assert len([row for row in mentions if row.get("candidate_id") == cid]) == mention_count
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    chapter1 = (ROOT / CHAPTER_1).read_text(encoding="utf-8-sig")
    chapter2 = (ROOT / CHAPTER_2).read_text(encoding="utf-8-sig")
    index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "had also joined with his brother Carlo in buying and furnishing a palace" in chapter1
    assert "the Orsini sold their estates at Monte Rotondo to Carlo Barberini" in chapter2
    assert "When his brother Carlo died in 1630" in chapter2
    assert "Though commander-in-chief of the papal land and sea forces" in chapter2
    assert "| Barberini, Carlo (brother to Urban VIII) |  |  |  | 26, 31 |" in index
    assert "| Barberini, Carlo (brother to Urban VIII) |  | monuments to |  | 41 |" in index

    statements = sync.load_statements()
    direct_relation_ids = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relation_ids == RELATION_CANDIDATES, direct_relation_ids

    planned_alignment = [dict(row) for row in alignments]
    for cid in CANDIDATES:
        target = next(row for row in planned_alignment if row.get("candidate_id") == cid)
        target["ku_id"] = KU_ID
        target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "卡洛·巴贝里尼",
        "name_en": "Carlo Barberini",
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
        "2026-10-17 strict-stage 表审计通过：`errors=[]`、`s2_missing=[]`。审计警告中的4,546条待登记 "
        "`decision=new` alignment 行，含4,531条候选决定映射（4,462组）和15条外部身份记录。另有两条既有字段来源引用未能从对应卡片source列表解析 "
        "（`enr-06678`、`enr-06937`）；相关字段仍保留原状态。审计还提示S2迁移的语义质量仍须按关联过程记录检查；结构一致性不代表独立语义验收，也不产生准确率、召回率或语义处理吞吐指标。"
    )
    result_text, n = re.subn(
        r"^\d{4}-\d{2}-\d{2} strict-stage 表审计通过：.*$",
        audit_line, result_text, count=1, flags=re.M,
    )
    assert n == 1
    result_text += (
        "\n\n### S4 person：Carlo Barberini 两候选同组登记（2026-10-17）\n\n"
        f"`cand-0194`（B.csv#41）与 `cand-0195`（B.csv#42 子项 monuments to）按同一 S3 组 `{GROUP}` 共映射至"
        "[卡洛·巴贝里尼人物卡](../units/persons/carlo-barberini-brother-of-urban-viii.md)。索引明示其为 Urban VIII 之兄；"
        "第2章 pp.26、31、41 的亲属称谓、全名和纪念叙述相互吻合。与 Antonio Barberini 卡中另一代父亲 Carlo Barberini 区分。"
        "6条直接关系候选待 S6，未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-carlo-barberini-brother-urban-viii\"></a>\n\n"
        "### S4 person：Carlo Barberini 同组两候选登记（2026-10-17）\n\n"
        f"`cand-0194`（B.csv#41，pp.26、31）与 `cand-0195`（B.csv#42，monuments to，p.41）保持 S3 组 `{GROUP}`，"
        f"共同映射至[卡洛·巴贝里尼人物卡](../../../{CARD_REL})，一组登记一个 KU。第2章 p.26 L68 称 Urban 与兄长 Carlo 共同购置宫殿；"
        "p.31 L7–8 以 Carlo Barberini 全名指称1624、1625年两次地产交易的同一买方；p.41 L121–123 记 Urban 的兄长 Carlo 于1630年去世，"
        "并记 Pope 为其订制纪念牌。主项和 monuments to 子项所列页码由同一原书索引明确连接，支持该候选组为一人。"
        "该人不是 Antonio Barberini 卡所记的父亲 Carlo Barberini；后者为 Urban 的父辈，本卡明确分开。"
        "6条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。"
        "本轮未新增正式关系、enrichment 字段事实或 sources.csv 记录。"
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
        print(f"S4 Carlo Barberini two-candidate group dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"same identity group={GROUP}; candidates={len(group_rows)}; direct_relation_candidates={len(direct_relation_ids)}")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD_REL).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: one group, {len(CANDIDATES)} candidates -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
