from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TABLES = ROOT / "04-knowledge" / "tables"
MENTIONS_PATH = TABLES / "mentions.csv"
STATEMENTS_PATH = TABLES / "book-statements.jsonl"
ALIGNMENT_PATH = TABLES / "alignment.csv"
PROCESS_PATH = ROOT / "03-processing" / "patrons-and-painters-full-book-s2" / "process" / "knowledge.md"
RESULT_PATH = ROOT / "04-knowledge" / "results" / "patrons-and-painters-full-book-s2.md"
PERSON_CANDIDATE = "cand-0441"
WORK_CANDIDATE = "cand-4796"
GROUP = "new-person:bracciolini-francesco-bracciolini-francesc-7cfa25f9e6"
MENTION_IDS = {"m-chp2-seciv-l96-104-0015", "m-chp2-seciv-l96-104-0017"}
STATEMENT_ID = "st-chp2-seciv-l96-104-poem-publication-and-honours"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def replace_once(text, old, new, label):
    count = text.count(old)
    assert count == 1, f"{label}: expected one exact occurrence, found {count}"
    return text.replace(old, new, 1)


def plan_text_updates(process_text: str, result_text: str):
    process_note = """### 端点校正：Bracciolini 诗作子目与人物分流（2026-10-16）

复核第2章 p.52 后发现，索引 B.csv#288 的人物子目“L’elettione di Urbano VIII”及其正文提及“the poem”被映射到人物候选 `cand-0441`。第2章 p.57 将同名对象明确写作 Francesco Bracciolini 所作的颂诗；同一对象已有 archive 候选 `cand-4796`，其 S3 决定仍为 `undecided`（诗作／版本粒度未裁定）。因此将 `m-chp2-seciv-l96-104-0015`、`m-chp2-seciv-l96-104-0017` 与断言 `st-chp2-seciv-l96-104-poem-publication-and-honours` 的 object 端点改映至 `cand-4796`；`cand-0441` 继续作为索引中的人物子目候选，与 `cand-0440` 共组，不再把诗名当作人物身份锚点。诗作候选保持待证，相关关系留待 S6；人物组直接断言端点由16条/15条关系候选调整为15条/14条。原映射及改因保留在提及、对齐和本记录中。

"""
    process_text = replace_once(
        process_text,
        "## S4 KU 登记（2026-10-15）\n\n",
        process_note + "## S4 KU 登记（2026-10-15）\n\n",
        "process correction insertion",
    )
    result_note = """### S2 端点校正：Francesco Bracciolini 与《L’elettione di Urbano VIII》（2026-10-16）

第2章 p.52 的题名与“the poem”原映射至人物索引子目 `cand-0441`；p.57 明确说同名颂诗由 Francesco Bracciolini 创作。现将两条提及及出版断言的 object 改映至 archive 候选 `cand-4796`。该诗候选仍为 S3 `undecided`（版本／粒度待定），其关系不进入正式边；`cand-0441` 仍作为人物索引候选与 `cand-0440` 共组。此校正将人物组的直接 S2 端点数从16/15关系候选改为15/14；依据与保留的旧映射见[过程记录](../../03-processing/patrons-and-painters-full-book-s2/process/knowledge.md#端点校正bracciolini-诗作子目与人物分流-2026-10-16)及[校正脚本](../../03-processing/patrons-and-painters-full-book-s2/process/reconcile_s2_bracciolini_poem_endpoint_20261016.py)。

"""
    result_text = replace_once(
        result_text,
        "### 家族类型 S3 补裁决与 S4 登记（2026-10-16）\n\n",
        result_note + "### 家族类型 S3 补裁决与 S4 登记（2026-10-16）\n\n",
        "result correction insertion",
    )
    return process_text, result_text


