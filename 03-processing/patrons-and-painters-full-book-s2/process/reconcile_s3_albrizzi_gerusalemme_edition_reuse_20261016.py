from __future__ import annotations

import argparse
import csv
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
CARD_PATH = ROOT / "04-knowledge" / "units" / "archives" / "gerusalemme-liberata-illustrations-1745.md"
CANDIDATE = "cand-9990"
PLATE_CANDIDATE = "cand-3600"
KU_ID = "units/archives/gerusalemme-liberata-illustrations-1745"
TARGET_GROUP = "sg3-ku-units-archives-gerusalemme-liberata-illustrations-1745"
PREVIOUS_GROUP = "archive-group-0a3583f7dde3"
BODY_QUOTE = "Venetian eighteenth-century books—the Gerusalemme Liberata which he brought out in 1745 (Plate 57a)."
PLATE_QUOTE = "57 a Piazzetta: Final plate of Illustrations to Gerusalemme Liber ata, published by Albrizzi 1745"

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
    parser = argparse.ArgumentParser(description="Correct the S3 identity of Albrizzi's 1745 illustrated Gerusalemme Liberata")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    align_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, manifest = read_csv(MANIFEST_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    target, plate = by_id[CANDIDATE], by_id[PLATE_CANDIDATE]
    manifest_row = next(r for r in manifest if r["ku_id"] == KU_ID)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    process = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result = RESULT_PATH.read_text(encoding="utf-8-sig")
    assert target["decision"] == "new" and not target.get("ku_id")
    assert group(target["resolution_note"]) == PREVIOUS_GROUP
    assert candidate_by_id[CANDIDATE]["suggested_type"] == "archive"
    assert plate["decision"] == "same" and plate.get("ku_id") == KU_ID
    assert manifest_row["type"] == "archive" and CARD_PATH.exists()
    assert CARD_PATH.relative_to(ROOT).as_posix() in accepted

    old_group_rows = [
        r for r in alignments if r.get("candidate_id") and not r.get("external_source")
        and r["decision"] == "new" and group(r.get("resolution_note", "")) == PREVIOUS_GROUP
    ]
    assert [r["candidate_id"] for r in old_group_rows] == [CANDIDATE]
    body_source = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
    plate_source = ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md"
    assert BODY_QUOTE in body_source.read_text(encoding="utf-8-sig")
    assert PLATE_QUOTE in plate_source.read_text(encoding="utf-8-sig")

    planned = [dict(r) for r in alignments]
    planned_by_id = {r["candidate_id"]: r for r in planned if r.get("candidate_id") and not r.get("external_source")}
    previous_note = target["resolution_note"]
    row = planned_by_id[CANDIDATE]
    row["decision"] = "same"
    row["ku_id"] = KU_ID
    row["process_ref"] = "S3-cross-chapter-archive-reuse-2026-10-16"
    row["resolution_note"] = (
        f"group={TARGET_GROUP}; source_ref=entity-candidates.csv#{CANDIDATE}; "
        f"candidate_source_ref={candidate_by_id[CANDIDATE]['candidate_source_ref']}; "
        "S3 cross-chapter correction 2026-10-16: map as same to the existing archive KU for the 1745 illustrated edition. "
        "Chapter 13, p. 335, L36 identifies the Gerusalemme Liberata brought out by Albrizzi in 1745 and points to Plate 57a; "
        "the plate list, p. xv, L135 identifies Plate 57a as Piazzetta's final plate of illustrations to Gerusalemme Liberata, "
        "published by Albrizzi in 1745. This direct cross-reference resolves the candidate to the existing edition card. "
        "Candidate cand-3600 already maps the plate-list record to the same KU. This corrects the earlier new decision. "
        f"prior_decision=new; prior_group={PREVIOUS_GROUP}; prior_resolution_note={previous_note}"
    )

    process, result, totals = update_progress(process, result, planned, len(manifest))
    marker = "### S3 跨章复用纠偏：Albrizzi 1745 年《耶路撒冷解放》插图本（2026-10-16）"
    assert marker not in process and marker not in result
    note = (
        f"\n\n{marker}\n\n"
        f"{CANDIDATE} 原裁为新 archive 组 {PREVIOUS_GROUP}。第13章 p.335 L36 明称 Albrizzi 于1745年推出 Gerusalemme Liberata 并回指 Plate 57a；"
        "章前图版目录 p.xv L135 将 Plate 57a 说明为 Piazzetta 为该书绘制的插图末页，并记出版者 Albrizzi 与年份1745。"
        "正文与图版目录指向同一版次，故 cand-9990 改为 same，复用既有 archive KU "
        f"{KU_ID}；cand-3600 已映射至该 KU。原书并非新增知识元，本批未改卡、manifest 或 accepted。"
        "该候选涉及的参与者、赞助、出版和版本关系仍留待 S6 依具体证据审查。"
        f"\n\nS4 当前已登记{totals[0]:,}组/{totals[1]:,}条成员映射，尚待登记{totals[2]:,}组/{totals[3]:,}条。"
    )
    result_note = (
        f"\n\n### S3 跨章身份纠偏：Albrizzi 1745 年《耶路撒冷解放》插图本（2026-10-16）\n\n"
        "cand-9990 改为复用 cand-3600 所指的既有 archive KU。第13章正文将1745年版次回指 Plate 57a；图版目录将其标为 "
        "Piazzetta 为 Albrizzi 1745 年版绘制的插图末页，形成直接同一性依据。本次未新增 KU 或变更 manifest。"
    )
    process += note
    result += result_note

    old_counts = "same=1,718（指向1,025个既有 KU）、new=5,006（4,837个身份组）"
    new_counts = "same=1,719（指向1,025个既有 KU）、new=5,005（4,836个身份组）"
    assert old_counts in result
    result = result.replace(old_counts, new_counts, 1)

    if args.dry_run:
        print(f"dry-run passed: {CANDIDATE} new -> same; target={KU_ID}; "
              f"S4={totals[0]}/{totals[1]} pending={totals[2]}/{totals[3]}")
        return 0
    write_csv(ALIGNMENT_PATH, align_fields, planned)
    PROCESS_PATH.write_text(process, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result, encoding="utf-8-sig", newline="")
    print(f"applied: {CANDIDATE} -> same {KU_ID}; no KU or manifest change")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
