from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s4-gesu-high-altar-muziano-works-20261017"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_ii.md"
RELATION_STATEMENTS = {
    "st-chp3-secii-l6-17-muziano-circumcision-commission",
    "st-chp3-seciv-l16-24-cardinal-high-altar-decoration",
    "st-chp3-seciv-l16-24-farnese-heirs-high-altar-decoration",
    "st-chp3-seciv-l26-33-ignatius-remains-proposed-relocation",
}

SPECS = [
    {
        "candidate": "cand-1720",
        "group": "new-person:girolamo-muziano-85c13d2489",
        "type": "person",
        "ku": "units/persons/girolamo-muziano",
        "card": "04-knowledge/units/persons/girolamo-muziano.md",
        "name_zh": "吉罗拉莫·穆齐亚诺",
        "name_en": "Girolamo Muziano",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 66.",
                "location": "第3章，印刷页66；OCR L7–8。",
                "summary": "哈斯克尔称 Cardinal Farnese 委托 Girolamo Muziano 为耶稣堂主祭坛绘制《The Circumcision》。",
                "quotes": [("line 8; print p. 66", "Girolamo Muziano to paint The Circumcision")],
                "source_file": SOURCE_FILE,
                "doc_id": "patrons-and-painters",
                "span": "lines 7–8; print p. 66",
            },
            {
                "citation": f"{BOOK_CITATION}, index, s.v. Muziano.",
                "location": "书后索引，M.csv#261；印刷页66。",
                "summary": "索引以 Muziano, Girolamo 列出该人物及其正文页码。",
                "quotes": [("M.csv#261", "Muziano, Girolamo")],
                "source_file": "02-sources/03-Index/03-2-Index-CSV/M.csv",
                "doc_id": "patrons-and-painters-index",
                "span": "M.csv#261",
            },
        ],
        "body_zh": (
            "本卡记录书后索引所列 Girolamo Muziano，以及第3章正文明确称名的画家身份。哈斯克尔称 Cardinal Alessandro Farnese 委托其为耶稣堂主祭坛绘制《The Circumcision》。"
            "本卡只保留来源中的姓名和画家角色，不补写生卒、籍贯或其他外部生平。"
        ),
        "body_en": (
            "This card records the painter indexed as Girolamo Muziano and named in Chapter 3. Haskell says Cardinal Alessandro Farnese commissioned him to paint The Circumcision for the Gesù High Altar. "
            "The card preserves only the source’s name and painter role; no dates, birthplace, or other external biography are added."
        ),
        "section": "### 人物身份",
        "boundary_zh": "原书所称画家；作品及委托关系分别记录。",
        "boundary_en": "The painter named in the book; the work and commission are recorded separately.",
    },
    {
        "candidate": "cand-4999",
        "group": "workgrp-75fd35c26a4b62",
        "type": "work",
        "ku": "units/works/gesu-high-altar",
        "card": "04-knowledge/units/works/gesu-high-altar.md",
        "name_zh": "耶稣堂主祭坛",
        "name_en": "High Altar of the Gesù",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 66.",
                "location": "第3章，印刷页66；OCR L7–9。",
                "summary": "哈斯克尔称 Farnese 为主祭坛装饰保留家族权利，并称 Muziano 为主祭坛绘制《The Circumcision》。",
                "quotes": [
                    ("line 8; print p. 66", "paint The Circumcision for the High Altar"),
                    ("lines 8–9; print p. 66", "the High Altar exclusively for his family"),
                ],
                "source_file": SOURCE_FILE,
                "doc_id": "patrons-and-painters",
                "span": "lines 7–9; print p. 66",
            },
        ],
        "body_zh": (
            "本卡记录原书所称耶稣堂 High Altar 这一独立祭坛结构。哈斯克尔称 Farnese 将其装饰保留给自己及家族，并称 Muziano 受委托为其绘制《The Circumcision》。"
            "祭坛结构按 S3 类型作为 work 记录，与祭坛画及耶稣堂建筑分别处理；本卡不补写形制、材料或现存状况。"
        ),
        "body_en": (
            "This card records the Gesù High Altar as a distinct altar structure. Haskell says Farnese reserved its decoration for himself and his family and that Muziano was commissioned to paint The Circumcision for it. "
            "Following the S3 classification, the altar structure is recorded as a work, separate from the painting and the church building; no form, material, or present condition is added."
        ),
        "section": "### 作品身份",
        "boundary_zh": "祭坛结构为 work；《The Circumcision》为另一件绘画 work，教堂整体为 place。",
        "boundary_en": "The altar structure is a work; The Circumcision is a separate painting work, and the church as a whole is a place.",
    },
    {
        "candidate": "cand-5003",
        "group": "workgrp-c358a8984d4dc4",
        "type": "work",
        "ku": "units/works/muziano-circumcision-gesu-high-altar",
        "card": "04-knowledge/units/works/muziano-circumcision-gesu-high-altar.md",
        "name_zh": "耶稣堂主祭坛《割礼》祭坛画",
        "name_en": "The Circumcision for the High Altar of the Gesù",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 3, p. 66.",
                "location": "第3章，印刷页66；OCR L7–8。",
                "summary": "哈斯克尔称 Cardinal Alessandro Farnese 委托 Muziano 为耶稣堂主祭坛绘制题名为 The Circumcision 的画作。",
                "quotes": [("line 8; print p. 66", "Girolamo Muziano to paint The Circumcision for the High Altar")],
                "source_file": SOURCE_FILE,
                "doc_id": "patrons-and-painters",
                "span": "lines 7–8; print p. 66",
            },
        ],
        "body_zh": (
            "本卡记录哈斯克尔称为《The Circumcision》的绘画。原书称 Cardinal Alessandro Farnese 委托 Girolamo Muziano 为耶稣堂主祭坛绘制此画。"
            "中文题名为描述性译名；原书所述委托目的地是已单独登记的[耶稣堂主祭坛结构](gesu-high-altar.md)。原书此处未说明画作是否完成、材质或现存地点。"
        ),
        "body_en": (
            "This card records the painting Haskell calls The Circumcision. The book says Cardinal Alessandro Farnese commissioned Girolamo Muziano to paint it for the Gesù High Altar. "
            "The Chinese title is descriptive; the altar structure is separately registered as the [Gesù High Altar](gesu-high-altar.md). The passage does not say whether the painting was completed or identify its medium or present location."
        ),
        "section": "### 作品身份",
        "boundary_zh": "祭坛画为 work；主祭坛结构是另一件 work，教堂建筑为 place。",
        "boundary_en": "The painting is a work; the altar structure is a separate work, and the church building is a place.",
    },
]


