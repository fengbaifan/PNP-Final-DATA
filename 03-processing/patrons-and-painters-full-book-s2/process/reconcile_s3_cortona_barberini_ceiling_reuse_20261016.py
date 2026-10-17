from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
CARD_PATH = ROOT / "04-knowledge" / "units" / "works" / "pietro-da-cortona-glorification-of-the-reign-of-urban-viii.md"
CANDIDATE = "cand-4687"
PLATE_CANDIDATE = "cand-4080"
SCENE_CANDIDATE = "cand-4582"
KU_ID = "units/works/pietro-da-cortona-glorification-of-the-reign-of-urban-viii"
TARGET_GROUP = "sg3-ku-units-works-pietro-da-cortona-glorification-of-the-reign-of-urban-viii"
PREVIOUS_GROUP = "workgrp-e046c2fab34446"
QUOTE_BODY = "There he and Cortona planned the decoration of the great Barberini ceiling (Plate 13)."
QUOTE_PLATE = "13 Pietro da Cortona: Glorification of the Reign of Urban VIII"

def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)

def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def group(note):
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None

def current_progress(rows):
    new_rows = [r for r in rows if r.get("candidate_id") and not r.get("external_source") and r["decision"] == "new"]
    by_group = defaultdict(list)
    for row in new_rows:
        group_id = group(row.get("resolution_note", ""))
        assert group_id, row["candidate_id"]
        by_group[group_id].append(row)
    registered = {g: rs for g, rs in by_group.items() if any(r.get("ku_id") for r in rs)}
    mapped = sum(bool(r.get("ku_id")) for rs in registered.values() for r in rs)
    return len(registered), mapped, len(by_group) - len(registered), len(new_rows) - mapped

def update_progress(process, result, rows, manifest_count):
    registered, mapped, pending_groups, pending_members = current_progress(rows)
    p, pn = re.subn(
        r"已登记\s*[\d,]+\s*组、\s*[\d,]+\s*条成员映射，尚待登记\s*[\d,]+\s*组、\s*[\d,]+\s*条。",
        f"已登记{registered:,}组、{mapped:,}条成员映射，尚待登记{pending_groups:,}组、{pending_members:,}条。",
        process, count=1)
    assert pn == 1
    r, rn = re.subn(
        r"S4 已登记\s*[\d,]+\s*组、映射\s*[\d,]+\s*条成员候选；尚待登记\s*[\d,]+\s*组、\s*[\d,]+\s*条映射。",
        f"S4 已登记{registered:,}组、映射{mapped:,}条成员候选；尚待登记{pending_groups:,}组、{pending_members:,}条映射。",
        result, count=1)
    assert rn == 1
    r, mn = re.subn(
        r"(\|\s*\[KU 登记\]\(\.\./tables/ku-manifest\.csv\)\s*\|\s*)[\d,]+ KU",
        lambda m: f"{m.group(1)}{manifest_count:,} KU", r, count=1)
    assert mn == 1
    return p, r, (registered, mapped, pending_groups, pending_members)

