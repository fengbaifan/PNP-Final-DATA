from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync
import scripts.build_field_facts as field_facts

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
RELATIONS_PATH = TABLES / "relations.csv"
ENRICHMENT_PATH = TABLES / "enrichment.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
AGENTS_PATH = ROOT / "AGENTS.md"
DATE = "2026-10-20"
ANCHOR = "s4-s5-s6-archive-ch3-ch7-bibliographic-citations-20261020"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
CH3 = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
CH7 = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
BIB = "02-sources/02-Markdown/21_CHP-21Bibliography.md"


SPECS = [
    {
        "candidate": "cand-5473",
        "group": "archive-group-58e12013842e",
        "ku_id": "units/archives/lanckoronska-decoracja-gesu-1935",
        "type": "archive",
        "sub_type": "book",
        "name_zh": "耶稣堂装饰",
        "name_en": "Decoration of the Church of the Gesù",
        "sources": [
            {
                "location": "第21章，印刷页427书目条目；OCR L661。",
                "summary": "书目列出作者形式、题名、Lvov 与 1935 年；只支持 Haskell 的书目著录。S0 OCR 作“II Gesù”，既有 S2 图像校读记为“Il Gesù”。",
                "source_file": BIB,
                "span": "L661; printed p.427",
                "quotes": ["Lanckoronska, K.: Decoracja Kosciola II Gesù, Lvov 1935."],
                "link": "[第21章 p.427 书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L661)",
            },
            {
                "location": "第3章，印刷页82注3、页83注2、页84注1；OCR L203、L206–207。",
                "summary": "三条脚注分别以 Lanckoronska, 1935 或简写 Lanckoronska 引用该书；被引内容未独立查阅。",
                "source_file": CH3,
                "span": "L203, L206–207; printed pp.82 n.3, 83 n.2, 84 n.1",
                "quotes": [
                    "3 These drawings are in Berlin and Düsseldorf. This whole interpretation of the iconography of the Gesù frescoes is derived from Lanckoronska, 1935.",
                    "2 Lanckoronska.",
                    "1 Lanckoronska.",
                ],
                "link": "[第3章 p.82–84脚注](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md#L203)",
            },
        ],
        "fields": [
            ("文献类型", "图书", "S1；第21章书目，印刷页427"),
            ("原题名", "*Decoracja Kosciola Il Gesù*", "S1；第21章书目，印刷页427；S0 OCR作“II Gesù”，既有S2图像校读为“Il Gesù”"),
            ("责任者（书目署名）", "K. Lanckoronska（照录书目形式；人物候选cand-10932仍待证）", "S1；第21章书目，印刷页427"),
            ("出版地", "Lvov", "S1；第21章书目，印刷页427"),
            ("出版年", "1935", "S1；第21章书目，印刷页427"),
            ("Haskell书内引文范围", "第3章p.82 n.3、p.83 n.2、p.84 n.1；被引内容未独立查阅", "S2；第3章脚注，印刷页82–84"),
        ],
        "paragraph_zh": (
            "本卡登记 Haskell 第21章书目列出的出版物 *Decoracja Kosciola Il Gesù*（Lvov，1935）。"
            "中文显示名和英文名为描述性工作译名。书目署名保留“K. Lanckoronska”；对应人物候选 cand-10932 仍为 S3 undecided，"
            "本卡不补全姓名或将其并入人物 KU。第3章三条脚注引用该书；原书及被引页均未独立查阅。"
        ),
        "paragraph_en": (
            "This unit records the publication *Decoracja Kosciola Il Gesù* (Lvov, 1935) as listed in Haskell’s chapter 21 bibliography. "
            "The Chinese display name and English name are descriptive working translations. The bibliographic author form “K. Lanckoronska” "
            "is retained; person candidate cand-10932 remains S3 undecided, so the name is not expanded or linked to a person KU. "
            "Three chapter 3 notes cite the publication. Neither the publication nor its cited pages was independently consulted."
        ),
        "citation_ids": [
            "st-chp3-seciv-notes-l189-204-p82-n3-lanckoronska",
            "st-chp3-seciv-notes-l205-243-p83-n2-lanckoronska",
            "st-chp3-seciv-notes-l205-243-p84-n1-lanckoronska",
        ],
        "relation_role": "第3章脚注书目引文",
        "relation_scope": "Haskell第3章p.82 n.3、p.83 n.2、p.84 n.1分别引用该书或以作者姓氏简写回指；只记录书内引注，不表示被引内容已核实。",
        "relation_span": "lines 203, 206–207; print pp.82 n.3, 83 n.2, 84 n.1",
        "relation_file": CH3,
    },
    {
        "candidate": "cand-5491",
        "group": "archive-group-4d60e2987b4e",
        "ku_id": "units/archives/baldinucci-vita-padre-pozzo-ms-cod-palat-565",
        "type": "archive",
        "sub_type": "manuscript",
        "name_zh": "波佐神父传手稿",
        "name_en": "Vita del Padre Pozzo manuscript",
        "sources": [
            {
                "location": "第3章，印刷页88注5、页89注3、页90注2；OCR L232、L235、L238。",
                "summary": "第88页注5完整著录一条 Baldinucci 手稿引用；第89、90页脚注以“Baldinucci MS. cit.”回指。S0 OCR 的叶码缩写保留原样；手稿未查阅。",
                "source_file": CH3,
                "span": "L232, L235, L238; printed pp.88 n.5, 89 n.3, 90 n.2",
                "quotes": [
                    "5 See MSS. Cod. Palat. 565, if. 120-42, in Biblioteca Nazionale, Florence: Francesco Baldinucci: Vita del Padre Pozzo.",
                    "3 Quoted by Pastor, XIV, parte II, p. 26. See also Baldinucci MS. cit.",
                    "2 Baldinucci MS. cit.",
                ],
                "link": "[第3章 p.88–90脚注](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md#L232)",
            },
        ],
        "fields": [
            ("文献类型", "未刊手稿（据Haskell脚注）", "S1；第3章p.88 n.5"),
            ("题名（书内著录）", "*Vita del Padre Pozzo*", "S1；第3章p.88 n.5"),
            ("责任者（脚注著录）", "Francesco Baldinucci（Haskell脚注署名；未建立人物身份映射）", "S1；第3章p.88 n.5；biographer候选cand-5388仍为undecided，不与Filippo Baldinucci合并"),
            ("脚注所列保管机构", "Biblioteca Nazionale, Florence", "S1；第3章p.88 n.5；仅记录Haskell引文著录"),
            ("脚注所列馆藏号", "Cod. Palat. 565", "S1；第3章p.88 n.5"),
            ("脚注叶码定位（S0 OCR）", "“if. 120-42”；缩写校读未在本批独立核验", "S1；第3章p.88 n.5"),
            ("Haskell书内引文范围", "第3章p.88 n.5、p.89 n.3、p.90 n.2；手稿及所引叶码未查阅", "S1；第3章脚注，印刷页88–90"),
        ],
        "paragraph_zh": (
            "本卡登记 Haskell 第3章脚注所指向的 *Vita del Padre Pozzo* 手稿，按引文保留 Biblioteca Nazionale, Florence、"
            "Cod. Palat. 565 和 S0 OCR 叶码形式“if. 120-42”。第88页注5将其著录为“Francesco Baldinucci: Vita del Padre Pozzo”；"
            "这只是 Haskell 的书内著录，本批未确认作者人物身份，也未将其与既有 Filippo Baldinucci KU 合并。"
            "手稿及引用叶码均未独立查阅。"
        ),
        "paragraph_en": (
            "This unit records the *Vita del Padre Pozzo* manuscript cited in Haskell’s chapter 3 notes, retaining the cited repository "
            "Biblioteca Nazionale, Florence, shelfmark Cod. Palat. 565, and the S0 OCR locator “if. 120-42”. Chapter 3 note 5 attributes "
            "the manuscript as “Francesco Baldinucci: Vita del Padre Pozzo”. This records Haskell’s attribution only; the person’s identity "
            "was not established here and was not merged with the existing Filippo Baldinucci KU. Neither the manuscript nor the cited folios "
            "was independently consulted."
        ),
        "citation_ids": [
            "st-chp3-seciv-notes-l205-243-p88-n5-baldinucci-ms",
            "st-chp3-seciv-notes-l205-243-p89-n3-baldinucci-citation",
            "st-chp3-seciv-notes-l205-243-p90-n2-baldinucci-ms",
        ],
        "relation_role": "第3章脚注书目引文",
        "relation_scope": "Haskell第3章p.88 n.5著录该手稿；p.89 n.3与p.90 n.2以“Baldinucci MS. cit.”回指。只记录引注，不确认手稿作者身份、馆藏记录或叶码内容。",
        "relation_span": "lines 232, 235, 238; print pp.88 n.5, 89 n.3, 90 n.2",
        "relation_file": CH3,
    },
    {
        "candidate": "cand-7042",
        "group": "archive-group-a26d5e573340",
        "ku_id": "units/archives/bonnaffe-dictionnaire-amateurs-francais-1884",
        "type": "archive",
        "sub_type": "book",
        "name_zh": "法国17世纪鉴赏家辞典",
        "name_en": "Dictionary of French Art Collectors in the Seventeenth Century",
        "sources": [
            {
                "location": "第21章，印刷页416书目条目；OCR L220。",
                "summary": "书目列出 Edmond Bonnaffé、题名、Paris 与 1884 年；只支持 Haskell 的书目著录。",
                "source_file": BIB,
                "span": "L220; printed p.416",
                "quotes": ["Bonnaffé, Edmond: Dictionnaire des amateurs français au XVII siècle, Paris 1884."],
                "link": "[第21章 p.416 书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L220)",
            },
            {
                "location": "第7章，印刷页175注2、页184注4、页187注1；OCR L313、L357、L362。",
                "summary": "三条脚注分别引用该书第269页、第168–170页、第68–69及113–115页；被引内容未独立查阅。",
                "source_file": CH7,
                "span": "L313, L357, L362; printed pp.175 n.2, 184 n.4, 187 n.1",
                "quotes": [
                    "2 Bonnaffe, p. 269.",
                    "4 Bonnaffé, pp. 168-70, and Briganti, 1962, p. 230. Guercino’s Cato is now at Marseilles—Hoog, pp. 270 ff.",
                    "1 Alazard, passim, and Bonnaffé, pp. 68-9 and 113-15. —",
                ],
                "link": "[第7章 p.175、184、187脚注](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md#L313)",
            },
        ],
        "fields": [
            ("文献类型", "图书", "S1；第21章书目，印刷页416"),
            ("原题名", "*Dictionnaire des amateurs français au XVII siècle*", "S1；第21章书目，印刷页416"),
            ("责任者（书目署名）", "[Edmond Bonnaffé](../persons/edmond-bonnaffe.md)（照录书目责任者形式）", "S1；第21章书目，印刷页416"),
            ("出版地", "Paris", "S1；第21章书目，印刷页416"),
            ("出版年", "1884", "S1；第21章书目，印刷页416"),
            ("Haskell书内引文范围", "第7章p.175 n.2引p.269；p.184 n.4引pp.168–170；p.187 n.1引pp.68–69、113–115；被引内容未独立查阅", "S2；第7章脚注，印刷页175、184、187"),
        ],
        "paragraph_zh": (
            "本卡登记 Haskell 第21章书目列出的 Edmond Bonnaffé《Dictionnaire des amateurs français au XVII siècle》（Paris，1884）。"
            "作者姓名按书目形式链接至本批登记的人物 KU；该登记只确认书内姓名与责任者著录，不补写生平或外部身份。"
            "第7章三条脚注引用该书；原书及被引页未独立查阅。中文与英文显示名为描述性工作译名。"
        ),
        "paragraph_en": (
            "This unit records Edmond Bonnaffé’s *Dictionnaire des amateurs français au XVII siècle* (Paris, 1884) as listed in Haskell’s "
            "chapter 21 bibliography. The name is linked to the person KU registered in this batch; that registration records only the name "
            "and bibliographic responsibility stated in Haskell, without adding biography or external identity claims. Three chapter 7 notes "
            "cite the book. Neither the book nor the cited pages was independently consulted. The Chinese display name and English name are "
            "descriptive working translations."
        ),
        "citation_ids": [
            "st-chp7-p175-n2-cite-bonnaffe",
            "st-chp7-p184-n4-cite-bonnaffe",
            "st-chp7-p187-n1-cite-bonnaffe",
        ],
        "relation_role": "第7章脚注书目引文",
        "relation_scope": "Haskell第7章p.175 n.2、p.184 n.4、p.187 n.1分别引用该书pp.269、168–170、68–69及113–115；只记录书内引注，不表示被引内容已核实。",
        "relation_span": "lines 313, 357, 362; print pp.175 n.2, 184 n.4, 187 n.1",
        "relation_file": CH7,
    },
]

