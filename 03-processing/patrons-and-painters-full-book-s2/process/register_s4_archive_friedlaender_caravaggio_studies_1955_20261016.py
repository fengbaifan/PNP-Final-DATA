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
GROUP = "archive-group-0f865c2062ea"
MEMBERS = ("cand-4375",)
KU_ID = "units/archives/friedlaender-caravaggio-studies-1955"
CARD_REL = "04-knowledge/units/archives/friedlaender-caravaggio-studies-1955.md"
NAME_ZH = "《卡拉瓦乔研究》"
NAME_EN = "Caravaggio Studies"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "1", "page": "10", "file": "01_CHP-1.md", "lines": "375",
        "quote": "The significance of this has been pointed out by Friedlaender, p. 105.",
        "summary": "第1章印刷页10注2称相关意义已由 Friedlaender 指出，并引其第105页。",
        "note": "被引页未独立查阅；此处仅记录 Haskell 的引用。",
    },
    {
        "chapter": "1", "page": "11", "file": "01_CHP-1.md", "lines": "421",
        "quote": "The contract has been published by Friedlaender, p. 302.",
        "summary": "第1章印刷页11注4称1600年合同由 Friedlaender 刊布，并引第302页。",
        "note": "被引页及所刊文本未独立查阅。",
    },
    {
        "chapter": "2", "page": "29", "file": "02_CHP-2_sec_i.md", "lines": "144",
        "quote": "2 For del Monte and Caravaggio see Friedlaender.",
        "summary": "第2章印刷页29注2引 Friedlaender，作为 del Monte 与 Caravaggio 讨论的参考。",
        "note": "本注未列页码；书目身份由第21章书目确认。",
    },
    {
        "chapter": "3", "page": "64", "file": "03_CHP-3_sec_i.md", "lines": "36",
        "quote": "1 Friedlaender, p. 123, and the forceful, but not necessarily decisive, rejection of this opinion by G. Cozzi, 1961, pp. 36 ss.",
        "summary": "第3章印刷页64注1引 Friedlaender 第123页，并转述 Cozzi 对前述观点作出有力但未必决定性的反驳。",
        "note": "保留 Haskell 对争论力度的限定；两项研究均未在本轮独立查阅。",
    },
    {
        "chapter": "3", "page": "70", "file": "03_CHP-3_sec_ii.md", "lines": "156",
        "quote": "1 Friedlaender, p. 187, and Cozzi, p. 51.",
        "summary": "第3章印刷页69–70的注1并列引用 Friedlaender 第187页及 Cozzi 第51页。",
        "note": "本注所引材料未独立查阅；S2 未把此纯书目定位列为关系候选。",
    },
    {
        "chapter": "5", "page": "120", "file": "05_CHP-5_intro.md", "lines": "9",
        "quote": "2 Friedlaender, p. 101.",
        "summary": "第5章印刷页120注2引用 Friedlaender 第101页。",
        "note": "被引页未独立查阅。",
    },
    {
        "chapter": "21", "page": "423", "file": "21_CHP-21Bibliography.md", "lines": "499",
        "quote": "Friedlaender, Walter: Caravaggio Studies, Princeton 1955. .",
        "summary": "第21章参考书目印刷页423列 Walter Friedlaender、*Caravaggio Studies*、Princeton 与1955年。",
        "note": "末尾重复句点在 S2 图像校读记录中判为 OCR 标点伪影；书目项不证明该书内容已查阅。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        location = f"第{item['chapter']}章，印刷页{item['page']}；Markdown 行{item['lines']}"
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

**中文：** 本卡登记 Walter Friedlaender 的 *Caravaggio Studies*。Haskell 第21章参考书目将其列为 Princeton 1955 年出版物；第1、2、3、5章多处注释引用该书不同页码。以上仅确认 Haskell 书内的书目身份和引文位置，不表示本轮查阅 Friedlaender 原书或核实其被引内容。中文标题为书名的工作译名。

**English:** This card records Walter Friedlaender’s *Caravaggio Studies*. Haskell’s Chapter 21 bibliography identifies it as a Princeton publication from 1955; notes in Chapters 1, 2, 3, and 5 cite different pages. This establishes the bibliographic identity and citation locations within Haskell’s book only; Friedlaender’s book and cited passages were not consulted in this pass. The Chinese title is a working translation.

### 书目身份

- **题名：** *Caravaggio Studies*；第21章参考书目，印刷页423。
- **作者：** Walter Friedlaender；据书目照录。
- **出版信息：** Princeton，1955；书目未在该条列出出版者，本卡不补写。
- **本书引文位置：** pp.101、105、123、187、302；另有未标具体页的引文。上述页码均为 Haskell 所引 Friedlaender 版本的页码，不是 Haskell 本书页码。

### 身份边界

S3 新组 `{GROUP}` 仅含 archive 候选 `cand-4375`，不与 Walter Friedlaender 人物对象或其其他出版物合并。第3章 p.64 注1还转述 G. Cozzi 对前述观点作出“有力但未必决定性”的反驳；本卡保留为 Haskell 的学术引文语境，不裁决争论，也不把并列引用视为独立验证。

## 关系与证据

当前没有登记正式关系。6条 S2 关系候选留待 S6；第3章 p.69–70 的一条纯书目定位不属于关系候选。原书及被引页未独立查阅。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Friedlaender's Caravaggio Studies in S4")
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
        and NAME_EN.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    for item in SOURCES:
        source_text = " ".join((ROOT / "02-sources" / "02-Markdown" / item["file"]).read_text(encoding="utf-8-sig").split())
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
        f"\n\n### S4 archive：Friedlaender《Caravaggio Studies》1955年版身份组登记（{DATE}）\n\n"
        f"- `cand-4375` → `{GROUP}` → `{KU_ID}`；第21章 p.423 书目列 Walter Friedlaender、题名、Princeton 与1955年；第1、2、3、5章引用相关页码。卡片登记书目身份与 Haskell 的引文位置，不称查阅原书或核实引文内容。\n"
        "- 直接 S2 记录8条，其中6条关系候选留待 S6；第3章 p.69–70 的一条注释是纯书目定位，不作关系处理。第3章 p.64 中 Cozzi 对前述观点的反驳保留 Haskell 的限定，本批不裁决学术争论。\n"
        "- 未并入 Friedlaender 人物或其他出版物；未新增正式关系、外部身份或 S5 补足。\n\n"
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
