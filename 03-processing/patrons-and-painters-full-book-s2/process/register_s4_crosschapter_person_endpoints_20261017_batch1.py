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
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

ITEMS = (
    {
        "candidate": "cand-2701",
        "group": "new-person:alessandro-varotari-il-padovanino-8619a21d71",
        "ku_id": "units/persons/alessandro-varotari-il-padovanino",
        "card_rel": "04-knowledge/units/persons/alessandro-varotari-il-padovanino.md",
        "canonical_name": "亚历山德罗·瓦罗塔里（Alessandro Varotari）",
        "name_en": "Alessandro Varotari",
        "anchor": "s4-person-alessandro-varotari-il-padovanino-20261017",
        "alias": "il Padovanino",
        "description_cn": "哈斯克尔在第4章称Alessandro Varotari为画家，并以“il Padovanino”称之；他记述Varotari赶赴罗马临摹Titian送往西班牙的《维纳斯的崇拜》。第13章另以Padovanino之名列举Filippo Pinelli收藏中的画家。",
        "description_en": "In chapter 4 Haskell identifies Alessandro Varotari as a painter and calls him “il Padovanino”; he recounts that Varotari hurried to Rome to copy Titian’s Worship of Venus when it was sent to Spain. Chapter 13 also names Padovanino among the painters represented in Filippo Pinelli’s collection.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "lines": [83, 84],
                "location": "第4章，印刷页105；OCR L83–84",
                "span": "lines 83–84; print p. 105",
                "quote": "Alessandro Varotari, ‘il Padovanino’, rushed to Rome to copy it, Cassiano acquired a number of pictures from the artist",
                "summary": "哈斯克尔称Varotari为il Padovanino，并记述他赴罗马临摹《维纳斯的崇拜》，Cassiano随后从他处购入多幅画作。",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "lines": [80],
                "location": "第13章，印刷页340；OCR L80",
                "span": "line 80; print p. 340",
                "quote": "Pictures attributed to Giorgione, Bassano, Veronese and Titian, as well as others by Palma Giovane, Padovanino and Pietro della Vecchia, figure very strongly in his collection.",
                "summary": "哈斯克尔以Padovanino之名列出Filippo Pinelli收藏中的作品归属对象。",
            },
        ),
        "statement_ids": (
            "st-chp4-sec-ii-l80-89-cassiano-acquired-varotari-pictures",
            "st-chp4-sec-ii-l80-89-varotari-travelled-to-copy-worship",
            "st-chp4-sec-ii-p100-varotari-assumption",
        ),
    },
    {
        "candidate": "cand-5505",
        "group": "new-person:longhi-roberto-5fac70ede1",
        "ku_id": "units/persons/roberto-longhi",
        "card_rel": "04-knowledge/units/persons/roberto-longhi.md",
        "canonical_name": "罗伯托·隆基（Roberto Longhi）",
        "name_en": "Roberto Longhi",
        "anchor": "s4-person-roberto-longhi-20261017",
        "description_cn": "哈斯克尔在第5章引用Roberto Longhi关于Cerquozzi与Velasquez归属问题的研究，并明确保留对该归属的怀疑；第20章又记载Longhi曾发表一幅Maffeo Barberini肖像候选。这里仅登记书中跨章指称的同一人物，不把其判断转写为本项目已确认的作品归属。",
        "description_en": "In chapter 5 Haskell cites Roberto Longhi’s discussion of Cerquozzi and the attribution to Velasquez, while explicitly retaining doubt about that attribution. Chapter 20 also records that Longhi published a candidate portrait of Maffeo Barberini. This entry registers the same person named across chapters and does not treat either attribution as confirmed by this project.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
                "lines": [140],
                "location": "第5章，印刷页136，注3；OCR L140",
                "span": "line 140; print p. 136, note 3",
                "quote": "The significance of Cerquozzi for Velasquez was pointed out by Roberto Longhi in 1950, and though his attribution to Velasquez of the so-called ‘Rissa all’ambasciata di Spagna’ is not altogether convincing",
                "summary": "哈斯克尔称Longhi于1950年指出Cerquozzi对Velasquez的重要性，同时说明他对《Rissa all’ambasciata di Spagna》的Velasquez归属并不完全信服。",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "lines": [11],
                "location": "第20章后记，印刷页396；OCR L11",
                "span": "line 11; print p. 396",
                "quote": "Not long afterwards Roberto Longhi published another candidate for the role (then, as now, in an undisclosed private collection),5",
                "summary": "哈斯克尔称Longhi后来发表了另一幅Maffeo Barberini肖像候选，并指出其收藏地点未公开。",
            },
        ),
        "statement_ids": (
            "st-chp5-notes-l140-velasquez-attribution",
            "st-chp20-p396-longhi-alternative-portrait",
        ),
    },
)


