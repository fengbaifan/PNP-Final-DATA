from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
PROCESS_ANCHOR = "s4-three-direct-endpoint-terms-20261017"


RECORDS = [
    {
        "candidate_ids": ("cand-0969", "cand-0970"),
        "group": "sg3-term-englishpatronage",
        "ku_id": "units/terms/english-patronage-of-italian-art",
        "card_path": "04-knowledge/units/terms/english-patronage-of-italian-art.md",
        "title_zh": "英国对意大利艺术的赞助",
        "name_en": "English patronage of Italian art",
        "description_zh": (
            "本术语记录哈斯克尔第7章关于英国方面赞助意大利艺术及延请意大利艺术家的书内主题。第177页讨论英国方面争取意大利主要艺术家的早期努力；第7章后段转向17世纪后半的英国王室、赴意大利旅行者及 Shaftesbury 所鼓励的艺术赞助。"
            "这些场景在书中分属不同阶段和参与者，不构成单一机构或连续政策。"
        ),
        "description_en": (
            "This term records Chapter 7’s account of English patronage of Italian art and efforts to recruit Italian artists. The chapter first discusses earlier English attempts to secure leading Italian artists, then turns to English royal patronage, travellers to Italy in the later seventeenth century, and the artistic patronage welcomed and stimulated by Shaftesbury. "
            "These episodes involve different periods and actors and do not constitute one institution or continuous policy."
        ),
        "scope": (
            "**原书与索引用法：** `cand-0970` 对应索引子目“of Italian artists in 17th century”，覆盖 pp.177–199；`cand-0969` 对应索引主项并锚定 p.198 对 Shaftesbury 所鼓励的 English patronage of the arts 的叙述。两条候选组成同一主题身份组，卡片分别保留早期延请、王室及旅行赞助、Shaftesbury 趣味的语境。"
        ),
        "boundary": (
            "**对象边界：** 本卡是哈斯克尔第7章所述的国别性赞助主题，不是机构、赞助人名单或所有英国人在意大利的活动汇总。它比既有一般术语 `Art patronage` 范围具体；“English tourists in Italy”候选 `cand-0973` 独立记录旅行者群体，不并入本卡。哈斯克尔关于王室赞助与游客影响的比较保留为作者判断。"
        ),
        "locator": "第7章 pp.177、195、197–198；索引 E.csv#4–5。",
        "sources": [
            {"chapter": "7", "page": "177", "file": "07_CHP-7_sec_i.md", "lines": "94", "quote": "English efforts to dislodge the principal Italian artists met with very similar results.", "summary": "第7章将英国争取意大利主要艺术家的努力与其他欧洲王权的尝试并置。"},
            {"chapter": "7", "page": "195", "file": "07_CHP-7_sec_iv.md", "lines": "44", "quote": "the impact of England upon Italian art was almost negligible before 1700", "summary": "哈斯克尔区分1700年前与下一世纪英国对意大利艺术影响的分量；该判断保留为作者概括。"},
            {"chapter": "7", "page": "197", "file": "07_CHP-7_sec_iv.md", "lines": "65", "quote": "the patronage of English royalty is of little consequence compared to that of the tourists who flocked to Italy in increasing numbers", "summary": "第7章比较英国王室赞助与赴意大利旅行者带来的委托；本卡不把比较量化。"},
            {"chapter": "7", "page": "198", "file": "07_CHP-7_sec_iv.md", "lines": "81", "quote": "he welcomed and stimulated English patronage of the arts", "summary": "哈斯克尔称 Shaftesbury 欢迎并促进英国艺术赞助；保留为书内观点。"},
        ],
        "relations": [
            "st-chp7-p177-i05", "st-chp7-p195-english-patronage-next-century",
            "st-chp7-p197-exeter-unique-commission-scale", "st-chp7-p197-tourist-patronage-comparison",
            "st-chp7-p198-enthusiasm-and-shaftesbury-theory", "st-chp7-p198-shaftesbury-welcomed-patronage",
        ],
        "external_note": "本次依本书索引和第7章正文登记术语；未新增外部赞助史或人物身份验证。",
    },
    {
        "candidate_ids": ("cand-4672",),
        "group": "sg3-term-cand-4672",
        "ku_id": "units/terms/wisdom-personified-sacchi-divine-wisdom",
        "card_path": "04-knowledge/units/terms/wisdom-personified-sacchi-divine-wisdom.md",
        "title_zh": "萨基《神圣智慧》中的智慧人格化概念",
        "name_en": "Wisdom Personified in Sacchi’s Divine Wisdom",
        "description_zh": (
            "本术语记录哈斯克尔第2章关于 Sacchi 耶稣堂前厅穹顶壁画主题“Divine Wisdom”的神学概念和人格化形象。作者称主题取自《所罗门智训》，并讨论它如何在巴贝里尼家族赞助语境中被解释、转化为对统治者的颂扬。"
            "卡片记录的是被表现的概念及其书内解释，不是壁画作品本身或圣经文本。"
        ),
        "description_en": (
            "This term records the theological concept and personification underlying the theme “Divine Wisdom” in Sacchi’s ceiling fresco for the vestibule of the Chiesa Nuova, as discussed in Chapter 2. Haskell says the subject derives from the Wisdom of Solomon and describes how it was interpreted in the Barberini patronage context and transformed into praise of the rulers. "
            "The card denotes the concept and its interpretation in the book, not the fresco itself or the biblical text."
        ),
        "scope": (
            "**原书用法：** 第2章 pp.50–51 将智慧概念、女性人格化形象、日轮与巴贝里尼家族纹章之间的图像联系置于同一图像解释中；作者指出经顾问解释后，智慧在一定程度上与要求尊崇它的具体统治者相认同。"
        ),
        "boundary": (
            "**对象边界：** 本卡与候选“Divine Wisdom”所指的壁画作品分开，也与《所罗门智训》这部文本分开。它不把基督教神学中的一切智慧概念合并到此条书内解释，也不独立裁决该图像解释的神学效力；相关作品、文本及人物关系仍按各自候选待 S6。"
        ),
        "locator": "第2章 pp.50–51。",
        "sources": [
            {"chapter": "2", "page": "50", "file": "02_CHP-2_sec_iv.md", "lines": "87", "quote": "Divine Wisdom, derived from the Apocryphal Wisdom of Solomon", "summary": "哈斯克尔称萨基穹顶壁画主题源自《所罗门智训》，并将其作为艺术中此前未表现的主题介绍。"},
            {"chapter": "2", "page": "50", "file": "02_CHP-2_sec_iv.md", "lines": "89", "quote": "Wisdom was majestically exalted—but it was, to a large extent, identified with the particular princes", "summary": "第2章称智慧被人格化并在一定程度上与特定统治者认同；该解释保留为作者的图像学论述。"},
            {"chapter": "2", "page": "51", "file": "02_CHP-2_sec_iv.md", "lines": "92", "quote": "it was a conventional emblem for Wisdom", "summary": "作者解释日轮一方面是智慧的惯用象征，另一方面又是巴贝里尼家族的标识。"},
        ],
        "relations": [
            "st-chp2-seciv-l79-89-divine-wisdom-artwork-personifies-concept",
            "st-chp2-seciv-l79-89-divine-wisdom-central-figure-description-continues",
            "st-chp2-seciv-l79-89-wisdom-of-solomon-calls-princes-to-honour-wisdom",
            "st-chp2-seciv-l91-94-love-and-fear-control-lust-and-wrath",
            "st-chp2-seciv-l91-94-sun-conventional-emblem-for-wisdom",
            "st-chp2-seciv-l91-94-wisdom-attributes-personified-as-maidens",
        ],
        "external_note": "本次未使用外部神学或图像学数据库；卡片保留哈斯克尔对图像主题的解释状态。",
    },
    {
        "candidate_ids": ("cand-4686",),
        "group": "sg3-term-cand-4686",
        "ku_id": "units/terms/bracciolini-barberini-ceiling-iconographic-programme",
        "card_path": "04-knowledge/units/terms/bracciolini-barberini-ceiling-iconographic-programme.md",
        "title_zh": "布拉奇奥利尼为巴贝里尼大礼堂设计的图像纲领",
        "name_en": "Bracciolini’s Iconographic Programme for the Barberini Great Ceiling",
        "description_zh": (
            "本术语记录哈斯克尔对 Francesco Bracciolini 为巴贝里尼宫大礼堂穹顶设计的图像纲领的叙述。作者称 Bracciolini 拟定的方案由 Pietro da Cortona 执行，旨在颂扬巴贝里尼家族；之后又比较宫殿穹顶的新主题、文学性和宫廷赞助语境。"
            "此条记录设计方案这一概念对象，不是穹顶壁画本身、诗稿档案或抽象的巴洛克风格。"
        ),
        "description_en": (
            "This term records Haskell’s account of Francesco Bracciolini’s iconographic programme for the great hall ceiling of the Barberini palace. The author says Bracciolini drew up the programme and Pietro da Cortona executed it as a hymn to the family’s glory; the discussion then compares the ceiling’s novel theme, literary character, and courtly patronage context. "
            "The unit denotes the design scheme, not the ceiling fresco itself, a manuscript archive, or an abstract Baroque style."
        ),
        "scope": (
            "**原书用法：** 第2章 p.51 以“programme”指 Bracciolini 拟定、Cortona 执行并颂扬巴贝里尼家族的方案；pp.52–53 继续讨论这一穹顶主题的象征内容、宫廷文学趣味及其在教皇赞助中的新颖性。"
        ),
        "boundary": (
            "**对象边界：** 本卡的 `term` 类型表示一项可识别的图像纲领概念，而非独立档案文献或单件作品。巴贝里尼大礼堂穹顶壁画本体仍按 work 候选处理；二者的正式 `depicts`、`realized_as` 或组成关系留待 S6，不在本次登记中建立。"
        ),
        "locator": "第2章 pp.51–53。",
        "sources": [
            {"chapter": "2", "page": "51", "file": "02_CHP-2_sec_iv.md", "lines": "94", "quote": "the programme which Francesco Bracciolini drew up and Pietro so brilliantly executed was designed as a hymn to their glory", "summary": "哈斯克尔称 Bracciolini 拟定、Cortona 执行的方案旨在颂扬巴贝里尼家族。"},
            {"chapter": "2", "page": "53", "file": "02_CHP-2_sec_iv.md", "lines": "108–109", "quote": "the very idea of such a theme was also quite new in papal patronage of the seventeenth century", "summary": "第2章称这一主题在17世纪教皇赞助中较新颖；该判断属于作者的历史比较。"},
            {"chapter": "2", "page": "53", "file": "02_CHP-2_sec_iv.md", "lines": "109", "quote": "Pietro da Cortona both reflect the intensely literary interests of the new court", "summary": "哈斯克尔将萨基与 Cortona 的穹顶置于新宫廷强烈文学趣味的背景中。"},
        ],
        "relations": [
            "st-chp2-seciv-l106-112-ceilings-literary-interests",
            "st-chp2-seciv-l106-112-papal-theme-novelty",
            "st-chp2-seciv-l106-112-princely-flattery-comparison",
            "st-chp2-seciv-l91-94-bracciolini-called-in-to-devise-family-programme",
            "st-chp2-seciv-l91-94-bracciolini-programme-executed-by-cortona-for-family-glory",
            "st-chp2-seciv-l96-104-bracciolini-cortona-plan-ceiling",
        ],
        "external_note": "本次按哈斯克尔的书内描述登记图像纲领术语；未新增外部档案或作品身份记录。",
    },
]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label} anchor; found {count}")
    return text.replace(old, new, 1)


