from __future__ import annotations

import argparse
import json
import re
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
ANCHOR = "s3-s4-person-camillo-astalli-20261017"
CANDIDATE = "cand-0144"
GROUP = "new-person:astalli-camillo-acfa71028e"
KU_ID = "units/persons/camillo-astalli"
CARD_REL = "04-knowledge/units/persons/camillo-astalli.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "卡米洛·阿斯塔利"
NAME_EN = "Camillo Astalli"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/A.csv"
SOURCE_FILE = "02-sources/02-Markdown/06_CHP-6_sec_i.md"
INDEX_QUOTE = '"Astalli (Pamfili), Camillo"'
SOURCE_QUOTE = (
    "The palace itself had been assigned to yet another substitute for a true papal nephew, "
    "Camillo Astalli, inevitably a relation of Donna Olimpia, who added to the general "
    "confusion by calling himself Pamfili."
)
RELATION_IDS = (
    "st-chp6-p148-astalli-assigned-papal-palace",
    "st-chp6-p148-astalli-relation-to-olimpia",
    "st-chp6-p148-astalli-substitute-nephew",
)

SOURCES = (
    {
        "citation": f"{BOOK_CITATION}, book index.",
        "location": "书后索引，A.csv#145；索引定位印刷页148",
        "summary": "索引以 Astalli (Pamfili), Camillo 为主项，定位至 p.148；此处仅作为书内定位依据，不单独证明人物生平或亲缘。",
        "quote": INDEX_QUOTE,
        "span": "A.csv#145",
        "doc_id": "patrons-and-painters-index",
        "file": INDEX_FILE,
    },
    {
        "citation": f"{BOOK_CITATION}, ch. 6, p. 148.",
        "location": "第6章，印刷页148；OCR L33–34",
        "summary": "哈斯克尔称纳沃纳广场宫殿曾分配给 Camillo Astalli，称其为 Donna Olimpia 的一位亲属但未说明亲缘，并说他称自己 Pamfili；同段语境将他与真正的 Prince Camillo Pamfili 区分。",
        "quote": SOURCE_QUOTE,
        "span": "lines 33–34; print p. 148",
        "doc_id": "patrons-and-painters",
        "file": SOURCE_FILE,
    },
)


def make_card() -> str:
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": item["citation"],
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

**中文：** 本卡记录哈斯克尔第6章 p.148 具名的 Camillo Astalli。哈斯克尔称纳沃纳广场宫殿曾分配给 Astalli，并将他描述为真正教皇侄辈的替代者；原文又称他是 Donna Olimpia 的一位亲属，但没有说明具体亲缘，并说他称自己为 Pamfili。这些均限于哈斯克尔在该段的叙述。本卡沿用 S3 已作出的身份区分，不与真正的 Prince Camillo Pamfili 合并；不补写书外生平。中文显示名为项目工作音译。

**English:** This card records Camillo Astalli, named on p. 148 of Haskell’s chapter 6. Haskell says that the Piazza Navona palace had been assigned to Astalli and characterizes him as a substitute for a true papal nephew. The passage also calls him a relation of Donna Olimpia without specifying the kinship and says that he called himself Pamfili. These statements are limited to Haskell’s account in this passage. The card follows the S3 identity decision and keeps Astalli distinct from the authentic Prince Camillo Pamfili; no external biography is added. The Chinese display name is a project working transliteration.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 本章具名形式 / Name used in the passage | Camillo Astalli | 第6章，印刷页148，L33–34 |
| 文中所述自称 / Self-designation reported in the passage | Pamfili | 第6章，印刷页148，L34；原文称其 calling himself Pamfili |

### 本章相关内容

纳沃纳广场的教皇宫曾分配给 Astalli；来源没有在该句指出分配行为的实施者。Donna Olimpia 的亲属关系也未注明具体程度。不得据此扩展为具体亲缘、正式头衔或 Astalli 对科尔托纳天顶画的委托。

The papal palace in Piazza Navona had been assigned to Astalli; the source does not name the assigning actor in that sentence. The passage does not specify the degree of his kinship with Donna Olimpia. These statements do not establish a particular kinship, formal title, or a commission by Astalli for Cortona’s ceiling fresco.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

以下3条直接 S2 关系候选留待 S6 逐项审查；“自称 Pamfili” statement 为非关系陈述：

{relations}

“替代真正教皇侄辈”保留为哈斯克尔的描述，不据此推定亲缘或将 Astalli 与 Pamfili 家族成员合并。

