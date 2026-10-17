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
GROUP = "new-person:augustus-iii-of-poland-1d39936dba"
MEMBERS = ("cand-0148", "cand-0149", "cand-0151", "cand-0152")
UNDECIDED_NEIGHBOR = "cand-0150"

RECORD = {
    "candidate": "cand-0148",
    "group": GROUP,
    "slug": "augustus-iii-of-poland",
    "name_zh": "波兰国王奥古斯都三世",
    "name_en": "Augustus III of Poland (Frederick Augustus II, Elector of Saxony)",
    "description_zh": (
        "哈斯克尔明确将十八世纪初的萨克森选帝侯身份与后来波兰国王 Augustus III 相连，并记其三度访问威尼斯及在德累斯顿汇集 Rosalba Carriera 作品。"
        "第10章称 Augustus III 为 Augustus II 之子、1733年继位者，并述其购藏；第14章记 Francesco Algarotti 曾为萨克森选帝侯 Augustus 工作，"
        "随后为国王购画。本描述仅按原书叙述保留名称与时间语境，不补写外部生平。"
    ),
    "description_en": (
        "Haskell explicitly identifies the early-eighteenth-century Prince Elector of Saxony with the later Augustus III of Poland, noting three visits to Venice and his collection of Rosalba Carriera's works in Dresden. "
        "Chapter 10 calls Augustus III the son of Augustus II and says he succeeded to the throne in 1733, then describes his collecting. Chapter 14 recounts Francesco Algarotti working for Augustus, Elector of Saxony, and later purchasing pictures for the King. "
        "This description follows the book's account and adds no external biography."
    ),
    "context_zh": (
        "索引 `A.csv#149` 主项及 `A.csv#150`（F. Algarotti）、`A.csv#152`（Dresden Gallery）、`A.csv#153`（摩德纳公爵收藏作品）对应四条有 S2 正文锚点的候选。"
        "第10章 pp.277、294 和第14章 p.349 跨章记述该人物的头衔、继位与购藏语境。相邻 `A.csv#151` Rosalba Carriera 子目是 `cand-0150`，无正文提及，仍为 `undecided`，不映射到本 KU。"
    ),
    "context_en": (
        "The main entry `A.csv#149` and `A.csv#150` (F. Algarotti), `A.csv#152` (Dresden Gallery), and `A.csv#153` (pictures from the Dukes of Modena) correspond to four candidates with S2 body anchors. "
        "Chapters 10 (pp. 277, 294) and 14 (p. 349) provide cross-chapter context for his titles, succession, and collecting. The adjacent Rosalba Carriera subentry `A.csv#151` is `cand-0150`; it has no body mention, remains `undecided`, and is not mapped to this KU."
    ),
    "boundary_zh": (
        "本卡只指原书称 Augustus III of Poland、即索引所列 Frederick Augustus II, Elector of Saxony 的人物。原书另以 Augustus II of Poland / Frederick Augustus I 指称其父，本卡不与之合并。"
        "cand-0150 的 Rosalba Carriera 索引子目因缺少正文锚点而保留待证；不由该索引子目反推人物关系。书内叙述与外部身份核验分开。"
    ),
    "boundary_en": (
        "This card refers only to the person the book calls Augustus III of Poland and the index names Frederick Augustus II, Elector of Saxony. The book separately identifies his father as Augustus II of Poland / Frederick Augustus I; they are not merged. "
        "The Rosalba Carriera index subentry `cand-0150` remains undecided because it lacks a body anchor; no relationship is inferred from that subentry. The book's account is kept separate from external identity verification."
    ),
    "sources": [
        card_writer.source(
            "10", "277", "10_CHP-10_intro.md", "19",
            "Above all there was the Prince Elector of Saxony, later to be Augustus III of Poland, who visited Venice three times during the first two decades of the eighteenth century",
            "第10章明确将萨克森选帝侯与后来波兰国王 Augustus III 对应，并记其在18世纪最初二十年三度访问威尼斯。",
        ),
        card_writer.source(
            "10", "294", "10_CHP-10_intro.md", "298",
            "The patronage of his son Augustus III, who succeeded to the throne in 1733, was of a wholly different order.",
            "第10章以其父 Augustus II 的叙述为上下文，称 Augustus III 为其子，并记其1733年继位。",
        ),
        card_writer.source(
            "10", "294", "10_CHP-10_intro.md", "299",
            "His fabulous purchases for it—such as the hundred finest pictures from the collections of the Dukes of Modena—cannot be discussed here but must at least be mentioned as an indication of his vast artistic ambitions.",
            "第10章以德累斯顿画廊为语境，举出购自摩德纳公爵收藏的大量绘画。",
        ),
        card_writer.source(
            "14", "349", "14_CHP-14_intro.md", "30",
            "in 1742 he was in Dresden, working for Augustus, Elector of Saxony. In May 1743 he payed a visit to Venice to buy pictures for the King, and he remained there until 1745.",
            "第14章记 Francesco Algarotti 于1742年在德累斯顿为萨克森选帝侯 Augustus 工作，并于1743年到威尼斯为国王购画。",
            "引文保留来源拼写 payed。",
        ),
    ],
    "type_notes_zh": "英文规范名保留索引给出的波兰王号与萨克森选帝侯姓名/头衔；中文显示名为便于识别的工作译名。",
    "type_notes_en": "The English name preserves the Polish royal title and Saxon elector name/title given in the index; the Chinese display name is a working rendering for readability.",
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
    parser = argparse.ArgumentParser(description="Register the four anchored Augustus III person candidates")
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
    current = decision_rows(alignments)
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1137, f"unexpected manifest count: {len(manifest)}"
    decision_counts = Counter(row["decision"] for row in current)
    assert decision_counts == Counter({"same": 1691, "new": 4990, "undecided": 5618, "excluded": 97, "conflict": 7}), decision_counts
    groups = defaultdict(list)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = get_group(row["resolution_note"])
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            groups[group].append(row)
    for group, rows in groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
            registered[group] = rows
    assert (len(groups), sum(map(len, groups.values()))) == (4821, 4990)
    assert (len(registered), sum(map(len, registered.values()))) == (118, 142)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4703, 4848)
    assert set(row["candidate_id"] for row in groups[GROUP]) == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    expected_index = {
        "cand-0148": "A.csv#149",
        "cand-0149": "A.csv#150",
        "cand-0151": "A.csv#152",
        "cand-0152": "A.csv#153",
    }
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == RECORD["name_en"]
        assert candidate["index_entry_id"] == expected_index[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == GROUP
    unresolved = candidate_by_id[UNDECIDED_NEIGHBOR]
    undecided_row = alignment_by_id[UNDECIDED_NEIGHBOR]
    assert unresolved["index_entry_id"] == "A.csv#151"
    assert unresolved["sub_entry"] == "and Rosalba Carriera"
    assert undecided_row["decision"] == "undecided" and not undecided_row.get("ku_id")

    rel_path = "04-knowledge/units/persons/augustus-iii-of-poland.md"
    ku_id = "units/persons/augustus-iii-of-poland"
    card_path = UNITS / "persons" / "augustus-iii-of-poland.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == KIND and "augustus iii" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if set(MEMBERS) & {statement.get("subject_candidate_id"), statement.get("object_candidate_id")}:
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 31 and len(relation_ids) == 26

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = ku_id
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {ku_id}."
    planned_manifest = list(manifest)
    planned_manifest.append({
        "ku_id": ku_id,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": rel_path,
    })

    if args.dry_run:
        print(
            "dry-run passed: cand-0148/cand-0149/cand-0151/cand-0152 Augustus III person_group=1 candidate_members=4 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=119 mapped_candidates_after=146 pending_groups=4702 "
            "pending_candidates=4844 manifest_after=1138; cand-0150 Rosalba subentry remains undecided and unmapped"
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
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {rel_path}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(
        f"applied: Augustus III person_groups=1 candidate_members=4 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; cand-0150 left undecided"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
