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
PROCESS_REF = "S3-pietro-monaco-index-subentry-2026-10-16"
GROUP = "new-person:monaco-pietro-2f390e5d35"
MEMBERS = ("cand-1682", "cand-1683")


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def group_id(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def decision_rows(rows):
    return [r for r in rows if r.get("candidate_id") and not r.get("external_source")]


def summarize(alignments, candidates):
    rows = decision_rows(alignments)
    decisions = Counter(r["decision"] for r in rows)
    new = [r for r in rows if r["decision"] == "new"]
    groups = defaultdict(list)
    by_type = defaultdict(list)
    for row in new:
        group = group_id(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
        by_type[candidates[row["candidate_id"]]["suggested_type"]].append(row)
    registered = {g: rr for g, rr in groups.items() if any(r.get("ku_id") for r in rr)}
    return decisions, groups, registered, by_type


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def update_process(text, decisions, groups, registered, by_type):
    new_count = decisions["new"]
    mapped = sum(bool(r.get("ku_id")) for rr in registered.values() for r in rr)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - mapped
    pattern = (
        r"(\*\*状态：处理中。\*\* 本轮按当前 S3 裁决需登记 )([\d,]+)"
        r"( 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 )([\d,]+)"
        r"( 个身份组；截至本次复核，已登记 )([\d,]+)( 组、)([\d,]+)"
        r"( 条成员映射，尚待登记 )([\d,]+)( 组、)([\d,]+)( 条。)"
    )
    replacement = (
        rf"\g<1>{new_count:,}\g<3>{len(groups):,}\g<5>{len(registered):,}"
        rf"\g<7>{mapped:,}\g<9>{pending_groups:,}\g<11>{pending_members:,}\g<13>"
    )
    text, count = re.subn(pattern, replacement, text, count=1)
    assert count == 1, "process current S4 status paragraph did not match"
    person = by_type["person"]
    person_groups = {group_id(r["resolution_note"]) for r in person}
    registered_person = {g for g in person_groups if g in registered}
    person_mapped = sum(bool(r.get("ku_id")) for r in person)
    text += (
        "\n\n### S3 身份补裁：Pietro Monaco 经纪活动索引子目归组（2026-10-16）\n\n"
        "- `cand-1682`（M.csv#222，pp.342n、345）与 `cand-1683`（M.csv#223，“activities as dealer”）均为同一 Pietro Monaco 主目下的人物候选。p.342 注5称其为版画师；p.345 正文称“Monaco himself”，并称其用版画宣传本人经纪活动；同页索引子目对应此活动，支持并入同一人物身份组。\n"
        "- `cand-1683` 从 `undecided` 裁为 `new`，归入 `new-person:monaco-pietro-2f390e5d35`，与 `cand-1682` 共用一个 S4 KU。保留 Haskell 对宣传意图的“almost certainly”限定；版画、出版物及其他 Monaco 同名候选不据此合并。旧待证理由与新证据去向均保存在对齐行。原注释提及的版画与书目未独立查阅。\n"
        f"- 更新后全局 S3：same={decisions['same']:,}、new={new_count:,}（{len(groups):,} 组）、undecided={decisions['undecided']:,}、conflict={decisions['conflict']:,}、excluded={decisions['excluded']:,}。person 新组 {len(person_groups):,} 组/{len(person):,} 候选，S4 已登记 {len(registered_person)} 组/{person_mapped} 条，待登记 {len(person_groups)-len(registered_person):,} 组/{len(person)-person_mapped:,} 条。\n"
    )
    return text


def update_result(text, decisions, groups, registered, by_type):
    new_count = decisions["new"]
    mapped = sum(bool(r.get("ku_id")) for rr in registered.values() for r in rr)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - mapped
    text = replace_once(text, "new=5,006（4,838个身份组）", f"new={new_count:,}（{len(groups):,}个身份组）", "current S3 new count")
    text = replace_once(text, "undecided=5,576。", f"undecided={decisions['undecided']:,}。", "current S3 undecided count")
    text = replace_once(text, "S4 已登记172组、映射221条成员候选；尚待登记4,666组、4,785条映射。", f"S4 已登记{len(registered)}组、映射{mapped}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。", "current S4 totals")
    text = replace_once(text, "| new | 5,006 | 按 4,838 个当前身份组进入 S4；每组登记一个 KU |", f"| new | {new_count:,} | 按 {len(groups):,} 个当前身份组进入 S4；每组登记一个 KU |", "S3 new table row")
    text = replace_once(text, "| undecided | 5,576 |", f"| undecided | {decisions['undecided']:,} |", "S3 undecided table row")
    person = by_type["person"]
    person_groups = {group_id(r["resolution_note"]) for r in person}
    registered_person = {g for g in person_groups if g in registered}
    person_mapped = sum(bool(r.get("ku_id")) for r in person)
    person_line = re.compile(r"person\s*类型[\d,]+组/[\d,]+条候选，已登记[\d,]+组/[\d,]+条、待登记[\d,]+组/[\d,]+条")
    text, count = person_line.subn(
        f"person 类型{len(person_groups):,}组/{len(person):,}条候选，已登记{len(registered_person)}组/{person_mapped:,}条、待登记{len(person_groups)-len(registered_person):,}组/{len(person)-person_mapped:,}条",
        text,
        count=1,
    )
    assert count == 1, "result current person type summary did not match"
    text += (
        "\n\n### S3 身份补裁：Pietro Monaco 经纪活动索引子目归组（2026-10-16）\n\n"
        "`cand-1683`（M.csv#223，“activities as dealer”）不再保留为待证：它是 `cand-1682`（M.csv#222）同一 Pietro Monaco 主目下的索引子目，p.345 正文又称“Monaco himself”并叙述其经纪活动。两项候选合并进入一个人物组；Haskell 对用版画宣传经纪业务的推断仍保留“almost certainly”限定。旧待证理由和复裁证据均见对齐行及过程记录。"
    )
    return text


def main():
    parser = argparse.ArgumentParser(description="Resolve the Pietro Monaco dealer-activity index sub-entry into its existing person group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT)
    candidate_fields, candidate_rows = read_csv(CANDIDATES)
    candidates = {r["candidate_id"]: r for r in candidate_rows}
    by_id = {r["candidate_id"]: r for r in decision_rows(alignments)}
    assert set(MEMBERS) <= set(candidates) and set(MEMBERS) <= set(by_id)
    assert by_id["cand-1682"]["decision"] == "new" and group_id(by_id["cand-1682"]["resolution_note"]) == GROUP
    assert by_id["cand-1683"]["decision"] == "undecided" and not by_id["cand-1683"].get("ku_id")
    assert candidates["cand-1682"]["suggested_type"] == candidates["cand-1683"]["suggested_type"] == "person"
    assert candidates["cand-1682"]["index_entry_id"] == "M.csv#222" and candidates["cand-1683"]["index_entry_id"] == "M.csv#223"
    assert candidates["cand-1683"]["sub_entry"] == "activities as dealer"

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    dealer_statement = next(r for r in statements if r.get("statement_id") == "st-chp13-p345-monaco-collection-advertised-dealer")
    engraver_statement = next(r for r in statements if r.get("statement_id") == "st-chp13-p345-monaco-engraver-role")
    assert dealer_statement["subject_candidate_id"] == "cand-1682"
    assert engraver_statement["subject_candidate_id"] == "cand-1682"
    assert "almost certainly" in dealer_statement["qualifiers"]["claim"]
    self_reference = next(r for r in statements if r.get("statement_id") == "st-chp13-p345-monaco-reproduced-work-groups")
    assert "Monaco himself" in self_reference["original_quote"]
    assert self_reference["object_candidate_id"] == "cand-1682"
    source = (ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md").read_text(encoding="utf-8-sig")
    assert "the engraver Pietro Monaco" in source and "Monaco himself" in source and "activities as a dealer" in source
    assert not any("Pietro Monaco" == row.get("name_en") for row in read_csv(TABLES / "ku-manifest.csv")[1])

    before, groups_before, registered_before, _ = summarize(alignments, candidates)
    assert before == Counter({"same": 1717, "new": 5006, "undecided": 5576, "excluded": 98, "conflict": 7}), dict(before)
    assert len(groups_before) == 4838 and len(registered_before) == 172
    assert len(groups_before[GROUP]) == 1 and groups_before[GROUP][0]["candidate_id"] == "cand-1682"
    old_person_note = by_id["cand-1682"]["resolution_note"]
    old_undecided_note = by_id["cand-1683"]["resolution_note"]
    by_id["cand-1682"]["process_ref"] = PROCESS_REF
    by_id["cand-1682"]["resolution_note"] += (
        " S3 Monaco identity review 2026-10-16: cand-1683 is added to this person group because the shared M.csv heading and p.345 text identify the dealer-activity sub-entry as the same 'Monaco himself' named as engraver."
    )
    person_detail = (
        "P.342 note 5 names Pietro Monaco as engraver of nos. 41 and 84 in Raccolta di Opere scelte; p.345 index sub-entry 'activities as dealer' and the matching 'Monaco himself' passage concern the same named person. The publication and prints were not independently consulted."
    )
    candidates["cand-1682"]["detail"] = person_detail
    candidates["cand-1683"]["detail"] = (
        "Index sub-entry M.csv#223 lists 'activities as dealer' under Pietro Monaco; p.345 describes the same named Monaco as an engraver who engaged in dealer activity. "
        "The source's 'almost certainly' qualifies his proposed advertising purpose, not the person's identity."
    )
    by_id["cand-1683"]["decision"] = "new"
    by_id["cand-1683"]["ku_id"] = ""
    by_id["cand-1683"]["process_ref"] = PROCESS_REF
    by_id["cand-1683"]["resolution_note"] = (
        "source_ref=candidate=cand-1683;index_entry=M.csv#223;index_pages=345;"
        "s2_statements=st-chp13-p345-monaco-collection-advertised-dealer,st-chp13-p345-monaco-reproduced-work-groups@chp-13:13_CHP-13_intro:l161-171#L166-168; "
        f"group={GROUP}; S3 identity review 2026-10-16: undecided -> new. The sub-entry 'activities as dealer' belongs to the same Pietro Monaco main heading as M.csv#222; p.345 calls the same engraver 'Monaco himself' and describes his dealer activity. "
        "The source's 'almost certainly' qualifies the proposed advertising purpose, not the person's identity. Keep the print collection, individual engravings, and unrelated Monaco candidates separate. "
        f"Prior S3 resolution retained verbatim as history: {old_undecided_note}"
    )

    after, groups_after, registered_after, types_after = summarize(alignments, candidates)
    expected = Counter({"same": 1717, "new": 5007, "undecided": 5575, "excluded": 98, "conflict": 7})
    assert after == expected, dict(after)
    assert len(groups_after) == 4838 and len(registered_after) == 172
    assert {r["candidate_id"] for r in groups_after[GROUP]} == set(MEMBERS)
    assert len(types_after["person"]) == 1176
    process_text = update_process(PROCESS.read_text(encoding="utf-8-sig"), after, groups_after, registered_after, types_after)
    result_text = update_result(RESULT.read_text(encoding="utf-8-sig"), after, groups_after, registered_after, types_after)

    print("S3 Pietro Monaco index-subentry identity correction dry-run passed")
    print("decisions:", dict(after))
    print("new group count remains 4,838; new candidates: 5,006 -> 5,007")
    print("S4 registered remains 172 groups/221 candidates; pending=4,666 groups/4,786 candidates")
    print("cand-1682 and cand-1683 share one person group; prior undecided rationale retained")
    if args.dry_run:
        print("dry-run only; no files changed")
        return 0
    write_csv(ALIGNMENT, alignment_fields, alignments)
    write_csv(CANDIDATES, candidate_fields, candidate_rows)
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: S3 candidate decision/grouping, preserved prior rationale, process record, and current result counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
