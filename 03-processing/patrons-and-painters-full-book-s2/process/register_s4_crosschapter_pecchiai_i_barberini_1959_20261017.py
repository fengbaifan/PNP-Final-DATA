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
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "archive-group-pecchiai-i-barberini-1959"
KU_ID = "units/archives/pecchiai-i-barberini-1959"
CARD_REL = "04-knowledge/units/archives/pecchiai-i-barberini-1959.md"
NAME_ZH = "《巴贝里尼家族》"
NAME_EN = "The Barberini Family"
ANCHOR = "s4-crosschapter-pecchiai-i-barberini-1959-20261017"
MEMBERS = ("cand-4239", "cand-4575")
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "file": "02-sources/02-Markdown/02_CHP-2_intro.md",
        "location": "第2章开篇注1，印刷页24；OCR L7",
        "span": "OCR line 7; printed page 24",
        "quote": "1 For the Barberini and Urban VIII in particular see, unless otherwise indicated, Pastor, XIII, and Pecchiai, 1959.",
        "summary": "Haskell将Pecchiai 1959列为有关巴贝里尼与乌尔班八世的总体参考；此注未给书名或引用页码，书名由第21章书目对应。",
    },
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
        "location": "第2章注3，印刷页41；OCR L187；PDF物理页26",
        "span": "OCR line 187; printed page 41; PDF physical page 26",
        "quote": "3 Pecchiai, 1959, pp. 130 ff.",
        "summary": "Haskell在脚注中将Pecchiai 1959的第130页及后续页作为书目定位；所引页未独立查阅。",
    },
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
        "location": "第2章注2，印刷页47；OCR L206；PDF物理页32",
        "span": "OCR line 206; printed page 47; PDF physical page 32",
        "quote": "2 The documents published by Pecchiai (1959, pp. 161 ff.) effectively dispose of Pastor’s claim (XIII, p. 263) that Taddeo ‘brillava per la purezza di costumi . . .'.",
        "summary": "Haskell称Pecchiai 1959第161页及后续页所刊文件足以反驳Pastor关于Taddeo道德操守的说法；这是哈斯克尔对所引材料的评价，本项目未查读该书或独立解决此争论。",
    },
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md",
        "location": "第2章注1，印刷页54；OCR L232；PDF物理页39",
        "span": "OCR line 232; printed page 54; PDF physical page 39",
        "quote": "1 Apart from Pastor and Pecchiai, 1959, see the report of the Venetian ambassador Angelo Contarini, 1627-9, published by Barozzi e Berchet, I, p. 257.",
        "summary": "Haskell在另一条脚注中将Pecchiai 1959与Pastor、威尼斯使节报告并列为参考；该定位不提供额外版本信息。",
    },
    {
        "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "location": "第21章书目，印刷页433；OCR L940",
        "span": "OCR line 940; printed page 433",
        "quote": "Pecchiai, P.: I Barberini, Roma 1959.",
        "summary": "书目将作者著录为Pecchiai, P.，题名I Barberini，出版项Roma 1959；出版物本身未独立查阅。",
    },
)


