from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import register_s4_person_endpoints_ciarpi_castello_conduitt_corelli_corradini_coypel_20261017 as base  # noqa: E402

TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
ALIGNMENT_PATH = TABLES / "alignment.csv"
ENTITY_PATH = TABLES / "entity-candidates.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-person-admiral-binchs-byng-identity-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
TARGET_GROUP = "new-person:admiral-byng-817cd89b59"
OLD_GROUP = "new-person:admiral-binchs-admiral-binchs-english-a1fee8a9dc"
IDENTITY_STATEMENT = "st-chp7-p200-n5-binchs-identified-byng"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile Haskell's explicit Binchs/Admiral Byng identity statement as an S3 person group."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = base.sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = base.sync.read_csv(ENTITY_PATH)
    _, manifest = base.sync.read_csv(MANIFEST_PATH)
    by_candidate = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert len(by_candidate) == len(candidate_by_id)
    primary = by_candidate["cand-0475"]
    source_form = by_candidate["cand-7301"]
    assert primary["decision"] == source_form["decision"] == "new"
    assert not primary.get("ku_id") and not source_form.get("ku_id")
    assert base.sync.get_group(primary["resolution_note"]) == TARGET_GROUP
    assert base.sync.get_group(source_form["resolution_note"]) == OLD_GROUP
    assert not any(
        row.get("type") == "person"
        and "byng" in f"{row.get('canonical_name', '')} {row.get('name_en', '')}".casefold()
        for row in manifest
    ), "an existing Byng person KU must be reviewed before keeping this as new"

    index_rows = base.read_index_rows("B.csv")
    index_row = index_rows[323]
    assert index_row.get("Main Entry") == "Byng, Admiral"
    assert index_row.get("Page Numbers", "") == "200n"
    source_text = (ROOT / "02-sources/02-Markdown/07_CHP-7_sec_v.md").read_text(encoding="utf-8-sig")
    assert "working for the English Admiral ‘Binchs’" in source_text
    assert "must be Admiral Byng, as from 1718 Commander of the British fleet in the Mediterranean" in source_text
    assert "back in Naples in 1719" in source_text
    assert "Footnote 5 is in a later composite source segment" in candidate_by_id["cand-7301"].get("detail", "")

    statement_lines = STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
    statements = [json.loads(line) for line in statement_lines if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    identity_statement = statement_by_id[IDENTITY_STATEMENT]
    assert identity_statement["subject_candidate_id"] == "cand-7301"
    assert identity_statement["object_candidate_id"] == "cand-0475"
    assert identity_statement["predicate"] == "author_identifies_as"
    assert identity_statement["original_quote"] == "must be Admiral Byng"
    assert (identity_statement.get("qualifiers") or {}).get("relation_candidate") is True
    assert "keep cand-7301 and cand-0475 separate" in identity_statement["qualifiers"].get("qualification", "")
    assert f'<a id="{ANCHOR}"></a>' not in PROCESS_PATH.read_text(encoding="utf-8-sig")

    planned_alignments = [dict(row) for row in alignments]
    revised_primary = next(row for row in planned_alignments if row.get("candidate_id") == "cand-0475" and not row.get("external_source"))
    revised_source_form = next(row for row in planned_alignments if row.get("candidate_id") == "cand-7301" and not row.get("external_source"))
    revised_primary["process_ref"] = PROCESS_REF
    revised_primary["resolution_note"] = (
        "source_ref=candidate=cand-0475;index_entry=B.csv#323;index_pages=200n;"
        "s2_mentions=m-chp7-p200-p202-notes-025@02-sources/02-Markdown/07_CHP-7_sec_v.md#L62-76[Admiral Byng;chars=828-840];"
        f"group={TARGET_GROUP}; S3复核（{DATE}）：索引主项为‘Byng, Admiral’，可规范显示为Admiral Byng，但未提供名字；"
        "与cand-7301归入同一new人物组，依据第7章p.200注5对正文‘Binchs’的明确识别。"
        "该身份依据是Haskell的书内推断，不是外部身份核验；S4登记为一个source-local人物KU。"
    )
    prior_source_form_note = revised_source_form["resolution_note"]
    assert f"group={OLD_GROUP};" in prior_source_form_note
    revised_source_form["process_ref"] = PROCESS_REF
    revised_source_form["resolution_note"] = (
        "source_ref=candidate=cand-7301;candidate_source_ref=chp-7:07_CHP-7_sec_v:l9-18#L13;"
        "source_file=02-sources/02-Markdown/07_CHP-7_sec_v.md#L9-18;"
        "s2_mentions=m-chp7-p200-p202-notes-022@02-sources/02-Markdown/07_CHP-7_sec_v.md#L62-76[Binchs;chars=702-708],"
        "m-chp7-p200-v-040@02-sources/02-Markdown/07_CHP-7_sec_v.md#L9-18[English Admiral ‘Binchs’;chars=1616-1640];"
        f"prior_group_id={OLD_GROUP};group={TARGET_GROUP}; S3复核（{DATE}）：保留cand-7301的来源拼写与原候选；"
        "与索引候选cand-0475归入同一new人物组，依据Haskell第7章p.200注5明言‘Binchs’ must be Admiral Byng。"
        "这是作者推断，不是外部身份核验。此前以脚注尚未迁入为由单独分组的理由已被新迁入的注5取代。"
        f" 原alignment note：{prior_source_form_note}"
    )
    assert base.sync.get_group(revised_primary["resolution_note"]) == TARGET_GROUP
    assert base.sync.get_group(revised_source_form["resolution_note"]) == TARGET_GROUP

    planned_candidates = [dict(row) for row in candidates]
    revised_candidate = next(row for row in planned_candidates if row.get("candidate_id") == "cand-7301")
    revised_candidate["detail"] = (
        "Haskell's p.200 n.5 explicitly identifies source form ‘Binchs’ as Admiral Byng. "
        "S3 groups this source-form candidate with the index candidate on that attributed identity claim; "
        "no external identity verification is implied."
    )

    planned_statement_lines = list(statement_lines)
    statement_line_indexes = [
        i for i, line in enumerate(planned_statement_lines)
        if line.strip() and json.loads(line).get("statement_id") == IDENTITY_STATEMENT
    ]
    assert len(statement_line_indexes) == 1
    identity_statement["qualifiers"]["qualification"] = (
        "S3 groups cand-7301 and cand-0475 as one source-local person based on Haskell's explicit footnote identification. "
        "The identity remains Haskell's inference, with no external verification; this is identity evidence, not a substantive graph relation."
    )
    identity_statement["qualifiers"]["relation_candidate"] = False
    identity_statement["qualifiers"]["relation_candidate_note"] = (
        "S3 uses this author-identification assertion to group the candidate names; it is not a substantive relation edge and is closed from S6 relation review."
    )
    planned_statement_lines[statement_line_indexes[0]] = json.dumps(identity_statement, ensure_ascii=False)
    planned_statements_text = "\n".join(planned_statement_lines) + "\n"

    before_stats = base.sync.summarize_by_type(candidates, alignments)
    stats = base.sync.summarize_by_type(planned_candidates, planned_alignments)
    before_totals = {key: sum(item[key] for item in before_stats.values()) for key in next(iter(before_stats.values()))}
    totals = {key: sum(item[key] for item in stats.values()) for key in next(iter(stats.values()))}
    assert stats["person"]["new_candidates"] == before_stats["person"]["new_candidates"]
    assert stats["person"]["new_groups"] == before_stats["person"]["new_groups"] - 1
    assert stats["person"]["pending_groups"] == before_stats["person"]["pending_groups"] - 1
    assert stats["person"]["pending_members"] == before_stats["person"]["pending_members"]
    assert totals["new_groups"] == before_totals["new_groups"] - 1
    assert totals["pending_groups"] == before_totals["pending_groups"] - 1
    assert totals["pending_members"] == before_totals["pending_members"]

    process_text = base.process_sync.refresh_process_type_table(
        PROCESS_PATH.read_text(encoding="utf-8-sig"), stats
    )
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n"
        f"### S3人物身份组复核：‘Binchs’与Admiral Byng（{DATE}）\n\n"
        f"`cand-0475`（B.csv#323，索引‘Byng, Admiral’，p.200n）与`cand-7301`（正文来源拼写‘English Admiral ‘Binchs’’）"
        f"均保留`new`，现归入同一身份组`{TARGET_GROUP}`。第7章p.200正文称Paolo de Matteis在那不勒斯被攻占后为English Admiral ‘Binchs’工作；"
        "该句注号5。已渲染的CHP-7.pdf物理第38页扫描确认注5明言‘Binchs’ must be Admiral Byng，并称其自1718年起为地中海英国舰队司令；"
        "同注报告‘Binchs’于1719年已回那不勒斯。直接原文依据是Haskell的书内识别，足以把这两个书内名称候选归为一个source-local人物组；"
        "它不是外部身份核验，也不补出索引未提供的名字。原来因脚注尚未迁入而将cand-7301单列的理由已被注5的现行证据取代；"
        f"旧组号保留为`prior_group_id={OLD_GROUP}`。\n\n"
        f"`{IDENTITY_STATEMENT}`仅作为S3身份依据，不作为实质关系边，已从S6关系候选中明确关闭；‘1719年回那不勒斯’、"
        "自1718年任舰队司令及de Matteis为其工作三项原书陈述仍保留为关系/履历候选，留待S6逐条审查。"
        "本次没有外部来源核验、没有新增formal relation。S3 new候选数不变，身份组减少1；待登记组减少1，待登记成员候选数不变。\n"
    )

    result_text = base.sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text, n_statements = re.subn(
        r"(原书断言及关系候选.*?relation_candidate true )10,400(、false )4,762(、unset 0)",
        r"\g<1>10,399\g<2>4,763\g<3>", result_text, count=1,
    )
    assert n_statements == 1, "could not refresh relation-candidate totals"
    result_text += (
        f"\n\n### S3人物身份组裁决：‘Binchs’与Admiral Byng（{DATE}）\n\n"
        f"`cand-0475`（B.csv#323）与`cand-7301`（正文来源拼写）均维持`new`，归入`{TARGET_GROUP}`。"
        "第7章p.200注5明言‘Binchs’ must be Admiral Byng；扫描页物理第38页核对了该注与正文注号。"
        "本决定仅采用Haskell的书内身份推断，未作外部身份核验；索引未给出名字。身份断言已标为S3证据而非S6实质关系；"
        "1719年回那不勒斯、1718年舰队司令身份及de Matteis为其工作仍待S6审查。详见"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: candidates=2; decisions remain new; groups {before_totals['new_groups']}->{totals['new_groups']}; "
            f"pending={before_totals['pending_groups']}/{before_totals['pending_members']}->"
            f"{totals['pending_groups']}/{totals['pending_members']}; identity_statement relation_candidate true->false; no files changed"
        )
        return 0

    base.sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    base.sync.write_csv(ENTITY_PATH, candidate_fields, planned_candidates)
    STATEMENTS_PATH.write_text(planned_statements_text, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {TARGET_GROUP} contains cand-0475 and cand-7301; groups={totals['new_groups']}; "
        f"pending={totals['pending_groups']}/{totals['pending_members']}; identity statement closed as S3 evidence"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
