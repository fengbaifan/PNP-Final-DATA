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

CANDIDATE = "cand-4236"
GROUP = "sg3-place-cand-4236"
KU_ID = "units/places/pantheon-rome"
CARD_REL = "04-knowledge/units/places/pantheon-rome.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "罗马万神殿"
NAME_EN = "Pantheon, Rome"
BOOK_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "location": "第2章；印刷页34；OCR L39",
        "summary": "第2章称，Bernini 华盖柱的青铜短缺通过拆取 Pantheon 的青铜解决；未说明拆取数量或具体构件。",
        "quote": "the second by the despoiling of the Pantheon.",
        "source_span": "line 39; print p. 34",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    },
    {
        "location": "第2章；印刷页35；OCR L47",
        "summary": "第2章称，从 Pantheon 拆取青铜是 Bernini 建议的；未指明执行者或精确数量。",
        "quote": "the removal, at Bernini’s suggestion, of bronze from the Pantheon",
        "source_span": "line 47; print p. 35",
        "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
    },
    {
        "location": "第5章；印刷页126；OCR L62",
        "summary": "第5章记载罗马 Pantheon 每年3月19日举行圣约瑟节年度展览。",
        "quote": "the one held in the Pantheon each year on 19 March to celebrate the feast day of St Joseph.",
        "source_span": "line 62; print p. 126",
        "source_file": "02-sources/02-Markdown/05_CHP-5_sec_i.md",
    },
    {
        "location": "第10章；印刷页321；OCR L168",
        "summary": "哈斯克尔转述 Lodoli 认为 Pantheon 也并非完美；具体批评对象未说明。",
        "quote": "Even the Pantheon, he said, was not perfect;",
        "source_span": "line 168; print p. 321",
        "source_file": "02-sources/02-Markdown/10_CHP-10_sec_ii.md",
    },
    {
        "location": "第14章；印刷页348；OCR L20",
        "summary": "哈斯克尔转述 Algarotti 以 Pantheon 与圣彼得大殿比较；此处保留评价者归属。",
        "quote": "he compares St Peter’s unfavourably with the Pantheon.",
        "source_span": "line 20; print p. 348",
        "source_file": "02-sources/02-Markdown/14_CHP-14_intro.md",
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
                    {"source_span": item["source_span"].split(";", 1)[0], "text": item["quote"]}
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": item["source_file"],
                    "source_span": item["source_span"],
                },
            }
        )
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p34 = "[第2章 p.34](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L39）"
    p35 = "[第2章 p.35](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L47）"
    p126 = "[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L62）"
    p321 = "[第10章 p.321](../../../02-sources/02-Markdown/10_CHP-10_sec_ii.md)（L168）"
    p348 = "[第14章 p.348](../../../02-sources/02-Markdown/14_CHP-14_intro.md)（L20）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔在第2、5、10及14章中称为 Pantheon 的罗马建筑。第2章将其记作 Bernini 华盖青铜材料的来源；第5章称其为年度圣约瑟节展览的举办地；第10章转述 Lodoli 对该建筑的评价；第14章转述 Algarotti 以其与圣彼得大殿比较。各章论述的发言者和证据范围分开保留；本卡不据这些提及扩写未见于所引段落的建筑沿革。{p34} {p35} {p126} {p321} {p348}

**English:** This unit records the Roman building referred to as the Pantheon by Haskell in Chapters 2, 5, 10 and 14. Chapter 2 names it as the source of bronze for Bernini’s baldacchino; Chapter 5 identifies it as the venue for the annual St Joseph’s Day exhibition; Chapter 10 reports Lodoli’s assessment of the building; and Chapter 14 reports Algarotti’s comparison of it with St Peter’s Basilica. The speaker and evidentiary scope of each passage are kept distinct; the card does not add a building history beyond the cited passages. {p34} {p35} {p126} {p321} {p348}

### 本书相关内容

