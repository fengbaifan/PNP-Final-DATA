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
GROUP = "new-person:antonio-conti-b4d2c59e45"
MEMBERS = ("cand-0826", "cand-0827", "cand-0828", "cand-0829", "cand-0830")

RECORD = {
    "candidate": "cand-0826",
    "group": GROUP,
    "slug": "antonio-conti",
    "name_zh": "安东尼奥·孔蒂",
    "name_en": "Antonio Conti",
    "description_zh": (
        "第10章介绍威尼斯贵族 Antonio Conti，记其1713年赴巴黎、1715年赴伦敦结识 Newton、1726年返威尼斯并于1749年去世。"
        "其写作和思想影响 Francesco Algarotti，也为绘画中想象力的作用辩护。原书说 Newton 提议 Conti 入选 Royal Society；"
        "本卡保留“提议”，不将其改写为实际当选。"
    ),
    "description_en": (
        "Chapter 10 introduces the Venetian nobleman Antonio Conti, recording his 1713 visit to Paris, his 1715 journey to "
        "London and meeting with Newton, his return to Venice in 1726, and his death in 1749. His writing and ideas influenced "
        "Francesco Algarotti, and he defended the role of fantasy in painting. Haskell says Newton proposed Conti's election "
        "to the Royal Society; this card preserves that as a proposal and does not state that Conti was elected."
    ),
    "context_zh": (
        "索引 `C.csv#356–360` 的人物主项及 Algarotti、Newton、绘画中的想象力和 Royal Society 交叉子目，指向第10章同一连续叙述中的 Antonio Conti。"
        "第10章 pp.318–320 记其赴法英旅行、与 Newton 交往、1726年回到威尼斯、写作及艺术观；其中 Royal Society 仅为 Newton 提议其入选。"
    ),
    "context_en": (
        "The person entry and the Algarotti, Newton, fantasy-in-painting, and Royal Society subentries in index `C.csv#356–360` "
        "refer to Antonio Conti in the same continuous Chapter 10 account. Pages 318–320 record his travels to France and England, "
        "his contact with Newton, his return to Venice in 1726, his writing, and his views on art; the Royal Society reference is "
        "only Newton's proposal that he be elected."
    ),
    "boundary_zh": (
        "本卡只指原书全名 Antonio Conti。五条索引候选是同一人物主项及其交叉子目，不据姓名相同合并其他 Conti。"
        "Royal Society 子目不能覆盖正文对选举状态的限定；不把提议写成实际当选。书内转述与本轮外部身份核验分开。"
    ),
    "boundary_en": (
        "This card refers only to the person named Antonio Conti in the book. The five index candidates are the person entry "
        "and its cross-reference subentries; other people named Conti are not merged on name similarity. The Royal Society "
        "subentry does not override the prose qualification: a proposal is not recorded as an election. The book's account is "
        "kept separate from external identity verification."
    ),
    "sources": [
        card_writer.source(
            "10", "318", "10_CHP-10_sec_ii.md", "142",
            "Antonio Conti, of noble origins, was among the pioneers of that growing number of Italian intellectuals who realised that a visit to England and France was essential to avoid the stifling provincialism of Venice.",
            "第10章称 Antonio Conti 出身贵族，是较早认识到意大利知识人需访问英法者之一。",
        ),
        card_writer.source(
            "10", "319", "10_CHP-10_sec_ii.md", "145",
            "Newton proposed Conti",
            "第10章以 proposed 表述 Newton 对 Conti 入选 Royal Society 的提议；本卡不据此称其实际当选。",
            "该句其余部分的 OCR 含 U+FFFD 置换符；此处仅摘录可清晰定位的前半句。",
        ),
        card_writer.source(
            "10", "319", "10_CHP-10_sec_ii.md", "148–149",
            "In 1726 Conti returned to Venice, where he spent most of his time until his death in\n1749.",
            "第10章记 Conti 于1726年回到威尼斯，1749年去世。",
        ),
        card_writer.source(
            "10", "320", "10_CHP-10_sec_ii.md", "155–156",
            "Francesco Algarotti, who was in constant correspondence with him, took over many ideas from this Italian pioneer in the understanding of Newton.",
            "第10章称 Francesco Algarotti 与 Conti 保持通信并承接了其关于 Newton 的许多思想。",
        ),
        card_writer.source(
            "10", "319", "10_CHP-10_sec_ii.md", "149",
            "he made an interesting defence of fantasy in painting which chimed in well with contemporary practice",
            "第10章记 Conti 曾为绘画中的想象力辩护，并将其与当时实践相联系。",
        ),
    ],
    "type_notes_zh": "中文显示名为便于识别所用工作音译；原书和索引使用 Antonio Conti。",
    "type_notes_en": "The Chinese display name is a working transliteration for readability; the source and index use Antonio Conti.",
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
    parser = argparse.ArgumentParser(description="Register the five-candidate Antonio Conti person group")
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

    assert len(manifest) == 1136, f"unexpected manifest count: {len(manifest)}"
    decision_counts = Counter(row["decision"] for row in current)
    assert decision_counts == Counter({"same": 1691, "new": 4990, "undecided": 5618, "excluded": 97, "conflict": 7}), decision_counts
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
    assert (len(groups), sum(map(len, groups.values()))) == (4821, 4990)
    assert (len(registered), sum(map(len, registered.values()))) == (117, 137)
    assert (len(groups) - len(registered), sum(map(len, groups.values())) - sum(map(len, registered.values()))) == (4704, 4853)
    assert set(row["candidate_id"] for row in groups[GROUP]) == set(MEMBERS)
    assert all(not row.get("ku_id") for row in groups[GROUP])

    for cid in MEMBERS:
        candidate = candidate_by_id[cid]
        row = alignment_by_id[cid]
        assert candidate["suggested_type"] == KIND
        assert candidate["canonical_name"] == "Conti, Antonio"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == GROUP
    assert candidate_by_id["cand-0826"]["index_entry_id"] == "C.csv#356"
    assert candidate_by_id["cand-0827"]["sub_entry"] == "and Francesco Algarotti"
    assert candidate_by_id["cand-0828"]["sub_entry"] == "and Sir Isaac Newton"
    assert candidate_by_id["cand-0829"]["sub_entry"] == "defence of fantasy in painting"
    assert candidate_by_id["cand-0830"]["sub_entry"] == "election to Royal Society"

    rel_path = "04-knowledge/units/persons/antonio-conti.md"
    ku_id = "units/persons/antonio-conti"
    card_path = UNITS / "persons" / "antonio-conti.md"
    assert not card_path.exists() and rel_path not in accepted_text
    assert not any(row["ku_id"] == ku_id or row["card_path"] == rel_path for row in manifest)
    assert not any(
        row["type"] == KIND and "antonio conti" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
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
    assert len(endpoint_ids) == 36 and len(relation_ids) == 19

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
            "dry-run passed: cand-0826..cand-0830 Antonio Conti person_group=1 candidate_members=5 "
            f"statement_endpoints={len(endpoint_ids)} relation_candidates={len(relation_ids)} "
            "registered_groups_after=118 mapped_candidates_after=142 pending_groups=4703 "
            "pending_candidates=4848 manifest_after=1137; Royal Society election is recorded as Newton's proposal only"
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
        f"applied: Antonio Conti person_groups=1 candidate_members=5 statement_endpoints={len(endpoint_ids)} "
        f"relation_candidates={len(relation_ids)} manifest={len(planned_manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
