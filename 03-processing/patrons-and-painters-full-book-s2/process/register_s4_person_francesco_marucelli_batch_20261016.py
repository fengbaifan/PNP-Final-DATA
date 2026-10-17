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
GROUP = "new-person:francesco-marucelli-7aa23816fc"
MEMBER = "cand-1554"
KU_ID = "units/persons/francesco-marucelli"
CARD_PATH = "04-knowledge/units/persons/francesco-marucelli.md"
RECORD = {
    "name_zh": "弗朗切斯科·马鲁切利",
    "name_en": "Francesco Marucelli",
    "description_zh": (
        "第6章称 Francesco Marucelli 为佛罗伦萨赞助人和收藏家，记其居于西班牙广场、以藏书为主要兴趣，并将大量藏书记录于一部学术著作；他关注当代艺术，撰写部分画家生平，向 Filippo Baldinucci 提供在罗马工作的艺术家资料，为藏书中伟大作家的作品委托制作多种材质的胸像，并喜爱 Theodor Helmbrecker 的作品；Helmbrecker 为其绘制十六幅画，包括乡村生活场景和带有寓意暗示的作品。Haskell 对其赞助趣味的评价属于作者判断。第8章称 Marucelli 兄弟中最有声望的 Francesco 于1703年在罗马去世。"
    ),
    "description_en": (
        "Chapter 6 identifies Francesco Marucelli as a Florentine patron and collector who lived in the Piazza di Spagna. It says books were his chief passion and that he recorded his substantial library in a learned work; it also notes his interest in contemporary art, his accounts of some painters' lives, information he sent Filippo Baldinucci about artists working in Rome, busts he commissioned of writers represented in his library, and his delight in Theodor Helmbrecker's work. Helmbrecker painted sixteen pictures for him, including scenes of country life and works with a hint of allegory. Haskell's assessment of Marucelli's patronage and taste is attributed to the author. Chapter 8 says that Francesco, the most distinguished of the Marucelli brothers, died in Rome in 1703."
    ),
    "context_zh": (
        "M.csv#93“Marucelli, Francesco”列第6章 pp.157–158及第8章 p.235。第6章 p.157 首次以全名介绍其佛罗伦萨籍赞助人与收藏家身份；p.158 记其居西班牙广场、热衷藏书、撰写画家生平及与 Baldinucci 的通信，并叙其赞助 Helmbrecker。第8章 p.235 在 Ricci 与 Grand Prince Ferdinand 的叙事中提及 Marucelli 兄弟，称最有声望的 Francesco 于1703年在罗马去世；姓氏、已知领域和索引页码相合。对其赞助质量和品味的评价保留为 Haskell 的判断。"
    ),
    "context_en": (
        "M.csv#93, “Marucelli, Francesco,” lists Chapter 6 pp. 157–158 and Chapter 8 p. 235. Chapter 6 p. 157 introduces him by full name as a Florentine patron and collector; p. 158 describes his residence in the Piazza di Spagna, passion for books, writing on painters, correspondence with Baldinucci, and patronage of Helmbrecker. Chapter 8 p. 235 mentions the Marucelli brothers while discussing Ricci and Grand Prince Ferdinand, saying that Francesco, the most distinguished, died in Rome in 1703. The surname, known context, and index locator support the cross-chapter identity. Haskell's assessment of his patronage and taste remains attributed."
    ),
    "boundary_zh": (
        "本卡对应唯一候选 `cand-1554`，属于 S3 组 `new-person:francesco-marucelli-7aa23816fc`。第6章 p.157 的全名与第8章 p.235 的 Marucelli 兄弟语境、Francesco 名称及索引页码共同支持同一人物；不据此扩建完整家族成员表。manifest 中无同名人物 KU。16条直接 S2 断言端点中11条为关系候选，留待 S6；本批不新增正式关系、作品/archive KU、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents the sole candidate `cand-1554` in S3 group `new-person:francesco-marucelli-7aa23816fc`. The full name in Chapter 6 p. 157 and the Marucelli brothers, the name Francesco, and matching index locator in Chapter 8 p. 235 support one person across the chapters; no complete family membership list is inferred. No same-name person KU exists in the manifest. Eleven of 16 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, work or archive KUs, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": "索引规范形式为 Marucelli, Francesco；正文以 Francesco Marucelli、Marucelli 及 Francesco 指称。中文名为工作音译。",
    "type_notes_en": "The index form is Marucelli, Francesco; the prose uses Francesco Marucelli, Marucelli, and Francesco.",
    "sources": [
        card_writer.source(
            "6", "157", "06_CHP-6_sec_iv.md", "9",
            "Another interesting patron and collector was the Florentine Francesco Marucelli,",
            "第6章以全名介绍 Francesco Marucelli，并称其为佛罗伦萨赞助人与收藏家。",
        ),
        card_writer.source(
            "6", "158", "06_CHP-6_sec_iv.md", "13",
            "who lived in the piazza di Spagna.1 Books were his real passion and he amassed a considerable library which he recorded in a work of a great scholarly erudition.",
            "第6章记其居所、藏书兴趣及著录藏书的学术著作；出版身份和题名不由此猜定。",
        ),
        card_writer.source(
            "6", "158", "06_CHP-6_sec_iv.md", "13",
            "He wrote the lives of some of the principal painters, many of whom were his friends, and he sent details about artists working in Rome to Filippo Baldinucci",
            "第6章记其撰写部分画家生平并向 Baldinucci 提供在罗马工作的艺术家资料；具体关系留待 S6。",
        ),
        card_writer.source(
            "8", "235", "08_CHP-8_sec_ii.md", "296–297",
            "of whom Francesco, the most distinguished, had died in Rome in\n1703",
            "第8章称 Marucelli 兄弟中 Francesco 最有声望，并记其1703年在罗马去世；与第6章全名及索引页码互证。",
        ),
        card_writer.source(
            "6", "158", "06_CHP-6_sec_iv.md", "15",
            "he commissioned busts in stucco, wood, marble and paint of the great writers whose works",
            "第6章记其为藏书中伟大作家的作品委托制作灰泥、木、石、绘画等材质的胸像。",
        ),
        card_writer.source(
            "6", "158", "06_CHP-6_sec_iv.md", "15",
            "he delighted in the bambocciate of the Flemish painter Theodor Helmbrecker whose most enthusiastic admirer he was and who painted sixteen pictures for him",
            "第6章称其喜爱 Helmbrecker 的风俗画，Helmbrecker 为其绘制十六幅作品；乡村生活与寓意场景的细节据同句后文。",
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
        "截至 Carlo de' Rossi 批次，4,818 个当前 `new` 身份组中完成158组，余4,660组；4,988条成员候选中映射202条，余4,786条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记52组、89条候选，待登记1,033组、1,089条候选。",
        "截至 Francesco Marucelli 批次，4,818 个当前 `new` 身份组中完成159组，余4,659组；4,988条成员候选中映射203条，余4,785条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记53组、90条候选，待登记1,032组、1,088条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Francesco Bracciolini、Carlo de' Rossi 已登记为人物 KU。",
        "Francesco Bracciolini、Carlo de' Rossi、Francesco Marucelli 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Francesco Bracciolini 的15条与 Carlo de' Rossi 的14条关系候选",
        "Francesco Bracciolini 的15条、Carlo de' Rossi 的14条与 Francesco Marucelli 的11条关系候选",
        "process pending relation candidates",
    )
    batch = """### person：Francesco Marucelli 跨章直接端点组登记（2026-10-16）

- `cand-1554`（M.csv#93，pp.157、158、235）登记为 `units/persons/francesco-marucelli`。第6章 p.157 以全名介绍其赞助人和收藏家身份；第8章 p.235 的 Marucelli 兄弟语境称 Francesco 于1703年在罗马去世，支持其与索引人物同一。
- 第6章 p.158 记其藏书、画家生平写作和向 Baldinucci 提供资料；这些有关人物、收藏、著作和委托的正式端点均留待 S6，卡片不把作者评价转为无条件事实。
- 16条直接 S2 断言端点中11条为关系候选；本批不新增正式关系、archive/work KU、外部身份记录或 S5 补足。[register_s4_person_francesco_marucelli_batch_20261016.py](register_s4_person_francesco_marucelli_batch_20261016.py) dry-run 核对唯一组成员、6处精确引文、端点和外键后通过，再 apply 更新卡片、manifest、accepted.yml 与候选映射。manifest 从1,177增至1,178；累计登记159组、203条候选映射，余4,659组、4,785条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "目前完成158组、映射202条成员候选，余4,660组、4,786条映射。",
        "目前完成159组、映射203条成员候选，余4,659组、4,785条映射。",
        "result top S4 counts",
    )
    text = replace_once(
        text,
        "Francesco Bracciolini、Carlo de' Rossi 五十个补充 person 组",
        "Francesco Bracciolini、Carlo de' Rossi、Francesco Marucelli 五十一个补充 person 组",
        "result top person names",
    )
    text = replace_once(text, "1,177 KU；含本轮新增52个 person 组（", "1,178 KU；含本轮新增53个 person 组（", "result manifest count")
    text = replace_once(
        text,
        "Francesco Bracciolini、Carlo de' Rossi、2个 Valmarana 组）",
        "Francesco Bracciolini、Carlo de' Rossi、Francesco Marucelli、2个 Valmarana 组）",
        "result manifest names",
    )
    text = replace_once(text, "当前已登记52个 person 组（", "当前已登记53个 person 组（", "result current person count")
    text = replace_once(
        text,
        "Francesco Bracciolini、Carlo de' Rossi、Valmarana 跨章2组）",
        "Francesco Bracciolini、Carlo de' Rossi、Francesco Marucelli、Valmarana 跨章2组）",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,660个 `new` 身份组、4,786条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记52组、89条候选，待登记1,033组、1,089条候选。",
        "当前尚余4,659个 `new` 身份组、4,785条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记53组、90条候选，待登记1,032组、1,088条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Francesco Marucelli 跨章直接端点组登记（2026-10-16）

`cand-1554`（M.csv#93）已登记为[Francesco Marucelli 人物卡](../../04-knowledge/units/persons/francesco-marucelli.md)。第6章 pp.157–158 提供全名、赞助人和收藏家身份以及藏书和写作语境；第8章 p.235 的 Marucelli 兄弟上下文记载 Francesco 于1703年在罗马去世，与索引页码相合。16条直接 S2 端点中11条关系候选留待 S6；本批未新增正式关系、work/archive KU、外部身份记录或 S5 补足。批次脚本核对6处原文锚点、S3 决定和映射。manifest 从1,177增至1,178；累计登记159组、203条候选映射，余4,659组、4,785条。

"""
    return replace_once(
        text,
        "### person：Carlo de’ Rossi 跨章直接端点组登记（2026-10-16）\n\n",
        batch + "### person：Carlo de’ Rossi 跨章直接端点组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register Francesco Marucelli's person identity group in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == MEMBER)
    alignment = next(row for row in alignments if row.get("candidate_id") == MEMBER and not row.get("external_source"))
    assert len(manifest) == 1177, f"unexpected manifest size: {len(manifest)}"
    assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
    assert candidate["index_entry_id"] == "M.csv#93" and candidate["index_page_range"] == "157, 158, 235"
    assert alignment["decision"] == "new" and not alignment.get("ku_id") and get_group(alignment["resolution_note"]) == GROUP
    assert not any(row["type"] == KIND and "marucelli" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)
    existing_card_path = ROOT / CARD_PATH
    existing_legacy_card = existing_card_path.read_text(encoding="utf-8-sig") if existing_card_path.exists() else None
    if existing_legacy_card is not None:
        assert (
            "title: 弗朗切斯科·马鲁切利（Francesco Marucelli）" in existing_legacy_card
            and "Haskell, Patrons and Painters" in existing_legacy_card
            and "Helmbrecker" in existing_legacy_card
            and "第一、六章限定测试" in existing_legacy_card
        ), "existing card is not the expected unaccepted legacy draft"
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") == MEMBER or statement.get("object_candidate_id") == MEMBER:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert (len(endpoints), len(relation_endpoints)) == (16, 11), (len(endpoints), len(relation_endpoints))

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
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (158, 202)
    for group, rows in registered_groups.items():
        assert len(rows) == len(new_groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    registered_person_groups = {
        group: rows for group, rows in registered_groups.items()
        if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    assert (len(registered_person_groups), sum(map(len, registered_person_groups.values()))) == (52, 89)

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
    assert len(planned_manifest) == 1178

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
            "dry-run passed: group=1 candidates=1 endpoints=16 relation_candidates=11 "
            "registered_groups_after=159 mapped_candidates_after=203 manifest_after=1178"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=1 endpoints=16 relation_candidates=11 "
        "manifest=1178 registered_groups=159 mapped_candidates=203"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
