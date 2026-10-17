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
GROUP = "new-person:carlo-ferrante-cb229cd01f"
MEMBERS = ("cand-0560", "cand-10983")

RECORD = {
    "candidate": "cand-0560",
    "group": GROUP,
    "slug": "ferrante-carlo",
    "name_zh": "费兰特·卡洛",
    "name_en": "Ferrante Carlo",
    "description_zh": (
        "第5章介绍 Ferrante Carlo（索引作 Carlo, Ferrante）：他于1578年生于帕尔马，是律师、诗人，并先后担任两位枢机的秘书；"
        "他热衷绘画收藏，与多位艺术家交往并委托作品。第20章后记转述 Nicholas Turner 的研究，指出 Bellori 关于 Lanfranco 的"
        "若干著名评论很大程度上源自 Ferrante Carlo 的写作。本卡仅记录原书叙述。"
    ),
    "description_en": (
        "Chapter 5 identifies Ferrante Carlo (indexed as Carlo, Ferrante): born in Parma in 1578, he was a lawyer and poet "
        "who served successively as secretary to two cardinals; he was devoted to collecting pictures, associated with "
        "leading artists, and commissioned works. The Chapter 20 postscript reports Nicholas Turner's finding that some "
        "of Bellori's famous comments on Lanfranco were closely derived from Ferrante Carlo's writing. This card records "
        "the book's account only."
    ),
    "context_zh": (
        "第5章 pp.123–124 将 Ferrante Carlo 置于十七世纪艺术赞助与交易语境，记其律师、诗人和秘书经历、对绘画的兴趣、"
        "与 Cassiano dal Pozzo 及艺术家的交往、委托和收藏。第20章 p.402 后记明称其写作是 Bellori 若干 Lanfranco 评论的来源，"
        "并回指作者在第5章对该人物的叙述。"
    ),
    "context_en": (
        "Chapter 5, pp. 123–124, places Ferrante Carlo in the context of seventeenth-century artistic patronage and dealing, "
        "recording his work as a lawyer, poet, and secretary, his interest in pictures, his contacts with Cassiano dal Pozzo "
        "and artists, and his commissions and collection. The Chapter 20 postscript, p. 402, explicitly names his writing "
        "as a source for some of Bellori's comments on Lanfranco and refers back to the account of him in Chapter 5."
    ),
    "boundary_zh": (
        "本卡仅指原书写作 Ferrante Carlo、索引倒置为 Carlo, Ferrante 的人物；不由姓名顺序推断不同人物，也不把 Bellori、"
        "Lanfranco 或其评论及作品并入该人物身份。后记关于写作来源的说法是 Haskell 转述 Nicholas Turner，不表示本轮独立查阅该研究。"
    ),
    "boundary_en": (
        "This card refers only to the person named Ferrante Carlo in the text and inverted as Carlo, Ferrante in the index; "
        "the name order is not used to infer a different person. Bellori, Lanfranco, the comments, and the works are not "
        "merged into this person's identity. The postscript is Haskell reporting Nicholas Turner, whose study was not "
        "independently consulted in this task."
    ),
    "sources": [
        card_writer.source(
            "5", "123", "05_CHP-5_sec_i.md", "28–33",
            "Ferrante Carlo, born in Parma in 1578, was a most cultivated lawyer and poet who was employed as secretary first by Cardinal Sfondrato and then by Cardinal Borghese, in whose palace he lived.",
            "第5章记 Ferrante Carlo 于1578年生于帕尔马，称其为律师、诗人，并记其先后担任两位枢机秘书。",
        ),
        card_writer.source(
            "5", "123", "05_CHP-5_sec_i.md", "28–33",
            "His real passion was for pictures, and although contemporaries were doubtful about his taste and understanding, he was in touch with Cassiano dal Pozzo and many leading artists.",
            "第5章记其对绘画的兴趣以及与 Cassiano dal Pozzo 和多位艺术家的联系。",
        ),
        card_writer.source(
            "5", "123", "05_CHP-5_sec_i.md", "28–33",
            "His special favourites were the Bolognese and Giovanni Lanfranco from his native Parma. He befriended and commissioned works from all of these and owned a notable collection.",
            "第5章称其喜爱博洛尼亚画家及 Lanfranco，和他们交往、委托作品并拥有重要收藏。",
        ),
        card_writer.source(
            "20", "402", "20_CHP-20Postscript.md", "102",
            "However, Nicholas Turner’s demonstration that some of Bellori’s most famous critical comments on Lanfranco were very closely derived from the writing of Ferrante Carlo shows that I did not fully appreciate the significance of this latter figure when writing about him in Chapter 5.",
            "第20章后记转述 Nicholas Turner 的研究，称 Bellori 关于 Lanfranco 的若干评论很大程度上源自 Ferrante Carlo 的写作，并回指第5章。",
            "该处为 Haskell 转述 Nicholas Turner；本轮未独立查阅该研究。",
        ),
    ],
    "type_notes_zh": "原书正文名为 Ferrante Carlo；索引依姓氏排序，记为 Carlo, Ferrante。中文显示名为工作音译。",
    "type_notes_en": "The prose form is Ferrante Carlo; the index inverts it as Carlo, Ferrante. The Chinese display name is a working transliteration.",
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
    parser = argparse.ArgumentParser(description="Register Ferrante Carlo's cross-chapter person KU")
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

    assert len(manifest) == 1135, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (116, 135)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4705, 4855)
    assert set(row["candidate_id"] for row in groups[GROUP]) == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    first = candidate_by_id["cand-0560"]
    second = candidate_by_id["cand-10983"]
    assert first["suggested_type"] == second["suggested_type"] == KIND
    assert first["canonical_name"] == "Carlo, Ferrante" and first["index_entry_id"] == "C.csv#84"
    assert second["canonical_name"] == "Ferrante Carlo"
    assert second["candidate_source_ref"] == "chp-20:20_CHP-20Postscript:l98-108#L102"
    for cid in MEMBERS:
        row = alignment_by_id[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == GROUP

    rel_path = "04-knowledge/units/persons/ferrante-carlo.md"
    ku_id = "units/persons/ferrante-carlo"
    card_path = UNITS / "persons" / "ferrante-carlo.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == KIND and "ferrante" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(endpoint_ids) == 36 and len(relation_ids) == 24

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
            "dry-run passed: cand-0560/cand-10983 Ferrante Carlo person_group=1 candidate_members=2 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=117 mapped_candidates_after=137 pending_groups=4704 "
            "pending_candidates=4853 manifest_after=1136; chapter 20 explicitly links Ferrante Carlo back to chapter 5"
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
        f"applied: Ferrante Carlo person_groups=1 candidate_members=2 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
