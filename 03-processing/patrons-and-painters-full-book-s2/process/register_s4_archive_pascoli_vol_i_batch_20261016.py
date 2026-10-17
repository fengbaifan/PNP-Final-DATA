from __future__ import annotations

import argparse
import json
import re
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

GROUP = "archive-group-31f7e821ab60"
CANDIDATE = "cand-4834"
VOLUME_II_CANDIDATE = "cand-4552"
KU_ID = "units/archives/lione-pascoli-vite-dei-pittori-vol-i"
CARD_PATH = "04-knowledge/units/archives/lione-pascoli-vite-dei-pittori-vol-i.md"
NAME_ZH = "利奥内·帕斯科利《现代画家、雕塑家与建筑师传》第一卷（1730）"
NAME_EN = "Lione Pascoli, Lives of Modern Painters, Sculptors and Architects, vol. I (1730)"

BIB_FILE = "21_CHP-21Bibliography.md"
CH1_FILE = "01_CHP-1.md"
CH7_FILE = "07_CHP-7_sec_i.md"
BIB_QUOTE = (
    "Pascoli, Lione: Vite de’ Pittori, Scultori ed Architetti moderni, I, 1730, and II, "
    "1736—facsimile edition published by R. Istituto d’Archeologia e Storia dell’Arte, Roma 1933."
)
CH1_QUOTE = "2 Pascoli, I, p. 93."
CH7_QUOTE = (
    "4 Pascoli, I, p. 127. Canini, who accompanied Cardinal Chigi on his visit to Paris in 1664, "
    "was also employed at the French court—Pascoli, II, p. 124."
)


def read_csv(path: Path):
    return card_writer.read_csv(path)


def write_csv(path: Path, fields, rows):
    return card_writer.write_csv(path, fields, rows)


def make_source(file: str, location: str, quote: str, summary: str, span: str):
    return {
        "citation": card_writer.BOOK_CITATION,
        "location": location,
        "sentence_summary": summary,
        "original_quotes": [{"source_span": span, "text": quote}],
        "evidence_ref": {
            "doc_id": "patrons-and-painters",
            "source_file": f"02-sources/02-Markdown/{file}",
            "source_span": span,
        },
    }


def card_text():
    sources = [
        make_source(
            BIB_FILE,
            "第21章书目；印刷页433；OCR L932",
            BIB_QUOTE,
            "书目将 Lione Pascoli 的作品列为第一卷（1730）和第二卷（1736），并记载一套由 R. Istituto d’Archeologia e Storia dell’Arte 于1933年在罗马出版的影印版。",
            "lines L932; print p. 433",
        ),
        make_source(
            CH1_FILE,
            "第1章；印刷页7；注2；OCR L230",
            CH1_QUOTE,
            "第1章注2引用 Pascoli 第一卷第93页。该记录只证明 Haskell 的引文定位，不证明本卡已查阅被引页面。",
            "lines L230; print p. 7, note 2",
        ),
        make_source(
            CH7_FILE,
            "第7章；印刷页187；注4；OCR L365",
            CH7_QUOTE,
            "第7章注4引用 Pascoli 第一卷第127页，并在同一注中另引第二卷第124页；卷次分别保留。",
            "lines L365; print p. 187, note 4",
        ),
    ]
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "archive",
        "sub_type": "book",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    bib_link = f"[第21章书目 p.433](../../../02-sources/02-Markdown/{BIB_FILE})（L932）"
    ch1_link = f"[第1章 p.7 注2](../../../02-sources/02-Markdown/{CH1_FILE})（L230）"
    ch7_link = f"[第7章 p.187 注4](../../../02-sources/02-Markdown/{CH7_FILE})（L365）"
    body = f"""## 内容

### 描述

**中文：** 第21章书目将此文献著录为 Lione Pascoli 的 *Vite de’ Pittori, Scultori ed Architetti moderni* 第一卷（1730）；同条另列第二卷（1736），并称影印版由 R. Istituto d’Archeologia e Storia dell’Arte 于1933年在罗马出版。Haskell 在多章脚注中引用第一卷，例如第1章 p.7 注2和第7章 p.187 注4。本卡只记录 Haskell 所载书目及引文定位，未查阅 Pascoli 原书或影印本；中英文展示题名为描述性工作译名，不是书目原载英文题名。

**English:** Chapter 21’s bibliography lists this work by Lione Pascoli as volume I (1730) of *Vite de’ Pittori, Scultori ed Architetti moderni*; the same entry separately lists volume II (1736) and says that a facsimile edition was published in Rome in 1933 by R. Istituto d’Archeologia e Storia dell’Arte. Haskell cites volume I in notes across several chapters, including chapter 1, p. 7, note 2, and chapter 7, p. 187, note 4. This card records Haskell’s bibliographic entry and citation locators only; neither Pascoli’s original book nor the facsimile was consulted. The Chinese and English display titles are descriptive working translations, not English titles printed in the bibliography.

### 题名与版本

| 字段 | 内容 | 依据 |
|---|---|---|
| 原题名 | *Vite de’ Pittori, Scultori ed Architetti moderni* | {bib_link} |
| 中文描述性工作题名 | {NAME_ZH} | {bib_link}；非原题 |
| 英文描述性工作题名 | {NAME_EN} | {bib_link}；非书目原载英文题名 |
| 卷次与原版年份 | 第一卷（I），1730年 | {bib_link} |
| 书目所列影印版 | R. Istituto d’Archeologia e Storia dell’Arte；罗马，1933年 | {bib_link}；仅按 Haskell 书目转录，未核版本实物或目录 |

### 基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 文献类型 | 图书；题名指画家、雕塑家与建筑师传记 | {bib_link} |
| 作者 | Lione Pascoli | {bib_link} |
| 语种 | 意大利语（据原题名） | {bib_link} |
| Haskell 的卷内引文示例 | 第一卷第93页；第一卷第127页（第二卷第124页另列） | {ch1_link}；{ch7_link}；Pascoli 被引页未查阅 |

## 关系与证据

本卡未新增正式关系。书内引文候选仍由对应 S2 陈述追踪并留待 S6；本次 KU 登记不把被引页内容写成已核实事实。第一卷与第二卷保持不同卷次，第二卷的 S3 身份组不并入本卡。
"""
    return f"---\n{fm}---\n\n{body}"


