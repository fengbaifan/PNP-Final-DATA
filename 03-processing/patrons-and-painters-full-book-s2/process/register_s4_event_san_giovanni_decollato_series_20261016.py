from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as result_sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

CANDIDATE = "cand-6039"
GROUP = "sg3-event-s-giovanni-decollato-series"
OCCURRENCES = {
    "cand-11766": "1662",
    "cand-11767": "1668",
    "cand-11768": "1675",
    "cand-11769": "1736",
}
KU_ID = "units/events/annual-exhibition-s-giovanni-decollato"
CARD_REL = "04-knowledge/units/events/annual-exhibition-s-giovanni-decollato.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "罗马圣若望斩首堂年度展览系列"
NAME_EN = "Annual Exhibition at S. Giovanni Decollato, Rome"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "location": "第5章第I节；印刷页127；OCR L78–81",
        "summary": "哈斯克尔记载，罗马 S. Giovanni Decollato 回廊在8月29日圣日举行年度展览；修会赞助背景、早期记载及1662与1668年届次均见该段。",
        "quotes": (
            (
                "line 78",
                "The other great annual exhibition held in Rome took place in the cloisters of S. Giovanni Decollate on 29 August, the saint’s day.",
            ),
            (
                "line 79",
                "It was held under the auspices of the leading patrician families and evidently redounded to their credit at least as much as to that of the artists represented.",
            ),
            (
                "line 79",
                "It is recorded as a regular institution as early as 1620, but there are traces of it some twenty years previously.",
            ),
            (
                "line 80",
                "Almost certainly the pictures were designed to decorate the church as part of the celebrations in honour of the saint.",
            ),
            (
                "line 80",
                "Salvator Rosa, however, made full use of the exhibition to show his work to the public, and much of our information about it is derived from him and dates from rather later in the century.",
            ),
            (
                "line 81",
                "In 1662 it fell to the Sacchetti to organise the exhibition. Naturally, writes Rosa, pride of place was given to Pietro da Cortona, the family painter.",
            ),
            (
                "line 81",
                "Six years later the Rospigliosi were responsible and they challenged all previous patrons by the lavishness of the display they organised.",
            ),
        ),
        "span": "lines 78–81; print p. 127",
    },
    {
        "location": "第5章第I节；印刷页128；OCR L88–90",
        "summary": "第5章记载1675年圣年展览及后期商业化趋势；1736年展出212幅新旧作品并发行目录，且有人期待教宗出价。",
        "quotes": (
            (
                "line 88",
                "Another lavish exhibition was arranged for the Holy Year of 1675 when over two hundred pictures were shown by the Medici.",
            ),
            (
                "line 89",
                "In later years when the great patrician families were more interested in selling than in displaying their pictures, the exhibitions seem to have become far more commercial.",
            ),
            (
                "line 90",
                "Thus 212 pictures, old and modern, were exhibited in 1736, a catalogue was issued, and there were hopes that the Pope would make a bid.",
            ),
        ),
        "span": "lines 88–90; print p. 128",
    },
)


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append(
            {
                "citation": BOOK_CITATION,
                "location": item["location"],
                "sentence_summary": item["summary"],
                "original_quotes": [
                    {"source_span": span, "text": quote}
                    for span, quote in item["quotes"]
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": item["span"],
                },
            }
        )
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p127 = "[第5章 p.127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L78–81）"
    p128 = "[第5章 p.128](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L88–90）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔所述罗马 S. Giovanni Decollato 回廊的年度艺术展览系列，举行于每年8月29日、圣日。作者称其早在1620年已被记录为常规活动，并有约早二十年的迹象；这不足以确定首届日期。展览与具体年份的个别场次分开建模。{p127}

**English:** This unit records the annual art-exhibition series that Haskell places in the cloisters of S. Giovanni Decollato in Rome on 29 August, the saint’s day. He says it was recorded as a regular institution by 1620 and that traces existed roughly twenty years earlier; this does not establish an exact first date. Individual year-specific exhibitions are modeled separately from the recurring series. {p127}

### 活动性质与时间

- 活动性质：年度重复展览系列；本卡不指任何单一年份的场次。{p127}
- 举行日期：每年8月29日；哈斯克尔称为该圣人的纪念日。原文没有在此处给出系列终止时间。{p127}
- 早期记载：1620年已记为常规活动；约1600年前后已有迹象。原文没有确定首届年份。{p127}
- 举办地点：罗马 S. Giovanni Decollato 教堂回廊。该活动不与同名地点实体或博洛尼亚的 Confraternità di S. Giovanni Battista Decollato 机构合并。{p127}

### 书内活动记录

