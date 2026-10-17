from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_FILE = "02-sources/02-Markdown/09_CHP-9_intro.md"

AUSTRIA = {
    "candidate": "cand-8471",
    "group": "sg3-institution-cand-8471",
    "ku": "units/institutions/austrian-government",
    "zh": "奥地利政府",
    "en": "Austrian government",
    "card": "04-knowledge/units/institutions/austrian-government.md",
    "anchor": "s4-institution-austrian-government-20261017",
    "statement": "st-chp9-p259-note5-foscarini-library-transfer",
}
HOF = {
    "candidate": "cand-8472",
    "group": "sg3-institution-cand-8472",
    "ku": "units/institutions/hofbibliothek-vienna",
    "zh": "维也纳宫廷图书馆",
    "en": "Hofbibliothek, Vienna",
    "card": "04-knowledge/units/institutions/hofbibliothek-vienna.md",
    "anchor": "s4-institution-hofbibliothek-vienna-20261017",
    "statement": "st-chp9-p259-note5-library-current-location",
}
COLLECTION = {
    "candidate": "cand-8462",
    "group": "archive-group-915e97393793",
    "ku": "units/archives/marco-foscarini-library",
    "zh": "马尔科·福斯卡里尼的书籍与手稿收藏",
    "en": "Marco Foscarini's library of manuscripts and history books",
    "card": "04-knowledge/units/archives/marco-foscarini-library.md",
    "anchor": "s4-archive-marco-foscarini-library-20261017",
    "statements": {
        "st-chp9-p259-marco-library-versus-pictures",
        "st-chp9-p259-note5-foscarini-library-transfer",
        "st-chp9-p259-note5-library-current-location",
        "st-chp9-p260-books-and-manuscripts-returned",
    },
}
RELATIONS_BY_CANDIDATE = {
    AUSTRIA["candidate"]: {AUSTRIA["statement"]},
    HOF["candidate"]: {HOF["statement"]},
    COLLECTION["candidate"]: COLLECTION["statements"],
}


def insert_accepted(lines: list[str], card_paths: list[str]) -> list[str]:
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    for card_path in sorted(card_paths):
        entry = f"- {card_path}"
        assert entry not in lines
        insert_at = next(
            (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_path),
            claims_idx,
        )
        lines.insert(insert_at, entry)
        claims_idx += 1
    return lines


def card_frontmatter(zh: str, en: str, entity_type: str, process_ref: str, sources: list[dict], sub_type: str = "") -> str:
    metadata = {
        "title": f"{zh}（{en}）",
        "name_en": en,
        "type": entity_type,
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": process_ref,
    }
    if sub_type:
        metadata["sub_type"] = sub_type
    return yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)


def make_austria_card() -> str:
    fm = card_frontmatter(
        AUSTRIA["zh"], AUSTRIA["en"], "institution", f"03-processing/{TASK}/process/knowledge.md#{AUSTRIA['anchor']}",
        [{
            "citation": BOOK,
            "location": "第9章 p.259 注5；OCR L393",
            "sentence_summary": "Haskell 注5称，Marco Foscarini 的后代于1800年将其图书收藏售予 Austrian government。本卡仅记录该书内称谓及其作为报告中受让方的范围，不识别更具体的国家机构。",
            "original_quotes": [{"source_span": "line 393; print p.259, note 5", "text": "the Austrian government in 1800"}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_FILE, "source_span": "line 393; print p.259, note 5"},
        }],
        "government named as recipient in the source",
    )
    body = f"""## 内容

### 描述

**中文：** Haskell 第9章 p.259 注5在 Marco Foscarini 图书收藏的1800年出售记述中，将 Austrian government 称为受让方。本知识元保留原书的宽泛称谓，不将其等同于某一具体政权机关、后继政府或其他政治实体。中文名为工作译名。

**English:** Haskell's note 5 on p.259 names the Austrian government as recipient in the reported 1800 sale of Marco Foscarini's library. This unit preserves the source's broad designation and does not equate it with a more specific governing body, successor government, or other political entity.

### 身份依据

| 字段 | 值 | 证据 |
|---|---|---|
| 原书名称 | Austrian government | S1（第9章 p.259 注5） |
| 本书语境角色 | 1800年出售 Foscarini 图书收藏时的受让方；此处是来源所述角色，不作为已审定的正式关系 | S1（第9章 p.259 注5） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 候选 {AUSTRIA['statement']} 留待 S6；逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{AUSTRIA['anchor']})。
"""
    return f"---\n{fm}---\n\n{body}"


