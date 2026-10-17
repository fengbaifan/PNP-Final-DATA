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

CANDIDATE = "cand-5529"
GROUP = "sg3-place-cand-5529"
KU_ID = "units/places/germany"
CARD = "04-knowledge/units/places/germany.md"
NAME_ZH = "德国"
NAME_EN = "Germany"
ANCHOR = "s4-place-germany-crosschapter-20261017"

RELATION_IDS = {
    "st-chp4-sec-i-l20-24-soldiered-in-germany",
    "st-chp7-p194-carlone-court-migration",
    "st-chp7-p195-lazzarini-output-germany",
    "st-chp10-p293-venetian-patronage-germany",
    "st-chp13-p334-albrizzi-travel-and-vienna-education",
    "st-chp15-p361-most-schulenburg-collection-sent-to-germany",
}
NON_RELATION_ID = "st-chp10-p295-augustus-german-patronage-comparison"

SOURCES = (
    {
        "file": "02-sources/02-Markdown/04_CHP-4_sec_i.md",
        "location": "第4章，印刷页96，正文行21",
        "span": "line 21; print p.96",
        "quote": "soldiering in Germany",
        "summary": "Haskell称 Paolo Giordano II 曾在 Germany 服役，随后迁至 Rome；未给出具体路线或时间。",
        "zh": "Haskell称 Paolo Giordano II 曾在德国服役，之后迁至罗马；没有给出具体路线或日期。",
        "en": "Haskell says Paolo Giordano II soldiered in Germany before moving to Rome; no route or date is supplied.",
    },
    {
        "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "location": "第7章，印刷页194，正文行24",
        "span": "line 24; print p.194",
        "quote": "Whole families of painters and craftsmen such as the Carlone moved into Germany and wandered from court to court.",
        "summary": "Haskell称包括 Carlone 在内的画家与工匠家族迁入 Germany 并在宫廷间流动；未列家族成员或宫廷。",
        "zh": "Haskell称包括 Carlone 在内的画家与工匠家族迁入德国并在各宫廷间流动；没有列出成员或宫廷。",
        "en": "Haskell says painter and craftsman families including the Carlone moved into Germany and travelled from court to court; the members and courts are not enumerated.",
    },
    {
        "file": "02-sources/02-Markdown/07_CHP-7_sec_iv.md",
        "location": "第7章，印刷页195，正文行42",
        "span": "line 42; print p.195",
        "quote": "who sent much of his output to Germany.",
        "summary": "Haskell称 Gregorio Lazzarini 将大量作品送往 Germany；未点出具体作品或目的地。",
        "zh": "Haskell称 Gregorio Lazzarini 将大量作品送往德国；没有指明具体作品或地点。",
        "en": "Haskell says Gregorio Lazzarini sent much of his output to Germany; no works or destinations within Germany are named.",
    },
    {
        "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章，印刷页293，正文行288–289",
        "span": "lines 288–289; print p.293",
        "quote": "finding enthusiastic patrons all over Germany.",
        "summary": "Haskell概括威尼斯艺术家在 Germany 各地仍有热心赞助者；未枚举人物。",
        "zh": "Haskell概括威尼斯艺术家在德国各地仍有热心赞助者；没有列出艺术家名单。",
        "en": "Haskell generalizes that Venetian artists continued to find enthusiastic patrons throughout Germany; the artists are not enumerated.",
    },
    {
        "file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "location": "第10章，印刷页295，正文行316",
        "span": "line 316; print p.295",
        "quote": "No sovereign in Germany could rival Augustus in his patronage or collecting",
        "summary": "Haskell在赞助比较中称 Germany 没有君主可与 Augustus 的赞助和收藏相比；此句不是已登记关系。",
        "zh": "Haskell在赞助比较中称德国没有君主可与 Augustus 的赞助和收藏相比；保留为作者比较，不转成正式关系。",
        "en": "In a patronage comparison, Haskell says no sovereign in Germany could rival Augustus in patronage or collecting; this remains an authorial comparison, not a formal relation.",
    },
    {
        "file": "02-sources/02-Markdown/13_CHP-13_intro.md",
        "location": "第13章，印刷页334，正文行26",
        "span": "line 26; print p.334",
        "quote": "he travelled widely, especially in Germany and Austria",
        "summary": "Haskell称 Albrizzi 曾广泛旅行，尤其到 Germany 与 Austria；未列出具体城市。",
        "zh": "Haskell称 Albrizzi 曾广泛旅行，尤其到德国和奥地利；没有列出具体城市。",
        "en": "Haskell says Albrizzi travelled widely, especially in Germany and Austria; no particular cities are given.",
    },
    {
        "file": "02-sources/02-Markdown/15_CHP-15_sec_i.md",
        "location": "第15章，印刷页361，正文行10–11",
        "span": "lines 10–11; print p.361",
        "quote": "most of it had long since been sent to\nGermany;",
        "summary": "Haskell称 Schulenburg 收藏的大部分早已运往 Germany；保留 most 与 long since，不推成全部或精确日期。",
        "zh": "Haskell称 Schulenburg 收藏的大部分早已运往德国；保留“大部分”和“早已”的限定，不推为全部或精确日期。",
        "en": "Haskell says most of the Schulenburg collection had long since been sent to Germany; this does not mean all of it or establish a precise date.",
    },
)


