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
GROUP = "new-person:carl-gustav-tessin-aa1ed44d34"
MEMBERS = ("cand-2552", "cand-2553", "cand-2554")

RECORD = {
    "candidate": "cand-2552",
    "group": GROUP,
    "slug": "carl-gustav-tessin",
    "name_zh": "卡尔·古斯塔夫·特辛伯爵",
    "name_en": "Count Carl Gustav Tessin",
    "description_zh": "哈斯克尔称 Count Tessin 是瑞典人，生于1695年；早年旅行时接触 Watteau，后来担任瑞典王室建筑事务主管，1739年任驻法大使并在巴黎形成当代绘画与素描收藏。书中也记载他与威尼斯艺术圈往来、收藏 Tiepolo 等人的作品，并与 Zanetti 交谊。本卡以索引全名作为显示名，正文多称 Count Tessin；内容限于书内转述，不作外部核验。",
    "description_en": "Haskell identifies Count Tessin as a Swede born in 1695 who encountered Watteau during his early travels, later served as superintendent of the Swedish royal buildings, and became ambassador to France in 1739, assembling a collection of contemporary drawings and paintings in Paris. The book also records his contacts with the Venetian art world, his purchases of works by Tiepolo and others, and his friendship with Zanetti. The display name follows the full index form while the prose usually says Count Tessin; this card is limited to the book's account and makes no external verification claim.",
    "context_zh": "第10章 pp.292–293 以 Count Tessin 叙述其瑞典身份、1695年出生、早年旅行、王室职务、驻法经历及收藏；第13章 pp.341–342 将 Swedish Count Tessin 置于 Zanetti 的威尼斯交游与艺术收藏语境，记述他借助 Zanetti 扩充收藏并向 Tiepolo 致意。三个索引候选分别覆盖人物总项、与 Tiepolo 的关系提示及与 A. M. Zanetti the Elder 的关系提示，正文锚点指向同一位瑞典伯爵。",
    "context_en": "Chapter 10, pp. 292–293, refers to Count Tessin in its account of his Swedish identity, birth in 1695, early travels, royal office, French embassy, and collecting. Chapter 13, pp. 341–342, places the Swedish Count Tessin in Zanetti's Venetian network, recording his use of Zanetti's taste in building his collection and his message to Tiepolo. The three index candidates cover the person entry and its Tiepolo and A. M. Zanetti the Elder cross-references; their body anchors point to the same Swedish count.",
    "boundary_zh": "本卡只指索引所列的 Count Carl Gustav Tessin。第10章与第13章的 Count Tessin / Swedish Count Tessin 由国籍、年代、外交经历、艺术收藏与共同的威尼斯交游语境跨章对应；不把其父（原文未具名的斯德哥尔摩王宫建筑师）、A. M. Zanetti、Tiepolo、Zuccarelli 或被送往 Zanetti 门下的年轻 protégé 并入人物身份。候选关系仍留待 S6 审查；本卡未新增正式关系。",
    "boundary_en": "This card refers only to the Count Carl Gustav Tessin named by the index. The Count Tessin / Swedish Count Tessin passages in Chapters 10 and 13 are grouped across chapters through their nationality, chronology, diplomatic career, art collecting, and shared Venetian context. His father (the unnamed architect of the Stockholm Royal Palace), A. M. Zanetti, Tiepolo, Zuccarelli, and the young protégé sent to Zanetti are distinct people. Candidate relations remain for S6 review; no formal relation is added here.",
    "sources": [
        card_writer.source(
            "10", "292", "10_CHP-10_intro.md", "268–277",
            "Count Tessin was a Swede, son of the architect who had built the Royal Palace in Stockholm.",
            "第10章称 Count Tessin 为瑞典人，并在同段记其1695年出生。",
        ),
        card_writer.source(
            "10", "293", "10_CHP-10_intro.md", "279–290",
            "In 1739 he became ambassador to France and during his three years in Paris he assembled a superb collection of contemporary drawings and paintings",
            "第10章记述 Tessin 于1739年出任驻法大使，并在巴黎形成当代绘画和素描收藏。",
        ),
        card_writer.source(
            "10", "293", "10_CHP-10_intro.md", "279–290",
            "In a well-known letter he enumerated the merits and drawbacks of the leading artists and found that only Tiepolo was ideal.",
            "第10章记载 Tessin 对威尼斯主要艺术家的评议及其对 Tiepolo 的判断。",
        ),
        card_writer.source(
            "13", "341", "13_CHP-13_intro.md", "90–96",
            "Among foreign visitors the Swedish Count Tessin was his especial friend.",
            "第13章将 Swedish Count Tessin 记为 Zanetti 的特别友人。",
        ),
        card_writer.source(
            "13", "342", "13_CHP-13_intro.md", "98–105",
            "Tessin sent friendly messages to Tiepolo",
            "第13章记述 Tessin 经 Zanetti 向 Tiepolo 传递友好问候。",
        ),
    ],
    "type_notes_zh": "规范显示名采用索引全名 Count Carl Gustav Tessin；书内正文多简称 Count Tessin 或 Swedish Count Tessin。中文名为便于识别的音译。",
    "type_notes_en": "The display name follows the full index form Count Carl Gustav Tessin; the book's prose usually shortens this to Count Tessin or Swedish Count Tessin. The Chinese display name is transliterated.",
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
    parser = argparse.ArgumentParser(description="Register the cross-chapter Count Carl Gustav Tessin person group")
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
    alignment_by_id = {row["candidate_id"]: row for row in decision_rows(alignments)}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1133, f"unexpected manifest count: {len(manifest)}"
    current = decision_rows(alignments)
    counts = Counter(row["decision"] for row in current)
    assert counts == Counter({"same": 1688, "new": 4993, "undecided": 5618, "excluded": 97, "conflict": 7}), counts
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = get_group(row["resolution_note"])
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            new_groups[group].append(row)
    for group, rows in new_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
            registered[group] = rows
    assert len(new_groups) == 4824
    assert len(registered) == 114 and sum(map(len, registered.values())) == 131
    assert len(new_groups) - len(registered) == 4710
    assert sum(map(len, new_groups.values())) - 131 == 4862
    assert set(row["candidate_id"] for row in new_groups[GROUP]) == set(MEMBERS)
    assert all(not row.get("ku_id") for row in new_groups[GROUP])

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Tessin, Count Carl Gustav"
        assert row["decision"] == "new" and get_group(row["resolution_note"]) == GROUP
    assert candidate_by_id["cand-2553"]["sub_entry"] == "and Tiepolo"
    assert candidate_by_id["cand-2554"]["sub_entry"] == "and A. M. Zanetti the Elder"

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(row["type"] == KIND and row.get("name_en", "").casefold() == RECORD["name_en"].casefold() for row in manifest)

    endpoint_ids = set()
    relation_ids = set()
    endpoint_by_candidate = Counter()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            matched = [cid for cid in MEMBERS if cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id"))]
            if matched:
                endpoint_ids.add(statement["statement_id"])
                endpoint_by_candidate.update(matched)
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 34 and len(relation_ids) == 28
    assert endpoint_by_candidate == Counter({"cand-2552": 21, "cand-2553": 4, "cand-2554": 12})

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    planned_manifest = list(manifest)
    for cid in MEMBERS:
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
    planned_registered = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new" and row.get("ku_id"):
            planned_registered[get_group(row["resolution_note"])].append(row)
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (115, 134)
    assert len(planned_manifest) == 1134

    if args.dry_run:
        print(
            "dry-run passed: Count Carl Gustav Tessin person_group=1 candidate_members=3 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=115 mapped_candidates_after=134 pending_groups=4709 "
            "pending_candidates=4859 manifest_after=1134; index full name distinguished from book prose form"
        )
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
    print(
        f"applied: Count Carl Gustav Tessin person_groups=1 candidate_members=3 "
        f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
