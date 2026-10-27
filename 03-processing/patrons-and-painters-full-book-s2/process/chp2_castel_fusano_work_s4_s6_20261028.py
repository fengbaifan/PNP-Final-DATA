"""Guarded S4/S5/S6 write for the Chapter 2 Castel Fusano undertaking."""
from __future__ import annotations

import argparse
import codecs
import csv
import hashlib
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = (
    "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    "#s2-s4-s5-s6-chp2-castel-fusano-country-house-decoration-20261028"
)
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
SOURCE_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 2, p. 39."
)
PLACE = {
    "candidate_id": "cand-4480",
    "alignment_id": "aln-4663",
    "ku_id": "units/places/castel-fusano",
    "canonical_name": "卡斯特尔富萨诺",
    "name_en": "Castel Fusano",
    "card_path": "04-knowledge/units/places/castel-fusano.md",
}
WORK = {
    "candidate_id": "cand-4481",
    "alignment_id": "aln-4664",
    "ku_id": "units/works/marcello-sacchetti-country-house-decoration-castel-fusano",
    "canonical_name": "马尔切洛·萨凯蒂卡斯特尔富萨诺乡间别墅装饰工程",
    "name_en": "Decoration of Marcello Sacchetti’s Country House at Castel Fusano",
    "card_path": (
        "04-knowledge/units/works/"
        "marcello-sacchetti-country-house-decoration-castel-fusano.md"
    ),
}


def read_text(path: Path) -> tuple[str, bool, str]:
    raw = path.read_bytes()
    bom = raw.startswith(codecs.BOM_UTF8)
    text = raw[len(codecs.BOM_UTF8) if bom else 0 :].decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, bom, newline


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bool, str]:
    text, bom, newline = read_text(path)
    reader = csv.DictReader(io.StringIO(text, newline=""))
    rows = list(reader)
    if not reader.fieldnames:
        raise ValueError(f"Missing CSV header: {path}")
    return reader.fieldnames, rows, bom, newline


def encode_csv(
    fields: list[str], rows: list[dict[str, str]], bom: bool, newline: str
) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=fields, extrasaction="raise", lineterminator=newline
    )
    writer.writeheader()
    writer.writerows(rows)
    data = stream.getvalue().encode("utf-8")
    return codecs.BOM_UTF8 + data if bom else data


def read_jsonl(path: Path) -> tuple[list[dict], bool, str]:
    text, bom, newline = read_text(path)
    return [json.loads(line) for line in text.splitlines() if line.strip()], bom, newline


def encode_jsonl(rows: list[dict], bom: bool, newline: str) -> bytes:
    text = "".join(json.dumps(row, ensure_ascii=False) + newline for row in rows)
    data = text.encode("utf-8")
    return codecs.BOM_UTF8 + data if bom else data


def stable_id(prefix: str, value: str) -> str:
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def card_table_id(ku_id: str, section: str, index: int = 1) -> str:
    header = ["字段", "值", "证据"]
    value = f"{ku_id}|{section}|{index}|{'|'.join(header)}"
    return stable_id("tbl-", value)


def find_one(rows: list[dict], key: str, value: str) -> dict:
    matches = [row for row in rows if row.get(key) == value]
    if len(matches) != 1:
        raise ValueError(f"Expected one {key}={value}; found {len(matches)}")
    return matches[0]