def make_card(spec: dict) -> str:
    sources = []
    for item in spec["sources"]:
        sources.append({
            "citation": item["citation"],
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": item["doc_id"],
                "source_file": item["source_file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{spec['name_zh']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": spec["type"],
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

{spec['section']}

**中文：** {spec['body_zh']}

**English:** {spec['body_en']}

### 对象边界

**中文：** {spec['boundary_zh']}

**English:** {spec['boundary_en']}

## 关系与证据

当前没有已登记的正式关系。委托、祭坛结构及绘画之间的 S2 关系候选留待 S6 核对端点、方向、语境和证据；本次不将断言转换为关系边，不新增 S5 enrichment。
"""


def insert_accepted_paths(text: str, card_paths: list[str]) -> str:
    lines = text.splitlines()
    for card_path in sorted(card_paths):
        assert f"- {card_path}" not in lines
        insert_at = next(
            (
                i for i, line in enumerate(lines)
                if line.startswith("- 04-knowledge/units/") and line[2:] > card_path
            ),
            next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
        )
        lines.insert(insert_at, f"- {card_path}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Muziano and the Gesù altar works in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    for spec in SPECS:
        cid = spec["candidate"]
        assert candidate_map[cid].get("suggested_type") == spec["type"]
        decision = decisions[cid]
        assert decision.get("decision") == "new" and not decision.get("ku_id")
        assert sync.get_group(decision.get("resolution_note", "")) == spec["group"]
        members = [
            row["candidate_id"] for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new" and not row.get("ku_id")
            and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert members == [cid], (spec["group"], members)
        assert spec["card"] not in accepted_text
        assert not (ROOT / spec["card"]).exists()
        assert not any(row.get("ku_id") == spec["ku"] or row.get("card_path") == spec["card"] for row in manifest)
        assert not any(
            row.get("type") == spec["type"]
            and row.get("name_en", "").casefold() == spec["name_en"].casefold()
            for row in manifest
        ), f"duplicate type/name for {cid}"

    assert decisions["cand-0995"].get("ku_id") == "units/persons/cardinal-alessandro-farnese"
    assert decisions["cand-5007"].get("decision") == "undecided"
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    source_quotes = (
        "Girolamo Muziano to paint The Circumcision for the High Altar",
        "the High Altar exclusively for his family",
    )
    assert all(" ".join(quote.split()) in source_text for quote in source_quotes)

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    assert RELATION_STATEMENTS.issubset(statements)
    assert all(statements[sid].get("qualifiers", {}).get("relation_candidate") is True for sid in RELATION_STATEMENTS)
    commission = statements["st-chp3-secii-l6-17-muziano-circumcision-commission"]
    assert commission.get("qualifiers", {}).get("artist_candidate_id") == "cand-1720"
    assert commission.get("qualifiers", {}).get("location_candidate_id") == "cand-4999"

    planned_alignment = [dict(row) for row in alignments]
    for spec in SPECS:
        matched = [
            row for row in planned_alignment
            if row.get("candidate_id") == spec["candidate"] and not row.get("external_source")
        ]
        assert len(matched) == 1
        matched[0]["ku_id"] = spec["ku"]
        matched[0]["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        matched[0]["resolution_note"] += (
            f" S4 registration: source-backed {spec['type']} group {spec['group']} "
            f"maps to {spec['ku']}; the commission and inter-work relations remain for S6."
        )

    planned_manifest = list(manifest)
    for spec in SPECS:
        planned_manifest.append({
            "ku_id": spec["ku"],
            "type": spec["type"],
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": spec["card"],
        })
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    mappings = "；".join(
        f"`{s['candidate']}`（{s['group']}）→ [{s['name_zh']}](../../../{s['card']})"
        for s in SPECS
    )
    process_text += f"""

<a id="{ANCHOR}"></a>

### S4：耶稣堂主祭坛、Muziano 與《The Circumcision》登记（{DATE}）

按三个独立 S3 身份组登记：{mappings}。第3章 p.66 称 Cardinal Alessandro Farnese 委托 Girolamo Muziano 为 High Altar 绘制《The Circumcision》，并称 Farnese 将主祭坛装饰保留给自己及家族。人物、祭坛结构和绘画分别建卡；S3 已将 High Altar 定为 work，故不与耶稣堂 place 或祭坛画合并。原书未说明该画是否完成、材质或现存地点，本轮不补写。

四条相关 S2 关系候选 `{', '.join(sorted(RELATION_STATEMENTS))}` 留待 S6；继承人候选 `cand-5007` 仍为 undecided。未新增正式关系或 S5 enrichment，`relations.csv` 与 `enrichment.jsonl` 未变更。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    result_note = (
        f"\n\n### S4：耶稣堂主祭坛、Muziano 与《The Circumcision》（{DATE}）\n\n"
        "按三个独立 S3 身份组登记画家、主祭坛结构和祭坛画；祭坛结构与画作保持不同 work 身份。"
        "委托、家族保留装饰及继承人相关陈述留待 S6；未补写作品完成状态、材质或现存地点。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。\n"
    )
    result_text = result_text.rstrip() + result_note
    planned_accepted = insert_accepted_paths(accepted_text, [spec["card"] for spec in SPECS])
    cards = [(ROOT / spec["card"], make_card(spec)) for spec in SPECS]

    if args.dry_run:
        print("dry-run passed: three singleton S3 groups have distinct person and work destinations")
        print(f"verified {len(source_quotes)} source quotations, indexed person identity, and separate altar/painting candidates")
        print(f"S6 relation candidates preserved: {len(RELATION_STATEMENTS)}; heirs candidate remains undecided")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; all accepted paths unique")
        print("planned writes: three bilingual cards, accepted.yml, ku-manifest.csv, three alignment mappings, process record, result")
        return 0

    for path, content in cards:
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: 3 S4 groups; manifest={len(planned_manifest):,}; "
        f"registered={totals['registered_groups']}/{totals['registered_members']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
