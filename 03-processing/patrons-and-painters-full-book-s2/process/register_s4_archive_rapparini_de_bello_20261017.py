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
        "candidate": "cand-2108",
        "group": "archive-group-91edf12eec0e",
        "type": "archive",
        "ku_id": "units/archives/le-portrait-du-vrai-merite-rapparini-1709",
        "card_rel": "04-knowledge/units/archives/le-portrait-du-vrai-merite-rapparini-1709.md",
        "name_zh": "《普法尔茨选侯殿下所体现的真德》",
        "name_en": "The Portrait of True Merit in the Person of His Serene Highness the Elector Palatine",
        "anchor": "s4-archive-rapparini-eulogy-20261017",
    },
    {
        "candidate": "cand-2515",
        "group": "archive-group-80d625037359",
        "type": "archive",
        "ku_id": "units/archives/de-bello-belgico",
        "card_rel": "04-knowledge/units/archives/de-bello-belgico.md",
        "name_zh": "《比利时战争》",
        "name_en": "The Belgian War",
        "anchor": "s4-archive-de-bello-belgico-20261017",
    },
    {
        "candidate": "cand-2514",
        "group": "new-person:famiano-strada-9d61d3fbf9",
        "type": "person",
        "ku_id": "units/persons/famiano-strada",
        "card_rel": "04-knowledge/units/persons/famiano-strada.md",
        "name_zh": "法比亚诺·斯特拉达",
        "name_en": "Famiano Strada",
        "anchor": "s4-person-famiano-strada-20261017",
    },
)

RAPPARINI_SOURCE = {
    "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
    "location": "第10章脚注1，印刷页282；OCR L520；PDF物理页11",
    "span": "OCR line 520; printed page 282; PDF physical page 11",
    "quote": "1 I am most grateful to Dr Alessandro Bettagno for indicating to me the manuscripts of Rapparini which were published in Dusseldorf in 1958. His Le Portrait du Vrai Mérité dans la personne serenissime de Monseigneur l’Electeur Palatin gives a fairly hill account of Johann Wilhelm’s patronage, but as the eulogy was written in 1709 there are naturally no references to Pellegrini. The extracts I have quoted can be found on pages 14, 18, 75, 83, 81 and 69.",
    "summary": "Haskell称Rapparini文稿于1958年在Dusseldorf出版，并称题名所指颂词写于1709年、论述Johann Wilhelm的赞助且不涉及Pellegrini；所引文本未独立查阅。既有S2记录依据PDF物理页11校正题名Mérité为Mérite、将OCR hill校为full，本次沿用而未重新校勘。",
}

DE_BELLO_SOURCE = {
    "file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
    "location": "第5章，印刷页137；OCR L72–73；PDF物理页22",
    "span": "OCR lines 72–73; printed page 137; PDF physical page 22",
    "quote": "In 1647, for instance, he was collaborating with Jan Miel, Giacomo Borgognone and others on the illustration of the second volume of Famiano Strada’s De Bello Belgico, a celebration of Alessandro Farnese’s campaigns on behalf of the Spaniards in the Low\nCountries;",
    "summary": "Haskell称1647年Cerquozzi与Jan Miel、Giacomo Borgognone及其他艺术家合作为De Bello Belgico第二卷作插图，并将该卷描述为颂扬Alessandro Farnese代表西班牙在Low Countries的战事；1647是插图合作年份，不据此推作出版年。",
}


def make_sources(rows: tuple[dict[str, str], ...]) -> list[dict[str, object]]:
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
        for item in rows
    ]


def make_frontmatter(item: dict[str, str], sources: tuple[dict[str, str], ...], sub_type: str | None = None) -> str:
    data: dict[str, object] = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": item["type"],
        "evidence_status": "source_backed",
        "sources": make_sources(sources),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}",
    }
    if sub_type:
        data["sub_type"] = sub_type
    dumped = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{dumped}---\n"


