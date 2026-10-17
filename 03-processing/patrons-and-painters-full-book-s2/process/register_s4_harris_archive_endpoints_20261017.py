from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import s3_reuse_sassoferrato_candidates_20261017 as summary_tools
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
ANCHOR = "s3-s4-archive-harris-citation-endpoints-20261017"
BT = chr(96)

ARCHIVES = (
    {
        "candidate": "cand-7118",
        "group": "archive-group-ead5029fb147",
        "ku_id": "units/archives/harris-velazquez-mission-italy-1960",
        "card_path": "04-knowledge/units/archives/harris-velazquez-mission-italy-1960.md",
        "name_zh": "委拉斯开兹的意大利之行",
        "name_en": "Velazquez’s Mission in Italy",
        "original_title": "La misión de Velazquez in Italia",
        "author": "Harris, Enriqueta",
        "journal": "Archivo Español de Arte",
        "year": "1960",
        "pages": "109–136",
        "supplement": "",
        "description_zh": (
            "本卡记录哈斯克尔书目所列 Enriqueta Harris 的文章 La misión de Velazquez in Italia，刊于 Archivo Español de Arte，"
            "1960年，109–136页。第7章 p.190 注1将其作为委拉斯开兹1649年意大利行程的引文定位；本卡只登记哈斯克尔书内的书目信息，不转述未读文章内容。"
        ),
        "description_en": (
            "This card records Enriqueta Harris’s article La misión de Velazquez in Italia, listed in Haskell’s bibliography as appearing in Archivo Español de Arte "
            "in 1960, pages 109–136. Chapter 7 p. 190 n. 1 cites it in connection with Velázquez’s 1649 Italian mission. The card records Haskell’s bibliographic "
            "information only and does not summarize the unread article."
        ),
        "rows": (
            ("原题名", "La misión de Velazquez in Italia", "S2"),
            ("责任者（书目署名）", "Harris, Enriqueta", "S2"),
            ("期刊名", "Archivo Español de Arte", "S2"),
            ("出版年", "1960（p.190 注1校正 OCR i960）", "S1、S2"),
            ("页码", "109–136", "S1、S2"),
        ),
        "sources": (
            card_writer.source(
                "7", "190", "07_CHP-7_sec_i.md", "375",
                "Harris, in Archivo Español, i960, pp. 109-36",
                "第7章注1给出 Harris 在 Archivo Español 的1960年引文定位，OCR 将年份识为 i960；页图校正为1960，所引文章未独立查阅。",
            ),
            card_writer.source(
                "21", "424", "21_CHP-21Bibliography.md", "571",
                "Harris, Enriqueta: ‘La misión de Velazquez in Italia’ in Archivo Espanol de Arte, i960, pp. 109-136.",
                "书目 p.424 列出文章原题、责任者、期刊及页码；OCR 的 i960 与 p.190 注1页图校正一致。文章未独立查阅。",
            ),
        ),
        "relation_ids": ("st-chp7-p190-n1-cite-harris-1960",),
        "relation_note": "该书目引用候选保留 S6；不把未读文章内容或引文所涉事实当作本文已核实。",
        "identity_note": "",
    },
    {
        "candidate": "cand-7119",
        "group": "archive-group-bb76a9f7bb76",
        "ku_id": "units/archives/harris-colonna-decoration-san-antonio-portugueses",
        "card_path": "04-knowledge/units/archives/harris-colonna-decoration-san-antonio-portugueses.md",
        "name_zh": "安杰洛·米凯莱·科隆纳与葡萄牙人圣安东尼堂装饰",
        "name_en": "Angelo Michele Colonna and the Decoration of San Antonio of the Portuguese",
        "original_title": "Angelo Michele Colonna y la decoración de San Antonio de los Portugueses",
        "author": "Harris, Enriqueta",
        "journal": "Archivo Español de Arte",
        "year": "1961（第7章注1归年；第21章书目未列年）",
        "pages": "101–105",
        "supplement": "",
        "description_zh": (
            "本卡记录哈斯克尔书目所列 Enriqueta Harris 文章 Angelo Michele Colonna y la decoración de San Antonio de los Portugueses，"
            "刊于 Archivo Español de Arte，书目列 pp.101–105；第7章 p.190 注1将该组页码归于1961年。第21章书目条目没有列年。文章未独立查阅，"
            "本卡只登记哈斯克尔的书目记录。"
        ),
        "description_en": (
            "This card records Haskell’s bibliographic entry for Enriqueta Harris’s article Angelo Michele Colonna y la decoración de San Antonio de los Portugueses "
            "in Archivo Español de Arte, pages 101–105. Chapter 7 p. 190 n. 1 attributes those pages to 1961; the bibliography entry itself omits the year. "
            "The article was not independently consulted, so this card records Haskell’s bibliographic information only."
        ),
        "rows": (
            ("原题名", "Angelo Michele Colonna y la decoración de San Antonio de los Portugueses", "S2"),
            ("责任者（书目署名）", "Harris, Enriqueta", "S2"),
            ("期刊名", "Archivo Español de Arte", "S2"),
            ("出版年", "1961（第7章 p.190 注1归年；第21章书目未列年）", "S1、S2"),
            ("页码", "101–105", "S1、S2"),
        ),
        "sources": (
            card_writer.source(
                "7", "190", "07_CHP-7_sec_i.md", "375",
                "1961, pp. 101-105 (for Colonna and Mitelli)",
                "第7章注1明确把用于 Colonna 与 Mitelli 的 pp.101–105 归于1961年。",
            ),
            card_writer.source(
                "21", "424", "21_CHP-21Bibliography.md", "573",
                "Harris, Enriqueta: ‘Angelo Michele Colonna y la decoración de San Antonio de los Portugueses’ in Archivo Espatiol de Arte, pp. 101-105.",
                "书目 p.424 列出作者、原题、刊名与页码，但没有年份；OCR 的 Espatiol 按 S2 页图记录校正为 Español。",
            ),
        ),
        "relation_ids": ("st-chp7-p190-n1-cite-harris-1961",),
        "relation_note": "该书目引用候选保留 S6；年份来源限定为第7章注1，未将其补写为第21章书目原有字段。",
        "identity_note": "",
    },
    {
        "candidate": "cand-7127",
        "group": "archive-group-63afaa8ea5cf",
        "ku_id": "units/archives/harris-marques-del-carpio-velazquez-1957",
        "card_path": "04-knowledge/units/archives/harris-marques-del-carpio-velazquez-1957.md",
        "name_zh": "卡皮奥侯爵与委拉斯开兹绘画",
        "name_en": "The Marquis of Carpio and His Paintings by Velázquez",
        "original_title": "El Marqués del Carpio y sus cuadros de Velázquez",
        "author": "Harris, Enriqueta",
        "journal": "Archivo Español de Arte",
        "year": "1957",
        "pages": "136–139",
        "supplement": "",
        "description_zh": (
            "本卡记录哈斯克尔书目所列 Enriqueta Harris 的文章 El Marqués del Carpio y sus cuadros de Velázquez，刊于 Archivo Español de Arte，"
            "1957年，pp.136–139。第7章 p.190 注5引用该文；书目及注释均提供书内书目依据。文章未独立查阅，本卡不据题名复述其内容。"
        ),
        "description_en": (
            "This card records Enriqueta Harris’s article El Marqués del Carpio y sus cuadros de Velázquez, listed in Haskell’s bibliography as appearing in "
            "Archivo Español de Arte in 1957, pages 136–139. Chapter 7 p. 190 n. 5 cites it. The article was not independently consulted, and its contents are "
            "not inferred from the title."
        ),
        "rows": (
            ("原题名", "El Marqués del Carpio y sus cuadros de Velázquez", "S2"),
            ("责任者（书目署名）", "Harris, Enriqueta", "S2"),
            ("期刊名", "Archivo Español de Arte", "S2"),
            ("出版年", "1957", "S1、S2"),
            ("页码", "136–139", "S1、S2"),
        ),
        "sources": (
            card_writer.source(
                "7", "190", "07_CHP-7_sec_i.md", "378",
                "Harris, 1957, pp. 136-9.",
                "第7章注5以 Harris, 1957, pp.136–139 为引文定位。",
            ),
            card_writer.source(
                "21", "424", "21_CHP-21Bibliography.md", "568–569",
                "El Marques del Carpio y sus cuadros de Velázquez",
                "书目 p.424 给出责任者、题名、刊名、年份与页码；题名和刊名重音按 S2 页图校正记录恢复。",
            ),
        ),
        "relation_ids": ("st-chp7-p190-n5-cite-harris-1957",),
        "relation_note": "该书目引用候选保留 S6；文章正文及其对 Del Carpio 藏品的判断未独立查阅。",
        "identity_note": "",
    },
    {
        "candidate": "cand-11165",
        "group": "archive-group-7d2e75a7375b",
        "ku_id": "units/archives/harris-andres-descripcion-escorial-1972",
        "card_path": "04-knowledge/units/archives/harris-andres-descripcion-escorial-1972.md",
        "name_zh": "卡西亚诺·达尔·波佐的埃斯科里亚尔记述（1626）",
        "name_en": "Description of El Escorial by Cassiano dal Pozzo (1626)",
        "original_title": "Descripción del Escorial por Cassiano dal Pozzo (1626)",
        "author": "Harris, Enriqueta & Andrés, Gregorio de",
        "journal": "Archivo Español de Arte",
        "year": "1972",
        "pages": "",
        "supplement": "anejo",
        "description_zh": (
            "本卡记录哈斯克尔第21章书目 p.425 所列联合署名及文献题名：Harris, Enriqueta 与 Andrés, Gregorio de，"
            "Descripción del Escorial por Cassiano dal Pozzo (1626)，Archivo Español de Arte，1972 (anejo)。第20章 p.401 注1仅作 Harris and de Andrés 的短引。"
            "文章未独立查阅；责任者字段保存书目署名，不据此消除 de Andrés 人物候选 cand-11167 的待证状态。"
        ),
        "description_en": (
            "This card records the joint byline and title listed in Haskell’s chapter 21 bibliography, p. 425: Harris, Enriqueta and Andrés, Gregorio de, "
            "Descripción del Escorial por Cassiano dal Pozzo (1626), Archivo Español de Arte, 1972 (anejo). Chapter 20 p. 401 n. 1 gives only the short citation "
            "Harris and de Andrés. The article was not independently consulted. The byline is transcribed as a bibliographic record and does not resolve person "
            "candidate cand-11167."
        ),
        "rows": (
            ("原题名", "Descripción del Escorial por Cassiano dal Pozzo (1626)", "S2"),
            ("责任者（书目署名）", "Harris, Enriqueta & Andrés, Gregorio de", "S2"),
            ("期刊名", "Archivo Español de Arte", "S2"),
            ("出版年", "1972", "S2"),
            ("增刊标记", "anejo", "S2"),
        ),
        "sources": (
            card_writer.source(
                "20", "401", "20_CHP-20Postscript.md", "231",
                "Harris and de Andres.",
                "第20章后记注1以 Harris 与 de Andrés 的姓氏形式作短引；OCR 未显示重音，校正记录在 S2。",
            ),
            card_writer.source(
                "21", "425", "21_CHP-21Bibliography.md", "578",
                "Harris, Enriqueta & Andres, Gregorio de: ‘Description del Escoriai por Cassiano dal Pozzo (1626)’",
                "书目 p.425 列出联合署名、文献题名、期刊与1972年 anejo；OCR 重音和题名校正按 S2 页图记录恢复。",
            ),
        ),
        "relation_ids": (),
        "relation_note": "p.401 短引及 p.425 书目项是 citation/bibliography 记录，S2 未将其标为 relation_candidate；本次不新增正式关系。",
        "identity_note": "责任者书目署名包含 Gregorio de Andrés；人物候选 cand-11167 仍 undecided，不映射到人物 KU。",
    },
)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_of(note):
    match = re.search(r"(?:^|; )group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label}; found {count}")
    return text.replace(old, new, 1)


