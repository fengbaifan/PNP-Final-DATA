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
GROUP = "new-person:giambattista-marino-17f964d895"
MEMBERS = ("cand-1548",)
KU_ID = "units/persons/giambattista-marino"
REL_PATH = "04-knowledge/units/persons/giambattista-marino.md"


RECORD = {
    "name_zh": "吉安巴蒂斯塔·马里诺",
    "name_en": "Giambattista Marino",
    "description_zh": (
        "第2章称那不勒斯诗人 Giambattista Marino 是 Marcello Sacchetti 的密友之一，记他于1623年结束八年巴黎之行返回意大利，在罗马停留一年后前往那不勒斯并很快去世。书中称他热爱绘画、收藏绘画、促成年轻 Nicolas Poussin 来意大利，并曾将 Poussin 作品介绍给 Marcello Sacchetti；第4章记述 Poussin 绘画最早的赞赏者 Marino 委托作品以及其遗赠去向不明。作者对宫廷赞助未果的原因保留为推测。"
    ),
    "description_en": (
        "Chapter 2 identifies the Neapolitan poet Giambattista Marino as one of Marcello Sacchetti's close friends and says he returned to Italy in 1623 after an eight-year stay in Paris, spent a year in Rome, and soon died in Naples. The book describes his interest in painting and collecting, says he persuaded the young Nicolas Poussin to come to Italy, and records his introduction of Poussin to Marcello Sacchetti. Chapter 4 describes works commissioned from Poussin by Marino, whom it calls the painter's first known admirer, and leaves the recipient of Marino's bequest unidentified. Haskell's explanation for Marino's unsuccessful papal patronage remains conjectural."
    ),
    "context_zh": (
        "M.csv#87“Marino, Giambattista”列出第2章 pp.38、44，第4章 pp.96、104、115、118、122，第10章 p.318，第14章 p.348及第20章 p.398。第2章 pp.38–44叙其诗人身份、巴黎归来、罗马与那不勒斯行程、与 Marcello Sacchetti 的友谊、绘画兴趣和 Poussin 的早期意大利经历；第4章 p.115 讨论 Marino 委托的 Poussin 图画及其后来归属，受遗赠者只称不明友人，并将 Cassiano dal Pozzo 列为可能对象。关于其未获教皇赞助的原因，作者用“no doubt”表达推测，不据此确立因果。索引后续页码仅作候选定位，不把未逐项引用的页码扩写为额外事实。"
    ),
    "context_en": (
        "M.csv#87, “Marino, Giambattista,” lists Chapter 2 pp. 38 and 44; Chapter 4 pp. 96, 104, 115, 118, and 122; Chapter 10 p. 318; Chapter 14 p. 348; and Chapter 20 p. 398. Chapters 2 pp. 38–44 discuss his poetic identity, return from Paris, movements between Rome and Naples, friendship with Marcello Sacchetti, interest in painting, and Poussin's early Italian career. Chapter 4 p. 115 discusses Poussin drawings commissioned by Marino and their later custody; the recipient of Marino's bequest is described only as an unidentified friend, with Cassiano dal Pozzo offered as a possibility. Haskell's explanation for the lack of papal patronage is hedged with “no doubt” and is not treated as established causation. The remaining index page references are retained as locating evidence and are not expanded into unreviewed claims."
    ),
    "boundary_zh": (
        "本卡对应唯一候选 cand-1548，属于 S3 跨章组 `new-person:giambattista-marino-17f964d895`；索引主项和多章正文均以 Giambattista Marino 指名，当前 manifest 无既有人物 KU。那不勒斯籍贯、巴黎访问年数、去世地点及赞助解释均按 Haskell 的原话和限定记录，不引入外部生卒年或作品目录。受遗赠者身份保留未明，Cassiano dal Pozzo 只是作者提出的可能人选。16条直接 S2 断言端点全部为关系候选，留待 S6；本批不新增正式关系、archive/work KU、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents the sole candidate cand-1548 in the cross-chapter S3 group `new-person:giambattista-marino-17f964d895`; the index main entry and passages across chapters name Giambattista Marino, and there is no existing person KU in the manifest. His Neapolitan origin, length of the Paris stay, place of death, and the explanation for the lack of papal patronage follow Haskell's wording and qualifications; no external life dates or work catalogue are added. The recipient of the bequest remains unidentified, with Cassiano dal Pozzo only a possibility proposed by the author. All 16 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, archive or work KUs, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": (
        "索引规范名为 Marino, Giambattista；正文以 Giambattista Marino、Marino 称呼。中文显示名为工作音译。"
    ),
    "type_notes_en": (
        "The index form is Marino, Giambattista; the prose uses Giambattista Marino and Marino. The Chinese display name is a working transliteration."
    ),
    "sources": [
        card_writer.source(
            "2", "38", "02_CHP-2_sec_ii.md", "76–77",
            "Among his close friends was the most famous poet of the age, the Neapolitan Giambattista Marino, who returned to Italy from an eight-year visit to Paris in 1623.2 Marino spent only a year in Rome before going to\nNaples where he died soon afterwards, disappointed in his hopes of papal patronage— no doubt the sensuality of much of his verse offended Urban’s austerer taste.",
            "第2章称 Marino 为那不勒斯诗人，记其1623年结束八年巴黎之行返意，在罗马一年后赴那不勒斯并很快去世；教皇赞助未果的解释保留作者推测语气。",
        ),
        card_writer.source(
            "2", "38", "02_CHP-2_sec_ii.md", "77",
            "None the less he enjoyed a triumphant welcome in Rome, and he must have been particularly well received by Sacchetti, to whom he had dedicated a pretty song, for the two men shared a passion for painting. Marino had made a collection of his own and had persuaded the young Nicolas Poussin to follow him to Italy.",
            "第2章记 Marino 在罗马受到欢迎，与 Sacchetti 共享绘画兴趣，拥有自己的收藏，并劝说年轻 Poussin 来意大利。",
        ),
        card_writer.source(
            "2", "44", "02_CHP-2_sec_iv.md", "14",
            "Nicolas Poussin, who had arrived from Paris eighteen months earlier and had been introduced by Giambattista Marino to Barberini’s friend Marcello Sacchetti.4",
            "第2章称 Nicolas Poussin 由 Giambattista Marino 介绍给 Marcello Sacchetti。",
        ),
        card_writer.source(
            "4", "115", "04_CHP-4_sec_ii.md", "186",
            "Poussin that had originally been commissioned by the painter’s first known admirer, the poet Giambattista Marino. They consisted mainly of mythological subjects loosely inspired by Marino’s most famous poem, the Adone. Marino bequeathed them to some unidentified friend, possibly Cassiano dal Pozzo, and when the French writer Felibien was in Rome, between 1647 and 1650, they belonged to Massimi, ‘who kept them most carefully among several others by Poussin’s hand.’3 t'Exposition Poussin, p. 109.",
            "第4章称相关 Poussin 图画原由 Marino 委托；其遗赠对象不明，Cassiano dal Pozzo 仅为可能人选，后来一度为 Massimi 所有。",
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


def group_of(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def replace_after_once(text, marker, old, new, label):
    start = text.index(marker) + len(marker)
    return text[:start] + replace_once(text[start:], old, new, label)


def updated_process(text):
    text = replace_once(
        text,
        "截至 Niccolò Cassana 批次，4,818 个当前 `new` 身份组中完成152组，余4,666组；4,988条成员候选中映射193条，余4,795条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记46组、80条候选，待登记1,039组、1,098条候选。",
        "截至 Giambattista Marino 批次，4,818 个当前 `new` 身份组中完成153组，余4,665组；4,988条成员候选中映射194条，余4,794条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记47组、81条候选，待登记1,038组、1,097条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Pietro Liberi、Niccolò Cassana 已登记为人物 KU。",
        "Pietro Liberi、Niccolò Cassana、Giambattista Marino 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Niccolò Cassana 的16条关系候选及其他已登记对象的 S2 关系候选仍待 S6",
        "Niccolò Cassana 的16条、Giambattista Marino 的16条关系候选及其他已登记对象的 S2 关系候选仍待 S6",
        "process pending relation candidates",
    )
    batch = """### person：Giambattista Marino 跨章身份组登记（2026-10-16）

- `cand-1548`（M.csv#87）属于 `new-person:giambattista-marino-17f964d895`，登记为 `units/persons/giambattista-marino`。索引页码横跨第2、4、10、14、20章；现有 manifest 中无同名人物 KU。
- 第2章记其与 Marcello Sacchetti 的友谊、1623年返意后的行程、绘画兴趣和对 Poussin 的影响；关于教皇赞助未果原因是作者推测。第4章称 Marino 是 Poussin 最早的赞赏者之一，并记 Poussin 图画由其委托、遗赠给身份未明之友人；Cassiano dal Pozzo 只作为可能对象保留。未增写外部生卒年或作品目录。
- 16条直接 S2 断言端点全部为关系候选，留待 S6；本批未新增正式关系、archive/work KU、外部身份记录或 S5 补足。[register_s4_person_giambattista_marino_batch_20261016.py](register_s4_person_giambattista_marino_batch_20261016.py) dry-run 核对候选组、4处精确引文、端点数和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,171增至1,172；累计登记153组、194条候选映射，余4,665组、4,794条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def updated_result(text):
    text = replace_once(text, "目前完成152组、映射193条成员候选，余4,666组、4,795条映射。", "目前完成153组、映射194条成员候选，余4,665组、4,794条映射。", "result top S4 counts")
    text = replace_once(
        text,
        "Pietro Liberi、Niccolò Cassana 四十四个补充 person 组",
        "Pietro Liberi、Niccolò Cassana、Giambattista Marino 四十五个补充 person 组",
        "result top person names",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,171 KU；含本轮新增46个 person 组（", "| [KU 登记](../tables/ku-manifest.csv) | 1,172 KU；含本轮新增47个 person 组（", "result manifest count")
    text = replace_once(
        text,
        "Pietro Liberi、Niccolò Cassana、2个 Valmarana 组",
        "Pietro Liberi、Niccolò Cassana、Giambattista Marino、2个 Valmarana 组",
        "result manifest names",
    )
    text = replace_once(text, "当前已登记46个 person 组（", "当前已登记47个 person 组（", "result current person count")
    text = replace_after_once(
        text,
        "当前已登记47个 person 组（",
        "Pietro Liberi、Niccolò Cassana、",
        "Pietro Liberi、Niccolò Cassana、Giambattista Marino、",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,666个 `new` 身份组、4,795条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记46组、80条候选，待登记1,039组、1,098条候选。",
        "当前尚余4,665个 `new` 身份组、4,794条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记47组、81条候选，待登记1,038组、1,097条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Giambattista Marino 跨章身份组登记（2026-10-16）

`cand-1548`（M.csv#87）已映射至 [Giambattista Marino 人物卡](../../04-knowledge/units/persons/giambattista-marino.md)。索引页码跨第2、4、10、14、20章；现有清单中无同名人物 KU。16条直接 S2 端点均为关系候选，留待 S6；遗赠对象仍未确认，Cassiano dal Pozzo 仅是作者提出的可能人选。批次不新增正式关系、archive/work KU、外部身份核验或 S5 补足。dry-run/apply 依据见[S4批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_giambattista_marino_batch_20261016.py)。manifest 从1,171增至1,172；累计登记153组、194条候选映射，余4,665组、4,794条。

"""
    return replace_once(
        text,
        "### person：Niccolò Cassana 跨索引身份组登记（2026-10-16）\n\n",
        batch + "### person：Niccolò Cassana 跨索引身份组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Giambattista Marino person identity group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result_text = RESULT_PATH.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1171, f"unexpected manifest count: {len(manifest)}"
    counts = Counter(row["decision"] for row in current)
    assert counts == Counter({"same": 1698, "new": 4988, "undecided": 5614, "excluded": 97, "conflict": 7}), counts
    groups = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = group_of(row["resolution_note"])
            assert group
            groups[group].append(row)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new" and row.get("ku_id"):
            registered[group_of(row["resolution_note"])].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(groups), sum(map(len, groups.values()))) == (4818, 4988)
    assert (len(registered_groups), sum(len(value) for value in registered_groups.values())) == (152, 193)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert not any(row.get("ku_id") for row in groups[GROUP])
    assert alignment_by_id[MEMBERS[0]]["decision"] == "new"
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == "person"
    assert candidate_by_id[MEMBERS[0]]["canonical_name"] == "Marino, Giambattista"
    assert candidate_by_id[MEMBERS[0]]["index_entry_id"] == "M.csv#87"
    assert not (ROOT / REL_PATH).exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == "person" and "giambattista marino" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)

    endpoint_ids, relation_ids = set(), set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if MEMBERS[0] in {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert (len(endpoint_ids), len(relation_ids)) == (16, 16), (len(endpoint_ids), len(relation_ids))
    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id[MEMBERS[0]]["ku_id"] = KU_ID
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": "person", "canonical_name": RECORD["name_zh"], "name_en": RECORD["name_en"], "source_task": TASK, "card_path": REL_PATH})
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new":
            planned_groups[group_of(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(len(value) for value in planned_registered.values())) == (153, 194)
    assert (len(planned_groups) - len(planned_registered), sum(len(value) - sum(bool(row.get("ku_id")) for row in value) for value in planned_groups.values())) == (4665, 4794)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, "person")
    card_text, dates = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert dates == 2

    if args.dry_run:
        print(
            "dry-run passed: Giambattista Marino person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} source_quotes={len(RECORD['sources'])} "
            "existing_KU_matches=0 registered_groups_after=153 mapped_candidates_after=194 "
            "pending_groups=4665 pending_candidates=4794 manifest_after=1172; no formal relations added"
        )
        return 0

    (ROOT / REL_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > REL_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {REL_PATH}")
    ACCEPTED_PATH.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(planned_process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(planned_result, encoding="utf-8-sig", newline="\n")
    print(f"applied: Giambattista Marino person_groups=1 candidates=1 endpoints=16 relation_candidates=16 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
