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

CANDIDATE = "cand-1662"
GROUP = "new-person:jan-miel-27b41b4426"
KU_ID = "units/persons/jan-miel"
CARD_REL = "04-knowledge/units/persons/jan-miel.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "扬·米尔"
NAME_EN = "Jan Miel"
SOURCE_P126 = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
SOURCE_P137_140 = "02-sources/02-Markdown/05_CHP-5_sec_iii.md"
SOURCE_P207 = "02-sources/02-Markdown/08_CHP-8_sec_i.md"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/M.csv"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
BACKUP_SUFFIX = ".bak-s4-jan-miel-20261016"

SOURCES = (
    {
        "source_file": SOURCE_P126,
        "location": "第5章，印刷页126；OCR L74；PDF物理页7",
        "span": "line 74; print p. 126; PDF physical p. 7",
        "summary": (
            "Haskell称 Jan Miel 为 Flemish painter，并叙述其1654年遗嘱向 Congregazione 留款。"
            "该处OCR将姓氏写作 Miei；既有 S2 页图校读记录确认 PDF 物理页7读作 Miel。"
        ),
        "quotes": (
            ("line 74", "the Flemish painter Jan Miei left 300 scudi to the Congregazione"),
        ),
    },
    {
        "source_file": SOURCE_P137_140,
        "location": "第5章，印刷页137、140；OCR L72、L75–76、L112",
        "span": "lines 72, 75–76, 112; print pp. 137, 140; PDF physical pp. 22, 25",
        "summary": (
            "第137页将 Jan Miel 列为 De Bello Belgico 第二卷插图合作者，并称若干家族关注题材接近 Cerquozzi 的画家；"
            "第140页记 Haskell 对 Miel 在 bambocciante 画法与历史画之间游移的评价。"
        ),
        "quotes": (
            (
                "line 72",
                "collaborating with Jan Miel, Giacomo Borgognone and others on the illustration of the second volume of Famiano Strada’s De Bello Belgico",
            ),
            (
                "lines 75–76",
                "artists who specialised in subjects similar to those of\nCerquozzi—Jan Miel, for instance",
            ),
            (
                "line 112",
                "Jan Miel also found himself veering between a profitable bambocciante manner, which earned him discredit in the social circles to which he aspired, and the more acceptable branch of ‘history painting’ which was far less suited to his talents.",
            ),
        ),
    },
    {
        "source_file": SOURCE_P207,
        "location": "第8章，印刷页207；OCR L44",
        "span": "line 44; print p. 207; PDF physical p. 5",
        "summary": "第8章将 Jan Miel 列为 Roomer 愿意搜求作品的 Bamboccianti 与战画家例子之一；并未指明作品或确认购藏。",
        "quotes": (
            (
                "line 44",
                "by bamboccianti and battle painters such as Pieter van Laer, Jan Miel and Borgognone",
            ),
        ),
    },
    {
        "source_file": INDEX_FILE,
        "location": "全书索引，M.csv#202；索引页码126、127、137、140、207",
        "span": "M.csv#202; indexed pages 126, 127, 137, 140, 207",
        "summary": "索引以 Miel, Jan 为姓名主项，并列出正文定位页码。",
        "quotes": (("M.csv#202", "Miel, Jan"),),
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
    p126 = "[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L74）"
    p137_140 = "[第5章 pp.137、140](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md)（L72、75–76、112）"
    p207 = "[第8章 p.207](../../../02-sources/02-Markdown/08_CHP-8_sec_i.md)（L44）"
    index = "[全书索引 M.csv#202](../../../02-sources/03-Index/03-2-Index-CSV/M.csv)"
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 哈斯克尔在第5章称 Jan Miel 为佛兰德画家；第5章和第8章还在插图合作、绘画题材与 Roomer 搜求作品的语境中提到他。第126页 OCR 将姓氏末字母识作 Miei，既有 S2 页图校读记录指出扫描页读作 Miel。本卡保留索引所列姓名，不扩展生卒或未经本书支持的传记。{p126} {p137_140} {p207} {index}

**English:** Haskell identifies Jan Miel as a Flemish painter in Chapter 5. Chapters 5 and 8 also mention him in discussions of illustration, subject matter, and works Roomer sought to acquire. The p. 126 OCR reads “Miei,” while the existing S2 scan check records the page image as “Miel.” This card preserves the indexed name and adds no life dates or biography unsupported by the book. {p126} {p137_140} {p207} {index}

### 名称与书内身份

- **索引姓名：** Miel, Jan；正文按英文语序作 Jan Miel。中文显示名“扬·米尔”为项目工作译名。{index}
- **书内身份：** Haskell 称其为佛兰德画家；第5章 p.137 将他列为 1647 年 *De Bello Belgico* 第二卷插图合作者，第8章 p.207 仅把他列为 Roomer 搜求画作时的画家例子，未指名具体作品或确认购藏。{p126} {p137_140} {p207}
- **文字与身份边界：** 第5章 p.126 的 OCR 形式 Miei 与页图校读 Miel 的差异按来源记录保留。本卡不推定生卒、籍贯以外的传记信息，不把未指名作品并入人物身份，也未使用外部身份源。{p126} {index}

## 关系与证据

当前没有登记正式关系。涉及 Jan Miel 的 13 条 S2 关系候选均保留待 S6 逐条裁决；本卡的合作、成员、遗嘱、风格与购藏语境仅作为来源限定的身份说明，不构成正式关系边。{p126} {p137_140} {p207}
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
    parser = argparse.ArgumentParser(description="Register Jan Miel's cross-chapter person identity group in S4.")
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
    assert candidate.get("canonical_name") == "Miel, Jan"
    assert candidate.get("index_entry_id") == "M.csv#202"
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
    index_text = normalized_sources[INDEX_FILE]
    assert "Miel, Jan" in index_text

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
    assert len(related) == 13, f"unexpected statement count involving Jan Miel: {len(related)}"
    assert relation_count == 13, f"unexpected relation-candidate count involving Jan Miel: {relation_count}"

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
        f"；person 身份组 {GROUP}（{CANDIDATE}）映射至[扬·米尔人物卡]"
        f"(../units/persons/jan-miel.md)，13条关系候选留待 S6。各组来源、身份边界和映射更正见[过程记录]"
    )
    assert next_result.count(old_marker) == 1
    next_result = next_result.replace(old_marker, new_marker, 1)

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    assert f"S4 person：Jan Miel {GROUP}" not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n### S4 person：Jan Miel 跨章身份组登记（{DATE}）\n\n"
        f"- {CANDIDATE} → {GROUP} → {KU_ID}；该 S3 组只含此候选。索引 M.csv#202 列名 "
        "Miel, Jan，并指向 p.126、127、137、140、207；第5章 p.126 称其为佛兰德画家并记其遗嘱，"
        "扫描页校读记录确认 OCR 的 Jan Miei 应读 Jan Miel。第5章 p.137、140及第8章 p.207 "
        "继续以同一姓名讨论插图合作、绘画风格和 Roomer 搜求作品的例子；不据此认定未指名作品或额外传记。\n"
        f"- 直接涉及该人物的13条 S2 陈述均为关系候选，全部留待 S6；本次未登记正式关系、外部身份或 S5 补足。\n\n"
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
