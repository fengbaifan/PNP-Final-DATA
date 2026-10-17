from __future__ import annotations

import argparse
import json
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
ANCHOR = "s4-person-relation-endpoints-mancini-manfredi-marchesi-marchiori-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def book_source(source_file: str, location: str, span: str, quote: str, summary: str) -> dict:
    return {
        "citation": BOOK,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": span,
        },
    }


def index_source(t: dict) -> dict:
    return {
        "citation": "Francis Haskell, *Patrons and Painters*, index, M.csv.",
        "location": f"书后索引，{t['index_entry']}；指向印刷页{t['index_page']}",
        "sentence_summary": f"索引以“{t['index_name']}”为主条并指向印刷页{t['index_page']}。",
        "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}",
            "source_span": t["index_entry"],
        },
    }


TARGETS = [
    {
        "candidate": "cand-1506",
        "group": "new-person:francesco-mancini-f439d8fb6a",
        "ku": "units/persons/francesco-mancini",
        "card": "04-knowledge/units/persons/francesco-mancini.md",
        "name_zh": "弗朗切斯科·曼奇尼",
        "name_en": "Francesco Mancini",
        "index_entry": "M.csv#43",
        "index_file": "M.csv",
        "index_name": "Mancini, Francesco",
        "index_page": "351",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "location": "第14章，印刷页351；OCR L51",
        "span": "line 51; print p. 351",
        "quote": "in Rome, only Mancini besides the rather special case of Pannini",
        "summary": "Haskell将Mancini列为Algarotti在罗马建议纳入画廊的画家之一；书后索引将该页的Mancini列为Francesco。",
        "relation_ids": ["st-chp14-p351-rome-artists"],
        "endpoints": [("st-chp14-p351-rome-artists", "cand-0072", "cand-1506", "found_subject_for_artist_in_city_context", "only Mancini besides")],
        "description_zh": "本卡登记哈斯克尔第14章所称Francesco Mancini。第351页在概述Algarotti为画廊提出的画家名单时称罗马除Pannini这一特殊情形外只有Mancini；书后索引以“Mancini, Francesco”指向该页。此处身份限于书内所指人物，不据同姓补充生平。中文显示名为项目工作音译。",
        "description_en": "This card records the Francesco Mancini named in Chapter 14. On page 351, while summarizing Algarotti's proposed painters for a gallery, Haskell says that in Rome there was only Mancini besides the special case of Pannini; the index identifies the page's Mancini as “Mancini, Francesco.” The record is limited to the person named in the book and adds no biography from the surname. The Chinese display name is a working transliteration.",
        "context_zh": "第14章将Mancini列入Algarotti的罗马画家建议名单；对应statement仍是S2关系候选，留待S6裁决。该人物与现有Giulio Mancini、Maria Mancini为不同身份。",
        "context_en": "Chapter 14 includes Mancini in Algarotti's proposed list of Roman painters. The corresponding statement remains an S2 relation candidate for S6 review. This person is distinct from the existing KUs for Giulio Mancini and Maria Mancini.",
        "name_rows": [("索引姓名", "Francesco Mancini", "S1、S2")],
    },
    {
        "candidate": "cand-1511",
        "group": "new-person:eustachio-manfredi-e87f85ad8e",
        "ku": "units/persons/eustachio-manfredi",
        "card": "04-knowledge/units/persons/eustachio-manfredi.md",
        "name_zh": "尤斯塔基奥·曼弗雷迪",
        "name_en": "Eustachio Manfredi",
        "index_entry": "M.csv#48",
        "index_file": "M.csv",
        "index_name": "Manfredi, Eustachio",
        "index_page": "347",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "location": "第14章，印刷页347；OCR L9",
        "span": "line 9; print p. 347",
        "quote": "remained in constant correspondence with Eustachio Manfredi",
        "summary": "Haskell称Algarotti与Eustachio Manfredi保持通信；书后索引以Manfredi, Eustachio指向第347页。",
        "relation_ids": ["st-chp14-p347-algarotti-corresponded-with-manfredi"],
        "endpoints": [("st-chp14-p347-algarotti-corresponded-with-manfredi", "cand-0043", "cand-1511", "corresponded_with", "Eustachio Manfredi")],
        "description_zh": "本卡登记哈斯克尔第14章具名的Eustachio Manfredi。第347页称Algarotti与他保持通信，书后索引以“Manfredi, Eustachio”指向该页。此记录只登记书内人物身份及书中语境；通信关系候选尚待S6。中文显示名为项目工作音译。",
        "description_en": "This card records the Eustachio Manfredi named in Chapter 14. Page 347 says that Algarotti remained in correspondence with him, and the index lists “Manfredi, Eustachio” at that page. This record registers only the book-named person and context; the correspondence candidate remains for S6. The Chinese display name is a working transliteration.",
        "context_zh": "Haskell称Algarotti与Manfredi在学生时代相识后持续通信；该陈述仍为来源归因的关系候选，不在S4转为正式关系。",
        "context_en": "Haskell says Algarotti remained in correspondence with Manfredi after meeting him during his student days. This remains a source-attributed relation candidate and is not made formal in S4.",
        "name_rows": [("索引姓名", "Eustachio Manfredi", "S1、S2")],
    },
    {
        "candidate": "cand-1538",
        "group": "new-person:marchesi-raffaelo-548b679336",
        "ku": "units/persons/raffaelo-marchesi",
        "card": "04-knowledge/units/persons/raffaelo-marchesi.md",
        "name_zh": "拉斐洛·马尔凯西",
        "name_en": "Raffaelo Marchesi",
        "index_entry": "M.csv#76",
        "index_file": "M.csv",
        "index_name": "Marchesi, Raffaelo",
        "index_page": "136",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md",
        "location": "第5章，印刷页136；OCR L41",
        "span": "line 41; print p. 136",
        "quote": "the distinguished lawyer Raffaele Marchesi to whom he bequeathed some of his works",
        "summary": "正文称Raffaele Marchesi为律师并称Cerquozzi将部分作品遗赠给他；同页索引将姓名写为Raffaelo Marchesi。",
        "relation_ids": ["st-chp5-p136-marchesi-lawyer-and-beneficiary-of-cerquozzi-bequest"],
        "endpoints": [("st-chp5-p136-marchesi-lawyer-and-beneficiary-of-cerquozzi-bequest", "cand-0625", "cand-1538", "bequeathed_unspecified_works_to", "Raffaele Marchesi")],
        "description_zh": "本卡登记书后索引作“Marchesi, Raffaelo”的人物。正文同一印刷页将律师姓名写作“Raffaele Marchesi”，并称Cerquozzi将部分作品遗赠给他。两种拼写都保留为本书对同一页人物的指称；本卡以索引形式作显示名，不宣称已确定规范拼法。中文显示名为按索引拼写形成的项目工作音译。",
        "description_en": "This card records the person indexed as “Marchesi, Raffaelo.” On the same printed page, the body spells the lawyer's name “Raffaele Marchesi” and says that Cerquozzi bequeathed some of his works to him. Both spellings are preserved as the book's forms for the person discussed on that page; the index form is used as the display name without claiming that the standard spelling has been settled. The Chinese display name is a working transliteration based on the index form.",
        "context_zh": "第5章称律师Raffaele Marchesi为Cerquozzi部分作品遗赠对象。索引拼写Raffaelo与正文Raffaele的差异记作来源异形，未借此判断人物为两人；关系候选仍待S6。",
        "context_en": "Chapter 5 names lawyer Raffaele Marchesi as the recipient of some of Cerquozzi's works. The index/body difference between Raffaelo and Raffaele is retained as a source variant and is not treated as evidence of two people; the relation candidate remains for S6.",
        "name_rows": [
            ("索引姓名拼写", "Raffaelo Marchesi", "S1"),
            ("正文姓名拼写", "Raffaele Marchesi", "S2"),
        ],
    },
    {
        "candidate": "cand-1541",
        "group": "new-person:giovanni-marchiori-065f269ab2",
        "ku": "units/persons/giovanni-marchiori",
        "card": "04-knowledge/units/persons/giovanni-marchiori.md",
        "name_zh": "乔瓦尼·马尔基奥里",
        "name_en": "Giovanni Marchiori",
        "index_entry": "M.csv#79",
        "index_file": "M.csv",
        "index_name": "Marchiori, Giovanni",
        "index_page": "356",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
        "location": "第14章，印刷页356；OCR L101–102",
        "span": "lines 101–102; print p. 356",
        "quote": "the sculptor Giovanni Marchiori to produce some figures for a church in\nBerlin",
        "summary": "Haskell称Algarotti为雕塑家Giovanni Marchiori取得柏林一座教堂人物雕像的委托；书后索引以Marchiori, Giovanni指向第356页。",
        "relation_ids": ["st-chp14-p356-marchiori-berlin-church-commission"],
        "endpoints": [("st-chp14-p356-marchiori-berlin-church-commission", "cand-0063", "cand-1541", "obtained_commission_for_figures_for_church_in_berlin", "sculptor Giovanni Marchiori")],
        "description_zh": "本卡登记哈斯克尔第14章具名的雕塑家Giovanni Marchiori。第356页称Algarotti为他取得柏林一座教堂人物雕像的委托；书后索引以“Marchiori, Giovanni”指向该页。此卡不独立核实委托后续或雕像身份。中文显示名为项目工作音译。",
        "description_en": "This card records the sculptor Giovanni Marchiori named in Chapter 14. Page 356 says that Algarotti obtained for him a commission to produce figures for a church in Berlin; the index lists “Marchiori, Giovanni” at that page. This card does not independently verify the commission's outcome or identify the figures. The Chinese display name is a working transliteration.",
        "context_zh": "原书称Algarotti取得该委托并提及其致Bonomo信中“for the honour of Italy”的劝促；人物与教堂雕塑委托关系候选留待S6。",
        "context_en": "Haskell says Algarotti obtained the commission and mentions his appeal to Bonomo “for the honour of Italy.” The person/commission relation candidate remains for S6.",
        "name_rows": [("索引与正文姓名", "Giovanni Marchiori", "S1、S2")],
    },
]


