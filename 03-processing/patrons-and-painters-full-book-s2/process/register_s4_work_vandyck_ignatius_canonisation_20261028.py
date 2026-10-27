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
CANDIDATE_ID = "cand-5400"
GROUP_ID = "workgrp-3ccf5ad12afead"
KU_ID = "units/works/van-dyck-canonisation-picture-ignatius-1622"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
ANCHOR = "s4-s5-s6-chp3-p91-vandyck-ignatius-canonisation-picture-20261028"
CREATOR_STATEMENT = "st-chp3-seciv-l152-163-van-dyck-painted-canonisation-picture"
INSTALL_STATEMENT = "st-chp3-seciv-l152-163-jesuits-placed-canonisation-picture-above-remains"
CREATOR_RELATION_ID = "rel-2478"
INSTALL_RELATION_ID = "rel-2479"
ARTIST_KU = "units/persons/van-dyck"
CHAPEL_KU = "units/places/gesu-chapel-st-ignatius"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
TITLE_ZH = "范戴克为圣依纳爵1622年册封礼所绘之图像"
TITLE_EN = "Van Dyck's Picture for Ignatius's 1622 Canonisation"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 3, p. 91."
)


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
                "location": "第3章，印刷页91，L154–156；PDF物理页33。",
                "sentence_summary": (
                    "Haskell称圣依纳爵1622年册封时，耶稣会士将其遗骨迁入该礼拜堂，并把Van Dyck为册封礼绘制的图像安置在遗骨上方。"
                ),
                "original_quotes": [
                    {
                        "source_span": "Chapter 3, printed p. 91, lines 154–156",
                        "text": (
                            "When Ignatius was canonised in 1622, they moved his remains to this chapel, "
                            "and above them placed the picture painted for the occasion by Van Dyck."
                        ),
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "lines 154–156; printed p. 91; PDF physical p. 33",
                },
            }
        ],
        "created": "2026-10-28",
        "updated": "2026-10-28",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = "[第3章 p.91](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L154–156；PDF物理页33）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录 Haskell 所述、为圣依纳爵1622年册封礼绘制并于册封时安置在耶稣堂圣依纳爵礼拜堂的 Van Dyck 图像。此为描述性名称，不是原题；原书未给出图像题名、明确描绘题材、作品版本或现藏地。本卡与另有记载的 Van Dyck 圣方济各·沙勿略图像为不同作品。{source}

**English:** This card records the Van Dyck picture Haskell says was painted for Ignatius's 1622 canonisation and placed in the Chapel of St Ignatius in the Gesù on that occasion. This is a descriptive name, not an original title. Haskell supplies no title, explicit depicted subject, version, or present location. This is distinct from the separately reported Van Dyck picture of St Francis Xavier. {source}

### 作品信息

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性名称 | {TITLE_ZH}（{TITLE_EN}）；描述性名称，非原题 | S1；第3章，印刷页91，L154–156；PDF物理页33 |
| 作品类型 | 绘画／Painting | S1；第3章，印刷页91，L156；PDF物理页33 |
| 关联场合 | 圣依纳爵1622年册封 | S1；第3章，印刷页91，L156；PDF物理页33 |

## 关系与证据

### 关系记录

