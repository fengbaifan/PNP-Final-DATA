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

KIND = "person"
GROUP = "new-person:agucchi-battista-giovanni-9239cc0f09"
MEMBERS = ("cand-0018",)
KU_ID = "units/persons/giovanni-battista-agucchi"
CARD_PATH = "04-knowledge/units/persons/giovanni-battista-agucchi.md"
PROCESS_REF = "03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-giovanni-battista-agucchi"

RECORD = {
    "name_zh": "乔瓦尼·巴蒂斯塔·阿古基",
    "name_en": "Giovanni Battista Agucchi",
    "description_zh": (
        "书中索引以 Giovanni Battista Agucchi 登录此人；第2章称其为 Monsignor Agucchi，记其任 Secretary of State，"
        "并称其亦为 Bolognese。哈斯克尔叙述他在1607至1615年退出公职期间草拟艺术理论；第6章又将他列为 Ideal 概念的先行阐述者之一。"
        "第20章后记以 Giambattista Agucchi 再称此人。以上限于原书陈述；中文名为工作音译。"
    ),
    "description_en": (
        "The index identifies this person as Giovanni Battista Agucchi. Chapter 2 calls him Monsignor Agucchi, says he held the office of Secretary of State, "
        "and describes him as also a Bolognese. Haskell says he sketched out a theory of art during his retirement from public life between 1607 and 1615; "
        "Chapter 6 names him among the pioneers who had elaborated the concept of the Ideal. The Chapter 20 postscript also calls him Giambattista Agucchi. "
        "These details are limited to the book's account; the Chinese display name is a working transliteration."
    ),
    "context_zh": (
        "索引主项 A.csv#17 列印刷页28、159、397–398。第2章以 Monsignor Agucchi 指称，后记以 Giambattista Agucchi 给出姓名形式；"
        "人物称谓、艺术理论语境和后记的全名锚点支持将这些跨章提及归入同一新身份组。"
    ),
    "context_en": (
        "The main index entry A.csv#17 lists printed pp. 28, 159, and 397–398. Chapter 2 uses Monsignor Agucchi, while the postscript gives the name "
        "Giambattista Agucchi; the shared personal reference, art-theory context, and full-name anchor support one cross-chapter new identity group."
    ),
    "boundary_zh": (
        "规范姓名依索引全名；后记的 Giambattista Agucchi 作为书内拼写变体保留，不据此补写出生、死亡或完整履历。后记称 Agucchi 确曾编制 Cardinal Aldobrandini 收藏的目录，"
        "但将相关委托或购买说法明确写为无确证的研究建议；本卡不把该建议写成确定事实。13条直接 S2 陈述中11条为关系候选，涉及人物、术语及未决对象；"
        "这些候选留待 S6，不在本批建立正式关系。没有进行外部身份核验或 S5 补足。"
    ),
    "boundary_en": (
        "The index supplies the canonical full name; the postscript's form Giambattista Agucchi is retained as a source variant, without adding a birth date, "
        "death date, or complete biography. The postscript says Agucchi certainly drew up an inventory of Cardinal Aldobrandini's collection, but explicitly "
        "qualifies the proposed commission or purchase as lacking conclusive evidence; this card does not present that proposal as established fact. Of 13 direct "
        "S2 statements, 11 are relation candidates involving people, terms, and unresolved objects. They remain for S6; this batch creates no formal relation and "
        "records no external identity check or S5 enrichment."
    ),
    "type_notes_zh": (
        "姓名：索引规范形式为 Agucchi, Giovanni Battista；正文另称 Monsignor Agucchi，后记写作 Giambattista Agucchi。中文显示名为工作音译。"
    ),
    "type_notes_en": (
        "Name: the index form is Agucchi, Giovanni Battista; the prose also uses Monsignor Agucchi, and the postscript writes Giambattista Agucchi. "
        "The Chinese display name is a working transliteration."
    ),
    "sources": [
        card_writer.source(
            "2", "28", "02_CHP-2_sec_i.md", "87",
            "Holding the influential post of Secretary of State was Monsignor Agucchi, also a Bolognese.",
            "第2章称 Monsignor Agucchi 任 Secretary of State，并称其亦为 Bolognese；保留原书称谓，不改写为出生地或现代国籍。",
        ),
        card_writer.source(
            "2", "28", "02_CHP-2_sec_i.md", "87",
            "he had sketched out a theory of art during a period of retirement from public life between 1607 and 1615.",
            "第2章称他在1607至1615年退出公职期间草拟艺术理论。",
        ),
        card_writer.source(
            "6", "159", "06_CHP-6_sec_iv.md", "31",
            "His criterion of judgement was based on the concept of the Ideal as it had already been elaborated by pioneers such as Monsignor Agucchi.",
            "第6章将 Monsignor Agucchi 列为此前阐述 Ideal 概念的先行者之一。",
        ),
        card_writer.source(
            "20", "397", "20_CHP-20Postscript.md", "23–24",
            "Another patron whose early career has been much illuminated in recent years is\nGiambattista Agucchi—so much so that we now probably know (or feel we know)",
            "后记以 Giambattista Agucchi 为名，并以“probably know (or feel we know)”限定对其早年经历的认识。",
        ),
        card_writer.source(
            "20", "398", "20_CHP-20Postscript.md", "28",
            "and has also suggested—again plausibly but without conclusive evidence—that it was Agucchi who commissioned or bought the forty or so Bolognese paintings in Cardinal Aldobrandini’s collection, of which he certainly drew up the inventory.",
            "后记把相关委托或购买归为 D’Onofrio 的可能性建议并明言无确证，同时称 Agucchi 确曾编制 Cardinal Aldobrandini 收藏目录。",
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


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def current_counts(alignments):
    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {group: rows for group, rows in groups.items() if any(row.get("ku_id") for row in rows)}
    return len(new_rows), groups, registered


def update_process(text, new_count, groups, registered):
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - sum(sum(bool(row.get("ku_id")) for row in rows) for rows in registered.values())
    text = replace_once(
        text,
        "本轮按当前 S3 裁决需登记 5,006 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 4,835 个身份组；截至本次复核，已登记 165 组、212 条成员映射，尚待登记 4,670 组、4,794 条。",
        f"本轮按当前 S3 裁决需登记 {new_count:,} 条 `new` 候选，按 `resolution_note` 中的 `group=` 汇总为 {len(groups):,} 个身份组；截至本次复核，已登记 {len(registered):,} 组、{sum(sum(bool(row.get('ku_id')) for row in rows) for rows in registered.values()):,} 条成员映射，尚待登记 {pending_groups:,} 组、{pending_members:,} 条。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "截至 Bamboccianti 术语组登记后，4,836 个当前 `new` 身份组中完成165组，余4,671组；5,008条成员候选中映射212条，余4,796条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,178条候选，已登记57组、95条候选，待登记1,029组、1,083条候选。procedure 已登记23组、24条候选，term 已登记1组/1条候选，work、place 各登记1组/1条和2组/2条候选。",
        "截至 Bamboccianti 术语组登记后，4,836 个当前 `new` 身份组中完成165组，余4,671组；5,008条成员候选中映射212条，余4,796条。family 已登记80组/86条，另8组/8条待登记；person 类型1,086组、1,178条候选，已登记57组、95条候选，待登记1,029组、1,083条。procedure 已登记23组/24条；term 已登记2组/4条；work、place 各登记1组/1条和2组/2条候选。",
        "process S4 historical checkpoint detail",
    )
    batch = (
        "\n\n### person：Giovanni Battista Agucchi 单候选跨章身份组登记（2026-10-16）\n\n"
        "- `cand-0018`（A.csv#17）是单成员 S3 组 `new-person:agucchi-battista-giovanni-9239cc0f09`，登记至 `units/persons/giovanni-battista-agucchi`。索引列 pp.28、159、397–398；第2章称 Monsignor Agucchi，后记以 Giambattista Agucchi 作姓名锚点。卡片采用书内规范全名，保留后记对早年经历的限定；对委托／购买的无确证建议不写成确定事实。\n"
        "- 13条直接 S2 陈述中11条为关系候选，涉及10个对端候选：Annibale Carracci、Domenichino 两端已映射；6个 term 新身份仍待 S4；2个后记对象候选仍为 `undecided`。所有关系候选继续待 S6；本批不增加正式边，也未作外部身份核验或 S5 补足。\n"
        f"- 批次脚本 dry-run 核对单成员组、5处精确来源引文、13条直接陈述及关系对端去向后通过。manifest 从1,184增至1,185；累计登记{len(registered)}组、{sum(sum(bool(row.get('ku_id')) for row in rows) for rows in registered.values())}条候选映射，余{pending_groups}组、{pending_members}条。person 类型已登记58组/96条，余1,028组/1,082条。脚本：`register_s4_person_agucchi_batch_20261016.py`。\n"
    )
    return text + batch


def update_result(text, new_count, groups, registered):
    reg_members = sum(sum(bool(row.get("ku_id")) for row in rows) for rows in registered.values())
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - reg_members
    text = replace_once(
        text,
        "S4 已登记165组、映射212条成员候选；尚待登记4,670组、4,794条映射。",
        f"S4 已登记{len(registered)}组、映射{reg_members}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "result current S4 totals",
    )
    text = replace_once(
        text,
        "当前已登记56个 person 组（",
        "当前已登记58个 person 组（",
        "result registered person group count",
    )
    text = replace_once(
        text,
        "Simon Vouet、Valmarana 跨章2组",
        "Simon Vouet、Giovanni Battista Agucchi、Valmarana 跨章2组",
        "result registered person names",
    )
    text = replace_once(
        text,
        "其余候选中无 S2 正文锚点的 Albrizzi 索引子目仍为 `undecided`。",
        "其余候选中无 S2 正文锚点的 Albrizzi 索引子目仍为 `undecided`。family 类型共88组/94条候选，已登记80组/86条、待登记8组/8条；person 类型1,086组/1,178条候选，已登记58组/96条、待登记1,028组/1,082条。",
        "result S4 type registration counts",
    )
    text = replace_once(
        text,
        "person 1,029组/1,083条",
        "person 1,028组/1,082条",
        "result S4 person pending breakdown",
    )
    text = replace_once(
        text,
        "尚待登记4,670组、4,794条。按类型待登记",
        "尚待登记4,669组、4,793条。按类型待登记",
        "result current S4 pending breakdown",
    )
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,184 KU；",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,185 KU；",
        "result manifest size",
    )
    text = replace_once(
        text,
        "含本轮新增57个 person 组（",
        "含本轮新增58个 person 组（",
        "result manifest person count",
    )
    text = replace_once(
        text,
        "Simon Vouet、Cardinal Pier Donato Cesi、2个 Valmarana 组",
        "Simon Vouet、Cardinal Pier Donato Cesi、Giovanni Battista Agucchi、2个 Valmarana 组",
        "result manifest person list",
    )
    text = replace_once(
        text,
        "五十二个补充 person 组",
        "五十三个补充 person 组",
        "result added person group count",
    )
    batch = (
        "\n\n### person：Giovanni Battista Agucchi 跨章身份组 S4 登记（2026-10-16）\n\n"
        "`cand-0018`（A.csv#17）已登记为 [Giovanni Battista Agucchi 人物卡](../../04-knowledge/units/persons/giovanni-battista-agucchi.md)。第2章 pp.28 的职务与艺术理论叙述、第6章 p.159 的 Ideal 概念语境，以及第20章后记 pp.397–398 的 Giambattista Agucchi 姓名形式共同支持跨章组；后记对收藏委托／购买的说法保留“无确证”限定。13条直接 S2 陈述中11条为关系候选，10个对端中2个已映射、6个新 term 候选待 S4、2个对象候选仍待证；关系均待 S6，本批未新增正式关系、外部身份核验或 S5 补足。manifest 为1,185 KU；S4累计登记166组/213条映射，待登记4,669组/4,793条。\n"
        f"批次证据与写回记录见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md)和[登记脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_agucchi_batch_20261016.py)。"
    )
    return text + batch


def main():
    parser = argparse.ArgumentParser(description="Register the Giovanni Battista Agucchi person group as one source-backed KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }

    assert len(manifest) == 1184, f"unexpected manifest size: {len(manifest)}"
    assert len(MEMBERS) == 1
    candidate = candidates[MEMBERS[0]]
    alignment = alignment_by_id[MEMBERS[0]]
    assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
    assert candidate["index_entry_id"] == "A.csv#17"
    assert candidate["canonical_name"] == "Agucchi, Giovanni Battista"
    assert candidate["index_page_range"] == "28, 159, 397-398"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    assert CARD_PATH not in ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert not (ROOT / CARD_PATH).exists()
    assert not any(
        row["type"] == KIND and row["name_en"].casefold() == "giovanni battista agucchi"
        for row in manifest
    ), "matching person KU already exists"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    direct = [
        row for row in statements
        if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS
    ]
    relation_rows = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate")]
    counterpart_ids = {
        row.get("object_candidate_id") if row.get("subject_candidate_id") in MEMBERS else row.get("subject_candidate_id")
        for row in relation_rows
    }
    counterpart_ids.discard(None)
    assert (len(direct), len(relation_rows), len(counterpart_ids)) == (13, 11, 10)
    counterpart_status = Counter(alignment_by_id[cid]["decision"] for cid in counterpart_ids)
    assert counterpart_status == Counter({"same": 2, "new": 6, "undecided": 2}), dict(counterpart_status)

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_count, groups, registered = current_counts(alignments)
    assert (new_count, len(groups), len(registered), sum(sum(bool(r.get("ku_id")) for r in rows) for rows in registered.values())) == (5006, 4835, 165, 212)
    assert len(groups[GROUP]) == 1 and groups[GROUP][0]["candidate_id"] == MEMBERS[0]
    person_groups = {
        group: rows for group, rows in groups.items()
        if all(candidates[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    registered_person = {group: rows for group, rows in registered.items() if group in person_groups}
    assert (sum(map(len, person_groups.values())), len(person_groups)) == (1178, 1086)
    assert (sum(sum(bool(row.get("ku_id")) for row in rows) for rows in registered_person.values()), len(registered_person)) == (95, 57)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id[MEMBERS[0]]["ku_id"] = KU_ID
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1185
    new_count_after, groups_after, registered_after = current_counts(planned_alignment)
    assert (new_count_after, len(groups_after), len(registered_after), sum(sum(bool(r.get("ku_id")) for r in rows) for rows in registered_after.values())) == (5006, 4835, 166, 213)

    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"), new_count_after, groups_after, registered_after)
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), new_count_after, groups_after, registered_after)
    card_text = card_writer.make_card(RECORD, KIND)
    assert card_text.count("'2026-10-15'") == 2, "unexpected card date template"
    card_text = card_text.replace("'2026-10-15'", "'2026-10-16'")
    assert "乔瓦尼·巴蒂斯塔·阿古基（Giovanni Battista Agucchi）" in card_text
    assert "11 are relation candidates" in card_text

    print(f"S3 group={GROUP}; members={','.join(MEMBERS)}; type={KIND}")
    print(f"direct S2 statements={len(direct)}; relation candidates={len(relation_rows)}; unique counterpart ids={len(counterpart_ids)}")
    print(f"counterpart decisions={dict(counterpart_status)}")
    print("S4 before=165 groups/212 candidates; after=166 groups/213 candidates; pending=4669 groups/4793 candidates")
    print("manifest=1184 -> 1185; person pending=1028 groups/1082 candidates")
    if args.dry_run:
        print("dry-run passed: one S3 new group, five source quotes, cross-chapter anchors, relation-candidate destinations, and all planned foreign-key writes checked; no files changed")
        print("card preview:")
        print(card_text)
        return 0

    card_path = ROOT / CARD_PATH
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: Agucchi card, manifest, accepted.yml, alignment.csv, process record, current result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
