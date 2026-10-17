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
GROUP = "archive-group-a17b1987a05a"
MEMBERS = ("cand-5658",)
KU_ID = "units/archives/haskell-rinehart-dal-pozzo-collection-1960"
CARD_REL = "04-knowledge/units/archives/haskell-rinehart-dal-pozzo-collection-1960.md"
NAME_ZH = "《达尔·波佐藏品：一些新证据》"
NAME_EN = "The dal Pozzo Collection—Some New Evidence"
ARTICLE_TITLE = "The dal Pozzo collection—some new evidence"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "4", "page": "100", "file": "04_CHP-4_sec_ii.md", "lines": "240",
        "quote": "For the question of dal Pozzo’s portraits and for the most complete inventory of his pictures that has so far come to light see Haskell and Rinehart, i960.",
        "summary": "第4章 p.100 注2以 Haskell 与 Rinehart 的文章作为 dal Pozzo 肖像及其藏画清单的参考。",
        "note": "本卡记录 Haskell 的引文及其所述用途；该文章未独立查阅。",
    },
    {
        "chapter": "4", "page": "103", "file": "04_CHP-4_sec_ii.md", "lines": "250",
        "quote": "1 Mancini, I, p. 263, and Haskell and Rinehart, i960.",
        "summary": "第4章 p.103 注1并列引用 Mancini 与 Haskell、Rinehart 的1960年文章。",
        "note": "本书抽取文本写作 i960；S2 记录图像所示年份为1960。文章未查阅。",
    },
    {
        "chapter": "4", "page": "113", "file": "04_CHP-4_sec_ii.md", "lines": "289",
        "quote": "3 Lumbroso, p. 314, and Haskell and Rinehart, i960...",
        "summary": "第4章 p.113 注3并列引用 Lumbroso 第314页及 Haskell、Rinehart 1960年文章。",
        "note": "OCR 年份写作 i960；S2 注明 scan reading 为1960。文章未查阅。",
    },
    {
        "chapter": "4", "page": "113", "file": "04_CHP-4_sec_ii.md", "lines": "290",
        "quote": "see Haskell and Rinehart, i960. Only a small fraction of it can now be identified.",
        "summary": "第4章 p.113 注4引用 Haskell 与 Rinehart，讨论 Carlo Antonio dal Pozzo 藏画的散佚。",
        "note": "这是 Haskell 对该文章的引用语境，不是本卡对藏画散佚情况的独立验证。",
    },
    {
        "chapter": "4", "page": "未在该 S2 记录中单独标注", "file": "04_CHP-4_sec_ii.md", "lines": "256",
        "quote": "2 Haskell and Rinehart, 1960, but see also p. 100, note 2.",
        "summary": "第4章另一处注释引用 Haskell 与 Rinehart 1960年文章，并回指本书 p.100 注2。",
        "note": "来源行有年份；S2 未给该注释单独打印页定位，保留未标注状态。",
    },
    {
        "chapter": "21", "page": "425", "file": "21_CHP-21Bibliography.md", "lines": "596–597",
        "quote": "Haskell, F. and Rinehart, S.: ‘The dal Pozzo collection—some new evidence’ in Burlington\nMagazine, i960, pp. 318-326.",
        "summary": "第21章书目列 F. Haskell 与 S. Rinehart 合著的文章题名、Burlington Magazine、年份和页码范围。",
        "note": "该条 OCR 写 i960；candidate 记录 S2 对扫描页年份读作1960。文章未独立查阅。",
    },
    {
        "chapter": "21", "page": "未在该 S2 记录中单独标注", "file": "21_CHP-21Bibliography.md", "lines": "1049",
        "quote": "Rinehart, S.: See also Haskell and Rinehart.",
        "summary": "第21章参考书目在 Rinehart 名下交叉指向 Haskell 与 Rinehart 合著条目。",
        "note": "交叉指引帮助识别作者条目，不是另一篇出版物。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        page = item["page"]
        page_part = f"印刷页{page}" if page.startswith("未在") else f"印刷页{page}"
        location = f"第{item['chapter']}章，{page_part}；Markdown 行{item['lines']}"
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
                "source_span": f"lines {item['lines']}" + (f"; print p. {page}" if page.isdigit() else ""),
            },
        })
    return rows


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "journal article",
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

**中文：** 本卡登记 F. Haskell 与 S. Rinehart 合著的文章 *{ARTICLE_TITLE}*。第21章参考书目将其列于 *Burlington Magazine*，1960年，第318–326页；第4章多处引用。卡片只确认本书中的书目身份与引用路径，不表示文章已独立查阅或文章内容已核验。中文题名为忠实的工作译名。

**English:** This card records the article *{ARTICLE_TITLE}* by F. Haskell and S. Rinehart. Chapter 21 lists it in *Burlington Magazine*, 1960, pages 318–326; Chapter 4 cites it in several notes. The card establishes the bibliographic identity and citation path within Haskell’s book only; the article was not independently consulted and its contents were not verified. The Chinese title is a descriptive working translation.

### 书目身份

- **题名：** *{ARTICLE_TITLE}*；第21章参考书目，印刷页425。
- **作者：** F. Haskell、S. Rinehart；按书目缩写照录，不扩写姓名。
- **刊物与范围：** *Burlington Magazine*，1960年，pp.318–326；出版信息来自 Haskell 书目。
- **年份转录：** 部分本书转录行写作 i960；S2 候选记录将扫描页所示读作1960。本卡保留原始 OCR 引文，不把文章年份误写为1960之前或独立核验。

### 身份边界

S3 新组 {GROUP} 仅含 archive 候选 cand-5658，指向该期刊文章，不是 dal Pozzo 的清单原件、藏画集合或相关人物。第4章对该文章的内容概述仍是 Haskell 的转述；未将被引档案及其中肖像、版画等对象并入本 KU。

## 关系与证据

当前没有登记正式关系。6条直接 S2 关系候选留待 S6；其他书目交叉指引和纯引文定位保留为来源记录，不自动成为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Haskell and Rinehart's dal Pozzo article in S4")
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
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and ARTICLE_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    for item in SOURCES:
        source_text = " ".join((ROOT / "02-sources/02-Markdown" / item["file"]).read_text(encoding="utf-8-sig").split())
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
    assert len(direct) == 8 and len(relations) == 6, (len(direct), len(relations))

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
        f"\n\n### S4 archive：Haskell 与 Rinehart 达尔·波佐藏品文章身份组登记（{DATE}）\n\n"
        f"- cand-5658 → {GROUP} → {KU_ID}；第21章 p.425 书目列 F. Haskell、S. Rinehart、文章题名、Burlington Magazine、1960年及 pp.318–326；第4章多处引用。文章本身未独立查阅。\n"
        "- 直接 S2 记录8条，其中6条关系候选留待 S6。书目 OCR 年份写作 i960；S2 候选记录注明扫描页读作1960，卡片保留 OCR 引文并说明该差异。被引库存原件与文章保持分立。\n"
        "- 未新增正式关系、外部身份或 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append

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
