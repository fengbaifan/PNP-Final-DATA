from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-16"

CANDIDATE = "cand-1752"
GROUP = "new-person:de-dominique-non-denon-dominique-vivant-d852c29287"
KU_ID = "units/persons/dominique-de-non-vivant-denon"
CARD_REL = "04-knowledge/units/persons/dominique-de-non-vivant-denon.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "多米尼克·德农"
NAME_EN = "Dominique De Non (Dominique Vivant-Denon)"
SOURCE_FILE = "02-sources/02-Markdown/15_CHP-15_sec_ii.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/N.csv"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-dominique-de-non-20261016"

TEXT_QUOTES = (
    (
        "lines 77–78",
        "Apart from sculptors the only artist with whom he had close contacts'was Dominique De Non, "
        "who later (as Dominique Vivant-Denon) became Napoleon’s celebrated director of museums.2 "
        "De Non settled in Venice for about five years in the early ’nineties, and led a busy life as a controversial but highly admired engraver and also as a collector.",
    ),
    (
        "lines 78–81",
        "He bought a large proportion of Zanetti’s prints, including the Rembrandts, which had a profound effect on his own style and that of his principal pupil Francesco Novelli. "
        "At Ferney he had engraved a portrait of Voltaire and in Naples he had worked on the\n"
        "Abbé de Saint-Non’s Voyage Pittoresque de la Grèce et de la Sicile, and he.was thus well qualified through his political and antiquarian interests to appeal to Querini. "
        "He moved a great deal in his circle and drew his portrait (which he signed ‘amico suavissimo’) and\n"
        "- also that of Mme Rosenberg among her friends.",
    ),
)
INDEX_QUOTE = "Non, Dominique De (Dominique Vivant-Denon)"


def source_row(location: str, summary: str, quotes: list[tuple[str, str]], source_file: str, span: str):
    return {
        "citation": BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [
            {"source_span": source_span, "text": quote}
            for source_span, quote in quotes
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": source_file,
            "source_span": span,
        },
    }


