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
GROUP = "new-person:borgognone-giacomo-courtois-jacques-e79bfdac5a"
MEMBERS = ("cand-0399",)

RECORD = {
    "candidate": "cand-0399",
    "group": GROUP,
    "slug": "jacques-courtois",
    "name_zh": "雅克·库尔图瓦",
    "name_en": "Jacques Courtois / Giacomo Borgognone",
    "description_zh": "哈斯克尔将其称为法国画家 Jacques Courtois，并说明意大利人称他为 Giacomo Borgognone；他于1657年加入耶稣会，早年从第戎来到意大利，后来在 S. Andrea 初修院与 Casa Professa 继续绘画。书中称他与兄弟 Guglielmo 为 Oliva 作画，并记其于1676年去世，未能完成耶稣教堂看台装饰。本卡只记录书内身份与限定叙述；关于其妻之死的杀人说法仅作为传闻保存，不当作事实，也未作外部核验。",
    "description_en": "Haskell identifies him as the French painter Jacques Courtois and says Italians called him Giacomo Borgognone. He entered the Society of Jesus in 1657, having come to Italy from Dijon as a youth, and later continued painting at the S. Andrea novitiate and the Casa Professa. The book says he and his brother Guglielmo painted for Oliva and records his death in 1676 before the intended tribune decoration of the Gesù could be completed. This card records the source-defined identity and qualified account; the allegation concerning his wife's death is preserved only as a rumour, not as fact. No external verification was made.",
    "context_zh": "第3章 pp.78–79 将 Jacques Courtois 与意大利名 Giacomo Borgognone 明确相连，叙述他从第戎来到意大利、1657年加入耶稣会并继续作画；p.79 说他与兄弟 Guglielmo 为 Oliva 作画。第3章 pp.87–88 再以 Giacomo Borgognone 及其兄弟 Guglielmo 的作品和教堂委托讨论其耶稣会艺术活动；p.79 记其于1676年去世，未能完成 Gesù 看台工程。",
    "context_en": "Chapter 3, pp. 78–79, explicitly connects Jacques Courtois with the Italian name Giacomo Borgognone, recounts his move from Dijon to Italy and entry into the Society of Jesus in 1657, and says he continued to paint. Page 79 says he and his brother Guglielmo painted for Oliva. Pages 87–88 revisit Giacomo Borgognone and the work of the brothers in Jesuit commissions; page 79 records his death in 1676 before the Gesù tribune project was completed.",
    "boundary_zh": "本卡指 Jacques Courtois／Giacomo Borgognone，不与其兄弟 Guglielmo 合并。候选 cand-0401、cand-0402 的正文对象是 Guglielmo Borgognone，依据第3章的兄弟关系复用既有人物卡 units/persons/guglielmo-cortese；不把兄弟的 Martyrdom of St. Andrew 委托或其他作品归给本卡。cand-0400 只有索引子目、没有正文锚点，仍为 undecided。关于其妻身份、匿名告解神父及未具名赞助人等候选也不在本卡推定。S2 正式关系候选仍待 S6 审查。",
    "boundary_en": "This card refers to Jacques Courtois / Giacomo Borgognone and remains separate from his brother Guglielmo. Candidates cand-0401 and cand-0402 refer to Guglielmo Borgognone and reuse the existing person card units/persons/guglielmo-cortese on the basis of the Chapter 3 sibling passages. The brother's Martyrdom of St. Andrew commission and other works are not assigned to this card. Candidate cand-0400 has only an index subentry and no body anchor, so it remains undecided. The identity of Courtois's wife, an unnamed confessor, and unnamed patrons is not inferred here. S2 relation candidates remain for S6 review.",
    "sources": [
        card_writer.source(
            "3", "78", "03_CHP-3_sec_iv.md", "16–24",
            "In 1657 a French painter, Jacques Courtois, had entered the Society.",
            "第3章以全名识别 Jacques Courtois，并称其于1657年加入耶稣会。",
        ),
        card_writer.source(
            "3", "78–79", "03_CHP-3_sec_iv.md", "16–24",
            "Courtois—or Giacomo Borgognone as the Italians called him—had come to Italy from Dijon when still only 15",
            "第3章明确把 Jacques Courtois 与意大利名 Giacomo Borgognone 对应，并叙述其早年从第戎来到意大利。",
        ),
        card_writer.source(
            "3", "79", "03_CHP-3_sec_iv.md", "26–33",
            "He and his brother Guglielmo painted much for Oliva",
            "第3章把 Courtois/Giacomo Borgognone 与其兄弟 Guglielmo 分开，并记述二人为 Oliva 作画。",
        ),
        card_writer.source(
            "3", "87", "03_CHP-3_sec_iv.md", "106–116",
            "including even battle pictures by Giacomo Borgognone.",
            "第3章再次以 Giacomo Borgognone 指称其战役画作。",
        ),
        card_writer.source(
            "3", "88", "03_CHP-3_sec_iv.md", "106–116",
            "who was commissioned in 1668 to paint The Martyrdom of St. Andrew for the High Altar",
            "第3章记述 Guglielmo Borgognone 于1668年受托绘制圣安德烈祭坛画；该段续称其兄弟为 Jesuit Giacomo，用于明确兄弟边界。",
        ),
    ],
    "type_notes_zh": "规范名采用第3章的 Jacques Courtois，意大利名 Giacomo Borgognone 按原书作为同一人的名称形式保留。中文名为便于识别的音译。",
    "type_notes_en": "The normalized name follows Jacques Courtois in Chapter 3; Giacomo Borgognone is retained as the source's Italian name for the same person. The Chinese display name is transliterated.",
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


def grouped_ids(rows, decision):
    groups = defaultdict(set)
    for row in rows:
        if row["decision"] == decision:
            group = get_group(row.get("resolution_note", ""))
            assert group, f"{decision} candidate lacks group: {row['candidate_id']}"
            groups[group].add(row["candidate_id"])
    return groups


def main():
    parser = argparse.ArgumentParser(description="Register Jacques Courtois as one S4 person KU")
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
    alignment_by_id = {row["candidate_id"]: row for row in decision_rows(alignments)}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1131, f"unexpected manifest count: {len(manifest)}"
    current = decision_rows(alignments)
    counts = Counter(row["decision"] for row in current)
    assert counts == Counter({"same": 1688, "new": 4993, "undecided": 5618, "excluded": 97, "conflict": 7}), counts
    new_groups = defaultdict(list)
    same_groups = defaultdict(list)
    for row in current:
        group = get_group(row["resolution_note"])
        if row["decision"] == "new":
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            new_groups[group].append(row)
        elif row["decision"] == "same":
            if group:
                same_groups[group].append(row)
    registered = defaultdict(list)
    for group, rows in new_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
            registered[group] = rows
    assert len(new_groups) == 4824
    assert sum(len(rows) > 1 for rows in new_groups.values()) == 132
    assert (len(registered), sum(map(len, registered.values()))) == (112, 127)
    assert len(new_groups) - len(registered) == 4712
    assert sum(map(len, new_groups.values())) - 127 == 4866

    guglielmo_group = "sg3-ku-units-persons-guglielmo-cortese"
    assert {row["candidate_id"] for row in same_groups[guglielmo_group]} == {
        "cand-3063", "cand-3480", "cand-0401", "cand-0402"
    }
    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Borgognone, Giacomo (Jacques Courtois)"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == GROUP
    assert {row["candidate_id"] for row in new_groups[GROUP]} == set(MEMBERS)
    assert alignment_by_id["cand-0400"]["decision"] == "undecided"

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == KIND and row.get("name_en", "").casefold() == RECORD["name_en"].casefold()
        for row in manifest
    )
    assert any(row["ku_id"] == "units/persons/guglielmo-cortese" for row in manifest)

    endpoint_statement_count = 0
    relation_candidate_count = 0
    endpoint_chapters = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            if MEMBERS[0] in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                endpoint_statement_count += 1
                endpoint_chapters.add(statement["statement_id"].split("-")[1])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    relation_candidate_count += 1
    assert endpoint_statement_count == 40, f"unexpected statement endpoint count: {endpoint_statement_count}"
    assert relation_candidate_count == 37, f"unexpected relation-candidate endpoint count: {relation_candidate_count}"
    assert {"chp3", "chp5", "chp9"}.issubset(endpoint_chapters), endpoint_chapters

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
    planned_manifest = list(manifest)
    target = planned_by_id[MEMBERS[0]]
    target["ku_id"] = ku_id
    target["resolution_note"] += f" S4 registration: mapped {GROUP} to {ku_id}."
    planned_manifest.append({
        "ku_id": ku_id,
        "type": KIND,
        "canonical_name": RECORD["name_zh"],
        "name_en": RECORD["name_en"],
        "source_task": TASK,
        "card_path": rel_path,
    })
    planned_registered = defaultdict(list)
    planned_groups = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new":
            group = get_group(row["resolution_note"])
            planned_groups[group].append(row)
            if row.get("ku_id"):
                planned_registered[group].append(row)
    assert all(len(planned_registered[g]) == len(planned_groups[g]) for g in planned_registered)
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (113, 128)
    assert len(planned_manifest) == 1132

    if args.dry_run:
        print(
            "dry-run passed: Jacques Courtois person_group=1 candidate_members=1 "
            f"statement_endpoints={endpoint_statement_count} relation_candidates={relation_candidate_count} "
            "registered_groups_after=113 mapped_candidates_after=128 pending_groups=4711 "
            "pending_candidates=4865 manifest_after=1132; Guglielmo KU remains separate and cand-0400 stays undecided"
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
    print(
        f"applied: Jacques Courtois person_groups=1 candidate_members=1 statement_endpoints={endpoint_statement_count} "
        f"relation_candidates={relation_candidate_count} manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
