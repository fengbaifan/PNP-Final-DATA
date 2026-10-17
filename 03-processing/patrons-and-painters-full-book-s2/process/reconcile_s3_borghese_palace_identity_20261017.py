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

CANDIDATE = "cand-0398"
PRIOR_GROUP = "sg3-place-cand-0398"
REUSED_CANDIDATE = "cand-6796"
REUSE_GROUP = "sg3-ku-units-places-mazarin-bentivoglio-palace-rome"
KU_ID = "units/places/mazarin-bentivoglio-palace-rome"
CARD_REL = "04-knowledge/units/places/mazarin-bentivoglio-palace-rome.md"
RELATION_IDS = {
    "st-chp2-seciv-l65-77-borghese-palace-decoration-by-artists",
    "st-chp2-seciv-l65-77-enzo-buys-borghese-palace-1619",
    "st-chp2-seciv-l65-77-guido-relative-austerity-explained",
    "st-chp2-seciv-l65-77-mazarin-acquires-palace-from-lante",
    "st-chp2-seciv-l65-77-tassi-gentileschi-frescoes-1611-1612",
    "st-chp2-seciv-l65-77-borghese-palace-decoration-by-tassi",
    "st-chp2-seciv-l65-77-borghese-palace-decoration-by-gentileschi",
    "st-chp2-seciv-l65-77-borghese-palace-decoration-by-unnamed-artists",
}
PRIOR_NOTE = (
    "group=sg3-place-cand-0398; "
    "source_ref=chp-2:02_CHP-2_sec_iv:l65-77#m-chp2-seciv-l65-77-0002; "
    "S2 source anchor and type-specific description distinguish a source-supported object/concept "
    "not represented by an exact same-type KU; eligible for S4 registration after this decision."
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the Borghese Palace candidate to the accepted Bentivoglio palace KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    manifest = sync.read_csv(MANIFEST_PATH)[1]
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }

    candidate = candidate_by_id[CANDIDATE]
    target = alignment_by_id[CANDIDATE]
    already_registered = alignment_by_id[REUSED_CANDIDATE]
    assert candidate["index_entry_id"] == "B.csv#245"
    assert candidate["canonical_name"] == "Borghese Palace"
    assert candidate["index_page_range"] == "49"
    assert candidate["suggested_type"] == "place"
    assert target["decision"] == "new" and not target.get("ku_id")
    assert sync.get_group(target.get("resolution_note", "")) == PRIOR_GROUP
    assert already_registered["decision"] == "new" and already_registered.get("ku_id") == KU_ID
    assert sync.get_group(already_registered.get("resolution_note", "")) == "sg3-place-cand-6796"
    assert any(row.get("ku_id") == KU_ID and row.get("card_path") == CARD_REL for row in manifest)
    assert CARD_REL in ACCEPTED_PATH.read_text(encoding="utf-8-sig")

    index = (ROOT / "02-sources/03-Index/03-1-Index-MD/B.md").read_text(encoding="utf-8-sig")
    chapter2 = (ROOT / "02-sources/02-Markdown/02_CHP-2_sec_iv.md").read_text(encoding="utf-8-sig")
    chapter7 = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_i.md").read_text(encoding="utf-8-sig")
    card = (ROOT / CARD_REL).read_text(encoding="utf-8-sig")
    assert "| Borghese Palace | Rome |  |  | 49 |" in index
    assert "the great Borghese palace on the" in chapter2 and "Quirinal" in chapter2
    assert "The palace was bought by Bentivoglio from the Altemps family in 1619" in chapter2
    assert "The Bentivoglio sold the palace to the Lante family, from whom it was acquired by Cardinal Mazarin" in chapter2
    assert "Mazarin bought the palace from the Lante family which had acquired it from the Bentivoglio." in chapter7
    assert "Lante family which had acquired it from the Bentivoglio" in card

    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE or row.get("object_candidate_id") == CANDIDATE)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == RELATION_IDS, direct_relations

    planned_alignments = [dict(row) for row in alignments]
    planned_target = next(row for row in planned_alignments if row.get("candidate_id") == CANDIDATE)
    prior_note = planned_target["resolution_note"]
    planned_target["decision"] = "same"
    planned_target["ku_id"] = KU_ID
    planned_target["process_ref"] = (
        f"03-processing/{TASK}/process/knowledge.md#s3-borghese-palace-identity"
    )
    planned_target["resolution_note"] = (
        f"source_ref=chp-2:02_CHP-2_sec_iv:l65-77#m-chp2-seciv-l65-77-0002;"
        f"matched_manifest={KU_ID};matched_candidate_ids={REUSED_CANDIDATE};group={REUSE_GROUP};"
        "S3 correction 2026-10-17: the chapter 2 p.49 text identifies the Borghese palace on the Quirinal, "
        "says Enzo Bentivoglio bought it in 1619, then explicitly traces the palace from Bentivoglio to Lante "
        "and Cardinal Mazarin; chapter 7 p.183 note 2 gives the same Lante-to-Bentivoglio transfer chain. "
        "Reuse the already registered same-type place KU for the same physical building under its later "
        "Bentivoglio/Mazarin history; keep Villa Borghese separate. "
        f"prior_decision=new;prior_group={PRIOR_GROUP};prior_resolution_note={prior_note}"
    )

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"),
        stats,
        totals,
        len(manifest),
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n<a id=\"s3-borghese-palace-identity\"></a>\n\n"
        "### S3 更正：Borghese Palace 与既有 Bentivoglio/Mazarin 宫殿为同一地点（2026-10-17）\n\n"
        "候选 cand-0398（B.csv#245，印刷页49）原判 new，组 sg3-place-cand-0398。复核第2章 p.49：Haskell 将其称为 Quirinal 上的 great Borghese palace，称 Enzo Bentivoglio 于1619年购入；第2章注1记载 Bentivoglio 于1619年从 Altemps 家族购得该宫殿。正文随后明确称 Bentivoglio 将这座宫殿售予 Lante 家族，后由 Cardinal Mazarin 购得。第7章 p.183 注2以相同次序记载 Mazarin 从 Lante 购入、Lante 从 Bentivoglio 取得。"
        "既有 units/places/mazarin-bentivoglio-palace-rome 卡已记录 Bentivoglio → Lante → Mazarin 的同一转手链，并将对象类型定为 Rome 的宫殿建筑。两处证据在地点、建筑类型、所有权转移顺序和跨章互引上吻合，故 cand-0398 与已登记 cand-6796 指向同一宫殿；不是另一座 Borghese 建筑。Villa Borghese 仍为不同地点。"
        f"现将 cand-0398 从 new 更正为 same，映射至 {KU_ID}；S3 原决定、原组及原始 resolution_note 完整保存在 alignment 的 prior_decision、prior_group 与 prior_resolution_note 文本中。8条 cand-0398 直接 relation_candidate 保持原端点与分类；relations.csv、KU manifest、accepted.yml 均无需改动。"
        f"S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个既有KU）、new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组、conflict={sync.fmt(totals['conflict'])}、excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )
    result_text += (
        "\n\n### S3 更正：Borghese Palace 复用既有 Bentivoglio/Mazarin 宫殿 KU（2026-10-17）\n\n"
        "cand-0398（B.csv#245）由 new 更正为 same，映射至既有[马萨林购得的罗马本蒂沃利奥宫殿卡](../units/places/mazarin-bentivoglio-palace-rome.md)。第2章 p.49 将 Borghese 宫殿的1619年购置与后续 Bentivoglio—Lante—Mazarin 转手相连；第7章 p.183 注2给出相同转手链。保留原 new 决定与理由；8条关系候选未改。"
        f"S3 same={sync.fmt(totals['same_candidates'])}、new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组；S4 待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )

    if args.dry_run:
        print("S3 Borghese Palace identity correction dry-run passed")
        print(f"{CANDIDATE}: new/{PRIOR_GROUP} -> same/{KU_ID}")
        print(f"{REUSED_CANDIDATE} remains registered to the same KU; relation_candidates={len(direct_relations)} unchanged")
        print(
            f"same={sync.fmt(totals['same_candidates'])}/{sync.fmt(totals['same_kus'])} KUs; "
            f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])} groups; "
            f"S4 pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}"
        )
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE} -> same {KU_ID}; no KU, manifest, accepted entry, or relation added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
