#!/usr/bin/env python3
"""Register the chapter 8 Longhi article and four named Vannini works.
Default mode previews the bounded update; pass --apply to write it.
"""
from __future__ import annotations

import argparse
import csv
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
KNOWLEDGE = ROOT / "04-knowledge"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch8-p212-vannini-longhi-article-20261028"
TASK = "patrons-and-painters-full-book-s2"
SOURCE = "haskell-1980-rev-ed"
MAIN_STATEMENT = "st-chp8-p212-four-scenes-made-for-house-and-considered-finest"
PUBLICATION_STATEMENT = "st-chp8-p212-n2-longhi-publishes-vannini-scenes"
PACECO_STATEMENT = "st-chp8-p213-n1-longhi-publication"
BIB_STATEMENT = "st-chp21-bib-l701-754-entry-03"
SEGMENT_MAIN = "chp-8:08_CHP-8_sec_i:l98-106"
SEGMENT_NOTE = "chp-8:08_CHP-8_sec_i:l126-157"
SEGMENT_BIB = "chp-21:21_CHP-21Bibliography:l701-754"
CHP8 = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
BIB = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
MAIN_QUOTE = "the four large scenes from the Old Testament—\nThe Sacrifice of Isaac, The Fall of Manna, Moses striking the Rock and Susanna and the Elders—which he produced for the house"
PUB_QUOTE = "Two of the pictures—The Fäll of Manna and Moses striking the Rock—are published by R. Longhi, 1956, in an article on the del Rosso collection."
BIB_QUOTE = "Paragone,\nLonghi, R.: ‘Un collezionista di pittura napoletana nella Firenze del ’600’ in 75,\n1956, pp. 61-64."
ARCHIVE_ID = "units/archives/longhi-un-collezionista-pittura-napoletana-firenze-seicento-1956"
ARCHIVE_SLUG = "longhi-un-collezionista-pittura-napoletana-firenze-seicento-1956"
ARTICLE_TITLE_ZH = "《十七世纪佛罗伦萨的一位那不勒斯绘画收藏家》"
ARTICLE_TITLE_EN = "A Collector of Neapolitan Painting in Seventeenth-Century Florence"
ARTICLE_ORIGINAL = "Un collezionista di pittura napoletana nella Firenze del ’600"

WORKS = [
    {
        "candidate": "cand-7528",
        "alignment": "aln-7704",
        "ku": "units/works/vannini-sacrifice-of-isaac-del-rosso-house",
        "slug": "vannini-sacrifice-of-isaac-del-rosso-house",
        "name_zh": "《以撒献祭》",
        "name_en": "The Sacrifice of Isaac",
        "statement": "st-chp8-p212-sacrifice-of-isaac-created-by-vannini",
        "characteristic": "《以撒献祭》",
        "publication": False,
    },
    {
        "candidate": "cand-7529",
        "alignment": "aln-7705",
        "ku": "units/works/vannini-fall-of-manna-del-rosso-house",
        "slug": "vannini-fall-of-manna-del-rosso-house",
        "name_zh": "《玛纳降下》",
        "name_en": "The Fall of Manna",
        "statement": "st-chp8-p212-fall-of-manna-created-by-vannini",
        "characteristic": "《玛纳降下》",
        "publication": True,
    },
    {
        "candidate": "cand-7530",
        "alignment": "aln-7706",
        "ku": "units/works/vannini-moses-striking-rock-del-rosso-house",
        "slug": "vannini-moses-striking-rock-del-rosso-house",
        "name_zh": "《摩西击石》",
        "name_en": "Moses striking the Rock",
        "statement": "st-chp8-p212-moses-striking-rock-created-by-vannini",
        "characteristic": "《摩西击石》",
        "publication": True,
    },
    {
        "candidate": "cand-7531",
        "alignment": "aln-7707",
        "ku": "units/works/vannini-susanna-and-elders-del-rosso-house",
        "slug": "vannini-susanna-and-elders-del-rosso-house",
        "name_zh": "《苏撒纳与长老》",
        "name_en": "Susanna and the Elders",
        "statement": "st-chp8-p212-susanna-and-elders-created-by-vannini",
        "characteristic": "《苏撒纳与长老》",
        "publication": False,
    },
]

