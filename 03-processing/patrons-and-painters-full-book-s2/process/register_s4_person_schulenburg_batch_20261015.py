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

BATCH = [
    {
        "candidate": "cand-2401",
        "group": "new-person:johann-marshal-matthias-schulenburg-240303b710",
        "slug": "johann-matthias-schulenburg",
        "name_zh": "约翰·马蒂亚斯·舒伦堡",
        "name_en": "Johann Matthias Schulenburg",
        "description_zh": "第10章以 Johann Matthias Schulenburg 全名识别一名萨克森家族出身的军人，叙述其在1715—1716年保卫 Corfu 后继续服务威尼斯共和国，并在威尼斯领地定居；章节同时将他置于威尼斯外国收藏家语境。第20章后记回顾其收藏及相关研究分歧。本卡登记书中这位人物身份，不将原书叙述转写为外部已核事实。",
        "description_en": "Chapter 10 identifies Johann Matthias Schulenburg by full name as a man from a Saxon family, recounts his 1715–16 defence of Corfu and continued service to the Venetian Republic, and places him among foreign collectors in Venice. The Chapter 20 postscript revisits his collection and later scholarly disagreement. This card registers the person as presented in the book; it does not recast the account as externally verified fact.",
        "context_zh": "第10章候选索引列 p.311，正文 L8 给出全名；同章继续讨论其在威尼斯的收藏与艺术赞助。第9章 p.267 称其购入一批 Castiglione 作品；第20章 p.407 后记回顾其收藏研究。",
        "context_en": "The Chapter 10 index candidate lists p. 311, where the text at L8 gives his full name; the chapter also discusses his collecting and patronage in Venice. Chapter 9 (p. 267) says he bought a group of works by Castiglione, and the Chapter 20 postscript (p. 407) revisits scholarship on his collection.",
        "boundary_zh": "姓名与身份仅按书内全名及跨章同一指称登记；萨克森家族出身、军旅经历和收藏活动均保持为哈斯克尔的书内陈述。OCR L7 页标为 `[Page 1661]`、L17 为 `[Page 312]`，p.311 定位据候选索引暂用，待页图复核。S2 的赞助、委托和收藏断言留待 S6，不在本卡新增正式关系。",
        "boundary_en": "Register the person only under the full name and cross-chapter references in the book; Saxon origin, military service, and collecting remain Haskell's reports. The OCR marker at L7 reads `[Page 1661]` and L17 reads `[Page 312]`; p. 311 is provisionally taken from the index candidate and awaits image review. S2 claims about patronage, commissions, and collecting remain for S6; this card adds no formal relations.",
        "sources": [
            card_writer.source(
                "10", "311", "10_CHP-10_sec_ii.md", "8",
                "Johann Matthias Schulenburg, who came from a Saxon family, was born in 1661.",
                "第10章以全名识别 Schulenburg，并称其出身萨克森家族、1661年出生。",
                "印刷页暂按候选索引定位 p.311；OCR L7 页标异常为[Page 1661]，L17 为[Page 312]，待页图复核。",
            ),
            card_writer.source(
                "9", "267", "09_CHP-9_intro.md", "320–321",
                "Marshall Schulenburg bought a large batch4 among which were several Castigliones",
                "第9章称 Schulenburg 购入一批包含若干 Castiglione 作品的藏品；原书将批次事实与艺术家曾任 Mantua 宫廷画家相连。",
            ),
            card_writer.source(
                "20", "407", "20_CHP-20Postscript.md", "169–171",
                "Marshal Schulenburg’s collection has been discussed in two recent articles.",
                "第20章后记提及两篇新近研究讨论 Schulenburg 的收藏，并呈现对其艺术鉴赏力的不同评价。",
            ),
        ],
        "type_notes_zh": "原书形式为 Johann Matthias Schulenburg；第10章使用 Marshal，其他章节亦见 Field Marshall（保留原文拼写）。本卡不独立核验其军衔、家系或生平。",
        "type_notes_en": "The book gives the name Johann Matthias Schulenburg and uses Marshal in Chapter 10; another passage spells the title Field Marshall. This card does not independently verify his rank, family, or biography.",
    }
]


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
    parser = argparse.ArgumentParser(description="Register the high-priority Schulenburg S4 person group")
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
    assert len(manifest) == 1122, f"unexpected manifest count: {len(manifest)}"

    new_rows = [row for row in alignments if not row.get("external_source") and row.get("decision") == "new"]
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for row in new_rows:
        group = get_group(row["resolution_note"])
        assert group
        new_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
    assert len(new_rows) == 5008 and len(new_groups) == 4831
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (103, 109)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    candidate_endpoints = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        for line in f:
            statement = json.loads(line)
            candidate_endpoints.update(
                cid for cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")) if cid
            )
    record = BATCH[0]
    cid = record["candidate"]
    candidate = candidate_by_id[cid]
    alignment = alignment_by_id[cid]
    assert candidate["suggested_type"] == KIND
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == record["group"]
    assert [row["candidate_id"] for row in new_groups[record["group"]]] == [cid]
    assert cid in candidate_endpoints
    rel_path = f"04-knowledge/units/persons/{record['slug']}.md"
    ku_id = f"units/persons/{record['slug']}"
    card_path = UNITS / "persons" / f"{record['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    for item in record["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (cid, item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_manifest = list(manifest)
    planned_by_id[cid]["ku_id"] = ku_id
    planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {record['group']} to {ku_id}."
    planned_manifest.append({
        "ku_id": ku_id,
        "type": KIND,
        "canonical_name": record["name_zh"],
        "name_en": record["name_en"],
        "source_task": TASK,
        "card_path": rel_path,
    })
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row.get("decision") == "new":
            planned_groups[get_group(row["resolution_note"])].append(row)
    planned_registered = {group: rows for group, rows in planned_groups.items() if any(row.get("ku_id") for row in rows)}
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (104, 110)

    if args.dry_run:
        print("dry-run passed: person_groups=1 candidates=1 registered_groups_after=104 mapped_candidates_after=110 manifest_after=1123")
        return 0

    card_path.write_text(card_writer.make_card(record, KIND), encoding="utf-8-sig", newline="\n")
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
