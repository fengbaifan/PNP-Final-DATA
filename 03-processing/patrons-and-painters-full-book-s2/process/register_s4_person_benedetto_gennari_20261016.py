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

CANDIDATE = "cand-1127"
GROUP = "new-person:benedetto-gennari-2efcec4904"
KU_ID = "units/persons/benedetto-gennari"
CARD_REL = "04-knowledge/units/persons/benedetto-gennari.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "贝内代托·詹纳里"
NAME_EN = "Benedetto Gennari"
SOURCE_P189 = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
SOURCE_P196 = "02-sources/02-Markdown/07_CHP-7_sec_iv.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/G.csv"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-benedetto-gennari-20261016"

SOURCES = (
    {
        "source_file": SOURCE_P189,
        "location": "第7章，印刷页189；OCR L252–255",
        "span": "lines 252–255; print p. 189; PDF physical p. 44",
        "summary": (
            "Haskell 将 Benedetto Gennari 列为对 Louis XIV 怀有敬慕的博洛尼亚画家之一；"
            "作者同时保留对这种敬慕并非全无利害动机的怀疑。"
        ),
        "quotes": (
            (
                "lines 253–255",
                "We are told that Carlo Cignani, Benedetto Gennari, Luigi Quaini and Donato Creti were all keen admirers of Louis XIV, and it is not being excessively cynical to suspect that such admiration was not wholly disinterested.",
            ),
        ),
    },
    {
        "source_file": SOURCE_P196,
        "location": "第7章，印刷页196；OCR L52–58",
        "span": "lines 52–58; print p. 196; PDF physical p. 51",
        "summary": (
            "Haskell 称 Benedetto Gennari 来自 Bologna，是 Guercino 之侄，并叙述其在 England、Paris 工作及1688年离开 England 后返回 France、最终回到 Italy。"
        ),
        "quotes": (
            (
                "lines 52–53",
                "Another Italian artist who came to England at about the same time as Verrio was\nBenedetto Gennari from Bologna.",
            ),
            (
                "line 53",
                "He was the nephew of Guercino whom Charles I had tried to entice some fifty years earlier and he too was working in Paris, where he had enjoyed a certain success.",
            ),
            (
                "lines 53–54",
                "Some of these brash mythological paintings, heavily tinged with eroticism, have survived and we can see that in them he followed the current\nFrench practice of portraying his sitters in the guise of some ancient heroine or deity.",
            ),
            (
                "lines 55–58",
                "Gennari turned from Danae or Elizabeth Felton as Cleopatra to altar paintings, and in combination with\nVerrio, Christopher Wren and Grinling Gibbons he helped to put into effect in\nWhitehall the most full-blooded Baroque decoration ever seen in an English church.\nBut this could scarcely last, and in 1688 Gennari was compelled to leave ‘quel funesto paese’ and return to France and eventually Italy, having acquired abroad ‘a new style which devoted special care to the rich decoration of his royal sitters’.",
            ),
        ),
    },
    {
        "source_file": INDEX_FILE,
        "location": "全书索引，G.csv#34；索引页码189、196",
        "span": "G.csv#34; indexed pages 189, 196",
        "summary": "索引以 Gennari, Benedetto 为姓名主项，并指向正文页189、196。",
        "quotes": (("G.csv#34", "Gennari, Benedetto"),),
    },
)


def source_row(item: dict):
    return {
        "citation": BOOK_CITATION,
        "location": item["location"],
        "sentence_summary": item["summary"],
        "original_quotes": [
            {"source_span": span, "text": quote}
            for span, quote in item["quotes"]
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": item["source_file"],
            "source_span": item["span"],
        },
    }


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [source_row(item) for item in SOURCES],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    p189 = "[第7章 p.189](../../../02-sources/02-Markdown/07_CHP-7_sec_i.md)（L252–255）"
    p196 = "[第7章 p.196](../../../02-sources/02-Markdown/07_CHP-7_sec_iv.md)（L52–58）"
    index = "[全书索引 G.csv#34](../../../02-sources/03-Index/03-2-Index-CSV/G.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 哈斯克尔第7章在 p.189 将 Benedetto Gennari 列为仰慕 Louis XIV 的博洛尼亚画家之一，并保留作者对这种仰慕是否全无利害动机的怀疑。p.196 称 Gennari 来自 Bologna、是 Guercino 之侄，记述其在 England 与 Paris 工作，并于1688年离开 England，后返回 France、最终回到 Italy。本卡按书内叙述登记人物，不补入生卒或未经本书支持的身份细节。{p189} {p196} {index}

