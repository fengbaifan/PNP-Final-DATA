from __future__ import annotations

import argparse
import re
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

CANDIDATES = ("cand-0184", "cand-0185")
GROUP = "new-person:antonio-barbaro-antonio-barbaro-conception-e91bacacf4"
KU_ID = "units/persons/antonio-barbaro"
CARD_REL = "04-knowledge/units/persons/antonio-barbaro.md"
CHAPTER = "02-sources/02-Markdown/09_CHP-9_intro.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/B.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp9-p248-facade-design-and-building",
    "st-chp9-p248-barbaro-fought-war-of-candia",
    "st-chp9-p248-antonio-ambassador-in-rome",
    "st-chp9-p249-barbaro-conduct",
    "st-chp9-p249-barbaro-will-location",
    "st-chp9-p249-barbaro-returned-and-opposed-morosini",
    "st-chp9-p253-barbaro-dolfin-roman-epics",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页248；OCR L42–46",
            "sentence_summary": (
                "Haskell称 Antonio Barbaro 曾参与 Candia 战争；S. Maria del Giglio 外立面由其设计，"
                "旨在颂扬他本人及兄弟；并称他曾在 Rome 任大使。"
            ),
            "original_quotes": [
                {
                    "source_span": "lines 42–43",
                    "text": (
                        "There was, for instance, the façade of S. Maria del Giglio, which was designed by\n"
                        "Antonio Barbaro, who had fought in the war of Candia, as an apotheosis of himself and his brothers"
                    ),
                },
                {
                    "source_span": "lines 45–46",
                    "text": "Rome, where\nAntonio had served as ambassador.",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 42–46; print p. 248",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页249；OCR L79",
            "sentence_summary": (
                "Haskell称 Barbaro 在 Candia 战争中的表现有些不光彩，Morosini 以无能为由将其免职；"
                "他随后回到 Venice 并试图煽动对 Morosini 的敌意。该段转述及所引脚注来源未独立核读。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 79",
                    "text": (
                        "Antonio Barbaro’s conduct in the war of Candia had been somewhat discreditable, "
                        "and he had been dismissed by Francesco Morosini for incompetence. He thereupon returned "
                        "to Venice and did everything possible to whip up hostility against Morosini"
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "line 79; print p. 249",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第9章；印刷页253；OCR L129",
            "sentence_summary": "Haskell称 Tiepolo 的 Roman epics 纪念了 Antonio Barbaro 与 Daniele Dolfin。",
            "original_quotes": [
                {
                    "source_span": "line 129",
                    "text": "the Roman epics with which he had commemorated them",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "line 129; print p. 253",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；B.csv#31–32；印刷页248–253",
            "sentence_summary": (
                "索引以 Barbaro, Antonio 为主项，定位第248、249、253页；and S. Maria del Giglio 子项定位第248、249页。"
            ),
            "original_quotes": [
                {"source_span": "index entry B.csv#31", "text": "| Barbaro, Antonio |  |  |  | 248, 249, 253 |"},
                {
                    "source_span": "index entry B.csv#32",
                    "text": "| Barbaro, Antonio |  | and S. Maria del Giglio |  | 248, 249 |",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entries B.csv#31–32",
            },
        },
    ]
    frontmatter = {
        "title": "安东尼奥·巴尔巴罗（Antonio Barbaro）",
        "name_en": "Antonio Barbaro",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p248 = f"[第9章 p.248](../../../{CHAPTER})（L42–46）"
    p249 = f"[第9章 p.249](../../../{CHAPTER})（L79）"
    p253 = f"[第9章 p.253](../../../{CHAPTER})（L129）"
    index = f"[书后索引](../../../{INDEX_FILE})（B.csv#31–32）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记书后索引主项“Barbaro, Antonio”及其 S. Maria del Giglio 子项所指的 Antonio Barbaro。跨页全名、同一建筑语境及第253页再次出现的 Antonio Barbaro 支持将两条索引候选合为一个书内人物身份组。Haskell 称他曾参与 Candia 战争、曾在 Rome 任大使，并称 S. Maria del Giglio 外立面由他设计，以颂扬他本人及兄弟；这只是作者在书中的叙述。第249页进一步转述其战时表现、被 Morosini 免职及回到 Venice 后的行动，相关脚注来源未独立核读。本卡不补充外部生平，也不把这些陈述登记为正式关系。{p248} {p249} {p253} {index}

**English:** This card records the Antonio Barbaro named in the index main entry “Barbaro, Antonio” and its S. Maria del Giglio subentry. The repeated full name, the shared architectural context, and the further mention of Antonio Barbaro on page 253 support treating the two index candidates as one book-local person identity group. Haskell says that he had fought in the War of Candia and served as ambassador in Rome, and attributes the design of the façade of S. Maria del Giglio to him as an apotheosis of himself and his brothers; these remain the author’s statements in the book. Page 249 also recounts his wartime conduct, dismissal by Morosini, and actions after returning to Venice; the cited footnote sources have not been independently consulted. This card adds no external biography and does not register these statements as formal relations. {p248} {p249} {p253} {index}

### 身份边界

本卡只对应 Haskell 书中具名的 Antonio Barbaro。第248页注4提及其遗嘱出版物，第249页注1援引相关研究，但本轮未独立查阅这些材料；没有据此扩展亲属、任职年份或具体军旅经历。S. Maria del Giglio、其建筑师 Giuseppe Sardi、Morosini、Rome、Candia 战争及 Roman epics 均为独立端点，不并入人物身份。

This card refers only to the named Antonio Barbaro in Haskell’s book. Note 4 on page 248 refers to a publication of his will, and note 1 on page 249 cites related scholarship; neither was independently consulted in this task. No family detail, office dates, or specific military service has been inferred. S. Maria del Giglio, its architect Giuseppe Sardi, Morosini, Rome, the War of Candia, and the Roman epics remain separate endpoints and are not folded into the person identity.

## 关系与证据

7条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register both Antonio Barbaro S3 candidates in one S4 person group.")
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
        and (row.get("name_en") or "").casefold() == "antonio barbaro"
        for row in manifest
    ), "Antonio Barbaro person KU already exists"

    for cid, entry, pages, subentry in [
        ("cand-0184", "B.csv#31", "248, 249, 253", ""),
        ("cand-0185", "B.csv#32", "248, 249", "and S. Maria del Giglio"),
    ]:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["index_entry_id"] == entry
        assert candidate["canonical_name"] == "Barbaro, Antonio"
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

    chapter = (ROOT / CHAPTER).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    required_quotes = (
        "Antonio Barbaro, who had fought in the war of Candia",
        "Rome, where\nAntonio had served as ambassador.",
        "Antonio Barbaro’s conduct in the war of Candia had been somewhat discreditable",
        "the Roman epics with which he had commemorated them",
    )
    normalized_chapter = " ".join(chapter.split())
    for quote in required_quotes:
        assert " ".join(quote.split()) in normalized_chapter, quote
    assert "| Barbaro, Antonio |  |  |  | 248, 249, 253 |" in index_text
    assert "| Barbaro, Antonio |  | and S. Maria del Giglio |  | 248, 249 |" in index_text

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
        "canonical_name": "安东尼奥·巴尔巴罗",
        "name_en": "Antonio Barbaro",
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
        "\n\n<a id=\"s4-antonio-barbaro-person\"></a>\n\n"
        "### S4 person：Antonio Barbaro 两候选同组登记（2026-10-17）\n\n"
        f"`cand-0184`（B.csv#31，pp.248、249、253）与 `cand-0185`（B.csv#32，and S. Maria del Giglio，pp.248、249）"
        f"按 S3 身份组 `{GROUP}` 共同映射至[Antonio Barbaro 人物卡](../../../{CARD_REL})，一组登记一个 KU。"
        "跨页全名、建筑子项与第253页再次出现的姓名支持该书内人物身份；本轮未使用外部身份记录。"
        "第248页记 Haskell 对 façade 设计、Candia 战争和 Rome 大使经历的叙述；第249页的战时评价与 Morosini 相关叙述保留作者归属，"
        "脚注所引材料未独立核读。第253页将 Tiepolo 的 Roman epics 说成纪念 Antonio Barbaro 与 Daniele Dolfin。"
        "7条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。"
        "未新增正式关系或外部字段事实。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Antonio Barbaro 同组两候选登记（2026-10-17）\n\n"
        f"`cand-0184` 与 `cand-0185` 按 S3 组 `{GROUP}` 共同映射至[Antonio Barbaro 人物卡]"
        "(../units/persons/antonio-barbaro.md)。书后索引主项定位第248、249、253页，S. Maria del Giglio 子项定位第248、249页；"
        "第248页同一段给出 Antonio Barbaro 全名与建筑语境，第253页再次以全名提及此人。卡片只记录 Haskell 书内说法，"
        "第249页脚注所引来源未独立核读。7条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Antonio Barbaro dry-run passed: {CANDIDATES} -> {KU_ID}")
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
