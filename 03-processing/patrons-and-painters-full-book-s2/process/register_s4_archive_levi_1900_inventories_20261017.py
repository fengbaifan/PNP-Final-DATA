from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_archive_memmo_query_sheet_20261017 as previous


sync = previous.sync
ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "archive-group-5b4568c2a1c8"
MEMBERS = ("cand-8533", "cand-11374")
KU_ID = "units/archives/le-collezioni-veneziane-1900"
CARD_REL = "04-knowledge/units/archives/le-collezioni-veneziane-1900.md"
NAME_ZH = "《从十四世纪至今的威尼斯艺术与古物收藏》"
NAME_EN = "Venetian Collections of Art and Antiquities from the Fourteenth Century to the Present"
ORIGINAL_TITLE = "Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
RELATION_IDS = (
    "st-chp9-p261-note2-levi-inventory-collection",
    "st-chp15-p368-note3-cites-levi-volume-ii-p254",
    "st-chp15-p368-note3-inventory-partly-published-in-levi",
    "st-chp15-p370-note1-cites-levi-volume-ii-p255",
    "st-chp15-p370-note1-inventory-published-in-levi",
)
DIRECT_IDS = RELATION_IDS + ("st-chp21-bib-l658-699-entry-25",)
PROCESS_ANCHOR = "s4-levi-1900-publication-20261017"

