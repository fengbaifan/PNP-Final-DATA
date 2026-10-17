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
PROCESS_REF = "S3-bellucci-canons-work-subentries-2026-10-16"
PERSON_GROUP = "new-person:antonio-bellucci-f1e7b7cdb6"
WORK_GROUPS = {
    "cand-0283": "sg3-work-bellucci-canons-descent-from-cross",
    "cand-0284": "sg3-work-bellucci-canons-nativity",
}
WORK_CANDIDATES = set(WORK_GROUPS)
MEMBERS = ("cand-0282", "cand-0283", "cand-0284")
STATEMENT_ID = "st-chp10-p281-bellucci-canons-large-canvases"


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
    person_groups = {group_id(r["resolution_note"]) for r in by_type["person"]}
    work_groups = {group_id(r["resolution_note"]) for r in by_type["work"]}
    registered_person = {g for g in person_groups if g in registered}
    registered_work = {g for g in work_groups if g in registered}
    person_mapped = sum(bool(r.get("ku_id")) for r in by_type["person"])
    work_mapped = sum(bool(r.get("ku_id")) for r in by_type["work"])
    text += (
        "\n\n### S3 类型纠偏：Antonio Bellucci 的 Canons 天花作品索引子目（2026-10-16）\n\n"
        "- `cand-0282` 保留为人物组 `new-person:antonio-bellucci-f1e7b7cdb6`；`cand-0283`（“Descent from the Cross”）与 `cand-0284`（“Nativity”）根据 B.csv#130–131 和第10章 p.281，从 person 改为 work，并各自进入独立作品组。\n"
        f"- S2 断言 `{STATEMENT_ID}` 将三幅大型天花画分别列为 The Nativity、The Descent from the Cross、The Ascension，并将前两项映射至索引子目；故两件作品不并为一件，也不并入 `cand-8945` 所指的三幅画集合。原 S3 分组理由保存在对齐行历史说明中。\n"
        "- 作品名按索引主题作描述性呈现；本次未补原题名、单件媒材、尺寸或现状。未发现同一 Bellucci/Canons 作品 KU，未作外部核验。\n"
        f"- 纠偏后全局 S3：same={totals['same']:,}、new={new_count:,}（{len(groups):,} 组）、undecided={totals['undecided']:,}、conflict={totals['conflict']:,}、excluded={totals['excluded']:,}。person 新组 {len(person_groups):,} 组/{len(by_type['person']):,} 候选，已登记 {len(registered_person)} 组/{person_mapped} 候选；work 新组 {len(work_groups):,} 组/{len(by_type['work']):,} 候选，已登记 {len(registered_work)} 组/{work_mapped} 候选。\n"
    )
    return text


def update_result(text, totals, groups, registered, by_type):
    new_count = totals["new"]
    reg_members = sum(bool(row.get("ku_id")) for members in registered.values() for row in members)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - reg_members
    text = replace_once(text, "new=5,006（4,836个身份组）", f"new={new_count:,}（{len(groups):,}个身份组）", "current S3 new count")
    text = replace_once(text, "| new | 5,006 | 按 4,836 个当前身份组进入 S4；每组登记一个 KU |", f"| new | {new_count:,} | 按 {len(groups):,} 个当前身份组进入 S4；每组登记一个 KU |", "S3 new table row")
    text = replace_once(text, "S4 已登记168组、映射216条成员候选；尚待登记4,668组、4,790条映射。", f"S4 已登记{len(registered)}组、映射{reg_members}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。", "current S4 totals")
    person = by_type["person"]
    work = by_type["work"]
    person_groups = {group_id(r["resolution_note"]) for r in person}
    work_groups = {group_id(r["resolution_note"]) for r in work}
    registered_person = {g for g in person_groups if g in registered}
    registered_work = {g for g in work_groups if g in registered}
    person_mapped = sum(bool(r.get("ku_id")) for r in person)
    work_mapped = sum(bool(r.get("ku_id")) for r in work)
    person_line = re.compile(r"person\s*类型[\d,]+组/[\d,]+条候选，已登记[\d,]+组/[\d,]+条、待登记[\d,]+组/[\d,]+条")
    text, count = person_line.subn(
        f"person 类型{len(person_groups):,}组/{len(person):,}条候选，已登记{len(registered_person):,}组/{person_mapped:,}条、待登记{len(person_groups)-len(registered_person):,}组/{len(person)-person_mapped:,}条",
        text,
        count=1,
    )
    assert count == 1, "result current person type summary did not match"
    work_line = re.compile(r"work\s*[\d,]+组/[\d,]+条")
    text, count = work_line.subn(
        f"work {len(work_groups)-len(registered_work):,}组/{len(work)-work_mapped:,}条",
        text,
        count=1,
    )
    assert count == 1, "result current work type summary did not match"
    text += (
        "\n\n### S3 类型纠偏：Antonio Bellucci 的 Canons 天花作品索引子目（2026-10-16）\n\n"
        "`cand-0282` 保留为 Bellucci 人物候选；索引子目 `cand-0283`“Descent from the Cross”与 `cand-0284`“Nativity”分别裁为 work，并拆成两个作品组。第10章 p.281 将其列为 Canons 天花三幅大型画中的两个主题；第三幅 Ascension 没有对应索引子目。三幅画的集合候选 `cand-8945` 仍保持原决定，个别作品不与集合合并。理由与原 S3 分组历史均保存在对齐行及过程记录。\n"
    )
    return text


