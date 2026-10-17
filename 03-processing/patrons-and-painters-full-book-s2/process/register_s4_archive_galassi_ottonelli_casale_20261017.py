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
        "candidate": "cand-4974",
        "group": "archive-group-0126bbcbcfbc",
        "type": "archive",
        "ku_id": "units/archives/storia-segreta-stile-gesuiti-1951",
        "card_rel": "04-knowledge/units/archives/storia-segreta-stile-gesuiti-1951.md",
        "name_zh": "《耶稣会风格秘史》",
        "name_en": "Secret History of Jesuit Style",
        "anchor": "s4-archive-galassi-paluzzi-book-20261017",
    },
    {
        "candidate": "cand-4979",
        "group": "archive-group-e399514e8ce5",
        "type": "archive",
        "ku_id": "units/archives/ottonelli-cortona-treatise-1652",
        "card_rel": "04-knowledge/units/archives/ottonelli-cortona-treatise-1652.md",
        "name_zh": "《绘画与雕塑论：其用途与滥用》",
        "name_en": "Treatise on Painting and Sculpture, on Their Use and Abuse",
        "anchor": "s4-archive-ottonelli-cortona-1652-20261017",
    },
    {
        "candidate": "cand-10937",
        "group": "new-person:casale-vittorio-9476a988c6",
        "type": "person",
        "ku_id": "units/persons/vittorio-casale",
        "card_rel": "04-knowledge/units/persons/vittorio-casale.md",
        "name_zh": "维托里奥·卡萨莱",
        "name_en": "Vittorio Casale",
        "anchor": "s4-person-vittorio-casale-20261017",
    },
)

GALASSI_SOURCES = (
    {
        "file": "02-sources/02-Markdown/03_CHP-3_intro.md",
        "location": "第3章开篇脚注，印刷页i；OCR L8；PDF物理页1",
        "span": "OCR line 8; printed page i; PDF physical page 1",
        "quote": "1 For the whole controversy about the Jesuits and the arts see Galassi Paluzzi, 1951, who, however, does not refer to the book mentioned in the next note nor to other passages to the same effect dating from before the nineteenth century.",
        "summary": "Haskell将Galassi Paluzzi 1951年研究列为耶稣会与艺术争议的参考，并称该书未涉及下一注所引著作或19世纪以前的类似论述；这是Haskell的书目评价，未由本项目独立核查。",
        "label": "第3章开篇脚注",
    },
    {
        "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "location": "第21章书目，印刷页423；OCR L506",
        "span": "OCR line 506; printed page 423",
        "quote": "Galassi Paluzzi, C.: Storia segreta dello stile dei Gesuiti, Roma 1951.",
        "summary": "书目将作者著录为Galassi Paluzzi, C.，题名为Storia segreta dello stile dei Gesuiti，出版项记Roma 1951；书籍未独立查阅。",
        "label": "第21章书目，p.423",
    },
)

