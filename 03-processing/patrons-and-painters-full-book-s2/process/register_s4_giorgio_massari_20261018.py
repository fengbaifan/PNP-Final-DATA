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
DATE = "2026-10-18"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CANDIDATE = "cand-1562"
GROUP = "new-person:giorgio-massari-068f7c6d56"
KU = "units/persons/giorgio-massari"
CARD = "04-knowledge/units/persons/giorgio-massari.md"
ANCHOR = "s4-person-giorgio-massari-20261018"
DIRECT_STATEMENTS = {
    "st-chp9-p272-massari-architect",
    "st-chp9-p272-massari-palladian-lines",
}
RELATED_STATEMENTS = {
    *DIRECT_STATEMENTS,
    "st-chp9-p270-gesuati-new-church-public-funding",
    "st-chp10-p321-pieta-governor-invited-lodoli-to-view-massari-model",
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
        "title": "乔尔乔·马萨里（Giorgio Massari）",
        "name_en": "Giorgio Massari",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "全书索引 M.csv#103；所列页码270、272、321",
                "sentence_summary": "Haskell索引将第9章与第10章的 Giorgio Massari 提及列在同一人物主项下。",
                "original_quotes": [{"source_span": "M.csv#103", "text": "Massari, Giorgio"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/03-Index/03-2-Index-CSV/M.csv", "source_span": "M.csv#103"},
            },
            {
                "citation": BOOK,
                "location": "第9章 p.270；S2 lines 27–36",
                "sentence_summary": "Haskell称Gesuati正聘请 Giorgio Massari 在 Zattere 建造一座新教堂。",
                "original_quotes": [{"source_span": "S2 lines 27–36; print p.270", "text": "the Gesuati, were beginning to employ Giorgio Massari to build a complete new church on the Zattere"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md", "source_span": "lines 27–36; print p.270"},
            },
            {
                "citation": BOOK,
                "location": "第9章 p.272；S2 lines 53–60",
                "sentence_summary": "在 Pietà 教堂叙述中，Haskell明确称 Massari 为建筑师。",
                "original_quotes": [{"source_span": "S2 lines 53–60; print p.272", "text": "Massari was the architect"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md", "source_span": "lines 53–60; print p.272"},
            },
            {
                "citation": BOOK,
                "location": "第10章 p.321；S2 lines 165–173",
                "sentence_summary": "Haskell在 Lodoli 受邀查看 Massari 为拟建教堂所作模型的叙述中，记录建筑师对方案选择压力的回应。",
                "original_quotes": [{"source_span": "S2 lines 165–173; print p.321", "text": "He was once invited by the governor of the Ospedale della Pietà to look at Massari’s tnodello for the proposed church."}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "source_span": "lines 165–173; print p.321"},
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** Haskell第9章称 G. Massari 为建筑师，并叙述 Gesuati 聘请他在 Zattere 建造新教堂；索引同时列出第9章 p.270、p.272 与第10章 p.321。第10章还记述 Lodoli 曾受邀查看 Massari 为拟建教堂所作的模型。中文名为本项目工作音译，身份说明限于书内材料。

**English:** In Chapter 9, Haskell identifies Giorgio Massari as an architect and reports that the Gesuati were employing him to build a new church on the Zattere; the index also lists Chapter 9, pp. 270 and 272, and Chapter 10, p. 321 under the same entry. Chapter 10 further recounts Lodoli being invited to inspect a model by Massari for a proposed church. The Chinese name is a working transliteration, and the identification is limited to the book.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文全名 | Giorgio Massari | S1（第9章 p.270；索引 M.csv#103） |

### 身份

| 字段 | 值 | 证据 |
|---|---|---|
| 本书称谓 | Architect（建筑师；Pietà 教堂叙述） | S1（第9章 p.272） |
| 受聘项目 | Gesuati 在 Zattere 的新教堂 | S1（第9章 p.270） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接关系候选 {', '.join(sorted(DIRECT_STATEMENTS))} 留待 S6；第9章 p.270 与第10章 p.321 的相关陈述也保留在过程记录供 S6 核对。本卡不据此预先建立委托、建造或作品关系。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter S3 person group for Giorgio Massari.")
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
    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()
    ]
    direct = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct == DIRECT_STATEMENTS
    related = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and CANDIDATE in (row.get("qualifiers") or {}).get("mentioned_candidate_ids", [])
    }
    assert RELATED_STATEMENTS.issubset(related)

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert f"- {CARD}" not in accepted_lines
    planned_alignments = [dict(row) for row in alignments]
    planned_alignment = next(row for row in planned_alignments if row.get("alignment_id") == alignment["alignment_id"])
    planned_alignment["ku_id"] = KU
    planned_alignment["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned_alignment["resolution_note"] += (
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；M.csv#103 将第9章 p.270、p.272 与第10章 p.321列为同一人物主项。"
        "登记仅采用书内姓名与称谓，不作外部身份或生平推断；关系候选留待 S6。"
    )
    planned_manifest = [*manifest, {
        "ku_id": KU,
        "type": "person",
        "canonical_name": "乔尔乔·马萨里",
        "name_en": "Giorgio Massari",
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
    assert totals["registered_groups"] == 695
    assert totals["registered_members"] == 856
    assert totals["pending_groups"] == 4090
    assert totals["pending_members"] == 4112
    assert len(planned_manifest) == len(manifest) + 1

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Giorgio Massari 跨章身份组登记（{DATE}）\n\n"
        f"cand-1562（M.csv#103，索引页码270、272、321）保持单成员 new 组 {GROUP}，登记为"
        f"[乔尔乔·马萨里（Giorgio Massari）](../../../{CARD})（{KU}）。第9章 p.270以全名记述 Gesuati 聘请其建造新教堂，"
        "p.272称其为 Pietà 教堂建筑师；第10章 p.321续见 Massari 模型及建筑师的回应。索引将这些页码列于同一人物条目。\n"
        f"- 直接关系候选 {', '.join(sorted(DIRECT_STATEMENTS))} 留待 S6；相关陈述 {', '.join(sorted(RELATED_STATEMENTS - DIRECT_STATEMENTS))} 保留供 S6 核对，未新增 formal relations。\n"
        f"- S4 登记后：{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记，"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记。"
    )

    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, result_matches = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert result_matches == 1
    result_text += (
        f"\n\n### S3/S4 person：Giorgio Massari 跨章身份组登记（{DATE}）\n\n"
        f"{CANDIDATE} → [乔尔乔·马萨里（Giorgio Massari）](../units/persons/giorgio-massari.md)；"
        "M.csv#103将第9章 p.270、p.272与第10章 p.321列为同一人物主项；关系候选留待 S6。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE}->{KU}; direct_relation_candidates={len(direct)}; "
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
