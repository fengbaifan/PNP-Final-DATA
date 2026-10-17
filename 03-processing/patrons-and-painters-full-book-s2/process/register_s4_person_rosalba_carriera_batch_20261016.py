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
GROUP = "new-person:carriera-rosalba-f0a77ca508"
MEMBERS = ("cand-0581", "cand-0585", "cand-0586", "cand-0588")

RECORD = {
    "candidate": "cand-0581",
    "group": GROUP,
    "slug": "rosalba-carriera",
    "name_zh": "罗萨尔巴·卡列拉",
    "name_en": "Rosalba Carriera",
    "description_zh": "哈斯克尔称 Rosalba Carriera 为威尼斯画家。第10章记述她于1703年绘制鼻烟盒及象牙微型画，Christian Cole 说服她转向粉彩肖像；书中又记她为欧洲访客作肖像，并在18世纪20年代为 Consul Smith 工作。第8章提到她为 Emmanuela Conti 绘制肖像，但该处 OCR 将姓拼作“Garriera”。本卡依据书内跨章同一人物叙述登记身份，保留拼写异文，不作外部核验。",
    "description_en": "Haskell identifies Rosalba Carriera as a Venetian painter. Chapter 10 says that in 1703 she was painting snuff-boxes and miniatures on ivory, and that Christian Cole persuaded her to turn to pastel portraits; it also records portrait commissions from European visitors and her work for Consul Smith in the 1720s. Chapter 8 mentions her portrait of Emmanuela Conti, with the surname rendered as “Garriera” in the OCR. This card registers the identity from the book's cross-chapter account, preserves the spelling variant, and makes no external verification claim.",
    "context_zh": "第10章 p.276 以全名 Rosalba Carriera 介绍她早期绘制鼻烟盒及象牙微型画的经历，并记 Christian Cole 劝其转向粉彩肖像；p.277 记法国收藏家 Crozat 欣赏其粉彩作品。第8章 p.228 记她为 Emmanuela Conti 绘肖像；第10章 p.303 又记 Consul Smith 在18世纪20年代委托她作画。",
    "context_en": "Chapter 10 (p. 276) names Rosalba Carriera and recounts her early work in snuff-boxes and ivory miniatures and Christian Cole's encouragement of pastel portraiture; p. 277 describes the French collector Crozat's interest in her pastels. Chapter 8 (p. 228) mentions her portrait of Emmanuela Conti, and Chapter 10 (p. 303) records commissions for her from Consul Smith in the 1720s.",
    "boundary_zh": "本卡对应索引主词 Rosalba Carriera 的人物身份，涵盖一般人物条目、Emmanuela Conti 肖像、作品价格及为 Consul Smith 工作等子目。第8章出现 OCR 形式 Garriera；第10章其他段落还有 Camera 拼法，按相邻语境保留为来源形式，不拆为不同人物。姓名依据索引和第10章 p.276 的全名规范。粉彩肖像、客户、赞助及交往仍为书内报告，不在本批转为正式关系或外部事实；相关 S2 关系候选待 S6 审查。",
    "boundary_en": "This card represents the person under the index headword Rosalba Carriera and covers the general entry and subentries for the Emmanuela Conti portrait, prices, and work for Consul Smith. Chapter 8 has the OCR form Garriera; other Chapter 10 passages also use Camera. These source forms are retained in context and are not split into separate people. The normalized name follows the index and the full form in Chapter 10 (p. 276). Reports about pastels, clients, patronage, and associations remain book-bounded and are not converted here into formal relations or external facts; related S2 relation candidates remain for S6 review.",
    "sources": [
        card_writer.source(
            "10", "276", "10_CHP-10_intro.md", "9–10",
            "In 1703 the British Ambassador’s first secretary, Christian Cole, came across a\nVenetian girl, Rosalba Carriera, painting snuff-boxes and miniatures on ivory. He persuaded her to turn to pastel portraits and within a few months her delicate, flimsy work was being compared to Guido Reni.",
            "第10章以全名称 Rosalba Carriera 为威尼斯画家，并记 Christian Cole 发现她作鼻烟盒和象牙微型画、劝她转向粉彩肖像。",
        ),
        card_writer.source(
            "10", "277", "10_CHP-10_intro.md", "22",
            "In Rosalba’s pastels which he saw during his visit of 1715 he found exactly what he was looking for",
            "第10章称 Pierre Crozat 在1715年访问威尼斯时见到 Rosalba 的粉彩作品并深受吸引。",
        ),
        card_writer.source(
            "8", "228", "08_CHP-8_sec_ii.md", "208",
            "He did, however, buy a portrait by Rosalba Garriera of his daughter-in-law Emmanuela",
            "第8章记 Zaccaria Conti 买入一幅 Rosalba 为其儿媳 Emmanuela 绘制的肖像；OCR 姓名为 Garriera。",
        ),
        card_writer.source(
            "10", "303", "10_CHP-10_intro.md", "405–406",
            "Among other artists whom Smith was especially patronising in the 1720s was\nRosalba Carriera.",
            "第10章将 Rosalba Carriera 列为 Smith 在18世纪20年代尤其赞助的画家之一。",
        ),
    ],
    "type_notes_zh": "规范名采用索引词头和第10章全名 Rosalba Carriera；书内 Garriera 与 Camera 保留为原书／OCR 拼写形式，未作为另一个身份。中文名为便于识别的音译。",
    "type_notes_en": "The normalized name follows the index headword and the full form Rosalba Carriera in Chapter 10. The source/OCR forms Garriera and Camera are retained as variants, not treated as separate identities. The Chinese display name is transliterated.",
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
    parser = argparse.ArgumentParser(description="Register Rosalba Carriera as one S4 person KU")
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
    assert len(manifest) == 1128, f"unexpected manifest count: {len(manifest)}"

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
    assert len(current) == 12403 and counts == {"same": 1681, "new": 5000, "conflict": 7, "excluded": 97, "undecided": 5618}, counts
    assert len(new_groups) == 4827
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (109, 121)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Carriera, Rosalba"
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
    assert endpoint_statement_count == 49, f"unexpected statement endpoint count: {endpoint_statement_count}"
    assert {"chp8", "chp9", "chp10", "chp13"}.issubset(endpoint_chapters), endpoint_chapters

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
    assert (len(planned_registered), sum(sum(bool(row.get("ku_id")) for row in rows) for rows in planned_registered.values())) == (110, 125)
    assert len(planned_manifest) == 1129

    if args.dry_run:
        print(
            "dry-run passed: Rosalba Carriera person_group=1 candidate_members=4 "
            f"statement_endpoints={endpoint_statement_count} registered_groups_after=110 "
            "mapped_candidates_after=125 manifest_after=1129; no external source accessed"
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
    print(f"applied: Rosalba Carriera person_groups=1 candidate_members=4 statement_endpoints={endpoint_statement_count} manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
