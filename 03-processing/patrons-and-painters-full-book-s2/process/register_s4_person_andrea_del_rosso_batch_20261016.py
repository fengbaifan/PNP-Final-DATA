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
GROUP = "new-person:andrea-del-rosso-670cf89453"
MEMBER = "cand-2275"
KU_ID = "units/persons/andrea-del-rosso"
CARD_PATH = "04-knowledge/units/persons/andrea-del-rosso.md"
RECORD = {
    "name_zh": "安德烈亚·德尔·罗索",
    "name_en": "Andrea del Rosso",
    "description_zh": (
        "第8章称 Andrea 为德尔·罗索兄弟中的长兄，生于1640年，36岁时获授与稍年轻的 Lorenzo 共同拥有的面粉专卖特许；他后来成为参议员，并任教皇邮政总局局长。Haskell 记其经常将画作借予罗马 S. Salvatore in Lauro 的展览，并称其于1715年去世。第8章另述兄弟的祖父 Andrea：祖父在1642年时已距去世两年，p.212 又记其建造家族礼拜堂；该祖父与本卡长兄是两代同名人物。"
    ),
    "description_en": (
        "Chapter 8 identifies Andrea as the eldest of the del Rosso brothers, born in 1640. At age 36 he received the lucrative flour monopoly shared with the slightly younger Lorenzo; both later became senators, and Andrea served as director-general of the papal postal services. Haskell says Andrea frequently lent pictures to exhibitions at S. Salvatore in Lauro in Rome and reports that he died in 1715. The chapter separately identifies the brothers' grandfather, also named Andrea: in 1642 he was two years from death, and p. 212 continues the account with his family chapel. The grandfather is a different generation and person from this card's subject."
    ),
    "context_zh": (
        "Q-R.csv#203“Rosso, Andrea del”列第8章 pp.210–213、241、403–404。第8章 p.211 明称长兄 Andrea 生于1640年；同页注释记其1715年去世。祖父另在 p.211 被明确称为 their grandfather，并在 p.212 继续以 Andrea 指称建造家族礼拜堂的人。S3 已将祖父候选 cand-2279 从本组分出，分别保留两个同名人物身份。关于 Andrea 与 Lorenzo 的亲属、共同特许、任职及借画信息仍属书中记载，其正式关系端点留待 S6。"
    ),
    "context_en": (
        "Q-R.csv#203, “Rosso, Andrea del,” lists Chapter 8 pp. 210–213, 241, and 403–404. Chapter 8 p. 211 explicitly calls Andrea the eldest brother and dates his birth to 1640; its note reports his death in 1715. Their grandfather is separately introduced as “their grandfather” on p. 211 and is the Andrea who built the family chapel in the continuation on p. 212. S3 separated candidate cand-2279 into a distinct group, preserving two same-named people. The chapter's statements about Andrea's kinship with Lorenzo, shared concession, offices, and picture loans remain source claims; formal relationship endpoints await S6."
    ),
    "boundary_zh": (
        "本卡仅对应 cand-2275，属于 S3 组 `new-person:andrea-del-rosso-670cf89453`。同名祖父 cand-2279 现属独立组 `new-person:andrea-del-rosso-grandfather-2279`；不得将两人合并。S3 拆分依据为长兄生于1640年、记于1715年去世，而祖父在1642年时距去世两年且随后出现家族礼拜堂叙述。13条直接 S2 断言端点中9条为关系候选，均留待 S6。本批不新增正式关系、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents only cand-2275 in S3 group `new-person:andrea-del-rosso-670cf89453`. The same-named grandfather, cand-2279, is in the separate group `new-person:andrea-del-rosso-grandfather-2279`; the two people must not be merged. S3 distinguished the eldest brother, born in 1640 and reported dead in 1715, from the grandfather who was two years from death in 1642 and is then associated with the family chapel. Nine of 13 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": "索引规范形式为 Rosso, Andrea del；正文使用 Andrea、Andrea del Rosso。中文名为工作音译。",
    "type_notes_en": "The index form is Rosso, Andrea del; the prose uses Andrea and Andrea del Rosso.",
    "sources": [
        card_writer.source(
            "8", "211", "08_CHP-8_sec_i.md", "85",
            "Andrea, the eldest of the brothers, who was born in 1640, was at the age of 36 awarded the lucrative flour monopoly",
            "第8章称 Andrea 为兄弟中的长兄，生于1640年，并记其36岁时获授面粉专卖特许。",
        ),
        card_writer.source(
            "8", "211", "08_CHP-8_sec_i.md", "85",
            "Both men later became Senators, and Andrea eventually died in Rome",
            "第8章称 Andrea 与 Lorenzo 后来均成为参议员，并记 Andrea 在罗马去世。",
        ),
        card_writer.source(
            "8", "211", "08_CHP-8_sec_i.md", "86",
            "Salvatore in Lauro, as director-general of the papal postal services",
            "第8章续句记其借画展览语境及教皇邮政总局局长身份；具体正式关系留待 S6。",
        ),
        card_writer.source(
            "8", "211", "08_CHP-8_sec_i.md", "96",
            "Ottavio died in 1714, Andrea in 1715 and Lorenzo in 1719.",
            "第8章注释分别记载 Ottavio、Andrea 和 Lorenzo 的去世年份。",
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
        "截至 Andrea del Rosso 跨代组拆分后、下一 S4 批次前，4,819 个当前 `new` 身份组中完成159组，余4,660组；",
        "截至 Andrea del Rosso 长兄批次，4,819 个当前 `new` 身份组中完成160组，余4,659组；",
        "current S4 group counts",
    )
    text = replace_once(
        text,
        "person 类型1,086组、1,178条候选，已登记53组、90条候选，待登记1,033组、1,088条候选。",
        "person 类型1,086组、1,178条候选，已登记54组、91条候选，待登记1,032组、1,087条候选。",
        "current S4 person group counts",
    )
    batch = """### person：Andrea del Rosso 长兄身份组登记（2026-10-16）

- `cand-2275`（Q-R.csv#203，pp.210–213、241、403–404）登记为 `units/persons/andrea-del-rosso`。第8章 p.211 明称其为长兄并记生于1640年；同页注释记其1715年去世。与其同名的祖父 `cand-2279` 已经 S3 拆分，归入单独的 `new-person:andrea-del-rosso-grandfather-2279`，本卡不予合并。
- 13条直接 S2 断言端点中9条为关系候选，均留待 S6。批次核对组成员、4处原文锚点、端点、S3 拆分决定及外键后 dry-run 通过；apply 升级人物卡并更新 manifest、accepted.yml、候选映射与结果文件。本批不新增正式关系、外部身份记录或 S5 补足。
- manifest 从1,178增至1,179；累计登记160组、204条候选映射，余4,659组、4,784条。person 类型共1,086组、1,178条候选，当前登记54组、91条映射，余1,032组、1,087条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "目前完成159组、映射203条成员候选，余4,660组、4,785条映射。",
        "目前完成160组、映射204条成员候选，余4,659组、4,784条映射。",
        "result current S4 registration counts",
    )
    text = replace_once(text, "1,178 KU；含本轮新增53个 person 组（", "1,179 KU；含本轮新增54个 person 组（", "result manifest count")
    text = replace_once(
        text,
        "Francesco Marucelli、2个 Valmarana 组）",
        "Francesco Marucelli、Andrea del Rosso、2个 Valmarana 组）",
        "result manifest names",
    )
    text = replace_once(text, "当前已登记53个 person 组（", "当前已登记54个 person 组（", "result current person groups")
    text = replace_once(
        text,
        "Francesco Marucelli、Valmarana 跨章2组）",
        "Francesco Marucelli、Andrea del Rosso、Valmarana 跨章2组）",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,660个 `new` 身份组、4,785条成员候选映射；",
        "当前尚余4,659个 `new` 身份组、4,784条成员候选映射；",
        "result current unregistered group count",
    )
    text = replace_once(
        text,
        "person 类型1,086组、1,178条候选，已登记53组、90条候选，待登记1,033组、1,088条候选。",
        "person 类型1,086组、1,178条候选，已登记54组、91条候选，待登记1,032组、1,087条候选。",
        "result current person registration counts",
    )
    batch = """### person：Andrea del Rosso 长兄 S4 登记（2026-10-16）

`cand-2275`（Q-R.csv#203）已登记为[Andrea del Rosso 人物卡](../../04-knowledge/units/persons/andrea-del-rosso.md)。第8章 p.211 称其为德尔·罗索兄弟中的长兄，生于1640年；p.211 注释记其1715年去世。同名祖父 `cand-2279` 已由 S3 归入独立人物组 `new-person:andrea-del-rosso-grandfather-2279`，不映射到本卡。13条直接 S2 端点中9条关系候选均待 S6；本批未新增正式关系、外部身份记录或 S5 补足。批次脚本核对4处原文锚点和候选映射。manifest 从1,178增至1,179；累计登记160组、204条映射，余4,659组、4,784条。

"""
    return replace_once(text, "### person：Francesco Marucelli", batch + "### person：Francesco Marucelli", "result S4 batch insertion")


def main():
    parser = argparse.ArgumentParser(description="Register the source-distinguished eldest-brother Andrea del Rosso in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == MEMBER)
    alignment = next(row for row in alignments if row.get("candidate_id") == MEMBER and not row.get("external_source"))
    assert len(manifest) == 1178, f"unexpected manifest size: {len(manifest)}"
    assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
    assert candidate["index_entry_id"] == "Q-R.csv#203" and candidate["index_page_range"] == "210, 211, 212, 213, 241, 403, 404"
    assert alignment["decision"] == "new" and not alignment.get("ku_id") and get_group(alignment["resolution_note"]) == GROUP
    assert "S3 grouping correction 2026-10-16" in alignment["resolution_note"]
    assert not any(row["type"] == KIND and "andrea del rosso" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)
    assert not (ROOT / CARD_PATH).exists(), CARD_PATH
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)
    grandfather = next(row for row in alignments if row.get("candidate_id") == "cand-2279" and not row.get("external_source"))
    assert grandfather["decision"] == "new" and not grandfather.get("ku_id")
    assert get_group(grandfather["resolution_note"]) == "new-person:andrea-del-rosso-grandfather-2279"

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") == MEMBER or statement.get("object_candidate_id") == MEMBER:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert (len(endpoints), len(relation_endpoints)) == (13, 9), (len(endpoints), len(relation_endpoints))

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
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (159, 203)
    for group, rows in registered_groups.items():
        assert len(rows) == len(groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    registered_person_groups = {
        group: rows for group, rows in registered_groups.items()
        if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    assert (len(registered_person_groups), sum(map(len, registered_person_groups.values()))) == (53, 90)
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
    assert len(planned_manifest) == 1179

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
            "dry-run passed: group=1 candidates=1 endpoints=13 relation_candidates=9 "
            "registered_groups_after=160 mapped_candidates_after=204 manifest_after=1179; separate grandfather group preserved"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=1 endpoints=13 relation_candidates=9 "
        "manifest=1179 registered_groups=160 mapped_candidates=204"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
