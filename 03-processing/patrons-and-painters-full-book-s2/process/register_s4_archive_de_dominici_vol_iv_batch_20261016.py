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

GROUP = "archive-group-4fa823613e1b"
CANDIDATE = "cand-4835"
SET_CANDIDATE = "cand-11317"
KU_ID = "units/archives/de-dominici-vite-napoletane-vol-iv-1843"
CARD_PATH = "04-knowledge/units/archives/de-dominici-vite-napoletane-vol-iv-1843.md"
NAME_ZH = "贝尔纳多·德·多米尼奇《那不勒斯画家、雕塑家与建筑师传》第四卷（1843）"
NAME_EN = "Bernardo de Dominici, Lives of Neapolitan Painters, Sculptors and Architects, vol. IV (1843)"

BIB_FILE = "21_CHP-21Bibliography.md"
CH3_FILE = "03_CHP-3_sec_iv.md"
CH7_FILE = "07_CHP-7_sec_i.md"
BIB_QUOTE = "Dominici, Bernardo de: Vite dei pittori scultori ed architetti napoletani, 4 vols., Napoli 1843."
CH3_QUOTE = "1 De Dominici, IV, p. 27. For the comments of Cassiano dal Pozzo see Lumbroso, p. 195."
CH7_QUOTE = "6 De Dominici, IV, p. 50."


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
            "第21章书目；印刷页421；OCR L430",
            BIB_QUOTE,
            "书目列出 Bernardo de Dominici 的 *Vite dei pittori scultori ed architetti napoletani* 四卷本，出版地为那不勒斯，年份为1843。",
            "lines L430; print p. 421",
        ),
        make_source(
            CH3_FILE,
            "第3章；印刷页78；注1；OCR L192",
            CH3_QUOTE,
            "第3章注1引用 De Dominici 第四卷第27页；该条只记录 Haskell 的引文位置。",
            "lines L192; print p. 78, note 1",
        ),
        make_source(
            CH7_FILE,
            "第7章；印刷页189；注6；OCR L374",
            CH7_QUOTE,
            "第7章注6引用 De Dominici 第四卷第50页；该条只记录 Haskell 的引文位置。",
            "lines L374; print p. 189, note 6",
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
    bib_link = f"[第21章书目 p.421](../../../02-sources/02-Markdown/{BIB_FILE})（L430）"
    ch3_link = f"[第3章 p.78 注1](../../../02-sources/02-Markdown/{CH3_FILE})（L192）"
    ch7_link = f"[第7章 p.189 注6](../../../02-sources/02-Markdown/{CH7_FILE})（L374）"
    body = f"""## 内容

### 描述

**中文：** 第21章书目列出 Bernardo de Dominici 的 *Vite dei pittori scultori ed architetti napoletani* 四卷本，1843年那不勒斯版。Haskell 的多处脚注明确引用第四卷，例如第3章 p.78 注1和第7章 p.189 注6。本卡记录这些书内书目和卷级引文定位；De Dominici 原书及其被引页未独立查阅。书目另有一个全套四卷对象候选 `cand-11317`，该候选仍为 `undecided`；本卡只登记明确的第四卷引文目标，不将全套对象并入本身份组，也不据此断言两者的正式部分关系。中英文展示题名为描述性工作译名。

**English:** Chapter 21’s bibliography lists Bernardo de Dominici’s *Vite dei pittori scultori ed architetti napoletani* as a four-volume Naples edition of 1843. Haskell’s notes explicitly cite volume IV in several places, including chapter 3, p. 78, note 1, and chapter 7, p. 189, note 6. This card records those in-book bibliographic and volume-specific citation locators; neither De Dominici’s books nor the cited pages were independently consulted. A separate candidate for the complete four-volume set, `cand-11317`, remains `undecided`; this card registers only the explicit volume-IV citation target and does not merge the set-level candidate or assert a formal part relationship. The Chinese and English display titles are descriptive working translations.

### 题名与版本

| 字段 | 内容 | 依据 |
|---|---|---|
| 原题名 | *Vite dei pittori scultori ed architetti napoletani* | {bib_link} |
| 中文描述性工作题名 | {NAME_ZH} | {bib_link}；非原题 |
| 英文描述性工作题名 | {NAME_EN} | {bib_link}；非书目原载英文题名 |
| 卷次与出版年份 | 第四卷（IV）；书目所列版本为1843年 | {bib_link}；Haskell 的卷级引文见下 |
| 书目出版信息 | 那不勒斯；四卷本 | {bib_link}；全套与卷级候选的 S3 身份边界未合并 |

### 基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 文献类型 | 图书 | {bib_link} |
| 作者 | Bernardo de Dominici（按书目责任者形式） | {bib_link} |
| 语种 | 意大利语（据原题名） | {bib_link} |
| Haskell 的卷内引文示例 | 第四卷 p.27；第四卷 p.50 | {ch3_link}；{ch7_link}；De Dominici 被引页未查阅 |

## 关系与证据

本卡未新增正式关系。候选所关联的书内引文由对应 S2 陈述追踪并留待 S6；本次登记不把被引页内容写成已核实事实。全套四卷候选 `cand-11317` 的身份／粒度仍待证，与本卡保持分开。
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
    parser = argparse.ArgumentParser(description="Register the volume-IV De Dominici citation endpoint as an archive KU")
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

    set_candidate = alignment_by_candidate[SET_CANDIDATE]
    assert set_candidate["decision"] == "undecided" and not set_candidate.get("ku_id")
    assert candidates[SET_CANDIDATE]["suggested_type"] == "archive"

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
    assert len(relation_statements) == 13, f"unexpected relation-candidate count: {len(relation_statements)}"

    for file, quote in ((BIB_FILE, BIB_QUOTE), (CH3_FILE, CH3_QUOTE), (CH7_FILE, CH7_QUOTE)):
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
        "\n\n### S4 archive：De Dominici《Vite》第四卷直接关系端点登记（2026-10-16）\n\n"
        f"{CANDIDATE}（{GROUP}）登记至 [{NAME_ZH}]"
        "(../../../04-knowledge/units/archives/de-dominici-vite-napoletane-vol-iv-1843.md)。"
        "第21章 p.421 书目列全套四卷本及1843年那不勒斯版；第3章 p.78 注1、第7章 p.189 注6明确引用第四卷。"
        "本卡的对象范围限于卷级引文目标，未查阅原书或被引页。全套书目候选 cand-11317 仍为 undecided，未并组、未映射，"
        "也未据此建立 part_of 关系。该候选对应24条直接 S2 陈述，其中13条为关系候选；本批无正式关系、外部核验或 S5 补足。"
        f"S4 当前登记{registered}组/{mapped}条成员映射，尚待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### archive：De Dominici《Vite》第四卷 S4 登记（2026-10-16）\n\n"
        f"{CANDIDATE} 映射至 [De Dominici 第四卷 archive 卡](../units/archives/de-dominici-vite-napoletane-vol-iv-1843.md)。"
        "卡片依据第21章书目记载的原题、责任者和1843年那不勒斯四卷本，以及第3、7章的卷四引文定位；只登记卷级引用目标。"
        "全套候选 cand-11317 仍为 undecided，未合并或建立正式关系；原书及被引页未查阅，引文关系候选留待 S6。"
        f"全书 S4 当前登记{registered}组/{mapped}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    updated_process += process_note
    updated_result += result_note

    if args.dry_run:
        print(f"S4 archive registration dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"group members=1; direct S2 statements={len(target_statements)}; relation candidates={len(relation_statements)}")
        print(f"set-level candidate remains undecided: {SET_CANDIDATE}")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}")
        print(
            f"registered={registered:,} groups/{mapped:,} candidates; "
            f"pending={pending_groups:,} groups/{pending_members:,} candidates"
        )
        print("source quotes, S3 group, S2 endpoints, open set-level boundary, and destination uniqueness checked; no files changed")
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
