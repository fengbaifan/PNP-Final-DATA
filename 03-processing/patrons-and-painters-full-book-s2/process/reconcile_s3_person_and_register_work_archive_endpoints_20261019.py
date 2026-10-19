from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as stats_helper


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ROOT_GUIDE_PATH = ROOT / "AGENTS.md"
DATE = "2026-10-19"
PROCESS_ANCHOR = "s3-s4-person-work-archive-endpoints-20261019"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SAME_RULINGS = {
    "cand-1106": {
        "target": "units/persons/galileo-galilei",
        "group": "sg3-ku-units/persons/galileo-galilei",
        "reason": (
            "G.csv#13 is the ‘and Ludovico Cigoli’ sub-entry under the full-name "
            "Galilei, Galileo heading. The existing source-backed Galileo KU cites "
            "the matching p.102 passage, which identifies Cigoli as Galileo's "
            "favourite painter and occasional collaborator. The index form is "
            "surname-first; it is not another person."
        ),
    },
    "cand-1108": {
        "target": "units/persons/galileo-galilei",
        "group": "sg3-ku-units/persons/galileo-galilei",
        "reason": (
            "G.csv#15 is the ‘views on painting’ sub-entry under the full-name "
            "Galilei, Galileo heading. The existing source-backed Galileo KU cites "
            "the matching p.103 passage, which names Galileo and summarizes his "
            "views on painting. The index form is surname-first; it is not another person."
        ),
    },
    "cand-2349": {
        "target": "units/persons/giovanni-da-san-giovanni",
        "group": "sg3-ku-units/persons/giovanni-da-san-giovanni",
        "reason": (
            "S.csv#37 gives the inverted index form ‘San Giovanni, Giovanni da’ "
            "at pp.49 and 95. The existing source-backed person KU cites the p.49 "
            "Baldinucci note and p.95 passage, both naming Giovanni da San Giovanni; "
            "the locations and contexts match the index entry."
        ),
    },
    "cand-5945": {
        "target": "units/works/poussin-moses-trampling-on-pharaoh-s-crown",
        "group": "sg3-ku-units/works/poussin-moses-trampling-on-pharaoh-s-crown",
        "prior_group": "workgrp-0efe5e6f22b460",
        "reason": (
            "The chapter 4 p.114 title ‘Moses trampling on Pharaoh's Crown’ and "
            "p.115 narrative identify the same specific Poussin work as plate 19a "
            "in the existing source-backed work KU. The manifest already maps "
            "cand-2018 and cand-4087 to that KU from the index and plate evidence. "
            "Reuse the existing KU rather than register a duplicate."
        ),
    },
    "cand-5439": {
        "target": "units/places/s-ignazio",
        "group": "sg3-ku-units/places/s-ignazio",
        "prior_group": "sg3-place-cand-5439",
        "reason": (
            "The chapter 3 p.93 candidate names the Jesuit church S. Ignazio in Rome. "
            "The existing same-type place KU S. Ignazio is located in Rome and is "
            "anchored by the plate 15 reference to a vault fresco at S. Ignazio, Rome. "
            "This is the church, distinct from the Chapel of St Ignatius in the Gesù."
        ),
    },
}

NEW_GROUPS = {
    "cand-5457": {
        "group": "workgrp-1a180be8d3050f",
        "ku_id": "units/works/pierre-legros-monument-gregory-xv-ludovico-ludovisi",
        "card_path": "04-knowledge/units/works/pierre-legros-monument-gregory-xv-ludovico-ludovisi.md",
        "type": "work",
    },
    "cand-5458": {
        "group": "archive-group-7630830856b3",
        "ku_id": "units/archives/jesuit-archives-ecclesia-s-ignatii-de-urbe-1255",
        "card_path": "04-knowledge/units/archives/jesuit-archives-ecclesia-s-ignatii-de-urbe-1255.md",
        "type": "archive",
    },
}

