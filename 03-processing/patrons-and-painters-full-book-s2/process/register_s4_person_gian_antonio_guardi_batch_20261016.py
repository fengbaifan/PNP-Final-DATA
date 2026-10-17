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
GROUP = "new-person:antonio-gian-guardi-antonio-gian-guardi-s-daa9764d01"
MEMBERS = ("cand-1245",)
KU_ID = "units/persons/gian-antonio-guardi"
REL_PATH = "04-knowledge/units/persons/gian-antonio-guardi.md"


RECORD = {
    "candidate": "cand-1245",
    "group": GROUP,
    "slug": "gian-antonio-guardi",
    "name_zh": "吉安·安东尼奥·瓜尔迪",
    "name_en": "Gian Antonio Guardi",
    "description_zh": (
        "第10章称 Gian Antonio Guardi 在1730年前至1745年间为 Marshal Schulenburg 工作并领取月薪。哈斯克尔说 Schulenburg 主要把他视作有用的临摹者，而非独立画家；Guardi 只在1737年受托创作过一组自己的历史画，此后主要临摹威尼斯经典、同代画作并绘制肖像。"
        "哈斯克尔将1742–1743年临摹 Van Mour 版画的土耳其题材作品视为他展现奇幻想象力的突出例外；第9章以“奇幻但不严肃”概括其艺术，第17章提及他对 Pietro Longhi 风格的尝试。"
    ),
    "description_en": (
        "Chapter 10 says Gian Antonio Guardi worked for Marshal Schulenburg from before 1730 until 1745 and received a monthly salary. Haskell says Schulenburg regarded him chiefly as a useful copyist rather than an original painter; Guardi was commissioned only once, in 1737, to paint history pictures of his own, and otherwise copied Venetian masterpieces and contemporary works and produced portraits. "
        "Haskell treats the Turkish scenes copied after Van Mour engravings in 1742–1743 as a notable exception that revealed Guardi's imaginative gifts. Chapter 9 characterizes his art as magical but unserious, and Chapter 17 mentions his excursions into Pietro Longhi's manner."
    ),
    "context_zh": (
        "人物主项为 `G.csv#155`，索引列 pp.258、312、315、383。第9、10章以全名 Gian Antonio Guardi 连续指称同一画家；第10章注2转述 Watson 将相关系列归于 Gian Antonio 而非 Francesco Guardi。该既有卡不同于 manifest 中的 Francesco Guardi 人物 KU。第17章 p.383 注1只称作品在 Correr 当时被认作 Guardi 所作，未给出名字；此归属沿用原书限定，不由此扩展为新身份锚点。"
    ),
    "context_en": (
        "The person main entry is `G.csv#155`, indexed at pp. 258, 312, 315, and 383. Chapters 9 and 10 use the full name Gian Antonio Guardi for the same painter; Chapter 10 note 2 reports Watson's attribution of a series to Gian Antonio rather than Francesco Guardi. This person is distinct from the accepted Francesco Guardi KU in the manifest. Chapter 17 (p. 383) note 1 says only that works were known as Guardi's in Correr's day, without a first name; this source limitation is retained and is not used as an additional identity anchor."
    ),
    "boundary_zh": (
        "卡片限于本书对 Gian Antonio Guardi 的具名叙述，不作外部身份核验。Haskell 关于 Schulenburg 评价、Guardi 风格及作品归属均保留为作者陈述；p.313 注2所引 Watson 论文及 p.383 注1所引 Pignatti 文献未独立查阅。Correr 收藏作品的 Guardi / Longhi 归属争议不在此解决。友谊、委托、临摹、赞助、肖像及作品归属等 S2 关系候选留待 S6；本卡未新增正式关系。"
    ),
    "boundary_en": (
        "This card is limited to the book's named account of Gian Antonio Guardi and claims no external identity check. Haskell's judgments about Schulenburg's view, Guardi's style, and work attribution remain attributed to the author; the Watson paper cited in p. 313 note 2 and Pignatti item cited in p. 383 note 1 were not independently consulted. The attribution dispute around works in the Correr collection is not resolved here. S2 candidates about friendship, commissions, copying, patronage, portraits, and work attribution remain for S6; no formal relations are added."
    ),
    "sources": [
        card_writer.source(
            "9", "258", "09_CHP-9_intro.md", "179–186",
            "an artist of magical but quite unserious qualities",
            "哈斯克尔称 Gian Antonio Guardi 的艺术具有奇幻但不严肃的特质，并认为其在 Venice 的事业相对有限。",
            "这是作者的风格与事业评价。",
        ),
        card_writer.source(
            "10", "312", "10_CHP-10_sec_ii.md", "17–32",
            "Gian Antonio Guardi who worked for him for some fifteen years",
            "哈斯克尔称 Guardi 在1730年前至1745年间为 Schulenburg 工作并领取月薪。",
            "起止时间依原书措辞保留。",
        ),
        card_writer.source(
            "10", "313", "10_CHP-10_sec_ii.md", "72–81",
            "the little Turkish scenes copied in 1742 and 1743",
            "哈斯克尔将 Guardi 临摹 Van Mour 版画的土耳其题材作品作为其想象力显现的例外，并称 Schulenburg 是其最持久的赞助人却未理解其才能。",
            "保留 Haskell 的作品评价与赞助关系陈述，不直接登记关系。",
        ),
        card_writer.source(
            "10", "313 n. 2", "10_CHP-10_sec_ii.md", "285",
            "attributes the series to Gian Antonio rather than Francesco Guardi",
            "哈斯克尔转述 Watson 将相关系列归于 Gian Antonio 而不是 Francesco Guardi。",
            "Watson 文献未独立查阅；保留为 Haskell 的转述。",
        ),
        card_writer.source(
            "17", "383", "17_CHP-17_sec_ii.md", "19–22",
            "Gian Antonio Guardi’s excursions into Longhi’s manner",
            "哈斯克尔称 Correr 曾购入 Guardi 对 Longhi 风格的尝试；同页注释记载这些作品后来被目录列作 Longhi、而 Correr 当时称其为 Guardi 所作。",
            "注释未指明是哪一位 Guardi；Pignatti 未独立查阅，不据此解决归属。",
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


def endpoint_counts(member_ids):
    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if {statement.get("subject_candidate_id"), statement.get("object_candidate_id")} & set(member_ids):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    return endpoint_ids, relation_ids


def validate_sources(card_text: str | None = None):
    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])
        if card_text is not None:
            assert item["quote"] in card_text, (REL_PATH, item["quote"])


def main():
    parser = argparse.ArgumentParser(description="Register the S4 Gian Antonio Guardi person group")
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
    any_artifact = bool(manifest_matches) or card_path.exists() or accepted_registered or any(row.get("ku_id") == KU_ID for row in member_rows)
    if any_artifact:
        assert len(manifest) >= 1159
        assert len(manifest_matches) == 1 and manifest_matches[0].get("card_path") == REL_PATH
        assert card_path.exists() and accepted_registered
        assert member_rows[0]["decision"] == "new" and member_rows[0].get("ku_id") == KU_ID
        assert f"S4 registration: mapped {GROUP} to {KU_ID}." in member_rows[0]["resolution_note"]
        card_text = card_path.read_text(encoding="utf-8-sig")
        assert "吉安·安东尼奥·瓜尔迪（Gian Antonio Guardi）" in card_text
        assert "created: '2026-10-16'" in card_text and "updated: '2026-10-16'" in card_text
        validate_sources(card_text)
        endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
        assert (len(endpoint_ids), len(relation_ids)) == (23, 19)
        if args.dry_run:
            print(f"post-apply dry-run passed: Gian Antonio Guardi card, accepted entry, candidate mapping, citations, and 23 endpoints / 19 relation candidates verified; Francesco Guardi remains separate; manifest={len(manifest)}; no files written")
        else:
            print("already applied: Gian Antonio Guardi S4 registration verified; no files written")
        return 0

    assert len(manifest) == 1158, f"unexpected manifest count: {len(manifest)}"
    counts = Counter(row["decision"] for row in decisions)
    assert counts == Counter({"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7})
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
    assert (len(registered), sum(map(len, registered.values()))) == (139, 175)
    assert (len(person_groups), sum(map(len, person_groups.values()))) == (1087, 1179)
    assert (len(person_registered), sum(map(len, person_registered.values()))) == (33, 62)
    assert (len(person_groups) - len(person_registered), sum(map(len, person_groups.values())) - sum(map(len, person_registered.values()))) == (1054, 1117)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id["cand-1245"]
    row = alignment_by_id["cand-1245"]
    assert candidate["suggested_type"] == KIND
    assert candidate["index_entry_id"] == "G.csv#155"
    assert candidate["canonical_name"] == "Guardi, Gian Antonio"
    assert row["decision"] == "new" and not row.get("ku_id") and get_group(row["resolution_note"]) == GROUP
    assert not card_path.exists(), f"unexpected existing card: {REL_PATH}"
    assert REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == KIND and "gian antonio guardi" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    assert any(row["type"] == KIND and "francesco guardi" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    validate_sources()
    endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
    assert (len(endpoint_ids), len(relation_ids)) == (23, 19), (len(endpoint_ids), len(relation_ids))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_by_id[MEMBERS[0]]["ku_id"] = KU_ID
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
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
        print("dry-run passed: Gian Antonio Guardi person_group=1 candidate_members=1 statement_endpoints=23 relation_candidates=19; Francesco Guardi remains separate; Correr attribution limitations retained; registered_groups_after=140 mapped_candidates_after=176 pending_groups=4680 pending_candidates=4813 manifest_after=1159; no files written")
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
    print(f"applied: Gian Antonio Guardi person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; Francesco Guardi remains separate; no formal relations added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
