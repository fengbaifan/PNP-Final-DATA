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
PROCESS_ANCHOR = "s4-two-direct-endpoint-events-20261017"

RECORDS = [
    {
        "candidate_ids": ("cand-4780",),
        "group": "sg3-event-cand-4780",
        "ku_id": "units/events/first-operatic-performances-barberini-palace-1632",
        "card_path": "04-knowledge/units/events/first-operatic-performances-barberini-palace-1632.md",
        "title_zh": "巴贝里尼宫最初的歌剧演出（哈斯克尔纪为1632年2月）",
        "name_en": "First Operatic Performances at the Barberini Palace (February 1632 in Haskell’s Account)",
        "description_zh": (
            "本事件记录哈斯克尔所述巴贝里尼宫内最初举行的歌剧演出：正文记为1632年2月，并称数年后演出才从宫内大房间迁入 Pietro da Cortona 专门建造的剧场。"
            "这不是关于歌剧在欧洲或罗马首次出现的主张。"
        ),
        "description_en": (
            "This event records the first operatic performances held in the Barberini palace in Haskell’s account. The text dates them to February 1632 and says they moved from a large room in the palace to a purpose-built theatre by Pietro da Cortona only a few years later. "
            "It is not a claim about the first opera in Europe or Rome."
        ),
        "details_zh": (
            "**事件类型：** 宫廷宫邸内的歌剧演出\n- **哈斯克尔所记日期：** 1632年2月；注3记录1634、1633与1632等异说，并称1632年获 Bouchard 证词与一则 avviso 支持，后续重演造成混淆。\n- **起初场地：** 巴贝里尼宫内大房间。\n- **后续场地：** 数年后迁入 Pietro da Cortona 建造、可容纳约3,000人的专用剧场。\n- **证据边界：** 日期及迁移叙述均按哈斯克尔正文与注3登记，本轮未另行核对注中所引文献。"
        ),
        "details_en": (
            "**Event type:** Operatic performances in a court palace\n- **Date in Haskell:** February 1632; footnote 3 records competing dates of 1634, 1633, and 1632, and endorses 1632 on Bouchard’s evidence and an avviso; later repeat performances caused confusion.\n- **Initial venue:** A large room in the Barberini palace.\n- **Later venue:** A purpose-built theatre by Pietro da Cortona, seating about 3,000, to which the performances moved a few years later.\n- **Evidence boundary:** Dates and transfer are recorded from Haskell’s text and note 3; the cited works have not been independently checked in this registration."
        ),
        "boundary_zh": "**身份边界：** 本卡是宫内演出事件组，不是剧场建筑或某一部歌剧作品；演出参与者、剧目与相关人员仍按各自候选处理。正文称“最初”演出，范围限于巴贝里尼宫的叙述语境。日期采用哈斯克尔在注3中的裁决，同时保留其列出的史料分歧，不扩展为独立验证结论。",
        "boundary_en": "**Identity boundary:** This card records the palace performance event, not the theatre building or a particular opera. Participants, works, and related people remain separate candidates. Haskell’s wording about performances “for the first time” is limited to this palace context. The date follows his conclusion in note 3 while retaining the cited disagreement; it is not presented as an independent verification.",
        "sources": [
            {
                "chapter": "2", "page": "56", "lines": "148", "file": "02_CHP-2_sec_iv.md",
                "quote": "Operatic performances were given for the first time in February 1632",
                "summary": "第2章称巴贝里尼宫内的歌剧演出始于1632年2月，并说明演出后来迁至专用剧场。",
            },
            {
                "chapter": "2", "page": "56（注3）", "lines": "239", "file": "02_CHP-2_sec_iv.md",
                "quote": "This latter date, confirmed by Bouchard’s evidence and an avviso published by Clementi, I, p. 444, is the correct one and the muddle has been caused by the repeat performances given in later years",
                "summary": "注3列举1634、1633和1632等日期说；哈斯克尔依据 Bouchard 与 avviso 取1632年，并将混淆归于后续重演。",
            },
        ],
        "relations": [
            "st-chp2-seciv-l139-152-bouchard-attends-first-performance-fragment",
            "st-chp2-seciv-l139-152-operatic-performances-and-theatre-transfer",
            "st-chp2-seciv-l171-179-bouchard-attends-first-performance-continuation",
            "st-chp2-seciv-l171-179-s-alessio-performance-and-plot",
            "st-chp2-seciv-l171-179-young-barberini-cardinals-greet-guests",
            "st-chp2-seciv-l190-245-operatic-performance-date-dispute",
        ],
        "external_note": "本次依据哈斯克尔正文与注3登记事件；注中所引 Bouchard、avviso 及二手研究未在本轮独立核查。",
    },
    {
        "candidate_ids": ("cand-4767",),
        "group": "sg3-event-cand-4767",
        "ku_id": "units/events/cardinal-antonio-medieval-joust-piazza-navona-1634",
        "card_path": "04-knowledge/units/events/cardinal-antonio-medieval-joust-piazza-navona-1634.md",
        "title_zh": "卡迪纳尔安东尼奥在纳沃纳广场组织的中世纪式骑士比武（1634）",
        "name_en": "Cardinal Antonio’s Medieval Joust in Piazza Navona (1634)",
        "description_zh": (
            "本事件记录哈斯克尔所述1634年卡迪纳尔安东尼奥在罗马纳沃纳广场组织的中世纪式骑士比武。原计划是迎接一位波兰亲王来访的娱乐活动；亲王取消访问后，安东尼奥仍决定举行，并以复兴青年骑士精神为由。Bentivoglio 负责安排，Andrea Sacchi 绘制了比武高潮场面。"
        ),
        "description_en": (
            "This event records the medieval-style joust that Haskell says Cardinal Antonio organised in Rome’s Piazza Navona in 1634. It was first planned as entertainment for a visiting Polish prince; after the visit was cancelled, Antonio continued with the event, invoking the revival of chivalry among Rome’s young men. Bentivoglio arranged it, and Andrea Sacchi painted its culminating moment."
        ),
        "details_zh": (
            "**事件类型：** 纳沃纳广场的中世纪式骑士比武与公共庆典\n- **哈斯克尔所记日期：** 1634年。\n- **地点：** 罗马纳沃纳广场。\n- **组织者：** 卡迪纳尔安东尼奥·巴贝里尼。\n- **筹办与记录：** Bentivoglio 负责安排；Andrea Sacchi 绘制高潮场面，并为 Bentivoglio 的记述绘制插图。\n- **原计划与实际举行：** 原拟作为迎接波兰亲王的娱乐；来访取消后仍举行。\n- **证据边界：** 日期、目的及过程按哈斯克尔叙述登记；本卡不将作者的动机转述等同于组织者可独立核实的内心事实。"
        ),
        "details_en": (
            "**Event type:** Medieval-style joust and public spectacle in Piazza Navona\n- **Date in Haskell:** 1634.\n- **Place:** Piazza Navona, Rome.\n- **Organizer:** Cardinal Antonio Barberini.\n- **Arrangements and record:** Bentivoglio arranged the event; Andrea Sacchi painted its culmination and illustrated Bentivoglio’s account.\n- **Original plan and event:** Planned as entertainment for a Polish prince; it went ahead after the visit was cancelled.\n- **Evidence boundary:** Date, purpose, and sequence follow Haskell’s account; his reported motive is not treated as independently verified interior intent."
        ),
        "boundary_zh": "**身份边界：** 本卡记录一次比武事件，不是 Sacchi 的绘画作品、Bentivoglio 的书或巴贝里尼家族整体复兴骑士传统的抽象概念。相关人物、作品、家族与地点仍各按其候选身份审查；本次不因同一叙述建立正式关系。",
        "boundary_en": "**Identity boundary:** This card records one joust, not Sacchi’s painting, Bentivoglio’s book, or an abstract concept of the Barberini revival of chivalry. People, works, families, and the place remain separate candidate identities; no formal relation is created from their co-occurrence in this account.",
        "sources": [
            {
                "chapter": "2", "page": "55", "lines": "134", "file": "02_CHP-2_sec_iv.md",
                "quote": "the great ‘mediaeval joust’ which Cardinal Antonio organised in the Piazza Navona in 1634",
                "summary": "哈斯克尔将该比武定为1634年，并指明组织者和纳沃纳广场地点。",
            },
            {
                "chapter": "2", "page": "55", "lines": "135–136", "file": "02_CHP-2_sec_iv.md",
                "quote": "which, owing to the state of the times, was ignored rather than wholly lost",
                "summary": "正文引述安东尼奥希望令罗马青年重拾骑士精神的说法；本卡保留为哈斯克尔转述的活动理由。",
            },
            {
                "chapter": "2", "page": "56", "lines": "140–141", "file": "02_CHP-2_sec_iv.md",
                "quote": "Andrea Sacchi painted the culminating moment",
                "summary": "第2章称 Sacchi 绘制纳沃纳广场比武高潮场面；作品本体与事件分别处理。",
            },
        ],
        "relations": [
            "st-chp2-seciv-l127-137-antonio-continues-joust-to-revive-chivalry",
            "st-chp2-seciv-l127-137-antonio-organizes-mediaeval-joust",
            "st-chp2-seciv-l127-137-author-irony-at-clerical-society",
            "st-chp2-seciv-l127-137-bentivoglio-arranges-joust",
            "st-chp2-seciv-l127-137-joust-planned-for-prince-visit-cancelled",
            "st-chp2-seciv-l139-152-joust-pastiche-receives-delighted-approval",
        ],
        "external_note": "本次依据第2章事件叙述登记；未新增外部活动记录、日期核查或参会者身份验证。",
    },
]


