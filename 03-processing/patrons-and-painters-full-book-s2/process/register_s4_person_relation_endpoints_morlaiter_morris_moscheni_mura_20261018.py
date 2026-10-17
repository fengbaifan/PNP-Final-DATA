from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
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
ANCHOR = "s4-person-relation-endpoints-morlaiter-morris-moscheni-mura-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


TARGETS = [
    {
        "candidate": "cand-1703", "group": "new-person:michelangelo-morlaiter-17d79e97ce",
        "ku": "units/persons/michelangelo-morlaiter", "card": "04-knowledge/units/persons/michelangelo-morlaiter.md",
        "name_zh": "米开朗基罗·莫莱特", "name_en": "Michelangelo Morlaiter",
        "index_entry": "M.csv#244", "index_name": "Morlaiter, Michelangelo", "page": "312",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "location": "第10章，印刷页312；OCR L19–20",
        "span": "lines 19–20; print p. 312", "quote": "sculpted by Corradini and Morlaiter",
        "summary": "Haskell称Schulenburg的肖像曾由Morlaiter雕塑；同页书后索引以“Morlaiter, Michelangelo”定位该人物。",
        "relation_ids": ["st-chp10-p312-morlaiter-sculpted-portraits-of"],
        "endpoints": [("st-chp10-p312-morlaiter-sculpted-portraits-of", "cand-1703", "cand-2401", "sculpted_portraits_of", "sculpted by Corradini and Morlaiter")],
        "description_zh": "本卡登记哈斯克尔第10章第312页所称Morlaiter。正文仅用姓氏称他曾雕塑Schulenburg的肖像；书后索引以“Morlaiter, Michelangelo”指向同页。本卡保留正文与索引各自的姓名形式，不补充肖像名称或其他生平信息。中文显示名为项目工作音译。",
        "description_en": "This card records the Morlaiter named on page 312 of Chapter 10. The body uses only the surname when saying he sculpted portraits of Schulenburg; the index identifies the page's Morlaiter as “Morlaiter, Michelangelo.” Both source forms are preserved without adding portrait titles or other biographical information. The Chinese display name is a working transliteration.",
        "context_zh": "Haskell列举了不止一位为Schulenburg制作肖像的艺术家，且未给出具体肖像题名；相关关系候选留待S6。",
        "context_en": "Haskell lists more than one artist who made portraits of Schulenburg and gives no individual portrait title; the relation candidate remains for S6.",
        "name_rows": [("索引全名", "Michelangelo Morlaiter", "S1"), ("正文称名", "Morlaiter", "S2")],
    },
    {
        "candidate": "cand-1707", "group": "new-person:morris-roger-69ba5e4869",
        "ku": "units/persons/roger-morris", "card": "04-knowledge/units/persons/roger-morris.md",
        "name_zh": "罗杰·莫里斯", "name_en": "Roger Morris",
        "index_entry": "M.csv#248", "index_name": "Morris, Roger", "page": "309",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "location": "第10章，印刷页309；OCR L470",
        "span": "line 470; print p. 309", "quote": "one by Roger Morris",
        "summary": "Haskell称十一幅图中有一幅展示Roger Morris的一件作品；书后索引以“Morris, Roger”指向该页。",
        "relation_ids": ["st-chp10-p309-one-picture-after-morris"],
        "endpoints": [("st-chp10-p309-one-picture-after-morris", "cand-9251", "cand-1707", "one_of_eleven_pictures_portrays_a_work_by_roger_morris", "one by Roger Morris")],
        "description_zh": "本卡登记哈斯克尔第10章所称Roger Morris。第309页将他列为十一幅图中一幅所呈现作品的创作者；书后索引以“Morris, Roger”指向该页。原书此处没有称Morris为该幅图像本身的作者，本卡不作此推断。中文显示名为项目工作音译。",
        "description_en": "This card records the Roger Morris named in Chapter 10. Page 309 lists him as the maker of a work represented in one of eleven pictures; the index lists “Morris, Roger” at that page. The passage does not identify Morris as the maker of the picture itself, and this card makes no such inference. The Chinese display name is a working transliteration.",
        "context_zh": "S2候选指十一幅图中有一幅呈现Roger Morris的一件作品；不将其改写成Morris绘制该图。关系候选留待S6。",
        "context_en": "The S2 candidate says that one of the eleven pictures shows a work by Roger Morris; it does not say Morris painted that picture. The relation candidate remains for S6.",
        "name_rows": [("索引与正文姓名", "Roger Morris", "S1、S2")],
    },
    {
        "candidate": "cand-1708", "group": "new-person:moscheni-pietro-41b3d0bea5",
        "ku": "units/persons/pietro-moscheni", "card": "04-knowledge/units/persons/pietro-moscheni.md",
        "name_zh": "皮耶特罗·莫斯凯尼", "name_en": "Pietro Moscheni",
        "index_entry": "M.csv#249", "index_name": "Moscheni, Pietro", "page": "322",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "location": "第10章，印刷页322；OCR L182",
        "span": "line 182; print p. 322", "quote": "commissioned by a friend of Lodoli’s, Pietro Moscheni",
        "summary": "Haskell称Lodoli的朋友Pietro Moscheni委托Alessandro Longhi绘制Carlo Lodoli肖像；同页索引以“Moscheni, Pietro”指向该页。",
        "relation_ids": ["st-chp10-p322-moscheni-commissioned-longhi-portrait", "st-chp10-p322-moscheni-friend-of-lodoli"],
        "endpoints": [
            ("st-chp10-p322-moscheni-commissioned-longhi-portrait", "cand-1708", "cand-1425", "commissioned-portrait-of-carlo-lodoli-by-alessandro-longhi", "commissioned by a friend of Lodoli’s, Pietro Moscheni"),
            ("st-chp10-p322-moscheni-friend-of-lodoli", "cand-1708", "cand-1411", "friend-of", "commissioned by a friend of Lodoli’s, Pietro Moscheni"),
        ],
        "description_zh": "本卡登记哈斯克尔第10章所称Pietro Moscheni。第322页称Lodoli的朋友Moscheni委托Alessandro Longhi绘制Carlo Lodoli肖像；书后索引以“Moscheni, Pietro”指向该页。原文未给委托日期，本卡不补充日期或人物履历。中文显示名为项目工作音译。",
        "description_en": "This card records the Pietro Moscheni named in Chapter 10. Page 322 says that Lodoli's friend Moscheni commissioned Alessandro Longhi to paint a portrait of Carlo Lodoli; the index lists “Moscheni, Pietro” at that page. No commission date is supplied, and this card adds neither a date nor biography. The Chinese display name is a working transliteration.",
        "context_zh": "委托与Lodoli友谊两条S2关系候选均留待S6；未把来源叙述转换为正式关系。",
        "context_en": "Both S2 candidates concerning the commission and friendship with Lodoli remain for S6; the source account is not converted into formal relations.",
        "name_rows": [("索引与正文姓名", "Pietro Moscheni", "S1、S2")],
    },
    {
        "candidate": "cand-1716", "group": "new-person:de-francesco-mura-a4cbc8f2bb",
        "ku": "units/persons/francesco-de-mura", "card": "04-knowledge/units/persons/francesco-de-mura.md",
        "name_zh": "弗朗切斯科·德·穆拉", "name_en": "Francesco de Mura",
        "index_entry": "M.csv#257", "index_name": "Mura, Francesco de", "page": "351",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md", "location": "第14章，印刷页351；OCR L51",
        "span": "line 51; print p. 351", "quote": "subjects for Francesco de Mura and Solimena among the Neapolitans",
        "summary": "Haskell称Algarotti在那不勒斯画家中为Francesco de Mura和Solimena寻找题材；索引以“Mura, Francesco de”指向该页。",
        "relation_ids": ["st-chp14-p351-neapolitan-subjects"],
        "endpoints": [("st-chp14-p351-neapolitan-subjects", "cand-0072", "cand-1716", "found_subject_for_artist", "subjects for Francesco de Mura and Solimena")],
        "description_zh": "本卡登记哈斯克尔第14章具名的Francesco de Mura。第351页称Algarotti在那不勒斯画家中为他和Solimena寻找题材；书后索引以“Mura, Francesco de”指向该页。此处只记录书内姓名与叙述，不推导具体城市或正式组织归属。中文显示名为项目工作音译。",
        "description_en": "This card records the Francesco de Mura named in Chapter 14. Page 351 says that Algarotti found subjects for him and Solimena among the Neapolitan artists; the index lists “Mura, Francesco de” at that page. This entry records only the book's name and account and does not infer a specific city or formal organizational membership. The Chinese display name is a working transliteration.",
        "context_zh": "S2候选记录Haskell对Algarotti提案的报告；地区语境保留为“那不勒斯画家中”，不据此构造机构关系。",
        "context_en": "The S2 candidate records Haskell's account of Algarotti's proposal. Its regional context remains “among the Neapolitan artists” and is not turned into an institutional relation.",
        "name_rows": [("索引与正文姓名", "Francesco de Mura", "S1、S2")],
    },
]


