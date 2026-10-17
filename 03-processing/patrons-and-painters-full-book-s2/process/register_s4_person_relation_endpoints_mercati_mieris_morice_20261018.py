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
ANCHOR = "s4-person-relation-endpoints-mercati-mieris-morice-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


TARGETS = [
    {
        "candidate": "cand-1654", "group": "new-person:battista-giovanni-mercati-5106be2253",
        "ku": "units/persons/giovanni-battista-mercati", "card": "04-knowledge/units/persons/giovanni-battista-mercati.md",
        "name_zh": "乔瓦尼·巴蒂斯塔·梅尔卡蒂", "name_en": "Giovanni Battista Mercati",
        "index_entry": "M.csv#194", "index_name": "Mercati, Giovanni Battista", "page": "121n",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md", "location": "第5章脚注2，印刷页121n",
        "span": "footnote 2, printed p. 121n", "quote": "a print by Giovanni Battista Mercati",
        "summary": "Haskell的实质性脚注称该版画由Giovanni Battista Mercati制作；书后索引以“Mercati, Giovanni Battista”指向第121页注。",
        "relation_ids": ["st-chp5-note-p121-n2-print-created-by"],
        "endpoints": [("st-chp5-note-p121-n2-print-created-by", "cand-6092", "cand-1654", "created_by", "print by Giovanni Battista Mercati")],
        "description_zh": "本卡登记哈斯克尔第5章脚注中的Giovanni Battista Mercati。第121页注称一幅版画由Mercati制作；书后索引以“Mercati, Giovanni Battista”指向该页注。来源未在此给出制作日期，且所引文献未作独立核查，本卡不补写相关事实。中文显示名为项目工作音译。",
        "description_en": "This card records the Giovanni Battista Mercati named in Chapter 5's footnote. The note on page 121 says that a print was made by Mercati; the index lists “Mercati, Giovanni Battista” at that note. No date is supplied here, and the cited materials were not independently checked; this card adds no such facts. The Chinese display name is a working transliteration.",
        "context_zh": "版画制作关系候选留待S6；本卡只登记脚注和索引所支持的人物身份。",
        "context_en": "The print-making relation candidate remains for S6; this card records only the identity supported by the footnote and index.",
        "name_rows": [("索引与脚注姓名", "Giovanni Battista Mercati", "S1、S2")],
    },
    {
        "candidate": "cand-1663", "group": "new-person:frans-mieris-van-7bf8b1dd69",
        "ku": "units/persons/frans-van-mieris", "card": "04-knowledge/units/persons/frans-van-mieris.md",
        "name_zh": "弗兰斯·范·米里斯", "name_en": "Frans van Mieris",
        "index_entry": "M.csv#203", "index_name": "Mieris, Frans van", "page": "307",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "location": "第10章，印刷页307；OCR L448",
        "span": "line 448; print p. 307", "quote": "attributed to the secondary painter Frans van Mieris",
        "summary": "Haskell称《Lady at the Virginals》当时被归于画家Frans van Mieris；索引以“Mieris, Frans van”指向第307页。",
        "relation_ids": ["st-chp10-p307-vermeer-attribution-to-mieris"],
        "endpoints": [("st-chp10-p307-vermeer-attribution-to-mieris", "cand-9234", "cand-1663", "attributed_to_frans_van_mieris_at_the_time", "attributed to the secondary painter Frans van Mieris")],
        "description_zh": "本卡登记哈斯克尔第10章所称Frans van Mieris。第307页在讨论《Lady at the Virginals》时称该画当时被归于van Mieris；书后索引以“Mieris, Frans van”指向该页。这是历史归属的来源记录，不表示该画的现行作者认定。中文显示名为项目工作音译。",
        "description_en": "This card records the Frans van Mieris named in Chapter 10. On page 307, while discussing Lady at the Virginals, Haskell says the painting was then attributed to van Mieris; the index lists “Mieris, Frans van” at that page. This is a record of a historical attribution, not the work's current accepted authorship. The Chinese display name is a working transliteration.",
        "context_zh": "该画的历史归属候选留待S6；本次登记不将其表述为作品现行作者。",
        "context_en": "The historical attribution candidate remains for S6; this registration does not present him as the work's current accepted author.",
        "name_rows": [("索引与正文姓名", "Frans van Mieris", "S1、S2")],
    },
    {
        "candidate": "cand-1702", "group": "new-person:morice-william-007a902cb7",
        "ku": "units/persons/sir-william-morice", "card": "04-knowledge/units/persons/sir-william-morice.md",
        "name_zh": "威廉·莫里斯爵士", "name_en": "Sir William Morice",
        "index_entry": "M.csv#243", "index_name": "Morice, Sir William", "page": "290",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md", "location": "第10章，印刷页290；OCR L246",
        "span": "line 246; print p. 290", "quote": "Sir William Morice bought the remaining ones that had been completed",
        "summary": "Haskell称Sir William Morice于1730年购买了已完成的其余画作；书后索引以“Morice, Sir William”指向第290页。",
        "relation_ids": ["st-chp10-p290-morice-purchase"],
        "endpoints": [("st-chp10-p290-morice-purchase", "cand-9007", "cand-1702", "sir_william_morice_bought_remaining_completed_pictures_in_1730", "Sir William Morice bought the remaining ones that had been completed")],
        "description_zh": "本卡登记哈斯克尔第10章所称Sir William Morice。第290页称他于1730年购买了已完成的其余画作；书后索引以“Morice, Sir William”指向该页。原文限定购买对象为已完成的部分，本卡不扩展为购买未完成作品。中文显示名为项目工作音译。",
        "description_en": "This card records the Sir William Morice named in Chapter 10. Page 290 says that in 1730 he bought the remaining pictures that had been completed; the index lists “Morice, Sir William” at that page. The source limits the purchase to completed pictures, and this card does not extend it to unfinished works. The Chinese display name is a working transliteration.",
        "context_zh": "S2关系候选只指Haskell所述已完成画作的购买；相关脚注记载的信件由Chaloner刊布而未独立查阅，候选留待S6。",
        "context_en": "The S2 relation candidate concerns only Haskell's report of the purchase of completed pictures. The cited letter noted in the footnote was published by Chaloner and was not independently consulted; the candidate remains for S6.",
        "name_rows": [("索引与正文姓名", "Sir William Morice", "S1、S2")],
    },
]


