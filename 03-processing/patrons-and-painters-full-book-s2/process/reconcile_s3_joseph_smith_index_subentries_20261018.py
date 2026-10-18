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
CARD_PATH = ROOT / "04-knowledge" / "units" / "persons" / "joseph-smith-venice.md"
DATE = "2026-10-18"
ANCHOR = "s3-joseph-smith-index-subentries-20261018"
KU_ID = "units/persons/joseph-smith-venice"
MAIN_CANDIDATE = "cand-2440"
GROUP = "new-person:joseph-m-smith-joseph-smith-de20176f48"
EXISTING_MEMBERS = {"cand-2440", "cand-2442", "cand-2443", "cand-2447", "cand-2468"}
TARGETS = {
    "cand-2441": ("S.csv#130", "and Canaletto", "304, 305, 306, 307, 308, 309, 310"),
    "cand-2444": ("S.csv#133", "and Marco Ricci", "303, 310"),
    "cand-2445": ("S.csv#134", "and neo-Palladianism", "308, 309"),
    "cand-2446": ("S.csv#135", "and Sebastiano Ricci", "302, 303, 306, 310"),
    "cand-2448": ("S.csv#137", "artistic tastes", "306"),
    "cand-2449": ("S.csv#138", "attitude of English contemporaries", "301"),
    "cand-2454": ("S.csv#143", "comparison of collection with Marshal Schulenburg's", "315"),
    "cand-2455": ("S.csv#144", "contacts with British visitors to Venice", "301, 302"),
    "cand-2456": ("S.csv#145", "contacts with Venetian society", "299, 300, 301"),
    "cand-2459": ("S.csv#148", "early collecting of paintings", "302, 303"),
    "cand-2463": ("S.csv#152", "move towards classicism in taste", "309"),
    "cand-2474": ("S.csv#163", "support for Pasquali's publishing firm", "299, 301, 306, 337"),
}
UNCHANGED_NEIGHBORS = {
    "cand-2450": ("new", "units/archives/bibliotheca-smithiana-1755", "archive"),
    "cand-2451": ("new", "", "archive"),
    "cand-2452": ("new", "", "archive"),
    "cand-2453": ("undecided", "", "event"),
    "cand-2457": ("undecided", "", "place"),
    "cand-2458": ("new", "units/archives/dactylografa-smithiana", "archive"),
    "cand-2460": ("undecided", "", "event"),
    "cand-2461": ("undecided", "", "event"),
    "cand-2464": ("new", "", "place"),
    "cand-2465": ("undecided", "", "event"),
    "cand-2466": ("undecided", "", "event"),
    "cand-2467": ("undecided", "", "event"),
    "cand-2469": ("undecided", "", "event"),
    "cand-2470": ("undecided", "", "event"),
    "cand-2471": ("new", "", "event"),
    "cand-2472": ("undecided", "", "event"),
    "cand-2473": ("undecided", "", "event"),
}


