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
UNITS = ROOT / "04-knowledge" / "units"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

KIND = "term"
GROUP = "sg3-term-cand-8108"
MEMBERS = ("cand-8108",)
KU_ID = "units/terms/venetian-nobility-social-estate"
CARD_PATH = "04-knowledge/units/terms/venetian-nobility-social-estate.md"
DATE = "2026-10-16"

RECORD = {
    "title_zh": "威尼斯贵族阶层",
    "name_en": "Venetian nobility",
    "description_zh": (
        "本书以“nobility”“aristocracy”及相关称谓指称威尼斯历史语境中的贵族社会阶层。第9章区分旧贵族家族、"
        "贫困的 patrician 家庭和新近获准进入贵族阶层的家庭，并讨论该阶层在政治任职、艺术赞助及文化活动中的位置。"
        "这是对哈斯克尔书内用法的记录，不将这一社会阶层等同于威尼斯共和国或其政府机构，也不将取得贵族身份的程序并入本概念。"
    ),
    "description_en": (
        "In this book, “nobility,” “aristocracy,” and related expressions refer to the Venetian noble estate in its historical social context. "
        "Chapter 9 distinguishes older families, poorer patrician families, and families newly admitted to the nobility, and discusses the estate "
        "in relation to political office, art patronage, and cultural activity. This records Haskell’s usage in the book; it does not identify the "
        "social estate with the Republic of Venice or a government office, or merge the process of admission into the concept."
    ),
    "sources": [
        card_writer.source(
            "9", "247", "09_CHP-9_intro.md", "28",
            "The whole government and higher administration of the State were in the hands of the nobility",
            "哈斯克尔称威尼斯国家的政府及高级行政由贵族掌握；这是关于其政治位置的作者叙述。",
        ),
        card_writer.source(
            "9", "247", "09_CHP-9_intro.md", "28",
            "new families, who were allowed to buy themselves into the nobility",
            "哈斯克尔区分较早的贵族与获准购入贵族身份的新家族；此处描述身份准入，不把准入程序等同该社会阶层。",
        ),
        card_writer.source(
            "9", "248", "09_CHP-9_intro.md", "39",
            "the identification of the aristocracy and the State was absolute",
            "哈斯克尔以此概括贵族阶层与国家政治的关系；卡片保留为作者解释，不将社会阶层与政治实体合并。",
        ),
        card_writer.source(
            "9", "249", "09_CHP-9_intro.md", "81",
            "Admission to the nobility now depended purely on wealth.",
            "哈斯克尔将当时贵族身份准入与财富相联系；本条是历史用例，相关准入机制不并入术语对象。",
        ),
        card_writer.source(
            "8", "214", "08_CHP-8_sec_i.md", "123",
            "a family of rich publishers who early in the eighteenth century bought their way into the nobility",
            "第8章以 Baglioni 家族为例，称其在18世纪初进入威尼斯贵族阶层。",
        ),
        card_writer.source(
            "10", "299", "10_CHP-10_intro.md", "362",
            "meetings between the Venetian nobility and English diplomats",
            "第10章将威尼斯贵族作为与英国外交人员会面的社会群体。",
        ),
        card_writer.source(
            "13", "333", "13_CHP-13_intro.md", "18",
            "collections of poems and eulogies brought out to commemorate specific ceremonies involving the nobility",
            "第13章以贵族参与的仪式为纪念性诗集和颂辞的场景。",
        ),
        card_writer.source(
            "15", "362", "15_CHP-15_sec_i.md", "17",
            "a far wider range of culture than was common in the Venetian nobility",
            "第15章以威尼斯贵族作为衡量 Farsetti 文化经历广度的比较群体。",
        ),
        card_writer.source(
            "15", "365", "15_CHP-15_sec_ii.md", "8",
            "The Venetian nobility, he explained, would never come if they were not entertained.",
            "第15章记 Andrea Memmo 对贵族是否到场及娱乐安排的判断。",
        ),
        card_writer.source(
            "15", "366", "15_CHP-15_sec_ii.md", "15",
            "only certain classes of people could present statues in their own names—nobles or important churchmen",
            "第15章将 nobles 列为有资格以本人名义呈献雕像的社会类别之一。",
        ),
    ],
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise AssertionError(f"expected one {label} anchor; found {count}")
    return text.replace(old, new, 1)


def make_card():
    sources = []
    for item in RECORD["sources"]:
        sources.append({
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
    frontmatter = {
        "title": f"{RECORD['title_zh']}（{RECORD['name_en']}）",
        "name_en": RECORD["name_en"],
        "type": KIND,
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#term-venetian-nobility-s4-registration-2026-10-16",
    }
    fm = card_writer.yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    body = f"""## 内容

### 描述

**中文：** {RECORD['description_zh']}

**English:** {RECORD['description_en']}

### 术语范围与边界

**范围：** 本书中的 Venetian nobility 是威尼斯历史语境中的贵族社会阶层。第9章以旧贵族家族、较贫的 patrician 家庭和新近获准进入者说明其内部差异；Haskell 讨论其政治任职和治理影响（第9章，印刷页247）。

**原书用词：** Haskell 使用 nobility、aristocracy、nobles 等表达。patrician 出现在具体家庭和身份语境中，卡片保留它在各段中的实际用法，不主张上述词在所有场合均可互换（第9章，印刷页247–249）。

**章内位置：** 第8章以 Baglioni 家族进入贵族阶层为例；第9章联系政治行政、艺术赞助和绘画；第10章、第13章和第15章分别用于外交交往、仪式出版、文化比较、集市活动和呈献资格。每处用例只说明其所在语境，不推定每名成员均承担这些角色（第8章 p.214；第9章 pp.247–257；第10章 p.299；第13章 p.333；第15章 pp.362、365–366）。

**对象边界：** 贵族阶层是 term；威尼斯共和国或 government 是政治实体/机构层次，家族与个人是不同粒度对象。购入或获准进入贵族身份是历史过程，不等同于贵族阶层这一概念（第9章，印刷页247–249）。

### 本书用例

- 第8章 p.214：Baglioni 家族被称为18世纪初进入贵族阶层的富有出版商家族。
- 第9章 pp.247–249：贵族阶层与国家治理、家族差异、身份准入和财富语境相连；关于“贵族与国家绝对认同”的说法保留为 Haskell 的解释。
- 第9章 pp.252–257：作为画家工作对象及艺术赞助、贵族群体变化和绘画语境中的集体称谓。
- 第10章 p.299、第13章 p.333：分别作为外交会面和仪式纪念出版的社会参与群体。
- 第15章 pp.362、365–366：作为文化比较群体、集市娱乐对象和雕像呈献资格类别。

## 关系与证据

### 关系记录

本批没有建立正式关系。`cand-8108` 对应的28条 S2 断言仍标记为关系候选，涉及22个不同对端；11条断言的对端已有 KU，17条仍待相应候选的 S3/S4 去向明确。每条候选关系仍须在 S6 逐项核对关系类型、方向、语境和证据。

### 身份与外部链接

本卡记录 Haskell 的书内术语用法；本批没有使用外部身份或术语数据库。
"""
    return f"---\n{fm}---\n\n{body}"


def update_process(text: str) -> str:
    entry = """### term：威尼斯贵族阶层跨章术语组 S4 登记（2026-10-16）

- `cand-8108`（S3 组 `sg3-term-cand-8108`）映射至 `units/terms/venetian-nobility-social-estate`。S2 提及账本在第8、9、10、13、15章均将相关表达指向威尼斯贵族社会阶层；第9章 p.247 的核心段落区分旧贵族家族、较贫的 patrician 家庭和新近获准进入者，并将贵族置于政治行政语境。第9章 p.248 的“aristocracy and the State”表述作为 Haskell 的解释保留，不据此将术语与共和国 institution KU 合并。
- 核对术语目录及 manifest，未发现表达同一社会阶层的既有 term KU。贵族身份准入/购入是程序，不并入本 term；家族和个人为不同粒度对象。`cand-10473` 所指第15章另一个未具名社会群体仍为 `undecided`，对齐注释明确不与 `cand-8108` 合并。本卡只登记本书用法，不作外部术语核验。
- `cand-8108` 连接28条直接 S2 关系候选断言、涉及22个不同对端；登记前11条对端已映射、17条仍待 S3/S4。批次不创建正式关系；后续按 S6 逐项裁决。脚本 dry-run 核对原文引文、身份组唯一成员、类型边界、断言数及关系对端计数后通过。
- 首次表格审计发现卡片手写属性表有5行、但无对应 enrichment 行。S5 尚未启动，故移除属性表、保留带逐项来源的术语范围说明；复审以表格审计 errors=[] 为准。
- manifest 从1,182增至1,183；累计登记164组、209条候选映射，余4,672组、4,799条映射。term 类型已登记1组/1条候选，余931组/945条候选。

"""
    text = replace_once(text, "### 登记进度与后续\n", entry + "### 登记进度与后续\n", "S4 term batch insertion")
    text = replace_once(
        text,
        "截至威尼斯共和国跨章身份复核后，4,836 个当前 `new` 身份组中完成163组，余4,673组；5,008条成员候选中映射208条，余4,800条。",
        "截至威尼斯贵族阶层术语组登记后，4,836 个当前 `new` 身份组中完成164组，余4,672组；5,008条成员候选中映射209条，余4,799条。",
        "S4 progress counts",
    )
    text = replace_once(
        text,
        "procedure 已登记23组、24条候选，work、place 各登记1组/1条和2组/2条候选。",
        "procedure 已登记23组、24条候选，term 已登记1组/1条候选，work、place 各登记1组/1条和2组/2条候选。",
        "S4 type progress",
    )
    return text


def update_result(text: str) -> str:
    text = replace_once(
        text,
        "S4 已登记163组、映射208条成员候选；尚待登记4,673组、4,800条映射。",
        "S4 已登记164组、映射209条成员候选；尚待登记4,672组、4,799条映射。",
        "result current S4 counts",
    )
    text = replace_once(
        text,
        "本批新增 Cardinal Pier Donato Cesi 人物组。",
        "此前已登记 Cardinal Pier Donato Cesi 人物组；本批新增 `cand-8108` 威尼斯贵族阶层 term 组。",
        "result latest S4 summary",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,182 KU;", "| [KU 登记](../tables/ku-manifest.csv) | 1,183 KU;", "manifest count") if "| [KU 登记](../tables/ku-manifest.csv) | 1,182 KU;" in text else replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,182 KU；", "| [KU 登记](../tables/ku-manifest.csv) | 1,183 KU；", "manifest count")
    text = replace_once(
        text,
        "以及1个 work、2个 place 组；其余 S4 新组待登记",
        "以及1个 term（威尼斯贵族阶层）、1个 work、2个 place 组；其余 S4 新组待登记",
        "manifest type summary",
    )
    entry = """### term：威尼斯贵族阶层跨章术语组 S4 登记（2026-10-16）

`cand-8108` 已映射至[威尼斯贵族阶层术语卡](../../04-knowledge/units/terms/venetian-nobility-social-estate.md)。第8、9、10、13、15章的书内用例支持其作为威尼斯历史社会阶层的术语组；卡片区分共和国/政府机构、贵族身份准入程序、家族和个人。另一个第15章未具名社会群体候选 `cand-10473` 仍为 `undecided`，未与本组并合。28条直接 S2 关系候选连接22个对端，其中11条对端已有 KU、17条仍待后续 S3/S4；本批没有新增正式关系或外部术语核验。manifest 从1,182增至1,183；累计登记164组、209条候选映射，余4,672组、4,799条。

"""
    return replace_once(
        text,
        "### person：Cardinal Pier Donato Cesi 跨章身份组 S4 登记（2026-10-16）\n",
        entry + "### person：Cardinal Pier Donato Cesi 跨章身份组 S4 登记（2026-10-16）\n",
        "result S4 term batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Venetian nobility term group as one source-backed S4 KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }

    assert len(manifest) == 1182, f"unexpected manifest count: {len(manifest)}"
    assert len(MEMBERS) == 1
    candidate = candidate_by_id[MEMBERS[0]]
    alignment = alignment_by_id[MEMBERS[0]]
    assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    group_rows = [
        row for row in alignments
        if not row.get("external_source") and row.get("decision") == "new"
        and get_group(row["resolution_note"]) == GROUP
    ]
    assert [row["candidate_id"] for row in group_rows] == list(MEMBERS)
    assert not any(row["type"] == KIND and row["ku_id"] == KU_ID for row in manifest)
    assert not any(row["type"] == KIND and row["card_path"] == CARD_PATH for row in manifest)
    card_path = ROOT / CARD_PATH
    assert not card_path.exists(), card_path
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_PATH not in accepted_text

    term_names = ("venetian nobility", "venetian aristocracy", "威尼斯贵族阶层")
    assert not any(
        row["type"] == KIND
        and any(name in (row["canonical_name"] + " " + row["name_en"]).casefold() for name in term_names)
        for row in manifest
    ), "same-scope term KU may already exist"

    statements = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if MEMBERS[0] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                statements.append(statement)
    relation_statements = [
        row for row in statements
        if (row.get("qualifiers") or {}).get("relation_candidate") is True
    ]
    assert len(relation_statements) == 28, len(relation_statements)
    counterparts = Counter()
    for statement in relation_statements:
        other = (
            statement.get("object_candidate_id")
            if statement.get("subject_candidate_id") in MEMBERS
            else statement.get("subject_candidate_id")
        )
        counterparts[bool(alignment_by_id.get(other, {}).get("ku_id"))] += 1
    assert counterparts == Counter({True: 11, False: 17}), counterparts

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        groups[group].append(row)
    registered = {
        group: rows for group, rows in groups.items()
        if any(row.get("ku_id") for row in rows)
    }
    assert (len(new_rows), len(groups)) == (5008, 4836)
    assert (len(registered), sum(map(len, registered.values()))) == (163, 208)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_by_id[MEMBERS[0]]["ku_id"] = KU_ID
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["title_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1183
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row.get("decision") == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {
        group: rows for group, rows in planned_groups.items()
        if any(row.get("ku_id") for row in rows)
    }
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (164, 209)

    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_text = make_card()

    if args.dry_run:
        print(
            "dry-run passed: group=sg3-term-cand-8108 candidates=1 direct_relation_candidates=28 "
            "counterparts=22 mapped_statements=11 pending_statements=17 "
            "registered_groups_after=164 mapped_candidates_after=209 manifest_after=1183"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=sg3-term-cand-8108 candidates=1 direct_relation_candidates=28 "
        "counterparts=22 mapped_statements=11 pending_statements=17 "
        "manifest=1183 registered_groups=164 mapped_candidates=209"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
