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
CANDIDATE = "cand-0268"
GROUP = "new-person:bella-della-stefano-4ee4ce0873"
KU = "units/persons/stefano-della-bella"
CARD = "04-knowledge/units/persons/stefano-della-bella.md"
ANCHOR = "s4-person-stefano-della-bella-20261018"
STATEMENTS = {
    "st-chp7-p176-i21",
    "st-chp7-p176-i22",
    "st-chp7-p183-i17",
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
        "title": "斯特凡诺·德拉·贝拉（Stefano della Bella）",
        "name_en": "Stefano della Bella",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "全书索引 B.csv#115；所列页码176、183",
                "sentence_summary": "Haskell索引将第176、183页中 Stefano della Bella 的人物提及列入同一全名主项。",
                "original_quotes": [{"source_span": "B.csv#115", "text": "Bella, Stefano della"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/03-Index/03-2-Index-CSV/B.csv", "source_span": "B.csv#115"},
            },
            {
                "citation": BOOK,
                "location": "第7章 p.176；S2 L84",
                "sentence_summary": "Haskell将 Stefano della Bella 称为蚀刻师和素描家；扫描页读法支持 OCR 中的姓名校正。",
                "original_quotes": [{"source_span": "S2 line 84; print p.176", "text": "etcher and draughtsman Stefano della Bella"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "source_span": "line 84; print p.176"},
            },
            {
                "citation": BOOK,
                "location": "第7章 p.183；S2 L166",
                "sentence_summary": "Haskell在第183页以同一全名叙述 Stefano della Bella 返回意大利。",
                "original_quotes": [{"source_span": "S2 line 166; print p.183", "text": "Stefano della Bella rushed back to Italy"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "source_span": "line 166; print p.183"},
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** Haskell第7章 p.176 称 Stefano della Bella 为蚀刻师和素描家；第183页再次使用同一全名。索引 B.csv#115 将两页列在 Stefano della Bella 主项下。中文名为本项目工作音译，人物身份限于书内证据。

**English:** Haskell calls Stefano della Bella an etcher and draughtsman on p. 176 of Chapter 7 and uses the same full name again on p. 183. The index lists both pages under the Stefano della Bella entry. The Chinese name is a working transliteration, and the identity is limited to evidence in the book.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文全名 | Stefano della Bella | S1（第7章 pp.176、183；索引 B.csv#115） |

### 身份

| 字段 | 值 | 证据 |
|---|---|---|
| 本书职业身份 | Etcher and draughtsman（蚀刻师与素描家） | S1（第7章 p.176） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。三条直接 S2 候选（{', '.join(sorted(STATEMENTS))}）留待 S6；其中未具名的 Florentine ambassador 与未具名的威胁者不在本卡补造身份。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S3 person group for Stefano della Bella.")
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
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；B.csv#115 将第7章 p.176 与 p.183 两处全名列入同一人物主项。"
        "S0 OCR姓名差异以既有扫描核读记录为准，源文件不改写。三条关系候选留待 S6。"
    )
    planned_manifest = [*manifest, {
        "ku_id": KU,
        "type": "person",
        "canonical_name": "斯特凡诺·德拉·贝拉",
        "name_en": "Stefano della Bella",
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
    assert totals["registered_groups"] == 693
    assert totals["registered_members"] == 854
    assert totals["pending_groups"] == 4092
    assert totals["pending_members"] == 4114
    assert len(planned_manifest) == len(manifest) + 1

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Stefano della Bella 身份组登记（{DATE}）\n\n"
        f"cand-0268（B.csv#115，索引页码176、183）保持单成员 new 组 {GROUP}，登记为"
        f"[斯特凡诺·德拉·贝拉（Stefano della Bella）](../../../{CARD})（{KU}）。第7章两页以同一全名和艺术家身份相互支持。\n"
        "- 保留既有 S0 OCR 对照：p.176 扫描读作 della Bella，OCR 转录差异不写回来源文件。\n"
        f"- 三条直接 S2 关系候选 {', '.join(sorted(STATEMENTS))} 留待 S6；未新增 formal relations。\n"
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
        f"\n\n### S3/S4 person：Stefano della Bella 身份组登记（{DATE}）\n\n"
        f"{CANDIDATE} → [斯特凡诺·德拉·贝拉（Stefano della Bella）](../units/persons/stefano-della-bella.md)；"
        "第7章两处身份锚点对应索引同一主项；关系候选留待 S6。"
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
