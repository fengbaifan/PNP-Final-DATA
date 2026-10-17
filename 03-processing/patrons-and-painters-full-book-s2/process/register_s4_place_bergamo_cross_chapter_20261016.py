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

CANDIDATES = ("cand-11460", "cand-6208", "cand-7743", "cand-8574")
GROUP = "sg3-place-bergamo-city"
KU_ID = "units/places/bergamo"
CARD_REL = "04-knowledge/units/places/bergamo.md"
NAME_ZH = "贝加莫"
NAME_EN = "Bergamo"

SOURCES = (
    {
        "file": "03-Index/03-2-Index-CSV/B.csv",
        "location": "书后索引 B.csv#325；印刷页215–21",
        "lines": "B.csv#325",
        "quote": "Bergamo,,,,215-21",
        "summary": "书后索引以 Bergamo 为主项，列出印刷页215–21。",
    },
    {
        "file": "02-Markdown/05_CHP-5_sec_iii.md",
        "location": "第5章；印刷页153；注6",
        "lines": "153",
        "quote": "Io venni dalla predetta mia patria [Bergamo] da quindici anni e venni in Napoli, et sempre ho abitato in Napoli al Baglivo",
        "summary": "第5章注6引述 Codazzi 1636 年的话，将 Bergamo 称为其 patria；本卡仅记录城市指称，不据此补写人物出生或迁居事实。",
    },
    {
        "file": "02-Markdown/08_CHP-8_sec_ii.md",
        "location": "第8章；印刷页223",
        "lines": "143",
        "quote": "Work on the church of Santa Maria Maggiore in Bergamo began in 1137",
        "summary": "第8章将 Santa Maria Maggiore 置于 Bergamo，并称其工程始于1137年。",
    },
    {
        "file": "02-Markdown/09_CHP-9_intro.md",
        "location": "第9章；印刷页263",
        "lines": "234",
        "quote": "he never achieved any higher post than the governorship of Bergamo in 1690.",
        "summary": "第9章以 Bergamo 指称 Zaccaria Sagredo 于1690年任职的城市。",
    },
)


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def make_card():
    source_rows = []
    for item in SOURCES:
        file_path = item["file"]
        source_file = f"02-sources/{file_path}"
        citation = card_writer.BOOK_CITATION
        source_rows.append({
            "citation": citation,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": source_file,
                "source_span": f"{item['lines']}; {item['location']}",
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "place",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ev5 = "[第5章 p.153 注6](../../../02-sources/02-Markdown/05_CHP-5_sec_iii.md)"
    ev8 = "[第8章 p.223](../../../02-sources/02-Markdown/08_CHP-8_sec_ii.md)"
    ev9 = "[第9章 p.263](../../../02-sources/02-Markdown/09_CHP-9_intro.md)"
    index_ref = "[书后索引 B.csv#325](../../../02-sources/03-Index/03-2-Index-CSV/B.csv)"
    body = f"""## 内容

### 描述

**中文：** Bergamo 是本书多章及书后索引所指的城市。S3 将索引主项与正文中 Codazzi 所称 patria、Santa Maria Maggiore 所在城市，以及 Zaccaria Sagredo 的任职地点合并为同一城市身份组。此卡只登记地名及书中城市指称，不据此扩写现代行政边界、历史政治归属或城市沿革，也不将人物履历、教堂或任职事件并入城市实体。{index_ref} {ev5} {ev8} {ev9}

**English:** Bergamo is a city named across the book and its index. S3 groups the index heading with the city references in Codazzi’s quoted patria, the location of Santa Maria Maggiore, and the place of Zaccaria Sagredo’s governorship. This unit records the place name and the book’s use of it as a city; it does not add modern administrative boundaries, a full political history, or a city chronology, and it keeps biographies, the church, and office-holding events separate from the city entity. {index_ref} {ev5} {ev8} {ev9}

### 名称与身份范围

- 书中名称：Bergamo；中文显示名“贝加莫”为工作译名。{index_ref}
- 对象类型：城市地点。第8章称其曾由 Venice 统治并位于 Milan 以东三十英里；本卡不将相邻政治实体并为城市身份。{ev8}
- 书内跨章指称：第5章 p.153 注6引 Codazzi 以 Bergamo 为 patria；第8章 p.223 将 Santa Maria Maggiore 置于 Bergamo；第9章 p.263 将 Bergamo 作为 governorship 所在地。{ev5} {ev8} {ev9}
- 索引：主项 Bergamo，印刷页215–21；Santa Maria Maggiore 的子项延伸至 p.223。{index_ref}

## 关系与证据

### 关系记录

当前没有正式关系。该组15条直接 S2 陈述均为关系候选，包括人物居住、离开或到访城市，以及工程、委任和城市历史语境；均留待 S6 逐条判定。本卡不把提及、共现或索引子目转写为正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def count_groups(rows):
    groups = defaultdict(list)
    for row in rows:
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new":
            group = card_writer.get_group(row["resolution_note"])
            assert group, f"new decision lacks group: {row['candidate_id']}"
            groups[group].append(row)
    registered = {group: members for group, members in groups.items() if any(row.get("ku_id") for row in members)}
    mapped = sum(bool(row.get("ku_id")) for members in registered.values() for row in members)
    pending = [row for row in rows if row.get("decision") == "new" and not row.get("ku_id") and not row.get("external_source")]
    return len(registered), mapped, len(groups) - len(registered), len(pending)


def update_result(result, manifest_count, registered, mapped, pending_groups, pending_members):
    pattern = re.compile(r"S4 已登记\s*[\d,]+组、映射[\d,]+条成员候选；尚待登记[\d,]+组、[\d,]+条映射。")
    result, n = pattern.subn(
        f"S4 已登记{registered:,}组、映射{mapped:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        result,
        count=1,
    )
    assert n == 1, "could not update current S4 summary in result"
    manifest_pattern = re.compile(r"(\|\s*\[KU 登记\]\(\.\./tables/ku-manifest\.csv\)\s*\|\s*)[\d,]+ KU")
    result, n = manifest_pattern.subn(lambda m: f"{m.group(1)}{manifest_count:,} KU", result, count=1)
    assert n == 1, "could not update manifest total in result"
    return result


def main():
    parser = argparse.ArgumentParser(description="Register the cross-chapter Bergamo city identity group in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert all(candidate in candidate_by_id and candidate_by_id[candidate]["suggested_type"] == "place" for candidate in CANDIDATES)
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and card_writer.get_group(row["resolution_note"]) == GROUP
    ]
    assert sorted(row["candidate_id"] for row in group_rows) == sorted(CANDIDATES)
    assert all(not row.get("ku_id") for row in group_rows)
    assert not card_path.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 15, f"unexpected direct statement count: {len(direct)}"
    assert len(direct_relations) == 15, f"unexpected direct relation candidate count: {len(direct_relations)}"

    for item in SOURCES:
        source = ROOT / "02-sources" / item["file"]
        text = " ".join(source.read_text(encoding="utf-8-sig").split())
        quote = " ".join(item["quote"].split())
        assert quote in text, (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for candidate_id in CANDIDATES:
        planned_by_id[candidate_id]["ku_id"] = KU_ID
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "place",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    registered, mapped, pending_groups, pending_members = count_groups(planned_alignment)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), len(planned_manifest), registered, mapped, pending_groups, pending_members)
    process_note = (
        "\n\n### S4 place：Bergamo 跨章城市身份组登记（2026-10-16）\n\n"
        f"`{', '.join(CANDIDATES)}`（`{GROUP}`）统一登记至[贝加莫地点卡](../../../04-knowledge/units/places/bergamo.md)。"
        "S3 将索引主项 B.csv#325 与第5章 Codazzi 的 patria、第8章 Santa Maria Maggiore 所在城市和第9章 Sagredo 任职地点归为同一城市。"
        "S2 共15条直接陈述，全部是关系候选，仍留待 S6；未把城市与人物、教堂、共和国或任职事件合并，也未新建正式关系。"
        f"S4 累计登记{registered:,}组/{mapped:,}条成员映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### place：Bergamo 跨章身份组 S4 登记（2026-10-16）\n\n"
        "`cand-11460`、`cand-6208`、`cand-7743`、`cand-8574` 共映射至[贝加莫地点卡](../units/places/bergamo.md)。"
        "索引主项与第5、8、9章正文候选构成同一城市身份；15条直接关系候选仍留待 S6，不新增正式关系。"
        f"全书 S4 当前登记{registered:,}组/{mapped:,}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 place dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"direct statements={len(direct)}; relation candidates={len(direct_relations)}; source quotations={len(SOURCES)}")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={registered:,} groups/{mapped:,} candidates; pending={pending_groups:,} groups/{pending_members:,} candidates")
        print("four cross-chapter candidate decisions and all source quotations checked; no files changed")
        return 0

    card_path.write_text(make_card(), encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={registered:,}/{mapped:,}; pending={pending_groups:,}/{pending_members:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
