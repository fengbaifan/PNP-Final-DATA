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
INDEX_PATH = ROOT / "02-sources" / "03-Index" / "03-2-Index-CSV" / "A.csv"
SOURCE_PATH = ROOT / "02-sources" / "02-Markdown" / "13_CHP-13_intro.md"
FRONT_MATTER_PATH = ROOT / "02-sources" / "02-Markdown" / "00_05_List_of_Plates.md"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CARD_PATH = ROOT / "04-knowledge" / "units" / "persons" / "albrizzi.md"
DATE = "2026-10-18"
ANCHOR = "s3-albrizzi-index-subentries-20261018"
KU_ID = "units/persons/albrizzi"
HEADWORD = "Albrizzi, Giambattista"
MAIN_CANDIDATE = "cand-0025"
EXISTING_CANDIDATE = "cand-3711"
ALIGNED_SAME = {"cand-0025", "cand-0027", "cand-0029"}
TARGETS = {
    "cand-0026": ("A.csv#25", "edition of works of Bossuet", "334, 335", "334–335"),
    "cand-0028": ("A.csv#27", "Il Forestiere Illuminato", "334", "334"),
    "cand-0030": (
        "A.csv#29",
        "publication of gems in A. M. Zanetti's collection",
        "337, 344",
        "337, 344",
    ),
}


