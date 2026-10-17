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
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
STATEMENTS = TABLES / "book-statements.jsonl"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
EXISTING_KU = "units/persons/romanelli"
EXISTING_GROUP = "sg3-ku-units-persons-romanelli"
EXISTING_CANDIDATE = "cand-3878"
TARGET = "cand-2208"
OLD_NEW_GROUP = "new-person:francesco-giovan-romanelli-9cc80a7086"
PROCESS_REF = "S3-Romanelli-cross-chapter-identity-reconciliation-2026-10-16"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def group_of(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def grouped_ids(rows, decision):
    groups = defaultdict(set)
    for row in rows:
        if row["decision"] == decision:
            group = group_of(row.get("resolution_note", ""))
            assert group, f"{decision} candidate lacks group: {row['candidate_id']}"
            groups[group].add(row["candidate_id"])
    return groups


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def updated_process(text):
    text = replace_once(
        text,
        "其中 277 组包含多个候选。S4 新增的 KU 不计入 `same` 组。经跨章复核，4,988 条 `new` 候选当前分为 4,819 个新身份组，其中 133 组含多个候选。",
        "其中 278 组包含多个候选。S4 新增的 KU 不计入 `same` 组。经跨章复核，4,988 条 `new` 候选当前分为 4,818 个新身份组，其中 133 组含多个候选。",
        "process S3 current group summary",
    )
    text = replace_once(
        text,
        "| person | 3,469 | 963 | 1,179 | 2 | 7 | 1,318 |",
        "| person | 3,469 | 964 | 1,178 | 2 | 7 | 1,318 |",
        "process S3 person decision row",
    )
    text = replace_once(
        text,
        "| **合计** | **12,404** | **1,697** | **4,988** | **7** | **97** | **5,615** |",
        "| **合计** | **12,404** | **1,698** | **4,988** | **7** | **97** | **5,614** |",
        "process S3 total decision row",
    )
    text = replace_once(
        text,
        "当前有 4,989 个 `new` 身份候选、4,819 个新身份组；",
        "当前有 4,988 个 `new` 身份候选、4,818 个新身份组；",
        "process S3 closure counts",
    )
    text = replace_once(
        text,
        "### S3 补充裁决：Pierre Crozat 索引子目并入跨章人物组（2026-10-16）\n",
        "### S3 补充裁决：Giovan Francesco Romanelli 复用既有人物 KU（2026-10-16）\n\n`cand-2208`（Q-R.csv#135，Romanelli, Giovan Francesco）原为 `new-person:francesco-giovan-romanelli-9cc80a7086`。第7章 p.181 以 Giovan Francesco Romanelli 指称 Francesco Barberini 的 favorite painter，随后连续叙述其绘制 Mazarin 画廊上层画廊及《罗慕路斯与雷穆斯》；既有 `units/persons/romanelli` 卡片以 Giovanni Francesco Romanelli 为全名，记录同一画廊和图版26b，且候选 `cand-3878` 已映射到该 KU。据全名异写、人物角色和同一作品/委托语境，将 `cand-2208` 从 `new` 更正为 `same`，并入 `sg3-ku-units-persons-romanelli`。原 `new` 组及理由保存在对齐行历史注释；[复核脚本](reconcile_s3_romanelli_existing_identity_20261016.py) dry-run 核对既有卡、accepted/manifest、精确原文和18条直接断言端点（16条关系候选）后 apply。same=1,698、new=4,988、undecided=5,614；same 组数维持1,019，多候选组增至278；new 组降至4,818。S4 manifest 与已登记147组/187条候选映射不变，未登记余4,671组/4,801条候选。未新增外部来源或正式关系。\n\n### S3 补充裁决：Pierre Crozat 索引子目并入跨章人物组（2026-10-16）\n",
        "process Romanelli S3 log",
    )
    text = replace_once(
        text,
        "本轮按当前 S3 裁决需登记 4,989 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 4,819 个身份组。",
        "本轮按当前 S3 裁决需登记 4,988 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 4,818 个身份组。",
        "process S4 initial counts",
    )
    text = replace_once(
        text,
        "截至 Giovanni Vianello 批次，4,819 个当前 `new` 身份组中完成147组，余4,672组；4,989条成员候选中映射187条，余4,802条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记41组、74条候选，待登记1,045组、1,105条候选。",
        "截至 Giovanni Vianello 批次及 Romanelli 复用裁决，4,818 个当前 `new` 身份组中完成147组，余4,671组；4,988条成员候选中映射187条，余4,801条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记41组、74条候选，待登记1,044组、1,104条候选。",
        "process current S4 counts",
    )
    return text


def updated_result(text):
    lines = text.splitlines()
    status_ids = [i for i, line in enumerate(lines) if line.startswith("**当前状态：全书 S2 语义处理已完成")]
    assert len(status_ids) == 1, f"result status lines={len(status_ids)}"
    i = status_ids[0]
    line = replace_once(
        lines[i],
        "本轮 S3 候选级决定闭包已完成；S4 KU 登记处理中。",
        "本轮 S3 候选级决定闭包已完成（含本次 Romanelli 复用补裁决）；S4 KU 登记处理中。",
        "result S3 status note",
    )
    line = replace_once(
        line,
        "S4 需登记4,989条 `new` 候选、4,819个当前身份组；目前完成147组、映射187条成员候选，余4,672组、4,802条映射。",
        "S4 需登记4,988条 `new` 候选、4,818个当前身份组；目前完成147组、映射187条成员候选，余4,671组、4,801条映射。",
        "result S4 status counts",
    )
    lines[i] = line
    text = "\n".join(lines) + "\n"
    text = replace_once(
        text,
        "| same | 1,697 | 指向 S3 开始时既有的 1,019 个 KU；跨章复核净增24条复用决定 |",
        "| same | 1,698 | 指向 S3 开始时既有的 1,019 个 KU；跨章复核净增25条复用决定 |",
        "result S3 same row",
    )
    text = replace_once(
        text,
        "| new | 4,989 | 按 4,819 个当前身份组进入 S4；每组登记一个 KU |",
        "| new | 4,988 | 按 4,818 个当前身份组进入 S4；每组登记一个 KU |",
        "result S3 new row",
    )
    text = replace_once(
        text,
        "当前尚余4,672个 `new` 身份组、4,802条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记41组、74条候选，待登记1,045组、1,105条候选。",
        "当前尚余4,671个 `new` 身份组、4,801条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记41组、74条候选，待登记1,044组、1,104条候选。",
        "result current S4 type counts",
    )
    reconciliation = """### S3 补充裁决：Giovan Francesco Romanelli 复用既有人物 KU（2026-10-16）

`cand-2208`（Q-R.csv#135）原属新人物组；第7章 p.181 以 Giovan Francesco Romanelli 指称 Francesco Barberini 的 favorite painter，继续叙述同一人绘制 Mazarin 画廊上层画廊及《罗慕路斯与雷穆斯》。既有人物 KU `units/persons/romanelli` 以 Giovanni Francesco Romanelli 为全名，记录同一画廊及图版26b；accepted-ku 候选 `cand-3878` 已映射到该卡。故将 `cand-2208` 从 `new` 改为 `same`，并入既有 Romanelli 身份组；原决定理由保留在对齐行历史注释。18条直接 S2 端点中16条为关系候选，仍留待 S6。决定计数现为 same=1,698、new=4,988、undecided=5,614；新身份组4,818个。S4 未登记组减少1组，不改动既有 KU、manifest、accepted.yml 或正式关系。证据与 dry-run/apply 记录见[既有人物卡](../../04-knowledge/units/persons/romanelli.md)和[S3 复核脚本](../../03-processing/patrons-and-painters-full-book-s2/process/reconcile_s3_romanelli_existing_identity_20261016.py)。

"""
    return replace_once(
        text,
        "### person：Giorgio Pisani S4 登记（2026-10-16）\n\n",
        reconciliation + "### person：Giorgio Pisani S4 登记（2026-10-16）\n\n",
        "result Romanelli S3 reconciliation log",
    )


def main():
    parser = argparse.ArgumentParser(description="Map the Giovan Francesco Romanelli candidate to the existing Romanelli person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT)
    _, candidates = read_csv(CANDIDATES)
    _, manifest = read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = decision_rows(alignments)
    decision_by_id = {row["candidate_id"]: row for row in decisions}
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1166, f"unexpected manifest count: {len(manifest)}"
    manifest_row = manifest_by_id[EXISTING_KU]
    assert manifest_row["type"] == "person"
    assert manifest_row["card_path"] == "04-knowledge/units/persons/romanelli.md"
    existing_card = (ROOT / manifest_row["card_path"]).read_text(encoding="utf-8-sig")
    accepted_text = (ROOT / "04-knowledge" / "accepted.yml").read_text(encoding="utf-8-sig")
    assert manifest_row["card_path"] in accepted_text
    for phrase in ("Giovanni Francesco Romanelli", "Romulus and Remus", "Mazarin", "romanelli-romulus-and-remus.md"):
        assert phrase in existing_card, phrase

    target = decision_by_id[TARGET]
    existing = decision_by_id[EXISTING_CANDIDATE]
    assert candidate_by_id[TARGET]["suggested_type"] == "person"
    assert candidate_by_id[TARGET]["canonical_name"] == "Romanelli, Giovan Francesco"
    assert candidate_by_id[TARGET]["index_entry_id"] == "Q-R.csv#135"
    assert candidate_by_id[EXISTING_CANDIDATE]["candidate_origin"] == "accepted-ku"
    assert candidate_by_id[EXISTING_CANDIDATE]["candidate_source_ref"] == manifest_row["card_path"]
    assert target["decision"] == "new" and not target.get("ku_id")
    assert group_of(target["resolution_note"]) == OLD_NEW_GROUP
    assert existing["decision"] == "same" and existing["ku_id"] == EXISTING_KU
    assert group_of(existing["resolution_note"]) == EXISTING_GROUP
    current_new_ids = {
        row["candidate_id"] for row in decisions
        if row["decision"] == "new" and group_of(row.get("resolution_note", "")) == OLD_NEW_GROUP
    }
    assert current_new_ids == {TARGET}

    source_path = ROOT / "02-sources" / "02-Markdown" / "07_CHP-7_sec_i.md"
    source_text = source_path.read_text(encoding="utf-8-sig")
    for quote in (
        "his favourite painter Giovan Francesco Romanelli",
        "painting the newly built upper gallery of\nMazarin’s palace",
        "Romanelli divided the area into a number of oval, circular, rectangular and square compartments",
    ):
        assert quote in source_text, quote

    endpoint_ids = set()
    relation_ids = set()
    with STATEMENTS.open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if TARGET in {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 18 and len(relation_ids) == 16, (len(endpoint_ids), len(relation_ids))

    before = Counter(row["decision"] for row in decisions)
    same_before = grouped_ids(decisions, "same")
    new_before = grouped_ids(decisions, "new")
    assert before == Counter({"same": 1697, "new": 4989, "undecided": 5614, "excluded": 97, "conflict": 7}), before
    assert len(same_before) == 1019 and sum(len(ids) > 1 for ids in same_before.values()) == 277
    assert same_before[EXISTING_GROUP] == {EXISTING_CANDIDATE}
    assert len(new_before) == 4819 and new_before[OLD_NEW_GROUP] == {TARGET}

    registered_before = defaultdict(set)
    for row in decisions:
        if row["decision"] == "new" and row.get("ku_id"):
            registered_before[group_of(row["resolution_note"])].add(row["candidate_id"])
    assert (len(registered_before), sum(map(len, registered_before.values()))) == (147, 187)

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned)}
    target_plan = planned_by_id[TARGET]
    source_prefix, old_tail = target_plan["resolution_note"].split("; group=", 1)
    target_plan["decision"] = "same"
    target_plan["ku_id"] = EXISTING_KU
    target_plan["process_ref"] = PROCESS_REF
    target_plan["resolution_note"] = (
        f"{source_prefix}; group={EXISTING_GROUP}; S3 cross-chapter identity reconciliation: the full-book index candidate "
        "Romanelli, Giovan Francesco names the same painter identified in the accepted front-matter KU as Giovanni Francesco Romanelli. "
        "Chapter 7 p. 181 calls him Francesco Barberini's favourite painter and continues with his work on the Mazarin gallery and the Romulus and Remus ceiling detail; the existing card records the same gallery and Plate 26b. "
        f"The existing accepted-ku candidate {EXISTING_CANDIDATE} already maps to this person KU. Reuse the existing identity; preserve the source spelling variant. "
        "No new external source was accessed. Historical new-group decision and rationale retained: group="
        f"{old_tail}"
    )

    after_rows = decision_rows(planned)
    after = Counter(row["decision"] for row in after_rows)
    assert after == Counter({"same": 1698, "new": 4988, "undecided": 5614, "excluded": 97, "conflict": 7}), after
    same_after = grouped_ids(after_rows, "same")
    new_after = grouped_ids(after_rows, "new")
    assert len(same_after) == 1019 and sum(len(ids) > 1 for ids in same_after.values()) == 278
    assert same_after[EXISTING_GROUP] == {EXISTING_CANDIDATE, TARGET}
    assert len(new_after) == 4818 and OLD_NEW_GROUP not in new_after
    registered_after = defaultdict(set)
    for row in after_rows:
        if row["decision"] == "new" and row.get("ku_id"):
            registered_after[group_of(row["resolution_note"])].add(row["candidate_id"])
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (147, 187)
    pending_groups = {g: ids for g, ids in new_after.items() if g not in registered_after}
    assert (len(pending_groups), sum(map(len, pending_groups.values()))) == (4671, 4801)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    if args.dry_run:
        print(
            f"dry-run passed: {TARGET} new->same {EXISTING_KU}; existing_same_group_candidates=2; "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "same=1697->1698 new=4989->4988 new_groups=4819->4818; "
            "registered_S4_groups=147 unchanged; pending_S4_groups=4671 candidates=4801; "
            "manifest/accepted unchanged; no new external source"
        )
        return 0

    write_csv(ALIGNMENT, alignment_fields, planned)
    PROCESS_PATH.write_text(planned_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(planned_result, encoding="utf-8-sig", newline="\n")
    print(f"applied: {TARGET} mapped to existing Romanelli KU; same={after['same']} new={after['new']} new_groups={len(new_after)} pending_S4={len(pending_groups)} groups/{sum(map(len, pending_groups.values()))} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
