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
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
KIND = "person"
GROUP = "new-person:eugene-of-savoy-c81f37e553"
MEMBERS = ("cand-2384", "cand-2385", "cand-2386")
KU_ID = "units/persons/prince-eugene-of-savoy"
CARD_PATH = "04-knowledge/units/persons/prince-eugene-of-savoy.md"
RECORD = {
    "name_zh": "萨伏依的欧根亲王",
    "name_en": "Prince Eugene of Savoy",
    "description_zh": (
        "第7章以“the great Prince Eugene of Savoy”称其为萨伏依的欧根亲王，并称其赞助意大利画家与雕塑家。第8、10、13及20章另有同名人物的跨章记载；本卡按书内称谓和语境登记，不扩写外部生平。"
    ),
    "description_en": (
        "Chapter 7 names him “the great Prince Eugene of Savoy” and records his patronage of Italian painters and sculptors. Chapters 8, 10, 13, and 20 also refer to this named figure in related contexts. This card follows the book's name and context without adding an external biography."
    ),
    "context_zh": (
        "S.csv#72 主项列第10章 p.311、第13章 p.341 和第20章 p.403；第8章 p.228 另以 Prince Eugene of Savoy 指其与 Crespi 的服务关系。S.csv#73、#74 分别以“意大利艺术家赞助”和“品味”为子目，均指向第7章 p.201。该页称其赞助意大利画家与雕塑家、雇用 Crespi 五年，并将其趣味描述为偏于 sumptuous and heavy；这些说法均按 Haskell 的叙述或评价保留。索引页码用于定位，不把未逐项阅读的条目扩写为新事实。"
    ),
    "context_en": (
        "The main index entry S.csv#72 lists Chapter 10 p. 311, Chapter 13 p. 341, and Chapter 20 p. 403; Chapter 8 p. 228 also names Prince Eugene of Savoy in connection with Crespi's service. S.csv#73 and #74, for patronage of Italian artists and taste, both point to Chapter 7 p. 201. That page records his patronage of Italian painters and sculptors and five years of employment of Crespi, and characterizes his taste as sumptuous and heavy. These statements remain attributed to Haskell; index references are not expanded into claims from unread passages."
    ),
    "boundary_zh": (
        "本卡对应 S3 组 `new-person:eugene-of-savoy-c81f37e553` 的 cand-2384、cand-2385、cand-2386；三条均为 `new`，以一个 KU 登记。S.csv#72–74 的索引锚点由第7章 p.201 的全名和赞助语境、第8章 p.228 的全名，以及第10、13、20章对应叙述支持；不是仅凭姓氏或萨伏依家族归属合并。现有 House of Savoy 是 family 类型，仍与本人物分开。16条直接 S2 断言端点中15条为关系候选，留待 S6；本批不新增正式关系、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents cand-2384, cand-2385, and cand-2386 in the S3 group `new-person:eugene-of-savoy-c81f37e553`; all three have `new` decisions and map to one KU. Their S.csv#72–74 index anchors are supported by the full name and patronage context on Chapter 7 p. 201, the full name on Chapter 8 p. 228, and the corresponding accounts in Chapters 10, 13, and 20. The grouping does not rely on surname similarity or membership in the House of Savoy; the existing House of Savoy KU remains a distinct family. Fifteen of 16 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": "索引形式为 Savoy, Prince Eugene of；正文亦作 Prince Eugene of Savoy、Prince Eugene 与 Eugene。中文名为工作音译。",
    "type_notes_en": "The index form is Savoy, Prince Eugene of; the prose also uses Prince Eugene of Savoy, Prince Eugene, and Eugene.",
    "sources": [
        card_writer.source(
            "7", "201", "07_CHP-7_sec_v.md", "43–44",
            "the great Prince Eugene of\nSavoy",
            "第7章明确称其为 Prince Eugene of Savoy，为三条索引候选提供全名锚点。",
        ),
        card_writer.source(
            "7", "201", "07_CHP-7_sec_v.md", "49–50",
            "He proved this by his magnificent patronage of Italian painters and sculptors.",
            "第7章称其以赞助意大利画家与雕塑家展示其对意大利艺术的支持。",
        ),
        card_writer.source(
            "8", "228", "08_CHP-8_sec_ii.md", "209",
            "from Prince Eugene of Savoy in whose service I now am",
            "Crespi 的转述书信再次使用 Prince Eugene of Savoy 全名；保留为 Haskell 引述的书内语境。",
        ),
        card_writer.source(
            "10", "311", "10_CHP-10_sec_ii.md", "10",
            "in 1715 the Republic appealed to Eugene for help against the Turks he advised them to turn to Schulenburg",
            "第10章记 Haskell 所述 Venice 于1715年向 Eugene 求助及其建议；该关系候选留待 S6。",
        ),
        card_writer.source(
            "13", "341", "13_CHP-13_intro.md", "93",
            "he bought pictures from the heirs of\nPrince Eugene",
            "第13章记 Zanetti 于1736年在维也纳从 Eugene 的继承人处购画；不据此推断继承人身份。",
        ),
        card_writer.source(
            "20", "403", "20_CHP-20Postscript.md", "114",
            "there have been contributions to this aspect of Prince Eugens collecting",
            "第20章提到关于 Prince Eugene 收藏的研究进展；原 OCR 的 Eugens 缺撇号，按上下文识别为所有格，不扩写研究内容。",
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


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def update_process(text):
    text = replace_once(
        text,
        "截至 Galileo Galilei 批次，4,818 个当前 `new` 身份组中完成154组，余4,664组；4,988条成员候选中映射195条，余4,793条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记48组、82条候选，待登记1,037组、1,096条候选。",
        "截至 Prince Eugene of Savoy 批次，4,818 个当前 `new` 身份组中完成155组，余4,663组；4,988条成员候选中映射198条，余4,790条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记49组、85条候选，待登记1,036组、1,093条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Giambattista Marino、Galileo Galilei 已登记为人物 KU。",
        "Giambattista Marino、Galileo Galilei、Prince Eugene of Savoy 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Giambattista Marino 的16条与 Galileo Galilei 的11条关系候选",
        "Giambattista Marino 的16条、Galileo Galilei 的11条与 Prince Eugene of Savoy 的15条关系候选",
        "process pending relation candidates",
    )
    batch = """### person：萨伏依的欧根亲王跨章身份组登记（2026-10-16）

- S3 组 `new-person:eugene-of-savoy-c81f37e553` 包含 `cand-2384`（S.csv#72，pp.311、341、403）、`cand-2385`（S.csv#73，p.201，patronage of Italian artists）和 `cand-2386`（S.csv#74，p.201，taste），登记为一个人物 KU `units/persons/prince-eugene-of-savoy`。已有 House of Savoy 是 family KU，不与人物合并。
- 书内身份锚点包括第7章 p.201 的 Prince Eugene of Savoy 全名及意大利艺术赞助叙述、第8章 p.228 Crespi 引述中的全名、第10章 p.311 的 Eugene、第13章 p.341 Eugene 的继承人，以及第20章 p.403 对其收藏研究的提及。卡片只保留 Haskell 的来源归属和限定，不扩写外部生平；第20章 OCR 的所有格拼写问题在来源注释中说明。
- 本组16条直接 S2 断言端点中15条为关系候选，全部待 S6；未新增正式关系、外部身份记录或 S5 补足。[register_s4_person_eugene_of_savoy_batch_20261016.py](register_s4_person_eugene_of_savoy_batch_20261016.py) dry-run 核对三条 S3 组成员、6处精确引文、端点/关系候选数和登记外键后通过，再 apply 更新卡片、manifest、accepted.yml 与三条候选映射。manifest 从1,173增至1,174；累计登记155组、198条候选映射，余4,663组、4,790条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "目前完成154组、映射195条成员候选，余4,664组、4,793条映射。",
        "目前完成155组、映射198条成员候选，余4,663组、4,790条映射。",
        "result top S4 counts",
    )
    text = replace_once(
        text,
        "Galileo Galilei 四十六个补充 person 组",
        "Galileo Galilei、Prince Eugene of Savoy 四十七个补充 person 组",
        "result top person names",
    )
    text = replace_once(
        text,
        "1,173 KU；含本轮新增48个 person 组（",
        "1,174 KU；含本轮新增49个 person 组（",
        "result manifest count",
    )
    text = replace_once(
        text,
        "Giambattista Marino、Galileo Galilei、2个 Valmarana 组）",
        "Giambattista Marino、Galileo Galilei、Prince Eugene of Savoy、2个 Valmarana 组）",
        "result manifest names",
    )
    text = replace_once(
        text,
        "当前已登记48个 person 组（",
        "当前已登记49个 person 组（",
        "result current person count",
    )
    text = replace_once(
        text,
        "Giambattista Marino、Galileo Galilei、Valmarana 跨章2组）",
        "Giambattista Marino、Galileo Galilei、Prince Eugene of Savoy、Valmarana 跨章2组）",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,664个 `new` 身份组、4,793条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记48组、82条候选，待登记1,037组、1,096条候选。",
        "当前尚余4,663个 `new` 身份组、4,790条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记49组、85条候选，待登记1,036组、1,093条候选。",
        "result current S4 type counts",
    )
    batch = """### person：萨伏依的欧根亲王跨章身份组登记（2026-10-16）

`cand-2384`、`cand-2385`、`cand-2386` 属于 S3 组 `new-person:eugene-of-savoy-c81f37e553`，已共同映射至[萨伏依的欧根亲王人物卡](../../04-knowledge/units/persons/prince-eugene-of-savoy.md)。第7章 p.201 提供全名和意大利艺术赞助语境；第8章 p.228、第10章 p.311、第13章 p.341及第20章 p.403 提供跨章同名锚点。16条直接 S2 断言端点中15条关系候选留待 S6；没有新增正式关系、外部身份记录或 S5 补足。批次脚本核对6处原文引文、S3 组成员及候选映射。manifest 从1,173增至1,174；累计登记155组、198条候选映射，余4,663组、4,790条。

"""
    return replace_once(
        text,
        "### person：Galileo Galilei 跨章身份组登记（2026-10-16）\n\n",
        batch + "### person：Galileo Galilei 跨章身份组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Prince Eugene of Savoy S4 identity group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    align_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    assert len(manifest) == 1173, f"unexpected manifest size: {len(manifest)}"
    assert set(MEMBERS) <= set(candidate_by_id)
    group_rows = [row for row in alignments if not row.get("external_source") and get_group(row["resolution_note"]) == GROUP]
    assert {row["candidate_id"] for row in group_rows} == set(MEMBERS), "S3 group membership changed"
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = align_by_id[cid]
        assert candidate["suggested_type"] == KIND and candidate["status"] == "open", cid
        assert row["decision"] == "new" and not row.get("ku_id"), cid
    assert not any(row["type"] == KIND and "eugen" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)
    assert not (ROOT / CARD_PATH).exists(), CARD_PATH
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") in MEMBERS or statement.get("object_candidate_id") in MEMBERS:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(endpoints) == 16, f"direct endpoints changed: {len(endpoints)}"
    assert len(relation_endpoints) == 15, f"relation-candidate count changed: {len(relation_endpoints)}"

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group, f"new decision lacks group: {row['candidate_id']}"
        new_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(new_groups), len(new_rows)) == (4818, 4988)
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (154, 195)
    for group, rows in registered_groups.items():
        assert len(rows) == len(new_groups[group]) and len({row["ku_id"] for row in rows}) == 1, group

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    })
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if row.get("external_source") or row["decision"] != "new":
            continue
        planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(planned_registered), sum(sum(bool(row.get("ku_id")) for row in rows) for rows in planned_registered.values())) == (155, 198)
    assert len(planned_manifest) == 1174

    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    assert CARD_PATH not in accepted_text
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_PATH}")
    planned_accepted = "\n".join(accepted_lines) + "\n"

    process_text = update_process(PROCESS_PATH.read_text(encoding="utf-8-sig"))
    result_text = update_result(RESULT_PATH.read_text(encoding="utf-8-sig"))
    card_text = card_writer.make_card(RECORD, KIND)
    assert card_text.count("'2026-10-15'") == 2, "unexpected card date template"
    card_text = card_text.replace("'2026-10-15'", "'2026-10-16'")
    assert card_text.startswith("---\n") and "Prince Eugene of Savoy" in card_text

    if args.dry_run:
        print(
            "dry-run passed: group=1 candidates=3 endpoints=16 relation_candidates=15 "
            "registered_groups_after=155 mapped_candidates_after=198 manifest_after=1174"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=3 endpoints=16 relation_candidates=15 "
        "manifest=1174 registered_groups=155 mapped_candidates=198"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
