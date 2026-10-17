from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml
import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
CARD_REL = "04-knowledge/units/places/palazzo-barberini.md"
KU_ID = "units/places/palazzo-barberini"
PREVIOUS_GROUP = "sg3-place-barberinipalace"
CANDIDATES = ("cand-0240", "cand-0241")
THEATRE_CANDIDATE = "cand-4782"
TARGET_GROUP = "sg3-same-place-palazzo-barberini"


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def counts(rows):
    candidate_rows = [row for row in rows if row.get("candidate_id") and not row.get("external_source")]
    decisions = Counter(row["decision"] for row in candidate_rows)
    same_kus = {row["ku_id"] for row in candidate_rows if row.get("decision") == "same" and row.get("ku_id")}
    new_groups = defaultdict(list)
    for row in candidate_rows:
        if row.get("decision") == "new":
            group = card_writer.get_group(row.get("resolution_note", ""))
            assert group, f"new decision lacks group: {row['candidate_id']}"
            new_groups[group].append(row)
    registered_groups = {group: members for group, members in new_groups.items() if any(r.get("ku_id") for r in members)}
    mapped = sum(bool(r.get("ku_id")) for members in registered_groups.values() for r in members)
    return {
        "same": decisions["same"],
        "same_kus": len(same_kus),
        "new": decisions["new"],
        "new_groups": len(new_groups),
        "conflict": decisions["conflict"],
        "excluded": decisions["excluded"],
        "undecided": decisions["undecided"],
        "registered_groups": len(registered_groups),
        "mapped": mapped,
        "pending_groups": len(new_groups) - len(registered_groups),
        "pending_members": sum(not r.get("ku_id") for r in candidate_rows if r.get("decision") == "new"),
    }


def update_result(result, totals):
    s3_pattern = re.compile(r"same=[\d,]+（指向[\d,]+个既有 KU）、new=[\d,]+（[\d,]+个身份组）")
    result, n = s3_pattern.subn(
        f"same={totals['same']:,}（指向{totals['same_kus']:,}个既有 KU）、new={totals['new']:,}（{totals['new_groups']:,}个身份组）",
        result,
        count=1,
    )
    assert n == 1, "could not update current S3 summary"
    s4_pattern = re.compile(r"S4 已登记\s*[\d,]+组、映射[\d,]+条成员候选；尚待登记[\d,]+组、[\d,]+条映射。")
    result, n = s4_pattern.subn(
        f"S4 已登记{totals['registered_groups']:,}组、映射{totals['mapped']:,}条成员候选；"
        f"尚待登记{totals['pending_groups']:,}组、{totals['pending_members']:,}条映射。",
        result,
        count=1,
    )
    assert n == 1, "could not update current S4 summary"
    return result