WORK_RELATIONS = (
    "st-chp3-seciv-l179-187-documents-preserved-in-jesuit-archives",
    "st-chp3-seciv-l179-187-legros-completed-ludovisi-monument-in-1710",
    "st-chp3-seciv-l179-187-monument-to-cardinal-ludovisi",
    "st-chp3-seciv-l179-187-monument-to-pope-gregory-xv",
    "st-chp3-seciv-l179-187-ludovisi-monument-located-in-s-ignazio",
)
POUSSIN_RELATIONS = (
    "st-chp4-sec-ii-p115-first-work-early-commission",
    "st-chp4-sec-ii-p115-first-work-exceptional-patron",
    "st-chp4-sec-ii-p115-first-work-josephus",
    "st-chp4-sec-ii-p115-first-work-story-not-in-bible",
    "st-chp4-sec-ii-p115-first-work-created-by-poussin",
)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    encoding = "utf-8-sig" if path == ALIGNMENT_PATH else "utf-8"
    with path.open("w", encoding=encoding, newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_jsonl(path: Path):
    with path.open(encoding="utf-8-sig") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_jsonl(path: Path, rows):
    with path.open("w", encoding="utf-8-sig", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def append_card_table_fields(card_texts, existing_rows):
    sys.path.insert(0, str(ROOT / "scripts"))
    import audit_tables

    _, source_rows = read_csv(TABLES / "sources.csv")
    sources = {row["source_id"]: row for row in source_rows}
    source_id = "haskell-1980-rev-ed"
    assert source_id in sources
    source_citation = (
        "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
        "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 3, p. 93."
    )
    existing_ids = {row["enrichment_id"] for row in existing_rows}
    existing_occurrences = {row["occurrence_id"] for row in existing_rows}
    numeric_ids = [
        int(value.split("-")[-1]) for value in existing_ids
        if value.startswith("enr-") and value.split("-")[-1].isdigit()
    ]
    next_number = max(numeric_ids, default=0) + 1
    additions = []

    for card_path, card_text in card_texts.items():
        manifest_row = next(row for row in NEW_GROUPS.values() if row["card_path"] == card_path)
        ku_id = manifest_row["ku_id"]
        boundary = re.match(r"\A(?:\ufeff)?---\r?\n.*?\r?\n---(?:\r?\n|$)", card_text, re.DOTALL)
        assert boundary, card_path
        tables = audit_tables.independently_parse_card_tables(card_text[boundary.end():], ku_id)
        for table_id, table in tables.items():
            for row_index, cells in enumerate(table["rows"], 1):
                payload = f"{ku_id}|{table_id}|{row_index}|{'|'.join(cells)}"
                occurrence_id = "occ-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
                enrichment_id = f"enr-{next_number:05d}"
                assert enrichment_id not in existing_ids
                assert occurrence_id not in existing_occurrences
                additions.append({
                    "enrichment_id": enrichment_id,
                    "ku_id": ku_id,
                    "field": cells[0],
                    "value": cells[1],
                    "origin": "book",
                    "source_id": source_id,
                    "source_ids": [source_id],
                    "source_ref": "S1",
                    "source_citations": [source_citation],
                    "source_urls": [],
                    "evidence": f"S1; {cells[2]}",
                    "evidence_status": "source_backed",
                    "dispute": None,
                    "accessed_date": "",
                    "occurrence_id": occurrence_id,
                    "table_id": table_id,
                    "table_section": table["section"],
                    "has_header": table["has_header"],
                    "table_header": table["header"],
                    "row_index": row_index,
                    "cells": cells,
                    "unit_evidence_status": "source_backed",
                })
                existing_ids.add(enrichment_id)
                existing_occurrences.add(occurrence_id)
                next_number += 1
    assert len(additions) == 9, len(additions)
    return existing_rows + additions


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label}; found {count}")
    return text.replace(old, new, 1)


def current_candidate_decisions(candidate_rows, alignment_rows):
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    alignment_by_candidate = defaultdict(list)
    for row in alignment_rows:
        cid = row.get("candidate_id", "")
        if cid in candidate_ids:
            alignment_by_candidate[cid].append(row)
    decisions = {}
    for cid, rows in alignment_by_candidate.items():
        candidate_decisions = [row for row in rows if not row.get("external_source")]
        if len(candidate_decisions) == 1:
            decisions[cid] = candidate_decisions[0]
        elif not candidate_decisions and len(rows) == 1:
            decisions[cid] = rows[0]
        else:
            raise AssertionError(f"ambiguous candidate decision rows: {cid}")
    assert len(decisions) == len(candidate_ids)
    return decisions


def totals(stats):
    keys = (
        "same_candidates", "same_kus", "new_candidates", "new_groups",
        "registered_groups", "registered_members", "pending_groups",
        "pending_members", "conflict", "excluded", "undecided", "total",
    )
    return {key: sum(row[key] for row in stats.values()) for key in keys}


def endpoint_pending_by_type(candidate_rows, decisions, statements):
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    pending = {}
    for cid, row in decisions.items():
        if row["decision"] == "new" and not row.get("ku_id"):
            group = stats_helper.get_group(row.get("resolution_note", ""))
            assert group, f"new candidate lacks current identity group: {cid}"
            pending[cid] = (group, candidate_by_id[cid].get("suggested_type", ""))
    groups = defaultdict(set)
    for statement in statements:
        if (statement.get("qualifiers") or {}).get("relation_candidate") is not True:
            continue
        for cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
            if cid in pending:
                group, kind = pending[cid]
                groups[kind].add(group)
    return {kind: len(group_ids) for kind, group_ids in groups.items()}


def fully_mapped_relation_ids(decisions, statements):
    def mapped(cid):
        row = decisions.get(cid)
        return bool(row and row.get("decision") in {"same", "new"} and row.get("ku_id"))

    return {
        statement["statement_id"]
        for statement in statements
        if (statement.get("qualifiers") or {}).get("relation_candidate") is True
        and all((cid := statement.get(key)) and mapped(cid)
                for key in ("subject_candidate_id", "object_candidate_id"))
    }


def make_work_card():
    card_path = "04-knowledge/units/works/pierre-legros-monument-gregory-xv-ludovico-ludovisi.md"
    source_file = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
    sources = [{
        "citation": BOOK_CITATION,
        "location": "第3章，印刷页93；OCR L182、186",
        "sentence_summary": (
            "上下文将 S. Ignazio 确认为耶稣会教堂；哈斯克尔随后称 Pierre Legros 于1710年在同一教堂完成 "
            "Pope Gregory XV 与 Cardinal Ludovisi 的纪念碑。"
        ),
        "original_quotes": [
            {
                "source_span": "line 182",
                "text": "In fact, the powerfully illusionistic art that they fostered in S. Andrea al Quirinale, the Gesù and above all S. Ignazio long after such decoration had vanished elsewhere was prompted by just such considerations.",
            },
            {
                "source_span": "line 186",
                "text": "In 1710 Pierre Legros completed the monument to Pope Gregory XV and Cardinal Ludovisi in the same church.",
            },
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": "lines 182, 186; print p. 93",
        },
    }]
    frontmatter = {
        "title": "格列高利十五世与卢多维科·卢多维西纪念碑（Monument to Pope Gregory XV and Cardinal Ludovico Ludovisi at S. Ignazio）",
        "name_en": "Monument to Pope Gregory XV and Cardinal Ludovico Ludovisi at S. Ignazio",
        "type": "work",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第3章 p.93](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md#L182)"
    body = f"""## 内容

### 描述

**中文：** 本卡对应哈斯克尔所述的一座纪念碑：Pierre Legros 于1710年在 S. Ignazio 完成，纪念 Pope Gregory XV 与 Cardinal Ludovico Ludovisi。书中未给出独立正式题名，当前题名为描述性名称。{source_link}

**English:** This card represents the monument Haskell says Pierre Legros completed at S. Ignazio in 1710 for Pope Gregory XV and Cardinal Ludovico Ludovisi. The book supplies no separate formal title; the display title is descriptive. {source_link}

### 作品身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 题名性质 | 描述性工作题名；原书仅称为 monument | 第3章 p.93，L186 |
| 作品类型 | 纪念碑 | 第3章 p.93，L186 |
| 完成者 | Pierre Legros（原文称 completed by） | 第3章 p.93，L186 |
| 完成年份 | 1710 | 第3章 p.93，L186 |
| 地点 | S. Ignazio（由同段上下文的 same church 指代） | 第3章 p.93，L182、186 |
| 纪念对象 | Pope Gregory XV；Cardinal Ludovisi | 第3章 p.93，L186 |

## 关系与证据

### 关系记录

本卡目前没有已裁决的正式关系。以下5条原书 S2 关系候选仍待 S6 逐项审查，端点映射不代表关系已成立：`{WORK_RELATIONS[0]}`、`{WORK_RELATIONS[1]}`、`{WORK_RELATIONS[2]}`、`{WORK_RELATIONS[3]}`、`{WORK_RELATIONS[4]}`。判断与候选端点见[批次过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{PROCESS_ANCHOR})。

### 身份与外部链接

本卡依据书内来源登记；本批未查验外部作品目录、现存状态或档案原件。
"""
    return card_path, f"---\n{fm}---\n\n{body}"


def make_archive_card():
    card_path = "04-knowledge/units/archives/jesuit-archives-ecclesia-s-ignatii-de-urbe-1255.md"
    source_file = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
    sources = [{
        "citation": BOOK_CITATION,
        "location": "第3章，印刷页93；OCR L186–187",
        "sentence_summary": (
            "哈斯克尔称与 Legros 纪念碑项目有关的多份文件保存在 Jesuit Archives，所引定位为 "
            "Ecclesia S. Ignatii de Urbe, 1255；本卡记录书中引用的档案定位，不表示原件已阅。"
        ),
        "original_quotes": [{
            "source_span": "lines 186–187",
            "text": "Many documents relating to this project are preserved in the Jesuit Archives: Ecclesia S.\nIgnatii de Urbe, 1255.",
        }],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": "lines 186–187; print p. 93",
        },
    }]
    frontmatter = {
        "title": "耶稣会档案定位 Ecclesia S. Ignatii de Urbe, 1255（Jesuit Archives reference Ecclesia S. Ignatii de Urbe, 1255）",
        "name_en": "Jesuit Archives reference Ecclesia S. Ignatii de Urbe, 1255",
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第3章 p.93](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md#L186)"
    body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔为 Legros 纪念碑项目所引的耶稣会档案定位：作者称相关多份文件保存在 Jesuit Archives，定位写作 Ecclesia S. Ignatii de Urbe, 1255。此描述性名称代表书中所指的档案定位，不把它扩写为已查阅的单件原件或已确认的完整档案系列。{source_link}

**English:** This card records the Jesuit Archives reference Haskell cites for documents relating to Legros’s monument: Ecclesia S. Ignatii de Urbe, 1255. The descriptive title represents the archival reference as cited in the book; it does not identify a consulted individual document or a verified complete archival series. {source_link}

### 档案定位

| 字段 | 值 | 证据 |
|---|---|---|
| 来源所称保管机构 | Jesuit Archives | 第3章 p.93，L186–187 |
| 原书所引档案标识 | Ecclesia S. Ignatii de Urbe, 1255 | 第3章 p.93，L186–187 |
| 原书概述的材料范围 | 与 Legros 纪念碑项目有关的多份文件；具体文件未在该段列明 | 第3章 p.93，L186–187 |

## 关系与证据

### 关系记录

本卡目前没有已裁决的正式关系。原书关系候选 `{WORK_RELATIONS[0]}` 仍待 S6 逐项审查；此档案定位与纪念碑项目的对应关系尚未登记为正式关系。判断与候选端点见[批次过程记录](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{PROCESS_ANCHOR})。

### 身份与外部链接

本批未查阅档案原件或外部馆藏目录；卡片只记录 Haskell 所引定位及其限定。
"""
    return card_path, f"---\n{fm}---\n\n{body}"


def update_knowledge(text: str) -> str:
    replacements = (
        (
            "| person | 3,464 | 1,158 | 1,067 / 1,168 | 4 | 7 | 1,127 | 765 / 864 | 302 / 304 |",
            "| person | 3,464 | 1,161 | 1,067 / 1,168 | 4 | 7 | 1,124 | 765 / 864 | 302 / 304 |",
            "person current type row",
        ),
        (
            "| place | 1,109 | 228 | 559 / 569 | 0 | 0 | 312 | 43 / 53 | 516 / 516 |",
            "| place | 1,109 | 229 | 558 / 568 | 0 | 0 | 312 | 43 / 53 | 515 / 515 |",
            "place current type row",
        ),
        (
            "| work | 2,397 | 237 | 479 / 495 | 5 | 29 | 1,631 | 51 / 57 | 428 / 438 |",
            "| work | 2,397 | 238 | 478 / 494 | 5 | 29 | 1,631 | 52 / 58 | 426 / 436 |",
            "work current type row",
        ),
        (
            "| **合计** | **12,407** | **1,975** | **4,812 / 5,026** | **9** | **100** | **5,297** | **1,189 / 1,382** | **3,623 / 3,644** |",
            "| **合计** | **12,407** | **1,980** | **4,810 / 5,024** | **9** | **100** | **5,294** | **1,191 / 1,384** | **3,619 / 3,640** |",
            "current type-table total",
        ),
        (
            "5,297项 `undecided`",
            "5,294项 `undecided`",
            "current snapshot undecided",
        ),
        (
            "same的1,975条候选指向1,053个既有KU；new候选组成4,812个类型内身份组，共5,026条映射。",
            "same的1,980条候选指向1,055个既有KU；new候选组成4,810个类型内身份组，共5,024条映射。",
            "current snapshot S3 totals",
        ),
        (
            "3,623组、3,644条成员映射尚待登记。",
            "3,619组、3,640条成员映射尚待登记；S2 10,399条关系候选中330条至少缺一个候选端点（125段：仅缺object 217条、仅缺subject 41条、两端均缺72条）；字段表11,702条，其中1,627条unverified。",
            "current snapshot S4 totals",
        ),
    )
    for old, new, label in replacements:
        text = replace_once(text, old, new, label)

    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S3–S4 跨章人物复用与作品／档案端点批次（2026-10-19）

本批复核五项既有候选身份、登记两个直接关系端点组；未新增正式关系或 S5 外部补足，新增9条 `origin=book`、`source_backed` 结构化字段以对应两张卡的正文表格。

| 候选 | 原决定 | 当前决定／S4去向 | 关键证据与边界 |
|---|---|---|---|
| `cand-1106`、`cand-1108` | undecided | same → `units/persons/galileo-galilei` | G.csv#13、#15 是 Galileo 主项下的 Ludovico Cigoli 与 painting-views 子项；第4章 pp.102–103 的现有人物卡已记录对应原文。索引姓氏前置不构成另一人物。 |
| `cand-2349` | undecided | same → `units/persons/giovanni-da-san-giovanni` | S.csv#37 的倒置姓名及 pp.49、95 与既有人物卡所引的第2章 Baldinucci 注和第4章艺术家名单吻合。 |
| `cand-5945` | new，`workgrp-0efe5e6f22b460` | same → `units/works/poussin-moses-trampling-on-pharaoh-s-crown` | 第4章 p.114 的具体题名、p.115 叙述与既有图版19a作品卡一致；cand-2018、cand-4087 已映射至同一作品。保留原组号与旧理由，不另建卡。 |
| `cand-5439` | new，`sg3-place-cand-5439` | same → `units/places/s-ignazio` | 第3章 p.93 的 S. Ignazio 耶稣会教堂与既有同类型 S. Ignazio 地点卡（罗马）相符；不与 Gesù 内 St Ignatius 礼拜堂合并。 |
| `cand-5457` | new，`workgrp-1a180be8d3050f` | new → [S. Ignazio 纪念碑作品卡](../../../04-knowledge/units/works/pierre-legros-monument-gregory-xv-ludovico-ludovisi.md) | 第3章 p.93 L182、186 将 S. Ignazio、1710年、Pierre Legros、Gregory XV 与 Cardinal Ludovisi 连接为一件作品；当前同类型 manifest 无相同作品。题名为描述性工作题名。 |
| `cand-5458` | new，`archive-group-7630830856b3` | new → [Jesuit Archives 档案定位卡](../../../04-knowledge/units/archives/jesuit-archives-ecclesia-s-ignatii-de-urbe-1255.md) | 第3章 p.93 L186–187 所引 `Ecclesia S. Ignatii de Urbe, 1255` 作为档案定位登记；不表示项目已查阅文件，也不与 `Fondo di Gesù, N. 865-13` 合并。 |

人物三条由 `undecided` 改为 `same`；作品 `cand-5945` 与地点 `cand-5439` 由 `new` 改为 `same`，移除两个重复待登组。新增两个 KU（work 1、archive 1），全部各映射一个候选。S3 当前为 same=1,980（1,055个既有KU）、new=5,024（4,810组）、conflict=9、excluded=100、undecided=5,294（含622项未分类）。S4 已登记1,191组／1,384条映射，待登记3,619组／3,640条映射；直接关系端点待登队列由1,868降至1,864组／候选成员。

本批涉及的10条直接关系候选中，8条现在已有两端 S3/S4 KU 映射，可交 S6 裁决；2条仍受 `cand-5948`（Josephus 身份待证）与 `cand-5965`（Bible archive 尚待S4）影响。S6关系表未新增行，S2中330条缺少候选端点的陈述未变。S3/S4映射只解除端点阻塞，不代表关系已正式成立。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    replacements = (
        ("same=1,975（指向1,053个既有KU）", "same=1,980（指向1,055个既有KU）", "result current same count"),
        ("new=5,026（4,812个身份组）", "new=5,024（4,810个身份组）", "result current new count"),
        ("S4已登记1,189组、映射1,382条成员候选", "S4已登记1,191组、映射1,384条成员候选", "result current registered count"),
        ("尚待登记3,623组、3,644条映射", "尚待登记3,619组、3,640条映射", "result current pending count"),
        ("待登记队列为1,868组／1,868条候选映射", "待登记队列为1,864组／1,864条候选映射", "result current endpoint count"),
        ("KU=2,208", "KU=2,210", "result current KU count"),
        ("S4待登记new候选映射3,644条", "S4待登记new候选映射3,640条", "result audit pending mappings"),
        ("5,297项待证对象仍未解决", "5,294项待证对象仍未解决", "result current unresolved count"),
        ("当前5,297项 `undecided` 中", "当前5,294项 `undecided` 中", "result next S3 backlog count"),
        ("S5字段表11,693条", "S5字段表11,702条", "result current field-table count"),
        ("enrichment=11,693（1,627条unverified）", "enrichment=11,702（1,627条unverified）", "result audit field-table count"),
        ("| [字段表](../tables/enrichment.jsonl) | 11,693条，其中1,627条 unverified |", "| [字段表](../tables/enrichment.jsonl) | 11,702条，其中1,627条 unverified |", "result field-table product row"),
        ("| same | 1,975 | 指向 1,053 个既有 KU |", "| same | 1,980 | 指向 1,055 个既有 KU |", "result S3 same table row"),
        ("| new | 5,026 | 按 4,812 个当前身份组进入 S4；每组登记一个 KU |", "| new | 5,024 | 按 4,810 个当前身份组进入 S4；每组登记一个 KU |", "result S3 new table row"),
        ("| undecided | 5,297 |", "| undecided | 5,294 |", "result S3 undecided table row"),
        ("不代表当前2,208 KU及1,232条关系的发布状态。", "不代表当前2,210 KU及1,232条关系的发布状态。", "result current KU release note"),
        ("312条S2候选至少缺一个端点。", "330条S2候选至少缺一个端点。", "result current missing endpoint count"),
        ("312条S2候选仍至少缺一个端点。", "330条S2候选仍至少缺一个端点。", "result audit missing endpoint count"),
        ("312条至少缺一端的候选留待上游身份／端点补齐", "330条至少缺一端的候选留待上游身份／端点补齐", "result next-step missing endpoint count"),
    )
    if text.count("undecided=5,297") != 2:
        raise AssertionError("expected two current undecided summaries")
    text = text.replace("undecided=5,297", "undecided=5,294")
    for old, new, label in replacements:
        text = replace_once(text, old, new, label)

    text = replace_once(
        text,
        "312条 S2 关系候选至少缺一个端点，分布于126个来源段：仅缺 object 214条、仅缺 subject 31条、两端均缺67条。312条均保留逐行理由，无缺理由开放端点；它们仍是 S2 候选，不是 S6 正式关系。",
        "330条 S2 关系候选至少缺一个端点，分布于125个来源段：仅缺 object 217条、仅缺 subject 41条、两端均缺72条。330条均保留逐行理由，无缺理由开放端点；它们仍是 S2 候选，不是 S6 正式关系。",
        "result current missing endpoint breakdown",
    )

    text = replace_once(
        text,
        "KU 登记](../tables/ku-manifest.csv) | 2,208 KU",
        "KU 登记](../tables/ku-manifest.csv) | 2,210 KU",
        "current KU product row",
    )
    text = replace_once(
        text,
        "same=1,975（1,053个既有KU）、new=5,026（4,812个类型内身份组）",
        "same=1,980（1,055个既有KU）、new=5,024（4,810个类型内身份组）",
        "audit current S3 totals",
    )
    text = replace_once(
        text,
        "S4已登记1,189组／1,382条候选映射，待登记3,623组／3,644条",
        "S4已登记1,191组／1,384条候选映射，待登记3,619组／3,640条",
        "audit current S4 totals",
    )
    text = replace_once(
        text,
        "直接关系端点队列1,868组／1,868条",
        "直接关系端点队列1,864组／1,864条",
        "audit current endpoint count",
    )
    text = replace_once(
        text,
        "person 31／31、institution 96／96、event 144／144、place 233／233、work 342／342、archive 483／483、term 539／539",
        "person 31／31、institution 96／96、event 144／144、place 232／232、work 340／340、archive 482／482、term 539／539",
        "current endpoint type counts",
    )
    text = replace_once(
        text,
        "2026-10-19 `build_cards.py --check` 全量预检通过且未写卡片：2,208张卡",
        "历史预检（2026-10-19、本批前）`build_cards.py --check` 全量预检通过且未写卡片：2,208张卡",
        "mark pre-batch card check historical",
    )

    plan_old = "先处理1,868个待登记组：人物31、机构96、事件144、地点233、作品342、档案483、术语539；再登记其余1,755组。"
    plan_new = "先处理1,864个待登记组：人物31、机构96、事件144、地点232、作品340、档案482、术语539；再登记其余1,755组。"
    text = replace_once(text, plan_old, plan_new, "current S4 endpoint plan")

    heading = "## S3 身份决定与交接\n\n"
    batch = f"""### S3–S4跨章人物与直接关系作品／档案批次（2026-10-19）

人物 `cand-1106`、`cand-1108`、`cand-2349` 复用既有人物 KU；作品 `cand-5945` 与地点 `cand-5439` 由待新增组改为复用既有 KU；作品 `cand-5457` 与档案定位 `cand-5458` 两个新组已登记，见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR})。新增2个KU；10条直接关系候选中8条已有两端KU映射并可交S6，另2条仍待 Josephus 身份与《圣经》档案端点补齐。两张新卡新增9条书内结构字段；未新增正式关系或 S5 外部补足。

