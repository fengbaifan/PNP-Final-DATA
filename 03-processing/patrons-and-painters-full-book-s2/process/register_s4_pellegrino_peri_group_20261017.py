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

CANDIDATES = ("cand-1878", "cand-6081")
GROUP = "new-person:pellegrino-peri-0180e88b93"
KU_ID = "units/persons/pellegrino-peri"
CARD_REL = "04-knowledge/units/persons/pellegrino-peri.md"
CHAPTER = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
INDEX_FILE = "02-sources/03-Index/03-1-Index-MD/P.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
RELATION_CANDIDATES = {
    "st-chp5-p122-peri-gaulli",
    "st-chp5-p122-peri-residence-near-pasquino",
    "st-chp5-p122-carlone-debt",
    "st-chp5-note-p122-n1-carlone-attack",
    "st-chp5-note-p122-n1-carlone-loan",
    "st-chp5-note-p122-n1-peri-theft",
}


def make_card() -> str:
    sources = [
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页122；OCR L18",
            "sentence_summary": (
                "Haskell称 Pellegrino Peri 在17世纪后半叶住在 Pasquino 雕像附近，"
                "并在年轻 Gaulli 到 Rome 时雇用了他；同句称 Gian Andrea Carlone 欠 Peri 债务且拒绝偿还。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 18",
                    "text": (
                        "one Pellegrino Peri who lived near the statue of Pasquino during the second half of the "
                        "seventeenth century and who employed the young Gaulli on his arrival in Rome"
                    ),
                },
                {
                    "source_span": "line 18",
                    "text": "Gian Andrea Carlone who refused to pay back a debt he owed him",
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "line 18; print p. 122",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "第5章；印刷页122注1；OCR L132",
            "sentence_summary": (
                "第122页注1称 Peri 与 Gaulli 的往来可参 Pascoli；并转述1666年 Carlone 袭击 Peri、拒还借款，"
                "以及1681年 Peri 报告其店中两幅画被盗。该注引用的 Pascoli 与 Bertolotti 未独立核读。"
            ),
            "original_quotes": [
                {
                    "source_span": "line 132",
                    "text": (
                        "For Pellegrino Peri and his dealings with Gaulli see Pascoli, I, p. 198. In 1666 he was "
                        "attacked by Giovanni Andrea Carlone, who refused to pay him back a loan."
                    ),
                },
                {
                    "source_span": "line 132",
                    "text": (
                        "In 1681 he denounced the robbery of two pictures by Filippo Lauri and Giovanni Perusini "
                        "which had been stolen from his shop"
                    ),
                },
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHAPTER,
                "source_span": "line 132; print p. 122 note 1",
            },
        },
        {
            "citation": BOOK_CITATION,
            "location": "书后索引；P.csv#79；印刷页122",
            "sentence_summary": "书后索引以 Peri, Pellegrino 为主项，定位第122页。",
            "original_quotes": [
                {"source_span": "index entry P.csv#79", "text": "| Peri, Pellegrino |  |  |  | 122 |"},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": INDEX_FILE,
                "source_span": "index entry P.csv#79",
            },
        },
    ]
    frontmatter = {
        "title": "佩莱格里诺·佩里（Pellegrino Peri）",
        "name_en": "Pellegrino Peri",
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-17",
        "updated": "2026-10-17",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p122 = f"[第5章 p.122](../../../{CHAPTER})（L18）"
    n122 = f"[第5章 p.122 注1](../../../{CHAPTER})（L132）"
    index = f"[书后索引](../../../{INDEX_FILE})（P.csv#79）"
    body = f"""## 内容

### 描述

**中文：** 本卡合并索引候选“Peri, Pellegrino”与第122页注1中的正文候选“Pellegrino Peri”；同名主项与书内全名一致，按 S3 身份组登记为一个书内人物。第122页称他在17世纪后半叶住在 Pasquino 雕像附近，并在年轻 Gaulli 初到 Rome 时雇用了他；同句称 Gian Andrea Carlone 欠 Peri 债务且拒绝偿还。第122页注1进一步转述1666年 Carlone 袭击 Peri，以及1681年 Peri 报告其店内两幅画被盗。后两项是 Haskell 对 Pascoli、Bertolotti 的引述；被引材料未独立核读，因此本卡只记录作者报告，不将其写成独立核实的生平事实。{p122} {n122} {index}

**English:** This card groups the index candidate “Peri, Pellegrino” with the body candidate “Pellegrino Peri” in note 1 on page 122. The index form and the full name in the book match, so the S3 identity group is registered as one book-local person. Page 122 says that he lived near the statue of Pasquino in the second half of the seventeenth century and employed the young Gaulli on his arrival in Rome; the same sentence says that Gian Andrea Carlone owed Peri a debt and refused to repay it. Note 1 on page 122 further reports that Carlone attacked Peri in 1666 and that Peri reported the theft of two pictures from his shop in 1681. These latter claims are Haskell’s reports citing Pascoli and Bertolotti; those cited works were not independently consulted, so this card records the author’s account rather than independently verified biographical facts. {p122} {n122} {index}

### 身份边界

本卡仅对应 Haskell 与索引具名的 Pellegrino Peri。正文称他居住在 Pasquino 雕像附近并雇用 Gaulli；注释所述袭击、借款与失窃信息均经由作者转引，未核读原始研究。两幅被盗画作未具标题，也未逐幅对应两位画家；不扩张其作品清单或身份资料。

This card refers only to the Pellegrino Peri named by Haskell and the index. The text says that he lived near the statue of Pasquino and employed Gaulli; the attack, loan, and theft details in the note are author-reported citations whose sources were not consulted. The two stolen pictures are untitled and are not mapped one-to-one to the two artists; no catalogue or further identity details are inferred.

## 关系与证据

6条直接 S2 `relation_candidate` 保留待 S6：{', '.join(sorted(RELATION_CANDIDATES))}。本轮未登记正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Pellegrino Peri S3 person identity group in S4.")
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
        and (row.get("name_en") or "").casefold() == "pellegrino peri"
        for row in manifest
    ), "Pellegrino Peri person KU already exists"

    expected = {
        "cand-1878": ("P.csv#79", "Peri, Pellegrino", "122", ""),
        "cand-6081": ("", "Pellegrino Peri", "", "body-mention"),
    }
    for cid in CANDIDATES:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        entry, name, pages, origin = expected[cid]
        assert candidate["index_entry_id"] == entry
        assert candidate["canonical_name"] == name
        assert candidate["index_page_range"] == pages
        assert candidate["candidate_origin"] == origin
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
        "one Pellegrino Peri who lived near the statue of Pasquino during the second half of the seventeenth century",
        "who employed the young Gaulli on his arrival in Rome",
        "Gian Andrea Carlone who refused to pay back a debt he owed him",
        "In 1666 he was attacked by Giovanni Andrea Carlone",
        "In 1681 he denounced the robbery of two pictures by Filippo Lauri and Giovanni Perusini",
    ):
        assert " ".join(quote.split()) in normalized, quote
    assert "| Peri, Pellegrino |  |  |  | 122 |" in index_text

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
        "canonical_name": "佩莱格里诺·佩里",
        "name_en": "Pellegrino Peri",
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
        "\n\n<a id=\"s4-pellegrino-peri-person\"></a>\n\n"
        "### S4 person：Pellegrino Peri 索引与正文候选同组登记（2026-10-17）\n\n"
        f"`cand-1878`（P.csv#79，p.122）与 `cand-6081`（第5章 p.122 注1正文候选）按 S3 组 `{GROUP}` "
        f"共同映射至[Pellegrino Peri 人物卡](../../../{CARD_REL})。索引反序形式、正文全名及同页脚注全名相符；一组只登记一个 KU。"
        "Haskell第122页称 Peri 住在 Pasquino 附近并雇用初到 Rome 的 Gaulli；正文另称 Carlone 欠款拒还。注1转述1666年袭击和1681年失窃报告，"
        "引述 Pascoli 与 Bertolotti，但被引文献未独立核读。六条直接 relation_candidate 原样保留待 S6："
        + ", ".join(sorted(RELATION_CANDIDATES)) + "。本轮未新增正式关系。"
        f"S4 累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text += (
        "\n\n### S4 person：Pellegrino Peri 同组登记（2026-10-17）\n\n"
        f"`cand-1878` 与 `cand-6081` 按 S3 组 `{GROUP}` 共同映射至[Pellegrino Peri 人物卡]"
        "(../units/persons/pellegrino-peri.md)。索引主项与第5章 p.122 的全名及脚注同名锚点吻合。"
        "有关居所、Gaulli 雇用及 Carlone 债务为 Haskell 正文说法；注1中的1666年袭击与1681年失窃报告转引 Pascoli、Bertolotti，未独立核读。"
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
        print(f"S4 Pellegrino Peri dry-run passed: {CANDIDATES} -> {KU_ID}")
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
