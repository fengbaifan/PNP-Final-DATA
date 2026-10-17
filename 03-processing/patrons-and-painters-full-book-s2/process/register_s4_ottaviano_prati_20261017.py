from __future__ import annotations

import argparse
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
ANCHOR = "s3-s4-person-ottaviano-prati-20261017"
CANDIDATES = ("cand-6090",)
GROUP = "new-person:ottaviano-prati-f3bfa7e4a0"
KU_ID = "units/persons/ottaviano-prati"
CARD_REL = "04-knowledge/units/persons/ottaviano-prati.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "奥塔维亚诺·普拉蒂"
NAME_EN = "Ottaviano Prati"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)
SECTION_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
SECTION_QUOTE = (
    "3 Blunt and Cooke, pp. 102 if In the Galleria N azionale di Arte Antica in Rome "
    "is a signed portrait of Monsignor Ottaviano Prati, who at different times was "
    "Governor of Benevento and Viterbo-Moroni, LXI, p. 216, and CH, p. 363. 4 Gigli passim."
)
NAME_QUOTE = "a signed portrait of Monsignor Ottaviano Prati"
OFFICE_QUOTE = "who at different times was Governor of Benevento and Viterbo"
RELATION_IDS = (
    "st-chp5-note-p131-n3-prati-portrait",
    "st-chp5-note-p131-n3-prati-governor-benevento",
    "st-chp5-note-p131-n3-prati-governor-viterbo",
)


