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
ANCHOR = "s4-place-piazza-di-trevi-20261017"
GROUP = "sg3-place-cand-6806"
CANDIDATE = "cand-6806"
KU_ID = "units/places/piazza-di-trevi"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "特雷维广场"
NAME_EN = "Piazza di Trevi"
CHP7_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
QUOTE = "in the Piazza di Trevi"
STATEMENT = "st-chp7-p183-i08"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)


def make_card() -> str:
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": f"{BOOK_CITATION}, ch. 7, p. 183.",
                "location": "第7章，印刷页183；OCR L164。",
                "sentence_summary": "哈斯克尔以 Piazza di Trevi 标注 SS. Vincenzo ed Anastasio 教堂及其立面的地点语境。",
                "original_quotes": [
                    {"source_span": "line 164; print p. 183", "text": QUOTE},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": CHP7_FILE,
                    "source_span": "line 164; print p. 183",
                },
            },
        ],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 地点身份

**中文：** 哈斯克尔在第7章 p.183 以 Piazza di Trevi 指出 SS. Vincenzo ed Anastasio 教堂立面的地点语境。本卡仅记录原书明确命名的罗马广场，不补写坐标、边界、现代地址或空间沿革；教堂建筑与其立面作品分别属于 place 和 work 对象。[S1]

**English:** In Chapter 7, p. 183, Haskell uses Piazza di Trevi to locate the façade of SS. Vincenzo ed Anastasio. This card records only the square named in the book; it adds no coordinates, boundaries, modern address, or spatial history. The church building and its façade remain distinct place and work objects. [S1]

## 关系与证据

当前没有正式关系。地点在 {STATEMENT} 中作为语境出现；教堂／立面与广场之间是否建立正式空间关系留待 S6 核对。
"""


def insert_accepted_path(text: str) -> str:
    lines = text.splitlines()
    assert f"- {CARD_REL}" not in lines
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
    parser = argparse.ArgumentParser(description="Register Piazza di Trevi as a source-local place endpoint in S4.")
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

    assert candidate_map[CANDIDATE].get("suggested_type") == "place"
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert decisions[CANDIDATE].get("decision") == "new" and not decisions[CANDIDATE].get("ku_id")
    assert "Named location of SS. Vincenzo ed Anastasio" in decisions[CANDIDATE]["resolution_note"]
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "place" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English place name already exists in manifest"

    source_text = (ROOT / CHP7_FILE).read_text(encoding="utf-8-sig")
    assert QUOTE in source_text
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    statement = statements[STATEMENT]
    assert CANDIDATE in statement["qualifiers"].get("mentioned_candidate_ids", [])
    assert statement["qualifiers"].get("relation_candidate") is True
    assert statement.get("object_candidate_id") == "cand-6797"

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: source-local place identity group {GROUP} maps to {KU_ID}; spatial relation remains for S6."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "place",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip()
    process_entry = f"""

<a id="{ANCHOR}"></a>

### S4 place：Piazza di Trevi 书内地点端点登记（{DATE}）

单成员 S3 地点组 {GROUP}（`{CANDIDATE}`）依据第7章 p.183 的明确地点指称登记为[特雷维广场地点卡](../../../04-knowledge/units/places/piazza-di-trevi.md)。卡片只保留书内可确认的广场名称及其在教堂立面叙述中的位置语境；未补坐标、边界、现址或外部对应。其与立面 work 候选 `cand-6797` 的空间关系留待 S6，不在 S4 建边。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 place：Piazza di Trevi（{DATE}）\n\n"
        "单成员书内地点候选登记为 place KU；与教堂立面 work 的空间关系保持待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} is the complete single-member S3 place group {GROUP}")
        print("verified the named urban-square locator and preserved building/work distinctions")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv and enrichment.jsonl unchanged")
        print("planned writes: one bilingual place card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
        return 0

    CARD_PATH.write_text(card_content, encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Piazza di Trevi place group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
