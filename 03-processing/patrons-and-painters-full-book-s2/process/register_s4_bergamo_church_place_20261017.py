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
PROCESS_ANCHOR = "s4-bergamo-santa-maria-maggiore-place-20261017"

RECORD = {
    "candidate_id": "cand-7627",
    "group": "sg3-place-cand-7627",
    "ku_id": "units/places/santa-maria-maggiore-bergamo",
    "card_path": "04-knowledge/units/places/santa-maria-maggiore-bergamo.md",
    "title_zh": "贝加莫的圣母玛利亚教堂",
    "name_en": "Church of Santa Maria Maggiore in Bergamo",
    "description_zh": (
        "本地点知识元记录贝加莫的 Santa Maria Maggiore 教堂。哈斯克尔称其营建始于1137年，之后历经数世纪断续施工；书中描述其主体结构、门廊、钟楼、祭衣间及内部装饰在不同时期陆续变化。"
        "本卡以教堂建筑作为地点实体，不把其内部空间、建筑构件或祭坛画并入本体。"
    ),
    "description_en": (
        "This place unit records the church of Santa Maria Maggiore in Bergamo. Haskell says work began in 1137 and continued fitfully over several centuries; the book describes changes to its structure, porticoes, campanile, sacristy, and interior decoration at different times. "
        "The card denotes the church building as a place, separate from its interior spaces, architectural components, and altarpieces."
    ),
    "context_zh": (
        "**原书语境：** 第8章 p.215 将教堂置于贝加莫由外地艺术家参与的收藏与赞助讨论之后，先述其自1137年起的建筑变化，再转入1653年以后围绕中部交叉空间展开的装饰工程。该历史过程为地点定位证据，不表示相关作品或空间就是教堂本体。"
    ),
    "context_en": (
        "**Book context:** Chapter 8, p. 215 places the church after a discussion of collecting and patronage involving artists from outside Bergamo. Haskell first outlines building changes from 1137 and then turns to the decoration programme begun after 1653 around the central crossing. This history anchors the place identity; it does not make the works or interior spaces identical with the church building."
    ),
    "boundary_zh": "**对象边界：** 本卡与贝加莫城市本身分开；教堂的钟楼、祭衣间、穹顶、交叉空间及内部祭坛画保持各自对象身份。书中所述教堂工程和装饰关系仍留待 S6 按具体端点与证据审查。",
    "boundary_en": "**Identity boundary:** This card is distinct from the city of Bergamo. The campanile, sacristy, dome, crossing, and interior altarpieces remain separate objects. Construction and decoration relations described in the book remain pending S6 review against their specific endpoints and evidence.",
    "sources": [
        {
            "chapter": "8", "page": "215", "lines": "13", "file": "08_CHP-8_sec_ii.md",
            "quote": "Work on the church of Santa Maria Maggiore in Bergamo began in 1137, and continued fitfully over the next few centuries.",
            "summary": "哈斯克尔明确指名贝加莫的圣母玛利亚教堂，并将其营建起点记为1137年。",
        },
        {
            "chapter": "8", "page": "215", "lines": "13", "file": "08_CHP-8_sec_ii.md",
            "quote": "The successive modifications of the interior were far more drastic.",
            "summary": "第8章区分建筑本体与其内部装饰在历代发生的变化。",
        },
        {
            "chapter": "8", "page": "215", "lines": "13", "file": "08_CHP-8_sec_ii.md",
            "quote": "Traces of Gothic frescoes still remain, but from the middle of the sixteenth century the whole decoration was changed.",
            "summary": "哈斯克尔记述教堂内部保存的哥特式壁画痕迹及16世纪中叶后的装饰变化。",
        },
    ],
    "relations": [
        "st-chp8-p215-church-work-began-1137",
        "st-chp8-p215-gothic-fresco-traces-remain",
        "st-chp8-p215-decoration-changed-and-altar-paintings-appeared",
        "st-chp8-p215-campanile-completed-1425",
        "st-chp8-p215-sacristy-added-late-15c",
        "st-chp8-p216-committee-assessment-visit",
    ],
    "external_note": "本次仅依据第8章 p.215 的来源记录登记地点；未新增建筑目录、地址或外部建筑史验证。",
}


