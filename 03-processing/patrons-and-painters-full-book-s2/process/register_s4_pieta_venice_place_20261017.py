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
PROCESS_ANCHOR = "s4-pieta-venice-place-20261017"

RECORD = {
    "candidate_id": "cand-8551",
    "group": "sg3-place-cand-8551",
    "ku_id": "units/places/church-of-the-pieta-venice-haskell-account",
    "card_path": "04-knowledge/units/places/church-of-the-pieta-venice-haskell-account.md",
    "title_zh": "哈斯克尔所称威尼斯“Pietà”教堂",
    "name_en": "Church of the Pietà, Venice (Haskell’s Source-Level Name)",
    "description_zh": (
        "本地点知识元按哈斯克尔在第9章中的称呼，记录威尼斯的 Pietà 教堂。作者称其在18世纪上半叶建造，并叙述1745年决定重建、1754—1755年 Tiepolo 在椭圆形穹顶绘制《信仰的胜利》；另一处又将穹顶壁画说成教堂的委托。"
        "卡片保留来源名称，不推定其完整的意大利语正式名称。"
    ),
    "description_en": (
        "This place unit records the church in Venice that Haskell calls the Pietà in Chapter 9. He describes it as erected during the first half of the eighteenth century, reports the decision to rebuild it in 1745, and says Tiepolo painted The Triumph of Faith on its oval dome in 1754–55; elsewhere he refers to Tiepolo’s dome frescoes in the church. "
        "The card preserves Haskell’s source wording and does not infer a full Italian formal name."
    ),
    "context_zh": (
        "**原书语境：** 第9章 p.272 将教堂置于威尼斯宗教建筑与官方赞助讨论中：作者回述其14世纪的收容所前身、威尼斯总督与元老院的赞助，继而叙述1745年重建、Massari 的建筑设计及立面迟至约150年后才完成。第9章 p.202 另将 Tiepolo 为该教堂穹顶作画作为画家酬金比较的一例。"
    ),
    "context_en": (
        "**Book context:** Chapter 9, p. 272 discusses the church in the context of Venetian religious architecture and public patronage. Haskell recounts the fourteenth-century refuge on the site, patronage by the Doge and Senate, the 1745 rebuilding decision, Massari’s architectural role, and the façade’s much later completion. On p. 202 he also cites Tiepolo’s dome frescoes there when comparing artists’ fees."
    ),
    "boundary_zh": "**对象边界：** 本卡记录教堂这一 place 身份，不等同于旧址上的收容所／慈善机构、椭圆穹顶或 Tiepolo 的《信仰的胜利》壁画作品。哈斯克尔仅以 Pietà 称呼教堂；未凭本轮证据补写完整意大利语正式名称，也未将同址旧机构与后来教堂合并。",
    "boundary_en": "**Identity boundary:** This card denotes the church as a place, distinct from the earlier refuge or charitable institution on the site, the oval dome, and Tiepolo’s fresco The Triumph of Faith. Haskell calls the church the Pietà; this registration does not supply a full Italian formal name or merge the earlier institution with the later church.",
    "sources": [
        {
            "chapter": "9", "page": "202", "lines": "221", "file": "09_CHP-9_intro.md",
            "quote": "the church of the Pietà in Venice",
            "summary": "哈斯克尔将 Tiepolo 的穹顶壁画定位在威尼斯 Pietà 教堂；本卡按其来源命名记录地点。",
        },
        {
            "chapter": "9", "page": "272", "lines": "56–57", "file": "09_CHP-9_sec_ii.md",
            "quote": "The first stone was therefore laid by Doge Grimani when in 1745 it was decided to rebuild the church",
            "summary": "第9章记述教堂于1745年决定重建，并由总督 Grimani 奠基。",
        },
        {
            "chapter": "9", "page": "272", "lines": "58–59", "file": "09_CHP-9_sec_ii.md",
            "quote": "Massari was the architect",
            "summary": "哈斯克尔指名 Massari 为教堂建筑师，并接着讨论其对设计的意见及立面完成时间。",
        },
    ],
    "relations": [
        "st-chp9-p272-doge-grimani-rebuild",
        "st-chp9-p272-massari-architect",
        "st-chp9-p272-pieta-facade-delay",
        "st-chp9-p272-pieta-gazzetta-description",
        "st-chp9-p272-pieta-refuge-foundation",
        "st-chp9-p273-pieta-five-altar-pictures",
    ],
    "external_note": "本次仅依据哈斯克尔对 Pietà 教堂的称呼及第9章正文登记地点；未新增外部建筑记录或正式名称核验。",
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
        "| place | 1,109 | 223 | 562 / 570 | 0 | 0 | 316 | 35 / 42 | 527 / 528 |",
        "| place | 1,109 | 223 | 562 / 570 | 0 | 0 | 316 | 36 / 43 | 526 / 527 |",
        "process place S4 row",
    )
    text = base.replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **635 / 783** | **4,157 / 4,189** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **636 / 784** | **4,156 / 4,188** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 place：威尼斯 Pietà 教堂登记（2026-10-17）

