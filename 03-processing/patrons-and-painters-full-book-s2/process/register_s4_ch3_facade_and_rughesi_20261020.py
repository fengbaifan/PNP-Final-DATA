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
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 3, p. 69."
)

FACADE = {
    "candidate_id": "cand-5032",
    "group": "workgrp-719c454f6671a5",
    "ku_id": "units/works/facade-chiesa-nuova",
    "card_rel": "04-knowledge/units/works/facade-chiesa-nuova.md",
    "name_zh": "Chiesa Nuova立面",
    "name_en": "Façade of Chiesa Nuova",
}
RUGHESI = {
    "candidate_id": "cand-2309",
    "group": "new-person:fausto-rughesi-0ad1c7880f",
    "ku_id": "units/persons/fausto-rughesi",
    "card_rel": "04-knowledge/units/persons/fausto-rughesi.md",
    "name_zh": "福斯托·鲁盖西",
    "name_en": "Fausto Rughesi",
}
HEADING = "### S4：Chiesa Nuova 立面与 Fausto Rughesi（2026-10-20）"
PROCESS_ANCHOR = "s4-ch3-facade-fausto-rughesi-20261020"
STATEMENT_ID = "st-chp3-secii-l40-52-façade-erection-delay"
QUOTE = "the façade by Fausto Rughesi was not erected for another sixteen years."


def card_frontmatter(*, title: str, name_en: str, entity_type: str, summary: str) -> str:
    frontmatter = {
        "title": title,
        "name_en": name_en,
        "type": entity_type,
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第3章，印刷页69；来源转录第46行。",
                "sentence_summary": summary,
                "original_quotes": [{"source_span": "line 46; print p. 69", "text": QUOTE}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "line 46; print p. 69",
                },
            }
        ],
        "created": "2026-10-20",
        "updated": "2026-10-20",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    return yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)


def make_facade_card() -> str:
    fm = card_frontmatter(
        title=f"{FACADE['name_zh']}（{FACADE['name_en']}）",
        name_en=FACADE["name_en"],
        entity_type="work",
        summary="Haskell称Chiesa Nuova主结构完成后，Fausto Rughesi所作立面又过十六年才建成。",
    )
    source_link = f"[第3章 p.69](../../../{SOURCE_FILE})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡依既有 S3 身份分组登记 Haskell 在 Chiesa Nuova 建筑叙述中称为立面的对象。原文将其表述为“by Fausto Rughesi”；本卡记录该来源归属，不据此补充建筑师身份或外部核验结论。{source_link}

**English:** This unit follows the existing S3 identity group for the object Haskell calls the façade in his account of Chiesa Nuova. The source describes it as “by Fausto Rughesi”; this card records that attribution without adding a biographical role or external identity claim. {source_link}

### 本章相关内容

Haskell称，教堂主结构到1590年已完成，而立面又过十六年才建成。原文只给出相对间隔；本卡不把该表述换算为精确建成年份。主结构完成与立面建成的时间关系仍须按 S6 逐条裁决。

## 关系与证据

### 正式关系

本次未新增正式关系。直接 S2 候选 `{STATEMENT_ID}` 的两端现均有 KU，但关系类型、时间语境及证据仍待 S6 审查。Fausto Rughesi 的作者归属保留为 Haskell 的来源表述；本次不新增 S2 断言或正式 `created_by` 关系。
"""


def make_person_card() -> str:
    fm = card_frontmatter(
        title=f"{RUGHESI['name_zh']}（{RUGHESI['name_en']}）",
        name_en=RUGHESI["name_en"],
        entity_type="person",
        summary="Haskell将Chiesa Nuova立面称为Fausto Rughesi所作。",
    )
    source_link = f"[第3章 p.69](../../../{SOURCE_FILE})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记 Haskell 在 Chiesa Nuova 立面叙述中点名为 Fausto Rughesi 的人物，沿用既有 S3 书内身份分组。中文名为暂译；本卡不补充未经本书该处支持的生平或外部身份判断。{source_link}

**English:** This unit records the person Haskell names as Fausto Rughesi in the account of the Chiesa Nuova façade, following the existing S3 source-local identity group. The Chinese rendering is provisional; this card adds no biography or external identity claim unsupported by this passage. {source_link}

### 名称

来源拼写为 Fausto Rughesi；本项目中文暂译为“{RUGHESI['name_zh']}”。原文锚点为第3章第46行，印刷页69。

### 本章相关内容

Haskell将 Chiesa Nuova 立面称为 Fausto Rughesi 所作，并说明其建成晚于教堂主结构完成。这里仅记录本段来源中的姓名与归属表述，不据此推断其职业头衔、其他作品或生平。

## 关系与证据

### 正式关系

本次未新增正式关系。立面归属按来源表述保留；正式创作者关系尚未写入 `relations.csv`。
"""


