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
DATE = "2026-10-17"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_CITATION = "Francis Haskell, *Patrons and Painters*, index."
INDEX_DIR = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV"
ANCHOR = "s4-person-direct-endpoints-ceruti-cesi-champaigne-charles-chiarini-chigi-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BT = chr(96)

TARGETS = [
    {
        "candidate": "cand-0637",
        "group": "new-person:ceruti-giacomo-435ed1cd37",
        "ku": "units/persons/giacomo-ceruti",
        "card": "04-knowledge/units/persons/giacomo-ceruti.md",
        "name_zh": "贾科莫·切鲁蒂",
        "name_en": "Giacomo Ceruti",
        "name_field": "原文全名",
        "index_entry": "C.csv#161",
        "index_file": "C.csv",
        "index_name": "Ceruti, Giacomo",
        "index_page": "312, 314",
        "source_fragments": ["Giacomo Ceruti", "he was painted by"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "lines 18-20; print p. 312",
                "location": "第10章 p.312；OCR L18-20",
                "summary": (
                    "Haskell将Giacomo Ceruti列入为Schulenburg绘制肖像的画家；没有指认具体肖像。"
                ),
                "quote": "he was painted by Bartolommeo Nazari, Giuseppe Nogari, Giacomo Ceruti",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第10章点名的Giacomo Ceruti。第312页将他列入为Schulenburg绘制肖像的画家，"
            "但未指认任何单件肖像。索引以“Ceruti, Giacomo”列出该人物，并指向第312、314页。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Giacomo Ceruti named in Chapter 10. Page 312 lists him among the artists who painted portraits of Schulenburg, but identifies "
            "no individual portrait. The index lists “Ceruti, Giacomo” at pages 312 and 314. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp10-p312-ceruti-painted-portraits-of"],
        "relation_context_zh": (
            "Haskell只列出肖像画家，没有给出具体作品题名；该S2候选留待S6。"
        ),
        "relation_context_en": (
            "Haskell lists the portrait painter but gives no individual picture title; the S2 candidate remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp10-p312-ceruti-painted-portraits-of",
                "cand-0637",
                "cand-2401",
                "painted_portraits_of",
                "Giacomo Ceruti",
            ),
        ],
    },
    {
        "candidate": "cand-0641",
        "group": "new-person:cesi-federico-5a8ec02660",
        "ku": "units/persons/prince-federico-cesi",
        "card": "04-knowledge/units/persons/prince-federico-cesi.md",
        "name_zh": "费德里科·切西亲王",
        "name_en": "Prince Federico Cesi",
        "name_field": "索引名",
        "index_entry": "C.csv#165",
        "index_file": "C.csv",
        "index_name": "Cesi, Prince Federico",
        "index_page": "99",
        "source_fragments": ["Prince Federico Cesi, its founder", "died in 1630"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "source_span": "line 233; print p. 99",
                "location": "第4章 p.99；OCR L233",
                "summary": (
                    "Haskell称Prince Federico Cesi是Accademia dei Lincei的创办者，并称他于1630年去世；此处作为书内身份陈述。"
                ),
                "quote": "When Prince Federico Cesi, its founder, died in 1630",
            },
        ],
        "description_zh": (
            "本卡登记索引名为Prince Federico Cesi的人物。Haskell第4章第99页称他是Accademia dei Lincei的创办者，并记其于1630年去世；"
            "本卡记录的是书内身份与年代陈述，不构成独立传记核验。索引以“Cesi, Prince Federico”列出该人物。中文名为本项目工作译写。"
        ),
        "description_en": (
            "This card records the person indexed as Prince Federico Cesi. Chapter 4, page 99, identifies him as founder of the Accademia dei Lincei and dates "
            "his death to 1630. This records the book's identity and date statements, not independent biographical verification. The index lists “Cesi, Prince "
            "Federico.” The Chinese name is a working rendering."
        ),
        "relation_ids": [
            "st-chp4-sec-ii-l232-308-cesi-died-1630",
            "st-chp4-sec-ii-l232-308-cesi-identified-as-founder",
        ],
        "relation_context_zh": (
            "创办者身份与1630年卒年均按Haskell书内陈述记录，未作外部传记核验；两项S2候选留待S6。"
        ),
        "relation_context_en": (
            "The founder identification and 1630 death date are recorded as Haskell's statements, without external biographical verification; both S2 candidates remain for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp4-sec-ii-l232-308-cesi-died-1630",
                "cand-0641",
                "cand-5641",
                "died",
                "died in 1630",
            ),
            (
                "st-chp4-sec-ii-l232-308-cesi-identified-as-founder",
                "cand-0641",
                "cand-0003",
                "identified_as_founder",
                "Prince Federico Cesi, its founder",
            ),
        ],
    },
    {
        "candidate": "cand-0643",
        "group": "new-person:champaigne-de-philippe-bec5499e28",
        "ku": "units/persons/philippe-de-champaigne",
        "card": "04-knowledge/units/persons/philippe-de-champaigne.md",
        "name_zh": "菲利普·德·尚佩涅",
        "name_en": "Philippe de Champaigne",
        "name_field": "原文全名",
        "index_entry": "C.csv#167",
        "index_file": "C.csv",
        "index_name": "Champaigne, Philippe de",
        "index_page": "175",
        "source_fragments": ["Philippe de Champaigne", "Phikppe de Champaigne"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md",
                "source_span": "lines 63, 85-86; print pp. 175-176",
                "location": "第7章 pp.175-176；OCR L63、85-86",
                "summary": (
                    "Haskell称Orazio Gentileschi的画作对Philippe de Champaigne的风格影响曾被研究者追溯；同节稍后有一次OCR异拼，"
                    "与索引全名并列保留。"
                ),
                "quote": "the influence of which has been traced on the styles of artists as different as Louis Le Nain, Laurent de la Hyre and Philippe de Champaigne",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第7章点名的Philippe de Champaigne。第175页称，Orazio Gentileschi的画作对他的风格影响曾被研究者追溯；"
            "这是转述的艺术史判断，不指认具体作品，也不建立师生关系。同一段落稍后OCR出现“Phikppe”异拼，本卡以索引名及正文完整拼法"
            "记录身份，原提及保留在S2账本中。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Philippe de Champaigne named in Chapter 7. Page 175 says that the influence of Orazio Gentileschi's pictures has been traced "
            "in Champaigne's style; this is a reported art-historical assessment, not a claim about a specific picture or a teacher-pupil relation. A later "
            "OCR mention in the same section reads “Phikppe”; the index and full spelling in the text anchor this identity, while the original mention remains "
            "in the S2 ledger. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp7-p175-i04"],
        "relation_context_zh": (
            "影响说是对研究者判断的转述，不等同师承或单件作品影响；保留S2限定，候选留待S6。"
        ),
        "relation_context_en": (
            "The influence statement reports an art-historical assessment; it does not establish apprenticeship or influence on a specific work. Preserve the S2 qualification and leave the candidate for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp7-p175-i04",
                "cand-1138",
                "cand-0643",
                "influenced_style_of",
                "Philippe de Champaigne",
            ),
        ],
    },
    {
        "candidate": "cand-0659",
        "group": "new-person:charles-of-sweden-xii-22ffb5a1d4",
        "ku": "units/persons/charles-xii-of-sweden",
        "card": "04-knowledge/units/persons/charles-xii-of-sweden.md",
        "name_zh": "瑞典国王卡尔十二世",
        "name_en": "Charles XII of Sweden",
        "name_field": "原文全名",
        "index_entry": "C.csv#183",
        "index_file": "C.csv",
        "index_name": "Charles XII of Sweden",
        "index_page": "311",
        "source_fragments": ["Charles XII of Sweden", "fought for the Saxons"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "line 10; print p. 311",
                "location": "第10章 p.311；OCR L10",
                "summary": (
                    "Haskell称Schulenburg曾为萨克森一方与Charles XII of Sweden作战，并说他晚年喜欢谈及这些战斗；对方兵力未具体说明。"
                ),
                "quote": "he fought for the Saxons in a scries of engagements against Charles XII of Sweden",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第10章点名的Charles XII of Sweden。第311页称Schulenburg曾为萨克森一方参加与Charles XII的多次交战，"
            "并说他晚年喜欢谈起这些战斗；原文没有细分交战中的具体兵力。索引以“Charles XII of Sweden”列出该人物。中文名为本项目工作译写。"
        ),
        "description_en": (
            "This card records Charles XII of Sweden named in Chapter 10. Page 311 says that Schulenburg fought for the Saxons in several engagements against "
            "Charles XII and later liked to talk about them; the source does not specify the forces in each engagement. The index lists “Charles XII of Sweden.” "
            "The Chinese name is a working rendering."
        ),
        "relation_ids": ["st-chp10-p311-schulenburg-fought-for-saxons-against-charles-xii"],
        "relation_context_zh": (
            "S2记录Schulenburg为萨克森一方与Charles XII交战的书内叙述；“晚年谈起”亦保留为Haskell转述，候选留待S6。"
        ),
        "relation_context_en": (
            "S2 records Haskell's account of Schulenburg fighting for the Saxons against Charles XII; the later recollections also remain attributed to Haskell. The candidate remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp10-p311-schulenburg-fought-for-saxons-against-charles-xii",
                "cand-2401",
                "cand-0659",
                "fought_for_saxons_against_charles_xii",
                "engagements against Charles XII of Sweden",
            ),
        ],
    },
    {
        "candidate": "cand-0662",
        "group": "new-person:chiarini-marcantonio-92d65d97a6",
        "ku": "units/persons/marcantonio-chiarini",
        "card": "04-knowledge/units/persons/marcantonio-chiarini.md",
        "name_zh": "马尔坎托尼奥·基亚里尼",
        "name_en": "Marc’antonio Chiarini",
        "name_field": "原文全名",
        "index_entry": "C.csv#186",
        "index_file": "C.csv",
        "index_name": "Chiarini, Marcantonio",
        "index_page": "200, 201",
        "source_fragments": ["Marc’antonio Chiarini", "frescoed by the Bolognese"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
                "source_span": "line 14; print p. 200",
                "location": "第7章 p.200；OCR L14",
                "summary": (
                    "Haskell称Daun位于Vienna的宫殿由博洛尼亚人Marc’antonio Chiarini绘制壁画；没有说明日期、房间或题材。"
                ),
                "quote": "which was frescoed by the Bolognese Marc’antonio Chiarini",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第7章点名的Marc’antonio Chiarini。第200页称Daun位于Vienna的宫殿由Chiarini绘制壁画；原文没有给出"
            "日期、房间或壁画题材。索引以“Chiarini, Marcantonio”列出该人物并指向第200、201页。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Marc’antonio Chiarini named in Chapter 7. Page 200 says that Daun's palace in Vienna was frescoed by Chiarini; no date, room, "
            "or subject is supplied. The index lists “Chiarini, Marcantonio” at pages 200 and 201. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp7-p200-v-chiarini-frescoes-daun-palace"],
        "relation_context_zh": (
            "宫殿壁画归属保留Haskell原文范围，不补入年代、房间或题材；正式关系留待S6。"
        ),
        "relation_context_en": (
            "The palace-fresco attribution retains Haskell's scope, without adding a date, room, or subject; the formal relation remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp7-p200-v-chiarini-frescoes-daun-palace",
                "cand-0662",
                "cand-7299",
                "frescoed_palace",
                "frescoed by the Bolognese Marc’antonio Chiarini",
            ),
        ],
    },
    {
        "candidate": "cand-0663",
        "group": "new-person:agostino-chigi-il-magnifico-8646b69f00",
        "ku": "units/persons/agostino-chigi-il-magnifico",
        "card": "04-knowledge/units/persons/agostino-chigi-il-magnifico.md",
        "name_zh": "阿戈斯蒂诺·基吉（il Magnifico）",
        "name_en": "Agostino Chigi ‘il Magnifico’",
        "name_field": "原文全名",
        "index_entry": "C.csv#187",
        "index_file": "C.csv",
        "index_name": "Chigi, Agostino 'il Magnifico'",
        "index_page": "150",
        "source_fragments": [
            "Agostino ‘il Magnifico’",
            "whose friendship with Raphael was legendary",
        ],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_i.md",
                "source_span": "line 57; print p. 150",
                "location": "第6章 p.150；OCR L57",
                "summary": (
                    "Haskell称Fabio Chigi是Agostino ‘il Magnifico’的后裔，并称Agostino与Raphael的友谊具有传奇色彩；"
                    "亲缘与评价均为书内陈述。"
                ),
                "quote": "Agostino ‘il Magnifico’ whose friendship with Raphael was legendary",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第6章称作Agostino ‘il Magnifico’的人物。第150页称Fabio Chigi是他的直系后裔，并形容他与Raphael的友谊"
            "“具有传奇色彩”。亲缘及评价均保留为书内陈述，未作外部核验。索引以“Chigi, Agostino ‘il Magnifico’”列出该人物。"
            "中文名为本项目工作译写。"
        ),
        "description_en": (
            "This card records the person Haskell calls Agostino ‘il Magnifico’ in Chapter 6. Page 150 says Fabio Chigi was his direct descendant and "
            "describes his friendship with Raphael as legendary. Both the genealogy and characterization remain statements in the book and were not externally "
            "verified. The index lists “Chigi, Agostino 'il Magnifico'.” The Chinese name is a working rendering."
        ),
        "relation_ids": [
            "st-chp6-p150-agostino-raphael-friendship",
            "st-chp6-p150-fabio-descended-from-agostino",
        ],
        "relation_context_zh": (
            "Raphael友谊的“传奇”表述和Fabio Chigi直系后裔关系均为Haskell书内叙述，未外部核验；两项S2候选留待S6。"
        ),
        "relation_context_en": (
            "Both the “legendary” characterization of the Raphael friendship and the direct-descent statement about Fabio Chigi are Haskell's account and were "
            "not externally verified; both S2 candidates remain for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp6-p150-agostino-raphael-friendship",
                "cand-0663",
                "cand-2098",
                "agostino_chigi_was_a_friend_of_raphael",
                "friendship with Raphael was legendary",
            ),
            (
                "st-chp6-p150-fabio-descended-from-agostino",
                "cand-0665",
                "cand-0663",
                "fabio_chigi_was_a_direct_descendant_of_agostino_chigi",
                "Agostino ‘il Magnifico’",
            ),
        ],
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
            "location": f"全书索引 {t['index_entry']}；所列页码{t['index_page']}",
            "sentence_summary": f"索引主项为“{t['index_name']}”，页码指向{t['index_page']}。",
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}",
                "source_span": t["index_entry"],
            },
        },
    ]
    for source in t["book_sources"]:
        sources.append(
            {
                "citation": BOOK,
                "location": source["location"],
                "sentence_summary": source["summary"],
                "original_quotes": [{"source_span": source["source_span"], "text": source["quote"]}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": source["source_file"],
                    "source_span": source["source_span"],
                },
            }
        )
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
    links = [
        f"[{source['location']}](../../../{source['source_file']})"
        for source in t["book_sources"]
    ]
    links.append(
        f"[索引 {t['index_entry']}](../../../02-sources/03-Index/03-2-Index-CSV/{t['index_file']})"
    )
    evidence_links = " ".join(links)
    relation_list = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']} {evidence_links}

