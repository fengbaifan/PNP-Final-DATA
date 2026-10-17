from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml
import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
LIBRARY_CARD = "../institutions/biblioteca-marciana.md"


def source(chapter, page, file, lines, quote, summary, note=""):
    return {
        "chapter": chapter,
        "page": page,
        "file": file,
        "lines": lines,
        "quote": quote,
        "summary": summary,
        "note": note,
    }


RECORDS = [
    {
        "candidate": "cand-12115",
        "group": "archive-group-aeab9d7c31d9",
        "ku_id": "units/archives/pisani-entry-pamphlet-set-1780",
        "slug": "pisani-entry-pamphlet-set-1780",
        "name_zh": "乔治·皮萨尼1780年就任圣马可检察官纪念宣传册集",
        "name_en": "Pamphlet Set for Giorgio Pisani’s Election as Procuratore di San Marco (1780)",
        "description_zh": (
            "哈斯克尔称乔治·皮萨尼1780年当选圣马可检察官时曾有宣传册为其祝贺，其中包含引发保守派反感的寓意版画；"
            "第十章注1又称 Biblioteca Marciana 所藏的一组宣传册有十八世纪手写批语。此卡只登记书中作为整体提及的宣传册集，"
            "不将选举事件并入文献，也不把集合拆成已核实的单件清单。"
        ),
        "description_en": (
            "Haskell says pamphlets were printed in Giorgio Pisani’s honour after his 1780 election as Procuratore di San Marco, "
            "and that they included allegorical prints which aroused hostility among the bienpensants. Chapter 10 note 1 also describes "
            "a set at the Biblioteca Marciana bearing eighteenth-century annotations. This card records the collective pamphlet-set "
            "reference, keeps the election event distinct, and does not turn the set into a verified item-level inventory."
        ),
        "context_zh": (
            "第十章 p.326 将这些宣传册置于皮萨尼当选后的政治反应中；注1把一组宣传册定位于 Biblioteca Marciana, Misc. 212，"
            "并转述其中的手写批语。"
        ),
        "context_en": (
            "Chapter 10 (p. 326) places the pamphlets in the political response to Pisani’s election; note 1 locates a set at "
            "Biblioteca Marciana, Misc. 212 and reports its handwritten comments."
        ),
        "boundary_zh": (
            "整体中文、英文题名均为描述性工作题名，不是原题。书目注1列有若干出版物，但本卡不推定它们与收藏集合逐一对应，"
            "不推定每册都包含正文提及的全部版画，也不补作者、出版者分配或现藏状态。"
        ),
        "boundary_en": (
            "Both display titles are descriptive working titles, not original titles. Although note 1 lists publications, this card does not "
            "map them item by item to the cited set, infer that every pamphlet contains all prints mentioned in the narrative, assign authors "
            "or publishers to the collective object, or assert present holdings."
        ),
        "name_rows": [
            (
                "中文描述性工作题名",
                "乔治·皮萨尼1780年就任圣马可检察官纪念宣传册集",
                "[第十章 p.326](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L211–L213）",
            ),
            (
                "英文描述性工作题名",
                "Pamphlet Set for Giorgio Pisani’s Election as Procuratore di San Marco (1780)",
                "[第十章 p.326](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L211–L213）",
            ),
            (
                "集合原题",
                "书中未给整体集合一个单独题名；注1列举个别出版物",
                "[第十章 p.326 注1](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L218–L221）",
            ),
        ],
        "info_rows": [
            (
                "文献类型",
                "为皮萨尼1780年当选而印行、并被书中作为一组提及的宣传册",
                "[第十章 p.326](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L211–L213、L221）",
            ),
            (
                "图像语境",
                "哈斯克尔称其中包含引发 bienpensants 反感的寓意版画",
                "[第十章 p.326](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L213）",
            ),
            (
                "书中馆藏定位",
                "Biblioteca Marciana, Venice, Misc. 212；书中报告该组有十八世纪手写批语",
                "[第十章 p.326 注1](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L221）",
            ),
        ],
        "sources": [
            source(
                "10", "326", "10_CHP-10_sec_ii.md", "L211-L212",
                "In 1780, after complicated intrigues, he was suddenly elected\nProcuratore di San Marco. The appointment was greeted with great enthusiasm.",
                "哈斯克尔记皮萨尼于1780年当选圣马可检察官，任命受到热烈欢迎。",
            ),
            source(
                "10", "326", "10_CHP-10_sec_ii.md", "L213",
                "in the pamphlets that were printed in his honour were included strange allegorical prints that aroused the hostility of the bienpensants",
                "哈斯克尔称为皮萨尼印行的宣传册包含引起 bienpensants 反感的寓意版画。",
            ),
            source(
                "10", "326", "10_CHP-10_sec_ii.md", "L221",
                "The set of these pamphlets in the Biblioteca Marciana, Venice [Misc. 212] are all marked in an eighteenth-century hand with indignant comments such as Perfidioso, Seditioso, etc.",
                "注1称威尼斯 Biblioteca Marciana 所藏的这一组宣传册带有十八世纪手写批语。",
                "note 1",
            ),
        ],
        "relation_note": (
            "S2 的馆藏定位关系候选 st-chp10-p326-n01-marciana-set 留待 S6；机构身份现可连到"
            "[Biblioteca Marciana](../institutions/biblioteca-marciana.md)。本批没有正式关系。"
        ),
        "expected_direct_statements": 2,
    },
    {
        "candidate": "cand-10199",
        "group": "archive-group-d38c600c2388",
        "ku_id": "units/archives/zanetti-marciana-manuscript-volume-cxvi-7356",
        "slug": "zanetti-marciana-manuscript-volume-cxvi-7356",
        "name_zh": "A. M. Zanetti 的笔记与书信卷册（Biblioteca Marciana, Cod. CXVI, 7356）",
        "name_en": "A. M. Zanetti Notes and Correspondence Volume (Biblioteca Marciana, Cod. CXVI, 7356)",
        "description_zh": (
            "第十三章注4将 Biblioteca Marciana, MSS. Italiani, Cl. XI, Cod. CXVI, 7356 描述为属于 A. M. Zanetti 的卷册，"
            "其中有他的部分笔记及写给他的多封书信，卷首由 Zanetti 编有索引和摘要。此卡以书目定位和书中描述识别该卷册；"
            "手稿和目录未独立查阅。"
        ),
        "description_en": (
            "Chapter 13 note 4 describes Biblioteca Marciana, MSS. Italiani, Cl. XI, Cod. CXVI, 7356 as a volume belonging to "
            "A. M. Zanetti, containing some of his notes and a number of letters addressed to him, with an index and summaries prepared "
            "by Zanetti at the beginning. This card identifies the volume by the book’s locator and description; neither the manuscript "
            "nor its catalogue was independently consulted."
        ),
        "context_zh": (
            "第十三章 pp.341–342 的连续注释描述该卷册及其中的来信；p.342 注1另列七封 Tessin 来信的日期。七封信的候选"
            "cand-10205 保持独立身份组，不并入包含它们的卷册。"
        ),
        "context_en": (
            "The consecutive notes on pp. 341–342 describe the volume and letters addressed to Zanetti; note 1 on p. 342 separately "
            "lists seven Tessin letters by date. Candidate cand-10205 for those seven letters remains a distinct identity group and is not "
            "merged into the containing volume."
        ),
        "boundary_zh": (
            "中英文均为描述性工作题名，不是卷册原题。A. M. Zanetti 保留原书缩写形式，不扩展姓名；不把卷册和其中单件书信、"
            "收据、笔记或其他文献等同，也不据书中摘要认定已读手稿内容。"
        ),
        "boundary_en": (
            "Both display titles are descriptive working titles, not an original title for the volume. The source form A. M. Zanetti is "
            "retained without expanding the name. The volume is kept distinct from individual letters, receipts, notes, and other documents "
            "it may contain; Haskell’s summaries do not mean the manuscript has been read."
        ),
        "name_rows": [
            (
                "中文描述性工作题名",
                "A. M. Zanetti 的笔记与书信卷册（Biblioteca Marciana, Cod. CXVI, 7356）",
                "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）",
            ),
            (
                "英文描述性工作题名",
                "A. M. Zanetti Notes and Correspondence Volume (Biblioteca Marciana, Cod. CXVI, 7356)",
                "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）",
            ),
            (
                "原题",
                "书中未给该卷册一个独立题名；以馆藏号和内容说明定位",
                "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）",
            ),
        ],
        "info_rows": [
            (
                "文献类型",
                "包含笔记与书信的手稿卷册",
                "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）",
            ),
            (
                "馆藏定位",
                "Biblioteca Marciana, MSS. Italiani, Cl. XI, Cod. CXVI, 7356",
                "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）",
            ),
            (
                "书中所述归属",
                "卷册属于 A. M. Zanetti；仅保留书中措辞，不独立核验所有权",
                "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）",
            ),
            (
                "内容描述",
                "包含 Zanetti 的部分笔记及写给他的多封信，特别提到 Liechtenstein 亲王、Tessin 伯爵和 Schulenburg 元帅来信",
                "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）",
            ),
            (
                "卷首整理",
                "由 Zanetti 编制索引并摘要信件",
                "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）",
            ),
        ],
        "sources": [
            source(
                "13", "341", "13_CHP-13_intro.md", "L226",
                "This is a volume belonging to A. M. Zanetti containing some of his notes and a number of letters to him, notably from the Prince of Liechtenstein, Count Tessin and Marshal Schulenburg.",
                "注4称该卷册属于 A. M. Zanetti，含其部分笔记及来自 Liechtenstein 亲王、Tessin 伯爵和 Schulenburg 元帅等人的来信。",
                "note 4",
            ),
            source(
                "13", "341", "13_CHP-13_intro.md", "L226",
                "These are indexed and summarised by Zanetti himself at the beginning of the volume.",
                "注4称信件由 Zanetti 在卷首编制索引和摘要。",
                "note 4",
            ),
            source(
                "13", "342", "13_CHP-13_intro.md", "L227-L228",
                "The seven letters from Tessin are dated 23 September 1736 (from Vienna), 9 November 1736 (from Strahlsund), 12 March 1737,\n20 April 1744, 5 April 1748,11 June 1748 (all from Stockholm), 26 October 1743 (—but 1748)—from Copenhagen. The present quotation comes from the last of these letters.",
                "注1在同一馆藏号下逐项列出七封 Tessin 来信的日期、地点，并指出书中引用来自最后一封。",
                "note 1; retain the printed 1743— but 1748 correction and source spelling",
            ),
        ],
        "relation_note": (
            "书内馆藏定位的 S2 候选关系留待 S6；机构身份入口为"
            "[Biblioteca Marciana](../institutions/biblioteca-marciana.md)。包含的七封 Tessin 来信另属候选 cand-10205，"
            "不作为本卷册的同一身份或正式边。本批没有正式关系。"
        ),
        "expected_direct_statements": 5,
    },
    {
        "candidate": "cand-10683",
        "group": "archive-group-2f5c7d842455",
        "ku_id": "units/archives/manfrin-pamphlet-risposta-1797",
        "slug": "manfrin-pamphlet-risposta-1797",
        "name_zh": "1797年答《为公民 Gerolamo Manfrin 所作辩护信》小册子",
        "name_en": "Pamphlet Replying to an Apologetic Letter for Citizen Gerolamo Manfrin (1797)",
        "description_zh": (
            "第十七章注8以一份1797年在威尼斯印行、馆藏定位为 Biblioteca Marciana 183.C.89、p.321 的小册子作为争议性材料例证。"
            "Haskell 据这类材料评论 Manfrin 的声誉，并保留其对不诚实程度的疑问；本卡记录的是 Haskell 的引用与评价，"
            "未独立查阅小册子或馆藏目录。"
        ),
        "description_en": (
            "Chapter 17 note 8 cites a pamphlet printed in Venice in 1797, with the locator Biblioteca Marciana 183.C.89, p. 321, "
            "as an example of controversial material. Haskell uses such material to comment on Manfrin’s reputation while leaving the "
            "extent of dishonesty uncertain. This card records Haskell’s citation and assessment; the pamphlet and catalogue were not "
            "independently consulted."
        ),
        "context_zh": (
            "脚注所载意大利文题名中，S2 候选 canonical_name 记作 imparziale，而第十七章 OCR 转录为 impacciale。"
            "未对照扫描原页，本卡保留 OCR 引文，不自行校正题名拼写。"
        ),
        "context_en": (
            "The S2 candidate canonical_name records imparziale, while the Chapter 17 OCR transcription reads impacciale. The scan has "
            "not been checked; this card preserves the OCR quotation without silently normalizing the title."
        ),
        "boundary_zh": (
            "中英文展示题名均为描述性工作题名，不是原题或正式英文译名。Haskell 未在已读引文中提供出版者；不把该小册子"
            "写成针对 Manfrin 的攻击文，也不据其题名或脚注创建正式关系。脚注8的 Haskell 印刷页未在当前 S2 定位中登记；"
            "其中 p.321 是小册子引用页，不能当作 Haskell 的印刷页。"
        ),
        "boundary_en": (
            "Both display titles are descriptive working titles, not an original title or an established English translation. Haskell’s "
            "citation gives no publisher. The pamphlet is not characterized as an attack on Manfrin, and no formal relation is inferred "
            "from its title or note. The Haskell printed page for note 8 is not registered in the current S2 locator; p. 321 is the cited "
            "pamphlet page, not Haskell’s printed page."
        ),
        "name_rows": [
            (
                "中文描述性工作题名",
                "1797年答《为公民 Gerolamo Manfrin 所作辩护信》小册子",
                "[第十七章注8](../../../02-sources/02-Markdown/17_CHP-17_intro.md)（OCR L10；印刷页未登记）",
            ),
            (
                "英文描述性工作题名",
                "Pamphlet Replying to an Apologetic Letter for Citizen Gerolamo Manfrin (1797)",
                "[第十七章注8](../../../02-sources/02-Markdown/17_CHP-17_intro.md)（OCR L10；印刷页未登记）",
            ),
            (
                "原题（按 OCR 转录）",
                "Risposta alla lettera apologetica impacciale per il Cittadino Gerolamo Manfrin",
                "[第十七章注8](../../../02-sources/02-Markdown/17_CHP-17_intro.md)（OCR L10；与候选规范名拼写不同，未校页）",
            ),
        ],
        "info_rows": [
            (
                "文献类型",
                "小册子（pamphlet）",
                "[第十七章注8](../../../02-sources/02-Markdown/17_CHP-17_intro.md)（OCR L10）",
            ),
            (
                "出版地点与年份",
                "In Venezia, 1797（按书中引文）",
                "[第十七章注8](../../../02-sources/02-Markdown/17_CHP-17_intro.md)（OCR L10）",
            ),
            (
                "馆藏定位",
                "Biblioteca Marciana, 183.C.89, p. 321；p.321 为书中引文所列小册子页码",
                "[第十七章注8](../../../02-sources/02-Markdown/17_CHP-17_intro.md)（OCR L10）",
            ),
            (
                "本书引用语境",
                "Haskell 将其列作争议性材料的例子，并称 Manfrin 的不诚实程度并不清楚",
                "[第十七章注8](../../../02-sources/02-Markdown/17_CHP-17_intro.md)（OCR L10）",
            ),
        ],
        "sources": [
            source(
                "17", "not recorded", "17_CHP-17_intro.md", "L10",
                "8 See, for instance, the pamphlet Risposta alla lettera apologetica impacciale per il Cittadino Gerolamo Manfrin, In Venezia 1797, Anno I della Libertà Italiana (Biblioteca Marciana: 183.C.89, p. 321). From this and a mass of similar controversial material it is obvious that Manfrin made himself highly unpopular, though it is not quite clear to what extent he was actually dishonest.",
                "注8列出一份1797年威尼斯小册子及 Marciana 馆藏定位，并将其作为 Haskell 讨论 Manfrin 声誉的例证；印刷页尚未由 S2 定位。",
                "note 8; printed page not registered in S2; p. 321 is the pamphlet locator",
            ),
        ],
        "relation_note": (
            "S2 的馆藏定位关系候选留待 S6；机构身份入口为"
            "[Biblioteca Marciana](../institutions/biblioteca-marciana.md)。本卡不把小册子标题解释为针对 Manfrin 的攻击，"
            "也不新增正式关系。"
        ),
        "expected_direct_statements": 1,
    },
]


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def card_text(record):
    source_rows = []
    for item in record["sources"]:
        if item["page"] == "not recorded":
            location = f"第{item['chapter']}章；印刷页未由 S2 定位；OCR {item['lines']}"
            source_span = f"lines {item['lines']}; printed-page locator absent from S2"
        else:
            location = f"第{item['chapter']}章；印刷页{item['page']}；OCR {item['lines']}"
            source_span = f"lines {item['lines']}; print p. {item['page']}"
        if item["note"]:
            location += f"；{item['note']}"
            source_span += f"; {item['note']}"
        source_rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": location,
            "sentence_summary": item["summary"],
            "original_quotes": [{
                "source_span": f"lines {item['lines']}",
                "text": item["quote"],
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": source_span,
            },
        })
    frontmatter = {
        "title": f"{record['name_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    name_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in record["name_rows"])
    info_rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in record["info_rows"])
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 名称

