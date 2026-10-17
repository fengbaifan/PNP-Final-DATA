from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "archive-group-4ec5e3284567"
MEMBERS = ("cand-1515", "cand-10849")
KU_ID = "units/archives/manfrin-edwards-letter-1793-12-03"
CARD_REL = "04-knowledge/units/archives/manfrin-edwards-letter-1793-12-03.md"
CARD_PATH = ROOT / CARD_REL
ANCHOR = "s4-archive-manfrin-edwards-letter-1793-12-03-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "file": "02-sources/02-Markdown/17_CHP-17_sec_i.md",
        "location": "第17章注6，印刷页380；OCR L31",
        "span": "OCR line 31; printed page 380, note 6",
        "quote": "Biblioteca Correr—Epistolario Meschini—published in full in Appendix 7.",
        "summary": "哈斯克尔称该书信藏于Biblioteca Correr的Epistolario Meschini，并在附录7全文刊出。",
    },
    {
        "file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
        "location": "第19章附录7，印刷页395；OCR L197",
        "span": "OCR line 197; printed page 395",
        "quote": "Letter from Girolamo Manfrin to Pietro Edwards of 3 December 1793",
        "summary": "附录7标题以双方姓名和日期识别该书信，并称其涉及曼弗林画廊的形成。",
    },
    {
        "file": "02-sources/02-Markdown/19_CHP-19Appendix.md",
        "location": "第19章附录7，印刷页395；OCR L197",
        "span": "OCR line 197; printed page 395",
        "quote": "Epistolario Moschini). See Chapter 17, p. 380, note 6.",
        "summary": "附录标题给出Moschini拼写并回指第17章p.380注6；两处拼写差异保留，不据此改写来源记录。",
    },
)


def make_sources() -> list[dict[str, object]]:
    return [
        {
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        }
        for item in SOURCES
    ]


