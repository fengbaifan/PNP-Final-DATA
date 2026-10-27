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

CANDIDATE = "cand-5549"
GROUP = "workgrp-d9b4a51552812a"
WORK_KU = "units/works/paolo-giordano-ii-medal-portrait-1631"
WORK_CARD_REL = f"04-knowledge/{WORK_KU}.md"
WORK_CARD = ROOT / WORK_CARD_REL
ANCHOR = "s4-s5-s6-chp4-p97-paolo-giordano-ii-medal-20261028"
FORMAL_RELATION_ID = "rel-2476"
PENDING_RELATION_ID = "rel-2477"
STATEMENT_SUBJECT = "st-chp4-sec-i-l26-33-medal-1631"
STATEMENT_ATTRIBUTION = "st-chp4-sec-i-l26-33-medal-attribution"
PAOLO_KU = "units/persons/paolo-giordano-ii-orsini"
MAKER_KU = "units/persons/giulio-della-greca"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/04_CHP-4_sec_i.md"
TITLE_ZH = "保罗·焦尔达诺二世肖像奖章（1631）"
TITLE_EN = "Medal Portrait of Paolo Giordano II (1631)"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 4, p. 97."
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
                "location": "第4章，印刷页97，L28；PDF物理页4。",
                "sentence_summary": (
                    "Haskell称1631年再次见到Paolo Giordano II的一枚神采生动的奖章，并以perhaps限定其可能由Giulio della Greca制作。"
                ),
                "original_quotes": [
                    {
                        "source_span": "Chapter 4, printed p. 97, line 28",
                        "text": "In 1631, however, we see him once more in a superbly spirited medal perhaps by Giulio della Greca2",
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "line 28; printed p. 97; PDF physical p. 4",
                },
            }
        ],
        "created": "2026-10-28",
        "updated": "2026-10-28",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = "[第4章 p.97](../../../02-sources/02-Markdown/04_CHP-4_sec_i.md)（L28；PDF物理页4）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录 Haskell 在谈及保罗·焦尔达诺二世时提到的1631年肖像奖章。原文称“we see him once more”于奖章中出现，语境将被表现者指向 Paolo Giordano II。Haskell称奖章“superbly spirited”，并以“perhaps”表示可能由 Giulio della Greca 制作；此制作归属尚非确定事实。该奖章与随后提及的 Paolo 及其妻 Isabella 大理石胸像组为不同对象。{source}

**English:** This card records the 1631 medal Haskell mentions while discussing Paolo Giordano II. The phrase “we see him once more” in the medal identifies Paolo as its represented subject in context. Haskell calls it “superbly spirited” and qualifies Giulio della Greca as its possible maker with “perhaps”; that attribution is not treated as certain. This medal is distinct from the marble busts of Paolo and his wife Isabella mentioned later in the passage. {source}

### 作品信息

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性名称 | {TITLE_ZH}（{TITLE_EN}）；描述性暂题，非原题 | S1；第4章，印刷页97 L28 |
| 作品类型 | 肖像奖章／Portrait medal | S1；第4章，印刷页97 L28 |
| 书中年代 | 1631 | S1；第4章，印刷页97 L28 |

## 关系与证据

### 关系记录

Paolo Giordano II 为被表现者，正式关系仅记录这一来源所述对象关系。Giulio della Greca 的制作归属为 Haskell 明确限定的可能性，作为待证关系保留。

### S3 身份组

