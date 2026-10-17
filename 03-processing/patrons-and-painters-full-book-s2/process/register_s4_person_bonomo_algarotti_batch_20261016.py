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
GROUP = "new-person:algarotti-bonomo-6fee58462e"
MEMBERS = ("cand-0040",)
KU_ID = "units/persons/bonomo-algarotti"
REL_PATH = "04-knowledge/units/persons/bonomo-algarotti.md"


RECORD = {
    "name_zh": "博诺莫·阿尔加罗蒂",
    "name_en": "Bonomo Algarotti",
    "description_zh": (
        "哈斯克尔第14章称 Bonomo 为 Francesco Algarotti 的长兄，称他有鉴赏力，并认为他对 Francesco 的影响相当大但难以评估。书中记述 Bonomo 购买了两人共同收藏中的许多绘画，协助落实 Francesco 的计划，并向他提供意大利社交与艺术消息；第14章注释和第15章称 Bonomo 于1776年去世。"
        "索引以“Algarotti, Bonomo”列名；本卡按本书所见称谓登记这位兄长，不与 Francesco Algarotti 合并。相关亲缘、通信、藏品和委托事实仍保留来源限定。"
    ),
    "description_en": (
        "Chapter 14 identifies Bonomo as Francesco Algarotti's elder brother, describes him as a man of taste, and says his influence on Francesco was considerable but difficult to evaluate. "
        "The book reports that Bonomo bought many of the pictures in their joint collection, helped put Francesco's plans into practice, and kept him informed about social and artistic news in Italy; a Chapter 14 note and Chapter 15 report that Bonomo died in 1776. "
        "The index form is Algarotti, Bonomo. This card registers the brother as named in the book and keeps him distinct from Francesco Algarotti; kinship, correspondence, collection, and commission claims remain source-bounded."
    ),
    "context_zh": (
        "A.csv#41“Algarotti, Bonomo”指向第10章 p.293 注3、第14章 pp.347–348、350注、355–357及第15章 p.361。第10章注3列出 Francesco 致其兄 Bonomo 的1749年书信；第14章开篇连续介绍长兄、两人共同收藏及其协助 Francesco 的计划；注释称 Bonomo 于1776年去世。第15章再次以 Francesco 的兄长解释其藏画在1776年后开始散出。原书未给出 Bonomo 的其他名字。"
    ),
    "context_en": (
        "A.csv#41, “Algarotti, Bonomo,” points to Chapter 10 p. 293 n. 3; Chapter 14 pp. 347–48, 350 n., and 355–57; and Chapter 15 p. 361. The Chapter 10 note lists a 1749 letter from Francesco to his brother Bonomo. Chapter 14 introduces the elder brother and describes their joint collection and his help with Francesco's plans; its note reports that Bonomo died in 1776. Chapter 15 again identifies him as Francesco's brother when explaining that the pictures began to disperse after 1776. The book supplies no other given name for Bonomo."
    ),
    "boundary_zh": (
        "本卡对应唯一 S3 候选 cand-0040 及索引形式“Algarotti, Bonomo”；正文只称 Bonomo，未提供更完整个人名。第14、15章明确称他为 Francesco Algarotti 的兄长，因此与既有 units/persons/francesco-algarotti 是两位不同人物，不能因共同收藏、通信或同姓合并。16条直接 S2 断言端点中15条标记为关系候选，全部留待 S6；本批未新增正式关系、作品/藏品/档案 KU、外部身份记录或 S5 补足。中文名为工作音译。"
    ),
    "boundary_en": (
        "This card represents the sole S3 candidate cand-0040 and the index form “Algarotti, Bonomo”; the prose calls him Bonomo and supplies no fuller personal name. Chapters 14 and 15 explicitly identify him as Francesco Algarotti's brother, so he is a different person from the existing units/persons/francesco-algarotti KU and must not be merged with Francesco because of their joint collection, correspondence, or surname. Fifteen of 16 direct S2 statement endpoints are marked as relation candidates and remain for S6. This batch adds no formal relation, work/collection/archive KU, external identity record, or S5 enrichment. The Chinese display name is a working transliteration."
    ),
    "type_notes_zh": (
        "索引规范名为 Algarotti, Bonomo；正文称 Bonomo 或 Francesco 的兄长。本书没有提供其他名字，故不补写全名或生平。"
    ),
    "type_notes_en": (
        "The index form is Algarotti, Bonomo; the prose calls him Bonomo or Francesco's brother. The book supplies no other given name, so no fuller name or biography is added."
    ),
    "sources": [
        card_writer.source(
            "10", "293 n. 3", "10_CHP-10_intro.md", "559",
            "Letter from Francesco Algarotti to his brother Bonomo dated 5 September 1749",
            "第10章注3列出 Francesco 于1749年9月5日致其兄 Bonomo 的信；只按 Haskell 的书目引文记录。",
            "该信及 Treviso 馆藏未在本批独立查阅。",
        ),
        card_writer.source(
            "14", "347", "14_CHP-14_intro.md", "9–15",
            "his elder brother\nBonomo, himself a man of great taste, whose influence on the more mercurial and spectacular Francesco was certainly considerable though difficult to evaluate.",
            "第14章称 Bonomo 是 Francesco 的长兄、有鉴赏力，并将其影响评价为相当大但难以评估。",
        ),
        card_writer.source(
            "14", "347", "14_CHP-14_intro.md", "10–15",
            "it was Bonomo who bought many of the pictures that made up their joint collection",
            "第14章称 Bonomo 购买了 Francesco 与他共同收藏中的许多绘画。",
        ),
        card_writer.source(
            "14", "347 n. 1", "14_CHP-14_intro.md", "169",
            "dedicated to Francesco’s brother Bonomo who died in 1776.",
            "第14章注1称 Farsetti 的拉丁文 Algarotti 传记题献给 Francesco 的兄长 Bonomo，并称其于1776年去世。",
        ),
        card_writer.source(
            "14", "356", "14_CHP-14_intro.md", "102",
            "He was always writing to Bonomo asking him to look through their collection and send suitable examples to be disposed of abroad",
            "第14章称 Francesco 常写信请 Bonomo 查看两人收藏并挑选适合出售到国外的作品。",
        ),
        card_writer.source(
            "15", "361", "15_CHP-15_sec_i.md", "11",
            "Algarotti’s own pictures began to be dispersed soon after the death of his brother Bonomo in 1776.",
            "第15章称 Francesco 的藏画在其兄 Bonomo 于1776年去世后不久开始散出。",
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


def updated_process(text):
    text = replace_once(
        text,
        "截至 Giovanni Vianello 批次及 Romanelli 复用裁决，4,818 个当前 `new` 身份组中完成147组，余4,671组；4,988条成员候选中映射187条，余4,801条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记41组、74条候选，待登记1,044组、1,104条候选。",
        "截至 Bonomo Algarotti 批次，4,818 个当前 `new` 身份组中完成148组，余4,670组；4,988条成员候选中映射188条，余4,800条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记42组、75条候选，待登记1,043组、1,103条候选。",
        "process S4 current counts",
    )
    text = replace_once(
        text,
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello 已登记为人物 KU。",
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello、Bonomo Algarotti 已登记为人物 KU。",
        "process registered person list",
    )
    text = replace_once(
        text,
        "Giovanni Vianello 的8条及其他已登记对象",
        "Giovanni Vianello 的8条、Bonomo Algarotti 的15条及其他已登记对象",
        "process pending S6 list",
    )
    batch = """### person：Bonomo Algarotti 跨章直接端点登记（2026-10-16）

- `cand-0040`（A.csv#41，索引名 Algarotti, Bonomo）属于 `new-person:algarotti-bonomo-6fee58462e`，登记为 `units/persons/bonomo-algarotti`。第14、15章称 Bonomo 是 Francesco Algarotti 的长兄；第10章脚注记录 Francesco 致兄长 Bonomo 的书信。该组只指兄长，不与既有 Francesco Algarotti KU 合并；本书没有提供 Bonomo 的其他名字。
- 卡片记录第14章对其鉴赏力、影响、共同收藏和协助计划的叙述，并保留 Haskell 对影响难以评估的限定；书中称 Bonomo 于1776年去世。引文所指 Treviso 书信和 1790 年代传记未在本批独立查阅。
- 16条直接 S2 断言端点中15条标记为关系候选，全部留待 S6；本批未新增正式关系、作品/藏品/档案 KU、外部身份记录或 S5 补足。[register_s4_person_bonomo_algarotti_batch_20261016.py](register_s4_person_bonomo_algarotti_batch_20261016.py) dry-run 核对单候选组、6处精确原文锚点、既有 Francesco Algarotti KU 边界、端点数和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,166增至1,167；累计登记148组、188条候选映射，余4,670组、4,800条候选。

"""
    return replace_once(text, "### 登记进度与后续\n", batch + "### 登记进度与后续\n", "process Bonomo batch log")


def updated_result(text):
    lines = text.splitlines()
    status_ids = [i for i, line in enumerate(lines) if line.startswith("**当前状态：全书 S2 语义处理已完成")]
    assert len(status_ids) == 1, f"result status lines={len(status_ids)}"
    i = status_ids[0]
    line = replace_once(
        lines[i],
        "目前完成147组、映射187条成员候选，余4,671组、4,801条映射",
        "目前完成148组、映射188条成员候选，余4,670组、4,800条映射",
        "result S4 status counts",
    )
    line = replace_once(
        line,
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello 三十九个补充 person 组",
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello、Bonomo Algarotti 四十个补充 person 组",
        "result S4 registered person names",
    )
    lines[i] = line
    text = "\n".join(lines) + "\n"
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,166 KU；含本轮新增41个 person 组（",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,167 KU；含本轮新增42个 person 组（",
        "result KU manifest table",
    )
    text = replace_once(
        text,
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello、2个 Valmarana 组",
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello、Bonomo Algarotti、2个 Valmarana 组",
        "result KU registered names table",
    )
    text = replace_once(
        text,
        "当前尚余4,671个 `new` 身份组、4,801条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记41组、74条候选，待登记1,044组、1,104条候选。",
        "当前尚余4,670个 `new` 身份组、4,800条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记42组、75条候选，待登记1,043组、1,103条候选。",
        "result current S4 type counts",
    )
    text = replace_once(text, "当前已登记41个 person 组（", "当前已登记42个 person 组（", "result person summary count")
    text = replace_once(
        text,
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello、Valmarana 跨章2组",
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello、Bonomo Algarotti、Valmarana 跨章2组",
        "result person summary names",
    )
    batch = """### person：Bonomo Algarotti 跨章直接端点登记（2026-10-16）

`cand-0040`（A.csv#41）已映射至 [Bonomo Algarotti 人物卡](../../04-knowledge/units/persons/bonomo-algarotti.md)。第14、15章明确称 Bonomo 为 Francesco Algarotti 的长兄；索引名“Algarotti, Bonomo”据此登记其兄长身份，保留与既有 Francesco Algarotti KU 的人物边界。16条直接 S2 端点中15条为关系候选，全部留待 S6；书内没有提供 Bonomo 的其他名字。本批未新增正式关系、作品/藏品/档案 KU、外部身份核验或 S5 补足。依据与 dry-run/apply 记录见[人物卡](../../04-knowledge/units/persons/bonomo-algarotti.md)和[S4 批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_bonomo_algarotti_batch_20261016.py)。manifest 从1,166增至1,167；累计登记148组、188条候选映射，余4,670组、4,800条。

"""
    return replace_once(
        text,
        "### person：Giovanni Vianello 直接端点登记（2026-10-16）\n\n",
        batch + "### person：Giovanni Vianello 直接端点登记（2026-10-16）\n\n",
        "result Bonomo batch section",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Bonomo Algarotti person identity group")
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

    assert len(manifest) == 1166, f"unexpected manifest count: {len(manifest)}"
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
    registered_groups = {g: rows for g, rows in registered.items() if rows}
    assert (len(groups), sum(map(len, groups.values()))) == (4818, 4988)
    assert (len(registered_groups), sum(len(v) for v in registered_groups.values())) == (147, 187)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert not any(row.get("ku_id") for row in groups[GROUP])
    assert alignment_by_id[MEMBERS[0]]["decision"] == "new"
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == KIND
    assert candidate_by_id[MEMBERS[0]]["canonical_name"] == "Algarotti, Bonomo"
    assert not candidate_by_id[MEMBERS[0]]["sub_entry"]

    card_path = ROOT / REL_PATH
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert any(row["ku_id"] == "units/persons/francesco-algarotti" and row["type"] == "person" for row in manifest)
    assert not any(
        row["type"] == KIND and "bonomo algarotti" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if MEMBERS[0] in {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 16 and len(relation_ids) == 15, (len(endpoint_ids), len(relation_ids))
    for item in RECORD["sources"]:
        source = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id[MEMBERS[0]]["ku_id"] = KU_ID
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": KIND, "canonical_name": RECORD["name_zh"], "name_en": RECORD["name_en"], "source_task": TASK, "card_path": REL_PATH})
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if row.get("candidate_id") and not row.get("external_source") and row["decision"] == "new":
            planned_groups[group_of(row["resolution_note"])].append(row)
    planned_registered = {g: rows for g, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({r["ku_id"] for r in mapped}) == 1, group
    assert (len(planned_registered), sum(len(v) for v in planned_registered.values())) == (148, 188)
    assert (len(planned_groups) - len(planned_registered), sum(len(v) - sum(bool(r.get("ku_id")) for r in v) for v in planned_groups.values())) == (4670, 4800)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert date_count == 2

    if args.dry_run:
        print(
            "dry-run passed: Bonomo Algarotti person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "source_quotes=6 registered_groups_after=148 mapped_candidates_after=188 "
            "pending_groups=4670 pending_candidates=4800 manifest_after=1167; "
            "kept distinct from existing Francesco Algarotti KU; no formal relations added"
        )
        return 0

    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
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
    print(f"applied: Bonomo Algarotti person_groups=1 candidates=1 endpoints=16 relation_candidates=15 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
