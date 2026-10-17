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
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"

PERSON_GROUP = "new-person:bellotto-bernardo-3bfd904005"
WORK_GROUP = "sg3-work-bellotto-cross-church-ruins"
PERSON_MEMBERS = ("cand-0279", "cand-0281")
WORK_MEMBER = "cand-0280"
PERSON_KU = "units/persons/bernardo-bellotto"
WORK_KU = "units/works/bellotto-ruins-church-of-the-cross-dresden"
PERSON_CARD = "04-knowledge/units/persons/bernardo-bellotto.md"
WORK_CARD = "04-knowledge/units/works/bellotto-ruins-church-of-the-cross-dresden.md"


PERSON = {
    "name_zh": "贝尔纳多·贝洛托",
    "name_en": "Bernardo Bellotto",
    "description_zh": (
        "书中称 Bellotto 为 Canaletto 之侄：他于1747年抵达德累斯顿，不到一年获任宫廷画家，任至七年战争后该宫廷解体。"
        "1765年他返回德累斯顿，短暂停留期间绘制十字教堂废墟，随后离开。此后他原拟前往圣彼得堡，途中受波兰新王 Stanislas Poniatowski 劝留而转往华沙；"
        "书中称他为该王绘制大量城市景观，持续十二年直至1780年去世。以上仅记录原书叙述，未作外部身份核验；中文名为工作音译。"
    ),
    "description_en": (
        "Haskell calls Bellotto a nephew of Canaletto. He arrived in Dresden in 1747, was appointed court painter within a year, and held the post until that court broke up after the Seven Years War. "
        "He returned to Dresden in 1765, stayed briefly to paint the ruins of the Church of the Cross, and then left. He later planned to travel to St Petersburg but was persuaded to stop in Warsaw by the new King Stanislas Poniatowski; "
        "Haskell says Bellotto produced many views for the king for twelve years until his death in 1780. This card records the book's account only; the Chinese display name is a working transliteration."
    ),
    "context_zh": (
        "索引 B.csv#126（印刷页295）与 B.csv#128（印刷页298）分别提供人物主目和“work in Warsaw”子目。第10章 pp.295、298 将两个姓名锚点置于德累斯顿宫廷服务、1765年回返及转赴华沙的连续叙述中。"
    ),
    "context_en": (
        "Index entries B.csv#126 (printed p. 295) and B.csv#128 (printed p. 298, sub-entry 'work in Warsaw') provide two anchors. Chapter 10 (pp. 295 and 298) places both name anchors in a continuous account of Dresden court service, the 1765 return, and the move to Warsaw."
    ),
    "boundary_zh": (
        "人物身份与经历限于本书叙述；不补写出生、完整履历、具体宫廷任命年份或未经本书确认的生平细节。Canaletto 亲缘及其为王室创作的关系候选保留来源归属，均待 S6 关系审查；本批未建立正式关系，也未进行外部身份核验或 S5 补足。"
    ),
    "boundary_en": (
        "Identity and biography are limited to this book. No birth details, complete biography, exact court appointment year, or unsupported life details are added. The Canaletto kinship and royal-patronage relation candidates retain their source attribution for S6; this batch creates no formal relation and records no external identity check or S5 enrichment."
    ),
    "type_notes_zh": "人物；索引姓名为 Bernardo Bellotto。书中称其为 Canaletto 之侄；亲缘关系仍按来源归属保留，待 S6 审查。",
    "type_notes_en": "Person; the index gives the name Bernardo Bellotto. The book calls him Canaletto's nephew; retain that source-attributed kinship for S6 review.",
    "sources": [
        card_writer.source(
            "10", "295", "10_CHP-10_intro.md", "L315",
            "In 1747 Bernardo Bellotto, the nephew of Canaletto, arrived in Dresden and within a year he was appointed ‘pittore di corte’",
            "Haskell names Bellotto, calls him Canaletto's nephew, and says he arrived in Dresden in 1747 and received the court-painter appointment within a year.",
        ),
        card_writer.source(
            "10", "295", "10_CHP-10_intro.md", "L315",
            "In 1765, after he had already found employment elsewhere, Bellotto returned to Dresden.",
            "Haskell dates Bellotto's return to Dresden to 1765, without naming the intervening employment in this sentence.",
        ),
        card_writer.source(
            "10", "298", "10_CHP-10_intro.md", "L348",
            "Bernardo Bellotto was planning to go to S t Petersburg after the collapse of the Dresden court and the death of Augustus III.",
            "The chapter identifies Bellotto's intended route after the Dresden court's collapse and Augustus III's death; the OCR spacing in 'S t Petersburg' is preserved in the source quotation.",
        ),
        card_writer.source(
            "10", "298", "10_CHP-10_intro.md", "L348",
            "he was persuaded to stop in Warsaw by the new King of Poland Stanislas Poniatowski",
            "Haskell says the new King of Poland, Stanislas Poniatowski, persuaded Bellotto to stop in Warsaw.",
        ),
        card_writer.source(
            "10", "298", "10_CHP-10_intro.md", "L348",
            "for twelve years until his death in 1780, he produced for that art-loving and reforming monarch a large number of views",
            "The source says Bellotto produced many views for the monarch for twelve years, until his death in 1780.",
        ),
    ],
}

