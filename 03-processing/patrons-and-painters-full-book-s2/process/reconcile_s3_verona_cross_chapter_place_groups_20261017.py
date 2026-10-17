from __future__ import annotations

import argparse
import re
from pathlib import Path

import register_s4_archive_memmo_query_sheet_20261017 as process_sync

sync = process_sync.sync
ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
REGIONAL_CANDIDATE = "cand-7661"
EXPLICIT_CANDIDATE = "cand-8681"
OLD_GROUP = "sg3-place-cand-7661"
TARGET_GROUP = "sg3-place-cand-8681"
SOURCE_REGIONAL = "02-sources/02-Markdown/08_CHP-8_sec_ii.md"
SOURCE_EXPLICIT = "02-sources/02-Markdown/09_CHP-9_sec_ii.md"
QUOTE_REGIONAL = "Veronese Brusasorci"
QUOTE_EXPLICIT = "Of Cignaroli in Verona it was claimed"
PROCESS_ANCHOR = "s3-verona-cross-chapter-place-merge-20261017"
RESULT_MARKER = "S3 place：Verona 跨章身份组合"


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge the S3 source-local Verona place groups across chapters")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert REGIONAL_CANDIDATE in candidate_by_id and EXPLICIT_CANDIDATE in candidate_by_id
    for cid in (REGIONAL_CANDIDATE, EXPLICIT_CANDIDATE):
        assert candidate_by_id[cid].get("suggested_type") == "place"
        row = alignment_by_id[cid]
        assert row.get("decision") == "new" and not row.get("ku_id")
    regional_row = alignment_by_id[REGIONAL_CANDIDATE]
    explicit_row = alignment_by_id[EXPLICIT_CANDIDATE]
    regional_group = group_of(regional_row.get("resolution_note", ""))
    explicit_group = group_of(explicit_row.get("resolution_note", ""))
    assert regional_group in {OLD_GROUP, TARGET_GROUP}
    assert explicit_group == TARGET_GROUP
    target_members = {
        cid for cid, row in alignment_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == TARGET_GROUP
    }
    if regional_group == OLD_GROUP:
        assert target_members == {EXPLICIT_CANDIDATE}
    else:
        assert target_members == {REGIONAL_CANDIDATE, EXPLICIT_CANDIDATE}
    assert not any(
        row.get("type") == "place"
        and any(row.get(key, "").strip().casefold() == "verona" for key in ("canonical_name", "name_en"))
        for row in manifest
    ), "possible existing Verona place KU"

    for relative, quote in ((SOURCE_REGIONAL, QUOTE_REGIONAL), (SOURCE_EXPLICIT, QUOTE_EXPLICIT)):
        source = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert normalized(quote) in normalized(source), relative

    statement_lines = (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    statement_by_id = {}
    for line in statement_lines:
        if line.strip():
            import json
            statement = json.loads(line)
            statement_by_id[statement["statement_id"]] = statement
    regional_statement = statement_by_id["st-chp8-p216-brusasorci-described-as-veronese"]
    regional_context = statement_by_id["st-chp8-p216-padre-massimo-massacre-commission"]
    explicit_statement = statement_by_id["st-chp9-p268-cignaroli-saints-claim"]
    travel_statement = statement_by_id["st-chp14-p348-travel-verona"]
    assert regional_statement.get("object_candidate_id") == REGIONAL_CANDIDATE
    assert regional_statement.get("predicate") == "described_as_veronese"
    assert REGIONAL_CANDIDATE in regional_context.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    assert "linked to Verona" in regional_context.get("qualifiers", {}).get("qualification", "")
    assert EXPLICIT_CANDIDATE in explicit_statement.get("qualifiers", {}).get("mentioned_candidate_ids", [])
    assert travel_statement.get("object_candidate_id") == REGIONAL_CANDIDATE

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    if regional_group == OLD_GROUP:
        old_note = planned_by_id[REGIONAL_CANDIDATE]["resolution_note"]
        planned_by_id[REGIONAL_CANDIDATE]["resolution_note"] = re.sub(
            rf"group={re.escape(OLD_GROUP)}(?=[;| ])",
            f"group={TARGET_GROUP}",
            old_note,
            count=1,
        )
        planned_by_id[REGIONAL_CANDIDATE]["resolution_note"] += (
            f" S3 identity reconciliation {DATE}: same geographic city as {EXPLICIT_CANDIDATE}; "
            "the p.216 regional adjective ‘Veronese’ is explicitly linked to Verona in the S2 qualification, "
            "and the p.268 passage names Cignaroli in Verona. Additional Verona locators occur on pp.297, 311, 327, and 348. "
            f"Merge into {TARGET_GROUP}; preserve prior_group={OLD_GROUP}; do not infer residence or political/institutional identity."
        )
        planned_by_id[EXPLICIT_CANDIDATE]["resolution_note"] += (
            f" S3 identity reconciliation {DATE}: identity peer={REGIONAL_CANDIDATE}; "
            "the regional Verona candidate at p.216 and explicit city name at p.268 identify the same city; "
            "p.348 also names Verona as an itinerary destination. Both candidates remain new members of this one place group."
        )
    else:
        assert f"prior_group={OLD_GROUP}" in planned_by_id[REGIONAL_CANDIDATE]["resolution_note"]
        assert f"identity peer={REGIONAL_CANDIDATE}" in planned_by_id[EXPLICIT_CANDIDATE]["resolution_note"]

    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    planned_candidate_by_id[REGIONAL_CANDIDATE]["detail"] = (
        "Verona as geographic origin/context: p.216 calls Brusasorci ‘Veronese’ (the linked S2 statement records this as a regional adjective), "
        "and the p.268 source explicitly says ‘Cignaroli in Verona’. S3 groups this with cand-8681, which anchors additional city mentions at pp.297, 311, 327, and 348. "
        "No residence, political-entity, or institutional claim is inferred."
    )
    planned_candidate_by_id[EXPLICIT_CANDIDATE]["detail"] = (
        "Geographic city Verona explicitly named at p.268 in the Cignaroli passage; grouped in S3 with cand-7661, "
        "whose p.216 regional adjective and p.348 route anchor the same city. Other explicit Verona uses occur at pp.297, 311, and 327. "
        "No residence, political-entity, or institutional claim is inferred."
    )

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    summary_pattern = r"(4,972 条 new 候选组成 )[\d,]+( 个类型内身份组)"
    next_process, count = re.subn(
        summary_pattern,
        rf"\g<1>{sync.fmt(totals['new_groups'])}\g<2>",
        next_process,
        count=1,
    )
    assert count == 1, "could not refresh the S3 new-group summary"
    if f'<a id="{PROCESS_ANCHOR}"></a>' not in next_process:
        next_process += (
            f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
            "### S3 place：Verona 跨章身份组并合（2026-10-17）\n\n"
            f"- cand-7661 原属 {OLD_GROUP}，cand-8681 原属 {TARGET_GROUP}；两者保持 S3 new，现归入 {TARGET_GROUP} 一个 place 身份组，两个候选在 S4 共用一个 KU。旧组号和裁决理由保留在 alignment 注释。\n"
            "- 语义依据：第8章 p.216 将 Brusasorci 称为 “Veronese”，对应 statement 的限定明确将地域形容词连到 Verona；第9章 p.268 明称 “Cignaroli in Verona”。此外，S2 已用 cand-8681 记录 p.297 Rotari 的 native Verona、p.311 Schulenburg 在 Verona 的叙述及 p.327 书籍在 Verona 出版；第14章 p.348 也将 Verona 列入行程。以上是同一城市的地名/地域来源用法，不表示所有人物曾居住于此。\n"
            "- 未把 Verona 与政治实体或机构合并；cand-8681 的相关作品与人物关系仍按各自 S2 资格状态处理。本次不增加或删除候选、提及、statement。\n"
            f"\nS3 new 候选{sync.fmt(totals['new_candidates'])}，身份组{sync.fmt(totals['new_groups'])}；"
            f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
            f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
        )
    if RESULT_MARKER not in next_result:
        next_result += (
            f"\n\n### {RESULT_MARKER}（2026-10-17）\n\n"
            f"cand-7661（p.216 regional adjective）与 cand-8681（p.268 explicit Verona）现同属 {TARGET_GROUP}，"
            "并由 p.297、311、327、348 的同一城市用法补强跨章映射。两候选仍保持 new；S4 应登记一个 Verona place KU。"
        )

    if args.dry_run:
        print(f"S3 dry-run passed: {REGIONAL_CANDIDATE}+{EXPLICIT_CANDIDATE} -> {TARGET_GROUP}")
        print(f"new groups={totals['new_groups']}; S4 pending={totals['pending_groups']}/{totals['pending_members']}")
        print("candidate, mention and statement counts unchanged; no files changed")
        return 0

    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "entity-candidates.csv", candidate_fields, planned_candidates)
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(f"applied: {REGIONAL_CANDIDATE}+{EXPLICIT_CANDIDATE} -> {TARGET_GROUP}; new groups={totals['new_groups']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
