from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_endpoints_ciarpi_castello_conduitt_corelli_corradini_coypel_20261017 as base  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-person-endpoints-assereto-barelli-baretti-bartoli-basadonna-bassi-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
BT = chr(96)
base.DATE = DATE
base.ANCHOR = ANCHOR
base.PROCESS_REF = PROCESS_REF

TARGETS = [
    {
        "candidate": "cand-0143", "members": ["cand-0143"], "group": "new-person:assereto-gioacchino-c4b08a3476",
        "ku": "units/persons/gioacchino-assereto", "card": "04-knowledge/units/persons/gioacchino-assereto.md",
        "name_zh": "焦阿基诺·阿塞雷托", "name_en": "Gioacchino Assereto", "name_field": "索引名",
        "index_entries": [{"entry": "A.csv#144", "file": "A.csv", "name": "Assereto, Gioacchino", "page": "197"}],
        "source_fragments": ["in Genoa, Piola, Assereto and Valerio Castelli"],
        "book_sources": [{"source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md", "source_span": "line 74; print p. 197",
            "location": "第7章第IV节 p.197；OCR L74", "summary": "Haskell将Assereto列入Lord Exeter在Genoa收藏的艺术家名单；该列表没有指认具体作品或交易。",
            "quote": "in Genoa, Piola, Assereto and Valerio Castelli"}],
        "description_zh": "本卡登记索引名为Gioacchino Assereto的人物。第7章第IV节 p.197将Assereto列入Lord Exeter在Genoa收藏的艺术家名单；该段没有说明具体作品或交易。全名来自同页索引，正文使用姓氏。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Gioacchino Assereto. Chapter 7, section IV, p.197, lists Assereto among the artists represented in Lord Exeter’s Genoese collecting; the passage identifies no individual work or transaction. The full name comes from the same-page index, while the body uses the surname. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p197-exeter-collected-assereto-genoa"],
        "relation_context_zh": "Haskell的列表将Assereto與Exeter在Genoa的收藏相连，但没有指出具体作品或交易性质；S2候选留待S6。",
        "relation_context_en": "Haskell’s list associates Assereto with Exeter’s Genoese collecting but names no specific work or transaction type; the S2 candidate remains for S6.",
        "statement_endpoints": [("st-chp7-p197-exeter-collected-assereto-genoa", "cand-0984", "cand-0143", "collector_artist_association_in_city", "Piola, Assereto and Valerio Castelli")],
        "alignment_notes": {"cand-0143": "全名取自同页索引A.csv#144；正文在p.197以Assereto姓氏列名，未外部核验。"},
    },
    {
        "candidate": "cand-0243", "members": ["cand-0243", "cand-0244"], "group": "new-person:agostino-barelli-5bf161332b",
        "ku": "units/persons/agostino-barelli", "card": "04-knowledge/units/persons/agostino-barelli.md",
        "name_zh": "阿戈斯蒂诺·巴雷利", "name_en": "Agostino Barelli", "name_field": "索引名",
        "index_entries": [
            {"entry": "B.csv#90", "file": "B.csv", "name": "Barelli, Agostino", "sub_entry": "palace at Nymphenburg", "page": "193"},
            {"entry": "B.csv#91", "file": "B.csv", "name": "Barelli, Agostino", "sub_entry": "Theatine church in Munich", "page": "193"},
        ],
        "source_fragments": ["the Bolognese architect Agostino Barelli came to", "built a church for the Theatines", "central block of the royal palace at Nymphenburg"],
        "book_sources": [{"source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md", "source_span": "lines 15-16; print p. 193",
            "location": "第7章第IV节 p.193；OCR L15-16", "summary": "Haskell称建筑师Agostino Barelli于1662年来到Munich，为Theatines建造一座教堂，并建造Nymphenburg宫的中央部分；没有将整座宫殿归于他。",
            "quote": "the Bolognese architect Agostino Barelli came to\nMunich and built a church for the Theatines, based on the Roman prototype of S. Andrea della Valle, and also the central block of the royal palace at Nymphenburg"}],
        "description_zh": "本卡登记建筑师Agostino Barelli。第7章第IV节 p.193称他于1662年来到Munich，为Theatines建造一座教堂，并建造Nymphenburg宫的中央部分；不将整座宫殿归于他。索引以两个同名子项分别定位这两项活动，二者指向同一位正文点名的人物。中文名为本项目工作音译。",
        "description_en": "This card records the architect Agostino Barelli. Chapter 7, section IV, p.193, says that he came to Munich in 1662, built a church for the Theatines, and built the central block of Nymphenburg Palace; it does not attribute the entire palace to him. The index has two same-name subentries for these activities, both pointing to the person named in the passage. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p193-barelli-nymphenburg", "st-chp7-p193-barelli-theatine-church"],
        "relation_context_zh": "同一句分别指认Theatines教堂与Nymphenburg宫中央部分；不扩展为建造整座宫殿，两个S2候选留待S6。",
        "relation_context_en": "The same sentence identifies a Theatine church and the central block of Nymphenburg Palace; it does not attribute the entire palace to Barelli. Both S2 candidates remain for S6.",
        "statement_endpoints": [
            ("st-chp7-p193-barelli-nymphenburg", "cand-0243", "cand-1715", "built_central_block_of", "central block of the royal palace at Nymphenburg"),
            ("st-chp7-p193-barelli-theatine-church", "cand-0243", "cand-7159", "built_for_theatines_based_on_prototype", "built a church for the Theatines"),
        ],
        "alignment_notes": {
            "cand-0243": "同页正文全名支持此人物KU；S2工作限定保留。",
            "cand-0244": "按S3复核记录与cand-0243共用KU；索引子项只作同一人物的定位，不增加独立端点。",
        },
    },
    {
        "candidate": "cand-0245", "members": ["cand-0245"], "group": "new-person:baretti-giuseppe-aa0168e566",
        "ku": "units/persons/giuseppe-baretti", "card": "04-knowledge/units/persons/giuseppe-baretti.md",
        "name_zh": "朱塞佩·巴雷蒂", "name_en": "Giuseppe Baretti", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#92", "file": "B.csv", "name": "Baretti, Giuseppe", "page": "318, 328"}],
        "source_fragments": ["Giuseppe Baretti and other unorthodox thinkers were rapidly expelled from her territory", "Baretti, chief scourge of the effeminate culture of Venice and close friend of Dr Johnson, wrote enthusiastically of him"],
        "book_sources": [
            {"source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "source_span": "line 140; print p. 318", "location": "第10章第II节 p.318；OCR L140", "summary": "Haskell将Giuseppe Baretti列入被驱逐出威尼斯领土的非正统思想者。", "quote": "Giuseppe Baretti and other unorthodox thinkers were rapidly expelled from her territory"},
            {"source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "source_span": "line 243; print p. 328", "location": "第10章第II节 p.328；OCR L243", "summary": "Haskell称Baretti写信热烈称赞Zuccarelli，并以评论者和Dr Johnson友人的身份介绍他；引文来源见注3。", "quote": "Thus Baretti, chief scourge of the effeminate culture of Venice and close friend of Dr Johnson, wrote enthusiastically of him"},
        ],
        "description_zh": "本卡登记Giuseppe Baretti。第10章第II节 p.318称他被驱逐出威尼斯领土；p.328称他热烈称赞Zuccarelli，并将他描述为批评威尼斯文化的人及Dr Johnson的亲友。后一书信依据由Haskell转引，未独立查阅。中文名为本项目工作音译。",
        "description_en": "This card records Giuseppe Baretti. Chapter 10, section II, p.318, says he was expelled from Venetian territory; p.328 says he wrote enthusiastically in praise of Zuccarelli and describes him as a critic of Venetian culture and a friend of Dr Johnson. The latter correspondence is reported through Haskell and was not independently consulted. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp10-p318-baretti-expelled-from-venetian-territory", "st-chp10-p328-baretti-wrote-enthusiastically-of-zuccarelli"],
        "relation_context_zh": "逐出威尼斯领土为Haskell的概括；关于Zuccarelli的赞语由Haskell转引Baretti，所引原信未查。两项S2候选留待S6。",
        "relation_context_en": "The expulsion is Haskell’s summary; Baretti’s praise of Zuccarelli is reported through Haskell, and the cited letter was not consulted. Both S2 candidates remain for S6.",
        "statement_endpoints": [
            ("st-chp10-p318-baretti-expelled-from-venetian-territory", "cand-0245", "cand-8838", "expelled_from_territory", "Giuseppe Baretti and other unorthodox thinkers were rapidly expelled"),
            ("st-chp10-p328-baretti-wrote-enthusiastically-of-zuccarelli", "cand-0245", "cand-2879", "wrote_enthusiastically_of", "Baretti, chief scourge of the effeminate culture of Venice"),
        ],
    },
    {
        "candidate": "cand-0251", "members": ["cand-0251"], "group": "new-person:bartoli-pietro-santo-29a748b5ca",
        "ku": "units/persons/pietro-santo-bartoli", "card": "04-knowledge/units/persons/pietro-santo-bartoli.md",
        "name_zh": "彼得罗·桑托·巴托利", "name_en": "Pietro Santo Bartoli", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#98", "file": "B.csv", "name": "Bartoli, Pietro Santo", "page": "117, 118"}],
        "source_fragments": ["Pietro Santo Bartoli of the fllustrations", "160 drawings by Pietro Santo Bartoli of antique paintings"],
        "book_sources": [
            {"source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md", "source_span": "line 226; print p. 118", "location": "第4章第II节 p.118；OCR L226", "summary": "Haskell称Massimi委托Bartoli复制一部晚期古代Virgil手稿插图；手稿未作更具体识别，原OCR异文校正记录在S2。", "quote": "He had copies made by Pietro Santo Bartoli of the fllustrations of one of the-oldest and most famous manuscripts in the Vatican library—a late antique edition of Virgil"},
            {"source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md", "source_span": "line 300; print p. 117 n. 2", "location": "第4章第II节 p.117 注2；OCR L300", "summary": "注2称该藏家拥有Bartoli绘制的160幅古代绘画图样，并引Michaelis p.50。", "quote": "Thus he owned 160 drawings by Pietro Santo Bartoli of antique paintings"},
        ],
        "description_zh": "本卡登记Pietro Santo Bartoli。第4章第II节 p.118称Massimi曾委托他复制梵蒂冈一部晚期古代Virgil手稿的插图，但未进一步识别手稿；p.117注2称Massimi拥有Bartoli绘制的160幅古代绘画图样。两项均为Haskell书内陈述，注释所引文献未独立查阅。中文名为本项目工作音译。",
        "description_en": "This card records Pietro Santo Bartoli. Chapter 4, section II, p.118, says Massimi had him copy illustrations from a late antique Virgil manuscript in the Vatican, which is not identified further; note 2 on p.117 says Massimi owned 160 drawings by Bartoli of antique paintings. Both are Haskell’s statements, and the cited reference was not independently consulted. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp4-sec-ii-p118-bartoli-copied-illustrations", "st-chp4-sec-ii-p117note-fn2-bartoli-authorship"],
        "relation_context_zh": "手稿未逐件识别；注2所列160幅图样及作者归属保留为Haskell的书目陈述，不扩展作品清单。两项S2候选留待S6。",
        "relation_context_en": "The manuscript is not individually identified; the 160 drawings and their attribution remain Haskell’s bibliographic statements and do not form a complete work list. Both S2 candidates remain for S6.",
        "statement_endpoints": [
            ("st-chp4-sec-ii-p118-bartoli-copied-illustrations", "cand-11672", "cand-0251", "created_by", "Pietro Santo Bartoli of the fllustrations"),
            ("st-chp4-sec-ii-p117note-fn2-bartoli-authorship", "cand-5983", "cand-0251", "created_by", "drawings by Pietro Santo Bartoli"),
        ],
    },
    {
        "candidate": "cand-0254", "members": ["cand-0254"], "group": "new-person:basadonna-pietro-a1f78c71c6",
        "ku": "units/persons/pietro-basadonna", "card": "04-knowledge/units/persons/pietro-basadonna.md",
        "name_zh": "枢机彼得罗·巴萨多纳", "name_en": "Cardinal Pietro Basadonna", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#101", "file": "B.csv", "name": "Basadonna, Cardinal Pietro", "page": "162"}],
        "source_fragments": ["Cardinal Basadonna’s bedroom was full of ‘tableaux de nudités’", "Cardinal Basadonna’s tomb with a penetrating bust"],
        "book_sources": [
            {"source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md", "source_span": "line 19; print p. 162", "location": "第6章第V节 p.162；OCR L19", "summary": "Haskell转述一名法国使节对Cardinal Basadonna卧室的报告，并明确以“if we are to believe”限定该说法。", "quote": "Cardinal Basadonna’s bedroom was full of ‘tableaux de nudités’"},
            {"source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md", "source_span": "line 54; print p. 162 n. 7", "location": "第6章第V节 p.162 注7；OCR L54", "summary": "注7称Cardinal Basadonna之墓及一尊引人注目的半身像位于Palazzo Venezia的S. Marco教堂；法国使节报告经Michaud转引。", "quote": "Cardinal Basadonna’s tomb with a penetrating bust is in the church of S. Marco in the Palazzo Venezia"},
        ],
        "description_zh": "本卡登记索引名为Cardinal Pietro Basadonna的人物。第6章第V节 p.162转述法国使节对其卧室的说法，并以“if we are to believe”限定；注7称其墓与一尊半身像位于Palazzo Venezia的S. Marco教堂。使节报告经Michaud转引，未独立查阅；半身像雕塑者未具名。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Cardinal Pietro Basadonna. Chapter 6, section V, p.162, reports a French envoy’s statement about his bedroom and qualifies it with “if we are to believe”; note 7 places his tomb and a bust in the church of S. Marco at Palazzo Venezia. The envoy’s report is cited through Michaud and was not independently consulted; the bust’s sculptor is unnamed. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp6-p162-v1-24", "st-chp6-p162-n7-tomb"],
        "relation_context_zh": "卧室内容为Haskell转述的法国使节说法，保留作者限定；墓与半身像的雕塑者未具名。两项S2候选留待S6。",
        "relation_context_en": "The bedroom account is Haskell’s report of a French envoy and retains the author’s qualification; the sculptor of the bust is unnamed. Both S2 candidates remain for S6.",
        "statement_endpoints": [
            ("st-chp6-p162-v1-24", "cand-6507", "cand-0254", "french_envoy_report_of_nude_pictures", "Cardinal Basadonna’s bedroom was full"),
            ("st-chp6-p162-n7-tomb", "cand-0254", "cand-6573", "tomb_located_in_church", "Cardinal Basadonna’s tomb with a penetrating bust"),
        ],
    },
    {
        "candidate": "cand-0259", "members": ["cand-0259"], "group": "new-person:bassi-francesco-cremonese-il-6c7c921364",
        "ku": "units/persons/francesco-bassi-il-cremonese", "card": "04-knowledge/units/persons/francesco-bassi-il-cremonese.md",
        "name_zh": "弗朗切斯科·巴西（il Cremonese）", "name_en": "Francesco Bassi (il Cremonese)", "name_field": "索引名",
        "index_entries": [{"entry": "B.csv#106", "file": "B.csv", "name": "Bassi, Francesco (il Cremonese)", "page": "227, 228, 233"}],
        "source_fragments": ["one landscape by Francesco Bassi, il", "old and il Cremonese was blind", "Francesco Bassi despite the doubts he had about the value of his work"],
        "book_sources": [
            {"source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "source_span": "lines 203-204; print p. 227", "location": "第8章第II节 p.227；OCR L203-204", "summary": "Haskell将Francesco Bassi与称谓il Cremonese并列，记Conti拟购其一幅风景画。", "quote": "one landscape by Francesco Bassi, il\nCremonese, to make a complete set of four"},
            {"source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "source_span": "line 207; print p. 228", "location": "第8章第II节 p.228；OCR L207", "summary": "Haskell转述Marchesini称il Cremonese失明。", "quote": "old and il Cremonese was blind"},
            {"source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md", "source_span": "lines 274-275; print p. 233", "location": "第8章第II节 p.233；OCR L274-275", "summary": "Haskell推测Ferdinand可能出于忠诚而避免伤害年迈的风景画家Francesco Bassi，尽管他对Bassi作品价值有所疑虑。", "quote": "It may have been that same feeling of loyalty that made him take particular trouble not to hurt the ageing landscape painter\nFrancesco Bassi despite the doubts he had about the value of his work"},
        ],
        "description_zh": "本卡登记索引名为Francesco Bassi (il Cremonese)的人物。第8章第II节 p.227将Francesco Bassi与il Cremonese并列；p.228转述Marchesini称il Cremonese失明；p.233则由Haskell推测Ferdinand可能出于忠诚而避免伤害年迈的Bassi，尽管他怀疑其作品价值。推测和转述均保留原有语气。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Francesco Bassi (il Cremonese). Chapter 8, section II, p.227 pairs Francesco Bassi with the name il Cremonese; p.228 reports Marchesini as saying il Cremonese was blind; p.233 has Haskell suggest that Ferdinand may have avoided hurting the ageing Bassi out of loyalty despite doubts about his work. The reported and conjectural wording is retained. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp8-p228-bassi-blindness", "st-chp8-p233-bassi-loyalty"],
        "relation_context_zh": "失明说为Haskell转述Marchesini；忠诚动机明确为Haskell推测，作品价值疑虑也保留为来源判断。两项S2候选留待S6。",
        "relation_context_en": "The blindness claim is Haskell’s report of Marchesini; the loyalty motive is explicitly Haskell’s conjecture, as are the doubts about the work. Both S2 candidates remain for S6.",
        "statement_endpoints": [
            ("st-chp8-p228-bassi-blindness", "cand-1540", "cand-0259", "marchesini_reports_bassi_as_blind", "il Cremonese was blind"),
            ("st-chp8-p233-bassi-loyalty", "cand-1609", "cand-0259", "may_have_protected_bassi_out_of_loyalty_despite_doubts", "Francesco Bassi despite the doubts he had about the value of his work"),
        ],
    },
]


