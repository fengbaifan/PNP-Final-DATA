from __future__ import annotations

import argparse
import re
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
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
MAIN = "cand-0383"
SUBENTRY = "cand-0384"
GROUP = "new-person:bombelli-sebastiano-c6f300a2fb"
ANCHOR = "s3-bombelli-index-subentry-20261017"
INDEX_PATH = "02-sources/03-Index/03-2-Index-CSV/B.csv"
BODY_PATH = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the Bombelli person index subentry to its source-backed identity group.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(ENTITY_PATH)
    _, manifest = sync.read_csv(MANIFEST_PATH)
    by_candidate = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    main_candidate = by_candidate[MAIN]
    subentry_candidate = by_candidate[SUBENTRY]
    main_alignment = decisions[MAIN]
    subentry_alignment = decisions[SUBENTRY]

    assert main_candidate["suggested_type"] == "person"
    assert main_candidate["canonical_name"] == "Bombelli Sebastiano"
    assert main_candidate["index_entry_id"] == "B.csv#230"
    assert main_alignment["decision"] == "new" and not main_alignment.get("ku_id")
    assert sync.get_group(main_alignment.get("resolution_note", "")) == GROUP
    assert subentry_candidate["suggested_type"] == "person"
    assert subentry_candidate["canonical_name"] == "Bombelli Sebastiano"
    assert subentry_candidate["index_entry_id"] == "B.csv#231"
    assert subentry_candidate["index_page_range"] == "227"
    assert subentry_candidate["sub_entry"] == "portraits of Stefano Conti and his family"
    assert subentry_alignment["decision"] == "undecided" and not subentry_alignment.get("ku_id")
    assert "no mapped S2 mention/body source_ref" in subentry_alignment.get("resolution_note", "")
    group_members = [
        row["candidate_id"] for row in alignments
        if row.get("candidate_id") and not row.get("external_source") and row.get("decision") == "new"
        and sync.get_group(row.get("resolution_note", "")) == GROUP
    ]
    assert group_members == [MAIN]
    assert not any(row.get("type") == "person" and "bombelli" in row.get("name_en", "").casefold() for row in manifest)

    index = (ROOT / INDEX_PATH).read_text(encoding="utf-8-sig")
    body = (ROOT / BODY_PATH).read_text(encoding="utf-8-sig")
    assert "Bombelli Sebastiano,,portraits of Stefano Conti and his family,,227" in index
    assert "portraits of his wife, his son and himself painted by Sebastiano Bombelli" in body
    assert "Sebastiano Bombelli, the leading portraitist in the city" in body

    planned_alignments = [dict(row) for row in alignments]
    changed = next(row for row in planned_alignments if row.get("candidate_id") == SUBENTRY and not row.get("external_source"))
    changed["decision"] = "new"
    changed["process_ref"] = f"{TASK}#{ANCHOR}"
    changed["resolution_note"] += (
        f" S3复核（{DATE}）：由 undecided 改为 new；group={GROUP}; 该索引候选是 Bombelli 人物主项下的肖像子目，"
        "页码227；第8章 p.227 正文明确说 Stefano Conti 的妻子、儿子和本人肖像由 Sebastiano Bombelli 绘制。"
        "索引主项 cand-0383 同列 p.227、278，且两处正文均出现同一全名；子目描述该画家在 p.227 的工作，不是独立人物。"
        "现与 cand-0383 共用一个 new person 身份组；此前‘没有映射 S2 提及’的待证理由保留在本行作历史记录。"
    )

    stats = sync.summarize_by_type(candidates, planned_alignments)
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert totals["same_candidates"] == 1891
    assert totals["new_candidates"] == 4968
    assert totals["new_groups"] == 4785
    assert totals["undecided"] == 5440
    assert totals["registered_groups"] == 666
    assert totals["registered_members"] == 822
    assert totals["pending_groups"] == 4119
    assert totals["pending_members"] == 4146

    process_text = process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：Sebastiano Bombelli 索引子目并入跨章人物组（{DATE}）\n\n"
        f"- {SUBENTRY}（B.csv#231）原为 undecided：索引候选无独立 S2 mention，故旧理由要求补正文锚点。第8章 p.227 正文明确说 Stefano "
        "Conti 的妻子、儿子和本人肖像由 Sebastiano Bombelli 绘制；索引子目“portraits of Stefano Conti and his family”即定位该处，"
        "不是另一个人物或作品实体。现改为 new，并入候选主项 cand-0383 的 {GROUP}。\n"
        "- 主项 cand-0383 的索引 B.csv#230 覆盖 p.227、278；第8章与第10章正文均以 Sebastiano Bombelli 指同一人物。"
        "本组可登记为一个 person KU；第10章召往 Vienna 的关系候选仍待 S6。\n"
        f"- S3 same={sync.fmt(totals['same_candidates'])}（{sync.fmt(totals['same_kus'])}个 KU），"
        f"new={sync.fmt(totals['new_candidates'])}/{sync.fmt(totals['new_groups'])}组，"
        f"undecided={sync.fmt(totals['undecided'])}；S4 已登记"
        f"{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条，待登记"
        f"{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text, count = re.subn(
        r"(当前待登记 S4 的 new 候选映射为)[\d,]+(条)",
        rf"\g<1>{sync.fmt(totals['pending_members'])}\g<2>",
        result_text,
        count=1,
    )
    assert count == 1
    result_text += (
        f"\n\n### S3 person：Sebastiano Bombelli 索引子目并组复核（{DATE}）\n\n"
        f"{SUBENTRY} 从 undecided 改为 new，并入 {GROUP}；p.227 的索引肖像子目由同页正文锚定，"
        "与 p.278 主项共同指向同一人物组。S4 登记时两条候选映射共用一个 KU。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: {SUBENTRY} undecided->new/{GROUP}; members={len(group_members)}->2; "
            f"new={totals['new_candidates']}/{totals['new_groups']}; undecided={totals['undecided']}; "
            f"pending={totals['pending_groups']}/{totals['pending_members']}"
        )
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    PROCESS_PATH.write_text(process_text + "\n", encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text + "\n", encoding="utf-8-sig", newline="\n")
    print(f"applied: {SUBENTRY} new->{GROUP}; no KU or relation written in this S3 reconciliation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
