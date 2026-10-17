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

CANDIDATES = ("cand-0944", "cand-0945")
GROUP = "new-person:dorigny-louis-fc0f85a71c"
KU_ID = "units/persons/louis-dorigny"
CARD_REL = "04-knowledge/units/persons/louis-dorigny.md"
CHAPTER_7 = "02-sources/02-Markdown/07_CHP-7_sec_v.md"
CHAPTER_9_INTRO = "02-sources/02-Markdown/09_CHP-9_intro.md"
CHAPTER_9_II = "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/D.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp9-p250-widmann-country-house-frescoes",
    "st-chp9-p250-zenobio-fresco-cycle",
    "st-chp9-p251-manin-employed-dorigny",
    "st-chp9-p268-manin-dorigny",
    "st-chp9-p268-dorigny-passeriano-villa",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第7章；印刷页201；OCR L49–50",
            "sentence_summary": (
                "Haskell称 Louis Dorigny 与数位意大利艺术家赴维也纳，为 Prince Eugene 的 Upper 与 Lower Belvedere 绘制壁画。"
            ),
            "original_quotes": [
                {
                    "source_span": "lines 49–50",
                    "text": (
                        "Louis Dorigny, Marc’antonio Chiarini, Gaetano Fanti, Carlo Carlone and others came from Italy "
                        "to paint frescoes in the Upper and Lower Belvederes"
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_7,
                "source_span": "lines 49–50; print p. 201",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页250–251；OCR L92、111",
            "sentence_summary": (
                "第250页称法国画家 Dorigny 受聘为 Zenobio 宫绘制神话壁画，并记其为 Widmann 乡间住宅绘制壁画；"
                "第251页称 Manin 家族多项工程雇用画家 Luigi Dorigny。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 92",
                    "text": "the French artist Dorigny had been called in to paint a series of spectacular mythological frescoes",
                },
                {
                    "source_span": "line 98",
                    "text": "their country house at Bagnoli di Sopra was painted by Dorigny with frescoes of Diana and Actaeon",
                },
                {
                    "source_span": "line 111",
                    "text": "they employed the same team of artists, the architect Domenico Rossi and the painter Luigi Dorigny, on many of their enterprises",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_9_INTRO,
                "source_span": "lines 92, 98, 111; print pp. 250–251",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页268、270；OCR L15、28",
            "sentence_summary": (
                "第268页称 Manin 家族常用画家 Louis Dorigny，并称其装饰 Passeriano 别墅；"
                "第270页以 Dorigny 姓氏列入受雇画家。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 15",
                    "text": "Whenever they could they made use of the painter Louis Dorigny, who also decorated their villa at Passeriano",
                },
                {
                    "source_span": "line 28",
                    "text": "Rich families, old and new, employed Lazzarini, Bambini and Dorigny to supply pictures and frescoes",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_9_II,
                "source_span": "lines 15, 28; print pp. 268, 270",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；D.csv#46 主项、D.csv#47 子项；印刷页201、250、251、268、270",
            "sentence_summary": (
                "索引主项 Dorigny, Louis 列第201、250、251、268、270页；work for Manin 子项列第268页。"
            ),
            "original_quotes": [
                {
                    "source_span": "index entry D.csv#46",
                    "text": "| Dorigny, Louis |  |  |  | 201, 250, 251, 268, 270 |",
                },
                {
                    "source_span": "index entry D.csv#47",
                    "text": "| Dorigny, Louis |  | work for Manin |  | 268 |",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entries D.csv#46–47",
            },
        },
    ]
    frontmatter = {
        "title": "路易·多里尼（Louis Dorigny）",
        "name_en": "Louis Dorigny",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p201 = f"[第7章 p.201](../../../{CHAPTER_7})（L49–50）"
    p250 = f"[第9章 p.250](../../../{CHAPTER_9_INTRO})（L92、98）"
    p251 = f"[第9章 p.251](../../../{CHAPTER_9_INTRO})（L111）"
    p268 = f"[第9章 p.268](../../../{CHAPTER_9_II})（L15）"
    p270 = f"[第9章 p.270](../../../{CHAPTER_9_II})（L28）"
    index = f"[书后索引](../../../{INDEX_FILE})（D.csv#46–47）"
    body = f"""## 内容

### 描述

**中文：** 本卡将索引主项“Dorigny, Louis”及其“work for Manin”子项映射到同一人物 KU。跨章材料分别使用 Louis Dorigny、Luigi Dorigny 与 Dorigny：第7章称 Louis Dorigny 与多名意大利艺术家前往维也纳，为 Prince Eugene 的 Upper、Lower Belvedere 绘制壁画；第9章 p.250 称法国画家 Dorigny 为 Zenobio 宫绘制神话壁画，并为 Widmann 乡间住宅绘制 Diana 与 Actaeon 壁画；p.251 称 Manin 家族雇用画家 Luigi Dorigny；p.268 则明确以 Louis Dorigny 指称 Manin 家族常用的画家并记其装饰 Passeriano 别墅。索引同一主项及 Manin 子项把这些页码聚合在一起，正文全名及同一 Manin 赞助语境支持将 Louis／Luigi 两种写法归入同一书内人物。本卡不使用外部身份记录，也不扩写脚注未核实的生平。{p201} {p250} {p251} {p268} {p270} {index}

**English:** This card maps the index main entry “Dorigny, Louis” and its “work for Manin” subentry to one person KU. Across chapters, the book uses Louis Dorigny, Luigi Dorigny, and Dorigny. Chapter 7 says that Louis Dorigny came from Italy with other artists to paint frescoes in Prince Eugene’s Upper and Lower Belvederes. Chapter 9, p.250 calls Dorigny a French artist engaged to paint mythological frescoes at the Zenobio palace and says that he painted Diana and Actaeon frescoes at the Widmann country house. Page 251 says that the Manin employed the painter Luigi Dorigny; p.268 names Louis Dorigny as a painter they used whenever possible and records his decoration of their Passeriano villa. The shared index entry and Manin subentry aggregate these locations, while the full names and repeated Manin context support treating Louis and Luigi as forms for the same book-local person. No external identity record is used and no biography from unchecked footnotes is added. {p201} {p250} {p251} {p268} {p270} {index}

### 身份边界

本卡只确认 Haskell 书内的 Louis／Luigi Dorigny 人物组。第270页仅以姓氏列举 Dorigny，单独看不足以识别人物；该页定位按索引保留，不作为独立身份锚点。Zenobio、Widmann、Manin、Prince Eugene 及各处建筑和作品均为独立对象。具体委托、雇用和装饰事实仍是 S2 关系候选，留待 S6 审查。

This card identifies only the Louis/Luigi Dorigny person group within Haskell’s book. Page 270 gives only the surname Dorigny, which is insufficient as an independent identity anchor; the page location is retained through the index. Zenobio, Widmann, Manin, Prince Eugene, and the buildings and works remain distinct objects. Specific commissions, employment, and decoration claims remain S2 relation candidates for S6 review.

## 关系与证据

5条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the cross-chapter Louis Dorigny S3 person group in S4.")
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
        and (row.get("name_en") or "").casefold() == "louis dorigny"
        for row in manifest
    ), "Louis Dorigny person KU already exists"

    expected = {
        "cand-0944": ("D.csv#46", "Dorigny, Louis", "201, 250, 251, 268, 270", ""),
        "cand-0945": ("D.csv#47", "Dorigny, Louis", "268", "work for Manin"),
    }
    for cid in CANDIDATES:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        entry, name, pages, subentry = expected[cid]
        assert candidate["index_entry_id"] == entry
        assert candidate["canonical_name"] == name
        assert candidate["index_page_range"] == pages
        assert candidate.get("sub_entry", "") == subentry
        assert candidate["suggested_type"] == "person"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    sources = {
        CHAPTER_7: (ROOT / CHAPTER_7).read_text(encoding="utf-8-sig"),
        CHAPTER_9_INTRO: (ROOT / CHAPTER_9_INTRO).read_text(encoding="utf-8-sig"),
        CHAPTER_9_II: (ROOT / CHAPTER_9_II).read_text(encoding="utf-8-sig"),
    }
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    required = {
        CHAPTER_7: ("Louis Dorigny, Marc’antonio Chiarini",),
        CHAPTER_9_INTRO: (
            "the French artist Dorigny had been called in to paint a series of spectacular mythological frescoes",
            "their country house at Bagnoli di Sopra was painted by Dorigny with frescoes of Diana and Actaeon",
            "the painter Luigi Dorigny",
        ),
        CHAPTER_9_II: (
            "Whenever they could they made use of the painter Louis Dorigny, who also decorated their villa at Passeriano",
            "Rich families, old and new, employed Lazzarini, Bambini and Dorigny to supply pictures and frescoes",
        ),
    }
    for source_file, quotes in required.items():
        normalized = " ".join(sources[source_file].split())
        for quote in quotes:
            assert " ".join(quote.split()) in normalized, (source_file, quote)
    assert "| Dorigny, Louis |  |  |  | 201, 250, 251, 268, 270 |" in index_text
    assert "| Dorigny, Louis |  | work for Manin |  | 268 |" in index_text

    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == RELATION_CANDIDATES, direct_relations

    planned_alignment = [dict(row) for row in alignments]
    for cid in CANDIDATES:
        target = next(row for row in planned_alignment if row.get("candidate_id") == cid and not row.get("external_source"))
        target["ku_id"] = KU_ID
        target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": "路易·多里尼",
        "name_en": "Louis Dorigny",
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
        "\n\n<a id=\"s4-louis-dorigny-cross-chapter-person\"></a>\n\n"
        "### S4 person：Louis／Luigi Dorigny 跨章索引组登记（2026-10-17）\n\n"
        f"`cand-0944`（D.csv#46，pp.201、250、251、268、270）与 `cand-0945`（D.csv#47，work for Manin，p.268）"
        f"按 S3 组 `{GROUP}` 共同映射至[Louis Dorigny 人物卡](../../../{CARD_REL})。第7章 p.201 明称 Louis Dorigny；"
        "第9章 p.251 以 Luigi Dorigny 指 Manin 家族雇用的画家，p.268 又称 Louis Dorigny，并记其装饰 Manin 的 Passeriano 别墅。"
        "同一索引主项和 Manin 子项及共享语境支持该书内姓名变体归并；第270页仅列姓氏，不独立承担身份识别。"
        "5条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。"
        "本轮未新增正式关系或外部身份记录。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Louis／Luigi Dorigny 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-0944` 与 `cand-0945` 按 S3 组 `{GROUP}` 共同映射至[Louis Dorigny 人物卡]"
        "(../units/persons/louis-dorigny.md)。第7章 p.201 全名、Manin 子项、p.251 的 Luigi 与 p.268 的 Louis 写法及赞助语境相合。"
        "第270页只见姓氏，按索引保留定位，不单独作身份锚点。5条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Louis Dorigny dry-run passed: {CANDIDATES} -> {KU_ID}")
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
        f"applied: {len(CANDIDATES)} candidates -> {KU_ID}; "
        f"registered={sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; "
        f"pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; "
        f"manifest={sync.fmt(len(planned_manifest))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
