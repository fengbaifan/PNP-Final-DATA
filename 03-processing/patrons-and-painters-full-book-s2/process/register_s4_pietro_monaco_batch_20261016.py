from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
GROUP = "new-person:monaco-pietro-2f390e5d35"
MEMBERS = ("cand-1682", "cand-1683")
KU_ID = "units/persons/pietro-monaco"
CARD_PATH = "04-knowledge/units/persons/pietro-monaco.md"

RECORD = {
    "name_zh": "皮耶特罗·莫纳科",
    "name_en": "Pietro Monaco",
    "description_zh": (
        "索引主目和“activities as dealer”子目均指向 Pietro Monaco。第13章称他为版画师，并记其于1743年出版一部含55幅版画的集子；"
        "Haskell 称，其中相当比例的当代作品属于 Monaco，并认为他几乎可以肯定是在用版画宣传自己的经纪活动。第8章注释另提到 Monaco 于1763年出版的第42、51和89号版画。"
        "第13章注2还记一封致 John Strange、日期为1763/4年2月4日的信及17幅拟售作品。以上均按原书表述登记；中文名为工作音译。"
    ),
    "description_en": (
        "The index main entry and its 'activities as dealer' sub-entry refer to Pietro Monaco. Chapter 13 calls him an engraver and says he published a collection of fifty-five prints in 1743. "
        "Haskell says a strikingly high proportion of the contemporary works reproduced belonged to Monaco and that he was almost certainly using the plates to advertise his dealer activity. Chapter 8's note also refers to Monaco's prints published in 1763, nos. 42, 51, and 89. "
        "Chapter 13 note 2 reports a letter to John Strange dated 4 February 1763/4 and a list of seventeen pictures offered for sale. These are recorded as the book's account; the Chinese display name is a working transliteration."
    ),
    "context_zh": (
        "索引 M.csv#222 列出 pp.342n、345；M.csv#223 将“activities as dealer”列为同一 Pietro Monaco 主目下的子目。第8章 p.214 注4提及 1763 年版画，第13章 p.342 注5提及其版画署名，p.345 正文叙述其印刷出版和经纪活动；这些跨章锚点共同支持同一人物身份。"
    ),
    "context_en": (
        "Index entry M.csv#222 lists pp. 342n and 345; M.csv#223 places 'activities as dealer' under the same Pietro Monaco main entry. Chapter 8 (p. 214, note 4) mentions prints published in 1763; Chapter 13 (p. 342, note 5) attributes prints to him, and p. 345 discusses his print publication and dealer activity. These cross-chapter anchors support one person identity."
    ),
    "boundary_zh": (
        "Haskell 对版画用于宣传经纪活动的说法为“almost certainly”，本卡保留其推断性质。信件日期印为 1763/4 年 2 月 4 日，不选定年份；第8章所引 1763 年版画与第13章所述 1743 年出版物及后续版次不作未经核实的版本对应。版画、出版物、信件均未独立查阅；不补完整履历、现藏情况或确定的赞助关系。关系候选留待 S6，本批无正式关系、外部身份核验或 S5 补足。"
    ),
    "boundary_en": (
        "Haskell's claim that the plates were used to advertise Monaco's dealer activity is qualified as 'almost certainly'. The letter date is printed as 4 February 1763/4; no year is selected. The Chapter 8 reference to prints published in 1763 is not mapped to the 1743 collection or its later editions without verification. The prints, publication, and letter were not independently consulted. No full biography, present holdings, or certain patronage relation is added. Relation candidates remain for S6; this batch creates no formal relation, external identity check, or S5 enrichment."
    ),
    "type_notes_zh": "人物；索引同一主目包含版画师与经纪活动子目。",
    "type_notes_en": "Person; the index places the engraver and dealer-activity sub-entry under the same person heading.",
    "sources": [
        card_writer.source(
            "8", "214", "08_CHP-8_sec_i_notes_p214_visual-transcription.md", "L4",
            "the engravings of Pietro Monaco published in 1763, Nos. 42, 51 and 89.",
            "A Chapter 8 note refers to three Monaco engravings published in 1763; no edition mapping is inferred from this reference alone.",
        ),
        card_writer.source(
            "13", "342n", "13_CHP-13_intro.md", "L232",
            "were engraved by Pietro Monaco in Raccolta di Opere scelte, Nos. 41 and 84.",
            "The note reports that Monaco engraved two Sebastiano Ricci paintings included as nos. 41 and 84 in the cited publication; neither prints nor publication were consulted.",
        ),
        card_writer.source(
            "13", "345", "13_CHP-13_intro.md", "L165",
            "the engraver Pietro Monaco, who in 1743 published a collection of fifty-five prints",
            "Haskell identifies Monaco as an engraver and reports a 1743 print collection of fifty-five items; this sentence supplies no title for that collection.",
        ),
        card_writer.source(
            "13", "345", "13_CHP-13_intro.md", "L166-L168",
            "Monaco himself: eight drawings by Tiepolo, nine paintings by Pittoni, and one each by Zais, Piazzetta and Nazari.",
            "The passage lists examples of contemporary works reproduced in the collection and attributed as belonging to Monaco; it does not provide a full inventory.",
        ),
        card_writer.source(
            "13", "345", "13_CHP-13_intro.md", "L167-L168",
            "he was almost certainly using the plates to advertise his activities as a dealer",
            "Haskell's interpretation of Monaco's purpose is explicitly qualified as 'almost certainly'.",
        ),
        card_writer.source(
            "13", "345", "13_CHP-13_intro.md", "L250",
            "Letter of 4 February 1763/4 in British Museum, Add. MSS. 23,729, f. 49.",
            "The printed locator gives an ambiguous year form, 1763/4, which this card retains without resolution.",
        ),
    ],
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def current_counts(alignments):
    new_rows = [r for r in alignments if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(r.get("ku_id") for r in rows)}
    return len(new_rows), groups, registered


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def update_status(text, new_count, groups, registered):
    mapped = sum(bool(r.get("ku_id")) for rows in registered.values() for r in rows)
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
    assert count == 1, "process S4 status paragraph did not match"
    return text, mapped, pending_groups, pending_members


def update_result(text, new_count, groups, registered, candidates):
    mapped = sum(bool(r.get("ku_id")) for rows in registered.values() for r in rows)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - mapped
    text = replace_once(
        text,
        "S4 已登记172组、映射221条成员候选；尚待登记4,666组、4,786条映射。",
        f"S4 已登记{len(registered)}组、映射{mapped}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "result current S4 totals",
    )
    new_rows = [r for rows in groups.values() for r in rows]
    person_rows = [r for r in new_rows if candidates[r["candidate_id"]]["suggested_type"] == "person"]
    work_rows = [r for r in new_rows if candidates[r["candidate_id"]]["suggested_type"] == "work"]
    person_groups = {get_group(r["resolution_note"]) for r in person_rows}
    work_groups = {get_group(r["resolution_note"]) for r in work_rows}
    registered_person = {g for g in person_groups if g in registered}
    registered_work = {g for g in work_groups if g in registered}
    person_mapped = sum(bool(r.get("ku_id")) for r in person_rows)
    work_mapped = sum(bool(r.get("ku_id")) for r in work_rows)
    person_line = re.compile(r"person\s*类型[\d,]+组/[\d,]+条候选，已登记[\d,]+组/[\d,]+条、待登记[\d,]+组/[\d,]+条")
    text, count = person_line.subn(
        f"person 类型{len(person_groups):,}组/{len(person_rows):,}条候选，已登记{len(registered_person):,}组/{person_mapped:,}条、待登记{len(person_groups)-len(registered_person):,}组/{len(person_rows)-person_mapped:,}条",
        text,
        count=1,
    )
    assert count == 1, "result current person type counts did not match"
    text, count = re.compile(r"work\s*[\d,]+组/[\d,]+条").subn(
        f"work {len(work_groups)-len(registered_work):,}组/{len(work_rows)-work_mapped:,}条", text, count=1
    )
    assert count == 1, "result current work type counts did not match"
    text = replace_once(text, "1,191 KU；含本轮新增61个 person 组", "1,192 KU；含本轮新增62个 person 组", "manifest total")
    text = replace_once(text, "Frederick the Great、2个 Valmarana 组", "Frederick the Great、Pietro Monaco、2个 Valmarana 组", "registered person list")
    text += (
        "\n\n### person：Pietro Monaco 跨章人物身份组 S4 登记（2026-10-16）\n\n"
        f"`cand-1682`（M.csv#222）与 `cand-1683`（M.csv#223，“activities as dealer”）共映射至 [Pietro Monaco 人物卡](../units/persons/pietro-monaco.md)。卡片连接第8章 p.214 注4与第13章 pp.342n、345；保留“almost certainly”意图推断、1763/4 信件日期歧义及出版物版本对应未决。12条直接 S2 陈述中11条为关系候选，均留待 S6；本批无正式关系、外部身份核验或 S5 补足。S4 当前累计登记173组/223条映射，待登记4,665组/4,784条。\n"
    )
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the Pietro Monaco person group including the corrected dealer-activity index sub-entry.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidates = {r["candidate_id"]: r for r in candidate_rows}
    by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    assert len(manifest) == 1191, f"unexpected manifest size: {len(manifest)}"
    assert all(cid in by_id and by_id[cid]["decision"] == "new" and not by_id[cid].get("ku_id") for cid in MEMBERS)
    assert all(get_group(by_id[cid]["resolution_note"]) == GROUP for cid in MEMBERS)
    assert all(candidates[cid]["suggested_type"] == "person" for cid in MEMBERS)
    assert candidates["cand-1682"]["index_entry_id"] == "M.csv#222" and candidates["cand-1683"]["index_entry_id"] == "M.csv#223"
    assert candidates["cand-1683"]["sub_entry"] == "activities as dealer"
    assert not any(r.get("ku_id") == KU_ID or r.get("card_path") == CARD_PATH for r in manifest)
    assert not (ROOT / CARD_PATH).exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_PATH not in accepted

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    direct = [r for r in statements if r.get("subject_candidate_id") in MEMBERS or r.get("object_candidate_id") in MEMBERS]
    relations = [r for r in direct if r.get("qualifiers", {}).get("relation_candidate")]
    counterparts = set()
    for row in relations:
        subject, obj = row.get("subject_candidate_id"), row.get("object_candidate_id")
        counterparts.add(obj if subject in MEMBERS else subject)
    counterparts.difference_update(MEMBERS)
    assert (len(direct), len(relations)) == (12, 11)
    counterpart_status = Counter(by_id[cid]["decision"] for cid in counterparts if cid in by_id)
    assert sum(counterpart_status.values()) == len(counterparts)
    for item in RECORD["sources"]:
        path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_count, groups_before, registered_before = current_counts(alignments)
    assert (new_count, len(groups_before), len(registered_before)) == (5007, 4838, 172)
    assert {r["candidate_id"] for r in groups_before[GROUP]} == set(MEMBERS)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignment if r.get("candidate_id") and not r.get("external_source")}
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": "person",
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1192
    new_after, groups_after, registered_after = current_counts(planned_alignment)
    mapped_after = sum(bool(r.get("ku_id")) for rows in groups_after.values() for r in rows)
    assert (new_after, len(groups_after), len(registered_after), mapped_after) == (5007, 4838, 173, 223)

    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text, _, pending_groups, pending_members = update_status(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), new_after, groups_after, registered_after
    )
    process_text += (
        "\n\n### person：Pietro Monaco 跨章人物身份组 S4 登记（2026-10-16）\n\n"
        f"- `cand-1682`、`cand-1683` 共登记至 `{KU_ID}`（{CARD_PATH}）；覆盖 M.csv#222–223、第8章 p.214 注4及第13章 pp.342n、345。`cand-1683` 在 S3 从 `undecided` 改为与主目同组，S4 映射到同一人物卡。\n"
        f"- 12条直接 S2 陈述中11条为关系候选；10个不同对端的决定为 {dict(counterpart_status)}。书中版画师、收藏及经纪活动的关系证据继续留待 S6；无正式关系写入。\n"
        "- 卡片保留 “almost certainly” 对宣传意图的限定、4 February 1763/4 的日期歧义及打印版次映射未决；版画、出版物和信件未独立查阅。\n"
        f"- dry-run 核对唯一2成员组、6处来源引文、12条直接陈述、11条关系候选及登记外键；manifest 从1,191增至1,192，S4 累计登记173组/223条候选映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), new_after, groups_after, registered_after, candidates)
    card_text = card_writer.make_card(RECORD, "person").replace("'2026-10-15'", "'2026-10-16'")
    assert RECORD["name_en"] in card_text and "no formal relation" in RECORD["boundary_en"]

    print("S4 Pietro Monaco registration dry-run passed")
    print("group members:", ",".join(MEMBERS), "->", KU_ID)
    print(f"direct S2 statements={len(direct)}; relation candidates={len(relations)}; unique counterpart IDs={len(counterparts)}")
    print("counterpart decisions:", dict(counterpart_status))
    print("manifest=1,191 -> 1,192; registered=172 groups/221 candidates -> 173 groups/223 candidates")
    print("pending=4,665 groups/4,784 candidates; person pending=1,024/1,073")
    if args.dry_run:
        print("dry-run passed: revised S3 group, six source anchors, qualification boundaries, and planned mappings checked; no files changed")
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: Pietro Monaco card, manifest, accepted.yml, alignment mappings, process record, and current result counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
