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

CANDIDATE_ID = "cand-3553"
GROUP = "archive-group-4cf03a73377f"
KU_ID = "units/archives/negri-san-tommaso-letter-1676"
CARD_REL = "04-knowledge/units/archives/negri-san-tommaso-letter-1676.md"
SOURCE_REF = "chp-1:01_CHP-1_sec_ii:l168-239#L899"
STATEMENT_IDS = {
    "st-chp1-secii-p21-n3-cites-negri-letter",
    "st-chp1-secii-p21-n3-letter-authored-by-negri",
    "st-chp1-secii-p21-n3-letter-addressed-to-marchese",
}
ANCHOR = "s3-existing-negri-san-tommaso-letter-1676-reuse-20261017"


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve the full-book Negri letter candidate to its existing archive KU.")
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
    assert candidate.get("canonical_name") == "Letter from Paolo Negri to Marchese di S. Tommaso (1676)"
    assert candidate.get("candidate_source_ref") == SOURCE_REF
    assert sync.get_group(alignment.get("resolution_note", "")) == GROUP

    manifest = sync.read_csv(ROOT / "04-knowledge" / "tables" / "ku-manifest.csv")[1]
    target_manifest = [row for row in manifest if row.get("ku_id") == KU_ID]
    assert len(target_manifest) == 1
    assert target_manifest[0].get("type") == "archive"
    assert target_manifest[0].get("card_path") == CARD_REL
    card = (ROOT / CARD_REL).read_text(encoding="utf-8-sig")
    assert "Letter from Paolo Negri to the Marquis of S. Tommaso (1676-12-24)" in card
    assert "dated 24 December 1676" in card
    assert "Marchese di S. Tommaso" in card
    assert "Claretta" in card and "1885" in card

    source_full = (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1.md").read_text(encoding="utf-8-sig")
    source_section = (ROOT / "02-sources" / "02-Markdown" / "01_CHP-1_sec_ii.md").read_text(encoding="utf-8-sig")
    assert "Letter from Paolo Negri to Marchese di S. Tommaso, dated 24 December 1676" in source_full
    assert "Letter from Paolo Negri to Marchese di S. Tommaso, dated 24 December 1676" in source_section

    statements = sync.load_statements()
    actual = {
        row["statement_id"]
        for row in statements
        if (row.get("subject_candidate_id") == CANDIDATE_ID or row.get("object_candidate_id") == CANDIDATE_ID)
        and (row.get("qualifiers") or {}).get("relation_candidate") is True
    }
    assert actual == STATEMENT_IDS, actual

    if alignment.get("decision") == "same" and alignment.get("ku_id") == KU_ID:
        print(f"ALREADY ALIGNED: {CANDIDATE_ID} -> {KU_ID}; 3 source-defined relation candidates unchanged.")
        return 0
    assert alignment.get("decision") == "new" and not alignment.get("ku_id"), alignment

    rationale = (
        f"source_ref=candidate_ref={SOURCE_REF}; statements={','.join(sorted(STATEMENT_IDS))}; group={GROUP}; "
        f"S3 reuse adjudication: same -> {KU_ID}. The source note identifies Paolo Negri's letter to the Marchese di S. Tommaso "
        "as dated 24 December 1676 and quoted by Claretta (1885, p. 542). The existing archive KU records the same "
        "sender, recipient, exact date, and Claretta citation from the same Chapter 1 note. Internal comparison of the "
        "source transcription and existing card; no external identity or manuscript claim is added."
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

    _, manifest_rows = sync.read_csv(ROOT / "04-knowledge" / "tables" / "ku-manifest.csv")
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    result_text = sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest_rows)
    )
    process_text = PROCESS_PATH.read_text(encoding="utf-8-sig")
    process_text += (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        "### S3 archive：Paolo Negri 致 Marchese di S. Tommaso 书信复用裁决（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`（{SOURCE_REF}）由单候选`new`组改判`same`，映射到既有"
        f"[{KU_ID}](../../../{CARD_REL})。原书第1章 p.21 注3明确给出同一寄件人、收件人、1676年12月24日日期及Claretta 1885 p.542刊引信息；"
        "既有卡片正以同一注释和同一日期标识该信。内部来源与卡片比对足以确认同一书信；不新增外部身份或原件主张。\n\n"
        "3条S2关系候选保留原ID，未新增正式关系。\n\n"
        f"当前 S3：same={sync.fmt(totals['same_candidates'])}候选/{sync.fmt(totals['same_kus'])} KU；"
        f"new={sync.fmt(totals['new_candidates'])}候选/{sync.fmt(totals['new_groups'])}组；"
        f"conflict={sync.fmt(totals['conflict'])}；excluded={sync.fmt(totals['excluded'])}；"
        f"undecided={sync.fmt(totals['undecided'])}。S4已登记{sync.fmt(totals['registered_groups'])}组，"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条候选映射。"
    )
    result_text += (
        "\n\n### S3 archive：Negri–Marchese di S. Tommaso 1676年书信复用（2026-10-17）\n\n"
        f"`{CANDIDATE_ID}`已从`new`改判`same`，映射至既有[书信卡](../units/archives/negri-san-tommaso-letter-1676.md)。"
        "原书注3与卡片在寄件人、收件人、1676年12月24日及Claretta刊引上相合；未新增KU或关系。"
        f"详情见[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    if args.dry_run:
        print(f"S3 reuse dry-run passed: {CANDIDATE_ID} new -> same -> {KU_ID}")
        print(f"relation_candidates={len(actual)}; new_groups={totals['new_groups']:,}; same_candidates={totals['same_candidates']:,}")
        print("no files changed")
        return 0

    sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(f"applied: {CANDIDATE_ID} -> same -> {KU_ID}; relation_candidates={len(actual)} unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
