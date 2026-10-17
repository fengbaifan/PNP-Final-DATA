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
GROUP = "new-person:cassana-niccolo-7c18d86b6b"
MEMBERS = ("cand-0593", "cand-0594")
KU_ID = "units/persons/niccolo-cassana"
REL_PATH = "04-knowledge/units/persons/niccolo-cassana.md"


RECORD = {
    "name_zh": "尼科洛·卡萨纳",
    "name_en": "Niccolò Cassana",
    "description_zh": (
        "哈斯克尔称 Niccolò Cassana 为热那亚画家，并记其自1698年起在威尼斯担任 Grand Prince Ferdinand 的代理人，也为其作画及担任艺术顾问，数次赴佛罗伦萨为王子及家人绘制肖像。第7章提到 Queen Anne 雇用他为肖像画家，但主文所记1714年卒年带问号，注释转述 Ratti 的1713年说法，并称其来英时间及是否卒于英格兰不明；卡片保留这些异文和不确定性。"
    ),
    "description_en": (
        "Haskell identifies Niccolò Cassana as a Genoese artist and says that from 1698 he acted as an agent in Venice for Grand Prince Ferdinand, worked for him as a painter and artistic adviser, and visited Florence several times to paint portraits of the Prince and his household. Chapter 7 mentions Queen Anne employing him as a portrait painter, but its 1714 death date is queried; a note reports Ratti's 1713 date and says that the date of Cassana's arrival in England and whether he died there are unknown. These variants and uncertainties are retained."
    ),
    "context_zh": (
        "C.csv#117“Cassana, Niccolò”列出第7章 p.197、第8章 pp.232–240、第9章 p.265 注及第10章 p.276；C.csv#118 是同一姓名的“as agent for Grand Prince Ferdinand”子目。第7章全名锚点称其为热那亚画家；第8章称他自1698年起在威尼斯为 Ferdinand 任代理，并作为画家和艺术顾问为其工作。S2 记录第8章 OCR 多处省略 Niccolò 重音，既有读页记录说明图像印作 Niccolò；本卡不改写来源 OCR。第7章主文“1714?”与注释转述 Ratti 的1713年及英国行程、死地不明并列，不作裁决。第9、10章另有 Cassana 肖像及估价提及，具体对象与归属保持来源限定。"
    ),
    "context_en": (
        "C.csv#117, “Cassana, Niccolò,” points to Chapter 7 p. 197, Chapter 8 pp. 232–240, a Chapter 9 p. 265 note, and Chapter 10 p. 276; C.csv#118 is the same name's “as agent for Grand Prince Ferdinand” subentry. Chapter 7 gives his full name and calls him a Genoese artist; Chapter 8 says that from 1698 he acted as Ferdinand's agent in Venice and worked for him as a painter and artistic adviser. The S2 reading record notes that the Chapter 8 OCR often omits the accent in Niccolò and that the page image has it; this card does not rewrite the source OCR. The main text's “1714?” and the note's report of Ratti's 1713 date, uncertain English itinerary, and uncertain place of death are retained without resolution. Chapters 9 and 10 also mention Cassana portraits and picture estimates; specific objects and provenance remain source-bounded."
    ),
    "boundary_zh": (
        "本卡对应 S3 组 `new-person:cassana-niccolo-7c18d86b6b` 的两个成员 cand-0593（C.csv#117 主项）和 cand-0594（C.csv#118 代理人子目），共用一张人物 KU。姓名相同，且第8章正文明确以 Niccolo Cassana 指认 Ferdinand 在威尼斯的代理人，子目与主项同组有书内锚点；并非仅据同姓合并。章内 OCR 形式 Niccolo 与打印重音形式 Niccolò 按既有 S2 读页记录处理。死亡年份与英国行程信息冲突，继续待证。17条直接 S2 断言端点中16条标记为关系候选，全部留待 S6；本批不新增正式关系、work/archive KU、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents both members of S3 group `new-person:cassana-niccolo-7c18d86b6b`: cand-0593 (C.csv#117 main entry) and cand-0594 (C.csv#118 agent subentry), mapped to one person KU. They share the same name, and Chapter 8 explicitly names Niccolo Cassana as Ferdinand's agent in Venice, supporting the subentry's grouping with the main entry; the merge is not based on surname alone. The OCR form Niccolo and the printed accented form Niccolò follow the existing S2 reading note. Conflicting death-year and English-itinerary information remains unresolved. Sixteen of 17 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, work or archive KUs, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": (
        "索引规范名为 Cassana, Niccolò。第7章打印文本作 Niccolò，第8–10章 OCR 常作 Niccolo；既有 S2 读页记录指出相关页图像显示重音形式，不更改来源文件。"
    ),
    "type_notes_en": (
        "The index form is Cassana, Niccolò. Chapter 7 prints Niccolò, while the Chapter 8–10 OCR often reads Niccolo; the existing S2 page-reading note records the accented form in the page image, and the source files are not altered."
    ),
    "sources": [
        card_writer.source(
            "7", "197", "07_CHP-7_sec_iv.md", "64",
            "and was doubtless there to greet the Genoese artist Niccolò Cassana whom she employed as her portrait painter until his death in 1714?",
            "第7章称 Queen Anne 雇用热那亚画家 Niccolò Cassana 为肖像画家；句末问号保留对1714年卒年的不确定。",
        ),
        card_writer.source(
            "7", "197 n. 1", "07_CHP-7_sec_iv.md", "108",
            "1 Agnelli, printed at end ofbook after imprimatur. Ratti (Soprani/Ratti, II, p. 15) says that he died in 1713 after refusing an official post as the Queen’s Painter. It is not known just when he came to England or whether he died in this country.",
            "第7章注1转述 Ratti 称 Cassana 于1713年去世，并说明其赴英时间及是否卒于英国不明；此为 Haskell 转引，未独立核阅 Ratti。",
        ),
        card_writer.source(
            "8", "232", "08_CHP-8_sec_ii.md", "252–253",
            "years to Niccolo Cassana, the Genoese artist who acted as his agent in Venice as from\n1698?",
            "第8章称 Niccolo Cassana 是热那亚画家，自1698年起在威尼斯为 Grand Prince Ferdinand 任代理。",
        ),
        card_writer.source(
            "8", "234", "08_CHP-8_sec_ii.md", "285",
            "Niccolo Cassana also worked a good deal for Ferdinand as painter as well as artistic adviser. He visited Florence on various occasions chiefly so as to paint portraits of the Prince and his household, and from time to time he would send pictures from\nVenice.",
            "第8章称 Cassana 为 Ferdinand 作画并担任艺术顾问，曾赴佛罗伦萨绘制王子及家人肖像，也从威尼斯寄画。",
        ),
        card_writer.source(
            "8", "234", "08_CHP-8_sec_ii.md", "287",
            "Cassana also painted history pictures for the Grand Prince, mostly in a light vein—a Bacchanal, a Venus playing with Cupid and so on, though there was also a Conspiracy of Catiline.5",
            "第8章记 Cassana 为 Grand Prince 绘制历史题材作品；作品名称按原文引述，具体对象关系留待 S6。",
        ),
        card_writer.source(
            "10", "276", "10_CHP-10_intro.md", "13",
            "and in 1710 and 1711 he wrote to Lord Dartmouth enclosing estimates of pictures signed by Sebastiano Ricci and Niccolo Cassana—Osti, 1951, p. 119.",
            "第10章记 Christian Cole 于1710、1711年致 Lord Dartmouth 信中附有署为 Sebastiano Ricci 与 Niccolo Cassana 的画作估价；按 Haskell 转述记录。",
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
        "截至 Philip Neri 与 Pietro Liberi 批次，4,818 个当前 `new` 身份组中完成151组，余4,667组；4,988条成员候选中映射191条，余4,797条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记45组、78条候选，待登记1,040组、1,100条候选。",
        "截至 Niccolò Cassana 批次，4,818 个当前 `new` 身份组中完成152组，余4,666组；4,988条成员候选中映射193条，余4,795条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记46组、80条候选，待登记1,039组、1,098条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi 已登记为人物 KU。",
        "Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi、Niccolò Cassana 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Philip Neri 的16条关系候选与 Pietro Liberi 的11条关系候选及其他已登记对象的 S2 关系候选仍待 S6",
        "Philip Neri 的16条关系候选、Pietro Liberi 的11条关系候选与 Niccolò Cassana 的16条关系候选及其他已登记对象的 S2 关系候选仍待 S6",
        "process pending relation candidates",
    )
    batch = """### person：Niccolò Cassana 跨索引身份组登记（2026-10-16）

- cand-0593（C.csv#117 主项）与 cand-0594（C.csv#118，“as agent for Grand Prince Ferdinand”子目）属于 `new-person:cassana-niccolo-7c18d86b6b`，共映射至 `units/persons/niccolo-cassana`。同名与第8章对其威尼斯代理角色的直接说明支持并组；manifest 中没有既有人物 KU。
- 第7章称其为热那亚画家，Queen Anne 肖像画家职位及1714年卒年以问号表达；注1转述 Ratti 的1713年说法，并称来英时间和死地不明。第8章说明他自1698年为 Ferdinand 在威尼斯任代理、兼作画家和艺术顾问；第10章估价信息仅保留 Haskell 的转述。不同年份和不确定项并列，不作外部裁决。
- 17条直接 S2 断言端点中16条为关系候选，均留待 S6；本批不新增正式关系、作品/档案 KU、外部身份记录或 S5 补足。[register_s4_person_niccolo_cassana_batch_20261016.py](register_s4_person_niccolo_cassana_batch_20261016.py) dry-run 核对两条组成员、6处精确原文锚点、端点/关系候选数和登记外键后通过，再 apply 登记一张卡并完成 manifest、accepted.yml 和两条候选映射。manifest 从1,170增至1,171；累计登记152组、193条候选映射，余4,666组、4,795条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def updated_result(text):
    text = replace_once(text, "目前完成151组、映射191条成员候选，余4,667组、4,797条映射。", "目前完成152组、映射193条成员候选，余4,666组、4,795条映射。", "result top S4 counts")
    text = replace_once(
        text,
        "Bonomo Algarotti、Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi 四十三个补充 person 组",
        "Bonomo Algarotti、Donna Olimpia Maidalchini、Philip Neri、Pietro Liberi、Niccolò Cassana 四十四个补充 person 组",
        "result top person names",
    )
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,170 KU；含本轮新增45个 person 组（", "| [KU 登记](../tables/ku-manifest.csv) | 1,171 KU；含本轮新增46个 person 组（", "result manifest count")
    text = replace_once(
        text,
        "Philip Neri、Pietro Liberi、2个 Valmarana 组",
        "Philip Neri、Pietro Liberi、Niccolò Cassana、2个 Valmarana 组",
        "result manifest names",
    )
    text = replace_once(text, "当前已登记45个 person 组（", "当前已登记46个 person 组（", "result current person count")
    text = replace_after_once(
        text,
        "当前已登记46个 person 组（",
        "Pietro Liberi、",
        "Pietro Liberi、Niccolò Cassana、",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,667个 `new` 身份组、4,797条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记45组、78条候选，待登记1,040组、1,100条候选。",
        "当前尚余4,666个 `new` 身份组、4,795条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记46组、80条候选，待登记1,039组、1,098条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Niccolò Cassana 跨索引身份组登记（2026-10-16）

`cand-0593`（C.csv#117 主项）和 `cand-0594`（C.csv#118 代理人子目）共映射至 [Niccolò Cassana 人物卡](../../04-knowledge/units/persons/niccolo-cassana.md)。第8章正文支持其作为 Grand Prince Ferdinand 在威尼斯的代理人，与主项同属一人；manifest 无既有同名 KU。第7章主文“1714?”、注1转述 Ratti 的1713年说法及死地未明均保留待证。17条直接 S2 端点中16条关系候选留待 S6；本批无正式关系、外部身份核验或 S5 补足。过程和 dry-run/apply 依据见[S4批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_niccolo_cassana_batch_20261016.py)。manifest 从1,170增至1,171；累计登记152组、193条候选映射，余4,666组、4,795条。

"""
    return replace_once(
        text,
        "### person：Philip Neri 与 Pietro Liberi 跨章身份组登记（2026-10-16）\n\n",
        batch + "### person：Philip Neri 与 Pietro Liberi 跨章身份组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Niccolò Cassana person identity group")
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

    assert len(manifest) == 1170, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered_groups), sum(len(value) for value in registered_groups.values())) == (151, 191)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert not any(row.get("ku_id") for row in groups[GROUP])
    assert all(alignment_by_id[candidate_id]["decision"] == "new" for candidate_id in MEMBERS)
    assert all(candidate_by_id[candidate_id]["suggested_type"] == "person" for candidate_id in MEMBERS)
    assert all(candidate_by_id[candidate_id]["canonical_name"] == "Cassana, Niccolò" for candidate_id in MEMBERS)
    assert candidate_by_id["cand-0594"]["sub_entry"] == "as agent for Grand Prince Ferdinand"
    assert candidate_by_id["cand-0593"]["sub_entry"] == ""
    assert not (ROOT / REL_PATH).exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == "person" and "cassana" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)

    endpoint_ids, relation_ids = set(), set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if set(MEMBERS) & {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert (len(endpoint_ids), len(relation_ids)) == (17, 16), (len(endpoint_ids), len(relation_ids))
    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for candidate_id in MEMBERS:
        planned_by_id[candidate_id]["ku_id"] = KU_ID
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
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
    assert (len(planned_registered), sum(len(value) for value in planned_registered.values())) == (152, 193)
    assert (len(planned_groups) - len(planned_registered), sum(len(value) - sum(bool(row.get("ku_id")) for row in value) for value in planned_groups.values())) == (4666, 4795)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, "person")
    card_text, dates = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert dates == 2

    if args.dry_run:
        print(
            "dry-run passed: Niccolò Cassana person_group=1 candidate_members=2 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} source_quotes={len(RECORD['sources'])} "
            "existing_KU_matches=0 mapped_to_one_KU=true registered_groups_after=152 mapped_candidates_after=193 "
            "pending_groups=4666 pending_candidates=4795 manifest_after=1171; no formal relations added"
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
    print(f"applied: Niccolò Cassana person_groups=1 candidates=2 endpoints=17 relation_candidates=16 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
