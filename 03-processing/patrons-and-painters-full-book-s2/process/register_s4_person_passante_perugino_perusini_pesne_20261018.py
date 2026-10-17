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
ANCHOR = "s4-person-passante-perugino-perusini-pesne-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

TARGETS = [
    {
        "candidate": "cand-1854", "group": "new-person:bartolommeo-passante-776a9fc247",
        "ku": "units/persons/bartolommeo-passante", "card": "04-knowledge/units/persons/bartolommeo-passante.md",
        "name_zh": "巴托洛梅奥·帕桑特", "name_en": "Bartolommeo Passante",
        "index_file": "P.csv", "index_entry": "P.csv#54", "index_name": "Passante, Bartolommeo", "page": "206",
        "text_sources": [{
            "source_file": "02-sources/02-Markdown/08_CHP-8_sec_i.md", "location": "第8章第I节，印刷页206；OCR L38",
            "span": "line 38; print p. 206", "quote": "Ribera’s pupil, Bartolommeo Passante",
            "summary": "Haskell称Bartolommeo Passante为Ribera的学生，并说Roomer向低地国家输出其那不勒斯绘画。",
        }],
        "description_zh": "本卡登记哈斯克尔第8章第I节第206页所称Bartolommeo Passante。正文称他为Ribera的学生，并提及Roomer向低地国家输出他的那不勒斯绘画；书后索引以“Passante, Bartolommeo”指向该页。本卡保留书内称名与归属，不补充外部生平信息。中文显示名为项目工作音译。",
        "description_en": "This card records Bartolommeo Passante named on page 206 of Chapter 8, section I. The passage calls him a pupil of Ribera and mentions Roomer's trade in Neapolitan paintings by him to the Low Countries; the index lists “Passante, Bartolommeo” at that page. The card preserves the book's naming and account without adding external biography. The Chinese display name is a working transliteration.",
        "context_zh": "相关绘画归属仍按Haskell叙述记录；本次没有将其转换为正式作品关系。",
        "context_en": "The painting attribution remains recorded as Haskell's account; this registration creates no formal work relation.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Passante, Bartolommeo", "S1"), ("正文姓名", "Bartolommeo Passante", "S2")],
    },
    {
        "candidate": "cand-1883", "group": "new-person:perugino-pietro-628c4b189f",
        "ku": "units/persons/pietro-perugino", "card": "04-knowledge/units/persons/pietro-perugino.md",
        "name_zh": "彼得罗·佩鲁吉诺", "name_en": "Pietro Perugino",
        "index_file": "P.csv", "index_entry": "P.csv#84", "index_name": "Perugino, Pietro", "page": "56, 175",
        "text_sources": [
            {
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_iv.md", "location": "第2章第IV节，印刷页56；OCR L145",
                "span": "line 145; print p. 56", "quote": "Titian and Perugino",
                "summary": "Haskell在第56页转述1642年出版物对Barberini宫藏品的描述，其中列出Perugino。",
            },
            {
                "source_file": "02-sources/02-Markdown/07_CHP-7_sec_i.md", "location": "第7章第I节，印刷页175；OCR L67",
                "span": "line 67; print p. 175", "quote": "studiolo by Perugino",
                "summary": "Haskell在第175页提及Isabella d’Este书斋作品中的Perugino；书后索引将第56、175页归于同一主条。",
            },
        ],
        "description_zh": "本卡登记书后索引“Perugino, Pietro”所指人物。正文第56页和第175页均仅称Perugino：前者转述Barberini宫收藏描述，后者提及Isabella d’Este书斋作品；索引将两页列在同一条目下。本卡按该跨章书内身份组登记，不补充外部生平。中文显示名为项目工作音译。",
        "description_en": "This card records the person indexed as “Perugino, Pietro”. The book uses only “Perugino” on pages 56 and 175: the first passage recounts a description of the Barberini palace collection, while the second mentions works for Isabella d'Este's studiolo. The index places both pages under one entry. The card registers this cross-chapter, source-local identity group without adding external biography. The Chinese display name is a working transliteration.",
        "context_zh": "同一索引主条把第56与175页称名连接起来；本次不据作品提及构造创作关系。",
        "context_en": "The shared index entry links the page 56 and 175 name forms; this registration does not infer a creator relation from the mentions.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Perugino, Pietro", "S1"), ("正文称名", "Perugino", "S2，p.56；S2，p.175")],
    },
    {
        "candidate": "cand-1884", "group": "new-person:giovanni-perusini-bcbd5a7b57",
        "ku": "units/persons/giovanni-perusini", "card": "04-knowledge/units/persons/giovanni-perusini.md",
        "name_zh": "乔瓦尼·佩鲁西尼", "name_en": "Giovanni Perusini",
        "index_file": "P.csv", "index_entry": "P.csv#85", "index_name": "Perusini, Giovanni", "page": "122n",
        "text_sources": [{
            "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md", "location": "第5章第I节注，印刷页122注1；OCR L132",
            "span": "line 132; print p. 122 n. 1", "quote": "two pictures by Filippo Lauri and Giovanni Perusini",
            "summary": "Haskell的注释称Pellegrino Peri在1681年报告其店中被盗的两幅画分别由Filippo Lauri与Giovanni Perusini绘制。",
        }],
        "description_zh": "本卡登记哈斯克尔第5章第I节第122页注1所称Giovanni Perusini。注释称Pellegrino Peri于1681年报告其店中被盗的两幅画分别出自Filippo Lauri和Perusini；书后索引以“Perusini, Giovanni”定位该注。本卡保留归属的来源语境，不据此新增正式作品关系。中文显示名为项目工作音译。",
        "description_en": "This card records Giovanni Perusini named in Chapter 5, section I, page 122 note 1. The note says that in 1681 Pellegrino Peri reported two pictures stolen from his shop, by Filippo Lauri and Perusini; the index lists “Perusini, Giovanni” at that note. The card preserves the attribution's source context without creating a formal work relation. The Chinese display name is a working transliteration.",
        "context_zh": "注释报告的是两幅失窃绘画及其归属；本次保留原叙述，不建立正式边。",
        "context_en": "The note reports two stolen pictures and their attributions; this registration preserves the account and creates no formal edge.",
        "relation_ids": [],
        "name_rows": [("索引姓名", "Perusini, Giovanni", "S1"), ("正文姓名", "Giovanni Perusini", "S2")],
    },
    {
        "candidate": "cand-1888", "group": "new-person:antoine-pesne-22a62961be",
        "ku": "units/persons/antoine-pesne", "card": "04-knowledge/units/persons/antoine-pesne.md",
        "name_zh": "安托万·佩斯内", "name_en": "Antoine Pesne",
        "index_file": "P.csv", "index_entry": "P.csv#89", "index_name": "Pesne, Antoine", "page": "",
        "text_sources": [{
            "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md", "location": "第10章第II节，印刷页316；OCR L113",
            "span": "line 113; print p. 316", "quote": "his friend Antoine Pesne",
            "summary": "Haskell称Streit委托其朋友Antoine Pesne绘制Frederick the Great与Prussia王后的肖像；索引列出Pesne但未标页码。",
        }],
        "description_zh": "本卡登记哈斯克尔第10章第II节第316页所称Antoine Pesne。正文称Streit委托其朋友Pesne绘制Frederick the Great与Prussia王后的肖像；索引列出“Pesne, Antoine”但未标页码。相关朋友关系S2候选保留待S6裁决，本卡不建立正式关系。中文显示名为项目工作音译。",
        "description_en": "This card records Antoine Pesne named on page 316 of Chapter 10, section II. The passage says Streit commissioned his friend Pesne to paint Frederick the Great and the Queen of Prussia; the index lists “Pesne, Antoine” without a page number. The S2 friendship candidate remains for S6 review, and this card creates no formal relation. The Chinese display name is a working transliteration.",
        "context_zh": "S2朋友关系候选`st-chp10-p316-streit-regarded-pesne-as-friend`留待S6裁决；本次不新增正式边。",
        "context_en": "The S2 friendship candidate `st-chp10-p316-streit-regarded-pesne-as-friend` remains for S6 review; this registration adds no formal edge.",
        "relation_ids": ["st-chp10-p316-streit-regarded-pesne-as-friend"],
        "endpoints": [("st-chp10-p316-streit-regarded-pesne-as-friend", "cand-2519", "cand-1888", "identified-as-friend-of-antoine-pesne", "his friend Antoine Pesne")],
        "name_rows": [("索引姓名", "Pesne, Antoine", "S1"), ("正文姓名", "Antoine Pesne", "S2")],
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


def make_text_source(t: dict, evidence: dict) -> dict:
    return {
        "citation": BOOK, "location": evidence["location"], "sentence_summary": evidence["summary"],
        "original_quotes": [{"source_span": evidence["span"], "text": evidence["quote"]}],
        "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": evidence["source_file"], "source_span": evidence["span"]},
    }


