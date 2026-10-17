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
import register_s4_ottaviano_prati_20261017 as prati_sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-prati-portrait-and-governorship-places-20261017"
SECTION_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
SECTION_QUOTE_PORTRAIT = "a signed portrait of Monsignor Ottaviano Prati"
SECTION_QUOTE_GALLERY = "In the Galleria N azionale di Arte Antica in Rome is a signed portrait of Monsignor Ottaviano Prati"
SECTION_QUOTE_GOVERNORSHIPS = "who at different times was Governor of Benevento and Viterbo"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = (
    {
        "candidate_id": "cand-6091",
        "group": "workgrp-18912bb6d0e607",
        "ku_id": "units/works/portrait-monsignor-ottaviano-prati",
        "type": "work",
        "canonical_name": "奥塔维亚诺·普拉蒂肖像",
        "name_en": "Portrait of Monsignor Ottaviano Prati",
        "card_path": "04-knowledge/units/works/portrait-monsignor-ottaviano-prati.md",
        "summary": "注3报告一幅 Monsignor Ottaviano Prati 的签名肖像，并记述其所在机构；未记原题、创作者或创作年代。",
        "quotes": (SECTION_QUOTE_PORTRAIT, SECTION_QUOTE_GALLERY),
        "statements": (
            "st-chp5-note-p131-n3-prati-portrait",
            "st-chp5-note-p131-n3-portrait-located-galleria",
        ),
    },
    {
        "candidate_id": "cand-6093",
        "group": "sg3-place-cand-6093",
        "ku_id": "units/places/benevento",
        "type": "place",
        "canonical_name": "贝内文托",
        "name_en": "Benevento",
        "card_path": "04-knowledge/units/places/benevento.md",
        "summary": "注3称 Ottaviano Prati 曾在不同时期任 Benevento 总督，但未给任职年代或管辖范围。",
        "quotes": (SECTION_QUOTE_GOVERNORSHIPS,),
        "statements": ("st-chp5-note-p131-n3-prati-governor-benevento",),
    },
    {
        "candidate_id": "cand-6094",
        "group": "sg3-place-cand-6094",
        "ku_id": "units/places/viterbo",
        "type": "place",
        "canonical_name": "维泰博",
        "name_en": "Viterbo",
        "card_path": "04-knowledge/units/places/viterbo.md",
        "summary": "注3称 Ottaviano Prati 曾在不同时期任 Viterbo 总督，但未给任职年代或管辖范围。",
        "quotes": (SECTION_QUOTE_GOVERNORSHIPS,),
        "statements": ("st-chp5-note-p131-n3-prati-governor-viterbo",),
    },
)


