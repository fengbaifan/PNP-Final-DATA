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

CANDIDATES = ("cand-0249", "cand-5530")
GROUP = "new-person:baroni-leonora-970b86fc4c"
KU_ID = "units/persons/leonora-baroni"
CARD_REL = "04-knowledge/units/persons/leonora-baroni.md"
CHAPTER_4 = "02-sources/02-Markdown/04_CHP-4_sec_i.md"
CHAPTER_7 = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/B.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp4-sec-i-l20-24-collection-honours-baroni",
    "st-chp4-sec-i-l20-24-milton-captivated-by-baroni",
    "st-chp4-sec-i-l42-67-fn96-baroni-publication",
    "st-chp7-p180-i21",
    "st-chp7-p180-i22",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第4章；印刷页96（索引定位；OCR页标作[Page 9]）；OCR L22",
            "sentence_summary": (
                "Haskell称 Paolo Giordano 负责出版赞颂 Leonora Baroni 的诗歌，并称她是歌声使 Milton 着迷的歌手；"
                "相邻注释列出一部1639年 Bracciano 出版物。被引诗集未独立核读。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 22",
                    "text": (
                        "he was responsible for publishing the poems written by a number of admirers in honour of "
                        "Leonora Baroni, the singer who so captivated Milton"
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_4,
                "source_span": "line 22; index print-page locator 96; OCR page marker truncated",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章；印刷页180–181；OCR L136、145",
            "sentence_summary": (
                "Haskell称 Mazarin 选择歌手 Leonora Baroni 为情妇，称她的成功开创了歌剧明星传统；"
                "第181页又称 Mazarin 早期未能将其带到巴黎，并称她为 former mistress。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 136",
                    "text": (
                        "he chose as his mistress Leonora Baroni, the singer whose fabulous success inaugurated "
                        "the long and frenzied tradition of operatic ‘stardom’"
                    ),
                },
                {
                    "source_span": "line 145",
                    "text": "he was at first not even able to bring to Paris some of the best Italian musicians, including his former mistress Leonora Baroni",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_7,
                "source_span": "lines 136, 145; print pp. 180–181",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；B.csv#96；印刷页96、180、181",
            "sentence_summary": "书后索引以 Baroni, Leonora 为主项，定位第96、180、181页。",
            "original_quotes": [
                {
                    "source_span": "index entry B.csv#96",
                    "text": "| Baroni, Leonora |  |  |  | 96, 180, 181 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry B.csv#96",
            },
        },
    ]
    frontmatter = {
        "title": "莱奥诺拉·巴罗尼（Leonora Baroni）",
        "name_en": "Leonora Baroni",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p96 = f"[第4章 p.96](../../../{CHAPTER_4})（L22；OCR页标作“[Page 9]”，索引列p.96）"
    p180 = f"[第7章 p.180](../../../{CHAPTER_7})（L136）"
    p181 = f"[第7章 p.181](../../../{CHAPTER_7})（L145）"
    index = f"[书后索引](../../../{INDEX_FILE})（B.csv#96）"
    body = f"""## 内容

### 描述

**中文：** 本卡将索引主项“Baroni, Leonora”与第4章正文候选“Leonora Baroni”合为同一跨章书内人物组。第4章称她为歌手，并记 Paolo Giordano 负责出版仰慕者为她所作的诗；注释列出一部1639年 Bracciano 出版物，但该诗集未独立查阅。第7章 p.180 称 Mazarin 选择歌手 Leonora Baroni 为情妇，并以其成功说明歌剧明星传统的形成；p.181 又称 Mazarin 早期未能把她带到巴黎，称她为其 former mistress。婚恋叙述与成功评价均保留为 Haskell 的书内表述，不作外部核实或扩大。本卡不将诗集、Milton、Paolo Giordano 或 Mazarin 写成正式关系。{p96} {p180} {p181} {index}

**English:** This card groups the index main entry “Baroni, Leonora” with the Chapter 4 body candidate “Leonora Baroni” as one cross-chapter person in the book. Chapter 4 calls her a singer and says Paolo Giordano arranged publication of poems written by admirers in her honour. Its note lists a 1639 publication at Bracciano, but the poetry collection was not independently consulted. Chapter 7, p.180 says that Mazarin chose the singer Leonora Baroni as his mistress and uses her success in discussing the rise of operatic stardom; p.181 says that Mazarin initially failed to bring her to Paris and calls her his former mistress. The relationship account and assessment of her success remain Haskell’s statements in the book and are not independently verified or expanded. This card does not register the collection, Milton, Paolo Giordano, or Mazarin as formal relations. {p96} {p180} {p181} {index}

### 身份边界

跨章身份依据为相同全名、歌手描述及索引页码 96、180、181。第4章 OCR 页标显示“[Page 9]”，第5章来源紧接其后标为第97页；书后索引将该歌手所在段落定位为第96页。本卡保留此 OCR 页标缺位，不据此改动来源原文。脚注提及的诗集及生平来源未独立核读；不补充出生、死亡或训练经历。

Cross-chapter identity rests on the same full name, the singer description, and index locations 96, 180, and 181. The Chapter 4 OCR page marker reads “[Page 9]”; the following source page is marked 97, while the book index locates the singer passage on page 96. This card preserves the missing OCR digit rather than altering the source text. The cited poetry collection and biographical sources have not been independently consulted; no birth, death, or training details are added.

## 关系与证据

5条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Leonora Baroni cross-chapter S3 person group in S4.")
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
        and (row.get("name_en") or "").casefold() == "leonora baroni"
        for row in manifest
    ), "Leonora Baroni person KU already exists"

    expected = {
        "cand-0249": ("B.csv#96", "Baroni, Leonora", "96, 180, 181", ""),
        "cand-5530": ("", "Leonora Baroni", "", "body-mention"),
    }
    for cid in CANDIDATES:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        entry, name, pages, origin = expected[cid]
        assert candidate["index_entry_id"] == entry
        assert candidate["canonical_name"] == name
        assert candidate["index_page_range"] == pages
        assert candidate.get("candidate_origin", "") == origin
        assert candidate["suggested_type"] == "person"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    ch4 = (ROOT / CHAPTER_4).read_text(encoding="utf-8-sig")
    ch7 = (ROOT / CHAPTER_7).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    for quote in (
        "Leonora Baroni, the singer who so captivated Milton",
        "he was responsible for publishing the poems written by a number of admirers in honour of",
    ):
        assert " ".join(quote.split()) in " ".join(ch4.split()), quote
    for quote in (
        "he chose as his mistress Leonora Baroni, the singer whose fabulous success",
        "including his former mistress Leonora Baroni",
    ):
        assert " ".join(quote.split()) in " ".join(ch7.split()), quote
    assert "| Baroni, Leonora |  |  |  | 96, 180, 181 |" in index_text

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
        "canonical_name": "莱奥诺拉·巴罗尼",
        "name_en": "Leonora Baroni",
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
        "\n\n<a id=\"s4-leonora-baroni-person\"></a>\n\n"
        "### S4 person：Leonora Baroni 跨章同名候选组登记（2026-10-17）\n\n"
        f"`cand-0249`（B.csv#96，pp.96、180、181）与 `cand-5530`（第4章 p.96 正文候选）按 S3 组 `{GROUP}` "
        f"共同映射至[Leonora Baroni 人物卡](../../../{CARD_REL})。索引名与正文全名一致；第4章称她为歌手并提及为其所作的赞颂诗，"
        "第7章两页均以同一全名叙述她与 Mazarin 的关系。第4章 OCR 页标作[Page 9]，但索引定位p.96且下页标为p.97；该缺位原样记录。"
        "恋爱关系和歌剧明星评价保持 Haskell 归属。五条直接 relation_candidate 原样保留待 S6："
        + ", ".join(sorted(RELATION_CANDIDATES)) + "。未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Leonora Baroni 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-0249` 与 `cand-5530` 按 S3 组 `{GROUP}` 共同映射至[Leonora Baroni 人物卡]"
        "(../units/persons/leonora-baroni.md)。第4章歌手及赞颂诗叙述、第7章 p.180–181 重复全名和索引页码96、180、181相合。"
        "第4章 OCR 页标缺一位，暂按索引定位记录为p.96；婚恋与成功评价仍属 Haskell 的书内说法。五条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 Leonora Baroni dry-run passed: {CANDIDATES} -> {KU_ID}")
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
