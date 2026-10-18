from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402
import register_s4_archive_memmo_query_sheet_20261017 as process_sync  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT = TABLES / "alignment.csv"
ENTITY = TABLES / "entity-candidates.csv"
MANIFEST = TABLES / "ku-manifest.csv"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
CARD = ROOT / "04-knowledge" / "units" / "persons" / "charles-de-brosses.md"
DATE = "2026-10-18"
CANDIDATE = "cand-9436"
INDEX_CANDIDATE = "cand-0455"
EXISTING_KU = "units/persons/charles-de-brosses"
OLD_GROUP = "new-person:brosses-charles-de-443ef2c49c"
INDEX_GROUP = "new-person:brosses-charles-de-president-73d472266d"
SAME_GROUP = "sg3-ku-units-persons-charles-de-brosses"
ANCHOR = "s3-brosses-cross-chapter-person-reuse-20261018"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align the Chapter 10 Charles de Brosses person candidate to the indexed cross-chapter KU."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT)
    _, candidates = sync.read_csv(ENTITY)
    _, manifest = sync.read_csv(MANIFEST)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    manifest_by_id = {row["ku_id"]: row for row in manifest}
    candidate = candidate_by_id[CANDIDATE]
    index_candidate = candidate_by_id[INDEX_CANDIDATE]
    decisions = [row for row in alignments if row.get("candidate_id") and not row.get("external_source")]
    target_rows = [row for row in decisions if row.get("candidate_id") == CANDIDATE]
    index_rows = [row for row in decisions if row.get("candidate_id") == INDEX_CANDIDATE]

    assert candidate["suggested_type"] == "person"
    assert candidate["candidate_origin"] == "body-mention"
    assert candidate["candidate_source_ref"] == "chp-10:10_CHP-10_intro:l491-634#L554"
    assert candidate["canonical_name"] == "Charles de Brosses (author named in p.292 note 1)"
    assert index_candidate["suggested_type"] == "person"
    assert index_candidate["index_entry_id"] == "B.csv#302"
    assert index_candidate["canonical_name"] == "Brosses, Président Charles De"
    assert index_candidate["index_page_range"] == "245, 260, 311n"
    assert len(target_rows) == 1 and target_rows[0]["decision"] == "new"
    assert not target_rows[0].get("ku_id")
    assert sync.get_group(target_rows[0].get("resolution_note", "")) == OLD_GROUP
    assert len(index_rows) == 1 and index_rows[0]["decision"] == "new"
    assert index_rows[0].get("ku_id") == EXISTING_KU
    assert sync.get_group(index_rows[0].get("resolution_note", "")) == INDEX_GROUP
    assert manifest_by_id[EXISTING_KU]["type"] == "person"
    assert manifest_by_id[EXISTING_KU]["card_path"] == "04-knowledge/units/persons/charles-de-brosses.md"
    assert not any(row.get("candidate_id") == CANDIDATE and row.get("external_source") for row in alignments)

    archive_ids = {"cand-9437", "cand-9879", "cand-8429", "cand-8505", "cand-11268"}
    assert all(candidate_by_id[cid]["suggested_type"] == "archive" for cid in archive_ids)
    assert candidate_by_id["cand-9437"]["canonical_name"].startswith("De Brosses, Lettres d'Italie")
    assert "volume I, page 142" in candidate_by_id["cand-9879"]["canonical_name"]
    assert "volume I, page 149" in candidate_by_id["cand-8429"]["canonical_name"]
    assert "volume II, page 39" in candidate_by_id["cand-8505"]["canonical_name"]

    source_ch9 = (ROOT / "02-sources/02-Markdown/09_CHP-9_intro.md").read_text(encoding="utf-8-sig")
    source_ch10 = (ROOT / "02-sources/02-Markdown/10_CHP-10_intro.md").read_text(encoding="utf-8-sig")
    source_ch10_sec2 = (ROOT / "02-sources/02-Markdown/10_CHP-10_sec_ii.md").read_text(encoding="utf-8-sig")
    source_bibliography = (ROOT / "02-sources/02-Markdown/21_CHP-21Bibliography.md").read_text(encoding="utf-8-sig")
    assert "President de Brosses found to be a man" in source_ch9
    assert "B.csv#302" in (ROOT / "02-sources/03-Index/03-2-Index-CSV/B.csv").read_text(encoding="utf-8-sig") or "311n" in index_candidate["index_page_range"]
    assert "1 De Brosses, I, p. 282." in source_ch10
    assert "De Brosses, I, p. 142" in source_ch10_sec2
    assert "Brosses, Charles de" in source_bibliography
    assert "m-chp10-p292-notes-n1-de-brosses" in target_rows[0]["resolution_note"]
    assert "m-s2-ch10-p311-312-note-0017" in target_rows[0]["resolution_note"]

    before = sync.summarize_by_type(candidates, alignments)
    planned = [dict(row) for row in alignments]
    target = next(
        row for row in planned
        if row.get("candidate_id") == CANDIDATE and not row.get("external_source")
    )
    original_note = target["resolution_note"]
    source_prefix, old_decision_tail = original_note.split("; group=", 1)
    target.update({
        "ku_id": EXISTING_KU,
        "decision": "same",
        "accessed_date": DATE,
        "process_ref": PROCESS_REF,
        "resolution_note": (
            f"{source_prefix}; matched_manifest={EXISTING_KU}; matched_candidate_ids={INDEX_CANDIDATE}; "
            f"group={SAME_GROUP}; S3 same（{DATE}）：cand-9436从new改为same并复用索引人物KU。"
            "第10章p.311注5中的De Brosses与S1索引B.csv#302明确列出的311n相合；"
            "同一候选还锚定第10章p.292注1的De Brosses，第21章书目以Charles de Brosses署名Lettres d’Italie。"
            "第9章索引候选cand-0455的称号、页码与书目全名共同支持同一人物；该映射仅处理身份。"
            "archive候选cand-9437、cand-9879、cand-8429、cand-8505及书目作品cand-11268保持各自archive粒度。"
            f"历史new决定及原组保留：group={old_decision_tail}"
        ),
    })

    after = sync.summarize_by_type(candidates, planned)
    totals = {key: sum(row[key] for row in after.values()) for key in next(iter(after.values()))}
    before_totals = {key: sum(row[key] for row in before.values()) for key in next(iter(before.values()))}
    assert totals["same_candidates"] == before_totals["same_candidates"] + 1
    assert totals["new_candidates"] == before_totals["new_candidates"] - 1
    assert totals["pending_groups"] == before_totals["pending_groups"] - 1
    assert totals["pending_members"] == before_totals["pending_members"] - 1
    assert len(manifest) == 2123

    process_text = process_sync.refresh_process_type_table(
        PROCESS.read_text(encoding="utf-8-sig"), after
    )
    future_zh = "第10章p.292与p.311的S2人物候选cand-9436在下一条S3复核中并入本KU"
    completed_zh = "第10章p.292与p.311的S2人物候选cand-9436已由下述S3复核映射至本KU"
    assert process_text.count(future_zh) == 1
    process_text = process_text.replace(future_zh, completed_zh, 1)
    old_context_zh = (
        "第9章p.245与p.260及第10章p.292、p.311均以De Brosses姓名或引文定位出现；"
        "p.311注5与索引311n相合。第10章人物候选cand-9436将在S3复核中映射到本KU；"
        "archive候选cand-9437、cand-9879及书目作品cand-11268保持分开。"
        "引文均经Haskell转引，De Brosses原书页未独立查阅。"
    )
    new_context_zh = (
        "第9章p.245与p.260及第10章p.292、p.311均以De Brosses姓名或引文定位出现；"
        "p.311注5与索引311n相合。S3依据该索引锚点及书目署名“Brosses, Charles de”，"
        f"将第10章人物候选cand-9436映射到本KU；[裁决记录](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
        "archive候选cand-9437、cand-9879及书目作品cand-11268保持分开。"
        "引文均经Haskell转引，De Brosses原书页未独立查阅。"
    )
    old_context_en = (
        "De Brosses appears by name or citation in Chapter 9, pages 245 and 260, and Chapter 10, pages 292 and 311; "
        "the page 311 note matches index locator 311n. The Chapter 10 person candidate cand-9436 will be aligned to this KU in an S3 review; "
        "archive candidates cand-9437 and cand-9879 and the bibliographic work cand-11268 remain separate. "
        "The cited passages are mediated by Haskell, and the original De Brosses pages were not independently consulted."
    )
    new_context_en = (
        "De Brosses appears by name or citation in Chapter 9, pages 245 and 260, and Chapter 10, pages 292 and 311; "
        "the page 311 note matches index locator 311n. S3 matched the Chapter 10 person candidate cand-9436 to this KU "
        f"through that index anchor and the bibliography form “Brosses, Charles de” ([adjudication record](../../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})). "
        "Archive candidates cand-9437 and cand-9879 and the bibliographic work cand-11268 remain separate. "
        "The cited passages are mediated by Haskell, and the original De Brosses pages were not independently consulted."
    )
    assert process_text.count(old_context_zh) == 1
    process_text = process_text.replace(old_context_zh, new_context_zh, 1)
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3 person：de Brosses跨章人物身份复用（{DATE}）\n\n"
        f"cand-9436由new改为same，映射到已登记的[Charles de Brosses KU](../../../04-knowledge/units/persons/charles-de-brosses.md)（{EXISTING_KU}）。"
        "S1索引B.csv#302将该人物页码列为245、260及311n；S2 cand-9436记录第10章p.292注1与p.311注5的De Brosses称名，"
        "其中p.311注5正落在索引311n所指位置。第21章书目“Brosses, Charles de”提供同书作者全名。"
        "这些书内索引、正文／脚注与书目锚点支持同一人物；不要求原引文页已独立阅读，也不把书目或引文定位对象合并到人物。"
        "cand-9437、cand-9879、cand-8429与cand-8505仍是各自的archive引文定位候选；cand-11268是两卷本书目对象。"
        "保留原new组与原S3理由作为历史记录；本次没有新增外部身份来源、字段事实、正式关系或S6裁决。"
    )

    card_text = CARD.read_text(encoding="utf-8-sig")
    assert card_text.count(old_context_zh) == 1
    assert card_text.count(old_context_en) == 1
    card_text = card_text.replace(old_context_zh, new_context_zh, 1)
    card_text = card_text.replace(old_context_en, new_context_en, 1)

    result_text = sync.update_result(
        RESULT.read_text(encoding="utf-8-sig"), after, totals, len(manifest)
    )
    external_total = sum(bool(row.get("external_source")) for row in planned)
    import re

    result_text, count = re.subn(
        r"^\| \[全书对齐\].*$",
        f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(len(planned))} 条："
        f"{sync.fmt(len(candidates))} 条候选决定记录及 {sync.fmt(external_total)} 条外部身份记录；候选决定数见下表 |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert count == 1
    batch_result = (
        f"### S3 person：de Brosses跨章人物身份复用（{DATE}）\n\n"
        f"cand-9436由new改为same，映射至[Charles de Brosses KU](../units/persons/charles-de-brosses.md)。"
        "第10章p.311注5与S1索引B.csv#302的311n定位相合，第21章书目提供Charles de Brosses全名；"
        "人物same裁决与书目／引文archive候选分开。"
    )
    marker = "## 未解决项与交接限制"
    assert result_text.count(marker) == 1
    result_text = result_text.replace(marker, batch_result + "\n\n" + marker, 1)

    if args.dry_run:
        print(
            f"dry-run passed: {CANDIDATE} new->same {EXISTING_KU}; matched_candidate={INDEX_CANDIDATE}; "
            f"same={before_totals['same_candidates']}->{totals['same_candidates']} "
            f"new={before_totals['new_candidates']}->{totals['new_candidates']}; "
            f"pending={before_totals['pending_groups']}/{before_totals['pending_members']}->"
            f"{totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)} unchanged"
        )
        return 0

    sync.write_csv(ALIGNMENT, alignment_fields, planned)
    PROCESS.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    CARD.write_text(card_text, encoding="utf-8", newline="\n")
    print(
        f"applied: {CANDIDATE} -> same:{EXISTING_KU}; matched_candidate={INDEX_CANDIDATE}; "
        f"same={totals['same_candidates']} new={totals['new_candidates']} "
        f"pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
