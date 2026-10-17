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
GROUP = "new-person:joseph-m-smith-joseph-smith-de20176f48"
MEMBERS = ("cand-2440", "cand-2442", "cand-2443", "cand-2447", "cand-2468")

RECORD = {
    "candidate": "cand-2440",
    "group": GROUP,
    "slug": "joseph-smith-venice",
    "name_zh": "约瑟夫·史密斯",
    "name_en": "Joseph Smith",
    "description_zh": "哈斯克尔称 Joseph Smith 是联结威尼斯与外部世界的重要人物，也是其时代重要的艺术赞助人。书中记述他约1675年出生，18世纪初作为商人与经营者定居威尼斯，并于1744年成为英国领事；第9章记其向 Sagredo 继承人购买绘画，第19章附录讨论其收藏与皇家收藏的关系。此卡依据书内叙述登记身份，不作外部核验。",
    "description_en": "Haskell presents Joseph Smith as an important link between Venice and the outside world and as a leading art patron of his day. The book reports that he was born around 1675, settled in Venice in the early eighteenth century as a businessman and merchant, and became British Consul in 1744. Chapter 9 notes his purchases from the Sagredo heirs, while the Chapter 19 appendix discusses his collections and their relation to the Royal Collection. This card registers the identity from the book's account and makes no external verification claim.",
    "context_zh": "第9章 p.264 称其为英国领事 Joseph Smith，并记其向 Sagredo 继承人购买作品；第10章 pp.299–300 以全名介绍其来历、威尼斯商贸活动及1744年任英国领事；第19章附录5讨论其收藏与 George III 所购皇家收藏。",
    "context_en": "Chapter 9 (p. 264) names British Consul Joseph Smith among the buyers from the Sagredo heirs. Chapter 10 (pp. 299–300) gives his full name, background, commercial activity in Venice, and 1744 appointment as British Consul. Appendix 5 in Chapter 19 discusses his collections and the works bought by George III for the Royal Collection.",
    "boundary_zh": "本卡对应第10章以“CONSUL JOSEPH SMITH”为题的连续人物叙述，以及第9章领事购藏和第19章皇家收藏附录中的同一 Joseph Smith。五条索引候选覆盖其传记、与 McSwiny、Rosalba Carriera 的关联、Sagredo 购藏及皇家收藏语境；第19章同处出现 Giuseppe Smith 与 Joseph Smith 的目录形式，按后文明确的威尼斯国王领事语境归组。此处仅登记人物身份，不把原书所述购买、委托、收藏和交往改作正式关系或外部核实；相关 S2 断言仍待 S6 审查。",
    "boundary_en": "This card represents the continuous account headed “CONSUL JOSEPH SMITH” in Chapter 10 and the same Joseph Smith in Chapter 9's consular purchase context and Chapter 19's Royal Collection appendix. The five index candidates cover his biography, index links to McSwiny and Rosalba Carriera, the Sagredo purchases, and the Royal Collection context. Chapter 19 uses both Giuseppe Smith and Joseph Smith in catalogue forms; they are grouped here in the surrounding context that explicitly identifies the deceased Joseph Smith as His Majesty's Consul at Venice. This card registers identity only: the book's reports of purchases, commissions, collections, and associations are not made into formal relations or externally verified facts, and relevant S2 claims remain for S6 review.",
    "sources": [
        card_writer.source(
            "9", "264", "09_CHP-9_intro.md", "241–242",
            "Both the British Consul, Joseph\nSmith,4 and his successor, John Udney, were among those who came to buy.",
            "第9章将 Joseph Smith 明确称为英国领事，并记其与继任者 John Udney 都向 Sagredo 继承人购画。",
        ),
        card_writer.source(
            "10", "299", "10_CHP-10_intro.md", "359–361",
            "Twas an Englishman, Joseph Smith, who became the greatest art patron of his day.\nHe was born in about 1675, educated at Westminster School and settled in Venice during the early years of the eighteenth century as a businessman and merchant.",
            "第10章以全名介绍 Joseph Smith，称其为英国人及重要艺术赞助人，并记述其出生、教育和迁居威尼斯的商贸背景。",
        ),
        card_writer.source(
            "10", "299", "10_CHP-10_intro.md", "365",
            "In 1744 he was made British Consul",
            "第10章记 Joseph Smith 于1744年出任英国领事。",
        ),
        card_writer.source(
            "19", "391", "19_CHP-19Appendix.md", "114–118",
            "Consul Smith and the Royal Collection",
            "第19章附录5以领事 Smith 与皇家收藏为题，讨论其1762年向 George III 出售大量绘画与素描。",
        ),
        card_writer.source(
            "19", "394", "19_CHP-19Appendix.md", "161",
            "Joseph Smith, Esq.,",
            "第19章目录标题将有关剩余藏书的目录归于 Joseph Smith, Esq.；紧接下行称其为威尼斯国王领事。",
        ),
    ],
    "type_notes_zh": "规范名采用第10章人物标题和正文中的 Joseph Smith；第19章书目标题还出现 Giuseppe Smith 形式。中文名为便于识别的音译，不扩展家世或外部生平。",
    "type_notes_en": "The normalized name follows the Chapter 10 heading and narrative form Joseph Smith; Chapter 19 catalogue material also uses the form Giuseppe Smith. The Chinese display name is transliterated; no genealogy or external biography is added.",
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
    parser = argparse.ArgumentParser(description="Register the cross-chapter Joseph Smith identity group as one S4 person KU")
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
    assert len(manifest) == 1126, f"unexpected manifest count: {len(manifest)}"

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
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (107, 114)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        alignment = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Smith, Joseph"
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
    assert endpoint_statement_count == 194, f"unexpected statement endpoint count: {endpoint_statement_count}"
    assert {"chp9", "chp10", "chp19"}.issubset(endpoint_chapters), endpoint_chapters

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
    assert (len(planned_registered), sum(sum(bool(row.get("ku_id")) for row in rows) for rows in planned_registered.values())) == (108, 119)
    assert len(planned_manifest) == 1127

    if args.dry_run:
        print(
            "dry-run passed: Joseph Smith person_group=1 candidate_members=5 "
            f"statement_endpoints={endpoint_statement_count} registered_groups_after=108 "
            "mapped_candidates_after=119 manifest_after=1127; no external source accessed"
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
    print(f"applied: Joseph Smith person_groups=1 candidate_members=5 statement_endpoints={endpoint_statement_count} manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
