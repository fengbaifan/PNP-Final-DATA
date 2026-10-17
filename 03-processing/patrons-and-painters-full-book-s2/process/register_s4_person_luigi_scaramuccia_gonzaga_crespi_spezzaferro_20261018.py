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
import register_s4_person_relation_endpoints_allegrini_bouchardon_20261018 as person_sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ANCHOR = "s4-person-relation-endpoints-scaramuccia-gonzaga-crespi-spezzaferro-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
VATICAN_URL = (
    "https://www.vatican.va/news_services/liturgy/libretti/2025/"
    "20250423-libretto-traslazione-bara.pdf"
)
VATICAN_CITATION = (
    "The Holy See, *Traslazione della bara del Romano Pontefice Francesco*, "
    f"Vatican City, 23 April 2025. {VATICAN_URL}. Accessed 2026-10-18."
)


def book_source(source_file: str, location: str, source_span: str, quote: str, summary: str) -> dict:
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": source_span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": source_span,
        },
    }


TARGETS = [
    {
        "candidate": "cand-2390",
        "group": "new-person:luigi-scaramuccia-aa9d76a4e9",
        "ku": "units/persons/luigi-scaramuccia",
        "card": "04-knowledge/units/persons/luigi-scaramuccia.md",
        "name_zh": "路易吉·斯卡拉穆恰",
        "name_en": "Luigi Scaramuccia",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "source_span": "line 44; print p. 124, n. 1",
        "quote": "Luigi Scaramuccia dedicated a print to him of Venus and Adonis",
        "summary": "Haskell称Luigi Scaramuccia将一幅《维纳斯与阿多尼斯》版画题献给Niccolò Simonelli；书后索引以Scaramuccia, Luigi列于印刷页124。",
        "relation_ids": ["st-chp5-note-p124-n1-scaramuccia-dedicated-by"],
        "statement_endpoints": [
            ("st-chp5-note-p124-n1-scaramuccia-dedicated-by", "cand-6018", "cand-2390", "dedicated_by", "Luigi Scaramuccia")
        ],
        "description_zh": (
            "本卡登记哈斯克尔第5章注1具名的Luigi Scaramuccia。该注称他将一幅《维纳斯与阿多尼斯》版画题献给Niccolò Simonelli；"
            "书后索引以“Scaramuccia, Luigi”列出同一印刷页。中文名为项目工作音译，身份范围限于书内具名人物，不据姓名补充生平。"
        ),
        "description_en": (
            "This card records the Luigi Scaramuccia named in Chapter 5, note 1. Haskell says that he dedicated a Venus and Adonis print to Niccolò Simonelli; the book index lists “Scaramuccia, Luigi” at the same printed page. The Chinese display name is a working transliteration. This record is limited to the person named in the book and adds no biography from the name alone."
        ),
        "context_zh": "哈斯克尔把Scaramuccia记为版画题献者；该书内陈述对应的S2关系候选保留待S6审查。索引作品候选cand-2391与人物cand-2390类型不同，仍各自保持其S3去向。",
        "context_en": "Haskell names Scaramuccia as the print's dedicator; the corresponding S2 relation candidate remains for S6 review. The index-derived work candidate cand-2391 and person candidate cand-2390 are different types and retain their separate S3 dispositions.",
        "name_rows": [("原文全名", "Luigi Scaramuccia", "S1")],
        "sources": [
            book_source(
                "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "第5章，印刷页124，注1；OCR L44",
                "line 44; print p. 124, n. 1",
                "Luigi Scaramuccia dedicated a print to him of Venus and Adonis",
                "Haskell点名Luigi Scaramuccia并称其题献一幅Venus and Adonis版画。",
            ),
            {
                "citation": "Francis Haskell, *Patrons and Painters*, index, S.csv.",
                "location": "书后索引，S.csv#78；指向印刷页124",
                "sentence_summary": "索引以Scaramuccia, Luigi为主条并指向印刷页124。",
                "original_quotes": [{"source_span": "S.csv#78", "text": "Scaramuccia, Luigi"}],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": "02-sources/03-Index/03-2-Index-CSV/S.csv",
                    "source_span": "S.csv#78",
                },
            },
        ],
    },
    {
        "candidate": "cand-5453",
        "group": "new-person:blessed-gonzaga-luigi-302904be8f",
        "ku": "units/persons/aloysius-gonzaga",
        "card": "04-knowledge/units/persons/aloysius-gonzaga.md",
        "name_zh": "阿洛伊修斯·贡扎加",
        "name_en": "Aloysius Gonzaga",
        "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
        "source_span": "line 185; print p. 93",
        "quote": "the Blessed Luigi Gonzaga",
        "summary": "Haskell称Legros的浮雕表现Blessed Luigi Gonzaga升天；其他章节以S. Luigi Gonzaga称指相关绘画或modello主题。",
        "relation_ids": ["st-chp3-seciv-l179-187-assumption-relief-represents-luigi-gonzaga"],
        "statement_endpoints": [
            (
                "st-chp3-seciv-l179-187-assumption-relief-represents-luigi-gonzaga",
                "cand-5452",
                "cand-5453",
                "represents_assumption_of_blessed_luigi_gonzaga",
                "Blessed Luigi Gonzaga",
            )
        ],
        "description_zh": (
            "本卡登记《赞助人与画家》以Blessed Luigi Gonzaga、S. Luigi Gonzaga指称的人物。梵蒂冈2025年礼仪文本在同一祷文行中并列英文“Saint Aloysius (Gonzaga)”与意大利文“San Luigi (Gonzaga)”，"
            "据此将书中Luigi Gonzaga与Aloysius Gonzaga归为同一身份。中文显示名为项目工作音译；本书称号原样保留，不据此改写书内措辞。"
        ),
        "description_en": (
            "This card records the person named in *Patrons and Painters* as Blessed Luigi Gonzaga and S. Luigi Gonzaga. A 2025 Holy See liturgical booklet places the English “Saint Aloysius (Gonzaga)” and Italian “San Luigi (Gonzaga)” in corresponding lines of the same litany; this supports treating the book's Luigi Gonzaga and Aloysius Gonzaga as one identity. The Chinese display name is a working transliteration, and the book's wording is preserved as written."
        ),
        "context_zh": "本书称该人物为S. Ignazio左横堂一件浮雕所表现的主题，并以the Assumption of the Blessed Luigi Gonzaga称述；这里依原句表述为Luigi Gonzaga升天主题，不据此另造作品题名。第8章及第9章另以S. Luigi Gonzaga指称绘画与modello主题。相应S2关系候选留待S6，不在S4建立作品关系。",
        "context_en": "The book names him as the subject of the Assumption bas-relief in the left transept of S. Ignazio; Chapters 8 and 9 also use S. Luigi Gonzaga for the subjects of a painting and a modello. The S2 relation candidate remains for S6; no work relation is created in S4.",
        "name_rows": [
            ("英文惯用名", "Aloysius Gonzaga", "S4"),
            ("意大利文名", "Luigi Gonzaga", "S1、S2、S3、S4"),
            ("书中称号", "Blessed", "S1"),
        ],
        "sources": [
            book_source(
                "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "第3章，印刷页93；OCR L185",
                "line 185; print p. 93",
                "the Blessed Luigi Gonzaga",
                "Haskell以Blessed Luigi Gonzaga称Legros浮雕所表现的人物。",
            ),
            book_source(
                "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "第8章；OCR L8（本段印刷页203）",
                "line 8; print p. 203",
                "a S. Luigi Gonzaga' by Guido Reni",
                "Haskell记述Malpighi对一幅Guido Reni所作S. Luigi Gonzaga绘画的评论。",
            ),
            book_source(
                "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
                "第9章，印刷页272，注3；OCR L111",
                "line 111; print p. 272, n. 3",
                "a modello for the Glory of S. Luigi Gonzaga",
                "Haskell在注释中称一件modello的主题为S. Luigi Gonzaga。",
            ),
            {
                "citation": VATICAN_CITATION,
                "location": "礼仪祷文，PDF p. 20，印刷页40–41；英意对照行",
                "sentence_summary": "梵蒂冈文本在对应英意祷文行中并列Saint Aloysius (Gonzaga)与San Luigi (Gonzaga)，支持两种称名指向同一圣人。",
                "original_quotes": [
                    {"source_span": "PDF p. 20; printed pp. 40–41", "text": "Saint Aloysius (Gonzaga)… San Luigi (Gonzaga)…"}
                ],
                "evidence_ref": {
                    "doc_id": "holy-see-2025-papal-coffin-translation-liturgical-booklet",
                    "source_file": VATICAN_URL,
                    "source_span": "PDF p. 20; printed pp. 40–41; English/Italian litany line",
                },
            },
        ],
    },
    {
        "candidate": "cand-7716",
        "group": "new-person:crespi-luigi-bd0f28eb72",
        "ku": "units/persons/luigi-crespi-author",
        "card": "04-knowledge/units/persons/luigi-crespi-author.md",
        "name_zh": "路易吉·克雷斯皮",
        "name_en": "Luigi Crespi",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "source_span": "line 449; print p. 239, n. 1",
        "quote": "L. Crespi, p. 211, says that he was in Florence for two years",
        "summary": "Haskell注1转述L. Crespi关于Giuseppe Maria Crespi在佛罗伦萨停留两年的说法，并同时指出另一时长记载；书目列出Luigi Crespi著作。",
        "relation_ids": ["st-chp8-p239-note1-luigi-crespi-stay"],
        "statement_endpoints": [
            ("st-chp8-p239-note1-luigi-crespi-stay", "cand-7716", "cand-0871", "reports_two_year_florence_stay_for", "two years")
        ],
        "description_zh": (
            "本卡登记书目中署名Luigi Crespi、并在注释中简称L. Crespi的作者。书目列有其1769年《Vite de’ Pittori bolognesi non descritte nella ‘Felsina Pittrice’》；"
            "哈斯克尔以L. Crespi p.211转述Giuseppe Maria Crespi在佛罗伦萨停留两年的说法，同时给出1709年最多八个月及Zanotti暗示多次到访的不同叙述。被引书页未独立查阅；本卡不把争议时长写作已核事实，也不与画家Giuseppe Maria Crespi合并。"
        ),
        "description_en": (
            "This card records the author named Luigi Crespi in the bibliography and cited in notes as L. Crespi. The bibliography lists his 1769 *Vite de’ Pittori bolognesi non descritte nella ‘Felsina Pittrice’*. Haskell attributes to L. Crespi, p. 211, a two-year Florence stay for Giuseppe Maria Crespi, while also giving a maximum of eight months during 1709 and noting Zanotti's implication of multiple visits. The cited pages were not independently consulted; the disputed duration is not treated as verified fact, and this author is kept distinct from painter Giuseppe Maria Crespi."
        ),
        "context_zh": "原书的L. Crespi两年说与哈斯克尔所述八个月上限并列，Zanotti的多次到访暗示也未消解差异；关系候选保留来源归因并待S6，不作实体层面的事实裁决。",
        "context_en": "The book juxtaposes L. Crespi's two-year account with Haskell's eight-month maximum; Zanotti's implication of multiple visits does not resolve the discrepancy. The relation candidate preserves source attribution and remains for S6; this registration does not adjudicate the underlying claim.",
        "name_rows": [("书目全名", "Luigi Crespi", "S1")],
        "sources": [
            book_source(
                "02-sources/02-Markdown/21_CHP-21Bibliography.md",
                "书后参考书目，印刷页420；OCR L389",
                "line 389; print p. 420",
                "Crespi, Luigi: Vite de’ Pittori bolognesi non descritte nella ‘Felsina Pittrice’, Roma 1769.",
                "书目以Crespi, Luigi著录一部1769年出版的意大利文著作。",
            ),
            book_source(
                "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "第8章，印刷页239，注1；OCR L449",
                "line 449; print p. 239, n. 1",
                "L. Crespi, p. 211, says that he was in Florence for two years",
                "注释把两年停留说法归于L. Crespi，同时说明哈斯克尔所述1709年最多八个月及Zanotti的多次到访暗示。",
            ),
            book_source(
                "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "第8章，印刷页238，注3；OCR L445",
                "line 445; print p. 238, n. 3",
                "the letter from Ferdinand published by Luigi Crespi, p. 203",
                "注释以全名Luigi Crespi指称出版Ferdinand书信文本的作者，并给出页码203。",
            ),
        ],
    },
    {
        "candidate": "cand-10881",
        "group": "new-person:luigi-spezzaferro-cd9c5c8655",
        "ku": "units/persons/luigi-spezzaferro",
        "card": "04-knowledge/units/persons/luigi-spezzaferro.md",
        "name_zh": "路易吉·斯佩察费罗",
        "name_en": "Luigi Spezzaferro",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "source_span": "line 22; print p. 397",
        "quote": "Luigi Spezzaferro",
        "summary": "Haskell称Luigi Spezzaferro研究Del Monte的文化形成并强调其对科学探究的兴趣；书后参考书目列出其1971年文章。",
        "relation_ids": ["st-chp20-p397-spezzaferro-del-monte-caravaggio"],
        "statement_endpoints": [
            (
                "st-chp20-p397-spezzaferro-del-monte-caravaggio",
                "cand-10881",
                "cand-1691",
                "spezzaferro_examined_del_montes_cultural_formation_and_scientific_interests",
                "examined his cultural formation in considerable detail",
            )
        ],
        "description_zh": (
            "本卡登记哈斯克尔后记具名的Luigi Spezzaferro。哈斯克尔概述其对枢机Del Monte文化形成的研究，并称其强调Del Monte对科学探究的兴趣；"
            "书后参考书目列出Spezzaferro 1971年文章。该文章及哈斯克尔对其观点的转述未在本次独立查阅，本卡仅保存书内所指人物及其语境。中文显示名为项目工作音译。"
        ),
        "description_en": (
            "This card records the Luigi Spezzaferro named in Haskell's postscript. Haskell summarizes his study of Cardinal Del Monte's cultural formation and says that it stresses Del Monte's interest in scientific investigation; the bibliography lists Spezzaferro's 1971 article. Neither the article nor Haskell's account of its argument was independently consulted for this registration. The Chinese display name is a working transliteration."
        ),
        "context_zh": "第20章的S2关系候选记载哈斯克尔对Spezzaferro研究的转述；原书所引文章另有archive候选cand-10882，二者保持人物与文献类型区别，关系留待S6。",
        "context_en": "The Chapter 20 S2 relation candidate records Haskell's account of Spezzaferro's study. The cited article has its own archive candidate, cand-10882; the person and publication remain distinct types, and the relation is for S6 review.",
        "name_rows": [("原文全名", "Luigi Spezzaferro", "S1、S2")],
        "sources": [
            book_source(
                "02-sources/02-Markdown/20_CHP-20Postscript.md",
                "后记，印刷页397；OCR L22",
                "line 22; print p. 397",
                "Luigi Spezzaferro",
                "后记具名Spezzaferro，并概述其对Del Monte文化形成与科学兴趣的研究。",
            ),
            book_source(
                "02-sources/02-Markdown/21_CHP-21Bibliography.md",
                "书后参考书目，印刷页437；OCR L1126",
                "line 1126; print p. 437",
                "Spezzaferro, Luigi: ‘La cultura del Cardinal Del Monte e il primo tempo del Caravaggio’ in Storia dell’Arte, 1971, pp. 57-92.",
                "书目列出Luigi Spezzaferro发表于1971年的文章及页码。",
            ),
        ],
    },
]


