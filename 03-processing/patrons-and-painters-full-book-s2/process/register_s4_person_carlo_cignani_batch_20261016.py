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
KIND = "person"
GROUP = "new-person:carlo-cignani-8a5a0153eb"
MEMBERS = ("cand-0748", "cand-0749")
KU_ID = "units/persons/carlo-cignani"
REL_PATH = "04-knowledge/units/persons/carlo-cignani.md"


RECORD = {
    "candidate": "cand-0748",
    "group": GROUP,
    "slug": "carlo-cignani",
    "name_zh": "卡洛·奇尼亚尼",
    "name_en": "Carlo Cignani",
    "description_zh": (
        "哈斯克尔称 Carlo Cignani 为来自 Bologna 的画家，并记述其作品与委托跨越多个宫廷和城市。第7章称他曾为 Louis XIV 绘制两幅未具名画作，并记一项未继续推进的巴黎邀约；"
        "第8章叙述其 Bergamo 教堂中殿委托谈判未果，以及1692年再次受邀时他正绘制 Forlì 主教座堂穹顶。第10章记 Johann Wilhelm 委托他在 Bologna 与 Rome 工作，并提及 Joseph Smith 收藏中的画作与纸本作品；第13章称 Pasquali 于1749年出版记录 Smith 收藏的 Cignani 与 Ricci 作品的图书。"
    ),
    "description_en": (
        "Haskell identifies Carlo Cignani as a painter from Bologna and discusses his work and commissions across several courts and cities. Chapter 7 says that he painted two unidentified pictures for Louis XIV and records a Paris approach that was not pursued. "
        "Chapter 8 recounts the failed negotiation for the Bergamo church nave commission and says that, when approached again in 1692, he was painting the cupola of Forlì Cathedral. Chapter 10 records Johann Wilhelm commissioning him to work in Bologna and Rome and mentions paintings and drawings by him in Joseph Smith's collection; Chapter 13 says Pasquali published a 1749 book recording works by Cignani and Ricci in that collection."
    ),
    "context_zh": (
        "人物主项为索引 `C.csv#272`；`C.csv#273` 的子目为 `and S. Maria Maggiore, Bergamo`。第8章 pp.219–220 在 Bergamo 委托谈判及再度接洽的连续叙述中明确写出 Carlo Cignani / Cignani，支持将两条 person 候选归入同一人物。子目保留 Bergamo 委托语境，不与教堂、穹顶或画作合并。"
    ),
    "context_en": (
        "The person main entry is `C.csv#272`; `C.csv#273` has the subentry `and S. Maria Maggiore, Bergamo`. Chapters 8 (pp. 219–220) name Carlo Cignani / Cignani in the continuous account of the Bergamo commission negotiations and renewed approach, supporting one person identity for both person candidates. The subentry retains the Bergamo commission context and is not merged with the church, cupola, or paintings."
    ),
    "boundary_zh": (
        "本卡限于本书对 Carlo Cignani 的称名与叙述，不补写出生、卒年或外部身份核验。Louis XIV 的两幅画、Smith 收藏中的七幅 cartoons、Forlì 穹顶及其他作品保持为作品或作品组，不并入人物。Haskell 的评价、转述和未具名对象均保留原有范围；S2 关系候选留待 S6，本卡未新增正式关系。"
    ),
    "boundary_en": (
        "This card is limited to the name and account of Carlo Cignani in the book; it adds no birth or death dates and claims no external identity check. The two pictures for Louis XIV, the seven cartoons in Smith's collection, the Forlì cupola, and other works remain works or work groups, not part of the person record. Haskell's judgments, reported claims, and unnamed objects retain their source limits; S2 relation candidates remain for S6, and no formal relations are added here."
    ),
    "sources": [
        card_writer.source(
            "7", "189", "07_CHP-7_sec_i.md", "247–250",
            "who painted a couple of pictures for the King",
            "哈斯克尔称 Carlo Cignani 曾为 Louis XIV 绘制两幅画，并叙述罗马法国学院负责人曾询问其是否愿赴巴黎；此事未继续推进。",
            "画作与巴黎行程均未具名或证实完成。",
        ),
        card_writer.source(
            "8", "219", "08_CHP-8_sec_ii.md", "96",
            "Carlo Cignani of Bologna",
            "哈斯克尔称 Cignani 参与 Bergamo 教堂中殿委托谈判；其报价与费用要求及委员会协商后，计划未能达成。",
            "这是本书对谈判过程的叙述，不推断未完成的委托为实际创作。",
        ),
        card_writer.source(
            "8", "220", "08_CHP-8_sec_ii.md", "101–105",
            "the committee turned to Cignani once again",
            "哈斯克尔称委员会于1692年再次转向 Cignani；当时他正绘制 Forlì 主教座堂穹顶，并说明他对 Bergamo 项目空间条件的异议。",
            "原书未说明 Cignani 接受再度接洽；保留来源对其穹顶作品及委托谈判的区分。",
        ),
        card_writer.source(
            "10", "282", "10_CHP-10_intro.md", "146–147",
            "commissioned painters such as Cignani",
            "哈斯克尔称 Johann Wilhelm 委托 Cignani 等画家在 Bologna 与 Rome 工作。",
            "不据委托表述补写具体作品或完成状态。",
        ),
        card_writer.source(
            "10", "302", "10_CHP-10_intro.md", "398",
            "seven cartoons by the Bolognese Carlo Cignani",
            "哈斯克尔称 Joseph Smith 将七幅 Carlo Cignani cartoons 挂在其宅邸的另一间房中。",
            "七幅 cartoons 仅作为作品组记录，未拆分为七件作品。",
        ),
        card_writer.source(
            "13", "337", "13_CHP-13_intro.md", "53",
            "his paintings by Cignani and Ricci in 1749",
            "哈斯克尔称 Pasquali 于1749年出版图书，记录 Joseph Smith 收藏中的 Cignani 与 Ricci 作品。",
            "原书未提供此处图书的准确题名或单件画作身份。",
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


def get_group(note: str):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Register the S4 Carlo Cignani person group")
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
    decisions = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in decisions}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    card_path = ROOT / REL_PATH
    manifest_matches = [row for row in manifest if row.get("ku_id") == KU_ID]
    accepted_registered = f"- {REL_PATH}" in accepted_text.splitlines()
    member_rows = [alignment_by_id[candidate_id] for candidate_id in MEMBERS]
    any_registration_artifact = bool(manifest_matches) or card_path.exists() or accepted_registered or any(
        row.get("ku_id") == KU_ID for row in member_rows
    )
    if any_registration_artifact:
        assert len(manifest) >= 1154, f"unexpected post-registration manifest count: {len(manifest)}"
        assert len(manifest_matches) == 1 and manifest_matches[0].get("card_path") == REL_PATH
        assert card_path.exists() and accepted_registered
        assert all(row["decision"] == "new" and row.get("ku_id") == KU_ID for row in member_rows)
        assert all(f"S4 registration: mapped {GROUP} to {KU_ID}." in row["resolution_note"] for row in member_rows)
        assert Counter(row["decision"] for row in decisions) == Counter(
            {"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7}
        )
        post_groups = defaultdict(list)
        post_registered = defaultdict(list)
        for row in decisions:
            if row["decision"] != "new":
                continue
            group = get_group(row["resolution_note"])
            post_groups[group].append(row)
            if row.get("ku_id"):
                post_registered[group].append(row)
        for group, rows in post_registered.items():
            assert len(rows) == len(post_groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
        assert {row["candidate_id"] for row in post_groups[GROUP]} == set(MEMBERS)
        assert all(row.get("ku_id") == KU_ID for row in post_groups[GROUP])
        card_text = card_path.read_text(encoding="utf-8-sig")
        assert "卡洛·奇尼亚尼（Carlo Cignani）" in card_text
        assert "created: '2026-10-16'" in card_text and "updated: '2026-10-16'" in card_text
        for item in RECORD["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])
            assert item["quote"] in card_text, (REL_PATH, item["quote"])
        endpoint_ids = set()
        relation_ids = set()
        with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
            for line in stream:
                statement = json.loads(line)
                if {statement.get("subject_candidate_id"), statement.get("object_candidate_id")} & set(MEMBERS):
                    endpoint_ids.add(statement["statement_id"])
                    if statement.get("qualifiers", {}).get("relation_candidate") is True:
                        relation_ids.add(statement["statement_id"])
        assert len(endpoint_ids) == 27 and len(relation_ids) == 19
        if args.dry_run:
            print(f"post-apply dry-run passed: Carlo Cignani S4 card, accepted entry, 2 candidate mappings, group consistency, citations, and 27 endpoints / 19 relation candidates verified; current manifest={len(manifest)}; no files written")
        else:
            print("already applied: Carlo Cignani S4 registration verified; no files written")
        return 0

    assert len(manifest) == 1153, f"unexpected manifest count: {len(manifest)}"
    assert Counter(row["decision"] for row in decisions) == Counter(
        {"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7}
    )

    groups = defaultdict(list)
    registered = defaultdict(list)
    person_groups = defaultdict(list)
    person_registered = defaultdict(list)
    for row in decisions:
        if row["decision"] != "new":
            continue
        group = get_group(row["resolution_note"])
        assert group, f"new candidate lacks identity group: {row['candidate_id']}"
        groups[group].append(row)
        if candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND:
            person_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
            if candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND:
                person_registered[group].append(row)
    for group, rows in registered.items():
        assert len(rows) == len(groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    assert (len(groups), sum(map(len, groups.values()))) == (4820, 4989)
    assert (len(registered), sum(map(len, registered.values()))) == (134, 168)
    assert (len(person_groups), sum(map(len, person_groups.values()))) == (1087, 1179)
    assert (len(person_registered), sum(map(len, person_registered.values()))) == (28, 55)
    assert (len(person_groups) - len(person_registered), sum(map(len, person_groups.values())) - sum(map(len, person_registered.values()))) == (1059, 1124)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    expected = {
        "cand-0748": ("C.csv#272", "Cignani, Carlo", ""),
        "cand-0749": ("C.csv#273", "Cignani, Carlo", "and S. Maria Maggiore, Bergamo"),
    }
    for candidate_id, (entry, name, subentry) in expected.items():
        candidate = candidate_by_id[candidate_id]
        alignment = alignment_by_id[candidate_id]
        assert candidate["suggested_type"] == KIND
        assert candidate["index_entry_id"] == entry
        assert candidate["canonical_name"] == name and candidate["sub_entry"] == subentry
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == GROUP

    assert not card_path.exists(), f"unexpected existing card: {REL_PATH}"
    assert REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND and "cignani" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if {statement.get("subject_candidate_id"), statement.get("object_candidate_id")} & set(MEMBERS):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 27 and len(relation_ids) == 19, (len(endpoint_ids), len(relation_ids))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for candidate_id in MEMBERS:
        planned_by_id[candidate_id]["ku_id"] = KU_ID
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": KU_ID,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": REL_PATH,
    })

    if args.dry_run:
        print(
            "dry-run passed: Carlo Cignani person_group=1 candidate_members=2 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=135 mapped_candidates_after=170 pending_groups=4685 "
            "pending_candidates=4819 manifest_after=1154; no existing same-type KU; no formal relations added; no files written"
        )
        return 0

    card_text = card_writer.make_card(RECORD, KIND)
    card_text = re.sub(r"^created: '2026-10-15'$", "created: '2026-10-16'", card_text, flags=re.MULTILINE)
    card_text = re.sub(r"^updated: '2026-10-15'$", "updated: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert "created: '2026-10-16'" in card_text and "updated: '2026-10-16'" in card_text
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
        f"applied: Carlo Cignani person_groups=1 candidate_members=2 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
