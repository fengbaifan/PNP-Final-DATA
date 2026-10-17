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
ANCHOR = "s3-s4-person-pietro-foscarini-20261017"
CANDIDATE = "cand-1056"
GROUP = "new-person:foscarini-pietro-0946cf5155"
KU_ID = "units/persons/pietro-foscarini"
CARD_REL = "04-knowledge/units/persons/pietro-foscarini.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "皮埃特罗·福斯卡里尼"
NAME_EN = "Pietro Foscarini"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/F.csv"
SOURCE_259 = "02-sources/02-Markdown/09_CHP-9_intro.md"
SOURCE_273 = "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
RELATION_IDS = (
    "st-chp9-p259-pietro-foscarini-procuratore",
    "st-chp9-p259-pietro-left-picture-group-with-palace",
    "st-chp9-p259-pietro-left-other-venetian-classics",
    "st-chp9-p273-n02-foscarini-will-marble-altar-bequest",
)

SOURCES = (
    {
        "location": "书后索引，F.csv#71；索引定位 pp.259、273n",
        "summary": "索引主项 Foscarini, Pietro 定位至 p.259 与 p.273 注；该定位与两页正文的全名一致。",
        "quote": '"Foscarini, Pietro",,,,"259, 273n"',
        "span": "F.csv#71",
        "doc_id": "patrons-and-painters-index",
        "file": INDEX_FILE,
    },
    {
        "location": "第9章，印刷页259；OCR L188–200",
        "summary": "正文称 Pietro Foscarini 是一组留在宅邸的画作的前任所有者，并称其为 Procuratore di San Marco；Haskell 对其1745年去世的记述带问号，卡片保留该不确定性。",
        "quote": "had been left with the palace by its former owner, Pietro Foscarini, himself a Procuratore di San Marco, who died in 1745?",
        "span": "lines 188–200; print p. 259",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_259,
    },
    {
        "location": "第9章，印刷页259；OCR L323–445，注4",
        "summary": "第9章注4称 Pietro Foscarini 的遗嘱及其绘画清单藏于 Biblioteca Correr；原始文书未在本项目独立查阅。",
        "quote": "Pietro Foscarini’s will and the inventory of his pictures are in the Biblioteca Correr, Cod. Cicogna, MMDCCCCXLV—2686.",
        "span": "line 392; print p. 259 n. 4",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_259,
    },
    {
        "location": "第9章，印刷页273；OCR L85–127，注2",
        "summary": "第9章注2再次全名提及 Pietro Foscarini，称其1745年遗嘱为 S. Simeon Grande 教堂的精细大理石祭坛留款，并给出 Biblioteca Correr 手稿定位；原始遗嘱未独立查阅。",
        "quote": "For instance, Pietro Foscarini left money in his will in 1745 for an ‘altare di marmo fine’ to be erected in the church—Biblioteca Correr, Cod. Cicogna, MMDCCCCXLV—2686.",
        "span": "line 116; print p. 273 n. 2",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_273,
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

**中文：** 本卡记录哈斯克尔第9章 p.259 与 p.273 注2 提及、并由索引定位至两处的 Pietro Foscarini。p.259 称一组留在宅邸的画作包括七幅 Tintoretto 及其他威尼斯名作，这些画作由前任所有者 Pietro Foscarini 留下；作者称他为 Procuratore di San Marco，并以问号写其可能于1745年去世。p.259 注4和 p.273 注2 均将其遗嘱定位于 Biblioteca Correr 的同一手稿；p.273 注2称其1745年遗嘱为 S. Simeon Grande 教堂的一座精细大理石祭坛留款。原始遗嘱与清单未在本项目独立查阅；中文显示名为项目工作音译。

**English:** This card records Pietro Foscarini, cited on p. 259 and p. 273 n. 2 of Haskell’s chapter 9 and located at both places by the index. On p. 259 Haskell says that a group of pictures left with a palace by its former owner, Pietro Foscarini, included seven Tintorettos and other Venetian classics. He identifies Foscarini as a Procuratore di San Marco and places a question mark after the statement that he died in 1745. Chapter 9 p. 259 n. 4 and p. 273 n. 2 locate his will in the same Biblioteca Correr manuscript; p. 273 n. 2 says the 1745 will left money for a fine marble altar at S. Simeon Grande. The will and inventory were not independently consulted. The Chinese display name is a project working transliteration.

### 名称与身份边界

索引主项 `Foscarini, Pietro`（F.csv#71）列 p.259 与 p.273 注2。两处正文都写出 Pietro Foscarini 全名，且 p.273 注2与 p.259 注4将遗嘱定位到同一 Biblioteca Correr 手稿；两候选姓名、手稿定位及1745年遗嘱语境相合，按 S3 归为同一书内人物。既有 Marco Foscarini 人物卡对应不同的名字，不与本卡合并。死亡年份问号原样保留；本卡不据遗嘱日期推定确切死亡日期。

The index entry `Foscarini, Pietro` (F.csv#71) lists p. 259 and p. 273 n. 2. Both passages give the full name, and p. 273 n. 2 and p. 259 n. 4 locate the will in the same Biblioteca Correr manuscript; the matching name, manuscript locator, and 1745 will context support the S3 grouping as one book-local person. The existing Marco Foscarini card represents a different person and is not merged. Haskell’s question mark after the death year is preserved; the will date is not used to infer an exact death date.

## 关系与证据

本次没有新增正式关系。以下4条直接 S2 关系候选留待 S6 逐项审查：

{relations}

作画留置、Procuratore di San Marco 身份及遗嘱留款均按哈斯克尔书内报告保留；原始档案未独立查阅，本次未写入 `relations.csv`。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Pietro Foscarini's cross-page source-local person group in S4.")
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
        and decisions[CANDIDATE].get("ku_id") == KU_ID
        and decisions[CANDIDATE].get("decision") == "new"
    ):
        print("ALREADY REGISTERED: Pietro Foscarini person group")
        return 0

    assert len(manifest) == 1552 and len(alignments) == 12642
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
        INDEX_FILE: ("Foscarini, Pietro", "259, 273n"),
        SOURCE_259: ("Pietro Foscarini, himself a Procuratore di San Marco, who died in 1745?", "Pietro Foscarini’s will and the inventory of his pictures"),
        SOURCE_273: ("Pietro Foscarini left money in his will in 1745", "altare di marmo fine"),
    }.items():
        source_text = (ROOT / rel).read_text(encoding="utf-8-sig")
        for snippet in snippets:
            assert snippet in source_text, f"source excerpt missing from {rel}: {snippet}"

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = [row for row in statements.values() if CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))]
    assert {row["statement_id"] for row in direct} == set(RELATION_IDS)
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is True for sid in RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    row = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    row["ku_id"] = KU_ID
    row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    }]
    assert len(planned_manifest) == 1553
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert (totals["registered_groups"], totals["registered_members"], totals["pending_groups"], totals["pending_members"]) == (534, 668, 4270, 4311)

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    old_warning = "审计警告中的4,327条待登记 `decision=new` alignment 行，含4,312条候选决定映射（4,271组）和15条外部身份记录。"
    new_warning = "审计警告中的4,326条待登记 `decision=new` alignment 行，含4,311条候选决定映射（4,270组）和15条外部身份记录。"
    assert old_warning in result_text
    result_text = result_text.replace(old_warning, new_warning, 1)

    process_entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Pietro Foscarini 跨页人物组登记（{DATE}）

