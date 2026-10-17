from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import register_s4_valmarana_cluster_batch_20261015 as card_writer


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"

CANDIDATE = "cand-0694"
GROUP = "sg3-place-cand-0694"
KU_ID = "units/places/s-andrea-al-quirinale"
CARD_REL = "04-knowledge/units/places/s-andrea-al-quirinale.md"
INTERIOR_KU = "units/places/interior-sant-andrea-quirinale"
EVENT_KU = "units/events/s-andrea-al-quirinale-rebuilding-project"
MARKER = "### S3 跨章身份复用纠偏：Churches 索引下的 S. Andrea al Quirinale（2026-10-16）"


def read_csv(path):
    return card_writer.read_csv(path)


def write_csv(path, fields, rows):
    card_writer.write_csv(path, fields, rows)


def totals(rows):
    candidates = [r for r in rows if r.get("candidate_id") and not r.get("external_source")]
    d = Counter(r["decision"] for r in candidates)
    same_kus = {r["ku_id"] for r in candidates if r["decision"] == "same" and r.get("ku_id")}
    groups = defaultdict(list)
    for row in candidates:
        if row["decision"] == "new":
            group = card_writer.get_group(row.get("resolution_note", ""))
            assert group, f"new decision lacks group: {row['candidate_id']}"
            groups[group].append(row)
    registered = {g: members for g, members in groups.items() if any(r.get("ku_id") for r in members)}
    mapped = sum(bool(r.get("ku_id")) for members in registered.values() for r in members)
    pending = [r for r in candidates if r["decision"] == "new" and not r.get("ku_id")]
    return {
        "same": d["same"], "same_kus": len(same_kus), "new": d["new"], "new_groups": len(groups),
        "conflict": d["conflict"], "excluded": d["excluded"], "undecided": d["undecided"],
        "registered_groups": len(registered), "mapped": mapped,
        "pending_groups": len(groups) - len(registered), "pending_members": len(pending),
    }


def update_result(result, current):
    s3_pattern = re.compile(r"same=[\d,]+（指向[\d,]+个既有 KU）、new=[\d,]+（[\d,]+个身份组）")
    result, n = s3_pattern.subn(
        f"same={current['same']:,}（指向{current['same_kus']:,}个既有 KU）、new={current['new']:,}（{current['new_groups']:,}个身份组）",
        result,
        count=1,
    )
    assert n == 1, "could not update current S3 summary"
    s4_pattern = re.compile(r"S4 已登记\s*[\d,]+组、映射[\d,]+条成员候选；尚待登记[\d,]+组、[\d,]+条映射。")
    result, n = s4_pattern.subn(
        f"S4 已登记{current['registered_groups']:,}组、映射{current['mapped']:,}条成员候选；"
        f"尚待登记{current['pending_groups']:,}组、{current['pending_members']:,}条映射。",
        result,
        count=1,
    )
    assert n == 1, "could not update current S4 summary"
    return result


