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
ANCHOR = "s4-person-longhi-maccarani-facade-endpoints-20261017"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/"
CHP7_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
PERSON_SPECS = (
    {
        "candidate_id": "cand-1428",
        "group": "new-person:longhi-martino-younger-48ba69e866",
        "ku_id": "units/persons/martino-longhi-younger",
        "card_rel": "04-knowledge/units/persons/martino-longhi-younger.md",
        "name_zh": "马蒂诺·隆吉（小）",
        "name_en": "Martino Longhi the Younger",
        "index_file": INDEX_FILE + "L.csv",
        "index_ref": "L.csv#85",
        "index_quote": "Longhi, Martino, the Younger",
        "body_quote": "the architect Martino Longhi the Younger to add a façade to the church of SS. Vincenzo ed",
        "body_span": "lines 163–164; print p. 183",
        "summary_zh": "哈斯克尔称 Martino Longhi the Younger 为建筑师，并将其与为 SS. Vincenzo ed Anastasio 教堂增建立面相联系。",
        "description_zh": "哈斯克尔在第7章称 Martino Longhi the Younger 为建筑师，并说他受委托为 SS. Vincenzo ed Anastasio 教堂增建立面。本卡仅记录书内具名身份与角色，不补写生卒年、训练、职业经历或外部身份。",
        "description_en": "In Chapter 7, Haskell names Martino Longhi the Younger as an architect and says he was commissioned to add a façade to the church of SS. Vincenzo ed Anastasio. This card records only the named identity and role in the book; it adds no dates, training, career details, or external identity claims.",
        "anchor": "S2 chapter 7, p. 183; index L.csv#85.",
    },
    {
        "candidate_id": "cand-1463",
        "group": "new-person:maccarani-paolo-bda33fc651",
        "ku_id": "units/persons/paolo-maccarani",
        "card_rel": "04-knowledge/units/persons/paolo-maccarani.md",
        "name_zh": "保罗·马卡拉尼",
        "name_en": "Paolo Maccarani",
        "index_file": INDEX_FILE + "M.csv",
        "index_ref": "M.csv#0",
        "index_quote": "Maccarani, Paolo",
        "body_quote": "through Paolo Maccarani, an agent in Rome",
        "body_span": "line 163; print p. 183",
        "summary_zh": "哈斯克尔称 Paolo Maccarani 为驻罗马的代理人，并将其列为 Mazarin 委托 Longhi 增建教堂立面的中介。",
        "description_zh": "第7章称 Paolo Maccarani 为罗马代理人，并说 Mazarin 通过他委托 Martino Longhi the Younger 为 SS. Vincenzo ed Anastasio 教堂增建立面。本卡只记录书内姓名与职务称谓，不据此补写生平或外部身份。",
        "description_en": "Chapter 7 calls Paolo Maccarani an agent in Rome and says that Mazarin commissioned Martino Longhi the Younger through him to add a façade to SS. Vincenzo ed Anastasio. This card records only the name and role as stated in the book; it adds no biography or external identity claim.",
        "anchor": "S2 chapter 7, p. 183; index M.csv#0.",
    },
)
RELATION_STATEMENT = "st-chp7-p183-i08"


