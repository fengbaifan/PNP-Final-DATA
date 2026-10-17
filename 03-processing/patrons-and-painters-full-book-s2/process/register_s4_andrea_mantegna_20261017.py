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
CANDIDATE = "cand-1522"
GROUP = "new-person:andrea-mantegna-b0a921de46"
KU = "units/persons/andrea-mantegna"
CARD = "04-knowledge/units/persons/andrea-mantegna.md"
ANCHOR = "s4-person-andrea-mantegna-20261017"
STATEMENTS = {"st-chp17-p380-manfrin-collection-represented-mantegna"}


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
        "title": "安德烈亚·曼特尼亚（Andrea Mantegna）",
        "name_en": "Andrea Mantegna",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "全书索引 M.csv#59；所列页码175、380",
                "sentence_summary": "Haskell索引将 Mantegna 的两处正文页码对应到人物主项 Andrea Mantegna。",
                "original_quotes": [{"source_span": "M.csv#59", "text": "Mantegna, Andrea"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/03-Index/03-2-Index-CSV/M.csv", "source_span": "M.csv#59"},
            },
            {
                "citation": BOOK,
                "location": "第7章 p.175；S2 L61–74",
                "sentence_summary": "Haskell将 Mantegna 列入为 Richelieu 收藏绘画的艺术家。",
                "original_quotes": [{"source_span": "S2 L61–74; print p.175", "text": "Mantegna, Costa and Correggio"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "source_span": "lines 61–74; print p.175"},
            },
            {
                "citation": BOOK,
                "location": "第17章 p.380；S2 L8–20",
                "sentence_summary": "Haskell在 Manfrin 收藏叙述中再次提到 Mantegna。",
                "original_quotes": [{"source_span": "S2 L8–20; print p.380", "text": "The Venetian pictures began with Mantegna and Bellini"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/17_CHP-17_sec_i.md", "source_span": "lines 8–20; print p.380"},
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** Haskell索引以 Andrea Mantegna 主项列出第175与380页；第7章提到 Mantegna 与 Costa、Correggio 等艺术家，第17章在威尼斯绘画收藏叙述中再次提及 Mantegna。中文名为本项目工作音译，身份依据限于书内索引及这两处正文。

**English:** Haskell's index lists pp. 175 and 380 under Andrea Mantegna. Chapter 7 mentions Mantegna among artists alongside Costa and Correggio, and Chapter 17 names him again in its account of the Venetian pictures in a collection. The Chinese name is a working transliteration; the identification is limited to the index and these two passages.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文全名 | Andrea Mantegna | S1（Haskell索引 M.csv#59） |

### 身份边界

Manfrin collection 候选 cand-1513 仍为 S3 undecided（索引将其列作 Girolamo Manfrin 的 collection 子目，类型尚未裁决）；此人物卡不据此建立作品清单或馆藏 KU。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 候选 {', '.join(sorted(STATEMENTS))} 留待 S6；原文提及收藏中的作品涉及 Mantegna，但未识别单件作品。本卡登记不替代对 collection 端点和关系范围的裁决。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter S3 person group for Andrea Mantegna.")
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

    collection_candidate = next(row for row in candidates if row["candidate_id"] == "cand-1513")
    collection_alignment = next(row for row in alignments if row.get("candidate_id") == "cand-1513" and not row.get("external_source"))
    assert collection_candidate.get("suggested_type") == ""
    assert collection_alignment["decision"] == "undecided" and not collection_alignment.get("ku_id")
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
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；M.csv#59 将第7章 p.175 与第17章 p.380 两处 Mantegna 提及列于 Andrea Mantegna 主项。"
        "Manfrin collection cand-1513 保持 undecided/untyped，不预设作品端点。直接关系候选留待 S6。"
    )
    planned_manifest = [*manifest, {
        "ku_id": KU,
        "type": "person",
        "canonical_name": "安德烈亚·曼特尼亚",
        "name_en": "Andrea Mantegna",
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
    assert totals["registered_groups"] == 691
    assert totals["registered_members"] == 852
    assert totals["pending_groups"] == 4094
    assert totals["pending_members"] == 4116
    assert len(planned_manifest) == len(manifest) + 1

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Andrea Mantegna 跨章身份组登记（{DATE}）\n\n"
        f"cand-1522（M.csv#59，索引页码175、380）保持单成员 new 组 {GROUP}，登记为"
        f"[安德烈亚·曼特尼亚（Andrea Mantegna）](../../../{CARD})（{KU}）。"
        "第7章 p.175 与第17章 p.380 的姓氏提及由索引对应同一全名主项；未添加外部身份或作品清单。\n"
        "- Manfrin collection 候选 cand-1513 仍 undecided/untyped；不建立作品或收藏 KU。\n"
        f"- 直接 S2 关系候选 {', '.join(sorted(STATEMENTS))} 留待 S6；未新增 formal relations。\n"
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
        f"\n\n### S3/S4 person：Andrea Mantegna 跨章身份组登记（{DATE}）\n\n"
        f"{CANDIDATE} → [安德烈亚·曼特尼亚（Andrea Mantegna）](../units/persons/andrea-mantegna.md)；"
        "第7章与第17章提及归于书内索引的同一主项；Manfrin collection 候选保持 undecided/untyped，关系候选留待 S6。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE}->{KU}; relation_candidates={len(direct)}; "
            f"collection={collection_alignment['decision']}/untyped; manifest={len(manifest)}->{len(planned_manifest)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}"
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
