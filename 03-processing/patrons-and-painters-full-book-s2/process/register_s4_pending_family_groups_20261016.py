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
KIND = "family"


BATCH = [
    {
        "members": ["cand-0930", "cand-0931"],
        "group": "sg3-family-dolfinfamily",
        "slug": "dolfin-family-venice",
        "name_zh": "多尔芬家族",
        "name_en": "Dolfin family",
        "description_zh": (
            "哈斯克尔称 Dolfin 是“老式”的显赫家族，并将 Tiepolo 为其绘制的十幅罗马史场景称作该家族在1720年代的赞助活动。"
            "本卡登记书中所指的家族集体，不把家族活动直接分配给某一位成员。"
        ),
        "description_en": (
            "Haskell describes the Dolfin as a prominent family of the old style and places Tiepolo's ten Roman-history scenes for them "
            "among the family's patronage in the 1720s. This card registers the family collective named in the book without assigning "
            "the family's activity to a particular member."
        ),
        "context_zh": "第9章印刷页252将家族称谓、Tiepolo 的十幅场景及其赞助语境并置；D.csv 的家族主项及其 Tiepolo 赞助子目对应此段。",
        "context_en": "Chapter 9 (p. 252) places the family reference alongside Tiepolo's ten-scene cycle and its patronage context; the family heading and Tiepolo-patronage subentry in D.csv point to this passage.",
        "boundary_zh": "不补写完整谱系或成员表；书中所称其对 Aquileia 宗主教区的“近乎垄断”保留为 Haskell 的说法，不补定时期；家族赞助及宗教职位关系候选留待 S6。",
        "boundary_en": "Do not add a complete genealogy or membership list. Preserve Haskell's qualification that the family's hold over the Patriarchate of Aquileia was a 'virtual monopoly' and leave its period unspecified; family-patronage and ecclesiastical-office relation candidates remain for S6.",
        "sources": [
            card_writer.source("9", "252", "09_CHP-9_intro.md", "119", "his greatest patrons of the 1720s", "哈斯克尔称 Tiepolo 为 Dolfin 绘制的十幅罗马史场景属于该家族在1720年代的赞助语境。"),
            card_writer.source("9", "252", "09_CHP-9_intro.md", "119", "They were a tremendous family in the old style.", "哈斯克尔称 Dolfin 是“老式”的显赫家族。"),
        ],
    },
    {
        "members": ["cand-1057"],
        "group": "sg3-family-foscarinifamily",
        "slug": "foscarini-family-venice",
        "name_zh": "福斯卡里尼家族",
        "name_en": "Foscarini family",
        "description_zh": (
            "哈斯克尔称 Marco Foscarini 出身威尼斯最古老的家族之一；第9章 p.259 另引述一位1749年在家族宫殿工作的建筑画家对家族财富的描述。"
            "后者是 Haskell 保存的嵌套转述，不作为独立核实的财产或收入数据。"
        ),
        "description_en": (
            "Haskell says Marco Foscarini descended from one of Venice's oldest families. Chapter 9 (p. 259) also quotes an architectural painter "
            "working at the family palace in 1749 on the family's wealth. That passage is Haskell's nested report, not independently verified "
            "property or income data."
        ),
        "context_zh": "第9章印刷页258以 Marco Foscarini 的家族出身展开叙述；p.259 转述1749年宫中建筑画家的家族财富说法。",
        "context_en": "Chapter 9 (p. 258) introduces Marco Foscarini through his family descent; p. 259 relays a 1749 account of the family's wealth by a painter working at its palace.",
        "boundary_zh": "本卡仅登记书中的家族集体；不补完整谱系、个人售藏者或产权链。p.259 的财富判断及数字保留其转述属性；相关家族成员、财产和收藏关系候选留待 S6。",
        "boundary_en": "This card registers only the family collective named in the book; it adds no complete genealogy, individual seller, or chain of title. Preserve the p. 259 wealth claim and figures as a nested report; family-member, property, and collection relation candidates remain for S6.",
        "sources": [
            card_writer.source("9", "258", "09_CHP-9_intro.md", "185", "Marco Foscarini was descended from one of the oldest families in Venice.", "哈斯克尔称 Marco Foscarini 出身威尼斯最古老的家族之一。"),
            card_writer.source("9", "259", "09_CHP-9_intro.md", "192", "the family is the richest in Venice", "哈斯克尔引述一位1749年在宫中工作的建筑画家称该家族富有；这是嵌套转述，不是独立核实。", "引自 Haskell 所转录的1749年说法；金额、财富判断与所有权链未独立核验。"),
        ],
    },
    {
        "members": ["cand-7617"],
        "group": "sg3-family-cand-7617",
        "slug": "giovanelli-family-venice",
        "name_zh": "焦瓦内利家族",
        "name_en": "Giovanelli family",
        "description_zh": (
            "第8章注4将“the Giovanelli”列为拥有 Giordano 或 Solimena 画作的威尼斯群体之一；第9章又称该家族于1668年获授贵族身份，并购买 Tiepolo、Piazzetta、Canaletto、Zuccarelli 及古代大师的作品。"
            "本卡保留书中的家族集体称谓和两处不同语境。"
        ),
        "description_en": (
            "Chapter 8, note 4, lists 'the Giovanelli' among Venetian groups that owned pictures by either Giordano or Solimena. Chapter 9 says the family was ennobled in 1668 and bought works by Tiepolo, Piazzetta, Canaletto, Zuccarelli, and old masters. "
            "This card preserves the book's family-collective reference across the two contexts."
        ),
        "context_zh": "第8章印刷页214注4与第9章 p.262 分别提供画作所有者群体及购买作品的家族比较；后者明确使用 family 称谓。",
        "context_en": "Chapter 8 (p. 214 n. 4) names an owner group, while Chapter 9 (p. 262) compares the family's purchases and explicitly calls it a family.",
        "boundary_zh": "p.214 的群体性所有权表述不指明具体画作或个人；不把家族与另一条尚未定型的 Giovanelli collection 候选视为同一对象，也不据此确认收藏的完整范围。关系候选留待 S6。",
        "boundary_en": "The group-level ownership statement on p. 214 identifies no particular picture or individual. Keep the family distinct from the separate, still-untyped Giovanelli collection candidate and do not infer the collection's full extent. Relation candidates remain for S6.",
        "sources": [
            card_writer.source("8", "214 n. 4", "08_CHP-8_sec_i_notes_p214_visual-transcription.md", "4", "the Giovanelli and the Widmann all owned pictures by one or other of them", "哈斯克尔称 Giovanelli 与 Widmann 等威尼斯群体拥有 Giordano 或 Solimena 的画作，未逐件指定艺术家。"),
            card_writer.source("9", "262", "09_CHP-9_intro.md", "228", "only the Giovanelli, ennobled in 1668, bought works by Tiepolo, Piazzetta, Canaletto", "哈斯克尔称 Giovanelli 家族于1668年获授贵族身份，并将其购买当代艺术家及古代大师作品作为比较例。"),
        ],
    },
    {
        "members": ["cand-8501"],
        "group": "sg3-family-cand-8501",
        "slug": "miani-family-camerata",
        "name_zh": "卡梅拉塔的米亚尼家族",
        "name_en": "Miani of Camerata",
        "description_zh": (
            "哈斯克尔注8在一组家户雇佣示例中提及“the Miani of Camerata”，并在同一列表中括号引 Alessandro Longhi。"
            "该注未指明具体家族成员，也未将某位艺术家明确配给这个家族。"
        ),
        "description_en": (
            "Haskell's note 8 names 'the Miani of Camerata' in a list of household-employment examples and gives Alessandro Longhi parenthetically in the same list. The note identifies no family member and does not clearly assign a particular artist to this family."
        ),
        "context_zh": "第9章印刷页260注8；该注以多个家族称谓串列家户雇佣示例。",
        "context_en": "Chapter 9 (p. 260 n. 8); the note strings together several family references as household-employment examples.",
        "boundary_zh": "保留来源中的地名限定，不扩展为具体个人、家族成员表或确定的艺术家—家族雇佣关系；括号内 Alessandro Longhi 是引注，不将其当作受雇者。关系候选留待 S6。",
        "boundary_en": "Retain the place qualifier from the source and add no individual, family-membership list, or definite artist-family employment relation. Alessandro Longhi appears as a citation, not as an established employee. Relation candidates remain for S6.",
        "sources": [
            card_writer.source("9", "260 n. 8", "09_CHP-9_intro_notes_p260_visual-transcription.md", "1", "the Miani of Camerata", "哈斯克尔注8将 Miani of Camerata 列入一组家户雇佣示例，但未将具体艺术家配给该家族。", "括号内 Alessandro Longhi 按 S2 记录仅作来源引注，不作为确定的雇佣对象。"),
        ],
    },
    {
        "members": ["cand-8502"],
        "group": "sg3-family-cand-8502",
        "slug": "baglione-family-polazzo",
        "name_zh": "波拉佐的巴廖内家族",
        "name_en": "Baglione of Polazzo",
        "description_zh": (
            "哈斯克尔注8在一组家户雇佣示例中提及“the Baglione of Polazzo”，并在同一列表中括号引 Alessandro Longhi。"
            "该注未指明具体家族成员，也未将某位艺术家明确配给这个家族。"
        ),
        "description_en": (
            "Haskell's note 8 names 'the Baglione of Polazzo' in a list of household-employment examples and gives Alessandro Longhi parenthetically in the same list. The note identifies no family member and does not clearly assign a particular artist to this family."
        ),
        "context_zh": "第9章印刷页260注8；该注以多个家族称谓串列家户雇佣示例。",
        "context_en": "Chapter 9 (p. 260 n. 8); the note strings together several family references as household-employment examples.",
        "boundary_zh": "保留来源中的地名限定；不因同姓与人物 Giovanni Baglione 合并，也不扩展为具体成员或确定的艺术家—家族雇佣关系。括号内 Alessandro Longhi 是引注，不将其当作受雇者。关系候选留待 S6。",
        "boundary_en": "Retain the place qualifier and do not merge this family with the person Giovanni Baglione on surname alone. Add no individual member or definite artist-family employment relation. Alessandro Longhi appears as a citation, not as an established employee. Relation candidates remain for S6.",
        "sources": [
            card_writer.source("9", "260 n. 8", "09_CHP-9_intro_notes_p260_visual-transcription.md", "1", "the Baglione of Polazzo (Alessandro Longhi)", "哈斯克尔注8将 Baglione of Polazzo 列入一组家户雇佣示例；Alessandro Longhi 按 S2 记录为引注而非确定的雇佣对象。"),
        ],
    },
    {
        "members": ["cand-8571"],
        "group": "sg3-family-cand-8571",
        "slug": "sagredo-family-venice",
        "name_zh": "萨格雷多家族",
        "name_en": "Sagredo family",
        "description_zh": (
            "哈斯克尔称 Sagredo 是威尼斯最古老的家族之一，并在第9章 p.263–264 将家族集体叙述与 Zaccaria Sagredo 的收藏活动分别展开。"
            "本卡只登记家族层级身份，不补完整世系。"
        ),
        "description_en": (
            "Haskell counts the Sagredo among the oldest Venetian families and, in Chapter 9 (pp. 263–264), distinguishes the family-level account from Zaccaria Sagredo's collecting activity. This card registers the family identity only and adds no complete genealogy."
        ),
        "context_zh": "第9章印刷页263–264先概述 Sagredo 家族，再转入 Zaccaria 的个人经历与收藏；两种层级不合并。",
        "context_en": "Chapter 9 (pp. 263–264) first describes the Sagredo family and then turns to Zaccaria's personal life and collection; the two levels remain distinct.",
        "boundary_zh": "不据家族集体陈述补出完整成员、继承链或分支；Niccolò、Zaccaria、未具名继承人及 Sagredo 收藏保持各自对象边界，具体成员关系和流转关系不在本卡登记。",
        "boundary_en": "Do not infer a complete membership, succession chain, or branch from the family-level statement. Keep Niccolò, Zaccaria, the unnamed heirs, and the Sagredo collection distinct; this card does not register specific membership or transfer relations.",
        "sources": [
            card_writer.source("9", "263", "09_CHP-9_intro.md", "234", "The Sagredo were among the oldest of Venetian families", "哈斯克尔将 Sagredo 列为威尼斯最古老的家族之一；后文另行叙述 Zaccaria 的个人经历。"),
        ],
    },
]


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


