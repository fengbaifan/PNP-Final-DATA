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
ANCHOR = "s4-person-direct-endpoints-ciarpi-castello-conduitt-corelli-corradini-coypel-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BT = chr(96)

TARGETS = [
    {
        "candidate": "cand-0745",
        "group": "new-person:baccio-ciarpi-ed3407fcf7",
        "ku": "units/persons/baccio-ciarpi",
        "card": "04-knowledge/units/persons/baccio-ciarpi.md",
        "name_zh": "巴乔·恰尔皮",
        "name_en": "Baccio Ciarpi",
        "name_field": "原文全名",
        "index_entry": "C.csv#269",
        "index_file": "C.csv",
        "index_name": "Ciarpi, Baccio",
        "index_page": "43",
        "source_fragments": ["Baccio Ciarpi", "his master"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "source_span": "lines 144-145; print p. 43",
                "location": "第2章 p.43；OCR L144-145",
                "summary": (
                    "Haskell称Baccio Ciarpi是Pietro da Cortona的老师，并将其列入Barberini时期祭坛画装饰的参与者；"
                    "相关画作没有逐件指认。"
                ),
                "quote": "Pietro da Cortona (and his master Baccio Ciarpi)",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第2章点名的Baccio Ciarpi。第43页称他是Pietro da Cortona的老师，并将他列入Barberini时期祭坛画装饰的参与者；"
            "没有识别Ciarpi对应的单件画作或具体分工。索引以“Ciarpi, Baccio”列出该人物。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Baccio Ciarpi named in Chapter 2. Page 43 calls him Pietro da Cortona's master and includes him among the participants in the "
            "Barberini altar-picture campaign; no individual picture or specific task is assigned to Ciarpi. The index lists “Ciarpi, Baccio.” The Chinese name "
            "is a working transliteration."
        ),
        "relation_ids": [
            "st-chp2-secii-l141-145-ciarpi-master-of-pietro",
            "st-chp2-secii-l141-145-baccio-ciarpi-paintings-contributed",
        ],
        "relation_context_zh": (
            "师承说按Haskell书内叙述保留；祭坛画只指一组未逐件识别的作品，不推定具体画作。两项候选留待S6。"
        ),
        "relation_context_en": (
            "The training statement is retained as Haskell's account; the altar paintings remain an unidentified group, with no individual work inferred. Both candidates remain for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp2-secii-l141-145-ciarpi-master-of-pietro",
                "cand-0745",
                "cand-0342",
                "master_of_reported",
                "master Baccio Ciarpi",
            ),
            (
                "st-chp2-secii-l141-145-baccio-ciarpi-paintings-contributed",
                "cand-0745",
                "cand-4545",
                "altar_paintings_contributed_reported",
                "master Baccio Ciarpi",
            ),
        ],
    },
    {
        "candidate": "cand-0766",
        "group": "new-person:castello-citta-da-di-matteo-8b25099440",
        "ku": "units/persons/matteo-da-castello",
        "card": "04-knowledge/units/persons/matteo-da-castello.md",
        "name_zh": "马泰奥·达·卡斯泰洛",
        "name_en": "Matteo da Castello",
        "name_field": "原文全名",
        "index_entry": "C.csv#290",
        "index_file": "C.csv",
        "index_name": "Città di Castello, Matteo da",
        "index_page": "68, 69",
        "source_fragments": [
            "architect Matteo da Castello",
            "replaced Matteo da Castello as architect",
        ],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "source_span": "line 38; print p. 68",
                "location": "第3章 p.68；OCR L38",
                "summary": (
                    "Haskell称Philip Neri与建筑师Matteo da Castello密切合作，后者由Oratorians选定。"
                ),
                "quote": "worked in close co-operation with the architect Matteo da Castello whom the Oratorians chose",
            },
            {
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_ii.md",
                "source_span": "line 46; print p. 69",
                "location": "第3章 p.69；OCR L46",
                "summary": (
                    "Haskell称Martino Longhi the Elder后来取代Matteo da Castello担任建筑师。"
                ),
                "quote": "Martino Longhi the Elder replaced Matteo da Castello as architect",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第3章点名的Matteo da Castello。第68页称他是Oratorians选定、并与Philip Neri密切合作的建筑师；"
            "第69页称Martino Longhi the Elder后来接替他。索引以“Città di Castello, Matteo da”列出相关页码。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records Matteo da Castello named in Chapter 3. Page 68 identifies him as the architect chosen by the Oratorians and says he worked "
            "closely with Philip Neri; page 69 says Martino Longhi the Elder later replaced him. The index lists the relevant pages under “Città di Castello, "
            "Matteo da.” The Chinese name is a working transliteration."
        ),
        "relation_ids": [
            "st-chp3-secii-l33-38-philip-worked-with-oratorian-chosen-matteo",
            "st-chp3-secii-l40-52-longhi-replaces-matteo",
        ],
        "relation_context_zh": (
            "建筑师由Oratorians选定、与Philip Neri合作，并由Longhi接任；均保留来源角色限定，候选留待S6。"
        ),
        "relation_context_en": (
            "The architect was selected by the Oratorians, worked with Philip Neri, and was later replaced by Longhi; preserve those source-defined roles for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp3-secii-l33-38-philip-worked-with-oratorian-chosen-matteo",
                "cand-1898",
                "cand-0766",
                "worked_in_close_cooperation_with_architect",
                "architect Matteo da Castello",
            ),
            (
                "st-chp3-secii-l40-52-longhi-replaces-matteo",
                "cand-1427",
                "cand-0766",
                "replaced_as_architect",
                "replaced Matteo da Castello as architect",
            ),
        ],
    },
    {
        "candidate": "cand-0820",
        "group": "new-person:conduitt-john-1595bc5af5",
        "ku": "units/persons/john-conduitt",
        "card": "04-knowledge/units/persons/john-conduitt.md",
        "name_zh": "约翰·康杜伊特",
        "name_en": "John Conduitt",
        "name_field": "原文全名",
        "index_entry": "C.csv#350",
        "index_file": "C.csv",
        "index_name": "Conduitt, John",
        "index_page": "290n, 291n, 304n",
        "source_fragments": ["Letter from John Conduitt to McSwiny", "June 1730 John Conduitt"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 545; print p. 290 n. 1",
                "location": "第10章 p.290 注1；OCR L545",
                "summary": (
                    "Haskell称一封John Conduitt于1729年6月4日写给McSwiny的信保存在King’s College, Cambridge的Conduitt papers中；"
                    "信件未独立查阅。"
                ),
                "quote": "Letter from John Conduitt to McSwiny of 4 June 1729 kept among the Conduitt papers in the Library of King’s College, Cambridge",
            },
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 608; print p. 304 n. 4",
                "location": "第10章 p.304 注4；OCR L608",
                "summary": (
                    "Haskell引述John Conduitt于1730年6月要求Smith代购三幅Canaletto作品，并指向p.290注1；"
                    "该交叉引用对应的是1729年另一封信，身份与来源对应未决。"
                ),
                "quote": "in June 1730 John Conduitt ‘desired Mr S[mith] to procure 3 pictures from Canaletto’ —see p. 290, note 1",
            },
        ],
        "description_zh": (
            "本卡登记Haskell第10章索引及注释中点名的John Conduitt。第290页注1称一封1729年6月4日致McSwiny的信保存在Conduitt papers；"
            "第304页注4另引述他于1730年6月请Smith代购三幅Canaletto画作，却回指第290页注1。S2已标明该引用与日期不吻合，"
            "被引信件的身份和来源对应仍未解决；本卡不把两处记录合并为同一信。正文OCR另有“John Conduits”异拼，候选账本保留。"
            "中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records John Conduitt named in the Chapter 10 index and notes. Note 1 on page 290 reports a letter to McSwiny dated 4 June 1729 "
            "among the Conduitt papers; note 4 on page 304 quotes a June 1730 request for Smith to procure three Canaletto pictures but points back to note 1 "
            "on page 290. S2 records that the cross-reference and dates do not match, leaving the identity and provenance of the quoted record unresolved; "
            "this card does not merge the two records into one letter. One OCR mention also reads “John Conduits,” retained in the candidate ledger. The "
            "Chinese name is a working transliteration."
        ),
        "relation_ids": [
            "st-chp10-p290-note1-letter-direction",
            "st-chp10-p304-note4-conduitt-procurement-request",
        ],
        "relation_context_zh": (
            "1729年致McSwiny信与1730年代购引文之间的内部引用不吻合；信件身份和出处未决，两项S2候选均留待S6。"
        ),
        "relation_context_en": (
            "The internal reference between the 1729 letter to McSwiny and the June 1730 procurement quotation does not match; the record's identity and "
            "provenance remain unresolved, and both S2 candidates remain for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp10-p290-note1-letter-direction",
                "cand-9420",
                "cand-0820",
                "haskell_reports_conduitt_letter_to_mcswiny",
                "Letter from John Conduitt to McSwiny",
            ),
            (
                "st-chp10-p304-note4-conduitt-procurement-request",
                "cand-0820",
                "cand-2440",
                "requested_procurement_of_works",
                "John Conduitt",
            ),
        ],
    },
    {
        "candidate": "cand-0843",
        "group": "new-person:arcangelo-corelli-ed47e21c49",
        "ku": "units/persons/arcangelo-corelli",
        "card": "04-knowledge/units/persons/arcangelo-corelli.md",
        "name_zh": "阿尔坎杰洛·科雷利",
        "name_en": "Arcangelo Corelli",
        "name_field": "索引名",
        "index_entry": "C.csv#373",
        "index_file": "C.csv",
        "index_name": "Corelli, Arcangelo",
        "index_page": "165n",
        "source_fragments": ["Arcangelo CoreUi", "He owned a Europa by Ricci"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/06_CHP-6_sec_v.md",
                "source_span": "line 66; print p. 165 n. 3",
                "location": "第6章 p.165 注3；OCR L66",
                "summary": (
                    "Haskell称Ottoboni的朋友中有小提琴家Arcangelo Corelli，并称他拥有一幅Ricci的Europa；作品题名或身份尚未确定，"
                    "被引库存目录未独立查阅。OCR将Corelli识作CoreUi。"
                ),
                "quote": "Among these friends was the great violinist Arcangelo CoreUi. He owned a Europa by Ricci",
            },
        ],
        "description_zh": (
            "本卡登记索引名为Arcangelo Corelli的人物。Haskell第6章注3称他是Ottoboni的朋友，并称他拥有一幅Ricci的《Europa》；"
            "注释未给作品完整题名，所引库存目录未独立查阅。当前OCR将姓名识作“CoreUi”，本卡按索引全名登记并保留该识读差异；"
            "不把这条记录与其他《Europa》作品合并。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records the person indexed as Arcangelo Corelli. Chapter 6, note 3, names him as one of Ottoboni's friends and says he owned a Europa "
            "by Ricci; the note gives no full title, and the cited inventory was not independently consulted. The current OCR reads the name as “CoreUi”; "
            "the index supplies the full form used here, with the reading difference retained. This record is not merged with other Europa works. The Chinese "
            "name is a working transliteration."
        ),
        "relation_ids": ["st-chp6-p165-n3-europa", "st-chp6-p165-n3-friend"],
        "relation_context_zh": (
            "友谊为Haskell注释所述；Ricci作品仅称Europa且库存目录未查，作品身份未决。两项候选留待S6。"
        ),
        "relation_context_en": (
            "The friendship is reported in Haskell's note; the Ricci work is identified only as a Europa and the inventory was not consulted, leaving the work "
            "identity unresolved. Both candidates remain for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp6-p165-n3-europa",
                "cand-0843",
                "cand-6586",
                "owned_artwork",
                "He owned a Europa by Ricci",
            ),
            (
                "st-chp6-p165-n3-friend",
                "cand-0843",
                "cand-1795",
                "friend_of",
                "Among these friends was the great violinist",
            ),
        ],
    },
    {
        "candidate": "cand-0849",
        "group": "new-person:antonio-corradini-f5fd2d8463",
        "ku": "units/persons/antonio-corradini",
        "card": "04-knowledge/units/persons/antonio-corradini.md",
        "name_zh": "安东尼奥·科拉迪尼",
        "name_en": "Antonio Corradini",
        "name_field": "索引名",
        "index_entry": "C.csv#379",
        "index_file": "C.csv",
        "index_name": "Corradini, Antonio",
        "index_page": "241, 265, 312",
        "source_fragments": ["sculpted by Corradini and Morlaiter"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
                "source_span": "lines 19-20; print p. 312",
                "location": "第10章 p.312；OCR L19-20",
                "summary": (
                    "Haskell将Corradini列为为Schulenburg制作雕像肖像的雕塑家；没有指认具体作品。"
                ),
                "quote": "sculpted by Corradini and Morlaiter",
            },
        ],
        "description_zh": (
            "本卡登记索引名为Antonio Corradini的雕塑家。Haskell第10章第312页将Corradini与Morlaiter并列，列为制作Schulenburg肖像雕塑的艺术家；"
            "没有指认单件雕塑。索引以“Corradini, Antonio”列出该人物，并指向第241、265、312页。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records the sculptor indexed as Antonio Corradini. Chapter 10, page 312, lists Corradini alongside Morlaiter among the sculptors of "
            "Schulenburg portraits, without identifying an individual sculpture. The index lists “Corradini, Antonio” at pages 241, 265, and 312. The Chinese "
            "name is a working transliteration."
        ),
        "relation_ids": ["st-chp10-p312-corradini-sculpted-portraits-of"],
        "relation_context_zh": (
            "Haskell只列出肖像雕塑家，没有给出具体作品题名；该S2候选留待S6。"
        ),
        "relation_context_en": (
            "Haskell lists the portrait sculptor but gives no individual sculpture title; the S2 candidate remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp10-p312-corradini-sculpted-portraits-of",
                "cand-0849",
                "cand-2401",
                "sculpted_portraits_of",
                "sculpted by Corradini",
            ),
        ],
    },
    {
        "candidate": "cand-0866",
        "group": "new-person:antoine-coypel-d0089dab93",
        "ku": "units/persons/antoine-coypel",
        "card": "04-knowledge/units/persons/antoine-coypel.md",
        "name_zh": "安托万·柯佩尔",
        "name_en": "Antoine Coypel",
        "name_field": "索引名",
        "index_entry": "C.csv#399",
        "index_file": "C.csv",
        "index_name": "Coypel, Antoine",
        "index_page": "285",
        "source_fragments": ["She met Rigaud and Watteau", "Coypel, Vleughels, Oppenord"],
        "book_sources": [
            {
                "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
                "source_span": "line 186; print p. 285",
                "location": "第10章 p.285；OCR L186",
                "summary": (
                    "Haskell将Coypel列入Carriera在巴黎遇见的艺术家与鉴赏家名单；没有描述单独会面。"
                ),
                "quote": "She met Rigaud and Watteau, both of whom expressed their deep admiration, and all the other artists and connoisseurs—Coypel, Vleughels, Oppenord, de Troy, Mariette.",
            },
        ],
        "description_zh": (
            "本卡登记索引名为Antoine Coypel的人物。Haskell第10章第285页将Coypel列入Carriera在巴黎遇见的艺术家与鉴赏家名单；"
            "原文没有给出与Coypel单独会面的细节。索引以“Coypel, Antoine”列出该人物。中文名为本项目工作音译。"
        ),
        "description_en": (
            "This card records the person indexed as Antoine Coypel. Chapter 10, page 285, includes Coypel in a list of artists and connoisseurs whom Carriera "
            "met in Paris; it gives no details of an individual encounter. The index lists “Coypel, Antoine.” The Chinese name is a working transliteration."
        ),
        "relation_ids": ["st-chp10-p285-carriera-met-coypel"],
        "relation_context_zh": (
            "S2只将Coypel列入集体名单，没有提供单独会面的细节；候选留待S6。"
        ),
        "relation_context_en": (
            "S2 places Coypel in a collective list and gives no separate encounter details; the candidate remains for S6."
        ),
        "statement_endpoints": [
            (
                "st-chp10-p285-carriera-met-coypel",
                "cand-0581",
                "cand-0866",
                "met",
                "Coypel, Vleughels, Oppenord",
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
            f" S4登记（{DATE}）：{t['group']} 映射至 {t['ku']}；书内索引与正文共同支持source-local人物登记，"
            "来源限定与未决对应保留，直接关系候选仍待S6。"
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
    assert totals["registered_groups"] == 775 and totals["registered_members"] == 946
    assert totals["pending_groups"] == 4001 and totals["pending_members"] == 4015
    assert stats["person"]["registered_groups"] == 369
    assert stats["person"]["registered_members"] == 455
    assert stats["person"]["pending_groups"] == 699
    assert stats["person"]["pending_members"] == 700
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
        + "\n\n本批登记6个单候选S3 new人物组，每组映射至一张KU。Conduitt的1729/1730内部引用差异、"
        "Corelli作品题名与OCR异拼、其余对象的来源范围均保留；本批没有添加外部身份事实或formal relations。\n\n"
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
        + "。六组均为S3单候选new组；姓名字段与书内依据可追溯。S2关系候选留待S6，本批不创建formal relations。"
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