def main():
    parser = argparse.ArgumentParser(description="Correct Bellucci's indexed Canons paintings from person candidates to two separate work groups.")
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
    assert candidates["cand-0282"]["suggested_type"] == "person"
    assert candidates["cand-0283"]["suggested_type"] == candidates["cand-0284"]["suggested_type"] == "person"
    assert candidates["cand-0283"]["sub_entry"] == "Descent from the Cross"
    assert candidates["cand-0284"]["sub_entry"] == "Nativity"
    assert by_id["cand-8945"]["decision"] == "undecided"
    manifest = read_csv(TABLES / "ku-manifest.csv")[1]
    assert not any("bellucci-canons" in row["ku_id"] for row in manifest)

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    statement = next(row for row in statements if row.get("statement_id") == STATEMENT_ID)
    mentioned = statement.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    assert all(cid in mentioned for cid in MEMBERS)
    assert all(subject in statement["qualifiers"]["claim"] for subject in ["Nativity", "Descent from the Cross", "Ascension"])
    source = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "Bellucci painted three large and twenty smaller canvases" in source

    before, groups_before, registered_before, _ = summarize(alignments, candidates)
    assert before == Counter({"same": 1717, "new": 5006, "undecided": 5576, "excluded": 98, "conflict": 7}), dict(before)
    assert len(groups_before) == 4836 and len(registered_before) == 168
    old_notes = {cid: by_id[cid]["resolution_note"] for cid in MEMBERS}
    by_id["cand-0282"]["process_ref"] = PROCESS_REF
    by_id["cand-0282"]["resolution_note"] = (
        f"source_ref=candidate=cand-0282;index_entry=B.csv#129;index_pages=227,278,280,281,283,284,294,405,406; group={PERSON_GROUP}; "
        "S3 Bellucci type correction 2026-10-16: the person group now contains only cand-0282; the two named work sub-entries cand-0283 and cand-0284 are split to distinct work groups. "
        f"Prior S3 resolution retained verbatim as history: {old_notes['cand-0282']}"
    )
    for cid, group in WORK_GROUPS.items():
        entry = candidates[cid]
        by_id[cid]["process_ref"] = PROCESS_REF
        by_id[cid]["resolution_note"] = (
            f"source_ref=candidate={cid};index_entry={entry['index_entry_id']};index_pages=281;"
            f"s2_statement={STATEMENT_ID}@chp-10:10_CHP-10_intro:l125-139#L132-133; group={group}; "
            "S3 type correction 2026-10-16: person -> work. The index lists this named subject as a separate Bellucci sub-entry; S2 names it among three large canvases for the Canons chapel ceiling and maps the index sub-entry to that subject. "
            "Treat the Nativity and Descent from the Cross as distinct works; do not merge either with the three-work collective candidate cand-8945. No existing same-work KU or external work source was found/consulted. "
            f"Prior S3 resolution retained verbatim as history: {old_notes[cid]}"
        )
        entry["suggested_type"] = "work"

    after, groups_after, registered_after, types_after = summarize(alignments, candidates)
    assert after == before and len(groups_after) == 4838 and len(registered_after) == 168
    assert group_id(by_id["cand-0282"]["resolution_note"]) == PERSON_GROUP
    assert all(group_id(by_id[cid]["resolution_note"]) == WORK_GROUPS[cid] for cid in WORK_CANDIDATES)
    assert len(types_after["person"]) == 1175 and len(types_after["work"]) == 496
    process_text = update_process(PROCESS.read_text(encoding="utf-8-sig"), after, groups_after, registered_after, types_after)
    result_text = update_result(RESULT.read_text(encoding="utf-8-sig"), after, groups_after, registered_after, types_after)

    print("S3 Bellucci work-subentry type correction dry-run passed")
    print("decision totals unchanged:", dict(after))
    print("new groups: 4,836 -> 4,838; new candidates remain 5,006")
    print("pending S4: 4,670 groups / 4,790 candidates")
    print("person pending: 1,027 groups / 1,077 candidates; work pending: 481 groups / 494 candidates")
    print("cand-0282 remains person; cand-0283 and cand-0284 become separate work groups")
    if args.dry_run:
        print("dry-run only; no files changed")
        return 0
    write_csv(ALIGNMENT, alignment_fields, alignments)
    write_csv(CANDIDATES, candidate_fields, candidate_rows)
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: S3 type/group corrections, preserved prior rationales, process record, and current result counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
