from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import register_s4_archive_memmo_query_sheet_20261017 as archive_sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
TABLES = ROOT / "04-knowledge" / "tables"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_FILE = "02-sources/02-Markdown/13_CHP-13_intro.md"
INDEX_ROOT = "02-sources/03-Index/03-2-Index-CSV"
ANCHOR = "s4-archive-chiesa-gesu-cristo-vendicata-cluster-20261017"

BOOK_GROUP = "archive-group-chiesa-gesu-cristo-vendicata-text"
BOOK_MEMBERS = ("cand-2718", "cand-9993")
AUTHOR_GROUP = "new-person:antonio-da-venezia-1f888bfe23"
AUTHOR_MEMBERS = ("cand-10148",)
PUBLISHER_GROUP = "new-person:battista-giovanni-recurti-abdf8eeb09"
PUBLISHER_MEMBERS = ("cand-2111",)
FRONTISPIECE_GROUP = "workgrp-eecaa82c32cc90"
FRONTISPIECE_MEMBERS = ("cand-10149",)

BOOK_KU = "units/archives/la-chiesa-di-gesu-cristo-vendicata"
BOOK_CARD = "04-knowledge/units/archives/la-chiesa-di-gesu-cristo-vendicata.md"
BOOK_ZH = "《耶稣基督教会在其标志与教义上的辩护》"
BOOK_EN = "The Church of Jesus Christ Vindicated in Its Signs and Dogmas"

AUTHOR_KU = "units/persons/antonio-da-venezia"
AUTHOR_CARD = "04-knowledge/units/persons/antonio-da-venezia.md"
AUTHOR_ZH = "安东尼奥·达·威尼斯"
AUTHOR_EN = "Antonio da Venezia"

PUBLISHER_KU = "units/persons/giovanni-battista-recurti"
PUBLISHER_CARD = "04-knowledge/units/persons/giovanni-battista-recurti.md"
PUBLISHER_ZH = "乔瓦尼·巴蒂斯塔·雷库尔蒂"
PUBLISHER_EN = "Giovanni Battista Recurti"

WORK_KU = "units/works/religion-trampling-on-heresy-book-frontispiece"
WORK_CARD = "04-knowledge/units/works/religion-trampling-on-heresy-book-frontispiece.md"
WORK_ZH = "《宗教践踏异端》"
WORK_EN = "Religion trampling on Heresy"

MEMBERS_BY_GROUP = {
    BOOK_GROUP: BOOK_MEMBERS,
    AUTHOR_GROUP: AUTHOR_MEMBERS,
    PUBLISHER_GROUP: PUBLISHER_MEMBERS,
    FRONTISPIECE_GROUP: FRONTISPIECE_MEMBERS,
}
KU_BY_GROUP = {
    BOOK_GROUP: (BOOK_KU, "archive", BOOK_ZH, BOOK_EN, BOOK_CARD),
    AUTHOR_GROUP: (AUTHOR_KU, "person", AUTHOR_ZH, AUTHOR_EN, AUTHOR_CARD),
    PUBLISHER_GROUP: (PUBLISHER_KU, "person", PUBLISHER_ZH, PUBLISHER_EN, PUBLISHER_CARD),
    FRONTISPIECE_GROUP: (WORK_KU, "work", WORK_ZH, WORK_EN, WORK_CARD),
}

RELATION_IDS = {
    "st-chp13-p335-albrizzi-close-relations-with-recurti",
    "st-chp13-p335-piazzetta-frontispiece-before-albrizzi-enterprise",
    "st-chp13-p335-recurti-published-devotional-book",
    "st-chp13-p335-note2-book-frontispiece",
    "st-chp13-p335-note2-piazzetta-drew-design",
    "st-chp13-p335-note2-pitteri-engraved-design",
}

