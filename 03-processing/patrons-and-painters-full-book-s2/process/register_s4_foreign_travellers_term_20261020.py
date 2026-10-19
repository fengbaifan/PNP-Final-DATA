from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
sys.path.insert(0, str(PROCESS_DIR))

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync
import register_s4_work_second_scuola_scheme_20261020 as s4_helpers

PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
AGENTS_PATH = ROOT / "AGENTS.md"

CANDIDATE = "cand-3562"
GROUP = "sg3-term-cand-3562"
KU_ID = "units/terms/foreign-travellers"
CARD_REL = "04-knowledge/units/terms/foreign-travellers.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "外国旅行者"
NAME_EN = "Foreign Travellers"
DATE = "2026-10-20"
PROCESS_ANCHOR = "s4-foreign-travellers-term-crosschapter-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
RELATION_IDS = {
    "st-chp4-intro-l3-8-foreign-travellers-flocked-to-rome",
    "st-chp5-p129-dealers_and_travellers",
    "st-chp9-p245-footnote1-measures-and-brosses",
    "st-chp9-p245-visitor-access",
    "st-chp9-p246-betrothal-judgment",
}
DIRECT_STATEMENT_IDS = RELATION_IDS | {"st-chp4-intro-l3-8-rome-collecting-scene"}
SOURCES = (
    {
        "file": "01_CHP-1_sec_ii.md",
        "location": "第1章 sec. ii，OCR L4",
        "span": "line 4",
        "quote": "activities of foreign travellers and their agents",
        "summary": "第1章把外国旅行者及其代理人列为艺术家与客户关系中的中介活动之一。",
    },
    {
        "file": "04_CHP-4_intro.md",
        "location": "第4章导言，OCR L7",
        "span": "line 7",
        "quote": "foreign travellers who flocked to the city",
        "summary": "第4章称外国旅行者前往罗马参观私人收藏；不据此识别个人或同一旅行团。",
    },
    {
        "file": "05_CHP-5_sec_i.md",
        "location": "第5章，印刷页129；OCR L105",
        "span": "line 105; print p. 129",
        "quote": "travellers of all kinds, including Protestants",
        "summary": "第5章以各类旅行者（包括新教徒）说明罗马对旅行者更易到达。",
    },
    {
        "file": "09_CHP-9_intro.md",
        "location": "第9章，印刷页245；OCR L13–15",
        "span": "lines 13–15; print p. 245",
        "quote": "Foreign ambassadors, and sometimes even ordinary travellers, were kept to themselves and refused contact with the nobility",
        "summary": "第9章区分外国使节与普通旅行者，并叙述他们与贵族接触受限；脚注另转述 de Brosses 关于外国人较少获接见的说法。",
    },
    {
        "file": "09_CHP-9_intro.md",
        "location": "第9章，印刷页246；OCR L22",
        "span": "line 22; print p. 246",
        "quote": "mainly the tourists who found such ceremonies as The Betrothal of the Sea somewhat ridiculous",
        "summary": "第9章把对“海上婚礼”仪式的评价归于游客群体；保留为 Haskell 的概括。",
    },
)


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_file = f"02-sources/02-Markdown/{item['file']}"
        chapter = item["location"].split("，")[0]
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source_file,
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本术语记录哈斯克尔在书中使用的外国旅行者、游客及外国来访者等一般类别。第1章将旅行者及其代理人置于艺术家与客户关系的中间环节；第4、5章分别讨论赴罗马参观收藏及罗马对各类旅行者的可达性；第9章区分外国使节、普通旅行者与游客在威尼斯政治文化叙述中的位置。上述称谓服务于不同语境，不表示各章指向同一批人。来源：[第1章](../../../02-sources/02-Markdown/01_CHP-1_sec_ii.md#L4)、[第4章](../../../02-sources/02-Markdown/04_CHP-4_intro.md#L7)、[第5章 p.129](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md#L105)、[第9章 pp.245–246](../../../02-sources/02-Markdown/09_CHP-9_intro.md#L13)。

**English:** This term records the general categories of foreign travellers, tourists, and foreign visitors used in Haskell’s account. Chapter 1 places travellers and their agents among the intermediaries between artists and clients; Chapters 4 and 5 discuss visits to Roman collections and Rome’s accessibility to travellers of different kinds; Chapter 9 distinguishes foreign ambassadors, ordinary travellers, and tourists in its account of Venetian political culture. These labels belong to different contexts and do not identify the same people across chapters. Sources: [Chapter 1](../../../02-sources/02-Markdown/01_CHP-1_sec_ii.md#L4), [Chapter 4](../../../02-sources/02-Markdown/04_CHP-4_intro.md#L7), [Chapter 5, p. 129](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md#L105), [Chapter 9, pp. 245–246](../../../02-sources/02-Markdown/09_CHP-9_intro.md#L13).

### 术语范围与边界

**书内用法：** 候选 `cand-3562` 是一般类别，不是具名人物、正式组织或单一旅行团。不同段落分别涉及艺术市场中介、罗马收藏访客、各类赴罗马旅行者、威尼斯的外国使节／普通来访者，以及对仪式持评价的游客；不把这些人群合并成一个历史群体或推断个体经历。

**相邻术语：** 第7章索引所列“17世纪后半赴意大利的英国游客”（`units/terms/english-tourists-italy-late-seventeenth-century`）具有明确国别与时代范围，仍独立保留；本卡不将其并入或扩展为该群体。

## 关系与证据

### 关系记录

以下5条直接 S2 关系候选均保留待 S6 逐条审查；登记术语端点不预先决定关系类型、方向或事实成立：{", ".join(f"`{item}`" for item in sorted(RELATION_IDS))}。
"""


def preserve_bom_write_csv(path: Path, fieldnames, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fieldnames, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter foreign travellers term group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE].get("suggested_type") == "term"
    target_rows = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    ]
    assert len(target_rows) == 1
    target = target_rows[0]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert result_sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row.get("candidate_id") for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "term"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    ), "same-title term already exists in the manifest"

    for item in SOURCES:
        source_file = ROOT / "02-sources" / "02-Markdown" / item["file"]
        source_text = " ".join(source_file.read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, item["quote"]

    statements = result_sync.load_statements()
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_ids = {row["statement_id"] for row in direct_statements}
    relation_ids = {
        row["statement_id"] for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert direct_ids == DIRECT_STATEMENT_IDS, (direct_ids - DIRECT_STATEMENT_IDS, DIRECT_STATEMENT_IDS - direct_ids)
    assert relation_ids == RELATION_IDS

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] = (
        (planned_target.get("resolution_note") or "")
        + f" S4 registration: mapped {GROUP} to {KU_ID}; the card treats chapter-specific visitor labels as distinct contexts, not one historical cohort."
    )
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "term",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]

    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    before_queue = s4_helpers.compute_direct_queue(candidate_by_id, alignments, statements)
    direct_queue = s4_helpers.compute_direct_queue(candidate_by_id, planned_alignment, statements)
    assert before_queue["groups"] == direct_queue["groups"] + 1
    assert before_queue["members"] == direct_queue["members"] + 1
    assert before_queue["endpoint_candidates"] == direct_queue["endpoint_candidates"] + 1

    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_entry = (
        "\n\n### S4 term：外国旅行者跨章术语组（2026-10-20）\n\n"
        f"`{CANDIDATE}` 沿用既有 S3 `new` 组 `{GROUP}`，登记至[外国旅行者术语卡](../units/terms/foreign-travellers.md)。"
        "第1、4、5、9章提供不同语境的来源锚点；旅行者、游客、外国人、使节与普通来访者不视为同一批人。"
        "第7章限定为17世纪后半赴意大利英国游客的术语卡保持独立。5条直接 S2 关系候选留待 S6；"
        "本次未新增正式关系、S5字段或外部身份核验。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])}组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])}条映射；"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text = result_text.rstrip() + result_entry + "\n"

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text = s4_helpers.refresh_knowledge_table(process_text, stats)
    process_entry = (
        "\n\n<a id=\"" + PROCESS_ANCHOR + "\"></a>\n\n"
        "### S4 term：外国旅行者跨章术语组（2026-10-20）\n\n"
        f"`{CANDIDATE}` 沿用既有 S3 `new` term 组 `{GROUP}`，登记至[外国旅行者术语卡](../../../{CARD_REL})。"
        "第1章将旅行者及其代理人置于艺术家—客户关系的中间环节；第4章称外国旅行者前往罗马参观收藏；"
        "第5章以各类旅行者（包括新教徒）说明罗马对来访者的可达性；第9章分别涉及外国使节、普通旅行者及游客。"
        "这些称谓处于不同叙述语境，不构成同一历史群体或个人身份判断。第7章已有的英国游客术语卡范围更窄，继续独立。"
        f"5条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）保留待 S6；本次未新增 formal 关系、S5 字段或外部身份核验。"
        f"登记后 S4 已登记{result_sync.fmt(totals['registered_groups'])}组／{result_sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{result_sync.fmt(totals['pending_groups'])}组／{result_sync.fmt(totals['pending_members'])}条映射；"
        f"直接端点队列由{before_queue['groups']}组／{before_queue['members']}成员降至{direct_queue['groups']}组／{direct_queue['members']}成员。"
    )
    process_text = process_text.rstrip() + process_entry + "\n"
    agents_text = s4_helpers.refresh_agents(
        AGENTS_PATH.read_text(encoding="utf-8-sig"), totals, direct_queue,
        statements, result_sync.read_csv(TABLES / "relations.csv")[1],
        [json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()],
    )

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 term dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"source anchors={len(SOURCES)}; direct S2 relation candidates={len(relation_ids)}; no formal edge created")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(
            f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, "
            f"{totals['registered_members']:,}/{totals['new_candidates']:,} mappings; "
            f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}"
        )
        print(f"direct queue={before_queue['groups']:,}/{before_queue['members']:,} -> {direct_queue['groups']:,}/{direct_queue['members']:,}")
        print("result, process table, and AGENTS snapshot refreshed in memory only")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8", newline="\n")
    preserve_bom_write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    preserve_bom_write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']:,}/{totals['registered_members']:,}; "
        f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}; "
        f"direct={before_queue['groups']:,}->{direct_queue['groups']:,} groups"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
