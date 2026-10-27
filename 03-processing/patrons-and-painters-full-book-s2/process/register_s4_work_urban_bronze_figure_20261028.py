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
RELATION_MATRIX_PATH = ROOT / "01-domain" / "relation-domain-range.yml"
RELATION_TYPES_PATH = ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml"

CANDIDATE = "cand-4532"
GROUP = "workgrp-9139fbaec4193a"
WORK_KU = "units/works/urban-viii-tomb-blessing-bronze-figure"
WORK_CARD_REL = f"04-knowledge/{WORK_KU}.md"
WORK_CARD = ROOT / WORK_CARD_REL
ANCHOR = "s4-s5-s6-chp2-p42-urban-viii-bronze-figure-20261028"
RELATION_IDS = ("rel-2474", "rel-2475")
STATEMENT_PART = "st-chp2-secii-l127-139-urban-tomb-bronze-figure-cast"
STATEMENT_SUBJECT = "st-chp2-secii-l127-139-urban-tomb-bronze-figure-interpretation"
TOMB_KU = "units/works/tomb-of-urban-viii-st-peters"
POPE_KU = "units/persons/urbano-viii"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 2, pp. 41–42."
)
TITLE_ZH = "乌尔班八世墓中的祝福姿态教宗巨型青铜像"
TITLE_EN = "Gigantic Bronze Figure of the Blessing Pope for the Tomb of Urban VIII"


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
        "title": f"{TITLE_ZH}（{TITLE_EN}）",
        "name_en": TITLE_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第2章，印刷页41–42；L125、128–129；PDF物理页27。",
                "sentence_summary": (
                    "Haskell在乌尔班八世墓葬叙述中称，祝福姿态教宗巨像随后以青铜铸成，并描述其高坐于朝圣者之上、右手抬起。"
                    "原文未指明该像的铸造者。"
                ),
                "original_quotes": [
                    {
                        "source_span": "Chapter 2, printed p. 41, line 125",
                        "text": (
                            "Urban VIII’s greatest commission to record his own glory was that for his tomb which he ordered in 1627 after only three years on the throne."
                        ),
                    },
                    {
                        "source_span": "Chapter 2, printed p. 42, lines 128–129",
                        "text": (
                            "Soon afterwards the gigantic bronze figure of the blessing Pope was cast. Grander, more dramatically solemn than in any other representation, he sits far above the pilgrim, cut off even from the allegorical virtues well below, his right hand raised in an authoritative gesture that seems as keen to command or to ward off his enemies as to bless."
                        ),
                    },
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "lines 125, 128–129; printed pp. 41–42",
                },
            }
        ],
        "created": "2026-10-28",
        "updated": "2026-10-28",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = "[第2章 pp.41–42](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L125、128–129；PDF物理页27）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录 Haskell 在乌尔班八世墓葬叙述中称为“the gigantic bronze figure of the blessing Pope”的雕像。印刷页42称该像随后以青铜铸成，并描述教宗高坐于朝圣者之上、右手抬起。该像按原书叙述作为墓葬纪念碑的一部分登记。Haskell没有指明此像的铸造者；本卡不由墓葬总工程的受托关系推定该像由 Bernini 铸造。作者对姿势的象征性阐释仍归于 Haskell。{source}

**English:** This card records the statue Haskell calls “the gigantic bronze figure of the blessing Pope” in his account of Urban VIII’s tomb. On p. 42 he says it was subsequently cast in bronze and describes the Pope seated high above a pilgrim, with his right hand raised. The figure is registered as a component of the tomb monument in the book’s account. Haskell does not name its caster; this card does not infer that Bernini cast it from his responsibility for the overall tomb project. The author’s symbolic interpretation of the pose remains attributed to Haskell. {source}

### 作品信息

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性名称 | 乌尔班八世墓中的祝福姿态教宗巨型青铜像（Gigantic Bronze Figure of the Blessing Pope for the Tomb of Urban VIII）；描述性暂题，非原题 | S1；第2章，印刷页42，L128；PDF物理页27 |
| 作品类型 | 祝福姿态教宗人物像／Figure of the blessing Pope | S1；第2章，印刷页42，L128；PDF物理页27 |
| 材质 | 青铜／Bronze | S1；第2章，印刷页42，L128；PDF物理页27 |
| 技法 | 铸造／Casting | S1；第2章，印刷页42，L128；PDF物理页27 |

