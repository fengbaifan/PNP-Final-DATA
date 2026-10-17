from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import s3_reuse_sassoferrato_candidates_20261017 as summary_tools
import register_s4_valmarana_cluster_batch_20261015 as card_writer

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

GROUP = "new-person:alexander-great-68fcc5120d"
MEMBERS = ("cand-3442", "cand-9593")
KU_ID = "units/persons/alexander-the-great"
CARD_PATH = "04-knowledge/units/persons/alexander-the-great.md"
DATE = "2026-10-17"
ANCHOR = "s3-s4-person-alexander-the-great-20261017"
NAME_ZH = "亚历山大大帝"
NAME_EN = "Alexander the Great"
DIRECT_RELATIONS = (
    "st-chp10-p282-rapparini-alexander-comparison",
    "st-chp10-p313-pittoni-history-series-for-schulenburg",
    "st-chp8-p228-sebastiano-proposal-failed",
)
SOURCES = (
    card_writer.source(
        "1", "10", "01_CHP-1_sec_ii.md", "46",
        "celebrate the glories of Alexander the Great",
        "哈斯克尔以王室委托颂扬 Alexander the Great 的题材说明单一主题系列；这是概括性例子。",
    ),
    card_writer.source(
        "8", "228", "08_CHP-8_sec_ii.md", "207",
        "must represent Alexander the Great",
        "哈斯克尔称 Conti 要求 Sebastiano Ricci 画两幅以 Alexander the Great 为题的历史画，但因报价过高而未实施。",
    ),
    card_writer.source(
        "10", "282", "10_CHP-10_intro.md", "142",
        "comparing him to Alexander the Great",
        "哈斯克尔称 Rapparini 常将其主人 Johann Wilhelm 与 Alexander the Great 比较；这是哈斯克尔的叙述。",
    ),
    card_writer.source(
        "10", "313", "10_CHP-10_sec_ii.md", "78",
        "Scipio and Alexander the Great, Polyxena and Iphigenia.",
        "哈斯克尔把 Alexander the Great 列为 Pittoni 为 Schulenburg 创作的系列画题材之一，没有给出单件作品题名。",
    ),
)

DESCRIPTION_ZH = (
    "本书第1章以王室委托颂扬 Alexander the Great 为概括性例子；第8章记述 Sebastiano Ricci 曾受要求创作以他为题的两幅历史画，"
    "但方案未实施；第10章提到 Rapparini 将 Johann Wilhelm 与他比较，并把他列为 Pittoni 为 Schulenburg 创作的系列画题材之一。"
    "本卡仅归并这些书内具名提及，不确认具体作品身份，也不把比较或题材陈述登记为正式关系。"
)
DESCRIPTION_EN = (
    "Chapter 1 uses royal commissions celebrating Alexander the Great as a general example. Chapter 8 says Sebastiano Ricci was asked to paint two history pictures "
    "featuring him, but the proposal came to nothing. Chapter 10 reports Rapparini’s comparison of Johann Wilhelm to Alexander and lists him among subjects in "
    "a Pittoni series for Schulenburg. This card consolidates only these named references in the book; it does not identify individual works or record the comparisons "
    "or subject references as formal relations."
)
BT = chr(96)


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_of(note):
    match = re.search(r"(?:^|; )group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label}; found {count}")
    return text.replace(old, new, 1)


def book_source(spec):
    return {
        "citation": card_writer.BOOK_CITATION,
        "location": f"第{spec['chapter']}章，印刷页{spec['page']}；OCR L{spec['lines']}",
        "sentence_summary": spec["summary"],
        "original_quotes": [{"source_span": f"lines {spec['lines']}", "text": spec["quote"]}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{spec['file']}",
            "source_span": f"lines {spec['lines']}; print p. {spec['page']}",
        },
    }


def make_card():
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": [book_source(spec) for spec in SOURCES],
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** {DESCRIPTION_ZH}

**English:** {DESCRIPTION_EN}

### 名称

规范英文名依照书内拼写 Alexander the Great。中文显示名采用通行译名“亚历山大大帝”；卡片不补写生卒、地域归属或其他外部生平信息。

The English name follows the spelling in the book. The Chinese display name uses the conventional rendering 亚历山大大帝. No dates, political affiliation, or other external biographical details are added.

### 身份边界

本卡指书中具名的 Alexander the Great，不代表 Ricci 未实施的绘画方案，也不把 Pittoni 系列拆成已确认的单件作品。第1章的王室委托概括性例子不构成具体关系端点。

