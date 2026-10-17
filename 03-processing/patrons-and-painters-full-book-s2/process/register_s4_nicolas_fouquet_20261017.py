from __future__ import annotations

import argparse
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-nicolas-fouquet-20261017"
CANDIDATE = "cand-1062"
GROUP = "new-person:fouquet-nicolas-426b26efec"
KU_ID = "units/persons/nicolas-fouquet"
CARD_REL = "04-knowledge/units/persons/nicolas-fouquet.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "尼古拉·富凯"
NAME_EN = "Nicolas Fouquet"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/F.csv"
SOURCE_FILE = "02-sources/02-Markdown/07_CHP-7_sec_i.md"
RELATION_IDS = (
    "st-chp7-p186-i17",
    "st-chp7-p186-i18",
    "st-chp7-p186-i19",
    "st-chp7-p187-i01",
)

SOURCES = (
    {
        "location": "书后索引，F.csv#77；索引定位 p.186",
        "summary": "索引主项 Fouquet, Nicolas 定位至 p.186；该条目给出正文中姓氏 Fouquet 的全名定位。",
        "quote": '"Fouquet, Nicolas",,,,186',
        "span": "F.csv#77",
        "doc_id": "patrons-and-painters-index",
        "file": INDEX_FILE,
    },
    {
        "location": "第7章，印刷页186；OCR L215–222",
        "summary": "第7章以 Fouquet 姓氏叙述其任财政大臣、在 Louis XIV 掌权时被捕，以及 Colbert 接替他；同一叙述称二人曾受雇于 Mazarin。全名由书后索引对应。",
        "quote": "Both Fouquet, the unfortunate finance minister who was arrested as soon as Louis XIV took over power, and Colbert, who replaced him, had been employed by Mazarin",
        "span": "lines 215–222; print p. 186",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_FILE,
    },
    {
        "location": "第7章，印刷页187；OCR L215–222 continuation",
        "summary": "同段续句称 Fouquet 与 Colbert 都是意大利艺术的热情收藏者；作为 Haskell 的概括保留，不补充收藏清单。",
        "quote": "and both were enthusiastic collectors of Italian art.",
        "span": "lines 215–222; print p. 187 continuation",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_FILE,
    },
)


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": item["doc_id"],
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relations = "\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第7章 p.186–187 连续段落中的 Fouquet；书后索引将该姓氏定位为 Nicolas Fouquet。p.186 称其为 Louis XIV 掌权时被捕的财政大臣，并说 Colbert 接替了他；同段还称 Fouquet 与 Colbert 曾受雇于 Mazarin。续至 p.187 时，Haskell 称二人都是意大利艺术的热情收藏者。卡片只保留本书对该人物的称谓和叙述，不增加外部身份或收藏事实。

**English:** This card records the Fouquet in Haskell’s continuous passage on pp. 186–187 of chapter 7; the book’s index identifies the surname as Nicolas Fouquet. On p. 186 Haskell calls him the finance minister arrested when Louis XIV took power and says Colbert replaced him; the same passage says both men had been employed by Mazarin. Continuing onto p. 187, Haskell says that both were enthusiastic collectors of Italian art. The card records this book-local identification and account without adding external identity or collection facts.

### 名称与身份边界

索引主项 `Fouquet, Nicolas`（F.csv#77）定位至 p.186；正文使用 Fouquet 姓氏，角色、Colbert 接替及 Mazarin 雇佣语境与该索引定位相合。中文显示名“尼古拉·富凯”为项目工作音译。关系语境不超出第7章 pp.186–187 的叙述范围。