## 关系与证据

### 关系记录

本卡记录该青铜像属于乌尔班八世墓葬纪念碑，并以乌尔班八世为表现对象。关系范围限于原书对该像的描述，不补作者归属或实际创作意图。

### S3 身份组

- 候选：`{CANDIDATE}`
- S3决定：`new`；身份组 `{GROUP}`
- 书内来源：第2章，印刷页41–42，L125、128–129
- S4 KU：`{WORK_KU}`
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the S3 work group for Urban VIII's tomb bronze figure and adjudicate its S6 endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    relation_fields, relations = read_csv(RELATIONS_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    alignment = [row for row in alignments if row["candidate_id"] == CANDIDATE]
    assert len(alignment) == 1
    alignment_row = alignment[0]
    assert alignment_row["alignment_id"] == "aln-4715"
    assert alignment_row["decision"] == "new" and not alignment_row["ku_id"]
    assert f"group={GROUP}" in alignment_row["resolution_note"]
    assert candidate["suggested_type"] == "work"
    assert candidate["candidate_source_ref"] == "chp-2:02_CHP-2_sec_ii:l127-139#L128"
    assert not any(row["ku_id"] == WORK_KU or row["card_path"] == WORK_CARD_REL for row in manifest)
    assert not WORK_CARD.exists()
    assert not any(row["relation_id"] in RELATION_IDS for row in relations)
    assert not any(row["subject_ku_id"] == WORK_KU or row["object_ku_id"] == WORK_KU for row in relations)

    statements = {
        row["statement_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    part_statement = statements[STATEMENT_PART]
    subject_statement = statements[STATEMENT_SUBJECT]
    assert part_statement["subject_candidate_id"] == CANDIDATE
    assert part_statement["object_candidate_id"] == "cand-4512"
    assert part_statement["qualifiers"]["relation_candidate"] is True
    assert subject_statement["subject_candidate_id"] == CANDIDATE
    assert subject_statement["object_candidate_id"] == "cand-0236"
    assert subject_statement["qualifiers"]["relation_candidate"] is True
    for statement_id in (STATEMENT_PART, STATEMENT_SUBJECT):
        assert not any(statement_id in row["source_span"] for row in relations)

    ku_ids = {row["ku_id"] for row in manifest}
    assert TOMB_KU in ku_ids and POPE_KU in ku_ids
    type_rows = {row["ku_id"]: row["type"] for row in manifest}
    matrix = yaml.safe_load(RELATION_MATRIX_PATH.read_text(encoding="utf-8"))["domain_range"]
    controlled_types = set(yaml.safe_load(RELATION_TYPES_PATH.read_text(encoding="utf-8"))["types"])
    assert {"part_of", "has_subject"}.issubset(controlled_types)
    assert "work" in matrix["part_of"]["domain"] and "work" in matrix["part_of"]["range"]
    assert "work" in matrix["has_subject"]["domain"] and "person" in matrix["has_subject"]["range"]
    assert type_rows[TOMB_KU] == "work" and type_rows[POPE_KU] == "person"

    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted = yaml.safe_load(accepted_text)
    assert WORK_CARD_REL not in accepted["units"]

    enrichment_lines = ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines()
    enrichment_rows = [json.loads(line) for line in enrichment_lines if line.strip()]
    assert not any(row.get("ku_id") == WORK_KU for row in enrichment_rows)
    next_enrichment = max(int(row["enrichment_id"].split("-")[1]) for row in enrichment_rows) + 1
    next_relation = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    assert next_relation == 2474

    fields = [
        ("描述性名称", f"{TITLE_ZH}（{TITLE_EN}）；描述性暂题，非原题", "内容 / 作品信息"),
        ("作品类型", "祝福姿态教宗人物像／Figure of the blessing Pope", "内容 / 作品信息"),
        ("材质", "青铜／Bronze", "内容 / 作品信息"),
        ("技法", "铸造／Casting", "内容 / 作品信息"),
    ]
    section = "内容 / 作品信息"
    table_id = "tbl-" + hashlib.sha256(
        f"{WORK_KU}|{section}|1|字段|值|证据".encode("utf-8")
    ).hexdigest()[:16]
    evidence = "S1；第2章，印刷页42，L128；PDF物理页27"
    new_enrichment = []
    for offset, (field, value, table_section) in enumerate(fields):
        assert table_section == section
        row_index = offset + 1
        new_enrichment.append({
            "enrichment_id": f"enr-{next_enrichment + offset:05d}",
            "ku_id": WORK_KU,
            "field": field,
            "value": value,
            "origin": "book",
            "source_id": SOURCE_ID,
            "source_ids": [SOURCE_ID],
            "source_ref": "S1",
            "source_citations": [BOOK_CITATION],
            "source_urls": [],
            "evidence": evidence,
            "evidence_status": "source_backed",
            "dispute": None,
            "accessed_date": "",
            "occurrence_id": stable_id("occ", f"{WORK_KU}|{field}"),
            "table_id": table_id,
            "table_section": section,
            "has_header": True,
            "table_header": ["字段", "值", "证据"],
            "row_index": row_index,
            "cells": [field, value, evidence],
            "unit_evidence_status": "source_backed",
        })

    process_ref = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    new_relations = [
        {
            "relation_id": RELATION_IDS[0],
            "subject_ku_id": WORK_KU,
            "object_ku_id": TOMB_KU,
            "predicate": "part_of",
            "time": "",
            "role": "墓葬组成雕像",
            "scope": "仅记录Haskell在墓葬工程叙述中列出的祝福姿态青铜像；不推定该像的铸造者。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 2, printed p. 42, lines 128–129; statement={STATEMENT_PART}",
            "source_file": SOURCE_FILE,
            "note": f"S6 formal; bounded component relation. See {process_ref}.",
        },
        {
            "relation_id": RELATION_IDS[1],
            "subject_ku_id": WORK_KU,
            "object_ku_id": POPE_KU,
            "predicate": "has_subject",
            "time": "",
            "role": "被表现的教宗人物",
            "scope": "仅记录Haskell在Urban VIII墓葬语境中称为祝福教宗的像；不把姿势解释扩展为人物意图或创作者事实。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 2, printed p. 42, line 128; statement={STATEMENT_SUBJECT}",
            "source_file": SOURCE_FILE,
            "note": f"S6 formal; source-bounded subject identification. See {process_ref}.",
        },
    ]

    alignment_row["ku_id"] = WORK_KU
    alignment_row["process_ref"] = process_ref
    alignment_row["resolution_note"] += f" S4 registration: mapped {GROUP} to {WORK_KU}; S6 explicitly adjudicated both source-backed direct candidates."
    manifest.append({
        "ku_id": WORK_KU,
        "type": "work",
        "canonical_name": TITLE_ZH,
        "name_en": TITLE_EN,
        "source_task": TASK,
        "card_path": WORK_CARD_REL,
    })
    relations.extend(new_relations)
    enrichment_rows.extend(new_enrichment)

    units = accepted["units"]
    insert_at = next((i for i, path in enumerate(units) if path > WORK_CARD_REL), len(units))
    units.insert(insert_at, WORK_CARD_REL)
    accepted_lines = accepted_text.splitlines()
    accepted_line = f"- {WORK_CARD_REL}"
    line_insert_at = next((i for i, line in enumerate(accepted_lines) if line.startswith("- ") and line[2:] > WORK_CARD_REL), len(accepted_lines))
    accepted_lines.insert(line_insert_at, accepted_line)

    print(f"S3: retain cand-4532 new / {GROUP}; no identity reopen triggered.")
    print(f"S4: register one source-defined work KU: {WORK_KU}.")
    print("S5: append four Haskell-backed fields: descriptive title, type, material, and technique.")
    print("S6: formal part_of tomb monument and has_subject Urban VIII; caster remains unnamed.")
    print(f"Relations: {RELATION_IDS[0]}, {RELATION_IDS[1]}.")
    print(f"Card: {WORK_CARD_REL}")
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