def make_source(target: dict) -> dict:
    return {
        "citation": f"{BOOK_CITATION}, ch. 5, p. 131, n. 3.",
        "location": "第5章第一节，印刷页131注3；OCR L147",
        "sentence_summary": target["summary"],
        "original_quotes": [
            {"source_span": "L147; print p. 131 n. 3", "text": quote}
            for quote in target["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SECTION_FILE,
            "source_span": "L147; print p. 131 n. 3",
        },
    }


def make_card(target: dict) -> str:
    frontmatter = {
        "title": f"{target['canonical_name']}（{target['name_en']}）",
        "name_en": target["name_en"],
        "type": target["type"],
        "evidence_status": "source_backed",
        "sources": [make_source(target)],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    if target["type"] == "work":
        body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔第5章 p.131 注3所报告的 Monsignor Ottaviano Prati 签名肖像。卡片题名依据原文描述拟定，不是原题；注释未给创作者或创作年代。

**English:** This card records the signed portrait of Monsignor Ottaviano Prati reported in footnote 3 on p. 131 of Haskell’s chapter 5. The card title is descriptive, not an original title; the note gives no artist or date.

### 题名

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性题名 / Descriptive title | 奥塔维亚诺·普拉蒂肖像（Portrait of Monsignor Ottaviano Prati） | S1 |
| 题名性质 / Title status | 项目描述性暂题；原题未载 / Project descriptive title; original title not stated | S1 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作品类型 / Work type | 签名肖像 / Signed portrait | S1 |
| 署名者 / Signatory | 本注未说明 / Not identified in this note | S1 |

### 本章相关内容

**中文：** 哈斯克尔注3称这幅肖像位于罗马 Galleria Nazionale di Arte Antica。该位置是书中转述，未据此声称已核验现藏；注释也未提供作品原题、作者或年代。原 OCR 将馆名写作 “Galleria N azionale”；据 S2 校勘记录，正文使用规范拼写。

**English:** Haskell’s footnote 3 reports the portrait at Rome’s Galleria Nazionale di Arte Antica. This is the book’s report and does not establish present custody. The note supplies no original title, artist, or date. The OCR reads “Galleria N azionale”; the normalized spelling follows the S2 correction record.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

以下书内关系候选留待 S6 逐项裁决：

- `st-chp5-note-p131-n3-prati-portrait`
- `st-chp5-note-p131-n3-portrait-located-galleria`

"""
    else:
        chinese = "贝内文托" if target["name_en"] == "Benevento" else "维泰博"
        statement_id = target["statements"][0]
        body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔第5章 p.131 注3提及的地点 {target['name_en']}。该注将其列为 Ottaviano Prati 曾任总督的地点之一，但未提供任职年代或管辖范围。中文显示名为项目工作音译。

**English:** This card records {target['name_en']}, named in footnote 3 on p. 131 of Haskell’s chapter 5 as one place where Ottaviano Prati served as governor at different times. The note gives no appointment dates or jurisdictional extent. The Chinese display name is a project working transliteration.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 来源中的名称 / Name in source | {target['name_en']} | S1 |

### 本章相关内容

**中文：** 注3记述 Ottaviano Prati 曾在不同时期任 {target['name_en']} 总督；具体时间和所辖空间范围未载。

**English:** Footnote 3 says that Ottaviano Prati served as governor of {target['name_en']} at different times; it does not specify the dates or jurisdictional extent.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

书内任职候选 `{statement_id}` 留待 S6 裁决。

"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted_paths(text: str, card_paths: list[str]) -> str:
    lines = text.splitlines()
    for card_path in sorted(card_paths):
        assert f"- {card_path}" not in lines, f"accepted entry already exists: {card_path}"
        insert_at = next(
            (
                i for i, line in enumerate(lines)
                if line.startswith("- 04-knowledge/units/") and line[2:] > card_path
            ),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_path}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three direct S2 relation endpoint groups in S4.")
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

    if all(
        (ROOT / target["card_path"]).exists()
        and f"- {target['card_path']}" in accepted_text.splitlines()
        and any(row.get("ku_id") == target["ku_id"] for row in manifest)
        and decisions.get(target["candidate_id"], {}).get("ku_id") == target["ku_id"]
        for target in TARGETS
    ):
        print("ALREADY REGISTERED: Prati portrait and governorship place groups")
        return 0

    source_text = (ROOT / SECTION_FILE).read_text(encoding="utf-8-sig")
    assert SECTION_QUOTE_PORTRAIT in source_text
    assert SECTION_QUOTE_GALLERY in source_text
    assert SECTION_QUOTE_GOVERNORSHIPS in source_text
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    planned_alignment = [dict(row) for row in alignments]
    for target in TARGETS:
        cid = target["candidate_id"]
        assert cid in candidate_map and candidate_map[cid].get("suggested_type") == target["type"]
        assert candidate_map[cid].get("candidate_source_ref", "").endswith("#L147")
        decision = decisions[cid]
        assert decision.get("decision") == "new" and not decision.get("ku_id")
        assert sync.get_group(decision.get("resolution_note", "")) == target["group"]
        group_rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == target["group"]
        ]
        assert [row["candidate_id"] for row in group_rows] == [cid]
        assert not (ROOT / target["card_path"]).exists(), f"card path exists: {target['card_path']}"
        assert target["card_path"] not in accepted_text
        assert not any(row.get("ku_id") == target["ku_id"] or row.get("card_path") == target["card_path"] for row in manifest)
        assert not any(
            row.get("type") == target["type"]
            and (row.get("name_en", "").casefold() == target["name_en"].casefold()
                 or row.get("canonical_name") == target["canonical_name"])
            for row in manifest
        ), f"same name already exists in manifest: {target['ku_id']}"
        assert all(sid in statements and statements[sid]["qualifiers"].get("relation_candidate") is True for sid in target["statements"])
        for row in planned_alignment:
            if row.get("candidate_id") == cid and not row.get("external_source"):
                row["ku_id"] = target["ku_id"]
                row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
                row["resolution_note"] += f" S4 registration: group {target['group']} maps to {target['ku_id']}."

    planned_manifest = list(manifest) + [
        {
            "ku_id": target["ku_id"],
            "type": target["type"],
            "canonical_name": target["canonical_name"],
            "name_en": target["name_en"],
            "source_task": TASK,
            "card_path": target["card_path"],
        }
        for target in TARGETS
    ]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text = prati_sync.update_pending_warning(result_text, planned_alignment)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S4 work/place：Prati 签名肖像及两处总督任职地点直接端点登记（{DATE}）

按三组现有 S3 `new` 决定登记：`cand-6091`（`{TARGETS[0]['group']}`）→ [奥塔维亚诺·普拉蒂肖像](../../../04-knowledge/units/works/portrait-monsignor-ottaviano-prati.md)；`cand-6093`（`{TARGETS[1]['group']}`）→ [贝内文托](../../../04-knowledge/units/places/benevento.md)；`cand-6094`（`{TARGETS[2]['group']}`）→ [维泰博](../../../04-knowledge/units/places/viterbo.md)。

第5章 p.131 注3提供签名肖像及两个任职地点的书内锚点。肖像卡采用项目描述性暂题，不推定作者、原题或年代；地点卡只保留书内地名及任职语境，不补任期或辖区。中文地名是项目工作音译。所有卡均有双语描述及原文来源定位。

`st-chp5-note-p131-n3-prati-portrait`、`st-chp5-note-p131-n3-portrait-located-galleria`、`st-chp5-note-p131-n3-prati-governor-benevento` 与 `st-chp5-note-p131-n3-prati-governor-viterbo` 仍是 S2 关系候选，留待 S6；本次不写入 `relations.csv`。未做外部身份核验或 S5 字段补足。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 work/place：Prati 肖像与任职地点（{DATE}）\n\n"
        "三个直接关系端点组已登记为一张作品卡与两张地点卡；S2 关系候选仍待 S6，`relations.csv` 未修改。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_paths(accepted_text, [target["card_path"] for target in TARGETS])
    card_contents = [(ROOT / target["card_path"], make_card(target)) for target in TARGETS]

    if args.dry_run:
        print("dry-run passed: three single-candidate S3 groups, source anchors, and four direct relation-candidate statements verified")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv unchanged")
        print("planned writes: one work card, two place cards, accepted.yml, ku-manifest.csv, three alignment mappings, process record, result")
        return 0

    for card_path, content in card_contents:
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: 3 endpoint groups registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