| 字段 | 内容 | 依据 |
|---|---|---|
{name_rows}

### 基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
{info_rows}

### 本书相关内容

**中文：** {record['context_zh']}

**English:** {record['context_en']}

### 身份边界

**中文：** {record['boundary_zh']}

**English:** {record['boundary_en']}

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

{record['relation_note']}
"""
    return f"---\n{fm}---\n\n{body}"


def count_new_groups(alignment_rows):
    new_rows = [
        row for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
    ]
    groups = defaultdict(list)
    for row in new_rows:
        group = card_writer.get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {
        group: rows for group, rows in groups.items()
        if any(row.get("ku_id") for row in rows)
    }
    mapped = sum(bool(row.get("ku_id")) for rows in registered.values() for row in rows)
    return new_rows, groups, registered, mapped


def update_progress(process, result, alignment_rows, manifest_rows):
    new_rows, groups, registered, mapped = count_new_groups(alignment_rows)
    pending_groups = len(groups) - len(registered)
    pending_members = len(new_rows) - mapped
    process_pattern = re.compile(
        r"已登记\s*[\d,]+\s*组、\s*[\d,]+\s*条成员映射，尚待登记\s*[\d,]+\s*组、\s*[\d,]+\s*条。"
    )
    process, process_count = process_pattern.subn(
        f"已登记{len(registered):,}组、{mapped:,}条成员映射，尚待登记"
        f"{pending_groups:,}组、{pending_members:,}条。",
        process,
        count=1,
    )
    assert process_count == 1, "process current S4 totals did not match"
    result_pattern = re.compile(
        r"S4 已登记\s*[\d,]+\s*组、映射\s*[\d,]+\s*条成员候选；尚待登记\s*[\d,]+\s*组、\s*[\d,]+\s*条映射。"
    )
    result, result_count = result_pattern.subn(
        f"S4 已登记{len(registered):,}组、映射{mapped:,}条成员候选；"
        f"尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        result,
        count=1,
    )
    assert result_count == 1, "result current S4 totals did not match"
    manifest_pattern = re.compile(
        r"(\|\s*\[KU 登记\]\(\.\./tables/ku-manifest\.csv\)\s*\|\s*)[\d,]+ KU"
    )
    result, manifest_count = manifest_pattern.subn(
        lambda match: f"{match.group(1)}{len(manifest_rows):,} KU",
        result,
        count=1,
    )
    assert manifest_count == 1, "result manifest total did not match"
    return process, result, len(registered), mapped, pending_groups, pending_members


def main():
    parser = argparse.ArgumentParser(
        description="Register three archive identity groups directly associated with the Biblioteca Marciana endpoint."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_candidate = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert len(manifest) == 1194, f"unexpected manifest size: {len(manifest)}"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    new_paths = []
    total_direct = 0

    for record in RECORDS:
        cid = record["candidate"]
        group = record["group"]
        rel_path = f"04-knowledge/units/archives/{record['slug']}.md"
        card_path = ROOT / rel_path
        assert cid in candidates and candidates[cid]["suggested_type"] == "archive"
        alignment = alignment_by_candidate[cid]
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert card_writer.get_group(alignment["resolution_note"]) == group
        group_rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and card_writer.get_group(row["resolution_note"]) == group
        ]
        assert [row["candidate_id"] for row in group_rows] == [cid], (group, group_rows)
        assert not card_path.exists()
        assert not any(
            row.get("ku_id") == record["ku_id"] or row.get("card_path") == rel_path
            for row in manifest
        )
        assert rel_path not in accepted
        direct = [
            row for row in statements
            if row.get("subject_candidate_id") == cid or row.get("object_candidate_id") == cid
        ]
        assert len(direct) == record["expected_direct_statements"], (cid, len(direct))
        assert all(row.get("qualifiers", {}).get("relation_candidate") for row in direct)
        total_direct += len(direct)
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (cid, item["file"], item["quote"])
        planned_by_id[cid]["ku_id"] = record["ku_id"]
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {group} to {record['ku_id']}."
        planned_manifest.append({
            "ku_id": record["ku_id"],
            "type": "archive",
            "canonical_name": record["name_zh"],
            "name_en": record["name_en"],
            "source_task": TASK,
            "card_path": rel_path,
        })
        new_paths.append(rel_path)

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    updated_process, updated_result, registered, mapped, pending_groups, pending_members = update_progress(
        process_text, result_text, planned_alignment, planned_manifest
    )
    links = "、".join(
        f"[{record['candidate']}](../../../04-knowledge/units/archives/{record['slug']}.md)"
        for record in RECORDS
    )
    process_note = (
        "\n\n### S4 archive：Biblioteca Marciana 的三个直接文献端点登记（2026-10-16）\n\n"
        f"分别登记 {links}。cand-12115 是皮萨尼1780年当选后的宣传册集合；cand-10199 是 Zanetti "
        "笔记与书信所在的卷册；cand-10683 是 Haskell p. note 8 所引1797年 Manfrin 相关小册子。"
        "三者分别是集合、包含多件材料的卷册、单件出版物，不相互合并。三组共对应8条直接 S2 陈述/关系候选，"
        "均留待 S6；本批不新增正式关系或外部目录核验。cand-10205 的七封 Tessin 来信继续作为独立 archive 组，"
        "不并入 cand-10199。cand-10683 候选规范名作 imparziale，而 OCR 行 L10 作 impacciale；未校扫描页，"
        "保留该拼写待核。"
        f"S4 累计登记{registered}组/{mapped}条成员候选，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### archive：Biblioteca Marciana 三个直接关系端点 S4 登记（2026-10-16）\n\n"
        "分别登记 Pisani 1780年宣传册集、A. M. Zanetti 笔记与书信卷册、以及 Haskell 第十七章注8所引1797年小册子。"
        "它们是不同身份粒度；Zanetti 卷册不与 cand-10205 七封 Tessin 来信合并。Manfrin 小册子的候选规范拼写 "
        "imparziale 与 OCR 转录 impacciale 保留待核。三组的馆藏/语境关系候选留待 S6，不新增正式边。"
        f"全书 S4 当前登记{registered}组/{mapped}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    updated_process += process_note
    updated_result += result_note

    if args.dry_run:
        print("S4 archive direct-endpoint dry-run passed")
        for record in RECORDS:
            print(f"{record['candidate']} ({record['group']}) -> {record['ku_id']}")
        print(f"direct relation candidates={total_direct}; all remain for S6 review")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}")
        print(
            f"registered={registered:,} groups/{mapped:,} candidates; "
            f"pending={pending_groups:,} groups/{pending_members:,} candidates"
        )
        print("source quotes, group boundaries, candidate mappings, and unique destinations checked; no files changed")
        return 0

    for record in RECORDS:
        target = ROOT / f"04-knowledge/units/archives/{record['slug']}.md"
        target.write_text(card_text(record), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    for rel_path in sorted(new_paths):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {rel_path}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(updated_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(updated_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: archive groups=3; manifest={len(planned_manifest):,}; "
        f"registered={registered}/{mapped}; pending={pending_groups}/{pending_members}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
