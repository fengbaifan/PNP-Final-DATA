from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync


ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
SOURCE = ROOT / "02-sources" / "02-Markdown" / "10_CHP-10_intro.md"
SEGMENT = "chp-10:10_CHP-10_intro:l491-634"
PROCESS_REF = "S3-carlevarijs-entry-works-2026-10-16"
CASES = {
    "cand-0556": {
        "decision": "new",
        "group": "sg3-work-carlevarijs-colloredo-entry-1726",
        "note": "Entry of the Count of Colloredo",
        "rationale": "C.csv#80 is a work subentry. The indexed subentry has an exact S2 mention and st-chp10-notes-p277n5-colloredo-entry says Carlevarijs painted this named entry in 1726. The Count's first name and any commission are not inferred. No exact same-type work KU was found.",
    },
    "cand-0557": {
        "decision": "new",
        "group": "sg3-work-carlevarijs-manchester-entry-1707",
        "note": "Lord Manchester’s Entry into Venice",
        "rationale": "C.csv#81 subentry and p.277 note 5 name Lord Manchester's Entry into Venice (1707) as a Carlevarijs painting; st-chp10-p276-manchester-carlevarijs-entry separately says Lord Manchester commissioned Carlevarijs to record his entry. This candidate is the work, not the person heading the index entry. No exact same-type work KU was found.",
    },
    "cand-8839": {
        "decision": "new",
        "group": "sg3-work-carlevarijs-manchester-entry-1707",
        "note": "Lord Manchester’s Entry into Venice",
        "rationale": "The p.276 body candidate and C.csv#81 index subentry identify the same source-level painting: the body says Lord Manchester commissioned Carlevarijs to record his entry, and p.277 note 5 names the painting and dates it to 1707. S2 already anchors the exact title as m-chp10-p277n5-manchester-entry. The book-era Birmingham location is not treated as current.",
    },
    "cand-8845": {
        "decision": "new",
        "group": "sg3-work-carlevarijs-regatta-frederick-iv-1709",
        "note": "Regatta in honour of Frederick IV of Denmark",
        "rationale": "The p.277 body says Luca Carlevarijs painted the regatta offered in Frederick IV's honour; note 5 identifies it as the Regatta in honour of Frederick IV of Denmark (1709). The source supports a distinct work identity, but not a current holding or an independently identified surviving version. No exact same-type work KU was found.",
    },
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def csv_text(fields, rows):
    from io import StringIO

    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description="Resolve Carlevarijs entry-work candidates in S3 with source anchors.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_path = TABLES / "entity-candidates.csv"
    alignment_path = TABLES / "alignment.csv"
    mention_path = TABLES / "mentions.csv"
    statement_path = TABLES / "book-statements.jsonl"
    candidate_fields, candidates = read_csv(candidate_path)
    alignment_fields, alignments = read_csv(alignment_path)
    mention_fields, mentions = read_csv(mention_path)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert set(CASES) <= candidate_by_id.keys()
    assert set(CASES) <= alignment_by_id.keys()
    assert all(alignment_by_id[cid]["decision"] == "undecided" for cid in CASES)
    assert all(not alignment_by_id[cid].get("ku_id") for cid in CASES)
    existing_title_mentions = [
        row for row in mentions
        if row["mention_id"] == "m-chp10-p277n5-manchester-entry"
        and row["candidate_id"] == "cand-8839"
        and row["surface_form"] == "Lord Manchester’s Entry into Venice (1707)"
    ]
    assert len(existing_title_mentions) == 1
    existing_start = int(existing_title_mentions[0]["start_char"])
    existing_end = int(existing_title_mentions[0]["end_char"])
    assert "st-chp10-notes-p277n5-manchester-entry" not in {
        json.loads(line)["statement_id"] for line in statement_path.read_text(encoding="utf-8-sig").splitlines() if line
    }

    quote = "Besides Lord Manchester’s Entry into Venice (1707)"
    source_lines = SOURCE.read_text(encoding="utf-8-sig").splitlines()
    segment_text = "\n".join(source_lines[490:634])
    start = segment_text.index(quote) + len("Besides ")
    end = start + len("Lord Manchester’s Entry into Venice (1707)")
    assert segment_text[start:end] == "Lord Manchester’s Entry into Venice (1707)"
    assert (existing_start, existing_end) == (start, end)

    candidate_by_id["cand-0557"]["suggested_type"] = "work"
    candidate_by_id["cand-0557"]["canonical_name"] = "Lord Manchester’s Entry into Venice (1707)"
    candidate_by_id["cand-0557"]["sub_entry"] = "Entry of Lord Manchester"
    candidate_by_id["cand-0557"]["detail"] = (
        "C.csv#81 is an index subentry under Luca Carlevarijs. Chapter 10 p.276 says Lord Manchester commissioned Carlevarijs "
        "to record his 1707 Venice entry; p.277 note 5 names the resulting painting as Lord Manchester’s Entry into Venice (1707). "
        "The candidate is the work, not the indexed artist. The footnote cited for the p.276 location report was not used to establish a current holding."
    )
    candidate_by_id["cand-8839"]["canonical_name"] = "Lord Manchester’s Entry into Venice (1707)"
    candidate_by_id["cand-8839"]["detail"] = (
        "Source-level painting identified across Chapter 10 pp.276–277: Lord Manchester commissioned Luca Carlevarijs to record his "
        "1707 Venice entry, and p.277 note 5 names the work as Lord Manchester’s Entry into Venice (1707). The p.276 note reports "
        "a Birmingham City Art Gallery location at the time of Haskell's source; do not treat it as a current holding or as independent version verification."
    )
    planned_mentions = mentions

    statements = [
        json.loads(line)
        for line in statement_path.read_text(encoding="utf-8-sig").splitlines()
        if line
    ]
    new_statement = {
        "statement_id": "st-chp10-notes-p277n5-manchester-entry",
        "segment_id": SEGMENT,
        "subject_candidate_id": "cand-0554",
        "object_candidate_id": "cand-8839",
        "predicate": "carlevarijs_painted_lord_manchester_entry_into_venice_1707",
        "qualifiers": {
            "source_line_start": 499,
            "source_line_end": 499,
            "printed_page": 277,
            "pdf_physical_page": 2,
            "claim": "Haskell's note 5 names Lord Manchester's Entry into Venice (1707) as a painting by Carlevarijs; the p.276 narrative says Lord Manchester commissioned Carlevarijs to record his entry.",
            "speaker": "Haskell, footnote with related body statement",
            "text_layer": "authorial note",
            "qualification": "The note identifies the work and year. Lord Manchester's personal identity is unresolved; the cited p.276 note about a reported holding is not used as current location evidence.",
            "mentioned_candidate_ids": ["cand-0554", "cand-0557", "cand-8839", "cand-1504"],
            "footnote_number": 5,
            "related_body_statement_ids": ["st-chp10-p276-manchester-carlevarijs-entry"],
            "footnote_segment": SEGMENT,
            "footnote_source_line": 499,
            "relation_candidate": True,
        },
        "original_quote": "Besides Lord Manchester’s Entry into Venice (1707)",
        "source_file": "02-sources/02-Markdown/10_CHP-10_intro.md",
        "origin": "book",
    }
    planned_statements = statements + [new_statement]

    prior_history = []
    for cid, spec in CASES.items():
        row = alignment_by_id[cid]
        prior_history.append(
            f"- `{cid}`: prior decision=`{row['decision']}`; prior resolution_note=`{row.get('resolution_note','')}`"
        )
        if cid in {"cand-0557", "cand-8839"}:
            candidate_by_id[cid]["suggested_type"] = "work"
        if cid == "cand-8839":
            candidate_by_id[cid]["canonical_name"] = "Lord Manchester’s Entry into Venice (1707)"
        row["decision"] = spec["decision"]
        row["ku_id"] = ""
        row["process_ref"] = PROCESS_REF
        row["resolution_note"] = (
            f"source_ref=entity-candidates.csv#{cid};index_entry={candidate_by_id[cid].get('index_entry_id','')};"
            f"index_subentry={candidate_by_id[cid].get('sub_entry','')};segment={SEGMENT};"
            f"mentions={ 'm-chp10-p277n5-colloredo-entry' if cid == 'cand-0556' else 'm-chp10-p277n5-manchester-entry' if cid in {'cand-0557','cand-8839'} else 'm-chp10-p277n5-frederick-regatta' };"
            f"statements={ 'st-chp10-notes-p277n5-colloredo-entry' if cid == 'cand-0556' else 'st-chp10-notes-p277n5-manchester-entry,st-chp10-p276-manchester-carlevarijs-entry' if cid in {'cand-0557','cand-8839'} else 'st-chp10-p277-carlevarijs-regatta' };"
            f"decision=new;group={spec['group']};rationale={spec['rationale']}"
        )

    group_counts = {}
    for row in alignments:
        if row.get("decision") == "new" and not row.get("external_source"):
            match = re.search(r"group=([^;| ]+)", row.get("resolution_note", ""))
            if match:
                group_counts.setdefault(match.group(1), []).append(row["candidate_id"])
    expected_group_members = {
        "sg3-work-carlevarijs-colloredo-entry-1726": {"cand-0556"},
        "sg3-work-carlevarijs-manchester-entry-1707": {"cand-0557", "cand-8839"},
        "sg3-work-carlevarijs-regatta-frederick-iv-1709": {"cand-8845"},
    }
    for group, expected in expected_group_members.items():
        assert set(group_counts.get(group, [])) == expected, (group, group_counts.get(group))

    stats = sync.summarize_by_type(candidates, alignments)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    _, manifest = read_csv(TABLES / "ku-manifest.csv")
    result_text = sync.update_result(RESULT.read_text(encoding="utf-8-sig"), stats, totals, len(manifest))
    # The alignment table includes identity-source rows in addition to the 12,404 candidate decisions.
    external_count = sum(bool(row.get("external_source")) for row in alignments)
    result_text, n = re.subn(
        r"^\| \[全书对齐\].*$",
        f"| [全书对齐](../tables/alignment.csv) | {sync.fmt(len(alignments))} 条：{sync.fmt(totals['total'])} 条候选决定记录及 {sync.fmt(external_count)} 条外部身份记录；候选决定数见下表 |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n == 1
    result_text, n_mentions = re.subn(
        r"^\| \[提及账本\].*$",
        f"| [提及账本](../tables/mentions.csv) | {sync.fmt(len(mentions))} mentions |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n_mentions == 1
    result_text, n_statements = re.subn(
        r"^\| \[原书断言及关系候选\].*$",
        f"| [原书断言及关系候选](../tables/book-statements.jsonl) | {sync.fmt(len(statements) + 1)} statements；relation_candidate true {sync.fmt(sum(bool(x.get('qualifiers', {}).get('relation_candidate')) for x in planned_statements))}、false {sync.fmt(sum(x.get('qualifiers', {}).get('relation_candidate') is False for x in planned_statements))}、unset {sync.fmt(sum('relation_candidate' not in x.get('qualifiers', {}) for x in planned_statements))} |",
        result_text,
        count=1,
        flags=re.M,
    )
    assert n_statements == 1
    status = (
        f"**当前状态：全书 S2 语义处理已完成，尚未独立语义验收；S3 候选决定账本已按收口标准核对，"
        f"{sync.fmt(totals['total'])} 个候选均有唯一决定、说明与过程引用。{sync.fmt(totals['undecided'])} 项明确保留为待证，"
        f"其身份问题尚未解决；S4 KU 登记处理中。** "
        f"{sync.fmt(totals['total'])} 个候选决定行中，same={sync.fmt(totals['same_candidates'])}（指向{sync.fmt(totals['same_kus'])}个既有 KU）、"
        f"new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}个身份组）、conflict={sync.fmt(totals['conflict'])}、"
        f"excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。"
        f"S4 已登记{sync.fmt(totals['registered_groups'])}组、映射{sync.fmt(totals['registered_members'])}条成员候选；"
        f"尚待登记{sync.fmt(totals['pending_groups'])}组、{sync.fmt(totals['pending_members'])}条映射。"
    )
    result_text, n = re.subn(r"^\*\*当前状态：.*?S3 已将", status + "S3 已将", result_text, count=1, flags=re.M)
    assert n == 1

    process_note = (
        "\n\n### S3 补裁：Carlevarijs 三件入城／节庆作品（2026-10-16）\n\n"
        "复核 C.csv#80–82 与第10章 p.276 正文、p.277 注5后，明确分开艺术家、人物和三件作品。"
        "`cand-0556`（Entry of the Count of Colloredo，1726）、`cand-0557`（Lord Manchester’s Entry into Venice，1707）及 `cand-8845`（Regatta in honour of Frederick IV of Denmark，1709）"
        "均由原先待证改裁为独立 new work 组；不与 Carlevarijs 人物 `cand-0554`／`cand-0558` 合并。"
        "`cand-0557` 原 suggested_type=person 是索引父项误读，已改为 work；复用既有精确提及 `m-chp10-p277n5-manchester-entry`，并新增 S2 关系候选陈述"
        "`st-chp10-notes-p277n5-manchester-entry`；该陈述把 p.277 注5作品名与 p.276 委托正文相连，保留 Lord Manchester 身份待证。"
        "Colloredo 的名与委托关系不外推；Fredericksborg 的现今地点不核定。原 alignment 决定及注释在写入前保存在本脚本 dry-run 审查对象及此前 S3 记录；本次逐行改为清晰的当前理由并保留书内来源锚点。"
        f"本批前 S3 `undecided` {sync.fmt(totals['undecided'] + len(CASES))}，`new` {sync.fmt(totals['new_candidates'] - len(CASES))}；本批后 `undecided` {sync.fmt(totals['undecided'])}，`new` {sync.fmt(totals['new_candidates'])}，"
        f"new 身份组{sync.fmt(totals['new_groups'])}。相关旧注释：{' '.join(prior_history)}\n"
    )
    result_text += (
        "\n\n### S3 补裁：Carlevarijs 三件入城／节庆作品（2026-10-16）\n\n"
        "`cand-0556`（Colloredo 入城，1726）、`cand-0557` 与 `cand-8839`（Lord Manchester 入城，1707；同一作品）及 `cand-8845`（Frederick IV 庆典赛舟，1709）归入三个独立 work 身份组；"
        "`cand-0557` 类型由 person 更正为 work；已有候选 `cand-8839` 与索引子目同指该作品，并共用一个 new work 组。作品身份依据第10章 p.276 正文及 p.277 注5；人物 Carlevarijs 保持独立。Lord Manchester 与 Count of Colloredo 的个人身份不扩定；"
        "Regatta 的当前馆藏地点不核定。Manchester 项新增精确 S2 mention 与关系候选陈述，正式关系仍待 S6。"
        f"S3 现为 same={sync.fmt(totals['same_candidates'])}、new={sync.fmt(totals['new_candidates'])}（{sync.fmt(totals['new_groups'])}组）、conflict={sync.fmt(totals['conflict'])}、excluded={sync.fmt(totals['excluded'])}、undecided={sync.fmt(totals['undecided'])}。"
        "\n\n写入前 alignment 记录：\n\n" + "\n".join(prior_history) + "\n"
    )

    if args.dry_run:
        print("S3 Carlevarijs work adjudication dry-run passed")
        print(f"  candidates={len(CASES)}; new={totals['new_candidates']}; groups={totals['new_groups']}; undecided={totals['undecided']}")
        print(f"  Manchester title span=[{start},{end}); existing mention reused; new statement ID is unique")
        print(f"  mentions={len(mentions)} -> {len(planned_mentions)}; statements={len(statements)} -> {len(planned_statements)}")
        return 0

    write_csv(candidate_path, candidate_fields, candidates)
    write_csv(alignment_path, alignment_fields, alignments)
    with statement_path.open("w", encoding="utf-8-sig", newline="\n") as stream:
        for row in planned_statements:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    PROCESS.write_text(PROCESS.read_text(encoding="utf-8-sig") + process_note, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(result_text, encoding="utf-8-sig", newline="\n")
    print("S3 Carlevarijs work adjudication applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