def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)

def line_ending(path: Path) -> str:
    raw = path.read_bytes()
    return "\r\n" if b"\r\n" in raw else "\n"

def write_csv(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator=line_ending(path))
        writer.writeheader()
        writer.writerows(rows)

def change_row(rows, key, value, updates, label):
    matches = [row for row in rows if row.get(key) == value]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {label} row for {value}; found {len(matches)}")
    matches[0].update(updates)
    return matches[0]

def source_citation():
    return "Francis Haskell, Patrons and Painters, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."

def quote_yaml(value):
    return json.dumps(value, ensure_ascii=False)

def work_card(work):
    cite = source_citation()
    extra_source = ""
    extra_reading = ""
    if work["publication"]:
        extra_source = f"""
  - citation: "{cite}"
    location: "第8章；印刷页212注2；Markdown L150；PDF物理页10。"
    sentence_summary: "Haskell称{work['name_en']}由R. Longhi发表于1956年关于Del Rosso收藏的文章；该文未独立查阅。"
    original_quotes:
      - source_span: "line 150; printed p.212 n.2; PDF physical p.10"
        text: {quote_yaml(PUB_QUOTE)}
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {CHP8}
      source_span: "line 150; printed p.212 n.2; PDF physical p.10"
"""
        extra_reading = f" Haskell also reports that this picture was published in R. Longhi's 1956 article; that article was not independently consulted."
    return f"""---
title: {quote_yaml(work['name_zh'] + '（' + work['name_en'] + '）')}
name_en: {quote_yaml(work['name_en'])}
type: work
sub_type: painting
evidence_status: source_backed
sources:
  - citation: "{cite}"
    location: "第8章；印刷页212；来源文件L100–101；PDF物理页10。"
    sentence_summary: "Haskell将{work['name_en']}列为Ottavio Vannini为Del Rosso家族住宅制作的四幅大型旧约场景之一。"
    original_quotes:
      - source_span: "lines 100–101; printed p.212; PDF physical p.10"
        text: {quote_yaml(MAIN_QUOTE)}
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {CHP8}
      source_span: "lines 100–101; printed p.212; PDF physical p.10"
{extra_source}created: "2026-10-28"
updated: "2026-10-28"
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 本卡记录Haskell列出的{work['name_en']}。Haskell称其属于Ottavio Vannini为Del Rosso家族住宅制作的四幅大型旧约场景，并将四幅作品称为Vannini最出色的作品；本卡将作者归属限定为Haskell的书内表述，不表示独立作品目录或实物已核验。{extra_reading}来源未给出现今位置或可确认的存世版本。

**English:** This card records Haskell's named {work['name_en']}. He identifies it as one of four large Old Testament scenes produced by Ottavio Vannini for the Del Rosso family house and describes the four as among Vannini's finest works. The attribution is limited to Haskell's account; no independent catalogue or surviving object has been verified.{extra_reading} The source gives no present location or identifiable surviving version.

### 名称与书内范围

| 字段 | 值 | 依据 |
|---|---|---|
| 来源所用名称 | {work['name_en']} | 第8章 p.212，L100–101 |
| 题名性质 | Haskell的描述性作品名称；未核实为原题 | 第8章 p.212，L100–101 |
| 作品类型 | 大型旧约场景（Haskell原文） | 第8章 p.212，L100–101 |
| 来源所述创作者 | Ottavio Vannini；Haskell称由其制作 | 第8章 p.212，L100–101 |
| 来源所述委托／使用语境 | 为Del Rosso家族住宅制作；不据此推定具体委托人或产权 | 第8章 p.212，L100–101 |

## 关系与证据

### 关系记录

请见下方由S6关系表生成的正式关系投影。创作者边仅记录Haskell的书内归属。{("论文收录边仅记录Haskell称该画发表于Longhi论文，不确认具体图版或论文正文。" if work["publication"] else "本批没有为该画推定与Longhi论文的关系。")}

### 身份与边界

本对象对应S3身份组及候选 {work['candidate']}；仅按Haskell第8章p.212的独立作品称名登记。它与另外三幅场景分开。作品组合候选cand-7527仍未被登记为单一知识元；不推定原题、现藏地或作品版本。

### 关系候选入口

[身份、来源字段与关系裁决过程](../../../{PROCESS_REF.replace('03-processing/', '03-processing/')})
"""