"""
    text = replace_once(text, heading, heading + batch, "insert current batch in result")
    return text


def update_root_guide(text: str) -> str:
    old = next(line for line in text.splitlines() if line.startswith("项目版本为初始化阶段的 0.1.0；"))
    new = (
        "项目版本为初始化阶段的 0.1.0；全书 S2 内部处理已完成，尚未独立语义验收。"
        "S3 已为12,407个候选记录现行决定及可追溯去向：same=1,980（指向1,055个既有 KU）、"
        "new=5,024（4,810个身份组）、conflict=9、excluded=100、undecided=5,294（其中622项未分类）；"
        "这表示决定记录覆盖齐全，不表示冲突与待证身份已解决。S4 已登记1,191／4,810个新增身份组（1,384条候选映射），"
        "3,619组／3,640条映射待登记；直接关系端点待登队列为1,864组／1,864条候选映射，其中人物31组、档案482组、"
        "作品340组、地点232组。S2 有10,399条关系候选（relation_candidate=true）；S6关系表有1,232条记录（1,230 formal、"
        "2 pending），二者是不同数据集，现有关系行数不能代表S2候选的逐条裁决覆盖。330条S2关系候选至少缺一个端点。"
        "S5字段表11,702条、其中1,627条unverified；S6关系表45条缺结构化 source_id（44条formal、1条pending）。"
        "S5、S6尚未收口。覆盖、计数与未决项以[全书当前结果](04-knowledge/results/patrons-and-painters-full-book-s2.md)"
        "及其结构化表为准；其中按日期记录的批次段落是历史快照，不作为当前累计数。"
        "[第一章结果](04-knowledge/results/patrons-and-painters-chp-1.md)仅说明独立的历史任务，不由规则版本或文件数量推导全书完成。"
        "知识发现与页面暂停。有效对象见 [accepted.yml](04-knowledge/accepted.yml)；遗留文件与未处理来源不自动成为成果。"
    )
    return replace_once(text, old, new, "root current status")


def add_accepted_paths(text: str, paths):
    lines = text.splitlines()
    for path in sorted(paths):
        if f"- {path}" in lines:
            raise AssertionError(f"accepted path already exists: {path}")
        insert_at = next(
            (i for i, line in enumerate(lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > path),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {path}")
    return "\n".join(lines) + "\n"


def make_process_entry():
    return f"""

