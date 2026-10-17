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
        "candidate": "cand-1894",
        "group": "new-person:petty-william-e0750fd206",
        "ku_id": "units/persons/william-petty-arundel-agent",
        "card_rel": "04-knowledge/units/persons/william-petty-arundel-agent.md",
        "canonical_name": "威廉·佩蒂（William Petty）",
        "name_en": "William Petty",
        "anchor": "s4-person-william-petty-arundel-agent-20261017",
        "description_cn": "第4章正文称Lord Arundel在1636年写信给其代理人，注释将一封从Ratisbon寄出的信标为致William Petty；第7章又记载Arundel于1636年写信给在Rome的William Petty。本条仅登记书内姓名与代理人语境，不据此补充外部身份或完整履历。",
        "description_en": "Chapter 4 says Lord Arundel wrote to his agent in 1636, and its note identifies a letter from Ratisbon as addressed to William Petty. Chapter 7 also records Arundel writing to William Petty in Rome in 1636. This entry records only the name and agent context in the book, without adding an external identity or full biography.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
                "lines": [28],
                "location": "第4章，印刷页97；OCR L28",
                "span": "line 28; print p. 97",
                "quote": "Lord Arundel, ever on the lookout for possible treasures, wnote to his agent in 1636",
                "summary": "哈斯克尔称Lord Arundel于1636年写信给其代理人，谈及一位负债的公爵所拥有的珍物。",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
                "lines": [56],
                "location": "第4章，印刷页98，注5；OCR L56",
                "span": "line 56; print p. 98, note 5",
                "quote": "Letter to William Petty from Ratisbon, dated 8 September 1636, published by Hervey, p. 386.",
                "summary": "注释将前述信件定位为1636年9月8日从Ratisbon寄给William Petty的信，并称由Hervey刊布。",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "lines": [119],
                "location": "第7章，印刷页179；OCR L119",
                "span": "line 119; print p. 179",
                "quote": "he wrote in November 1636 to William Petty in Rome",
                "summary": "哈斯克尔称Arundel于1636年11月写信给在罗马的William Petty。",
            },
        ),
        "statement_ids": (
            "st-chp4-sec-i-l26-33-arundel-letter",
            "st-chp4-sec-i-l42-67-fn97-arundel-letter",
        ),
    },
    {
        "candidate": "cand-1947",
        "group": "new-person:elder-pitt-william-a3834b7e2c",
        "ku_id": "units/persons/william-pitt-the-elder",
        "card_rel": "04-knowledge/units/persons/william-pitt-the-elder.md",
        "canonical_name": "威廉·皮特长者（William Pitt, the Elder）",
        "name_en": "William Pitt, the Elder",
        "anchor": "s4-person-william-pitt-elder-20261017",
        "description_cn": "第14章记载Algarotti在1764年遗嘱中将两幅画留给“elder Pitt”，并称这一举动招致Diderot的讽刺评论；第20章后记再次称为“Elder Pitt”。书内索引给出姓名形式William Pitt, the Elder。本卡保留来源的语境，不扩展为该人物的其他生平事实。",
        "description_en": "Chapter 14 says Algarotti’s 1764 will left two pictures to the “elder Pitt” and that the gesture drew sarcastic comments from Diderot; the chapter 20 postscript again calls him the “Elder Pitt.” The book index gives the form William Pitt, the Elder. This record preserves the source context without adding other biographical facts.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/14_CHP-14_intro.md",
                "lines": [102],
                "location": "第14章，印刷页356；OCR L102",
                "span": "line 102; print p. 356",
                "quote": "in his will, drawn up in 1764, he left two pictures to the elder Pitt",
                "summary": "哈斯克尔称Algarotti于1764年遗嘱中将两幅画留给elder Pitt，并说此举引发Diderot的讽刺评论。",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "lines": [192],
                "location": "第20章后记，印刷页409；OCR L192",
                "span": "line 192; print p. 409",
                "quote": "Algarotti left to the Elder Pitt",
                "summary": "哈斯克尔在后记中再次称Algarotti将两幅画留给Elder Pitt。",
            },
            {
                "file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
                "lines": [150],
                "location": "书内索引，P.csv L150；索引条目列页310注、356、409",
                "span": "line 150; index entry lists p. 310 n., pp. 356, 409",
                "quote": "Pitt, William, the Elder",
                "summary": "书内索引将elder Pitt规范为William Pitt, the Elder，并列出跨章页码。",
            },
        ),
        "statement_ids": (
            "st-chp14-p356-will-bequest-two-pictures-to-pitt",
        ),
    },
    {
        "candidate": "cand-4515",
        "group": "new-person:iii-paul-d17277c320",
        "ku_id": "units/persons/pope-paul-iii",
        "card_rel": "04-knowledge/units/persons/pope-paul-iii.md",
        "canonical_name": "教宗保禄三世（Pope Paul III）",
        "name_en": "Pope Paul III",
        "anchor": "s4-person-pope-paul-iii-20261017",
        "description_cn": "第2章称Paul III曾召集特伦托会议，并记述Guglielmo della Porta为其制作的陵墓被移至圣彼得大教堂的另一壁龛；第4章再次以OCR形式“Paul Ill”提及该陵墓与Urban VIII陵墓相对。本条使用第2章明确的Paul III作为姓名依据，保留第4章OCR字形。",
        "description_en": "Chapter 2 says Paul III summoned the Council of Trent and describes Guglielmo della Porta’s tomb for him being moved to another niche in St Peter’s. Chapter 4 refers again to that tomb opposite the tomb of Urban VIII, with the OCR reading “Paul Ill.” This entry uses the clear form in chapter 2 as its name evidence and preserves the chapter 4 OCR reading.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "lines": [125],
                "location": "第2章，印刷页41；OCR L125",
                "span": "line 125; print p. 41",
                "quote": "Guglielmo della Porta’s tomb of Paul III, who had summoned the Council",
                "summary": "哈斯克尔称Guglielmo della Porta为Paul III制作的陵墓，并明确说Paul III召集了该会议。",
            },
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "lines": [128],
                "location": "第2章，印刷页42；OCR L128",
                "span": "line 128; print p. 42",
                "quote": "of Trent, was moved from one of the central pillars to a corresponding niche on the left of the apse.",
                "summary": "承接前句，哈斯克尔说明该陵墓由中央柱移至后殿左侧相应壁龛。",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "lines": [55, 56],
                "location": "第4章，印刷页104；OCR L55–56",
                "span": "lines 55–56; print p. 104",
                "quote": "the tomb of Urban VIII ‘though it has been praised has in no way diminished the reputation of Paul Ill’s [by Guglielmo della Porta] opposite’",
                "summary": "哈斯克尔转述Cassiano对Urban VIII陵墓及其对面Paul Ill陵墓的评价；OCR将III识为Ill，未据此改写原文。",
            },
        ),
        "statement_ids": (
            "st-chp2-secii-l118-125-paul-iii-and-council",
            "st-chp2-secii-l127-139-council-of-trent-continuation",
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
    relations = "、".join(f"`{sid}`" for sid in item["statement_ids"])
    body = f"""## 内容

### 描述

**中文：** {item['description_cn']} {links}

**English:** {item['description_en']} {links}

### 本章相关内容

本卡仅记录哈斯克尔在所引章节及索引中的人物身份和相关语境，不扩展为完整生平。

## 关系与证据

### 关系记录

本任务未新增正式关系。直接S2关系候选{relations}留待S6逐条裁决。
"""
    return f"---\n{frontmatter}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three cross-chapter person identity groups as S4 KUs.")
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

