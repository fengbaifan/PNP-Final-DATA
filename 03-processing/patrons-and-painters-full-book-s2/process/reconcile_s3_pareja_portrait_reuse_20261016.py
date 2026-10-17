from __future__ import annotations

import argparse
import re
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
ALIGNMENT = ROOT / "04-knowledge" / "tables" / "alignment.csv"
CANDIDATES = ROOT / "04-knowledge" / "tables" / "entity-candidates.csv"
MANIFEST = ROOT / "04-knowledge" / "tables" / "ku-manifest.csv"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
CARD = ROOT / "04-knowledge" / "units" / "works" / "velasquez-juan-de-pareja.md"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
KU = "units/works/velasquez-juan-de-pareja"
CARD_PATH = "04-knowledge/units/works/velasquez-juan-de-pareja.md"
OLD_GROUP = "workgrp-63a60a31a83492"
PROCESS_REF = "S3-pareja-portrait-reuse-2026-10-16"
MEMBERS = ("cand-2714", "cand-6034")
SOURCES = (
    ("05_CHP-5_sec_i.md", "showed the portrait of his servant Pareja", "第5章记 Velasquez 于1650年在 Pantheon 展览中展出其仆人 Pareja 的肖像。"),
    ("08_CHP-8_sec_ii.md", "Velasquez’s portrait of his servant Juan de Pareja", "第8章再次以画家及人物全名描述该肖像。"),
    ("08_CHP-8_sec_ii.md", "It is the picture now in the Metropolitan Museum", "第8章注4将库存描述所指画作明确指认为现藏大都会艺术博物馆的作品。"),
)


def norm(value: str) -> str:
    return " ".join(value.split())


