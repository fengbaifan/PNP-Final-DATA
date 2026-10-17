from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s4-two-direct-endpoint-terms-20261017"


RECORDS = [
    {
        "candidate_id": "cand-9985",
        "group": "sg3-term-cand-9985",
        "ku_id": "units/terms/poem-eulogy-collections-noble-ceremonies",
        "card_path": "04-knowledge/units/terms/poem-eulogy-collections-noble-ceremonies.md",
        "title_zh": "纪念贵族典礼的诗歌与颂诗集",
        "name_en": "Collections of poems and eulogies commemorating noble ceremonies",
        "description_zh": (
            "本术语记录哈斯克尔所述威尼斯18世纪插图书的第一类：为纪念涉及贵族的具体典礼而出版的诗歌与颂诗集。作者举出就职仪式、婚礼及少女入修道院等情形，并讨论其版式、委托方式、读者接受及对诗人和艺术家的影响。"
            "本卡是出版物类别，不是某一部书或档案文献。"
        ),
        "description_en": (
            "This term records the first of Haskell’s two broad categories of illustrated books published in eighteenth-century Venice: collections of poems and eulogies issued to commemorate particular ceremonies involving the nobility. He gives examples such as taking office, marriage, and a young woman’s entry into a convent, and discusses their format, commissioning, reception, and effects on poets and artists. "
            "The unit denotes a publishing category, not an individual book or archival item."
        ),
        "scope": (
            "**原书用法：** 第13章 pp.333–334 将这些出版物与第二类插图书（现代及古代作者的精美版本）区分。哈斯克尔提到出版者依委托安排小册子或全页插图，也记录贵族家族徽章、婚礼和公共赠阅等具体语境。"
        ),
        "boundary": (
            "**对象边界：** 本卡只登记类别本身，不代表每一部纪念集都有插图、相同格式或相同受众。p.334 所述花费一千杜卡特的匿名贵族个案，不因此成为本卡所指的单一对象；未具名的具体纪念集候选 `cand-12135` 保持独立 archive 身份决定，不与此 term 合并。"
        ),
        "locator": "第13章 pp.333–334。",
        "sources": [
            {"chapter": "13", "page": "333", "file": "13_CHP-13_intro.md", "lines": "18", "quote": "the innumerable collections of poems and eulogies brought out to commemorate specific ceremonies involving the nobility", "summary": "哈斯克尔把纪念贵族典礼的诗歌与颂诗集列为威尼斯18世纪插图书的第一类，并举出若干典礼。"},
            {"chapter": "13", "page": "333", "file": "13_CHP-13_intro.md", "lines": "18–19", "quote": "These might be little more than the briefest pamphlets with the title page decorated with an elaborate frieze", "summary": "作者指出此类出版物可能是简短小册子，也可能包含全页插图；格式并不统一。"},
            {"chapter": "13", "page": "333", "file": "13_CHP-13_intro.md", "lines": "19", "quote": "These collections, which were the plague of Venetian poets who were required to contribute verses and the mainstay of many fine artists, were enormously popular with the public.", "summary": "哈斯克尔描述此类出版物对诗人、艺术家和读者的不同影响，保留为作者概述。"},
            {"chapter": "13", "page": "334", "file": "13_CHP-13_intro.md", "lines": "22", "quote": "One noble said that he had spent a thousand ducats on such a collection", "summary": "作者以一名未具名贵族的花费说明单项出版计划可能成本很高；不据此识别具体书名。"},
        ],
        "relations": [
            "st-chp13-p333-anonymous-quotation-on-poem-collections",
            "st-chp13-p333-collections-popular-and-burdened-poets",
            "st-chp13-p333-commemorative-poetry-for-noble-ceremonies",
            "st-chp13-p333-pamphlet-format-and-commissioned-design",
            "st-chp13-p334-bettinelli-criticized-opulent-poem-collection",
            "st-chp13-p333-poem-collections-required-contributions-from-venetian-poets",
            "st-chp13-p333-poem-collections-supported-fine-artists",
        ],
        "external_note": "本次仅登记哈斯克尔所划分的书内出版物类别；未新增外部书目、出版史或文献身份记录。",
    },
    {
        "candidate_id": "cand-6554",
        "group": "sg3-term-cand-6554",
        "ku_id": "units/terms/ottoboni-influence-style-haskell-account",
        "card_path": "04-knowledge/units/terms/ottoboni-influence-style-haskell-account.md",
        "title_zh": "哈斯克尔所述奥托博尼影响下的艺术风格",
        "name_en": "Style attributed by Haskell to Pietro Ottoboni’s influence on the arts",
        "description_zh": (
            "本术语记录哈斯克尔对枢机主教 Pietro Ottoboni 影响艺术的概括性描述：一种略显平淡的甜美感，受学院古典主义约束，趋向冷静而匿名的面貌，并可在师徒与宫廷之间传播。作者同时指出它缺少“真正的巴洛克”活力及法国洛可可的繁复幻想。"
            "本卡保存书内的特定风格判断，不把它扩展为已确立的艺术学校或时期名称。"
        ),
        "description_en": (
            "This term records Haskell’s characterization of Pietro Ottoboni’s influence on the arts: a somewhat bland sweetness restrained by academic classicism, tending toward cool anonymity, and transmissible from master to pupil and court to court. The author also contrasts it with the vigour of the “true Baroque” and the intricate fantasy of French rococo. "
            "The unit preserves a source-specific stylistic judgment and does not expand it into an established school or period name."
        ),
        "scope": (
            "**原书用法：** 第6章 p.165 先讨论 Trevisani、Conca、Gaulli、Juvarra 等人在 Ottoboni 圈中的不同经历，随后以审慎句式“if one can point to any specific influence”概括其艺术影响。此卡仅覆盖该段所描述的风格特征和作者比较。"
        ),
        "boundary": (
            "**对象边界：** 这不是 Ottoboni 赞助的全部艺术风格，也不是具有已知成员名册的画派。哈斯克尔的比较语句不等于每位受其赞助的画家都呈现相同风格；“true Baroque”、法国洛可可和后期18世纪绘画是原文中的对照项，保持各自候选及关系裁决，不并入本卡。"
        ),
        "locator": "第6章 p.165。",
        "sources": [
            {"chapter": "6", "page": "165", "file": "06_CHP-6_sec_v.md", "lines": "37", "quote": "a rather bland sweetness, restrained by the rules of academic classicism from verging too far in the direction of the rococo, and tending towards a certain cool anonymity", "summary": "哈斯克尔以限定性语言概括 Ottoboni 对艺术的特定影响，并描述其风格特征。"},
            {"chapter": "6", "page": "165", "file": "06_CHP-6_sec_v.md", "lines": "37", "quote": "It was a style easily transmitted from master to pupil, from court to court", "summary": "作者称这种风格易在师徒和宫廷之间传播；此为该段概括，不据此建立组织关系。"},
            {"chapter": "6", "page": "165", "file": "06_CHP-6_sec_v.md", "lines": "37", "quote": "It lacked the vigour of the true Baroque", "summary": "哈斯克尔以真正的巴洛克和法国洛可可作为比较项，保留其评价措辞。"},
        ],
        "relations": [
            "st-chp6-p165-v1-10", "st-chp6-p165-v1-11", "st-chp6-p165-v1-12",
            "st-chp6-p165-v1-13", "st-chp6-p165-v1-11-audience-reception",
            "st-chp6-p165-v1-12-french-rococo", "st-chp6-p165-v1-12-later-painting",
        ],
        "external_note": "本次依据哈斯克尔第6章的直接表述登记；未新增外部艺术史核验或风格流派记录。",
    },
]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label} anchor; found {count}")
    return text.replace(old, new, 1)