`cand-1056`（F.csv#71，索引 p.259 与 p.273 n.2）保留 S3 source-local 人物组 `{GROUP}`，登记为[皮埃特罗·福斯卡里尼人物卡](../../../04-knowledge/units/persons/pietro-foscarini.md)。第9章 p.259 全名指向其作为 Procuratore di San Marco 及一组留在宅邸画作的前任所有者，Haskell 对1745年去世的记述带问号；p.259 注4与 p.273 注2将遗嘱定位到同一 Biblioteca Correr 手稿，p.273 注2再次全名并记载1745年祭坛留款。索引定位、全名与遗嘱语境支持同一书内人物。原始遗嘱和清单未独立查阅；本卡不把1745年遗嘱日期写成确切死亡日期，也不与既有 Marco Foscarini 合并。

4条直接 S2 关系候选 `{RELATION_IDS[0]}`、`{RELATION_IDS[1]}`、`{RELATION_IDS[2]}`、`{RELATION_IDS[3]}` 留待 S6；本次未新增正式关系或写入 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip() + process_entry
    result_note = (
        f"\n\n### S3→S4 person：Pietro Foscarini（{DATE}）\n\n"
        "`cand-1056`→[皮埃特罗·福斯卡里尼人物卡](../units/persons/pietro-foscarini.md)。索引 p.259、p.273 n.2 与两页重复全名及同一遗嘱手稿定位相合；1745年死亡仍带原书问号。"
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
        print("dry-run passed: cand-1056 maps to one source-local Pietro Foscarini KU")
        print("p.259 and p.273 n.2 names, shared will locator, and four relation-candidate links verified")
        print("the questioned 1745 death date remains uncertain; Marco Foscarini remains distinct")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; pending-new alignment rows=4,326; relations unchanged")
        print("planned writes: person card, accepted.yml, ku-manifest.csv, alignment.csv, process record, result")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Pietro Foscarini registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