def write_csv_preserving_bom(path: Path, fields, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fields, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Chiesa Nuova façade and source-named creator S4 units.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    statements = result_sync.load_statements()

    targets = []
    for spec, expected_type in ((FACADE, "work"), (RUGHESI, "person")):
        candidate = candidate_by_id[spec["candidate_id"]]
        assert candidate.get("suggested_type") == expected_type
        rows = [
            row for row in alignments
            if row.get("candidate_id") == spec["candidate_id"] and not row.get("external_source")
        ]
        assert len(rows) == 1
        target = rows[0]
        assert target.get("decision") == "new" and not target.get("ku_id")
        assert result_sync.get_group(target.get("resolution_note", "")) == spec["group"]
        group_rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and result_sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert [row.get("candidate_id") for row in group_rows] == [spec["candidate_id"]]
        assert not (ROOT / spec["card_rel"]).exists()
        assert not any(row.get("ku_id") == spec["ku_id"] or row.get("card_path") == spec["card_rel"] for row in manifest)
        targets.append(target)

    for spec, entity_type in ((FACADE, "work"), (RUGHESI, "person")):
        assert not any(
            row.get("type") == entity_type
            and (row.get("name_en", "").casefold() == spec["name_en"].casefold()
                 or row.get("canonical_name", "").casefold() == spec["name_zh"].casefold())
            for row in manifest
        ), f"same-title entity already exists: {spec['ku_id']}"

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert all(spec["card_rel"] not in accepted for spec in (FACADE, RUGHESI))
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert " ".join(QUOTE.split()) in source_text

    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") == FACADE["candidate_id"]
        or row.get("object_candidate_id") == FACADE["candidate_id"]
    ]
    assert {row["statement_id"] for row in direct_statements} == {
        STATEMENT_ID,
        "st-chp3-secii-l54-60-decoration-funds-absorbed-by-facade-costs",
    }
    assert all(row.get("qualifiers", {}).get("relation_candidate") is True for row in direct_statements)
    endpoint_rows = [
        row for row in alignments
        if row.get("candidate_id") == "cand-0710" and row.get("ku_id") and not row.get("external_source")
    ]
    assert endpoint_rows, "Chiesa Nuova church endpoint must already have a KU"
    rughesi_mentions = [row for row in direct_statements if row.get("qualifiers", {}).get("artist_candidate_id") == RUGHESI["candidate_id"]]
    assert {row["statement_id"] for row in rughesi_mentions} == {STATEMENT_ID}

    planned_alignment = [dict(row) for row in alignments]
    for spec, target in zip((FACADE, RUGHESI), targets):
        planned_target = next(
            row for row in planned_alignment
            if row.get("candidate_id") == spec["candidate_id"] and not row.get("external_source")
        )
        planned_target["ku_id"] = spec["ku_id"]
        planned_target["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
        planned_target["resolution_note"] = (
            (planned_target.get("resolution_note") or "")
            + f" S4 registration (2026-10-20): mapped {spec['group']} to {spec['ku_id']}; "
              "registration is source-local and does not add external identity verification or a formal relation."
        )

    planned_manifest = list(manifest)
    for spec, entity_type in ((FACADE, "work"), (RUGHESI, "person")):
        planned_manifest.append({
            "ku_id": spec["ku_id"],
            "type": entity_type,
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": spec["card_rel"],
        })

    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    before_queue = s4_helpers.compute_direct_queue(candidate_by_id, alignments, statements)
    after_queue = s4_helpers.compute_direct_queue(candidate_by_id, planned_alignment, statements)
    assert before_queue["groups"] == after_queue["groups"] + 1
    assert before_queue["members"] == after_queue["members"] + 1
    assert before_queue["endpoint_candidates"] == after_queue["endpoint_candidates"] + 1

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    assert PROCESS_ANCHOR not in process_text and HEADING not in process_text
    assert HEADING not in result_text
    process_text = s4_helpers.refresh_knowledge_table(process_text, stats)
    process_text += (
        f"\n\n{HEADING}\n\n"
        f"`{FACADE['candidate_id']}` 沿用 S3 `new` 组 `{FACADE['group']}`，登记为立面 work；"
        f"`{RUGHESI['candidate_id']}` 沿用 S3 `new` 组 `{RUGHESI['group']}`，登记为来源点名的人物。"
        "第3章 p.69 称 Chiesa Nuova 的主结构到1590年已完成，Fausto Rughesi所作立面又过十六年才建成；"
        "保留来源给出的相对间隔，不换算精确年份。该句的 S2 关系候选两端现均有 KU；仍须 S6 审查关系类型、方向、时间语境和证据。"
        "人物及作品身份均沿用书内 S3 分组，未作外部身份核验；本次未新增 S2 断言、正式关系或 S5 字段。"
        f"登记后 S4 已登记 {result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])} 组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])} 条映射；"
        f"待登记 {result_sync.fmt(totals['pending_groups'])} 组／{result_sync.fmt(totals['pending_members'])} 条映射。"
        f"直接端点队列由 {before_queue['groups']:,} 组／{before_queue['members']:,} 成员降至 "
        f"{after_queue['groups']:,} 组／{after_queue['members']:,} 成员。"
    )
    result_text = result_sync.update_result(result_text, stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n{HEADING}\n\n"
        f"`{FACADE['candidate_id']}` 与 `{RUGHESI['candidate_id']}` 分别沿用既有 S3 `new` 组，"
        "登记 Chiesa Nuova 立面 work 与来源点名的 Fausto Rughesi 人物卡。Haskell称主结构到1590年已完成，而立面又过十六年才建成；"
        "保留相对时间，不换算绝对年份。相关 S2 关系候选两端现均已有 KU，关系裁决留待 S6。"
        "不新增 S2 断言、正式关系、外部身份核验或 S5 字段。"
        f"当前 S4 登记 {totals['registered_groups']:,}/{totals['new_groups']:,} 组、"
        f"{totals['registered_members']:,}/{totals['new_candidates']:,} 条映射；"
        f"待登记 {totals['pending_groups']:,} 组／{totals['pending_members']:,} 条映射。"
    )

    altar_path = ROOT / "04-knowledge/units/works/high-altar-chiesa-nuova.md"
    altar_text = altar_path.read_text(encoding="utf-8-sig")
    old_status = "四条候选中，三条的两端现均有对应 KU（两条涉及圣母诞生，一条涉及 Angelo Cesi）；涉及立面费用的另一条中，立面对象 `cand-5032` 尚未登记。即使端点齐备，以上候选仍须经 S6 语义裁决后才能成为正式关系。"
    new_status = "四条候选的两端现均有对应 KU（两条涉及圣母诞生，一条涉及 Angelo Cesi，一条涉及立面费用）；以上候选仍须经 S6 逐条语义裁决后才能成为正式关系。"
    assert altar_text.count(old_status) == 1
    altar_text = altar_text.replace(old_status, new_status)

    accepted_lines = accepted.splitlines()
    for spec in sorted((FACADE, RUGHESI), key=lambda item: item["card_rel"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > spec["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {spec['card_rel']}")

    relations = result_sync.read_csv(TABLES / "relations.csv")[1]
    enrichment = [
        json.loads(line)
        for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    agents_text = s4_helpers.refresh_agents(
        AGENTS_PATH.read_text(encoding="utf-8-sig"), totals, after_queue,
        statements, relations, enrichment,
    )

    if args.dry_run:
        print(f"S4 dry-run passed: {FACADE['candidate_id']} -> {FACADE['ku_id']}; {RUGHESI['candidate_id']} -> {RUGHESI['ku_id']}")
        print(f"source quotation checked; direct statements={len(direct_statements)}; all relation-candidate endpoints have KUs")
        print(f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, {totals['registered_members']:,}/{totals['new_candidates']:,} mappings")
        print(f"direct endpoint queue={before_queue['groups']:,}/{before_queue['members']:,} -> {after_queue['groups']:,}/{after_queue['members']:,}")
        print("No S2, S5, or S6 records are changed by the planned write.")
        return 0

    (ROOT / FACADE["card_rel"]).write_text(make_facade_card(), encoding="utf-8", newline="\n")
    (ROOT / RUGHESI["card_rel"]).write_text(make_person_card(), encoding="utf-8", newline="\n")
    write_csv_preserving_bom(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv_preserving_bom(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    altar_path.write_text(altar_text, encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(
        f"applied: 2 KU groups; registered={totals['registered_groups']:,}/{totals['new_groups']:,}; "
        f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}; "
        f"direct endpoint groups={before_queue['groups']:,}->{after_queue['groups']:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
