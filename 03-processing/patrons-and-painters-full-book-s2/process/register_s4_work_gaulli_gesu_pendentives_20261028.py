from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
RELATIONS_PATH = TABLES / "relations.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

CANDIDATE = "cand-5271"
WORK_GROUP = "workgrp-d7414b802d0064"
WORK_KU = "units/works/gaulli-gesu-dome-pendentive-figures"
WORK_CARD_REL = f"04-knowledge/{WORK_KU}.md"
WORK_CARD = ROOT / WORK_CARD_REL
ANCHOR = "s4-s5-s6-chp3-p83-gaulli-gesu-pendentive-figures-20261028"
RELATION_ID = "rel-2473"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 3, p. 83."
)
STATEMENT_DESIGN = "st-chp3-seciv-l69-73-gaulli-four-figures-in-pendentives"
STATEMENT_OLIVA = "st-chp3-seciv-l69-73-oliva-added-judges"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    encoding = "utf-8-sig" if path.read_bytes().startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha1(value.encode('utf-8')).hexdigest()[:16]}"


def card_text() -> str:
    frontmatter = {
        "title": "耶稣堂穹顶穹隅人物组（Figure Group in the Gesù Dome Pendentives）",
        "name_en": "Figure Group in the Gesù Dome Pendentives",
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第3章，印刷页83 L70；PDF物理页25。",
                "sentence_summary": (
                    "Haskell先说明Oliva选择穹隅图像群组，再称艺术家解决了在单一穹隅安排四个可辨人物的构图问题。"
                ),
                "original_quotes": [
                    {
                        "source_span": "Chapter 3, printed p. 83, line 70; PDF physical p. 25",
                        "text": (
                            "Oliva decided that he would include all three and add to them a group which had not "
                            "hitherto been represented, the Judges. With miraculous ease the artist solved the "
                            "problems posed by presenting four figures in a single pendentive and made them sweeping "
                            "enough to fit in with his grandiose patterns, yet sufficiently individualised to be easily "
                            "recognisable and never monotonous."
                        ),
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "Chapter 3, printed p. 83, line 70; PDF physical p. 25",
                },
            }
        ],
        "created": "2026-10-28",
        "updated": "2026-10-28",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = "[第3章 p.83](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L70；PDF物理页25）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录 Haskell 在讨论耶稣堂穹顶穹隅图像时所述的人物组。作者称 Oliva 决定采用惯常图像群组并加入一组此前未在该处表现的图像；随后将单一穹隅中四个人物的构图解决方案归于 Gaulli。此卡只表示 Haskell 所述的穹隅人物组，不推定整座穹顶的总人物数，也不补出个体身份。{source}

**English:** This card records the figure group discussed by Haskell in connection with the Gesù dome pendentives. He says Oliva chose the customary iconographic groups and added a further group not previously represented in that setting; he then attributes the compositional solution for presenting four figures in a single pendentive to Gaulli. This card represents Haskell’s source-defined pendentive group; it does not infer the total number of figures across the dome or identify individual figures. {source}

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性名称 | 耶稣堂穹顶穹隅人物组（Figure Group in the Gesù Dome Pendentives）；描述性暂题，非原题 | S1；第3章，印刷页83 L70 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作品类型 | 穹顶穹隅人物构图组；按来源的群组粒度登记 | S1；第3章，印刷页83 L70 |
| 对象范围 | Haskell说明在单一穹隅中呈现四个人物；原文未给整座穹顶的总人物数或个体名单 | S1；第3章，印刷页83 L70 |
| 来源所述职责 | Oliva决定图像群组；Gaulli解决四个人物在单一穹隅中的构图呈现。此处不把两种职责合并为同一角色 | S1；第3章，印刷页83 L70 |

## 关系与证据

### 关系记录

Gaulli 的来源限定设计归属见 `relations.csv` 正式记录；Oliva 的图像主题选择陈述保留在本卡与原书 statement 中，未转换为不精确的设计或委托关系。

### S3 身份组

