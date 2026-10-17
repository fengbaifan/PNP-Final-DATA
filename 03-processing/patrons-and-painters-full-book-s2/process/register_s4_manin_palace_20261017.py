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

CANDIDATE = "cand-1520"
GROUP = "sg3-place-cand-1520"
KU_ID = "units/places/manin-palace-venice"
CARD_REL = "04-knowledge/units/places/manin-palace-venice.md"
NAME_ZH = "马宁宫殿"
NAME_EN = "Manin Palace, Venice"
BOOK_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged edition "
    "(Yale University Press, 1980; this printing 2006)."
)
RELATION_CANDIDATES = {
    "st-chp9-p251-cignani-and-mazza",
    "st-chp9-p251-gallery-works",
    "st-chp9-p251-palace-hangings-tapestries",
    "st-chp9-p251-gallery-sansovino-bronzes",
    "st-chp9-p251-gallery-giovanni-da-udine-pictures",
    "st-chp9-p251-gallery-andrea-del-sarto-pictures",
    "st-chp9-p251-mazza-marble-venus",
    "st-chp9-p251-palace-mirrors",
    "st-chp9-p251-manin-style-at-palace",
}
NON_RELATION_STATEMENTS = {
    "st-chp9-p251-1708-palace-description",
    "st-chp9-p251-palace-decoration-exceeded-expectations",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页251；OCR L107–112",
            "sentence_summary": (
                "第9章称 Manin 家族的宫殿位于威尼斯大运河，并将其与 Passeriano 的乡间宅邸分开叙述；"
                "其中1708年通信者所述装饰与藏品仅按原书转述记录。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 108",
                    "text": "Their palace on the Grand Canal, wrote a correspondent in 1708",
                },
                {
                    "source_span": "line 112",
                    "text": "as well as in their palace and country house",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "lines 107–112; print p. 251",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页251；注3；OCR L351",
            "sentence_summary": (
                "脚注3列出一封1708年通信的刊载题名，其中以 Palazzo di S.E. il Signor Co: Manin in Venezia "
                "指明通信所述婚礼庆典发生于 Manin 宫殿。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 351",
                    "text": "Palazzo di S.E. il Signor Co: Manin in Venezia",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/09_CHP-9_intro.md",
                "source_span": "line 351; print p. 251; footnote 3",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；M.csv#57",
            "sentence_summary": "索引以 Manin palace 为主项，标注城市 Venice 与第251页定位。",
            "original_quotes": [
                {
                    "source_span": "index row M.csv#57",
                    "text": "| Manin palace | Venice |  |  | 251 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-1-Index-MD/M.md",
                "source_span": "index row M.csv#57",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#s4-manin-palace-venice",
    }
    front = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p251 = "[第9章 p.251](../../../02-sources/02-Markdown/09_CHP-9_intro.md)"
    index = "[书后索引 M.csv#57](../../../02-sources/03-Index/03-1-Index-MD/M.md)"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书后索引 M.csv#57 所列 Venice 的 Manin palace。第9章将它称为 Manin 家族位于大运河上的宫殿；页下注释所引1708年通信题名写作 Palazzo di S.E. il Signor Co: Manin in Venezia。原书另述 Passeriano 的 Manin country house，本卡与该乡间宅邸及 Manin 家族实体分开。此处不据原书描述推定宫殿的现代正式名称、现存状态或具体地址。{p251}；{index}

**English:** This card identifies the Manin palace in Venice listed under index entry M.csv#57. Chapter 9 calls it the Manin family’s palace on the Grand Canal; the title cited in footnote 3 for a 1708 letter reads Palazzo di S.E. il Signor Co: Manin in Venezia. Haskell separately describes the Manin country house at Passeriano, which is kept distinct from this palace and from the Manin family as an entity. The account does not establish a current formal building name, survival status, or precise address. {p251}; {index}

### 名称与身份边界

| 字段 | 值 | 依据 |
|---|---|---|
| 中文显示名 | {NAME_ZH}（项目工作译名） | 本项目命名；不宣称为官方中文名 |
| 英文显示名 | {NAME_EN} | 描述性英文名 |
| 书中名称 | Manin palace；Their palace on the Grand Canal | {p251}；{index} |
| 注释所引名称 | Palazzo di S.E. il Signor Co: Manin in Venezia | 第9章 p.251 注3 |
| 身份区分 | Manin 家族宫殿；与 Passeriano 的 country house、Manin family 分开 | {p251}；{index} |

### 基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 地点性质 | 宫殿／建筑地点 | 第9章 p.251；索引 M.csv#57 |
| 城市 | Venice | {index} |
| 位置描述 | 大运河沿岸；这是 Haskell 对宫殿的书内定位 | {p251} |
| 书内记载语境 | Haskell 转述一名1708年通信者对宫殿及其室内装饰的描述；不据此确认现存馆藏或建筑现状 | {p251} |

## 关系与证据

以下9条直接 S2 关系候选留待 S6 逐项审查，本卡未将其登记为正式关系：{", ".join(sorted(RELATION_CANDIDATES))}。
S2 中 palace description 与 decoration exceeded expectations 两条陈述仍保持原有非关系分类。
"""
    return f"---\n{front}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register the Manin palace place identity group as one S4 place KU."
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
    assert candidate["index_entry_id"] == "M.csv#57"
    assert candidate["canonical_name"] == "Manin palace"
    assert candidate["index_page_range"] == "251"
    assert candidate["suggested_type"] == "place"
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
        or (row.get("type") == "place" and "manin" in (row.get("name_en") or "").casefold())
        for row in manifest
    )
    card_path = ROOT / CARD_REL
    assert not card_path.exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted

    index = (ROOT / "02-sources/03-Index/03-1-Index-MD/M.md").read_text(encoding="utf-8-sig")
    chapter = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    assert "| Manin palace | Venice |  |  | 251 |" in index
    assert "Their palace on the Grand Canal, wrote a correspondent in 1708" in chapter
    assert "Palazzo di S.E. il Signor Co: Manin in Venezia" in chapter
    assert "as well as in their palace and country house" in chapter

    statements = sync.load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relation_ids = {
        row["statement_id"] for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    direct_non_relation_ids = {
        row["statement_id"] for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is not True
    }
    assert direct_relation_ids == RELATION_CANDIDATES, direct_relation_ids
    assert direct_non_relation_ids == NON_RELATION_STATEMENTS, direct_non_relation_ids
    assert len([
        row for row in sync.read_csv(TABLES / "mentions.csv")[1]
        if row.get("candidate_id") == CANDIDATE
    ]) == 3

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE)
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "place",
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
        "\n\n<a id=\"s4-manin-palace-venice\"></a>\n\n"
        "### S4 place：Manin Palace, Venice（马宁宫殿）身份组登记（2026-10-17）\n\n"
        f"{CANDIDATE}（M.csv#57；S3 组 {GROUP}）映射至[地点卡](../../../{CARD_REL})。"
        "索引列名 Manin palace、城市 Venice 与第251页定位；正文称其为 Manin 家族大运河宫殿，注3所引1708年通信题名写 Palazzo di S.E. il Signor Co: Manin in Venezia。"
        "书中另有 Passeriano 乡间宅邸，本卡明确与之及 Manin family 区分；不推定现存状态或精确地址。"
        f"9条直接 relation_candidate 留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。"
        "palace description 与 decoration exceeded expectations 两条 statement 维持非关系分类。"
        f"本轮未写 relations.csv、未登记正式关系，未新增 sources.csv 记录。S4 累计登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 place：Manin Palace, Venice 跨章/索引身份组（2026-10-17）\n\n"
        f"{CANDIDATE}（M.csv#57）登记至[马宁宫殿地点卡](../units/places/manin-palace-venice.md)。"
        "第9章 p.251 正文、注3与索引主项相互定位；与 Manin family 和 Passeriano country house 分开。"
        "9条关系候选留待 S6，2条非关系陈述保持原分类。"
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
        print(f"S4 Manin Palace dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(
            f"index=M.csv#57; mentions=3; relation_candidates={len(direct_relation_ids)}; "
            f"non_relations={len(direct_non_relation_ids)}"
        )
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
