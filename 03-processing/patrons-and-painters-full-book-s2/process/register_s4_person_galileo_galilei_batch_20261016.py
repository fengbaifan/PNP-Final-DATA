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
GROUP = "new-person:galilei-galileo-ff0ea1f6cb"
MEMBERS = ("cand-1105",)
KU_ID = "units/persons/galileo-galilei"
REL_PATH = "04-knowledge/units/persons/galileo-galilei.md"


RECORD = {
    "name_zh": "伽利略·伽利莱",
    "name_en": "Galileo Galilei",
    "description_zh": (
        "第4章记 Cassiano dal Pozzo 与 Galileo 的交往，并称 Cassiano 在 Galileo 受宗教裁判所判决约一年后仍以友好口吻致信；Galileo 回信感谢 Cassiano 将其肖像纳入藏书。该章还称 Ludovico Cigoli 是 Galileo 偏爱的画家及偶尔合作对象，并呈现 Galileo 对绘画风格的看法。Haskell 对科学态度与审美的联系属于作者解释；第3章与第10章另有对 Galileo 的提及，均按原书语境限定。"
    ),
    "description_en": (
        "Chapter 4 recounts Galileo's contact with Cassiano dal Pozzo: about a year after Galileo's condemnation by the Inquisition, Cassiano wrote to him in a friendly spirit, and Galileo thanked Cassiano for including his portrait in the library. The chapter also identifies Ludovico Cigoli as Galileo's favourite painter and an occasional collaborator, and presents Galileo's views on painting. Haskell's connection between a scientific outlook and aesthetic taste remains the author's interpretation. Chapters 3 and 10 contain further references to Galileo, retained within their source contexts."
    ),
    "context_zh": (
        "G.csv#12“Galilei, Galileo”列出第2章 p.33、第3章 p.74、第4章 pp.98–108、第10章 p.320及第20章 p.366。第4章 p.102 称其偏爱的画家和偶尔合作者为 Ludovico Cigoli，并将科学态度与审美转变联系起来；p.103 引述其关于绘画的比较意见，随后由 Haskell 概括其艺术立场。p.108 记 Cassiano dal Pozzo 在 Galileo 受宗教裁判所判决约一年后友好致信，Galileo 回复并感谢其收藏肖像。第3章 p.74 仅以 Grassi 与 Galileo 的争议作背景说明；第10章 p.320 称 Galileo 是 Lodoli 的偏爱作者之一。上述内容不扩写成独立科学史传记。"
    ),
    "context_en": (
        "G.csv#12, “Galilei, Galileo,” lists Chapter 2 p. 33, Chapter 3 p. 74, Chapter 4 pp. 98–108, Chapter 10 p. 320, and Chapter 20 p. 366. Chapter 4 p. 102 names Ludovico Cigoli as Galileo's favourite painter and occasional collaborator and connects scientific outlook with aesthetic taste; p. 103 quotes Galileo's comparison of painting styles, followed by Haskell's summary of his artistic position. Page 108 recounts a friendly letter from Cassiano dal Pozzo about a year after Galileo's condemnation by the Inquisition and Galileo's thanks for the portrait in Cassiano's library. Chapter 3 p. 74 mentions the Grassi controversy only as context; Chapter 10 p. 320 calls Galileo one of Lodoli's favourite authors. These passages are not expanded into an independent scientific biography."
    ),
    "boundary_zh": (
        "本卡对应唯一 cand-1105，属于跨章组 `new-person:galilei-galileo-ff0ea1f6cb`；索引给出全名，正文多以 Galileo 称呼，当前 manifest 中无既有人物 KU。裁判所判决及 Cassiano 往来按 Haskell 的叙述保留，不补外部日期、科学史事实或全书作品清单。第4章关于艺术偏好与科学态度的语句区分来源直接记载和作者解释。16条直接 S2 断言端点中11条为关系候选，全部留待 S6；本批不新增正式关系、作品/archive KU、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents the sole candidate cand-1105 in the cross-chapter group `new-person:galilei-galileo-ff0ea1f6cb`; the index supplies the full name while the prose usually says Galileo, and no existing person KU is in the manifest. The Inquisition judgment and correspondence with Cassiano remain attributed to Haskell; no external dates, scientific-history facts, or full-book work list are added. Chapter 4's statements about artistic preference and scientific outlook distinguish source report from authorial interpretation. Eleven of 16 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, work or archive KUs, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": (
        "索引规范名为 Galilei, Galileo；正文多以 Galileo 指称。中文显示名为通行音译。"
    ),
    "type_notes_en": (
        "The index form is Galilei, Galileo; the prose usually refers to him as Galileo."
    ),
    "sources": [
        card_writer.source(
            "3", "74", "03_CHP-3_sec_ii.md", "116",
            "In the end a Jesuit father, Orazio Grassi, of no architectural experience but celebrated for a controversy with Galileo, was appointed.",
            "第3章提及 Jesuit Orazio Grassi 曾与 Galileo 发生争论；仅按原书作为格拉西任命背景记录。",
        ),
        card_writer.source(
            "4", "102", "04_CHP-4_sec_ii.md", "44",
            "Galileo himself had been the first to show how a scientific attitude almost inevitably gave a particular turn to aesthetic taste.3 His favourite painter and occasional collaborator was Ludovico Cigoli, the leader of those Florentine artists who were breaking away from a late Mannerist style to a more rational and naturalistic manner.4",
            "第4章称 Galileo 偏爱的画家及偶尔合作者为 Ludovico Cigoli，并将科学态度对审美的影响作为作者分析。",
        ),
        card_writer.source(
            "4", "103", "04_CHP-4_sec_ii.md", "47",
            "Galileo’s was a plea for the classical against the Mannerist, the full-blooded and rational against the perverse and the illogical.",
            "第4章以该句概括 Galileo 关于艺术的立场；这是 Haskell 对此前引文的解释。",
        ),
        card_writer.source(
            "4", "108", "04_CHP-4_sec_ii.md", "114–115",
            "We find him writing in the most friendly spirit to his old colleague Galileo about a year after his condemnation by the Inquisition; and in 1641 he received a letter from the scientist, written ‘from the Villa d’Arcetri, my unending prison and exile from town’.\nIn this Galileo thanked Cassiano for including his portrait among those which he kept in his library.3",
            "第4章记 Cassiano 在 Galileo 受宗教裁判所判决约一年后友好致信，Galileo 于1641年回信并感谢其收藏自己的肖像。",
        ),
        card_writer.source(
            "10", "320", "10_CHP-10_sec_ii.md", "158–159",
            "Lodoli’s favourite authors were\nGalileo and Bacon; he took his pupils to visit libraries and distinguished scholars.",
            "第10章称 Galileo 与 Bacon 是 Carlo Lodoli 喜爱的作者。",
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
        "截至 Giambattista Marino 批次，4,818 个当前 `new` 身份组中完成153组，余4,665组；4,988条成员候选中映射194条，余4,794条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记47组、81条候选，待登记1,038组、1,097条候选。",
        "截至 Galileo Galilei 批次，4,818 个当前 `new` 身份组中完成154组，余4,664组；4,988条成员候选中映射195条，余4,793条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记48组、82条候选，待登记1,037组、1,096条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Pietro Liberi、Niccolò Cassana、Giambattista Marino 已登记为人物 KU。",
        "Pietro Liberi、Niccolò Cassana、Giambattista Marino、Galileo Galilei 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Giambattista Marino 的16条关系候选及其他已登记对象的 S2 关系候选仍待 S6",
        "Giambattista Marino 的16条与 Galileo Galilei 的11条关系候选及其他已登记对象的 S2 关系候选仍待 S6",
        "process pending relation candidates",
    )
    batch = """### person：Galileo Galilei 跨章身份组登记（2026-10-16）

- `cand-1105`（G.csv#12）属于 `new-person:galilei-galileo-ff0ea1f6cb`，登记为 `units/persons/galileo-galilei`。索引页码横跨第2、3、4、10、20章；manifest 中无同名人物 KU。
- 卡片据第4章关于 Cassiano dal Pozzo 友好通信与肖像、第4章对 Ludovico Cigoli 的画家身份、第3章对 Orazio Grassi 争议的提及，以及第10章对 Lodoli 阅读偏好的叙述。第4章将科学态度和艺术判断相联系的句子作为 Haskell 的作者解释保留；不扩写外部生平或科学史。
- 16条直接 S2 断言端点中11条为关系候选，全部留待 S6；本批未新增正式关系、作品/archive KU、外部身份记录或 S5 补足。[register_s4_person_galileo_galilei_batch_20261016.py](register_s4_person_galileo_galilei_batch_20261016.py) dry-run 核对唯一组成员、5处精确引文、端点/关系候选数和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,172增至1,173；累计登记154组、195条候选映射，余4,664组、4,793条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def updated_result(text):
    text = replace_once(text, "目前完成153组、映射194条成员候选，余4,665组、4,794条映射。", "目前完成154组、映射195条成员候选，余4,664组、4,793条映射。", "result top S4 counts")
    text = replace_once(
        text,
        "Giambattista Marino 四十五个补充 person 组",
        "Giambattista Marino、Galileo Galilei 四十六个补充 person 组",
        "result top person names",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,172 KU；含本轮新增47个 person 组（", "| [KU 登记](../tables/ku-manifest.csv) | 1,173 KU；含本轮新增48个 person 组（", "result manifest count")
    text = replace_once(
        text,
        "Giambattista Marino、2个 Valmarana 组",
        "Giambattista Marino、Galileo Galilei、2个 Valmarana 组",
        "result manifest names",
    )
    text = replace_once(text, "当前已登记47个 person 组（", "当前已登记48个 person 组（", "result current person count")
    text = replace_after_once(
        text,
        "当前已登记48个 person 组（",
        "Giambattista Marino、",
        "Giambattista Marino、Galileo Galilei、",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,665个 `new` 身份组、4,794条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记47组、81条候选，待登记1,038组、1,097条候选。",
        "当前尚余4,664个 `new` 身份组、4,793条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记48组、82条候选，待登记1,037组、1,096条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Galileo Galilei 跨章身份组登记（2026-10-16）

`cand-1105`（G.csv#12）已映射至 [Galileo Galilei 人物卡](../../04-knowledge/units/persons/galileo-galilei.md)。第4章记其与 Cassiano dal Pozzo 往来及其对 Cigoli 的画家偏好，第3章和第10章另有争议背景及 Lodoli 的阅读偏好。16条直接 S2 端点中11条关系候选留待 S6；本批不新增正式关系、外部核验或 S5 补足。判断和 dry-run/apply 记录见[S4批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_galileo_galilei_batch_20261016.py)。manifest 从1,172增至1,173；累计登记154组、195条候选映射，余4,664组、4,793条。

"""
    return replace_once(
        text,
        "### person：Giambattista Marino 跨章身份组登记（2026-10-16）\n\n",
        batch + "### person：Giambattista Marino 跨章身份组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Galileo Galilei person identity group")
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

    assert len(manifest) == 1172, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered_groups), sum(len(value) for value in registered_groups.values())) == (153, 194)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert not any(row.get("ku_id") for row in groups[GROUP])
    assert alignment_by_id[MEMBERS[0]]["decision"] == "new"
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == "person"
    assert candidate_by_id[MEMBERS[0]]["canonical_name"] == "Galilei, Galileo"
    assert candidate_by_id[MEMBERS[0]]["index_entry_id"] == "G.csv#12"
    assert not (ROOT / REL_PATH).exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == "person" and "galileo galilei" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)

    endpoint_ids, relation_ids = set(), set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if MEMBERS[0] in {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert (len(endpoint_ids), len(relation_ids)) == (16, 11), (len(endpoint_ids), len(relation_ids))
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
    assert (len(planned_registered), sum(len(value) for value in planned_registered.values())) == (154, 195)
    assert (len(planned_groups) - len(planned_registered), sum(len(value) - sum(bool(row.get("ku_id")) for row in value) for value in planned_groups.values())) == (4664, 4793)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, "person")
    card_text, dates = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert dates == 2

    if args.dry_run:
        print(
            "dry-run passed: Galileo Galilei person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} source_quotes={len(RECORD['sources'])} "
            "existing_KU_matches=0 registered_groups_after=154 mapped_candidates_after=195 "
            "pending_groups=4664 pending_candidates=4793 manifest_after=1173; no formal relations added"
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
    print(f"applied: Galileo Galilei person_groups=1 candidates=1 endpoints=16 relation_candidates=11 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