def decision_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {
        row["candidate_id"]: row
        for row in rows
        if row.get("candidate_id") and not row.get("external_source")
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align the remaining Albrizzi person-index subentries to the existing person KU."
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
        if row.get("index_source_file") == "A.csv"
        and row.get("canonical_name") == HEADWORD
        and row.get("suggested_type") == "person"
    ]
    assert {row["candidate_id"] for row in indexed} == ALIGNED_SAME | set(TARGETS)
    for cid in ALIGNED_SAME | {EXISTING_CANDIDATE}:
        assert by_id[cid]["decision"] == "same" and by_id[cid]["ku_id"] == KU_ID
    assert candidate_by_id[MAIN_CANDIDATE]["index_entry_id"] == "A.csv#24"
    for cid, (index_entry, subentry, pages, _) in TARGETS.items():
        candidate = candidate_by_id[cid]
        alignment = by_id[cid]
        assert candidate["suggested_type"] == "person"
        assert candidate["canonical_name"] == HEADWORD
        assert candidate["index_source_file"] == "A.csv"
        assert candidate["index_entry_id"] == index_entry
        assert candidate["sub_entry"] == subentry
        assert candidate["index_page_range"] == pages
        assert alignment["decision"] == "undecided" and not alignment.get("ku_id")
        assert "index-seeded candidate has no mapped S2 mention" in alignment["resolution_note"]

    with INDEX_PATH.open(encoding="cp1252", newline="") as stream:
        index_rows = list(csv.DictReader(stream))
    for _, (index_entry, subentry, pages, _) in TARGETS.items():
        row_number = int(index_entry.split("#")[1])
        row = index_rows[row_number]
        assert row["Main Entry"] == HEADWORD
        assert row["Sub-entry"] == subentry
        assert row["Page Numbers"] == pages

    source = SOURCE_PATH.read_text(encoding="utf-8-sig")
    for evidence in (
        "Three publishers stand out above all the others for the enterprise and quality of their patronage—Giambattista Albrizzi",
        "one of his most popular books was a guide to Venice II Forestiere Illuminate",
        "In 1736 he began to bring out a complete edition in French of the works of Bossuet",
        "Albrizzi’s Bossuet a series of vignettes and illustrations",
        "Dactyliotheca Ant. M. Zanetti, for which Albrizzi was, after some hesitation, again chosen as publisher",
    ):
        assert evidence in source, f"book evidence marker missing: {evidence}"
    plate_list = FRONT_MATTER_PATH.read_text(encoding="utf-8-sig")
    assert "published by Albrizzi 1745, with portraits of Piazzetta and Albrizzi" in plate_list

    card_bytes = CARD_PATH.read_bytes()
    card_encoding = "utf-8-sig" if card_bytes.startswith(b"\xef\xbb\xbf") else "utf-8"
    card_text = card_bytes.decode(card_encoding)
    for form in ("Giovanni Battista Albrizzi", "Giambatista Albrizzi"):
        assert form in card_text
    assert "https://www.treccani.it/enciclopedia/giovanni-battista-albrizzi_" in card_text

    planned = [dict(row) for row in alignments]
    planned_by_id = decision_rows(planned)
    for cid, (index_entry, subentry, pages, printed_pages) in TARGETS.items():
        row = planned_by_id[cid]
        row["decision"] = "same"
        row["ku_id"] = KU_ID
        row["process_ref"] = f"{TASK}#{ANCHOR}"
        row["resolution_note"] += (
            f" S3复核（{DATE}）：原undecided理由保留为历史；{index_entry}在A.csv中与主项"
            f"“{HEADWORD}”同列，person型子目为“{subentry}”，书内页码{printed_pages}（索引记{pages}）。"
            "第13章p.334直接以Giambattista Albrizzi全名介绍威尼斯出版者；同页记其出版《Il Forestiere Illuminato》指南，"
            "并称他于1736年开始刊行Bossuet法文版；p.335明确写作Albrizzi's Bossuet；p.344记Zanetti宝石目录再次选Albrizzi为出版者。"
            "Treccani《意大利传记辞典》以Giovanni Battista Albrizzi为题，记其出版者身份与Bossuet作品（1736–1757）、"
            "Il Forestiero illuminato、Gemme antiche di A. M. Zanetti（1750），并明确区分同名侄辈（1798–1806）；"
            "这些18世纪中叶出版活动因此归于本卡所指的长辈。"
            "既有人物KU units/persons/albrizzi采用Giovanni Battista姓名并记录出版署名Giambatista；"
            f"主项候选{MAIN_CANDIDATE}及已登记同组候选cand-0027、cand-0029、章前候选{EXISTING_CANDIDATE}均已映射该KU。"
            f"该子目所标为同一出版者，故改判same → {KU_ID}。Haskell约生于1699年的记载与既有卡精确日期1698-12-29的差异继续保留为来源核对项；"
            "本次不新增关系或扩展书内断言。"
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
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Albrizzi人物索引子目复用既有人物KU（{DATE}）\n\n"
        "- cand-0026（A.csv#25，edition of works of Bossuet，pp.334–335）、cand-0028（A.csv#27，Il Forestiere Illuminato，p.334）及"
        "cand-0030（A.csv#29，publication of gems in A. M. Zanetti's collection，pp.337、344）均由undecided改判same → "
        f"[{KU_ID}](../../../04-knowledge/{KU_ID}.md)。A.csv三项都是同一Giambattista Albrizzi人物主项下的person型子目。"
        "第13章p.334以该全名介绍威尼斯出版者，并在pp.334–335记Bossuet法文版、指南及其与Piazzetta的出版合作；"
        "p.344又明确称Albrizzi为Zanetti宝石目录出版者。Treccani《意大利传记辞典》以Giovanni Battista Albrizzi为题，"
        "记其出版Bossuet作品（1736–1757）、Il Forestiero illuminato、Gemme antiche di A. M. Zanetti（1750），"
        "并区分同名侄辈（1798–1806）；[Treccani DBI](https://www.treccani.it/enciclopedia/giovanni-battista-albrizzi_%28Dizionario-Biografico%29/)；"
        "既有人物KU的Giovanni Battista及Giambatista姓名形式、1745年图版出版证据与此相合。\n"
        "- 边界：Bossuet版、威尼斯指南及Zanetti宝石目录仍为独立archive/work对象，不因person型索引子目合并入人物卡；"
        "不据索引关系新增人物—作品正式关系。Haskell约生于1699年与既有外部来源精确日期1698-12-29的差异仍作为来源核对项保留。\n"
        f"- 更新后S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，undecided={sync.fmt(totals['undecided'])}；"
        f"S4待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )

    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text += (
        f"\n\n### S3 person：Albrizzi人物索引子目身份归组（{DATE}）\n\n"
        "三个描述Bossuet版、威尼斯指南及Zanetti宝石目录的person型索引子目现映射至既有Giovanni Battista Albrizzi人物KU；"
        "出版物对象、身份外的事实与正式关系仍各守其证据状态。详情见"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})及alignment.csv。"
    )

    identity_section = (
        "### 身份与书内索引\n\n"
        "中文：第13章及人物索引中的全名形式Giambattista Albrizzi、既有人物卡所记录的Giovanni Battista Albrizzi和出版署名Giambatista Albrizzi，"
        "均指向本卡所记威尼斯出版者。A.csv人物主项cand-0025及其Bossuet版、威尼斯指南和Zanetti宝石目录三个person型子目"
        "（cand-0026、cand-0028、cand-0030）现统一映射至本卡；出版物仍是独立对象。Treccani传记条目区分其同名侄辈。"
        "Haskell约生于1699年与既有来源所记精确日期1698-12-29的差异保留为来源核对项。\n\n"
        "English: The Chapter 13 and person-index form Giambattista Albrizzi, the existing card's Giovanni Battista Albrizzi, "
        "and the publication signature Giambatista Albrizzi refer to the Venetian publisher recorded here. The A.csv person "
        "headword cand-0025 and its three person-type subentries for the Bossuet edition, the Venice guide, and Zanetti's gem "
        "catalogue (cand-0026, cand-0028, cand-0030) now map to this card; the publications remain separate objects. Treccani's "
        "biographical entry distinguishes his nephew of the same name. The difference between Haskell's approximate birth year "
        "1699 and the existing source's exact date 1698-12-29 remains a source-check item.\n\n"
    )
    assert "### 身份与书内索引\n" not in card_text
    assert card_text.count("## 关系与证据\n") == 1
    assert "updated: '2026-09-14'" in card_text
    card_text = card_text.replace("## 关系与证据\n", identity_section + "## 关系与证据\n", 1)
    card_text = card_text.replace("updated: '2026-09-14'", f"updated: '{DATE}'", 1)

    if args.dry_run:
        print(
            f"dry-run passed: same additions={len(TARGETS)}->{KU_ID}; "
            f"same={totals['same_candidates']}/{totals['same_kus']}; undecided={totals['undecided']}; "
            f"new_groups={totals['new_groups']}; pending={totals['pending_groups']}/{totals['pending_members']}; "
            "existing_albrizzi_decisions=4; manifest_unchanged; relations_added=0"
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
