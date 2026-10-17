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
GROUP = "new-person:borromini-francesco-685a6ddd7c"
MEMBERS = ("cand-0404", "cand-0406", "cand-0407")

RECORD = {
    "candidate": "cand-0404",
    "group": GROUP,
    "slug": "francesco-borromini",
    "name_zh": "弗朗切斯科·博罗米尼",
    "name_en": "Francesco Borromini",
    "description_zh": "哈斯克尔将 Francesco Borromini 描述为17世纪罗马建筑师。第2章称他曾协助 Bernini 修改 Barberini 宫方案；第3章记其为 Chiesa Nuova 建造毗邻 Oratorian 的建筑；第6章记他接手圣若望拉特朗大殿的改建，并参与 Piazza Navona 的 S. Agnese 工程。这里仅概述书中明确的建筑工作，不把竞争关系扩写为未证实的因果，也不作外部核验。",
    "description_en": "Haskell presents Francesco Borromini as a seventeenth-century Roman architect. Chapter 2 says he helped Bernini modify the Barberini palace plan; Chapter 3 mentions his design for the building adjoining the Oratorian Chiesa Nuova; Chapter 6 says he took over the remodelling of St John Lateran and worked on S. Agnese in Piazza Navona. This description is limited to the architectural work stated in the book; it does not turn rivalry into an unsupported causal account and makes no external verification claim.",
    "context_zh": "第2章 p.48 记载 Borromini 曾作为 Carlo Maderno 的助手协助 Bernini 修改 Barberini 宫方案；第3章 pp.75–76 记其设计 Chiesa Nuova 附属建筑。第6章 pp.147–148 以全名 Francesco Borromini 介绍其接手拉特朗大殿改建，并说明旧建筑结构限制了设计；p.149 将他与 S. Agnese 的圆顶及立面工程相连。索引主项和 Innocent X、Scalzi church 子项均以同一全名定位上述书内提及。",
    "context_en": "Chapter 2, p. 48, says Borromini assisted Bernini as Carlo Maderno's former assistant on the Barberini palace plan; Chapter 3, pp. 75–76, mention his design for the building adjoining the Chiesa Nuova. Chapter 6, pp. 147–148, names Francesco Borromini and says he took over the remodelling of St John Lateran, whose existing structure constrained the design; p. 149 connects him to the dome and façade of S. Agnese. The main index entry and the Innocent X and Scalzi church subentries point to these source mentions under the same full name.",
    "boundary_zh": "本卡只指 Francesco Borromini 一人。候选 cand-0404、cand-0406、cand-0407 分别来自主索引、Innocent X 子目和 Scalzi church 子目；正文锚点均为同一建筑师，不因此把相关教堂、建筑方案、Bernini 或 Maderno 并入人物身份。原有 `francesco-borromini.md` 文件未列入 manifest 或 accepted.yml，属于未登记旧稿；本轮核对其书内依据后在固定路径改写为当前双语 S4 卡并登记，不把旧稿视作已有 KU。正式关系仍待 S6 审查。",
    "boundary_en": "This card refers to Francesco Borromini as one person. Candidates cand-0404, cand-0406, and cand-0407 come from the main index entry and its Innocent X and Scalzi church subentries; their body anchors point to the same architect. The churches, architectural schemes, Bernini, and Maderno are not merged into his person identity. The pre-existing file `francesco-borromini.md` was not in the manifest or accepted.yml and was an unregistered draft. After checking its book evidence, this batch rewrites that fixed path as the current bilingual S4 card and registers it; the draft is not treated as an existing KU. Formal relations remain for S6 review.",
    "sources": [
        card_writer.source(
            "2", "48", "02_CHP-2_sec_iv.md", "54–63",
            "with the help of his predecessor’s assistant Francesco Borromini made a few modifications",
            "第2章以全名记述 Borromini 协助 Bernini 修改 Barberini 宫方案。",
        ),
        card_writer.source(
            "3", "75", "03_CHP-3_sec_ii.md", "125–135",
            "a building adjoining the Chiesa Nuova by Borromini to accommodate the library and the concerts of religious music",
            "第2章记述 Borromini 为 Chiesa Nuova 设计毗邻建筑，用于图书馆及宗教音乐会。",
        ),
        card_writer.source(
            "6", "147", "06_CHP-6_sec_i.md", "13–24",
            "Francesco Borromini, his hated rival.",
            "第6章以全名介绍 Borromini，并将其与 Bernini 的竞争作为书内关系语境。",
        ),
        card_writer.source(
            "6", "148", "06_CHP-6_sec_i.md", "26–36",
            "Borromini, the most daring of Baroque architects, was told to preserve the essential structure of the old",
            "第6章记述 Borromini 接手拉特朗大殿改建，并说明既有建筑结构对设计的限制。",
        ),
        card_writer.source(
            "6", "149", "06_CHP-6_sec_i.md", "38–46",
            "Borromini's dome and façade of the adjoining S. Agnese.",
            "第6章将 Borromini 与 Piazza Navona 的 S. Agnese 圆顶及立面工程相连。",
        ),
    ],
    "type_notes_zh": "规范名采用第6章正文全名 Francesco Borromini。中文名为便于识别的音译。",
    "type_notes_en": "The normalized name follows the full form Francesco Borromini in Chapter 6. The Chinese display name is transliterated.",
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
    parser = argparse.ArgumentParser(description="Register the cross-chapter Francesco Borromini person group")
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

    assert len(manifest) == 1132, f"unexpected manifest count: {len(manifest)}"
    current = decision_rows(alignments)
    counts = Counter(row["decision"] for row in current)
    assert counts == Counter({"same": 1688, "new": 4993, "undecided": 5618, "excluded": 97, "conflict": 7}), counts
    new_groups = defaultdict(list)
    registered = defaultdict(list)
    for row in current:
        if row["decision"] == "new":
            group = get_group(row["resolution_note"])
            assert group, f"new candidate lacks group: {row['candidate_id']}"
            new_groups[group].append(row)
    for group, rows in new_groups.items():
        mapped = [row for row in rows if row.get("ku_id")]
        if mapped:
            assert len(mapped) == len(rows) and len({row["ku_id"] for row in mapped}) == 1, group
            registered[group] = rows
    assert len(new_groups) == 4824
    assert len(registered) == 113 and sum(map(len, registered.values())) == 128
    assert len(new_groups) - len(registered) == 4711
    assert sum(map(len, new_groups.values())) - 128 == 4865
    assert set(row["candidate_id"] for row in new_groups[GROUP]) == set(MEMBERS)
    assert all(not row.get("ku_id") for row in new_groups[GROUP])

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Borromini, Francesco"
        assert row["decision"] == "new" and get_group(row["resolution_note"]) == GROUP
    assert candidate_by_id["cand-0406"]["sub_entry"] == "and Pope Innocent X"
    assert candidate_by_id["cand-0407"]["sub_entry"] == "Scalzi church in Rome"

    rel_path = f"04-knowledge/units/persons/{RECORD['slug']}.md"
    ku_id = f"units/persons/{RECORD['slug']}"
    card_path = UNITS / "persons" / f"{RECORD['slug']}.md"
    assert card_path.exists(), "the known unregistered draft at the fixed KU path must be reviewed before apply"
    legacy_text = card_path.read_text(encoding="utf-8-sig")
    assert "Francesco Borromini" in legacy_text and "拉特朗" in legacy_text
    assert rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(row["type"] == KIND and row.get("name_en", "").casefold() == RECORD["name_en"].casefold() for row in manifest)

    endpoint_count = 0
    relation_candidate_count = 0
    endpoint_by_candidate = Counter()
    mentions = set()
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as stream:
        for line in stream:
            statement = json.loads(line)
            for cid in MEMBERS:
                if cid in (statement.get("subject_candidate_id"), statement.get("object_candidate_id")):
                    endpoint_count += 1
                    endpoint_by_candidate[cid] += 1
                    if statement.get("qualifiers", {}).get("relation_candidate") is True:
                        relation_candidate_count += 1
    with (TABLES / "mentions.csv").open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["candidate_id"] in MEMBERS:
                mentions.add(row["candidate_id"])
    assert endpoint_count == 33 and endpoint_by_candidate == Counter({"cand-0404": 24, "cand-0406": 9})
    assert relation_candidate_count == 31, relation_candidate_count
    assert mentions == set(MEMBERS), mentions

    for item in RECORD["sources"]:
        source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
        assert item["quote"] in source_path.read_text(encoding="utf-8-sig"), (item["file"], item["quote"])

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in decision_rows(planned_alignment)}
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
    planned_registered = defaultdict(list)
    for row in planned_alignment:
        if not row.get("external_source") and row["decision"] == "new" and row.get("ku_id"):
            planned_registered[get_group(row["resolution_note"])].append(row)
    assert (len(planned_registered), sum(map(len, planned_registered.values()))) == (114, 131)
    assert len(planned_manifest) == 1133

    if args.dry_run:
        print(
            "dry-run passed: Francesco Borromini person_group=1 candidate_members=3 "
            f"statement_endpoints={endpoint_count} relation_candidates={relation_candidate_count} "
            "registered_groups_after=114 mapped_candidates_after=131 pending_groups=4710 "
            "pending_candidates=4862 manifest_after=1133; fixed path will formalize an unaccepted legacy draft"
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
        f"applied: Francesco Borromini person_groups=1 candidate_members=3 statement_endpoints={endpoint_count} "
        f"relation_candidates={relation_candidate_count} manifest={len(planned_manifest)}; unaccepted draft formalized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
