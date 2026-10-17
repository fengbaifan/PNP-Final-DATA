from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-john-vanbrugh-person-20261017"
CANDIDATE = "cand-2690"
GROUP = "new-person:john-vanbrugh-c177249729"
KU_ID = "units/persons/sir-john-vanbrugh"
CARD_REL = "04-knowledge/units/persons/sir-john-vanbrugh.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "约翰·范布勒爵士"
NAME_EN = "Sir John Vanbrugh"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CHAPTER_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
INDEX_FILE = "02-sources/02-Markdown/22_CHP-22Index_intro.md"
QUOTES = (
    "their great country houses built for them by the gentleman-architect Vanbrugh",
    "decorate his mansions in Arlington Street and at Kimbolton in Huntingdonshire, rebuilt for him by Vanbrugh.",
    "The same architect had for some years been erecting in Yorkshire a country house as palatial as any German imitation of Versailles for Lord Carlisle",
    "one—curiously enough—by Vanbrugh, though the example chosen shows him at his most Palladian.",
    "Vanbrugh, Sir John, 278-9, 309",
)
RELATION_IDS = (
    "st-chp10-p278-vanbrugh-built-friends-country-houses",
    "st-chp10-p279-vanbrugh-carlisle-castle-howard",
    "st-chp10-p309-one-picture-after-vanbrugh",
)


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, ch. 10, p. 278.",
            "location": "第10章，印刷页278；OCR L34–35",
            "sentence_summary": "哈斯克尔称 Vanbrugh 为 gentleman-architect，并将 Manchester、Carlisle 等人的乡间住宅建造归于他。",
            "original_quotes": [{"source_span": "L34–35; print p. 278", "text": QUOTES[0]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_FILE,
                "source_span": "L34–35; print p. 278",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 10, p. 279.",
            "location": "第10章，印刷页279；OCR L44",
            "sentence_summary": "哈斯克尔以“同一位建筑师”承接 Vanbrugh，记述曼彻斯特的两处宅邸及 Lord Carlisle 的约克郡乡间住宅。",
            "original_quotes": [
                {"source_span": "L44; print p. 279", "text": QUOTES[1]},
                {"source_span": "L44; print p. 279", "text": QUOTES[2]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_FILE,
                "source_span": "L44; print p. 279",
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 10, p. 309.",
            "location": "第10章，印刷页309；OCR L470",
            "sentence_summary": "哈斯克尔在一组建筑图像中提到一幅表现 Vanbrugh 作品的图像，并对所选实例作风格评价。",
            "original_quotes": [{"source_span": "L470; print p. 309", "text": QUOTES[3]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_FILE,
                "source_span": "L470; print p. 309",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后人名索引 V 项；OCR L3319，印本索引页码未核准",
            "sentence_summary": "书后索引以完整倒置形式列名 Vanbrugh, Sir John，并列本书第278–279、309页。",
            "original_quotes": [{"source_span": "L3319", "text": QUOTES[4]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "L3319",
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
    pending = "\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    body = f"""## 内容

### 描述

**中文：** 本卡记录《赞助人与画家》第10章及书后索引所指的建筑师 Vanbrugh。正文称他为 gentleman-architect，并在 p.279 以“同一位建筑师”延续叙述；索引将其全名列作 “Vanbrugh, Sir John”。此卡只登记本书内身份，不补写外部生平。中文显示名为项目工作音译。

**English:** This card records the architect Vanbrugh named in chapter 10 and the book’s index. The prose calls him a “gentleman-architect” and continues the reference on p. 279 as “the same architect”; the index gives the full heading “Vanbrugh, Sir John.” This card records the source-local identity without adding an external biography. The Chinese display name is a project working transliteration.

### 名称

| 字段 | 值 | 依据 |
|---|---|---|
| 正文具名形式 / Name in text | Vanbrugh | 第10章，印刷页278；S1 |
| 建筑师身份 / Identity as architect | gentleman-architect（哈斯克尔原文称谓） | 第10章，印刷页278；S1 |
| 书后索引形式 / Index heading | Vanbrugh, Sir John | OCR L3319；S4 |
| 正文具名形式（p.279） / Name in text (p. 279) | Vanbrugh | 第10章，印刷页279；S2 |
| 正文具名形式（p.309） / Name in text (p. 309) | Vanbrugh | 第10章，印刷页309；S3 |

### 本章相关内容

**中文：** 第10章 p.278 将 Vanbrugh 与 Manchester、Carlisle 等人的乡间住宅建造联系起来。p.279 记述曼彻斯特的宅邸由他重建，并称“同一位建筑师”曾为 Lord Carlisle 在约克郡营建乡间住宅；同页后文提到 Castle Howard，但本卡不据相邻叙述消解该住宅与地名候选之间仍待核的映射。p.309 又在建筑图像清单中提到一幅表现 Vanbrugh 作品的图像。以上均为哈斯克尔的书内叙述，不作为独立核实的建筑史事实。

**English:** On p. 278, Haskell associates Vanbrugh with the country houses of Manchester, Carlisle, and others. On p. 279, he says Manchester’s mansions were rebuilt by Vanbrugh and that “the same architect” had been erecting a country house for Lord Carlisle in Yorkshire. Castle Howard is named later on that page, but this card does not resolve the still-pending mapping between the house description and the place candidate from adjacent prose. On p. 309, Haskell also mentions an image representing a work by Vanbrugh. These are Haskell’s source-local statements, not independently verified architectural history.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

以下书内关系候选留待 S6 逐项裁决：

{pending}
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
    parser = argparse.ArgumentParser(description="Register the John Vanbrugh person group in S4.")
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
    assert candidate_map[CANDIDATE]["index_entry_id"] == "UVWXYZ.csv#26"
    assert candidate_map[CANDIDATE]["index_page_range"] == "278, 279, 309"
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English name already exists in manifest"

    chapter = (ROOT / CHAPTER_FILE).read_text(encoding="utf-8-sig")
    index = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert all(quote in chapter for quote in QUOTES[:4])
    assert QUOTES[4] in index
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    expected_endpoints = {
        RELATION_IDS[0]: "subject_candidate_id",
        RELATION_IDS[1]: "subject_candidate_id",
        RELATION_IDS[2]: "object_candidate_id",
    }
    for sid, endpoint in expected_endpoints.items():
        statement = statements[sid]
        assert statement["qualifiers"].get("relation_candidate") is True
        assert statement.get(endpoint) == CANDIDATE

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
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S4 person：Sir John Vanbrugh 书内人物组登记（{DATE}）

`cand-2690` 是单成员 S3 人物组 `{GROUP}`，对应书后索引主项 `UVWXYZ.csv#26`（pp.278–279、309）。正文 p.278 将 Vanbrugh 称为 gentleman-architect；p.279 以 “The same architect” 延续指称；书后索引以倒置全名 “Vanbrugh, Sir John” 列项。无同名既有人物 KU，故将该书内身份登记为[约翰·范布勒爵士人物卡](../../../04-knowledge/units/persons/sir-john-vanbrugh.md)。本次不引入外部生平或身份来源。

`st-chp10-p278-vanbrugh-built-friends-country-houses`、`st-chp10-p279-vanbrugh-carlisle-castle-howard` 与 `st-chp10-p309-one-picture-after-vanbrugh` 保留为 S2 关系候选，留待 S6；未修改 `relations.csv`。p.279 后文出现的 Castle Howard 不用于本次解决尚待核的住宅／地点候选映射。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 person：Sir John Vanbrugh（{DATE}）\n\n"
        "单成员索引人物组登记为来源内人物 KU；3条关系候选及相邻住宅／地点映射仍待后续裁决。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print("dry-run passed: cand-2690 is the sole member of its new-person S3 group")
        print("verified p.278/p.279/p.309 prose, the full indexed name, and all three relation-candidate endpoints")
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
    print(f"applied: Sir John Vanbrugh person group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