- 赞助与目的：展览由罗马主要贵族家族赞助，其声望收益不亚于参展画家。哈斯克尔认为作品几乎可以肯定用于圣日庆典装饰教堂；Salvator Rosa 也利用展览向公众展示作品。作者说明关于展览的许多材料来自 Rosa，且形成于本世纪较晚时期，故不将其叙述外推为全部届次的完整记录。{p127}
- 1662年：由 Sacchetti 家族负责组织；Rosa称 Pietro da Cortona 获显著位置。{p127}
- 1668年：Rospigliosi 负责组织，展陈规模与奢华程度超过此前届次。{p127}
- 1675年圣年：另有一次华丽展览，Medici 展出二百余幅画作。{p128}
- 后期商业化：哈斯克尔认为，贵族家族逐渐更关注出售而非展示作品，展览似乎因而更趋商业化；此为作者的概括性判断。1736年记录有212幅新旧画作、目录出版及期待教宗竞价的情形。{p128}

## 关系与证据

### 关系记录

当前没有已登记的正式关系。12条直接 S2 陈述中8条为关系候选，逐条保留在[原书陈述表](../../tables/book-statements.jsonl)，留待 S6 按端点、类型、方向、语境和证据审查。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register the recurring S. Giovanni Decollato exhibition as an event in S4."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = result_sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = result_sync.read_csv(ALIGNMENT_PATH)
    _, candidates = result_sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidate_by_id
    assert candidate_by_id[CANDIDATE].get("suggested_type") == "event"
    target = decisions[CANDIDATE]
    assert target["decision"] == "new" and not target.get("ku_id")
    assert result_sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and result_sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    for cid in OCCURRENCES:
        assert decisions[cid]["decision"] == "new" and not decisions[cid].get("ku_id")
        assert result_sync.get_group(decisions[cid].get("resolution_note", "")) != GROUP
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "event"
        and "giovanni decollato" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".lower()
        and "annual" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".lower()
        for row in manifest
    ), "same recurring S. Giovanni Decollato event already exists in the manifest"

    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for item in SOURCES:
        for span, quote in item["quotes"]:
            assert " ".join(quote.split()) in source_text, (item["location"], span, quote)

    statements = result_sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 12 and len(direct_relations) == 8
    assert {row.get("segment_id") for row in direct} == {
        "chp-5:05_CHP-5_sec_i:l76-83",
        "chp-5:05_CHP-5_sec_i:l85-97",
    }

    planned_alignment = [dict(row) for row in alignments]
    mapped = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append(
        {
            "ku_id": KU_ID,
            "type": "event",
            "canonical_name": NAME_ZH,
            "name_en": NAME_EN,
            "source_task": TASK,
            "card_path": CARD_REL,
        }
    )
    stats = result_sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = result_sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S4 event：S. Giovanni Decollato 年度展览系列登记（2026-10-16）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）映射至[罗马圣若望斩首堂年度展览系列事件卡](../../../04-knowledge/units/events/annual-exhibition-s-giovanni-decollato.md)。"
        "第5章 pp.127–128 记载年度展览于8月29日在教堂回廊举行；1620年已有常规活动记录，约1600年前后可见较早迹象，但首届年份不明。"
        "卡片保留作者对宗教装饰目的及晚期商业化的判断范围，并区分 Salvator Rosa 的公众展示用途。"
        "1662、1668、1675、1736年四个具体场次候选 `cand-11766`–`cand-11769` 各有独立 new 组，尚未登记，不映射为系列本体；同名博洛尼亚善会机构与本罗马展览事件亦分开。"
        "12条直接 S2 陈述中8条关系候选仍待 S6；本次未生成正式关系或 S5 补足。"
        f"S4 累计登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    result_note = (
        "\n\n### event：S. Giovanni Decollato 年度展览系列 S4 登记（2026-10-16）\n\n"
        f"`{CANDIDATE}` 映射至[罗马圣若望斩首堂年度展览系列事件卡](../units/events/annual-exhibition-s-giovanni-decollato.md)。"
        "系列本体与1662、1668、1675、1736年四个具体场次分别保留；本卡只记录每年8月29日的重复活动，不推定确切首届或终止年份。"
        "8条关系候选留待 S6；没有新增正式关系或 S5 补足。"
        f"全书 S4 当前登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 event dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"group members={len(group_rows)}; direct statements={len(direct)}; relation candidates={len(direct_relations)}")
        print("print pp.127–128 quotations checked; four dated event occurrences remain separate new groups")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    result_sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    result_sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={result_sync.fmt(totals['registered_groups'])}/{result_sync.fmt(totals['registered_members'])}; "
        f"pending={result_sync.fmt(totals['pending_groups'])}/{result_sync.fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
