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
GROUP = "new-person:simon-vouet-89e2a49200"
MEMBERS = ("cand-2792", "cand-2793")
KU_ID = "units/persons/simon-vouet"
CARD_PATH = "04-knowledge/units/persons/simon-vouet.md"
RECORD = {
    "name_zh": "西蒙·武埃",
    "name_en": "Simon Vouet",
    "description_zh": (
        "第2章称 Simon Vouet 为 Francesco Barberini 赞助的法国画家之一，并将他与 Caravaggio 的影响及装饰性风格联系起来；Haskell 说他1627年离开罗马时已预示后来带到法国的 grand manner。第4章记他约1614年抵达罗马，是 Cassiano dal Pozzo 首位大规模雇用来创作原创绘画的画家，也是 Cassiano 在罗马最持续支持的画家之一。第4章另称他曾为 Bracciano 公爵夫人 Isabella 画像；该条索引子目指画家本人，不足以识别或登记具体肖像作品。"
    ),
    "description_en": (
        "Chapter 2 identifies Simon Vouet as one of the French artists patronised by Francesco Barberini and discusses Caravaggio's influence and Vouet's decorative manner. Haskell says that by leaving Rome in 1627 Vouet was already foreshadowing the grand manner he later introduced into France. Chapter 4 dates his arrival in Rome to about 1614 and identifies him as the first artist Cassiano dal Pozzo employed on a large scale to produce original paintings, as well as one of Cassiano's most consistent supporters in Rome. Chapter 4 also says he had painted Isabella, Duchess of Bracciano; the index subentry identifies the artist, not an individually identified portrait work."
    ),
    "context_zh": (
        "UVWXYZ.csv#129 为 Simon Vouet 主项，列第2、4、7、8章等页；#130 子目“portrait of Isabella, Duchess of Bracciano”列 p.97。第4章 p.97 正文明确称 Isabella 已由 Simon Vouet 绘制；该子目因此与主项同指画家，未形成第二个人物或可独立识别的肖像 KU。两候选共用一个人物身份组。"
    ),
    "context_en": (
        "UVWXYZ.csv#129 is the main Simon Vouet entry, with pages in Chapters 2, 4, 7, and 8; #130 is the subentry “portrait of Isabella, Duchess of Bracciano,” pointing to p. 97. Chapter 4 p. 97 explicitly says Isabella had already been painted by Simon Vouet. The subentry therefore points to the same artist as the main entry; it neither names a second person nor identifies a discrete portrait KU. Both candidates belong to one person identity group."
    ),
    "boundary_zh": (
        "本卡合并 `cand-2792`（UVWXYZ.csv#129 主项）与 `cand-2793`（#130 肖像子目），对应 S3 组 `new-person:simon-vouet-89e2a49200`。索引子目所述肖像仅用于确认画家身份，不在本批另立作品。14条直接 S2 断言端点全部带关系候选标记，均留待 S6。本批不新增正式关系、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card maps `cand-2792` (main entry UVWXYZ.csv#129) and `cand-2793` (portrait subentry #130) to S3 group `new-person:simon-vouet-89e2a49200`. The portrait subentry identifies the artist and does not create a separate work in this batch. All 14 direct S2 statement endpoints are marked as relation candidates and remain for S6. This batch adds no formal relations, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": "索引规范形式为 Vouet, Simon；正文使用 Simon Vouet、Vouet。中文名为工作音译。",
    "type_notes_en": "The index form is Vouet, Simon; the prose uses Simon Vouet and Vouet.",
    "sources": [
        card_writer.source(
            "2", "46", "02_CHP-2_sec_iv.md", "33",
            "He patronised other French artists, Simon Vouet and Valentin",
            "第2章称 Francesco Barberini 赞助 Simon Vouet 等法国画家。",
        ),
        card_writer.source(
            "2", "46", "02_CHP-2_sec_iv.md", "35",
            "Vouet’s talent was by nature more decorative and by the time he left Rome in 1627 he was already foreshadowing the grand manner which he then introduced into France.",
            "第2章评价其装饰性风格，并记其离开罗马及后来在法国引入 grand manner 的叙述。",
        ),
        card_writer.source(
            "4", "102", "04_CHP-4_sec_ii.md", "37",
            "The first artist whom he employed on a large scale to produce original painting as opposed to illustrations of antiquity or natural history was the Frenchman Simon",
            "第4章称 Vouet 是 Cassiano dal Pozzo 首位大规模雇用创作原创绘画的画家。",
        ),
        card_writer.source(
            "4", "102", "04_CHP-4_sec_ii.md", "38",
            "Vouet, who had arrived in Rome in about 16142 and had quickly acquired a reputation as a follower of Caravaggio",
            "第4章记其约1614年抵达罗马并因戏剧性场景画而获得追随 Caravaggio 的声誉。",
        ),
        card_writer.source(
            "4", "97", "04_CHP-4_sec_i.md", "28",
            "his wife Isabella3 who had already been painted by Simon Vouet",
            "第4章确认 Isabella 曾由 Simon Vouet 绘制；所指具体肖像未识别。",
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
        "截至 Antonio degli Effetti 批次，4,819 个当前 `new` 身份组中完成161组，余4,658组；",
        "截至 Simon Vouet 批次，4,819 个当前 `new` 身份组中完成162组，余4,657组；",
        "current S4 group counts",
    )
    text = replace_once(
        text,
        "person 类型1,086组、1,178条候选，已登记55组、92条候选，待登记1,031组、1,086条候选。",
        "person 类型1,086组、1,178条候选，已登记56组、94条候选，待登记1,030组、1,084条候选。",
        "current S4 person group counts",
    )
    batch = """### person：Simon Vouet 双候选组登记（2026-10-16）

- `cand-2792`（UVWXYZ.csv#129 主项）与 `cand-2793`（#130 “portrait of Isabella, Duchess of Bracciano”子目）共同映射至 `units/persons/simon-vouet`。第4章 p.97 正文明确称 Isabella 已由 Simon Vouet 绘制；子目指画家，不指一位新人物或可识别的肖像作品。
- 第2章 p.46 与第4章 pp.97、102 提供赞助、风格、罗马活动及肖像语境。14条直接 S2 端点全部为关系候选，留待 S6；本批不新增肖像作品 KU、正式关系、外部身份记录或 S5 补足。
- 批次脚本 dry-run 核对两条组成员、5处原文锚点、端点和外键后通过。manifest 从1,180增至1,181；累计登记162组、207条候选映射，余4,657组、4,781条。person 类型已登记56组、94条候选映射，余1,030组、1,084条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "目前完成161组、映射205条成员候选，余4,658组、4,783条映射。",
        "目前完成162组、映射207条成员候选，余4,657组、4,781条映射。",
        "result current S4 registration counts",
    )
    text = replace_once(text, "1,180 KU；含本轮新增55个 person 组（", "1,181 KU；含本轮新增56个 person 组（", "result manifest count")
    text = replace_once(
        text,
        "Antonio degli Effetti、2个 Valmarana 组）",
        "Antonio degli Effetti、Simon Vouet、2个 Valmarana 组）",
        "result manifest names",
    )
    text = replace_once(text, "当前已登记55个 person 组（", "当前已登记56个 person 组（", "result current person groups")
    text = replace_once(
        text,
        "Antonio degli Effetti、Valmarana 跨章2组）",
        "Antonio degli Effetti、Simon Vouet、Valmarana 跨章2组）",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,658个 `new` 身份组、4,783条成员候选映射；",
        "当前尚余4,657个 `new` 身份组、4,781条成员候选映射；",
        "result current unregistered group count",
    )
    text = replace_once(
        text,
        "person 类型1,086组、1,178条候选，已登记55组、92条候选，待登记1,031组、1,086条候选。",
        "person 类型1,086组、1,178条候选，已登记56组、94条候选，待登记1,030组、1,084条候选。",
        "result current person registration counts",
    )
    batch = """### person：Simon Vouet 双候选 S4 登记（2026-10-16）

`cand-2792`（UVWXYZ.csv#129 主项）与 `cand-2793`（#130 肖像子目）已共同登记为[Simon Vouet 人物卡](../../04-knowledge/units/persons/simon-vouet.md)。第4章 p.97 正文确认 Isabella 曾由 Vouet 绘制，说明索引子目指画家本人；具体肖像未识别。14条直接 S2 断言端点均为关系候选，留待 S6；未新增肖像作品 KU、正式关系、外部身份记录或 S5 补足。manifest 从1,180增至1,181；累计登记162组、207条映射，余4,657组、4,781条。

"""
    return replace_once(text, "### person：Antonio degli Effetti", batch + "### person：Antonio degli Effetti", "result S4 batch insertion")


def main():
    parser = argparse.ArgumentParser(description="Register Simon Vouet's main index entry and portrait subentry as one person KU")
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
    assert len(manifest) == 1180, f"unexpected manifest size: {len(manifest)}"
    for candidate_id in MEMBERS:
        candidate = candidate_by_id[candidate_id]
        alignment = alignment_by_id[candidate_id]
        assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == GROUP
    assert candidate_by_id["cand-2792"]["index_entry_id"] == "UVWXYZ.csv#129"
    assert candidate_by_id["cand-2793"]["index_entry_id"] == "UVWXYZ.csv#130"
    assert candidate_by_id["cand-2793"]["sub_entry"] == "portrait of Isabella, Duchess of Bracciano"
    assert not any(row["type"] == KIND and "simon vouet" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)
    assert not (ROOT / CARD_PATH).exists(), CARD_PATH
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") in MEMBERS or statement.get("object_candidate_id") in MEMBERS:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert (len(endpoints), len(relation_endpoints)) == (14, 14), (len(endpoints), len(relation_endpoints))

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
    assert (len(new_rows), len(groups)) == (4988, 4819)
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (161, 205)
    for group, rows in registered_groups.items():
        assert len(rows) == len(groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    registered_person_groups = {
        group: rows for group, rows in registered_groups.items()
        if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    assert (len(registered_person_groups), sum(map(len, registered_person_groups.values()))) == (55, 92)
    assert len(groups[GROUP]) == 2

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
    assert len(planned_manifest) == 1181

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
            "dry-run passed: group=1 candidates=2 endpoints=14 relation_candidates=14 "
            "registered_groups_after=162 mapped_candidates_after=207 manifest_after=1181"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=2 endpoints=14 relation_candidates=14 "
        "manifest=1181 registered_groups=162 mapped_candidates=207"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
