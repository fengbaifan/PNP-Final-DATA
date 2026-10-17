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

CANDIDATES = ("cand-2804",)
GROUP = "new-person:antoine-watteau-92f90f3ca9"
KU_ID = "units/persons/antoine-watteau"
CARD_REL = "04-knowledge/units/persons/antoine-watteau.md"
CHAPTER_10 = "02-sources/02-Markdown/10_CHP-10_intro.md"
CHAPTER_18 = "02-sources/02-Markdown/18_CHP-18Conclusion.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/UVWXYZ.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp10-p277-crozat-description-of-watteau",
    "st-chp10-p277-crozat-met-watteau",
    "st-chp10-p284-watteau-at-crozat-house",
    "st-chp10-p285-carriera-met-watteau",
    "st-chp10-p292-tessin-early-travel",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页277、284、285、292；OCR L22、172、186、277",
            "sentence_summary": (
                "第277页称 Pierre Crozat 返回法国时遇见 Watteau，并称他有能力创作足以匹配 Rosalba 作品的画作；"
                "第284页以 Antoine Watteau 全名称其为 Crozat 的新发现，并记其住在 Crozat 家中。"
                "第285页记 Rosalba Carriera 与 Watteau 相见；第292页称 Count Tessin 在1714–1719年的早期旅行中结识 Watteau。"
                "以上均为 Haskell 对人物及其交往的书内叙述，关系裁决留待 S6。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 22; print p. 277",
                    "text": (
                        "he wrote to her later and promised her a painting by Watteau in exchange for her work, as this artist "
                        "whom he met on his return to France at the end of the year was the only man ‘able to produce something worthy of you’"
                    ),
                },
                {
                    "source_span": "line 172; print p. 284",
                    "text": "Crozat’s latest discovery, the 32-year-old Antoine Watteau, was living in his house",
                },
                {
                    "source_span": "line 186; print p. 285",
                    "text": "She met Rigaud and Watteau, both of whom expressed their deep admiration",
                },
                {
                    "source_span": "line 277; print p. 292",
                    "text": "he first came into contact with Watteau",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_10,
                "source_span": "lines 22, 172, 186, 277; print pp. 277, 284, 285, 292",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "结论；OCR [Page 2] L8；书后索引定位印刷页384",
            "sentence_summary": (
                "结论将 Watteau 列入与意大利画家不同、表达个人视角的外国画家之中。"
                "来源转录的页眉标作[Page 2]，而书后索引将此处定位为印刷页384；本卡保留两种定位信息。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 8; source marker [Page 2]",
                    "text": "Vermeer, Louis Le Nain, Georges de la Tour, Poussin, Watteau or Chardin",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_18,
                "source_span": "line 8; source marker [Page 2]; index print p. 384",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；UVWXYZ.csv#141；印刷页277、284、285、292、384",
            "sentence_summary": "书后索引以 Watteau, Antoine 为主项，汇总定位第277、284、285、292、384页。",
            "original_quotes": [
                {
                    "source_span": "index entry UVWXYZ.csv#141",
                    "text": "| Watteau, Antoine |  |  |  | 277, 284, 285, 292, 384 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry UVWXYZ.csv#141",
            },
        },
    ]
    frontmatter = {
        "title": "安托万·华托（Antoine Watteau）",
        "name_en": "Antoine Watteau",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    pages = f"[第10章 pp.277、284、285、292](../../../{CHAPTER_10})"
    conclusion = f"[结论](../../../{CHAPTER_18})（OCR [Page 2] L8）"
    index = f"[书后索引](../../../{INDEX_FILE})（UVWXYZ.csv#141）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应书后索引主项“Watteau, Antoine”（UVWXYZ.csv#141），索引将第10章 pp.277、284、285、292及结论印刷页384归于同一人物。第284页明称 Antoine Watteau；其余第10章段落以 Watteau 或指代形式叙述其与 Crozat、Rosalba Carriera、Count Tessin 的交往。结论也以 Watteau 全名列举其画家身份。以上作为 Haskell 的书内说法保存。p.277 所说 Crozat 以 Watteau 画作交换 Rosalba 作品，其中画作保持为独立的作品候选，不并入人物卡。此次 S4 只登记人物身份映射，5条关系候选留待 S6。{pages} {conclusion} {index}

**English:** This card records the person indexed as “Watteau, Antoine” (UVWXYZ.csv#141), whose entry groups Chapter 10 pp.277, 284, 285, and 292 with conclusion print p.384. Chapter 10, p.284 gives the full name Antoine Watteau; the other passages refer to Watteau or use anaphoric references in accounts of his contacts with Crozat, Rosalba Carriera, and Count Tessin. The conclusion also lists Watteau among painters. These remain statements in Haskell’s book. The painting by Watteau mentioned on p.277 in connection with Crozat’s exchange for Rosalba’s work remains a separate work candidate and is not merged into this person card. This S4 action registers the person identity mapping only; five relation candidates remain for S6. {pages} {conclusion} {index}

## 关系与证据

5条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Antoine Watteau's S3 person identity group in S4.")
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
        and (row.get("name_en") or "").casefold() == "antoine watteau"
        for row in manifest
    ), "Antoine Watteau person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "UVWXYZ.csv#141"
    assert candidate["canonical_name"] == "Watteau, Antoine"
    assert candidate["index_page_range"] == "277, 284, 285, 292, 384"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    chapter_10 = (ROOT / CHAPTER_10).read_text(encoding="utf-8-sig")
    chapter_18 = (ROOT / CHAPTER_18).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert "Crozat’s latest discovery, the 32-year-old Antoine Watteau, was living in his house" in chapter_10
    assert "whom he met on his return to France at the end of the year" in chapter_10
    assert "She met Rigaud and Watteau, both of whom expressed their deep admiration" in chapter_10
    assert "he first came into contact with Watteau" in chapter_10
    assert "Poussin, Watteau or Chardin" in chapter_18
    assert "| Watteau, Antoine |  |  |  | 277, 284, 285, 292, 384 |" in index_text

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
        "canonical_name": "安托万·华托",
        "name_en": "Antoine Watteau",
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
        "\n\n<a id=\"s4-antoine-watteau-person\"></a>\n\n"
        "### S4 person：Antoine Watteau 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-2804`（UVWXYZ.csv#141，pp.277、284、285、292、384）保持 S3 组 `{GROUP}`，映射至[Antoine Watteau 人物卡]"
        f"(../../../{CARD_REL})。第10章 p.284 明示全名，索引将第10章四处及结论 p.384 列于同一人物主项。"
        "Crozat 于 p.277 提及的 Watteau 画作保持为独立作品候选。5条直接 relation_candidate 原样保留待 S6："
        + ", ".join(sorted(RELATION_CANDIDATES)) + "。本轮未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Antoine Watteau 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-2804`（UVWXYZ.csv#141）映射至[Antoine Watteau 人物卡]"
        "(../units/persons/antoine-watteau.md)。第10章 p.284 正文全名及索引跨页定位支持同一人物身份；"
        "p.277 提及的画作单独保留。5条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Antoine Watteau dry-run passed: {CANDIDATES} -> {KU_ID}")
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
