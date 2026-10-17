from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE3 = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
SOURCE20 = "02-sources/02-Markdown/20_CHP-20Postscript.md"
CANDIDATE = "cand-1427"
GROUP = "new-person:elder-longhi-martino-e7aa738609"
KU = "units/persons/martino-longhi-elder"
CARD = "04-knowledge/units/persons/martino-longhi-elder.md"
ANCHOR = "s4-person-martino-longhi-elder-20261017"
STATEMENTS = {
    "st-chp3-secii-l40-52-longhi-replaces-matteo",
    "st-chp20-p400-bonadonna-russo-longhi-and-angelo-cesi",
}


def insert_accepted(lines: list[str], card_path: str) -> list[str]:
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    entry = f"- {card_path}"
    assert entry not in lines
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_path),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def make_card() -> str:
    metadata = {
        "title": "马蒂诺·隆吉（长者）（Martino Longhi the Elder）",
        "name_en": "Martino Longhi the Elder",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "第3章 p.69；S2 L46",
                "sentence_summary": "Haskell称 Martino Longhi the Elder 接替 Matteo da Castello 担任建筑师。",
                "original_quotes": [
                    {
                        "source_span": "S2 line 46; print p.69",
                        "text": "Martino Longhi the Elder replaced Matteo da Castello as architect",
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE3,
                    "source_span": "line 46; print p.69",
                },
            },
            {
                "citation": BOOK,
                "location": "第20章 p.400；S2 L52–53",
                "sentence_summary": "Haskell再次以 Martino Longhi the Elder 指称 Chiesa Nuova 的第二任建筑师。",
                "original_quotes": [
                    {
                        "source_span": "S2 lines 52–53; print p.400",
                        "text": "Martino Longhi the Elder as (the second) architect of the church",
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE20,
                    "source_span": "lines 52–53; print p.400",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** Haskell 第3章称 Martino Longhi the Elder 接替 Matteo da Castello 担任建筑师；第20章在回顾 Chiesa Nuova 的建筑任命时再次以相同全名指称该建筑师。中文名为本项目工作音译，身份依据限于本书两处记载。

**English:** Haskell names Martino Longhi the Elder as the architect who replaced Matteo da Castello in Chapter 3, then uses the same full name for the church's second architect in the Chapter 20 account of Chiesa Nuova. The Chinese name is a working transliteration; the identification is limited to these two passages.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文姓名 | Martino Longhi the Elder | S1（第3章 p.69；第20章 p.400） |

### 身份

| 字段 | 值 | 证据 |
|---|---|---|
| 本书职业身份 | 建筑师；第20章称为教堂的第二任建筑师 | S1（第3章 p.69；第20章 p.400） |

### 身份边界

现有 Martino Longhi the Younger 人物 KU 保持独立。原书对两者分别使用 the Elder 和 the Younger；本卡不据同姓推断亲缘关系。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。两条直接 S2 关系候选（{', '.join(sorted(STATEMENTS))}）留待 S6；第20章的任命解释仍保留 Haskell 转述的“probably”限定。本卡登记不等于关系裁决。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter S3 person group for Martino Longhi the Elder.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE)
    matches = [row for row in alignments if row.get("candidate_id") == CANDIDATE and not row.get("external_source")]
    assert len(matches) == 1
    alignment = matches[0]
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert group_members == [CANDIDATE]
    assert not any(row.get("ku_id") == KU for row in manifest)
    assert not (ROOT / CARD).exists()
    younger = [row for row in manifest if row.get("ku_id") == "units/persons/martino-longhi-younger"]
    assert len(younger) == 1

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == STATEMENTS

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert f"- {CARD}" not in accepted_lines
    planned_alignments = [dict(row) for row in alignments]
    planned_alignment = next(row for row in planned_alignments if row.get("alignment_id") == alignment["alignment_id"])
    planned_alignment["ku_id"] = KU
    planned_alignment["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned_alignment["resolution_note"] += (
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；第3章 p.69 与第20章 p.400 的全名和建筑师语境对应。"
        "与现有 Martino Longhi the Younger KU 分立；不推断亲缘。两条直接关系候选留待 S6。"
    )
    planned_manifest = [*manifest, {
        "ku_id": KU,
        "type": "person",
        "canonical_name": "马蒂诺·隆吉（长者）",
        "name_en": "Martino Longhi the Elder",
        "source_task": TASK,
        "card_path": CARD,
    }]
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = insert_accepted(accepted_lines, CARD)
    card = make_card()
    header = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert header and isinstance(yaml.safe_load(header.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 689
    assert totals["registered_members"] == 850
    assert totals["pending_groups"] == 4096
    assert totals["pending_members"] == 4118
    assert len(planned_manifest) == len(manifest) + 1

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Martino Longhi the Elder 跨章身份组登记（{DATE}）\n\n"
        f"cand-1427（L.csv#84，索引列 pp.69、400）保持单成员 new 组 {GROUP}，登记为"
        f"[马蒂诺·隆吉（长者）（Martino Longhi the Elder）](../../../{CARD})（{KU}）。"
        "第3章 p.69 与第20章 p.400 在不同章节重复全名并均置于 Chiesa Nuova 建筑师语境；"
        "与 Martino Longhi the Younger KU 分开，不推断亲缘，也未访问外部身份来源。\n"
        f"- 两条直接 S2 关系候选 {', '.join(sorted(STATEMENTS))} 留待 S6；第20章的任命解释保留 probably 限定。\n"
        f"- S4 登记后：{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记，"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记。"
    )

    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, matches = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert matches == 1
    result_text += (
        f"\n\n### S3/S4 person：Martino Longhi the Elder 跨章身份组登记（{DATE}）\n\n"
        f"{CANDIDATE} → [马蒂诺·隆吉（长者）（Martino Longhi the Elder）](../units/persons/martino-longhi-elder.md)；"
        "第3章与第20章同名身份组登记，与 Martino Longhi the Younger 分立；两条关系候选留待 S6。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE}->{KU}; relation_candidates={len(direct)}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    (ROOT / CARD).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE}->{KU}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