def card_text() -> str:
    links = (
        "[第17章注6 p.380](../../../02-sources/02-Markdown/17_CHP-17_sec_i.md#L31)；"
        "[第19章附录7 p.395](../../../02-sources/02-Markdown/19_CHP-19Appendix.md#L197)"
    )
    fm = {
        "title": "吉罗拉莫·曼弗林致皮耶特罗·爱德华兹书信（1793年12月3日）",
        "name_en": "Letter from Girolamo Manfrin to Pietro Edwards (3 December 1793)",
        "type": "archive",
        "sub_type": "letter",
        "evidence_status": "source_backed",
        "sources": make_sources(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    frontmatter = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{frontmatter}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔附录7全文刊出的1793年12月3日书信，标题将Girolamo Manfrin列为发信人、Pietro Edwards列为收信人，并称其涉及Manfrin画廊的形成。附录标题定位至Biblioteca Correr的Epistolario Moschini；第17章p.380注6则写作Epistolario Meschini，并指向附录7。这里保留两处拼写差异；原手稿未独立查阅。{links}

**English:** This card records the letter printed in full in Haskell’s Appendix 7, dated 3 December 1793 and identified in its heading as a letter from Girolamo Manfrin to Pietro Edwards concerning the formation of Manfrin’s picture gallery. The appendix heading locates it in the Epistolario Moschini at Biblioteca Correr; chapter 17, page 380, note 6 spells the series name Epistolario Meschini and points to Appendix 7. Both source forms are retained; the manuscript was not independently consulted. {links}

### 文献身份与范围

- **文书类型：** 单封书信；题名为依据附录标题形成的描述性名称，不声称为原件题名。
- **日期与收发双方：** 1793-12-03；Girolamo Manfrin致Pietro Edwards，按哈斯克尔附录标题记录。
- **档案定位：** 哈斯克尔将其定位于Biblioteca Correr的Epistolario Moschini；第17章注6使用Meschini拼写。原件及馆藏目录未在本任务独立查阅。
- **对象边界：** 本卡只登记该单封书信，不与候选`cand-10605`所指Epistolario Moschini档案系列合并；也不将书信内容升级为新的关系断言。

## 关系与证据

当前没有本任务新增的正式关系。直接S2关系候选`st-chp17-p380-note6-edwards-letter-source`与`st-chp19-p395-manfrin-edwards-letter-source`保留待S6复核；身份登记不代替对书信、档案系列或附录刊布关系的正式审查。
"""


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter S3 group for Manfrin's 1793 letter as one S4 archive KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id)
    for cid in MEMBERS:
        candidate, row = candidate_by_id[cid], decisions[cid]
        assert candidate.get("suggested_type") == "archive"
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row)
        assert sync.get_group(row.get("resolution_note", "")) == GROUP, (cid, sync.get_group(row.get("resolution_note", "")))
    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    assert not CARD_PATH.exists() and CARD_REL not in ACCEPTED.read_text(encoding="utf-8-sig")
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and row.get("name_en", "").casefold() == "letter from girolamo manfrin to pietro edwards (3 december 1793)"
        for row in manifest
    )
    for item in SOURCES:
        source_text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, item

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relation_candidates = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert {row["statement_id"] for row in direct} == {
        "st-chp17-p380-note6-edwards-letter-source",
        "st-chp19-p395-manfrin-edwards-letter-source",
    }
    assert len(relation_candidates) == 2

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        row = planned_by_id[cid]
        row["ku_id"] = KU_ID
        row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        row["resolution_note"] += (
            f" S4 registration (2026-10-17): {GROUP} maps to {KU_ID}; the appendix heading and chapter 17 note identify the same dated letter. "
            "The manuscript was not independently consulted, and no S6 formal relation is implied."
        )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "曼弗林致爱德华兹书信（1793年12月3日）",
        "name_en": "Letter from Girolamo Manfrin to Pietro Edwards (3 December 1793)",
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    fm = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_next = result_next.rstrip() + f"""

### S4 archive：Manfrin致Edwards书信（1793-12-03；{DATE}）

`cand-1515`（索引子项）与`cand-10849`（附录7书信候选）同属`{GROUP}`，共同登记为[1793年书信archive KU](../units/archives/manfrin-edwards-letter-1793-12-03.md)。附录标题给出发信人、收信人、日期及画廊语境，并回指第17章p.380注6；注6称该信藏于Epistolario Meschini并在附录7全文刊出，附录标题拼作Epistolario Moschini。原件未独立查阅，两条直接S2关系候选待S6。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_append = f"""

<a id="{ANCHOR}"></a>

### S4 archive：Manfrin致Edwards书信（1793-12-03；{DATE}）

- `cand-1515`（M.csv#52，p.395）与`cand-10849`（第19章附录7）同属`{GROUP}`，共同映射至[1793年书信archive KU](../../../{CARD_REL})。附录标题明确Girolamo Manfrin致Pietro Edwards、日期1793-12-03及画廊形成主题；第17章p.380注6称书信藏于Biblioteca Correr的Epistolario Meschini并在附录7全文刊出。附录标题写作Epistolario Moschini；两处拼写均保留。手稿未独立查阅。
- 该KU仅指单封书信，与`cand-10605`所指档案系列Epistolario Moschini分开。2条直接S2关系候选留待S6；本次只登记身份，不新增正式边或S5补足。

The index entry and the Appendix 7 letter candidate map to one KU. The appendix heading identifies Manfrin as sender, Edwards as recipient, gives the date 3 December 1793, and describes the letter's subject as the formation of Manfrin's gallery. Chapter 17, page 380, note 6 points to the same letter and spells the collection Meschini; Appendix 7 spells it Moschini. Both forms are retained. The manuscript was not independently consulted. The letter remains distinct from the archival series candidate; both direct S2 relation candidates remain pending S6.

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = PROCESS.read_text(encoding="utf-8-sig").rstrip() + process_append
    accepted_next = insert_accepted(ACCEPTED.read_text(encoding="utf-8-sig"))

    if args.dry_run:
        print(f"dry-run passed: group={GROUP}; members={','.join(MEMBERS)} -> {KU_ID}; direct_statements={len(direct)}; relation_candidates_pending={len(relation_candidates)}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}")
        print("No files changed; no S5 enrichment or S6 formal relation rows will be written.")
        return 0

    CARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_next, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
