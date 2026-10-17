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
GROUP = "new-person:de-marie-medici-0edb22161a"
MEMBERS = ("cand-1631",)

RECORD = {
    "candidate": "cand-1631",
    "group": GROUP,
    "slug": "marie-de-medici",
    "name_zh": "玛丽·德·美第奇",
    "name_en": "Marie de Medici",
    "description_zh": (
        "哈斯克尔称 Marie de Medici 是亨利四世之妻，并认为她的宫廷活动推动意大利艺术影响进入巴黎。"
        "第7章记她召 Franz Pourbus the Younger 入巴黎、营建新宫，并于1621年委托 Rubens 为长廊绘制她与亨利四世生平的寓意场景；"
        "第2章也提及 Rubens 为二人创作的寓意组画。第7章关于意大利艺术家的论述称，唯一明确存世的她的委托是 Orazio Gentileschi 的《Public Felicity triumphant over Dangers》。"
        "以上均按原书的记述和范围保留。"
    ),
    "description_en": (
        "Haskell identifies Marie de Medici as the wife of Henri IV and says her court helped Italian artistic influence take hold in Paris. "
        "Chapter 7 records her summoning Franz Pourbus the Younger to Paris, building a new palace, and commissioning Rubens in 1621 "
        "to paint allegorical scenes from her life and Henri IV's in its galleries; Chapter 2 also mentions Rubens's cycle for the couple. "
        "Within Chapter 7's discussion of Italian artists, Haskell says the only certain surviving commission from her is "
        "Orazio Gentileschi's Public Felicity triumphant over Dangers. The book's wording and scope are preserved here."
    ),
    "context_zh": (
        "索引 `M.csv#171` 主项列出印刷页53、173–175。第2章 p.53 将 Rubens 为 Marie de Medici 与 Henri IV 创作的寓意组画置于赞助语境；"
        "第7章 pp.173–175 连续讨论她的家族联系、宫廷艺术活动、建筑计划和绘画委托。"
    ),
    "context_en": (
        "The main entry `M.csv#171` indexes printed pages 53 and 173–175. Chapter 2 (p. 53) places Rubens's allegorical cycle for "
        "Marie de Medici and Henri IV in its account of artistic patronage; Chapter 7 (pp. 173–175) discusses her family connections, "
        "courtly art activity, building plans, and picture commissions in sequence."
    ),
    "boundary_zh": (
        "本卡仅指书中以 Marie de Medici 为名的同一人物，不据其家族关系替代具体端点。关于 Rubens 长廊与“唯一明确存世委托”的说法按各自章节语境并存，"
        "不以后一表述抹去前一叙述。24条 S2 关系候选仍待 S6 逐条审查，本卡不新增正式关系，也未作外部身份核验。"
    ),
    "boundary_en": (
        "This card refers only to the person named Marie de Medici in the book and does not use family affiliation as a substitute for explicit endpoints. "
        "The account of Rubens's galleries and the statement about the 'only certain surviving commission' are retained in their respective chapter contexts; "
        "the latter does not erase the former. All 24 S2 relation candidates remain for item-by-item S6 review; this card adds no formal relations and records no external identity check."
    ),
    "sources": [
        card_writer.source(
            "2", "53", "02_CHP-2_sec_iv.md", "110–111",
            "Rubens’s allegorical cycle in honour of Marie de Medici and Henri IV in Paris.",
            "第2章将 Rubens 为 Marie de Medici 与 Henri IV 创作的寓意组画置于艺术赞助叙述中。",
        ),
        card_writer.source(
            "7", "173", "07_CHP-7_sec_i.md", "42–43",
            "Henri’s wife, however, was not a Medici for nothing, and it was largely under her guidance that a certain Italian influence began to make itself felt in Paris.",
            "第7章称 Marie de Medici 的宫廷影响推动意大利艺术影响在巴黎出现。",
        ),
        card_writer.source(
            "7", "174", "07_CHP-7_sec_i.md", "50",
            "It was in 1604 that Marie undertook her first important service to the arts.",
            "第7章将 Marie 1604年的一次艺术赞助行动称为她对艺术的重要服务开端。",
        ),
        card_writer.source(
            "7", "174", "07_CHP-7_sec_i.md", "57",
            "was approached and asked to paint the two long galleries in her new palace with allegorical scenes of her life and that of her husband.",
            "第7章记述 1621 年 Rubens 受邀为新宫两条长廊绘制她与 Henri IV 生平的寓意场景。",
        ),
        card_writer.source(
            "7", "175", "07_CHP-7_sec_i.md", "63",
            "Only one certain commission from Marie de Medici survives, but it is entirely typical of her interests at this time.",
            "第7章关于意大利艺术家的论述称，Marie de Medici 唯一明确存世的委托体现了她当时的兴趣。",
            "本句下文指 Orazio Gentileschi 的《Public Felicity triumphant over Dangers》；保留章节讨论范围。",
        ),
    ],
    "type_notes_zh": "中文显示名为便于识别所用工作音译；原书和索引使用 Marie de Medici。",
    "type_notes_en": "The Chinese display name is a working transliteration; the source and index use Marie de Medici.",
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
    parser = argparse.ArgumentParser(description="Register the Marie de Medici person group")
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

    assert len(manifest) == 1139, f"unexpected manifest count: {len(manifest)}"
    decision_counts = Counter(row["decision"] for row in current)
    assert decision_counts == Counter({"same": 1696, "new": 4985, "undecided": 5618, "excluded": 97, "conflict": 7}), decision_counts
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
    assert (len(groups), sum(map(len, groups.values()))) == (4819, 4985)
    assert (len(registered), sum(map(len, registered.values()))) == (120, 149)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4699, 4836)
    assert set(row["candidate_id"] for row in groups[GROUP]) == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id[MEMBERS[0]]
    alignment = alignment_by_id[MEMBERS[0]]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Medici, Marie de"
    assert candidate["index_entry_id"] == "M.csv#171"
    assert candidate["index_page_range"] == "53, 173, 174, 175"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP

    rel_path = "04-knowledge/units/persons/marie-de-medici.md"
    ku_id = "units/persons/marie-de-medici"
    card_path = UNITS / "persons" / "marie-de-medici.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == KIND and "marie de medici" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(endpoint_ids) == 27 and len(relation_ids) == 24, (len(endpoint_ids), len(relation_ids))

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
            "dry-run passed: Marie de Medici person_group=1 candidate_members=1 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=121 mapped_candidates_after=150 pending_groups=4698 "
            "pending_candidates=4835 manifest_after=1140; no new formal relations"
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
        f"applied: Marie de Medici person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
