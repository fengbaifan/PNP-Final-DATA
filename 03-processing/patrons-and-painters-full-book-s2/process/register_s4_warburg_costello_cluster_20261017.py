from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
UCP_HISTORY = "https://www.journals.uchicago.edu/journals/jwci/history"
UCP_1950_TOC = "https://www.journals.uchicago.edu/toc/jwci/1950/13/3-4"
JSTOR_1950_TOC = "https://www.jstor.org/stable/i230411"
ARTICLE_DOI = "https://doi.org/10.2307/750214"

PERSON_CANDIDATE = "cand-7016"
PERSON_GROUP = "new-person:costello-jane-costello-jane-miss-c6062f1806"
PERSON_KU = "units/persons/jane-costello"
PERSON_ZH = "简·科斯特洛"
PERSON_EN = "Jane Costello"
PERSON_CARD = f"04-knowledge/{PERSON_KU}.md"
PERSON_ANCHOR = "s4-person-jane-costello-20261017"
PERSON_PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{PERSON_ANCHOR}"

JOURNAL_CANDIDATE = "cand-6004"
JOURNAL_GROUP = "archive-group-288e9f99e396"
JOURNAL_KU = "units/archives/journal-warburg-courtauld-institutes"
JOURNAL_ZH = "瓦尔堡与考陶尔德学院学报"
JOURNAL_EN = "Journal of the Warburg and Courtauld Institutes"
JOURNAL_CARD = f"04-knowledge/{JOURNAL_KU}.md"
JOURNAL_ANCHOR = "s4-archive-journal-warburg-courtauld-institutes-20261017"
JOURNAL_PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{JOURNAL_ANCHOR}"

ARTICLE_CANDIDATE = "cand-7017"
ARTICLE_GROUP = "archive-group-4ecb8673d506"
ARTICLE_KU = "units/archives/costello-twelve-pictures-ordered-velasquez-1950"
ARTICLE_ZH = "委拉斯开兹“订购”的十二幅画与瓦尔古阿内拉审判（1950年）"
ARTICLE_EN = 'The Twelve Pictures "Ordered by Velasquez" and the Trial of Valguarnera (1950)'
ARTICLE_CARD = f"04-knowledge/{ARTICLE_KU}.md"
ARTICLE_ANCHOR = "s4-archive-costello-twelve-pictures-1950-20261017"
ARTICLE_PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ARTICLE_ANCHOR}"
ARTICLE_RELATIONS = {
    "st-chp1-secii-p11-n3-cites-costello-p278",
    "st-chp1-secii-p11-n6-cites-costello-p274",
    "st-chp7-p172-n3-cite-costello",
    "st-chp1-secii-l613-n1-cites-costello-p274-275",
}

CHP1_FILE = "02-sources/02-Markdown/01_CHP-1.md"
CHP4_FILE = "02-sources/02-Markdown/04_CHP-4_sec_ii.md"
CHP5_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
CHP7_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
CHP16_FILE = "02-sources/02-Markdown/16_CHP-16_intro.md"
BIB_FILE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"


def insert_accepted(lines: list[str], card_paths: list[str]) -> list[str]:
    units_idx = lines.index("units:")
    claims_idx = next(
        (i for i in range(units_idx + 1, len(lines)) if re.fullmatch(r"[A-Za-z0-9_-]+:", lines[i])),
        len(lines),
    )
    for card_path in sorted(card_paths):
        entry = f"- {card_path}"
        assert entry not in lines
        insert_at = next(
            (i for i in range(units_idx + 1, claims_idx) if lines[i].startswith("- ") and lines[i][2:] > card_path),
            claims_idx,
        )
        lines.insert(insert_at, entry)
        claims_idx += 1
    return lines


