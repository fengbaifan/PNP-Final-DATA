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
INDEX_PATH = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "B.csv"
SOURCE_PATH = ROOT / "02-sources" / "02-Markdown" / "06_CHP-6_sec_iv.md"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CARD_PATH = ROOT / "04-knowledge" / "units" / "persons" / "giovanni-pietro-bellori.md"
DATE = "2026-10-18"
ANCHOR = "s3-bellori-remaining-index-subentries-20261018"
KU_ID = "units/persons/giovanni-pietro-bellori"
HEADWORD = "Bellori, Gian Pietro"
EXISTING_MEMBERS = {"cand-0272", "cand-0274", "cand-0277"}
EXISTING_GROUP = "sg3-ku-units-persons-giovanni-pietro-bellori"
TARGETS = {
    "cand-0273": ("B.csv#120", "as librarian and antiquarian to Queen Christina of Sweden", "160, 161"),
    "cand-0275": ("B.csv#122", "devotion to Raphael", "159"),
    "cand-0276": ("B.csv#123", "influence of his views", "160"),
}


def decision_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Map remaining Bellori person-index subentries to the existing Bellori person KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    by_id = decision_rows(alignments)
    assert len(by_id) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert any(row["ku_id"] == KU_ID and row["type"] == "person" for row in manifest)

    indexed = [
        row for row in candidates
        if row.get("index_source_file") == "B.csv"
        and row.get("canonical_name") == HEADWORD
        and row.get("suggested_type") == "person"
    ]
    assert {row["candidate_id"] for row in indexed} == EXISTING_MEMBERS | set(TARGETS)
    for cid in EXISTING_MEMBERS:
        assert by_id[cid]["decision"] == "same" and by_id[cid]["ku_id"] == KU_ID
        assert sync.get_group(by_id[cid]["resolution_note"]) == EXISTING_GROUP
    for cid, (index_entry, subentry, pages) in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == HEADWORD
        assert candidate["index_source_file"] == "B.csv"
        assert candidate["index_entry_id"] == index_entry
        assert candidate["sub_entry"] == subentry
        assert candidate["index_page_range"] == pages
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "index-seeded candidate has no mapped S2 mention" in alignment["resolution_note"]

    with INDEX_PATH.open(encoding="utf-8-sig", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    for _, (index_entry, subentry, pages) in TARGETS.items():
        row_number = int(index_entry.split("#")[1])
        row = index_rows[row_number]
        assert row["Main Entry"] == HEADWORD
        assert row["Sub-entry"] == subentry
        assert row["Page Numbers"] == pages

    source = SOURCE_PATH.read_text(encoding="utf-8-sig")
    for evidence in (
        "was Gian Pietro Bellori.",
        "The devout love for Raphael that both men felt",
        "His influence grew with the years.",
        "appointed librarian and antiquarian to Queen",
        "owing to the overriding influence of Bellori",
    ):
        assert evidence in source, f"book evidence marker missing: {evidence}"

    planned = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned)
    for cid, (index_entry, subentry, pages) in TARGETS.items():
        row = planned_by_id[cid]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = f"{TASK}#{ANCHOR}"
        row["resolution_note"] += (
            f" S3复核（{DATE}）：原undecided理由保留为历史；{index_entry}在B.csv中属于person主项"
            f"“{HEADWORD}”（B.csv#119），子目为“{subentry}”，印刷页码{pages}。"
            "第6章p.158以全名Gian Pietro Bellori引入人物；p.159–161连续使用Bellori并记其对Raphael的推崇、"
            "批评影响及在Queen Christina宫廷的职务。主项cand-0272及已same至本KU的cand-0274、cand-0277"
            "已把相同姓名和跨章语境连接到既有人物卡；其Q714400对齐也保留在历史记录中。"
            f"该索引子目定位同一人物，故改判same → {KU_ID}。职务、评价及其他索引涉及的人物不由此扩写为本卡事实或正式关系。"
        )

    for before, after in zip(alignments, planned):
        if before.get("candidate_id") not in TARGETS:
            assert before == after, f"unexpected alignment change: {before.get('candidate_id')}"

    before_stats = sync.summarize_by_type(candidates, alignments)
    stats = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    before_totals = {
        key: sum(item[key] for item in before_stats.values()) for key in next(iter(before_stats.values()))
    }
    assert totals["same_candidates"] == before_totals["same_candidates"] + len(TARGETS)
    assert totals["same_kus"] == before_totals["same_kus"]
    assert totals["undecided"] == before_totals["undecided"] - len(TARGETS)
    for key in ("new_candidates", "new_groups", "registered_groups", "registered_members", "pending_groups", "pending_members", "conflict", "excluded", "total"):
        assert totals[key] == before_totals[key], f"unexpected count change: {key}"

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Bellori人物索引子目复用既有人物KU（{DATE}）\n\n"
        "- cand-0273（B.csv#120，as librarian and antiquarian to Queen Christina of Sweden，pp.160–161）、"
        "cand-0275（B.csv#122，devotion to Raphael，p.159）及cand-0276（B.csv#123，influence of his views，p.160）"
        f"均由undecided改判same → [{KU_ID}](../../../04-knowledge/{KU_ID}.md)。三项都是person主项"
        f"“{HEADWORD}”下的person型子目。第6章p.158给出全名，p.159–161连续叙述同一Bellori，"
        "既有cand-0272、cand-0274、cand-0277与跨章Bellori候选已映射同一KU。\n"
        "- 边界：Queen Christina、Raphael及其他索引人物仍各有独立候选。子目只作索引检索定位；"
        "不把职务、艺术观点或其影响转写成新增事实或正式关系，也不改变既有人物卡限定为第1章证据的内容范围。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，undecided={sync.fmt(totals['undecided'])}；"
        f"S4待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text += (
        f"\n\n### S3 person：Bellori人物索引子目身份归组（{DATE}）\n\n"
        "三个有关其任职、Raphael及艺术观点的person型索引子目现映射至既有Bellori人物KU；"
        "卡片事实范围、其他人物身份及正式关系均不由索引交叉项扩写。详情见"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})及alignment.csv。"
    )

    card_bytes = CARD_PATH.read_bytes()
    card_encoding = "utf-8-sig" if card_bytes.startswith(b"\xef\xbb\xbf") else "utf-8"
    card_text = card_bytes.decode(card_encoding)
    identity_section = (
        "### 索引身份对应\n\n"
        "中文：B.csv#119“Bellori, Gian Pietro”主项及cand-0273、cand-0275、cand-0276三个person型子目现均映射至本卡。"
        "第6章p.158–161以Gian Pietro Bellori全名及连续叙述锚定该身份；主项cand-0272和已有同身份子目cand-0274、cand-0277"
        "此前已映射至本KU。这里仅确认索引指向同一人；Queen Christina相关职务、Raphael偏好及其影响仍不扩充本卡事实或正式关系。\n\n"
        "English: The B.csv#119 headword “Bellori, Gian Pietro” and its person-type subentries cand-0273, cand-0275, and cand-0276 "
        "now all map to this card. Chapter 6, pp. 158–161, anchors the identity with the full name Gian Pietro Bellori and a continuous account; "
        "the headword candidate cand-0272 and established person subentries cand-0274 and cand-0277 already map to this KU. This confirms only that the "
        "index refers to the same person; the Queen Christina office, Raphael preference, and influence do not expand this card's facts or formal relations.\n\n"
    )
    assert "### 索引身份对应\n" not in card_text
    assert card_text.count("## 关系与证据\n") == 1
    assert "updated: 2026-09-14" in card_text
    card_text = card_text.replace("## 关系与证据\n", identity_section + "## 关系与证据\n", 1)
    card_text = card_text.replace("updated: 2026-09-14", f"updated: {DATE}", 1)

    if args.dry_run:
        print(
            f"dry-run passed: same additions={len(TARGETS)}->{KU_ID}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; undecided={totals['undecided']}; "
            f"new_groups={totals['new_groups']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
            "preserved_existing_members=3; formal_relations_added=0"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned)
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    CARD_PATH.write_text(card_text, encoding=card_encoding, newline="\n")
    print(
        f"applied: same additions={len(TARGETS)}->{KU_ID}; "
        f"same={totals['same_candidates']}/{totals['same_kus']}; undecided={totals['undecided']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