OTTONELLI_SOURCES = (
    {
        "file": "02-sources/02-Markdown/03_CHP-3_sec_i.md",
        "location": "第3章，印刷页64；OCR L21",
        "span": "OCR line 21; printed page 64",
        "quote": "It was a Jesuit, Padre Ottonefli, who pressed Pietro da Cortona’s claims on the Barberini when they were having their palace decorated and who later wrote a highly casuistical treatise in collaboration with the artist on the persuasive possibilities of painting.5",
        "summary": "Haskell称耶稣会士Padre Ottonefli曾与Pietro da Cortona合作撰写绘画说服力论著；OCR姓名形式保留，不据此扩充未决的Ottonelli人物身份。",
        "label": "第3章 p.64",
    },
    {
        "file": "02-sources/02-Markdown/03_CHP-3_sec_i.md",
        "location": "第3章注5，印刷页64；OCR L40",
        "span": "OCR line 40; printed page 64",
        "quote": "5 Odomenigio Lelonotti da Fanano e Britio Prenetteri [Gio. Dom. Ottonelli e Pietro da Cortona]: Trattato.",
        "summary": "注5以方括号将两个假名与Gio. Dom. Ottonelli、Pietro da Cortona对应，并简引Trattato；该括号是Haskell书内识别，不是独立作者鉴定。",
        "label": "第3章注5，p.64",
    },
    {
        "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "location": "第21章书目，印刷页432；OCR L904–905",
        "span": "OCR lines 904–905; printed page 432",
        "quote": "[Ottonelli, Gio. Dom. S. J. e Pietro da Cortona]—Odomenigio Lelonotti da Fanano e Britio\nPrenetteri: Trattato della Pittura e Scultura, uso ed abuso loro, composto da un Theologo e da un Pittore, per offerirlo ai Sigg. Accademici del Disegno di Firenze, Firenze 1652.",
        "summary": "Haskell书目列出带方括号署名及假名署名的1652年条目，出版地记Firenze；记录限于书内著录，未独立查阅该版。",
        "label": "第21章书目，p.432，1652年条目",
    },
    {
        "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "location": "第20章，印刷页400；OCR L48–49；PDF物理页5",
        "span": "OCR lines 48–49; printed page 400; PDF physical page 5",
        "quote": "Finally, an edition by Vittorio Casale of the treatise on painting and sculpture jointly written by the Jesuit father Ottonelli and by Pietro da Cortona has examined the parts contributed by the theologian and the artist to this strange publication,3 and Casale’s subsequent discovery of the censor’s comments on it at last gives us some indication of the way in which these issues were discussed in Jesuit circles.4",
        "summary": "Haskell另述Casale版及审查意见发现；这说明同一论著在后续章节的讨论语境，但不证明本书实际查阅过1652年版或审查意见。",
        "label": "第20章 p.400",
    },
    {
        "file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "location": "第20章注3，印刷页400；OCR L227；PDF物理页5",
        "span": "OCR line 227; printed page 400; PDF physical page 5",
        "quote": "3 Ottonelli and Berrettini.",
        "summary": "第20章注3以Ottonelli and Berrettini作短引；该短引不单独提供题名或版本信息。",
        "label": "第20章注3，p.400",
    },
    {
        "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "location": "第21章书目，印刷页432；OCR L906–907",
        "span": "OCR lines 906–907; printed page 432",
        "quote": "Ottonelli, Gio. Dom.—Berrettini, P.: Trattato della Pittura e Scultura, (a cura di Vittorio\nCasale), Treviso 1973.",
        "summary": "书目另列Casale编校的Treviso 1973年版；S3候选cand-11160仍为未决身份/粒度，本次不并入1652年版。",
        "label": "第21章书目，p.432，1973年条目",
    },
)

CASALE_SOURCES = (
    OTTONELLI_SOURCES[3],
    OTTONELLI_SOURCES[5],
)


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


def frontmatter(item: dict[str, str], sources: tuple[dict[str, str], ...]) -> str:
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
    if item["candidate"] in {"cand-4974", "cand-4979"}:
        data["sub_type"] = "book"
    dumped = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{dumped}---\n"


def card_galassi(item: dict[str, str]) -> str:
    fm = frontmatter(item, GALASSI_SOURCES)
    ch3 = "[第3章开篇脚注](../../../02-sources/02-Markdown/03_CHP-3_intro.md#L8)"
    bib = "[第21章书目 p.423](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L506)"
    return f"""{fm}
## 内容

### 描述

**中文：** 本卡记录哈斯克尔在书目中列出的意大利语书籍 *Storia segreta dello stile dei Gesuiti*。第3章开篇脚注将其作为讨论耶稣会与艺术争议的参考，并称它没有涉及下一注所引著作及19世纪以前的类似论述；后一判断是哈斯克尔的书目评价，本项目未独立核查。中文与英文展示题名为工作译名。{ch3}；{bib}

**English:** This card records the Italian-titled book *Storia segreta dello stile dei Gesuiti* listed in Haskell’s bibliography. The opening note to chapter 3 cites it for the controversy about the Jesuits and the arts and says that it does not refer to the work in the following note or to similar passages before the nineteenth century. That assessment is Haskell’s bibliographic report and has not been independently checked here. The Chinese and English display titles are working translations. {ch3}; {bib}

### 文献身份与书目著录

- **原题名：** *Storia segreta dello stile dei Gesuiti*。
- **中文工作译名：** 《耶稣会风格秘史》；无通行题名依据，不作为正式中文出版题名。
- **英文工作译名：** *Secret History of Jesuit Style*；不作为正式英文出版题名。
- **文献类型：** Haskell书目所列书籍；出版者未见于本书该条目。
- **责任者著录：** Galassi Paluzzi, C.（按书目原样保留缩写，不扩展姓名）。
- **出版项：** Roma，1951（按书目原文）。
- **阅读状态：** Haskell引用和书目条目已核对；所引著作本身未独立查阅。

## 关系与证据

当前没有正式关系。S2候选 `st-chp3-intro-l7-9-galassi-citation` 记录哈斯克尔书中的书目引用；`st-chp3-intro-l7-9-galassi-coverage-assessment` 记录其对该书覆盖范围的评价。两者均留待S6，不把引用或作者评价转成经外部核实的事实。
"""


