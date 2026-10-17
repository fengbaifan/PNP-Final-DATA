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
GROUP = "new-person:colonna-girolamo-4252615c6d"
MEMBERS = ("cand-0809",)
KU_ID = "units/persons/girolamo-colonna"
CARD_REL = "04-knowledge/units/persons/girolamo-colonna.md"
NAME_ZH = "吉罗拉莫·科隆纳"
NAME_EN = "Girolamo Colonna"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
SOURCE_155 = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
SOURCE_180 = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
PROCESS_ANCHOR = "s4-person-girolamo-colonna-crosschapter-20261017"
RELATION_IDS = (
    "st-chp6-p155-colonna-palace-decorated-by-girolamo",
    "st-chp7-p180-i07",
)
QUOTE_155 = (
    "Their palace, situated near the one sold to the Chigi, had been largely rebuilt and decorated "
    "by Filippo and his son, Cardinal Girolamo, during the first half of the century,"
)
QUOTE_180 = "He accompanied Girolamo Colonna to Spain"


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def sources():
    return [
        {
            "citation": BOOK_CITATION,
            "location": "第6章，印刷页155；Markdown L105；PDF物理页10。",
            "sentence_summary": (
                "Haskell称Colonna家族宫殿在本世纪上半叶由Filippo及其子、枢机Girolamo大幅重建和装饰；"
                "句子将两人并列为参与者，没有区分Girolamo个人的具体贡献。"
            ),
            "original_quotes": [{"source_span": "line 105; print p. 155", "text": QUOTE_155}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_155,
                "source_span": "line 105; print p. 155; PDF physical p. 10",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章，印刷页180；Markdown L132–133；PDF物理页14。",
            "sentence_summary": (
                "Haskell称Mazarin曾陪同Girolamo Colonna前往西班牙；随后称Girolamo任家族所募军团的队长，"
                "该军团意在收复意大利北部的Valtellina。原文没有给出这段旅程的日期。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 132; print p. 180; continuation in line 133",
                    "text": "He accompanied Girolamo Colonna to Spain and then served as captain of a regiment raised by the family to reconquer the Valtellina in North Italy.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_180,
                "source_span": "lines 132–133; print p. 180; PDF physical p. 14",
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
    p155 = f"[第6章 p.155](../../../{SOURCE_155})（L105）"
    p180 = f"[第7章 p.180](../../../{SOURCE_180})（L132–133）"
    relation_list = "\n".join(f"- {statement_id}" for statement_id in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记第6章和第7章具名的枢机 Girolamo Colonna，中文名采用项目工作音译。第6章称他是 Filippo Colonna 之子，并说父子在本世纪上半叶大幅重建和装饰 Colonna 家族宫殿；该句没有区分 Girolamo 的个人贡献。第7章称 Mazarin 曾陪同 Girolamo 前往西班牙，随后 Girolamo 担任家族所募军团的队长以收复意大利北部 Valtellina，原文未给出旅程日期。以上仅记录 Haskell 的书内叙述，未作外部人物或事件核验。{p155}；{p180}

**English:** This card records Cardinal Girolamo Colonna, named in chapters 6 and 7; the Chinese name is a project transliteration. Chapter 6 identifies him as Filippo Colonna’s son and says that the two substantially rebuilt and decorated the Colonna family palace during the first half of the century; the sentence does not distinguish Girolamo’s individual contribution. Chapter 7 says that Mazarin accompanied Girolamo to Spain, after which Girolamo served as captain of a regiment raised by the family to reconquer Valtellina in northern Italy. The passage gives no date for the journey. These remain Haskell’s reports and have not been externally verified. {p155}; {p180}

### 姓名与身份范围

- **书内全名：** Girolamo Colonna。第6章称 Cardinal Girolamo，第7章写作 Girolamo Colonna。{p155}；{p180}
- **中文工作音译：** {NAME_ZH}，仅作项目展示名，不作为原语姓名或独立身份依据。
- **身份范围：** 本卡对应 cand-0809 的单一 S3 new 人物组；不与其父 Filippo Colonna（cand-0806）合并。

### 本书相关内容

- 第6章 p.155 将 Girolamo 与其父 Filippo 并列为 Colonna 家族宫殿的重建、装饰参与者；不细分其个人职责。原文“his son”明确指 Filippo 与 Girolamo 的父子语境，但本轮不据此创建正式亲缘关系。{p155}
- 第7章 p.180 称 Mazarin 陪同 Girolamo Colonna 前往西班牙；随后称 Girolamo 担任家族所募军团队长，以收复意大利北部 Valtellina。旅程日期未载。{p180}
- 端点去向：Colonna 家族宫殿 cand-0815 已登记并映射至 units/places/colonna-family-palace-rome；Mazarin cand-1588 已复用 units/persons/mazarin；Spain cand-5120 已复用 units/places/spain。Filippo Colonna cand-0806 保持独立 S3 new 组、待 S4。
- 关系记录边界：当前两条直接 S2 关系候选留待 S6；父子措辞尚无独立 statement ID，S6 回读本段时一并核查。此卡不把描述性内容转成正式关系。

## 关系与证据

当前没有正式关系记录。下列直接 S2 关系候选均留待 S6 核对端点、方向、语境和证据：

{relation_list}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Girolamo Colonna's cross-chapter S4 person group")
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
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert decisions["cand-0815"].get("decision") == "new"
    assert decisions["cand-0815"].get("ku_id") == "units/places/colonna-family-palace-rome"
    assert decisions["cand-1588"].get("decision") == "same"
    assert decisions["cand-1588"].get("ku_id") == "units/persons/mazarin"
    assert decisions["cand-5120"].get("decision") == "same"
    assert decisions["cand-5120"].get("ku_id") == "units/places/spain"
    assert decisions["cand-0806"].get("decision") == "new"

    card_path = ROOT / CARD_REL
    registered = [
        row for row in manifest
        if row.get("ku_id") == KU_ID and row.get("card_path") == CARD_REL
    ]
    if (
        registered and card_path.exists() and CARD_REL in accepted
        and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS)
    ):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 2 relation candidates remain pending S6.")
        return 0
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and NAME_EN.casefold() == (row.get("name_en") or "").casefold()
        for row in manifest
    )

    for relative, quote in ((SOURCE_155, QUOTE_155), (SOURCE_180, "He accompanied Girolamo Colonna to Spain")):
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
            "full-name anchors in chapters 6 and 7; no external identity verification."
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
        f"### S4 person：Girolamo Colonna 跨章身份组登记（{DATE}）\n\n"
        f"- cand-0809 保持 S3 new 组 {GROUP}，映射至[{NAME_ZH}（{NAME_EN}）人物卡](../../../{CARD_REL})（{KU_ID}）。"
        "第6章 p.155 称 Cardinal Girolamo，第7章 p.180 写出全名 Girolamo Colonna；两处共同支持同一书内人物组，未作外部核验。\n"
        "- 第6章称 Filippo 与其子 Cardinal Girolamo 参与 Colonna 家族宫殿重建、装饰，但没有区分个人贡献；"
        "此处父子措辞尚无单独 S2 statement ID，保留为 S6 回读核查项。cand-0806 Filippo Colonna 独立保持 S3 new、待 S4。\n"
        f"- 两条直接关系候选（{', '.join(RELATION_IDS)}）留待 S6。宫殿 cand-0815 已登记；Mazarin cand-1588 与 Spain cand-5120 已指向既有 KU；"
        "本批没有登记正式关系。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"
    next_result += (
        f"\n\n### person：Girolamo Colonna 跨章身份组 S4 登记（{DATE}）\n\n"
        f"cand-0809 登记至[人物卡](../units/persons/girolamo-colonna.md)。第6章与第7章的全名、称谓相合；"
        "两条关系候选待 S6。Mazarin 与 Spain 复用既有 KU，家族宫殿候选已独立登记；Filippo Colonna 另组待 S4，"
        "原文父子措辞尚无独立 statement ID，留待 S6 回读核查。\n\n"
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
