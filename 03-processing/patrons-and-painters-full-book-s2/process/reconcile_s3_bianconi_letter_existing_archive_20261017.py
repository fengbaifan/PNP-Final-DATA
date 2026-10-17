from __future__ import annotations

import argparse
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"

CANDIDATE_ID = "cand-3554"
GROUP = "archive-group-d0f04ae9d515"
KU_ID = "units/archives/bianconi-letter-1762"
CARD_REL = "04-knowledge/units/archives/bianconi-letter-1762.md"
SOURCE_REF = "chp-1:01_CHP-1_sec_ii:l168-239#L896"
STATEMENT_ID = "st-chp1-secii-p21-n2-cites-bianconi-letter"
ANCHOR = "s3-existing-bianconi-letter-1762-reuse-20261017"


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the Haskell Bianconi letter candidate to its existing archive KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE_ID)
    alignment = next(
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE_ID and not row.get("external_source")
    )
    assert candidate.get("suggested_type") == "archive"
    assert candidate.get("canonical_name") == "Letter from G. L. Bianconi (1762)"
    assert candidate.get("candidate_source_ref") == SOURCE_REF
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP

    manifest = sync.read_csv(ROOT / "04-knowledge" / "tables" / "ku-manifest.csv")[1]
    target_manifest = [row for row in manifest if row.get("ku_id") == KU_ID]
    assert len(target_manifest) == 1 and target_manifest[0].get("card_path") == CARD_REL
    assert target_manifest[0].get("type") == "archive"
    card = (ROOT / CARD_REL).read_text(encoding="utf-8-sig")
    assert "Letter from Giovanni Ludovico Bianconi to Marchese Filippo Hercolani (1762-11-22)" in card
    assert "Bottari, VII, p. 362" in card

    source_full = (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md").read_text(encoding="utf-8-sig")
    source_section = (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md").read_text(encoding="utf-8-sig")
    assert "letter from G. L. Bianconi of22 November 1762" in source_full
    assert "letter from G. L. Bianconi of22 November 1762" in source_section
    statements = sync.load_statements()
    direct_relations = {
        row["statement_id"] for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert direct_relations == {STATEMENT_ID}, direct_relations

    if alignment.get("decision") == "same" and alignment.get("ku_id") == KU_ID:
        print(f"ALREADY ALIGNED: {CANDIDATE_ID} -> {KU_ID}; 1 source-defined citation candidate unchanged.")
        return 0
    assert alignment.get("decision") == "new" and not alignment.get("ku_id"), alignment

    rationale = (
        f"source_ref=candidate_ref={SOURCE_REF}; statement={STATEMENT_ID}; group={GROUP}; "
        f"S3 reuse adjudication: same -> {KU_ID}. Haskell's Chapter 1 note identifies G. L. Bianconi's "
        "letter of 22 November 1762 and locates the quotation at Bottari, volume VII, p. 362; the existing "
        "archive card records the same author, exact date, and Bottari locator. The note's OCR joins 'of' and '22' "
        "as 'of22'; this does not alter the date. Internal comparison only; no further letter content is inferred."
    )
    planned_alignment = [dict(row) for row in alignments]
    target = next(
        row for row in planned_alignment
        if row.get("candidate_id") == CANDIDATE_ID and not row.get("external_source")
    )
    target["decision"] = "same"
    target["ku_id"] = KU_ID
    target["resolution_note"] = rationale
    target["process_ref"] = f"S3-full-book-2026-10-17#{ANCHOR}"

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S3 archive：G. L. Bianconi 1762年书信复用裁决（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（{SOURCE_REF}）由`new`改判`same`，映射到既有[{KU_ID}](../../../{CARD_REL})。"
        "Haskell第1章 p.21 注2给出Bianconi、1762年11月22日及Bottari卷VII第362页；既有卡记录同一作者、日期和刊本定位。"
        "OCR将`of 22`连写为`of22`；日期本身清楚。只确认文献身份，不把Haskell摘引扩成独立内容核验。"
        "1条直接书目关系候选保留待S6。\n\n"
        f"当前 S3：same={sync.fmt(totals['same_candidates'])}候选/{sync.fmt(totals['same_kus'])} KU；"
        f"new={sync.fmt(totals['new_candidates'])}候选/{sync.fmt(totals['new_groups'])}组；"
        f"conflict={sync.fmt(totals['conflict'])}；excluded={sync.fmt(totals['excluded'])}；"
        f"undecided={sync.fmt(totals['undecided'])}。S4已登记{sync.fmt(totals['registered_groups'])}组，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )
    result_text += (
        "\n\n### S3 archive：Bianconi 1762年书信复用（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`已从`new`改判`same`，映射至既有[书信卡](../units/archives/bianconi-letter-1762.md)。"
        "Haskell注2与卡片在作者、1762年11月22日和Bottari卷VII第362页上相合；未新增KU。"
        f"详情见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    if args.dry_run:
        print(f"S3 reuse dry-run passed: {CANDIDATE_ID} new -> same -> {KU_ID}")
        print(f"relation_candidates={len(direct_relations)}; new_groups={totals['new_groups']:,}; same_candidates={totals['same_candidates']:,}")
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE_ID} -> same -> {KU_ID}; relation_candidates=1 unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