def card_ottonelli(item: dict[str, str]) -> str:
    fm = frontmatter(item, OTTONELLI_SOURCES)
    sec = "[第3章正文 p.64](../../../02-sources/02-Markdown/03_CHP-3_sec_i.md#L21)"
    note = "[第3章注5 p.64](../../../02-sources/02-Markdown/03_CHP-3_sec_i.md#L40)"
    bib1652 = "[第21章书目 p.432，1652年条目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L904)"
    ch20 = "[第20章 p.400](../../../02-sources/02-Markdown/20_CHP-20Postscript.md#L48)"
    bib1973 = "[第21章书目 p.432，1973年条目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L906)"
    pietro = "[Pietro da Cortona 人物卡](../persons/pietro-da-cortona.md)"
    return f"""{fm}
## 内容

### 描述

**中文：** 本卡记录哈斯克尔第21章书目所列、出版项记为Firenze 1652的《绘画与雕塑论》版本。书目同时保留原文假名署名及方括号内的责任者归属；第3章正文和注5也将这部论著与Ottonelli、Pietro da Cortona联系起来。上述责任者与合作关系均为哈斯克尔书内记载，未独立核验原版或作者身份。中文和英文题名为工作译名。{sec}；{note}；{bib1652}

**English:** This card records the edition of the *Trattato della Pittura e Scultura* listed in Haskell’s chapter 21 bibliography with the publication statement Firenze 1652. The entry preserves a pseudonymous byline and the bracketed attribution printed by Haskell; chapter 3 also connects the treatise with Ottonelli and Pietro da Cortona. These attributions and the collaboration are Haskell’s reports; neither the original edition nor the authorship has been independently verified. The Chinese and English display titles are working translations. {sec}; {note}; {bib1652}

### 文献身份与版本边界

- **原题名：** *Trattato della Pittura e Scultura, uso ed abuso loro*；书目续列副题 *composto da un Theologo e da un Pittore, per offerirlo ai Sigg. Accademici del Disegno di Firenze*。原文按哈斯克尔书目保留，含原书拼写。
- **书目署名：** 哈斯克尔印作 `[Ottonelli, Gio. Dom. S. J. e Pietro da Cortona]`，并列假名署名 `Odomenigio Lelonotti da Fanano e Britio Prenetteri`。这是书目中的署名与方括号识别，不作为独立作者鉴定；Ottonelli 候选 `cand-1800` 在S3仍为未决。{pietro}仅作为已对齐人物的身份入口，不表示正式作者关系。
- **文献类型与版本：** 书籍；本条具体指哈斯克尔书目所列Firenze 1652版本。出版者未见于该条目。
- **中文工作译名：** 《绘画与雕塑论：其用途与滥用》；不声称是正式中文书名。
- **英文工作译名：** *Treatise on Painting and Sculpture, on Their Use and Abuse*；不声称是正式英文书名。
- **与后出版本的区分：** 第21章紧邻另列由Vittorio Casale编校、Treviso 1973年出版的书目条目。其候选 `cand-11160` 的S3身份/粒度仍未决，本卡只登记1652年条目；不把两条书目并为同一版次。{bib1973}
- **阅读状态：** Haskell正文、脚注及书目条目已核对；1652年版、1973年版和审查意见均未独立查阅。第20章的后续章节叙述不证明这里登记的1652年版本已被阅读。{ch20}

## 关系与证据

当前没有正式关系。以下S2关系候选留待S6：`st-chp3-seci-l16-24-ottonelli-coauthored-treatise`、`st-chp3-seci-l35-43-trattato-cortona-bracket-identification`、`st-chp3-seci-l35-43-trattato-ottonelli-bracket-identification`、`st-chp20-p400-casale-ottonelli-treatise-and-censor`。哈斯克尔的署名、括号识别及后续版本叙述均不在本次写成正式边。
"""