def card_rapparini(item: dict[str, str]) -> str:
    fm = make_frontmatter(item, (RAPPARINI_SOURCE,), "eulogy")
    note = "[第10章脚注1 p.282](../../../02-sources/02-Markdown/10_CHP-10_intro.md#L520)"
    person = "[Giorgio Maria Rapparini人物卡](../persons/giorgio-maria-rapparini.md)"
    return f"""{fm}
## 内容

### 描述

**中文：** 本卡记录哈斯克尔第10章脚注中所引Rapparini颂词 *Le Portrait du Vrai Mérite dans la personne serenissime de Monseigneur l’Electeur Palatin*。哈斯克尔称该颂词写于1709年，并称Rapparini文稿于1958年在Dusseldorf出版；本卡不指定具体手稿、出版者或印本，也未独立查阅该文献。中文与英文题名为工作译名。{note}

**English:** This card records the Rapparini eulogy cited in Haskell’s chapter 10 footnote, *Le Portrait du Vrai Mérite dans la personne serenissime de Monseigneur l’Electeur Palatin*. Haskell dates the eulogy to 1709 and says that Rapparini’s manuscripts were published in Dusseldorf in 1958. This card does not identify a particular manuscript, publisher, or printed copy; the text has not been independently consulted. The Chinese and English display titles are working translations. {note}

### 文献身份与书目著录

- **原题名：** *Le Portrait du Vrai Mérite dans la personne serenissime de Monseigneur l’Electeur Palatin*。既有S2校勘记录依据PDF物理页11将OCR `Mérité`校为`Mérite`；本次沿用，不表示重新校勘扫描页。
- **中文工作译名：** 《普法尔茨选侯殿下所体现的真德》；不声称为正式中文题名。
- **英文工作译名：** *The Portrait of True Merit in the Person of His Serene Highness the Elector Palatine*；不声称为正式英文题名。
- **文献类型：** 哈斯克尔称其为颂词（eulogy）；该文稿被纳入Rapparini文稿的出版语境。
- **书内著录信息：** 哈斯克尔称颂词写于1709年，并称Rapparini文稿于Dusseldorf 1958年出版；所引页码为14、18、75、83、81、69。书内未在该注中给出出版者或独立卷册信息。
- **相关对象：** 哈斯克尔将该颂词与[Giorgio Maria Rapparini人物卡](../persons/giorgio-maria-rapparini.md)相联系；此身份入口不代替S6正式作者关系裁决。
- **阅读状态：** 本项目核对的是哈斯克尔脚注及S2既有校勘记录；颂词及1958年出版物未独立查阅。

## 关系与证据

当前没有正式关系。`st-chp10-notes-p282n1-eulogy-1709-no-pellegrini`记录哈斯克尔所述Rapparini与颂词的关系，留待S6审查；`st-chp10-notes-p282n1-portrait-patronage-account`记录作者对颂词内容范围的评价，不视作独立内容核验。
"""


def card_de_bello(item: dict[str, str]) -> str:
    fm = make_frontmatter(item, (DE_BELLO_SOURCE,), "book")
    source = "[第5章 p.137](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md#L72)"
    strada = "[Famiano Strada人物卡](../persons/famiano-strada.md)"
    cerquozzi = "[Michelangelo Cerquozzi人物卡](../persons/michelangelo-cerquozzi.md)"
    miel = "[Jan Miel人物卡](../persons/jan-miel.md)"
    borgognone = "[Giacomo Borgognone / Jacques Courtois人物卡](../persons/jacques-courtois.md)"
    return f"""{fm}
## 内容

### 描述

**中文：** 本卡记录哈斯克尔以书名 *De Bello Belgico* 提及的书籍。第5章p.137具体谈到第二卷，并称1647年{cerquozzi}与{miel}、{borgognone}及其他艺术家合作为该卷作插图；1647是书中所述的合作时间，不是本卡推定的出版年份。哈斯克尔称该卷描写Alessandro Farnese代表西班牙在Low Countries的战事。{source}

**English:** This card records the book Haskell names as *De Bello Belgico*. On page 137, chapter 5 discusses its second volume and says that in 1647 {cerquozzi} collaborated with {miel}, {borgognone}, and other artists on its illustrations. The year 1647 is the reported date of this collaboration, not an inferred publication year. Haskell describes the volume as a celebration of Alessandro Farnese’s campaigns on behalf of Spain in the Low Countries. {source}

### 文献身份与版本边界

- **原题名：** *De Bello Belgico*。
- **中文工作译名：** 《比利时战争》；仅作项目展示名，不声称是正式中文书名。
- **英文工作译名：** *The Belgian War*；仅作项目展示名。
- **文献类型与粒度：** 书籍；本卡记录书名层级身份。第5章提到第二卷，但本段未给出该书的出版地、出版者、版次或出版年；不把插图合作年1647写成出版年。
- **责任者记载：** Haskell称其为Famiano Strada之书，身份入口见{strada}；该关系候选留待S6，不表示本项目独立查阅或核实作者归属。
- **书内语境：** 第5章以Cerquozzi的合作为例，提到Jan Miel、Giacomo Borgognone及未具名的其他艺术家参与第二卷插图。姓名链接仅作身份入口，具体角色候选仍待S6。

## 关系与证据

当前没有正式关系。以下S2关系候选全部留待S6：`st-chp5-p137-de-bello-farnese-campaigns`、`st-chp5-p137-miel-borgognone-strada-collaboration`、`st-chp5-p137-miel-contributed-to-de-bello-illustrations`、`st-chp5-p137-borgognone-contributed-to-de-bello-illustrations`、`st-chp5-p137-unnamed-artists-contributed-to-de-bello-illustrations`、`st-chp5-p137-de-bello-authored-by-famiano-strada`。相关事件端点`cand-11927`和未具名艺术家组`cand-11930`仍为S3未决，不据此猜造实体或正式边。
"""


