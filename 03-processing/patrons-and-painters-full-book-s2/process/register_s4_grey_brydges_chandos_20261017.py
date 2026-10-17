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
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-grey-brydges-fifth-lord-chandos-20261017"
CANDIDATES = ("cand-0644", "cand-0645")
GROUP = "new-person:5th-brydges-chandos-grey-b35ab5db22"
KU_ID = "units/persons/grey-brydges-fifth-lord-chandos"
CARD_REL = "04-knowledge/units/persons/grey-brydges-fifth-lord-chandos.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "格雷·布里奇斯，第五代钱多斯勋爵"
NAME_EN = "Grey Brydges, 5th Lord Chandos"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/C.csv"
INTRO_FILE = "02-sources/02-Markdown/03_CHP-3_intro.md"
SECTION_FILE = "02-sources/02-Markdown/03_CHP-3_sec_i.md"
INDEX_MAIN_QUOTE = '"Chandos, Grey Brydges, 5th Lord"'
INDEX_SUBENTRY_QUOTE = "Discourse of Rome"
SECTION_QUOTE = "‘In the next place’, wrote Grey Brydges, 5th Lord Chandos, in his Discourse of Rome,"
FOOTNOTE_QUOTE = "2 [Grey Brydges, 5th Lord Chandos]: Horae Subsecivae, pp. 386 ff."
RELATION_IDS = (
    "st-chp3-seci-l3-14-charge-attributed-to-grey",
    "st-chp3-seci-l3-14-grey-quoted-jesuit-description",
    "st-chp3-intro-l7-9-horae-authored-by-chandos",
)
NON_RELATION_ID = "st-chp3-seci-l3-14-haskell-evaluates-grey"

SOURCES = (
    {
        "citation": f"{BOOK_CITATION}, book index.",
        "location": "书后索引，C.csv#168 主项与 C.csv#169 子项；均定位印刷页63",
        "summary": "索引主项列 Chandos, Grey Brydges, 5th Lord，子项为 Discourse of Rome；两条均定位 p.63。索引仅作书内定位，不独立验证身份或著作责任。",
        "quotes": (("C.csv#168", INDEX_MAIN_QUOTE), ("C.csv#169", INDEX_SUBENTRY_QUOTE)),
        "doc_id": "patrons-and-painters-index",
        "file": INDEX_FILE,
    },
    {
        "citation": f"{BOOK_CITATION}, ch. 3, p. 63.",
        "location": "第3章第一节，印刷页63；OCR L7–14",
        "summary": "正文以 Grey Brydges, 5th Lord Chandos 全名引出其 Discourse of Rome 中关于耶稣会教堂的旅人记述；这是哈斯克尔转引的来源，不表示本次独立查阅该书。",
        "quotes": (("lines 7–14; print p. 63", SECTION_QUOTE),),
        "doc_id": "patrons-and-painters",
        "file": SECTION_FILE,
    },
    {
        "citation": f"{BOOK_CITATION}, ch. 3, p. 63, n. 2.",
        "location": "第3章引言，印刷页63，注2；OCR L9",
        "summary": "脚注以方括号将 Grey Brydges, 5th Lord Chandos 列在 Horae Subsecivae 题名前；这是书内的责任归属，尚未独立核实。正文称 Discourse of Rome，脚注题为 Horae Subsecivae，两题名关系待证。",
        "quotes": (("lines 7–9; print p. 63, n. 2", FOOTNOTE_QUOTE),),
        "doc_id": "patrons-and-painters",
        "file": INTRO_FILE,
    },
)


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": item["citation"],
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": item["doc_id"],
                "source_file": item["file"],
                "source_span": "; ".join(span for span, _ in item["quotes"]),
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relations = "\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第3章 p.63 具名的 Grey Brydges, 5th Lord Chandos。正文以此名引出他在 *Discourse of Rome* 中对耶稣会教堂的旅人描述；同页脚注又以方括号将此人列于 *Horae Subsecivae* 题名前。书后索引的 Chandos 主项及 *Discourse of Rome* 子项均定位 p.63。正文与脚注题名之间的书目关系尚未解决；脚注的责任归属也未独立核实。本卡按 S3 合并 `cand-0644` 与 `cand-0645`，只登记同一书内人物身份，不裁定两题名是否指同一文献。中文显示名为项目工作音译及头衔暂译。

**English:** This card records Grey Brydges, 5th Lord Chandos, named on p. 63 of Haskell’s chapter 3. The prose introduces a traveller’s description of Jesuit churches from his *Discourse of Rome*; the footnote on the same page brackets his name before the title *Horae Subsecivae*. Both the Chandos index entry and its *Discourse of Rome* subentry point to p. 63. The bibliographic relationship between the two titles remains unresolved, and the footnote’s attribution has not been independently verified. Following S3, this card maps `cand-0644` and `cand-0645` to one book-local person; it does not decide whether the two titles identify the same work. The Chinese display name and title are project working translations.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 本名 / Name | Grey Brydges | 第3章第一节，印刷页63，L8 |
| 贵族称号 / Peerage title | 5th Lord Chandos | 第3章第一节，印刷页63，L8；索引 C.csv#168 |

### 本章相关内容

哈斯克尔将一段关于耶稣会教堂的旅人描述归于 Grey Brydges，并称该指控于1620年由一位英国旅人首次提出；邻句将旅人具名为 Grey。哈斯克尔还评价该段更多体现 Grey 的新教信念，而非他对情势的真实理解。引文及评价均为哈斯克尔的转述，不代表本次核实了旅人所指教堂或其评价的真实性。第3章注2对 *Horae Subsecivae* 的方括号归属，与正文的 *Discourse of Rome* 题名并列保留，不据此合并文献。

