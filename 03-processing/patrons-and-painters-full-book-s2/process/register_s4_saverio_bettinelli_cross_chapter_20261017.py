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
ANCHOR = "s4-saverio-bettinelli-cross-chapter-20261017"
CANDIDATES = ("cand-0369", "cand-0370")
GROUP = "new-person:bettinelli-saverio-9ac59400eb"
KU_ID = "units/persons/saverio-bettinelli"
CARD_REL = "04-knowledge/units/persons/saverio-bettinelli.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "萨韦里奥·贝蒂内利"
NAME_EN = "Saverio Bettinelli"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CHAPTER_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
INDEX_FILE = "02-sources/02-Markdown/22_CHP-22Index_intro.md"
NAME_QUOTE = "here Saverio Bettinelli exploded"
QUOTE_START = "I have never seen a scientific or important book more luxuriously produced."
INDEX_QUOTE = "Bettinelli, Saverio"
RELATION_IDS = (
    "st-chp13-p333-anonymous-quotation-on-poem-collections",
    "st-chp13-p334-bettinelli-criticized-opulent-poem-collection",
)


def make_card() -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, ch. 13, p. 334.",
            "location": "第13章，印刷页334；OCR L22–24",
            "sentence_summary": "哈斯克尔在讨论仪式纪念诗集的制作费用时点名 Saverio Bettinelli，并引出他的评价。",
            "original_quotes": [
                {"source_span": "L22; print p. 334", "text": NAME_QUOTE},
                {"source_span": "L23; print p. 334", "text": QUOTE_START},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_FILE,
                "source_span": "L22–24; print p. 334",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后人名索引 B 项；OCR L499，印本索引页码未核准",
            "sentence_summary": "索引以倒置形式列名 Bettinelli, Saverio，并注明本书第320、334页。",
            "original_quotes": [
                {"source_span": "L499", "text": INDEX_QUOTE},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "L499",
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

**中文：** 本卡记录哈斯克尔第13章印刷页334正文中具名的 Saverio Bettinelli。该段在论述仪式纪念诗集的出版时，引出 Bettinelli 对一本精印书籍的评价。中文显示名为项目工作音译。

**English:** This card records Saverio Bettinelli, named in the text on p. 334 of Haskell’s chapter 13. In a discussion of publishing ceremonial verse collections, Haskell introduces Bettinelli’s comment on an elaborately produced book. The Chinese display name is a project working transliteration.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 正文具名形式 / Name in text | Saverio Bettinelli | S1 |
| 书后索引形式 / Index heading | Bettinelli, Saverio | S2 |

### 本章相关内容

**中文：** 第13章 p.333–334 讨论用于仪式纪念的诗集及其出版。p.334 以 “here Saverio Bettinelli exploded” 引出一段评价。此卡保留原书对发言者的归属，不把评价写成客观质量判断。

**English:** Chapter 13, pp. 333–334 discusses collections of verse published for ceremonies. On p. 334, Haskell introduces a comment with “here Saverio Bettinelli exploded.” The card preserves the source’s attribution and does not treat the comment as an objective quality judgment.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

以下书内关系候选留待 S6 逐项裁决：

- `{RELATION_IDS[0]}`
- `{RELATION_IDS[1]}`

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
    parser = argparse.ArgumentParser(description="Register the Saverio Bettinelli cross-chapter person group in S4.")
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
        and all(decisions.get(cid, {}).get("ku_id") == KU_ID for cid in CANDIDATES)
    ):
        print("ALREADY REGISTERED: Saverio Bettinelli cross-chapter person group")
        return 0

    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold() or row.get("canonical_name") == NAME_ZH)
        for row in manifest
    ), "same person already exists in manifest"

    group_rows = []
    for cid in CANDIDATES:
        assert cid in candidate_map and candidate_map[cid].get("suggested_type") == "person"
        row = decisions[cid]
        assert row.get("decision") == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == GROUP
        group_rows.append(row)
    actual_group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert actual_group_members == set(CANDIDATES)
    assert candidate_map[CANDIDATES[0]]["index_entry_id"] == "B.csv#216"
    assert candidate_map[CANDIDATES[1]]["index_entry_id"] == "B.csv#217"
    assert candidate_map[CANDIDATES[1]]["sub_entry"] == "Dell'entusiasmo per le Belle Arti"

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "Bettinelli, Saverio, 320, 334" in index_text
    assert "Dell’entusiasmo per le Belle Arti, 320" in index_text
    chapter13 = (ROOT / CHAPTER_FILE).read_text(encoding="utf-8-sig")
    assert NAME_QUOTE in chapter13 and QUOTE_START in chapter13
    chapter10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_sec_ii.md").read_text(encoding="utf-8-sig")
    assert "Saverio Bettinelli’s Delientusiasmo per le Belle Arti (Milan, 1769)" in chapter10

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    assert all(
        sid in statements and statements[sid]["qualifiers"].get("relation_candidate") is True
        and any(cid in (statements[sid].get("subject_candidate_id"), statements[sid].get("object_candidate_id")) for cid in CANDIDATES)
        for sid in RELATION_IDS
    )

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: cross-chapter identity group {GROUP} maps both index candidates to one KU, {KU_ID}."

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

### S4 person：Saverio Bettinelli 跨章身份组登记（{DATE}）

跨章身份组 `{GROUP}` 含两条 S3 `new` 候选：`cand-0369` 是索引主项 `B.csv#216`（索引列 p.320、334），`cand-0370` 是同名主项下的子目 `B.csv#217`（`Dell'entusiasmo per le Belle Arti`，p.320）。第13章 p.334 正文以完整姓名 “Saverio Bettinelli” 点名发言者；书后索引以倒置姓名列主项。两候选据此登记到同一张[萨韦里奥·贝蒂内利人物卡](../../../04-knowledge/units/persons/saverio-bettinelli.md)。这只裁决人物身份，不将索引子目题名登记为作品，也未作外部身份核验。

`{RELATION_IDS[0]}` 与 `{RELATION_IDS[1]}` 是人物对仪式纪念诗集的书内评论／评价关系候选，均留待 S6；未修改 `relations.csv`。卡片记录第13章 p.334 正文及全书索引的姓名证据，不扩写人物生平。未进行 S5 外部字段核验。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 person：Saverio Bettinelli 跨章身份组（{DATE}）\n\n"
        "两个索引候选合并映射到一张人物卡；两条第13章书内关系候选仍待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print("dry-run passed: two cross-chapter index candidates form one person group with a full-name p.334 anchor")
        print("verified the p.320 and p.334 source/index anchors and two pending S2 relation candidates")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv unchanged")
        print("planned writes: one bilingual person card, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Bettinelli cross-chapter group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
