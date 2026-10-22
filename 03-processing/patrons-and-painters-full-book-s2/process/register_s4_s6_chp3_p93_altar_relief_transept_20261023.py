#!/usr/bin/env python3
"""Register the Chapter 3 p.93 altar, relief, and left-transept endpoints.

Default mode builds a targeted preview without touching project files. Apply
only after reviewing the printed counts and candidate-to-KU mapping.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
SOURCE_FILE = "02-sources/02-Markdown/03_CHP-3_sec_iv.md"
SOURCE_PATH = ROOT / SOURCE_FILE
PROCESS_ANCHOR = "s4-s5-s6-chp3-p93-altar-relief-transept-20261023"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)."
)
SOURCE_SPAN = "Chapter 3, printed p. 93 L185; PDF physical p. 35"
STATEMENT_IDS = {
    "st-chp3-seciv-l179-187-relief-part-of-1697-altar",
    "st-chp3-seciv-l179-187-left-transept-part-of-s-ignazio",
}
NEW_KUS = [
    {
        "candidate_id": "cand-5451",
        "group": "workgrp-fceb5486119b13",
        "ku_id": "units/works/pozzo-1697-altar-s-ignazio-left-transept",
        "type": "work",
        "canonical_name": "圣依纳爵堂左耳堂1697年祭坛",
        "name_en": "1697 Altar in the Left Transept of S. Ignazio",
        "card_path": "04-knowledge/units/works/pozzo-1697-altar-s-ignazio-left-transept.md",
        "summary": "Haskell称Andrea Pozzo于1697年设计了S. Ignazio左耳堂的一座祭坛；Pierre Legros以一件贡扎加升天主题浅浮雕完成该祭坛。",
        "quote_key": "altar",
        "description_zh": (
            "本卡登记Haskell第3章p.93所述S. Ignazio左耳堂内的1697年祭坛。"
            "原文称Andrea Pozzo设计该祭坛，Pierre Legros以一件描绘Blessed Luigi Gonzaga升天主题的浅浮雕完成该祭坛。"
            "此处仅记录书内叙述，不据此推断祭坛现存状态或独立核实其作品身份。"
        ),
        "description_en": (
            "This unit records the 1697 altar in the left transept of S. Ignazio described by Haskell in Chapter 3, p. 93. "
            "The passage says Andrea Pozzo designed it and Pierre Legros completed it with a bas-relief representing "
            "the Assumption of Blessed Luigi Gonzaga. This records the book's account and does not establish the altar's "
            "present condition or an independently verified work identity."
        ),
        "name_value": "S. Ignazio左耳堂内的1697年祭坛；描述性工作名称",
        "basic_rows": [
            ("作品类型", "祭坛（altar）", "S1；第3章 p.93 L185"),
            ("设计年份", "1697年；仅为原书所述设计年份，不据此推断完工或现存状态", "S1；statement st-chp3-seciv-l179-187-pozzo-designed-1697-altar；第3章 p.93 L185"),
        ],
    },
    {
        "candidate_id": "cand-5452",
        "group": "workgrp-94bba391cc10ad",
        "ku_id": "units/works/assumption-of-blessed-luigi-gonzaga-bas-relief-s-ignazio",
        "type": "work",
        "canonical_name": "路易吉·贡扎加升天主题浅浮雕",
        "name_en": "Bas-Relief of the Assumption of Blessed Luigi Gonzaga",
        "card_path": "04-knowledge/units/works/assumption-of-blessed-luigi-gonzaga-bas-relief-s-ignazio.md",
        "summary": "Haskell称Pierre Legros以一件描绘Blessed Luigi Gonzaga升天主题的浅浮雕完成S. Ignazio左耳堂内的1697年祭坛。",
        "quote_key": "altar",
        "description_zh": (
            "本卡以描述性工作名称登记Haskell第3章p.93所述的浅浮雕。"
            "原文称该浮雕描绘Blessed Luigi Gonzaga升天主题，并称Pierre Legros以此完成Pozzo于1697年设计的左耳堂祭坛。"
            "原文未给该浮雕的正式题名或现存地点；本卡不作外部作品身份核验。"
        ),
        "description_en": (
            "This unit uses a descriptive working name for the bas-relief described by Haskell in Chapter 3, p. 93. "
            "The passage says that it represented the Assumption of Blessed Luigi Gonzaga and that Pierre Legros used it "
            "to complete Pozzo's 1697 altar in the left transept. No formal title or present location is supplied, and "
            "the work has not been externally identified."
        ),
        "name_value": "描绘Blessed Luigi Gonzaga升天主题的浅浮雕；描述性工作名称，不是原文正式题名",
        "basic_rows": [
            ("作品类型", "浅浮雕（bas-relief）", "S1；第3章 p.93 L185"),
            ("来源所述主题", "Blessed Luigi Gonzaga升天", "S1；statement st-chp3-seciv-l179-187-assumption-relief-represents-luigi-gonzaga；第3章 p.93 L185"),
        ],
    },
    {
        "candidate_id": "cand-5459",
        "group": "sg3-place-cand-5459",
        "ku_id": "units/places/left-transept-s-ignazio",
        "type": "place",
        "canonical_name": "圣依纳爵堂左耳堂",
        "name_en": "Left Transept of S. Ignazio",
        "card_path": "04-knowledge/units/places/left-transept-s-ignazio.md",
        "summary": "Haskell将Pozzo于1697年设计的祭坛定位于S. Ignazio左耳堂。",
        "quote_key": "left_transept",
        "description_zh": (
            "本卡登记Haskell第3章p.93所称S. Ignazio教堂的左耳堂。"
            "原文以该空间定位Pozzo于1697年设计的祭坛；此处为描述性空间名称，不补入原文未提供的独立专名或现状信息。"
        ),
        "description_en": (
            "This unit records the left transept of S. Ignazio named by Haskell in Chapter 3, p. 93. "
            "The passage uses this space to locate Pozzo's 1697 altar. The name is descriptive; no independent proper "
            "name or present-condition claim is added."
        ),
        "name_value": "S. Ignazio左耳堂；描述性空间名称",
        "basic_rows": [
            ("空间类型", "教堂内部空间；左侧耳堂（left transept）", "S1；第3章 p.93 L185"),
        ],
    },
]

RELATION_SPECS = [
    {
        "statement_id": "st-chp3-seciv-l179-187-pozzo-designed-1697-altar",
        "subject": "units/works/pozzo-1697-altar-s-ignazio-left-transept",
        "object": "units/persons/andrea-pozzo",
        "predicate": "designed_by",
        "time": "1697",
        "role": "设计者",
        "scope": "Haskell directly says Padre Pozzo designed the altar in 1697. This records the design attribution and year stated in the passage; it does not assert completion or present condition.",
        "note": "The altar remains distinct from the earlier great altar project discussed on p. 92.",
    },
    {
        "statement_id": "st-chp3-seciv-l179-187-legros-completed-altar-with-relief",
        "subject": "units/works/pozzo-1697-altar-s-ignazio-left-transept",
        "object": "units/persons/pierre-ii-legros",
        "predicate": "contributed_by",
        "time": "",
        "role": "以浅浮雕完成祭坛",
        "scope": "Haskell says Legros completed the altar with an appealing bas-relief. This records his stated contribution to the altar's completion; it does not identify him as the altar's designer or claim that he alone made the relief.",
        "note": "Mapped from the source's completion wording; no broader authorship is inferred.",
    },
    {
        "statement_id": "st-chp3-seciv-l179-187-assumption-relief-represents-luigi-gonzaga",
        "subject": "units/works/assumption-of-blessed-luigi-gonzaga-bas-relief-s-ignazio",
        "object": "units/persons/aloysius-gonzaga",
        "predicate": "has_subject",
        "time": "",
        "role": "表现主题",
        "scope": "Haskell describes the bas-relief as representing the Assumption of Blessed Luigi Gonzaga. This records its represented subject, not a portrait or an independently established formal title.",
        "note": "The existing person KU is reused; no separate work title is inferred from the subject phrase.",
    },
    {
        "statement_id": "st-chp3-seciv-l179-187-pozzo-altar-located-left-transept",
        "subject": "units/works/pozzo-1697-altar-s-ignazio-left-transept",
        "object": "units/places/left-transept-s-ignazio",
        "predicate": "located_at",
        "time": "",
        "role": "原文所述建筑位置",
        "scope": "Haskell places the 1697 altar in the left transept of S. Ignazio. This records the historical location stated in the passage and makes no claim about present survival.",
        "note": "The immediately named left transept is kept distinct from the right-transept chapel and from the Gesù.",
    },
    {
        "statement_id": "st-chp3-seciv-l179-187-relief-part-of-1697-altar",
        "subject": "units/works/assumption-of-blessed-luigi-gonzaga-bas-relief-s-ignazio",
        "object": "units/works/pozzo-1697-altar-s-ignazio-left-transept",
        "predicate": "part_of",
        "time": "",
        "role": "祭坛组成部分",
        "scope": "Haskell says Legros completed the altar with an appealing bas-relief. This records the relief as a component used to complete the altar; it does not assert the relief's separate installation history or present location.",
        "note": "The relation is limited to the source's explicit altar-with-relief construction.",
    },
    {
        "statement_id": "st-chp3-seciv-l179-187-left-transept-part-of-s-ignazio",
        "subject": "units/places/left-transept-s-ignazio",
        "object": "units/places/s-ignazio",
        "predicate": "part_of",
        "time": "",
        "role": "建筑内部空间",
        "scope": "The source calls this space the left transept of S. Ignazio. This records the transept as part of that church and does not claim a present-day architectural survey.",
        "note": "The church candidate is already mapped to the S. Ignazio place KU and remains distinct from the Gesù chapel.",
    },
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]], bytes]:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw[len(bom):].decode("utf-8")
    with io.StringIO(text, newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader), bom


def csv_bytes(path: Path, fields: list[str], rows: list[dict[str, str]], bom: bytes) -> bytes:
    old = path.read_bytes()
    line_ending = "\r\n" if b"\r\n" in old else "\n"
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore", lineterminator=line_ending)
    writer.writeheader()
    writer.writerows(rows)
    return bom + out.getvalue().encode("utf-8")


def read_text(path: Path) -> tuple[str, bytes, str]:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw[len(bom):].decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text, bom, newline


def text_bytes(text: str, bom: bytes) -> bytes:
    return bom + text.encode("utf-8")


def read_jsonl(path: Path) -> tuple[list[dict], bytes, str]:
    raw = path.read_bytes()
    bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
    text = raw[len(bom):].decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return rows, bom, newline


def append_jsonl_bytes(path: Path, rows: list[dict], bom: bytes, newline: str) -> bytes:
    old = path.read_bytes()
    if old and not old.endswith((b"\n", b"\r")):
        old += newline.encode("ascii")
    suffix = "".join(json.dumps(row, ensure_ascii=False) + newline for row in rows)
    return old + suffix.encode("utf-8")


def load_field_builder():
    root_text = str(ROOT)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    path = ROOT / "scripts" / "build_field_facts.py"
    spec = importlib.util.spec_from_file_location("build_field_facts_targeted_batch", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load field extraction interface: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_card(spec: dict, quote: str) -> str:
    frontmatter = {
        "title": f"{spec['canonical_name']}（{spec['name_en']}）",
        "name_en": spec["name_en"],
        "type": spec["type"],
        "evidence_status": "source_backed",
        "sources": [
            {
                "citation": BOOK_CITATION,
                "location": "第3章，印刷页93，L185；PDF物理页35。",
                "sentence_summary": spec["summary"],
                "original_quotes": [
                    {
                        "source_span": "line 185; printed p. 93; PDF physical p. 35",
                        "text": quote,
                    }
                ],
                "evidence_ref": {
                    "doc_id": "patrons-and-painters",
                    "source_file": SOURCE_FILE,
                    "source_span": SOURCE_SPAN,
                },
            }
        ],
        "created": "2026-10-23",
        "updated": "2026-10-23",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    evidence = "S1；第3章 p.93 L185"
    body = [
        "## 内容",
        "",
        "### 描述",
        "",
        f"**中文：** {spec['description_zh']} [第3章 p.93](../../../{SOURCE_FILE})。",
        "",
        f"**English:** {spec['description_en']} [Chapter 3, p. 93](../../../{SOURCE_FILE}).",
        "",
        "### 名称",
        "",
        "| 字段 | 内容 | 依据 |",
        "|---|---|---|",
        f"| 描述性名称 | {spec['name_value']} | {evidence} |",
        "",
        "### 基本信息",
        "",
        "| 字段 | 内容 | 依据 |",
        "|---|---|---|",
    ]
    body.extend(f"| {field} | {value} | {basis} |" for field, value, basis in spec["basic_rows"])
    body.extend(
        [
            "",
            "## 关系与证据",
            "",
            "### 身份入口",
            "",
            f"- **S3身份组：** {spec['group']}；候选：{spec['candidate_id']}；KU：{spec['ku_id']}。",
            "",
            "### 关系记录",
            "",
            "关系以正式关系表为准。",
            "",
            "### 关系候选入口",
            "",
            f"[全书 S2–S6 过程记录](../../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR})",
            "",
        ]
    )
    return f"---\n{fm}---\n\n" + "\n".join(body)


def read_alignment_main_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_candidate: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_candidate.setdefault(row.get("candidate_id", ""), []).append(row)
    result: dict[str, dict[str, str]] = {}
    for candidate_id, candidates in by_candidate.items():
        primary = [row for row in candidates if not row.get("external_source")]
        if len(primary) == 1:
            result[candidate_id] = primary[0]
    return result


def add_units_to_accepted(text: str, new_paths: list[str]) -> str:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.strip() == "units:"), None)
    if start is None:
        raise AssertionError("accepted.yml has no units section")
    end = start + 1
    while end < len(lines):
        stripped = lines[end].strip()
        if stripped and not lines[end].startswith((" ", "\t", "- ")):
            break
        end += 1
    unit_lines = [line for line in lines[start + 1:end] if line.startswith("- 04-knowledge/units/")]
    current = [line.strip()[2:] for line in unit_lines]
    current_set = set(current)
    duplicates = current_set.intersection(new_paths)
    if duplicates:
        raise AssertionError(f"accepted.yml already has new unit(s): {sorted(duplicates)}")
    newline = "\r\n" if any("\r\n" in line for line in lines) else "\n"
    block = lines[start + 1:end] + [f"- {path}{newline}" for path in new_paths]
    return "".join(lines[: start + 1] + block + lines[end:])


def update_results(text: str, newline: str, field_ids: list[str], relation_ids: list[str]) -> str:
    start_marker = "### 本轮进度与后续工作（2026-10-23）"
    next_marker = "### S4/S5/S6 archive：第10章 p.302"
    start = text.find(start_marker)
    end = text.find(next_marker, start + len(start_marker))
    if start < 0 or end < 0:
        raise AssertionError("could not isolate the current results block")
    fields = "、".join(field_ids)
    rels = "、".join(relation_ids)
    block_lines = [
        start_marker,
        "",
        (
            "本轮完成第19批S4/S5/S6关系端点工作：沿用既有S3 new组登记3个KU及3条候选映射，"
            "为新卡补录8条Haskell书内来源支持字段，并将6条直接关系候选逐项裁为formal；"
            "没有重开S3决定。逐项依据见[本批过程记录]"
            f"(../../03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR})。"
        ),
        "",
        (
            "**当前全书状态。** S0有832个源段（678 complete、154 excluded）。"
            "S2共15,247条statement，统一独立逐条复核9,573条（62.8%，尚未接收）；"
            "第七章1,146/1,264、第八章487/1,474；第3章1,173/1,183及第10–12章1,567/1,567的独立记录仍分开报告，均未接收；"
            "统一复核台账待按statement ID与来源版本核平。"
            "S3主决定覆盖12,390/12,410个候选，仍缺20项（person 16、institution 2、archive 2）；"
            "same=2,028、new=5,032（4,801组）、conflict=9、excluded=100、undecided=5,221（含622项类型边界未决）；"
            "另22项跨来源decision不同，须按来源与身份语义逐项复核，不直接视为身份冲突。"
            "S4已登记1,541/4,801组（32.1%）、1,758/5,032条候选映射（34.9%），待登记3,260组／3,274条映射。"
            f"S5有12,424条字段，1,634条unverified（本批新增字段：{fields}）。"
            "原始book-statements.jsonl中relation_candidate=true共10,472条；"
            "S6已裁决585/10,472条（365 formal、158 pending、62 rejected；5.6%），余9,887条；"
            f"relations.csv共1,585条（1,576 formal、9 pending；本批新增：{rels}）。"
            "339条关系候选至少缺一个S2端点候选ID（subject-only 46、object-only 221、both 72）。"
            "candidate-backlog共10条（9条完成、1条明确undecided，pending=0）。"
        ),
        "",
        (
            "本批新增2条S2原子关系statement，均引用既有mentions与第3章p.93 L185；"
            "统一S2独立复核分子不变。S5字段均来自Haskell书内原句；"
            "关系裁决限于设计、以浮雕完成祭坛、表现贡扎加升天主题、祭坛位置、浮雕组成祭坛及左耳堂属于教堂。"
            "此批不作外部作品身份核验，也不把S2定向补充分子并入独立审读。"
        ),
        "",
        "**后续工作规划。**",
        "",
        "1. **继续按关系解锁价值登记S4并同批裁决S6。** 优先从有直接S2关系、端点证据明确的S3既有new组中批量登记KU；每批完成受影响的全部直接关系候选去向。",
        "2. **定向补缺端点与关键S5字段。** 对缺少S2候选端点的关系回到具体来源段，补入原子statement并按新证据需要核对身份；字段只按明确缺口补足或记录待证条件。",
        "3. **继续分章S2独立语义审读。** 先核平statement ID与来源版本台账，再从第八章低覆盖段落连续推进；定向修订不计入独立复核分子。",
        "4. **S3仅在当前登记或新证据触发时重开。** 不启动全库S3重扫；触发时保留原决定与组号，记录改变判断的具体证据。",
        "5. **S4/S5/S6满足收口条件并完成全书审计后准备S7。** 知识发现与页面制作仍暂不开展。",
        "",
    ]
    new_block = newline.join(block_lines)
    return text[:start] + new_block + text[end:]


def make_process_record(field_records: list[dict], relation_rows: list[dict], newline: str) -> str:
    field_table = [
        "| enrichment ID | KU | 字段 | 状态 |",
        "|---|---|---|---|",
    ]
    field_table.extend(
        f"| {row['enrichment_id']} | {row['ku_id']} | {row['field']} | {row['evidence_status']} |"
        for row in field_records
    )
    s4_table = [
        "| 候选 | S3身份组 | S4 KU | 类型 |",
        "|---|---|---|---|",
    ]
    s4_table.extend(
        f"| {spec['candidate_id']} | {spec['group']} | {spec['ku_id']} | {spec['type']} |"
        for spec in NEW_KUS
    )
    s6_table = [
        "| S2关系候选 | 决定 | 正式关系 | 裁决依据 |",
        "|---|---|---|---|",
    ]
    for spec, row in zip(RELATION_SPECS, relation_rows, strict=True):
        s6_table.append(
            f"| {spec['statement_id']} | formal | {row['relation_id']} {spec['predicate']} | {spec['scope']} |"
        )
    lines = [
        "",
        f'<a id="{PROCESS_ANCHOR}"></a>',
        "### S4/S5/S6：第3章 p.93 左耳堂祭坛与贡扎加浮雕端点（2026-10-23）",
        "",
        "本批只沿用当前alignment.csv中的S3决定，不重开身份裁决。cand-5451、cand-5452与cand-5459分别保持既有new组；Pozzo、Legros、Aloysius Gonzaga与S. Ignazio均指向已登记KU。cand-1379的主决定仍为new并沿用已登记的Pierre II Legros KU；其外部身份行不替代主决定。",
        "",
        *s4_table,
        "",
        f"新增三张卡均以Haskell第3章印刷页93、L185为直接书内来源；未作外部作品身份核验。S5新增字段如下，共{len(field_records)}条，均为source_backed：",
        "",
        *field_table,
        "",
        "原段已含四条直接关系候选：Pozzo设计祭坛、Legros以浮雕完成祭坛、浮雕表现Blessed Luigi Gonzaga升天主题、祭坛位于左耳堂。新增两条S2原子statement：浮雕是该祭坛组成部分；左耳堂属于S. Ignazio。两条均复用既有mention/candidate，不新增mention，不计入独立S2审读。",
        "",
        *s6_table,
        "",
        "Legros的角色限于原文所述以浮雕完成祭坛，不推为祭坛设计者或浮雕唯一制作者；has_subject记录主题，不当作人物肖像或正式作品题名；part_of两边分别表达浮雕与祭坛的组成关系、耳堂与教堂的空间组成关系。六条关系均有第3章p.93 L185的Haskell书内证据。",
        "",
        f"批后：S2为9,573/15,247，独立复核分子不变；第3章独立章节覆盖为1,173/1,183。S3决定与分组未变。S4登记1,541/4,801组、1,758/5,032条映射；S5字段12,424条（1,634条unverified）；S6裁决585/10,472（365 formal、158 pending、62 rejected）；relations.csv为1,585条（1,576 formal、9 pending）。",
        "",
        "本批写入后的机械与定向卡片检查结果记于全书当前结果页；任何机械通过均不代表全书语义接收或S4–S6收口。",
        "",
    ]
    return newline.join(lines)


def make_stage_record(new_statements: list[dict], newline: str) -> str:
    lines = [
        "",
        "### S2定向补关系端点：第3章 p.93 左耳堂祭坛与浮雕（2026-10-23）",
        "",
        "为S4/S6直接端点工作定向补入两条原子关系statement，均定位到第3章印刷页93 L185并复用本段已有mentions。未改变实体候选、既有S3决定或身份组，也未把修订计入独立语义审读。",
        "",
        "| 新statement | 主体候选 | 客体候选 | 原子关系 |",
        "|---|---|---|---|",
    ]
    lines.extend(
        f"| {row['statement_id']} | {row['subject_candidate_id']} | {row['object_candidate_id']} | {row['qualifiers']['claim']} |"
        for row in new_statements
    )
    lines.extend(
        [
            "",
            "浮雕—祭坛关系以原文“Legros completed [the altar] with an appealing bas-relief”为依据；耳堂—教堂关系以“the left transept of S. Ignazio”为依据。S2统一复核分子维持9,573，第3章独立章节分母由1,181增至1,183。",
            "",
        ]
    )
    return newline.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the reviewed targeted batch")
    args = parser.parse_args()

    if SOURCE_PATH.is_file() is False:
        raise FileNotFoundError(SOURCE_PATH)
    source_text, _, _ = read_text(SOURCE_PATH)
    candidate_rows = list(csv.DictReader((TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="")))
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_path = TABLES / "alignment.csv"
    align_fields, alignment_rows, align_bom = read_csv(alignment_path)
    main_alignments = read_alignment_main_rows(alignment_rows)
    manifest_path = TABLES / "ku-manifest.csv"
    manifest_fields, manifest_rows, manifest_bom = read_csv(manifest_path)
    manifest_by_id = {row["ku_id"]: row for row in manifest_rows}
    statements_path = TABLES / "book-statements.jsonl"
    statements, statements_bom, statements_nl = read_jsonl(statements_path)
    statements_by_id = {row["statement_id"]: row for row in statements}
    relations_path = TABLES / "relations.csv"
    relations_fields, relation_rows, relations_bom = read_csv(relations_path)
    relation_ids_existing = {row["relation_id"] for row in relation_rows}
    relation_candidates_existing = {
        row.get("statement_id", "")
        for row in statements
        if row.get("qualifiers", {}).get("relation_candidate") is True
    }
    enrichment_path = TABLES / "enrichment.jsonl"
    old_enrichment, enrichment_bom, enrichment_nl = read_jsonl(enrichment_path)
    cards = {
        spec["card_path"]: make_card(
            spec,
            (
                statements_by_id["st-chp3-seciv-l179-187-pozzo-designed-1697-altar"]["original_quote"]
                .split(" The chapel in the right transect was only completed", 1)[0]
                if spec["quote_key"] == "altar"
                else "an altar in the left transept of S. Ignazio"
            ),
        )
        for spec in NEW_KUS
    }

    for spec in NEW_KUS:
        candidate_id = spec["candidate_id"]
        candidate = candidate_by_id.get(candidate_id)
        alignment = main_alignments.get(candidate_id)
        if candidate is None or alignment is None:
            raise AssertionError(f"missing candidate or primary alignment: {candidate_id}")
        if candidate.get("suggested_type") != spec["type"] or alignment.get("decision") != "new":
            raise AssertionError(f"unexpected S3 type/decision for {candidate_id}")
        note = alignment.get("resolution_note", "")
        group_match = re.search(r"(?<![A-Za-z0-9_-])group=([A-Za-z0-9_./:-]+)", note)
        if not group_match or group_match.group(1).rstrip(".,:;") != spec["group"]:
            raise AssertionError(f"S3 group changed for {candidate_id}")
        if alignment.get("ku_id"):
            raise AssertionError(f"{candidate_id} already has a KU mapping")
        if spec["ku_id"] in manifest_by_id or (ROOT / spec["card_path"]).exists():
            raise AssertionError(f"target KU/card already exists: {spec['ku_id']}")
    for candidate_id, expected_ku in {
        "cand-2034": "units/persons/andrea-pozzo",
        "cand-1379": "units/persons/pierre-ii-legros",
        "cand-5453": "units/persons/aloysius-gonzaga",
        "cand-5439": "units/places/s-ignazio",
    }.items():
        alignment = main_alignments.get(candidate_id)
        if alignment is None or alignment.get("ku_id") != expected_ku:
            raise AssertionError(f"existing endpoint mapping changed for {candidate_id}")
    for spec in RELATION_SPECS[:4]:
        if spec["statement_id"] not in relation_candidates_existing:
            raise AssertionError(f"expected direct S2 relation candidate is absent: {spec['statement_id']}")
    if any(row.get("statement_id") in {spec["statement_id"] for spec in RELATION_SPECS} for row in relation_rows):
        raise AssertionError("one or more target relation candidates already have an S6 relation row")
    if STATEMENT_IDS.intersection(statements_by_id):
        raise AssertionError(f"new S2 statement ID already exists: {sorted(STATEMENT_IDS.intersection(statements_by_id))}")
    if any(spec["statement_id"] in statements_by_id for spec in RELATION_SPECS[4:]):
        raise AssertionError("one or more planned new S2 statement IDs already exist")
    if any((ROOT / rel_path).exists() for rel_path in cards):
        raise AssertionError("one or more target card paths already exist")
    if not all(quote in source_text for quote in (
        "In 1697 Padre Pozzo designed an altar in the left transept of S. Ignazio",
        "an altar in the left transept of S. Ignazio",
    )):
        raise AssertionError("source quote did not match the current S2 source file")

    new_ku_rows = [
        {
            "ku_id": spec["ku_id"],
            "type": spec["type"],
            "canonical_name": spec["canonical_name"],
            "name_en": spec["name_en"],
            "source_task": TASK,
            "card_path": spec["card_path"],
        }
        for spec in NEW_KUS
    ]
    field_builder = load_field_builder()
    with tempfile.TemporaryDirectory(prefix="pnp-s4-s6-chp3-p93-") as temporary:
        temporary_root = Path(temporary)
        for rel_path, body in cards.items():
            target = temporary_root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8", newline="\n")
        original_base = field_builder.BASE
        field_builder.BASE = temporary_root
        try:
            field_records, source_registry, warnings, cards_with_tables = field_builder.extract_records(new_ku_rows)
        finally:
            field_builder.BASE = original_base
    if warnings or cards_with_tables != len(NEW_KUS):
        raise AssertionError(f"target field extraction warnings={warnings}, cards_with_tables={cards_with_tables}")
    if len(field_records) != 8 or any(row["evidence_status"] != "source_backed" for row in field_records):
        raise AssertionError(
            f"expected 8 source-backed fields, got {len(field_records)}; statuses="
            f"{[row['evidence_status'] for row in field_records]}"
        )
    if any(row["source_ids"] != ["haskell-1980-rev-ed"] for row in field_records):
        raise AssertionError("target field rows did not resolve to the existing Haskell source ID")
    field_builder.assign_ids(field_records, enrichment_path)
    existing_occurrences = {row.get("occurrence_id", "") for row in old_enrichment}
    if any(row["occurrence_id"] in existing_occurrences for row in field_records):
        raise AssertionError("target field occurrence collides with the existing enrichment ledger")

    new_statements = [
        {
            "statement_id": "st-chp3-seciv-l179-187-relief-part-of-1697-altar",
            "segment_id": "chp-3:03_CHP-3_sec_iv:l179-187",
            "subject_candidate_id": "cand-5452",
            "object_candidate_id": "cand-5451",
            "predicate": "part_of",
            "qualifiers": {
                "source_line_start": 185,
                "source_line_end": 185,
                "claim": "Haskell says Legros completed Pozzo's altar with an appealing bas-relief, recording the relief as a component of the altar.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative (lower-page text; no separate note number legible)",
                "print_page": 93,
                "pdf_physical_page": 35,
                "mentioned_candidate_ids": ["cand-5452", "cand-5451"],
                "relation_candidate": True,
                "relation_candidate_note": "The source says Legros completed the altar with the bas-relief; records the relief as part of the altar without asserting separate installation or present location.",
            },
            "original_quote": statements_by_id["st-chp3-seciv-l179-187-pozzo-designed-1697-altar"]["original_quote"].split(
                " The chapel in the right transect was only completed", 1
            )[0],
            "origin": "book",
            "source_file": SOURCE_FILE,
        },
        {
            "statement_id": "st-chp3-seciv-l179-187-left-transept-part-of-s-ignazio",
            "segment_id": "chp-3:03_CHP-3_sec_iv:l179-187",
            "subject_candidate_id": "cand-5459",
            "object_candidate_id": "cand-5439",
            "predicate": "part_of",
            "qualifiers": {
                "source_line_start": 185,
                "source_line_end": 185,
                "claim": "Haskell identifies the left transept as part of S. Ignazio.",
                "speaker": "Haskell",
                "text_layer": "authorial narrative (lower-page text; no separate note number legible)",
                "print_page": 93,
                "pdf_physical_page": 35,
                "mentioned_candidate_ids": ["cand-5459", "cand-5439"],
                "relation_candidate": True,
                "relation_candidate_note": "The locative phrase calls this transept the left transept of S. Ignazio.",
            },
            "original_quote": "the left transept of S. Ignazio",
            "origin": "book",
            "source_file": SOURCE_FILE,
        },
    ]
    for spec, statement in zip(RELATION_SPECS[4:], new_statements, strict=True):
        if spec["statement_id"] != statement["statement_id"]:
            raise AssertionError("S2 statement and S6 relation references do not align")

    matrix = yaml.safe_load((ROOT / "01-domain" / "relation-domain-range.yml").read_text(encoding="utf-8"))
    types = {row["ku_id"]: row["type"] for row in manifest_rows}
    types.update({row["ku_id"]: row["type"] for row in new_ku_rows})
    domain_range = matrix.get("domain_range", {})
    for spec in RELATION_SPECS:
        subject_type = types.get(spec["subject"], "")
        object_type = types.get(spec["object"], "")
        allowed = domain_range.get(spec["predicate"])
        if not allowed or subject_type not in allowed.get("domain", []) or object_type not in allowed.get("range", []):
            raise AssertionError(
                f"relation domain/range invalid: {spec['predicate']} {subject_type}->{object_type}"
            )
    last_relation_number = max(
        int(row["relation_id"].removeprefix("rel-"))
        for row in relation_rows
        if re.fullmatch(r"rel-\d+", row["relation_id"])
    )
    relation_rows_new = []
    for offset, spec in enumerate(RELATION_SPECS, 1):
        relation_id = f"rel-{last_relation_number + offset:04d}"
        if relation_id in relation_ids_existing:
            raise AssertionError(f"relation ID collision: {relation_id}")
        relation_rows_new.append(
            {
                "relation_id": relation_id,
                "subject_ku_id": spec["subject"],
                "object_ku_id": spec["object"],
                "predicate": spec["predicate"],
                "time": spec["time"],
                "role": spec["role"],
                "scope": spec["scope"],
                "origin": "book",
                "status": "formal",
                "source_id": "haskell-1980-rev-ed",
                "source_span": f"{SOURCE_SPAN}; statement={spec['statement_id']}",
                "source_file": SOURCE_FILE,
                "note": spec["note"],
            }
        )
    if set(STATEMENT_IDS) != {row["statement_id"] for row in new_statements}:
        raise AssertionError("planned S2 statement ID set changed")

    staged: dict[Path, bytes] = {}
    for spec, body in zip(NEW_KUS, cards.values(), strict=True):
        card_path = ROOT / spec["card_path"]
        staged[card_path] = body.encode("utf-8")

    for spec in NEW_KUS:
        if spec["candidate_id"] not in candidate_by_id:
            raise AssertionError(f"candidate disappeared: {spec['candidate_id']}")
    manifest_rows.extend(new_ku_rows)
    staged[manifest_path] = csv_bytes(manifest_path, manifest_fields, manifest_rows, manifest_bom)

    for spec in NEW_KUS:
        alignment = main_alignments[spec["candidate_id"]]
        alignment["ku_id"] = spec["ku_id"]
        alignment["resolution_note"] = (
            alignment["resolution_note"].rstrip()
            + f" S4 registration 2026-10-23: mapped existing S3 group {spec['group']} to {spec['ku_id']}."
        )
    staged[alignment_path] = csv_bytes(alignment_path, align_fields, alignment_rows, align_bom)

    accepted_text, accepted_bom, _ = read_text(ACCEPTED)
    staged[ACCEPTED] = text_bytes(
        add_units_to_accepted(accepted_text, [spec["card_path"] for spec in NEW_KUS]),
        accepted_bom,
    )
    staged[statements_path] = append_jsonl_bytes(statements_path, new_statements, statements_bom, statements_nl)
    relation_rows.extend(relation_rows_new)
    staged[relations_path] = csv_bytes(relations_path, relations_fields, relation_rows, relations_bom)
    staged[enrichment_path] = append_jsonl_bytes(enrichment_path, field_records, enrichment_bom, enrichment_nl)

    knowledge_path = PROCESS / "knowledge.md"
    knowledge_text, knowledge_bom, knowledge_nl = read_text(knowledge_path)
    if f'id="{PROCESS_ANCHOR}"' in knowledge_text:
        raise AssertionError("process anchor already exists")
    staged[knowledge_path] = text_bytes(
        knowledge_text.rstrip("\r\n") + make_process_record(field_records, relation_rows_new, knowledge_nl),
        knowledge_bom,
    )
    stages_path = PROCESS / "stages.md"
    stages_text, stages_bom, stages_nl = read_text(stages_path)
    staged[stages_path] = text_bytes(
        stages_text.rstrip("\r\n") + make_stage_record(new_statements, stages_nl),
        stages_bom,
    )

    results_text, results_bom, results_nl = read_text(RESULT)
    staged[RESULT] = text_bytes(
        update_results(
            results_text,
            results_nl,
            [row["enrichment_id"] for row in field_records],
            [row["relation_id"] for row in relation_rows_new],
        ),
        results_bom,
    )

    print(f"batch={PROCESS_ANCHOR}")
    print(f"registered_kus={len(NEW_KUS)} registered_mappings={len(NEW_KUS)}")
    print(f"source_backed_fields={len(field_records)} field_ids={','.join(row['enrichment_id'] for row in field_records)}")
    print(f"new_s2_statements={len(new_statements)} relation_candidates_decided={len(RELATION_SPECS)}")
    print(f"formal_relations={len(relation_rows_new)} relation_ids={','.join(row['relation_id'] for row in relation_rows_new)}")
    print(f"files_to_write={len(staged)}")
    for path in staged:
        print(f"  {path.relative_to(ROOT).as_posix()}")
    if not args.apply:
        print("preview only; pass --apply to write this targeted batch")
        return 0

    originals = {path: path.read_bytes() if path.exists() else None for path in staged}
    written: list[Path] = []
    try:
        for path, data in staged.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + ".batch-tmp")
            temporary.write_bytes(data)
            temporary.replace(path)
            written.append(path)
    except Exception:
        for path in reversed(written):
            old = originals[path]
            if old is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(old)
        raise
    print("apply complete; in-process rollback snapshots were held until all files were written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
