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

CANDIDATE = "cand-1509"
GROUP = "new-person:mancini-maria-652896852a"
KU_ID = "units/persons/maria-mancini"
CARD_REL = "04-knowledge/units/persons/maria-mancini.md"
CHAPTER = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
INDEX = "02-sources/03-Index/03-1-Index-MD/M.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp6-p155-lorenzo-maria-marriage",
    "st-chp6-p155-maria-impression-of-palace",
    "st-chp6-p155-maria-social-position",
    "st-chp6-p156-infidelities-lead-to-departure",
    "st-chp6-p156-maria-separation-demand",
    "st-chp6-p155-maria-niece-of-mazarin",
    "st-chp6-p155-maria-first-love-of-louis-xiv",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第6章；印刷页155；OCR L106–107",
            "sentence_summary": (
                "Haskell 以 Maria Mancini 全名记载其于1661年与 Lorenzo Onofrio 结婚，"
                "并称她为 Cardinal Mazarin 的 niece 及 Louis XIV 的 first love。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 106",
                    "text": (
                        "In 1661, at the age of 24, he married Maria Mancini, the niece "
                        "of Cardinal Mazarin and the first love of Louis XIV."
                    ),
                },
                {
                    "source_span": "lines 106–107",
                    "text": (
                        "For some years, while she bore him son after son, she was one of the two "
                        "leading ladies in Roman society, rivalled only by Queen Christina of Sweden."
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 106–107; print p. 155",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第6章；印刷页156；OCR L116–117",
            "sentence_summary": (
                "Haskell 称 Lorenzo 在婚后数年同意妻子要求的 ‘separatione di letto’，"
                "并将她于1672年离开丈夫归因于 Lorenzo 的不忠。"
            ),
            "original_quotes": [
                {
                    "source_span": "lines 116–117",
                    "text": (
                        "Within a few years of his marriage he was compelled to agree to his wife’s "
                        "demand for a ‘separatione di letto’, and his reckless infidelities led to "
                        "her leaving him in 1672."
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 116–117; print p. 156",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；M.csv#46；印刷页155",
            "sentence_summary": "索引以 Mancini, Maria 形式列出人物，并定位第155页。",
            "original_quotes": [
                {
                    "source_span": "index entry M.csv#46",
                    "text": "| Mancini, Maria |  |  |  | 155 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX,
                "source_span": "index entry M.csv#46",
            },
        },
    ]
    frontmatter = {
        "title": "玛丽亚·曼奇尼（Maria Mancini）",
        "name_en": "Maria Mancini",
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

**中文：** Haskell 第6章以全名记载 Maria Mancini，称她为 Cardinal Mazarin 的侄辈女性亲属（niece；原文未说明具体亲属支系），并称她于1661年与 Lorenzo Onofrio Colonna 结婚。作者称她是 Louis XIV 的 first love，并描述她到罗马后的社会位置；第156页记其要求 ‘separatione di letto’，以及 Haskell 所述她于1672年离开丈夫。本卡只登记本书可支持的人物身份与叙述，不补出生、死亡、具体亲属支系或外部生平。[第6章 p.155](../../../{CHAPTER})（L106–107）；[第6章 p.156](../../../{CHAPTER})（L116–117）

**English:** Chapter 6 names Maria Mancini and calls her Cardinal Mazarin’s niece, without specifying the kinship line; Haskell says she married Lorenzo Onofrio Colonna in 1661. He also calls her Louis XIV’s first love and describes her social position after arriving in Rome. Page 156 records her demand for a ‘separatione di letto’ and Haskell’s account that she left her husband in 1672. This card registers only the identity and account supported by the book; it adds no birth or death dates, specific kinship line, or external biography. [Chapter 6, p.155](../../../{CHAPTER}) (L106–107); [Chapter 6, p.156](../../../{CHAPTER}) (L116–117)

### 名称

中文显示名“玛丽亚·曼奇尼”为原书姓名 Maria Mancini 的工作音译。第6章 p.155 L106 使用书内全名 Maria Mancini；索引 M.csv#46 以反序形式 Mancini, Maria 列出该人物。

The Chinese display name 玛丽亚·曼奇尼 is a working transliteration of the source name Maria Mancini. Chapter 6, p.155, L106, gives the full name Maria Mancini; index entry M.csv#46 lists the reversed form Mancini, Maria.

### 身份边界

本卡对应 Haskell 第6章的 Maria Mancini，不与同书其他 Mancini 人物按姓氏合并。原书称谓支持 “niece”，但未在此处说明具体亲属支系；本轮没有查阅外部身份记录，也不将 Haskell 的叙述写成独立核实的传记事实。

This card identifies the Maria Mancini named in Haskell’s Chapter 6 and does not merge her with other people named Mancini in the book. The source says “niece” but does not specify the kinship line. No external identity record was consulted, and Haskell’s account is not presented as independently verified biography.

## 关系与证据

7条直接 S2 `relation_candidate` 保留待 S6 裁决：`{', '.join(sorted(RELATION_CANDIDATES))}`。本轮未登记正式关系；候选与依据详见[知识处理记录](../../../03-processing/{TASK}/process/knowledge.md)。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Maria Mancini's S3 person group in S4.")
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
    candidate = candidate_by_id[CANDIDATE]
    alignment = alignment_by_id[CANDIDATE]
    assert candidate["index_entry_id"] == "M.csv#46"
    assert candidate["canonical_name"] == "Mancini, Maria"
    assert candidate["index_page_range"] == "155"
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
        or (row.get("type") == "person" and (row.get("name_en") or "").casefold() == "maria mancini")
        for row in manifest
    )
    card_path = ROOT / CARD_REL
    assert not card_path.exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted

    chapter = (ROOT / CHAPTER).read_text(encoding="utf-8-sig")
    index = (ROOT / INDEX).read_text(encoding="utf-8-sig")
    assert "In 1661, at the age of 24, he married Maria Mancini" in chapter
    assert "the niece of Cardinal Mazarin and the first love of Louis XIV" in chapter
    assert "Within a few years of his marriage he was compelled to agree to his wife’s demand" in chapter
    assert "her leaving him in" in chapter and "1672" in chapter
    assert "| Mancini, Maria |  |  |  | 155 |" in index
    assert len([row for row in mentions if row.get("candidate_id") == CANDIDATE]) == 4

    statements = sync.load_statements()
    direct_relation_ids = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relation_ids == RELATION_CANDIDATES, direct_relation_ids

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE)
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "玛丽亚·曼奇尼",
        "name_en": "Maria Mancini",
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
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1, "could not refresh the enrichment artifact count"
    audit_line = (
        "2026-10-17 strict-stage 表审计通过：`errors=[]`、`s2_missing=[]`。审计警告中的4,552条待登记 "
        "`decision=new` alignment 行，含4,537条候选决定映射（4,467组）和15条外部身份记录。另有两条既有字段来源引用未能从对应卡片source列表解析 "
        "（`enr-06678`、`enr-06937`）；相关字段仍保留原状态。审计还提示S2迁移的语义质量仍须按关联过程记录检查；结构一致性不代表独立语义验收，也不产生准确率、召回率或语义处理吞吐指标。"
    )
    result_text, n = re.subn(r"^\d{4}-\d{2}-\d{2} strict-stage 表审计通过：.*$", audit_line, result_text, count=1, flags=re.M)
    assert n == 1, "could not refresh the current audit summary"
    result_text += (
        "\n\n### S4 person：Maria Mancini 直接关系端点身份组（2026-10-17）\n\n"
        f"`cand-1509`（M.csv#46）按 S3 身份组 `{GROUP}` 登记至[玛丽亚·曼奇尼人物卡](../units/persons/maria-mancini.md)。"
        "索引反序全名对应第6章 p.155 的 Maria Mancini，p.156 的 wife/her 指代由同一段婚姻语境承接；本卡不与 Giulio Mancini 等同姓人物合并。"
        "仅记录 Haskell 对人物身份、婚姻和后续叙述的原书表述，不补具体亲属支系或外部生平。"
        f"7条直接 S2 关系候选保持待 S6，未新增正式关系或字段事实。S4 累计登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-maria-mancini\"></a>\n\n"
        "### S4 person：Maria Mancini 直接关系端点登记（2026-10-17）\n\n"
        f"候选 `{CANDIDATE}`（M.csv#46）保持 S3 `new` 身份组 `{GROUP}`，映射至[玛丽亚·曼奇尼人物卡](../../../{CARD_REL})；"
        "该组仅含此一条人物候选，同组登记一个 KU。第6章 p.155 L106 明称 Maria Mancini，交代她与 Lorenzo Onofrio 于1661年结婚，"
        "并称她是 Cardinal Mazarin 的 niece、Louis XIV 的 first love；p.155 L106–107 描述其抵达罗马后的社会处境。"
        "第6章 p.156 L116–117 记 Haskell 所述的 ‘separatione di letto’ 要求及她于1672年离开丈夫；书后索引 M.csv#46 以 Mancini, Maria 定位 p.155。"
        "原书称 niece，但未说明亲属支系；本卡不推定该支系，不补出生、死亡或外部生平。Giulio Mancini 等其他同姓人物保持分立。"
        "7条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。"
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
        print(f"S4 Maria Mancini dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"index=M.csv#46; mentions=4; relation_candidates={len(direct_relation_ids)}; no type/identity conflation")
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
