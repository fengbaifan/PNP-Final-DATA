from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
TABLES = ROOT / "04-knowledge" / "tables"
sys.path.insert(0, str(PROCESS_DIR))

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as table_helpers
import register_s4_work_second_scuola_scheme_20261020 as s4_helpers

DATE = "2026-10-22"
ANCHOR = "s4-s5-s6-chp8-p223-ruffo-chapel-20261022"
PROCESS_PATH = PROCESS_DIR / "knowledge.md"
STAGES_PATH = PROCESS_DIR / "stages.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
SOURCE_CH8 = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE_CH6 = "02-sources/02-Markdown/06_CHP-6_sec_v.md"
CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)."

SPECS = [
    {
        "candidate": "cand-6559",
        "group": "sg3-place-cand-6559",
        "ku_id": "units/places/church-of-s-lorenzo-in-damaso",
        "card_path": "04-knowledge/units/places/church-of-s-lorenzo-in-damaso.md",
        "name_zh": "圣洛伦佐·因·达马索教堂",
        "name_en": "Church of S. Lorenzo in Damaso",
        "source_file": SOURCE_CH6,
        "line": "40",
        "quote": "Ottoboni’s titular church of S. Lorenzo in Damaso",
        "summary": "第6章称 S. Lorenzo in Damaso 为 Pietro Ottoboni 的 titular church；第8章另称鲁福的礼拜堂位于该教堂中。",
        "anchor": ANCHOR,
    },
    {
        "candidate": "cand-7728",
        "group": "sg3-place-cand-7728",
        "ku_id": "units/places/ruffo-chapel-s-lorenzo-in-damaso",
        "card_path": "04-knowledge/units/places/ruffo-chapel-s-lorenzo-in-damaso.md",
        "name_zh": "鲁福枢机礼拜堂",
        "name_en": "Ruffo Chapel at S. Lorenzo in Damaso",
        "source_file": SOURCE_CH8,
        "line": "144–145",
        "quote": "The rich chapel which Nicola Salvi built for him in S.\nLorenzo in Damaso was decorated by Sebastiano Cbnca and Corrado Giaquinto",
        "summary": "第8章称 Nicola Salvi 为 Cardinal Tommaso Ruffo 在 S. Lorenzo in Damaso 建造了一座礼拜堂，并称 Sebastiano Conca 和 Corrado Giaquinto 装饰该空间。印刷页将 OCR 的 Cbnca 校读为 Conca。",
        "anchor": ANCHOR,
    },
]


def make_sources(spec: dict) -> list[dict]:
    if spec["candidate"] == "cand-6559":
        return [
            {
                "citation": CITATION,
                "location": "第6章，印刷页165；来源转录 L40。",
                "sentence_summary": "Haskell称 S. Lorenzo in Damaso 为 Pietro Ottoboni 的 titular church。",
                "original_quotes": [{"source_span": "line 40; print p. 165", "text": spec["quote"]}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_CH6, "source_span": "line 40; print p. 165"},
            },
            {
                "citation": CITATION,
                "location": "第8章，印刷页223；来源转录 L144–145。",
                "sentence_summary": "Haskell称鲁福的礼拜堂位于 S. Lorenzo in Damaso；本卡将教堂与礼拜堂作为不同地点记录。",
                "original_quotes": [{"source_span": "lines 144–145; print p. 223; PDF physical p. 25", "text": "The rich chapel which Nicola Salvi built for him in S.\nLorenzo in Damaso"}],
                "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_CH8, "source_span": "lines 144–145; print p. 223; PDF physical p. 25"},
            },
        ]
    return [
        {
            "citation": CITATION,
            "location": "第8章，印刷页223；来源转录 L144–145；PDF物理页25。",
            "sentence_summary": spec["summary"],
            "original_quotes": [{"source_span": "lines 144–145; print p. 223; PDF physical p. 25", "text": spec["quote"]}],
            "evidence_ref": {"doc_id": "patrons-and-painters", "source_file": SOURCE_CH8, "source_span": "lines 144–145; print p. 223; PDF physical p. 25"},
        }
    ]


