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
ANCHOR = "s4-giovanni-adamo-20261017"
CANDIDATE = "cand-0016"
GROUP = "new-person:adamo-giovanni-15d8ae3b24"
KU_ID = "units/persons/giovanni-adamo"
CARD_REL = "04-knowledge/units/persons/giovanni-adamo.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "乔瓦尼·阿达莫"
NAME_EN = "Giovanni Adamo"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SECTION_FILE = "02-sources/02-Markdown/01_CHP-1_sec_ii.md"
INDEX_FILE = "02-sources/02-Markdown/22_CHP-22Index_intro.md"
NAME_QUOTE = "another patron, Giovanni Adamo"
COMMISSION_QUOTE = "when commissioning a work from the"
ARTIST_QUOTE = "Genoese painter Paolo Girolamo Piola"
INSTRUCTION_QUOTE = "I leave it to you whether to make it sacred or profane, with men or with women"
RELATION_ID = "st-chp1-secii-l40-46-09"


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, ch. 1, p. 10.",
            "location": "第1章第二节，印刷页10；OCR L43–45",
            "sentence_summary": "哈斯克尔称 Giovanni Adamo 为一位赞助人，并记述其委托 Paolo Girolamo Piola 创作一件未具名作品，说明尺寸而将题材选择留给画家。",
            "original_quotes": [
                {"source_span": "L43; print p. 10", "text": NAME_QUOTE},
                {"source_span": "L43–44; print p. 10", "text": COMMISSION_QUOTE},
                {"source_span": "L44; print p. 10", "text": ARTIST_QUOTE},
                {"source_span": "L45; print p. 10", "text": INSTRUCTION_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SECTION_FILE,
                "source_span": "L43–45; print p. 10",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后人名索引 A 项；OCR L34，印本索引页码未核准",
            "sentence_summary": "索引以倒置形式列名 Adamo, Giovanni，并注明本书第10页。",
            "original_quotes": [
                {"source_span": "L34", "text": "Adamo, Giovanni"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "L34",
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

**中文：** 本卡记录哈斯克尔第1章 p.10 具名的 Giovanni Adamo。该段称他为一位赞助人，并记述他委托 Paolo Girolamo Piola 创作一件未具名作品，给出尺寸而将题材选择留给画家。中文显示名为项目工作音译。

**English:** This card records Giovanni Adamo, named on p. 10 of Haskell’s chapter 1. The passage calls him a patron and says he commissioned an unnamed work from Paolo Girolamo Piola, specifying its size while leaving the subject to the painter. The Chinese display name is a project working transliteration.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 正文具名形式 / Name in text | Giovanni Adamo | S1 |
| 书后索引形式 / Index heading | Adamo, Giovanni | S2 |

### 本章相关内容

**中文：** 哈斯克尔记述 Adamo 允许 Piola 自行选择作品题材，可以是宗教或世俗主题，人物可为男性或女性。来源未给作品题名、具体题材或委托日期；这条委托仍是书内关系候选。

**English:** Haskell says Adamo left Piola to choose the work’s subject, sacred or profane and with male or female figures. The source gives no title, specific subject, or commission date; the commission remains a book-level relation candidate.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

书内委托候选 `{RELATION_ID}` 留待 S6 裁决；本卡不将未具名作品另立为知识元。

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
    parser = argparse.ArgumentParser(description="Register Giovanni Adamo's direct relation endpoint in S4.")
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
        print("ALREADY REGISTERED: Giovanni Adamo person group")
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
    assert candidate_map[CANDIDATE]["index_entry_id"] == "A.csv#15"
    assert candidate_map[CANDIDATE]["index_page_range"] == "10"
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold() or row.get("canonical_name") == NAME_ZH)
        for row in manifest
    ), "same person already exists in manifest"

    passage = (ROOT / SECTION_FILE).read_text(encoding="utf-8-sig")
    index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert NAME_QUOTE in passage and COMMISSION_QUOTE in passage and ARTIST_QUOTE in passage and INSTRUCTION_QUOTE in passage
    assert "Adamo, Giovanni, 10" in index
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    assert RELATION_ID in statements
    assert statements[RELATION_ID]["qualifiers"].get("relation_candidate") is True
    assert statements[RELATION_ID].get("subject_candidate_id") == CANDIDATE
    assert statements[RELATION_ID].get("object_candidate_id") == "cand-1935"

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

### S4 person：Giovanni Adamo 直接关系端点登记（{DATE}）

`cand-0016` 是单成员 S3 人物组 `{GROUP}`。第1章 p.10 正文以 “Giovanni Adamo” 具名，书后 A 项索引以倒置形式列名，均指向同一书内人物身份；现登记为[乔瓦尼·阿达莫人物卡](../../../04-knowledge/units/persons/giovanni-adamo.md)。未作外部身份核验。

`{RELATION_ID}` 记录 Adamo 委托 Paolo Girolamo Piola 创作一件未具名作品并将题材选择留给画家的书内断言，仍留待 S6；不写入 `relations.csv`，不为未具名作品另建 KU。没有据此扩展人物生平或作品清单。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 person：Giovanni Adamo（{DATE}）\n\n"
        "单成员人物组已登记；未具名作品及委托关系保持待 S6 裁决。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print("dry-run passed: cand-0016 is the sole member of its new-person S3 group")
        print("verified the p.10 source passage, index name form, existing Piola KU, and direct S2 relation candidate")
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
    print(f"applied: Giovanni Adamo person group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
