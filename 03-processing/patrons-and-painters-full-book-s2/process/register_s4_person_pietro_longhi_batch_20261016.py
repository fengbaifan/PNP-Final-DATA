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
GROUP = "new-person:longhi-pietro-fbe3e4f111"
MEMBERS = ("cand-1429", "cand-1430", "cand-1433")
UNDECIDED_NEIGHBORS = ("cand-1431", "cand-1432", "cand-1434")

RECORD = {
    "candidate": "cand-1429",
    "group": GROUP,
    "slug": "pietro-longhi",
    "name_zh": "彼得罗·隆吉",
    "name_en": "Pietro Longhi",
    "description_zh": (
        "哈斯克尔第10章称 Pietro Longhi 在威尼斯社会受到重视；第13章称 Remondini 以复制出版推广其作品。"
        "第17章称他主导 Teodoro Correr 收藏中的18世纪画家部分；后记提到1776年售画目录列有归于他的两幅“conversation”作品，"
        "同时提醒目录与作品归属并不确定。以上均为原书的记述或评价。"
    ),
    "description_en": (
        "Chapter 10 says Pietro Longhi was highly regarded in Venetian society; Chapter 13 says Remondini popularised his work through reproduction. "
        "Chapter 17 says he dominates the eighteenth-century artists in Teodoro Correr's collection. The appendix notes two 'conversation' pictures attributed to him in the 1776 sale list, while warning that the catalogue and attributions are not definitive. "
        "These are the book's reports and assessments."
    ),
    "context_zh": (
        "索引 `L.csv#86` 主项覆盖其在多个章节中的叙述；`L.csv#87` 标注 Carlo Goldoni 关联，`L.csv#90` 标注 Teodoro Correr 收藏。"
        "第9、10、13、15、17章及第19章后记分别提供正文或注释锚点。"
    ),
    "context_en": (
        "The main entry `L.csv#86` covers the book's references across chapters; `L.csv#87` marks the Carlo Goldoni connection and `L.csv#90` the Teodoro Correr collection. "
        "Chapters 9, 10, 13, 15, and 17, plus the Chapter 19 appendix, supply body or note anchors."
    ),
    "boundary_zh": (
        "本卡只指索引和正文明确称 Pietro Longhi 的威尼斯画家。第15、17章称 Alessandro Longhi 为其子；本批将 Alessandro 与 Pietro 区分，亲缘断言留待 S6 审查，不新增正式关系。"
        "第10章注释转述 Paoletti 将画家称作“Antonio”Longhi，Haskell 认为该来源不完全可靠；本卡不将该称呼当作可靠异名，也不据此创建第二人物。"
        "相邻 cand-1431、cand-1432、cand-1434 仍按既有 S3 决定待证，不映射到本 KU。"
    ),
    "boundary_en": (
        "This card refers only to the Venetian painter explicitly named Pietro Longhi in the index and body. Chapters 15 and 17 call Alessandro Longhi his son; this batch keeps Alessandro distinct, leaves the kinship claim for S6 review, and adds no formal relation. "
        "A Chapter 10 note reports that Paoletti calls the artist 'Antonio' Longhi, which Haskell says is not wholly reliable; this is not adopted as a reliable alias and does not create a second person. "
        "Adjacent candidates cand-1431, cand-1432, and cand-1434 retain their existing S3 unresolved decisions and are not mapped to this KU."
    ),
    "sources": [
        card_writer.source(
            "10", "323", "10_CHP-10_sec_ii.md", "187–188",
            "For we know that Pietro Longhi was highly thought of in other advanced circles of\nVenetian society.",
            "第10章称 Pietro Longhi 在威尼斯社会的其他开明圈子中受到高度评价。",
        ),
        card_writer.source(
            "13", "340", "13_CHP-13_intro.md", "85",
            "Piazzetta, Amigoni, Guarana and, above all, Pietro Longhi were popularised by the Remondini in this way.",
            "第13章称 Remondini 通过复制出版推广 Piazzetta、Amigoni、Guarana，尤其是 Pietro Longhi 的作品。",
        ),
        card_writer.source(
            "15", "361", "15_CHP-15_sec_i.md", "8",
            "Of the great names of the first half of the century only Pietro Longhi carried on for another twenty years",
            "第15章称，在上半世纪的名家中，Pietro Longhi 又延续了二十年的创作活动。",
        ),
        card_writer.source(
            "17", "382", "17_CHP-17_sec_ii.md", "12–14",
            "Of eighteenth-century artists one painter completely dominates the collection—\nPietro Longhi. In view of his passion for Longhi’s ‘documentary’ scenes, it is strange that Correr should have paid no attention whatsoever to the view-painters.",
            "第17章称 Pietro Longhi 主导 Correr 收藏中的18世纪画家部分，并描述 Correr 对其纪实性场景的偏爱。",
        ),
        card_writer.source(
            "19", "393", "19_CHP-19Appendix.md", "150",
            "‘two conversations, Mr Murray and family’ by Pietro Longhi",
            "后记转录1776年售画目录所列归于 Pietro Longhi 的两幅 conversation 作品。",
            "同段明确提示目录及归属不可视为定论。",
        ),
        card_writer.source(
            "10", "323", "10_CHP-10_sec_ii.md", "192",
            "who calls the artist ‘Antonio’ Longhi, does not seem wholly reliable.",
            "第10章注释续文称 Paoletti 将画家称为“Antonio”Longhi，并被 Haskell 评价为不完全可靠；本卡不将该称呼提升为规范名或可靠异名。",
            "OCR L192 是印本注5的续文，注号及 Paoletti 引证始于 L322；此处不创建独立 Antonio Longhi 人物。",
        ),
    ],
    "type_notes_zh": "中文显示名为便于识别所用工作音译；英文规范名按原书和索引写作 Pietro Longhi。",
    "type_notes_en": "The Chinese display name is a working transliteration for readability; the source and index give the English name as Pietro Longhi.",
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
    parser = argparse.ArgumentParser(description="Register the three anchored Pietro Longhi person candidates")
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

    assert len(manifest) == 1138, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (119, 146)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4702, 4844)
    assert set(row["candidate_id"] for row in groups[GROUP]) == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    expected_index = {"cand-1429": "L.csv#86", "cand-1430": "L.csv#87", "cand-1433": "L.csv#90"}
    expected_subentry = {"cand-1429": "", "cand-1430": "Carlo Goldoni and", "cand-1433": "paintings in collection of Teodoro Correr"}
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Longhi, Pietro"
        assert candidate["index_entry_id"] == expected_index[cid]
        assert candidate["sub_entry"] == expected_subentry[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == GROUP
    for cid in UNDECIDED_NEIGHBORS:
        row = alignment_by_id[cid]
        assert row["decision"] == "undecided" and not row.get("ku_id"), cid

    rel_path = "04-knowledge/units/persons/pietro-longhi.md"
    ku_id = "units/persons/pietro-longhi"
    card_path = UNITS / "persons" / "pietro-longhi.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == KIND and "pietro longhi" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(endpoint_ids) == 29 and len(relation_ids) == 20

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
            "dry-run passed: cand-1429/cand-1430/cand-1433 Pietro Longhi person_group=1 candidate_members=3 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=120 mapped_candidates_after=149 pending_groups=4701 "
            "pending_candidates=4841 manifest_after=1139; cand-1431/cand-1432/cand-1434 remain undecided"
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
        f"applied: Pietro Longhi person_groups=1 candidate_members=3 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; adjacent undecided candidates left unmapped"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
