from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-chp8-p204-p205-roomer-endpoints-20261027"
TODAY = "2026-10-27"

KUS = [
    {
        "ku_id": "units/archives/ceci-un-mercante-mecenate-gaspare-roomer-1920",
        "type": "archive",
        "canonical_name": "《17世纪的商人赞助人加斯帕尔·罗默》（Un mercante mecenate del secolo XVII: Gaspare Roomer, 1920）",
        "name_en": "Giuseppe Ceci, Un mercante mecenate del secolo XVII: Gaspare Roomer (1920)",
        "card_path": "04-knowledge/units/archives/ceci-un-mercante-mecenate-gaspare-roomer-1920.md",
        "title": "《17世纪的商人赞助人加斯帕尔·罗默》（Un mercante mecenate del secolo XVII: Gaspare Roomer, 1920）",
        "description_zh": "Haskell书目所列Giuseppe Ceci关于Gaspar Roomer的期刊论文，刊于《Napoli Nobilissima》1920年卷。",
        "description_en": "Giuseppe Ceci’s journal article on Gaspar Roomer, listed in Haskell’s bibliography in the 1920 volume of Napoli Nobilissima.",
        "location": "Haskell第21章书目，印刷页418，Markdown行327。",
        "summary": "书目著录给出作者、题名、期刊、年份和页码；文章正文未作为本批证据。",
        "quote": "Ceci, Giuseppe: ‘Un mercante mecenate del secolo XVII: Gaspare Roomer’ in Napoli Nobilissima, 1920, pp. 160-164.",
        "sub_type": "journal_article",
    },
    {
        "ku_id": "units/archives/vaes-corneille-de-wael-1925",
        "type": "archive",
        "canonical_name": "《科尔内利斯·德·瓦尔（1592–1667）》（Corneille de Wael, 1925）",
        "name_en": "M. Vaes, Corneille de Wael (1592–1667) (1925)",
        "card_path": "04-knowledge/units/archives/vaes-corneille-de-wael-1925.md",
        "title": "《科尔内利斯·德·瓦尔（1592–1667）》（Corneille de Wael (1592–1667), 1925）",
        "description_zh": "Maurice Vaes关于Corneille de Wael的期刊论文，Haskell书目著录为1925年、页137–247；第6章所引p.171位于此页码范围内。",
        "description_en": "Maurice Vaes’s journal article on Corneille de Wael, listed by Haskell as a 1925 publication on pages 137–247; the chapter 6 citation to page 171 falls within that range.",
        "location": "Haskell第21章书目，印刷页439，Markdown行1186–1187；第6章印刷页156注2。",
        "summary": "书目和页码范围将第6章的Vaes 1925 p.171指针对应到该期刊论文；被引页未查。",
        "quote": "Vaes, M.: ‘Corneille de Wael (1592-1667)’ in Bulletin de ITnstitut Belge de Rome, 1925, pp. 137-247.",
        "sub_type": "journal_article",
        "external": "Académie royale de Belgique (Biographie Nationale)",
        "external_url": "https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf",
        "external_location": "Maurice Vaes条目所列Corneille de Wael研究，fasc. V (1925), pp. 137–247；用于出版物身份比对。",
        "external_summary": "条目核对论文作者、卷期年份和页码范围；不证明Haskell或其他作者所引页面的具体内容。",
    },
    {
        "ku_id": "units/archives/vaes-le-sejour-van-dyck-1924",
        "type": "archive",
        "canonical_name": "《安东尼·凡·戴克在意大利的逗留》（Le séjour de Van Dyck en Italie, 1924）",
        "name_en": "M. Vaes, Le séjour de Van Dyck en Italie (1924)",
        "card_path": "04-knowledge/units/archives/vaes-le-sejour-van-dyck-1924.md",
        "title": "《安东尼·凡·戴克在意大利的逗留》（Le séjour de Van Dyck en Italie, 1924）",
        "description_zh": "Maurice Vaes关于Van Dyck在意大利经历的期刊论文，Haskell书目列为1924年、页163–234。",
        "description_en": "Maurice Vaes’s journal article on Van Dyck’s stay in Italy, listed by Haskell as a 1924 publication on pages 163–234.",
        "location": "Haskell第21章书目，印刷页439，Markdown行1184–1185；第2章印刷页211注3。",
        "summary": "书目著录及Vaes研究目录支持出版物身份；Haskell引用p.211，文章与该页未查。",
        "quote": "Vaes, M.: ‘Le séjour de Van Dyck en Italie’ (Bulletin de l’Institut Belge de Rome, 1924).",
        "sub_type": "journal_article",
        "external": "Académie royale de Belgique (Biographie Nationale)",
        "external_url": "https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf",
        "external_location": "Maurice Vaes条目所列Van Dyck研究，fasc. IV (1924), pp. 163–234；用于出版物身份比对。",
        "external_summary": "条目核对论文作者、卷期年份和页码范围；不证明Haskell或其他作者所引页面的具体内容。",
    },
    {
        "ku_id": "units/places/chicago",
        "type": "place",
        "canonical_name": "芝加哥（Chicago）",
        "name_en": "Chicago",
        "card_path": "04-knowledge/units/places/chicago.md",
        "title": "芝加哥（Chicago）",
        "description_zh": "Haskell在第8章脚注中将《迦拿婚宴》报告为当时位于芝加哥；此处指城市，不等同于芝加哥艺术博物馆。",
        "description_en": "Haskell’s chapter 8 note reports The Marriage at Cana as then being in Chicago; this place is the city, not the Art Institute of Chicago.",
        "location": "第8章印刷页204注2，Markdown行128；第2章印刷页55行40另列芝加哥与柏林。",
        "summary": "第2章列举城市与两幅Poussin风景画，但未逐幅配对；本卡不作此配对。",
        "quote": "The Marriage at Cana of about 1686, now in Chicago",
    },
    {
        "ku_id": "units/persons/giuseppe-ceci",
        "type": "person",
        "canonical_name": "朱塞佩·切奇（Giuseppe Ceci）",
        "name_en": "Giuseppe Ceci",
        "card_path": "04-knowledge/units/persons/giuseppe-ceci.md",
        "title": "朱塞佩·切奇（Giuseppe Ceci）",
        "description_zh": "Haskell书目列为1920年Gaspar Roomer论文的作者。",
        "description_en": "Identified in Haskell’s bibliography as the author of the 1920 article on Gaspar Roomer.",
        "location": "第21章书目，印刷页418，Markdown行327。",
        "summary": "姓名与作者责任仅按Haskell书目著录记录；不据此扩写生平。",
        "quote": "Ceci, Giuseppe",
    },
    {
        "ku_id": "units/persons/maurice-vaes",
        "type": "person",
        "canonical_name": "莫里斯·瓦埃斯（Maurice Vaes）",
        "name_en": "Maurice Vaes",
        "card_path": "04-knowledge/units/persons/maurice-vaes.md",
        "title": "莫里斯·瓦埃斯（Maurice Vaes）",
        "description_zh": "比利时艺术史学者；Haskell在第2、6、7、8章所见的Vaes／M. Vaes引文及书目记录，经权威作者目录对读后归入同一人物。",
        "description_en": "A Belgian art historian; the Vaes/M. Vaes citations and bibliography entries in Haskell’s chapters 2, 6, 7, and 8 are grouped to this person through authority and bibliographic comparison.",
        "location": "Haskell第21章书目，印刷页439；第2章p.211注3、第6章p.156注2、第7章p.170注1、第8章p.207。",
        "summary": "姓名身份来源仅用于作者身份对齐；不据此声称读过Vaes论文或核实Haskell所引内容。",
        "quote": "Vaes, M.",
        "external": "Académie royale de Belgique (Biographie Nationale)",
        "external_url": "https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf",
        "external_location": "Maurice Vaes作者条目及其1924、1925年研究清单。",
        "external_summary": "用以将M. Vaes形式与Maurice Vaes及两篇期刊论文联系；不核实论文正文。",
        "external2": "Römisches Jahrbuch der Bibliotheca Hertziana",
        "external2_url": "https://ahnp.ub.uni-heidelberg.de/journals/rjbh/article/download/95009/89787",
        "external2_location": "书目中的Vaes 1931论文著录。",
        "external2_summary": "该学术书目以Maurice Vaes署名列出同题1931年论文，用于对读Haskell书目记录；不核实p.202内容。",
    },
    {
        "ku_id": "units/persons/saint-januarius",
        "type": "person",
        "canonical_name": "圣雅努阿里乌斯（Saint Januarius）",
        "name_en": "Saint Januarius",
        "card_path": "04-knowledge/units/persons/saint-januarius.md",
        "title": "圣雅努阿里乌斯（Saint Januarius）",
        "description_zh": "第8章脚注中被指为Sebastiano Marcotti版画描绘对象的圣人。",
        "description_en": "The saint named in chapter 8 as the subject of a print by Sebastiano Marcotti.",
        "location": "第8章印刷页205注4，Markdown行133；原書印刷讀作Januarius，OCR異文Januatius。",
        "summary": "僅記錄版畫所指名的對象；不補寫生平或把人物與版畫、Ribera的底本合併。",
        "quote": "St Januarius",
    },
    {
        "ku_id": "units/persons/sebastiano-marcotti",
        "type": "person",
        "canonical_name": "塞巴斯蒂亚诺·马尔科蒂（Sebastiano Marcotti）",
        "name_en": "Sebastiano Marcotti",
        "card_path": "04-knowledge/units/persons/sebastiano-marcotti.md",
        "title": "塞巴斯蒂亚诺·马尔科蒂（Sebastiano Marcotti）",
        "description_zh": "Haskell第8章脚注中被指为1665年圣雅努阿里乌斯版画创作者的版画家。",
        "description_en": "The printmaker identified by Haskell in chapter 8 as the maker of a 1665 print of Saint Januarius.",
        "location": "第8章印刷页205注4，Markdown行133；索引M.csv#80。",
        "summary": "只记录本书支持的创作者身份，不补写生卒或其他作品。",
        "quote": "a print by Sebastiano Marcotti",
    },
    {
        "ku_id": "units/works/flaying-of-marsyas-san-martino-1637",
        "type": "work",
        "canonical_name": "圣马蒂诺博物馆藏《剥皮的马尔西亚斯》图（1637）",
        "name_en": "Flaying of Marsyas picture at Museo di San Martino (1637)",
        "card_path": "04-knowledge/units/works/flaying-of-marsyas-san-martino-1637.md",
        "title": "圣马蒂诺博物馆藏《剥皮的马尔西亚斯》图（1637）（Flaying of Marsyas picture at Museo di San Martino）",
        "description_zh": "Haskell第8章注释所据的一幅圣马蒂诺博物馆作品，记为1637年；原书没有在该注中给出正式题名或作者。",
        "description_en": "A Museo di San Martino picture underlying Haskell’s chapter 8 note and dated there to 1637; that note supplies no formal title or maker.",
        "location": "第8章印刷页205注3，Markdown行132。",
        "summary": "此画与Haskell称Roomer在1634年住宅清单中所列作品被明确区分；不将两者当作同一物，也不补定作者。",
        "quote": "The picture of this subject now in the Museo di S. Martino ... it is dated 1637",
    },
    {
        "ku_id": "units/works/marcotti-januarius-print-1665",
        "type": "work",
        "canonical_name": "马尔科蒂《圣雅努阿里乌斯版画》（1665）",
        "name_en": "Sebastiano Marcotti print of Saint Januarius (1665)",
        "card_path": "04-knowledge/units/works/marcotti-januarius-print-1665.md",
        "title": "马尔科蒂《圣雅努阿里乌斯版画》（1665）（Sebastiano Marcotti print of Saint Januarius）",
        "description_zh": "Haskell记载的一幅1665年版画，描绘圣雅努阿里乌斯，并题献给Gaspar Roomer；脚注称其底本为Ribera作品，但未识别该底本。",
        "description_en": "A print recorded by Haskell as dated 1665, depicting Saint Januarius and dedicated to Gaspar Roomer; the note attributes its model to Ribera but does not identify that underlying work.",
        "location": "第8章印刷页205注4，Markdown行133；OCR校正记录原书Januarius。",
        "summary": "版画作为独立作品建模；不与Ribera的绘画底本合并，也不推定现存印次或馆藏。",
        "quote": "There is also a print by Sebastiano Marcotti of St Januatius by Ribera, dated 1665 and dedicated to Roomer",
    },
    {
        "ku_id": "units/works/marriage-at-cana-c-1686",
        "type": "work",
        "canonical_name": "《迦拿婚宴》（The Marriage at Cana；約1686）",
        "name_en": "The Marriage at Cana (reported about 1686)",
        "card_path": "04-knowledge/units/works/marriage-at-cana-c-1686.md",
        "title": "《迦拿婚宴》（The Marriage at Cana；约1686）",
        "description_zh": "Haskell第8章脚注所指的一幅《迦拿婚宴》；对象以本书题名、年代和地点描述限定，与Mattia Preti另一幅《迦拿婚宴》候选分开。",
        "description_en": "A Marriage at Cana identified in Haskell’s chapter 8 note by title, reported date, and location; kept distinct from the separate Mattia Preti Cana painting candidate.",
        "location": "第8章印刷页204注2，Markdown行128。",
        "summary": "年代约1686；Chicago位置仅按Haskell该版本的报告记录，不作为当前馆藏断言。",
        "quote": "The Marriage at Cana of about 1686, now in Chicago",
    },
]

