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
        "candidate": "cand-4553",
        "group": "archive-group-3091943966c4",
        "ku_id": "units/archives/fraschetti-il-bernini-1900",
        "card_rel": "04-knowledge/units/archives/fraschetti-il-bernini-1900.md",
        "name_zh": "《贝尔尼尼》",
        "name_en": "Bernini",
        "sub_type": "book",
        "anchor": "s4-archive-fraschetti-il-bernini-1900-20261017",
    },
    {
        "candidate": "cand-4554",
        "group": "archive-group-fad1206fd041",
        "ku_id": "units/archives/este-resident-avviso-1633-01-08-bernini",
        "card_rel": "04-knowledge/units/archives/este-resident-avviso-1633-01-08-bernini.md",
        "name_zh": "罗马埃斯特使节关于贝尔尼尼的报告（1633年1月8日）",
        "name_en": "Avviso from the Este Resident in Rome on Bernini (8 January 1633)",
        "sub_type": "avviso",
        "anchor": "s4-archive-avviso-este-resident-1633-01-08-20261017",
    },
)

BOOK_SOURCES = (
    {
        "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
        "location": "第2章脚注1，印刷页37；OCR L167；PDF物理页18",
        "span": "OCR line 167; printed page 37; PDF physical page 18",
        "quote": "1 Fraschetti, p. 107, publishes an avviso from the Este Resident in Rome dated 8 January 1633 (Borghese died in October): ‘Il Cavalier Bernini di commissione del Papa ha fatto in marmo la testa de Cardinal Borghese che ha donato in ricompensa 500 zeahini et un diamante di 150 scudi.’",
        "summary": "Haskell以Fraschetti p.107为书目出处，称其刊有一则1633年1月8日罗马埃斯特使节报告，并给出意大利语引文；报告及Fraschetti相应页均未在本任务独立查阅。",
    },
    {
        "file": "02-sources/02-Markdown/01_CHP-1.md",
        "location": "第1章注1，印刷页17；OCR L700–701；PDF物理页16",
        "span": "OCR lines 700–701; printed page 17; PDF physical page 16",
        "quote": "A letter from Fulvio Testi to Conte Francesco Fontana published by Fraschetti (p. 108)",
        "summary": "Haskell在第1章指出Testi致Fontana的书信由Fraschetti刊出，并引第108页；书目同列Il Bernini，支撑该跨章书目身份对应。",
    },
    {
        "file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "location": "第5章注3，印刷页123；OCR L140；PDF物理页4",
        "span": "OCR line 140; printed page 123; PDF physical page 4",
        "quote": "3 Fraschetti, p. 71",
        "summary": "第5章另引Fraschetti第71页；该定位补充跨章引用证据，不证明本项目已查阅该页。",
    },
    {
        "file": "02-sources/02-Markdown/21_CHP-21Bibliography.md",
        "location": "第21章书目，印刷页422；OCR L493",
        "span": "OCR line 493; printed page 422",
        "quote": "Fraschetti, S.: Il Bernini, Milano 1900.",
        "summary": "书目将作者著录为Fraschetti, S.，题名Il Bernini，出版项Milano 1900；作者全名未由该条目给出。",
    },
)

AVVISO_SOURCE = {
    "file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    "location": "第2章脚注1，印刷页37；OCR L167；PDF物理页18",
    "span": "OCR line 167; printed page 37; PDF physical page 18",
    "quote": BOOK_SOURCES[0]["quote"],
    "summary": "Haskell称Fraschetti p.107刊出一则1633年1月8日罗马埃斯特使节报告，并引用其关于Bernini制作Cardinal Borghese大理石头像及酬赠的意大利语文字；原报告未直接查阅，枢机名字在注中只有姓氏。",
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


def make_frontmatter(item: dict[str, str], sources: tuple[dict[str, str], ...]) -> str:
    data = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": "archive",
        "sub_type": item["sub_type"],
        "evidence_status": "source_backed",
        "sources": make_sources(sources),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}",
    }
    dumped = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{dumped}---\n"