def make_card() -> str:
    sources = [
        source_row(
            "第15章，印刷页371；OCR L77–81",
            "Haskell 先以 Dominique De Non 称呼此人，并在同句明确说明其后来以 Dominique Vivant-Denon 为名；后续段落叙述其威尼斯居留、版画家与收藏者身份及与 Querini、Mme Rosenberg 的交往。",
            list(TEXT_QUOTES),
            SOURCE_FILE,
            "lines 77–81; print p. 371; PDF physical p. 8",
        ),
        source_row(
            "全书索引，N.csv#32；索引页371",
            "索引将 Dominique De Non 与 Dominique Vivant-Denon 并列为同一人物的名称形式。",
            [("N.csv#32", INDEX_QUOTE)],
            INDEX_FILE,
            "N.csv#32; indexed page 371",
        ),
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p371 = "[第15章 p.371](../../../02-sources/02-Markdown/15_CHP-15_sec_ii.md)（L77–81）"
    index = "[全书索引 N.csv#32](../../../02-sources/03-Index/03-2-Index-CSV/N.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 第15章 p.371 先称此人为 Dominique De Non，随即明确说他后来以 Dominique Vivant-Denon 为名。Haskell 将其描述为版画家和收藏者，并叙述其在 Venice 居留约五年、在 Ferney 刻制 Voltaire 肖像，以及参与 Abbé de Saint-Non 的旅行画册。本卡把这两个书内名称形式登记为同一人物，不补入出生名、生卒或其他外部传记。{p371} {index}

**English:** On p. 371 of Chapter 15, Haskell first names the person Dominique De Non and immediately states that he later became known as Dominique Vivant-Denon. Haskell describes him as an engraver and collector and recounts his roughly five-year stay in Venice, an engraving of Voltaire made at Ferney, and work on Abbé de Saint-Non’s travel book. This card records the two forms used in the book as one person and adds no birth name, life dates, or external biography. {p371} {index}

### 名称与书内身份

- **书内名称形式：** Dominique De Non；同段后文明确括注其后来名称为 Dominique Vivant-Denon。中文显示名“多米尼克·德农”为项目工作译名。{p371}
- **索引形式：** N.csv#32 将 “Non, Dominique De” 与 “Dominique Vivant-Denon” 并列；另一个索引交叉引用候选 cand-2930 是 “see under” 导引，不是第二个人物记录。{index}
- **书内经历边界：** Venice 居留约五年、版画与收藏活动及与 Querini、Mme Rosenberg 的交往均按 Haskell 叙述保留；未将版画、收藏对象或肖像并入人物，也未另建正式关系。{p371}

## 关系与证据

当前没有登记正式关系。涉及此人物的 13 条 S2 关系候选仍待 S6 逐条裁决；其中与 Napoleon 的机构职务表述按书内名称形式保留，相关端点及其他关系不在 S4 中定为正式关系。{p371}
"""


def insert_accepted(accepted_text: str) -> str:
    lines = accepted_text.splitlines()
    assert CARD_REL not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {CARD_REL}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Dominique De Non / Vivant-Denon in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert CANDIDATE in candidate_by_id
    candidate = candidate_by_id[CANDIDATE]
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Non, Dominique De (Dominique Vivant-Denon)"
    assert candidate.get("index_entry_id") == "N.csv#32"
    target = alignment_by_id[CANDIDATE]
    assert target.get("decision") == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and any(
            alias.casefold() in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
            for alias in ("Dominique De Non", "Dominique Vivant-Denon")
        )
        for row in manifest
    ), "same-identity person KU already exists in manifest"
    assert alignment_by_id["cand-2930"]["decision"] == "excluded"
    assert "see under Non, Dominique De" in alignment_by_id["cand-2930"]["resolution_note"]
    assert candidate_by_id["cand-1753"].get("suggested_type") == "work"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    for _, quote in TEXT_QUOTES:
        assert " ".join(quote.split()) in source_text, quote
    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    assert INDEX_QUOTE in index_text

    statements_path = TABLES / "book-statements.jsonl"
    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    def contains_candidate(value) -> bool:
        if isinstance(value, dict):
            return any(contains_candidate(v) for v in value.values())
        if isinstance(value, list):
            return any(contains_candidate(v) for v in value)
        return value == CANDIDATE

    related = [row for row in statements if contains_candidate(row)]
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in related)
    assert len(related) == 15, f"unexpected statement count involving De Non: {len(related)}"
    assert relation_count == 13, f"unexpected relation-candidate count involving De Non: {relation_count}"

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    card = make_card()
    frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert frontmatter_match and isinstance(yaml.safe_load(frontmatter_match.group(1)), dict)

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_marker = "。各组来源、身份边界和映射更正见[过程记录]"
    new_marker = (
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[多米尼克·德农人物卡]"
        f"(../units/persons/dominique-de-non-vivant-denon.md)，13条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"S4 person：Dominique De Non {GROUP}" not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n### S4 person：Dominique De Non／Dominique Vivant-Denon 跨章身份组登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；索引 N.csv#32 与第15章 p.371 同列 Dominique De Non 和 "
        "Dominique Vivant-Denon；正文 L77 明确以 “who later (as Dominique Vivant-Denon)” 说明后者是同一人物的后用名。"
        "对应索引交叉引用 cand-2930 保持 excluded，索引中的 Voltaire 肖像版画候选 cand-1753 保持 work，均未并入人物组。\n"
        f"- 涉及该人物的15条 S2 陈述中13条为关系候选，均留待 S6；本次不确定 Napoleon 的具体端点、不登记正式关系或 S5 补足。\n\n"
        f"S4 当前已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条成员映射，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )
    next_accepted = insert_accepted(accepted)
    target_files = [
        TABLES / "alignment.csv", TABLES / "ku-manifest.csv",
        ACCEPTED, KNOWLEDGE, RESULT,
    ]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in target_files)

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members=1; identity_sources=2; "
            f"related_statements={len(related)}; relation_candidates_pending={relation_count}; "
            f"crossref_excluded=cand-2930; work_candidate_separate=cand-1753; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"manifest={len(manifest)}->{len(planned_manifest)}"
        )
        return 0

    write_targets = {
        TABLES / "alignment.csv": None,
        TABLES / "ku-manifest.csv": None,
        ACCEPTED: next_accepted,
        KNOWLEDGE: next_knowledge,
        RESULT: next_result,
    }
    for path in write_targets:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    CARD_PATH.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    for path, content in write_targets.items():
        if content is not None:
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; relation_candidates_pending={relation_count}; "
        f"crossref_excluded=cand-2930; work_candidate_separate=cand-1753; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; recovery_backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