def make_card(t: dict) -> str:
    sources = []
    for entry in t["index_entries"]:
        sub_entry = entry.get("sub_entry", "")
        extra = f"，子项为“{sub_entry}”" if sub_entry else ""
        sources.append({
            "citation": INDEX_CITATION,
            "location": f"全书索引 {entry['entry']}{extra}；所列页码{entry['page']}",
            "sentence_summary": f"索引主项为“{entry['name']}”{extra}，页码指向{entry['page']}。",
            "original_quotes": [{"source_span": entry["entry"], "text": entry["name"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{entry['file']}", "source_span": entry["entry"]},
        })
    for source in t["book_sources"]:
        sources.append({
            "citation": base.BOOK,
            "location": source["location"],
            "sentence_summary": source["summary"],
            "original_quotes": [{"source_span": source["source_span"], "text": source["quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": source["source_file"], "source_span": source["source_span"]},
        })
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": sources, "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = base.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    links = [f"[{entry['entry']}](../../../02-sources/03-Index/03-2-Index-CSV/{entry['file']})" for entry in t["index_entries"]]
    links.extend(f"[{source['location']}](../../../{source['source_file']})" for source in t["book_sources"])
    evidence = " ".join(links)
    if len(t["index_entries"]) > 1:
        name_evidence = "、".join(f"索引 {x['entry']}" for x in t["index_entries"])
        source_markers = "、".join(f"S{i}" for i in range(1, len(t["index_entries"]) + 1))
    else:
        name_evidence = f"索引 {t['index_entries'][0]['entry']}"
        source_markers = "S1"
    relations = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']} {evidence}

**English:** {t['description_en']} {evidence}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| {t['name_field']} | {t['index_entries'][0]['name']} | {source_markers}（{name_evidence}） |

### 本书相关内容

**中文：** {t['relation_context_zh']} {evidence}

**English:** {t['relation_context_en']} {evidence}

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

当前没有登记在 relations.csv 中的正式关系。直接S2候选 {relations} 留待S6审查；本次S4登记不裁决或创建正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register six source-backed new person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = base.sync.read_csv(ALIGNMENT_PATH)
    _, candidates = base.sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = base.sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert len(candidate_by_id) == len(alignment_by_id) and len(manifest_by_ku) == len(manifest)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    before_stats = base.sync.summarize_by_type(candidates, alignments)

    for t in TARGETS:
        member_ids = t["members"]
        for cid in member_ids:
            c, a = candidate_by_id[cid], alignment_by_id[cid]
            assert c.get("suggested_type") == "person"
            assert a.get("decision") == "new" and not a.get("ku_id")
            assert base.sync.get_group(a.get("resolution_note", "")) == t["group"]
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and base.sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert set(group_members) == set(member_ids), (t["group"], group_members)
        for entry in t["index_entries"]:
            row = base.read_index_rows(entry["file"])[int(entry["entry"].split("#")[1])]
            assert row.get("Main Entry") == entry["name"] and row.get("Page Numbers", "") == entry["page"]
            if entry.get("sub_entry"):
                assert row.get("Sub-entry") == entry["sub_entry"]
        combined_source_text = "\n".join((ROOT / file).read_text(encoding="utf-8-sig") for file in {s["source_file"] for s in t["book_sources"]})
        normalized_source = re.sub(r"\s+", " ", combined_source_text)
        assert all(re.sub(r"\s+", " ", fragment) in normalized_source for fragment in t["source_fragments"]), t["candidate"]
        for source in t["book_sources"]:
            assert re.sub(r"\s+", " ", source["quote"]) in normalized_source, (t["candidate"], source["source_span"])
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and (row.get("subject_candidate_id") in member_ids or row.get("object_candidate_id") in member_ids)
        }
        expected_direct = {row[0] for row in t["statement_endpoints"]}
        assert direct == expected_direct, (t["group"], direct, expected_direct)
        for sid, subject, obj, predicate, quote_fragment in t["statement_endpoints"]:
            statement = statement_by_id[sid]
            assert statement.get("subject_candidate_id") == subject and statement.get("object_candidate_id") == obj
            normalized_quote = re.sub(r"\s+", " ", statement.get("original_quote", ""))
            assert statement.get("predicate") == predicate and re.sub(r"\s+", " ", quote_fragment) in normalized_quote, sid
        assert t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold() for row in manifest)

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    map_count = sum(len(t["members"]) for t in TARGETS)
    for t in TARGETS:
        for cid in t["members"]:
            a = next(row for row in planned_alignments if row.get("candidate_id") == cid and not row.get("external_source"))
            a["ku_id"] = t["ku"]
            a["process_ref"] = PROCESS_REF
            detail = t.get("alignment_notes", {}).get(cid, "书内索引与正文支持source-local人物登记，保留S2语境和未决限定。")
            group_token = f"group={t['group']}"
            if a["resolution_note"].endswith(group_token):
                a["resolution_note"] += ";"
            a["resolution_note"] += f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；{detail}直接关系候选留待S6。"
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = accepted_lines
    for t in TARGETS:
        planned_accepted = base.insert_accepted(planned_accepted, t["card"])
    assert len(accepted_paths) + len(TARGETS) == len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")})

    stats = base.sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(row[key] for row in before_stats.values()) for key in next(iter(before_stats.values()))}
    assert stats["person"]["registered_groups"] == before_stats["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == before_stats["person"]["registered_members"] + map_count
    assert totals["registered_groups"] == before_totals["registered_groups"] + len(TARGETS)
    assert totals["registered_members"] == before_totals["registered_members"] + map_count
    assert totals["pending_groups"] == before_totals["pending_groups"] - len(TARGETS)
    assert totals["pending_members"] == before_totals["pending_members"] - map_count
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(base.yaml.safe_load(match.group(1)), dict)
    process_text = base.process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    group_lines = []
    for t in TARGETS:
        candidate_label = "、".join(f"{BT}{cid}{BT}" for cid in t["members"])
        relation_labels = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
        group_lines.append(
            f"- {candidate_label}（{BT}{t['group']}{BT}）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；"
            f"S2直接关系候选 {relation_labels} 留待S6；{t['relation_context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物：六组直接关系端点登记（{DATE}）\n\n"
        + "\n".join(group_lines)
        + "\n\n本批登记6个S3 new人物身份组、7条候选映射；Barelli两条同名索引子项按S3裁决共用一张KU。姓名结构化字段仅登记索引主项；"
        "本批不添加外部身份事实或formal relations。Assereto全名来自同页索引；Barelli建筑范围、Baretti转引、Bartoli的OCR校正与作品范围、"
        "Basadonna的使节转述限定及Bassi的转述/推测语气均按来源保留。\n\n"
        f"登记后人物类型S4为{base.sync.fmt(stats['person']['registered_groups'])}组/"
        f"{base.sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{base.sync.fmt(stats['person']['pending_groups'])}组/{base.sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{base.sync.fmt(totals['registered_groups'])}组/{base.sync.fmt(totals['registered_members'])}条已登记、"
        f"{base.sync.fmt(totals['pending_groups'])}组/{base.sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )
    result_text = base.sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, count = re.subn(r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)", rf"\g<1>{base.sync.fmt(totals['pending_members'])}\g<2>", result_text, count=1)
    assert count == 1
    enrichment_rows = sum(1 for line in ENRICHMENT_PATH.read_text(encoding="utf-8-sig").splitlines() if line.strip()) + len(TARGETS)
    result_lines = result_text.splitlines()
    enrichment_indexes = [i for i, line in enumerate(result_lines) if line.startswith("| [既有字段表]")]
    assert len(enrichment_indexes) == 1
    result_lines[enrichment_indexes[0]] = (
        f"| [既有字段表](../tables/enrichment.jsonl) | {base.sync.fmt(enrichment_rows)}条，其中1,615条 unverified |"
    )
    result_text = "\n".join(result_lines)
    result_text += (
        f"\n\n### S4人物身份组登记：六个直接关系端点（{DATE}）\n\n"
        + "；".join(f"{BT}{' / '.join(t['members'])}{BT} → {BT}../units/persons/{t['ku'].split('/')[-1]}.md{BT}" for t in TARGETS)
        + "。六组对应七条候选映射，均为new身份组；S2关系候选留待S6，本批不创建formal relations。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: groups={len(TARGETS)}; candidate_mappings={map_count}; index/source/S2 relation checks passed; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; person_registered="
            f"{stats['person']['registered_groups']}/{stats['person']['registered_members']}; enrichment={enrichment_rows}"
        )
        print("formal_relations_added=0; no files changed")
        return 0

    for rel_path, card in cards.items():
        (ROOT / rel_path).write_text(card, encoding="utf-8", newline="\n")
    base.sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    base.sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(TARGETS)}; candidate_mappings={map_count}; registered="
        f"{totals['registered_groups']}/{totals['registered_members']}; pending="
        f"{totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
