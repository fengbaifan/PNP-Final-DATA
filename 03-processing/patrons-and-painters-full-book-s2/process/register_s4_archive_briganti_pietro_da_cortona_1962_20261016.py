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
GROUP = "archive-group-68573842c8b3"
MEMBERS = ("cand-4473",)
KU_ID = "units/archives/briganti-pietro-da-cortona-1962"
CARD_REL = "04-knowledge/units/archives/briganti-pietro-da-cortona-1962.md"
NAME_ZH = "《皮耶特罗·达·科尔托纳》"
NAME_EN = "Pietro da Cortona"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"

SOURCES = [
    {
        "chapter": "21", "page": "423", "file": "21_CHP-21Bibliography.md", "lines": "261",
        "quote": "Briganti, G.: Pietro da Cortona, Firenze 1962.",
        "summary": "第21章参考书目印刷页423列 G. Briganti、*Pietro da Cortona*、Firenze 与1962年。",
        "note": "保留书目给出的首字母，不扩写作者全名。",
    },
    {
        "chapter": "1", "page": "12", "file": "01_CHP-1.md", "lines": "462",
        "quote": "Brigand, 1962, p. 251",
        "summary": "第1章印刷页12注1引用 Briganti 1962 年出版物第251页，涉及一项有争议的作品归属。",
        "note": "本地转录作 Brigand；书目写 Briganti。被引页未独立查阅，本卡不校定该段争议。",
    },
    {
        "chapter": "2", "page": "38", "file": "02_CHP-2_sec_ii_visual-transcription.md", "lines": "9",
        "quote": "For this whole section see Mostra di Pietro da Cortona, 1956, and Briganti, 1962.",
        "summary": "第2章印刷页38注释续页将 Briganti 1962 列为本节整体参考。",
        "note": "此处是章节范围的书目指引，不指向单一事实；其他出版物仍保持独立身份。",
    },
    {
        "chapter": "2", "page": "51", "file": "02_CHP-2_sec_iv.md", "lines": "226",
        "quote": "2 For the most recent discussion of the fresco see Briganti, 1962.",
        "summary": "第2章印刷页51注2将 Briganti 1962 作为相关壁画较新讨论的参考。",
        "note": "仅记录 Haskell 的引文定位。",
    },
    {
        "chapter": "2", "page": "59", "file": "02_CHP-2_sec_vii.md", "lines": "44",
        "quote": "8 Briganti, 1962, p. 254. The picture has disappeared.",
        "summary": "第2章印刷页59注8引用 Briganti 1962 年版第254页，并报告该画已不存。",
        "note": "画作状况是 Haskell 的陈述；本卡不将其当作该书内容的独立核验。",
    },
    {
        "chapter": "3", "page": "75", "file": "03_CHP-3_sec_ii.md", "lines": "173",
        "quote": "2 For the date see Pollak, 1927, I, p. 436, and Brigand, 1962, p. 205.",
        "summary": "第3章印刷页75注2并列引 Pollak 与 Briganti 1962 年版第205页以讨论日期。",
        "note": "OCR 转录作 Brigand；卡片按书目标题登记，不裁决被引日期。",
    },
    {
        "chapter": "3", "page": "77", "file": "03_CHP-3_sec_iv.md", "lines": "190",
        "quote": "1 Brigand, 1962, pp. 248-9. ,-",
        "summary": "第3章印刷页77注1引用 Briganti 1962 年版第248–249页。",
        "note": "OCR 转录作 Brigand 并带有末尾杂字符；仅记录书目定位。",
    },
    {
        "chapter": "6", "page": "149", "file": "06_CHP-6_sec_i.md", "lines": "44",
        "quote": "Brigand,’1962, p. 146.",
        "summary": "第6章印刷页149注1引用 Briganti 1962 年版第146页，讨论 Cortona 的 Aeneid 壁画年代。",
        "note": "保留 OCR 标点与 Brigand 转录；不据引文核实年代。",
    },
    {
        "chapter": "7", "page": "176", "file": "07_CHP-7_sec_i.md", "lines": "315",
        "quote": "3 ibid., p. 31, note 2. 4 ibid., pp. 36 and 37; Brigand, 1962, p. 142.",
        "summary": "第7章印刷页176注4引用 Briganti 1962 年版第142页。",
        "note": "S2 过程记录指出扫描页转录将该处印刷 Briganti 识为 Brigand；被引页未独立查阅。",
    },
    {
        "chapter": "7", "page": "184", "file": "07_CHP-7_sec_i.md", "lines": "357",
        "quote": "4 Bonnaffé, pp. 168-70, and Briganti, 1962, p. 230. Guercino’s Cato is now at Marseilles—Hoog, pp. 270 ff.",
        "summary": "第7章印刷页184注4引用 Briganti 1962 年版第230页。",
        "note": "该书页未独立查阅；同注其他出版物保持独立书目身份。",
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

**中文：** 本卡登记 G. Briganti 的 *Pietro da Cortona*，据 Haskell 第21章书目，出版地 Firenze，年份1962。Haskell 在第1、2、3、6、7章多次引用该出版物，涉及作品归属、壁画、日期等不同讨论。卡片只确认书目身份和 Haskell 的引用位置，不表示独立查阅该书或复核所引内容。中文题名为依原题所作的工作译名。

**English:** This card records G. Briganti’s *Pietro da Cortona*, identified in Haskell’s Chapter 21 bibliography as published in Firenze in 1962. Haskell cites it in Chapters 1, 2, 3, 6, and 7 in discussions of attribution, frescoes, dates, and other topics. The card records bibliographic identity and Haskell’s citation locations only; it does not indicate independent consultation of the book or verification of cited contents. The Chinese title is a working translation of the original title.

### 书目身份

- **题名：** *Pietro da Cortona*；第21章参考书目，印刷页423。
- **责任者：** G. Briganti；按书目所列首字母和姓氏记录，不扩写全名。
- **出版信息：** Firenze，1962；书目未列出版者，本卡不补写。
- **本书引文位置：** Haskell 引第142、146、205、230、248–249、251、254页及未标具体页的章节范围参考；这些是被引出版物的页码。

### 身份边界

S3 新组 {GROUP} 仅含 cand-4473 这一 archive 候选。它与 Pietro da Cortona 人物 KU units/persons/pietro-da-cortona 区分；同名书题不代表对象类型或身份相同。Haskell 正文、注释中的转录出现 Briganti/Brigand 差异，书目项作 G. Briganti；本卡不扩写作者全名，不据引文裁决作品归属或其他学术争议。

## 关系与证据

当前没有登记正式关系。6条 S2 关系候选留待 S6；其他章节范围或纯书目定位记录不自动升格为关系。原书与被引页未独立查阅。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Briganti's Pietro da Cortona in S4")
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
        and "pietro da cortona" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        and "briganti" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(direct) == 10 and len(relations) == 6, (len(direct), len(relations))

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
        f"\n\n### S4 archive：G. Briganti《Pietro da Cortona》1962年版身份组登记（{DATE}）\n\n"
        f"- cand-4473 → {GROUP} → {KU_ID}；第21章 p.423 书目列 G. Briganti、Pietro da Cortona、Firenze 1962。第1、2、3、6、7章多处引用该书；本次登记书目身份，不表示查阅原书或核验被引页。\n"
        "- 直接 S2 记录10条，其中6条关系候选留待 S6。Haskell/OCR 中出现 Briganti 与 Brigand 的转录差异；卡片保留书目中的 G. Briganti，不扩写姓名，也不裁决作品归属争论。\n"
        "- 与 Pietro da Cortona 人物 KU 区分；未新增正式关系、外部身份或 S5 补足。\n\n"
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
