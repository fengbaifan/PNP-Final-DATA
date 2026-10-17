from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_archive_memmo_query_sheet_20261017 as previous


sync = previous.sync
ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "archive-group-dactylografia-smithiana"
MEMBERS = ("cand-1848", "cand-2458")
KU_ID = "units/archives/dactylografa-smithiana"
CARD_REL = "04-knowledge/units/archives/dactylografa-smithiana.md"
NAME_ZH = "约瑟夫·史密斯奖章与宝石图册"
NAME_EN = "Dactylografa Smithiana"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
PASSAGE_QUOTE = (
    "It was naturally Pasquali who published the fine illustrated books which recorded some of the treasures in Smith’s collection— "
    "his paintings by Cignani and Ricci in 1749, and eighteen years later the Dactylografa\n"
    "Smithiana. This contained 100 plates engraved by Brustolon, mostly in a severely neoclassical style, "
    "illustrating Smith’s medals and gems, and it was clearly influenced by\n"
    "Albrizzi’s publication a few years earlier of the gems in A. M. Zanetti’s collection. "
    "But the general presentation is far simpler with none of the rich and elaborate decoration of that book, "
    "and the text—printed in Latin only—is aimed at a more scholarly public."
)
RELATION_IDS = (
    "st-chp13-p337-dactylografa-contained-100-brustolon-plates",
    "st-chp13-p337-dactylografa-illustrated-smith-medals-gems",
    "st-chp13-p337-dactylografa-influenced-by-albrizzi-zanetti-publication",
    "st-chp13-p337-dactylografa-latin-only-scholarly-audience",
    "st-chp13-p337-dactylografa-simpler-presentation-than-albrizzi-book",
    "st-chp13-p337-pasquali-published-dactylografa-smithiana",
)
DIRECT_STATEMENT_IDS = RELATION_IDS + ("st-chp13-p337-dactylografa-neoclassical-style",)
PROCESS_ANCHOR = "s4-dactylografa-smithiana-20261017"


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def source_rows():
    return [{
        "citation": BOOK_CITATION,
        "location": "第13章导言，印刷页337；Markdown 行53–55。该书未独立查阅。",
        "sentence_summary": (
            "Haskell 将 Dactylografa Smithiana 记为 Pasquali 在1749年相关图书之后十八年出版的插图书，"
            "称其中有 Brustolon 刻制的100幅图版，表现 Smith 的奖章与宝石，并说明文本仅用拉丁语、"
            "面向较学术的读者；题名拼写与索引有异，版年未据相对时间折算。"
        ),
        "original_quotes": [{"source_span": "lines 53–55; print p. 337", "text": PASSAGE_QUOTE}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/13_CHP-13_intro.md",
            "source_span": "lines 53–55; print p. 337",
        },
    }]


def card_text():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "illustrated book",
        "evidence_status": "source_backed",
        "sources": source_rows(),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    source_link = "../../../02-sources/02-Markdown/13_CHP-13_intro.md"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡登记哈斯克尔第13章 p.337 所述的 *Dactylografa Smithiana* 插图书。哈斯克尔称，Pasquali 在1749年出版的相关插图书之后十八年出版此书；书中有 Brustolon 刻制的100幅图版，表现 Joseph Smith 的奖章与宝石。哈斯克尔称图版大多呈严谨的新古典主义风格，并认为此书明显受到 Albrizzi 早先刊行 A. M. Zanetti 藏宝石图版的影响；书的编排较简，正文仅用拉丁语，面向较学术的读者。以上均为哈斯克尔对该书的叙述，本书未独立查阅。[第13章 p. 337]({source_link})（L53–55）

**English:** This card records the illustrated book *Dactylografa Smithiana* described in Chapter 13, p. 337. Haskell says Pasquali published it eighteen years after the illustrated books he had produced in 1749; it contained 100 plates engraved by Brustolon, depicting Joseph Smith’s medals and gems. Haskell describes most plates as severely Neoclassical and says the book was clearly influenced by Albrizzi’s earlier publication of gems in A. M. Zanetti’s collection. He describes its presentation as simpler and its Latin-only text as aimed at a more scholarly public. These are Haskell’s statements about the book; the publication itself was not consulted in this pass.

