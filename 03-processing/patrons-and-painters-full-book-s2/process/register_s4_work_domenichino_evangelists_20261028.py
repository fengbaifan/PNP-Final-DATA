from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

from register_s4_event_pantheon_st_joseph_exhibition_20261016 import read_csv

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
MENTIONS_PATH = TABLES / "mentions.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
RELATIONS_PATH = TABLES / "relations.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"

PERSON_CANDIDATE = "cand-1660"
INDEX_WORK_CANDIDATE = "cand-1661"
BODY_WORK_CANDIDATE = "cand-10437"
WORK_CANDIDATE = "cand-5066"
WORK_GROUP = "workgrp-7a7cc80a0bb94c"
RELATED_WORK_GROUP = "workgrp-115824c7c6bcea"
WORK_KU = "units/works/domenichino-evangelist-figures-sant-andrea-della-valle"
WORK_CARD_REL = f"04-knowledge/{WORK_KU}.md"
WORK_CARD = ROOT / WORK_CARD_REL
ANCHOR = "s3-s4-s5-s6-chp3-p72-domenichino-evangelist-figures-20261028"
RELATION_IDS = ("rel-2468", "rel-2469")
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
SOURCE_ID = "haskell-1980-rev-ed"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def read_statement_lines() -> tuple[list[str], list[dict], bool]:
    raw_bytes = STATEMENTS_PATH.read_bytes()
    has_bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    raw_lines = raw_bytes.decode("utf-8-sig").splitlines()
    rows = [json.loads(line) for line in raw_lines if line.strip()]
    return raw_lines, rows, has_bom


def write_csv_preserving_encoding(path: Path, fields: list[str], rows: list[dict]) -> None:
    has_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    encoding = "utf-8-sig" if has_bom else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def card_text() -> str:
    frontmatter = {
        "title": "圣安德烈堂穹隅四福音书作者像（Four Evangelist Figures in the Pendentives of S. Andrea della Valle）",
        "name_en": "Four Evangelist Figures in the Pendentives of S. Andrea della Valle",
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 72.",
                "location": "第3章，印刷页72 L80；PDF物理页10。",
                "sentence_summary": (
                    "Haskell称 Domenichino 在 S. Andrea della Valle 的穹隅制作四位纪念性福音书作者像，"
                    "并将其描述为明显源自 Michelangelo。"
                ),
                "original_quotes": [
                    {
                        "source_span": "line 80; print p. 72",
                        "text": "he produced in the pendentives four monumental figures of the Evangelists, clearly derived from Michelangelo",
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "line 80; print p. 72; PDF physical p. 10",
                },
            }
        ],
        "created": "2026-10-28",
        "updated": "2026-10-28",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source = "[第3章 p.72](../../../02-sources/02-Markdown/03_CHP-3_sec_ii.md)（L80；PDF物理页10）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录 Haskell 所述 Domenichino 在 S. Andrea della Valle 穹隅制作的四位纪念性福音书作者像，按来源共同描述保留为一个作品组，不拆分为四件作品，也不把描述性名称当作原题。Haskell 称这些形象“明显源自 Michelangelo”；这是作者的艺术史判断，本卡不将其表述为已独立验证的影响事实。{source}

**English:** This unit records the group of four monumental Evangelist figures that Haskell says Domenichino produced in the pendentives of S. Andrea della Valle. The figures remain one source-defined group rather than four separate works, and the descriptive title is not treated as an original title. Haskell describes them as “clearly derived from Michelangelo”; this is the author's art-historical interpretation, not an independently verified influence claim. {source}

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 描述性名称 | 圣安德烈堂穹隅四福音书作者像（Four Evangelist Figures in the Pendentives of S. Andrea della Valle）；来源描述性名称 | S1；第3章，印刷页72 L80 |

### 基本信息

| 字段 | 值 | 证据 |
|---|---|---|
| 作品类型 | 穹隅中的四位纪念性福音书作者像；按来源作为一个作品组登记 | S1；第3章，印刷页72 L80 |
| 表现对象 | 四位福音书作者；来源未逐一命名 | S1；第3章，印刷页72 L80 |
| 书中位置 | S. Andrea della Valle 的穹隅 | S1；第3章，印刷页72 L80 |

## 关系与证据

### 关系记录

### S3 身份组

- 候选：`{WORK_CANDIDATE}`
- S3决定：`new`；身份组 `{WORK_GROUP}`
- 书内来源：第3章，印刷页72 L80；PDF物理页10
- S4 KU：`{WORK_KU}`

### 关系候选入口