def make_card() -> str:
    source_entries = [
        {
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        }
        for item in SOURCES
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": source_entries,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p24 = "[第2章开篇注1 p.24](../../../02-sources/02-Markdown/02_CHP-2_intro.md#L7)"
    p41 = "[第2章注3 p.41](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md#L187)"
    p47 = "[第2章注2 p.47](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md#L206)"
    p54 = "[第2章注1 p.54](../../../02-sources/02-Markdown/02_CHP-2_sec_iv.md#L232)"
    bib = "[第21章书目 p.433](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L940)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔书目所列P. Pecchiai著 *I Barberini*（Roma 1959）。第2章在开篇及后续脚注多次引用该书，涉及巴贝里尼与乌尔班八世的一般参考，以及Pecchiai所刊文件。第47页脚注称这些文件足以反驳Pastor关于Taddeo道德操守的说法；这是哈斯克尔对所引材料的评价，本项目未查读该书或独立判断争论。中文和英文展示题名为工作译名。{p24}；{p41}；{p47}；{p54}；{bib}

**English:** This card records P. Pecchiai’s *I Barberini* (Rome, 1959), as listed in Haskell’s bibliography. Chapter 2 cites the book several times, both as a general reference on the Barberini and Urban VIII and for documents published by Pecchiai. A note on page 47 says those documents effectively dispose of Pastor’s claim about Taddeo’s moral character. That is Haskell’s assessment of the cited material; the book has not been read here and the dispute has not been independently adjudicated. The Chinese and English display titles are working translations. {p24}; {p41}; {p47}; {p54}; {bib}

### 题名与书目著录

- **原题名：** *I Barberini*。
- **中文工作译名：** 《巴贝里尼家族》；不声称为正式中文题名。
- **英文工作译名：** *The Barberini Family*；不声称为正式英文题名。
- **作者著录：** `Pecchiai, P.`（依第21章书目原样保留）；人物候选`cand-4238`因仅有姓氏与首字母仍为S3未决，不据此扩展全名或建立作者关系。
- **文献类型：** 书籍；题名语言为意大利语。
- **出版项：** Roma，1959（书目原文）；出版者未见于该条目。
- **哈斯克尔书内定位：** 第2章注1引用作巴贝里尼与乌尔班八世的一般参考；另见第130页及后续页、第161页及后续页的定位。此处为哈斯克尔的引文页码，不表示本项目已读该书相应页。
- **阅读状态：** 已核对哈斯克尔的引文及其第21章书目著录；Pecchiai著作及其所刊文件均未独立查阅。

## 关系与证据

当前没有正式关系。`st-chp2-intro-l6-7-pecchiai-citation`保留哈斯克尔的书目引用；`st-chp2-seciv-l190-245-taddeo-moral-claim-disputed`保留其对Pastor与所引文件之间争议的评价，留待S6审查。关于Taddeo的说法仍是哈斯克尔转述的来源冲突，不在本卡转为独立核实结论。
"""


def insert_accepted(text: str) -> str:
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
    parser = argparse.ArgumentParser(description="Merge cross-chapter Pecchiai references into one S3 archive group and register one KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert len(decisions) == len(candidate_by_id)
    assert decisions["cand-4238"].get("decision") == "undecided" and not decisions["cand-4238"].get("ku_id")

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    old_groups: dict[str, str] = {}
    for cid in MEMBERS:
        row = decisions[cid]
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row.get("decision"), row.get("ku_id"))
        old_group = sync.get_group(row.get("resolution_note", ""))
        assert old_group and old_group != GROUP
        old_groups[cid] = old_group

    # Merge only after the source bibliography and all cross-chapter citation anchors have been checked.
    for cid in MEMBERS:
        row = planned_by_id[cid]
        row["resolution_note"] = row["resolution_note"].replace(
            f"group={old_groups[cid]}", f"group={GROUP}", 1
        )
        row["resolution_note"] += (
            f" S3 cross-chapter reconciliation ({DATE}): merged prior group {old_groups[cid]} into {GROUP}; "
            "both candidates cite the same bibliographic identity Pecchiai, P., I Barberini, Roma 1959."
        )
        row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        row["ku_id"] = KU_ID

    group_members = {
        row["candidate_id"]
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and NAME_EN.casefold() == row.get("name_en", "").casefold()
        for row in manifest
    )

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_4239 = {
        row["statement_id"] for row in statements
        if row.get("subject_candidate_id") == "cand-4239" or row.get("object_candidate_id") == "cand-4239"
    }
    direct_4575 = {
        row["statement_id"] for row in statements
        if row.get("subject_candidate_id") == "cand-4575" or row.get("object_candidate_id") == "cand-4575"
    }
    assert direct_4239 == {"st-chp2-intro-l6-7-pecchiai-citation"}
    assert direct_4575 == {
        "st-chp2-secii-l147-193-cite-pecchiai1959-p130ff",
        "st-chp2-seciv-l190-245-citation-20",
        "st-chp2-seciv-l190-245-citation-50",
        "st-chp2-seciv-l190-245-taddeo-moral-claim-disputed",
        "st-chp21-bib-l928-983-entry-09",
    }

    for source in SOURCES:
        text = " ".join((ROOT / source["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(source["quote"].split()) in text, source["file"]

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS.read_text(encoding="utf-8-sig").rstrip()
    process_append = f"""

<a id="{ANCHOR}"></a>

### S3跨章合组与S4登记：Pecchiai《I Barberini》（{DATE}）

`cand-4239`与`cand-4575`此前分别处于`{old_groups['cand-4239']}`和`{old_groups['cand-4575']}`两个单成员archive新组。逐条核对后合并为`{GROUP}`：第2章开篇注1以`Pecchiai, 1959`作总体书目指引；第2章p.41注3引第130页及后续页；第2章p.47注2引第161页及后续页并报告Pecchiai所刊文件与Pastor说法的冲突；第2章p.54注1再次引用该书；第21章p.433完整列出`Pecchiai, P.: I Barberini, Roma 1959`。题名、责任者缩写、出版地与年份一致，支持两候选属于同一书目身份。

两候选映射至唯一[《巴贝里尼家族》archive KU](../../../{CARD_REL})。`cand-4238`所指作者人物仅有姓氏和首字母，S3仍为`undecided`；卡内保留书目署名，不扩展姓名或创建作者正式关系。Pecchiai所刊文件与Pastor关于Taddeo道德操守的冲突仅按Haskell原话保留，书和所引页未独立查阅；2条关系候选留待S6。没有新增S5补足。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = process_text + process_append
    result_append = f"""

### S3/S4 archive：Pecchiai《I Barberini》跨章同一身份组（{DATE}）

`cand-4239`与`cand-4575`依据第2章多处书内引用及第21章书目统一为一个新archive组并登记一张卡；作者人物`cand-4238`仍因缩写不足待证。Haskell转述的文献冲突不作独立裁决，关系候选留待S6。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    accepted_next = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"dry-run passed: {', '.join(MEMBERS)} -> one group {GROUP} -> {KU_ID}")
        print(
            f"verified_source_entries={len(SOURCES)}; direct_statements={len(direct_4239)+len(direct_4575)}; "
            "relation_candidates_pending=2; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("cand-4238 remains undecided; cited claims remain for S6; no external facts added")
        print("no files changed")
        return 0

    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_next, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: group={GROUP}; candidates={len(MEMBERS)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
