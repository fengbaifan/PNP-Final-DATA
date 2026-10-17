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
ANCHOR = "s4-person-harley-paciaudi-paolini-parigi-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = [
    {
        "candidate": "cand-1801", "group": "new-person:harley-of-oxford-robert-a663f62cf8",
        "ku": "units/persons/robert-harley-earl-of-oxford", "card": "04-knowledge/units/persons/robert-harley-earl-of-oxford.md",
        "name_zh": "罗伯特·哈利（牛津伯爵）", "name_en": "Robert Harley, Earl of Oxford",
        "index_file": "O.csv", "index_entry": "O.csv#36", "index_name": "Oxford, Robert Harley, Earl of", "page": "288",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "location": "第10章，印刷页288；OCR L220–221",
        "span": "lines 220–221; print p. 288", "quote": "Robert Harley, Earl of\nOxford",
        "summary": "Haskell称纪念碑方案最终包括Robert Harley, Earl of Oxford；书后索引以“Oxford, Robert Harley, Earl of”定位第288页。",
        "description_zh": "本卡登记哈斯克尔第10章第288页所称Robert Harley, Earl of Oxford。该段称纪念碑方案包括他，并概述其在结束Marlborough所发动战争中的政治作用；书后索引以“Oxford, Robert Harley, Earl of”定位该页。本卡只记录书内姓名和叙述。中文显示名为项目工作译名。",
        "description_en": "This card records Robert Harley, Earl of Oxford, named on page 288 of Chapter 10. The passage says he was included in the monument scheme and summarizes his political role in bringing the wars waged by Marlborough to an end; the index lists “Oxford, Robert Harley, Earl of” at that page. The card records only the book's name and account. The Chinese display name is a working translation.",
        "context_zh": "人物作为纪念碑方案所纪念对象之一出现；本次未创建其他关系记录。",
        "context_en": "The person appears as one of those commemorated in the monument scheme; this registration creates no other relation record.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Oxford, Robert Harley, Earl of", "S1"), ("正文姓名", "Robert Harley, Earl of Oxford", "S2")],
    },
    {
        "candidate": "cand-1802", "group": "new-person:maria-paciaudi-paolo-c642933872",
        "ku": "units/persons/paolo-maria-paciaudi", "card": "04-knowledge/units/persons/paolo-maria-paciaudi.md",
        "name_zh": "保罗·玛丽亚·帕西奥迪", "name_en": "Paolo Maria Paciaudi",
        "index_file": "P.csv", "index_entry": "P.csv#0", "index_name": "Paciaudi, Abate Paolo Maria", "page": "360n",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md", "location": "第14章，印刷页360注2；OCR L219",
        "span": "line 219; print p. 360 n. 2", "quote": "letter to Paciaudi, edited by Charles Nisard",
        "summary": "Haskell的注释提及一封致Paciaudi的信；索引以“Paciaudi, Abate Paolo Maria”定位第360页注2。",
        "description_zh": "本卡登记书后索引所列Abate Paolo Maria Paciaudi。第14章第360页注2提及一封致Paciaudi的信；正文在该注中仅用姓氏，索引提供Abate Paolo Maria全名形式。本卡不补充未由本书此处支持的生平信息。中文显示名为项目工作音译。",
        "description_en": "This card registers Abate Paolo Maria Paciaudi as named in the index. Chapter 14, page 360 note 2, mentions a letter to Paciaudi; the note uses only his surname, while the index provides the fuller form Abate Paolo Maria. The card adds no biographical details unsupported by this passage. The Chinese display name is a working transliteration.",
        "context_zh": "索引全名与注释中的姓氏共同支持书内人物身份；本次没有把文献引述转换为正式关系。",
        "context_en": "The indexed name and the surname in the note support the source-local person identity; this registration does not turn the bibliographic reference into a formal relation.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Paciaudi, Abate Paolo Maria", "S1"), ("正文称名", "Paciaudi", "S2")],
    },
    {
        "candidate": "cand-1829", "group": "new-person:paolini-pietro-aa29b3e319",
        "ku": "units/persons/pietro-paolini", "card": "04-knowledge/units/persons/pietro-paolini.md",
        "name_zh": "皮耶特罗·保利尼", "name_en": "Pietro Paolini",
        "index_file": "P.csv", "index_entry": "P.csv#28", "index_name": "Paolini, Pietro", "page": "",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iii.md", "location": "第5章第III节注150，印刷页150注1；OCR L150",
        "span": "line 150; print p. 150 n. 1", "quote": "The Death of Wallenstein by Pietro Paolini",
        "summary": "Haskell在注释中将《瓦伦斯坦之死》归于Pietro Paolini；索引列出“Paolini, Pietro”，未标页码。",
        "description_zh": "本卡登记哈斯克尔第5章第III节第150页注1所称Pietro Paolini。注释将《瓦伦斯坦之死》归于Paolini，并指向Marabottini 1963；书后索引列出“Paolini, Pietro”但未标页码。本卡保留Haskell的归属陈述，不据此新增作品关系或进一步断言。中文显示名为项目工作音译。",
        "description_en": "This card records Pietro Paolini named in Chapter 5, section III, page 150 note 1. The note attributes The Death of Wallenstein to Paolini and refers to Marabottini (1963); the index lists “Paolini, Pietro” without a page number. The card preserves Haskell's attribution without creating a work relation or making a further claim. The Chinese display name is a working transliteration.",
        "context_zh": "S2关系候选st-chp5-notes-l126-165-l150-wallenstein-authorship保留为来源归属，待S6核对作品端点和边界；本次不登记正式关系。",
        "context_en": "The S2 candidate st-chp5-notes-l126-165-l150-wallenstein-authorship remains a source-attributed claim pending S6 review of the work endpoint and scope; this registration creates no formal relation.",
        "relation_ids": ["st-chp5-notes-l126-165-l150-wallenstein-authorship"],
        "endpoints": [("st-chp5-notes-l126-165-l150-wallenstein-authorship", "cand-1830", "cand-1829", "created_by", "The Death of Wallenstein by Pietro Paolini")],
        "name_rows": [("索引姓名", "Paolini, Pietro", "S1"), ("正文姓名", "Pietro Paolini", "S2")],
    },
    {
        "candidate": "cand-1835", "group": "new-person:giulio-parigi-905380a51e",
        "ku": "units/persons/giulio-parigi", "card": "04-knowledge/units/persons/giulio-parigi.md",
        "name_zh": "朱利奥·帕里吉", "name_en": "Giulio Parigi",
        "index_file": "P.csv", "index_entry": "P.csv#34", "index_name": "Parigi, Giulio", "page": "95",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_i.md", "location": "第4章第I节，印刷页95；OCR L14",
        "span": "line 14; print p. 95", "quote": "Giulio Parigi",
        "summary": "Haskell将Giulio Parigi列在Paolo Giordano II宫廷周围的艺术家与音乐家中；索引以“Parigi, Giulio”指向第95页。",
        "description_zh": "本卡登记哈斯克尔第4章第I节第95页所称Giulio Parigi。正文将他列在围绕Paolo Giordano II的艺术家与音乐家群体中；书后索引以“Parigi, Giulio”指向该页。本卡只记录来源所载姓名和语境，不推定任职或正式隶属。中文显示名为项目工作音译。",
        "description_en": "This card records Giulio Parigi named on page 95 of Chapter 4, section I. The passage lists him among the artists and musicians around Paolo Giordano II; the index lists “Parigi, Giulio” at that page. The card records only the source's name and context and does not infer an office or formal affiliation. The Chinese display name is a working transliteration.",
        "context_zh": "正文是群体语境，没有明确任职或隶属；本次不建立正式关系。",
        "context_en": "The passage gives a group context without specifying an office or affiliation; this registration creates no formal relation.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Parigi, Giulio", "S1"), ("正文姓名", "Giulio Parigi", "S2")],
    },
]


def make_source(t: dict, index: bool) -> dict:
    if index:
        return {
            "citation": f"Francis Haskell, *Patrons and Painters*, index, {t['index_file']}.",
            "location": f"书后索引，{t['index_entry']}" + (f"；指向印刷页{t['page']}" if t["page"] else "；未标页码"),
            "sentence_summary": f"索引以“{t['index_name']}”为主条" + (f"并指向印刷页{t['page']}。" if t["page"] else "，未标页码。"),
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": f"02-sources/03-Index/03-2-Index-CSV/{t['index_file']}", "source_span": t["index_entry"]},
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
    parser = argparse.ArgumentParser(description="Register four S3-new person groups, including a direct relation endpoint.")
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
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Harley、Paciaudi、Paolini与Parigi四组索引／正文人物登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组，各登记一个KU。Paolini归属断言`st-chp5-notes-l126-165-l150-wallenstein-authorship`保留待S6核对作品端点；Harley纪念碑语境、Paciaudi书目信息及Parigi群体语境不转换为formal relation。未新增外部来源或relation row。\n\n"
        + f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        + f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        + f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Harley、Paciaudi、Paolini与Parigi（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，各登记一张KU；Paolini的作品归属候选保留待S6核对，未新增正式关系。"
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