def card_strada(item: dict[str, str]) -> str:
    fm = make_frontmatter(item, (DE_BELLO_SOURCE,))
    archive = "[De Bello Belgico文献卡](../archives/de-bello-belgico.md)"
    return f"""{fm}
## 内容

### 描述

**中文：** 本卡记录哈斯克尔以全名提及的Famiano Strada。第5章称 *De Bello Belgico* 为Strada之书；该段特别讨论第二卷及其插图合作。这里只登记来源中可识别的人物身份，不补充生卒、职务或其他传记事实。{archive}

**English:** This card records Famiano Strada, named in full by Haskell. Chapter 5 calls *De Bello Belgico* Strada’s book and discusses the second volume and its illustration collaborators. This unit records only the identifiable person in the source and adds no dates, offices, or other biographical facts. {archive}

### 姓名

- **原文姓名：** Famiano Strada。
- **中文工作音译：** 法比亚诺·斯特拉达；本轮未核对权威中文译名。

## 关系与证据

当前没有正式关系。`st-chp5-p137-de-bello-authored-by-famiano-strada`记录哈斯克尔的书内归属陈述，留待S6审查；相关文献身份入口见{archive}。
"""


BUILDERS = {
    "cand-2108": ((RAPPARINI_SOURCE,), card_rapparini),
    "cand-2515": ((DE_BELLO_SOURCE,), card_de_bello),
    "cand-2514": ((DE_BELLO_SOURCE,), card_strada),
}


