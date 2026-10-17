from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
CANDIDATE_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
SOURCE_PATH = ROOT / "02-sources" / "02-Markdown" / "08_CHP-8_sec_i.md"
GROUP_BROTHERS = "new-person:andrea-del-rosso-670cf89453"
GROUP_GRANDFATHER = "new-person:andrea-del-rosso-grandfather-2279"
PROCESS_REF = "S3-full-book-2026-10-16"


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
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def update_process(text):
    text = replace_once(
        text,
        "4,988 条 `new` 候选当前分为 4,818 个新身份组，其中 133 组含多个候选。",
        "4,988 条 `new` 候选当前分为 4,819 个新身份组，其中 133 组含多个候选。",
        "current S3 group and multi-candidate counts",
    )
    text = replace_once(
        text,
        "当前有 4,988 个 `new` 身份候选、4,818 个新身份组；",
        "当前有 4,988 个 `new` 身份候选、4,819 个新身份组；",
        "S3 closure current group count",
    )
    text = replace_once(
        text,
        "汇总为 4,818 个身份组。",
        "汇总为 4,819 个身份组。",
        "S4 scope group count",
    )
    text = replace_once(
        text,
        "截至 Francesco Marucelli 批次，4,818 个当前 `new` 身份组中完成159组，余4,659组；",
        "截至 Andrea del Rosso 跨代组拆分后、下一 S4 批次前，4,819 个当前 `new` 身份组中完成159组，余4,660组；",
        "current S4 group counts",
    )
    text = replace_once(
        text,
        "person 类型1,085组、1,178条候选，已登记53组、90条候选，待登记1,032组、1,088条候选。",
        "person 类型1,086组、1,178条候选，已登记53组、90条候选，待登记1,033组、1,088条候选。",
        "current S4 person group counts",
    )
    section = """### S3 纠正：Andrea del Rosso 跨代同名人物拆分（2026-10-16）

`cand-2275`（Q-R.csv#203）与 `cand-2279`（Q-R.csv#207）原按相同姓名锚点共组。第8章 p.211 明确称长兄 Andrea 生于1640年，p.211 注释记其于1715年去世；同页另起句称“their grandfather”在1642年距去世两年，p.212 续以 Andrea 指称建造家族礼拜堂的祖父。两者虽同名，代际和生平不相容，必须分开。保留两条候选级 `new` 决定：`cand-2275` 留在 `new-person:andrea-del-rosso-670cf89453`，`cand-2279` 单独归入 `new-person:andrea-del-rosso-grandfather-2279`。旧组并列理由保留在对齐行历史注释。总组数增1至4,819，多候选组减1至133；候选数、已登记组与映射数不变。尚未新建 KU 或关系。

"""
    return replace_once(text, "## S4 KU 登记（2026-10-15）\n\n", section + "## S4 KU 登记（2026-10-15）\n\n", "S3 reconciliation insertion")


def update_result(text):
    text = replace_once(
        text,
        "4,988条 `new` 候选、4,818个当前身份组；目前完成159组、映射203条成员候选，余4,659组、4,785条映射。",
        "4,988条 `new` 候选、4,819个当前身份组；目前完成159组、映射203条成员候选，余4,660组、4,785条映射。",
        "result current S4 group counts",
    )
    text = replace_once(
        text,
        "| new | 4,988 | 按 4,818 个当前身份组进入 S4；",
        "| new | 4,988 | 按 4,819 个当前身份组进入 S4；",
        "result S3 new group count",
    )
    text = replace_once(
        text,
        "当前尚余4,659个 `new` 身份组、4,785条成员候选映射；",
        "当前尚余4,660个 `new` 身份组、4,785条成员候选映射；",
        "result current unregistered group count",
    )
    text = replace_once(
        text,
        "person 类型1,085组、1,178条候选，已登记53组、90条候选，待登记1,032组、1,088条候选。",
        "person 类型1,086组、1,178条候选，已登记53组、90条候选，待登记1,033组、1,088条候选。",
        "result current person group counts",
    )
    section = """### S3 更正：Andrea del Rosso 跨代同名人物拆分（2026-10-16）

`cand-2275`（Q-R.csv#203，兄弟中的长兄）与 `cand-2279`（Q-R.csv#207，兄弟的祖父）原被相同姓名锚点误并。第8章 p.211 记长兄 Andrea 生于1640年、1715年去世；同页明确转述祖父在1642年距去世两年，p.212 续述该祖父 Andrea 建造家族礼拜堂。证据表明这是两代同名人物，不能作为同一 KU。现维持两条 `new` 决定并拆为两个组：长兄 `new-person:andrea-del-rosso-670cf89453`，祖父 `new-person:andrea-del-rosso-grandfather-2279`。复核脚本核对原文、4条对应 S2 断言和既有 manifest；旧组理由保留在对齐注释。本次不新增 KU、外部身份记录或正式关系。`new` 候选仍为4,988条，身份组增至4,819组，多候选组减至133组；S4 已登记159组、203条映射不变。

"""
    return replace_once(text, "### S2 端点校正：Francesco Bracciolini", section + "### S2 端点校正：Francesco Bracciolini", "result S3 reconciliation insertion")


