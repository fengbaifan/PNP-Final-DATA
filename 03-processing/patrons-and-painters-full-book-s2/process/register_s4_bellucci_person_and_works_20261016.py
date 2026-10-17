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

PERSON_GROUP = "new-person:antonio-bellucci-f1e7b7cdb6"
WORK_GROUPS = {
    "cand-0283": "sg3-work-bellucci-canons-descent-from-cross",
    "cand-0284": "sg3-work-bellucci-canons-nativity",
}
PERSON_MEMBER = "cand-0282"
PERSON_KU = "units/persons/antonio-bellucci"
PERSON_CARD = "04-knowledge/units/persons/antonio-bellucci.md"
WORKS = {
    "cand-0283": {
        "group": WORK_GROUPS["cand-0283"],
        "ku_id": "units/works/antonio-bellucci-descent-from-the-cross-canons",
        "card_path": "04-knowledge/units/works/antonio-bellucci-descent-from-the-cross-canons.md",
        "name_zh": "贝卢奇所绘《耶稣下十字架》（Canons 礼拜堂，描述性题名）",
        "name_en": "Antonio Bellucci's Descent from the Cross at Canons Chapel (descriptive title)",
        "subject": "The Descent from the Cross",
        "subject_zh": "《耶稣下十字架》",
    },
    "cand-0284": {
        "group": WORK_GROUPS["cand-0284"],
        "ku_id": "units/works/antonio-bellucci-nativity-canons",
        "card_path": "04-knowledge/units/works/antonio-bellucci-nativity-canons.md",
        "name_zh": "贝卢奇所绘《耶稣诞生》（Canons 礼拜堂，描述性题名）",
        "name_en": "Antonio Bellucci's Nativity at Canons Chapel (descriptive title)",
        "subject": "The Nativity",
        "subject_zh": "《耶稣诞生》",
    },
}

PERSON = {
    "name_zh": "安东尼奥·贝卢奇",
    "name_en": "Antonio Bellucci",
    "description_zh": (
        "索引以 Antonio Bellucci 为人物主目。第10章称 Hapsburgs 于1709年雇他任 court painter，也叙述他后来在英格兰受雇，并为 James Brydges 的 Canons 礼拜堂作画。"
        "第20章后记转述一篇关于 Bellucci 在 Vienna 的研究文章，称其在当地活动的时间可能是1692至1704年；保留 Haskell 对该研究结论的可能性表述。"
        "以上仅登记原书叙述，未作外部身份核验；中文名为工作音译。"
    ),
    "description_en": (
        "The index identifies the person as Antonio Bellucci. Chapter 10 says the Hapsburgs employed him as their court painter in 1709 and later describes his English employment and work for James Brydges's Canons chapel. "
        "The Chapter 20 postscript summarizes an article on Bellucci in Vienna and says it makes a presence there between 1692 and 1704 appear likely. This preserves Haskell's qualification of the reported research; the account has not been externally checked."
    ),
    "context_zh": (
        "索引 B.csv#129 列出印刷页227、278、280–281、283–284、294及405–406。第10章记述其在德国宫廷与英格兰的工作，第20章后记又以 Bellucci 为名讨论 Vienna 研究；这些跨章主目均指向 Antonio Bellucci。"
    ),
    "context_en": (
        "Index entry B.csv#129 lists printed pp. 227, 278, 280–281, 283–284, 294, and 405–406. Chapter 10 discusses his work at German courts and in England; the Chapter 20 postscript again names Bellucci in its account of research on Vienna. These cross-chapter main-entry anchors identify Antonio Bellucci."
    ),
    "boundary_zh": (
        "Hapsburgs 的具体制度或王朝边界仍未由本段确定；Vienna 1692–1704 是 Haskell 转述研究文章后给出的可能时间，不写成已核实的确定履历。作品现状、现藏地及赞助／委托关系仍须按具体证据审查。相关关系候选留待 S6；本批未建立正式关系、未进行外部身份核验或 S5 补足。"
    ),
    "boundary_en": (
        "This passage does not resolve the precise institutional or dynastic boundary of the Hapsburg actor. The 1692–1704 Vienna presence is reported by Haskell as likely based on an article, not as an independently verified biographical fact. Work status, present locations, and patronage or commission relations require their own evidence review. Relation candidates remain for S6; this batch creates no formal relation, external identity check, or S5 enrichment."
    ),
    "type_notes_zh": "人物；索引姓名为 Antonio Bellucci。跨章身份归并仅基于本书姓名与语境锚点。",
    "type_notes_en": "Person; the index gives the name Antonio Bellucci. The cross-chapter identity grouping uses the book's name and contextual anchors.",
    "sources": [
        card_writer.source(
            "10", "278", "10_CHP-10_intro.md", "L30",
            "in 1709 employed Antonio Bellucci as their court painter.",
            "Haskell says the Hapsburgs employed Antonio Bellucci as their court painter in 1709; the exact institutional or dynastic scope of 'their' is not resolved here.",
        ),
        card_writer.source(
            "10", "281", "10_CHP-10_intro.md", "L128-L133",
            "Bellucci painted three large and twenty smaller canvases which were let into the rococo ceiling, representing The Nativity, The Descent from the Cross and The Ascension,",
            "Haskell names three subjects among the large canvases Bellucci painted for the Canons chapel ceiling. The indexed Nativity and Descent subjects are separate work candidates; the collective group remains distinct.",
        ),
        card_writer.source(
            "20", "406", "20_CHP-20Postscript.md", "L155",
            "An article on Bellucci in Vienna (and especially on his decorations in the Liechtenstein palace there) makes it appear likely that the artist was in the city between 1692 and 1704",
            "The postscript reports a study that makes Bellucci's presence in Vienna between 1692 and 1704 appear likely; this is retained as a qualified research report.",
        ),
    ],
}