def work_card() -> str:
    return """---
title: 马尔切洛·萨凯蒂卡斯特尔富萨诺乡间别墅装饰工程（Decoration of Marcello Sacchetti’s Country House at Castel Fusano）
name_en: Decoration of Marcello Sacchetti’s Country House at Castel Fusano
type: work
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 2, p. 39.'
  location: 第2章，印刷页39，L83、L85；PDF物理页20。
  sentence_summary: Haskell称Marcello雇用Pietro da Cortona承担一项规模更大的乡间别墅装饰工程，并评价Pietro对所选题材的诠释和装饰方案调整。
  original_quotes:
  - source_span: 第2章印刷页39 L83；PDF物理页20。
    text: |-
      Soon afterwards Marcello employed Pietro on a new and larger undertaking—the decoration of his country house at Castel Fusano near Ostia.
  - source_span: 第2章印刷页39 L85；PDF物理页20。
    text: |-
      In his successful interpretation of these themes, and his ability 40 adapt them to a convincing decorative scheme, Pietro da Cortona showed that he had found his true road.
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_ii.md
    source_span: chp-2:02_CHP-2_sec_ii:l80-89 L83,L85; printed p. 39; PDF physical p. 20
created: '2026-10-28'
updated: '2026-10-28'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s4-s5-s6-chp2-castel-fusano-country-house-decoration-20261028
---

## 内容

### 描述

**中文：** 本卡记录Haskell所述、由Marcello雇用Pietro da Cortona承担的卡斯特尔富萨诺乡间别墅装饰工程。书中称Pietro诠释了Marcello选择的题材并调整为装饰方案；这记录书内对项目范围和设计职责的表述，不证明工程已经完成、现存或由Pietro独自施工。前文另提一座近Ostia的villa，本卡不据相近地点将两处建筑认作同一对象。

**English:** This unit records the country-house decoration project at Castel Fusano for which Haskell says Marcello employed Pietro da Cortona. Haskell describes Pietro as interpreting Marcello’s chosen subjects and adapting them into a decorative scheme. This preserves the book’s account of the project and design role; it does not establish completion, survival, or Pietro’s sole execution. Haskell mentions another villa near Ostia earlier in the chapter; proximity alone does not identify the two buildings as the same.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性名称 | 马尔切洛·萨凯蒂卡斯特尔富萨诺乡间别墅装饰工程（Decoration of Marcello Sacchetti’s Country House at Castel Fusano）；项目描述性暂名 | S1；第2章，印刷页39 L83 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作品类型 | 乡间别墅装饰工程；本KU表示装饰 undertaking，不表示房屋建筑本身或任何一件存世作品 | S1；第2章，印刷页39 L83 |
| 来源所述范围与职责 | Haskell称Marcello雇用Pietro承担该工程，并称Pietro诠释Marcello选定的题材、调整装饰方案；不据此认定Pietro独自施工 | S1；第2章，印刷页39 L83、L85 |

## 关系与证据

### 关系记录

### 身份组

- S3候选：cand-4481
- S3决定：new；身份组 workgrp-fae124b86a40d2
- S4知识元：units/works/marcello-sacchetti-country-house-decoration-castel-fusano

### 关系候选入口

[第2章 Castel Fusano 装饰工程批次记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s4-s5-s6-chp2-castel-fusano-country-house-decoration-20261028)
"""


def place_card() -> str:
    return """---
title: 卡斯特尔富萨诺（Castel Fusano）
name_en: Castel Fusano
type: place
evidence_status: source_backed
sources:
- citation: 'Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006), ch. 2, p. 39.'
  location: 第2章，印刷页39，L83；PDF物理页20。
  sentence_summary: Haskell将Castel Fusano称为Marcello Sacchetti乡间别墅所在地点，并补充其近Ostia。
  original_quotes:
  - source_span: 第2章印刷页39 L83；PDF物理页20。
    text: |-
      Soon afterwards Marcello employed Pietro on a new and larger undertaking—the decoration of his country house at Castel Fusano near Ostia.
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/02_CHP-2_sec_ii.md
    source_span: chp-2:02_CHP-2_sec_ii:l80-89 L83; printed p. 39; PDF physical p. 20
created: '2026-10-28'
updated: '2026-10-28'
process_ref: 03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s4-s5-s6-chp2-castel-fusano-country-house-decoration-20261028
---

## 内容

### 描述

**中文：** 本卡仅登记Haskell明确写出的地点名称Castel Fusano；它不是乡间别墅建筑卡，也不据“near Ostia”推定现代行政层级或与第2章前文所述villa同一。

**English:** This unit records only the named place Castel Fusano in Haskell’s account. It is not a card for the country-house building; “near Ostia” is not used here to infer a modern administrative status or identity with the villa mentioned earlier in Chapter 2.

### 名称

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 地点性质 | Haskell用作Marcello Sacchetti乡间别墅所在地的命名地点；本卡只记录来源中的地名锚点 | S1；第2章，印刷页39 L83 |

## 关系与证据

### 关系记录

### 身份组

- S3候选：cand-4480
- S3决定：new；身份组 sg3-place-cand-4480
- S4知识元：units/places/castel-fusano

### 关系候选入口

[第2章 Castel Fusano 装饰工程批次记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s2-s4-s5-s6-chp2-castel-fusano-country-house-decoration-20261028)
"""