This card refers to the named Alexander the Great in the book. It does not represent Ricci’s unrealized proposal or treat Pittoni’s series as separately identified works. The general royal-commission example in chapter 1 is not a specific relation endpoint.

## 关系与证据

本次没有新增正式关系。以下三条直接涉及该人物的 S2 关系候选留待 S6：{BT}{DIRECT_RELATIONS[0]}{BT}（Rapparini 将 Johann Wilhelm 与 Alexander 比较）；{BT}{DIRECT_RELATIONS[1]}{BT}（Pittoni 为 Schulenburg 创作的系列题材）；{BT}{DIRECT_RELATIONS[2]}{BT}（Ricci 未实施的绘画方案）。作品身份、语境及方向须在 S6 分别裁决。
"""


def update_process(text, stats, manifest_count):
    if f'<a id="{ANCHOR}"></a>' in text:
        return text
    registered_groups = sum(row["registered_groups"] for row in stats.values())
    pending_groups = sum(row["pending_groups"] for row in stats.values())
    pending_members = sum(row["pending_candidates"] for row in stats.values())
    registered_members = sum(row["new_candidates"] for row in stats.values()) - pending_members
    entry = f"""

<a id="{ANCHOR}"></a>

### S3→S4 person：Alexander the Great 跨章身份组登记（{DATE}）

cand-3442（第1章 p.10、第8章 p.228、第10章 p.282）与 cand-9593（第10章 p.313）按相同完整人名保留在 {GROUP}，共映射至[亚历山大大帝人物卡](../../../04-knowledge/units/persons/alexander-the-great.md)。两项均为人物候选；人物清单未见该全名或同义拼写对应的既有 KU。卡片仅登记书内具名身份，未补写外部生平。

来源摘录与句意分别记在卡片的四条 Haskell 来源项：第1章 p.10 为一般性王室委托例子；第8章 p.228 所述 Ricci 提案因报价过高而未实施；第10章 p.282 是 Haskell 对 Rapparini 比较 Johann Wilhelm 与 Alexander 的转述；第10章 p.313 列出 Pittoni 为 Schulenburg 创作的系列题材，未给单件作品题名。

三条直接 S2 关系候选 {BT}{DIRECT_RELATIONS[0]}{BT}、{BT}{DIRECT_RELATIONS[1]}{BT}、{BT}{DIRECT_RELATIONS[2]}{BT} 留待 S6；第1章概括性例子不转为人物关系。本次未新增正式关系。

S4 当前登记 {registered_groups:,} 组／{registered_members:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_members:,} 条映射；KU 总数 {manifest_count:,}。
"""
    return text.rstrip() + entry


def update_result(text, planned_alignment, planned_manifest, planned_stats):
    candidate_rows = [row for row in planned_alignment if not row.get("external_source")]
    registered_groups = sum(row["registered_groups"] for row in planned_stats.values())
    pending_groups = sum(row["pending_groups"] for row in planned_stats.values())
    pending_members = sum(row["pending_candidates"] for row in planned_stats.values())
    registered_members = sum(row["new_candidates"] for row in planned_stats.values()) - pending_members
    pending_new = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id"))
    pending_external = sum(1 for row in planned_alignment if row["decision"] == "new" and not row.get("ku_id") and row.get("external_source"))

    text = replace_once(
        text,
        "S4 已登记525组、映射656条成员候选；尚待登记4,279组、4,322条映射。",
        f"S4 已登记{registered_groups:,}组、映射{registered_members:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "S4 top-line counts",
    )
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,544 KU",
        f"| [KU 登记](../tables/ku-manifest.csv) | {len(planned_manifest):,} KU",
        "manifest count",
    )

    warning = re.compile(
        "审计警告中的[\\d,]+条待登记 " + re.escape(BT) + "decision=new" + re.escape(BT) +
        " alignment 行，含[\\d,]+条候选决定映射（[\\d,]+组）和[\\d,]+条外部身份记录。"
    )
    warning_text = (
        f"审计警告中的{pending_new:,}条待登记 {BT}decision=new{BT} alignment 行，含{pending_members:,}条候选决定映射"
        f"（{pending_groups:,}组）和{pending_external:,}条外部身份记录。"
    )
    text, count = warning.subn(warning_text, text, count=1)
    if count != 1:
        raise AssertionError(f"pending-new warning matches: {count}")

    start = text.find("| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |")
    end = text.find("\n\n本轮新增的 archive 身份组包括：", start)
    if start < 0 or end < 0:
        raise AssertionError("S3/S4 type summary table not found")
    text = text[:start] + summary_tools.type_table(planned_stats, candidate_rows) + text[end:]

    heading = "### S3→S4 person：Alexander the Great 跨章身份组登记（2026-10-17）"
    if heading not in text:
        text = text.rstrip() + f"""

