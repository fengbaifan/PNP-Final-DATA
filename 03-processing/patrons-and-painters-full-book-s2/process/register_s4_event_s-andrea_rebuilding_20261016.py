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

CANDIDATE = "cand-5309"
GROUP = "sg3-event-cand-5309"
KU_ID = "units/events/s-andrea-al-quirinale-rebuilding-project"
CARD_REL = "04-knowledge/units/events/s-andrea-al-quirinale-rebuilding-project.md"
NAME_ZH = "奎里纳尔山圣安德烈初学院教堂重建工程"
NAME_EN = "Rebuilding of the Jesuit novitiate church of S. Andrea al Quirinale"

SOURCES = (
    {
        "page": "85",
        "lines": "90-91",
        "quote": "In the rebuilding of their novitiate church, S. Andrea al Quirinale, they were faced not with the tyranny, hesitation or meanness of a rich patron, but with the absolute supremacy of the most gifted and successful architect since Michelangelo.",
        "summary": "第3章称耶稣会在重建其初学院教堂 S. Andrea al Quirinale 时面对建筑师的主导地位。",
    },
    {
        "page": "86",
        "lines": "97-101",
        "quote": "In the novitiate church of S. Andrea which he began to build in 1658 he had his greatest opportunity of doing so.",
        "summary": "第3章称 Bernini 于1658年开始建造 S. Andrea 初学院教堂。",
    },
    {
        "page": "86",
        "lines": "100-101",
        "quote": "In 1649 Cardinal Ceva agreed to build a new church and lodgings, and he chose for the purpose Borromini, the most prominent architect of the day since the temporary eclipse of Bernini.5 The drawings were made, but Innocent X forbade their being executed. Seven years later, however, the Rector of the novitiate appealed once again to the new Pope, Alexander VII, whose close friend he was. This time he was successful, and after the Pope had satisfied himself that his view would not be disturbed, he strongly encouraged all his entourage to contribute towards the expense.",
        "summary": "第3章叙述1649年 Cardinal Ceva 同意建新教堂与宿舍并选择 Borromini，绘图未获 Innocent X 执行；七年后院长再次向 Alexander VII 上诉成功，教皇鼓励其随从捐助。",
    },
    {
        "page": "87",
        "lines": "107-108",
        "quote": "an episode in 1663 when Prince Pamfdi went to visit the work in progress.",
        "summary": "第3章记载 Prince Pamfili 于1663年视察进行中的工程。",
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
            "location": f"第3章；印刷页{item['page']}；OCR L{item['lines']}",
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": "02-sources/02-Markdown/03_CHP-3_sec_iv.md",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "event",
        "evidence_status": "source_backed",
        "sources": source_rows,
        "created": "2026-10-16",
        "updated": "2026-10-16",
        "process_ref": f"03-processing/{TASK}/process/knowledge.md",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    ev85 = "[第3章 p.85](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L90–91）"
    ev86 = "[第3章 p.86](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L97–101）"
    ev87 = "[第3章 p.87](../../../02-sources/02-Markdown/03_CHP-3_sec_iv.md)（L107–108）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔叙述的耶稣会奎里纳尔山初学院教堂重建工程，地点为罗马的 S. Andrea al Quirinale。书中称 Bernini 于1658年开始建造；工程前身包括1649年 Cardinal Ceva 同意建新教堂与宿舍、选择 Borromini 后绘图未获 Innocent X 执行，以及七年后院长向 Alexander VII 上诉成功。第3章另记 Prince Camillo Pamfili 于1663年查看施工。以上日期与进程均按原书叙述保留；所引段落没有给出工程完工日期。中文题名为工作译名。{ev85} {ev86} {ev87}

**English:** This unit records Haskell’s account of the Jesuit rebuilding project for the novitiate church of S. Andrea al Quirinale in Rome. The book says Bernini began building in 1658. The preceding project history includes Cardinal Ceva’s 1649 agreement to build a new church and lodgings, his selection of Borromini, the prohibition by Innocent X against executing the drawings, and the Rector’s successful appeal to Alexander VII seven years later. Chapter 3 also reports Prince Camillo Pamfili’s visit to the work in progress in 1663. Dates and stages follow Haskell’s account; the cited passage does not give a completion date. The Chinese title is a working translation. {ev85} {ev86} {ev87}

### 名称与类型

- 书中对象：重建耶稣会初学院教堂 S. Andrea al Quirinale 的工程。{ev85}
- 对象类型：事件／建设工程；不等同于教堂建筑实体。{ev85} {ev86}
- 地点：罗马的 S. Andrea al Quirinale（地点实体另见[奎里纳尔圣安德烈堂](../places/s-andrea-al-quirinale.md)）；地点端点关系候选留待 S6。{ev85} {ev86}

### 进程

- 1649年：Cardinal Ceva 同意建新教堂和宿舍，选择 Borromini；Innocent X 禁止执行其图纸。{ev86}
- 七年后：初学院院长向 Alexander VII 再次上诉成功，教皇鼓励其随从为费用捐助；按原文相对时间记载。{ev86}
- 1658年：Bernini 开始建造 S. Andrea 初学院教堂。{ev86}
- 1663年：Prince Camillo Pamfili 查看进行中的工程。{ev87}
- 完工时间：所引叙述未提供。{ev86} {ev87}

## 关系与证据

### 关系记录

当前没有正式关系。该事件组有17条直接 S2 陈述，其中16条为关系候选；人物、机构、建筑地点及工程内容均留待 S6 逐条审查。本卡仅登记建设事件身份；已有的 S. Andrea al Quirinale 地点卡维持 place 类型，不与本事件合并。
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
    parser = argparse.ArgumentParser(description="Register the S. Andrea al Quirinale rebuilding event in S4.")
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

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE]["suggested_type"] == "event"
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
    assert len(direct_relations) == 16, f"unexpected direct relation candidate count: {len(direct_relations)}"

    for item in SOURCES:
        source = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
        text = " ".join(source.read_text(encoding="utf-8-sig").split())
        quote = " ".join(item["quote"].split())
        assert quote in text, (item["page"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    target = next(row for row in planned_alignment if row.get("candidate_id") == CANDIDATE and not row.get("external_source"))
    target["ku_id"] = KU_ID
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": "event",
        "canonical_name": NAME_ZH,
        "name_en": NAME_EN,
        "source_task": TASK,
        "card_path": CARD_REL,
    })
    registered, mapped, pending_groups, pending_members = count_groups(planned_alignment)
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), len(planned_manifest), registered, mapped, pending_groups, pending_members)
    process_note = (
        "\n\n### S4 event：S. Andrea al Quirinale 教堂重建工程登记（2026-10-16）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）登记至[奎里纳尔山圣安德烈初学院教堂重建工程卡]"
        "(../../../04-knowledge/units/events/s-andrea-al-quirinale-rebuilding-project.md)。"
        "S3 类型为 event；既有 S. Andrea al Quirinale KU 是 place，二者保持分开。第3章 pp.85–87 记录项目背景、1649年方案受阻、"
        "七年后上诉成功、Bernini 于1658年开建，以及1663年 Pamfili 视察工程；本段未载完工日期。17条直接陈述中的16条关系候选留待 S6，"
        "本批未新增正式关系或开展 S5。"
        f"S4 累计登记{registered:,}组/{mapped:,}条成员映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_note = (
        "\n\n### event：S. Andrea al Quirinale 重建工程 S4 登记（2026-10-16）\n\n"
        f"`{CANDIDATE}` 映射至[重建工程事件卡](../units/events/s-andrea-al-quirinale-rebuilding-project.md)。"
        "地点实体仍指向既有 place 卡；事件与建筑不合并。17条直接断言中16条关系候选留待 S6，完工日期保留为原书未载。"
        f"全书 S4 当前登记{registered:,}组/{mapped:,}条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 event dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"direct statements={len(direct)}; relation candidates={len(direct_relations)}; source quotations={len(SOURCES)}")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={registered:,} groups/{mapped:,} candidates; pending={pending_groups:,} groups/{pending_members:,} candidates")
        print("source quotations checked; no files changed")
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
