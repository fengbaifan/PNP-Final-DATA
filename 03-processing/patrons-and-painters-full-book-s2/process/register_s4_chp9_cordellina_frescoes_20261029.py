from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
PROC = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
ANCHOR = "s3-s4-s5-s6-chp9-cordellina-frescoes-20261029"
PROC_REF = f"03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR}"
SOURCE_ID = "haskell-1980-rev-ed"
SOURCE_FILE = "02-sources/02-Markdown/09_CHP-9_intro.md"
CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006), "
    "ch. 9, printed p. 256."
)

WORKS = [
    {
        "candidate": "cand-2583",
        "alignment": "aln-2918",
        "group": "sg3-work-cand-2583",
        "ku": "units/works/tiepolo-continence-of-scipio-montecchio-house",
        "title_zh": "西庇阿的节制",
        "title_en": "The Continence of Scipio",
        "mention": "m-chp9-p256-continence-of-scipio-work",
        "statement": "st-chp9-p256-tiepolo-painted-continence-scipio",
        "index": "T.csv#46",
        "quote": "The Continence of Scipio",
        "location": "第9章印刷页256 L160",
        "kind": "墙面壁画（fresco）",
        "kind_evidence": "S1；第9章印刷页256 L160；Haskell称作品为墙面上的fresco。",
        "description_cn": (
            "本卡记录哈斯克尔第9章称为“The Continence of Scipio”的作品。原文将其列为提埃坡罗在"
            "科代利纳蒙泰基奥乡间住宅墙面绘制的壁画之一。中文题名为暂译；书内称名和位置不指认某一"
            "存世版本或外部目录条目。"
        ),
        "description_en": (
            "This card records the work Haskell names “The Continence of Scipio” in Chapter 9. He describes "
            "it as one of the wall frescoes Tiepolo painted at Carlo Cordellina’s country house at Montecchio. "
            "The Chinese title is provisional; the book’s wording and location do not identify a surviving "
            "version or catalogue record."
        ),
        "context_cn": (
            "哈斯克尔把此作品与另一件墙面作品《大流士家人在亚历山大大帝面前》并列，另将《艺术的凯旋》"
            "置于天顶。本卡只记录单件作品，不把三件壁画合并为一个组画或方案。"
        ),
        "context_en": (
            "Haskell names this wall fresco alongside a separate wall fresco, The Family of Darius before "
            "Alexander the Great, and places The Triumph of the Arts on the ceiling. This card records one "
            "work and does not merge the three frescoes into a cycle or programme."
        ),
        "type_note": "walls",
    },
    {
        "candidate": "cand-2589",
        "alignment": "aln-2924",
        "group": "sg3-work-cand-2589",
        "ku": "units/works/tiepolo-family-of-darius-before-alexander-montecchio-house",
        "title_zh": "亚历山大大帝面前的大流士家人",
        "title_en": "The Family of Darius before Alexander the Great",
        "mention": "m-chp9-p256-family-of-darius-work",
        "statement": "st-chp9-p256-tiepolo-painted-family-of-darius",
        "index": "T.csv#52",
        "quote": "The Family of Darius before Alexander the Great",
        "location": "第9章印刷页256 L160–161",
        "kind": "墙面壁画（fresco）",
        "kind_evidence": "S1；第9章印刷页256 L160–161；Haskell称作品为墙面上的fresco。",
        "description_cn": (
            "本卡记录哈斯克尔第9章称为“The Family of Darius before Alexander the Great”的作品。"
            "原文将其列为提埃坡罗在科代利纳蒙泰基奥乡间住宅墙面绘制的壁画之一。中文题名为暂译；"
            "不据此确定大流士的具体身份，也不指认某一存世版本或外部目录条目。"
        ),
        "description_en": (
            "This card records the work Haskell names “The Family of Darius before Alexander the Great” in "
            "Chapter 9. He describes it as one of the wall frescoes Tiepolo painted at Carlo Cordellina’s "
            "country house at Montecchio. The Chinese title is provisional; the card does not resolve which "
            "Darius the title refers to or identify a surviving version or catalogue record."
        ),
        "context_cn": (
            "原文把此墙面作品与《西庇阿的节制》分别列名，并将《艺术的凯旋》列为天顶作品；三者不合并。"
            "书中称名未说明此作品是否属于后世所说的完整组画。"
        ),
        "context_en": (
            "The source names this wall work separately from The Continence of Scipio and places The Triumph "
            "of the Arts on the ceiling. The three works are kept distinct; Haskell does not define a later "
            "complete cycle here."
        ),
        "type_note": "walls",
    },
    {
        "candidate": "cand-2610",
        "alignment": "aln-2945",
        "group": "sg3-work-cand-2610",
        "ku": "units/works/tiepolo-triumph-of-the-arts-montecchio-house",
        "title_zh": "艺术的凯旋",
        "title_en": "The Triumph of the Arts",
        "mention": "m-chp9-p256-triumph-of-arts-work",
        "statement": "st-chp9-p256-tiepolo-painted-triumph-of-arts",
        "index": "T.csv#73",
        "quote": "the Triumph of the Arts on the ceiling",
        "location": "第9章印刷页256 L161",
        "kind": "天顶壁画（fresco on ceiling）",
        "kind_evidence": "S1；第9章印刷页256 L161；Haskell称作品在ceiling上。",
        "description_cn": (
            "本卡记录哈斯克尔第9章称为“The Triumph of the Arts”的作品。原文将其列为提埃坡罗在"
            "科代利纳蒙泰基奥乡间住宅天顶绘制的壁画。中文题名为暂译；书内称名和位置不指认某一存世"
            "版本或外部目录条目。"
        ),
        "description_en": (
            "This card records the work Haskell names “The Triumph of the Arts” in Chapter 9. He describes "
            "it as a fresco Tiepolo painted on the ceiling of Carlo Cordellina’s country house at Montecchio. "
            "The Chinese title is provisional; the book’s wording and location do not identify a surviving "
            "version or catalogue record."
        ),
        "context_cn": (
            "哈斯克尔把《艺术的凯旋》与两件墙面壁画分开，并明确置于天顶。本卡只记录这件具名作品，"
            "不将其与不同宅邸的《雄辩之力》天顶画合并。"
        ),
        "context_en": (
            "Haskell distinguishes The Triumph of the Arts from the two wall frescoes and places it on the "
            "ceiling. This card records the named work separately from the Powers of Eloquence ceiling in a "
            "different palace."
        ),
        "type_note": "ceiling",
    },
]