def group_of(note: str) -> str:
    match = re.search(r"group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Reuse the accepted Juan de Pareja portrait KU for the full-book S3 group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {row["candidate_id"]: row for row in alignments if row.get("candidate_id") and not row.get("external_source")}
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    assert len(decisions) == len(candidate_by_id) == 12404
    assert set(MEMBERS) <= set(candidate_by_id)
    target = manifest_by_id[KU]
    assert target["type"] == "work" and target["card_path"] == CARD_PATH
    assert CARD_PATH in ACCEPTED.read_text(encoding="utf-8-sig")
    assert CARD.is_file()

    group_members = sorted(cid for cid, row in decisions.items() if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == OLD_GROUP)
    assert group_members == sorted(MEMBERS), group_members
    for cid in MEMBERS:
        row = decisions[cid]
        assert candidate_by_id[cid]["suggested_type"] == "work"
        assert row["decision"] == "new" and not row.get("ku_id")
        assert group_of(row.get("resolution_note", "")) == OLD_GROUP

    for filename, quote, _ in SOURCES:
        source_path = ROOT / "02-sources" / "02-Markdown" / filename
        assert norm(quote) in norm(source_path.read_text(encoding="utf-8-sig")), (filename, quote)

    planned = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned if row.get("candidate_id") and not row.get("external_source")}
    old_notes = {}
    for cid in MEMBERS:
        row = planned_by_id[cid]
        old_notes[cid] = row["resolution_note"]
        row["decision"] = "same"
        row["ku_id"] = KU
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"matched_manifest={KU}; matched_existing_card={CARD_PATH}; source_ref={candidate_by_id[cid].get('candidate_source_ref', '')}; "
            "Same: Haskell’s Chapter 5 account of Velasquez showing his servant Pareja’s portrait in 1650 matches the full-title portrait in Chapter 8; "
            "Chapter 8 note 4 identifies that inventory picture as the painting now in the Metropolitan Museum, matching the accepted plate 34 KU. "
            f"Prior S3 new group id {OLD_GROUP} and prior rationale retained: {old_notes[cid]}"
        )

    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1761
    assert totals["new_candidates"] == 5005 and totals["new_groups"] == 4836
    assert totals["registered_groups"] == 236 and totals["registered_members"] == 295
    assert totals["pending_groups"] == 4600 and totals["pending_members"] == 4710

    card = CARD.read_text(encoding="utf-8-sig")
    assert "### 1650与1704年的展览记载" not in card
    source_block = """- citation: Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)
  location: 第5章；印刷页126；OCR L67
  sentence_summary: 第5章记 Velasquez 于1650年在 Pantheon 展览中展出其仆人 Pareja 的肖像。
  original_quotes:
  - source_span: lines 67
    text: showed the portrait of his servant Pareja
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/05_CHP-5_sec_i.md
    source_span: lines 67; print p. 126
- citation: Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)
  location: 第8章；印刷页222；OCR L133
  sentence_summary: 第8章再次以画家及人物全名描述该肖像。
  original_quotes:
  - source_span: lines 133
    text: Velasquez’s portrait of his servant Juan de Pareja
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/08_CHP-8_sec_ii.md
    source_span: lines 133; print p. 222
- citation: Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)
  location: 第8章注4；印刷页222；OCR L137
  sentence_summary: 第8章注4将库存描述所指画作明确指认为现藏大都会艺术博物馆的作品。
  original_quotes:
  - source_span: lines 137
    text: It is the picture now in the Metropolitan Museum
  evidence_ref:
    doc_id: patrons-and-painters
    source_file: 02-sources/02-Markdown/08_CHP-8_sec_ii.md
    source_span: lines 137; print p. 222
"""
    marker = "created: '2026-09-14'\n"
    assert card.count(marker) == 1
    card = card.replace(marker, source_block + marker, 1)
    assert "updated: '2026-09-15'" in card
    card = card.replace("updated: '2026-09-15'", "updated: '2026-10-16'", 1)
    assert "process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#剩余作品与收藏链集中审查" in card
    card = card.replace(
        "process_ref: 03-processing/patrons-and-painters-front-matter/process/knowledge.md#剩余作品与收藏链集中审查",
        f"process_ref: 03-processing/{TASK}/process/knowledge.md",
        1,
    )
    body = """### 1650与1704年的展览记载

**中文：** Haskell 第5章称 Velasquez 于1650年在 Pantheon 展览中展出其仆人 Pareja 的肖像；第8章以“Velasquez 的 Juan de Pareja 肖像”再次提及该作，并称它于1704年被送往罗马展览。第8章注4进一步把所引库存描述中的肖像认定为现藏大都会艺术博物馆的画作。该组跨章名称、画家和人物线索与本卡图版34及大都会藏品相合。以上记录 Haskell 的叙述与识别，不在此新增正式展出或借展关系。

**English:** Haskell says in Chapter 5 that Velasquez showed his portrait of his servant Pareja at the Pantheon exhibition in 1650. Chapter 8 again names Velasquez’s portrait of Juan de Pareja and reports that it was sent to an exhibition in Rome in 1704. Note 4 identifies the inventory picture as the painting now in the Metropolitan Museum. These cross-chapter references to the painter, sitter, and portrait match this card’s plate 34 and the Metropolitan collection record. This records Haskell’s account and identification; it does not add formal exhibition or loan relations.

"""
    body_marker = "## 关系与证据\n"
    assert card.count(body_marker) == 1
    card = card.replace(body_marker, body + body_marker, 1)

    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    explanation = (
        "\n\n### S3 作品复用：Juan de Pareja 肖像跨章组并入既有 KU（2026-10-16）\n\n"
        "`cand-2714`（第8章索引中的 Velasquez 肖像）与 `cand-6034`（第5章1650年 Pantheon 展览中的 Pareja 肖像）原共属 `workgrp-63a60a31a83492`，裁为 new。复核第8章 p.222 注4后改为复用既有 `units/works/velasquez-juan-de-pareja`：该注明确指出库存描述中的画作就是现藏 Metropolitan Museum 的作品；第8章正文使用完整画家和人物名，第5章记 Velasquez 在1650年展出的正是其仆人 Pareja 肖像。现有 KU 的图版34目录与 Met 藏品号进一步锁定该作品。两条 alignment 改为 same，`workgrp-63a60a31a83492` 及原裁理由保留在决定注记中；没有新增 KU 或 manifest 行。\n\n"
        "S2 中9条关系候选保持待 S6；本次没有改动 `relations.csv` 或已有关系。卡片补入第5章与第8章的书内引文及展览语境，但不新增正式展出／借展边。\n\n"
        f"更正后 S3：same={sync.fmt(totals['same_candidates'])}、new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组）、conflict={sync.fmt(totals['conflict'])}、excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。S4 已登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    process_text += explanation
    result_text += explanation

    if args.dry_run:
        print("S3 Pareja portrait reuse dry-run passed")
        print(f"same: {','.join(MEMBERS)} -> {KU}; prior new group={OLD_GROUP} retained in resolution history")
        print(f"source quotations checked={len(SOURCES)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}")
        print("No files changed.")
        return 0

    sync.write_csv(ALIGNMENT, alignment_fields, planned)
    CARD.write_text(card, encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("S3 Pareja portrait reuse applied: two candidates now map to the accepted work KU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