def group_for(row):
    return card_writer.get_group(row.get("resolution_note", ""))


def update_progress(process: str, result: str, alignment_rows, manifest_rows):
    new_rows = [
        row for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"
    ]
    groups = {}
    for row in new_rows:
        group = group_for(row)
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups.setdefault(group, []).append(row)
    registered = {
        group: rows for group, rows in groups.items()
        if any(row.get("ku_id") for row in rows)
    }
    mapped = sum(bool(row.get("ku_id")) for rows in registered.values() for row in rows)
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
    parser = argparse.ArgumentParser(description="Register Pascoli's Vite, volume I, as an archive KU")
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
    card_path = ROOT / CARD_PATH
    rel_card_path = CARD_PATH
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidates and candidates[CANDIDATE]["suggested_type"] == "archive"
    target = alignment_by_candidate[CANDIDATE]
    assert target["decision"] == "new" and not target.get("ku_id")
    assert group_for(target) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and group_for(row) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not card_path.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == rel_card_path for row in manifest)
    assert rel_card_path not in accepted

    volume_ii = alignment_by_candidate[VOLUME_II_CANDIDATE]
    assert volume_ii["decision"] == "new" and not volume_ii.get("ku_id")
    assert group_for(volume_ii) != GROUP
    assert candidates[VOLUME_II_CANDIDATE]["suggested_type"] == "archive"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    target_statements = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    relation_statements = [
        row for row in target_statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert len(target_statements) == 24, f"unexpected S2 statement count: {len(target_statements)}"
    assert len(relation_statements) == 22, f"unexpected relation-candidate count: {len(relation_statements)}"

    for file, quote in ((BIB_FILE, BIB_QUOTE), (CH1_FILE, CH1_QUOTE), (CH7_FILE, CH7_QUOTE)):
        source_path = ROOT / "02-sources" / "02-Markdown" / file
        assert quote in source_path.read_text(encoding="utf-8-sig"), f"source quote changed: {file}"

    planned_alignment = [dict(row) for row in alignments]
    planned_by_candidate = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_candidate[CANDIDATE]["ku_id"] = KU_ID
    planned_by_candidate[CANDIDATE]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
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
        "\n\n### S4 archive：Lione Pascoli《Vite》第一卷直接引文端点登记（2026-10-16）\n\n"
        f"{CANDIDATE}（{GROUP}）登记至 [{NAME_ZH}]"
        "(../../../04-knowledge/units/archives/lione-pascoli-vite-dei-pittori-vol-i.md)。"
        "第21章书目 p.433 将第一卷列为1730年，并记第二卷为1736年及1933年罗马影印版；本卡只登记第一卷。"
        "第1章 p.7 注2与第7章 p.187 注4提供跨章引用示例。该候选对应24条直接 S2 陈述，其中22条为关系候选；"
        "Haskell所引Pascoli页未独立查阅，卷二 cand-4552 保持独立 new 组。未新增正式关系、外部核验或 S5 补足。"
        f"S4 当前登记{registered}组/{mapped}条成员映射，尚待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### archive：Pascoli《Vite》第一卷 S4 登记（2026-10-16）\n\n"
        f"{CANDIDATE} 映射至 [Pascoli《Vite》第一卷 archive 卡](../units/archives/lione-pascoli-vite-dei-pittori-vol-i.md)。"
        "卡片依据第21章 p.433 书目记录作者、原题、第一卷1730年及书目所列1933年罗马影印版，并以第1、7章脚注示例定位该卷的书内引用。"
        "Pascoli 原书及影印本均未查阅；卷二保持另一 S3 身份组；引文关系候选留待 S6，本批未登记正式关系或开展 S5。"
        f"全书 S4 当前登记{registered}组/{mapped}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    updated_process += process_note
    updated_result += result_note

    if args.dry_run:
        print(f"S4 archive registration dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"group members=1; direct S2 statements={len(target_statements)}; relation candidates={len(relation_statements)}")
        print(f"volume II remains separate: {VOLUME_II_CANDIDATE} -> {group_for(volume_ii)}")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}")
        print(
            f"registered={registered:,} groups/{mapped:,} candidates; "
            f"pending={pending_groups:,} groups/{pending_members:,} candidates"
        )
        print("source quotes, S3 group, S2 endpoints, and destination uniqueness checked; no files changed")
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
