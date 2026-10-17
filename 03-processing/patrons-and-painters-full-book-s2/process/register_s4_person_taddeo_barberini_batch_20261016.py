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
GROUP = "new-person:barberini-taddeo-2a827b7370"
MEMBERS = ("cand-0239",)

RECORD = {
    "candidate": "cand-0239",
    "group": GROUP,
    "slug": "taddeo-barberini",
    "name_zh": "塔代奥·巴贝里尼",
    "name_en": "Taddeo Barberini",
    "description_zh": "哈斯克尔称 Taddeo Barberini 是教皇乌尔班八世的侄子、Antonio 的兄弟；他获授重要政治职位和财富，1627年与 Anna Colonna 成婚，1631年被任命为罗马长官。第2章称他对艺术兴趣有限，第6章在卡斯特罗战争语境中评价其作为总司令的能力。此卡只记录书内人物身份与限定叙述，不作外部核验。",
    "description_en": "Haskell identifies Taddeo Barberini as a nephew of Pope Urban VIII and brother of Antonio. He received important political posts and wealth, married Anna Colonna in 1627, and was made Prefect of Rome in 1631. Chapter 2 says he had little interest in the arts, while Chapter 6 assesses his command during the War of Castro. This card records the identity and qualified account in the book, with no external verification.",
    "context_zh": "第2章 pp.31–32 将 Taddeo 放入乌尔班八世的家族任用语境，称其为 Antonio 的兄弟和教皇侄子，并记其与 Anna Colonna 的婚姻；pp.47–48 记其任命、罗马长官职衔和对 Barberini 宫邸的控制。第6章 p.146 在卡斯特罗战争段落称其为总司令。",
    "context_en": "Chapters 2 (pp. 31–32) place Taddeo in Urban VIII's family appointments, identify him as Antonio's brother and the Pope's nephew, and mention his marriage to Anna Colonna. Pages 47–48 record his appointments, the prefecture of Rome, and his control of the Barberini palace. Chapter 6 (p. 146) names him as commander-in-chief in the account of the War of Castro.",
    "boundary_zh": "本卡只指人物 Taddeo Barberini，不与 Barberini family 集体卡或其兄弟 Antonio Barberini 人物卡合并。正文称其父亲为 papal armies 的最高统帅但未在该处具名，本卡不推定父亲身份；妻子被称为 Anna Colonna，但本卡不据此新增关系。书中对其性格、艺术兴趣和军事能力的评价属于 Haskell 叙述。本轮未新增正式关系或外部生平。",
    "boundary_en": "This card refers to Taddeo Barberini as a person and remains distinct from the Barberini family card and his brother Antonio Barberini's person KU. The text says his father held supreme command of the papal armies but does not name him in that passage, so this card does not infer the father's identity. His wife is named as Anna Colonna, but no formal relation is added here. The book's comments on his character, artistic interests, and military ability remain Haskell's account. No formal relations or external biography are added.",
    "sources": [
        card_writer.source(
            "2", "31", "02_CHP-2_sec_ii.md", "4",
            "Antonio’s brother Taddeo was given important political posts, great wealth",
            "第2章将 Taddeo 明确称为 Antonio 的兄弟，并概述其政治职位与财富。",
        ),
        card_writer.source(
            "2", "32", "02_CHP-2_sec_ii.md", "11",
            "chosen as bride for Don Taddeo",
            "第2章将 Don Taddeo 明确称为教皇的侄子，并在同段记述其与 Anna Colonna 的婚配。",
        ),
        card_writer.source(
            "2", "47", "02_CHP-2_sec_iv.md", "38–40",
            "Taddeo was at once the weakest and the most brutal of the Barberini.",
            "第2章记录 Haskell 对 Taddeo 性格的评价；该评价作为作者叙述保留。",
        ),
        card_writer.source(
            "2", "48", "02_CHP-2_sec_iv.md", "47–48",
            "In 1631 he was given the archaic title of Prefect of Rome",
            "第2章记述 Taddeo 获授罗马长官职衔及其权利主张。",
        ),
        card_writer.source(
            "6", "146", "06_CHP-6_sec_i.md", "6",
            "Don Taddeo showed his disastrous limitations as commander-in-chief",
            "第6章在卡斯特罗战争语境中评价 Taddeo 的总司令表现。",
        ),
    ],
    "type_notes_zh": "规范名采用第2章正文所用 Taddeo Barberini；Don Taddeo 为同一书内称谓。中文显示名为音译。",
    "type_notes_en": "The normalized name follows the Taddeo Barberini form used in Chapter 2. Don Taddeo is another form used in the same account. The Chinese display name is transliterated.",
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


def get_group(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description="Register Taddeo Barberini as one S4 person KU")
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
    assert len(manifest) == 1130, f"unexpected manifest count: {len(manifest)}"

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
    assert len(current) == 12403 and counts == {"same": 1685, "new": 4996, "conflict": 7, "excluded": 97, "undecided": 5618}, counts
    assert len(new_groups) == 4826
    registered_groups = {group: rows for group, rows in registered.items() if rows}
    assert (len(registered_groups), sum(map(len, registered_groups.values()))) == (111, 126)
    for group, rows in registered_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        assert len(mapped) == len(new_groups[group]) and len({row["ku_id"] for row in mapped}) == 1, group

    candidate_id = MEMBERS[0]
    candidate = candidate_by_id[candidate_id]
    alignment = alignment_by_id[candidate_id]
    assert candidate["suggested_type"] == KIND
    assert candidate["canonical_name"] == "Barberini, Taddeo (nephew to Urban VIII)"
    assert alignment["decision"] == "new" and not alignment.get("ku_id")
    assert get_group(alignment["resolution_note"]) == GROUP
    assert new_groups[GROUP] and {row["candidate_id"] for row in new_groups[GROUP]} == set(MEMBERS)

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(row["type"] == "person" and row.get("name_en", "").casefold() == RECORD["name_en"].casefold() for row in manifest)
    assert not any("Taddeo Barberini" in row.get("name_en", "") for row in manifest if row["type"] == "person")

    endpoint_count = 0
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if candidate_id in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_count += 1
    assert endpoint_count == 42, f"unexpected statement endpoint count: {endpoint_count}"

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    planned_manifest = list(manifest)
    planned_by_id[candidate_id]["ku_id"] = ku_id
    planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {ku_id}."
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
    assert (len(planned_registered), sum(sum(bool(row.get("ku_id")) for row in rows) for rows in planned_registered.values())) == (112, 127)
    assert len(planned_manifest) == 1131

    if args.dry_run:
        print(
            "dry-run passed: Taddeo Barberini person_group=1 candidate_members=1 "
            f"statement_endpoints={endpoint_count} registered_groups_after=112 "
            "mapped_candidates_after=127 manifest_after=1131"
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
    print(f"applied: Taddeo Barberini person_groups=1 candidate_members=1 statement_endpoints={endpoint_count} manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
