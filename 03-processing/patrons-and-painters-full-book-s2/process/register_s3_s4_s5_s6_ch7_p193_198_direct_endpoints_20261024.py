from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
TASK = "s3-s4-s5-s6-chp7-p193-198-direct-endpoints-20261024"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#" + TASK
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_7 = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
SOURCE_21 = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
SOURCE_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
CREATED = "2026-10-24"


def archive(
    candidate_id: str,
    ku_id: str,
    title: str,
    name_en: str,
    sub_type: str,
    zh: str,
    en: str,
    bibliography_statement: str | None,
    footnote_statement: str,
    facts: list[tuple[str, str, str]],
    group: str,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "ku_id": ku_id,
        "type": "archive",
        "canonical_name": title,
        "name_en": name_en,
        "sub_type": sub_type,
        "description_zh": zh,
        "description_en": en,
        "bibliography_statement": bibliography_statement,
        "footnote_statement": footnote_statement,
        "facts": facts,
        "group": group,
        "card_path": f"04-knowledge/{ku_id}.md",
    }


ARCHIVES = [
    archive(
        "cand-7250",
        "units/archives/von-holst-pittura-veneziana-reno-neva-1951",
        "《威尼斯绘画：莱茵河与涅瓦河之间》（La pittura veneziana tra il Reno e la Neva）",
        "La pittura veneziana tra il Reno e la Neva",
        "journal article; Haskell bibliography record",
        "本卡登记 Haskell 第21章书目所列 Niels von Holst 的期刊论文。第7章 p.193 注1引该文第132页；论文与被引页均未独立查阅。",
        "This card records the journal article by Niels von Holst listed in Haskell’s Chapter 21 bibliography. Chapter 7, p.193 n.1 cites p.132; neither the article nor the cited page was independently consulted.",
        "st-chp21-bib-l616-656-entry-02",
        "st-chp7-p193-n1-von-holst",
        [
            ("文献类型", "期刊论文（Haskell书目记录）", "S1"),
            ("书目署名", "Niels von Holst（照录书目形式）", "S1"),
            ("原题名", "La pittura veneziana tra il Reno e la Neva", "S1"),
            ("期刊", "Arte Veneta", "S1"),
            ("出版年与页码", "1951；pp. 131–140", "S1"),
            ("Haskell书内引注", "第7章印刷页193注1引p.132；论文与所引页未独立查阅", "S2"),
        ],
        "archive-group-fad2b6785931",
    ),
    archive(
        "cand-7252",
        "units/archives/heilbronner-arte-italiana-mondo-1936",
        "《意大利艺术在世界：慕尼黑的巴洛克建筑师》（Arte italiana nel mondo—Architetti del Barocco a Monaco di Baviera）",
        "Arte italiana nel mondo—Architetti del Barocco a Monaco di Baviera",
        "journal article; Haskell bibliography record",
        "本卡登记 Haskell 第21章书目所列 P. Heilbronner 期刊论文。第7章 p.193 注3引该文 pp.887–904；论文与被引页未独立查阅。",
        "This card records the journal article by P. Heilbronner listed in Haskell’s Chapter 21 bibliography. Chapter 7, p.193 n.3 cites pp.887–904; neither the article nor those pages was independently consulted.",
        "st-chp21-bib-l577-614-entry-19",
        "st-chp7-p193-n3-cite-heilbronner",
        [
            ("文献类型", "期刊论文（Haskell书目记录）", "S1"),
            ("书目署名", "P. Heilbronner（照录书目形式）", "S1"),
            ("原题名", "Arte italiana nel mondo—Architetti del Barocco a Monaco di Baviera", "S1"),
            ("期刊", "Le Vie d’Italia e del Mondo", "S1"),
            ("出版年与页码", "1936；pp. 887–904", "S1"),
            ("Haskell书内引注", "第7章印刷页193注3引pp.887–904；论文与所引页未独立查阅", "S2"),
        ],
        "archive-group-2333d87ba012",
    ),
    archive(
        "cand-7253",
        "units/archives/von-freeden-quellen-barocks-franken-schoenborn-1955",
        "《舍恩博恩家族影响下的弗兰肯巴洛克史料》（Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn, I. Teil, zweiter Halbband）",
        "Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn, I. Teil, zweiter Halbband",
        "book volume; Haskell bibliography record",
        "本卡登记 Haskell 第21章书目所列 Max H. von Freeden 编著的《Quellen》第一部分第二分册。书目列 Würzburg、1955；第7章 p.194 注3提及该书。所引文献未独立查阅。",
        "This card records the second half-volume of Part I of Quellen listed in Haskell’s Chapter 21 bibliography under Max H. von Freeden. The bibliography gives Würzburg, 1955; Chapter 7, p.194 n.3 cites the work. The cited volume was not independently consulted.",
        "st-chp21-bib-l461-496-entry-28",
        "st-chp7-p194-n3-cite-von-freeden",
        [
            ("文献类型", "图书分册（Haskell书目记录）", "S1"),
            ("书目署名", "Max H. von Freeden（照录书目形式）", "S1"),
            ("原题名", "Quellen zur Geschichte des Barocks in Franken unter dem Einfluss des Hauses Schönborn", "S1"),
            ("部分与分册", "I. Teil, zweiter Halbband", "S1"),
            ("出版地与年份", "Würzburg, 1955", "S1"),
            ("Haskell书内引注", "第7章印刷页194注3；该书未独立查阅", "S2"),
        ],
        "archive-group-e96d417e186f",
    ),
    archive(
        "cand-7254",
        "units/archives/brett-third-earl-shaftesbury-1951",
        "《沙夫茨伯里伯爵三世》（The Third Earl of Shaftesbury）",
        "The Third Earl of Shaftesbury",
        "book; Haskell bibliography record",
        "本卡登记 Haskell 第21章书目所列 R. L. Brett 的《The Third Earl of Shaftesbury》。第7章 p.198 注3引第38页；该书及所引页未独立查阅。",
        "This card records R. L. Brett’s The Third Earl of Shaftesbury listed in Haskell’s Chapter 21 bibliography. Chapter 7, p.198 n.3 cites p.38; neither the book nor the cited page was independently consulted.",
        "st-chp21-bib-l243-293-entry-04",
        "st-chp7-p198-n3-brett",
        [
            ("文献类型", "图书（Haskell书目记录）", "S1"),
            ("书目署名", "R. L. Brett（照录书目形式）", "S1"),
            ("原题名", "The Third Earl of Shaftesbury", "S1"),
            ("出版地与年份", "London, 1951", "S1"),
            ("Haskell书内引注", "第7章印刷页198注3引p.38；该书与所引页未独立查阅", "S2"),
        ],
        "archive-group-705356d6ce02",
    ),
    archive(
        "cand-7255",
        "units/archives/vertue-notebooks-walpole-society-1930-1955",
        "《维尔蒂笔记》（Notebooks）",
        "Notebooks",
        "book set; Haskell bibliography record",
        "本卡登记 Haskell 第21章书目所列 George Vertue《Notebooks》出版组。书目明确写六卷及另列索引，并列 Walpole Society 卷号；不将索引计作第七卷。第7章 p.198 注1引卷II第132页；刊本与所引页未独立查阅。",
        "This card records the George Vertue Notebooks publication set listed in Haskell’s Chapter 21 bibliography. The entry distinguishes six volumes from a separately mentioned index and lists Walpole Society volume numbers; the index is not counted as a seventh volume. Chapter 7, p.198 n.1 cites vol. II, p.132; neither the set nor the cited page was independently consulted.",
        "st-chp21-bib-l1179-1218-entry-20",
        "st-chp7-p198-n1-vertue",
        [
            ("文献类型", "多卷本（Haskell书目记录）", "S1"),
            ("书目责任者", "George Vertue（照录书目形式）", "S1"),
            ("原题名", "Notebooks", "S1"),
            ("卷数与索引", "书目称 published in 6 vols.，另有 an index；不据此称七卷本", "S1"),
            ("Walpole Society卷号", "XVIII, XX, XXII, XXIV, XXVI, XXIX, XXX（书目原列）", "S1"),
            ("出版年代与Haskell引注", "1930–55；第7章印刷页198注1引vol. II, p.132；刊本与所引页未独立查阅", "S1、S2"),
        ],
        "archive-group-89c1070aa290",
    ),
    archive(
        "cand-7260",
        "units/archives/honour-english-patrons-italian-sculptors-1958",
        "《十八世纪上半叶的英国赞助人与意大利雕塑家》（English patrons and Italian sculptors in the first half of the eighteenth century）",
        "English patrons and Italian sculptors in the first half of the eighteenth century",
        "journal article; Haskell bibliography record",
        "本卡登记 Haskell 第21章书目所列 H. Honour 期刊论文。第7章 p.197 注6引 pp.220 ff.；论文与被引页未独立查阅。",
        "This card records H. Honour’s journal article listed in Haskell’s Chapter 21 bibliography. Chapter 7, p.197 n.6 cites pp.220 ff.; neither the article nor those pages was independently consulted.",
        "st-chp21-bib-l616-656-entry-03",
        "st-chp7-p197-n6-monnot-tomb-citations",
        [
            ("文献类型", "期刊论文（Haskell书目记录）", "S1"),
            ("书目署名", "H. Honour（照录书目形式）", "S1"),
            ("原题名", "English patrons and Italian sculptors in the first half of the eighteenth century", "S1"),
            ("期刊与卷号", "Connoisseur, vol. 141", "S1"),
            ("出版年与页码", "1958；pp. 220–226", "S1"),
            ("Haskell书内引注", "第7章印刷页197注6引pp.220 ff.；论文与所引页未独立查阅", "S2"),
        ],
        "archive-group-758b8ebd4760",
    ),
    archive(
        "cand-7262",
        "units/archives/gennari-raccolta-memorie-ms-b344",
        "《贝内代托·杰纳里回忆录汇编》（Raccolta di Memorie di Benedetto Gennari）",
        "Raccolta di Memorie di Benedetto Gennari",
        "manuscript record; Haskell footnote citation",
        "本卡只登记 Haskell 第7章 p.196 注1所列题名、MS B.344、Archiginnasio di Bologna 收藏说明及 Warburg Institute 的影印本说明。原稿、影印件及所引页均未独立查阅；不据题名扩写责任者或内容。",
        "This card records only the title, shelfmark MS B.344, repository wording for the Archiginnasio in Bologna, and photocopy note for the Warburg Institute as stated in Haskell’s Chapter 7, p.196 n.1. The manuscript, photocopy, and cited pages were not independently consulted; authorship and contents are not inferred from the title.",
        None,
        "st-chp7-p196-n1-gennari-evidence",
        [
            ("文献类型", "手稿记录（按Haskell注释所列）", "S1"),
            ("题名", "Raccolta di Memorie di Benedetto Gennari（照录来源形式）", "S1"),
            ("架号", "MS B.344", "S1"),
            ("来源所列保管机构", "Archiginnasio, Bologna（仅记录Haskell注释）", "S1"),
            ("影印件说明", "photocopy in Warburg Institute（仅记录Haskell注释）", "S1"),
        ],
        "archive-group-1c78e0c55f2c",
    ),
    archive(
        "cand-7265",
        "units/archives/croce-shaftesbury-in-italia-1927",
        "《意大利的沙夫茨伯里》（Shaftesbury in Italia）",
        "Shaftesbury in Italia",
        "reprinted essay; Haskell bibliography record",
        "本卡登记 Haskell 第21章书目所列 Benedetto Croce 的再版论文。书目称其收入 Uomini e cose della vecchia Italia，Bari，1927，pp.272–309；第7章 p.198 注6引该文。论文与被引页未独立查阅。",
        "This card records Benedetto Croce’s reprinted essay listed in Haskell’s Chapter 21 bibliography. The entry places it in Uomini e cose della vecchia Italia, Bari, 1927, pp.272–309; Chapter 7, p.198 n.6 cites the essay. Neither the essay nor the cited pages was independently consulted.",
        "st-chp21-bib-l376-418-entry-14",
        "st-chp7-p198-n6-shaftesbury-citations",
        [
            ("文献类型", "再版论文（Haskell书目记录）", "S1"),
            ("书目署名", "Benedetto Croce（照录书目形式）", "S1"),
            ("原题名", "Shaftesbury in Italia", "S1"),
            ("再版信息", "收入 Uomini e cose della vecchia Italia；Bari, 1927", "S1"),
            ("页码", "pp. 272–309", "S1"),
            ("Haskell书内引注", "第7章印刷页198注6；论文与所引页未独立查阅", "S2"),
        ],
        "archive-group-6fe9be2f1018",
    ),
]

