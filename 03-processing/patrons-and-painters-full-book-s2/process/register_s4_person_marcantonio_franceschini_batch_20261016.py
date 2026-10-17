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
UNITS = ROOT / "04-knowledge" / "units"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
KIND = "person"
GROUP = "new-person:franceschini-marcantonio-12371601a9"
MEMBERS = ("cand-1069", "cand-1070")
KU_ID = "units/persons/marcantonio-franceschini"
REL_PATH = "04-knowledge/units/persons/marcantonio-franceschini.md"


RECORD = {
    "name_zh": "马尔坎托尼奥·弗兰切斯基尼",
    "name_en": "Marcantonio Franceschini",
    "description_zh": (
        "哈斯克尔称 Marcantonio Franceschini 为博洛尼亚画家，记述他是 Cignani 的学生、受 Liechtenstein 家族大量委托，并在 Conti 收藏的委托过程中提供画家意见和题材建议。"
        "第19章附录把 Conti 的委托文书与 Franceschini 及 Felice Torelli 联系起来；书信及档案材料仅按本书的刊载和转述范围记录。"
    ),
    "description_en": (
        "Haskell identifies Marcantonio Franceschini as a Bolognese painter and Cignani's pupil, records extensive commissions from the Liechtenstein family, and describes his advice and subject proposals in the commission process for Conti's collection. "
        "The Chapter 19 appendix connects Conti commission documents with Franceschini and Felice Torelli; letters and archival materials are recorded only within the book's presentation and reporting."
    ),
    "context_zh": (
        "F.csv#84 人物主项收录第7、8、10章页码；F.csv#85 的“letters relating to commission from Stefano Conti”子目指向第19章 p.389。第7章 p.194 记 Liechtenstein 家族向其订购42幅画，并引 Prince of Liechtenstein 将题材交由画家决定的信。"
        "第8章 pp.220、223、227 连续叙述委员会接洽 Franceschini、Ruffo 的委托及其致 Conti 的题材意见；第19章附录列出相关委托文书和1705年致 Alessandro Marchesini 的信。原档案、书信及被引研究未在本批独立查阅。"
    ),
    "context_en": (
        "F.csv#84 is the person entry for Chapters 7, 8, and 10; F.csv#85, “letters relating to commission from Stefano Conti,” points to Chapter 19 p. 389. "
        "Chapter 7 p. 194 records forty-two paintings ordered by the Liechtenstein family and quotes a Prince of Liechtenstein leaving the subject to the painter's taste. "
        "Chapter 8 pp. 220, 223, and 227 follows the committee's approach to Franceschini, Ruffo's commissions, and Franceschini's subject advice to Conti; the Chapter 19 appendix lists related commission documents and a 1705 letter to Alessandro Marchesini. "
        "The original records, letters, and cited scholarship were not independently consulted in this batch."
    ),
    "boundary_zh": (
        "本卡只指原书称作 Marcantonio Franceschini 的博洛尼亚画家；F.csv#84 与 #85 同属该人，#85 是书信/委托语境子目而非第二位人物。与既有人物 Baldassarre Franceschini（units/persons/baldassare-franceschini）按全名区分。"
        "委托、通信、作品及档案材料不因人物卡登记而成为正式关系或同一 KU。18条直接 S2 断言端点中16条标记为关系候选，全部待 S6 逐项审查；本批未新增正式关系、作品/档案 KU、外部身份记录或 S5 补足。"
    ),
    "boundary_en": (
        "This card refers only to the Bolognese painter the book calls Marcantonio Franceschini. F.csv#84 and #85 refer to the same person; #85 is a correspondence/commission subentry, not a second person. "
        "Keep him distinct by full name from the existing Baldassarre Franceschini KU at units/persons/baldassare-franceschini. Commissions, correspondence, works, and archival materials do not become formal relations or the same KU through this person registration. "
        "Sixteen of 18 direct S2 statement endpoints are marked as relation candidates, all retained for item-by-item S6 review. No formal relation, work/archive KU, external identity record, or S5 enrichment was added."
    ),
    "type_notes_zh": (
        "姓名：本书正文与书信标题使用 Marcantonio Franceschini；中文显示名为工作音译。职业身份：第7、8章称其为博洛尼亚画家及 Cignani 学生。"
    ),
    "type_notes_en": (
        "Name: the prose and letter headings use Marcantonio Franceschini; the Chinese display form is a working transliteration. Professional identity: Chapters 7 and 8 describe him as a Bolognese painter and Cignani's pupil."
    ),
    "sources": [
        card_writer.source(
            "7", "194", "07_CHP-7_sec_iv.md", "29",
            "ordered forty-two paintings from the Bolognese Marcantonio Franceschini alone.",
            "第7章称 Liechtenstein 家族只向博洛尼亚画家 Marcantonio Franceschini 一人订购了42幅画。",
        ),
        card_writer.source(
            "8", "220", "08_CHP-8_sec_ii.md", "108–109",
            "Bolognese pupil of Cignani, Marcantonio Franceschini.",
            "第8章称委员会在 David 方案过于复杂后接洽 Cignani 的博洛尼亚学生 Marcantonio Franceschini。",
        ),
        card_writer.source(
            "8", "223", "08_CHP-8_sec_ii.md", "141–142",
            "Marcantonio Franceschini (after 1720)",
            "第8章将 Marcantonio Franceschini 列为 Ruffo 在1720年后委托宗教画与历史画的博洛尼亚画家之一。",
        ),
        card_writer.source(
            "8", "227", "08_CHP-8_sec_ii.md", "190–191",
            "‘It is a little difficult’, wrote Marcantonio Franceschini from Bologna",
            "第8章引述 Franceschini 从博洛尼亚致 Stefano Conti 的信，说明指定人物数量使题材选择困难。",
            "信件依 Haskell 的正文引述；原信未在本批独立查阅。",
        ),
        card_writer.source(
            "19", "389", "19_CHP-19Appendix.md", "77–79",
            "Documents relating to commissions from Stefano Conti of Lucca to Marcantonio Franceschini and Felice Torelli in thè Biblioteca Governativa, Lucca: MS. 3 299.",
            "第19章附录将 Conti 委托 Franceschini 与 Torelli 的文书定位于 Biblioteca Governativa, Lucca, MS. 3299。",
            "按原书 OCR 保留 thè 与馆藏号排印形式；未独立调阅原档案。",
        ),
        card_writer.source(
            "19", "389", "19_CHP-19Appendix.md", "78–79",
            "Letter from Marcantonio Franceschini to Alessandro Marchesini of 17 February 1705:",
            "第19章附录列出 Marcantonio Franceschini 于1705年2月17日致 Alessandro Marchesini 的信。",
            "据本书附录标题记录；未独立查阅原件。",
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
    old = (
        "截至 Alessandro Marchesini 批次，4,819 个当前 `new` 身份组中完成144组，余4,675组；4,989条成员候选中映射183条，余4,806条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记38组、70条候选，待登记1,048组、1,109条候选。"
    )
    new = (
        "截至 Marcantonio Franceschini 批次，4,819 个当前 `new` 身份组中完成145组，余4,674组；4,989条成员候选中映射185条，余4,804条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记39组、72条候选，待登记1,047组、1,107条候选。"
    )
    text = replace_once(text, old, new, "process S4 current counts")
    text = replace_once(text, "Pierre Crozat、Alessandro Marchesini 已登记为人物 KU。", "Pierre Crozat、Alessandro Marchesini、Marcantonio Franceschini 已登记为人物 KU。", "process registered person list")
    text = replace_once(text, "Alessandro Marchesini 的16条及其他已登记对象", "Alessandro Marchesini 的16条、Marcantonio Franceschini 的16条及其他已登记对象", "process pending S6 list")
    batch = """### person：Marcantonio Franceschini 跨章双候选组登记（2026-10-16）

- `cand-1069`（F.csv#84 人物主项）与 `cand-1070`（F.csv#85，“letters relating to commission from Stefano Conti”子目）同属 `new-person:franceschini-marcantonio-12371601a9`，登记为 `units/persons/marcantonio-franceschini`，两条候选映射到一张人物卡。卡片与既有 Baldassarre Franceschini 人物 KU 按全名区分。
- 第7章 p.194 记 Liechtenstein 家族向 Franceschini 订购42幅画；第8章 pp.220、223、227 记其为 Cignani 学生、委员会向其询价、Ruffo 委托及其致 Conti 的题材意见；第19章 p.389 附录列出相关 Conti 委托文书及1705年致 Marchesini 的信。原信和馆藏未在本批独立查阅，作者判断仍按原书层级保留。
- 该组18条直接 S2 断言端点中16条标记为关系候选，全部留待 S6。批次脚本 [register_s4_person_marcantonio_franceschini_batch_20261016.py](register_s4_person_marcantonio_franceschini_batch_20261016.py) dry-run 核对组成员、同姓既有 KU 边界、6处原文锚点、端点/候选数及外键后通过；apply 将两条候选映射至同一卡。manifest 从1,163增至1,164；累计登记145组、185条候选映射，余4,674组、4,804条候选。

"""
    return replace_once(text, "### 登记进度与后续\n", batch + "### 登记进度与后续\n", "process Franceschini batch log")


def updated_result(text):
    lines = text.splitlines()
    status_ids = [i for i, line in enumerate(lines) if line.startswith("**当前状态：全书 S2 语义处理已完成")]
    assert len(status_ids) == 1, f"result status lines={len(status_ids)}"
    i = status_ids[0]
    line = lines[i]
    line = line.replace("目前完成144组、映射183条成员候选，余4,675组、4,806条映射", "目前完成145组、映射185条成员候选，余4,674组、4,804条映射")
    line = line.replace("Alessandro Marchesini 三十六个补充 person 组", "Alessandro Marchesini、Marcantonio Franceschini 三十七个补充 person 组")
    assert "目前完成145组、映射185条成员候选" in line and "Marcantonio Franceschini 三十七个补充 person 组" in line
    lines[i] = line
    text = "\n".join(lines) + "\n"
    text = replace_once(text, "| [KU 登记](../tables/ku-manifest.csv) | 1,163 KU；含本轮新增38个 person 组（", "| [KU 登记](../tables/ku-manifest.csv) | 1,164 KU；含本轮新增39个 person 组（", "result KU manifest table")
    text = replace_once(text, "Alessandro Marchesini、2个 Valmarana 组", "Alessandro Marchesini、Marcantonio Franceschini、2个 Valmarana 组", "result KU registered names table")
    text = replace_once(text, "当前尚余4,675个 `new` 身份组、4,806条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记38组、70条候选，待登记1,048组、1,109条候选。", "当前尚余4,674个 `new` 身份组、4,804条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记39组、72条候选，待登记1,047组、1,107条候选。", "result current S4 type counts")
    text = replace_once(text, "Alessandro Marchesini、Valmarana 跨章2组", "Alessandro Marchesini、Marcantonio Franceschini、Valmarana 跨章2组", "result current person list")
    text = replace_once(text, "(../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_alessandro_marchesini_batch_20261016.py)", "(../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_alessandro_marchesini_batch_20261016.py)、[Marcantonio Franceschini 人物卡](../../04-knowledge/units/persons/marcantonio-franceschini.md)与[S4 批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_marcantonio_franceschini_batch_20261016.py)", "result S4 artifacts")
    result_batch = """### person：Marcantonio Franceschini 跨章双候选组登记（2026-10-16）

`cand-1069`（F.csv#84 人物主项）与 `cand-1070`（F.csv#85，“letters relating to commission from Stefano Conti”子目）已映射到 [Marcantonio Franceschini 人物卡](../../04-knowledge/units/persons/marcantonio-franceschini.md)。卡片与同姓的 Baldassarre Franceschini KU 区分。第7、8章提供画家身份和委托语境，第19章附录列出相关书信/档案目录但原件未在本批查阅。18条直接 S2 断言端点中16条为关系候选，均留待 S6；本批未新增正式关系、作品/档案 KU、外部身份记录或 S5 补足。\n\n"""
    return replace_once(text, "## 未解决项与交接限制\n", result_batch + "## 未解决项与交接限制\n", "result Franceschini batch section")


def main():
    parser = argparse.ArgumentParser(description="Register the Marcantonio Franceschini person identity group")
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

    assert len(manifest) == 1163, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered_groups), sum(len(v) for v in registered_groups.values())) == (144, 183)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])
    assert all(alignment_by_id[c]["decision"] == "new" for c in MEMBERS)
    assert all(candidate_by_id[c]["suggested_type"] == KIND for c in MEMBERS)
    assert candidate_by_id["cand-1069"]["canonical_name"] == candidate_by_id["cand-1070"]["canonical_name"] == "Franceschini, Marcantonio"
    assert candidate_by_id["cand-1070"]["sub_entry"] == "letters relating to commission from Stefano Conti"

    card_path = ROOT / REL_PATH
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == KIND and "marcantonio franceschini" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    assert any(row["ku_id"] == "units/persons/baldassare-franceschini" and row["type"] == "person" for row in manifest)

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if {"cand-1069", "cand-1070"} & {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 18 and len(relation_ids) == 16, (len(endpoint_ids), len(relation_ids))
    for item in RECORD["sources"]:
        source = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for candidate in MEMBERS:
        planned_by_id[candidate]["ku_id"] = KU_ID
        planned_by_id[candidate]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": KIND, "canonical_name": RECORD["name_zh"], "name_en": RECORD["name_en"], "source_task": TASK, "card_path": REL_PATH})
    planned_groups = defaultdict(list)
    planned_candidates = [row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")]
    for row in planned_candidates:
        if row["decision"] == "new":
            planned_groups[group_of(row["resolution_note"])].append(row)
    planned_registered = {g: rows for g, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({r["ku_id"] for r in mapped}) == 1, group
    assert (len(planned_registered), sum(len(v) for v in planned_registered.values())) == (145, 185)
    assert (len(planned_groups) - len(planned_registered), sum(len(v) - sum(bool(r.get("ku_id")) for r in v) for v in planned_groups.values())) == (4674, 4804)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert date_count == 2

    if args.dry_run:
        print(
            "dry-run passed: Marcantonio Franceschini person_group=1 candidate_members=2 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            f"registered_groups_after={len(planned_registered)} mapped_candidates_after="
            f"{sum(len(v) for v in planned_registered.values())} pending_groups=4674 pending_candidates=4804 "
            f"manifest_after={len(planned_manifest)}; Baldassarre Franceschini kept distinct; no formal relations added"
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
    print(f"applied: Marcantonio Franceschini registered as {KU_ID}; mapped 2 candidates; manifest=1164 registered_groups=145 mapped_candidates=185")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
