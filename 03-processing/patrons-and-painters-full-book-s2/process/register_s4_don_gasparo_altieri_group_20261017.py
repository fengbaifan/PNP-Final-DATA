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

CANDIDATES = ("cand-0089",)
GROUP = "new-person:altieri-gasparo-d03e2990cb"
KU_ID = "units/persons/don-gasparo-altieri"
CARD_REL = "04-knowledge/units/persons/don-gasparo-altieri.md"
CHAPTER = "02-sources/02-Markdown/06_CHP-6_sec_v.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/A.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp6-p161-v1-14",
    "st-chp6-p161-v1-15",
    "st-chp6-p161-v1-19",
    "st-chp6-p161-v1-22",
    "st-chp6-p162-v1-01",
    "st-chp6-p162-v1-02",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第6章；印刷页161–162；OCR L9–10、15–16",
            "sentence_summary": (
                "第161页以 Don Gasparo Altieri 指称此人，并称其为教皇 Clement X 的养侄及 Gonfaloniere of the Church；"
                "同页称 Carlo Maratta 与其学生为宫邸筹划的装饰未能完成，原因被说成与 Don Gasparo 的未明分歧。"
                "第162页将 Claude 的《The Landing of Aeneas in Latium》称为其赞助活动最值得记述的例子，并说他把该画加入同一画家的《Sacrifice to Apollo》。"
                "这些是 Haskell 的书内说法，相关关系候选仍待 S6 裁决。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 9",
                    "text": "Altieri, the Pope’s adopted nephew and Gonfaloniere of the Church",
                },
                {
                    "source_span": "line 10",
                    "text": (
                        "- It is also characteristic that the work dragged on for some twenty years and that the decoration "
                        "planned for the palace by Carlo Maratta and his pupils was never completed owing to some unspecified "
                        "differences with Don Gasparo Altieri.4"
                    ),
                },
                {
                    "source_span": "lines 15–16",
                    "text": (
                        "or a Chigi so that the most memorable record of his patronage is Claude’s The landing of "
                        "Aeneas in Latium which he added to the same artist’s Sacrifice to Apollo, painted for his father "
                        "some twelve years earlier? Clement X had good reason to try to economise."
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 9–10, 15–16; print pp. 161–162",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；A.csv#90；印刷页161",
            "sentence_summary": "书后索引以 Altieri, Don Gasparo 为主项，定位第161页。",
            "original_quotes": [
                {
                    "source_span": "index entry A.csv#90",
                    "text": "| Altieri, Don Gasparo |  |  |  | 161 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry A.csv#90",
            },
        },
    ]
    frontmatter = {
        "title": "加斯帕罗·阿尔蒂耶里（Don Gasparo Altieri）",
        "name_en": "Don Gasparo Altieri",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p161_162 = f"[第6章 pp.161–162](../../../{CHAPTER})（L9–10、15–16）"
    index = f"[书后索引](../../../{INDEX_FILE})（A.csv#90）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书后索引主项“Altieri, Don Gasparo”（A.csv#90）及第6章 p.161–162 的 Don Gasparo Altieri。Haskell在第161页称其为 Pope Clement X 的养侄及 Gonfaloniere of the Church，并叙述与其有关的宫邸装饰计划；第162页将 Claude 的《The Landing of Aeneas in Latium》作为其赞助活动的例子。以上仅作为本书对该人物的叙述保存；本次登记只建立人物身份映射，关系和职务陈述仍按各自的 S2 候选待 S6 裁决。{p161_162} {index}

**English:** This card records the person indexed as “Altieri, Don Gasparo” (A.csv#90) and named Don Gasparo Altieri in Chapter 6, pp.161–162. On p.161, Haskell calls him Pope Clement X’s adopted nephew and Gonfaloniere of the Church and discusses a palace decoration project associated with him; on p.162, the author cites Claude’s *The Landing of Aeneas in Latium* as an example of his patronage. These are preserved as statements in the book. This registration establishes the person identity mapping only; the relationship and office claims remain S2 candidates for S6 adjudication. {p161_162} {index}

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。阿尔蒂耶里家族保持为独立 family KU，不因姓氏相同而并入本人物卡。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Don Gasparo Altieri's S3 person identity group in S4.")
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
        and (row.get("name_en") or "").casefold() == "don gasparo altieri"
        for row in manifest
    ), "Don Gasparo Altieri person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "A.csv#90"
    assert candidate["canonical_name"] == "Altieri, Don Gasparo"
    assert candidate["index_page_range"] == "161"
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
    assert "Altieri, the Pope’s adopted nephew and Gonfaloniere of the Church" in chapter
    assert "the decoration planned for the palace by Carlo Maratta and his pupils was never completed" in chapter
    assert "Claude’s The landing of\nAeneas in Latium which he added to the same artist’s Sacrifice to Apollo" in chapter
    assert "| Altieri, Don Gasparo |  |  |  | 161 |" in index_text

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
        "canonical_name": "加斯帕罗·阿尔蒂耶里",
        "name_en": "Don Gasparo Altieri",
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
        "\n\n<a id=\"s4-don-gasparo-altieri-person\"></a>\n\n"
        "### S4 person：Don Gasparo Altieri 身份组登记（2026-10-17）\n\n"
        f"`cand-0089`（A.csv#90，p.161）保持 S3 组 `{GROUP}`，映射至[Don Gasparo Altieri 人物卡]"
        f"(../../../{CARD_REL})。书后索引主项及第6章 p.161 正文姓名相合；既有 Altieri family KU 保持独立。"
        "Haskell关于其与 Clement X 的关系、Gonfaloniere 职务、宫邸装饰争议和 Claude 作品的叙述仍按原书语境保存。"
        "6条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。本轮未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Don Gasparo Altieri 身份组登记（2026-10-17）\n\n"
        f"`cand-0089`（A.csv#90）映射至[Don Gasparo Altieri 人物卡]"
        "(../units/persons/don-gasparo-altieri.md)。书后索引姓名与第6章 p.161 正文相合；"
        "阿尔蒂耶里家族保持独立。6条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Don Gasparo Altieri dry-run passed: {CANDIDATES} -> {KU_ID}")
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
