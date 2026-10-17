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
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
KIND = "person"
GROUP = "new-person:cesi-donato-pier-f179444158"
MEMBERS = ("cand-0640",)
KU_ID = "units/persons/cardinal-pier-donato-cesi"
CARD_PATH = "04-knowledge/units/persons/cardinal-pier-donato-cesi.md"

RECORD = {
    "name_zh": "皮耶·多纳托·切西枢机",
    "name_en": "Cardinal Pier Donato Cesi",
    "description_zh": (
        "第3章以全名称他为 Pier Donato Cesi 枢机，并记其同意出资完成 Chiesa Nuova；他要求取得与 Farnese "
        "在 Gesù 相同的权利，其本人和家族也获 Oratorian Congregation 事务中的优先权。Haskell 还说其在教堂建造中的实际干预有限。"
        "第20章后记以转引的1581年信件说明其自我克制；引文经 Haskell 转述，脚注指向 Bonadonna Russo 1968 年第135页，"
        "本批未核读原信。第3章将其与兄弟 Angelo Cesi 区分，并称 Pier Donato 于1586年去世后，Angelo 延续家族赞助。"
        "以上均为本书陈述；外部身份与事实未在本批核验。"
    ),
    "description_en": (
        "Chapter 3 names him Cardinal Pier Donato Cesi and says he agreed to fund completion of Chiesa Nuova; he sought rights at the church "
        "comparable to those Farnese held at the Gesù, and his terms provided privileges for him and his family in Oratorian Congregation affairs. "
        "Haskell also says Cesi had little involvement in the church's building. The Chapter 20 postscript uses a 1581 letter, quoted second-hand by "
        "Haskell, to illustrate Cesi's self-restraint; its footnote cites Bonadonna Russo (1968, p. 135), whose original letter was not checked in this batch. "
        "Chapter 3 distinguishes Cesi from his brother Angelo, saying Angelo continued family patronage after Pier Donato's death in 1586. "
        "These are reports in the book; external identity and facts were not verified in this batch."
    ),
    "context_zh": (
        "C.csv#164 的索引主项为“Cesi, Cardinal Pier Donato”，列第3章 pp.69–70。第3章 p.69 明列全名；第20章后记 p.400 "
        "以“Cardinal Cesi”简称，并回顾同一 Oratorian Chiesa Nuova 的赞助与建造语境。全名锚点及相互衔接的书内语境支持该候选跨章节指向同一人物。"
    ),
    "context_en": (
        "The main index entry C.csv#164 is “Cesi, Cardinal Pier Donato,” with pages 69–70 in Chapter 3. Chapter 3 p. 69 gives his full name; "
        "the Chapter 20 postscript p. 400 shortens it to “Cardinal Cesi” while revisiting the patronage and building history of the same Oratorian "
        "Chiesa Nuova. The full-name anchor and connected source context support the cross-chapter identification."
    ),
    "boundary_zh": (
        "本卡对应 S3 组 `new-person:cesi-donato-pier-f179444158`，成员只有 `cand-0640`。书内另称其兄弟 Angelo Cesi 延续家族赞助；"
        "Angelo 与本卡人物是不同身份，Cesi 家族 KU 和 Cardinal Alessandro Farnese 人物 KU 也不与本卡合并。11 条直接 S2 断言均标为关系候选；"
        "其中8条的对端已映射至 Farnese 枢机或 Oratorians 机构 KU，另3条的 Chiesa Nuova 对端 `cand-0710` 尚未登记。本批不建立正式关系，"
        "待端点完成后按 S6 审查。中文名为工作音译；未查外部身份来源。"
    ),
    "boundary_en": (
        "This card maps the singleton S3 group `new-person:cesi-donato-pier-f179444158`, containing only `cand-0640`. The book separately names "
        "his brother Angelo Cesi as continuing the family's patronage; Angelo is a distinct identity. The Cesi family KU and Cardinal Alessandro Farnese KU "
        "are also kept separate. All 11 direct S2 statements are marked as relation candidates: eight counterpart endpoints map to the Farnese cardinal or "
        "the Oratorians institution KU, while the three Chiesa Nuova counterparts (`cand-0710`) remain unregistered. This batch creates no formal relation; "
        "the statements remain for S6 after the endpoint is registered. The Chinese display name is a working transliteration; no external identity source was consulted."
    ),
    "type_notes_zh": (
        "索引规范形式为 Cesi, Cardinal Pier Donato；正文称 Cardinal Pier Donato Cesi、Cardinal Cesi。中文显示名为便于识别的工作音译。"
    ),
    "type_notes_en": (
        "The index form is Cesi, Cardinal Pier Donato; the prose uses Cardinal Pier Donato Cesi and Cardinal Cesi. The Chinese display name is a working transliteration."
    ),
    "sources": [
        card_writer.source(
            "3", "69", "03_CHP-3_sec_ii.md", "42–43",
            "Cardinal Pier Donato Cesi was obviously very much under the influence of Cardinal\nFarnese.",
            "第3章以全名指认人物，并将其受 Cardinal Farnese 影响表述为 Haskell 的判断。",
        ),
        card_writer.source(
            "3", "69", "03_CHP-3_sec_ii.md", "43",
            "When, therefore, he agreed to pay for the completion of the Chiesa Nuova, he went out of his way to insist that he should enjoy the same rights as those of Farnese in the Gesù.",
            "第3章记其同意资助 Chiesa Nuova 竣工，并要求享有与 Farnese 在 Gesù 相同的权利。",
        ),
        card_writer.source(
            "3", "69", "03_CHP-3_sec_ii.md", "43",
            "His arms too were to be set up in the church, and he and his family were to enjoy overriding privileges in the affairs of the Congregation.",
            "第3章称其与家族在 Oratorian Congregation 事务中享有优先权。",
        ),
        card_writer.source(
            "3", "69", "03_CHP-3_sec_ii.md", "43–44",
            "His terms were accepted, but he interfered little enough in the building of the church and some years after his death in 1586, his brother Angelo\nCesi, Bishop of Todi, continued the family patronage.",
            "第3章称其条款获接受、其实际干预建造有限，并将兄弟 Angelo Cesi 的后续家族赞助与 Pier Donato 区分。",
        ),
        card_writer.source(
            "20", "400", "20_CHP-20Postscript.md", "51",
            "This control was in fact a consequence of the deliberate (and exceptional) policy of self-restraint exercised by the patron Cardinal Cesi which contrasts strikingly with Cardinal Farnese’s treatment of the Jesuits. ‘There is no need to send me copies of the plans so that a design that appeals to my taste can be chosen’, he wrote to a leading Oratorian in 1581, ‘because my taste will be whatever satisfies you and the other Fathers.’6",
            "后记将 Oratorian 的建造控制部分归因于 Cardinal Cesi 的自我克制，并转引其1581年致 Oratorian 的信；此处为 Haskell 的解释和二手引文。",
            "注6引 Bonadonna Russo, 1968, p. 135；原信未在本批独立查阅",
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
        "截至 Simon Vouet 批次，4,819 个当前 `new` 身份组中完成162组，余4,657组；4,988条成员候选中映射203条，余4,785条。",
        "截至 Cardinal Pier Donato Cesi 批次，4,844 个当前 `new` 身份组中完成163组，余4,681组；5,016条成员候选中映射208条，余4,808条。",
        "current S4 group and candidate counts",
    )
    text = replace_once(
        text,
        "person 类型1,086组、1,178条候选，已登记56组、94条候选，待登记1,030组、1,084条候选。",
        "person 类型1,086组、1,178条候选，已登记57组、95条候选，待登记1,029组、1,083条候选。",
        "current S4 person counts",
    )
    text = replace_once(
        text,
        "Francesco Marucelli 已登记为人物 KU。",
        "Francesco Marucelli、Andrea del Rosso、Antonio degli Effetti、Simon Vouet、Cardinal Pier Donato Cesi 已登记为人物 KU。",
        "current S4 person names",
    )
    batch = """### person：Cardinal Pier Donato Cesi 单候选跨章组登记（2026-10-16）

- `cand-0640`（C.csv#164，索引主项 “Cesi, Cardinal Pier Donato”）对应 S3 组 `new-person:cesi-donato-pier-f179444158`，登记为 `units/persons/cardinal-pier-donato-cesi`。第3章 p.69 给出全名和 Chiesa Nuova 赞助语境；第20章后记 p.400 以 “Cardinal Cesi” 回顾同一人物的自我克制与1581年信件。卡片将该信标为 Haskell 的二手引文，脚注所引原文未在本批核读。
- 11条直接 S2 断言全部带 `relation_candidate`；其中8条对端已映射到 Cardinal Alessandro Farnese 或 Oratorians KU，3条对端为尚未登记的 Chiesa Nuova 候选 `cand-0710`。关系候选不写入正式关系表，留待端点登记后 S6 审查；本批不做外部身份核验或 S5 补足。书内将其兄弟 Angelo Cesi 与 Pier Donato 区分，未合并 Cesi 家族卡或 Farnese 枢机卡。
- 批次脚本 dry-run 核对单成员身份组、5处精确引文、11条断言、8个已映射/3个待登记对端及现有外键后通过。manifest 从1,181增至1,182；累计登记163组、208条候选映射，余4,681组、4,808条。person 类型已登记57组、95条候选映射，余1,029组、1,083条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "S4 已登记162组、映射207条成员候选；尚待登记4,682组、4,809条映射。",
        "S4 已登记163组、映射208条成员候选；尚待登记4,681组、4,808条映射。本批新增 Cardinal Pier Donato Cesi 人物组。",
        "result current S4 counts",
    )
    text = replace_once(
        text,
        "Francesco Marucelli 五十一个补充 person 组",
        "Francesco Marucelli、Cardinal Pier Donato Cesi 五十二个补充 person 组",
        "result current S4 person summary",
    )
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,181 KU；含本轮新增56个 person 组（",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,182 KU；含本轮新增57个 person 组（",
        "result manifest count",
    )
    text = replace_once(
        text,
        "Simon Vouet、2个 Valmarana 组",
        "Simon Vouet、Cardinal Pier Donato Cesi、2个 Valmarana 组",
        "result manifest person names",
    )
    batch = """### person：Cardinal Pier Donato Cesi 跨章身份组 S4 登记（2026-10-16）

`cand-0640`（C.csv#164）已登记为[Cardinal Pier Donato Cesi 人物卡](../../04-knowledge/units/persons/cardinal-pier-donato-cesi.md)。第3章 p.69 给出全名及 Chiesa Nuova 赞助、权利和家族优先权语境；第20章后记 p.400 以 Haskell 转引的1581年信件说明其自我克制，并保留原信未核读的限制。书内明确区分其兄弟 Angelo Cesi。11条直接 S2 断言均为关系候选，8条对端已有 Farnese 枢机或 Oratorians KU，3条对端 `cand-0710`（Chiesa Nuova）仍待登记；本批不新增正式关系、外部身份核验或 S5 补足。manifest 从1,181增至1,182；累计登记163组、208条候选映射，余4,681组、4,808条。

"""
    return replace_once(
        text,
        "### person：Simon Vouet 双候选 S4 登记（2026-10-16）",
        batch + "### person：Simon Vouet 双候选 S4 登记（2026-10-16）",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Pier Donato Cesi S3 person group as one source-backed KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }

    assert len(manifest) == 1181, f"unexpected manifest size: {len(manifest)}"
    assert len(MEMBERS) == 1
    for candidate_id in MEMBERS:
        candidate = candidate_by_id[candidate_id]
        alignment = alignment_by_id[candidate_id]
        assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
        assert candidate["index_entry_id"] == "C.csv#164"
        assert candidate["canonical_name"] == "Cesi, Cardinal Pier Donato"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == GROUP
    assert not any(
        row["type"] == KIND
        and (row["canonical_name"] + " " + row["name_en"]).casefold().find("pier donato cesi") >= 0
        for row in manifest
    ), "matching person KU already exists"
    assert not (ROOT / CARD_PATH).exists(), CARD_PATH
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") in MEMBERS or statement.get("object_candidate_id") in MEMBERS:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert (len(endpoints), len(relation_endpoints)) == (11, 11), (len(endpoints), len(relation_endpoints))
    mapped_counterparts = Counter()
    pending_counterparts = Counter()
    for statement in relation_endpoints:
        other = (
            statement.get("object_candidate_id")
            if statement.get("subject_candidate_id") in MEMBERS
            else statement.get("subject_candidate_id")
        )
        counterpart = alignment_by_id.get(other, {})
        if counterpart.get("ku_id"):
            mapped_counterparts[other] += 1
        else:
            pending_counterparts[other] += 1
    assert sum(mapped_counterparts.values()) == 8, dict(mapped_counterparts)
    assert pending_counterparts == Counter({"cand-0710": 3}), dict(pending_counterparts)

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    new_rows = [row for row in alignments if not row.get("external_source") and row["decision"] == "new"]
    groups = defaultdict(list)
    registered = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(new_rows), len(groups)) == (5016, 4844)
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (162, 207)
    for group, rows in registered_groups.items():
        assert len(rows) == len(groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    assert len(groups[GROUP]) == 1
    person_groups = {
        group: rows for group, rows in groups.items()
        if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    mapped_person_groups = {group: rows for group, rows in registered_groups.items() if group in person_groups}
    assert (sum(map(len, person_groups.values())), len(person_groups)) == (1178, 1086)
    assert (sum(map(len, mapped_person_groups.values())), len(mapped_person_groups)) == (94, 56)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for candidate_id in MEMBERS:
        planned_by_id[candidate_id]["ku_id"] = KU_ID
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest) + [{
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": CARD_PATH,
    }]
    assert len(planned_manifest) == 1182

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
            "dry-run passed: group=1 candidates=1 endpoints=11 relation_candidates=11 "
            "counterparts_mapped=8 pending=3 pending_candidate=cand-0710 "
            "registered_groups_after=163 mapped_candidates_after=208 manifest_after=1182"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=1 endpoints=11 relation_candidates=11 "
        "counterparts_mapped=8 pending=3 pending_candidate=cand-0710 "
        "manifest=1182 registered_groups=163 mapped_candidates=208"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
