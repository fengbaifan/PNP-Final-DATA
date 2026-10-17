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
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
DATE = "2026-10-18"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
INDEX_DIR = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
ANCHOR = "s4-person-relation-endpoints-bracci-burnacini-simone-bussi-cadani-calandrucci-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"

TARGETS = [
    {
        "candidate": "cand-0425", "group": "new-person:bracci-pietro-f76036a853",
        "ku": "units/persons/pietro-bracci", "card": "04-knowledge/units/persons/pietro-bracci.md",
        "name_zh": "皮埃特罗·布拉奇", "name_en": "Pietro Bracci", "name_field": "原文全名",
        "index_entry": "B.csv#272", "index_file": "B.csv", "index_name": "Bracci, Pietro",
        "index_page": "93n", "index_subentry": "Annunciation",
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
            "source_span": "line 185; print p. 93", "location": "第3章 p.93；OCR L185",
            "quote": "The chapel in the right transept was only completed in 1749 when Filippo della Valle and Pietro Bracci made a marble bas-relief of the Annunciation—see Fabrini.",
            "fragments": ["Pietro Bracci made a marble bas-relief of the Annunciation"],
            "summary": "Haskell称右侧耳堂礼拜堂于1749年完工，Filippo della Valle与Pietro Bracci制作了一件《天使报喜》大理石浅浮雕。",
        }],
        "description_zh": "本卡登记Haskell所称制作《天使报喜》大理石浅浮雕的Pietro Bracci。第3章称他与Filippo della Valle共同制作该浮雕，所在礼拜堂于1749年完工；索引子目为“Annunciation”。本卡不推定作品现状、地点或独立作品身份。中文名为本项目工作音译。",
        "description_en": "This card records Pietro Bracci, whom Haskell names with Filippo della Valle as a maker of a marble bas-relief of the Annunciation. Chapter 3 says the right-transept chapel was completed in 1749; the index sub-entry is “Annunciation.” This card does not infer the work's present state, location, or a separately verified work identity. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp3-seciv-l179-187-bracci-made-annunciation-relief"],
        "relation_context_zh": "作品候选cand-5455仍须按S3/S4状态处理；制作关系候选留待S6，未据此建立作品KU或正式边。",
        "relation_context_en": "Work candidate cand-5455 remains subject to its S3/S4 status; the maker relation remains for S6, and no work KU or formal edge is created here.",
        "statements": [("st-chp3-seciv-l179-187-bracci-made-annunciation-relief", "cand-0425", "cand-5455", "made_marble_bas_relief_of_annunciation", "Pietro Bracci made a marble bas-relief of the Annunciation")],
    },
    {
        "candidate": "cand-0472", "group": "new-person:burnacini-lodovico-ottavio-ef7e064231",
        "ku": "units/persons/lodovico-ottavio-burnacini", "card": "04-knowledge/units/persons/lodovico-ottavio-burnacini.md",
        "name_zh": "洛多维科·奥塔维奥·布尔纳奇尼", "name_en": "Lodovico Ottavio Burnacini", "name_field": "原文全名",
        "index_entry": "B.csv#320", "index_file": "B.csv", "index_name": "Burnacini, Lodovico Ottavio",
        "index_page": "193", "index_subentry": "",
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "source_span": "line 10; print p. 193", "location": "第7章 p.193；OCR L10",
            "quote": "His father had summoned the architect Lodovico Ottavio Burnacini",
            "fragments": ["His father had summoned the architect Lodovico Ottavio Burnacini"],
            "summary": "Haskell称Leopold的父亲曾召来建筑师Lodovico Ottavio Burnacini；本段没有指明父亲姓名。",
        }],
        "description_zh": "本卡登记Haskell第7章点名的建筑师Lodovico Ottavio Burnacini。第193页称Leopold的父亲曾召其前来；原文没有在此处说出父亲姓名，本卡不凭后文或外部信息补定。中文名为本项目工作音译。",
        "description_en": "This card records the architect Lodovico Ottavio Burnacini named in Chapter 7. On page 193, Haskell says Leopold's father had summoned him; the passage does not name the father, and this card does not identify him by inference or external information. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p193-leopold-father-summoned-burnacini"],
        "relation_context_zh": "被指称的召请者在该段未具名；召请关系仍为S2候选，留待S6核对端点与原文范围。",
        "relation_context_en": "The person said to have summoned Burnacini is unnamed in this passage; the summons remains an S2 candidate for S6 endpoint and source-scope review.",
        "statements": [("st-chp7-p193-leopold-father-summoned-burnacini", "cand-7163", "cand-0472", "summoned_as_architect", "Lodovico Ottavio Burnacini")],
    },
    {
        "candidate": "cand-0469", "group": "new-person:buonaccorsi-simone-0295b5645e",
        "ku": "units/persons/simone-buonaccorsi", "card": "04-knowledge/units/persons/simone-buonaccorsi.md",
        "name_zh": "西蒙·布奥纳科尔西枢机", "name_en": "Cardinal Simone Buonaccorsi", "name_field": "索引名",
        "index_entry": "B.csv#317", "index_file": "B.csv", "index_name": "Buonaccorsi, Cardinal Simone",
        "index_page": "223", "index_subentry": "",
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
            "source_span": "line 147; print p. 223", "location": "第8章 p.223；OCR L147",
            "quote": "one of whom, Simone, was to become a Cardinal",
            "fragments": ["one of whom, Simone, was to become a Cardinal"],
            "summary": "Haskell称Francesca Bussi到1726年已有十八名子女，其中Simone后来将成为枢机；同页索引将Cardinal Simone列为Buonaccorsi。",
        }],
        "description_zh": "本卡登记索引所列Cardinal Simone Buonaccorsi。第8章 p.223称Francesca Bussi的十八名子女中有一位Simone将成为枢机；B.csv#317也指向p.223并列出“Buonaccorsi, Cardinal Simone”。S3据同页姓名与身份锚点将这处Simone映射到该索引人物；这是书内对齐，不构成外部身份验证。母子关系候选仍待S6。中文名为本项目工作音译。",
        "description_en": "This card records the person indexed as Cardinal Simone Buonaccorsi. Chapter 8, p. 223, says that one of Francesca Bussi's eighteen children was Simone, who was to become a cardinal; index entry B.csv#317 also points to p. 223 and names “Buonaccorsi, Cardinal Simone.” S3 maps the mention to that indexed person on the shared-page and matching-identity anchors. This is an internal book alignment, not external identity verification. The mother-child relation candidate remains for S6. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp8-p223-francesca-mother-of-simone"],
        "relation_context_zh": "同页索引支持将子女名单中的Simone映射到Cardinal Simone Buonaccorsi；母子谓词仍是S2候选，留待S6。",
        "relation_context_en": "The same-page index supports mapping Simone in the list of children to Cardinal Simone Buonaccorsi; the mother-child predicate remains an S2 candidate for S6.",
        "statements": [("st-chp8-p223-francesca-mother-of-simone", "cand-0474", "cand-0469", "mother_of", "one of whom, Simone")],
        "s3_note": " S3补充复核（2026-10-18）：第8章p.223称Francesca Bussi的十八名子女之一Simone将成为枢机；索引B.csv#317同页列出“Buonaccorsi, Cardinal Simone”。共同印刷页、同名Simone与枢机身份支持mention到cand-0469的书内映射；关系谓词仍留待S6，不声称外部身份核验。",
    },
    {
        "candidate": "cand-0474", "group": "new-person:bussi-francesca-bfc6aa40fd",
        "ku": "units/persons/francesca-bussi", "card": "04-knowledge/units/persons/francesca-bussi.md",
        "name_zh": "弗朗切斯卡·布西", "name_en": "Francesca Bussi", "name_field": "原文全名",
        "index_entry": "B.csv#322", "index_file": "B.csv", "index_name": "Bussi, Francesca",
        "index_page": "223", "index_subentry": "",
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
            "source_span": "line 147; print p. 223", "location": "第8章 p.223；OCR L147",
            "quote": "In 1699 he married Francesca Bussi, who by 1726 had brought eighteen children into the world, one of whom, Simone, was to become a Cardinal.",
            "fragments": ["he married Francesca Bussi", "by 1726 had brought eighteen children"],
            "summary": "Haskell称一位在本段未具名的Macerata贵族于1699年与Francesca Bussi结婚，并称她到1726年已有十八名子女。",
        }],
        "description_zh": "本卡登记Haskell第8章点名的Francesca Bussi。第223页称一位在该段未具名的Macerata贵族于1699年与她结婚，并称她到1726年有十八名子女，其中Simone将成为枢机；索引B.csv#322列出她的姓名并指向同页。该婚姻与母子关系仍是S2候选，留待S6。中文名为本项目工作音译。",
        "description_en": "This card records Francesca Bussi, named in Chapter 8. Page 223 says that a Macerata nobleman, unnamed in this passage, married her in 1699 and that by 1726 she had eighteen children, one of whom, Simone, was to become a cardinal; index entry B.csv#322 lists her name at the same page. The marriage and mother-child statements remain S2 candidates for S6. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp8-p223-raimondo-married-francesca", "st-chp8-p223-francesca-mother-of-simone"],
        "relation_context_zh": "婚姻对象在对应S2候选中为cand-0467；Simone现按同页索引对齐至cand-0469。两项关系均留待S6，不添加其他家族分支主张。",
        "relation_context_en": "The spouse endpoint in its S2 candidate is cand-0467; Simone is now aligned to cand-0469 from the same-page index. Both relations remain for S6, with no additional family-branch claims.",
        "statements": [
            ("st-chp8-p223-raimondo-married-francesca", "cand-0467", "cand-0474", "married", "married Francesca Bussi"),
            ("st-chp8-p223-francesca-mother-of-simone", "cand-0474", "cand-0469", "mother_of", "one of whom, Simone"),
        ],
    },
    {
        "candidate": "cand-0476", "group": "new-person:cadani-stefano-ec786fc4ba",
        "ku": "units/persons/stefano-cadani", "card": "04-knowledge/units/persons/stefano-cadani.md",
        "name_zh": "斯特法诺·卡达尼", "name_en": "Stefano Cadani", "name_field": "原文全名",
        "index_entry": "C.csv#0", "index_file": "C.csv", "index_name": "Cadani, Stefano",
        "index_page": "194", "index_subentry": "",
        "book_sources": [{
            "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
            "source_span": "line 24; print p. 194", "location": "第7章 p.194；OCR L24",
            "quote": "By 1669 Johann Georg III of Saxony was employing an Italian painter called Stefano Cadani at Dresden",
            "fragments": ["Italian painter called Stefano Cadani at Dresden"],
            "summary": "Haskell称Johann Georg III of Saxony至迟于1669年已在Dresden雇用意大利画家Stefano Cadani；该句末注1仍待查。",
        }],
        "description_zh": "本卡登记Haskell第7章所称意大利画家Stefano Cadani。第194页称Johann Georg III of Saxony至迟于1669年已在Dresden雇用他；该句后注1尚未独立查阅。本卡不据此扩写履历。中文名为本项目工作音译。",
        "description_en": "This card records Stefano Cadani, whom Chapter 7 describes as an Italian painter. Page 194 says that Johann Georg III of Saxony was employing him at Dresden by 1669; note 1 following the sentence was not independently consulted. This card does not expand the biography beyond that account. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p194-cadani-employed-dresden"],
        "relation_context_zh": "雇用陈述留待S6；该句后注1未查，未据此增加雇用起始日或其他任职信息。",
        "relation_context_en": "The employment statement remains for S6; note 1 was not consulted, and no start date or further career information is inferred.",
        "statements": [("st-chp7-p194-cadani-employed-dresden", "cand-1324", "cand-0476", "employed_italian_painter_at_dresden", "Stefano Cadani at Dresden")],
    },
    {
        "candidate": "cand-0481", "group": "new-person:calandrucci-giacinto-de37a3f605",
        "ku": "units/persons/giacinto-calandrucci", "card": "04-knowledge/units/persons/giacinto-calandrucci.md",
        "name_zh": "贾钦托·卡兰德鲁奇", "name_en": "Giacinto Calandrucci", "name_field": "原文全名",
        "index_entry": "C.csv#5", "index_file": "C.csv", "index_name": "Calandrucci, Giacinto",
        "index_page": "192, 197", "index_subentry": "",
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "source_span": "line 286; print p. 192", "location": "第7章 p.192；OCR L286",
                "quote": "Giacinto Calandrucci and Niccolo Berrettoni, to take employment under the King in Madrid",
                "fragments": ["Giacinto Calandrucci", "to take employment under the King in"],
                "summary": "Haskell称Del Carpio在罗马曾试图说服Giacinto Calandrucci与Niccolo Berrettoni到Madrid为国王效力。",
            },
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
                "source_span": "lines 74–75; print p. 197", "location": "第7章 p.197；OCR L74–L75",
                "quote": "in Rome, Maratta, Brandi, Gaulli and Calandrucci. No Englishman had ever commissioned contemporary Italian painting on such a scale before",
                "fragments": ["in Rome, Maratta, Brandi, Gaulli and", "Calandrucci."],
                "summary": "Haskell在叙述Exeter于所到城市委托绘画后，列出他在罗马相关的画家，其中有Calandrucci；该清单未指认单件作品或交易。",
            },
        ],
        "description_zh": "本卡登记索引所列Giacinto Calandrucci。第7章 p.192以全名提及他与Niccolo Berrettoni，称Del Carpio曾试图说服二人赴Madrid为国王效力；p.197在Exeter各城市绘画委托的叙述中以姓氏列出Calandrucci。索引将p.192与p.197列在同一主项下。中文名为本项目工作音译。",
        "description_en": "This card records Giacinto Calandrucci, as named in the index. Chapter 7, p. 192, names him with Niccolo Berrettoni and says Del Carpio had tried to persuade them to work for the King in Madrid; p. 197 lists Calandrucci by surname in Haskell's account of Exeter's painting commissions across the cities he visited. The index places pp. 192 and 197 under one entry. The Chinese name is a working transliteration.",
        "relation_ids": ["st-chp7-p197-exeter-collected-calandrucci-rome"],
        "relation_context_zh": "p.197清单为概括性城市—画家列举，没有指认单件作品或具体交易；关联候选留待S6。",
        "relation_context_en": "The p. 197 list is a general city-and-painter enumeration, identifying no individual work or specific transaction; the association candidate remains for S6.",
        "statements": [("st-chp7-p197-exeter-collected-calandrucci-rome", "cand-0984", "cand-0481", "collector_artist_association_in_city", "Genoa, Piola")],
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
    at = next(
        (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_path),
        claims_idx,
    )
    lines.insert(at, entry)
    return lines


