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
PROCESS_ANCHOR = "s4-indecency-erotic-term-20261017"

RECORD = {
    "candidate_ids": ("cand-1313",),
    "group": "sg3-term-cand-1313",
    "ku_id": "units/terms/indecency-and-erotic-in-haskell-index",
    "card_path": "04-knowledge/units/terms/indecency-and-erotic-in-haskell-index.md",
    "title_zh": "哈斯克尔索引中的不雅与艳情主题",
    "name_en": "Indecency and the Erotic in Haskell’s Index",
    "description_zh": (
        "本术语对应哈斯克尔索引项“Indecency and the erotic”，汇集书中涉及裸体表现、情色内容及其道德边界的不同讨论。第7章谈及德意志王侯对裸体画的需求、对作品是否构成不雅的判断，以及女性裸体在意大利绘画中的历史位置；第17章另谈 Manfrin 以自拟情色题材组织绘画竞赛。"
        "索引项将不同作品、人物和时代的相关页码归在一起，不表示它们组成单一流派或共同立场。"
    ),
    "description_en": (
        "This term corresponds to Haskell’s index heading “Indecency and the erotic,” which gathers distinct discussions in the book concerning nude representation, erotic subject matter, and moral boundaries. Chapter 7 addresses German princely demand for nudes, judgments about whether paintings were obscene, and the historical role of the female nude in Italian painting; Chapter 17 separately discusses Manfrin’s competitions for pictures on erotic themes of his own devising. "
        "The index groups page references about different works, people, and periods; it does not imply one artistic movement or shared position."
    ),
    "scope": (
        "**索引用法：** `cand-1313` 对应索引 I.csv#4，页码包括 pp.127、140、162、175、183–184、194、195n、212–213n、217、239、257–258、381。卡片以第7章 pp.194–195 的裸体与道德评价，以及第17章 p.381 的情色题材竞赛作为可核读例证；不将所列页码压缩为单一叙事。"
    ),
    "boundary": (
        "**对象边界：** 本卡记录索引层面的主题汇集，不是艺术类型、单件作品、统一道德理论或所有裸体图像的总称。各页仍须按其人物、作品、赞助与语境分别解释；第17章的四个竞赛题材保留为具体题材，不由本 term 取代。第7章有关王侯品味的概括保留哈斯克尔所说“superficial survey”的限定。"
    ),
    "locator": "索引 I.csv#4；重点核读第7章 pp.194–195、第17章 p.381。",
    "sources": [
        {
            "chapter": "7", "page": "194", "file": "07_CHP-7_sec_iv.md", "lines": "35",
            "quote": "a superficial survey such as the present indicates only an intense preoccupation with the erotic",
            "summary": "哈斯克尔以自身的概览性调查概括德国王侯对情色题材的关注，同时明确承认不同王侯品味存在差异。",
        },
        {
            "chapter": "7", "page": "195", "file": "07_CHP-7_sec_iv.md", "lines": "41",
            "quote": "the female nude played a more important rôle in Italian painting during the half-century after 1670 than ever before or since",
            "summary": "第7章将女性裸体在1670年后半世纪意大利绘画中的作用作为作者的历史判断提出。",
        },
        {
            "chapter": "17", "page": "381", "file": "17_CHP-17_sec_i.md", "lines": "24",
            "quote": "pictures on erotic themes which he himself devised",
            "summary": "哈斯克尔称 Manfrin 组织画家竞赛，题材由其本人拟定；此处仅作为索引主题所涵盖的一例。",
        },
    ],
    "relations": [
        "st-chp7-p194-german-princely-taste-variation",
        "st-chp7-p194-nudes-expected",
        "st-chp7-p195-cignani-testimony",
        "st-chp7-p195-female-nude-historical-role",
        "st-chp7-p195-german-patron-generalization",
        "st-chp7-p195-lazzarini-testimony",
    ],
    "external_note": "本次依据书内索引与对应章节登记主题术语；未新增外部艺术史概括或作品身份验证。",
}


def update_process(text: str) -> str:
    text = base.replace_once(
        text,
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 31 / 41 | 898 / 900 |",
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 32 / 42 | 897 / 899 |",
        "process term S4 row",
    )
    text = base.replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **631 / 779** | **4,161 / 4,193** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **632 / 780** | **4,160 / 4,192** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    member_ids = "、".join(f"`{item}`" for item in RECORD["candidate_ids"])
    relation_ids = "、".join(f"`{item}`" for item in RECORD["relations"])
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 term：跨章索引主题登记（2026-10-17）

{member_ids}（`{RECORD['group']}`）保持 S3 `new` term 组，映射至[{RECORD['title_zh']}术语卡](../../../{RECORD['card_path']})（`{RECORD['ku_id']}`）。该身份按索引的主题性汇集登记；第7章的裸体画讨论与第17章的 Manfrin 竞赛保留各自语境，不据此构造统一流派或历史态度。

6条直接 S2 关系候选（{relation_ids}）继续待 S6。本次未新增正式关系、外部身份验证或 S5 enrichment。

