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
GROUP = "new-person:colonna-lorenzo-onofrio-c75ad3fea2"
MEMBERS = ("cand-0811", "cand-0812", "cand-0813")

RECORD = {
    "candidate": "cand-0811",
    "group": GROUP,
    "slug": "lorenzo-onofrio-colonna",
    "name_zh": "洛伦佐·奥诺弗里奥·科隆纳",
    "name_en": "Lorenzo Onofrio Colonna",
    "description_zh": (
        "哈斯克尔第6章称 Lorenzo Onofrio 是科隆纳家族最有影响的赞助人，记他于1661年与 Maria Mancini 结婚。"
        "他持续扩充家族绘画收藏，对神话寓言与风景尤感兴趣，并委托 Claude 创作风景和八幅神话场景；他也雇用 Giovanni Coli 与 Filippo Gherardi "
        "参与家族宫殿的 Lepanto 大画廊装饰。原书仅推测他与部分画作的题材构思密切相关；本卡保留该限定，不把个人委托与家族整体活动混为一谈。"
    ),
    "description_en": (
        "Chapter 6 identifies Lorenzo Onofrio as the Colonna family's most influential patron and says he married Maria Mancini in 1661. "
        "He continued to expand the family picture collection, preferred mythological fables and landscapes, and commissioned Claude to make landscapes "
        "and a series of eight mythological scenes. He also employed Giovanni Coli and Filippo Gherardi on the Lepanto gallery decoration in the family palace. "
        "Haskell only suggests that Lorenzo was closely connected with the conception of some subjects; this qualification is retained, and his personal "
        "commissions are kept distinct from the family's broader activity."
    ),
    "context_zh": (
        "索引 `C.csv#341` 主项与 `C.csv#342`（employment of Claude）、`C.csv#343`（liking for mythological fables and landscapes）三个条目均使用同一全名，覆盖印刷页155–156。"
        "第6章正文先以 Lorenzo Onofrio 全名确认人物，再在同页叙述 Claude 聘用、绘画题材偏好、婚姻和宫殿装饰。"
    ),
    "context_en": (
        "The main index entry `C.csv#341` and subentries `C.csv#342` (employment of Claude) and `C.csv#343` (liking for mythological fables and landscapes) "
        "use the same full name and cover printed pages 155–156. Chapter 6 names Lorenzo Onofrio before discussing Claude's employment, his subject preferences, "
        "his marriage, and the palace decoration on those pages."
    ),
    "boundary_zh": (
        "本卡只指原书明确称 Lorenzo Onofrio 的个人，不等同于科隆纳家族或其他 Colonna 人物。Claude 的八幅神话画、家庭收藏与家族宫殿装饰分别保留书中的个人／家族语境；"
        "原书对其参与部分题材构思使用推测语气，不据此断言他是创作者或正式委托人。三条 S2 关系候选仍待 S6 逐项审查，本卡不新增正式关系，也未作外部身份核验。"
    ),
    "boundary_en": (
        "This card refers only to the individual Haskell names Lorenzo Onofrio; it is not the Colonna family or another person named Colonna. "
        "Claude's eight mythological pictures, the family collection, and palace decoration retain their personal or collective contexts from the book. "
        "Haskell uses qualified language about Lorenzo's connection with the conception of some subjects; this is not upgraded into authorship or a formal commission. "
        "All 23 S2 relation candidates remain for item-by-item S6 review. This card adds no formal relations and records no external identity check."
    ),
    "sources": [
        card_writer.source(
            "6", "155", "06_CHP-6_sec_i.md", "105",
            "But the most interesting and influential patron of the family was Lorenzo Onofrio, Grand Constable of the Kingdom of Naples.",
            "第6章称 Lorenzo Onofrio 是科隆纳家族最有影响的赞助人，并记其为那不勒斯王国 Grand Constable。",
        ),
        card_writer.source(
            "6", "155", "06_CHP-6_sec_i.md", "106–107",
            "In 1661, at the age of 24, he married Maria Mancini, the niece of Cardinal Mazarin and the first love of Louis XIV.",
            "第6章记 Lorenzo 于1661年、24岁时与 Maria Mancini 结婚。",
        ),
        card_writer.source(
            "6", "155", "06_CHP-6_sec_i.md", "107–108",
            "But his greatest passion seems to have been for mythological fables and landscapes, wherever possible in combination.",
            "第6章称 Lorenzo 似乎尤其偏爱神话寓言与风景，并保留 seems 的限定。",
        ),
        card_writer.source(
            "6", "156", "06_CHP-6_sec_i.md", "113",
            "his employment of Claude, ranging over a period of nearly twenty years, showed the discrimination of his taste.1 After a Landscape with the Flight into Egypt which he bought from the artist in 1662, the year after his marriage, he subsequently commissioned from him a series of eight mythological scenes",
            "第6章称 Lorenzo 聘用 Claude 近20年，1662年购画后又委托其创作八幅神话场景。",
        ),
        card_writer.source(
            "6", "156", "06_CHP-6_sec_i.md", "114–115",
            "suggest that Lorenzo\nOnofrio himself was closely connected with the creation of these beautiful pictures.",
            "第6章推测 Lorenzo Onofrio 与这些画作的构思关系密切；本卡不将这一推测升级为确定事实。",
            "原句以 suggest 表达推论，前文也以 almost certainly 限定部分家族/地产寓意。",
        ),
        card_writer.source(
            "6", "156", "06_CHP-6_sec_i.md", "117",
            "Fourteen years earlier he had employed the two Lucchese artists Giovanni Coli and Filippo Gherardi",
            "第6章称 Lorenzo 聘请 Giovanni Coli 与 Filippo Gherardi 为宫殿大画廊的 Lepanto 壁画方案工作，并说明其祖先为题材对象。",
        ),
    ],
    "type_notes_zh": "中文显示名为便于识别所用工作音译；索引全名写作 Lorenzo Onofrio Colonna，正文称 Lorenzo Onofrio。",
    "type_notes_en": "The Chinese display name is a working transliteration; the index gives Lorenzo Onofrio Colonna and the prose calls him Lorenzo Onofrio.",
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
    parser = argparse.ArgumentParser(description="Register the three-candidate Lorenzo Onofrio Colonna person group")
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

    assert len(manifest) == 1140, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (121, 150)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4698, 4837)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    expected = {
        "cand-0811": ("C.csv#341", ""),
        "cand-0812": ("C.csv#342", "employment of Claude"),
        "cand-0813": ("C.csv#343", "liking for mythological fables and landscapes"),
    }
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Colonna, Lorenzo Onofrio"
        assert (candidate["index_entry_id"], candidate["sub_entry"]) == expected[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == GROUP
    for cid in ("cand-0812", "cand-0813"):
        assert "prior_decision=undecided" in alignment_by_id[cid]["resolution_note"]

    rel_path = "04-knowledge/units/persons/lorenzo-onofrio-colonna.md"
    ku_id = "units/persons/lorenzo-onofrio-colonna"
    card_path = UNITS / "persons" / "lorenzo-onofrio-colonna.md"
    assert card_path.exists() and rel_path not in accepted_text
    draft_text = card_path.read_text(encoding="utf-8-sig")
    assert "title: 洛伦佐·奥诺弗里奥·科隆纳（Lorenzo Onofrio Colonna）" in draft_text
    assert "科隆纳家族的赞助人" in draft_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == KIND and "lorenzo onofrio colonna" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(endpoint_ids) == 27 and len(relation_ids) == 23, (len(endpoint_ids), len(relation_ids))

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
            "dry-run passed: Lorenzo Onofrio Colonna person_group=1 candidate_members=3 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=122 mapped_candidates_after=153 pending_groups=4697 "
            "pending_candidates=4834 manifest_after=1141; existing unaccepted draft will be updated in place; no formal relations added"
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
        f"applied: Lorenzo Onofrio Colonna person_groups=1 candidate_members=3 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; existing draft updated; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
