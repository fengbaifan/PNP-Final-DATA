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

GROUP = "archive-group-e45ca62cc403"
CANDIDATE = "cand-7115"
KU_ID = "units/archives/zanotti-storia-accademia-clementina-1739"
CARD_PATH = "04-knowledge/units/archives/zanotti-storia-accademia-clementina-1739.md"
NAME_ZH = "G. P. Zanotti《克莱门蒂娜学院史》两卷本（博洛尼亚，1739）"
NAME_EN = "G. P. Zanotti, History of the Accademia Clementina, 2 vols. (Bologna, 1739)"

BIB_FILE = "21_CHP-21Bibliography.md"
CH7_FILE = "07_CHP-7_sec_i.md"
BIB_QUOTE = "Zanotti, G. P.: Storia dell’Accademia Clementina, 2 vols., Bologna 1739."
CH7_QUOTE_1 = (
    "4 Zanotti, I, p. 245, and Montaiglon, I, p. 190. In 1685 the director of the French Academy "
    "in Rome tried to persuade Luca Giordano to paint a picture for the King, but the artist defaulted "
    "on his obligations— Alazard, p. 142."
)
CH7_QUOTE_2 = "6 Zanotti, I, pp. 155, 170, 199, and II, p. 121."


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
            "第21章书目；印刷页441；OCR L1292",
            BIB_QUOTE,
            "书目以 G. P. Zanotti 为责任者形式，列出《Storia dell’Accademia Clementina》两卷本，博洛尼亚1739年。",
            "lines L1292; print p. 441",
        ),
        make_source(
            CH7_FILE,
            "第7章；印刷页189；注4；OCR L372",
            CH7_QUOTE_1,
            "第7章注4引用 Zanotti 第一卷第245页；本记录只表明 Haskell 的引文定位。",
            "lines L372; print p. 189, note 4",
        ),
        make_source(
            CH7_FILE,
            "第7章；印刷页189；注5；OCR L373",
            CH7_QUOTE_2,
            "第7章注5引用 Zanotti 第一卷第155、170、199页和第二卷第121页，卷次分别保留。",
            "lines L373; print p. 189, note 5",
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
    bib_link = f"[第21章书目 p.441](../../../02-sources/02-Markdown/{BIB_FILE})（L1292）"
    ch7_1_link = f"[第7章 p.189 注4](../../../02-sources/02-Markdown/{CH7_FILE})（L372）"
    ch7_2_link = f"[第7章 p.189 注5](../../../02-sources/02-Markdown/{CH7_FILE})（L373）"
    body = f"""## 内容

### 描述

**中文：** 第21章书目将该文献著录为 G. P. Zanotti 的 *Storia dell’Accademia Clementina*，两卷本，博洛尼亚1739年。Haskell 在多章脚注中分别引用第一、二卷；第7章 p.189 注4、注5是其中两个例子。本卡只记录书目责任者形式和 Haskell 的引文定位；没有将 initials 扩写为全名，也未查阅 Zanotti 原书或被引页。中英文展示题名为描述性工作译名，并非书目原载英文题名。

**English:** Chapter 21’s bibliography lists G. P. Zanotti’s *Storia dell’Accademia Clementina* in two volumes, published in Bologna in 1739. Haskell cites both volumes in notes across several chapters; chapter 7, p. 189, notes 4 and 5 provide two examples. This card records the bibliographic author form and Haskell’s citation locators only; the initials have not been expanded to a full name, and neither Zanotti’s books nor the cited pages were consulted. The Chinese and English display titles are descriptive working translations, not an English title printed in the bibliography.

### 题名与版本

| 字段 | 内容 | 依据 |
|---|---|---|
| 原题名 | *Storia dell’Accademia Clementina* | {bib_link} |
| 中文描述性工作题名 | {NAME_ZH} | {bib_link}；非原题 |
| 英文描述性工作题名 | {NAME_EN} | {bib_link}；非书目原载英文题名 |
| 卷数 | 两卷 | {bib_link} |
| 出版信息 | 博洛尼亚，1739年 | {bib_link} |

### 基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 文献类型 | 图书 | {bib_link} |
| 责任者形式 | G. P. Zanotti；书目未在此项展开姓名 | {bib_link} |
| 语种 | 意大利语（据原题名） | {bib_link} |
| Haskell 的卷内引文示例 | 第一卷 p.245；第一卷 pp.155、170、199及第二卷 p.121 | {ch7_1_link}；{ch7_2_link}；Zanotti 被引页未查阅 |

## 关系与证据

本卡未新增正式关系。书内引文候选仍由对应 S2 陈述追踪并留待 S6；本次 KU 登记不把被引页内容写成已核实事实。书目所列两卷作为一个两卷本书目对象登记，未拆成独立卷册卡。
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
    parser = argparse.ArgumentParser(description="Register the two-volume Storia dell’Accademia Clementina archive KU")
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
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_PATH for row in manifest)
    assert CARD_PATH not in accepted

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
    assert len(target_statements) == 27, f"unexpected S2 statement count: {len(target_statements)}"
    assert len(relation_statements) == 14, f"unexpected relation-candidate count: {len(relation_statements)}"

    for file, quote in ((BIB_FILE, BIB_QUOTE), (CH7_FILE, CH7_QUOTE_1), (CH7_FILE, CH7_QUOTE_2)):
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
        "card_path": CARD_PATH,
    })
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    updated_process, updated_result, registered, mapped, pending_groups, pending_members = update_progress(
        process_text, result_text, planned_alignment, planned_manifest
    )
    process_note = (
        "\n\n### S4 archive：Zanotti《Storia dell’Accademia Clementina》两卷本登记（2026-10-16）\n\n"
        f"{CANDIDATE}（{GROUP}）登记至 [{NAME_ZH}]"
        "(../../../04-knowledge/units/archives/zanotti-storia-accademia-clementina-1739.md)。"
        "第21章 p.441 书目列责任者形式 G. P. Zanotti、书名、两卷本及博洛尼亚1739年；不将 initials 扩写为全名。"
        "第7章 p.189 注4、注5示例分别引用卷一及卷二。该候选对应27条直接 S2 陈述，其中14条为关系候选；"
        "原书和被引页未独立查阅。本批无正式关系、外部核验或 S5 补足。"
        f"S4 当前登记{registered}组/{mapped}条成员映射，尚待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### archive：Zanotti《克莱门蒂娜学院史》S4 登记（2026-10-16）\n\n"
        f"{CANDIDATE} 映射至 [Storia dell’Accademia Clementina archive 卡](../units/archives/zanotti-storia-accademia-clementina-1739.md)。"
        "卡片依据第21章书目记录 G. P. Zanotti 这一责任者形式、原题、两卷本和博洛尼亚1739年，并以第7章脚注定位卷一、卷二的书内引用。"
        "作者 initials 未扩写，原书及被引页未查阅；引文关系候选留待 S6，本批未登记正式关系或开展 S5。"
        f"全书 S4 当前登记{registered}组/{mapped}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    updated_process += process_note
    updated_result += result_note

    if args.dry_run:
        print(f"S4 archive registration dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"group members=1; direct S2 statements={len(target_statements)}; relation candidates={len(relation_statements)}")
        print(f"bibliography entry and {len([CH7_QUOTE_1, CH7_QUOTE_2])} chapter citation anchors verified; author initials preserved")
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
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
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
