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

CANDIDATE_ID = "cand-3551"
GROUP = "archive-group-11eac9bc3f82"
KU_ID = "units/archives/rosa-ruffo-letter-1666"
CARD_REL = "04-knowledge/units/archives/rosa-ruffo-letter-1666.md"
SOURCE_REF = "chp-1:01_CHP-1_sec_ii:l155-159#L944"
STATEMENT_IDS = {
    "st-chp1-secii-p22-n1-cites-rosa-letter",
    "st-chp1-secii-p22-n1-letter-authored-by-rosa",
    "st-chp1-secii-p22-n1-letter-addressed-to-ruffo",
}
ANCHOR = "s3-existing-rosa-ruffo-letter-1666-reuse-20261017"


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the full-book Rosa-Ruffo letter candidate to its existing archive KU.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = sync.read_csv(ALIGNMENT_PATH)
    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    candidate = next(row for row in candidates if row["candidate_id"] == CANDIDATE_ID)
    targets = [
        row for row in alignments
        if row.get("candidate_id") == CANDIDATE_ID and not row.get("external_source")
    ]
    assert len(targets) == 1
    alignment = targets[0]
    assert candidate.get("suggested_type") == "archive"
    assert candidate.get("canonical_name") == "Letter from Salvator Rosa to Don Antonio Ruffo (1666)"
    assert candidate.get("candidate_source_ref") == SOURCE_REF
    assert alignment.get("resolution_note", "").find(f"group={GROUP}") >= 0

    manifest_fields, manifest = sync.read_csv(ROOT / "04-knowledge" / "tables" / "ku-manifest.csv")
    target_manifest = [row for row in manifest if row.get("ku_id") == KU_ID]
    assert len(target_manifest) == 1
    assert target_manifest[0].get("type") == "archive"
    assert target_manifest[0].get("card_path") == CARD_REL
    card_path = ROOT / CARD_REL
    assert card_path.exists()
    card = card_path.read_text(encoding="utf-8-sig")
    assert "Letter from Salvator Rosa to Antonio Ruffo (1666-04-01)" in card
    assert "dated I April 1666" in card
    assert "Don Antonio Ruffo" in card

    source_path = ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md"
    source = source_path.read_text(encoding="utf-8-sig")
    assert "See the letter from Salvator Rosa to Don Antonio Ruffo, dated I April 1666" in source

    statements = sync.load_statements()
    actual_statements = {
        row["statement_id"]
        for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual_statements == STATEMENT_IDS, actual_statements

    if alignment.get("decision") == "same" and alignment.get("ku_id") == KU_ID:
        print(f"ALREADY ALIGNED: {CANDIDATE_ID} -> {KU_ID}; 3 source-defined relation candidates unchanged.")
        return 0
    assert alignment.get("decision") == "new" and not alignment.get("ku_id"), alignment

    rationale = (
        f"source_ref=candidate_ref={SOURCE_REF}; statements={','.join(sorted(STATEMENT_IDS))}; group={GROUP}; "
        f"S3 reuse adjudication: same -> {KU_ID}. The candidate's Chapter 1 note 1 names Salvator Rosa, "
        "Don Antonio Ruffo, and a letter dated 1 April 1666; the existing archive card records the same "
        "correspondence, date, and book location (print p. 22, note 1). The source statement records the OCR "
        "form 'I April'; the printed page is read as '1 April', a transcription variation rather than a second "
        "letter. This is an internal comparison of the cited source and existing card; no external source was accessed."
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
        "### S3 archive：Salvator Rosa 致 Don Antonio Ruffo 书信复用裁决（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（{SOURCE_REF}）由原先的单候选 `new` 身份组改判 `same`，映射到既有"
        f"[{KU_ID}](../../../{CARD_REL})。原书第1章 p.22 注1给出通信双方及1666-04-01日期；既有档案卡记录同一书内注释、"
        "同一日期、寄件人与收件人。S2句子转录的罗马数字`I`与印本所读阿拉伯数字`1`是转录差异，不构成第二封信。"
        "比较仅依据本书及现有卡片；未访问外部来源。\n\n"
        "该候选的3条书内关系候选保留原ID，未在本轮重建或增写正式关系。此裁决不改变原刊本归属问题，也不把原信或刊本说成已独立查阅。\n\n"
        f"当前 S3：same={sync.fmt(totals['same_candidates'])} 候选/{sync.fmt(totals['same_kus'])} KU；"
        f"new={sync.fmt(totals['new_candidates'])} 候选/{sync.fmt(totals['new_groups'])} 组；"
        f"conflict={sync.fmt(totals['conflict'])}；excluded={sync.fmt(totals['excluded'])}；"
        f"undecided={sync.fmt(totals['undecided'])}。S4 已登记{sync.fmt(totals['registered_groups'])}组，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )
    result_text += (
        "\n\n### S3 archive：Rosa–Ruffo 1666年书信复用（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}` 已从 `new` 改判 `same`，映射至既有[书信卡](../units/archives/rosa-ruffo-letter-1666.md)。"
        "第1章 p.22 注1所载寄件人、收件人和1666年4月1日日期与卡片相合；OCR `I April` 与印本 `1 April` 为转录差异。"
        "原书3条关系候选仍保留，未新增正式关系或KU。详情见[过程记录](../../03-processing/"
        f"{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    if args.dry_run:
        print(f"S3 reuse dry-run passed: {CANDIDATE_ID} new -> same -> {KU_ID}")
        print(f"relation_candidates={len(actual_statements)}; new_groups={totals['new_groups']:,}; same_candidates={totals['same_candidates']:,}")
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE_ID} -> same -> {KU_ID}; relation_candidates={len(actual_statements)} unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