### 文献属性与范围

- **题名形式：** 正文拼作 *Dactylografa Smithiana*；索引在 Pasquali 与 Smith 两个主项下均作 *Dactylografia Smithiana*。本轮保留正文与索引异文，未核对题名页或外部目录；中文展示名为便于识别的描述性工作题名。
- **文献类型：** 插图书；来源称其正文仅用拉丁语。版次、出版地、出版者地址及实物馆藏未独立核验。
- **出版时间表述：** Haskell 以“1749年之后十八年”叙述其出版顺序。本卡保留相对时间，不换算成确定年份。
- **内容范围：** 100幅图版据称表现 Smith 的奖章与宝石。此数量与内容均按 Haskell 的概述保存，不视为对全书或全部藏品的完整编目。
- **相关书目：** Haskell 将本书与[1749年《Dactyliotheca Ant. M. Zanetti》](dactyliotheca-ant-m-zanetti-1749.md)作影响与编排比较；两书为不同 archive。比较表述不在本轮登记为正式关系。

### 身份边界

S3 身份组 archive-group-dactylografia-smithiana 包含 cand-1848（P.csv#48）与 cand-2458（S.csv#147），两条索引均把子目 Dactylografia Smithiana 指向第337页所述文本，故共同映射至本卡。该书与 Smith 的藏品、1749年 Zanetti 图录、Pasquali 的其他出版物分别处理；正文题名与索引异文不拆为两个版本或对象。

## 关系与证据

当前未登记正式关系。直接 S2 关系候选 {", ".join(RELATION_IDS)} 均留待 S6 核对端点、方向、语境与证据。有关版画风格的 statement 另作为来源限定的描述保留，不因此增加正式关系或独立核验状态。
"""


def normalized(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Dactylografa Smithiana in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decision_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    group_members = {
        cid for cid, row in decision_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    for cid in MEMBERS:
        assert candidate_by_id[cid].get("suggested_type") == "archive"
        assert decision_by_id[cid].get("decision") == "new" and not decision_by_id[cid].get("ku_id")

    card_path = ROOT / CARD_REL
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "archive"
        and any(
            phrase in " ".join(row.values()).casefold()
            for phrase in ("dactylografa smithiana", "dactylografia smithiana")
        )
        for row in manifest
    )

    source_path = ROOT / "02-sources/02-Markdown/13_CHP-13_intro.md"
    source_text = source_path.read_text(encoding="utf-8-sig")
    assert normalized(PASSAGE_QUOTE) in normalized(source_text), "source quote changed"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relations = [
        row for row in direct
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert {row["statement_id"] for row in direct} == set(DIRECT_STATEMENT_IDS)
    assert {row["statement_id"] for row in relations} == set(RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = card_text()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated archive card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    next_process = previous.refresh_process_type_table(process_text, stats)
    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S4 archive：Dactylografa Smithiana 插图书登记（{DATE}）\n\n"
        f"- cand-1848 与 cand-2458 保持同一 S3 new 身份组 {GROUP}，共同映射至"
        f"[{NAME_ZH}](../../../{CARD_REL})（{KU_ID}）。正文题名为 Dactylografa Smithiana，"
        "两条索引子目写作 Dactylografia Smithiana；异文并存，不据此拆分对象。\n"
        "- Haskell 称此书在1749年相关插图书之后十八年出版，含 Brustolon 刻制的100幅版画，"
        "表现 Joseph Smith 的奖章与宝石；仅用拉丁语，面向较学术的读者。版年不从相对时间换算，"
        "本书及题名页未查阅。与既有1749年 Zanetti 图录分开。\n"
        f"- 共{len(direct)}条直接 S2 陈述，其中{len(relations)}条关系候选"
        f"（{', '.join(RELATION_IDS)}）全部留待 S6；本批未新增正式关系、外部身份验证或 S5 enrichment。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = next_process.rstrip() + process_append + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
            f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; "
        f"direct_statements={len(direct)}; relation_candidates_pending={len(relations)}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
