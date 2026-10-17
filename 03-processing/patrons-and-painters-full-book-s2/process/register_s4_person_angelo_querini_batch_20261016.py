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
GROUP = "new-person:angelo-querini-angelo-querini-s-2a00c0b28f"

RECORD = {
    "candidate": "cand-2075",
    "group": GROUP,
    "slug": "angelo-querini",
    "name_zh": "安杰洛·奎里尼",
    "name_en": "Angelo Querini",
    "description_zh": "哈斯克尔以 Angelo Querini 为威尼斯重要赞助人之一，叙述其对 Lodoli 的兴趣、政治活动及晚年文化与收藏生活。第15章将他置于 Alticchiero 别墅和园林的语境；这些评价和经历均按原书叙述登记，不作外部核验。",
    "description_en": "Haskell presents Angelo Querini as an important Venetian patron and recounts his interest in Lodoli, political activity, and later cultural and collecting life. Chapter 15 places him in the context of the villa and gardens at Alticchiero; these characterizations and events are recorded as the book's account, not as externally verified facts.",
    "context_zh": "第10章 p.320 将 Querini 列为 Lodoli 交往的威尼斯启蒙人物之一；第15章 p.368–369 以其姓名为专节，叙述其赞助、政治活动与晚年文化生活。",
    "context_en": "Chapter 10 (p. 320) names Querini among Lodoli's Venetian associates associated with the Enlightenment; Chapter 15 (pp. 368–69) gives him a dedicated section on his patronage, political activity, and later cultural life.",
    "boundary_zh": "姓名按书内全名和第10、15章回指登记；不将哈斯克尔的评价改写成客观排名，不补未引证的头衔、家系或外部生平。S2 的赞助、收藏及人物交往断言仍留待 S6，不在本卡新增正式关系。中文名为便于识别的音译。",
    "boundary_en": "Register the person from the full name and cross-chapter references in the book. Do not turn Haskell's assessments into objective rankings or add uncited titles, genealogy, or external biography. S2 claims about patronage, collecting, and associations remain for S6; this card adds no formal relations. The Chinese display name is a transliteration for readability.",
    "sources": [
        card_writer.source(
            "10", "320", "10_CHP-10_sec_ii.md", "161",
            "but also Angelo Querini and Giambattista",
            "第10章称 Lodoli 与包括 Angelo Querini 在内的威尼斯启蒙人物交往。",
        ),
        card_writer.source(
            "15", "368", "15_CHP-15_sec_ii.md", "43–45",
            "The last important patron to emerge in Venice, Angelo Querini, carried his ‘enlightened’ views much further than either of these men",
            "第15章以 Angelo Querini 为一位威尼斯赞助人，并以 enlightened 描述其观点。",
        ),
        card_writer.source(
            "15", "369", "15_CHP-15_sec_ii.md", "50–53",
            "After his release he played no further part in active politics, but devoted himself to intellectual and cultural pursuits.",
            "第15章称 Querini 获释后不再参与积极政治，转向知识与文化活动。",
        ),
    ],
    "type_notes_zh": "原书名为 Angelo Querini；音译仅用于中文显示。候选表所列索引页258–373仅作检索范围，本卡所引章页为核读到的书内段落。",
    "type_notes_en": "The book names him Angelo Querini; the Chinese form is for display only. The index range 258–373 is a retrieval range; the citations here identify the checked passages in the book.",
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
    parser = argparse.ArgumentParser(description="Register the cross-chapter Angelo Querini S4 person group")
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
    assert len(manifest) == 1123, f"unexpected manifest count: {len(manifest)}"

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
    assert (len(current), len(new_rows), len(new_groups)) == (12403, 5007, 4830)
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (104, 110)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    cid = RECORD["candidate"]
    candidate = candidate_by_id[cid]
    alignment = alignment_by_id[cid]
    assert candidate["suggested_type"] == KIND
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert [row["candidate_id"] for row in new_groups[GROUP]] == [cid]
    candidate_endpoints = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            candidate_endpoints.update(
                item for item in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) if item
            )
    assert cid in candidate_endpoints

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (cid, item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    planned_by_id[cid]["ku_id"] = ku_id
    planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {ku_id}."
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
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (105, 111)

    if args.dry_run:
        print("dry-run passed: person_groups=1 candidates=1 registered_groups_after=105 mapped_candidates_after=111 manifest_after=1124")
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
    print(f"applied: person_groups=1 candidates=1 manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