def book_source(spec):
    return {
        "citation": card_writer.BOOK_CITATION,
        "location": f"第{spec['chapter']}章，印刷页{spec['page']}；OCR L{spec['lines']}",
        "sentence_summary": spec["summary"],
        "original_quotes": [{"source_span": f"lines {spec['lines']}", "text": spec["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{spec['file']}",
            "source_span": f"lines {spec['lines']}; print p. {spec['page']}",
        },
    }


def make_card(item):
    frontmatter = {
        "title": f"{item['name_zh']}（{item['name_en']}）",
        "name_en": item["name_en"],
        "type": "archive",
        "evidence_status": "source_backed",
        "sources": [book_source(spec) for spec in item["sources"]],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in item["rows"])
    relation_list = "、".join(f"{BT}{statement_id}{BT}" for statement_id in item["relation_ids"])
    relation_status = (
        f"本次没有新增正式关系。直接 S2 书目引用候选 {relation_list} 留待 S6；{item['relation_note']}"
        if item["relation_ids"] else f"本次没有新增正式关系。{item['relation_note']}"
    )
    identity = f"\n\n### 身份边界\n\n{item['identity_note']}" if item["identity_note"] else ""
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {item['description_zh']}

**English:** {item['description_en']}

### 书目信息

以下责任者与出版信息仅按哈斯克尔书内注释／书目登记；西班牙语题名为来源所列原题，卡片显示中文及英文题名为项目工作译名。

| 字段 | 值 | 证据 |
|---|---|---|
{rows}
{identity}

## 关系与证据

{relation_status}
"""


def update_process(text, stats, manifest_count):
    if f'<a id="{ANCHOR}"></a>' in text:
        return text
    registered_groups = sum(row["registered_groups"] for row in stats.values())
    pending_groups = sum(row["pending_groups"] for row in stats.values())
    pending_members = sum(row["pending_candidates"] for row in stats.values())
    registered_members = sum(row["new_candidates"] for row in stats.values()) - pending_members
    lines = [
        f"- {item['candidate']}（{item['group']}）→ {item['ku_id']}：{item['name_zh']}（{item['name_en']}）"
        for item in ARCHIVES
    ]
    summary = "\n".join(lines)
    entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 archive：Harris 引文与合著书目身份组登记（{DATE}）

本次登记四个互不合并的 archive 身份组：

{summary}

四项均依据哈斯克尔注释或书目中的可定位题名、责任者和出版信息登记；没有独立查阅文章，也没有导入文章内容。1961 年只由第7章 p.190 注1给出，书目 p.424 未列年份；1972 年书目的 de Andrés 署名按行内原样保存，人物候选 cand-11167 仍 undecided。三条 S2 书目引用关系候选留待 S6；1972 年 p.401 短引及 p.425 书目项不是 relation_candidate。本次未新增正式关系或外部身份记录。

四张卡的书目字段表已列出原题、责任者署名及来源限定；表格事实随后通过 build_field_facts 登记。

S4 当前登记 {registered_groups:,} 组／{registered_members:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_members:,} 条映射；KU 总数 {manifest_count:,}。
"""
    return text.rstrip() + entry


def update_result(text, planned_alignment, planned_manifest, planned_stats):
    candidate_rows = [row for row in planned_alignment if not row.get("external_source")]
    registered_groups = sum(row["registered_groups"] for row in planned_stats.values())
    pending_groups = sum(row["pending_groups"] for row in planned_stats.values())
    pending_members = sum(row["pending_candidates"] for row in planned_stats.values())
    registered_members = sum(row["new_candidates"] for row in planned_stats.values()) - pending_members
    pending_new = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id"))
    pending_external = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id") and row.get("external_source"))

    text = replace_once(
        text,
        "S4 已登记527组、映射660条成员候选；尚待登记4,277组、4,318条映射。",
        f"S4 已登记{registered_groups:,}组、映射{registered_members:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "S4 top-line counts",
    )
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,546 KU",
        f"| [KU 登记](../tables/ku-manifest.csv) | {len(planned_manifest):,} KU",
        "manifest count",
    )

    warning = re.compile(
        "审计警告中的[\\d,]+条待登记 " + re.escape(BT) + "decision=new" + re.escape(BT) +
        " alignment 行，含[\\d,]+条候选决定映射（[\\d,]+组）和[\\d,]+条外部身份记录。"
    )
    warning_text = (
        f"审计警告中的{pending_new:,}条待登记 {BT}decision=new{BT} alignment 行，含{pending_members:,}条候选决定映射"
        f"（{pending_groups:,}组）和{pending_external:,}条外部身份记录。"
    )
    text, count = warning.subn(warning_text, text, count=1)
    if count != 1:
        raise AssertionError(f"pending-new warning matches: {count}")

    start = text.find("| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |")
    end = text.find("\n\n本轮新增的 archive 身份组包括：", start)
    if start < 0 or end < 0:
        raise AssertionError("S3/S4 type summary table not found")
    text = text[:start] + summary_tools.type_table(planned_stats, candidate_rows) + text[end:]

    heading = "### S3→S4 archive：Harris 引文与合著书目身份组登记（2026-10-17）"
    if heading not in text:
        links = "；".join(
            f"{item['candidate']} → [{item['name_zh']}（{item['name_en']}）](../units/archives/{Path(item['card_path']).name})"
            for item in ARCHIVES
        )
        text = text.rstrip() + f"""

{heading}

四个互不合并的 archive 组已分别登记：{links}。依据限于第7章 p.190 注释、第20章 p.401 短引及第21章 pp.424–425 书目；文章均未独立查阅。1961 年只由第7章注1给出；1972 年责任者署名按书目记录，de Andrés 人物候选 cand-11167 仍 undecided。

三条直接 S2 书目引用候选留待 S6；1972 年短引及书目记录不标为 relation_candidate。本次未新增正式关系。

S4 当前登记 {registered_groups:,} 组／{registered_members:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_members:,} 条映射；KU 总数 {len(planned_manifest):,}。
"""
    return text


def main():
    parser = argparse.ArgumentParser(description="Register four distinct Harris-related archive candidates")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    card_paths = [ROOT / item["card_path"] for item in ARCHIVES]
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    if all(path.exists() for path in card_paths):
        assert all(any(row["ku_id"] == item["ku_id"] for row in manifest) for item in ARCHIVES)
        print("ALREADY REGISTERED: all four Harris archive groups")
        return 0

    assert len(manifest) == 1546, f"unexpected manifest count: {len(manifest)}"
    assert len(alignments) == 12642, f"unexpected alignment count: {len(alignments)}"
    assert sum(1 for row in alignments if row.get("external_source")) == 235
    assert len(card_paths) == len(ARCHIVES) and not any(path.exists() for path in card_paths)
    assert all(item["card_path"] not in accepted_text for item in ARCHIVES)
    existing_archive_text = " ".join(
        row["canonical_name"] + " " + row["name_en"] + " " + row["card_path"]
        for row in manifest if row["type"] == "archive"
    ).casefold()
    for item in ARCHIVES:
        assert item["candidate"] in candidate_map
        candidate = candidate_map[item["candidate"]]
        assert candidate["suggested_type"] == "archive"
        assert item["name_en"].casefold() not in existing_archive_text

    candidate_alignment = {}
    for item in ARCHIVES:
        rows = [row for row in alignments if row["candidate_id"] == item["candidate"] and not row.get("external_source")]
        assert len(rows) == 1
        row = rows[0]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert group_of(row["resolution_note"]) == item["group"]
        candidate_alignment[item["candidate"]] = row
        for spec in item["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / spec["file"]
            assert spec["quote"] in source_path.read_text(encoding="utf-8-sig"), f"source excerpt missing from {spec['file']}"

    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in {sid for item in ARCHIVES for sid in item["relation_ids"]} | {
                "st-chp20-p401-n01-citation", "st-chp21-bib-l577-614-entry-01"
            }:
                statements[statement["statement_id"]] = statement
    direct_ids = {sid for item in ARCHIVES for sid in item["relation_ids"]}
    assert direct_ids <= set(statements)
    assert all((statements[sid].get("qualifiers") or {}).get("relation_candidate") is True for sid in direct_ids)
    assert (statements["st-chp20-p401-n01-citation"].get("qualifiers") or {}).get("relation_candidate") is False
    assert (statements["st-chp21-bib-l577-614-entry-01"].get("qualifiers") or {}).get("relation_candidate") is False
    assert next(row for row in read_csv(TABLES / "alignment.csv")[1] if row["candidate_id"] == "cand-11167")["decision"] == "undecided"

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        item = next((item for item in ARCHIVES if item["candidate"] == row["candidate_id"] and not row.get("external_source")), None)
        if item:
            row["ku_id"] = item["ku_id"]
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: mapped {item['group']} to {item['ku_id']}."

    planned_manifest = list(manifest) + [{
        "ku_id": item["ku_id"],
        "type": "archive",
        "canonical_name": item["name_zh"],
        "name_en": item["name_en"],
        "source_task": TASK,
        "card_path": item["card_path"],
    } for item in ARCHIVES]
    assert len(planned_manifest) == 1550
    planned_stats = summary_tools.compute_stats(planned_alignment, candidates)
    assert (
        sum(row["registered_groups"] for row in planned_stats.values()),
        sum(row["pending_groups"] for row in planned_stats.values()),
        sum(row["pending_candidates"] for row in planned_stats.values()),
    ) == (531, 4273, 4314)

    accepted_lines = accepted_text.splitlines()
    for card_path in sorted(item["card_path"] for item in ARCHIVES):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_path}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"), planned_stats, len(planned_manifest))
    result_text = update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        planned_alignment,
        planned_manifest,
        planned_stats,
    )
    cards = {item["card_path"]: make_card(item) for item in ARCHIVES}

    if args.dry_run:
        print(
            f"dry-run passed: archive_groups={len(ARCHIVES)} registered_groups=531 mapped_candidates=664 "
            "pending_groups=4273 pending_candidates=4314 manifest_after=1550 alignment_after=12642"
        )
        for item in ARCHIVES:
            print(f"plan: {item['candidate']} / {item['group']} -> {item['ku_id']} ({len(item['rows'])} field rows)")
        print("planned writes: four cards, accepted.yml, ku-manifest.csv, alignment.csv, process/knowledge.md, result")
        return 0

    for rel_path, contents in cards.items():
        (ROOT / rel_path).write_text(contents, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        f"applied: archive_groups={len(ARCHIVES)} registered_groups=531 mapped_candidates=664 "
        f"pending_groups=4273 pending_candidates=4314 manifest={len(planned_manifest)} alignment={len(planned_alignment)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
