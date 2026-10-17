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
        "candidate": "cand-1385",
        "group": "new-person:jean-lemaire-e5876e626a",
        "ku_id": "units/persons/jean-lemaire",
        "card_rel": "04-knowledge/units/persons/jean-lemaire.md",
        "canonical_name": "让·勒梅尔（Jean Lemaire）",
        "name_en": "Jean Lemaire",
        "anchor": "s4-person-jean-lemaire-20261017",
        "description_cn": "第4章称Jean Lemaire为Poussin的朋友，并提到他创作的capricci；第7章又记载Poussin于1639年致信其友Jean Lemaire。此卡仅登记书内跨章指称的人物身份及相关语境。",
        "description_en": "Chapter 4 identifies Jean Lemaire as a friend of Poussin and mentions capricci by him. Chapter 7 records that Poussin wrote to his friend Jean Lemaire in 1639. This card registers only the person named across these chapters and the stated context.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "lines": [81],
                "location": "第4章，印刷页105；OCR L81",
                "span": "line 81; print p. 105",
                "quote": "some capricci by Poussin’s friend, Jean Lemaire",
                "summary": "哈斯克尔称Jean Lemaire为Poussin的朋友，并将若干capricci归于他。",
            },
            {
                "file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "lines": [81],
                "location": "第7章，印刷页176；OCR L81",
                "span": "line 81; print p. 176",
                "quote": "Early in 1639 Poussin wrote to his friend Jean Lemaire",
                "summary": "哈斯克尔记述Poussin于1639年初写信给友人Jean Lemaire。",
            },
        ),
        "statement_ids": (
            "st-chp4-sec-ii-l80-89-poussin-friend-of-jean-lemaire",
            "st-chp4-sec-ii-l80-89-lemaire-created-capricci",
        ),
    },
    {
        "candidate": "cand-1099",
        "group": "new-person:antonio-gai-479e2478a1",
        "ku_id": "units/persons/antonio-gai",
        "card_rel": "04-knowledge/units/persons/antonio-gai.md",
        "canonical_name": "安东尼奥·盖（Antonio Gai）",
        "name_en": "Antonio Gai",
        "anchor": "s4-person-antonio-gai-20261017",
        "description_cn": "原书索引将雕塑家Gai列为Antonio Gai。第10章记述Tessin特别欣赏雕塑家Gai；第13章又称Tessin经Zanetti委托Gai创作一件人物雕像，并以“un demi-Michel Ange”评价他。来源未给出该雕像的正式题名或完成状态。",
        "description_en": "The book index identifies the sculptor Gai as Antonio Gai. Chapter 10 records that Tessin particularly admired the sculptor Gai; chapter 13 says Tessin used Zanetti to commission a figure from him and described him as “un demi-Michel Ange.” The source does not give the figure a formal title or state its completion status.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "lines": [283, 284],
                "location": "第10章，印刷页293；OCR L283–284",
                "span": "lines 283–284; print p. 293",
                "quote": "the sculptor Gai, whom he particularly admired",
                "summary": "哈斯克尔转述Tessin说，他将尽力帮助自己特别欣赏的雕塑家Gai。",
            },
            {
                "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
                "lines": [102],
                "location": "第13章，正文页标342；OCR L102（书内索引列页341）",
                "span": "line 102; source page marker 342; index entry lists p. 341",
                "quote": "a figure by the sculptor Gai, whom he considered to be ‘un demi-Michel Ange’",
                "summary": "哈斯克尔称Tessin借Zanetti之力委托Gai制作一件人物雕像，并以“半个米开朗琪罗”评价Gai；书内索引列341页，正文转录页标为342。",
            },
            {
                "file": "02-sources/03-Index/03-2-Index-CSV/G.csv",
                "lines": [8],
                "location": "书内索引，G.csv L8；索引条目列页293、341",
                "span": "line 8; index entry lists pp. 293, 341",
                "quote": "Gai, Antonio",
                "summary": "书内索引给出雕塑家Gai的全名Antonio Gai，并列出正文页码293与341。",
            },
        ),
        "statement_ids": (
            "st-chp10-p293-tessin-gai-letter",
            "st-chp13-p342-tessin_assessed_gai_as_half_michelangelo",
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

本卡仅记录哈斯克尔在所引章节及索引中的人物身份、称谓和相关语境，不扩展为完整生平或作品目录。

## 关系与证据

### 关系记录

本任务未新增正式关系。直接S2关系候选{relations}留待S6逐条裁决。
"""
    return f"---\n{frontmatter}---\n\n{body}"


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

### S4 person：跨章人物关系端点——Jean Lemaire 与 Antonio Gai（{DATE}）

`cand-1385`（{ITEMS[0]['group']}）依据第4、7章反复出现的全名登记为[Jean Lemaire](../units/persons/jean-lemaire.md)。`cand-1099`（{ITEMS[1]['group']}）依据第10、13章“雕塑家Gai”的指称及书内索引全名登记为[Antonio Gai](../units/persons/antonio-gai.md)。Gai索引列示第341页，而第13章正文转录页标为342，过程记录保留两种定位。两组各新增一个person KU；4条直接关系候选待S6，不新增正式边或外部身份核验状态。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-lemaire-gai-20261017"></a>

### S4 person：两组跨章人物关系端点（{DATE}）

- `cand-1385`（`{ITEMS[0]['group']}`）登记至[Jean Lemaire](../../../04-knowledge/units/persons/jean-lemaire.md)。第4章p.105明示其为Poussin之友并称其制作capricci；第7章p.176再次以全名将其作为Poussin的朋友提及。两个直接关系候选留待S6。
- `cand-1099`（`{ITEMS[1]['group']}`）登记至[Antonio Gai](../../../04-knowledge/units/persons/antonio-gai.md)。第10章p.293称其为雕塑家并记Tessin特别欣赏他；第13章正文转录在页标342称其制作一件人物雕像，Tessin称其为“un demi-Michel Ange”。书内索引G.csv L8给出全名Antonio Gai，但页码列为293、341；第13章源码页标为342，故同时保留，不改写为同页。相关雕像无正式题名或完成状态依据。
- 两组新增2个person KU、2条候选映射；直接S2关系候选共4条，全部留待S6；本次未新增正式关系或外部身份核验状态。

`cand-1385` and `cand-1099` are registered as separate person KUs from cross-chapter book references. The Gai identity follows the book index's full name; its index page 341 and the chapter transcription's page marker 342 are both retained. All four direct relation candidates remain pending S6.

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
        print("verified_direct_relation_candidates=4; no external verification status or S6 formal relation rows will be written; no files changed")
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
