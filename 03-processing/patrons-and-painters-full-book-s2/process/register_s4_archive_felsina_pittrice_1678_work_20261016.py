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
GROUP = "archive-group-04dd83a032f3"
MEMBERS = ("cand-6933",)
EDITION_CANDIDATE = "cand-11384"
KU_ID = "units/archives/felsina-pittrice-1678-work"
CARD_REL = "04-knowledge/units/archives/felsina-pittrice-1678-work.md"
NAME_ZH = "《博洛尼亚画家传》"
NAME_EN = "Felsina Pittrice (Lives of the Bolognese Painters)"
ORIGINAL_TITLE = "Felsina Pittrice"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "7", "page": "176", "file": "07_CHP-7_sec_i.md", "lines": "316",
        "quote": "5 Malvasia, II, p. 264. 6 Blunt, 1954, p. 89.",
        "summary": "第7章 p.176 注5引用 Malvasia 第二卷第264页。",
        "note": "Haskell 的引文定位；具体版本及被引页未独立查阅。",
    },
    {
        "chapter": "7", "page": "178", "file": "07_CHP-7_sec_i.md", "lines": "324",
        "quote": "1 Malvasia, II, p. 261, and Mahon, 1949, p. 222, who suggests that there was no link between the Semiramis and Charles I’s invitation.",
        "summary": "第7章 p.178 注1引用 Malvasia 第二卷第261页，并并列讨论 Mahon 的解释。",
        "note": "此处引用页仍是书内定位，不表示读过该版本。",
    },
    {
        "chapter": "7", "page": "182", "file": "07_CHP-7_sec_i.md", "lines": "345",
        "quote": "3 Malvasia, II, p. 264.",
        "summary": "第7章 p.182 注3引用 Malvasia 第二卷第264页。",
        "note": "Haskell 的引文定位；被引页未独立查阅。",
    },
    {
        "chapter": "7", "page": "182", "file": "07_CHP-7_sec_i.md", "lines": "346",
        "quote": "4 ibid., II, p. 327.",
        "summary": "第7章 p.182 注4以 ibid. 回指 Malvasia，引用第二卷第327页。",
        "note": "回指关系按相邻注释保留；被引页未独立查阅。",
    },
    {
        "chapter": "7", "page": "189", "file": "07_CHP-7_sec_i.md", "lines": "252–253",
        "quote": "Malvasia’s Felsina Pittrice (lives of the Bolognese artists) of 1678 to Louis XIV.",
        "summary": "第7章 p.189 称 Malvasia 的 *Felsina Pittrice*（博洛尼亚画家传）发表于1678年并题献给 Louis XIV。",
        "note": "句子跨 Markdown 行断排；保留 Haskell 对原作年份及题献的陈述，不据此将1841年版合并。",
    },
    {
        "chapter": "8", "page": "203", "file": "08_CHP-8_intro.md", "lines": "9",
        "quote": "3 See Malvasia and Zanotti, passim.",
        "summary": "第8章 p.203 注3泛引 Malvasia 与 Zanotti。",
        "note": "未指定卷页；仅记录 Haskell 的书目指向。",
    },
    {
        "chapter": "21", "page": "428", "file": "21_CHP-21Bibliography.md", "lines": "743",
        "quote": "Malvasia, Carlo Cesare: Felsina Pittrice, 2 vols., Bologna 1841.",
        "summary": "第21章书目 p.428 列 Carlo Cesare Malvasia 的两卷本 *Felsina Pittrice*，Bologna 1841。",
        "note": "这是另一个 1841 年版候选 cand-11384 的书目证据；该候选当前为 S3 undecided，本卡不把该版本登记到1678年作品组。",
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
        "sub_type": "literary work",
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

**中文：** 本卡登记 Carlo Cesare Malvasia 的 *Felsina Pittrice* 1678年作品身份。Haskell 第7章称该作题献给 Louis XIV，并在第7、8章多处引用其内容。Haskell 书目另列两卷本 Bologna 1841 年版，但对应的 edition 候选 cand-11384 目前仍为 S3 undecided；本卡不把1841年印本的具体版本身份并入1678年作品卡。被引卷页和原书均未独立查阅。中文题名为据 Haskell 英文释义所作的描述性工作译名。

**English:** This card records the 1678 work identity of Carlo Cesare Malvasia’s *Felsina Pittrice*. Haskell’s Chapter 7 says it was dedicated to Louis XIV and cites it in Chapters 7 and 8. Haskell’s bibliography separately lists a two-volume Bologna 1841 edition; its edition candidate, cand-11384, remains S3 undecided. This card does not merge that specific 1841 printing with the 1678 work. The original work and cited pages were not independently consulted. The Chinese title is a descriptive working translation of Haskell’s English gloss.

### 作品身份

- **原题名：** *Felsina Pittrice*；Haskell glosses it as “lives of the Bolognese artists.”
- **作者：** Carlo Cesare Malvasia；姓名见第21章书目。
- **原作时间与题献：** Haskell p.189 gives 1678 and dedication to Louis XIV.
- **版本边界：** Haskell’s bibliography identifies a separate two-volume Bologna 1841 edition (cand-11384, S3 undecided). The volume-II locators cited in Chapters 7 and 8 are retained as Haskell’s references; the cited printing is not independently identified or consulted here.

### 身份边界

S3 新组 {GROUP} 仅含作品候选 cand-6933。该身份不与 Malvasia 人物 KU 或 S3 尚未裁决的1841年版候选 cand-11384 合并；也不把正文未点名的其他版本、卷册或手抄本扩展进本卡。

## 关系与证据

当前没有登记正式关系。6条直接 S2 关系候选留待 S6，包括 Haskell 所引页码及作品题献陈述；本卡不把引文自动转为正式边。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the 1678 Felsina Pittrice work in S4")
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
    assert decisions[EDITION_CANDIDATE].get("decision") == "undecided"
    assert not decisions[EDITION_CANDIDATE].get("ku_id")
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and ORIGINAL_TITLE.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        and "1678" in " ".join(row.values())
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
    assert len(direct) == 6 and len(relations) == 6, (len(direct), len(relations))

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
        f"\n\n### S4 archive：Malvasia《Felsina Pittrice》1678年作品身份组登记（{DATE}）\n\n"
        f"- cand-6933 → {GROUP} → {KU_ID}，按 S3 组登记1678年作品身份。第7章 p.189 称该作题献 Louis XIV；第7、8章另有 Malvasia 卷页引文。第21章书目列两卷本 Bologna 1841 年版，候选 cand-11384 当前为 undecided；本卡不把该 edition 映射到1678年作品。\n"
        "- 直接 S2 记录6条，全部为关系候选，留待 S6；卷页指向的具体印本未独立确认或查阅。\n"
        "- 未新增正式关系、外部版本身份或 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; sources={len(SOURCES)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}; "
            f"separate_1841_edition={EDITION_CANDIDATE}:undecided"
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
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"separate_1841_edition={EDITION_CANDIDATE}:undecided"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