def source_row(item: dict, index: int) -> dict:
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
        "type": "place",
        "evidence_status": "source_backed",
        "sources": [source_row(item, index) for index, item in enumerate(SOURCES, 1)],
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

**中文：** 本卡登记 Haskell 多章叙述中作为地理地点使用的名称 Germany。S3 将第4章关于 Paolo Giordano II 服役地点的候选判为新 place 身份；其他章节的同名指称涉及画工迁移、作品流向、赞助者所在地域、旅行及收藏转运。本卡只记录书中这些地点指称及其限定，不据此补定现代边界、历史主权、具体路线或未列出的地点，也不把 Southern Germany 候选并入本组。第10章 p.295 的君主比较保留为 Haskell 的作者性表述；不据此建立政治实体或关系。{source_link(SOURCES[0], 1)} {source_link(SOURCES[3], 4)} {source_link(SOURCES[4], 5)}

**English:** This unit records Germany as a geographic place name used across Haskell’s chapters. S3 classified the Chapter 4 candidate for the setting of Paolo Giordano II’s military service as a new place identity. Other chapters use the same place name in accounts of artisan migration, the destination of artistic output, patronage, travel, and collection transfer. This unit records those source-defined references and their limits; it does not add modern boundaries, historical sovereignty, specific routes, or unnamed destinations, and it does not merge the separate Southern Germany candidates. The comparison of rulers on p.295 remains Haskell’s authorial statement and does not create a political entity or relation. {source_link(SOURCES[0], 1)} {source_link(SOURCES[3], 4)} {source_link(SOURCES[4], 5)}

### 书内地理指称

| 语境（中文） | Context (English) | 证据 / Evidence |
|---|---|---|
{table_rows}

## 关系与证据

尚未登记正式关系。六条直接关系候选（{relation_list}）均留待 S6 逐条审查。第10章 p.295 的 `{NON_RELATION_ID}` 在 S2 中不是 relation candidate，本卡仅保存其作者性比较语境，不将其改写为关系。未使用外部身份记录；cand-8832 与 cand-8861 的 Southern Germany 地点组保持独立。"""
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
    parser = argparse.ArgumentParser(description="Register the S3 Germany place identity group in S4")
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
    candidate = next((r for r in candidates if r.get("candidate_id") == CANDIDATE), None)
    assert candidate and candidate.get("suggested_type") == "place"
    row = next(r for r in alignments if r.get("candidate_id") == CANDIDATE and not r.get("external_source"))
    assert row["decision"] == "new" and not row.get("ku_id")
    assert sync.get_group(row.get("resolution_note", "")) == GROUP
    members = [
        r["candidate_id"] for r in alignments
        if r.get("candidate_id") and not r.get("external_source") and r.get("decision") == "new"
        and sync.get_group(r.get("resolution_note", "")) == GROUP
    ]
    assert members == [CANDIDATE], members
    assert not (ROOT / CARD).exists() and CARD not in accepted
    assert not any(r.get("ku_id") == KU_ID or r.get("card_path") == CARD for r in manifest)
    assert not any(r.get("type") == "place" and (r.get("name_en") or "").casefold() == NAME_EN.casefold() for r in manifest)

    statements = sync.load_statements()
    direct = [
        r for r in statements
        if CANDIDATE in (r.get("subject_candidate_id"), r.get("object_candidate_id"))
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
    planned_row = next(r for r in planned_alignment if r.get("candidate_id") == CANDIDATE and not r.get("external_source"))
    planned_row["ku_id"] = KU_ID
    planned_row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "place",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD,
    }]
    with tempfile.TemporaryDirectory(prefix="pnp-s4-germany-preview-") as temp_dir:
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
        f"### S4 place：Germany 跨章地点组登记（{DATE}）\n\n"
        f"- `{CANDIDATE}`（`{GROUP}`）登记至[德国地点卡](../../../{CARD})，仅作为 Haskell 多章中的地理地点名；未补定现代边界、历史主权、具体路线或未记载地点。\n"
        f"- 对照第4章 p.96、 第7章 pp.194–195、第10章 pp.293、295、第13章 p.334及第15章 p.361的书内语境，保留人物服役、迁移、作品流向、赞助、旅行、君主比较与收藏转运的原文范围。p.295 的比较句不是关系候选。\n"
        f"- 六条直接 S2 关系候选（{', '.join(sorted(RELATION_IDS))}）留待 S6。cand-8832 与 cand-8861 的 Southern Germany 地点组不并入本组；无外部身份来源或正式关系新增。\n"
        f"- S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU={sync.fmt(len(planned_manifest))}，字段={sync.fmt(len(planned_facts))}。"
    )
    planned_accepted = insert_accepted(accepted)

    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP}; candidate={CANDIDATE}; new_KU={KU_ID}; "
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
        f"applied: group={GROUP}; candidate={CANDIDATE}; new_KU={KU_ID}; field_rows={len(facts)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}; "
        f"enrichment={len(old_facts)}->{len(planned_facts)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
