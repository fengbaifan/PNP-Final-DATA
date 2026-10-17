from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

CANDIDATE = "cand-0003"
GROUP = "sg3-institution-cand-0003"
KU_ID = "units/institutions/accademia-dei-lincei"
CARD_REL = "04-knowledge/units/institutions/accademia-dei-lincei.md"
NAME_ZH = "林琴科学院"
NAME_EN = "Lincean Academy"
BOOK_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged edition "
    "(Yale University Press, 1980; this printing 2006)."
)
RELATION_CANDIDATES = {
    "st-chp4-sec-ii-l232-308-cassiano-admitted-to-lincei",
    "st-chp4-sec-ii-l232-308-cesi-identified-as-founder",
    "st-chp4-sec-ii-l232-308-clerical-patronage-and-church-conflict",
    "st-chp4-sec-ii-l232-308-heresy-charges-and-attacks-left-lincei-firm",
    "st-chp4-sec-ii-l232-308-lincei-described-as-scientific-ancestor",
    "st-chp4-sec-ii-l232-308-lincei-disintegrated-after-cesi-death",
    "st-chp4-sec-ii-l232-308-lincei-membership-rule",
    "st-chp4-sec-ii-l232-308-lynx-metaphor-and-suppression",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第2章；印刷页33；OCR L27",
            "sentence_summary": (
                "第2章将 Accademia dei Lincei 与 Galileo 并列为罗马社会中开展严肃科学实验的实例；"
                "该处支持书中名称与机构语境，不单独说明创立时间或后续沿革。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 27",
                    "text": "serious scientific experiments as conducted by the Accademia dei Lincei and Galileo",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "source_span": "line 27; print p. 33",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第4章；印刷页99；脚注99；OCR L233",
            "sentence_summary": (
                "第4章脚注99再次使用 Accademia dei Lincei 名称，并以 the Accademia 与 the Lincei 简称；"
                "作者称其为近期创建的欧洲科学社团先驱，此处作为 Haskell 的比较性表述记录。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 233",
                    "text": "organisers of the Accademia dei Lincei, the recently created ancestor of all European scientific societies",
                },
                {
                    "source_span": "line 233",
                    "text": "Only bachelors were admitted to the Accademia dei Lincei and the clergy were expressly excluded.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/04_CHP-4_sec_ii.md",
                "source_span": "line 233; print p. 99; footnote 99",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#s4-accademia-dei-lincei",
    }
    front = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p33 = "[第2章 p.33](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L27）"
    p99 = "[第4章 p.99 注99](../../../02-sources/02-Markdown/04_CHP-4_sec_ii.md)（L233）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录 Haskell 在第2章与第4章所称的 Accademia dei Lincei。第2章将其与 Galileo 并列为罗马语境中的科学实验活动；第4章脚注99以 the Accademia 和 the Lincei 简称该机构，并讨论其成员组织。中文显示名“{NAME_ZH}”为项目工作译名，原文名称保留为 Accademia dei Lincei。第4章将其比作欧洲科学社团的“先驱”是作者的比较性表述；本卡不据此声称存在已核实的正式制度传承，也不把本书中的历史对象与任何后来的同名机构合并。{p33}；{p99}

**English:** This card records the Accademia dei Lincei named by Haskell in Chapters 2 and 4. Chapter 2 places it alongside Galileo in the context of scientific experiments in Rome; Chapter 4, footnote 99, refers to it as “the Accademia” and “the Lincei” and discusses its membership. The Chinese display name is a project working translation; the Italian name is retained. Chapter 4’s comparison of the institution to an “ancestor” of European scientific societies is recorded as the author’s characterization, not as a verified institutional succession. This card does not merge the historical subject in the book with any later institution of the same name. {p33}; {p99}

### 名称

| 字段 | 值 | 依据 |
|---|---|---|
| 中文显示名 | {NAME_ZH}（项目工作译名） | 本项目命名；不宣称为官方译名 |
| 英文显示名 | {NAME_EN} | 描述性英文译名；原语名称见下 |
| 原文名称 | Accademia dei Lincei | {p33}、{p99}；索引 A.csv#2 |
| 书中简称 | the Accademia；the Lincei | {p99} |

### 基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 书中机构性质 | 学院／学术团体；第2章以其科学实验活动为例，第4章称其为 Accademia 并提及成员 | {p33}；{p99} |
| 书中语境 | 哈斯克尔讨论的罗马科学与学术活动 | {p33}；第4章 p.99 注99 |

## 关系与证据

以下8条直接 S2 关系候选留待 S6 逐项审查；本卡不将其登记为正式关系：{", ".join(sorted(RELATION_CANDIDATES))}。
"""
    return f"---\n{front}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register the Accademia dei Lincei S3 identity group as one S4 institution KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate = candidate_by_id[CANDIDATE]
    alignment = alignment_by_id[CANDIDATE]
    assert candidate["index_entry_id"] == "A.csv#2"
    assert candidate["canonical_name"] == "Accademia dei Lincei"
    assert candidate["index_page_range"] == "33, 99"
    assert candidate["suggested_type"] == "institution"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not any(
        row.get("ku_id") == KU_ID
        or (row.get("type") == "institution" and row.get("name_en") == NAME_EN)
        for row in manifest
    )
    card_path = ROOT / CARD_REL
    assert not card_path.exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted

    index = (ROOT / "02-sources/03-Index/03-1-Index-MD/A.md").read_text(encoding="utf-8-sig")
    chapter2 = (ROOT / "02-sources/02-Markdown/02_CHP-2_sec_ii.md").read_text(encoding="utf-8-sig")
    chapter4 = (ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md").read_text(encoding="utf-8-sig")
    assert "| Accademia dei Lincei | Rome |  |  | 33, 99 |" in index
    assert "serious scientific experiments as conducted by the Accademia dei Lincei and Galileo" in chapter2
    assert "organisers of the Accademia dei Lincei" in chapter4
    assert "Only bachelors were admitted to the Accademia dei Lincei" in chapter4

    statements = sync.load_statements()
    direct_relation_ids = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relation_ids == RELATION_CANDIDATES, direct_relation_ids
    assert len([
        row for row in sync.read_csv(TABLES / "mentions.csv")[1]
        if row.get("candidate_id") == CANDIDATE
    ]) == 9

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE)
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "institution",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(planned_manifest),
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-accademia-dei-lincei\"></a>\n\n"
        "### S4 institution：Accademia dei Lincei（林琴科学院）身份组登记（2026-10-17）\n\n"
        f"{CANDIDATE}（A.csv#2；S3 组 {GROUP}）映射至[机构卡](../../../{CARD_REL})。"
        "索引主项同一行定位第2章 p.33 与第4章 p.99；前者将该学院置于罗马科学实验语境，后者脚注99再次使用完整名称并以 the Accademia、the Lincei 指称。"
        "没有同类型既有 KU，按 S3 的 new 决定登记一个机构 KU。中文显示名为项目工作译名；书内“欧洲科学社团先驱”保留为 Haskell 的比较性表述，不扩写为已核实的制度传承，也不延伸到后来的同名机构。"
        f"8条直接 relation_candidate 保持待 S6 审查：{', '.join(sorted(RELATION_CANDIDATES))}。"
        f"本轮未写 relations.csv、未登记正式关系，未改 sources.csv。S4 累计登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 institution：Accademia dei Lincei 跨章身份组（2026-10-17）\n\n"
        f"{CANDIDATE}（A.csv#2）由第2章 p.33 与第4章 p.99 的索引定位合并至[林琴科学院卡](../units/institutions/accademia-dei-lincei.md)。"
        "本卡保留意大利语名称，将中文名标为项目工作译名；Haskell 的“先驱”比较不作为已核实的正式沿革。"
        "8条直接关系候选待 S6，未新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print(f"S4 Accademia dei Lincei dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"cross-chapter index anchors=33, 99; mentions=9; direct relation candidates={len(direct_relation_ids)}")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; registered={sync.fmt(totals['registered_groups'])}/"
        f"{sync.fmt(totals['registered_members'])}; pending={sync.fmt(totals['pending_groups'])}/"
        f"{sync.fmt(totals['pending_members'])}; manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