{heading}

cand-3442 与 cand-9593 同属一个跨章人物身份组，已映射至[亚历山大大帝人物卡](../units/persons/alexander-the-great.md)。身份依据为第1章 p.10、第8章 p.228、第10章 pp.282、313 的书内全名；没有新增外部生平或身份标识。

Ricci 未实施的方案、Pittoni 系列题材及 Rapparini 的比较叙述所涉三条直接 S2 关系候选留待 S6；第1章的一般性例子不建边。本次未新增正式关系。

S4 当前登记 {registered_groups:,} 组／{registered_members:,} 条候选映射；待登记 {pending_groups:,} 组／{pending_members:,} 条映射；KU 总数 {len(planned_manifest):,}。
"""
    return text


def main():
    parser = argparse.ArgumentParser(description="Register Alexander the Great as one cross-chapter person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_map = {row["candidate_id"]: row for row in candidates}
    member_rows = [row for row in alignments if row["candidate_id"] in MEMBERS and not row.get("external_source")]
    card_path = ROOT / CARD_PATH
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    if card_path.exists() and len(member_rows) == len(MEMBERS) and all(row.get("ku_id") == KU_ID for row in member_rows):
        assert CARD_PATH in accepted_text and any(row["ku_id"] == KU_ID for row in manifest)
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}")
        return 0

    assert len(manifest) == 1544, f"unexpected manifest count: {len(manifest)}"
    assert len(alignments) == 12642, f"unexpected alignment count: {len(alignments)}"
    assert sum(1 for row in alignments if row.get("external_source")) == 235
    assert not card_path.exists() and CARD_PATH not in accepted_text
    assert set(candidate_map) >= set(MEMBERS)
    assert len(member_rows) == len(MEMBERS)
    assert all(candidate_map[cid]["suggested_type"] == "person" for cid in MEMBERS)
    assert {candidate_map[cid]["canonical_name"].split(" (", 1)[0] for cid in MEMBERS} == {NAME_EN}
    assert all(row["decision"] == "new" and not row.get("ku_id") and group_of(row["resolution_note"]) == GROUP for row in member_rows)
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    person_names = " ".join(
        row["canonical_name"] + " " + row["name_en"] + " " + row["card_path"]
        for row in manifest if row["type"] == "person"
    ).casefold()
    assert "alexander the great" not in person_names and "alessandro magno" not in person_names

    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in DIRECT_RELATIONS:
                statements[statement["statement_id"]] = statement
    assert set(statements) == set(DIRECT_RELATIONS)
    assert all((row.get("qualifiers") or {}).get("relation_candidate") is True for row in statements.values())
    for spec in SOURCES:
        source_path = ROOT / "02-sources" / "02-Markdown" / spec["file"]
        source_text = source_path.read_text(encoding="utf-8-sig")
        assert spec["quote"] in source_text, f"source excerpt missing from {spec['file']}"

    planned_alignment = [dict(row) for row in alignments]
    for row in planned_alignment:
        if row["candidate_id"] in MEMBERS and not row.get("external_source"):
            row["ku_id"] = KU_ID
            row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
            row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1545
    planned_stats = summary_tools.compute_stats(planned_alignment, candidates)
    assert (
        sum(row["registered_groups"] for row in planned_stats.values()),
        sum(row["pending_groups"] for row in planned_stats.values()),
        sum(row["pending_candidates"] for row in planned_stats.values()),
    ) == (526, 4278, 4320)

    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(
        PROCESS_PATH.read_text(encoding="utf-8-sig"),
        planned_stats,
        len(planned_manifest),
    )
    result_text = update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        planned_alignment,
        planned_manifest,
        planned_stats,
    )
    card_text = make_card()

    if args.dry_run:
        print(
            f"dry-run passed: group={GROUP} members={','.join(MEMBERS)} ku={KU_ID} "
            f"registered_groups=526 mapped_candidates=658 pending_groups=4278 pending_candidates=4320 "
            f"manifest_after={len(planned_manifest)} alignment_after={len(planned_alignment)}"
        )
        print("planned writes: card, accepted.yml, ku-manifest.csv, alignment.csv, process/knowledge.md, result")
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        f"applied: group={GROUP} ku={KU_ID} members={len(MEMBERS)} "
        f"registered_groups=526 mapped_candidates=658 pending_groups=4278 pending_candidates=4320 "
        f"manifest={len(planned_manifest)} alignment={len(planned_alignment)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
