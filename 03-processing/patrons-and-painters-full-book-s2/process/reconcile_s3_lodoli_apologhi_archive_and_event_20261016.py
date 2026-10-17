from __future__ import annotations

import argparse
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
CANDIDATES = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
PROCESS_REF = "S3-lodoli-apologhi-archive-event-2026-10-16"

DECISIONS = {
    "cand-1413": {
        "type": "archive",
        "group": "sg3-archive-lodoli-apologhi-1787",
        "source": "L.csv#70 p.367; mention IDs=m-chp15-p367-memmo-0012,m-chp15-p367-memmo-0049",
        "note": (
            "S3 identity review 2026-10-16: new archive group=sg3-archive-lodoli-apologhi-1787. "
            "Printed p.367 note 2 gives the full title, Carlo de' Conti Lodoli as author, Bassano [Remondini], and 1787; "
            "the body identifies fifty-eight Apologhi published by Andrea Memmo. No matching archive KU exists in the manifest. "
            "The cited edition was not independently consulted, which limits content verification but does not make the book identity indeterminate."
        ),
    },
    "cand-1651": {
        "type": "event",
        "group": "sg3-event-publication-lodoli-apologhi-1787",
        "source": "M.csv#191 p.367; index sub-entry=publication of Lodoli's Apologhi",
        "note": (
            "S3 identity review 2026-10-16: new event group=sg3-event-publication-lodoli-apologhi-1787. "
            "The index sub-entry identifies the 1787 publication occasion; p.367 says Memmo published the fifty-eight fables "
            "to celebrate his assumption of the Procuratore di San Marco office, and note 2 confirms the dated imprint. "
            "This publication event is distinct from the Apologhi archive candidate cand-1413 and no matching event KU exists in the manifest."
        ),
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile the Lodoli Apologhi archive and publication-event candidates in S3.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(CANDIDATES)
    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert candidate_by_id["cand-1413"]["suggested_type"] == "archive"
    assert candidate_by_id["cand-1651"]["suggested_type"] == "event"
    assert alignment_by_id["cand-1413"]["decision"] == "undecided"
    assert alignment_by_id["cand-1651"]["decision"] == "undecided"
    assert "Apologhi" in candidate_by_id["cand-1413"]["sub_entry"]
    assert "publication" in candidate_by_id["cand-1651"]["sub_entry"]
    assert "1787" in candidate_by_id["cand-1413"]["detail"]
    assert "1787" in candidate_by_id["cand-1651"]["detail"]
    assert not any(
        "apologhi" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        and row.get("type") in {"archive", "event"}
        for row in manifest
    ), "a matching Apologhi archive/event KU exists; reuse it instead"

    source = (ROOT / "02-sources" / "02-Markdown" / "15_CHP-15_sec_ii.md").read_text(encoding="utf-8-sig")
    for quote in (
        "In 1787 he returned to Venice to take up the post of Procuratore di San Marco",
        "To celebrate his official assumption of office he published fifty-eight of Lodoli’s Apologhi",
        "Apologhi immaginati, e sol estemporaneamente in voce esposti agli amici suoi",
        "Bassano [Remondini], 1787",
    ):
        assert quote in source, quote

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    for cid, decision in DECISIONS.items():
        row = planned_by_id[cid]
        previous = row["resolution_note"]
        row.update(
            decision="new",
            ku_id="",
            process_ref=PROCESS_REF,
            accessed_date="",
            resolution_note=(
                f"source_ref=candidate={cid};{decision['source']};group={decision['group']}; "
                f"{decision['note']} prior_resolution_note={previous}"
            ),
        )

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_text += (
        "\n\n### S3 跨类型裁决：Lodoli《Apologhi》文本与1787年出版事件（2026-10-16）\n\n"
        "`cand-1413`（L.csv#70，archive）与 `cand-1651`（M.csv#191，event）分别改为 new。第15章 p.367 正文称 Andrea Memmo 于1787年回威尼斯就任 Procuratore di San Marco，并为纪念就职出版 Carlo de' Conti Lodoli 的五十八则 `Apologhi`；注2给出原文全题名及 Bassano [Remondini]、1787年出版项。故 archive 候选指这部特定印本，event 候选指出版发生，两者不合并；现有 manifest 无匹配 archive 或 event KU。书本身未独立查阅，当前只裁决书目身份，不作版本全文验证。新组分别为 `sg3-archive-lodoli-apologhi-1787` 与 `sg3-event-publication-lodoli-apologhi-1787`，进入 S4 各登记一 KU。原 undecided 理由保留在对齐行。未登记正式关系或开展 S5。"
    )
    result_text += (
        "\n\n### S3 跨类型身份组：Lodoli《Apologhi》及1787年出版事件（2026-10-16）\n\n"
        "archive 候选 `cand-1413` 与 event 候选 `cand-1651` 分别裁为 new，前者是 p.367 注2所列1787年印本，后者是 Memmo 就任 Procuratore di San Marco 时安排出版的事件。两项边界分开，分别进入 S4。旧待证理由保存在 alignment 行。"
    )

    if args.dry_run:
        print("S3 Lodoli Apologhi dry-run passed:")
        for cid, decision in DECISIONS.items():
            print(f"  {cid}: undecided {decision['type']} -> new group {decision['group']}")
        print("  body and note 2 source anchors checked; archive and publication event remain distinct")
        print(f"  S3 new={totals['new_candidates']:,}/{totals['new_groups']:,} groups; undecided={totals['undecided']:,}")
        print(f"  S4 pending={totals['pending_groups']:,}/{totals['pending_members']:,} candidate mappings")
        return 0

    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied S3 decisions for the Apologhi archive and 1787 publication event")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