def decision_rows(alignment_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in alignment_rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align Joseph Smith person index subentries to the registered person KU."
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
    assert manifest_by_ku[KU_ID]["name_en"] == "Joseph Smith"
    main_candidate = candidate_by_id[MAIN_CANDIDATE]
    main_alignment = by_id[MAIN_CANDIDATE]
    assert main_candidate["index_entry_id"] == "S.csv#129"
    assert main_candidate["canonical_name"] == "Smith, Joseph"
    assert main_alignment["decision"] == "new" and main_alignment["ku_id"] == KU_ID
    assert sync.get_group(main_alignment["resolution_note"]) == GROUP

    existing_members = {
        cid for cid, row in by_id.items()
        if row["decision"] == "new" and sync.get_group(row.get("resolution_note", "")) == GROUP
    }
    assert existing_members == EXISTING_MEMBERS
    assert all(by_id[cid]["ku_id"] == KU_ID for cid in EXISTING_MEMBERS)

    smith_person_ids = {
        row["candidate_id"] for row in candidates
        if row["canonical_name"] == "Smith, Joseph"
        and row["suggested_type"] == "person"
        and row["index_source_file"] == "S.csv"
    }
    assert smith_person_ids == EXISTING_MEMBERS | set(TARGETS)
    for cid, (index_entry, sub_entry, page) in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["index_source_file"] == "S.csv"
        assert candidate["index_entry_id"] == index_entry
        assert candidate["canonical_name"] == "Smith, Joseph"
        assert candidate["sub_entry"] == sub_entry
        assert candidate["index_page_range"] == page
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "index-seeded candidate has no mapped S2 mention" in alignment["resolution_note"]

    candidate_by_id_guard = candidate_by_id
    for cid, (decision, ku_id, kind) in UNCHANGED_NEIGHBORS.items():
        candidate = candidate_by_id_guard[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == kind
        assert (alignment["decision"], alignment["ku_id"]) == (decision, ku_id)

    planned = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned)
    for cid, (index_entry, sub_entry, page) in TARGETS.items():
        row = planned_by_id[cid]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = f"{TASK}#{ANCHOR}"
        row["resolution_note"] += (
            f" S3复核（{DATE}）：原undecided理由保留为历史；{index_entry}是人物主项"
            f"“Smith, Joseph”（S.csv#129）下的person型索引子目“{sub_entry}”，印刷页码为{page}。"
            "主项正文在第10章p.299以全名Joseph Smith及“CONSUL JOSEPH SMITH”标题锚定，"
            "既有人物KU还由第9章p.264及第19章pp.391–394的领事／皇家收藏语境支持。"
            f"该子目定位的是同一主项人物，故改判same → {KU_ID}。子目中出现的其他人物、作品、主题、"
            "收藏比较及交往措辞只保留为索引定位，不据此建立正式关系、断言额外事实或合并相关端点。"
        )

    for before, after in zip(alignments, planned):
        if before.get("candidate_id") not in TARGETS:
            assert before == after, f"unexpected alignment change: {before.get('candidate_id')}"

    for cid, (decision, ku_id, kind) in UNCHANGED_NEIGHBORS.items():
        candidate = candidate_by_id[cid]
        alignment = planned_by_id[cid]
        assert candidate["suggested_type"] == kind
        assert (alignment["decision"], alignment["ku_id"]) == (decision, ku_id)

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
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Joseph Smith跨章索引身份组复用既有人物KU（{DATE}）\n\n"
        "- "
        + "、".join(
            f"{cid}（{index_entry}，{sub_entry}，p.{page}）"
            for cid, (index_entry, sub_entry, page) in TARGETS.items()
        )
        + f"均由undecided改判same → [{KU_ID}](../../../04-knowledge/{KU_ID}.md)。S.csv#129主项为“Smith, Joseph”；"
        "以上12项是同一person主项下跨第9、10、13、15及19章页码的索引子目，不是另12个人物。第10章p.299的全名与"
        "“CONSUL JOSEPH SMITH”标题、既有人物卡第9章p.264及第19章pp.391–394的语境共同支持主项身份。"
        "此前五条new候选仍保留其source-local人物组和S4映射；本批只把同一主项下其余12条索引候选same至已登记KU。\n"
        "- 边界：Canaletto、Marco Ricci、Sebastiano Ricci、Marshal Schulenburg等仍各自为不同候选人物；"
        "neo-Palladianism、审美、英格兰同代人的态度、访客与交往、收藏及Pasquali出版活动仅作为索引子目，"
        "不据此采纳新事实或登记正式关系。相邻archive、event、place候选和原决定均不变。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，"
        f"undecided={sync.fmt(totals['undecided'])}；S4待登记{sync.fmt(totals['pending_groups'])}组/"
        f"{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text += (
        f"\n\n### S3 person：Joseph Smith跨章索引身份组复用（{DATE}）\n\n"
        "12条同一人物主项下的索引子目现映射至既有Joseph Smith人物KU；索引中涉及的档案、作品、事件、地点、"
        "主题与其他人物均保留各自候选及当前决定。详情见"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})及alignment.csv。"
    )

    card_text = CARD_PATH.read_text(encoding="utf-8-sig")
    old_zh = (
        "五条索引候选覆盖其传记、与 McSwiny、Rosalba Carriera 的关联、Sagredo 购藏及皇家收藏语境；"
    )
    new_zh = (
        "原S4登记组的五条索引候选覆盖其传记、与 McSwiny、Rosalba Carriera 的关联、Sagredo 购藏及皇家收藏语境。"
        "S3另将同一人物主项下的12条person型索引子目映射为same，仅作为页码检索定位，不将子目短语作为独立人物、事实或正式关系；"
    )
    old_en = (
        "The five index candidates cover his biography, index links to McSwiny and Rosalba Carriera, the Sagredo purchases, "
        "and the Royal Collection context. "
    )
    new_en = (
        "The five index candidates in the original S4 registration group cover his biography, index links to McSwiny and "
        "Rosalba Carriera, the Sagredo purchases, and the Royal Collection context. S3 also maps twelve person-type index "
        "subentries under the same headword to this KU as same; they remain page-reference locators, and their labels do not "
        "become separate people, factual claims, or formal relations. "
    )
    assert card_text.count(old_zh) == 1
    assert card_text.count(old_en) == 1
    card_text = card_text.replace(old_zh, new_zh, 1).replace(old_en, new_en, 1)
    assert "updated: '2026-10-16'" in card_text
    card_text = card_text.replace("updated: '2026-10-16'", "updated: '2026-10-18'", 1)

    if args.dry_run:
        print(
            f"dry-run passed: same additions={len(TARGETS)}->{KU_ID}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; "
            f"undecided={totals['undecided']}; new_groups={totals['new_groups']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"preserved_new_group_members={len(EXISTING_MEMBERS)}; "
            f"adjacent_candidates_unchanged={len(UNCHANGED_NEIGHBORS)}; manifest={len(manifest)}"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    CARD_PATH.write_text(card_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: same additions={len(TARGETS)}->{KU_ID}; same={totals['same_candidates']}/{totals['same_kus']}; "
        f"undecided={totals['undecided']}; manifest={len(manifest)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
