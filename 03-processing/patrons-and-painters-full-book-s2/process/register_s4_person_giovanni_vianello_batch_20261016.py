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
GROUP = "new-person:giovanni-vianello-01f3203923"
MEMBERS = ("cand-2764",)
KU_ID = "units/persons/giovanni-vianello"
REL_PATH = "04-knowledge/units/persons/giovanni-vianello.md"


RECORD = {
    "name_zh": "乔瓦尼·维亚内洛",
    "name_en": "Giovanni Vianello",
    "description_zh": (
        "哈斯克尔第16章称 Dr Giovanni Vianello 为 Chioggia Cathedral 的 canon，并将他可能属于 Sasso 与 della Lena 的交往圈明确保留为推测。"
        "书中记其于1793年刊行 Rosalba 日记版本、拥有200余幅绘画，并在1790年出版绘画目录；作者同时说其是否为画商尚不确定。第16章还记录 Vianello 收藏的 Francesco Guardi 作品及其对 Guardi 风格的评价。上述内容均按哈斯克尔的叙述、判断和限定登记。"
    ),
    "description_en": (
        "In Chapter 16, Haskell identifies Dr Giovanni Vianello as a canon of Chioggia Cathedral and qualifies his possible membership in the circle of Sasso and della Lena as uncertain. "
        "The book says he brought out an edition of Rosalba's journal in 1793, owned over 200 pictures, and published a catalogue of his paintings in 1790; Haskell explicitly leaves uncertain whether he was a dealer. Chapter 16 also records works by Francesco Guardi in Vianello's collection and his assessment of Guardi's style. These details retain Haskell's narrative, judgements, and qualifications."
    ),
    "context_zh": (
        "UVWXYZ.csv#100 将 Vianello, Dr Giovanni 列于印刷页376。第16章 p.376 的段落以 Dr Giovanni Vianello 为全名，称其为 Chioggia Cathedral 的 canon，随后连续叙述 Rosalba 日记版本、绘画目录、收藏规模与 Guardi 作品。来源 OCR 将 ‘Giovanni’ 与 ‘Vianello’ 连写；索引候选保留分开的规范词头。第13章脚注另以姓氏 Vianello 提及 Rosalba 日记首位编辑，但本卡不据该姓氏单独扩展身份或书目信息。"
    ),
    "context_en": (
        "UVWXYZ.csv#100 lists Vianello, Dr Giovanni at printed p. 376. The Chapter 16 passage gives the full form Dr Giovanni Vianello, identifies him as a canon of Chioggia Cathedral, and continues with the Rosalba journal edition, picture catalogue, collection, and Guardi works. The OCR joins ‘Giovanni’ and ‘Vianello’; the index candidate preserves the spaced name form. A Chapter 13 footnote also refers to a first editor of Rosalba's journal by the surname Vianello, but this card does not use that surname alone to expand identity or bibliographic claims."
    ),
    "boundary_zh": (
        "本卡对应 S3 组 `new-person:giovanni-vianello-01f3203923` 中的唯一候选 cand-2764。第16章 p.376 提供全名及人物语境；‘可能属于 Sasso 与 della Lena 的圈子’保持原文的推测语气，画商身份明确记为不确定。第13章脚注的姓氏提及不单独作为新增身份依据。20条直接 S2 断言端点中8条标记为关系候选，全部留待 S6；本批不登记正式关系、不扩建作品或档案 KU，不作外部核验或 S5 补足。中文名为工作音译。"
    ),
    "boundary_en": (
        "This card represents the sole candidate cand-2764 in S3 group `new-person:giovanni-vianello-01f3203923`. Chapter 16 p. 376 supplies the full name and person context. The statement that he may have belonged to the circle of Sasso and della Lena retains its hedge, and dealer status remains explicitly uncertain. The Chapter 13 surname-only footnote is not used by itself as an additional identity basis. Eight of 20 direct S2 statement endpoints are marked as relation candidates and remain for S6. This batch adds no formal relations, work or archive KU, external verification, or S5 enrichment. The Chinese display name is a working transliteration."
    ),
    "type_notes_zh": (
        "索引规范名为 Vianello, Dr Giovanni；第16章 OCR 写作 Dr GiovanniVianello，词间空格按索引分词显示，未据此修订来源文件。职业身份按原书称其为 Chioggia Cathedral 的 canon；是否为画商不确定。"
    ),
    "type_notes_en": (
        "The index form is Vianello, Dr Giovanni. Chapter 16 OCR reads Dr GiovanniVianello; the spacing in the display name follows the index and the source file has not been edited. The book calls him a canon of Chioggia Cathedral and says dealer status is uncertain."
    ),
    "sources": [
        card_writer.source(
            "16", "376", "16_CHP-16_intro.md", "39",
            "a canon ofChioggia Cathedral, Dr GiovanniVianello.1",
            "第16章称 Dr Giovanni Vianello 为 Chioggia Cathedral 的 canon；OCR 将词间空格连写，姓名显示依索引候选分词。",
            "来源 OCR 连写 ‘ofChioggia’ 与 ‘GiovanniVianello’；本批保留原文，不作来源文本校改。",
        ),
        card_writer.source(
            "16", "376", "16_CHP-16_intro.md", "40–41",
            "he brought out in 1793 of Rosalba’s journal.",
            "第16章提到 Vianello 于1793年刊行 Rosalba 日记版本，并转述 Haskell 对其学术姿态的评价。",
        ),
        card_writer.source(
            "16", "376", "16_CHP-16_intro.md", "41",
            "It is not certain whether or not he was a dealer, but the publication of a catalogue of his paintings in 1790, some three years before his death, strongly suggests that he was by then willing to dispose of them.",
            "第16章明确说其是否为画商不确定，并以1790年绘画目录推断他当时可能准备出售藏画；推断仍归于 Haskell。",
        ),
        card_writer.source(
            "16", "376", "16_CHP-16_intro.md", "41",
            "He owned over 200 pictures, the vast majority of which were Venetian of the seventeenth and eighteenth centuries.",
            "第16章称 Vianello 拥有200余幅绘画，绝大多数为17、18世纪威尼斯作品。",
        ),
        card_writer.source(
            "16", "376", "16_CHP-16_intro.md", "42",
            "Vianello also owned three works by Francesco Guardi—two paintings and a drawing—but his appreciation of this artist was greater than such a small number would suggest.",
            "第16章称其收藏三件 Francesco Guardi 作品（两幅画和一幅素描），并评价他对 Guardi 的欣赏超过藏品数量所显示的程度。",
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
        "截至 Giustiniana Wynne-Rosenberg 批次，4,819 个当前 `new` 身份组中完成146组，余4,673组；4,989条成员候选中映射186条，余4,803条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记40组、73条候选，待登记1,046组、1,106条候选。",
        "截至 Giovanni Vianello 批次，4,819 个当前 `new` 身份组中完成147组，余4,672组；4,989条成员候选中映射187条，余4,802条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记41组、74条候选，待登记1,045组、1,105条候选。",
        "process S4 current counts",
    )
    text = replace_once(
        text,
        "Pierre Crozat、Alessandro Marchesini、Marcantonio Franceschini、Giustiniana Wynne-Rosenberg 已登记为人物 KU。",
        "Pierre Crozat、Alessandro Marchesini、Marcantonio Franceschini、Giustiniana Wynne-Rosenberg、Giovanni Vianello 已登记为人物 KU。",
        "process registered person list",
    )
    text = replace_once(
        text,
        "Giustiniana Wynne-Rosenberg 的16条及其他已登记对象",
        "Giustiniana Wynne-Rosenberg 的16条、Giovanni Vianello 的8条及其他已登记对象",
        "process pending S6 list",
    )
    batch = """### person：Giovanni Vianello 直接端点登记（2026-10-16）

- `cand-2764`（UVWXYZ.csv#100，索引名 Vianello, Dr Giovanni）属于 `new-person:giovanni-vianello-01f3203923`，登记为 `units/persons/giovanni-vianello`。第16章 p.376 提供全名、Chioggia Cathedral canon 身份及收藏叙述；OCR 的连写保留在引文中，显示姓名按索引分词。第13章脚注另有姓氏 Vianello 的书内提及，但本卡不据该姓氏单独扩展身份或书目信息。
- 卡片保留 Haskell 对可能圈层成员身份、学术姿态、画商身份和藏品处置的限定；20条直接 S2 断言端点中8条为关系候选，均待 S6。本批未新增正式关系、作品/档案 KU、外部身份记录或 S5 补足。
- [register_s4_person_giovanni_vianello_batch_20261016.py](register_s4_person_giovanni_vianello_batch_20261016.py) dry-run 核对单候选组、5处精确原文锚点、20条端点/8条关系候选、既有人物 KU 边界和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,165增至1,166；累计登记147组、187条候选映射，余4,672组、4,802条候选。

"""
    return replace_once(text, "### 登记进度与后续\n", batch + "### 登记进度与后续\n", "process Vianello batch log")


def updated_result(text):
    lines = text.splitlines()
    status_ids = [i for i, line in enumerate(lines) if line.startswith("**当前状态：全书 S2 语义处理已完成")]
    assert len(status_ids) == 1, f"result status lines={len(status_ids)}"
    i = status_ids[0]
    line = replace_once(
        lines[i],
        "目前完成146组、映射186条成员候选，余4,673组、4,803条映射",
        "目前完成147组、映射187条成员候选，余4,672组、4,802条映射",
        "result S4 status counts",
    )
    line = replace_once(
        line,
        "Giustiniana Wynne-Rosenberg 三十八个补充 person 组",
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello 三十九个补充 person 组",
        "result S4 registered person names",
    )
    lines[i] = line
    text = "\n".join(lines) + "\n"
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,165 KU；含本轮新增40个 person 组（",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,166 KU；含本轮新增41个 person 组（",
        "result KU manifest table",
    )
    text = replace_once(
        text,
        "Giustiniana Wynne-Rosenberg、2个 Valmarana 组",
        "Giustiniana Wynne-Rosenberg、Giovanni Vianello、2个 Valmarana 组",
        "result KU registered names table",
    )
    text = replace_once(
        text,
        "当前尚余4,673个 `new` 身份组、4,803条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记40组、73条候选，待登记1,046组、1,106条候选。",
        "当前尚余4,672个 `new` 身份组、4,802条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记41组、74条候选，待登记1,045组、1,105条候选。",
        "result current S4 type counts",
    )
    text = replace_once(text, "当前已登记40个 person 组（", "当前已登记41个 person 组（", "result person summary count")
    text = replace_once(
        text,
        "Marcantonio Franceschini、Giustiniana Wynne-Rosenberg、Valmarana 跨章2组",
        "Marcantonio Franceschini、Giustiniana Wynne-Rosenberg、Giovanni Vianello、Valmarana 跨章2组",
        "result person summary names",
    )
    result_batch = """### person：Giovanni Vianello 直接端点登记（2026-10-16）

`cand-2764`（UVWXYZ.csv#100）已映射至 [Giovanni Vianello 人物卡](../../04-knowledge/units/persons/giovanni-vianello.md)。第16章 p.376 明称 Dr Giovanni Vianello 为 Chioggia Cathedral canon，并叙述其 Rosalba 日记版本和绘画收藏；第13章脚注的 Vianello 姓氏提及未单独扩展为身份事实。20条直接 S2 端点中8条为关系候选，全部留待 S6；可能圈层成员身份及画商身份按原文保留不确定。本批未新增正式关系、作品/档案 KU、外部身份记录或 S5 补足。依据与 dry-run/apply 记录见[人物卡](../../04-knowledge/units/persons/giovanni-vianello.md)和[S4 批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_giovanni_vianello_batch_20261016.py)。manifest 从1,165增至1,166；累计登记147组、187条候选映射，余4,672组、4,802条。

"""
    return replace_once(
        text,
        "### person：Giustiniana Wynne-Rosenberg 跨章身份组登记（2026-10-16）\n\n",
        result_batch + "### person：Giustiniana Wynne-Rosenberg 跨章身份组登记（2026-10-16）\n\n",
        "result Vianello batch section",
    )


def main():
    parser = argparse.ArgumentParser(description="Register the Giovanni Vianello person identity group")
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

    assert len(manifest) == 1165, f"unexpected manifest count: {len(manifest)}"
    counts = Counter(row["decision"] for row in current)
    assert counts == Counter({"same": 1697, "new": 4989, "undecided": 5614, "excluded": 97, "conflict": 7}), counts
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
    assert (len(groups), sum(map(len, groups.values()))) == (4819, 4989)
    assert (len(registered_groups), sum(len(v) for v in registered_groups.values())) == (146, 186)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])
    assert alignment_by_id[MEMBERS[0]]["decision"] == "new"
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == KIND
    assert candidate_by_id[MEMBERS[0]]["canonical_name"] == "Vianello, Dr Giovanni"
    assert not candidate_by_id[MEMBERS[0]]["sub_entry"]

    card_path = ROOT / REL_PATH
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND
        and "giovanni vianello" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(endpoint_ids) == 20 and len(relation_ids) == 8, (len(endpoint_ids), len(relation_ids))
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
    assert (len(planned_registered), sum(len(v) for v in planned_registered.values())) == (147, 187)
    assert (len(planned_groups) - len(planned_registered), sum(len(v) - sum(bool(r.get("ku_id")) for r in v) for v in planned_groups.values())) == (4672, 4802)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert date_count == 2

    if args.dry_run:
        print(
            "dry-run passed: Giovanni Vianello person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "source_quotes=5 registered_groups_after=147 mapped_candidates_after=187 "
            "pending_groups=4672 pending_candidates=4802 manifest_after=1166; "
            "surname-only Ch. 13 footnote not used to expand identity; no formal relations added"
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
    print(f"applied: Giovanni Vianello person_groups=1 candidates=1 endpoints=20 relation_candidates=8 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
