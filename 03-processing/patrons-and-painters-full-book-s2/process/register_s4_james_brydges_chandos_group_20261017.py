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

CANDIDATES = ("cand-0647",)
GROUP = "new-person:1st-brydges-chandos-james-of-46f0373d10"
KU_ID = "units/persons/james-brydges-first-duke-of-chandos"
CARD_REL = "04-knowledge/units/persons/james-brydges-first-duke-of-chandos.md"
CHAPTER = "02-sources/02-Markdown/10_CHP-10_intro.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/C.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp10-p281-bellucci-chandos-chapel-team",
    "st-chp10-p281-brydges-acquired-canons",
    "st-chp10-p281-brydges-bellucci-patron",
    "st-chp10-p281-brydges-canons-concerts",
    "st-chp10-p281-brydges-created-duke",
    "st-chp10-p281-brydges-paymaster-service",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第10章；印刷页281；OCR L128–132",
            "sentence_summary": (
                "Haskell称 James Brydges 是 Bellucci 最重要的英国赞助人，1719年成为第一代 Chandos 公爵；"
                "并记其军需总监经历、1713年购置 Canons、在府邸举办音乐会及雇用 Bellucci 等人装饰礼拜堂。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 128",
                    "text": (
                        "Bellucci’s most important English patron was James Brydges, who managed to get himself "
                        "created first Duke of Chandos in 1719 at the age of 46."
                    ),
                },
                {
                    "source_span": "lines 128–129",
                    "text": (
                        "Though born in poverty he acquired an immense fortune from war profiteering after having "
                        "served for eight years as Paymaster to the Forces. In 1713 he acquired the old Elizabethan "
                        "manor of Canons at Edgware"
                    ),
                },
                {
                    "source_span": "lines 129–132",
                    "text": (
                        "he entertained his friends with magnificent concerts organised by Handel and Dr Pepusch. "
                        "He had a number of ceilings in the state rooms both at Canons and in his London house "
                        "painted with allegorical subjects by Bellucci and, above all, he employed this artist "
                        "together with the Bolognese stuccatore Bagutti and a mysterious figure called Francesco Sleter "
                        "to decorate the chapel."
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "lines 128–132; print p. 281",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；C.csv#171；印刷页281",
            "sentence_summary": "书后索引以 Chandos, James Brydges, 1st Duke of 为主项，定位第281页。",
            "original_quotes": [
                {
                    "source_span": "index entry C.csv#171",
                    "text": "| Chandos, James Brydges, 1st Duke of |  |  |  | 281 |",
                }
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry C.csv#171",
            },
        },
    ]
    frontmatter = {
        "title": "詹姆斯·布里奇斯，第一代钱多斯公爵（James Brydges, 1st Duke of Chandos）",
        "name_en": "James Brydges, 1st Duke of Chandos",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    page = f"[第10章 p.281](../../../{CHAPTER})（L128–132）"
    index = f"[书后索引](../../../{INDEX_FILE})（C.csv#171）"
    body = f"""## 内容

### 描述

**中文：** 本卡登记书后索引 C.csv#171“Chandos, James Brydges, 1st Duke of”及第10章 p.281 全名所指的人物。Haskell称 Brydges 为 Bellucci 最重要的英国赞助人，记其1719年成为第一代 Chandos 公爵、曾任 Paymaster to the Forces 八年、1713年购置 Canons 府邸，并在府邸举办由 Handel 与 Dr Pepusch 组织的音乐会；还称他与 Bagutti、Francesco Sleter 一同雇用 Bellucci 等人装饰礼拜堂。关于其财富来源及“最重要赞助人”的判断保留为 Haskell 的表述。本卡据此建立人物身份，不把任职、委托、建筑或音乐会写成正式关系。{page} {index}

**English:** This card records the person named in index entry C.csv#171, “Chandos, James Brydges, 1st Duke of,” and by full name on Chapter 10, p.281. Haskell calls Brydges Bellucci’s most important English patron, says that he became the first Duke of Chandos in 1719, served eight years as Paymaster to the Forces, acquired Canons in 1713, and entertained friends there at concerts organized by Handel and Dr Pepusch. Haskell also says that he employed Bellucci with Bagutti and Francesco Sleter to decorate the chapel. The account of his fortune and the assessment “most important patron” remain attributed to Haskell. This card registers the person and does not turn offices, commissions, the house, or concerts into formal relations. {page} {index}

### 身份边界

本卡对应人物 James Brydges；“第一代 Chandos 公爵”是其书内头衔，不另建为人物。Canons、伦敦住宅、Bellucci、Bagutti、Francesco Sleter、Handel 与 Dr Pepusch 均为独立对象。原书称军需总监任职八年但未列确切起止日期；不据此补外部生平或验证头衔授予程序。

This card refers to James Brydges as a person; “first Duke of Chandos” is his title in the book and is not a separate person. Canons, the London house, Bellucci, Bagutti, Francesco Sleter, Handel, and Dr Pepusch remain distinct objects. Haskell gives an eight-year Paymaster tenure without exact dates; no external biography or title-grant procedure is added.

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register James Brydges's S3 person identity group in S4.")
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
        and (row.get("name_en") or "").casefold() == "james brydges, 1st duke of chandos"
        for row in manifest
    ), "James Brydges person KU already exists"
    candidate = candidate_by_id[CANDIDATES[0]]
    alignment = alignment_by_id[CANDIDATES[0]]
    assert candidate["index_entry_id"] == "C.csv#171"
    assert candidate["canonical_name"] == "Chandos, James Brydges, 1st Duke of"
    assert candidate["index_page_range"] == "281"
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
        "Bellucci’s most important English patron was James Brydges",
        "created first Duke of Chandos in 1719 at the age of 46",
        "In 1713 he acquired the old Elizabethan manor of Canons at Edgware",
        "he employed this artist together with the Bolognese stuccatore Bagutti",
    ):
        assert " ".join(quote.split()) in normalized, quote
    assert "| Chandos, James Brydges, 1st Duke of |  |  |  | 281 |" in index_text

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
        "canonical_name": "詹姆斯·布里奇斯，第一代钱多斯公爵",
        "name_en": "James Brydges, 1st Duke of Chandos",
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
        "\n\n<a id=\"s4-james-brydges-chandos-person\"></a>\n\n"
        "### S4 person：James Brydges，第一代 Chandos 公爵身份组登记（2026-10-17）\n\n"
        f"`cand-0647`（C.csv#171，p.281）保持 S3 组 `{GROUP}`，映射至[James Brydges 人物卡](../../../{CARD_REL})。"
        "索引头衔与第10章正文全名、爵位相合。p.281 记其 Paymaster 任职、1713年取得 Canons、1719年成为 Chandos 公爵、赞助 Bellucci 及主持音乐会；"
        "财富来源和“最重要英国赞助人”作为 Haskell 的说法保留。六条直接 relation_candidate 原样保留待 S6："
        + ", ".join(sorted(RELATION_CANDIDATES)) + "。本轮未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：James Brydges，第一代 Chandos 公爵身份组登记（2026-10-17）\n\n"
        f"`cand-0647`（C.csv#171）映射至[James Brydges 人物卡](../units/persons/james-brydges-first-duke-of-chandos.md)。"
        "第10章 p.281 的全名、爵位与索引主项对应；卡片将第一代 Chandos 公爵作为人物头衔而非另一个实体。"
        "六条直接关系候选仍待 S6，未新增正式关系。"
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
        print(f"S4 James Brydges dry-run passed: {CANDIDATES} -> {KU_ID}")
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
