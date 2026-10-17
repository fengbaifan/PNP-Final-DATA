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
GROUP = "new-person:alessandro-algardi-a854efdf4e"
MEMBERS = ("cand-0034", "cand-0035", "cand-0036")
KU_ID = "units/persons/alessandro-algardi"
REL_PATH = "04-knowledge/units/persons/alessandro-algardi.md"


RECORD = {
    "candidate": "cand-0034",
    "group": GROUP,
    "slug": "alessandro-algardi",
    "name_zh": "亚历山德罗·阿尔加尔迪",
    "name_en": "Alessandro Algardi",
    "description_zh": (
        "哈斯克尔称 Bernini 一度失去最受青睐雕塑家的地位，Alessandro Algardi 随之获得重要教皇委托；Algardi 制作 Innocent X 与 Donna Olimpia 的胸像，"
        "并参与圣彼得大教堂及教皇家族别墅工程。第7章叙述他在 Pamfili 宫廷中的突出地位及 Mazarin 于1648年延揽他的尝试；第15章将 Querini 所藏一件 Hercules 归于 Algardi。"
    ),
    "description_en": (
        "Haskell says Bernini temporarily lost his place as the most favoured sculptor and Alessandro Algardi received important papal commissions. Algardi made busts of Innocent X and Donna Olimpia and received work at St Peter's and the papal family's villa. "
        "Chapter 7 recounts his prominent place at the Pamfili court and Mazarin's 1648 attempt to recruit him; Chapter 15 attributes a Hercules in Querini's collection to Algardi."
    ),
    "context_zh": (
        "索引 `A.csv#35` 为人物主项；`A.csv#36`、`A.csv#37` 分别以 Donna Olimpia 与 Innocent X 胸像作子目。正文第6章 p.148 明言胸像由 Algardi 制作，三条候选共同指向雕塑家，不把胸像作品并作人物。"
    ),
    "context_en": (
        "The person main entry is `A.csv#35`; `A.csv#36` and `A.csv#37` use busts of Donna Olimpia and Innocent X as subentries. Chapter 6 (p. 148) explicitly says Algardi made the busts, so the three candidates resolve to the sculptor and the busts are not merged into the person."
    ),
    "boundary_zh": (
        "卡片依据本书的具名语境和既有未登记草稿原位更新；未作外部身份核验。保留 Haskell 的归属、风格评价與转述限定，不将候选断言直接变成正式关系；相关关系候选留待 S6。"
    ),
    "boundary_en": (
        "This card is updated in place from the existing unregistered draft using the book's named contexts; no external identity check is claimed. Preserve Haskell's attributions, stylistic judgments, and reported wording without turning candidate statements into formal relations; relation candidates remain for S6."
    ),
    "sources": [
        card_writer.source(
            "6", "148", "06_CHP-6_sec_i.md", "30",
            "made busts of Innocent and Donna",
            "哈斯克尔称 Algardi 制作 Innocent X 与 Donna Olimpia 的胸像。",
        ),
        card_writer.source(
            "6", "148", "06_CHP-6_sec_i.md", "31",
            "adopted a colder, more classical manner",
            "哈斯克尔称 Algardi 转向较冷峻、较古典的风格；这是作者对其风格的描述。",
        ),
        card_writer.source(
            "6", "159", "06_CHP-6_sec_iv.md", "34",
            "The sculptor Algardi was given a full-scale life",
            "哈斯克尔称 Bellori 为雕塑家 Algardi 写有完整篇幅的传记。",
        ),
        card_writer.source(
            "7", "182", "07_CHP-7_sec_i.md", "157",
            "tried, through the most generous offers, to persuade him",
            "哈斯克尔叙述 Mazarin 于1648年写信并以优厚条件试图延揽 Algardi；Algardi 在此之前曾拒绝类似邀请。",
            "保留作者的时间与转述语气，不将邀请写成实际迁居。",
        ),
        card_writer.source(
            "15", "371", "15_CHP-15_sec_ii.md", "76",
            "His more modern work included a Hercules by Algardi",
            "哈斯克尔称 Querini 所藏较新的作品中包括一件归于 Algardi 的 Hercules。",
            "记录为 Haskell 的归属说法；未独立核验作品身份或归属。",
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
    parser = argparse.ArgumentParser(description="Register the S4 Alessandro Algardi person group")
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

    assert len(manifest) == 1152, f"unexpected manifest count: {len(manifest)}"
    decision_counts = Counter(row["decision"] for row in decisions)
    assert decision_counts == Counter(
        {"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7}
    ), decision_counts

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
    assert (len(registered), sum(map(len, registered.values()))) == (133, 165)
    assert (len(person_groups), sum(map(len, person_groups.values()))) == (1087, 1179)
    assert (len(person_registered), sum(map(len, person_registered.values()))) == (27, 52)
    assert (len(person_groups) - len(person_registered), sum(map(len, person_groups.values())) - sum(map(len, person_registered.values()))) == (1060, 1127)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Algardi, Alessandro"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == GROUP
    assert candidate_by_id["cand-0034"]["index_entry_id"] == "A.csv#35"
    assert candidate_by_id["cand-0035"]["index_entry_id"] == "A.csv#36"
    assert candidate_by_id["cand-0035"]["sub_entry"] == "bust of Donna Olimpia Maidalchini"
    assert candidate_by_id["cand-0036"]["index_entry_id"] == "A.csv#37"
    assert candidate_by_id["cand-0036"]["sub_entry"] == "bust of Pope Innocent X"

    card_path = ROOT / REL_PATH
    assert card_path.exists(), "expected the unregistered historical draft to be updated in place"
    old_card = card_path.read_text(encoding="utf-8-sig")
    assert "Alessandro Algardi" in old_card and "贝洛里" in old_card and "来源与未决项" in old_card
    assert REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND and "algardi" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(endpoint_ids) == 21 and len(relation_ids) == 19, (endpoint_ids, relation_ids)

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

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
            "dry-run passed: Alessandro Algardi person_group=1 candidate_members=3 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=134 mapped_candidates_after=168 pending_groups=4686 "
            "pending_candidates=4821 manifest_after=1153; existing unregistered draft will be updated in place; no formal relations added; no files written"
        )
        return 0

    card_text = card_writer.make_card(RECORD, KIND)
    card_text = re.sub(r"^created: '2026-10-15'$", "created: '2026-09-09'", card_text, flags=re.MULTILINE)
    card_text = re.sub(r"^updated: '2026-10-15'$", "updated: '2026-10-16'", card_text, flags=re.MULTILINE)
    assert "created: '2026-09-09'" in card_text and "updated: '2026-10-16'" in card_text
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
        f"applied: Alessandro Algardi person_groups=1 candidate_members=3 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; updated existing draft in place; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
