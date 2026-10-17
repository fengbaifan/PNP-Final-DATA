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
DATE = "2026-10-16"
GROUP = "archive-group-zanetti-dactyliotheca-1749"
MEMBERS = ("cand-10012", "cand-2845")
KU_ID = "units/archives/dactyliotheca-ant-m-zanetti-1749"
CARD_REL = "04-knowledge/units/archives/dactyliotheca-ant-m-zanetti-1749.md"
NAME_ZH = "《扎内蒂宝石与奖章图录》"
NAME_EN = "Dactyliotheca Ant. M. Zanetti"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "13", "page": "337", "file": "13_CHP-13_intro.md", "lines": "54–55",
        "quote": "publication a few years earlier of the gems in A. M. Zanetti",
        "summary": "第13章称 Pasquali 的 Dactylografa Smithiana 受到数年前 Albrizzi 关于 Zanetti 宝石收藏的出版物影响；本书 p.344 提供该较早出版物的题名与书目信息。",
        "note": "此处的 Dactylografa Smithiana 是受影响的另一部书，不与被引的 Albrizzi 图录合并。",
    },
    {
        "chapter": "13", "page": "344", "file": "13_CHP-13_intro.md", "lines": "117–118",
        "quote": "Dactyliotheca Ant. M. Zanetti",
        "summary": "第13章将此题名明确用于1749年刊行的 A. M. Zanetti 宝石与奖章收藏图录。",
        "note": "原书题名；不将图录与其中所编目的私人收藏混为一物。",
    },
    {
        "chapter": "13", "page": "344", "file": "13_CHP-13_intro.md", "lines": "117–118",
        "quote": "for which Albrizzi was, after some hesitation, again chosen as publisher",
        "summary": "第13章记 Albrizzi 经一番犹豫后再次被选为出版者。",
    },
    {
        "chapter": "13", "page": "344", "file": "13_CHP-13_intro.md", "lines": "118–119",
        "quote": "Francesco Gori wrote a Latin commentary, but a more general public was kept in mind",
        "summary": "第13章记 Francesco Gori 撰写拉丁文评注，并为更广泛读者提供意大利文译本。",
    },
    {
        "chapter": "13", "page": "344", "file": "13_CHP-13_intro.md", "lines": "119–122",
        "quote": "the magnificent volume, which was published at his own expense",
        "summary": "Haskell 称该书由 Zanetti 自费出版，并将其解释为兼具奢华销售目录目的。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        location = f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}"
        if item.get("note"):
            location += f"；{item['note']}"
        rows.append({
            "citation": BOOK_CITATION,
            "location": location,
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    return rows


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "illustrated catalogue",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 第13章将 *Dactyliotheca Ant. M. Zanetti* 记为1749年出版的图文目录，内容为 A. M. Zanetti 的宝石与奖章收藏，插图由 Zanetti 提供，出版者为 Albrizzi。第337页提到一部更早的 Albrizzi 宝石图录曾影响 Pasquali 的 *Dactylografa Smithiana*；第344页给出了该较早出版物的题名及出版语境。本卡登记书目对象，不是被编目的实体收藏。

**English:** Chapter 13 identifies *Dactyliotheca Ant. M. Zanetti* as an illustrated catalogue published in 1749, describing A. M. Zanetti’s collection of gems and medals, with illustrations provided by Zanetti and Albrizzi as publisher. Page 337 refers to an earlier Albrizzi publication of Zanetti’s gems as an influence on Pasquali’s *Dactylografa Smithiana*; p. 344 supplies the title and publication context of that earlier book. This card records the bibliographic work, not the physical collection it catalogues.

### 名称与版本

| 字段 | 内容 | 依据 |
|---|---|---|
| 原题名 | *Dactyliotheca Ant. M. Zanetti* | [第13章 p.344](../../../02-sources/02-Markdown/13_CHP-13_intro.md)；OCR L117–118 |
| 中文描述性工作题名 | {NAME_ZH} | 根据原题及书内内容所作的识别性译名；非原题 |
| 文献类型 | 图文目录（illustrated catalogue） | 第13章 p.344；所编目为宝石与奖章收藏 |
| 出版年 | 1749年 | 第13章 p.344；原书直接记载 |
| 出版者 | Albrizzi | 第13章 p.344；Haskell称其经犹豫后再次被选为出版者 |

### 本书语境

第13章先谈 Pasquali 于1767年出版的 *Dactylografa Smithiana*，称它受到 Albrizzi 数年前关于 A. M. Zanetti 宝石收藏的出版物影响。随后第344页把较早出版物明确称为 *Dactyliotheca Ant. M. Zanetti*，并记为1749年出版。此处的两部书分属不同出版者与时间，不合并。

Haskell 称 Zanetti 为自己收藏的宝石与奖章目录提供插图；Francesco Gori 撰写拉丁文评注，另提供意大利文译本。书的献辞对象先考虑波兰国王，之后选定瑞典女王；原书并未在此证明最终印本上确实印有该献辞。Haskell 还称 Zanetti 自费出版，并判断该卷册部分意在作为奢华销售目录；后者保留为作者解释。

### 身份边界

中文：本卡仅指1749年 *Dactyliotheca Ant. M. Zanetti* 图录。它与被其影响的 Pasquali《Dactylografa Smithiana》（cand-1848 所在 archive 组）是两部不同出版物；与 Zanetti 的实体宝石、奖章收藏（cand-10113，仍因类型未定而 undecided）也分开。cand-10012 与索引候选 cand-2845 共映射此 archive KU；cand-2845 是该书的索引入口，不是 Zanetti 人物卡。King of Poland 与 Queen of Sweden 的献辞候选仍各自保留，不据“被考虑／选定”写成已印献辞。

English: This card records only the 1749 *Dactyliotheca Ant. M. Zanetti*. It is distinct from Pasquali’s later *Dactylografa Smithiana* (the archive group containing cand-1848) and from Zanetti’s physical collection of gems and medals (cand-10113, still undecided because its type is unresolved). Body candidate cand-10012 and index candidate cand-2845 map to this one archive KU; cand-2845 is an index locator for the book, not a person record for Zanetti. The dedicatee candidates for the King of Poland and Queen of Sweden remain separate; “considered” or “chosen” does not establish a dedication printed in the volume.

## 关系与证据

当前没有登记正式关系。S2 中关于 Zanetti、Albrizzi、Francesco Gori、译本、拟献辞对象及被编目收藏的关系候选留待 S6 按端点、方向、语境和证据逐条核验。Haskell 的销售目录判断按作者解释保留。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the two-candidate 1749 Zanetti Dactyliotheca archive group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
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
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        row = decisions[cid]
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert row.get("decision") == "new" and not row.get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and NAME_EN.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    for item in SOURCES:
        text = " ".join((ROOT / "02-sources" / "02-Markdown" / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, (item["file"], item["quote"])

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
    assert len(direct) == 12 and len(relations) == 10, (len(direct), len(relations))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    process_append = (
        f"\n\n### S4 archive：1749年《Dactyliotheca Ant. M. Zanetti》登记（{DATE}）\n\n"
        f"- `cand-10012,cand-2845` → `{GROUP}` → `{KU_ID}`；12条直接 S2 断言，10条关系候选留待 S6。"
        "第337页对早期 Albrizzi 宝石出版物的回指与第344页给出的 1749 年题名共同确认同一图录；"
        "不与后来的 Pasquali《Dactylografa Smithiana》或被编目的实体收藏合并。"
        "未新增正式关系，未开展 S5 外部补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    result_append = (
        f"\n\n### S4 archive：1749年《Dactyliotheca Ant. M. Zanetti》登记（{DATE}）\n\n"
        f"- cand-10012 与 cand-2845 共映射至[扎内蒂宝石与奖章图录 archive KU](../units/archives/dactyliotheca-ant-m-zanetti-1749.md)。"
        "卡片保留原题、1749年、Albrizzi 出版、Zanetti 插图、Gori 拉丁文评注及意大利文译本，并把目录与实体收藏、"
        "后来的 Dactylografa Smithiana 及未决献辞对象分开。10条关系候选留待 S6，不新增正式关系。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append
    next_result += result_append

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; sources={len(SOURCES)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
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
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; direct_statements={len(direct)}; "
        f"relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
