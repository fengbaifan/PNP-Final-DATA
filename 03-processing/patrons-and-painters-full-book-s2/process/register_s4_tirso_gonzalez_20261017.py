from __future__ import annotations

import argparse
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
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
CANDIDATE = "cand-1213"
GROUP = "new-person:gonzalez-tirso-dbb6b94ada"
KU = "units/persons/tirso-gonzalez"
CARD = "04-knowledge/units/persons/tirso-gonzalez.md"
ANCHOR = "s4-person-tirso-gonzalez-20261017"
STATEMENTS = {
    "st-chp3-seciv-l152-163-gonzalez-resumed-undertaking",
    "st-chp3-seciv-l165-177-tirso-final-decision-may-1695",
    "st-chp3-seciv-l165-177-tirso-forbade-further-criticism",
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
        "title": "蒂尔索·冈萨雷斯（Tirso Gonzalez）",
        "name_en": "Tirso Gonzalez",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "第3章 p.91；S2 L162–163",
                "sentence_summary": "Haskell称 undertaking 在 Tirso Gonzalez 于1687年接任后重新恢复；原文将他称为 Spaniard。",
                "original_quotes": [
                    {
                        "source_span": "S2 lines 162–163; print p.91",
                        "text": "under the Spaniard, Tirso Gonzalez, who took over in 1687, the undertaking was again resumed in the transept chapel",
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "lines 162–163; print p.91",
                },
            },
            {
                "citation": BOOK,
                "location": "第3章 p.92；S2 L171",
                "sentence_summary": "同一段以 General, Tirso Gonzalez 指称其为总会长；该名称与 p.91 的全名和接任语境一致。",
                "original_quotes": [
                    {
                        "source_span": "S2 line 171; print p.92",
                        "text": "the General, Tirso Gonzalez",
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "line 171; print p.92",
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

**中文：** Haskell 第3章在叙述耶稣会圣依纳爵祭坛项目时，以 Tirso Gonzalez 指称于1687年接任的耶稣会总会长；第92页再次称他为 General。此处中文名为工作音译，人物身份与职位仅据本书记载。

**English:** In Haskell's account of the Jesuit altar project for St Ignatius, Tirso Gonzalez is named as the Jesuit General who took over in 1687; p.92 again identifies him as the General. The Chinese name is a working transliteration, and the identification and office are limited to the book's account.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文姓名 | Tirso Gonzalez | S1（第3章 pp.91–92）；索引 G.csv#121 |

### 身份

| 字段 | 值 | 证据 |
|---|---|---|
| 本书称谓 | General of the Society（耶稣会总会长；依本段语境） | S1（第3章 p.92） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。三条直接 S2 关系候选（{', '.join(sorted(STATEMENTS))}）留待 S6；本卡登记不等于关系裁决。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-local S3 person group for Tirso Gonzalez.")
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
        __import__("json").loads(line)
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
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；仅据第3章 pp.91–92 的同名与总会长语境登记，"
        "未添加外部生平或身份标识。三条直接关系候选留待 S6。"
    )
    planned_manifest = [*manifest, {
        "ku_id": KU,
        "type": "person",
        "canonical_name": "蒂尔索·冈萨雷斯",
        "name_en": "Tirso Gonzalez",
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
    assert totals["registered_groups"] == 688
    assert totals["registered_members"] == 849
    assert totals["pending_groups"] == 4097
    assert totals["pending_members"] == 4119
    assert len(planned_manifest) == len(manifest) + 1

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Tirso Gonzalez 身份组登记（{DATE}）\n\n"
        f"cand-1213（G.csv#121；索引列 pp.91–92）保持单成员 new 组 {GROUP}，登记为"
        f"[蒂尔索·冈萨雷斯（Tirso Gonzalez）](../../../{CARD})（{KU}）。第3章 p.91 与 p.92 的全名和总会长语境相合；"
        "仅按 Haskell 的称谓记录，未补外部身份或生平。\n"
        f"- 三条直接 S2 关系候选 {', '.join(sorted(STATEMENTS))} 留待 S6；未新增 formal relations。\n"
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
        f"\n\n### S3/S4 person：Tirso Gonzalez 身份组登记（{DATE}）\n\n"
        f"{CANDIDATE} → [蒂尔索·冈萨雷斯（Tirso Gonzalez）](../units/persons/tirso-gonzalez.md)；"
        "保留原书人名与总会长语境，三条关系候选留待 S6。"
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