def insert_accepted(text: str, card_rel: str) -> str:
    lines = text.splitlines()
    assert f"- {card_rel}" not in lines
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def card_text(item: dict[str, object]) -> str:
    sources = []
    for source in item["sources"]:
        sources.append({
            "citation": BOOK_CITATION,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["span"], "text": source["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source["file"],
                "source_span": source["span"],
            },
        })
    fm = {
        "title": item["canonical_name"],
        "name_en": item["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}",
    }
    frontmatter = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    links = "；".join(
        f"[来源{index}](../../../{source['file']}#L{source['lines'][0]})"
        for index, source in enumerate(item["sources"], start=1)
    )
    alias_section = (
        f"\n### 名称\n\n原书别称：`{item['alias']}`（来源1、2）。\n"
        if item.get("alias") else ""
    )
    relations = "、".join(f"`{sid}`" for sid in item["statement_ids"])
    return f"""---
{frontmatter}---

## 内容

### 描述

**中文：** {item['description_cn']} {links}

**English:** {item['description_en']} {links}{alias_section}
### 本章相关内容

本卡仅记录哈斯克尔在所引章节中具名的人物身份、称谓及相关语境。原书中的作品归属、解释和评价按其原有限定保留，不由身份登记提升为已核定事实。

## 关系与证据

### 关系记录

本任务未新增正式关系。直接S2关系候选{relations}留待S6逐条裁决。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two cross-chapter person identity groups as S4 KUs.")
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
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    cards: list[tuple[dict[str, object], str, Path]] = []
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    for item in ITEMS:
        cid = str(item["candidate"])
        row = decisions[cid]
        assert candidate_by_id[cid].get("suggested_type") == "person"
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row)
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        group_members = {
            other["candidate_id"] for other in alignments
            if other.get("candidate_id") and not other.get("external_source")
            and other.get("decision") == "new"
            and sync.get_group(other.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        card_path = ROOT / str(item["card_rel"])
        assert not card_path.exists() and str(item["card_rel"]) not in accepted
        assert not any(entry.get("ku_id") == item["ku_id"] or entry.get("card_path") == item["card_rel"] for entry in manifest)
        assert not any(
            entry.get("type") == "person"
            and entry.get("name_en", "").casefold() == str(item["name_en"]).casefold()
            for entry in manifest
        ), item["name_en"]

        for source in item["sources"]:
            source_text = " ".join((ROOT / str(source["file"])).read_text(encoding="utf-8-sig").split())
            assert " ".join(str(source["quote"]).split()) in source_text, (cid, source)

        direct = [
            statement for statement in statements
            if statement.get("subject_candidate_id") == cid or statement.get("object_candidate_id") == cid
        ]
        relation_ids = {
            statement["statement_id"] for statement in direct
            if (statement.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert relation_ids == set(item["statement_ids"]), (cid, relation_ids, item["statement_ids"])

        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration ({DATE}): {item['group']} maps to {item['ku_id']}; "
            "cross-chapter source identity registered; no independent external identity verification or formal S6 relation is implied."
        )
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "person",
            "canonical_name": item["canonical_name"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
        card = card_text(item)
        fm = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)
        cards.append((item, card, card_path))

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_append = f"""

### S4 person：跨章人物关系端点——Alessandro Varotari 与 Roberto Longhi（{DATE}）

`cand-2701`（{ITEMS[0]['group']}）按第4章全名与别称“il Padovanino”及第13章索引条目中的Padovanino用例登记为[Alessandro Varotari](../units/persons/alessandro-varotari-il-padovanino.md)。`cand-5505`（{ITEMS[1]['group']}）依据第4、5、7、20章的全名及姓氏指代登记为[Roberto Longhi](../units/persons/roberto-longhi.md)。两组各新增一个person KU；3条与Varotari相关、2条与Longhi相关的直接S2关系候选均待S6，本次不新增正式边。未访问外部身份规范记录。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-varotari-longhi-20261017"></a>

### S4 person：两组跨章人物关系端点（{DATE}）

- `cand-2701`（`{ITEMS[0]['group']}`）登记至[Alessandro Varotari](../../../04-knowledge/units/persons/alessandro-varotari-il-padovanino.md)。第4章p.105明确写出全名与别称“il Padovanino”，并记述其赴罗马临摹Titian的《维纳斯的崇拜》；第13章p.340另以Padovanino列名。S3已依据同一全名／明确别称锚点完成组内对齐，未调用外部身份来源。
- `cand-5505`（`{ITEMS[1]['group']}`）登记至[Roberto Longhi](../../../04-knowledge/units/persons/roberto-longhi.md)。S2跨第4、5、7、20章记录同一全名及姓氏指代；本卡以第5章p.136注3和第20章p.396作为书内事实依据，保留哈斯克尔对Velasquez归属的限定。
- 两组均为S3 `new`，各登记一个KU；直接S2关系候选共5条，均留待S6：{', '.join(f'`{sid}`' for item in ITEMS for sid in item['statement_ids'])}。本次未登记外部核验状态、作品归属事实或正式关系。

`cand-2701` and `cand-5505` are registered as separate person KUs from cross-chapter book evidence. The book supports the names, alias, and cited contexts; no external identity records were consulted. All five direct S2 relation candidates remain pending S6, and no formal relations were added.

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = PROCESS.read_text(encoding="utf-8-sig").rstrip() + process_append
    accepted_next = accepted
    for item, _, _ in cards:
        accepted_next = insert_accepted(accepted_next, str(item["card_rel"]))

    if args.dry_run:
        print("dry-run passed: " + "; ".join(f"{item['candidate']} -> {item['ku_id']}" for item in ITEMS))
        print(
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("verified_direct_relation_candidates=5; no external verification status or S6 formal relation rows will be written; no files changed")
        return 0

    for _, card, card_path in cards:
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_next, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
