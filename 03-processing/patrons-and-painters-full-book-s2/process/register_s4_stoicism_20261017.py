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

CANDIDATE = "cand-2510"
GROUP = "sg3-term-cand-2510"
KU_ID = "units/terms/stoicism-seventeenth-century"
CARD_REL = "04-knowledge/units/terms/stoicism-seventeenth-century.md"
NAME_ZH = "斯多葛主义"
NAME_EN = "Stoicism in the seventeenth century"
BOOK_CITATION = (
    "Francis Haskell, Patrons and Painters, revised and enlarged edition "
    "(Yale University Press, 1980; this printing 2006)."
)
RELATION_CANDIDATES = {
    "st-chp5-p143-rosa-quotation-alludes-to-stoicism",
    "st-chp5-p143-rosa-stoic-roast-meat-letter",
    "st-chp5-p143-rosa-studied-stoics-for-art-themes",
    "st-chp5-p143-stoicism-appealed-to-the-disappointed",
    "st-chp5-p143-stoicism-colored-ethics-and-imagery",
    "st-chp5-p143-stoicism-gained-ground-in-europe",
    "st-chp5-p144-regulus-raised-small-picture-idiom-to-heroic-tragedy",
    "st-chp5-p143-stoicism-virtually-replaced-christianity",
    "st-chp5-seciv-note-l41-p143-rosa-described-himself-as-stoic",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页143；OCR L15–16",
            "sentence_summary": (
                "Haskell 将 Rosa 信中的 Stoic 比喻解释为对 Stoicism 的暗指，并概述该哲学自16世纪后期在欧洲传播；"
                "其关于它对基督教信念替代作用的表述明确限定为 some daring thinkers。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 15",
                    "text": "So too is the allusion to Stoicism.",
                },
                {
                    "source_span": "lines 15–16",
                    "text": "All over Europe this philosophy had been gaining ground ever since the late sixteenth century until for some daring thinkers it virtually replaced Christianity as a guiding creed.",
                },
                {
                    "source_span": "line 16",
                    "text": "Salvator Rosa, in particular, would passionately study the Stoics and search in their writings for themes for his pictures and prints.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iv.md",
                "source_span": "lines 15–16; print p. 143",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页144；OCR L26",
            "sentence_summary": (
                "Haskell 将 Rosa 对《Regulus》题材的处理解释为经由研究斯多葛历史学家，把小型绘画题材提升为英雄悲剧。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 26",
                    "text": "Rosa’s grudging obligation to the bamboccianti and instinctive love of the picturesque are raised to high, heroic tragedy through his study of the Stoic historians.",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iv.md",
                "source_span": "line 26; print p. 144",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页143；注2；OCR L41",
            "sentence_summary": (
                "Haskell 的注2称 Rosa 在1651年致 Ricciardi 的信中自称 Stoic；本卡只记录书中注释的报告，"
                "不将被引信件当作本轮独立核读的原件。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 41",
                    "text": "Rosa referred to himself as a Stoic in a letter to Ricciardi dated 27 May 1651",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/05_CHP-5_sec_iv.md",
                "source_span": "line 41; print p. 143; footnote 2",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；S.csv#199",
            "sentence_summary": "索引主项将 Stoicism in 17th century 定位于第5章印刷页142–144。",
            "original_quotes": [
                {
                    "source_span": "index row S.csv#199",
                    "text": "| Stoicism in 17th century |  |  |  | 142, 143, 144 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/03-Index/03-1-Index-MD/S.md",
                "source_span": "index row S.csv#199",
            },
        },
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "term",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#s4-stoicism",
    }
    front = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p143 = "[第5章 p.143](../../../02-sources/02-Markdown/05_CHP-5_sec_iv.md)（L15–16）"
    p144 = "[第5章 p.144](../../../02-sources/02-Markdown/05_CHP-5_sec_iv.md)（L26）"
    index = "[书后索引 S.csv#199](../../../02-sources/03-Index/03-1-Index-MD/S.md)"
    body = f"""## 内容

### 描述

**中文：** 本术语以书后索引 S.csv#199 的 Stoicism in 17th century 为锚，限于哈斯克尔第5章 pp.143–144 对斯多葛主义的讨论。作者称这一哲学自16世纪后期在欧洲传播，并对思想家、艺术家的伦理与图像产生影响；“几乎取代基督教信念”明确限定为 some daring thinkers 的情形。哈斯克尔还将 Rosa 信中的 Stoic 比喻解释为对斯多葛主义的暗指，称 Rosa 研究斯多葛作者以寻找绘画主题，并以《Regulus》说明其对艺术题材的影响。以上均为本书的历史概括或作者解释，不作为完整的斯多葛学派史，也不扩展为独立核实的普遍历史结论。{p143}；{p144}；{index}

**English:** This term is anchored to the index entry S.csv#199, “Stoicism in 17th century,” and is limited to Haskell’s discussion on pp.143–144 of Chapter 5. The author says the philosophy spread in Europe from the late sixteenth century and influenced the ethics and imagery of thinkers and artists; the claim that it “virtually replaced” Christianity as a guiding creed is explicitly limited to some daring thinkers. Haskell also interprets a Stoic metaphor in a letter by Rosa as an allusion to Stoicism, says Rosa studied Stoic writings for artistic themes, and uses Regulus to describe their influence on his treatment of subjects. These are the book’s historical summary and the author’s interpretation, not a comprehensive history of Stoicism or independently verified general conclusions. {p143}; {p144}; {index}

### 名称与语境

| 字段 | 内容 | 依据 |
|---|---|---|
| 中文规范名 | {NAME_ZH} | 项目术语译名 |
| 书中索引名 | Stoicism in 17th century | {index}；pp.142–144 |
| 讨论时段 | Haskell 将传播脉络追溯至16世纪后期，并讨论17世纪思想与艺术语境 | {p143}；{p144} |
| 书中具体语境 | Salvator Rosa 的信件比喻、对 Stoic writings 的研读及《Regulus》题材阐释 | {p143}；{p144} |
| 归属限定 | “几乎取代基督教信念”只指作者所称的 some daring thinkers；不泛化至所有思想家或整个时期 | {p143} |

## 关系与证据

以下9条直接 S2 关系候选留待 S6 逐项审查；本卡不将其登记为正式关系：{", ".join(sorted(RELATION_CANDIDATES))}。
"""
    return f"---\n{front}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register the Stoicism term identity group as one S4 term KU."
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
    assert candidate["index_entry_id"] == "S.csv#199"
    assert candidate["canonical_name"] == "Stoicism in 17th century"
    assert candidate["index_page_range"] == "142, 143, 144"
    assert candidate["suggested_type"] == "term"
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
        or (row.get("type") == "term" and "stoic" in (row.get("name_en") or "").casefold())
        for row in manifest
    )
    card_path = ROOT / CARD_REL
    assert not card_path.exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted

    index = (ROOT / "02-sources/03-Index/03-1-Index-MD/S.md").read_text(encoding="utf-8-sig")
    chapter = (ROOT / "02-sources/02-Markdown/05_CHP-5_sec_iv.md").read_text(encoding="utf-8-sig")
    assert "| Stoicism in 17th century |  |  |  | 142, 143, 144 |" in index
    assert "So too is the allusion to Stoicism." in chapter
    assert "for some daring thinkers it virtually replaced" in chapter
    assert "Salvator Rosa, in particular, would passionately study the Stoics" in chapter
    assert "through his study of the Stoic historians" in chapter
    assert "Rosa referred to himself as a Stoic in a letter to Ricciardi dated 27 May 1651" in chapter

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
    ]) == 4

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE)
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "term",
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
        "\n\n<a id=\"s4-stoicism\"></a>\n\n"
        "### S4 term：Stoicism in 17th century 术语组登记（2026-10-17）\n\n"
        f"{CANDIDATE}（S.csv#199；S3 组 {GROUP}）映射至[斯多葛主义术语卡](../../../{CARD_REL})。"
        "第5章 pp.143–144 的正文与注释讨论该哲学在 Haskell 所述历史中的传播、伦理／图像影响及 Rosa 的相关实践；索引主项限定页段。"
        "卡片保留作者解释与 some daring thinkers 限定，不将局部叙述扩展成全面哲学史；关于 Rosa 1651年自称 Stoic 的内容只按 Haskell 注2转述，不称已独立核读原信。"
        f"9条直接 relation_candidate 保持待 S6 审查：{', '.join(sorted(RELATION_CANDIDATES))}。"
        f"本轮未写 relations.csv、未登记正式关系，未新增 sources.csv 记录。S4 累计登记{sync.fmt(totals['registered_groups'])}组/"
        f"{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 term：Stoicism in 17th century 术语身份组（2026-10-17）\n\n"
        f"{CANDIDATE}（S.csv#199）登记至[斯多葛主义术语卡](../units/terms/stoicism-seventeenth-century.md)。"
        "卡片按 pp.143–144 的作者叙述限定对象范围，保留 “some daring thinkers” 限定及 Rosa 1651年信件为 Haskell 注释转述的证据状态。"
        "9条直接关系候选留待 S6，未新增正式关系。"
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
        print(f"S4 Stoicism dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"index=S.csv#199; mentions=4; relation_candidates={len(direct_relation_ids)}")
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