CH9_QUOTE = (
    "A number of Venetian inventories of the eighteenth century are included in "
    "C. A. Levi’s collection of 1900."
)
CH15_QUOTE_1 = "part of which Is published by Levi, II, p. 254."
CH15_QUOTE_2 = (
    "A very unclassified inventory of Angelo Querini’s effects at Alticchiero "
    "is published by Levi, II, p. 255."
)
CH19_QUOTE = "Archivio di Stato-Petizion 467 by C. A. Levi, II, pp. 236-48."
BIB_QUOTE = (
    "Levi, C. A.: Le Collezioni Veneziane d’arte e d’antichità dal secolo XIV ai nostri giorni,\n"
    "Venezia 1900."
)


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def source_rows():
    return [
        {
            "citation": BOOK_CITATION,
            "location": "第9章，印刷页261，注2；Markdown 行405。",
            "sentence_summary": (
                "Haskell 称18世纪威尼斯的若干库存清单收入 C. A. Levi 于1900年出版的汇编；"
                "他另称其他清单仍未刊行。该描述不表示本卡穷尽相关库存清单。"
            ),
            "original_quotes": [{"source_span": "line 405; print p. 261, note 2", "text": CH9_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "line 405; print p. 261, note 2",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第15章，印刷页368注3、页370注1；Markdown 行99–100、109。",
            "sentence_summary": (
                "两条注释分别将 Memmo 的 Petizion 488 清单部分内容和 Angelo Querini 的 Alticchiero "
                "库存清单指向 Levi 第二卷 p.254、p.255。底层库存清单与出版物是不同文献对象；"
                "两者均未独立查阅。"
            ),
            "original_quotes": [
                {"source_span": "lines 99–100; print p. 368, note 3", "text": CH15_QUOTE_1},
                {"source_span": "line 109; print p. 370, note 1", "text": CH15_QUOTE_2},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "source_span": "lines 99–100 and 109; print pp. 368 and 370",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第19章附录，印刷页391；Markdown 行119。",
            "sentence_summary": (
                "Haskell 称 Smith 宫中藏品清单从威尼斯国家档案馆 Petizion 467 由 C. A. Levi "
                "第二卷 pp.236–248 重刊；原档案清单与其刊本分开。"
            ),
            "original_quotes": [{"source_span": "line 119; print p. 391", "text": CH19_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
                "source_span": "line 119; print p. 391",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第21章书目，印刷页427；Markdown 行691–692。",
            "sentence_summary": (
                "书目列出 C. A. Levi 的意大利文题名与 Venezia 1900 出版信息；"
                "未给出本轮所需的完整卷册范围，相关正文引文明确指向第二卷。"
            ),
            "original_quotes": [{"source_span": "lines 691–692; print p. 427", "text": BIB_QUOTE}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
                "source_span": "lines 691–692; print p. 427",
            },
        },
    ]


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ch9 = "../../../02-sources/02-Markdown/09_CHP-9_intro.md"
    ch15 = "../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md"
    ch19 = "../../../02-sources/02-Markdown/19_CHP-19Appendix.md"
    ch21 = "../../../02-sources/02-Markdown/21_CHP-21Bibliography.md"
    relation_text = "、".join(RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记哈斯克尔第21章书目所列的 C. A. Levi 出版物，原题为 *{ORIGINAL_TITLE}*，书目给出 Venezia 1900。第9章称，18世纪威尼斯的若干库存清单收录在 Levi 的1900年汇编中；第15章两条注释引用其第二卷 p.254、p.255；第19章附录引用第二卷 pp.236–248。题名、年份和卷次将这些章内引文与第21章的完整书目记录对应起来。出版物及被引页未独立查阅，所有内容仍为 Haskell 的书内报告。[第9章 p. 261](../../../02-sources/02-Markdown/09_CHP-9_intro.md)（L405）；[第15章 pp. 368、370](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L99–100、109）；[第19章 p. 391](../../../02-sources/02-Markdown/19_CHP-19Appendix.md)（L119）；[第21章 p. 427](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md)（L691–692）。

**English:** This card records the C. A. Levi publication listed in Haskell’s chapter 21 bibliography under the Italian title *{ORIGINAL_TITLE}*, with Venezia 1900 as its publication information. Chapter 9 says that a number of eighteenth-century Venetian inventories are included in Levi’s 1900 collection; two chapter 15 notes cite volume II, pages 254 and 255; and the chapter 19 appendix cites volume II, pages 236–248. The title, year, and volume references connect these chapter citations with the full chapter 21 bibliographic entry. The publication and cited pages were not independently consulted; the contents remain Haskell’s reports. [Chapter 9, p. 261](../../../02-sources/02-Markdown/09_CHP-9_intro.md) (L405); [chapter 15, pp. 368 and 370](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md) (L99–100, 109); [chapter 19, p. 391](../../../02-sources/02-Markdown/19_CHP-19Appendix.md) (L119); [chapter 21, p. 427](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md) (L691–692).

### 题名、版本与范围

- **原题名：** *{ORIGINAL_TITLE}*，见[第21章 p. 427]({ch21})（L691–692）。
- **工作译名：** {NAME_ZH}；英文展示译名为 {NAME_EN}。二者为便于识别的描述性译名，不声称是该书的原载题名。
- **出版信息：** Venezia 1900。Haskell 正文所引页码分布于第二卷 p.254、p.255、pp.236–248；总卷数及实物版本未独立核验。
- **内容范围：** Haskell 仅称该出版物收入“若干”18世纪威尼斯库存清单；本卡不作为该类清单的穷尽目录。
- **责任者形式：** 书目写作 C. A. Levi；本轮不扩写 initials，也不据出版物身份推定相应人物候选的完整身份。

### 身份边界

S3 身份组 archive-group-5b4568c2a1c8 包含 cand-8533 与 cand-11374，现共同映射至本卡。cand-8533 的章节引文与 cand-11374 的书目全题名原分属两个 new 组；第9、15、19、21章的1900年信息、题名和第二卷页码支持它们指向同一出版物。两条候选的原分组及更正依据均保留在 alignment 记录。

本卡指 Levi 的出版物，不与被刊清单的原档案对象合并：Smith 宫藏清单 Petizion 467（cand-10806）、Memmo 的 Petizion 488 财物清单、Angelo Querini 的 Alticchiero 库存清单（cand-10567）及未具名库存清单群（cand-8531）均保持独立。C. A. Levi 人物候选 cand-8532 仍待证；Vol. I 短引 cand-10659 与 cand-10732 的出版物身份仍 undecided，不并入本卡。

## 关系与证据

当前未登记正式关系。直接 S2 关系候选 {relation_text} 均留待 S6 核对端点、方向、语境与证据。第21章书目陈述用于识别出版物，不构成新增关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Levi’s 1900 Venetian collections publication in S4")
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
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert set(MEMBERS) <= set(candidate_by_id)
    group_members = {
        cid for cid, row in decision_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decision_by_id[cid].get("decision") == "new" and not decision_by_id[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and ORIGINAL_TITLE.casefold() in " ".join(row.values()).casefold()
        for row in manifest
    )

    source_checks = (
        ("02-sources/02-Markdown/09_CHP-9_intro.md", CH9_QUOTE),
        ("02-sources/02-Markdown/15_CHP-15_sec_ii.md", CH15_QUOTE_1),
        ("02-sources/02-Markdown/15_CHP-15_sec_ii.md", CH15_QUOTE_2),
        ("02-sources/02-Markdown/19_CHP-19Appendix.md", CH19_QUOTE),
        ("02-sources/02-Markdown/21_CHP-21Bibliography.md", BIB_QUOTE),
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
    assert {row["statement_id"] for row in direct} == set(DIRECT_IDS)
    assert {row["statement_id"] for row in relations} == set(RELATION_IDS)

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
    next_process = previous.refresh_process_type_table(process_text, stats)
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S4 archive：Levi 1900 年《威尼斯艺术与古物收藏》登记（{DATE}）\n\n"
        f"- cand-8533 与 cand-11374 保持同一 S3 new 组 {GROUP}，共同映射至"
        f"[{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）。书目原题为 {ORIGINAL_TITLE}，"
        "第21章列 Venezia 1900；中文与英文展示题名均为描述性工作译名。\n"
        "- 第9章称该1900年出版物收入若干18世纪威尼斯库存清单；第15章引其第二卷 p.254、p.255，"
        "第19章引第二卷 pp.236–248。正文卷页定位与书目题名、年份支持跨章身份并组；出版物及被引页未独立查阅。\n"
        f"- 共{len(direct)}条直接 S2 陈述，其中{len(relations)}条关系候选（{', '.join(RELATION_IDS)}）全部留待 S6。"
        "原档案清单、未具名库存清单群、C. A. Levi 人物与卷I短引保持独立；本批未新增正式关系、外部身份验证或 S5 enrichment。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
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
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
        f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