STRUCTURED_FACTS = {
    "units/archives/ceci-un-mercante-mecenate-gaspare-roomer-1920": [
        ("期刊", "Napoli Nobilissima", "S1；第21章印刷页418，L327；statement=st-chp21-bib-l295-334-entry-24"),
        ("出版年", "1920", "S1；第21章印刷页418，L327；statement=st-chp21-bib-l295-334-entry-24"),
        ("文章页码", "160–164", "S1；第21章印刷页418，L327；statement=st-chp21-bib-l295-334-entry-24"),
    ],
    "units/archives/vaes-corneille-de-wael-1925": [
        ("期刊", "Bulletin de l’Institut Belge de Rome", "S1；第21章印刷页439，L1186–1187；statement=st-chp21-bib-l1179-1218-entry-06"),
        ("出版年", "1925", "S1；第21章印刷页439，L1186–1187；statement=st-chp21-bib-l1179-1218-entry-06"),
        ("文章页码", "137–247", "S1；第21章印刷页439，L1186–1187；statement=st-chp21-bib-l1179-1218-entry-06；S2；Académie royale de Belgique, Maurice Vaes entry: https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf"),
    ],
    "units/archives/vaes-le-sejour-van-dyck-1924": [
        ("期刊", "Bulletin de l’Institut Belge de Rome", "S1；第21章印刷页439，L1184–1185；statement=st-chp21-bib-l1179-1218-entry-05"),
        ("出版年", "1924", "S1；第21章印刷页439，L1184–1185；statement=st-chp21-bib-l1179-1218-entry-05"),
        ("期刊页码", "163–234", "S2；Académie royale de Belgique, Maurice Vaes entry: https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf"),
    ],
    "units/works/flaying-of-marsyas-san-martino-1637": [
        ("来源所报年代", "1637", "S1；第8章印刷页205注3，L132；statement=st-chp8-p205-san-martino-flaying-not-roomer-1634-picture"),
    ],
    "units/works/marcotti-januarius-print-1665": [
        ("来源所报日期", "1665", "S1；第8章印刷页205注4，L133；statement=st-chp8-p205-marcotti-januarius-print-dedicated-to-roomer"),
    ],
    "units/works/marriage-at-cana-c-1686": [
        ("来源所报年代", "约1686", "S1；第8章印刷页204注2，L128；statement=st-chp8-p204-marriage-at-cana-date-and-location"),
    ],
}