def build_card(record: dict) -> str:
    sources = []
    for item in record["sources"]:
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
        "title": f"{record['title_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": "event",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    yaml_text = base.card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relations = "、".join(f"`{item}`" for item in record["relations"])
    members = "、".join(f"`{item}`" for item in record["candidate_ids"])
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 时间、地点与过程

**中文：**

{record['details_zh']}

**English:**

{record['details_en']}

### 身份边界

中文：{record['boundary_zh']}

English: {record['boundary_en']}

**候选定位：** {members}；S3 身份组 `{record['group']}`。

## 关系与证据

未建立正式关系。该身份组有 {len(record['relations'])} 条 `relation_candidate=true` 的直接 S2 关系候选：{relations}。这些候选均保留待 S6 逐条审查；本次只完成 S4 身份登记，没有写入 `relations.csv`。

### 身份与外部链接

{record['external_note']}
"""
    return f"---\n{yaml_text}---\n\n{body}"


def update_process(text: str) -> str:
    text = base.replace_once(
        text,
        "| event | 357 | 7 | 231 / 235 | 0 | 0 | 115 | 29 / 33 | 202 / 202 |",
        "| event | 357 | 7 | 231 / 235 | 0 | 0 | 115 | 31 / 35 | 200 / 200 |",
        "process event S4 row",
    )
    text = base.replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **632 / 780** | **4,160 / 4,192** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **634 / 782** | **4,158 / 4,190** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    notes = []
    for record in RECORDS:
        notes.append(
            f"- `{record['candidate_ids'][0]}`（`{record['group']}`）保持 S3 `new` event 组，映射至[{record['title_zh']}事件卡](../../../{record['card_path']})（`{record['ku_id']}`）。{record['boundary_zh']} 6条直接关系候选留待 S6。"
        )
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 event：两组直接关系端点登记（2026-10-17）

本批登记两个已有 S3 `new` event 组；日期、来源归属与对象边界见对应卡片：

{chr(10).join(notes)}

两组登记2个 event KU 与2条候选映射。共12条直接 S2 关系候选继续待 S6；本次未新增正式关系、外部事件验证或 S5 enrichment。

S4累计登记634组/782条候选映射；待登记4,158组/4,190条；KU总数1,653。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = base.replace_once(text,
        "S4 已登记632组、映射780条成员候选；尚待登记4,160组、4,192条映射。",
        "S4 已登记634组、映射782条成员候选；尚待登记4,158组、4,190条映射。", "current S4 count")
    text = base.replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,651 KU", "| [KU 登记](../tables/ku-manifest.csv) | 1,653 KU", "current manifest count")
    text = base.replace_once(text,
        "当前审计提示4,207条待登记 `decision=new` alignment 行，其中4,192条是4,160个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,205条待登记 `decision=new` alignment 行，其中4,190条是4,158个未登记身份组的候选映射，另15条是外部身份记录。", "current strict-stage pending rows")
    text = base.replace_once(text,
        "| event | 7→7 | 235／231 | 29／202；202 | 0 | 0 | 115 |",
        "| event | 7→7 | 235／231 | 31／200；200 | 0 | 0 | 115 |", "result event S4 row")
    text = base.replace_once(text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **632／4,160；4,192** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **634／4,158；4,190** | **8** | **100** | **5,441** |", "result total S4 row")
    text = base.replace_once(text,
        "2026-10-17 七批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)、[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)及[不雅与艳情索引主题](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-indecency-erotic-term-20261017)；共新增19个KU与20条候选映射，129条直接关系候选继续待S6。",
        "2026-10-17 八批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)、[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)、[英国游客身份组](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-english-tourists-italy-term-20261017)、[修会教堂与罗马画家群体](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017-batch2)、[不雅与艳情索引主题](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-indecency-erotic-term-20261017)及[两组事件](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-events-20261017)；共新增21个KU与22条候选映射，141条直接关系候选继续待S6。", "current S4 batch note")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Register two source-backed event groups that are direct S2 relation endpoints")
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

    assert len(manifest) == 1651, f"unexpected manifest count: {len(manifest)}"
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
            assert candidate_by_id[candidate_id]["suggested_type"] == "event"
            row = alignment_by_id[candidate_id]
            assert row["decision"] == "new" and not row.get("ku_id")
            assert base.get_group(row.get("resolution_note", "")) == record["group"]
        for item in manifest:
            if item["type"] == "event":
                assert item["name_en"].casefold() != record["name_en"].casefold()
                assert item["canonical_name"].casefold() != record["title_zh"].casefold()

    relation_ids = {item for record in RECORDS for item in record["relations"]}
    statements = {}
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("statement_id") in relation_ids:
                statements[statement["statement_id"]] = statement
    assert set(statements) == relation_ids
    for record in RECORDS:
        for statement_id in record["relations"]:
            statement = statements[statement_id]
            assert record["candidate_ids"][0] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")), statement_id
            assert (statement.get("qualifiers") or {}).get("relation_candidate") is True, statement_id
        for source in record["sources"]:
            source_text = (ROOT / "02-sources" / "02-Markdown" / source["file"]).read_text(encoding="utf-8-sig")
            assert source["quote"] in source_text, (record["group"], source["quote"])

    groups, registered, pending = base.count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (632, 780)
    assert (len(pending), sum(map(len, pending.values()))) == (4160, 4192)
    event_registered = [members for members in registered.values() if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == "event" for row in members)]
    event_pending = [members for members in pending.values() if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == "event" for row in members)]
    assert (len(event_registered), sum(map(len, event_registered))) == (29, 33)
    assert (len(event_pending), sum(map(len, event_pending))) == (202, 202)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    for record in RECORDS:
        for candidate_id in record["candidate_ids"]:
            row = planned_by_id[candidate_id]
            row["ku_id"] = record["ku_id"]
            row["resolution_note"] += f" S4 registration: mapped {record['group']} to {record['ku_id']}; direct relation candidates remain pending S6."
        planned_manifest.append({
            "ku_id": record["ku_id"], "type": "event", "canonical_name": record["title_zh"],
            "name_en": record["name_en"], "source_task": TASK, "card_path": record["card_path"],
        })
    assert len(planned_manifest) == 1653
    _, registered_after, pending_after = base.count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (634, 782)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4158, 4190)

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
    card_texts = {record["card_path"]: build_card(record) for record in RECORDS}

    if args.dry_run:
        print("dry-run passed: groups=2 candidates=2 direct_relation_candidates=12 registered_groups_after=634 mapped_candidates_after=782 pending_groups_after=4158 pending_candidates_after=4190 manifest_after=1653 cards=2")
        return 0

    for record in RECORDS:
        (ROOT / record["card_path"]).write_text(card_texts[record["card_path"]], encoding="utf-8-sig", newline="\n")
    base.write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    base.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=2 candidates=2 direct_relation_candidates=12 registered_groups=634 mapped_candidates=782 pending_groups=4158 pending_candidates=4190 manifest=1653 cards=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