<a id="{PROCESS_ANCHOR}"></a>

### S3–S4跨章人物复用与作品／档案端点批次（2026-10-19）

人物复用线索来自索引倒置姓名、主项与子项及既有人物卡的同页证据；不以姓名相似单独判定。`cand-1106`、`cand-1108` → `units/persons/galileo-galilei`：G.csv#13 的 Ludovico Cigoli 子项对应第4章 p.102；G.csv#15 的 painting-views 子项对应 p.103，现有人物卡分别引用这两页。`cand-2349`（S.csv#37，Giovanni da San Giovanni，pp.49、95）→ `units/persons/giovanni-da-san-giovanni`：既有卡分别引用第2章 p.49 的 Baldinucci 注与第4章 p.95 的人名列表。三条索引候选原均为 `undecided`，现由 `same` 映射至有效同类型 KU；原理由留在 alignment 历史注释中。

`cand-5945` 原为 `new`，现复用 `units/works/poussin-moses-trampling-on-pharaoh-s-crown`。第4章 p.114 直接给出《Moses trampling on Pharaoh’s Crown》题名，p.115继续描述同一件作品；已有图版19a work KU 的来源锚点与 `cand-2018`、`cand-4087` 的 same 映射证实这不是新作品。原 `workgrp-0efe5e6f22b460` 作为 `prior_group` 保留，不再进入待登记组。