“Substitute for a true papal nephew” remains Haskell’s characterization; it does not establish kinship or justify merging Astalli with a member of the Pamfili family.
"""


def update_pending_warning(result: str, alignment_rows: list[dict]) -> str:
    pending = [row for row in alignment_rows if row.get("decision") == "new" and not row.get("ku_id")]
    candidate_rows = [row for row in pending if not row.get("external_source")]
    external_rows = [row for row in pending if row.get("external_source")]
    pending_groups = {
        sync.get_group(row.get("resolution_note", "")) or row.get("candidate_id", "")
        for row in candidate_rows
    }
    warning = (
        f"审计警告中的{sync.fmt(len(pending))}条待登记 `decision=new` alignment 行，含"
        f"{sync.fmt(len(candidate_rows))}条候选决定映射（{sync.fmt(len(pending_groups))}组）和"
        f"{sync.fmt(len(external_rows))}条外部身份记录。"
    )
    result, count = re.subn(
        r"审计警告中的[\d,]+条待登记 `decision=new` alignment 行，含[\d,]+条候选决定映射（[\d,]+组）和[\d,]+条外部身份记录。",
        warning,
        result,
        count=1,
    )
    assert count == 1, "could not refresh pending-alignment audit note"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the S3 Camillo Astalli person group in S4.")
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

    if (
        CARD_PATH.exists()
        and CARD_REL in accepted_text
        and any(row.get("ku_id") == KU_ID for row in manifest)
        and decisions.get(CANDIDATE, {}).get("ku_id") == KU_ID
    ):
        print("ALREADY REGISTERED: Camillo Astalli person group")
        return 0

    assert CANDIDATE in candidate_map and candidate_map[CANDIDATE]["suggested_type"] == "person"
    target = decisions[CANDIDATE]
    assert target["decision"] == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert CARD_PATH.exists(), "expected tracked pre-S4 draft card at the fixed object path"
    old_card = CARD_PATH.read_text(encoding="utf-8-sig")
    assert "created: 2026-09-09" in old_card and "updated: 2026-09-09" in old_card
    assert "Camillo Astalli" in old_card and "name_en:" not in old_card
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold() or row.get("canonical_name") == NAME_ZH)
        for row in manifest
    ), "same person already exists in the manifest"

    index_text = (ROOT / INDEX_FILE).read_bytes().decode("gbk")
    source_text = " ".join((ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig").split())
    assert INDEX_QUOTE in index_text and "Astalli" in index_text[index_text.index(INDEX_QUOTE):index_text.index(INDEX_QUOTE) + 80]
    assert " ".join(SOURCE_QUOTE.split()) in source_text

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = [
        row for row in statements.values()
        if CANDIDATE in (row.get("subject_candidate_id"), row.get("object_candidate_id"))
    ]
    direct_ids = {row["statement_id"] for row in direct}
    assert direct_ids == set(RELATION_IDS) | {"st-chp6-p148-astalli-uses-pamfili-name"}
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is True for sid in RELATION_IDS)
    assert statements["st-chp6-p148-astalli-uses-pamfili-name"]["qualifiers"].get("relation_candidate") is False

    planned_alignment = [dict(row) for row in alignments]
    planned_target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
    planned_target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; the existing unaccepted draft card was revised in place."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
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
    result_text = update_pending_warning(result_text, planned_alignment)

    process_entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Camillo Astalli 人物组登记（{DATE}）

`cand-0144`（A.csv#145，索引定位 p.148）按 S3 组 `{GROUP}` 登记为[卡米洛·阿斯塔利人物卡](../../../04-knowledge/units/persons/camillo-astalli.md)。第6章 p.148 明确具名 Camillo Astalli，称纳沃纳广场教皇宫曾分配给他，称他为 Donna Olimpia 的一位亲属但未说明具体亲缘，并记述他称自己 Pamfili。依照 S3，Astalli 不与真正的 Prince Camillo Pamfili 合并；不补外部生平，也不据书中关系陈述预先建立正式边。仓库原有同路径草稿未列入 accepted.yml 或 ku-manifest.csv，本次原位升级并登记，不创建重复卡。

3条直接 S2 关系候选 `{RELATION_IDS[0]}`、`{RELATION_IDS[1]}`、`{RELATION_IDS[2]}` 留待 S6；“自称 Pamfili” statement 为非关系陈述。本次未写入 `relations.csv`。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip() + process_entry

    result_note = (
        f"\n\n### S3→S4 person：Camillo Astalli（{DATE}）\n\n"
        "`cand-0144`→[卡米洛·阿斯塔利人物卡](../units/persons/camillo-astalli.md)。"
        "以第6章 p.148 原文和索引定位登记 source-local 身份；3条直接关系候选留待 S6，未新增正式关系。"
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
        print("dry-run passed: S3 new-person group contains only cand-0144 and has no existing KU mapping")
        print("verified source name, self-designation, index locator, and three direct relation-candidate statements")
        print(f"existing legacy draft will be revised in place; manifest={len(manifest):,}->{len(planned_manifest):,}")
        print(f"registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
        print("planned writes: person card, accepted.yml, ku-manifest.csv, alignment.csv, process record, result")
        print("relations.csv remains unchanged; field-fact rows will be reviewed through build_field_facts.py before apply")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Camillo Astalli registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