def make_hof_card() -> str:
    fm = card_frontmatter(
        HOF["zh"], HOF["en"], "institution", f"03-processing/{TASK}/process/knowledge.md#{HOF['anchor']}",
        [{
            "citation": BOOK,
            "location": "第9章 p.259 注5；OCR L393",
            "sentence_summary": "Haskell 注5称，Foscarini 图书收藏后来位于 Hofbibliothek, Vienna。这里记录原书给出的机构名称及其收藏存放语境，不将它改写为城市实体或未经核对的现代馆名。",
            "original_quotes": [{"source_span": "line 393; print p.259, note 5", "text": "in the Hofbibliothek, Vienna"}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_FILE, "source_span": "line 393; print p.259, note 5"},
        }],
        "historical library institution named as a collection location",
    )
    body = f"""## 内容

### 描述

**中文：** Haskell 第9章 p.259 注5称 Marco Foscarini 的图书收藏后来位于 Hofbibliothek, Vienna。本知识元以原书所用名称标识该图书馆机构，并与维也纳城市及 Foscarini 的收藏本身区分；中文名为工作译名。

**English:** Haskell's note 5 on p.259 says Marco Foscarini's library was later in the Hofbibliothek, Vienna. This unit identifies the library institution under the source's name and keeps it distinct from the city of Vienna and from Foscarini's collection itself.

### 身份依据

| 字段 | 值 | 证据 |
|---|---|---|
| 原书名称 | Hofbibliothek, Vienna | S1（第9章 p.259 注5） |
| 本书语境角色 | Haskell 所述 Foscarini 图书收藏的后来存放机构；不在本卡确认其现代继承机构 | S1（第9章 p.259 注5） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。直接 S2 候选 {HOF['statement']} 留待 S6；逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{HOF['anchor']})。
"""
    return f"---\n{fm}---\n\n{body}"


