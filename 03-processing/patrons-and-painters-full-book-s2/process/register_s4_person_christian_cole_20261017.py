from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

import register_s4_event_pantheon_st_joseph_exhibition_20261016 as sync

ROOT = Path(__file__).resolve().parents[3]
TASK = "patrons-and-painters-full-book-s2"
TABLES = ROOT / "04-knowledge" / "tables"
PROCESS = ROOT / "03-processing" / TASK / "process" / "knowledge.md"
RESULT = ROOT / "04-knowledge" / "results" / f"{TASK}.md"
ACCEPTED = ROOT / "04-knowledge" / "accepted.yml"
DATE = "2026-10-17"
GROUP = "new-person:christian-cole-b8a8cee01c"
MEMBERS = ("cand-0801",)
KU_ID = "units/persons/christian-cole"
CARD_REL = "04-knowledge/units/persons/christian-cole.md"
NAME_ZH = "克里斯蒂安·科尔"
NAME_EN = "Christian Cole"
BOOK_CITATION = "Francis Haskell, *Patrons and Painters*, revised and enlarged ed. (New Haven and London: Yale University Press, 1980; this printing 2006)"
INDEX_FILE = "02-sources/03-Index/03-2-Index-CSV/C.csv"
SOURCE_FILE = "02-sources/02-Markdown/10_CHP-10_intro.md"
RELATION_IDS = (
    "st-chp10-notes-p276n1-biographical-attribution",
    "st-chp10-p276-cole-carriera-pastel-portraits",
    "st-chp10-p276-cole-dartmouth-estimates",
    "st-chp10-p276-cole-recommended-pellegrini",
)
SOURCES = (
    {
        "file": INDEX_FILE,
        "location": "全书索引 C.csv#331；索引页码276",
        "span": "C.csv#331",
        "quote": "Cole, Christian",
        "summary": "索引以全名倒置形式“Cole, Christian”列出该人物，并指向印刷页276。",
    },
    {
        "file": SOURCE_FILE,
        "location": "第10章，印刷页276；L9–10；PDF物理页1",
        "span": "lines 9–10; print p. 276; PDF physical p. 1",
        "quote": "In 1703 the British Ambassador’s first secretary, Christian Cole, came across a Venetian girl, Rosalba Carriera, painting snuff-boxes and miniatures on ivory. He persuaded her to turn to pastel portraits",
        "summary": "Haskell以全名写作Christian Cole，并叙述其1703年在威尼斯遇见Rosalba Carriera及劝她转向粉彩肖像；此为书内叙述，未在本轮独立核验。",
    },
    {
        "file": SOURCE_FILE,
        "location": "第10章，印刷页276注1；L492；PDF物理页1",
        "span": "line 492; print p. 276, note 1; PDF physical p. 1",
        "quote": "Most early biographers report that a ‘certo signor Colle inglese’ was the first to advise Rosalba to turn to pastels",
        "summary": "Haskell转述早期传记作者将建议归于一位‘certo signor Colle inglese’；被引传记未独立查阅，故保留为归属转述，不提升为独立确认。",
    },
)


def group_of(note: str) -> str:
    match = re.search(r"(?:^|[;| ])group=([^;| ]+)", note or "")
    return match.group(1) if match else ""


