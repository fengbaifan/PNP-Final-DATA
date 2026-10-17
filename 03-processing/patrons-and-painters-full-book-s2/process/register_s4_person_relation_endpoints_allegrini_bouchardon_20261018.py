from __future__ import annotations

import argparse
import csv
import io
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
DATE = "2026-10-18"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
INDEX_DIR = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
ANCHOR = "s4-person-relation-endpoints-allegrini-antonazzi-arconato-arrighi-maffeo-bouchardon-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

TARGETS = [
    {
        "candidate": "cand-0084",
        "group": "new-person:allegrini-francesco-59c88290a5",
        "ku": "units/persons/francesco-allegrini",
        "card": "04-knowledge/units/persons/francesco-allegrini.md",
        "name_zh": "弗朗切斯科·阿莱格里尼",
        "name_en": "Francesco Allegrini",
        "name_field": "原文全名",
        "index_entry": "A.csv#85",
        "index_file": "A.csv",
        "index_name": "Allegrini, Francesco",
        "index_page": "157",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
        "source_span": "line 8; print p. 157",
        "source_quote": "Francesco' Allegrini",
        "source_fragments": ["Francesco' Allegrini"],
        "location": "第6章 p.157；OCR L8",
        "summary": "Haskell将Francesco Allegrini列为Antonio degli Effetti收藏中其他画家的一个例子；此处没有识别具体画作。",
        "description_zh": (
            "本卡登记Haskell第6章所指的Francesco Allegrini。第157页将他列为Antonio degli Effetti收藏中“其他画家”的一个例子，"
            "没有识别任何单件作品。索引以“Allegrini, Francesco”列出该人物并指向同页；中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records the Francesco Allegrini named in Chapter 6. On page 157, Haskell gives him as one example among the other painters represented in Antonio degli Effetti's collection; no individual picture is identified. The index lists the person as “Allegrini, Francesco” at the same page. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp6-p157-collection-includes-work-by-allegrini"],
        "relation_context_zh": "该S2候选只称收藏中有Allegrini的作品，不指认单件作品或完整作品目录；关系留待S6。",
        "relation_context_en": "This S2 candidate says only that the collection included work by Allegrini; it identifies neither an individual picture nor a complete catalogue. The relation remains for S6.",
        "statement_endpoints": [("st-chp6-p157-collection-includes-work-by-allegrini", "cand-6389", "cand-0084", "collection_includes_work_by", "Francesco' Allegrini")],
    },
    {
        "candidate": "cand-0112",
        "group": "new-person:antonazzi-antonio-maria-603399deaf",
        "ku": "units/persons/antonio-maria-antonazzi",
        "card": "04-knowledge/units/persons/antonio-maria-antonazzi.md",
        "name_zh": "安东尼奥·玛丽亚·安东纳齐",
        "name_en": "Antonio Maria Antonazzi",
        "name_field": "原文全名",
        "index_entry": "A.csv#113",
        "index_file": "A.csv",
        "index_name": "Antonazzi, Antonio Maria",
        "index_page": "116n",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "source_span": "line 297; print p. 116 n. 3",
        "source_quote": "He had also taken with him the miniaturist Antonio Maria Antonazzi",
        "source_fragments": ["miniaturist Antonio Maria Antonazzi"],
        "location": "第4章 p.116 注3；OCR L297",
        "summary": "Haskell注3称Massimi曾带上微型画家Antonio Maria Antonazzi；代词指向Massimi，未给出目的地或日期。",
        "description_zh": (
            "本卡登记Haskell注3点名的微型画家Antonio Maria Antonazzi。上下文将“带上他”的主语指向Massimi；该注没有说明目的地或日期。"
            "索引以“Antonazzi, Antonio Maria”列出人物并指向第116页注3；中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records the miniaturist Antonio Maria Antonazzi named in Haskell's note 3. The context resolves the subject of “had also taken” as Massimi; the note gives no destination or date. The index lists the person as “Antonazzi, Antonio Maria” at page 116 note 3. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp4-sec-ii-p116note-fn3-antonazzi"],
        "relation_context_zh": "S2记录Haskell注3所述Massimi与Antonazzi同行；目的地、日期及正式关系尚未另行确认，留待S6。",
        "relation_context_en": "S2 records Haskell's note 3 saying Massimi took Antonazzi with him; no destination or date is given, and the formal relation remains for S6.",
        "statement_endpoints": [("st-chp4-sec-ii-p116note-fn3-antonazzi", "cand-1564", "cand-0112", "took_along_with", "miniaturist Antonio Maria Antonazzi")],
    },
    {
        "candidate": "cand-0115",
        "group": "new-person:arconato-galeazzo-8143cc061e",
        "ku": "units/persons/galeazzo-arconato",
        "card": "04-knowledge/units/persons/galeazzo-arconato.md",
        "name_zh": "加莱亚佐·阿尔科纳托",
        "name_en": "Galeazzo Arconato",
        "name_field": "原文全名",
        "index_entry": "A.csv#116",
        "index_file": "A.csv",
        "index_name": "Arconato, Galeazzo",
        "index_page": "106",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "source_span": "line 96; print p. 106",
        "source_quote": "had then been largely reconstructed by Galeazzo Arconato, another acquaintance of Cassiano",
        "source_fragments": ["reconstructed by Galeazzo Arconato", "another acquaintance of Cassiano"],
        "location": "第4章 p.106；OCR L96",
        "summary": "Haskell称，Ambrogio Mazenta散佚的Leonardo手稿收藏后来很大程度上由Galeazzo Arconato重建，并称Arconato是Cassiano的另一位熟人。",
        "description_zh": (
            "本卡登记Haskell第4章点名的Galeazzo Arconato。第106页称，Ambrogio Mazenta散佚的Leonardo手稿收藏后来很大程度上由Arconato重建，"
            "并称他是Cassiano的另一位熟人。以上为书内叙述；两个关系候选均未在本次转成正式关系。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records the Galeazzo Arconato named in Chapter 4. On page 106, Haskell says that Ambrogio Mazenta's dispersed collection of Leonardo manuscripts was later largely reconstructed by Arconato, and calls him another acquaintance of Cassiano. These remain statements in the book; neither relation candidate is made formal in this registration. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp4-sec-ii-l91-99-arconato-reconstructed-mazenta-collection", "st-chp4-sec-ii-l91-99-cassiano-acquaintance-of-arconato"],
        "relation_context_zh": "收藏重建与Cassiano熟人两条S2陈述保持原文限定，均留待S6逐条裁决。",
        "relation_context_en": "The S2 statements about reconstructing the collection and being Cassiano's acquaintance retain their source wording and both remain for separate S6 decisions.",
        "statement_endpoints": [
            ("st-chp4-sec-ii-l91-99-arconato-reconstructed-mazenta-collection", "cand-5788", "cand-0115", "largely_reconstructed_by", "Galeazzo Arconato"),
            ("st-chp4-sec-ii-l91-99-cassiano-acquaintance-of-arconato", "cand-2036", "cand-0115", "acquaintance_of", "another acquaintance of Cassiano"),
        ],
    },
    {
        "candidate": "cand-0122",
        "group": "new-person:arrighi-landini-orazio-e060d35cff",
        "ku": "units/persons/orazio-arrighi-landini",
        "card": "04-knowledge/units/persons/orazio-arrighi-landini.md",
        "name_zh": "奥拉齐奥·阿里吉-兰迪尼",
        "name_en": "Orazio Arrighi-Landini",
        "name_field": "索引名",
        "index_entry": "A.csv#123",
        "index_file": "A.csv",
        "index_name": "Arrighi-Landini, Orazio",
        "index_page": "",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "source_span": "line 593; print p. 301 n. 6",
        "source_quote": "In a note on page 30 of his Tempio della Filosofia, 1757, the poet Arrighi-Landini tells how Smith supplied him with a copy of Pope's famous epitaph.",
        "source_fragments": ["the poet Arrighi-Landini", "Tempio della Filosofia, 1757"],
        "location": "第10章 p.301 注6；OCR L593",
        "summary": "Haskell称Arrighi-Landini在其《Tempio della Filosofia》中的一条注释记载Smith给他一份Pope墓志铭副本；本地书目同名题名著录为1755年，版次对应未决，所引页未查。",
        "description_zh": (
            "本卡登记索引名为Orazio Arrighi-Landini的人物。Haskell第10章注6称，Arrighi-Landini在《Tempio della Filosofia》中的一条注释记载Smith给他Pope墓志铭副本；"
            "Haskell引1757年，本地书目同名题名为1755年，版次对应尚未解决，所引页也未查。原文没有说明墓志铭主题与Newton有关。索引条目A.csv#123的页码栏为空，"
            "因此本卡不把该索引当作页码核验；中文名为工作音译。"
        ),
        "description_en": (
            "This card records the person named in the index as Orazio Arrighi-Landini. Chapter 10, note 6, says that a note in Arrighi-Landini's *Tempio della Filosofia* reports Smith supplying him with a copy of Pope's famous epitaph. Haskell cites 1757, while the local bibliography has a title match dated 1755; edition identity remains unresolved and the cited page was not read. The source does not connect the epitaph to Newton. The page-number field for index entry A.csv#123 is blank, so the index is not treated here as a page-level check. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp10-p301-note6-arrighi_pope_epitaph_report"],
        "relation_context_zh": "所引《Tempio della Filosofia》页未查，1757/1755版次对应未决；该S2陈述留待S6，且不把墓志铭连到Newton。",
        "relation_context_en": "The cited *Tempio della Filosofia* page was not consulted and the 1757/1755 edition correspondence is unresolved; this S2 candidate remains for S6 and is not linked to Newton's epitaph.",
        "statement_endpoints": [("st-chp10-p301-note6-arrighi_pope_epitaph_report", "cand-2440", "cand-0122", "smith_reportedly_supplied_arrighi_landini_a_copy_of_popes_epitaph", "the poet Arrighi-Landini")],
    },
    {
        "candidate": "cand-0238",
        "group": "new-person:barberini-maffeo-1c4c752e81",
        "ku": "units/persons/maffeo-barberini-son-of-taddeo",
        "card": "04-knowledge/units/persons/maffeo-barberini-son-of-taddeo.md",
        "name_zh": "马费奥·巴贝里尼亲王（塔代奥之子）",
        "name_en": "Prince Maffeo Barberini (son of Taddeo Barberini)",
        "name_field": "索引名",
        "index_entry": "B.csv#85",
        "index_file": "B.csv",
        "index_name": "Barberini, Prince Maffeo (son of Taddeo Barberini)",
        "index_page": "61",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_vii.md",
        "source_span": "line 35; print p. 61",
        "source_quote": "Maffeo, son of Taddeo2",
        "source_fragments": ["Maffeo, son of Taddeo"],
        "location": "第2章 p.61；OCR L35",
        "summary": "Haskell明确称Maffeo为Taddeo之子；索引将其列作Barberini家Prince Maffeo并指向该页。亲子关系候选保留至S6。",
        "description_zh": (
            "本卡登记索引所列Barberini家Prince Maffeo（Taddeo之子）。Haskell第2章明确称“Maffeo, son of Taddeo”；"
            "书内身份说明限于这一索引名与亲子称述，不补写生平或其他家族关系。该亲子关系仍是S2候选，留待S6裁决。中文名为工作译写。"
        ),
        "description_en": (
            "This card records the index entry for Prince Maffeo of the Barberini family, identified there as Taddeo Barberini's son. Chapter 2 explicitly says “Maffeo, son of Taddeo.” The book-based identity is limited to this indexed name and kinship wording; no biography or additional family relations are inferred. The parent-child statement remains an S2 candidate for S6. The Chinese name is a working rendering."
        ),
        "relation_ids": ["st-chp2-secvii-l32-36-maffeo-son-of-taddeo"],
        "relation_context_zh": "Haskell直接称Maffeo为Taddeo之子；亲子关系只保留为S2候选，正式关系留待S6。",
        "relation_context_en": "Haskell directly identifies Maffeo as Taddeo's son; this remains an S2 candidate, with any formal relation decision reserved for S6.",
        "statement_endpoints": [("st-chp2-secvii-l32-36-maffeo-son-of-taddeo", "cand-0238", "cand-0239", "son-of", "Maffeo, son of Taddeo")],
    },
    {
        "candidate": "cand-0420",
        "group": "new-person:bouchardon-edme-6f9687ca41",
        "ku": "units/persons/edme-bouchardon",
        "card": "04-knowledge/units/persons/edme-bouchardon.md",
        "name_zh": "埃德梅·布沙东",
        "name_en": "Edmé Bouchardon",
        "name_field": "索引名",
        "index_entry": "B.csv#267",
        "index_file": "B.csv",
        "index_name": "Bouchardon, Edmé",
        "index_page": "356",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "source_span": "line 102; print p. 356",
        "source_quote": "the French sculptor Bouchardon",
        "source_fragments": ["the French sculptor Bouchardon"],
        "location": "第14章 p.356；OCR L102；注3",
        "summary": "Haskell称Algarotti曾为法国雕塑家Bouchardon提供介绍信，以说明他鼓励外国艺术家赴意大利学习；注3所引两封信未对应到Bouchardon。",
        "description_zh": (
            "本卡登记索引名为Edmé Bouchardon的法国雕塑家。Haskell第14章称Algarotti曾为Bouchardon提供介绍信，作为其鼓励外国艺术家赴意大利学习的例子；"
            "注3列出1750年10月25日及1752年4月23日两封信，但没有说明哪一封对应Bouchardon，信件未独立查阅。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records the French sculptor indexed as Edmé Bouchardon. Chapter 14 says that Algarotti provided Bouchardon with a letter of introduction as an example of his efforts to encourage foreign artists to study in Italy. Note 3 lists letters dated 25 October 1750 and 23 April 1752 but does not identify which, if either, concerned Bouchardon; the letters were not independently consulted. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp14-p356-algarotti-provided-introduction-for-bouchardon"],
        "relation_context_zh": "S2陈述未把注3的两封信与Bouchardon逐一对应；正式关系留待S6。",
        "relation_context_en": "The S2 statement does not map either letter in note 3 specifically to Bouchardon; the formal relation remains for S6.",
        "statement_endpoints": [("st-chp14-p356-algarotti-provided-introduction-for-bouchardon", "cand-0063", "cand-0420", "provided_letter_of_introduction_for", "letters of introduction, for instance, for the French sculptor Bouchardon")],
    },
]


