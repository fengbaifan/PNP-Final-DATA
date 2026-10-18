from __future__ import annotations

import argparse
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
ANCHOR = "s3-angelo-querini-index-subentries-20261018"
KU_ID = "units/persons/angelo-querini"
MAIN_CANDIDATE = "cand-2075"
TARGETS = {
    "cand-2076": ("Q-R.csv#3", "and De Non", "371"),
    "cand-2077": ("Q-R.csv#4", "and Enlightenment", "369"),
    "cand-2078": ("Q-R.csv#5", "and Carlo Lodoli", "368"),
    "cand-2082": ("Q-R.csv#9", "influence of Rousseau", "372"),
    "cand-2083": ("Q-R.csv#10", "opposition of Marco Foscarini to", "258, 259"),
    "cand-2084": ("Q-R.csv#11", "romantic, 'pagan, and Manichean' soul", "370, 371"),
    "cand-2085": ("Q-R.csv#12", "taste for antique", "371, 372"),
    "cand-2086": ("Q-R.csv#13", "visit to Voltaire", "369"),
}


def decision_rows(alignment_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align Angelo Querini person-index subentries to his registered person KU."
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
    assert manifest_by_ku[KU_ID]["name_en"] == "Angelo Querini"
    main_candidate = candidate_by_id[MAIN_CANDIDATE]
    main_alignment = by_id[MAIN_CANDIDATE]
    assert main_candidate["index_entry_id"] == "Q-R.csv#2"
    assert main_candidate["canonical_name"] == "Querini, Angelo"
    assert main_alignment["decision"] == "new" and main_alignment["ku_id"] == KU_ID

    card = (ROOT / manifest_by_ku[KU_ID]["card_path"]).read_text(encoding="utf-8-sig")
    assert "Angelo Querini" in card
    assert "print p. 320" in card and "print p. 368" in card

    for cid, (index_entry, sub_entry, page) in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["index_entry_id"] == index_entry
        assert candidate["canonical_name"] == "Querini, Angelo"
        assert candidate["sub_entry"] == sub_entry
        assert candidate["index_page_range"] == page
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "index-seeded candidate has no mapped S2 mention" in alignment["resolution_note"]

    # These neighbouring index rows denote different types or distinct people and remain untouched.
    assert candidate_by_id["cand-2074"]["canonical_name"] == "Querini, Andrea"
    assert candidate_by_id["cand-2079"]["suggested_type"] == "event"
    assert candidate_by_id["cand-2080"]["suggested_type"] == "place"
    assert candidate_by_id["cand-2081"]["suggested_type"] == "place"
    assert candidate_by_id["cand-2087"]["canonical_name"] == "Querini, Giacomo"

    planned = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned)
    for cid, (index_entry, sub_entry, page) in TARGETS.items():
        row = planned_by_id[cid]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = f"{TASK}#{ANCHOR}"
        row["resolution_note"] += (
            f" S3复核（{DATE}）：原undecided理由保留为历史；{index_entry}的“Querini, Angelo”"
            f"为主项cand-2075下的人物索引子目“{sub_entry}”，定位印刷页{page}。书末索引主项跨列pp.258–373；"
            "第10章p.320和第15章p.368均以全名Angelo Querini称同一人物，现有person KU已收录这两处跨章来源。"
            f"该子项候选改判same → {KU_ID}；子目只保留为身份组下的主题/关系定位，不与De Non、Carlo Lodoli、"
            "Marco Foscarini或Voltaire合并。相邻的Andrea Querini、Giacomo Querini仍独立；arrest and detention事件、"
            "Alticchiero country house与garden地点候选继续各按其类型处理。身份对齐不采纳子目谓词，也不新增正式关系。"
        )

    before = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(item[key] for item in before.values()) for key in next(iter(before.values()))}
    same_target_already_counted = any(
        row["decision"] == "same" and row.get("ku_id") == KU_ID for row in by_id.values()
    )
    expected_same_kus = before["person"]["same_kus"] + (0 if same_target_already_counted else 1)
    assert totals["same_candidates"] == before_totals["same_candidates"] + len(TARGETS)
    assert totals["undecided"] == before_totals["undecided"] - len(TARGETS)
    assert totals["new_candidates"] == before_totals["new_candidates"]
    assert totals["new_groups"] == before_totals["new_groups"]
    assert totals["registered_groups"] == before_totals["registered_groups"]
    assert totals["pending_groups"] == before_totals["pending_groups"]
    assert totals["pending_members"] == before_totals["pending_members"]
    assert stats["person"]["same_candidates"] == before["person"]["same_candidates"] + len(TARGETS)
    assert stats["person"]["undecided"] == before["person"]["undecided"] - len(TARGETS)
    assert stats["person"]["same_kus"] == expected_same_kus

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Angelo Querini索引子项复用既有人物KU（{DATE}）\n\n"
        "- cand-2076（Q-R.csv#3，and De Non）、cand-2077（#4，and Enlightenment）、cand-2078（#5，and Carlo Lodoli）、"
        "cand-2082（#9，influence of Rousseau）、cand-2083（#10，opposition of Marco Foscarini to）、"
        "cand-2084（#11，romantic, 'pagan, and Manichean' soul）、cand-2085（#12，taste for antique）与"
        f"cand-2086（#13，visit to Voltaire）均由undecided改判same → [{KU_ID}](../../../04-knowledge/{KU_ID}.md)。"
        "八项均隶属同一人物主项“Querini, Angelo”，页码258–373；既有cand-2075以第10章p.320和第15章p.368全名锚点"
        "登记该人物，支持跨章复用。\n"
        "- 子目标题保留为索引定位，不采纳为独立事实或正式关系；De Non、Lodoli、Foscarini、Voltaire仍为不同人物端点。"
        "cand-2074（Andrea Querini）与cand-2087（Giacomo Querini）不并入；事件cand-2079及地点cand-2080、cand-2081保持各自类型和决定。"
        "未新增正式关系。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，"
        f"undecided={sync.fmt(totals['undecided'])}；S4待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text += (
        f"\n\n### S3 person：Angelo Querini索引子项复用（{DATE}）\n\n"
        "八个同一人物主项下的索引候选改为same并指向既有Angelo Querini人物KU；相邻人物、事件、地点及子目关系范围保持分开。"
        f"详见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})及alignment.csv。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: same additions={len(TARGETS)}->{KU_ID}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; "
            f"undecided={totals['undecided']}; new_groups={totals['new_groups']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"distinct_event_place_rows=3; manifest={len(manifest)}"
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
