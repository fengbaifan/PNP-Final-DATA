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
GROUP = "archive-group-memmo-elementi-lodoliana-1786"
MEMBERS = ("cand-1414", "cand-1647", "cand-8812")
KU_ID = "units/archives/elementi-architettura-lodoliana"
CARD_REL = "04-knowledge/units/archives/elementi-architettura-lodoliana.md"
NAME_ZH = "《洛多利建筑原理》"
NAME_EN = "Elements of Lodolian Architecture"
ORIGINAL_TITLE = "Elementi dell’architettura lodoliana"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "10", "page": "320", "file": "10_CHP-10_sec_ii.md", "lines": "309",
        "quote": "Our only source for Lodoli’s life is Andrea Memmo’s anonymous Elementi dell’architettura lodoliana, first published in Rome in 1786, but there are many scattered references to him in Venetian learned journalism of the first half of the eighteenth century. See also Petrocchi, 1947.",
        "summary": "第10章注2将 Andrea Memmo 的匿名著作 Elementi dell’architettura lodoliana 记为1786年在罗马首次出版，并称其为 Lodoli 生平的唯一来源，同时提及威尼斯学术刊物中的零散材料和 Petrocchi 1947。",
        "note": "此处将题名、归属和出版年连在同一书内引文中；不是对该书原件的独立查阅。",
    },
    {
        "chapter": "15", "page": "367", "file": "15_CHP-15_sec_ii.md", "lines": "31",
        "quote": "his last year in Rome he published the Elementi dell’Architettura lodoliana",
        "summary": "第15章称 Memmo 在其于罗马的最后一年出版 Elementi，并将其称为首部且唯一一部完整阐述 Lodoli 建筑理论的著作。",
        "note": "“首部且唯一一部完整阐述”是 Haskell 对该书的评价。",
    },
    {
        "chapter": "15", "page": "367", "file": "15_CHP-15_sec_ii.md", "lines": "93",
        "quote": "For some reason Memmo published only the first volume of his Elementi in 1786, and though he completed the whole work before his death the full two-volume edition did not appear until 1834.",
        "summary": "第15章注1区分1786年只出版首卷与1834年才出现的完整两卷本，并称 Memmo 生前已完成全书。",
        "note": "保留首卷初刊与完整两卷本刊行的版本时间差，不将1786年说成完整两卷本出版年。",
    },
    {
        "chapter": "21", "page": "参考书目", "file": "21_CHP-21Bibliography.md", "lines": "797",
        "quote": "[Memnio, Andrea]: Elementi dell’architettura lodoliana, Roma 1786.",
        "summary": "全书参考书目列出题名、罗马和1786年，OCR责任者拼写作 Memnio；第10章注2与第15章正文提供 Memmo 归属和版本语境。",
        "note": "保留书目 OCR 拼写异文，不据此改写责任者或另造一个书目对象。",
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
        "sub_type": "book",
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

**中文：** 本卡登记 Andrea Memmo 的 *{ORIGINAL_TITLE}*。第10章将它称为 Memmo 的匿名著作，记为1786年在罗马首次出版；第15章称其为唯一完整阐述 Carlo Lodoli 建筑理论的著作，并记载 Memmo 只在1786年出版首卷、完整两卷本至1834年才刊行。这里保存 Haskell 对作品及出版过程的叙述，不表示已独立查阅1786年或1834年版本。

**English:** This card records Andrea Memmo’s *{ORIGINAL_TITLE}*. Chapter 10 calls it Memmo’s anonymous work and dates its first publication to Rome in 1786. Chapter 15 describes it as the only complete account of Carlo Lodoli’s architectural theories and says that Memmo published only the first volume in 1786, while the complete two-volume edition did not appear until 1834. This records Haskell’s account; it does not indicate independent consultation of either the 1786 or 1834 edition.

### 书目身份与版本

- **原题名：** *{ORIGINAL_TITLE}*。[第10章 p.320 注2](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)；[第15章 p.367](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)。
- **责任者：** Andrea Memmo；第10章称该书为匿名著作，第15章记 Memmo 出版此书。
- **初刊信息：** 1786年在罗马出版首卷。第10章 p.320 注2与第15章 p.367 注1分别给出初刊年和卷册范围。
- **完整版本：** Haskell称完整两卷本于1834年刊行；第15章 p.367 注1。
- **内容：** Lodoli 建筑理论；“首部且唯一一部完整论述”为 Haskell 的评价，第15章 p.367。

### 跨章引用语境

第9、10、15章分别以 Andrea Memmo 1786 年著作的页码作注释引用；第10章 p.320 注2和第15章 p.367明确给出 *{ORIGINAL_TITLE}* 题名，参考书目亦列出同题名与罗马、1786年。索引候选 `cand-1414`、`cand-1647` 与引用／书目候选 `cand-8812` 因此共指此 archive。参考书目 OCR 将姓氏录作 “Memnio”；本卡保留该转录异文，不据此另立身份。

第15章注1说明1786年出版的是首卷，完整两卷本至1834年才出现。卡内分别记录两个出版节点，不把首卷等同于完整版本。第10章将作品称为“匿名”而同时归于 Memmo；本卡按原书这一并置表述保存，不推断封面或题名页上的责任者形式。

### 身份边界

本卡仅指 *{ORIGINAL_TITLE}* 这部 archive，与 Memmo 为就任 Procuratore 庆典出版的 *Apologhi*（既有 `units/archives/lodoli-apologhi-1787`）分开；被引的 Petrocchi 1947 及其他学术文献亦各为独立 archive。三个 S3 候选 `cand-1414`、`cand-1647`、`cand-8812` 映射至同一 KU；其余同名索引或作者人物不并入。

## 关系与证据

当前没有登记正式关系。S2 中有关 Memmo 出版或引用此书、此书作为 Lodoli 生平材料及其建筑理论内容的7条关系候选留待 S6 逐条核验端点、方向、语境与证据。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Memmo Elementi archive group in S4")
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
        and (NAME_EN.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
             or ORIGINAL_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold())
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
    assert len(direct) == 12 and len(relations) == 7, (len(direct), len(relations))

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
        f"\n\n### S4 archive：Memmo《{NAME_ZH[1:-1]}》跨章身份组登记（{DATE}）\n\n"
        f"- `cand-1414,cand-1647,cand-8812` → `{GROUP}` → `{KU_ID}`；12条直接 S2 断言，7条关系候选留待 S6。"
        "第10章 p.320 注2 将题名、Memmo归属及罗马1786年初刊置于同一说明中；第15章 p.367正文与注1区分首卷和完整两卷本；"
        "第21章参考书目保留 OCR 异文“Memnio”。"
        "卡片只记录 Haskell 对题名、责任者、理论内容及出版沿革的叙述，不声称已独立查阅1786或1834年版本；"
        "不与 Memmo 的《Apologhi》或被引学术文献合并。本次不新增正式关系或进行 S5 外部补足。\n\n"
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
