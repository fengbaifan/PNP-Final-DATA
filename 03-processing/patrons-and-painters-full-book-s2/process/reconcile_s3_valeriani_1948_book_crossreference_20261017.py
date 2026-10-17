from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import register_s4_archive_memmo_query_sheet_20261017 as process_sync

sync = process_sync.sync
ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
STAGES = ROOT / "03-processing" / TASK / "process" / "stages.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
DATE = "2026-10-17"
BODY_CANDIDATE = "cand-11088"
BIB_CANDIDATE = "cand-11204"
SOURCE_GROUP = "archive-group-8a548cd83811"
TARGET_GROUP = "archive-group-09a3b2fdbd56"
BODY_SOURCE = "02-sources/02-Markdown/20_CHP-20Postscript.md"
BIB_SOURCE = "02-sources/02-Markdown/21_CHP-21Bibliography.md"
BODY_QUOTE = (
    "The interest of the eighteenth-century Russian court in attracting artists from Venice "
    "was investigated in a fully documented book about Giuseppe Valeriani in 1948,7"
)
NOTE_QUOTE = "7 Konopleva."
BIB_QUOTE = "Konopleva, M. S.: Teatralni Zhivopicets Giuseppe Valeriani, Leningrad 1948."
S2_STATEMENT_ID = "st-chp20-p406-n07-citation"
BODY_STATEMENT_ID = "st-chp20-p406-russian-court-valeriani-book"
BIB_STATEMENT_ID = "st-chp21-bib-l616-656-entry-28"
PROCESS_ANCHOR = "s3-s4-valeriani-1948-publication-reconciliation-20261017"
CORRECTION_MARKER = "S2 citation correction 2026-10-17: footnote 7 identifies the 1948 book"


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def normalized(text: str) -> str:
    return " ".join(text.split())


