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
ANCHOR = "s4-person-relation-endpoints-mattei-mazenta-mazzoni-menzini-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
BOOK = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def book_source(t: dict) -> dict:
    return {
        "citation": BOOK,
        "location": t["location"],
        "sentence_summary": t["summary"],
        "original_quotes": [{"source_span": t["span"], "text": t["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": t["source_file"],
            "source_span": t["span"],
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
        "candidate": "cand-1580",
        "group": "new-person:mattei-tommaso-037aacedcb",
        "ku": "units/persons/tommaso-mattei",
        "card": "04-knowledge/units/persons/tommaso-mattei.md",
        "name_zh": "托马索·马泰",
        "name_en": "Tommaso Mattei",
        "index_entry": "M.csv#119",
        "index_file": "M.csv",
        "index_name": "Mattei, Tommaso",
        "index_page": "221",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章，印刷页221；OCR L123–124",
        "span": "lines 123–124; print p. 221",
        "quote": "the Roman architect Tommaso Mattei",
        "summary": "Haskell称Ferrara大主教宫于1710年由罗马建筑师Tommaso Mattei建造；索引以“Mattei, Tommaso”指向该页。",
        "relation_ids": ["st-chp8-p221-palace-built-by-mattei"],
        "endpoints": [
            ("st-chp8-p221-palace-built-by-mattei", "cand-1580", "cand-2306", "built_palace_as_architect", "the Roman architect Tommaso Mattei")
        ],
        "description_zh": "本卡登记哈斯克尔第8章具名的Tommaso Mattei。第221页称Ferrara大主教宫于1710年由罗马建筑师Mattei建造；书后索引以“Mattei, Tommaso”指向该页。此处保留Haskell的书内陈述，不延伸为未具名委托人、职务或其他生平事实。中文显示名为项目工作音译。",
        "description_en": "This card records the Tommaso Mattei named in Chapter 8. Page 221 says that the Archbishop's Palace in Ferrara was built in 1710 by the Roman architect Mattei; the index lists “Mattei, Tommaso” at that page. The entry retains Haskell's account and adds no unnamed patron, office, or other biographical facts. The Chinese display name is a working transliteration.",
        "context_zh": "第8章下一页还以“his architect”指称Mattei；相关关系候选只按S2原记录留待S6，不在本次登记中新增关系边。",
        "context_en": "The next page of Chapter 8 also refers to Mattei as “his architect.” The relation candidate remains for S6 under its S2 record; this registration adds no relation edge.",
        "name_rows": [("索引与正文姓名", "Tommaso Mattei", "S1、S2")],
    },
    {
        "candidate": "cand-1601",
        "group": "new-person:ambrogio-mazenta-f50481318d",
        "ku": "units/persons/ambrogio-mazenta",
        "card": "04-knowledge/units/persons/ambrogio-mazenta.md",
        "name_zh": "安布罗焦·马曾塔",
        "name_en": "Ambrogio Mazenta",
        "index_entry": "M.csv#140",
        "index_file": "M.csv",
        "index_name": "Mazenta, Ambrogio",
        "index_page": "106",
        "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
        "location": "第4章，印刷页106；OCR L96",
        "span": "line 96; print p. 106",
        "quote": "notably the Barnabite monk Ambrogio Mazenta",
        "summary": "Haskell称Ambrogio Mazenta为Barnabite修士及Cassiano通信对象之一，并称其重要的Leonardo手稿收藏在其去世前已散佚；索引以“Mazenta, Ambrogio”指向该页。",
        "relation_ids": [
            "st-chp4-sec-ii-l91-99-cassiano-corresponded-with-leonardo-manuscript-owners",
            "st-chp4-sec-ii-l91-99-mazenta-collection-reconstructed",
        ],
        "endpoints": [
            ("st-chp4-sec-ii-l91-99-cassiano-corresponded-with-leonardo-manuscript-owners", "cand-2036", "cand-1601", "corresponded_with", "notably the Barnabite monk Ambrogio Mazenta"),
            ("st-chp4-sec-ii-l91-99-mazenta-collection-reconstructed", "cand-5788", "cand-1601", "dispersed_before_owner_death", "important collection had been dispersed"),
        ],
        "description_zh": "本卡登记哈斯克尔第4章具名的Barnabite修士Ambrogio Mazenta。第106页称他是Cassiano重要的通信对象之一，并称其Leonardo手稿收藏在他去世前已散佚、后来由Galeazzo Arconato大部分重建。上述内容保留为Haskell的报告，本卡不补写收藏清单或人物生平。中文显示名为项目工作音译。",
        "description_en": "This card records the Barnabite monk Ambrogio Mazenta named in Chapter 4. Page 106 calls him one of Cassiano's notable correspondents and says his Leonardo manuscript collection had been dispersed before his death and later largely reconstructed by Galeazzo Arconato. These points remain Haskell's account; this card adds no collection inventory or biography. The Chinese display name is a working transliteration.",
        "context_zh": "通信与收藏散佚／重建两条候选均留待S6；本卡不将Haskell的叙述转为正式关系。",
        "context_en": "Both candidates concerning correspondence and the collection's dispersal/reconstruction remain for S6; this card does not convert Haskell's account into formal relations.",
        "name_rows": [("索引与正文姓名", "Ambrogio Mazenta", "S1、S2")],
    },
    {
        "candidate": "cand-1603",
        "group": "new-person:mazzoni-nicola-3547657524",
        "ku": "units/persons/nicola-mazzoni",
        "card": "04-knowledge/units/persons/nicola-mazzoni.md",
        "name_zh": "尼科拉·马佐尼",
        "name_en": "Nicola Mazzoni",
        "index_entry": "M.csv#143",
        "index_file": "M.csv",
        "index_name": "Mazzoni, Nicola",
        "index_page": "337n",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章脚注2，印刷页337n；OCR L204",
        "span": "footnote 2, line 204; print p. 337n",
        "quote": "Niccola Mazzoni",
        "summary": "Haskell转引一封写给Prato书商Niccola Mazzoni的信；索引主条拼作“Nicola”，指向第337页注。",
        "relation_ids": ["st-chp13-p337-note2-pasquali-letter-to-mazzoni"],
        "endpoints": [
            ("st-chp13-p337-note2-pasquali-letter-to-mazzoni", "cand-1844", "cand-1603", "wrote_to_bookseller_about_tuscan_censorship", "the Prato bookseller Niccola Mazzoni")
        ],
        "description_zh": "本卡登记哈斯克尔第13章脚注所称Prato书商Nicola Mazzoni。脚注正文拼作“Niccola Mazzoni”，而书后索引主条写作“Mazzoni, Nicola”；两种书内拼写均保留，不判定哪一种为规范拼法。Haskell称其所引信件由Nuti于1941年刊布；本卡不表示已独立查阅信件原件。中文显示名为项目工作音译。",
        "description_en": "This card records the Prato bookseller Nicola Mazzoni named in Chapter 13's footnote. The footnote spells the name “Niccola Mazzoni,” while the index entry is “Mazzoni, Nicola”; both book forms are preserved without selecting a standard spelling. Haskell says the cited letter was published by Nuti in 1941; this card does not imply independent consultation of the letter. The Chinese display name is a working transliteration.",
        "context_zh": "该脚注报告Pasquali写给Mazzoni的信，并经Nuti（1941）转引；书信内容及其中“qui”所指保持S2限定，关系候选留待S6。",
        "context_en": "The footnote reports a letter from Pasquali to Mazzoni through Nuti (1941). The letter's contents and the referent of “qui” retain the S2 qualifications; the relation candidate remains for S6.",
        "name_rows": [
            ("索引姓名拼写", "Nicola Mazzoni", "S1"),
            ("脚注姓名拼写", "Niccola Mazzoni", "S2（Haskell转引Nuti，1941）"),
        ],
    },
    {
        "candidate": "cand-1653",
        "group": "new-person:benedetto-menzini-b45fd70cd1",
        "ku": "units/persons/benedetto-menzini",
        "card": "04-knowledge/units/persons/benedetto-menzini.md",
        "name_zh": "贝内代托·门齐尼",
        "name_en": "Benedetto Menzini",
        "index_entry": "M.csv#193",
        "index_file": "M.csv",
        "index_name": "Menzini, Benedetto",
        "index_page": "230",
        "source_file": "02-sources/02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章，印刷页230；OCR L229–230",
        "span": "lines 229–230; print p. 230",
        "quote": "Benedetto Menzini and Scipione Maffei",
        "summary": "Haskell称Ferdinand支持Benedetto Menzini等作家，但未给出具体书名、金额或正式委托；索引以“Menzini, Benedetto”指向该页。",
        "relation_ids": ["st-chp8-p230-ferdinand-supported-benedetto-menzini"],
        "endpoints": [
            ("st-chp8-p230-ferdinand-supported-benedetto-menzini", "cand-1609", "cand-1653", "ferdinand_supported_benedetto_menzini", "Benedetto Menzini")
        ],
        "description_zh": "本卡登记哈斯克尔第8章称为writer的Benedetto Menzini。第230页称Ferdinand支持Menzini等作家，但未给出具体书名、金额或正式委托；本卡不补充这些细节。中文显示名为项目工作音译。",
        "description_en": "This card records Benedetto Menzini, whom Haskell calls a writer in Chapter 8. Page 230 says Ferdinand supported Menzini and other writers but gives no specific title, amount, or formal commission; this card adds none. The Chinese display name is a working transliteration.",
        "context_zh": "来源所述支持关系候选留待S6；不将其扩写为具体资助或委托。",
        "context_en": "The source-reported support candidate remains for S6 and is not expanded into a specific subsidy or commission.",
        "name_rows": [("索引与正文姓名", "Benedetto Menzini", "S1、S2")],
    },
]


def make_card(t: dict) -> str:
    frontmatter = {
        "title": f"{t['name_zh']}（{t['name_en']}）",
        "name_en": t["name_en"],
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [index_source(t), book_source(t)],
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
    parser = argparse.ArgumentParser(description="Register four source-backed S4 person endpoint groups.")
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
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate.get("suggested_type") == "person"
        assert alignment.get("decision") == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == t["group"]
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new"
            and sync.get_group(row.get("resolution_note", "")) == t["group"]
        ]
        assert members == [cid], (t["group"], members)
        assert candidate.get("index_entry_id") == t["index_entry"]
        assert candidate.get("canonical_name") == t["index_name"]
        assert candidate.get("index_page_range") == t["index_page"]
        index_rows = person_sync.read_index_rows(t["index_file"])
        index_row = index_rows[int(t["index_entry"].split("#")[1])]
        assert index_row.get("Main Entry") == t["index_name"]
        assert index_row.get("Page Numbers", "") == t["index_page"]
        body = (ROOT / t["source_file"]).read_text(encoding="utf-8-sig")
        assert t["quote"] in body, (cid, t["quote"])
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
        row = next(row for row in planned_alignments if row.get("candidate_id") == t["candidate"] and not row.get("external_source"))
        row["ku_id"] = t["ku"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = row.get("resolution_note", "").rstrip() + (
            f" S4登记（{DATE}）：身份组{t['group']}映射至{t['ku']}；新增一张书内来源支持的人物KU，"
            "相关S2关系候选仍待S6。"
        )
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
    log_rows = [
        f"- `{t['candidate']}`（`{t['group']}`）→ [{t['name_zh']}（{t['name_en']}）]"
        f"(../../../{t['card']})；S2关系候选"
        f"{'、'.join(f'`{sid}`' for sid in t['relation_ids'])}留待S6。{t['context_zh']}"
        for t in TARGETS
    ]
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Mattei、Mazenta、Mazzoni与Menzini四组直接端点登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组，各登记一个人物KU。Mattei与Mazenta的登记保留原书建筑及通信／收藏表述的来源限定；"
        "Nicola Mazzoni的索引拼写与脚注“Niccola”异形并列保存，书信依据仍为Haskell经Nuti的转引；"
        "Menzini的支持表述不扩写为具体资助或委托。关系候选均待S6；未新增正式关系、外部来源或backlog项目。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Mattei、Mazenta、Mazzoni与Menzini（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，各登记一张KU；关系候选留待S6。Nicola Mazzoni索引主条与脚注的Niccola拼写均保留，"
        "脚注所涉信件仍按Haskell转引Nuti（1941）的范围记录；未新增外部来源或正式关系。"
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