WORK = {
    "name_zh": "贝洛托所绘德累斯顿十字教堂废墟（绘画）",
    "name_en": "Bellotto's painting of the ruins of Dresden's Church of the Cross",
    "description_zh": (
        "第10章称 Bellotto 于1765年返回德累斯顿后，仅停留至完成一幅十字教堂废墟绘画，随后离开；书中称教堂在与 Frederick the Great 相关的轰炸中被毁。"
        "索引将这幅绘画另列为 Bellotto 的子目。此卡采用描述性名称，以区别绘画作品与教堂地点。"
    ),
    "description_en": (
        "Chapter 10 reports that after returning to Dresden in 1765, Bellotto stayed only long enough to paint the ruins of the Church of the Cross, which the text associates with a bombardment by Frederick the Great, and then left. "
        "The index lists the painting as a separate Bellotto sub-entry. This card uses a descriptive title to distinguish the work from the church site."
    ),
    "context_zh": (
        "索引 B.csv#127（印刷页295）将“painting of ruins of Church of the Cross, Dresden”列在 Bellotto 名下。S2 断言 `st-chp10-p295-cross-church-painting` 将 Bellotto（`cand-0279`）和绘画（`cand-0280`）分为创作者与作品端点；教堂地点另为 `cand-9111`。"
    ),
    "context_en": (
        "Index entry B.csv#127 (printed p. 295) lists 'painting of ruins of Church of the Cross, Dresden' under Bellotto. S2 statement `st-chp10-p295-cross-church-painting` separates Bellotto (`cand-0279`) and the painting (`cand-0280`) as creator and work endpoints; the church site is a distinct candidate, `cand-9111`."
    ),
    "boundary_zh": (
        "该名称是依据索引子目形成的描述性标题，不是原书给出的原题名。来源未提供媒材、尺寸、现藏地或作品存续状态；未将它并入 `cand-9110` 所指的多幅德累斯顿景观集合。创作者—作品关系候选留待 S6；本批未新增正式关系、外部作品核验或 S5 补足。"
    ),
    "boundary_en": (
        "The name is a descriptive title based on the index sub-entry, not an original title supplied by the book. The source gives no medium, dimensions, current location, or survival status. This work is not merged with the broader Dresden-view set represented by `cand-9110`. The creator-work relation candidate remains for S6; this batch adds no formal relation, external work verification, or S5 enrichment."
    ),
    "type_notes_zh": "作品；单件绘画。题名为便于识别的描述性命名，不表示原题名。",
    "type_notes_en": "Work; an individual painting. The title is descriptive for identification and is not presented as an original title.",
    "sources": [
        card_writer.source(
            "10", "295", "10_CHP-10_intro.md", "L315",
            "the artist stayed just long enough to paint the ruins of the Church of the Cross which had been wrecked in a bombardment of Frederick the Great that had shocked Europe.4 Then he left.",
            "Haskell reports that Bellotto stayed briefly after his 1765 return, painted the church ruins, and then left. The cited Posse study at note 4 was not independently consulted.",
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
    new_rows = [row for row in alignments if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
    return len(new_rows), groups, registered


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def update_status_paragraph(text, new_count, groups, registered):
    reg_members = sum(bool(row.get("ku_id")) for rows in registered.values() for row in rows)
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
    assert count == 1, "process/result current S4 status paragraph did not match"
    return text, reg_members, pending_groups, pending_members


def update_result(text, new_count, groups, registered, candidates):
    reg_members = sum(bool(row.get("ku_id")) for rows in registered.values() for row in rows)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - reg_members
    text = replace_once(
        text,
        "S4 已登记166组、映射213条成员候选；尚待登记4,670组、4,793条映射。",
        f"S4 已登记{len(registered)}组、映射{reg_members}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "result current S4 totals",
    )
    person_rows = [r for rows in groups.values() for r in rows if candidates[r["candidate_id"]]["suggested_type"] == "person"]
    work_rows = [r for rows in groups.values() for r in rows if candidates[r["candidate_id"]]["suggested_type"] == "work"]
    person_group_ids = {get_group(r["resolution_note"]) for r in person_rows}
    work_group_ids = {get_group(r["resolution_note"]) for r in work_rows}
    registered_person = {g for g in person_group_ids if g in registered}
    registered_work = {g for g in work_group_ids if g in registered}
    person_reg_members = sum(bool(r.get("ku_id")) for r in person_rows)
    work_reg_members = sum(bool(r.get("ku_id")) for r in work_rows)
    person_summary = re.compile(r"person\s*类型[\d,]+组/[\d,]+条候选，已登记[\d,]+组/[\d,]+条、待登记[\d,]+组/[\d,]+条")
    text, count = person_summary.subn(
        f"person 类型{len(person_group_ids):,}组/{len(person_rows):,}条候选，已登记{len(registered_person):,}组/{person_reg_members:,}条、待登记{len(person_group_ids)-len(registered_person):,}组/{len(person_rows)-person_reg_members:,}条",
        text,
        count=1,
    )
    assert count == 1, "result current person type summary did not match"
    work_summary = re.compile(r"work\s*[\d,]+组/[\d,]+条")
    work_pending_groups = len(work_group_ids) - len(registered_work)
    work_pending_members = len(work_rows) - work_reg_members
    text, count = work_summary.subn(f"work {work_pending_groups:,}组/{work_pending_members:,}条", text, count=1)
    assert count == 1, "result current work type summary did not match"

    text = replace_once(text, "1,185 KU；含本轮新增58个 person 组", "1,187 KU；含本轮新增59个 person 组", "current manifest row count")
    text = replace_once(text, "Giovanni Battista Agucchi、2个 Valmarana 组", "Giovanni Battista Agucchi、Bernardo Bellotto、2个 Valmarana 组", "registered person list")
    text = replace_once(text, "1个 work、2个 place 组", "2个 work、2个 place 组", "registered work group count")
    text += (
        "\n\n### person 与 work：Bernardo Bellotto 跨章身份组及十字教堂废墟绘画 S4 登记（2026-10-16）\n\n"
        "`cand-0279` 与 `cand-0281` 共映射至 [Bernardo Bellotto 人物卡](../units/persons/bernardo-bellotto.md)；`cand-0280` 映射至独立的 [十字教堂废墟绘画作品卡](../units/works/bellotto-ruins-church-of-the-cross-dresden.md)。人物卡据第10章 pp.295、298 记录德累斯顿与华沙叙述；作品卡采用描述性标题，不声称原题名、媒材或现藏地。人物组11条直接 S2 陈述中10条为关系候选；人物—作品、地点与轰炸事件的正式关系留待 S6，本批未新建关系、未作外部核验或 S5 补足。S4 当前累计登记168组/216条成员候选，待登记4,668组/4,790条。\n"
    )
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the corrected Bellotto person and work identity groups as two source-backed KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    assert len(manifest) == 1185, f"unexpected manifest size: {len(manifest)}"
    assert all(cid in by_id and by_id[cid]["decision"] == "new" and not by_id[cid].get("ku_id") for cid in (*PERSON_MEMBERS, WORK_MEMBER))
    assert all(get_group(by_id[cid]["resolution_note"]) == PERSON_GROUP for cid in PERSON_MEMBERS)
    assert get_group(by_id[WORK_MEMBER]["resolution_note"]) == WORK_GROUP
    assert candidates["cand-0279"]["suggested_type"] == candidates["cand-0281"]["suggested_type"] == "person"
    assert candidates[WORK_MEMBER]["suggested_type"] == "work"
    assert candidates[WORK_MEMBER]["index_entry_id"] == "B.csv#127"
    assert candidates[WORK_MEMBER]["sub_entry"] == "painting of ruins of Church of the Cross, Dresden"
    assert by_id["cand-9110"]["decision"] == "undecided"
    assert all(not any(row.get(key) == value for row in manifest) for key, value in (("ku_id", PERSON_KU), ("ku_id", WORK_KU), ("card_path", PERSON_CARD), ("card_path", WORK_CARD)))
    assert not (ROOT / PERSON_CARD).exists() and not (ROOT / WORK_CARD).exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert PERSON_CARD not in accepted and WORK_CARD not in accepted

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    person_direct = [r for r in statements if r.get("subject_candidate_id") in PERSON_MEMBERS or r.get("object_candidate_id") in PERSON_MEMBERS]
    person_relations = [r for r in person_direct if r.get("qualifiers", {}).get("relation_candidate")]
    counterpart_ids = set()
    for row in person_relations:
        subject, obj = row.get("subject_candidate_id"), row.get("object_candidate_id")
        counterpart_ids.add(obj if subject in PERSON_MEMBERS else subject)
    counterpart_ids.difference_update(PERSON_MEMBERS)
    assert (len(person_direct), len(person_relations), len(counterpart_ids)) == (11, 10, 9)
    counterpart_status = Counter(by_id[cid]["decision"] for cid in counterpart_ids)
    assert counterpart_status == Counter({"new": 7, "undecided": 2}), dict(counterpart_status)
    work_statement = next(r for r in statements if r.get("statement_id") == "st-chp10-p295-cross-church-painting")
    assert work_statement["subject_candidate_id"] == "cand-0279" and work_statement["object_candidate_id"] == WORK_MEMBER
    assert work_statement.get("qualifiers", {}).get("relation_candidate") is True

    for record in (PERSON, WORK):
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_count, groups_before, registered_before = current_counts(alignments)
    assert (new_count, len(groups_before), len(registered_before)) == (5006, 4836, 166)
    assert len(groups_before[PERSON_GROUP]) == 2 and {r["candidate_id"] for r in groups_before[PERSON_GROUP]} == set(PERSON_MEMBERS)
    assert len(groups_before[WORK_GROUP]) == 1 and groups_before[WORK_GROUP][0]["candidate_id"] == WORK_MEMBER

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignment if r.get("candidate_id") and not r.get("external_source")}
    for cid in PERSON_MEMBERS:
        planned_by_id[cid]["ku_id"] = PERSON_KU
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {PERSON_GROUP} to {PERSON_KU}."
    planned_by_id[WORK_MEMBER]["ku_id"] = WORK_KU
    planned_by_id[WORK_MEMBER]["resolution_note"] += f" S4 registration: mapped {WORK_GROUP} to {WORK_KU}."

    planned_manifest = list(manifest) + [
        {"ku_id": PERSON_KU, "type": "person", "canonical_name": PERSON["name_zh"], "name_en": PERSON["name_en"], "source_task": TASK, "card_path": PERSON_CARD},
        {"ku_id": WORK_KU, "type": "work", "canonical_name": WORK["name_zh"], "name_en": WORK["name_en"], "source_task": TASK, "card_path": WORK_CARD},
    ]
    assert len(planned_manifest) == 1187
    new_after, groups_after, registered_after = current_counts(planned_alignment)
    assert (new_after, len(groups_after), len(registered_after)) == (5006, 4836, 168)
    registered_member_count = sum(bool(row.get("ku_id")) for rows in registered_after.values() for row in rows)
    assert registered_member_count == 216

    accepted_lines = accepted.splitlines()
    for card_path in sorted((PERSON_CARD, WORK_CARD)):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_path}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    process_text, _, pending_groups, pending_members = update_status_paragraph(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), new_after, groups_after, registered_after
    )
    process_text += (
        "\n\n### person / work：Bernardo Bellotto 与十字教堂废墟绘画 S4 登记（2026-10-16）\n\n"
        f"- 人物组 `{PERSON_GROUP}` 的 `cand-0279`、`cand-0281` 共映射至 `{PERSON_KU}`（{PERSON_CARD}）；依据第10章 pp.295、298。人物组11条直接 S2 陈述中10条为关系候选，9个不同对端中7个已裁为 new、2个仍 undecided。\n"
        f"- 作品组 `{WORK_GROUP}` 的 `cand-0280` 映射至 `{WORK_KU}`（{WORK_CARD}）；依据索引 B.csv#127 与第10章 p.295 的作品端点陈述。作品名称是描述性标题，不补原题名、媒材、现藏地或存续状态。\n"
        "- `st-chp10-p295-cross-church-painting` 现在两端均有 KU；正式创作关系仍待 S6。本批未新增关系或外部核验，未执行 S5。\n"
        f"- 批次 dry-run 核对2组、3条候选映射、6处原文引文和现有登记外键；manifest 从1,185增至1,187，S4 累计登记168组/216条成员候选，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), new_after, groups_after, registered_after, candidates)
    person_card = card_writer.make_card(PERSON, "person").replace("'2026-10-15'", "'2026-10-16'")
    work_card = card_writer.make_card(WORK, "work").replace("'2026-10-15'", "'2026-10-16'")
    assert PERSON["name_en"] in person_card and WORK["name_en"] in work_card
    assert "no formal relation" in PERSON["boundary_en"] and "descriptive title" in WORK["boundary_en"]

    print("S4 Bellotto person/work registration dry-run passed")
    print("person group members:", ",".join(PERSON_MEMBERS), "->", PERSON_KU)
    print("work group member:", WORK_MEMBER, "->", WORK_KU)
    print(f"direct S2 statements for person={len(person_direct)}; relation candidates={len(person_relations)}; unique counterpart IDs={len(counterpart_ids)}")
    print("counterpart decisions:", dict(counterpart_status))
    print("manifest=1,185 -> 1,187; registered=166 groups/213 candidates -> 168 groups/216 candidates")
    print("pending=4,668 groups/4,790 candidates; person pending=1,027/1,079; work pending=479/492")
    if args.dry_run:
        print("dry-run passed: groups, evidence quotes, cross-chapter members, and all planned foreign-key writes checked; no files changed")
        print("card previews:\n" + person_card + "\n" + work_card)
        return 0

    for card_path, card_text in ((PERSON_CARD, person_card), (WORK_CARD, work_card)):
        target = ROOT / card_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: two cards, manifest, accepted.yml, alignment mappings, process record, and current result counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