**English:** In Chapter 7, p. 189, Haskell lists Benedetto Gennari among the Bolognese painters who admired Louis XIV, while retaining the author’s suspicion that this admiration was not wholly disinterested. On p. 196, Haskell says Gennari came from Bologna and was Guercino’s nephew, and recounts his work in England and Paris, his departure from England in 1688, and his eventual return to Italy. This card records the book’s account and adds no life dates or identity details unsupported by it. {p189} {p196} {index}

### 名称与书内身份

- **索引姓名：** Gennari, Benedetto；正文按英文语序作 Benedetto Gennari。中文显示名“贝内代托·詹纳里”为项目工作译名。{index}
- **书内身份与经历：** Haskell 称其为来自 Bologna 的意大利艺术家，并记其曾在 England、Paris 工作，1688年离开 England 后返回 France，最终回到 Italy。所有地点与时间按本书叙述归属，不扩写为独立核验的完整年表。{p196}
- **关系与评价边界：** “Guercino 之侄”、对 Louis XIV 的敬慕及与 Verrio 等人的合作均保留为 S2 来源断言；本卡不将其升级为正式关系或补入外部传记。{p189} {p196}

## 关系与证据

当前没有登记正式关系。涉及 Benedetto Gennari 的 12 条 S2 关系候选仍待 S6 逐条裁决；本卡所引亲属、合作、委托与风格语境均保持来源限定。{p189} {p196}
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
    parser = argparse.ArgumentParser(description="Register Benedetto Gennari's cross-chapter person identity group in S4.")
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
    assert candidate.get("canonical_name") == "Gennari, Benedetto"
    assert candidate.get("index_entry_id") == "G.csv#34"
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
        and (row.get("name_en", "").casefold() == NAME_EN.casefold()
             or row.get("canonical_name", "").casefold() == NAME_ZH.casefold())
        for row in manifest
    ), "same-identity person KU already exists in manifest"

    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD_REL not in accepted
    normalized_sources = {}
    for item in SOURCES:
        text = (ROOT / item["source_file"]).read_text(encoding="utf-8-sig")
        normalized_sources[item["source_file"]] = " ".join(text.split())
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in normalized_sources[item["source_file"]], quote
    assert "Gennari, Benedetto" in normalized_sources[INDEX_FILE]

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
    assert len(related) == 13, f"unexpected statement count involving Benedetto Gennari: {len(related)}"
    assert relation_count == 12, f"unexpected relation-candidate count involving Benedetto Gennari: {relation_count}"

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
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[贝内代托·詹纳里人物卡]"
        f"(../units/persons/benedetto-gennari.md)，12条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"S4 person：Benedetto Gennari {GROUP}" not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n### S4 person：Benedetto Gennari 跨章身份组登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 组只含此候选。索引 G.csv#34 指向第7章 p.189、196；"
        "p.189 将其列为敬慕 Louis XIV 的博洛尼亚画家之一，同时保留 Haskell 对其动机的怀疑；p.196 "
        "称其来自 Bologna、为 Guercino 之侄，记其在 England 与 Paris 工作及1688年离开 England 后的去向。"
        "本卡保留书内归属，不补入生卒、外部身份或完整传记。\n"
        f"- 涉及该人物的13条 S2 陈述中12条为关系候选，均留待 S6；本次未登记正式关系或 S5 补足。\n\n"
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
            f"dry-run passed: {CANDIDATE} -> {KU_ID}; group_members=1; identity_sources={len(SOURCES)}; "
            f"related_statements={len(related)}; relation_candidates_pending={relation_count}; "
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
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; "
        f"manifest={len(planned_manifest)}; recovery_backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
