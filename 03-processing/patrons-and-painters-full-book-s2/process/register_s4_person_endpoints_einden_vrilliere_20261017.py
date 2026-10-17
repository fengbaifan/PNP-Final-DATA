from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

PEOPLE = {
    "cand-0914": {
        "group": "new-person:den-einden-ferdinand-van-03e3736ba2",
        "ku_id": "units/persons/ferdinand-van-den-einden",
        "card_rel": "04-knowledge/units/persons/ferdinand-van-den-einden.md",
        "name_zh": "费迪南德·范登埃因登",
        "name_en": "Ferdinand van den Einden",
        "index": "D.csv#16",
        "pages": "第8章 p.207 注1、p.208",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "sources": [
            {
                "location": "第8章；印刷页207；注1；OCR L136",
                "span": "line 136; print p. 207, note 1",
                "summary": "注释称 Gaspar Roomer 去世时将70幅画留给 Ferdinand van den Einden；又记述 Van den Einden 将其画作遗赠给三个女儿。女儿未具名。",
                "quotes": [
                    ("line 136", "When Roomer died he left seventy of his pictures to Ferdinand van den Einden, the son of his business associate Jan."),
                    ("line 136", "Van den Einden, who himself had a fine collection, imturn left a third of his pictures to each of his three daughters."),
                ],
            },
            {
                "location": "第8章；印刷页208；OCR L57–60",
                "span": "lines 57–60; print p. 208",
                "summary": "正文称 Ferdinand van den Einden 是 Jan 之子及 Roomer 的商业伙伴，继承父亲财富并形成大型绘画收藏，赞助较年轻一代画家，且委托 Mattia Preti 创作大型画作。",
                "quotes": [
                    ("lines 57–58", "Closely associated with Roomer as patron were his business partners Jan and Ferdinand van den Einden."),
                    ("lines 58–59", "his fortune was inherited by his son Ferdinand, who was thus able to buy himself the title of Marquis and to acquire a vast collection of pictures."),
                    ("lines 59–60", "Thus he was so struck by Mattia Preti’s Marriage at Cana and the general approval it met with that he ordered several very large pictures by that artist."),
                ],
            },
        ],
        "body": """### 描述

**中文：** 本卡对应第8章和书后索引中的 Ferdinand van den Einden。Haskell 称他为 Jan 之子、Gaspar Roomer 的商业伙伴及赞助人，记述他继承父亲财富和 Roomer 留给他的70幅画、建立大型绘画收藏，并委托 Mattia Preti 创作大型画作。这些均为 Haskell 的书内记载；本卡不补写书外生平。中文名为项目工作音译。[第8章 p.207 注1](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L136）；[第8章 p.208](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L57–60）

**English:** This card represents Ferdinand van den Einden as indexed and discussed in Chapter 8. Haskell identifies him as Jan’s son and a business partner and patron associated with Gaspar Roomer; the text says he inherited his father’s fortune and seventy pictures left by Roomer, formed a large picture collection, and commissioned large pictures from Mattia Preti. These are Haskell’s reports; no biography beyond the book is added. The Chinese display name is a project working transliteration. [Chapter 8, p.207 n.1](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md) (L136); [Chapter 8, p.208](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md) (L57–60)

### 名称与身份边界

- 对应 S3 候选 `cand-0914`（D.csv#16；索引页码207n、208），保持独立人物组 `new-person:den-einden-ferdinand-van-03e3736ba2`。
- 与其父 Jan van den Einden（`cand-0915`）分为两个 source-local 人物；两卡同批登记，但不合并身份。
- 原书只称“three daughters”而未具名；相应候选 `cand-11553` 因类型与成员边界未定继续保持 S3 `undecided`，不创建女儿 KU。

### 关系与证据

以下9条 S2 关系候选留待 S6；本卡未新增正式关系：

- `st-chp8-p207-n1-ferdinand-left-thirds-to-daughters`（女儿群体端点 `cand-11553`：undecided）
- `st-chp8-p207-n1-roomer-bequeathed-seventy-pictures-to-ferdinand`（Roomer：same，已有 KU）
- `st-chp8-p208-ferdinand-admired-giordano-works-unknown`（作品端点 `cand-7464`：undecided）
- `st-chp8-p208-ferdinand-commissioned-large-preti-pictures`（作品端点 `cand-7463`：undecided）
- `st-chp8-p208-ferdinand-inherited-fortune-collected`（Jan：new，另卡登记）
- `st-chp8-p208-ferdinand-sponsored-later-venetian-inspired-painters`（术语端点 `cand-7462`：new，待 S4）
- `st-chp8-p208-ferdinand-taste-modeled-roomer-inherited-pictures`
- `st-chp8-p208-three-preti-paintings-brutal-realism`
- `st-chp8-p208-roomer-business-partner-ferdinand-van-den-einden`
""",
    },
    "cand-0915": {
        "group": "new-person:den-einden-jan-van-b2552241c3",
        "ku_id": "units/persons/jan-van-den-einden",
        "card_rel": "04-knowledge/units/persons/jan-van-den-einden.md",
        "name_zh": "扬·范登埃因登",
        "name_en": "Jan van den Einden",
        "index": "D.csv#17",
        "pages": "第8章 p.207 注1、p.208",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        "sources": [
            {
                "location": "第8章；印刷页207；注1；OCR L136",
                "span": "line 136; print p. 207, note 1",
                "summary": "注释称 Jan 是 Gaspar Roomer 商业伙伴，并把 Ferdinand van den Einden 称作其子。",
                "quotes": [
                    ("line 136", "Ferdinand van den Einden, the son of his business associate Jan."),
                ],
            },
            {
                "location": "第8章；印刷页208；OCR L58–59",
                "span": "lines 58–59; print p. 208",
                "summary": "Haskell 称 Jan van den Einden 为弗拉芒人，记述其与 Roomer 于17世纪30年代开始的商业伙伴关系及其子 Ferdinand 对财富的继承。",
                "quotes": [
                    ("line 58", "Jan van den Einden was also Flemish though, unlike Roomer, his origins seem to have been lowly."),
                    ("lines 58–59", "After some early struggles his partnership with Roomer which began in the 1630s led to his enrichment"),
                    ("lines 58–59", "his fortune was inherited by his son Ferdinand"),
                ],
            },
        ],
        "body": """### 描述

**中文：** 本卡对应第8章和书后索引所称 Jan van den Einden。Haskell 称他为弗拉芒人，并记述他与 Gaspar Roomer 的商业伙伴关系始于17世纪30年代；正文称其子 Ferdinand 继承了他的财富。关于其出身“lowly”是 Haskell 的表述，保留为作者归属，不作外部验证。中文名为项目工作音译。[第8章 p.208](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L58–59）；[第8章 p.207 注1](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L136）

**English:** This card represents Jan van den Einden as named in Chapter 8 and the index. Haskell identifies him as Flemish and says that his business partnership with Gaspar Roomer began in the 1630s; the text calls Ferdinand his son and says that Ferdinand inherited his fortune. The description of Jan’s origins as “lowly” remains attributed to Haskell and is not independently verified. The Chinese display name is a project working transliteration. [Chapter 8, p.208](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md) (L58–59); [Chapter 8, p.207 n.1](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md) (L136)

### 名称与身份边界

- 对应 S3 候选 `cand-0915`（D.csv#17；索引页码207n、208），保持独立人物组 `new-person:den-einden-jan-van-b2552241c3`。
- 与其子 Ferdinand van den Einden（`cand-0914`）分别登记；同姓和父子关系不构成同一身份。
- 未依据本书之外资料补入生卒、正式头衔或家族沿革。

### 关系与证据

以下3条 S2 关系候选留待 S6；本卡未新增正式关系：

- `st-chp8-p208-ferdinand-inherited-fortune-collected`（Jan → Ferdinand）
- `st-chp8-p208-jan-partnership-1630s-enriched`（Roomer：same，已有 KU）
- `st-chp8-p208-van-den-einden-men-business-partners`

`st-chp8-p208-jan-flemish-origin` 是关于 Jan 的非关系陈述，维持原分类。
""",
    },
    "cand-1347": {
        "group": "new-person:de-la-louis-phelipeaux-vrilliere-9bfa815caa",
        "ku_id": "units/persons/louis-phelipeaux-de-la-vrilliere",
        "card_rel": "04-knowledge/units/persons/louis-phelipeaux-de-la-vrilliere.md",
        "name_zh": "路易·菲利波·德·拉维利埃",
        "name_en": "Louis Phélipeaux de la Vrillière",
        "index": "L.csv#4",
        "pages": "第7章 p.184–185",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
        "sources": [
            {
                "location": "第7章；印刷页184；OCR L173–176",
                "span": "lines 173–176; print p. 184",
                "summary": "Haskell 将 Louis Phélipeaux de la Vrillière 称为国务秘书，并比较其收藏趣味与 Mazarin；记述其宫殿及 Guido Reni《The Rape of Helen》。",
                "quotes": [
                    ("line 173", "Louis Phélipeaux de la Vrillière, a secretary of state."),
                    ("lines 175–176", "he acquired a large and famous picture by Guido Reni of The Rape of Helen"),
                ],
            },
            {
                "location": "第7章；印刷页185；OCR L205–209",
                "span": "lines 205–209; print p. 185",
                "summary": "Haskell 记述 La Vrillière 在1640年代增加一系列绘画，并以其作品题材讨论其与 Mazarin 的趣味异同。",
                "quotes": [
                    ("lines 207–209", "In the 1640s La Vrilliere added to these a series of paintings"),
                    ("line 209", "Even a bare list of the titles of these ten huge paintings is enough to indicate the differences in taste between La Vrilliere and Mazarin."),
                ],
            },
        ],
        "body": """### 描述

**中文：** 本卡对应索引及第7章 p.184–185 所称 Louis Phélipeaux de la Vrillière。Haskell 称其为国务秘书及 Mazarin 的同时代人，叙述其绘画收藏、Guido Reni《The Rape of Helen》的购藏，以及1640年代增加的绘画系列；关于两位收藏者趣味的比较保留为作者论述。中文名为项目工作音译，不声称为规范译名。[第7章 p.184](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L173–176）；[第7章 p.185](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L205–209）

**English:** This card represents Louis Phélipeaux de la Vrillière as indexed and discussed on pp.184–185 of Chapter 7. Haskell calls him a secretary of state and a contemporary of Mazarin, and discusses his picture collection, acquisition of Guido Reni’s *The Rape of Helen*, and a series of paintings added in the 1640s. The comparison between the two collectors’ tastes remains Haskell’s analysis. The Chinese display name is a project working transliteration, not an asserted standard form. [Chapter 7, p.184](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L173–176); [Chapter 7, p.185](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md) (L205–209)

### 名称与身份边界

- 对应 S3 候选 `cand-1347`（L.csv#4；索引页码184–185），保持独立人物组 `new-person:de-la-louis-phelipeaux-vrilliere-9bfa815caa`。
- Haskell 提及的宫殿候选 `cand-6820` 仍为 S3 `undecided`，本卡不把它登记为已识别的 place；绘画系列候选 `cand-6846` 亦保持 `undecided`。
- 本卡不补入外部生平，也不把作者对收藏趣味的分析写成不带归属的事实。

### 关系与证据

以下9条 S2 关系候选留待 S6；本卡未新增正式关系：

- `st-chp7-p184-i13`（Mazarin：same，已有 KU）
- `st-chp7-p184-i15`（宫殿候选 `cand-6820`：undecided）
- `st-chp7-p184-i16`（古代英雄题材术语 `cand-6828`：new，待 S4）
- `st-chp7-p184-i17`（Guido Reni《The Rape of Helen》`cand-6826`：new，待 S4）
- `st-chp7-p185-i05`、`st-chp7-p185-i13`、`st-chp7-p185-i14`、`st-chp7-p185-i15`、`st-chp7-p185-i18`（画作系列身份候选仍 undecided；与 Mazarin 的比较保留原语境）
""",
    },
}