def make_card(spec: dict) -> str:
    title = f"{spec['name_zh']}（{spec['name_en']}）"
    frontmatter = {
        "title": title,
        "name_en": spec["name_en"],
        "type": "place",
        "evidence_status": "source_backed",
        "sources": make_sources(spec),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    if spec["candidate"] == "cand-6559":
        body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔称为 S. Lorenzo in Damaso 的教堂。第6章将其称作 Pietro Ottoboni 的 titular church；第8章称 Cardinal Tommaso Ruffo 的礼拜堂位于该教堂中。此处仅保存原书所述的教堂身份与语境，不延伸为当代机构或建筑状态的核验。

**English:** This unit records the church Haskell names as S. Lorenzo in Damaso. Chapter 6 calls it Pietro Ottoboni’s titular church; chapter 8 places Cardinal Tommaso Ruffo’s chapel within it. The card preserves the church identity and contexts reported in the book and does not verify a present-day institution or building state.

### 基本信息

| 字段 | 值 | 依据 |
|---|---|---|
| 地点性质 | 教堂；Haskell称其为 Ottoboni 的 titular church。 | S1；第6章 p.165 L40。 |

## 关系与证据

### 身份与外部链接

本卡依据原书登记；本批未核验同粒度外部权威身份记录。

### 关系记录
"""
    else:
        body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔在第8章所称、为 Cardinal Tommaso Ruffo 建造于 S. Lorenzo in Damaso 内的礼拜堂。原书称 Nicola Salvi 为建造者，并称 Sebastiano Conca 与 Corrado Giaquinto 装饰该空间；个别装饰作品没有在此句中识别。名称为描述性工作名，礼拜堂与所在教堂分别登记。

**English:** This unit records the chapel Haskell describes in chapter 8 as built for Cardinal Tommaso Ruffo within S. Lorenzo in Damaso. He names Nicola Salvi as its builder and Sebastiano Conca and Corrado Giaquinto as decorators; no individual decorative works are identified in this sentence. The display name is descriptive, and the chapel is registered separately from its host church.

### 基本信息

| 字段 | 值 | 依据 |
|---|---|---|
| 地点性质 | 室内礼拜堂（interior chapel）。 | S1；第8章 p.223 L144–145。 |

### 营建参与者

| 字段 | 值 | 依据 |
|---|---|---|
| 建造者 | Nicola Salvi。 | S1；第8章 p.223 L144。 |
| 装饰者 | Sebastiano Conca；印本校读，OCR转录作 Cbnca。 | S1；第8章 p.223 L145；PDF物理页25。 |
| 装饰者 | Corrado Giaquinto。 | S1；第8章 p.223 L145。 |

## 关系与证据

### 身份与外部链接

本卡为原书所述空间的来源限定登记；本批未核验同粒度外部权威身份记录。

### 关系记录
"""
    return f"---\n{fm}---\n\n{body}"


def insert_accepted(text: str) -> str:
    lines = text.splitlines()
    for spec in SPECS:
        entry = f"- {spec['card_path']}"
        assert entry not in lines
        at = next((i for i, line in enumerate(lines) if line.startswith("- 04-knowledge/units/") and line[2:] > spec["card_path"]), next((i for i, line in enumerate(lines) if line == "claims:"), len(lines)))
        lines.insert(at, entry)
    return "\n".join(lines) + "\n"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp.replace(path)


def write_csv_utf8(path: Path, fieldnames, rows) -> None:
    import csv

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the chapter 8 Ruffo chapel and host church in S4, with a targeted S2 split.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = table_helpers.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = table_helpers.read_csv(ALIGNMENT_PATH)
    _, candidates = table_helpers.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    statements = table_helpers.load_statements()
    statement_by_id = {row["statement_id"]: row for row in statements}
    source8 = (ROOT / SOURCE_CH8).read_text(encoding="utf-8-sig")
    source6 = (ROOT / SOURCE_CH6).read_text(encoding="utf-8-sig")
    assert "The rich chapel which Nicola Salvi built for him in S.\nLorenzo in Damaso was decorated by Sebastiano Cbnca and Corrado Giaquinto" in source8
    assert SPECS[0]["quote"] in source6
    assert "CHP-8.pdf physical page 25" in statement_by_id["st-chp8-p223-conca-decorated-chapel"]["qualifiers"]["ocr_corrections"][0]["basis"]

    for spec in SPECS:
        candidate = candidate_by_id[spec["candidate"]]
        rows = [r for r in alignments if r.get("candidate_id") == spec["candidate"] and not r.get("external_source")]
        assert candidate.get("suggested_type") == "place"
        assert len(rows) == 1 and rows[0].get("decision") == "new" and not rows[0].get("ku_id")
        assert table_helpers.get_group(rows[0].get("resolution_note", "")) == spec["group"]
        group = [r for r in alignments if not r.get("external_source") and r.get("decision") == "new" and table_helpers.get_group(r.get("resolution_note", "")) == spec["group"]]
        assert [r.get("candidate_id") for r in group] == [spec["candidate"]]
        assert not (ROOT / spec["card_path"]).exists()
        assert not any(r.get("ku_id") == spec["ku_id"] or r.get("card_path") == spec["card_path"] for r in manifest)
        assert not any(r.get("type") == "place" and r.get("name_en", "").casefold() == spec["name_en"].casefold() for r in manifest)

    salvi = statement_by_id["st-chp8-p223-salvi-built-chapel"]
    assert salvi["subject_candidate_id"] == "cand-2347" and salvi["object_candidate_id"] == "cand-7728"
    assert salvi["qualifiers"].get("relation_candidate") is True
    salvi = json.loads(json.dumps(salvi))
    salvi["predicate"] = "salvi_built_chapel_for_ruffo"
    salvi["original_quote"] = "The rich chapel which Nicola Salvi built for him"
    salvi["qualifiers"].update({
        "source_line_start": 144,
        "source_line_end": 144,
        "claim": "Haskell reports that Nicola Salvi built a rich chapel for Cardinal Tommaso Ruffo.",
        "qualification": "The statement preserves the builder and beneficiary in Haskell’s wording; it does not assert a formal commission. The chapel’s location and decoration are handled separately.",
        "mentioned_candidate_ids": ["cand-2347", "cand-2304", "cand-7728"],
        "relation_candidate_note": "Builder and beneficiary are reported in one source-defined construction claim. The controlled relation vocabulary has no exact place-builder predicate; do not substitute created_by, erected_by, entrusted_to_build or commissioned_by.",
    })
    new_statement = {
        "statement_id": "st-chp8-p223-chapel-part-of-san-lorenzo",
        "segment_id": "chp-8:08_CHP-8_sec_ii:l140-150",
        "subject_candidate_id": "cand-7728",
        "object_candidate_id": "cand-6559",
        "predicate": "part_of",
        "qualifiers": {
            "source_line_start": 144,
            "source_line_end": 145,
            "printed_page": 223,
            "pdf_physical_page": 25,
            "claim": "Haskell locates Ruffo’s rich chapel in S. Lorenzo in Damaso.",
            "speaker": "Haskell",
            "text_layer": "body",
            "qualification": "The chapel is an interior space recorded separately from the host church; the source gives no finer architectural boundary.",
            "mentioned_candidate_ids": ["cand-7728", "cand-6559"],
            "relation_candidate": True,
            "relation_candidate_note": "The source locates the interior chapel in the named church; part_of expresses the source-supported interior-space relation without equating the chapel with the whole church.",
        },
        "original_quote": "The rich chapel which Nicola Salvi built for him in S.\nLorenzo in Damaso",
        "origin": "book",
        "source_file": SOURCE_CH8,
    }
    assert new_statement["statement_id"] not in statement_by_id
    assert new_statement["original_quote"] in source8
    planned_statements = []
    for row in statements:
        if row["statement_id"] == salvi["statement_id"]:
            planned_statements.append(salvi)
            planned_statements.append(new_statement)
        else:
            planned_statements.append(row)

    planned_alignments = [dict(row) for row in alignments]
    for spec in SPECS:
        row = next(r for r in planned_alignments if r.get("candidate_id") == spec["candidate"] and not r.get("external_source"))
        row["ku_id"] = spec["ku_id"]
        row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
        row["resolution_note"] += f" S4 registration: existing S3 new group {spec['group']} maps to {spec['ku_id']}; the church and interior chapel remain distinct place units."
    planned_manifest = list(manifest) + [
        {"ku_id": s["ku_id"], "type": "place", "canonical_name": s["name_zh"], "name_en": s["name_en"], "source_task": TASK, "card_path": s["card_path"]}
        for s in SPECS
    ]
    accepted_text = insert_accepted(ACCEPTED_PATH.read_text(encoding="utf-8-sig"))
    primary_rows = [r for r in planned_alignments if r.get("candidate_id") in candidate_by_id and not r.get("external_source")]
    primary_by_candidate: dict[str, dict] = {}
    for row in primary_rows:
        cid = row["candidate_id"]
        assert cid not in primary_by_candidate, f"duplicate primary S3 rows: {cid}"
        primary_by_candidate[cid] = row
    new_groups: dict[str, list[dict]] = {}
    for row in primary_rows:
        if row.get("decision") == "new":
            group = table_helpers.get_group(row.get("resolution_note", ""))
            assert group
            new_groups.setdefault(group, []).append(row)
    totals = {
        "new_candidates": sum(len(rows) for rows in new_groups.values()),
        "new_groups": len(new_groups),
        "registered_groups": 0,
        "registered_members": 0,
        "pending_groups": 0,
        "pending_members": 0,
    }
    for rows in new_groups.values():
        mapped = [r.get("ku_id", "") for r in rows]
        if all(mapped):
            assert len(set(mapped)) == 1
            totals["registered_groups"] += 1
            totals["registered_members"] += len(rows)
        else:
            assert not any(mapped)
            totals["pending_groups"] += 1
            totals["pending_members"] += len(rows)
    before_queue = s4_helpers.compute_direct_queue(candidate_by_id, alignments, statements)
    after_queue = s4_helpers.compute_direct_queue(candidate_by_id, planned_alignments, planned_statements)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]

    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    stages_text = STAGES_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    assert ANCHOR not in process_text and ANCHOR not in result_text
    entry = f"""

<a id="{ANCHOR}"></a>
### S3沿用／S4／S5／S6：第八章 p.223 鲁福礼拜堂与 S. Lorenzo in Damaso（{DATE}）

**S3与对象边界。** 沿用既有 `new` 身份组：`cand-6559`（`sg3-place-cand-6559`）是第6章与第8章所称的 S. Lorenzo in Damaso 教堂；`cand-7728`（`sg3-place-cand-7728`）是第8章所述教堂内部的鲁福礼拜堂。两者各为单成员地点组；本批不重开 S3，也不作外部建筑身份核验。

**S2定向原子化。** 将 `st-chp8-p223-salvi-built-chapel` 收窄为 Nicola Salvi 为 Cardinal Tommaso Ruffo 建造礼拜堂的来源陈述；礼拜堂位于 S. Lorenzo in Damaso 的位置拆为新候选 `st-chp8-p223-chapel-part-of-san-lorenzo`。装饰者陈述保持原位。新statement复用既有 `cand-7728` 与 `cand-6559`，不新增 mention 或改变 S3 决定。此为定向修订，不增加 S2 独立语义复核分子；S2 statement 和关系候选分母各增加1。

**S4登记与S5字段。** 新增两条映射：`cand-6559`→`units/places/church-of-s-lorenzo-in-damaso`、`cand-7728`→`units/places/ruffo-chapel-s-lorenzo-in-damaso`。教堂卡记录第6章的 titular church 语境；礼拜堂卡分列地点性质、建造者 Nicola Salvi、装饰者 Sebastiano Conca 和 Corrado Giaquinto，共5条由 Haskell 原书支持的字段。Conca 姓名按扫描印刷页25校读；OCR原样及校读依据保留。未加入外部来源。

**S6逐候选裁决。**

| S2 statement | 决定 | 去向与理由 |
|---|---|---|
| `st-chp8-p223-salvi-built-chapel` | pending | 原书报告 Salvi 建造礼拜堂并为 Ruffo 建造。当前受控词表无精确的地点建造者关系；不以 `created_by`、`erected_by`、`entrusted_to_build` 或 `commissioned_by` 替代。S2原文范围和S5字段保留。 |
| `st-chp8-p223-conca-decorated-chapel` | pending | 原书称 Conca 装饰礼拜堂，但词表没有装饰者谓词；不改写为创作者关系。 |
| `st-chp8-p223-giaquinto-decorated-chapel` | pending | 原书称 Giaquinto 装饰礼拜堂，但词表没有装饰者谓词；不改写为创作者关系。 |
| `st-chp8-p223-chapel-part-of-san-lorenzo` | formal | `rel-1454 part_of`：礼拜堂→S. Lorenzo in Damaso 教堂。只表达原书称该内部空间位于教堂中，不推断更精细的建筑边界。 |

三条谓词缺口候选明确记为 pending，因当前无可用受控谓词，不写入 `relations.csv`；formal `part_of` 边写入关系表。定向卡片预览与渲染仅涉及上述两张地点卡。
"""
    entry += f"\n\n批后 S4（按主决定行统计）：已登记 {totals['registered_groups']:,}/{totals['new_groups']:,} 组、{totals['registered_members']:,}/{totals['new_candidates']:,} 条映射；待登记 {totals['pending_groups']:,} 组／{totals['pending_members']:,} 条映射。直接端点队列由 {before_queue['groups']:,} 组／{before_queue['members']:,} 条映射降至 {after_queue['groups']:,} 组／{after_queue['members']:,} 条映射。\n"
    process_text = process_text.rstrip() + entry + "\n"
    stage_entry = f"""

### {DATE}：第八章 p.223 端点触发的S2原子化修订

修订 `st-chp8-p223-salvi-built-chapel`，将建造者及为 Ruffo 建造的陈述与礼拜堂在 S. Lorenzo in Damaso 内的位置分开；新增 `st-chp8-p223-chapel-part-of-san-lorenzo`，端点复用既有 `cand-7728`、`cand-6559`。引用 CHP-8.pdf 物理页25核对，确认OCR `Cbnca` 的印刷读法为 `Conca`。本次定向修订不计入S2独立语义复核分子；S2 statement 和 S6候选分母各增加1，第八章当前分母加1。原章序复核游标不变。
"""
    stages_text = stages_text.rstrip() + stage_entry + "\n"
    result_entry = f"""

### S3沿用／S4／S5／S6：第八章 p.223 鲁福礼拜堂与所在教堂（{DATE}）

沿用两个既有 S3 `new` 地点组，登记教堂与其内部的鲁福礼拜堂为不同 KU。将原有建造陈述与地点关系拆分，礼拜堂→教堂的 `part_of` 裁为 formal（`rel-1454`）；建造者及两位装饰者候选因缺少精确受控谓词均记 pending，不强套创作、委托或建造谓词。新增5条 Haskell 原书支持字段，Conca 拼写按扫描页校读；未添加外部身份核验。详情见[知识过程](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。

批后状态：S2 statement 与关系候选分母分别增加1，独立复核分子不变；S3决定不变；S4新增2组／2条映射；S5字段抽取待单独预览与写入；S6本批4条裁决（1 formal、3 pending）。
"""
    result_text = result_text.replace("更新日期：2026-10-22。", "更新日期：2026-10-22。" + result_entry, 1)
    cards = [(ROOT / s["card_path"], make_card(s)) for s in SPECS]

    if args.dry_run:
        print("dry-run passed: both single-member S3 new place groups are eligible for S4")
        print("source quotations checked against chapter 6 and chapter 8; printed p.223 image confirms Conca")
        print("S2 planned: narrow the Salvi claim and add one chapel-to-church part_of candidate")
        print(f"S4 totals from primary S3 rows: registered={totals['registered_groups']}/{totals['new_groups']} groups, {totals['registered_members']}/{totals['new_candidates']} mappings; pending={totals['pending_groups']}/{totals['pending_members']}")
        print(f"direct endpoint queue: {before_queue['groups']}/{before_queue['members']} -> {after_queue['groups']}/{after_queue['members']} groups/mappings")
        print("S6 planned: rel-1454 part_of formal; builder and two decorator candidates pending due to predicate gaps")
        print("S5 card rows planned=5; enrichment remains unchanged until build_field_facts.py preview is reviewed")
        print("planned writes: 2 cards, 2 alignment mappings, manifest, accepted.yml, S2 JSONL, process and result records")
        return 0

    for path, content in cards:
        path.write_text(content, encoding="utf-8-sig", newline="\n")
    write_csv_utf8(MANIFEST_PATH, manifest_fields, planned_manifest)
    table_helpers.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    write_jsonl(STATEMENTS_PATH, planned_statements)
    ACCEPTED_PATH.write_text(accepted_text, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8", newline="\n")
    STAGES_PATH.write_text(stages_text, encoding="utf-8", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8", newline="\n")
    print(f"applied: S4 +2 groups/{len(SPECS)} mappings; S2 +1 statement/+1 relation candidate; direct queue {before_queue['groups']}->{after_queue['groups']} groups")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
