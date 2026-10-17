from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
from io import StringIO
from pathlib import Path

PROCESS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-16"

PERSON_GROUP = "new-person:baglione-giovanni-f65db6f695"
WORK_GROUP = "workgrp-3089e5ca7ba112"
PERSON_MEMBERS = ("cand-0156", "cand-0157", "cand-0158")
WORK_MEMBERS = ("cand-5013", "cand-5297")
OLD_WORK_GROUPS = {
    "cand-5013": "workgrp-3089e5ca7ba112",
    "cand-5297": "workgrp-098003cb22b988",
}


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def csv_text(fieldnames, rows) -> str:
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def get_group(note: str) -> str | None:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else None


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, f"{label}: expected one occurrence, found {count}"
    return text.replace(old, new, 1)


def planned_rows(rows):
    by_id = {
        row["candidate_id"]: row
        for row in rows
        if row.get("candidate_id") and not row.get("external_source")
    }

    person = by_id["cand-0157"]
    assert person["decision"] == "undecided" and not person.get("ku_id")
    assert "s2_mentions=none" in person["resolution_note"]
    assert get_group(by_id["cand-0156"]["resolution_note"]) == PERSON_GROUP
    assert get_group(by_id["cand-0158"]["resolution_note"]) == PERSON_GROUP

    for cid, old_group in OLD_WORK_GROUPS.items():
        row = by_id[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        assert get_group(row["resolution_note"]) == old_group

    revised = [dict(row) for row in rows]
    revised_by_id = {
        row["candidate_id"]: row
        for row in revised
        if row.get("candidate_id") and not row.get("external_source")
    }

    person_note = revised_by_id["cand-0157"]["resolution_note"]
    revised_by_id["cand-0157"]["decision"] = "new"
    revised_by_id["cand-0157"]["process_ref"] = "S3-full-book-2026-10-16"
    revised_by_id["cand-0157"]["resolution_note"] = (
        f"source_ref=candidate=cand-0157;index_entry=B.csv#4;index_pages=127;"
        f"group={PERSON_GROUP}; S3复核（{DATE}）：同头项与正文锚点支持映射至Giovanni Baglione人物组。"
        "B.csv#4的主项仍为Baglione, Giovanni，Divine Love是作品子项；同页正文以[Giovanni Baglione]为全名，"
        "明确称其绘制Divine Love。该子项是人物索引定位，不是另一个人物或别名。"
        f" prior_decision=undecided; prior_resolution_note={person_note}"
    )

    for cid in WORK_MEMBERS:
        row = revised_by_id[cid]
        old_group = OLD_WORK_GROUPS[cid]
        row["process_ref"] = "S3-full-book-2026-10-16"
        row["resolution_note"] += (
            f" S3组复核（{DATE}）：将该候选与{','.join(WORK_MEMBERS)}归入同一"
            f"{WORK_GROUP}。p.66称Baglione绘制The Resurrection画作；p.84称同一画家"
            "于1602年为耶稣堂右横翼、曾奉献于Resurrection的礼拜堂绘制祭坛画。"
            "共同画家、复活题材、耶稣会教堂语境及年代相容支持同一作品判断；p.84未重述题名，"
            "p.66未明说地点，故不推定具体陈列位置或投诉年份。"
            f" prior_group={old_group}; decision remains new."
        )
        row["resolution_note"] = row["resolution_note"].replace(
            f"group={old_group}", f"group={WORK_GROUP}", 1
        )

    return revised


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refine the Baglione person and Resurrection work identity groups in S3."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignment = read_csv(ALIGNMENT)
    candidate_fields, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert candidate_by_id["cand-0157"]["suggested_type"] == "person"
    assert candidate_by_id["cand-0157"]["index_entry_id"] == "B.csv#4"
    assert candidate_by_id["cand-0157"]["sub_entry"] == "Divine Love"
    assert candidate_by_id["cand-5013"]["suggested_type"] == "work"
    assert candidate_by_id["cand-5297"]["suggested_type"] == "work"

    _, manifest = read_csv(TABLES / "ku-manifest.csv")
    assert not any(
        row.get("ku_id") in {
            "units/persons/giovanni-baglione",
            "units/works/giovanni-baglione-resurrection-gesu-altarpiece",
        }
        for row in manifest
    )

    index_text = (ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv").read_text(
        encoding="utf-8-sig"
    )
    ch3_66 = (ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md").read_text(
        encoding="utf-8-sig"
    )
    ch3_84 = (ROOT / "02-sources/02-Markdown/03_CHP-3_sec_iv.md").read_text(
        encoding="utf-8-sig"
    )
    ch5_127 = (ROOT / "02-sources/02-Markdown/05_CHP-5_sec_i.md").read_text(
        encoding="utf-8-sig"
    )
    assert "Baglione, Giovanni" in index_text and "Divine Love" in index_text
    assert "The Resurrection Giovanni" in ch3_66 and "Baglione was forced to complain" in ch3_66
    assert "Baglione had painted an altarpiece in 1602" in ch3_84
    assert "he [Giovanni Baglione] competed with me" in ch5_127
    assert "picture which was called Divine Love" in ch5_127

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    relevant = [
        row for row in statements
        if row.get("subject_candidate_id") in {"cand-0156", "cand-0158", "cand-5013", "cand-5297"}
        or row.get("object_candidate_id") in {"cand-0156", "cand-0158", "cand-5013", "cand-5297"}
    ]
    assert any(row["statement_id"] == "st-chp3-seciv-l75-81-baglione-altarpiece" for row in relevant)

    revised = planned_rows(alignment)
    stats = sync.summarize_by_type(candidates, revised)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    section = (
        f"\n\n### S3复核：Baglione人物子项与《The Resurrection》作品组（{DATE}）\n\n"
        "- cand-0157（B.csv#4，Divine Love，p.127）原为undecided，理由是无S2正文提及。复核索引主项与原文后改为"
        f"new并并入{PERSON_GROUP}：同一主项Baglione, Giovanni在p.127以Divine Love作作品子项；正文同页"
        "以[Giovanni Baglione]为全名并明确称其绘制该画。该索引子项不是第二个人，也不作为人物别名。"
        "原未决理由保留在alignment resolution_note的prior记录中。\n"
        "- cand-5013（p.66的The Resurrection画作）和cand-5297（p.84的1602年耶稣堂右横翼礼拜堂祭坛画）"
        f"从两个new组并为同一new作品组{WORK_GROUP}。相同画家、复活题材、耶稣会教堂语境与相容年代支持此判断；"
        "p.84未重复题名且p.66未明说地点，因此不推定祭坛画的题名出处、展示状态或投诉年份。两条旧组号与前次理由仍保留在alignment行。\n"
        "- 其余Cand-0156及Cand-0158保持原new决定；同组三条person候选将在S4映射到一个KU。"
        "本次没有新增relations.csv正式关系；p.66、p.84、p.127所涉关系仍待S6审查。"
    )
    assert "### S3复核：Baglione人物子项与《The Resurrection》作品组" not in process_text
    planned_process = process_text + section
    result_insert = (
        f"### S3复核：Baglione人物子项与《The Resurrection》作品组（{DATE}）\n\n"
        "cand-0157（B.csv#4，Divine Love）由undecided改为new并入Giovanni Baglione人物组："
        "同页正文全名及作品子项语境提供直接身份锚点。cand-5013（p.66 The Resurrection）与"
        "cand-5297（p.84 1602年耶稣堂祭坛画）归为一个new作品组，依据为同一画家、复活题材、"
        "耶稣会教堂语境及相容年代；题名和具体陈列状态不作超出原文的推断。"
        "两项工作组判断及旧理由均保留于对齐表和过程记录。\n\n"
    )
    anchor = "候选决定按每个候选一条"
    assert result_text.count(anchor) == 1
    planned_result = result_text.replace(anchor, result_insert + anchor, 1)
    planned_result = sync.update_result(
        planned_result, stats, totals, len(manifest)
    )

    print("S3 changes:")
    print("  cand-0157: undecided -> new; group=person Baglione")
    print("  cand-5013 + cand-5297: two new work groups -> one new work group")
    print(f"  totals: new={totals['new_candidates']}/{totals['new_groups']} groups; undecided={totals['undecided']}")
    print("  no KU or formal relation written")
    if args.dry_run:
        print("dry-run passed; no files changed")
        return 0

    backup_suffix = ".bak-s3-baglione-groups-20261016"
    for path in (ALIGNMENT, PROCESS, RESULT):
        backup = path.with_name(path.name + backup_suffix)
        if backup.exists():
            raise FileExistsError(f"refusing to overwrite backup: {backup}")
        shutil.copy2(path, backup)
    ALIGNMENT.write_text(csv_text(alignment_fields, revised), encoding="utf-8-sig", newline="")
    PROCESS.write_text(planned_process, encoding="utf-8-sig", newline="")
    RESULT.write_text(planned_result, encoding="utf-8-sig", newline="")
    print("applied alignment, process record, and current S3/S4 result summary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