def read_index_rows(file_name: str) -> list[dict[str, str]]:
    raw = (INDEX_DIR / file_name).read_bytes()
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        content = raw.decode("cp1252")
    return list(csv.DictReader(io.StringIO(content)))


def make_card(t: dict) -> str:
    sources = [{
        "citation": INDEX_CITATION,
        "location": f"全书索引 {t['index_entry']}；所列页码{t['index_page']}",
        "sentence_summary": f"索引主项为“{t['index_name']}”，页码指向{t['index_page']}。",
        "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}", "source_span": t["index_entry"]},
    }]
    for item in t["book_sources"]:
        sources.append({
            "citation": BOOK,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["source_span"], "text": item["quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": item["source_file"], "source_span": item["source_span"]},
        })
    metadata = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": sources, "created": DATE, "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=1000)
    evidence = "；".join(f"S1（{item['location']}）" for item in t["book_sources"][:1])
    if t["name_field"] == "索引名":
        evidence = f"S1（索引 {t['index_entry']}）"
    body_links = " ".join(
        f"[{item['location']}](../../../{item['source_file']})" for item in t["book_sources"]
    )
    index_link = f"[索引 {t['index_entry']}](../../../02-sources/03-Index/03-2-Index-CSV/{t['index_file']})"
    relation_list = "、".join(f"`{sid}`" for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']} {body_links} {index_link}

**English:** {t['description_en']} {body_links} {index_link}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| {t['name_field']} | {t['name_en'] if t['name_field'] == '原文全名' else t['index_name']} | {evidence} |

### 本书相关内容

**中文：** {t['relation_context_zh']} {body_links}

**English:** {t['relation_context_en']} {body_links}

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

S2直接关系候选 {relation_list} 留待S6逐条审查；本次S4不创建正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register six source-backed new person groups in S4, including a page-level S3 identity reassessment.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    assert len(candidate_by_id) == len(alignment_by_id)
    manifest_by_ku = {r["ku_id"]: r for r in manifest}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    raw_statement_lines = STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
    statements = [json.loads(line) for line in raw_statement_lines if line.strip()]
    statement_by_id = {r["statement_id"]: r for r in statements}

    for t in TARGETS:
        cid = t["candidate"]
        c, a = candidate_by_id[cid], alignment_by_id[cid]
        assert c.get("suggested_type") == "person"
        assert a.get("decision") == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == t["group"]
        assert c.get("canonical_name") == t["index_name"]
        assert c.get("index_entry_id") == t["index_entry"]
        group_members = [
            r["candidate_id"] for r in alignments
            if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new"
            and sync.get_group(r.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)
        index_rows = read_index_rows(t["index_file"])
        index_row = index_rows[int(t["index_entry"].split("#")[1])]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        if t["index_subentry"]:
            assert index_row.get("Sub-entry") == t["index_subentry"]
        for item in t["book_sources"]:
            text = (ROOT / item["source_file"]).read_text(encoding="utf-8-sig")
            assert all(fragment in text for fragment in item["fragments"]), (cid, item["source_file"])
        direct_ids = {
            r["statement_id"] for r in statements
            if (r.get("qualifiers") or {}).get("relation_candidate") is True
            and cid in (r.get("subject_candidate_id"), r.get("object_candidate_id"))
        }
        expected_ids = {item[0] for item in t["statements"]}
        assert direct_ids == expected_ids, (cid, direct_ids, expected_ids)
        for sid, subject, obj, predicate, fragment in t["statements"]:
            s = statement_by_id[sid]
            assert s.get("subject_candidate_id") == subject and s.get("object_candidate_id") == obj
            assert s.get("predicate") == predicate
            assert fragment in s.get("original_quote", ""), (sid, fragment, s.get("original_quote", ""))
        assert t["ku"] not in manifest_by_ku
        assert t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(r.get("type") == "person" and (r.get("name_en") or "").casefold() == t["name_en"].casefold() for r in manifest)

    planned_alignments = [dict(r) for r in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        a = next(r for r in planned_alignments if r.get("candidate_id") == t["candidate"] and not r.get("external_source"))
        a["ku_id"] = t["ku"]
        a["process_ref"] = PROCESS_REF
        a["resolution_note"] += f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；依据书内索引与正文锚点，仅登记本书支持的人物身份，关系候选留待S6。"
        if t.get("s3_note"):
            a["resolution_note"] += t["s3_note"]
        planned_manifest.append({
            "ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"],
            "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"],
        })
    planned_manifest.sort(key=lambda r: r["ku_id"])

    planned_accepted = accepted_lines
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, t["card"])
    assert len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}) == len(accepted_paths) + len(TARGETS)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(r[key] for r in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 751 and totals["registered_members"] == 922
    assert totals["pending_groups"] == 4025 and totals["pending_members"] == 4039
    assert stats["person"]["registered_groups"] == 345 and stats["person"]["registered_members"] == 431
    assert stats["person"]["pending_groups"] == 723 and stats["person"]["pending_members"] == 724
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    planned_cards = {t["card"]: make_card(t) for t in TARGETS}
    for text in planned_cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    detail_lines = []
    for t in TARGETS:
        rels = "、".join(f"`{sid}`" for sid in t["relation_ids"])
        detail_lines.append(
            f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；"
            f"直接S2关系候选 {rels} 留待S6；{t['relation_context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3/S4 person：六组直接关系端点身份组登记（{DATE}）\n\n"
        + "\n".join(detail_lines)
        + "\n\n#### S3补充复核：Cardinal Simone Buonaccorsi同页身份映射\n\n"
        "第8章p.223称Francesca Bussi的十八名子女之一Simone将成为枢机；索引B.csv#317同页列出“Buonaccorsi, Cardinal Simone”。"
        "cand-0469既有new组保持不变；本次补记该书内mention-to-index身份对应，S2的母子关系候选仍待S6。未访问外部身份记录。\n\n"
        "六个S3单候选new人物组各登记为一张KU；六条原文全名/索引名字段均从卡片表提取并另行登记。"
        "未新增formal relations；其他冲突、未决和待登记组保持原状态。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条待登记；"
        f"全书为{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条已登记、"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条待登记，KU={len(planned_manifest)}。"
    )

    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, n = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>", result_text, count=1,
    )
    assert n == 1
    result_text += (
        f"\n\n### S3/S4 人物身份组登记：六个直接关系端点（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。六组均为单候选new组。cand-0469的p.223提及与索引B.csv#317同页，S3据此将Simone映射到Cardinal Simone Buonaccorsi；母子关系仍待S6。"
        "其余关系候选留待S6；未新增正式边。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: six singleton person groups; candidate/index/source/S2 checks passed; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; person={stats['person']['registered_groups']}/"
            f"{stats['person']['registered_members']} registered; Simone S3 note preserved in alignment"
        )
        print("formal_relations_added=0; enrichment_rows_changed=0; no files changed")
        return 0

    for rel, text in planned_cards.items():
        (ROOT / rel).write_text(text, encoding="utf-8", newline="\n")
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
