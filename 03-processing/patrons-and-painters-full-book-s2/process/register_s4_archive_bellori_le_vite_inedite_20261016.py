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
GROUP = "archive-group-ce7b481807cb"
MEMBERS = ("cand-4831",)
KU_ID = "units/archives/le-vite-inedite-bellori-piacentini-1942"
CARD_REL = "04-knowledge/units/archives/le-vite-inedite-bellori-piacentini-1942.md"
NAME_ZH = "《未刊传记：圭多·雷尼、安德烈亚·萨基、卡洛·马拉塔》"
NAME_EN = "Unpublished Lives of Guido Reni, Andrea Sacchi, and Carlo Maratta"
ORIGINAL_TITLE = "Le Vite inedite (Guido Reni, Andrea Sacchi, Carlo Maratta)"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "21", "page": "参考书目", "file": "21_CHP-21Bibliography.md", "lines": "138",
        "quote": "Bellori, G. P.: Le Vite inedite (Guido Reni, Andrea Sacchi, Carlo Maratta)—edizione a cura di M. Piacentini, Roma 1942.",
        "summary": "全书参考书目列 Bellori 的 Le Vite inedite（Guido Reni、Andrea Sacchi、Carlo Maratta），由 M. Piacentini 编，出版地 Roma、出版年1942；当前参考书目源片段未标出印刷页。",
        "note": "此处译名《未刊传记》为工作译名，原题及编辑者照录。",
    },
    {
        "chapter": "7", "page": "189", "file": "07_CHP-7_sec_i.md", "lines": "371",
        "quote": "3 Montaiglon, I, p. 104, and Bellori, 1942, pp. 101 and 126.",
        "summary": "第7章注3并列引用 Montaiglon 与 Bellori 1942年版第101、126页；只记录 Haskell 的引用位置，不声称已阅读 Bellori 原书。",
        "note": "引文中的页码属于 Bellori 版本，不是 Haskell 本书页码。",
    },
    {
        "chapter": "1", "page": "10", "file": "01_CHP-1_sec_ii.md", "lines": "183",
        "quote": "4 Luzio, p. 292. 5 Bellori, 1942, p. 117.",
        "summary": "第1章注5引用 Bellori 1942年版第117页；Haskell 本书 p.10 注5。",
        "note": "引用页码属于 Bellori 版本；本条用于确认该版在全书中的引用语境。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        page = f"印刷页{item['page']}" if item["chapter"] != "21" else item["page"]
        location = f"第{item['chapter']}章，{page}；OCR L{item['lines']}"
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
                "source_span": (
                    f"lines {item['lines']}; print page not marked in source excerpt"
                    if item["chapter"] == "21"
                    else f"lines {item['lines']}; print p. {item['page']}"
                ),
            },
        })
    return rows


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "edited edition",
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

**中文：** 本卡登记 Giovanni Pietro Bellori 的 *{ORIGINAL_TITLE}*，即 M. Piacentini 编、1942年于罗马出版的版本。Haskell 第1、2、6、7章注释多次引用该版不同页码；这只证明该版本是本书引用的文献对象，不表示已独立查阅 Bellori 原书或验证这些引文。中文名《未刊传记》为工作译名。

**English:** This card records Giovanni Pietro Bellori’s *{ORIGINAL_TITLE}*, the edition edited by M. Piacentini and published in Rome in 1942. Notes in Chapters 1, 2, 6, and 7 cite different pages of this edition. Those citations identify the bibliographic object referenced by Haskell; they do not indicate independent consultation of Bellori’s book or verification of the cited passages. The Chinese title 《未刊传记》 is a descriptive working translation.

### 书目身份

- **原题名：** *{ORIGINAL_TITLE}*；Haskell 第21章参考书目 OCR L138。
- **责任者／编辑者：** Bellori, G. P.；M. Piacentini 编；第21章参考书目。
- **出版信息：** Roma，1942；第21章参考书目。
- **对象范围：** 题名括号列出 Guido Reni、Andrea Sacchi、Carlo Maratta 三篇传记；本卡记录 Piacentini 编订的1942年出版物，不将 Bellori 本人、被传记画家或其他 Bellori 著作并入。

### 全书引用

第1章注5 引用 Bellori 1942年版第117页；第2章注释引用第47、255页等；第2章第七节注释引用第84、85页；第6章注释引用第107、108页；第7章 pp.189、191 的注释引用第101、126、117、121页。上述页码均属于被引的 Bellori 版本；其原文未在本次登记中独立查阅。第21章参考书目给出完整题名、编者、出版地与年份。

### 身份边界

S3 候选 `cand-4831` 指向这一个 archive 组。此书与 Bellori 人物 KU `units/persons/giovanni-pietro-bellori` 分开；亦与 Bellori 的其他著作、Haskell 正文中所述的委托和作品分开。当前来源未提供出版者或外部馆藏标识，不补造此类字段。

## 关系与证据

当前没有登记正式关系。S2 中九条有关 Haskell 引用 Bellori 1942年版的关系候选留待 S6 核对其各自端点、引用方向、页码语境与证据范围。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Bellori's 1942 Le Vite inedite archive in S4")
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
        and ORIGINAL_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(direct) == 14 and len(relations) == 9, (len(direct), len(relations))

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
        f"\n\n### S4 archive：Bellori《{NAME_ZH[1:-1]}》1942年版身份组登记（{DATE}）\n\n"
        f"- `cand-4831` → `{GROUP}` → `{KU_ID}`；14条直接 S2 断言，其中9条引用关系候选留待 S6。"
        "第21章参考书目 OCR L138 明列题名、Piacentini 编、Roma 1942；第1、7章注释提供该版在本书中的引用位置。"
        "本卡记录 Haskell 所引书目对象，不声称阅读 Bellori 原书；人物 Bellori KU 与该 archive 分开。"
        "本次不新增正式关系或进行 S5 外部补足。\n\n"
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
