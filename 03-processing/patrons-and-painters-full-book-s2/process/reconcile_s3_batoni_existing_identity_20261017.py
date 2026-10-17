from __future__ import annotations

import argparse
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
ACCEPTED_PATH = ROOT / "04-knowledge" / "accepted.yml"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
KU_ID = "units/persons/pompeo-batoni"
CARD_REL = "04-knowledge/units/persons/pompeo-batoni.md"
OLD_GROUP = "new-person:batoni-pompeo-e737feffb7"
SAME_GROUP = "sg3-ku-units-persons-pompeo-batoni"
CANDIDATES = ("cand-0260", "cand-0261", "cand-0262")


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the three Pompeo Batoni index candidates to the accepted Batoni person KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest_fields, manifest = sync.read_csv(MANIFEST_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    manifest_row = next(row for row in manifest if row.get("ku_id") == KU_ID)
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    card = (ROOT / CARD_REL).read_text(encoding="utf-8-sig")

    assert manifest_row.get("type") == "person"
    assert manifest_row.get("name_en") == "Pompeo Girolamo Batoni"
    assert manifest_row.get("card_path") == CARD_REL and CARD_REL in accepted
    assert "title: 蓬佩奥·吉罗拉莫·巴托尼（Pompeo Girolamo Batoni）" in card
    assert "| 惯用名 | Pompeo Batoni |" in card
    assert "| 全名 | Pompeo Girolamo Batoni／蓬佩奥·吉罗拉莫·巴托尼 |" in card
    assert decisions["cand-3871"]["decision"] == "same" and decisions["cand-3871"]["ku_id"] == KU_ID
    assert all(decisions[cid]["decision"] == "new" and not decisions[cid].get("ku_id") for cid in CANDIDATES)
    assert all(sync.get_group(decisions[cid].get("resolution_note", "")) == OLD_GROUP for cid in CANDIDATES)
    assert candidate_by_id["cand-0260"]["index_entry_id"] == "B.csv#107"
    assert candidate_by_id["cand-0261"]["index_entry_id"] == "B.csv#108" and candidate_by_id["cand-0261"]["sub_entry"] == "Cleopatra"
    assert candidate_by_id["cand-0262"]["index_entry_id"] == "B.csv#109" and candidate_by_id["cand-0262"]["sub_entry"] == "Triumph of Venice"
    assert all(candidate_by_id[cid]["suggested_type"] == "person" for cid in CANDIDATES)

    source_index = (ROOT / "02-sources/03-Index/03-1-Index-MD/B.md").read_text(encoding="utf-8-sig")
    ocr_index = " ".join((ROOT / "02-sources/02-Markdown/22_CHP-22Index.md").read_text(encoding="utf-8-sig").split())
    source_ch9 = " ".join((ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig").split())
    source_ch10 = " ".join((ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig").split())
    source_ch14 = " ".join((ROOT / "02-sources/02-Markdown/14_CHP-14_intro.md").read_text(encoding="utf-8-sig").split())
    source_ch17 = " ".join((ROOT / "02-sources/02-Markdown/17_CHP-17_sec_i.md").read_text(encoding="utf-8-sig").split())
    assert "| Batoni, Pompeo |  |  |  | xvii, 259, 298 |" in source_index
    assert "| Batoni, Pompeo |  | Cleopatra |  | 357 |" in source_index
    assert "| Batoni, Pompeo |  | Triumph of Venice |  | 259, 357, 381 |" in source_index
    assert "Batoni, Pompeo, xvii, 239, 298" in ocr_index
    assert "he employed Pompeo Batoni" in source_ch9 and "painting by Pompeo Batoni opposite" in source_ch10
    assert "He suggested that Batoni" in source_ch14 and "Batoni’s Triumph of Venice" in source_ch17

    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        row = planned_by_id[cid]
        old_note = row["resolution_note"]
        c = candidate_by_id[cid]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["resolution_note"] = (
            f"source_ref=candidate={cid};index_entry={c['index_entry_id']};matched_manifest={KU_ID};matched_candidate_ids=cand-3871;group={SAME_GROUP}; "
            "Same: the accepted person card records full name Pompeo Girolamo Batoni and conventional name Pompeo Batoni; existing candidate cand-3871 already maps to this KU. "
            "The normalized Index B.csv#107–109 gives the same personal name; its Cleopatra and Triumph of Venice subentries are person-index locators, not separate people. The Chapter 22 OCR reads 239 for the main-entry page, while the normalized index source records p.259; preserve this transcription discrepancy. "
            "Chapter 9 p.259 names Pompeo Batoni; Chapters 10 p.298 and 14 p.357 use the same painter in the related Cleopatra comparison/proposal, and Chapter 17 p.381 refers to the previously named Triumph of Venice. Reuse the existing person KU; no new KU or external source is needed. "
            f"prior_decision=new; prior_group={OLD_GROUP}; prior_resolution_note={old_note}"
        )

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3 跨章身份复核：Pompeo Batoni 复用既有人物 KU（2026-10-17）\n\n"
        f"`cand-0260`（B.csv#107）、`cand-0261`（B.csv#108，子目 Cleopatra）与 `cand-0262`（B.csv#109，子目 Triumph of Venice）原共属新人物组 `{OLD_GROUP}`。"
        f"既有[Pompeo Girolamo Batoni 人物卡](../../../{CARD_REL})明确记录全名 Pompeo Girolamo Batoni、惯用名 Pompeo Batoni；全书前置候选 `cand-3871` 已映射至 `{KU_ID}`。"
        "索引三条均是同一画家名下的作品定位；规范化索引源记录主项 p.259，Chapter 22 OCR 转录为 p.239 的差异保留待核。第9章 p.259 明称 Pompeo Batoni，第10章 p.298 与第14章 p.357 的 Cleopatra 比较/建议语境及第17章 p.381 对已述《Triumph of Venice》的回指相容。"
        f"三条决定从 `new` 更正为 `same`，并入既有组 `{SAME_GROUP}`、映射至 `{KU_ID}`；旧组号及每条原理由保留于 alignment 的 prior_group/prior_resolution_note。"
        "本轮不改人物卡、manifest、S2 断言或 relations.csv；作品及提案关系候选仍按原状态留待 S6。"
        f"修正后 S3 same={sync.fmt(totals['same_candidates'])}条、new={sync.fmt(totals['new_candidates'])}条/{sync.fmt(totals['new_groups'])}组；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )
    result_text += (
        "\n\n### S3 复核：Pompeo Batoni 跨章候选复用（2026-10-17）\n\n"
        f"`cand-0260`、`cand-0261`、`cand-0262` 从 `{OLD_GROUP}` 更正为 same，复用 `{KU_ID}`；既有卡明确记录全名与惯用名，`cand-3871` 已属同一 KU。旧决定和理由保存在 alignment 历史字段；未新增 KU 或正式关系。"
        f"S3 same={sync.fmt(totals['same_candidates'])}；new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}；S4 待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    if args.dry_run:
        print("S3 Batoni existing-identity dry-run passed")
        print("cand-0260/0261/0262 -> existing Pompeo Girolamo Batoni person KU; cand-3871 already reuses it")
        print("prior new-group token and all three rationales preserved")
        print(f"same={sync.fmt(totals['same_candidates'])}; new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}")
        print(f"S4 pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: cand-0260/0261/0262 now reuse {KU_ID}; no KU created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
