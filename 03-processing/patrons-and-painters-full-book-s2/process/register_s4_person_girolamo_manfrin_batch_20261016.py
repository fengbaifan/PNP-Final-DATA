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
GROUP = "new-person:girolamo-manfrin-girolamo-manfrin-s-c3ddada91a"
MEMBERS = ("cand-1512",)

RECORD = {
    "candidate": "cand-1512",
    "group": GROUP,
    "slug": "girolamo-manfrin",
    "name_zh": "吉罗拉莫·曼弗林",
    "name_en": "Girolamo Manfrin",
    "description_zh": (
        "哈斯克尔在第17章的威尼斯艺术赞助与收藏叙述中，将吉罗拉莫·曼弗林描述为当地重要赞助者和收藏者；"
        "他记载曼弗林的画廊曾有四百余幅画作，并组织画家围绕其自拟题材举行竞赛。第20章后记称曼弗林藏品"
        "曾包括 Giorgione 的《暴风雨》，同时指出这些作品的来源仍所知甚少。本卡只记录原书叙述。"
    ),
    "description_en": (
        "In his account of artistic patronage and collecting in Venice, Haskell describes Girolamo Manfrin as an "
        "important local patron and collector; he says Manfrin's gallery had held more than 400 pictures and that "
        "Manfrin organized competitions for painters around subjects he devised. The Chapter 20 postscript says "
        "the collection once included Giorgione's Tempesta while acknowledging that its sources remain poorly known. "
        "This card records the book's account only."
    ),
    "context_zh": (
        "第17章 pp.379–381 记述曼弗林在威尼斯的艺术赞助、收藏、其画廊和画家竞赛；Haskell 称其画廊有四百余幅画作，"
        "并称曼弗林曾为画家竞赛拟定题材。第20章 p.410 后记讨论其收藏散佚，称藏品一度包括 Giorgione 的《暴风雨》，"
        "并明确指出收藏来源仍所知甚少。"
    ),
    "context_en": (
        "Chapter 17, pp. 379–381, discusses Manfrin's artistic patronage and collecting in Venice, his gallery, and "
        "competitions for painters; Haskell says the gallery held more than 400 pictures and that Manfrin devised "
        "the competition subjects. The Chapter 20 postscript, p. 410, discusses the dispersal of his collection, "
        "says it once included Giorgione's Tempesta, and explicitly notes that its sources remain poorly known."
    ),
    "boundary_zh": (
        "本卡仅指索引人物 Girolamo Manfrin。曼弗林、其画廊／藏品、竞赛题材及其中具名作品是不同对象；"
        "不把作品、收藏整体或活动并入人物身份，也不补全收藏来源、成员或逐件所有权链。"
    ),
    "boundary_en": (
        "This card refers only to the indexed person Girolamo Manfrin. Manfrin, his gallery or collection, the "
        "competition subjects, and named pictures are distinct objects; the pictures, collection as a whole, and "
        "activities are not merged into his identity, and no complete provenance or item-by-item ownership chain is inferred."
    ),
    "sources": [
        card_writer.source(
            "17", "379", "17_CHP-17_sec_i.md", "3–6",
            "Girolamo Manfrin was almost the caricature of a type of figure that has at all times depressed the conservative supporters of an old order.",
            "第17章以 Girolamo Manfrin 为名介绍人物，并在后文记其在威尼斯的地位与艺术赞助。",
        ),
        card_writer.source(
            "17", "380", "17_CHP-17_sec_i.md", "11",
            "We first come across Manfrin in this connection in 1785 when the posthumous edition of Tiepolo’s etchings Varj Capriccj was dedicated to him.",
            "第17章将曼弗林与1785年奉献给他的 Tiepolo 版画遗著版相连，并继续记其威尼斯艺术界活动。",
        ),
        card_writer.source(
            "17", "381", "17_CHP-17_sec_i.md", "23",
            "The expertise of his advisers combined with Manfrin’s own wealth assembled a huge collection of over 400 pictures.",
            "第17章称其画廊藏有四百余幅画作。",
        ),
        card_writer.source(
            "17", "381", "17_CHP-17_sec_i.md", "24",
            "He would organise competitions among the painters to produce pictures on erotic themes which he himself devised—Joseph and Potiphars Wife, Bathsheba bathing, Lot and his Daughters, Susanna and the Elders.",
            "第17章称曼弗林会组织画家围绕其自拟题材举行竞赛，并列举题材。",
        ),
        card_writer.source(
            "20", "410", "20_CHP-20Postscript.md", "208–209",
            "The dispersal of the Manfrin collection (which at one time included Giorgione’s\nTempesta) belongs to the history of nineteenth-century Venice, and we are still badly informed about the sources from which he obtained his pictures.",
            "第20章后记称曼弗林藏品曾包括 Giorgione 的 Tempesta，并指出作品来源仍所知甚少。",
        ),
    ],
    "type_notes_zh": "中文显示名为便于识别所用工作音译；原书人物名为 Girolamo Manfrin。",
    "type_notes_en": "The Chinese display name is a working transliteration for readability; the source name is Girolamo Manfrin.",
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
    parser = argparse.ArgumentParser(description="Register Girolamo Manfrin's cross-chapter person KU")
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

    assert len(manifest) == 1134, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (115, 134)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4706, 4856)
    assert set(row["candidate_id"] for row in groups[GROUP]) == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id[MEMBERS[0]]
    alignment = alignment_by_id[MEMBERS[0]]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Manfrin, Girolamo"
    assert candidate["index_entry_id"] == "M.csv#49"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP

    rel_path = "04-knowledge/units/persons/girolamo-manfrin.md"
    ku_id = "units/persons/girolamo-manfrin"
    card_path = UNITS / "persons" / "girolamo-manfrin.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == KIND and "manfrin" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if MEMBERS[0] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 40 and len(relation_ids) == 20

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    planned_by_id[MEMBERS[0]]["ku_id"] = ku_id
    planned_by_id[MEMBERS[0]]["resolution_note"] += f" S4 registration: mapped {GROUP} to {ku_id}."
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
            "dry-run passed: cand-1512 Girolamo Manfrin person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=116 mapped_candidates_after=135 pending_groups=4705 "
            "pending_candidates=4855 manifest_after=1135; no existing person KU or duplicate fixed path"
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
        f"applied: Girolamo Manfrin person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
