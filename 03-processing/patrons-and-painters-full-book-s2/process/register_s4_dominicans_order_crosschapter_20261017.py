from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

import register_s4_archive_memmo_query_sheet_20261017 as archive_sync
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

CANDIDATES = ("cand-0941",)
GROUP = "sg3-institution-cand-0941"
KU_ID = "units/institutions/dominicans"
CARD = "04-knowledge/units/institutions/dominicans.md"
NAME_ZH = "多明我会"
NAME_EN = "Dominicans"
ANCHOR = "s4-institution-dominicans-crosschapter-20261017"

RELATION_IDS = {
    "st-chp5-p131-1636-transfer-to-barberini",
    "st-chp5-p131-dominicans-decided-to-sell-raphael-holy-family",
    "st-chp5-p131-dominicans-held-raphael-holy-family",
    "st-chp9-p270-dominican-commission",
    "st-chp9-p270-n07-benigna-dominican-church-model",
    "st-chp9-p270-n07-zanetti-dominican-alms",
}
NON_RELATION_ID = "st-chp9-p271-dominican-church-exaltation"

SOURCES = (
    {
        "file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
        "location": "第5章，印刷页131，正文行119–120",
        "span": "lines 119–120; print p.131",
        "quote": "The Dominicans of Santa Sabina, anxious to raise money, had decided to sell a Raphael Holy Family in their possession to Vincenzo Giustiniani",
        "summary": "Haskell点名 Santa Sabina 的 Dominicans，并记述其出售 Raphael Holy Family 的计划；此处指当地团体，不泛化为全体会士的行动。",
        "zh": "Haskell点名圣萨比纳的多明我会团体，并记述其出售《圣家族》的计划；此处是当地团体的行动，不泛化为全体会士。",
        "en": "Haskell names the Dominicans of Santa Sabina and reports their plan to sell the Raphael Holy Family; this is a local community’s action, not an act attributed to every Dominican.",
    },
    {
        "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章，印刷页269，正文行19",
        "span": "line 19; print p.269",
        "quote": "the Jesuits and Dominicans, for instance",
        "summary": "Haskell列举 Jesuits 与 Dominicans 为出资兴建宏伟教堂的修会；保留为复数团体名称。",
        "zh": "Haskell以耶稣会与多明我会为例，讨论出资兴建宏伟教堂的修会；保留来源中的复数团体称呼。",
        "en": "Haskell names Jesuits and Dominicans as examples of religious orders whose monks found resources for magnificent churches; the source’s collective plural is retained.",
    },
    {
        "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章，印刷页270，正文行35",
        "span": "line 35; print p.270",
        "quote": "Scarcely less imposing as patrons were the Dominicans, for whom between 1725 and 1727 Piazzetta painted his only frescoes",
        "summary": "Haskell称 Dominicans 是重要赞助者，并记述 Piazzetta 为其绘制壁画；此处保留来源的集合性归属。",
        "zh": "Haskell称 Dominicans 为重要赞助者，并记述 Piazzetta 为其绘制壁画；保留来源的集合性指称，不指定某一地方团体。",
        "en": "Haskell describes the Dominicans as important patrons and says Piazzetta painted frescoes for them; the collective attribution is retained without assigning it to a particular local community.",
    },
    {
        "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章，印刷页270，注7，正文行36",
        "span": "line 36; print p.270, note 7",
        "quote": "Domenicani Osservanti sopra le Zattere",
        "summary": "Haskell所引 Benigna 条目指称 Zattere 的 Observant Dominicans；具体教会建造事仍按来源限定保留。",
        "zh": "Haskell所引 Benigna 条目点名 Zattere 的 Observant Dominicans；其教堂建造记载保留为特定地方团体的来源报告。",
        "en": "The Benigna entry cited by Haskell names the Observant Dominicans on the Zattere; the church-building account remains a report about that local community.",
    },
    {
        "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章，印刷页270，注7，正文行102",
        "span": "line 102; print p.270, note 7",
        "quote": "the Dominicans were still collecting alms all day long for the building of their church",
        "summary": "Haskell转述 Zanetti 于1743年关于 Dominicans 为其教堂募捐的记载；不据此指定是哪一教堂。",
        "zh": "Haskell转述 Zanetti 于1743年关于 Dominicans 为其教堂募捐的记载；此句没有单独确定教堂身份。",
        "en": "Haskell relays an account by Zanetti, written in 1743, that the Dominicans collected alms for their church; this sentence alone does not identify the church.",
    },
    {
        "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章，印刷页271，正文行45",
        "span": "line 45; print p.271",
        "quote": "the most combative religious organisation in eighteenth-century Venice",
        "summary": "Haskell将有关教堂的 exaltation and triumph 语调联系到威尼斯一支好战的宗教组织；保留为作者概括，不建立关系边。",
        "zh": "Haskell把教堂的 exaltation and triumph 语调联系到十八世纪威尼斯一支好战的宗教组织；此句是作者概括，不建关系边。",
        "en": "Haskell links a church’s note of exaltation and triumph to a combative religious organization in eighteenth-century Venice; this remains an authorial characterization, not a relation edge.",
    },
    {
        "file": "02-sources/02-Markdown/09_CHP-9_sec_ii.md",
        "location": "第9章，印刷页272，正文行55",
        "span": "line 55; print p.272",
        "quote": "The contrast with the Dominicans could scarcely be greater: in S. Maria del Rosario every painting celebrates the triumph and glory of the Order",
        "summary": "Haskell以 S. Maria del Rosario 的作品颂扬 the Order，与耶稣会教堂作对比；保留其修会层级语境。",
        "zh": "Haskell称 S. Maria del Rosario 的每幅画都颂扬 the Order，并与耶稣会教堂形成对比；保留修会层级的语境。",
        "en": "Haskell says every painting in S. Maria del Rosario celebrates the triumph and glory of the Order, contrasting it with the Jesuit church; the order-level context is retained.",
    },
    {
        "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章，印刷页338，正文行67–68",
        "span": "lines 67–68; print p.338",
        "quote": "the local-Dominicans and the Portuguese",
        "summary": "Haskell称 Jesuits 的本地对手包括 local-Dominicans；保留其地方限定，不扩写具体修院或成员。",
        "zh": "Haskell称 Jesuits 的本地对手包括 local-Dominicans；保留地方限定，不扩写具体修院或成员。",
        "en": "Haskell names the local-Dominicans among the Jesuits’ local adversaries; the local qualifier is retained without adding a convent or individual members.",
    },
)


