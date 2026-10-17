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
GROUP = "new-person:giambattista-ricciardi-b81c07f682"
MEMBERS = ("cand-2187",)
KU_ID = "units/persons/giambattista-ricciardi"
REL_PATH = "04-knowledge/units/persons/giambattista-ricciardi.md"

RECORD = {
    "candidate": "cand-2187",
    "group": GROUP,
    "slug": "giambattista-ricciardi",
    "name_zh": "詹巴蒂斯塔·里恰尔迪",
    "name_en": "Giambattista Ricciardi",
    "description_zh": (
        "哈斯克尔第5章称 Giambattista Ricciardi 为 Salvator Rosa 最亲密且挚爱的朋友，并称他是诗人；Rosa 长期为他绘画并向他寻求建议。"
        "哈斯克尔还说 Ricciardi 居于另一座城市，不能提供 Rosa 所求的个人赞助。第7章在1669年书信语境中称他为 Rosa 忠实且长期相伴的朋友。"
    ),
    "description_en": (
        "Chapter 5 calls Giambattista Ricciardi Salvator Rosa's closest and much-loved friend and identifies him as a poet; Rosa continued painting for him "
        "and sought his advice. Haskell also says Ricciardi lived in another town and could not provide the personal patronage Rosa wanted. Chapter 7, "
        "in the context of a 1669 letter, calls him Rosa's loyal and long-suffering friend."
    ),
    "context_zh": (
        "索引主项 `Q-R.csv#114` 列印刷页144、145、169。第5章 p.142 已出现其全名；p.144–145 叙述他与 Rosa 的友情、咨询和书信往来；"
        "第7章 p.169 回述 Rosa 于1669年致他的信。索引页码之外的 p.142 是正文交叉锚点，不另建身份。"
    ),
    "context_en": (
        "The main index entry `Q-R.csv#114` lists printed pages 144, 145, and 169. Chapter 5 already gives his full name on p. 142; pp. 144–145 "
        "describe his friendship, advice, and correspondence with Rosa; Chapter 7 (p. 169) refers back to Rosa's 1669 letter to him. The p. 142 "
        "mention is an additional prose anchor, not a separate identity."
    ),
    "boundary_zh": (
        "本卡仅指书中称为 Giambattista Ricciardi 或 G. B. Ricciardi 的人物，不按姓氏并入其他 Ricciardi 人物，也不吸收致他的信件或信中提及的作品。"
        "哈斯克尔称 Ricciardi 的信未存；关于其性情、文学与艺术判断的内容均是书中评价。其与 Rosa 的友情、咨询和通信不自动登记为正式关系；"
        "23条 S2 关系候选仍须在 S6 逐项审查。本卡未新增正式关系，也未作外部身份核验。"
    ),
    "boundary_en": (
        "This card refers only to the person the book calls Giambattista Ricciardi or G. B. Ricciardi. It does not merge him with other people named Ricciardi "
        "or absorb the letters addressed to him or works mentioned in them. Haskell says Ricciardi's letters have not survived; statements about his character, "
        "literary work, and artistic judgment remain the book's assessments. Friendship, advice, and correspondence with Rosa are not automatically entered as "
        "formal relations. All 23 S2 relation candidates remain for item-by-item S6 review. No formal relation or external identity check is added here."
    ),
    "sources": [
        card_writer.source(
            "5", "142", "05_CHP-5_sec_iv.md", "8–9",
            "his closest friend\nGiambattista Ricciardi.",
            "第5章称 Giambattista Ricciardi 是 Rosa 最亲密的朋友，并在同段记述 Rosa 购买一幅 Van Laer 摹本以取悦他。",
        ),
        card_writer.source(
            "5", "144", "05_CHP-5_sec_iv.md", "28",
            "To find such a patron Rosa had to turn to Florence, the home of his closest friend the poet Giambattista Ricciardi. For him he went on painting a number of pictures long after he had settled in Rome and to him he looked for constant advice",
            "第5章称 Ricciardi 是诗人及 Rosa 最亲密的朋友，记 Rosa 长期为他绘画并向他寻求建议。",
        ),
        card_writer.source(
            "5", "145", "05_CHP-5_sec_iv.md", "35",
            "As his letters have not survived",
            "第5章说明 Ricciardi 的信未存，称其为 Rosa 忠实且挚爱的朋友，同时对其文学作品与艺术判断作出带限定的评价。",
            "保留 Haskell 对 Rosa 判断的转述与 does not seem 的限定。",
        ),
        card_writer.source(
            "5", "145", "05_CHP-5_sec_iv.md", "35",
            "He was certainly a devoted and muchloved friend, but Rosa does not seem to have thought very highly of his artistic judgement",
            "第5章说明 Ricciardi 的信未存，称其为 Rosa 忠实且挚爱的朋友，同时对其文学作品与艺术判断作出带限定的评价。",
            "保留 Haskell 对 Rosa 判断的转述与 does not seem 的限定。",
        ),
        card_writer.source(
            "5", "145", "05_CHP-5_sec_iv.md", "35",
            "And, in any case, Ricciardi lived in a different town and could not therefore give him the personal patronage he wanted.",
            "第5章明确区分 Rosa 与 Ricciardi 的友情和 Rosa 未能从他那里获得个人赞助。",
        ),
        card_writer.source(
            "7", "169", "07_CHP-7_sec_i.md", "3–5",
            "his loyal and long suffering friend\nG. B. Ricciardi",
            "第7章回述 Rosa 于1669年写信给忠实且长期相伴的朋友 G. B. Ricciardi。",
        ),
    ],
    "type_notes_zh": "姓名：索引主项写作 Ricciardi, Giambattista；第7章书信段写作 G. B. Ricciardi。中文名为工作音译。",
    "type_notes_en": "Name: the index main entry is Ricciardi, Giambattista; the Chapter 7 letter passage uses G. B. Ricciardi. The Chinese display name is a working transliteration.",
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
    parser = argparse.ArgumentParser(description="Register the Giambattista Ricciardi person group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    manifest_path = TABLES / "ku-manifest.csv"
    alignment_path = TABLES / "alignment.csv"
    accepted_path = ROOT / "04-knowledge" / "accepted.yml"
    card_path = UNITS / "persons" / "giambattista-ricciardi.md"
    manifest_fields, manifest = read_csv(manifest_path)
    alignment_fields, alignments = read_csv(alignment_path)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    current = decision_rows(alignments)
    alignment_by_id = {row["candidate_id"]: row for row in current}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1141, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (122, 153)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4697, 4834)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id["cand-2187"]
    alignment = alignment_by_id["cand-2187"]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Ricciardi, Giambattista"
    assert candidate["index_entry_id"] == "Q-R.csv#114"
    assert candidate["index_page_range"] == "144, 145, 169"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert "no unique existing person KU matched" in alignment["resolution_note"]
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND and "ricciardi" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if "cand-2187" in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 23 and len(relation_ids) == 23, (len(endpoint_ids), len(relation_ids))

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    planned_by_id["cand-2187"]["ku_id"] = KU_ID
    planned_by_id["cand-2187"]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."
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
            "dry-run passed: Giambattista Ricciardi person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=123 mapped_candidates_after=154 pending_groups=4696 "
            "pending_candidates=4833 manifest_after=1142; no formal relations added"
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
        f"applied: Giambattista Ricciardi person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
