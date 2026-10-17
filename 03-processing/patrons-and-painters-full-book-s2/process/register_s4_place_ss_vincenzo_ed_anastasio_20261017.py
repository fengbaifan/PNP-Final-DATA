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
ANCHOR = "s4-place-ss-vincenzo-ed-anastasio-20261017"
GROUP = "sg3-place-cand-0723"
CANDIDATE = "cand-0723"
KU_ID = "units/places/church-ss-vincenzo-ed-anastasio"
CARD_REL = f"04-knowledge/{KU_ID}.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "圣文森佐与圣阿纳斯塔西奥教堂"
NAME_EN = "Church of SS. Vincenzo ed Anastasio"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/C.csv"
CHP7_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
INDEX_QUOTE = "SS. Vincenzo ed Anastasio"
BODY_QUOTES = (
    "to add a façade to the church of SS. Vincenzo ed",
    "Anastasio in the Piazza di Trevi.",
)
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
                "citation": f"{BOOK_CITATION}, index, s.v. Churches, subentry SS. Vincenzo ed Anastasio.",
                "location": "书后索引，C.csv#247；印刷页183。",
                "sentence_summary": "索引在 Churches 主项下列出 SS. Vincenzo ed Anastasio，并指向第7章 p.183。",
                "original_quotes": [
                    {"source_span": "C.csv#247", "text": INDEX_QUOTE},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters-index",
                    "source_file": INDEX_FILE,
                    "source_span": "C.csv#247",
                },
            },
            {
                "citation": f"{BOOK_CITATION}, ch. 7, p. 183.",
                "location": "第7章，印刷页183；OCR L163–164。",
                "sentence_summary": "哈斯克尔称该教堂增建立面；同段将其位置写为 Piazza di Trevi。",
                "original_quotes": [
                    {"source_span": "line 163; print p. 183", "text": BODY_QUOTES[0]},
                    {"source_span": "line 164; print p. 183", "text": BODY_QUOTES[1]},
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": CHP7_FILE,
                    "source_span": "lines 163–164; print p. 183",
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

### 建筑地点身份

**中文：** 哈斯克尔称 SS. Vincenzo ed Anastasio 教堂是第7章所述立面的建筑地点，并以 Piazza di Trevi 标注其位置语境。[S1–S2] 中文名称按来源音译，不补写该建筑的建造、管理、历史名称或现存状态。

**English:** Haskell identifies SS. Vincenzo ed Anastasio as the church building to which the Chapter 7 façade was added and places it in the context of Piazza di Trevi. [S1–S2] The English name follows the source; this card adds no construction history, administration, historical name, or survival status.

### 对象边界

教堂建筑为 place；增建的立面另作为 work 候选处理。广场地点见[特雷维广场](piazza-di-trevi.md)。导航链接不表示正式空间关系；该关系留待 S6。

## 关系与证据

当前没有正式关系。{STATEMENT} 将教堂作为委托立面的建筑地点提及；教堂、立面作品及 Piazza di Trevi 之间的空间或作品关系须在 S6 按端点分别审查。
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
    parser = argparse.ArgumentParser(description="Register SS. Vincenzo ed Anastasio as a source-local building place in S4.")
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
    assert candidate_map[CANDIDATE].get("sub_entry") == "SS. Vincenzo ed Anastasio"
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert decisions[CANDIDATE].get("decision") == "new" and not decisions[CANDIDATE].get("ku_id")
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "place" and row.get("name_en", "").casefold() == NAME_EN.casefold()
        for row in manifest
    ), "same English building name already exists in manifest"

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    body_text = (ROOT / CHP7_FILE).read_text(encoding="utf-8-sig")
    assert INDEX_QUOTE in index_text
    assert all(quote in body_text for quote in BODY_QUOTES)
    statements = {row["statement_id"]: row for row in sync.load_statements()}
    statement = statements[STATEMENT]
    assert CANDIDATE in statement["qualifiers"].get("mentioned_candidate_ids", [])
    assert statement["qualifiers"].get("relation_candidate") is True
    assert statement.get("object_candidate_id") == "cand-6797"
    assert decisions["cand-6806"].get("ku_id") == "units/places/piazza-di-trevi"

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: source-local building-place identity group {GROUP} maps to {KU_ID}; work and spatial relations remain for S6."

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

### S4 place：SS. Vincenzo ed Anastasio 教堂建筑地点登记（{DATE}）

索引候选 `cand-0723` 属 S3 单成员组 {GROUP}，类型为 place，索引主项 Churches 下的子目为 SS. Vincenzo ed Anastasio。现登记为[圣文森佐与圣阿纳斯塔西奥教堂地点卡](../../../04-knowledge/units/places/church-ss-vincenzo-ed-anastasio.md)。第7章 p.183 的立面记述将其指作建筑地点，并说明位置语境为已登记的 Piazza di Trevi。教堂建筑、广场及立面 work 候选 `cand-6797` 各保留为不同对象；本次只登记教堂 place。

`{STATEMENT}` 中建筑与立面、广场的关系仍留待 S6 审查，不写入 `relations.csv`。本卡不补外部建筑名、坐标、建造历史或现存状态，也未新增 S5 enrichment。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text += process_entry
    result_note = (
        f"\n\n### S4 place：SS. Vincenzo ed Anastasio 教堂（{DATE}）\n\n"
        "索引子目及第7章叙述支持一张建筑 place KU；教堂、广场与立面仍分属不同候选对象，正式关系待 S6。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"
    planned_accepted = insert_accepted_path(accepted_text)
    card_content = make_card()

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} is the complete single-member S3 building-place group {GROUP}")
        print("verified index subentry, chapter 7 building reference, and separate Piazza/work candidates")
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
    print(f"applied: church place group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
