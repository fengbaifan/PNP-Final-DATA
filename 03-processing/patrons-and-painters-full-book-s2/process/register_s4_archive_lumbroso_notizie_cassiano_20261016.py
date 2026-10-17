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
GROUP = "archive-group-01f343df099c"
MEMBERS = ("cand-5683",)
KU_ID = "units/archives/lumbroso-notizie-cassiano-dal-pozzo-1874"
CARD_REL = "04-knowledge/units/archives/lumbroso-notizie-cassiano-dal-pozzo-1874.md"
NAME_ZH = "《卡西亚诺·达尔·波佐生平札记》"
NAME_EN = "Notes on the Life of Cassiano dal Pozzo"
ORIGINAL_TITLE = "Notizie sulla vita di Cassiano dal Pozzo"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "4", "page": "101", "file": "04_CHP-4_sec_ii.md", "lines": "242",
        "quote": "1 Lumbroso, pp. 176, 179, 197, 251, 299; Bottari, I, p. 369; Peiresc, IV, p. 525.",
        "summary": "第4章 p.101 注1引用 Lumbroso 多页，并将其与 Bottari、Peiresc 的相关引文并列；原书题名和出版信息见第21章参考书目。",
        "note": "此处列的是被引 Lumbroso 版本的页码，不是 Haskell 本书页码。",
    },
    {
        "chapter": "7", "page": "177", "file": "07_CHP-7_sec_i.md", "lines": "322",
        "quote": "4 Lumbroso, p. 369",
        "summary": "第7章 p.177 注4引用 Lumbroso 第369页。",
        "note": "仅记录 Haskell 的引用位置，不表示已阅读该被引页。",
    },
    {
        "chapter": "21", "page": "428", "file": "21_CHP-21Bibliography.md", "lines": "721",
        "quote": "Lumbroso, G.: Notizie sulla vita di Cassiano dal Pozzo, Torino 1874.",
        "summary": "第21章参考书目列 G. Lumbroso、题名、Torino 与1874年；印刷页428。",
        "note": "据书目记录本身登记，不据此声称查阅外部目录或原书。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        if item["chapter"] == "21":
            location = f"第21章，参考书目，印刷页{item['page']}；OCR L{item['lines']}"
            source_span = f"lines {item['lines']}; print p. {item['page']}"
        else:
            location = f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}"
            source_span = f"lines {item['lines']}; print p. {item['page']}"
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
                "source_span": source_span,
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

**中文：** 本卡登记 G. Lumbroso 的 *{ORIGINAL_TITLE}*，即1874年在 Torino 出版的文献。Haskell 第4章多条注释引用其不同页码，第7章 p.177 注4亦引用第369页；第21章参考书目列出完整题名、责任者、Torino 与1874年。卡片仅标识 Haskell 引用的书目对象，不表示已独立查阅 Lumbroso 原书或验证引文内容。中文名《卡西亚诺·达尔·波佐生平札记》为描述性工作译名。

**English:** This card records G. Lumbroso’s *{ORIGINAL_TITLE}*, published in Torino in 1874. Several notes in Chapter 4 cite different pages, and Chapter 7, p. 177, note 4 cites p. 369. Chapter 21’s bibliography supplies the full title, author, place, and year. The card identifies the bibliographic work cited by Haskell; it does not indicate independent consultation of Lumbroso’s book or verification of the cited passages. The Chinese title is a descriptive working translation.

### 书目身份

- **原题名：** *{ORIGINAL_TITLE}*；第21章参考书目 p.428。
- **责任者：** G. Lumbroso；照录参考书目形式。
- **出版信息：** Torino，1874年；第21章参考书目 p.428。
- **引文语境：** Haskell 在第4章 p.101 注1列 Lumbroso pp.176、179、197、251、299；同章还引 pp.167、185、202、211、314 等；第7章 p.177 注4引 p.369。被引页未在本次登记中独立查阅。

### 身份边界

S3 新组 `archive-group-01f343df099c` 仅含 `cand-5683`，指向此1874年书目对象。Cassiano dal Pozzo 人物 KU 保持独立。相邻的 `cand-5648`（1617年8月27日信件）、`cand-5649`（p.137 的 Lumbroso 引用）、`cand-5643`（“passim”引文）和 `cand-5462`（p.195 引文）未并入本组；它们各自现有 S3 `undecided` 决定及身份/粒度疑点继续保留，不因作者姓氏或存在本书书目记录而自动映射。

## 关系与证据

当前没有登记正式关系。S2 中九条 Haskell 引用该书的关系候选留待 S6 逐条核验端点、引用方向、语境与证据；被引页未独立阅读。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Lumbroso's 1874 Cassiano biography as an S4 archive")
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
    assert len(direct) == 10 and len(relations) == 9, (len(direct), len(relations))

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
        f"\n\n### S4 archive：Lumbroso《{NAME_ZH[1:-1]}》1874年版身份组登记（{DATE}）\n\n"
        f"- `cand-5683` → `{GROUP}` → `{KU_ID}`；10条直接 S2 断言，其中9条书目引用候选留待 S6。"
        "第21章 p.428 参考书目给出题名、G. Lumbroso、Torino 与1874年；第4章 p.101 注1及第7章 p.177 注4显示本书引用该书的不同页码。"
        "只登记该明确题名和版本，不表示已读 Lumbroso 原书。`cand-5648`、`cand-5649`、`cand-5643` 与 `cand-5462` 保持各自 undecided，不并入此组。"
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
