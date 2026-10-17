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
KU_ID = "units/persons/anthony-blunt"
CARD_REL = "04-knowledge/units/persons/anthony-blunt.md"
OLD_GROUP = "new-person:anthony-blunt-anthony-blunt-opinion-s-c8c64cf49b"
CANDIDATES = ("cand-0379", "cand-5902")


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve two Sir Anthony Blunt candidate rows to the accepted Anthony Frederick Blunt KU.")
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
    card_path = ROOT / CARD_REL
    accepted = ACCEPTED_PATH.read_text(encoding="utf-8-sig")
    card = card_path.read_text(encoding="utf-8-sig")

    assert manifest_row.get("type") == "person" and manifest_row.get("name_en") == "Anthony Frederick Blunt"
    assert manifest_row.get("card_path") == CARD_REL and CARD_REL in accepted
    assert "| 惯用名 | Anthony Blunt |" in card
    assert "| 称谓 | Sir |" in card
    assert "| 全名 | Anthony Frederick Blunt |" in card
    assert candidate_by_id["cand-0379"]["canonical_name"] == "Blunt, Sir Anthony"
    assert candidate_by_id["cand-0379"]["index_entry_id"] == "B.csv#226"
    assert candidate_by_id["cand-5902"]["canonical_name"] == "Sir Anthony Blunt (art historian cited in Haskell’s note)"
    assert all(decisions[cid]["decision"] == "new" and not decisions[cid].get("ku_id") for cid in CANDIDATES)
    assert all(sync.get_group(decisions[cid].get("resolution_note", "")) == OLD_GROUP for cid in CANDIDATES)
    assert decisions["cand-3722"]["decision"] == "same" and decisions["cand-3722"]["ku_id"] == KU_ID

    source_index = " ".join((ROOT / "02-sources/02-Markdown/22_CHP-22Index.md").read_text(encoding="utf-8-sig").split())
    source_body = " ".join((ROOT / "02-sources/02-Markdown/04_CHP-4_sec_ii.md").read_text(encoding="utf-8-sig").split())
    assert "Blunt, Sir Anthony, 264n" in source_index
    assert "Sir Anthony Blunt’s opinion" in source_body or "Sir Anthony Blunt's opinion" in source_body

    statements = sync.load_statements()
    direct = {
        row["statement_id"]: row for row in statements
        if any(cid in (row.get("subject_candidate_id"), row.get("object_candidate_id")) for cid in CANDIDATES)
    }
    assert set(direct) == {
        "st-chp10-p308-note1-date-explanation",
        "st-chp2-seciv-l31-43-blunt-four-evangelists-hypothesis",
    }
    assert (direct["st-chp10-p308-note1-date-explanation"].get("qualifiers") or {}).get("relation_candidate") is False
    assert (direct["st-chp2-seciv-l31-43-blunt-four-evangelists-hypothesis"].get("qualifiers") or {}).get("relation_candidate") is True

    planned = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid in CANDIDATES:
        row = planned_by_id[cid]
        old_note = row["resolution_note"]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["resolution_note"] = (
            f"source_ref=candidate={cid}; matched_manifest={KU_ID}; matched_candidate_ids=cand-3722; "
            f"group=sg3-ku-{KU_ID.replace('/', '-')}; Same: the existing accepted card records Anthony Frederick Blunt's "
            "full name, the conventional name Anthony Blunt, and the historical title Sir. The source candidate gives "
            "‘Blunt, Sir Anthony’ or ‘Sir Anthony Blunt’; its index and note contexts match those explicit name forms. "
            "Reuse the existing person KU; no new KU or external source is needed. "
            f"prior_decision=new; prior_group={OLD_GROUP}; prior_resolution_note={old_note}"
        )

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(kind[key] for kind in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3 跨章身份复核：Sir Anthony Blunt 复用既有人物卡（2026-10-17）\n\n"
        f"候选 `cand-0379`（B.csv#226，索引形式 ‘Blunt, Sir Anthony’）与 `cand-5902`（正文注释形式 ‘Sir Anthony Blunt’）原作为同一新人物组 `{OLD_GROUP}`。"
        f"核对发现既有[Anthony Frederick Blunt 人物卡](../../../04-knowledge/units/persons/anthony-blunt.md)已明确记录全名、惯用名 ‘Anthony Blunt’ 与称号 ‘Sir’；候选 `cand-3722` 也已映射到该 KU。"
        f"两条决定据此从 `new` 更正为 `same`，均映射至 `{KU_ID}`；旧组 token 与逐行原理由保留在 `prior_group`/`prior_resolution_note` 字段。"
        "一条关于 Blunt 解释 Canaletto 日期的陈述为非关系；p.57 对其 Four Evangelists 系列假说的 statement 保持 relation_candidate，留待 S6。未新建 KU、未改 relations.csv。"
        f"修正后 S3 same={sync.fmt(totals['same_candidates'])}条、new={sync.fmt(totals['new_candidates'])}条/{sync.fmt(totals['new_groups'])}组；"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条；KU 总数{sync.fmt(len(manifest))}。"
    )
    result_text += (
        "\n\n### S3 复核：Anthony Blunt 身份复用（2026-10-17）\n\n"
        f"`cand-0379` 与 `cand-5902` 从 `{OLD_GROUP}` 更正为 same，复用 `{KU_ID}`；既有卡明确包含全名、惯用名与称号，候选 `cand-3722` 亦已指向该卡。旧决定和理由均留存于 alignment 历史字段。"
        "本轮没有新增 KU 或正式关系。"
        f"S3 same={sync.fmt(totals['same_candidates'])}；new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}；"
        f"S4 待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    if args.dry_run:
        print("S3 Blunt cross-chapter reuse dry-run passed")
        print("cand-0379 and cand-5902 -> existing Anthony Frederick Blunt KU; cand-3722 already reuses it")
        print("prior new-group tokens and full rationales preserved")
        print("one relation candidate remains pending S6; one statement remains non-relational")
        print(f"same={sync.fmt(totals['same_candidates'])}; new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}")
        print(f"S4 pending={sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}; no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: cand-0379 and cand-5902 now reuse {KU_ID}; no KU created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
