from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml
import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
GROUP = "archive-group-4a4d65fbc201"
CANDIDATE = "cand-8789"
PUBLISHER_CANDIDATE = "cand-12425"
KU_ID = "units/archives/venice-scalzi-pamphlet-1734"
CARD_PATH = "04-knowledge/units/archives/venice-scalzi-pamphlet-1734.md"
SOURCE_FILE = "09_CHP-9_sec_ii.md"
QUOTE = (
    "5 Risposta ad un amico sopra certi riflessi falsamente concepiti contra la Chiesa dei "
    "Carmelitani Scalzi a Venezia—a pamphlet of 32 pages by M.A.—published by Luigi Pavini "
    "in 1734 (Marciana, Misc. 1135, n. 3) referred to by Ferrari, 1882."
)
NAME_ZH = "答一位友人：论针对威尼斯赤足加尔默罗会教堂的若干错误见解"
NAME_EN = (
    "Reply to a Friend Concerning Certain Misconceived Views Against the Church of the "
    "Discalced Carmelites in Venice"
)


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def card_text():
    source = {
        "citation": card_writer.BOOK_CITATION,
        "location": "第九章；印刷页269；注5；OCR L95",
        "sentence_summary": (
            "第九章注5列出一份32页、作者标识为M.A.的小册子，报告其由Luigi Pavini于1734年出版，"
            "给出Biblioteca Marciana馆藏号，并说明该书目参见Ferrari 1882。"
        ),
        "original_quotes": [{"source_span": "lines L95", "text": QUOTE}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{SOURCE_FILE}",
            "source_span": "lines L95; print p. 269, note 5",
        },
    }
    frontmatter = {
        "title": f"《{NAME_ZH}》（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "pamphlet",
        "evidence_status": "source_backed",
        "sources": [source],
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    evidence = (
        "[第九章 p.269 注5原书转录](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)"
        "（L95）"
    )
    body = f"""## 内容

### 描述

**中文：** 第九章第269页注5列出一份32页小册子，原题为 *Risposta ad un amico sopra certi riflessi falsamente concepiti contra la Chiesa dei Carmelitani Scalzi a Venezia*，作者标识为 M.A.；脚注称其由 Luigi Pavini 于1734年出版，馆藏号为 Biblioteca Marciana, Misc. 1135, n. 3，并注明参见 Ferrari 1882。以上均为 Haskell 的书内书目报告；小册子与 Ferrari 1882 未独立查阅。中文题名为描述性工作译名。

**English:** Chapter 9, p. 269, note 5 lists a 32-page pamphlet under the original title *Risposta ad un amico sopra certi riflessi falsamente concepiti contra la Chiesa dei Carmelitani Scalzi a Venezia*, with M.A. as the author form. The note says it was published by Luigi Pavini in 1734, gives the locator Biblioteca Marciana, Misc. 1135, no. 3, and refers to Ferrari, 1882. These are Haskell's bibliographic statements; neither the pamphlet nor Ferrari 1882 was independently consulted. The Chinese title is a descriptive working translation.

### 名称与版本

| 字段 | 内容 | 依据 |
|---|---|---|
| 中文描述性工作题名 | {NAME_ZH} | {evidence}；非原题 |
| 英文描述性工作题名 | {NAME_EN} | {evidence}；非本书所载英文题名 |
| 原题名 | *Risposta ad un amico sopra certi riflessi falsamente concepiti contra la Chiesa dei Carmelitani Scalzi a Venezia* | {evidence} |

### 基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 文献类型 | 32页小册子（pamphlet） | {evidence} |
| 作者标识 | M.A.；仅记录脚注所列形式，未辨明个人身份 | {evidence} |
| 出版者 | Luigi Pavini | {evidence}；出版者身份候选已映射至[Luigi Pavini人物卡](../persons/luigi-pavini.md) |
| 出版年 | 1734年 | {evidence} |
| 馆藏定位 | Biblioteca Marciana, Misc. 1135, n. 3 | {evidence}；为 Haskell 所引定位，未独立核对馆藏记录 |
| 引用来源 | Ferrari, 1882 | {evidence}；Haskell 注明参见该书，本卡未独立查阅或确认具体书目条目 |

### 本书相关内容

第9章第269页正文讨论1732年一位匿名撰稿人为教堂开支辩护；脚注5为该段提供上述小册子书目定位。脚注给出的作者形式是 M.A.，本卡不据相邻叙述将其还原为具名个人。

## 关系与证据

### 关系记录

本卡未新增正式关系。S2 候选陈述 st-chp9-p269-n05 明确记载 Luigi Pavini 为出版者；该端点已映射到其人物卡，出版关系留待 S6 按正式关系契约审查。馆藏定位只按 Haskell 报告保留；本批未新增或确认 held_by 正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def count_new_groups(alignment_rows):
    new_rows = [
        row for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
    ]
    groups = defaultdict(list)
    for row in new_rows:
        group = card_writer.get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {
        group: rows for group, rows in groups.items()
        if any(row.get("ku_id") for row in rows)
    }
    mapped = sum(bool(row.get("ku_id")) for rows in registered.values() for row in rows)
    return new_rows, groups, registered, mapped


def update_progress(process, result, alignment_rows, manifest_rows):
    new_rows, groups, registered, mapped = count_new_groups(alignment_rows)
    pending_groups = len(groups) - len(registered)
    pending_members = len(new_rows) - mapped
    process_pattern = re.compile(
        r"已登记\s*[\d,]+\s*组、\s*[\d,]+\s*条成员映射，尚待登记\s*[\d,]+\s*组、\s*[\d,]+\s*条。"
    )
    process, process_count = process_pattern.subn(
        f"已登记{len(registered):,}组、{mapped:,}条成员映射，尚待登记"
        f"{pending_groups:,}组、{pending_members:,}条。",
        process,
        count=1,
    )
    assert process_count == 1, "process current S4 totals did not match"
    result_pattern = re.compile(
        r"S4 已登记\s*[\d,]+\s*组、映射\s*[\d,]+\s*条成员候选；尚待登记\s*[\d,]+\s*组、\s*[\d,]+\s*条映射。"
    )
    result, result_count = result_pattern.subn(
        f"S4 已登记{len(registered):,}组、映射{mapped:,}条成员候选；"
        f"尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        result,
        count=1,
    )
    assert result_count == 1, "result current S4 totals did not match"
    manifest_pattern = re.compile(
        r"(\|\s*\[KU 登记\]\(\.\./tables/ku-manifest\.csv\)\s*\|\s*)[\d,]+ KU"
    )
    result, manifest_count = manifest_pattern.subn(
        lambda match: f"{match.group(1)}{len(manifest_rows):,} KU",
        result,
        count=1,
    )
    assert manifest_count == 1, "result manifest total did not match"
    return process, result, len(registered), mapped, pending_groups, pending_members


def main():
    parser = argparse.ArgumentParser(
        description="Register the 1734 Scalzi pamphlet as the archive endpoint for the Luigi Pavini S2 relation candidate."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_candidate = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    rel_card_path = "04-knowledge/units/archives/venice-scalzi-pamphlet-1734.md"
    card_path = ROOT / rel_card_path
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1192, f"unexpected manifest size: {len(manifest)}"
    assert CANDIDATE in candidates and candidates[CANDIDATE]["suggested_type"] == "archive"
    alignment = alignment_by_candidate[CANDIDATE]
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert card_writer.get_group(alignment["resolution_note"]) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new"
        and card_writer.get_group(row["resolution_note"]) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not card_path.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == rel_card_path for row in manifest)
    assert rel_card_path not in accepted

    publisher = alignment_by_candidate[PUBLISHER_CANDIDATE]
    assert publisher["decision"] == "new" and publisher.get("ku_id") == "units/persons/luigi-pavini"
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    statement = [row for row in statements if row.get("statement_id") == "st-chp9-p269-n05"]
    assert len(statement) == 1 and statement[0].get("object_candidate_id") == CANDIDATE
    assert statement[0].get("qualifiers", {}).get("relation_candidate") is True
    assert "published by Luigi Pavini" in statement[0].get("original_quote", "")
    source_path = ROOT / "02-sources" / "02-Markdown" / SOURCE_FILE
    assert QUOTE in source_path.read_text(encoding="utf-8-sig")

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[CANDIDATE]["ku_id"] = KU_ID
    planned_by_id[CANDIDATE]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "archive",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": rel_card_path,
    })
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    updated_process, updated_result, registered, mapped, pending_groups, pending_members = update_progress(
        process_text, result_text, planned_alignment, planned_manifest
    )
    process_note = (
        "\n\n### S4 archive：Luigi Pavini 直接关系端点小册子登记（2026-10-16）\n\n"
        f"{CANDIDATE}（{GROUP}）映射至 [1734年威尼斯赤足加尔默罗会小册子卡]"
        "(../../../04-knowledge/units/archives/venice-scalzi-pamphlet-1734.md)。"
        "第九章 p.269 注5记录原题、32页、M.A.作者形式、Luigi Pavini为出版者、"
        "Biblioteca Marciana, Misc. 1135, n. 3 馆藏定位，并注明参见 Ferrari 1882；"
        "小册子与 Ferrari 均未独立查阅。出版者候选 cand-12425 已映射至 Luigi Pavini 人物卡，"
        "该出版关系仍待 S6 审查；馆藏定位不在本批升级为正式关系。相关短引候选 cand-8777 保持 undecided，"
        "未并入本卡。登记前 archive 直接关系对象有一个 new 身份组待映射，本批完成该组；"
        f"S4 累计登记{registered}组/{mapped}条成员候选，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### archive：1734年威尼斯赤足加尔默罗会小册子 S4 登记（2026-10-16）\n\n"
        f"{CANDIDATE} 映射至 [小册子 archive 卡](../units/archives/venice-scalzi-pamphlet-1734.md)。"
        "卡片保留 Haskell 脚注所给原题、M.A.作者形式、出版者与馆藏定位；中文/英文展示题名为工作译名。"
        "原件和 Ferrari 1882 未独立查阅；Pavini 出版关系及馆藏关系留待 S6，不新增正式边。"
        f"全书 S4 当前登记{registered}组/{mapped}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    updated_process += process_note
    updated_result += result_note

    if args.dry_run:
        print(f"S4 archive registration dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"direct relation statement=st-chp9-p269-n05; publisher endpoint -> {publisher['ku_id']}")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}")
        print(
            f"registered={registered:,} groups/{mapped:,} candidates; "
            f"pending={pending_groups:,} groups/{pending_members:,} candidates"
        )
        print("source quote, unique S3 group, endpoint mapping, and destination uniqueness checked; no files changed")
        return 0

    card_path.write_text(card_text(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > rel_card_path),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {rel_card_path}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(updated_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(updated_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={registered}/{mapped}; pending={pending_groups}/{pending_members}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