def make_card() -> str:
    sources = []
    for item in SOURCES:
        sources.append({
            "citation": BOOK_CITATION,
            "location": item["location"],
            "sentence_summary": item["summary"],
            "original_quotes": [{"source_span": item["span"], "text": item["quote"]}],
            "evidence_ref": {
                "doc_id": "patrons-and-painters",
                "source_file": item["file"],
                "source_span": item["span"],
            },
        })
    frontmatter = {
        "title": f"{NAME_ZH}（{NAME_EN}）",
        "name_en": NAME_EN,
        "type": "person",
        "evidence_status": "source_backed",
        "sources": sources,
        "created": DATE,
        "updated": DATE,
        "process_ref": f"03-processing/{TASK}/process/knowledge.md#s3-s4-person-christian-cole-20261017",
    }
    fm = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False, width=1000)
    idx = "[全书索引 C.csv#331](../../../02-sources/03-Index/03-2-Index-CSV/C.csv)"
    ch10 = "[第10章 p.276](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L9–10）"
    note = "[第10章 p.276 注1](../../../02-sources/02-Markdown/10_CHP-10_intro.md)（L492）"
    relation_list = "\n".join(f"- `{relation_id}`" for relation_id in RELATION_IDS)
    return f"""---
{fm}---

## 内容

### 描述

**中文：** 本卡对应全书索引中的 Christian Cole。第10章以全名叙述其在1703年担任英国驻威尼斯大使第一秘书、遇见Rosalba Carriera并劝她转向粉彩肖像；注1另转述早期传记作者称一位“certo signor Colle inglese”首先提出该建议。注释所引传记未独立查阅，故该说法仍按Haskell的转述记录。{idx} {ch10} {note}

**English:** This unit corresponds to Christian Cole in the index. Chapter 10 names him as the British Ambassador’s first secretary in Venice in 1703 and says that he encountered Rosalba Carriera and persuaded her to turn to pastel portraits. Note 1 separately reports earlier biographers’ attribution of the advice to a “certo signor Colle inglese.” The cited biographies were not independently consulted, so that attribution remains Haskell’s report. {idx} {ch10} {note}

### 姓名与身份范围

- **索引形式：** `Cole, Christian`，索引指向第10章印刷页276。{idx}
- **书内全名：** 正文写作 `Christian Cole`；本卡依此建立书内人物身份。{ch10}
- **拼写边界：** 注1引用的早期传记用语为 `certo signor Colle inglese`；该转述与正文全名同处于Cole讨论语境，但不作为额外的外部身份核验或独立别名结论。{note}
- **中文显示名：** “克里斯蒂安·科尔”为项目工作音译。

## 关系与证据

当前没有正式关系记录。以下4条直接S2关系候选保留各自语气与来源层次，待S6裁决：

{relation_list}

其中早期传记归属仍是Haskell的转述；Manchester与Pellegrini的选择关系保留“almost certainly”；Lord Dartmouth候选`cand-0904`仍为S3 `undecided`，在其身份裁决前不强行补建端点。"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Christian Cole's S4 person identity group")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    _, candidates = sync.read_csv(TABLES / "entity-candidates.csv")
    align_fields, alignments = sync.read_csv(TABLES / "alignment.csv")
    manifest_fields, manifest = sync.read_csv(TABLES / "ku-manifest.csv")
    accepted = ACCEPTED.read_text(encoding="utf-8-sig")
    process_text = PROCESS.read_text(encoding="utf-8-sig")
    result_text = RESULT.read_text(encoding="utf-8-sig")
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    decisions = {
        row["candidate_id"]: row for row in alignments
        if row.get("candidate_id") and not row.get("external_source")
    }
    assert len(decisions) == len(candidate_by_id), "candidate/alignment decision coverage differs"
    assert all(cid in candidate_by_id for cid in MEMBERS)
    assert all(candidate_by_id[cid].get("suggested_type") == "person" for cid in MEMBERS)
    group_members = {
        cid for cid, row in decisions.items()
        if row.get("decision") == "new" and group_of(row.get("resolution_note", "")) == GROUP
    }
    assert group_members == set(MEMBERS), group_members
    card_path = ROOT / CARD_REL
    registered = [r for r in manifest if r.get("ku_id") == KU_ID and r.get("card_path") == CARD_REL]
    if registered and card_path.exists() and CARD_REL in accepted and all(decisions[cid].get("ku_id") == KU_ID for cid in MEMBERS):
        print(f"ALREADY REGISTERED: {GROUP} -> {KU_ID}; 4 relation candidates remain non-formal.")
        return 0
    for cid in MEMBERS:
        assert decisions[cid].get("decision") == "new" and not decisions[cid].get("ku_id")
    assert not card_path.exists() and CARD_REL not in accepted
    assert not any(row.get("ku_id") == KU_ID for row in manifest)
    assert not any(row.get("type") == "person" and row.get("name_en", "").casefold() == NAME_EN.casefold() for row in manifest)

    index_text = (ROOT / INDEX_FILE).read_text(encoding="utf-8-sig")
    source_text = (ROOT / SOURCE_FILE).read_text(encoding="utf-8-sig")
    for item in SOURCES:
        full_text = (ROOT / item["file"]).read_text(encoding="utf-8-sig")
        assert " ".join(item["quote"].split()) in " ".join(full_text.split()), item["quote"]
    assert "Cole, Christian" in index_text and "C.csv#331" in candidate_by_id[MEMBERS[0]].get("index_entry_id", "")
    assert "Christian Cole" in source_text and "Colle inglese" in source_text

    statements = [
        json.loads(line)
        for line in (TABLES / "book-statements.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    direct = [row for row in statements if row.get("subject_candidate_id") in MEMBERS or row.get("object_candidate_id") in MEMBERS]
    relations = [row for row in direct if row.get("qualifiers", {}).get("relation_candidate") is True]
    assert {row.get("statement_id") for row in relations} == set(RELATION_IDS)

    planned_alignment = [dict(row) for row in alignments]
    planned_by_id = {row["candidate_id"]: row for row in planned_alignment if row.get("candidate_id") and not row.get("external_source")}
    for cid in MEMBERS:
        planned_by_id[cid]["ku_id"] = KU_ID
        planned_by_id[cid]["resolution_note"] += f" S4 registration: mapped {GROUP} to {KU_ID}; source-local full-name match, no external identity claim."
    planned_manifest = list(manifest)
    planned_manifest.append({"ku_id": KU_ID, "type": "person", "canonical_name": NAME_ZH, "name_en": NAME_EN, "source_task": TASK, "card_path": CARD_REL})
    card = make_card()
    match = re.match(r"\A---\n(.*?)\n---\n", card, re.DOTALL)
    assert match and isinstance(yaml.safe_load(match.group(1)), dict), "generated person card frontmatter is invalid"
    stats = sync.summarize_by_type(candidates, planned_alignment)
    totals = {key: sum(row[key] for row in stats.values()) for key in next(iter(stats.values()))}
    next_result = sync.update_result(result_text, stats, totals, len(planned_manifest))
    anchor = "s3-s4-person-christian-cole-20261017"
    process_append = (
        f"\n\n<a id=\"{anchor}\"></a>\n\n### S4 person：Christian Cole关系端点登记（{DATE}）\n\n"
        f"- `{MEMBERS[0]}`（`{GROUP}`）映射到[{NAME_EN}人物卡](../../../{CARD_REL})。全书索引C.csv#331列`Cole, Christian`；第10章p.276正文给出全名`Christian Cole`，注1中的`certo signor Colle inglese`只作为Haskell转述的早期传记归属，不视为独立核验。\n"
        "- 直接S2关系候选4条，分别涉及Carriera、Lord Dartmouth及Pellegrini；Dartmouth端点`cand-0904`仍为S3 undecided。引述的早期传记未独立查阅，Manchester/Pellegrini关系保留原文“almost certainly”。本次只登记人物身份，不新增正式关系。\n\n"
        f"S4累计登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条候选映射；待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。"
    )
    next_process = process_text + process_append
    next_result += (
        f"\n\n### person：Christian Cole关系端点 S4 登记（{DATE}）\n\n"
        f"`{MEMBERS[0]}`登记至[人物卡](../units/persons/christian-cole.md)；全名由第10章正文与索引相合。4条关系候选待S6；Lord Dartmouth端点`cand-0904`仍为S3 undecided。\n\n"
        f"S4当前登记{sync.fmt(totals['registered_groups'])}组/{sync.fmt(totals['registered_members'])}条映射，待登记{sync.fmt(totals['pending_groups'])}组/{sync.fmt(totals['pending_members'])}条。\n"
    )

    if args.dry_run:
        print(f"dry-run passed: {GROUP} -> {KU_ID}; sources={len(SOURCES)}; relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(manifest)}->{len(planned_manifest)}")
        print("no files changed")
        return 0

    card_path.write_text(card, encoding="utf-8-sig", newline="\n")
    sync.write_csv(TABLES / "alignment.csv", align_fields, planned_alignment)
    sync.write_csv(TABLES / "ku-manifest.csv", manifest_fields, planned_manifest)
    accepted_lines = accepted.splitlines()
    insert_at = next(
        (i for i, line in enumerate(accepted_lines) if line.startswith("- 04-knowledge/units/") and line[2:] > CARD_REL),
        next((i for i, line in enumerate(accepted_lines) if line == "claims:"), len(accepted_lines)),
    )
    accepted_lines.insert(insert_at, f"- {CARD_REL}")
    ACCEPTED.write_text("\n".join(accepted_lines) + "\n", encoding="utf-8-sig", newline="\n")
    PROCESS.write_text(next_process, encoding="utf-8-sig", newline="\n")
    RESULT.write_text(next_result, encoding="utf-8-sig", newline="\n")
    print(f"applied: {GROUP} -> {KU_ID}; candidates={len(MEMBERS)}; relation_candidates_pending={len(relations)}; registered={totals['registered_groups']}/{totals['registered_members']}; pending={totals['pending_groups']}/{totals['pending_members']}; manifest={len(planned_manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
