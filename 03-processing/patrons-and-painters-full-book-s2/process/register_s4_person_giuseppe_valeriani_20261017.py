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
GROUP = "new-person:giuseppe-valeriani-196d624a19"
MEMBERS = ("cand-9382",)
KU_ID = "units/persons/giuseppe-valeriani"
CARD_REL = "04-knowledge/units/persons/giuseppe-valeriani.md"
NAME_ZH = "朱塞佩·瓦莱里亚尼"
NAME_EN = "Giuseppe Valeriani"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
SOURCE_P289 = "02-sources/02-Markdown/10_CHP-10_intro_notes_p289_visual-transcription.md"
SOURCE_P406 = "02-sources/02-Markdown/20_CHP-20Postscript.md"
PROCESS_ANCHOR = "s4-person-giuseppe-valeriani-crosschapter-20261017"
RELATION_IDS = (
    "st-chp10-p289-note1-row03-artist2",
    "st-chp10-p289-note1-row04-artist2",
    "st-chp20-p406-russian-court-valeriani-book",
)
QUOTE_CAPTION = "The Venetian artists concerned in the enterprise were:"
QUOTE_P289_WILLIAM = (
    "| Domenico Valeriani; Giuseppe Valeriani; Cimaroli; Balestra | "
    "William III | Duke of Kent |"
)
QUOTE_P289_NEWTON = (
    "| Domenico Valeriani; Giuseppe Valeriani; Pittoni | "
    "Isaac Newton | Fitzwilliam Museum |"
)
QUOTE_P406 = (
    "The interest of the eighteenth-century Russian court in attracting artists from Venice "
    "was investigated in a fully documented book about Giuseppe Valeriani in 1948,7 and two "
    "further articles have been devoted to the topic in recent years."
)


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def sources():
    return [
        {
            "citation": BOOK_CITATION,
            "location": "第10章，印刷页289，注1表；项目视觉转录 L2、L7–8；PDF物理页18。",
            "sentence_summary": (
                "Haskell注1的表格说明下列为参与相关纪念碑项目的威尼斯艺术家；"
                "项目视觉转录在 William III 与 Isaac Newton 两行均列 Giuseppe Valeriani。"
                "行列位置支持书内关联，但没有说明他个人的创作、执行或委托角色。"
            ),
            "original_quotes": [
                {"source_span": "line 2; print p. 289, note 1", "text": QUOTE_CAPTION},
                {"source_span": "line 7; print p. 289, note 1", "text": QUOTE_P289_WILLIAM},
                {"source_span": "line 8; print p. 289, note 1", "text": QUOTE_P289_NEWTON},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_P289,
                "source_span": "lines 2, 7–8; print p. 289, note 1; PDF physical p. 18",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第20章后记，印刷页406；Markdown L157；PDF物理页15。",
            "sentence_summary": (
                "Haskell称一部1948年、资料详尽的 Giuseppe Valeriani 著作研究了18世纪俄罗斯宫廷"
                "吸引威尼斯艺术家的兴趣，并提及此后另有两篇相关论文；该书和论文未独立查阅。"
            ),
            "original_quotes": [{"source_span": "line 157; print p. 406", "text": QUOTE_P406}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_P406,
                "source_span": "line 157; print p. 406; PDF physical p. 15",
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
    p289 = f"[第10章 p.289 注1](../../../{SOURCE_P289})（L2、L7–8）"
    p406 = f"[第20章 p.406](../../../{SOURCE_P406})（L157）"
    relation_list = "\n".join(f"- {statement_id}" for statement_id in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记书内以全名 Giuseppe Valeriani 提及的人物，中文名采用项目工作音译。第10章注1表将他列在“参与相关纪念碑项目的威尼斯艺术家”栏，分别出现在 William III 与 Isaac Newton 两行；表格未界定其个人的创作、执行或委托角色。第20章后记称一部1948年资料详尽的 Giuseppe Valeriani 著作研究了18世纪俄罗斯宫廷吸引威尼斯艺术家的兴趣，并提及两篇后续论文。以上为 Haskell 的书内报告；所述著作和论文未独立查阅，也未作外部人物身份核验。{p289}；{p406}

**English:** This card records the person named Giuseppe Valeriani in the book; the Chinese name is a project transliteration. Chapter 10, note 1, lists him in the column for Venetian artists concerned in the monument enterprise, on the rows for William III and Isaac Newton. The table does not define his individual role in creating, executing, or commissioning either monument. The chapter 20 postscript says that a fully documented 1948 book about Giuseppe Valeriani investigated the eighteenth-century Russian court’s interest in attracting artists from Venice, and mentions two later articles. These are Haskell’s reports; the book and articles have not been independently consulted, and the person’s identity has not been externally verified. {p289}; {p406}

### 姓名与身份范围

- **书内全名：** Giuseppe Valeriani。{p289}；{p406}
- **中文工作音译：** {NAME_ZH}，仅作项目展示名，不作为原语姓名或独立身份依据。
- **身份范围：** 本卡对应候选 cand-9382 的单一 S3 new 身份组。第10章表格中的两次出现与第20章的全名相同；本卡保留书内人物身份，不补充外部生平。

### 本书相关内容

- 第10章注1表的标题说明所列为“参与相关项目的威尼斯艺术家”。项目视觉转录在 William III 与 Isaac Newton 两行均列 Giuseppe Valeriani。表格没有说明个人贡献的具体性质；两行各自指向的纪念碑候选 cand-9387、cand-9375 仍为 S3 undecided，本卡不据此登记作品关系。{p289}
- 第20章后记称一部1948年出版、资料详尽的 Giuseppe Valeriani 著作研究俄罗斯宫廷对威尼斯艺术家的兴趣。该段没有列书名；候选 cand-11088 为单独的 archive 身份组，仍待 S4 登记，相关书籍未独立查阅。{p406}
- 身份边界：索引合并标题“Valeriani, Domenico and Giuseppe”候选 cand-2679 已裁为 excluded，因为它不是一位人物；Domenico Valeriani 候选 cand-9381 与本卡人物分别保留，不合并。以上不将两位同姓者推作同一人。

## 关系与证据

当前没有正式关系记录。下列直接 S2 关系候选均留待 S6 核对端点、方向、语境和证据：

{relation_list}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Giuseppe Valeriani's cross-chapter S4 person group")
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
    assert decisions["cand-2679"].get("decision") == "excluded"
    assert decisions["cand-9381"].get("decision") == "new"
    assert decisions["cand-9375"].get("decision") == "undecided"
    assert decisions["cand-9387"].get("decision") == "undecided"
    assert decisions["cand-11088"].get("decision") == "new"

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

    source_checks = (
        (SOURCE_P289, QUOTE_CAPTION),
        (SOURCE_P289, QUOTE_P289_WILLIAM),
        (SOURCE_P289, QUOTE_P289_NEWTON),
        (SOURCE_P406, QUOTE_P406),
    )
    for relative, quote in source_checks:
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
            "same source-local full name in chapter 10 and chapter 20; no external identity verification."
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
        f"### S4 person：Giuseppe Valeriani 跨章身份组登记（{DATE}）\n\n"
        f"- cand-9382 保持 S3 new 组 {GROUP}，映射至[{NAME_ZH}（{NAME_EN}）人物卡](../../../{CARD_REL})（{KU_ID}）。"
        "第10章 p.289 注1表和第20章 p.406 后记均以同一全名指名；候选组按现有 S3 身份决定登记，不作外部人物核验。\n"
        "- 第10章表格把他列为参与相关纪念碑项目的威尼斯艺术家，在 William III、Isaac Newton 两行出现；"
        "没有说明其个人创作、执行或委托角色。第20章称1948年有一部关于 Giuseppe Valeriani 的资料详尽著作研究俄国宫廷对威尼斯艺术家的兴趣；"
        "该书未独立查阅。\n"
        "- 3 条直接关系候选（{', '.join(RELATION_IDS)}）全部留待 S6。索引合并候选 cand-2679 维持 excluded；"
        "Domenico Valeriani cand-9381 为独立 new 人物组；William III、Isaac Newton 纪念碑候选 cand-9387、cand-9375 维持 undecided；"
        "相关1948年著作 cand-11088 为独立 archive new 组，待 S4。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"
    next_result += (
        f"\n\n### person：Giuseppe Valeriani 跨章身份组 S4 登记（{DATE}）\n\n"
        f"cand-9382 登记至[人物卡](../units/persons/giuseppe-valeriani.md)。第10章 p.289 与第20章 p.406 "
        "均以全名指名；不推断其在两件纪念碑中的个人角色，1948年著作未独立查阅。3条直接关系候选待 S6。"
        "Domenico Valeriani 保持独立；合并索引标题维持 excluded，两个纪念碑端点及1948年著作各保留原 S3 决定。\n\n"
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
