from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

CANDIDATE = "cand-6031"
GROUP = "sg3-event-cand-6031"
KU_ID = "units/events/annual-st-josephs-day-exhibition-pantheon"
CARD_REL = "04-knowledge/units/events/annual-st-josephs-day-exhibition-pantheon.md"
CARD_PATH = ROOT / CARD_REL
NAME_ZH = "万神殿圣约瑟节年度展览"
NAME_EN = "Annual St Joseph’s Day Exhibition at the Pantheon"
SOURCE_FILE = "02-sources/02-Markdown/05_CHP-5_sec_i.md"
BOOK_CITATION = (
    "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. "
    "(New Haven and London: Yale University Press, 1980; this printing 2006)"
)

SOURCES = (
    {
        "location": "第5章；印刷页126；OCR L62–65",
        "summary": (
            "第5章称展览每年3月19日在 Pantheon 举行以庆祝圣约瑟节，由 Congregazione dei Virtuosi 组织；"
            "画家提交作品后由该会成员遴选，展品在柱廊陈列。Haskell称该系列可能始于17世纪初，并在1764年前某时结束；"
            "此处保留其可能性及时间范围，PDF印刷页确认OCR的“17Ó4”读作1764。"
        ),
        "quotes": (
            ("lines 62", "the one held in the Pantheon each year on 19 March to celebrate the feast day of St Joseph"),
            ("lines 62", "This was organised by the Congregazione dei Virtuosi"),
            ("lines 63", "They probably began early in the seventeenth century and came to an end some time before 17Ó4."),
            ("lines 64–65", "Each artist could submit one picture and a selection was made by the members of the Congregazione."),
            ("lines 65", "The pictures chosen were then arranged under the colonnade of the portico, while above the balustrade was hung a large Dream of St Joseph and probably tapestries. Both old masters and contemporary works were shown."),
        ),
        "span": "lines 62–65; print p. 126",
    },
    {
        "location": "第5章；印刷页126；OCR L66–70",
        "summary": "第5章以1650年 Velasquez 展出 Pareja 肖像为例，说明艺术家后来也利用这场展览吸引注意。",
        "quotes": (
            ("lines 66–67", "In 1650, for instance, Velasquez, then on his second visit to Rome, showed the portrait of his servant Pareja which understandably caused a sensation."),
        ),
        "span": "lines 66–70; print p. 126",
    },
    {
        "location": "第5章；印刷页127；OCR L77",
        "summary": "第5章记载1680年一届展览中，当局命令警察以两幅画“不雅”为由予以扣押；原文只记命令，不确认扣押已执行。",
        "quotes": (
            ("lines 77", "Indeed, at the exhibition of 1680 the authorities ordered the police to seize two of the pictures on the grounds that they were indecent."),
        ),
        "span": "lines 77; print p. 127",
    },
)

TYPE_ORDER = (
    "archive", "event", "family", "institution", "person", "place",
    "procedure", "term", "work", "未分类",
)
TYPE_LABELS = {"unclassified": "未分类", "": "未分类"}


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note: str) -> str:
    note = note or ""
    patterns = (
        re.compile(r"(?<![A-Za-z0-9_-])group=([A-Za-z0-9_./:-]+)"),
        re.compile(r"身份组=([A-Za-z0-9_./:-]+)"),
    )
    matches = [match for pattern in patterns for match in pattern.finditer(note)]
    if not matches:
        return ""
    # Notes retain prior decisions; use the first explicit current group marker,
    # while avoiding matches inside keys such as prior_group= and current_group=.
    return min(matches, key=lambda match: match.start()).group(1).rstrip(".,:;")


