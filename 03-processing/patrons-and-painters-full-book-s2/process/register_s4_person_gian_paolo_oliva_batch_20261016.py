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
GROUP = "new-person:gian-oliva-paolo-b799139c04"
MEMBERS = ("cand-1771", "cand-1775")

RECORD = {
    "candidate": "cand-1771",
    "group": GROUP,
    "slug": "gian-paolo-oliva",
    "name_zh": "吉安·保罗·奥利瓦",
    "name_en": "Gian Paolo Oliva",
    "description_zh": "哈斯克尔称 Gian Paolo Oliva 是耶稣会士，也是 Bernini 的亲密朋友；他后来担任耶稣会总会长。第3章记述他于1680年召 Andrea Pozzo 来罗马，并叙述其推动圣依纳爵纪念工程、1681年去世；第6章再次以耶稣会总会长身份提及他。本卡仅据书内交叉语境登记人物，不把友谊、召请或工程记述写成正式关系，也未作外部核验。",
    "description_en": "Haskell identifies Gian Paolo Oliva as a Jesuit and one of Bernini's closest friends; Oliva later served as General of the Society of Jesus. Chapter 3 says that in 1680 he summoned Andrea Pozzo to Rome and recounts his efforts concerning the monument to Ignatius and his death in 1681. Chapter 6 again refers to him as General of the Jesuits. This card registers the identity from the book's cross-chapter context; it does not turn friendship, the summons, or the project account into formal relations and makes no external verification claim.",
    "context_zh": "第3章 p.64 称 Gian Paolo Oliva 为耶稣会士和 Bernini 的亲密朋友；pp.88、91 以 General Oliva 记述其召请 Andrea Pozzo 及圣依纳爵纪念工程。第6章 p.153 再称其为耶稣会总会长，并置于 Bernini 赴巴黎的政治语境。",
    "context_en": "Chapter 3 (p. 64) names Gian Paolo Oliva as a Jesuit and close friend of Bernini. Pages 88 and 91 refer to him as General Oliva in the accounts of summoning Andrea Pozzo and the Ignatius monument. Chapter 6 (p. 153) again calls him General of the Jesuits in the political context of Bernini's journey to Paris.",
    "boundary_zh": "本卡只指索引所列 Gian Paolo Oliva。cand-1771 的一般人物条目与 cand-1775 的“and Gaulli”交叉子目均锚定第3章这位以全名出现的耶稣会士；第3章后续反复以 Oliva、General Oliva 指称同一人，第6章的 General of the Jesuits 也与之相接。不把 Bernini、Andrea Pozzo、Carlo Maratta 或其他 Jesuit 人物并入本卡。友谊、艺术赞助、召请 Pozzo 及建筑计划仍是书内断言，不构成本轮新增正式关系或外部生平。",
    "boundary_en": "This card refers only to the indexed Gian Paolo Oliva. cand-1771's general entry and cand-1775's “and Gaulli” cross-reference both anchor to the Jesuit named in full in Chapter 3; the subsequent references to Oliva and General Oliva continue the same account, and Chapter 6's General of the Jesuits is consistent with it. Bernini, Andrea Pozzo, Carlo Maratta, and other Jesuits are not merged into this card. Friendship, patronage, the summons to Pozzo, and architectural plans remain book-reported claims and add neither formal relations nor external biography in this batch.",
    "sources": [
        card_writer.source(
            "3", "64", "03_CHP-3_sec_i.md", "21",
            "It was another Jesuit, Gian Paolo Oliva, who became one of Bernini’s closest and most influential friends.",
            "第3章以全名称 Gian Paolo Oliva 为耶稣会士，并称其为 Bernini 的亲密且有影响的朋友。",
        ),
        card_writer.source(
            "3", "88", "03_CHP-3_sec_iv.md", "125",
            "When in 1680 General Oliva summoned to Rome the 38year-old Andrea Pozzo to remedy this state of affairs his ambitions must at last have seemed fulfilled.",
            "第3章称耶稣会总会长 Oliva 于1680年召 Andrea Pozzo 到罗马，处理 S. Ignazio 教堂装饰问题。",
        ),
        card_writer.source(
            "3", "88", "03_CHP-3_sec_iv.md", "126",
            "Some of his paintings had reached Oliva who had shown them to Carlo Maratta. On his advice Pozzo was ordered to Rome. When he arrived after an unhurried journey, Oliva was dead.",
            "第3章接续记述 Oliva 曾将 Pozzo 的画作展示给 Carlo Maratta，并说 Pozzo 抵达时 Oliva 已去世。",
        ),
        card_writer.source(
            "3", "91", "03_CHP-3_sec_iv.md", "161–162",
            "When Oliva became General, he was determined to have the monument to\nIgnatius",
            "第3章以 Oliva 任总会长及其推动圣依纳爵纪念工程的叙述再次指称该人物。",
        ),
        card_writer.source(
            "6", "153", "06_CHP-6_sec_i.md", "86",
            "and Oliva, the General of the Jesuits, who was most anxious to appease the\nFrench, put the greatest moral pressure on him to go.",
            "第6章将 Oliva 称为耶稣会总会长，并记述其对 Bernini 赴巴黎施加的压力。",
        ),
    ],
    "type_notes_zh": "规范名采用第3章的全名 Gian Paolo Oliva；其他相关段落以 Oliva 或 General Oliva 指称。中文名为便于识别的音译，不扩写宗教履历或外部生平。",
    "type_notes_en": "The normalized name follows the full form Gian Paolo Oliva in Chapter 3; related passages use Oliva or General Oliva. The Chinese display name is transliterated, without expanding his religious career or external biography.",
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
    parser = argparse.ArgumentParser(description="Register Gian Paolo Oliva as one S4 person KU")
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
    assert len(manifest) == 1127, f"unexpected manifest count: {len(manifest)}"

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
    counts = {decision: sum(row["decision"] == decision for row in current) for decision in ("same", "new", "conflict", "excluded", "undecided")}
    assert len(current) == 12403 and counts == {"same": 1678, "new": 5003, "conflict": 7, "excluded": 97, "undecided": 5618}, counts
    assert len(new_groups) == 4828
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (108, 119)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Oliva, Gian Paolo"
        assert alignment["decision"] == "new" and not alignment.get("ku_id")
        assert get_group(alignment["resolution_note"]) == GROUP
    assert {row["candidate_id"] for row in new_groups[GROUP]} == set(MEMBERS)

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(row["type"] == "person" and row.get("name_en", "").casefold() == RECORD["name_en"].casefold() for row in manifest)

    endpoint_statement_count = 0
    endpoint_chapters = defaultdict(int)
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            endpoints = {item for item in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) if item}
            if endpoints & set(MEMBERS):
                endpoint_statement_count += 1
                endpoint_chapters[statement["statement_id"].split("-")[1]] += 1
    assert endpoint_statement_count == 56, f"unexpected statement endpoint count: {endpoint_statement_count}"
    assert {"chp3", "chp6"}.issubset(endpoint_chapters), endpoint_chapters

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
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
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(planned_registered), sum(sum(bool(row.get("ku_id")) for row in rows) for rows in planned_registered.values())) == (109, 121)
    assert len(planned_manifest) == 1128

    if args.dry_run:
        print(
            "dry-run passed: Gian Paolo Oliva person_group=1 candidate_members=2 "
            f"statement_endpoints={endpoint_statement_count} registered_groups_after=109 "
            "mapped_candidates_after=121 manifest_after=1128; no external source accessed"
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
    print(f"applied: Gian Paolo Oliva person_groups=1 candidate_members=2 statement_endpoints={endpoint_statement_count} manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
