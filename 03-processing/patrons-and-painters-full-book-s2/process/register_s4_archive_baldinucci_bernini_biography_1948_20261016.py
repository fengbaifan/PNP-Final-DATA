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
GROUP = "archive-group-5a4cacb078dc"
MEMBERS = ("cand-4548",)
KU_ID = "units/archives/baldinucci-bernini-biography-samek-ludovici-1948"
CARD_REL = "04-knowledge/units/archives/baldinucci-bernini-biography-samek-ludovici-1948.md"
NAME_ZH = "《贝尔尼尼骑士传》"
NAME_EN = "Life of the Cavaliere Gio. Lorenzo Bernini"
ORIGINAL_TITLE = "Vita del Cavaliere Gio. Lorenzo Bernini"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "1", "page": "17", "file": "01_CHP-1.md", "lines": "699",
        "quote": "Baldi\u00ad\nnucci, 1948, p. 89.",
        "summary": "第1章 p.17 注1引用 Baldinucci 1948年版第89页，讨论 Thomas Baker 的贝尔尼尼胸像。",
        "note": "仅记录 Haskell 的引文定位。",
    },
    {
        "chapter": "1", "page": "19", "file": "01_CHP-1.md", "lines": "796",
        "quote": "1 Baldinucci, 1948, p. 78.",
        "summary": "第1章 p.19 注1引用 Baldinucci 1948年版第78页。",
        "note": "被引页未独立查阅。",
    },
    {
        "chapter": "2", "page": "34", "file": "02_CHP-2_sec_ii.md", "lines": "158",
        "quote": "3 BaMinucci, 1948, p. 80.",
        "summary": "第2章 p.34 注3引用 Baldinucci 1948年版第80页。",
        "note": "本地 OCR 作 BaMinucci；S2 记录已按扫描页识别为 Baldinucci。被引页未独立查阅。",
    },
    {
        "chapter": "3", "page": "82", "file": "03_CHP-3_sec_iv.md", "lines": "202",
        "quote": "1 Book I, chapter 16, verse 117. 2 Baldinucci, 1948, p. 135.",
        "summary": "第3章 p.82 注2引用 Baldinucci 1948年版第135页。",
        "note": "前一条经文定位与本书目引用并列；不表示独立查阅原书。",
    },
    {
        "chapter": "6", "page": "151", "file": "06_CHP-6_sec_i.md", "lines": "136",
        "quote": "1 Baldinucci, 1948, p. 107.",
        "summary": "第6章 p.151 注1引用 Baldinucci 1948年版第107页。",
        "note": "被引页未独立查阅。",
    },
    {
        "chapter": "6", "page": "153", "file": "06_CHP-6_sec_i.md", "lines": "145",
        "quote": "1 Baldinucci, 1948, pp. in ff.",
        "summary": "第6章 p.153 注1引用 Baldinucci 1948年版多个后续页；S2 记录说明印刷页读作 pp.111 ff.，并指向该版第249页注107。",
        "note": "保留 OCR 摘录 pp. in ff.；采用的印刷读法及页码限定来自 S2 记录，不是本轮重新校读。",
    },
    {
        "chapter": "7", "page": "177", "file": "07_CHP-7_sec_i.md", "lines": "319",
        "quote": "1 Baldinucci, 1948, p. 92.",
        "summary": "第7章 p.177 注1引用 Baldinucci 1948年版第92页。",
        "note": "被引页未独立查阅。",
    },
    {
        "chapter": "21", "page": "未在该 S2 记录中单独标注", "file": "21_CHP-21Bibliography.md", "lines": "89",
        "quote": "Baldinucci, Filippo: Vita del Cavaliere Gio. Lorenzo Bernini—studio e note di Sergio Samek Ludovici, Milano 1948.",
        "summary": "第21章书目列 Filippo Baldinucci、作品题名、Sergio Samek Ludovici 的研究与注释责任，以及 Milano 1948。",
        "note": "书目行未在该 S2 记录中单独标注印刷页；不补造出版者。",
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
                "source_span": f"lines {item['lines']}" + (f"; print p. {item['page']}" if item["page"].isdigit() else ""),
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

**中文：** 本卡登记 Filippo Baldinucci 所著 *{ORIGINAL_TITLE}*，由 Sergio Samek Ludovici 作研究与注释，Milano，1948。Haskell 在第1、2、3、6、7章多处引用该版不同页码。卡片仅确认本书中的书目身份和引文位置，不表示 Baldinucci 原书或被引页已独立查阅。中文题名为据原题拟定的描述性工作译名。

**English:** This card records Filippo Baldinucci’s *{ORIGINAL_TITLE}*, with study and notes by Sergio Samek Ludovici, published in Milano in 1948. Haskell cites different pages in Chapters 1, 2, 3, 6, and 7. This establishes the bibliographic identity and citation locations within Haskell’s book only; Baldinucci’s book and cited passages were not independently consulted. The Chinese title is a descriptive working translation.

### 书目身份

- **题名：** *{ORIGINAL_TITLE}*；题名保留原书缩写 Gio.
- **作者：** Filippo Baldinucci。
- **研究与注释：** Sergio Samek Ludovici；书目原文作 “studio e note di”。
- **出版信息：** Milano，1948；书目未列出版者，本卡不补写。
- **本书引文位置：** pp.78、80、89、92、107、135、111 ff.；S2 另记该版 note 107 位于 p.249。均为 Haskell 对所引版本的页码，未独立查阅。

### 身份边界

S3 新组 {GROUP} 仅含 archive 候选 cand-4548，指向这部贝尔尼尼传记版次。它与 Filippo Baldinucci 人物 KU、Gian Lorenzo Bernini 人物 KU及贝尔尼尼的具体雕塑或绘画对象区分；编辑与注释责任不据此另行合并到作者身份。

## 关系与证据

当前没有登记正式关系。6条直接 S2 关系候选留待 S6；书目身份和引文定位不自动产生正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Baldinucci's 1948 Bernini biography in S4")
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
        and "1948" in " ".join(row.values())
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
        f"\n\n### S4 archive：Baldinucci《Vita del Cavaliere Gio. Lorenzo Bernini》1948年版身份组登记（{DATE}）\n\n"
        f"- cand-4548 → {GROUP} → {KU_ID}；第21章书目列 Filippo Baldinucci、题名、Sergio Samek Ludovici 的研究与注释、Milano 1948；第1、2、3、6、7章多处引用不同页码。原书未查阅。\n"
        "- 直接 S2 记录8条，其中6条关系候选留待 S6。部分 OCR 形态（BaMinucci、pp. in ff.）及 S2 的校读依据照实保留，不将其写成原书已核读。\n"
        "- 与作者人物及 Bernini 作品对象区分；未新增正式关系、外部身份或 S5 补足。\n\n"
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