def source_row(item: dict) -> dict:
    return {
        "citation": BOOK_CITATION,
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["file"],
            "source_span": item["span"],
        },
    }


def source_link(item: dict, index: int) -> str:
    relative = item["file"].removeprefix("02-sources/")
    return f"[S{index}：{item['location']}](../../../02-sources/{relative})"


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": [source_row(item) for item in SOURCES],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    table_rows = "\n".join(
        f"| {item['zh']} | {item['en']} | {source_link(item, index)}（S{index}） |"
        for index, item in enumerate(SOURCES, 1)
    )
    relation_list = "、".join(f"`{statement_id}`" for statement_id in sorted(RELATION_IDS))
    body = f"""## 内容

### 描述

**中文：** 本卡以 Haskell 的复数称呼 Dominicans 登记多明我会这一修会层级的机构身份。S3 将索引 D.csv#43（印刷页270–272）与第5章“Dominicans of Santa Sabina”、第9章威尼斯语境中的 Dominicans／the Order、以及第13章 local-Dominicans 归入同一 institution 组。书内还区分了具体地方团体（如 Santa Sabina 与 Zattere 的 Observant Dominicans）及其所在教堂；本卡记录修会层级名称，不把地方修院、教堂、个别成员或某一次行动合并为修会事实。各项转让、委托、募捐及作者概括均保留在对应 S2 候选的原限定内。{source_link(SOURCES[0], 1)} {source_link(SOURCES[2], 3)} {source_link(SOURCES[3], 4)} {source_link(SOURCES[7], 8)}

**English:** This unit records the institutional identity of the Dominican religious order under Haskell’s plural source form *Dominicans*. S3 grouped the D.csv#43 index entry (printed pp.270–272) with “Dominicans of Santa Sabina” in Chapter 5, the Dominicans / “the Order” in the Venetian context of Chapter 9, and “local-Dominicans” in Chapter 13. The book also distinguishes specific local communities, including Santa Sabina and the Observant Dominicans on the Zattere, and their churches. This unit records the order-level name; it does not attribute a local convent, church, individual member, or single action to the entire order. Transfers, commissions, alms reports, and authorial characterizations retain the qualifications of their S2 candidates. {source_link(SOURCES[0], 1)} {source_link(SOURCES[2], 3)} {source_link(SOURCES[3], 4)} {source_link(SOURCES[7], 8)}

### 书内指称与范围

| 语境（中文） | Context (English) | 证据 / Evidence |
|---|---|---|
{table_rows}

## 关系与证据

未登记正式关系。六条直接 S2 关系候选（{relation_list}）均留待 S6 审查；第9章 p.271 的 `{NON_RELATION_ID}` 在 S2 中不是 relation candidate，只保留为 Haskell 的组织性概括。候选 `cand-0941` 对应的地方团体与教堂范围继续按各自来源限定，不据此扩展或反推成员关系。未使用外部身份来源。"""
    return f"---\n{fm}---\n\n{body.strip()}\n"


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    if f"- {CARD}" in lines:
        raise AssertionError(f"accepted.yml already includes {CARD}")
    insert_at = next(
        (i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Dominican order institution group in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT / "scripts"))
    import build_field_facts

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    assert all(cid in candidate_by_id and candidate_by_id[cid].get("suggested_type") == "institution" for cid in CANDIDATES)
    group_rows = [
        r for r in alignments if r.get("candidate_id") in CANDIDATES and not r.get("external_source")
    ]
    assert len(group_rows) == len(CANDIDATES)
    assert all(r.get("decision") == "new" and not r.get("ku_id") for r in group_rows)
    assert all(sync.get_group(r.get("resolution_note", "")) == GROUP for r in group_rows)
    all_group_members = [
        r["candidate_id"] for r in alignments
        if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new"
        and sync.get_group(r.get("resolution_note", "")) == GROUP
    ]
    assert sorted(all_group_members) == sorted(CANDIDATES), all_group_members
    assert not (ROOT / CARD).exists() and CARD not in accepted
    assert not any(r.get("ku_id") == KU_ID or r.get("card_path") == CARD for r in manifest)
    assert not any(r.get("type") == "institution" and (r.get("name_en") or "").casefold() == NAME_EN.casefold() for r in manifest)

    statements = sync.load_statements()
    direct = [
        r for r in statements
        if set(CANDIDATES) & {r.get("subject_candidate_id"), r.get("object_candidate_id")}
    ]
    direct_ids = {r["statement_id"] for r in direct}
    relation_ids = {
        r["statement_id"] for r in direct
        if (r.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert len(direct) == 7 and direct_ids == RELATION_IDS | {NON_RELATION_ID}, (len(direct), direct_ids)
    assert relation_ids == RELATION_IDS, relation_ids

    for item in SOURCES:
        source_text = " ".join((ROOT / item["file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, (item["file"], item["quote"])
    source_ids = {r.get("source_id") for r in sync.read_csv(TABLES / "sources.csv")[1]}
    assert "haskell-1980-rev-ed" in source_ids

    planned_card = make_card()
    fm = re.match(r"\A---\n(.*?)\n---\n", planned_card, re.DOTALL)
    assert fm and isinstance(yaml.safe_load(fm.group(1)), dict)
    planned_alignment = [dict(r) for r in alignments]
    for cid in CANDIDATES:
        row = next(r for r in planned_alignment if r.get("candidate_id") == cid and not r.get("external_source"))
        row["resolution_note"] += (
            " S3 cross-chapter scope confirmation 2026-10-17: the source/index forms refer to the Dominican religious order at organizational level; "
            "Santa Sabina and Zattere communities, their churches, and individual actions remain distinct and retain their source qualifiers."
        )
        row["ku_id"] = KU_ID
        row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "institution",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD,
    }]

    with tempfile.TemporaryDirectory(prefix="pnp-s4-dominicans-preview-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_card = temp_root / CARD
        temp_card.parent.mkdir(parents=True, exist_ok=True)
        temp_card.write_text(planned_card, encoding="utf-8-sig", newline="\n")
        original_base = build_field_facts.BASE
        build_field_facts.BASE = temp_root
        try:
            facts, source_registry, warnings, cards_with_tables = build_field_facts.extract_records([planned_manifest[-1]])
        finally:
            build_field_facts.BASE = original_base
    assert not warnings, warnings
    assert cards_with_tables == 1 and len(facts) == len(SOURCES), (cards_with_tables, len(facts))
    assert all(r["evidence_status"] == "source_backed" and r["source_ids"] == ["haskell-1980-rev-ed"] for r in facts)
    assert set(source_registry) == {"haskell-1980-rev-ed"}
    build_field_facts.assign_ids(facts, TABLES / "enrichment.jsonl")
    old_facts = [
        json.loads(line) for line in (TABLES / "enrichment.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    assert not any(r.get("ku_id") == KU_ID for r in old_facts)
    planned_facts = old_facts + facts
    assert len({r["enrichment_id"] for r in planned_facts}) == len(planned_facts)
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest))
    result_text, n = re.subn(
        r"^\| \[既有字段表\]\(\.\./tables/enrichment\.jsonl\) \|.*$",
        f"| [既有字段表](../tables/enrichment.jsonl) | {sync.fmt(len(planned_facts))}条，其中{sync.fmt(sum(r.get('evidence_status') == 'unverified' for r in planned_facts))}条 unverified |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1
    process_text = archive_sync.refresh_process_type_table(PROCESS.read_text(encoding="utf-8-sig"), stats)
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### S4 institution：Dominicans 跨章修会身份组登记（{DATE}）\n\n"
        f"- `{', '.join(CANDIDATES)}`（`{GROUP}`）登记至[多明我会机构卡](../../../{CARD})；S3 以 D.csv#43 及第5章 Santa Sabina、第9章威尼斯修会语境、第13章 local-Dominicans 判断为修会层级 institution。alignment 已补充跨章范围理由：地方团体、教堂与个别行动不等同于全体修会。\n"
        f"- 8处来源引文覆盖组织称谓及地方语境；六条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6。第9章 p.271 的 `{NON_RELATION_ID}` 不是 relation candidate，不转为正式边。未使用外部身份来源。\n"
        f"- S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU={sync.fmt(len(planned_manifest))}，字段={sync.fmt(len(planned_facts))}。"
    )
    planned_accepted = insert_accepted(accepted)

    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP}; members={len(CANDIDATES)}; new_KU={KU_ID}; "
            f"source_rows={len(SOURCES)}; direct_statements={len(direct)}; relation_candidates={len(relation_ids)}; "
            f"new_field_rows={len(facts)}; registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}; "
            f"enrichment={len(old_facts)}->{len(planned_facts)}"
        )
        for fact in facts:
            print(f"  {fact['field']} | {fact['source_ref']} | {fact['evidence_status']}")
        return 0

    (ROOT / CARD).write_text(planned_card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    build_field_facts.write_jsonl(TABLES / "enrichment.jsonl", planned_facts)
    ACCEPTED.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: group={GROUP}; members={len(CANDIDATES)}; new_KU={KU_ID}; field_rows={len(facts)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"enrichment={len(old_facts)}->{len(planned_facts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