def archive_card():
    cite = source_citation()
    return f"""---
title: {quote_yaml(ARTICLE_TITLE_ZH + "（" + ARTICLE_TITLE_EN + "）")}
name_en: {quote_yaml(ARTICLE_TITLE_EN)}
type: archive
sub_type: journal article; Haskell bibliography record
evidence_status: source_backed
sources:
  - citation: "{cite}"
    location: "第21章书目；印刷页428；Markdown L707–709。"
    sentence_summary: "书目列出R. Longhi的题名、Paragone、75、1956及页码61–64；论文未独立查阅。"
    original_quotes:
      - source_span: "lines 707–709; printed p.428"
        text: {quote_yaml(BIB_QUOTE)}
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {BIB}
      source_span: "lines 707–709; printed p.428"
  - citation: "{cite}"
    location: "第8章；印刷页212注2；Markdown L150；PDF物理页10。"
    sentence_summary: "Haskell称两幅Vannini场景由R. Longhi发表于1956年关于Del Rosso收藏的文章。"
    original_quotes:
      - source_span: "line 150; printed p.212 n.2; PDF physical p.10"
        text: {quote_yaml(PUB_QUOTE)}
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {CHP8}
      source_span: "line 150; printed p.212 n.2; PDF physical p.10"
  - citation: "{cite}"
    location: "第8章；印刷页213注1；Markdown L154。"
    sentence_summary: "Haskell称Paceco de Rosa的画由R. Longhi发表于1956年；具体作品未具名。"
    original_quotes:
      - source_span: "line 154; printed p.213 n.1"
        text: "the latter are published by R. Longhi, 1956."
    evidence_ref:
      doc_id: patrons-and-painters
      source_file: {CHP8}
      source_span: "line 154; printed p.213 n.1"
created: "2026-10-28"
updated: "2026-10-28"
process_ref: {PROCESS_REF}
---

## 内容

### 描述

**中文：** 本卡登记Haskell第21章书目所列的Longhi期刊论文。中英文显示名为对意大利语原题的描述性工作译名，原题另行照录。哈斯克尔第8章注释称若干Del Rosso收藏的画发表于该文；论文全文与被引内容均未独立查阅。作者形式“Longhi, R.”按S3身份裁决映射至Roberto Longhi。

**English:** This unit records the Longhi journal article listed in Haskell's chapter 21 bibliography. The bilingual display title is a descriptive working translation of the Italian original, which is retained below. Haskell's chapter 8 notes say that certain paintings from the Del Rosso collection were published in the article; neither the article nor its cited contents was independently consulted. The author form “Longhi, R.” maps to Roberto Longhi under the existing S3 identity decision.

### 书目身份与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 文献类型 | 期刊论文；Haskell书目记录 | 第21章印刷页428，L707–709 |
| 原题名 | {ARTICLE_ORIGINAL} | 第21章印刷页428，L708 |
| 作者（书目署名） | Roberto Longhi（书目形式：Longhi, R.；按S3映射） | 第21章印刷页428，L708–709 |
| 期刊 | Paragone | 第21章印刷页428，L707 |
| 卷／期标记 | 75（照录书目；未另行区分卷号与期号） | 第21章印刷页428，L708 |
| 出版年 | 1956 | 第21章印刷页428，L709 |
| 页码 | 61–64 | 第21章印刷页428，L709 |
| 查阅状态 | 本批仅核对Haskell书目和注释；论文未独立查阅 | 第8章p.212注2及p.213注1 |

## 关系与证据

### 关系记录

正式关系由S6关系表维护并投影；作者边仅记录书目署名。第8章注2明确将《玛纳降下》和《摩西击石》与该论文相连；第8章注1所称Paceco de Rosa画作没有具名作品端点，继续待证，不建立泛化作品组。

### 身份边界

本KU对应S3身份组archive-group-3378e0841547及候选cand-7604。身份范围限于Haskell所指的期刊论文书目记录；不声称查阅论文，也不将论文中的内容或作品归属当作已独立核实事实。

### 身份与关系过程

[本批身份、字段与关系裁决过程](../../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s3-s4-s5-s6-ch8-p212-vannini-longhi-article-20261028)
"""

