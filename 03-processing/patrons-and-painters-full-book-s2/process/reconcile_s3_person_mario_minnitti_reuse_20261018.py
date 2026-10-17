from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_person_relation_endpoints_allegrini_bouchardon_20261018 as person_sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
DATE = "2026-10-18"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CARD = "04-knowledge/units/persons/mario-minnitti.md"
KU = "units/persons/mario-minnitti"
ANCHOR = "s3-person-mario-minnitti-reuse-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
GROUP = "sg3-ku-units-persons-mario-minnitti"
OLD_QUOTE = "New source-local person candidate: no unique existing person KU matched; source anchor gives a full personal name."
SHARED_QUOTE = "Mario Minnitti in Augusta (Sicily) in 1617"


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile the M-index spelling variant to the accepted Mario Minniti KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    candidate = next(row for row in candidates if row.get("candidate_id") == "cand-1671")
    row = next(row for row in alignments if row.get("candidate_id") == "cand-1671" and not row.get("external_source"))
    target = next(row for row in manifest if row.get("ku_id") == KU)
    assert candidate.get("suggested_type") == "person"
    assert candidate.get("canonical_name") == "Minitti, Mario"
    assert candidate.get("index_entry_id") == "M.csv#211"
    assert candidate.get("index_page_range") == "9n"
    assert row.get("decision") == "new" and not row.get("ku_id")
    assert sync.get_group(row.get("resolution_note", "")) == "new-person:mario-minitti-86e2f9e4a5"
    assert target.get("type") == "person" and target.get("name_en") == "Mario Minniti"
    assert target.get("card_path") == CARD
    assert (ROOT / CARD).is_file()
    index_rows = person_sync.read_index_rows("M.csv")
    index_row = index_rows[211]
    assert index_row.get("Main Entry") == "Minitti, Mario"
    assert index_row.get("Page Numbers", "") == "9n"
    source = (ROOT / "02-sources/02-Markdown/01_CHP-1_sec_ii.md").read_text(encoding="utf-8-sig")
    card_text = (ROOT / CARD).read_text(encoding="utf-8-sig")
    assert SHARED_QUOTE in source and SHARED_QUOTE in card_text
    assert "Minnitti" in card_text and "Mario Minniti" in card_text
    prior_same = next(
        item for item in alignments
        if item.get("candidate_id") == "cand-3081" and item.get("decision") == "same"
        and item.get("ku_id") == KU and not item.get("external_source")
    )
    assert sync.get_group(prior_same.get("resolution_note", "")) == GROUP
    statement = next(
        item for item in sync.load_statements()
        if item.get("statement_id") == "st-chp1-secii-notes-local-commissions-minnitti-1617"
    )
    assert statement.get("object_candidate_id") == "cand-1671"
    assert (statement.get("qualifiers") or {}).get("relation_candidate") is True

    planned = [dict(item) for item in alignments]
    planned_row = next(item for item in planned if item.get("candidate_id") == "cand-1671" and not item.get("external_source"))
    planned_row["ku_id"] = KU
    planned_row["decision"] = "same"
    planned_row["process_ref"] = PROCESS_REF
    planned_row["resolution_note"] = (
        "source_ref=candidate=cand-1671;index_entry=M.csv#211;index_pages=9n;"
        "s2_statement=st-chp1-secii-notes-local-commissions-minnitti-1617;"
        "matched_manifest=units/persons/mario-minnitti[name_en=Mario Minniti;card_path=04-knowledge/units/persons/mario-minnitti.md]; "
        f"group={GROUP}; Same: the M-index form ‘Minitti, Mario’ at p.9n points to the Chapter 1 footnote naming ‘Mario Minnitti’ "
        "in Augusta in 1617. The exact Haskell passage and citation are already preserved in the accepted Mario Minniti card, "
        "which records Minnitti as a source spelling variant for this person. Reuse the existing KU; the index spelling is not a second person. "
        f"Previous S3 new rationale superseded: {OLD_QUOTE} The cited Agnello publication and any original contract are not independently consulted; "
        "no external identity source was accessed."
    )

    baseline = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["new_groups"] == baseline["person"]["new_groups"] - 1
    assert stats["person"]["new_candidates"] == baseline["person"]["new_candidates"] - 1
    assert stats["person"]["same_candidates"] == baseline["person"]["same_candidates"] + 1
    assert stats["person"]["same_kus"] == baseline["person"]["same_kus"]
    assert stats["person"]["registered_groups"] == baseline["person"]["registered_groups"]
    assert stats["person"]["pending_groups"] == baseline["person"]["pending_groups"] - 1
    assert stats["person"]["pending_members"] == baseline["person"]["pending_members"] - 1

    process_text = process_sync.refresh_process_type_table(PROCESS_PATH.read_text(encoding="utf-8-sig"), stats)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3人物身份复核：复用Mario Minniti既有KU（{DATE}）\n\n"
        "cand-1671的书后索引M.csv#211写作“Minitti, Mario”，指向第1章脚注页9n；同一脚注正文写“Mario Minnitti in Augusta (Sicily) in 1617”。"
        f"已采纳的[{CARD.split('/')[-1]}](../../../{CARD})保存了完全相同的Haskell段落和来源引用，并明确将“Mario Minnitti”列为该人物的来源拼写异形。"
        "因此撤回cand-1671的S3 new判断，改为same → units/persons/mario-minnitti；旧决定理由（未匹配既有KU）不再成立，"
        "索引多一个t的拼写不是另一人物。新映射加入既有身份组，未新增KU或外部来源。脚注引述的Agnello出版材料及原始合同仍未独立核读；"
        "关系候选st-chp1-secii-notes-local-commissions-minnitti-1617仍待S6。\n\n"
        f"复核后人物S3为same {sync.fmt(stats['person']['same_kus'])}个KU/{sync.fmt(stats['person']['same_candidates'])}条，"
        f"new {sync.fmt(stats['person']['new_groups'])}组/{sync.fmt(stats['person']['new_candidates'])}条；"
        f"S4新组待登记{sync.fmt(stats['person']['pending_groups'])}组/{sync.fmt(stats['person']['pending_members'])}条，全书KU={len(manifest)}。"
    )
    result_text = sync.update_result(RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    result_text += (
        f"\n\n### S3人物身份复核：Mario Minniti姓名异形复用（{DATE}）\n\n"
        "cand-1671由new改判same，映射至既有Mario Minniti KU。M.csv的“Minitti, Mario”与第1章脚注的“Mario Minnitti”指向同一页9n材料；"
        "既有卡已保存该精确Haskell引文并将Minnitti记录为来源拼写异形。未新增KU或外部来源；Agnello转引材料/原始合同仍未独立核读，"
        f"关系候选留待S6。详见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#{ANCHOR})。"
    )

    if args.dry_run:
        print(
            "dry-run passed: index/body/accepted-card/source equivalence confirmed; "
            f"new person groups={baseline['person']['new_groups']}->{stats['person']['new_groups']}; "
            f"S4 pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; "
            "KU unchanged; external sources added=0; no files changed"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: cand-1671=same->{KU}; person_new_groups={stats['person']['new_groups']}; "
        f"person_pending={stats['person']['pending_groups']}/{stats['person']['pending_members']}; KU unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
