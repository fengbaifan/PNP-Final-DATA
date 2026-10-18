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
ANCHOR = "s3-ferdinand-tuscany-index-subentries-20261018"
KU_ID = "units/persons/ferdinand-grand-prince-tuscany"
MAIN_CANDIDATE = "cand-1609"
EXISTING_MEMBERS = {"cand-1609", "cand-1611", "cand-1617"}
TARGETS = {
    "cand-1612": (
        "M.csv#152", "and G. M. Crespi", "support in break with conventional 'history picture'", "239"
    ),
    "cand-1613": ("M.csv#153", "and Fumiani", "", "234"),
    "cand-1614": ("M.csv#154", "and Gabbiani", "", "233"),
    "cand-1615": ("M.csv#155", "and Karl Loth", "", "233"),
    "cand-1616": ("M.csv#156", "and Livio Mehus", "", "240"),
    "cand-1619": ("M.csv#159", "and Venice", "", "230, 231, 232, 233"),
    "cand-1621": ("M.csv#161", "employment of Niccol\u00f2 Cassana", "", "232, 234"),
    "cand-1622": (
        "M.csv#162", "patronage of contemporary artists", "", "232, 233, 234, 235, 236, 237, 238, 239"
    ),
    "cand-1623": ("M.csv#163", "collaboration with painters", "", "232, 234, 236"),
    "cand-1624": ("M.csv#164", "support of writers", "", "230"),
}
UNCHANGED_NEIGHBORS = {
    "cand-1610": ("new", "units/procedures/ferdinand-art-exhibition-guidance", "procedure"),
    "cand-1618": ("undecided", "", "term"),
    "cand-1620": ("undecided", "", ""),
}


def decision_rows(alignment_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align Ferdinand of Tuscany's person index subentries to the registered person KU."
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
    assert manifest_by_ku[KU_ID]["name_en"] == "Grand Prince Ferdinand of Tuscany"
    main_candidate = candidate_by_id[MAIN_CANDIDATE]
    main_alignment = by_id[MAIN_CANDIDATE]
    assert main_candidate["index_entry_id"] == "M.csv#149"
    assert main_candidate["canonical_name"] == "Medici, Grand Prince Ferdinand de'"
    assert main_alignment["decision"] == "same" and main_alignment["ku_id"] == KU_ID

    existing_members = {
        cid for cid, row in by_id.items()
        if row["decision"] == "same" and row["ku_id"] == KU_ID
        and candidate_by_id[cid]["canonical_name"] == main_candidate["canonical_name"]
    }
    assert existing_members == EXISTING_MEMBERS

    same_headword_person_ids = {
        row["candidate_id"] for row in candidates
        if row["canonical_name"] == main_candidate["canonical_name"]
        and row["suggested_type"] == "person"
        and row["index_source_file"] == "M.csv"
    }
    assert same_headword_person_ids == EXISTING_MEMBERS | set(TARGETS)
    for cid, (index_entry, sub_entry, detail, page) in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["index_source_file"] == "M.csv"
        assert candidate["index_entry_id"] == index_entry
        assert candidate["canonical_name"] == main_candidate["canonical_name"]
        assert candidate["sub_entry"] == sub_entry
        assert candidate["detail"] == detail
        assert candidate["index_page_range"] == page
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "index-seeded candidate has no mapped S2 mention" in alignment["resolution_note"]

    for cid, (decision, ku_id, kind) in UNCHANGED_NEIGHBORS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == kind
        assert (alignment["decision"], alignment["ku_id"]) == (decision, ku_id)

    planned = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned)
    for cid, (index_entry, sub_entry, detail, page) in TARGETS.items():
        row = planned_by_id[cid]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = f"{TASK}#{ANCHOR}"
        row["resolution_note"] += (
            f" S3复核（{DATE}）：原undecided理由保留为历史；{index_entry}是人物主项"
            f"“Medici, Grand Prince Ferdinand de'”（M.csv#149）下的person型索引子目“{sub_entry}”；"
            f"{('补充索引限定“' + detail + '”；') if detail else ''}印刷页码为{page}。"
            "主项cand-1609已same至既有人物KU；第8章p.229以Medici和Grand Prince Ferdinand指称该人，"
            "并在后续页连续叙述其父Cosimo III、兄弟Gian Gastone及其艺术活动；既有KU的前言与图版目录锚点相符。"
            f"因此本子目改判same → {KU_ID}。子目提到的画家、Venice及赞助／合作／支持措辞仅作索引定位，"
            "不据此建立正式关系或额外事实。"
        )

    for before, after in zip(alignments, planned):
        if before.get("candidate_id") not in TARGETS:
            assert before == after, f"unexpected alignment change: {before.get('candidate_id')}"

    before = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {key: sum(item[key] for item in before.values()) for key in next(iter(before.values()))}
    assert totals["same_candidates"] == before_totals["same_candidates"] + len(TARGETS)
    assert totals["same_kus"] == before_totals["same_kus"]
    assert totals["undecided"] == before_totals["undecided"] - len(TARGETS)
    for key in ("new_candidates", "new_groups", "registered_groups", "pending_groups", "pending_members"):
        assert totals[key] == before_totals[key]
    assert stats["person"]["same_candidates"] == before["person"]["same_candidates"] + len(TARGETS)
    assert stats["person"]["same_kus"] == before["person"]["same_kus"]
    assert stats["person"]["undecided"] == before["person"]["undecided"] - len(TARGETS)

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Grand Prince Ferdinand索引子项复用既有人物KU（{DATE}）\n\n"
        "- "
        + "、".join(
            f"{cid}（{index_entry}，{sub_entry}{'／' + detail if detail else ''}，p.{page}）"
            for cid, (index_entry, sub_entry, detail, page) in TARGETS.items()
        )
        + f"均由undecided改判same → [{KU_ID}](../../../04-knowledge/{KU_ID}.md)。M.csv#149主项为"
        "“Medici, Grand Prince Ferdinand de'”；以上10项是同一person主项下的索引子目，不是另10个人物。"
        "第8章p.229以Medici及Grand Prince Ferdinand明确开启其叙述，后文连续记述同一人物的出生、家庭、"
        "威尼斯旅行、收藏及与画家的往来；主项cand-1609及索引子项cand-1611、cand-1617已same至既有人物KU。\n"
        "- 边界：画家、Venice与16世纪威尼斯绘画仍是不同候选；艺术展览程序cand-1610保持其procedure KU，"
        "术语cand-1618和未分类收藏cand-1620保持原决定。子目描述的赞助、合作、用人或支持不转写为正式关系。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，"
        f"undecided={sync.fmt(totals['undecided'])}；S4待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text += (
        f"\n\n### S3 person：Grand Prince Ferdinand跨章索引身份组复用（{DATE}）\n\n"
        "10条人物主项下的索引子目现映射至既有Grand Prince Ferdinand人物KU；画家、地点、术语、展览程序及收藏候选"
        "保留各自类型和决定。详情见"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})及alignment.csv。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: same additions={len(TARGETS)}->{KU_ID}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; "
            f"undecided={totals['undecided']}; new_groups={totals['new_groups']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"preserved_same_members={len(EXISTING_MEMBERS)}; "
            f"adjacent_candidates_unchanged={len(UNCHANGED_NEIGHBORS)}; manifest={len(manifest)}"
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
