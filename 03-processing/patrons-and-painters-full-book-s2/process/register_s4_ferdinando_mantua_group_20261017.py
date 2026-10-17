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

CANDIDATES = ("cand-1523",)
GROUP = "new-person:ferdinando-mantua-of-ff7aabd931"
KU_ID = "units/persons/ferdinando-duke-of-mantua"
CARD_REL = "04-knowledge/units/persons/ferdinando-duke-of-mantua.md"
CHAPTER_1 = "02-sources/02-Markdown/01_CHP-1_sec_ii.md"
CHAPTER_7 = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/M.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp7-p175-i10",
    "st-chp7-p175-i11",
    "st-chp7-p175-i12",
    "st-chp7-p175-i13",
    "st-chp7-p175-i14",
    "st-chp7-p175-i16",
    "st-chp7-p175-i17",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第1章；印刷页14；OCR L81",
            "sentence_summary": (
                "Haskell称1617年曼托瓦公爵写信向 Guido Reni 订画《正义拥抱和平》，"
                "并表示会慷慨酬谢；该句不具名，书后索引将第14页归于 Ferdinando。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 81",
                    "text": (
                        "In 1617, for instance, the Duke of Mantua wrote to Guido Reni asking him for a painting "
                        "of Justice embracing Peace. He gave the measurements, but made no mention of the price "
                        "beyond saying that Guido would be ‘generously rewarded’."
                    ),
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_1,
                "source_span": "line 81; print p. 14",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第7章；印刷页175；OCR L64–65",
            "sentence_summary": (
                "Haskell于1624年称 Marie de Medici 的侄子 Ferdinando 已为曼托瓦公爵，"
                "并叙述他对法国宫廷称谓的关切、与父亲 Vincenzo 的收藏赞助比较及艺术赞助。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 64",
                    "text": (
                        "In 1624, while Rubens and Gentileschi were making use of all their gifts to this effect, "
                        "her nephew Ferdinando, now Duke ofMantua, was worried by similar problems."
                    ),
                },
                {
                    "source_span": "lines 64–65",
                    "text": (
                        "Ferdinando like his father Vincenzo was a fanatical collector and patron who employed many "
                        "of the leading artists in Italy, above all that most sensitive and poetic of painters "
                        "Domenico Fetti."
                    ),
                },
                {
                    "source_span": "line 65",
                    "text": (
                        "He therefore proposed sending ten pictures of Apollo and the Muses which Giovanni Baglione "
                        "had brought with him from Rome a few years earlier."
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER_7,
                "source_span": "lines 64–65; print p. 175",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；M.csv#60；印刷页10、14、175",
            "sentence_summary": "书后索引以 Mantua, Ferdinando, Duke of 为主项，列第10、14、175页。",
            "original_quotes": [
                {
                    "source_span": "index entry M.csv#60",
                    "text": "| Mantua, Ferdinando, Duke of |  |  |  | 10, 14, 175 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry M.csv#60",
            },
        },
    ]
    frontmatter = {
        "title": "费迪南多，曼托瓦公爵（Ferdinando, Duke of Mantua）",
        "name_en": "Ferdinando, Duke of Mantua",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p14 = f"[第1章 p.14](../../../{CHAPTER_1})（L81）"
    p175 = f"[第7章 p.175](../../../{CHAPTER_7})（L64–65）"
    index = f"[书后索引](../../../{INDEX_FILE})（M.csv#60）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记索引主项“Mantua, Ferdinando, Duke of”所指的人物。第7章 p.175 明称 Marie de Medici 的侄子 Ferdinando 于1624年已为曼托瓦公爵；同章叙述其重视法国宫廷对其称谓、与父亲 Vincenzo 同为收藏家及赞助人、雇用多位意大利艺术家，并提出赠送 Baglione 带来的十幅 Apollo 与 Muses 题材画作。第1章 p.14 的索引定位页记载一位曼托瓦公爵于1617年向 Guido Reni 订画；索引将该页与第175页列在同一人物主项下，作为跨章定位依据。索引另列 p.10，但该页当前可读正文没有找到对应的公爵提及，故不以该定位增加人物事实。卡片仅保留 Haskell 的书内称谓和叙述，不推定外部全名、生卒年或更精确的朝代身份。{p14} {p175} {index}

**English:** This card records the person named in the index main entry “Mantua, Ferdinando, Duke of.” Chapter 7, p.175 explicitly calls Ferdinando a nephew of Marie de Medici and says that by 1624 he was Duke of Mantua. The passage recounts his concern with his form of address at the French court, describes him and his father Vincenzo as collectors and patrons, says that he employed leading Italian artists, and reports his proposal to send ten Apollo-and-Muses pictures brought by Baglione. Chapter 1, p.14 describes a Duke of Mantua commissioning a painting from Guido Reni in 1617; the index places that page and p.175 under one person entry, which supplies the cross-chapter locator. The index also lists p.10, but the currently readable text on that page contains no corresponding mention of the duke, so that locator is not used to add a biographical fact. The card preserves Haskell’s names and account without inferring an external full name, dates of life, or a more precise regnal identity. {p14} {p175} {index}

### 身份边界

本卡的识别依据限于索引主项和第7章 p.175 的全名、爵位及亲属语境；第1章 p.14 的匿名爵位与索引交叉定位一致。第175页提及其父 Vincenzo，但该候选的准确统治者身份仍未解决；不将父子候选合并，也不据此扩展父名或家族关系。第175页列出的十幅画仅为发送提议，原文未证实寄出、收到或接受；人物身份卡不登记这些关系。

Identification here is limited to the index main entry and the full name, title, and kinship context on Chapter 7, p.175; the anonymous ducal title on Chapter 1, p.14 aligns through the index. Page 175 names his father Vincenzo, but that candidate’s exact regnal identity remains unresolved; the two person candidates are not merged, and no further family detail is inferred. The ten pictures on p.175 are only a proposal to send; the source does not establish that they were sent, received, or accepted. This person card does not register those relations.

## 关系与证据

7条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Ferdinando Duke of Mantua S3 person identity group in S4.")
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
        and (row.get("name_en") or "").casefold() == "ferdinando, duke of mantua"
        for row in manifest
    ), "Ferdinando Duke of Mantua person KU already exists"

    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "M.csv#60"
    assert candidate["canonical_name"] == "Mantua, Ferdinando, Duke of"
    assert candidate["index_page_range"] == "10, 14, 175"
    assert candidate["suggested_type"] == "person"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert {row["candidate_id"] for row in group_rows} == set(CANDIDATES)

    chapter1 = (ROOT / CHAPTER_1).read_text(encoding="utf-8-sig")
    chapter7 = (ROOT / CHAPTER_7).read_text(encoding="utf-8-sig")
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    for quote in (
        "In 1617, for instance, the Duke of Mantua wrote to Guido Reni asking him for a painting of Justice embracing Peace",
        "her nephew Ferdinando, now Duke ofMantua, was worried by similar problems",
        "Ferdinando like his father Vincenzo was a fanatical collector and patron",
        "He therefore proposed sending ten pictures of",
    ):
        combined = " ".join((chapter1 + " " + chapter7).split())
        assert " ".join(quote.split()) in combined, quote
    assert "| Mantua, Ferdinando, Duke of |  |  |  | 10, 14, 175 |" in index_text

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
        "canonical_name": "费迪南多，曼托瓦公爵",
        "name_en": "Ferdinando, Duke of Mantua",
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
        "\n\n<a id=\"s4-ferdinando-duke-mantua-person\"></a>\n\n"
        "### S4 person：Ferdinando, Duke of Mantua 跨章索引身份组登记（2026-10-17）\n\n"
        f"`cand-1523`（M.csv#60，pp.10、14、175）保持 S3 组 `{GROUP}`，映射至[Ferdinando, Duke of Mantua 人物卡]"
        f"(../../../{CARD_REL})。第7章 p.175 明称其为 Marie de Medici 之侄 Ferdinando，并称其于1624年为曼托瓦公爵；"
        "第1章 p.14 记1617年一位曼托瓦公爵向 Guido Reni 订画，索引将两页归入同一主项。索引另列的 p.10 当前正文未找到对应公爵提及，"
        "保留为未核实定位，不据其扩充身份。父亲 Vincenzo 的统治者身份未解决。"
        "7条直接 relation_candidate 原样保留待 S6：" + ", ".join(sorted(RELATION_CANDIDATES)) + "。"
        "未新增正式关系或外部身份记录。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Ferdinando, Duke of Mantua 跨章身份组登记（2026-10-17）\n\n"
        f"`cand-1523`（M.csv#60）映射至[Ferdinando, Duke of Mantua 人物卡]"
        "(../units/persons/ferdinando-duke-of-mantua.md)。第7章 p.175 的全名、亲属语境和1624年爵位与书后索引主项相合；"
        "第1章 p.14 的曼托瓦公爵订画记录依索引归入同一条目。p.10 索引定位未在现有正文转录中找到明确对应，不作身份依据。"
        "父亲 Vincenzo 的确切身份及7条关系候选留待后续阶段，未新增正式关系。"
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
        print(f"S4 Ferdinando Duke of Mantua dry-run passed: {CANDIDATES} -> {KU_ID}")
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
