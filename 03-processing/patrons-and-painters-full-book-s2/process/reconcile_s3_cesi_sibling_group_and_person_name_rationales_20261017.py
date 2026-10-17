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
MENTIONS_PATH = TABLES / "mentions.csv"
MANIFEST_PATH = TABLES / "ku-manifest.csv"
PROCESS_PATH = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
ANCHOR = "s3-reconcile-cesi-sibling-identity-and-title-only-rationales-20261017"
PROCESS_REF = f"03-processing/{TASK}/process/knowledge.md#{ANCHOR}"
GROUP = "new-person:angelo-cesi-d4e25faff9"
OLD_MON_SIGNOR_GROUP = "new-person:angelo-cesi-monsignor-20261017"
DBI_URL = "https://www.treccani.it/enciclopedia/angelo-cesi_res-9e027433-87ea-11dc-8e9d-0016357eee51_(Dizionario-Biografico)/"
DBI_ENTRY = "Luigi Cajani, ‘CESI, Angelo’, Dizionario Biografico degli Italiani, vol. 24 (1980)"
TITLE_ONLY_IDS = ["cand-0538", "cand-0559", "cand-0614", "cand-0615"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the two Angelo Cesi candidate forms and correct four title-only S3 rationales."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    alignment_fields, alignments = base.sync.read_csv(ALIGNMENT_PATH)
    candidate_fields, candidates = base.sync.read_csv(ENTITY_PATH)
    _, manifest = base.sync.read_csv(MANIFEST_PATH)
    mention_fields, mentions = base.sync.read_csv(MENTIONS_PATH)
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    assert len(alignment_by_id) == len(candidate_by_id)

    bishop = alignment_by_id["cand-0639"]
    monsignor = alignment_by_id["cand-10945"]
    assert bishop["decision"] == monsignor["decision"] == "new"
    assert not bishop.get("ku_id") and not monsignor.get("ku_id")
    assert base.sync.get_group(bishop["resolution_note"]) == GROUP
    assert base.sync.get_group(monsignor["resolution_note"]) == OLD_MON_SIGNOR_GROUP
    assert candidate_by_id["cand-0639"].get("index_entry_id") == "C.csv#163"
    assert candidate_by_id["cand-0639"].get("index_page_range") == "69, 70, 400"
    assert candidate_by_id["cand-10945"].get("candidate_source_ref") == "chp-20:20_CHP-20Postscript:l46-57#L53"

    ch3 = (ROOT / "02-sources/02-Markdown/03_CHP-3_sec_ii.md").read_text(encoding="utf-8-sig")
    ch20 = (ROOT / "02-sources/02-Markdown/20_CHP-20Postscript.md").read_text(encoding="utf-8-sig")
    assert "his brother Angelo Cesi, Bishop of Todi" in " ".join(ch3.split())
    assert "Cardinal Angelo Cesi" in ch3 and "In 1606 Cardinal Cesi died" in ch3
    assert "his brother, Monsignor Angelo Cesi" in " ".join(ch20.split())
    assert any(
        row.get("type") == "person"
        and any(name in f"{row.get('canonical_name', '')} {row.get('name_en', '')}" for name in ("Angelo Cesi", "Angelo, Bishop"))
        for row in manifest
    ) is False, "no existing same-type Angelo Cesi KU should be available for this new group"

    statements_lines = STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
    statements = [json.loads(line) for line in statements_lines if line.strip()]
    statement_by_id = {row["statement_id"]: row for row in statements}
    promise_id = "st-chp3-secii-l54-60-cesi-promised-high-altar-decoration"
    death_id = "st-chp3-secii-l54-60-angelo-cesi-died-1606"
    promise = statement_by_id[promise_id]
    death = statement_by_id[death_id]
    assert promise.get("subject_candidate_id") == "cand-0639"
    assert "confirm identity at S3" in promise["qualifiers"].get("qualification", "")
    assert death.get("subject_candidate_id") == "cand-0639"

    prior_bishop_note = bishop["resolution_note"]
    prior_monsignor_note = monsignor["resolution_note"]
    planned_alignments = [dict(row) for row in alignments]
    revised_alignment = {
        row["candidate_id"]: row
        for row in planned_alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    revised_alignment["cand-0639"]["process_ref"] = PROCESS_REF
    revised_alignment["cand-0639"]["accessed_date"] = DATE
    revised_alignment["cand-0639"]["resolution_note"] = (
        "source_ref=candidate=cand-0639;index_entry=C.csv#163;index_pages=69,70,400;"
        "s2_mentions=m-chp3-secii-l40-52-0011@02-sources/02-Markdown/03_CHP-3_sec_ii.md#L40-52[Angelo;chars=779-785],"
        "m-chp3-secii-l40-52-0012@02-sources/02-Markdown/03_CHP-3_sec_ii.md#L40-52[Cesi;chars=786-790],"
        "m-chp3-secii-l54-60-0026@02-sources/02-Markdown/03_CHP-3_sec_ii.md#L54-60[Cardinal Angelo Cesi;chars=2063-2083],"
        "m-chp20-p400-037@02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57[Monsignor Angelo Cesi];"
        f"group={GROUP}; S3复核（{DATE}）：索引人物为Angelo Cesi, Bishop of Todi；第3章p.69称其为Pier Donato Cesi的兄弟，"
        "第2版后记p.400称Monsignor Angelo Cesi为同一Cardinal Cesi的兄弟，二者是同一兄弟身份链，故cand-10945并入本组。"
        f"Treccani DBI（{DBI_ENTRY}；{DBI_URL}；访问于{DATE}）记载Angelo Cesi为托迪主教、1606年去世，并称1586年晋铎枢机的推荐未成功；"
        "这支持p.69与p.400的兄弟身份，也说明第3章p.70的‘Cardinal Angelo’称谓与权威传记不一致。p.70同时记其1606年去世；"
        "S3将该书内称谓映射到同一Angelo Cesi，但保留头衔冲突为待核的来源事实，不把它当作独立枢机身份。无既有同类KU；新建一组。"
    )
    revised_alignment["cand-10945"]["process_ref"] = PROCESS_REF
    revised_alignment["cand-10945"]["accessed_date"] = DATE
    revised_alignment["cand-10945"]["resolution_note"] = (
        "source_ref=candidate=cand-10945;candidate_source_ref=chp-20:20_CHP-20Postscript:l46-57#L53;"
        "source_file=02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57;"
        "s2_mentions=m-chp20-p400-037@02-sources/02-Markdown/20_CHP-20Postscript.md#L46-57[Monsignor Angelo Cesi];"
        f"prior_group_id={OLD_MON_SIGNOR_GROUP};group={GROUP}; S3复核（{DATE}）：p.400的Monsignor Angelo Cesi是第3章p.69所称Pier Donato的兄弟Angelo Cesi, Bishop of Todi，"
        "与cand-0639相同；Treccani DBI (Angelo Cesi, Bishop of Todi, died 1606; cardinal nomination in 1586 unsuccessful) corroborates the identity."
        f"该外部记录：{DBI_URL}（访问于{DATE}）。原先把他拆作独立人物的结论被第3章的兄弟关系及权威传记改判；仍为source-local new person，未复用现有KU。"
    )
    prior_title_notes: dict[str, str] = {}
    for cid in TITLE_ONLY_IDS:
        row = revised_alignment[cid]
        assert row["decision"] == "new" and not row.get("ku_id")
        old_group = base.sync.get_group(row["resolution_note"])
        assert old_group and not old_group.startswith("sg3-")
        assert "source anchor gives a full personal name" in row["resolution_note"]
        prior_title_notes[cid] = row["resolution_note"]
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"source_ref=candidate={cid};index_entry={candidate_by_id[cid].get('index_entry_id')};"
            f"index_pages={candidate_by_id[cid].get('index_page_range')}; prior_group_id={old_group};group={old_group}; "
            f"S3理由更正（{DATE}）：保留既有new source-local人物组；索引与正文为头衔加姓氏或姓氏加头衔，未提供given name，"
            "不再称其为‘full personal name’，也不据此补造名字或外部生平。原组边界与无既有同类KU判断不变。"
        )

    planned_candidates = [dict(row) for row in candidates]
    revised_candidate = {row["candidate_id"]: row for row in planned_candidates}
    revised_candidate["cand-10945"]["canonical_name"] = "Monsignor Angelo Cesi"
    revised_candidate["detail"] = (
        "S3跨章复核（2026-10-17）：本书第3章p.69称Angelo Cesi为Pier Donato Cesi的兄弟，第2版后记p.400称Monsignor Angelo Cesi为同一Cardinal Cesi的兄弟；"
        "Treccani DBI确认Angelo Cesi为托迪主教并于1606年去世，1586年枢机任命推荐未成功。与cand-0639同一source-local人物；"
        "本书第3章p.70称‘Cardinal Angelo’与权威传记的身份/头衔不一致，保留为待核书内称谓。"
    )

    planned_mentions = [dict(row) for row in mentions]
    mention_notes = {
        "m-chp3-secii-l54-60-0026": "S3 maps this title-form reference to the Bishop of Todi Angelo Cesi candidate cand-0639; Treccani DBI reports the 1586 cardinal nomination was unsuccessful. Retain Haskell's conflicting title as source wording.",
        "m-chp3-secii-l54-60-0035": "Continuation of the same p.70 source reference; identity maps to cand-0639, while Haskell's cardinal title remains in conflict with the Treccani DBI biography.",
    }
    for row in planned_mentions:
        if row.get("mention_id") in mention_notes:
            row["note"] = mention_notes[row["mention_id"]]
    assert set(mention_notes) <= {row.get("mention_id") for row in planned_mentions}

    planned_statement_lines = list(statements_lines)
    target_statement_ids = {promise_id, death_id}
    changed_statement_ids = set()
    for i, line in enumerate(planned_statement_lines):
        if not line.strip():
            continue
        statement = json.loads(line)
        sid = statement.get("statement_id")
        if sid == promise_id:
            statement["qualifiers"]["qualification"] = (
                "S3 identity mapping finalized to Angelo Cesi, Bishop of Todi (cand-0639), using the p.69–70 chapter context and the p.400 sibling reference. "
                "Treccani DBI says the 1586 cardinal nomination was unsuccessful; Haskell's title ‘Cardinal Angelo’ is retained as disputed source wording. "
                "This does not independently verify the promise about the High Altar."
            )
            statement["qualifiers"]["relation_candidate_note"] = (
                "The identity endpoint is mapped to cand-0639 at S3. The book's cardinal title conflicts with the Treccani DBI biography; the promised decoration claim remains a separate S6 relation/content review."
            )
        elif sid == death_id:
            statement["qualifiers"]["qualification"] = (
                "Haskell calls him ‘Cardinal Cesi’ and dates the death to 1606. Treccani DBI identifies Angelo Cesi as Bishop of Todi, records an unsuccessful cardinal nomination in 1586, and gives his death in 1606; retain the title discrepancy as source conflict."
            )
            statement["qualifiers"]["relation_candidate"] = False
            statement["qualifiers"]["relation_candidate_note"] = (
                "Death date is a source-backed biographical claim, not a substantive graph relation; the title discrepancy is documented in S3."
            )
        else:
            continue
        planned_statement_lines[i] = json.dumps(statement, ensure_ascii=False)
        changed_statement_ids.add(sid)
    assert changed_statement_ids == target_statement_ids
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
    assert f'<a id="{ANCHOR}"></a>' not in process_text
    process_text = process_text.rstrip() + (
        f"\n\n<a id=\"{ANCHOR}\"></a>\n\n### S3跨章身份组复核：Angelo Cesi 与头衔型人物理由更正（{DATE}）\n\n"
        "#### Cesi身份组\n\n"
        "将`cand-0639`（C.csv#163；索引页69、70、400）与`cand-10945`（后记p.400来源候选）重新归为同一组`"
        f"{GROUP}`。第3章p.69称Angelo Cesi为Cardinal Pier Donato的兄弟及托迪主教；后记p.400称Monsignor Angelo Cesi为Cardinal Cesi的兄弟。"
        "两处都指向同一兄弟身份。Treccani DBI条目“CESI, Angelo”将其识别为托迪主教；条目称1586年枢机任命推荐未成功，并记其1606年去世；"
        "该文还称他与兄弟Pier Donato共同资助Vallicella教堂。来源："
        f"[{DBI_ENTRY}]({DBI_URL})，访问于{DATE}。由此，第3章p.70的‘Cardinal Angelo’及‘1606年Cardinal Cesi去世’可映射到同一Angelo Cesi，"
        "但书内枢机头衔与DBI不符；此头衔冲突保留为来源问题，不据以拆出第三个人，也不把书内身份判断当作外部事实。"
        f"旧拆分组号`{OLD_MON_SIGNOR_GROUP}`保留在cand-10945的alignment历史字段；被纠正的旧裁决记录如下：\n\n"
        f"- `cand-0639`旧注：{prior_bishop_note}\n"
        f"- `cand-10945`旧注：{prior_monsignor_note}\n\n"
        "`st-chp3-secii-l54-60-cesi-promised-high-altar-decoration`的端点身份已在S3定为cand-0639；其装饰承诺仍留待S6逐条审查。"
        "`st-chp3-secii-l54-60-angelo-cesi-died-1606`仅是履历断言，已从关系候选中关闭；死年获DBI支持，Cardinal称谓仍与DBI冲突。\n\n"
        "#### 头衔型人物组理由更正\n\n"
        "`cand-0538`（Marshal Caprara）、`cand-0559`（Earl of Carlisle）、`cand-0614`（Conte Cavazza）和`cand-0615`（Comte de Caylus）"
        "均保留原new组，但alignment旧理由误称它们有‘full personal name’。现更正为书内/索引仅给头衔与姓氏，未提供given name；不补造全名。"
        "Caylus的p.319全称与p.360跨行拆开的同一称谓构成书内跨章锚点；Carlisle的索引页279、305及正文p.278–279明确承接‘Lord Carlisle’与代词‘He’。\n\n"
        "被更正的四条旧alignment理由保留如下：\n\n"
        + "\n".join(f"- `{cid}`：{note}" for cid, note in prior_title_notes.items())
        + "\n\n"
        f"本次S3组成员增加cand-10945并并入既有组，候选数不变、new身份组数减少1；S4待登记组减少1，待登记成员数不变。"
        f"S3 new={base.sync.fmt(totals['new_candidates'])}候选/{base.sync.fmt(totals['new_groups'])}组；"
        f"S4已登记{base.sync.fmt(totals['registered_groups'])}组/{base.sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{base.sync.fmt(totals['pending_groups'])}组/{base.sync.fmt(totals['pending_members'])}条映射；KU={len(manifest)}。\n"
    )

    result_text = base.sync.update_result(
        RESULT_PATH.read_text(encoding="utf-8-sig"), stats, totals, len(manifest)
    )
    result_text, relation_count_updates = re.subn(
        r"(原书断言及关系候选.*?relation_candidate true )10,399(、false )4,763(、unset 0)",
        r"\g<1>10,398\g<2>4,764\g<3>", result_text, count=1,
    )
    assert relation_count_updates == 1, "could not refresh relation candidate counts"
    result_text += (
        f"\n\n### S3跨章身份组更正：Angelo Cesi兄弟身份（{DATE}）\n\n"
        f"`cand-0639`（托迪主教Angelo Cesi）与`cand-10945`（后记p.400的Monsignor Angelo Cesi）合入`{GROUP}`。"
        "第3章p.69与后记p.400均称其为Cardinal Pier Donato Cesi的兄弟。Treccani DBI证实Angelo为托迪主教、1606年去世，且1586年枢机推荐未成功；"
        "书中p.70称‘Cardinal Angelo’的头衔冲突保留为来源问题。当前新组数减少1，S4待登记组减少1、成员映射不变。详见"
        f"[过程记录](../../03-processing/{TASK}/process/knowledge.md#{ANCHOR})。"
    )

    if args.dry_run:
        print(
            f"dry-run passed: cand-0639/cand-10945 merge into {GROUP}; title-only rationales corrected={len(TITLE_ONLY_IDS)}; "
            f"new groups {before_totals['new_groups']}->{totals['new_groups']}; "
            f"pending={before_totals['pending_groups']}/{before_totals['pending_members']}->"
            f"{totals['pending_groups']}/{totals['pending_members']}; Treccani DBI and source sibling evidence checked; no files changed"
        )
        return 0

    base.sync.write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignments)
    base.sync.write_csv(ENTITY_PATH, candidate_fields, planned_candidates)
    base.sync.write_csv(MENTIONS_PATH, mention_fields, planned_mentions)
    STATEMENTS_PATH.write_text(planned_statements_text, encoding="utf-8-sig", newline="\n")
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="\n")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: cand-0639 and cand-10945 now share {GROUP}; corrected title-only rationales={len(TITLE_ONLY_IDS)}; "
        f"new groups={totals['new_groups']}; pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
