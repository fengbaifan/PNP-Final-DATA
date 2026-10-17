from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
KNOWLEDGE = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-16"

MEMBERS = ("cand-1950", "cand-1952")
GROUP = "new-person:battista-giovan-pittoni-01fdd70f9d"
SAME_KU = "units/persons/pittoni"
CARD_REL = "04-knowledge/units/persons/pittoni.md"
NEW_PROCESS_REF = "S3-S4-Pittoni-reuse-existing-KU-2026-10-16"
BACKUP_SUFFIX = ".bak-s3-pittoni-reuse-20261016"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the full-book Giovan Battista Pittoni group to the accepted Pittoni person KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    existing = next((row for row in manifest if row.get("ku_id") == SAME_KU), None)
    assert existing is not None
    assert existing.get("type") == "person" and existing.get("card_path") == CARD_REL
    card_text = (ROOT / CARD_REL).read_text(encoding="utf-8-sig")
    assert "Giovanni Battista Pittoni" in card_text
    assert "Canaletto, Cimaroli and Pittoni" in card_text
    assert "Allegorical Tomb to the memory of Archbishop Tillotson" in card_text
    assert any(row.get("candidate_id") == "cand-3870" and row.get("decision") == "same" and row.get("ku_id") == SAME_KU for row in alignments)

    main_candidate = candidate_by_id[MEMBERS[0]]
    assert main_candidate.get("suggested_type") == "person"
    assert main_candidate.get("canonical_name") == "Pittoni, Giovan Battista"
    assert main_candidate.get("index_entry_id") == "P.csv#151"
    assert decisions[MEMBERS[0]].get("decision") == "new"
    assert sync.get_group(decisions[MEMBERS[0]].get("resolution_note", "")) == GROUP
    assert "Giovanni Battista Pittoni" in card_text

    expected = {
        "cand-1950": ("P.csv#151", "", "214, 260n, 288, 296, 297, 315, 345, 351, 361, 374"),
        "cand-1952": ("P.csv#153", "German patrons", "313"),
    }
    for cid, (entry, subentry, pages) in expected.items():
        candidate = candidate_by_id[cid]
        row = decisions[cid]
        assert candidate.get("suggested_type") == "person"
        assert candidate.get("canonical_name") == main_candidate["canonical_name"]
        assert candidate.get("index_entry_id") == entry
        assert candidate.get("sub_entry", "") == subentry
        assert candidate.get("index_page_range") == pages
        assert row.get("decision") == "new" and not row.get("ku_id")
        assert sync.get_group(row.get("resolution_note", "")) == GROUP

    _, index_rows = sync.read_csv(ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "P.csv")
    for entry_number, subentry in ((151, ""), (153, "German patrons")):
        source_row = index_rows[entry_number]
        assert source_row["Main Entry"] == "Pittoni, Giovan Battista"
        assert source_row["Sub-entry"] == subentry

    source_ch10 = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    source_ch10_ii = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_sec_ii.md").read_text(encoding="utf-8-sig")
    source_caption = (ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    assert "in Venice on Piazzetta and Pittoni" in source_ch10
    assert "Pittoni was considered to be one of the leading history painters in Venice" in source_ch10_ii
    assert "he was already much in favour with German patrons" in source_ch10_ii
    assert "Canaletto, Cimaroli, and Pittoni" in source_caption
    assert "Allegorical tomb to the memory of Archbishop Tillotson" in source_caption

    old_same = decisions.get("cand-3870")
    assert old_same and old_same.get("ku_id") == SAME_KU
    existing_same_kus = {
        row["ku_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "same" and row.get("ku_id")
    }
    assert SAME_KU in existing_same_kus

    statements_path = TABLES / "book-statements.jsonl"
    statements = [
        json.loads(line)
        for line in statements_path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    def contains_candidate(value, candidate_id: str) -> bool:
        if isinstance(value, dict):
            return any(contains_candidate(item, candidate_id) for item in value.values())
        if isinstance(value, list):
            return any(contains_candidate(item, candidate_id) for item in value)
        return value == candidate_id

    related = [
        statement for statement in statements
        if any(contains_candidate(statement, cid) for cid in MEMBERS)
    ]
    relation_count = sum(bool(row.get("qualifiers", {}).get("relation_candidate")) for row in related)
    assert len(related) == 29, f"unexpected Pittoni statement count: {len(related)}"
    assert relation_count == 20, f"unexpected Pittoni relation-candidate count: {relation_count}"

    planned = [dict(row) for row in alignments]
    for cid in MEMBERS:
        row = next(
            item for item in planned
            if item.get("candidate_id") == cid and not item.get("external_source")
        )
        old_note = row.get("resolution_note", "")
        previous_group = f"group={GROUP}"
        assert old_note.count(previous_group) == 1
        row["decision"] = "same"
        row["ku_id"] = SAME_KU
        row["process_ref"] = NEW_PROCESS_REF
        row["resolution_note"] = (
            old_note.replace(previous_group, f"previous_group_label={GROUP}", 1)
            + f" S3 re-review (2026-10-16): same as accepted person KU {SAME_KU}. The full-book index gives the same "
            "personal name in its main entry and the German patrons subentry; the book's p. 288 account and p. 313 "
            "passage identify Pittoni as the Venetian painter, matching the accepted card's Giovanni Battista Pittoni "
            "and the Tillotson memorial painting role. Full-book candidate cand-3870 already reuses this KU for the "
            "same image-caption identity. The Giovan/Giovanni spelling variant is supported by the full personal name "
            "in the existing source-backed card and its cited art-catalogue record; no new KU. Prior new group label "
            f"retained in previous_group_label. S4 reuse mapping: {SAME_KU}."
        )
        assert sync.get_group(row["resolution_note"]) == ""

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1764 and totals["same_kus"] == 1025, totals
    assert totals["new_candidates"] == 5006 and totals["new_groups"] == 4834, totals
    assert totals["pending_groups"] == 4563 and totals["pending_members"] == 4666, totals
    assert len(manifest) == 1290
    next_result = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )

    knowledge_text = KNOWLEDGE.read_text(encoding="utf-8-sig")
    marker = "### S3-S4 re-review: Pittoni reuses existing person KU (2026-10-16)"
    assert marker not in knowledge_text
    next_knowledge = knowledge_text + (
        f"\n\n{marker}\n\n"
        f"- cand-1950 与 cand-1952 原属 {GROUP}，索引主项和 German patrons 子项均写作 Pittoni, Giovan Battista。"
        "既有人物 KU units/persons/pittoni 的双语卡片名为 Giovanni Battista Pittoni，并已用本书图版目录、Zeri 作者字段与"
        "Tillotson 纪念画图注建立“图注 Pittoni”身份；全书 cand-3870 亦已判同并映射到该 KU。第10章 p.288 将 Pittoni 列在"
        "McSwiny 威尼斯绘画团队中，第10章 p.313 称其为威尼斯历史画家并明确关联 German patrons 子项。全名变体、画家身份和同一"
        "图版项目共同支持两候选复用既有身份，不是仅按姓氏合并。\n"
        f"- cand-1950、cand-1952 均由 new 改为 same，映射至 {SAME_KU}；原 new 组标签及理由分别保留在各自 alignment 行中。未创建"
        "重复卡片，未新增正式关系；涉及该人物的20条关系候选仍待 S6。\n\n"
        f"S3 same={sync.fmt(totals['same_candidates'])}/{sync.fmt(totals['same_kus'])}; "
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}; "
        f"undecided={sync.fmt(totals['undecided'])}. S4 registered="
        f"{sync.fmt(totals['registered_groups'])}/{sync.fmt(totals['registered_members'])}; pending="
        f"{sync.fmt(totals['pending_groups'])}/{sync.fmt(totals['pending_members'])}.\n"
    )

    target_files = [ALIGNMENT, KNOWLEDGE, RESULT]
    assert all(not path.with_name(path.name + BACKUP_SUFFIX).exists() for path in target_files)
    if args.dry_run:
        print(
            f"dry-run passed: {'/'.join(MEMBERS)} new->{SAME_KU} same; existing_card={CARD_REL}; "
            f"same={totals['same_candidates']}/{totals['same_kus']} new={totals['new_candidates']}/{totals['new_groups']} "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"relation_candidates_remain_pending={relation_count}; manifest={len(manifest)}"
        )
        return 0

    write_targets = {ALIGNMENT: None, KNOWLEDGE: next_knowledge, RESULT: next_result}
    for path in write_targets:
        shutil.copy2(path, path.with_name(path.name + BACKUP_SUFFIX))
    sync.write_csv(ALIGNMENT, alignment_fields, planned)
    for path, content in write_targets.items():
        if content is not None:
            path.write_text(content, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {'/'.join(MEMBERS)} -> existing {SAME_KU}; same={totals['same_candidates']}/{totals['same_kus']} "
        f"new={totals['new_candidates']}/{totals['new_groups']}; "
        f"pending_groups={totals['pending_groups']} pending_members={totals['pending_members']}; "
        f"relation_candidates_remain_pending={relation_count}; recovery_backups={len(write_targets)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