def make_sources(record):
    rows = []
    for item in record["sources"]:
        rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}",
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    return rows


def make_card(record):
    frontmatter = {
        "title": f"{record['title_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": "term",
        "evidence_status": "source_backed",
        "sources": make_sources(record),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relation_ids = "、".join(f"`{item}`" for item in record["relations"])
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 术语范围与边界

{record['scope']}

{record['boundary']}

**候选定位：** `{record['candidate_id']}`；S3 身份组 `{record['group']}`。{record['locator']}

## 关系与证据

### 关系记录

未建立正式关系。该候选有 {len(record['relations'])} 条 `relation_candidate=true` 的直接 S2 关系候选：{relation_ids}。这些候选均保留待 S6 逐条审查；本次只完成 S4 身份登记，没有写入 `relations.csv`。

### 身份与外部链接

{record['external_note']}
"""
    return f"---\n{fm}---\n\n{body}"


def count_groups(rows):
    groups = defaultdict(list)
    for row in rows:
        if row.get("decision") == "new" and not row.get("external_source"):
            group = get_group(row.get("resolution_note", ""))
            assert group, f"new decision lacks group: {row.get('candidate_id')}"
            groups[group].append(row)
    registered, pending = {}, {}
    for group, members in groups.items():
        mapped = [row for row in members if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(members) and len({row["ku_id"] for row in mapped}) == 1, group
            registered[group] = members
        else:
            pending[group] = members
    return groups, registered, pending


def update_process(text: str) -> str:
    text = replace_once(
        text,
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 23 / 32 | 906 / 909 |",
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 25 / 34 | 904 / 907 |",
        "process term S4 row",
    )
    text = replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **618 / 765** | **4,174 / 4,207** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **620 / 767** | **4,172 / 4,205** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    bullets = []
    for record in RECORDS:
        bullets.append(
            f"- `{record['candidate_id']}`（`{record['group']}`）保持 S3 `new`，登记为[{record['title_zh']}术语卡](../../../{record['card_path']})（`{record['ku_id']}`）。"
            f"{record['boundary']} {len(record['relations'])} 条直接关系候选留待 S6。"
        )
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 term：两组直接关系端点登记（2026-10-17）

两组均为单成员 S3 `new` 术语组，来源引文与候选映射记录在卡片和 `alignment.csv` 中：

{chr(10).join(bullets)}

合计登记2个 term KU 与2条候选映射。两组共14条直接 S2 关系候选仍待 S6；本次未新增正式关系、外部术语验证或 S5 enrichment。

S4累计登记620组/767条候选映射；待登记4,172组/4,205条；KU总数1,639。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(text,
        "S4 已登记618组、映射765条成员候选；尚待登记4,174组、4,207条映射。",
        "S4 已登记620组、映射767条成员候选；尚待登记4,172组、4,205条映射。", "current S4 count")
    text = replace_once(text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,637 KU",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,639 KU", "current manifest count")
    text = replace_once(text,
        "当前审计提示4,222条待登记 `decision=new` alignment 行，其中4,207条是4,174个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,220条待登记 `decision=new` alignment 行，其中4,205条是4,172个未登记身份组的候选映射，另15条是外部身份记录。", "current strict-stage pending rows")
    text = replace_once(text,
        "| term | 42→35 | 941／929 | 23／906；909 | 0 | 2 | 655 |",
        "| term | 42→35 | 941／929 | 25／904；907 | 0 | 2 | 655 |", "result term S4 row")
    text = replace_once(text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **618／4,174；4,207** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **620／4,172；4,205** | **8** | **100** | **5,441** |", "result total S4 row")
    text = replace_once(text,
        "本轮 term 登记批次见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)；五组共增加5个KU与5条候选映射，43条直接关系候选继续待S6。",
        "2026-10-17 两批 term 登记见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)及[第二批记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)；共新增7个KU与7条候选映射，57条直接关系候选继续待S6。", "current term batch note")
    return text


def main():
    parser = argparse.ArgumentParser(description="Register two additional S3 term groups that are direct S2 relation endpoints")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1637, f"unexpected manifest count: {len(manifest)}"
    assert all(not (ROOT / item["card_path"]).exists() for item in RECORDS)
    for record in RECORDS:
        cid = record["candidate_id"]
        assert candidate_by_id[cid]["suggested_type"] == "term"
        row = alignment_by_id[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row.get("resolution_note", "")) == record["group"]
        members = [
            item for item in alignments
            if not item.get("external_source") and item.get("decision") == "new"
            and get_group(item.get("resolution_note", "")) == record["group"]
        ]
        assert [item["candidate_id"] for item in members] == [cid]
        assert record["ku_id"] not in manifest_by_id and record["card_path"] not in accepted_text
        exact_duplicate = [
            item for item in manifest if item["type"] == "term"
            and (item["name_en"].casefold() == record["name_en"].casefold()
                 or item["canonical_name"].casefold() == record["title_zh"].casefold())
        ]
        assert not exact_duplicate, (cid, exact_duplicate)

    relation_ids = {item for record in RECORDS for item in record["relations"]}
    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in relation_ids:
                statements[statement["statement_id"]] = statement
    assert set(statements) == relation_ids
    for record in RECORDS:
        for statement_id in record["relations"]:
            statement = statements[statement_id]
            assert record["candidate_id"] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))
            assert (statement.get("qualifiers") or {}).get("relation_candidate") is True
        for source in record["sources"]:
            text = (ROOT / "02-sources" / "02-Markdown" / source["file"]).read_text(encoding="utf-8-sig")
            assert source["quote"] in text, (record["candidate_id"], source["quote"])

    groups, registered, pending = count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (618, 765)
    assert (len(pending), sum(map(len, pending.values()))) == (4174, 4207)
    term_registered = [members for members in registered.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "term" for r in members)]
    term_pending = [members for members in pending.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "term" for r in members)]
    assert (len(term_registered), sum(map(len, term_registered))) == (23, 32)
    assert (len(term_pending), sum(map(len, term_pending))) == (906, 909)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    for record in RECORDS:
        row = planned_by_id[record["candidate_id"]]
        row["ku_id"] = record["ku_id"]
        row["resolution_note"] += f" S4 registration: mapped {record['group']} to {record['ku_id']}; {len(record['relations'])} direct relation candidates remain pending S6."
        planned_manifest.append({
            "ku_id": record["ku_id"], "type": "term", "canonical_name": record["title_zh"],
            "name_en": record["name_en"], "source_task": TASK, "card_path": record["card_path"],
        })
    assert len(planned_manifest) == 1639
    _, registered_after, pending_after = count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (620, 767)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4172, 4205)

    accepted_lines = accepted_text.splitlines()
    for record in sorted(RECORDS, key=lambda item: item["card_path"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > record["card_path"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {record['card_path']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_texts = {record["card_path"]: make_card(record) for record in RECORDS}

    if args.dry_run:
        print("dry-run passed: groups=2 candidates=2 direct_relation_candidates=14 registered_groups_after=620 mapped_candidates_after=767 pending_groups_after=4172 pending_candidates_after=4205 manifest_after=1639 cards=2")
        return 0

    for record in RECORDS:
        (ROOT / record["card_path"]).write_text(card_texts[record["card_path"]], encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=2 candidates=2 direct_relation_candidates=14 registered_groups=620 mapped_candidates=767 pending_groups=4172 pending_candidates=4205 manifest=1639 cards=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