def make_sources(record):
    rows = []
    for item in record["sources"]:
        rows.append({
            "citation": card_writer.BOOK_CITATION,
            "location": f"第{item['chapter']}章，印刷页{item['page']}；OCR L{item['lines']}",
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": f"lines {item['lines']}", "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": f"02-sources/02-Markdown/{item['file']}",
                "source_span": f"lines {item['lines']}; print p. {item['page']}",
            },
        })
    return rows


def make_card(record):
    frontmatter = {
        "title": f"{record['title_zh']}（{record['name_en']}）",
        "name_en": record["name_en"],
        "type": "term",
        "evidence_status": "source_backed",
        "sources": make_sources(record),
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#{PROCESS_ANCHOR}",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    relation_ids = "、".join(f"`{item}`" for item in record["relations"])
    member_ids = "、".join(f"`{item}`" for item in record["candidate_ids"])
    body = f"""## 内容

### 描述

**中文：** {record['description_zh']}

**English:** {record['description_en']}

### 术语范围与边界

{record['scope']}

{record['boundary']}

**候选定位：** {member_ids}；S3 身份组 `{record['group']}`。{record['locator']}

## 关系与证据

### 关系记录

未建立正式关系。该身份组有 {len(record['relations'])} 条 `relation_candidate=true` 的直接 S2 关系候选：{relation_ids}。这些候选均保留待 S6 逐条审查；本次只完成 S4 身份登记，没有写入 `relations.csv`。

### 身份与外部链接

{record['external_note']}
"""
    return f"---\n{fm}---\n\n{body}"


def count_groups(rows):
    groups = defaultdict(list)
    for row in rows:
        if row.get("decision") == "new" and not row.get("external_source"):
            group = get_group(row.get("resolution_note", ""))
            assert group, f"new decision lacks group: {row.get('candidate_id')}"
            groups[group].append(row)
    registered, pending = {}, {}
    for group, members in groups.items():
        mapped = [row for row in members if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(members) and len({row["ku_id"] for row in mapped}) == 1, group
            registered[group] = members
        else:
            pending[group] = members
    return groups, registered, pending


def update_process(text: str) -> str:
    text = replace_once(
        text,
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 25 / 34 | 904 / 907 |",
        "| term | 1,640 | 42 | 929 / 941 | 0 | 2 | 655 | 28 / 38 | 901 / 903 |",
        "process term S4 row",
    )
    text = replace_once(
        text,
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **625 / 772** | **4,167 / 4,200** |",
        "| **合计** | **12,407** | **1,886** | **4,792 / 4,972** | **8** | **100** | **5,441** | **628 / 776** | **4,164 / 4,196** |",
        "process total S4 row",
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' in text:
        raise AssertionError(f"process anchor already exists: {PROCESS_ANCHOR}")
    bullets = []
    for record in RECORDS:
        member_ids = "、".join(f"`{item}`" for item in record["candidate_ids"])
        bullets.append(
            f"- {member_ids}（`{record['group']}`）保持同一 S3 `new` term 组，映射至[{record['title_zh']}术语卡](../../../{record['card_path']})（`{record['ku_id']}`）。"
            f"{record['boundary']} {len(record['relations'])} 条直接关系候选留待 S6。"
        )
    entry = f"""

<a id="{PROCESS_ANCHOR}"></a>

### S4 term：三组直接关系端点登记（2026-10-17）

本批登记三个已有 S3 `new` 术语组，其中 English patronage 组含两条同组候选；同组候选共同映射至一个 KU。来源范围、类型边界和待证关系见对应卡片：

{chr(10).join(bullets)}

三组登记3个 term KU 与4条候选映射。共18条直接 S2 关系候选继续待 S6；本次未新增正式关系、外部术语验证或 S5 enrichment。

S4累计登记628组/776条候选映射；待登记4,164组/4,196条；KU总数1,647。
"""
    return text.rstrip() + entry


def update_result(text: str) -> str:
    text = replace_once(text,
        "S4 已登记625组、映射772条成员候选；尚待登记4,167组、4,200条映射。",
        "S4 已登记628组、映射776条成员候选；尚待登记4,164组、4,196条映射。", "current S4 count")
    text = replace_once(text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,644 KU",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,647 KU", "current manifest count")
    text = replace_once(text,
        "当前审计提示4,215条待登记 `decision=new` alignment 行，其中4,200条是4,167个未登记身份组的候选映射，另15条是外部身份记录。",
        "当前审计提示4,211条待登记 `decision=new` alignment 行，其中4,196条是4,164个未登记身份组的候选映射，另15条是外部身份记录。", "current strict-stage pending rows")
    text = replace_once(text,
        "| term | 42→35 | 941／929 | 25／904；907 | 0 | 2 | 655 |",
        "| term | 42→35 | 941／929 | 28／901；903 | 0 | 2 | 655 |", "result term S4 row")
    text = replace_once(text,
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **625／4,167；4,200** | **8** | **100** | **5,441** |",
        "| **合计** | **1,886→1,040** | **4,972／4,792** | **628／4,164；4,196** | **8** | **100** | **5,441** |", "result total S4 row")
    text = replace_once(text,
        "2026-10-17 三批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)及[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)；共新增12个KU与12条候选映射，87条直接关系候选继续待S6。",
        "2026-10-17 四批 S4 登记见[term批次一](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-terms-20261017)、[term批次二](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-two-direct-endpoint-terms-20261017)、[term批次三](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-three-direct-endpoint-terms-20261017)及[work批次](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#s4-five-direct-endpoint-works-20261017)；共新增15个KU与16条候选映射，105条直接关系候选继续待S6。", "current S4 batch note")
    return text


def main():
    parser = argparse.ArgumentParser(description="Register three source-backed term groups that are direct S2 relation endpoints")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    manifest_by_id = {row["ku_id"]: row for row in manifest}

    assert len(manifest) == 1644, f"unexpected manifest count: {len(manifest)}"
    for record in RECORDS:
        assert not (ROOT / record["card_path"]).exists()
        assert record["ku_id"] not in manifest_by_id and record["card_path"] not in accepted_text
        group_rows = [
            row for row in alignments
            if not row.get("external_source") and row.get("decision") == "new"
            and get_group(row.get("resolution_note", "")) == record["group"]
        ]
        assert {row["candidate_id"] for row in group_rows} == set(record["candidate_ids"]), record["group"]
        for cid in record["candidate_ids"]:
            assert candidate_by_id[cid]["suggested_type"] == "term"
            row = alignment_by_id[cid]
            assert row["decision"] == "new" and not row.get("ku_id") and get_group(row.get("resolution_note", "")) == record["group"]
        for item in manifest:
            if item["type"] == "term":
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
            assert any(cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) for cid in record["candidate_ids"]), statement_id
            assert (statement.get("qualifiers") or {}).get("relation_candidate") is True, statement_id
        for source in record["sources"]:
            text = (ROOT / "02-sources" / "02-Markdown" / source["file"]).read_text(encoding="utf-8-sig")
            assert source["quote"] in text, (record["group"], source["quote"])

    groups, registered, pending = count_groups(alignments)
    assert (len(groups), sum(map(len, groups.values()))) == (4792, 4972)
    assert (len(registered), sum(map(len, registered.values()))) == (625, 772)
    assert (len(pending), sum(map(len, pending.values()))) == (4167, 4200)
    term_registered = [members for members in registered.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "term" for r in members)]
    term_pending = [members for members in pending.values() if all(candidate_by_id[r["candidate_id"]]["suggested_type"] == "term" for r in members)]
    assert (len(term_registered), sum(map(len, term_registered))) == (25, 34)
    assert (len(term_pending), sum(map(len, term_pending))) == (904, 907)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    for record in RECORDS:
        for cid in record["candidate_ids"]:
            row = planned_by_id[cid]
            row["ku_id"] = record["ku_id"]
            row["resolution_note"] += f" S4 registration: mapped {record['group']} to {record['ku_id']}; direct relation candidates remain pending S6."
        planned_manifest.append({
            "ku_id": record["ku_id"], "type": "term", "canonical_name": record["title_zh"],
            "name_en": record["name_en"], "source_task": TASK, "card_path": record["card_path"],
        })
    assert len(planned_manifest) == 1647
    _, registered_after, pending_after = count_groups(planned_alignment)
    assert (len(registered_after), sum(map(len, registered_after.values()))) == (628, 776)
    assert (len(pending_after), sum(map(len, pending_after.values()))) == (4164, 4196)

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
    card_texts = {record["card_path"]: make_card(record) for record in RECORDS}

    if args.dry_run:
        print("dry-run passed: groups=3 candidates=4 direct_relation_candidates=18 registered_groups_after=628 mapped_candidates_after=776 pending_groups_after=4164 pending_candidates_after=4196 manifest_after=1647 cards=3")
        return 0

    for record in RECORDS:
        (ROOT / record["card_path"]).write_text(card_texts[record["card_path"]], encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print("applied: groups=3 candidates=4 direct_relation_candidates=18 registered_groups=628 mapped_candidates=776 pending_groups=4164 pending_candidates=4196 manifest=1647 cards=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