def insert_accepted(text: str, card_rel: str) -> str:
    lines = text.splitlines()
    assert f"- {card_rel}" not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Rapparini's eulogy, De Bello Belgico, and Famiano Strada in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    statement_rows = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    cards: list[tuple[dict[str, str], str, Path]] = []
    direct_count = 0
    relation_count = 0
    expected_ids = {
        "cand-2108": {
            "st-chp10-notes-p282n1-eulogy-1709-no-pellegrini",
            "st-chp10-notes-p282n1-portrait-patronage-account",
        },
        "cand-2515": {
            "st-chp5-p137-de-bello-farnese-campaigns",
            "st-chp5-p137-miel-borgognone-strada-collaboration",
            "st-chp5-p137-miel-contributed-to-de-bello-illustrations",
            "st-chp5-p137-borgognone-contributed-to-de-bello-illustrations",
            "st-chp5-p137-unnamed-artists-contributed-to-de-bello-illustrations",
            "st-chp5-p137-de-bello-authored-by-famiano-strada",
        },
        "cand-2514": {"st-chp5-p137-de-bello-authored-by-famiano-strada"},
    }

    for item in ITEMS:
        cid = item["candidate"]
        candidate = candidate_by_id[cid]
        row = decisions[cid]
        card_path = ROOT / item["card_rel"]
        assert candidate.get("suggested_type") == item["type"], (cid, candidate.get("suggested_type"))
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row.get("decision"), row.get("ku_id"))
        assert sync.get_group(row.get("resolution_note", "")) == item["group"], (cid, row.get("resolution_note"))
        group_members = {
            other["candidate_id"]
            for other in alignments
            if other.get("candidate_id") and not other.get("external_source")
            and other.get("decision") == "new"
            and sync.get_group(other.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        assert not card_path.exists() and item["card_rel"] not in accepted_text
        assert not any(entry.get("ku_id") == item["ku_id"] or entry.get("card_path") == item["card_rel"] for entry in manifest)
        assert not any(
            entry.get("type") == item["type"]
            and item["name_en"].casefold() == entry.get("name_en", "").casefold()
            for entry in manifest
        ), item["name_en"]

        for source in BUILDERS[cid][0]:
            source_text = " ".join((ROOT / source["file"]).read_text(encoding="utf-8-sig").split())
            assert " ".join(source["quote"].split()) in source_text, (cid, source["file"], source["span"])

        direct = [
            statement for statement in statement_rows
            if statement.get("subject_candidate_id") == cid or statement.get("object_candidate_id") == cid
        ]
        assert {statement["statement_id"] for statement in direct} == expected_ids[cid], cid
        relations = [
            statement for statement in direct
            if statement.get("qualifiers", {}).get("relation_candidate") is True
        ]
        if cid == "cand-2108":
            assert len(relations) == 1
        else:
            assert len(relations) == len(direct)
        direct_count += len(direct)
        relation_count += len(relations)

        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration: {item['group']} maps to {item['ku_id']}; "
            "this records source-local identity only; related S2 claims remain for S6."
        )
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": item["type"],
            "canonical_name": item["name_zh"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
        card = BUILDERS[cid][1](item)
        fm_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert fm_match and isinstance(yaml.safe_load(fm_match.group(1)), dict), (cid, "frontmatter invalid")
        cards.append((item, card, card_path))

    assert decisions["cand-11927"].get("decision") == "undecided" and not decisions["cand-11927"].get("ku_id")
    assert decisions["cand-11930"].get("decision") == "undecided" and not decisions["cand-11930"].get("ku_id")
    assert decisions["cand-2107"].get("ku_id") == "units/persons/giorgio-maria-rapparini"
    assert decisions["cand-1662"].get("ku_id") == "units/persons/jan-miel"
    assert decisions["cand-0399"].get("ku_id") == "units/persons/jacques-courtois"
    assert decisions["cand-3084"].get("ku_id") == "units/persons/michelangelo-cerquozzi"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS.read_text(encoding="utf-8-sig").rstrip()
    accepted_next = accepted_text
    for item, _, _ in cards:
        accepted_next = insert_accepted(accepted_next, item["card_rel"])

    process_append = f"""

<a id="s4-archive-rapparini-de-bello-20261017"></a>

### S4 archive 与直接人物端点：Rapparini颂词、De Bello Belgico、Famiano Strada（{DATE}）

- `{ITEMS[0]['candidate']}`（`{ITEMS[0]['group']}`）登记至[{ITEMS[0]['name_zh']}](../../../{ITEMS[0]['card_rel']})。第10章p.282注1给出题名，并称该颂词写于1709年、Rapparini文稿于Dusseldorf 1958年出版。既有S2记录已将扫描读作`Mérité`校为`Mérite`、将`hill`校为`full`；本次沿用该S2校勘，不声称重读文献或扫描。Rapparini人物端点已复用{decisions['cand-2107']['ku_id']}。
- `{ITEMS[1]['candidate']}`（`{ITEMS[1]['group']}`）登记至[{ITEMS[1]['name_zh']}](../../../{ITEMS[1]['card_rel']})，仅到书名层级。第5章p.137称第二卷，并叙述1647年Cerquozzi与Jan Miel、Giacomo Borgognone等人为该卷作插图；1647不作出版年。Haskell明确称书为Famiano Strada之作，因此其S3新人物端点`{ITEMS[2]['candidate']}`同步登记至[{ITEMS[2]['name_zh']}](../../../{ITEMS[2]['card_rel']})。Miel、Borgognone和Cerquozzi端点已分别映射既有卡。
- De Bello组的6条S2关系候选均留待S6；campaign事件端点`cand-11927`和未具名艺术家组`cand-11930`在S3为`undecided`，本次未推定或创建KU。Rapparini颂词的1条关系候选及Strada著作归属候选也留待S6；没有新增正式边或S5补足。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = process_text + process_append
    result_append = f"""

### S4 archive / person：Rapparini颂词与De Bello Belgico（{DATE}）

`cand-2108`登记为Rapparini颂词的书内文献身份；`cand-2515`登记为书名 *De Bello Belgico*，`cand-2514`登记Famiano Strada人物端点。两组文献未外查或独立阅读。De Bello的6条关系候选及Rapparini、Strada关联候选留待S6；`cand-11927`、`cand-11930`继续保留S3未决。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_text.rstrip() + result_append

    if args.dry_run:
        print("dry-run passed: " + "; ".join(f"{item['candidate']} ({item['group']}) -> {item['ku_id']}" for item in ITEMS))
        print(
            f"verified_cards={len(cards)}; direct_statements={direct_count}; "
            f"pending_relation_candidates={relation_count}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("undecided endpoints cand-11927 and cand-11930 preserved; no S5 or S6 rows will be written")
        print("no files changed")
        return 0

    for _, card, card_path in cards:
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    ACCEPTED.write_text(accepted_next, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(ITEMS)}; candidates={len(ITEMS)}; direct_statements={direct_count}; "
        f"pending_relation_candidates={relation_count}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
