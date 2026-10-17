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
GROUP = "new-person:donna-maidalchini-olimpia-d9e87ff16a"
MEMBERS = ("cand-1496",)
KU_ID = "units/persons/olimpia-maidalchini"
REL_PATH = "04-knowledge/units/persons/olimpia-maidalchini.md"


RECORD = {
    "name_zh": "奥林皮娅·马伊达尔基尼",
    "name_en": "Olimpia Maidalchini",
    "description_zh": (
        "哈斯克尔第6章称 Olimpia Maidalchini 为教皇英诺森十世的弟媳、卡米洛·潘菲利之母，并记她在卡米洛的家族与宫廷事务中发挥影响。第3章称她约于1650年劝说 Theatines 委托 Mattia Preti 绘制教堂后殿，第4章则记 Camillo Massimi 从 Velasquez 处购得她的肖像。书中对其性格及宫廷影响的评价均保留为作者叙述。"
    ),
    "description_en": (
        "Chapter 6 identifies Olimpia Maidalchini as Innocent X's sister-in-law and Camillo Pamfili's mother, and describes her influence in Camillo's family and court affairs. Chapter 3 says that around 1650 she persuaded the Theatines to commission Mattia Preti to paint their church apse; Chapter 4 records that Camillo Massimi acquired her portrait from Velasquez. The book's characterisations of her and her court influence remain attributed to Haskell."
    ),
    "context_zh": (
        "M.csv#33“Donna Olimpia Maidalchini”列出第3章 p.78、第4章 p.116、第6章 pp.147、150、153。第6章 p.147 以全名将她称为 Camillo 的母亲和教皇的弟媳，随后叙述她对 Camillo 婚姻与宫廷事务的影响；第3、4章分别记载她促成 Mattia Preti 委托及 Camillo Massimi 收藏其肖像。第6章 p.150 的灵柩费用争执按 Haskell 的记载保存。索引中的 Donna 是称谓，不据此增加其他姓名。"
    ),
    "context_en": (
        "M.csv#33, “Donna Olimpia Maidalchini,” points to Chapter 3 p. 78, Chapter 4 p. 116, and Chapter 6 pp. 147, 150, and 153. Chapter 6 p. 147 gives her full name and identifies her as Camillo's mother and the Pope's sister-in-law, then describes her influence over Camillo's marriage and court affairs. Chapters 3 and 4 record her role in the Mattia Preti commission and Camillo Massimi's acquisition of her portrait. The Chapter 6 p. 150 dispute over the Pope's coffin costs is retained as Haskell's account. “Donna” is treated as a form of address, not an additional personal name."
    ),
    "boundary_zh": (
        "本卡对应唯一 S3 候选 cand-1496，属于跨章组 `new-person:donna-maidalchini-olimpia-d9e87ff16a`。旧路径文件曾是第一、六章限定测试草稿，但不在 accepted.yml 或 KU manifest 中；本次在原路径更新登记，不把未采纳草稿当作既有 KU，也不另建重复路径。她是 Camillo 的母亲，与其妻 Olimpia Aldobrandini（既有 units/persons/olimpia-aldobrandini）为不同人物。17条直接 S2 断言端点中13条为关系候选，均待 S6；本批不新增正式关系、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents the sole S3 candidate cand-1496 in the cross-chapter group `new-person:donna-maidalchini-olimpia-d9e87ff16a`. A file at this path existed as a Chapter 1/6 test draft, but it was absent from accepted.yml and the KU manifest; this registration updates that path without treating the unaccepted draft as an existing KU or creating a duplicate path. She is Camillo's mother and is distinct from his wife, Olimpia Aldobrandini (the existing units/persons/olimpia-aldobrandini KU). Thirteen of 17 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": (
        "索引名为 Donna Olimpia Maidalchini；第6章正文给出姓名 Olimpia Maidalchini。卡片以 Olimpia Maidalchini 为英文规范显示名，并保留 Donna Olimpia 为书内称谓。"
    ),
    "type_notes_en": (
        "The index form is Donna Olimpia Maidalchini; Chapter 6 gives the name Olimpia Maidalchini. The English display name follows the personal name, while Donna Olimpia is retained as the form used in the book."
    ),
    "sources": [
        card_writer.source(
            "3", "78", "03_CHP-3_sec_iv.md", "17–18",
            "In about 1650 Pope\nInnocent X’s all-powerful sister-in-law, Donna Olimpia, persuaded the Theatines to commission Mattia Preti to paint the apse of their church.",
            "第3章称 Donna Olimpia 约于1650年劝说 Theatines 委托 Mattia Preti 绘制教堂后殿。",
        ),
        card_writer.source(
            "4", "116", "04_CHP-4_sec_ii.md", "197",
            "He also acquired from the painter a portrait of Donna Olimpia, the Pope’s greedy, ambitious and overbearing sister-in-law whose influence at court entertained and outraged the Roman newswriters.",
            "第4章称 Camillo Massimi 从 Velasquez 处购得 Donna Olimpia 肖像；作者对其性格及宫廷影响的评价保留为作者判断。",
        ),
        card_writer.source(
            "6", "147", "06_CHP-6_sec_i.md", "14–16",
            "he had been alternatively encouraged and thwarted by his formidable mother, the Pope’s sister-in-law, Donna\nOlimpia Maidalchini. This legendary figure, whose dominating position in Innocent X’s court, led to endless scandals and ferocious quarrels, was shrewd, greedy and ambitious.\nAbove all she was excessively jealous of anyone replacing her as the first lady in Rome, and she showed her displeasure at Camillo’s marriage by making sure that neither he nor his wife should be allowed into the city.",
            "第6章给出姓名 Olimpia Maidalchini，称她为 Camillo 的母亲、教皇的弟媳，并叙述其宫廷位置、作者评价及她对 Camillo 婚姻的反应。",
        ),
        card_writer.source(
            "6", "147", "06_CHP-6_sec_i.md", "17–18",
            "the 17-y earold Francesco Maidalchini who was chosen by his aunt Donna Olimpia to supersede\nCamillo as papal nephew was clearly not destined to make an impact on Roman culture.",
            "第6章称 Francesco Maidalchini 由其姑母 Donna Olimpia 选为继 Camillo 之后的 papal nephew。",
        ),
        card_writer.source(
            "6", "150", "06_CHP-6_sec_i.md", "56–57",
            "Donna Olimpia and Prince Camillo Pamfili refused to pay for a coffin for the Pope when he died in January 1655. While the corpse lay rotting in a cellar, mother and son quarrelled over who should be charged for the burial.\n‘He says that he has never received anything from His Holiness... . . She replies that she is not the heiress... . .’5",
            "第6章据其叙述及所引材料记 Donna Olimpia 与 Camillo 拒付英诺森十世的棺材费用，并争执葬礼费用归属；卡片保留该叙述层级。",
        ),
        card_writer.source(
            "6", "153", "06_CHP-6_sec_i.md", "88–89",
            "The extravagance of the Barberini and the\nWar of Castro, followed by the dominance at court of Donna Olimpia, provided obvious and much appreciated targets.",
            "第6章将 Donna Olimpia 在宫廷的支配地位与罗马讽刺文学的攻击对象联系起来。",
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


def group_of(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def replace_after_once(text, marker, old, new, label):
    start = text.index(marker) + len(marker)
    tail = replace_once(text[start:], old, new, label)
    return text[:start] + tail


def updated_process(text):
    text = replace_once(
        text,
        "截至 Bonomo Algarotti 批次，4,818 个当前 `new` 身份组中完成148组，余4,670组；4,988条成员候选中映射188条，余4,800条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记42组、75条候选，待登记1,043组、1,103条候选。",
        "截至 Donna Olimpia Maidalchini 批次，4,818 个当前 `new` 身份组中完成149组，余4,669组；4,988条成员候选中映射189条，余4,799条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记43组、76条候选，待登记1,042组、1,102条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Giovanni Vianello、Bonomo Algarotti 已登记为人物 KU。",
        "Giovanni Vianello、Bonomo Algarotti、Donna Olimpia Maidalchini 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Bonomo Algarotti 的15条及其他已登记对象的 S2 关系候选仍待 S6",
        "Bonomo Algarotti 的15条、Donna Olimpia Maidalchini 的17条（其中13条为关系候选）及其他已登记对象的 S2 关系候选仍待 S6",
        "process pending relation candidates",
    )
    batch = """### person：Donna Olimpia Maidalchini 跨章身份组登记（2026-10-16）

- `cand-1496`（M.csv#33）属于 `new-person:donna-maidalchini-olimpia-d9e87ff16a`，登记为 `units/persons/olimpia-maidalchini`。第3、4、6章的索引与 S2 锚点支持同一位 Donna Olimpia Maidalchini；第6章以全名说明她是 Camillo 的母亲及教皇的弟媳。她与 Camillo 的妻子 Olimpia Aldobrandini 不同；后者继续使用既有 KU `units/persons/olimpia-aldobrandini`。
- 固定路径原有一张第一、六章限定测试草稿，但该卡不在 accepted.yml 或 manifest 中，故 `new` 决定不改为复用。本批在原路径将草稿更新为当前双语 S4 卡，保留其母子／配偶身份边界及来源限定，不复制出第二张卡。
- 17条直接 S2 断言端点中13条为关系候选，全部留待 S6；未新增正式关系、外部身份记录或 S5 补足。批次脚本 [register_s4_person_olimpia_maidalchini_batch_20261016.py](register_s4_person_olimpia_maidalchini_batch_20261016.py) dry-run 核对唯一组成员、6处精确原文锚点、端点及候选数、既有妻子 KU 边界、旧草稿路径和登记外键后通过，再 apply 更新卡片、manifest、accepted.yml 与候选映射。manifest 从1,167增至1,168；累计登记149组、189条候选映射，余4,669组、4,799条候选。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def updated_result(text):
    text = replace_once(
        text,
        "目前完成148组、映射188条成员候选，余4,670组、4,800条映射。",
        "目前完成149组、映射189条成员候选，余4,669组、4,799条映射。",
        "result top S4 counts",
    )
    text = replace_once(
        text,
        "Bonomo Algarotti 四十个补充 person 组",
        "Bonomo Algarotti、Donna Olimpia Maidalchini 四十一个补充 person 组",
        "result top registered person names",
    )
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,167 KU；含本轮新增42个 person 组（",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,168 KU；含本轮新增43个 person 组（",
        "result manifest count",
    )
    text = replace_once(
        text,
        "Giovanni Vianello、Bonomo Algarotti、2个 Valmarana 组",
        "Giovanni Vianello、Bonomo Algarotti、Donna Olimpia Maidalchini、2个 Valmarana 组",
        "result manifest registered names",
    )
    text = replace_once(
        text,
        "当前已登记42个 person 组（",
        "当前已登记43个 person 组（",
        "result current person count",
    )
    text = replace_after_once(
        text,
        "当前已登记43个 person 组（",
        "Giovanni Vianello、Bonomo Algarotti、",
        "Giovanni Vianello、Bonomo Algarotti、Donna Olimpia Maidalchini、",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,670个 `new` 身份组、4,800条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记42组、75条候选，待登记1,043组、1,103条候选。",
        "当前尚余4,669个 `new` 身份组、4,799条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记43组、76条候选，待登记1,042组、1,102条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Donna Olimpia Maidalchini 跨章身份组登记（2026-10-16）

`cand-1496`（M.csv#33）已映射至 [Olimpia Maidalchini 人物卡](../../04-knowledge/units/persons/olimpia-maidalchini.md)。第3、4、6章支持同一人物；第6章给出全名，并称她是 Camillo 的母亲及教皇的弟媳。既有 `Olimpia Aldobrandini` KU 是 Camillo 的妻子，二人保持区分。固定路径的旧测试草稿未列入 accepted.yml 或 KU manifest，本次原位更新，不另建重复卡。17条直接 S2 端点中13条关系候选留待 S6；本批不新增正式关系、外部身份核验或 S5 补足。dry-run/apply 记录见[S4 批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_olimpia_maidalchini_batch_20261016.py)。manifest 从1,167增至1,168；累计登记149组、189条候选映射，余4,669组、4,799条。

"""
    return replace_once(
        text,
        "### person：Bonomo Algarotti 跨章直接端点登记（2026-10-16）\n\n",
        batch + "### person：Bonomo Algarotti 跨章直接端点登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Donna Olimpia Maidalchini person identity group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1167, f"unexpected manifest count: {len(manifest)}"
    counts = Counter(row["decision"] for row in current)
    assert counts == Counter({"same": 1698, "new": 4988, "undecided": 5614, "excluded": 97, "conflict": 7}), counts
    groups = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = group_of(row["resolution_note"])
            assert group
            groups[group].append(row)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new" and row.get("ku_id"):
            registered[group_of(row["resolution_note"])].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(groups), sum(map(len, groups.values()))) == (4818, 4988)
    assert (len(registered_groups), sum(len(value) for value in registered_groups.values())) == (148, 188)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert not any(row.get("ku_id") for row in groups[GROUP])
    assert alignment_by_id[MEMBERS[0]]["decision"] == "new"
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == KIND
    assert candidate_by_id[MEMBERS[0]]["canonical_name"] == "Maidalchini, Donna Olimpia"
    assert candidate_by_id[MEMBERS[0]]["index_entry_id"] == "M.csv#33"

    card_path = ROOT / REL_PATH
    old_draft = card_path.read_text(encoding="utf-8-sig")
    assert "本轮为第一、六章限定测试" in old_draft
    assert REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND
        and "olimpia maidalchini" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )
    assert any(row["candidate_id"] == "cand-3210" and row["ku_id"] == "units/persons/olimpia-aldobrandini" and row["decision"] == "same" for row in current)
    assert any(row["ku_id"] == "units/persons/olimpia-aldobrandini" and row["type"] == "person" for row in manifest)

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if MEMBERS[0] in {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert (len(endpoint_ids), len(relation_ids)) == (17, 13), (len(endpoint_ids), len(relation_ids))
    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id[MEMBERS[0]]["ku_id"] = KU_ID
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; adopted the pre-existing unaccepted draft path in place."
    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": KIND, "canonical_name": RECORD["name_zh"], "name_en": RECORD["name_en"], "source_task": TASK, "card_path": REL_PATH})
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new":
            planned_groups[group_of(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(len(value) for value in planned_registered.values())) == (149, 189)
    assert (len(planned_groups) - len(planned_registered), sum(len(value) - sum(bool(row.get("ku_id")) for row in value) for value in planned_groups.values())) == (4669, 4799)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, KIND)
    card_text, updated_count = re.subn(r"^updated: '2026-10-15'$", "updated: '2026-10-16'", card_text, flags=re.MULTILINE)
    card_text, created_count = re.subn(r"^created: '2026-10-15'$", "created: '2026-09-09'", card_text, flags=re.MULTILINE)
    assert updated_count == 1 and created_count == 1

    if args.dry_run:
        print(
            "dry-run passed: Donna Olimpia Maidalchini person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} source_quotes={len(RECORD['sources'])} "
            "existing_wife_KU_distinct=true legacy_draft_path_adopted=true registered_groups_after=149 "
            "mapped_candidates_after=189 pending_groups=4669 pending_candidates=4799 manifest_after=1168; no formal relations added"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > REL_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {REL_PATH}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(planned_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(planned_result, encoding="utf-8-sig", newline="\n")
    print(f"applied: Donna Olimpia Maidalchini person_groups=1 candidates=1 endpoints=17 relation_candidates=13 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
