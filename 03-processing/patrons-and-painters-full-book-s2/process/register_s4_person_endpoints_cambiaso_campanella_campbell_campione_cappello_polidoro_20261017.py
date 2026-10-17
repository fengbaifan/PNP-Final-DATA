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
ANCHOR = "s4-person-direct-endpoints-cambiaso-campanella-campbell-campione-cappello-polidoro-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BT = chr(96)

TARGETS = [
    {
        "candidate": "cand-0488",
        "group": "new-person:cambiaso-luca-7e46c6cf0e",
        "ku": "units/persons/luca-cambiaso",
        "card": "04-knowledge/units/persons/luca-cambiaso.md",
        "name_zh": "卢卡·坎比亚索",
        "name_en": "Luca Cambiaso",
        "name_field": "原文全名",
        "index_entry": "C.csv#12",
        "index_file": "C.csv",
        "index_name": "Cambiaso, Luca",
        "index_page": "29",
        "source_fragments": [
            "Luca Cambiaso",
            "experiments with lighting may well have seemed to anticipate those of Caravaggio",
        ],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_i.md",
                "source_span": "lines 101-102; print p. 29",
                "location": "第2章 p.29；OCR L101-102",
                "summary": (
                    "Haskell将Luca Cambiaso列入Giustiniani收藏中其他画家的作品，并称其照明实验可能使人联想到Caravaggio；"
                    "原文没有识别单件作品，比较保留推测语气。"
                ),
                "quote": "Luca Cambiaso, the Genoese painter whose experiments with lighting may well have seemed to anticipate those of Caravaggio",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第2章点名的Luca Cambiaso。第29页将他的作品列入Giustiniani收藏，并称其照明实验“可能”使人联想到Caravaggio；"
            "原文没有识别单件作品，也不把比较写成直接影响。索引以“Cambiaso, Luca”列出该人物并指向同页。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Luca Cambiaso named in Chapter 2. On page 29, Haskell includes work by him in Giustiniani's collection and says his experiments "
            "with lighting may well have seemed to anticipate Caravaggio's. No individual picture is identified, and the comparison is not stated as direct "
            "influence. The index lists “Cambiaso, Luca” at the same page. The Chinese name is a working transliteration."
        ),
        "relation_ids": [
            "st-chp2-seci-l95-106-cambiaso-collection",
            "st-chp2-seci-l95-106-lighting-comparison",
        ],
        "relation_context_zh": (
            "作品归属候选指向原文所述的一组未逐件识别的收藏画作；照明比较保留“可能”限定。两项均留待S6，不创建正式关系。"
        ),
        "relation_context_en": (
            "The attribution candidate concerns an unspecified group of collection pictures, not individually identified works; the lighting comparison retains "
            "its qualification. Both remain for S6, and no formal relation is created."
        ),
        "statement_endpoints": [
            (
                "st-chp2-seci-l95-106-cambiaso-collection",
                "cand-0488",
                "cand-11568",
                "creator_of",
                "Luca Cambiaso",
            ),
            (
                "st-chp2-seci-l95-106-lighting-comparison",
                "cand-0488",
                "cand-0544",
                "authorial_qualified_comparison",
                "may well have seemed to anticipate those of Caravaggio",
            ),
        ],
    },
    {
        "candidate": "cand-0491",
        "group": "new-person:campanella-tommaso-08b48e27fb",
        "ku": "units/persons/tommaso-campanella",
        "card": "04-knowledge/units/persons/tommaso-campanella.md",
        "name_zh": "托马索·坎帕内拉",
        "name_en": "Tommaso Campanella",
        "name_field": "索引名",
        "index_entry": "C.csv#15",
        "index_file": "C.csv",
        "index_name": "Campanella, Tommaso",
        "index_page": "40n",
        "source_fragments": [
            "Campanella helped him in his researches",
            "spying on Campanella hi Paris",
        ],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "source_span": "line 182; print p. 40 n. 3",
                "location": "第2章 p.40 注3；OCR L182",
                "summary": (
                    "Haskell注3称Walker发表的材料显示Campanella帮助Urban VIII进行研究，并转述Barberini下令在巴黎监视Campanella；"
                    "注中所引Walker与Bazzoni均未在本任务中独立查阅。"
                ),
                "quote": "which shows that Campanella helped him in his researches. The rather sinister spying on Campanella hi Paris",
            },
        ],
        "description_zh": (
            "本卡登记索引名为Tommaso Campanella的人物。Haskell第2章注3称，Walker发表的材料显示Campanella帮助Urban VIII进行研究；"
            "同一注还转述Barberini下令在巴黎监视Campanella。以上均为Haskell对所引材料的转述，Walker与Bazzoni未在本任务中独立查阅，"
            "索引页码为第40页注3。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records the person indexed as Tommaso Campanella. Chapter 2, note 3, says that material published by Walker shows Campanella helping "
            "Urban VIII in his researches; the same note reports that the Barberini ordered surveillance of Campanella in Paris. These are Haskell's reports "
            "of cited material. Walker and Bazzoni were not independently consulted in this task. The index points to page 40 note 3. The Chinese name is a "
            "working transliteration."
        ),
        "relation_ids": [
            "st-chp2-secii-l147-193-campanella-urban-research",
            "st-chp2-secii-l147-193-campanella-surveillance",
        ],
        "relation_context_zh": (
            "帮助Urban VIII研究与Barberini下令监视Campanella均为注释转述；引文来源未独立查阅，保持S2限定并留待S6。"
        ),
        "relation_context_en": (
            "The reported assistance to Urban VIII and surveillance ordered by the Barberini both come through a footnote's account of cited sources; those "
            "sources were not independently consulted. Preserve the S2 qualifications and leave both candidates for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp2-secii-l147-193-campanella-urban-research",
                "cand-0491",
                "cand-0209",
                "research_assistance_reported",
                "Campanella helped him in his researches",
            ),
            (
                "st-chp2-secii-l147-193-campanella-surveillance",
                "cand-3464",
                "cand-0491",
                "surveillance_reported",
                "spying on Campanella hi Paris",
            ),
        ],
    },
    {
        "candidate": "cand-0493",
        "group": "new-person:campbell-colen-dc5c057058",
        "ku": "units/persons/colen-campbell",
        "card": "04-knowledge/units/persons/colen-campbell.md",
        "name_zh": "科伦·坎贝尔",
        "name_en": "Colen Campbell",
        "name_field": "原文全名",
        "index_entry": "C.csv#17",
        "index_file": "C.csv",
        "index_name": "Campbell, Colen",
        "index_page": "309",
        "source_fragments": ["Colen Campbell", "Vitruvius Britannicus"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "lines 469-471; print p. 309",
                "location": "第10章 p.309；OCR L469-471",
                "summary": (
                    "Haskell说十一幅画中有两幅描绘Colen Campbell的作品，并称该组画主要依据其《Vitruvius Britannicus》的版画；"
                    "前者不是说Campbell绘制了这两幅画。"
                ),
                "quote": "two by Colen Campbell",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第10章点名的Colen Campbell。第309页说，十一幅画中有两幅描绘Campbell的作品；紧接着称这一系列主要依据"
            "《Vitruvius Britannicus》的版画。原文没有说Campbell绘制了这两幅画。索引列出“Campbell, Colen”，并有"
            "“Vitruvius Britannicus”子项。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Colen Campbell named in Chapter 10. Page 309 says that two of eleven pictures portray works by Campbell and then says that the "
            "series was based primarily on engravings from *Vitruvius Britannicus*. The source does not say that Campbell made the two pictures. The index lists "
            "“Campbell, Colen” with a “Vitruvius Britannicus” subentry. The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp10-p309-two-pictures-after-campbell"],
        "relation_context_zh": (
            "该候选指两幅画描绘Campbell的作品，不表示Campbell本人绘制这两幅画；正式关系留待S6。"
        ),
        "relation_context_en": (
            "The candidate says two pictures portray works by Campbell; it does not attribute the pictures themselves to him. The formal relation remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp10-p309-two-pictures-after-campbell",
                "cand-9251",
                "cand-0493",
                "two_of_eleven_pictures_portray_works_by_colen_campbell",
                "two by Colen Campbell",
            ),
        ],
    },
    {
        "candidate": "cand-0494",
        "group": "new-person:campione-da-giovanni-587cbff61c",
        "ku": "units/persons/giovanni-da-campione",
        "card": "04-knowledge/units/persons/giovanni-da-campione.md",
        "name_zh": "乔瓦尼·达·坎皮奥内",
        "name_en": "Giovanni da Campione",
        "name_field": "原文全名",
        "index_entry": "C.csv#18",
        "index_file": "C.csv",
        "index_name": "Campione, Giovanni da",
        "index_page": "215",
        "source_fragments": [
            "Giovanni da Campione",
            "he also built the rather more restrained entrance to the south",
        ],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
                "source_span": "line 13; print p. 215",
                "location": "第8章 p.215；OCR L13",
                "summary": (
                    "Haskell称Giovanni da Campione于1355年建造Santa Maria Maggiore的哥特式门廊，数年后又建造南侧较为简朴的入口；"
                    "后者没有给出确切年份。"
                ),
                "quote": "In 1355 Giovanni da Campione erected the delicate but richly ornamented Gothic portico",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第8章点名的Giovanni da Campione。第215页称他于1355年建造Santa Maria Maggiore的哥特式门廊，"
            "数年后又建造南侧较为简朴的入口；后一个时间仍只是相对表述。索引以“Campione, Giovanni da”列出该人物并指向同页。"
            "中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Giovanni da Campione named in Chapter 8. Page 215 says that he erected the Gothic portico of Santa Maria Maggiore in 1355 and "
            "built a more restrained south entrance a few years later; the latter date remains relative. The index lists “Campione, Giovanni da” at the same "
            "page. The Chinese name is a working transliteration."
        ),
        "relation_ids": [
            "st-chp8-p215-campione-erected-gothic-portico-1355",
            "st-chp8-p215-campione-built-south-entrance",
        ],
        "relation_context_zh": (
            "门廊与南入口是两项不同建造陈述；后一项只给出“数年后”，不补出确切年份。两项关系均留待S6。"
        ),
        "relation_context_en": (
            "The portico and south entrance are two separate construction statements; the latter is dated only as a few years later. Both remain for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp8-p215-campione-erected-gothic-portico-1355",
                "cand-0494",
                "cand-7629",
                "erected_gothic_portico_in_1355",
                "Giovanni da Campione erected",
            ),
            (
                "st-chp8-p215-campione-built-south-entrance",
                "cand-0494",
                "cand-7631",
                "built_south_entrance_a_few_years_after_1355",
                "he also built the rather more restrained entrance to the south",
            ),
        ],
    },
    {
        "candidate": "cand-0537",
        "group": "new-person:antonio-cappello-17b238059e",
        "ku": "units/persons/antonio-cappello",
        "card": "04-knowledge/units/persons/antonio-cappello.md",
        "name_zh": "安东尼奥·卡佩洛",
        "name_en": "Antonio Cappello",
        "name_field": "原文全名",
        "index_entry": "C.csv#61",
        "index_file": "C.csv",
        "index_name": "Cappello, Antonio",
        "index_page": "367",
        "source_fragments": ["commissioned by Antonio Cappello from Giovanni Ferrari"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/15_CHP-15_sec_ii.md",
                "source_span": "line 36; print p. 367",
                "location": "第15章 p.367；OCR L36",
                "summary": (
                    "Haskell称Canova自己的雕像由Antonio Cappello委托Giovanni Ferrari制作；该句分别指出委托人、雕像对象与制作人。"
                ),
                "quote": "the sculptor’s own statue, commissioned by Antonio Cappello from Giovanni Ferrari",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第15章点名的Antonio Cappello。第367页称，Canova自己的雕像由Cappello委托Giovanni Ferrari制作；"
            "此处委托对象是雕像，制作人是Ferrari。索引以“Cappello, Antonio”列出该人物并指向同页。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Antonio Cappello named in Chapter 15. Page 367 says that Cappello commissioned Giovanni Ferrari to make a statue of Canova; the "
            "commissioned object is the statue and Ferrari is identified as its maker. The index lists “Cappello, Antonio” at the same page. The Chinese name "
            "is a working transliteration."
        ),
        "relation_ids": ["st-chp15-p367-canova-statue-commissioned-by-cappello-from-ferrari"],
        "relation_context_zh": (
            "S2陈述是Cappello委托Ferrari制作Canova雕像，不是Cappello直接委托Canova创作；正式关系留待S6。"
        ),
        "relation_context_en": (
            "The S2 statement is that Cappello commissioned Ferrari to make a statue of Canova, not that Cappello directly commissioned Canova. The formal relation "
            "remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp15-p367-canova-statue-commissioned-by-cappello-from-ferrari",
                "cand-11531",
                "cand-0537",
                "commissioned_by",
                "commissioned by Antonio Cappello",
            ),
        ],
    },
    {
        "candidate": "cand-0553",
        "group": "new-person:caravaggio-da-polidoro-2585cffaf3",
        "ku": "units/persons/polidoro-da-caravaggio",
        "card": "04-knowledge/units/persons/polidoro-da-caravaggio.md",
        "name_zh": "波利多罗·达·卡拉瓦乔",
        "name_en": "Polidoro da Caravaggio",
        "name_field": "原文全名",
        "index_entry": "C.csv#77",
        "index_file": "C.csv",
        "index_name": "Caravaggio, Polidoro da",
        "index_page": "124, 210",
        "source_fragments": [
            "Polidoro da Caravaggio",
            "Polidoro da",
            "Caravaggio",
            "special interest in Polidoro da",
        ],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
                "source_span": "lines 37-38; print p. 124",
                "location": "第5章 p.124；OCR L37-38",
                "summary": (
                    "Haskell称Niccolò Simonelli收藏的素描包括Polidoro da Caravaggio的作品；此处作为跨章姓名锚点，不新建正式关系。"
                ),
                "quote": "Romano, Polidoro da Caravaggio and Annibale Carracci",
            },
            {
                "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md",
                "source_span": "lines 75-76; print p. 210",
                "location": "第8章 p.210；OCR L75-76",
                "summary": (
                    "Haskell称Ruffo对Polidoro da Caravaggio这位古代大师特别感兴趣；OCR正文将Ruffo识作Russo，S2已按纸本限定记录该校正。"
                ),
                "quote": "Of old masters Russo showed a special interest in Polidoro da Caravaggio",
            },
        ],
        "description_zh": (
            "本卡按跨章身份组登记Polidoro da Caravaggio：第5章第124页在Niccolò Simonelli的素描收藏中以全名提及他；"
            "第8章第210页再次以全名称其为Ruffo特别感兴趣的古代大师。后者OCR将Ruffo识作Russo，S2已依据纸本记录校正。"
            "索引“Caravaggio, Polidoro da”同时指向两页。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card registers Polidoro da Caravaggio as one cross-chapter identity group. Chapter 5, page 124, names him in Niccolò Simonelli’s drawing "
            "collection; Chapter 8, page 210, again gives his full name and says Ruffo took special interest in him as an old master. The Chapter 8 OCR reads "
            "“Russo” for Ruffo; S2 records the print-based correction. The index entry “Caravaggio, Polidoro da” points to both pages. The Chinese name is a "
            "working transliteration."
        ),
        "relation_ids": ["st-chp8-p210-ruffo-interest-in-polidoro-da-caravaggio"],
        "relation_context_zh": (
            "第8章S2候选为Ruffo对Polidoro的兴趣，保留纸本校正及原文范围；第5章仅用作跨章身份锚点。本批不创建正式关系，候选留待S6。"
        ),
        "relation_context_en": (
            "The Chapter 8 S2 candidate concerns Ruffo’s interest in Polidoro and retains the print-based correction and source scope; Chapter 5 serves as a "
            "cross-chapter identity anchor. No formal relation is created, and the candidate remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp8-p210-ruffo-interest-in-polidoro-da-caravaggio",
                "cand-2297",
                "cand-0553",
                "collector_showed_special_interest_in_old_master_polidoro_da_caravaggio",
                "special interest in Polidoro da",
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
    index_location = f"全书索引 {t['index_entry']}；所列页码{t['index_page']}"
    sources = [
        {
            "citation": INDEX_CITATION,
            "location": index_location,
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
            f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；索引与正文共同支持本批source-local人物登记，"
            "直接关系候选仍待S6。"
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
    assert totals["registered_groups"] == 757 and totals["registered_members"] == 928
    assert totals["pending_groups"] == 4019 and totals["pending_members"] == 4033
    assert stats["person"]["registered_groups"] == 351
    assert stats["person"]["registered_members"] == 437
    assert stats["person"]["pending_groups"] == 717
    assert stats["person"]["pending_members"] == 718
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
        + "\n\n本批登记6个单候选S3 new人物组，每组映射至一张KU；姓名字段均由书内索引或正文支持。"
        "Polidoro da Caravaggio的cand-0553由第5章与第8章的全名提及组成跨章身份锚点。"
        "本批没有加入外部身份事实或formal relations；其余未决与冲突对象保持原有去向。\n\n"
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
        + "。六组均为S3单候选new组；Polidoro da Caravaggio以第5、8章全名锚点合并登记。"
        "对应S2关系候选留待S6；本批不创建formal relations，也不添加外部身份事实。"
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
