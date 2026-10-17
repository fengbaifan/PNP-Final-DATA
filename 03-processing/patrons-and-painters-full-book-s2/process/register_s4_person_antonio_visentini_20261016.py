from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import shutil
from io import StringIO
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge/tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge/results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge/accepted.yml"
DATE = "2026-10-16"

CANDIDATE = "cand-2783"
GROUP = "new-person:antonio-visentini-26bdbd19e8"
KU_ID = "units/persons/antonio-visentini"
CARD_REL = "04-knowledge/units/persons/antonio-visentini.md"
CARD = ROOT / CARD_REL
NAME_ZH = "安东尼奥·维森蒂尼"
NAME_EN = "Antonio Visentini"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
TRECCANI_URL = "https://www.treccani.it/enciclopedia/antonio-visentini_(Dizionario-Biografico)/"
ICCD_URL = "https://catalogo.beniculturali.it/Agent/7304fc00c8dfda8cd628ce9554df755d"
GALLERIE_URL = "https://www.gallerieaccademia.it/opera/fantasia-architettonica/"
BACKUP_SUFFIX = ".bak-s4-antonio-visentini-20261016"

BOOK_SOURCES = (
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章 p.306；OCR L437",
        "span": "line 437; print p. 306",
        "summary": "正文称 Smith 保留的原始绘稿大多出自 Visentini；该处仅用姓氏，结合第10章 p.308 的全名身份锚点阅读。",
        "quotes": (("line 437", "Smith retained the original drawings most of which were by Visentini"),),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章 pp.308–309；OCR L464–465、474–478",
        "span": "lines 464–465, 474–478; print pp. 308–309",
        "summary": "正文以全名 Antonio Visentini 记其为 Smith 长期聘用的建筑师和书籍插图者，并记录其更新 Gallacini 论建筑错误的著作。p.309 另称 Visentini 建造一座宫殿的新古典化大理石立面，但该句 his palace 的指代不在本次身份裁决中消解。",
        "quotes": (
            ("line 464", "Antonio Visentini had already been employed by him for more than fifteen years as an architect and book illustrator"),
            ("line 474", "Antonio Visentini with a series of bitter attacks on the Baroque architects"),
            ("line 478", "Visentini built a new classicising marble façade for his palace"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章 p.301 注2、注4；OCR L589–591",
        "span": "lines 589–591; print p. 301 notes",
        "summary": "注释将 Smith 与 Visentini 的合作安排作审慎类比，并称 Poleni 请 Smith 向 Visentini 取得绘图；不把这些注释扩写成已核实的关系类型。",
        "quotes": (
            ("line 589", "it seems likely that Smith had some similar arrangement with Visentini"),
            ("line 591", "Polòni asks Smith to obtain some drawings for him from Visentini"),
        ),
    },
    {
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
        "location": "第10章 p.322；OCR L181",
        "span": "line 181; print p. 322",
        "summary": "正文推测 Lodoli 可能与 Canaletto、Visentini 等艺术家保持密切接触，措辞为 may，保留为待审关系候选。",
        "quotes": (("line 181", "It seems more likely that he may have been in close touch with artists like Canaletto and Visentini"),),
    },
    {
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章 p.338；OCR L65–66",
        "span": "lines 65–66; print p. 338",
        "summary": "正文称 Pasquali 支持 Visentini 对巴洛克建筑的批评；姓氏形式由第10章全名及索引锚点校对。",
        "quotes": (("lines 65–66", "later we find him supporting Visentini’s attack on Baroque architecture"),),
    },
    {
        "source_file": "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv",
        "location": "全书索引 UVWXYZ.csv#119；页码 301n、306、309、322、338",
        "span": "UVWXYZ.csv#119",
        "summary": "索引以 Visentini, Antonio 列出第10章注释与正文及第13章的对应页码。",
        "quotes": (("UVWXYZ.csv#119", "Visentini, Antonio"),),
    },
)


def source_row(item: dict) -> dict:
    return {
        "citation": (
            BOOK_CITATION
            if item["source_file"].startswith("02-sources/02-Markdown/")
            else "Francis Haskell, *Patrons and Painters*, index"
        ),
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [
            {"source_span": span, "text": quote}
            for span, quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["source_file"],
            "source_span": item["span"],
        },
    }


def make_card() -> str:
    sources = [source_row(item) for item in BOOK_SOURCES]
    sources.extend(
        [
            {
                "citation": f"Elisabetta Molteni, “VISENTINI, Antonio,” *Dizionario Biografico degli Italiani*, vol. 99 (2020). {TRECCANI_URL} Accessed {DATE}.",
                "location": "Entry heading; birth and death paragraphs; professional and Smith context",
                "sentence_summary": (
                    "The DBI identifies Antonio Visentini, born in Venice on 21 November 1688 and deceased there on 26 June 1782. "
                    "It describes him as an architect, painter, engraver, graphic designer, and author, and discusses his long professional "
                    "connection with Joseph Smith, his work as an illustrator, and his continuation of Gallaccini's architectural criticism."
                ),
            },
            {
                "citation": f"Catalogo Generale dei Beni Culturali (ICCD), agent record 7304fc00c8dfda8cd628ce9554df755d. {ICCD_URL} Accessed {DATE}.",
                "location": "Agent record heading and linked work records",
                "sentence_summary": "The national cultural heritage catalogue has an artist authority record under Visentini Antonio, dated 1688–1782, with records of works attributed to or associated with him.",
            },
            {
                "citation": f"Gallerie dell’Accademia di Venezia, “Fantasia architettonica,” catalogue 448. {GALLERIE_URL} Accessed {DATE}.",
                "location": "Artist field and work record",
                "sentence_summary": "The museum catalogue names the artist Antonio Maria Visentini and gives Venice, 1688–1782, providing a documented name variant with matching dates.",
            },
        ]
    )
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p306 = "[第10章 p.306](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L437）"
    p308 = "[第10章 pp.308–309](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L464–478）"
    notes = "[第10章 p.301 注2、注4](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L589–591）"
    p322 = "[第10章 p.322](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L181）"
    p338 = "[第13章 p.338](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L65–66）"
    index = "[全书索引 UVWXYZ.csv#119](../../../02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv)"
    treccani = f"[Treccani DBI]({TRECCANI_URL})"
    iccd = f"[意大利文化遗产总目录（ICCD）]({ICCD_URL})"
    gallerie = f"[威尼斯学院美术馆目录]({GALLERIE_URL})"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 全书索引以“Visentini, Antonio”列出第10章注释与正文及第13章的页码。第10章 p.308 以全名记载 Antonio Visentini 长期为 Joseph Smith 担任建筑师和书籍插图者；p.306 称 Smith 保留的原始绘稿多为 Visentini 所作，p.309 记其续写 Gallacini 的建筑批评。第13章再次提到 Pasquali 支持 Visentini 对巴洛克建筑的批评。Treccani DBI、意大利文化遗产总目录及威尼斯学院美术馆记录在姓名、威尼斯活动语境和1688–1782年日期上吻合；美术馆使用变体名 Antonio Maria Visentini。中文名为项目工作音译。{index} {p306} {p308} {p338} {treccani} {iccd} {gallerie}

**English:** The book’s index lists “Visentini, Antonio” across the notes and text of Chapter 10 and the text of Chapter 13. Chapter 10 names Antonio Visentini as an architect and book illustrator employed by Joseph Smith for more than fifteen years; it says that most of the original drawings retained by Smith were by Visentini and records his continuation of Gallaccini’s architectural criticism. Chapter 13 again mentions Pasquali’s support for Visentini’s criticism of Baroque architecture. Treccani’s DBI, the Italian national cultural heritage catalogue, and the Gallerie dell’Accademia records agree on the identity, Venetian context, and dates 1688–1782; the museum uses the variant name Antonio Maria Visentini. The Chinese display name is a project working transliteration. {index} {p306} {p308} {p338} {treccani} {iccd} {gallerie}

### 名称与身份比对

- **规范展示名：** Antonio Visentini，依本书第10章正文全名及全书索引。{p308} {index}
- **姓名异形：** Visentini, Antonio（索引形式）；Antonio Maria Visentini（威尼斯学院美术馆作品目录形式）。姓名形式与1688–1782年日期相互对应。{index} {gallerie}
- **身份：** 威尼斯人建筑师、画家、雕刻家、图形设计者及建筑/透视论著作者。Treccani DBI 的专业描述与本书建筑师、插图者及建筑批评语境吻合。{treccani}
- **生卒：** 1688年11月21日生于威尼斯，1782年6月26日卒于威尼斯。{treccani} 意大利国家目录与威尼斯学院美术馆也采用1688–1782年范围。{iccd} {gallerie}
- **身份边界：** p.309 “his palace”的具体所指未由本次身份登记裁定；p.322 关于 Lodoli 与 Visentini 密切接触的表述是作者推测。相关陈述保持各自证据状态，不因本卡而成为正式关系。{p308} {p322}

### 跨章语境

本书索引的 p.301 注释、p.306、p.309、p.322 与 p.338 对应同一索引人物项。p.308 全名与其建筑师、书籍插图者身份提供核心锚点；其余章节与注释中姓氏的用法沿同一 Smith、Pasquali、Gallacini 语境出现。{index} {notes} {p306} {p308} {p322} {p338}

## 关系与证据

### 外部身份记录

- **Treccani DBI：** {treccani}；以 Antonio Visentini 立目，记威尼斯出生及去世日期，并说明其专业身份和与 Joseph Smith 的工作语境。
- **Catalogo Generale dei Beni Culturali：** {iccd}；记录 Visentini Antonio（1688–1782）及相关作品目录项。
- **Gallerie dell’Accademia di Venezia：** {gallerie}；作品目录以 Antonio Maria Visentini 署名并记 Venice, 1688–1782。

### 关系记录

当前没有登记正式关系。涉及 {CANDIDATE} 的14条 S2 关系候选留待 S6 逐条审查；包括 Smith、Poleni、Lodoli、Pasquali、Gallacini相关语境。p.322 的 Lodoli 接触说法保留其推测性质，p.309 的“his palace”所指保持未决。本卡仅完成 S3 身份决定与 S4 KU 登记，未开展 S5 补足。
"""


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    assert CARD_REL not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def contains_candidate(value, candidate_id: str) -> bool:
    if isinstance(value, dict):
        return any(contains_candidate(item, candidate_id) for item in value.values())
    if isinstance(value, list):
        return any(contains_candidate(item, candidate_id) for item in value)
    return value == candidate_id


def normalize(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Antonio Visentini S3 group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    manifest_fields, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate = candidate_by_id[CANDIDATE]
    target = next(
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Visentini, Antonio"
    assert candidate.get("index_entry_id") == "UVWXYZ.csv#119"
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    aliases = {"antonio visentini", "visentini, antonio", "antonio maria visentini"}
    assert not any(
        row.get("type") == "person"
        and (
            row.get("canonical_name", "").casefold() in aliases
            or row.get("name_en", "").casefold() in aliases
        )
        for row in manifest
    ), "same-identity person KU already exists in manifest"
    assert not any(
        row.get("candidate_id") == CANDIDATE and row.get("external_source")
        for row in alignments
    ), "external identity record already exists for candidate"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    for item in BOOK_SOURCES:
        normalized_source = normalize((ROOT / item["source_file"]).read_text(encoding="utf-8-sig"))
        for _, quote in item["quotes"]:
            assert normalize(quote) in normalized_source, (item["source_file"], quote)
    _, index_rows = sync.read_csv(ROOT / "02-sources/03-Index/03-2-Index-CSV/UVWXYZ.csv")
    index_row = index_rows[int(candidate["index_entry_id"].split("#")[1])]
    assert index_row.get("Main Entry") == candidate["canonical_name"]
    assert index_row.get("Page Numbers") == "301n, 306, 309, 322, 338"

    statements = [
        json.loads(line)
        for line in STATEMENTS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    related = [row for row in statements if contains_candidate(row, CANDIDATE)]
    relation_count = sum(
        row.get("qualifiers", {}).get("relation_candidate") is True
        for row in related
    )
    assert len(related) == 20 and relation_count == 14, (len(related), relation_count)

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    previous_note = planned_target.get("resolution_note", "")
    prior_status = "No external identity source was accessed; KU assignment remains for S4."
    assert prior_status in previous_note
    previous_note = previous_note.replace(
        prior_status,
        "Prior S3 record (2026-10-15): no external identity source was accessed at that time; "
        "the KU assignment then remained pending for S4.",
        1,
    )
    external_note = (
        f"S3 identity review (2026-10-16): Treccani DBI, Elisabetta Molteni, "
        f"VISENTINI, Antonio, vol. 99 (2020), {TRECCANI_URL}, identifies Antonio Visentini, "
        "born in Venice on 1688-11-21 and deceased there on 1782-06-26, and describes him as "
        "architect, painter, engraver, graphic designer, and author on architecture and perspective. "
        "It discusses his professional connection with Joseph Smith, his illustration work, and his "
        "continuation of Gallaccini's architectural criticism. Catalogo Generale dei Beni Culturali "
        f"agent record ({ICCD_URL}) lists Visentini Antonio, 1688/1782; Gallerie dell'Accademia "
        f"({GALLERIE_URL}) uses Antonio Maria Visentini with the same Venice and 1688–1782 dates. "
        "These independent name, date, role, and Smith/Gallaccini-context anchors support the one "
        "source-local person group. The p.309 pronoun 'his palace' and p.322 tentative Lodoli-contact "
        "claim remain unresolved and are not converted into formal relations. No same-identity "
        "person KU was found in the current manifest."
    )
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = "S3-full-book-2026-10-16"
    planned_target["resolution_note"] = (
        previous_note + "; " + external_note
        + f" S4 registration: mapped {GROUP} to {KU_ID}."
    )

    used_alignment_ids = {
        int(match.group(1))
        for row in planned_alignment
        if (match := re.fullmatch(r"aln-(\d+)", row.get("alignment_id", "")))
    }
    next_id = max(used_alignment_ids, default=0) + 1
    authority_rows = [
        {
            "alignment_id": f"aln-{next_id:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Treccani DBI",
            "external_id": TRECCANI_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: the DBI entry names Antonio Visentini, born in Venice on 1688-11-21 "
                "and deceased there on 1782-06-26; it describes his professional roles, Smith context, "
                "book illustration, and Gallaccini-related architectural writing."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 1:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Catalogo Generale dei Beni Culturali (ICCD)",
            "external_id": ICCD_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: the national cultural heritage catalogue has an artist authority "
                "record Visentini Antonio, 1688/1782, with linked work records."
            ),
        },
        {
            "alignment_id": f"aln-{next_id + 2:04d}",
            "candidate_id": CANDIDATE,
            "ku_id": KU_ID,
            "external_source": "Gallerie dell'Accademia di Venezia",
            "external_id": GALLERIE_URL,
            "decision": "same",
            "accessed_date": DATE,
            "process_ref": "S3-full-book-2026-10-16",
            "legacy_ku_id": "",
            "resolution_note": (
                "Identity only: the museum catalogue names Antonio Maria Visentini and gives "
                "Venice, 1688–1782, matching Treccani's Antonio Visentini."
            ),
        },
    ]
    planned_alignment.extend(authority_rows)

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    external_count = sum(bool(row.get("external_source")) for row in planned_alignment)
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(planned_manifest),
    )
    next_result, count_updates = re.subn(
        r"\d+(?=条外部身份记录单独保留)",
        str(external_count),
        next_result,
        count=1,
    )
    assert count_updates == 1, "could not refresh external identity record count"
    marker = "。各组来源、身份边界和映射更正见[过程记录]"
    assert next_result.count(marker) == 1
    result_insert = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[安东尼奥·维森蒂尼人物卡]"
        "(../units/persons/antonio-visentini.md)，14条关系候选留待 S6" + marker
    )
    next_result = next_result.replace(marker, result_insert, 1)

    note = (
        f"\n### S3-S4 person：{NAME_EN} 跨章身份组裁决与登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；索引 UVWXYZ.csv#119 以 Visentini, Antonio 列出 p.301 注释、"
        "第10章 pp.306、309、322 及第13章 p.338。第10章 p.308 正文明确全名 Antonio Visentini，"
        "称其长期为 Joseph Smith 担任建筑师与书籍插图者；同章 p.306、p.309及第13章 p.338 的姓氏形式沿用这一语境。"
        f"Treccani DBI（Elisabetta Molteni, vol. 99, 2020; {TRECCANI_URL}）记其1688年11月21日生于威尼斯、"
        "1782年6月26日卒于威尼斯，并列建筑师、画家、雕刻家、图形设计者及建筑/透视论著作者身份，讨论其与 Smith 的工作往来、"
        "书籍插图及 Gallacini 论著。意大利文化遗产总目录（ICCD）记录 Visentini Antonio（1688/1782）；"
        "威尼斯学院美术馆目录使用 Antonio Maria Visentini，并给出 Venice, 1688–1782。姓名、日期、职业和书内 Smith/Gallacini 语境支持同一身份组。"
        "未发现同身份既有 person KU。p.309 的 his palace 所指未裁定；p.322 对 Lodoli 接触关系的说法保留推测性质，不由身份登记转成正式关系。中文名为项目工作音译。\n"
        "- 涉及该候选的20条 S2 陈述中14条标为关系候选，留待 S6 逐条审查；没有登记正式关系，也未开展 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"### S3-S4 person：{NAME_EN} 跨章身份组裁决与登记（{DATE}）" not in knowledge_text
    next_knowledge = knowledge_text + note
    next_accepted = insert_accepted(accepted)

    output = {
        ALIGNMENT: None,
        MANIFEST: None,
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        RESULT: next_result,
        CARD: card,
    }
    for path, headers, rows in (
        (ALIGNMENT, alignment_fields, planned_alignment),
        (MANIFEST, manifest_fields, planned_manifest),
    ):
        buffer = StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        output[path] = buffer.getvalue()

    protected_paths = [path for path in output if path != CARD]
    assert all(
        not path.with_name(path.name + BACKUP_SUFFIX).exists()
        for path in protected_paths
    )
    if args.dry_run:
        for path, updated in output.items():
            if path == CARD:
                print(f"--- create {CARD_REL} ({len(updated)} characters)")
                print("\n".join(updated.splitlines()[:22]))
                continue
            current = path.read_text(encoding="utf-8-sig")
            diff = difflib.unified_diff(
                current.splitlines(keepends=True),
                updated.splitlines(keepends=True),
                fromfile=str(path.relative_to(ROOT)),
                tofile=str(path.relative_to(ROOT)) + " (updated)",
                n=2,
            )
            print("".join(diff), end="")
        print(
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members=1; "
            f"book_and_authority_sources={len(BOOK_SOURCES) + 3}; related_statements={len(related)}; "
            f"relation_candidates_pending={relation_count}; external_records={external_count}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    backups: list[tuple[Path, Path]] = []
    for path in protected_paths:
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        shutil.copy2(path, backup)
        backups.append((path, backup))
    try:
        for path, updated in output.items():
            path.write_text(updated, encoding="utf-8-sig", newline="\n")
    except Exception:
        for path, backup in backups:
            shutil.copy2(backup, path)
        if CARD.exists():
            CARD.unlink()
        raise
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; relation_candidates_pending={relation_count}; "
        f"external_records={external_count}; registered={totals['registered_groups']}/"
        f"{totals['registered_members']}; pending={totals['pending_groups']}/"
        f"{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"recovery_backups={len(backups)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
