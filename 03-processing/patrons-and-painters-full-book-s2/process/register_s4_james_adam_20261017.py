from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_ottaviano_prati_20261017 as prati_sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-james-adam-source-local-group-20261017"
CANDIDATE = "cand-0011"
GROUP = "new-person:adam-james-24bd4e0e2f"
KU_ID = "units/persons/james-adam-venice"
CARD_REL = "04-knowledge/units/persons/james-adam-venice.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "詹姆斯·亚当"
NAME_EN = "James Adam"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CHAPTER_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
INDEX_FILE = "02-sources/02-Markdown/22_CHP-22Index_intro.md"
QUOTE_P302 = "James Adam burst out in a fit of rage"
QUOTE_P310 = "James Adam met him and wrote"
INDEX_QUOTE = "Adam, James"
RELATION_ID = "st-chp10-p302-james-adam-criticism"


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, ch. 10, p. 302.",
            "location": "第10章，印刷页302；OCR L392",
            "sentence_summary": "哈斯克尔在讨论 Joseph Smith 时点名 James Adam，并引出他对 Smith 逢迎言辞的批评。",
            "original_quotes": [
                {"source_span": "L392; print p. 302", "text": QUOTE_P302},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_FILE,
                "source_span": "L392; print p. 302",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 10, p. 310.",
            "location": "第10章，印刷页310；OCR L487–488",
            "sentence_summary": "哈斯克尔再次以 James Adam 全名指认一段关于 Joseph Smith 的转述，并引述其对 Smith 财务处境的看法。",
            "original_quotes": [
                {"source_span": "L487; print p. 310", "text": QUOTE_P310},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_FILE,
                "source_span": "L487–488; print p. 310",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后人名索引 A 项；OCR L28，印本索引页码未核准",
            "sentence_summary": "索引以倒置形式列名 Adam, James，并列出本书第302、310、392页。",
            "original_quotes": [
                {"source_span": "L28", "text": INDEX_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "L28",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔第10章 p.302、p.310 具名的 James Adam。两处均围绕 Joseph Smith 引述或转述 Adam 的话。此卡仅记录书内可追溯的人物身份，不补写外部生平。中文显示名为项目工作音译。

**English:** This card records James Adam, named on pp. 302 and 310 of Haskell’s chapter 10. Both passages quote or report Adam’s remarks about Joseph Smith. The card records the source-local person identity without adding an external biography. The Chinese display name is a project working transliteration.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 正文具名形式 / Name in text | James Adam | S1、S2 |
| 书后索引形式 / Index heading | Adam, James | S3 |

### 本章相关内容

**中文：** p.302 引述 James Adam 批评 Smith 的逢迎言辞；p.310 再次点名 Adam，并转述他对 Smith 财务状况的看法。相关引述保留为哈斯克尔的来源陈述，不写成独立核实的财务事实。

**English:** On p. 302 Haskell quotes James Adam criticizing Smith’s flattering language; on p. 310 he names Adam again and reports his view of Smith’s finances. These remain Haskell’s source-attributed statements, not independently verified financial facts.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

书内评价候选 `{RELATION_ID}` 留待 S6 裁决。

"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted_path(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register James Adam's source-local person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    if (
        CARD_PATH.exists()
        and CARD_REL in accepted_text
        and any(row.get("ku_id") == KU_ID for row in manifest)
        and decisions.get(CANDIDATE, {}).get("ku_id") == KU_ID
    ):
        print("ALREADY REGISTERED: James Adam source-local person group")
        return 0

    assert CANDIDATE in candidate_map and candidate_map[CANDIDATE].get("suggested_type") == "person"
    decision = decisions[CANDIDATE]
    assert decision.get("decision") == "new" and not decision.get("ku_id")
    assert sync.get_group(decision.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert candidate_map[CANDIDATE]["index_entry_id"] == "A.csv#10"
    assert candidate_map[CANDIDATE]["index_page_range"] == "302, 310, 392"
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English name already exists in manifest"

    chapter = (ROOT / CHAPTER_FILE).read_text(encoding="utf-8-sig")
    index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    appendix = (ROOT / "02-sources/02-Markdown/19_CHP-19Appendix.md").read_text(encoding="utf-8-sig")
    assert QUOTE_P302 in chapter and QUOTE_P310 in chapter
    assert "Adam, James, 302, 310, 392" in index
    assert "On 20 August 1760 James wrote to Robert Adam of Smith" in appendix
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    assert RELATION_ID in statements
    assert statements[RELATION_ID]["qualifiers"].get("relation_candidate") is True
    assert statements[RELATION_ID].get("subject_candidate_id") == CANDIDATE
    assert statements[RELATION_ID].get("object_candidate_id") == "cand-2440"
    assert decisions["cand-2440"].get("ku_id") == "units/persons/joseph-smith-venice"

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: source-local person group {GROUP} maps to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text = prati_sync.update_pending_warning(result_text, planned_alignment)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S4 person：James Adam 跨章书内人物组登记（{DATE}）

`cand-0011` 是单成员 S3 人物组 `{GROUP}`，索引主项 `A.csv#10` 合并页302、310、392。p.302 与 p.310 均以全名 James Adam 指认讨论 Joseph Smith 的说话者；p.302 注1与 p.310 注5涉及 1760 年 8 月20日的同一封 James 致 Robert Adam 信件，附录5 p.392 再引该信。现以本书内姓名、索引和相同书信锚点登记为[詹姆斯·亚当人物卡](../../../04-knowledge/units/persons/james-adam-venice.md)。信件原件和 Fleming 刊本均未独立查读；本次不据此确认外部身份或亲属关系。

`{RELATION_ID}` 保留为 James Adam 对 Joseph Smith 的书内评价候选，待 S6 裁决；不修改 `relations.csv`。p.310 的财务评价仍明确归于哈斯克尔转引，不登记为已核实事实。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 person：James Adam（{DATE}）\n\n"
        "索引 p.302、310、392 的单人组已登记；评论关系候选仍待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print("dry-run passed: cand-0011 is the sole member of its new-person S3 group")
        print("verified p.302/p.310 full-name anchors, the p.392 letter cross-reference, and the Joseph Smith relation candidate")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv unchanged")
        print("planned writes: one bilingual person card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: James Adam person group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
