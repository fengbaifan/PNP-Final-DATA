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
GROUP = "new-person:gasparo-gozzi-3503eaac17"
MEMBERS = ("cand-1220", "cand-1223")
KU_ID = "units/persons/gasparo-gozzi"
REL_PATH = "04-knowledge/units/persons/gasparo-gozzi.md"


RECORD = {
    "candidate": "cand-1220",
    "group": GROUP,
    "slug": "gasparo-gozzi",
    "name_zh": "加斯帕罗·戈齐",
    "name_en": "Gasparo Gozzi",
    "description_zh": (
        "哈斯克尔称 Gasparo Gozzi 是 Goldoni 的热心崇拜者，并在威尼斯贵族圈中依附于较开明的贵族；第10章另以 Gaspare Gozzi 拼写，记他批评建筑装饰、编辑《Osservatore Veneto》，"
        "为 Goldoni 辩护并评论 Pietro Longhi 与 Tiepolo。哈斯克尔还概述 Gozzi 以寓言讨论绘画的自然性与劳作者、1782年访问 Padua 的 Arena 礼拜堂后倡议以公共艺术表现公民德行，以及他为 Giorgio Pisani 撰写颂词。"
    ),
    "description_en": (
        "Haskell calls Gasparo Gozzi an ardent admirer of Goldoni and describes him as dependent on more open-minded Venetian nobles. Chapter 10 also spells the name Gaspare Gozzi and recounts his criticism of architectural ornament, editorship of Osservatore Veneto, defence of Goldoni, and writing on Pietro Longhi and Tiepolo. "
        "Haskell also discusses Gozzi's fable about natural images and working people, his 1782 visit to the Arena Chapel in Padua and proposal for public art representing civic virtues, and his tribute for Giorgio Pisani."
    ),
    "context_zh": (
        "索引人物主项 `G.csv#128` 与子目 `G.csv#131`（support for Giorgio Pisani）均为 person 候选。第10章 pp.321、323–326 在连续论述中以 Gaspare / Gasparo Gozzi 明确指称同一作者；p.323 另称 Carlo 是其兄弟。此卡只收录 Gasparo 人物候选，不合并其兄 Carlo、关于其文章的 archive 候选、观点 term 候选或未具名颂词 archive 候选。"
    ),
    "context_en": (
        "The person main entry `G.csv#128` and subentry `G.csv#131` (support for Giorgio Pisani) are both person candidates. Chapters 10 (pp. 321, 323–326) refer to the same author as Gaspare / Gasparo Gozzi in a continuous account; p. 323 identifies Carlo as his brother. This card includes only the Gasparo person candidates, not his brother Carlo, archive candidates for his articles, term candidates for his views, or the unidentified tribute archive candidate."
    ),
    "boundary_zh": (
        "本卡依据本书中 Gasparo / Gaspare Gozzi 的具名语境，不补写生卒年或外部身份核验。`cand-9979` 所涉 p.333 “Gaspara Gozzi”与索引 Gasparo p.333 的对应仍为 `conflict`，不由本次登记解决或映射；文章、寓言、书信、期刊及观点保持其各自候选类型，未具名颂词也不并入人物。关系候选留待 S6，本卡未新增正式关系。"
    ),
    "boundary_en": (
        "This card relies on the book's named contexts for Gasparo / Gaspare Gozzi and adds no birth or death dates or external identity check. The p. 333 'Gaspara Gozzi' reference in `cand-9979` remains in `conflict` with the index's Gasparo p. 333 locator; this registration neither resolves nor maps it. Articles, the fable, letters, journal, and views retain their candidate types, and the unidentified tribute is not merged into the person. Relation candidates remain for S6; no formal relations are added here."
    ),
    "sources": [
        card_writer.source(
            "9", "247", "09_CHP-9_intro.md", "27–36",
            "Gasparo Gozzi, his keen admirer",
            "哈斯克尔称 Gasparo Gozzi 是 Goldoni 的热心崇拜者，并在本段描述其在威尼斯社会中的位置。",
            "这是 Haskell 对其社会位置的描述，不扩展为正式雇佣或隶属关系。",
        ),
        card_writer.source(
            "10", "321", "10_CHP-10_sec_ii.md", "165–173",
            "Gaspare Gozzi must certainly have had Lodoli in mind",
            "哈斯克尔推断 Gaspare Gozzi 批评装饰过度的建筑时必然想到 Lodoli，并引述他对建筑服务路人而非居住者的批评。",
            "保留 Haskell 的推断语气；书中说明 Lodoli 自己的著作已失传。",
        ),
        card_writer.source(
            "10", "323", "10_CHP-10_sec_ii.md", "186–192",
            "Gasparo Gozzi, who was also a strong defender of Goldoni",
            "哈斯克尔称 Gasparo Gozzi 是 Goldoni 的有力辩护者，并记其编辑《Osservatore Veneto》及两度撰文评论 Longhi、比较 Longhi 与 Tiepolo。",
            "同段明称 Carlo 是其兄弟；两人保持为不同人物。",
        ),
        card_writer.source(
            "10", "324", "10_CHP-10_sec_ii.md", "194–201",
            "Elsewhere Gasparo Gozzi made the same point with far greater social implications",
            "哈斯克尔概述 Gozzi 的寓言：由一位哲人说明自然、可理解的图像，并借农耕场景表达对劳作者的尊重。",
            "寓言内的哲人、图像和未具名劳作者不由此卡新增为确切人物或作品身份。",
        ),
        card_writer.source(
            "10", "325", "10_CHP-10_sec_ii.md", "203–208",
            "In later years Gozzi turned again to the didactic possibilities of painting",
            "哈斯克尔记述 Gozzi 后来再次讨论绘画的教化作用，倡议在公共场所表现贵族虔敬、公共服务与文学赞助。",
            "所述方案是 Gozzi 的主张，不是已实施的委托或作品。",
        ),
        card_writer.source(
            "10", "326", "10_CHP-10_sec_ii.md", "210–222",
            "Gozzi wrote a tribute",
            "哈斯克尔称 Giorgio Pisani 于1780年获任后，Gozzi 为他撰写颂词。",
            "书中未给颂词题名或全文；相应 archive 候选保持独立且待证。",
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
    parser = argparse.ArgumentParser(description="Register the S4 Gasparo Gozzi person group")
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
    any_registration_artifact = bool(manifest_matches) or card_path.exists() or accepted_registered or any(
        row.get("ku_id") == KU_ID for row in member_rows
    )
    if any_registration_artifact:
        assert len(manifest) >= 1155
        assert len(manifest_matches) == 1 and manifest_matches[0].get("card_path") == REL_PATH
        assert card_path.exists() and accepted_registered
        assert all(row["decision"] == "new" and row.get("ku_id") == KU_ID for row in member_rows)
        assert all(f"S4 registration: mapped {GROUP} to {KU_ID}." in row["resolution_note"] for row in member_rows)
        counts = Counter(row["decision"] for row in decisions)
        assert counts == Counter({"same": 1696, "new": 4989, "undecided": 5615, "excluded": 97, "conflict": 7})
        card_text = card_path.read_text(encoding="utf-8-sig")
        assert "加斯帕罗·戈齐（Gasparo Gozzi）" in card_text
        assert "created: '2026-10-16'" in card_text and "updated: '2026-10-16'" in card_text
        validate_sources(card_text)
        endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
        assert (len(endpoint_ids), len(relation_ids)) == (27, 13)
        if args.dry_run:
            print("post-apply dry-run passed: Gasparo Gozzi S4 card, accepted entry, 2 mappings, citations, and 27 endpoints / 13 relation candidates verified; conflict cand-9979 remains untouched")
        else:
            print("already applied: Gasparo Gozzi S4 registration verified; no files written")
        return 0

    assert len(manifest) == 1154, f"unexpected manifest count: {len(manifest)}"
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
    assert (len(registered), sum(map(len, registered.values()))) == (135, 170)
    assert (len(person_groups), sum(map(len, person_groups.values()))) == (1087, 1179)
    assert (len(person_registered), sum(map(len, person_registered.values()))) == (29, 57)
    assert (len(person_groups) - len(person_registered), sum(map(len, person_groups.values())) - sum(map(len, person_registered.values()))) == (1058, 1122)
    assert {row["candidate_id"] for row in groups[GROUP]} == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    expected = {
        "cand-1220": ("G.csv#128", "Gozzi, Gasparo", ""),
        "cand-1223": ("G.csv#131", "Gozzi, Gasparo", "support for Giorgio Pisani"),
    }
    for candidate_id, (entry, name, subentry) in expected.items():
        candidate = candidate_by_id[candidate_id]
        row = alignment_by_id[candidate_id]
        assert candidate["suggested_type"] == KIND
        assert candidate["index_entry_id"] == entry
        assert candidate["canonical_name"] == name and candidate["sub_entry"] == subentry
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == GROUP

    assert candidate_by_id["cand-1219"]["canonical_name"] == "Gozzi, Carlo"
    assert get_group(alignment_by_id["cand-1219"]["resolution_note"]) != GROUP
    assert alignment_by_id["cand-9979"]["decision"] == "conflict"
    for candidate_id in ("cand-1221", "cand-1222", "cand-1224", "cand-9793"):
        assert candidate_id not in MEMBERS
        assert get_group(alignment_by_id[candidate_id]["resolution_note"]) != GROUP

    assert not card_path.exists(), f"unexpected existing card: {REL_PATH}"
    assert REL_PATH not in accepted_text
    assert not any(row["ku_id"] == KU_ID or row["card_path"] == REL_PATH for row in manifest)
    assert not any(row["type"] == KIND and "gasparo gozzi" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold() for row in manifest)
    validate_sources()
    endpoint_ids, relation_ids = endpoint_counts(MEMBERS)
    assert (len(endpoint_ids), len(relation_ids)) == (27, 13), (len(endpoint_ids), len(relation_ids))

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for candidate_id in MEMBERS:
        planned_by_id[candidate_id]["ku_id"] = KU_ID
        planned_by_id[candidate_id]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}."

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
        print("dry-run passed: Gasparo Gozzi person_group=1 candidate_members=2 statement_endpoints=27 relation_candidates=13; Carlo Gozzi remains separate; cand-9979 p.333 conflict untouched; registered_groups_after=136 mapped_candidates_after=172 pending_groups=4684 pending_candidates=4817 manifest_after=1155; no files written")
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
    print(f"applied: Gasparo Gozzi person_groups=1 candidate_members=2 statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}; Carlo Gozzi remains separate; cand-9979 conflict untouched; no formal relations added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