RELATION_IDS = {
    "cand-0914": {
        "st-chp8-p207-n1-ferdinand-left-thirds-to-daughters",
        "st-chp8-p207-n1-roomer-bequeathed-seventy-pictures-to-ferdinand",
        "st-chp8-p208-ferdinand-admired-giordano-works-unknown",
        "st-chp8-p208-ferdinand-commissioned-large-preti-pictures",
        "st-chp8-p208-ferdinand-inherited-fortune-collected",
        "st-chp8-p208-ferdinand-sponsored-later-venetian-inspired-painters",
        "st-chp8-p208-ferdinand-taste-modeled-roomer-inherited-pictures",
        "st-chp8-p208-three-preti-paintings-brutal-realism",
        "st-chp8-p208-roomer-business-partner-ferdinand-van-den-einden",
    },
    "cand-0915": {
        "st-chp8-p208-ferdinand-inherited-fortune-collected",
        "st-chp8-p208-jan-partnership-1630s-enriched",
        "st-chp8-p208-van-den-einden-men-business-partners",
    },
    "cand-1347": {
        "st-chp7-p184-i13", "st-chp7-p184-i15", "st-chp7-p184-i16",
        "st-chp7-p184-i17", "st-chp7-p185-i05", "st-chp7-p185-i13",
        "st-chp7-p185-i14", "st-chp7-p185-i15", "st-chp7-p185-i18",
    },
}
NON_RELATION_IDS = {
    "cand-0914": set(),
    "cand-0915": {"st-chp8-p208-jan-flemish-origin"},
    "cand-1347": set(),
}