Haskell attributes a traveller’s description of Jesuit churches to Grey Brydges and says an English traveller first made the charge in 1620; the adjacent sentence names Grey. Haskell also judges the passage to reflect Grey’s Protestant convictions more than his real understanding of the situation. Both the quotation and this assessment are Haskell’s account, not an independent verification of the church identified by the traveller or the truth of the account. The bracketed attribution to *Horae Subsecivae* in chapter 3 note 2 is kept alongside the prose title *Discourse of Rome*; the titles are not merged here.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

以下3条直接 S2 关系候选留待 S6 逐项审查；脚注作者归属仍是哈斯克尔的书内归属，不作为已经核实的正式关系：

{relations}
"""


def update_pending_warning(result: str, alignment_rows: list[dict]) -> str:
    pending = [row for row in alignment_rows if row.get("decision") == "new" and not row.get("ku_id")]
    candidate_rows = [row for row in pending if not row.get("external_source")]
    external_rows = [row for row in pending if row.get("external_source")]
    pending_groups = {
        sync.get_group(row.get("resolution_note", "")) or row.get("candidate_id", "")
        for row in candidate_rows
    }
    warning = (
        f"审计警告中的{sync.fmt(len(pending))}条待登记 `decision=new` alignment 行，含"
        f"{sync.fmt(len(candidate_rows))}条候选决定映射（{sync.fmt(len(pending_groups))}组）和"
        f"{sync.fmt(len(external_rows))}条外部身份记录。"
    )
    result, count = re.subn(
        r"审计警告中的[\d,]+条待登记 `decision=new` alignment 行，含[\d,]+条候选决定映射（[\d,]+组）和[\d,]+条外部身份记录。",
        warning,
        result,
        count=1,
    )
    assert count == 1, "could not refresh pending-alignment audit note"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S3 Grey Brydges identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    if (
        CARD_PATH.exists()
        and CARD_REL in accepted_text
        and any(row.get("ku_id") == KU_ID for row in manifest)
        and all(decisions.get(cid, {}).get("ku_id") == KU_ID for cid in CANDIDATES)
    ):
        print("ALREADY REGISTERED: Grey Brydges person group")
        return 0

    assert all(cid in candidate_map and candidate_map[cid]["suggested_type"] == "person" for cid in CANDIDATES)
    target_rows = [decisions[cid] for cid in CANDIDATES]
    assert all(row["decision"] == "new" and not row.get("ku_id") for row in target_rows)
    assert all(sync.get_group(row.get("resolution_note", "")) == GROUP for row in target_rows)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert sorted(row["candidate_id"] for row in group_rows) == sorted(CANDIDATES)
    assert not CARD_PATH.exists(), "target card path already exists; inspect for an existing object before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold() or row.get("canonical_name") == NAME_ZH)
        for row in manifest
    ), "same person already exists in the manifest"

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    section_text = " ".join((ROOT / SECTION_FILE).read_text(encoding="utf-8-sig").split())
    intro_text = " ".join((ROOT / INTRO_FILE).read_text(encoding="utf-8-sig").split())
    assert INDEX_MAIN_QUOTE in index_text and INDEX_SUBENTRY_QUOTE in index_text
    assert " ".join(SECTION_QUOTE.split()) in section_text
    assert " ".join(FOOTNOTE_QUOTE.split()) in intro_text

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = [
        row for row in statements.values()
        if any(cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")) for cid in CANDIDATES)
    ]
    assert {row["statement_id"] for row in direct} == set(RELATION_IDS) | {NON_RELATION_ID}
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is True for sid in RELATION_IDS)
    assert statements[NON_RELATION_ID]["qualifiers"].get("relation_candidate") is False

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: both index candidates in {GROUP} map to one KU, {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text = update_pending_warning(result_text, planned_alignment)

    process_entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Grey Brydges, 5th Lord Chandos 两候选并组登记（{DATE}）

`cand-0644`（C.csv#168，Chandos 主项）与 `cand-0645`（C.csv#169，Discourse of Rome 子项）按 S3 组 `{GROUP}` 共用[格雷·布里奇斯人物卡](../../../04-knowledge/units/persons/grey-brydges-fifth-lord-chandos.md)。书后索引两条均定位 p.63；第3章第一节以完整姓名引出 *Discourse of Rome* 中的旅人引文，第3章注2又将同一全名置于 *Horae Subsecivae* 前。两候选是同一人物的索引主项及子项，不是两个人物。正文和脚注的书目题名关系仍待证，方括号归属未独立核实；S4 不据此建立文献或作者正式关系。

直接 S2 关系候选 `{RELATION_IDS[0]}`、`{RELATION_IDS[1]}`、`{RELATION_IDS[2]}` 留待 S6；哈斯克尔对 Grey 的评价 statement 保持非关系分类。引文中的耶稣会教堂不在本卡身份裁决中消歧。本次未写入 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip() + process_entry

    result_note = (
        f"\n\n### S3→S4 person：Grey Brydges, 5th Lord Chandos（{DATE}）\n\n"
        "`cand-0644`（Chandos 主项）与 `cand-0645`（*Discourse of Rome* 子项）共用一张人物 KU。"
        "p.63 正文全名和同页索引定位支持书内身份；正文与注2分别列 *Discourse of Rome* 与 *Horae Subsecivae*，两题名关系及脚注归属继续待证。"
        "3条直接关系候选留待 S6，未新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("dry-run passed: cand-0644 and cand-0645 form exactly one S3 new-person group")
        print("verified both index entries, the full name in the prose, the footnote attribution, and three direct S2 relation candidates")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv unchanged")
        print("planned writes: one bilingual person card, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Grey Brydges person group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