def main():
    parser = argparse.ArgumentParser(description="Reuse the existing Palazzo Barberini place KU for two new S3 candidates.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, manifest = read_csv(MANIFEST_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    manifest_row = next((r for r in manifest if r.get("ku_id") == KU_ID), None)
    card_path = ROOT / CARD_REL
    accepted = (ROOT / "04-knowledge" / "accepted.yml").read_text(encoding="utf-8-sig")
    process = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result = RESULT_PATH.read_text(encoding="utf-8-sig")

    assert all(cid in candidate_by_id and candidate_by_id[cid]["suggested_type"] == "place" for cid in CANDIDATES)
    old_rows = [alignment_by_id[cid] for cid in CANDIDATES]
    assert all(row["decision"] == "new" and not row.get("ku_id") for row in old_rows)
    assert all(card_writer.get_group(row["resolution_note"]) == PREVIOUS_GROUP for row in old_rows)
    assert manifest_row and manifest_row["type"] == "place" and manifest_row["card_path"] == CARD_REL
    assert card_path.exists() and CARD_REL in accepted
    card_frontmatter = yaml.safe_load(card_path.read_text(encoding="utf-8-sig").split("---", 2)[1])
    assert card_frontmatter.get("type") == "place" and card_frontmatter.get("sub_type") == "building"
    assert "Palazzo Barberini" in card_frontmatter.get("name_en", "")
    assert alignment_by_id[THEATRE_CANDIDATE]["decision"] == "undecided"

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    direct = [row for row in statements if row.get("subject_candidate_id") in CANDIDATES or row.get("object_candidate_id") in CANDIDATES]
    relation_rows = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert len(direct) == 20, f"unexpected direct statement count: {len(direct)}"
    assert len(relation_rows) == 14, f"unexpected relation candidate count: {len(relation_rows)}"
    source = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
    source_text = " ".join(source.read_text(encoding="utf-8-sig").split())
    assert " ".join("But the most immediately striking feature of the Barberini palace was the theatre.".split()) in source_text

    planned = [dict(row) for row in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned if r.get("candidate_id") and not r.get("external_source")}
    for candidate_id in CANDIDATES:
        target = planned_by_id[candidate_id]
        previous_note = target["resolution_note"]
        target["decision"] = "same"
        target["ku_id"] = KU_ID
        target["process_ref"] = "S3-cross-chapter-place-reuse-2026-10-16"
        if candidate_id == "cand-0240":
            evidence = (
                "B.csv#87 is the Barberini palace main index heading (pp. 46–53); the existing same-type KU is the building "
                "Palazzo Barberini (manifest path and accepted card)."
            )
        else:
            evidence = (
                "B.csv#88 retains the canonical name Barberini palace with sub-entry theatre (pp. 56–58). Chapter 2, p. 57, "
                "calls the theatre a feature of the Barberini palace; the separately named, unidentified theatre candidate "
                "cand-4782 remains undecided and is not merged into this building KU."
            )
        target["resolution_note"] = (
            f"source_ref=B.csv#{'87' if candidate_id == 'cand-0240' else '88'}; existing_ku={CARD_REL}; "
            f"S3 cross-chapter place correction 2026-10-16: same -> {KU_ID}. {evidence} "
            f"prior_decision=new; prior_group={PREVIOUS_GROUP}; prior_resolution_note={previous_note}"
        )

    totals = counts(planned)
    updated_result = update_result(result, totals)
    marker = "### S3 跨章复用纠偏：Barberini palace 复用既有建筑地点（2026-10-16）"
    assert marker not in process and marker not in updated_result
    process_note = (
        f"\n\n{marker}\n\n"
        "cand-0240（B.csv#87，主项）与 cand-0241（B.csv#88，theatre 子目）原裁为同一新 place 组。"
        "第2章 p.57 明称 theatre 是 Barberini palace 的一项特征；独立识别的 theatre 候选 cand-4782 仍是未定身份的内部空间，"
        "不并入建筑卡。既有 KU units/places/palazzo-barberini 的类型为 place/building，卡名 Palazzo Barberini；"
        "故两项均从 new 更正为 same 并映射至该卡。原决定和组号保留在各 alignment resolution_note。"
        f"20条直接 S2 陈述中14条为关系候选，仍留待 S6；本批未修改卡片、manifest 或 accepted。S3 现为 same={totals['same']:,}"
        f"（{totals['same_kus']:,}个既有 KU）、new={totals['new']:,}（{totals['new_groups']:,}组）、conflict={totals['conflict']}、"
        f"excluded={totals['excluded']}、undecided={totals['undecided']:,}。S4 已登记{totals['registered_groups']:,}组/{totals['mapped']:,}条映射，"
        f"待登记{totals['pending_groups']:,}组/{totals['pending_members']:,}条。"
    )
    result_note = (
        "\n\n### place：Barberini palace 跨章身份复用（2026-10-16）\n\n"
        "cand-0240、cand-0241 映射至[既有 Palazzo Barberini 建筑地点卡](../units/places/palazzo-barberini.md)。"
        "theatre 是该宫内部空间的子目；其候选 cand-4782 保留 undecided，不与宫殿建筑合并。20条直接陈述中的14条关系候选仍待 S6。"
        f"当前 S3 same={totals['same']:,}（{totals['same_kus']:,}个既有 KU）、new={totals['new']:,}（{totals['new_groups']:,}组）；"
        f"S4 已登记{totals['registered_groups']:,}组/{totals['mapped']:,}条映射，待登记{totals['pending_groups']:,}组/{totals['pending_members']:,}条。"
    )
    process += process_note
    updated_result += result_note

    if args.dry_run:
        print(f"S3 reuse dry-run passed: {CANDIDATES} -> {KU_ID}")
        print(f"direct statements={len(direct)}; relation candidates={len(relation_rows)}; theatre identity remains undecided")
        print(
            f"S3 same={totals['same']:,}/{totals['same_kus']:,} KUs; new={totals['new']:,}/{totals['new_groups']:,} groups; "
            f"S4 pending={totals['pending_groups']:,} groups/{totals['pending_members']:,} candidates"
        )
        print("existing building card, index entries, and chapter source checked; no files changed")
        return 0

    write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(updated_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATES} -> {KU_ID}; same={totals['same']:,}/{totals['same_kus']:,}; "
        f"new={totals['new']:,}/{totals['new_groups']:,}; S4 pending={totals['pending_groups']:,}/{totals['pending_members']:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
