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

CANDIDATES = ("cand-2794",)
GROUP = "new-person:cornelius-de-wael-34ec2709b7"
KU_ID = "units/persons/cornelius-de-wael"
CARD_REL = "04-knowledge/units/persons/cornelius-de-wael.md"
CHAPTER = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/UVWXYZ.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp5-p122-wael-clients",
    "st-chp5-p122-wael-stock",
    "st-chp5-p122-wael-trade",
    "st-chp5-p122-wael-gaulli-acquaintance",
    "st-chp5-p122-wael-small-pictures",
    "st-chp5-p122-wael-important-artists",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页122；OCR L18–19",
            "sentence_summary": (
                "Haskell称 Cornelius de Wael 于1657年离开 Genoa，参与广泛商业活动并拥有大量待售画作；"
                "其交易对象主要是同乡，并拥有 Gaulli 的早期作品和其他较小画家作品。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 18",
                    "text": (
                        "The artist Cornelius de Wael, for instance, who left Genoa in 1657, engaged in extensive "
                        "commercial activities and had a large gallery of pictures which were evidently for sale."
                    ),
                },
                {
                    "source_span": "lines 18–19",
                    "text": (
                        "He dealt principally with his own compatriots, both as regards artists and clients. Though he "
                        "also owned early works by Gaulli whom he must have known in Genoa as well as smaller pictures "
                        "by Italian genre, flower and battle painters, he played little part in the lives of the more "
                        "important artists."
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 18–19; print p. 122",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；UVWXYZ.csv#131；印刷页122",
            "sentence_summary": "书后索引以 Wael, Cornelius de 为主项，定位第122页。",
            "original_quotes": [
                {
                    "source_span": "index entry UVWXYZ.csv#131",
                    "text": "| Wael, Cornelius de |  |  |  | 122 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry UVWXYZ.csv#131",
            },
        },
    ]
    frontmatter = {
        "title": "科内利斯·德·瓦尔（Cornelius de Wael）",
        "name_en": "Cornelius de Wael",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p122 = f"[第5章 p.122](../../../{CHAPTER})（L18–19）"
    index = f"[书后索引](../../../{INDEX_FILE})（UVWXYZ.csv#131）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记书后索引“Wael, Cornelius de”及第5章 p.122 全名所指的人物。Haskell称他于1657年离开 Genoa，积极从事商业活动，并拥有大量显然待售的画作；他主要与同乡画家及客户往来。作者还说他拥有 Gaulli 的早期作品、其他意大利风俗画家、花卉画家和战争画家所作的小幅画，并以“must have known in Genoa”推断他与 Gaulli 的相识。相关数量、收藏内容和作者对其在重要艺术家生活中作用较小的评价均保留为书内说法；不据此补充生平或逐件作品目录。{p122} {index}

**English:** This card records the person named in the index as “Wael, Cornelius de” and by full name on Chapter 5, p.122. Haskell says that he left Genoa in 1657, engaged in extensive commercial activity, and had a large gallery of pictures apparently for sale; he dealt mainly with compatriots as artists and clients. The author also says that he owned early works by Gaulli and smaller pictures by Italian genre, flower, and battle painters, and infers that he “must have known” Gaulli in Genoa. The collection claims and Haskell’s assessment that de Wael played little part in the lives of more important artists remain attributed to the book; no biography or itemized work catalogue is added. {p122} {index}

### 身份边界

身份依据限于索引主项和第5章同页正文全名。Gaulli 与其他画家、Genoa 及画作收藏均为独立对象；“must have known”保留为 Haskell 的推断，不改写为确定关系。作者所述商业活动不用于推导未记载的职业头衔或具体交易。

Identification is limited to the index main entry and the full name in the Chapter 5 passage. Gaulli, the other painters, Genoa, and the picture collection remain distinct objects. “Must have known” is retained as Haskell’s inference and is not rewritten as a certain relationship. The account of commercial activity is not used to infer an unrecorded occupational title or specific transaction.

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Cornelius de Wael's S3 person identity group in S4.")
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
        and (row.get("name_en") or "").casefold() == "cornelius de wael"
        for row in manifest
    ), "Cornelius de Wael person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "UVWXYZ.csv#131"
    assert candidate["canonical_name"] == "Wael, Cornelius de"
    assert candidate["index_page_range"] == "122"
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
    normalized = " ".join(chapter.split())
    for quote in (
        "The artist Cornelius de Wael, for instance, who left Genoa in 1657",
        "engaged in extensive commercial activities and had a large gallery of pictures which were evidently for sale",
        "He dealt principally with his own compatriots",
        "owned early works by Gaulli whom he must have known in Genoa",
        "he played little part in the lives of the more important artists",
    ):
        assert " ".join(quote.split()) in normalized, quote
    assert "| Wael, Cornelius de |  |  |  | 122 |" in index_text

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
        "canonical_name": "科内利斯·德·瓦尔",
        "name_en": "Cornelius de Wael",
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
        "\n\n<a id=\"s4-cornelius-de-wael-person\"></a>\n\n"
        "### S4 person：Cornelius de Wael 直接关系端点登记（2026-10-17）\n\n"
        f"`cand-2794`（UVWXYZ.csv#131，p.122）保持 S3 组 `{GROUP}`，映射至[Cornelius de Wael 人物卡]"
        f"(../../../{CARD_REL})。索引主项和正文全名一致。Haskell记述其于1657年离开 Genoa、经商并持有大量待售画作，"
        "与同乡的艺术家和客户往来，且拥有不同类别的小幅画；“must have known”保留为作者推断。"
        "6条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。"
        "本轮未新增正式关系或外部身份记录。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Cornelius de Wael 身份组登记（2026-10-17）\n\n"
        f"`cand-2794`（UVWXYZ.csv#131）映射至[Cornelius de Wael 人物卡](../units/persons/cornelius-de-wael.md)。"
        "索引及第5章 p.122 正文给出相同全名；人物描述保留 Haskell 对其商业活动、收藏及其与 Gaulli 相识的推断。"
        "6条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Cornelius de Wael dry-run passed: {CANDIDATES} -> {KU_ID}")
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
