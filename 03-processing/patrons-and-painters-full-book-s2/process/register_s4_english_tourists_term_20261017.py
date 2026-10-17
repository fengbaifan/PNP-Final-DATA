from __future__ import annotations

import argparse
import csv
import json
import sys
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
PROCESS_ANCHOR = "s4-english-tourists-italy-term-20261017"

RECORD = {
    "candidate_ids": ("cand-0973",),
    "group": "sg3-term-cand-0973",
    "ku_id": "units/terms/english-tourists-italy-late-seventeenth-century",
    "card_path": "04-knowledge/units/terms/english-tourists-italy-late-seventeenth-century.md",
    "title_zh": "17世纪后半赴意大利的英国旅行者",
    "name_en": "English Tourists in Italy in the Second Half of the Seventeenth Century",
    "description_zh": (
        "本术语记录哈斯克尔索引所指17世纪后半赴意大利的英国游客群体。第7章称，英国游客在这一时期数量增加，早期多数主要寻求自己的肖像；作者随后另提因公务留在意大利者，并以 Thomas Isham、Lord Exeter 等说明更广泛的赞助与收藏。"
        "这些是作者在同一讨论中区分的参与方式，不表示所有游客具有相同经历或赞助行为。"
    ),
    "description_en": (
        "This term records the group of English tourists in Italy during the second half of the seventeenth century identified in Haskell’s index. Chapter 7 says their numbers increased and that, at first, most were mainly interested in portraits of themselves; Haskell then separately mentions men detained in Italy on business and uses Thomas Isham and Lord Exeter to illustrate more extensive patronage and collecting. "
        "These are distinct modes of participation in the same discussion, not attributes shared by every tourist."
    ),
    "scope": (
        "**索引与原书用法：** `cand-0973` 对应索引 E.csv#8 子目“in second half of 17th century”，指向 p.197。第7章称这一时期赴意大利的游客人数增加，并概述他们最初的肖像需求；p.198 又提到意大利传记中关于 English milordi 访问画室的叙述。"
    ),
    "boundary": (
        "**对象边界：** 本卡记录书中这一时间限定的游客群体，不是正式组织、单一旅行团或具名个人名单。因公务留在意大利者是作者紧接着另行指出的少数人；Isham、Exeter 等收藏者是后文个案，不能据此推定每位游客都进行大规模委托。该群体也不等同于一般术语“英国对意大利艺术的赞助”（`units/terms/english-patronage-of-italian-art`）或概括性的 Grand Tour 旅行惯例。"
    ),
    "locator": "第7章 pp.197–198；索引 E.csv#8。",
    "sources": [
        {
            "chapter": "7", "page": "197", "file": "07_CHP-7_sec_iv.md", "lines": "65",
            "quote": "tourists who flocked to Italy in increasing numbers",
            "summary": "哈斯克尔称17世纪后半赴意大利的游客人数增加；索引将该时间段列为 English tourists in Italy 的子目。",
        },
        {
            "chapter": "7", "page": "197", "file": "07_CHP-7_sec_iv.md", "lines": "65",
            "quote": "At first the majority of these were interested only in their own likenesses",
            "summary": "作者概括游客早期多数主要关注自身肖像；保留为哈斯克尔的群体性判断。",
        },
        {
            "chapter": "7", "page": "198", "file": "07_CHP-7_sec_iv.md", "lines": "81",
            "quote": "the English milordi visiting studios, paying fabulous prices and inviting artists from all over the peninsula to come and settle in England",
            "summary": "哈斯克尔转述意大利传记关于英国贵族游客访问画室、高价购买及邀请艺术家赴英的叙述；该概述不用于识别未具名个人。",
        },
    ],
    "relations": [
        "st-chp7-p197-business-visitors-more-enterprising",
        "st-chp7-p197-tourist-patronage-comparison",
        "st-chp7-p197-tourists-seek-portraits",
        "st-chp7-p198-english-tourist-collecting",
        "st-chp7-p198-english-milordi-paid-fabulous-prices",
        "st-chp7-p198-english-milordi-invited-artists-to-england",
    ],
    "external_note": "本次依据本书索引与第7章正文登记术语；未新增外部旅游史、个人身份或委托事实验证。",
}


