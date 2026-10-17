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
ANCHOR = "s4-person-philip-piccino-pompeati-porta-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = [
    {
        "candidate": "cand-1895", "group": "new-person:ii-of-philip-spain-d29092bda5",
        "ku": "units/persons/philip-ii-of-spain", "card": "04-knowledge/units/persons/philip-ii-of-spain.md",
        "name_zh": "西班牙的菲利普二世", "name_en": "Philip II of Spain",
        "index_file": "P.csv", "index_entry": "P.csv#96", "index_name": "Philip II of Spain", "page": "170",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "location": "第7章第I节，印刷页170；OCR L15–16",
        "span": "lines 15–16; print p. 170", "quote": "Philip II had spent large sums in building up collections of paintings",
        "summary": "Haskell将Philip II列为曾投入大量资金建立绘画收藏的16世纪统治者之一；索引以“Philip II of Spain”指向第170页。",
        "description_zh": "本卡登记哈斯克尔第7章第I节第170页所称Philip II。正文将他列为曾投入大量资金建立绘画收藏的16世纪统治者之一；书后索引以“Philip II of Spain”指向该页。本卡只记录这一书内称名和语境。中文显示名为项目工作译名。",
        "description_en": "This card records Philip II named on page 170 of Chapter 7, section I. The passage lists him among sixteenth-century rulers who spent large sums building painting collections; the index identifies him as “Philip II of Spain” at that page. The card records only this source name and context. The Chinese display name is a working translation.",
        "context_zh": "正文给出收藏史的概括性例证，不构造具体委托或收藏关系。",
        "context_en": "The passage gives a general example in collecting history and does not establish a specific commission or collection relation.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Philip II of Spain", "S1"), ("正文称名", "Philip II", "S2")],
    },
    {
        "candidate": "cand-1926", "group": "new-person:jacopo-piccino-7b6fbf5d82",
        "ku": "units/persons/jacopo-piccino", "card": "04-knowledge/units/persons/jacopo-piccino.md",
        "name_zh": "雅各布·皮奇诺", "name_en": "Jacopo Piccino",
        "index_file": "P.csv", "index_entry": "P.csv#127", "index_name": "Piccino, Jacopo", "page": "408",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md", "location": "Postscript，印刷页408；OCR L185–188",
        "span": "lines 185–188; print p. 408", "quote": "probably those by Piccino in Matina’s volume",
        "summary": "Haskell转述Parker的判断：Maggiotto的狗总椭圆肖像可能改编自Matina卷中的Piccino版画；索引以“Piccino, Jacopo”指向第408页。",
        "description_zh": "本卡登记书后索引“Piccino, Jacopo”所指人物。Postscript第408页转述Parker的判断，称Maggiotto的狗总椭圆肖像可能改编自Matina卷中的Piccino版画；原文保留probably的限定。本卡记录该书内称名，不把可能的版画归属写成确定事实。中文显示名为项目工作音译。",
        "description_en": "This card records the person indexed as “Piccino, Jacopo”. On page 408 of the Postscript, Haskell reports Parker's view that Maggiotto's oval Doge portraits were probably adapted from engravings by Piccino in Matina's volume; the source retains the qualification “probably”. This card records the source-local name and does not turn the possible print attribution into a certainty. The Chinese display name is a working transliteration.",
        "context_zh": "Parker所述版画来源保持推测语气；S4只登记索引人物身份，不作确定创作归属。",
        "context_en": "Parker's proposed print source remains tentative; S4 registers the indexed person without asserting a definite authorship attribution.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Piccino, Jacopo", "S1"), ("正文称名", "Piccino", "S2")],
    },
    {
        "candidate": "cand-1972", "group": "new-person:domenico-pompeati-dddf91ab34",
        "ku": "units/persons/domenico-pompeati", "card": "04-knowledge/units/persons/domenico-pompeati.md",
        "name_zh": "多梅尼科·庞佩亚蒂", "name_en": "Domenico Pompeati",
        "index_file": "P.csv", "index_entry": "P.csv#174", "index_name": "Pompeati, Domenico", "page": "394",
        "source_file": "02-sources/02-Markdown/19_CHP-19Appendix.md", "location": "第19章Appendix，印刷页394；OCR L159–160",
        "span": "lines 159–160; print p. 394", "quote": "Giacomo Caraboli and Domenico Pompeati",
        "summary": "Haskell称Joseph Smith此前将一批书售予Giacomo Caraboli与Domenico Pompeati；索引以“Pompeati, Domenico”指向第394页。",
        "description_zh": "本卡登记哈斯克尔第19章Appendix第394页所称Domenico Pompeati。正文称Joseph Smith此前把一批书售予Giacomo Caraboli与Pompeati；书后索引以“Pompeati, Domenico”指向该页。本卡不推定其与其他同名者的身份关系，也不补充生平。中文显示名为项目工作音译。",
        "description_en": "This card records Domenico Pompeati named on page 394 of the Chapter 19 Appendix. The passage says Joseph Smith had earlier sold a group of books to Giacomo Caraboli and Pompeati; the index lists “Pompeati, Domenico” at that page. The card does not infer an identity link to other people with the same name or add biography. The Chinese display name is a working transliteration.",
        "context_zh": "人物出现在Joseph Smith售书叙述中；本次不创建正式交易关系。",
        "context_en": "The person appears in the account of Joseph Smith's book sale; this registration creates no formal transaction relation.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Pompeati, Domenico", "S1"), ("正文姓名", "Domenico Pompeati", "S2")],
    },
    {
        "candidate": "cand-1977", "group": "new-person:della-guglielmo-porta-e07ba351f0",
        "ku": "units/persons/guglielmo-della-porta", "card": "04-knowledge/units/persons/guglielmo-della-porta.md",
        "name_zh": "古列尔莫·德拉·波尔塔", "name_en": "Guglielmo della Porta",
        "index_file": "P.csv", "index_entry": "P.csv#179", "index_name": "Porta, Guglielmo della", "page": "",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md", "location": "第4章第II节，印刷页104；OCR L54–56",
        "span": "lines 54–56; print p. 104", "quote": "[by Guglielmo della Porta] opposite",
        "summary": "Haskell以方括号补明Paul III墓由Guglielmo della Porta创作；书后索引列出“Porta, Guglielmo della”，未标页码。",
        "description_zh": "本卡登记第4章第II节第104页所称Guglielmo della Porta。Haskell在比较Urban VIII与Paul III墓的文字中以方括号注明Paul III墓为della Porta所作；书后索引列出“Porta, Guglielmo della”但未标页码。对应创作关系S2候选留待S6核对端点和证据范围，本卡不建立正式边。中文显示名为项目工作音译。",
        "description_en": "This card records Guglielmo della Porta named on page 104 of Chapter 4, section II. In comparing the tombs of Urban VIII and Paul III, Haskell inserts in brackets that the Paul III tomb was by della Porta; the index lists “Porta, Guglielmo della” without a page number. The corresponding S2 creator candidate remains for S6 review of endpoints and evidence scope, and this card creates no formal edge. The Chinese display name is a working transliteration.",
        "context_zh": "S2创作关系候选`st-chp4-sec-ii-l53-63-guglielmo-created-paul-tomb`留待S6裁决；本次不新增formal relation。",
        "context_en": "The S2 creator candidate `st-chp4-sec-ii-l53-63-guglielmo-created-paul-tomb` remains for S6 review; this registration adds no formal relation.",
        "relation_ids": ["st-chp4-sec-ii-l53-63-guglielmo-created-paul-tomb"],
        "endpoints": [("st-chp4-sec-ii-l53-63-guglielmo-created-paul-tomb", "cand-1977", "cand-4516", "creator_of", "[by Guglielmo della Porta]")],
        "name_rows": [("索引姓名", "Porta, Guglielmo della", "S1"), ("正文姓名", "Guglielmo della Porta", "S2")],
    },
]


