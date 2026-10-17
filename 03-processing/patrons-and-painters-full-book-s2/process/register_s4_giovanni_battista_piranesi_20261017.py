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
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/P.csv"
CANDIDATE = "cand-1938"
GROUP = "new-person:battista-giovanni-piranesi-8cb8ba565d"
KU = "units/persons/giovanni-battista-piranesi"
CARD = "04-knowledge/units/persons/giovanni-battista-piranesi.md"
ANCHOR = "s4-person-giovanni-battista-piranesi-20261017"
STATEMENTS = {"st-chp15-p370-piranesi-prints-created-by-piranesi"}


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
        "title": "乔瓦尼·巴蒂斯塔·皮拉内西（Giovanni Battista Piranesi）",
        "name_en": "Giovanni Battista Piranesi",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK,
                "location": "全书索引 P.csv#139；所列页码309、358、370",
                "sentence_summary": "Haskell索引将 Giovanni Battista Piranesi 列为人物主项，并对应第10、14、15章的三个页码。",
                "original_quotes": [{"source_span": "P.csv#139", "text": "Piranesi, Giovanni Battista"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": INDEX_FILE, "source_span": "P.csv#139"},
            },
            {
                "citation": BOOK,
                "location": "第10章 p.309；S2 L468–479",
                "sentence_summary": "Haskell在讨论建筑理论对巴洛克建筑及后继者的批评时提及 Piranesi。",
                "original_quotes": [{"source_span": "S2 L468–479; print p.309", "text": "down to Piranesi"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "source_span": "lines 468–479; print p.309"},
            },
            {
                "citation": BOOK,
                "location": "第14章 p.358；S2 L118–124",
                "sentence_summary": "Haskell称 Algarotti 欣赏 Piranesi 在罗马的平行创作。",
                "original_quotes": [{"source_span": "S2 L118–124; print p.358", "text": "parallel creations of Piranesi in Rome"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md", "source_span": "lines 118–124; print p.358"},
            },
            {
                "citation": BOOK,
                "location": "第15章 p.370；S2 L61–67",
                "sentence_summary": "Haskell写到 Alticchiero 浴室墙面陈列 prints by Piranesi；没有识别具体单件版画。",
                "original_quotes": [{"source_span": "S2 line 62; print p.370", "text": "prints by Piranesi"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md", "source_span": "line 62; print p.370"},
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** Haskell索引以全名 Giovanni Battista Piranesi 列出第309、358、370页；正文相应章节以姓氏 Piranesi 指称同一人物。第15章 p.370 称 Alticchiero 浴室陈列“prints by Piranesi”，但未识别具体版画。本卡限于该跨章人物身份，不将集合描述拆成单件作品或正式关系。

**English:** Haskell's index lists Giovanni Battista Piranesi at pp. 309, 358, and 370; the corresponding chapters use the surname Piranesi for the person. Chapter 15, p. 370, says that the bathroom at Alticchiero displayed “prints by Piranesi,” without identifying individual prints. This card records the cross-chapter person identity only and does not split the collective description into individual works or a formal relation.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文全名 | Giovanni Battista Piranesi | S1（Haskell索引 P.csv#139） |

### 身份边界

第15章 p.366 的 Francesco Piranesi 是另一名人物，对应索引 P.csv#138；不得与本卡合并。索引将 p.370 的浴室版画指称列在 Giovanni Battista Piranesi 主项下。中文名为本项目工作音译。

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 候选 {', '.join(sorted(STATEMENTS))} 留待 S6；对应候选 cand-10545 仍为 undecided，因为原文是未具名的版画集合，不登记为单件作品。逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter S3 person group for Giovanni Battista Piranesi.")
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
    assert any(row.get("ku_id") == "units/persons/martino-longhi-elder" for row in manifest)
    assert any(row.get("ku_id") == "units/persons/martino-longhi-younger" for row in manifest)

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
    piranesi_prints = next(row for row in candidates if row["candidate_id"] == "cand-10545")
    piranesi_prints_alignment = next(row for row in alignments if row.get("candidate_id") == "cand-10545" and not row.get("external_source"))
    assert piranesi_prints["suggested_type"] == "work"
    assert piranesi_prints_alignment["decision"] == "undecided" and not piranesi_prints_alignment.get("ku_id")
    francesco = next(row for row in candidates if row["candidate_id"] == "cand-1937")
    francesco_alignment = next(row for row in alignments if row.get("candidate_id") == "cand-1937" and not row.get("external_source"))
    assert francesco["canonical_name"] == "Piranesi, Francesco"
    assert sync.get_group(francesco_alignment.get("resolution_note", "")) == "new-person:francesco-piranesi-42d51ce564"

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    assert f"- {CARD}" not in accepted_lines
    planned_alignments = [dict(row) for row in alignments]
    planned_alignment = next(row for row in planned_alignments if row.get("alignment_id") == alignment["alignment_id"])
    planned_alignment["ku_id"] = KU
    planned_alignment["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned_alignment["resolution_note"] += (
        f" S4登记（{DATE}）：{GROUP} 映射至 {KU}；依 P.csv#139 对应第10、14、15章的三处 Piranesi 提及。"
        "与 cand-1937 Francesco Piranesi 保持分组；浴室版画集合 cand-10545 仍 undecided。"
        "直接关系候选留待 S6。"
    )
    planned_manifest = [*manifest, {
        "ku_id": KU,
        "type": "person",
        "canonical_name": "乔瓦尼·巴蒂斯塔·皮拉内西",
        "name_en": "Giovanni Battista Piranesi",
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
    assert totals["registered_groups"] == 690
    assert totals["registered_members"] == 851
    assert totals["pending_groups"] == 4095
    assert totals["pending_members"] == 4117
    assert len(planned_manifest) == len(manifest) + 1

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：Giovanni Battista Piranesi 跨章身份组登记（{DATE}）\n\n"
        f"cand-1938（P.csv#139，索引页码309、358、370）保持单成员 new 组 {GROUP}，登记为"
        f"[乔瓦尼·巴蒂斯塔·皮拉内西（Giovanni Battista Piranesi）](../../../{CARD})（{KU}）。"
        "第10章 p.309、第14章 p.358 与第15章 p.370 的姓氏提及由书内索引归入同一全名主项。\n"
        "- 区分：cand-1937 Francesco Piranesi（P.csv#138，p.366）保持独立人物组；cand-10495 是其1786年版画作品组；cand-10545 浴室版画集合仍 undecided，不拆成单件。\n"
        f"- 直接 S2 候选 {', '.join(sorted(STATEMENTS))} 留待 S6；未新增 formal relations。\n"
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
        f"\n\n### S3/S4 person：Giovanni Battista Piranesi 跨章身份组登记（{DATE}）\n\n"
        f"{CANDIDATE} → [乔瓦尼·巴蒂斯塔·皮拉内西（Giovanni Battista Piranesi）](../units/persons/giovanni-battista-piranesi.md)；"
        "与 Francesco Piranesi 分组；浴室版画候选仍 undecided，关系候选留待 S6。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE}->{KU}; relation_candidates={len(direct)}; "
            f"Francesco={francesco_alignment['decision']}; prints={piranesi_prints_alignment['decision']}; "
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
