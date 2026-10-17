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
GROUP = "new-person:alessandro-marchesini-f0fde7762c"
MEMBERS = ("cand-1539", "cand-1540")
KU_ID = "units/persons/alessandro-marchesini"
REL_PATH = "04-knowledge/units/persons/alessandro-marchesini.md"


RECORD = {
    "name_zh": "亚历山德罗·马尔凯西尼",
    "name_en": "Alessandro Marchesini",
    "description_zh": (
        "哈斯克尔称 Alessandro Marchesini 为维罗纳画家，记述他居住在威尼斯、曾在博洛尼亚 Carlo Cignani 的学校学习，并受 Stefano Conti 任命为代理人。"
        "他替 Conti 催办画家委托、定期报告、转交预付款、推荐艺术家并提出改画建议；1725年 Conti 再向他征询。书信及艺术家评价均按哈斯克尔的叙述和引文范围保留。"
    ),
    "description_en": (
        "Haskell describes Alessandro Marchesini as a Veronese painter who lived in Venice, studied at Carlo Cignani's school in Bologna, and was appointed Stefano Conti's agent. "
        "Marchesini pressed artists over delayed commissions, reported regularly to Conti, distributed advances, recommended artists, and proposed alterations; Conti sought his advice again in 1725. "
        "Accounts of letters and artists' opinions remain bounded to Haskell's narrative and quotations."
    ),
    "context_zh": (
        "M.csv#78 的“work for Stefano Conti”子目对应第8章 pp.226–228；第8章以全名介绍 Marchesini 并连续说明他的代理工作。M.csv#77 主项指向第9章 p.265 注4、p.270 注6，其中列出他致 Conti 的1725年书信。"
        "第19章 p.389 附录另列 Marcantonio Franceschini 于1705年致 Marchesini 的信。书内注释和附录所引档案/出版材料未在本批独立查阅。"
    ),
    "context_en": (
        "The M.csv#78 subentry “work for Stefano Conti” points to Chapter 8, pp. 226–228, where the full name appears in a continuous account of Marchesini's agency. "
        "The M.csv#77 main entry points to Chapter 9 p. 265 n. 4 and p. 270 n. 6, which cite his 1725 letters to Conti. Chapter 19 p. 389 also lists a 1705 letter from Marcantonio Franceschini to Marchesini. "
        "The cited archival and published materials in these notes and the appendix were not independently consulted in this batch."
    ),
    "boundary_zh": (
        "本卡只指第8章具名的画家 Alessandro Marchesini，以及索引主项/子目和第9、19章所指同一人物；不把书信候选当作人物，也不把同名程序 units/procedures/marchesini-written-reports-to-conti 合并为人物 KU。"
        "第8章对其能力的评价属于 Haskell 的判断；所引书信仍经 Haskell 转述或刊载。cand-1539、cand-1540 共对应20条直接 S2 断言端点，其中16条标记为关系候选，全部留待 S6。未补入生卒年、外部身份记录、正式关系或 S5 内容。"
    ),
    "boundary_en": (
        "This card refers only to the painter Alessandro Marchesini named in Chapter 8 and the same person indexed in the main entry/subentry and referenced in Chapters 9 and 19. "
        "Letter candidates remain distinct from the person, as does the same-named procedure KU units/procedures/marchesini-written-reports-to-conti. Haskell's assessment of his ability is the author's judgement; cited letters remain mediated or reproduced by Haskell. "
        "Candidates cand-1539 and cand-1540 map to 20 direct S2 statement endpoints, 16 marked as relation candidates; all remain for S6. No birth/death dates, external identity records, formal relations, or S5 enrichment were added."
    ),
    "type_notes_zh": (
        "姓名：正文称 Alessandro Marchesini；索引主项与“work for Stefano Conti”子目共用同一姓名。职业身份：第8章称其为 Veronese painter；居住地与学习经历仅按该章原文记录。"
    ),
    "type_notes_en": (
        "Name: the prose calls him Alessandro Marchesini; the index main entry and “work for Stefano Conti” subentry share that name. Professional identity: Chapter 8 calls him a Veronese painter; residence and study are recorded only as stated there."
    ),
    "sources": [
        card_writer.source(
            "8", "226", "08_CHP-8_sec_ii.md", "185–186",
            "a Veronese painter,\nAlessandro Marchesini, from whom he at once ordered a number of pictures and whom he appointed his agent.",
            "第8章称 Stefano Conti 接触维罗纳画家 Alessandro Marchesini，立即向他订画并任命他为代理人。",
        ),
        card_writer.source(
            "8", "226", "08_CHP-8_sec_ii.md", "186–187",
            "He lived in Venice, but had studied in the school of Carlo Cignani in\nBologna",
            "第8章称 Marchesini 居住在威尼斯，曾在博洛尼亚 Carlo Cignani 的学校学习。",
        ),
        card_writer.source(
            "8", "226", "08_CHP-8_sec_ii.md", "186–187",
            "writing regularly to his patron to keep him informed, handing out the advance payments, suggesting new artists, and even proposing alterations in the work of established masters.",
            "第8章列出 Marchesini 的代理工作：定期向赞助人报告、转交预付款、推荐新艺术家并建议修改成熟画家的作品。",
        ),
        card_writer.source(
            "8", "227", "08_CHP-8_sec_ii.md", "203",
            "To Alessandro Marchesini’s great delight, Conti turned once more to him for advice.",
            "第8章称 Stefano Conti 于1725年恢复收藏时再次向 Marchesini 征询意见。",
        ),
        card_writer.source(
            "9", "265 n. 4", "09_CHP-9_intro.md", "431",
            "See letters from Alessandro Marchesini to Stefano Conti, dated 11 August and I December 1725 published by Haskell, 1956, p. 298.",
            "第9章注释列出 Marchesini 于1725年8月11日和12月1日致 Stefano Conti 的两封信，并指向 Haskell 1956 年刊文。",
            "所引 Haskell 1956 年文献未在本批独立查阅。",
        ),
        card_writer.source(
            "9", "270 n. 6", "09_CHP-9_sec_ii.md", "101",
            "Letter of Alessandro Marchesini to Stefano Conti dated 11 August 1725 in Biblioteca Governativa, Lucca, and Zarzabini, p. 19.",
            "第9章注释列出 Biblioteca Governativa, Lucca 所藏的一封1725年8月11日 Marchesini 致 Conti 书信，并引 Zarzabini。",
            "仅记录本书注释给出的档案定位；未独立调阅馆藏或 Zarzabini。",
        ),
        card_writer.source(
            "19", "389", "19_CHP-19Appendix.md", "77–79",
            "Letter from Marcantonio Franceschini to Alessandro Marchesini of 17 February 1705:",
            "第19章附录列出 Marcantonio Franceschini 于1705年2月17日致 Alessandro Marchesini 的信，置于 Conti 委托档案材料项下。",
            "据本书附录标题记录；未独立查阅 Biblioteca Governativa, Lucca 原件。",
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
        "截至 Pierre Crozat 批次，4,819 个当前 `new` 身份组中完成143组，余4,676组；4,989条成员候选中映射181条，余4,808条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记37组、68条候选，待登记1,049组、1,111条候选。"
    )
    new = (
        "截至 Alessandro Marchesini 批次，4,819 个当前 `new` 身份组中完成144组，余4,675组；4,989条成员候选中映射183条，余4,806条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记38组、70条候选，待登记1,048组、1,109条候选。"
    )
    text = replace_once(text, old, new, "process S4 current counts")
    text = replace_once(text, "Giorgio Pisani、Francesco Zuccarelli 已登记为人物 KU。", "Giorgio Pisani、Francesco Zuccarelli、Pierre Crozat、Alessandro Marchesini 已登记为人物 KU。", "process registered person list")
    text = replace_once(text, "Pierre Crozat 的14条及其他已登记对象", "Pierre Crozat 的14条、Alessandro Marchesini 的16条及其他已登记对象", "process pending S6 list")
    batch = """### person：Alessandro Marchesini 跨章双候选组登记（2026-10-16）

- `cand-1539`（M.csv#77 人物主项）与 `cand-1540`（M.csv#78，“work for Stefano Conti”子目）同属 `new-person:alessandro-marchesini-f0fde7762c`，登记为 `units/persons/alessandro-marchesini`，两条候选映射到一张人物卡。相邻已有程序 KU `units/procedures/marchesini-written-reports-to-conti` 记录的是报告活动，不替代人物卡。
- 第8章 pp.226–228 以全名称其为维罗纳画家，记载其在威尼斯居住、曾在博洛尼亚 Cignani 学习，以及担任 Conti 代理人的具体工作和1725年再次提供建议。第9章注释列出两封1725年致 Conti 的信及 Lucca 馆藏定位；第19章附录列出 Franceschini 于1705年致 Marchesini 的信。书信原件/转引材料未在本批独立查阅，Haskell 对其能力的评价保持为作者判断。
- 该组20条直接 S2 断言端点中16条标记为关系候选，全部留待 S6；本批未新增正式关系、书信 KU、外部身份记录或 S5 补足。批次脚本 [register_s4_person_alessandro_marchesini_batch_20261016.py](register_s4_person_alessandro_marchesini_batch_20261016.py) dry-run 核对 S3 组成员、类型、7处原文锚点、端点/候选数及外键后通过；apply 将两条候选映射至同一卡。manifest 从1,162增至1,163；累计登记144组、183条候选映射，余4,675组、4,806条候选。

"""
    return replace_once(text, "### 登记进度与后续\n", batch + "### 登记进度与后续\n", "process Marchesini batch log")


def updated_result(text):
    lines = text.splitlines()
    status_ids = [i for i, line in enumerate(lines) if line.startswith("**当前状态：全书 S2 语义处理已完成")]
    assert len(status_ids) == 1, f"result status lines={len(status_ids)}"
    i = status_ids[0]
    line = lines[i]
    line = line.replace("目前完成143组、映射181条成员候选，余4,676组、4,808条映射", "目前完成144组、映射183条成员候选，余4,675组、4,806条映射")
    line = line.replace("Francesco Zuccarelli、Pierre Crozat 三十五个补充 person 组", "Francesco Zuccarelli、Pierre Crozat、Alessandro Marchesini 三十六个补充 person 组")
    assert "目前完成144组、映射183条成员候选" in line and "Alessandro Marchesini 三十六个补充 person 组" in line
    lines[i] = line
    text = "\n".join(lines) + "\n"
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,161 KU；含本轮新增36个 person 组（",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,163 KU；含本轮新增38个 person 组（",
        "result KU manifest table",
    )
    text = replace_once(text, "Francesco Zuccarelli、Pierre Crozat、2个 Valmarana 组", "Francesco Zuccarelli、Pierre Crozat、Alessandro Marchesini、2个 Valmarana 组", "result KU registered names table")
    text = replace_once(text, "当前尚余4,676个 `new` 身份组、4,808条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记37组、68条候选，待登记1,049组、1,111条候选。", "当前尚余4,675个 `new` 身份组、4,806条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记38组、70条候选，待登记1,048组、1,109条候选。", "result current S4 type counts")
    text = replace_once(text, "Francesco Zuccarelli、Pierre Crozat、Valmarana 跨章2组", "Francesco Zuccarelli、Pierre Crozat、Alessandro Marchesini、Valmarana 跨章2组", "result current person list")
    text = replace_once(text, "(../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_pierre_crozat_batch_20261016.py)", "(../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_pierre_crozat_batch_20261016.py)、[Alessandro Marchesini 人物卡](../../04-knowledge/units/persons/alessandro-marchesini.md)与[S4 批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_alessandro_marchesini_batch_20261016.py)", "result S4 artifacts")
    result_batch = """### person：Alessandro Marchesini 跨章双候选组登记（2026-10-16）

`cand-1539`（M.csv#77 人物主项）与 `cand-1540`（M.csv#78，“work for Stefano Conti”子目）已映射到 [Alessandro Marchesini 人物卡](../../04-knowledge/units/persons/alessandro-marchesini.md)。第8章 pp.226–228 为直接人物与代理工作证据；第9章注释和第19章附录保留书信目录/引用，未声称独立查阅原件。20条直接 S2 断言端点中16条为关系候选，均待 S6；现有同名程序 KU 与人物分开。本批未新增正式关系、archive KU、外部身份记录或 S5 补足。\n\n"""
    text = replace_once(text, "## 未解决项与交接限制\n", result_batch + "## 未解决项与交接限制\n", "result Marchesini batch section")
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the Alessandro Marchesini person identity group")
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

    assert len(manifest) == 1162, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered_groups), sum(len(v) for v in registered_groups.values())) == (143, 181)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])
    assert all(alignment_by_id[c]["decision"] == "new" for c in MEMBERS)
    assert all(candidate_by_id[c]["suggested_type"] == KIND for c in MEMBERS)
    assert candidate_by_id["cand-1539"]["canonical_name"] == candidate_by_id["cand-1540"]["canonical_name"] == "Marchesini, Alessandro"
    assert candidate_by_id["cand-1540"]["sub_entry"] == "work for Stefano Conti"

    card_path = ROOT / REL_PATH
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == KIND and "alessandro marchesini" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    assert any(row["ku_id"] == "units/procedures/marchesini-written-reports-to-conti" and row["type"] == "procedure" for row in manifest)

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if {"cand-1539", "cand-1540"} & {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 20 and len(relation_ids) == 16, (len(endpoint_ids), len(relation_ids))

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
    planned_registered = {g: v for g, v in planned_groups.items() if any(row.get("ku_id") for row in v)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({r["ku_id"] for r in mapped}) == 1, group
    assert (len(planned_registered), sum(len(v) for v in planned_registered.values())) == (144, 183)
    assert (len(planned_groups) - len(planned_registered), sum(map(len, planned_groups.values())) - sum(len(v) for v in planned_registered.values())) == (4675, 4806)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert date_count == 2, f"expected two card dates, found {date_count}"

    if args.dry_run:
        print(
            "dry-run passed: Alessandro Marchesini person_group=1 candidate_members=2 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            f"registered_groups_after={len(planned_registered)} mapped_candidates_after="
            f"{sum(len(v) for v in planned_registered.values())} pending_groups=4675 pending_candidates=4806 "
            f"manifest_after={len(planned_manifest)}; procedure KU kept separate; no formal relations added"
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
    print(f"applied: Alessandro Marchesini registered as {KU_ID}; mapped 2 candidates; manifest=1163 registered_groups=144 mapped_candidates=183")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