def make_creator_statement(base, work):
    row = deepcopy(base)
    row["statement_id"] = work["statement"]
    row["subject_candidate_id"] = work["candidate"]
    row["object_candidate_id"] = "cand-2694"
    row["predicate"] = "created_by"
    q = row["qualifiers"]
    for key in ("footnote_numbers", "footnote_marker", "footnote_segment", "footnote_statement_ids",
                "linked_body_statement_ids", "footnote_refs", "footnote_number"):
        q.pop(key, None)
    q.update({
        "source_line_start": 100,
        "source_line_end": 101,
        "printed_page": 212,
        "pdf_physical_page": 10,
        "claim": f"Haskell says {work['name_en']} was one of four large Old Testament scenes produced by Ottavio Vannini for the Del Rosso house.",
        "speaker": "Haskell",
        "text_layer": "body",
        "qualification": "Records Haskell's source-attributed creator statement only; no independent attribution verification or present-location claim is made.",
        "mentioned_candidate_ids": [work["candidate"], "cand-2694"],
        "relation_candidate": True,
        "relation_candidate_note": "The plural clause 'which he produced for the house' applies to each of the four separately named scene candidates; this statement isolates one work-to-creator attribution for S6."
    })
    row["claim"] = q["claim"]
    row["qualification"] = q["qualification"]
    row["mentioned_candidate_ids"] = q["mentioned_candidate_ids"]
    return row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply the reviewed, bounded update")
    args = parser.parse_args()

    paths = {
        "statements": TABLES / "book-statements.jsonl",
        "mentions": TABLES / "mentions.csv",
        "alignment": TABLES / "alignment.csv",
        "candidates": TABLES / "entity-candidates.csv",
        "manifest": TABLES / "ku-manifest.csv",
        "relations": TABLES / "relations.csv",
        "accepted": KNOWLEDGE / "accepted.yml",
    }
    for path in [*paths.values(), KNOWLEDGE / "units"]:
        if not path.exists():
            raise FileNotFoundError(path)

    statements = [json.loads(line) for line in paths["statements"].read_text(encoding="utf-8").splitlines() if line]
    ids = [row["statement_id"] for row in statements]
    if len(ids) != len(set(ids)):
        raise ValueError("current book-statements.jsonl contains duplicate IDs")

    by_id = {row["statement_id"]: row for row in statements}
    required_ids = [MAIN_STATEMENT, PUBLICATION_STATEMENT, PACECO_STATEMENT, BIB_STATEMENT]
    if any(sid not in by_id for sid in required_ids):
        raise ValueError("one or more expected S2 source statements are missing")
    new_statement_ids = [work["statement"] for work in WORKS] + ["st-chp8-p212-moses-striking-rock-published-in-longhi"]
    if set(ids) & set(new_statement_ids):
        raise ValueError("one or more proposed S2 statement IDs already exist")

    # Candidate and alignment preconditions: preserve all five current S3 new decisions.
    align_fields, alignment = read_csv(paths["alignment"])
    candidate_fields, candidates = read_csv(paths["candidates"])
    s4_specs = [
        ("cand-7604", "aln-7780", ARCHIVE_ID, "archive"),
        *[(w["candidate"], w["alignment"], w["ku"], "work") for w in WORKS],
    ]
    for candidate_id, alignment_id, ku_id, expected_type in s4_specs:
        row = next((r for r in alignment if r["alignment_id"] == alignment_id), None)
        if not row or row["candidate_id"] != candidate_id or row["decision"] != "new" or row["ku_id"]:
            raise ValueError(f"S3 new/unmapped precondition failed for {candidate_id}")
        if (KNOWLEDGE / f"{ku_id}.md").exists():
            raise ValueError(f"card already exists: {ku_id}.md")
        if any(r["ku_id"] == ku_id for r in alignment):
            raise ValueError(f"KU already mapped: {ku_id}")
        candidate = next((r for r in candidates if r["candidate_id"] == candidate_id), None)
        if not candidate or candidate["suggested_type"] != expected_type:
            raise ValueError(f"candidate type mismatch for {candidate_id}")

    # Revise the group statement to preserve Haskell's evaluation without treating an unresolved group as a KU edge.
    group = by_id[MAIN_STATEMENT]
    group["predicate"] = "four_vannini_scenes_considered_among_his_finest_works"
    group["qualifiers"]["claim"] = "Haskell reports that the four named scenes were considered Vannini's finest works."
    group["qualifiers"]["qualification"] = "This preserves Haskell's evaluative report about the four-scene group; it does not assert an external ranking or a separately identified group object."
    group["qualifiers"]["relation_candidate"] = False
    group["qualifiers"].pop("relation_candidate_note", None)
    group["claim"] = group["qualifiers"]["claim"]
    group["qualification"] = group["qualifiers"]["qualification"]

    creator_rows = [make_creator_statement(group, work) for work in WORKS]
    main_idx = next(i for i, row in enumerate(statements) if row["statement_id"] == MAIN_STATEMENT)
    statements[main_idx + 1:main_idx + 1] = creator_rows

    # Atomize the p.212 footnote's two explicitly named picture/article edges.
    pub = by_id[PUBLICATION_STATEMENT]
    pub["subject_candidate_id"] = "cand-7604"
    pub["object_candidate_id"] = "cand-7529"
    pub["predicate"] = "has_subject"
    pubq = pub["qualifiers"]
    pubq["claim"] = "Haskell says The Fall of Manna was published by R. Longhi in the 1956 article on the Del Rosso collection."
    pubq["qualification"] = "The printed page reads 'Fall' (the OCR reads 'Fäll'). This records Haskell's report that the article includes this work; the article was not independently read and no specific reproduction or plate is asserted."
    pubq["relation_candidate_note"] = "The statement is oriented as article to work for the controlled has_subject relation; the scope is limited to Haskell's report that this named picture was published in the article."
    pub["claim"] = pubq["claim"]
    pub["qualification"] = pubq["qualification"]
    second_pub = deepcopy(pub)
    second_pub["statement_id"] = "st-chp8-p212-moses-striking-rock-published-in-longhi"
    second_pub["subject_candidate_id"] = "cand-7604"
    second_pub["object_candidate_id"] = "cand-7530"
    second_pub["qualifiers"]["claim"] = "Haskell says Moses striking the Rock was published by R. Longhi in the 1956 article on the Del Rosso collection."
    second_pub["qualifiers"]["qualification"] = pubq["qualification"]
    second_pub["claim"] = second_pub["qualifiers"]["claim"]
    second_pub["qualification"] = second_pub["qualifiers"]["qualification"]
    second_pub["qualifiers"]["mentioned_candidate_ids"] = ["cand-7530", "cand-7603", "cand-7604", "cand-7489"]
    second_pub["mentioned_candidate_ids"] = second_pub["qualifiers"]["mentioned_candidate_ids"]
    pub_idx = next(i for i, row in enumerate(statements) if row["statement_id"] == PUBLICATION_STATEMENT)
    statements.insert(pub_idx + 1, second_pub)

    # Retain the p.213 publication report, but leave the unnamed picture-group endpoint explicitly open.
    paceco = by_id[PACECO_STATEMENT]
    paceco["subject_candidate_id"] = None
    paceco["object_candidate_id"] = "cand-7604"
    paceco["predicate"] = "has_subject"
    pq = paceco["qualifiers"]
    pq["claim"] = "Haskell says the Paceco de Rosa pictures (the latter, not all artists just named) were published by R. Longhi in 1956."
    pq["qualification"] = "The bibliography identifies the cited article but it was not independently read. Haskell does not name or enumerate the individual Paceco de Rosa pictures here."
    pq["open_endpoint_reason"] = "The source refers collectively to unnamed Paceco de Rosa pictures without titles, count, or a bounded work-group identity. Candidate cand-2235 is the artist, not the paintings; do not create a work-group KU unless a source identifies a stable object or set."
    pq["relation_candidate_note"] = "Keep as an open S2 relation candidate with the article mapped but no identified work endpoint; S6 remains process-only pending until a stable work endpoint and a supported relation can be established."
    paceco["claim"] = pq["claim"]
    paceco["qualification"] = pq["qualification"]

    # Convert the bibliography entry into the explicit article authorship relation candidate.
    bib = by_id[BIB_STATEMENT]
    bib["subject_candidate_id"] = "cand-7604"
    bib["object_candidate_id"] = "cand-7603"
    bib["predicate"] = "authored_by"
    bq = bib["qualifiers"]
    bq["claim"] = "Haskell's bibliography lists the 1956 Paragone article under Longhi, R.; the current S3 identity decision maps R. Longhi to Roberto Longhi."
    bq["relation_candidate"] = True
    bq["mentioned_candidate_ids"] = ["cand-7604", "cand-7603"]
    bq["text_layer"] = "bibliographic entry"
    bq["qualification"] = "The author form is bibliographic attribution only. The article and its cited contents were not independently consulted."
    bq["relation_candidate_note"] = "The printed bibliography directly attributes this journal article to Longhi, R.; S3 maps the initials form to the existing Roberto Longhi KU. This supports archive authored_by person without confirming article contents."
    bib["claim"] = bq["claim"]
    bib["qualification"] = bq["qualification"]
    bib["mentioned_candidate_ids"] = bq["mentioned_candidate_ids"]

    # Add individual creator relation candidates adjacent to the existing group statement.
    # (The group statement remains a non-relation evaluative claim.)
    if len([s for s in statements if s.get("statement_id") in new_statement_ids]) != len(new_statement_ids):
        raise ValueError("new S2 statements did not materialize exactly once")

    mentions_fields, mentions = read_csv(paths["mentions"])
    author_mention_id = "m-chp21-bib-l701-754-003-longhi-author"
    if any(r["mention_id"] == author_mention_id for r in mentions):
        raise ValueError(f"mention already exists: {author_mention_id}")
    article_mention = next((r for r in mentions if r["mention_id"] == "m-chp21-bib-l701-754-003"), None)
    if not article_mention or article_mention["candidate_id"] != "cand-7604":
        raise ValueError("expected article mention not found")
    full_span = article_mention["surface_form"]
    title_form = "‘Un collezionista di pittura napoletana nella Firenze del ’600’"
    if title_form not in full_span or "Longhi, R." not in full_span:
        raise ValueError("bibliography mention no longer contains expected title and author")
    span_start = int(article_mention["start_char"])
    author_start = span_start + full_span.index("Longhi, R.")
    title_start = span_start + full_span.index(title_form)
    article_mention.update({
        "surface_form": title_form,
        "start_char": str(title_start),
        "end_char": str(title_start + len(title_form)),
        "note": "Exact journal-article title in the bibliography entry; author is separately annotated."
    })
    mentions.append({
        "mention_id": author_mention_id,
        "segment_id": SEGMENT_BIB,
        "candidate_id": "cand-7603",
        "surface_form": "Longhi, R.",
        "start_char": str(author_start),
        "end_char": str(author_start + len("Longhi, R.")),
        "note": "Bibliographic author form for cand-7604; S3 maps the R. Longhi identity to Roberto Longhi."
    })

    manifest_fields, manifest = read_csv(paths["manifest"])
    if any(r["ku_id"] == ARCHIVE_ID for r in manifest):
        raise ValueError(f"manifest already contains {ARCHIVE_ID}")
    for work in WORKS:
        if any(r["ku_id"] == work["ku"] for r in manifest):
            raise ValueError(f"manifest already contains {work['ku']}")
    manifest.append({
        "ku_id": ARCHIVE_ID,
        "type": "archive",
        "canonical_name": ARTICLE_TITLE_ZH,
        "name_en": ARTICLE_TITLE_EN,
        "source_task": TASK,
        "card_path": f"04-knowledge/units/archives/{ARCHIVE_SLUG}.md",
    })
    for work in WORKS:
        manifest.append({
            "ku_id": work["ku"],
            "type": "work",
            "canonical_name": work["name_zh"],
            "name_en": work["name_en"],
            "source_task": TASK,
            "card_path": f"04-knowledge/units/works/{work['slug']}.md",
        })

    # Seven natural-key-unique formal S6 edges: author, four creator attributions, two article subject links.
    rel_fields, relations = read_csv(paths["relations"])
    rel_specs = [
        {
            "subject_ku_id": ARCHIVE_ID,
            "object_ku_id": "units/persons/roberto-longhi",
            "predicate": "authored_by",
            "time": "",
            "role": "书目作者署名Longhi, R.；S3身份映射至Roberto Longhi",
            "scope": "仅记录Haskell书目将该期刊论文署名为Longhi, R.；按S3身份决定映射至Roberto Longhi。论文正文及所引内容未独立查阅。",
            "source_span": "Chapter 21, printed p.428, lines 707–709; statement=" + BIB_STATEMENT,
            "source_file": BIB,
            "note": "书目署名为直接证据；S3只解决作者身份，不据此确认论文内容。",
        },
        *[
            {
                "subject_ku_id": work["ku"],
                "object_ku_id": "units/persons/ottavio-vannini",
                "predicate": "created_by",
                "time": "",
                "role": "Haskell所述创作者",
                "scope": f"仅记录Haskell称{work['name_en']}为Ottavio Vannini为Del Rosso家族住宅制作的四幅大型旧约场景之一；不表示外部归属核验、具体委托关系、存世版本或现今地点。",
                "source_span": "Chapter 8, printed p.212, lines 100–101; statement=" + work["statement"],
                "source_file": CHP8,
                "note": "原文的which he produced适用于四幅分别列名的场景；本边限于Haskell的书内归属。",
            }
            for work in WORKS
        ],
        *[
            {
                "subject_ku_id": ARCHIVE_ID,
                "object_ku_id": work["ku"],
                "predicate": "has_subject",
                "time": "",
                "role": "Haskell称该画发表于Longhi 1956年论文",
                "scope": f"仅记录Haskell称{work['name_en']}发表于关于Del Rosso收藏的Longhi 1956年文章；论文未独立查阅，不据此断言特定图版、复制版本或作品归属。",
                "source_span": "Chapter 8, printed p.212 n.2, line 150; statement=" + (
                    PUBLICATION_STATEMENT if work["candidate"] == "cand-7529"
                    else "st-chp8-p212-moses-striking-rock-published-in-longhi"
                ),
                "source_file": CHP8,
                "note": "关系只复述Haskell的出版说明；不声称已查看该文章。",
            }
            for work in WORKS if work["publication"]
        ],
    ]
    last_rel = max(int(r["relation_id"].split("-")[1]) for r in relations)
    for index, spec in enumerate(rel_specs, start=1):
        natural_key = (
            spec["subject_ku_id"], spec["object_ku_id"], spec["predicate"],
            spec["time"], spec["role"], spec["scope"],
        )
        if any((
            r["subject_ku_id"], r["object_ku_id"], r["predicate"], r["time"], r["role"], r["scope"]
        ) == natural_key for r in relations):
            raise ValueError(f"formal relation natural key already exists for {spec}")
        relations.append({
            "relation_id": f"rel-{last_rel + index:04d}",
            **spec,
            "origin": "book",
            "status": "formal",
            "source_id": SOURCE,
        })

    # Update all five S4 mappings and refresh the one article candidate detail.
    process_root = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md"
    s4_resolutions = [
        ("cand-7604", "aln-7780", ARCHIVE_ID, "archive-group-3378e0841547", "新建archive KU；仅登记Haskell书目记录及书内引文，不声称查阅论文。"),
        *[(w["candidate"], w["alignment"], w["ku"], f"既有S3 new身份组 {next((r['resolution_note'].split('group=')[1].split(';')[0] for r in alignment if r['alignment_id']==w['alignment']), '见alignment.csv')}", "新建work KU；仅记录Haskell分别命名的旧约场景及书内作者归属。") for w in WORKS],
    ]
    for candidate_id, alignment_id, ku_id, group, explanation in s4_resolutions:
        row = next(r for r in alignment if r["alignment_id"] == alignment_id)
        row["ku_id"] = ku_id
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (row["resolution_note"].rstrip() + f" S4 registration (2026-10-28): {explanation} process_ref={PROCESS_REF}.")
    article_candidate = next(r for r in candidates if r["candidate_id"] == "cand-7604")
    article_candidate["detail"] = "Haskell's chapter 21 bibliography records the article title, journal, 1956 date, pages and author form Longhi, R. Chapter 8 cites it. S3 maps R. Longhi to the existing Roberto Longhi KU. The article itself was not consulted."

    # Register only these five fixed units in accepted.yml; preserve YAML structure and ordering.
    accepted_text = paths["accepted"].read_text(encoding="utf-8")
    accepted_paths = [f"04-knowledge/units/archives/{ARCHIVE_SLUG}.md"] + [
        f"04-knowledge/units/works/{w['slug']}.md" for w in WORKS
    ]
    for card_path in accepted_paths:
        if card_path in accepted_text:
            raise ValueError(f"accepted.yml already contains {card_path}")
    insertion = "".join(f"- {card_path}\n" for card_path in accepted_paths)
    if "\nclaims:\n" not in accepted_text:
        raise ValueError("accepted.yml claims section not found")
    accepted_text = accepted_text.replace("\nclaims:\n", "\n" + insertion + "claims:\n", 1)

    card_files = {
        KNOWLEDGE / "units" / "archives" / f"{ARCHIVE_SLUG}.md": archive_card(),
        **{
            KNOWLEDGE / "units" / "works" / f"{w['slug']}.md": work_card(w)
            for w in WORKS
        },
    }
    for path, content in card_files.items():
        if path.exists():
            raise ValueError(f"card already exists: {path}")

    print("BATCH PREVIEW" if not args.apply else "APPLYING BATCH")
    print(f"S4: {len(s4_specs)} new KU mappings; article + {len(WORKS)} individual works")
    print(f"S2: {len(new_statement_ids)} new statements, one p.213 open endpoint, one author mention; independent-review count unchanged")
    print(f"S6 formal edges: {len(rel_specs)}; p.213 unnamed Paceco pictures remain process-only pending")
    print("Relations:")
    for row in rel_specs:
        print(f"  {row['subject_ku_id']} --{row['predicate']}--> {row['object_ku_id']}")
    print("New cards:")
    for path in card_files:
        print(f"  {path.relative_to(ROOT)}")

    if not args.apply:
        return

    # Save table updates after all semantic preconditions and natural-key checks pass.
    paths["statements"].write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in statements),
        encoding="utf-8",
        newline="",
    )
    write_csv(paths["mentions"], mentions_fields, mentions)
    write_csv(paths["alignment"], align_fields, alignment)
    write_csv(paths["candidates"], candidate_fields, candidates)
    write_csv(paths["manifest"], manifest_fields, manifest)
    write_csv(paths["relations"], rel_fields, relations)
    paths["accepted"].write_text(accepted_text, encoding="utf-8", newline="")
    for path, content in card_files.items():
        path.write_text(content, encoding="utf-8", newline="")
    print("Applied all S2/S4/S6 tables, accepted.yml, manifest and five cards.")

if __name__ == "__main__":
    main()