def make_source(t: dict, index: bool) -> dict:
    if index:
        return {
            "citation": "Francis Haskell, *Patrons and Painters*, index, M.csv.",
            "location": f"书后索引，{t['index_entry']}；指向印刷页{t['page']}",
            "sentence_summary": f"索引以“{t['index_name']}”为主条并指向印刷页{t['page']}。",
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/03-Index/03-2-Index-CSV/M.csv", "source_span": t["index_entry"]},
        }
    return {
        "citation": BOOK, "location": t["location"], "sentence_summary": t["summary"],
        "original_quotes": [{"source_span": t["span"], "text": t["quote"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["source_file"], "source_span": t["span"]},
    }


def make_card(t: dict) -> str:
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": [make_source(t, True), make_source(t, False)],
        "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    names = "\n".join(f"| {field} | {value} | {basis} |" for field, value, basis in t["name_rows"])
    relations = "、".join(f"`{sid}`" for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}

**English:** {t['description_en']}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
{names}

### 本书相关内容

**中文：** {t['context_zh']}

**English:** {t['context_en']}

## 关系与证据

### 关系记录

当前没有登记在 `relations.csv` 中的正式关系。S2关系候选 {relations} 保留来源归因并留待S6裁决；本次S4身份登记不将其转为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four source-backed M-index person endpoint groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = sync.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}

    for t in TARGETS:
        cid = t["candidate"]
        candidate = candidate_by_id[cid]
        alignment = next(row for row in alignments if row.get("candidate_id") == cid and not row.get("external_source"))
        assert candidate.get("suggested_type") == "person"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        group_members = [row["candidate_id"] for row in alignments if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"]]
        assert group_members == [cid], (t["group"], group_members)
        assert candidate.get("index_entry_id") == t["index_entry"] and candidate.get("canonical_name") == t["index_name"] and candidate.get("index_page_range") == t["page"]
        index = person_sync.read_index_rows("M.csv")[int(t["index_entry"].split("#")[1])]
        assert index.get("Main Entry") == t["index_name"] and index.get("Page Numbers", "") == t["page"]
        assert t["quote"] in (ROOT / t["source_file"]).read_text(encoding="utf-8-sig"), (cid, t["quote"])
        assert t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold() for row in manifest)
        direct = {row["statement_id"] for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))}
        assert direct == set(t["relation_ids"]), (cid, direct)
        for sid, subject, obj, predicate, quote in t["endpoints"]:
            statement = statement_by_id[sid]
            assert (statement.get("subject_candidate_id"), statement.get("object_candidate_id"), statement.get("predicate")) == (subject, obj, predicate)
            assert quote in statement.get("original_quote", "")

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(row for row in planned_alignments if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + f" S4登记（{DATE}）：身份组{t['group']}映射至{t['ku']}；新增一张书内来源支持的人物KU，相关S2关系候选仍待S6。"
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = person_sync.insert_accepted(planned_accepted, t["card"])

    baseline = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["registered_groups"] == baseline["person"]["registered_groups"] + len(TARGETS)
    assert stats["person"]["registered_members"] == baseline["person"]["registered_members"] + len(TARGETS)
    assert stats["person"]["pending_groups"] == baseline["person"]["pending_groups"] - len(TARGETS)
    assert stats["person"]["pending_members"] == baseline["person"]["pending_members"] - len(TARGETS)
    assert len(planned_manifest) == len(manifest) + len(TARGETS)
    cards = {t["card"]: make_card(t) for t in TARGETS}
    for card in cards.values():
        match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
        assert match and isinstance(yaml.safe_load(match.group(1)), dict)

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    log_rows = [f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；S2关系候选{'、'.join(f'`{sid}`' for sid in t['relation_ids'])}留待S6。{t['context_zh']}" for t in TARGETS]
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Morlaiter、Morris、Moscheni与de Mura四组直接端点登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组，各登记一个KU。Morlaiter正文只作姓氏称呼，索引提供Michelangelo全名；Morris不被写成所绘图片的作者；"
        "Moscheni两条候选分别记录委托和友谊；de Mura的地区措辞保留为‘那不勒斯画家中’。关系候选留待S6，未新增外部来源、正式关系或backlog项目。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Morlaiter、Morris、Moscheni与de Mura（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，各登记一张KU；Morlaiter正文姓氏与索引全名并列记录，Morris未被写作图片作者，Moscheni关系候选分开保留，"
        "de Mura地域描述不扩展为机构归属。候选关系留待S6，未新增外部来源或正式关系。"
    )

    if args.dry_run:
        print(f"dry-run passed: four singleton person groups; index/source/S2 endpoint checks passed; manifest={len(manifest)}->{len(planned_manifest)}; person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; KU={len(planned_manifest)}; external_sources_added=0; relation_rows_added=0; no files changed")
        return 0
    for path, card in cards.items():
        (ROOT / path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: groups=4; candidate_mappings=4; KU={len(planned_manifest)}; person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; external_sources_added=0; relation_rows_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
