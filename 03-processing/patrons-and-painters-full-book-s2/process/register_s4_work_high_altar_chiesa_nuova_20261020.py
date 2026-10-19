from __future__ import annotations

import argparse
import json
import re
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

CANDIDATE = "cand-5033"
GROUP = "workgrp-d80b6b26bc76a0"
KU_ID = "units/works/high-altar-chiesa-nuova"
CARD_REL = "04-knowledge/units/works/high-altar-chiesa-nuova.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "Chiesa Nuova主祭坛"
NAME_EN = "High Altar of Chiesa Nuova"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), ch. 3, pp. 69–70."
)
DIRECT_IDS = {
    "st-chp3-secii-l40-52-high-altar-nativity",
    "st-chp3-secii-l54-60-cesi-promised-high-altar-decoration",
    "st-chp3-secii-l54-60-decoration-funds-absorbed-by-facade-costs",
    "st-chp3-secii-l54-60-high-altar-nativity-dedication",
}
QUOTES = (
    (
        "lines 47–48; print p. 69",
        "The chapels were then dedicated to the mysteries of the Virgin, the High Altar being assigned to Her Nativity and those in the transepts to Her Presentation and Her Coronation.",
    ),
    (
        "line 58; print p. 70",
        "The High Altar had been originally dedicated to the Nativity; its decoration had been promised by Cardinal Angelo Cesi.",
    ),
    (
        "line 58; print p. 70",
        "the money set aside for its decoration was found to have been absorbed in the unexpected expenses of the façade.",
    ),
)
HEADING = "### S4 work：Chiesa Nuova 主祭坛（2026-10-20）"
PROCESS_ANCHOR = "s4-work-high-altar-chiesa-nuova-20261020"


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第3章，印刷页69–70；来源转录第47–48、58行。",
                "sentence_summary": (
                    "Haskell 称主祭坛最初奉献于圣母诞生，并称 Cardinal Angelo Cesi 曾承诺装饰；"
                    "约1605年预留给其装饰的款项据称被意外的立面费用吸收。"
                ),
                "original_quotes": [
                    {"source_span": span, "text": quote} for span, quote in QUOTES
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": "lines 47–48, 58; print pp. 69–70",
                },
            }
        ],
        "created": "2026-10-20",
        "updated": "2026-10-20",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"[第3章 pp.69–70](../../../{SOURCE_FILE})"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 在 Chiesa Nuova 叙述中称为“High Altar”的对象，按既有 S3 身份决定登记为 work。第69页称主祭坛分配予圣母诞生；第70页称其原奉献于圣母诞生，装饰曾由原文所称“Cardinal Angelo Cesi”承诺。约1605年预留给“其装饰”的款项据称被立面的意外费用吸收。“其”的先行词依 S2 暂指主祭坛；本卡不把它等同于后文的祭坛画，也不将枢机头衔冲突改写为已核实身份。{source_link}

**English:** This unit records the object Haskell calls the “High Altar” in his account of Chiesa Nuova, following the existing S3 identity decision to register it as a work. Haskell says on p. 69 that the High Altar was assigned to the Nativity of the Virgin; on p. 70 he says it was originally dedicated to the Nativity and that decoration had been promised by the person he calls “Cardinal Angelo Cesi.” Funds set aside for “its decoration” were reportedly absorbed by unexpected façade expenses around 1605. S2 provisionally resolves “its” to the High Altar. This unit keeps the altar distinct from the later altarpiece and does not treat the disputed cardinal title as verified identity. {source_link}

### 本章相关内容

Haskell 将装饰承诺、约1605年的款项状况及立面费用分别叙述。款项与立面费用之间的具体机制未明；本卡保留原书报告，不补作资金转移解释。Cardinal Angelo Cesi 的人物身份沿用 S3 指向 Angelo Cesi, Bishop of Todi 的映射，枢机称谓冲突及承诺事实本身均保持原有来源限定。

## 关系与证据

### 正式关系

本次未新增正式关系。以下4条直接 S2 关系候选仍待 S6 逐条审查：

- `st-chp3-secii-l40-52-high-altar-nativity`
- `st-chp3-secii-l54-60-cesi-promised-high-altar-decoration`
- `st-chp3-secii-l54-60-decoration-funds-absorbed-by-facade-costs`
- `st-chp3-secii-l54-60-high-altar-nativity-dedication`

