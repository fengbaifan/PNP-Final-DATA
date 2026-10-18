from __future__ import annotations

import argparse
import csv
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
INDEX_PATH = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "O.csv"
SOURCE_PATH = ROOT / "02-sources" / "02-Markdown" / "03_CHP-3_sec_iv.md"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CARD_PATH = ROOT / "04-knowledge" / "units" / "persons" / "gian-paolo-oliva.md"
DATE = "2026-10-18"
ANCHOR = "s3-oliva-index-subentries-20261018"
KU_ID = "units/persons/gian-paolo-oliva"
HEADWORD = "Oliva, Gian Paolo"
EXISTING_MEMBERS = {"cand-1771", "cand-1775"}
TARGETS = {
    "cand-1772": ("O.csv#6", "and Bernini", "85, 86", "85–86"),
    "cand-1773": ("O.csv#7", "and Borgognone", "78, 79", "78–79"),
    "cand-1774": ("O.csv#8", "and Duke of Parma", "79, 80, 81", "79–81"),
    "cand-1776": ("O.csv#10", "and Cardinal Negroni", "84, 85", "84–85"),
}
UNCHANGED_NEIGHBORS = {
    "cand-1775": ("person", "new", KU_ID),
}


def decision_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align Oliva person-index cross-references to the existing Gian Paolo Oliva KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    by_id = decision_rows(alignments)
    assert len(by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    manifest = sync.read_csv(TABLES / "ku-manifest.csv")[1]
    assert any(row["ku_id"] == KU_ID and row["type"] == "person" for row in manifest)

    indexed = [
        row for row in candidates
        if row.get("index_source_file") == "O.csv"
        and row.get("canonical_name") == HEADWORD
        and row.get("suggested_type") == "person"
    ]
    assert {row["candidate_id"] for row in indexed} == EXISTING_MEMBERS | set(TARGETS)
    assert candidate_by_id["cand-1771"]["index_entry_id"] == "O.csv#5"
    assert all(by_id[cid]["ku_id"] == KU_ID for cid in EXISTING_MEMBERS)
    assert {by_id[cid]["decision"] for cid in EXISTING_MEMBERS} == {"new"}
    assert {sync.get_group(by_id[cid]["resolution_note"]) for cid in EXISTING_MEMBERS} == {
        "new-person:gian-oliva-paolo-b799139c04"
    }
    for cid, (index_entry, subentry, pages, _) in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == HEADWORD
        assert candidate["index_source_file"] == "O.csv"
        assert candidate["index_entry_id"] == index_entry
        assert candidate["sub_entry"] == subentry
        assert candidate["index_page_range"] == pages
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "index-seeded candidate has no mapped S2 mention" in alignment["resolution_note"]

    with INDEX_PATH.open(encoding="utf-8-sig", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    for _, (index_entry, subentry, pages, _) in TARGETS.items():
        row_number = int(index_entry.split("#")[1])
        row = index_rows[row_number]
        assert row["Main Entry"] == HEADWORD
        assert row["Sub-entry"] == subentry
        assert row["Page Numbers"] == pages

    source = SOURCE_PATH.read_text(encoding="utf-8-sig")
    for evidence in (
        "the outstanding personality was already the Vicar, Oliva",
        "He and his brother Guglielmo painted much for Oliva",
        "During the course of his futile negotiations with the Duke of Parma, Oliva",
        "When in 1661 Oliva became General, this connection was still further strengthened",
        "Very reluctantly and under extreme pressure Oliva was compelled to agree to the change",
    ):
        assert evidence in source, f"book evidence marker missing: {evidence}"

    planned = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned)
    for cid, (index_entry, subentry, pages, printed_pages) in TARGETS.items():
        row = planned_by_id[cid]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = f"{TASK}#{ANCHOR}"
        row["resolution_note"] += (
            f" S3复核（{DATE}）：原undecided理由保留为历史；{index_entry}在O.csv中与主项"
            f"“{HEADWORD}”同列，person型子目为“{subentry}”，书内页码{printed_pages}（索引记{pages}）。"
            "第3章相应段落继续以Vicar Oliva、Oliva及Jesuit General指称该既有人物："
            "pp.78–79将他置于Borgognone叙述，pp.79–81记其与帕尔马公爵的工程谈判，"
            "pp.84–85记其与Negroni的教堂装饰争议，pp.85–86明确称其为Jesuit General并叙述其与Bernini的友谊。"
            f"结合主项候选cand-1771及已登记同组cand-1775，两者均指向{KU_ID}，该索引子目定位同一人物，"
            f"故改判same → {KU_ID}。子目中的其他人物和往来语仅作索引定位，不据此登记正式关系或额外断言。"
        )

    for before, after in zip(alignments, planned):
        if before.get("candidate_id") not in TARGETS:
            assert before == after, f"unexpected alignment change: {before.get('candidate_id')}"
    for cid, (kind, decision, ku_id) in UNCHANGED_NEIGHBORS.items():
        assert candidate_by_id[cid]["suggested_type"] == kind
        assert (by_id[cid]["decision"], by_id[cid]["ku_id"]) == (decision, ku_id)

    before_stats = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {
        key: sum(item[key] for item in before_stats.values()) for key in next(iter(before_stats.values()))
    }
    assert totals["same_candidates"] == before_totals["same_candidates"] + len(TARGETS)
    assert totals["same_kus"] == before_totals["same_kus"] + 1
    assert totals["undecided"] == before_totals["undecided"] - len(TARGETS)
    for key in ("new_candidates", "new_groups", "registered_groups", "registered_members", "pending_groups", "pending_members", "conflict", "excluded", "total"):
        assert totals[key] == before_totals[key], f"unexpected count change: {key}"

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Oliva人物索引子目复用既有人物KU（{DATE}）\n\n"
        "- cand-1772（O.csv#6，and Bernini，pp.85–86）、cand-1773（O.csv#7，and Borgognone，pp.78–79）、"
        "cand-1774（O.csv#8，and Duke of Parma，pp.79–81）及cand-1776（O.csv#10，and Cardinal Negroni，pp.84–85）"
        f"均由undecided改判same → [{KU_ID}](../../../04-knowledge/{KU_ID}.md)。O.csv四条均以person型子目置于同一"
        f"“{HEADWORD}”主项；书内相应段落将其连接至主项cand-1771及已登记cand-1775所指的Jesuit General Gian Paolo Oliva。"
        "既有人物卡的第3章全名、总会长身份和第6章p.153语境与这些页码连续相符。\n"
        "- 边界：Bernini、Borgognone、Duke of Parma及Cardinal Negroni仍为各自的人物候选；子目只提供检索定位。"
        "不由索引交叉项建立友谊、赞助、委托或冲突等正式关系；相关书内断言仍按既有S2状态等待S6。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，undecided={sync.fmt(totals['undecided'])}；"
        f"S4待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(sync.read_csv(TABLES / "ku-manifest.csv")[1])
    )
    result_text += (
        f"\n\n### S3 person：Oliva人物索引子目身份归组（{DATE}）\n\n"
        "四条人物型交叉索引子目现映射至既有Gian Paolo Oliva人物KU；索引中涉及的其他人物与书内往来继续保留各自身份及证据状态。"
        f"详情见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})及alignment.csv。"
    )

    card_text = CARD_PATH.read_text(encoding="utf-8-sig")
    old_zh = (
        "cand-1771 的一般人物条目与 cand-1775 的“and Gaulli”交叉子目均锚定第3章这位以全名出现的耶稣会士；"
    )
    new_zh = (
        "cand-1771的一般人物主项以及cand-1772（and Bernini）、cand-1773（and Borgognone）、cand-1774（and Duke of Parma）、"
        "cand-1775（and Gaulli）与cand-1776（and Cardinal Negroni）均隶属同一人物主项；四条原待决person型子目现映射为same。"
        "它们锚定第3章这位以全名出现的耶稣会士；"
    )
    old_en = (
        "cand-1771's general entry and cand-1775's “and Gaulli” cross-reference both anchor to the Jesuit named in full in Chapter 3; "
    )
    new_en = (
        "cand-1771's general person entry and cand-1772 (and Bernini), cand-1773 (and Borgognone), cand-1774 (and Duke of Parma), "
        "cand-1775 (and Gaulli), and cand-1776 (and Cardinal Negroni) all belong to the same person headword; the four previously "
        "undecided person-type subentries now map to this KU as same. They anchor to the Jesuit named in full in Chapter 3; "
    )
    assert card_text.count(old_zh) == 1
    assert card_text.count(old_en) == 1
    card_text = card_text.replace(old_zh, new_zh, 1).replace(old_en, new_en, 1)
    assert "updated: '2026-10-16'" in card_text
    card_text = card_text.replace("updated: '2026-10-16'", f"updated: '{DATE}'", 1)

    if args.dry_run:
        print(
            f"dry-run passed: same additions={len(TARGETS)}->{KU_ID}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; undecided={totals['undecided']}; "
            f"new_groups={totals['new_groups']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
            "preserved_existing_group_members=2; formal_relations_added=0"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    CARD_PATH.write_text(card_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: same additions={len(TARGETS)}->{KU_ID}; "
        f"same={totals['same_candidates']}/{totals['same_kus']}; undecided={totals['undecided']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
