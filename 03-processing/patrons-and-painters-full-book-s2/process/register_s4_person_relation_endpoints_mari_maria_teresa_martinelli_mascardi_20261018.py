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
ANCHOR = "s4-person-relation-endpoints-mari-maria-teresa-martinelli-mascardi-20261018"
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
        "candidate": "cand-1543",
        "group": "new-person:cosimo-mari-23dde1b6dd",
        "ku": "units/persons/cosimo-mari",
        "card": "04-knowledge/units/persons/cosimo-mari.md",
        "name_zh": "科西莫·马里",
        "name_en": "Cosimo Mari",
        "index_entry": "M.csv#81",
        "index_file": "M.csv",
        "index_name": "Mari, Cosimo",
        "index_page": "409",
        "source_file": "02-sources/02-Markdown/20_CHP-20Postscript.md",
        "location": "第20章后记，印刷页409；OCR L192–193",
        "span": "lines 192–193; print p. 409",
        "quote": "bequeathed to Cosimo Mari two paintings by Tiepolo",
        "summary": "Haskell转述Da Pozzo公布的遗嘱，称Algarotti将两幅Tiepolo画作遗赠给Cosimo Mari；书后索引以“Mari, Cosimo”指向该页。",
        "relation_ids": ["st-chp20-p409-tiepolo-pictures-bequeathed-to-cosimo-mari"],
        "endpoints": [
            ("st-chp20-p409-tiepolo-pictures-bequeathed-to-cosimo-mari", "cand-0041", "cand-1543", "bequeaths_two_tiepolo_pictures_with_named_subjects_to_cosimo_mari", "bequeathed to Cosimo Mari")
        ],
        "description_zh": "本卡登记哈斯克尔第20章后记中的Cosimo Mari。第409页转述Da Pozzo公布的遗嘱，称Algarotti将两幅Tiepolo画作遗赠给他；此处登记限于书中指称的人物，遗嘱文本和作品身份未由本卡独立核实。中文显示名为项目工作音译。",
        "description_en": "This card records the Cosimo Mari named in Chapter 20's postscript. On page 409, Haskell reports Da Pozzo's publication of a will and says that Algarotti bequeathed two paintings by Tiepolo to him. The entry is limited to the person named in the book; the will text and the identities of the paintings are not independently verified here. The Chinese display name is a working transliteration.",
        "context_zh": "Haskell将该遗赠说法归于Da Pozzo公布的遗嘱；相关候选关系留待S6，脚注3所涉遗嘱依据仍按S2记录保留待核。",
        "context_en": "Haskell attributes the reported bequest to a will published by Da Pozzo. The relation candidate remains for S6, and the will evidence associated with note 3 remains subject to the S2 review record.",
        "name_rows": [("索引与正文姓名", "Cosimo Mari", "S1、S2")],
    },
    {
        "candidate": "cand-1545",
        "group": "new-person:holy-maria-roman-teresa-b39636bd88",
        "ku": "units/persons/maria-teresa-holy-roman-empress",
        "card": "04-knowledge/units/persons/maria-teresa-holy-roman-empress.md",
        "name_zh": "玛丽亚·特蕾莎",
        "name_en": "Empress Maria Teresa",
        "index_entry": "M.csv#83",
        "index_file": "M.csv",
        "index_name": "Maria Teresa, Holy Roman Empress",
        "index_page": "335",
        "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章，印刷页335；OCR L36",
        "span": "line 36; print p. 335",
        "quote": "It was dedicated to the Empress Maria Teresa",
        "summary": "Haskell称1745年版《耶路撒冷》题献给Empress Maria Teresa；索引以“Maria Teresa, Holy Roman Empress”指向该页。",
        "relation_ids": ["st-chp13-p335-gerusalemme-dedicated-to-maria-teresa"],
        "endpoints": [
            ("st-chp13-p335-gerusalemme-dedicated-to-maria-teresa", "cand-9990", "cand-1545", "dedicated_to_empress_maria_teresa", "dedicated to the Empress Maria Teresa")
        ],
        "description_zh": "本卡登记哈斯克尔第13章所称Empress Maria Teresa。第335页称1745年版《耶路撒冷》题献给她，并将其奢华品味与统治时期Schönbrunn的装饰相联系；书后索引列名“Maria Teresa, Holy Roman Empress”。本卡只记录来源中的身份称名和语境，不扩展人物生平或独立核实相关历史判断。中文显示名为项目工作音译。",
        "description_en": "This card records the Empress Maria Teresa named in Chapter 13. Page 335 says that the 1745 edition of the Gerusalemme was dedicated to her and associates her taste for luxury with decorations at Schönbrunn during her rule; the index lists “Maria Teresa, Holy Roman Empress.” This entry records the source's naming and context without adding a biography or independently verifying the historical claims. The Chinese display name is a working transliteration.",
        "context_zh": "正文称名“Empress Maria Teresa”与索引称名“Maria Teresa, Holy Roman Empress”并列保存；题献关系候选留待S6。关于Schönbrunn的表述作为Haskell的作者叙述保留，不登记为第二条正式关系。",
        "context_en": "The body form “Empress Maria Teresa” and the index form “Maria Teresa, Holy Roman Empress” are both preserved. The dedication candidate remains for S6. The Schönbrunn statement is retained as Haskell's authorial account and is not registered as a second formal relation.",
        "name_rows": [
            ("正文姓名与称号", "Empress Maria Teresa", "S2"),
            ("索引姓名与称号", "Maria Teresa, Holy Roman Empress", "S1"),
        ],
    },
    {
        "candidate": "cand-1553",
        "group": "new-person:domenico-martinelli-8fc1406b14",
        "ku": "units/persons/domenico-martinelli",
        "card": "04-knowledge/units/persons/domenico-martinelli.md",
        "name_zh": "多梅尼科·马蒂内利",
        "name_en": "Domenico Martinelli",
        "index_entry": "M.csv#92",
        "index_file": "M.csv",
        "index_name": "Martinelli, Domenico",
        "index_page": "201",
        "source_file": "02-sources/02-Markdown/07_CHP-7_sec_v.md",
        "location": "第7章，印刷页201；OCR L54",
        "span": "line 54; print p. 201",
        "quote": "Domenico Martinelli came to build the town palace of the Liechtenstein family in 1691",
        "summary": "Haskell称Domenico Martinelli于1691年来建造Liechtenstein家族的城市宅邸；索引以“Martinelli, Domenico”指向该页。",
        "relation_ids": ["st-chp7-p201-v-martinelli-town-palace-1691"],
        "endpoints": [
            ("st-chp7-p201-v-martinelli-town-palace-1691", "cand-7317", "cand-1553", "came_to_build_town_palace_in_1691", "Domenico Martinelli came to build")
        ],
        "description_zh": "本卡登记哈斯克尔第7章具名的Domenico Martinelli。第201页称他于1691年来建造Liechtenstein家族的城市宅邸；书后索引以“Martinelli, Domenico”指向该页。原文没有说明工程完成时间或具体合同，本卡不作此类推断。中文显示名为项目工作音译。",
        "description_en": "This card records the Domenico Martinelli named in Chapter 7. Page 201 says that he came to build the Liechtenstein family's town palace in 1691; the index lists “Martinelli, Domenico” at that page. The source does not state a completion date or identify a specific contract, and this card makes neither inference. The Chinese display name is a working transliteration.",
        "context_zh": "本条只登记人物身份及Haskell的书内叙述；城市宅邸仍是独立地点候选，相关关系候选留待S6。",
        "context_en": "This entry records only the person's identity and Haskell's account. The town palace remains a separate place candidate, and the relation candidate remains for S6.",
        "name_rows": [("索引与正文姓名", "Domenico Martinelli", "S1、S2")],
    },
    {
        "candidate": "cand-1560",
        "group": "new-person:agostino-mascardi-04145514b9",
        "ku": "units/persons/agostino-mascardi",
        "card": "04-knowledge/units/persons/agostino-mascardi.md",
        "name_zh": "阿戈斯蒂诺·马斯卡尔迪",
        "name_en": "Agostino Mascardi",
        "index_entry": "M.csv#99",
        "index_file": "M.csv",
        "index_name": "Mascardi, Agostino",
        "index_page": "157",
        "source_file": "02-sources/02-Markdown/06_CHP-6_sec_iv.md",
        "location": "第6章，印刷页157；OCR L56",
        "span": "line 56; print p. 157",
        "quote": "The vogue of this work, which later caught the fancy of Lord Shaftesbury, was largely due to Agostino Mascardi",
        "summary": "Haskell称《The Table》的流行在很大程度上归于Agostino Mascardi，并称其于1629年译作并附长篇注释；同页还称他为Urban VIII时期罗马大学的修辞学教授。索引以“Mascardi, Agostino”指向该页。",
        "relation_ids": ["st-chp6-p157-mascardi-professorship", "st-chp6-p157-table-vogue-mascardi"],
        "endpoints": [
            ("st-chp6-p157-mascardi-professorship", "cand-1560", "cand-6394", "professorship_at_university", "well-known Professore d’Eloquenza at Rome University"),
            ("st-chp6-p157-table-vogue-mascardi", "cand-1560", "cand-6390", "translation_and_commentary_promoted_vogue", "largely due to Agostino Mascardi"),
        ],
        "description_zh": "本卡登记哈斯克尔第6章所称Agostino Mascardi。第157页将《The Table》的流行“很大程度上”归于他，并称他于1629年翻译该作并附长篇注释；同页称其为Urban VIII时期罗马大学的修辞学教授。上述内容均作为Haskell的来源叙述保留，本卡不独立验证其因果判断、任职或作品版本。中文显示名为项目工作音译。",
        "description_en": "This card records the Agostino Mascardi named in Chapter 6. Page 157 says that the vogue of The Table was “largely” due to him and that he translated it with a long commentary in 1629; the same page identifies him as a professor of rhetoric at Rome University under Urban VIII. These points are retained as Haskell's account and are not independently verified here, including its causal wording, appointment, or edition history. The Chinese display name is a working transliteration.",
        "context_zh": "两条关于任教与翻译/声望的S2关系候选均留待S6；Rome University与cand-5169（Sapienza）的身份对应仍待S3处理，不在本次扩写或定边。",
        "context_en": "Both S2 relation candidates concerning the professorship and the translation/reception remain for S6. The identity of Rome University with cand-5169 (Sapienza) remains for S3 review and is not resolved or formalized here.",
        "name_rows": [("索引与正文姓名", "Agostino Mascardi", "S1、S2")],
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
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S4 person：Cosimo Mari、Maria Teresa、Domenico Martinelli与Agostino Mascardi四组直接端点登记（{DATE}）\n\n"
        + "\n".join(log_rows)
        + "\n\n四组均为单候选S3 new身份组，逐组登记一个人物KU。Maria Teresa正文称名与索引称号并列保留；"
        "Cosimo Mari遗嘱叙述、Martinelli的“came to build”限定、Mascardi关于任教及《The Table》的来源归因均按原书语气保留。"
        "关系候选留待S6；Rome University与cand-5169（Sapienza）的身份对应仍待S3。未新增正式关系、外部来源或backlog项目。\n\n"
        f"登记后人物类型S4为{sync.fmt(stats['person']['registered_groups'])}组/"
        f"{sync.fmt(stats['person']['registered_members'])}条已登记、{sync.fmt(stats['person']['pending_groups'])}组/"
        f"{sync.fmt(stats['person']['pending_members'])}条待登记；全书KU={len(planned_manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text += (
        f"\n\n### S4人物身份组登记：Mari、Maria Teresa、Martinelli与Mascardi（{DATE}）\n\n"
        + "；".join(f"`{t['candidate']}` → `../units/persons/{t['ku'].split('/')[-1]}.md`" for t in TARGETS)
        + "。四组均为S3 new，各登记一张KU；关系候选留待S6。Maria Teresa正文称名与索引称号并列保留；"
        "Cosimo Mari的遗嘱依据仍按S2待核记录处理，Martinelli的原文不延伸为工程完成或合同事实，"
        "Mascardi的因果性与任职内容保留为Haskell报告而未独立核实。未新增外部来源或正式关系。"
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