def make_card(t: dict) -> str:
    sources = [index_source(t), book_source(t["source_file"], t["location"], t["span"], t["quote"], t["summary"])]
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
    rows = "\n".join(f"| {field} | {value} | {evidence} |" for field, value, evidence in t["name_rows"])
    relation_ids = "、".join(f"`{sid}`" for sid in t["relation_ids"])
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {t['description_zh']}

**English:** {t['description_en']}

### 姓名

| 字段 | 值 | 证据 |
|---|---|---|
{rows}

### 本书相关内容

**中文：** {t['context_zh']}

**English:** {t['context_en']}

## 关系与证据

### 关系记录

当前没有登记在 `relations.csv` 中的正式关系。S2关系候选 {relation_ids} 保留来源归因并留待S6裁决；本次S4身份登记不将其转为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four S4 person endpoint groups with source-variant tracking.")
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
    statements = sync.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}

    for t in TARGETS:
        cid = t["candidate"]
        c = candidate_by_id[cid]
        a = alignment_by_id[cid]
        assert c.get("suggested_type") == "person"
        assert a.get("decision") == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == t["group"]
        group_members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert group_members == [cid], (t["group"], group_members)
        assert c.get("index_entry_id") == t["index_entry"]
        assert c.get("canonical_name") == t["index_name"]
        assert c.get("index_page_range") == t["index_page"]
        index_rows = person_sync.read_index_rows(t["index_file"])
        index_row = index_rows[int(t["index_entry"].split("#")[1])]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        body = (ROOT / t["source_file"]).read_text(encoding="utf-8-sig")
        assert t["quote"] in body
        assert t["ku"] not in manifest_by_ku
        assert t["card"] not in accepted_paths
        assert not (ROOT / t["card"]).exists()
        assert not any(
            row.get("type") == "person"
            and (row.get("name_en") or "").casefold() == t["name_en"].casefold()
            for row in manifest
        )
        direct = {
            row["statement_id"] for row in statements
            if (row.get("qualifiers") or {}).get("relation_candidate") is True
            and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
        }
        assert direct == set(t["relation_ids"]), (cid, direct)
        for sid, subject, obj, predicate, quote in t["endpoints"]:
            statement = statement_by_id[sid]
            assert statement.get("subject_candidate_id") == subject
            assert statement.get("object_candidate_id") == obj
            assert statement.get("predicate") == predicate
            assert quote in statement.get("original_quote", "")

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
        if t["candidate"] == "cand-1538":
            suffix += (
                "身份拼写核对：书后索引M.csv#76作Raffaelo Marchesi，正文第5章p.136 L41作Raffaele Marchesi，"
                "同页索引定位与段落语境指向同一书内人物；卡片保留两种原文拼写，不声称已确定规范形式。"
            )
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + suffix
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
    assert len({line[2:] for line in planned_accepted if line.startswith("- 04-knowledge/units/")}) == len(accepted_paths) + len(TARGETS)

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
    log_rows = []
    for t in TARGETS:
        rels = "、".join(f"`{sid}`" for sid in t["relation_ids"])
        log_rows.append(
            f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）]"
            f"(../../../{t['card']})；S2关系候选{rels}留待S6。{t['context_zh']}"
        )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Mancini、Manfredi、Marchesi、Marchiori四组直接端点登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组，各登记一个人物KU。cand-1538的书后索引写Raffaelo Marchesi，而正文同页写Raffaele Marchesi；"
        "相同索引页码、姓名和律师/遗赠语境支持归为同一书内人物，卡片保留拼写异形，不认定哪一形式为规范名。"
        "所有书内陈述仍为S2关系候选；未新增正式关系、外部事实、来源登记或backlog项目。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    result_text += (
        f"\n\n### S4 人物身份组登记：四个直接关系端点（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，逐组登记一张KU，相关关系候选待S6。Marchesi书后索引的Raffaelo与正文的Raffaele拼写差异已保留；"
        "此批不认定规范拼法，不新增外部来源或正式关系。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: four singleton person groups; index/source/S2 endpoint checks passed; "
            f"manifest={len(manifest)}->{len(planned_manifest)}; person_registered="
            f"{stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
            f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
            f"KU={len(planned_manifest)}; external_sources_added=0; relation_rows_added=0; no files changed"
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
        f"applied: groups=4; candidate_mappings=4; KU={len(planned_manifest)}; "
        f"person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; "
        f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
        "external_sources_added=0; relation_rows_added=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