def main():
    parser = argparse.ArgumentParser(description="Correct Bracciolini poem mentions and the statement endpoint")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    mention_fields, mentions = read_csv(MENTIONS_PATH)
    alignment_fields, alignments = read_csv(ALIGNMENT_PATH)
    mention_by_id = {row["mention_id"]: row for row in mentions}
    assert set(MENTION_IDS) <= set(mention_by_id)
    for mid in MENTION_IDS:
        assert mention_by_id[mid]["candidate_id"] == PERSON_CANDIDATE, mid
    assert mention_by_id["m-chp2-seciv-l96-104-0015"]["surface_form"] == "L’elettione di Urbano VIII"
    assert mention_by_id["m-chp2-seciv-l96-104-0017"]["surface_form"] == "the poem"

    person_candidate, work_candidate = {}, {}
    with (TABLES / "entity-candidates.csv").open(encoding="utf-8-sig", newline="") as stream:
        candidates = {row["candidate_id"]: row for row in csv.DictReader(stream)}
    person_candidate = candidates[PERSON_CANDIDATE]
    work_candidate = candidates[WORK_CANDIDATE]
    assert person_candidate["suggested_type"] == "person" and person_candidate["index_entry_id"] == "B.csv#288"
    assert work_candidate["suggested_type"] == "archive" and work_candidate["canonical_name"] == "L’elettione di Urbano VIII"

    statement_lines = STATEMENTS_PATH.read_text(encoding="utf-8-sig").splitlines()
    statement_matches = []
    for index, line in enumerate(statement_lines):
        row = json.loads(line)
        if row.get("statement_id") == STATEMENT_ID:
            statement_matches.append((index, line, row))
    assert len(statement_matches) == 1
    statement_index, statement_line, statement = statement_matches[0]
    assert statement["subject_candidate_id"] == "cand-0440" and statement["object_candidate_id"] == PERSON_CANDIDATE
    assert statement["qualifiers"]["print_page"] == 52 and statement["qualifiers"]["relation_candidate"] is True
    row_candidate = next(row for row in alignment_rows(alignments) if row.get("candidate_id") == PERSON_CANDIDATE)
    assert row_candidate["decision"] == "new" and not row_candidate.get("ku_id")
    assert f"group={GROUP}" in row_candidate["resolution_note"]
    work_alignment = next(row for row in alignments if row.get("candidate_id") == WORK_CANDIDATE and not row.get("external_source"))
    assert work_alignment["decision"] == "undecided" and not work_alignment.get("ku_id")
    assert "cand-4796" in statement["original_quote"] or "L’elettione di Urbano VIII" in statement["original_quote"]

    planned_mentions = [dict(row) for row in mentions]
    planned_mention_by_id = {row["mention_id"]: row for row in planned_mentions}
    planned_mention_by_id["m-chp2-seciv-l96-104-0015"]["candidate_id"] = WORK_CANDIDATE
    planned_mention_by_id["m-chp2-seciv-l96-104-0015"]["note"] = (
        "Corrected 2026-10-16: this title is the archive candidate cand-4796 (the poem), not the person index subentry cand-0441."
    )
    planned_mention_by_id["m-chp2-seciv-l96-104-0017"]["candidate_id"] = WORK_CANDIDATE
    planned_mention_by_id["m-chp2-seciv-l96-104-0017"]["note"] = (
        "Anaphoric reference to L’elettione di Urbano VIII; corrected 2026-10-16 to archive candidate cand-4796."
    )

    planned_alignment = [dict(row) for row in alignments]
    planned_alignment_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    old_anchor = (
        "s2_mentions=m-chp2-seciv-l96-104-0015@02-sources/02-Markdown/02_CHP-2_sec_iv.md#L96-104["
        "L’elettione di Urbano VIII;chars=500-526],m-chp2-seciv-l96-104-0017@02-sources/02-Markdown/02_CHP-2_sec_iv.md#L96-104["
        "the poem;chars=584-592]"
    )
    new_anchor = (
        "previous_s2_mentions=m-chp2-seciv-l96-104-0015[title] and m-chp2-seciv-l96-104-0017[anaphora]; "
        "corrected 2026-10-16 to archive candidate cand-4796, not person evidence"
    )
    note = planned_alignment_by_id[PERSON_CANDIDATE]["resolution_note"]
    assert note.count(old_anchor) == 1
    note = note.replace(old_anchor, new_anchor, 1)
    note += " S2 mapping correction: the B.csv#288 person index subentry remains grouped with cand-0440 by the shared person index name; the poem title and its anaphora are not person identity anchors."
    planned_alignment_by_id[PERSON_CANDIDATE]["resolution_note"] = note
    planned_alignment_by_id[WORK_CANDIDATE]["resolution_note"] += (
        " S2 mapping correction (2026-10-16): st-chp2-seciv-l96-104-poem-publication-and-honours also points to this archive candidate; exact edition/granularity remains undecided."
    )

    new_statement_line = statement_line.replace(
        '"object_candidate_id": "cand-0441"',
        '"object_candidate_id": "cand-4796"',
        1,
    )
    assert new_statement_line != statement_line
    new_statement = json.loads(new_statement_line)
    assert new_statement["object_candidate_id"] == WORK_CANDIDATE
    statement_lines[statement_index] = new_statement_line
    planned_statement_text = "\n".join(statement_lines) + "\n"

    person_endpoint_count = 0
    person_relation_count = 0
    with STATEMENTS_PATH.open(encoding="utf-8-sig") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("subject_candidate_id") in {"cand-0440", PERSON_CANDIDATE} or row.get("object_candidate_id") in {"cand-0440", PERSON_CANDIDATE}:
                if row.get("statement_id") == STATEMENT_ID:
                    continue
                person_endpoint_count += 1
                person_relation_count += int(row.get("qualifiers", {}).get("relation_candidate") is True)
    assert (person_endpoint_count, person_relation_count) == (16, 15)

    process_text, result_text = plan_text_updates(
        PROCESS_PATH.read_text(encoding="utf-8-sig"),
        RESULT_PATH.read_text(encoding="utf-8-sig"),
    )
    if args.dry_run:
        print(
            "dry-run passed: mentions=2 reassigned_to=cand-4796 statement_object=cand-4796 "
            "person_group_endpoints=16 relation_candidates=15 work_S3=undecided"
        )
        return 0

    write_csv(MENTIONS_PATH, mention_fields, planned_mentions)
    STATEMENTS_PATH.write_text(planned_statement_text, encoding="utf-8-sig", newline="\n")
    write_csv(ALIGNMENT_PATH, alignment_fields, planned_alignment)
    PROCESS_PATH.write_text(process_text, encoding="utf-8-sig", newline="")
    RESULT_PATH.write_text(result_text, encoding="utf-8-sig", newline="")
    print(
        "applied: mentions=2 reassigned_to=cand-4796 statement_object=cand-4796 "
        "person_group_endpoints=16 relation_candidates=15 work_S3=undecided"
    )
    return 0


def alignment_rows(rows):
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