def read_csv(name: str) -> tuple[Path, list[str], list[dict[str, str]]]:
    path = TABLES / name
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return path, list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    encoding = "utf-8-sig" if path.read_bytes().startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha1(value.encode('utf-8')).hexdigest()[:16]}"


def table_id(ku: str, section: str) -> str:
    value = f"{ku}|{section}|1|字段|值|证据"
    return "tbl-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def card_text(work: dict[str, str]) -> str:
    source_location = f"{work['location']}；PDF物理页18。"
    title_evidence = f"S1；{work['location']}；按印本称名记录，不据此匹配外部目录题名。"
    frontmatter = {
        "title": f"{work['title_zh']}（{work['title_en']}）",
        "name_en": work["title_en"],
        "type": "work",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": CITATION,
                "location": source_location,
                "sentence_summary": (
                    "哈斯克尔称提埃坡罗受召装饰科代利纳位于蒙泰基奥的乡间住宅，并将此具名壁画置于该住宅的墙面或天顶。"
                ),
                "original_quotes": [
                    {"source_span": f"{work['location']}；PDF物理页18", "text": work["quote"]}
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": f"{work['location']}；PDF physical p.18",
                },
            }
        ],
        "created": "2026-10-29",
        "updated": "2026-10-29",
        "process_ref": PROC_REF,
    }
    yaml_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return (
        f"---\n{yaml_text}---\n\n"
        "## 内容\n\n"
        "### 描述\n\n"
        f"**中文：** {work['description_cn']}\n\n"
        f"**English:** {work['description_en']}\n\n"
        "### 名称\n\n| 字段 | 值 | 证据 |\n| --- | --- | --- |\n"
        f"| 书内题名 | {work['title_en']} | {title_evidence} |\n\n"
        "### 基本信息\n\n| 字段 | 值 | 证据 |\n| --- | --- | --- |\n"
        f"| 作品类型 | {work['kind']} | {work['kind_evidence']} |\n\n"
        f"### 本章相关内容\n\n**中文：** {work['context_cn']}\n\n"
        f"**English:** {work['context_en']}\n\n"
        "## 关系与证据\n\n"
        "### 身份与外部链接\n\n"
        "本卡按哈斯克尔的书内称名和叙述界定；未加入外部作品目录或存世版本标识。\n\n"
        "### 关系记录\n\n| 方向与关系 | 关联知识元 | 语境与证据 |\n| --- | --- | --- |\n\n"
        f"### 关系候选入口\n\n[本批逐项S3–S6裁决与边界](../../../03-processing/"
        f"patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})\n"
    )


