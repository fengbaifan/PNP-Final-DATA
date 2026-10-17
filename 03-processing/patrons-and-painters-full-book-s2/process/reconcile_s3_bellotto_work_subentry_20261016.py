from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
PROCESS = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
PROCESS_REF = "S3-bellotto-work-subentry-2026-10-16"
PERSON_GROUP = "new-person:bellotto-bernardo-3bfd904005"
WORK_GROUP = "sg3-work-bellotto-cross-church-ruins"
MEMBERS = ("cand-0279", "cand-0280", "cand-0281")
WORK_STATEMENT = "st-chp10-p295-cross-church-painting"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_id(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def summarize(alignments, candidates):
    rows = decision_rows(alignments)
    decisions = Counter(row["decision"] for row in rows)
    new_rows = [row for row in rows if row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = group_id(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: members for group, members in groups.items() if any(r.get("ku_id") for r in members)}
    by_type = defaultdict(list)
    for row in new_rows:
        by_type[candidates[row["candidate_id"]]["suggested_type"]].append(row)
    return decisions, groups, registered, by_type


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def update_process(text, totals, groups, registered, by_type):
    new_count = totals["new"]
    reg_members = sum(bool(row.get("ku_id")) for members in registered.values() for row in members)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - reg_members
    pattern = (
        r"(\*\*状态：处理中。\*\* 本轮按当前 S3 裁决需登记 )([\d,]+)"
        r"( 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 )([\d,]+)"
        r"( 个身份组；截至本次复核，已登记 )([\d,]+)( 组、)([\d,]+)"
        r"( 条成员映射，尚待登记 )([\d,]+)( 组、)([\d,]+)( 条。)"
    )
    replacement = (
        rf"\g<1>{new_count:,}\g<3>{len(groups):,}\g<5>{len(registered):,}"
        rf"\g<7>{reg_members:,}\g<9>{pending_groups:,}\g<11>{pending_members:,}\g<13>"
    )
    text, count = re.subn(pattern, replacement, text, count=1)
    assert count == 1, "process current S4 status paragraph did not match"
    person = by_type["person"]
    work = by_type["work"]
    person_groups = {group_id(row["resolution_note"]) for row in person}
    work_groups = {group_id(row["resolution_note"]) for row in work}
    registered_person = {g for g in person_groups if g in registered}
    registered_work = {g for g in work_groups if g in registered}
    text += (
        "\n\n### S3 类型纠偏：Bernardo Bellotto 的作品索引子目（2026-10-16）\n\n"
        "- `cand-0279` 与 `cand-0281` 保留在人物组 `new-person:bellotto-bernardo-3bfd904005`；两条索引主目与第10章 pp.295、298 的 Bernardo Bellotto 指称相互对应。\n"
        "- `cand-0280` 从 person 改为 work，单独进入 `sg3-work-bellotto-cross-church-ruins`。索引 B.csv#129 的子目是“painting of ruins of Church of the Cross, Dresden”；S2 断言 `st-chp10-p295-cross-church-painting` 另列 Bellotto 为人物端点、该绘画为作品端点。\n"
        "- 第10章 p.295 仅支持描述性作品名，不提供原题名、媒材、现藏地或作品存续状态。Dresden Church of the Cross 地点候选保持独立；候选 `cand-9110` 所指的多幅城市景观集合仍为 `undecided`，不与此单件作品合并。无现有同一作品 KU，也未作外部身份核验。原 S3 判断保存在三条对齐行的历史说明中。\n"
        f"- 纠偏后全局 S3：same={totals['same']:,}、new={new_count:,}（{len(groups):,} 组）、undecided={totals['undecided']:,}、conflict={totals['conflict']:,}、excluded={totals['excluded']:,}。person 新组 {len(person_groups):,}/{sum(len(g) for g in [person])} 候选，其中 S4 已登记 {len(registered_person)} 组；work 新组 {len(work_groups):,}/{len(work)} 候选，其中 S4 已登记 {len(registered_work)} 组。\n"
    )
    return text


def update_result(text, totals, groups, registered, by_type):
    new_count = totals["new"]
    reg_members = sum(bool(row.get("ku_id")) for members in registered.values() for row in members)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - reg_members
    text = replace_once(text, "new=5,006（4,835个身份组）", f"new={new_count:,}（{len(groups):,}个身份组）", "current S3 new count")
    text = replace_once(text, "S4 已登记166组、映射213条成员候选；尚待登记4,669组、4,793条映射。", f"S4 已登记{len(registered)}组、映射{reg_members}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。", "current S4 totals")
    text = replace_once(text, "| same | 1,708 |", f"| same | {totals['same']:,} |", "S3 same table row")
    text = replace_once(text, "| new | 5,005 | 按 4,834 个当前身份组进入 S4；每组登记一个 KU |", f"| new | {new_count:,} | 按 {len(groups):,} 个当前身份组进入 S4；每组登记一个 KU |", "S3 new table row")
    text = replace_once(text, "| undecided | 5,586 |", f"| undecided | {totals['undecided']:,} |", "S3 undecided table row")
    person = by_type["person"]
    work = by_type["work"]
    person_groups = {group_id(row["resolution_note"]) for row in person}
    work_groups = {group_id(row["resolution_note"]) for row in work}
    registered_person = {g for g in person_groups if g in registered}
    registered_work = {g for g in work_groups if g in registered}
    person_reg_members = sum(bool(row.get("ku_id")) for row in person)
    work_reg_members = sum(bool(row.get("ku_id")) for row in work)
    person_line = re.compile(r"person\s*类型[\d,]+组/[\d,]+条候选，已登记[\d,]+组/[\d,]+条、待登记[\d,]+组/[\d,]+条")
    text, count = person_line.subn(
        f"person 类型{len(person_groups):,}组/{len(person):,}条候选，已登记{len(registered_person):,}组/{person_reg_members:,}条、待登记{len(person_groups)-len(registered_person):,}组/{len(person)-person_reg_members:,}条",
        text,
        count=1,
    )
    assert count == 1, "result current person type summary did not match"
    work_line = re.compile(r"work\s*[\d,]+组/[\d,]+条")
    text, count = work_line.subn(
        f"work {len(work_groups)-len(registered_work):,}组/{len(work)-work_reg_members:,}条",
        text,
        count=1,
    )
    assert count == 1, "result current work type summary did not match"
    text += (
        "\n\n### S3 类型纠偏：Bernardo Bellotto 的作品索引子目（2026-10-16）\n\n"
        "`cand-0279` 与 `cand-0281` 保留为跨章人物组；`cand-0280` 根据 B.csv#129 的作品子目和第10章 p.295 的 S2 人物—作品端点断言，从 person 改为 work 并新建独立作品组。该卡使用描述性名称，不声称书中给出原题名、媒材或现藏地。教堂地点独立；`cand-9110` 的多幅德累斯顿景观集合继续待证。原决定和本次更正理由均在对齐行留痕。\n"
    )
    return text


def main():
    parser = argparse.ArgumentParser(description="Correct the Bellotto painting sub-entry from person to work and split its S3 identity group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT)
    candidate_fields, candidate_rows = read_csv(CANDIDATES)
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    by_id = {row["candidate_id"]: row for row in decision_rows(alignments)}
    assert set(MEMBERS) <= set(candidates) and set(MEMBERS) <= set(by_id)
    assert all(by_id[cid]["decision"] == "new" and not by_id[cid].get("ku_id") for cid in MEMBERS)
    assert all(group_id(by_id[cid]["resolution_note"]) == PERSON_GROUP for cid in MEMBERS)
    assert all(candidates[cid]["suggested_type"] == "person" for cid in MEMBERS)
    assert candidates["cand-0280"]["index_entry_id"] == "B.csv#127"
    assert candidates["cand-0280"]["sub_entry"] == "painting of ruins of Church of the Cross, Dresden"
    assert not any(r.get("ku_id") == "units/works/bellotto-ruins-church-of-the-cross-dresden" for r in read_csv(TABLES / "ku-manifest.csv")[1])

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    statement = next(row for row in statements if row.get("statement_id") == WORK_STATEMENT)
    assert statement["subject_candidate_id"] == "cand-0279" and statement["object_candidate_id"] == "cand-0280"
    assert "Bellotto stayed just long enough" in statement["qualifiers"]["claim"]
    source = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "to paint the ruins of the Church of the Cross which had been wrecked" in source

    before, groups_before, registered_before, _ = summarize(alignments, candidates)
    assert before == Counter({"same": 1717, "new": 5006, "undecided": 5576, "excluded": 98, "conflict": 7}), dict(before)
    assert len(groups_before) == 4835 and len(registered_before) == 166

    old_notes = {cid: by_id[cid]["resolution_note"] for cid in MEMBERS}
    for cid in ("cand-0279", "cand-0281"):
        note = by_id[cid]["resolution_note"]
        by_id[cid]["process_ref"] = PROCESS_REF
        by_id[cid]["resolution_note"] = (
            f"source_ref={note.split(';', 1)[0].removeprefix('source_ref=')}; group={PERSON_GROUP}; "
            "S3 Bellotto type correction 2026-10-16: retained in the person group with the other full-name person anchor; "
            "cand-0280 is excluded from this person group and assigned to its source-attested work group. "
            f"Prior S3 resolution retained verbatim as history: {old_notes[cid]}"
        )

    work_note = by_id["cand-0280"]["resolution_note"]
    by_id["cand-0280"]["process_ref"] = PROCESS_REF
    by_id["cand-0280"]["resolution_note"] = (
        "source_ref=candidate=cand-0280;index_entry=B.csv#127;index_pages=295;"
        f"s2_statement={WORK_STATEMENT}@chp-10:10_CHP-10_intro:l304-316#L315; group={WORK_GROUP}; "
        "S3 type correction 2026-10-16: person -> work. The index sub-entry names a painting of the ruins of Dresden's Church of the Cross, "
        "and S2 explicitly models Bellotto as its creator/person endpoint and this candidate as the work endpoint. "
        "The Church remains a distinct place candidate; cand-9110's broader Dresden views remain undecided, so no merge is inferred. "
        "No existing same-work KU or external identity source was found/consulted. "
        f"Prior S3 resolution retained verbatim as history: {work_note}"
    )
    candidates["cand-0280"]["suggested_type"] = "work"

    after, groups_after, registered_after, types_after = summarize(alignments, candidates)
    assert after == before and len(groups_after) == 4836 and len(registered_after) == 166
    assert group_id(by_id["cand-0280"]["resolution_note"]) == WORK_GROUP
    assert group_id(by_id["cand-0279"]["resolution_note"]) == PERSON_GROUP
    assert group_id(by_id["cand-0281"]["resolution_note"]) == PERSON_GROUP
    assert len(types_after["person"]) == 1177 and len(types_after["work"]) == 494
    process_text = update_process(PROCESS.read_text(encoding="utf-8-sig"), after, groups_after, registered_after, types_after)
    result_text = update_result(RESULT.read_text(encoding="utf-8-sig"), after, groups_after, registered_after, types_after)

    print("S3 Bellotto work-subentry type correction dry-run passed")
    print("decisions unchanged:", dict(after))
    print("new identity groups: 4,835 -> 4,836; new candidates remain 5,006")
    print("S4 pending after correction: 4,670 groups / 4,793 candidates")
    print("person pending: 1,028 groups / 1,081 candidates; work pending: 480 groups / 493 candidates")
    print("cand-0279/cand-0281 remain person; cand-0280 becomes work in a distinct group")
    if args.dry_run:
        print("dry-run only; no files changed")
        return 0
    write_csv(ALIGNMENT, alignment_fields, alignments)
    write_csv(CANDIDATES, candidate_fields, candidate_rows)
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: S3 type/group correction, preserved prior rationale, process record, and current result counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
