from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-18"
ANCHOR = "s3-rosalba-carriera-index-subentries-20261018"
KU_ID = "units/persons/rosalba-carriera"
MAIN_CANDIDATE = "cand-0581"
GROUP = "new-person:carriera-rosalba-f0a77ca508"
TARGETS = {
    "cand-0582": ("C.csv#106", "and Augustus III of Poland", "295"),
    "cand-0583": ("C.csv#107", "influence on French painting", "285"),
    "cand-0584": ("C.csv#108", "journal, edited by Vianello", "376"),
    "cand-0587": ("C.csv#111", "Winter", "303"),
    "cand-0589": ("C.csv#113", "work in Paris", "284, 285"),
}
ARCHIVE_KU = "units/archives/carriera-journal-vianello-1793"
WINTER_STATEMENT = "st-chp10-p303-winter-description"


def decision_rows(alignment_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align Rosalba Carriera's person index subentries to her registered person KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    by_id = decision_rows(alignments)
    assert len(by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    manifest_by_ku = {row["ku_id"]: row for row in manifest}

    assert KU_ID in manifest_by_ku and manifest_by_ku[KU_ID]["type"] == "person"
    assert manifest_by_ku[KU_ID]["name_en"] == "Rosalba Carriera"
    assert ARCHIVE_KU in manifest_by_ku and manifest_by_ku[ARCHIVE_KU]["type"] == "archive"
    main_candidate = candidate_by_id[MAIN_CANDIDATE]
    main_alignment = by_id[MAIN_CANDIDATE]
    assert main_candidate["index_entry_id"] == "C.csv#105"
    assert main_candidate["canonical_name"] == "Carriera, Rosalba"
    assert main_alignment["decision"] == "new" and main_alignment["ku_id"] == KU_ID
    assert sync.get_group(main_alignment["resolution_note"]) == GROUP

    existing_member_ids = {MAIN_CANDIDATE, "cand-0585", "cand-0586", "cand-0588"}
    existing_members = {
        cid for cid, row in by_id.items()
        if row["decision"] == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert existing_members == existing_member_ids
    assert all(by_id[cid]["ku_id"] == KU_ID for cid in existing_member_ids)

    for cid, (index_entry, sub_entry, page) in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["index_entry_id"] == index_entry
        assert candidate["canonical_name"] == "Carriera, Rosalba"
        assert candidate["sub_entry"] == sub_entry
        assert candidate["index_page_range"] == page
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "index-seeded candidate has no mapped S2 mention" in alignment["resolution_note"]

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    winter = next(row for row in statements if row["statement_id"] == WINTER_STATEMENT)
    assert winter["subject_candidate_id"] == "cand-0588"
    assert winter["object_candidate_id"] == "cand-9203"
    assert winter["qualifiers"]["relation_candidate"] is True

    planned = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned)
    for cid, (index_entry, sub_entry, page) in TARGETS.items():
        row = planned_by_id[cid]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = f"{TASK}#{ANCHOR}"
        row["resolution_note"] += (
            f" S3复核（{DATE}）：原undecided理由保留为历史；{index_entry}的“Carriera, Rosalba”"
            f"是该人物主项下的索引子目“{sub_entry}”，定位印刷页{page}。主项cand-0581由第10章p.276全名"
            "Rosalba Carriera及跨章正文形式确认，并已登记到既有person KU；主项下C.csv#109、#110、#112的"
            "人物候选亦已映射到同一KU。因此本候选改判same → units/persons/rosalba-carriera。子目只作为人物索引定位，"
            "不把Augustus III映射为Carriera、不将第1793年日记刊本并入人物，也不把Winter索引子目替代为作品；"
            "相关archive/work候选及S2关系候选保留各自去向。"
        )

    before = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(item[key] for item in before.values()) for key in next(iter(before.values()))}
    assert totals["same_candidates"] == before_totals["same_candidates"] + len(TARGETS)
    assert totals["undecided"] == before_totals["undecided"] - len(TARGETS)
    assert totals["new_candidates"] == before_totals["new_candidates"]
    assert totals["new_groups"] == before_totals["new_groups"]
    assert totals["registered_groups"] == before_totals["registered_groups"]
    assert totals["pending_groups"] == before_totals["pending_groups"]
    assert totals["pending_members"] == before_totals["pending_members"]
    assert stats["person"]["same_candidates"] == before["person"]["same_candidates"] + len(TARGETS)
    assert stats["person"]["undecided"] == before["person"]["undecided"] - len(TARGETS)
    assert stats["person"]["same_kus"] == before["person"]["same_kus"] + 1

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Rosalba Carriera索引子项复用既有人物KU（{DATE}）\n\n"
        "- cand-0582（C.csv#106，and Augustus III of Poland）、cand-0583（#107，influence on French painting）、"
        "cand-0584（#108，journal, edited by Vianello）、cand-0587（#111，Winter）及cand-0589（#113，work in Paris）"
        f"均由undecided改判same → [{KU_ID}](../../../04-knowledge/{KU_ID}.md)。五项均为人物主项“Carriera, Rosalba”"
        "下的书后索引子目，页码分别为295、285、376、303、284–285；不是五个独立人物。主项cand-0581由第10章p.276"
        "的全名锚定，且主项下cand-0585、cand-0586、cand-0588已进入同一Carriera人物KU，提供跨章上下文连续性。\n"
        f"- 关系边界：Augustus III（cand-0148）保持独立人物；1793年journal候选仍是独立archive KU [{ARCHIVE_KU}]"
        f"(../../../04-knowledge/{ARCHIVE_KU}.md)；`Winter`作品端点cand-9203及其S2 statement {WINTER_STATEMENT}不由索引子项替代。"
        "不新增正式关系；相关S2关系候选保持原状态。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，"
        f"undecided={sync.fmt(totals['undecided'])}；S4待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text += (
        f"\n\n### S3 person：Rosalba Carriera索引子项复用（{DATE}）\n\n"
        "五个只含同一人物主项及其子目的索引候选改为same并指向既有Rosalba Carriera人物KU；"
        "1793年日记刊本与Winter作品候选保持独立。详情见"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})及alignment.csv。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: same additions={len(TARGETS)}->{KU_ID}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; "
            f"undecided={totals['undecided']}; new_groups={totals['new_groups']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"archive_kept_separate={ARCHIVE_KU}; winter_work=cand-9203; manifest={len(manifest)}"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    print(
        f"applied: same additions={len(TARGETS)}->{KU_ID}; same={totals['same_candidates']}/{totals['same_kus']}; "
        f"undecided={totals['undecided']}; manifest={len(manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
