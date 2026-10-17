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

CANDIDATES = ("cand-3427",)
GROUP = "new-person:mary-virgin-0b7fd09ac8"
KU_ID = "units/persons/virgin-mary"
CARD_REL = "04-knowledge/units/persons/virgin-mary.md"
CHAPTER_1 = "02-sources/02-Markdown/01_CHP-1_sec_ii.md"
CHAPTER_6 = "02-sources/02-Markdown/06_CHP-6_sec_v.md"
CHAPTER_9_INTRO = "02-sources/02-Markdown/09_CHP-9_intro.md"
CHAPTER_9_SEC_II = "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
CHAPTER_10 = "02-sources/02-Markdown/10_CHP-10_intro.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp3-secii-l40-52-chapels-marian-mysteries",
    "st-chp3-seciv-l118-128-madonna-chapel-last-to-be-adorned",
    "st-chp3-secii-l74-81-lanfranco-dome-depicts-virgin",
    "st-chp3-seciv-l179-187-unnamed-order-worshipped-virgin",
    "st-chp4-sec-ii-p110-flight-figures-foreground",
    "st-chp9-p255-fatherland-invokes-virgin",
    "st-chp9-p274-zompini-virgin-typology",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第1章；印刷页9；OCR L29–30",
            "sentence_summary": (
                "第1章在一幅祭坛画的主题说明中并列提及 Madonna de Carmine 与 St Teresa 从 Virgin 领受会衣。"
                "这里的 Virgin 指圣母人物；该画作与所描绘人物不合并。"
            ),
            "original_quotes": [
                {
                    "source_span": "lines 29–30; print p. 9",
                    "text": (
                        "the figures were to include the ‘Madonna de Carmine with the Child in Her arms, St Teresa receiving "
                        "the habit from the Virgin and the rules of the Order from the Child, St Joseph and St John the\nBaptist’"
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_1,
                "source_span": "lines 29–30; print p. 9",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第6章；印刷页162；OCR L18",
            "sentence_summary": "第6章以 Virgin Mary 全名提及 Quirinal 中 Guido Reni 所绘的圣母像。",
            "original_quotes": [
                {
                    "source_span": "line 18; print p. 162",
                    "text": (
                        "the covering of an overexposed breast of the Virgin Mary painted in the Quirinal by Guido Reni "
                        "at the beginning of the century"
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_6,
                "source_span": "line 18; print p. 162",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页255；OCR L149",
            "sentence_summary": "第9章记 Tiepolo 的 Pisani 家族寓意画中，Fatherland 向 Virgin 指出家族成员的功绩并为其祈求祝福。",
            "original_quotes": [
                {
                    "source_span": "line 149; print p. 255",
                    "text": "the Fatherland points out their merits to the Virgin and invokes her blessing on them",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_9_INTRO,
                "source_span": "line 149; print p. 255",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页273–274；OCR L64–72",
            "sentence_summary": (
                "第273页称 Scuola del Carmine 的方案以 Virgin 为中心，并转述通过其代祷获救的教义；"
                "第274页引用 Blessed Virgin 并将其与 Esther 比较。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 67; print p. 273",
                    "text": "the hope that the Brethren have of being saved from damnation through the intercession of the Virgin",
                },
                {
                    "source_span": "line 72; print p. 274",
                    "text": "a fine panegyric of the Blessed Virgin, ingeniously comparing her to Esther",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_9_SEC_II,
                "source_span": "lines 64–72; print pp. 273–274",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页295；OCR L310–311",
            "sentence_summary": "第10章将 Virgin Mary 与 Magdalene 并列为宗教题材。",
            "original_quotes": [
                {
                    "source_span": "lines 310–311; print p. 295",
                    "text": "religious subjects such as the Magdalene or the Virgin\nMary. It hardly mattered as they were all equally attractive.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_10,
                "source_span": "lines 310–311; print p. 295",
            },
        },
    ]
    frontmatter = {
        "title": "圣母玛利亚（Virgin Mary）",
        "name_en": "Virgin Mary",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p9 = f"[第1章 p.9](../../../{CHAPTER_1})（L29–30）"
    p162 = f"[第6章 p.162](../../../{CHAPTER_6})（L18）"
    p255 = f"[第9章 p.255](../../../{CHAPTER_9_INTRO})（L149）"
    p273_274 = f"[第9章 pp.273–274](../../../{CHAPTER_9_SEC_II})（L64–72）"
    p295 = f"[第10章 p.295](../../../{CHAPTER_10})（L310–311）"
    body = f"""## 内容

### 描述

**中文：** 本卡对应 S3 新人物组 `new-person:mary-virgin-0b7fd09ac8`。S2 在第1、2、3、4、5、6、8、9、10章记录30条相关提及，使用 Virgin Mary、the Virgin、Blessed Virgin 与 Madonna 等称谓；第6章 p.162 和第10章 p.295 明确写出 Virgin Mary 全名。此卡登记被这些宗教与图像语境指称的圣母人物，不对应任何一幅具体绘画或雕像。涉及圣母像、Madonna 题材或作品题名时，作品对象保持独立。本轮 S4 只完成身份映射，关系候选仍留待 S6。{p9} {p162} {p255} {p273_274} {p295}

**English:** This card records the S3 new-person group `new-person:mary-virgin-0b7fd09ac8`. S2 records 30 mentions across Chapters 1, 2, 3, 4, 5, 6, 8, 9, and 10, using forms such as Virgin Mary, the Virgin, Blessed Virgin, and Madonna; Chapter 6, p.162 and Chapter 10, p.295 give the explicit name Virgin Mary. The card denotes the Marian person referred to in these religious and iconographic contexts, not any particular painting or sculpture. Images of the Virgin, Madonna subjects, and work titles remain distinct objects. This S4 step records identity mapping only; it does not accept the relationship candidates, which remain for S6. {p9} {p162} {p255} {p273_274} {p295}

## 关系与证据

7条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Virgin Mary cross-chapter S3 identity group in S4.")
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
        and (row.get("name_en") or "").casefold() == "virgin mary"
        for row in manifest
    ), "Virgin Mary person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["canonical_name"] == "Virgin Mary"
    assert candidate["suggested_type"] == "person"
    assert candidate["candidate_origin"] == "body-mention"
    assert candidate["candidate_source_ref"] == "chp-1:01_CHP-1_sec_ii:l28-38#L297"
    assert not candidate.get("index_entry_id")
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)
    mention_count = sum(1 for row in sync.read_csv(TABLES / "mentions.csv")[1] if row.get("candidate_id") in CANDIDATES)
    assert mention_count == 30, mention_count

    ch1 = (ROOT / CHAPTER_1).read_text(encoding="utf-8-sig")
    ch6 = (ROOT / CHAPTER_6).read_text(encoding="utf-8-sig")
    ch9_intro = (ROOT / CHAPTER_9_INTRO).read_text(encoding="utf-8-sig")
    ch9_sec_ii = (ROOT / CHAPTER_9_SEC_II).read_text(encoding="utf-8-sig")
    ch10 = (ROOT / CHAPTER_10).read_text(encoding="utf-8-sig")
    assert "Madonna de Carmine with the Child in Her arms, St Teresa receiving the habit from the Virgin" in ch1
    assert "the Virgin Mary painted in the Quirinal by Guido Reni" in ch6
    assert "the Fatherland points out their merits to the Virgin and invokes her blessing on them" in ch9_intro
    assert "intercession of the Virgin" in ch9_sec_ii and "the Blessed Virgin, ingeniously comparing her to Esther" in ch9_sec_ii
    assert "religious subjects such as the Magdalene or the Virgin Mary" in " ".join(ch10.split())

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
        "canonical_name": "圣母玛利亚",
        "name_en": "Virgin Mary",
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
        "\n\n<a id=\"s4-virgin-mary-cross-chapter-person\"></a>\n\n"
        "### S4 person：Virgin Mary 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-3427`（body-mention，S2 source anchor `{candidate['candidate_source_ref']}`）保持 S3 组 `{GROUP}`，"
        f"映射至[Virgin Mary 人物卡](../../../{CARD_REL})。30条 S2 提及横跨第1、2、3、4、5、6、8、9、10章；"
        "Virgin Mary、the Virgin、Blessed Virgin 与 Madonna 等称谓在相应宗教／图像语境下指向该人物。"
        "具体绘画、雕像和作品题名不并入人物卡。7条直接 relation_candidate 原样保留待 S6："
        + ", ".join(sorted(RELATION_CANDIDATES)) + "。本轮未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Virgin Mary 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-3427` 映射至[Virgin Mary 人物卡](../units/persons/virgin-mary.md)。30条 S2 提及跨9个章节，"
        "第6章 p.162 与第10章 p.295 明示全名；人物与特定圣母像、作品保持区分。7条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Virgin Mary dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"identity_group={GROUP}; candidates={len(group_rows)}; mentions={mention_count}; direct_relation_candidates={len(direct_relations)}")
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
        f"applied: {CANDIDATES[0]} -> {KU_ID}; mentions={mention_count}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