def render_facts_table(ku_id: str) -> str:
    facts = STRUCTURED_FACTS.get(ku_id, [])
    if not facts:
        return ""
    rows = ["### 基本信息", "| 字段 | 值 | 证据 |", "|---|---|---|"]
    rows.extend(f"| {field} | {value} | {evidence} |" for field, value, evidence in facts)
    return "\n\n" + "\n".join(rows) + "\n"


def make_card(ku: dict) -> str:
    def yaml_string(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    source = (
        f"- citation: {yaml_string('Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006).')}\n"
        f"  location: {yaml_string(ku['location'])}\n"
        f"  sentence_summary: {yaml_string(ku['summary'])}\n"
        "  original_quotes:\n"
        f"  - source_span: {yaml_string(ku['location'])}\n"
        f"    text: {json.dumps(ku['quote'], ensure_ascii=False)}\n"
        "  evidence_ref:\n"
        "    doc_id: patrons-and-painters\n"
        f"    source_file: {yaml_string(ku.get('card_source_file', '02-sources/02-Markdown/08_CHP-8_sec_i.md'))}\n"
        f"    source_span: {yaml_string(ku['location'])}\n"
    )
    if ku["ku_id"] == "units/archives/vaes-le-sejour-van-dyck-1924":
        source = source.replace("02-sources/02-Markdown/08_CHP-8_sec_i.md", "02-sources/02-Markdown/21_CHP-21Bibliography.md")
    if ku["ku_id"] == "units/archives/vaes-corneille-de-wael-1925":
        source = source.replace("02-sources/02-Markdown/08_CHP-8_sec_i.md", "02-sources/02-Markdown/21_CHP-21Bibliography.md")
    if ku["ku_id"] in {"units/archives/ceci-un-mercante-mecenate-gaspare-roomer-1920", "units/persons/giuseppe-ceci", "units/persons/maurice-vaes"}:
        source = source.replace("02-sources/02-Markdown/08_CHP-8_sec_i.md", "02-sources/02-Markdown/21_CHP-21Bibliography.md")
    if ku["ku_id"] == "units/archives/vaes-le-sejour-van-dyck-1924":
        source += (
            f"- citation: {yaml_string('Académie royale de Belgique, Biographie Nationale, Maurice Vaes. https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf. Accessed 2026-10-27.')}\n"
            f"  location: {yaml_string('Maurice Vaes条目中的1924年研究及页码范围。')}\n"
            f"  sentence_summary: {yaml_string('用于核对书目身份；不证明Haskell所引p.211内容。')}\n"
        )
    if ku["ku_id"] == "units/archives/vaes-corneille-de-wael-1925":
        source += (
            f"- citation: {yaml_string('Académie royale de Belgique, Biographie Nationale, Maurice Vaes. https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf. Accessed 2026-10-27.')}\n"
            f"  location: {yaml_string('Maurice Vaes条目中的1925年研究及页码范围。')}\n"
            f"  sentence_summary: {yaml_string('用于核对书目身份；不证明Haskell所引p.171或p.185内容。')}\n"
        )
    if ku["ku_id"] == "units/persons/maurice-vaes":
        source += (
            f"- citation: {yaml_string('Académie royale de Belgique, Biographie Nationale, Maurice Vaes. https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf. Accessed 2026-10-27.')}\n"
            f"  location: {yaml_string('作者条目与1924、1925年研究书目。')}\n"
            f"  sentence_summary: {yaml_string('用于将书中M. Vaes姓名形式对齐到Maurice Vaes；不核实所引文献内容。')}\n"
            f"- citation: {yaml_string('Römisches Jahrbuch der Bibliotheca Hertziana, bibliography. https://ahnp.ub.uni-heidelberg.de/journals/rjbh/article/download/95009/89787. Accessed 2026-10-27.')}\n"
            f"  location: {yaml_string('Vaes 1931条目。')}\n"
            f"  sentence_summary: {yaml_string('以Maurice Vaes署名列出同题1931年论文，用于作者身份对读；不核实Haskell所引p.202。')}\n"
        )
    sub_type = f"sub_type: {ku['sub_type']}\n" if ku.get("sub_type") else ""
    return (
        "---\n"
        f"title: {json.dumps(ku['title'], ensure_ascii=False)}\n"
        f"name_en: {json.dumps(ku['name_en'], ensure_ascii=False)}\n"
        f"type: {ku['type']}\n"
        f"{sub_type}evidence_status: source_backed\n"
        "sources:\n"
        f"{source}"
        f"created: '{TODAY}'\nupdated: '{TODAY}'\n"
        f"process_ref: {PROCESS_REF}\n"
        "---\n\n"
        "## 内容\n\n### 描述\n"
        f"**中文：** {ku['description_zh']}\n\n"
        f"**English:** {ku['description_en']}\n"
        f"{render_facts_table(ku['ku_id'])}\n"
        "## 关系与证据\n\n### 身份与外部链接\n\n"
        "身份、版本与证据范围见本卡来源记录；不以相似题名或共同提及代替同一性判断。\n\n"
        "### 关系记录\n\n正式关系按本书对应来源与逐条S6裁决登记；本卡不补入未裁决关系。\n"
    )


def csv_bytes(path: Path, updates: dict[str, dict], additions: list[dict], key: str, sort_key: str | None = None) -> bytes:
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    physical = text.splitlines(keepends=True)
    reader = csv.DictReader(io.StringIO(text, newline=""))
    fields = reader.fieldnames
    if not fields:
        raise ValueError(f"Missing CSV header: {path}")
    prev = reader.line_num
    entries = []
    found = set()
    for row in reader:
        end = reader.line_num
        row = {k: (v or "") for k, v in row.items() if k is not None}
        row_id = row.get(key, "")
        found.add(row_id)
        changed = dict(row)
        changed.update(updates.get(row_id, {}))
        raw = "".join(physical[prev:end])
        entries.append((changed, raw if row_id not in updates else None))
        prev = end
    missing = set(updates) - found
    if missing:
        raise ValueError(f"CSV update target not found in {path}: {sorted(missing)}")
    existing_ids = {row.get(key, "") for row, _ in entries}
    for row in additions:
        if row.get(key, "") in existing_ids:
            raise ValueError(f"Duplicate {key} in {path}: {row[key]}")
        existing_ids.add(row.get(key, ""))

    def serialize(row: dict) -> str:
        out = io.StringIO(newline="")
        writer = csv.writer(out, lineterminator=newline)
        writer.writerow([row.get(field, "") for field in fields])
        return out.getvalue()

    if sort_key:
        if [row[sort_key] for row, _ in entries] != sorted(row[sort_key] for row, _ in entries):
            raise ValueError(f"Expected {path} to be sorted by {sort_key}; refusing reorder")
        additions = sorted(additions, key=lambda r: r[sort_key])
        merged = []
        ai = 0
        for row, raw in entries:
            while ai < len(additions) and additions[ai][sort_key] < row[sort_key]:
                merged.append((additions[ai], None))
                ai += 1
            merged.append((row, raw))
        merged.extend((row, None) for row in additions[ai:])
        entries = merged
    else:
        entries.extend((row, None) for row in additions)

    # All project tables use a one-line CSV header.
    body = "".join(raw if raw is not None else serialize(row) for row, raw in entries)
    result = (physical[0] + body).encode("utf-8")
    return (b"\xef\xbb\xbf" + result) if bom else result


def accepted_bytes(add_paths: list[str]) -> bytes:
    path = ROOT / "04-knowledge" / "accepted.yml"
    original = path.read_bytes()
    bom = original.startswith(b"\xef\xbb\xbf")
    text = original.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    unit_start = next(i for i, line in enumerate(lines) if line.strip() == "units:")
    unit_end = next((i for i in range(unit_start + 1, len(lines)) if lines[i] and not lines[i][0].isspace() and not lines[i].startswith("-")), len(lines))
    present = {line.strip()[2:].strip() for line in lines[unit_start + 1 : unit_end] if line.lstrip().startswith("- ")}
    for path_value in sorted(add_paths):
        if path_value in present:
            raise ValueError(f"Accepted card path already present: {path_value}")
        insert = unit_end
        for i in range(unit_start + 1, unit_end):
            line = lines[i]
            if line.lstrip().startswith("- ") and line.strip()[2:].strip() > path_value:
                insert = i
                break
        lines.insert(insert, f"- {path_value}\n")
        unit_end += 1
        present.add(path_value)
    result = "".join(lines).encode("utf-8")
    return (b"\xef\xbb\xbf" + result) if bom else result


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def clarify_s2_claim_endpoints(apply: bool) -> int:
    path = TABLES / "book-statements.jsonl"
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    targets = {
        "st-chp8-p205-n1-articles-reference-firsthand-sources": {
            "old_predicate": "roomer_articles_said_to_quote_and_reference_available_firsthand_sources",
            "new_predicate": "source_method_claim",
            "relation_candidate": False,
            "qualification": "This records Haskell's description of the two articles' source apparatus; it is not an article-to-article relation. The articles and named sources were not independently consulted.",
            "relation_candidate_note": "Not an S6 relation candidate after semantic clarification; review rejected a formal edge and retained this S2 source-method claim.",
        },
        "st-chp8-p207-n1-limits-on-other-colonna-provenance": {
            "old_predicate": "haskell_rejects_vaes_provenance_certainty_for_other_pictures",
            "new_predicate": "source_assessment_claim",
            "relation_candidate": False,
            "qualification": "This is Haskell's evidentiary position about provenance of other pictures, not a relation between the collection and Vaes. It does not cancel the separately qualified report about two Codazzi works.",
            "relation_candidate_note": "Not an S6 relation candidate after semantic clarification; review rejected a collection-to-person edge and retained this S2 assessment claim.",
        },
        "st-chp8-p205-drunk-silenus-capaccio-1634-list": {
            "old_predicate": "dated_1626_at_capodimonte_not_listed_in_roomer_house_picture_list_1634",
            "new_predicate": "source_list_comparison_claim",
            "relation_candidate": False,
            "qualification": "This is Haskell's negative cross-source report that the dated Capodimonte painting is absent from Capaccio's 1634 list. It is not a relation between the painting and the list, and it does not overturn the separate Palomino report.",
            "relation_candidate_note": "Not an S6 relation candidate after semantic clarification; retain the source-list comparison claim without a graph edge.",
        },
        "st-chp8-p205-san-martino-flaying-not-roomer-1634-picture": {
            "old_predicate": "1637_san_martino_picture_not_the_flaying_of_marsyas_listed_at_roomer_in_1634",
            "new_predicate": "source_identity_distinction_claim",
            "relation_candidate": False,
            "qualification": "Haskell explicitly distinguishes the extant 1637 San Martino picture from the earlier work in Roomer's 1634 house list. This is a negative identity statement, not a same_as edge.",
            "relation_candidate_note": "Not an S6 relation candidate after semantic clarification; retain the source's non-identity claim without a graph edge.",
        },
    }
    found: dict[str, dict] = {}
    for line in lines:
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("statement_id") in targets:
            found[record["statement_id"]] = record
    if set(found) != set(targets):
        raise ValueError(f"Expected exactly two S2 clarification targets; found {sorted(found)}")

    current = all(
        record.get("predicate") == targets[sid]["new_predicate"]
        and record.get("subject_candidate_id") is None
        and record.get("object_candidate_id") is None
        and record.get("qualifiers", {}).get("relation_candidate") == targets[sid]["relation_candidate"]
        for sid, record in found.items()
    )
    if current:
        print("S2 claim clarifications already applied; no changes.")
        return 0

    for sid, record in found.items():
        spec = targets[sid]
        already_clarified = (
            record.get("predicate") == spec["new_predicate"]
            and record.get("subject_candidate_id") is None
            and record.get("object_candidate_id") is None
        )
        if record.get("predicate") != spec["old_predicate"] and not already_clarified:
            raise ValueError(f"Unexpected predicate for {sid}: {record.get('predicate')}")
        qualifiers = record.get("qualifiers")
        if not isinstance(qualifiers, dict):
            raise ValueError(f"Expected statement qualifiers for {sid}")
        qualifiers["qualification"] = spec["qualification"]
        qualifiers["relation_candidate_note"] = spec["relation_candidate_note"]
        qualifiers["relation_candidate"] = spec["relation_candidate"]
        record["predicate"] = spec["new_predicate"]
        record["subject_candidate_id"] = None
        record["object_candidate_id"] = None
        print(f"{sid}: {spec['old_predicate']} -> {spec['new_predicate']}; subject/object -> null; S6=edge rejected")

    if not apply:
    print("Dry run only. Pass --apply together with --clarify-s2-claims to write these four records.")
        return 0

    rendered = []
    for line in lines:
        if not line.strip():
            rendered.append(line)
            continue
        record = json.loads(line)
        if record.get("statement_id") in found:
            rendered.append(json.dumps(found[record["statement_id"]], ensure_ascii=False))
        else:
            rendered.append(line)
    output = newline.join(rendered) + (newline if text.endswith(("\n", "\r")) else "")
    path.write_bytes(output.encode("utf-8"))
    print("Applied four source-claim corrections; S2 candidate mentions remain on the statements.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply the reviewed chapter 8 p.204-205 S3-S4-S6 batch.")
    parser.add_argument("--apply", action="store_true", help="Apply changes; without this flag only preview the bounded plan.")
    parser.add_argument("--clarify-s2-claims", action="store_true", help="Clarify four chapter 8 claim-shaped statements; dry-run by default.")
    args = parser.parse_args()

    if args.clarify_s2_claims:
        return clarify_s2_claim_endpoints(args.apply)

    align = load_rows(TABLES / "alignment.csv")
    candidates = load_rows(TABLES / "entity-candidates.csv")
    mentions = load_rows(TABLES / "mentions.csv")
    manifest = load_rows(TABLES / "ku-manifest.csv")
    statements_path = TABLES / "book-statements.jsonl"
    statement_lines = statements_path.read_text(encoding="utf-8").splitlines()
    statements = {json.loads(line)["statement_id"]: json.loads(line) for line in statement_lines}
    alignment_by_id = {row["alignment_id"]: row for row in align}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    statement_ids = set(statements)
    manifest_ids = {row["ku_id"] for row in manifest}
    mention_ids = {row["mention_id"] for row in mentions}

    expected_decisions = {
        "aln-5027": "new", "aln-6565": "undecided", "aln-6566": "undecided",
        "aln-7173": "new", "aln-7756": "new", "aln-7759": "new",
        "aln-7760": "new", "aln-7765": "new", "aln-7766": "new",
        "aln-7767": "undecided", "aln-12688": "new",
    }
    for alignment_id, decision in expected_decisions.items():
        row = alignment_by_id.get(alignment_id)
        if row is None or row["decision"] != decision:
            raise ValueError(f"Unexpected starting alignment state for {alignment_id}")
    if "cand-12454" in candidate_by_id or "aln-12784" in alignment_by_id or "aln-12785" in alignment_by_id:
        raise ValueError("Planned new candidate/alignment ID is already in use")
    if any(ku["ku_id"] in manifest_ids or (ROOT / ku["card_path"]).exists() for ku in KUS):
        raise ValueError("A planned KU or card path already exists")
    new_statement_ids = {
        "st-chp8-p204-marriage-at-cana-influence-barocci",
        "st-chp8-p205-marcotti-print-created-by-marcotti",
        "st-chp8-p205-marcotti-print-has-subject-januarius",
        "st-chp21-bib-l1179-1218-vaes1924-authored-by",
        "st-chp21-bib-l1179-1218-vaes1925-authored-by",
        "st-chp21-bib-l1179-1218-vaes1931-authored-by",
        "st-chp21-bib-l295-334-ceci-authored-by",
    }
    if new_statement_ids & statement_ids:
        raise ValueError(f"Planned S2 statement ID already exists: {sorted(new_statement_ids & statement_ids)}")
    new_mention_ids = {
        "m-chp8-p205-note-vaes-person",
        "m-chp21-bib-l1179-1218-029", "m-chp21-bib-l1179-1218-030",
        "m-chp21-bib-l1179-1218-031", "m-chp21-bib-l295-334-032",
    }
    if new_mention_ids & mention_ids:
        raise ValueError(f"Planned mention ID already exists: {sorted(new_mention_ids & mention_ids)}")

    print("批次范围：第8章 p.204–205；跨章 Vaes 1924/1925/1931 与 S2 作者候选、版画及Chicago端点。")
    print(f"S4新KU：{len(KUS)}；S2新增statement：{len(new_statement_ids)}；新增mention：{len(new_mention_ids)}。")
    print("S3裁决：cand-6386→new Maurice Vaes；cand-6387→same Vaes 1925文章；cand-7591→new Saint Januarius；cand-12454→new Giuseppe Ceci。")
    print("S6拟正式边：作品地点1、作品影响2、版画创作者/题材/题献3、作品收藏1、文献作者4、Haskell引用Vaes 1925 1；另有未定作品关系pending，并将4条来源主张/否定识别从关系候选撤出。")
    print("现有Vaes 1931 Haskell citation edge保留，脚注引用不重复登记。")
    # S3 decisions and cross-chapter identity groups.
    alignment_updates = {
        "aln-5027": {
            "ku_id": "units/archives/vaes-le-sejour-van-dyck-1924", "external_source": "Académie royale de Belgique (Biographie Nationale)",
            "external_id": "https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf", "accessed_date": TODAY,
            "resolution_note": alignment_by_id["aln-5027"]["resolution_note"] + " | Identity corroboration: the Académie royale de Belgique entry for Maurice Vaes lists the 1924 Van Dyck study, fasc. IV, pp.163–234, matching Haskell's bibliography; this identifies the publication, not p.211's cited content. S4 mapped to units/archives/vaes-le-sejour-van-dyck-1924.",
        },
        "aln-6565": {
            "decision": "new", "ku_id": "units/persons/maurice-vaes", "external_source": "Académie royale de Belgique (Biographie Nationale)",
            "external_id": "https://www.academieroyale.be/academie/documents/FichierPDFBiographieNationaleTome2096.pdf", "accessed_date": TODAY,
            "resolution_note": "S3 identity only: Haskell's Vaes/M. Vaes citations in ch.2 p.211 n.3, ch.6 p.156 n.2, ch.7 p.170 n.1 and ch.8 pp.207–208 are compared with the ch.21 bibliography. The Académie royale de Belgique entry identifies Maurice Vaes and lists the exact 1924 Van Dyck and 1925 Corneille de Wael studies; a Heidelberg scholarly bibliography lists Maurice Vaes's 1931 Appunti under the Haskell title. New same-type person identity group=new-person:maurice-vaes; this does not verify any cited page or article content. S4 mapped to units/persons/maurice-vaes.",
        },
        "aln-6566": {
            "decision": "same", "ku_id": "units/archives/vaes-corneille-de-wael-1925",
            "resolution_note": "S3 resolved by cross-chapter bibliographic identity: Haskell ch.6 p.156 n.2 cites Vaes (1925), p.171; the ch.21 bibliography identifies M. Vaes, Corneille de Wael (1592–1667), 1925, pp.137–247, and the Académie royale de Belgique lists the same article and range. Page 171 is within that article. Same archive identity=units/archives/vaes-corneille-de-wael-1925; group=archive-group-vaes-corneille-de-wael-1925. Article and cited page not read.",
        },
        "aln-7173": {
            "resolution_note": alignment_by_id["aln-7173"]["resolution_note"] + " S3 cross-chapter author identity: M. Vaes on this Haskell ch.21 bibliography entry is grouped with Maurice Vaes in person group=new-person:maurice-vaes; bibliographic identity only, cited p.202 not read.",
        },
        "aln-7756": {
            "ku_id": "units/works/marriage-at-cana-c-1686",
            "resolution_note": alignment_by_id["aln-7756"]["resolution_note"] + " S4 mapped to units/works/marriage-at-cana-c-1686. S3 scope: Haskell's source-defined 1686 Chicago work; distinct from the separate Mattia Preti Marriage Feast at Cana candidate cand-7448. No exact surviving-version or external object identity asserted.",
        },
        "aln-7759": {
            "ku_id": "units/archives/ceci-un-mercante-mecenate-gaspare-roomer-1920",
            "resolution_note": alignment_by_id["aln-7759"]["resolution_note"] + " S4 mapped to units/archives/ceci-un-mercante-mecenate-gaspare-roomer-1920; the p.418 bibliography gives 1920, pp.160–164. The parenthetical year in p.205 n.1 remains textually ambiguous and does not overwrite the bibliography.",
        },
        "aln-7760": {
            "ku_id": "units/archives/vaes-corneille-de-wael-1925",
            "resolution_note": "S3 new archive group=archive-group-vaes-corneille-de-wael-1925. Haskell ch.8 pp.205/208 short citations and ch.21 bibliography identify the 1925 periodical article, pp.137–247; the external Académie record confirms the same periodical pagination. This is not a separately paginated reprint; cited pp.185 and article contents not read. S4 mapped to units/archives/vaes-corneille-de-wael-1925.",
        },
        "aln-7765": {
            "ku_id": "units/works/flaying-of-marsyas-san-martino-1637",
            "resolution_note": alignment_by_id["aln-7765"]["resolution_note"] + " S4 mapped to units/works/flaying-of-marsyas-san-martino-1637; kept distinct from the unidentified 1634 Roomer-listed painting cand-7412.",
        },
        "aln-7766": {
            "ku_id": "units/works/marcotti-januarius-print-1665",
            "resolution_note": alignment_by_id["aln-7766"]["resolution_note"] + " S4 mapped to units/works/marcotti-januarius-print-1665; not merged with a Ribera painting or another print impression.",
        },
        "aln-7767": {
            "decision": "new", "ku_id": "units/persons/saint-januarius",
            "resolution_note": "S3 new source-defined person group=new-person:saint-januarius. The printed p.205 n.4 names St Januarius as the image subject; S0 OCR Januatius is corrected from the print image. No same-type person KU or conflicting candidate exists in the current registry. S4 mapped to units/persons/saint-januarius; no biography inferred.",
        },
        "aln-12688": {
            "ku_id": "units/archives/vaes-corneille-de-wael-1925",
            "resolution_note": alignment_by_id["aln-12688"]["resolution_note"] + " group=archive-group-vaes-corneille-de-wael-1925; S4 mapped to units/archives/vaes-corneille-de-wael-1925.",
        },
        "aln-1877": {
            "ku_id": "units/persons/sebastiano-marcotti",
            "resolution_note": alignment_by_id["aln-1877"]["resolution_note"] + " S4 mapped to units/persons/sebastiano-marcotti.",
        },
        "aln-4807": {
            "ku_id": "units/places/chicago",
            "resolution_note": alignment_by_id["aln-4807"]["resolution_note"] + " S4 mapped to units/places/chicago. This is the city; it is not the Art Institute as institution or archive.",
        },
    }
    alignment_updates["aln-5027"]["resolution_note"] = alignment_updates["aln-5027"]["resolution_note"].replace("S4 mapped to units/archives/vaes-le-sejour-van-dyck-1924.", "group=archive-group-a64508fc3933; S4 mapped to units/archives/vaes-le-sejour-van-dyck-1924.")

    new_alignment = [
        {
            "alignment_id": "aln-12784", "candidate_id": "cand-6386", "ku_id": "units/persons/maurice-vaes",
            "external_source": "Römisches Jahrbuch der Bibliotheca Hertziana", "external_id": "https://ahnp.ub.uni-heidelberg.de/journals/rjbh/article/download/95009/89787",
            "decision": "new", "accessed_date": TODAY, "process_ref": PROCESS_REF, "legacy_ku_id": "",
            "resolution_note": "Identity corroboration only: the scholarly bibliography lists the Haskell-title 1931 Appunti under Maurice Vaes, confirming the M. Vaes name form in the ch.7 citation/bibliography. It does not verify p.202 or the article's content. group=new-person:maurice-vaes.",
        },
        {
            "alignment_id": "aln-12785", "candidate_id": "cand-12454", "ku_id": "units/persons/giuseppe-ceci",
            "external_source": "", "external_id": "", "decision": "new", "accessed_date": TODAY,
            "process_ref": PROCESS_REF, "legacy_ku_id": "",
            "resolution_note": "source_ref=chp-21:21_CHP-21Bibliography:l295-334#L327; mention=m-chp21-bib-l295-334-032; statement=st-chp21-bib-l295-334-entry-24; the bibliography gives the full name Ceci, Giuseppe as author of the Roomer article. No same-type person KU/candidate is represented; group=new-person:giuseppe-ceci. This is an author identity only, not a biographical claim. S4 mapped to units/persons/giuseppe-ceci.",
        },
    ]

    candidate_updates = {
        "cand-6386": {"detail": "Cross-chapter source form Vaes/M. Vaes; Haskell ch.21 bibliography and authority bibliography identify Maurice Vaes. The 1924, 1925 and 1931 cited articles are separate archive objects, not person aliases."},
        "cand-6387": {"detail": "Citation pointer at Haskell ch.6 p.156 n.2, Vaes (1925), p.171; page lies within the ch.21 bibliography article range pp.137–247 and identifies cand-7584's same periodical article. Citation pointer is reused, not a separate publication."},
        "cand-7580": {"detail": "Haskell ch.8 p.204 n.2 identifies a source-defined Marriage at Cana, about 1686 and then in Chicago. Kept distinct from the Mattia Preti Marriage Feast at Cana candidate cand-7448. The cited van der Rohe article was not read, and no exact surviving version or attribution is asserted."},
        "cand-7584": {"detail": "Haskell ch.21 bibliography identifies M. Vaes, Corneille de Wael (1592–1667), Bulletin de l’Institut Belge de Rome, 1925, pp.137–247. Haskell's ch.6 p.156 n.2 citation to p.171 is the same article. Distinct from separately paginated reprints; cited pages and article not read."},
        "cand-7591": {"detail": "Printed p.205 n.4 reads St Januarius and names the saint as the subject of the Marcotti print; S0 OCR Januatius is corrected against the page image. This is a person subject candidate, distinct from Ribera and the print."},
    }

    # S2 atomization and bibliography author edges.
    statement_updates = {
        "st-chp8-p204-marriage-at-cana-date-and-location": {
            "predicate": "located_at",
            "qualifiers": {
                **statements["st-chp8-p204-marriage-at-cana-date-and-location"]["qualifiers"],
                "claim": "Haskell reports The Marriage at Cana as then located in Chicago.",
                "qualification": "The location is bounded to Haskell's 1980 edition; it is not asserted as current. The approximate date remains a separate reported S5 field.",
                "relation_candidate_note": "Atomic work-to-place location claim; the source-reported date is retained separately.",
            },
        },
        "st-chp8-p204-marriage-at-cana-influence": {
            "predicate": "influenced_by",
            "qualifiers": {
                **statements["st-chp8-p204-marriage-at-cana-influence"]["qualifiers"],
                "claim": "Haskell says the painting shows the impact of Veronese.",
                "mentioned_candidate_ids": ["cand-7580", "cand-2755"],
                "qualification": "Haskell's stylistic assessment only; this record concerns Veronese, while Barocci is atomized in a linked sibling statement. Neither cited source nor the assessed painting was independently consulted.",
            },
        },
        "st-chp8-p205-marcotti-januarius-print-dedicated-to-roomer": {
            "predicate": "dedicated_to",
            "qualifiers": {
                **statements["st-chp8-p205-marcotti-januarius-print-dedicated-to-roomer"]["qualifiers"],
                "claim": "Haskell reports that the print was dedicated to Gaspar Roomer.",
                "mentioned_candidate_ids": ["cand-7590", "cand-2223"],
                "qualification": "This atom is the dedication only; printmaker, depicted saint, date and the unidentified Ribera model are represented separately. OCR correction remains attached to the cited print reading.",
            },
        },
        "st-chp8-p205-n1-articles-reference-firsthand-sources": {
            "subject_candidate_id": None,
            "object_candidate_id": None,
            "predicate": "source_method_claim",
            "qualifiers": {
                **statements["st-chp8-p205-n1-articles-reference-firsthand-sources"]["qualifiers"],
                "qualification": "This records Haskell's description of the two articles' source apparatus; it is not an article-to-article relation. The articles and named sources were not independently consulted.",
                "relation_candidate": False,
                "relation_candidate_note": "Not an S6 relation candidate after semantic clarification; review rejected a formal edge and retained this S2 source-method claim.",
            },
        },
        "st-chp8-p205-n1-roomer-source-citations": {
            "qualifiers": {
                **statements["st-chp8-p205-n1-roomer-source-citations"]["qualifiers"],
                "mentioned_candidate_ids": ["cand-2223", "cand-7583", "cand-7584", "cand-6386"],
            },
        },
        "st-chp21-bib-l1179-1218-entry-05": {
            "qualifiers": {**statements["st-chp21-bib-l1179-1218-entry-05"]["qualifiers"], "mentioned_candidate_ids": ["cand-4844", "cand-6386"]},
        },
        "st-chp21-bib-l1179-1218-entry-06": {
            "qualifiers": {**statements["st-chp21-bib-l1179-1218-entry-06"]["qualifiers"], "mentioned_candidate_ids": ["cand-7584", "cand-6386"]},
        },
        "st-chp21-bib-l1179-1218-entry-07": {
            "qualifiers": {**statements["st-chp21-bib-l1179-1218-entry-07"]["qualifiers"], "mentioned_candidate_ids": ["cand-6997", "cand-6386"]},
        },
        "st-chp21-bib-l295-334-entry-24": {
            "qualifiers": {**statements["st-chp21-bib-l295-334-entry-24"]["qualifiers"], "mentioned_candidate_ids": ["cand-7583", "cand-12454"]},
        },
        "st-chp8-p207-n1-limits-on-other-colonna-provenance": {
            "subject_candidate_id": None,
            "object_candidate_id": None,
            "predicate": "source_assessment_claim",
            "qualifiers": {
                **statements["st-chp8-p207-n1-limits-on-other-colonna-provenance"]["qualifiers"],
                "qualification": "This is Haskell's evidentiary position about provenance of other pictures, not a relation between the collection and Vaes. It does not cancel the separately qualified report about two Codazzi works.",
                "relation_candidate": False,
                "relation_candidate_note": "Not an S6 relation candidate after semantic clarification; review rejected a collection-to-person edge and retained this S2 assessment claim.",
            },
        },
        "st-chp8-p205-drunk-silenus-capaccio-1634-list": {
            "subject_candidate_id": None,
            "object_candidate_id": None,
            "predicate": "source_list_comparison_claim",
            "qualifiers": {
                **statements["st-chp8-p205-drunk-silenus-capaccio-1634-list"]["qualifiers"],
                "qualification": "This is Haskell's negative cross-source report that the dated Capodimonte painting is absent from Capaccio's 1634 list. It is not a relation between the painting and the list, and it does not overturn the separate Palomino report.",
                "relation_candidate": False,
                "relation_candidate_note": "Not an S6 relation candidate after semantic clarification; retain the source-list comparison claim without a graph edge.",
            },
        },
        "st-chp8-p205-san-martino-flaying-not-roomer-1634-picture": {
            "subject_candidate_id": None,
            "object_candidate_id": None,
            "predicate": "source_identity_distinction_claim",
            "qualifiers": {
                **statements["st-chp8-p205-san-martino-flaying-not-roomer-1634-picture"]["qualifiers"],
                "qualification": "Haskell explicitly distinguishes the extant 1637 San Martino picture from the earlier work in Roomer's 1634 house list. This is a negative identity statement, not a same_as edge.",
                "relation_candidate": False,
                "relation_candidate_note": "Not an S6 relation candidate after semantic clarification; retain the source's non-identity claim without a graph edge.",
            },
        },
    }
    for statement_id, update in statement_updates.items():
        if statement_id not in statements:
            raise ValueError(f"Missing S2 statement: {statement_id}")

    def author_statement(statement_id: str, segment_id: str, line_start: int, line_end: int, printed_page: int,
                         quote: str, source_file: str, archive_candidate: str, author_candidate: str,
                         claim: str) -> dict:
        return {
            "statement_id": statement_id,
            "segment_id": segment_id,
            "subject_candidate_id": archive_candidate,
            "object_candidate_id": author_candidate,
            "predicate": "authored_by",
            "qualifiers": {
                "source_line_start": line_start, "source_line_end": line_end,
                "printed_page": printed_page,
                "claim": claim,
                "speaker": "Haskell bibliography",
                "text_layer": "bibliographic responsibility statement",
                "qualification": "The author form and publication identity are taken from Haskell's bibliography; the cited article itself was not consulted.",
                "mentioned_candidate_ids": [archive_candidate, author_candidate],
                "relation_candidate": True,
                "relation_candidate_note": "The bibliography byline explicitly names the person as author of this archive item.",
            },
            "original_quote": quote,
            "origin": "book",
            "source_file": source_file,
        }

    added_statements = [
        {
            "statement_id": "st-chp8-p204-marriage-at-cana-influence-barocci",
            "segment_id": "chp-8:08_CHP-8_sec_i:l126-157", "subject_candidate_id": "cand-7580",
            "object_candidate_id": "cand-0247", "predicate": "influenced_by",
            "qualifiers": {"source_line_start": 128, "source_line_end": 128, "printed_page": 204, "pdf_physical_page": 2,
                           "claim": "Haskell says the painting shows the impact of Barocci.", "speaker": "Haskell", "text_layer": "footnote",
                           "qualification": "Haskell's stylistic assessment only; this is the Barocci atom of a sentence also naming Veronese. Neither cited source nor the assessed painting was independently consulted.",
                           "footnote_number": 2, "linked_body_statement_ids": ["st-chp8-p204-crespi-paintings-reflect-travel-influences"],
                           "mentioned_candidate_ids": ["cand-7580", "cand-0247"], "relation_candidate": True,
                           "relation_candidate_note": "Atomic work-to-artist stylistic influence claim as reported by Haskell."},
            "original_quote": "which shows the impact of Veronese and Barocci", "origin": "book",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        },
        {
            "statement_id": "st-chp8-p205-marcotti-print-created-by-marcotti",
            "segment_id": "chp-8:08_CHP-8_sec_i:l126-157", "subject_candidate_id": "cand-7590",
            "object_candidate_id": "cand-1542", "predicate": "created_by",
            "qualifiers": {"source_line_start": 133, "source_line_end": 133, "printed_page": 205, "pdf_physical_page": 3,
                           "claim": "Haskell identifies Sebastiano Marcotti as the maker of the 1665 print.", "speaker": "Haskell", "text_layer": "footnote",
                           "qualification": "The claim concerns the print, not the unidentified Ribera model; the source gives no surviving impression or catalogue number.",
                           "footnote_number": 4, "mentioned_candidate_ids": ["cand-7590", "cand-1542"], "relation_candidate": True,
                           "relation_candidate_note": "Atomic printmaker relation expressly stated by Haskell."},
            "original_quote": "There is also a print by Sebastiano Marcotti", "origin": "book",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        },
        {
            "statement_id": "st-chp8-p205-marcotti-print-has-subject-januarius",
            "segment_id": "chp-8:08_CHP-8_sec_i:l126-157", "subject_candidate_id": "cand-7590",
            "object_candidate_id": "cand-7591", "predicate": "has_subject",
            "qualifiers": {"source_line_start": 133, "source_line_end": 133, "printed_page": 205, "pdf_physical_page": 3,
                           "claim": "Haskell identifies Saint Januarius as the subject of the Marcotti print.", "speaker": "Haskell", "text_layer": "footnote",
                           "qualification": "The print is distinct from the saint and from the unidentified Ribera model; OCR Januatius is corrected to the printed Januarius.",
                           "footnote_number": 4, "mentioned_candidate_ids": ["cand-7590", "cand-7591"], "relation_candidate": True,
                           "relation_candidate_note": "Atomic work-to-person subject relation expressly stated by Haskell."},
            "original_quote": "of St Januatius by Ribera", "origin": "book",
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
        },
        author_statement("st-chp21-bib-l1179-1218-vaes1924-authored-by", "chp-21:21_CHP-21Bibliography:l1179-1218", 1184, 1185, 439,
                         "Vaes, M.",
                         "02-sources/02-Markdown/21_CHP-21Bibliography.md", "cand-4844", "cand-6386",
                         "Haskell's bibliography identifies M. Vaes as author of Le séjour de Van Dyck en Italie (1924)."),
        author_statement("st-chp21-bib-l1179-1218-vaes1925-authored-by", "chp-21:21_CHP-21Bibliography:l1179-1218", 1186, 1187, 439,
                         "Vaes, M.",
                         "02-sources/02-Markdown/21_CHP-21Bibliography.md", "cand-7584", "cand-6386",
                         "Haskell's bibliography identifies M. Vaes as author of Corneille de Wael (1592-1667) (1925)."),
        author_statement("st-chp21-bib-l1179-1218-vaes1931-authored-by", "chp-21:21_CHP-21Bibliography:l1179-1218", 1188, 1189, 439,
                         "Vaes, M.",
                         "02-sources/02-Markdown/21_CHP-21Bibliography.md", "cand-6997", "cand-6386",
                         "Haskell's bibliography identifies M. Vaes as author of Appunti di Carel van Mander su vari pittori italiani suoi contemporanei (1931)."),
        author_statement("st-chp21-bib-l295-334-ceci-authored-by", "chp-21:21_CHP-21Bibliography:l295-334", 327, 327, 418,
                         "Ceci, Giuseppe",
                         "02-sources/02-Markdown/21_CHP-21Bibliography.md", "cand-7583", "cand-12454",
                         "Haskell's bibliography identifies Giuseppe Ceci as author of Un mercante mecenate del secolo XVII: Gaspare Roomer (1920)."),
    ]

    mention_additions = [
        {"mention_id": "m-chp8-p205-note-vaes-person", "segment_id": "chp-8:08_CHP-8_sec_i:l126-157", "candidate_id": "cand-6386", "surface_form": "Vaes", "start_char": "651", "end_char": "655", "note": "Surname within Haskell's p.205 n.1 author citation; resolved to Maurice Vaes in S3."},
        {"mention_id": "m-chp21-bib-l1179-1218-029", "segment_id": "chp-21:21_CHP-21Bibliography:l1179-1218", "candidate_id": "cand-6386", "surface_form": "Vaes, M.", "start_char": "309", "end_char": "317", "note": "Author form in the Haskell bibliography entry for the 1924 Van Dyck article; S3 resolves the identity to Maurice Vaes."},
        {"mention_id": "m-chp21-bib-l1179-1218-030", "segment_id": "chp-21:21_CHP-21Bibliography:l1179-1218", "candidate_id": "cand-6386", "surface_form": "Vaes, M.", "start_char": "412", "end_char": "420", "note": "Author form in the Haskell bibliography entry for the 1925 Corneille de Wael article; S3 resolves the identity to Maurice Vaes."},
        {"mention_id": "m-chp21-bib-l1179-1218-031", "segment_id": "chp-21:21_CHP-21Bibliography:l1179-1218", "candidate_id": "cand-6386", "surface_form": "Vaes, M.", "start_char": "513", "end_char": "521", "note": "Author form in the Haskell bibliography entry for the 1931 Van Mander article; S3 resolves the identity to Maurice Vaes."},
        {"mention_id": "m-chp21-bib-l295-334-032", "segment_id": "chp-21:21_CHP-21Bibliography:l295-334", "candidate_id": "cand-12454", "surface_form": "Ceci, Giuseppe", "start_char": "2362", "end_char": "2376", "note": "Author form in the Haskell bibliography entry for the 1920 Roomer article; source spelling retained."},
    ]

    candidates_add = [{
        "candidate_id": "cand-12454", "index_entry_id": "", "canonical_name": "Giuseppe Ceci", "index_page_range": "",
        "suggested_type": "person", "status": "open", "index_source_file": "", "sub_entry": "",
        "detail": "Haskell's p.418 bibliography names Giuseppe Ceci as author of the 1920 Gaspar Roomer article; no broader biography is asserted.",
        "exclude_reason": "", "candidate_origin": "body-mention", "candidate_source_ref": "chp-21:21_CHP-21Bibliography:l295-334#L327",
    }]

    candidate_bytes = csv_bytes(TABLES / "entity-candidates.csv", candidate_updates, candidates_add, "candidate_id")
    alignment_bytes = csv_bytes(TABLES / "alignment.csv", alignment_updates, new_alignment, "alignment_id")
    mention_bytes = csv_bytes(TABLES / "mentions.csv", {}, mention_additions, "mention_id")
    manifest_additions = [{k: ku.get(k, "") for k in ["ku_id", "type", "canonical_name", "name_en", "source_task", "card_path"]} | {"source_task": "patrons-and-painters-full-book-s2"} for ku in KUS]
    manifest_bytes = csv_bytes(TABLES / "ku-manifest.csv", {}, manifest_additions, "ku_id")
    accepted = accepted_bytes([ku["card_path"] for ku in KUS])

    changed_lines = []
    for raw in statements_path.read_text(encoding="utf-8").splitlines():
        obj = json.loads(raw)
        sid = obj["statement_id"]
        if sid in statement_updates:
            obj.update(statement_updates[sid])
        changed_lines.append(json.dumps(obj, ensure_ascii=False) if sid in statement_updates else raw)
    changed_lines.extend(json.dumps(item, ensure_ascii=False) for item in added_statements)
    statement_bytes = ("\n".join(changed_lines) + "\n").encode("utf-8")

    writes = {
        TABLES / "entity-candidates.csv": candidate_bytes,
        TABLES / "alignment.csv": alignment_bytes,
        TABLES / "mentions.csv": mention_bytes,
        TABLES / "ku-manifest.csv": manifest_bytes,
        ROOT / "04-knowledge" / "accepted.yml": accepted,
        statements_path: statement_bytes,
    }
    for ku in KUS:
        writes[ROOT / ku["card_path"]] = make_card(ku).encode("utf-8")
    print(f"Preflight constructed {len(writes)} writes; CSV uniqueness/order, target presence and new card paths are validated.")
    for path, content in writes.items():
        current = path.read_bytes() if path.exists() else b""
        print(f"  {path.relative_to(ROOT)}: {len(current)} -> {len(content)} bytes")
    if not args.apply:
        print("Dry run only. Review the bounded path/size list, then pass --apply to write the changes.")
        return 0
    if args.apply:
        for path, content in writes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        print(f"Applied {len(writes)} bounded writes, including {len(KUS)} new KU cards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