def main():
    parser = argparse.ArgumentParser(description="Register the six remaining S4 family identity groups")
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
    decision_rows = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    alignment_by_id = {row["candidate_id"]: row for row in decision_rows}
    accepted_text = accepted_path.read_text(encoding="utf-8-sig")

    assert len(manifest) == 1145, f"unexpected manifest count: {len(manifest)}"
    decisions = Counter(row["decision"] for row in decision_rows)
    assert decisions == Counter(
        {"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7}
    ), decisions

    new_groups = defaultdict(list)
    registered = defaultdict(list)
    family_groups = defaultdict(list)
    family_registered = defaultdict(list)
    for row in decision_rows:
        if row["decision"] != "new":
            continue
        group = get_group(row["resolution_note"])
        assert group, f"new candidate lacks identity group: {row['candidate_id']}"
        new_groups[group].append(row)
        if candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND:
            family_groups[group].append(row)
        if row.get("ku_id"):
            registered[group].append(row)
            if candidate_by_id[row["candidate_id"]]["suggested_type"] == KIND:
                family_registered[group].append(row)
    for group, rows in registered.items():
        assert len(rows) == len(new_groups[group]) and len({row["ku_id"] for row in rows}) == 1, group
    assert (len(new_groups), sum(map(len, new_groups.values()))) == (4820, 4989)
    assert (len(registered), sum(map(len, registered.values()))) == (126, 157)
    assert (len(family_groups), sum(map(len, family_groups.values()))) == (80, 86)
    assert (len(family_registered), sum(map(len, family_registered.values()))) == (74, 79)
    pending_family = {
        group: rows for group, rows in family_groups.items() if group not in family_registered
    }
    assert (len(pending_family), sum(map(len, pending_family.values()))) == (6, 7)
    assert set(pending_family) == {record["group"] for record in BATCH}

    manifest_by_id = {row["ku_id"]: row for row in manifest}
    planned_manifest = list(manifest)
    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    new_paths = []
    total_endpoints = set()
    total_relation_ids = set()

    for record in BATCH:
        group = record["group"]
        members = set(record["members"])
        rows = new_groups[group]
        assert {row["candidate_id"] for row in rows} == members, (group, rows)
        assert all(not row.get("ku_id") for row in rows), group
        assert all(candidate_by_id[cid]["suggested_type"] == KIND for cid in members)
        ku_id = f"units/families/{record['slug']}"
        rel_path = f"04-knowledge/units/families/{record['slug']}.md"
        card_path = ROOT / rel_path
        assert not card_path.exists(), rel_path
        assert rel_path not in accepted_text, rel_path
        assert ku_id not in manifest_by_id, ku_id
        assert not any(row["card_path"] == rel_path for row in manifest)
        record["ku_id"] = ku_id
        record["rel_path"] = rel_path
        record["card_path"] = card_path
        new_paths.append(rel_path)

        for item in record["sources"]:
            source_path = ROOT / "02-sources" / "02-Markdown" / item["file"]
            source_text = source_path.read_text(encoding="utf-8-sig")
            assert item["quote"] in source_text, (item["file"], item["quote"])

        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines():
            statement = json.loads(line)
            endpoints = {
                statement.get("subject_candidate_id"),
                statement.get("object_candidate_id"),
            }
            if endpoints & members:
                total_endpoints.add(statement["statement_id"])
                if statement.get("qualifiers", {}).get("relation_candidate") is True:
                    total_relation_ids.add(statement["statement_id"])

        for cid in members:
            row = planned_by_id[cid]
            row["ku_id"] = ku_id
            row["resolution_note"] += f" S4 registration: mapped {group} to {ku_id}."
        planned_manifest.append({
            "ku_id": ku_id,
            "type": KIND,
            "canonical_name": record["name_zh"],
            "name_en": record["name_en"],
            "source_task": TASK,
            "card_path": rel_path,
        })

    assert len(total_relation_ids) == 8, (total_endpoints, total_relation_ids)
    assert len(total_endpoints) == 11, total_endpoints

    if args.dry_run:
        print(
            "dry-run passed: family_groups=6 candidate_members=7; "
            f"statement_endpoints={len(total_endpoints)} relation_candidates={len(total_relation_ids)}; "
            "registered_groups_after=132 mapped_candidates_after=164 pending_groups=4688 "
            "pending_candidates=4825 manifest_after=1151; no formal relations added; no files written"
        )
        return 0

    for record in BATCH:
        card_text = card_writer.make_card(record, KIND)
        card_text, date_count = re.subn(
            r"^(created|updated): '2026-10-15'$", r"\1: '2026-10-16'", card_text, flags=re.MULTILINE
        )
        assert date_count == 2, (record["rel_path"], date_count)
        record["card_path"].parent.mkdir(parents=True, exist_ok=True)
        record["card_path"].write_text(card_text, encoding="utf-8-sig", newline="\n")

    write_csv(manifest_path, manifest_fields, planned_manifest)
    write_csv(alignment_path, alignment_fields, planned_alignment)
    accepted_lines = accepted_text.splitlines()
    for rel_path in sorted(new_paths):
        insert_at = next(
            (
                i for i, line in enumerate(accepted_lines)
                if line.startswith("- 04-knowledge/units/") and line[2:] > rel_path
            ),
            next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
        )
        accepted_lines.insert(insert_at, f"- {rel_path}")
    accepted_path.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="")
    print(
        f"applied: family_groups=6 candidate_members=7 statement_endpoints={len(total_endpoints)} "
        f"relation_candidates={len(total_relation_ids)} manifest={len(planned_manifest)}; no formal relations added"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