def work_record(info):
    return {
        "name_zh": info["name_zh"],
        "name_en": info["name_en"],
        "description_zh": (
            f"第10章称 Bellucci 为 Canons 礼拜堂天花绘制三幅大型画，题材包括{info['subject_zh']}、《耶稣下十字架》和《升天》。"
            f"索引另以 Bellucci 子目列出“{info['subject']}”。此卡以描述性标题标识其中一件作品，不把索引题材伪作原题名。"
        ),
        "description_en": (
            f"Chapter 10 says Bellucci painted three large canvases for the Canons chapel ceiling, with subjects including {info['subject']}, The Descent from the Cross, and The Ascension. "
            f"The index lists '{info['subject']}' as a separate Bellucci sub-entry. This card uses a descriptive title for one of the works and does not present the indexed subject as a verified original title."
        ),
        "context_zh": (
            f"索引 B.csv#{'130' if info['subject']=='The Descent from the Cross' else '131'}（印刷页281）将“{info['subject']}”列在 Bellucci 名下。"
            "第10章 p.281 将该题材列为 Canons 礼拜堂天花三幅大型画之一；另有二十幅较小画布的集合叙述。相关集合候选 `cand-8945` 不与本件合并。"
        ),
        "context_en": (
            f"Index entry B.csv#{'130' if info['subject']=='The Descent from the Cross' else '131'} (printed p. 281) lists '{info['subject']}' under Bellucci. "
            "Chapter 10 (p. 281) names the subject as one of three large Canons chapel ceiling canvases and separately mentions twenty smaller canvases. The collective candidate `cand-8945` is not merged with this work."
        ),
        "boundary_zh": (
            "题名是依据索引子目添加的描述性名称，不是已核实的原题名。来源未提供单件作品的尺寸、媒材、现藏地或存续状态；关于 Canons 礼拜堂后来转移及使用的脚注材料未独立查阅。"
            "创作者—作品正式关系留待 S6；本批未建立关系、外部作品核验或 S5 补足。"
        ),
        "boundary_en": (
            "The title is a descriptive rendering based on the index sub-entry, not a verified original title. The source gives no individual dimensions, medium, present location, or survival status; the footnote material about the chapel's later transfer and use was not independently consulted. "
            "The formal creator-work relation remains for S6; this batch creates no relation, external work verification, or S5 enrichment."
        ),
        "type_notes_zh": "作品；索引子目对应三幅大型画中的一件。与三幅画的集合候选 cand-8945 分开。",
        "type_notes_en": "Work; the index sub-entry corresponds to one of the three large canvases. Keep it distinct from collective candidate cand-8945.",
        "sources": [
            card_writer.source(
                "10", "281", "10_CHP-10_intro.md", "L132-L133",
                "Bellucci painted three large and twenty smaller canvases which were let into the rococo ceiling, representing The Nativity, The Descent from the Cross and The Ascension,",
                f"Haskell names {info['subject']} as one of three subjects among Bellucci's large Canons chapel ceiling canvases. The index supplies a separate Bellucci sub-entry; the source does not provide an individual original title or present location.",
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


def update_status(text, new_count, groups, registered):
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
    assert count == 1, "process S4 status paragraph did not match"
    return text, reg_members, pending_groups, pending_members


def update_result(text, new_count, groups, registered, candidates):
    reg_members = sum(bool(row.get("ku_id")) for rows in registered.values() for row in rows)
    pending_groups = len(groups) - len(registered)
    pending_members = new_count - reg_members
    text = replace_once(
        text,
        "S4 已登记168组、映射216条成员候选；尚待登记4,670组、4,790条映射。",
        f"S4 已登记{len(registered)}组、映射{reg_members}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        "result current S4 totals",
    )
    new_rows = [row for rows in groups.values() for row in rows]
    typed = {kind: [r for r in new_rows if candidates[r["candidate_id"]]["suggested_type"] == kind] for kind in ("person", "work")}
    type_group_ids = {kind: {get_group(r["resolution_note"]) for r in rows} for kind, rows in typed.items()}
    registered_type_groups = {kind: {g for g in type_group_ids[kind] if g in registered} for kind in typed}
    mapped_by_type = {kind: sum(bool(r.get("ku_id")) for r in rows) for kind, rows in typed.items()}
    person_line = re.compile(r"person\s*类型[\d,]+组/[\d,]+条候选，已登记[\d,]+组/[\d,]+条、待登记[\d,]+组/[\d,]+条")
    text, count = person_line.subn(
        f"person 类型{len(type_group_ids['person']):,}组/{len(typed['person']):,}条候选，已登记{len(registered_type_groups['person']):,}组/{mapped_by_type['person']:,}条、待登记{len(type_group_ids['person'])-len(registered_type_groups['person']):,}组/{len(typed['person'])-mapped_by_type['person']:,}条",
        text,
        count=1,
    )
    assert count == 1, "result person type counts did not match"
    work_pending_groups = len(type_group_ids["work"]) - len(registered_type_groups["work"])
    work_pending_members = len(typed["work"]) - mapped_by_type["work"]
    text, count = re.compile(r"work\s*[\d,]+组/[\d,]+条").subn(
        f"work {work_pending_groups:,}组/{work_pending_members:,}条", text, count=1
    )
    assert count == 1, "result work pending counts did not match"
    text = replace_once(text, "1,187 KU；含本轮新增59个 person 组", "1,190 KU；含本轮新增60个 person 组", "current manifest total")
    text = replace_once(text, "Bernardo Bellotto、2个 Valmarana 组", "Bernardo Bellotto、Antonio Bellucci、2个 Valmarana 组", "registered person list")
    text = replace_once(text, "2个 work、2个 place 组", "4个 work、2个 place 组", "registered work count")
    text += (
        "\n\n### person / work：Antonio Bellucci 跨章人物及两件 Canons 作品 S4 登记（2026-10-16）\n\n"
        f"`cand-0282` 映射至 [Antonio Bellucci 人物卡](../units/persons/antonio-bellucci.md)；`cand-0283`、`cand-0284` 分别映射至 [《耶稣下十字架》](../units/works/antonio-bellucci-descent-from-the-cross-canons.md)与[《耶稣诞生》](../units/works/antonio-bellucci-nativity-canons.md)。人物卡保留 Haskell 对 Hapsburgs 与 Vienna 研究的限定；两件作品卡根据索引子目与 p.281 三幅大画叙述采用描述性标题。相关集合候选 `cand-8945` 仍独立待证；本批未新增正式关系、外部核验或 S5 补足。S4 当前累计登记171组/219条成员候选，待登记4,667组/4,787条。\n"
    )
    return text


def make_card(record):
    text = card_writer.make_card(record, "person" if record is PERSON else "work")
    text = text.replace("'2026-10-15'", "'2026-10-16'")
    assert record["name_en"] in text
    return text


def main():
    parser = argparse.ArgumentParser(description="Register Antonio Bellucci and two separately indexed Canons works as source-backed KUs.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidate_rows = read_csv(TABLES / "entity-candidates.csv")
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    assert len(manifest) == 1187, f"unexpected manifest size: {len(manifest)}"
    members = (PERSON_MEMBER, *WORKS.keys())
    assert all(cid in by_id and by_id[cid]["decision"] == "new" and not by_id[cid].get("ku_id") for cid in members)
    assert get_group(by_id[PERSON_MEMBER]["resolution_note"]) == PERSON_GROUP
    assert candidates[PERSON_MEMBER]["suggested_type"] == "person"
    for cid, info in WORKS.items():
        assert get_group(by_id[cid]["resolution_note"]) == info["group"]
        assert candidates[cid]["suggested_type"] == "work"
        assert candidates[cid]["index_entry_id"] in {"B.csv#130", "B.csv#131"}
        assert candidates[cid]["sub_entry"] == info["subject"].removeprefix("The ")
        assert not (ROOT / info["card_path"]).exists()
    assert not (ROOT / PERSON_CARD).exists()
    assert not any(row.get("ku_id") == PERSON_KU or row.get("card_path") == PERSON_CARD for row in manifest)
    assert not any(row.get("ku_id") in {info["ku_id"] for info in WORKS.values()} for row in manifest)

    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert PERSON_CARD not in accepted and all(info["card_path"] not in accepted for info in WORKS.values())
    statement_rows = [json.loads(line) for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    large_canvases = next(row for row in statement_rows if row.get("statement_id") == "st-chp10-p281-bellucci-canons-large-canvases")
    assert set(members) <= set(large_canvases["qualifiers"]["mentioned_candidate_ids"])

    records = {PERSON_MEMBER: PERSON, **{cid: work_record(info) for cid, info in WORKS.items()}}
    for record in records.values():
        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_count, groups_before, registered_before = current_counts(alignments)
    assert (new_count, len(groups_before), len(registered_before)) == (5006, 4838, 168)
    assert len(groups_before[PERSON_GROUP]) == 1 and groups_before[PERSON_GROUP][0]["candidate_id"] == PERSON_MEMBER
    for cid, info in WORKS.items():
        assert len(groups_before[info["group"]]) == 1 and groups_before[info["group"]][0]["candidate_id"] == cid

    direct_person = [r for r in statement_rows if r.get("subject_candidate_id") == PERSON_MEMBER or r.get("object_candidate_id") == PERSON_MEMBER]
    relation_person = [r for r in direct_person if r.get("qualifiers", {}).get("relation_candidate")]
    counterparts = set()
    for row in relation_person:
        s, o = row.get("subject_candidate_id"), row.get("object_candidate_id")
        counterparts.add(o if s == PERSON_MEMBER else s)
    counterparts.discard(None)
    counterpart_status = Counter(by_id[cid]["decision"] for cid in counterparts)
    assert relation_person and counterparts

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned_alignment if r.get("candidate_id") and not r.get("external_source")}
    planned_by_id[PERSON_MEMBER]["ku_id"] = PERSON_KU
    planned_by_id[PERSON_MEMBER]["resolution_note"] += f" S4 registration: mapped {PERSON_GROUP} to {PERSON_KU}."
    for cid, info in WORKS.items():
        planned_by_id[cid]["ku_id"] = info["ku_id"]
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {info['group']} to {info['ku_id']}."
    planned_manifest = list(manifest) + [
        {"ku_id": PERSON_KU, "type": "person", "canonical_name": PERSON["name_zh"], "name_en": PERSON["name_en"], "source_task": TASK, "card_path": PERSON_CARD},
        *[
            {"ku_id": info["ku_id"], "type": "work", "canonical_name": info["name_zh"], "name_en": info["name_en"], "source_task": TASK, "card_path": info["card_path"]}
            for info in WORKS.values()
        ],
    ]
    assert len(planned_manifest) == 1190
    new_after, groups_after, registered_after = current_counts(planned_alignment)
    assert (new_after, len(groups_after), len(registered_after)) == (5006, 4838, 171)
    mapped_after = sum(bool(row.get("ku_id")) for rows in groups_after.values() for row in rows)
    assert mapped_after == 219

    accepted_lines = accepted.splitlines()
    for card_path in sorted([PERSON_CARD, *(info["card_path"] for info in WORKS.values())]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > card_path),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {card_path}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    process_text, _, pending_groups, pending_members = update_status(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), new_after, groups_after, registered_after
    )
    process_text += (
        "\n\n### person / work：Antonio Bellucci 与两件 Canons 作品 S4 登记（2026-10-16）\n\n"
        f"- `cand-0282` 从 `{PERSON_GROUP}` 登记至 `{PERSON_KU}`（{PERSON_CARD}）；索引页码包括227、278、280–281、283–284、294及405–406，人物卡引述第10章 p.278、281 与第20章后记 p.406，并保留 Hapsburgs 的边界与 Vienna 年代的可能性限定。直接 S2 陈述 {len(direct_person)} 条，关系候选 {len(relation_person)} 条；对端决定 {dict(counterpart_status)}，均待后续关系阶段。\n"
        f"- `cand-0283` 与 `cand-0284` 分别登记至 `{WORKS['cand-0283']['ku_id']}` 和 `{WORKS['cand-0284']['ku_id']}`；索引 B.csv#130–131 与 p.281 集合描述共同支持两个单件作品。描述性标题不作原题名声明；集合候选 `cand-8945` 保持独立。\n"
        "- 两作品的创作端点虽由原书在集合画作叙述中共同说明，正式关系仍待 S6 逐端点审核；本批不新建关系，不做外部核验或 S5 补足。\n"
        f"- dry-run 核对3个 S3 成员、3张卡片、5处原文引文及登记外键；manifest 从1,187增至1,190，S4 累计登记171组/219条成员候选，待登记{pending_groups:,}组/{pending_members:,}条。"
    )
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), new_after, groups_after, registered_after, candidates)
    card_texts = {PERSON_CARD: make_card(PERSON)}
    card_texts.update({info["card_path"]: make_card(records[cid]) for cid, info in WORKS.items()})

    print("S4 Bellucci person/work registration dry-run passed")
    print("person member:", PERSON_MEMBER, "->", PERSON_KU)
    for cid, info in WORKS.items():
        print("work member:", cid, "->", info["ku_id"])
    print(f"person direct S2 statements={len(direct_person)}; relation candidates={len(relation_person)}; unique counterpart IDs={len(counterparts)}")
    print("counterpart decisions:", dict(counterpart_status))
    print("manifest=1,187 -> 1,190; registered=168 groups/216 candidates -> 171 groups/219 candidates")
    print("pending=4,667 groups/4,787 candidates; person pending=1,026/1,076; work pending=479/492")
    if args.dry_run:
        print("dry-run passed: cross-chapter identity, two separate indexed works, source quotes, and planned mappings checked; no files changed")
        return 0

    for card_path, card_text in card_texts.items():
        target = ROOT / card_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied: person and two work cards, manifest, accepted.yml, alignment mappings, process record, and current result counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