def card_casale(item: dict[str, str]) -> str:
    fm = frontmatter(item, CASALE_SOURCES)
    ch20 = "[第20章 p.400](../../../02-sources/02-Markdown/20_CHP-20Postscript.md#L48)"
    bib = "[第21章书目 p.432](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L906)"
    archive = "[1652年条目卡](../archives/ottonelli-cortona-treatise-1652.md)"
    return f"""{fm}
## 内容

### 描述

**中文：** 本卡记录哈斯克尔在第20章和第21章书目中以全名提及的Vittorio Casale。第20章称有一部Casale版论著并报告其发现审查意见；第21章将Casale列在Treviso 1973年版的编校信息中。这些是哈斯克尔的书内记载，未独立核查。中文姓名为工作音译。{ch20}；{bib}

**English:** This card records Vittorio Casale, named in full in Haskell’s chapter 20 discussion and chapter 21 bibliography. Chapter 20 reports an edition associated with Casale and a subsequent discovery of censor’s comments; chapter 21 lists Casale in the editorial statement for a 1973 Treviso edition. These are reports in Haskell’s book and have not been independently checked. The Chinese name is a working transliteration. {ch20}; {bib}

### 姓名与书内提及

- **原文姓名：** Vittorio Casale。
- **中文工作音译：** 维托里奥·卡萨莱；无权威中文姓名记录已在本轮核实。
- **书内提及范围：** 哈斯克尔将其与绘画、雕塑论著的后出版本和审查意见发现联系起来；相关版次与文献关系仍由各自S3候选记录，本卡不把这些叙述提升为外部核实的传记事实。{ch20}；{bib}

## 关系与证据

当前没有正式关系。S2候选 `st-chp20-p400-casale-ottonelli-treatise-and-censor` 留待S6审查。相应1973年版archive候选 `cand-11160` 仍为S3未决，本卡不代替该版本的身份裁决。{archive}
"""