PERSON_SPEC = {
    "candidate": "cand-7043",
    "group": "new-person:bonnaffe-edmond-a247874362",
    "ku_id": "units/persons/edmond-bonnaffe",
    "type": "person",
    "name_zh": "埃德蒙·博纳费",
    "name_en": "Edmond Bonnaffé",
    "source": {
        "location": "第21章，印刷页416书目条目；OCR L220。",
        "summary": "书目以“Bonnaffé, Edmond”形式列出该书责任者；只记录 Haskell 的书目身份，不补写生平或外部身份。",
        "source_file": BIB,
        "span": "L220; printed p.416",
        "quote": "Bonnaffé, Edmond: Dictionnaire des amateurs français au XVII siècle, Paris 1884.",
        "link": "[第21章 p.416 书目](../../../02-sources/02-Markdown/21_CHP-21Bibliography.md#L220)",
    },
}


def source_entry(source: dict) -> dict:
    return {
        "citation": f"{BOOK_CITATION}, {source['location']}",
        "location": source["location"],
        "sentence_summary": source["summary"],
        "original_quotes": [
            {"source_span": source["span"], "text": quote}
            for quote in source.get("quotes", [source.get("quote", "")])
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source["source_file"],
            "source_span": source["span"],
        },
    }


def make_archive_card(spec: dict) -> str:
    fm_data = {
        "title": f"《{spec['name_zh']}》（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": "archive",
        "sub_type": spec["sub_type"],
        "evidence_status": "source_backed",
        "sources": [source_entry(source) for source in spec["sources"]],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in spec["fields"])
    links = "；".join(source["link"] for source in spec["sources"])
    english_links = "; ".join(source["link"] for source in spec["sources"])
    return f"""---
{yaml.safe_dump(fm_data, allow_unicode=True, sort_keys=False, width=1000)}---

## 内容

### 描述

**中文：** {spec['paragraph_zh']} {links}

**English:** {spec['paragraph_en']} {english_links}

### 书目身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
{rows}

### 身份边界

本 KU 对应 S3 身份组 `{spec['group']}`，登记为独立 archive 对象。身份范围限于 Haskell 书目／脚注所指的出版物或手稿；不据引注推断被引内容已核实。

## 关系与证据

### 关系记录

| 方向与关系 | 关联知识元 | 语境与证据 |
|---|---|---|

### 身份入口

- **S3身份组：** `{spec['group']}`；候选 `{spec['candidate']}` 映射至本 KU。详细身份去向及逐条 S6 裁决见[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def make_person_card() -> str:
    source = PERSON_SPEC["source"]
    fm_data = {
        "title": f"{PERSON_SPEC['name_zh']}（{PERSON_SPEC['name_en']}）",
        "name_en": PERSON_SPEC["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [source_entry(source)],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    link = source["link"]
    return f"""---
{yaml.safe_dump(fm_data, allow_unicode=True, sort_keys=False, width=1000)}---