def make_index_source(t: dict) -> dict:
    return {
        "citation": f"Francis Haskell, *Patrons and Painters*, index, {t['index_file']}.",
        "location": f"书后索引，{t['index_entry']}" + (f"；指向印刷页{t['page']}" if t["page"] else "；未标页码"),
        "sentence_summary": f"索引以“{t['index_name']}”为主条" + (f"并指向印刷页{t['page']}。" if t["page"] else "，未标页码。"),
        "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}", "source_span": t["index_entry"]},
    }


def make_text_source(t: dict) -> dict:
    return {
        "citation": BOOK, "location": t["location"], "sentence_summary": t["summary"],
        "original_quotes": [{"source_span": t["span"], "text": t["quote"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["source_file"], "source_span": t["span"]},
    }


def make_card(t: dict) -> str:
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": [make_index_source(t), make_text_source(t)],
        "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    names = "\n".join(f"| {field} | {value} | {basis} |" for field, value, basis in t["name_rows"])
    pending = "、".join(f"`{sid}`" for sid in t["relation_ids"])
    pending_note = f"S2关系候选{pending}保留来源归因并留待S6裁决；" if pending else "本批未将来源叙述转换为正式关系；"
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

当前没有登记在 `relations.csv` 中的正式关系；{pending_note}本次S4身份登记不将其转为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register four S3-new person groups, including Guglielmo della Porta's work endpoint.")
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
        assert candidate.get("index_entry_id") == t["index_entry"] and candidate.get("canonical_name") == t["index_name"] and candidate.get("index_page_range", "") == t["page"]
        index = person_sync.read_index_rows(t["index_file"])[int(t["index_entry"].split("#")[1])]
        assert index.get("Main Entry") == t["index_name"] and index.get("Page Numbers", "") == t["page"]
        assert t["quote"] in (ROOT / t["source_file"]).read_text(encoding="utf-8-sig"), (cid, t["quote"])
        assert t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold() for row in manifest)
        direct = {row["statement_id"] for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))}
        assert direct == set(t["relation_ids"]), (cid, direct)
        for sid, subject, obj, predicate, quote in t.get("endpoints", []):
            statement = statement_by_id[sid]
            assert (statement.get("subject_candidate_id"), statement.get("object_candidate_id"), statement.get("predicate")) == (subject, obj, predicate)
            assert quote in statement.get("original_quote", "")

    planned_alignments = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(row for row in planned_alignments if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + f" S4登记（{DATE}）：身份组{t['group']}映射至{t['ku']}；新增一张书内来源支持的人物KU，formal relation仍按S2候选状态保留。"
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
    log_rows = [f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；依据索引{t['index_entry']}与正文{t['location']}登记。" for t in TARGETS]
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Philip II、Piccino、Pompeati与della Porta四组索引／正文登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组。Piccino版画来源保留Parker的可能性措辞；della Porta的Paul III墓创作候选`st-chp4-sec-ii-l53-63-guglielmo-created-paul-tomb`留待S6核对。Philip II的概括性收藏史语境和Pompeati售书记录不转换为formal relation；未新增外部来源或relation row。\n\n"
        + f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        + f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        + f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Philip II、Piccino、Pompeati与della Porta（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，各登记一张KU；Piccino来源归属保留推测语气，della Porta创作关系候选留待S6。"
    )

    if args.dry_run:
        print(f"dry-run passed: four singleton person groups; index/source/endpoint checks passed; manifest={len(manifest)}->{len(planned_manifest)}; person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; KU={len(planned_manifest)}; external_sources_added=0; relation_rows_added=0; no files changed")
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