def main():
    parser = argparse.ArgumentParser(description="Reuse the existing S. Andrea al Quirinale place KU for cand-0694.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    _, manifest = read_csv(MANIFEST_PATH)
    _, candidates = read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {r["candidate_id"]: r for r in candidates}
    alignment_by_id = {r["candidate_id"]: r for r in alignments if r.get("candidate_id") and not r.get("external_source")}
    place_manifest = next((r for r in manifest if r.get("ku_id") == KU_ID), None)
    interior_manifest = next((r for r in manifest if r.get("ku_id") == INTERIOR_KU), None)
    event_manifest = next((r for r in manifest if r.get("ku_id") == EVENT_KU), None)
    card_path = ROOT / CARD_REL
    accepted = (ROOT / "04-knowledge" / "accepted.yml").read_text(encoding="utf-8-sig")
    process = PROCESS_PATH.read_text(encoding="utf-8-sig")
    result = RESULT_PATH.read_text(encoding="utf-8-sig")

    assert CANDIDATE in candidate_by_id and candidate_by_id[CANDIDATE]["suggested_type"] == "place"
    assert candidate_by_id[CANDIDATE]["index_entry_id"] == "C.csv#218"
    assert candidate_by_id[CANDIDATE]["sub_entry"] == "S. Andrea al Quirinale"
    row = alignment_by_id[CANDIDATE]
    assert row["decision"] == "new" and not row.get("ku_id")
    assert card_writer.get_group(row["resolution_note"]) == GROUP
    group_rows = [
        r for r in alignments if r.get("candidate_id") and not r.get("external_source")
        and r["decision"] == "new" and card_writer.get_group(r.get("resolution_note", "")) == GROUP
    ]
    assert [r["candidate_id"] for r in group_rows] == [CANDIDATE]
    assert place_manifest and place_manifest["type"] == "place" and place_manifest["card_path"] == CARD_REL
    assert interior_manifest and interior_manifest["type"] == "place" and event_manifest and event_manifest["type"] == "event"
    assert card_path.exists() and CARD_REL in accepted

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    direct = [r for r in statements if r.get("subject_candidate_id") == CANDIDATE or r.get("object_candidate_id") == CANDIDATE]
    relation_rows = [r for r in direct if (r.get("qualifiers") or {}).get("relation_candidate") is True]
    assert len(direct) == 20, f"unexpected direct statement count: {len(direct)}"
    assert len(relation_rows) == 13, f"unexpected relation candidate count: {len(relation_rows)}"

    checks = (
        ("03_CHP-3_sec_ii.md", "The decoration both of another little church, S. Andrea al Quirinale"),
        ("03_CHP-3_sec_ii.md", "these churches were intended for Jesuit novices and not for the general public"),
        ("03_CHP-3_sec_iv.md", "In the novitiate church of S. Andrea which he began to build in 1658"),
    )
    for file_name, quote in checks:
        source = ROOT / "02-sources" / "02-Markdown" / file_name
        source_text = " ".join(source.read_text(encoding="utf-8-sig").split())
        assert " ".join(quote.split()) in source_text, (file_name, quote)

    planned = [dict(r) for r in alignments]
    target = next(r for r in planned if r.get("candidate_id") == CANDIDATE and not r.get("external_source"))
    previous_note = target["resolution_note"]
    target["decision"] = "same"
    target["ku_id"] = KU_ID
    target["process_ref"] = "S3-cross-chapter-place-reuse-2026-10-16"
    target["resolution_note"] = (
        f"source_ref=C.csv#218 (sub-entry: S. Andrea al Quirinale); existing_ku={CARD_REL}; "
        f"S3 place correction 2026-10-16: same -> {KU_ID}. Chapters 3, pp. 67–68 and 85–88, discuss this named church, "
        "and the index entry’s sub-entry names the same S. Andrea al Quirinale. The accepted place KU already identifies "
        "the church building; its interior remains separate at "
        f"{INTERIOR_KU}, and the rebuilding project remains a separate event at {EVENT_KU}. "
        f"prior_decision=new; prior_group={GROUP}; prior_resolution_note={previous_note}"
    )
    current = totals(planned)
    updated_result = update_result(result, current)
    assert MARKER not in process and MARKER not in updated_result
    process_note = (
        f"\n\n{MARKER}\n\n"
        f"`{CANDIDATE}`（C.csv#218，sub-entry `S. Andrea al Quirinale`）原裁为新 place 组 `{GROUP}`；"
        f"现改为 same 并映射至既有[奎里纳尔圣安德烈堂地点卡](../../../04-knowledge/units/places/s-andrea-al-quirinale.md)。"
        "第3章 pp.67–68、85–88 将该名称用于同一教堂；教堂建筑、内部空间 KU "
        f"`{INTERIOR_KU}` 和重建工程 event KU `{EVENT_KU}` 各自保持独立。"
        f"20条直接 S2 陈述中13条为关系候选，仍留待 S6。S3 现为 same={current['same']:,}（{current['same_kus']:,}个既有 KU）、"
        f"new={current['new']:,}（{current['new_groups']:,}组）、conflict={current['conflict']}、excluded={current['excluded']}、"
        f"undecided={current['undecided']:,}；S4 已登记{current['registered_groups']:,}组/{current['mapped']:,}条映射，"
        f"待登记{current['pending_groups']:,}组/{current['pending_members']:,}条。原决定和理由保留在 alignment。"
    )
    result_note = (
        "\n\n### place：S. Andrea al Quirinale 跨章复用既有教堂地点（2026-10-16）\n\n"
        f"`{CANDIDATE}` 改为 same 并映射至[既有教堂地点卡](../units/places/s-andrea-al-quirinale.md)。"
        f"内部空间 KU `{INTERIOR_KU}` 与重建工程 event KU `{EVENT_KU}` 不并入；13条关系候选仍待 S6。"
        f"当前 S3 same={current['same']:,}（{current['same_kus']:,}个既有 KU）、new={current['new']:,}（{current['new_groups']:,}组）；"
        f"S4 已登记{current['registered_groups']:,}组/{current['mapped']:,}条映射，待登记{current['pending_groups']:,}组/{current['pending_members']:,}条。"
    )
    process += process_note
    updated_result += result_note

    if args.dry_run:
        print(f"S3 place reuse dry-run passed: {CANDIDATE} -> {KU_ID}")
        print(f"direct statements={len(direct)}; relation candidates={len(relation_rows)}; interior and rebuilding event remain separate")
        print(
            f"S3 same={current['same']:,}/{current['same_kus']:,} KUs; new={current['new']:,}/{current['new_groups']:,} groups; "
            f"S4 pending={current['pending_groups']:,} groups/{current['pending_members']:,} candidates"
        )
        print("C-index heading, named church passages, and existing place/interior/event cards checked; no files changed")
        return 0

    write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(updated_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {CANDIDATE} -> {KU_ID}; same={current['same']:,}/{current['same_kus']:,}; "
        f"new={current['new']:,}/{current['new_groups']:,}; "
        f"S4 pending={current['pending_groups']:,}/{current['pending_members']:,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