def card_book(item: dict[str, str]) -> str:
    fm = make_frontmatter(item, BOOK_SOURCES)
    p37 = "[第2章注1 p.37](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md#L167)"
    p17 = "[第1章注1 p.17](../../../02-sources/02-Markdown/01_CHP-1.md#L700)"
    p123 = "[第5章注3 p.123](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md#L140)"
    bib = "[第21章书目 p.422](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L493)"
    avviso = "[1633年埃斯特使节报告卡](este-resident-avviso-1633-01-08-bernini.md)"
    return f"""{fm}
## 内容

### 描述

**中文：** 本卡记录哈斯克尔书目所列S. Fraschetti著 *Il Bernini*（Milano 1900）。该书在第1、2、5章多次被引用，包括第2章注中所称刊载一则1633年埃斯特使节报告的第107页。书籍作者只以首字母著录；本卡不扩展Fraschetti全名，也不把引文内容提升为已独立查核。{p37}；{p17}；{p123}；{bib}

**English:** This card records S. Fraschetti’s *Il Bernini* (Milan, 1900), as listed in Haskell’s bibliography. The book is cited several times in chapters 1, 2, and 5, including page 107 in chapter 2, which Haskell identifies as the publication location for a 1633 notice from the Este resident. The author is listed only by an initial; this card does not expand Fraschetti’s name or treat the cited contents as independently checked. {p37}; {p17}; {p123}; {bib}

### 题名与书目著录

- **原题名：** *Il Bernini*。
- **中文工作译名：** 《贝尔尼尼》；沿用人名题名，不声称为正式中文书名。
- **英文展示名：** *Bernini*；保留原题核心词。
- **文献类型：** 书籍。
- **责任者著录：** Fraschetti, S.（按第21章书目保留首字母）；人物候选`cand-3519`身份未决，不扩展全名。
- **出版项：** Milano，1900；该书目条目未列出版者。
- **跨章引文：** 哈斯克尔在第1章注1引p.108说明Testi书信的刊布；第2章注1引p.107说明Avviso刊布；第5章注3引p.71；其他定位见S2对齐记录。上述均是哈斯克尔的引用位置，不表示本项目完整查读 *Il Bernini*。{p17}；{p37}；{p123}
- **相关对象：** 第2章所称Avviso另登记为{avviso}。这里的链接仅为身份入口；二者间不新增正式关系边。

## 关系与证据

当前没有本任务新增的正式关系。S2书目引用候选`st-chp1-secii-l659-n2-cites-fraschetti-passim`、`st-chp1-secii-p17-n1-fraschetti-p108`、`st-chp5-note-p123-n3-cites-fraschetti`留待S6复核；其余书目定位保留为来源依据。
"""


