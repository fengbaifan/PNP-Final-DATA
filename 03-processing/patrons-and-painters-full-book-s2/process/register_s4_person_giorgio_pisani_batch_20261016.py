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
KIND = "person"
GROUP = "new-person:giorgio-pisani-31dda8db5c"
MEMBERS = ("cand-1942",)
KU_ID = "units/persons/giorgio-pisani"
REL_PATH = "04-knowledge/units/persons/giorgio-pisani.md"

RECORD = {
    "candidate": "cand-1942",
    "group": GROUP,
    "slug": "giorgio-pisani",
    "name_zh": "乔治奥·皮萨尼",
    "name_en": "Giorgio Pisani",
    "description_zh": (
        "哈斯克尔将 Giorgio Pisani 列为威尼斯 Barnabotti（贫困贵族）之一，记述他于1780年当选圣马可检察官、" 
        "随后遭逮捕，并在其任职与相关画作的政治争议中扮演委托人和赞助者。第20章后记补述 Boscarati 在审讯中的说法，" 
        "称 Pisani 对所委托画作题材兴趣不大；该说法保留为哈斯克尔转述。"
    ),
    "description_en": (
        "Haskell places Giorgio Pisani among the Barnabotti, Venice's poorer nobles, and recounts his election as Procuratore di San Marco in 1780, "
        "his subsequent arrest, and his role as commissioner and patron amid political controversy over his appointment and related pictures. "
        "The Chapter 20 postscript adds Haskell's report of Boscarati's testimony that Pisani showed little interest in the subjects of the pictures he commissioned."
    ),
    "context_zh": (
        "第10章 pp.325–327 连续叙述 Pisani 的改革主张、1780年任职、庆典图像、委托版画、逮捕及 Boscarati 的处境；" 
        "第20章 p.408 后记回顾相关画作引发的政治风波，并转述 Boscarati 在审讯中的说法。"
    ),
    "context_en": (
        "Chapter 10 (pp. 325–327) follows Pisani's reform proposals, his 1780 appointment, imagery associated with the celebrations, a print commission, "
        "his arrest, and Boscarati's situation. The Chapter 20 postscript (p. 408) revisits the political uproar around the pictures and reports Boscarati's testimony."
    ),
    "boundary_zh": (
        "本卡只指第10章及后记所称的 Giorgio Pisani；与 Pisani 家族集体卡及其他同姓人物分开，不据姓氏推定支系或谱系。" 
        "哈斯克尔对图像意图有修正和保留，后记中的审讯内容也是其对 Olivato 文章的转述；不把委托、赞助、任职、政治活动或被捕事实登记为正式关系。"
        "cand-1942 有23条直接 S2 断言端点，其中15条标记为关系候选，均待 S6 逐项审查。本批未新增正式关系或外部身份核验。"
    ),
    "boundary_en": (
        "This card refers only to the Giorgio Pisani in Chapter 10 and the postscript. It remains distinct from collective Pisani family units and other people "
        "with the surname; no branch or genealogy is inferred from the name. Haskell qualifies and revises his account of the pictures' intent, and the postscript "
        "reports Boscarati's testimony through Olivato. Commissioning, patronage, office, political activity, and arrest are not entered as formal relations. "
        "Candidate cand-1942 has 23 direct S2 statement endpoints, of which 15 are marked as relation candidates; each remains for S6 review. No formal relation "
        "or external identity verification was added in this batch."
    ),
    "sources": [
        card_writer.source(
            "10", "325", "10_CHP-10_sec_ii.md", "203–208",
            "Giorgio Pisani belonged to that class of poor nobles, the Barnabotti, which caused the government so much trouble during the eighteenth century.",
            "第10章称 Giorgio Pisani 属于威尼斯 Barnabotti，即贫困贵族阶层，并将其置于18世纪政治改革叙述中。",
        ),
        card_writer.source(
            "10", "326", "10_CHP-10_sec_ii.md", "210–222",
            "In 1780, after complicated intrigues, he was suddenly elected\nProcuratore di San Marco. The appointment was greeted with great enthusiasm.",
            "第10章记述 Pisani 于1780年当选 Procuratore di San Marco；邻近段落叙述庆祝其任职的图像与刊物。",
        ),
        card_writer.source(
            "10", "327", "10_CHP-10_sec_ii.md", "224–239",
            "Pisani was arrested, and his painter Felice Boscarati, who was dangerously fond of satire, also had trouble after the disgrace of his patron.",
            "第10章记述 Pisani 被捕及其画家 Felice Boscarati 在赞助人失势后的处境。",
        ),
        card_writer.source(
            "20", "408", "20_CHP-20Postscript.md", "174–185",
            "another of the very bizarre allegorical canvases by Felice Boscarati which helped to create such a political uproar around Giorgio Pisani",
            "后记回顾 Boscarati 画作与 Giorgio Pisani 周围政治风波的关联；本段还转述 Olivato 对作品原始委托情境的讨论及 Boscarati 审讯证词。",
            "Haskell 转述 Olivato；原文章及审讯记录未在本批独立查阅。",
        ),
    ],
    "type_notes_zh": (
        "姓名：正文与后记均用 Giorgio Pisani；脚注/题名材料见 Missier Zorzi Pisani 等威尼斯语形式。中文显示名为工作音译，不据称谓推定家族支系。"
    ),
    "type_notes_en": (
        "Name: the prose and postscript use Giorgio Pisani; the notes and title material include Venetian forms such as Missier Zorzi Pisani. "
        "The Chinese display form is a working transliteration and does not imply a family branch."
    ),
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


def decision_rows(rows):
    return [row for row in rows if row.get("candidate_id") and not row.get("external_source")]


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Register the Giorgio Pisani person group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    card_path = UNITS / "persons" / "giorgio-pisani.md"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current = decision_rows(alignments)
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1159, f"unexpected manifest count: {len(manifest)}"
    decision_counts = Counter(row["decision"] for row in current)
    assert decision_counts == Counter({"same": 1697, "new": 4988, "undecided": 5615, "excluded": 97, "conflict": 7}), decision_counts
    groups = defaultdict(list)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = get_group(row["resolution_note"])
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            groups[group].append(row)
            if row.get("ku_id"):
                registered[group].append(row)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    for group, rows in registered_groups.items():
        assert len(rows) == len(groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    assert (len(groups), sum(map(len, groups.values()))) == (4819, 4988)
    assert (len(registered_groups), sum(len(rows) for rows in registered_groups.values())) == (140, 176)
    assert (len(groups) - len(registered_groups), sum(map(len, groups.values())) - sum(len(rows) for rows in registered_groups.values())) == (4679, 4812)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id["cand-1942"]
    alignment = alignment_by_id["cand-1942"]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Pisani, Giorgio"
    assert candidate["index_entry_id"] == "P.csv#143"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert "full personal name" in alignment["resolution_note"]
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND and "giorgio pisani" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if "cand-1942" in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 23 and len(relation_ids) == 15, (len(endpoint_ids), len(relation_ids))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    planned_by_id["cand-1942"]["ku_id"] = KU_ID
    planned_by_id["cand-1942"]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": REL_PATH,
    })

    planned_groups = defaultdict(list)
    for row in decision_rows(planned_alignment):
        if row["decision"] == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    for group, rows in planned_registered.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
    assert (len(planned_registered), sum(len(rows) for rows in planned_registered.values())) == (141, 177)
    assert (len(planned_groups) - len(planned_registered), sum(map(len, planned_groups.values())) - sum(len(rows) for rows in planned_registered.values())) == (4678, 4811)

    if args.dry_run:
        print(
            "dry-run passed: Giorgio Pisani person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            f"registered_groups_after={len(planned_registered)} mapped_candidates_after="
            f"{sum(len(rows) for rows in planned_registered.values())} pending_groups=4678 "
            f"pending_candidates=4811 manifest_after={len(manifest) + 1}; no formal relations added"
        )
        return 0

    card_text = card_writer.make_card(RECORD, KIND)
    card_text, date_count = re.subn(
        r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE
    )
    assert date_count == 2, f"expected two card dates, found {date_count}"
    card_path.write_text(card_text, encoding="utf-8-sig", newline="\n")
    write_csv(manifest_path, manifest_fields, planned_manifest)
    write_csv(alignment_path, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > REL_PATH),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {REL_PATH}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(
        f"applied: Giorgio Pisani person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