def update_process(text: str) -> str:
    text = base.replace_once(
        text,
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 28 / 38 | 901 / 903 |",
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 29 / 39 | 900 / 902 |",
        "process term S4 row",
    )
    text = base.replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **628 / 776** | **4,164 / 4,196** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **629 / 777** | **4,163 / 4,195** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    member = "`cand-0973`"
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 term：英国游客身份组登记（2026-10-17）

`cand-0973`（`{RECORD['group']}`）保持单一 S3 `new` term 组，映射至[{RECORD['title_zh']}术语卡](../../../{RECORD['card_path']})（`{RECORD['ku_id']}`）。该组与英国对意大利艺术赞助术语分开；游客多数、因公务留意大利者和后文的重要收藏者按原书语境区分。6条直接 S2 关系候选留待 S6；本次未新增正式关系、外部身份验证或 S5 enrichment。

S4累计登记629组/777条候选映射；待登记4,163组/4,195条；KU总数1,648。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = base.replace_once(
        text,
        "S4 已登记628组、映射776条成员候选；尚待登记4,164组、4,196条映射。",
        "S4 已登记629组、映射777条成员候选；尚待登记4,163组、4,195条映射。",
        "current S4 count",
    )
    text = base.replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,647 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,648 KU", "current manifest count")
    text = base.replace_once(
        text,
        "当前审计提示4,211条待登记 `decision=new` alignment 行，其中4,196条是4,164个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,210条待登记 `decision=new` alignment 行，其中4,195条是4,163个未登记身份组的候选映射，另15条是外部身份记录。",
        "current strict-stage pending rows",
    )
    text = base.replace_once(
        text,
        "| term | 42→35 | 941／929 | 28／901；903 | 0 | 2 | 655 |",
        "| term | 42→35 | 941／929 | 29／900；902 | 0 | 2 | 655 |",
        "result term S4 row",
    )
    text = base.replace_once(
        text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **628／4,164；4,196** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **629／4,163；4,195** | **8** | **100** | **5,441** |",
        "result total S4 row",
    )
    text = base.replace_once(
        text,
        "2026-10-17 四批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)及[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)；共新增15个KU与16条候选映射，105条直接关系候选继续待S6。",
        "2026-10-17 五批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)及[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)；共新增16个KU与17条候选映射，111条直接关系候选继续待S6。",
        "current S4 batch note",
    )
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-backed English tourist term group as an S4 relation endpoint")
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

    assert len(manifest) == 1647, f"unexpected manifest count: {len(manifest)}"
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
        assert RECORD["candidate_ids"][0] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")), statement_id
        assert (statement.get("qualifiers") or {}).get("relation_candidate") is True, statement_id
    for source in RECORD["sources"]:
        source_text = (ROOT / "02-sources" / "02-Markdown" / source["file"]).read_text(encoding="utf-8-sig")
        assert source["quote"] in source_text, source["quote"]

    groups, registered, pending = base.count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (628, 776)
    assert (len(pending), sum(map(len, pending.values()))) == (4164, 4196)
    term_registered = [members for members in registered.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "term" for r in members)]
    term_pending = [members for members in pending.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "term" for r in members)]
    assert (len(term_registered), sum(map(len, term_registered))) == (28, 38)
    assert (len(term_pending), sum(map(len, term_pending))) == (901, 903)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id["cand-0973"]["ku_id"] = RECORD["ku_id"]
    planned_by_id["cand-0973"]["resolution_note"] += f" S4 registration: mapped {RECORD['group']} to {RECORD['ku_id']}; direct relation candidates remain pending S6."
    planned_manifest = list(manifest) + [{
        "ku_id": RECORD["ku_id"], "type": "term", "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"], "source_task": TASK, "card_path": RECORD["card_path"],
    }]
    assert len(planned_manifest) == 1648
    _, registered_after, pending_after = base.count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (629, 777)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4163, 4195)

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
        print("dry-run passed: groups=1 candidates=1 direct_relation_candidates=6 registered_groups_after=629 mapped_candidates_after=777 pending_groups_after=4163 pending_candidates_after=4195 manifest_after=1648 cards=1")
        return 0

    (ROOT / RECORD["card_path"]).write_text(card_text, encoding="utf-8-sig", newline="\n")
    base.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    base.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=1 candidates=1 direct_relation_candidates=6 registered_groups=629 mapped_candidates=777 pending_groups=4163 pending_candidates=4195 manifest=1648 cards=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