四条候选中，三条的两端现均有对应 KU（两条涉及圣母诞生，一条涉及 Angelo Cesi）；涉及立面费用的另一条中，立面对象 `cand-5032` 尚未登记。即使端点齐备，以上候选仍须经 S6 语义裁决后才能成为正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def write_csv_preserving_bom(path: Path, fields, rows) -> None:
    had_bom = path.read_bytes().startswith(b"\xef\xbb\xbf")
    result_sync.write_csv(path, fields, rows)
    if not had_bom and path.read_bytes().startswith(b"\xef\xbb\xbf"):
        path.write_bytes(path.read_bytes()[3:])


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Chiesa Nuova High Altar S4 work endpoint.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate = candidate_by_id[CANDIDATE]
    assert candidate.get("suggested_type") == "work"

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
        row.get("type") == "work"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    ), "same-title work already exists in the manifest"
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for _, quote in QUOTES:
        assert " ".join(quote.split()) in source_text, quote

    statements = result_sync.load_statements()
    direct_statements = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    assert {row["statement_id"] for row in direct_statements} == DIRECT_IDS
    relation_ids = {
        row["statement_id"] for row in direct_statements
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    assert relation_ids == DIRECT_IDS
    assert all(row.get("origin") == "book" for row in direct_statements)

    registered_endpoint_ids = {"cand-0639", "cand-5035"}
    for endpoint_id in registered_endpoint_ids:
        endpoint_rows = [row for row in alignments if row.get("candidate_id") == endpoint_id and row.get("ku_id")]
        assert endpoint_rows, endpoint_id
    facade_rows = [row for row in alignments if row.get("candidate_id") == "cand-5032" and not row.get("external_source")]
    assert len(facade_rows) == 1 and not facade_rows[0].get("ku_id")

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}"
    planned_target["resolution_note"] = (
        (planned_target.get("resolution_note") or "")
        + f" S4 registration (2026-10-20): mapped {GROUP} to {KU_ID}; card records the source-described High Altar "
        "as a work, distinct from the later altarpiece. The Cesi title wording and the provisional antecedent of “its” "
        "remain source-qualified; four relation candidates await S6."
    )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "work",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
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
        f"`{CANDIDATE}` 沿用既有 S3 `new` 身份组 `{GROUP}`，登记至"
        f"[Chiesa Nuova 主祭坛卡](../../../{CARD_REL})。第3章 pp.69–70 将对象称为 High Altar，"
        "称其分配／原奉献于圣母诞生，并报告 Cardinal Angelo Cesi 曾承诺装饰；约1605年预留款据称被意外立面费用吸收。"
        "卡片保留 S2 对“its”先行词的暂定判断和 Cardinal 头衔冲突，不将祭坛与后文祭坛画混同，不补资金转移机制。"
        f"4条直接 S2 关系候选（{', '.join(sorted(DIRECT_IDS))}）均留待 S6；圣母诞生与 Angelo Cesi 端点已有 KU，"
        "立面候选 `cand-5032` 尚未登记；本次无 formal 关系、外部身份核验或 S5 字段写入。"
        f"登记后 S4 已登记 {result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['new_groups'])} 组、"
        f"{result_sync.fmt(totals['registered_members'])}/{result_sync.fmt(totals['new_candidates'])} 条映射；"
        f"待登记 {result_sync.fmt(totals['pending_groups'])} 组／{result_sync.fmt(totals['pending_members'])} 条映射。"
        f"直接端点队列由 {before_queue['groups']:,} 组／{before_queue['members']:,} 成员降至 "
        f"{after_queue['groups']:,} 组／{after_queue['members']:,} 成员。"
    )
    result_text = result_sync.update_result(result_text, stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n{HEADING}\n\n"
        f"`{CANDIDATE}` 沿用 S3 `new` 组 `{GROUP}`，登记至[Chiesa Nuova 主祭坛卡](../units/works/high-altar-chiesa-nuova.md)。"
        "第3章 pp.69–70 记载主祭坛与圣母诞生的奉献关系、Cardinal Angelo Cesi 的装饰承诺及约1605年预留款被意外立面费用吸收的报告。"
        "卡片按原书来源保留头衔冲突和‘its’暂定先行词，区分主祭坛与后文祭坛画。4条直接关系候选留待 S6；"
        "圣母诞生及 Angelo Cesi 已有 KU，立面 `cand-5032` 待登记。未新增正式关系、外部身份或 S5 字段。"
        f"S4 登记 {totals['registered_groups']:,}/{totals['new_groups']:,} 组、{totals['registered_members']:,}/{totals['new_candidates']:,} 条映射；"
        f"待登记 {totals['pending_groups']:,} 组／{totals['pending_members']:,} 条映射。"
    )
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
        print(f"S4 work dry-run passed: {CANDIDATE} -> {KU_ID}; group members={len(group_rows)}")
        print(f"source quotations checked={len(QUOTES)}; direct statements={len(direct_statements)}; relation candidates={len(relation_ids)}")
        print(f"registered={totals['registered_groups']:,}/{totals['new_groups']:,} groups, {totals['registered_members']:,}/{totals['new_candidates']:,} mappings")
        print(f"direct endpoint queue={before_queue['groups']:,}/{before_queue['members']:,} -> {after_queue['groups']:,}/{after_queue['members']:,}")
        print("3 relation candidates have registered endpoint KUs; the façade endpoint for the remaining candidate is still pending")
        print("No S2, S5, or S6 records are changed by the planned write.")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8", newline="\n")
    write_csv_preserving_bom(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv_preserving_bom(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']:,}/{totals['new_groups']:,}; "
        f"pending={totals['pending_groups']:,}/{totals['pending_members']:,}; "
        f"direct={before_queue['groups']:,}->{after_queue['groups']:,} groups"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