### S4 person：跨章人物关系端点——William Petty、William Pitt the Elder 与 Pope Paul III（{DATE}）

`cand-1894`（{ITEMS[0]['group']}）依据第4、7章及索引条目登记为[William Petty](../units/persons/william-petty-arundel-agent.md)。`cand-1947`（{ITEMS[1]['group']}）依据第14、20章及索引条目登记为[William Pitt, the Elder](../units/persons/william-pitt-the-elder.md)。`cand-4515`（{ITEMS[2]['group']}）依据第2、4章关于Paul III陵墓的指称登记为[Pope Paul III](../units/persons/pope-paul-iii.md)；第4章OCR作“Paul Ill”，已保留。三组各新增一个person KU；5条直接S2关系候选留待S6，不新增正式边或外部身份核验状态。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-petty-pitt-paul-iii-20261017"></a>

### S4 person：三组跨章人物关系端点（{DATE}）

- `cand-1894`（`{ITEMS[0]['group']}`）登记至[William Petty](../../../04-knowledge/units/persons/william-petty-arundel-agent.md)。第4章p.97称Lord Arundel给代理人写信，注5（p.98）指明寄往William Petty；第7章p.179再次称Arundel写给罗马的William Petty。相关两条直接关系候选留待S6。
- `cand-1947`（`{ITEMS[1]['group']}`）登记至[William Pitt, the Elder](../../../04-knowledge/units/persons/william-pitt-the-elder.md)。第14章p.356记载Algarotti遗嘱将两幅画留给elder Pitt，第20章后记p.409再次提及该遗赠；P.csv L150给出索引全名。直接遗赠候选留待S6。
- `cand-4515`（`{ITEMS[2]['group']}`）登记至[Pope Paul III](../../../04-knowledge/units/persons/pope-paul-iii.md)。第2章p.41–42明确写Paul III召集特伦托会议，并续述其陵墓移位；第4章p.104的OCR将Paul III转录为“Paul Ill”，该异文已保留。两条直接关系候选留待S6。
- 三组新增3个person KU和3条候选映射；直接S2关系候选共5条，均不在本次升级为正式关系。

`cand-1894`, `cand-1947`, and `cand-4515` are registered as separate person KUs from cross-chapter book evidence. The Paul III reference in chapter 4 preserves the OCR form “Paul Ill.” All five direct relation candidates remain pending S6; no external identity records or formal relations were added.

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