def card_avviso(item: dict[str, str]) -> str:
    fm = make_frontmatter(item, (AVVISO_SOURCE,))
    source = "[第2章注1 p.37](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md#L167)"
    fraschetti = "[Fraschetti《Il Bernini》书目卡](fraschetti-il-bernini-1900.md)"
    return f"""{fm}
## 内容

### 描述

**中文：** 本卡记录哈斯克尔第2章脚注所引的一则 *avviso*：其来源被称为罗马的埃斯特使节，日期为1633年1月8日。哈斯克尔称该报告由Fraschetti刊于第107页，并引述其关于Bernini奉教皇之命制作Cardinal Borghese大理石头像及酬赠的文字。原报告和Fraschetti第107页均未在本任务独立查阅；注中未给使节姓名、原档号，也未给枢机名字的首名。{source}

**English:** This card records an *avviso* cited in Haskell’s chapter 2 footnote. Haskell identifies its source as the Este resident in Rome and dates it 8 January 1633; he says that Fraschetti printed it on page 107. The quotation concerns Bernini making a marble head of Cardinal Borghese on the Pope’s commission and the reported recompense. Neither the original notice nor Fraschetti’s page 107 has been independently consulted here. Haskell gives no name for the resident, no archival reference, and no forename for the cardinal. {source}

### 文献身份与转引

- **题名：** 无正式题名见于本章；本卡标题是根据来源角色、内容与日期拟定的描述性名称。
- **文献类型：** *Avviso*（报告／消息文书），依哈斯克尔称谓。
- **日期：** 1633-01-08（按哈斯克尔注录）。
- **来源与刊录：** 哈斯克尔称其出自罗马埃斯特使节并由{fraschetti}第107页刊出；这是书内转引信息，不代表原件或刊本已直接查阅。
- **原文摘录：** 保留Haskell OCR所录 `500 zeahini` 拼写；本卡不依其他版本校改该词，也不推断收报人或文书保存处。
- **身份边界：** `Cardinal Borghese`仅按注中称谓记录，不指定名字；不把该文书与Bernini其他头像委托或付款记录合并。

## 关系与证据

当前没有正式关系记录。来源脚注称该Avviso刊于Fraschetti第107页，但S2尚未为候选`{ITEMS[1]['candidate']}`建立单独的`book-statements`主客体关系行；本次仅登记文书身份和原文定位，不将刊录关系写成正式边。后续S6若审此边，须回到{source}补齐可追溯的S2关系候选，再裁决刊录关系。
"""