def build_card() -> str:
    sources = []
    for item in RECORD["sources"]:
        sources.append({
            "citation": base.card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}",
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    frontmatter = {
        "title": f"{RECORD['title_zh']}（{RECORD['name_en']}）",
        "name_en": RECORD["name_en"],
        "type": "place",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    yaml_text = base.card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relation_ids = "、".join(f"`{item}`" for item in RECORD["relations"])
    body = f"""## 内容

### 描述

**中文：** {RECORD['description_zh']}

**English:** {RECORD['description_en']}

### 本书语境

{RECORD['context_zh']}

{RECORD['context_en']}

### 身份边界

中文：{RECORD['boundary_zh']}

English: {RECORD['boundary_en']}

**候选定位：** `{RECORD['candidate_id']}`；S3 身份组 `{RECORD['group']}`。

## 关系与证据

未建立正式关系。该身份组有 {len(RECORD['relations'])} 条 `relation_candidate=true` 的直接 S2 关系候选：{relation_ids}。这些候选均保留待 S6 逐条审查；本次只完成 S4 身份登记，没有写入 `relations.csv`。

### 身份与外部链接

{RECORD['external_note']}
"""
    return f"---\n{yaml_text}---\n\n{body}"


def update_process(text: str) -> str:
    text = base.replace_once(
        text,
        "| place | 1,109 | 223 | 562 / 570 | 0 | 0 | 316 | 34 / 41 | 528 / 529 |",
        "| place | 1,109 | 223 | 562 / 570 | 0 | 0 | 316 | 35 / 42 | 527 / 528 |",
        "process place S4 row",
    )
    text = base.replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **634 / 782** | **4,158 / 4,190** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **635 / 783** | **4,157 / 4,189** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 place：贝加莫圣母玛利亚教堂登记（2026-10-17）

`{RECORD['candidate_id']}`（`{RECORD['group']}`）保持 S3 `new` place 组，映射至[{RECORD['title_zh']}地点卡](../../../{RECORD['card_path']})（`{RECORD['ku_id']}`）。来源将该教堂与贝加莫城市及内部空间、建筑构件、祭坛画区分；6条直接 S2 关系候选继续待 S6，本次不建立正式边或 S5 enrichment。

S4累计登记635组/783条候选映射；待登记4,157组/4,189条；KU总数1,654。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = base.replace_once(text,
        "S4 已登记634组、映射782条成员候选；尚待登记4,158组、4,190条映射。",
        "S4 已登记635组、映射783条成员候选；尚待登记4,157组、4,189条映射。", "current S4 count")
    text = base.replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,653 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,654 KU", "current manifest count")
    text = base.replace_once(text,
        "当前审计提示4,205条待登记 `decision=new` alignment 行，其中4,190条是4,158个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,204条待登记 `decision=new` alignment 行，其中4,189条是4,157个未登记身份组的候选映射，另15条是外部身份记录。", "current strict-stage pending rows")
    text = base.replace_once(text,
        "| place | 223→153 | 570／562 | 34／528；529 | 0 | 0 | 316 |",
        "| place | 223→153 | 570／562 | 35／527；528 | 0 | 0 | 316 |", "result place S4 row")
    text = base.replace_once(text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **634／4,158；4,190** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **635／4,157；4,189** | **8** | **100** | **5,441** |", "result total S4 row")
    text = base.replace_once(text,
        "2026-10-17 八批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)、[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)、[不雅与艳情索引主题](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-indecency-erotic-term-20261017)及[两组事件](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-events-20261017)；共新增21个KU与22条候选映射，141条直接关系候选继续待S6。",
        "2026-10-17 九批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)、[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)、[不雅与艳情索引主题](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-indecency-erotic-term-20261017)、[两组事件](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-events-20261017)及[贝加莫圣母玛利亚教堂](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-bergamo-santa-maria-maggiore-place-20261017)；共新增22个KU与23条候选映射，147条直接关系候选继续待S6。", "current S4 batch note")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-backed Bergamo church place group as an S4 relation endpoint")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = base.read_csv(MANIFEST_PATH)
    alignment_fields, alignments = base.read_csv(ALIGNMENT_PATH)
    _, candidates = base.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1653, f"unexpected manifest count: {len(manifest)}"
    assert not (ROOT / RECORD["card_path"]).exists()
    assert RECORD["ku_id"] not in manifest_by_id and RECORD["card_path"] not in accepted_text
    group_rows = [
        row for row in alignments
        if not row.get("external_source") and row.get("decision") == "new"
        and base.get_group(row.get("resolution_note", "")) == RECORD["group"]
    ]
    assert {row["candidate_id"] for row in group_rows} == {RECORD["candidate_id"]}
    candidate = candidate_by_id[RECORD["candidate_id"]]
    row = alignment_by_id[RECORD["candidate_id"]]
    assert candidate["suggested_type"] == "place"
    assert row["decision"] == "new" and not row.get("ku_id") and base.get_group(row.get("resolution_note", "")) == RECORD["group"]
    for item in manifest:
        if item["type"] == "place":
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
        assert RECORD["candidate_id"] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")), statement_id
        assert (statement.get("qualifiers") or {}).get("relation_candidate") is True, statement_id
    for source in RECORD["sources"]:
        source_text = (ROOT / "02-sources" / "02-Markdown" / source["file"]).read_text(encoding="utf-8-sig")
        assert source["quote"] in source_text, source["quote"]

    groups, registered, pending = base.count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (634, 782)
    assert (len(pending), sum(map(len, pending.values()))) == (4158, 4190)
    place_registered = [members for members in registered.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "place" for r in members)]
    place_pending = [members for members in pending.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "place" for r in members)]
    assert (len(place_registered), sum(map(len, place_registered))) == (34, 41)
    assert (len(place_pending), sum(map(len, place_pending))) == (528, 529)

    planned_alignment = [dict(item) for item in alignments]
    planned_by_id = {item["candidate_id"]: item for item in planned_alignment if item.get("candidate_id") and not item.get("external_source")}
    planned_by_id[RECORD["candidate_id"]]["ku_id"] = RECORD["ku_id"]
    planned_by_id[RECORD["candidate_id"]]["resolution_note"] += f" S4 registration: mapped {RECORD['group']} to {RECORD['ku_id']}; direct relation candidates remain pending S6."
    planned_manifest = list(manifest) + [{
        "ku_id": RECORD["ku_id"], "type": "place", "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"], "source_task": TASK, "card_path": RECORD["card_path"],
    }]
    assert len(planned_manifest) == 1654
    _, registered_after, pending_after = base.count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (635, 783)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4157, 4189)

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
    card_text = build_card()

    if args.dry_run:
        print("dry-run passed: groups=1 candidates=1 direct_relation_candidates=6 registered_groups_after=635 mapped_candidates_after=783 pending_groups_after=4157 pending_candidates_after=4189 manifest_after=1654 cards=1")
        return 0

    (ROOT / RECORD["card_path"]).write_text(card_text, encoding="utf-8-sig", newline="\n")
    base.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    base.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=1 candidates=1 direct_relation_candidates=6 registered_groups=635 mapped_candidates=783 pending_groups=4157 pending_candidates=4189 manifest=1654 cards=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
