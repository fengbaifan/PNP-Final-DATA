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
        "candidate": "cand-4231",
        "group": "new-person:apostle-peter-94e2c375ba",
        "ku_id": "units/persons/saint-peter-the-apostle",
        "card_rel": "04-knowledge/units/persons/saint-peter-the-apostle.md",
        "canonical_name": "使徒圣彼得（Saint Peter the Apostle）",
        "name_en": "Saint Peter the Apostle",
        "anchor": "s4-person-apostle-peter-20261017",
        "description_cn": "哈斯克尔第2章称“圣彼得本人”，讨论贝尔尼尼华盖中以圣彼得三重冕与钥匙表现教宗制度的方式；第3章又将圣彼得列为Lanfranco穹顶壁画中的人物。本条记录的是使徒圣彼得，与同名的圣彼得大教堂这一地点区分。",
        "description_en": "In chapter 2 Haskell refers to “St Peter himself” while discussing the papal symbolism of Bernini’s baldacchino, represented by Peter’s tiara and keys. Chapter 3 also names St Peter among the figures in Lanfranco’s dome fresco. This record identifies the apostle and distinguishes him from St Peter’s Basilica as a place.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "lines": [44],
                "location": "第2章，印刷页35；OCR L44",
                "span": "line 44; print p. 35",
                "quote": "References toSt Peter himself and the establishment of the papacy were confined to relatively small angels above the cornice carrying his tiara and keys.",
                "summary": "哈斯克尔将圣彼得本人及教宗制度的象征限定为华盖栏檐上方持其三重冕与钥匙的小天使。",
            },
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "lines": [79],
                "location": "第3章，印刷页72；OCR L79",
                "span": "line 79; print p. 72",
                "quote": "St Peter with St Andrew Avellino",
                "summary": "哈斯克尔在描述Lanfranco穹顶壁画时将圣彼得列为人物形象之一。",
            },
        ),
        "statement_ids": (
            "st-chp2-secii-l42-50-references_to_peter_and_papacy",
            "st-chp3-secii-l74-81-lanfranco-dome-depicts-st-peter",
        ),
    },
    {
        "candidate": "cand-2775",
        "group": "new-person:barozzi-da-giacomo-vignola-072c61027f",
        "ku_id": "units/persons/giacomo-barozzi-da-vignola",
        "card_rel": "04-knowledge/units/persons/giacomo-barozzi-da-vignola.md",
        "canonical_name": "贾科莫·巴罗齐·达·维尼奥拉（Giacomo Barozzi da Vignola）",
        "name_en": "Giacomo Barozzi da Vignola",
        "anchor": "s4-person-giacomo-barozzi-da-vignola-20261017",
        "description_cn": "哈斯克尔在第3章称Vignola为亚历山德罗·法尔内塞枢机的建筑师，并提及他在第4章、第10章与第20章的建筑语境中出现。原书索引将相关条目规范为Giacomo Barozzi da Vignola，S3据全名与跨章指称归为同一人物。",
        "description_en": "In chapter 3 Haskell identifies Vignola as Cardinal Alessandro Farnese’s architect, and the name also appears in architectural contexts in chapters 4, 10, and 20. The book index gives the full form Giacomo Barozzi da Vignola; S3 grouped the cross-chapter references under this person using the indexed full name.",
        "sources": (
            {
                "file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "lines": [4],
                "location": "第3章，印刷页65；OCR L4",
                "span": "line 4; print p. 65",
                "quote": "he employed his own architect Vignola and his own painters.",
                "summary": "哈斯克尔称亚历山德罗·法尔内塞雇用Vignola担任自己的建筑师，并另雇画家。",
            },
            {
                "file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "lines": [51],
                "location": "第4章，印刷页103；OCR L51",
                "span": "line 51; print p. 103",
                "quote": "Bramante, Serlio, Palladio, Vignola and the other restorers of this great art",
                "summary": "哈斯克尔转述Cassiano对Vignola及其他建筑艺术复兴者的评价。",
            },
            {
                "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "lines": [35],
                "location": "第20章后记，印刷页398；OCR L35",
                "span": "line 35; print p. 398",
                "quote": "a Farnese camp, under Alessandro Cardinal Farnese, supporting Vignola.",
                "summary": "哈斯克尔引James Ackerman概述Gesù方案争论时，称Farnese一方支持Vignola。",
            },
        ),
        "statement_ids": (
            "st-chp3-secii-l3-4-farnese-employed-vignola-and-painters",
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

本卡仅记录哈斯克尔在所引章节中的人物身份及必要语境，不补写来源未提供的生卒、亲缘或履历信息。

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

### S4 person：跨章人物关系端点——Saint Peter 与 Giacomo Barozzi da Vignola（{DATE}）

`cand-4231`（{ITEMS[0]['group']}）登记为[使徒圣彼得](../units/persons/saint-peter-the-apostle.md)；S2已将其与圣彼得大教堂地点及同名作品区分。`cand-2775`（{ITEMS[1]['group']}）依据原书索引全名与第3、4、10、20章的指称登记为[Giacomo Barozzi da Vignola](../units/persons/giacomo-barozzi-da-vignola.md)。两组各新增一个person KU；与两人相关的3条直接S2关系候选均待S6，本次不新增正式边，未访问外部身份来源。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s4-person-peter-vignola-20261017"></a>

### S4 person：两组跨章人物关系端点（{DATE}）

- `cand-4231`（`{ITEMS[0]['group']}`）登记至[使徒圣彼得](../../../04-knowledge/units/persons/saint-peter-the-apostle.md)。S2在第2、3、6、8、9章累计记录16处提及，明确区分使徒本人、同名教堂地点及作品题名；本卡以第2章p.35和第3章p.72的具名语句作为证据。两条直接关系候选为华盖中的圣彼得象征及Lanfranco穹顶人物描绘，均待S6。
- `cand-2775`（`{ITEMS[1]['group']}`）登记至[Giacomo Barozzi da Vignola](../../../04-knowledge/units/persons/giacomo-barozzi-da-vignola.md)。原书索引规范全名并列出跨章页码65、103、338、398；第3章p.65称其为Alessandro Farnese的建筑师，第4章和第20章继续出现其名。S3已按索引全名及跨章指称完成身份组，不调用外部身份记录。
- 两组新增2个person KU、2条候选映射；1条雇用建筑师关系候选与2条涉及圣彼得的关系候选共3条，全部保留待S6。未新增正式关系或S5事实。

`cand-4231` and `cand-2775` are registered as separate person KUs from cross-chapter book evidence. S2 distinguishes the apostle Peter from the basilica and similarly named work; the Vignola group follows the book index's full name and chapter references. All three direct relation candidates remain pending S6; no external identity records or formal relations were added.

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
        print("verified_direct_relation_candidates=3; no external verification status or S6 formal relation rows will be written; no files changed")
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
