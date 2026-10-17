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
GROUP = "new-person:monterey-of-59ddb10ee4"
MEMBERS = ("cand-1693",)
KU_ID = "units/persons/count-of-monterey"
REL_PATH = "04-knowledge/units/persons/count-of-monterey.md"

RECORD = {
    "candidate": "cand-1693",
    "group": GROUP,
    "slug": "count-of-monterey",
    "name_zh": "蒙特雷伯爵",
    "name_en": "Count of Monterey",
    "description_zh": (
        "哈斯克尔称 Count of Monterey 是17世纪上半叶意大利最显著的西班牙赞助人。第5章称他于1630年任罗马大使并接待 Velasquez；"
        "第7章接续称他于1631年调往 Naples 并任总督，购买绘画、继续雇用在罗马接触的艺术家，也为 Domenichino、Lanfranco 与 Ribera 提供委托或赞助。"
    ),
    "description_en": (
        "Haskell calls the Count of Monterey the most conspicuous Spanish patron in Italy during the first half of the seventeenth century. Chapter 5 "
        "identifies him as the ambassador in Rome who welcomed Velasquez in 1630. Chapter 7 continues the account with his transfer to Naples as viceroy "
        "in 1631, his purchases of paintings, his continued employment of artists he had met in Rome, and commissions or patronage involving Domenichino, "
        "Lanfranco, and Ribera."
    ),
    "context_zh": (
        "索引主项 `M.csv#234` 列印刷页136、171、172。第5章 p.136 称 Ambassador Monterey；第7章 p.171 明称 Count of Monterey，并把1630年罗马大使叙述与1631年调任 Naples 的总督身份连起来；"
        "p.172 续述其对当地艺术家的赞助。"
    ),
    "context_en": (
        "The main index entry `M.csv#234` lists printed pages 136, 171, and 172. Chapter 5 (p. 136) calls him Ambassador Monterey. Chapter 7 (p. 171) "
        "names the Count of Monterey and connects the 1630 Roman ambassadorship with his transfer to Naples as viceroy in 1631; p. 172 continues "
        "the account of his patronage of local artists."
    ),
    "boundary_zh": (
        "本卡按原书与索引的称谓记录同一书内人物，不补写原书未给出的名字、完整头衔或外部身份信息。1630年罗马大使、1631年赴 Naples 的总督及后文 Monterey 均依第7章连续叙述归为同一人物；"
        "不得与其姻亲 Count-Duke Olivarez 或其他总督混同。24条 S2 关系候选留待 S6 逐项审查。本卡未新增正式关系，也未作外部身份核验。"
    ),
    "boundary_en": (
        "This card uses the name forms supplied by the book and index and adds no personal name, fuller title, or external identity information absent from the source. "
        "The 1630 Roman ambassador, the viceroy transferred to Naples in 1631, and later references to Monterey are treated as one person because Chapter 7 "
        "presents them in a continuous account. He is kept distinct from his brother-in-law Count-Duke Olivarez and from other viceroys. All 24 S2 relation "
        "candidates remain for item-by-item S6 review. No formal relation or external identity check is added here."
    ),
    "sources": [
        card_writer.source(
            "5", "136", "05_CHP-5_sec_iii.md", "42",
            "the Ambassador Monterey in 1630",
            "第5章称 Velasquez 于1630年作为 Ambassador Monterey 的客人留宿。",
        ),
        card_writer.source(
            "7", "171", "07_CHP-7_sec_i.md", "25",
            "the Count of Monterey, the most conspicuous Spanish patron in Italy during the first half of the century",
            "第7章以 Count of Monterey 指称该人物，并称其为17世纪上半叶意大利最显著的西班牙赞助人。",
        ),
        card_writer.source(
            "7", "171", "07_CHP-7_sec_i.md", "25–26",
            "Monterey had also made contact with a number of contemporary painters and sculptors and when he was transferred to Naples in 1631 he wished to go on employing them.",
            "第7章将 Monterey 调任 Naples 的年份记为1631，并称他希望继续雇用此前接触的艺术家。",
        ),
        card_writer.source(
            "7", "172", "07_CHP-7_sec_i.md", "301",
            "Certainly he, like other painters in the city, owed much to this Viceroy’s patronage.",
            "第7章称当地画家与其他人一样受益于该总督的赞助；此处保留为 Haskell 的概括。",
        ),
    ],
    "type_notes_zh": "姓名：索引写作 Monterey, Count of；正文另称 Ambassador Monterey 与 the Viceroy。原书在本处未提供其本名。",
    "type_notes_en": "Name: the index reads Monterey, Count of; the prose also calls him Ambassador Monterey and the Viceroy. The book does not give his personal name here.",
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
    parser = argparse.ArgumentParser(description="Register the Count of Monterey person group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    card_path = ROOT / REL_PATH
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current = decision_rows(alignments)
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1142, f"unexpected manifest count: {len(manifest)}"
    decision_counts = Counter(row["decision"] for row in current)
    assert decision_counts == Counter({"same": 1696, "new": 4987, "undecided": 5616, "excluded": 97, "conflict": 7}), decision_counts
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
    assert (len(groups), sum(map(len, groups.values()))) == (4819, 4987)
    assert (len(registered), sum(map(len, registered.values()))) == (123, 154)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4696, 4833)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id["cand-1693"]
    alignment = alignment_by_id["cand-1693"]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Monterey, Count of"
    assert candidate["index_entry_id"] == "M.csv#234"
    assert candidate["index_page_range"] == "136, 171, 172"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert "no unique existing person KU matched" in alignment["resolution_note"]
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND and "monterey" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if "cand-1693" in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 26 and len(relation_ids) == 24, (len(endpoint_ids), len(relation_ids))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    planned_by_id["cand-1693"]["ku_id"] = KU_ID
    planned_by_id["cand-1693"]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
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
            "dry-run passed: Count of Monterey person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=124 mapped_candidates_after=155 pending_groups=4695 "
            "pending_candidates=4832 manifest_after=1143; no formal relations added"
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
        f"applied: Count of Monterey person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