- 候选：`{CANDIDATE}`
- S3决定：`new`；身份组 `{GROUP}`
- 书内来源：第4章，印刷页97 L28；PDF物理页4
- S4 KU：`{WORK_KU}`
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the 1631 medal work group and adjudicate its two S6 candidates.")
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
    assert alignment_row["alignment_id"] == "aln-5730"
    assert alignment_row["decision"] == "new" and not alignment_row["ku_id"]
    assert f"group={GROUP}" in alignment_row["resolution_note"]
    assert candidate["suggested_type"] == "work"
    assert candidate["candidate_source_ref"] == "chp-4:04_CHP-4_sec_i:l26-33#L28"
    assert not any(row["ku_id"] == WORK_KU or row["card_path"] == WORK_CARD_REL for row in manifest)
    assert not WORK_CARD.exists()
    assert not any(row["relation_id"] in {FORMAL_RELATION_ID, PENDING_RELATION_ID} for row in relations)
    assert not any(row["subject_ku_id"] == WORK_KU or row["object_ku_id"] == WORK_KU for row in relations)

    statements = {
        row["statement_id"]: row
        for row in (
            json.loads(line)
            for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    subject_statement = statements[STATEMENT_SUBJECT]
    attribution_statement = statements[STATEMENT_ATTRIBUTION]
    assert subject_statement["subject_candidate_id"] == "cand-0428"
    assert subject_statement["object_candidate_id"] == CANDIDATE
    assert subject_statement["qualifiers"]["relation_candidate"] is True
    assert attribution_statement["subject_candidate_id"] == "cand-5548"
    assert attribution_statement["object_candidate_id"] == CANDIDATE
    assert attribution_statement["qualifiers"]["relation_candidate"] is True
    for statement_id in (STATEMENT_SUBJECT, STATEMENT_ATTRIBUTION):
        assert not any(statement_id in row["source_span"] for row in relations)

    ku_ids = {row["ku_id"] for row in manifest}
    assert PAOLO_KU in ku_ids and MAKER_KU in ku_ids
    unit_types = {row["ku_id"]: row["type"] for row in manifest}
    matrix = yaml.safe_load(RELATION_MATRIX_PATH.read_text(encoding="utf-8"))["domain_range"]
    controlled_types = set(yaml.safe_load(RELATION_TYPES_PATH.read_text(encoding="utf-8"))["types"])
    assert {"has_subject", "created_by"}.issubset(controlled_types)
    assert "work" in matrix["has_subject"]["domain"] and "person" in matrix["has_subject"]["range"]
    assert "work" in matrix["created_by"]["domain"] and "person" in matrix["created_by"]["range"]
    assert unit_types[PAOLO_KU] == "person" and unit_types[MAKER_KU] == "person"

    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted = yaml.safe_load(accepted_text)
    assert WORK_CARD_REL not in accepted["units"]
    enrichment_lines = ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines()
    enrichment_rows = [json.loads(line) for line in enrichment_lines if line.strip()]
    assert not any(row.get("ku_id") == WORK_KU for row in enrichment_rows)
    next_enrichment = max(int(row["enrichment_id"].split("-")[1]) for row in enrichment_rows) + 1
    next_relation = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    assert next_relation == 2476

    section = "内容 / 作品信息"
    table_id = "tbl-" + hashlib.sha256(
        f"{WORK_KU}|{section}|1|字段|值|证据".encode("utf-8")
    ).hexdigest()[:16]
    evidence = "S1；第4章，印刷页97，L28；PDF物理页4"
    new_enrichment = []
    for offset, (field, value) in enumerate([
        ("描述性名称", f"{TITLE_ZH}（{TITLE_EN}）；描述性暂题，非原题"),
        ("作品类型", "肖像奖章／Portrait medal"),
        ("书中年代", "1631"),
    ]):
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
            "row_index": offset + 1,
            "cells": [field, value, evidence],
            "unit_evidence_status": "source_backed",
        })

    process_ref = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    new_relations = [
        {
            "relation_id": FORMAL_RELATION_ID,
            "subject_ku_id": WORK_KU,
            "object_ku_id": PAOLO_KU,
            "predicate": "has_subject",
            "time": "1631（原书所述奖章年代）",
            "role": "被表现者",
            "scope": "仅记录Haskell称在奖章中再次看到Paolo Giordano II；不对奖章实物版本作外部确认。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 4, printed p. 97, line 28; statement={STATEMENT_SUBJECT}",
            "source_file": SOURCE_FILE,
            "note": f"S6 formal; source-bounded depicted-subject relation. See {process_ref}.",
        },
        {
            "relation_id": PENDING_RELATION_ID,
            "subject_ku_id": WORK_KU,
            "object_ku_id": MAKER_KU,
            "predicate": "created_by",
            "time": "",
            "role": "Haskell所述的可能制作者",
            "scope": "Haskell用“perhaps”限定Giulio della Greca的制作者归属；待独立来源确认，不将可能归属表述为确定创作事实。",
            "origin": "book",
            "status": "pending",
            "source_id": SOURCE_ID,
            "source_span": f"Chapter 4, printed p. 97, line 28; statement={STATEMENT_ATTRIBUTION}",
            "source_file": SOURCE_FILE,
            "note": f"S6 pending; source itself qualifies the attribution as possible. See {process_ref}.",
        },
    ]

    alignment_row["ku_id"] = WORK_KU
    alignment_row["process_ref"] = process_ref
    alignment_row["resolution_note"] += f" S4 registration: mapped {GROUP} to {WORK_KU}; S6 formalized the represented subject and retained the qualified maker attribution as pending."
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

    print(f"S3: retain cand-5549 new / {GROUP}; no identity reopen triggered.")
    print(f"S4: register one work KU: {WORK_KU}.")
    print("S5: append three Haskell-backed fields: descriptive title, medal type, and book-reported year.")
    print("S6: has_subject formal for Paolo Giordano II; created_by pending because Haskell says 'perhaps'.")
    print(f"Relations: {FORMAL_RELATION_ID} formal, {PENDING_RELATION_ID} pending.")
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
