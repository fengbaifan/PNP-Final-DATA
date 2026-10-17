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
        "candidate": "cand-1861",
        "group": "new-person:claude-de-fabri-nicolas-peiresc-cf0115e95f",
        "ku_id": "units/persons/nicolas-claude-fabri-de-peiresc",
        "card_rel": "04-knowledge/units/persons/nicolas-claude-fabri-de-peiresc.md",
        "canonical_name": "尼古拉-克洛德-法布里·德·佩雷斯克（Nicolas-Claude-Fabri de Peiresc）",
        "name_en": "Nicolas-Claude-Fabri de Peiresc",
        "anchor": "s4-person-peiresc-20261017",
        "description_cn": "原书索引将Peiresc列为Nicolas-Claude-Fabri de Peiresc。第2章称他为普罗旺斯古物学者，并记述Maffeo与他保持学术通信；第4章又引用Peiresc对Cassiano的称誉。",
        "description_en": "The book index identifies Peiresc as Nicolas-Claude-Fabri de Peiresc. Chapter 2 calls him a Provençal antiquary and says Maffeo corresponded with him on learned matters; chapter 4 quotes Peiresc’s praise of Cassiano.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "lines": [113],
                "location": "第2章，印刷页30；OCR L113",
                "span": "line 113; print p. 30",
                "quote": "a learned correspondence with the Provençal antiquary Peiresc",
                "summary": "哈斯克尔称Maffeo与普罗旺斯古物学者Peiresc有学术通信。",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "lines": [16],
                "location": "第4章，印刷页100；OCR L16",
                "span": "line 16; print p. 100",
                "quote": "Peiresc called him ‘la fleur des bons amys’",
                "summary": "哈斯克尔引Peiresc称Cassiano为“la fleur des bons amys”。",
            },
            {
                "file": "02-sources/03-Index/03-2-Index-CSV/P.csv",
                "lines": [64],
                "location": "书内索引，P.csv L64；索引条目列页30、100、107注",
                "span": "line 64; index entry lists pp. 30, 100, 107 n.",
                "quote": "Peiresc, Nicolas-Claude-Fabri de",
                "summary": "书内索引提供Peiresc的全名，并列出正文及注释页码。",
            },
        ),
        "statement_ids": (
            "st-chp2-seci-l108-119-maffeo-correspondence-peiresc",
            "st-chp4-sec-ii-l15-22-peiresc",
        ),
    },
    {
        "candidate": "cand-2353",
        "group": "new-person:german-joachim-sandrart-von-joachim-sandra-2467fbbb7e",
        "ku_id": "units/persons/joachim-von-sandrart",
        "card_rel": "04-knowledge/units/persons/joachim-von-sandrart.md",
        "canonical_name": "约阿希姆·冯·桑德拉尔特（Joachim von Sandrart）",
        "name_en": "Joachim von Sandrart",
        "anchor": "s4-person-joachim-von-sandrart-20261017",
        "description_cn": "第2章以全名Joachim von Sandrart称其为德国人，并记述Giustiniani依其建议将一幅画置于帷幕后；第8章又记载Sandrart回忆见过一幅描绘自杀中的Cato的绘画。本条仅登记书内跨章指称的同一人物。",
        "description_en": "Chapter 2 names Joachim von Sandrart as a German and says Giustiniani placed a painting behind a curtain on his advice. Chapter 8 records Sandrart’s recollection of a painting of Cato shown in the act of suicide. This entry registers the same person named across the chapters.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "lines": [102],
                "location": "第2章，印刷页29；OCR L102",
                "span": "line 102; print p. 29",
                "quote": "on the advice of the German Joachim von Sandrart",
                "summary": "哈斯克尔称Giustiniani依德国人Joachim von Sandrart的建议将一幅画藏在帷幕后。",
            },
            {
                "file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "lines": [27],
                "location": "第8章，印刷页205；OCR L27",
                "span": "line 27; print p. 205",
                "quote": "Sandrart recalled seeing a Cato ‘who lies in his own welling blood after committing suicide and tears his intestines into pieces with his hands’.",
                "summary": "哈斯克尔转述Sandrart曾见到一幅以自杀后的Cato为题的绘画，并复述其描绘细节。",
            },
            {
                "file": "02-sources/03-Index/03-2-Index-CSV/S.csv",
                "lines": [43],
                "location": "书内索引，S.csv L43；索引条目列页29",
                "span": "line 43; index entry lists p. 29",
                "quote": "Sandrart, Joachim von",
                "summary": "书内索引以Joachim von Sandrart为规范姓名形式。",
            },
        ),
        "statement_ids": (
            "st-chp2-seci-l95-106-sandart-advice",
            "st-chp8-p205-sandrart-recalled-cato",
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

### S4 person：跨章人物关系端点——Nicolas-Claude-Fabri de Peiresc 与 Joachim von Sandrart（{DATE}）

`cand-1861`（{ITEMS[0]['group']}）依据第2、4章姓名及书内索引全名登记为[Nicolas-Claude-Fabri de Peiresc](../units/persons/nicolas-claude-fabri-de-peiresc.md)。`cand-2353`（{ITEMS[1]['group']}）依据第2章全名及第8章姓氏指代登记为[Joachim von Sandrart](../units/persons/joachim-von-sandrart.md)。两组各新增一个person KU；4条直接S2关系候选留待S6，不新增正式边或外部身份核验状态。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-peiresc-sandrart-20261017"></a>

### S4 person：两组跨章人物关系端点（{DATE}）

- `cand-1861`（`{ITEMS[0]['group']}`）登记至[Nicolas-Claude-Fabri de Peiresc](../../../04-knowledge/units/persons/nicolas-claude-fabri-de-peiresc.md)。第2章p.30称其为普罗旺斯古物学者，第4章p.100引用其对Cassiano的称誉；P.csv L64给出索引全名并列页30、100、107注。两条直接关系候选均待S6。
- `cand-2353`（`{ITEMS[1]['group']}`）登记至[Joachim von Sandrart](../../../04-knowledge/units/persons/joachim-von-sandrart.md)。第2章p.29以全名称其为德国人，第8章p.205再次以Sandrart姓氏转述其所见Cato绘画；S.csv L43确认书内索引姓名。两条直接关系候选均待S6。
- 两组新增2个person KU和2条候选映射；4条直接S2关系候选保留待S6，不新增正式关系或外部身份核验状态。

`cand-1861` and `cand-2353` are registered as separate person KUs from cross-chapter references and book-index names. All four direct relation candidates remain pending S6; no external identity records or formal relations were added.

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