**English:** {t['description_en']} {evidence_links}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| {t['name_field']} | {t['index_name']} | S1（索引 {t['index_entry']}） |

### 本书相关内容

**中文：** {t['relation_context_zh']} {evidence_links}

**English:** {t['relation_context_en']} {evidence_links}

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

当前没有登记在 relations.csv 中的正式关系。直接S2候选 {relation_list} 留待S6审查；本次S4登记不裁决或创建正式关系。
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
        index_row_number = int(t["index_entry"].split("#")[1])
        index_row = read_index_rows(t["index_file"])[index_row_number]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        combined_source_text = "\n".join(
            (ROOT / source_file).read_text(encoding="utf-8-sig")
            for source_file in {s["source_file"] for s in t["book_sources"]}
        )
        assert all(fragment in combined_source_text for fragment in t["source_fragments"]), cid
        normalized_source = re.sub(r"\s+", " ", combined_source_text)
        for source in t["book_sources"]:
            assert re.sub(r"\s+", " ", source["quote"]) in normalized_source, (
                cid, source["source_span"], source["quote"]
            )
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
        a["resolution_note"] += (
            f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；书内姓名和索引支持source-local人物登记，"
            "原文限定保留，直接关系候选仍待S6。"
        )
        planned_manifest.append(
            {
                "ku_id": t["ku"],
                "type": "person",
                "canonical_name": t["name_zh"],
                "name_en": t["name_en"],
                "source_task": TASK,
                "card_path": t["card"],
            }
        )
    planned_manifest.sort(key=lambda row: row["ku_id"])

    planned_accepted = accepted_lines
    for t in TARGETS:
        planned_accepted = insert_accepted(planned_accepted, t["card"])
    assert len(accepted_paths) + len(TARGETS) == len(
        {line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}
    )

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] == 769 and totals["registered_members"] == 940
    assert totals["pending_groups"] == 4007 and totals["pending_members"] == 4021
    assert stats["person"]["registered_groups"] == 363
    assert stats["person"]["registered_members"] == 449
    assert stats["person"]["pending_groups"] == 705
    assert stats["person"]["pending_members"] == 706
    assert len(planned_manifest) == len(manifest) + len(TARGETS)

    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    group_lines = []
    for t in TARGETS:
        statements_text = ", ".join(f"{BT}{sid}{BT}" for sid in t["relation_ids"])
        group_lines.append(
            f"- {BT}{t['candidate']}{BT}（{BT}{t['group']}{BT}）→ "
            f"[{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；"
            f"S2直接关系候选 {statements_text} 留待S6；{t['relation_context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4人物：六组直接关系端点身份组登记（{DATE}）\n\n"
        + "\n".join(group_lines)
        + "\n\n本批登记6个单候选S3 new人物组；身份依据限于书内姓名、索引定位及相应来源段。"
        "Champaigne的OCR异拼、Cesi的书内生卒/创办者陈述、Chigi的谱系与评价以及其余端点的限定均保留；"
        "本批没有添加外部身份事实或formal relations。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、"
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
        + "；".join(
            f"{BT}{t['candidate']}{BT} → {BT}../units/persons/{t['ku'].split('/')[-1]}.md{BT}"
            for t in TARGETS
        )
        + "。六组均为S3单候选new组；各卡保留对应来源限定。S2关系候选留待S6，本批不创建formal relations。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: six singleton person groups; candidate/index/source/S2 relation checks passed; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered="
            f"{totals['registered_groups']}/{totals['registered_members']}; "
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
        f"applied: groups={len(TARGETS)}; candidate_mappings={len(TARGETS)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; formal_relations_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