def make_card() -> str:
    source = {
        "citation": f"{BOOK_CITATION}, ch. 5, p. 131, n. 3.",
        "location": "第5章第一节，印刷页131注3；OCR L147",
        "sentence_summary": (
            "注3称罗马 Galleria Nazionale di Arte Antica 藏有 Ottaviano Prati 的签名肖像，"
            "并称他曾在不同时期任 Benevento 与 Viterbo 总督；未给任职年代或肖像作者。"
        ),
        "original_quotes": [
            {"source_span": "L147; print p. 131 n. 3", "text": NAME_QUOTE},
            {"source_span": "L147; print p. 131 n. 3", "text": OFFICE_QUOTE},
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": SECTION_FILE,
            "source_span": "L147; print p. 131 n. 3",
        },
    }
    index_source = {
        "citation": BOOK_CITATION,
        "location": "书后人名索引 P 项；OCR 转录 L2552，印本页码未核准",
        "sentence_summary": "人名索引以倒置形式列出 Prati, Monsignor Ottaviano；转录行末含 OCR 字串 13 m G。",
        "original_quotes": [
            {"source_span": "L2552", "text": "Prati, Monsignor Ottaviano"},
        ],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": "02-sources/02-Markdown/22_CHP-22Index_intro.md",
            "source_span": "L2552",
        },
    }
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [source, index_source],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    pending = "\n".join(f"- `{sid}`" for sid in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡记录哈斯克尔第5章 p.131 注3具名的 Ottaviano Prati。注释以 “Monsignor” 称呼他；中文显示名为项目工作音译。

**English:** This card records Ottaviano Prati, named in footnote 3 on p. 131 of Haskell’s chapter 5. The footnote styles him “Monsignor.” The Chinese display name is a project working transliteration.

### 名称

| 字段 | 值 | 证据 |
|---|---|---|
| 本章具名形式 / Name used in the passage | Monsignor Ottaviano Prati | 第5章第一节，印刷页131注3，L147；S1 |
| 姓名 / Personal name | Ottaviano Prati | 第5章第一节，印刷页131注3，L147；S1 |
| 教会称谓 / Ecclesiastical honorific | Monsignor | 第5章第一节，印刷页131注3，L147；S1 |
| 书后索引形式 / Index heading | Prati, Monsignor Ottaviano | L2552；S2 |

### 本章相关内容

**中文：** 哈斯克尔注3称罗马 Galleria Nazionale di Arte Antica 藏有 Prati 的一幅签名肖像，并记述他曾在不同时期任 Benevento 与 Viterbo 总督。注释未给任职年代或肖像作者。

**English:** Haskell’s footnote 3 reports a signed portrait of Prati in Rome’s Galleria Nazionale di Arte Antica and says that he served as governor of Benevento and Viterbo at different times. It gives no dates for those appointments or name for the portrait’s artist.

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

以下书内关系候选留待 S6 逐项裁决：

{pending}

肖像的作者和年代未在该注中给出。此卡保留哈斯克尔的转述范围，不将书内候选关系写成已裁决正式边。
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
    parser = argparse.ArgumentParser(description="Register the Ottaviano Prati person group in S4.")
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
        and all(decisions.get(cid, {}).get("ku_id") == KU_ID for cid in CANDIDATES)
    ):
        print("ALREADY REGISTERED: Ottaviano Prati person group")
        return 0

    assert all(cid in candidate_map and candidate_map[cid]["suggested_type"] == "person" for cid in CANDIDATES)
    target_rows = [decisions[cid] for cid in CANDIDATES]
    assert all(row["decision"] == "new" and not row.get("ku_id") for row in target_rows)
    assert all(sync.get_group(row.get("resolution_note", "")) == GROUP for row in target_rows)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == list(CANDIDATES)
    assert not CARD_PATH.exists(), "target card path already exists; inspect before proceeding"
    assert CARD_REL not in accepted_text
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert not any(
        row.get("type") == "person"
        and (row.get("name_en", "").casefold() == NAME_EN.casefold() or row.get("canonical_name") == NAME_ZH)
        for row in manifest
    ), "same person already exists in the manifest"

    source_text = (ROOT / SECTION_FILE).read_text(encoding="utf-8-sig")
    assert SECTION_QUOTE in source_text
    assert NAME_QUOTE in source_text and OFFICE_QUOTE in source_text
    assert candidate_map[CANDIDATES[0]]["candidate_source_ref"].endswith("#L147")

    statements = {row["statement_id"]: row for row in sync.load_statements()}
    direct = [
        row for row in statements.values()
        if any(cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")) for cid in CANDIDATES)
    ]
    assert {row["statement_id"] for row in direct} == set(RELATION_IDS)
    assert all(statements[sid]["qualifiers"].get("relation_candidate") is True for sid in RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row.get("candidate_id") in CANDIDATES and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: the source-local person group {GROUP} maps to one KU, {KU_ID}."

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

### S3→S4 person：Ottaviano Prati 书内人物身份组登记（{DATE}）

`cand-6090` 是单成员 S3 组 `{GROUP}`。第5章 p.131 注3以 “Monsignor Ottaviano Prati” 具名；脚注转述一幅 Prati 的签名肖像，并称他曾在不同时期任 Benevento、Viterbo 总督，但未给任职年代或肖像作者。该书内锚点足以登记来源内人物身份，不提供外部生平或完整身份链。

现登记为[奥塔维亚诺·普拉蒂人物卡](../../../04-knowledge/units/persons/ottaviano-prati.md)，仅映射 `{CANDIDATES[0]}` 一个候选。项目已有的 `Ottaviano Ottoviani` 是另一个全名与独立来源的对象；本组不因共享名字 Ottaviano 而合并。另一个候选 `cand-6091` 是签名肖像的独立 work 组，未在本次 S4 登记。

`{RELATION_IDS[0]}`、`{RELATION_IDS[1]}` 与 `{RELATION_IDS[2]}` 保持 S2 关系候选，留待 S6；不修改 `relations.csv`。本次没有新增外部身份记录或 S5 字段核验。

S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(planned_manifest))}。
"""
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig").rstrip() + process_entry

    result_note = (
        f"\n\n### S3→S4 person：Ottaviano Prati（{DATE}）\n\n"
        "`cand-6090` 由单成员 new-person 组登记为一张人物卡，依据为第5章 p.131 注3的全名锚点。"
        "签名肖像及两处总督任职仍各自保留为 S2 关系候选，未新增正式关系；Ottaviano Ottoviani 保持分立。"
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
        print("dry-run passed: cand-6090 is the sole member of the S3 new-person group")
        print("verified the p.131 n.3 name/source anchor, manifest identity separation, and three direct S2 relation candidates")
        print(f"manifest={len(manifest):,}->{len(planned_manifest):,}; registered={totals['registered_groups']}/{totals['registered_members']}")
        print(f"pending={totals['pending_groups']}/{totals['pending_members']}; relations.csv unchanged")
        print("planned writes: one bilingual person card, accepted.yml, ku-manifest.csv, one alignment mapping, process record, result")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    sync.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: Ottaviano Prati person group registered; manifest={len(planned_manifest)}; pending={totals['pending_groups']}/{totals['pending_members']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
