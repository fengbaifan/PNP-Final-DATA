from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as process_sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "new-person:guarini-guarino-bdced3f938"
MEMBERS = ("cand-6876",)
KU_ID = "units/persons/guarino-guarini"
CARD_REL = "04-knowledge/units/persons/guarino-guarini.md"
NAME_ZH = "瓜里诺·瓜里尼"
NAME_EN = "Guarino Guarini"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
SOURCE_186 = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE_193 = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
PROCESS_ANCHOR = "s4-person-guarino-guarini-20261017"
RELATION_IDS = (
    "st-chp7-p186-i09",
    "st-chp7-p186-i10",
    "st-chp7-p193-adelaide-fails-to-attract-guarini",
)
QUOTE_186 = (
    "For this purpose the Theatines summoned a member of their own order, "
    "Guarino Guarini, who arrived in 1662. There he began work on the church "
    "which was interrupted in 1669 and only completed some fifty years later."
)
QUOTE_193 = "She failed in her attempt to attract Guarino Guarini,"


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def sources():
    return [
        {
            "citation": BOOK_CITATION,
            "location": "第7章，印刷页186；Markdown L219；PDF物理页24。",
            "sentence_summary": (
                "Haskell称Theatines为圣安娜—皇家教堂项目召来本会成员Guarino Guarini，"
                "并记其于1662年抵达、开始教堂工程；工程于1669年中断，约五十年后才完成。"
            ),
            "original_quotes": [
                {"source_span": "line 219; print p. 186; PDF physical p. 24", "text": QUOTE_186}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_186,
                "source_span": "line 219; print p. 186; PDF physical p. 24",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章，印刷页193；Markdown L15；PDF物理页31。",
            "sentence_summary": (
                "Haskell称Adelaide Enrichetta未能如愿吸引Guarino Guarini；"
                "该句没有说明邀请条件或发生时间。"
            ),
            "original_quotes": [
                {"source_span": "line 15; print p. 193; PDF physical p. 31", "text": QUOTE_193}
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_193,
                "source_span": "line 15; print p. 193; PDF physical p. 31",
            },
        },
    ]


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch7p186 = f"[第7章 p.186](../../../{SOURCE_186})（L219）"
    ch7p193 = f"[第7章 p.193](../../../{SOURCE_193})（L15）"
    relation_list = "\n".join(f"- {statement_id}" for statement_id in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记书内具名人物 Guarino Guarini，中文名采用项目工作音译。Haskell称 Theatines 为重建圣安娜—皇家教堂召来本会成员 Guarini；他于1662年抵达并开始教堂工程，工程于1669年中断，约五十年后才完成。第7章后文又称 Adelaide Enrichetta 未能如愿吸引 Guarini。以上仅记录 Haskell 的叙述；未独立核验其生平或相关事件，约五十年的工程完成时间不换算为确切年份。{ch7p186}；{ch7p193}

**English:** This card records the person named Guarino Guarini in Haskell’s account; the Chinese form is a project transliteration. Haskell says that the Theatines summoned Guarini, a member of their order, for the rebuilding of the church of St Anne-la-Royale. He arrived in 1662 and began work on the church; the work was interrupted in 1669 and completed about fifty years later. A later passage says that Adelaide Enrichetta failed to attract him. These are Haskell’s reports; Guarini’s biography and the events have not been independently verified, and the approximate completion interval is not converted into a precise year. {ch7p186}; {ch7p193}

### 姓名与身份范围

- **书内全名：** Guarino Guarini。{ch7p186}；{ch7p193}
- **中文工作音译：** {NAME_ZH}，仅作项目展示名，不作为原语姓名或独立身份依据。
- **身份范围：** 本卡登记人物；只记录本书所述与 Theatines 及圣安娜—皇家教堂项目相关的语境。{ch7p186}

### 本书相关内容

- 第7章 p.186 称 Theatines 召来本会成员 Guarini 参与重建圣安娜—皇家教堂；原文称其于1662年抵达，随后开始教堂工程。Haskell称工程于1669年中断，并“约五十年后”才完成；本卡保留约数，不推算完成年份。{ch7p186}
- 第7章 p.193 称 Adelaide Enrichetta 曾试图吸引 Guarini，但未能如愿；该处没有交代邀请的条件和时间。{ch7p193}
- 类型边界：Theatines 对应机构候选 cand-2564，已复用既有 KU units/institutions/theatines；圣安娜—皇家教堂为地点候选 cand-6875，S3 new、待 S4；Adelaide Enrichetta 为人物候选 cand-2380，S3 new、待 S4。它们不并入 Guarini 人物身份。

## 关系与证据

当前没有正式关系记录。下列直接 S2 关系候选均留待 S6 核对端点、方向、语境和证据：

{relation_list}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Guarino Guarini's S4 person identity group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert set(MEMBERS) <= set(candidate_by_id)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "person"
        assert candidate_by_id[cid].get("canonical_name") == NAME_EN
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    registered = [
        row for row in manifest
        if row.get("ku_id") == KU_ID and row.get("card_path") == CARD_REL
    ]
    if (
        registered and card_path.exists() and CARD_REL in accepted
        and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS)
    ):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 3 relation candidates remain pending S6.")
        return 0
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and NAME_EN.casefold() == (row.get("name_en") or "").casefold()
        for row in manifest
    )

    for relative, quote in ((SOURCE_186, QUOTE_186), (SOURCE_193, QUOTE_193)):
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert normalized(quote) in normalized(source_text), f"source quote changed: {relative}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [
        row for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row.get("statement_id") for row in direct} == set(RELATION_IDS)
    assert {row.get("statement_id") for row in relations} == set(RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration: mapped {GROUP} to {KU_ID}; "
            "source-local person identity, no external identity verification."
        )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated person card frontmatter is invalid"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S4 person：Guarino Guarini 跨章身份组登记（{DATE}）\n\n"
        f"- cand-6876 保持 S3 new 组 {GROUP}，映射至[{NAME_ZH}（{NAME_EN}）人物卡](../../../{CARD_REL})（{KU_ID}）。"
        "第7章 p.186 与 p.193 均明载同一全名，候选分组保留单一人物；本次仅据书内全名登记，不作外部身份或生平核验。\n"
        "- p.186 称 Theatines 召来本会成员 Guarini，记其1662年抵达、开始圣安娜—皇家教堂工程，工程1669年中断并约五十年后完成；"
        "p.193 称 Adelaide Enrichetta 未能吸引 Guarini，未详邀请条件或时间。工程完成时间保持约数。\n"
        "- 3 条直接关系候选（{', '.join(RELATION_IDS)}）全部留待 S6。cand-2564 Theatines 已映射 units/institutions/theatines；"
        "cand-6875 圣安娜—皇家教堂与 cand-2380 Adelaide Enrichetta 各自保持 S3 new、待 S4；本次不建立正式关系。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"
    next_result += (
        f"\n\n### person：Guarino Guarini 跨章身份组 S4 登记（{DATE}）\n\n"
        "cand-6876 登记至[人物卡](../units/persons/guarino-guarini.md)。第7章 p.186、p.193 的全名一致；"
        "本卡只记录 Haskell 的书内叙述。3 条直接关系候选待 S6；Theatines 已映射既有机构 KU，"
        "教堂地点与 Adelaide Enrichetta 人物各自待 S4。\n\n"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; sources=2; direct_statements={len(direct)}; "
            f"relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; no files changed"
        )
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; relation_candidates_pending={len(relations)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