def source(t: dict, index: bool) -> dict:
    if index:
        return {
            "citation": "Francis Haskell, *Patrons and Painters*, index, M.csv.",
            "location": f"书后索引，{t['index_entry']}；指向印刷页{t['page']}",
            "sentence_summary": f"索引以“{t['index_name']}”为主条并指向印刷页{t['page']}。",
            "original_quotes": [{"source_span": t["index_entry"], "text": t["index_name"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": "02-sources/03-Index/03-2-Index-CSV/M.csv", "source_span": t["index_entry"]},
        }
    return {
        "citation": BOOK,
        "location": t["location"],
        "sentence_summary": t["summary"],
        "original_quotes": [{"source_span": t["span"], "text": t["quote"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": t["source_file"], "source_span": t["span"]},
    }


def make_card(t: dict) -> str:
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": [source(t, True), source(t, False)],
        "created": DATE, "updated": DATE, "process_ref": PROCESS_REF,
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    name_rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in t["name_rows"])
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
{name_rows}

### 本书相关内容

**中文：** {t['context_zh']}

**English:** {t['context_en']}

## 关系与证据

### 关系记录

当前没有登记在 `relations.csv` 中的正式关系。S2关系候选 {relation_ids} 保留来源归因并留待S6裁决；本次S4身份登记不将其转为正式关系。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register three source-backed M-index person endpoint groups.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_ku = {row["ku_id"]: row for row in manifest}
    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    accepted_paths = {line[2:] for line in accepted_lines if line.startswith("- 04-knowledge/units/")}
    statements = sync.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}

    for t in TARGETS:
        cid = t["candidate"]
        c, a = candidate_by_id[cid], alignment_by_id[cid]
        assert c.get("suggested_type") == "person"
        assert a.get("decision") == "new" and not a.get("ku_id")
        assert sync.get_group(a.get("resolution_note", "")) == t["group"]
        members = [row["candidate_id"] for row in alignments if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == t["group"]]
        assert members == [cid], (t["group"], members)
        assert c.get("index_entry_id") == t["index_entry"] and c.get("canonical_name") == t["index_name"] and c.get("index_page_range") == t["page"]
        index_row = person_sync.read_index_rows("M.csv")[int(t["index_entry"].split("#")[1])]
        assert index_row.get("Main Entry") == t["index_name"] and index_row.get("Page Numbers", "") == t["page"]
        body = (ROOT / t["source_file"]).read_text(encoding="utf-8-sig")
        assert t["quote"] in body, (cid, t["quote"])
        assert t["ku"] not in manifest_by_ku and t["card"] not in accepted_paths and not (ROOT / t["card"]).exists()
        assert not any(row.get("type") == "person" and (row.get("name_en") or "").casefold() == t["name_en"].casefold() for row in manifest)
        direct = {row["statement_id"] for row in statements if (row.get("qualifiers") or {}).get("relation_candidate") is True and cid in (row.get("subject_candidate_id"), row.get("object_candidate_id"))}
        assert direct == set(t["relation_ids"]), (cid, direct)
        for sid, subject, obj, predicate, quote in t["endpoints"]:
            row = statement_by_id[sid]
            assert (row.get("subject_candidate_id"), row.get("object_candidate_id"), row.get("predicate")) == (subject, obj, predicate)
            assert quote in row.get("original_quote", "")

    planned = [dict(row) for row in alignments]
    planned_manifest = list(manifest)
    for t in TARGETS:
        row = next(row for row in planned if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        row["ku_id"], row["process_ref"] = t["ku"], PROCESS_REF
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + f" S4登记（{DATE}）：身份组{t['group']}映射至{t['ku']}；新增一张书内来源支持的人物KU，相关S2关系候选仍待S6。"
        planned_manifest.append({"ku_id": t["ku"], "type": "person", "canonical_name": t["name_zh"], "name_en": t["name_en"], "source_task": TASK, "card_path": t["card"]})
    planned_manifest.sort(key=lambda row: row["ku_id"])
    planned_accepted = list(accepted_lines)
    for t in TARGETS:
        planned_accepted = person_sync.insert_accepted(planned_accepted, t["card"])

    baseline = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
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
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Mercati、van Mieris与Morice三组直接端点登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n三组均为单候选S3 new身份组，各登记一个KU。Mercati的脚注身份保留转引范围；van Mieris仅记录《Lady at the Virginals》的历史归属；"
        "Morice的购买范围限定为已完成画作，脚注所引信件未独立查阅。关系候选留待S6，未新增外部来源、正式关系或backlog项目。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Mercati、van Mieris与Morice（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。三组均为S3 new，各登记一张KU；关系候选留待S6。van Mieris仅记载为书中所述历史归属对象；Morice的购买对象限于已完成作品；"
        "Mercati身份来自Haskell脚注，所引材料未独立核查。未新增外部来源或正式关系。"
    )

    if args.dry_run:
        print(f"dry-run passed: three singleton person groups; index/source/S2 endpoint checks passed; manifest={len(manifest)}->{len(planned_manifest)}; person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; KU={len(planned_manifest)}; external_sources_added=0; relation_rows_added=0; no files changed")
        return 0
    for rel_path, card in cards.items():
        (ROOT / rel_path).write_text(card, encoding="utf-8", newline="\n")
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    ACCEPTED_PATH.write_text("\n".join(planned_accepted) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: groups=3; candidate_mappings=3; KU={len(planned_manifest)}; person_registered={stats['person']['registered_groups']}/{stats['person']['registered_members']}; person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; external_sources_added=0; relation_rows_added=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