- 候选：`{CANDIDATE}`
- S3决定：`new`；身份组 `{WORK_GROUP}`
- 书内来源：第3章，印刷页83 L70；PDF物理页25
- S4 KU：`{WORK_KU}`

### 对象边界

本卡不同于整项耶稣堂穹顶与拱顶装饰委托、穹顶《双重代求》中心构图，以及中殿窗龛中的十六尊灰泥像；不将这些不同粒度或不同空间对象合并。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the S3 work group for the Gesù dome pendentive figures.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    relation_fields, relations = read_csv(RELATIONS_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    alignment = [row for row in alignments if row["candidate_id"] == CANDIDATE and not row["external_source"]]
    assert len(alignment) == 1
    alignment_row = alignment[0]
    assert alignment_row["alignment_id"] == "aln-5454"
    assert alignment_row["decision"] == "new" and not alignment_row["ku_id"]
    assert f"group={WORK_GROUP}" in alignment_row["resolution_note"]
    assert candidate["suggested_type"] == "work"
    assert candidate["candidate_source_ref"] == "chp-3:03_CHP-3_sec_iv:l69-73#L70"
    assert not any(row["ku_id"] == WORK_KU or row["card_path"] == WORK_CARD_REL for row in manifest)
    assert not WORK_CARD.exists()
    assert not any(row["subject_ku_id"] == WORK_KU or row["object_ku_id"] == WORK_KU for row in relations)
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted = yaml.safe_load(accepted_text)
    assert WORK_CARD_REL not in accepted["units"]
    assert RELATION_ID not in {row["relation_id"] for row in relations}

    statement_rows = {
        row["statement_id"]: row
        for row in (json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip())
    }
    design_statement = statement_rows[STATEMENT_DESIGN]
    oliva_statement = statement_rows[STATEMENT_OLIVA]
    assert design_statement["subject_candidate_id"] == "cand-1117"
    assert design_statement["object_candidate_id"] == CANDIDATE
    assert design_statement["qualifiers"]["relation_candidate"] is True
    assert oliva_statement["subject_candidate_id"] == "cand-1771"
    assert oliva_statement["object_candidate_id"] == CANDIDATE
    assert oliva_statement["qualifiers"]["relation_candidate"] is True
    for statement_id in (STATEMENT_DESIGN, STATEMENT_OLIVA):
        assert not any(statement_id in row["source_span"] for row in relations)

    enrichment_lines = ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines()
    enrichment_rows = [json.loads(line) for line in enrichment_lines if line.strip()]
    assert not any(row.get("ku_id") == WORK_KU for row in enrichment_rows)
    next_enrichment = max(int(row["enrichment_id"].split("-")[1]) for row in enrichment_rows) + 1
    fields = [
        ("描述性名称", "耶稣堂穹顶穹隅人物组（Figure Group in the Gesù Dome Pendentives）；描述性暂题，非原题", "内容 / 名称"),
        ("作品类型", "穹顶穹隅人物构图组；按来源的群组粒度登记", "内容 / 基本信息"),
        ("对象范围", "Haskell说明在单一穹隅中呈现四个人物；原文未给整座穹顶的总人物数或个体名单", "内容 / 基本信息"),
        ("来源所述职责", "Oliva决定图像群组；Gaulli解决四个人物在单一穹隅中的构图呈现。此处不把两种职责合并为同一角色", "内容 / 基本信息"),
    ]
    table_ids = {
        section: "tbl-" + hashlib.sha256(
            f"{WORK_KU}|{section}|1|字段|值|证据".encode("utf-8")
        ).hexdigest()[:16]
        for section in {section for _, _, section in fields}
    }
    evidence = "S1；第3章，印刷页83 L70；PDF物理页25"
    citation = BOOK_CITATION
    new_enrichment = []
    row_index: dict[str, int] = {}
    for offset, (field, value, section) in enumerate(fields):
        row_index[section] = row_index.get(section, 0) + 1
        new_enrichment.append({
            "enrichment_id": f"enr-{next_enrichment + offset:05d}",
            "ku_id": WORK_KU,
            "field": field,
            "value": value,
            "origin": "book",
            "source_id": SOURCE_ID,
            "source_ids": [SOURCE_ID],
            "source_ref": "S1",
            "source_citations": [citation],
            "source_urls": [],
            "evidence": evidence,
            "evidence_status": "source_backed",
            "dispute": None,
            "accessed_date": "",
            "occurrence_id": stable_id("occ", f"{WORK_KU}|{field}"),
            "table_id": table_ids[section],
            "table_section": section,
            "has_header": True,
            "table_header": ["字段", "值", "证据"],
            "row_index": row_index[section],
            "cells": [field, value, evidence],
            "unit_evidence_status": "source_backed",
        })

    relation_row = {
        "relation_id": RELATION_ID,
        "subject_ku_id": WORK_KU,
        "object_ku_id": "units/persons/giovan-battista-gaulli",
        "predicate": "designed_by",
        "time": "",
        "role": "Haskell所述的构图设计归属",
        "scope": "仅记录Haskell将单一穹隅中四个人物的构图解决方案归于Gaulli；不推定整座穹顶总人数，不等同于所有施工或整个装饰工程的唯一执行者。",
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": f"Chapter 3, printed p. 83 L70; statement={STATEMENT_DESIGN}",
        "source_file": SOURCE_FILE,
        "note": f"S6 formal; source-bounded design attribution. See 03-processing/{TASK}/process/knowledge.md#{ANCHOR}.",
    }
    assert relation_row["object_ku_id"] in {row["ku_id"] for row in manifest}

    process_ref = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    alignment_row["ku_id"] = WORK_KU
    alignment_row["process_ref"] = process_ref
    alignment_row["resolution_note"] += f" S4 registration: mapped {WORK_GROUP} to {WORK_KU}; S6 reviewed both direct source candidates."

    manifest_row = {
        "ku_id": WORK_KU,
        "type": "work",
        "canonical_name": "耶稣堂穹顶穹隅人物组",
        "name_en": "Figure Group in the Gesù Dome Pendentives",
        "source_task": TASK,
        "card_path": WORK_CARD_REL,
    }
    manifest.append(manifest_row)
    relations.append(relation_row)
    enrichment_rows.extend(new_enrichment)

    units = accepted["units"]
    insert_at = next((i for i, path in enumerate(units) if path > WORK_CARD_REL), len(units))
    units.insert(insert_at, WORK_CARD_REL)
    accepted_lines = accepted_text.splitlines()
    accepted_line = f"- {WORK_CARD_REL}"
    line_insert_at = next((i for i, line in enumerate(accepted_lines) if line.startswith("- ") and line[2:] > WORK_CARD_REL), len(accepted_lines))
    accepted_lines.insert(line_insert_at, accepted_line)

    print("S3: retain cand-5271 new / workgrp-d7414b802d0064; no identity reopen triggered.")
    print(f"S4: register one work KU: {WORK_KU}.")
    print("S5: append four source-backed fields about descriptive title, type, scope, and separated roles.")
    print("S6: designed_by formal for Gaulli; reject Oliva-to-work edge because the controlled vocabulary has no precise iconographic-selection predicate.")
    print(f"S6 relation row: {RELATION_ID}.")
    if args.dry_run:
        return

    WORK_CARD.write_text(card_text(), encoding="utf-8", newline="\n")
    write_csv(ALIGNMENT_PATH, alignment_fields, alignments)
    write_csv(MANIFEST_PATH, manifest_fields, manifest)
    write_csv(RELATIONS_PATH, relation_fields, relations)
    encoding = "utf-8-sig" if ENRICHMENT_PATH.read_bytes().startswith(b"\xef\xbb\xbf") else "utf-8"
    ENRICHMENT_PATH.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in enrichment_rows) + "\n",
        encoding=encoding,
        newline="\n",
    )
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8")
    print("Applied S4/S5/S6 registration; inspect the card through build_cards.py --preview.")


if __name__ == "__main__":
    main()
