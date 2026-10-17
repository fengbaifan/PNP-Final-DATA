from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-work-mazarin-facade-ss-vincenzo-20261017"
CANDIDATE = "cand-6797"
GROUP = "workgrp-568625e1ef6077"
KU_ID = "units/works/facade-ss-vincenzo-ed-anastasio-piazza-di-trevi"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "特雷维广场圣文森佐与圣阿纳斯塔西奥教堂立面"
NAME_EN = "Façade of SS. Vincenzo ed Anastasio in Piazza di Trevi"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE_SPAN = "lines 163–165; print p. 183"
RELATION_STATEMENTS = {
    "st-chp7-p183-i08",
    "st-chp7-p183-i09",
    "st-chp7-p183-i10",
    "st-chp7-p183-i12",
    "st-chp7-p183-n3-facade-inscription",
}


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 7, p. 183.",
                "location": "第7章，印刷页183；OCR L163–165。",
                "sentence_summary": (
                    "哈斯克尔称 Mazarin 经 Paolo Maccarani 委托建筑师 Martino Longhi the Younger "
                    "为 SS. Vincenzo ed Anastasio 教堂增建立面；作者还叙述工程延宕、Mazarin 的经济困难，"
                    "并将立面的视觉效果解释为彰显其权威。"
                ),
                "original_quotes": [
                    {
                        "source_span": "line 163; print p. 183",
                        "text": "through Paolo Maccarani, an agent in Rome",
                    },
                    {
                        "source_span": "line 163; print p. 183",
                        "text": "the architect Martino Longhi the Younger",
                    },
                    {
                        "source_span": "lines 163–164; print p. 183",
                        "text": "to add a façade to the church of SS. Vincenzo ed Anastasio",
                    },
                    {
                        "source_span": "lines 164–165; print p. 183",
                        "text": "served to proclaim the splendour and arrogance of the Cardinal’s authority",
                    },
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": SOURCE_SPAN,
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "[第7章 p.183](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L163–165）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔在第7章所述、增建于 SS. Vincenzo ed Anastasio 教堂的立面。原书称 Mazarin 经 Paolo Maccarani 委托建筑师 Martino Longhi the Younger 增建立面；本卡保留作者所述委托关系，不据此补写实际施工分工或其他身份信息。哈斯克尔还称工程延宕、Mazarin 受到经济困难困扰，并把立面解释为彰显枢机权威的视觉表达。后一判断是作者的解释。{source_link}

**English:** This unit records the façade described in Chapter 7 as an addition to the church of SS. Vincenzo ed Anastasio. Haskell says Mazarin commissioned the architect Martino Longhi the Younger through Paolo Maccarani to add it; this card preserves the reported commission without inferring the division of actual construction work or adding biographical claims. Haskell also says that the work dragged on as Mazarin faced economic difficulties, and interprets the façade as proclaiming the Cardinal’s authority. The last point is the author’s interpretation. {source_link}

### 对象边界

立面作为 work 登记，与建筑地点[圣文森佐与圣阿纳斯塔西奥教堂](../places/church-ss-vincenzo-ed-anastasio.md)及地点[特雷维广场](../places/piazza-di-trevi.md)分开。卡内链接仅用于对象导航，不表达正式关系。原书脚注提及的档案与铭文材料未在本次独立核阅；相关断言仍按 S2 来源层级保留，待 S6 审查。

## 关系与证据

当前没有已登记的正式关系。`st-chp7-p183-i08`、`i09`、`i10`、`i12` 与 `st-chp7-p183-n3-facade-inscription` 的委托、人物角色、地点及铭文陈述留待 S6 逐条核对端点、方向、语境和证据；本次不写入 `relations.csv`，也不新增 S5 enrichment。
"""


def insert_accepted_path(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register the Mazarin façade work in S4 after cross-chapter endpoint registration."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert candidate_map[CANDIDATE].get("suggested_type") == "work"
    target = decisions[CANDIDATE]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "work"
        and "facade" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".casefold()
        and "vincenzo" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".casefold()
        and "trevi" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".casefold()
        for row in manifest
    ), "same façade work appears to exist already; inspect before proceeding"

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    source_quotes = (
        "through Paolo Maccarani, an agent in Rome",
        "the architect Martino Longhi the Younger",
        "to add a façade to the church of SS. Vincenzo ed Anastasio",
        "served to proclaim the splendour and arrogance of the Cardinal’s authority",
    )
    assert all(" ".join(quote.split()) in source_text for quote in source_quotes)

    endpoint_targets = {
        "cand-1588": "units/persons/mazarin",
        "cand-1463": "units/persons/paolo-maccarani",
        "cand-1428": "units/persons/martino-longhi-younger",
        "cand-0723": "units/places/church-ss-vincenzo-ed-anastasio",
        "cand-6806": "units/places/piazza-di-trevi",
    }
    assert all(decisions[cid].get("ku_id") == target_ku for cid, target_ku in endpoint_targets.items())

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = {
        row["statement_id"]: row for row in statements.values()
        if row.get("subject_candidate_id") == CANDIDATE
        or row.get("object_candidate_id") == CANDIDATE
    }
    assert RELATION_STATEMENTS.issubset(direct)
    assert all(direct[sid].get("qualifiers", {}).get("relation_candidate") is True for sid in RELATION_STATEMENTS)

    planned_alignment = [dict(row) for row in alignments]
    mapped = [
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(mapped) == 1
    mapped[0]["ku_id"] = KU_ID
    mapped[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    mapped[0]["resolution_note"] += f" S4 registration: source-backed façade work group {GROUP} maps to {KU_ID}; formal person, place, commission, and inscription relations remain for S6."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_text += f"""

<a id="{ANCHOR}"></a>

### S4 work：Mazarin 委托的 SS. Vincenzo ed Anastasio 教堂立面（{DATE}）

单成员 S3 作品组 `{GROUP}`（`{CANDIDATE}`）映射至[特雷维广场圣文森佐与圣阿纳斯塔西奥教堂立面作品卡](../../../04-knowledge/units/works/facade-ss-vincenzo-ed-anastasio-piazza-di-trevi.md)。第7章 p.183 称 Mazarin 经 Paolo Maccarani 委托建筑师 Martino Longhi the Younger 增建立面；哈斯克尔另述工程延宕及经济困难，并将立面解释为彰显枢机权威。后者保留为作者解释。卡片将立面 work 与教堂建筑及 Piazza di Trevi place 分开；跨章端点在本次登记前均已有 KU 去向。

本段关联的 {len(RELATION_STATEMENTS)} 条 S2 关系候选 `{', '.join(sorted(RELATION_STATEMENTS))}` 留待 S6 逐条核验。脚注所引档案与铭文未在本轮独立核阅，不据此新增证据或关系；`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_text = result_text.rstrip() + (
        f"\n\n### S4 work：Mazarin 委托的教堂立面（{DATE}）\n\n"
        f"`{CANDIDATE}` 映射至[立面作品卡](../units/works/facade-ss-vincenzo-ed-anastasio-piazza-di-trevi.md)。"
        "卡片按书内叙述记录委托、建筑师角色、工程延宕与作者对立面权威表达的解释；与教堂和广场地点分开。"
        f"{len(RELATION_STATEMENTS)} 条关联 S2 关系候选留待 S6，脚注所引档案与铭文未独立核阅；本轮未新增正式关系或 S5 补足。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} is the complete single-member S3 work group {GROUP}")
        print(f"verified {len(source_quotes)} source quotations and {len(endpoint_targets)} mapped cross-chapter endpoints")
        print(f"S6 relation candidates preserved: {len(RELATION_STATEMENTS)}; relations.csv and enrichment.jsonl unchanged")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; accepted path unique")
        print("planned writes: one bilingual work card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
