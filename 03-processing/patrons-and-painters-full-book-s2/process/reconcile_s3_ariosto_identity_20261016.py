from __future__ import annotations

import argparse
import json
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
PROCESS_REF = "S3-ariosto-cross-chapter-2026-10-16"
TRECCANI = "https://www.treccani.it/enciclopedia/ludovico-ariosto/"


def normalized(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile the Ariosto person and Orlando Furioso index subentry in S3.")
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
    person = candidate_by_id["cand-0116"]
    subentry = candidate_by_id["cand-0117"]
    poem = candidate_by_id["cand-5719"]
    proposed_edition = candidate_by_id["cand-9997"]

    assert person["suggested_type"] == "person"
    assert person["canonical_name"] == "Ariosto"
    assert subentry["suggested_type"] == "person"
    assert subentry["sub_entry"] == "Orlando Furioso"
    assert alignment_by_id["cand-0116"]["decision"] == "undecided"
    assert alignment_by_id["cand-0117"]["decision"] == "undecided"
    assert alignment_by_id["cand-5719"]["decision"] == "excluded"
    assert alignment_by_id["cand-9997"]["decision"] == "excluded"
    assert not any(
        row.get("type") == "person"
        and "ariosto" in (row.get("canonical_name", "") + " " + row.get("name_en", "")).casefold()
        for row in manifest
    ), "an Ariosto person KU already exists; do not create a duplicate"

    source_paths = [
        ROOT / "02-sources" / "02-Markdown" / "04_CHP-4_sec_ii.md",
        ROOT / "02-sources" / "02-Markdown" / "09_CHP-9_intro.md",
        ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md",
        ROOT / "02-sources" / "02-Markdown" / "20_CHP-20Postscript.md",
    ]
    source_text = normalized(" ".join(path.read_text(encoding="utf-8-sig") for path in source_paths))
    for quote in (
        "his own favourite Ariosto",
        "scenes from Homer, Virgil, Tasso and Ariosto",
        "Ariosto, Tasso and Metastasio",
        "scenes from Homer, Virgil, Ariosto and Tasso",
    ):
        assert normalized(quote) in source_text, quote
    assert "edition of the Orlando Furioso—a project that came to nothing" in source_text

    mentions = [
        row for row in sync.read_csv(TABLES / "mentions.csv")[1]
        if row.get("candidate_id") == "cand-0116"
    ]
    mention_ids = {row["mention_id"] for row in mentions}
    expected_mentions = {
        "m-chp4-sec-ii-l46-51-0003",
        "m-chp4-sec-ii-l46-51-0006",
        "m-chp9-p258-ariosto",
        "m-s2-ch13-p339-029",
        "m-chp20-p405-023",
    }
    assert expected_mentions <= mention_ids

    planned_candidates = [dict(row) for row in candidates]
    planned_alignment = [dict(row) for row in alignments]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    planned_alignment_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }

    person_row = planned_alignment_by_id["cand-0116"]
    prior_person_note = person_row["resolution_note"]
    person_row.update(
        decision="new",
        ku_id="",
        process_ref=PROCESS_REF,
        accessed_date="2026-10-16",
        resolution_note=(
            "source_ref=candidate=cand-0116;index_entry=A.csv#117;index_pages=339;"
            "s2_mentions=" + ",".join(sorted(expected_mentions)) +
            "; S3 cross-chapter identity review 2026-10-16; group=sg3-person-ludovico-ariosto; "
            "Chapter 4 p.103 calls Ariosto a poet whose work Galileo discusses; chapter 9 p.258 and chapter 20 p.405 name Ariosto among the literary sources for Tiepolo's Valmarana frescoes; chapter 13 p.339 names Ariosto among the Italian classics issued by Zatta. "
            f"Treccani identifies Ariosto as Ludovico Ariosto, a poet and author of Orlando Furioso ({TRECCANI}; accessed 2026-10-16). "
            "No matching person KU exists in the manifest. These chapter references identify one person; route as one new person KU in S4. "
            f"prior_resolution_note={prior_person_note}"
        ),
    )

    subentry_row = planned_alignment_by_id["cand-0117"]
    prior_subentry_note = subentry_row["resolution_note"]
    subentry_row.update(
        decision="excluded",
        ku_id="",
        process_ref=PROCESS_REF,
        accessed_date="",
        resolution_note=(
            "source_ref=candidate=cand-0117;index_entry=A.csv#118;index_pages=103,336;sub_entry=Orlando Furioso; "
            "S3 type correction: person -> work, because the index subentry names the literary text, not another person. "
            "Exclude the literary text from the current work KU scope, consistent with cand-5719's exclusion. "
            "The p.336 reference is a proposed edition that came to nothing; its separate archive candidate cand-9997 is also excluded because no realized edition or surviving archive is identified. "
            "Do not merge this title or proposal into the Ludovico Ariosto person KU. "
            f"prior_resolution_note={prior_subentry_note}"
        ),
    )
    planned_candidate_by_id["cand-0117"]["suggested_type"] = "work"

    stats = sync.summarize_by_type(planned_candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    process_note = (
        "\n\n### S3 跨章人物裁决：Ariosto 与《Orlando Furioso》索引子目（2026-10-16）\n\n"
        "`cand-0116`（A.csv#117）在第4章 p.103、第9章 p.258、第13章 p.339、第20章后记 p.405 均指 Ariosto。正文分别将其置于诗人、文学题材来源及经典作品出版语境；Treccani《在线百科》规范项为 Ariosto, Ludovico，明确其为诗人及《Orlando furioso》作者；"
        f"[Treccani 人物条目]({TRECCANI})（2026-10-16访问）。"
        "manifest 未有同名 person KU，故归为单一新人物组 `sg3-person-ludovico-ariosto`，待 S4 登记。身份组只合并人物提及，不把所指作品并入人物卡。\n\n"
        "`cand-0117`（A.csv#118，sub-entry `Orlando Furioso`，索引页码103、336）原标为 person，现按子目对象更正为 work。p.103 所指文学文本与 `cand-5719` 相同，而该文学文本不属于当前艺术作品 work KU 范围；p.336 指向 Gerbault 发起但未实现的拟议版本，archive 候选 `cand-9997` 已因无实际出版物或存世档案件而排除。该子目不是第二个人，也不与新建的 Ariosto 人物组或未实现出版计划合并，故裁为 excluded。原 undecided 理由保存在 alignment 行的 `prior_resolution_note`。本次未创建 KU、未登记关系或开展 S5。"
    )
    result_note = (
        "\n\n### S3 跨章身份组：Ariosto 人物与《Orlando Furioso》子目裁决（2026-10-16）\n\n"
        "`cand-0116` 改为单一新 person 组，覆盖第4、9、13、20章；`cand-0117` 从 person 更正为 work 并排除，因它指文学文本索引子目而非人物，p.336 未实现版本由既有 excluded archive 候选单独承接。原待证理由保存在 alignment 行。新人物组进入 S4 待登记；本批不新增 KU、正式关系或 S5 补足。"
    )
    process_text += process_note
    result_text += result_note

    if args.dry_run:
        print("S3 Ariosto reconciliation dry-run passed:")
        print("  cand-0116: undecided -> new person group sg3-person-ludovico-ariosto")
        print("  cand-0117: undecided person -> excluded work subentry")
        print("  cross-chapter mentions=5; Treccani identity page and source text checked")
        print(f"  S3 same={totals['same_candidates']:,}; new={totals['new_candidates']:,}/{totals['new_groups']:,} groups; excluded={totals['excluded']:,}; undecided={totals['undecided']:,}")
        print(f"  S4 registered={totals['registered_groups']:,}/{totals['registered_members']:,}; pending={totals['pending_groups']:,}/{totals['pending_members']:,}")
        return 0

    sync.write_csv(CANDIDATES, candidate_fields, planned_candidates)
    sync.write_csv(ALIGNMENT, alignment_fields, planned_alignment)
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("applied Ariosto cross-chapter identity and index-subentry decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