`{RECORD['candidate_id']}`（`{RECORD['group']}`）保持 S3 `new` place 组，映射至[{RECORD['title_zh']}地点卡](../../../{RECORD['card_path']})（`{RECORD['ku_id']}`）。卡片保留哈斯克尔来源命名，与同址早期收容所、穹顶及壁画作品分开；6条直接 S2 关系候选继续待 S6，本次不建立正式边或 S5 enrichment。

S4累计登记636组/784条候选映射；待登记4,156组/4,188条；KU总数1,655。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = base.replace_once(text,
        "S4 已登记635组、映射783条成员候选；尚待登记4,157组、4,189条映射。",
        "S4 已登记636组、映射784条成员候选；尚待登记4,156组、4,188条映射。", "current S4 count")
    text = base.replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,654 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,655 KU", "current manifest count")
    text = base.replace_once(text,
        "当前审计提示4,204条待登记 `decision=new` alignment 行，其中4,189条是4,157个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,203条待登记 `decision=new` alignment 行，其中4,188条是4,156个未登记身份组的候选映射，另15条是外部身份记录。", "current strict-stage pending rows")
    text = base.replace_once(text,
        "| place | 223→153 | 570／562 | 35／527；528 | 0 | 0 | 316 |",
        "| place | 223→153 | 570／562 | 36／526；527 | 0 | 0 | 316 |", "result place S4 row")
    text = base.replace_once(text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **635／4,157；4,189** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **636／4,156；4,188** | **8** | **100** | **5,441** |", "result total S4 row")
    text = base.replace_once(text,
        "2026-10-17 九批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)、[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)、[不雅与艳情索引主题](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-indecency-erotic-term-20261017)、[两组事件](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-events-20261017)及[贝加莫圣母玛利亚教堂](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-bergamo-santa-maria-maggiore-place-20261017)；共新增22个KU与23条候选映射，147条直接关系候选继续待S6。",
        "2026-10-17 十批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)、[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)、[不雅与艳情索引主题](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-indecency-erotic-term-20261017)、[两组事件](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-events-20261017)、[贝加莫圣母玛利亚教堂](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-bergamo-santa-maria-maggiore-place)及[威尼斯 Pietà 教堂](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-pieta-venice-place-20261017)；共新增23个KU与24条候选映射，153条直接关系候选继续待S6。", "current S4 batch note")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Register the source-named Pietà church in Venice as an S4 place endpoint")
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

    assert len(manifest) == 1654, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (635, 783)
    assert (len(pending), sum(map(len, pending.values()))) == (4157, 4189)
    place_registered = [members for members in registered.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "place" for r in members)]
    place_pending = [members for members in pending.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "place" for r in members)]
    assert (len(place_registered), sum(map(len, place_registered))) == (35, 42)
    assert (len(place_pending), sum(map(len, place_pending))) == (527, 528)

    planned_alignment = [dict(item) for item in alignments]
    planned_by_id = {item["candidate_id"]: item for item in planned_alignment if item.get("candidate_id") and not item.get("external_source")}
    planned_by_id[RECORD["candidate_id"]]["ku_id"] = RECORD["ku_id"]
    planned_by_id[RECORD["candidate_id"]]["resolution_note"] += f" S4 registration: mapped {RECORD['group']} to {RECORD['ku_id']}; direct relation candidates remain pending S6."
    planned_manifest = list(manifest) + [{
        "ku_id": RECORD["ku_id"], "type": "place", "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"], "source_task": TASK, "card_path": RECORD["card_path"],
    }]
    assert len(planned_manifest) == 1655
    _, registered_after, pending_after = base.count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (636, 784)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4156, 4188)

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
        print("dry-run passed: groups=1 candidates=1 direct_relation_candidates=6 registered_groups_after=636 mapped_candidates_after=784 pending_groups_after=4156 pending_candidates_after=4188 manifest_after=1655 cards=1")
        return 0

    (ROOT / RECORD["card_path"]).write_text(card_text, encoding="utf-8-sig", newline="\n")
    base.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    base.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=1 candidates=1 direct_relation_candidates=6 registered_groups=636 mapped_candidates=784 pending_groups=4156 pending_candidates=4188 manifest=1655 cards=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