def make_card(spec: dict) -> str:
    sources = [
        {
            "citation": f"{BOOK_CITATION}, index, s.v. {spec['index_quote']}.",
            "location": f"书后索引，{spec['index_ref']}；印刷页183。",
            "sentence_summary": f"索引以 {spec['index_quote']} 列名，并指向第7章 p.183。",
            "original_quotes": [
                {"source_span": spec["index_ref"], "text": spec["index_quote"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters-index",
                "source_file": spec["index_file"],
                "source_span": spec["index_ref"],
            },
        },
        {
            "citation": f"{BOOK_CITATION}, ch. 7, p. 183.",
            "location": f"第7章，印刷页183；OCR {spec['body_span']}。",
            "sentence_summary": spec["summary_zh"],
            "original_quotes": [
                {"source_span": spec["body_span"], "text": spec["body_quote"]},
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": CHP7_FILE,
                "source_span": spec["body_span"],
            },
        },
    ]
    frontmatter = {
        "title": f"{spec['name_zh']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": "person",
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

### 书内身份

**中文：** {spec['description_zh']} [S1–S2]

**English:** {spec['description_en']} [S1–S2]

### 身份边界

本卡依据索引与哈斯克尔正文记录来源内身份，未做外部身份核验。正文中的委托、设计、代理或其他角色须按具体 statement 保留原说话者与证据范围；本卡不新增正式关系。

## 关系与证据

当前没有正式关系。第7章 p.183 的相关关系候选 {RELATION_STATEMENT} 留待 S6 审查；此处仅提供书内身份入口。
"""


def insert_accepted_path(text: str, card_rel: str) -> str:
    lines = text.splitlines()
    assert f"- {card_rel}" not in lines
    insert_at = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("- 04-knowledge/units/") and line[2:] > card_rel
        ),
        next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)),
    )
    lines.insert(insert_at, f"- {card_rel}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the Longhi and Maccarani person endpoint groups in S4.")
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

    for spec in PERSON_SPECS:
        cid = spec["candidate_id"]
        assert candidate_map[cid].get("suggested_type") == "person"
        rows = [
            row for row in alignments
            if row.get("candidate_id") and not row.get("external_source")
            and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == spec["group"]
        ]
        assert [row["candidate_id"] for row in rows] == [cid]
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
        assert not (ROOT / spec["card_rel"]).exists(), f"target card already exists: {spec['card_rel']}"
        assert spec["card_rel"] not in accepted_text
        assert not any(row.get("ku_id") == spec["ku_id"] or row.get("card_path") == spec["card_rel"] for row in manifest)
        assert not any(
            row.get("type") == "person" and row.get("name_en", "").casefold() == spec["name_en"].casefold()
            for row in manifest
        ), f"same English name already exists: {spec['name_en']}"

    source_text = (ROOT / CHP7_FILE).read_text(encoding="utf-8-sig")
    for spec in PERSON_SPECS:
        assert spec["body_quote"] in source_text
        index_text = (ROOT / spec["index_file"]).read_text(encoding="utf-8-sig")
        assert spec["index_quote"] in index_text
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    relation = statements[RELATION_STATEMENT]
    assert "cand-1428" in relation["qualifiers"].get("mentioned_candidate_ids", [])
    assert "cand-1463" in relation["qualifiers"].get("mentioned_candidate_ids", [])
    assert relation["qualifiers"].get("relation_candidate") is True
    assert relation.get("subject_candidate_id") == "cand-1588"
    assert relation.get("object_candidate_id") == "cand-6797"

    planned_alignment = [dict(row) for row in alignments]
    spec_map = {spec["candidate_id"]: spec for spec in PERSON_SPECS}
    for row in planned_alignment:
        spec = spec_map.get(row.get("candidate_id"))
        if spec and not row.get("external_source"):
            row["ku_id"] = spec["ku_id"]
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: source-local person identity group {spec['group']} maps to {spec['ku_id']}."

    planned_manifest = list(manifest) + [
        {
            "ku_id": spec["ku_id"],
            "type": "person",
            "canonical_name": spec["name_zh"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": spec["card_rel"],
        }
        for spec in PERSON_SPECS
    ]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S4 person：特雷维广场立面作品的两个书内人物端点（{DATE}）

按既有 S3 身份组分别登记：`cand-1428`（{PERSON_SPECS[0]['group']}；索引 L.csv#85）映射至[马蒂诺·隆吉（小）人物卡](../../../04-knowledge/units/persons/martino-longhi-younger.md)；`cand-1463`（{PERSON_SPECS[1]['group']}；索引 M.csv#0）映射至[保罗·马卡拉尼人物卡](../../../04-knowledge/units/persons/paolo-maccarani.md)。第7章 p.183 分别称 Longhi the Younger 为建筑师，称 Maccarani 为罗马代理人。两卡仅记录来源内具名身份与角色，不补写外部生平。

两人物出现在 {RELATION_STATEMENT} 的书内叙述中；该关系候选仍按 S6 核对 Mazarin、人物角色、作品及地点端点。作品 cand-6797 与地点 cand-6806 仍各按其 S3 新组等待 S4，不在本次写入正式关系；`relations.csv` 与 enrichment 未变更。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 person：Longhi the Younger 与 Paolo Maccarani（{DATE}）\n\n"
        "两个独立 S3 人物组按索引及第7章 p.183 登记为 source-backed 人物 KU；身份仅限书内，不新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    for spec in PERSON_SPECS:
        accepted_text = insert_accepted_path(accepted_text, spec["card_rel"])
    cards = {spec["card_rel"]: make_card(spec) for spec in PERSON_SPECS}

    if args.dry_run:
        print("dry-run passed: cand-1428 and cand-1463 each map to their complete singleton S3 person group")
        print("verified index identities, chapter 7 p.183 roles, and their appearance in the facade statement")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv and enrichment.jsonl unchanged")
        print("planned writes: two bilingual person cards, accepted.yml, ku-manifest.csv, two alignment mappings, process record, result")
        return 0

    for card_rel, content in cards.items():
        (ROOT / card_rel).write_text(content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(accepted_text, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Longhi and Maccarani person groups registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
