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
GROUP = "new-person:5th-exeter-19f06f587b"
MEMBERS = ("cand-0984",)
KU_ID = "units/persons/5th-lord-exeter"
REL_PATH = "04-knowledge/units/persons/5th-lord-exeter.md"


RECORD = {
    "candidate": "cand-0984",
    "group": GROUP,
    "slug": "5th-lord-exeter",
    "name_zh": "第五代埃克塞特勋爵",
    "name_en": "5th Lord Exeter",
    "description_zh": (
        "哈斯克尔称第五代埃克塞特勋爵是大规模的绘画收藏者和赞助人；他在1680至1685年间两次赴意大利，并在所到城市委托绘画。"
        "第7章还叙述其跨城市购藏和委托活动，并称其对英国收藏史具有重要作用。"
    ),
    "description_en": (
        "Haskell describes the 5th Lord Exeter as a collector and patron on a far larger scale. He visited Italy twice between 1680 and 1685 "
        "and commissioned paintings in every city he visited. Chapter 7 also recounts his collecting and commissions across Italian cities and "
        "calls his role in the history of English collecting highly significant."
    ),
    "context_zh": (
        "索引 `E.csv#20` 列印刷页197、198、211。第7章 p.197–198 集中叙述其意大利旅行、绘画委托和收藏活动；第8章 p.211 注释又以 “Lord Exeter” 指称一幅售予他的作品。"
    ),
    "context_en": (
        "The index entry `E.csv#20` lists printed pages 197, 198, and 211. Chapter 7 (pp. 197–198) recounts his Italian travels, commissions, and collecting; a Chapter 8 note on p. 211 also refers to a picture sold to 'Lord Exeter.'"
    ),
    "boundary_zh": (
        "本卡采用书中明确给出的称谓，不补写个人姓名、完整世系或未见于本书的头衔。购藏、委托及雇佣陈述均保留原书的语境与范围；相关正式关系留待 S6 审查。"
    ),
    "boundary_en": (
        "This card uses the title supplied by the book and adds no personal name, complete genealogy, or fuller title absent from the source. "
        "Collecting, commissioning, and employment statements retain their source context and scope; formal relations remain for S6 review."
    ),
    "sources": [
        card_writer.source(
            "7", "197", "07_CHP-7_sec_iv.md", "71",
            "collector and patron on a far larger scale",
            "哈斯克尔将第五代埃克塞特勋爵称为大规模的收藏者和赞助人。",
        ),
        card_writer.source(
            "7", "197", "07_CHP-7_sec_iv.md", "72",
            "he commissioned paintings in all the cities he visited.",
            "哈斯克尔称他在1680至1685年间两次赴意，并在所到城市委托绘画。",
        ),
        card_writer.source(
            "7", "198", "07_CHP-7_sec_iv.md", "80",
            "Lord Exeter played a highly significant role in the history of English collecting.",
            "哈斯克尔称 Lord Exeter 对英国收藏史具有重要作用。",
        ),
        card_writer.source(
            "8", "211", "08_CHP-8_sec_i.md", "151",
            "the Flight into Egypt sold to Lord Exeter",
            "第8章注释称一幅由 Carlo Dolci 创作的《逃往埃及》售予 Lord Exeter；本卡只用其作为跨章称谓锚点。",
            "此注定位人物称谓，不据此扩写作品版本、交易细节或收藏流传链。",
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
    parser = argparse.ArgumentParser(description="Register the S4 person group for the 5th Lord Exeter")
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

    assert len(manifest) == 1151, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (132, 164)
    assert (len(person_groups), sum(map(len, person_groups.values()))) == (1087, 1179)
    assert (len(person_registered), sum(map(len, person_registered.values()))) == (26, 51)
    assert (len(person_groups) - len(person_registered), sum(map(len, person_groups.values())) - sum(map(len, person_registered.values()))) == (1061, 1128)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id["cand-0984"]
    alignment = alignment_by_id["cand-0984"]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Exeter, 5th Lord"
    assert candidate["index_entry_id"] == "E.csv#20"
    assert candidate["index_page_range"] == "197, 198, 211"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert "no unique existing person KU matched" in alignment["resolution_note"]
    assert "source anchor gives a full personal name" in alignment["resolution_note"]
    card_path = ROOT / REL_PATH
    assert not card_path.exists() and REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(
        row["type"] == KIND and "exeter" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    )

    endpoint_ids = set()
    relation_ids = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if "cand-0984" in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_ids.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_ids.add(statement["statement_id"])
    assert len(endpoint_ids) == 24 and len(relation_ids) == 21, (endpoint_ids, relation_ids)

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    target_alignment = planned_by_id["cand-0984"]
    note = target_alignment["resolution_note"]
    note = note.replace(
        "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name.",
        "New source-local person candidate: no unique existing person KU matched; source anchor identifies him by the explicit title '5th Lord Exeter' and supplies no personal name.",
    )
    note = note.replace(
        "Grouped with cand-0984 by identical normalized full-name/explicit-alias anchor (5th exeter), not surname-only similarity.",
        "Grouped from the indexed title and the explicit body forms 'The 5th Lord Exeter' and 'Lord Exeter', not surname-only similarity.",
    )
    note += (
        " S3 identity wording clarification 2026-10-16: the earlier phrase 'full personal name' was imprecise; "
        "the source provides a title-level personal referent only, and this card does not infer a personal name."
    )
    target_alignment["resolution_note"] = note
    target_alignment["ku_id"] = KU_ID
    target_alignment["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

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
            "dry-run passed: 5th Lord Exeter person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=133 mapped_candidates_after=165 pending_groups=4687 "
            "pending_candidates=4824 manifest_after=1152; no formal relations added; no files written"
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
        f"applied: 5th Lord Exeter person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
