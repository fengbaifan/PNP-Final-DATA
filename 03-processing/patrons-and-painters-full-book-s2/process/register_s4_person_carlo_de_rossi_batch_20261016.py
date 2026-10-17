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
GROUP = "new-person:carlo-de-rossi-01b009d0b8"
MEMBER = "cand-2269"
KU_ID = "units/persons/carlo-de-rossi"
CARD_PATH = "04-knowledge/units/persons/carlo-de-rossi.md"
RECORD = {
    "name_zh": "卡洛·德·罗西",
    "name_en": "Carlo de' Rossi",
    "description_zh": (
        "第5章称 Carlo de’ Rossi 为 Salvator Rosa 在罗马的主要赞助人和银行家，也称其为有才华的音乐家、作曲家 Luigi 的兄弟。Haskell 记述 Rosa 曾将4000 scudi存入其处，De’ Rossi 按6%付息，并建立了 Rosa 作品的私人收藏；第6、7章继续使用其姓名叙述作品和收藏语境。所有内容均限于书内记载。"
    ),
    "description_en": (
        "Chapter 5 identifies Carlo de’ Rossi as Salvator Rosa's principal patron in Rome and his banker, and calls him a talented musician and brother of the composer Luigi. Haskell reports that Rosa deposited 4,000 scudi with him, that De’ Rossi paid six per cent interest, and that he assembled a private collection of Rosa's works. Chapters 6 and 7 refer to him again in accounts of a painting and a collection; the card stays within the book's reports."
    ),
    "context_zh": (
        "Q-R.csv#197“Rossi, Carlo de’”列第5章 pp.143–144，子目为“and Salvator Rosa”。第5章 p.143 称 Carlo de’ Rossi 是 Rosa 的银行家、主要赞助人和音乐家，并说明他是作曲家 Luigi 的兄弟；p.144 描述其收藏 Rosa 作品的画廊和房间。第6章 p.153 再记 Rosa 为 Carlo de’ Rossi 绘制的《Fortune》，第7章 p.190 则以 Carlo de Rossi 指其收藏。该索引子目不是其姓名组成部分；关于资金、赞助、友谊、作品与收藏的关系仍由 S6 逐项裁决。"
    ),
    "context_en": (
        "Q-R.csv#197, “Rossi, Carlo de’,” lists Chapter 5 pp. 143–144 with the sub-entry “and Salvator Rosa.” Page 143 names Carlo de’ Rossi as Rosa's banker and principal patron in Rome, describes him as a musician, and identifies him as composer Luigi's brother; p. 144 describes the gallery and rooms in which he collected Rosa's works. Chapter 6 p. 153 mentions a Fortune painted by Rosa for Carlo de’ Rossi, and Chapter 7 p. 190 calls him Carlo de Rossi when describing a visit to his collection. The index sub-entry is not part of his name; relations involving money, patronage, friendship, works, and collecting remain for S6 adjudication."
    ),
    "boundary_zh": (
        "本卡对应唯一候选 `cand-2269`，属于 S3 组 `new-person:carlo-de-rossi-01b009d0b8`。索引以姓名和 Salvator Rosa 子目定位本人物；不与 Salvator Rosa 合并。正文中 De’ Rossi／Carlo de Rossi 的变体按上下文对应此人物；现有 manifest 无同名人物 KU。16条直接 S2 断言端点中14条为关系候选，均待 S6；本批不新增正式关系、作品/archive KU、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card represents the sole candidate `cand-2269` in S3 group `new-person:carlo-de-rossi-01b009d0b8`. The index names Carlo de’ Rossi and adds Salvator Rosa as a locating sub-entry; the two people are not merged. De’ Rossi and Carlo de Rossi are treated as contextual forms of the same person in the cited passages, and no existing person KU in the manifest matches him. Fourteen of 16 direct S2 statement endpoints are relation candidates and remain for S6. This batch adds no formal relations, work or archive KUs, external identity record, or S5 enrichment."
    ),
    "type_notes_zh": "索引规范形式为 Rossi, Carlo de’；正文作 Carlo de’ Rossi、De’ Rossi 及 Carlo de Rossi。中文名为工作音译。",
    "type_notes_en": "The index form is Rossi, Carlo de’; the prose uses Carlo de’ Rossi, De’ Rossi, and Carlo de Rossi.",
    "sources": [
        card_writer.source(
            "5", "143", "05_CHP-5_sec_iv.md", "21",
            "His greatest patron in Rome was his banker, Carlo de’ Rossi,",
            "第5章明确提供 Carlo de’ Rossi 的姓名，并称其为 Rosa 在罗马的主要赞助人和银行家。",
        ),
        card_writer.source(
            "5", "143", "05_CHP-5_sec_iv.md", "21",
            "brother of the famous composer Luigi and himself a talented musician.",
            "第5章称 Carlo de’ Rossi 是作曲家 Luigi 的兄弟并为有才华的音乐家；不扩展其家族背景。",
        ),
        card_writer.source(
            "5", "144", "05_CHP-5_sec_iv.md", "24",
            "Before that, however, De’ Rossi had assembled what amounted to a private museum of Rosa’s works consisting of a large gallery and several small rooms.",
            "第5章描述 De’ Rossi 收藏 Rosa 作品的私人画廊和房间。",
        ),
        card_writer.source(
            "6", "153", "06_CHP-6_sec_i.md", "89",
            "a picture painted by Salvator Rosa for Carlo de’ Rossi (Plate 24).",
            "第6章以另一页码和完整姓名再次提及 Carlo de’ Rossi；作品关系留待 S6。",
        ),
        card_writer.source(
            "7", "190", "07_CHP-7_sec_i.md", "265",
            "Salvator Rosa’s friend Carlo de Rossi",
            "第7章以 Carlo de Rossi 指 Salvator Rosa 的朋友，并叙述访问其收藏；保留原书异体拼写。",
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
        "截至 Francesco Bracciolini 批次，4,818 个当前 `new` 身份组中完成157组，余4,661组；4,988条成员候选中映射201条，余4,787条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记51组、88条候选，待登记1,034组、1,090条候选。",
        "截至 Carlo de' Rossi 批次，4,818 个当前 `new` 身份组中完成158组，余4,660组；4,988条成员候选中映射202条，余4,786条。family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记52组、89条候选，待登记1,033组、1,089条候选。",
        "process current S4 counts",
    )
    text = replace_once(
        text,
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini 已登记为人物 KU。",
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini、Carlo de' Rossi 已登记为人物 KU。",
        "process registered person names",
    )
    text = replace_once(
        text,
        "Cardinal Giovan Francesco Negroni 的15条与 Francesco Bracciolini 的15条关系候选",
        "Cardinal Giovan Francesco Negroni 的15条、Francesco Bracciolini 的15条与 Carlo de' Rossi 的14条关系候选",
        "process pending relation candidates",
    )
    batch = """### person：Carlo de’ Rossi 跨章直接端点组登记（2026-10-16）

- `cand-2269`（Q-R.csv#197，pp.143–144；子目“and Salvator Rosa”）属于 `new-person:carlo-de-rossi-01b009d0b8`，登记为 `units/persons/carlo-de-rossi`。现有 manifest 无同名人物 KU；该索引子目只用于定位，不与 Salvator Rosa 合并。
- 第5章 p.143 提供全名，称其为 Rosa 的银行家、罗马主要赞助人、音乐家及作曲家 Luigi 的兄弟；p.144 记其收藏 Rosa 作品。第6章 p.153 和第7章 p.190 再以 Carlo de’ Rossi／Carlo de Rossi 指其人。
- 16条直接 S2 断言端点中14条为关系候选，均留待 S6；本批不新增正式关系、作品/archive KU、外部身份记录或 S5 补足。[register_s4_person_carlo_de_rossi_batch_20261016.py](register_s4_person_carlo_de_rossi_batch_20261016.py) dry-run 核对组成员、5处原文引文、端点数和登记外键后通过，再 apply 更新卡片、manifest、accepted.yml 与候选映射。manifest 从1,176增至1,177；累计登记158组、202条候选映射，余4,660组、4,786条。

"""
    return replace_once(text, "### 登记进度与后续\n\n", batch + "### 登记进度与后续\n\n", "process S4 batch insertion")


def update_result(text):
    text = replace_once(
        text,
        "目前完成157组、映射201条成员候选，余4,661组、4,787条映射。",
        "目前完成158组、映射202条成员候选，余4,660组、4,786条映射。",
        "result top S4 counts",
    )
    text = replace_once(
        text,
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini 四十九个补充 person 组",
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini、Carlo de' Rossi 五十个补充 person 组",
        "result top person names",
    )
    text = replace_once(text, "1,176 KU；含本轮新增51个 person 组（", "1,177 KU；含本轮新增52个 person 组（", "result manifest count")
    text = replace_once(
        text,
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini、2个 Valmarana 组）",
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini、Carlo de' Rossi、2个 Valmarana 组）",
        "result manifest names",
    )
    text = replace_once(text, "当前已登记51个 person 组（", "当前已登记52个 person 组（", "result current person count")
    text = replace_once(
        text,
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini、Valmarana 跨章2组）",
        "Cardinal Giovan Francesco Negroni、Francesco Bracciolini、Carlo de' Rossi、Valmarana 跨章2组）",
        "result current person names",
    )
    text = replace_once(
        text,
        "当前尚余4,661个 `new` 身份组、4,787条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记51组、88条候选，待登记1,034组、1,090条候选。",
        "当前尚余4,660个 `new` 身份组、4,786条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,085组、1,178条候选，已登记52组、89条候选，待登记1,033组、1,089条候选。",
        "result current S4 type counts",
    )
    batch = """### person：Carlo de’ Rossi 跨章直接端点组登记（2026-10-16）

`cand-2269`（Q-R.csv#197）已登记为[Carlo de’ Rossi 人物卡](../../04-knowledge/units/persons/carlo-de-rossi.md)。第5章 pp.143–144 给出姓名、银行家及主要赞助人身份，并记其与 Rosa 的资金和收藏语境；第6章 p.153、第7章 p.190 再次出现 Carlo de’ Rossi／Carlo de Rossi。索引“and Salvator Rosa”是定位子目，不是姓名或合并依据。16条直接 S2 端点中14条关系候选留待 S6；本批未新增正式关系、work/archive KU、外部身份记录或 S5 补足。批次脚本核对5处原文引文、S3 决定和映射。manifest 从1,176增至1,177；累计登记158组、202条候选映射，余4,660组、4,786条。

"""
    return replace_once(
        text,
        "### person：Francesco Bracciolini 双索引候选组登记（2026-10-16）\n\n",
        batch + "### person：Francesco Bracciolini 双索引候选组登记（2026-10-16）\n\n",
        "result S4 batch insertion",
    )


def main():
    parser = argparse.ArgumentParser(description="Register Carlo de' Rossi's person identity group in S4")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == MEMBER)
    alignment = next(row for row in alignments if row.get("candidate_id") == MEMBER and not row.get("external_source"))
    assert len(manifest) == 1176, f"unexpected manifest size: {len(manifest)}"
    assert candidate["suggested_type"] == KIND and candidate["status"] == "open"
    assert candidate["index_entry_id"] == "Q-R.csv#197" and candidate["index_page_range"] == "143, 144"
    assert alignment["decision"] == "new" and not alignment.get("ku_id") and get_group(alignment["resolution_note"]) == GROUP
    assert not any(row["type"] == KIND and "carlo de" in (row["canonical_name"] + " " + row["name_en"]).casefold() for row in manifest)
    assert not (ROOT / CARD_PATH).exists(), CARD_PATH
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == CARD_PATH for row in manifest)

    endpoints = []
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if statement.get("subject_candidate_id") == MEMBER or statement.get("object_candidate_id") == MEMBER:
                endpoints.append(statement)
    relation_endpoints = [row for row in endpoints if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert (len(endpoints), len(relation_endpoints)) == (16, 14), (len(endpoints), len(relation_endpoints))

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
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (157, 201)
    for group, rows in registered_groups.items():
        assert len(rows) == len(new_groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    registered_person_groups = {
        group: rows for group, rows in registered_groups.items()
        if all(candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND for row in rows)
    }
    assert (len(registered_person_groups), sum(map(len, registered_person_groups.values()))) == (51, 88)

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
    assert len(planned_manifest) == 1177

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
            "dry-run passed: group=1 candidates=1 endpoints=16 relation_candidates=14 "
            "registered_groups_after=158 mapped_candidates_after=202 manifest_after=1177"
        )
        return 0

    (ROOT / CARD_PATH).write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(MANIFEST_PATH, manifest_fields, planned_manifest)
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    ACCEPTED_PATH.write_text(planned_accepted, encoding="utf-8-sig", newline="")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: group=1 candidates=1 endpoints=16 relation_candidates=14 "
        "manifest=1177 registered_groups=158 mapped_candidates=202"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