- **青铜材料来源：** 第2章称华盖柱所需青铜的短缺通过拆取 Pantheon 的青铜解决；第35页进一步称拆取由 Bernini 建议。原文未指明拆取数量、具体构件或执行者。{p34} {p35}
- **展览场所：** 第5章称年度圣约瑟节展览每年3月19日在 Pantheon 举行；该重复活动另见[万神殿圣约瑟节年度展览事件卡](../events/annual-st-josephs-day-exhibition-pantheon.md)。此内容关联有原文依据，正式场地关系仍待 S6。{p126}
- **建筑评价：** 第10章转述 Lodoli 说 Pantheon 也不完美，但没有指出所批评的具体特征。{p321}
- **比较性评价：** 第14章的比较属于 Haskell 转述的 Algarotti 书信判断，不作为 Haskell 本人或本卡对建筑的评价。{p348}

本卡对象是建筑地点；展览系列及其在门廊的陈列空间分别处理，不合并为建筑本体。

## 关系与证据

### 关系记录

当前没有已登记的正式关系。四条直接 S2 端点陈述均为关系候选，保留在[原书陈述表](../../tables/book-statements.jsonl)，留待 S6 按关系类型、方向、语境和证据审查。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Roman Pantheon building as a place in S4.")
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

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE].get("suggested_type") == "place"
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
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "place"
        and "pantheon" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".lower()
        for row in manifest
    ), "same-type Pantheon building already exists in manifest"

    for item in SOURCES:
        source_text = " ".join((ROOT / item["source_file"]).read_text(encoding="utf-8-sig").split())
        assert " ".join(item["quote"].split()) in source_text, (item["location"], item["quote"])

    statements = result_sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 4 and len(direct_relations) == 4
    assert {
        row.get("segment_id") for row in direct
    } == {
        "chp-2:02_CHP-2_sec_ii:l30-40",
        "chp-2:02_CHP-2_sec_ii:l42-50",
        "chp-5:05_CHP-5_sec_i:l60-74",
        "chp-10:10_CHP-10_sec_ii:l165-173",
    }
    mentions = [
        row for row in result_sync.read_csv(TABLES / "mentions.csv")[1]
        if row.get("candidate_id") == CANDIDATE
    ]
    assert {m.get("segment_id", "").split(":", 1)[0] for m in mentions} >= {"chp-2", "chp-5", "chp-10", "chp-14"}

    planned_alignment = [dict(row) for row in alignments]
    mapped = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    mapped["ku_id"] = KU_ID
    mapped["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append(
        {
            "ku_id": KU_ID,
            "type": "place",
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
        "\n\n### S4 place：罗马 Pantheon 建筑跨章身份组登记（2026-10-16）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）映射至[罗马万神殿地点卡](../../../04-knowledge/units/places/pantheon-rome.md)。同一建筑在第2章 pp.34–35、第5章 p.126、第10章 p.321及第14章 p.348 均有提及；第14章另有一条比较性陈述，仅作提及证据，不改写其评价主体。"
        "建筑本体与圣约瑟节年度展览事件、华盖作品及展览门廊陈列空间分开；门廊空间候选 `cand-11743` 仍为 undecided，本次不据其待决状态扩大建筑卡范围。"
        "四条直接 S2 端点陈述均为关系候选，保留至 S6；未将材料拆取、场地和评价陈述转成正式边，也未开展 S5。"
        f"S4 累计登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    result_note = (
        "\n\n### place：罗马 Pantheon 建筑 S4 登记（2026-10-16）\n\n"
        f"`{CANDIDATE}` 映射至[罗马万神殿地点卡](../units/places/pantheon-rome.md)。卡片汇集第2、5、10、14章对同一罗马建筑的提及，并区分华盖青铜来源、年度展览场地、Lodoli 评论与 Algarotti 比较的证据范围。建筑、展览事件及门廊陈列空间不合并；4条关系候选留待 S6。"
        f"全书 S4 当前登记{result_sync.fmt(totals['registered_groups'])}组/{result_sync.fmt(totals['registered_members'])}条映射，待登记{result_sync.fmt(totals['pending_groups'])}组/{result_sync.fmt(totals['pending_members'])}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 place dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"identity group members={len(group_rows)}; cross-chapter mentions={len(mentions)}")
        print(f"direct endpoint statements={len(direct)}; relation candidates={len(direct_relations)}")
        print("print pp.34–35, 126, 321, 348 quotations checked; building and portico display space remain distinct")
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
