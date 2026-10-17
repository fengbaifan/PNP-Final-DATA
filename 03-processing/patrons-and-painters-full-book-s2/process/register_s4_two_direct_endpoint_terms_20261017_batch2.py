from __future__ import annotations

import argparse
import json
from pathlib import Path

import register_s4_three_direct_endpoint_terms_20261017 as base


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s4-two-direct-endpoint-terms-20261017-batch2"

RECORDS = [
    {
        "candidate_ids": ("cand-0680",),
        "group": "sg3-term-cand-0680",
        "ku_id": "units/terms/churches-of-religious-orders-in-rome-haskell-account",
        "card_path": "04-knowledge/units/terms/churches-of-religious-orders-in-rome-haskell-account.md",
        "title_zh": "哈斯克尔所述罗马宗教修会的教堂",
        "name_en": "Churches of Religious Orders in Rome in Haskell’s Account",
        "description_zh": (
            "本术语记录哈斯克尔第3章所讨论的罗马宗教修会教堂及其营建、装饰。作者提及耶稣会、奥拉托利会和提亚蒂诺会的教堂，并将这些教堂的建设与装饰放在修会精神权威、罗马家族财力及教廷赞助等因素的互动中考察。"
            "卡片保留作者对各时期差异的说明，不把这些教堂解释为统一的建筑计划。"
        ),
        "description_en": (
            "This term records the churches of religious orders in Rome discussed in Chapter 3, including their construction and decoration. Haskell refers to Jesuit, Oratorian, and Theatine churches and considers their building and decoration in relation to the interaction of the orders’ spiritual authority, the financial power of Roman families, and court patronage. "
            "The card retains Haskell’s account of variation across periods and does not treat the churches as one coordinated building programme."
        ),
        "scope": (
            "**索引与原书用法：** `cand-0680` 对应索引 C.csv#204，主项为 Churches of religious orders，地点子目为 Rome，页码覆盖 pp.65–93。第3章还概述修会母堂的装饰、赞助条件与时期差异；本卡记录这一类别及作者的总体讨论。"
        ),
        "boundary": (
            "**对象边界：** 本卡是书内的类别性术语，不是修会、单一教堂或统一工程。Gesù、S. Ignazio、S. Andrea della Valle、Chiesa Nuova 等可辨认建筑仍各属 place 身份；本卡不替代这些对象，也不据类别表述新建教堂之间的正式关系。它与既有术语“宗教修会的艺术赞助”（`units/terms/patronage-by-religious-orders`）相关但不相同：本卡关注教堂类别及其营建、装饰语境。"
        ),
        "locator": "第3章 pp.63–65；索引 C.csv#204（Rome，pp.65–93）。",
        "sources": [
            {
                "chapter": "3", "page": "63", "file": "03_CHP-3_sec_i.md", "lines": "5",
                "quote": "their churches were extended, rebuilt, decorated and copied; artists eagerly competed for their commissions",
                "summary": "哈斯克尔概述罗马主要修会教堂的扩建、重建、装饰及其艺术委托。",
            },
            {
                "chapter": "3", "page": "64", "file": "03_CHP-3_sec_i.md", "lines": "21",
                "quote": "the Jesuits had to wait for decades before they were able to make any progress whatsoever with the decoration of their own churches",
                "summary": "第3章指出耶稣会自身教堂装饰曾长期受阻；作者将此置于财力与赞助机制中解释。",
            },
            {
                "chapter": "3", "page": "65", "file": "03_CHP-3_sec_i.md", "lines": "32–33",
                "quote": "churches belonging to the principal religious Orders depended on a synthesis derived from conflicting forces",
                "summary": "哈斯克尔将具名修会教堂的装饰概括为多种力量互动的结果，并强调其强弱随时期而异。",
            },
        ],
        "relations": [
            "st-chp3-seci-l16-24-jesuits-delayed-church-decoration",
            "st-chp3-seci-l26-33-church-decoration-synthesis",
            "st-chp3-seci-l26-33-churches-dialectic-spiritual-moneyed-patrons",
            "st-chp3-seci-l26-33-papal-court-patronage-personal-channels",
            "st-chp3-seci-l3-14-mother-churches-baroque-inference",
            "st-chp3-seci-l3-14-orders-rise-and-works",
        ],
        "external_note": "本次仅依据本书索引与第3章正文登记类别术语；未新增外部建筑身份或修会史验证。",
    },
    {
        "candidate_ids": ("cand-11845",),
        "group": "sg3-term-cand-11845",
        "ku_id": "units/terms/artists-drawn-to-rome-by-patronage-and-prospects",
        "card_path": "04-knowledge/units/terms/artists-drawn-to-rome-by-patronage-and-prospects.md",
        "title_zh": "因赞助与发展机会聚集罗马的画家群体",
        "name_en": "Artists Drawn to Rome by Patronage and Prospects",
        "description_zh": (
            "本术语记录哈斯克尔第1章关于17世纪罗马画家聚集机制的概括：贵族希望延请本国画家，艺术家则认为罗马提供足够的创作空间与报酬；两端的供需相互强化，使罗马成为不断变化的画家与鉴赏者人口汇聚之处。"
            "这里记录的是作者界定的社会性群体及其吸引机制，不是具名画家名单。"
        ),
        "description_en": (
            "This term records Haskell’s Chapter 1 account of the forces drawing painters to seventeenth-century Rome: aristocrats sought painters of their own nationality, while artists believed Rome offered sufficient scope and rewards; supply and demand reinforced one another, making the city a focus for a constantly changing population of painters and dilettantes. "
            "The unit denotes this source-defined social group and its attraction mechanism, not a list of named painters."
        ),
        "scope": (
            "**原书用法：** `cand-11845` 锚定第1章 pp.14–15 关于罗马对艺术家的“双重吸引”：贵族延请本国画家，艺术家寻求足够的机会与报酬；哈斯克尔称供需彼此强化，并指出罗马汇聚不断变化的画家与鉴赏者。"
        ),
        "boundary": (
            "**对象边界：** 本卡记录哈斯克尔在特定历史论述中划定的群体，不是正式团体、单一迁徙事件或罗马城市本身。未具名的群体判断不自动识别各成员；可识别画家仍按 person 身份分别登记。它与罗马 place 身份及一般的艺术赞助术语相区分，不把“发展机会”扩展为所有艺术家的共同动机。"
        ),
        "locator": "第1章 pp.14–15。",
        "sources": [
            {
                "chapter": "1", "page": "15", "file": "01_CHP-1_sec_ii.md", "lines": "87",
                "quote": "Rome alone offered them sufficient scope and rewards for their talents",
                "summary": "哈斯克尔称艺术家认为罗马能为其才干提供足够空间与报酬。",
            },
            {
                "chapter": "1", "page": "15", "file": "01_CHP-1_sec_ii.md", "lines": "87",
                "quote": "The process was self-generating: supply and demand reinforced each other",
                "summary": "第1章将艺术家赴罗马与贵族延聘之间的相互作用概括为供需强化过程。",
            },
            {
                "chapter": "1", "page": "15", "file": "01_CHP-1_sec_ii.md", "lines": "87",
                "quote": "the city became the focus of a constantly shifting population of painters and dilettantes in search of each other",
                "summary": "哈斯克尔称罗马成为不断变化的画家与鉴赏者人口相互寻找、汇聚的中心。",
            },
        ],
        "relations": [
            "st-chp1-secii-l79-84-17",
            "st-chp1-secii-l86-94-01",
            "st-chp1-secii-l86-94-01b",
            "st-chp1-secii-l86-94-01c",
            "st-chp1-secii-l86-94-01d",
            "st-chp1-secii-l86-94-01f",
        ],
        "external_note": "本次仅依据第1章的群体描述登记术语；未新增画家成员身份或外部迁徙史验证。",
    },
]