`cand-5439` 原为 place `new`，现复用 `units/places/s-ignazio`。第3章 p.93将对象称为罗马的 S. Ignazio 耶稣会教堂；既有同类型地点卡的图版15来源称 S. Ignazio, Rome。该教堂与 [Gesù 内的 St Ignatius 礼拜堂](../../../04-knowledge/units/places/gesu-chapel-st-ignatius.md)保持区分；原 `sg3-place-cand-5439` 留作 prior_group。

新增 S4 work 组 `workgrp-1a180be8d3050f`（`cand-5457`）→ `units/works/pierre-legros-monument-gregory-xv-ludovico-ludovisi`，及 archive 组 `archive-group-7630830856b3`（`cand-5458`）→ `units/archives/jesuit-archives-ecclesia-s-ignatii-de-urbe-1255`。两个组均为单成员，已创建双语卡、写入 `ku-manifest.csv` 和 `accepted.yml` 并完成映射。作品卡记录 Haskell 所称 Pierre Legros 于1710年完成、纪念 Gregory XV 与 Cardinal Ludovisi 的 S. Ignazio 纪念碑；档案卡只记录 Haskell 的 `Ecclesia S. Ignatii de Urbe, 1255` 档案定位，未把原件或整组文件写成已查阅。两者均仅依据第3章 p.93；无外部目录／档案访问、S5外部补足或 S6 正式边新增。正文结构表新增9条 `origin=book`、`source_backed` 字段记录；档案定位与既有 `Fondo di Gesù, N. 865-13` 为不同引用，未合并。