BUILDERS = {
    "cand-4974": (GALASSI_SOURCES, card_galassi),
    "cand-4979": (OTTONELLI_SOURCES, card_ottonelli),
    "cand-10937": (CASALE_SOURCES, card_casale),
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
    parser = argparse.ArgumentParser(description="Register two source-local archive groups and the direct Casale person endpoint in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED.read_text(encoding="utf-8-sig")
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"

    statement_rows = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    cards: list[tuple[dict[str, str], str, Path]] = []
    mapped_count = 0

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
            and item["name_en"].casefold() == (entry.get("name_en", "").casefold())
            for entry in manifest
        ), ("same name already registered", item["name_en"])

        for source in BUILDERS[cid][0]:
            source_text = " ".join((ROOT / source["file"]).read_text(encoding="utf-8-sig").split())
            assert " ".join(source["quote"].split()) in source_text, (cid, source["file"], source["span"])

        direct = [
            statement for statement in statement_rows
            if statement.get("subject_candidate_id") == cid or statement.get("object_candidate_id") == cid
        ]
        relation_candidates = [
            statement for statement in direct
            if statement.get("qualifiers", {}).get("relation_candidate") is True
        ]
        if cid == "cand-4974":
            assert {row["statement_id"] for row in direct} == {
                "st-chp3-intro-l7-9-galassi-citation",
                "st-chp3-intro-l7-9-galassi-coverage-assessment",
                "st-chp21-bib-l498-536-entry-06",
            }
            assert len(relation_candidates) == 2
        elif cid == "cand-4979":
            assert {row["statement_id"] for row in direct} == {
                "st-chp3-seci-l16-24-ottonelli-coauthored-treatise",
                "st-chp3-seci-l35-43-trattato-cortona-bracket-identification",
                "st-chp3-seci-l35-43-trattato-ottonelli-bracket-identification",
                "st-chp20-p400-casale-ottonelli-treatise-and-censor",
                "st-chp20-p400-n03-citation",
                "st-chp21-bib-l883-926-entry-15",
            }
            assert len(relation_candidates) == 4
        else:
            assert {row["statement_id"] for row in direct} == {
                "st-chp20-p400-casale-ottonelli-treatise-and-censor",
            }
            assert len(relation_candidates) == 1

        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration: {item['group']} maps to {item['ku_id']}; "
            "mapping records source-local identity only, not an S6 formal relation or independent external verification."
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
        mapped_count += len(direct)

    # Keep the 1973 edition candidate and the partial Ottonelli person candidate in their existing S3 states.
    assert decisions["cand-11160"].get("decision") == "undecided" and not decisions["cand-11160"].get("ku_id")
    assert decisions["cand-1800"].get("decision") == "undecided" and not decisions["cand-1800"].get("ku_id")

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

<a id="s4-archive-galassi-ottonelli-casale-20261017"></a>

### S4 archive 与直接人物端点：Galassi Paluzzi、Ottonelli–Pietro da Cortona、Vittorio Casale（{DATE}）

- `{ITEMS[0]['candidate']}`（`{ITEMS[0]['group']}`）登记至[{ITEMS[0]['name_zh']}](../../../{ITEMS[0]['card_rel']})。第3章开篇注1引用Galassi Paluzzi, 1951，并报告其书目覆盖范围；第21章p.423列完整原题、作者缩写和Roma 1951书目项。书籍及评价未独立查阅或核验，未扩展作者姓名、出版者或著作内容。
- `{ITEMS[1]['candidate']}`（`{ITEMS[1]['group']}`）登记至[{ITEMS[1]['name_zh']}](../../../{ITEMS[1]['card_rel']})，对象粒度限定为第21章p.432所列Firenze 1652版本。第3章p.64正文和注5记录合作论著及括号署名；原书目假名、方括号责任者和完整题名照录。第20章p.400的后出版本叙述保留为书内语境，不当作本项目读过1652年版或审查意见的证据。
- `{ITEMS[2]['candidate']}`（`{ITEMS[2]['group']}`）登记至[维托里奥·卡萨莱人物卡](../../../{ITEMS[2]['card_rel']})。第20章p.400及第21章p.432明确以Vittorio Casale全名提及其与后出版本／审查意见的关联；仅登记书内可识别人物身份，不扩展传记。
- 1652年版本与第21章另列的Treviso 1973年版分开处理。`cand-11160` 的S3状态为 `undecided`，本次未写入KU或关系。Ottonelli人物候选 `cand-1800` 因姓名形式不足仍为 `undecided`；Pietro da Cortona复用既有`units/persons/pietro-da-cortona`。候选`cand-10938`所指未具名审查意见文献仍未决，不与书本身合并。
- Galassi组2条、Ottonelli论著组4条、Casale人物组1条直接S2关系候选均留待S6；本次没有新增正式关系或S5补足。登记依据只限Haskell书内段落、脚注和书目。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = process_text + process_append
    result_append = f"""

### S4 archive / person：Galassi、Ottonelli–Pietro da Cortona 与 Casale（{DATE}）

`cand-4974`映射至Galassi Paluzzi书目项，`cand-4979`映射至Haskell所列1652年论著版本；`cand-10937`映射至书内明确全名人物Vittorio Casale。1652与1973年书目版本保持分立，`cand-11160`继续待决；Ottonelli人物`cand-1800`及未具名审查意见文献`cand-10938`也未借本次登记消解。对应书内关系候选均留待S6，未新增S5事实。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_text.rstrip() + result_append
    for item, _, _ in cards:
        result_next = result_next.replace(
            "`cand-11160`继续待决", "`cand-11160`继续待决", 1
        )

    if args.dry_run:
        print(
            "dry-run passed: "
            + "; ".join(f"{item['candidate']} ({item['group']}) -> {item['ku_id']}" for item in ITEMS)
        )
        print(
            f"verified_cards={len(cards)}; direct_statements={mapped_count}; "
            f"pending_relation_candidates=7; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("cand-11160 and cand-1800 remain undecided; no S5 or S6 rows will be written")
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
        f"applied: groups={len(ITEMS)}; candidates={len(ITEMS)}; direct_statements={mapped_count}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