def update_process(text: str) -> str:
    text = base.replace_once(
        text,
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 29 / 39 | 900 / 902 |",
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 31 / 41 | 898 / 900 |",
        "process term S4 row",
    )
    text = base.replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **629 / 777** | **4,163 / 4,195** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **631 / 779** | **4,161 / 4,193** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    bullets = []
    for record in RECORDS:
        member_ids = "、".join(f"`{item}`" for item in record["candidate_ids"])
        bullets.append(
            f"- {member_ids}（`{record['group']}`）保持 S3 `new` term 组，映射至[{record['title_zh']}术语卡](../../../{record['card_path']})（`{record['ku_id']}`）。"
            f"{record['boundary']} {len(record['relations'])} 条直接关系候选留待 S6。"
        )
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 term：两组直接关系端点登记（2026-10-17）

本批登记两个已有 S3 `new` term 组。候选成员各自映射一个 KU；来源定位、语境和边界见对应卡片：

{chr(10).join(bullets)}

两组登记2个 term KU 与2条候选映射。共12条直接 S2 关系候选继续待 S6；本次未新增正式关系、外部身份验证或 S5 enrichment。

S4累计登记631组/779条候选映射；待登记4,161组/4,193条；KU总数1,650。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = base.replace_once(text,
        "S4 已登记629组、映射777条成员候选；尚待登记4,163组、4,195条映射。",
        "S4 已登记631组、映射779条成员候选；尚待登记4,161组、4,193条映射。", "current S4 count")
    text = base.replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,648 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,650 KU", "current manifest count")
    text = base.replace_once(text,
        "当前审计提示4,210条待登记 `decision=new` alignment 行，其中4,195条是4,163个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,208条待登记 `decision=new` alignment 行，其中4,193条是4,161个未登记身份组的候选映射，另15条是外部身份记录。", "current strict-stage pending rows")
    text = base.replace_once(text,
        "| term | 42→35 | 941／929 | 29／900；902 | 0 | 2 | 655 |",
        "| term | 42→35 | 941／929 | 31／898；900 | 0 | 2 | 655 |", "result term S4 row")
    text = base.replace_once(text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **629／4,163；4,195** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **631／4,161；4,193** | **8** | **100** | **5,441** |", "result total S4 row")
    text = base.replace_once(text,
        "2026-10-17 五批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)及[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)；共新增16个KU与17条候选映射，111条直接关系候选继续待S6。",
        "2026-10-17 六批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)及[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)；共新增18个KU与19条候选映射，123条直接关系候选继续待S6。", "current S4 batch note")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two source-backed term groups that are direct S2 relation endpoints")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    base.PROCESS_ANCHOR = PROCESS_ANCHOR
    manifest_fields, manifest = base.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = base.read_csv(ALIGNMENT_PATH)
    _, candidates = base.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1648, f"unexpected manifest count: {len(manifest)}"
    for record in RECORDS:
        assert not (ROOT / record["card_path"]).exists()
        assert record["ku_id"] not in manifest_by_id and record["card_path"] not in accepted_text
        group_rows = [
            row for row in alignments
            if not row.get("external_source") and row.get("decision") == "new"
            and base.get_group(row.get("resolution_note", "")) == record["group"]
        ]
        assert {row["candidate_id"] for row in group_rows} == set(record["candidate_ids"]), record["group"]
        for candidate_id in record["candidate_ids"]:
            assert candidate_by_id[candidate_id]["suggested_type"] == "term"
            row = alignment_by_id[candidate_id]
            assert row["decision"] == "new" and not row.get("ku_id")
            assert base.get_group(row.get("resolution_note", "")) == record["group"]
        for item in manifest:
            if item["type"] == "term":
                assert item["name_en"].casefold() != record["name_en"].casefold()
                assert item["canonical_name"].casefold() != record["title_zh"].casefold()

    all_relation_ids = {item for record in RECORDS for item in record["relations"]}
    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in all_relation_ids:
                statements[statement["statement_id"]] = statement
    assert set(statements) == all_relation_ids
    for record in RECORDS:
        for statement_id in record["relations"]:
            statement = statements[statement_id]
            assert any(candidate_id in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) for candidate_id in record["candidate_ids"]), statement_id
            assert (statement.get("qualifiers") or {}).get("relation_candidate") is True, statement_id
        for source in record["sources"]:
            source_text = (ROOT / "02-sources" / "02-Markdown" / source["file"]).read_text(encoding="utf-8-sig")
            assert source["quote"] in source_text, (record["group"], source["quote"])

    groups, registered, pending = base.count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (629, 777)
    assert (len(pending), sum(map(len, pending.values()))) == (4163, 4195)
    term_registered = [members for members in registered.values() if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == "term" for row in members)]
    term_pending = [members for members in pending.values() if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == "term" for row in members)]
    assert (len(term_registered), sum(map(len, term_registered))) == (29, 39)
    assert (len(term_pending), sum(map(len, term_pending))) == (900, 902)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    for record in RECORDS:
        for candidate_id in record["candidate_ids"]:
            row = planned_by_id[candidate_id]
            row["ku_id"] = record["ku_id"]
            row["resolution_note"] += f" S4 registration: mapped {record['group']} to {record['ku_id']}; direct relation candidates remain pending S6."
        planned_manifest.append({
            "ku_id": record["ku_id"], "type": "term", "canonical_name": record["title_zh"],
            "name_en": record["name_en"], "source_task": TASK, "card_path": record["card_path"],
        })
    assert len(planned_manifest) == 1650
    _, registered_after, pending_after = base.count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (631, 779)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4161, 4193)

    accepted_lines = accepted_text.splitlines()
    for record in sorted(RECORDS, key=lambda item: item["card_path"]):
        insert_at = next(
            (i for i, line in enumerate(accepted_lines)
             if line.startswith("- 04-knowledge/units/") and line[2:] > record["card_path"]),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {record['card_path']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_texts = {record["card_path"]: base.make_card(record) for record in RECORDS}

    if args.dry_run:
        print("dry-run passed: groups=2 candidates=2 direct_relation_candidates=12 registered_groups_after=631 mapped_candidates_after=779 pending_groups_after=4161 pending_candidates_after=4193 manifest_after=1650 cards=2")
        return 0

    for record in RECORDS:
        (ROOT / record["card_path"]).write_text(card_texts[record["card_path"]], encoding="utf-8-sig", newline="\n")
    base.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    base.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=2 candidates=2 direct_relation_candidates=12 registered_groups=631 mapped_candidates=779 pending_groups=4161 pending_candidates=4193 manifest=1650 cards=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