def find_statement(lines: list[str], statement_id: str) -> tuple[int, dict]:
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("statement_id") == statement_id:
            return index, row
    raise AssertionError(f"missing statement: {statement_id}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconcile the 1948 Valeriani book body mention with its footnote and bibliography in S3"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    candidate_fields, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    alignment_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    stages_text = STAGES.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    alignment_by_id = {
        row["candidate_id"]: row
        for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert BODY_CANDIDATE in candidate_by_id and BIB_CANDIDATE in candidate_by_id
    assert candidate_by_id[BODY_CANDIDATE].get("suggested_type") == "archive"
    assert candidate_by_id[BIB_CANDIDATE].get("suggested_type") == "archive"
    body_row = alignment_by_id[BODY_CANDIDATE]
    bib_row = alignment_by_id[BIB_CANDIDATE]
    assert body_row.get("decision") == "new" and not body_row.get("ku_id")
    assert bib_row.get("decision") == "new" and not bib_row.get("ku_id")
    body_group = group_of(body_row.get("resolution_note", ""))
    bib_group = group_of(bib_row.get("resolution_note", ""))
    assert body_group in {SOURCE_GROUP, TARGET_GROUP}
    assert bib_group == TARGET_GROUP

    group_members = {
        cid for cid, row in alignment_by_id.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == TARGET_GROUP
    }
    if body_group == SOURCE_GROUP:
        assert group_members == {BIB_CANDIDATE}
    else:
        assert group_members == {BODY_CANDIDATE, BIB_CANDIDATE}

    for relative, quote in (
        (BODY_SOURCE, BODY_QUOTE),
        (BODY_SOURCE, NOTE_QUOTE),
        (BIB_SOURCE, BIB_QUOTE),
    ):
        source_text = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert normalized(quote) in normalized(source_text), f"source evidence changed: {relative}"

    statement_lines = (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
    body_index, body_statement = find_statement(statement_lines, BODY_STATEMENT_ID)
    footnote_index, footnote_statement = find_statement(statement_lines, S2_STATEMENT_ID)
    bib_index, bib_statement = find_statement(statement_lines, BIB_STATEMENT_ID)
    assert body_statement.get("object_candidate_id") == "cand-9382"
    assert body_statement.get("subject_candidate_id") == BODY_CANDIDATE
    assert (body_statement.get("qualifiers") or {}).get("footnote_statement_ids") == [S2_STATEMENT_ID]
    assert footnote_statement.get("object_candidate_id") == BIB_CANDIDATE
    assert footnote_statement.get("original_quote") == NOTE_QUOTE
    assert (footnote_statement.get("qualifiers") or {}).get("relation_candidate") is False
    assert bib_statement.get("object_candidate_id") == BIB_CANDIDATE
    bib_record = (bib_statement.get("qualifiers") or {}).get("bibliographic_record") or {}
    assert bib_record.get("title_as_printed") == "Teatralni Zhivopicets Giuseppe Valeriani"
    assert bib_record.get("publication_details_as_printed") == "Leningrad 1948"

    current_claim = (footnote_statement.get("qualifiers") or {}).get("claim", "")
    if CORRECTION_MARKER in footnote_statement.get("qualifiers", {}).get("qualification", ""):
        assert "later article" not in current_claim.casefold()
    else:
        assert "later articles" in current_claim

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {
        row["candidate_id"]: row
        for row in planned_alignment
        if row.get("candidate_id") and not row.get("external_source")
    }
    planned_candidates = [dict(row) for row in candidates]
    planned_candidate_by_id = {row["candidate_id"]: row for row in planned_candidates}
    if body_group == SOURCE_GROUP:
        old_note = planned_by_id[BODY_CANDIDATE]["resolution_note"]
        planned_by_id[BODY_CANDIDATE]["resolution_note"] = re.sub(
            rf"group={re.escape(SOURCE_GROUP)}(?=[;| ])",
            f"group={TARGET_GROUP}",
            old_note,
            count=1,
        )
        planned_by_id[BODY_CANDIDATE]["resolution_note"] += (
            f" S3 identity reconciliation {DATE}: same 1948 publication as {BIB_CANDIDATE}; "
            f"prior_group={SOURCE_GROUP}; body p.406 marker 7 points to the Konopleva citation; "
            "the chapter 21 bibliography gives M. S. Konopleva, the title Teatralni Zhivopicets "
            "Giuseppe Valeriani, Leningrad 1948. Keep both archive candidates in the single "
            f"new group {TARGET_GROUP}; the publication was not independently consulted."
        )
        planned_by_id[BIB_CANDIDATE]["resolution_note"] += (
            f" S3 identity reconciliation {DATE}: identity peer={BODY_CANDIDATE}; "
            "chapter 20 p.406 describes a fully documented 1948 book about Giuseppe Valeriani "
            "and footnote 7 cites Konopleva; the chapter 21 title and publication year match "
            "that description. Keep both candidates in this one new archive group."
        )
    else:
        assert f"prior_group={SOURCE_GROUP}" in planned_by_id[BODY_CANDIDATE]["resolution_note"]
        assert f"identity peer={BODY_CANDIDATE}" in planned_by_id[BIB_CANDIDATE]["resolution_note"]

    planned_candidate_by_id[BODY_CANDIDATE]["detail"] = (
        "The p.406 body description is identified with the bibliography entry at p.426 through footnote 7: "
        "M. S. Konopleva, Teatralni Zhivopicets Giuseppe Valeriani, Leningrad 1948. "
        "This and the bibliography candidate cand-11204 form one archive identity group; "
        "the publication itself was not independently consulted."
    )
    planned_candidate_by_id[BIB_CANDIDATE]["detail"] = (
        "The bibliography entry at printed p.426 supplies the title and publication details for the book "
        "described at p.406, note 7. In S3 it shares one archive identity group with cand-11088. "
        "The author remains identified only as printed, M. S. Konopleva; the cited publication was not independently consulted."
    )

    planned_statements = list(statement_lines)
    if CORRECTION_MARKER not in footnote_statement.get("qualifiers", {}).get("qualification", ""):
        footnote_statement["qualifiers"]["claim"] = (
            "Footnote 7 identifies the 1948 book about Giuseppe Valeriani named in the preceding p.406 sentence; "
            "the chapter 21 bibliography supplies its title and publication details."
        )
        footnote_statement["qualifiers"]["qualification"] = (
            "The footnote gives only the surname Konopleva; the bibliography prints the author as M. S. Konopleva. "
            "The person’s full identity remains unresolved, and the cited book was not independently consulted. "
            + CORRECTION_MARKER
            + "."
        )
        planned_statements[footnote_index] = json.dumps(
            footnote_statement, ensure_ascii=False, separators=(",", ":")
        )

    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(manifest))
    next_process = process_sync.refresh_process_type_table(process_text, stats)
    summary_pattern = r"(4,972 条 new 候选组成 )[\d,]+( 个类型内身份组)"
    next_process, summary_count = re.subn(
        summary_pattern,
        rf"\g<1>{sync.fmt(totals['new_groups'])}\g<2>",
        next_process,
        count=1,
    )
    assert summary_count == 1, "could not refresh the S3 new-group summary"

    process_append = (
        f"\n\n<a id=\"{PROCESS_ANCHOR}\"></a>\n\n"
        f"### S3 archive：1948 年 Giuseppe Valeriani 著作跨章并组与脚注校正（{DATE}）\n\n"
        f"- {BODY_CANDIDATE} 原属 {SOURCE_GROUP}，{BIB_CANDIDATE} 原属 {TARGET_GROUP}；两者均保持 S3 new，"
        f"现统一进入 {TARGET_GROUP}，作为一个待 S4 登记的 archive 身份组。旧组号、原裁决理由及本次合组依据均保留在 alignment 注释。\n"
        "- 第20章 p.406 正文称一部1948年、资料详尽的 Giuseppe Valeriani 著作；紧随该句的注号7指向同页注释“Konopleva”。"
        "第21章 p.426 书目列 M. S. Konopleva、Teatralni Zhivopicets Giuseppe Valeriani、Leningrad 1948。"
        "注号与完整书目题名、年份及被研究人物相互吻合，支持正文候选与书目候选是同一出版物；未独立查阅该书。\n"
        f"- 顺带更正 {S2_STATEMENT_ID} 的 S2 claim：原称注7引用“后续论文”，但正文明确将注号7附于1948年著作，"
        "后续两篇论文标注注号8，注释列为“Ernst; Fomiciova”。现记录注7对应正文所述书籍；关系候选状态仍为 false，"
        "仅作为书目引用事实。作者全名未得，人物候选 cand-11203 保持 undecided；两篇后续论文候选 cand-11089 也保持 undecided。\n"
        "- 相关实体边界：人物 cand-9382 已映射 units/persons/giuseppe-valeriani；18世纪俄罗斯宫廷 cand-11087 与出版地 Leningrad cand-5796 "
        "保持各自 S3 new、待 S4，不并入文献卡；合并索引标题 cand-2679 仍 excluded。\n\n"
        f"S3 new 候选{sync.fmt(totals['new_candidates'])}，身份组{sync.fmt(totals['new_groups'])}；"
        f"S4 当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，"
        f"待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    if f'<a id="{PROCESS_ANCHOR}"></a>' not in next_process:
        next_process = next_process.rstrip() + process_append + "\n"

    result_append = (
        f"\n\n### S3 archive：1948 年 Giuseppe Valeriani 著作跨章并组（{DATE}）\n\n"
        f"{BODY_CANDIDATE}（第20章 p.406 正文描述）与 {BIB_CANDIDATE}（第20章注7及第21章 p.426 书目）"
        f"现同属 {TARGET_GROUP}：1948年出版年、Giuseppe Valeriani 主题与注号7所指的 M. S. Konopleva 书目记录相合。"
        "两候选均保持 S3 new，合并为一个待 S4 登记的 archive KU；书籍未独立查阅。已更正注7 statement 对应书目的 claim；"
        "作者个人身份与注号8的两篇后续论文仍待证。"
    )
    if "S3 archive：1948 年 Giuseppe Valeriani 著作跨章并组" not in next_result:
        next_result = next_result.rstrip() + result_append + "\n"

    stages_append = (
        f"\n\n### S2 p.406 注7与1948年书目引用校正（{DATE}）\n\n"
        f"- {S2_STATEMENT_ID} 原 claim 将注7说明为“俄国宫廷相关后续论文之一”；回读 p.406 L157–158 与注释 L262 后确认，"
        "正文的1948年著作带注号7，紧接的“两篇后续论文”带注号8，注8列 Ernst 与 Fomiciova。故注7实际对应正文所述的书籍。\n"
        "- 已将该 statement claim 改为注7识别前句所述 Giuseppe Valeriani 研究书；qualification 保留注释仅写 Konopleva、"
        "完整作者身份未明及书未独立查阅。predicate 和 relation_candidate=false 不变；S2 statement 数量及候选覆盖不变。"
        "正文原句、注7原文、书目行及候选映射未改。\n"
        f"- 修正后将 cand-11088 正文候选与 cand-11204 书目候选按同一出版物归入 {TARGET_GROUP}；"
        "旧组号和旧决定理由均保留在 S3 alignment 注释中。"
    )
    if "### S2 p.406 注7与1948年书目引用校正" not in stages_text:
        stages_text = stages_text.rstrip() + stages_append + "\n"

    if args.dry_run:
        print(
            f"dry-run passed: {BODY_CANDIDATE}+{BIB_CANDIDATE} -> {TARGET_GROUP}; "
            f"S2_correction={S2_STATEMENT_ID}; new_groups={totals['new_groups']}; "
            f"S4_pending={totals['pending_groups']}/{totals['pending_members']}; "
            f"statements={len(statement_lines)}; no files changed"
        )
        return 0

    sync.write_csv(TABLES / "alignment.csv", alignment_fields, planned_alignment)
    sync.write_csv(TABLES / "entity-candidates.csv", candidate_fields, planned_candidates)
    (TABLES / "book-statements.jsonl").write_text(
        "\n".join(planned_statements) + "\n",
        encoding="utf-8-sig",
        newline="\n",
    )
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    STAGES.write_text(stages_text, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(
        f"applied: {BODY_CANDIDATE}+{BIB_CANDIDATE} -> {TARGET_GROUP}; "
        f"S2 corrected={S2_STATEMENT_ID}; new_groups={totals['new_groups']}; "
        f"S4_pending={totals['pending_groups']}/{totals['pending_members']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