def main():
    parser = argparse.ArgumentParser(description="Correct the S3 identity of the Barberini great-ceiling candidate")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = read_csv(MANIFEST_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    target = by_id[CANDIDATE]
    plate = by_id[PLATE_CANDIDATE]
    scene = by_id[SCENE_CANDIDATE]
    manifest_row = next(r for r in manifest if r["ku_id"] == KU_ID)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    process = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result = RESULT_PATH.read_text(encoding="utf-8-sig")
    assert target["decision"] == "new" and not target.get("ku_id")
    assert group(target["resolution_note"]) == PREVIOUS_GROUP
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "work"
    assert plate["decision"] == "same" and plate.get("ku_id") == KU_ID
    assert scene["decision"] == "new" and scene.get("ku_id", "") == ""
    assert candidate_by_id[SCENE_CANDIDATE]["suggested_type"] == "work"
    assert manifest_row["type"] == "work" and CARD_PATH.exists()
    assert str(CARD_PATH.relative_to(ROOT)).replace("\\", "/") in accepted

    old_group_rows = [
        r for r in alignments if r.get("candidate_id") and not r.get("external_source")
        and r["decision"] == "new" and group(r.get("resolution_note", "")) == PREVIOUS_GROUP
    ]
    assert [r["candidate_id"] for r in old_group_rows] == [CANDIDATE]
    body_source = ROOT / "02-sources" / "02-Markdown" / "02_CHP-2_sec_iv.md"
    plate_source = ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md"
    assert QUOTE_BODY in body_source.read_text(encoding="utf-8-sig")
    assert QUOTE_PLATE in plate_source.read_text(encoding="utf-8-sig")
    with (TABLES / "book-statements.jsonl").open(encoding="utf-8-sig") as f:
        statements = [json.loads(line) for line in f if line.strip()]
    relation_rows = [s for s in statements if CANDIDATE in (s.get("subject_candidate_id"), s.get("object_candidate_id"))
                     and (s.get("qualifiers") or {}).get("relation_candidate") is True]
    assert len(relation_rows) == 18, len(relation_rows)

    planned = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned if r.get("candidate_id") and not r.get("external_source")}
    previous_note = target["resolution_note"]
    planned_target = planned_by_id[CANDIDATE]
    planned_target["decision"] = "same"
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = "S3-cross-chapter-work-reuse-2026-10-16"
    planned_target["resolution_note"] = (
        f"group={TARGET_GROUP}; source_ref=entity-candidates.csv#{CANDIDATE}; "
        f"candidate_source_ref={candidate_by_id[CANDIDATE]['candidate_source_ref']}; "
        "S3 cross-chapter correction 2026-10-16: map as same to the existing plate-13 work KU. "
        "Chapter 2, p. 52, L99 explicitly calls the great Barberini ceiling “Plate 13”; "
        "the plate list identifies plate 13 as Pietro da Cortona’s Glorification of the Reign of Urban VIII at Palazzo Barberini. "
        "The exact cross-reference resolves the candidate to the existing work. Keep cand-4582, the Forge of Vulcan scene, "
        "in its separate work group. This corrects the earlier new decision and its no-existing-KU rationale. "
        f"prior_decision=new; prior_group={PREVIOUS_GROUP}; prior_resolution_note={previous_note}"
    )

    process, result, totals = update_progress(process, result, planned, len(manifest))
    marker = "### S3 跨章复用纠偏：科尔托纳巴贝里尼宫大天花画（2026-10-16）"
    assert marker not in process and marker not in result
    note = (
        f"\n\n{marker}\n\n"
        f"{CANDIDATE} 原裁为新 work 组 {PREVIOUS_GROUP}。复核第2章 p.52 L99 的正文明确称 great Barberini ceiling (Plate 13)；"
        "章前图版目录 p.xii L59–60 将 Plate 13 标为 Pietro da Cortona: Glorification of the Reign of Urban VIII，"
        "并列出 Palazzo Barberini。正文与图版目录的直接交叉指称证明二者是同一作品，故改为 same 并映射至既有 KU "
        f"{KU_ID}。cand-4080 已映射至同一 KU；候选因此复用既有作品卡，不新建重复卡。"
        "候选 cand-4582 为该天花画中的 Forge of Vulcan 场景，仍保留独立 work 身份组，不在本批合并或创建正式部分关系。"
        f"该候选的18条关系候选继续留待 S6。S3 决定数现为 same=1,718、new=5,006（4,837组）、conflict=7、"
        "excluded=98、undecided=5,575；S4 新组登记数不变。"
        f"\n\nS4 当前已登记{totals[0]:,}组/{totals[1]:,}条成员映射，尚待登记{totals[2]:,}组/{totals[3]:,}条。"
    )
    result_note = (
        f"\n\n### S3 跨章身份纠偏：Pietro da Cortona 的巴贝里尼宫大天花画（2026-10-16）\n\n"
        f"cand-4687 改为复用 cand-4080 所指的既有作品 KU。第2章称该大天花画为 Plate 13，图版目录将 Plate 13 题为 "
        "Glorification of the Reign of Urban VIII，形成直接同一性证据；cand-4582 的 Forge of Vulcan 场景保持独立身份组。"
        "该纠偏未增删 KU、manifest 或 accepted 条目，相关18条关系候选仍待 S6。"
    )
    process += note
    result += result_note

    # Refresh the current result summary without rewriting its historical S3 batch notes.
    old_counts = "same=1,717（指向1,025个既有 KU）、new=5,007（4,838个身份组）"
    new_counts = "same=1,718（指向1,025个既有 KU）、new=5,006（4,837个身份组）"
    assert old_counts in result
    result = result.replace(old_counts, new_counts, 1)
    result = result.replace("8个新家族组尚待 S4", "8个新家族身份组已完成 S4 登记", 1)
    assert "8个新家族身份组已完成 S4 登记" in result
    old_pending = "S4 已登记196组、映射247条成员候选；尚待登记4,642组、4,760条映射。"
    new_pending = (
        f"S4 已登记{totals[0]:,}组、映射{totals[1]:,}条成员候选；"
        f"尚待登记{totals[2]:,}组、{totals[3]:,}条映射。"
    )
    if old_pending in result:
        result = result.replace(old_pending, new_pending, 1)

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} new -> same; target={KU_ID}; "
              f"scene_separate={SCENE_CANDIDATE}; relations_pending={len(relation_rows)}; "
              f"S4={totals[0]}/{totals[1]} pending={totals[2]}/{totals[3]}")
        return 0

    write_csv(ALIGNMENT_PATH, align_fields, planned)
    PROCESS_PATH.write_text(process, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result, encoding="utf-8-sig", newline="")
    print(f"applied: {CANDIDATE} -> same {KU_ID}; no KU or manifest change")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