两项关系候选的 S6 裁决依据及证据边界见[批次过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the S. Andrea della Valle Evangelist figures work group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    mention_fields, mentions = read_csv(MENTIONS_PATH)
    relation_fields, relations = read_csv(RELATIONS_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    statement_lines, statements, statements_have_bom = read_statement_lines()
    statement_by_id = {row["statement_id"]: row for row in statements}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert candidate_by_id[PERSON_CANDIDATE]["suggested_type"] == "person"
    assert candidate_by_id[INDEX_WORK_CANDIDATE]["suggested_type"] == "work"
    assert candidate_by_id[BODY_WORK_CANDIDATE]["suggested_type"] == "work"
    assert candidate_by_id[WORK_CANDIDATE]["suggested_type"] == "work"
    index_row = decision_by_id[INDEX_WORK_CANDIDATE]
    assert index_row["alignment_id"] == "aln-1996" and index_row["decision"] == "undecided"
    body_group = decision_by_id[BODY_WORK_CANDIDATE]
    assert body_group["decision"] == "new" and not body_group.get("ku_id")
    assert f"group={RELATED_WORK_GROUP}" in body_group["resolution_note"]
    work_row = decision_by_id[WORK_CANDIDATE]
    assert work_row["alignment_id"] == "aln-5249" and work_row["decision"] == "new"
    assert f"group={WORK_GROUP}" in work_row["resolution_note"]
    assert not work_row.get("ku_id")
    assert decision_by_id[PERSON_CANDIDATE]["decision"] == "same"
    assert decision_by_id[PERSON_CANDIDATE]["ku_id"] == "units/persons/michelangelo"
    assert not any(row.get("ku_id") == WORK_KU or row.get("card_path") == WORK_CARD_REL for row in manifest)
    assert not WORK_CARD.exists()
    assert WORK_CARD_REL not in accepted_text

    mention = next(row for row in mentions if row["mention_id"] == "m-chp3-secii-l74-81-0043")
    assert mention["candidate_id"] == INDEX_WORK_CANDIDATE and mention["surface_form"] == "Michelangelo"
    creator_statement = statement_by_id["st-chp3-secii-l74-81-domenichino-produced-evangelist-figures"]
    influence_statement = statement_by_id["st-chp3-secii-l74-81-evangelist-figures-derived-from-michelangelo"]
    assert creator_statement["subject_candidate_id"] == "cand-0934"
    assert creator_statement["object_candidate_id"] == WORK_CANDIDATE
    assert influence_statement["subject_candidate_id"] == WORK_CANDIDATE
    assert influence_statement["object_candidate_id"] == INDEX_WORK_CANDIDATE
    assert influence_statement["qualifiers"]["interpretation_by_candidate_id"] == INDEX_WORK_CANDIDATE
    assert influence_statement["qualifiers"]["relation_candidate"] is True

    s3_match_note = (
        "source_ref=entity-candidates.csv#cand-1661;index_entry=M.csv#201;index_source=M.csv;index_pages=362;"
        "sub_entry=Risen Christ (in Santa Maria sopra Minerva, Rome);matched_candidate=cand-10437;"
        "matched_source=chp-15:15_CHP-15_sec_i:l16-25#L21[Michelangelo’s Risen Christ in Santa Maria sopra Minerva];"
        f"group={RELATED_WORK_GROUP}; S3 targeted resolution (2026-10-28): the index sub-entry and the explicit p.362 body title/location identify the same source-level work. "
        "Use cand-10437's new work group; no existing exact work KU or external work record was identified. "
        "The unrelated p.72 Michelangelo artist mention was corrected to person candidate cand-1660."
    )
    assert sum(row.get("candidate_id") == INDEX_WORK_CANDIDATE and not row.get("external_source") for row in alignments) == 1
    assert sum(row.get("candidate_id") == WORK_CANDIDATE and not row.get("external_source") for row in alignments) == 1

    for sid in (
        "st-chp3-secii-l74-81-domenichino-produced-evangelist-figures",
        "st-chp3-secii-l74-81-evangelist-figures-derived-from-michelangelo",
    ):
        assert not any(row.get("source_span", "").endswith(f"statement={sid}") for row in relations)
    assert all(relation_id not in {row.get("relation_id") for row in relations} for relation_id in RELATION_IDS)
    assert len(relations) > 0

    print("S3: cand-1661 -> new / existing source-level group workgrp-115824c7c6bcea (cand-10437).")
    print("S2: remap one Michelangelo mention and one influence-statement endpoint to person cand-1660.")
    print(f"S4: map cand-5066 / {WORK_GROUP} to {WORK_KU}.")
    print("S5: extract four Haskell source-backed fields from the new work card.")
    print("S6: append created_by and influenced_by formal rows for the two cited statements.")
    print(f"New relation IDs: {', '.join(RELATION_IDS)}")
    if args.dry_run:
        return

    index_row["decision"] = "new"
    index_row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    index_row["resolution_note"] = s3_match_note
    mention["candidate_id"] = PERSON_CANDIDATE
    mention["note"] = "Artist from whom Haskell says the figures were derived; mapped to the person candidate, not the Risen Christ work index entry."
    influence_statement["object_candidate_id"] = PERSON_CANDIDATE
    influence_statement["qualifiers"]["interpretation_by_candidate_id"] = PERSON_CANDIDATE
    work_row["ku_id"] = WORK_KU
    work_row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    work_row["resolution_note"] += f" S4 registration: mapped {WORK_GROUP} to {WORK_KU}."

    manifest.append({
        "ku_id": WORK_KU,
        "type": "work",
        "canonical_name": "圣安德烈堂穹隅四福音书作者像",
        "name_en": "Four Evangelist Figures in the Pendentives of S. Andrea della Valle",
        "source_task": TASK,
        "card_path": WORK_CARD_REL,
    })
    relation_rows = [
        {
            "relation_id": RELATION_IDS[0],
            "subject_ku_id": WORK_KU,
            "object_ku_id": "units/persons/domenichino",
            "predicate": "created_by",
            "time": "",
            "role": "Haskell书内报告中的创作者归属",
            "scope": "第3章称 Domenichino 在 S. Andrea della Valle 穹隅制作四位福音书作者像；此边记录书内归属，不表示已由外部作品目录核验。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": "Chapter 3, printed p. 72 L80; statement=st-chp3-secii-l74-81-domenichino-produced-evangelist-figures",
            "source_file": SOURCE_FILE,
            "note": "S6 formal; direct creator statement in Haskell's account.",
        },
        {
            "relation_id": RELATION_IDS[1],
            "subject_ku_id": WORK_KU,
            "object_ku_id": "units/persons/michelangelo",
            "predicate": "influenced_by",
            "time": "",
            "role": "Haskell书内艺术史解释",
            "scope": "Haskell称四位福音书作者像 clearly derived from Michelangelo；记录作者的来源限定判断，不声称外部独立验证或已知直接传承路径。",
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": "Chapter 3, printed p. 72 L80; statement=st-chp3-secii-l74-81-evangelist-figures-derived-from-michelangelo",
            "source_file": SOURCE_FILE,
            "note": "S6 formal as Haskell's source-level interpretation only.",
        },
    ]
    relations.extend(relation_rows)
    WORK_CARD.write_text(card_text(), encoding="utf-8")
    write_csv_preserving_encoding(ALIGNMENT_PATH, alignment_fields, alignments)
    write_csv_preserving_encoding(MANIFEST_PATH, manifest_fields, manifest)
    write_csv_preserving_encoding(MENTIONS_PATH, mention_fields, mentions)
    write_csv_preserving_encoding(RELATIONS_PATH, relation_fields, relations)
    updated_statement_lines: list[str] = []
    for raw_line in statement_lines:
        row = json.loads(raw_line) if raw_line.strip() else None
        if row and row.get("statement_id") == influence_statement["statement_id"]:
            raw_line = json.dumps(influence_statement, ensure_ascii=False)
        updated_statement_lines.append(raw_line)
    statement_encoding = "utf-8-sig" if statements_have_bom else "utf-8"
    STATEMENTS_PATH.write_text("\n".join(updated_statement_lines) + "\n", encoding=statement_encoding)
    accepted = yaml.safe_load(accepted_text)
    units = accepted["units"]
    assert isinstance(units, list)
    insert_at = next((i for i, path in enumerate(units) if path > WORK_CARD_REL), len(units))
    units.insert(insert_at, WORK_CARD_REL)
    old_lines = accepted_text.splitlines()
    accepted_line = f"- {WORK_CARD_REL}"
    line_insert_at = next((i for i, line in enumerate(old_lines) if line.startswith("- ") and line[2:] > WORK_CARD_REL), len(old_lines))
    old_lines.insert(line_insert_at, accepted_line)
    ACCEPTED_PATH.write_text("\n".join(old_lines) + "\n", encoding="utf-8")
    print("Applied the targeted S2/S3/S4/S6 batch. Run build_field_facts preview before apply.")


if __name__ == "__main__":
    main()