def card_text(t: dict) -> str:
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": t["sources"],
        "created": DATE,
        "updated": DATE,
        "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relation_list = "、".join(f"`{sid}`" for sid in t["relation_ids"])
    name_rows = "\n".join(
        f"| {field} | {value} | {evidence} |"
        for field, value, evidence in t["name_rows"]
    )
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}

**English:** {t['description_en']}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
{name_rows}

### 本书相关内容

**中文：** {t['context_zh']}

**English:** {t['context_en']}

## 关系与证据

### 关系记录

当前没有登记在 `relations.csv` 中的正式关系。S2关系候选 {relation_list} 保留来源归因并留待S6裁决；本次S4身份登记不将其转为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four source-backed new person groups in S4.")
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
    accepted_paths = {
        line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")
    }
    statements = sync.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}

    for t in TARGETS:
        cid = t["candidate"]
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "person"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert members == [cid], (t["group"], members)
        assert t["ku"] not in manifest_by_ku
        assert t["card"] not in accepted_paths
        assert not (ROOT / t["card"]).exists()
        assert not any(
            row.get("type") == "person"
            and (row.get("name_en") or "").casefold() == t["name_en"].casefold()
            for row in manifest
        )
        for src in t["sources"]:
            source_file = (src.get("evidence_ref") or {}).get("source_file", "")
            if source_file.startswith("http"):
                assert source_file == VATICAN_URL and t["candidate"] == "cand-5453"
                continue
            source_text = (ROOT / source_file).read_text(encoding="utf-8-sig")
            for quote in src.get("original_quotes", []):
                assert quote["text"] in source_text, (cid, source_file, quote["source_span"])
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        }
        expected = {row[0] for row in t["statement_endpoints"]}
        assert direct == expected, (cid, direct, expected)
        for sid, subject, obj, predicate, quote in t["statement_endpoints"]:
            statement = statement_by_id[sid]
            assert statement.get("subject_candidate_id") == subject
            assert statement.get("object_candidate_id") == obj
            assert statement.get("predicate") == predicate
            assert quote in statement.get("original_quote", ""), (sid, quote)

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(
            row for row in planned_alignments
            if row.get("candidate_id") == t["candidate"] and not row.get("external_source")
        )
        row["ku_id"] = t["ku"]
        row["process_ref"] = PROCESS_REF
        suffix = (
            f" S4登记（{DATE}）：身份组{t['group']}映射至{t['ku']}；"
            "新增一张书内来源支持的人物KU，相关S2关系候选仍待S6。"
        )
        if t["candidate"] == "cand-5453":
            suffix += (
                "别名同一性另据Holy See 2025年礼仪文本PDF p.20、印刷页40–41的英意对照行核对；"
                "该外部来源只支持Aloysius/Luigi称名对应，不扩写书内事实。"
            )
        row["resolution_note"] = (row.get("resolution_note", "").rstrip() + suffix)
        planned_manifest.append({
            "ku_id": t["ku"],
            "type": "person",
            "canonical_name": t["name_zh"],
            "name_en": t["name_en"],
            "source_task": TASK,
            "card_path": t["card"],
        })
    planned_manifest.sort(key=lambda row: row["ku_id"])

    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = person_sync.insert_accepted(planned_accepted, t["card"])
    final_accepted_paths = {
        line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")
    }
    assert len(final_accepted_paths) == len(accepted_paths) + len(TARGETS)

    baseline_stats = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == baseline_stats["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == baseline_stats["person"]["registered_members"] + len(TARGETS)
    assert stats["person"]["pending_groups"] == baseline_stats["person"]["pending_groups"] - len(TARGETS)
    assert stats["person"]["pending_members"] == baseline_stats["person"]["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    cards = {t["card"]: card_text(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    rows = []
    for t in TARGETS:
        relations = "、".join(f"`{sid}`" for sid in t["relation_ids"])
        rows.append(
            f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）]"
            f"(../../../{t['card']})；S2候选{relations}留待S6；{t['context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### S4 person：Scaramuccia、Gonzaga、Crespi、Spezzaferro四组人物身份登记（{DATE}）\n\n"
        + "\n".join(rows)
        + "\n\n四组均按各自S3 new身份组登记为一个人物KU，未按名字相近合并。"
        "Scaramuccia人物候选cand-2390与版画作品候选cand-2391保持类型区分；Luigi Crespi与画家Giuseppe Maria Crespi保持人物区分；"
        "Spezzaferro及其文章候选cand-10882保持人物/文献区分。Luigi Gonzaga与Aloysius Gonzaga的别名同一性据梵蒂冈2025年英意礼仪对照行确认，未将外部资料用于扩写书内事实。"
        "四条S2关系候选均留待S6；未新增正式关系或enrichment字段。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、"
        f"{sync.fmt(stats['person']['pending_groups'])}组/"
        f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text += (
        f"\n\n### S4 人物身份组登记：四个直接关系端点（{DATE}）\n\n"
        + "；".join(
            f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`"
            for t in TARGETS
        )
        + "。四组均为S3 new，逐组登记一张KU；Luigi Gonzaga/Aloysius Gonzaga别名同一性据梵蒂冈礼仪文本核对。"
        "Scaramuccia相关作品cand-2391、Spezzaferro文章cand-10882和各关系候选维持独立S3/S6去向；Luigi Crespi关于佛罗伦萨停留的书内说法仍有冲突且未独立核读。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: four singleton person groups; source quotes, group membership, S2 endpoints, "
            f"accepted paths and duplicate names checked; manifest={len(manifest)}->{len(planned_manifest)}; "
            f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
            f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
            f"KU={len(planned_manifest)}; relation_rows_added=0; enrichment_rows_changed=0; no files changed"
        )
        return 0

    for rel_path, card in cards.items():
        (ROOT / rel_path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups=4; candidate_mappings=4; manifest={len(planned_manifest)}; "
        f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
        f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
        "relation_rows_added=0; enrichment_rows_changed=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