def make_card(t: dict) -> str:
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）", "name_en": t["name_en"], "type": "person",
        "evidence_status": "source_backed", "sources": [make_index_source(t), *[make_text_source(t, e) for e in t["text_sources"]]],
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
    parser = argparse.ArgumentParser(description="Register four S3-new person groups, including the Antoine Pesne relation endpoint.")
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
        for evidence in t["text_sources"]:
            assert evidence["quote"] in (ROOT / evidence["source_file"]).read_text(encoding="utf-8-sig"), (cid, evidence["quote"])
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
    log_rows = [f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）](../../../{t['card']})；依据索引{t['index_entry']}与正文{t['text_sources'][0]['location']}登记。" for t in TARGETS]
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Passante、Perugino、Perusini与Pesne四组索引／正文登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组。Perugino的第56、175页姓氏称名由同一索引条目连接；Pesne的朋友关系候选`st-chp10-p316-streit-regarded-pesne-as-friend`保留待S6。Passante绘画、Perusini失窃画作归属均按Haskell来源语境记录，未新增formal relation或外部来源。\n\n"
        + f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        + f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        + f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Passante、Perugino、Perusini与Pesne（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，各登记一张KU；Perugino跨章称名由同一索引条目连接，Pesne的朋友关系候选保留待S6。"
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
