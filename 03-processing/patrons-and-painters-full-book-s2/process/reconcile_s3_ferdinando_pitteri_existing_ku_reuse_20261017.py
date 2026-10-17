from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
PROCESS_DIR = ROOT / "03-processing" / TASK / "process"
sys.path.insert(0, str(PROCESS_DIR))
import register_s4_crosschapter_person_endpoints_20261017_batch6 as precedent

sync = precedent.sync
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = PROCESS_DIR / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ITEMS = (
    {
        "candidate": "cand-1608",
        "ku_id": "units/persons/ferdinando-ii-de-medici",
        "group": "new-person:de-ferdinando-ii-medici-of-tuscany-86d09e74dc",
        "anchor": "s3-ferdinando-ii-reuse-20261017",
        "card": "04-knowledge/units/persons/ferdinando-ii-de-medici.md",
        "evidence": (
            "Index M.csv#148 names Ferdinando II de' Medici as Grand Duke of Tuscany and lists pages 76, 178, 403; "
            "chapter 20 p.403 says Grand Duke Ferdinand II, while chapter 7 identifies the relevant Grand Duke of Tuscany; "
            "the existing person card title and profile identify the same ruler."
        ),
        "same_note": (
            "The index full name/title and the cross-chapter ruler references match the accepted Ferdinando II de' Medici person KU; "
            "the existing card's distinct Van Dyck portrait evidence remains its own scope."
        ),
        "statement_ids": ("st-chp20-p403-campbell-ferdinand-ii-palazzo-pitti",),
    },
    {
        "candidate": "cand-1948",
        "ku_id": "units/persons/marco-pitteri",
        "group": "new-person:marco-pitteri-1a39ee76ea",
        "anchor": "s3-marco-pitteri-reuse-locator-review-20261017",
        "card": "04-knowledge/units/persons/marco-pitteri.md",
        "evidence": (
            "Chapter 9 p.200 explicitly names engraver Marco Pitteri; chapters 10 and 13 refer to Pitteri in engraving contexts; "
            "the existing accepted person card is Marco Alvise Pitteri and already cites the book's plate-list caption Marco Pitteri plus the Treccani identity record. "
            "The index candidate record reports pp.260, 312, 335n, while current P.csv row P.csv#149 reads pp.260, 312, 222n, and the chapter 9 source page marker reads p.200. "
            "The locator variants remain unresolved and are not used to create or merge a different person."
        ),
        "same_note": (
            "The exact artist form Marco Pitteri and engraving role match the accepted Marco Alvise Pitteri identity; reuse is supported independently of the unresolved page locator. "
            "Preserve the candidate's index range (260, 312, 335n), the current index row (260, 312, 222n), and chapter 9 source page marker p.200 as a locator discrepancy."
        ),
        "statement_ids": (
            "st-chp10-p312-pitteri-engraved-portraits-of",
            "st-chp13-p335-note2-pitteri-engraved-design",
        ),
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Correct two cross-chapter person groups from duplicate new to same existing KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    planned_alignment = [dict(row) for row in alignments]
    decision_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decision_by_id) == len(candidate_by_id)
    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]

    for item in ITEMS:
        cid = item["candidate"]
        row = decision_by_id[cid]
        assert candidate_by_id[cid].get("suggested_type") == "person"
        assert row.get("decision") == "new" and not row.get("ku_id"), row
        assert sync.get_group(row.get("resolution_note", "")) == item["group"]
        assert any(entry.get("ku_id") == item["ku_id"] and entry.get("type") == "person" and entry.get("card_path") == item["card"] for entry in manifest)
        card_path = ROOT / item["card"]
        assert card_path.exists()

        direct_relation_ids = {
            statement["statement_id"] for statement in statements
            if (statement.get("subject_candidate_id") == cid or statement.get("object_candidate_id") == cid)
            and (statement.get("qualifiers") or {}).get("relation_candidate") is True
        }
        assert direct_relation_ids == set(item["statement_ids"]), (cid, direct_relation_ids)

        if cid == "cand-1608":
            quote = "Medici, Ferdinando II de', Grand Duke of Tuscany"
            source = ROOT / "02-sources/03-Index/03-2-Index-CSV/M.csv"
            assert " ".join(quote.split()) in " ".join(source.read_text(encoding="utf-8-sig").split())
            assert "Grand Duke Ferdinand Il’s decision in 1637" in (ROOT / "02-sources/02-Markdown/20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
        else:
            assert "Marco Pitteri" in (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
            assert "Marco Pitteri" in card_path.read_text(encoding="utf-8-sig")
            assert "Pitteri, Marco" in (ROOT / "02-sources/03-Index/03-2-Index-CSV/P.csv").read_text(encoding="utf-8-sig")

        row["decision"] = "same"
        row["ku_id"] = item["ku_id"]
        row["process_ref"] = f"03-processing/{TASK}/process/knowledge.md#{item['anchor']}"
        row["resolution_note"] = (
            f"source_ref=candidate={cid}; prior_new_group={item['group']}; same_target={item['ku_id']}; "
            f"existing_KU_card={item['card']}; identity_comparison={item['evidence']} "
            "S4 duplicate check found the accepted person KU; corrected current S3 decision from new to same without creating a KU. "
            f"{item['same_note']}"
        )

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(result[key] for result in stats.values()) for key in next(iter(stats.values()))}
    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    result_next = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    result_append = f"""

### S3/S4 复核：Ferdinando II de’ Medici 与 Marco Alvise Pitteri 复用既有 KU（{DATE}）

`cand-1608`由`new-person:de-ferdinando-ii-medici-of-tuscany-86d09e74dc`改为`same` → [Ferdinando II de’ Medici人物卡](../units/persons/ferdinando-ii-de-medici.md)。M.csv索引全名与头衔、章7大公指称及章20“Grand Duke Ferdinand II”同现身份，既有卡已登记该人物；本次复用，不重复建卡。

`cand-1948`由`new-person:marco-pitteri-1a39ee76ea`改为`same` → [Marco Alvise Pitteri人物卡](../units/persons/marco-pitteri.md)。第9章p.200明确称“Marco Pitteri”，第10、13章继续以雕版家语境称Pitteri；既有卡已用图版目录中的“Marco Pitteri”及外部身份记录标识该人物。页码定位问题仍保留：候选记录写索引页260、312、335n；当前P.csv#149写260、312、222n；第9章来源页标为p.200。此差异不改变人物复用判断，不据此补造或替换章节定位。

两条候选均映射既有KU，不增加manifest或新卡。Ferdinando II的1条、Pitteri的2条直接S2关系候选仍待S6。

当前same {sync.fmt(totals['same_candidates'])}条，new {sync.fmt(totals['new_candidates'])}条（{sync.fmt(totals['new_groups'])}组）；S4新组已登记{sync.fmt(totals['registered_groups'])}组，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条映射；KU总数{sync.fmt(len(manifest))}。
"""
    result_next = result_next.rstrip() + result_append
    process_append = f"""

<a id="s3-ferdinando-ii-reuse-20261017"></a>

### S3/S4复核：Ferdinando II de’ Medici 复用既有人物 KU（{DATE}）

- `cand-1608`原判为`new-person:de-ferdinando-ii-medici-of-tuscany-86d09e74dc`。S4重复对象预检命中`units/persons/ferdinando-ii-de-medici`。M.csv#148索引完整写作“Medici, Ferdinando II de’, Grand Duke of Tuscany”；第7章p.178以Grand Duke of Tuscany出现，第20章p.403写Grand Duke Ferdinand II，现有人物卡正是Ferdinando II de’ Medici。索引姓名、头衔和跨章语境足以支持同一人物。
- 将`cand-1608`当前决定改为`same`并映射到既有KU；原new组留在`alignment.csv`理由中，不新建卡。`st-chp20-p403-campbell-ferdinand-ii-palazzo-pitti`记录的学术转述仍待S6逐条裁决。

<a id="s3-marco-pitteri-reuse-locator-review-20261017"></a>

### S3/S4复核：Marco Pitteri 复用既有人物 KU，页码定位待核（{DATE}）

- `cand-1948`原判为`new-person:marco-pitteri-1a39ee76ea`。S4重复对象预检命中既有`units/persons/marco-pitteri`，其规范名为Marco Alvise Pitteri；该卡引用同一书的图版目录“Marco Pitteri”并已有Treccani身份记录。第9章p.200正文明确称engraver Marco Pitteri，第10章p.312与第13章p.335注2均在雕版语境称Pitteri，足以支持身份复用。
- 页码分歧单独保留：`entity-candidates.csv`所存索引范围为260、312、335n，S1原始P.csv#149记录260、312、222n，而第9章Markdown页标为200。未把p.200改写为p.260，也未改动原始索引或来源资产；该问题是定位待核，不据此新建第二个Pitteri。
- 将`cand-1948`当前决定改为`same` → `units/persons/marco-pitteri`，原new组与定位差异均留痕。直接关系候选`st-chp10-p312-pitteri-engraved-portraits-of`及`st-chp13-p335-note2-pitteri-engraved-design`待S6；不新建KU或正式关系。

Both groups were initially marked new. Accepted person cards and source names identify Ferdinando II de’ Medici and Marco Alvise Pitteri as the existing targets, so their current alignment rows now use `same`. For Pitteri, the S1 index range, raw index row, and chapter 9 page marker remain discrepant; the locator issue is retained without changing source records or creating a duplicate person. All three direct relation candidates remain pending S6.
"""
    process_next = PROCESS.read_text(encoding="utf-8-sig").rstrip() + process_append

    if args.dry_run:
        print("dry-run passed: " + "; ".join(f"{item['candidate']} new -> same {item['ku_id']}" for item in ITEMS))
        print(
            f"same={totals['same_candidates']}; new={totals['new_candidates']}/{totals['new_groups']}; "
            f"registered={totals['registered_groups']}/{totals['registered_members']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged"
        )
        print("direct_relation_candidates=3 remain pending S6; page-locator discrepancy preserved; no new card or formal relation will be written")
        return 0

    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    PROCESS.write_text(process_next, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_next, encoding="utf-8-sig", newline="\n")
    print(f"applied: two candidates mapped same to existing KUs; manifest={len(manifest)} unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