def insert_accepted(lines: list[str], card_path: str) -> list[str]:
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    entry = f"- {card_path}"
    assert entry not in lines
    insert_at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_path),
        claims_idx,
    )
    lines.insert(insert_at, entry)
    return lines


def read_index_rows(file_name: str) -> list[dict[str, str]]:
    raw = (INDEX_DIR / file_name).read_bytes()
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("cp1252")
    return list(csv.DictReader(io.StringIO(content)))


def make_card(t: dict) -> str:
    sources = [
        {
            "citation": INDEX_CITATION,
            "location": f"全书索引 {t['index_entry']}" + (f"；所列页码{t['index_page']}" if t["index_page"] else "；页码栏为空"),
            "sentence_summary": f"索引主项为“{t['index_name']}”" + (f"，页码指向{t['index_page']}。" if t["index_page"] else "；本项未给页码。"),
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}",
                "source_span": t["index_entry"],
            },
        },
        {
            "citation": BOOK,
            "location": t["location"],
            "sentence_summary": t["summary"],
            "original_quotes": [{"source_span": t["source_span"], "text": t["source_quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": t["source_file"],
                "source_span": t["source_span"],
            },
        },
    ]
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = f"../../../{t['source_file']}"
    index_link = f"../../../02-sources/03-Index/03-2-Index-CSV/{t['index_file']}"
    relation_list = ", ".join(f"`{sid}`" for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']} [{t['location']}]({source_link}) [索引 {t['index_entry']}]({index_link})

**English:** {t['description_en']} [{t['location']}]({source_link}) [索引 {t['index_entry']}]({index_link})

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| {t['name_field']} | {t['index_name']} | S1（索引 {t['index_entry']}） |

### 本书相关内容

**中文：** {t['relation_context_zh']} [{t['location']}]({source_link})

**English:** {t['relation_context_en']} [{t['location']}]({source_link})

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

当前没有登记在 `relations.csv` 中的正式关系。直接 S2 候选 {relation_list} 留待 S6 审查；本次 S4 登记不裁决或创建正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register six source-backed new person groups in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(candidate_by_id) == len(alignment_by_id)
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    assert len(manifest_by_ku) == len(manifest)
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = [
        json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    statement_by_id = {row["statement_id"]: row for row in statements}

    for t in TARGETS:
        cid = t["candidate"]
        c = candidate_by_id[cid]
        a = alignment_by_id[cid]
        assert c.get("suggested_type") == "person"
        assert a.get("decision") == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == t["group"]
        assert c.get("index_entry_id") == t["index_entry"]
        assert c.get("canonical_name") == t["index_name"]
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)
        index_rows = read_index_rows(t["index_file"])
        assert t["index_entry"].split("#")[1].isdigit()
        index_row = index_rows[int(t["index_entry"].split("#")[1])]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        source = (ROOT / t["source_file"]).read_text(encoding="utf-8-sig")
        assert all(fragment in source for fragment in t["source_fragments"]), cid
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        }
        expected_direct = {row[0] for row in t["statement_endpoints"]}
        assert direct == expected_direct, (cid, direct, expected_direct)
        for sid, subject, obj, predicate, quote_fragment in t["statement_endpoints"]:
            statement = statement_by_id[sid]
            assert statement.get("subject_candidate_id") == subject
            assert statement.get("object_candidate_id") == obj
            assert statement.get("predicate") == predicate
            assert quote_fragment in statement.get("original_quote", ""), (
                sid, quote_fragment, statement.get("original_quote", "")
            )
        assert t["ku"] not in manifest_by_ku
        assert t["card"] not in accepted_paths
        assert not (ROOT / t["card"]).exists()
        assert not any(
            row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold()
            for row in manifest
        )

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        a = next(row for row in planned_alignments if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        a["ku_id"] = t["ku"]
        a["process_ref"] = PROCESS_REF
        a["resolution_note"] += f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；书内索引与所引正文共同支持本批 source-local 人物登记，关系候选仍待 S6。"
        planned_manifest.append({
            "ku_id": t["ku"],
            "type": "person",
            "canonical_name": t["name_zh"],
            "name_en": t["name_en"],
            "source_task": TASK,
            "card_path": t["card"],
        })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    planned_accepted = accepted_lines
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, t["card"])
    assert len(accepted_paths) + len(TARGETS) == len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")})

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 745 and totals["registered_members"] == 916
    assert totals["pending_groups"] == 4031 and totals["pending_members"] == 4045
    assert stats["person"]["registered_groups"] == 339
    assert stats["person"]["registered_members"] == 425
    assert stats["person"]["pending_groups"] == 729
    assert stats["person"]["pending_members"] == 730
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    group_lines = []
    for t in TARGETS:
        statements_text = ", ".join(f"`{sid}`" for sid in t["relation_ids"])
        group_lines.append(
            f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；"
            f"S2直接关系候选 {statements_text} 留待S6；{t['relation_context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：六组直接关系端点身份组登记（{DATE}）\n\n"
        + "\n".join(group_lines)
        + "\n\n本批登记6个单候选S3 new人物组，每组映射至一张KU；姓名表所列名称均有索引或正文来源。"
        "Arrighi-Landini索引条目页码栏为空，登记保留这一限制；其书目版次对应仍未解决。"
        "未添加外部身份事实或formal relations；卡片中的姓名行将按来源登记为结构化字段。其余未决对象不受本批影响。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, n = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert n == 1
    result_text += (
        f"\n\n### S4 人物身份组登记：六个直接关系端点（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。六组均为S3单候选new组；相关S2关系候选留待S6。"
        "Arrighi-Landini索引页码栏为空，且1757/1755年版次对应未解决；本批仅登记书内点名的人物，不将书目信息升级为外部验证。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: six singleton person groups; candidate/index/source/S2 relation checks passed; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; person_registered="
            f"{stats['person']['registered_groups']}/{stats['person']['registered_members']}"
        )
        print("formal_relations_added=0; enrichment_rows_changed=0; no files changed")
        return 0

    for rel_path, card in cards.items():
        (ROOT / rel_path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=6; candidate_mappings=6; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
