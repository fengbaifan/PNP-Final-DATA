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
CANDIDATE = "cand-9448"
GROUP = "sg3-institution-cand-9448"
KU_ID = "units/institutions/biblioteca-marciana"
CARD_PATH = "04-knowledge/units/institutions/biblioteca-marciana.md"
NAME_ZH = "马尔恰纳图书馆"
NAME_EN = "Biblioteca Marciana"
DIRECT_RELATION_STATEMENTS = (
    "st-chp10-p326-n01-marciana-set",
    "st-chp13-p341-notes-note4-volume-locator-at-biblioteca-marciana",
    "st-chp17-pi-note3-pamphlet-locator",
)
SOURCES = [
    {
        "chapter": "9",
        "page": "269",
        "file": "09_CHP-9_sec_ii.md",
        "lines": "L95",
        "quote": "Marciana, Misc. 1135, n. 3",
        "summary": "第九章注5以 Marciana, Misc. 1135, n. 3 给出一份1734年小册子的馆藏定位。",
        "note": "note 5; abbreviated form",
    },
    {
        "chapter": "10",
        "page": "293",
        "file": "10_CHP-10_intro.md",
        "lines": "L558",
        "quote": "2 Letter from Tessin to A. M. Zanetti the Elder dated 12 March 1737 in Bibiioteca Marciana, Cl.XI, Cod. CXVI, 7356.",
        "summary": "第十章注2给出 Tessin 致 A. M. Zanetti 的1737年书信及其 Biblioteca Marciana 馆藏号；本段 OCR 拼作 Bibiioteca。",
        "note": "note 2; OCR reads Bibiioteca, retained as transcribed",
    },
    {
        "chapter": "10",
        "page": "301",
        "file": "10_CHP-10_intro.md",
        "lines": "L591",
        "quote": "4 There are two very friendly letters from Poleni to Smith, dated 9 and 17 April 1747, in the Biblioteca Marciana—MSS. Ital:Cl.X. Cod CCLXXXVIII—6580.",
        "summary": "第十章注4将 Poleni 致 Smith 的1747年书信定位于 Biblioteca Marciana。",
        "note": "note 4",
    },
    {
        "chapter": "10",
        "page": "326",
        "file": "10_CHP-10_sec_ii.md",
        "lines": "L221",
        "quote": "The set of these pamphlets in the Biblioteca Marciana, Venice [Misc. 212] are all marked in an eighteenth-century hand with indignant comments such as Perfidioso, Seditioso, etc.",
        "summary": "第十章称一组庆祝 Pisani 入选的宣传册藏于威尼斯 Biblioteca Marciana，并记有十八世纪手写批语。",
        "note": "",
    },
    {
        "chapter": "13",
        "page": "341",
        "file": "13_CHP-13_intro.md",
        "lines": "L226",
        "quote": "4 Biblioteca Marciana, Venice—MSS. Italiani—Cl. XI, Cod. CXVI, 7356.",
        "summary": "第十三章注4以 Biblioteca Marciana, Venice 和馆藏号定位 Zanetti 的笔记与书信卷册。",
        "note": "note 4",
    },
    {
        "chapter": "17",
        "page": "380",
        "file": "17_CHP-17_sec_i.md",
        "lines": "L17-L18",
        "quote": "A further catalogue of the pictures still remaining in the collection was published by\nAb. G. Nicoletti in 1872 (Biblioteca Marciana: Misc. C. 11231).",
        "summary": "第十七章将一份1872年出版的 Manfrin 藏画目录定位于 Biblioteca Marciana, Misc. C. 11231。",
        "note": "",
    },
]


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def card_text():
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章；印刷页{item['page']}；OCR {item['lines']}"
            + (f"；{item['note']}" if item["note"] else ""),
            "sentence_summary": item["summary"],
            "original_quotes": [{
                "source_span": f"lines {item['lines']}",
                "text": item["quote"],
            }],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}"
                + (f"; {item['note']}" if item["note"] else ""),
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "institution",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ev9 = "[第九章 p.269 注5](../../../02-sources/02-Markdown/09_CHP-9_sec_ii.md)（L95）"
    ev10 = "[第十章 p.301 注4、p.326](../../../02-sources/02-Markdown/10_CHP-10_intro.md)"
    ev13 = "[第十三章 p.341 注4](../../../02-sources/02-Markdown/13_CHP-13_intro.md)（L226）"
    ev17 = "[第十七章 p.380](../../../02-sources/02-Markdown/17_CHP-17_sec_i.md)（L17–18）"
    body = f"""## 内容

### 描述

**中文：** 哈斯克尔在第九、十、十三和十七章以 Biblioteca Marciana 或 Marciana 为书信、手稿、小册子及目录提供馆藏定位；部分引文明确写作 Venice。此卡只登记原书中的机构指称及其被引用的保管语境，不独立核验机构沿革、当前馆藏、目录记录或馆藏号。中文显示名为工作译名，原文名称保留意大利语。

**English:** Across Chapters 9, 10, 13, and 17, Haskell uses Biblioteca Marciana or Marciana as a repository locator for letters, manuscripts, pamphlets, and a catalogue; some citations specify Venice. This card records the institution name and repository context as used in the book. It does not independently verify the institution's history, present holdings, catalogue records, or shelfmarks. The Chinese display name is a working translation; the Italian name is retained.

### 名称

| 字段 | 内容 | 依据 |
|---|---|---|
| 中文显示名（工作译名） | {NAME_ZH} | {ev10}；不宣称官方中文名 |
| 书中名称 | Biblioteca Marciana | {ev10}、{ev13}；第九章注5另用简称 Marciana（{ev9}） |

### 基本信息

| 字段 | 内容 | 依据 |
|---|---|---|
| 书中机构类型 | 图书馆／文献保管机构；仅按书中引用语境记录 | {ev10}，第十章称 letters located in the Biblioteca Marciana |
| 书中地点称谓 | Venice | {ev10}、{ev13} |
| 引用中的文献类别 | 书信、手稿卷册、宣传册组及藏画目录均被书中定位于该机构；不据此主张当前馆藏状态 | {ev9}、{ev10}、{ev13}、{ev17} |

### 本书相关内容

跨章引文包括 Tessin 与 Zanetti 的书信定位、Poleni 与 Smith 的书信、Pisani 入选相关宣传册组、Zanetti 卷册，以及 Manfrin 藏画的1872年目录。第十章 p.293 注2的 OCR 将名称拼作 Bibiioteca；第十章 p.301及第十三章 p.341 的转录拼作 Biblioteca。本卡保留该转录差异，不把 OCR 字样另作机构身份。

## 关系与证据

### 关系记录

当前没有正式关系。正文中的导航与线索不自动形成关系边。

S2 中有待 S6 审查的馆藏定位候选：第九章 p.269 注5的1734年小册子见[对应 archive 卡](../archives/venice-scalzi-pamphlet-1734.md)；另有第十章宣传册组、第十三章 Zanetti 卷册及第十七章 Manfrin 小册子定位。本批仅登记机构身份，不写入正式持有、保管或收藏关系。
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
        description="Register Biblioteca Marciana as the cross-chapter institution identity group."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    candidate_fields, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_candidate = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    rel_card_path = "04-knowledge/units/institutions/biblioteca-marciana.md"
    card_path = ROOT / rel_card_path
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1193, f"unexpected manifest size: {len(manifest)}"
    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE]["suggested_type"] == "institution"
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

    mentions = [
        row for row in read_csv(TABLES / "mentions.csv")[1]
        if row.get("candidate_id") == CANDIDATE
    ]
    assert len(mentions) == 11, f"unexpected cross-chapter mention count: {len(mentions)}"
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relation_ids = {
        row["statement_id"] for row in direct
        if row.get("qualifiers", {}).get("relation_candidate")
    }
    assert direct_relation_ids == set(DIRECT_RELATION_STATEMENTS), direct_relation_ids
    by_statement = {row["statement_id"]: row for row in statements}
    assert all(
        by_statement[statement_id].get("object_candidate_id") == CANDIDATE
        for statement_id in DIRECT_RELATION_STATEMENTS
    )

    for item in SOURCES:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

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
        "type": "institution",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": rel_card_path,
    })
    process_text = (PROCESS_PATH).read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")
    updated_process, updated_result, registered, mapped, pending_groups, pending_members = update_progress(
        process_text, result_text, planned_alignment, planned_manifest
    )
    process_note = (
        "\n\n### S4 institution：Biblioteca Marciana 跨章身份组登记（2026-10-16）\n\n"
        f"{CANDIDATE}（{GROUP}）映射至 [Biblioteca Marciana 机构卡]"
        "(../../../04-knowledge/units/institutions/biblioteca-marciana.md)。"
        "S2 共记录11处跨章提及；第九、十、十三、十七章的引文均将该名称用作馆藏定位。"
        "三条直接关系候选为宣传册组、Zanetti 卷册和 Manfrin 小册子定位，仍留待 S6；"
        "不推定当前馆藏、不核验外部目录，也未新增正式关系。第十章 p.293 注2 的 OCR 拼作 Bibiioteca，"
        "p.301及第十三章 p.341 转录作 Biblioteca；卡片保留该转录差异，不把它另分为身份。"
        f"S4 累计登记{registered}组/{mapped}条成员候选，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### institution：Biblioteca Marciana 跨章组 S4 登记（2026-10-16）\n\n"
        "cand-9448 的11处跨章提及映射至 [Biblioteca Marciana 机构卡]"
        "(../units/institutions/biblioteca-marciana.md)。卡片只登记书内的机构名及馆藏定位语境；"
        "p.293 OCR 的 Bibiioteca 拼写差异被保留说明，宣传册、卷册和目录的关系候选仍待 S6。"
        f"全书 S4 当前登记{registered}组/{mapped}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    updated_process += process_note
    updated_result += result_note

    if args.dry_run:
        print(f"S4 institution dry-run passed: {CANDIDATE} ({len(mentions)} mentions) -> {KU_ID}")
        print(f"direct relation candidates={len(direct_relation_ids)}; all remain for S6 review")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}")
        print(
            f"registered={registered:,} groups/{mapped:,} candidates; "
            f"pending={pending_groups:,} groups/{pending_members:,} candidates"
        )
        print("six cross-chapter source anchors and one unregistered S3 group checked; no files changed")
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