WORKS = [
    {
        "candidate_id": "cand-7269",
        "ku_id": "units/works/portrait-thomas-killigrew-canini-1651",
        "type": "work",
        "canonical_name": "托马斯·基利格鲁肖像（Portrait of Thomas Killigrew）",
        "name_en": "Portrait of Thomas Killigrew",
        "sub_type": "portrait; descriptive title based on Haskell",
        "description_zh": "本卡登记 Haskell 第7章 p.197 所述 Thomas Killigrew 肖像。正文称 Killigrew 曾请人为其画像，注2将该画归于 Giovanni Angelo Canini 并记为1651年。题名为描述性工作题名；Haskell 所引 Vertue 卷I第114页未独立查阅。",
        "description_en": "This card records the portrait of Thomas Killigrew described on p.197 of Haskell’s Chapter 7. The body says Killigrew had his portrait painted, and n.2 attributes the picture to Giovanni Angelo Canini and dates it to 1651. The title is descriptive; Haskell’s cited Vertue vol. I, p.114 was not independently consulted.",
        "source_statements": ["st-chp7-p197-tourist-portrait-examples", "st-chp7-p197-n2-killigrew-portrait"],
        "facts": [
            ("来源描述性题名", "Portrait of Thomas Killigrew（描述性工作题名；非原题名）", "S1、S2"),
            ("描绘对象", "Thomas Killigrew（由正文“his portrait”与注2的Killigrew对应）", "S1、S2"),
            ("来源所报作者归属", "Giovanni Angelo Canini（Haskell注2的归属；未独立核验）", "S2"),
            ("来源所报年代", "1651（Haskell注2）", "S2"),
            ("Haskell所引位置", "Vertue, vol. I, p.114；该书及所引页未独立查阅", "S2"),
        ],
        "group": "workgrp-3f4eed0a1ba762",
        "card_path": "04-knowledge/units/works/portrait-thomas-killigrew-canini-1651.md",
        "identity_boundary_zh": "本KU对应 S3 身份组 workgrp-3f4eed0a1ba762。作品题名为来源限定的描述性工作题名；不映射至图版30a、30b或31a中的某一图版，不补写现存版本、收藏地或外部作品目录身份。",
        "identity_boundary_en": "This KU represents S3 group workgrp-3f4eed0a1ba762. Its title is a source-limited descriptive working title; it is not mapped to any one of Plates 30a, 30b, or 31a, and no surviving version, collection location, or external catalogue identity is added.",
    },
    {
        "candidate_id": "cand-7270",
        "ku_id": "units/works/james-altham-as-hermit-salvator-rosa-1665",
        "type": "work",
        "canonical_name": "詹姆斯·阿尔瑟姆扮作隐士（James Altham as a Hermit）",
        "name_en": "James Altham as a Hermit",
        "sub_type": "portrait; descriptive title based on Haskell",
        "description_zh": "本卡登记 Haskell 第7章 p.197 注2所述 James Altham 扮作隐士的肖像。注2将其归于 Salvator Rosa，记为1665年，并称其属于 Bankes Collection。后者身份／类型未决；馆藏与原作均未独立查阅。",
        "description_en": "This card records the portrait of James Altham as a hermit described in Haskell’s Chapter 7, p.197 n.2. The note attributes it to Salvator Rosa, dates it to 1665, and names the Bankes Collection. The collection’s identity and type remain unresolved; neither the collection record nor the work was independently consulted.",
        "source_statements": ["st-chp7-p197-tourist-portrait-examples", "st-chp7-p197-n2-altham-portrait"],
        "facts": [
            ("来源描述性题名", "James Altham as a Hermit（描述性工作题名；非原题名）", "S1、S2"),
            ("描绘对象", "James Altham（由正文“his portrait”与注2对应）", "S1、S2"),
            ("来源所报作者归属", "Salvator Rosa（Haskell注2的归属；未独立核验）", "S2"),
            ("来源所报年代", "1665（Haskell注2）", "S2"),
            ("来源所报收藏", "Bankes Collection（候选cand-7271；身份／类型未决，不据此建立关系）", "S2"),
            ("Haskell所引位置", "Italian Art and Britain, p.20；该书及所引页未独立查阅", "S2"),
        ],
        "group": "workgrp-aae9f8afeca1b9",
        "card_path": "04-knowledge/units/works/james-altham-as-hermit-salvator-rosa-1665.md",
        "identity_boundary_zh": "本KU对应 S3 身份组 workgrp-aae9f8afeca1b9。题名为来源限定的描述性工作题名；Bankes Collection 仍为未分类、未定身份的候选 cand-7271，不表示当前所在地或所有权。未将本画对应至图版30a、30b或31a。",
        "identity_boundary_en": "This KU represents S3 group workgrp-aae9f8afeca1b9. The title is a source-limited descriptive working title. Bankes Collection remains untyped and unidentified as candidate cand-7271; no present location or ownership is asserted. This work is not assigned to any one of Plates 30a, 30b, or 31a.",
    },
]

