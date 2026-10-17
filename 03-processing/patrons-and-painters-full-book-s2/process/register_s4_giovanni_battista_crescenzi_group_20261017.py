from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATES = ("cand-0869",)
GROUP = "new-person:battista-crescenzi-giovanni-0fabe7dc0e"
KU_ID = "units/persons/giovanni-battista-crescenzi"
CARD_REL = "04-knowledge/units/persons/giovanni-battista-crescenzi.md"
CHAPTER = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/C.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp7-p173-i01",
    "st-chp7-p173-i02",
    "st-chp7-p173-i04",
    "st-chp7-p173-i07",
    "st-chp7-p173-i09",
    "st-chp7-p173-i10",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第7章；印刷页173；OCR L37–43",
            "sentence_summary": (
                "第7章 p.173 以 Giovanni Battista Crescenzi 全名指称此人。Haskell称其生于1577年、出身罗马贵族家族，"
                "称其确实从事建筑并在 Buen Retiro 营建中发挥重要作用；同段提及其未具名的枢机兄弟及两人对 Claude 的雇用。"
                "这些内容均保留为作者叙述；姓名之外的身份和关系陈述依原候选状态待后续裁决。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 38",
                    "text": "Giovanni Battista Crescenzi, who was born in 1577, came of a noble Roman family.",
                },
                {
                    "source_span": "line 38",
                    "text": (
                        "The Venetian ambassador was being too suspicious, for Crescenzi really did practise architecture "
                        "and he played an essential rôle in the building of the Buen Retiro."
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 37–43; print p. 173",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；C.csv#403；印刷页173",
            "sentence_summary": "书后索引以 Crescenzi, Giovanni Battista 为主项，定位第173页。",
            "original_quotes": [
                {
                    "source_span": "index entry C.csv#403",
                    "text": "| Crescenzi, Giovanni Battista |  |  |  | 173 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry C.csv#403",
            },
        },
    ]
    frontmatter = {
        "title": "乔瓦尼·巴蒂斯塔·克雷申齐（Giovanni Battista Crescenzi）",
        "name_en": "Giovanni Battista Crescenzi",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p173 = f"[第7章 p.173](../../../{CHAPTER})（L37–43）"
    index = f"[书后索引](../../../{INDEX_FILE})（C.csv#403）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书后索引主项“Crescenzi, Giovanni Battista”（C.csv#403）及第7章 p.173 的 Giovanni Battista Crescenzi。Haskell称其生于1577年、出身罗马贵族家族，并说他确实从事建筑、在 Buen Retiro 的建造中发挥重要作用。该段还提及其兄弟为枢机，并叙述两人雇用 Claude 的活动；本卡保留这些作者说法，未具名的兄弟不另行指认为具体人物。此次 S4 只登记人物身份映射，相关关系候选留待 S6。{p173} {index}

**English:** This card records the person indexed as “Crescenzi, Giovanni Battista” (C.csv#403) and named Giovanni Battista Crescenzi in Chapter 7, p.173. Haskell says that he was born in 1577, came from a noble Roman family, practised architecture, and played an important role in the building of Buen Retiro. The passage also mentions a cardinal brother and says that the two men employed Claude; these remain the author’s statements, and the unnamed brother is not identified as a specific person. This S4 action registers the person identity mapping only; the related candidates remain for S6 adjudication. {p173} {index}

### 身份边界

本卡与既有 Crescenzi family KU 分开。原书提及的枢机兄弟未具名，本卡不为其创建或指定人物身份。

This person card remains distinct from the existing Crescenzi family KU. The cardinal brother is unnamed in the passage and is not assigned a specific identity here.

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Giovanni Battista Crescenzi's S3 person identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en") or "").casefold() == "giovanni battista crescenzi"
        for row in manifest
    ), "Giovanni Battista Crescenzi person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "C.csv#403"
    assert candidate["canonical_name"] == "Crescenzi, Giovanni Battista"
    assert candidate["index_page_range"] == "173"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    chapter = (ROOT / CHAPTER).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "Giovanni Battista Crescenzi, who was born in 1577, came of a noble Roman family." in chapter
    assert "Crescenzi really did practise architecture and he played an essential rôle in the building of the Buen Retiro." in chapter
    assert "| Crescenzi, Giovanni Battista |  |  |  | 173 |" in index_text

    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == RELATION_CANDIDATES, direct_relations

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATES[0] and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "乔瓦尼·巴蒂斯塔·克雷申齐",
        "name_en": "Giovanni Battista Crescenzi",
        "source_task": TASK,
        "card_path": CARD_REL,
    })

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s4-giovanni-battista-crescenzi-person\"></a>\n\n"
        "### S4 person：Giovanni Battista Crescenzi 身份组登记（2026-10-17）\n\n"
        f"`cand-0869`（C.csv#403，p.173）保持 S3 组 `{GROUP}`，映射至[Giovanni Battista Crescenzi 人物卡]"
        f"(../../../{CARD_REL})。索引主项及第7章 p.173 正文全名相符；既有 Crescenzi family KU 保持独立。"
        "书中未具名的枢机兄弟不另行指认为特定人物。6条直接 relation_candidate 原样保留待 S6："
        + ", ".join(sorted(RELATION_CANDIDATES)) + "。本轮未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Giovanni Battista Crescenzi 身份组登记（2026-10-17）\n\n"
        f"`cand-0869`（C.csv#403）映射至[Giovanni Battista Crescenzi 人物卡]"
        "(../units/persons/giovanni-battista-crescenzi.md)。索引姓名与第7章 p.173 正文全名相合；"
        "既有 Crescenzi family KU 保持独立，未具名的兄弟不作身份指认。6条直接关系候选仍待 S6，未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
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
        print(f"S4 Giovanni Battista Crescenzi dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"identity_group={GROUP}; candidates={len(group_rows)}; direct_relation_candidates={len(direct_relations)}")
        print(
            f"manifest={len(manifest):,}->{len(planned_manifest):,}; "
            f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
            f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    (ROOT / CARD_REL).write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES[0]} -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