本批5条 same 映射、移除2个 S3 new 身份组，并登记2个新 KU。S3 为 same=1,980（1,055个目标KU）、new=5,024（4,810组）、conflict=9、excluded=100、undecided=5,294；S4 已登记1,191组／1,384条映射、待登记3,619组／3,640条映射。直接关系端点待登队列为1,864组／候选成员，其中 work 340、archive 482、place 232。

上述两个身份组各有5条 `relation_candidate=true` 直接陈述；现在共8条具有完整的 S3/S4 端点KU映射，可提交 S6 判断，剩余2条仍被 `cand-5948`（Josephus 身份待证）和 `cand-5965`（Bible archive 新组待登记）阻断。10条陈述均未写入 `relations.csv`；书中仍有330条陈述至少缺一个 candidate endpoint（125段；仅缺object 217条、仅缺subject 41条、两端均缺72条），数量未因本批改变。按全书10,399条关系候选计算，拥有完整端点KU映射的statement由3,885条增至3,893条；这只表示可进入S6审查，不代表formal关系已成立。两张新卡的9行书内结构化字段同步写入 `enrichment.jsonl`，不会增加S5外部核查完成数。
"""


def main():
    parser = argparse.ArgumentParser(description="Reconcile person/work/place reuse and register related work/archive S4 endpoints")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    enrichment_rows = read_jsonl(ENRICHMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = current_candidate_decisions(candidates, alignments)
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    root_guide_text = ROOT_GUIDE_PATH.read_text(encoding="utf-8-sig")
    statements = stats_helper.load_statements()

    before_totals = totals(stats_helper.summarize_by_type(candidates, alignments))
    assert before_totals == {
        "same_candidates": 1975, "same_kus": 1053, "new_candidates": 5026,
        "new_groups": 4812, "registered_groups": 1189, "registered_members": 1382,
        "pending_groups": 3623, "pending_members": 3644, "conflict": 9,
        "excluded": 100, "undecided": 5297, "total": 12407,
    }, before_totals
    assert len(manifest) == 2208
    assert len(alignments) == 12713
    assert len(enrichment_rows) == 11693

    target_cards = {}
    for cid, ruling in SAME_RULINGS.items():
        row = decisions[cid]
        assert row["decision"] == ("new" if cid in {"cand-5945", "cand-5439"} else "undecided"), (cid, row["decision"])
        assert candidate_by_id[cid]["suggested_type"] == manifest_by_id[ruling["target"]]["type"]
        target_cards[cid] = manifest_by_id[ruling["target"]]["card_path"]
        assert (ROOT / target_cards[cid]).is_file(), target_cards[cid]
        old_note = row.get("resolution_note", "")
        prior_group = ruling.get("prior_group", "")
        history = f"; prior_decision={row['decision']}; prior_resolution_note={old_note}"
        if prior_group:
            history += f"; prior_group={prior_group}"
        row["decision"] = "same"
        row["ku_id"] = ruling["target"]
        row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
        row["resolution_note"] = (
            f"source_ref=candidate={cid};index_entry={candidate_by_id[cid].get('index_entry_id','')};"
            f"index_pages={candidate_by_id[cid].get('index_page_range','')}; "
            f"group={ruling['group']}; same_target={ruling['target']}; "
            f"S3 identity ruling {DATE}: {ruling['reason']}{history}"
        )

    # Confirm all source passages used for the person and Poussin reuse decisions.
    source_checks = {
        "02-sources/02-Markdown/04_CHP-4_sec_ii.md": (
            "Galileo himself had been the first to show how a scientific attitude",
            "Galileo’s was a plea for the classical against the Mannerist",
            "Moses trampling on Pharaoh’s Crown",
            "the scene where as a child he accidentally trampled on Pharaoh’s crown",
        ),
        "02-sources/02-Markdown/02_CHP-2_sec_iv.md": (
            "Baldinucci (VI, 1728, pp. 25-7) has a long story of Giovanni da San Giovanni",
        ),
        "02-sources/02-Markdown/04_CHP-4_sec_i.md": (
            "Giovanni da San Giovanni, Filippo Napoletano",
        ),
    }
    for relative, phrases in source_checks.items():
        source = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert all(phrase in source for phrase in phrases), relative
    for cid, target in (("cand-1106", "units/persons/galileo-galilei"),
                        ("cand-1108", "units/persons/galileo-galilei"),
                        ("cand-2349", "units/persons/giovanni-da-san-giovanni")):
        assert decisions[cid]["ku_id"] == target

    # Check the S. Ignazio card is the same place, not the chapel within the Gesù.
    assert decisions["cand-5439"]["ku_id"] == "units/places/s-ignazio"
    assert manifest_by_id["units/places/s-ignazio"]["type"] == "place"
    assert "Chapel of St Ignatius in the Gesù" in manifest_by_id["units/places/gesu-chapel-st-ignatius"]["name_en"]

    planned_manifest = list(manifest)
    for cid, record in NEW_GROUPS.items():
        row = decisions[cid]
        candidate = candidate_by_id[cid]
        assert candidate["suggested_type"] == record["type"]
        assert row["decision"] == "new" and not row.get("ku_id"), (cid, row)
        assert stats_helper.get_group(row.get("resolution_note", "")) == record["group"]
        members = [
            item for item in decisions.values()
            if item["decision"] == "new" and stats_helper.get_group(item.get("resolution_note", "")) == record["group"]
        ]
        assert [item["candidate_id"] for item in members] == [cid], (record["group"], members)
        assert record["ku_id"] not in manifest_by_id
        assert record["card_path"] not in accepted_text
        assert not (ROOT / record["card_path"]).exists()
        exact_duplicates = [
            row for row in manifest if row["type"] == record["type"]
            and (row["name_en"].casefold() == candidate["canonical_name"].casefold()
                 or row["canonical_name"].casefold() == candidate["canonical_name"].casefold())
        ]
        assert not exact_duplicates, (cid, exact_duplicates)
        row["ku_id"] = record["ku_id"]
        row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
        row["resolution_note"] += (
            f" S4 registration {DATE}: mapped {record['group']} to {record['ku_id']}; "
            "direct S2 relation candidates remain for S6."
        )
        planned_manifest.append({
            "ku_id": record["ku_id"], "type": record["type"],
            "canonical_name": candidate["canonical_name"],
            "name_en": (
                "Monument to Pope Gregory XV and Cardinal Ludovico Ludovisi at S. Ignazio"
                if cid == "cand-5457" else
                "Jesuit Archives reference Ecclesia S. Ignatii de Urbe, 1255"
            ),
            "source_task": TASK,
            "card_path": record["card_path"],
        })

    relation_by_id = {
        statement["statement_id"]: statement
        for statement in statements
        if statement.get("statement_id") in set(WORK_RELATIONS) | set(POUSSIN_RELATIONS)
    }
    expected_relations = set(WORK_RELATIONS) | set(POUSSIN_RELATIONS)
    assert set(relation_by_id) == expected_relations
    for sid in expected_relations:
        statement = relation_by_id[sid]
        assert (statement.get("qualifiers") or {}).get("relation_candidate") is True
    for sid in WORK_RELATIONS:
        assert "cand-5457" in (relation_by_id[sid].get("subject_candidate_id"), relation_by_id[sid].get("object_candidate_id"))
    for sid in POUSSIN_RELATIONS:
        assert "cand-5945" in (relation_by_id[sid].get("subject_candidate_id"), relation_by_id[sid].get("object_candidate_id"))

    # Confirm the book text for both new S4 cards and preserve the printed OCR line break.
    chapter = (ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md").read_text(encoding="utf-8-sig")
    assert "In 1710 Pierre Legros completed the monument to Pope Gregory XV and Cardinal Ludovisi in the same church." in chapter
    assert "Many documents relating to this project are preserved in the Jesuit Archives: Ecclesia S.\nIgnatii de Urbe, 1255." in chapter

    after_totals = totals(stats_helper.summarize_by_type(candidates, alignments))
    assert after_totals == {
        "same_candidates": 1980, "same_kus": 1055, "new_candidates": 5024,
        "new_groups": 4810, "registered_groups": 1191, "registered_members": 1384,
        "pending_groups": 3619, "pending_members": 3640, "conflict": 9,
        "excluded": 100, "undecided": 5294, "total": 12407,
    }, after_totals
    assert len(planned_manifest) == 2210

    direct_before = endpoint_pending_by_type(candidates, current_candidate_decisions(candidates, read_csv(ALIGNMENT_PATH)[1]), statements)
    direct_after = endpoint_pending_by_type(candidates, decisions, statements)
    assert direct_before == {
        "person": 31, "institution": 96, "event": 144, "place": 233,
        "work": 342, "archive": 483, "term": 539,
    }, direct_before
    assert direct_after == {
        "person": 31, "institution": 96, "event": 144, "place": 232,
        "work": 340, "archive": 482, "term": 539,
    }, direct_after
    assert sum(direct_before.values()) == 1868 and sum(direct_after.values()) == 1864
    full_before = fully_mapped_relation_ids(current_candidate_decisions(candidates, read_csv(ALIGNMENT_PATH)[1]), statements)
    full_after = fully_mapped_relation_ids(decisions, statements)
    assert len(full_before) == 3885 and len(full_after) == 3893
    assert len(full_after - full_before) == 8
    assert set(WORK_RELATIONS).issubset(full_after)
    assert len(set(POUSSIN_RELATIONS) & full_after) == 3

    missing_breakdown = {"only_object": 0, "only_subject": 0, "both": 0}
    for statement in statements:
        if (statement.get("qualifiers") or {}).get("relation_candidate") is not True:
            continue
        subject_missing = not statement.get("subject_candidate_id")
        object_missing = not statement.get("object_candidate_id")
        if subject_missing and object_missing:
            missing_breakdown["both"] += 1
        elif subject_missing:
            missing_breakdown["only_subject"] += 1
        elif object_missing:
            missing_breakdown["only_object"] += 1
    assert missing_breakdown == {"only_object": 217, "only_subject": 41, "both": 72}

    planned_accepted = add_accepted_paths(accepted_text, [r["card_path"] for r in NEW_GROUPS.values()])
    process_updated = update_knowledge(process_text)
    process_updated = process_updated.rstrip() + make_process_entry()
    result_updated = update_result(result_text)
    root_guide_updated = update_root_guide(root_guide_text)
    card_texts = dict((make_work_card(), make_archive_card()))
    planned_enrichment = append_card_table_fields(card_texts, enrichment_rows)
    assert len(planned_enrichment) == 11702

    if args.dry_run:
        print(
            "dry-run passed: same=5 new-groups-removed=2 new-KU-groups-registered=2 "
            "new-cards=2 book-fields=9/11702 S3-same=1980/1055 new=5024/4810 undecided=5294 "
            "S4-registered=1191/1384 pending=3619/3640 direct-endpoints=1864 "
            "relation-statements-newly-endpoint-complete=8 relation-missing-candidate-endpoints=330"
        )
        return 0

    for card_path, card_text in card_texts.items():
        (ROOT / card_path).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_jsonl(ENRICHMENT_PATH, planned_enrichment)
    write_csv(ALIGNMENT_PATH, alignment_fields, alignments)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_updated, encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_updated, encoding="utf-8", newline="\n")
    ROOT_GUIDE_PATH.write_text(root_guide_updated, encoding="utf-8", newline="\n")
    print(
        "applied: same=5 new-groups-removed=2 new-KU-groups-registered=2 "
        "new-cards=2 book-fields=9/11702 S3-same=1980/1055 new=5024/4810 undecided=5294 "
        "S4-registered=1191/1384 pending=3619/3640 direct-endpoints=1864 "
        "relation-statements-newly-endpoint-complete=8 relation-missing-candidate-endpoints=330"
    )
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
