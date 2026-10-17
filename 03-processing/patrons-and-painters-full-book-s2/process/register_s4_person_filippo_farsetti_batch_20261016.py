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
UNITS = ROOT / "04-knowledge" / "units"
KIND = "person"
GROUP = "new-person:farsetti-filippo-farsetti-filippo-h-n-a027772c3f"
MEMBERS = ("cand-1002",)

RECORD = {
    "candidate": "cand-1002",
    "group": GROUP,
    "slug": "filippo-farsetti",
    "name_zh": "菲利波·法尔塞蒂",
    "name_en": "Filippo Farsetti",
    "description_zh": "哈斯克尔称 Filippo Farsetti 生于1703年，约17或18岁时成为 Padre Lodoli 的学生，曾广泛旅行并在巴黎居住数年；他以成为 abate 回避其身份所附带的政治责任，并把大量时间、精力和财力投入艺术。第15章将其收藏、对古典雕塑和当代艺术的兴趣及其对威尼斯艺术环境的影响相连，同时指出其具体收藏时间与个人目标仍不完全清楚。本卡仅登记书内人物身份和限定叙述，不作外部核验。",
    "description_en": "Haskell says Filippo Farsetti was born in 1703, became a pupil of Padre Lodoli at about seventeen or eighteen, travelled widely, and lived for several years in Paris. He avoided the political responsibilities attached to his status by becoming an abate and devoted much of his time, energy, and money to the arts. Chapter 15 connects his collections and interests in classical sculpture and contemporary arts with the Venetian artistic milieu, while noting that the chronology of his collecting and his personal aims remain incompletely known. This card registers the identity and qualified account in the book, with no external verification.",
    "context_zh": "第15章正文页标 p.302（候选索引 p.362）以全名介绍其出生、求学、旅行、巴黎居住和艺术投入；pp.363–364 讨论其私人收藏、对威尼斯新古典主义及艺术 patronage 的影响，并明确说其仍是一个了解有限的人物。第10章候选索引 p.322 将其列为 Lodoli 的仰慕者之一（正文 OCR 页标为 [Page 22]），第16章候选索引 p.373 再次把他置于18世纪后半叶威尼斯 patronage 语境（正文 OCR 页标为 [Page 2]）。",
    "context_en": "Chapter 15's source page marker is p. 302 (candidate index p. 362); it names him in the account of his birth, pupilage, travel, residence in Paris, and commitment to the arts. Pages 363–364 discuss his private collections and influence on Venetian Neoclassicism and patronage, while explicitly describing him as a figure whose aims and achievements remain partly obscure. Chapter 10's candidate index gives p. 322 (OCR page marker [Page 22]) for the passage listing him among Lodoli's admirers; Chapter 16's candidate index gives p. 373 (OCR page marker [Page 2]) for the later patronage context.",
    "boundary_zh": "本卡只指人物 Filippo Farsetti，不与既有 Farsetti family 家族卡合并。第15章将其堂亲 Daniele 与他区分，并称 Daniele 继承且扩充收藏；不得把两人的活动或作品归并。Haskell 对 Filippo 的收藏编年与个人目标明确保留不确定性，本卡不补写家族史、具体作品清单或未证实的关系。友谊、师承、赞助、收藏和艺术影响等 S2 断言仍待 S6 审查；本卡未新增正式关系或外部生平。",
    "boundary_en": "This card refers to Filippo Farsetti as a person and remains distinct from the existing Farsetti family card. Chapter 15 distinguishes his cousin Daniele, who inherited and expanded the collection; their activities and works are not conflated. Haskell explicitly leaves the chronology of Filippo's collecting and his personal aims uncertain, so this card adds no family history, itemized collection, or unsupported relation. S2 claims about friendship, pupilage, patronage, collecting, and artistic influence remain for S6 review; no formal relations or external biography are added.",
    "sources": [
        card_writer.source(
            "15", "302", "15_CHP-15_sec_i.md", "17–18",
            "The man who exercised the greatest influence in this way was Filippo Farsetti.",
            "第15章以全名介绍 Filippo Farsetti，记述其出生、成为 Padre Lodoli 学生、旅行及在巴黎居住。正文页标为 p.302；候选索引页码为 p.362。",
            "候选索引页码 p.362；正文文件页标 p.302，依现有 family 卡的处理口径保留页码差异。",
        ),
        card_writer.source(
            "15", "363", "15_CHP-15_sec_i.md", "30–32",
            "Farsetti’s ostentatious wealth and devotion to classical sculpture would in themselves have made him a most important figure in the society of his time.",
            "第15章将 Farsetti 的古典雕塑兴趣与其对当代艺术的关注、以及对威尼斯绘画和雕塑的影响联系起来。",
        ),
        card_writer.source(
            "15", "364", "15_CHP-15_sec_i.md", "39–41",
            "However, a note of ruefulness comes in when he describes Filippo’s collecting and mentions the enormous expense that was involved",
            "第15章以 Filippo 的堂亲 Tommaso Giuseppe 的回忆提及其收藏及相关巨额花费；本卡保留该信息为书内转述。",
        ),
        card_writer.source(
            "10", "322", "10_CHP-10_sec_ii.md", "177–178",
            "Querini and Filippo Farsetti, all became strong supporters of that very classicism which",
            "第10章将 Filippo Farsetti 列为 Lodoli 的仰慕者之一，并记其支持 Lodoli 曾质疑的古典主义。",
            "候选索引页码 p.322；该段正文 OCR 页标显示 [Page 22]。",
        ),
        card_writer.source(
            "16", "373", "16_CHP-16_intro.md", "8",
            "the spectacular patronage of a Farsetti",
            "第16章将 Farsetti 与后半世纪威尼斯显赫 patronage 作比较，并转入较低阶层的收藏者。",
            "候选索引页码 p.373；正文 OCR 页标显示 [Page 2]。",
        ),
    ],
    "type_notes_zh": "规范名采用第15章全名 Filippo Farsetti。Farsetti family 是另一个集体对象；其堂亲 Daniele 与人物 Filippo 分开。中文名为便于识别的音译。",
    "type_notes_en": "The normalized name follows the full form Filippo Farsetti in Chapter 15. The Farsetti family is a separate collective entity, and his cousin Daniele remains distinct from Filippo. The Chinese display name is transliterated.",
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note)
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Register Filippo Farsetti as one S4 person KU")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")
    assert len(manifest) == 1129, f"unexpected manifest count: {len(manifest)}"

    current = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    new_rows = [row for row in current if row["decision"] == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        new_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    counts = {decision: sum(row["decision"] == decision for row in current) for decision in ("same", "new", "conflict", "excluded", "undecided")}
    assert len(current) == 12403 and counts == {"same": 1681, "new": 5000, "conflict": 7, "excluded": 97, "undecided": 5618}, counts
    assert len(new_groups) == 4827
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (110, 125)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    candidate = candidate_by_id[MEMBERS[0]]
    alignment = alignment_by_id[MEMBERS[0]]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Farsetti, Filippo"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert new_groups[GROUP] and {row["candidate_id"] for row in new_groups[GROUP]} == set(MEMBERS)

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(row["type"] == "person" and row.get("name_en", "").casefold() == RECORD["name_en"].casefold() for row in manifest)
    family = [row for row in manifest if row["ku_id"] == "units/families/farsetti-family"]
    assert len(family) == 1 and family[0]["type"] == "family"

    endpoint_statement_count = 0
    endpoint_chapters = defaultdict(int)
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            if MEMBERS[0] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_statement_count += 1
                endpoint_chapters[statement["statement_id"].split("-")[1]] += 1
    assert endpoint_statement_count == 48, f"unexpected statement endpoint count: {endpoint_statement_count}"
    assert {"chp10", "chp15"}.issubset(endpoint_chapters), endpoint_chapters

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    planned_by_id[MEMBERS[0]]["ku_id"] = ku_id
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {ku_id}."
    planned_manifest.append({
        "ku_id": ku_id,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": rel_path,
    })
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(planned_registered), sum(sum(bool(row.get("ku_id")) for row in rows) for rows in planned_registered.values())) == (111, 126)
    assert len(planned_manifest) == 1130

    if args.dry_run:
        print(
            "dry-run passed: Filippo Farsetti person_group=1 candidate_members=1 "
            f"statement_endpoints={endpoint_statement_count} registered_groups_after=111 "
            "mapped_candidates_after=126 manifest_after=1130; family KU remains separate"
        )
        return 0

    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert date_count == 2, f"expected two card dates, found {date_count}"
    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(manifest_path, manifest_fields, planned_manifest)
    write_csv(alignment_path, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {rel_path}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(f"applied: Filippo Farsetti person_groups=1 candidate_members=1 statement_endpoints={endpoint_statement_count} manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
