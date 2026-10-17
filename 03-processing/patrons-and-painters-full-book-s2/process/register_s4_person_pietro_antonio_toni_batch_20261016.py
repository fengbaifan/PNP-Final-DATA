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
GROUP = "new-person:antonio-pietro-priest-toni-antonio-pietro--3f08cc9cc0"
MEMBERS = ("cand-2640",)
KU_ID = "units/persons/pietro-antonio-toni"
REL_PATH = "04-knowledge/units/persons/pietro-antonio-toni.md"


RECORD = {
    "candidate": "cand-2640",
    "group": GROUP,
    "slug": "pietro-antonio-toni",
    "name_zh": "彼得罗·安东尼奥·托尼神父",
    "name_en": "Don Pietro Antonio Toni",
    "description_zh": (
        "第13章称 Don Pietro Antonio Toni 是一位出生于 Modena 附近、后定居 Venice 的神父、收藏家与艺术品经销者。哈斯克尔记述他与当时多位艺术家交往，尤其与 Sebastiano Ricci 亲近；Ricci 生病时 Toni 曾照料他，Ricci 后来赠予 Toni 版画与一件《东方三博士来朝》modello。"
        "Toni 还曾为年轻的 Pietro Antonio Novelli 提供建议与赞助，并在1748年去世时将收藏留给他；他也为 Zaccaria Sagredo、Zanetti、Consul Smith 等收藏者及外国访客充当代理人。"
    ),
    "description_en": (
        "Chapter 13 identifies Don Pietro Antonio Toni as a priest born near Modena who later settled in Venice, a collector, and an art dealer. Haskell recounts his contacts with leading artists, especially his closeness to Sebastiano Ricci: Toni cared for Ricci during an illness, and Ricci later gave him prints and a modello of an Adoration of the Magi. "
        "Toni also advised and patronised the young Pietro Antonio Novelli, to whom he left his collections when he died in 1748; he acted as an agent for collectors including Zaccaria Sagredo, Zanetti, and Consul Smith, as well as foreign visitors."
    ),
    "context_zh": (
        "人物主项为 `T.csv#103`，索引列 pp.345–346。第13章 pp.345–346 连续以全名、姓氏及指代叙述 Toni 的生平、艺术交往、收藏与经销活动。Toni 与 Pietro Antonio Novelli 是不同人物；Ricci、Pittoni、Sagredo、Zanetti、Smith、Pasquetti 等分别保留为关系端点候选，不并入本人物卡。"
    ),
    "context_en": (
        "The person main entry is `T.csv#103`, indexed at pp. 345–346. Chapter 13 (pp. 345–346) uses Toni's full name, surname, and anaphoric references in a continuous account of his life, artistic contacts, collecting, and dealing. Toni and Pietro Antonio Novelli are distinct people; Ricci, Pittoni, Sagredo, Zanetti, Smith, and Pasquetti remain separate relation-endpoint candidates, not part of this person card."
    ),
    "boundary_zh": (
        "卡片依据本书第13章，不补写生卒日期以外的外部生平或身份核验；出生、迁居与去世年份仅保留原书陈述。Haskell 的友谊、照料、馈赠、赞助、代理和收藏陈述均为 S2 候选关系，留待 S6 逐条审核；本卡未新增正式关系，也不将 Novelli 的后续风格评价写成 Toni 的确定因果影响。"
    ),
    "boundary_en": (
        "This card relies on Chapter 13 and adds no external biography or identity check; the birth, move, and death dates are retained only as stated in the book. Haskell's claims about friendship, care, gifts, patronage, agency, and collecting remain S2 relation candidates for individual review in S6. No formal relations are added, and Novelli's later stylistic characterization is not stated as a proven causal effect of Toni."
    ),
    "sources": [
        card_writer.source(
            "13", "345", "13_CHP-13_intro.md", "161–171",
            "the priest Don Pietro Antonio Toni",
            "哈斯克尔称 Toni 是出生于 Modena 附近并于三十年后定居 Venice 的神父，也称其缺钱但热衷收藏。",
            "日期与身份仅按本书陈述保留。",
        ),
        card_writer.source(
            "13", "345", "13_CHP-13_intro.md", "161–171",
            "His closest friend was Sebastiano Ricci",
            "哈斯克尔称 Sebastiano Ricci 是 Toni 最亲近的朋友，并记述 Toni 曾在 Ricci 生病时照料他，Ricci 后来赠予版画及一件 modello。",
            "这些表述对应的正式关系仍待 S6 审查。",
        ),
        card_writer.source(
            "13", "345", "13_CHP-13_intro.md", "161–171",
            "adviser and patron to his special protege the young Pietro Antonio",
            "哈斯克尔称 Toni 是年轻 Pietro Antonio Novelli 的顾问与赞助人，并将收藏留给 Novelli；Haskell 谨慎提出其谈话或许影响 Novelli 后来的写作风格。",
            "保留作者的推测语气，不把影响关系写成确定因果。",
        ),
        card_writer.source(
            "13", "346", "13_CHP-13_intro.md", "173–177",
            "agent for many far more important collectors than himself",
            "哈斯克尔称 Toni 曾为 Zaccaria Sagredo、Zanetti、Consul Smith 与若干外国访客充当代理人。",
            "不据此新增正式代理关系。",
        ),
        card_writer.source(
            "13", "346", "13_CHP-13_intro.md", "173–177",
            "he would go and buy prints from the hunchback Leonardo Pasquetti",
            "哈斯克尔称 Toni 曾以 Pasquetti 的摊位为向导购买版画。",
            "该活动仍作为书内叙述，关系候选留待 S6。",
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
    parser = argparse.ArgumentParser(description="Register the S4 Don Pietro Antonio Toni person group")
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
        assert len(manifest) >= 1158
        assert len(manifest_matches) == 1 and manifest_matches[0].get("card_path") == REL_PATH
        assert card_path.exists() and accepted_registered
        assert member_rows[0]["decision"] == "new" and member_rows[0].get("ku_id") == KU_ID
        assert f"S4 registration: mapped {GROUP} to {KU_ID}." in member_rows[0]["resolution_note"]
        card_text = card_path.read_text(encoding="utf-8-sig")
        assert "彼得罗·安东尼奥·托尼神父（Don Pietro Antonio Toni）" in card_text
        assert "created: '2026-10-16'" in card_text and "updated: '2026-10-16'" in card_text
        validate_sources(card_text)
        endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
        assert (len(endpoint_ids), len(relation_ids)) == (24, 19)
        if args.dry_run:
            print(f"post-apply dry-run passed: Don Pietro Antonio Toni card, accepted entry, candidate mapping, citations, and 24 endpoints / 19 relation candidates verified; manifest={len(manifest)}; no files written")
        else:
            print("already applied: Don Pietro Antonio Toni S4 registration verified; no files written")
        return 0

    assert len(manifest) == 1157, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (138, 174)
    assert (len(person_groups), sum(map(len, person_groups.values()))) == (1087, 1179)
    assert (len(person_registered), sum(map(len, person_registered.values()))) == (32, 61)
    assert (len(person_groups) - len(person_registered), sum(map(len, person_groups.values())) - sum(map(len, person_registered.values()))) == (1055, 1118)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    candidate = candidate_by_id["cand-2640"]
    row = alignment_by_id["cand-2640"]
    assert candidate["suggested_type"] == KIND
    assert candidate["index_entry_id"] == "T.csv#103"
    assert candidate["canonical_name"] == "Toni, Don Pietro Antonio"
    assert row["decision"] == "new" and not row.get("ku_id") and get_group(row["resolution_note"]) == GROUP
    assert not card_path.exists(), f"unexpected existing card: {REL_PATH}"
    assert REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == KIND and "pietro antonio toni" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    validate_sources()
    endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
    assert (len(endpoint_ids), len(relation_ids)) == (24, 19), (len(endpoint_ids), len(relation_ids))

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
        print("dry-run passed: Don Pietro Antonio Toni person_group=1 candidate_members=1 statement_endpoints=24 relation_candidates=19; no same-type KU or existing card; registered_groups_after=139 mapped_candidates_after=175 pending_groups=4681 pending_candidates=4814 manifest_after=1158; no files written")
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
    print(f"applied: Don Pietro Antonio Toni person_groups=1 candidate_members=1 statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; no formal relations added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