BODY_QUOTE = (
    "twelve years before their first enterprise together the artist had already produced "
    "a frontispiece for a devotional book published by Recurti"
)
NOTE_QUOTE = (
    "2 The book was Padre Antonio da Venezia: La Chiesa di Gesù Cristo vendicata ne' suoi "
    "contrasegni e ne' suoi dogmi, for which Piazzetta drew Religion trampling on Heresy "
    "engraved by Pitteri—see Gallo, 1948, p. 176, note 4."
)
INDEX_BOOK_ROW = '"Venezia, Padre Antonio da",,,,'
INDEX_PUBLISHER_ROW = '"Recurti, Giovanni Battista",,,,335'


def source_row(location: str, summary: str, quote: str, span: str, file: str = SOURCE_FILE) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": file,
            "source_span": span,
        },
    }


def make_card(title_zh: str, name_en: str, kind: str, sources: list[dict], body: str, sub_type: str = "") -> str:
    frontmatter = {
        "title": f"{title_zh}（{name_en}）",
        "name_en": name_en,
        "type": kind,
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    if sub_type:
        frontmatter["sub_type"] = sub_type
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{fm}---\n\n{body.strip()}\n"


def cards() -> dict[str, str]:
    body_location = "第13章，印刷页335，正文第33行；相对时间所指未换算为绝对年份。"
    note_location = "第13章，印刷页335注2，第193行；所引 Gallo 1948 年版本及页码未独立查阅。"
    body_summary = (
        "Haskell 称，在与 Albrizzi 首次合作十二年前，Piazzetta 已为 Recurti 出版的一部宗教书籍绘制卷首插图；"
        "此处仅保留相对时间，不推算绝对年份。"
    )
    note_summary = (
        "Haskell 注释给出书名及 Padre Antonio da Venezia 的题名前置署名形式，并称 Piazzetta 绘制题为 "
        "Religion trampling on Heresy 的卷首图像、由 Pitteri 刻版；本书及所引 Gallo 段落未独立查阅。"
    )
    body_source = source_row(body_location, body_summary, BODY_QUOTE, "line 33; print p. 335")
    note_source = source_row(note_location, note_summary, NOTE_QUOTE, "line 193; print p. 335, note 2")
    index_book_source = source_row(
        "书后索引 UVWXYZ.csv#54；印刷索引页472。",
        "索引主项以 Venezia, Padre Antonio da 形式列名；子目 OCR 与页码异文的校正依据另记于 S3 过程。",
        INDEX_BOOK_ROW,
        "UVWXYZ.csv#54; print index p. 472",
        f"{INDEX_ROOT}/UVWXYZ.csv",
    )
    index_publisher_source = source_row(
        "书后索引 Q-R.csv#38；条目页码335。",
        "索引以 Recurti, Giovanni Battista 为主项，并将第13章 p.335 列为定位页。",
        INDEX_PUBLISHER_ROW,
        "Q-R.csv#38; print index p. 465",
        f"{INDEX_ROOT}/Q-R.csv",
    )

    book_body = f"""## 内容

### 描述

**中文：** 本卡登记哈斯克尔第13章注2所列的书籍文本。中文题名为按意大利语题名形成的工作译名，不声称是正式中译。注释题名前置形式为 [Padre Antonio da Venezia](../persons/antonio-da-venezia.md)；此卡只记录哈斯克尔的题名／责任者形式，人物身份与确切作者归属未作外部核验。正文称该书由 [Giovanni Battista Recurti](../persons/giovanni-battista-recurti.md) 出版；具体版次、出版地、出版年及实物均未确认。{body_link('第13章 p.335', SOURCE_FILE, 'L33')}

**English:** This unit records the book text named in Haskell’s Chapter 13, note 2. The Chinese title is a working translation of the Italian title, not an established published translation. The prefixed form [Padre Antonio da Venezia](../persons/antonio-da-venezia.md) is recorded as Haskell’s title/responsibility form; the person’s external identity and precise authorship have not been verified. The main text says the book was published by [Giovanni Battista Recurti](../persons/giovanni-battista-recurti.md). No exact edition, place or year of publication, or physical copy has been confirmed. {body_link('Chapter 13, p. 335', SOURCE_FILE, 'L193')}

### 题名与书目信息

| 字段 | 值 | 证据 |
|---|---|---|
| 中文工作题名 | {BOOK_ZH} | S2（第13章 p.335 注2；工作译名） |
| 英文工作译名 | {BOOK_EN} | S2（据意大利语题名直译） |
| 原题名 | La Chiesa di Gesù Cristo vendicata ne' suoi contrasegni e ne' suoi dogmi | S2（第13章 p.335 注2） |
| 题名前置署名形式 | [Padre Antonio da Venezia](../persons/antonio-da-venezia.md)；哈斯克尔题名形式，作者身份未独立核验 | S2 |
| 文献类型 | devotional book（哈斯克尔称谓） | S1（第13章 p.335 正文） |
| 出版者（哈斯克尔所述） | [Giovanni Battista Recurti](../persons/giovanni-battista-recurti.md) | S1（第13章 p.335 正文） |

### 身份边界

S3 组 `{BOOK_GROUP}` 将索引子目 cand-2718 与第13章注2完整题名 cand-9993 对齐为同一书籍文本层级。此 KU 不代表某一已确认刊本或具体版本；题名中的 Padre Antonio da Venezia 与出版者 Recurti 各有独立 person KU，不与本书合并。注2所述卷首图像另登记为 work KU。书籍与卷首图像的身份登记不裁决正式关系。

## 关系与证据

当前没有登记在 `relations.csv` 中的正式关系。直接 S2 关系候选 `st-chp13-p335-piazzetta-frontispiece-before-albrizzi-enterprise`、`st-chp13-p335-recurti-published-devotional-book`、`st-chp13-p335-note2-book-frontispiece` 留待 S6；所引 Gallo 1948 年文本及被引书籍均未独立查阅。"""
    book_body = book_body.replace("{BOOK_GROUP}", BOOK_GROUP)
    book = make_card(BOOK_ZH, BOOK_EN, "archive", [body_source, note_source], book_body, "devotional book")

    author_body = f"""## 内容

### 描述

**中文：** 本卡仅记录哈斯克尔第13章注2及书后索引中的人物称名形式 Antonio da Venezia / Padre Antonio da Venezia。此姓名是该书题名前置署名形式；本轮未找到可唯一对应的既有 KU，也未查阅外部人物规范记录。除该名称及其书内题名语境外，不补写生卒、教职、地点或其他生平事实。此候选与书籍 archive KU 分开登记，不据此提前建立正式作者关系。

**English:** This unit records only the person-name forms Antonio da Venezia and Padre Antonio da Venezia in Haskell’s Chapter 13, note 2, and the book index. The name occurs as a prefixed responsibility form for the book. No unique existing KU or external authority record was identified in this pass. No dates, office, location, or other biographical facts are added. The person candidate is registered separately from the book archive KU; no formal authorship relation is asserted here.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 原文称名 | Antonio da Venezia | S1（第13章 p.335 注2；索引 UVWXYZ.csv#54） |
| 题名前置形式 | Padre Antonio da Venezia | S1（第13章 p.335 注2） |
| 称谓限定 | Padre 是书内称名的一部分；未据此补写教职或外部身份 | S1 |

## 关系与证据

本轮没有可裁决为正式边的 S2 关系候选。该人物名在书目题名中出现；其与[相关书籍文本](../archives/la-chiesa-di-gesu-cristo-vendicata.md)的关系仍按来源用语保留，不扩展为外部确认的著作权事实。"""
    author = make_card(AUTHOR_ZH, AUTHOR_EN, "person", [note_source, index_book_source], author_body)

    publisher_body = f"""## 内容

### 描述

**中文：** 本卡登记书后索引 Q-R.csv#38 所列的 Giovanni Battista Recurti。Haskell 第13章 p.335 称 Recurti 出版了题为 devotional book 的书籍，并称其与 Albrizzi 保持密切往来；这些是 Haskell 对特定书籍及关系的叙述。本轮未查阅外部人物规范记录或出版档案，不补写生卒、籍贯、任职年代或完整出版目录。

**English:** This unit records Giovanni Battista Recurti as named in index entry Q-R.csv#38. On Chapter 13, p.335, Haskell says Recurti published a devotional book and maintained close relations with Albrizzi; these remain Haskell’s statements about a particular book and relationship. No external person authority record or publishing archive was consulted, and no dates, birthplace, career span, or complete publication list is added.

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
| 全名（书后索引形式） | Giovanni Battista Recurti | S1（Q-R.csv#38） |
| 本章简称 | Recurti | S2（第13章 p.335 正文） |

### 本章身份与活动

| 字段 | 值 | 证据 |
|---|---|---|
| 特定出版活动 | Haskell 称其为一部宗教书籍的出版者；该书的具体版本未独立核验 | S2（第13章 p.335 正文） |

## 关系与证据

尚无正式关系写入 `relations.csv`。`st-chp13-p335-albrizzi-close-relations-with-recurti` 与 `st-chp13-p335-recurti-published-devotional-book` 两条直接 S2 关系候选留待 S6；另有非关系陈述 `st-chp13-p335-note2-recurti-citation`，不升级为关系。"""
    publisher = make_card(PUBLISHER_ZH, PUBLISHER_EN, "person", [index_publisher_source, body_source], publisher_body)

    work_body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔注释所称 *Religion trampling on Heresy* 卷首图像／设计。注释称 Giovanni Battista Piazzetta 绘制其设计、Marco Pitteri 刻版，并将其定位为 [La Chiesa di Gesù Cristo vendicata](../archives/la-chiesa-di-gesu-cristo-vendicata.md) 的卷首图像。当前身份粒度为注释中具名的图像设计，不指某一版次中的具体印张或一张已确认存世的原稿。该书及所引 Gallo 1948 年页段均未独立查阅。

**English:** This unit records the frontispiece image/design called *Religion trampling on Heresy* in Haskell’s note. The note says Giovanni Battista Piazzetta drew the design and Marco Pitteri engraved it, and places it as a frontispiece for [La Chiesa di Gesù Cristo vendicata](../archives/la-chiesa-di-gesu-cristo-vendicata.md). The identity is the named image/design in the note, not a particular impression in a verified edition or a confirmed surviving drawing. Neither the book nor the cited Gallo passage from 1948 was independently consulted.

### 作品信息

| 字段 | 值 | 证据 |
|---|---|---|
| 书内题名 | Religion trampling on Heresy | S1（第13章 p.335 注2） |
| 作品类型 | 书籍卷首图像／设计（按哈斯克尔注释） | S1 |
| 创作者角色 | Giovanni Battista [Piazzetta](../persons/piazzetta.md) 绘制设计 | S1（第13章 p.335 注2） |
| 创作者角色 | Marco [Pitteri](../persons/marco-pitteri.md) 刻版 | S1（第13章 p.335 注2） |
| 关联出版物 | [《La Chiesa di Gesù Cristo vendicata》](../archives/la-chiesa-di-gesu-cristo-vendicata.md)；Haskell 所述卷首图像所属文本 | S1 |

### 版本与存世

Haskell 的注释没有给出确切版次、印张馆藏或原稿存世信息。本卡不由“drawn”与“engraved”推定同一载体或当前存世状态。

## 关系与证据

当前没有正式关系写入 `relations.csv`。`st-chp13-p335-note2-book-frontispiece`、`st-chp13-p335-note2-piazzetta-drew-design` 与 `st-chp13-p335-note2-pitteri-engraved-design` 留待 S6，逐条核对端点、方向和证据。"""
    work = make_card(WORK_ZH, WORK_EN, "work", [note_source], work_body, "book frontispiece image/design")

    return {
        BOOK_CARD: book,
        AUTHOR_CARD: author,
        PUBLISHER_CARD: publisher,
        WORK_CARD: work,
    }


def body_link(label: str, source_file: str, line: str) -> str:
    return f"[{label}](../../../{source_file})（{line}）"


def add_accepted_paths(text: str, paths: list[str]) -> str:
    lines = text.splitlines()
    for path in sorted(paths):
        if f"- {path}" in lines:
            raise AssertionError(f"accepted.yml already includes {path}")
        insert_at = next(
            (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > path),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {path}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the p.335 book/frontispiece/person identity cluster in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT / "scripts"))
    import build_field_facts

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(alignment_by_id) == len(candidate_by_id)

    for group, members in MEMBERS_BY_GROUP.items():
        rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == group
        ]
        assert {row["candidate_id"] for row in rows} == set(members), (group, rows)
        for cid in members:
            assert candidate_by_id[cid]["suggested_type"] == KU_BY_GROUP[group][1]
            assert alignment_by_id[cid]["decision"] == "new" and not alignment_by_id[cid].get("ku_id")

    planned_cards = cards()
    assert set(planned_cards) == {item[4] for item in KU_BY_GROUP.values()}
    for card_rel, card in planned_cards.items():
        assert not (ROOT / card_rel).exists(), f"card already exists: {card_rel}"
        assert card_rel not in accepted
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict), f"invalid frontmatter: {card_rel}"

    existing_names = {
        (row.get("type", ""), (row.get("name_en") or "").casefold(), row.get("ku_id", ""))
        for row in manifest
    }
    for group, (ku_id, kind, name_zh, name_en, card_rel) in KU_BY_GROUP.items():
        assert not any(row.get("ku_id") == ku_id or row.get("card_path") == card_rel for row in manifest)
        assert (kind, name_en.casefold(), ku_id) not in existing_names
        assert not any(row.get("type") == kind and (row.get("name_en") or "").casefold() == name_en.casefold() for row in manifest)

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for quote in (BODY_QUOTE, NOTE_QUOTE):
        assert " ".join(quote.split()) in source_text, f"source quote missing: {quote}"
    for relative, quote in (
        (f"{INDEX_ROOT}/UVWXYZ.csv", INDEX_BOOK_ROW),
        (f"{INDEX_ROOT}/Q-R.csv", INDEX_PUBLISHER_ROW),
    ):
        text = " ".join((ROOT / relative).read_text(encoding="utf-8-sig").split())
        assert " ".join(quote.split()) in text, f"index row changed: {relative}"

    statements = sync.load_statements()
    new_ids = set(BOOK_MEMBERS + AUTHOR_MEMBERS + PUBLISHER_MEMBERS + FRONTISPIECE_MEMBERS)
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in new_ids or row.get("object_candidate_id") in new_ids
    ]
    relations = {
        row["statement_id"] for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert relations == RELATION_IDS, (relations, RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for group, members in MEMBERS_BY_GROUP.items():
        ku_id = KU_BY_GROUP[group][0]
        for cid in members:
            planned_by_id[cid]["ku_id"] = ku_id
            planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {group} to {ku_id}."

    planned_manifest = list(manifest)
    for ku_id, kind, name_zh, name_en, card_rel in KU_BY_GROUP.values():
        planned_manifest.append({
            "ku_id": ku_id,
            "type": kind,
            "canonical_name": name_zh,
            "name_en": name_en,
            "source_task": TASK,
            "card_path": card_rel,
        })

    with tempfile.TemporaryDirectory(prefix="pnp-s4-chiesa-preview-") as temp_dir:
        temp_root = Path(temp_dir)
        for card_rel, card in planned_cards.items():
            temp_card = temp_root / card_rel
            temp_card.parent.mkdir(parents=True, exist_ok=True)
            temp_card.write_text(card, encoding="utf-8-sig", newline="\n")
        original_base = build_field_facts.BASE
        build_field_facts.BASE = temp_root
        try:
            fact_rows, source_registry, warnings, cards_with_tables = build_field_facts.extract_records(planned_manifest[-4:])
        finally:
            build_field_facts.BASE = original_base
    assert not warnings, warnings
    assert cards_with_tables == 4
    assert fact_rows and all(row["evidence_status"] == "source_backed" for row in fact_rows)
    assert all(row["source_ids"] == ["haskell-1980-rev-ed"] for row in fact_rows)
    assert set(source_registry) <= {"haskell-1980-rev-ed"}
    build_field_facts.assign_ids(fact_rows, TABLES / "enrichment.jsonl")
    old_facts = [
        json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assert not any(row.get("ku_id") in {item[0] for item in KU_BY_GROUP.values()} for row in old_facts)
    planned_facts = old_facts + fact_rows
    assert len({row["enrichment_id"] for row in planned_facts}) == len(planned_facts)
    unverified = sum(row.get("evidence_status") == "unverified" for row in planned_facts)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    enrichment_pattern = re.compile(r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$", re.M)
    result_text, n = enrichment_pattern.subn(
        f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_facts))}条，其中{sync.fmt(unverified)}条 unverified |",
        result_text,
        count=1,
    )
    assert n == 1, "could not update enrichment artifact count"

    process_text = archive_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    process_append = (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### S3/S4 archive/person/work：第13章 p.335 书籍与卷首图像身份簇登记（{DATE}）\n\n"
        f"- archive 组 `{BOOK_GROUP}`：cand-2718（UVWXYZ.csv#54，p.335n）与 cand-9993（第13章 p.335 注2完整题名）映射至[《耶稣基督教会在其标志与教义上的辩护》](../../../{BOOK_CARD})。索引主项／子目与注2题名相合；只确认书籍文本层级，未确认具体版次、出版地或出版年。索引原错误页码和 OCR `3^5n` 的校正保留在候选与原始索引，不改写来源。\n"
        f"- person 组 `{AUTHOR_GROUP}`（cand-10148）登记为[Antonio da Venezia](../../../{AUTHOR_CARD})，仅表示 Haskell 题名前置署名形式；未补传记、教职或外部身份，也不建立正式著作权边。person 组 `{PUBLISHER_GROUP}`（cand-2111）登记为[Giovanni Battista Recurti](../../../{PUBLISHER_CARD})，以索引全名及本章 Recurti 称名相互定位；出版者与 Albrizzi 关系仍是 Haskell 的书内陈述。\n"
        f"- work 组 `{FRONTISPIECE_GROUP}`（cand-10149）登记为[《宗教践踏异端》](../../../{WORK_CARD})，粒度为注释所称图像／设计，不指明具体版次印张或存世原稿。Piazzetta 绘制、Pitteri 刻版按 Haskell 注释保留。\n"
        f"- 六条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）全部留待 S6；端点已映射至新 KU 或既有 KU，但没有新增正式关系。`st-chp13-p335-note2-recurti-citation` 的 `relation_candidate=false` 状态不变。Gallo 1948 p.176 n.4 与被引书籍均未独立查阅。\n"
        f"- 本簇四个 S3 新身份组登记为四个不同 KU，五条候选映射；S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条，KU 总数{sync.fmt(len(planned_manifest))}，结构化字段{sync.fmt(len(planned_facts))}条。"
    )
    process_text = process_text.rstrip() + process_append + "\n"
    planned_accepted = add_accepted_paths(accepted, [item[4] for item in KU_BY_GROUP.values()])

    if args.dry_run:
        print(
            f"dry-run passed: groups={len(MEMBERS_BY_GROUP)}; new_KUs={len(KU_BY_GROUP)}; "
            f"candidate_mappings={sum(map(len, MEMBERS_BY_GROUP.values()))}; new_field_rows={len(fact_rows)}; "
            f"direct_relation_candidates={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; enrichment={len(old_facts)}->{len(planned_facts)}"
        )
        for row in fact_rows:
            print(f"  {row['ku_id']} | {row['field']} | {row['value']} | {row['evidence_status']} | {row['source_ref']}")
        return 0

    for card_rel, card in planned_cards.items():
        (ROOT / card_rel).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / card_rel).write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    build_field_facts.write_jsonl(TABLES / "enrichment.jsonl", planned_facts)
    ACCEPTED.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: groups={len(MEMBERS_BY_GROUP)}; new_KUs={len(KU_BY_GROUP)}; "
        f"candidate_mappings={sum(map(len, MEMBERS_BY_GROUP.values()))}; new_field_rows={len(fact_rows)}; "
        f"direct_relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"enrichment={len(old_facts)}->{len(planned_facts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
