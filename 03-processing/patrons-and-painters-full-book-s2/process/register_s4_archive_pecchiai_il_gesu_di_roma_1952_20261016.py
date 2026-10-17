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
GROUP = "archive-group-3fd673cd267d"
MEMBERS = ("cand-4996",)
KU_ID = "units/archives/pecchiai-il-gesu-di-roma-1952"
CARD_REL = "04-knowledge/units/archives/pecchiai-il-gesu-di-roma-1952.md"
NAME_ZH = "《罗马耶稣堂史》"
NAME_EN = "The Gesù of Rome"
ORIGINAL_TITLE = "Il Gesù di Roma"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "3", "page": "未在该 S2 记录中单独标注", "file": "03_CHP-3_sec_i.md", "lines": "43",
        "quote": "3 For fully documented history of the church see Pecchiai, 1952.",
        "summary": "第3章本节注释指向 Pecchiai 1952 年出版物，作为罗马耶稣堂历史的详细研究。",
        "note": "候选与书目条目提供题名和出版信息；该书未查阅。",
    },
    {
        "chapter": "3", "page": "79", "file": "03_CHP-3_sec_iv.md", "lines": "195",
        "quote": "1 Pecchiai, 1952, p. 109, for these and subsequent negotiations.",
        "summary": "第3章 p.79 注1引用 Pecchiai 1952 年版第109页，讨论相关及后续谈判。",
        "note": "被引页未独立查阅。",
    },
    {
        "chapter": "3", "page": "84", "file": "03_CHP-3_sec_iv.md", "lines": "208",
        "quote": "2 Pecchiai, 1952, p. 129, and Pascoli, I, p. 201.",
        "summary": "第3章 p.84 注2并列引用 Pecchiai 第129页与 Pascoli 第一卷第201页。",
        "note": "仅登记 Haskell 的引文位置，不核实被引内容。",
    },
    {
        "chapter": "3", "page": "84", "file": "03_CHP-3_sec_iv.md", "lines": "209",
        "quote": "3 Pecchiai, 1952, p. 101.",
        "summary": "第3章 p.84 注3引用 Pecchiai 1952 年版第101页。",
        "note": "被引页未独立查阅。",
    },
    {
        "chapter": "3", "page": "85", "file": "03_CHP-3_sec_iv.md", "lines": "213",
        "quote": "3 Pecchiai, 1952, pp. 132-7.",
        "summary": "第3章 p.85 注3引用 Pecchiai 1952 年版第132–137页。",
        "note": "保留本书所用页码缩写；被引页未独立查阅。",
    },
    {
        "chapter": "3", "page": "91", "file": "03_CHP-3_sec_iv.md", "lines": "241",
        "quote": "2 Pecchiai, 1952, pp. 259 ff.",
        "summary": "第3章 p.91 注2引用 Pecchiai 1952 年版第259页及后续页。",
        "note": "未推定引用范围的终页。",
    },
    {
        "chapter": "21", "page": "433", "file": "21_CHP-21Bibliography.md", "lines": "939",
        "quote": "Pecchiai, P.: Il Gesù di Roma, Roma 1952.",
        "summary": "第21章参考书目 p.433 列 P. Pecchiai、*Il Gesù di Roma*、Roma 1952。",
        "note": "按书目保留作者首字母，不扩写全名或未列出的出版者。",
    },
]


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    rows = []
    for item in SOURCES:
        location = f"第{item['chapter']}章，{item['page']}；Markdown 行{item['lines']}"
        if item.get("note"):
            location += f"；{item['note']}"
        span = f"lines {item['lines']}"
        if item["page"].isdigit():
            span += f"; print p. {item['page']}"
        rows.append({
            "citation": BOOK_CITATION,
            "location": location,
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": span,
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

**中文：** 本卡登记 P. Pecchiai 的 *Il Gesù di Roma*（Roma，1952）。Haskell 第3章将其列为罗马耶稣堂详细历史的参考，并在后续章节多处引用不同页码。卡片只确认本书中的书目身份与引文位置，不表示独立查阅 Pecchiai 原书或核验被引页。中文题名为忠实的描述性工作译名。

**English:** This card records P. Pecchiai’s *Il Gesù di Roma* (Roma, 1952). Haskell’s Chapter 3 points to it for a fully documented history of the Gesù in Rome, and later notes cite several page ranges. The card establishes bibliographic identity and citation locations within Haskell’s book only; Pecchiai’s book and cited pages were not consulted in this pass. The Chinese title is a descriptive working translation.

### 书目身份

- **题名：** *Il Gesù di Roma*；第21章参考书目，印刷页433。
- **作者：** P. Pecchiai；按书目照录首字母，不扩写全名。
- **出版信息：** Roma，1952；书目未列出版者，本卡不补写。
- **本书引文位置：** Haskell 引第101、109、129、132–137、259页及后续页，并有一处不标具体页的概括性指引。页码属于被引版本，不是 Haskell 本书页码。

### 身份边界

S3 新组 {GROUP} 仅含 archive 候选 cand-4996，指向 Pecchiai 的书，不是罗马耶稣堂建筑、耶稣会机构或相关绘画对象。Haskell 对其研究用途的介绍保留为书内引文语境，不将其转成已核验的历史结论。

## 关系与证据

当前没有登记正式关系。6条直接 S2 关系候选留待 S6；纯书目引用不自动升格为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pecchiai's Il Gesù di Roma in S4")
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
    assert len(direct) == 7 and len(relations) == 6, (len(direct), len(relations))

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
        f"\n\n### S4 archive：P. Pecchiai《Il Gesù di Roma》1952年版身份组登记（{DATE}）\n\n"
        f"- cand-4996 → {GROUP} → {KU_ID}；第21章 p.433 书目列作者缩写、题名与 Roma 1952。第3章将其指作耶稣堂史的详细研究，并在 pp.79、84、85、91 注释中引用相关页码。原书未查阅。\n"
        "- 直接 S2 记录7条，其中6条关系候选留待 S6。书目身份指向 Pecchiai 的书，不与耶稣堂建筑、耶稣会机构或画作混同。\n"
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
