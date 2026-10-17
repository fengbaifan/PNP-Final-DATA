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
GROUP = "new-person:francesco-giovan-negroni-9728ee603a"
MEMBER = "cand-1732"
KU_ID = "units/persons/cardinal-giovan-francesco-negroni"
CARD_PATH = "04-knowledge/units/persons/cardinal-giovan-francesco-negroni.md"
RECORD = {
    "name_zh": "乔万·弗朗切斯科·内格罗尼枢机",
    "name_en": "Cardinal Giovan Francesco Negroni",
    "description_zh": (
        "索引以全名列作“Cardinal Giovan Francesco Negroni”。第3章称其为 Monsignor Negroni，记他在1660年代后期取得圣方济各·沙勿略小堂的赞助权，后来成为枢机主教；书中还记其参与小堂祭坛与绘画方案。上述叙述限于 Haskell 对该小堂及其装饰争议的记载。"
    ),
    "description_en": (
        "The index gives the full form “Cardinal Giovan Francesco Negroni.” Chapter 3 refers to him as Monsignor Negroni, says he acquired patronage of the Chapel of St Francis Xavier toward the end of the 1660s, and notes that he was later made a cardinal. The account also describes his role in the chapel's altar and painting plans; these statements remain within Haskell's account of the chapel and its decoration dispute."
    ),
    "context_zh": (
        "N.csv#12“Negroni, Cardinal Giovan Francesco”列出第3章 pp.84–85。p.84 以 Monsignor Negroni 指称取得圣方济各·沙勿略小堂赞助权、后来被擢为枢机的同一人物，并记其委托 Pietro da Cortona 绘制祭坛图稿；p.85 继续称其为 Cardinal，记其选择 Gianandrea Carlone 与 Carlo Maratta，并引录其对小堂权利和装饰安排的主张。正文只用姓氏或称号；全名依据索引规范项，不从同姓推断家族成员关系。"
    ),
    "context_en": (
        "N.csv#12, “Negroni, Cardinal Giovan Francesco,” lists Chapter 3 pp. 84–85. Page 84 refers to the same person as Monsignor Negroni, says he acquired patronage of the Chapel of St Francis Xavier and was later made a cardinal, and records his commission of altar drawings from Pietro da Cortona. Page 85 continues to call him the Cardinal and describes his selection of Gianandrea Carlone and Carlo Maratta, alongside his claims about chapel rights and decoration. The prose uses only the surname or title; the index supplies the full form, and no family membership is inferred from the shared surname."
    ),
    "boundary_zh": (
        "本卡对应唯一候选 `cand-1732`，属于 S3 组 `new-person:francesco-giovan-negroni-9728ee603a`。身份依据为 N.csv#12 的全名，以及第3章 p.84–85 中连续叙述的 Monsignor Negroni／the Cardinal；现有 Negroni family KU 属 family 类型，不与本人物合并，也不据同姓断定家族归属。17条直接 S2 断言端点中15条为关系候选，均留待 S6；本批不新增正式关系、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents the sole candidate `cand-1732` in S3 group `new-person:francesco-giovan-negroni-9728ee603a`. Identity is anchored by the full form in N.csv#12 and the continuous Chapter 3 account on pp. 84–85, which refers to Monsignor Negroni and then the Cardinal. The existing Negroni family KU is a family, not this person; no family membership is inferred from the surname. Fifteen of 17 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": "索引全名为 Cardinal Giovan Francesco Negroni；正文主要作 Monsignor Negroni、Negroni 或 the Cardinal。中文显示名为工作音译。",
    "type_notes_en": "The index gives Cardinal Giovan Francesco Negroni; the prose mainly uses Monsignor Negroni, Negroni, or the Cardinal.",
    "sources": [
        card_writer.source(
            "3", "84", "03_CHP-3_sec_iv.md", "80",
            "the patronage of the chapel was acquired by Monsignor Negroni",
            "第3章记述 Monsignor Negroni 于1660年代后期取得该小堂的赞助权；正文全名以索引规范项补足。",
        ),
        card_writer.source(
            "3", "84", "03_CHP-3_sec_iv.md", "80",
            "who was later made Cardinal",
            "同一句说明 Monsignor Negroni 后来成为枢机，支持与索引 Cardinal Giovan Francesco Negroni 的身份配对。",
        ),
        card_writer.source(
            "3", "84", "03_CHP-3_sec_iv.md", "80",
            "He commissioned drawings for a grandiose altar from Pietro da Cortona just before the artist’s death in 1669",
            "第3章记 Haskell 所述 Negroni 委托 Pietro da Cortona 绘制祭坛图稿；关系裁决留待 S6。",
        ),
        card_writer.source(
            "3", "85", "03_CHP-3_sec_iv.md", "87",
            "he chose instead another Genoese painter, Gianandrea Carlone",
            "第3章称 Negroni 选择 Gianandrea Carlone 绘制小堂；不据此写入正式关系。",
        ),
        card_writer.source(
            "3", "85", "03_CHP-3_sec_iv.md", "87",
            "and the most famous artist of the day, Carlo Maratta",
            "第3章同段称其选择 Carlo Maratta；此项与小堂装饰的关系留待 S6。",
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
        "截至 Prince Eugene of Savoy 批次，4,818 个当前 `new` 身份组中完成155组，余4,663组；4,988条成员候选中映射198条，余4,790条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记49组、85条候选，待登记1,036组、1,093条候选。",
        "截至 Cardinal Giovan Francesco Negroni 批次，4,818 个当前 `new` 身份组中完成156组，余4,662组；4,988条成员候选中映射199条，余4,789条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记50组、86条候选，待登记1,035组、1,092条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Giambattista Marino、Galileo Galilei、Prince Eugene of Savoy 已登记为人物 KU。",
        "Giambattista Marino、Galileo Galilei、Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Giambattista Marino 的16条、Galileo Galilei 的11条与 Prince Eugene of Savoy 的15条关系候选",
        "Giambattista Marino 的16条、Galileo Galilei 的11条、Prince Eugene of Savoy 的15条与 Cardinal Giovan Francesco Negroni 的15条关系候选",
        "process pending relation candidates",
    )
    batch = """### person：Cardinal Giovan Francesco Negroni 人物组登记（2026-10-16）

- `cand-1732`（N.csv#12，“Negroni, Cardinal Giovan Francesco”，pp.84–85）按一个人物组 `new-person:francesco-giovan-negroni-9728ee603a` 登记为 `units/persons/cardinal-giovan-francesco-negroni`。manifest 中只有 Negroni family 的 family KU；没有同名人物 KU。
- 第3章 p.84 将 Monsignor Negroni 与后来的 Cardinal 连续指称，并记其取得小堂赞助权及委托 Pietro da Cortona；p.85 继续称其为 the Cardinal，记其选用 Gianandrea Carlone 和 Carlo Maratta。卡片姓名采用索引全名；正文只用姓氏/称号，未据同姓推断 family membership。
- 本组17条直接 S2 断言端点中15条为关系候选，均留待 S6；本批不新增正式关系、外部身份记录或 S5 补足。[register_s4_person_giovan_francesco_negroni_batch_20261016.py](register_s4_person_giovan_francesco_negroni_batch_20261016.py) dry-run 核对索引决定、5处精确原文引文、端点/关系候选数及登记外键后通过，再 apply 写入卡片、manifest、accepted.yml 与候选映射。manifest 从1,174增至1,175；累计登记156组、199条候选映射，余4,662组、4,789条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "目前完成155组、映射198条成员候选，余4,663组、4,790条映射。",
        "目前完成156组、映射199条成员候选，余4,662组、4,789条映射。",
        "result top S4 counts",
    )
    text = replace_once(
        text,
        "Galileo Galilei、Prince Eugene of Savoy 四十七个补充 person 组",
        "Galileo Galilei、Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni 四十八个补充 person 组",
        "result top person names",
    )
    text = replace_once(
        text,
        "1,174 KU；含本轮新增49个 person 组（",
        "1,175 KU；含本轮新增50个 person 组（",
        "result manifest count",
    )
    text = replace_once(
        text,
        "Giambattista Marino、Galileo Galilei、Prince Eugene of Savoy、2个 Valmarana 组）",
        "Giambattista Marino、Galileo Galilei、Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni、2个 Valmarana 组）",
        "result manifest names",
    )
    text = replace_once(
        text,
        "当前已登记49个 person 组（",
        "当前已登记50个 person 组（",
        "result current person count",
    )
    text = replace_once(
        text,
        "Galileo Galilei、Prince Eugene of Savoy、Valmarana 跨章2组）",
        "Galileo Galilei、Prince Eugene of Savoy、Cardinal Giovan Francesco Negroni、Valmarana 跨章2组）",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,663个 `new` 身份组、4,790条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记49组、85条候选，待登记1,036组、1,093条候选。",
        "当前尚余4,662个 `new` 身份组、4,789条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记50组、86条候选，待登记1,035组、1,092条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Cardinal Giovan Francesco Negroni 人物组登记（2026-10-16）

`cand-1732`（N.csv#12）已登记为[Cardinal Giovan Francesco Negroni 人物卡](../../04-knowledge/units/persons/cardinal-giovan-francesco-negroni.md)。第3章 pp.84–85 连续以 Monsignor Negroni、Negroni 和 the Cardinal 指称，记其小堂赞助、祭坛与绘画方案；全名采用索引规范项。现有 Negroni family KU 保持不同类型，未推断家族成员关系。17条直接 S2 断言端点中15条关系候选留待 S6；本批无正式关系、外部身份记录或 S5 补足。批次脚本核对5处原文引文、S3 决定及映射。manifest 从1,174增至1,175；累计登记156组、199条候选映射，余4,662组、4,789条。

"""
    return replace_once(
        text,
        "### person：萨伏依的欧根亲王跨章身份组登记（2026-10-16）\n\n",
        batch + "### person：萨伏依的欧根亲王跨章身份组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register Cardinal Giovan Francesco Negroni as an S4 person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == MEMBER)
    alignment = next(row for row in alignments if row.get("candidate_id") == MEMBER and not row.get("external_source"))
    assert len(manifest) == 1174, f"unexpected manifest size: {len(manifest)}"
    assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
    assert candidate["index_entry_id"] == "N.csv#12" and candidate["canonical_name"] == "Negroni, Cardinal Giovan Francesco"
    assert alignment["decision"] == "new" and not alignment.get("ku_id") and get_group(alignment["resolution_note"]) == GROUP
    assert not any(row["type"] == KIND and "negroni" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)
    assert not (ROOT / CARD_PATH).exists(), CARD_PATH
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") == MEMBER or statement.get("object_candidate_id") == MEMBER:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert (len(endpoints), len(relation_endpoints)) == (17, 15), (len(endpoints), len(relation_endpoints))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        new_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(new_groups), len(new_rows)) == (4818, 4988)
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (155, 198)
    for group, rows in registered_groups.items():
        assert len(rows) == len(new_groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    registered_person_groups = {
        group: rows for group, rows in registered_groups.items()
        if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    assert (len(registered_person_groups), sum(map(len, registered_person_groups.values()))) == (49, 85)

    planned_alignment = [dict(row) for row in alignments]
    planned_row = next(row for row in planned_alignment if row.get("candidate_id") == MEMBER and not row.get("external_source"))
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
    assert len(planned_manifest) == 1175

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
            "dry-run passed: group=1 candidates=1 endpoints=17 relation_candidates=15 "
            "registered_groups_after=156 mapped_candidates_after=199 manifest_after=1175"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=1 endpoints=17 relation_candidates=15 "
        "manifest=1175 registered_groups=156 mapped_candidates=199"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