BUILDERS = {
    "cand-4553": (BOOK_SOURCES, card_book),
    "cand-4554": ((AVVISO_SOURCE,), card_avviso),
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
    parser = argparse.ArgumentParser(description="Register Fraschetti's book and its cited Este resident avviso as separate S4 archive units.")
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
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert len(decisions) == len(candidate_by_id)
    assert decisions["cand-3519"].get("decision") == "undecided" and not decisions["cand-3519"].get("ku_id")

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    cards: list[tuple[dict[str, str], str, Path]] = []
    for item in ITEMS:
        cid = item["candidate"]
        row = decisions[cid]
        candidate = candidate_by_id[cid]
        card_path = ROOT / item["card_rel"]
        assert candidate.get("suggested_type") == "archive"
        assert row.get("decision") == "new" and not row.get("ku_id"), (cid, row.get("decision"), row.get("ku_id"))
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        group_members = {
            other["candidate_id"]
            for other in alignments
            if other.get("candidate_id") and not other.get("external_source")
            and other.get("decision") == "new"
            and sync.get_group(other.get("resolution_note", "")) == item["group"]
        }
        assert group_members == {cid}, (item["group"], group_members)
        assert not card_path.exists() and item["card_rel"] not in accepted
        assert not any(entry.get("ku_id") == item["ku_id"] or entry.get("card_path") == item["card_rel"] for entry in manifest)
        assert not any(
            entry.get("type") == "archive"
            and item["name_en"].casefold() == entry.get("name_en", "").casefold()
            for entry in manifest
        ), item["name_en"]
        for source in BUILDERS[cid][0]:
            source_text = " ".join((ROOT / source["file"]).read_text(encoding="utf-8-sig").split())
            assert " ".join(source["quote"].split()) in source_text, (cid, source["file"], source["span"])

        planned_by_id[cid]["ku_id"] = item["ku_id"]
        planned_by_id[cid]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        planned_by_id[cid]["resolution_note"] += (
            f" S4 registration: {item['group']} maps to {item['ku_id']}; "
            "source-local archive identity only, no independent inspection or S6 formal relation implied."
        )
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "archive",
            "canonical_name": item["name_zh"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })
        card = BUILDERS[cid][1](item)
        fm = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)
        cards.append((item, card, card_path))

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_book = [
        row for row in statements
        if row.get("subject_candidate_id") == "cand-4553" or row.get("object_candidate_id") == "cand-4553"
    ]
    assert {row["statement_id"] for row in direct_book} == {
        "st-chp2-secii-l147-193-cite-fraschetti-p107",
        "st-chp2-seciv-l190-245-citation-83",
        "st-chp21-bib-l461-496-entry-27",
        "st-chp5-note-p123-n3-cites-fraschetti",
        "st-chp1-secii-l659-n2-cites-fraschetti-passim",
        "st-chp1-secii-p17-n1-fraschetti-p108",
    }
    pending_book_relations = [row for row in direct_book if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert {row["statement_id"] for row in pending_book_relations} == {
        "st-chp5-note-p123-n3-cites-fraschetti",
        "st-chp1-secii-l659-n2-cites-fraschetti-passim",
        "st-chp1-secii-p17-n1-fraschetti-p108",
    }
    mention = next(
        row for row in sync.read_csv(TABLES / "mentions.csv")[1]
        if row.get("mention_id") == "m-chp2-secii-l147-193-0040"
    )
    assert mention.get("candidate_id") == "cand-4554"
    assert not any(
        row.get("subject_candidate_id") == "cand-4554" or row.get("object_candidate_id") == "cand-4554"
        for row in statements
    ), "S2 relation mapping gap changed; re-review before applying"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    result_next = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS.read_text(encoding="utf-8-sig").rstrip()
    process_append = f"""

<a id="s4-archive-fraschetti-and-avviso-20261017"></a>

### S4 archive：Fraschetti《Il Bernini》及1633年Avviso（{DATE}）

- `{ITEMS[0]['candidate']}`（`{ITEMS[0]['group']}`）登记至[Fraschetti《Il Bernini》书目卡](../../../{ITEMS[0]['card_rel']})。第21章p.422将其列为`Fraschetti, S.: Il Bernini, Milano 1900`；第1章p.17、第2章p.37与p.58、第5章p.123等多处引文共同支持它们指向同一出版物。作者候选`cand-3519`只有首字母，S3仍未决；本卡不扩展其身份。
- `{ITEMS[1]['candidate']}`（`{ITEMS[1]['group']}`）登记至[1633年1月8日Avviso文书卡](../../../{ITEMS[1]['card_rel']})。唯一直接证据为第2章p.37注1：Haskell称其来自罗马埃斯特使节，记载日期，并引述意大利语文字；Cardinal Borghese仅保留姓氏，原报告、Fraschetti p.107及档案定位未独立查阅。
- `cand-4554`有S2提及`m-chp2-secii-l147-193-0040`及候选来源锚点，但`book-statements.jsonl`当前没有以该文书为主语或宾语的S2关系行。故虽已登记其身份，本次不新建Avviso→Fraschetti正式边；过程明确保留这一来源映射缺口供S6回到p.37原文处理。Haskell关于书籍引文的3条S2关系候选照常留待S6。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    process_next = process_text + process_append
    result_append = f"""

### S4 archive：Fraschetti《Il Bernini》与1633年Avviso（{DATE}）

`cand-4553`登记为Fraschetti 1900年 *Il Bernini*，对应第1、2、5章及书目中的同一书目身份；`cand-4554`登记为Haskell第2章引述的1633年1月8日Avviso。原件与刊本未独立查阅，未推定Cardinal Borghese的名字。发现cand-4554已有mentions锚点但无S2主客体关系行；本次在过程记录保留该缺口，未新增正式边。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU总数{sync.fmt(len(planned_manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    accepted_next = accepted
    for item, _, _ in cards:
        accepted_next = insert_accepted(accepted_next, item["card_rel"])

    if args.dry_run:
        print("dry-run passed: " + "; ".join(f"{x['candidate']} -> {x['ku_id']}" for x in ITEMS))
        print(
            f"verified_cards={len(cards)}; source_entries={sum(len(BUILDERS[x['candidate']][0]) for x in ITEMS)}; "
            f"direct_book_statements={len(direct_book)}; pending_book_relation_candidates={len(pending_book_relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}"
        )
        print("cand-4554 S2 relation mapping gap explicitly preserved; no S5 or formal S6 rows will be written")
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
        f"applied: groups={len(ITEMS)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
