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
GROUP = "new-person:bracciolini-francesco-bracciolini-francesc-7cfa25f9e6"
MEMBERS = ("cand-0440", "cand-0441")
KU_ID = "units/persons/francesco-bracciolini"
CARD_PATH = "04-knowledge/units/persons/francesco-bracciolini.md"
RECORD = {
    "name_zh": "弗朗切斯科·布拉乔利尼",
    "name_en": "Francesco Bracciolini",
    "description_zh": (
        "第2章称 Francesco Bracciolini 为托斯卡纳诗人和 Urban VIII 的宠爱诗人，记其曾任 Maffeo Barberini 的秘书，并受召为 Barberini 家族拟定颂扬方案。书中还提到题为《L’elettione di Urbano VIII》的颂诗及其出版后的荣誉；作者的贬评、修辞和时间限定仍归于 Haskell。"
    ),
    "description_en": (
        "Chapter 2 identifies Francesco Bracciolini as a Tuscan poet and Urban VIII's favoured poet, notes that he had served Maffeo Barberini as secretary, and says he was called on to devise a programme celebrating the Barberini family. It also refers to the eulogistic poem L’elettione di Urbano VIII and honours reported after its publication; Haskell's evaluative wording and qualifications remain attributed."
    ),
    "context_zh": (
        "B.csv#287“Bracciolini, Francesco”列第2章 pp.51–53、57；B.csv#288 是同一人物索引项下以《L’elettione di Urbano VIII》为内容的子目（p.52）。第51章页称他为托斯卡纳诗人，并记其为 Barberini 宫廷拟定装饰方案；p.52 记其早年任 Maffeo Barberini 秘书、离开后致信 Urban VIII，以及题名诗出版后的荣誉；p.57 说明同名颂诗由 Bracciolini 创作，是 Giulio Rospigliosi 评论的对象，不能把评论误作作者作品。索引页码保留为定位线索，不将未逐项阅读的页面扩写为事实。"
    ),
    "context_en": (
        "B.csv#287, “Bracciolini, Francesco,” lists Chapter 2 pp. 51–53 and 57; B.csv#288 is a sub-entry under the same person index entry for L’elettione di Urbano VIII (p. 52). Chapter 2 p. 51 calls him a Tuscan poet and describes his programme for the Barberini court; p. 52 recounts his earlier service as Maffeo Barberini's secretary, his departure and appeal to Urban VIII, and honours reported after publication of the titled poem. Page 57 identifies the eulogistic poem as Bracciolini's and as the subject of Giulio Rospigliosi's commentary; it does not credit the commentary to Bracciolini. Remaining index pages are retained as locators, not expanded into unread claims."
    ),
    "boundary_zh": (
        "本卡对应 `cand-0440` 与 `cand-0441`，同属 S3 人物组 `new-person:bracciolini-francesco-bracciolini-francesc-7cfa25f9e6`，登记为一个人物 KU。`cand-0441` 是人物索引子目，不代表诗作本身；第2章 p.52 的题名和“the poem”提及已改映至独立 archive 候选 `cand-4796`。该诗候选的 S3 状态仍为 `undecided`（版本／粒度待证），不与人物合并。16条直接 S2 断言端点中15条关系候选留待 S6；端点改挂未改变关系候选计数。本批不新增正式关系、作品/archive KU、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents `cand-0440` and `cand-0441` in the same S3 person group `new-person:bracciolini-francesco-bracciolini-francesc-7cfa25f9e6` and maps them to one person KU. `cand-0441` is a person index sub-entry, not the poem itself; the title and the phrase “the poem” on Chapter 2 p. 52 have been reassigned to the separate archive candidate `cand-4796`. That poem candidate remains S3 `undecided` (edition/granularity pending) and is not merged with the person. Fourteen of 15 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, work or archive KUs, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": "索引形式为 Bracciolini, Francesco；正文作 Francesco Bracciolini、Bracciolini，并称其为 Tuscan poet。中文名为工作音译。",
    "type_notes_en": "The index form is Bracciolini, Francesco; the prose uses Francesco Bracciolini and Bracciolini and calls him a Tuscan poet.",
    "sources": [
        card_writer.source(
            "2", "51", "02_CHP-2_sec_iv.md", "93",
            "The Pope’s favourite poet, the Tuscan Francesco Bracciolini, was called in to devise an elaborate programme to the glory of the family",
            "第2章提供人物全名、托斯卡纳诗人称谓及其为 Barberini 家族拟定方案的语境。",
        ),
        card_writer.source(
            "2", "51", "02_CHP-2_sec_iv.md", "94",
            "As a younger man he had served Maffeo Barberini as secretary for a few years",
            "第2章称 Bracciolini 年轻时曾任 Maffeo Barberini 秘书数年；保持 Haskell 的回顾性叙述。",
        ),
        card_writer.source(
            "2", "52", "02_CHP-2_sec_iv.md", "98",
            "after the publication of his sycophantic L’elettione di Urbano VIII",
            "第2章称题名诗出版后 Bracciolini 获得荣誉；保留作者的 sycophantic 评价，不由此扩展为未经核对的出版项。",
        ),
        card_writer.source(
            "2", "57", "02_CHP-2_sec_iv.md", "173–174",
            "the eulogistic L’elettione di\nUrbano VlII by his fellow Pistoian Francesco Bracciolini",
            "第2章 p.57 明确把 L’elettione 归于 Francesco Bracciolini，并称其为颂诗；OCR 将 VIII 识作 VlII，已按视觉核对记录。",
            "OCR title correction: visual reading of print p. 57 confirms Urbano VIII.",
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
        "截至 Cardinal Giovan Francesco Negroni 批次，4,818 个当前 `new` 身份组中完成156组，余4,662组；4,988条成员候选中映射199条，余4,789条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记50组、86条候选，待登记1,035组、1,092条候选。",
        "截至 Francesco Bracciolini 批次，4,818 个当前 `new` 身份组中完成157组，余4,661组；4,988条成员候选中映射201条，余4,787条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记51组、88条候选，待登记1,034组、1,090条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni 已登记为人物 KU。",
        "Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni、Francesco Bracciolini 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Prince Eugene of Savoy 的15条与 Cardinal Giovan Francesco Negroni 的15条关系候选",
        "Prince Eugene of Savoy 的15条、Cardinal Giovan Francesco Negroni 的15条与 Francesco Bracciolini 的15条关系候选",
        "process pending relation candidates",
    )
    batch = """### person：Francesco Bracciolini 双索引候选组登记（2026-10-16）

- `cand-0440`（B.csv#287，主项）与 `cand-0441`（B.csv#288，`L'elettione di Urbano VIII` 子目）属于同一 S3 人物组 `new-person:bracciolini-francesco-bracciolini-francesc-7cfa25f9e6`，共同登记为 `units/persons/francesco-bracciolini`。
- 子目题名和 p.52 的“the poem”经 S2 端点校正已映射至 archive 候选 `cand-4796`；该候选仍为 S3 `undecided`，不把诗作并入人物 KU。第2章 p.57 明确称该颂诗由 Bracciolini 创作；它是 Rospigliosi 评论的对象，不是 Rospigliosi 评论本身或 Bracciolini 所作的评论。
- 人物组16条直接 S2 断言端点中15条为关系候选，留待 S6；本批不新增正式关系、archive KU、外部身份记录或 S5 补足。[register_s4_person_francesco_bracciolini_batch_20261016.py](register_s4_person_francesco_bracciolini_batch_20261016.py) dry-run 核对两条组成员、4处引文、端点数和候选映射后通过，再 apply 更新卡片、manifest、accepted.yml 与两条人物候选映射。端点改挂未改变关系候选计数。manifest 从1,175增至1,176；累计登记157组、201条候选映射，余4,661组、4,787条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "目前完成156组、映射199条成员候选，余4,662组、4,789条映射。",
        "目前完成157组、映射201条成员候选，余4,661组、4,787条映射。",
        "result top S4 counts",
    )
    text = replace_once(
        text,
        "Cardinal Giovan Francesco Negroni 四十八个补充 person 组",
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini 四十九个补充 person 组",
        "result top person names",
    )
    text = replace_once(
        text,
        "1,175 KU；含本轮新增50个 person 组（",
        "1,176 KU；含本轮新增51个 person 组（",
        "result manifest count",
    )
    text = replace_once(
        text,
        "Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni、2个 Valmarana 组）",
        "Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni、Francesco Bracciolini、2个 Valmarana 组）",
        "result manifest names",
    )
    text = replace_once(
        text,
        "当前已登记50个 person 组（",
        "当前已登记51个 person 组（",
        "result current person count",
    )
    text = replace_once(
        text,
        "Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni、Valmarana 跨章2组）",
        "Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni、Francesco Bracciolini、Valmarana 跨章2组）",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,662个 `new` 身份组、4,789条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记50组、86条候选，待登记1,035组、1,092条候选。",
        "当前尚余4,661个 `new` 身份组、4,787条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记51组、88条候选，待登记1,034组、1,090条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Francesco Bracciolini 双索引候选组登记（2026-10-16）

`cand-0440` 与 `cand-0441` 已共同映射至[Francesco Bracciolini 人物卡](../../04-knowledge/units/persons/francesco-bracciolini.md)。`cand-0441` 是该人物索引项下的作品子目，不是作品实体；p.52 的题名及“the poem”现映射至 archive 候选 `cand-4796`，其 S3 状态仍为 `undecided`（版本／粒度待证）。第2章 p.57 将颂诗归于 Bracciolini，并明确它是 Rospigliosi 评论的对象。人物组15条直接 S2 端点中14条关系候选待 S6；本批未新增正式关系、archive KU、外部身份记录或 S5 补足。过程校正和 S4 dry-run/apply 见[端点校正记录](../../03-processing/patrons-and-painters-full-book-s2/process/reconcile_s2_bracciolini_poem_endpoint_20261016.py)及[登记脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_francesco_bracciolini_batch_20261016.py)。manifest 从1,175增至1,176；累计登记157组、201条候选映射，余4,661组、4,787条。

"""
    return replace_once(
        text,
        "### person：Cardinal Giovan Francesco Negroni 人物组登记（2026-10-16）\n\n",
        batch + "### person：Cardinal Giovan Francesco Negroni 人物组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register Francesco Bracciolini's person identity group in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    align_by_id = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    assert len(manifest) == 1175, f"unexpected manifest size: {len(manifest)}"
    assert {align_by_id[cid]["decision"] for cid in MEMBERS} == {"new"}
    assert {get_group(align_by_id[cid]["resolution_note"]) for cid in MEMBERS} == {GROUP}
    for cid in MEMBERS:
        assert candidate_by_id[cid]["suggested_type"] == KIND and candidate_by_id[cid]["status"] == "open", cid
        assert not align_by_id[cid].get("ku_id"), cid
    assert candidate_by_id["cand-0441"]["sub_entry"] == "L'elettione di Urbano VIII"
    assert align_by_id["cand-4796"]["decision"] == "undecided" and not align_by_id["cand-4796"].get("ku_id")
    assert not any(row["type"] == KIND and "bracciolini" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)
    assert not (ROOT / CARD_PATH).exists(), CARD_PATH
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") in MEMBERS or statement.get("object_candidate_id") in MEMBERS:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert (len(endpoints), len(relation_endpoints)) == (16, 15), (len(endpoints), len(relation_endpoints))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        new_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(new_groups), len(new_rows)) == (4818, 4988)
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (156, 199)
    for group, rows in registered_groups.items():
        assert len(rows) == len(new_groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    registered_person_groups = {
        group: rows for group, rows in registered_groups.items()
        if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    assert (len(registered_person_groups), sum(map(len, registered_person_groups.values()))) == (50, 86)

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
    assert len(planned_manifest) == 1176

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
            "dry-run passed: group=1 candidates=2 endpoints=16 relation_candidates=15 "
            "registered_groups_after=157 mapped_candidates_after=201 manifest_after=1176; archive candidate cand-4796 remains undecided"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=2 endpoints=16 relation_candidates=15 "
        "manifest=1176 registered_groups=157 mapped_candidates=201; archive candidate cand-4796 remains undecided"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
