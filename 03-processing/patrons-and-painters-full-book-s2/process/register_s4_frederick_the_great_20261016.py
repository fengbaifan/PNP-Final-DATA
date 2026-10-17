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
GROUP = "new-person:frederick-great-9b41b5d4e4"
MEMBERS = ("cand-1079", "cand-1080")
KU_ID = "units/persons/frederick-the-great"
CARD_PATH = "04-knowledge/units/persons/frederick-the-great.md"

RECORD = {
    "name_zh": "腓特烈大帝",
    "name_en": "Frederick the Great",
    "description_zh": (
        "第10章以 Crown Prince Frederick of Prussia (later the Great) 称其早年身份，并称他曾向 Schulenburg 寻求一位年轻 castrato；第14章称 Frederick the Great 是 Algarotti 的宫廷赞助人之一，"
        "记录他于1740年12月授 Algarotti 伯爵头衔，也记述 Algarotti 为其和宫廷顾问讨论柏林发展艺术中心的计划。第10章 p.295 又将德累斯顿十字教堂遭轰炸一事归于 Frederick the Great；此处保留原书的归因，不作外部核验。"
    ),
    "description_en": (
        "Chapter 10 calls him Crown Prince Frederick of Prussia (later the Great) when recounting his request to Schulenburg for a young castrato. Chapter 14 describes Frederick the Great as one of Algarotti's court patrons, reports that he made Algarotti a Count in December 1740, and says Algarotti advised him and his courtiers about plans to make Berlin a major centre for the arts. "
        "Chapter 10 (p. 295) also attributes the bombardment of Dresden's Church of the Cross to Frederick the Great; this card preserves the book's attribution without external verification."
    ),
    "context_zh": (
        "索引 F.csv#96 列出 p.295、211、349、360；F.csv#97 以“and F. Algarotti”子目列出 p.349、356、357、360。第10章 p.311 使用“Crown Prince Frederick of Prussia (later the Great)”的称谓，第14章多个段落则使用 Frederick the Great，支持跨章归入同一人物组。"
    ),
    "context_en": (
        "Index entry F.csv#96 lists pp. 295, 211, 349, and 360; F.csv#97 adds the sub-entry 'and F. Algarotti' on pp. 349, 356, 357, and 360. Chapter 10 (p. 311) uses 'Crown Prince Frederick of Prussia (later the Great)', while several Chapter 14 passages use Frederick the Great, supporting one cross-chapter person group."
    ),
    "boundary_zh": (
        "本卡以索引称谓与正文“Crown Prince Frederick of Prussia (later the Great)”的明确衔接登记身份，不另补出生日期、完整生平或未经本书支持的政治实体属性。轰炸归因与 Algarotti 关系均限于 Haskell 的叙述；第14章注释对两幅画究竟为国王还是 Algarotti 所订留有相反线索，本卡不把它们写成已决赞助事实。所有关系候选留待 S6；本批未建立正式关系、未作外部身份核验或 S5 补足。"
    ),
    "boundary_en": (
        "The identity is based on the index name and the book's explicit linkage 'Crown Prince Frederick of Prussia (later the Great)'; no birth date, complete biography, or unsupported political-entity attributes are added. The bombardment attribution and Algarotti associations remain Haskell's account. A Chapter 14 note gives conflicting indications about whether two paintings were for the King or Algarotti; this card does not treat that patronage as resolved. All relation candidates remain for S6; this batch creates no formal relation, external identity check, or S5 enrichment."
    ),
    "type_notes_zh": "人物；跨章身份依据为索引主目、and F. Algarotti 子目及正文 Crown Prince Frederick of Prussia (later the Great) 的明确称谓衔接。",
    "type_notes_en": "Person; the cross-chapter identity uses the index main entry, the 'and F. Algarotti' sub-entry, and the text's explicit wording 'Crown Prince Frederick of Prussia (later the Great)'.",
    "sources": [
        card_writer.source(
            "10", "295", "10_CHP-10_intro.md", "L315",
            "paint the ruins of the Church of the Cross which had been wrecked in a bombardment of Frederick the Great",
            "Haskell's sentence attributes the bombardment that destroyed the church to Frederick the Great; this card records the source attribution only.",
        ),
        card_writer.source(
            "10", "311", "10_CHP-10_sec_ii.md", "L12-L13",
            "Crown Prince Frederick of Prussia (later the Great)",
            "The chapter explicitly connects the crown-prince designation to the later epithet 'the Great'.",
        ),
        card_writer.source(
            "14", "349", "14_CHP-14_intro.md", "L25-L26",
            "Frederick the Great, who made him a Count in December 1740.",
            "Haskell reports that Frederick the Great made Algarotti a Count in December 1740; no investiture document is cited here.",
        ),
        card_writer.source(
            "14", "356", "14_CHP-14_intro.md", "L100-L103",
            "he was acting as adviser to Frederick the Great and his courtiers who had ambitious plans for turning Berlin into a great centre of the arts.",
            "The source describes Algarotti as an adviser to Frederick and his courtiers, attributing plans for Berlin to them without claiming that the plan was completed.",
        ),
        card_writer.source(
            "14", "357", "14_CHP-14_intro.md", "L127-L129",
            "suggest that the pictures were painted for him and not the King.",
            "Haskell reports a later evidentiary qualification that suggests two paintings were for Algarotti rather than Frederick; the conflicting patronage reports are left unresolved.",
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
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
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
    assert count == 1, "process current S4 status paragraph did not match"
    return text, mapped, pending_groups, pending_members


def update_result(text, new_count, groups, registered, candidates):
    mapped = sum(bool(r.get("ku_id")) for rows in registered.values() for r in rows)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - mapped
    text = replace_once(
        text,
        "S4 已登记171组、映射219条成员候选；尚待登记4,667组、4,787条映射。",
        f"S4 已登记{len(registered)}组、映射{mapped}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "result S4 counts",
    )
    new_rows = [row for rows in groups.values() for row in rows]
    person_rows = [r for r in new_rows if candidates[r["candidate_id"]]["suggested_type"] == "person"]
    work_rows = [r for r in new_rows if candidates[r["candidate_id"]]["suggested_type"] == "work"]
    person_groups = {get_group(r["resolution_note"]) for r in person_rows}
    work_groups = {get_group(r["resolution_note"]) for r in work_rows}
    reg_person_groups = {g for g in person_groups if g in registered}
    reg_work_groups = {g for g in work_groups if g in registered}
    person_mapped = sum(bool(r.get("ku_id")) for r in person_rows)
    work_mapped = sum(bool(r.get("ku_id")) for r in work_rows)
    person_pattern = re.compile(r"person\s*类型[\d,]+组/[\d,]+条候选，已登记[\d,]+组/[\d,]+条、待登记[\d,]+组/[\d,]+条")
    text, count = person_pattern.subn(
        f"person 类型{len(person_groups):,}组/{len(person_rows):,}条候选，已登记{len(reg_person_groups):,}组/{person_mapped:,}条、待登记{len(person_groups)-len(reg_person_groups):,}组/{len(person_rows)-person_mapped:,}条",
        text,
        count=1,
    )
    assert count == 1, "result current person type summary did not match"
    text, count = re.compile(r"work\s*[\d,]+组/[\d,]+条").subn(
        f"work {len(work_groups)-len(reg_work_groups):,}组/{len(work_rows)-work_mapped:,}条", text, count=1
    )
    assert count == 1, "result current work type summary did not match"
    text = replace_once(text, "1,190 KU；含本轮新增60个 person 组", "1,191 KU；含本轮新增61个 person 组", "manifest count")
    text = replace_once(text, "Antonio Bellucci、2个 Valmarana 组", "Antonio Bellucci、Frederick the Great、2个 Valmarana 组", "registered person list")
    text += (
        "\n\n### person：Frederick the Great 跨章身份组 S4 登记（2026-10-16）\n\n"
        f"`cand-1079`（F.csv#96）与 `cand-1080`（F.csv#97，“and F. Algarotti”）共映射至 [Frederick the Great 人物卡](../units/persons/frederick-the-great.md)。第10章 p.311 明称 Crown Prince Frederick of Prussia (later the Great)；第14章 pp.349、356–360 多次使用 Frederick the Great。人物卡保留 p.295 轰炸归因和 p.357 两幅画赞助对象的原书限定。12条直接 S2 陈述中11条为关系候选；正式关系留待 S6，本批无外部身份核验或 S5 补足。S4 当前累计登记172组/221条映射，待登记4,666组/4,785条。\n"
    )
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the cross-chapter Frederick the Great person group as one source-backed KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidates = {r["candidate_id"]: r for r in candidate_rows}
    by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    assert len(manifest) == 1190, f"unexpected manifest size: {len(manifest)}"
    assert all(cid in by_id and by_id[cid]["decision"] == "new" and not by_id[cid].get("ku_id") for cid in MEMBERS)
    assert all(get_group(by_id[cid]["resolution_note"]) == GROUP for cid in MEMBERS)
    assert all(candidates[cid]["suggested_type"] == "person" for cid in MEMBERS)
    assert candidates[MEMBERS[0]]["index_entry_id"] == "F.csv#96" and candidates[MEMBERS[1]]["index_entry_id"] == "F.csv#97"
    assert candidates[MEMBERS[1]]["sub_entry"] == "and F. Algarotti"
    assert not any(row.get("ku_id") == KU_ID or row.get("card_path") == CARD_PATH for row in manifest)
    assert not (ROOT / CARD_PATH).exists()
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_PATH not in accepted

    statements = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    direct = [row for row in statements if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    counterparts = set()
    for row in relations:
        subject, obj = row.get("subject_candidate_id"), row.get("object_candidate_id")
        counterparts.add(obj if subject in MEMBERS else subject)
    counterparts.difference_update(MEMBERS)
    assert (len(direct), len(relations)) == (12, 11)
    counterpart_status = Counter(by_id[cid]["decision"] for cid in counterparts if cid in by_id)
    assert sum(counterpart_status.values()) == len(counterparts)
    for item in RECORD["sources"]:
        assert item["quote"] in (ROOT / "02-sources" / "02-Markdown" / item["file"]).read_text(encoding="utf-8-sig"), item["quote"]

    new_count, groups_before, registered_before = current_counts(alignments)
    assert (new_count, len(groups_before), len(registered_before)) == (5006, 4838, 171)
    assert len(groups_before[GROUP]) == len(MEMBERS) and {r["candidate_id"] for r in groups_before[GROUP]} == set(MEMBERS)

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
    assert len(planned_manifest) == 1191
    new_after, groups_after, registered_after = current_counts(planned_alignment)
    mapped_after = sum(bool(r.get("ku_id")) for rows in groups_after.values() for r in rows)
    assert (new_after, len(groups_after), len(registered_after), mapped_after) == (5006, 4838, 172, 221)

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
        "\n\n### person：Frederick the Great 跨章身份组 S4 登记（2026-10-16）\n\n"
        f"- `cand-1079` 与 `cand-1080` 共登记至 `{KU_ID}`（{CARD_PATH}）；索引 F.csv#96–97，直接证据跨第10章 p.295、311 与第14章 pp.349、356–360。\n"
        f"- 12条直接 S2 陈述中11条为关系候选；{len(counterparts)}个不同对端决定为 {dict(counterpart_status)}。注5转述 Fantuzzi 对两幅画的赞助说法，并同时引用 letters/inventory 支持 Algarotti；本卡不把相反报告强行裁成确定赞助关系。\n"
        "- 人物卡保留“later the Great”、轰炸归因及柏林艺术中心计划等来源限定；本批不新增正式关系，不作外部身份核验或 S5 补足。\n"
        f"- dry-run 核对唯一2成员组、5处引文、12条直接陈述、11条关系候选及候选映射；manifest 从1,190增至1,191，S4 累计登记172组/221条映射，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), new_after, groups_after, registered_after, candidates)
    card_text = card_writer.make_card(RECORD, "person").replace("'2026-10-15'", "'2026-10-16'")
    assert RECORD["name_en"] in card_text and "no formal relation" in RECORD["boundary_en"]

    print("S4 Frederick the Great registration dry-run passed")
    print("group members:", ",".join(MEMBERS), "->", KU_ID)
    print(f"direct S2 statements={len(direct)}; relation candidates={len(relations)}; unique counterpart IDs={len(counterparts)}")
    print("counterpart decisions:", dict(counterpart_status))
    print("manifest=1,190 -> 1,191; registered=171 groups/219 candidates -> 172 groups/221 candidates")
    print("pending=4,666 groups/4,785 candidates; person pending=1,025/1,074")
    if args.dry_run:
        print("dry-run passed: identity group, evidence quotes, conflict qualification, and planned mappings checked; no files changed")
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: person card, manifest, accepted.yml, alignment mappings, process record, and current result counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