## 内容

### 描述

**中文：** Haskell 第21章书目以“Bonnaffé, Edmond”形式，将埃德蒙·博纳费列为《Dictionnaire des amateurs français au XVII siècle》（Paris，1884）的书目责任者。本卡只记录该书目身份与署名，不补写生平、职业或外部身份。{link}

**English:** Haskell’s chapter 21 bibliography lists Edmond Bonnaffé as the bibliographic author of *Dictionnaire des amateurs français au XVII siècle* (Paris, 1884). This unit records only that source-local identity and attribution; it adds no biography, occupation, or external identity claim. {link}

### 身份边界

本 KU 对应 S3 身份组 `{PERSON_SPEC['group']}`，仅以 Haskell 书目中明确列出的全名登记；本批未查询外部人物规范记录，也未据书目著录新增 `authored_by` 关系。

## 关系与证据

### 身份入口

- **S3身份组：** `{PERSON_SPEC['group']}`；候选 `{PERSON_SPEC['candidate']}` 映射至本 KU。书目署名与关系边界见[本批过程记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。
"""


def insert_accepted_paths(text: str, card_paths: list[str]) -> str:
    lines = text.splitlines()
    for card_rel in card_paths:
        if f"- {card_rel}" in lines:
            raise AssertionError(f"accepted path already exists: {card_rel}")
        insert_at = next(
            (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def write_csv_preserving_bom(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    encoding = "utf-8-sig" if path.read_bytes().startswith(b"\xef\xbb\xbf") else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize_relation_endpoint_queue(candidate_rows: list[dict], alignment_rows: list[dict], manifest_rows: list[dict], statements: list[dict]) -> tuple[int, int, int, dict[str, tuple[int, int]]]:
    manifest_ids = {r["ku_id"] for r in manifest_rows}
    candidates = {r["candidate_id"]: r for r in candidate_rows}
    decisions = {r["candidate_id"]: r for r in alignment_rows if r.get("candidate_id") and not r.get("external_source")}
    group_members: dict[str, set[str]] = {}
    group_types: dict[str, str] = {}
    for candidate_id, decision in decisions.items():
        if decision.get("decision") != "new" or decision.get("ku_id") in manifest_ids:
            continue
        group = sync.get_group(decision.get("resolution_note", ""))
        if group:
            group_members.setdefault(group, set()).add(candidate_id)
            group_types[group] = candidates[candidate_id]["suggested_type"]
    active_groups: set[str] = set()
    active_candidates: set[str] = set()
    for statement in statements:
        qualifiers = statement.get("qualifiers") or {}
        if not isinstance(qualifiers, dict) or qualifiers.get("relation_candidate") is not True:
            continue
        for candidate_id in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
            decision = decisions.get(candidate_id or "", {})
            if decision.get("decision") != "new" or decision.get("ku_id") in manifest_ids:
                continue
            group = sync.get_group(decision.get("resolution_note", ""))
            if not group:
                continue
            active_groups.add(group)
            active_candidates.add(candidate_id)
    type_counts: dict[str, tuple[int, int]] = {}
    for group in active_groups:
        kind = group_types[group]
        old_groups, old_members = type_counts.get(kind, (0, 0))
        type_counts[kind] = (old_groups + 1, old_members + len(group_members[group]))
    return len(active_groups), len(active_candidates), sum(len(group_members[g]) for g in active_groups), type_counts


def apply() -> int:
    parser = argparse.ArgumentParser(description="Register source-backed archive citation endpoints and adjudicate their S6 citations.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    relation_fields, relations = sync.read_csv(RELATIONS_PATH)
    source_fields, source_rows = sync.read_csv(TABLES / "sources.csv")
    backlog_fields, backlog_rows = sync.read_csv(TABLES / "candidate-backlog.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    decision_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    statements = sync.load_statements()
    statement_by_id = {r["statement_id"]: r for r in statements}
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    all_specs = [*SPECS, PERSON_SPEC]
    seen_ids, seen_paths = set(), set()
    for spec in all_specs:
        candidate = candidate_by_id[spec["candidate"]]
        decision = decision_by_id[spec["candidate"]]
        card_path = f"04-knowledge/{spec['ku_id']}.md"
        assert candidate.get("suggested_type") == spec["type"], spec["candidate"]
        assert decision.get("decision") == "new" and not decision.get("ku_id"), spec["candidate"]
        assert sync.get_group(decision.get("resolution_note", "")) == spec["group"], spec["candidate"]
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert members == [spec["candidate"]], (spec["group"], members)
        assert not (ROOT / card_path).exists(), card_path
        assert card_path not in accepted_text
        assert not any(row["ku_id"] == spec["ku_id"] or row["card_path"] == card_path for row in manifest)
        assert not any(row["type"] == spec["type"] and row["name_en"].casefold() == spec["name_en"].casefold() for row in manifest)
        assert spec["ku_id"] not in seen_ids and card_path not in seen_paths
        seen_ids.add(spec["ku_id"])
        seen_paths.add(card_path)

    assert "haskell-1980-rev-ed" in {row["source_id"] for row in source_rows}
    assert not any(row["status"] == "pending" for row in backlog_rows)
    assert ANCHOR not in process_text and ANCHOR not in result_text
    assert len(relations) == 1266 and sum(row["status"] == "formal" for row in relations) == 1264
    assert len([row for row in alignments if row.get("candidate_id") == "cand-7043" and not row.get("external_source")]) == 1

    cited_ids = [statement_id for spec in SPECS for statement_id in spec["citation_ids"]]
    for spec in SPECS:
        for statement_id in spec["citation_ids"]:
            statement = statement_by_id[statement_id]
            assert statement.get("qualifiers", {}).get("relation_candidate") is True, statement_id
            assert statement.get("predicate") == "cites", statement_id
            assert statement.get("subject_candidate_id") == "cand-2962", statement_id
            assert statement.get("object_candidate_id") == spec["candidate"], statement_id
            assert statement_id not in process_text, f"already adjudicated: {statement_id}"
            assert not any(statement_id in row.get("note", "") for row in relations), f"already in relations: {statement_id}"

    planned_alignment = [dict(row) for row in alignments]
    planned_decision_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for spec in all_specs:
        row = planned_decision_by_id[spec["candidate"]]
        row["ku_id"] = spec["ku_id"]
        row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        row["resolution_note"] += (
            f" S4 registration: {spec['group']} maps to {spec['ku_id']}; source-local registration only, "
            "with no unsupported external identity or document-content claim."
        )

    planned_manifest = list(manifest)
    for spec in all_specs:
        planned_manifest.append({
            "ku_id": spec["ku_id"],
            "type": spec["type"],
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": f"04-knowledge/{spec['ku_id']}.md",
        })
    paths = [f"04-knowledge/{spec['ku_id']}.md" for spec in all_specs]
    planned_accepted = insert_accepted_paths(accepted_text, paths)
    card_contents = {ROOT / paths[i]: make_archive_card(SPECS[i]) for i in range(len(SPECS))}
    card_contents[ROOT / paths[-1]] = make_person_card()

    new_relation_rows = []
    next_relation_id = max(int(row["relation_id"].split("-")[1]) for row in relations) + 1
    for spec in SPECS:
        new_relation_rows.append({
            "relation_id": f"rel-{next_relation_id:04d}",
            "subject_ku_id": "units/archives/patrons-and-painters",
            "object_ku_id": spec["ku_id"],
            "predicate": "cites",
            "time": "",
            "role": spec["relation_role"],
            "scope": spec["relation_scope"],
            "origin": "book",
            "status": "formal",
            "source_id": "haskell-1980-rev-ed",
            "source_span": spec["relation_span"],
            "source_file": spec["relation_file"],
            "note": "S2 statements: " + "; ".join(spec["citation_ids"]) + ". Bibliographic citation only; cited work and pages not consulted.",
        })
        next_relation_id += 1
    relation_keys = {
        (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"])
        for row in relations
    }
    for row in new_relation_rows:
        key = (row["subject_ku_id"], row["predicate"], row["object_ku_id"], row["time"], row["role"], row["scope"])
        assert key not in relation_keys, key
        relation_keys.add(key)
    planned_relations = relations + new_relation_rows

    source_markers = {r["source_id"] for r in source_rows}
    for content in card_contents.values():
        fm_match = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
        fm = yaml.safe_load(fm_match.group(1))
        assert all(field_facts.citation_identity(source["citation"])[0] in source_markers for source in fm["sources"])
    for spec in [*SPECS, PERSON_SPEC]:
        source_items = spec["sources"] if spec is not PERSON_SPEC else [PERSON_SPEC["source"]]
        for source in source_items:
            text = (ROOT / source["source_file"]).read_text(encoding="utf-8-sig")
            for quote in source.get("quotes", [source.get("quote", "")]):
                normalized_source = " ".join(text.split())
                normalized_quote = " ".join(quote.split())
                assert normalized_quote in normalized_source, f"quoted source text missing: {spec['candidate']} {quote}"

    # Run the existing extractor against temporary copies, then keep only these 19 rows.
    old_base = field_facts.BASE
    with tempfile.TemporaryDirectory(prefix="pnp-s4-archive-fields-") as temp_name:
        temp_root = Path(temp_name)
        field_facts.BASE = temp_root
        for path, content in card_contents.items():
            relative = path.relative_to(ROOT)
            temp_path = temp_root / relative
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.write_text(content, encoding="utf-8-sig", newline="\n")
        selected_manifest = [row for row in planned_manifest if row["ku_id"] in seen_ids]
        new_field_rows, new_sources, field_warnings, cards_with_tables = field_facts.extract_records(selected_manifest)
        field_facts.BASE = old_base
    assert not field_warnings, field_warnings
    assert cards_with_tables == 3 and len(new_field_rows) == 19, (cards_with_tables, len(new_field_rows))
    assert all(row["evidence_status"] == "source_backed" and row["origin"] == "book" for row in new_field_rows)
    assert all(row["source_ids"] == ["haskell-1980-rev-ed"] for row in new_field_rows)
    field_facts.assign_ids(new_field_rows, ENRICHMENT_PATH)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    updated_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    summary = (
        f"**当前状态：全书 S2 语义处理已完成，尚未独立语义验收；统一计入口径的独立逐条复核覆盖9,394/15,164条statement（61.9%），"
        f"第七章1,008/1,238、第八章482/1,462，均未接收；S3已记录全部候选的现行决定与去向，冲突及待证对象仍未解决；S4 KU登记处理中。** "
        f"12,408个候选决定行中，same=2,024（指向1,092个既有KU）、new=5,029（{sync.fmt(totals['new_groups'])}个身份组）、conflict=9、excluded=100、undecided=5,246（含622项类型未决）。"
        f"S4已登记{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['new_groups'])}组、{sync.fmt(totals['registered_members'])}/{sync.fmt(totals['new_candidates'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组／{sync.fmt(totals['pending_members'])}条映射。"
    )
    updated_result, replaced = re.subn(r"^\*\*当前状态：.*$", summary, updated_result, count=1, flags=re.M)
    assert replaced == 1
    updated_result = re.sub(
        r"^\| \[字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        "| [字段表](../tables/enrichment.jsonl) | 11,757条，其中1,625条 unverified |",
        updated_result,
        count=1,
        flags=re.M,
    )
    updated_result = re.sub(
        r"^\| \[关系表\]\(\.\./tables/relations\.csv\) \|.*$",
        "| [关系表](../tables/relations.csv) | 1,269条：1,267 formal、2 pending；0条缺结构化 `source_id`（45条已回补）；S2另有10,401条`relation_candidate=true`的statement，二者不是同一计数口径 |",
        updated_result,
        count=1,
        flags=re.M,
    )
    batch_result = (
        f"### S4/S5/S6 archive：第3章与第7章书目引注端点批次（{DATE}）\n\n"
        "登记三个直接 archive 组及其 S3 既有决定；另登记 Bonnaffé 书目责任者已有的 S3 新人物组，作为该 archive 必需责任者字段的依赖。"
        "S5 从 Haskell 原书为三张 archive 卡新增19条 source_backed 字段；不新增外部核验。九条直接 `cites` 候选逐条判为 formal，"
        "映射到三条关系记录；被引文献及页码均未独立查阅。Lanckoronska 与 Baldinucci 责任者形式保留其身份未决边界；不新增作者关系。"
        f"批次后 S4 为{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['new_groups'])}组、{sync.fmt(totals['registered_members'])}/{sync.fmt(totals['new_candidates'])}条映射；"
        f"S6关系表共{len(planned_relations):,}条。逐条证据见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。\n"
    )
    date_marker = "更新日期：2026-10-20。\n"
    assert date_marker in updated_result
    updated_result = updated_result.replace(date_marker, date_marker + "\n" + batch_result + "\n", 1)

    direct_groups, direct_candidates, direct_members, direct_types = summarize_relation_endpoint_queue(
        candidates, planned_alignment, planned_manifest, statements
    )
    archive_direct_groups, archive_direct_members = direct_types.get("archive", (0, 0))
    process_note = f"""

<a id="{ANCHOR}"></a>

### S4/S5/S6 archive：第3章与第7章书目引注端点批次（{DATE}）

按直接关系候选可解锁数、书内身份锚点和边界清晰度，登记三个直接 archive 组；Bonnaffé 的 S3 新人物组同时作为 archive 责任者字段依赖登记。批次脚本：[dry-run/apply](register_s4_s5_s6_archive_citations_20261020.py)。

**S4登记与身份边界：**

| 候选 | S3身份组 | KU | 依据与限制 |
|---|---|---|---|
| cand-5473 | archive-group-58e12013842e | `units/archives/lanckoronska-decoracja-gesu-1935` | 第21章p.427书目与第3章三条脚注；仅记录书目责任者形式“K. Lanckoronska”。人物候选 cand-10932 仍为 undecided，不扩写身份。|
| cand-5491 | archive-group-4d60e2987b4e | `units/archives/baldinucci-vita-padre-pozzo-ms-cod-palat-565` | 第3章p.88 n.5具名手稿及p.89、p.90回指；保留S0 OCR叶码“if. 120-42”。cand-5388所指 biographer 仍 undecided，不与 Filippo Baldinucci 合并，也不建立作者人物KU。|
| cand-7042 | archive-group-a26d5e573340 | `units/archives/bonnaffe-dictionnaire-amateurs-francais-1884` | 第21章p.416书目及第7章三条脚注；只登记 Haskell 的书目身份与引文范围。|
| cand-7043 | new-person:bonnaffe-edmond-a247874362 | `units/persons/edmond-bonnaffe` | 沿用 S3 全名新组，按第21章p.416书目责任者形式登记 source-local 人物卡；不补传记或外部身份。本批不从 relation_candidate=false 的书目行新增 authored_by 边。|

**S5定向字段：** 三张 archive 卡的书目类型、原题、书目责任者形式、出版项或手稿馆藏定位、Haskell引文范围共19条字段写入 `enrichment.jsonl`。字段均由 Haskell 原书锚点支持；OCR异文、责任者未决状态和“未读原件／被引页”限制随字段及卡片保留。未新增来源记录或外部核验。

**S6逐条裁决：** 九条直接引用候选均符合 archive→archive 的 `cites` 类型和值域；每条分别保留原句、脚注位置和关系映射。被引内容未核实，裁决只确认 Haskell 的书目引注。

| statement_id | 端点 | 原书定位 | 裁决 |
|---|---|---|---|
| st-chp3-seciv-notes-l189-204-p82-n3-lanckoronska | Haskell → Lanckoronska 1935 archive | 第3章p.82 n.3，L203 | formal，rel-{next_relation_id - 3:04d} `cites`；脚注明示由该书推导图像解释，只记录引注。|
| st-chp3-seciv-notes-l205-243-p83-n2-lanckoronska | Haskell → Lanckoronska 1935 archive | 第3章p.83 n.2，L206 | formal，同映射 rel-{next_relation_id - 3:04d}；简写引用由相邻完整题录唯一识别。|
| st-chp3-seciv-notes-l205-243-p84-n1-lanckoronska | Haskell → Lanckoronska 1935 archive | 第3章p.84 n.1，L207 | formal，同映射 rel-{next_relation_id - 3:04d}；脚注简写回指同一出版物。|
| st-chp3-seciv-notes-l205-243-p88-n5-baldinucci-ms | Haskell → Baldinucci manuscript archive | 第3章p.88 n.5，L232 | formal，rel-{next_relation_id - 2:04d} `cites`；明确著录手稿、馆藏号及叶码转录。|
| st-chp3-seciv-notes-l205-243-p89-n3-baldinucci-citation | Haskell → Baldinucci manuscript archive | 第3章p.89 n.3，L235 | formal，同映射 rel-{next_relation_id - 2:04d}；“MS. cit.”回指p.88 n.5。|
| st-chp3-seciv-notes-l205-243-p90-n2-baldinucci-ms | Haskell → Baldinucci manuscript archive | 第3章p.90 n.2，L238 | formal，同映射 rel-{next_relation_id - 2:04d}；“MS. cit.”回指同一手稿。|
| st-chp7-p175-n2-cite-bonnaffe | Haskell → Bonnaffé 1884 archive | 第7章p.175 n.2，L313 | formal，rel-{next_relation_id - 1:04d} `cites`；书目唯一识别该书。|
| st-chp7-p184-n4-cite-bonnaffe | Haskell → Bonnaffé 1884 archive | 第7章p.184 n.4，L357 | formal，同映射 rel-{next_relation_id - 1:04d}；多来源脚注只将 Bonnaffé 部分计为该边证据。|
| st-chp7-p187-n1-cite-bonnaffe | Haskell → Bonnaffé 1884 archive | 第7章p.187 n.1，L362 | formal，同映射 rel-{next_relation_id - 1:04d}；书目责任与题名可对应。|

三组 archive 登记后，S4 已登记{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['new_groups'])}组、{sync.fmt(totals['registered_members'])}/{sync.fmt(totals['new_candidates'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组／{sync.fmt(totals['pending_members'])}条映射。直接关系端点待登记{direct_groups}组／{direct_candidates}个候选／{direct_members}条成员映射，其中 archive {archive_direct_groups}组／{archive_direct_members}成员；非直接待登记{totals['pending_groups'] - direct_groups}组／{totals['pending_members'] - direct_members}条映射。KU={len(planned_manifest)}；S6关系表{len(planned_relations)}条（{sum(r['status'] == 'formal' for r in planned_relations)} formal、{sum(r['status'] == 'pending' for r in planned_relations)} pending）；本过程累计逐条裁决70条 S2 关系候选（42 formal、23 pending、5 rejected）。S5字段表{11738 + len(new_field_rows):,}条，其中1,625条unverified。非直接字段责任者和未决人物仍按其原S3状态保留。
"""
    updated_process = process_text.rstrip() + process_note

    current_snapshot = (
        f"项目版本为初始化阶段的 0.1.0；全书 S2 内部处理已完成，尚未独立语义验收。当前快照（2026-10-20）：S2 共15,164条statement（relation_candidate=true 10,401），其中333条至少缺一个candidate端点ID（仅缺subject 43、仅缺object 218、两端均缺72）；统一计入口径的独立逐条复核为9,394/15,164（61.9%），第七章1,008/1,238、第八章482/1,462，均未接收；另有第3章1,173/1,174和第10–12章1,567/1,567的独立章节复核记录，均未接收且不并入统一口径。S3决定记录覆盖12,408/12,408个候选：same=2,024（指向1,092个既有KU）、new=5,029（{sync.fmt(totals['new_groups'])}个身份组）、conflict=9、excluded=100、undecided=5,246（其中622项类型未决）；决定覆盖齐全不表示冲突和待证身份已解决。S4已登记{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['new_groups'])}组、{sync.fmt(totals['registered_members'])}/{sync.fmt(totals['new_candidates'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组／{sync.fmt(totals['pending_members'])}条映射。直接关系端点待登队列为{direct_groups:,}组／{direct_candidates:,}个端点候选／{direct_members:,}条组成员映射（person 2／2、institution 90／90、event 101／101、place 224／224、work 319／328、archive {archive_direct_groups}／{archive_direct_members}、term 525／525），另有{totals['pending_groups'] - direct_groups:,}组／{totals['pending_members'] - direct_members:,}条非直接映射待登记。S6关系表有1,269条记录（1,267 formal、2 pending），原45条待回补记录均已绑定结构化source_id；过程记录累计逐条裁决70条S2候选（42 formal、23 pending、5 rejected），不代表S2关系候选全量收口。S5字段表11,757条、其中1,625条unverified；S5、S6尚未全书收口。知识发现与页面暂停。有效对象见 [accepted.yml](04-knowledge/accepted.yml)；遗留文件与未处理来源不自动成为成果。"
    )
    agents_text, snapshot_count = re.subn(r"(?m)^项目版本为初始化阶段的 0\.1\.0；.*$", current_snapshot, AGENTS_PATH.read_text(encoding="utf-8-sig"), count=1)
    assert snapshot_count == 1

    if args.dry_run:
        print("dry-run passed: 4 single-member S3 groups map to 4 new KU cards (3 archive, 1 person dependency)")
        print(f"verified source quotes: {sum(len(s.get('quotes', [s.get('quote', '')])) for spec in SPECS for s in spec['sources']) + 1} across ch. 3, ch. 7, and ch. 21")
        print(f"S6 citation candidates: {len(cited_ids)} formal decisions -> {len(new_relation_rows)} citation edges; all endpoints and source_id resolve")
        print(f"S5 fields: {len(new_field_rows)} source_backed rows; enrichment {11738}->{11738 + len(new_field_rows)}")
        print(f"S4 registered {totals['registered_groups']}/{totals['new_groups']} groups, {totals['registered_members']}/{totals['new_candidates']} mappings; pending {totals['pending_groups']}/{totals['pending_members']}")
        print(f"direct endpoint queue after plan: {direct_groups} groups / {direct_candidates} candidates / {direct_members} member mappings")
        print("planned writes: 4 cards; accepted.yml; manifest; 4 alignment mappings; relations.csv; enrichment.jsonl; process/result/AGENTS snapshots")
        return 0

    for path, content in card_contents.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    write_csv_preserving_bom(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv_preserving_bom(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    write_csv_preserving_bom(RELATIONS_PATH, relation_fields, planned_relations)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    with ENRICHMENT_PATH.open("a", encoding="utf-8", newline="\n") as handle:
        for row in new_field_rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    PROCESS_PATH.write_text(updated_process, encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(updated_result.rstrip() + "\n", encoding="utf-8", newline="\n")
    AGENTS_PATH.write_text(agents_text, encoding="utf-8", newline="\n")
    print(f"applied: 4 KU cards; S4 registered={totals['registered_groups']}/{totals['new_groups']} groups, pending={totals['pending_groups']}/{totals['pending_members']} mappings")
    print(f"S6: {len(cited_ids)} formal citation decisions, {len(new_relation_rows)} relation rows; S5: {len(new_field_rows)} source_backed rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(apply())