def make_person_card() -> str:
    fm = yaml.safe_dump(
        {
            "title": f"{PERSON_ZH}（{PERSON_EN}）",
            "name_en": PERSON_EN,
            "type": "person",
            "evidence_status": "source_backed",
            "sources": [
                {
                    "citation": BOOK_CITATION,
                    "location": "第5章，印刷页131注2；OCR L139",
                    "sentence_summary": "Haskell 提到 Jane Costello 对 Ferrante Carlo 研究所引证据；第7章另引其论文，期刊目录将 Jane Costello 列为该文作者。",
                    "original_quotes": [{"source_span": "line 139; print p.131, note 2", "text": "Miss Jane Costello"}],
                    "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": CHP5_FILE, "source_span": "line 139; print p.131, note 2"},
                },
                {
                    "citation": f"The University of Chicago Press, *Journal of the Warburg and Courtauld Institutes*, vol. 13, no. 3–4 (1950). {UCP_1950_TOC} Accessed 2026-10-17.",
                    "location": "1950年卷期目录，Costello 论文条目",
                    "accessed_date": DATE,
                    "sentence_summary": "期刊目录将 Jane Costello 列为《The Twelve Pictures ‘Ordered by Velasquez’ and the Trial of Valguarnera》的作者；此记录仅支持本项目中的同名作者身份锚点，不补入传记事实。",
                    "original_quotes": [{"source_span": "volume 13, number 3–4, 1950, article entry", "text": "The Twelve Pictures \"Ordered by Velasquez\" and the Trial of Valguarnera; Jane Costello"}],
                },
            ],
            "created": DATE,
            "updated": DATE,
            "process_ref": PERSON_PROCESS_REF,
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    article_link = "[1950年论文](../archives/costello-twelve-pictures-ordered-velasquez-1950.md)"
    body = f"""## 内容

### 描述

**中文：** 本知识元只标识 Haskell 所引1950年论文目录所列作者 Jane Costello。书内提及她对 Ferrante Carlo 研究所引证据，期刊目录将她列为相关论文作者；不据此补充生平或其他同名者事实。中文名为工作音译。

**English:** This unit identifies only the Jane Costello credited as author of the 1950 article cited by Haskell. The book refers to her evidence in the study of Ferrante Carlo, and the journal contents list her as the article's author. No biography or facts about other people with the same name are inferred.

### 名称与身份依据

| 字段 | 值 | 证据 |
|---|---|---|
| 原文姓名 | Jane Costello | S1（Haskell 第5章 p.131 注2）；S2（University of Chicago Press 1950年卷期目录） |
| 本书中的身份线索 | Haskell 提及她对 Ferrante Carlo 研究所引证据；第7章另引其1950年论文 | S1（Haskell 第5章 p.131 注2；第7章 p.172 注3）；S2（期刊目录） |

## 关系与证据

### 关系记录

目前没有登记在 relations.csv 中的正式关系。论文作者身份有期刊目录支持，论文卡为 {article_link}；尚未将作者关系写入正式关系表。候选 cand-3509 的单姓 Costello 仍为独立待决对象，本卡不与其合并。逐组裁决见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{PERSON_ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def make_journal_card() -> str:
    fm = yaml.safe_dump(
        {
            "title": f"《{JOURNAL_ZH}》（{JOURNAL_EN}）",
            "name_en": JOURNAL_EN,
            "type": "archive",
            "sub_type": "scholarly journal",
            "evidence_status": "source_backed",
            "sources": [
                {
                    "citation": BOOK_CITATION,
                    "location": "第4章，印刷页118注1；OCR L303；第16章 pp.374–376 的注释引用",
                    "sentence_summary": "Haskell 第4章脚注以 Journal of the Warburg Institute 指称一篇1944年 Blunt 论文；第16章多条脚注以同一简称引用1960年的期刊文章。本卡将该简称记录为期刊的历史题名，不将文章与期刊合并。",
                    "original_quotes": [{"source_span": "line 303; print p.118, note 1", "text": "Blunt in Journal of Warburg Institute, 1944, pp. 165 ff."}],
                    "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": CHP4_FILE, "source_span": "line 303; print p.118, note 1"},
                },
                {
                    "citation": f"The University of Chicago Press, *Journal of the Warburg and Courtauld Institutes: History*. {UCP_HISTORY} Accessed 2026-10-17.",
                    "location": "History of the Journal; Origins and Association with the Courtauld",
                    "accessed_date": DATE,
                    "sentence_summary": "出版社记载期刊于1937–1938年以 Journal of the Warburg Institute 名称出版，并称与 Courtauld 的关联正式体现在1940年第三卷的刊名中。该连续刊名沿革支持同一 serial identity 的历史题名映射。",
                    "original_quotes": [{"source_span": "Association with the Courtauld section", "text": "formalised in the title to volume III, for 1940"}],
                },
                {
                    "citation": f"The University of Chicago Press, *Journal of the Warburg and Courtauld Institutes*, vol. 13, no. 3–4 (1950). {UCP_1950_TOC} Accessed 2026-10-17.",
                    "location": "1950年卷期目录",
                    "accessed_date": DATE,
                    "sentence_summary": "出版社以 Journal of the Warburg and Courtauld Institutes 为该刊现行刊名列出1950年第13卷第3–4期。",
                    "original_quotes": [{"source_span": "volume 13, number 3–4, 1950", "text": "Journal of the Warburg and Courtauld Institutes"}],
                },
            ],
            "created": DATE,
            "updated": DATE,
            "process_ref": JOURNAL_PROCESS_REF,
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    article_link = "[1950年 Costello 论文](costello-twelve-pictures-ordered-velasquez-1950.md)"
    body = f"""## 内容

### 描述

**中文：** 1937年创刊的学术期刊连续出版物。出版社记载其早期题名为 *Journal of the Warburg Institute*，与 Courtauld 的合作正式纳入1940年第三卷刊名后，使用 *Journal of the Warburg and Courtauld Institutes*。两种题名作为同一连续期刊的历史与后续刊名保留；中文刊名为工作译名，不声称为正式译名。

**English:** A scholarly serial founded in 1937. The publisher records its early title as *Journal of the Warburg Institute* and the formal adoption of the Courtauld association in the title of volume III, for 1940. The two titles are retained as successive titles of the continuing journal.

### 名称与沿革

| 字段 | 值 | 证据 |
|---|---|---|
| 后续刊名 | {JOURNAL_EN} | S2（University of Chicago Press 期刊史）；S3（1950年第13卷目录） |
| 早期刊名 | Journal of the Warburg Institute | S2（University of Chicago Press 期刊史） |
| 刊名沿革 | 第III卷（1940）正式体现与 Courtauld 的关联 | S2（University of Chicago Press 期刊史） |
| 书内简称异文 | Haskell 第4章 p.118 注1写作 Journal of Warburg Institute；未据此另建第二种期刊实体 | S1（Haskell p.118）；S2（出版社期刊史） |

### 本书相关引文

Haskell 在第4章和第16章引述该刊所载文章。此卡只记录期刊身份和可证的题名沿革；论文及其载文事实保持各自 archive 身份。可参看 {article_link}。

## 关系与证据

### 身份与外部链接

- [University of Chicago Press 期刊史]({UCP_HISTORY})：支持旧刊名及1940年起的刊名沿革。
- [1950年第13卷第3–4期目录]({UCP_1950_TOC})：支持后续刊名及该期目录。

### 关系记录

目前没有登记在 relations.csv 中的正式关系。刊物与所载文章的 part_of 关系留待 S6；文章不与期刊合并。逐组裁决见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{JOURNAL_ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def make_article_card() -> str:
    fm = yaml.safe_dump(
        {
            "title": f"《{ARTICLE_ZH}》（{ARTICLE_EN}）",
            "name_en": ARTICLE_EN,
            "type": "archive",
            "sub_type": "journal article",
            "evidence_status": "source_backed",
            "sources": [
                {
                    "citation": BOOK_CITATION,
                    "location": "第7章 p.172 注3；第1章 p.11 注3、注6及 p.15 注1；书目 p.420",
                    "sentence_summary": "Haskell 在第1、7章分别引用 Costello pp.247、274–275、278；第21章书目列出论文题名、作者、期刊、1950年及页码237–284。论文正文与所引页未独立查阅。",
                    "original_quotes": [
                        {"source_span": "line 304; print p.172, note 3", "text": "Costello, p. 247."},
                        {"source_span": "lines 382–383; bibliography print p.420", "text": "Costello, Jane: ‘The twelve pictures “ordered by Velasquez” and the trial of Valguarnera’ in Journal of the Warburg and Courtauld Institutes, 1950, pp. 237-284."},
                    ],
                    "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": BIB_FILE, "source_span": "lines 382–383; bibliography print p.420; see also chapter 1 and chapter 7 notes"},
                },
                {
                    "citation": f"The University of Chicago Press, *Journal of the Warburg and Courtauld Institutes*, vol. 13, no. 3–4 (1950). {UCP_1950_TOC} Accessed 2026-10-17.",
                    "location": "1950年卷期目录，Costello 论文条目",
                    "accessed_date": DATE,
                    "sentence_summary": "期刊目录列出 Jane Costello、论文正式刊名、卷期和页码237–284。目录证实的是书目信息，不是论文正文内容。",
                    "original_quotes": [{"source_span": "volume 13, number 3–4, 1950, article entry", "text": "The Twelve Pictures \"Ordered by Velasquez\" and the Trial of Valguarnera; Jane Costello; pp. 237–284"}],
                },
                {
                    "citation": f"JSTOR, *Journal of the Warburg and Courtauld Institutes*, vol. 13, no. 3/4 (1950), article record. {JSTOR_1950_TOC} Accessed 2026-10-17.",
                    "location": "卷期目录中该文的 DOI 记录",
                    "accessed_date": DATE,
                    "sentence_summary": "JSTOR 为同题、同作者、同页码论文列出 DOI 10.2307/750214。",
                    "original_quotes": [{"source_span": "article entry", "text": "https://doi.org/10.2307/750214"}],
                },
            ],
            "created": DATE,
            "updated": DATE,
            "process_ref": ARTICLE_PROCESS_REF,
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    author_link = "[简·科斯特洛（Jane Costello）](../persons/jane-costello.md)"
    journal_link = "[《瓦尔堡与考陶尔德学院学报》](journal-warburg-courtauld-institutes.md)"
    relation_text = ", ".join(sorted(ARTICLE_RELATIONS))
    body = f"""## 内容

### 描述

**中文：** Jane Costello 关于委拉斯开兹订购的十二幅画及瓦尔古阿内拉审判的学术论文，刊于1950年《Journal of the Warburg and Courtauld Institutes》第13卷第3–4期，页237–284。中文题名为工作译名；论文正文及 Haskell 所引页码未独立查阅。

**English:** A scholarly article by Jane Costello on the twelve pictures ordered by Velasquez and the Valguarnera trial, published in 1950 in volume 13, numbers 3–4, of the *Journal of the Warburg and Courtauld Institutes*, pages 237–284. The article and the pages cited by Haskell were not independently read.

### 书目信息

| 字段 | 值 | 证据 |
|---|---|---|
| 原文题名 | The Twelve Pictures “Ordered by Velasquez” and the Trial of Valguarnera | S1（Haskell 第21章书目 p.420）；S2（期刊目录） |
| 作者 | {author_link} | S1（Haskell 第21章书目）；S2（University of Chicago Press 1950年卷期目录） |
| 刊载期刊 | {journal_link} | S1（Haskell 第21章书目）；S2（期刊目录） |
| 出版年 | 1950 | S1（Haskell 第21章书目）；S2（期刊目录） |
| 卷 | 13 | S2（University of Chicago Press 1950年卷期目录） |
| 期 | 3–4 | S2（University of Chicago Press 1950年卷期目录） |
| 页码 | 237–284 | S1（Haskell 第21章书目）；S2（期刊目录） |
| DOI | [10.2307/750214]({ARTICLE_DOI}) | S3（JSTOR 卷期目录） |
| Haskell 引用页 | 247、274–275、278 | S1（Haskell 第1章及第7章注释；不代表已查阅论文原文） |

## 关系与证据

### 身份与外部链接

- [University of Chicago Press 1950年卷期目录]({UCP_1950_TOC})：题名、作者、卷期与页码。
- [JSTOR 卷期目录]({JSTOR_1950_TOC})：同一论文的 DOI 记录。

### 关系记录

目前没有登记在 relations.csv 中的正式关系。四条直接 S2 引文候选（{relation_text}）留待 S6；作者及刊载期刊作为有据书目字段记录，未在本次 S4 写入正式边。逐组裁决见[过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ARTICLE_ANCHOR})。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Jane Costello person, Warburg serial, and 1950 article groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    primary_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    registrations = [
        (PERSON_CANDIDATE, PERSON_GROUP, PERSON_KU, PERSON_PROCESS_REF, "person", "Jane Costello"),
        (JOURNAL_CANDIDATE, JOURNAL_GROUP, JOURNAL_KU, JOURNAL_PROCESS_REF, "archive", "Journal of the Warburg Institute"),
        (ARTICLE_CANDIDATE, ARTICLE_GROUP, ARTICLE_KU, ARTICLE_PROCESS_REF, "archive", "Jane Costello"),
    ]
    expected_members = {
        PERSON_GROUP: [PERSON_CANDIDATE],
        JOURNAL_GROUP: [JOURNAL_CANDIDATE],
        ARTICLE_GROUP: [ARTICLE_CANDIDATE],
    }
    for candidate_id, group, ku_id, process_ref, entity_type, expected_prefix in registrations:
        candidate = candidate_by_id[candidate_id]
        decision = primary_by_id[candidate_id]
        assert candidate["suggested_type"] == entity_type
        assert candidate["canonical_name"].startswith(expected_prefix)
        assert decision["decision"] == "new" and not decision.get("ku_id")
        assert sync.get_group(decision.get("resolution_note", "")) == group
        members = [
            row["candidate_id"]
            for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == group
        ]
        assert members == expected_members[group]
        assert not any(row.get("ku_id") == ku_id for row in manifest)
        assert not (ROOT / f"04-knowledge/{ku_id}.md").exists()
        assert process_ref.endswith((PERSON_ANCHOR, JOURNAL_ANCHOR, ARTICLE_ANCHOR))

    assert candidate_by_id[PERSON_CANDIDATE]["suggested_type"] == "person"
    assert candidate_by_id[ARTICLE_CANDIDATE]["detail"].find("article not independently read") >= 0
    assert primary_by_id["cand-3509"]["decision"] == "undecided"
    assert primary_by_id["cand-6005"]["decision"] == "undecided"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct_article_relations = {
        row["statement_id"] for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
        and ARTICLE_CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    }
    assert direct_article_relations == ARTICLE_RELATIONS
    assert not any(
        (row.get("qualifiers") or {}).get("relation_candidate") is True
        and PERSON_CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        for row in statements
    )

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    card_paths = [PERSON_CARD, JOURNAL_CARD, ARTICLE_CARD]
    assert all(path not in accepted_lines for path in card_paths)
    for path in card_paths:
        assert not (ROOT / path).exists()

    planned_alignments = [dict(row) for row in alignments]
    notes = {
        PERSON_CANDIDATE: (
            f" S4登记（{DATE}）：{PERSON_GROUP} 映射至 {PERSON_KU}；仅据 Haskell 的全名及1950年期刊目录的作者署名建立来源限定 person KU。"
            "不与 surname-only cand-3509 合并；不补充传记事实。"
        ),
        JOURNAL_CANDIDATE: (
            f" S4登记（{DATE}）：{JOURNAL_GROUP} 映射至 {JOURNAL_KU}；University of Chicago Press 期刊史将 Journal of the Warburg Institute 记为早期刊名，"
            "并记与 Courtauld 的关联正式体现于1940年卷III刊名。将早期题名和 Journal of the Warburg and Courtauld Institutes 作为同一连续期刊的历史/后续题名；"
            "候选 cand-6005 的 Blunt 1944 论文身份仍 undecided，未改写。"
        ),
        ARTICLE_CANDIDATE: (
            f" S4登记（{DATE}）：{ARTICLE_GROUP} 映射至 {ARTICLE_KU}；Haskell 第21章书目及 University of Chicago Press 1950年卷期目录支持题名、作者、卷期和页码；"
            "JSTOR 目录列 DOI 10.2307/750214。论文正文与所引页未独立查阅；四条直接引文候选留待 S6。"
        ),
    }
    for candidate_id, group, ku_id, process_ref, _, _ in registrations:
        row = primary_by_id[candidate_id]
        planned = next(item for item in planned_alignments if item.get("alignment_id") == row["alignment_id"])
        planned["ku_id"] = ku_id
        planned["process_ref"] = process_ref
        planned["resolution_note"] += notes[candidate_id]

    planned_manifest = list(manifest)
    planned_manifest.extend(
        [
            {"ku_id": PERSON_KU, "type": "person", "canonical_name": PERSON_ZH, "name_en": PERSON_EN, "source_task": TASK, "card_path": PERSON_CARD},
            {"ku_id": JOURNAL_KU, "type": "archive", "canonical_name": JOURNAL_ZH, "name_en": JOURNAL_EN, "source_task": TASK, "card_path": JOURNAL_CARD},
            {"ku_id": ARTICLE_KU, "type": "archive", "canonical_name": ARTICLE_ZH, "name_en": ARTICLE_EN, "source_task": TASK, "card_path": ARTICLE_CARD},
        ]
    )
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = insert_accepted(accepted_lines, card_paths)

    cards = {
        PERSON_CARD: make_person_card(),
        JOURNAL_CARD: make_journal_card(),
        ARTICLE_CARD: make_article_card(),
    }
    for card in cards.values():
        fm_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert fm_match and isinstance(yaml.safe_load(fm_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["registered_groups"] == 684
    assert totals["registered_members"] == 845
    assert totals["pending_groups"] == 4101
    assert totals["pending_members"] == 4123
    assert len(planned_manifest) == len(manifest) + 3

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    blocks = [
        f"""<a id="{PERSON_ANCHOR}"></a>

### S3/S4 person：Jane Costello 身份组登记（{DATE}）

{PERSON_CANDIDATE} 保持单成员 new 组 {PERSON_GROUP}，登记为[{PERSON_ZH}（{PERSON_EN}）](../../../{PERSON_CARD})（{PERSON_KU}）。书内以 Miss Jane Costello 指称作者；University of Chicago Press 的1950年卷期目录将 Jane Costello 列为该篇论文作者。候选 cand-3509 的单姓 Costello 仍 undecided，不合并；本卡不补入传记事实。
- 未新增 formal relations。
- S4 登记后：682组/843条成员映射已登记，4,103组/4,125条待登记。
""",
        f"""<a id="{JOURNAL_ANCHOR}"></a>

### S3/S4 archive：Warburg 期刊跨题名登记（{DATE}）

{JOURNAL_CANDIDATE} 保持单成员 new 组 {JOURNAL_GROUP}，登记为[《{JOURNAL_ZH}》（{JOURNAL_EN}）](../../../{JOURNAL_CARD})（{JOURNAL_KU}）。候选来源的旧题名 Journal of the Warburg Institute 与后续题名依出版社期刊史归于同一连续期刊：Courtauld 关联正式体现在1940年卷III刊名中。Haskell 第4章1944年引文使用旧题名短式；候选 cand-6005 的 Blunt 文章对象仍 undecided，不在此处改判。
- 未新增 formal relations。
- S4 登记后：683组/844条成员映射已登记，4,102组/4,124条待登记。
""",
        f"""<a id="{ARTICLE_ANCHOR}"></a>

### S3/S4 archive：Jane Costello 1950 年论文登记（{DATE}）

{ARTICLE_CANDIDATE} 保持单成员 new 组 {ARTICLE_GROUP}，登记为[《{ARTICLE_ZH}》（{ARTICLE_EN}）](../../../{ARTICLE_CARD})（{ARTICLE_KU}）。Haskell 第21章书目 p.420 与 University of Chicago Press 1950年第13卷第3–4期目录核对题名、作者、页码237–284；JSTOR 记录 DOI 10.2307/750214。论文正文及 Haskell 所引页未独立查阅。作者候选 {PERSON_CANDIDATE} 与期刊候选 {JOURNAL_CANDIDATE} 已分别登记为人物和期刊 KU。
- 四条直接 S2 引文候选 {', '.join(sorted(ARTICLE_RELATIONS))} 留待 S6；未新增 formal relations。
- S4 当前已登记684组/845条成员映射，尚待登记4,101组/4,123条。
""",
    ]
    for anchor in (PERSON_ANCHOR, JOURNAL_ANCHOR, ARTICLE_ANCHOR):
        assert f'<a id="{anchor}"></a>' not in process_text
    process_text = process_text.rstrip() + "\n\n" + "\n\n".join(block.rstrip() for block in blocks)

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert count == 1
    result_text += (
        f"\n\n### S3/S4 person：Jane Costello 身份组登记（{DATE}）\n\n"
        f"{PERSON_CANDIDATE} → [{PERSON_ZH}（{PERSON_EN}）](../units/persons/jane-costello.md)；"
        "范围限于该书所引1950年论文的作者身份，cand-3509 保留待证。\n\n"
        f"### S3/S4 archive：Warburg 期刊跨题名登记（{DATE}）\n\n"
        f"{JOURNAL_CANDIDATE} → [《{JOURNAL_ZH}》（{JOURNAL_EN}）](../units/archives/journal-warburg-courtauld-institutes.md)；"
        "出版社期刊史支持1937–1939年旧题名及1940年改题沿革。\n\n"
        f"### S3/S4 archive：Jane Costello 1950 年论文登记（{DATE}）\n\n"
        f"{ARTICLE_CANDIDATE} → [《{ARTICLE_ZH}》（{ARTICLE_EN}）](../units/archives/costello-twelve-pictures-ordered-velasquez-1950.md)；"
        "四项直接引文关系候选留待 S6；论文全文未独立查阅。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: person {PERSON_CANDIDATE}->{PERSON_KU}; journal {JOURNAL_CANDIDATE}->{JOURNAL_KU}; "
            f"article {ARTICLE_CANDIDATE}->{ARTICLE_KU}; article_relation_candidates={len(direct_article_relations)}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    for path, card in cards.items():
        (ROOT / path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: person {PERSON_CANDIDATE}->{PERSON_KU}; journal {JOURNAL_CANDIDATE}->{JOURNAL_KU}; "
        f"article {ARTICLE_CANDIDATE}->{ARTICLE_KU}; manifest={len(planned_manifest)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
