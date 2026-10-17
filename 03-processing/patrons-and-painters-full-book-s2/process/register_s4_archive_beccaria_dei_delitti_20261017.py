from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "archive-group-47e19ac2f4b5"
MEMBERS = ("cand-9707",)
KU_ID = "units/archives/dei-delitti-e-delle-pene-treatise"
CARD_REL = "04-knowledge/units/archives/dei-delitti-e-delle-pene-treatise.md"
NAME_ZH = "《论犯罪与刑罚》"
NAME_EN = "On Crimes and Punishments"
ORIGINAL_TITLE = "Dei delitti e delle pene"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = (
    {
        "file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章，印刷页318；L136；PDF物理页51",
        "span": "line 136; print p. 318; PDF physical p. 51",
        "quote": "in 1764 Beccaria published his epoch-making Dei delitti e delle pene and was rapturously welcomed in Paris.",
        "summary": "Haskell称Beccaria于1764年出版该论著，并称其在巴黎受到热烈欢迎；“epoch-making”和巴黎接待评价均作为作者陈述保留，不由本卡提升为独立核实事实。",
    },
    {
        "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章，印刷页337；L53；PDF物理页6",
        "span": "line 53; print p. 337; PDF physical p. 6",
        "quote": "he got into trouble with the Inquisitori di Stato for secretly distributing copies of Beccaria’s forbidden Dei delitti e delle pene",
        "summary": "Haskell称Pasquali因秘密散发该书副本而与Inquisitori di Stato发生麻烦；本段记载散发行为，不归为Beccaria本人的行动。",
    },
    {
        "file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
        "location": "第15章，印刷页369；L52；PDF物理页9",
        "span": "line 52; print p. 369; PDF physical p. 9",
        "quote": "In 1764 rumour credited him with being the author of Beccaria’s anonymously published Dei delitti e dette pene.",
        "summary": "Haskell报告1764年有传闻称Querini是匿名发表的该书作者；原文明确是传闻，不构成作者身份裁定。OCR作dette，既有S2据印刷页校为delle。",
    },
)


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "treatise",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p318 = "[第10章 p.318](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L136）"
    p337 = "[第13章 p.337](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L53）"
    p369 = "[第15章 p.369](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L52）"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录Haskell在第10章称为Beccaria作品的论著 *{ORIGINAL_TITLE}*。第13章以Pasquali秘密散发该书副本为语境再提及它；第15章则报告一则将Querini说成作者的传闻，并明确保留传闻性质。此处登记文本层级的文献身份，不指某一版次、实物副本，也不裁定传闻中的作者说法。中文题名为描述性工作译名。{p318} {p337} {p369}

**English:** This card records the treatise *{ORIGINAL_TITLE}*, which Haskell calls a work by Beccaria in Chapter 10. Chapter 13 refers to copies secretly distributed by Pasquali; Chapter 15 reports a rumour crediting Querini with authorship and explicitly presents it as a rumour. This is a text-level archive identity, not a particular edition or copy, and it does not decide the reported authorship claim. The English display title is a descriptive translation. {p318} {p337} {p369}

### 文献身份与版本边界

- **原题名：** *{ORIGINAL_TITLE}*；第15章OCR作 `dette pene`，既有S2据印刷页校为 `delle pene`。本卡保留原始OCR摘录和校正依据，不将其表述为新一轮扫描校勘。{p369}
- **文献类型与粒度：** 论著（treatise）；登记为文本层级身份，不推定具体刊本、版次、出版地或馆藏副本。{p318}
- **书内责任者：** Haskell第10章称Beccaria于1764年出版该书；Beccaria人物入口为[Cesare Beccaria](../persons/cesare-beccaria.md)。此导航不代表S6正式关系已经登记。{p318}
- **责任者传闻：** 第15章将Querini列作匿名出版作者的传闻对象，文本同时明言该说法是传闻；不据此把Querini登记为已确认作者。{p369}
- **显示题名：** 中文“《论犯罪与刑罚》”和英文 “On Crimes and Punishments” 为描述性工作译名；原题名保留意大利语。{p318}

## 关系与证据

当前没有登记正式关系。以下3条S2关系候选仍待S6：Beccaria与该文献的书内出版陈述、Pasquali秘密散发副本、以及Querini作者身份传闻。候选均保留原陈述的说话者和限定，不把叙述、传闻或导航链接改写成已采纳关系。"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Beccaria's treatise as a text-level archive KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    align_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    assert all(candidate_by_id[cid].get("suggested_type") == "archive" for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    card_path = ROOT / CARD_REL
    registered_rows = [
        row for row in manifest
        if row.get("ku_id") == KU_ID and row.get("card_path") == CARD_REL
    ]
    if (
        registered_rows
        and CARD_REL in accepted
        and card_path.exists()
        and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS)
    ):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; {len(MEMBERS)} candidate mapping; 3 relation candidates remain non-formal.")
        return 0
    for cid in MEMBERS:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")

    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and ORIGINAL_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    for item in SOURCES:
        source_text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, (item["file"], item["quote"])

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(direct) == 3 and len(relations) == 3, (len(direct), len(relations))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; text-level archive, no edition inferred."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n### S4 archive：Beccaria《Dei delitti e delle pene》文本身份登记（{DATE}）\n\n"
        f"- `{MEMBERS[0]}`（{GROUP}）登记为[{NAME_ZH}](../../../{CARD_REL})；文献身份为文本层级论著，不指定版本或实物副本。依据第10章p.318的书名与出版陈述、第13章p.337关于Pasquali散发副本的叙述，以及第15章p.369明确标作传闻的Querini作者说。p.369 OCR `dette` 按既有S2对印刷页校为 `delle`。\n"
        "- Beccaria、Pasquali与Querini相关的3条直接关系候选留待S6；未将出版叙述、散发事件或作者传闻转成正式边。书名候选与Beccaria人物候选分别落在archive和person KU。未新增外部版次或馆藏断言。\n\n"
        f"S4当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append
    result_append = (
        f"\n\n### archive：Beccaria 论著文本身份组登记（{DATE}）\n\n"
        f"`{MEMBERS[0]}`登记至[文献卡](../units/archives/dei-delitti-e-delle-pene-treatise.md)。第10、13、15章的题名提及合为一个文本层级archive KU；第15章Querini作者说保留为明确传闻。3条直接关系候选待S6。\n\n"
        f"S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_result += result_append

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; sources={len(SOURCES)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("no files changed")
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", align_fields, planned_alignment)
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
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; direct_statements={len(direct)}; "
        f"relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