def make_collection_card() -> str:
    marco = "[马尔科·福斯卡里尼（Marco Foscarini）](../persons/marco-foscarini.md)"
    austria = "[奥地利政府（Austrian government）](../institutions/austrian-government.md)"
    hof = "[维也纳宫廷图书馆（Hofbibliothek, Vienna）](../institutions/hofbibliothek-vienna.md)"
    fm = card_frontmatter(
        COLLECTION["zh"], COLLECTION["en"], "archive", f"03-processing/{TASK}/process/knowledge.md#{COLLECTION['anchor']}",
        [
            {
                "citation": BOOK,
                "location": "第9章 p.259；OCR L194",
                "sentence_summary": "Haskell 称 Marco Foscarini 的主要注意力投向一组包括手稿和其他著作、内容多关乎威尼斯史的图书收藏；另称他较少关注绘画。",
                "original_quotes": [{"source_span": "line 194; print p.259", "text": "his magnificent library of manuscripts and other works, mostly dealing with the history of Venice"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_FILE, "source_span": "line 194; print p.259"},
            },
            {
                "citation": BOOK,
                "location": "第9章 p.259 注5；OCR L393",
                "sentence_summary": "Haskell 注5称 Marco Foscarini 的后代于1800年将该收藏售予 Austrian government，且该收藏当时位于 Hofbibliothek, Vienna。转移和存放均保留为 Haskell 的来源报告。",
                "original_quotes": [{"source_span": "line 393; print p.259, note 5", "text": "The library was sold by Marco Foscarini's descendants to the Austrian government in 1800 and is now in the Hofbibliothek, Vienna."}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_FILE, "source_span": "line 393; print p.259, note 5"},
            },
            {
                "citation": BOOK,
                "location": "第9章 p.260；OCR L205",
                "sentence_summary": "Haskell 称 Foscarini 在罗马取得大量书籍和手稿，并带回其家族宫殿；不据此将收藏与宫殿建筑或机构合并。",
                "original_quotes": [{"source_span": "line 205; print p.260", "text": "he acquired large numbers of books and manuscripts which he brought back 'quasi trionfando' to the-family palace"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_FILE, "source_span": "line 205; print p.260"},
            },
        ],
        "personal collection of manuscripts and books",
    )
    relation_text = ", ".join(sorted(COLLECTION["statements"]))
    body = f"""## 内容

### 描述

**中文：** Haskell 第9章 p.259 将 Marco Foscarini 的藏书描述为一组手稿和其他著作，多数涉及威尼斯历史。此卡登记来源所指的私人书籍与手稿收藏，不是收藏所在的家族宫殿、后来的存放机构或单件手稿。名称中的中文为描述性工作译名。

**English:** Haskell describes Marco Foscarini's library on p.259 as a collection of manuscripts and other works, mostly about Venetian history. This unit records the source-described personal book and manuscript collection, not the family palace, a later holding institution, or an individual manuscript.

### 收藏信息

| 字段 | 值 | 证据 |
|---|---|---|
| 收藏者 | {marco}；Haskell 将该收藏称为 Foscarini 的图书馆 | S1（第9章 p.259） |
| 文献类型 | 私人图书与手稿收藏 | S1（第9章 p.259） |
| 内容范围 | 手稿和其他著作，多数涉及威尼斯史 | S1（第9章 p.259） |
| 1800年转移报告 | Haskell 称 Marco Foscarini 的后代将收藏售予 {austria} | S2（第9章 p.259 注5） |
| 后来存放报告 | Haskell 称收藏当时位于 {hof}；“now”是原书叙述时点 | S2（第9章 p.259 注5） |
| 入藏叙述 | Haskell 称 Foscarini 在罗马取得大量书籍和手稿，并带回家族宫殿 | S3（第9章 p.260） |

### 本书相关内容

Haskell 还说 Foscarini 对书籍比绘画更感兴趣；他为阐释文学兴趣而委托绘画。以上说法仅按本书叙述转述。本卡不核实 collection 的现存完整性、1800年交易的法律细节或其当代馆藏位置。〔[第9章 p.259](../../../{SOURCE_FILE})；[第9章 p.260](../../../{SOURCE_FILE})〕

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。四条直接 S2 候选（{relation_text}）留待 S6；逐组记录见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{COLLECTION['anchor']})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Foscarini's collection and its two direct institutional endpoints.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    primary_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    items = [AUSTRIA, HOF, COLLECTION]
    expected_types = {AUSTRIA["candidate"]: "institution", HOF["candidate"]: "institution", COLLECTION["candidate"]: "archive"}
    for item in items:
        candidate_id = item["candidate"]
        row = primary_by_id[candidate_id]
        assert candidate_by_id[candidate_id]["suggested_type"] == expected_types[candidate_id]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        members = [
            a["candidate_id"] for a in alignments
            if a.get("candidate_id") and not a.get("external_source") and a.get("decision") == "new"
            and sync.get_group(a.get("resolution_note", "")) == item["group"]
        ]
        assert members == [candidate_id]
        assert not any(r.get("ku_id") == item["ku"] for r in manifest)
        assert not (ROOT / item["card"]).exists()

    assert primary_by_id["cand-1053"]["decision"] == "same"
    assert primary_by_id["cand-1053"]["ku_id"] == "units/persons/marco-foscarini"
    assert any(r.get("candidate_id") == "cand-1057" and r.get("ku_id") == "units/families/foscarini-family-venice" for r in alignments)
    assert any(r.get("candidate_id") == "cand-2772" and r.get("ku_id") == "units/places/vienna" for r in alignments)
    assert primary_by_id["cand-1059"]["decision"] == "undecided" and not primary_by_id["cand-1059"].get("ku_id")

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    for item in items:
        candidate_id = item["candidate"]
        direct = {
            r["statement_id"] for r in statements
            if (r.get("qualifiers") or {}).get("relation_candidate") is True
            and candidate_id in (r.get("subject_candidate_id"), r.get("object_candidate_id"))
        }
        assert direct == RELATIONS_BY_CANDIDATE[candidate_id]

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    card_paths = [item["card"] for item in items]
    assert all(path not in accepted_lines for path in card_paths)
    planned_alignments = [dict(row) for row in alignments]
    notes = {
        AUSTRIA["candidate"]: (
            f" S4登记（{DATE}）：{AUSTRIA['group']} 映射至 {AUSTRIA['ku']}；限定为 Haskell 所称1800年图书收藏出售报告中的受让方，"
            "不识别更具体的政治机构。"
        ),
        HOF["candidate"]: (
            f" S4登记（{DATE}）：{HOF['group']} 映射至 {HOF['ku']}；保留 Haskell 所用 Hofbibliothek 名称，"
            "作为图书收藏的存放机构，不等同于维也纳城市或未经核对的现代馆名。"
        ),
        COLLECTION["candidate"]: (
            f" S4登记（{DATE}）：{COLLECTION['group']} 映射至 {COLLECTION['ku']}；按书籍与手稿收藏登记，"
            "与 Marco Foscarini 人物、家族宫殿、奥地利政府及 Hofbibliothek 分立。四条直接 S2 候选留待 S6。"
        ),
    }
    for item in items:
        row = primary_by_id[item["candidate"]]
        planned = next(r for r in planned_alignments if r.get("alignment_id") == row["alignment_id"])
        planned["ku_id"] = item["ku"]
        planned["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        planned["resolution_note"] += notes[item["candidate"]]

    planned_manifest = list(manifest)
    planned_manifest.extend(
        [
            {"ku_id": AUSTRIA["ku"], "type": "institution", "canonical_name": AUSTRIA["zh"], "name_en": AUSTRIA["en"], "source_task": TASK, "card_path": AUSTRIA["card"]},
            {"ku_id": HOF["ku"], "type": "institution", "canonical_name": HOF["zh"], "name_en": HOF["en"], "source_task": TASK, "card_path": HOF["card"]},
            {"ku_id": COLLECTION["ku"], "type": "archive", "canonical_name": COLLECTION["zh"], "name_en": COLLECTION["en"], "source_task": TASK, "card_path": COLLECTION["card"]},
        ]
    )
    planned_manifest.sort(key=lambda r: r["ku_id"])
    planned_accepted = insert_accepted(accepted_lines, card_paths)
    cards = {
        AUSTRIA["card"]: make_austria_card(),
        HOF["card"]: make_hof_card(),
        COLLECTION["card"]: make_collection_card(),
    }
    for card in cards.values():
        header = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert header and isinstance(yaml.safe_load(header.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(value[key] for value in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 687
    assert totals["registered_members"] == 848
    assert totals["pending_groups"] == 4098
    assert totals["pending_members"] == 4120
    assert len(planned_manifest) == len(manifest) + 3

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    counts = [
        (685, 846, 4100, 4122),
        (686, 847, 4099, 4121),
        (687, 848, 4098, 4120),
    ]
    blocks = []
    for item, (registered_groups, registered_members, pending_groups, pending_members) in zip(items, counts, strict=True):
        assert f'<a id="{item["anchor"]}"></a>' not in process_text
        if item is AUSTRIA:
            heading = "S3/S4 institution：Austrian government 端点登记"
            summary = "Haskell 第9章 p.259 注5将 Austrian government 作为 Marco Foscarini 图书收藏1800年出售记述中的受让方。名称按原书保留，不指定更细的政府机关。"
            relation_line = f"- 直接 S2 候选 {AUSTRIA['statement']} 留待 S6；未新增 formal relations。"
        elif item is HOF:
            heading = "S3/S4 institution：Hofbibliothek, Vienna 端点登记"
            summary = "Haskell 第9章 p.259 注5称 Foscarini 图书收藏后来位于 Hofbibliothek, Vienna。此机构与 Vienna place、藏书 collection 分开；未确认现代继承馆名。"
            relation_line = f"- 直接 S2 候选 {HOF['statement']} 留待 S6；未新增 formal relations。"
        else:
            heading = "S3/S4 archive：Marco Foscarini 书籍与手稿收藏登记"
            summary = (
                f"Haskell 第9章 pp.259–260 描述该收藏的内容和 Foscarini 的收藏活动；注5报告1800年出售及后来的存放地点。"
                f"人物端点复用 Marco Foscarini KU；家族与 Vienna place 端点沿用既有映射；两个机构端点分别登记。"
                f"候选 cand-1059 的 Foscarini palace 仍 undecided，不强行并入建筑或空间 KU。"
            )
            relation_line = f"- 四条直接 S2 候选 {', '.join(sorted(COLLECTION['statements']))} 留待 S6；未新增 formal relations。"
        blocks.append(
            f"<a id=\"{item['anchor']}\"></a>\n\n### {heading}（{DATE}）\n\n"
            f"{item['candidate']} 保持单成员 new 组 {item['group']}，登记为[{item['zh']}（{item['en']}）]"
            f"(../../../{item['card']})（{item['ku']}）。{summary}\n{relation_line}\n"
            f"- S4 登记后：{sync.fmt(registered_groups)}组/{sync.fmt(registered_members)}条已登记，"
            f"{sync.fmt(pending_groups)}组/{sync.fmt(pending_members)}条待登记。"
        )
    process_text = process_text.rstrip() + "\n\n" + "\n\n".join(blocks)

    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, matches = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert matches == 1
    result_text += (
        f"\n\n### S3/S4 institution：Austrian government 端点登记（{DATE}）\n\n"
        f"{AUSTRIA['candidate']} → [{AUSTRIA['zh']}（{AUSTRIA['en']}）](../units/institutions/austrian-government.md)；"
        "仅保留原书所用的受让方称谓。\n\n"
        f"### S3/S4 institution：Hofbibliothek, Vienna 端点登记（{DATE}）\n\n"
        f"{HOF['candidate']} → [{HOF['zh']}（{HOF['en']}）](../units/institutions/hofbibliothek-vienna.md)；"
        "按原书所述存放机构登记，不等同于 Vienna 城市。\n\n"
        f"### S3/S4 archive：Marco Foscarini 书籍与手稿收藏登记（{DATE}）\n\n"
        f"{COLLECTION['candidate']} → [{COLLECTION['zh']}（{COLLECTION['en']}）](../units/archives/marco-foscarini-library.md)；"
        "四项关系候选留待 S6；Foscarini palace 继续 undecided。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: Austrian {AUSTRIA['candidate']}->{AUSTRIA['ku']}; Hofbibliothek {HOF['candidate']}->{HOF['ku']}; "
            f"collection {COLLECTION['candidate']}->{COLLECTION['ku']}; relation_candidates=6; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    for path, card in cards.items():
        (ROOT / path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: Austrian {AUSTRIA['candidate']}->{AUSTRIA['ku']}; Hofbibliothek {HOF['candidate']}->{HOF['ku']}; "
        f"collection {COLLECTION['candidate']}->{COLLECTION['ku']}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