S4累计登记632组/780条候选映射；待登记4,160组/4,192条；KU总数1,651。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = base.replace_once(text,
        "S4 已登记631组、映射779条成员候选；尚待登记4,161组、4,193条映射。",
        "S4 已登记632组、映射780条成员候选；尚待登记4,160组、4,192条映射。", "current S4 count")
    text = base.replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,650 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,651 KU", "current manifest count")
    text = base.replace_once(text,
        "当前审计提示4,208条待登记 `decision=new` alignment 行，其中4,193条是4,161个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,207条待登记 `decision=new` alignment 行，其中4,192条是4,160个未登记身份组的候选映射，另15条是外部身份记录。", "current strict-stage pending rows")
    text = base.replace_once(text,
        "| term | 42→35 | 941／929 | 31／898；900 | 0 | 2 | 655 |",
        "| term | 42→35 | 941／929 | 32／897；899 | 0 | 2 | 655 |", "result term S4 row")
    text = base.replace_once(text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **631／4,161；4,193** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **632／4,160；4,192** | **8** | **100** | **5,441** |", "result total S4 row")
    text = base.replace_once(text,
        "2026-10-17 六批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)及[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)；共新增18个KU与19条候选映射，123条直接关系候选继续待S6。",
        "2026-10-17 七批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)、[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)及[不雅与艳情索引主题](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-indecency-erotic-term-20261017)；共新增19个KU与20条候选映射，129条直接关系候选继续待S6。", "current S4 batch note")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-backed indecency and erotic term as an S4 relation endpoint")
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

    assert len(manifest) == 1650, f"unexpected manifest count: {len(manifest)}"
    assert not (ROOT / RECORD["card_path"]).exists()
    assert RECORD["ku_id"] not in manifest_by_id and RECORD["card_path"] not in accepted_text
    group_rows = [
        row for row in alignments
        if not row.get("external_source") and row.get("decision") == "new"
        and base.get_group(row.get("resolution_note", "")) == RECORD["group"]
    ]
    assert {row["candidate_id"] for row in group_rows} == set(RECORD["candidate_ids"])
    for candidate_id in RECORD["candidate_ids"]:
        assert candidate_by_id[candidate_id]["suggested_type"] == "term"
        row = alignment_by_id[candidate_id]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert base.get_group(row.get("resolution_note", "")) == RECORD["group"]
    for item in manifest:
        if item["type"] == "term":
            assert item["name_en"].casefold() != RECORD["name_en"].casefold()
            assert item["canonical_name"].casefold() != RECORD["title_zh"].casefold()

    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in RECORD["relations"]:
                statements[statement["statement_id"]] = statement
    assert set(statements) == set(RECORD["relations"])
    for statement_id, statement in statements.items():
        assert "cand-1313" in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")), statement_id
        assert (statement.get("qualifiers") or {}).get("relation_candidate") is True, statement_id
    for source in RECORD["sources"]:
        source_text = (ROOT / "02-sources" / "02-Markdown" / source["file"]).read_text(encoding="utf-8-sig")
        assert source["quote"] in source_text, source["quote"]

    groups, registered, pending = base.count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (631, 779)
    assert (len(pending), sum(map(len, pending.values()))) == (4161, 4193)
    term_registered = [members for members in registered.values() if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == "term" for row in members)]
    term_pending = [members for members in pending.values() if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == "term" for row in members)]
    assert (len(term_registered), sum(map(len, term_registered))) == (31, 41)
    assert (len(term_pending), sum(map(len, term_pending))) == (898, 900)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id["cand-1313"]["ku_id"] = RECORD["ku_id"]
    planned_by_id["cand-1313"]["resolution_note"] += f" S4 registration: mapped {RECORD['group']} to {RECORD['ku_id']}; direct relation candidates remain pending S6."
    planned_manifest = list(manifest) + [{
        "ku_id": RECORD["ku_id"], "type": "term", "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"], "source_task": TASK, "card_path": RECORD["card_path"],
    }]
    assert len(planned_manifest) == 1651
    _, registered_after, pending_after = base.count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (632, 780)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4160, 4192)

    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines)
         if line.startswith("- 04-knowledge/units/") and line[2:] > RECORD["card_path"]),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {RECORD['card_path']}")
    planned_accepted = "\n".join(accepted_lines) + "\n"
    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_text = base.make_card(RECORD)

    if args.dry_run:
        print("dry-run passed: groups=1 candidates=1 direct_relation_candidates=6 registered_groups_after=632 mapped_candidates_after=780 pending_groups_after=4160 pending_candidates_after=4192 manifest_after=1651 cards=1")
        return 0

    (ROOT / RECORD["card_path"]).write_text(card_text, encoding="utf-8-sig", newline="\n")
    base.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    base.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=1 candidates=1 direct_relation_candidates=6 registered_groups=632 mapped_candidates=780 pending_groups=4160 pending_candidates=4192 manifest=1651 cards=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