def enrichment_rows() -> list[dict]:
    specs = [
        (
            WORK["ku_id"], "描述性名称",
            "马尔切洛·萨凯蒂卡斯特尔富萨诺乡间别墅装饰工程（Decoration of Marcello Sacchetti’s Country House at Castel Fusano）；项目描述性暂名",
            "内容 / 名称", 1, "第2章，印刷页39 L83",
        ),
        (
            WORK["ku_id"], "作品类型",
            "乡间别墅装饰工程；本KU表示装饰 undertaking，不表示房屋建筑本身或任何一件存世作品",
            "内容 / 基本信息", 1, "第2章，印刷页39 L83",
        ),
        (
            WORK["ku_id"], "来源所述范围与职责",
            "Haskell称Marcello雇用Pietro承担该工程，并称Pietro诠释Marcello选定的题材、调整装饰方案；不据此认定Pietro独自施工",
            "内容 / 基本信息", 2, "第2章，印刷页39 L83、L85",
        ),
        (
            PLACE["ku_id"], "地点性质",
            "Haskell用作Marcello Sacchetti乡间别墅所在地的命名地点；本卡只记录来源中的地名锚点",
            "内容 / 基本信息", 1, "第2章，印刷页39 L83",
        ),
    ]
    rows = []
    for number, (ku_id, field, value, section, row_index, evidence) in enumerate(specs, 18511):
        rows.append(
            {
                "enrichment_id": f"enr-{number}",
                "ku_id": ku_id,
                "field": field,
                "value": value,
                "origin": "book",
                "source_id": SOURCE_ID,
                "source_ids": [SOURCE_ID],
                "source_ref": "S1",
                "source_citations": [SOURCE_CITATION],
                "source_urls": [],
                "evidence": "S1；" + evidence,
                "evidence_status": "source_backed",
                "dispute": None,
                "accessed_date": "",
                "occurrence_id": stable_id("occ-", ku_id + "|" + field + "|" + evidence),
                "table_id": card_table_id(ku_id, section),
                "table_section": section,
                "has_header": True,
                "table_header": ["字段", "值", "证据"],
                "row_index": row_index,
                "cells": [field, value, "S1；" + evidence],
                "unit_evidence_status": "source_backed",
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write the reviewed changes")
    args = parser.parse_args()

    alignment_path = TABLES / "alignment.csv"
    manifest_path = TABLES / "ku-manifest.csv"
    enrichment_path = TABLES / "enrichment.jsonl"
    relations_path = TABLES / "relations.csv"
    statements_path = TABLES / "book-statements.jsonl"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"

    a_fields, alignment, a_bom, a_nl = read_csv(alignment_path)
    m_fields, manifest, m_bom, m_nl = read_csv(manifest_path)
    enrichment, e_bom, e_nl = read_jsonl(enrichment_path)
    r_fields, relations, r_bom, r_nl = read_csv(relations_path)
    statements, s_bom, s_nl = read_jsonl(statements_path)

    for spec in (PLACE, WORK):
        row = find_one(alignment, "alignment_id", spec["alignment_id"])
        if row["candidate_id"] != spec["candidate_id"] or row["decision"] != "new" or row["ku_id"]:
            raise ValueError(f"Unexpected S3/S4 row: {spec['alignment_id']}")
        if any(item["ku_id"] == spec["ku_id"] for item in manifest):
            raise ValueError(f"KU already exists: {spec['ku_id']}")
        if (ROOT / spec["card_path"]).exists():
            raise ValueError(f"Card already exists: {spec['card_path']}")

    by_id = {row["statement_id"]: row for row in statements}
    employment_id = "st-chp2-secii-l80-89-country-house-decoration-employed"
    design_id = "st-chp2-secii-l80-89-pietro-interpreted-decoration-themes"
    employment, design = by_id[employment_id], by_id[design_id]
    if employment["subject_candidate_id"] != "cand-2316" or employment["object_candidate_id"] != "cand-4481":
        raise ValueError("Employment statement changed since the independent review")
    if design["subject_candidate_id"] != "cand-0342" or design["object_candidate_id"] != "cand-4481":
        raise ValueError("Design statement changed since the independent review")
    new_ids = {
        "st-chp2-secii-l80-89-country-house-decoration-at-castel-fusano",
        "st-chp2-secii-l80-89-pietro-found-his-true-road",
    }
    if any(row["statement_id"] in new_ids for row in statements):
        raise ValueError("A proposed S2 statement ID already exists")

    next_relation = max(
        int(match.group(1))
        for row in relations
        if (match := re.fullmatch(r"rel-(\d+)", row["relation_id"]))
    ) + 1
    if next_relation != 2470:
        raise ValueError(f"Expected next relation ID rel-2470; found rel-{next_relation}")
    existing_enrichment_ids = {row["enrichment_id"] for row in enrichment}
    if any(f"enr-{n}" in existing_enrichment_ids for n in range(18511, 18515)):
        raise ValueError("A proposed enrichment ID already exists")

    accepted_text, accepted_bom, accepted_nl = read_text(accepted_path)
    accepted_lines = accepted_text.splitlines()
    if not accepted_lines or accepted_lines[0].strip() != "units:":
        raise ValueError("Unexpected accepted.yml structure")
    claims_index = next(
        (i for i, line in enumerate(accepted_lines) if line.strip() == "claims:"),
        None,
    )
    if claims_index is None:
        raise ValueError("accepted.yml claims section was not found")
    unit_lines = accepted_lines[1:claims_index]
    if any(line.strip() and not line.startswith("- ") for line in unit_lines):
        raise ValueError("Unexpected content in accepted.yml units section")
    accepted_paths = [line.strip()[2:] for line in unit_lines if line.strip()]
    for spec in (PLACE, WORK):
        if spec["card_path"] in accepted_paths:
            raise ValueError(f"Already accepted: {spec['card_path']}")

    employment_after = json.loads(json.dumps(employment))
    employment_q = employment_after["qualifiers"]
    employment_after["object_candidate_id"] = "cand-0342"
    employment_q.pop("artist_candidate_id", None)
    employment_q["project_candidate_id"] = "cand-4481"
    employment_q["place_candidate_id"] = "cand-4480"
    employment_q["possible_same_building_identity_candidate_id"] = "cand-4458"
    employment_q["nearby_place_candidate_id"] = "cand-4459"
    employment_q["qualification"] = (
        "The direct relation is Marcello's employment of Pietro; the decorative undertaking is its scope. "
        "The country house at Castel Fusano is not identified here with the earlier villa candidate cand-4458."
    )
    employment_q["relation_candidate_note"] = (
        "Haskell explicitly says Marcello employed Pietro on this undertaking. Map the employment to Pietro; "
        "retain the work as scope. Possible identity with cand-4458 remains unresolved."
    )
    employment_q["mentioned_candidate_ids"] = [
        "cand-2316", "cand-0342", "cand-4481", "cand-4480", "cand-4458", "cand-4459"
    ]

    design_after = json.loads(json.dumps(design))
    design_q = design_after["qualifiers"]
    design_q["claim"] = (
        "Haskell says Pietro successfully interpreted Marcello’s selected themes and adapted them to a convincing decorative scheme."
    )
    design_q["place_candidate_id"] = "cand-4480"
    design_q["possible_same_building_identity_candidate_id"] = "cand-4458"
    design_q["qualification"] = (
        "This statement records Haskell's account of Pietro's interpretation and design role. "
        "The separate career judgment that he had found his true road is split into a non-relation statement. "
        "The country house is not identified with the earlier villa candidate cand-4458."
    )
    design_q["relation_candidate_note"] = (
        "Haskell attributes interpretation of the chosen subjects and adaptation of the decorative scheme to Pietro. "
        "This supports a design role, not sole execution."
    )
    design_q["mentioned_candidate_ids"] = [
        "cand-0342", "cand-4481", "cand-4480", "cand-4458", "cand-4483", "cand-4484"
    ]

    site_statement = {
        "statement_id": "st-chp2-secii-l80-89-country-house-decoration-at-castel-fusano",
        "segment_id": "chp-2:02_CHP-2_sec_ii:l80-89",
        "subject_candidate_id": "cand-4481",
        "object_candidate_id": "cand-4480",
        "predicate": "decorative_undertaking_located_at_source_named_place",
        "qualifiers": {
            "source_line_start": 83,
            "source_line_end": 83,
            "claim": "Haskell locates the decorative undertaking at Marcello Sacchetti’s country house in Castel Fusano, near Ostia.",
            "speaker": "Haskell",
            "text_layer": "authorial narrative",
            "print_page": "39",
            "pdf_page": 20,
            "qualification": (
                "This records the project site named as Castel Fusano. It does not equate the country-house building "
                "with the earlier villa candidate cand-4458 or Castel Fusano with Ostia."
            ),
            "nearby_place_candidate_id": "cand-4459",
            "mentioned_candidate_ids": ["cand-4481", "cand-4480", "cand-4459"],
            "source_mention_ids": [
                "m-chp2-secii-l80-89-0026",
                "m-chp2-secii-l80-89-0028",
                "m-chp2-secii-l80-89-0029",
            ],
            "relation_candidate": True,
            "relation_candidate_note": (
                "The undertaking is explicitly situated at the named locality Castel Fusano. "
                "This edge denotes the project's site, not present storage or survival."
            ),
        },
        "original_quote": (
            "Soon afterwards Marcello employed Pietro on a new and larger undertaking—the decoration of his country house at Castel Fusano near Ostia."
        ),
        "origin": "book",
        "source_file": SOURCE_FILE,
    }
    career_statement = {
        "statement_id": "st-chp2-secii-l80-89-pietro-found-his-true-road",
        "segment_id": "chp-2:02_CHP-2_sec_ii:l80-89",
        "subject_candidate_id": "cand-0342",
        "object_candidate_id": None,
        "predicate": "authorial_career_judgment_reported",
        "qualifiers": {
            "source_line_start": 85,
            "source_line_end": 85,
            "claim": "Haskell concludes that Pietro’s interpretation and adaptation of the decorative scheme showed he had found his true road.",
            "speaker": "Haskell",
            "text_layer": "authorial evaluation",
            "print_page": "39",
            "pdf_page": 20,
            "qualification": (
                "This preserves Haskell's career judgment as an attributed evaluation; "
                "it is not a formal relation and does not establish an independent biography."
            ),
            "mentioned_candidate_ids": ["cand-0342"],
            "relation_candidate": False,
        },
        "original_quote": "showed that he had found his true road.",
        "origin": "book",
        "source_file": SOURCE_FILE,
    }

    alignment_after = [dict(row) for row in alignment]
    for spec in (PLACE, WORK):
        row = find_one(alignment_after, "alignment_id", spec["alignment_id"])
        row["ku_id"] = spec["ku_id"]
        row["process_ref"] = PROCESS_REF
        if spec["candidate_id"] == PLACE["candidate_id"]:
            row["resolution_note"] = row["resolution_note"].replace(
                "its identity as the villa previously mentioned near Ostia is likely but should be checked in S3.",
                "possible identity with earlier villa candidate cand-4458 remains unresolved; do not merge without further evidence.",
            )
        if spec["candidate_id"] == WORK["candidate_id"]:
            row["resolution_note"] = row["resolution_note"].replace(
                "指向可辨认的单件作品",
                "指向来源明确的装饰工程undertaking（非建筑实体或已知存世单件作品）",
            )
        row["resolution_note"] += (
            f" S4 registration (2026-10-28): {spec['candidate_id']} -> {spec['ku_id']}; "
            "the existing S3 new decision and identity group are retained."
        )

    manifest_after = list(manifest)
    for spec, kind in ((PLACE, "place"), (WORK, "work")):
        manifest_after.append(
            {
                "ku_id": spec["ku_id"],
                "type": kind,
                "canonical_name": spec["canonical_name"],
                "name_en": spec["name_en"],
                "source_task": "patrons-and-painters-full-book-s2",
                "card_path": spec["card_path"],
            }
        )

    enrichment_after = list(enrichment) + enrichment_rows()
    relations_after = list(relations)
    relation_specs = [
        {
            "subject_ku_id": "units/persons/pietro-da-cortona",
            "object_ku_id": "units/persons/marcello-sacchetti",
            "predicate": "employed_by",
            "time": "Soon afterwards, relative to the preceding works; Haskell gives no calendar date",
            "role": "Pietro was employed by Marcello for this undertaking",
            "scope": "The decorative undertaking at the country house in Castel Fusano; not a claim of long-term employment.",
            "source_span": "Chapter 2, printed p. 39 L83; statement=st-chp2-secii-l80-89-country-house-decoration-employed",
            "note": "S6 formal; direction follows the employed person to employer. No contract or numeric date is inferred.",
        },
        {
            "subject_ku_id": WORK["ku_id"],
            "object_ku_id": "units/persons/pietro-da-cortona",
            "predicate": "designed_by",
            "time": "",
            "role": "Interpretation of selected themes and adaptation of the decorative scheme",
            "scope": "The country-house decoration project; does not assign sole execution to Pietro.",
            "source_span": "Chapter 2, printed p. 39 L85; statement=st-chp2-secii-l80-89-pietro-interpreted-decoration-themes",
            "note": "S6 formal; records Haskell's source-level design attribution, not an independently verified work catalogue.",
        },
        {
            "subject_ku_id": WORK["ku_id"],
            "object_ku_id": PLACE["ku_id"],
            "predicate": "located_at",
            "time": "",
            "role": "Site of the decorative undertaking",
            "scope": "Castel Fusano as named in Haskell; not the current storage location or proof that any component survives.",
            "source_span": "Chapter 2, printed p. 39 L83; statement=st-chp2-secii-l80-89-country-house-decoration-at-castel-fusano",
            "note": "S6 formal; the nearby Ostia locator does not merge the place with Ostia or the earlier villa.",
        },
    ]
    for number, spec in enumerate(relation_specs, next_relation):
        relations_after.append(
            {
                "relation_id": f"rel-{number}",
                **spec,
                "origin": "book",
                "status": "formal",
                "source_id": SOURCE_ID,
                "source_file": SOURCE_FILE,
            }
        )

    accepted_paths.extend([PLACE["card_path"], WORK["card_path"]])
    accepted_after = accepted_nl.join(
        ["units:"] + ["- " + path for path in accepted_paths] + accepted_lines[claims_index:]
    ) + accepted_nl

    statements_after = list(statements)
    employment_index = next(i for i, row in enumerate(statements_after) if row["statement_id"] == employment_id)
    statements_after[employment_index] = employment_after
    statements_after.insert(employment_index + 1, site_statement)
    design_index = next(i for i, row in enumerate(statements_after) if row["statement_id"] == design_id)
    statements_after[design_index] = design_after
    statements_after.insert(design_index + 1, career_statement)

    files = [
        (alignment_path, encode_csv(a_fields, alignment_after, a_bom, a_nl)),
        (manifest_path, encode_csv(m_fields, manifest_after, m_bom, m_nl)),
        (enrichment_path, encode_jsonl(enrichment_after, e_bom, e_nl)),
        (relations_path, encode_csv(r_fields, relations_after, r_bom, r_nl)),
        (statements_path, encode_jsonl(statements_after, s_bom, s_nl)),
        (accepted_path, (codecs.BOM_UTF8 if accepted_bom else b"") + accepted_after.encode("utf-8")),
        (ROOT / PLACE["card_path"], place_card().encode("utf-8")),
        (ROOT / WORK["card_path"], work_card().encode("utf-8")),
    ]

    print("Mode:", "APPLY" if args.apply else "DRY RUN")
    print("S2: correct employment endpoint to Pietro; retain the project as scope.")
    print("S2: separate the career evaluation; add the explicit Castel Fusano site claim.")
    print("S4: register cand-4480 and cand-4481 using their existing S3 new decisions.")
    print("S5: add four source-backed fields. S6: add three formal decisions (rel-2470..rel-2472).")
    print("Cards:", PLACE["card_path"], WORK["card_path"])
    print("Files to write:", len(files))
    if args.apply:
        for path, payload in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + ".tmp")
            temporary.write_bytes(payload)
            temporary.replace(path)
        print("Applied guarded changes.")


if __name__ == "__main__":
    main()