def make_card(item: dict) -> str:
    sources = []
    for source in item["sources"]:
        sources.append({
            "citation": BOOK,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote} for span, quote in source["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["source_file"],
                "source_span": source["span"],
            },
        })
    frontmatter = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n## 内容\n\n{item['body']}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three directly connected person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    statements = sync.load_statements()

    for cid, item in PEOPLE.items():
        candidate = candidate_by_id[cid]
        row = decisions[cid]
        assert candidate["suggested_type"] == "person"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        members = [
            r for r in alignments
            if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new"
            and sync.get_group(r.get("resolution_note", "")) == item["group"]
        ]
        assert [r["candidate_id"] for r in members] == [cid]
        assert not (ROOT / item["card_rel"]).exists()
        assert item["card_rel"] not in accepted
        assert not any(r.get("ku_id") == item["ku_id"] or r.get("card_path") == item["card_rel"] for r in manifest)
        assert not any(
            r.get("type") == "person"
            and (r.get("name_en", "").casefold() == item["name_en"].casefold()
                 or r.get("canonical_name", "").casefold() == item["name_zh"].casefold())
            for r in manifest
        ), f"same-title person already exists: {cid}"
        source_text = " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())
        for source in item["sources"]:
            for _, quote in source["quotes"]:
                assert " ".join(quote.split()) in source_text, (cid, quote)
        direct = [
            s for s in statements
            if cid in (s.get("subject_candidate_id"), s.get("object_candidate_id"))
        ]
        assert {s["statement_id"] for s in direct} == RELATION_IDS[cid] | NON_RELATION_IDS[cid]
        assert {
            s["statement_id"] for s in direct
            if s.get("qualifiers", {}).get("relation_candidate") is True
        } == RELATION_IDS[cid]

    # Connected existing and unresolved endpoints are checked against S3's current destinations.
    assert decisions["cand-0915"]["decision"] == "new"
    assert decisions["cand-0915"].get("ku_id", "") == ""
    assert decisions["cand-11553"]["decision"] == "undecided"
    assert decisions["cand-6820"]["decision"] == "undecided"
    assert decisions["cand-6846"]["decision"] == "undecided"
    assert decisions["cand-7462"]["decision"] == "new"
    assert decisions["cand-6826"]["decision"] == "new"
    assert decisions["cand-6828"]["decision"] == "new"
    assert decisions["cand-1588"]["ku_id"] == "units/persons/mazarin"
    assert decisions["cand-2223"]["ku_id"] == "units/persons/gaspar-roomer"

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    for cid, item in PEOPLE.items():
        target = planned_by_id[cid]
        target["ku_id"] = item["ku_id"]
        target["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."
        planned_manifest.append({
            "ku_id": item["ku_id"],
            "type": "person",
            "canonical_name": item["name_zh"],
            "name_en": item["name_en"],
            "source_task": TASK,
            "card_path": item["card_rel"],
        })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 345 and totals["registered_members"] == 449
    assert totals["pending_groups"] == 4493 and totals["pending_members"] == 4569
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    audit_old = "4,587条待登记 `decision=new` alignment 行，含4,572条候选决定映射（4,496组）和15条外部身份记录。"
    audit_new = "4,584条待登记 `decision=new` alignment 行，含4,569条候选决定映射（4,493组）和15条外部身份记录。"
    assert audit_old in result_text
    result_text = result_text.replace(audit_old, audit_new, 1)

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_items = []
    for cid, item in PEOPLE.items():
        card = item["card_rel"].replace("04-knowledge/", "../../../04-knowledge/")
        result_items.append(f"`{cid}`→[{item['name_en']} 卡]({card})")
    process_note = (
        "\n\n### S4 person：Roomer 商业网络与 Mazarin 对照组的人物端点登记（2026-10-17）\n\n"
        + "；".join(result_items)
        + "。Ferdinand 与 Jan van den Einden 是两个独立 S3 人物组；正文称 Jan 为 Ferdinand 之父，并分别记述其与 Roomer 的关系。"
        "Louis Phélipeaux de la Vrillière 按书内全名登记为独立 source-local person，中文工作音译不作为规范身份依据。"
        "Ferdinand 的9条、Jan 的3条、Louis 的9条直接关系候选均留待 S6；Jan 的 Flemish-origin 句为1条非关系陈述。"
        "Mazarin 与 Gaspar Roomer 复用现有 KU；女儿群体 cand-11553、Chigi palace endpoint cand-6820 及 La Vrillière 绘画系列 cand-6846 维持 S3 undecided。"
        "候选 cand-7462（term）、cand-6826（work）、cand-6828（term）维持 S3 new，仍待 S4；本批未写 relations.csv。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_note = (
        "\n\n### S4 person：van den Einden 与 Louis Phélipeaux de la Vrillière（2026-10-17）\n\n"
        + "；".join(f"`{cid}`→[{item['name_en']} 卡]({item['card_rel'].replace('04-knowledge/', '../')})" for cid, item in PEOPLE.items())
        + "。Ferdinand、其父 Jan 及 Louis 各按独立 S3 new 组登记；21条直接关系候选留待 S6，Jan 另有1条非关系陈述。"
        "未决的具名边界、群体成员与绘画系列保持 undecided；其他 new work/term 端点仍待 S4。未新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    process_text += process_note
    result_text += result_note

    accepted_lines = accepted.splitlines()
    for item in sorted(PEOPLE.values(), key=lambda value: value["card_rel"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > item["card_rel"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {item['card_rel']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("S4 person dry-run passed: cand-0914, cand-0915, cand-1347 each have a unique source-local person KU")
        print("direct statement partitions: Ferdinand 9 relations; Jan 3 relations + 1 non-relation; Louis 9 relations")
        print("existing Roomer/Mazarin reuse targets, undecided endpoints, new work/term destinations, and source quotes checked")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}")
        print(f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; new alignment rows pending=4,584")
        print("no files changed")
        return 0

    for item in PEOPLE.values():
        (ROOT / item["card_rel"]).write_text(make_card(item), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: 3 person KUs registered; manifest={len(planned_manifest)}; pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
