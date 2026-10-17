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

CANDIDATE = "cand-4223"
GROUP = "sg3-institution-cand-4223"
KU_ID = "units/institutions/papacy"
CARD_REL = "04-knowledge/units/institutions/papacy.md"
NAME_ZH = "教宗职位制度"
NAME_EN = "Papacy"

SOURCES = (
    {
        "page": "33",
        "lines": "L22",
        "quote": "those more subtle threats which were eventually to undermine the whole status of the papacy",
        "summary": "第2章将 papacy 的整体地位描述为受到更隐蔽威胁的对象。",
    },
    {
        "page": "33",
        "lines": "L25-L26",
        "quote": "all emerged from the stifling silence and penetrated to the very core of Roman society, affecting the papacy itself.",
        "summary": "第2章称科学、形而上学、占星术与怀疑论等变化影响到罗马社会核心，并波及 papacy 本身。",
    },
)


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def make_card():
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第2章；印刷页{item['page']}；OCR {item['lines']}",
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"{item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/02_CHP-2_sec_ii.md",
                "source_span": f"{item['lines']}; print p. {item['page']}",
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
    ev = "[第2章 p.33](../../../02-sources/02-Markdown/02_CHP-2_sec_ii.md)（L22、L25–26）"
    body = f"""## 内容

### 描述

**中文：** 本卡按哈斯克尔第2章的制度性语境登记 Papacy（教宗职位制度）：作者称某些较隐蔽的威胁最终会动摇 papacy 的整体地位，又称科学实验、形而上学思辨、占星术及怀疑论等现象穿透罗马社会核心并影响 papacy 本身。中文显示名为工作译名，不是本轮核定的规范译名。此对象指书中作为制度性职位与权力秩序谈论的 papacy，不是 Urban VIII 个人，也不等同于原文另行提到的 Roman Court（Cour Romaine）。{ev}

**English:** This unit records the Papacy as an institutional office and order in Haskell’s Chapter 2. The author says that more subtle threats would eventually undermine the papacy’s overall status, and that scientific experiments, metaphysical speculation, astrology, and disbelief reached the core of Roman society and affected the papacy itself. The Chinese display name is a working translation, not a verified standard rendering. The entity is the papacy as discussed institutionally; it is distinct from Urban VIII as a person and from the separately named Roman Court (Cour Romaine). {ev}

### 名称与身份边界

- 书中名称：the papacy；中文显示名：教宗职位制度（工作译名）。{ev}
- 类型：institution；按书中制度性职位与权力秩序语境登记，不扩展为某任教宗、罗马教廷机关或抽象教义的集合。{ev}
- 相关人物和机构：Urban VIII 与 Roman Court 在原文中分别出现，身份不并入本卡。{ev}

## 关系与证据

### 关系记录

当前没有正式关系。S2 中有17条以本候选为端点的直接陈述，其中15条标记为关系候选；它们仍留待 S6 逐条审查。卡片仅登记该制度性对象及书中语境，不将作者所述影响改写为正式关系。
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
    parser = argparse.ArgumentParser(description="Register the Papacy institution identity candidate in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_candidate = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE]["suggested_type"] == "institution"
    alignment = alignment_by_candidate[CANDIDATE]
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert card_writer.get_group(alignment["resolution_note"]) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and card_writer.get_group(row["resolution_note"]) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not card_path.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    direct = [row for row in statements if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 17, f"unexpected direct statement count: {len(direct)}"
    assert len(direct_relations) == 15, f"unexpected direct relation candidate count: {len(direct_relations)}"

    source = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_ii.md"
    source_text = " ".join(source.read_text(encoding="utf-8-sig").split())
    for item in SOURCES:
        assert " ".join(item["quote"].split()) in source_text, item["quote"]

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "institution",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    registered, mapped, pending_groups, pending_members = count_groups(planned_alignment)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), len(planned_manifest), registered, mapped, pending_groups, pending_members)
    process_note = (
        "\n\n### S4 institution：Papacy 制度性身份组登记（2026-10-16）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）登记至[教宗职位制度机构卡](../../../04-knowledge/units/institutions/papacy.md)。"
        "按 S3 裁定登记为 institution，指书中作为制度性职位与权力秩序讨论的 papacy；与 Urban VIII 人物及 Roman Court 分开。"
        "第2章 p.33 的两处原文分别谈其整体地位所受威胁及社会变化对其影响。17条直接陈述中15条关系候选留待 S6；"
        "本批未作外部核验、未将罗马教廷或具体教宗并入，也未开展 S5。"
        f"S4 累计登记{registered:,}组/{mapped:,}条成员映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### institution：Papacy 制度性身份组 S4 登记（2026-10-16）\n\n"
        f"`{CANDIDATE}` 映射至[教宗职位制度卡](../units/institutions/papacy.md)。"
        "卡片保留其与 Urban VIII 人物、Roman Court 的边界；15条直接关系候选仍待 S6。"
        f"全书 S4 当前登记{registered:,}组/{mapped:,}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 institution dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"direct statements={len(direct)}; relation candidates={len(direct_relations)}; source quotations={len(SOURCES)}")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={registered:,} groups/{mapped:,} candidates; pending={pending_groups:,} groups/{pending_members:,} candidates")
        print("S3 identity boundary and source quotations checked; no files changed")
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
        f"applied: {CANDIDATE} -> {KU_ID}; manifest={len(planned_manifest):,}; "
        f"registered={registered:,}/{mapped:,}; pending={pending_groups:,}/{pending_members:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