The index main entry `Fouquet, Nicolas` (F.csv#77) points to p. 186; the surname in the text, the ministerial role, Colbert’s succession, and the Mazarin employment context align with that locator. The Chinese rendering is a project working transliteration. No identity or relationship claim is extended beyond Haskell’s account on pp. 186–187.

## 关系与证据

本次没有新增正式关系。以下4条直接 S2 关系候选留待 S6 逐项审查：

{relations}

“意大利艺术的热情收藏者”是 Haskell 对 Fouquet 与 Colbert 的共同描述；本次未据此补作品、收藏清单或正式关系，未写入 `relations.csv`。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Nicolas Fouquet's source-local person group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    if (
        CARD_PATH.exists()
        and any(row.get("ku_id") == KU_ID for row in manifest)
        and decisions[CANDIDATE].get("decision") == "new"
        and decisions[CANDIDATE].get("ku_id") == KU_ID
    ):
        print("ALREADY REGISTERED: Nicolas Fouquet person group")
        return 0

    assert len(manifest) == 1554 and len(alignments) == 12642
    assert candidate_map[CANDIDATE]["suggested_type"] == "person"
    target = decisions[CANDIDATE]
    assert target["decision"] == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    members = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in members] == [CANDIDATE]
    assert not CARD_PATH.exists() and CARD_REL not in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    for rel, snippets in {
        INDEX_FILE: ("Fouquet, Nicolas", "186"),
        SOURCE_FILE: ("Both Fouquet, the unfortunate finance minister who was arrested", "and Colbert, who replaced him, had been employed by Mazarin", "and both were enthusiastic collectors of Italian art"),
    }.items():
        text = (ROOT / rel).read_text(encoding="utf-8-sig")
        for snippet in snippets:
            assert snippet in text, f"source excerpt missing from {rel}: {snippet}"

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = [row for row in statements.values() if CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))]
    assert {row["statement_id"] for row in direct} == set(RELATION_IDS)
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is True for sid in RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    target_row = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    target_row["ku_id"] = KU_ID
    target_row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    target_row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    assert len(planned_manifest) == 1555
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert (totals["registered_groups"], totals["registered_members"], totals["pending_groups"], totals["pending_members"]) == (536, 671, 4268, 4308)

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_warning = "审计警告中的4,324条待登记 `decision=new` alignment 行，含4,309条候选决定映射（4,269组）和15条外部身份记录。"
    new_warning = "审计警告中的4,323条待登记 `decision=new` alignment 行，含4,308条候选决定映射（4,268组）和15条外部身份记录。"
    assert old_warning in result_text
    result_text = result_text.replace(old_warning, new_warning, 1)

    process_entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Nicolas Fouquet 人物组登记（{DATE}）

`cand-1062`（F.csv#77，索引定位 p.186）保留 S3 source-local 人物组 `{GROUP}`，登记为[尼古拉·富凯人物卡](../../../04-knowledge/units/persons/nicolas-fouquet.md)。第7章 p.186–187 连续段落以 Fouquet 姓氏描述财政大臣、被捕、由 Colbert 接替、曾受雇于 Mazarin 及与 Colbert 同为意大利艺术收藏者；全名由索引对应。卡片限于哈斯克尔书内叙述，未使用外部身份来源或补充收藏事实。

4条直接 S2 关系候选 `{RELATION_IDS[0]}`、`{RELATION_IDS[1]}`、`{RELATION_IDS[2]}`、`{RELATION_IDS[3]}` 留待 S6；本次未新增正式关系或写入 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip() + process_entry
    result_note = (
        f"\n\n### S3→S4 person：Nicolas Fouquet（{DATE}）\n\n"
        "`cand-1062`→[尼古拉·富凯人物卡](../units/persons/nicolas-fouquet.md)。全名由索引 p.186 对应正文连续段落中的姓氏 Fouquet。"
        "4条直接关系候选留待 S6；本次未新增正式关系。"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。"
    )
    result_text = result_text.rstrip() + result_note + "\n"

    accepted_lines = ACCEPTED_PATH.read_text(encoding="utf-8-sig").splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    if args.dry_run:
        print("dry-run passed: cand-1062 maps to one source-local Nicolas Fouquet KU")
        print("index full name, p.186–187 passage, and four direct relation-candidate links verified")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; pending-new alignment rows=4,323; relations unchanged")
        print("planned writes: person card, accepted.yml, ku-manifest.csv, alignment.csv, process record, result")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Nicolas Fouquet registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