def load_statements():
    return [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def make_card():
    source_rows = []
    for item in SOURCES:
        source_rows.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [
                {"source_span": span, "text": quote}
                for span, quote in item["quotes"]
            ],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": SOURCE_FILE,
                "source_span": item["span"],
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
    p126 = "[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L62–70）"
    p127 = "[第5章 p.127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L77）"
    body = f"""## 内容

### 描述

**中文：** 本卡记录哈斯克尔所述在罗马 Pantheon 每年3月19日举行、庆祝圣约瑟节的年度展览系列。作者称该展览由 Congregazione dei Virtuosi 组织；画家可各提交一幅作品，由该会成员遴选，展品陈列于柱廊。中文显示名为描述性工作译名。{p126}

**English:** This unit records the recurring exhibition series that Haskell describes as taking place each year at the Pantheon in Rome on 19 March for the feast of St Joseph. The author says that it was organized by the Congregazione dei Virtuosi; each artist could submit one picture for selection by members of the confraternity, and selected pictures were displayed under the portico colonnade. The Chinese display name is a descriptive working translation. {p126}

### 活动性质与时间

- 活动性质：每年举行的展览系列；身份粒度为重复活动系列，不指某一届。[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L62–65）
- 举行日期：每年3月19日；原书称其为庆祝圣约瑟节。[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L62）
- 起讫记载：Haskell称这些展览“可能”始于17世纪初，并于1764年前某时结束。首届和末届的确切日期未由该段确定；扫描印刷页确认 OCR 的“17Ó4”读作1764。[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L63）
- 举办地点：罗马 Pantheon。[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L62）
- 组织者：Congregazione dei Virtuosi。[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L62–63）

### 书内活动记录

- 遴选与陈列：每位画家可提交一幅画，由该会成员遴选；获选作品置于 Pantheon 柱廊，栏杆上悬挂一件大型《圣约瑟之梦》，并可能陈列挂毯。[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L64–65）
- 1650年：Haskell以 Velasquez 展出 Pareja 肖像为例，叙述艺术家开始利用 Pantheon 展览吸引公众注意。[第5章 p.126](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L66–70）
- 1680年：当局命令警察以“不雅”为由扣押两幅画；原文记载的是命令，不确认扣押已经执行。该年具体场次的事件候选 `cand-6047` 与本展览系列分开，仍待身份裁决。[第5章 p.127](../../../02-sources/02-Markdown/05_CHP-5_sec_i.md)（L77）

## 关系与证据

### 关系记录

当前没有已登记的正式关系。
"""
    return f"---\n{fm}---\n\n{body}"


def summarize_by_type(candidate_rows, alignment_rows):
    candidate_by_id = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_candidate = defaultdict(list)
    for row in alignment_rows:
        candidate_id = row.get("candidate_id", "")
        if candidate_id in candidate_by_id:
            alignment_by_candidate[candidate_id].append(row)
    decisions = {}
    for candidate_id, rows in alignment_by_candidate.items():
        candidate_rows = [row for row in rows if not row.get("external_source")]
        if len(candidate_rows) == 1:
            decisions[candidate_id] = candidate_rows[0]
        elif not candidate_rows and len(rows) == 1:
            # Some current candidate decisions carry their own external source.
            decisions[candidate_id] = rows[0]
        else:
            raise AssertionError(f"ambiguous candidate decision rows: {candidate_id}")
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    buckets = defaultdict(list)
    for cid, candidate in candidate_by_id.items():
        raw_type = candidate.get("suggested_type", "")
        kind = TYPE_LABELS.get(raw_type, raw_type) or "未分类"
        if kind not in TYPE_ORDER:
            kind = "未分类"
        buckets[kind].append(decisions[cid])

    result = {}
    for kind in TYPE_ORDER:
        rows = buckets[kind]
        same_rows = [r for r in rows if r["decision"] == "same"]
        same_targets = {r["ku_id"] for r in same_rows}
        assert all(same_targets), f"same rows without target in {kind}"
        new_groups = defaultdict(list)
        for row in rows:
            if row["decision"] == "new":
                group = get_group(row.get("resolution_note", ""))
                assert group, f"new row without identity group: {row['candidate_id']}"
                new_groups[group].append(row)
        registered_groups = 0
        registered_members = 0
        pending_groups = 0
        pending_members = 0
        for group, members in new_groups.items():
            mapped = [m.get("ku_id", "") for m in members]
            if all(mapped):
                assert len(set(mapped)) == 1, f"new group maps to multiple KUs: {group}"
                registered_groups += 1
                registered_members += len(members)
            else:
                assert not any(mapped), f"partially registered new group: {group}"
                pending_groups += 1
                pending_members += len(members)
        result[kind] = {
            "same_candidates": len(same_rows),
            "same_kus": len(same_targets),
            "new_candidates": sum(len(members) for members in new_groups.values()),
            "new_groups": len(new_groups),
            "registered_groups": registered_groups,
            "registered_members": registered_members,
            "pending_groups": pending_groups,
            "pending_members": pending_members,
            "conflict": sum(r["decision"] == "conflict" for r in rows),
            "excluded": sum(r["decision"] == "excluded" for r in rows),
            "undecided": sum(r["decision"] == "undecided" for r in rows),
            "total": len(rows),
        }
    return result


def fmt(n):
    return f"{n:,}"


def build_type_table(stats):
    lines = [
        "| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    totals = defaultdict(int)
    for kind in TYPE_ORDER:
        x = stats[kind]
        lines.append(
            f"| {kind} | {fmt(x['same_candidates'])}→{fmt(x['same_kus'])} "
            f"| {fmt(x['new_candidates'])}／{fmt(x['new_groups'])} "
            f"| {fmt(x['registered_groups'])}／{fmt(x['pending_groups'])}；{fmt(x['pending_members'])} "
            f"| {fmt(x['conflict'])} | {fmt(x['excluded'])} | {fmt(x['undecided'])} |"
        )
        for key in ("same_candidates", "same_kus", "new_candidates", "new_groups", "registered_groups", "registered_members", "pending_groups", "pending_members", "conflict", "excluded", "undecided", "total"):
            totals[key] += x[key]
    lines.append(
        f"| **合计** | **{fmt(totals['same_candidates'])}→{fmt(totals['same_kus'])}** "
        f"| **{fmt(totals['new_candidates'])}／{fmt(totals['new_groups'])}** "
        f"| **{fmt(totals['registered_groups'])}／{fmt(totals['pending_groups'])}；{fmt(totals['pending_members'])}** "
        f"| **{fmt(totals['conflict'])}** | **{fmt(totals['excluded'])}** | **{fmt(totals['undecided'])}** |"
    )
    return "\n".join(lines), dict(totals)


def update_result(result, stats, totals, manifest_count):
    n_decisions = totals["total"]
    summary = (
        f"**当前状态：全书 S2 语义处理已完成，尚未独立语义验收；S3 已记录全部候选的现行决定与去向，冲突及待证对象仍未解决；S4 KU 登记处理中。** "
        f"{fmt(n_decisions)} 个候选决定行中，same={fmt(totals['same_candidates'])}（指向{fmt(totals['same_kus'])}个既有 KU）、"
        f"new={fmt(totals['new_candidates'])}（{fmt(totals['new_groups'])}个身份组）、conflict={fmt(totals['conflict'])}、"
        f"excluded={fmt(totals['excluded'])}、undecided={fmt(totals['undecided'])}。"
        f"S4 已登记{fmt(totals['registered_groups'])}组、映射{fmt(totals['registered_members'])}条成员候选；"
        f"尚待登记{fmt(totals['pending_groups'])}组、{fmt(totals['pending_members'])}条映射。"
    )
    result, n = re.subn(r"^\*\*当前状态：.*$", summary, result, count=1, flags=re.M)
    assert n == 1, "could not refresh current status paragraph"

    # The result's S3 tally table follows the dedicated section heading.
    s3_start = result.index("## S3 身份决定与交接")
    table_start = result.index("| S3 决定 |", s3_start)
    table_end = result.index("\n\n", table_start)
    s3_table = "\n".join([
        "| S3 决定 | 候选数 | 去向 |",
        "|---|---:|---|",
        f"| same | {fmt(totals['same_candidates'])} | 指向 {fmt(totals['same_kus'])} 个既有 KU |",
        f"| new | {fmt(totals['new_candidates'])} | 按 {fmt(totals['new_groups'])} 个当前身份组进入 S4；每组登记一个 KU |",
        f"| conflict | {fmt(totals['conflict'])} | 冲突两侧与来源依据保留在对齐行，等待解决证据 |",
        f"| excluded | {fmt(totals['excluded'])} | 含 48 项 S1 排除及其余 S3 类型/对象边界排除 |",
        f"| undecided | {fmt(totals['undecided'])} | 保留对象、版本、身份、类型或来源方面的逐项未决理由及证据去向 |",
        f"| **合计** | **{fmt(n_decisions)}** | 每个候选一条当前决定记录 |",
    ])
    result = result[:table_start] + s3_table + result[table_end:]

    matrix_marker = "| 类型 | same（候选→KU） | new（候选／组） | S4 新组（已登记／待登记；待登候选） | conflict | excluded | undecided |"
    matrix_start = result.index(matrix_marker)
    matrix_end = result.index("\n\n", matrix_start)
    type_table, _ = build_type_table(stats)
    result = result[:matrix_start] + type_table + result[matrix_end:]

    # Keep the artifacts section current and avoid maintaining a duplicated KU inventory.
    artifact_pattern = re.compile(r"^\| \[KU 登记\]\(\.\./tables/ku-manifest\.csv\) \|.*$", re.M)
    replacement = (
        f"| [KU 登记](../tables/ku-manifest.csv) | {fmt(manifest_count)} KU；"
        "新组登记与待登记分类型统计见下表 |"
    )
    result, n = artifact_pattern.subn(replacement, result, count=1)
    assert n == 1, "could not simplify current manifest artifact row"
    return result


def main():
    parser = argparse.ArgumentParser(description="Register the annual Pantheon St Joseph's Day exhibition event in S4.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    candidate_decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE].get("suggested_type") == "event"
    alignment = candidate_decisions[CANDIDATE]
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment.get("resolution_note", "")) == GROUP
    group_rows = [
        row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
        and row.get("decision") == "new" and get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == [CANDIDATE]
    assert not CARD_PATH.exists()
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL not in accepted
    assert not any(
        row.get("type") == "event"
        and (row.get("name_en") == NAME_EN or row.get("canonical_name") == NAME_ZH)
        for row in manifest
    ), "same-title event already exists in manifest"

    source = ROOT / SOURCE_FILE
    source_text = " ".join(source.read_text(encoding="utf-8-sig").split())
    for item in SOURCES:
        for _, quote in item["quotes"]:
            assert " ".join(quote.split()) in source_text, (item["location"], quote)

    statements = load_statements()
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE
    ]
    direct_relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    assert len(direct) == 19, f"unexpected direct statement count: {len(direct)}"
    assert len(direct_relations) == 12, f"unexpected direct relation candidate count: {len(direct_relations)}"

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

    stats = summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["total"] == len(candidate_by_id)
    assert totals["registered_groups"] + totals["pending_groups"] == totals["new_groups"]
    assert totals["registered_members"] + totals["pending_members"] == totals["new_candidates"]
    result_text = update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(planned_manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S4 event：万神殿圣约瑟节年度展览身份组登记（2026-10-16）\n\n"
        f"`{CANDIDATE}`（`{GROUP}`）映射至[年度展览事件卡](../../../04-knowledge/units/events/annual-st-josephs-day-exhibition-pantheon.md)。"
        "身份粒度为每年3月19日的重复展览系列；A.csv#132 的泛称术语候选 `cand-0131` 仍为 `undecided`，只提供索引定位，未并入事件。"
        "组织者 `cand-0821` 与地点 `cand-4236` 是各自独立的 S3 new 组，尚待 S4；书中1680年具体场次候选 `cand-6047` 仍待身份裁决。"
        "第5章 pp.126–127 记载节日日期、组织者、遴选与陈列、1650年示例和1680年扣押命令；所引段落称系列可能始于17世纪初、1764年前某时结束，"
        "扫描印刷页确认 OCR 的“17Ó4”读作1764，首末届精确日期未定。19条直接 S2 陈述中12条关系候选保留至 S6，未登记正式关系或开展 S5。"
        f"S4 累计登记{fmt(totals['registered_groups'])}组/{fmt(totals['registered_members'])}条成员映射，待登记{fmt(totals['pending_groups'])}组/{fmt(totals['pending_members'])}条。"
    )
    result_note = (
        "\n\n### event：万神殿圣约瑟节年度展览 S4 登记（2026-10-16）\n\n"
        f"`{CANDIDATE}` 映射至[年度展览事件卡](../units/events/annual-st-josephs-day-exhibition-pantheon.md)。"
        "该卡登记每年3月19日举行的重复展览系列；泛称索引术语、组织者机构、Pantheon 地点和1680年具体场次各自保持身份边界。"
        "第5章 pp.126–127 记载其日期、组织和展陈方式，以及1650年展出肖像和1680年当局下令扣押画作的例子；后者只记命令，不断言已经执行。"
        "系列起始时间为原书所称“可能”在17世纪初，结束于1764年前某时；OCR读数经扫描印刷页确认，首末届精确日期未定。"
        "19条直接陈述中12条关系候选留待 S6；本轮未新增正式关系或开展 S5。"
        f"全书 S4 当前登记{fmt(totals['registered_groups'])}组/{fmt(totals['registered_members'])}条映射，待登记{fmt(totals['pending_groups'])}组/{fmt(totals['pending_members'])}条。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print(f"S4 event dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"identity group members={len(group_rows)}; direct statements={len(direct)}; relation candidates={len(direct_relations)}")
        print(f"source quotations checked={sum(len(x['quotes']) for x in SOURCES)}; event identity remains distinct from 1680 candidate cand-6047")
        print(f"manifest={len(manifest):,} -> {len(planned_manifest):,}; accepted path unique")
        print(f"registered={fmt(totals['registered_groups'])} groups/{fmt(totals['registered_members'])} candidates; pending={fmt(totals['pending_groups'])} groups/{fmt(totals['pending_members'])} candidates")
        print("S3 and type-level result counts refreshed in preview; no files changed")
        return 0

    CARD_PATH.write_text(make_card(), encoding="utf-8-sig", newline="\n")
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
        f"registered={fmt(totals['registered_groups'])}/{fmt(totals['registered_members'])}; "
        f"pending={fmt(totals['pending_groups'])}/{fmt(totals['pending_members'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
