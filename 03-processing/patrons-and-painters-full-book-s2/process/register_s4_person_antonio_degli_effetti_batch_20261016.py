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
GROUP = "new-person:antonio-degli-effetti-d279f76c76"
MEMBER = "cand-5974"
KU_ID = "units/persons/antonio-degli-effetti"
CARD_PATH = "04-knowledge/units/persons/antonio-degli-effetti.md"
RECORD = {
    "name_zh": "安东尼奥·德利·埃费蒂",
    "name_en": "Antonio degli Effetti",
    "description_zh": (
        "第6章称 Antonio degli Effetti 为古物研究者和地方史家；原藏画已失，Haskell 说了解其趣味主要依赖他自编的目录，同时指出目录中的部分画作是否实际拥有曾受质疑，但有独立证据表明他以收藏者闻名。外国旅人眼中，他的 Studiolo 似乎只陈列小画、缩微画、宝石和珠宝；Haskell 说明这些陈列对 Antonio 本人意义远超这种观感，并将其描述为文学兴趣浓厚的人：他在画廊入口复制一幅寓意人生的图画，并称其所藏多数作品旨在阐释该寓意的教训。Haskell 提到当时归于 Cebes 的《The Table》，脚注则纠正 Pinax 并非 Cebes 所作、可能出自公元1世纪；他对 Antonio 将财富本身作为题材的判断保留为作者解释。"
    ),
    "description_en": (
        "Chapter 6 identifies Antonio degli Effetti as an antiquarian and local historian. His pictures have disappeared; Haskell says knowledge of his taste depends chiefly on the catalogue he compiled, while noting doubts about whether he actually owned some listed pictures and independent evidence that he was known as a collector. To foreign travellers, his Studiolo might appear to contain little more than small paintings, miniatures, precious stones, and jewels; Haskell says its significance to Antonio was much greater. He describes Antonio as a man of letters: Antonio reproduced an allegorical picture of human life at his gallery entrance, and Haskell says most pictures he did own were intended to illustrate its lessons. The chapter mentions a dialogue called The Table, then attributed to Cebes; its footnote corrects that the Pinax was by another author and probably dates from the first century CE. Haskell's interpretation that Antonio delighted in wealth as a theme in its own right remains attributed to the author."
    ),
    "context_zh": (
        "第4章 p.116 注释提到 Antonio degli Effetti 的手稿收藏目录；第6章 p.156 以全名介绍其古物研究者和地方史家身份，p.157 续述他以自编目录为认识收藏趣味的主要依据，并讨论其文学兴趣与寓意画廊。相同全名、手稿目录语境和第6章人物叙述支持跨章同一性。Haskell 同页脚注纠正 The Table / Pinax 与 Cebes 的作者归属；不把该作品或目录中的具体画题、实际持有状态、被聘艺术家等关系在本批登记为正式 KU 或关系。"
    ),
    "context_en": (
        "A Chapter 4 p. 116 note refers to Antonio degli Effetti's manuscript collection inventory. Chapter 6 p. 156 names him as an antiquarian and local historian, and p. 157 continues with his catalogue as the main basis for understanding his taste and with his literary interests and allegorical gallery. The same full name, manuscript-inventory context, and Chapter 6 account support one identity across chapters. Haskell's footnote corrects the authorship attribution around The Table / Pinax and Cebes. This batch does not register the work, individual catalogue pictures, ownership status, or named artist references as formal KUs or relations."
    ),
    "boundary_zh": (
        "本卡对应唯一候选 `cand-5974`，属于 S3 组 `new-person:antonio-degli-effetti-d279f76c76`。第4章手稿目录注释与第6章 p.156 全名、p.157 收藏和文学语境共同支持本书内身份。15条直接 S2 断言端点中10条为关系候选，均留待 S6；目录中具体画作、作品归属及艺术家关系不据此登记。本批不新增正式关系、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents the sole candidate `cand-5974` in S3 group `new-person:antonio-degli-effetti-d279f76c76`. The Chapter 4 manuscript-inventory note and the full name and collecting and literary context in Chapter 6 pp. 156–157 support the source-local identity. Ten of 15 direct S2 statement endpoints are relation candidates and remain for S6; individual catalogue pictures, ownership, and artist relationships are not registered here. This batch adds no formal relations, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": "正文规范姓名为 Antonio degli Effetti；第4章以手稿收藏目录引用该人，第6章以全名介绍。中文名为工作音译。",
    "type_notes_en": "The prose form is Antonio degli Effetti; Chapter 4 references a manuscript collection inventory associated with him, and Chapter 6 introduces him by full name.",
    "sources": [
        card_writer.source(
            "4", "116", "04_CHP-4_sec_ii.md", "297",
            "MS. inventory of Antonio degli Effetti referred to in note 2, p. 156.",
            "第4章注释引用 Antonio degli Effetti 的手稿收藏目录，并指回第6章相关注释。",
        ),
        card_writer.source(
            "6", "156", "06_CHP-6_sec_iv.md", "5",
            "The strangest of all these collectors was the antiquarian and local historian Antonio degli Effetti.",
            "第6章以全名称其为古物研究者和地方史家。",
        ),
        card_writer.source(
            "6", "157", "06_CHP-6_sec_iv.md", "56",
            "Doubts have even been expressed as to whether he owned, rather than imagined, some of the pictures he mentions, but we have independent evidence that he was known as a collector.",
            "Haskell 区分目录所列画作的实际持有疑问与其以收藏者闻名的独立证据。",
        ),
        card_writer.source(
            "6", "157", "06_CHP-6_sec_iv.md", "56",
            "Studiolo might appear to consist of little more than",
            "第6章记外国旅人对 Antonio 的 Studiolo 陈列规模的观感。",
        ),
        card_writer.source(
            "6", "157", "06_CHP-6_sec_iv.md", "56",
            "For himself its significance was very much greater and of a totally different order.",
            "第6章说明该画廊对 Antonio 本人具有远超外观的意义。",
        ),
        card_writer.source(
            "6", "157", "06_CHP-6_sec_iv.md", "56",
            "He had a version of it reproduced at the entrance of his gallery and most of the pictures he owned were designed to illustrate its lessons.",
            "第6章称其在画廊入口复制寓意图，并说其实际所藏多数画作旨在阐释该图寓意。",
        ),
        card_writer.source(
            "6", "157", "06_CHP-6_sec_iv.md", "58",
            "In fact the Pinax is by a totally different author and probably dates from the first century' A.D.",
            "第6章脚注纠正 Pinax 并非 Cebes 所作，并将年代表述为可能属于公元1世纪。",
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
        "截至 Andrea del Rosso 长兄批次，4,819 个当前 `new` 身份组中完成160组，余4,659组；",
        "截至 Antonio degli Effetti 批次，4,819 个当前 `new` 身份组中完成161组，余4,658组；",
        "current S4 group counts",
    )
    text = replace_once(
        text,
        "person 类型1,086组、1,178条候选，已登记54组、91条候选，待登记1,032组、1,087条候选。",
        "person 类型1,086组、1,178条候选，已登记55组、92条候选，待登记1,031组、1,086条候选。",
        "current S4 person group counts",
    )
    batch = """### person：Antonio degli Effetti 跨章直接端点组登记（2026-10-16）

- `cand-5974`（第4章 p.116 注释及第6章 pp.156–157）登记为 `units/persons/antonio-degli-effetti`。第4章注释引用其手稿收藏目录，第6章以全名介绍其古物研究者和地方史家身份，并讨论其收藏目录与文学兴趣，支持同一书内人物身份。
- 卡片保留“实际是否拥有目录所列部分画作存疑”和 Pinax 作者归属校正；Haskell 对其趣味和财富主题的解释均注明为作者判断。15条直接 S2 端点中10条为关系候选，均留待 S6；本批不新增作品 KU、正式关系、外部身份记录或 S5 补足。
- 未登记旧稿已按现行双语结构升级，保留来源支持的内容并校正“实际拥有”及 Cebes/Pinax 限定。脚本 dry-run 核对旧稿、7处原文、组成员、端点和外键后通过。manifest 从1,179增至1,180；累计登记161组、205条候选映射，余4,658组、4,783条。person 类型已登记55组、92条候选映射，余1,031组、1,086条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "目前完成160组、映射204条成员候选，余4,659组、4,784条映射。",
        "目前完成161组、映射205条成员候选，余4,658组、4,783条映射。",
        "result current S4 registration counts",
    )
    text = replace_once(text, "1,179 KU；含本轮新增54个 person 组（", "1,180 KU；含本轮新增55个 person 组（", "result manifest count")
    text = replace_once(
        text,
        "Andrea del Rosso、2个 Valmarana 组）",
        "Andrea del Rosso、Antonio degli Effetti、2个 Valmarana 组）",
        "result manifest names",
    )
    text = replace_once(text, "当前已登记54个 person 组（", "当前已登记55个 person 组（", "result current person groups")
    text = replace_once(
        text,
        "Andrea del Rosso、Valmarana 跨章2组）",
        "Andrea del Rosso、Antonio degli Effetti、Valmarana 跨章2组）",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,659个 `new` 身份组、4,784条成员候选映射；",
        "当前尚余4,658个 `new` 身份组、4,783条成员候选映射；",
        "result current unregistered group count",
    )
    text = replace_once(
        text,
        "person 类型1,086组、1,178条候选，已登记54组、91条候选，待登记1,032组、1,087条候选。",
        "person 类型1,086组、1,178条候选，已登记55组、92条候选，待登记1,031组、1,086条候选。",
        "result current person registration counts",
    )
    batch = """### person：Antonio degli Effetti 跨章 S4 登记（2026-10-16）

`cand-5974` 已登记为[Antonio degli Effetti 人物卡](../../04-knowledge/units/persons/antonio-degli-effetti.md)。第4章 p.116 注释引用其手稿收藏目录；第6章 pp.156–157 以全名介绍其古物研究者和地方史家身份，并讨论其自编目录及文学兴趣。卡片保留 Haskell 对部分目录画作实际持有情况的疑问，并按脚注纠正 Pinax 与 Cebes 的作者归属。15条直接 S2 端点中10条关系候选留待 S6；未新增正式关系、work/archive KU、外部身份记录或 S5 补足。旧稿已原位升级并保留来源支持内容。manifest 从1,179增至1,180；累计登记161组、205条映射，余4,658组、4,783条。

"""
    return replace_once(text, "### person：Andrea del Rosso 长兄 S4 登记", batch + "### person：Andrea del Rosso 长兄 S4 登记", "result S4 batch insertion")


def main():
    parser = argparse.ArgumentParser(description="Register Antonio degli Effetti's source-local identity in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == MEMBER)
    alignment = next(row for row in alignments if row.get("candidate_id") == MEMBER and not row.get("external_source"))
    assert len(manifest) == 1179, f"unexpected manifest size: {len(manifest)}"
    assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
    assert candidate["candidate_source_ref"] == "chp-4:04_CHP-4_sec_ii:l232-308#L297"
    assert alignment["decision"] == "new" and not alignment.get("ku_id") and get_group(alignment["resolution_note"]) == GROUP
    legacy_path = ROOT / CARD_PATH
    legacy_card = legacy_path.read_text(encoding="utf-8-sig") if legacy_path.exists() else None
    if legacy_card is not None:
        assert (
            "title: 安东尼奥·德利·埃费蒂（Antonio degli Effetti）" in legacy_card
            and "Haskell, Patrons and Painters" in legacy_card
            and "《人生图》" in legacy_card
            and "第一、六章限定测试" in legacy_card
        ), "existing card is not the expected unaccepted legacy draft"
    assert not any(row["type"] == KIND and "antonio degli effetti" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") == MEMBER or statement.get("object_candidate_id") == MEMBER:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert (len(endpoints), len(relation_endpoints)) == (15, 10), (len(endpoints), len(relation_endpoints))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    registered = defaultdict(list)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(new_rows), len(groups)) == (4988, 4819)
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (160, 204)
    for group, rows in registered_groups.items():
        assert len(rows) == len(groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    registered_person_groups = {
        group: rows for group, rows in registered_groups.items()
        if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    assert (len(registered_person_groups), sum(map(len, registered_person_groups.values()))) == (54, 91)
    assert len(groups[GROUP]) == 1

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_row = planned_by_id[MEMBER]
    planned_row["ku_id"] = KU_ID
    planned_row["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1180

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

    if args.dry_run:
        print(
            "dry-run passed: group=1 candidates=1 legacy_card="
            f"{'upgradeable' if legacy_card is not None else 'none'} endpoints=15 relation_candidates=10 "
            "registered_groups_after=161 mapped_candidates_after=205 manifest_after=1180"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=1 endpoints=15 relation_candidates=10 "
        "manifest=1180 registered_groups=161 mapped_candidates=205"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