def build_batch() -> dict:
    alignment_path, alignment_fields, alignments = read_csv("alignment.csv")
    manifest_path, manifest_fields, manifest = read_csv("ku-manifest.csv")
    relations_path, relation_fields, relations = read_csv("relations.csv")
    backlog_path, backlog_fields, backlog = read_csv("candidate-backlog.csv")

    statements = {}
    for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            row = json.loads(line)
            statements[row["statement_id"]] = row

    # Work alignment and S2 evidence preflight.
    for work in WORKS:
        matches = [
            row for row in alignments
            if row["alignment_id"] == work["alignment"] and row["candidate_id"] == work["candidate"]
        ]
        assert len(matches) == 1
        assert matches[0]["decision"] == "undecided" and not matches[0]["ku_id"]
        assert work["group"] not in matches[0]["resolution_note"]
        assert not (ROOT / "04-knowledge" / f"{work['ku']}.md").exists()
        assert not any(row["ku_id"] == work["ku"] for row in manifest)
        statement = statements[work["statement"]]
        assert statement["subject_candidate_id"] == "cand-2569"
        assert statement["object_candidate_id"] == work["candidate"]
        assert statement["qualifiers"]["relation_candidate"] is True
        assert work["candidate"] in statement["qualifiers"]["mentioned_candidate_ids"]

    # Person cross-chapter correction preflight.
    people = {
        row["candidate_id"]: row for row in alignments
        if row["candidate_id"] in {"cand-8387", "cand-8388", "cand-8389"}
    }
    assert people["cand-8387"]["decision"] == "undecided"
    assert people["cand-8388"]["decision"] == "new" and not people["cand-8388"]["ku_id"]
    assert people["cand-8389"]["decision"] == "new" and not people["cand-8389"]["ku_id"]
    assert any(row["ku_id"] == "units/persons/alexander-the-great" for row in manifest)
    assert not any(row["candidate_id"] == "cand-12385" for row in backlog)
    assert len(backlog) == 89 and max(int(row["backlog_id"].split("-")[1]) for row in backlog) == 89
    assert max(int(row["relation_id"].split("-")[1]) for row in relations) == 2622

    # No matching formal or pending S6 record exists in the current table.
    relevant_statements = [
        *(work["statement"] for work in WORKS),
        "st-chp9-p256-cordellina-one-of-few-non-noble-tiepolo-patrons",
        "st-chp9-p256-cordellina-summoned-tiepolo-to-country-house",
        "st-chp9-p256-cordellina-built-montecchio-house",
        "st-chp14-p352-tiepolo-decorated-villa-cordellina",
    ]
    assert not any(
        any(statement_id in row["source_span"] for statement_id in relevant_statements)
        for row in relations
    )

    for work in WORKS:
        row = next(row for row in alignments if row["alignment_id"] == work["alignment"])
        old = row["resolution_note"]
        row["decision"] = "new"
        row["ku_id"] = work["ku"]
        row["process_ref"] = PROC_REF
        row["resolution_note"] = (
            f"prior_decision=undecided; prior_resolution_note={old}; group={work['group']}; "
            f"source_ref=entity-candidates.csv#{work['candidate']}; index_entry={work['index']}; "
            f"s2_mention={work['mention']}; s2_statement={work['statement']}; source-local named fresco; "
            f"no exact same-type work KU found in current work units or manifest; S4 mapped to {work['ku']}; "
            "no external catalogue or surviving-version identity asserted."
        )

    row = people["cand-8389"]
    old = row["resolution_note"]
    row["decision"] = "same"
    row["ku_id"] = "units/persons/alexander-the-great"
    row["process_ref"] = PROC_REF
    row["resolution_note"] = (
        "prior_decision=new; prior_group_token=new-person:alexander-alexander-before-darius-family-g-08ab4b892a; "
        f"prior_resolution_note={old}; group=new-person:alexander-great-68fcc5120d; "
        "source_ref=chp-9:09_CHP-9_intro:l157-165#L160; mention=m-chp9-p256-alexander-figure; "
        "the complete source name Alexander the Great exactly matches the existing cross-chapter person group "
        "cand-3442 and cand-9593 and its KU units/persons/alexander-the-great; exact-name continuity, not a "
        "title-context or surname-only match."
    )

    row = people["cand-8388"]
    old = row["resolution_note"]
    row["decision"] = "undecided"
    row["ku_id"] = ""
    row["process_ref"] = PROC_REF
    row["resolution_note"] = (
        "prior_decision=new; "
        "prior_group_token=new-person:alexander-before-darius-darius-family-grea-44b5380699; "
        f"prior_resolution_note={old}; source_ref=chp-9:09_CHP-9_intro:l157-165#L160; "
        "mention=m-chp9-p256-darius-figure; the source gives only Darius in a painting title and does not "
        "distinguish which historical person; the previous group token was generated from surrounding title "
        "words, not a Darius identity anchor; no Darius KU match or external identity evidence was established. "
        "Keep unresolved; do not merge with Alexander or another Darius."
    )

    row = people["cand-8387"]
    old = row["resolution_note"]
    row["process_ref"] = PROC_REF
    row["resolution_note"] = (
        f"prior_resolution_note={old}; source_ref=chp-9:09_CHP-9_intro:l157-165#L160; "
        "mention=m-chp9-p256-scipio-figure; the title says only Scipio. Do not merge with cand-8196 "
        "(Scipio Africanus in a separate Lazzarini canvas passage on p.250) on the name alone; "
        "identity remains undecided."
    )

    manifest_add = [
        {
            "ku_id": work["ku"],
            "type": "work",
            "canonical_name": work["title_zh"],
            "name_en": work["title_en"],
            "source_task": "patrons-and-painters-full-book-s2",
            "card_path": f"04-knowledge/{work['ku']}.md",
        }
        for work in WORKS
    ]

    enrich_path = TABLES / "enrichment.jsonl"
    enrich_bytes = enrich_path.read_bytes()
    enrich_lines = enrich_path.read_text(encoding="utf-8-sig").splitlines()
    enrichments = [json.loads(line) for line in enrich_lines if line.strip()]
    assert max(int(row["enrichment_id"].split("-")[1]) for row in enrichments) == 18836
    enrichment_add = []
    for work in WORKS:
        fields = [
            (
                "书内题名",
                work["title_en"],
                f"S1；{work['location']}；按印本称名记录，不据此匹配外部目录题名。",
                "内容 / 名称",
            ),
            ("作品类型", work["kind"], work["kind_evidence"], "内容 / 基本信息"),
        ]
        for field, value, evidence, section in fields:
            number = 18837 + len(enrichment_add)
            enrichment_add.append(
                {
                    "enrichment_id": f"enr-{number:05d}",
                    "ku_id": work["ku"],
                    "field": field,
                    "value": value,
                    "origin": "book",
                    "source_id": SOURCE_ID,
                    "source_ids": [SOURCE_ID],
                    "source_ref": "S1",
                    "source_citations": [CITATION],
                    "source_urls": [],
                    "evidence": evidence,
                    "evidence_status": "source_backed",
                    "dispute": None,
                    "accessed_date": "",
                    "occurrence_id": stable_id("occ", f"{work['ku']}|{field}"),
                    "table_id": table_id(work["ku"], section),
                    "table_section": section,
                    "has_header": True,
                    "table_header": ["字段", "值", "证据"],
                    "row_index": 1,
                    "cells": [field, value, evidence],
                    "unit_evidence_status": "source_backed",
                }
            )

    new_relations = []
    for index, work in enumerate(WORKS):
        relation_id = 2623 + index * 2
        new_relations.extend(
            [
                {
                    "relation_id": f"rel-{relation_id}",
                    "subject_ku_id": work["ku"],
                    "object_ku_id": "units/persons/giambattista-tiepolo",
                    "predicate": "created_by",
                    "time": "",
                    "role": "书内作者归属",
                    "scope": "仅记录哈斯克尔称Tiepolo绘制该具名壁画；不主张外部作品目录身份、存世版本或作品日期。",
                    "origin": "book",
                    "status": "formal",
                    "source_id": SOURCE_ID,
                    "source_span": (
                        f"Chapter 9, printed p.256, lines 160–161; PDF physical p.18; "
                        f"statement={work['statement']}"
                    ),
                    "source_file": SOURCE_FILE,
                    "note": f"S6 formal; source-local creator attribution. See {PROC_REF}.",
                },
                {
                    "relation_id": f"rel-{relation_id + 1}",
                    "subject_ku_id": work["ku"],
                    "object_ku_id": "units/places/villa-cordellina-montecchio",
                    "predicate": "installed_at",
                    "time": "",
                    "role": "书内报告的墙面／天顶安置地点",
                    "scope": (
                        "Haskell says Tiepolo was summoned to decorate Cordellina’s Montecchio country house "
                        f"and names this fresco on its {work['type_note']}. Records historical placement in "
                        "that house, not a present location, surviving state, or catalogue identity."
                    ),
                    "origin": "book",
                    "status": "formal",
                    "source_id": SOURCE_ID,
                    "source_span": (
                        f"Chapter 9, printed p.256, lines 160–161; PDF physical p.18; "
                        f"statements=st-chp9-p256-cordellina-summoned-tiepolo-to-country-house,{work['statement']}"
                    ),
                    "source_file": SOURCE_FILE,
                    "note": (
                        f"S6 formal; architectural-fresco placement uses installed_at, not overloaded located_at. "
                        f"See {PROC_REF}."
                    ),
                },
            ]
        )
    new_relations.append(
        {
            "relation_id": "rel-2629",
            "subject_ku_id": "units/persons/giambattista-tiepolo",
            "object_ku_id": "units/persons/carlo-cordellina",
            "predicate": "employed_by",
            "time": "",
            "role": "受雇装饰住宅的画家",
            "scope": (
                "Haskell calls Carlo Cordellina one of the few non-nobles able to employ Tiepolo and says "
                "Cordellina summoned him to decorate the Montecchio house. Records the source-reported employment "
                "without inferring contract terms, dates, or a separate commission for each fresco."
            ),
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": (
                "Chapter 9, printed p.256, lines 158–160; PDF physical p.18; "
                "statements=st-chp9-p256-cordellina-one-of-few-non-noble-tiepolo-patrons,"
                "st-chp9-p256-cordellina-summoned-tiepolo-to-country-house"
            ),
            "source_file": SOURCE_FILE,
            "note": f"S6 formal; artist-to-employer direction follows employed_by. See {PROC_REF}.",
        }
    )
    new_relations.append(
        {
            "relation_id": "rel-2630",
            "subject_ku_id": "units/places/villa-cordellina-montecchio",
            "object_ku_id": "units/persons/carlo-cordellina",
            "predicate": "erected_by",
            "time": "",
            "role": "书内所述营建者",
            "scope": (
                "Haskell says Carlo Cordellina built a country house at Montecchio; Chapter 14 identifies the "
                "same house as Villa Cordellina. Records the source-reported builder without adding a building "
                "date or modern architectural identity."
            ),
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE_ID,
            "source_span": (
                "Chapter 9, printed p.256, line 160; PDF physical p.18; "
                "statement=st-chp9-p256-cordellina-built-montecchio-house"
            ),
            "source_file": SOURCE_FILE,
            "note": f"S6 formal; the cross-chapter Villa Cordellina place group supports this source-local house identity. See {PROC_REF}.",
        }
    )

    backlog.append(
        {
            "backlog_id": "bl-0090",
            "canonical_name": "Cordellina’s magnanimity as interpreted in the two wall frescoes",
            "suggested_type": "term",
            "status": "undecided",
            "source_id": SOURCE_ID,
            "source_ref": (
                "chp-9:09_CHP-9_intro:l157-165#L161; "
                "st-chp9-p256-family-of-darius-alludes-to-cordellina-magnanimity"
            ),
            "statement_id": "st-chp9-p256-wall-paintings-allude-to-cordellina-magnanimity",
            "endpoint_role": "object",
            "candidate_id": "cand-12385",
            "ku_id": "",
            "decision_note": (
                "The two wall-fresco statements report Haskell’s interpretation of allusions to the patron’s "
                "magnanimity. This S3 new term has no registered KU, and the current controlled relation types "
                "provide no faithful alludes-to predicate. Keep both related claims pending; batch the term "
                "through S1–S3–S4 before reconsidering, and do not infer that the ceiling fresco shares this "
                "interpretation. Related statement: "
                "st-chp9-p256-family-of-darius-alludes-to-cordellina-magnanimity."
            ),
            "process_ref": PROC_REF,
        }
    )

    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    new_paths = sorted(row["card_path"] for row in manifest_add)
    for path in new_paths:
        assert f"- {path}" not in accepted_lines
        insert_at = next(
            (
                index
                for index, line in enumerate(accepted_lines)
                if line.startswith("- ") and line[2:] > path
            ),
            len(accepted_lines),
        )
        accepted_lines.insert(insert_at, f"- {path}")

    process = f"""

<a id="{ANCHOR}"></a>
### 2026-10-29：第9章p.256 Tiepolo三件住宅壁画的S3/S4/S6及人名核对

**原文依据与候选核对。** 对照第9章印刷页256（PDF物理页18）图像、来源转录、索引T.csv#46/#52/#73与当前S2表。三条直接mention分别为m-chp9-p256-continence-of-scipio-work、m-chp9-p256-family-of-darius-work、m-chp9-p256-triumph-of-arts-work，各有对应的relation_candidate=true statement；前两件被称为墙面壁画，第三件明确在天顶。原alignment注释称cand-2610“无可核正文提及”，与当前mentions.csv不符，现保留旧注作为历史并纠正该决定理由。此次未修改S2 statement或mention，故不增加统一复核计数。

**S3跨章身份决定。** 三个Tiepolo索引候选均由undecided改为书内来源限定new，分别使用单成员组sg3-work-cand-2583、sg3-work-cand-2589、sg3-work-cand-2610。全体works知识卡及manifest未发现可准确复用的同类型对象。两幅墙面作品与一幅天顶作品保持三个独立身份，不合并为一个组画；《The Family of Darius before Alexander the Great》不与第14章Piazzetta《The Death of Darius》混同，也不与另一宅邸的《Powers of Eloquence》壁画合并。身份仅限Haskell书内具名作品，不认定存世版本、外部目录条目、创作日期或完整周期。

同页人名候选也作定向核平：cand-8389从错误的单独new组改为same，并入已由第1、8、10章候选cand-3442、cand-9593建立的Alexander the Great组及KU units/persons/alexander-the-great；这是完整称名的跨章精确对应。cand-8388从由整段作品标题误生成的new-person组改为undecided：原文仅称Darius，未给足以区别具体历史人物的证据，且没有Darius KU匹配，不据标题猜为Darius III。cand-8387继续undecided；不能仅因同名而并入第9章p.250 Lazzarini描绘Scipio Africanus的另一组作品。上述person行在resolution_note中保留旧决定及旧组号。

**S4/S5登记。** 新增三个独立work KU：units/works/tiepolo-continence-of-scipio-montecchio-house、units/works/tiepolo-family-of-darius-before-alexander-montecchio-house、units/works/tiepolo-triumph-of-the-arts-montecchio-house；每卡只加入一条书内称名和一条作品类型字段，共6条source_backed字段。无日期、材料、外部身份或存世状态字段。

**S6相关裁决与待证去向。** 修改前relations.csv无以下statement裁决行；新增八条formal边：rel-2623/2625/2627 created_by分别记录三件作品的书内Tiepolo归属；rel-2624/2626/2628 installed_at分别记录两幅墙面作品及一幅天顶作品在Villa Cordellina的书内历史安置；rel-2629 employed_by记录Haskell称Carlo Cordellina雇用并召Tiepolo装饰其住宅；rel-2630 erected_by记录其营建Villa Cordellina的书内报告。以上不推断聘期、合同、建造日期或每件作品单独委托。使用installed_at表达壁画与建筑一体的历史安置，不使用标注needs_split的located_at。

两条墙面作品对cand-12385的magnanimity解释关系仍待证：当前候选虽为S3 new，尚无term KU，且受控类型没有忠实的alludes-to谓词；新增bl-0090作为待处理端点，不登记KU或formal边。st-chp9-p256-tiepolo-irritated-by-cordellina-entertainment的情绪陈述没有可忠实表达的受控谓词，保持process-only pending。未将人物标题mention自动转成has_subject关系，也未逐件推断commissioned_by。以上待证对象不阻断三个work KU登记。

| S2 statement | 当前S6去向 | 理由 |
|---|---|---|
| st-chp9-p256-tiepolo-painted-continence-scipio | formal：rel-2623 created_by；rel-2624 installed_at | Tiepolo→作品作者归属；作品→Villa Cordellina历史墙面安置。 |
| st-chp9-p256-tiepolo-painted-family-of-darius | formal：rel-2625 created_by；rel-2626 installed_at | Tiepolo→作品作者归属；作品→Villa Cordellina历史墙面安置。 |
| st-chp9-p256-tiepolo-painted-triumph-of-arts | formal：rel-2627 created_by；rel-2628 installed_at | Tiepolo→作品作者归属；作品→Villa Cordellina历史天顶安置。 |
| st-chp9-p256-cordellina-one-of-few-non-noble-tiepolo-patrons; st-chp9-p256-cordellina-summoned-tiepolo-to-country-house | formal：rel-2629 employed_by | 两句合读支持Tiepolo受雇为Cordellina装饰住宅；不延伸为每件作品的具体委托或合同。 |
| st-chp9-p256-cordellina-built-montecchio-house | formal：rel-2630 erected_by | 第9章称Cordellina在Montecchio建造乡间住宅；跨章S3 place组将该处与Villa Cordellina相连。 |
| st-chp9-p256-wall-paintings-allude-to-cordellina-magnanimity; st-chp9-p256-family-of-darius-alludes-to-cordellina-magnanimity | pending；bl-0090 | 解释性term端点cand-12385尚未登记，且无忠实alludes-to谓词；只适用于两幅墙画，不扩展至天顶画。 |
| st-chp9-p256-tiepolo-irritated-by-cordellina-entertainment | pending（process-only） | 原文报告的情绪不是争执、冲突或其他现有受控关系；不伪造formal边。 |
| st-chp14-p352-tiepolo-decorated-villa-cordellina | pending（process-only） | Haskell直接称Tiepolo装饰此建筑；当前受控谓词无忠实的person-to-place装饰角色。三条work installed_at边不代替该关系。 |

**批后状态与验证。** 本记录完成后按当前表格重算S2/S3/S4/S5/S6/backlog；针对六张受影响卡（3张新work、Tiepolo、Carlo Cordellina、Villa Cordellina）执行关系预览与渲染。结构审计与关系一致性仅证明格式、外键和表间约束；S2统一ID/来源版本核平、全书独立语义接收及S6历史裁决分母核平仍未解决。
"""
    process = process.lstrip("\n")

    return {
        "alignment_path": alignment_path,
        "alignment_fields": alignment_fields,
        "alignments": alignments,
        "manifest_path": manifest_path,
        "manifest_fields": manifest_fields,
        "manifest": manifest + manifest_add,
        "relations_path": relations_path,
        "relation_fields": relation_fields,
        "relations": relations + new_relations,
        "backlog_path": backlog_path,
        "backlog_fields": backlog_fields,
        "backlog": backlog,
        "enrich_path": enrich_path,
        "enrich_bytes": enrich_bytes,
        "enrich_lines": enrich_lines + [json.dumps(row, ensure_ascii=False) for row in enrichment_add],
        "accepted_path": accepted_path,
        "accepted_lines": accepted_lines,
        "cards": [(ROOT / "04-knowledge" / f"{work['ku']}.md", card_text(work)) for work in WORKS],
        "process": process,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Register the three Cordellina fresco work groups and adjudicate their direct relations.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    batch = build_batch()
    print("S3 new work groups: sg3-work-cand-2583, sg3-work-cand-2589, sg3-work-cand-2610.")
    print("S3 person corrections: cand-8389 same Alexander the Great; cand-8388 undecided; cand-8387 remains undecided.")
    print("S4/S5: 3 source-bounded work KUs and 6 Haskell-backed fields.")
    print("S6 formal: rel-2623 through rel-2628 created_by / installed_at; rel-2629 employed_by; rel-2630 erected_by.")
    print("Pending: cand-12385 term endpoint in bl-0090; irritation claim remains process-only pending.")
    if args.dry_run:
        return

    for path, text in batch["cards"]:
        path.write_text(text, encoding="utf-8", newline="\n")
    write_csv(batch["alignment_path"], batch["alignment_fields"], batch["alignments"])
    write_csv(batch["manifest_path"], batch["manifest_fields"], batch["manifest"])
    write_csv(batch["relations_path"], batch["relation_fields"], batch["relations"])
    write_csv(batch["backlog_path"], batch["backlog_fields"], batch["backlog"])
    encoding = "utf-8-sig" if batch["enrich_bytes"].startswith(b"\xef\xbb\xbf") else "utf-8"
    batch["enrich_path"].write_text(
        "\n".join(batch["enrich_lines"]) + "\n", encoding=encoding, newline="\n"
    )
    batch["accepted_path"].write_text(
        "\n".join(batch["accepted_lines"]) + "\n", encoding="utf-8", newline="\n"
    )
    with PROC.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(batch["process"])
    print("Applied S3/S4/S5/S6 work batch; review six affected cards with build_cards.py --preview.")


if __name__ == "__main__":
    main()
