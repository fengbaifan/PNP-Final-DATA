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
GROUP = "archive-group-fb110b11a649"
MEMBERS = ("cand-1508", "cand-6089")
KU_ID = "units/archives/mancini-considerazioni-sulla-pittura-1956"
CARD_REL = "04-knowledge/units/archives/mancini-considerazioni-sulla-pittura-1956.md"
CARD_PATH = ROOT / CARD_REL
ANCHOR = "s4-archive-mancini-considerazioni-sulla-pittura-1956-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "file": "02-sources/02-Markdown/01_CHP-1.md",
        "location": "第1章注1，印刷页14；OCR L562",
        "span": "OCR line 562; printed page 14",
        "quote": "Mancini, I, p. 140.",
        "summary": "第1章引用Mancini第一卷第140页；本次只保留为1956年版书目定位，不据此独立核查页内内容。",
    },
    {
        "file": "02-sources/02-Markdown/05_CHP-5_intro.md",
        "location": "第5章注3，印刷页120；OCR L9",
        "span": "OCR line 9; printed page 120",
        "quote": "3 Mancini, I, p. 249.",
        "summary": "第5章注3引用Mancini第一卷第249页；注释页面另含第1956年版书目互证。",
    },
    {
        "file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "location": "第5章注4，印刷页123；OCR L141",
        "span": "OCR line 141; printed page 123",
        "quote": "See also the critical edition of his works, 1956.",
        "summary": "第5章注4称可参见Mancini著作的1956年校勘版；该注与第21章完整书目对应。",
    },
    {
        "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "location": "第21章书目，印刷页428；OCR L745–746",
        "span": "OCR lines 745–746; printed page 428",
        "quote": "Mancini, Giulio: Considerazioni sulla Pittura, pubblicate per la prima volta da Adriana Marucchi con il commento da Luigi Salerno, 2 vols., Roma 1956.",
        "summary": "书目记录Giulio Mancini《Considerazioni sulla Pittura》，Adriana Marucchi编、Luigi Salerno注释、罗马1956年两卷本。",
    },
)


def get_group_token(note: str) -> str | None:
    match = re.search(r"(?:^|[;| ])group=([A-Za-z0-9-]+)", note)
    return match.group(1) if match else None


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
        "[第1章注1 p.14](../../../02-sources/02-Markdown/01_CHP-1.md#L562)；"
        "[第5章注3 p.120](../../../02-sources/02-Markdown/05_CHP-5_intro.md#L9)；"
        "[第5章注4 p.123](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md#L141)；"
        "[第21章书目 p.428](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L745)"
    )
    fm = {
        "title": "曼奇尼《绘画论》（Considerazioni sulla Pittura, 1956 critical edition）",
        "name_en": "Considerazioni sulla Pittura (1956 critical edition)",
        "type": "archive",
        "sub_type": "book",
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

**中文：** 本卡记录哈斯克尔第21章书目所列Giulio Mancini《Considerazioni sulla Pittura》1956年校勘版：Adriana Marucchi编、Luigi Salerno注释、罗马出版、两卷。第1、5章引文中的卷I页码与书目所列版次相对应；本项目未直接查阅该版本，因此不把引文内容表述为独立核验结果。{links}

**English:** This card records the 1956 critical edition of Giulio Mancini’s *Considerazioni sulla Pittura* listed in Haskell’s chapter 21 bibliography: edited by Adriana Marucchi, with commentary by Luigi Salerno, in two volumes, Rome. The volume I locators cited in chapters 1 and 5 correspond to this bibliographic record. The edition was not directly consulted in this project, so the cited contents are not treated as independently verified. {links}

### 书目身份与范围

- **原题名：** *Considerazioni sulla Pittura*。
- **中文工作名：** 《绘画论》；用于识别，不声称为正式中译题名。
- **版本：** Adriana Marucchi编、Luigi Salerno注释，Roma 1956，两卷；依据第21章书目照录。
- **对象边界：** 本卡登记1956年校勘版，不将泛称的`Treatise`另建为一个对象，也不登记Mancini人物。索引候选`cand-1508`（pp.124、130）与正文／书目候选`cand-6089`对应同一版次。
- **引文范围：** 哈斯克尔第1章注1引用第一卷p.140，第5章注3引用第一卷p.249；第5章注4另指1956年校勘版。原书对应页均未在本任务独立查阅。

## 关系与证据

当前没有本任务新增的正式关系。直接S2书目关系候选`st-chp1-secii-p14-n1-cites-mancini-i-p140`、`st-chp5-p120-note3-mancini-locator`及`st-chp5-note-p123-n4-critical-edition`留待S6复核；登记版次不自动建立引用边或验证引文内容。
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
    parser = argparse.ArgumentParser(description="Register the two-candidate S3 group for Mancini's 1956 critical edition as one S4 archive KU.")
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
        assert get_group_token(row.get("resolution_note", "")) == GROUP, (cid, get_group_token(row.get("resolution_note", "")))
    group_members = {
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and get_group_token(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    assert not CARD_PATH.exists() and CARD_REL not in ACCEPTED.read_text(encoding="utf-8-sig")
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and row.get("name_en", "").casefold() == "considerazioni sulla pittura (1956 critical edition)"
        for row in manifest
    )
    for item in SOURCES:
        text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in text, item

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
    assert len(direct) == 4 and len(relation_candidates) == 3

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
            f" S4 registration (2026-10-17): {GROUP} maps to {KU_ID}; both the index locator and the body/bibliography candidate "
            "refer to the same 1956 two-volume critical edition. The cited pages were not independently consulted; no S6 formal relation is implied."
        )
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": "曼奇尼《绘画论》（1956年校勘版）",
        "name_en": "Considerazioni sulla Pittura (1956 critical edition)",
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

### S4 archive：Mancini《Considerazioni sulla Pittura》1956年版（{DATE}）

`cand-1508`（索引子项）与`cand-6089`（正文／书目候选）同属`{GROUP}`，共同登记为[1956年校勘版archive KU](../units/archives/mancini-considerazioni-sulla-pittura-1956.md)。第21章p.428书目明确给出Marucchi编、Salerno注释、罗马1956年两卷本；第1、5章的卷I页码定位与该书目对应。4条直接S2陈述中3条关系候选仍待S6，原书未独立查阅。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_append = f"""

<a id="{ANCHOR}"></a>

### S4 archive：Mancini《Considerazioni sulla Pittura》1956年版（{DATE}）

- `cand-1508`（M.csv#45，pp.124、130）与`cand-6089`（第5章正文／第21章书目）保留同一S3身份组`{GROUP}`，共同映射到[1956年版archive KU](../../../{CARD_REL})。书目p.428给出完整题名、Adriana Marucchi编、Luigi Salerno注释、Roma 1956、2 vols；第1章注1和第5章注3的卷I页码定位及第5章注4的1956年校勘版说明相互支持。文献未独立查阅。
- 两名候选写入同一KU；不把第5章p.124的泛称`Treatise`另建对象，也不与Giulio Mancini人物KU合并。4条直接S2陈述中3条关系候选留待S6；本次不添加正式边或S5补足。

The index candidate and the body/bibliography candidate remain one S3 archive group and map to a single KU. Haskell's bibliography records the full title, Marucchi as editor, Salerno's commentary, Rome 1956, and two volumes; chapter 1 and chapter 5 cite volume I, and chapter 5 also points to the 1956 critical edition. The edition was not independently consulted. Three of the four direct S2 statements remain relation candidates for S6; no formal relation or S5 enrichment was added.

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
