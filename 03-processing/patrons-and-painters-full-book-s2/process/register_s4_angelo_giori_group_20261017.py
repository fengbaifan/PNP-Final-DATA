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

CANDIDATES = ("cand-1190",)
GROUP = "new-person:angelo-giori-610dcba3b7"
KU_ID = "units/persons/angelo-giori"
CARD_REL = "04-knowledge/units/persons/angelo-giori.md"
CHAPTER_2_II = "02-sources/02-Markdown/02_CHP-2_sec_ii.md"
CHAPTER_2_VII = "02-sources/02-Markdown/02_CHP-2_sec_vii.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/G.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp2-secii-l118-125-angelo-giori-artistic-interest",
    "st-chp2-secii-l118-125-angelo-giori-background",
    "st-chp2-secii-l118-125-angelo-giori-claude-patron",
    "st-chp2-secii-l118-125-angelo-giori-claude-pictures",
    "st-chp2-secii-l118-125-angelo-giori-supervision",
    "st-chp2-secii-l118-125-angelo-giori-admires-sacchi",
    "st-chp2-secvii-l5-19-giori-urges-congratulations",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第2章；印刷页41；OCR L125",
            "sentence_summary": (
                "Haskell称 Angelo Giori 曾在 Camerino 任校长，听说有晋升机会后步行到 Rome；"
                "他监督 Urban VIII 墓的工程，是 Barberini 家族的 protégé，并是 Claude 的特别赞助人。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 125",
                    "text": (
                        "the work which was supervised by a protege of the Barberini, the humbly born and rather mean "
                        "Angelo Giori, who had walked to Rome from Camerino where he worked as a schoolmaster when he "
                        "heard of the possibilities of preferment"
                    ),
                },
                {
                    "source_span": "line 125",
                    "text": "the special patron of Claude, seven of whose pictures he owned",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_2_II,
                "source_span": "line 125; print p. 41",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第2章；印刷页59；OCR L14",
            "sentence_summary": (
                "Haskell称在 Bernini 完成 Urban VIII 墓时，负责此事的 Angelo Giori 致信遭流放的枢机，"
                "建议他们向这位艺术家致贺；原文没有说明 Giori 所负责事务的行政范围。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 14",
                    "text": (
                        "Angelo Giori, who was in charge, wrote to the exiled Cardinals and suggested that they should "
                        "congratulate the artist"
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_2_VII,
                "source_span": "line 14; print p. 59",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；G.csv#97；印刷页41、59",
            "sentence_summary": "书后索引以 Giori, Angelo 为主项，定位第41页与第59页。",
            "original_quotes": [
                {"source_span": "index entry G.csv#97", "text": "| Giori, Angelo |  |  |  | 41, 59 |"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry G.csv#97",
            },
        },
    ]
    frontmatter = {
        "title": "安杰洛·焦里（Angelo Giori）",
        "name_en": "Angelo Giori",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p41 = f"[第2章 p.41](../../../{CHAPTER_2_II})（L125）"
    p59 = f"[第2章 p.59](../../../{CHAPTER_2_VII})（L14）"
    index = f"[书后索引](../../../{INDEX_FILE})（G.csv#97）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记书后索引 G.csv#97“Giori, Angelo”所指的 Angelo Giori。索引将他定位于第2章第41、59页；两处正文均重复其全名，构成跨章身份锚点。第41页中，Haskell称他曾在 Camerino 任校长，听说有晋升机会后步行到 Rome；后来监督 Urban VIII 墓的工程，被作者称为 Barberini 家族的 protégé，并是 Claude 的特别赞助人，拥有 Claude 的七幅画。作者在同段使用 “rather mean” 这一评价，本卡将其保留为作者措辞，不作客观人格事实。第59页称在 Bernini 完成 Urban VIII 墓时，Giori 致信遭流放的枢机，建议他们向艺术家致贺；“who was in charge” 的责任范围未说明。以上均是 Haskell 的书内叙述，不据脚注补充外部生平。{p41} {p59} {index}

**English:** This card records the Angelo Giori named in index entry G.csv#97. The index locates him on pages 41 and 59 of Chapter 2, where the text repeats his full name and provides cross-chapter identity anchors. On page 41, Haskell says that Giori had been a schoolmaster in Camerino and walked to Rome after hearing of opportunities for preferment; he later supervised work on Urban VIII’s tomb, is described by the author as a Barberini protégé, and is called Claude’s special patron who owned seven of Claude’s pictures. Haskell also uses the evaluative phrase “rather mean”; this card preserves it as the author’s characterization and does not treat it as an objective personality fact. Page 59 says that, when Bernini completed Urban VIII’s tomb, Giori wrote to the exiled Cardinals suggesting that they congratulate the artist; the scope of “who was in charge” is unspecified. These are Haskell’s statements in the book; no external biography is added from cited footnotes. {p41} {p59} {index}

### 身份边界

本卡只对应索引及第2章两处具名的 Angelo Giori。第41页注5、注6所引材料未在本轮独立核读；不推定他与 Barberini 的正式职务、亲缘或法律关系，也不补充“负责”一词的行政范围。Bernini、Claude、Sacchi、Urban VIII、枢机、Camerino 与 Rome 均为独立对象。

This card refers only to the named Angelo Giori in the index and the two Chapter 2 passages. The materials cited in notes 5 and 6 on page 41 have not been independently consulted. No formal office, kinship, or legal relationship with the Barberini is inferred, and the administrative scope of “in charge” is not expanded. Bernini, Claude, Sacchi, Urban VIII, the Cardinals, Camerino, and Rome remain separate objects.

## 关系与证据

7条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Angelo Giori's S3 person identity group in S4.")
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
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert not (ROOT / CARD_REL).exists()
    assert CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en") or "").casefold() == "angelo giori"
        for row in manifest
    ), "Angelo Giori person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "G.csv#97"
    assert candidate["canonical_name"] == "Giori, Angelo"
    assert candidate["index_page_range"] == "41, 59"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    chapter41 = (ROOT / CHAPTER_2_II).read_text(encoding="utf-8-sig")
    chapter59 = (ROOT / CHAPTER_2_VII).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    for quote in (
        "Angelo Giori, who had walked to Rome from Camerino where he worked as a schoolmaster",
        "the special patron of Claude, seven of whose pictures he owned",
    ):
        assert " ".join(quote.split()) in " ".join(chapter41.split()), quote
    assert "Angelo Giori, who was in charge, wrote to the exiled Cardinals" in " ".join(chapter59.split())
    assert "| Giori, Angelo |  |  |  | 41, 59 |" in index_text

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
        "canonical_name": "安杰洛·焦里",
        "name_en": "Angelo Giori",
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
        "\n\n<a id=\"s4-angelo-giori-person\"></a>\n\n"
        "### S4 person：Angelo Giori 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-1190`（G.csv#97，pp.41、59）保持 S3 组 `{GROUP}`，映射至[Angelo Giori 人物卡](../../../{CARD_REL})。"
        "书后索引以同一全名定位两页，正文第41、59页均再次具名；不需要依姓氏或外部相似身份合并。"
        "第41页记录 Haskell 对其 Camerino 校长经历、迁往 Rome、监督 Urban VIII 墓工程、Barberini protégé 身份及 Claude 收藏的叙述；"
        "“rather mean”保留为作者评价。第59页记其在 Bernini 完成墓葬工程时致信遭流放的枢机；责任范围未明。注5、注6引文未独立核读。"
        "7条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。"
        "本轮未新增正式关系或外部字段事实。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Angelo Giori 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-1190`（G.csv#97，pp.41、59）映射至[Angelo Giori 人物卡](../units/persons/angelo-giori.md)。"
        "索引同名主项、跨章页码和正文重复全名支持同一人物组；第41页关于其生平、监督 Urban VIII 墓工程及 Claude 收藏的内容，"
        "以及第59页的致信叙述，均保留为 Haskell 书内说法。脚注来源未独立核读，“rather mean”和“who was in charge”的范围分别保持作者评价及未定状态。"
        "7条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Angelo Giori dry-run passed: {CANDIDATES} -> {KU_ID}")
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