"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Register Van Dyck's 1622 canonisation picture and adjudicate its direct S6 candidates.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    relation_fields, relations = read_csv(RELATIONS_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    _, mentions = read_csv(TABLES / "mentions.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE_ID)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    candidate_alignments = [row for row in alignments if row["candidate_id"] == CANDIDATE_ID]
    assert len(candidate_alignments) == 1
    alignment = candidate_alignments[0]
    assert alignment["alignment_id"] == "aln-5581"
    assert alignment["decision"] == "new" and not alignment["ku_id"]
    assert f"group={GROUP_ID}" in alignment["resolution_note"]
    assert candidate["suggested_type"] == "work"
    assert candidate["candidate_source_ref"] == "chp-3:03_CHP-3_sec_iv:l152-163#L156"
    aligned_endpoints = {row["candidate_id"]: row for row in alignments}
    assert aligned_endpoints["cand-0960"]["decision"] == "same"
    assert aligned_endpoints["cand-0960"]["ku_id"] == ARTIST_KU
    assert aligned_endpoints["cand-3403"]["decision"] == "same"
    assert aligned_endpoints["cand-3403"]["ku_id"] == "units/institutions/jesuits"
    assert aligned_endpoints["cand-5236"]["decision"] == "new"
    assert aligned_endpoints["cand-5236"]["ku_id"] == CHAPEL_KU
    assert mention_by_id["m-chp3-seciv-l152-163-0031"]["candidate_id"] == "cand-0960"
    assert mention_by_id["m-chp3-seciv-l152-163-0031"]["surface_form"] == "Van Dyck"
    assert mention_by_id["m-chp3-seciv-l152-163-0029"]["candidate_id"] == "cand-5236"
    assert mention_by_id["m-chp3-seciv-l152-163-0029"]["surface_form"] == "this chapel"
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_REL for row in manifest)
    assert not CARD_PATH.exists()
    assert not any(row["relation_id"] in {CREATOR_RELATION_ID, INSTALL_RELATION_ID} for row in relations)
    assert not any(row["subject_ku_id"] == KU_ID or row["object_ku_id"] == KU_ID for row in relations)

    statements = {
        row["statement_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    creator = statements[CREATOR_STATEMENT]
    placement = statements[INSTALL_STATEMENT]
    assert creator["subject_candidate_id"] == "cand-0960"
    assert creator["object_candidate_id"] == CANDIDATE_ID
    assert creator["qualifiers"]["relation_candidate"] is True
    assert placement["subject_candidate_id"] == "cand-3403"
    assert placement["object_candidate_id"] == CANDIDATE_ID
    assert placement["qualifiers"]["relation_candidate"] is True
    for statement_id in (CREATOR_STATEMENT, INSTALL_STATEMENT):
        assert not any(statement_id in row["source_span"] for row in relations)

    unit_types = {row["ku_id"]: row["type"] for row in manifest}
    assert unit_types[ARTIST_KU] == "person"
    assert unit_types[CHAPEL_KU] == "place"
    assert any(row["candidate_id"] == "cand-5236" and row["ku_id"] == CHAPEL_KU for row in alignments)
    matrix = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))["domain_range"]
    controlled_types = set(yaml.safe_load((ROOT / ".agents" / "skills" / "ingest" / "references" / "relation-types.yml").read_text(encoding="utf-8"))["types"])
    assert {"created_by", "installed_at"}.issubset(controlled_types)
    assert "work" in matrix["created_by"]["domain"] and "person" in matrix["created_by"]["range"]
    assert "work" in matrix["installed_at"]["domain"] and "place" in matrix["installed_at"]["range"]

    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted = yaml.safe_load(accepted_text)
    assert CARD_REL not in accepted["units"]
    enrichment_rows = [json.loads(line) for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    assert not any(row.get("ku_id") == KU_ID for row in enrichment_rows)
    next_enrichment = max(int(row["enrichment_id"].split("-")[1]) for row in enrichment_rows) + 1
    next_relation = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    assert next_enrichment == 18526 and next_relation == 2478

    section = "内容 / 作品信息"
    table_id = "tbl-" + hashlib.sha256(f"{KU_ID}|{section}|1|字段|值|证据".encode("utf-8")).hexdigest()[:16]
    evidence_rows = [
        ("描述性名称", f"{TITLE_ZH}（{TITLE_EN}）；描述性名称，非原题", "S1；第3章，印刷页91，L154–156；PDF物理页33"),
        ("作品类型", "绘画／Painting", "S1；第3章，印刷页91，L156；PDF物理页33"),
        ("关联场合", "圣依纳爵1622年册封", "S1；第3章，印刷页91，L156；PDF物理页33"),
    ]
    new_enrichment = []
    citation = BOOK_CITATION
    for offset, (field, value, evidence) in enumerate(evidence_rows):
        new_enrichment.append({
            "enrichment_id": f"enr-{next_enrichment + offset:05d}",
            "ku_id": KU_ID,
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
            "occurrence_id": stable_id("occ", f"{KU_ID}|{field}"),
            "table_id": table_id,
            "table_section": section,
            "has_header": True,
            "table_header": ["字段", "值", "证据"],
            "row_index": offset + 1,
            "cells": [field, value, evidence],
            "unit_evidence_status": "source_backed",
        })

    process_ref = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    new_relations = [
        {
            "relation_id": CREATOR_RELATION_ID,
            "subject_ku_id": KU_ID,
            "object_ku_id": ARTIST_KU,
            "predicate": "created_by",
            "time": "",
            "role": "画家",
            "scope": "Haskell称该图像由Van Dyck为圣依纳爵1622年册封礼绘制；不将描述性卡名视为原题，也未独立核验作者归属。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 3, printed p. 91, line 156; statement={CREATOR_STATEMENT}; mention=m-chp3-seciv-l152-163-0031",
            "source_file": SOURCE_FILE,
            "note": f"S6 formal; source-bounded creator attribution. See {process_ref}.",
        },
        {
            "relation_id": INSTALL_RELATION_ID,
            "subject_ku_id": KU_ID,
            "object_ku_id": CHAPEL_KU,
            "predicate": "installed_at",
            "time": "1622年圣依纳爵册封时（Haskell所述）",
            "role": "历史安置地点",
            "scope": "仅记录Haskell称该图像在圣依纳爵1622年册封时被安置于耶稣堂圣依纳爵礼拜堂；不表示现藏地，也不把遗骨作为独立关系端点。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 3, printed p. 91, line 156; statement={INSTALL_STATEMENT}; mention=m-chp3-seciv-l152-163-0029",
            "source_file": SOURCE_FILE,
            "note": f"S6 formal; historical placement only, not a present-location claim. See {process_ref}.",
        },
    ]

    alignment["ku_id"] = KU_ID
    alignment["process_ref"] = process_ref
    alignment["resolution_note"] += (
        f" S4 registration: mapped {GROUP_ID} to {KU_ID}; the work is distinct from "
        "the separately registered Van Dyck picture of St Francis Xavier. S6 records source-bounded creator and 1622 historical installation relations."
    )
    manifest.append({
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": TITLE_ZH,
        "name_en": TITLE_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    relations.extend(new_relations)
    enrichment_rows.extend(new_enrichment)
    units = accepted["units"]
    insert_at = next((i for i, path in enumerate(units) if path > CARD_REL), len(units))
    units.insert(insert_at, CARD_REL)
    accepted_lines = accepted_text.splitlines()
    line_insert_at = next((i for i, line in enumerate(accepted_lines) if line.startswith("- ") and line[2:] > CARD_REL), len(accepted_lines))
    accepted_lines.insert(line_insert_at, f"- {CARD_REL}")

    print(f"S3: retain {CANDIDATE_ID} new / {GROUP_ID}; distinguish from the St Francis Xavier picture.")
    print(f"S4: register one work KU: {KU_ID}.")
    print("S5: append descriptive name, painting type, and source-reported 1622 occasion.")
    print("S6: created_by and historical installed_at are formal; neither asserts an original title or present location.")
    print(f"Relations: {CREATOR_RELATION_ID}, {INSTALL_RELATION_ID}.")
    if args.dry_run:
        return

    CARD_PATH.write_text(card_text(), encoding="utf-8", newline="\n")
    write_csv(ALIGNMENT_PATH, alignment_fields, alignments)
    write_csv(MANIFEST_PATH, manifest_fields, manifest)
    write_csv(RELATIONS_PATH, relation_fields, relations)
    encoding = "utf-8-sig" if ENRICHMENT_PATH.read_bytes().startswith(b"\xef\xbb\xbf") else "utf-8"
    ENRICHMENT_PATH.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in enrichment_rows) + "\n", encoding=encoding, newline="\n")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8")
    print("Applied S4/S5/S6 registration; inspect with build_cards.py --preview.")


if __name__ == "__main__":
    main()
