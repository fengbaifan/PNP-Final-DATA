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
GROUP = "archive-group-d2f847262fa3"
MEMBERS = ("cand-5160",)
KU_ID = "units/archives/soprani-vite-genovesi-ratti-1768"
CARD_REL = "04-knowledge/units/archives/soprani-vite-genovesi-ratti-1768.md"
NAME_ZH = "《热那亚画家、雕塑家与建筑师传》"
NAME_EN = "Lives of the Genoese Painters, Sculptors, and Architects"
ORIGINAL_TITLE = "Vite de’ Pittori, Scultori ed Architetti Genovesi"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "21", "page": "437", "file": "21_CHP-21Bibliography.md", "lines": "1122–1123",
        "quote": "Soprani, Raffaello: Vite de’ Pittori, Scultori ed Architetti Genovesi—in questa seconda edizione rivedute accresciute ed arrichite di note da Carlo Giuseppe Ratti, 2 vols.,\nGenova 1768.",
        "summary": "第21章参考书目印刷页437将该出版物列为 Raffaello Soprani 的《Vite de’ Pittori, Scultori ed Architetti Genovesi》，说明此第二版由 Carlo Giuseppe Ratti 修订并增注，共两卷，Genova 1768。",
        "note": "据书目照录题名拼写与版本信息；未查阅该版原书。",
    },
    {
        "chapter": "1", "page": "8", "file": "01_CHP-1_sec_ii.md", "lines": "175",
        "quote": "Soprani, II, p. 185.",
        "summary": "第1章印刷页8注1以 Soprani 第二卷第185页为 Paolo Girolamo Piola 居住经历的引文来源。",
        "note": "这是 Haskell 的引文定位；未独立查阅被引页。",
    },
    {
        "chapter": "3", "page": "74", "file": "03_CHP-3_sec_ii.md", "lines": "168",
        "quote": "1 Soprani, II, p. 10.",
        "summary": "第3章印刷页74注1引用 Soprani 第二卷第10页，作为耶稣会教堂 S. Ignazio 竞赛的历史叙述来源。",
        "note": "该项在 S2 中判为书目定位，不是实体间关系断言；被引页未独立查阅。",
    },
    {
        "chapter": "6", "page": "166", "file": "06_CHP-6_sec_v.md", "lines": "70",
        "quote": "Soprani, II, p. 186;",
        "summary": "第6章印刷页166注2引用 Soprani 第二卷第186页，涉及 Paolo Girolamo Piola 与 Niccolò Maria Pallavicini 的叙述。",
        "note": "只登记 Haskell 的来源定位；不据此确认被引页内容。",
    },
    {
        "chapter": "7", "page": "189", "file": "07_CHP-7_sec_i.md", "lines": "370",
        "quote": "1 Soprani, I, p. 254.",
        "summary": "第7章印刷页189注1引用 Soprani 第一卷第254页，关联 Haskell 对 Francesco Borzone 受聘于国王的叙述。",
        "note": "该被引页未独立查阅。",
    },
    {
        "chapter": "7", "page": "197", "file": "07_CHP-7_sec_iv.md", "lines": "108",
        "quote": "Ratti (Soprani/Ratti, II, p. 15) says that he died in 1713",
        "summary": "第7章印刷页197注1转述 Ratti 第二卷第15页称 Cassana 于1713年去世。",
        "note": "Haskell 正文另写1714年；本卡不裁决两项年份，S2已保留冲突，Ratti 原书页未独立查阅。",
    },
    {
        "chapter": "7", "page": "200", "file": "07_CHP-7_sec_v.md", "lines": "63",
        "quote": "1 Soprani, H, p. 120.",
        "summary": "第7章印刷页200注1引用 Soprani 第二卷第120页，关联 Peterborough 身份辨认的可能性。",
        "note": "Markdown OCR 将卷号识为 H；S2 按 CHP-7.pdf 实体页38核为 II。被引页未独立查阅。",
    },
    {
        "chapter": "7", "page": "200", "file": "07_CHP-7_sec_v.md", "lines": "64",
        "quote": "2 Soprani, II, p. 115...",
        "summary": "第7章印刷页200注2引用 Soprani 第二卷第115页，关联 de Ferrari 与 Noailles 的叙述。",
        "note": "保留 OCR 省略号；被引页未独立查阅。",
    },
    {
        "chapter": "8", "page": "203", "file": "08_CHP-8_intro.md", "lines": "8",
        "quote": "Soprani, passim.",
        "summary": "第8章印刷页203注1以 passim 泛引 Soprani，作为热那亚家族与收藏叙述的参考。",
        "note": "本条未给具体页码；被引出版物未独立查阅。",
    },
    {
        "chapter": "8", "page": "234", "file": "08_CHP-8_sec_ii.md", "lines": "427",
        "quote": "Ratti (see Soprani/Ratti, II, 14)",
        "summary": "第8章印刷页234注4引用 Ratti 第二卷第14页，转述 Cassana 为 Grand Prince 等人绘制肖像及历史画。",
        "note": "该 S2 记录不是关系候选；本卡仅记录书目引用，不把未具名人物或作品另行归并。",
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
    bibliography = {
        "chapter": "21", "page": "437", "file": "21_CHP-21Bibliography.md", "lines": "1122–1123",
        "quote": "Soprani, Raffaello: Vite de’ Pittori, Scultori ed Architetti Genovesi—in questa seconda edizione rivedute accresciute ed arrichite di note da Carlo Giuseppe Ratti, 2 vols.,\nGenova 1768.",
        "summary": "第21章参考书目印刷页437列出作者、题名、由 Carlo Giuseppe Ratti 修订增注的第二版、两卷本及 Genova 1768 出版信息。",
        "note": "用于确认本卡的书目身份与版本；不是对版本全文的查阅记录。",
    }
    location = f"第21章，印刷页437；Markdown 行1122–1123；{bibliography['note']}"
    rows.append({
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": bibliography["summary"],
        "original_quotes": [{"source_span": "lines 1122–1123", "text": bibliography["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
            "source_span": "lines 1122–1123; print p. 437",
        },
    })
    return rows


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
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

**中文：** 本卡登记 Raffaello Soprani 的 *{ORIGINAL_TITLE}* 1768 年第二版。第21章参考书目说明该版由 Carlo Giuseppe Ratti 修订并增注，共两卷，出版地为 Genova。第1、3、6、7、8章注释多次引用该版不同卷页，确认这些引文指向同一书目对象；原书及各被引页均未在本轮独立查阅。中文标题为据原题所作的描述性工作译名。

**English:** This card records the 1768 second edition of Raffaello Soprani’s *{ORIGINAL_TITLE}*. Chapter 21’s bibliography identifies Carlo Giuseppe Ratti as reviser and annotator, gives two volumes, and names Genova as the place of publication. Notes in Chapters 1, 3, 6, 7, and 8 cite different volume and page locators for this bibliographic object. The edition and cited pages were not independently consulted in this pass. The Chinese title is a descriptive working translation.

### 书目身份与版本

- **原题名：** *{ORIGINAL_TITLE}*；第21章参考书目，印刷页437。
- **作者：** Raffaello Soprani；据书目照录。
- **修订与增注：** Carlo Giuseppe Ratti；据书目所述第二版说明。
- **版本：** 第二版，2卷，Genova，1768。未补写书目未列出的出版者或馆藏标识。
- **本书引文位置：** 第1章 I/II卷 pp.185–186；第3章 II卷 p.10；第7章 I卷 p.254、II卷 pp.15、115、120；第8章 II卷 p.14及 passim。以上均为 Haskell 的引文定位，不表示这些页已独立核验。

### 身份边界

S3 新组 `{GROUP}` 仅含出版物候选 `cand-5160`，对应此 1768 年两卷本；不与 Raffaello Soprani、Carlo Giuseppe Ratti 两个人物候选或其他版次自动合并。第7章 p.197 的 1713 年说法与 Haskell 正文所记 1714 年冲突，仍按原断言分别保留，本卡不裁决。第3章 p.74 和第8章 p.234 的条目属于书目引文／转述，不据此增加正式关系。

## 关系与证据

当前没有登记正式关系。与本书有关的7条 S2 关系候选保留待 S6 裁决；书目引文和引用页尚未独立核验，不能仅凭引文创建内容关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the 1768 Soprani/Ratti edition in S4")
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
        source_text = " ".join((ROOT / "02-sources" / "02-Markdown" / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, (item["file"], item["quote"])
    bibliography_file = ROOT / "02-sources" / "02-Markdown" / "21_CHP-21Bibliography.md"
    bibliography_text = " ".join(bibliography_file.read_text(encoding="utf-8-sig").split())
    assert " ".join(source_rows()[-1]["original_quotes"][0]["text"].split()) in bibliography_text

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
    assert len(direct) == 10 and len(relations) == 7, (len(direct), len(relations))

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
        f"\n\n### S4 archive：Soprani/Ratti 1768年第二版跨章身份组登记（{DATE}）\n\n"
        f"- `cand-5160` → `{GROUP}` → `{KU_ID}`；书目候选仅一项，登记为 archive。第21章 p.437 明列 Raffaello Soprani、题名、Ratti 修订增注、两卷、Genova 1768；第1、3、6、7、8章均有卷页引文。卡片逐条保存本书的对应引文位置，原版及被引页未独立查阅。\n"
        "- 直接 S2 记录共10条，其中7条为关系候选，留待 S6；第3章 p.74 与第8章 p.234 两条保留为书目／转述记录，不升格为正式关系。第7章 p.197 的 Ratti 1713年说法与正文1714年说法仍为未解决冲突。\n"
        "- 未将出版物与 Soprani、Ratti 人物或其他版次合并；未新增外部身份、S5字段或正式关系。候选映射至本 KU。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_process = process_text + process_append

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; sources={len(SOURCES) + 1}; "
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
