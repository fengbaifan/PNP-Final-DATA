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
GROUP = "new-person:giustiniana-rosenberg-wynne-giustiniana-wy-8bd579547c"
MEMBERS = ("cand-2824",)
KU_ID = "units/persons/giustiniana-wynne-rosenberg"
REL_PATH = "04-knowledge/units/persons/giustiniana-wynne-rosenberg.md"


RECORD = {
    "name_zh": "朱斯蒂尼亚娜·温恩-罗森贝格",
    "name_en": "Giustiniana Wynne-Rosenberg",
    "description_zh": (
        "哈斯克尔第10章以 Giustiniana Wynne 记述她在 Lodoli、Andrea Memmo 与英国领事 Joseph Smith 的求爱叙事中的位置，并称她后来反复成为18世纪威尼斯赞助人与作家之间的联系线索。"
        "第15章称她是 Angelo Querini 的亲密朋友之一，记述她于1762年与奥地利大使 Count Rosenberg 结婚，并以 Mme Rosenberg 转述她对 Alticchiero 的描述；该章注释以 Giustiniana Wynne-Rosenberg 为《Alticchiero》（威尼斯，1787）的作者名。以上均按本书叙述和引文范围登记，未作外部核验。"
    ),
    "description_en": (
        "In Chapter 10, Haskell names her as Giustiniana Wynne in the courtship narratives involving Lodoli, Andrea Memmo, and British Consul Joseph Smith, and says she repeatedly appears as a link among eighteenth-century Venetian patrons and writers. "
        "Chapter 15 calls her one of Angelo Querini's close friends, reports her 1762 marriage to Austrian Ambassador Count Rosenberg, and presents her account of Alticchiero under the form Mme Rosenberg. Its note names Giustiniana Wynne-Rosenberg as the author of Alticchiero (Venice, 1787). These details are registered within the book's account and citations; no external verification was made."
    ),
    "context_zh": (
        "UVWXYZ.csv#161 的索引主项列印刷页300、302、364、369–371。第10章 p.300 以 Giustiniana Wynne 记 Lodoli 与 Memmo 求爱，并称她此后多次联系威尼斯赞助人与作家；p.302 再提 Smith 对她的追求。第15章 p.364 回述 Memmo 与她的交往，pp.369–371 使用 Giustiniana Wynne 和 Mme Rosenberg 两种称谓，叙述婚姻、学术交往及她对 Querini 别墅和园林的评论。p.369 注4以 Giustiniana Wynne-Rosenberg 列为《Alticchiero》作者。该1787年版本未在本批独立查阅。"
    ),
    "context_en": (
        "The UVWXYZ.csv#161 index entry points to printed pp. 300, 302, 364, and 369–71. Chapter 10 p. 300 names Giustiniana Wynne in the account of Lodoli and Memmo courting her and says she later recurs as a link among Venetian patrons and writers; p. 302 again mentions Smith's pursuit. Chapter 15 p. 364 recalls Memmo's involvement with her, while pp. 369–71 use both Giustiniana Wynne and Mme Rosenberg for the account of her marriage, learned company, and comments on Querini's villa and garden. Note 4 on p. 369 names Giustiniana Wynne-Rosenberg as the author of Alticchiero. The 1787 edition was not independently consulted in this batch."
    ),
    "boundary_zh": (
        "本卡将索引候选 cand-2824 及书内的 Giustiniana Wynne、Giustiniana Wynne-Rosenberg、Mme Rosenberg 称谓归于同一人物，依据是第10、15章跨章回指和第15章脚注的作者名。Count Rosenberg 是书中所述配偶，不并入本人物；既有人物 KU Pierre Rosenberg 也因全名和语境不同而保持区分。19条直接 S2 断言端点中16条标记为关系候选，全部保留待 S6 逐项审查；本批不新增正式关系、外部身份记录或 S5 补足。中文名为工作音译。"
    ),
    "boundary_en": (
        "This card groups index candidate cand-2824 with the book's forms Giustiniana Wynne, Giustiniana Wynne-Rosenberg, and Mme Rosenberg, based on the cross-chapter references and the author's name in the Chapter 15 note. Count Rosenberg is the spouse named in the book and is not merged into this person; the existing Pierre Rosenberg KU also remains distinct by full name and context. Sixteen of 19 direct S2 statement endpoints are marked as relation candidates and remain for item-by-item S6 review. No formal relation, external identity record, or S5 enrichment was added in this batch. The Chinese display name is a working transliteration."
    ),
    "type_notes_zh": (
        "索引规范名为 Wynne, Giustiniana (Mme Rosenberg)；正文使用 Giustiniana Wynne、Mme Rosenberg，p.369 注4给出 Giustiniana Wynne-Rosenberg。中文显示名仅作工作音译。"
    ),
    "type_notes_en": (
        "The index form is Wynne, Giustiniana (Mme Rosenberg). The prose uses Giustiniana Wynne and Mme Rosenberg; note 4 on p. 369 gives Giustiniana Wynne-Rosenberg. The Chinese display form is a working transliteration."
    ),
    "sources": [
        card_writer.source(
            "10", "300", "10_CHP-10_intro.md", "373–375",
            "both men were courting the beautiful Giustiniana Wynne, the illegitimate daughter of an English gentleman and a\nGreek adventuress.",
            "第10章以 Giustiniana Wynne 记 Lodoli 与 Memmo 对她的求爱，并称她为一位英国绅士与希腊女性的女儿；该亲缘说法仅按 Haskell 原文记录。",
        ),
        card_writer.source(
            "10", "302", "10_CHP-10_intro.md", "393",
            "his grotesque though pathetic pursuit of Giustiniana Wynne;",
            "第10章继续提到 Joseph Smith 对 Giustiniana Wynne 的追求。",
        ),
        card_writer.source(
            "15", "369", "15_CHP-15_sec_ii.md", "54–55",
            "This strange woman, who thus so closely links these three significant patrons, had in 1762 married the Austrian Ambassador, Count Rosenberg",
            "第15章以 Giustiniana Wynne 回指该女性，并称她于1762年与奥地利大使 Count Rosenberg 结婚。",
        ),
        card_writer.source(
            "15", "369 n. 4", "15_CHP-15_sec_ii.md", "108",
            "Giustiniana Wynne-Rosenberg: Alticchiero, Venezia 1787.",
            "第15章注4以 Giustiniana Wynne-Rosenberg 为《Alticchiero》（威尼斯，1787）的作者名；该版本未独立查阅。",
            "本条仅记录 Haskell 的书目引文，未据此声称核验原书。",
        ),
        card_writer.source(
            "15", "370", "15_CHP-15_sec_ii.md", "65",
            "and after her death in 1791 that of Mme Rosenberg herself",
            "第15章称 Querini 园林中的一处祭坛在 Mme Rosenberg 于1791年去世后纪念了与她的友谊；该关系候选仍待 S6。",
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
        "截至 Marcantonio Franceschini 批次，4,819 个当前 `new` 身份组中完成145组，余4,674组；4,989条成员候选中映射185条，余4,804条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记39组、72条候选，待登记1,047组、1,107条候选。",
        "截至 Giustiniana Wynne-Rosenberg 批次，4,819 个当前 `new` 身份组中完成146组，余4,673组；4,989条成员候选中映射186条，余4,803条。family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记40组、73条候选，待登记1,046组、1,106条候选。",
        "process S4 current counts",
    )
    text = replace_once(
        text,
        "Pierre Crozat、Alessandro Marchesini、Marcantonio Franceschini 已登记为人物 KU。",
        "Pierre Crozat、Alessandro Marchesini、Marcantonio Franceschini、Giustiniana Wynne-Rosenberg 已登记为人物 KU。",
        "process registered person list",
    )
    text = replace_once(
        text,
        "Alessandro Marchesini 的16条、Marcantonio Franceschini 的16条及其他已登记对象",
        "Alessandro Marchesini 的16条、Marcantonio Franceschini 的16条、Giustiniana Wynne-Rosenberg 的16条及其他已登记对象",
        "process pending S6 list",
    )
    batch = """### person：Giustiniana Wynne-Rosenberg 跨章身份组登记（2026-10-16）

- `cand-2824`（UVWXYZ.csv#161，索引名 Wynne, Giustiniana (Mme Rosenberg)）属于 `new-person:giustiniana-rosenberg-wynne-giustiniana-wy-8bd579547c`，登记为 `units/persons/giustiniana-wynne-rosenberg`。正文中的 Giustiniana Wynne、Mme Rosenberg 与脚注作者名 Giustiniana Wynne-Rosenberg 由第10、15章的跨章回指支持，合为一个人物 KU；Count Rosenberg 和既有 Pierre Rosenberg KU 均保持区分。
- 第10章 pp.300、302 与第15章 pp.369–371 提供身份、婚姻、回指及书目锚点。卡片保留 Haskell 的叙述层级；《Alticchiero》1787年版本未独立查阅。
- 19条直接 S2 断言端点中16条标记为关系候选，全部留待 S6；本批未新增正式关系、外部身份记录或 S5 补足。批次脚本 [register_s4_person_giustiniana_wynne_rosenberg_batch_20261016.py](register_s4_person_giustiniana_wynne_rosenberg_batch_20261016.py) dry-run 核对单候选组、5处精确原文锚点、端点/候选数、既有姓名边界和登记外键后通过，再 apply 完成卡片、manifest、accepted.yml 与候选映射。manifest 从1,164增至1,165；累计登记146组、186条候选映射，余4,673组、4,803条候选。

"""
    return replace_once(text, "### 登记进度与后续\n", batch + "### 登记进度与后续\n", "process Wynne batch log")


def updated_result(text):
    lines = text.splitlines()
    status_ids = [i for i, line in enumerate(lines) if line.startswith("**当前状态：全书 S2 语义处理已完成")]
    assert len(status_ids) == 1, f"result status lines={len(status_ids)}"
    i = status_ids[0]
    line = replace_once(
        lines[i],
        "目前完成145组、映射185条成员候选，余4,674组、4,804条映射",
        "目前完成146组、映射186条成员候选，余4,673组、4,803条映射",
        "result S4 status counts",
    )
    line = replace_once(
        line,
        "Marcantonio Franceschini 三十七个补充 person 组",
        "Marcantonio Franceschini、Giustiniana Wynne-Rosenberg 三十八个补充 person 组",
        "result S4 registered person names",
    )
    lines[i] = line
    text = "\n".join(lines) + "\n"
    text = replace_once(
        text,
        "| [KU 登记](../tables/ku-manifest.csv) | 1,164 KU；含本轮新增39个 person 组（",
        "| [KU 登记](../tables/ku-manifest.csv) | 1,165 KU；含本轮新增40个 person 组（",
        "result KU manifest table",
    )
    text = replace_once(
        text,
        "Alessandro Marchesini、Marcantonio Franceschini、2个 Valmarana 组",
        "Alessandro Marchesini、Marcantonio Franceschini、Giustiniana Wynne-Rosenberg、2个 Valmarana 组",
        "result KU registered names table",
    )
    text = replace_once(
        text,
        "当前尚余4,674个 `new` 身份组、4,804条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记39组、72条候选，待登记1,047组、1,107条候选。",
        "当前尚余4,673个 `new` 身份组、4,803条成员候选映射；family 类型共80组、86条候选，已全部登记；person 类型1,086组、1,179条候选，已登记40组、73条候选，待登记1,046组、1,106条候选。",
        "result current S4 type counts",
    )
    text = replace_once(
        text,
        "当前已登记36个 person 组（",
        "当前已登记40个 person 组（",
        "result person summary count",
    )
    text = replace_once(
        text,
        "Pierre Crozat、Alessandro Marchesini、Marcantonio Franceschini、Valmarana 跨章2组",
        "Pierre Crozat、Alessandro Marchesini、Marcantonio Franceschini、Giustiniana Wynne-Rosenberg、Valmarana 跨章2组",
        "result person summary names",
    )
    text = replace_once(
        text,
        "### person：Marcantonio Franceschini 跨章双候选组登记（2026-10-16）",
        "### person：Giustiniana Wynne-Rosenberg 跨章身份组登记（2026-10-16）\n\n`cand-2824`（UVWXYZ.csv#161）已映射至[Giustiniana Wynne-Rosenberg 人物卡](../../04-knowledge/units/persons/giustiniana-wynne-rosenberg.md)。第10章 pp.300、302 与第15章 pp.369–371 支持 Giustiniana Wynne、Mme Rosenberg 和脚注作者名 Giustiniana Wynne-Rosenberg 为同一人物；配偶 Count Rosenberg 与既有 Pierre Rosenberg KU 保持区分。19条直接 S2 端点中16条是关系候选，均留待 S6；1787年《Alticchiero》未独立查阅。本批未新增正式关系、外部身份核验或 S5 补足；依据与 dry-run/apply 记录见[人物卡](../../04-knowledge/units/persons/giustiniana-wynne-rosenberg.md)和[S4 批次脚本](../../03-processing/patrons-and-painters-full-book-s2/process/register_s4_person_giustiniana_wynne_rosenberg_batch_20261016.py)。manifest 从1,164增至1,165；累计登记146组、186条候选映射，余4,673组、4,803条。\n\n### person：Marcantonio Franceschini 跨章双候选组登记（2026-10-16）",
        "result Wynne batch section",
    )
    return text


def main():
    parser = argparse.ArgumentParser(description="Register the Giustiniana Wynne-Rosenberg person identity group")
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

    assert len(manifest) == 1164, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered_groups), sum(len(v) for v in registered_groups.values())) == (145, 185)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])
    assert alignment_by_id[MEMBERS[0]]["decision"] == "new"
    assert candidate_by_id[MEMBERS[0]]["suggested_type"] == KIND
    assert candidate_by_id[MEMBERS[0]]["canonical_name"] == "Wynne, Giustiniana (Mme Rosenberg)"
    assert not candidate_by_id[MEMBERS[0]]["sub_entry"]

    card_path = ROOT / REL_PATH
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND
        and any(token in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for token in ("giustiniana", "wynne"))
        for row in manifest
    )
    assert any(row["ku_id"] == "units/persons/pierre-rosenberg" and row["type"] == "person" for row in manifest)

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if MEMBERS[0] in {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 19 and len(relation_ids) == 16, (len(endpoint_ids), len(relation_ids))
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
    planned_candidates = [row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")]
    for row in planned_candidates:
        if row["decision"] == "new":
            planned_groups[group_of(row["resolution_note"])].append(row)
    planned_registered = {g: rows for g, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({r["ku_id"] for r in mapped}) == 1, group
    assert (len(planned_registered), sum(len(v) for v in planned_registered.values())) == (146, 186)
    assert (len(planned_groups) - len(planned_registered), sum(len(v) - sum(bool(r.get("ku_id")) for r in v) for v in planned_groups.values())) == (4673, 4803)

    planned_process = updated_process(process_text)
    planned_result = updated_result(result_text)
    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert date_count == 2

    if args.dry_run:
        print(
            "dry-run passed: Giustiniana Wynne-Rosenberg person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "source_quotes=5 registered_groups_after=146 mapped_candidates_after=186 "
            "pending_groups=4673 pending_candidates=4803 manifest_after=1165; "
            "Count Rosenberg and Pierre Rosenberg remain distinct; no formal relations added"
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
    print(f"applied: Giustiniana Wynne-Rosenberg person_groups=1 candidates=1 endpoints=19 relation_candidates=16 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