PERSON = {
    "candidate_id": "cand-1342",
    "ku_id": "units/persons/thomas-killigrew",
    "type": "person",
    "canonical_name": "托马斯·基利格鲁（Thomas Killigrew）",
    "name_en": "Thomas Killigrew",
    "sub_type": "",
    "description_zh": "本卡只记录 Haskell 第7章 p.197 将 Thomas Killigrew 列为曾请人为其画像的人物。来源称其为 playwright；此处不补写生平，也未做外部身份核验。",
    "description_en": "This card records only Thomas Killigrew as named by Haskell on p.197 of Chapter 7 among those who had portraits painted. The source calls him a playwright; no biography or external identity verification is added.",
    "source_statements": ["st-chp7-p197-tourist-portrait-examples", "st-chp7-p197-n2-killigrew-portrait"],
    "group": "new-person:killigrew-thomas-b439c4a7d3",
    "card_path": "04-knowledge/units/persons/thomas-killigrew.md",
}


def json_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def encode_csv(rows: list[dict[str, str]], fields: list[str]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def encode_jsonl(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def source_span(statement: dict) -> str:
    q = statement["qualifiers"]
    line_start = q["source_line_start"]
    line_end = q.get("source_line_end", line_start)
    lines = f"line {line_start}" if line_start == line_end else f"lines {line_start}–{line_end}"
    page = q.get("printed_page")
    physical = q.get("pdf_physical_page")
    note = q.get("footnote_marker")
    layer = f"; printed p.{page}" if page else ""
    layer += f" n.{note}" if note is not None else ""
    layer += f"; PDF physical p.{physical}" if physical else ""
    return f"{lines}{layer}"


def source_location(statement: dict) -> str:
    q = statement["qualifiers"]
    page = q.get("printed_page", "")
    note = q.get("footnote_marker")
    where = f"第7章，印刷页{page}"
    if note is not None:
        where += f"注{note}"
    elif statement["segment_id"].startswith("chp-21"):
        where = f"第21章书目，印刷页{page}"
    return f"{where}；Markdown {source_span(statement)}。"


def source_record(statement: dict, summary: str) -> dict:
    file = statement["source_file"]
    return {
        "citation": SOURCE_CITATION,
        "location": source_location(statement),
        "sentence_summary": summary,
        "original_quotes": [{"source_span": source_span(statement), "text": statement["original_quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": file,
            "source_span": source_span(statement),
        },
    }


def build_card(spec: dict, statements: dict[str, dict]) -> bytes:
    lines = [
        "---",
        f"title: {json_quote(spec['canonical_name'])}",
        f"name_en: {json_quote(spec['name_en'])}",
        f"type: {spec['type']}",
    ]
    if spec.get("sub_type"):
        lines.append(f"sub_type: {json_quote(spec['sub_type'])}")
    lines.extend([
        "evidence_status: source_backed",
        f"created: '{CREATED}'",
        f"updated: '{CREATED}'",
        f"process_ref: {json_quote(PROCESS_REF)}",
        "sources:",
    ])
    if spec["type"] == "archive":
        source_ids = [spec["bibliography_statement"]] if spec["bibliography_statement"] else []
        source_ids.append(spec["footnote_statement"])
        summaries = {
            spec["bibliography_statement"]: "Haskell第21章书目列出该文献的题名、责任者形式及出版信息；文献未独立查阅。"
            if spec["bibliography_statement"] else "",
            spec["footnote_statement"]: "Haskell第7章注释引用该文献；只记录书内引注和来源原文，不表示被引材料已阅读。",
        }
    else:
        source_ids = spec["source_statements"]
        summaries = {}
        for sid in source_ids:
            if sid == "st-chp7-p197-tourist-portrait-examples":
                summaries[sid] = "正文称 Killigrew、Altham 和 Baines 曾请人为其画像；不按图版号逐一配对。"
            else:
                summaries[sid] = "Haskell注2列出相应肖像描述、来源所报归属与年代；所引刊本未独立查阅。"
    for sid in source_ids:
        record = source_record(statements[sid], summaries[sid])
        lines.extend([
            f"- citation: {json_quote(record['citation'])}",
            f"  location: {json_quote(record['location'])}",
            f"  sentence_summary: {json_quote(record['sentence_summary'])}",
            "  original_quotes:",
        ])
        for quote in record["original_quotes"]:
            lines.extend([
                f"  - source_span: {json_quote(quote['source_span'])}",
                f"    text: {json_quote(quote['text'])}",
            ])
        lines.extend([
            "  evidence_ref:",
            f"    doc_id: {json_quote(record['evidence_ref']['doc_id'])}",
            f"    source_file: {json_quote(record['evidence_ref']['source_file'])}",
            f"    source_span: {json_quote(record['evidence_ref']['source_span'])}",
        ])
    lines.extend(["---", "", "## 内容", "", "### 描述", "", f"**中文：** {spec['description_zh']}", "", f"**English:** {spec['description_en']}"])
    if spec["type"] == "archive":
        lines.extend(["", "### 书目身份与范围", "", "| 字段 | 值 | 证据 |", "| --- | --- | --- |"])
        for field, value, ref in spec["facts"]:
            lines.append(f"| {field} | {value} | {ref} |")
        lines.extend([
            "",
            "### 身份边界",
            "",
            f"本KU对应 S3 身份组 {spec['group']}；范围限于 Haskell 书目与注释所指的文献记录，不据引注推断被引内容已核实。",
            "",
            f"This KU represents S3 group {spec['group']}; its scope is the work cited in Haskell’s bibliography and notes, not independent verification of the cited material.",
        ])
    elif spec["type"] == "work":
        lines.extend(["", "### 来源所载信息", "", "| 字段 | 内容 | 证据 |", "| --- | --- | --- |"])
        for field, value, ref in spec["facts"]:
            lines.append(f"| {field} | {value} | {ref} |")
        lines.extend(["", "### 身份边界", "", spec["identity_boundary_zh"], "", spec["identity_boundary_en"]])
    else:
        lines.extend([
            "",
            "### 身份边界",
            "",
            f"本KU对应 S3 来源局部人物组 {spec['group']}；本卡仅记录本书中可追溯的人名和语境，不扩写生平或外部身份。",
            "",
            f"This KU represents source-local S3 person group {spec['group']}; it records the traceable name and context in this book without adding biography or an external identity.",
        ])
    lines.extend(["", "## 关系与证据", ""])
    return ("\n".join(lines) + "\n").encode("utf-8")


def make_subject_statement(
    statement_id: str,
    work_candidate: str,
    person_candidate: str,
    person_name: str,
    footnote_statement: str,
    short_label: str,
    body: dict,
    footnote: dict,
) -> dict:
    return {
        "statement_id": statement_id,
        "segment_id": "chp-7:07_CHP-7_sec_iv:l97-119",
        "subject_candidate_id": work_candidate,
        "object_candidate_id": person_candidate,
        "predicate": "has_subject",
        "qualifiers": {
            "source_line_start": footnote["qualifiers"]["source_line_start"],
            "source_line_end": footnote["qualifiers"]["source_line_end"],
            "printed_page": 197,
            "pdf_physical_page": 35,
            "claim": f"Haskell identifies {person_name} as the person represented by the portrait; the body and linked footnote describe the same portrait context.",
            "speaker": "Haskell",
            "text_layer": "linked body and authorial footnote",
            "qualification": "This records the depicted-person identification in Haskell’s account. The cited external source was not independently consulted, and no mapping to Plates 30a, 30b, or 31a is inferred.",
            "footnote_marker": 2,
            "linked_body_statement_ids": [body["statement_id"]],
            "linked_footnote_statement_ids": [footnote_statement],
            "mentioned_candidate_ids": [work_candidate, person_candidate],
            "relation_candidate": True,
            "relation_candidate_note": f"S2 source-grounded relation candidate: the body says {person_name} had a portrait painted and the linked note identifies this work description; no plate-to-sitter mapping is inferred.",
            "support_source_lines": [
                {"line": body["qualifiers"]["source_line_start"], "printed_page": 197, "pdf_physical_page": 35},
                {"line": footnote["qualifiers"]["source_line_start"], "printed_page": 197, "pdf_physical_page": 35},
            ],
            "cited_material_not_independently_consulted": True,
            "relation_label": short_label,
        },
        "original_quote": footnote["original_quote"],
        "origin": "book",
        "source_file": SOURCE_7,
    }


def add_relation(
    rows: list[dict[str, str]],
    used_ids: set[str],
    used_keys: set[tuple[str, str, str, str, str, str]],
    next_id: int,
    subject: str,
    object_: str,
    predicate: str,
    time: str,
    role: str,
    scope: str,
    statement_id: str,
    span: str,
    file: str,
) -> int:
    natural = (subject, predicate, object_, time, role, scope)
    if natural in used_keys:
        raise ValueError(f"duplicate relation natural key for {statement_id}")
    relation_id = f"rel-{next_id:04d}"
    if relation_id in used_ids:
        raise ValueError(f"relation id collision: {relation_id}")
    rows.append({
        "relation_id": relation_id,
        "subject_ku_id": subject,
        "object_ku_id": object_,
        "predicate": predicate,
        "time": time,
        "role": role,
        "scope": scope,
        "origin": "book",
        "status": "formal",
        "source_id": SOURCE_ID,
        "source_span": span + f"; S2 statement: {statement_id}",
        "source_file": file,
        "note": "Haskell book evidence only; any cited external work or page remains unconsulted as stated.",
    })
    used_ids.add(relation_id)
    used_keys.add(natural)
    return next_id + 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    statement_path = TABLES / "book-statements.jsonl"
    statements = [json.loads(line) for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statements_by_id = {row["statement_id"]: row for row in statements}
    required_statement_ids = {
        spec["bibliography_statement"] for spec in ARCHIVES if spec["bibliography_statement"]
    } | {spec["footnote_statement"] for spec in ARCHIVES}
    required_statement_ids |= {sid for spec in WORKS + [PERSON] for sid in spec["source_statements"]}
    missing = required_statement_ids - statements_by_id.keys()
    if missing:
        raise SystemExit("missing source statement(s): " + ", ".join(sorted(missing)))

    candidate_path = TABLES / "entity-candidates.csv"
    candidates, candidate_fields = read_csv(candidate_path)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_path = TABLES / "alignment.csv"
    alignment, alignment_fields = read_csv(alignment_path)
    alignment_by_candidate: dict[str, list[dict[str, str]]] = {}
    for row in alignment:
        alignment_by_candidate.setdefault(row["candidate_id"], []).append(row)
    specs = ARCHIVES + WORKS + [PERSON]
    all_ku_ids = {row["ku_id"] for row in read_csv(TABLES / "ku-manifest.csv")[0]}
    manifest_path = TABLES / "ku-manifest.csv"
    manifest, manifest_fields = read_csv(manifest_path)
    manifest_ku_ids = {row["ku_id"] for row in manifest}
    if len(all_ku_ids) != len(manifest_ku_ids):
        raise SystemExit("duplicate KU ids detected in manifest")
    for spec in specs:
        cid = spec["candidate_id"]
        if cid not in candidate_by_id:
            raise SystemExit(f"missing candidate: {cid}")
        rows = alignment_by_candidate.get(cid, [])
        main_rows = [row for row in rows if row["external_source"] == "" and row["external_id"] == ""]
        if len(main_rows) != 1 or main_rows[0]["decision"] != "new":
            raise SystemExit(f"{cid} does not have exactly one S3 main new decision")
        if main_rows[0]["ku_id"]:
            raise SystemExit(f"{cid} already has an S4 mapping")
        if spec["ku_id"] in manifest_ku_ids:
            raise SystemExit(f"planned KU id already exists: {spec['ku_id']}")
        if (ROOT / spec["card_path"]).exists():
            raise SystemExit(f"planned card already exists: {spec['card_path']}")
        group_match = re.search(r"(?:group=|^)([^; ]+)", main_rows[0]["resolution_note"])
        if spec["group"] not in main_rows[0]["resolution_note"]:
            raise SystemExit(f"S3 identity group mismatch for {cid}: expected {spec['group']}")

    # Existing matching mentions make new mention rows unnecessary.
    mention_rows, mention_fields = read_csv(TABLES / "mentions.csv")
    mentioned = {row.get("candidate_id", "") for row in mention_rows}
    for cid in ("cand-7269", "cand-7270", "cand-1342", "cand-0085"):
        if cid not in mentioned:
            raise SystemExit(f"required source mention is missing for {cid}")

    body = statements_by_id["st-chp7-p197-tourist-portrait-examples"]
    killigrew_attribution = statements_by_id["st-chp7-p197-n2-killigrew-portrait"]
    altham_attribution = statements_by_id["st-chp7-p197-n2-altham-portrait"]
    new_statements = [
        make_subject_statement(
            "st-chp7-p197-killigrew-portrait-has-subject",
            "cand-7269",
            "cand-1342",
            "Thomas Killigrew",
            "st-chp7-p197-n2-killigrew-portrait",
            "Killigrew portrait subject",
            body,
            killigrew_attribution,
        ),
        make_subject_statement(
            "st-chp7-p197-altham-portrait-has-subject",
            "cand-7270",
            "cand-0085",
            "James Altham",
            "st-chp7-p197-n2-altham-portrait",
            "Altham portrait subject",
            body,
            altham_attribution,
        ),
    ]
    existing_statement_ids = set(statements_by_id)
    if existing_statement_ids & {row["statement_id"] for row in new_statements}:
        raise SystemExit("one or more planned S2 statement ids already exist")
    statements.extend(new_statements)

    for spec in specs:
        for row in alignment:
            if row["candidate_id"] == spec["candidate_id"] and not row["external_source"] and not row["external_id"]:
                row["ku_id"] = spec["ku_id"]
                break
        manifest.append({
            "ku_id": spec["ku_id"],
            "type": spec["type"],
            "canonical_name": spec["canonical_name"],
            "name_en": spec["name_en"],
            "source_task": "chp7-p193-198-direct-endpoints",
            "card_path": spec["card_path"],
        })
        manifest_ku_ids.add(spec["ku_id"])

    relations_path = TABLES / "relations.csv"
    relations, relation_fields = read_csv(relations_path)
    relation_ids = {row["relation_id"] for row in relations}
    natural_keys = {
        (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row.get("time", ""), row.get("role", ""), row.get("scope", ""))
        for row in relations
    }
    next_relation = max(int(re.search(r"(\d+)$", value).group(1)) for value in relation_ids) + 1
    new_relation_ids: dict[str, str] = {}
    source_7_cards = {spec["candidate_id"]: spec["ku_id"] for spec in ARCHIVES + WORKS}
    for spec in ARCHIVES:
        statement = statements_by_id[spec["footnote_statement"]]
        page = statement["qualifiers"]["printed_page"]
        note = statement["qualifiers"]["footnote_marker"]
        cited_label = spec["name_en"]
        span = f"Chapter 7, printed p.{page}, footnote {note}, line {statement['qualifiers']['source_line_start']}; PDF physical p.{statement['qualifiers']['pdf_physical_page']}"
        scope = (
            f"Haskell’s Chapter 7 p.{page} n.{note} cites {cited_label}; this records the book’s citation only. "
            "The cited publication or manuscript and any cited page were not independently consulted."
        )
        next_relation = add_relation(
            relations, relation_ids, natural_keys, next_relation,
            "units/archives/patrons-and-painters", spec["ku_id"], "cites", "",
            f"Chapter 7 p.{page} n.{note} citation", scope,
            spec["footnote_statement"], span, SOURCE_7,
        )
        new_relation_ids[spec["footnote_statement"]] = relations[-1]["relation_id"]

    for spec, creator, creator_name, statement_id, year, cited in [
        (WORKS[0], "units/persons/giovanni-angelo-canini", "Giovanni Angelo Canini", "st-chp7-p197-n2-killigrew-portrait", "1651", "Vertue, vol. I, p.114"),
        (WORKS[1], "units/persons/salvator-rosa", "Salvator Rosa", "st-chp7-p197-n2-altham-portrait", "1665", "Italian Art and Britain, p.20"),
    ]:
        scope = (
            f"Haskell p.197 n.2 reports the attribution to {creator_name} and the date {year}; "
            f"the attribution is recorded as Haskell’s source report, not independently authenticated. "
            f"The cited {cited} was not consulted."
        )
        next_relation = add_relation(
            relations, relation_ids, natural_keys, next_relation,
            spec["ku_id"], creator, "created_by", year,
            "Haskell-reported painter attribution", scope,
            statement_id,
            f"Chapter 7, printed p.197, footnote 2, line 109; PDF physical p.35",
            SOURCE_7,
        )
        new_relation_ids[statement_id + "-created_by"] = relations[-1]["relation_id"]

    for spec, person, statement_id, person_name in [
        (WORKS[0], PERSON["ku_id"], new_statements[0]["statement_id"], "Thomas Killigrew"),
        (WORKS[1], "units/persons/james-altham", new_statements[1]["statement_id"], "James Altham"),
    ]:
        scope = (
            f"Haskell’s p.197 body says {person_name} had his portrait painted; linked note 2 identifies the corresponding "
            "portrait description. This relation records the depicted-person identification only; cited material was not "
            "independently consulted and no plate-to-sitter mapping is inferred."
        )
        next_relation = add_relation(
            relations, relation_ids, natural_keys, next_relation,
            spec["ku_id"], person, "has_subject", "",
            "depicted person identified by Haskell", scope,
            statement_id,
            "Chapter 7, printed p.197, body line 65 and footnote 2 line 109; PDF physical p.35",
            SOURCE_7,
        )
        new_relation_ids[statement_id] = relations[-1]["relation_id"]

    backlog_path = TABLES / "candidate-backlog.csv"
    backlog, backlog_fields = read_csv(backlog_path)
    if any(row.get("candidate_id") == "cand-7271" for row in backlog):
        raise SystemExit("cand-7271 already has a candidate-backlog entry")
    next_backlog = max((int(re.search(r"(\d+)$", row["backlog_id"]).group(1)) for row in backlog), default=0) + 1
    backlog.append({
        "backlog_id": f"bl-{next_backlog:04d}",
        "canonical_name": "Bankes Collection (as named for the James Altham portrait)",
        "suggested_type": "",
        "status": "undecided",
        "source_id": SOURCE_ID,
        "source_ref": "chp-7:07_CHP-7_sec_iv:l97-119#L109",
        "statement_id": "st-chp7-p197-n2-altham-portrait",
        "endpoint_role": "source-reported collection for the portrait",
        "candidate_id": "cand-7271",
        "ku_id": "",
        "decision_note": "Retain candidate cand-7271 as S3 undecided: Haskell’s note names the Bankes Collection but does not identify a specific Bankes household, collection entity, repository, or present location. The taxonomy/type boundary and exact referent are unresolved. Do not assert ownership or a current-location relation; revisit when the specific collection or a supported type boundary is identified.",
        "process_ref": PROCESS_REF,
    })

    accepted_path = ROOT / "04-knowledge/accepted.yml"
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    claims = re.search(r"(?m)^claims:\s*$", accepted_text)
    if not claims:
        raise SystemExit("accepted.yml units/claims boundary changed")
    for spec in specs:
        path_line = f"- {spec['card_path']}"
        if path_line in accepted_text.splitlines():
            raise SystemExit(f"card path already appears in accepted.yml: {spec['card_path']}")
    insert_at = claims.start()
    additions = "".join(f"- {spec['card_path']}\n" for spec in specs)
    accepted_text = accepted_text[:insert_at] + additions + accepted_text[insert_at:]

    card_specs = []
    for spec in ARCHIVES:
        card_specs.append(spec)
    card_specs.extend(WORKS)
    card_specs.append(PERSON)
    new_cards = {ROOT / spec["card_path"]: build_card(spec, statements_by_id) for spec in card_specs}

    output_rows = {
        alignment_path: encode_csv(alignment, alignment_fields),
        manifest_path: encode_csv(manifest, manifest_fields),
        relations_path: encode_csv(relations, relation_fields),
        backlog_path: encode_csv(backlog, backlog_fields),
        statement_path: encode_jsonl(statements),
        accepted_path: accepted_text.encode("utf-8"),
        **new_cards,
    }
    used_kus = {row["ku_id"] for row in manifest}
    for row in relations:
        if row["status"] == "formal" and (row["subject_ku_id"] not in used_kus or row["object_ku_id"] not in used_kus):
            raise SystemExit(f"formal relation has an unresolved endpoint: {row['relation_id']}")

    before = {path: path.read_bytes() for path in output_rows if path.exists()}
    report = {
        "mode": "apply" if args.apply else "dry_run",
        "new_KUs": len(new_cards),
        "S4_candidate_mappings": len(specs),
        "new_S2_relation_candidate_statements": len(new_statements),
        "new_S6_formal_relations": len(new_relation_ids),
        "relation_ids_by_statement": new_relation_ids,
        "new_backlog_candidate": "cand-7271",
        "backlog_id": backlog[-1]["backlog_id"],
        "touched_files": [path.relative_to(ROOT).as_posix() for path in output_rows],
        "before_sha256": {path.relative_to(ROOT).as_posix(): hashlib.sha256(data).hexdigest() for path, data in before.items()},
        "output_sha256": {path.relative_to(ROOT).as_posix(): hashlib.sha256(data).hexdigest() for path, data in output_rows.items()},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("dry-run only; no files written")
        return

    recovery = ROOT / "06-runtime/recovery" / TASK
    if recovery.exists():
        raise SystemExit(f"recovery directory already exists: {recovery}")
    recovery.mkdir(parents=True)
    backup_manifest = {}
    for path, data in before.items():
        backup = recovery / "original" / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(data)
        backup_manifest[path.relative_to(ROOT).as_posix()] = hashlib.sha256(data).hexdigest()
    (recovery / "backup-manifest.json").write_text(json.dumps(backup_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    written: list[Path] = []
    created: list[Path] = []
    try:
        for path, data in output_rows.items():
            if path not in before:
                created.append(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
                handle.write(data)
                temporary = Path(handle.name)
            temporary.replace(path)
            written.append(path)
            if hashlib.sha256(path.read_bytes()).hexdigest() != hashlib.sha256(data).hexdigest():
                raise RuntimeError(f"post-write hash mismatch: {path}")
    except Exception:
        for path in reversed(written):
            if path in before:
                path.write_bytes(before[path])
            elif path.exists():
                path.unlink()
        for path in created:
            if path.exists():
                path.unlink()
        raise
    print(f"apply complete: {len(written)} files; recovery copy: {recovery.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