def main():
    parser = argparse.ArgumentParser(description="Separate the two source-distinguished generations named Andrea del Rosso")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(CANDIDATE_PATH)
    _, manifest = read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    rows = [row for row in alignment_by_id.values()]
    decision_counts = Counter(row["decision"] for row in rows)
    assert decision_counts == Counter({"same": 1698, "new": 4988, "undecided": 5614, "excluded": 97, "conflict": 7}), decision_counts

    brothers = candidate_by_id["cand-2275"]
    grandfather = candidate_by_id["cand-2279"]
    brothers_alignment = alignment_by_id["cand-2275"]
    grandfather_alignment = alignment_by_id["cand-2279"]
    assert brothers["suggested_type"] == grandfather["suggested_type"] == "person"
    assert brothers["index_entry_id"] == "Q-R.csv#203" and grandfather["index_entry_id"] == "Q-R.csv#207"
    assert brothers_alignment["decision"] == grandfather_alignment["decision"] == "new"
    assert not brothers_alignment.get("ku_id") and not grandfather_alignment.get("ku_id")
    assert group_of(brothers_alignment["resolution_note"]) == group_of(grandfather_alignment["resolution_note"]) == GROUP_BROTHERS
    assert not any(row["type"] == "person" and "andrea del rosso" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)

    source_text = SOURCE_PATH.read_text(encoding="utf-8-sig")
    for quote in (
        "Andrea, the eldest of the brothers, who was born in 1640",
        "In 1642, two years before his death, their grandfather",
        "Andrea had had built in the Theatine church of S. Gaetano a sumptuous family chapel",
        "Ottavio died in 1714, Andrea in 1715",
    ):
        assert quote in source_text, quote

    expected_statements = {
        "st-chp8-p211-andrea-born-and-flour-monopoly",
        "st-chp8-p211-andrea-died-1715",
        "st-chp8-p211-forebears-grandfather-open",
        "st-chp8-p212-grandfather-andrea-built-chapel",
    }
    found = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("statement_id") in expected_statements:
                found[row["statement_id"]] = row
    assert set(found) == expected_statements, set(found)
    assert all("cand-2275" in (row.get("subject_candidate_id"), row.get("object_candidate_id")) for key, row in found.items() if "grandfather" not in key and "chapel" not in key)
    assert all("cand-2279" in (row.get("subject_candidate_id"), row.get("object_candidate_id")) for key, row in found.items() if "grandfather" in key or "chapel" in key)

    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    parent_note = planned_by_id["cand-2275"]["resolution_note"]
    target_note = planned_by_id["cand-2279"]["resolution_note"]
    planned_by_id["cand-2275"]["resolution_note"] += (
        " S3 grouping correction 2026-10-16: cand-2279 was separated as the explicitly identified grandfather, "
        "a different generation from this Andrea; the former shared-name rationale is preserved above."
    )
    planned_target = planned_by_id["cand-2279"]
    planned_target["process_ref"] = PROCESS_REF
    planned_target["resolution_note"] = (
        "source_ref=candidate=cand-2279;index_entry=Q-R.csv#207;index_pages=211, 212;"
        "s2_statements=st-chp8-p211-forebears-grandfather-open,st-chp8-p212-grandfather-andrea-built-chapel;"
        f"group={GROUP_GRANDFATHER}; same-name person distinct by generation: the source identifies this Andrea as "
        "the brothers' grandfather, already dead two years after 1642, whereas cand-2275 is the eldest brother, "
        "born in 1640 and reported dead in 1715. The p.212 chapel statement continues the grandfather account; "
        "no external identity source was accessed. Previous grouping rationale retained verbatim: " + target_note
    )

    planned_rows = [row for row in planned if row.get("candidate_id") and not row.get("external_source")]
    assert Counter(row["decision"] for row in planned_rows) == decision_counts
    new_rows = [row for row in planned_rows if row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = group_of(row["resolution_note"])
        assert group
        groups[group].append(row)
    assert len(groups) == 4819 and len(new_rows) == 4988
    assert len(groups[GROUP_BROTHERS]) == 1 and len(groups[GROUP_GRANDFATHER]) == 1
    assert sum(len(group_rows) > 1 for group_rows in groups.values()) == 133
    registered = defaultdict(list)
    for row in new_rows:
        if row.get("ku_id"):
            registered[group_of(row["resolution_note"])].append(row)
    assert len(registered) == 159 and sum(map(len, registered.values())) == 203
    assert GROUP_GRANDFATHER not in registered

    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))

    if args.dry_run:
        print(
            "dry-run passed: cand-2279 separated from cand-2275; candidate decisions unchanged; "
            "new_groups=4819 multi_candidate_groups=133 registered=159/203; four S2 statements verified; no KU or relation write"
        )
        return 0

    write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: cand-2279 has a separate source-backed S3 identity group; prior grouping rationale retained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
